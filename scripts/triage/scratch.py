"""The application lock and the owned scratch root.

The default path through this program never writes repository source to disk at
all: blobs are read into bounded buffers, assessed, and dropped. This module
exists for the case where some dependency insists on a file, and for the
guarantee that whatever it leaves behind is bounded, identifiable, and removed.

What is actually promised, stated the way the README states it: no process can
run a `finally` block after SIGKILL or power loss. Normal operation — including
exceptions, timeouts and Ctrl-C — leaves zero per-assessment scratch. Abnormal
termination leaves marked directories under one owned root, and the next locked
startup removes them before doing anything else.
"""

from __future__ import annotations

import errno
import fcntl
import os
import secrets
import shutil
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from util import directory_bytes, iso, utc_now

MARKER = ".agent-memory-atlas-triage"
MARKER_BODY = "Owned by agent-memory-atlas triage. Safe to delete when no run is active.\n"


class LockBusy(RuntimeError):
    """Another triage process holds the lock."""


class CleanupFailed(RuntimeError):
    """A scratch directory could not be removed. Processing stops here."""


class UnsafeRoot(RuntimeError):
    """The configured scratch root is somewhere this program will not delete."""


@contextmanager
def application_lock(path: Path, *, wait: bool = False) -> Iterator[None]:
    """An OS-backed exclusive lock.

    `flock` rather than a PID file: the kernel releases it when the process dies,
    so a crashed run does not leave a lock that looks held forever and a stale
    PID does not have to be guessed about.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        flags = fcntl.LOCK_EX if wait else fcntl.LOCK_EX | fcntl.LOCK_NB
        try:
            fcntl.flock(handle, flags)
        except OSError as error:
            if error.errno in (errno.EAGAIN, errno.EACCES, errno.EWOULDBLOCK):
                raise LockBusy(
                    f"another triage process holds {path}. Wait for it, or use --wait."
                ) from None
            raise
        os.ftruncate(handle, 0)
        os.write(handle, f"{os.getpid()} {iso(utc_now())}\n".encode())
        yield
    finally:
        try:
            fcntl.flock(handle, fcntl.LOCK_UN)
        finally:
            os.close(handle)


def _refuse_dangerous(root: Path, state_dir: Path) -> None:
    resolved = root.resolve()
    forbidden = {
        Path("/"),
        Path.home().resolve(),
        state_dir.resolve(),
        Path("/tmp").resolve(),
        Path("/var").resolve(),
        Path("/var/tmp").resolve(),
        Path("/private/tmp").resolve(),
    }
    if resolved in forbidden or len(resolved.parts) <= 2:
        raise UnsafeRoot(f"refusing to manage {resolved} as a scratch root")


class Scratch:
    """Owns one directory. Creates children, removes them, and removes orphans."""

    def __init__(self, root: Path, state_dir: Path, *, max_bytes: int):
        self.root = root
        self.state_dir = state_dir
        self.max_bytes = max_bytes
        self.blocked: list[str] = []

    def ensure(self) -> None:
        _refuse_dangerous(self.root, self.state_dir)
        if self.root.is_symlink():
            raise UnsafeRoot(f"{self.root} is a symlink; refusing to use it as a scratch root")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        marker = self.root / MARKER
        if not marker.exists():
            marker.write_text(MARKER_BODY, encoding="utf-8")
        if not self._is_owned(self.root):
            raise UnsafeRoot(f"{self.root} is not marked as owned by this application")

    @staticmethod
    def _is_owned(path: Path) -> bool:
        marker = path / MARKER
        try:
            return marker.is_file() and not marker.is_symlink()
        except OSError:
            return False

    def reap(self) -> dict[str, object]:
        """Remove abandoned children. Call this after taking the lock, before work.

        With one active process by configuration, every marked child that exists
        at this point belongs to a run that is over. Unowned entries are reported
        and left alone rather than deleted, and symlinks are never followed.
        """
        self.ensure()
        removed, skipped, failed = [], [], []
        for entry in sorted(self.root.iterdir()):
            if entry.name == MARKER:
                continue
            try:
                info = entry.lstat()
            except OSError as error:
                failed.append((str(entry), str(error)))
                continue
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                skipped.append(str(entry))
                continue
            if not self._is_owned(entry):
                skipped.append(str(entry))
                continue
            try:
                shutil.rmtree(entry, ignore_errors=False)
                removed.append(entry.name)
            except OSError as error:
                failed.append((str(entry), str(error)))
        self.blocked = [f"{path}: {message}" for path, message in failed]
        return {
            "removed": removed,
            "skipped_unowned": skipped,
            "failed": failed,
            "bytes": directory_bytes(self.root),
        }

    @contextmanager
    def assessment_dir(self, *, prefix: str = "a") -> Iterator[Path]:
        """A per-assessment child, removed in `finally`.

        The name is `secrets.token_hex`, never anything derived from repository
        text: a path taken from a README is a path an attacker chooses.
        """
        self.ensure()
        if self.blocked:
            raise CleanupFailed(
                "scratch cleanup is outstanding; not starting new repository processing:\n  "
                + "\n  ".join(self.blocked)
            )
        used = self.usage()
        if used > self.max_bytes:
            raise CleanupFailed(
                f"{self.root} holds {used} bytes, over the {self.max_bytes} scratch ceiling; "
                f"run `triage cleanup` before processing more repositories"
            )
        child = self.root / f"{prefix}-{secrets.token_hex(8)}"
        child.mkdir(mode=0o700)
        (child / MARKER).write_text(MARKER_BODY, encoding="utf-8")
        try:
            yield child
        finally:
            try:
                shutil.rmtree(child, ignore_errors=False)
            except OSError as error:
                self.blocked.append(f"{child}: {error}")
                raise CleanupFailed(f"could not remove {child}: {error}") from error

    def usage(self) -> int:
        return directory_bytes(self.root)

"""Small shared helpers: time, hashing, atomic writes, bounded formatting.

Nothing here reaches the network or the database. Keeping it that way is what
lets the rest of the package be tested without either.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


# --- time ------------------------------------------------------------------
#
# Two clocks, deliberately separate. Every stored timestamp is UTC and carries
# its offset, so a machine that moves timezone cannot reinterpret history. The
# *day* a selection belongs to is a separate question answered in the configured
# civil timezone, because the twenty-a-day allowance is a human day.

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat(timespec="seconds")


def parse_iso(text: str) -> datetime:
    moment = datetime.fromisoformat(text)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment


def civil_day(moment: datetime, tz_name: str) -> str:
    """The YYYY-MM-DD the moment falls on in `tz_name`.

    DST is handled by zoneinfo rather than by arithmetic on hours: a day that is
    23 or 25 hours long is still one day's allowance.
    """
    return moment.astimezone(ZoneInfo(tz_name)).strftime("%Y-%m-%d")


def plus(moment: datetime, *, seconds: float = 0, days: float = 0) -> datetime:
    return moment + timedelta(seconds=seconds, days=days)


# --- hashing and json ------------------------------------------------------

def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def dumps(value: Any) -> str:
    """Stable JSON. Sorted keys so a content hash of a record is reproducible."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def loads(text: str | bytes) -> Any:
    return json.loads(text)


def truncate(text: str | None, limit: int) -> str | None:
    """Cap a string for durable storage, marking the cut so nobody reads the
    remainder as the whole. Evidence excerpts and quarantined lines go through
    here; the cap is the reason this database cannot grow with the feed."""
    if text is None:
        return None
    if len(text) <= limit:
        return text
    return text[:limit] + f"…[cut at {limit} chars]"


# --- files -----------------------------------------------------------------

def atomic_write(path: Path, payload: str | bytes, *, mode: int = 0o600) -> None:
    """Write through a temporary file in the same directory plus rename.

    A crash leaves either the previous file or the new one, never a half-written
    shortlist. The temporary lives beside the target so the rename stays on one
    filesystem.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    data = payload.encode("utf-8") if isinstance(payload, str) else payload
    handle, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def directory_bytes(path: Path) -> int:
    """Bytes under a directory, symlinks counted as links and never followed."""
    total = 0
    if not path.exists():
        return 0
    for root, dirs, files in os.walk(path, followlinks=False):
        for name in files:
            entry = Path(root) / name
            try:
                total += entry.lstat().st_size
            except OSError:
                continue
    return total


def human_bytes(count: int | None) -> str:
    if count is None:
        return "unknown"
    size = float(count)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if size < 1024 or unit == "GiB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} GiB"


# --- redaction -------------------------------------------------------------

_SECRET = re.compile(
    r"(gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{16,})"
)


def redact(text: str) -> str:
    """Strip anything shaped like a credential before it reaches a log or an
    export. The rule upstream is that tokens never enter these strings at all;
    this is the second line, for the message we did not write ourselves."""
    return _SECRET.sub("[redacted]", text)

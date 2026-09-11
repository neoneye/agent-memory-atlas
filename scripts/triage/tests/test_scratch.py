"""Section 11: what is left on disk after every way a run can end."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

import scratch as scratch_module
from scratch import CleanupFailed, LockBusy, MARKER, Scratch, UnsafeRoot, application_lock

PACKAGE = str(Path(__file__).resolve().parents[1])


class ScratchTests(unittest.TestCase):
    def setUp(self):
        self.state = Path(tempfile.mkdtemp(prefix="triage-scratch-"))
        self.addCleanup(lambda: _rmtree(self.state))
        self.scratch = Scratch(self.state / "scratch", self.state, max_bytes=1 << 20)
        self.scratch.ensure()

    def children(self) -> list[str]:
        return sorted(p.name for p in self.scratch.root.iterdir() if p.name != MARKER)

    def test_normal_completion_leaves_nothing(self):
        with self.scratch.assessment_dir() as directory:
            (directory / "buffer.bin").write_bytes(b"x" * 4096)
        self.assertEqual(self.children(), [])

    def test_an_exception_leaves_nothing(self):
        with self.assertRaises(ValueError):
            with self.scratch.assessment_dir() as directory:
                (directory / "buffer.bin").write_bytes(b"x")
                raise ValueError("boom")
        self.assertEqual(self.children(), [])

    def test_an_interrupt_leaves_nothing(self):
        with self.assertRaises(KeyboardInterrupt):
            with self.scratch.assessment_dir():
                raise KeyboardInterrupt
        self.assertEqual(self.children(), [])

    def test_a_timeout_leaves_nothing(self):
        with self.assertRaises(TimeoutError):
            with self.scratch.assessment_dir():
                raise TimeoutError
        self.assertEqual(self.children(), [])

    def test_names_never_come_from_repository_text(self):
        with self.scratch.assessment_dir() as directory:
            self.assertRegex(directory.name, r"^a-[0-9a-f]{16}$")

    def test_an_abandoned_child_is_removed_on_the_next_locked_start(self):
        orphan = self.scratch.root / "a-0123456789abcdef"
        orphan.mkdir()
        (orphan / MARKER).write_text("x")
        (orphan / "leftover").write_bytes(b"y" * 1000)
        reaped = self.scratch.reap()
        self.assertIn("a-0123456789abcdef", reaped["removed"])
        self.assertEqual(self.children(), [])

    def test_unowned_neighbours_are_reported_and_never_deleted(self):
        neighbour = self.scratch.root / "not-ours"
        neighbour.mkdir()
        (neighbour / "important").write_text("keep me")
        reaped = self.scratch.reap()
        self.assertEqual(reaped["removed"], [])
        self.assertTrue(neighbour.exists())
        self.assertTrue(any("not-ours" in path for path in reaped["skipped_unowned"]))

    def test_symlinks_are_never_followed_or_deleted(self):
        outside = self.state / "precious"
        outside.mkdir()
        (outside / "file").write_text("keep")
        link = self.scratch.root / "a-link"
        link.symlink_to(outside)
        reaped = self.scratch.reap()
        self.assertEqual(reaped["removed"], [])
        self.assertTrue((outside / "file").exists())
        self.assertTrue(link.is_symlink())

    def test_dangerous_roots_are_refused(self):
        for bad in (Path("/"), Path.home(), self.state, Path("/tmp")):
            with self.assertRaises(UnsafeRoot):
                Scratch(bad, self.state, max_bytes=1).ensure()

    def test_a_cleanup_failure_stops_new_repository_processing(self):
        self.scratch.blocked.append("/somewhere: Permission denied")
        with self.assertRaises(CleanupFailed) as caught:
            with self.scratch.assessment_dir():
                pass
        self.assertIn("/somewhere", str(caught.exception))

    def test_a_killed_process_leaves_bounded_scratch_that_the_next_start_removes(self):
        """SIGKILL runs no `finally`. The promise is bounded and identifiable."""
        script = (
            "import sys, time\n"
            f"sys.path.insert(0, {PACKAGE!r})\n"
            "from pathlib import Path\n"
            "from scratch import Scratch\n"
            f"s = Scratch(Path({str(self.scratch.root)!r}), Path({str(self.state)!r}), max_bytes=1<<20)\n"
            "with s.assessment_dir() as d:\n"
            "    (d / 'partial.bin').write_bytes(b'z' * 2048)\n"
            "    print('ready', flush=True)\n"
            "    time.sleep(30)\n"
        )
        process = subprocess.Popen([sys.executable, "-c", script], stdout=subprocess.PIPE)
        try:
            self.assertEqual(process.stdout.readline().strip(), b"ready")
            os.kill(process.pid, signal.SIGKILL)
            process.wait(timeout=10)
        finally:
            if process.poll() is None:
                process.kill()
        leftovers = self.children()
        self.assertEqual(len(leftovers), 1)
        self.assertLess(self.scratch.usage(), 1 << 20)
        self.assertIn(leftovers[0], self.scratch.reap()["removed"])
        self.assertEqual(self.children(), [])


class LockTests(unittest.TestCase):
    def setUp(self):
        self.state = Path(tempfile.mkdtemp(prefix="triage-lock-"))
        self.addCleanup(lambda: _rmtree(self.state))

    def test_a_second_process_cannot_take_the_lock(self):
        script = (
            "import sys, time\n"
            f"sys.path.insert(0, {PACKAGE!r})\n"
            "from pathlib import Path\n"
            "from scratch import application_lock\n"
            f"with application_lock(Path({str(self.state / 'l.lock')!r})):\n"
            "    print('held', flush=True)\n"
            "    time.sleep(30)\n"
        )
        process = subprocess.Popen([sys.executable, "-c", script], stdout=subprocess.PIPE)
        try:
            self.assertEqual(process.stdout.readline().strip(), b"held")
            with self.assertRaises(LockBusy):
                with application_lock(self.state / "l.lock"):
                    pass
        finally:
            process.kill()
            process.wait(timeout=10)

    def test_a_crashed_holder_releases_the_lock(self):
        script = (
            "import sys, time\n"
            f"sys.path.insert(0, {PACKAGE!r})\n"
            "from pathlib import Path\n"
            "from scratch import application_lock\n"
            f"with application_lock(Path({str(self.state / 'l.lock')!r})):\n"
            "    print('held', flush=True)\n"
            "    time.sleep(30)\n"
        )
        process = subprocess.Popen([sys.executable, "-c", script], stdout=subprocess.PIPE)
        self.assertEqual(process.stdout.readline().strip(), b"held")
        os.kill(process.pid, signal.SIGKILL)
        process.wait(timeout=10)
        # The kernel dropped it; no PID file has to be interpreted.
        with application_lock(self.state / "l.lock"):
            pass


def _rmtree(path: Path) -> None:
    import shutil
    shutil.rmtree(path, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

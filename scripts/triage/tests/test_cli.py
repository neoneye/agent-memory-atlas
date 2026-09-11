"""Section 11: state is never created by accident, and a backup restores a ledger."""

from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import __main__ as entry  # the package's own __main__, imported by `triage selftest`
from tests.support import Harness


def run_cli(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = entry.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class CliTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="triage-cli-"))
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
        self.helper = Harness()
        self.addCleanup(self.helper.close)
        self.atlas = self.helper.atlas_repo
        self.state = self.root / "state"
        self.out = self.root / "out"
        self.feed = self.root / "candidates.jsonl"
        self.feed.write_text(
            json.dumps({"kind": "repo", "repo": "example/memory-project", "status": "filed"}) + "\n",
            encoding="utf-8",
        )

    def base(self) -> list[str]:
        return ["--state-dir", str(self.state), "--atlas-repo", str(self.atlas),
                "--output-dir", str(self.out), "--source-file", str(self.feed), "--json"]

    def test_commands_refuse_to_create_state_implicitly(self):
        for command in ("status", "ingest", "select", "export"):
            code, _, err = run_cli(*self.base(), command)
            self.assertEqual(code, 2, command)
            self.assertIn("no triage state", err)
        self.assertFalse((self.state / "triage.sqlite3").exists())

    def test_init_then_ingest_then_status(self):
        self.assertEqual(run_cli(*self.base(), "init")[0], 0)
        code, out, _ = run_cli(*self.base(), "ingest")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["newly_imported"], 1)
        code, out, _ = run_cli(*self.base(), "status")
        payload = json.loads(out)
        self.assertEqual(payload["candidates_total"], 1)
        self.assertEqual(payload["capacity"]["slots_available"], 20)
        self.assertIn("not configured", payload["classifier"])

    def test_init_refuses_to_clobber_existing_state(self):
        run_cli(*self.base(), "init")
        code, _, err = run_cli(*self.base(), "init")
        self.assertEqual(code, 2)
        self.assertIn("already exists", err)

    def test_corrupt_state_is_reported_not_replaced(self):
        corrupt = self.root / "corrupt"
        corrupt.mkdir()
        (corrupt / "triage.sqlite3").write_bytes(b"this is not a database" * 100)
        code, _, err = run_cli("--state-dir", str(corrupt), "--atlas-repo", str(self.atlas),
                               "--json", "status")
        self.assertEqual(code, 2)
        self.assertIn("not a readable triage database", err)
        # And it is still there, unmodified, rather than replaced with a fresh one.
        self.assertTrue((corrupt / "triage.sqlite3").read_bytes().startswith(b"this is not"))

    def test_export_and_restore_preserve_decisions(self):
        run_cli(*self.base(), "init")
        run_cli(*self.base(), "ingest")
        run_cli(*self.base(), "assess", "--metadata-limit", "0", "--limit", "0")
        backup = self.root / "backup.jsonl"
        code, out, _ = run_cli(*self.base(), "export", "--output", str(backup))
        self.assertEqual(code, 0)
        self.assertGreater(json.loads(out)["rows"], 0)

        # A restore replaces a ledger; it never merges into one silently.
        code, _, err = run_cli(*self.base(), "restore", "--input", str(backup))
        self.assertEqual(code, 2)
        self.assertIn("does not merge", err)

        fresh = self.root / "fresh"
        argv = ["--state-dir", str(fresh), "--atlas-repo", str(self.atlas),
                "--output-dir", str(self.out), "--source-file", str(self.feed), "--json"]
        code, out, _ = run_cli(*argv, "restore", "--input", str(backup))
        self.assertEqual(code, 0)
        code, out, _ = run_cli(*argv, "status")
        self.assertEqual(json.loads(out)["candidates_total"], 1)

    def test_a_restore_refuses_a_file_without_a_header(self):
        bogus = self.root / "bogus.jsonl"
        bogus.write_text(json.dumps({"kind": "row", "table": "candidate", "row": {}}) + "\n")
        code, _, err = run_cli("--state-dir", str(self.root / "r2"), "--atlas-repo", str(self.atlas),
                               "--json", "restore", "--input", str(bogus))
        self.assertEqual(code, 2)
        self.assertIn("no header record", err)

    def test_explain_reports_the_next_action(self):
        run_cli(*self.base(), "init")
        run_cli(*self.base(), "ingest")
        code, out, _ = run_cli(*self.base(), "explain", "example/memory-project")
        payload = json.loads(out)
        self.assertEqual(payload["repo"], "example/memory-project")
        self.assertIn("awaiting evidence", payload["next_action"])

    def test_explain_on_an_unknown_repository_says_so(self):
        run_cli(*self.base(), "init")
        code, _, err = run_cli(*self.base(), "explain", "nobody/nothing")
        self.assertEqual(code, 2)
        self.assertIn("not in triage state", err)

    def test_run_writes_the_days_files_and_cleanup_is_idempotent(self):
        run_cli(*self.base(), "init")
        code, out, err = run_cli(*self.base(), "run", "--metadata-limit", "0", "--limit", "0")
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        files = payload["files"]
        self.assertIsNotNone(files)
        day_file = Path(files["json"])
        self.assertTrue(day_file.exists())
        self.assertTrue(day_file.name.endswith(".json"))
        report = json.loads(day_file.read_text(encoding="utf-8"))
        self.assertEqual(report["import"]["imported_new"], 1)
        self.assertEqual(report["selected"], 0)
        self.assertEqual(report["shortlist"], [])

        # A rerun regenerates the identical committed list without admitting more.
        run_cli(*self.base(), "select")
        after = json.loads(day_file.read_text(encoding="utf-8"))
        self.assertEqual(after["capacity"]["admitted_today"], 0)
        self.assertEqual(after["day"], report["day"])

        code, out, _ = run_cli(*self.base(), "cleanup")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["scratch"]["removed"], [])

    def test_a_dry_run_writes_no_files_and_admits_nothing(self):
        run_cli(*self.base(), "init")
        run_cli(*self.base(), "ingest")
        code, out, _ = run_cli(*self.base(), "select", "--dry-run")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertIsNone(payload["files"])
        self.assertEqual(payload["capacity"]["admitted_today"], 0)
        self.assertFalse(self.out.exists() and any(self.out.iterdir()))

    def test_a_source_failure_stops_run_without_touching_state(self):
        run_cli(*self.base(), "init")
        run_cli(*self.base(), "ingest")
        self.feed.unlink()
        code, _, err = run_cli(*self.base(), "run")
        self.assertEqual(code, 2)
        self.assertIn("source fetch failed", err)
        code, out, _ = run_cli(*self.base(), "status")
        self.assertEqual(json.loads(out)["candidates_total"], 1)


if __name__ == "__main__":
    unittest.main()


class InventoryTests(unittest.TestCase):
    """A missing atlas inventory stops selection, and nothing else."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="triage-inv-"))
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
        self.helper = Harness()
        self.addCleanup(self.helper.close)
        self.empty_atlas = self.root / "not-an-atlas"
        self.empty_atlas.mkdir()
        self.feed = self.root / "candidates.jsonl"
        self.feed.write_text(
            json.dumps({"kind": "repo", "repo": "example/memory-project"}) + "\n", encoding="utf-8")

    def test_ingest_proceeds_and_selection_does_not(self):
        base = ["--state-dir", str(self.root / "state"), "--output-dir", str(self.root / "out"),
                "--source-file", str(self.feed), "--json"]
        good = base + ["--atlas-repo", str(self.helper.atlas_repo)]
        self.assertEqual(run_cli(*good, "init")[0], 0)

        bad = base + ["--atlas-repo", str(self.empty_atlas)]
        code, out, err = run_cli(*bad, "run")
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        self.assertIsNotNone(payload["atlas_inventory_error"])
        self.assertIsNone(payload["files"])
        self.assertEqual(payload["import"]["imported_new"], 1)

        code, out, _ = run_cli(*bad, "status")
        self.assertEqual(json.loads(out)["candidates_total"], 1)

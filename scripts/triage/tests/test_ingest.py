"""Section 11: the source is read, never written, and never believed blindly."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import ingest as ingest_module
from identity import bind_repo_id, find
from tests.support import Harness

MINIMAL = {"kind": "repo", "repo": "example/memory-project", "status": "filed", "issue_number": 123}


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)

    def ingest(self):
        return ingest_module.run(self.h.config, self.h.connection, None)

    def test_minimal_filed_record_is_processed(self):
        self.h.feed([MINIMAL])
        result = self.ingest()
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.imported_new, 1)
        row = find(self.h.connection, name="example/memory-project")
        self.assertIsNotNone(row)
        # `filed` means Scout filed an issue, not that the atlas assessed it.
        self.assertEqual(row["triage_status"], "unassessed")

    def test_reordering_and_repetition_do_not_duplicate(self):
        records = [MINIMAL, {"kind": "repo", "repo": "other/thing"},
                   {"kind": "repo", "repo": "third/one"}]
        self.h.feed(records)
        self.ingest()
        self.h.feed(list(reversed(records)))
        second = self.ingest()
        self.assertEqual(second.imported_new, 0)
        self.assertEqual(second.duplicates, 3)
        self.assertEqual(self._count(), 3)

    def test_case_variation_is_one_candidate(self):
        self.h.feed([MINIMAL, {"kind": "repo", "repo": "Example/Memory-Project"}])
        self.ingest()
        self.assertEqual(self._count(), 1)

    def test_non_repository_records_are_ignored(self):
        self.h.feed([
            MINIMAL,
            {"kind": "post", "id": "t3_abc", "author": "a-reddit-user"},
            {"kind": "meta", "run": "2026-09-11"},
        ])
        result = self.ingest()
        self.assertEqual(result.repo_records, 1)
        self.assertEqual(result.other_records, 2)
        # The Reddit author is not a repository owner and never becomes one.
        self.assertIsNone(find(self.h.connection, name="a-reddit-user/anything")
                          if "/" in "a-reddit-user/anything" else None)

    def test_missing_entries_do_not_delete_decisions(self):
        self.h.feed([MINIMAL, {"kind": "repo", "repo": "other/thing"}])
        self.ingest()
        self.h.connection.execute(
            "UPDATE candidate SET triage_status = 'rejected', triage_reason = 'no tests' "
            "WHERE canonical_name = 'other/thing'"
        )
        self.h.feed([MINIMAL])
        self.ingest()
        row = find(self.h.connection, name="other/thing")
        self.assertEqual(row["triage_status"], "rejected")
        self.assertEqual(row["triage_reason"], "no tests")

    def test_malformed_lines_are_counted_and_quarantined(self):
        path = self.h.config.source_file
        path.write_text(json.dumps(MINIMAL) + "\n{not json\n[]\n", encoding="utf-8")
        result = self.ingest()
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.malformed, 2)
        self.assertTrue(result.quarantine)

    def test_a_feed_with_no_valid_repository_stops(self):
        self.h.config.source_file.write_text("{bad\n{worse\n", encoding="utf-8")
        result = self.ingest()
        self.assertEqual(result.status, "failed")
        self.assertIn("Stopping for inspection", result.failure)

    def test_a_vanished_source_cannot_erase_state(self):
        self.h.feed([MINIMAL])
        self.ingest()
        self.h.config.source_file.unlink()
        result = self.ingest()
        self.assertEqual(result.status, "failed")
        self.assertEqual(self._count(), 1)
        rows = self.h.connection.execute(
            "SELECT status FROM ingestion ORDER BY id").fetchall()
        self.assertEqual([row["status"] for row in rows], ["complete", "failed"])

    def test_an_oversized_feed_is_refused_whole(self):
        self.h.config.limits.feed_bytes = 64
        self.h.feed([MINIMAL, {"kind": "repo", "repo": "other/thing"}])
        result = self.ingest()
        self.assertEqual(result.status, "failed")
        self.assertEqual(self._count(), 0)

    def test_the_source_file_is_never_modified(self):
        self.h.feed([MINIMAL])
        before = self.h.config.source_file.read_bytes()
        self.ingest()
        self.h.connection.execute("UPDATE candidate SET triage_status = 'rejected'")
        self.ingest()
        self.assertEqual(self.h.config.source_file.read_bytes(), before)

    def test_invalid_names_never_become_candidates(self):
        self.h.feed([
            MINIMAL,
            {"kind": "repo", "repo": "../../etc/passwd"},
            {"kind": "repo", "repo": "https://evil.example.com/a/b"},
            {"kind": "repo", "repo": "one/two/three"},
        ])
        result = self.ingest()
        self.assertEqual(result.repo_records, 1)
        self.assertEqual(result.invalid_names, 3)

    def test_feed_hints_are_stored_as_hints(self):
        self.h.feed([{**MINIMAL, "description": "claims a lot", "latest": {"stars": 9999}}])
        self.ingest()
        row = find(self.h.connection, name="example/memory-project")
        provenance = json.loads(row["provenance"])["observations"][0]
        self.assertEqual(provenance["hint_stars"], 9999)
        self.assertEqual(provenance["status"], "filed")

    def _count(self) -> int:
        return int(self.h.connection.execute(
            "SELECT COUNT(*) AS n FROM candidate").fetchone()["n"])


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        self.h.feed([MINIMAL])
        ingest_module.run(self.h.config, self.h.connection, None)

    def test_a_rename_keeps_the_decision(self):
        row = find(self.h.connection, name="example/memory-project")
        self.h.connection.execute(
            "UPDATE candidate SET triage_status = 'rejected', triage_reason = 'no tests' WHERE id = ?",
            (row["id"],))
        outcome = bind_repo_id(self.h.connection, int(row["id"]), 555, "example/renamed")
        self.assertEqual(outcome, "renamed")
        moved = find(self.h.connection, name="example/renamed")
        self.assertEqual(moved["triage_status"], "rejected")
        # And the old name still finds it.
        self.assertEqual(find(self.h.connection, name="example/memory-project")["id"], row["id"])

    def test_a_reused_name_is_a_different_project(self):
        first = find(self.h.connection, name="example/memory-project")
        bind_repo_id(self.h.connection, int(first["id"]), 555, "example/memory-project")
        self.h.connection.execute(
            "UPDATE candidate SET triage_status = 'rejected' WHERE id = ?", (first["id"],))
        self.h.connection.execute(
            "INSERT INTO candidate(canonical_name, display_name, first_seen_at, last_seen_at) "
            "VALUES ('example/newcomer', 'example/newcomer', '2026-09-11', '2026-09-11')")
        second = find(self.h.connection, name="example/newcomer")
        outcome = bind_repo_id(self.h.connection, int(second["id"]), 555, "example/memory-project")
        self.assertEqual(outcome, "reused")
        self.assertEqual(find(self.h.connection, repo_id=555)["id"], first["id"])
        self.assertEqual(
            self.h.connection.execute(
                "SELECT triage_status FROM candidate WHERE id = ?", (second["id"],)
            ).fetchone()["triage_status"],
            "unassessed",
        )


if __name__ == "__main__":
    unittest.main()

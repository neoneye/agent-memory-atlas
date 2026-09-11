"""The day's JSONL and digest: shape, honesty, and regeneration."""

from __future__ import annotations

import json
import unittest
import uuid
from pathlib import Path

import atlas
import reports
import selection as selection_module
from db import transaction
from tests.support import Harness
from util import dumps, iso, utc_now


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        atlas.sync(self.h.connection, self.h.atlas_repo,
                   Path(self.h.config.policy_file).parent / "exclusions.txt")
        now = iso(utc_now())
        facts = {
            "head_commit": "e" * 40, "stars": 41, "forks": 6,
            "contributors_apparently_non_bot": 2, "contributors_bot": 1,
            "merged_external_pulls": None, "pushed_at": "2026-09-01T00:00:00Z",
            "open_issues_excluding_prs": 3, "open_pull_requests": 1,
            "created_at": "2024-02-02T00:00:00Z", "license": "MIT",
            "is_fork": False, "archived": False,
            "test_evidence": {
                "level": "memory_specific", "reason": "two files assert on recall",
                "ci_configured": True, "ci_workflow": ".github/workflows/ci.yml",
                "ci_run_observed": False,
                "files": [{"path": "tests/test_recall.py", "assertions": True,
                           "memory_related": True, "content_sha256": "abc123def456"}],
            },
            "inspection": {"commit": "e" * 40, "tree_paths": 120, "tree_truncated": False,
                           "blobs_read": 6, "notes": []},
            "awards": [{"component": "test_evidence", "points": 24, "anchor": "level_memory_specific",
                        "because": "tests assert on recall"}],
            "cautions": [], "limitations": ["scope judged by structural rules"],
        }
        with transaction(self.h.connection):
            cursor = self.h.connection.execute(
                "INSERT INTO candidate(canonical_name, display_name, first_seen_at, last_seen_at, "
                "triage_status) VALUES ('good/mem', 'good/mem', ?, ?, 'eligible')", (now, now))
            candidate_id = int(cursor.lastrowid)
            assessment = self.h.connection.execute(
                "INSERT INTO assessment(uuid, candidate_id, assessed_commit, assessed_at, "
                "policy_version, outcome, score, components, gates, facts, coverage, reasons) "
                "VALUES (?, ?, ?, ?, '2026-09-11.1', 'eligible', 74, ?, '{}', ?, ?, ?)",
                (str(uuid.uuid4()), candidate_id, "e" * 40, now,
                 dumps({"test_evidence": 30, "implementation_substance": 20,
                        "contribution_maintenance": 9, "atlas_value": 9, "adoption": 6}),
                 dumps(facts), dumps({"tree": "complete", "contributors": "sampled"}),
                 dumps(["passed all four gates and scored 74/60 minimum"])))
            self.h.connection.execute(
                "UPDATE candidate SET latest_assessment = ? WHERE id = ?",
                (int(assessment.lastrowid), candidate_id))
        self.shortlist = selection_module.finalize(self.h.connection, self.h.config)

    def records(self):
        return reports.build(self.h.connection and self.h.config, self.h.connection,
                             self.shortlist, {"policy_version": "2026-09-11.1"},
                             {"status": "complete", "identity": "github:Daily-Nerd/scout@main",
                              "content_hash": "f" * 64, "bytes": 211000, "transport": "contents-api"})

    def test_the_first_line_is_a_meta_record(self):
        records = self.records()
        self.assertEqual(records[0]["kind"], "meta")
        self.assertEqual(records[0]["selected"], 1)
        self.assertIn("capacity", records[0])
        self.assertIn("disk", records[0])
        self.assertEqual(records[0]["source"]["content_hash"], "f" * 64)

    def test_each_selection_carries_its_evidence(self):
        entry = self.records()[1]
        self.assertEqual(entry["kind"], "selection")
        self.assertEqual(entry["repo"], "good/mem")
        self.assertEqual(entry["url"], "https://github.com/good/mem")
        self.assertEqual(entry["pinned_commit"], "e" * 40)
        self.assertEqual(entry["score"], 74)
        self.assertEqual(sum(entry["score_components"].values()), 74)
        self.assertTrue(entry["selection_id"])
        self.assertEqual(entry["test_evidence"]["files"][0]["path"], "tests/test_recall.py")

    def test_an_unknown_metric_is_null_not_zero(self):
        entry = self.records()[1]
        self.assertIsNone(entry["metrics"]["merged_external_pulls"])
        self.assertEqual(entry["metrics"]["stars"], 41)

    def test_ci_configuration_is_never_reported_as_a_run(self):
        entry = self.records()[1]
        self.assertTrue(entry["test_evidence"]["ci_configured"])
        self.assertFalse(entry["test_evidence"]["ci_run_observed"])
        digest = reports.digest(self.records())
        self.assertIn("configures a test runner", digest)

    def test_writing_is_atomic_and_regenerating_is_byte_identical(self):
        records = self.records()
        jsonl, digest_path = reports.write(self.h.config, records, self.shortlist.day)
        first = jsonl.read_bytes()
        self.assertTrue(digest_path.exists())
        leftovers = [p.name for p in jsonl.parent.iterdir() if p.name.startswith(".")]
        self.assertEqual(leftovers, [])
        again = list(records)
        again[0] = dict(again[0], generated_at=records[0]["generated_at"])
        reports.write(self.h.config, again, self.shortlist.day)
        self.assertEqual(jsonl.read_bytes(), first)

    def test_the_digest_names_the_day_and_the_uncertainty(self):
        digest = reports.digest(self.records())
        self.assertIn(f"# Candidate shortlist — {self.shortlist.day}", digest)
        self.assertIn("not a claim to have assessed every repository", digest)
        self.assertIn("structural rules", digest)

    def test_an_empty_day_distinguishes_its_reasons(self):
        self.shortlist.entries = []
        records = reports.build(self.h.config, self.h.connection, self.shortlist,
                                {"assessment": {"budget_stopped": "daily inspection budget of 100"}},
                                {"status": "complete"})
        digest = reports.digest(records)
        self.assertIn("exhausted budget, not a judgement", digest)

        records = reports.build(self.h.config, self.h.connection, self.shortlist, {},
                                {"status": "failed", "failure": "connection reset"})
        digest = reports.digest(records)
        self.assertIn("source failure, not a judgement", digest)

    def test_writing_refuses_over_the_state_ceiling(self):
        self.h.config.limits.state_bytes = 1
        with self.assertRaises(RuntimeError) as caught:
            reports.write(self.h.config, self.records(), self.shortlist.day)
        self.assertIn("never deleted to make room", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

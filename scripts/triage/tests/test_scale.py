"""The 1,400-candidate fixture run: bounded, resumable, and leaving no scratch.

Every response here is simulated. Nothing in this file fetches 1,400 real
repositories, and the point of the fixture is the bookkeeping, not the network:
that a feed of that size imports once, that the budgets stop the run where they
say they will, that a second run continues instead of restarting, and that the
scratch root is empty afterwards.

1,400 is the capacity scenario from the specification, not a measured arrival
rate. An accumulated index holding that many repositories says nothing about how
many arrive in a day, and the report separates newly imported from backlog for
exactly that reason.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import assess as assess_module
import atlas
import ingest as ingest_module
import reports
import selection as selection_module
from policy import Policy
from scratch import Scratch
from tests.support import FakeClient, Harness, repo_routes
from tests.test_evidence import IMPLEMENTATION, REAL_TEST
from util import civil_day, directory_bytes, utc_now

TOTAL = 1400
COMMIT = "9" * 40
FILES = {
    "README.md": "# mem\n\nAgent memory with tests.\n",
    "tests/test_recall.py": REAL_TEST,
    "mem/store.py": IMPLEMENTATION,
}


class ScaleTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness(metadata_budget=40, inspection_budget=10)
        self.addCleanup(self.h.close)
        self.policy = Policy.load(self.h.config.policy_file)
        self.day = civil_day(utc_now(), self.h.config.timezone)
        atlas.sync(self.h.connection, self.h.atlas_repo,
                   Path(self.h.config.policy_file).parent / "exclusions.txt")
        self.client = FakeClient(self.h.config, self.h.connection, self.day)

        records = []
        for index in range(TOTAL):
            record = {"kind": "repo", "repo": f"owner{index % 50}/project{index:04d}",
                      "status": "filed" if index % 2 else "pending"}
            if index % 97 == 0:
                record["latest"] = {"stars": index, "pushed_at": "2026-09-01T00:00:00Z"}
            records.append(record)
        records.append({"kind": "meta", "run": "2026-09-11"})
        records.append({"kind": "post", "id": "t3_x", "author": "someone"})
        self.h.feed(records)

        # Enough routed repositories to satisfy every inspection the budget allows.
        for index in range(80):
            repo_routes(self.client, f"owner{index % 50}/project{index:04d}", commit=COMMIT,
                        files=FILES, repo_id=5000 + index)

    def test_the_whole_index_imports_once_and_only_once(self):
        first = ingest_module.run(self.h.config, self.h.connection, None)
        self.assertEqual(first.repo_records, TOTAL)
        self.assertEqual(first.imported_new, TOTAL)
        self.assertEqual(first.other_records, 2)
        second = ingest_module.run(self.h.config, self.h.connection, None)
        self.assertEqual(second.imported_new, 0)
        self.assertEqual(second.duplicates, TOTAL)
        self.assertTrue(second.unchanged)
        self.assertEqual(
            self.h.connection.execute("SELECT COUNT(*) AS n FROM candidate").fetchone()["n"], TOTAL)

    def test_budgets_stop_the_run_and_leave_a_reported_backlog(self):
        ingest_module.run(self.h.config, self.h.connection, None)
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.h.connection, self.client, self.day, run)
        self.assertEqual(run.metadata_collected, 40)
        self.assertIn("metadata budget", run.budget_stopped)
        self.assertGreater(run.backlog_no_metadata, 1300)

        assess_module.run_stage_c(self.h.config, self.h.connection, self.client, self.policy,
                                  self.day, run, {})
        self.assertEqual(run.inspected, 10)
        self.assertIn("inspection budget", run.budget_stopped)
        # 20% of the inspection budget went to the rotating exploration share.
        self.assertEqual(run.exploration_slots, 2)

    def test_a_second_run_continues_rather_than_restarting(self):
        ingest_module.run(self.h.config, self.h.connection, None)
        first = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.h.connection, self.client, self.day,
                                       first, limit=20)
        self.assertEqual(first.metadata_collected, 20)
        second = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.h.connection, self.client, self.day,
                                       second, limit=35)
        self.assertEqual(second.metadata_collected, 15)
        self.assertEqual(
            self.h.connection.execute("SELECT COUNT(*) AS n FROM metadata").fetchone()["n"], 35)

    def test_the_daily_request_ceiling_is_never_exceeded(self):
        self.h.config.limits.requests_per_day = 50
        ingest_module.run(self.h.config, self.h.connection, None)
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.h.connection, self.client, self.day, run)
        used = self.h.connection.execute(
            "SELECT used FROM budget WHERE name = 'github_requests'").fetchone()["used"]
        self.assertLessEqual(used, 50 + 1)
        self.assertIsNotNone(run.budget_stopped)

    def test_a_full_day_leaves_no_scratch_and_a_bounded_state_directory(self):
        ingest_module.run(self.h.config, self.h.connection, None)
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.h.connection, self.client, self.day, run)
        assess_module.run_stage_c(self.h.config, self.h.connection, self.client, self.policy,
                                  self.day, run, {})
        shortlist = selection_module.finalize(self.h.connection, self.h.config)
        report = reports.build(self.h.config, self.h.connection, shortlist,
                               {"policy_version": self.policy.version,
                                "import": {"repo_records": TOTAL, "imported_new": TOTAL},
                                "assessment": {"inspected": run.inspected}},
                               {"status": "complete", "identity": "fixture"})
        day_file, digest = reports.write(self.h.config, report, shortlist.day)

        scratch = Scratch(self.h.config.scratch_root, self.h.config.state_dir,
                          max_bytes=self.h.config.limits.scratch_bytes)
        scratch.ensure()
        self.assertEqual([p.name for p in scratch.root.iterdir() if not p.name.startswith(".")], [])
        self.assertLess(directory_bytes(self.h.config.state_dir),
                        self.h.config.limits.state_bytes)

        # No repository source survives in durable state: only paths, hashes and
        # capped excerpts. The whole database stays far below the index it read.
        db_bytes = self.h.config.db_path.stat().st_size
        self.assertLess(db_bytes, 8 * 1024 * 1024)

        written = json.loads(day_file.read_text(encoding="utf-8"))
        self.assertEqual(written["import"]["repo_records"], TOTAL)
        self.assertLessEqual(written["selected"], self.h.config.daily_admissions)
        self.assertEqual(len(written["shortlist"]), written["selected"])
        self.assertTrue(digest.read_text().startswith("# Candidate shortlist"))

    def test_newly_imported_is_reported_separately_from_the_backlog(self):
        first = ingest_module.run(self.h.config, self.h.connection, None)
        self.assertEqual(first.imported_new, TOTAL)
        self.h.feed([{"kind": "repo", "repo": f"owner{index % 50}/project{index:04d}"}
                     for index in range(TOTAL)] + [{"kind": "repo", "repo": "brand/new"}])
        second = ingest_module.run(self.h.config, self.h.connection, None)
        self.assertEqual(second.imported_new, 1)
        self.assertEqual(second.duplicates, TOTAL)


if __name__ == "__main__":
    unittest.main()

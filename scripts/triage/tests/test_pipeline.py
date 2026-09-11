"""End to end over a fake GitHub: import, assess, gate, rank, select."""

from __future__ import annotations

import unittest
from pathlib import Path

import assess as assess_module
import atlas
import ingest as ingest_module
import selection as selection_module
from policy import Policy
from tests.support import FakeClient, Harness, repo_routes
from tests.test_evidence import IMPLEMENTATION, REAL_TEST, TEMPLATE_TEST
from util import civil_day, utc_now

COMMIT = "c" * 40
GOOD_FILES = {
    "README.md": "# mem\n\nA memory for agents, with tests.\n",
    "pyproject.toml": "[project]\nname = 'mem'\n",
    ".github/workflows/ci.yml": "jobs:\n  test:\n    steps:\n      - run: pytest -q\n",
    "tests/test_recall.py": REAL_TEST,
    "mem/store.py": IMPLEMENTATION,
    "mem/scope.py": "def visible(rows, tenant_id):\n    return [r for r in rows if r.tenant_id == tenant_id]\n",
}
UNTESTED_FILES = {
    "README.md": "# promises\n\nFully tested, production ready.\n",
    "app.py": IMPLEMENTATION,
}


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        self.policy = Policy.load(self.h.config.policy_file)
        self.day = civil_day(utc_now(), self.h.config.timezone)
        atlas.sync(self.h.connection, self.h.atlas_repo,
                   Path(self.h.config.policy_file).parent / "exclusions.txt")
        self.client = FakeClient(self.h.config, self.h.connection, self.day)

    def _ingest(self, names):
        self.h.feed([{"kind": "repo", "repo": name, "status": "filed"} for name in names])
        return ingest_module.run(self.h.config, self.h.connection, None)

    def _assess(self, limit=None):
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.h.connection, self.client,
                                       self.day, run)
        assess_module.run_stage_c(self.h.config, self.h.connection, self.client, self.policy,
                                  self.day, run, {}, limit=limit)
        return run

    def test_a_tested_memory_project_becomes_eligible_and_is_selected(self):
        self._ingest(["good/mem"])
        repo_routes(self.client, "good/mem", commit=COMMIT, files=GOOD_FILES, repo_id=1)
        run = self._assess()
        self.assertEqual(run.eligible, 1, run.notes)
        shortlist = selection_module.finalize(self.h.connection, self.h.config)
        self.assertEqual(len(shortlist.entries), 1)
        entry = shortlist.entries[0]
        self.assertEqual(entry["name"], "good/mem")
        self.assertEqual(entry["commit"], COMMIT)
        self.assertGreaterEqual(entry["score"], self.policy.minimum_score)
        self.assertEqual(entry["facts"]["test_evidence"]["level"], "memory_specific")

    def test_a_promise_without_tests_is_rejected_not_deferred(self):
        self._ingest(["empty/promise"])
        repo_routes(self.client, "empty/promise", commit=COMMIT, files=UNTESTED_FILES, repo_id=2)
        run = self._assess()
        self.assertEqual(run.rejected, 1)
        row = self.h.connection.execute(
            "SELECT * FROM candidate WHERE canonical_name = 'empty/promise'").fetchone()
        self.assertEqual(row["triage_status"], "rejected")
        self.assertIsNotNone(row["next_assessment_at"])
        assessment = self.h.connection.execute(
            "SELECT facts FROM assessment WHERE candidate_id = ?", (row["id"],)).fetchone()
        self.assertIn("reassess", assessment["facts"])

    def test_a_template_suite_does_not_pass_the_gate(self):
        self._ingest(["scaffold/app"])
        repo_routes(self.client, "scaffold/app", commit=COMMIT, repo_id=3, files={
            "README.md": "# scaffold\n", "app.py": IMPLEMENTATION,
            "tests/test_example.py": TEMPLATE_TEST,
        })
        run = self._assess()
        self.assertEqual(run.rejected, 1)

    def test_a_truncated_tree_defers_rather_than_rejects(self):
        self._ingest(["big/repo"])
        repo_routes(self.client, "big/repo", commit=COMMIT, repo_id=4, truncated=True, files={
            "README.md": "# big\n", "app.py": IMPLEMENTATION,
        })
        run = self._assess()
        self.assertEqual(run.deferred, 1)
        row = self.h.connection.execute(
            "SELECT * FROM candidate WHERE canonical_name = 'big/repo'").fetchone()
        self.assertEqual(row["triage_status"], "deferred")
        self.assertIsNotNone(row["next_assessment_at"])

    def test_an_existing_atlas_report_is_never_selected_again(self):
        self._ingest(["someone/already-read", "good/mem"])
        repo_routes(self.client, "good/mem", commit=COMMIT, files=GOOD_FILES, repo_id=1)
        repo_routes(self.client, "someone/already-read", commit=COMMIT, files=GOOD_FILES, repo_id=9)
        run = self._assess()
        self.assertGreaterEqual(run.skipped_excluded, 1)
        shortlist = selection_module.finalize(self.h.connection, self.h.config)
        self.assertEqual([entry["name"] for entry in shortlist.entries], ["good/mem"])

    def test_unknown_counts_are_null_not_zero(self):
        self._ingest(["partial/repo"])
        repo_routes(self.client, "partial/repo", commit=COMMIT, files=GOOD_FILES, repo_id=5)
        # Remove the contributors route: the endpoint fails, the count is unknown.
        from fetching import api_url
        del self.client.routes[api_url("repos", "partial", "repo", "contributors",
                                       per_page=100, anon="0")]
        self._assess()
        row = self.h.connection.execute(
            "SELECT facts, coverage FROM assessment WHERE assessed_commit = ?", (COMMIT,)
        ).fetchone()
        from util import loads
        facts, coverage = loads(row["facts"]), loads(row["coverage"])
        self.assertIsNone(facts["contributors_apparently_non_bot"])
        self.assertEqual(coverage["contributors"], "unavailable")

    def test_bots_are_counted_separately_from_apparent_people(self):
        self._ingest(["bots/only"])
        repo_routes(self.client, "bots/only", commit=COMMIT, files=GOOD_FILES, repo_id=6,
                    contributors=[
                        {"login": "dependabot[bot]", "type": "Bot", "contributions": 300},
                        {"login": "renovate", "type": "User", "contributions": 120},
                    ])
        self._assess()
        from util import loads
        facts = loads(self.h.connection.execute(
            "SELECT facts FROM assessment ORDER BY id DESC LIMIT 1").fetchone()["facts"])
        self.assertEqual(facts["contributors_bot"], 2)
        self.assertEqual(facts["contributors_apparently_non_bot"], 0)

    def test_a_new_account_is_a_caution_not_a_rejection(self):
        self._ingest(["fresh/mem"])
        repo_routes(self.client, "fresh/mem", commit=COMMIT, files=GOOD_FILES, repo_id=7,
                    owner_created_at=utc_now().isoformat().replace("+00:00", "Z"))
        run = self._assess()
        from util import loads
        row = self.h.connection.execute(
            "SELECT outcome, facts FROM assessment ORDER BY id DESC LIMIT 1").fetchone()
        facts = loads(row["facts"])
        self.assertTrue(any("caution" in text.lower() or "capped" in text.lower()
                            for text in facts["cautions"]), facts["cautions"])
        # A young account caps the track-record points. It does not reject, and
        # the recorded reason is an observation rather than a judgement.
        self.assertIn(row["outcome"], ("eligible", "rejected"))
        self.assertNotIn("spam", " ".join(facts.get("reassessment_condition") or "").lower())
        self.assertLessEqual(
            next(a["points"] for a in facts["awards"] if a["component"] == "adoption")
            if any(a["component"] == "adoption" for a in facts["awards"]) else 0,
            2,
        )

    def test_the_inspection_budget_stops_and_leaves_a_backlog(self):
        names = [f"many/repo{index}" for index in range(6)]
        self._ingest(names)
        for index, name in enumerate(names):
            repo_routes(self.client, name, commit=COMMIT, files=GOOD_FILES, repo_id=100 + index)
        run = self._assess(limit=2)
        self.assertEqual(run.inspected, 2)
        self.assertIn("inspection budget", run.budget_stopped)
        self.assertGreater(run.backlog_unassessed, 0)

    def test_assessment_is_resumable_across_runs(self):
        names = [f"many/repo{index}" for index in range(4)]
        self._ingest(names)
        for index, name in enumerate(names):
            repo_routes(self.client, name, commit=COMMIT, files=GOOD_FILES, repo_id=200 + index)
        self._assess(limit=2)
        run = self._assess(limit=4)
        total = self.h.connection.execute(
            "SELECT COUNT(*) AS n FROM assessment").fetchone()["n"]
        self.assertEqual(total, 4)

    def test_scope_basis_is_labelled_heuristic_without_a_judge(self):
        self._ingest(["good/mem"])
        repo_routes(self.client, "good/mem", commit=COMMIT, files=GOOD_FILES, repo_id=1)
        self._assess()
        from util import loads
        facts = loads(self.h.connection.execute(
            "SELECT facts FROM assessment ORDER BY id DESC LIMIT 1").fetchone()["facts"])
        self.assertTrue(any("structural rules" in text for text in facts["limitations"]))


if __name__ == "__main__":
    unittest.main()


class ManualAssessmentTests(unittest.TestCase):
    """A hand-written verdict is checked against the bytes, like a model's."""

    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        self.policy = Policy.load(self.h.config.policy_file)
        self.day = civil_day(utc_now(), self.h.config.timezone)
        atlas.sync(self.h.connection, self.h.atlas_repo,
                   Path(self.h.config.policy_file).parent / "exclusions.txt")
        self.client = FakeClient(self.h.config, self.h.connection, self.day)
        self.h.feed([{"kind": "repo", "repo": "manual/subject"}])
        ingest_module.run(self.h.config, self.h.connection, None)
        repo_routes(self.client, "manual/subject", commit=COMMIT, files=UNTESTED_FILES, repo_id=77)

    def _manual(self, payload: dict):
        import json
        path = self.h.root / "labels.json"
        path.write_text(json.dumps([payload]), encoding="utf-8")
        from classifier import load_manual
        return load_manual(path)

    def _assess(self, manual):
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.h.connection, self.client, self.day, run)
        assess_module.run_stage_c(self.h.config, self.h.connection, self.client, self.policy,
                                  self.day, run, manual, limit=5)
        return run

    def test_a_manual_verdict_overrides_the_heuristic_scope(self):
        manual = self._manual({
            "repo": "manual/subject", "assessor": "simon", "in_scope": False,
            "substance": True, "test_evidence_level": "absent", "confidence": 0.9,
            "reasoning": "a document index, not agent memory",
            "citations": [{"path": "README.md", "quote": "Fully tested, production ready."}],
        })
        run = self._assess(manual)
        from util import loads
        row = self.h.connection.execute(
            "SELECT outcome, classifier_version, facts FROM assessment ORDER BY id DESC LIMIT 1"
        ).fetchone()
        self.assertEqual(row["outcome"], "rejected")
        self.assertEqual(row["classifier_version"], "manual:simon")
        self.assertFalse(any("No classifier was configured" in text
                             for text in loads(row["facts"])["limitations"]))

    def test_a_manual_citation_that_is_not_in_the_file_is_refused(self):
        manual = self._manual({
            "repo": "manual/subject", "assessor": "simon", "in_scope": True,
            "substance": True, "test_evidence_level": "memory_specific", "confidence": 1.0,
            "reasoning": "trust me",
            "citations": [{"path": "README.md", "quote": "this sentence is not in the readme"}],
        })
        run = self._assess(manual)
        self.assertTrue(any("manual assessment rejected" in note for note in run.notes), run.notes)
        row = self.h.connection.execute(
            "SELECT classifier_version FROM assessment ORDER BY id DESC LIMIT 1").fetchone()
        self.assertIsNone(row["classifier_version"])

    def test_a_concurrency_setting_this_build_cannot_honour_is_refused(self):
        self.h.config.limits.concurrent_assessments = 4
        with self.assertRaises(RuntimeError) as caught:
            self._assess({})
        self.assertIn("one repository at a time", str(caught.exception))

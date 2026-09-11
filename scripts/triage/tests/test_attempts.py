"""Section 11: leases, fencing tokens, and results that cannot overwrite each other."""

from __future__ import annotations

import unittest
import uuid
from pathlib import Path

import atlas
import attempts
import selection as selection_module
from db import transaction
from tests.support import Harness
from util import dumps, iso, plus, utc_now


class AttemptTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        atlas.sync(self.h.connection, self.h.atlas_repo,
                   Path(self.h.config.policy_file).parent / "exclusions.txt")
        now = iso(utc_now())
        with transaction(self.h.connection):
            cursor = self.h.connection.execute(
                "INSERT INTO candidate(canonical_name, display_name, first_seen_at, last_seen_at, "
                "triage_status) VALUES ('owner/repo', 'owner/repo', ?, ?, 'eligible')", (now, now))
            candidate_id = int(cursor.lastrowid)
            assessment = self.h.connection.execute(
                "INSERT INTO assessment(uuid, candidate_id, assessed_commit, assessed_at, "
                "policy_version, outcome, score, components, gates, facts, coverage, reasons) "
                "VALUES (?, ?, ?, ?, 'test', 'eligible', 80, '{}', '{}', ?, '{}', '[]')",
                (str(uuid.uuid4()), candidate_id, "a" * 40, now, dumps({"head_commit": "a" * 40})))
            self.h.connection.execute(
                "UPDATE candidate SET latest_assessment = ? WHERE id = ?",
                (int(assessment.lastrowid), candidate_id))
        self.shortlist = selection_module.finalize(self.h.connection, self.h.config)
        self.selection_id = self.shortlist.entries[0]["selection_id"]

    def test_a_claim_takes_a_lease_and_a_second_claim_is_refused(self):
        first = attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-a")
        self.assertEqual(first.fence, 1)
        with self.assertRaises(attempts.ClaimRefused) as caught:
            attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-b")
        self.assertIn("holds a lease", str(caught.exception))

    def test_an_expired_lease_is_reclaimed_with_a_higher_fence(self):
        first = attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-a")
        self.h.connection.execute(
            "UPDATE attempt SET lease_expires = ? WHERE uuid = ?",
            (iso(plus(utc_now(), seconds=-60)), first.attempt_id))
        second = attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-b")
        self.assertEqual(second.fence, 2)
        self.assertEqual(second.reclaimed_from, first.attempt_id)
        superseded = self.h.connection.execute(
            "SELECT status FROM attempt WHERE uuid = ?", (first.attempt_id,)).fetchone()
        self.assertEqual(superseded["status"], "superseded")

    def test_a_superseded_worker_cannot_overwrite_the_newer_attempt(self):
        first = attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-a")
        self.h.connection.execute(
            "UPDATE attempt SET lease_expires = ? WHERE uuid = ?",
            (iso(plus(utc_now(), seconds=-60)), first.attempt_id))
        second = attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-b")
        attempts.record(self.h.connection, second.attempt_id, {
            "status": "accepted", "analysed_commit": "b" * 40,
            "report": "content/systems/owner-repo.md"})
        with self.assertRaises(attempts.ResultRefused):
            attempts.record(self.h.connection, first.attempt_id, {
                "status": "rejected", "analysed_commit": "a" * 40, "reason": "out of scope"})
        candidate = self.h.connection.execute(
            "SELECT analysis_status FROM candidate LIMIT 1").fetchone()
        self.assertEqual(candidate["analysis_status"], "accepted")
        stale = self.h.connection.execute("SELECT COUNT(*) AS n FROM stale_submission").fetchone()
        self.assertGreaterEqual(stale["n"], 1)

    def test_a_technical_error_is_not_a_rejection_and_keeps_the_admission(self):
        claim = attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-a")
        attempts.record(self.h.connection, claim.attempt_id,
                        {"status": "error", "retryable": True, "category": "network"})
        candidate = self.h.connection.execute(
            "SELECT analysis_status FROM candidate LIMIT 1").fetchone()
        self.assertEqual(candidate["analysis_status"], "selected")
        selection = self.h.connection.execute("SELECT state FROM selection").fetchone()
        self.assertEqual(selection["state"], "open")
        # The retry continues the same selection: no new admission is spent.
        retry = attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-a")
        self.assertEqual(retry.selection_id, self.selection_id)
        self.assertEqual(
            self.h.connection.execute("SELECT COUNT(*) AS n FROM selection").fetchone()["n"], 1)

    def test_an_identical_resubmission_is_idempotent(self):
        claim = attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-a")
        payload = {"status": "accepted", "analysed_commit": "b" * 40, "report": "report.md"}
        attempts.record(self.h.connection, claim.attempt_id, dict(payload))
        again = attempts.record(self.h.connection, claim.attempt_id, dict(payload))
        self.assertTrue(again["idempotent"])

    def test_a_conflicting_resubmission_is_refused_and_recorded(self):
        claim = attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-a")
        attempts.record(self.h.connection, claim.attempt_id,
                        {"status": "accepted", "analysed_commit": "b" * 40, "report": "r.md"})
        with self.assertRaises(attempts.ResultRefused):
            attempts.record(self.h.connection, claim.attempt_id,
                            {"status": "rejected", "analysed_commit": "b" * 40, "reason": "no"})
        current = self.h.connection.execute("SELECT status FROM attempt").fetchone()
        self.assertEqual(current["status"], "accepted")

    def test_results_must_carry_the_commit_that_was_actually_analysed(self):
        claim = attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-a")
        with self.assertRaises(attempts.ResultRefused):
            attempts.record(self.h.connection, claim.attempt_id,
                            {"status": "accepted", "report": "r.md"})
        with self.assertRaises(attempts.ResultRefused):
            attempts.record(self.h.connection, claim.attempt_id,
                            {"status": "error", "category": "network"})

    def test_an_analysis_rejection_does_not_touch_the_source_file(self):
        self.h.feed([{"kind": "repo", "repo": "owner/repo"}])
        before = self.h.config.source_file.read_bytes()
        claim = attempts.claim(self.h.connection, self.h.config, self.selection_id, "worker-a")
        attempts.record(self.h.connection, claim.attempt_id, {
            "status": "rejected", "analysed_commit": "b" * 40,
            "reason": "a context buffer, not a memory"})
        self.assertEqual(self.h.config.source_file.read_bytes(), before)
        candidate = self.h.connection.execute(
            "SELECT analysis_status, triage_reason FROM candidate LIMIT 1").fetchone()
        self.assertEqual(candidate["analysis_status"], "rejected")
        self.assertIn("context buffer", candidate["triage_reason"])


if __name__ == "__main__":
    unittest.main()

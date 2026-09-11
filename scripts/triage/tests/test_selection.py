"""Section 11: the daily and outstanding ceilings, and what a rerun does."""

from __future__ import annotations

import unittest
import uuid
from pathlib import Path

import atlas
import selection as selection_module
from db import transaction
from tests.support import Harness
from util import civil_day, dumps, iso, plus, utc_now


class CapacityTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        atlas.sync(self.h.connection, self.h.atlas_repo,
                   Path(self.h.config.policy_file).parent / "exclusions.txt")
        self.seed(40)

    def seed(self, count: int) -> None:
        """Eligible candidates with fresh assessments, descending score."""
        now = iso(utc_now())
        with transaction(self.h.connection):
            for index in range(count):
                cursor = self.h.connection.execute(
                    "INSERT INTO candidate(canonical_name, display_name, first_seen_at, "
                    "last_seen_at, triage_status) VALUES (?, ?, ?, ?, 'eligible')",
                    (f"owner/repo{index:03d}", f"owner/repo{index:03d}", now, now),
                )
                candidate_id = int(cursor.lastrowid)
                assessment = self.h.connection.execute(
                    "INSERT INTO assessment(uuid, candidate_id, assessed_commit, assessed_at, "
                    "policy_version, outcome, score, components, gates, facts, coverage, reasons) "
                    "VALUES (?, ?, ?, ?, 'test', 'eligible', ?, '{}', '{}', ?, '{}', '[]')",
                    (str(uuid.uuid4()), candidate_id, "a" * 40, now, 100 - index,
                     dumps({"head_commit": "a" * 40})),
                )
                self.h.connection.execute(
                    "UPDATE candidate SET latest_assessment = ? WHERE id = ?",
                    (int(assessment.lastrowid), candidate_id),
                )

    def test_a_day_admits_at_most_the_daily_limit(self):
        shortlist = selection_module.finalize(self.h.connection, self.h.config)
        self.assertEqual(len(shortlist.entries), self.h.config.daily_admissions)

    def test_the_highest_scores_go_first_and_ties_break_deterministically(self):
        shortlist = selection_module.finalize(self.h.connection, self.h.config)
        scores = [entry["score"] for entry in shortlist.entries]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(shortlist.entries[0]["name"], "owner/repo000")

    def test_a_rerun_regenerates_the_same_list_without_admitting_more(self):
        first = selection_module.finalize(self.h.connection, self.h.config)
        second = selection_module.finalize(self.h.connection, self.h.config)
        self.assertTrue(second.frozen)
        self.assertFalse(second.created)
        self.assertEqual([e["selection_id"] for e in first.entries],
                         [e["selection_id"] for e in second.entries])
        self.assertEqual(
            self.h.connection.execute("SELECT COUNT(*) AS n FROM selection").fetchone()["n"],
            self.h.config.daily_admissions,
        )

    def test_outstanding_capacity_bounds_a_second_day(self):
        selection_module.finalize(self.h.connection, self.h.config)
        # Move the ledger on a day without closing any analysis.
        tomorrow = _tomorrow(self.h.config)
        room = selection_module.capacity(self.h.connection, self.h.config, tomorrow)
        self.assertEqual(room.remaining_daily, 20)
        self.assertEqual(room.remaining_outstanding, 0)
        self.assertEqual(room.slots, 0)

    def test_a_historical_day_never_admits(self):
        shortlist = selection_module.finalize(self.h.connection, self.h.config, day="2020-01-01")
        self.assertEqual(shortlist.entries, [])
        self.assertFalse(shortlist.created)
        self.assertEqual(
            self.h.connection.execute("SELECT COUNT(*) AS n FROM selection").fetchone()["n"], 0)

    def test_a_dry_run_admits_nothing(self):
        shortlist = selection_module.finalize(self.h.connection, self.h.config, dry_run=True)
        self.assertEqual(len(shortlist.entries), 20)
        self.assertEqual(
            self.h.connection.execute("SELECT COUNT(*) AS n FROM selection").fetchone()["n"], 0)

    def test_a_stale_assessment_is_not_a_basis_for_selection(self):
        old = iso(plus(utc_now(), days=-30))
        self.h.connection.execute("UPDATE assessment SET assessed_at = ?", (old,))
        shortlist = selection_module.finalize(self.h.connection, self.h.config)
        self.assertEqual(shortlist.entries, [])
        self.assertEqual(shortlist.stale_skipped, 40)

    def test_a_moved_branch_invalidates_the_assessment(self):
        self.h.connection.execute(
            "UPDATE assessment SET facts = ?", (dumps({"head_commit": "f" * 40}),))
        shortlist = selection_module.finalize(self.h.connection, self.h.config)
        self.assertEqual(shortlist.entries, [])
        self.assertEqual(shortlist.stale_skipped, 40)

    def test_a_cancelled_selection_is_not_backfilled_the_same_day(self):
        selection_module.finalize(self.h.connection, self.h.config)
        self.h.connection.execute(
            "UPDATE selection SET state = 'cancelled' WHERE slot <= 5")
        self.h.connection.execute(
            "UPDATE candidate SET analysis_status = 'cancelled' WHERE id IN "
            "(SELECT candidate_id FROM selection WHERE state = 'cancelled')")
        again = selection_module.finalize(self.h.connection, self.h.config)
        self.assertEqual(len(again.entries), 20)
        self.assertEqual(
            self.h.connection.execute("SELECT COUNT(*) AS n FROM selection").fetchone()["n"], 20)

    def test_a_timezone_change_does_not_reset_an_open_day(self):
        selection_module.finalize(self.h.connection, self.h.config)
        day = selection_module.today(self.h.config)
        self.h.config.timezone = "Pacific/Kiritimati"
        room = selection_module.capacity(self.h.connection, self.h.config, day)
        self.assertEqual(room.admitted_today, 20)
        self.assertEqual(room.remaining_daily, 0)

    def test_two_open_selections_for_one_candidate_are_impossible(self):
        selection_module.finalize(self.h.connection, self.h.config)
        row = self.h.connection.execute("SELECT * FROM selection LIMIT 1").fetchone()
        import sqlite3
        with self.assertRaises(sqlite3.IntegrityError):
            self.h.connection.execute(
                "INSERT INTO selection(uuid, day, tz, slot, candidate_id, assessment_id, "
                "created_at) VALUES (?, '2030-01-01', 'UTC', 1, ?, ?, ?)",
                (str(uuid.uuid4()), row["candidate_id"], row["assessment_id"], iso(utc_now())),
            )

    def test_an_empty_pool_is_reported_as_such(self):
        self.h.connection.execute("UPDATE candidate SET triage_status = 'deferred'")
        shortlist = selection_module.finalize(self.h.connection, self.h.config)
        self.assertEqual(shortlist.entries, [])
        self.assertTrue(any("not a claim to have assessed" in note for note in shortlist.notes))

    def test_selection_refuses_without_an_atlas_inventory(self):
        self.h.connection.execute("DELETE FROM atlas_member")
        with self.assertRaises(atlas.InventoryUnavailable):
            selection_module.finalize(self.h.connection, self.h.config)


def _tomorrow(config) -> str:
    return civil_day(plus(utc_now(), days=1), config.timezone)


if __name__ == "__main__":
    unittest.main()

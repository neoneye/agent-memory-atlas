"""Section 11: budgets reset on the right boundary, caches stay bounded, logs rotate."""

from __future__ import annotations

import unittest
from pathlib import Path

import journal
from db import budget_used, spend, transaction, vacuum_cache
from tests.support import Harness
from util import iso, plus, utc_now


class BudgetBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)

    def test_a_spent_budget_survives_restart(self):
        with transaction(self.h.connection):
            spend(self.h.connection, "2026-09-11", "github_requests", 2999)
        self.h.connection.close()
        import db
        self.h.connection = db.connect(self.h.config.db_path)
        self.assertEqual(budget_used(self.h.connection, "2026-09-11", "github_requests"), 2999)

    def test_a_new_day_resets_the_quota_without_touching_decisions(self):
        now = iso(utc_now())
        with transaction(self.h.connection):
            spend(self.h.connection, "2026-09-11", "github_requests", 3000)
            self.h.connection.execute(
                "INSERT INTO candidate(canonical_name, display_name, first_seen_at, last_seen_at, "
                "triage_status, triage_reason) VALUES ('a/b', 'a/b', ?, ?, 'rejected', 'no tests')",
                (now, now))
        self.assertEqual(budget_used(self.h.connection, "2026-09-12", "github_requests"), 0)
        row = self.h.connection.execute("SELECT * FROM candidate").fetchone()
        self.assertEqual(row["triage_status"], "rejected")
        self.assertEqual(row["triage_reason"], "no tests")

    def test_failed_requests_count_against_the_budget(self):
        from fetching import FetchError, NOT_FOUND
        from tests.support import FakeClient
        client = FakeClient(self.h.config, self.h.connection, "2026-09-11")
        with self.assertRaises(FetchError):
            client.get("https://api.github.com/repos/nobody/nothing")
        self.assertEqual(budget_used(self.h.connection, "2026-09-11", "github_requests"), 1)


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)

    def _put(self, key: str, size: int, *, age_days: float = 0) -> None:
        self.h.connection.execute(
            "INSERT OR REPLACE INTO http_cache(url_hash, url, fetched_at, status, bytes, body) "
            "VALUES (?, ?, ?, 200, ?, ?)",
            (key, f"https://api.github.com/{key}", iso(plus(utc_now(), days=-age_days)),
             size, b"x" * size),
        )

    def test_expired_entries_are_removed(self):
        self._put("old", 100, age_days=30)
        self._put("new", 100)
        with transaction(self.h.connection):
            result = vacuum_cache(self.h.connection, ttl_days=7, max_bytes=1 << 20)
        self.assertEqual(result["expired"], 1)
        self.assertEqual(
            self.h.connection.execute("SELECT COUNT(*) AS n FROM http_cache").fetchone()["n"], 1)

    def test_the_cache_is_evicted_down_to_its_ceiling(self):
        for index in range(20):
            self._put(f"k{index:02d}", 1000, age_days=20 - index)
        with transaction(self.h.connection):
            result = vacuum_cache(self.h.connection, ttl_days=365, max_bytes=5000)
        self.assertLessEqual(result["bytes"], 5000)
        self.assertGreater(result["evicted"], 0)
        # Eviction is least-recently-fetched first: the newest survives.
        remaining = {row["url_hash"] for row in
                     self.h.connection.execute("SELECT url_hash FROM http_cache")}
        self.assertIn("k19", remaining)
        self.assertNotIn("k00", remaining)

    def test_repeated_days_do_not_grow_the_cache_without_bound(self):
        for day in range(10):
            for index in range(50):
                self._put(f"d{day}-{index}", 2000)
            with transaction(self.h.connection):
                vacuum_cache(self.h.connection, ttl_days=7, max_bytes=20000)
        total = self.h.connection.execute(
            "SELECT COALESCE(SUM(bytes), 0) AS n FROM http_cache").fetchone()["n"]
        self.assertLessEqual(total, 20000)


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        self.path = self.h.config.log_path

    def test_a_token_never_reaches_the_log(self):
        journal.write(self.path, "ingest", {"detail": "failed with ghp_" + "a" * 36},
                      max_bytes=1 << 20)
        text = self.path.read_text()
        self.assertNotIn("ghp_", text)
        self.assertIn("[redacted]", text)

    def test_the_log_rotates_and_stays_bounded(self):
        for index in range(400):
            journal.write(self.path, "run", {"index": index, "pad": "x" * 200}, max_bytes=8192)
        live = self.path.stat().st_size
        previous = self.path.with_suffix(self.path.suffix + ".1")
        total = live + (previous.stat().st_size if previous.exists() else 0)
        self.assertLess(total, 8192 * 2 + 1000)
        self.assertTrue(previous.exists())

    def test_a_log_failure_never_fails_a_command(self):
        journal.write(Path("/proc/definitely/not/writable/triage.log"), "run", {},
                      max_bytes=1 << 20)


if __name__ == "__main__":
    unittest.main()

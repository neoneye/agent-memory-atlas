"""Metadata freshness through the real `Client` and its response cache.

`FakeClient` has no cache, so these tests keep the real request path and
replace only the socket: an opener that answers from a route table and counts
what it was asked.
"""

from __future__ import annotations

import io
import json
import unittest
from pathlib import Path

import assess as assess_module
import atlas
import ingest as ingest_module
from fetching import Client, api_url
from identity import find
from tests.support import FakeClient, Harness, repo_routes
from tests.test_intake_v2 import modern
from util import civil_day, iso, loads, plus, utc_now

COMMIT = "7" * 40


class _Stream(io.BytesIO):
    def __init__(self, body: bytes, headers: dict[str, str]):
        super().__init__(body)
        self.status = 200
        self.headers = headers


class RouteOpener:
    """Stands in for `urllib`'s opener. Everything above the socket — budget,
    cache read, cache write, bounded read — is the real `Client`."""

    def __init__(self, routes: dict):
        self.routes = routes
        self.asked: list[str] = []

    def open(self, request, timeout=None):
        url = request.full_url
        self.asked.append(url)
        payload, headers = self.routes[url]
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
        return _Stream(body, dict(headers))


class CachedRefreshTests(unittest.TestCase):
    NAME = "hot/one"

    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        self.conn = self.h.connection
        self.day = civil_day(utc_now(), self.h.config.timezone)
        atlas.sync(self.conn, self.h.atlas_repo, Path(self.h.config.policy_file).parent / "exclusions.txt")
        self.h.feed([modern(self.NAME, pushed_at="2026-09-01T00:00:00Z")])
        ingest_module.run(self.h.config, self.conn, None)
        # The route table repo_routes builds for the fake, served through the real client.
        table = FakeClient(self.h.config, self.conn, self.day)
        repo_routes(table, self.NAME, commit=COMMIT, files={"README.md": "x"}, stars=12)
        self.routes: dict[str, tuple] = {url: route for url, route in table.routes.items()
                                         if isinstance(url, str) and isinstance(route, tuple)}
        self.repo_url = api_url("repos", *self.NAME.split("/"))
        self.opener = RouteOpener(self.routes)

    def client(self) -> Client:
        client = Client(self.h.config, self.conn, self.day)
        client.opener = self.opener  # type: ignore[assignment]
        return client

    def collect(self) -> assess_module.AssessRun:
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.conn, self.client(), self.day, run)
        return run

    def metadata(self):
        cid = int(find(self.conn, name=self.NAME)["id"])  # type: ignore[index]
        return self.conn.execute("SELECT * FROM metadata WHERE candidate_id = ?", (cid,)).fetchone()

    def age_everything(self, days: int) -> str:
        """Move the measurement and every cached response `days` into the past,
        still inside the cache's seven-day life."""
        then = iso(plus(utc_now(), days=-days))
        self.conn.execute("UPDATE metadata SET collected_at = ?", (then,))
        self.conn.execute("UPDATE http_cache SET fetched_at = ?", (then,))
        return then

    def restar(self, stars: int) -> None:
        payload, headers = self.routes[self.repo_url]
        self.routes[self.repo_url] = ({**payload, "stargazers_count": stars}, headers)

    def test_a_refresh_triggered_by_a_newer_push_reads_github_not_the_cache(self):
        self.assertEqual(self.collect().metadata_collected, 1)
        self.assertEqual(loads(self.metadata()["facts"])["stars"], 12)
        self.assertGreater(self.conn.execute("SELECT COUNT(*) FROM http_cache").fetchone()[0], 0,
                           "the first collection populated the cache the refresh must not trust")
        self.age_everything(3)
        self.restar(999)
        self.h.feed([modern(self.NAME, pushed_at=iso(utc_now()))])  # Scout reports a newer push
        ingest_module.run(self.h.config, self.conn, None)
        self.opener.asked.clear()

        run = self.collect()
        self.assertEqual(run.metadata_refreshed, 1)
        self.assertIn(self.repo_url, self.opener.asked)
        self.assertEqual(loads(self.metadata()["facts"])["stars"], 999)
        self.assertGreater(self.metadata()["collected_at"], iso(plus(utc_now(), days=-1)))

    def test_a_first_collection_from_cache_keeps_the_cache_date(self):
        self.collect()
        then = self.age_everything(3)
        self.conn.execute("DELETE FROM metadata")
        self.restar(999)
        self.opener.asked.clear()

        run = self.collect()
        self.assertEqual(run.metadata_collected, 1)
        self.assertNotIn(self.repo_url, self.opener.asked, "a first collection may use the cache")
        row = self.metadata()
        self.assertEqual(loads(row["facts"])["stars"], 12)
        self.assertEqual(row["collected_at"], then,
                         "dated by the oldest response used, not by when it was assembled")


if __name__ == "__main__":
    unittest.main()

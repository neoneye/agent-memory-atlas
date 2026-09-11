"""Scout's 11 September feed: nested hints, a retracted legacy batch, a larger file.

Acceptance cases from notes/2026-09-11-candidate-triage-v2.md. Every fixture is
synthetic and shaped like one of upstream's two record forms at commit
51be06e0; no live feed is committed.
"""

from __future__ import annotations

import json
import sqlite3
import unittest
import uuid
from pathlib import Path

import assess as assess_module
import atlas
import db
import ingest as ingest_module
import selection as selection_module
from fetching import RATE_LIMIT, FetchError, api_url
from identity import find
from policy import Policy
from tests.support import FakeClient, Harness, repo_routes
from tests.test_evidence import IMPLEMENTATION
from util import civil_day, dumps, iso, loads, plus, utc_now

COMMIT = "5" * 40


def modern(name: str, **latest) -> dict:
    payload = {
        "author": "a-reddit-user", "description": "persistent memory for agents",
        "html_url": f"https://github.com/{name}", "license": "MIT",
        "matched_terms": ["topic:ai-memory"], "posted_at": None,
        "pushed_at": "2026-09-08T01:40:23Z", "repo": name.lower(), "source": "github",
        "source_url": f"https://github.com/{name}", "stars": 12, "subreddit": None,
    }
    payload.update(latest)
    return {
        "kind": "repo", "repo": name.lower(), "status": "pending",
        "first_seen_at": "2026-09-11T04:21:49+00:00", "last_seen_at": "2026-09-11T04:22:43+00:00",
        "latest": payload, "sources": ["github"], "source_urls": [f"https://github.com/{name}"],
    }


def legacy(name: str, issue: int = 1) -> dict:
    return {"kind": "repo", "repo": name.lower(), "status": "filed", "issue_number": issue,
            "first_seen_at": "2026-09-11T04:21:44+00:00", "sources": [], "title_only": True}


def minimal(name: str) -> dict:
    return {"kind": "repo", "repo": name.lower(), "status": "filed", "issue_number": 123}


class Base(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        self.conn = self.h.connection
        self.policy = Policy.load(self.h.config.policy_file)
        self.day = civil_day(utc_now(), self.h.config.timezone)
        atlas.sync(self.conn, self.h.atlas_repo, Path(self.h.config.policy_file).parent / "exclusions.txt")

    def ingest(self, records):
        self.h.feed(records)
        return ingest_module.run(self.h.config, self.conn, None)

    def row(self, name) -> sqlite3.Row:
        found = find(self.conn, name=name)
        assert found is not None, f"{name} not in state"
        return found


class HintTests(Base):
    def test_nested_latest_hints_survive_and_extras_are_tolerated(self):
        rec = modern("Good/Mem", readme_bytes=0, unexpected={"nested": True})
        self.ingest([rec])
        hints = loads(self.row("good/mem")["hints"])
        self.assertEqual(hints["origin"], "latest")
        self.assertEqual(hints["description"], "persistent memory for agents")
        self.assertEqual(hints["stars"], 12)
        self.assertIsNone(hints["topics"], "absent topics are not an empty list")
        self.assertEqual(hints["readme_bytes"], 0, "a measured zero stays zero")
        self.assertEqual(hints["sources"], ["github"])
        blob = self.row("good/mem")["hints"] + self.row("good/mem")["provenance"]
        self.assertNotIn("a-reddit-user", blob, "Scout's Reddit author is never stored")

    def test_topics_present_but_empty_is_distinct_from_missing(self):
        self.ingest([modern("a/b", topics=[]), modern("c/d")])
        self.assertEqual(loads(self.row("a/b")["hints"])["topics"], [])
        self.assertIsNone(loads(self.row("c/d")["hints"])["topics"])

    def test_invalid_hint_types_are_dropped_not_coerced(self):
        self.ingest([modern("x/y", stars=True, readme_bytes="large", topics=["ok", 5, ""])])
        hints = loads(self.row("x/y")["hints"])
        self.assertIsNone(hints["stars"])
        self.assertIsNone(hints["readme_bytes"])
        self.assertEqual(hints["topics"], ["ok"])

    def test_older_top_level_fields_are_a_labelled_fallback(self):
        self.ingest([{"kind": "repo", "repo": "old/style", "description": "memory", "stars": 3}])
        hints = loads(self.row("old/style")["hints"])
        self.assertEqual(hints["origin"], "top_level")
        self.assertEqual(hints["stars"], 3)

    def test_hints_are_never_copied_into_measured_facts(self):
        self.ingest([modern("good/mem", stars=99999)])
        self.assertIsNone(self.conn.execute("SELECT 1 FROM metadata").fetchone())

    def test_missing_or_future_upstream_tier_fields_never_break_ingestion(self):
        rec = modern("tiered/one")
        rec["tier"], rec["score"], rec["score_version"] = "A", 97, "v3"
        result = self.ingest([rec, modern("plain/two")])
        self.assertEqual(result.status, "complete")
        hints = loads(self.row("tiered/one")["hints"])
        self.assertEqual((hints["upstream_tier"], hints["upstream_score"]), ("A", 97))
        self.assertNotIn("upstream_tier", loads(self.row("plain/two")["hints"]))


class LegacyHoldTests(Base):
    def test_minimal_filed_records_remain_ordinary_input(self):
        self.ingest([minimal("old/minimal")])
        row = self.row("old/minimal")
        self.assertIsNone(row["source_hold"])
        self.assertIn(int(row["id"]), [int(r["id"]) for r in assess_module.assessable(self.conn)])

    def test_title_only_records_import_held_and_cost_no_budget(self):
        self.ingest([legacy("retracted/one"), modern("good/mem")])
        self.assertEqual(self.row("retracted/one")["source_hold"], "legacy_title_only")
        client = FakeClient(self.h.config, self.conn, self.day)
        repo_routes(client, "good/mem", commit=COMMIT, files={"README.md": "x", "mem/store.py": IMPLEMENTATION})
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.conn, client, self.day, run)
        self.assertFalse(any("retracted" in url for url in client.calls))
        self.assertEqual(run.metadata_collected, 1)
        self.assertEqual(run.held_skipped, 1)

    def test_a_later_payload_clears_only_the_source_hold(self):
        self.ingest([legacy("comes/back")])
        self.assertEqual(self.row("comes/back")["source_hold"], "legacy_title_only")
        stale = modern("comes/back")
        stale["title_only"] = True  # upstream left the flag stale
        result = self.ingest([stale])
        row = self.row("comes/back")
        self.assertIsNone(row["source_hold"])
        self.assertEqual(row["source_hold_disposition"], "cleared_by_payload")
        self.assertEqual(result.holds_cleared, 1)

    def test_an_analysis_rejection_outranks_the_hold_and_survives_a_payload(self):
        self.ingest([minimal("was/rejected")])
        self.conn.execute("UPDATE candidate SET analysis_status = 'rejected', triage_status = 'rejected'")
        self.ingest([legacy("was/rejected")])
        row = self.row("was/rejected")
        self.assertIsNone(row["source_hold"])
        self.assertEqual(row["source_hold_disposition"], "analysis_precedence")
        self.ingest([modern("was/rejected")])
        row = self.row("was/rejected")
        self.assertEqual((row["analysis_status"], row["triage_status"]), ("rejected", "rejected"))

    def test_a_policy_change_does_not_reopen_the_held_batch(self):
        self.ingest([legacy("held/one")])
        cid = int(self.row("held/one")["id"])
        a = self.conn.execute(
            "INSERT INTO assessment(uuid, candidate_id, assessed_at, policy_version, outcome) "
            "VALUES (?, ?, ?, 'old.0', 'rejected')", (str(uuid.uuid4()), cid, iso(utc_now()))).lastrowid
        self.conn.execute("UPDATE candidate SET triage_status='rejected', latest_assessment=? WHERE id=?", (a, cid))
        names = [r["canonical_name"] for r in assess_module.assessable(self.conn, "brand-new.9")]
        self.assertNotIn("held/one", names)

    def test_release_is_explicit_bounded_and_not_undone_by_reimport(self):
        self.ingest([legacy(f"held/r{i:03d}", i) for i in range(80)])
        released = ingest_module.release_holds(self.conn, batch=500)
        self.assertEqual(len(released), 50, "a batch is capped")
        one = ingest_module.release_holds(self.conn, names=["held/r070"])
        self.assertEqual(one, ["held/r070"])
        self.ingest([legacy(f"held/r{i:03d}", i) for i in range(80)])
        self.assertEqual(self.row("held/r070")["source_hold"], "released")
        self.assertEqual(self.conn.execute(
            "SELECT COUNT(*) FROM candidate WHERE source_hold='legacy_title_only'").fetchone()[0], 29)


def build_v1_state(path: Path, timezone: str) -> dict:
    """A database exactly as the v1 build left it, with real work in it: one
    candidate selected on a frozen day, one accepted, one eligible and waiting."""
    for suffix in ("", "-wal", "-shm"):
        Path(str(path) + suffix).unlink(missing_ok=True)
    c = sqlite3.connect(path); c.isolation_level = None; c.row_factory = sqlite3.Row
    for stmt in db._statements(db.MIGRATIONS[0][1]):
        c.execute(stmt)
    c.execute("INSERT INTO meta VALUES ('schema_version', '1')")
    c.execute("INSERT INTO meta VALUES ('policy_version', '2026-09-11.2')")
    now = iso(utc_now()); day = civil_day(utc_now(), timezone)
    def cand(name, triage, analysis):
        cid = c.execute("INSERT INTO candidate(canonical_name, display_name, first_seen_at, last_seen_at, "
                        "triage_status, analysis_status) VALUES (?,?,?,?,?,?)",
                        (name, name, now, now, triage, analysis)).lastrowid
        aid = c.execute("INSERT INTO assessment(uuid, candidate_id, assessed_commit, assessed_at, policy_version, "
                        "outcome, score, facts) VALUES (?,?,?,?,?,?,?,?)",
                        (str(uuid.uuid4()), cid, "a" * 40, now, "2026-09-11.2", triage, 70,
                         dumps({"head_commit": "a" * 40}))).lastrowid
        c.execute("UPDATE candidate SET latest_assessment=? WHERE id=?", (aid, cid))
        return cid, aid
    selected, sel_aid = cand("was/selected", "eligible", "selected")
    accepted, _ = cand("was/accepted", "eligible", "accepted")
    eligible, _ = cand("was/eligible", "eligible", "not_selected")
    c.execute("INSERT INTO day_ledger(day, tz, frozen_at, admitted) VALUES (?, ?, ?, 1)",
              (day, timezone, now))
    sel_uuid = str(uuid.uuid4())
    c.execute("INSERT INTO selection(uuid, day, tz, slot, candidate_id, assessment_id, selected_commit, created_at) "
              "VALUES (?,?,?,1,?,?,?,?)", (sel_uuid, day, timezone, selected, sel_aid, "a" * 40, now))
    c.close()
    return {"selected": selected, "accepted": accepted, "eligible": eligible, "sel_uuid": sel_uuid}


def v1_backup(path: Path, timezone: str, target: Path) -> dict:
    """A backup as the v1 build's `export` wrote it: header at schema 1, and
    rows carrying only v1 columns, including meta's own schema_version = 1."""
    import __main__ as entry
    ids = build_v1_state(path, timezone)
    c = sqlite3.connect(path); c.row_factory = sqlite3.Row
    lines = [dumps({"kind": "header", "schema_version": 1, "policy_version": "2026-09-11.2",
                    "exported_at": iso(utc_now()), "source": "test"})]
    for table in entry.EXPORT_TABLES:
        for row in c.execute(f"SELECT * FROM {table}"):
            lines.append(dumps({"kind": "row", "table": table, "row": {k: row[k] for k in row.keys()}}))
    c.close()
    for suffix in ("", "-wal", "-shm"):
        Path(str(path) + suffix).unlink(missing_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ids


class ExistingStateTests(unittest.TestCase):
    """A v1 database with real work in it, upgraded and then fed the new feed."""

    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        self.h.connection.close()
        path = self.h.config.db_path
        ids = build_v1_state(path, self.h.config.timezone)
        self.selected, self.accepted, self.eligible = ids["selected"], ids["accepted"], ids["eligible"]
        self.sel_uuid = ids["sel_uuid"]
        self.conn = db.connect(path)
        atlas.sync(self.conn, self.h.atlas_repo, Path(self.h.config.policy_file).parent / "exclusions.txt")
        self.h.connection = self.conn

    def test_migration_and_reimport_preserve_work_and_the_frozen_day(self):
        self.assertEqual(db.schema_version(self.conn), 2)
        self.h.feed([legacy("was/selected"), legacy("was/accepted"), legacy("was/eligible")])
        ingest_module.run(self.h.config, self.conn, None)
        rows = {r["canonical_name"]: r for r in self.conn.execute("SELECT * FROM candidate")}
        self.assertEqual(rows["was/selected"]["analysis_status"], "selected")
        self.assertIsNone(rows["was/selected"]["source_hold"])
        self.assertEqual(rows["was/accepted"]["source_hold_disposition"], "analysis_precedence")
        # Assessed before the hold: held for future automatic spending, evidence and status kept.
        self.assertEqual(rows["was/eligible"]["source_hold"], "legacy_title_only")
        self.assertEqual(rows["was/eligible"]["source_hold_disposition"], "assessed_before_hold")
        self.assertEqual(rows["was/eligible"]["triage_status"], "eligible")
        self.assertIsNotNone(rows["was/eligible"]["latest_assessment"])
        shortlist = selection_module.finalize(self.conn, self.h.config)
        self.assertTrue(shortlist.frozen)
        self.assertEqual([e["selection_id"] for e in shortlist.entries], [self.sel_uuid])
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM selection").fetchone()[0], 1)

    def test_a_held_eligible_candidate_is_offered_again_once_released(self):
        self.h.feed([legacy("was/eligible")])
        ingest_module.run(self.h.config, self.conn, None)
        pool, _ = selection_module.eligible_pool(self.conn, self.h.config)
        self.assertNotIn("was/eligible", [p["canonical"] for p in pool])
        self.assertEqual(selection_module.held_eligible(self.conn), 1)
        ingest_module.release_holds(self.conn, names=["was/eligible"])
        pool, _ = selection_module.eligible_pool(self.conn, self.h.config)
        self.assertIn("was/eligible", [p["canonical"] for p in pool])

    def test_export_restore_round_trip_keeps_holds_hints_and_admissions(self):
        import io
        from contextlib import redirect_stdout
        import __main__ as entry
        self.h.feed([legacy("was/eligible"), modern("new/one")])
        ingest_module.run(self.h.config, self.conn, None)
        backup = self.h.root / "backup.jsonl"
        base = ["--state-dir", str(self.h.config.state_dir), "--atlas-repo", str(self.h.atlas_repo), "--json"]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(entry.main(base + ["export", "--output", str(backup)]), 0)
            fresh = self.h.root / "restored"
            self.assertEqual(entry.main(["--state-dir", str(fresh), "--atlas-repo", str(self.h.atlas_repo),
                                         "--json", "restore", "--input", str(backup)]), 0)
        restored = db.connect(fresh / "triage.sqlite3")
        row = restored.execute("SELECT * FROM candidate WHERE canonical_name='was/eligible'").fetchone()
        self.assertEqual(row["source_hold"], "legacy_title_only")
        self.assertEqual(loads(restored.execute(
            "SELECT hints FROM candidate WHERE canonical_name='new/one'").fetchone()["hints"])["stars"], 12)
        self.assertEqual(restored.execute("SELECT uuid FROM selection").fetchone()["uuid"], self.sel_uuid)


class RestoreTests(unittest.TestCase):
    """A backup written by the v1 build, restored by this one, and then used."""

    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        self.backup = self.h.root / "v1-backup.jsonl"
        self.ids = v1_backup(self.h.root / "v1.sqlite3", self.h.config.timezone, self.backup)
        self.fresh = self.h.root / "restored"

    def cli(self, state_dir: Path, *argv: str) -> int:
        import io
        from contextlib import redirect_stderr, redirect_stdout
        import __main__ as entry
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return entry.main(["--state-dir", str(state_dir), "--atlas-repo", str(self.h.atlas_repo),
                               "--json", *argv])

    def test_a_v1_backup_restores_to_the_current_schema_and_reopens(self):
        self.assertEqual(self.cli(self.fresh, "restore", "--input", str(self.backup)), 0)
        # The next command opens it as every later run will. This is where a
        # rerun of migration 2 against columns the restore had built used to fail.
        self.assertEqual(self.cli(self.fresh, "status"), 0)
        self.assertEqual(self.cli(self.fresh, "status"), 0)
        conn = db.connect(self.fresh / "triage.sqlite3")
        self.addCleanup(conn.close)
        self.assertEqual(db.schema_version(conn), db.SCHEMA_VERSION)
        rows = {r["canonical_name"]: r for r in conn.execute("SELECT * FROM candidate")}
        self.assertEqual(rows["was/selected"]["analysis_status"], "selected")
        self.assertEqual(rows["was/accepted"]["analysis_status"], "accepted")
        self.assertEqual(rows["was/eligible"]["hints"], "{}", "v2 columns take their defaults")
        self.assertIsNone(rows["was/eligible"]["source_hold"])
        self.assertEqual(conn.execute("SELECT uuid FROM selection").fetchone()["uuid"], self.ids["sel_uuid"])
        self.assertEqual(db.get_meta(conn, "policy_version"), "2026-09-11.2")
        self.assertEqual(sorted(p.name for p in self.fresh.iterdir() if "restoring" in p.name), [])

    def test_the_restored_ledger_takes_the_new_feed_like_an_upgraded_one(self):
        self.assertEqual(self.cli(self.fresh, "restore", "--input", str(self.backup)), 0)
        conn = db.connect(self.fresh / "triage.sqlite3")
        self.addCleanup(conn.close)
        self.h.feed([legacy("was/selected"), legacy("was/accepted"), legacy("was/eligible")])
        result = ingest_module.run(self.h.config, conn, None)
        self.assertEqual(result.status, "complete", result.failure)
        row = conn.execute("SELECT * FROM candidate WHERE canonical_name='was/eligible'").fetchone()
        self.assertEqual((row["source_hold"], row["source_hold_disposition"]),
                         ("legacy_title_only", "assessed_before_hold"))

    def test_a_failed_restore_leaves_the_existing_ledger_in_place(self):
        existing = self.h.config.db_path
        self.h.connection.execute("INSERT INTO meta(key, value) VALUES ('marker', 'kept')")
        self.h.connection.close()
        broken = self.h.root / "broken.jsonl"
        lines = self.backup.read_text(encoding="utf-8").splitlines()
        # A v1 backup cannot carry a v2 column; this one claims to.
        lines.append(dumps({"kind": "row", "table": "candidate",
                            "row": {"id": 99, "canonical_name": "x/y", "display_name": "x/y",
                                    "first_seen_at": "t", "last_seen_at": "t", "hints": "{}"}}))
        broken.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertEqual(self.cli(self.h.config.state_dir, "restore", "--force", "--input", str(broken)), 2)
        conn = db.connect(existing)
        self.addCleanup(conn.close)
        self.assertEqual(db.get_meta(conn, "marker"), "kept")
        leftovers = [p.name for p in existing.parent.iterdir() if "restoring" in p.name or "replaced" in p.name]
        self.assertEqual(leftovers, [])

    def test_a_header_without_a_schema_version_is_refused(self):
        headless = self.h.root / "headless.jsonl"
        lines = self.backup.read_text(encoding="utf-8").splitlines()
        header = loads(lines[0]); header.pop("schema_version")
        headless.write_text("\n".join([dumps(header), *lines[1:]]) + "\n", encoding="utf-8")
        self.assertEqual(self.cli(self.fresh, "restore", "--input", str(headless)), 2)
        self.assertFalse((self.fresh / "triage.sqlite3").exists())


class ProvenanceTests(Base):
    def test_reordered_and_repeated_snapshots_add_no_observations(self):
        recs = [modern("a/one"), modern("b/two"), legacy("c/three")]
        self.ingest(recs)
        self.conn.execute("UPDATE candidate SET triage_status='rejected' WHERE canonical_name='a/one'")
        for i in range(10):
            again = [dict(r) for r in reversed(recs)]
            again[-1]["last_seen_at"] = f"2026-09-12T0{i}:00:00+00:00"  # Scout touched it again
            result = self.ingest(again)
            self.assertEqual(result.observations_added, 0)
        for name in ("a/one", "b/two", "c/three"):
            self.assertEqual(len(loads(self.row(name)["provenance"])["observations"]), 1)
        self.assertEqual(self.row("a/one")["triage_status"], "rejected")

    def test_a_meaningful_change_is_one_new_observation(self):
        self.ingest([modern("a/one", stars=1)])
        self.ingest([modern("a/one", stars=2)])
        self.assertEqual(len(loads(self.row("a/one")["provenance"])["observations"]), 2)

    def test_observations_stay_bounded_across_many_changing_imports(self):
        for stars in range(60):
            self.ingest([modern("busy/one", stars=stars)])
        self.assertEqual(len(loads(self.row("busy/one")["provenance"])["observations"]), 20)


class SchedulingTests(Base):
    def _seed(self):
        records = [legacy(f"old/l{i:02d}", i) for i in range(10)]
        records += [minimal(f"plain/m{i:02d}") for i in range(6)]
        records += [modern(f"hot/h{i:02d}", description="agent memory recall persist",
                           pushed_at=iso(utc_now()), stars=50) for i in range(6)]
        records += [modern(f"cold/c{i:02d}", description="a web framework", stars=0,
                           pushed_at="2019-01-01T00:00:00Z") for i in range(6)]
        self.ingest(records)

    def test_hinted_modern_rows_come_first_and_held_rows_never(self):
        self._seed()
        run = assess_module.AssessRun()
        queue = assess_module.metadata_queue(self.conn, self.h.config, run, 10)
        names = [row["canonical_name"] for row, _ in queue]
        self.assertFalse(any(n.startswith("old/") for n in names))
        self.assertTrue(all(n.startswith("hot/") for n in names[:6]), names)
        self.assertEqual(len(names), 10)

    def test_exploration_is_deterministic_and_reaches_unhinted_rows(self):
        self._seed()
        seen = set()
        for _ in range(10):
            run = assess_module.AssessRun()
            queue = assess_module.metadata_queue(self.conn, self.h.config, run, 5)
            for row, _ in queue:  # processed, as collect_metadata does
                assess_module.advance_rotation(self.conn, run, assess_module.METADATA_ROTATION, int(row["id"]))
            seen.update(row["canonical_name"] for row, _ in queue)
        self.assertEqual(len([n for n in seen if n.startswith("plain/")]), 6,
                         "the rotation walks every unhinted row, not one slice again and again")

        other = Harness(); self.addCleanup(other.close)
        atlas.sync(other.connection, other.atlas_repo, Path(other.config.policy_file).parent / "exclusions.txt")
        other.feed(json.loads("[" + ",".join(json.dumps(r) for r in [
            *[legacy(f"old/l{i:02d}", i) for i in range(10)], *[minimal(f"plain/m{i:02d}") for i in range(6)]]) + "]"))
        ingest_module.run(other.config, other.connection, None)
        first = [r["canonical_name"] for r, _ in assess_module.metadata_queue(other.connection, other.config, assess_module.AssessRun(), 5)]
        other.connection.execute("DELETE FROM rotation")
        second = [r["canonical_name"] for r, _ in assess_module.metadata_queue(other.connection, other.config, assess_module.AssessRun(), 5)]
        self.assertEqual(first, second)

    def test_stale_measurements_are_refreshed_under_the_budget(self):
        self.ingest([modern("hot/one")])
        cid = int(self.row("hot/one")["id"])
        old = iso(plus(utc_now(), days=-30))
        self.conn.execute("INSERT INTO metadata(candidate_id, collected_at, facts, coverage, prescore) "
                          "VALUES (?, ?, '{}', '{}', 0)", (cid, old))
        client = FakeClient(self.h.config, self.conn, self.day)
        repo_routes(client, "hot/one", commit=COMMIT, files={"README.md": "x"})
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.conn, client, self.day, run)
        self.assertEqual(run.metadata_refreshed, 1)
        fresh = self.conn.execute("SELECT collected_at FROM metadata WHERE candidate_id=?", (cid,)).fetchone()[0]
        self.assertGreater(fresh, old)

    def test_fresh_measurements_are_not_refetched_on_reimport(self):
        self.ingest([modern("hot/one")])
        cid = int(self.row("hot/one")["id"])
        self.conn.execute("INSERT INTO metadata(candidate_id, collected_at, facts, coverage, prescore) "
                          "VALUES (?, ?, '{}', '{}', 0)", (cid, iso(utc_now())))
        self.ingest([modern("hot/one", pushed_at=iso(plus(utc_now(), days=1)))])
        queue = assess_module.metadata_queue(self.conn, self.h.config, assess_module.AssessRun(), 10)
        self.assertEqual(queue, [], "a newer hinted push waits a day before it costs a request")

    def test_atlas_members_never_take_a_metadata_slot(self):
        # The member outranks the newcomer on every hint, and the allowance is
        # one repository: it must go to the newcomer, every day.
        self.ingest([modern("someone/already-read", description="agent memory recall persist",
                            pushed_at=iso(utc_now()), stars=5000),
                     modern("new/one", description="a web framework", stars=0)])
        self.h.config.exploration_share = 0.0
        for _ in range(2):
            run = assess_module.AssessRun()
            queue = assess_module.metadata_queue(self.conn, self.h.config, run, 1)
            self.assertEqual([row["canonical_name"] for row, _ in queue], ["new/one"])
            self.assertEqual(run.skipped_excluded, 1)
        client = FakeClient(self.h.config, self.conn, self.day)
        repo_routes(client, "new/one", commit=COMMIT, files={"README.md": "x"})
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.conn, client, self.day, run, limit=1)
        self.assertEqual(run.metadata_collected, 1)
        self.assertFalse(any("already-read" in url for url in client.calls))
        import reports
        self.assertEqual(reports.intake_summary(self.conn, self.h.config)["not_held_without_measurement"], 0,
                         "a repository the atlas reports on is no one's backlog")

    def test_unknown_values_are_never_read_as_measured_zero(self):
        self.assertEqual(assess_module.prescore({"stars": 0, "size_kb": None}),
                         assess_module.prescore({"stars": 0}))
        self.assertLess(assess_module.prescore({"size_kb": 3}), assess_module.prescore({"size_kb": None}))
        neutral = assess_module.hint_priority({"has_latest": True, "readme_bytes": None})
        absent = assess_module.hint_priority({"has_latest": True, "readme_bytes": 0})
        self.assertLess(absent, neutral)
        self.assertEqual(assess_module.hint_priority({"has_latest": True}), neutral)


class DayStopTests(Base):
    """A stop that belongs to the day — the request ceiling, a rate limit, a
    spent allowance — is never recorded against the repository in hand."""

    NAMES = [f"own{i}/repo{i}" for i in range(5)]

    def _client(self, ceiling: int | None = None) -> FakeClient:
        if ceiling is not None:
            self.h.config.limits.requests_per_day = ceiling
        client = FakeClient(self.h.config, self.conn, self.day)
        for i, name in enumerate(self.NAMES):
            repo_routes(client, name, commit=COMMIT, files={"README.md": "x", "mem/store.py": IMPLEMENTATION},
                        repo_id=5000 + i)
        return client

    def _deferred(self) -> list[str]:
        return [r["canonical_name"] for r in self.conn.execute(
            "SELECT canonical_name FROM candidate WHERE triage_status = 'deferred'")]

    def test_the_request_ceiling_mid_queue_defers_no_one(self):
        self.ingest([modern(name) for name in self.NAMES])
        probe = Harness(); self.addCleanup(probe.close)  # how many requests one collection costs
        atlas.sync(probe.connection, probe.atlas_repo, Path(probe.config.policy_file).parent / "exclusions.txt")
        probe.feed([modern(self.NAMES[0])]); ingest_module.run(probe.config, probe.connection, None)
        pc = FakeClient(probe.config, probe.connection, self.day)
        repo_routes(pc, self.NAMES[0], commit=COMMIT, files={"README.md": "x"}, repo_id=5000)
        assess_module.collect_metadata(probe.config, probe.connection, pc, self.day, assess_module.AssessRun())
        per_repo = len(pc.calls)

        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.conn, self._client(2 * per_repo + 2),
                                       self.day, run)
        self.assertEqual(run.metadata_collected, 2)
        self.assertEqual(run.metadata_failed, 0, "a request never made is not a failure")
        self.assertEqual(self._deferred(), [])
        self.assertIn("ceiling", run.budget_stopped or "")
        self.assertEqual(db.budget_used(self.conn, self.day, "metadata_repos"), 2,
                         "the cut-short collection spends no slot")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM metadata").fetchone()[0], 2)

    def test_a_rate_limit_mid_collection_defers_no_one(self):
        self.ingest([modern(self.NAMES[0])])
        client = self._client()
        owner, name = self.NAMES[0].split("/")
        client.route(api_url("repos", owner, name, "contributors", per_page=100, anon="0"),
                     FetchError(RATE_LIMIT, "HTTP 403", status=403))
        # The real client records the limit as it raises; the fake does not.
        self.conn.execute("INSERT INTO rate_limit(host, retry_at, reason, recorded_at) VALUES (?, ?, ?, ?)",
                          ("api.github.com", iso(plus(utc_now(), days=1)), "HTTP 403", iso(utc_now())))
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.conn, client, self.day, run)
        self.assertEqual((run.metadata_collected, run.metadata_failed), (0, 0))
        self.assertEqual(self._deferred(), [])
        self.assertIn("rate-limited", run.budget_stopped or "")

    def test_a_stop_mid_inspection_leaves_status_and_evidence_alone(self):
        self.ingest([modern(self.NAMES[0])])
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.conn, self._client(), self.day, run)
        cid = int(self.row(self.NAMES[0])["id"])
        self.conn.execute("UPDATE candidate SET triage_status = 'eligible' WHERE id = ?", (cid,))
        used = db.budget_used(self.conn, self.day, "github_requests")
        client = self._client(used)  # the ceiling is already reached: the tree read is refused
        before = self.conn.execute("SELECT COUNT(*) FROM assessment").fetchone()[0]
        run = assess_module.AssessRun()
        assess_module.run_stage_c(self.h.config, self.conn, client, self.policy, self.day, run, {})
        row = self.row(self.NAMES[0])
        self.assertEqual(row["triage_status"], "eligible", "a budget stop never overwrites a status")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM assessment").fetchone()[0], before)
        self.assertEqual(run.inspected, 0)
        self.assertEqual(db.budget_used(self.conn, self.day, "inspections"), 0)
        self.assertIn("ceiling", run.budget_stopped or "")

    def test_a_spent_day_offers_nothing_and_moves_no_cursor(self):
        import reports
        # Small enough that a queue built to the full allowance has an
        # exploration part, whose cursor a build-time write would move.
        self.h.config.inspection_budget, self.h.config.exploration_share = 4, 0.5
        self.ingest([modern(name) for name in self.NAMES])
        assess_module.collect_metadata(self.h.config, self.conn, self._client(), self.day,
                                       assess_module.AssessRun())
        db.spend(self.conn, self.day, "inspections", self.h.config.inspection_budget)
        self.conn.execute("DELETE FROM rotation")
        run = assess_module.AssessRun()
        assess_module.run_stage_c(self.h.config, self.conn, self._client(), self.policy, self.day, run, {})
        self.assertEqual((run.inspected, run.exploration_slots), (0, 0))
        self.assertIsNone(self.conn.execute("SELECT 1 FROM rotation").fetchone(),
                          "no candidate is skipped in the rotation by a run that inspected nothing")
        line = reports.digest({"day": self.day, "generated_at": iso(utc_now()), "generator": "test",
                               "timezone": self.h.config.timezone, "shortlist": [],
                               "assessment": {"inspected": 0, "exploration_slots": 0}})
        self.assertIn("0 repositories were inspected\n", line)
        self.assertNotIn("exploration share", line)

    def test_exploration_counts_inspections_made(self):
        self.h.config.exploration_share = 0.5
        self.ingest([modern(name) for name in self.NAMES])
        assess_module.collect_metadata(self.h.config, self.conn, self._client(), self.day,
                                       assess_module.AssessRun())
        run = assess_module.AssessRun()
        assess_module.run_stage_c(self.h.config, self.conn, self._client(), self.policy, self.day, run, {},
                                  limit=4)
        self.assertEqual(run.inspected, 4)
        self.assertEqual(run.exploration_slots, 2)
        cursor = self.conn.execute("SELECT cursor FROM rotation WHERE name = 'exploration'").fetchone()[0]
        self.assertIn(cursor, run.explored[assess_module.INSPECTION_ROTATION])


class GateIndependenceTests(Base):
    def test_a_high_upstream_tier_cannot_carry_a_readme_only_repository(self):
        rec = modern("promo/readme", description="the best agent memory, recall, persist", stars=5000)
        rec["tier"], rec["score"] = "A", 99
        self.ingest([rec])
        client = FakeClient(self.h.config, self.conn, self.day)
        repo_routes(client, "promo/readme", commit=COMMIT, files={"README.md": "memory " * 2000})
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.conn, client, self.day, run)
        assess_module.run_stage_c(self.h.config, self.conn, client, self.policy, self.day, run, {})
        self.assertEqual(run.eligible, 0)
        self.assertNotEqual(self.row("promo/readme")["triage_status"], "eligible")


class TransportTests(Base):
    URL = api_url("repos", "Daily-Nerd", "scout", "contents", "data", "candidates.jsonl", ref="main")

    def _client_with_feed(self, body: bytes, *, size=None, sha=None, raw: bytes | None = None,
                          inline: bytes | None = None):
        """Answer the way GitHub does: up to 1 MiB the JSON form carries the file
        as Base64 with a newline every 60 characters; above it, empty content."""
        import base64
        cfg = self.h.config
        cfg.source_kind = "github"
        client = FakeClient(cfg, self.conn, self.day)
        meta = {"size": len(body) if size is None else size,
                "sha": ingest_module.git_blob_sha(body) if sha is None else sha,
                "content": "", "encoding": "none"}
        carried = body if inline is None else inline
        if len(body) <= ingest_module.INLINE_LIMIT:
            encoded = base64.b64encode(carried).decode()
            meta["content"] = "\n".join(encoded[i:i + 60] for i in range(0, len(encoded), 60)) + "\n"
            meta["encoding"] = "base64"
        client.route(self.URL, meta, accept="application/vnd.github+json")
        client.route(self.URL, body if raw is None else raw, accept="application/vnd.github.raw")
        client.route(api_url("repos", "Daily-Nerd", "scout", "commits", path="data/candidates.jsonl",
                             sha="main", per_page=1), [{"sha": "51be06e0" + "0" * 32}])
        return client

    def _feed_of(self, approx_bytes: int) -> bytes:
        lines, total, i = [], 0, 0
        while total < approx_bytes:
            line = json.dumps(modern(f"owner{i % 97}/repo{i:05d}", description="agent memory " + "x" * 200))
            lines.append(line); total += len(line) + 1; i += 1
        return ("\n".join(lines) + "\n").encode()

    def test_feeds_between_200_kib_and_1_mib_import_from_the_inline_content(self):
        for approx in (220_575, 600 * 1024, 1000 * 1024):
            with self.subTest(bytes=approx):
                self.conn.execute("DELETE FROM candidate")
                body = self._feed_of(approx)
                self.assertLessEqual(len(body), ingest_module.INLINE_LIMIT)
                client = self._client_with_feed(body)
                result = ingest_module.run(self.h.config, self.conn, client)
                self.assertEqual(result.status, "complete", result.failure)
                self.assertEqual(result.verification, "blob-sha")
                self.assertEqual(client.calls.count(self.URL), 1, "the inline bytes are used, not fetched twice")

    def test_the_largest_inlined_file_fits_the_json_ceiling(self):
        body = b"x" * (ingest_module.INLINE_LIMIT - 1) + b"\n"
        client = self._client_with_feed(body)
        payload, _ = client.routes[(self.URL, "application/vnd.github+json")]
        self.assertLess(len(json.dumps(payload)), ingest_module.CONTENTS_JSON_BYTES)
        snapshot = ingest_module.fetch(self.h.config, client)
        self.assertEqual(snapshot.body, body)

    def test_inline_content_that_disagrees_with_the_reported_sha_is_refused(self):
        body = self._feed_of(300 * 1024)
        other = body.replace(b"agent memory", b"agent-memory", 1)
        result = ingest_module.run(self.h.config, self.conn, self._client_with_feed(body, inline=other))
        self.assertEqual(result.status, "failed")
        self.assertIn("git blob hash", result.failure)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM candidate").fetchone()[0], 0)

    def _big_feed(self) -> bytes:
        lines = [json.dumps(modern(f"owner{i % 97}/repo{i:05d}", description="agent memory " + "x" * 400))
                 for i in range(2600)]
        body = ("\n".join(lines) + "\n").encode()
        self.assertGreater(len(body), 1024 * 1024)
        return body

    def test_a_feed_over_one_mib_imports_through_raw_transport_verified(self):
        body = self._big_feed()
        result = ingest_module.run(self.h.config, self.conn, self._client_with_feed(body))
        self.assertEqual(result.status, "complete", result.failure)
        self.assertEqual(result.repo_records, 2600)
        self.assertEqual(result.verification, "blob-sha")
        self.assertTrue(result.upstream_commit.startswith("51be06e0"))

    def test_a_truncated_body_is_refused_and_prior_state_kept(self):
        body = self._big_feed()
        cut = ingest_module.run(self.h.config, self.conn,
                                self._client_with_feed(body, raw=body[:5000] + b"\n"))
        self.assertEqual(cut.status, "failed", "short body against the reported size")
        self.assertIn("truncated", cut.failure)
        before = self.conn.execute("SELECT COUNT(*) FROM candidate").fetchone()[0]
        self.assertEqual(before, 0)

    def test_a_different_body_with_the_right_size_is_refused(self):
        body = self._big_feed()
        other = body.replace(b"agent memory", b"agent-memory", 1)
        result = ingest_module.run(self.h.config, self.conn,
                                   self._client_with_feed(other, size=len(other), sha=ingest_module.git_blob_sha(body)))
        self.assertEqual(result.status, "failed")
        self.assertIn("git blob hash", result.failure)

    def test_a_feed_over_the_ceiling_is_refused_before_download(self):
        self.h.config.limits.feed_bytes = 512 * 1024
        result = ingest_module.run(self.h.config, self.conn, self._client_with_feed(self._big_feed()))
        self.assertEqual(result.status, "failed")
        self.assertIn("ceiling", result.failure)


class ReportTests(Base):
    def test_the_day_report_carries_the_intake_split(self):
        import reports
        self.ingest([legacy("old/one"), modern("new/one"), minimal("plain/one")])
        shortlist = selection_module.finalize(self.conn, self.h.config)
        report = reports.build(self.h.config, self.conn, shortlist, {}, {"status": "complete"})
        intake = report["intake"]
        self.assertEqual(intake["source_records"], {"with_hints": 1, "legacy_title_only": 1,
                                                    "without_hints_not_legacy": 1})
        self.assertEqual(intake["holds"].get("legacy_title_only"), 1)
        self.assertEqual(intake["accumulated_identities"], 3)
        digest = reports.digest(report)
        self.assertIn("## Intake", digest)
        self.assertIn("never an atlas score", digest)
        self.assertNotIn("passed triage", digest.lower())


if __name__ == "__main__":
    unittest.main()

"""SQLite state: schema, migrations, and the rule that nothing creates it by accident.

Triage owns this database. Scout's `candidates.jsonl` is read-only input and is
never written back. The one behaviour worth stating up front: every command
except `init` and `restore` *fails* when the database is absent, because the
alternative — creating an empty one and carrying on — reselects projects that
were analysed months ago and spends a day of the maintainer's analysis budget
proving it.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from util import iso, utc_now

SCHEMA_VERSION = 2


class StateMissing(RuntimeError):
    """No database where configuration says one should be."""


class StateCorrupt(RuntimeError):
    """A database that exists but cannot be trusted to continue from."""


MIGRATIONS: list[tuple[int, str]] = [
    (
        1,
        """
        CREATE TABLE meta (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        -- One row per fetch of the upstream feed, successful or not. A failed
        -- fetch is recorded and leaves every earlier decision intact.
        CREATE TABLE ingestion (
            id              INTEGER PRIMARY KEY,
            source_kind     TEXT NOT NULL,
            source_identity TEXT NOT NULL,
            transport       TEXT,
            fetched_at      TEXT NOT NULL,
            etag            TEXT,
            blob_sha        TEXT,
            content_hash    TEXT,
            content_bytes   INTEGER,
            status          TEXT NOT NULL CHECK (status IN ('complete','failed')),
            failure         TEXT,
            lines_total     INTEGER,
            repo_records    INTEGER,
            other_records   INTEGER,
            malformed       INTEGER,
            imported_new    INTEGER,
            duplicates      INTEGER,
            quarantine      TEXT
        );

        -- Identity is the GitHub repository id once resolved; the canonical
        -- owner/repo name is the bootstrap key and afterwards an alias.
        CREATE TABLE candidate (
            id                 INTEGER PRIMARY KEY,
            github_repo_id     INTEGER UNIQUE,
            canonical_name     TEXT NOT NULL UNIQUE,
            display_name       TEXT NOT NULL,
            first_seen_at      TEXT NOT NULL,
            last_seen_at       TEXT NOT NULL,
            provenance         TEXT NOT NULL DEFAULT '{}',
            triage_status      TEXT NOT NULL DEFAULT 'unassessed'
                               CHECK (triage_status IN ('unassessed','deferred','rejected','eligible')),
            triage_reason      TEXT,
            analysis_status    TEXT NOT NULL DEFAULT 'not_selected'
                               CHECK (analysis_status IN
                                      ('not_selected','selected','running','accepted','rejected','error','cancelled')),
            exclusion_reason   TEXT,
            next_assessment_at TEXT,
            last_assessed_at   TEXT,
            latest_assessment  INTEGER,
            inspections        INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX candidate_triage ON candidate(triage_status);
        CREATE INDEX candidate_analysis ON candidate(analysis_status);

        -- Every name a candidate has been known by, including its current one.
        -- A rename keeps the decision; a name reused by a different repository
        -- id becomes a separate candidate.
        CREATE TABLE alias (
            canonical_name TEXT PRIMARY KEY,
            candidate_id   INTEGER NOT NULL REFERENCES candidate(id) ON DELETE CASCADE,
            first_seen_at  TEXT NOT NULL,
            current        INTEGER NOT NULL DEFAULT 0
        );

        -- Immutable. A new reading appends; it never edits an older assessment.
        CREATE TABLE assessment (
            id                 INTEGER PRIMARY KEY,
            uuid               TEXT NOT NULL UNIQUE,
            candidate_id       INTEGER NOT NULL REFERENCES candidate(id) ON DELETE CASCADE,
            github_repo_id     INTEGER,
            assessed_commit    TEXT,
            assessed_at        TEXT NOT NULL,
            policy_version     TEXT NOT NULL,
            classifier_version TEXT,
            outcome            TEXT NOT NULL CHECK (outcome IN ('eligible','rejected','deferred')),
            score              INTEGER,
            components         TEXT NOT NULL DEFAULT '{}',
            gates              TEXT NOT NULL DEFAULT '{}',
            facts              TEXT NOT NULL DEFAULT '{}',
            coverage           TEXT NOT NULL DEFAULT '{}',
            reasons            TEXT NOT NULL DEFAULT '[]'
        );
        CREATE INDEX assessment_candidate ON assessment(candidate_id, assessed_at);

        -- The day ledger is what makes twenty a day mean twenty a day. A day is
        -- frozen once selected; a rerun regenerates the same list.
        CREATE TABLE day_ledger (
            day       TEXT PRIMARY KEY,
            tz        TEXT NOT NULL,
            frozen_at TEXT,
            admitted  INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE selection (
            id              INTEGER PRIMARY KEY,
            uuid            TEXT NOT NULL UNIQUE,
            day             TEXT NOT NULL REFERENCES day_ledger(day),
            tz              TEXT NOT NULL,
            slot            INTEGER NOT NULL,
            candidate_id    INTEGER NOT NULL REFERENCES candidate(id),
            assessment_id   INTEGER NOT NULL REFERENCES assessment(id),
            selected_commit TEXT,
            created_at      TEXT NOT NULL,
            state           TEXT NOT NULL DEFAULT 'open'
                            CHECK (state IN ('open','done','cancelled')),
            UNIQUE (day, slot),
            UNIQUE (day, candidate_id)
        );
        -- At most one live selection per candidate, enforced by the database
        -- rather than by whichever process happens to look first.
        CREATE UNIQUE INDEX selection_one_open ON selection(candidate_id) WHERE state = 'open';

        -- A claim on a selection. `fence` only ever increases, so a worker whose
        -- lease expired cannot overwrite the result of the worker that replaced it.
        CREATE TABLE attempt (
            id              INTEGER PRIMARY KEY,
            uuid            TEXT NOT NULL UNIQUE,
            selection_id    INTEGER NOT NULL REFERENCES selection(id),
            fence           INTEGER NOT NULL,
            worker          TEXT,
            claimed_at      TEXT NOT NULL,
            lease_expires   TEXT NOT NULL,
            status          TEXT NOT NULL CHECK (status IN
                            ('running','accepted','rejected','error','cancelled','superseded')),
            finished_at     TEXT,
            analysed_commit TEXT,
            result          TEXT,
            UNIQUE (selection_id, fence)
        );

        -- Rejected, stale or duplicate result submissions. Kept for diagnosis;
        -- they never change a current result.
        CREATE TABLE stale_submission (
            id           INTEGER PRIMARY KEY,
            attempt_uuid TEXT,
            received_at  TEXT NOT NULL,
            reason       TEXT NOT NULL,
            payload      TEXT
        );

        -- Budgets are per civil day and survive restart, so a rerun cannot spend
        -- an exhausted allowance a second time.
        CREATE TABLE budget (
            day  TEXT NOT NULL,
            name TEXT NOT NULL,
            used INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (day, name)
        );

        -- Metadata responses only. Source blobs are read, assessed and dropped.
        CREATE TABLE http_cache (
            url_hash   TEXT PRIMARY KEY,
            url        TEXT NOT NULL,
            etag       TEXT,
            fetched_at TEXT NOT NULL,
            status     INTEGER NOT NULL,
            bytes      INTEGER NOT NULL,
            body       BLOB NOT NULL
        );

        CREATE TABLE rate_limit (
            host       TEXT PRIMARY KEY,
            retry_at   TEXT NOT NULL,
            reason     TEXT,
            recorded_at TEXT NOT NULL
        );

        -- The atlas's own inventory, imported from report frontmatter. Selection
        -- stops rather than runs when this cannot be loaded.
        CREATE TABLE atlas_member (
            canonical_name TEXT PRIMARY KEY,
            slug           TEXT NOT NULL,
            revision       TEXT,
            analyzed_at    TEXT,
            imported_at    TEXT NOT NULL
        );

        -- Cheap metadata, kept between the collection stage and the inspection
        -- stage so ranking does not re-fetch. Facts only; no response bodies.
        CREATE TABLE metadata (
            candidate_id INTEGER PRIMARY KEY REFERENCES candidate(id) ON DELETE CASCADE,
            collected_at TEXT NOT NULL,
            facts        TEXT NOT NULL,
            coverage     TEXT NOT NULL,
            prescore     INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX metadata_prescore ON metadata(prescore DESC);

        -- Deterministic rotating exploration: where the last run stopped.
        CREATE TABLE rotation (
            name   TEXT PRIMARY KEY,
            cursor INTEGER NOT NULL DEFAULT 0
        );
        """,
    ),
    (
        2,
        """
        -- v2 (11 September 2026): Scout's feed now carries nested `latest`
        -- payloads beside a retracted, title-only legacy batch. Additive only,
        -- so a v1 database upgrades in place and nothing it held is reset.

        -- The current snapshot's validated hints for this identity. Labelled
        -- hints, never measurements: `metadata.facts` stays the atlas's own.
        ALTER TABLE candidate ADD COLUMN hints TEXT NOT NULL DEFAULT '{}';
        -- Scout's own observation time for those hints, distinct from
        -- `last_seen_at`, which is when this program last ingested the row.
        ALTER TABLE candidate ADD COLUMN hints_observed_at TEXT;
        -- A hold on automated intake, not a judgement about the project:
        -- NULL, 'legacy_title_only', or 'released' by the maintainer.
        ALTER TABLE candidate ADD COLUMN source_hold TEXT;
        ALTER TABLE candidate ADD COLUMN source_hold_disposition TEXT;
        ALTER TABLE candidate ADD COLUMN source_hold_changed_at TEXT;
        CREATE INDEX candidate_source_hold ON candidate(source_hold);

        -- Snapshot provenance for reproducible comparisons.
        ALTER TABLE ingestion ADD COLUMN upstream_commit TEXT;
        ALTER TABLE ingestion ADD COLUMN verification TEXT;
        ALTER TABLE ingestion ADD COLUMN source_shapes TEXT;
        """,
    ),
]


def _statements(script: str) -> list[str]:
    """Split a migration into statements without `executescript`.

    `executescript` commits whatever transaction is open before it runs, which
    would take each migration out of the transaction that is supposed to make it
    all-or-nothing. `sqlite3.complete_statement` does the splitting properly,
    including semicolons that fall inside literals.
    """
    statements: list[str] = []
    buffer = ""
    for line in script.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            text = buffer.strip()
            if text:
                statements.append(text)
            buffer = ""
    if buffer.strip():
        statements.append(buffer.strip())
    return statements


def _apply(connection: sqlite3.Connection, version: int, script: str) -> None:
    for statement in _statements(script):
        connection.execute(statement)
    connection.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES ('schema_version', ?)", (str(version),)
    )


def connect(path: Path, *, create: bool = False) -> sqlite3.Connection:
    """Open the state database.

    `create=False` and a missing file is an error, not an invitation.
    """
    if not path.exists():
        if not create:
            raise StateMissing(
                f"no triage state at {path}. Run `triage init` to create one, or "
                f"`triage restore --input <backup.jsonl>` to rebuild from a backup. "
                f"Nothing is created implicitly: an empty ledger would reselect "
                f"projects that were already analysed."
            )
        path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(path), isolation_level=None, timeout=30.0)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")
        current = schema_version(connection)
    except sqlite3.DatabaseError as error:
        # A file that exists and will not open is a fact to report, not a reason
        # to start a new ledger beside it.
        raise StateCorrupt(f"{path} is not a readable triage database: {error}") from error

    if current == 0 and not create:
        raise StateCorrupt(f"{path} exists but carries no schema version; refusing to guess.")

    for version, script in MIGRATIONS:
        if version > current:
            with transaction(connection):
                _apply(connection, version, script)
            current = version

    if current > SCHEMA_VERSION:
        raise StateCorrupt(
            f"{path} is at schema {current}; this build understands {SCHEMA_VERSION}. "
            f"Use the newer build or restore an older backup."
        )
    connection.execute(
        "INSERT OR IGNORE INTO meta(key, value) VALUES ('created_at', ?)", (iso(utc_now()),)
    )
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return connection


def schema_version(connection: sqlite3.Connection) -> int:
    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='meta'"
    ).fetchone()
    if row is None:
        return 0
    value = connection.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    return int(value["value"]) if value else 0


@contextmanager
def transaction(connection: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """IMMEDIATE so two runs contend for the write lock at the start rather than
    discovering the conflict after both have decided what to select."""
    connection.execute("BEGIN IMMEDIATE")
    try:
        yield connection
    except BaseException:
        connection.execute("ROLLBACK")
        raise
    connection.execute("COMMIT")


def get_meta(connection: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    row = connection.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_meta(connection: sqlite3.Connection, key: str, value: str) -> None:
    connection.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, value))


def budget_used(connection: sqlite3.Connection, day: str, name: str) -> int:
    row = connection.execute(
        "SELECT used FROM budget WHERE day = ? AND name = ?", (day, name)
    ).fetchone()
    return int(row["used"]) if row else 0


def spend(connection: sqlite3.Connection, day: str, name: str, amount: int = 1) -> int:
    """Record budget use. Failed requests and retries are spent here too — the
    ceiling exists to bound cost, and a request that errored still cost one."""
    connection.execute(
        "INSERT INTO budget(day, name, used) VALUES (?, ?, ?) "
        "ON CONFLICT(day, name) DO UPDATE SET used = used + excluded.used",
        (day, name, amount),
    )
    return budget_used(connection, day, name)


def vacuum_cache(connection: sqlite3.Connection, *, ttl_days: int, max_bytes: int) -> dict[str, int]:
    """Expire by age, then evict least-recently-fetched until under the ceiling.

    Run on every invocation. The maintainer does not reboot daily, so a cache
    that is only trimmed at startup is a cache that is never trimmed.
    """
    cutoff = iso(utc_now())
    removed_age = connection.execute(
        "DELETE FROM http_cache WHERE julianday(?) - julianday(fetched_at) > ?",
        (cutoff, ttl_days),
    ).rowcount
    removed_lru = 0
    total = connection.execute("SELECT COALESCE(SUM(bytes), 0) AS n FROM http_cache").fetchone()["n"]
    while total > max_bytes:
        row = connection.execute(
            "SELECT url_hash, bytes FROM http_cache ORDER BY fetched_at ASC LIMIT 1"
        ).fetchone()
        if row is None:
            break
        connection.execute("DELETE FROM http_cache WHERE url_hash = ?", (row["url_hash"],))
        total -= int(row["bytes"])
        removed_lru += 1
    return {"expired": max(removed_age, 0), "evicted": removed_lru, "bytes": total}

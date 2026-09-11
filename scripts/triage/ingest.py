"""Read Scout's candidate index and import identities. Never write it back.

Scout owns `data/candidates.jsonl`. It loads the whole file into dictionaries
keyed by repository name and post id, merges what it found today, and writes the
complete accumulated index back. That shape decides three things here:

* **Import the whole snapshot by identity, every time the bytes change.** A
  line-number cursor would be wrong on the first rewrite that reorders a record.
* **A repository missing from a later snapshot is not a deletion.** Scout is not
  an append-only event stream and does not intentionally drop candidates, but
  even if it did, a decision this program made stays made.
* **Repeated imports are idempotent.** The second import of an unchanged file
  adds nothing and changes nothing but `last_seen_at`.

`status: filed` means Scout filed an issue, not that the atlas assessed anything,
so `filed` and `pending` are both imported. Non-repository records — `post`,
`meta` — are counted and ignored. And Scout's Reddit `author` is the person who
wrote the post, never the repository's owner; it is not read here at all.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from config import Config
from db import transaction
from fetching import Client, FetchError, api_url, raw_url
from identity import InvalidName, canonical, upsert
from util import dumps, iso, loads, sha256_hex, truncate, utc_now


class IngestStopped(RuntimeError):
    """A feed that arrived but cannot be believed. Nothing is imported."""


@dataclass
class Snapshot:
    body: bytes
    identity: str
    kind: str
    transport: str
    etag: str | None = None
    blob_sha: str | None = None
    upstream_commit: str | None = None
    # How the bytes were checked: `blob-sha` when the Contents API's size and git
    # blob hash matched the body, `unverified` when only a transport fallback was
    # available, `file` for an explicit local source.
    verification: str = "unverified"

    @property
    def content_hash(self) -> str:
        return sha256_hex(self.body)


@dataclass
class ImportResult:
    ingestion_id: int
    status: str
    content_hash: str | None = None
    unchanged: bool = False
    lines_total: int = 0
    repo_records: int = 0
    other_records: int = 0
    malformed: int = 0
    invalid_names: int = 0
    imported_new: int = 0
    duplicates: int = 0
    quarantine: list[str] = field(default_factory=list)
    failure: str | None = None
    transport: str | None = None
    # (canonical_name, name as the feed wrote it, provenance, hints, shape) per valid record
    records: list[tuple[str, str, dict, dict, str]] = field(default_factory=list)
    # modern: a usable `latest` payload; legacy: `title_only` with none;
    # minimal: neither, the oldest shape, which stays ordinary input.
    shapes: dict[str, int] = field(default_factory=lambda: {"modern": 0, "legacy": 0, "minimal": 0})
    observations_added: int = 0
    holds_applied: int = 0
    holds_cleared: int = 0
    dispositions: dict[str, int] = field(default_factory=dict)
    upstream_commit: str | None = None
    verification: str | None = None


# --- fetching --------------------------------------------------------------

def git_blob_sha(body: bytes) -> str:
    """The object id git gives these bytes, so a download can be checked against
    the sha the Contents API reports for the file at that ref."""
    import hashlib
    return hashlib.sha1(b"blob %d\0" % len(body) + body).hexdigest()


def fetch(config: Config, client: Client | None) -> Snapshot:
    """Get the configured feed. A local file is an explicit choice, not a fallback.

    The feed passed 1 MiB on 11 September 2026, and the Contents API does not
    inline a file that size as Base64. So the fetch is two requests to the same
    endpoint: the JSON form, for the file's `size` and git blob `sha` at the ref,
    then the raw form, for the bytes — which are checked against both. A body
    that is short, long or different is refused before anything is imported,
    which is what makes a truncated download a failure rather than a feed that
    happens to have fewer rows.

    If the API is rate-limited, the same `repo@ref:path` is read from
    raw.githubusercontent.com and recorded as `unverified`. That is another
    route to the same file, not another source; there is deliberately no route
    to anyone's fork.
    """
    limits = config.limits
    if config.source_kind == "file":
        path = Path(config.source_file).expanduser() if config.source_file else None
        if path is None or not path.is_file():
            raise IngestStopped(f"configured local source {path} does not exist")
        size = path.stat().st_size
        if size > limits.feed_bytes:
            raise IngestStopped(f"{path} is {size} bytes, over the {limits.feed_bytes} ceiling")
        return Snapshot(path.read_bytes(), f"file:{path}", "file", "file", verification="file")

    if client is None:
        raise IngestStopped("no HTTP client available for a github source")

    owner, name = config.source_repo.split("/", 1)
    url = api_url("repos", owner, name, "contents", *config.source_path.split("/"),
                  ref=config.source_ref)
    try:
        meta = client.get(url, max_bytes=256 * 1024).json()
        expected_size = meta.get("size") if isinstance(meta, dict) else None
        expected_sha = meta.get("sha") if isinstance(meta, dict) else None
        if isinstance(expected_size, int) and expected_size > limits.feed_bytes:
            raise IngestStopped(
                f"the feed is {expected_size} bytes at {config.source_ref}, over the "
                f"{limits.feed_bytes} ceiling"
            )
        response = client.get(url, accept="application/vnd.github.raw",
                              max_bytes=limits.feed_bytes, reject_binary=True)
    except FetchError as error:
        if error.category not in ("rate_limit", "forbidden"):
            raise
        fallback = raw_url(config.source_repo, config.source_ref, config.source_path)
        response = client.get(fallback, accept="text/plain", max_bytes=limits.feed_bytes,
                              reject_binary=True)
        return Snapshot(response.body, config.source_identity, "github", "raw",
                        verification="unverified")

    body = response.body
    if isinstance(expected_size, int) and len(body) != expected_size:
        raise IngestStopped(
            f"the feed arrived as {len(body)} bytes where the Contents API reports "
            f"{expected_size}: truncated or altered, nothing imported"
        )
    if isinstance(expected_sha, str) and git_blob_sha(body) != expected_sha:
        raise IngestStopped(
            f"the feed's git blob hash does not match the {expected_sha[:12]} the Contents "
            f"API reports: nothing imported"
        )
    return Snapshot(
        body, config.source_identity, "github", "contents-api",
        etag=response.headers.get("etag"),
        blob_sha=expected_sha if isinstance(expected_sha, str) else None,
        upstream_commit=_upstream_commit(config, client),
        verification="blob-sha" if isinstance(expected_sha, str) else "size-only",
    )


def _upstream_commit(config: Config, client: Client) -> str | None:
    """The commit that last touched the feed at the configured ref, for a
    reproducible comparison later. Best effort: one request, and a failure costs
    only the provenance, never the import."""
    owner, name = config.source_repo.split("/", 1)
    try:
        items = client.get(
            api_url("repos", owner, name, "commits", path=config.source_path,
                    sha=config.source_ref, per_page=1),
            max_bytes=256 * 1024,
        ).json()
    except FetchError:
        return None
    if isinstance(items, list) and items and isinstance(items[0], dict):
        sha = items[0].get("sha")
        return sha if isinstance(sha, str) else None
    return None


# --- parsing ---------------------------------------------------------------

def parse(snapshot: Snapshot, *, quarantine_cap: int, excerpt_chars: int) -> ImportResult:
    """Split the snapshot into repository records, other records, and damage.

    Tolerant about shape — a record with a name and nothing else is valid input —
    and strict about the name, because the name becomes part of an API URL.
    """
    result = ImportResult(ingestion_id=0, status="parsed", content_hash=snapshot.content_hash,
                          transport=snapshot.transport)
    try:
        text = snapshot.body.decode("utf-8")
    except UnicodeDecodeError as error:
        raise IngestStopped(f"feed is not UTF-8: {error}") from error

    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        result.lines_total += 1
        try:
            record = loads(stripped)
        except ValueError as error:
            result.malformed += 1
            if len(result.quarantine) < quarantine_cap:
                result.quarantine.append(
                    f"line {number}: {error}: {truncate(stripped, 200)}"
                )
            continue
        if not isinstance(record, dict):
            result.malformed += 1
            if len(result.quarantine) < quarantine_cap:
                result.quarantine.append(f"line {number}: not an object")
            continue
        if record.get("kind") != "repo":
            result.other_records += 1
            continue

        raw_name = record.get("repo") or record.get("full_name") or record.get("name")
        try:
            key = canonical(raw_name or "")
        except InvalidName as error:
            result.invalid_names += 1
            if len(result.quarantine) < quarantine_cap:
                result.quarantine.append(f"line {number}: {error}")
            continue
        result.repo_records += 1
        hints = source_hints(record, excerpt_chars)
        shape = record_shape(record, hints)
        result.shapes[shape] += 1
        result.records.append((key, raw_name, _provenance(record, hints), hints, shape))

    if result.lines_total and result.repo_records == 0:
        raise IngestStopped(
            f"{result.lines_total} lines arrived and none yielded a valid repository "
            f"({result.malformed} malformed, {result.invalid_names} invalid names, "
            f"{result.other_records} non-repository). Stopping for inspection rather than "
            f"recording an empty feed as a successful one."
        )
    return result


# --- source hints ----------------------------------------------------------
#
# Scout writes two shapes of repository record. Modern ones carry `latest` — the
# description, stars, push date, licence, matched terms and sometimes topics and
# README size Scout saw when it last looked — beside `sources`, `source_urls`
# and first/last-seen times. The retracted initial batch carries `title_only:
# true`, an issue number and nothing else. Older fixtures and third-party feeds
# may put a description or stars at the top level; that is accepted as a
# labelled fallback and never preferred over `latest`.
#
# All of it is a hint: another program's observation of unknown age. None of it
# becomes a measured fact, feeds a gate, or enters the atlas's score. It may
# change which repository gets fetched first, and nothing else.

HINT_LIST_CAP = 20
HINT_ITEM_CHARS = 80
HINT_URL_CHARS = 300


def _int_or_none(value) -> int | None:
    # `bool` is an `int` in Python; a `true` in the stars field is not a count.
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _str_or_none(value, cap: int) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return truncate(value.strip(), cap)


def _str_list(value, cap_items: int, cap_chars: int) -> list[str] | None:
    """None when the field is absent or not a list; a list — possibly empty — when
    it was present. The difference is whether anything was observed at all."""
    if not isinstance(value, list):
        return None
    out = [truncate(item.strip(), cap_chars) for item in value
           if isinstance(item, str) and item.strip()]
    return out[:cap_items]


def usable_latest(record: dict) -> dict | None:
    latest = record.get("latest")
    if not isinstance(latest, dict):
        return None
    recognised = {"description", "stars", "pushed_at", "topics", "readme_bytes",
                  "html_url", "matched_terms", "license", "source"}
    return latest if recognised & set(latest) else None


def source_hints(record: dict, excerpt_chars: int) -> dict:
    """Validated, bounded, labelled. Missing stays None; a measured zero stays 0."""
    latest = usable_latest(record)
    top_level = latest is None and any(
        key in record for key in ("description", "stars", "pushed_at", "topics")
    )
    origin = latest if latest is not None else record
    hints = {
        "title_only": record.get("title_only") if isinstance(record.get("title_only"), bool) else None,
        "has_latest": latest is not None,
        "origin": "latest" if latest is not None else ("top_level" if top_level else None),
        "description": _str_or_none(origin.get("description"), excerpt_chars),
        "stars": _int_or_none(origin.get("stars")),
        "pushed_at": _str_or_none(origin.get("pushed_at"), 40),
        "topics": _str_list(origin.get("topics"), HINT_LIST_CAP, HINT_ITEM_CHARS),
        # A size Scout cached when it looked; not a fetched artifact, and not
        # proof that a README exists now.
        "readme_bytes": _int_or_none(origin.get("readme_bytes")),
        "license": _str_or_none(origin.get("license"), 40),
        "matched_terms": _str_list(origin.get("matched_terms"), HINT_LIST_CAP, HINT_ITEM_CHARS),
        "sources": _str_list(record.get("sources"), 10, 40),
        "source_urls": _str_list(record.get("source_urls"), 10, HINT_URL_CHARS),
        "status": _str_or_none(record.get("status"), 20),
        "issue_number": _int_or_none(record.get("issue_number")),
        "upstream_first_seen_at": _str_or_none(record.get("first_seen_at"), 40),
        "upstream_last_seen_at": _str_or_none(record.get("last_seen_at"), 40),
    }
    # Scout computes an A/B/C tier and a score at runtime and, at the pin this
    # was written against, does not export them. If a later feed does, they are
    # kept as versioned upstream hints — named apart from the atlas's score and
    # read by no gate.
    for key in ("tier", "score", "score_version", "scoring_version"):
        value = record.get(key, (latest or {}).get(key))
        if isinstance(value, (str, int, float)) and not isinstance(value, bool):
            hints[f"upstream_{key}"] = value if not isinstance(value, str) else truncate(value, 40)
    return hints


def record_shape(record: dict, hints: dict) -> str:
    if hints["has_latest"]:
        return "modern"
    if hints["title_only"] is True:
        return "legacy"
    return "minimal"


# Fields that make two observations different. Excluded on purpose: the local
# ingestion time, the line number, and Scout's own last-seen time, which moves
# every time Scout rewrites its index without anything about the repository
# changing.
FINGERPRINT_FIELDS = (
    "title_only", "has_latest", "description", "stars", "pushed_at", "topics",
    "readme_bytes", "license", "matched_terms", "sources", "source_urls", "status",
    "issue_number", "upstream_first_seen_at",
)


def fingerprint(hints: dict) -> str:
    return sha256_hex(dumps({key: hints.get(key) for key in FINGERPRINT_FIELDS}).encode())[:16]


def _provenance(record: dict, hints: dict) -> dict:
    """One bounded observation of what Scout said. `author` is deliberately
    absent: in Scout's Reddit records it is the person who wrote the post, never
    the repository's owner."""
    return {
        "fingerprint": fingerprint(hints),
        "observed_at": iso(utc_now()),
        "status": hints["status"],
        "issue_number": hints["issue_number"],
        "title_only": hints["title_only"],
        "has_latest": hints["has_latest"],
        "sources": hints["sources"],
        "upstream_first_seen_at": hints["upstream_first_seen_at"],
        "hint_stars": hints["stars"],
        "hint_pushed_at": hints["pushed_at"],
    }


# --- the legacy hold --------------------------------------------------------
#
# The retracted initial batch (Scout issue 1256) arrives as `title_only: true`
# with no payload. Those identities are imported and kept, and held out of the
# ordinary daily metadata and inspection budgets. The hold is about the source,
# not the project: it is not a rejection, it is separate from `analysis_status`,
# and a policy-version change does not lift it — only a usable payload in a
# later snapshot, or the maintainer, does.

HOLD = "legacy_title_only"
RELEASED = "released"


def apply_source_hold(connection: sqlite3.Connection, candidate_id: int, shape: str,
                      now: str) -> str | None:
    """Returns `held`, `cleared`, a disposition name when the hold was considered
    and not applied, or None when nothing changed."""
    row = connection.execute(
        "SELECT c.source_hold, c.source_hold_disposition, c.analysis_status, c.latest_assessment, "
        "       a.classifier_version "
        "FROM candidate c LEFT JOIN assessment a ON a.id = c.latest_assessment WHERE c.id = ?",
        (candidate_id,),
    ).fetchone()
    hold = row["source_hold"]

    if shape == "modern":
        if hold == HOLD:
            _set_hold(connection, candidate_id, None, "cleared_by_payload", now)
            return "cleared"
        return None

    if shape != "legacy" or hold in (HOLD, RELEASED):
        return None
    if row["source_hold_disposition"] in ("analysis_precedence", "manually_assessed"):
        return None

    # Precedence: an analysis already under way or finished, or a person's own
    # assessment, is never overwritten by a note about where the name came from.
    if row["analysis_status"] in ("selected", "running", "accepted", "rejected", "error", "cancelled"):
        _set_hold(connection, candidate_id, None, "analysis_precedence", now)
        return "analysis_precedence"
    if (row["classifier_version"] or "").startswith("manual"):
        _set_hold(connection, candidate_id, None, "manually_assessed", now)
        return "manually_assessed"

    # Evidence already collected is kept, and the candidate keeps its triage
    # status; the hold only stops future automatic spending on it.
    disposition = "assessed_before_hold" if row["latest_assessment"] is not None else "unassessed"
    _set_hold(connection, candidate_id, HOLD, disposition, now)
    return "held"


def _set_hold(connection: sqlite3.Connection, candidate_id: int, hold: str | None,
              disposition: str, now: str) -> None:
    connection.execute(
        "UPDATE candidate SET source_hold = ?, source_hold_disposition = ?, "
        "source_hold_changed_at = ? WHERE id = ?",
        (hold, disposition, now, candidate_id),
    )


def release_holds(connection: sqlite3.Connection, names: list[str] | None = None,
                  batch: int | None = None, cap: int = 50) -> list[str]:
    """Deliberately revisit legacy identities: by name, or a bounded batch.

    A released identity is not held again by a later import, so revisiting is a
    decision made once, not a daily sweep of the whole legacy set. The batch is
    ordered by what the hints say — which for a title-only record is almost
    nothing — then by first sighting, so the choice is reproducible.
    """
    from identity import canonical, find
    now = iso(utc_now())
    released: list[str] = []
    with transaction(connection):
        if names:
            for name in names[:cap]:
                row = find(connection, name=canonical(name))
                if row is None or row["source_hold"] != HOLD:
                    continue
                _set_hold(connection, int(row["id"]), RELEASED, "released_by_maintainer", now)
                released.append(row["display_name"])
        elif batch:
            rows = connection.execute(
                "SELECT id, display_name FROM candidate WHERE source_hold = ? "
                "ORDER BY first_seen_at, canonical_name LIMIT ?",
                (HOLD, max(0, min(batch, cap))),
            ).fetchall()
            for row in rows:
                _set_hold(connection, int(row["id"]), RELEASED, "released_by_maintainer", now)
                released.append(row["display_name"])
    return released


# --- importing -------------------------------------------------------------

def run(config: Config, connection: sqlite3.Connection, client: Client | None) -> ImportResult:
    """Fetch, parse, validate, and only then open a write transaction.

    A failure anywhere before the transaction records an `ingestion` row with
    `status = 'failed'` and leaves every candidate, assessment and selection
    exactly as it was.
    """
    limits = config.limits
    now = iso(utc_now())
    try:
        snapshot = fetch(config, client)
        parsed = parse(snapshot, quarantine_cap=limits.quarantine_lines,
                       excerpt_chars=limits.excerpt_chars)
    except (FetchError, IngestStopped) as error:
        message = f"{type(error).__name__}: {error}"
        with transaction(connection):
            cursor = connection.execute(
                "INSERT INTO ingestion(source_kind, source_identity, transport, fetched_at, "
                "status, failure) VALUES (?, ?, ?, ?, 'failed', ?)",
                (config.source_kind, config.source_identity, None, now, message),
            )
        return ImportResult(int(cursor.lastrowid), "failed", failure=message)

    previous = connection.execute(
        "SELECT content_hash FROM ingestion WHERE status = 'complete' AND source_identity = ? "
        "ORDER BY id DESC LIMIT 1",
        (config.source_identity,),
    ).fetchone()
    unchanged = previous is not None and previous["content_hash"] == snapshot.content_hash

    with transaction(connection):
        for key, raw_name, provenance, hints, shape in parsed.records:
            candidate_id, is_new, added = upsert(
                connection, raw_name, provenance, hints=hints,
                hints_observed_at=hints.get("upstream_last_seen_at") or hints.get("upstream_first_seen_at"),
            )
            parsed.observations_added += int(added)
            if is_new:
                parsed.imported_new += 1
            else:
                parsed.duplicates += 1
            outcome = apply_source_hold(connection, candidate_id, shape, now)
            if outcome == "held":
                parsed.holds_applied += 1
            elif outcome == "cleared":
                parsed.holds_cleared += 1
            elif outcome:
                parsed.dispositions[outcome] = parsed.dispositions.get(outcome, 0) + 1

        cursor = connection.execute(
            "INSERT INTO ingestion(source_kind, source_identity, transport, fetched_at, etag, "
            "blob_sha, content_hash, content_bytes, status, lines_total, repo_records, "
            "other_records, malformed, imported_new, duplicates, quarantine, upstream_commit, "
            "verification, source_shapes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'complete', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                config.source_kind, config.source_identity, snapshot.transport, now,
                snapshot.etag, snapshot.blob_sha,
                snapshot.content_hash, len(snapshot.body), parsed.lines_total,
                parsed.repo_records, parsed.other_records,
                parsed.malformed + parsed.invalid_names, parsed.imported_new, parsed.duplicates,
                dumps(parsed.quarantine) if parsed.quarantine else None,
                snapshot.upstream_commit, snapshot.verification, dumps(parsed.shapes),
            ),
        )
    parsed.upstream_commit = snapshot.upstream_commit
    parsed.verification = snapshot.verification
    parsed.ingestion_id = int(cursor.lastrowid)
    parsed.status = "complete"
    parsed.unchanged = unchanged
    return parsed

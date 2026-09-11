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
    # (canonical_name, name as the feed wrote it, provenance) for each valid record
    records: list[tuple[str, str, dict]] = field(default_factory=list)


# --- fetching --------------------------------------------------------------

def fetch(config: Config, client: Client | None) -> Snapshot:
    """Get the configured feed. A local file is an explicit choice, not a fallback.

    Two transports reach the same configured `repo@ref:path` — the Contents API,
    which carries an ETag and the blob sha, and raw.githubusercontent.com, which
    does not. If the API is rate-limited the raw transport is tried for the same
    identity. That is a different route to the same file; it is not a different
    source, and there is deliberately no route to anyone's fork.
    """
    limits = config.limits
    if config.source_kind == "file":
        path = Path(config.source_file).expanduser() if config.source_file else None
        if path is None or not path.is_file():
            raise IngestStopped(f"configured local source {path} does not exist")
        size = path.stat().st_size
        if size > limits.feed_bytes:
            raise IngestStopped(f"{path} is {size} bytes, over the {limits.feed_bytes} ceiling")
        return Snapshot(path.read_bytes(), f"file:{path}", "file", "file")

    if client is None:
        raise IngestStopped("no HTTP client available for a github source")

    owner, name = config.source_repo.split("/", 1)
    url = api_url("repos", owner, name, "contents", *config.source_path.split("/"),
                  ref=config.source_ref)
    try:
        response = client.get(url, accept="application/vnd.github.raw",
                              max_bytes=limits.feed_bytes, reject_binary=True)
        return Snapshot(
            response.body, config.source_identity, "github", "contents-api",
            etag=response.headers.get("etag"),
            blob_sha=response.headers.get("x-github-blob-sha"),
        )
    except FetchError as error:
        if error.category not in ("rate_limit", "forbidden"):
            raise
        fallback = raw_url(config.source_repo, config.source_ref, config.source_path)
        response = client.get(fallback, accept="text/plain", max_bytes=limits.feed_bytes,
                              reject_binary=True)
        return Snapshot(response.body, config.source_identity, "github", "raw")


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
        result.records.append((key, raw_name, _provenance(record, number, excerpt_chars)))

    if result.lines_total and result.repo_records == 0:
        raise IngestStopped(
            f"{result.lines_total} lines arrived and none yielded a valid repository "
            f"({result.malformed} malformed, {result.invalid_names} invalid names, "
            f"{result.other_records} non-repository). Stopping for inspection rather than "
            f"recording an empty feed as a successful one."
        )
    return result


def _provenance(record: dict, line_number: int, excerpt_chars: int) -> dict:
    """What Scout said, kept as a hint and labelled as one.

    Stars and descriptions from the feed are *not* copied into measured facts.
    They are an observation of unknown age made by another program; the metadata
    stage fetches its own. `author` is deliberately absent: in Scout's Reddit
    records that is the person who wrote the post.
    """
    latest = record.get("latest") if isinstance(record.get("latest"), dict) else None
    return {
        "observed_at": iso(utc_now()),
        "line": line_number,
        "status": record.get("status"),
        "issue_number": record.get("issue_number"),
        "source": record.get("source") or record.get("origin"),
        "post_id": record.get("post_id") or record.get("id"),
        "hint_description": truncate(record.get("description"), excerpt_chars),
        "hint_stars": latest.get("stars") if latest else record.get("stars"),
        "hint_pushed_at": latest.get("pushed_at") if latest else None,
    }


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
        for key, raw_name, provenance in parsed.records:
            _, is_new = upsert(connection, raw_name, provenance)
            if is_new:
                parsed.imported_new += 1
            else:
                parsed.duplicates += 1

        cursor = connection.execute(
            "INSERT INTO ingestion(source_kind, source_identity, transport, fetched_at, etag, "
            "blob_sha, content_hash, content_bytes, status, lines_total, repo_records, "
            "other_records, malformed, imported_new, duplicates, quarantine) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'complete', ?, ?, ?, ?, ?, ?, ?)",
            (
                config.source_kind, config.source_identity, snapshot.transport, now,
                snapshot.etag, snapshot.blob_sha,
                snapshot.content_hash, len(snapshot.body), parsed.lines_total,
                parsed.repo_records, parsed.other_records,
                parsed.malformed + parsed.invalid_names, parsed.imported_new, parsed.duplicates,
                dumps(parsed.quarantine) if parsed.quarantine else None,
            ),
        )
    parsed.ingestion_id = int(cursor.lastrowid)
    parsed.status = "complete"
    parsed.unchanged = unchanged
    return parsed

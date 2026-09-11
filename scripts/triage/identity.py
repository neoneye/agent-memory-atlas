"""Repository identity: validate a name, then stop trusting the name.

Scout's records carry `owner/repo`. That is the only key available at import,
so it bootstraps identity — but it is not identity. A project that is renamed or
transferred keeps its decision, and a name that is later reused by a different
repository is a different project. GitHub's numeric repository id is what makes
both of those true, and it arrives during metadata enrichment, not at import.
"""

from __future__ import annotations

import re
import sqlite3
from typing import Iterable

from util import dumps, iso, loads, utc_now

# GitHub's own rules: owner is alphanumeric with single hyphens, repo adds dot
# and underscore. Anything else is a malformed record, not a candidate — the
# names in this feed are interpolated into API URLs later, and that is exactly
# the place where a lax pattern turns a feed entry into a request somewhere else.
_OWNER = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")
_REPO = re.compile(r"^[A-Za-z0-9._-]{1,100}$")


class InvalidName(ValueError):
    pass


def parse(raw: str) -> tuple[str, str]:
    """`owner/repo` in, `(owner, repo)` out, or `InvalidName`.

    A URL is accepted only when it is a github.com repository URL; anything else
    is refused rather than guessed at, including `.git` suffixes and trailing
    path segments that would silently change which repository is fetched.
    """
    if not isinstance(raw, str):
        raise InvalidName(f"not a string: {raw!r}")
    text = raw.strip()
    if not text:
        raise InvalidName("empty name")
    for prefix in ("https://github.com/", "http://github.com/", "github.com/"):
        if text.lower().startswith(prefix):
            text = text[len(prefix):]
            break
    text = text.removesuffix(".git").strip("/")
    parts = text.split("/")
    if len(parts) != 2:
        raise InvalidName(f"expected owner/repo, got {raw!r}")
    owner, repo = parts
    if not _OWNER.match(owner):
        raise InvalidName(f"invalid owner in {raw!r}")
    if not _REPO.match(repo) or repo in {".", ".."}:
        raise InvalidName(f"invalid repository in {raw!r}")
    return owner, repo


def canonical(raw: str) -> str:
    """Case-folded `owner/repo`. GitHub names are case-insensitive for lookup
    but case-preserving for display, so the fold is the key and the original is
    kept alongside it."""
    owner, repo = parse(raw)
    return f"{owner.lower()}/{repo.lower()}"


def display(raw: str) -> str:
    owner, repo = parse(raw)
    return f"{owner}/{repo}"


# --- candidate rows --------------------------------------------------------

def find(connection: sqlite3.Connection, *, name: str | None = None,
         repo_id: int | None = None) -> sqlite3.Row | None:
    """Repository id first, then any name the project has been known by."""
    if repo_id is not None:
        row = connection.execute(
            "SELECT * FROM candidate WHERE github_repo_id = ?", (repo_id,)
        ).fetchone()
        if row is not None:
            return row
    if name is None:
        return None
    key = canonical(name)
    row = connection.execute(
        "SELECT c.* FROM candidate c JOIN alias a ON a.candidate_id = c.id "
        "WHERE a.canonical_name = ?",
        (key,),
    ).fetchone()
    if row is not None:
        return row
    return connection.execute(
        "SELECT * FROM candidate WHERE canonical_name = ?", (key,)
    ).fetchone()


OBSERVATION_CAP = 20


def upsert(connection: sqlite3.Connection, name: str, provenance: dict, *,
           hints: dict | None = None,
           hints_observed_at: str | None = None) -> tuple[int, bool, bool]:
    """Insert or touch a candidate by name. Returns `(candidate_id, is_new, added)`.

    Observations accumulate only when something meaningful changed. A repeated
    or reordered snapshot produces the same fingerprint as the observation it
    repeats, and touches `last_seen_at` — the local ingestion time — instead of
    appending a copy. A second Reddit post, a new star count or a new push date
    is a different fingerprint and is kept, within a bounded list.

    `hints` replace the stored hints: they are the current snapshot's view, and
    the history of what Scout said lives in the bounded observations.
    """
    key = canonical(name)
    now = iso(utc_now())
    row = find(connection, name=key)
    hints_json = dumps(hints) if hints is not None else None
    if row is None:
        cursor = connection.execute(
            "INSERT INTO candidate(canonical_name, display_name, first_seen_at, last_seen_at, "
            "provenance, hints, hints_observed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (key, display(name), now, now, dumps({"observations": [provenance]}),
             hints_json or "{}", hints_observed_at),
        )
        candidate_id = int(cursor.lastrowid)
        connection.execute(
            "INSERT OR IGNORE INTO alias(canonical_name, candidate_id, first_seen_at, current) "
            "VALUES (?, ?, ?, 1)",
            (key, candidate_id, now),
        )
        return candidate_id, True, True

    candidate_id = int(row["id"])
    stored = loads(row["provenance"] or "{}")
    observations = stored.get("observations", [])
    fp = provenance.get("fingerprint")
    known = {item.get("fingerprint") for item in observations if isinstance(item, dict)}
    added = False
    if fp is None:
        # A v1 caller without fingerprints: fall back to value equality.
        if provenance not in observations:
            observations.append(provenance)
            added = True
    elif fp not in known:
        observations.append(provenance)
        added = True
    stored["observations"] = observations[-OBSERVATION_CAP:]
    connection.execute(
        "UPDATE candidate SET last_seen_at = ?, provenance = ?, "
        "hints = COALESCE(?, hints), hints_observed_at = COALESCE(?, hints_observed_at) "
        "WHERE id = ?",
        (now, dumps(stored), hints_json, hints_observed_at, candidate_id),
    )
    return candidate_id, False, added


def bind_repo_id(connection: sqlite3.Connection, candidate_id: int, repo_id: int,
                 full_name: str) -> str:
    """Attach the numeric id, and handle the three things that can mean.

    Returns one of `bound`, `renamed`, or `reused`.

    `reused` is the interesting one: the name we imported now resolves to a
    repository id already held by a *different* candidate. That is a name
    handed on to a new project, and the decision recorded against the old
    project stays with the old project.
    """
    key = canonical(full_name)
    now = iso(utc_now())
    existing = connection.execute(
        "SELECT * FROM candidate WHERE github_repo_id = ?", (repo_id,)
    ).fetchone()

    if existing is not None and int(existing["id"]) != candidate_id:
        # The name we followed belongs to the repository that already holds this
        # id. Point the alias there and leave the other candidate untouched.
        connection.execute(
            "INSERT INTO alias(canonical_name, candidate_id, first_seen_at, current) "
            "VALUES (?, ?, ?, 0) ON CONFLICT(canonical_name) DO UPDATE SET candidate_id = excluded.candidate_id",
            (key, int(existing["id"]), now),
        )
        return "reused"

    row = connection.execute("SELECT * FROM candidate WHERE id = ?", (candidate_id,)).fetchone()
    outcome = "bound"
    if row["canonical_name"] != key:
        outcome = "renamed"
        connection.execute("UPDATE alias SET current = 0 WHERE candidate_id = ?", (candidate_id,))
        connection.execute(
            "INSERT INTO alias(canonical_name, candidate_id, first_seen_at, current) "
            "VALUES (?, ?, ?, 1) ON CONFLICT(canonical_name) DO UPDATE "
            "SET candidate_id = excluded.candidate_id, current = 1",
            (key, candidate_id, now),
        )
    connection.execute(
        "UPDATE candidate SET github_repo_id = ?, canonical_name = ?, display_name = ? WHERE id = ?",
        (repo_id, key, display(full_name), candidate_id),
    )
    connection.execute(
        "INSERT OR IGNORE INTO alias(canonical_name, candidate_id, first_seen_at, current) "
        "VALUES (?, ?, ?, 1)",
        (key, candidate_id, now),
    )
    return outcome


def aliases(connection: sqlite3.Connection, candidate_id: int) -> list[str]:
    return [
        row["canonical_name"]
        for row in connection.execute(
            "SELECT canonical_name FROM alias WHERE candidate_id = ? ORDER BY first_seen_at",
            (candidate_id,),
        )
    ]

"""Claims, leases, fencing tokens, and recording what the analysis found.

The full atlas analysis is a separate program. This is the contract between
them, and it has three jobs.

**A claim is a lease, not a handoff.** A worker claims a selection and gets an
attempt id and an expiry. A retry continues the same selection under a new
attempt — it does not consume another day's admission, because the admission was
spent when the candidate was selected.

**An expired lease is not an invitation to run blind.** Reclaiming supersedes
the previous attempt explicitly and increments a fencing token. The superseded
worker can still submit — it may have finished while its lease lapsed — and that
submission is recorded as stale rather than allowed to overwrite the attempt
that replaced it.

**A technical error is not a quality rejection.** A model timeout, a network
failure or a crashed clone comes back as `error` with a retryability flag, and
the candidate returns to the pool. Recording that as `rejected` would mean the
atlas had judged a project it never read.
"""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from typing import Any

from config import Config
from db import transaction
from util import dumps, iso, parse_iso, plus, truncate, utc_now

TERMINAL = {"accepted", "rejected", "cancelled"}
RESULT_STATUSES = {"accepted", "rejected", "error", "cancelled"}


class ClaimRefused(RuntimeError):
    pass


class ResultRefused(RuntimeError):
    pass


@dataclass
class Claim:
    attempt_id: str
    selection_id: str
    repo: str
    commit: str | None
    fence: int
    lease_expires: str
    reclaimed_from: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "attempt_id": self.attempt_id,
            "selection_id": self.selection_id,
            "repo": self.repo,
            "url": f"https://github.com/{self.repo}",
            "selected_commit": self.commit,
            "fence": self.fence,
            "lease_expires": self.lease_expires,
            "reclaimed_from": self.reclaimed_from,
            "cleanup_contract": (
                "the analyser owns any checkout it makes and deletes it on completion, "
                "including after an error, and recovers its own abandoned workspaces on its "
                "next start. Triage never clones and does not clean another program's directories."
            ),
        }


def _selection(connection: sqlite3.Connection, selection_uuid: str) -> sqlite3.Row:
    row = connection.execute(
        "SELECT s.*, c.display_name FROM selection s JOIN candidate c ON c.id = s.candidate_id "
        "WHERE s.uuid = ?",
        (selection_uuid,),
    ).fetchone()
    if row is None:
        raise ClaimRefused(f"no selection {selection_uuid}")
    return row


def claim(connection: sqlite3.Connection, config: Config, selection_uuid: str,
          worker: str | None, *, force: bool = False) -> Claim:
    row = _selection(connection, selection_uuid)
    if row["state"] != "open":
        raise ClaimRefused(f"selection {selection_uuid} is {row['state']}, not open")

    now = utc_now()
    with transaction(connection):
        live = connection.execute(
            "SELECT * FROM attempt WHERE selection_id = ? AND status = 'running' "
            "ORDER BY fence DESC LIMIT 1",
            (row["id"],),
        ).fetchone()
        reclaimed = None
        if live is not None:
            expired = parse_iso(live["lease_expires"]) <= now
            if not expired and not force:
                raise ClaimRefused(
                    f"attempt {live['uuid']} holds a lease on this selection until "
                    f"{live['lease_expires']} (worker {live['worker']}). Reconcile with that "
                    f"worker before reclaiming; --force records the reclaim explicitly."
                )
            connection.execute(
                "UPDATE attempt SET status = 'superseded', finished_at = ?, result = ? WHERE id = ?",
                (iso(now),
                 dumps({"superseded_because": "lease expired" if expired else "forced reclaim",
                        "reconciled_at": iso(now)}),
                 live["id"]),
            )
            reclaimed = live["uuid"]

        highest = connection.execute(
            "SELECT COALESCE(MAX(fence), 0) AS f FROM attempt WHERE selection_id = ?", (row["id"],)
        ).fetchone()["f"]
        fence = int(highest) + 1
        attempt_uuid = str(uuid.uuid4())
        expires = iso(plus(now, seconds=config.lease_seconds))
        connection.execute(
            "INSERT INTO attempt(uuid, selection_id, fence, worker, claimed_at, lease_expires, status) "
            "VALUES (?, ?, ?, ?, ?, ?, 'running')",
            (attempt_uuid, row["id"], fence, truncate(worker, 200), iso(now), expires),
        )
        connection.execute(
            "UPDATE candidate SET analysis_status = 'running' WHERE id = ?", (row["candidate_id"],)
        )
    return Claim(attempt_uuid, selection_uuid, row["display_name"], row["selected_commit"],
                 fence, expires, reclaimed)


def _record_stale(connection: sqlite3.Connection, attempt_uuid: str | None, reason: str,
                  payload: dict) -> None:
    connection.execute(
        "INSERT INTO stale_submission(attempt_uuid, received_at, reason, payload) "
        "VALUES (?, ?, ?, ?)",
        (attempt_uuid, iso(utc_now()), reason, truncate(dumps(payload), 4000)),
    )


def record(connection: sqlite3.Connection, attempt_uuid: str, payload: dict[str, Any]) -> dict:
    """Accept, reject, error or cancel one attempt. Idempotent for a repeat of
    the same submission; anything conflicting is stored as stale and refused."""
    status = payload.get("status")
    if status not in RESULT_STATUSES:
        raise ResultRefused(f"status must be one of {sorted(RESULT_STATUSES)}, got {status!r}")

    row = connection.execute(
        "SELECT a.*, s.uuid AS selection_uuid, s.candidate_id, s.id AS sid "
        "FROM attempt a JOIN selection s ON s.id = a.selection_id WHERE a.uuid = ?",
        (attempt_uuid,),
    ).fetchone()
    if row is None:
        with transaction(connection):
            _record_stale(connection, attempt_uuid, "no such attempt", payload)
        raise ResultRefused(f"no attempt {attempt_uuid}")

    if status in ("accepted", "rejected") and not payload.get("analysed_commit"):
        raise ResultRefused(
            f"a {status} result must carry the commit that was actually analysed; it can "
            f"differ from the selected commit and the difference is the point"
        )
    if status == "accepted" and not payload.get("report"):
        raise ResultRefused("an accepted result must name the report path or URL")
    if status == "rejected" and not payload.get("reason"):
        raise ResultRefused("a rejected result must carry a structured reason")
    if status == "error" and "retryable" not in payload:
        raise ResultRefused(
            "an error result must say whether it is retryable. A network or model failure is "
            "not a judgement about the project and must not be recorded as one."
        )

    stored = payload.copy()
    stored["recorded_at"] = iso(utc_now())

    if row["status"] != "running":
        existing = row["result"]
        same = existing and _comparable(existing) == _comparable(dumps(stored))
        with transaction(connection):
            _record_stale(
                connection, attempt_uuid,
                "idempotent repeat" if same else f"attempt already {row['status']}", payload,
            )
        if same:
            return {"attempt_id": attempt_uuid, "status": row["status"], "idempotent": True}
        raise ResultRefused(
            f"attempt {attempt_uuid} is already {row['status']}; the submission was recorded "
            f"as stale and the current result is unchanged"
        )

    newer = connection.execute(
        "SELECT uuid, fence FROM attempt WHERE selection_id = ? AND fence > ? "
        "ORDER BY fence DESC LIMIT 1",
        (row["sid"], row["fence"]),
    ).fetchone()
    if newer is not None:
        with transaction(connection):
            _record_stale(
                connection, attempt_uuid,
                f"fence {row['fence']} superseded by {newer['fence']} ({newer['uuid']})", payload,
            )
        raise ResultRefused(
            f"attempt {attempt_uuid} carries fence {row['fence']} and attempt {newer['uuid']} "
            f"holds {newer['fence']}. The later attempt owns this selection; the submission was "
            f"recorded for diagnosis and changed nothing."
        )

    with transaction(connection):
        connection.execute(
            "UPDATE attempt SET status = ?, finished_at = ?, analysed_commit = ?, result = ? "
            "WHERE id = ?",
            (status, iso(utc_now()), payload.get("analysed_commit"), dumps(stored), row["id"]),
        )
        if status in TERMINAL:
            connection.execute(
                "UPDATE selection SET state = ? WHERE id = ?",
                ("cancelled" if status == "cancelled" else "done", row["sid"]),
            )
            connection.execute(
                "UPDATE candidate SET analysis_status = ? WHERE id = ?", (status, row["candidate_id"])
            )
            if status == "rejected":
                connection.execute(
                    "UPDATE candidate SET triage_reason = ?, next_assessment_at = ? WHERE id = ?",
                    (
                        truncate(f"atlas analysis rejected at {payload.get('analysed_commit')}: "
                                 f"{payload.get('reason')}", 900),
                        payload.get("reassess_after"),
                        row["candidate_id"],
                    ),
                )
        else:
            # A technical error returns the candidate to the pool with the
            # selection left open, so a retry continues the same admission.
            connection.execute(
                "UPDATE candidate SET analysis_status = 'selected' WHERE id = ?",
                (row["candidate_id"],),
            )
    return {"attempt_id": attempt_uuid, "status": status,
            "selection": row["selection_uuid"], "idempotent": False}


def _comparable(blob: str) -> str:
    from util import loads
    try:
        payload = loads(blob)
    except ValueError:
        return blob
    payload.pop("recorded_at", None)
    return dumps(payload)


def outstanding(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT s.uuid AS selection_id, s.day, s.state, c.display_name, s.selected_commit, "
        "       a.uuid AS attempt_id, a.status AS attempt_status, a.lease_expires, a.worker "
        "FROM selection s JOIN candidate c ON c.id = s.candidate_id "
        "LEFT JOIN attempt a ON a.selection_id = s.id AND a.status = 'running' "
        "WHERE s.state = 'open' ORDER BY s.day, s.slot"
    ).fetchall()
    return [dict(row) for row in rows]

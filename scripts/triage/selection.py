"""Turning eligible candidates into a frozen daily shortlist.

Named `selection` rather than `select` because this directory is on `sys.path`
and `select` is a standard-library module.

Two ceilings, both real. Twenty new admissions per civil day in the configured
timezone, and twenty outstanding analyses across all dates — the second is what
stops twenty a day from becoming a hundred unfinished readings by Friday.
Available slots are the smaller of the two remainders, and fewer than twenty is
an ordinary result rather than a failure.

A day is *frozen* once selected. Rerunning regenerates the same list from the
committed transaction instead of selecting again, which is what makes the daily
report reproducible and what stops a crash between the transaction and the file
from spending a second day's allowance. Displaying an old day never admits
anything: only the current configured day can select.

A rejected or cancelled selection is not backfilled the same day. The allowance
is a bound on what is *started*, and quietly topping it up after a rejection
turns twenty into however many rejections arrive.
"""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass, field
from typing import Any

import atlas
from assess import duplicate_reason
from config import Config
from db import transaction
from util import civil_day, dumps, iso, loads, parse_iso, utc_now


@dataclass
class Capacity:
    day: str
    tz: str
    daily_limit: int
    outstanding_limit: int
    admitted_today: int
    outstanding: int

    @property
    def remaining_daily(self) -> int:
        return max(self.daily_limit - self.admitted_today, 0)

    @property
    def remaining_outstanding(self) -> int:
        return max(self.outstanding_limit - self.outstanding, 0)

    @property
    def slots(self) -> int:
        return min(self.remaining_daily, self.remaining_outstanding)

    def as_dict(self) -> dict[str, Any]:
        return {
            "day": self.day, "timezone": self.tz,
            "daily_limit": self.daily_limit, "admitted_today": self.admitted_today,
            "outstanding_limit": self.outstanding_limit, "outstanding": self.outstanding,
            "slots_available": self.slots,
        }


@dataclass
class Shortlist:
    day: str
    tz: str
    frozen: bool
    created: bool
    entries: list[dict[str, Any]] = field(default_factory=list)
    capacity: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    eligible_pool: int = 0
    stale_skipped: int = 0


def capacity(connection: sqlite3.Connection, config: Config, day: str) -> Capacity:
    admitted = connection.execute(
        "SELECT COUNT(*) AS n FROM selection WHERE day = ?", (day,)
    ).fetchone()["n"]
    outstanding = connection.execute(
        "SELECT COUNT(*) AS n FROM selection WHERE state = 'open'"
    ).fetchone()["n"]
    return Capacity(
        day=day, tz=config.timezone, daily_limit=config.daily_admissions,
        outstanding_limit=config.outstanding_capacity,
        admitted_today=int(admitted), outstanding=int(outstanding),
    )


def today(config: Config) -> str:
    return civil_day(utc_now(), config.timezone)


def eligible_pool(connection: sqlite3.Connection, config: Config) -> tuple[list[dict], int]:
    """Eligible candidates with a fresh enough assessment, in selection order.

    Freshness is a precondition, not a tiebreak: an assessment older than the
    configured window, or one taken at a commit the default branch has since
    moved off, is not a basis for spending half an hour. Those are counted and
    returned to the reassessment pool rather than selected on stale evidence.
    """
    rows = connection.execute(
        "SELECT c.*, a.id AS assessment_id, a.uuid AS assessment_uuid, a.score, "
        "       a.assessed_commit, a.assessed_at, a.components, a.facts, a.reasons, "
        "       a.policy_version, a.classifier_version "
        "FROM candidate c JOIN assessment a ON a.id = c.latest_assessment "
        "WHERE c.triage_status = 'eligible' AND c.analysis_status = 'not_selected'"
    ).fetchall()

    fresh, stale = [], 0
    now = utc_now()
    for row in rows:
        if duplicate_reason(connection, row):
            continue
        age_days = (now - parse_iso(row["assessed_at"])).total_seconds() / 86400
        if age_days > config.assessment_max_age_days:
            stale += 1
            continue
        facts = loads(row["facts"])
        head = facts.get("head_commit")
        if head and row["assessed_commit"] and head != row["assessed_commit"]:
            stale += 1
            continue
        fresh.append({
            "candidate_id": int(row["id"]),
            "name": row["display_name"],
            "canonical": row["canonical_name"],
            "first_seen_at": row["first_seen_at"],
            "assessment_id": int(row["assessment_id"]),
            "assessment_uuid": row["assessment_uuid"],
            "score": int(row["score"] or 0),
            "commit": row["assessed_commit"],
            "assessed_at": row["assessed_at"],
            "components": loads(row["components"]),
            "facts": facts,
            "reasons": loads(row["reasons"]),
            "policy_version": row["policy_version"],
            "classifier_version": row["classifier_version"],
        })

    # Deterministic all the way down: score, then who was seen first, then the
    # canonical name. Two runs over the same state produce the same order.
    fresh.sort(key=lambda item: (-item["score"], item["first_seen_at"], item["canonical"]))
    return fresh, stale


def existing(connection: sqlite3.Connection, day: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT s.*, c.display_name, c.canonical_name, a.score, a.components, a.facts, "
        "       a.reasons, a.assessed_at, a.policy_version, a.classifier_version, a.uuid AS assessment_uuid "
        "FROM selection s JOIN candidate c ON c.id = s.candidate_id "
        "JOIN assessment a ON a.id = s.assessment_id "
        "WHERE s.day = ? ORDER BY s.slot",
        (day,),
    ).fetchall()
    return [
        {
            "rank": int(row["slot"]),
            "selection_id": row["uuid"],
            "name": row["display_name"],
            "canonical": row["canonical_name"],
            "url": f"https://github.com/{row['display_name']}",
            "commit": row["selected_commit"],
            "score": int(row["score"] or 0),
            "components": loads(row["components"]),
            "facts": loads(row["facts"]),
            "reasons": loads(row["reasons"]),
            "assessed_at": row["assessed_at"],
            "assessment_id": row["assessment_uuid"],
            "policy_version": row["policy_version"],
            "classifier_version": row["classifier_version"],
            "state": row["state"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def finalize(connection: sqlite3.Connection, config: Config, *, day: str | None = None,
             dry_run: bool = False) -> Shortlist:
    """Select for the current configured day, or return the frozen list unchanged."""
    atlas.require(connection)
    current = today(config)
    target = day or current

    frozen_row = connection.execute(
        "SELECT * FROM day_ledger WHERE day = ?", (target,)
    ).fetchone()
    if frozen_row is not None and frozen_row["frozen_at"]:
        shortlist = Shortlist(day=target, tz=frozen_row["tz"], frozen=True, created=False)
        shortlist.entries = existing(connection, target)
        shortlist.capacity = capacity(connection, config, target).as_dict()
        shortlist.notes.append(
            f"{target} was finalized at {frozen_row['frozen_at']}; this is the committed list, "
            f"regenerated rather than reselected"
        )
        return shortlist

    if target != current:
        shortlist = Shortlist(day=target, tz=config.timezone, frozen=False, created=False)
        shortlist.entries = existing(connection, target)
        shortlist.capacity = capacity(connection, config, target).as_dict()
        shortlist.notes.append(
            f"{target} is not the current day in {config.timezone} ({current}); showing what was "
            f"recorded. Historical days do not admit."
        )
        return shortlist

    pool, stale = eligible_pool(connection, config)
    shortlist = Shortlist(day=target, tz=config.timezone, frozen=False, created=False)
    shortlist.eligible_pool = len(pool)
    shortlist.stale_skipped = stale
    if stale:
        shortlist.notes.append(
            f"{stale} eligible candidate(s) were skipped for an assessment older than "
            f"{config.assessment_max_age_days} days or taken at a commit the branch has moved off"
        )

    if dry_run:
        room = capacity(connection, config, target)
        shortlist.capacity = room.as_dict()
        shortlist.entries = [
            _entry(index + 1, None, item) for index, item in enumerate(pool[: room.slots])
        ]
        shortlist.notes.append("dry run: nothing was admitted")
        return shortlist

    with transaction(connection):
        connection.execute(
            "INSERT OR IGNORE INTO day_ledger(day, tz) VALUES (?, ?)", (target, config.timezone)
        )
        ledger = connection.execute("SELECT * FROM day_ledger WHERE day = ?", (target,)).fetchone()
        if ledger["tz"] != config.timezone:
            # A timezone change mid-day cannot reset the allowance: the day the
            # ledger was opened under is the day that counts.
            shortlist.notes.append(
                f"the ledger for {target} was opened in {ledger['tz']}; configuration now says "
                f"{config.timezone}. The existing day keeps its allowance."
            )
        room = capacity(connection, config, target)
        taken = {row["canonical"] for row in existing(connection, target)}
        slot = room.admitted_today
        created = 0
        for item in pool:
            if created >= room.slots:
                break
            if item["canonical"] in taken:
                continue
            slot += 1
            try:
                connection.execute(
                    "INSERT INTO selection(uuid, day, tz, slot, candidate_id, assessment_id, "
                    "selected_commit, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(uuid.uuid4()), target, config.timezone, slot, item["candidate_id"],
                     item["assessment_id"], item["commit"], iso(utc_now())),
                )
            except sqlite3.IntegrityError:
                # Another run got there first, or this candidate already holds an
                # open selection. Either way the ceiling held; move on.
                slot -= 1
                continue
            connection.execute(
                "UPDATE candidate SET analysis_status = 'selected' WHERE id = ?",
                (item["candidate_id"],),
            )
            created += 1
        connection.execute(
            "UPDATE day_ledger SET frozen_at = ?, admitted = ? WHERE day = ?",
            (iso(utc_now()), room.admitted_today + created, target),
        )

    shortlist.created = created > 0
    shortlist.frozen = True
    shortlist.entries = existing(connection, target)
    shortlist.capacity = capacity(connection, config, target).as_dict()
    if not shortlist.entries:
        shortlist.notes.append(
            "no candidate was admitted. This is a statement about the candidates actually "
            "inspected and found eligible, not a claim to have assessed the whole feed."
        )
    return shortlist


def _entry(rank: int, selection_id: str | None, item: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": rank,
        "selection_id": selection_id,
        "name": item["name"],
        "canonical": item["canonical"],
        "url": f"https://github.com/{item['name']}",
        "commit": item["commit"],
        "score": item["score"],
        "components": item["components"],
        "facts": item["facts"],
        "reasons": item["reasons"],
        "assessed_at": item["assessed_at"],
        "assessment_id": item["assessment_uuid"],
        "policy_version": item["policy_version"],
        "classifier_version": item["classifier_version"],
        "state": "proposed",
        "created_at": None,
    }

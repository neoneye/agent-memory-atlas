"""The two budgeted stages between a name and a decision.

Stage B collects cheap metadata for candidates that have none, one repository at
a time, under a daily request budget. Stage C spends a much smaller budget on
actually reading files: the default is a hundred repositories a day, which is a
cost ceiling and not a claim that a hundred inspections yield twenty eligible
projects.

Stage C's hundred is split. Eighty per cent goes to whatever the cheap metadata
ranks highest, and twenty per cent to a deterministic rotation through everything
else — because a ranking built from metadata is a ranking built from the signals
that are easy to see, and a new project with four stars and no description is
exactly what it cannot see. The rotation cursor persists, so the exploration
share walks the backlog instead of re-drawing the same slice every day.

Both stages are resumable. Both stop when a budget is spent, record what they
reached, and report the remainder as a backlog rather than as a finding.
"""

from __future__ import annotations

import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import atlas
import classifier as classifier_module
from config import Config
from db import budget_used, spend, transaction
from evidence import (
    Inspection, PASSING, UNKNOWN, choose_blobs, classify_scope, classify_substance,
    classify_tests, read_blobs, read_tree,
)
from fetching import Client, FetchError, RepoBudget
from identity import bind_repo_id
from metadata import Collector, collect
from policy import Policy, decide
from util import dumps, iso, loads, parse_iso, plus, truncate, utc_now

# Cheap pre-ranking vocabulary. Applied to a name, description and topics — the
# three fields the feed's own metadata gives for free. It decides *reading
# order*, never eligibility, which is why a keyword match is allowed to matter
# here and is not allowed to matter at the gate.
PRESCORE_TERMS = re.compile(
    r"memor|recall|remember|forget|context|knowledge|rag\b|retriev|episodic|semantic"
    r"|agent|session|persist|vector|embedding|graph|note|journal|reflect",
    re.IGNORECASE,
)


@dataclass
class AssessRun:
    metadata_collected: int = 0
    metadata_failed: int = 0
    inspected: int = 0
    eligible: int = 0
    rejected: int = 0
    deferred: int = 0
    skipped_excluded: int = 0
    budget_stopped: str | None = None
    backlog_unassessed: int = 0
    backlog_no_metadata: int = 0
    exploration_slots: int = 0
    notes: list[str] = field(default_factory=list)
    classifier_state: str = "not configured"


# --- exclusions ------------------------------------------------------------

def duplicate_reason(connection: sqlite3.Connection, row: sqlite3.Row) -> str | None:
    """Why this candidate must not be analysed again, or None.

    `already_in_atlas` names an existing report. It does not assert that this
    program performed that analysis — the atlas did, and the frontmatter is where
    that is recorded.
    """
    member = atlas.member(connection, row["canonical_name"])
    if member is None:
        for alias_row in connection.execute(
            "SELECT canonical_name FROM alias WHERE candidate_id = ?", (row["id"],)
        ):
            member = atlas.member(connection, alias_row["canonical_name"])
            if member is not None:
                break
    if member is not None:
        if str(member["slug"]).startswith("excluded:"):
            return f"already examined and set aside by the atlas: {member['slug'][9:]}"
        return (
            f"already_in_atlas: content/systems/{member['slug']}.md reports it at "
            f"{(member['revision'] or '')[:12]} (analysed {member['analyzed_at']})"
        )
    if row["analysis_status"] in ("selected", "running"):
        return f"an analysis is already {row['analysis_status']} for this candidate"
    if row["analysis_status"] == "accepted":
        return "an analysis of this candidate was already accepted"
    return None


def _reassessment_due(row: sqlite3.Row) -> bool:
    when = row["next_assessment_at"]
    if not when:
        return False
    return parse_iso(when) <= utc_now()


def assessable(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    """Candidates this program is still allowed to spend requests on."""
    rows = connection.execute(
        "SELECT * FROM candidate WHERE analysis_status NOT IN "
        "('selected','running','accepted') ORDER BY id"
    ).fetchall()
    out = []
    for row in rows:
        if row["triage_status"] == "rejected" and not _reassessment_due(row):
            continue
        if row["triage_status"] == "deferred" and not _reassessment_due(row):
            continue
        out.append(row)
    return out


# --- stage B ---------------------------------------------------------------

def prescore(facts: dict[str, Any]) -> int:
    """A cheap reading order, not a judgement.

    Deliberately blunt, and deliberately not dominated by stars: a fifteen-point
    contribution against sixty for vocabulary and recency means a popular
    repository with nothing memory-shaped about it sorts below an obscure one
    that looks like the thing being looked for.
    """
    if not facts:
        return 0
    score = 0
    haystack = " ".join(filter(None, [
        str(facts.get("full_name") or ""),
        str(facts.get("description") or ""),
        " ".join(facts.get("topics") or []),
    ]))
    hits = len(set(match.group(0).lower() for match in PRESCORE_TERMS.finditer(haystack)))
    score += min(hits * 10, 40)
    if facts.get("archived"):
        score -= 30
    if facts.get("is_fork"):
        score -= 15
    pushed = facts.get("pushed_at")
    if pushed:
        try:
            age = (utc_now() - parse_iso(pushed.replace("Z", "+00:00"))).days
            score += 20 if age <= 90 else (10 if age <= 365 else 0)
        except ValueError:
            pass
    stars = facts.get("stars") or 0
    score += min(int(stars ** 0.5), 15)
    if (facts.get("size_kb") or 0) < 20:
        score -= 10
    return score


def collect_metadata(config: Config, connection: sqlite3.Connection, client: Client,
                     day: str, run: AssessRun, limit: int | None = None) -> None:
    """One repository at a time, until the daily metadata budget is spent."""
    collector = Collector(client)
    allowance = limit if limit is not None else config.metadata_budget
    spent = budget_used(connection, day, "metadata_repos")
    pending = [
        row for row in assessable(connection)
        if connection.execute(
            "SELECT 1 FROM metadata WHERE candidate_id = ?", (row["id"],)
        ).fetchone() is None
    ]
    run.backlog_no_metadata = len(pending)

    for row in pending:
        if spent >= allowance:
            run.budget_stopped = f"daily metadata budget of {allowance} repositories"
            break
        if duplicate_reason(connection, row):
            run.skipped_excluded += 1
            continue
        owner, name = row["canonical_name"].split("/", 1)
        budget = RepoBudget()
        try:
            facts, coverage = collect(collector, owner, name, budget)
        except FetchError as error:
            if error.category in ("rate_limit", "budget_exceeded"):
                run.budget_stopped = str(error)
                break
            facts, coverage = {}, {"repository": "unavailable"}
        spent = spend(connection, day, "metadata_repos", 1)

        if not facts:
            run.metadata_failed += 1
            _defer(connection, row["id"], days=1,
                   reason=f"metadata unavailable: {coverage.get('repository')}")
            continue

        with transaction(connection):
            repo_id = facts.get("github_repo_id")
            if repo_id and facts.get("full_name"):
                outcome = bind_repo_id(connection, int(row["id"]), int(repo_id),
                                       facts["full_name"])
                if outcome == "renamed":
                    run.notes.append(
                        f"{row['canonical_name']} is now {facts['full_name']}; the decision "
                        f"follows the repository id, not the name"
                    )
                elif outcome == "reused":
                    run.notes.append(
                        f"{row['canonical_name']} now resolves to a repository id held by a "
                        f"different candidate; treated as a separate project"
                    )
                    continue
            connection.execute(
                "INSERT OR REPLACE INTO metadata(candidate_id, collected_at, facts, coverage, prescore) "
                "VALUES (?, ?, ?, ?, ?)",
                (row["id"], iso(utc_now()), dumps(facts), dumps(coverage), prescore(facts)),
            )
        run.metadata_collected += 1
        run.backlog_no_metadata -= 1


def _defer(connection: sqlite3.Connection, candidate_id: int, *, days: int, reason: str) -> None:
    with transaction(connection):
        connection.execute(
            "UPDATE candidate SET triage_status = 'deferred', triage_reason = ?, "
            "next_assessment_at = ? WHERE id = ?",
            (truncate(reason, 500), iso(plus(utc_now(), days=days)), candidate_id),
        )


# --- stage C ---------------------------------------------------------------

def inspection_queue(connection: sqlite3.Connection, config: Config, run: AssessRun,
                     allowance: int | None = None) -> list[sqlite3.Row]:
    """Eighty per cent by metadata rank, twenty per cent by rotation.

    The rotation is a cursor over candidate id, so it is reproducible: the same
    database at the same cursor picks the same exploration slice, and the cursor
    advances past what it handed out.
    """
    rows = [row for row in assessable(connection) if not duplicate_reason(connection, row)]
    have_metadata = {
        int(item["candidate_id"]): int(item["prescore"])
        for item in connection.execute("SELECT candidate_id, prescore FROM metadata")
    }
    eligible_rows = [row for row in rows if int(row["id"]) in have_metadata]
    run.backlog_unassessed = len(eligible_rows)

    budget = config.inspection_budget if allowance is None else allowance
    explore_count = int(budget * config.exploration_share)
    ranked_count = budget - explore_count

    ranked = sorted(
        eligible_rows,
        key=lambda row: (-have_metadata[int(row["id"])], row["first_seen_at"], row["canonical_name"]),
    )
    picked = ranked[:ranked_count]
    picked_ids = {int(row["id"]) for row in picked}

    cursor_row = connection.execute(
        "SELECT cursor FROM rotation WHERE name = 'exploration'"
    ).fetchone()
    cursor = int(cursor_row["cursor"]) if cursor_row else 0
    remainder = sorted(
        (row for row in eligible_rows if int(row["id"]) not in picked_ids),
        key=lambda row: int(row["id"]),
    )
    explored: list[sqlite3.Row] = []
    if remainder and explore_count:
        start = next((index for index, row in enumerate(remainder) if int(row["id"]) > cursor), 0)
        ordered = remainder[start:] + remainder[:start]
        explored = ordered[:explore_count]
        connection.execute(
            "INSERT INTO rotation(name, cursor) VALUES ('exploration', ?) "
            "ON CONFLICT(name) DO UPDATE SET cursor = excluded.cursor",
            (int(explored[-1]["id"]) if explored else cursor,),
        )
    run.exploration_slots = len(explored)
    return picked + explored


def inspect_one(config: Config, connection: sqlite3.Connection, client: Client,
                policy: Policy, row: sqlite3.Row, manual: dict[str, Any],
                run: AssessRun, day: str) -> dict[str, Any]:
    """Read one repository within the per-repository ceilings and decide.

    Bodies live in local variables for the length of this function. What is
    written down is paths, hashes, excerpts and the decision.
    """
    owner, name = row["canonical_name"].split("/", 1)
    stored = connection.execute(
        "SELECT * FROM metadata WHERE candidate_id = ?", (row["id"],)
    ).fetchone()
    facts = loads(stored["facts"]) if stored else {}
    coverage = loads(stored["coverage"]) if stored else {}
    budget = RepoBudget()
    deadline = time.monotonic() + config.limits.assessment_seconds

    commit = facts.get("head_commit")
    inspection = Inspection(commit=commit)
    blob_texts: dict[str, str] = {}

    if commit:
        inspection = read_tree(client, owner, name, commit, budget)
        coverage.update(inspection.coverage)
        if inspection.tree_paths and time.monotonic() < deadline:
            paths = choose_blobs(inspection, config.limits.blobs_per_repo)
            blobs, blob_coverage = read_blobs(client, owner, name, commit, paths, budget)
            inspection.blobs = blobs
            coverage.update(blob_coverage)
            blob_texts = {blob.path: blob.text for blob in blobs if blob.text}
    else:
        coverage["tree"] = "unavailable"
        inspection.notes.append("no default-branch commit was resolved; nothing was read")

    if time.monotonic() >= deadline:
        coverage["deadline"] = "budget_exceeded"
        inspection.notes.append(
            f"the {config.limits.assessment_seconds}s per-repository deadline was reached"
        )

    tests = classify_tests(inspection, config.limits.excerpt_chars)
    scope = classify_scope(inspection)
    substance = classify_substance(inspection)

    # A semantic judgement replaces the heuristic one where it exists, and
    # `basis` records which of the three produced the answer.
    verdict = manual.get(row["canonical_name"])
    classifier_error = None
    if verdict is not None and verdict.raw is not None:
        # A manual assessment cites paths; now that the blobs exist, the citations
        # are checked against them exactly as a model's would be.
        try:
            verdict = classifier_module.validate(verdict.raw, blob_texts)
            verdict.source = "manual"
            verdict.provider = "manual"
            verdict.model = str(verdict.raw.get("assessor", "unnamed"))
        except classifier_module.ClassifierRejected as error:
            run.notes.append(
                f"{row['canonical_name']}: manual assessment rejected ({error}); "
                f"falling back to the structural rules"
            )
            verdict = None
    if verdict is None and config.classifier_provider and blob_texts:
        used = budget_used(connection, day, "classifier_calls")
        if used >= config.limits.classifier_calls_per_day:
            classifier_error = "daily classifier budget spent"
        else:
            try:
                verdict = classifier_module.classify(config, row["display_name"], blob_texts)
                spend(connection, day, "classifier_calls", 1)
            except (classifier_module.ClassifierUnavailable,
                    classifier_module.ClassifierRejected) as error:
                classifier_error = str(error)
                # A failed call still cost one: the ceiling bounds spend, not success.
                spend(connection, day, "classifier_calls", 1)

    if verdict is not None:
        scope.in_scope = verdict.in_scope
        scope.basis = verdict.source
        scope.reasons.append(f"{verdict.source}: {verdict.reasoning}")
        if verdict.substance is not None:
            substance.readable = verdict.substance
            substance.reasons.append(f"{verdict.source}: substance judged from cited excerpts")
        if verdict.test_evidence_level != UNKNOWN and tests.level == UNKNOWN:
            tests.level = verdict.test_evidence_level
            tests.reason += f"; {verdict.source} read it as {verdict.test_evidence_level}"
        run.classifier_state = verdict.version
    elif classifier_error:
        run.classifier_state = f"error: {classifier_error}"
        run.notes.append(f"{row['canonical_name']}: classifier unavailable ({classifier_error})")

    decision = decide(
        policy, scope=scope, substance=substance, tests=tests, facts=facts,
        coverage=coverage, blob_texts=blob_texts,
        duplicate=duplicate_reason(connection, row),
        corpus_loaded=atlas.count(connection) > 0,
    )
    if scope.basis == "heuristic":
        decision.limitations.append(
            "scope and substance were judged by structural rules — path and vocabulary "
            "matching over the files read — not by anything that read the code. No "
            "classifier was configured and no manual assessment was supplied."
        )

    record = {
        "uuid": str(uuid.uuid4()),
        "candidate_id": int(row["id"]),
        "github_repo_id": facts.get("github_repo_id"),
        "assessed_commit": commit,
        "assessed_at": iso(utc_now()),
        "policy_version": policy.version,
        "classifier_version": verdict.version if verdict else None,
        "outcome": decision.outcome,
        "score": decision.score,
        "components": decision.components,
        "gates": decision.gates,
        "facts": facts,
        "coverage": coverage,
        "reasons": decision.reasons,
        "decision": decision,
        "tests": tests,
        "inspection": inspection,
        "budget": budget,
    }
    _persist(connection, row, record, policy)
    return record


def _persist(connection: sqlite3.Connection, row: sqlite3.Row, record: dict[str, Any],
             policy: Policy) -> None:
    decision = record["decision"]
    tests = record["tests"]
    inspection = record["inspection"]
    budget = record["budget"]
    facts_blob = dict(record["facts"])
    facts_blob["test_evidence"] = {
        "level": tests.level,
        "reason": tests.reason,
        "ci_configured": tests.ci_configured,
        "ci_workflow": tests.ci_workflow,
        "ci_run_observed": tests.ci_run_observed,
        "files": tests.files,
    }
    facts_blob["inspection"] = {
        "commit": inspection.commit,
        "tree_paths": len(inspection.tree_paths),
        "tree_truncated": inspection.truncated,
        "blobs_read": len([b for b in inspection.blobs if b.text]),
        "blob_paths": [b.path for b in inspection.blobs],
        "notes": inspection.notes,
        "requests": budget.requests,
        "source_bytes": budget.source_bytes,
    }
    facts_blob["awards"] = decision.awards
    facts_blob["cautions"] = decision.cautions
    facts_blob["limitations"] = decision.limitations
    facts_blob["reassessment_condition"] = decision.reassessment_condition

    with transaction(connection):
        cursor = connection.execute(
            "INSERT INTO assessment(uuid, candidate_id, github_repo_id, assessed_commit, "
            "assessed_at, policy_version, classifier_version, outcome, score, components, "
            "gates, facts, coverage, reasons) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                record["uuid"], record["candidate_id"], record["github_repo_id"],
                record["assessed_commit"], record["assessed_at"], record["policy_version"],
                record["classifier_version"], record["outcome"], record["score"],
                dumps(record["components"]), dumps(record["gates"]), dumps(facts_blob),
                dumps(record["coverage"]), dumps(record["reasons"]),
            ),
        )
        assessment_id = int(cursor.lastrowid)
        next_at = (
            iso(plus(utc_now(), days=decision.reassess_in_days))
            if decision.reassess_in_days else None
        )
        if decision.outcome == "eligible":
            next_at = iso(plus(utc_now(),
                               days=policy.reassessment_days["eligible_unselected_expiry"]))
        connection.execute(
            "UPDATE candidate SET triage_status = ?, triage_reason = ?, last_assessed_at = ?, "
            "latest_assessment = ?, next_assessment_at = ?, inspections = inspections + 1 "
            "WHERE id = ?",
            (
                decision.outcome, truncate("; ".join(decision.reasons), 900),
                record["assessed_at"], assessment_id, next_at, record["candidate_id"],
            ),
        )
    record["assessment_id"] = assessment_id


def run_stage_c(config: Config, connection: sqlite3.Connection, client: Client, policy: Policy,
                day: str, run: AssessRun, manual: dict[str, Any],
                limit: int | None = None) -> None:
    if config.limits.concurrent_assessments != 1:
        raise RuntimeError(
            f"concurrent_assessments is {config.limits.concurrent_assessments}; this build "
            f"assesses one repository at a time under a single application lock, and there is "
            f"no path that runs two. Leave it at 1 rather than configuring a concurrency that "
            f"does not exist."
        )
    allowance = limit if limit is not None else config.inspection_budget
    queue = inspection_queue(connection, config, run, allowance)
    spent = budget_used(connection, day, "inspections")

    for row in queue:
        if spent >= allowance:
            run.budget_stopped = f"daily inspection budget of {allowance} repositories"
            break
        try:
            record = inspect_one(config, connection, client, policy, row, manual, run, day)
        except FetchError as error:
            if error.category in ("rate_limit", "budget_exceeded"):
                run.budget_stopped = str(error)
                _defer(connection, int(row["id"]), days=1, reason=f"stopped: {error}")
                break
            _defer(connection, int(row["id"]), days=1, reason=f"fetch failed: {error}")
            run.deferred += 1
            continue
        spent = spend(connection, day, "inspections", 1)
        run.inspected += 1
        run.backlog_unassessed = max(run.backlog_unassessed - 1, 0)
        if record["outcome"] == "eligible":
            run.eligible += 1
        elif record["outcome"] == "rejected":
            run.rejected += 1
        else:
            run.deferred += 1

    # The queue is built to the size of the budget, so a full day usually ends by
    # running out of queue rather than by breaking out of the loop. Both are the
    # budget stopping the run, and the report says so either way.
    if spent >= allowance and run.backlog_unassessed > 0:
        run.budget_stopped = f"daily inspection budget of {allowance} repositories"

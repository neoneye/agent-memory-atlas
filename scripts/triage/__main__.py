#!/usr/bin/env python3
"""Candidate triage for the Agent Memory Atlas.

    python3 scripts/triage <command> [options]

Scout discovers repositories and writes them to `data/candidates.jsonl`. The
atlas can read about twenty repositories a day, properly, at a pinned commit.
This program stands between the two: it imports Scout's index without ever
writing to it, collects cheap evidence, remembers every decision, and produces
one bounded, explained shortlist a day.

It never clones anything, never runs anything it fetched, and never files an
issue. The expensive analysis is a separate program; the contract with it is
`claim` and `result`.

Run `python3 scripts/triage <command> --help` for a command's options.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import traceback
import unittest
from pathlib import Path
from typing import Any

import atlas
import attempts
import assess as assess_module
import db
import ingest as ingest_module
import journal
import reports
import scratch as scratch_module
import selection as selection_module
from classifier import ClassifierRejected, load_manual
from config import Config, load as load_config
from db import StateCorrupt, StateMissing, transaction, vacuum_cache
from fetching import Client
from policy import Policy
from util import civil_day, dumps, human_bytes, iso, loads, redact, utc_now

EXPORT_TABLES = [
    "meta", "candidate", "alias", "assessment", "day_ledger", "selection", "attempt",
    "budget", "rate_limit", "atlas_member", "rotation", "ingestion", "metadata",
    "stale_submission",
]
# `http_cache` is deliberately absent: it is a disposable cache of fetched
# response bodies, not a decision, and a backup is for decisions.


class Exit(RuntimeError):
    """A clean failure with a message for the user."""


# --- plumbing --------------------------------------------------------------

def open_state(config: Config, *, create: bool = False) -> sqlite3.Connection:
    return db.connect(config.db_path, create=create)


def make_client(config: Config, connection: sqlite3.Connection) -> Client:
    return Client(config, connection, civil_day(utc_now(), config.timezone))


def emit(payload: Any, *, as_json: bool) -> None:
    if as_json:
        print(dumps(payload))
        return
    print(_pretty(payload))


def _pretty(payload: Any, indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(payload, dict):
        lines = []
        for key, value in payload.items():
            if isinstance(value, (dict, list)) and value:
                lines.append(f"{pad}{key}:")
                lines.append(_pretty(value, indent + 1))
            else:
                lines.append(f"{pad}{key}: {_scalar(value)}")
        return "\n".join(lines)
    if isinstance(payload, list):
        return "\n".join(_pretty(item, indent) if isinstance(item, (dict, list))
                         else f"{pad}- {_scalar(item)}" for item in payload)
    return f"{pad}{_scalar(payload)}"


def _scalar(value: Any) -> str:
    if value is None:
        return "unknown"
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


# --- commands --------------------------------------------------------------

def cmd_init(args, config: Config) -> int:
    if config.db_path.exists() and not args.force:
        raise Exit(f"{config.db_path} already exists. Use --force to migrate it in place.")
    config.state_dir.mkdir(parents=True, exist_ok=True)
    connection = open_state(config, create=True)
    with transaction(connection):
        db.set_meta(connection, "policy_version", Policy.load(config.policy_file).version)
        db.set_meta(connection, "atlas_repo", str(config.atlas_repo))
    summary = atlas.sync(connection, config.atlas_repo, config.policy_file.parent / "exclusions.txt")
    scratch_module.Scratch(config.scratch_root, config.state_dir,
                           max_bytes=config.limits.scratch_bytes).ensure()
    emit({
        "state": str(config.db_path),
        "schema_version": db.schema_version(connection),
        "atlas_inventory": summary,
        "output_dir": str(config.output_dir),
        "source": config.source_identity,
        "note": "nothing is fetched yet; run `ingest`",
    }, as_json=args.json)
    return 0


def cmd_ingest(args, config: Config) -> int:
    connection = open_state(config)
    with scratch_module.application_lock(config.lock_path, wait=args.wait):
        _housekeeping(config, connection)
        try:
            inventory = atlas.sync(connection, config.atlas_repo,
                                   config.policy_file.parent / "exclusions.txt")
        except atlas.InventoryUnavailable as error:
            inventory = {"error": str(error)}
        client = None if config.source_kind == "file" else make_client(config, connection)
        result = ingest_module.run(config, connection, client)
    summary = {
        "status": result.status,
        "transport": result.transport,
        "content_hash": result.content_hash,
        "unchanged_since_last_fetch": result.unchanged,
        "lines": result.lines_total,
        "repository_records": result.repo_records,
        "non_repository_records": result.other_records,
        "malformed_or_invalid": result.malformed + result.invalid_names,
        "newly_imported": result.imported_new,
        "already_known": result.duplicates,
        "source_shapes": result.shapes,
        "observations_added": result.observations_added,
        "legacy_holds_applied": result.holds_applied,
        "legacy_holds_cleared_by_payload": result.holds_cleared,
        "hold_not_applied": result.dispositions,
        "verification": result.verification,
        "upstream_commit": result.upstream_commit,
        "quarantine": result.quarantine,
        "atlas_inventory": inventory,
    }
    if result.failure:
        summary["failure"] = result.failure
    emit(summary, as_json=args.json)
    return 0 if result.status == "complete" else 1


def _manual_assessments(args, config: Config) -> dict:
    if not getattr(args, "manual", None):
        return {}
    try:
        return load_manual(Path(args.manual))
    except ClassifierRejected as error:
        raise Exit(f"manual assessment file rejected: {error}") from None


def cmd_assess(args, config: Config) -> int:
    connection = open_state(config)
    policy = Policy.load(config.policy_file)
    day = civil_day(utc_now(), config.timezone)
    run = assess_module.AssessRun()
    if config.classifier_provider:
        run.classifier_state = f"{config.classifier_provider}:{config.classifier_model}"

    manual = _manual_assessments(args, config)
    if manual:
        run.classifier_state = "manual assessments imported"

    with scratch_module.application_lock(config.lock_path, wait=args.wait):
        _housekeeping(config, connection)
        client = make_client(config, connection)
        if not args.inspect_only:
            assess_module.collect_metadata(config, connection, client, day, run,
                                           limit=args.metadata_limit,
                                           policy_version=policy.version)
        if not args.metadata_only:
            assess_module.run_stage_c(config, connection, client, policy, day, run, manual,
                                      limit=args.limit)
    emit(_assess_summary(run, policy), as_json=args.json)
    return 0


def _assess_summary(run, policy: Policy) -> dict:
    return {
        "policy_version": policy.version,
        "metadata_collected": run.metadata_collected,
        "metadata_refreshed": run.metadata_refreshed,
        "metadata_failed": run.metadata_failed,
        "backlog_stale_metadata": run.backlog_stale_metadata,
        "legacy_held_not_spent_on": run.held_skipped,
        "inspected": run.inspected,
        "eligible": run.eligible,
        "rejected": run.rejected,
        "deferred": run.deferred,
        "skipped_already_handled": run.skipped_excluded,
        "exploration_slots": run.exploration_slots,
        "backlog_without_metadata": run.backlog_no_metadata,
        "backlog_assessable": run.backlog_unassessed,
        "budget_stopped": run.budget_stopped,
        "scope_judged_by": run.classifier_state,
        "notes": run.notes,
    }


def cmd_select(args, config: Config) -> int:
    connection = open_state(config)
    with scratch_module.application_lock(config.lock_path, wait=args.wait):
        try:
            shortlist = selection_module.finalize(connection, config, day=args.day,
                                                  dry_run=args.dry_run)
        except atlas.InventoryUnavailable as error:
            raise Exit(str(error)) from None
        records = None if args.dry_run else _write_day(config, connection, shortlist, {})
    emit({
        "day": shortlist.day,
        "frozen": shortlist.frozen,
        "selected": len(shortlist.entries),
        "eligible_pool": shortlist.eligible_pool,
        "capacity": shortlist.capacity,
        "notes": shortlist.notes,
        "files": records,
    }, as_json=args.json)
    return 0


def _batch_from_state(connection: sqlite3.Connection, config: Config, day: str) -> dict:
    """Rebuild a day's batch summary from the database.

    `run` has live counters and passes its own. `select` on its own does not, and
    reporting zeros there would be a false statement about the day rather than a
    missing one — so the counts come back out of the tables that recorded them.
    """
    last = connection.execute("SELECT * FROM ingestion ORDER BY id DESC LIMIT 1").fetchone()
    outcomes = {
        row["outcome"]: row["n"]
        for row in connection.execute(
            "SELECT outcome, COUNT(*) AS n FROM assessment WHERE substr(assessed_at, 1, 10) = ? "
            "GROUP BY outcome",
            (day,),
        )
    }
    budgets = {
        row["name"]: row["used"]
        for row in connection.execute("SELECT name, used FROM budget WHERE day = ?", (day,))
    }
    return {
        "policy_version": db.get_meta(connection, "policy_version"),
        "transport": last["transport"] if last else None,
        "import": {
            "status": last["status"] if last else "never fetched",
            "fetched_at": last["fetched_at"] if last else None,
            "repo_records": last["repo_records"] if last else None,
            "imported_new": last["imported_new"] if last else None,
            "duplicates": last["duplicates"] if last else None,
            "other_records": last["other_records"] if last else None,
            "malformed": last["malformed"] if last else None,
        },
        "assessment": {
            "inspected": sum(outcomes.values()),
            "eligible": outcomes.get("eligible", 0),
            "rejected": outcomes.get("rejected", 0),
            "deferred": outcomes.get("deferred", 0),
            "metadata_collected": budgets.get("metadata_repos", 0),
            "github_requests": budgets.get("github_requests", 0),
            # Held legacy identities are not backlog: nothing will be spent on
            # them until a payload arrives or the maintainer releases them.
            "backlog_without_metadata": int(connection.execute(
                "SELECT COUNT(*) AS n FROM candidate c LEFT JOIN metadata m "
                "ON m.candidate_id = c.id WHERE m.candidate_id IS NULL "
                "AND (c.source_hold IS NULL OR c.source_hold != 'legacy_title_only')").fetchone()["n"]),
            "backlog_assessable": int(connection.execute(
                "SELECT COUNT(*) AS n FROM candidate WHERE triage_status = 'unassessed' "
                "AND (source_hold IS NULL OR source_hold != 'legacy_title_only')"
            ).fetchone()["n"]),
            "scope_judged_by": (
                f"{config.classifier_provider}:{config.classifier_model}"
                if config.classifier_provider else
                "not configured — structural rules only, labelled heuristic"
            ),
        },
        "notes": [],
        "limitations": [],
    }


def _write_day(config: Config, connection: sqlite3.Connection, shortlist,
               batch: dict) -> dict[str, str] | None:
    derived = _batch_from_state(connection, config, shortlist.day)
    for key, value in derived.items():
        if key not in batch or not batch[key]:
            batch[key] = value
        elif isinstance(value, dict):
            batch[key] = {**value, **batch[key]}

    last = connection.execute(
        "SELECT * FROM ingestion ORDER BY id DESC LIMIT 1"
    ).fetchone()
    source = {
        "identity": last["source_identity"] if last else None,
        "status": last["status"] if last else "never fetched",
        "fetched_at": last["fetched_at"] if last else None,
        "content_hash": last["content_hash"] if last else None,
        "bytes": last["content_bytes"] if last else None,
        "transport": batch.get("transport") or (last["transport"] if last else None),
        "failure": last["failure"] if last else None,
        "unchanged": batch.get("unchanged"),
    } if last else {"status": "never fetched"}
    report = reports.build(config, connection, shortlist, batch, source)
    if getattr(shortlist, "frozen", False) or shortlist.entries:
        json_path, digest_path = reports.write(config, report, shortlist.day)
        return {"json": str(json_path), "digest": str(digest_path)}
    return None


def cmd_run(args, config: Config) -> int:
    connection = open_state(config)
    policy = Policy.load(config.policy_file)
    day = civil_day(utc_now(), config.timezone)
    run = assess_module.AssessRun()
    if config.classifier_provider:
        run.classifier_state = f"{config.classifier_provider}:{config.classifier_model}"
    manual = _manual_assessments(args, config)
    if manual:
        run.classifier_state = "manual assessments imported"

    with scratch_module.application_lock(config.lock_path, wait=args.wait):
        _housekeeping(config, connection)
        client = None if config.source_kind == "file" else make_client(config, connection)
        imported = ingest_module.run(config, connection, client)
        if imported.status == "failed" and not args.continue_on_source_failure:
            raise Exit(f"source fetch failed: {imported.failure}. State is untouched. "
                       f"Use --continue-on-source-failure to assess the existing backlog anyway.")
        if client is None:
            client = make_client(config, connection)

        # Ingestion does not depend on the atlas inventory; selection does, and
        # selecting without it risks proposing a repository that already has a
        # report. So a missing inventory stops selection and nothing else.
        inventory_error = None
        try:
            atlas.sync(connection, config.atlas_repo, config.policy_file.parent / "exclusions.txt")
        except atlas.InventoryUnavailable as error:
            inventory_error = str(error)

        if inventory_error is None:
            assess_module.collect_metadata(config, connection, client, day, run,
                                           limit=args.metadata_limit,
                                           policy_version=policy.version)
            assess_module.run_stage_c(config, connection, client, policy, day, run, manual,
                                      limit=args.limit)
            shortlist = selection_module.finalize(connection, config)
        else:
            run.notes.append(
                f"the atlas inventory could not be loaded, so assessment and selection were "
                f"skipped: {inventory_error}. The feed was imported and state is intact."
            )
            shortlist = selection_module.Shortlist(
                day=day, tz=config.timezone, frozen=False, created=False)
            shortlist.capacity = selection_module.capacity(connection, config, day).as_dict()
            shortlist.notes = list(run.notes)
        batch = {
            "policy_version": policy.version,
            "transport": imported.transport,
            "unchanged": imported.unchanged,
            "import": {
                "status": imported.status,
                "repo_records": imported.repo_records,
                "imported_new": imported.imported_new,
                "duplicates": imported.duplicates,
                "other_records": imported.other_records,
                "malformed": imported.malformed + imported.invalid_names,
            },
            "assessment": _assess_summary(run, policy),
            "notes": run.notes,
            "limitations": _limitations(config, run),
        }
        files = None if inventory_error else _write_day(config, connection, shortlist, batch)

    emit({
        "day": shortlist.day,
        "atlas_inventory_error": inventory_error,
        "import": batch["import"],
        "assessment": batch["assessment"],
        "selected": len(shortlist.entries),
        "capacity": shortlist.capacity,
        "files": files,
        "limitations": batch["limitations"],
    }, as_json=args.json)
    return 0


def _limitations(config: Config, run) -> list[str]:
    out = []
    if not config.classifier_provider and run.classifier_state.startswith("not configured"):
        out.append(
            "No semantic classifier is configured. Scope and substance were decided by "
            "structural rules — path shapes and vocabulary in the files that were read — which "
            "is a weaker basis than reading the code, and is labelled `heuristic` everywhere it "
            "appears rather than presented as equivalent."
        )
    if run.budget_stopped:
        out.append(f"A budget stopped the run early: {run.budget_stopped}. The remainder is a "
                   f"backlog, not a set of findings.")
    if run.backlog_unassessed:
        out.append(f"{run.backlog_unassessed} assessable candidates were not inspected today.")
    return out


def cmd_status(args, config: Config) -> int:
    connection = open_state(config)
    day = civil_day(utc_now(), config.timezone)
    counts = {
        row["triage_status"]: row["n"]
        for row in connection.execute(
            "SELECT triage_status, COUNT(*) AS n FROM candidate GROUP BY triage_status"
        )
    }
    analysis = {
        row["analysis_status"]: row["n"]
        for row in connection.execute(
            "SELECT analysis_status, COUNT(*) AS n FROM candidate GROUP BY analysis_status"
        )
    }
    last = connection.execute("SELECT * FROM ingestion ORDER BY id DESC LIMIT 1").fetchone()
    room = selection_module.capacity(connection, config, day)
    emit({
        "state": str(config.db_path),
        "schema_version": db.schema_version(connection),
        "policy_version": db.get_meta(connection, "policy_version"),
        "source": config.source_identity,
        "last_fetch": {
            "at": last["fetched_at"] if last else None,
            "status": last["status"] if last else "never fetched",
            "failure": last["failure"] if last else None,
            "repository_records": last["repo_records"] if last else None,
            "content_hash": (last["content_hash"] or "")[:16] if last else None,
        },
        "candidates_total": connection.execute(
            "SELECT COUNT(*) AS n FROM candidate").fetchone()["n"],
        "triage_status": counts,
        "analysis_status": analysis,
        "atlas_inventory": atlas.count(connection),
        "intake": reports.intake_summary(connection, config),
        "capacity": room.as_dict(),
        "outstanding": attempts.outstanding(connection),
        "budgets_today": {
            row["name"]: row["used"]
            for row in connection.execute("SELECT name, used FROM budget WHERE day = ?", (day,))
        },
        "classifier": (
            f"{config.classifier_provider}:{config.classifier_model}"
            if config.classifier_provider else
            "not configured — scope decided by structural rules, labelled heuristic"
        ),
        "disk": reports.disk_usage(config, connection),
    }, as_json=args.json)
    return 0


def cmd_explain(args, config: Config) -> int:
    from identity import InvalidName, canonical, find, aliases
    connection = open_state(config)
    try:
        key = canonical(args.repo)
    except InvalidName as error:
        raise Exit(str(error)) from None
    row = find(connection, name=key)
    if row is None:
        raise Exit(f"{args.repo} is not in triage state. It may never have been in the feed.")

    history = [
        {
            "assessment_id": item["uuid"],
            "at": item["assessed_at"],
            "commit": (item["assessed_commit"] or "")[:12],
            "outcome": item["outcome"],
            "score": item["score"],
            "components": loads(item["components"]),
            "gates": loads(item["gates"]),
            "reasons": loads(item["reasons"]),
            "coverage": loads(item["coverage"]),
            "policy": item["policy_version"],
            "scope_judged_by": item["classifier_version"] or "structural rules (heuristic)",
            "evidence": {
                key_: value for key_, value in loads(item["facts"]).items()
                if key_ in ("test_evidence", "inspection", "awards", "cautions",
                            "limitations", "reassessment_condition")
            },
        }
        for item in connection.execute(
            "SELECT * FROM assessment WHERE candidate_id = ? ORDER BY assessed_at DESC",
            (row["id"],),
        )
    ]
    selections = [
        dict(item) for item in connection.execute(
            "SELECT uuid, day, slot, state, selected_commit, created_at FROM selection "
            "WHERE candidate_id = ? ORDER BY day",
            (row["id"],),
        )
    ]
    duplicate = assess_module.duplicate_reason(connection, row)
    emit({
        "repo": row["display_name"],
        "github_repo_id": row["github_repo_id"],
        "aliases": aliases(connection, int(row["id"])),
        "first_seen": row["first_seen_at"],
        "last_ingested": row["last_seen_at"],
        "upstream_hints": {
            "note": "what Scout said, of unknown age; not measurements, never read by a gate",
            "observed_upstream_at": row["hints_observed_at"],
            **loads(row["hints"] or "{}"),
        },
        "source_hold": row["source_hold"],
        "source_hold_disposition": row["source_hold_disposition"],
        "observations": loads(row["provenance"]).get("observations", []),
        "triage_status": row["triage_status"],
        "triage_reason": row["triage_reason"],
        "analysis_status": row["analysis_status"],
        "next_assessment_at": row["next_assessment_at"],
        "excluded_because": duplicate,
        "next_action": _next_action(row, duplicate),
        "selections": selections,
        "assessments": history[: args.depth],
    }, as_json=args.json)
    return 0


def _next_action(row, duplicate: str | None) -> str:
    # Order matters: a candidate that is selected is "excluded" from selection,
    # but the action is to finish the analysis, not to do nothing.
    if row["analysis_status"] in ("selected", "running"):
        return (
            f"an analysis is {row['analysis_status']}; claim it with `triage claim` and record "
            f"the outcome with `triage result`"
        )
    if duplicate:
        return "nothing: excluded. " + duplicate
    if row["triage_status"] == "eligible":
        return "in the eligible pool; `triage select` may admit it when a slot is free"
    if row["triage_status"] == "deferred":
        return f"deferred until {row['next_assessment_at']}, then reassessed automatically"
    if row["triage_status"] == "rejected":
        return f"rejected; reassessed after {row['next_assessment_at']}"
    return "awaiting evidence collection under the daily budget"


def cmd_claim(args, config: Config) -> int:
    connection = open_state(config)
    with scratch_module.application_lock(config.lock_path, wait=args.wait):
        try:
            result = attempts.claim(connection, config, args.selection_id, args.worker,
                                    force=args.force)
        except attempts.ClaimRefused as error:
            raise Exit(str(error)) from None
    emit(result.as_dict(), as_json=args.json)
    return 0


def cmd_result(args, config: Config) -> int:
    connection = open_state(config)
    payload = loads(Path(args.input).read_text(encoding="utf-8")) if args.input else {
        "status": args.status,
        "analysed_commit": args.commit,
        "report": args.report,
        "reason": args.reason,
        "retryable": args.retryable,
    }
    with scratch_module.application_lock(config.lock_path, wait=args.wait):
        try:
            result = attempts.record(connection, args.attempt_id, payload)
        except attempts.ResultRefused as error:
            raise Exit(str(error)) from None
    emit(result, as_json=args.json)
    return 0


def cmd_legacy(args, config: Config) -> int:
    """List the held legacy identities, or release some deliberately.

    Release is a decision recorded once: a released identity is not held again
    by a later import, and its ordinary assessment resumes under the normal
    budgets. There is no daily sweep of the held set.
    """
    connection = open_state(config)
    if args.action == "list":
        rows = connection.execute(
            "SELECT display_name, triage_status, source_hold, source_hold_disposition, "
            "source_hold_changed_at FROM candidate WHERE source_hold IS NOT NULL "
            "ORDER BY source_hold, first_seen_at, canonical_name LIMIT ?",
            (args.limit,),
        ).fetchall()
        total = connection.execute(
            "SELECT COUNT(*) AS n FROM candidate WHERE source_hold = 'legacy_title_only'"
        ).fetchone()["n"]
        emit({"held_total": total, "shown": [dict(row) for row in rows]}, as_json=args.json)
        return 0
    if not args.repos and not args.batch:
        raise Exit("name repositories to release, or pass --batch N (at most 50)")
    with scratch_module.application_lock(config.lock_path, wait=args.wait):
        released = ingest_module.release_holds(connection, names=args.repos, batch=args.batch)
    emit({"released": released, "count": len(released)}, as_json=args.json)
    return 0


def cmd_cleanup(args, config: Config) -> int:
    """Cleanup only. No fetching, no classification, no selection."""
    connection = open_state(config)
    with scratch_module.application_lock(config.lock_path, wait=args.wait):
        manager = scratch_module.Scratch(config.scratch_root, config.state_dir,
                                         max_bytes=config.limits.scratch_bytes)
        reaped = manager.reap()
        with transaction(connection):
            cache = vacuum_cache(connection, ttl_days=config.limits.cache_ttl_days,
                                 max_bytes=config.limits.cache_bytes)
        if not reaped["failed"]:
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    usage = reports.disk_usage(config, connection)
    emit({
        "scratch": reaped,
        "cache": cache,
        "disk": usage,
        "note": (
            "decisions, assessments, selections and results are never deleted to reclaim space; "
            "use `triage export` and archive the backup if the state directory must shrink"
        ),
    }, as_json=args.json)
    return 1 if reaped["failed"] else 0


def _housekeeping(config: Config, connection: sqlite3.Connection) -> None:
    """Cache eviction and orphan removal on every run, not only at startup.

    The maintainer does not reboot daily, so anything that only happens at boot
    happens never. A cleanup failure stops repository processing before it
    starts, by raising out of `Scratch.assessment_dir`.
    """
    manager = scratch_module.Scratch(config.scratch_root, config.state_dir,
                                     max_bytes=config.limits.scratch_bytes)
    reaped = manager.reap()
    if reaped["failed"]:
        raise Exit(
            "scratch cleanup failed; not starting repository processing:\n  "
            + "\n  ".join(f"{path}: {message}" for path, message in reaped["failed"])
        )
    with transaction(connection):
        vacuum_cache(connection, ttl_days=config.limits.cache_ttl_days,
                     max_bytes=config.limits.cache_bytes)


def cmd_export(args, config: Config) -> int:
    connection = open_state(config)
    lines = [dumps({
        "kind": "header",
        "schema_version": db.schema_version(connection),
        "policy_version": db.get_meta(connection, "policy_version"),
        "exported_at": iso(utc_now()),
        "source": config.source_identity,
        "note": "decisions and history only; no credentials and no cached response bodies",
    })]
    for table in EXPORT_TABLES:
        for row in connection.execute(f"SELECT * FROM {table}"):
            record = {key: row[key] for key in row.keys()}
            lines.append(dumps({"kind": "row", "table": table, "row": record}))
    payload = "\n".join(lines) + "\n"
    if args.output:
        from util import atomic_write
        atomic_write(Path(args.output), payload, mode=0o600)
        emit({"output": args.output, "rows": len(lines) - 1}, as_json=args.json)
    else:
        sys.stdout.write(payload)
    return 0


def cmd_restore(args, config: Config) -> int:
    source = Path(args.input)
    if not source.is_file():
        raise Exit(f"no backup at {source}")
    if config.db_path.exists() and not args.force:
        raise Exit(
            f"{config.db_path} already exists. A restore replaces a ledger; it does not merge "
            f"into one. Move the existing state aside, or pass --force to replace it."
        )
    if config.db_path.exists():
        config.db_path.replace(config.db_path.with_suffix(".sqlite3.replaced"))

    connection = open_state(config, create=True)
    header, rows, skipped = None, 0, []
    with transaction(connection):
        for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = loads(line)
            except ValueError as error:
                raise Exit(f"{source}:{number}: not JSON ({error}); nothing was restored") from None
            if record.get("kind") == "header":
                header = record
                if int(record.get("schema_version", 0)) > db.SCHEMA_VERSION:
                    raise Exit(
                        f"backup is schema {record['schema_version']}; this build understands "
                        f"{db.SCHEMA_VERSION}"
                    )
                continue
            if record.get("kind") != "row":
                skipped.append(f"line {number}: unknown kind {record.get('kind')!r}")
                continue
            table, payload = record.get("table"), record.get("row")
            if table not in EXPORT_TABLES or not isinstance(payload, dict) or not payload:
                skipped.append(f"line {number}: unknown or empty table {table!r}")
                continue
            # Column names are interpolated into SQL, so they are checked against
            # the table's real columns rather than trusted from the file.
            known = {
                row["name"] for row in connection.execute(f"PRAGMA table_info({table})")
            }
            unknown = set(payload) - known
            if unknown:
                raise Exit(
                    f"{source}:{number}: {table} has no column(s) {sorted(unknown)}; "
                    f"nothing was restored"
                )
            columns = ", ".join(payload)
            marks = ", ".join("?" for _ in payload)
            connection.execute(
                f"INSERT OR REPLACE INTO {table}({columns}) VALUES ({marks})",
                tuple(payload.values()),
            )
            rows += 1
    if header is None:
        raise Exit(f"{source} has no header record; refusing to treat it as a backup")

    live = [
        dict(row) for row in connection.execute(
            "SELECT uuid, selection_id, worker, lease_expires FROM attempt WHERE status = 'running'"
        )
    ]
    emit({
        "restored_from": str(source),
        "exported_at": header.get("exported_at"),
        "rows": rows,
        "skipped": skipped,
        "leases_needing_reconciliation": live,
        "note": (
            "an attempt restored as `running` holds a lease from before the backup. Reconcile "
            "with the worker that held it before reclaiming; `triage claim --force` records the "
            "reclaim and raises the fencing token."
        ) if live else "no active leases in the backup",
    }, as_json=args.json)
    return 0


def cmd_selftest(args, config: Config) -> int:
    suite = unittest.defaultTestLoader.discover(
        str(Path(__file__).parent / "tests"), top_level_dir=str(Path(__file__).parent)
    )
    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    return 0 if runner.run(suite).wasSuccessful() else 1


# --- argument parsing ------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="triage", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--state-dir", help="where triage keeps its own state")
    parser.add_argument("--atlas-repo", help="the atlas checkout to read existing reports from")
    parser.add_argument("--output-dir", help="where the daily JSON report and digest are written")
    parser.add_argument("--source-repo", help="owner/repo holding the candidate feed")
    parser.add_argument("--source-ref", help="branch or tag of the candidate feed")
    parser.add_argument("--source-path", help="path to the candidate feed within that repository")
    parser.add_argument("--source-file", help="read a local candidates.jsonl instead of fetching")
    parser.add_argument("--timezone", help="civil timezone for the daily boundary")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--wait", action="store_true",
                        help="wait for the application lock instead of failing")
    parser.add_argument("--traceback", action="store_true", help="show tracebacks on failure")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create the state database explicitly")
    init.add_argument("--force", action="store_true", help="migrate an existing database in place")
    init.set_defaults(func=cmd_init)

    ingest = sub.add_parser("ingest", help="fetch the candidate feed and import identities")
    # SUPPRESS so that omitting it leaves the top-level --source-file in place;
    # an argparse default here would silently overwrite the parent's value.
    ingest.add_argument("--input", dest="source_file", default=argparse.SUPPRESS,
                        help="a local candidates.jsonl")
    ingest.set_defaults(func=cmd_ingest)

    assess = sub.add_parser("assess", help="collect metadata and inspect evidence, under budget")
    assess.add_argument("--limit", type=int, help="inspect at most this many repositories")
    assess.add_argument("--metadata-limit", type=int, help="collect metadata for at most this many")
    assess.add_argument("--metadata-only", action="store_true")
    assess.add_argument("--inspect-only", action="store_true")
    assess.add_argument("--manual", help="import structured manual assessments from a JSON file")
    assess.set_defaults(func=cmd_assess)

    select = sub.add_parser("select", help="finalize today's bounded selection")
    select.add_argument("--day", help="show a recorded day instead (never admits)")
    select.add_argument("--dry-run", action="store_true", help="show what would be admitted")
    select.set_defaults(func=cmd_select)

    run = sub.add_parser("run", help="ingest, assess, select and write the day's reports")
    run.add_argument("--limit", type=int)
    run.add_argument("--metadata-limit", type=int)
    run.add_argument("--manual")
    run.add_argument("--continue-on-source-failure", action="store_true")
    run.set_defaults(func=cmd_run)

    status = sub.add_parser("status", help="counts, capacity, budgets, last run, disk use")
    status.set_defaults(func=cmd_status)

    explain = sub.add_parser("explain", help="evidence, decision history and next action")
    explain.add_argument("repo")
    explain.add_argument("--depth", type=int, default=3, help="how many assessments to show")
    explain.set_defaults(func=cmd_explain)

    claim = sub.add_parser("claim", help="take an analysis lease on a selection")
    claim.add_argument("selection_id")
    claim.add_argument("--worker", help="an identifier for whoever is running the analysis")
    claim.add_argument("--force", action="store_true",
                       help="reclaim a live lease after reconciling with its holder")
    claim.set_defaults(func=cmd_claim)

    result = sub.add_parser("result", help="record what the analysis found")
    result.add_argument("attempt_id")
    result.add_argument("--input", help="a JSON result document")
    result.add_argument("--status", choices=sorted(attempts.RESULT_STATUSES))
    result.add_argument("--commit", help="the commit actually analysed")
    result.add_argument("--report", help="report path or URL, for an accepted result")
    result.add_argument("--reason", help="structured reason, for a rejected result")
    result.add_argument("--retryable", action="store_true", help="for a technical error")
    result.set_defaults(func=cmd_result)

    legacy = sub.add_parser("legacy", help="list or deliberately release held legacy identities")
    legacy.add_argument("action", choices=["list", "release"])
    legacy.add_argument("repos", nargs="*", help="OWNER/REPO to release")
    legacy.add_argument("--batch", type=int, help="release this many, oldest first (at most 50)")
    legacy.add_argument("--limit", type=int, default=50, help="how many to list")
    legacy.set_defaults(func=cmd_legacy)

    cleanup = sub.add_parser("cleanup", help="remove abandoned scratch and evict caches")
    cleanup.set_defaults(func=cmd_cleanup)

    export = sub.add_parser("export", help="back up decisions and history")
    export.add_argument("--output")
    export.set_defaults(func=cmd_export)

    restore = sub.add_parser("restore", help="rebuild state from a backup, validated")
    restore.add_argument("--input", required=True)
    restore.add_argument("--force", action="store_true", help="replace existing state")
    restore.set_defaults(func=cmd_restore)

    selftest = sub.add_parser("selftest", help="run the bundled test suite")
    selftest.add_argument("--verbose", action="store_true")
    selftest.set_defaults(func=cmd_selftest)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    overrides = {
        key: getattr(args, key, None)
        for key in ("state_dir", "atlas_repo", "output_dir", "source_repo", "source_ref",
                    "source_path", "source_file", "timezone")
    }
    config = load_config({key: value for key, value in overrides.items() if value})
    started = utc_now()
    try:
        code = args.func(args, config)
    except (Exit, StateMissing, StateCorrupt, scratch_module.LockBusy,
            scratch_module.UnsafeRoot, scratch_module.CleanupFailed,
            atlas.InventoryUnavailable, ingest_module.IngestStopped) as error:
        if args.traceback:
            traceback.print_exc()
        message = redact(f"{type(error).__name__}: {error}")
        print(message, file=sys.stderr)
        _log(config, args.command, started, 2, message)
        return 2
    _log(config, args.command, started, code, None)
    return code


def _log(config: Config, command: str, started, code: int, message: str | None) -> None:
    """One line per invocation. Never lets a logging failure fail a command."""
    if command == "selftest":
        return
    journal.write(
        config.log_path, command,
        {
            "seconds": round((utc_now() - started).total_seconds(), 1),
            "exit": code,
            "error": message,
            "source": config.source_identity,
        },
        max_bytes=config.limits.log_bytes,
    )


if __name__ == "__main__":
    sys.exit(main())

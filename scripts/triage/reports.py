"""The day's two artifacts: a JSON document and a Markdown digest.

`scout/YYYY-MM-DD.json` is the machine-readable one, and it is shaped so the
scout-to-triage path can be checked afterwards. One object: the run — the source
snapshot's hash, how many repositories were newly imported as against how many
were already in the backlog, how many were actually inspected, what stopped the
run, the day's capacity and disk use — and a `shortlist` array holding one
object per selected candidate with the evidence that selected it. Six weeks of
those files answer "is this working" without anyone having to reason about a
database.

Not JSON Lines. A file of two lines carrying two different record shapes is a
stream format used where there is no stream: a day's report is one document, it
is read whole, and `json.load` should be the whole of reading it.

It is pretty-printed with sorted keys so that a diff between two days shows what
changed rather than how the serializer felt.

Both files are written from the committed selection transaction with a temporary
file and an atomic rename. If writing fails, the selection still happened and
rerunning regenerates the identical file — it does not admit anything new.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from config import Config
from util import atomic_write, directory_bytes, human_bytes, iso, loads, utc_now


def paths(config: Config, day: str) -> tuple[Path, Path]:
    return config.output_dir / f"{day}.json", config.output_dir / f"{day}.md"


def intake_summary(connection: sqlite3.Connection, config: Config) -> dict[str, Any]:
    """The intake split, read back out of state so every command reports it alike.

    Two vocabularies are kept apart on purpose. *Hints* are what Scout said —
    another program's observation of unknown age. *Measurements* are what this
    program fetched from GitHub itself, with a collection time. A missing hint
    and a missing measurement are different gaps and are counted separately.
    """
    last = connection.execute(
        "SELECT * FROM ingestion WHERE status = 'complete' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    shapes = loads(last["source_shapes"]) if last is not None and last["source_shapes"] else {}
    total = int(connection.execute("SELECT COUNT(*) AS n FROM candidate").fetchone()["n"])
    holds = {
        row["source_hold"] or "none": int(row["n"])
        for row in connection.execute(
            "SELECT source_hold, COUNT(*) AS n FROM candidate GROUP BY source_hold")
    }
    dispositions = {
        row["source_hold_disposition"]: int(row["n"])
        for row in connection.execute(
            "SELECT source_hold_disposition, COUNT(*) AS n FROM candidate "
            "WHERE source_hold_disposition IS NOT NULL GROUP BY source_hold_disposition")
    }
    no_hints = int(connection.execute(
        "SELECT COUNT(*) AS n FROM candidate WHERE hints NOT LIKE '%\"has_latest\":true%'"
    ).fetchone()["n"])
    cutoff = f"-{int(config.metadata_max_age_days)} days"
    not_held = "(c.source_hold IS NULL OR c.source_hold != 'legacy_title_only')"
    no_measurement = int(connection.execute(
        f"SELECT COUNT(*) AS n FROM candidate c LEFT JOIN metadata m ON m.candidate_id = c.id "
        f"WHERE m.candidate_id IS NULL AND {not_held}").fetchone()["n"])
    stale_measurement = int(connection.execute(
        f"SELECT COUNT(*) AS n FROM candidate c JOIN metadata m ON m.candidate_id = c.id "
        f"WHERE julianday(m.collected_at) < julianday('now', ?) AND {not_held}", (cutoff,)
    ).fetchone()["n"])
    return {
        "snapshot": {
            "bytes": last["content_bytes"] if last else None,
            "sha256": last["content_hash"] if last else None,
            "git_blob": last["blob_sha"] if last else None,
            "upstream_commit": last["upstream_commit"] if last else None,
            "verification": last["verification"] if last else None,
            "ingested_at": last["fetched_at"] if last else None,
        },
        "newly_imported": last["imported_new"] if last else None,
        "accumulated_identities": total,
        "source_records": {
            "with_hints": shapes.get("modern"),
            "legacy_title_only": shapes.get("legacy"),
            "without_hints_not_legacy": shapes.get("minimal"),
        },
        "holds": holds,
        "hold_dispositions": dispositions,
        "identities_without_hints": no_hints,
        # Anything the atlas already reports on is excluded here as everywhere
        # else: a report is the end of the road for triage.
        "eligible_unselected": {
            "available": int(connection.execute(
                f"SELECT COUNT(*) AS n FROM candidate c WHERE triage_status = 'eligible' "
                f"AND analysis_status = 'not_selected' AND {not_held} AND NOT EXISTS "
                f"(SELECT 1 FROM atlas_member am WHERE am.canonical_name = c.canonical_name)"
            ).fetchone()["n"]),
            "held": int(connection.execute(
                "SELECT COUNT(*) AS n FROM candidate c WHERE triage_status = 'eligible' "
                "AND analysis_status = 'not_selected' AND source_hold = 'legacy_title_only' "
                "AND NOT EXISTS (SELECT 1 FROM atlas_member am WHERE am.canonical_name = c.canonical_name)"
            ).fetchone()["n"]),
        },
        "not_held_without_measurement": no_measurement,
        "not_held_with_stale_measurement": stale_measurement,
    }


def disk_usage(config: Config, connection: sqlite3.Connection) -> dict[str, Any]:
    cache = connection.execute("SELECT COALESCE(SUM(bytes),0) AS n FROM http_cache").fetchone()["n"]
    state = directory_bytes(config.state_dir)
    scratch = directory_bytes(config.scratch_root)
    return {
        "state_dir": config.state_dir.as_posix(),
        "state_bytes": state,
        "state_human": human_bytes(state),
        "state_ceiling": config.limits.state_bytes,
        "state_over_ceiling": state > config.limits.state_bytes,
        "cache_bytes": int(cache),
        "cache_ceiling": config.limits.cache_bytes,
        "scratch_bytes": scratch,
        "scratch_ceiling": config.limits.scratch_bytes,
        "output_bytes": directory_bytes(config.output_dir),
    }


def _entry_record(entry: dict[str, Any]) -> dict[str, Any]:
    facts = entry.get("facts") or {}
    tests = facts.get("test_evidence") or {}
    inspection = facts.get("inspection") or {}
    return {
        "rank": entry["rank"],
        "selection_id": entry["selection_id"],
        "repo": entry["name"],
        "url": entry["url"],
        "pinned_commit": entry["commit"],
        "score": entry["score"],
        "score_components": entry.get("components") or {},
        "score_awards": facts.get("awards") or [],
        "why_selected": "; ".join(entry.get("reasons") or []),
        "test_evidence": {
            "level": tests.get("level"),
            "why": tests.get("reason"),
            "ci_configured": tests.get("ci_configured"),
            "ci_workflow": tests.get("ci_workflow"),
            # Configured to run is not the same as observed to have run, and
            # nothing here has watched a run.
            "ci_run_observed": tests.get("ci_run_observed", False),
            "files": tests.get("files") or [],
        },
        "metrics": {
            "stars": facts.get("stars"),
            "forks": facts.get("forks"),
            "open_issues_excluding_prs": facts.get("open_issues_excluding_prs"),
            "open_pull_requests": facts.get("open_pull_requests"),
            "contributors_apparently_non_bot": facts.get("contributors_apparently_non_bot"),
            "contributors_bot": facts.get("contributors_bot"),
            "merged_external_pulls": facts.get("merged_external_pulls"),
            "pushed_at": facts.get("pushed_at"),
            "created_at": facts.get("created_at"),
            "license": facts.get("license"),
            "is_fork": facts.get("is_fork"),
            "archived": facts.get("archived"),
        },
        "uncertainty": {
            "coverage": entry.get("coverage") or facts.get("coverage") or {},
            "tree_truncated": inspection.get("tree_truncated"),
            "blobs_read": inspection.get("blobs_read"),
            "tree_paths_listed": inspection.get("tree_paths"),
            "notes": inspection.get("notes") or [],
            "cautions": facts.get("cautions") or [],
            "limitations": facts.get("limitations") or [],
        },
        "assessment_id": entry.get("assessment_id"),
        "assessed_at": entry.get("assessed_at"),
        "policy_version": entry.get("policy_version"),
        "scope_judged_by": entry.get("classifier_version") or "structural rules (heuristic)",
        "state": entry.get("state"),
    }


def build(config: Config, connection: sqlite3.Connection, shortlist, batch: dict[str, Any],
          source: dict[str, Any]) -> dict[str, Any]:
    return {
        "day": shortlist.day,
        "timezone": shortlist.tz,
        "generated_at": iso(utc_now()),
        "generator": "agent-memory-atlas triage",
        "policy_version": batch.get("policy_version"),
        "schema": 1,
        "source": source,
        "import": batch.get("import", {}),
        "assessment": batch.get("assessment", {}),
        "capacity": shortlist.capacity,
        "selected": len(shortlist.entries),
        "eligible_pool": shortlist.eligible_pool,
        "eligible_held": getattr(shortlist, "held_eligible", 0),
        "stale_skipped": shortlist.stale_skipped,
        "intake": intake_summary(connection, config),
        "notes": shortlist.notes + batch.get("notes", []),
        "limitations": batch.get("limitations", []),
        "disk": disk_usage(config, connection),
        "shortlist": [_entry_record(entry) for entry in shortlist.entries],
    }


def write(config: Config, report: dict[str, Any], day: str) -> tuple[Path, Path]:
    json_path, digest_path = paths(config, day)
    usage = report.get("disk", {})
    if usage.get("state_over_ceiling"):
        raise RuntimeError(
            f"state directory is {human_bytes(usage.get('state_bytes'))}, over the "
            f"{human_bytes(usage.get('state_ceiling'))} ceiling. Run `triage cleanup`, or "
            f"export and archive state deliberately. Decisions, results and selections are "
            f"never deleted to make room."
        )
    atomic_write(json_path, json.dumps(report, indent=2, sort_keys=True,
                                       ensure_ascii=False) + "\n", mode=0o644)
    atomic_write(digest_path, digest(report), mode=0o644)
    return json_path, digest_path


def digest(report: dict[str, Any]) -> str:
    meta = report
    entries = report.get("shortlist") or []
    lines: list[str] = []
    add = lines.append

    add(f"# Candidate shortlist — {meta['day']}")
    add("")
    add(f"Generated {meta['generated_at']} by {meta['generator']}, policy "
        f"`{meta.get('policy_version')}`, day boundary in {meta['timezone']}.")
    add("")

    source = meta.get("source", {})
    imported = meta.get("import", {})
    assessment = meta.get("assessment", {})
    capacity = meta.get("capacity", {})

    add("## What arrived")
    add("")
    if source.get("status") == "complete":
        add(f"- Source `{source.get('identity')}` via {source.get('transport')}, "
            f"{source.get('bytes')} bytes, sha256 `{(source.get('content_hash') or '')[:16]}`"
            + (" — unchanged since the last fetch" if source.get("unchanged") else ""))
    else:
        add(f"- **The source was not read.** {source.get('failure')}")
        add("- Nothing was imported. Existing decisions are untouched, and this is a source "
            "failure, not an empty feed.")
    add(f"- {imported.get('repo_records', 0)} repository records, "
        f"{imported.get('imported_new', 0)} of them new to triage, "
        f"{imported.get('duplicates', 0)} already known")
    if imported.get("other_records"):
        add(f"- {imported['other_records']} non-repository records ignored "
            f"(`post`, `meta`)")
    if imported.get("malformed"):
        add(f"- {imported['malformed']} line(s) could not be read and were quarantined")
    add("")

    intake = meta.get("intake") or {}
    if intake:
        records = intake.get("source_records") or {}
        snap = intake.get("snapshot") or {}
        holds = intake.get("holds") or {}
        add("## Intake")
        add("")
        add(f"- Snapshot: {snap.get('bytes')} bytes, sha256 `{(snap.get('sha256') or '')[:16]}`, "
            f"git blob `{(snap.get('git_blob') or 'unknown')[:12]}`, upstream commit "
            f"`{(snap.get('upstream_commit') or 'unknown')[:12]}`, checked by {snap.get('verification')}, "
            f"ingested {snap.get('ingested_at')}")
        add(f"- {intake.get('newly_imported')} identities new in this snapshot, "
            f"{intake.get('accumulated_identities')} accumulated")
        add(f"- Source records: {records.get('with_hints')} carry Scout hints, "
            f"{records.get('legacy_title_only')} are the title-only legacy batch, "
            f"{records.get('without_hints_not_legacy')} have neither")
        add(f"- Held from automatic intake: {holds.get('legacy_title_only', 0)} legacy identities; "
            f"{holds.get('released', 0)} released by the maintainer")
        add(f"- Gaps: {intake.get('identities_without_hints')} identities have no Scout hints; of the "
            f"identities not held, {intake.get('not_held_without_measurement')} have no measurement "
            f"of their own and {intake.get('not_held_with_stale_measurement')} have a stale one")
        waiting = intake.get("eligible_unselected") or {}
        add(f"- Eligible and not selected: {waiting.get('available', 0)} available for a later "
            f"day, {waiting.get('held', 0)} held as legacy with their evidence kept")
        add("")
        add("Scout's hints order which repositories get fetched first. They are never an atlas "
            "score, and Scout's own tiers are not a triage result.")
        add("")

    add("## What was looked at")
    add("")
    add(f"- {assessment.get('metadata_collected', 0)} repositories measured"
        + (f", {assessment['metadata_refreshed']} of them refreshes of stale measurements"
           if assessment.get("metadata_refreshed") else "")
        + f"; {assessment.get('backlog_without_metadata', 0)} still have none")
    # The exploration share is a counter from the run that did the inspecting. A
    # regenerated report does not have it, and reporting zero there would be a
    # claim rather than a gap.
    add(f"- {assessment.get('inspected', 0)} repositories were inspected"
        + (f" ({assessment['exploration_slots']} of them from the rotating exploration share)"
           if assessment.get("exploration_slots") is not None else ""))
    add(f"- {assessment.get('eligible', 0)} eligible, {assessment.get('rejected', 0)} rejected, "
        f"{assessment.get('deferred', 0)} deferred for incomplete evidence")
    add(f"- {assessment.get('backlog_assessable', 0)} assessable candidates remain in the backlog")
    if assessment.get("budget_stopped"):
        add(f"- **Stopped early:** {assessment['budget_stopped']}. The remainder is a backlog, "
            f"not a finding about those repositories.")
    add(f"- Scope and substance judged by: {assessment.get('scope_judged_by', 'unknown')}")
    add("")

    add("## Capacity")
    add("")
    add(f"- {capacity.get('admitted_today', 0)} admitted today of a {capacity.get('daily_limit')} "
        f"daily limit; {capacity.get('outstanding', 0)} outstanding of "
        f"{capacity.get('outstanding_limit')}; {capacity.get('slots_available', 0)} slots free")
    disk = meta.get("disk", {})
    add(f"- State {human_bytes(disk.get('state_bytes'))} of "
        f"{human_bytes(disk.get('state_ceiling'))}; cache "
        f"{human_bytes(disk.get('cache_bytes'))}; scratch "
        f"{human_bytes(disk.get('scratch_bytes'))}")
    add("")

    add("## Shortlist")
    add("")
    if not entries:
        add("No candidate was admitted today.")
        add("")
        if source.get("status") != "complete":
            add("This is a source failure, not a judgement: the feed could not be read.")
        elif assessment.get("budget_stopped"):
            add(f"This is an exhausted budget, not a judgement: {assessment['budget_stopped']}.")
        elif str(assessment.get("scope_judged_by", "")).startswith("not configured"):
            add("No semantic judge is configured, so scope was decided by structural rules. "
                "That is a weaker basis than this program is designed to use, and it is worth "
                "reading the deferred list before concluding anything about the feed.")
        else:
            add("Nothing among the repositories actually inspected passed the gates. "
                "That is a statement about what was inspected, not about the whole feed.")
    for entry in entries:
        tests = entry["test_evidence"]
        metrics = entry["metrics"]
        add(f"### {entry['rank']}. [{entry['repo']}]({entry['url']}) — {entry['score']}/100")
        add("")
        add(f"Pinned at `{(entry['pinned_commit'] or 'unknown')[:12]}`, selection "
            f"`{entry['selection_id']}`, assessed {entry['assessed_at']}.")
        add("")
        add(f"**Why selected.** {entry['why_selected']}")
        add("")
        add("| Component | Points |")
        add("| --- | ---: |")
        for name, points in sorted(entry["score_components"].items()):
            add(f"| {name.replace('_', ' ')} | {points} |")
        add("")
        add(f"**Test evidence — `{tests['level']}`.** {tests['why']}")
        if tests.get("files"):
            add("")
            for item in tests["files"][:5]:
                marker = "asserts" if item.get("assertions") else "no assertion found"
                add(f"- `{item['path']}` ({marker}"
                    + (", memory-related" if item.get("memory_related") else "")
                    + f") sha256 `{(item.get('content_sha256') or '')[:12]}`")
        if tests.get("ci_workflow"):
            add("")
            add(f"CI at `{tests['ci_workflow']}` configures a test runner. No run outcome was "
                f"observed, so nothing is claimed about whether the tests pass.")
        add("")
        add("**Metrics.** "
            + ", ".join(
                f"{key.replace('_', ' ')} {('unknown' if value is None else value)}"
                for key, value in metrics.items()
            ))
        add("")
        uncertainty = entry["uncertainty"]
        if uncertainty.get("tree_truncated"):
            add("**Uncertainty.** GitHub truncated the tree listing; absence of any path is not "
                "evidence here.")
            add("")
        for caution in uncertainty.get("cautions", []):
            add(f"**Caution.** {caution}")
            add("")
        for limitation in uncertainty.get("limitations", []):
            add(f"**Limitation.** {limitation}")
            add("")
        add(f"Scope judged by: {entry['scope_judged_by']}.")
        add("")

    if meta.get("notes"):
        add("## Notes")
        add("")
        for note in meta["notes"]:
            add(f"- {note}")
        add("")
    if meta.get("limitations"):
        add("## Limitations")
        add("")
        for limitation in meta["limitations"]:
            add(f"- {limitation}")
        add("")
    add("---")
    add("")
    add("This shortlist is the best among the candidates actually inspected and found "
        "eligible. It is not a claim to have assessed every repository in the feed, and the "
        "daily digest does not replace the cumulative source or the triage state.")
    return "\n".join(lines) + "\n"

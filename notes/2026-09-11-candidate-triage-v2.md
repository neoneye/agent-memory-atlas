# Candidate triage v2: adapt the existing intake to Scout's update

Handoff for Claude, 11 September 2026.

## Task

Update the **existing** `scripts/triage` implementation to consume the updated `Daily-Nerd/scout` feed effectively. Do not rebuild triage from scratch. The maintainer can process at most **20 candidates per day** through full atlas analysis. Scout discovers projects; atlas triage decides which deserve that limited capacity.

This note supplements [the original triage specification](2026-09-11-candidate-triage.md). For Scout source/schema observations and legacy-record handling, this note supersedes the older snapshot description. Preserve the original requirements for persistent decisions, bounded selection, static inspection, and cleanup unless this note explicitly changes them.

The immediate task is implementation and verification of these adaptations, not running a full analysis batch. Do not create issues, change Daily-Nerd's repository, schedule jobs, push commits, or reset the maintainer's existing triage state.

## Start with what already exists

Read `AGENTS.md`, `scripts/triage/README.md`, the original specification, and the affected modules. Relevant entry points:

| Existing file | Work to inspect |
| --- | --- |
| `scripts/triage/ingest.py` | Fetching, parsing, source hints and provenance |
| `scripts/triage/identity.py` | Canonical names, repository IDs, observation updates |
| `scripts/triage/assess.py` | Metadata queue, preliminary ranking, inspection queue |
| `scripts/triage/metadata.py` | Fresh facts and coverage labels |
| `scripts/triage/db.py` | Migrations, transactional state, persisted budgets |
| `scripts/triage/reports.py` | Daily JSON/Markdown and coverage reporting |
| `scripts/triage/selection.py`, `attempts.py` | Existing admission and analysis-result contracts |
| `scripts/triage/fetching.py`, `scratch.py` | Existing size limits and cleanup boundaries |
| `scripts/triage/tests/` | Existing regression and resource-limit tests |

This handoff was prepared after reading the atlas checkout at `96a2456baa5858e3560f3bd4f54fdae41ed08878`. Recheck the implementation before editing; it may have moved. The code observations below are starting points, not instructions to overwrite later fixes.

The existing program already provides a CLI, SQLite state, daily output under `scout/`, metadata collection, static evidence inspection, optional classifier/manual assessment, and claim/result handling. Keep those components and adapt them. Its README labels the rubric uncalibrated and scope heuristic when no judge is configured; preserve that distinction. This update does not turn a structural heuristic into a verified semantic judgment.

## Upstream source and verified changes

Normal source remains:

- Repository: `Daily-Nerd/scout`
- Ref: `main`
- File: `data/candidates.jsonl`
- [Human-readable file](https://github.com/Daily-Nerd/scout/blob/main/data/candidates.jsonl)
- [Raw file](https://raw.githubusercontent.com/Daily-Nerd/scout/main/data/candidates.jsonl)

No local Scout checkout is required. The maintainer's fork is only a contingency if upstream disappears; never automatically switch to it.

The updated upstream was inspected at commit [`51be06e097d7e77fb50a3250b441e586535f89f3`](https://github.com/Daily-Nerd/scout/commit/51be06e097d7e77fb50a3250b441e586535f89f3), candidate blob `58cec6b9a58eaaef5e17b1072ec524b86016163d`.

### Snapshot facts, not permanent constants

| Observed property | Value |
| --- | ---: |
| Candidate-file bytes | 1,790,897, approximately 1.71 MiB |
| Unique repository records | 3,167 |
| Records with a `latest` payload | 1,912 |
| Records marked `title_only: true`, without `latest` | 1,255 |
| Records with a `latest.readme_bytes` key | 1,743 |
| Records with a `latest.topics` field | 54 |

The snapshot also contained 106 post records and one metadata record. It parsed without malformed lines or duplicate repository names. Do not hard-code these counts or infer a daily arrival rate from them.

Scout still loads, merges, and replaces the complete accumulated index. A rewrite is not a new independent batch and a missing source row is not an instruction to delete atlas decisions.

The new search admits established repositories pushed within 14 days; it no longer requires creation within 14 days. It adds relevance keyword gating and excludes profile repositories. That improves discovery, but does not establish implementation quality.

The initial issue batch was explicitly retracted as a discovery misfire: [upstream explanation, issue 1256](https://github.com/Daily-Nerd/scout/issues/1256). `filed`, a closed issue, and `title_only` are not atlas analysis outcomes.

### Scout's tiers are preliminary hints

Scout now calculates an arithmetic score from stars, recency, memory-related names, README size, topics and description keywords. A/B/C thresholds are in [its configuration](https://github.com/Daily-Nerd/scout/blob/51be06e097d7e77fb50a3250b441e586535f89f3/scout.toml); scoring is in [tiering.py](https://github.com/Daily-Nerd/scout/blob/51be06e097d7e77fb50a3250b441e586535f89f3/src/scout/tiering.py).

These checks do not inspect tests, substantive implementation, contributors, account age or prior work. A long README is not test evidence. A low upstream score can reflect missing metadata, especially on Reddit discoveries and older records without topics.

Scores/tiers/component breakdowns **are not fields in the inspected JSONL**. They exist in runtime results, reports and issue bodies. Do not require them, scrape Markdown reports as the input contract, or fetch thousands of issues to reconstruct them. If upstream later exports them, accept them as versioned source hints distinct from the atlas's own score.

The published [17:21 UTC report](https://github.com/Daily-Nerd/scout/blob/51be06e097d7e77fb50a3250b441e586535f89f3/reports/2026-09-11T17-21-13Z.md) has 182 tier-A and 1,228 tier-B candidates. Scout allows issue filing for both tiers; its displayed top 20 is only a report truncation. It is not a daily admission ledger. Do not replace the atlas's selection logic with that list.

## Required implementation changes

### 1. Preserve the new source hints correctly

In the inspected `ingest.py`, `_provenance()` takes `hint_description` from the top-level record even though Scout normally puts it under `latest`. It also omits `title_only`, topics, README size and most source provenance. Fix the mapping, while retaining support for minimal and older records.

Store bounded, explicitly labelled source hints:

- `title_only` and whether a structurally usable `latest` payload exists;
- description, stars, pushed date, topics, README-size result;
- sources/source URLs and relevant first/last observation timestamps;
- source snapshot identity/hash and upstream commit/blob when available.

Prefer valid values in `latest`, with an explicit documented fallback for older top-level fields. Validate field types, cap lengths/list sizes, and distinguish missing/null from measured zero. `readme_bytes` is a historical size hint, not a fetched test artifact or proof of current README availability. Never infer the repository owner from a Reddit `author`.

Do not promote these hints into fresh `metadata.facts`. Keep source observation time distinct from local ingestion time. A newer Git commit that republishes the accumulated index does not refresh every repository's measurements.

Make repeated/reordered imports preserve the same meaningful observation rather than appending copies just because the ingestion timestamp or line number changed. Retain the bounded provenance policy and a separate last-ingested timestamp. A source hint update may change queue priority; it must not erase assessments or reset analysis results.

### 2. Keep the legacy issue-only batch out of normal assessment spending

Define a source-quality hold, for example `legacy_title_only`, when `title_only is true` **and** there is no usable `latest` payload. Import and retain these identities, but do not spend the ordinary daily metadata/inspection allowance on them by default.

This is a hold on automated intake, not a project-quality rejection. Keep it separate from `analysis_status` and from a permanent atlas exclusion. It must remain effective if the scoring policy version changes; a generic “policy changed, reconsider everything” rule must not reopen this old batch automatically.

Preserve the current behavior for an ordinary minimal `filed` record without an explicit legacy flag: unknown metadata alone must not make every older integration invalid. If a later snapshot supplies a valid payload for a legacy-held identity, clear only that source-quality hold, even if the `title_only` flag remained stale. Any atlas rejection, existing report, selection or running analysis still takes precedence.

Provide an explicit, bounded way to revisit an individual legacy identity or a requested legacy batch. No indefinite daily reconsideration of all 1,255 records and no dependence on upstream closing/reopening issues.

Existing state may already contain these candidates, assessments and a frozen daily shortlist. Add new provenance/hold information idempotently. Do not delete the database, rerun initialization, retroactively cancel selected work, or reset budget usage. New holds affect future automatic spending only. Independently assessed or manually approved legacy candidates should retain their evidence and receive an explicit disposition rather than having decisions silently overwritten.

### 3. Use the richer feed to improve which metadata is fetched first

In the inspected `assess.py`, metadata collection visits assessable candidates without metadata in candidate-ID order. With legacy records imported first, that can spend the budget on the retracted batch before reaching the corrected discoveries.

Filter source-quality holds before budgeted work, then use the saved source hints to prioritize **which missing/stale metadata to fetch next**. Reuse the intent of the existing preliminary ranking and retain deterministic exploration. Do not introduce a second authoritative atlas score or make high stars a gate.

Keep measured facts and source hints distinguishable in code and explanations. Do not feed unknown size/topics through a function that interprets missing values as negative measured facts. Distinctive low-star projects and candidates with sparse metadata must retain a bounded exploration route.

Tests must show that modern metadata-bearing candidates receive work ahead of the legacy-held batch, without permanently starving other non-held candidates.

### 4. Refresh facts deliberately

Scout skips already-seen GitHub repositories and caches README sizes without a freshness contract. The feed is useful for scheduling, but triage must own the evidence used to judge and select a project.

The inspected `collect_metadata()` only checks whether a metadata row exists. Add or verify a configurable staleness policy using `collected_at`, not row existence alone. Refresh under existing daily budgets; share owner lookups where possible. New feed hints can prompt a due refresh but must not trigger unbounded work on every reimport.

Keep the original evidence freshness and commit-pinning requirements before selection. Missing data from API failure, truncated trees or exhausted budgets remains unknown/deferred, not a zero count or “no tests.” Existing analysis rejections and active jobs must not be automatically reopened because a source timestamp changed.

### 5. Prove the larger-feed transport works; preserve resource limits

The feed is now above 1 MB. GitHub's [Contents API documentation](https://docs.github.com/en/rest/repos/contents#get-repository-content) requires raw/object handling for files in this size range; an embedded Base64 content field cannot be assumed.

The existing importer already requests raw content and has a 16 MiB ceiling. Verify it with a greater-than-1-MiB fixture and a small read-only live fetch, rather than replacing working transport code. The same-source raw transport is acceptable; a different repository is not an automatic fallback. Preserve previous successful state on fetch failures. Persist source identity/hash and use a pinned snapshot for reproducible comparisons when possible.

The candidate index is metadata, not thousands of checked-out repositories. Keep:

- no clones, repository archives, extraction, submodule/LFS downloads, installs, builds, or execution of fetched code;
- bounded tree/blob reads in memory, with body limits and timeouts;
- only short evidence excerpts, paths, hashes and derived facts in durable state;
- per-assessment cleanup on completion, error, timeout and ordinary cancellation;
- locked startup cleanup of bounded, application-owned leftovers after a crash;
- cleanup failure stopping new processing and reporting the exact leftover path;
- cache/log rotation during normal operation, with decisions never deleted to reclaim space.

Do not rely on reboot or system `/tmp` cleanup. Do not clean directories belonging to other programs. A SIGKILL cannot run `finally`; recovery must occur on the next locked invocation or explicit cleanup. The full analyser remains responsible for any checkout it creates.

### 6. Make the daily report explain the intake split

Extend `scout/YYYY-MM-DD.json` and its Markdown rendering with:

- source snapshot size/hash and ingestion time;
- newly imported identities versus the accumulated total;
- metadata-bearing source records, legacy-held records, and incomplete modern records;
- hints missing versus fresh measurements missing;
- metadata refreshed, repositories inspected, and work deferred by budgets;
- eligible-but-unselected candidates and existing daily/outstanding capacity.

Name upstream hints distinctly from the atlas assessment score. Never call Scout tier A “passed triage.” No need to import Scout's Markdown reports into the application.

Keep both existing limits: at most **20 new admissions per Copenhagen day**, and at most **20 outstanding selections/analyses** by default. Today's committed selection remains frozen; reruns must not issue another batch. Preserve accepted/rejected/error distinctions and claim/result idempotency.

## Implementation order and verification

1. **Map current behavior.** Confirm the file/function observations above against HEAD. State what is already implemented and only change remaining gaps. Use small synthetic fixtures matching upstream's old and new shapes; avoid committing the whole live feed as a fixture.
2. **Adapt ingestion and state.** Add source hints, stable observation deduplication and the legacy hold. Use a versioned migration only if schema changes are needed. Exercise an existing-state upgrade/export/restore round trip, including accepted/rejected results and a frozen shortlist.
3. **Adapt scheduling and refresh.** Apply holds before budget use, use hints for metadata ordering, preserve exploration, and refresh expired measured facts under existing budgets.
4. **Update reports and docs.** Keep the existing CLI and output locations. Document legacy handling, explicit reconsideration, hint freshness, and upstream-vs-atlas scoring. Link this note from the triage README or notes index if appropriate to repository conventions.
5. **Verify offline, then pilot.** Run the existing triage tests and focused additions. Use an isolated temporary state/output directory for tests; do not touch production state or today's committed shortlist. A live pilot should fetch the feed and inspect at most a small stated number of repositories, without finalizing a new production selection. Report requests, bytes, results and cleanup observations. Do not run full atlas analyses as verification.

Acceptance cases to add or extend:

- Modern nested `latest` hints survive ingestion; unexpected fields and missing topics are tolerated.
- Minimal `filed` records remain valid. Explicit title-only records import but consume no normal assessment budget.
- A legacy record later gains a payload and loses only its source-quality hold. A true analysis rejection remains rejected.
- Existing accepted/running/selected work and frozen-day admissions survive migration and source reimport.
- Reordered/unchanged snapshots do not grow equivalent provenance entries or reset decisions.
- Metadata-bearing modern rows reach the queue before held legacy rows; exploration remains deterministic and bounded.
- Old measured metadata refreshes; missing/unknown values never become measured zero.
- A feed over 1 MiB works through raw transport. Over-limit/truncated responses preserve the old state and report failure.
- Missing upstream tier/score fields never break ingestion. Hypothetical future fields cannot override atlas gates.
- A README-only or curated-list repository cannot pass merely because its upstream score would be high. Scope and substantive-test gates remain independent.
- Normal and injected-failure runs leave no per-repository scratch; crash recovery does not touch neighboring directories. Cache/log/provenance size remains bounded across repeated imports.
- Repeated, concurrent and next-day selection preserve daily/outstanding caps and analysis-result deduplication.

This is an intake update. Do not change capability marks or report claims based on stars, Scout tiers, issue status, or these intake measurements. Run site checks only if implementation touches site/build inputs or repository rules require them; a notes-only change does not itself call for a full site rebuild.

## Completion report expected from Claude

Explain what changed in the existing implementation, which upstream changes it now handles, how existing state was preserved, and which tests actually ran. Give the exact operational commands supported by the resulting CLI for ordinary intake and deliberate legacy reconsideration. Include one sample digest with clearly identified fixture or live provenance and measured resource use. State any unresolved compatibility or calibration limitations; do not claim that running a small pilot proves the ranking finds the globally best twenty projects.

Keep the response centered on the maintainer's workflow: Daily-Nerd supplies discoveries; the atlas keeps its own decisions; only a bounded shortlist reaches full analysis; temporary repository material does not accumulate.

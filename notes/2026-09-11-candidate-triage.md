# Agent Memory Atlas candidate triage

Specification and implementation plan for Claude — 11 September 2026.

## 1. Assignment and intended outcome

Build a triage program for the maintainer of Agent Memory Atlas. Scout discovers repositories; the atlas maintainer can process at most **20 candidates per day** through an expensive repository analysis that takes roughly 10–40 minutes per candidate.

The program must ingest Scout's discoveries, obtain enough evidence to assess them cheaply, remember decisions, and produce a ranked daily shortlist. It must not create GitHub issues or run the full atlas analysis. The maintainer should see up to 20 candidates and an understandable explanation for each, without manually inspecting the entire incoming feed.

Treat 1,400 incoming repositories per day as a capacity scenario, not a measured arrival rate. An accumulated candidate file containing that many repositories does not establish daily volume. Report newly imported repositories separately from the total backlog.

Implement this as an independent atlas intake component. Prefer a small Python CLI in the agent-memory-atlas repository, following that repository's actual instructions and layout. Inspect the target repository before choosing paths. The implementation must not depend on a checkout or fork of Scout, and does not require modifying Scout's discovery code.

Use Python's standard library and existing project dependencies where practical. Do not introduce a web service, message broker, vector database, or trained classifier for the initial version.

## 2. Candidate source and its existing behavior

Primary source:

- Repository: `Daily-Nerd/scout`
- Branch: `main`
- Path: `data/candidates.jsonl`
- Human-readable URL: <https://github.com/Daily-Nerd/scout/blob/main/data/candidates.jsonl>
- Raw URL: <https://raw.githubusercontent.com/Daily-Nerd/scout/main/data/candidates.jsonl>
- GitHub Contents API: `GET /repos/Daily-Nerd/scout/contents/data/candidates.jsonl?ref=main`

Make source repository, ref, path, and an optional local-file override configurable. Use Daily-Nerd's repository as the normal source. The maintainer's fork is only a contingency backup if upstream disappears, not an implementation dependency or an automatic fallback. If upstream becomes unavailable, preserve state and report the failure; switching to a backup source requires an explicit configuration change. Do not hard-code the maintainer's filesystem path into the application.

The following observations were verified against a saved Scout snapshot at commit `6278176`; they are not a verification of the current live upstream branch:

- Scout loads the existing JSONL into dictionaries keyed by repository name and post ID, merges observations, then replaces the file with the complete accumulated index. It does not intentionally discard yesterday's candidates. It is not an append-only event stream.
- The scheduled workflow persists the index to GitHub, including scheduled runs that do not create issues.
- Records include `kind: repo`, `kind: post`, and `kind: meta`. Only repository records are intake candidates.
- `status: filed` means a Scout issue was filed, not that the atlas assessed the repository. Import both `filed` and `pending` repository records.
- The inspected file was 215,661 bytes, approximately 211 KiB, containing 1,258 repository records. Only three contained the optional `latest` metadata object. Most records provided a repository name and issue reference only.
- GitHub discovery skips previously seen repository names. New Reddit posts can mention the same repository again. Saved records merge by name; subsequent observations can overwrite `latest` metadata.

A minimal valid incoming record is:

```json
{"kind":"repo","repo":"example/memory-project","status":"filed","issue_number":123}
```

Do not require a description, stars, `latest`, or source URL. Do not interpret Scout's Reddit `author` as the GitHub repository owner. Treat incoming metadata as hints requiring fresh evidence, not authoritative triage results.

Scout source references: `src/scout/history.py`, `src/scout/github_search.py`, `src/scout/reddit.py`, and `.github/workflows/scout.yml` in `Daily-Nerd/scout`.

## 3. Ownership: discoveries, assessments, and results

Scout owns `candidates.jsonl`. Triage reads it and **never edits, deletes entries from, or pushes changes to it**. A candidate that fails triage or atlas analysis remains in discovery history.

Triage owns its separate persistent state. Use SQLite for transactional decisions, daily selection limits, and analysis claims. Provide JSONL export/import for portability and backup; exports are derived artifacts, not a second independently writable authority. Do not use Scout's disposable `state/scout.db` as triage state.

Use a configurable state directory, proposed local default `~/.local/share/agent-memory-atlas-triage/`, outside temporary storage and outside any downloaded repository. Resolve all paths from configuration. An ephemeral CI runner must restore and persist this state; it must never silently start fresh every day.

Initially identify a source entry by validated, case-normalized `owner/repo`. Resolve the GitHub repository ID during metadata enrichment and use that ID for persistent identity. Retain old and current names as aliases. A rename or transfer must not reset a previous decision. If a name is reused for a different repository ID, treat it as a different project. Do not merge forks merely because they share a parent; identical/unmodified forks may be rejected with evidence.

Store these logical entities, with migrations and a schema version:

| Entity | Minimum information |
| --- | --- |
| Source ingestion | Source identity, fetch time, ETag/blob identifier when available, content hash, complete/failed status, imported/duplicate/malformed counts |
| Candidate | Repository ID when resolved, aliases, source provenance, first/last observation, current decision, next assessment date |
| Assessment | Immutable ID, repository ID, assessed commit, timestamp, evidence coverage, measured facts, gate outcomes, score components, reasons, policy version, classifier version if used |
| Selection | Date, configured timezone, slot, candidate ID, assessment ID, selected commit, creation time |
| Analysis attempt | Attempt ID, selection ID, claim/lease, timestamps, result status, actual analysed commit, rejection reason or report reference |

Each measurement needs a value plus coverage such as `complete`, `sampled`, `unavailable`, or `budget_exceeded`. Unknown counts must be null, never fabricated as zero. Keep the measurement's timestamp and sample window where applicable.

Ingest the complete source snapshot by identity on every changed fetch. Do not use a line-number cursor: Scout rewrites its index. Missing entries in a later source snapshot do not delete local decisions. Repeated imports are idempotent.

Fetch and validate the source before committing the ingestion transaction. A failed or oversized fetch must leave the previous successful state intact. Count and report malformed lines; quarantine a bounded diagnostic rather than silently pretending the feed is complete. If a nonempty input yields no valid repositories, stop for inspection.

## 4. Pipeline and capacity

### A. Import and exclude already handled projects

Import identities, resolve known aliases, and consult triage state before fetching more information. Exclude repositories already accepted into the atlas, rejected without a due reassessment, selected, or being analysed.

Provide an adapter for the atlas's existing report metadata and exclusions. Inspect the atlas implementation rather than assuming that a Scout issue or archive fork means an analysis exists. Existing atlas reports must be recognized before the first shortlist is produced. If the required atlas inventory cannot be loaded, stop selection rather than risk paying for duplicate analyses; feed ingestion may still proceed.

### B. Cheap metadata collection

Collect/cache repository and owner metadata without cloning. Process under a request and time budget; spread the first large backlog across resumable runs if necessary. Share owner lookups between candidates belonging to the same owner.

Record stars, forks, issue and PR counts separately where available, creation/push dates, owner type and creation date, archive/fork status, and licence information. Additional bounded requests can inspect recent commits, contributors, external PRs, and other public projects/contributions.

Do not crawl every author's entire GitHub history or paginate every commit simply to obtain an exact count. A sampled count with an explicit coverage label is acceptable. Account age measures the account, not developer experience; organization age is not maintainer experience. Public repository ownership is different from contributing to other projects. Private history is unavailable, not absent.

### C. Bounded evidence inspection

Choose an initial maximum of 100 repositories per day for closer inspection. This is a configurable cost limit, not a claim that exactly 100 will yield 20 eligible projects. Allocate approximately 80% to promising metadata-ranked candidates and 20% to deterministic rotating exploration among the remainder, so unknown/new projects can be inspected. Persist this budget across reruns.

Pin the default-branch commit once. Read the repository tree and selected text blobs at that commit: README, manifests, test configuration, CI workflow, a few test files, and a few relevant implementation files. Cache small derived facts; discard the fetched source bodies after assessment.

A keyword match is not sufficient evidence of atlas relevance. Assess whether the implementation persists agent-relevant claims or memories across sessions with an identity that can support correction. Follow the atlas's actual inclusion policy; basic persistence, a task queue, a context buffer, or an unrelated document index is not automatically in scope. Do not require a working correction mechanism as an admission gate: its absence can be a finding of the full analysis.

### D. Gate, rank, and select

Automatic eligibility requires:

1. Sufficient evidence that the repository is in atlas scope.
2. Readable implementation beyond a placeholder, promotional README, or unmodified template.
3. Substantive committed test evidence as defined below.
4. No existing completed analysis or active selection that makes it a duplicate.

For eligible projects, rank on inspection value and evidence, not popularity alone. Proposed initial 100-point rubric:

| Component | Maximum | Interpretation |
| --- | ---: | --- |
| Test evidence | 30 | Meaningful assertions and relevant behavior; memory-specific tests and CI execution earn more |
| Implementation substance | 25 | Concrete memory implementation with inspectable paths, beyond boilerplate |
| Contribution and maintenance evidence | 20 | Substantive external participation and development across time, with known bots separated |
| Potential value to the atlas | 15 | Evidence of a distinctive mechanism or an explicit gap in current atlas coverage |
| Adoption and public track record | 10 | Capped contribution from stars/forks and visible prior work; volume cannot dominate |

Implement explicit anchored sub-rules in a versioned policy configuration and show the awarded points. These weights are starting assumptions to calibrate, not validated predictions. Use a configurable minimum score, initially 60, in addition to the mandatory gates. Unknown novelty must not become an invented claim. If corpus comparison is unavailable, report that limitation and award no unsupported novelty points.

Default daily admission limit: **20 new selections**, timezone **Europe/Copenhagen**. Also default to **20 outstanding selections/analyses** across dates. Available slots equal the smaller of the remaining daily admission allowance and remaining outstanding capacity. Fewer than 20 is a valid result.

Persist slot allocation transactionally with uniqueness constraints. Repeated or overlapping invocations cannot exceed either limit. Freeze a date's shortlist when selection is finalized; normal reruns regenerate the same output. Do not automatically replace rejected or cancelled selections with additional candidates that day. Use the current configured day for live selection; displaying an old report must not create historical admissions. Use deterministic tie-breaking by score, first-seen time, and canonical repository identity.

The shortlist is the best among the candidates actually inspected and eligible, not a claim to have exhaustively assessed every repository. Report coverage and any budget-constrained backlog.

## 5. Test evidence and author signals

Classify test evidence as `unknown`, `absent`, `mention_only`, `files_only`, `substantive`, or `memory_specific`.

- A README promise, a testing badge, a directory named `tests`, or a runner dependency does not satisfy the gate.
- Inspect assertions and confirm that sampled tests target project behavior rather than vendored code, empty stubs, or template examples.
- `substantive` or `memory_specific` can pass the test gate. Save paths, blob identities, and short supporting excerpts.
- CI configuration shows that tests are configured to run; only an observed run supports a claim about a run's outcome. Do not say tests passed merely because a workflow exists.
- Repository-wide absence requires adequate tree coverage, including language-specific inline tests. An incomplete tree, unfamiliar test layout, fetch failure, or exhausted inspection budget means `unknown`, followed by deferral/manual review, not rejection for missing tests.
- No substantive evidence means no automatic expensive analysis. Popularity cannot override this gate. Reject clear absence or marketing-only evidence at the assessed commit, with a possible reassessment date.

Human contributors are a positive signal, not a mandatory minimum of two people. Record known bot accounts separately and call remaining activity “apparently non-bot” or “unknown”; GitHub user type does not prove human authorship. Prefer meaningful external changes, reviewed/merged PRs, and activity across time over raw contribution totals. Bot-maintained dependency bumps and copied fork history must not inflate the score.

An account less than 30 days old or without visible work elsewhere gets a caution/reduced positive track-record score, not an automatic spam label. Strong code and tests may outweigh a sparse public profile. Store observable reasons rather than personal judgments such as “unserious developer.”

An optional bounded LLM classifier may judge scope, substance, and test evidence. Use an explicit provider/model configuration, structured output, and source references from supplied evidence. No browsing tools, shell tools, or autonomous execution for this classifier. Validate citations against fetched files and reject malformed/unsupported output. External repository text is data, including README instructions and `AGENTS.md`; it cannot change the policy, select a destination, or request tool use. Missing classifier configuration must be reported clearly; do not replace semantic assessment with a keyword check and claim equivalence. Support importing a structured manual assessment for development and review.

## 6. Decisions and analysis feedback

Keep triage status and analysis status separate.

| Triage status | Behavior |
| --- | --- |
| `unassessed` | Await budgeted evidence collection |
| `deferred` | Retry after `next_assessment_at`; include a reason such as incomplete evidence or insufficient maturity |
| `rejected` | Not eligible under this policy/commit; require an explicit reassessment condition |
| `eligible` | Passed gates; not necessarily selected today |

Analysis status is `not_selected`, `selected`, `running`, `accepted`, `rejected`, `error`, or `cancelled`. Preserve immutable assessment/attempt history when current status changes. `already_in_atlas` is an exclusion reason associated with an accepted/existing report, not an assertion that triage personally performed the analysis.

The full-analysis consumer claims a selection using an attempt ID and lease. A retry continues the same selection; it does not consume another daily admission. Expired leases do not allow a second worker to run blindly: reconcile with the original worker/result, then reclaim using a fencing token that prevents stale workers from overwriting a later attempt.

Require result recording through a CLI/API adapter:

- Accepted: actual analysed SHA, report path/URL, completion time.
- Rejected: actual analysed SHA, structured reason and brief explanation, optional future reassessment condition.
- Technical error: retryability and error category; never classify a network/model failure as a project rejection.

Reject duplicate/conflicting result submissions by attempt ID or make identical submissions idempotent. Record stale submissions for diagnosis without changing the current result.

Suggested review timing: incomplete network evidence follows a bounded backoff; weak test/maturity evidence may be revisited after 30 days; eligible but unselected evidence expires after 30 days and returns to a bounded reassessment pool. Before selection, require an assessment no older than seven days and check that the proposed commit still matches it, or reassess within budget. A changed README alone does not automatically reopen an analysis rejection. Known accepted reports remain excluded until a separate atlas reanalysis policy requests otherwise.

## 7. Disk use and cleanup are acceptance requirements

The candidate index itself is small. Repository downloads, dependency caches, logs, and retained source snapshots are the disk risk. The maintainer does not reboot daily, so operating-system temporary cleanup is not an acceptable lifecycle strategy.

### No repository checkout in triage

- **Never `git clone`, download repository archives, extract tar/ZIP files, initialize submodules, or fetch Git LFS objects.** There is no automatic clone fallback.
- Never install dependencies, run builds/tests, execute hooks, import downloaded Python, or open fetched content as active HTML. Test inspection is static.
- Read tree metadata and a bounded number of text blobs through GitHub APIs. Do not materialize a repository directory tree, even from selected blobs.
- Stream responses with actual-byte limits and decoded/decompressed size limits; do not trust Content-Length or predeclared blob sizes. Reject binary and excessively large content.
- Use bounded in-memory buffers by default. Drop repository source bodies at the end of each assessment. Retain only capped excerpts, paths, hashes, and derived facts in durable state.
- Close response streams and handles on success, errors, timeouts, and cancellation. Avoid hidden disk caching by HTTP/LLM libraries.

Initial configurable limits, with enforcement tests:

| Resource | Default limit |
| --- | ---: |
| Candidate feed, decoded | 16 MiB |
| One source-text blob, decoded | 256 KiB |
| Source-text blobs per inspected repository | 12 |
| Source-text total per inspected repository | 2 MiB |
| One tree response, decoded | 10 MiB |
| All response bodies per inspected repository | 16 MiB |
| Per-repository requests, including retries | 30 |
| Global GitHub requests per day, including retries | 3,000 |
| Concurrent repository assessments | 1 |
| Active evidence inspection per repository | 90 seconds |
| Classifier calls per repository | 1 plus at most 1 bounded retry |
| Classifier input/output | 12,000 / 2,000 tokens per call |
| HTTP connect/read timeout | 5 / 20 seconds, also subject to the stage deadline |
| Persistent response cache | 64 MiB, metadata only, seven-day TTL, LRU eviction |
| Optional scratch contents | 32 MiB total |
| Logs | 16 MiB total, rotation and redaction |
| Entire application state directory | 256 MiB soft stop, including DB journals and outputs |

Maintain a separate configurable classifier daily cost/token cap. Stop starting new requests when a budget is exhausted, save progress, and report a deferred backlog. Never interpret a resource cap as proof that a project is poor. Do not wait through long rate-limit windows while retaining repository material; discard the buffers, record retry time, and end the attempt.

These are application ceilings, not promises that all incoming repositories can be fully inspected in a day. Classifier transport must receive cancellation/deadlines; a timed-out call must not remain as a detached background request. Use an interruptible worker boundary where the client cannot enforce this.

### If any dependency needs a temporary file

Prefer removing that need. Otherwise, use only a dedicated application-owned scratch root under the configured state directory, never random checkout folders in shared `/tmp`.

1. Acquire an application lock before scratch recovery or processing. On macOS/Linux use an OS-backed lock so a crashed process releases it; a leftover PID file alone is not a reliable lock.
2. Verify the scratch root is owned/marked by this application and is not a symlink. Refuse dangerous roots such as `/`, the home directory, the state root itself, or the system temporary root.
3. Create a randomly named per-assessment child directory with restrictive permissions. Names and paths must not come from repository text.
4. Write only bounded opaque temporary files, never files at repository-supplied paths. Do not follow symlinks.
5. Remove the per-assessment directory in `finally`, after closing all handles, for success, rejection, exception, timeout, and ordinary cancellation.
6. After acquiring the lock on the next invocation, remove marked abandoned scratch children before processing anything. With one active process, previous marked children are orphaned. Do not recursively clean unrelated paths or follow symlinks outside the owned tree.
7. Expose `triage cleanup` for explicit cleanup without running discovery or classification. It follows the same lock and ownership rules.
8. If deletion fails, stop new repository processing, report the exact path and error, and retry cleanup on the next invocation. Do not silently accumulate failures.

No process can guarantee `finally` after SIGKILL or power loss. Normal operation must leave zero per-repository scratch files; abnormal termination must leave only bounded, identifiable scratch that the next run or `cleanup` removes. This limitation must be stated accurately in the README. The default in-memory path leaves no repository bodies on disk even in that case, apart from deliberately retained short evidence excerpts.

Enforce cache eviction, log rotation, and scratch cleanup during every run, not only at machine startup. SQLite compaction/checkpointing must be bounded and account for journals and transient extra space. Stop before further state growth when the state ceiling cannot be met by evicting disposable material; **never delete decisions, results, or selections to make room**. Explain how to export/archive state deliberately. The database and output files are durable metadata, not cleanup targets.

Full atlas analysis is a separate owner of any eventual clone. Include cleanup responsibilities in the handoff contract: a downstream analyser must delete its own temporary checkout on completion and recover its own abandoned workspaces. Do not claim this triage implementation cleans another program's directories or weaken a pre-existing atlas archival policy.

## 8. Fetching, failure handling, and trust boundaries

Use read-only GitHub operations and credentials from configuration/environment. Never embed tokens in URLs, logs, database fields, classifier prompts, or exports. Construct API URLs from validated GitHub identities; do not follow arbitrary source links or send Authorization headers to a redirected host. Use a narrowly defined trusted GitHub-host policy for any necessary content retrieval.

Honor Retry-After and GitHub primary/secondary rate-limit headers. Persist exhausted budgets and retry timestamps so reruns cannot bypass limits. Isolate per-repository failures; preserve successfully committed assessments. Distinguish 403/429 limits, permission failures, transient errors, unavailable repositories, and empty repositories. A single 404 is not evidence that the author is a spammer or the repository has no tests.

GitHub recursive tree responses can be truncated. Follow bounded relevant subtrees or classify coverage as incomplete; never infer absence of tests from a truncated tree. Issues endpoints can include PRs, so count them separately. Contributor/commit samples must preserve their scope and uncertainty. API evidence is time-sensitive and can change independently of the pinned source commit.

## 9. CLI and user-facing outputs

Proposed interface; adapt naming to the target project, preserve semantics:

```text
triage init                              # explicitly create persistent state
triage ingest                            # fetch configured upstream source
triage ingest --input /path/candidates.jsonl
triage assess                            # resumable, under persisted budgets
triage select                            # finalize today's bounded selection
triage run                               # ingest, assess, select, write reports
triage status                            # counts, capacity, last run, disk use
triage explain OWNER/REPO                 # evidence, decision history, next action
triage claim SELECTION_ID                # obtain an analysis attempt/lease
triage result ATTEMPT_ID --input result.json
triage cleanup
triage export --output backup.jsonl
triage restore --input backup.jsonl       # validated restore; no silent merge/reset
```

Normal commands must fail clearly if established state is missing or corrupt. Do not silently create a fresh database and reselect old projects. Explicit initialization and validated restores are separate actions. Backups must preserve decision history, aliases, current state, selections, budget usage, leases, schema and policy references needed for safe continuation; do not export credentials or raw source caches. An active lease restored from backup requires reconciliation before claim reuse.

Write `shortlists/YYYY-MM-DD.json` and a matching Markdown digest under the configured output directory. They are generated from the committed selection transaction using temporary output files plus atomic rename. If report writing fails, rerunning must reproduce the committed list without creating new admissions. Inspect disk limits before writing. Do not interpret the daily digest as a replacement for the cumulative source or state.

For each selected candidate include rank, GitHub URL, pinned commit, score breakdown, a short “why selected,” test evidence paths, key metrics with uncertainty, and selection ID. Include batch-level import/inspection coverage, new versus historical counts, skipped categories, remaining capacity, deferred counts, source freshness, and disk use. Clearly distinguish zero eligible projects from an unavailable source/classifier or an exhausted budget.

Do not schedule unattended jobs, publish results, create issues, or push commits as part of implementing this specification unless the maintainer separately asks. The first live run should demonstrate a small bounded assessment batch and its cleanup behavior.

## 10. Implementation plan

### Phase 1 — Reliable intake and durable state

Inspect atlas instructions and existing report metadata. Add configuration, explicit state initialization/migrations, source fetching/local input, schema-tolerant import, canonical identities, and atlas membership import. Add the owned scratch manager and byte-limited HTTP reader at this stage so later collectors cannot bypass them. Implement export/restore and a basic `status` command.

Deliverable: importing the existing Scout file twice produces one candidate per identity, keeps `filed` candidates eligible for assessment, preserves decisions when source entries disappear, and leaves no untrusted checkout on disk.

### Phase 2 — Evidence collection and rules

Implement metadata caching, bounded tree/blob inspection, owner/contribution sampling, test detection across likely project languages, evidence coverage, and rule-based gates. Implement the optional structured classifier adapter and manual-assessment import. Add persisted API/classifier/time budgets and deferred retries. Make paths and excerpts available to `explain`.

Deliverable: a bounded sample yields auditable eligible/rejected/deferred decisions; incomplete evidence is distinguishable from negative evidence. No fetched code executes and no clones or archives are created.

### Phase 3 — Selection and analysis feedback

Implement deterministic ranking, outstanding-capacity accounting, one finalized shortlist per local day, transactional reservations, report generation, claims/leases/fencing, and accepted/rejected/error result handling. Add the atlas result adapter without implementing the full analysis itself.

Deliverable: repeated and concurrent runs cannot release more than 20 candidates or reselect completed/in-progress work. An atlas rejection persists without changing Scout's file.

### Phase 4 — Failure recovery and disk verification

Exercise normal completion, interrupts, injected connection errors, timeouts, malformed source/classifier responses, budget exhaustion, cleanup permission failures, abrupt process termination, missing/corrupt state, and restart. Test lock contention, safe orphan removal, and output reconstruction after a post-transaction crash.

Deliverable: a reproducible 1,400-candidate fixture run demonstrates bounded buffers, disk quotas, resumability, and zero leftover per-repository scratch after normal completion. Use simulated API responses; this test must not fetch 1,400 real repositories.

### Phase 5 — Calibrate and hand off

Manually review a small labelled sample containing useful low-star projects, established projects, irrelevant keyword matches, README-only claims, actual tests, template tests, new owners, known bots, and API failures. Compare classifier/gate decisions with that review, adjust policy anchors, and report false positives and valuable exclusions. Do not use stars as the ground-truth label. Treat already-reviewed atlas projects as examples to judge, not automatic positives for the new testing policy.

Document installation, token configuration, source/state locations, one-off and recurring operation, disk budgets, cleanup, backups, result recording, and resuming interrupted work. Provide a sample digest and measured resource usage from the small live pilot. State remaining limitations.

## 11. Required acceptance tests

- Source rewriting/reordering and repeated imports do not duplicate candidates. Non-repository records are ignored; minimal `filed` records are processed.
- Rename/transfer aliases preserve decisions; repository-name reuse with a new ID is separate.
- Neither triage rejection nor analysis rejection modifies the source input. Input bytes/hash remain unchanged.
- Source removal, HTTP failure, malformed lines, and truncated downloads cannot erase local state or be reported as a successful empty feed.
- Existing atlas reports, completed rejections, active selections, and running analyses are not selected again.
- Substantive tests pass the gate; README mentions, test stubs, and copied examples do not. Inline tests can be recognized. Truncated trees and unsupported layouts produce uncertainty.
- Bots do not count as confirmed human contributors. Organization age, missing private history, and unknown counts are not misrepresented.
- README prompt injection cannot change rules, access secrets, cause commands to execute, or redirect network requests.
- A rerun, concurrent run, local midnight/DST transition, crash during selection, and regenerated output preserve daily and outstanding limits. A changed timezone cannot silently reset an active day's allowance.
- Conflicting/stale analysis results cannot overwrite a current attempt; technical errors do not become quality rejections.
- Budgets count failed requests/retries and survive restart; a quota exhausted yesterday can reset at the correct configured boundary without resetting candidate decisions.
- Oversized/misdeclared/chunked/compressed responses stop at enforced limits. Rejected blobs never reach the classifier.
- Normal, exceptional, timeout, and interrupt paths leave no assessment scratch. SIGKILL leftovers are bounded and removed on the next locked startup. Symlinks and unowned paths are never traversed/deleted by cleanup.
- Cleanup failure stops further repository processing and identifies the remaining path. Logs/caches remain bounded over repeated simulated days; persistent outcomes are retained.
- Export/restore preserves admissions and analysis history, and missing/corrupt state never silently starts a new selection ledger.

## 12. Reference documentation

- Candidate feed: <https://github.com/Daily-Nerd/scout/blob/main/data/candidates.jsonl>
- Atlas inclusion policy: <https://neoneye.github.io/agent-memory-atlas/compare/>
- Atlas report method: <https://neoneye.github.io/agent-memory-atlas/methodology/per-repo-report-format/>
- GitHub tree API and truncated-tree behavior: <https://docs.github.com/en/rest/git/trees#get-a-tree>
- GitHub rate-limit handling: <https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api>
- GitHub issues/PR distinction: <https://docs.github.com/en/rest/issues/issues#list-repository-issues>

The supplied upstream candidate page and raw URL could not be fetched by the browsing tool when drafting this document. The source address is provided by the maintainer; the schema and size observations above come from the saved snapshot. Verify live accessibility during implementation without silently substituting a different upstream source. An optional local-file input is useful for fixtures and explicitly configured recovery, but no particular local checkout is required.

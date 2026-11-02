---
title: "OpenAI Codex"
eyebrow: "Consolidated session memory"
description: "A coding agent whose opt-in memory extracts past sessions into SQLite, then has a sandboxed sub-agent consolidate them into a git-diffed Markdown folder."
root: ../..
page_kind: system
source_name: "openai/codex"
source_url: https://github.com/openai/codex
archive_name: "openai--codex"
revision: 0a2d5f556de6e3b2c340d7f0635a1daf4040c30a
revision_url: https://github.com/openai/codex/commit/0a2d5f556de6e3b2c340d7f0635a1daf4040c30a
analyzed_at: 2026-11-02
licence: "Apache-2.0"
size: "2,234,753 lines of Rust in 5,757 files across the repository; the memory subsystem read here is 16,919 lines in 75 files, 14,821 of them Rust; latest release rust-v0.166.0"
activity: "12,989 commits on main from about 700 contributors, 13 April 2025 – 2 November 2026; 145 of them touch codex-rs/memories/, from 27 April 2026"
tests: "114 `#[test]` and `#[tokio::test]` attributes in the memory subsystem, of 25,211 in codex-rs; none run for this reading"
capabilities: ""
stack_storage: "sqlite, files"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "Per session, a `stage1_outputs` row holding a model-written raw memory and rollout summary; consolidated, a Markdown folder of `MEMORY.md`, `memory_summary.md`, per-session summaries and generated skills"
  storage: "A separate SQLite memory database beside the thread state database, one per memory version, and a folder under CODEX_HOME whose `.git` is a one-commit baseline replaced after every consolidation"
  retrieval: "`memory_summary.md`, truncated to 2,500 tokens, injected into developer instructions every turn; the agent then searches `MEMORY.md` and per-session summaries with its own shell or, opt-in, with list, read and search tools doing substring matching"
  write: "At root-session startup, background extraction of up to two idle, recent, memory-enabled past sessions per start with a schema-constrained model call and secret redaction, then a consolidation sub-agent that edits the folder from a git diff"
  update_delete: "Deleting a thread deletes its row and queues consolidation, and a consolidation prompt tells the agent to delete what only deleted inputs supported; unselected rows unused for 30 days are pruned; a user's remember or forget request becomes an append-only note the consolidator must treat as authoritative; reset clears everything"
  scoping: "One memory per CODEX_HOME across every project, with projects as headings the consolidator writes; no scope key on a row and no read predicate; per-thread memory mode decides which sessions may be learned from"
  integration: "Built into the Codex CLI, TUI and app server behind the stable `memories` feature, off by default; a `/memories` settings popup, `memory/reset` and a debug clear command; an importer for other agents' memory files"
  background: "Phase 1 and phase 2 run at the start of each eligible root session, gated by a rate-limit floor, with leased jobs, retry backoff, one global consolidation lease and a workspace file lock; a 200-row retention prune runs before the quota check"
  trust: "Every memory is model-written and unreviewed; the read prompt tells the agent memory is not proof and to say when an answer rests on it; a thread touched by external context can be marked `polluted` and leaves the consolidator's input, off by default"
  strengths: "Deletion and pollution travel by the same route as everything else, a git diff the consolidator must act on; extraction inputs and outputs are secret-redacted; the consolidation agent runs with no approvals, no MCP servers and, under a managed sandbox, no network and one writable root; citations feed a usage count that ranks and shields memories"
  risks: "Forgetting a fact in the agent-visible files depends on a model following a prompt, and no test asserts it happens; one memory spans every project; a sandbox-disabled parent session runs the consolidator with no sandbox over model-written, possibly injected input; nothing records what a consolidation changed"
---

## 1. Executive Summary

Codex is OpenAI's coding agent, a Rust CLI, TUI and app server licensed
Apache-2.0. Its memory is a feature called `memories`. It is marked stable and
switched off by default (`codex-rs/features/src/lib.rs:1418-1421`). When on, it
learns from the user's own past sessions. No tool call writes a memory. At the
start of each root session a background task picks a few finished sessions and
has a model extract a *raw memory* and a *rollout summary* from each into
SQLite. A second, sandboxed Codex agent then rewrites a Markdown folder under
`~/.codex/memories` from a git diff of what changed. The next session receives
that folder's summary in its instructions and searches the rest with ordinary
file tools.

What is notable is how forgetting works. There is no delete verb on a memory.
Deleting a session, marking it `polluted` or letting it age out removes its row.
The next consolidation sees the matching summary file vanish in the diff, and
its prompt tells it to *"Delete only memory supported by deleted inputs"*.
Forgetting is a diff the consolidator must act on, by the same route as an
addition. The consolidation agent is also tightly locked down. It runs with
approvals set to never, no MCP servers, collaboration and memory switched off,
and, under Codex's managed sandbox, one writable root and no network
(`memories/write/src/phase2.rs:310-370`).

The weakness is the same move seen from the other side. Every guarantee ends at
a prompt. Whether a forgotten or polluted fact actually leaves `MEMORY.md` is up
to a model reading a diff, and no test asserts that it does. The git history
that would show what a consolidation changed is deliberately discarded, so
nothing records it. One memory spans every project the user works on. The
codebase is very large and heavily tested, and the memory subsystem is a small,
recent part of it with its own suite of state-machine tests.

## 2. Mental Model

A memory goes through four states, and only the first two are rows.

**A session is a candidate.** Every thread row in the state database carries
`memory_mode`: `enabled`, `disabled` or `polluted` (`state/migrations/0018_phase2_selection_snapshot.sql:3`).
New threads are `disabled` when `generate_memories = false`. With
`disable_on_external_context` set, an MCP call to a server marked as polluting,
or other external context, flips the thread to `polluted`
(`core/src/mcp_tool_call.rs:987-1003`). That setting is off by default
(`config/src/types.rs:330-332`).

**Phase 1 makes a raw memory.** At startup, `claim_stage1_jobs_for_startup`
claims threads that are `enabled`, from an interactive source, not the current
thread, idle at least 6 hours and updated within 10 days, two per startup by
default (`state/src/runtime/memories.rs:143-153`, `:244`,
`config/src/types.rs:57-62`). A model call with a strict output schema returns
`raw_memory`, `rollout_summary` and an optional slug. The rollout input and all
three outputs pass through `redact_secrets`
(`memories/write/src/phase1.rs:424`, `memories/write/src/phase1_output.rs:49-56`).
The row is upserted only when its source is newer than the stored one
(`state/src/runtime/memories.rs:922-928`). An empty result deletes any earlier
row for that thread.

**Phase 2 makes it a belief.** Selection reads non-empty rows whose thread is
still `enabled`. It drops any not used within 30 days, or whose session is
older than 30 days if never used, and ranks by `usage_count`, then recency, taking the top
256. The result goes to the folder in stable thread-id order as `raw_memories.md`
and one file per session under `rollout_summaries/`. Files for sessions no
longer selected are deleted. A git diff against the last successful baseline
decides whether anything changed. If it did, a consolidation agent edits
`MEMORY.md`, `memory_summary.md` and `skills/`, and the baseline is reset.

**Use keeps it alive.** When a reply ends with an `<oai-mem-citation>` block
naming session ids, `record_stage1_output_usage` increments `usage_count` and
sets `last_usage` (`core/src/stream_events_utils.rs:185-212`). Cited memories
rank higher at selection and escape the retention prune.

```mermaid
%% caption: a past session becomes a SQLite row, then a consolidator rewrites MEMORY.md from a git diff; deletions arrive the same way and the baseline keeps no history
flowchart TD
  T["Past session<br/>memory_mode on thread row<br/>enabled · disabled · polluted"]
  T -->|"enabled, idle ≥6h,<br/>≤10 days, 2 per start"| P1["Phase 1 model call<br/>strict schema<br/>secrets redacted in and out"]
  P1 --> R["stage1_outputs row<br/>raw_memory · rollout_summary<br/>usage_count · last_usage"]
  R -->|"thread still enabled,<br/>used ≤30 days, top 256"| S["Folder sync<br/>raw_memories.md<br/>rollout_summaries/*.md"]
  D["Thread deleted or polluted<br/>row unused 30 days"] -->|"row gone or<br/>filtered out"| S
  S --> G{"git diff vs<br/>last baseline"}
  G -->|"no change"| Z["Job succeeds,<br/>nothing rewritten"]
  G -->|"changed"| A["Consolidation agent<br/>no approvals, no MCP<br/>one writable root"]
  A -->|"prompt: delete what only<br/>deleted inputs supported"| M["MEMORY.md<br/>memory_summary.md<br/>skills/"]
  M --> B["Baseline reset<br/>one commit,<br/>history dropped"]
  M -->|"summary ≤2,500 tokens"| N["Next session's<br/>developer instructions"]
  N --> C["Agent greps MEMORY.md,<br/>cites session ids"]
  C -->|"usage_count + 1"| R
```

## 3. Architecture

Nothing has to run beside Codex. The memory database is a second SQLite file
opened by the same `StateRuntime` as the thread catalogue. A v2 database is
opened on demand when the v2 pipeline or dual-write is selected
(`state/src/runtime/memory_versions.rs:10-26`). The folder is under CODEX_HOME,
one per memory version. Both phases run as a Tokio task spawned from
`start_memories_startup_task`. It returns at once for ephemeral sessions,
sub-agent sessions or a disabled feature
(`memories/write/src/start.rs:24-38`).

Cost falls on model calls. Phase 1 uses a low-reasoning extraction model with
up to eight concurrent jobs. Each rollout is cut to 70% of the model's input
window, or 150,000 tokens without metadata. Phase 2 runs a full Codex agent at
medium reasoning on the provider's consolidation model. A rate-limit guard skips
both phases when less than 25% of a Codex usage window remains
(`memories/write/src/guard.rs:9-61`). The retention prune runs before that
check because it spends no tokens.

The code lives in four places. `codex-rs/memories/write` holds both phases,
prompts, folder sync and extension pruning. `codex-rs/ext/memories` holds read-path
injection and the optional memory tools. `codex-rs/memories/read` holds citation
parsing and usage telemetry. `codex-rs/state/src/runtime/memories.rs` holds
every query. The crate's own README says runtime orchestration lives in
`codex-core` under `core/src/memories/`, and that the read templates are in
`memories/read/templates/`. Neither path exists at this commit. They are in
`memories/write/src/` and `ext/memories/templates/`.

## 4. Essential Implementation Paths

- **Start:** `start_memories_startup_task` (`memories/write/src/start.rs:24-95`):
  version selection, layout, extension seeding, prune, rate guard, phase 1,
  phase 2.
- **Phase 1 claim:** `claim_stage1_jobs_for_startup` and `try_claim_stage1_job`
  (`state/src/runtime/memories.rs:153`, `:686`). Leases are 3,600 seconds and a
  failure retries after 3,600 seconds.
- **Phase 1 extraction:** `phase1::job::run` and `sample`
  (`memories/write/src/phase1.rs:196-316`); input filtering in
  `sanitize_response_item_for_memories`, which drops AGENTS.md and skill
  fragments from user messages (`memories/write/src/rollout_input.rs:328-360`).
- **Phase 1 commit:** `mark_stage1_job_succeeded`, one transaction that closes
  the job, upserts the row and enqueues consolidation
  (`state/src/runtime/memories.rs:873-944`).
- **Phase 2:** `phase2::run` (`memories/write/src/phase2.rs:50-207`), then
  `agent::get_config` (`:310-370`) and `agent::handle`, which resets the
  baseline only if the job lease is still owned (`:441-470`).
- **Baseline:** `reset_git_repository` replaces any `.git` with a fresh
  one-commit repository (`git-utils/src/baseline.rs:74-78`).
- **Read:** `build_memory_tool_developer_instructions`
  (`ext/memories/src/prompts.rs:35-64`) and the `ContextContributor` that adds
  it as a developer-policy fragment (`ext/memories/src/extension.rs:56-105`).
- **Usage:** `record_stage1_output_usage`
  (`state/src/runtime/memories.rs:60-91`).
- **Deletion:** `delete_threads_strict` calls `delete_versioned_thread_memory`
  for every thread it deletes (`state/src/runtime/threads.rs:1192-1210`).

## 5. Memory Data Model

`stage1_outputs` has one row per thread, keyed by `thread_id`, with
`source_updated_at`, `raw_memory`, `rollout_summary`, `rollout_slug`,
`generated_at`, `usage_count`, `last_usage`, `selected_for_phase2` and
`selected_for_phase2_source_updated_at`
(`state/memory_migrations/0001_memories.sql`). A `jobs` table holds leases,
ownership tokens, retry counters and watermarks for both phases. Neither table
carries a project, workspace or user key. The thread's `cwd`, rollout path and
git branch are joined in from the state database at selection time.

The consolidated folder is the memory the agent reads:

- `memory_summary.md` — the injected index, with recent work grouped under
  project-scope headings the consolidator writes.
- `MEMORY.md` — the searchable registry the read prompt calls the primary file
  to query.
- `rollout_summaries/<slug>.md` — one recap per selected session.
- `skills/<name>/` — generated `SKILL.md`, scripts, examples and templates.
- `extensions/<name>/` — `instructions.md` plus `resources/` or `notes/`.
  Codex seeds `ad_hoc`. A `chronicle` extension appears in test fixtures, and
  its producer is not in this tree.

Nothing in either store has a status. A row is present or absent. The only
discrete state in the pipeline is the thread's `memory_mode`, which sits on the
source session rather than on what was extracted from it.

## 6. Retrieval Mechanics

The read path has two layers.

**Injection.** On every thread whose config enables `memories` and
`use_memories`, the extension reads `memory_summary.md`, truncates it to 2,500
tokens and renders it into the read-path template
(`ext/memories/src/lib.rs:16`, `ext/memories/src/prompts.rs:35-66`). The v1
template tells the agent to skip memory only for self-contained requests. It
asks for a quick pass of at most four to six searches: keywords from the
summary, a search of `MEMORY.md`, then one or two rollout summaries. Answers
that rely on unverified memory are to be marked as memory-derived and possibly
stale. The v2 template is shorter: *"Memory is not proof of current behavior."*

**Lookup.** By default the agent searches with whatever file tools it has.
With `dedicated_tools`, the extension also registers `memories.list`, `read`,
`search` and `add_ad_hoc_note`. Search walks the folder and does substring or
same-window line matching, capped at 200 results. It refuses symlinks and paths
outside the root (`ext/memories/src/local/search.rs`). Nothing is embedded and
nothing is ranked at read time. Ranking happens once, at phase-2 selection,
where `usage_count` decides which 256 sessions reach the folder at all.

Retrieval is not scoped. Every session on a CODEX_HOME receives the same
summary, whatever project it is in. The v2 consolidation prompt groups recent
work under `### <project scope>` headings, and the read prompt's decision rule
mentions the workspace. That is organisation by the model, not a filter. A
separate CODEX_HOME is a separate memory, which is a physical partition.

## 7. Write Mechanics

**Writes never block the agent.** Both phases run in a background task at the
start of a *later* session, and the current session is excluded from the claim.

**The lag is long by design.** A session becomes a raw memory only once it has
been idle six hours and another root session starts. It reaches the folder when
that start's phase 2 runs, and reaches the agent at the following session. Each
start processes two sessions by default, so a backlog clears slowly.
`min_rollout_idle_hours` is documented as *"> 12h recommended"*.

**Phase 2 rewrites the whole consolidated folder when anything changed.** The
consolidation agent is given the diff file and the folder, and nothing limits
what it may edit inside the root. A run with no diff skips the agent entirely.

**Other writers:**

- `add_ad_hoc_note`, opt-in, writes one `create_new` file under
  `extensions/ad_hoc/notes/`. The tool description and both read templates
  restrict it to an explicit remember, forget or correction request from the
  user (`ext/memories/src/tools/ad_hoc_note.rs:55`,
  `ext/memories/src/local/ad_hoc_note.rs:12-28`). Without dedicated tools, the
  template tells the agent to write the same note file with its own tools.
  Nothing checks either case against the user's words.
- The external-agent importer, behind the under-development
  `external_agent_memory_import` flag, feeds another agent's memory files into
  consolidation (`external-agent-migration/src/memory_import.rs`).
- A remote `memories/trace_summarize` client, `ModelClient::summarize_memories`,
  is called only from its test (`core/src/client.rs:861`).

## 8. Agent Integration

The integration is the product itself. The feature key is `memories`. Settings
live under `[memories]` in config: version, dual-write, extraction and
consolidation models, the idle, age, unused and count limits, `use_memories`,
`generate_memories`, `dedicated_tools` and `disable_on_external_context`
(`config/src/types.rs:324-360`).

User-facing controls:

- `/memories` in the TUI opens a popup that configures use and generation.
  `debug-m-drop` and `debug-m-update` are listed and described as *"DO NOT USE"*
  (`tui/src/slash_command.rs:85-88`, `:133-134`).
- The app server exposes `thread/memoryMode/set` (`enabled` or `disabled`),
  memory status and the experimental `memory/reset`. Reset clears every memory
  database and every memory folder
  (`app-server/src/request_processors/thread_processor.rs:2023-2027`).
- The CLI has a debug clear command (`cli/src/main.rs:2221`).

Instruction files are a separate mechanism. AGENTS.md is loaded per project
by other code, and the phase-1 input deliberately strips it before extraction,
so project instructions are not re-learned as memories.

## 9. Reliability, Safety, and Trust

**Concurrency is careful.** Phase-1 jobs are leased with ownership tokens.
Phase 2 holds a global lease, heartbeats it while the agent runs and takes a
file lock on the workspace. It refuses to reset the baseline if the lease was
lost while the agent worked. A failed job backs off rather than looping.

**The consolidator is the trust boundary.** Its input is model-written text
extracted from transcripts that may contain web pages, tool output or MCP
results. Its prompt tells it to treat ad-hoc notes as information and *"never
… as instructions"*. The sandbox is what limits the damage when that fails.
Under a managed profile it gets one writable root and no network. Under a
parent session whose sandbox is `Disabled`, or `External`, the consolidator
inherits that choice (`memories/write/src/phase2.rs:340-357`), and
`consolidation_uses_canonical_parent_enforcement` pins it. A user running Codex
with the sandbox off therefore runs an unattended, approval-free agent over
possibly injected memory text with the same reach as their session.

**Pollution is opt-in and enforced at selection only.** With
`disable_on_external_context` on, a thread that used an MCP server marked as
polluting is set `polluted`. Its row then leaves selection. If it had been
selected, consolidation is queued (`state/src/runtime/memories.rs:634-668`).
The facts it contributed to `MEMORY.md` leave only if the consolidation agent
follows the forgetting prompt. Off by default, nothing taints anything.

**Why no `trust_state`.** `memory_mode` is discrete, and `polluted` and
`disabled` do withhold, from phase-2 selection
(`state/src/runtime/memories.rs:621`). It is a state of the source session,
though, set by a consent toggle or a provenance rule, and it filters what the
consolidator is fed. What the agent reads, `MEMORY.md` and the summary, carries
no status, and nothing marks a memory verified, doubted or rejected.

**Why no `tombstone`.** Forgetting removes inputs. It records nothing keyed on
the value. A fact the user deleted with its session is re-learned from the next
session that repeats it. An ad-hoc "forget X" note is the near-miss. The note
persists, and the seeded instructions say *"Never delete a note file"* and
*"consider every note as authoritative"*. But the consolidator sees notes
through the diff, so a note is fresh input only in the run after it is written,
and nothing compares later inputs against it.

**Why no `audit_log`.** The folder is a git repository, and
`reset_git_repository` replaces `.git` with a fresh one-commit baseline after
every successful consolidation. `reset_drops_previous_history` asserts that the
new commit has no parent (`git-utils/src/baseline.rs:885-898`). The diff file
is deleted before the reset, so removed content does not survive in it either.
That is a privacy choice, and it means nothing records what a consolidation
changed. `jobs` records leases and watermarks, not mutations.

**Why no `human_review`.** No surface shows a person a pending memory. The user
can toggle generation, set a thread's mode, reset everything or edit the files.
Editing is authorship, after the fact.

## 10. Tests, Evals, and Benchmarks

The memory subsystem carries 114 test attributes. The state layer is tested
hardest, against real SQLite:

- claim ordering, leases and retry;
- watermark monotonicity;
- `prune_stage1_outputs_for_retention_prunes_stale_unselected_rows_only`;
- `delete_thread_removes_stage1_output_and_enqueues_phase2_when_selected`;
- `mark_thread_memory_mode_polluted_enqueues_phase2_for_selected_threads`;
- `clear_memory_data_clears_rows_and_preserves_thread_memory_modes`.

Two tests are close to what `negative_eval` asks for. Both seed an enabled and a
polluted thread with outputs:

- `list_stage1_outputs_for_global_includes_paginated_and_skips_polluted_threads`
  asserts that only the enabled one is returned.
- `get_phase2_input_selection_excludes_polluted_previous_selection` asserts the
  same for selection.

They are not vacuous, and they assert on the consolidator's input. The mark is
withheld because no committed case asserts that a fact stays out of what the
agent reads. That would mean a polluted, deleted or aged-out session's facts
leaving `MEMORY.md` or the injected summary, and that step is a model following
a prompt.

`memories/write/src/startup_tests.rs` (1,642 lines) runs both phases end to end
against a mock Responses server. It covers model and service-tier selection,
workspace-diff tracking across runs, extension pruning, symlink refusal and
`memories_startup_phase1_v2_preserves_human_evidence_and_redacts_storage`.
`phase2_sandbox_tests.rs` pins the sandbox inheritance in section 9.

No retrieval benchmark, extraction-quality eval or consolidation-fidelity eval
is committed. The README names a separate harness repository for prompt
snapshots, `openai/project/agent_memory/write`, which is not public. No paper is
cited. I ran no tests: 192 dependency files carried a commit date inside the
seven-day cooldown in a shallow clone, which dates every file to the tip.

## 11. For Your Own Build

### Steal

- **Forgetting by diff.** Make deletion an input change and let consolidation
  see it beside additions. Sync derived files exactly to the selected inputs,
  diff against the last good baseline and hand the consolidator the diff. A
  removed source then forces a rewrite, with no separate delete path to forget
  to call.
- **Redact on both sides of the model call.** Codex redacts the serialized
  transcript before extraction, and again the three fields the model returns.
- **Usage that feeds selection.** Citations increment a count that ranks
  sessions into the consolidated set and shields them from the age prune. That
  is a cheap, honest signal that a memory earned its place.
- **A locked-down consolidator.** The memory-writing agent gets no approvals,
  no MCP, no collaboration, no memory of its own, no notifications and one
  writable root. Its own threads are ephemeral so they never become memories.

### Avoid

- **Inheriting the parent's sandbox choice for an unattended writer.** A user
  who disables the sandbox for their own work has not agreed to an approval-free
  background agent reading model-extracted text with the same reach.
- **A forget path that ends at a prompt.** If a deletion must hold, the system
  needs a record keyed on the value that the next extraction is checked
  against. A diff the model is asked to honour is not that.
- **Discarding the only change history.** A one-commit baseline protects
  deleted content, at the price of never knowing what a consolidation did. A
  log of which inputs changed and which output sections were edited, without
  the text, would keep both properties.

### Fit

This design suits one developer who wants Codex to pick up their habits,
preferences and project facts across sessions and accepts that the result is a
model's notes about them. It costs nothing to run beyond model calls, and the
memory is plain Markdown the user can read and edit. It does not suit work
where memory must be correctable on demand, separated between clients or
repositories, or explained after the fact. Here one folder serves every
project, forgetting is a request the model may honour, and nothing records what
it did.

## 12. Open Questions

- Does the v2 consolidation, which drops the long handbook prompt, delete
  stale content from deleted inputs as reliably as v1? Nothing committed
  measures either.
- What writes `extensions/chronicle/resources/`? The feature flag and test
  fixtures are in the tree and the producer is not.
- Is a re-asserted fact after a "forget" note ever caught? The note persists,
  and only a run that re-reads every note could catch it.

## Appendix: File Index

**Write path**
- `codex-rs/memories/write/src/start.rs` — startup gating and phase order
- `codex-rs/memories/write/src/phase1.rs`, `phase1_output.rs`, `rollout_input.rs` — claim, extraction, filtering and redaction
- `codex-rs/memories/write/src/phase2.rs`, `workspace.rs`, `storage.rs` — selection sync, diff, consolidation agent and baseline reset
- `codex-rs/memories/write/src/extensions/` — ad-hoc instructions and resource pruning
- `codex-rs/memories/write/templates/memories/` — stage-one and consolidation prompts, v1 and v2
- `codex-rs/git-utils/src/baseline.rs` — the one-commit baseline and diff

**State**
- `codex-rs/state/memory_migrations/` — `stage1_outputs`, `jobs`, `consolidation_progress`
- `codex-rs/state/src/runtime/memories.rs` — every memory query, with its tests
- `codex-rs/state/src/runtime/memory_versions.rs` — v1/v2 stores, reset and thread deletion across both
- `codex-rs/state/src/runtime/threads.rs` — thread deletion cascade

**Read path**
- `codex-rs/ext/memories/src/` — injection, optional tools, local backend
- `codex-rs/ext/memories/templates/memories/` — read-path prompts
- `codex-rs/memories/read/src/` — citation parsing and usage telemetry
- `codex-rs/core/src/stream_events_utils.rs` — citation to usage count

**Configuration and controls**
- `codex-rs/config/src/types.rs` — `MemoriesToml`, defaults
- `codex-rs/features/src/lib.rs` — the `memories` and `chronicle` flags
- `codex-rs/core/src/mcp_tool_call.rs` — pollution marking

### Recorded searches

Run from the repository root at the pinned commit.

- **No value-keyed suppression in the memory code.**
  `git grep -n -i -E 'tombstone|suppress|forgotten|blocklist|denylist' -- codex-rs/memories codex-rs/ext/memories codex-rs/state/src/runtime/memories.rs codex-rs/state/memory_migrations`
  returns nothing.
- **No validity time.**
  `git grep -n -i -E 'valid_from|valid_to|valid_until|valid_at|event_time|occurred_at' -- codex-rs/memories codex-rs/ext/memories codex-rs/state`
  returns nothing.
- **No scope key in the memory schema.**
  `git grep -n -i -E 'project|cwd|workspace' -- codex-rs/state/memory_migrations`
  returns nothing.
- **No mutation log.**
  `git grep -n -i -E 'INSERT INTO (audit|history|memory_events)|memory_history|audit_log' -- codex-rs/state codex-rs/memories`
  returns nothing.
- **No review state.**
  `git grep -n -i -E 'approv|pending_review|verified|rejected' -- codex-rs/memories/write/src codex-rs/ext/memories/src codex-rs/state/memory_migrations`
  returns seven lines: input-validation errors in tests and the consolidator's
  `AskForApproval::Never` (`phase2.rs:26`, `:329-330`).
- **The remote summarize client has one caller, its test.**
  `git grep -n 'summarize_memories(' -- 'codex-rs/*.rs'` returns
  `core/src/client.rs:861` and `core/src/client_tests.rs:1650`.
- **Chronicle has no producer here.**
  `git grep -l -i 'chronicle' -- 'codex-rs/*.rs'` lists four files under
  `features/` and `config/` and two memory test files.

## History

**2026-11-02** — [`0a2d5f556de6e3b2c340d7f0635a1daf4040c30a`](https://github.com/openai/codex/commit/0a2d5f556de6e3b2c340d7f0635a1daf4040c30a), release rust-v0.166.0 plus later commits. First reading, from a shallow clone with history taken from the GitHub API. Screened first: one auto-run surface (`.vscode/settings.json`), ten build-time execution paths, three unpinned surfaces and every dependency file inside the cooldown window; nothing installed, built or run. No marks. `trust_state` and `negative_eval` are withheld on the same boundary: `polluted` threads leave the consolidator's input, tested, and what the agent reads carries no state ([section 9](#9-reliability-safety-and-trust)).

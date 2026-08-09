---
title: "AIPass"
eyebrow: "A budget on how often memory may speak"
description: "Surfacing is governed by a pure function with a per-session cap, a minimum message gap and a cooldown — so a relevant memory can still be refused because it spoke too recently."
root: ../..
page_kind: system
source_name: "AIOSAI/AIPass"
source_url: https://github.com/AIOSAI/AIPass
revision: 0d27e5ef282fca141c08c1d76fa3a8647a3eeea4
revision_url: https://github.com/AIOSAI/AIPass/commit/0d27e5ef282fca141c08c1d76fa3a8647a3eeea4
analyzed_at: 2026-08-09
capabilities: "scope_enforced"
stack_storage: "chroma, files"
stack_retrieval: "vector"
stack_source: "seeded"
matrix:
  memory_unit: "A JSON entry in a per-branch memory file, capped by type, plus symbolic fragments in ChromaDB"
  storage: "JSON files per branch as the hot tier, ChromaDB as the archive, with a subprocess isolation layer"
  retrieval: "Semantic search across branch archives, gated by a surfacing governance function"
  write: "Entries appended to branch files under a character cap; rollover archives what exceeds the limit"
  update_delete: "An AUDN dedup pattern — add, update, delete or noop — decided per fragment by an LLM"
  scoping: "branch is the scope key throughout, on files, limits, templates, search filters and lint"
  integration: "A drone CLI with per-module commands, hooks, a daemon and cross-branch template push"
  background: "A rollover watcher daemon, a monitor/detector pair and template synchronisation"
  trust: "A relevance score plus governance state; nothing epistemic on an entry"
  strengths: "Memory files have declared entry limits and a read-only linter that audits violations"
  risks: "The dedup verdict is an LLM call per fragment, with delete among the actions it may return"
---

## 1. Executive Summary

AIPass is a "Persistent Agent Workspace" — a large Python monorepo (roughly
377,000 lines, MIT) whose memory module is one of nineteen subsystems, alongside
mail, flow, spawn, drone, daemon, hooks and skills. The memory module itself is
about 38,500 lines.

**The mechanism worth the report is that recall is budgeted, not just ranked.**

`memory/apps/handlers/governance/engine.py` is a "Surfacing Governance Engine —
pure decision functions for controlling when recalled items should be
surfaced", and its default configuration is five numbers:

```python
{
    "enabled": True,
    "threshold": 0.3,
    "max_surfaces_per_session": 5,
    "min_messages_between": 10,
    "cooldown_seconds": 300,
}
```

`should_surface(item_id, relevance_score, state, config)` returns a tuple of
`(bool, reason, new_state)` and is documented as a "Pure function — does not
mutate the input state dict." The state it carries is
`surfaces_count`, `messages_since_last`, `last_surface_time` and `surfaced_ids`.

So a memory can clear the relevance threshold and still be refused — because
five have already surfaced this session, because fewer than ten messages have
passed, or because 300 seconds have not elapsed. **Relevance is necessary and
not sufficient.**

Almost every system in this atlas treats "should this be injected" as a ranking
question with a cutoff. This one treats it as a *rate* question with state, and
returns the reason. [Token Savior](../token-savior/) reaches the same territory
by learning a bandit; AIPass gets most of the way there with four counters and no
model.

**The second mechanism is a declared entry limit with a linter.** Memory files
are JSON per branch, entries are capped per type by a config with per-branch
overrides "deep-merged over the default entry_types", and `check_entry()` is "a
pure validator that checks whether a single entry text exceeds its character
cap". `drone @memory lint` audits violations **read-only**, and
`drone @memory rollover check` is a dry run.

A memory store that publishes a size contract, ships a read-only auditor for it,
and makes the destructive counterpart a separate command with a dry-run mode is
treating growth as a governed property rather than an emergent one.

## 2. Mental Model

Memory is per-**branch** — AIPass's unit of workspace — and two-tiered. The hot
tier is JSON files the agent reads directly, kept small by entry limits. The
archive is ChromaDB, holding what rolled over, searchable semantically across
branches.

A third layer sits beside them: **symbolic fragments**, LLM-extracted pieces
stored and deduplicated separately, with a bootstrap path that populates them
from session JSONLs.

```mermaid
flowchart TD
    E["entry written to a branch memory file"] --> L{"check_entry: over the character cap?"}
    L -->|yes| V["lint reports a violation — read-only"]
    L --> F["branch JSON file, hot tier"]
    F --> RO{"file over its entry limit?"}
    RO -->|"rollover check — dry run"| PRE["preview only"]
    RO -->|"rollover run"| ARC["extractor + orchestrator → ChromaDB archive"]
    S["session text"] --> SX["symbolic extractor, LLM"]
    SX --> DD{"AUDN deduplicator, LLM verdict"}
    DD -->|Add| FR["new fragment"]
    DD -->|Update| FU["existing fragment revised"]
    DD -->|Delete| FD["existing fragment removed"]
    DD -->|Noop| FN["nothing"]
    Q["query"] --> SR["semantic search over archives"]
    SR --> G{"should_surface: threshold, session cap,<br/>message gap, cooldown"}
    G -->|"refused, with a reason"| NO["not surfaced"]
    G -->|allowed| YES["surfaced; state updated"]
```

The `Delete` branch of the AUDN verdict is the one to watch: an LLM comparing a
new fragment against similar existing ones may decide the correct action is to
remove the old one.

## 3. Architecture

Nineteen top-level subsystems under `src/aipass/`, of which `memory` is one.
Within it: seven modules (governance, lint, rollover, search, symbolic,
templates, verify) over fifteen handler groups (archive, governance, intake,
json, learnings, monitor, rollover, schema, search, storage, symbolic,
templates, tracking and more).

Storage is `handlers/storage/chroma.py` plus `chroma_subprocess.py` — running
ChromaDB out of process, which is a defensive choice worth naming: an embedded
vector store that segfaults or leaks takes the agent down with it unless it is
isolated.

Templates are pushed across branches (`templates/pusher.py`, `differ.py`,
`spawn_pusher.py`) with a `template-status` command reporting version and push
state, so every branch's memory scaffolding stays in step.

The operational surface is a `drone @memory <command>` CLI, a rollover watcher
daemon and hooks.

## 4. Essential Implementation Paths

**Write** — an entry lands in a branch JSON file;
`handlers/json/entry_limits.check_entry()` validates against the effective cap.

**Audit** — `modules/lint.py` and `handlers/json/lint_handler.py`, read-only.

**Rollover** — `handlers/rollover/extractor.py` and `orchestrator.py`, with
`monitor/detector.py` and `memory_watcher.py` driving the watch mode.

**Symbolic** — `handlers/symbolic/`: `extractor`, `deduplicator` (AUDN),
`storage`, `retriever`, `chroma_client`, `hook`.

**Surface** — `handlers/governance/engine.should_surface`, re-exported through
`modules/governance.py` "for cross-branch consumers".

## 5. Memory Data Model

The hot tier is JSON with a schema normaliser (`handlers/schema/normalize.py`)
and a config-driven limit per entry type. That is unusual and it is the point:
the *shape* of what may be remembered is configuration, per branch, and
violations are reportable.

`changed_entries()` is "a pure diff helper that compares before/after file dicts
and returns only NEW or CHANGED entries" — so downstream work (vectorising,
archiving) processes deltas rather than whole files.

There is no status field, no confidence, no supersession pointer and no
provenance beyond the branch. The epistemic layer is entirely the governance
function and the dedup verdict.

## 6. Retrieval Mechanics

Semantic search over the ChromaDB archive with a `--branch` filter, plus
symbolic fragment search, plus a `verify` command that checks whether a specific
plan is vectorised — a small operational nicety that answers "is this actually
indexed" without a query.

**Scope is the branch and it is applied consistently**: memory files are
per-branch, entry limits have per-branch overrides, lint takes a branch
argument, search takes a `--branch` filter, and templates push per branch. That
earns `scope_enforced` — the key is stored, applied on the read path, and the
same key governs configuration.

The surfacing gate then applies on top, which means the read path has two
stages: what matches, and what is allowed to be said.

## 7. Write Mechanics

Writes are synchronous appends to JSON with a validator. Rollover is a separate,
explicitly invoked operation with a dry-run mode and a watcher for automation.

Correction is the AUDN dedup pattern — Add, Update, Delete, Noop — "decided…
via LLM". That vocabulary is well-chosen (it is the same shape as
[Memory Palace](../memory-palace/)'s write guard) and the risk is the `Delete`
verdict: a model comparing a new fragment against existing ones can conclude the
old one should go, and nothing found gates that decision, records why, or keeps
what was removed.

There is no rejected-value record. A fragment deleted by an AUDN verdict can be
re-extracted from the next session that mentions it.

## 8. Agent Integration

`drone @memory <command>` with seven module namespaces, hooks including a
symbolic capture hook with a `hook-test` command, a daemon, and cross-branch
template distribution. `symbolic bootstrap` populates fragments from historical
session JSONLs, so an existing workspace can be back-filled.

## 9. Reliability, Safety, and Trust

**Scope — awarded**, per section 6.

**Trust state, tombstone, bitemporal, audit log, negative eval — no.**

**Human review — withheld, and the near-miss is the lint command.**
`drone @memory lint` audits entry-limit violations and is explicitly read-only;
`rollover check` previews. Both surface work for a person and neither is a
surface where a person adjudicates *content* — they adjudicate *size*. That is a
real distinction and the commands are well-designed for what they do.

**The governance function is the safety mechanism and it is the right shape.**
Pure, stateful, reason-returning, configurable, and re-exported as a public API
for other subsystems. Its weakness is that the state is per-session and
in-memory: `new_state()` starts every counter at zero, so the cooldown and the
session cap reset whenever the state does, and nothing found persists
`surfaced_ids` across a restart.

**The dedup verdict is the risk.** An LLM with `Delete` in its action space,
operating on fragments extracted by another LLM, with no record of what was
removed.

## 10. Tests, Evals, and Benchmarks

**No paper.** 446 test files — the second-highest count in this pass — with a
root `conftest.py`, a `Dockerfile.test`, codecov integration, an OpenSSF
Scorecard badge and an OpenSSF Best Practices badge.

The Scorecard and Best Practices badges are supply-chain and process signals
rather than quality claims about memory, and this report treats them as such;
the atlas does not read badges as evidence about mechanisms.

No retrieval benchmark, no committed evaluation of the surfacing thresholds, and
no derivation for the five governance defaults (0.3, 5, 10, 300). They are
plausible numbers with no measurement behind them in the tree.

**I ran nothing.**

## 11. For Your Own Build

### Steal

- **Budget how often memory may speak, not just what it says.** A per-session
  cap, a minimum message gap and a cooldown, evaluated as a pure function that
  returns a reason, turns "is this relevant" into "is this worth interrupting
  for". Four counters, no model.
- **Return the reason with the decision.** `(bool, reason, new_state)` means a
  suppressed memory is explainable, which is the query-time signal most systems
  in this atlas lack.
- **Keep the governance function pure and re-export it.** "Does not mutate the
  input state dict" is what makes it testable, and publishing it for
  "cross-branch consumers" is what stops each subsystem inventing its own rules.
- **Declare an entry limit per type, with per-branch overrides deep-merged.**
  Memory growth becomes a configured property rather than an emergent one.
- **Ship a read-only linter for the limit, and a dry run for the fix.** `lint`
  and `rollover check` before `rollover run` is the right ordering of
  destructiveness.
- **Diff before you process.** `changed_entries()` returning only new or changed
  entries means archiving and vectorising cost proportional to change.
- **Run the embedded vector store in a subprocess.** `chroma_subprocess.py`
  means a crash in the index does not take the agent with it.
- **Give the archive a `verify` command.** "Is this plan actually vectorised" is
  a question an operator asks and a query cannot answer.

### Avoid

- **Do not give an LLM `Delete` without a record.** AUDN is a good vocabulary and
  the destructive verdict needs what the other three do not: a note of what was
  removed and why, or it is an unauditable deletion decided by a model comparing
  the output of another model.
- **Do not keep surfacing state only in memory.** A cooldown that resets on
  restart is a cooldown an agent can defeat by restarting.
- **Do not ship five tuned constants with no derivation.** 0.3, 5, 10 and 300 are
  the whole surfacing policy and nothing in the tree measures them.

### Fit

This suits someone adopting AIPass as a whole workspace — the memory module is
tightly coupled to branches, drones and templates, and is not a component to
lift. Within that, the governance and rollover design is more thought-through
than most.

`governance/engine.py` is the file to read regardless. It is a short pure
function and it encodes a question — *how often should memory interrupt?* — that
most of this corpus never asks.

## 12. Open Questions

- **Where does governance state live between sessions?** `new_state()` is a
  fresh dict; nothing found persists it.
- **What gates the AUDN `Delete` verdict?** The deduplicator "decides the correct
  action via LLM"; no confirmation, threshold or record was found.
- **Are the five governance defaults ever tuned per branch?** The entry limits
  support per-branch overrides; whether the surfacing config does was not traced.
- **How does rollover interact with the symbolic tier?** Entries roll over to
  ChromaDB; fragments live in ChromaDB already, and whether they age was not
  established.

## Appendix: File Index

**Surfacing governance** — `src/aipass/memory/apps/handlers/governance/engine.py`
(`DEFAULT_CONFIG` `:27-33`, `new_state` `:40`, `should_surface` `:56`),
`src/aipass/memory/apps/modules/governance.py`

**Entry limits and lint** — `handlers/json/entry_limits.py` (`check_entry`,
`changed_entries`), `handlers/json/lint_handler.py`, `config_loader.py`,
`memory_files.py`, `modules/lint.py`

**Rollover** — `handlers/rollover/extractor.py`, `orchestrator.py`,
`handlers/monitor/detector.py`, `memory_watcher.py`, `modules/rollover.py`

**Symbolic** — `handlers/symbolic/deduplicator.py` (the AUDN pattern `:9-14`),
`extractor.py`, `storage.py`, `retriever.py`, `chroma_client.py`, `hook.py`,
`modules/symbolic.py`

**Storage** — `handlers/storage/chroma.py`, `chroma_subprocess.py`,
`handlers/archive/indexer.py`, `handlers/schema/normalize.py`

**Search** — `handlers/search/query_executor.py`, `vector_search.py`,
`modules/search.py`, `modules/verify.py`

**Templates** — `handlers/templates/pusher.py`, `differ.py`, `spawn_pusher.py`,
`modules/templates.py`

**Documentation** — `src/aipass/memory/README.md` (the command surface and the
architecture tree)

## History

**2026-08-09** — [`0d27e5ef282fca141c08c1d76fa3a8647a3eeea4`](https://github.com/AIOSAI/AIPass/commit/0d27e5ef282fca141c08c1d76fa3a8647a3eeea4) — first reading. Screened before reading; the tree was read, never installed, and no test was run.

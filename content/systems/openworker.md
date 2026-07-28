---
title: OpenWorker
eyebrow: Policy over machinery
description: A 260-line memory whose real artifact is the prompt governing it — including the observation that without guidance models either never save anything or save noise the repository already records.
root: ../..
page_kind: system
source_name: andrewyng/openworker
source_url: https://github.com/andrewyng/openworker
revision: d3863966c9de
revision_url: https://github.com/andrewyng/openworker/commit/d3863966c9de
analyzed_at: 2026-07-28
capabilities: "scope_enforced"
matrix:
  memory_unit: "Row with scope, optional key, content, workspace, session, created_at"
  storage: "SQLite (`coworker.db`) alongside sessions and workspaces"
  retrieval: "Listing filtered by scope and workspace; no ranking or search"
  write: "Three agent tools — `remember`, `memory_update`, `memory_forget`"
  update_delete: "Update by id, hard delete by id; no supersession or tombstone"
  scoping: "`Scope` of global, workspace, or session, applied on read"
  integration: "Tools wired into the agent loop with guidance injected only when a store exists"
  background: "None for memory"
  trust: "Timestamps only; the prompt tells the model to re-verify what a memory names"
  strengths: "The write policy is explicit, and it addresses a stated failure of models without one"
  risks: "No ranking, no correction record, and the whole discipline lives in a prompt"
---

## 1. Executive Summary

OpenWorker is Andrew Ng's MIT-licensed AI coworker — a large desktop and CLI
agent with permissions, audit, risk classification, workspace trust, unattended
operation and self-wake. Its memory subsystem is **260 lines**: a `MemoryItem`,
a store interface, a SQLite implementation, and three tools.

By the atlas's usual measures that is unremarkable. The reason it is here is that
the memory's real artifact is not the code — it is the paragraph that governs the
model's use of it, and the comment above that paragraph:

```python
# When-to-remember rules, injected only when a memory store is wired. Without these,
# models either never call `remember` or save noise the repo already records.
```

That is a stated empirical finding about model behaviour, and it names a
**bimodal failure**: given a memory tool and no policy, models do not save
mediocre things — they either save nothing or save everything. Most systems in
this atlas have a memory tool with a one-line description and no stated
expectation of what happens next.

The policy itself is unusually specific for a prompt:

> "Use `remember` for durable facts: the user's corrections and stated
> preferences (**include the why**), and project context you couldn't rederive
> from the code. **Don't save what the repo already records** (code structure,
> git history, AGENTS.md) or details that only matter to the current task. Use
> **absolute dates**, never 'yesterday'."
>
> "Before saving, check the known-memories list: if an entry already covers it,
> **revise that entry** with `memory_update` instead of adding a near-duplicate;
> **retire** wrong or obsolete entries with `memory_forget`."
>
> "**Memories reflect when they were written.** If one names a file, flag, or
> URL, **verify it still exists** before relying on it."

Four mechanisms this atlas has documented as code appear here as instructions:
deduplication, supersession, an ROI test for what is worth storing, and
read-time staleness verification. [Magic Context](../magic-context/) builds a
whole re-verification subsystem to answer the last one; OpenWorker tells the
model to check.

Reservations, and they follow directly. A policy in a prompt is not enforced:
nothing rejects a near-duplicate, nothing records that a memory was retired, and
nothing detects when the model ignores the guidance. Retrieval is a filtered
list with no ranking. And `memory_forget` is a hard delete with no trace.

## 2. Mental Model

```text
remember(content, scope) ──▶ row in memories(scope, key, content,
                                            workspace, session_id, created_at)

scope ∈ { GLOBAL, WORKSPACE, SESSION }   applied when listing

memory_update(id, content) ──▶ content replaced in place
memory_forget(id)          ──▶ row deleted

read ──▶ list(scope?, workspace?) ──▶ format_memories() into the prompt
```

There are no states. A memory exists or it does not, and the transition between
those is a tool call the model decides to make on the strength of a paragraph of
guidance.

## 3. Architecture

`coworker/memory/` is four files — `base.py` (`Scope`, `MemoryItem`,
`MemoryStore` ABC, `format_memories`), `sqlite_store.py`, `tools.py`,
`__init__.py` — totalling 260 lines. The store shares `coworker.db` with
sessions and workspaces.

The surrounding system is the opposite of small: `permissions.py`, `audit.py`,
`risk.py`, `workspace_trust.py`, `unattended.py`, `selfwake.py`, `secrets.py`,
`connectors/`, `skills/`, `personas/`, `automation/`. Memory does not connect to
any of it — grep finds no reference to memory in the audit, permission or
unattended paths, so an agent running unattended writes memories under exactly
the same rules as an attended one.

### Deployment and ergonomics

A `pip`-installable Python application with a SQLite file; nothing else to stand
up for memory. The store is one table you can read with any SQLite client, and
memory is optional — the tools and their guidance are wired only when a store is
configured, so the agent runs without it.

## 4. Essential Implementation Paths

### The guidance is the mechanism

Every clause in the policy maps to something another system in this atlas builds:

| The instruction | Built elsewhere as |
| --- | --- |
| "Don't save what the repo already records" | [GenericAgent](../genericagent/)'s ROI rule — an entry the model would act on unprompted costs tokens and returns nothing |
| "revise that entry instead of adding a near-duplicate" | dedupe and merge passes in [mem0](../mem0/), [agentmemory](../agentmemory/), [Memora](../memora/) |
| "retire wrong or obsolete entries" | supersession chains in [Graphiti](../graphiti/), [Atomic Agent](../atomic-agent/) |
| "verify it still exists before relying on it" | [Magic Context](../magic-context/)'s git-triggered re-verification |
| "include the why" | reason fields in [Core Memory](../core-memory/), [Verel](../verel/) |
| "use absolute dates" | nothing — most systems here have this bug |

The last row is worth pausing on. "Use absolute dates, never 'yesterday'" fixes
a failure the atlas has not otherwise named: a memory recorded as "the user is
travelling next week" is *wrong* by the time it is read, and no amount of
retrieval quality recovers it. It costs one clause in a prompt.

The honest reading of this table is not that prompting is as good as machinery —
it plainly is not, because none of it is enforced or observable. It is that a
260-line memory with a well-considered policy may outperform a 10,000-line one
with none, and several systems in this atlas ship the second.

### Conditional injection

The guidance is "injected only when a memory store is wired", so an agent
without memory does not carry instructions about a tool it lacks. That is the
[gate the expensive path](../../patterns/gate-the-expensive-path/) instinct
applied to prompt real estate — context is spent only when there is something to
spend it on.

### A `key` column with no visible use

The schema carries `key TEXT` alongside `content`, and `MemoryItem` exposes it,
but the three tools do not set it: `remember(content, scope)` has no key
parameter. The column is the hook for exactly the "revise the entry that already
covers this" behaviour the prompt asks the model to perform by reading the list —
keyed memory would make that a lookup rather than a judgement.

It reads as a design that knows where it would go next.

### Three scopes, applied on read

`GLOBAL | WORKSPACE | SESSION`, with `list()` filtering on scope and workspace.
That is a real boundary applied on the read path rather than a tag, which is more
than several larger systems here manage — though with a single local user it is
about organization rather than isolation.

## 5. Memory Data Model

`memories(id, scope, key, content, workspace, session_id, created_at)`.

Absent: trust state, provenance beyond a timestamp, supersession, tombstone,
audit, ranking. `memory_forget` deletes the row; nothing records that it existed
or why it went, which sits oddly beside an application that has a dedicated
`audit.py` for other operations.

## 6. Retrieval Mechanics

`list(scope, workspace, limit)` and `format_memories()` into the prompt. No
embedding, no lexical search, no ranking, no relevance — memory is small enough
to inject wholesale, which is the same bet [nanobot](../nanobot/) makes.

That bet holds while the store is small. Nothing here bounds growth, and the
prompt's "check the known-memories list" instruction assumes the list is short
enough to read.

## 7. Write Mechanics

Three tools, called at the model's discretion under the guidance above. No
extraction pass, no background consolidation, no dedupe check.

### Operational cost

Zero LLM cost on the memory path — no extraction, no summarization, no
consolidation. Writes are synchronous SQLite inserts, so nothing blocks and
nothing lags: a memory is retrievable the moment it is written, which is the
freshness property the [benchmarks page](../../benchmarks/) says nobody measures
and which falls out for free here.

The recurring cost is context: every memory in scope is injected on every turn,
so per-turn tokens grow linearly with the store and nothing caps it.

## 8. Agent Integration

`memory_tools(store, workspace=...)` returns `remember`, `memory_update` and
`memory_forget`, wired into the agent's tool set alongside base tools,
permissions and `AGENTS.md`. Memory is one optional component of a much larger
agent.

## 9. Reliability, Safety, and Trust

Strengths:

- **An explicit write policy**, addressing a stated failure of models without one.
- **A named empirical finding** — without guidance, models either never save or
  save noise.
- **Absolute-date discipline**, which nothing else here asks for.
- **Read-time staleness instruction**, cheap where others build subsystems.
- **Three scopes applied on read.**
- **Conditional injection**, so unused tools cost no context.
- **No LLM on the memory path**, so writes are instant and free.

Gaps:

- **Nothing is enforced.** Dedupe, retirement, ROI and verification are requests,
  and no signal exists when the model ignores them.
- **`memory_forget` is a silent hard delete** in an application that audits other
  operations.
- **No ranking and no growth bound**, with everything in scope injected per turn.
- **No trust state, provenance, or supersession.**
- **Memory is disconnected from the trust machinery** — unattended runs write
  under the same rules as attended ones.
- **`key` exists and is unused.**

## 10. Tests, Evals, and Benchmarks

A `tests/` tree exists for the application. Nothing was run for this review, and
no memory-specific test or benchmark was located.

The measurable claim is the one in the comment: that guidance changes model
behaviour from bimodal — never saving or saving noise — to useful. That is an A/B
test with the guidance toggled, and the finding is stated as though it were
observed, so someone may already have the data.

## 11. For Your Own Build

### Steal

- **Write the when-to-remember policy down**, and expect the failure to be
  bimodal without it. A tool description is not a policy.
- **"Use absolute dates, never yesterday."** One clause; prevents a class of
  memory that is wrong by the time it is read.
- **"Don't save what the repo already records."** The cheapest possible ROI test:
  if the agent could rederive it, storing it costs tokens forever and returns
  nothing.
- **"Include the why"** on preferences and corrections, so a later reader can
  tell a decision from a whim.
- **Tell the model that memories age**, and to verify anything a memory names
  before relying on it — a poor substitute for re-verification machinery and far
  better than nothing.
- **Inject tool guidance only when the tool exists.**

### Avoid

- **A hard delete with no record**, especially in a system that audits elsewhere.
- **Unbounded wholesale injection** — it works until the store grows, and nothing
  here notices when it does.
- **Assuming the policy is followed.** None of it is observable, so the first
  sign of drift is memory quality nobody can explain.

### Fit

Right as evidence that a small memory with a considered policy beats a large one
without: if you are choosing where to spend the next day, this repository argues
for the prompt over the pipeline. Wrong as a memory design to build on — there is
no ranking, no correction record, no trust model, and the discipline that makes
it work has no enforcement behind it. Read the guidance paragraph, not the
schema.

## 12. Open Questions

- Was the bimodal finding measured, and by how much does the guidance move
  behaviour?
- What is `key` for, and why do the tools not set it?
- What happens when the store outgrows wholesale injection?
- Why does memory sit outside the audit and permission machinery the rest of the
  application uses?
- Does an unattended run get different memory guidance? Nothing found suggests it
  does.

## Appendix: File Index

- Policy: `coworker/agent.py` (`_MEMORY_GUIDANCE`, and the comment above it).
- Model: `coworker/memory/base.py` (`Scope`, `MemoryItem`, `MemoryStore`,
  `format_memories`).
- Store: `coworker/memory/sqlite_store.py` (the `memories` table).
- Tools: `coworker/memory/tools.py` (`remember`, `memory_update`,
  `memory_forget`).

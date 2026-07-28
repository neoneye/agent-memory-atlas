---
title: Qwen Code
eyebrow: Team memory in git
description: A coding agent whose memory has three tiers, the third of which is committed to the repository — so a write containing a secret is refused unconditionally, even when that tier is switched off.
root: ../..
page_kind: system
source_name: QwenLM/qwen-code
source_url: https://github.com/QwenLM/qwen-code
revision: 6a432ad2ebce
revision_url: https://github.com/QwenLM/qwen-code/commit/6a432ad2ebce
analyzed_at: 2026-07-28
capabilities: "scope_enforced, human_review"
matrix:
  memory_unit: "Auto-memory entry typed `user | feedback | project | reference`, with source refs"
  storage: "Markdown context files on disk; the team tier is committed to the repository"
  retrieval: "Indexed scan with a relevance selector; async recall on demand"
  write: "Background extraction from sessions, cursor-tracked; `dream` consolidation; skills reviewed before use"
  update_delete: "`forget` by candidate selection, by match, or by entry; no value-level tombstone found"
  scoping: "User, project and team tiers with separate paths; team writes guarded unconditionally"
  integration: "Built into the CLI; memory channels for intent and recall"
  background: "Extraction with a resumable offset cursor, dream consolidation, skill review nudges"
  trust: "Source session and message ids; extraction and dream record `updated` or `noop`"
  strengths: "A shared tier that is source-controlled, with secret writes refused even when the tier is off"
  risks: "Correction is entry-keyed, and re-extraction from retained sessions is unguarded"
---

## 1. Executive Summary

Qwen Code is an Apache-2.0 coding agent — a fork of Gemini CLI, and the file
headers show it: some memory modules carry "Copyright 2025 Google LLC" and
others "Copyright 2026 Qwen Team", so a reader tracing provenance should expect
part of this subsystem to have an upstream.

The memory package is about 9,000 lines across roughly thirty modules under
`packages/core/src/memory/`, with a test file beside nearly every one. It is one
of the more complete memory subsystems in this atlas, and the part worth the
review is the **third tier**.

Memory is split across user, project and **team** scopes, and the team tier is
committed to the repository. That makes it shared memory with a distribution
mechanism everyone already has — and it makes a leak permanent, which the code
addresses directly:

> "Team memory is committed to the repo and shared with every collaborator, so
> any write that targets the team directory and contains a detected secret is
> rejected — **unconditionally (even if the team tier is otherwise disabled)**,
> since the directory is source-controlled regardless."

Two things about that are worth copying. The guard is **fail-closed** on the
shared path, where every other system in this atlas that supports shared memory
either confirms or simply writes. And it ignores the feature flag: disabling the
team tier does not disable the guard, because the directory is still under
version control and a write landing there is still a commit away from being
public. Most feature flags in this position would gate the check along with the
feature, and the comment explains why this one does not.

The rest of the design is careful in the same register. Extraction runs against
a **resumable cursor** (`sessionId`, `processedOffset`), so an interrupted pass
does not restart or skip. Extraction and consolidation both record whether they
`updated` or were a `noop`, so "the pass ran and changed nothing" is
distinguishable from "the pass did not run" — a distinction the atlas has asked
for repeatedly and found almost nowhere. Memories carry `messageIds` back to the
exchange that produced them.

Reservations: correction is `forget`, keyed on entries and matches, with no
value-level tombstone — and since extraction runs repeatedly over retained
sessions, a forgotten memory can be re-derived from the material that produced
it. The subsystem is also large enough that its own design documents describe
several partially-landed efforts.

## 2. Mental Model

```text
tiers        user/      project/      team/  ← committed to the repository
                                        │
                                        └─ every write path-checked;
                                           secrets refused, flag or no flag

types        user | feedback | project | reference

session ──▶ extraction (cursor: sessionId + processedOffset)
              records: updated | noop, touched topics, session id
              │
              ▼
            entries ──▶ dream (consolidation)
                          records: updated | noop, recentSessionIdsSinceDream
              │
              ▼
            recall ──▶ relevance selector ──▶ context file

forget ──▶ by candidate selection | by match | by entry
           (nothing keyed on the rejected value)
```

## 3. Architecture

`packages/core/src/memory/` — `manager.ts` (1,504), `channel-memory.ts` (549),
`prompt.ts` (542), `forget.ts` (529), `writeContextFile.ts` (433),
`skillReviewAgentPlanner.ts` (406), `recall.ts` (406), `paths.ts` (377),
`channel-memory-document.ts` (373), plus `dream.ts`, `extract.ts`,
`extractionAgentPlanner.ts`, `indexer.ts`, `scan.ts`, `refresh.ts`,
`relevanceSelector.ts`, `remember.ts`, `entries.ts`, `store.ts`, `memoryAge.ts`,
`status.ts`, `secret-scanner.ts`, `learn-skill-agent.ts`, `pending-skills.ts`,
`memory-scoped-agent-config.ts`, and the team modules
(`team-memory-sync.ts`, `team-memory-git-status.ts`,
`team-memory-secret-guard.ts`, `team-paths.ts`).

`packages/channels/base/` adds `channel-memory-intent.ts` and
`channel-memory-recall.ts`.

### Deployment and ergonomics

Nothing to stand up: memory is Markdown files on disk plus, for the team tier,
files in the repository the developer already has. No database, no vector
service, no key required to store anything — extraction and consolidation use
the model the CLI is already configured with.

The team tier's distribution story is its best ergonomic property. Sharing
memory across a team normally means a service, an account model and an
authorization scheme; here it means `git pull`.

## 4. Essential Implementation Paths

### A shared tier that is source-controlled, and guarded accordingly

Putting shared memory in the repository is a decision with an obvious upside and
one serious hazard, and the code treats the hazard as primary. `checkTeamMemorySecrets`
"returns an error message to block the write, or null to allow it", and the
docstring records a performance decision alongside the safety one: "the cheap
path check runs first, so non-memory writes pay only a single path compare."

The atlas's [explicit write destination](../../patterns/explicit-write-destination/)
pattern argues that shared writes deserve confirmation. This is the stronger
form — a class of shared write that is *refused* — and the unconditional
behaviour is the detail that makes it trustworthy. A guard that a feature flag
can switch off protects you only while the flag is set the way you remember.

### Extraction that can be resumed rather than restarted

```ts
export interface AutoMemoryExtractCursor {
  sessionId?: string;
  processedOffset?: number;
  updatedAt: string;
}
```

An offset into a session, persisted. [nanobot](../nanobot/)'s best idea in this
atlas is not advancing a cursor after a failure; Qwen Code carries the cursor as
a first-class record, so an extraction interrupted halfway resumes at the
boundary rather than reprocessing the session or skipping the remainder.

This is the [recoverable background work](../../patterns/recoverable-background-work/)
requirement, met at the input rather than by a job queue.

### `noop` recorded as an outcome

```ts
lastExtractionStatus?: 'updated' | 'noop';
lastDreamStatus?: 'updated' | 'noop';
```

with `lastExtractionTouchedTopics`, `lastDreamTouchedTopics`, and
`recentSessionIdsSinceDream`.

Distinguishing "ran and found nothing" from "did not run" is a small schema
decision with a large operational return. Every system in this atlas with a
background pass has the failure where memory silently stops updating, and
without this field the two causes — the pass is broken, or there was genuinely
nothing to learn — look identical from the outside. Recording which *topics*
were touched narrows it further.

### Three forget paths

`selectManagedAutoMemoryForgetCandidates`, `forgetManagedAutoMemoryMatches` and
`forgetManagedAutoMemoryEntries` — 529 lines, which is more than most systems in
this atlas spend on deletion and more than several spend on retrieval.

Selecting candidates separately from acting on them is the shape
[Memora](../memora/) gets right with its dry-run default: a selection function
can be called and inspected without mutating. Whether it is used that way was not
traced.

What is missing is the same thing missing nearly everywhere: none of the three
records that a *value* was rejected. Extraction runs repeatedly over retained
sessions, so a forgotten memory can be re-derived by the pass that produced it,
and nothing consults the forget history on the way in.

### Signal handling as scar tissue

`team-memory-sync.ts` explains its own choice of kill signal per git operation:

> "`killSignal` is chosen PER OP because Node's `timeout` does not escalate: a
> git child that traps/blocks the signal hangs past the timeout. SIGKILL is
> unblockable but skips cleanup, so it is safe ONLY for read-only / network ops
> (no index/lock to corrupt) — which are also the hang-prone ones. MUTATING ops
> (add/commit) default to SIGTERM so git can release `index.lock` and finish
> cleanup."

It also uses `execFile` with no shell "so paths with spaces / metacharacters are
safe".

This is the kind of comment that only exists after an incident, and it belongs in
the same category as [Waku](../waku-agent/)'s fail-open gate and
[OptMem](../optmem/)'s UTF-8 note. A memory tier that commits to a shared
repository can corrupt `index.lock` for a whole team, and the code knows it.

### Skills with a review step

`learn-skill-agent.ts`, `pending-skills.ts`, `skillReviewAgentPlanner.ts` and a
`skillReviewNudge` integration test describe skills that are learned, held
pending, and reviewed before use.

That is closer to the [skills as procedural memory](../../patterns/skills-as-procedural-memory/)
pattern's verified-execution gate than most systems manage — a review is not an
execution proof, but a pending state that something must clear is more than a
file appearing in a directory.

## 5. Memory Data Model

Entries typed `user | feedback | project | reference`, with
`AutoMemorySourceRef` carrying `sessionId`, `recordedAt` and `messageIds`, and
`AutoMemoryMetadata` carrying schema version, timestamps, and the extraction and
dream bookkeeping above. `AUTO_MEMORY_SCHEMA_VERSION` is explicit, so a format
change has somewhere to hang a migration.

What is absent:

- **No trust state.** A memory exists; nothing marks it candidate or verified.
- **No value-level tombstone**, so `forget` does not survive re-extraction.
- **No supersession chain** — a revised memory replaces rather than links.

The four types are a good default set, and the presence of `feedback` as a
distinct type from `user` is notable: guidance about how to work is separated
from facts about the person, which most systems collapse into one bucket.

## 6. Retrieval Mechanics

`indexer.ts` and `scan.ts` build the index; `relevanceSelector.ts` chooses what
to surface; `recall.ts` and the channel modules provide sync and async paths, and
`docs/design/2026-05-15-async-memory-recall-design.md` documents the latter. The
selected memories are rendered by `writeContextFile.ts`.

`memoryAge.ts` exists, so age participates in selection.

## 7. Write Mechanics

Sessions feed extraction under the cursor; `remember.ts` handles explicit writes;
`dream.ts` consolidates; `refresh.ts` and `writeContextFile.ts` re-render the
context file. Team writes pass the secret guard, then the git sync.

### Operational cost

Extraction and dream are model calls that run against sessions rather than on
the critical path, so recall does not block on them. The design documents include
`2026-05-21-memory-pressure-monitor-design.md` and
`2026-07-11-managed-memory-microcompaction.md`, which indicates the context cost
of injected memory is treated as a managed budget rather than left to grow — the
concern the atlas's [benchmarks page](../../benchmarks/) says is usually
unmeasured.

The lag between an exchange and its extraction is bounded by when the background
pass runs, and the cursor makes the unprocessed remainder explicit, but no figure
for it was found.

## 8. Agent Integration

Memory is built into the CLI rather than mounted as a plugin, with
`memory-scoped-agent-config.ts` allowing configuration per scope and
`channel-memory-intent.ts` / `channel-memory-recall.ts` giving the agent an
intent and recall surface.

## 9. Reliability, Safety, and Trust

Strengths:

- **A shared tier distributed by git**, needing no service or account model.
- **Secret writes to the shared tier refused unconditionally**, independent of
  the feature flag, because the directory is source-controlled regardless.
- **A cheap path check first**, so the guard costs almost nothing on other
  writes.
- **A resumable extraction cursor** with a processed offset.
- **`noop` recorded as an outcome** for both extraction and consolidation, with
  touched topics.
- **Provenance to message ids.**
- **An explicit schema version.**
- **Three distinct forget paths**, with candidate selection separable from
  action.
- **Per-operation kill-signal reasoning** in the git path, and `execFile` with no
  shell.
- **Skills held pending until reviewed.**
- **Tests beside nearly every module**, plus lifecycle and nudge integration
  tests.

Gaps:

- **No value-level tombstone**, in a system whose extraction re-reads retained
  sessions.
- **No trust state or supersession chain.**
- **Secret detection bounds the guard.** Unconditional refusal is only as good as
  `secret-scanner.ts`, and a missed pattern is a permanent commit.
- **Large surface with in-flight designs**, so behaviour may differ between the
  documents and the code.
- **Mixed provenance** — some modules are upstream Gemini CLI by their headers,
  which matters when deciding where to report a bug.

## 10. Tests, Evals, and Benchmarks

Roughly half the files in the memory package are tests, including
`memoryLifecycle.integration.test.ts`, `skillReviewNudge.integration.test.ts`,
`team-memory-secret-guard.test.ts` and `team-memory-sync.test.ts`. There is also
`integration-tests/cli/save_memory.test.ts`.

Nothing was run for this review and no retrieval-quality benchmark was found. The
test coverage tracks the risky logic closely, which is the pattern the atlas sees
in its better-engineered entries.

The measurement this design invites is the secret guard's recall: of secrets that
reach a team-memory write, what fraction does `secret-scanner.ts` catch? An
unconditional refusal is a strong guarantee about the *decision* and says nothing
about the *detector*.

## 11. For Your Own Build

### Steal

- **Distribute shared memory through the repository.** It removes a service, an
  account model and an authorization scheme, and every collaborator already has
  the client.
- **Refuse secret-bearing writes to a shared tier unconditionally**, ignoring the
  feature flag that governs the tier. A guard a flag can disable protects you
  only while the flag is set the way you remember.
- **Put the cheap check first**, so a guard on one path does not tax every other.
- **Persist an extraction cursor with an offset**, so an interrupted pass resumes
  instead of restarting or skipping.
- **Record `noop` as an outcome.** "Ran and changed nothing" and "did not run"
  look identical from outside, and only one of them is a bug.
- **Separate `feedback` from `user`.** How to work and who the person is are
  different kinds of memory with different lifetimes.
- **Choose kill signals per operation** when shelling out to git, and never
  SIGKILL a mutating one.

### Avoid

- **Forget without a tombstone**, where extraction re-reads the sessions that
  produced the memory. Three forget paths and none of them survive the next pass.
- **Trusting a detector to make a guarantee.** The refusal is unconditional; the
  detection is not, and the permanent consequence sits behind the weaker half.

### Fit

Right for a team that already shares a repository and wants shared agent memory
without standing anything up — the git tier is the cheapest credible answer to
that problem in the atlas. Right also as a study in operational care: the cursor,
the `noop` status and the signal handling are all things learned the hard way.
Wrong if you need memory that stays corrected: forget is thorough about removing
entries and silent about preventing their return, and in a system that
re-extracts continuously that is the gap that will find you.

## 12. Open Questions

- What stops a forgotten memory being re-extracted from the sessions that
  produced it?
- What is `secret-scanner.ts`'s recall, and has it been measured against real
  credential formats?
- Is `selectManagedAutoMemoryForgetCandidates` ever used as a preview, or only
  internally before acting?
- Which memory modules are inherited from Gemini CLI and which are Qwen's? The
  headers differ; the boundary was not traced.
- Do the memory-pressure and microcompaction designs describe shipped behaviour
  or intent?

## Appendix: File Index

- Model: `packages/core/src/memory/types.ts` (`AUTO_MEMORY_TYPES`,
  `AutoMemorySourceRef`, `AutoMemoryMetadata`, `AutoMemoryExtractCursor`),
  `const.ts`.
- Team tier: `team-memory-secret-guard.ts` (`checkTeamMemorySecrets`),
  `team-memory-sync.ts`, `team-memory-git-status.ts`, `team-paths.ts`.
- Correction: `forget.ts` (`selectManagedAutoMemoryForgetCandidates`,
  `forgetManagedAutoMemoryMatches`, `forgetManagedAutoMemoryEntries`).
- Background: `extract.ts`, `extractionAgentPlanner.ts`, `dream.ts`,
  `dreamAgentPlanner.ts`, `refresh.ts`.
- Retrieval: `indexer.ts`, `scan.ts`, `relevanceSelector.ts`, `recall.ts`,
  `memoryAge.ts`, `writeContextFile.ts`.
- Skills: `learn-skill-agent.ts`, `pending-skills.ts`,
  `skillReviewAgentPlanner.ts`.
- Channels: `packages/channels/base/src/channel-memory-intent.ts`,
  `channel-memory-recall.ts`.
- Design notes: `docs/design/2026-05-15-async-memory-recall-design.md`,
  `docs/design/auto-memory/`, `docs/design/2026-05-21-memory-pressure-monitor-design.md`,
  `docs/design/2026-07-11-managed-memory-microcompaction.md`.

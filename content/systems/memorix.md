---
title: "Memorix"
eyebrow: "Every read fenced, one write unchecked"
description: "A local-first shared memory layer for coding agents whose observations carry a personal, team or project visibility enforced fail-closed at every read seam, and whose long-term memories climb a candidate-qualified-approved ladder a person drives — while the MCP transfer tool's import inserts arbitrary records verbatim, with no visibility validation, no project re-stamping and no reader check."
root: ../..
page_kind: system
source_name: "AVIDS2/memorix"
source_url: https://github.com/AVIDS2/memorix
archive_name: "AVIDS2--memorix"
revision: 7071a49c178f3ea7aa3eb811fa802da4c436f28e
revision_url: https://github.com/AVIDS2/memorix/commit/7071a49c178f3ea7aa3eb811fa802da4c436f28e
analyzed_at: 2026-09-16
capabilities: "scope_enforced, trust_state, human_review, negative_eval"
capability_evidence:
  scope_enforced: "a stored visibility resolved against the caller's bound project, agent and team membership, applied at every read seam and fail-closed for the narrow scopes | src/memory/visibility.ts:42-54, src/server.ts:621-637, src/store/orama-store.ts:1051, :1422, :1539, src/memory/session.ts:257, src/compact/engine.ts:257-304 | `canReadObservation` requires a bound project and an agent id before any personal or team record is visible, team additionally requires `isTeamMember === true`, and personal requires the caller be the creator or named in `sharedWithAgentIds`; the server's `getObservationReader` derives membership from the coordination store and the catch comment states the rule — \"A missing coordination store must never grant team visibility\" | tests/memory/long-term.test.ts:190 'keeps team memory unavailable without explicit active membership'"
  trust_state: "two stored state machines — an observation admission state and a long-term lifecycle — each filtering what is delivered | src/memory/admission.ts:15-29, src/memory/long-term-types.ts:11-19, src/memory/long-term.ts:123, :394-425 | `LONG_TERM_MEMORY_STATES` is `candidate`, `qualified`, `approved`, `archived`, `superseded`, and only `qualified` or `approved` are selectable for a task; `transitionMemory` runs in a transaction, refuses a transition whose current state is not the expected one, refuses to advance a record with no source evidence, and records an event carrying `fromState`, `toState` and a reason; observations carry an `admissionState` where `ephemeral` and `candidate` are excluded from automatic delivery | tests/memory/long-term.test.ts:44 'does not inject a candidate until it is explicitly qualified'; :227 'keeps an auditable lifecycle and removes archived records from delivery'"
  human_review: "a person advances a memory from candidate to qualified to approved from the CLI, giving a reason, and nothing reaches a task until they do | src/cli/commands/memory.ts:572-582, src/memory/long-term.ts:430-434 | `qualifyLongTermMemory` and `approveLongTermMemory` are reachable only through the `memorix memory` CLI, each requires a `reason` that is stored on the transition event, and the store refuses to advance a record that carries no evidence rows; a freshly created candidate returns zero results from `selectLongTermMemoriesForTask` until the person acts | tests/memory/long-term.test.ts:44"
  negative_eval: "a committed must-not selection assertion with the positive control in the same case | tests/memory/long-term.test.ts:190-224 | a team-scoped memory is created and qualified, then `selectLongTermMemoriesForTask` without membership asserts `.not.toContain(created.memory.id)` and the same call with `isTeamMember: true` asserts `.toContain(...)`; the candidate test at :44 pairs `toHaveLength(0)` before qualification with an exact-object match after it | tests/memory/long-term.test.ts:213"
stack_storage: "sqlite"
stack_retrieval: "vector, lexical, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "An observation — an entity, a type such as `decision`, `gotcha`, `trade-off` or `why-it-exists`, a project id, a visibility of `personal`, `team` or `project`, a creator agent, an optional shared-agent list, an `admissionState` and a `valueCategory`; separately a long-term memory of kind `episodic`, `semantic` or `procedural` with a scope, a lifecycle state, a portability and typed evidence rows"
  storage: "Local-first: SQLite plus an Orama search index under a project data directory, with a coordination store for team identity"
  retrieval: "A compact search, timeline and detail API over lexical and vector lanes with a code graph and reranking, plus `selectLongTermMemoriesForTask`, which filters on scope, lifecycle and portability before scoring"
  write: "MCP tools and agent hooks capture observations; long-term memories are created as candidates, manually or from evidence, and advance only through explicit transitions"
  update_delete: "Deduplication and consolidation merge project-visible observations only; retention and cleanup passes; a long-term record is archived or superseded, never silently rewritten, and each transition appends an event"
  scoping: "Project id plus a three-value visibility on observations; project, user or team scope with a project-bound or portable flag on long-term memories; team visibility requires an active coordination membership"
  integration: "An MCP server used by many agent hosts, a CLI, agent hooks and rules, a TUI, a dashboard, and packages for agent-core, ai and memcode"
  background: "Consolidation, deduplication, compaction checkpoints, freshness and retention passes, entity extraction and auto-relations"
  trust: "Admission state, the long-term lifecycle with required evidence and recorded reasons, an attribution guard, a secret filter, and a disclosure policy"
  strengths: "A visibility check applied at every read seam rather than at one gate; consolidation that refuses to merge personal or handoff records so they stay individually inspectable; a long-term ladder that will not advance a record without evidence and a stated reason"
  risks: "The MCP transfer tool's import inserts records verbatim — no visibility validation, no project re-stamping, no reader check, no admission gate — while export on the same tool is reader-filtered; an unrecognised visibility value resolves to project-wide and a missing admission state is treated as deliverable, both for upgrade compatibility; the module named `audit` tracks files written into the project rather than memory mutations"
---

## 1. Executive Summary

Memorix is a local-first shared memory layer for coding agents — Apache-2.0,
version 1.9.3, 833 commits since 14 February 2026, 292,812 lines of TypeScript
against 135,576 lines across 620 test files. It targets a long list of hosts
through MCP and its own hooks, and keeps everything on the machine.

Its memory has two tiers, and both are more carefully governed than the norm.

An **observation** carries a visibility — `personal`, `team` or `project` — and
`canReadObservation` is consulted at every seam that returns one: the MCP
server's handlers, the Orama store's search and hydration paths, the session
loader, and the compaction engine. The policy is fail-closed where it matters:
a personal or team record needs a bound project *and* an agent id before it is
visible at all, team needs `isTeamMember === true`, and the server derives
membership from the coordination store inside a `try` whose `catch` carries the
rule in a comment — "A missing coordination store must never grant team
visibility."

A **long-term memory** climbs a ladder. It is created as a `candidate`, and
`selectLongTermMemoriesForTask` will not return it. A person runs `memorix
memory qualify` and then `approve`, each with a reason; the transition runs in a
transaction, refuses to fire unless the record is in the expected state,
refuses to advance a record with no evidence rows, and appends an event
carrying `fromState`, `toState` and the reason. Archived and superseded records
drop out of delivery.

The discipline extends to the background work, which is where systems in this
corpus usually leak. Consolidation filters to project visibility before
clustering, with the reason written down: personal notes and targeted handoffs
"must remain individually inspectable and are never merged by a background job
or another agent's manual cleanup."

Against all of that stands one unchecked write. The `memorix` transfer MCP tool
has two actions. Export calls `exportAsJson(projectDir, project.id,
getObservationReader())`, so it returns only what the caller may read. Import
takes a JSON string, parses it, and hands it to `importFromJson`, which loops
over `data.observations` and inserts `{ ...obs, id: nextId++ }`. It does not
validate `visibility`, does not re-stamp `projectId`, does not check
`createdByAgentId` against the caller, does not consult a reader, and does not
apply the admission gate. Since an unrecognised visibility resolves to
`project` and a missing `admissionState` counts as deliverable, a crafted
payload writes project-wide, automatically-delivered memory attributed to any
project and any agent — through the same tool surface the agent already holds.

Four marks: `scope_enforced`, `trust_state`, `human_review`, `negative_eval`.

## 2. Mental Model

An **observation** is what an agent noticed: an entity, a type, a body, and the
provenance around it. Its **visibility** decides who sees it; its
**admissionState** decides whether it is delivered without being asked for.

A **reader** is the caller's identity: a bound project id, an agent id, and
whether that agent is an active team member. Every read takes one. A reader of
`undefined` returns true from the policy and is documented as reserved for
"trusted internal maintenance, not MCP delivery".

A **long-term memory** is a curated, durable lesson — episodic, semantic or
procedural — scoped to a project, a user or a team, marked `project-bound` or
`portable`, and backed by typed **evidence** rows whose relation is `supports`,
`verifies`, `derives` or `user-confirmed`.

A **lifecycle** is the ladder: `candidate` → `qualified` → `approved`, with
`archived` and `superseded` as exits. Only `qualified` and `approved` are
delivered.

```mermaid
%% caption: every read is fenced by the visibility policy and the lifecycle ladder; the transfer tool's import inserts records verbatim, skipping both
flowchart TB
    AGENT["coding agent over MCP"] --> CAP["capture observation"]
    CAP --> OBS[("observation<br/>projectId, visibility,<br/>createdByAgentId,<br/>admissionState")]
    MANUAL["memorix memory create"] --> CAND[("long-term memory<br/>state = candidate<br/>+ evidence rows")]
    CAND --> SEL1{"selectLongTermMemoriesForTask"}
    SEL1 -->|"candidate"| NONE["returns nothing"]
    PERSON["person runs qualify / approve<br/>with a reason"] --> TRANS{"transitionMemory<br/>in a transaction"}
    TRANS -->|"wrong current state"| ERR1["throws"]
    TRANS -->|"no evidence rows"| ERR2["throws — cannot advance"]
    TRANS -->|"ok"| ADV[("state = qualified / approved<br/>event: fromState, toState, reason")]
    ADV --> SEL2["delivered to a task"]
    OBS --> READ{"canReadObservation(record, reader)"}
    READ -->|"project"| P["visible if same project<br/>or an explicit global read"]
    READ -->|"team"| T["needs bound project + agentId<br/>+ isTeamMember === true"]
    READ -->|"personal"| PR["needs creator or<br/>sharedWithAgentIds"]
    READ --> SEAMS["applied at: server handlers,<br/>orama-store, session loader,<br/>compact engine, sdk"]
    CONS["consolidation / dedup"] --> ONLYP["filters to visibility === 'project'<br/>personal and handoffs never merged"]
    TOOL["memorix transfer tool"] --> EXP["action: export<br/>reader-filtered"]
    TOOL --> IMP["action: import<br/>JSON string from the caller"]
    IMP --> INS["importFromJson:<br/>insert { ...obs, id: nextId++ }"]
    INS -.->|"no visibility validation<br/>no projectId re-stamp<br/>no reader, no admission gate"| OBS
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `src/memory` | The model: `visibility.ts`, `admission.ts`, `long-term*.ts`, `consolidation.ts`, `deduplication.ts`, `retention.ts`, `freshness.ts`, `secret-filter.ts`, `attribution-guard.ts`, `disclosure-policy.ts` |
| `src/store` | The Orama index and the observation store, both applying the visibility filter |
| `src/server.ts` | The MCP server: reader construction, every tool handler, the transfer tool |
| `src/compact` | Compact search, timeline and detail — the bounded retrieval surface for one turn |
| `src/cli` | The CLI, including the `memory` command where qualification and approval live |
| `src/codegraph`, `src/rerank`, `src/embedding`, `src/knowledge` | Retrieval machinery and the knowledge-claim layer |
| `src/audit` | Tracks files Memorix wrote into a project (hooks, rules) for cleanup and rollback — not a memory mutation log |
| `packages/` | `agent-core`, `ai`, `memcode`, `tui` |

## 4. Essential Implementation Paths

- `src/memory/visibility.ts:42-54` — `canReadObservation`, the whole policy.
- `src/server.ts:621-637` — `getObservationReader`, and the fail-closed catch.
- `src/memory/long-term.ts:394-425` — `transitionMemory`.
- `src/memory/admission.ts:15-29` — the delivery gate and its legacy default.
- `src/memory/consolidation.ts:151-157` — why personal records are never merged.
- `src/memory/export-import.ts:157-212` — `importFromJson`.
- `src/server.ts:4268-4281` — the transfer tool's import branch.

## 5. Memory Data Model

Observations carry provenance and policy fields side by side: `projectId`,
`visibility`, `createdByAgentId`, `sharedWithAgentIds`, `admissionState`,
`valueCategory`, `topicKey`. The types that count as durable automatic captures
are enumerated — `decision`, `gotcha`, `problem-solution`, `trade-off`,
`why-it-exists` — which is a narrower and more opinionated set than most.

Long-term memories are deliberately separate, and the header says so: these
contracts are "intentionally separate from Observation provenance and Knowledge
Claim truth contracts." A long-term memory has a kind, a scope, a state, a
portability, `qualifiedAt` / `approvedAt` / `archivedAt` / `lastValidatedAt`,
and evidence rows typed by both source kind and relation.

## 6. Retrieval Mechanics

The compact API is the normal path for one coding turn, with an explicit
retrieval boundary that keeps accidental search-and-detail loops cheap and an
escape hatch when a caller genuinely needs history. Every one of those calls
passes a reader.

`selectLongTermMemoriesForTask` filters on scope, lifecycle and portability
before scoring, then ranks by similarity with a bonus for `approved` and a
freshness term derived from `lastValidatedAt` or the approval date. A
project-bound user memory stays in its project; an explicitly portable one
crosses.

## 7. Write Mechanics

Observation capture runs through the secret filter and the attribution guard.
Long-term creation produces a candidate and nothing else; the header on the
creation helper says it plainly — "Qualification and approval are deliberate
later transitions."

Import is the exception, and it is the one write that skips every check the
rest of the file applies. Its only guard is a dedup on `topicKey` scoped by the
`projectId` *in the payload*, which the payload also controls.

## 8. Agent Integration

An MCP server aimed at a long list of hosts, plus hooks, rules, a TUI and a
dashboard. Agents get the compact retrieval surface, capture tools and the
transfer tool. Qualification and approval are deliberately not MCP tools —
they are CLI commands, which is what makes the human-review mark real rather
than nominal.

## 9. Reliability, Safety, and Trust

**Import is the hole in an otherwise careful policy.** `exportAsJson` takes a
reader and returns only readable records. `importFromJson` takes a parsed
object and inserts each observation with a fresh id and everything else copied.
Three defaults compound it. `resolveObservationVisibility` maps any value that
is not `personal`, `team` or `project` to `project` — a deliberate upgrade
choice, since "[p]re-control-plane records were intentionally project-shared",
but it means an absent or misspelled visibility becomes project-wide.
`isEligibleForAutomaticDelivery` treats an absent `admissionState` as
deliverable, for the same compatibility reason. And nothing re-stamps
`projectId` to the importing project. The result is that the transfer tool can
write project-visible, automatically-delivered observations attributed to any
project and any agent id — and it is an MCP tool, so the agent holds it.

Two smaller notes. An explicit global read drops `projectId` from the reader,
and `canReadObservation` then allows project-visible records from other
projects; the comment states the intent and the narrow scopes stay fenced, so
this is a documented widening rather than a slip. And the module called `audit`
records which files Memorix wrote into a project so they can be cleaned up or
rolled back; it is not a mutation log for memory, and the only per-record
mutation history is the long-term tier's transition events. `audit_log` is
therefore withheld: no append-only record covers the observation write paths.

## 10. Tests, Evals, and Benchmarks

620 test files. `tests/memory/long-term.test.ts` is the one to read first: its
eight cases are each named for a property rather than a function, and they pair
a must-not with a positive control in the same body — nothing selected before
qualification and an exact match after, nothing selected without team
membership and the record returned with it, a portable user fact crossing
projects while a project-bound one stays home, and a portable candidate derived
from project evidence rejected outright.

## 11. For Your Own Build

### Steal

- **Put the visibility check at every seam that returns a record**, not at one
  gate. Memorix calls the same predicate from the server, the index, the
  session loader, the compaction engine and the SDK, which is why adding a
  retrieval path does not quietly add a bypass.
- **Refuse to advance a memory that has no evidence.** The transition throws
  rather than promoting an unsupported record, and the reason a person typed is
  stored on the event.
- **Exclude personal and handoff records from background merging**, and write
  down why. Consolidation is where privacy scopes usually die.
- **Keep promotion off the agent's tool surface.** Qualification and approval
  are CLI-only, so the thing being reviewed cannot approve itself.

### Avoid

- **An import that trusts its payload when the export beside it does not.** If
  every read is fenced and one write is not, the write is the policy.
- **Compatibility defaults that fail open on a field that decides visibility.**
  Defaulting an unknown visibility to project-wide is defensible for rows
  written before the field existed; applying the same default to rows arriving
  from outside is not the same decision.

### Fit

Reach for this if you want local-first shared memory across several agent hosts
with real per-agent and per-team scoping, and a curated tier a person controls.
Be deliberate about who can call the transfer tool.

## 12. Open Questions

- Should `importFromJson` re-stamp `projectId`, reject unknown visibility
  values, and drop `createdByAgentId` it cannot attribute to the caller? All
  three are one-line changes against the helpers already in the file.
- Should the import action be a CLI-only surface, like qualification, rather
  than an MCP tool?
- Does anything call the observation read path with `reader: undefined` outside
  maintenance? The bypass is documented; a type that made it unrepresentable on
  MCP paths would retire the question.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `src/memory/visibility.ts` | The read policy and its fail-closed reasoning |
| `src/memory/admission.ts` | The delivery gate and the legacy default |
| `src/memory/long-term-types.ts` | States, scopes, portability, evidence kinds |
| `src/memory/long-term.ts` | The transition machinery and its refusals |
| `src/memory/consolidation.ts` | Why personal records are never merged |
| `src/memory/export-import.ts` | The unchecked import |
| `src/server.ts` | Reader construction and the transfer tool |
| `src/cli/commands/memory.ts` | Where a person qualifies and approves |
| `tests/memory/long-term.test.ts` | Eight property-named tests worth copying |

## History

**2026-09-16** — [`7071a49c178f3ea7aa3eb811fa802da4c436f28e`](https://github.com/AVIDS2/memorix/commit/7071a49c178f3ea7aa3eb811fa802da4c436f28e) — first reading, at a commit dated 14 September 2026. Screened before opening, from a shallow clone: thirty-five files, three auto-run surfaces (`.gitmodules`, an `.opencode/` directory and an MCP server manifest declaring a start command), five build-time execution points, three unpinned surfaces, four dependency files inside the cooldown, and `CLAUDE.md` and `GEMINI.md` read as data. Nothing was installed, built or run.

---
title: Mercury Agent
eyebrow: Graded personal memory
description: A second-brain memory that grades every record on confidence, importance, and durability, keeps a subconscious tier below active recall, and lets the user pause learning entirely.
root: ../..
page_kind: system
source_name: cosmicstack-labs/mercury-agent
source_url: https://github.com/cosmicstack-labs/mercury-agent
archive_name: "cosmicstack-labs--mercury-agent"
revision: 781daac263507ed28800f380242507364137caec
revision_url: https://github.com/cosmicstack-labs/mercury-agent/commit/781daac263507ed28800f380242507364137caec
analyzed_at: 2026-09-18
capabilities: ""
capability_evidence:
stack_storage: "sqlite"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "`UserMemoryRecord` graded on confidence, importance, and durability"
  storage: "A better-sqlite3 database with an FTS5 virtual table kept current by insert, update and delete triggers, plus people and relation records"
  retrieval: "FTS5 over summary and detail, with a `LIKE` fallback over normalized terms; retrieval records `lastUsedAt` and `lastUsedQuery`"
  write: "Candidates with narrowed `evidenceKind`; `evidenceCount` on corroboration"
  update_delete: "`dismissed` boolean and `supersededBy`; no tombstone"
  scoping: "`durable`, `active`, `subconscious` tiers; single user"
  integration: "Internal, with a `brain/Memory.tsx` page offering per-record edit and delete, and a `/memory` chat menu carrying the shared-learning toggle"
  background: "A cloud pull — an incremental fetch of `shareable=1`, non-dismissed rows newer than a cursor"
  trust: "Four-way `evidenceKind`, corroboration counts, free-text provenance"
  strengths: "Durability separated from importance; a subconscious tier; a learning-pause switch"
  risks: "Scores estimated once at write time; dismissal is not durable; and `shareable` only ever ratchets upward automatically — a merge promotes a private record, nothing demotes one"
---

## 1. Executive Summary

Mercury is an MIT-licensed personal agent with a ~2,400-line memory subsystem — `user-memory.ts` (1,052 lines), `second-brain-db.ts`, `store.ts` — and a `brain/Memory.tsx` review page in its UI.

It is the smallest system in this batch and has the most opinionated record model. `UserMemoryRecord` carries **three independent graded scores** where most systems have one:

```typescript
confidence: number;   // how sure are we this is true
importance: number;   // how much does it matter
durability: number;   // how long should it last
```

Separating durability from importance is the unusual move. A fact can matter enormously today and be worthless next week (an active deadline) or matter mildly and hold for years (a dietary restriction). Systems that fold both into one "importance" field cannot express the difference, and their decay policies suffer for it — the atlas's [decay and reinforcement](../../patterns/decay-and-reinforcement/) pattern warns against applying one half-life to every memory kind, and this schema is what avoiding that looks like.

Three further details are distinctive:

**A subconscious tier.** `scope` is `durable | active | subconscious`. The first two are familiar; `subconscious` is a below-recall holding tier, counted separately in `UserMemorySummary.subconsciousTotal`. It is a middle state between "forgotten" and "in play" that almost nothing else here models.

**Learning can be paused.** `UserMemorySummary.learningPaused` exposes a switch that stops the agent forming new memories. For a personal assistant that observes continuously, a user-facing off switch is a genuine privacy control, and the atlas has not seen one before.

**Usage records the query, not just the count.** Alongside `lastUsedAt` sits `lastUsedQuery` — the actual query that last surfaced this memory. That is a far better debugging signal than a counter: it answers "why does this keep coming up?"

Reservations: `dismissed` is a boolean rather than a durable value-level tombstone, and no memory benchmark was found.

## 2. Mental Model

```typescript
interface UserMemoryRecord {
  id: string;
  type: UserMemoryType;
  summary: string;
  detail?: string | null;
  scope: 'durable' | 'active' | 'subconscious';
  evidenceKind: 'direct' | 'inferred' | 'manual' | 'system';
  source: 'conversation' | 'system';
  confidence: number;
  importance: number;
  durability: number;
  evidenceCount: number;
  provenance?: string | null;
  dismissed: boolean;
  supersededBy?: string | null;
  createdAt: number; updatedAt: number;
  lastSeenAt: number;
  lastUsedAt?: number | null;
  lastUsedQuery?: string | null;
}
```

A candidate is a strictly smaller shape, which is a good sign — a proposed memory cannot arrive pre-loaded with usage history or supersession:

```typescript
interface UserMemoryCandidate {
  type; summary; detail?;
  evidenceKind?: 'direct' | 'inferred';
  confidence; importance; durability;
}
```

Note that a candidate's `evidenceKind` is narrowed to `direct | inferred` — `manual` and `system` are reserved for records the extraction path cannot create.

Alongside user memories sit `UserPersonRecord` and `UserRelationMention`, so Mercury models **people and relations** as well as facts — a light social graph closer to [Honcho](../honcho/)'s peer modelling than to a flat preference store.

```text
conversation
  → candidate { evidenceKind: direct | inferred, confidence, importance, durability }
  → UserMemoryStore
      scope: durable | active | subconscious
      evidenceCount increments on corroboration
      dismissed / supersededBy for correction
  → retrieval → RetrievedUserMemory
      lastUsedAt, lastUsedQuery recorded
  → brain/Memory.tsx review UI
```

## 3. Architecture

- `src/memory/user-memory.ts` (1,052 lines) — `UserMemoryStore` and the record model.
- `src/memory/second-brain-db.ts` — persistence.
- `src/memory/store.ts`, `index.ts` — surface.
- `src/memory/user-memory.test.ts` — tests.
- `ui/src/pages/brain/Memory.tsx` — the operator review page.

```mermaid
%% caption: candidates reach a review page where a person dismisses or supersedes them, and a paused learning flag stops candidates being produced at all
flowchart TD
  Conv["Conversation"] --> Cand["UserMemoryCandidate"]
  Cand --> Store["UserMemoryStore"]
  Store --> DB["second-brain-db"]
  Store --> People["UserPersonRecord /<br/>UserRelationMention"]
  Q["Query"] --> Retr["retrieval"]
  DB --> Retr
  Retr --> Used["record lastUsedAt +<br/>lastUsedQuery"]
  DB --> UI["brain/Memory.tsx<br/>review page"]
  UI --> Dismiss["dismissed /<br/>supersededBy"]
  Pause["learningPaused"] -.blocks.-> Cand
```

## 4. Essential Implementation Paths

### Three scores instead of one

`confidence`, `importance`, and `durability` are orthogonal questions, and keeping them apart lets each drive a different mechanism: confidence should gate whether a memory is asserted, importance should influence ranking, and durability should drive decay. Systems in this atlas that conflate them end up with the failures the pattern library documents — [Holographic](../holographic/) folding truth and reachability into one `trust_score` is the clearest counterexample.

Whether Mercury actually uses all three independently was not traced end to end; the schema permits it, which is the precondition.

### The subconscious tier

A memory in `subconscious` scope is retained but below active recall, and `UserMemorySummary` reports its count separately from the total. This gives the system a graceful middle path: rather than deleting a memory that has stopped being useful, demote it, and keep the option of promotion if it becomes relevant again.

It also gives the user something honest to look at — "you have 412 memories, 180 of them subconscious" describes the store's real shape in a way a single total does not.

### `evidenceKind` and `evidenceCount`

`direct | inferred | manual | system` records *how* a memory came to exist, and `evidenceCount` counts corroborations. Together these support the write policy the atlas repeatedly recommends: a directly-stated fact corroborated three times should not be treated like a single inference. That the candidate type cannot set `manual` or `system` means the extraction path cannot forge provenance — a small but real integrity property, and the same instinct as [RainBox](../rainbox/)'s actor model, expressed through type narrowing rather than an actor enum.

### `lastUsedQuery`

Recording the query that last used a memory is the best small debugging affordance in this batch. Retrieval counters tell you a memory is popular; the query tells you *why*, which is what you need to diagnose a memory that keeps surfacing inappropriately. It is also exactly the input a human needs on a review page to judge whether a memory is earning its place.

### `learningPaused`

A user-facing switch that stops new memory formation. For an always-listening assistant this is a meaningful control, and it belongs in the same family as sensitivity levels and scoped exceptions — mechanisms that let a user shape what the system is allowed to know rather than only correcting it afterwards.

## 5. Memory Data Model

Persistence is `second-brain-db.ts`; people and relations sit alongside memories.

Gaps:

- **`dismissed` is a boolean on the record**, not a value-level tombstone. Dismissing memory X does not prevent an equivalent memory X′ from being extracted tomorrow with a fresh id — the laundering path the [rejected-value tombstone](../../patterns/rejected-value-tombstone/) pattern exists to close.
- **`provenance` is an optional string**, so the link back to evidence is free-text rather than a structured reference.
- **No scope beyond the three-level tier** — no project or workspace boundary, which is defensible for a single-user personal assistant and would not survive multi-user use.
- **No conflict state.** `supersededBy` records that a replacement happened; nothing marks two live memories as disagreeing.

## 6. Retrieval Mechanics

`RetrievedUserMemory` is the retrieval shape, and usage is recorded on every hit. The store is better-sqlite3 with an FTS5 virtual table, `memories_fts(summary, detail)`, kept current by insert, update and delete triggers rather than by a rebuild; a `LIKE` pass over normalized terms is the fallback when the query does not suit FTS. Ranking beyond that was not traced in detail; the three graded scores plus recency fields give the necessary inputs, and `subconscious` scope provides the filter that keeps demoted memories out of ordinary recall.

## 7. Write Mechanics

Candidates enter with `confidence`, `importance`, and `durability` already estimated, then become records. `evidenceCount` increments on corroboration rather than creating duplicates. `learningPaused` gates the whole path.

No verification tier was found — a candidate with high enough confidence appears to become a record without a separate promotion step, so the three scores are estimates made at extraction time rather than judgments earned over time.

## 8. Agent Integration

Memory is internal, with `brain/Memory.tsx` providing the review surface. That page is worth more than its size suggests: the atlas consistently finds that systems with an operator-facing memory view (RainBox's `/memory`, Magic Context's dashboard) develop better correction semantics, because someone can see what went wrong. The surface is real rather than decorative — each row carries edit and delete controls reaching `PUT` and `DELETE /api/brain/memory/:id` — but it is post-hoc: candidates are admitted, merged and conflict-resolved without passing a person.

### Memory can leave the machine, and the flag is a one-way ratchet

A `shareable` column gates an outward path. `src/index.ts:2683` answers a cloud command by fetching *"shareable memories newer than a cursor (incremental) … only `shareable=1`, non-dismissed rows with `updated_at > since`"*, indexed by `idx_memories_shareable_updated`.

The defaults are the careful part. The column is `INTEGER NOT NULL DEFAULT 0`, the migration that adds it backfills existing rows to `0` under the comment *"(private)"*, and the toggle behind it reads `config.memory.collaborativeKnowledge?.shareLearning ?? false`. Stamping is explicitly forward-only — *"existing memories are never retroactively flipped"* — and the chat toggle discloses both directions, telling the user on disable that *"(N memories already shareable are unchanged.)"*. A per-record `setShareable(id, boolean)` lets a person set or clear the flag by hand.

One path widens without a new decision. `mergeRecord` computes

```ts
const promoteShareable = candidate.shareable && existing.shareable !== 1;
```

and the comment states the intent: *"forward-only — never demotes a shareable memory."* So a memory recorded while sharing was off becomes shareable the moment a similar candidate arrives while sharing is on, and no automatic path moves it back. That is consistent with the rest of the merge, which takes `Math.max` of confidence, importance and durability — every merged field ratchets — but confidence and importance are rankings, and this one decides whether a record is eligible to leave the machine. The disclosure on disabling covers *new* memories; it does not cover an old private one being promoted later by a merge.

## 9. Reliability, Safety, and Trust

Strengths:

- **Three orthogonal grades** — confidence, importance, durability.
- **A subconscious tier** between active and forgotten.
- **Provenance kind with narrowed candidate types**, so extraction cannot claim manual or system origin.
- **Corroboration counting** rather than duplicate records.
- **`lastUsedQuery`** as a diagnostic signal.
- **A user-facing learning pause.**
- **An operator review page.**
- **People and relations modelled** alongside facts.

Gaps:

- **`dismissed` without a value tombstone**, so dismissal is not durable against re-extraction.
- **No verification tier** between candidate and record.
- **Free-text provenance.**
- **No conflict state.**
- **Single-user assumptions** throughout.
- **No memory benchmark.**

## 10. Tests, Evals, and Benchmarks

`user-memory.test.ts` sits beside the implementation. Nothing was run for this review, and no memory-quality benchmark was found.

The measurement this design invites is whether its three scores are independently predictive — whether `durability` estimated at write time actually predicts how long a memory stays useful. That is answerable from `lastUsedAt` history, and the data to answer it is already being recorded.

## 11. For Your Own Build

### Steal

- **Separate durability from importance.** How much a memory matters and how long it should last are different questions, and one field cannot answer both. This is the schema-level fix for the atlas's warning against a single global half-life.
- **A subconscious tier.** Demotion is a better default than deletion for memory that has merely stopped being relevant, and it gives you an honest way to describe the store's size.
- **Narrow the candidate type.** If extraction cannot construct `evidenceKind: 'manual'`, provenance cannot be forged — an integrity property enforced by the type system rather than by a check.
- **Record the query that used a memory**, not just a counter.
- **Give the user a pause switch** for learning.
- **Count corroborations on the record** instead of writing duplicates.

### Avoid

- **Dismissal without a tombstone**, in a system that extracts automatically.
- **Scores assigned once at extraction** with no path to revision.
- **Free-text provenance** that cannot be followed programmatically.
- **No conflict representation.**

### Fit

Borrow:

- The three-score model, especially the durability/importance split.
- The `durable | active | subconscious` tiering.
- The narrowed candidate type as a provenance-integrity trick.
- `lastUsedQuery`.
- The learning-pause control.

Do not copy:

- `dismissed` as a boolean if automatic extraction can regenerate the memory.
- Write-time score estimates as if they were earned confidence.

## 12. Open Questions

- Are the three scores used independently, or does ranking collapse them?
- What promotes or demotes a memory between `active` and `subconscious`, and is it reversible on use?
- Should dismissal write a value-level tombstone?
- Does `durability` estimated at extraction predict actual useful lifetime? The recorded usage data could answer this.
- How do person and relation records participate in retrieval?

## Appendix: File Index

- Record model and store: `src/memory/user-memory.ts` (`UserMemoryRecord`, `UserMemoryCandidate`, `UserMemorySummary`, `RetrievedUserMemory`, `UserPersonRecord`, `UserRelationMention`, `UserMemoryStore`).
- Persistence: `src/memory/second-brain-db.ts`, `src/memory/store.ts`.
- Surface: `src/memory/index.ts`.
- Review UI: `ui/src/pages/brain/Memory.tsx` (`onEdit` :317, `onDelete` :342, `handleSave`/`handleDelete`), and its routes at `src/web/api/brain.ts:156-180`.
- Sharing: the `shareable` column and its migration in `src/memory/second-brain-db.ts:119, 230-243`, the toggle and stamping in `src/memory/user-memory.ts:98, 290-302`, the promotion in `mergeRecord` :494-509, the cloud fetch in `src/index.ts:2683-2720`, the chat toggle in `src/core/agent.ts:6907-6957`.
- Tests: `src/memory/user-memory.test.ts`.

## History

**2026-09-18** — [`781daac263507ed28800f380242507364137caec`](https://github.com/cosmicstack-labs/mercury-agent/commit/781daac263507ed28800f380242507364137caec) — re-pinned from `31013b0`; 80 files and +493 lines, re-screened at the new pin. **Human review withdrawn**, leaving no capability mark. The edit and delete controls on the brain memory page are real and they reach the same better-sqlite3 database the agent reads — and they act on memories that are already stored and already retrievable. The [narrowed rubric](../../methodology/atlas-rubric/#human-review-surface) counts that as curation: the write has landed, and a person changing it afterwards is authoring rather than adjudicating.

The schema settles it. `memories` carries `type`, `categories`, `shareable`, `scope`, `evidence_kind`, `source`, `confidence`, `importance`, `durability`, `evidence_count`, `provenance` and a `dismissed` flag defaulting to `0` — so a memory is live the moment it is inserted, and `dismissed` is a soft delete applied later. There is no pending or proposed value anywhere in it.

The approval machinery the tree does carry is for something else: `approveTelegramPendingRequest`, `approveSignalPendingRequestByPairingCode`, `approveDiscordPendingRequest` and `approveSlackPendingRequest` admit a *person* to talk to the bot through a pairing code. That is access control over a channel, not admission control over a memory — the same distinction this atlas draws where an action queue sits beside a memory store.

**2026-09-14** — [`31013b0d0d64f0a4ea10432b5a55d975a7f9f2fe`](https://github.com/cosmicstack-labs/mercury-agent/commit/31013b0d0d64f0a4ea10432b5a55d975a7f9f2fe) — second reading, 55 commits on. Screened again: 0 auto-run surfaces, 2 build-time exec paths, 3 unpinned manifests and 2 dependency surfaces inside the seven-day cooldown; nothing was installed and nothing was run. Most of the diff is the website. `human_review` was re-tested at the producer — the brain page's per-row edit and delete reach `PUT` and `DELETE /api/brain/memory/:id` against the same database the agent reads — and holds; it carries the evidence record it had been asserted without, including the limit that candidates are admitted without passing a person. The stack row is promoted from seeded to reviewed and filled: better-sqlite3 with an FTS5 virtual table maintained by triggers and a `LIKE` fallback, which the seed recorded as unknown. The substantive addition since the previous pin is a `shareable` column gating an incremental cloud fetch. Its defaults are careful — column default `0`, existing rows backfilled private, the toggle `?? false`, stamping forward-only, and the chat surface disclosing that already-shareable memories are unchanged when sharing is switched off — but `mergeRecord` promotes an existing private record to shareable whenever a shareable candidate merges into it, and nothing demotes automatically.

**2026-07-27** — [`6e174a4b5ea77bbc753bff5f89c76db9303439d1`](https://github.com/cosmicstack-labs/mercury-agent/commit/6e174a4b5ea77bbc753bff5f89c76db9303439d1) — first reading.

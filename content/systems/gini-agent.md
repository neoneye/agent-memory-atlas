---
title: Gini Agent
eyebrow: Reimplemented memory model
description: A local reimplementation of the Hindsight memory model with four RRF-fused recall channels, bi-temporal units, an agent boundary tested in both directions — and a five-value trust model of which one value is ever written.
root: ../..
page_kind: system
source_name: Open-Curiosity/gini-agent
source_url: https://github.com/Open-Curiosity/gini-agent
archive_name: "Open-Curiosity--gini-agent"
revision: 6c5d85ed0ecd7fe8567124bd4890b16c329970d8
revision_url: https://github.com/Open-Curiosity/gini-agent/commit/6c5d85ed0ecd7fe8567124bd4890b16c329970d8
analyzed_at: 2026-09-19
capabilities: "trust_state, bitemporal, scope_enforced, negative_eval"
capability_evidence:
  scope_enforced: "every recall channel and the unit table | packages/runtime/src/memory/recall.ts:203, :242, :353, :383, packages/runtime/src/state/memory-db.ts:257 | `memory_units` carries `bank_id` and `agent_id`, and all four fused channels filter on both — the vector scan, the FTS join, the id rehydration and the temporal scan each read `WHERE bank_id = ? AND agent_id = ? AND status = 'active'`. `recall` throws when no `agentId` is supplied rather than defaulting | packages/runtime/src/memory/recall.test.ts:376 seeds two agents with **identical text and identical embeddings**, differing only in `agent_id`, and asserts in both directions that each agent's recall contains its own unit and not the other's; :410 asserts a fresh agent's pool is empty against a populated sibling; :429 asserts the missing-`agentId` call rejects"
  bitemporal: "the memory unit's time columns | packages/runtime/src/state/memory-db.ts:262-264, :271-272, packages/runtime/src/memory/temporal.ts | `occurred_start` and `occurred_end` record when the fact held, `mentioned_at` when it was said, and `created_at` / `updated_at` when the row was written — three distinct axes rather than one timestamp, with a temporal recall channel that matches units against a query date range | packages/runtime/src/memory/recall.test.ts:154 `matches units within the query date range`"
  trust_state: "the unit status, filtered on four reads — with three of its five values produced by no native path and reachable only through a migration importer | packages/runtime/src/state/memory-db.ts:96 (the union), :270 (the CHECK), :945-947 (the only native write), packages/runtime/src/memory/recall.ts:203, :242, :353, :383 (the filters), packages/runtime/src/integrations/openclaw-migrate.ts:3289-3301 and :3039 (the importer) | `status` is a CHECK-constrained five-value column — proposed / active / archived / rejected / conflicted — and all four recall channels admit only `active`, so any other value withholds the unit from retrieval. The producer test narrows the mark and the narrowing is more interesting than a flat absence. The only native write of a non-default status is `UPDATE memory_units SET status = archived` for observation rows; `proposed`, `rejected` and `conflicted` are produced by nothing in the engine. They are not unreachable, though: `coerceMemoryStatus` accepts all five from an imported OpenClaw record and passes the value through on insert, defaulting anything unrecognised to `active` — the most permissive value rather than a quarantine. So the vocabulary is inherited rather than dead, and an imported unit in one of those three states is stored, honoured by the filter and invisible, with no native transition back | no committed case asserts the filter; `packages/web/src/components/StatusPill.tsx:18` carries a colour for `conflicted`, so the interface is built to show a state the engine never produces"
  negative_eval: "the recall path across an agent boundary | packages/runtime/src/memory/recall.test.ts:376-408, :410-428 | `recall against one agent never surfaces another agent's units` inserts one unit per agent with the **same text and the same embedding**, so the only difference is `agent_id`, then asserts `fromA.units.some(e => e.unit.id === onlyB.id)` is `false` and the mirror for B — the exclusion is asserted by id, in both directions, through the real `recall` | each half carries its own positive control in the same expectation pair (`onlyA.id` present in A's result), so neither direction can pass on an empty pool; a second case asserts a fresh agent's pool is empty while a sibling agent's is populated"
stack_storage: "sqlite"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "`memory_units` with network, status, confidence, bi-temporal occurrence"
  storage: "SQLite (`memory_banks`, `entities`, `entity_mentions`, `memory_links`)"
  retrieval: "Four channels — semantic, BM25, graph spreading activation, temporal — fused by RRF then reranked"
  write: "`retain.ts`; `proposed` status as a candidate tier"
  update_delete: "A five-value status column of which only `archived` is ever written, by an observation-pruning statement; `proposed`, `rejected` and `conflicted` are declared and have no producer"
  scoping: "`agent_id` enforced across every channel and the HTTP API"
  integration: "CLI, HTTP, web UI"
  background: "`reflect.ts` consolidation, `reinforce.ts`"
  trust: "Per-unit `embedding_model`, source task and session ids"
  strengths: "Bi-temporal columns, an agent boundary asserted in both directions by a test that makes the two units identical apart from the key, and decisions kept as ADRs"
  risks: "Three of the five declared statuses have no writer anywhere in the tree, so the conflict and rejection model is a schema rather than a mechanism; no value tombstone"
---

## 1. Executive Summary

Gini is an MIT-licensed agent whose memory is a **local reimplementation of the Hindsight memory model** rather than an integration of it. The code says so directly:

> `recall.ts`: "This is Gini's local retrieval implementation for the hindsight memory model."
> `retain.ts`: "This is Gini's local retain implementation for the hindsight memory model."

It borrows the vocabulary — memory banks, memory units, retain/recall/reflect, four parallel recall channels — and implements them over its own SQLite schema in `state/memory-db.ts` (1,436 lines). The recall module cites the source paper's equation numbers (Eqs. 9–12), so this is a faithful implementation, not a loose homage.

That makes it the atlas's first **second implementation of a memory model it already documents**, which is interesting on its own. But two things make it worth reading independently of [Hindsight](../hindsight/).

**The unit schema is one of the richest here.** `memory_units` carries a `status` of `proposed | active | archived | rejected | conflicted` — including both a rejected state *and* an explicit conflicted state, which almost nothing else has — alongside a `network` of `world | experience | opinion | observation`, separate `occurred_start`/`occurred_end` and `mentioned_at` timestamps (bi-temporal), `embedding_model` and `embedding_dim` stored per unit, `confidence`, `agent_id`, and `source_task_id`/`source_session_id` provenance.

**Memory decisions are recorded as ADRs.** `docs/adr/agent-memory-isolation.md` documents making agent id the isolation key across all four recall channels, and states the failure that forced it: before isolation, "a 'coding' agent's pinned memories would pollute the 'research' agent's recall and vice versa." The atlas has thirty-odd systems and almost no written record of *why* any of them made the choices they did; Gini keeps one.

The main reservation is unusual for this atlas: the design is strong enough that the gaps are subtle — and the sharpest one is narrower than the first reading said. `conflicted` and `rejected` do not merely lack a resolution workflow: **nothing in the tree ever writes them.** A grep for either value across `packages/runtime/src`, excluding tests, returns the type union, the CHECK constraint and a set of unrelated promotion and pairing outcomes. The only production write of a non-default status is one statement, `UPDATE memory_units SET status = 'archived'` for `network = 'observation'` rows, and the generic setter that could write any status — `updateMemoryUnitStats` — has a single caller, which passes `lastUsedAt` and `bumpUsageCount`. The trust model is four-fifths schema. No memory-quality benchmark is committed either.

## 2. Mental Model

```sql
CREATE TABLE memory_units (
  id TEXT PRIMARY KEY,
  bank_id TEXT NOT NULL REFERENCES memory_banks(id) ON DELETE CASCADE,
  agent_id TEXT,                       -- isolation key
  text TEXT NOT NULL,
  embedding BLOB, embedding_dim INTEGER, embedding_model TEXT,
  occurred_start TEXT, occurred_end TEXT,   -- when it was true
  mentioned_at TEXT NOT NULL,               -- when it was said
  network TEXT NOT NULL
    CHECK (network IN ('world','experience','opinion','observation')),
  confidence REAL,
  metadata TEXT NOT NULL DEFAULT '{}',
  source_task_id TEXT, source_session_id TEXT,
  status TEXT NOT NULL DEFAULT 'active'
    CHECK (status IN ('proposed','active','archived','rejected','conflicted')),
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
)
-- plus memory_banks, entities, entity_mentions, memory_links, schema_meta
```

Three axes are worth separating out.

**Epistemic kind (`network`).** `world` (how things are), `experience` (what happened to me), `opinion` (a view held), `observation` (what was seen). Distinguishing an *opinion* from a *world fact* at the schema level is rare and consequential — a stated preference and a verifiable fact should not decay, conflict, or corroborate the same way.

**Lifecycle state (`status`).** `proposed` is meant as a candidate tier, `rejected` as a durable negative judgment, and `conflicted` as a unit known to disagree with another. The column is the best-designed trust vocabulary in this part of the corpus and three of its five values have no producer: at this commit the only status a unit can acquire after insertion is `archived`, and only by being an `observation` the pruning statement reached. The mark is carried on that one state, because it is written by live code and every recall channel admits `status = 'active'` only — a unit that acquires it is withheld from all four channels. What is not carried is the story the schema tells.

**Time.** `occurred_start`/`occurred_end` versus `mentioned_at` is [bi-temporal fact validity](../../patterns/bi-temporal-fact-validity/) — the pattern the atlas credits to [Graphiti](../graphiti/), implemented here as ordinary columns.

Recall:

```mermaid
%% caption: three retrieval channels — cosine, FTS5 BM25, and spreading activation seeded from the top semantic hits — each mapped to a numbered equation in the paper
flowchart LR
    Q["query"] --> SEM["semantic<br/><i>cosine vs query embedding, Eqs. 9–10</i>"]
    Q --> BM["bm25<br/><i>FTS5 MATCH on memory_units_fts, Eq. 11</i>"]
    Q --> GR["graph<br/><i>spreading activation from top semantic hits,<br/>decay δ=0.5, per-channel multipliers, Eq. 12</i>"]
    Q --> TM["temporal<br/><i>absolute or relative range parsed from the query;<br/>units whose occurred window overlaps it</i>"]
    SEM --> RRF["reciprocal rank fusion"]
    BM --> RRF
    GR --> RRF
    TM --> RRF
    RRF --> RK["rerank"] --> OUT["results"]

    style GR fill:#e7efe9,stroke:#3d6b59
```

Four channels, and the `agent_id` filter applies throughout rather than at the
end. The graph channel is the unusual one: it is **seeded from the top semantic
hits** rather than run independently, so traversal starts where similarity already
pointed.

## 3. Architecture

- `packages/runtime/src/memory/` — `retain.ts`, `recall.ts`, `reflect.ts`, `reinforce.ts`, `embedding.ts`, `entities.ts`, `temporal.ts`, `reranker.ts`, `schemas.ts`, `migrate.ts`, `migrate-pinned-to-user-md.ts`, plus `integration.test.ts` and per-module tests.
- `packages/runtime/src/state/memory-db.ts` (1,436 lines) — schema and storage.
- `packages/runtime/src/cli/commands/memory.ts` — CLI surface.
- `packages/web/` — query and view types for a memory UI.
- `docs/memory.md` and an extensive `docs/adr/` corpus.

```mermaid
%% caption: four retrieval channels fused by RRF then reranked, with reinforcement writing back to the units that were recalled
flowchart TD
  Task["Task /<br/>session"] --> Retain["retain.ts"]
  Retain --> Units["memory_units<br/>(banks, agent_id)"]
  Units --> Ent["entities / entity_mentions /<br/>memory_links"]
  Q["Query"] --> Recall["recall.ts"]
  Units --> Sem["semantic"]
  Units --> BM["bm25 (FTS5)"]
  Ent --> Graph["graph: spreading<br/>activation<br/>δ=0.5"]
  Units --> Temp["temporal<br/>(parsed<br/>range)"]
  Sem --> RRF["reciprocal<br/>rank fusion"]
  BM --> RRF
  Graph --> RRF
  Temp --> RRF
  RRF --> Rank["reranker.ts"]
  Rank --> Ctx["recalled context"]
  Ctx --> Reinf["reinforce.ts"]
  Units --> Refl["reflect.ts"]
```

## 4. Essential Implementation Paths

### Four channels, fused

`recall.ts` documents its channels and their equation provenance in a header comment, which is unusually good practice — a reader can check the implementation against the paper. The graph channel is spreading activation seeded from the top semantic hits with decay δ=0.5 and per-channel multipliers; the temporal channel only participates when the query actually contains a temporal expression, so it does not dilute fusion on queries where time is irrelevant.

Default channel weights appear in the module (`semantic: 1.0`, `temporal: 0.8`, among others), so fusion is tunable — though, as with most of the atlas, there is no committed evidence that the defaults are right. [MetaClaw](../metaclaw/) is the only system here that could answer that question.

### Per-agent isolation, as a documented decision

The ADR is worth quoting for its structure as much as its content. It records status and date, links related ADRs, states the decision (agent id is the isolation key; banks and units carry it; recall filters on it across all four channels; legacy rows carry `agentId`; `/api/memory*` filters by active agent), then gives the context — the cross-persona pollution that motivated it — and the consequence that a new agent starts with empty memory, config copied from defaults but content not.

"Configuration is copied at creation; content is not" is a small, precise rule that many systems get wrong by cloning too much or too little.

### Bi-temporal columns

Separating `occurred_start`/`occurred_end` from `mentioned_at` means a unit can record "the deploy failed on Tuesday" learned on Friday, and the temporal channel can match a query about Tuesday rather than about Friday. Graphiti achieves the same with edge validity intervals and a graph database; Gini achieves it with three columns and a range-overlap test, which is dramatically simpler and sufficient for unit-level facts.

### Embedder identity per unit

`embedding_model` and `embedding_dim` are stored on each unit rather than globally, so a model change does not silently invalidate the index — units embedded with different models are distinguishable and can be re-embedded selectively. The atlas praises [MemPalace](../mempalace/) for checking embedder identity and [Magic Context](../magic-context/) for keying embeddings by `(item, model_id)`; this is the same discipline.

### Migration as a first-class concern

`migrate.ts` and `migrate-pinned-to-user-md.ts` handle schema evolution and a specific data migration (pinned memories into a user Markdown file), and `memory-db.ts` comments describe an additive-column strategy where fresh installs get columns via `CREATE TABLE` while existing installs get them added. `schema_meta` tracks version.

## 5. Memory Data Model

Beyond `memory_units`, the schema carries `memory_banks`, `entities`, `entity_mentions`, and `memory_links` — an entity layer supporting the graph recall channel, and explicit links between units.

Gaps relative to the strongest models here:

- **`conflicted` and `rejected` are never written, let alone resolved.** The first reading recorded a missing resolution surface; the producer test at the re-read found there is nothing to resolve — no code path sets either value. Compare RainBox, whose four resolution options (supersede, reject, not-conflict, scoped exception) are the point of having the state, and which writes the state in the first place.
- **No rejected-*value* tombstone.** A rejected unit is a rejected row; nothing was found preventing an equivalent claim from being retained again under a new id.
- **`confidence` has no documented provenance** — how it is set, and whether anything updates it, was not traced.

## 6. Retrieval Mechanics

Genuine four-arm hybrid with RRF and reranking, agent-scoped throughout, with the temporal arm activating conditionally. `reinforce.ts` suggests retrieval feeds back into unit standing — the atlas's standing caution about popularity loops applies, and whether reinforcement touches `confidence` or only ranking is the question that matters. Keeping it out of `confidence` is the [MetaClaw](../metaclaw/) discipline; the schema here would permit either.

## 7. Write Mechanics

`retain.ts` is the write path; `reflect.ts` the consolidation pass; `proposed` status provides a candidate tier before a unit becomes `active`. Whether promotion from `proposed` is automatic or gated was not determined.

## 8. Agent Integration

A CLI (`cli/commands/memory.ts`), an HTTP surface (`/api/memory*`), and web query/view types indicate a memory UI. Agents are the isolation boundary, and the related ADR `agents-replace-profiles.md` explains that agents — not profiles — drive runtime behaviour, which is what made per-agent memory necessary.

## 9. Reliability, Safety, and Trust

Strengths:

- **A trust vocabulary worth copying**, `proposed`/`active`/`archived`/`rejected`/`conflicted` plus `confidence`, with the CHECK constraint that keeps it honest — noting that only `archived` is reached by any code here.
- **Epistemic kind on every unit**, separating opinion from world fact.
- **Bi-temporal columns**, cheaply.
- **Per-unit embedder identity.**
- **Four-channel recall with documented equation provenance.**
- **Agent-level isolation enforced across every channel and the HTTP API.**
- **Architecture decisions written down**, with the failure each fixed.
- **Versioned, additive schema migration.**

Gaps:

- **No writer at all** for the `conflicted`, `rejected` or `proposed` states, so there is no workflow to be missing.
- **No value-level tombstone**, so re-retention of a rejected claim appears possible.
- **Channel weights undefended** by any committed evaluation.
- **No memory-quality benchmark** found.
- **`reinforce` semantics unclear** — whether usage can move `confidence` is exactly the line the atlas cares about.

## 10. Tests, Evals, and Benchmarks

Per-module tests (`recall.test.ts`, `retain.test.ts`, `reflect.test.ts`, `embedding.test.ts`, `integration.test.ts`, `migrate-pinned-to-user-md.test.ts`) sit alongside the implementation, and `integration.test.ts` asserts end-to-end behaviour including that a follow-up task records recalled units. Nothing was run for this review.

**The isolation suite is the best thing in the file and this report missed it.**
`recall.test.ts`'s `describe("recall — per-agent isolation")` seeds two agents in
one instance with the *same text and the same embedding* — so the only difference
is `agent_id` — and then asserts, in both directions, that each agent's recall
contains its own unit and not the other's, by id:

```ts
const fromA = await recall(makeConfig(instance), { agentId: agentA, query: "swordfish" });
expect(fromA.units.some((entry) => entry.unit.id === onlyA.id)).toBe(true);
expect(fromA.units.some((entry) => entry.unit.id === onlyB.id)).toBe(false);
```

Making the two units identical apart from the key is what raises this above the
usual scope test: it cannot pass because the query happened to match one and not
the other. Two further cases assert that a fresh agent's pool is empty beside a
populated sibling, and that `recall` without an `agentId` rejects rather than
defaulting. `negative_eval` is carried from the 2026-09-17 reading on this
evidence.

No memory-quality benchmark was found. Given that the recall implementation cites specific equations from a published model, the natural evaluation — does this implementation reproduce the source model's reported behaviour? — is absent, and would be unusually easy to justify here.

## 11. For Your Own Build

### Steal

- **Write down memory decisions as ADRs.** Status, date, decision, context, consequences — and crucially the failure that motivated it. Across this whole corpus, Gini is the clearest example of a project that can explain itself.
- **`conflicted` as a first-class status.** Most systems either resolve conflicts silently or surface them outside the data model; making it a state means a conflicted unit can be found, counted, and worked through.
- **Epistemic kind as a column.** `world | experience | opinion | observation` costs one field and prevents a whole class of category errors.
- **Bi-temporal without a graph database.** Two occurrence columns plus a mention timestamp gets most of the value of temporal validity at unit granularity.
- **Store the embedding model on the row.**
- **Conditional temporal channel** — only fuse a time arm when the query has a time expression.
- **"Configuration is copied at creation; content is not."**

### Avoid

- **Modelled states without workflows** — `conflicted` and `rejected` need somewhere for a human to act.
- **Rejection without a value tombstone.**
- **Fusion weights as undefended defaults.**
- **Reinforcement of unclear reach.**

### Fit

Borrow:

- The `memory_units` schema more or less wholesale; it is among the best-shaped in the atlas.
- The ADR practice — the cheapest quality improvement available to any memory project.
- The conditional temporal channel and the per-unit embedder identity.

Do not copy:

- The trust states without building the workflow that resolves them.
- Fusion defaults without measuring them.

## 12. Open Questions

- What resolves a `conflicted` unit, and who sees it?
- Does `reinforce` touch `confidence`, or only ranking? The schema allows both; only one is safe.
- What promotes a unit from `proposed` to `active`?
- Does this implementation reproduce the source model's published retrieval behaviour? The equation citations invite the comparison.
- Should rejection write a value-level tombstone, given that retention is automatic?

## Appendix: File Index

- Schema and storage: `packages/runtime/src/state/memory-db.ts` (`memory_units`, `memory_banks`, `entities`, `entity_mentions`, `memory_links`, `schema_meta`).
- Write path: `packages/runtime/src/memory/retain.ts`.
- Retrieval: `packages/runtime/src/memory/recall.ts` (four channels, RRF), `reranker.ts`, `temporal.ts`, `entities.ts`.
- Consolidation and reinforcement: `reflect.ts`, `reinforce.ts`.
- Embeddings: `embedding.ts`.
- Migration: `migrate.ts`, `migrate-pinned-to-user-md.ts`.
- CLI: `packages/runtime/src/cli/commands/memory.ts`.
- Decisions: `docs/adr/agent-memory-isolation.md`, `docs/adr/agents-replace-profiles.md`, `docs/adr/prompt-cache-in-memory-tier.md`, `docs/adr/stable-system-prefix.md`, `docs/memory.md`.
- Tests: `packages/runtime/src/memory/*.test.ts`, `integration.test.ts`.

## History

**2026-09-19** — [`6c5d85ed0ecd7fe8567124bd4890b16c329970d8`](https://github.com/Open-Curiosity/gini-agent/commit/6c5d85ed0ecd7fe8567124bd4890b16c329970d8) — `trust_state` re-tested at an unchanged pin, and the negative half of the record needed the same treatment this sweep has been giving every negative claim. Natively it holds: the only `SET status` in production is `memory-db.ts:945`, writing `archived` for observation rows. But `proposed`, `rejected` and `conflicted` are not unreachable. `coerceMemoryStatus` (`packages/runtime/src/integrations/openclaw-migrate.ts:3297-3301`) accepts all five values from an imported OpenClaw record and passes the value through on insert (`:3039`), defaulting anything unrecognised to `active` — the most permissive value rather than a quarantine. So the vocabulary is inherited rather than dead, and the consequence is worth stating: an imported unit in one of those three states is stored, honoured by the filter and therefore invisible, with no native transition back to `active`. The filter itself is at four reads rather than the one recorded (`memory/recall.ts:203`, `:242`, `:353`, `:383`). One smaller observation beside it: the web UI carries a red pill style for `conflicted` (`packages/web/src/components/StatusPill.tsx:18`), so the interface is built to display a state the engine never produces on its own. Re-read from a fresh clone; nothing was installed and no suite was run.

**2026-09-17** — [`6c5d85ed0ecd7fe8567124bd4890b16c329970d8`](https://github.com/Open-Curiosity/gini-agent/commit/6c5d85ed0ecd7fe8567124bd4890b16c329970d8) — re-read at the same commit, still the tip; the last commit upstream removes a README section. Nothing in the code could have moved, so this reading audited the first one. Screened again: no auto-run surface, no build-time execution path, four unpinned manifests, nothing inside the cooldown; `AGENTS.md` and `CLAUDE.md` were read as data. Nothing was installed or run.

**`negative_eval` is added, on the best scope test in this part of the corpus.** `recall.test.ts` seeds two agents in one instance with the same text *and the same embedding*, so the only difference between the two units is `agent_id`, then asserts in both directions that each agent's recall contains its own unit and not the other's, by id. Making the units identical apart from the key removes the usual escape — it cannot pass because the query matched one and not the other. Two further cases assert an empty pool for a fresh agent beside a populated sibling, and that `recall` without an `agentId` rejects.

**The trust model is four-fifths schema, which the first reading reported as a missing workflow.** It recorded that `conflicted` and `rejected` exist without a resolution surface. The producer test run at this reading found there is nothing to resolve: no path in `packages/runtime/src` writes either value, nor `proposed`. The only production write of a non-default status in the tree is `UPDATE memory_units SET status = 'archived'` for `network = 'observation'` rows, and the generic setter that could write any status has one caller, which passes `lastUsedAt` and `bumpUsageCount`. `trust_state` is still carried — `archived` is written by live code and every recall channel admits `status = 'active'` only, so acquiring it withholds a unit from all four — but the mark now rests on one state rather than five, and the evidence record says so.

Everything else held: four channels fused by RRF, each filtering `bank_id` and `agent_id`; `occurred_start`/`occurred_end` and `mentioned_at` kept apart from `created_at`/`updated_at`; ADRs recording the failures that motivated the decisions. Marks go from three to four, all four now carrying evidence records. `stack_source` moves from `seeded` to `reviewed`.

**2026-07-27** — [`6c5d85ed0ecd7fe8567124bd4890b16c329970d8`](https://github.com/Open-Curiosity/gini-agent/commit/6c5d85ed0ecd7fe8567124bd4890b16c329970d8) — first reading.

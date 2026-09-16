---
title: "bwmem"
eyebrow: "The migration that added the second time axis says what question the first one could not answer"
description: "A per-user memory SDK on Postgres whose facts carry both time axes, whose four-value status keeps three of them out of every read, and whose corrections table records the old value, the new one and why."
root: ../..
page_kind: system
source_name: "Bitwarelabscom/bwmem"
source_url: https://github.com/Bitwarelabscom/bwmem
archive_name: "Bitwarelabscom--bwmem"
revision: a0f7c194121f7b89afa0439bcca44c86d66d0e99
revision_url: https://github.com/Bitwarelabscom/bwmem/commit/a0f7c194121f7b89afa0439bcca44c86d66d0e99
analyzed_at: 2026-09-16
capabilities: "trust_state, bitemporal, scope_enforced, audit_log"
capability_evidence:
  bitemporal: "a migration that names the question the first axis could not answer, and a read taking both instants | src/db/migrations/007_bi_temporal_facts.sql:1-27, src/memory/facts.service.ts:437-458 | the migration header states the distinction before any DDL: the table already had `valid_from`/`valid_until`, and \"[w]hat was missing is the second time axis — WHEN WE CHANGED OUR BELIEF — distinct from when something was true. Without this you can't honestly answer 'what did we believe about X on date Y' — you can only answer 'what was true on date Y.'\" It then defines each column in one line apiece and writes the composed query out. `getFactsAsOf(userId, asOfValidTime, asOfTxnTime)` implements exactly that, with the two predicates carrying their own comments — \"transaction-time: known to us, not yet superseded as of asOfTxnTime\" against \"valid-time: was true in the world at asOfValidTime\" — and both parameters defaulting to now, so the ordinary call is the point-in-time call with today's instants | the axes are fed from different places: `recorded_at` is stamped by the write and `superseded_at` by `NOW()` at the moment of belief change, while `valid_from`/`valid_until` are carried through extraction as the fact's own claim about the world"
  trust_state: "a four-value status constrained in the schema, with three values excluded from every read | src/db/migrations/001_core.sql:49-50, :65, src/memory/facts.service.ts:304-306, :395-397, src/memory/quality-scorer.service.ts:402, src/memory/fact-collision.service.ts:421 | `fact_status` is `VARCHAR(20) DEFAULT 'active'` under `CHECK (fact_status IN ('active', 'overridden', 'superseded', 'expired'))`, so the vocabulary is closed by the database rather than by convention. Every read path filters to `fact_status = 'active'`, and the partial index `ON facts(user_id, category) WHERE fact_status = 'active'` is built for exactly that predicate, which is a second, structural statement that the active set is the read set. A fact that was overridden, superseded or expired keeps its row, its lineage through `supersedes_id`, and its place in the bitemporal history, while dropping out of what the bot is given | the filter is repeated identically in the retrieval, search, quality-scoring and collision paths, and the expiry case is doubled in the same clause — `NOT (fact_type = 'temporary' AND valid_until IS NOT NULL AND valid_until <= NOW())` — so a temporary fact past its window is withheld before any sweep marks it"
  scope_enforced: "a per-user key on every stored fact, required by every read signature and present in every query | src/memory/facts.service.ts:274, :366, :442, :645, :671, :744, src/db/migrations/001_core.sql:65-67, src/memory/contradiction.service.ts:227-231 | `user_id` is stored on the fact and is the first bound parameter of every read: `WHERE user_id = $1` appears in the retrieval, full-text, as-of, quality and collision queries, and the contradiction check correlates `f.user_id = c.user_id` rather than matching a key alone. The service signatures make it non-omittable — every public read takes `userId: string` as a required first argument, with no default and no unscoped variant — and the indexes are keyed `(user_id, …)`, so the scope is what the query planner uses rather than a filter applied after the fact. Migration 007 adds a second, narrower axis beside it: `intent_id`, \"optional scope so the same fact key can hold different values in different conversation threads (e.g., a multi-turn task with its own facts that should not bleed into the user's general facts)\" | no read of the facts table anywhere in the tree omits the user predicate, and there is no administrative path that reads across users"
  audit_log: "an append-only corrections table carrying the old value, the new one, the kind of change and its reason | src/db/migrations/007_bi_temporal_facts.sql:25-27, src/memory/facts.service.ts:590-621 | `fact_corrections` is described in the migration as an \"append-only audit log of every supersession, so you can answer 'how did we come to believe what we believe'\", and the insert sits directly after the supersession in the same client transaction, recording `user_id`, `fact_key`, `old_value`, `new_value`, a correction type and a reason. Coverage is complete for this store because nothing is ever deleted: there is no `DELETE FROM facts` anywhere in the tree, so the mutation set is creation — recorded by the row's own `recorded_at` — and supersession, which sets `fact_status` and `superseded_at` and writes the correction row. The design choice worth naming is the inverse of the one [Verimem](../verimem/) argues for: bwmem puts both values in the log in the clear, which is what makes \"how did we come to believe this\" answerable and what makes an erasure request reach two tables instead of one | the correction type distinguishes a `temporary_override` from a `correction`, so a value displaced by a short-lived fact is not confused with one that was wrong"
stack_storage: "postgres"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A per-user fact — key, value, category, type, confidence, both validity bounds, both transaction bounds, a status, a lineage link and an override priority — beside messages, sessions, held intentions and emotional capture"
  storage: "PostgreSQL with pgvector for facts and embeddings, Redis for session state, and Neo4j optionally for the knowledge graph"
  retrieval: "Full-text and semantic search over active facts, with relevance scoring, collision handling and a context builder that assembles the prompt block"
  write: "Messages are recorded and facts extracted in the background, with contradiction detection and a quality scorer running over what was written"
  update_delete: "A correction supersedes: the old row keeps its lineage, takes a status and a `superseded_at`, and a corrections row records both values; nothing is deleted"
  scoping: "`user_id` stored on every fact and required by every read signature, with `intent_id` as an optional narrower scope for a conversation thread"
  integration: "A TypeScript SDK to drop into a chatbot, with a Docker compose stack for the three services it needs"
  background: "Multi-stage consolidation, fact extraction, sentiment analysis, response-quality scoring and dedup passes"
  trust: "A CHECK-constrained status vocabulary, confidence and override priority on a fact, contradiction detection over active values, and a corrections log with reasons"
  strengths: "The migration that introduced the second time axis is the document to read, because it states the problem before the solution: the table already had validity bounds, and \"[w]hat was missing is the second time axis — WHEN WE CHANGED OUR BELIEF — distinct from when something was true. Without this you can't honestly answer 'what did we believe about X on date Y' — you can only answer 'what was true on date Y.'\" It then defines each of the four columns in a line, writes out the composed predicate, and ships `getFactsAsOf(userId, asOfValidTime, asOfTxnTime)` with both instants defaulting to now — so the ordinary read and the historical read are the same code path with different arguments, and the historical one cannot rot separately. The status vocabulary is enforced by a `CHECK` rather than by application code, and the partial index is built on `WHERE fact_status = 'active'`, which makes the active set the read set at the planner level as well as in the predicate"
  risks: "The corrections log carries `old_value` and `new_value` in the clear, which is what makes the lineage answerable and also means an erasure request has to reach the corrections table as well as the fact — the opposite trade from the one argued a report earlier, and there is no purge path here that reaches both. Nothing is keyed on a rejected value, so a corrected fact can be re-extracted from a later message and written again as active. There is no human surface: this is an SDK, corrections come from extraction and contradiction detection rather than from a person, and the `reason` on a correction row is a fixed string chosen by the code (\"Value correction\", \"Temporary override\") rather than an explanation anybody wrote. The committed tests are unit-level — SQL shape, context formatting, consolidation gating — with no store-level case asserting that a superseded or another user's fact fails to come back, which is the assertion this design would most benefit from pinning. And the runtime is three services: Postgres with pgvector, Redis, and Neo4j when the graph is on"
---

## 1. Executive Summary

bwmem is a "Memory SDK for AI chatbots" giving "your bot persistent, per-user
memory: bi-temporal facts, semantic search, emotional capture, contradiction
detection, quality scoring, session-texture carryover, held intentions,
knowledge graph, and multi-stage consolidation." AGPL-3.0, TypeScript, version
0.11.2, 17,259 lines across 105 files, on PostgreSQL with pgvector, Redis, and
optionally Neo4j. It is extracted from Luna, the vendor's longer-running agent
system.

**The document worth reading is a migration.** `007_bi_temporal_facts.sql` opens
by stating what the schema could not do before it:

> "The facts table already has valid_from / valid_until (when a fact was true in
> the world) and supersedes_id (lineage). What was missing is the second time
> axis — WHEN WE CHANGED OUR BELIEF — distinct from when something was true.
> Without this you can't honestly answer 'what did we believe about X on date
> Y' — you can only answer 'what was true on date Y.'"

It then defines each column in a single line, writes out the composed query, and
`getFactsAsOf(userId, asOfValidTime, asOfTxnTime)` implements it with both
instants defaulting to now. That default is the part that matters: the ordinary
read and the historical read are the same function with different arguments, so
the historical path cannot quietly break while the current one keeps working —
the failure the atlas found two reports into this same family.

**The status vocabulary is enforced by the database.** `fact_status` is
constrained to `active`, `overridden`, `superseded` and `expired`, every read
filters to `active`, and the partial index is built `WHERE fact_status =
'active'` — so the active set is the read set in the planner as well as in the
predicate. A superseded fact keeps its row, its lineage and its place in the
bitemporal history while leaving what the bot is handed.

**Scope is the other thing done without a gap.** `user_id` is stored on every
fact, is the first bound parameter of every read, and is a required argument with
no unscoped variant; the indexes are keyed on it. Migration 007 adds `intent_id`
beside it for facts that belong to one conversation thread "and should not bleed
into the user's general facts."

**The trade to notice is in the corrections log.** `fact_corrections` records
`old_value` and `new_value` in the clear, which is exactly what makes "how did we
come to believe what we believe" answerable — and exactly what
[Verimem](../verimem/), read a report earlier, argues an immutable log must never
contain, because it turns erasure into a contradiction. Both positions are
defensible; what bwmem does not have is a purge path that reaches both tables.

## 2. Mental Model

A **fact** is per-user, keyed, and never deleted.

A **status** is one of four, and only one of them is readable.

A **correction** writes a row saying what the value was, what it became, and why.

An **as-of read** is the ordinary read with two instants supplied.

```mermaid
%% caption: facts carry validity bounds and transaction bounds on the same row, every read is scoped to a user and filtered to the active status, and a supersession writes both a status change and a corrections row in one transaction
flowchart TB
    MSG["a message"] --> EX["background extraction:<br/>fact key, value, category, type,<br/>valid_from / valid_until"]
    EX --> NEW[("facts: user_id · intent_id · fact_key · fact_value<br/>valid_from · valid_until — when it was TRUE<br/>recorded_at · superseded_at — when we BELIEVED it<br/>fact_status · supersedes_id · override_priority")]
    CHK["CHECK (fact_status IN ('active','overridden','superseded','expired'))"] --> NEW
    CONTRA["contradiction detection over<br/>ACTIVE values for the same key,<br/>correlated on f.user_id = c.user_id"] --> SUP
    SUP{"a correction"} --> S1["UPDATE facts SET fact_status = ...,<br/>superseded_at = NOW()"]
    SUP --> S2["INSERT INTO fact_corrections<br/>user_id · fact_key · old_value · new_value ·<br/>correction_type · reason"]
    S1 & S2 -.->|"one client transaction, and there is no<br/>DELETE FROM facts anywhere in the tree"| KEPT["the row keeps its lineage<br/>and leaves the read set"]
    S2 -.->|"old and new values in the clear —<br/>what makes the lineage answerable, and what<br/>makes an erasure reach two tables"| TRADE["the opposite trade from a hash-only chain"]
    NEW --> READ["every read: WHERE user_id = $1<br/>AND fact_status = 'active'"]
    READ -.->|"userId is a required first argument on every<br/>public read; no unscoped variant exists, and the<br/>indexes are keyed (user_id, …)"| SCOPED["the scope is the plan, not a post-filter"]
    READ --> TEMP["AND NOT (fact_type = 'temporary'<br/>AND valid_until <= NOW())"]
    TEMP -.->|"a temporary fact past its window is withheld<br/>before any sweep marks it expired"| SAFE["expiry does not wait for a job"]
    ASOF["getFactsAsOf(userId, asOfValidTime, asOfTxnTime)<br/>both default to now"] --> P1["recorded_at at or before txn instant,<br/>and superseded_at null or after it"]
    ASOF --> P2["valid_from null or at or before valid instant,<br/>and valid_until null or after it"]
    P1 & P2 -.->|"'what we believed at txn_time<br/>about state at valid_time'"| ANS["the ordinary read IS the historical read,<br/>so the historical path cannot rot alone"]
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `src/db/migrations/` | The schema, with the reasoning in the migration headers |
| `src/memory/facts.service.ts` | Writes, supersession, the corrections row, the as-of read |
| `src/memory/contradiction.service.ts` | Held contradictions over active values for one user |
| `src/memory/quality-scorer.service.ts` | Response scoring against what the store holds |
| `src/consolidation/` | The multi-stage background passes |
| `src/graph/` | Optional Neo4j sync, non-blocking and counted on failure |

## 4. Essential Implementation Paths

`src/db/migrations/007_bi_temporal_facts.sql:1-27` — the problem, the four
columns, and the composed query, before any DDL.

`src/memory/facts.service.ts:437-458` — both axes as parameters, each predicate
commented with the question it answers.

`src/db/migrations/001_core.sql:49-50`, `:65` — a status constrained by the
database and indexed on its own predicate.

`src/memory/facts.service.ts:590-621` — a supersession and its audit row in one
transaction.

## 5. Memory Data Model

A fact carries a user, an optional intent, a key and value, a category and type,
a confidence, an override priority, both validity bounds, both transaction
bounds, a status and a lineage link. Messages, sessions, held intentions and
emotional capture sit beside it, and `fact_corrections` records every belief
change.

## 6. Retrieval Mechanics

Full-text search with `to_tsquery` and semantic search over pgvector, both
scoped to the user and filtered to active facts, with a temporary-fact expiry
clause applied in the same predicate rather than depending on a sweep. A context
builder assembles what reaches the prompt.

## 7. Write Mechanics

Messages are recorded, facts extracted in the background, and a conflicting
value supersedes rather than overwrites: status and `superseded_at` on the old
row, a new row with `supersedes_id`, and a corrections row naming both values.
Graph sync is fire-and-forget with a counter on failure, so the optional service
cannot block a write.

## 8. Agent Integration

An SDK rather than a server: record messages, build context, inject into the
prompt. A Docker compose file brings up Postgres, Redis and Neo4j for local use.

## 9. Reliability, Safety, and Trust

The strong parts are the two axes with one read path, a status the database
constrains, and a user scope no read omits. The gaps are a corrections log that
stores plaintext values with no purge that reaches it, no value-keyed record to
stop a corrected fact being re-extracted, no person anywhere in the loop, and
tests that stop at the unit level.

## 10. Tests, Evals, and Benchmarks

Vitest unit tests over SQL shape, context formatting, consolidation gating,
contradiction handling and embedding behaviour. There is no store-level case
asserting that a superseded fact or another user's fact fails to come back,
which for a design that rests on exactly those two predicates would be the
cheapest assertion to add.

## 11. For Your Own Build

Write the migration header the way this one is written. Stating the question the
old schema could not answer, before the DDL, is what makes a second time axis a
decision rather than two more columns.

Default both as-of parameters to now. If the historical read is a separate
method, it will break separately and later.

Constrain the status in the database and index on the predicate you filter with.
It makes the active set the read set in two places instead of one.

Decide whether your audit log may hold values, and know what you are trading. In
the clear it answers how a belief formed; hashed or omitted it keeps erasure
possible. Either is defensible; having neither answer is not.

## 12. Open Questions

Whether an erasure path is planned that reaches `fact_corrections`. The facts
table is append-only by design and the corrections table holds the same values,
so a user's request to be forgotten currently has two places to go and one
mechanism.

Whether the `reason` column is meant to carry an explanation. It is populated
with one of two fixed strings today, and a column named `reason` in an audit log
invites a reader to expect the sentence somebody wrote.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `src/db/migrations/007_bi_temporal_facts.sql:1-27` | The clearest statement of why one time axis is not enough |
| `src/memory/facts.service.ts:437-458` | One read path serving both the current and the historical question |
| `src/db/migrations/001_core.sql:49-50`, `:65` | A status the database enforces and the index agrees with |
| `src/memory/facts.service.ts:590-621` | A supersession and its audit row, in one transaction |

## History

**2026-09-16** — [`a0f7c194121f7b89afa0439bcca44c86d66d0e99`](https://github.com/Bitwarelabscom/bwmem/commit/a0f7c194121f7b89afa0439bcca44c86d66d0e99) — first reading, at a commit dated 12 September 2026. Screened before opening, from a shallow clone: no auto-run surfaces, one build-time execution point, one unpinned dependency surface and two dependency files inside the seven-day cooldown, with `package-lock.json` present. Nothing was installed, built or run; no PostgreSQL, Redis or Neo4j was started, so the SQL described here is read from the migrations and the service source rather than executed.

---
title: "Hippo"
eyebrow: "Physics-model decay memory"
description: "A TypeScript memory layer that gives every entry mass, charge and temperature, and whose scope boundary is enforced in the query and suspended on purpose for consolidation."
root: ../..
page_kind: system
source_name: "kitfunso/hippo-memory"
source_url: https://github.com/kitfunso/hippo-memory
revision: a9c7cca3613b6571bfb37ad1fb6c070b7c976197
revision_url: https://github.com/kitfunso/hippo-memory/commit/a9c7cca3613b6571bfb37ad1fb6c070b7c976197
analyzed_at: 2026-08-04
capabilities: "trust_state, bitemporal, scope_enforced, audit_log"
matrix:
  memory_unit: "A memory row carrying strength, half-life, layer, emotional valence, schema fit, outcome score and a confidence level"
  storage: "SQLite with FTS5 and a 25-plus-step migration ladder; separate tables for conflicts, goals, policies, decisions, processes and audit"
  retrieval: "Hybrid BM25 plus vector with RRF, MMR rerank, a temporal-direction boost, and a physics pass over mass, charge and temperature"
  write: "`capture` extracts items from transcript text; CLI, HTTP and MCP writes; auto-learn from a repository"
  update_delete: "Record-keyed supersession honoured on read, plus a hard `forget`; no rejected-value record, so re-assertion is unguarded"
  scoping: "`tenant_id` as a read-path predicate on the API; the CLI is single-tenant-per-process by design and `sleep` is host-wide behind a loopback and admin gate"
  integration: "31 HTTP routes, an MCP server, and a large CLI"
  background: "A six-phase `sleep`: consolidation, dedup, quality audit that hard-deletes, auto-share, ambient state, graph extraction drain"
  trust: "`verified | observed | inferred | stale`, where only the first three are stored and `stale` is derived from disuse at 30 days"
  strengths: "A scope boundary enforced in the query and deliberately suspended for consolidation, fenced at the transport layer instead; a retention prune that records its own execution"
  risks: "Staleness is computed from retrieval recency rather than from evidence; the quality audit deletes host-wide; correction is record-keyed with no tombstone"
---

## 1. Executive Summary

Hippo is a **memory layer for coding agents** in 42,482 lines of TypeScript,
MIT, with 376 test files and a migration ladder past twenty-five steps. Its
README leads with a thesis this atlas agrees with — *"The secret to good memory
isn't remembering more. It's knowing what to forget"* — and the gap between that
sentence and the mechanism behind it is the most useful thing in the report.

**The design idea is a physics model.** Every entry gets a `mass` computed from
strength and retrieval count, a `charge` mapped from emotional valence, and a
`temperature` that decays with age (`src/physics.ts`). Retrieval is then a
hybrid of BM25 and vector similarity fused and MMR-reranked
(`src/search.ts:344`, `:801`), with an optional `physicsSearch` (`:861`) ranking
by those derived quantities instead. Whether the metaphor earns its keep is an
open question below; what it demonstrably buys is a single place where recency,
frequency and affect combine into one number.

**The strongest thing here is not the physics — it is the scope architecture.**
`tenant_id` is a real read-path predicate, and every place it is *omitted* is
deliberate and documented. The API recall path passes it. The CLI omits it at
fifteen-plus sites under a comment stating that `cli.ts` is
single-tenant-per-process. And `sleep` omits it and hard-deletes host-wide,
which would be a cross-tenant delete except that `/v1/sleep` is **loopback-only
and admin-gated**, with the 403 naming the reason. The boundary is enforced in
the query on the read path and deliberately suspended for consolidation, with
the suspension fenced at the transport layer instead. That is a position, not an
oversight, and the version reference in the error string says the project met
the hazard in production.

**The weakest thing is what the tagline promises.** The word *tombstone* appears
nowhere in `src/`. `forget` (`src/api.ts:1677`) resolves to
`DELETE FROM memories` (`src/store.ts:1654`). Correction is real and extensive —
453 occurrences of `superseded`, a `superseded_by` pointer honoured on read
(`src/ambient.ts:57`) — but it is **record-keyed**: it hides a row and does
nothing to stop the same value being re-asserted by a later extraction. For a
project whose stated secret is knowing what to forget, forgetting is a hard
delete with an audit row.

Second weakness, and subtler: **staleness is computed from disuse, not from
evidence.** See section 2.

## 2. Mental Model

A memory is a **row in SQLite** carrying `strength`, `half_life_days`, `layer`,
`tags_json`, `emotional_valence`, `schema_fit`, `outcome_score`,
`conflicts_with_json`, `pinned` and `confidence` (`src/db.ts:47`).

`confidence` is the epistemic axis and it is a discrete state, not a score:
`ConfidenceLevel = 'verified' | 'observed' | 'inferred' | 'stale'`
(`src/memory.ts:23`). **Only the first three are ever stored.**
`resolveConfidence` (`src/memory.ts:447`) short-circuits on `pinned` or
`verified`, then returns `'stale'` when `last_retrieved` is more than thirty
days old, otherwise the stored value.

That is worth stating plainly, because it is the design's quiet substitution: a
memory goes stale **because nobody looked at it**, not because anything
suggested it stopped being true. A verified fact is exempt; an `observed` one
that happens to be both correct and unfashionable is marked stale on a fixed
thirty-day threshold. The other three values in that union are epistemic, so a
reader sees a single field mixing "how we came to believe this" with "how
recently it was useful" — the conflation
[decay and reinforcement](../../patterns/decay-and-reinforcement/) exists to
separate.

Strength itself is separate and richer: `calculateStrength` (`src/memory.ts:309`)
with `deriveHalfLife` (`:390`), an `applyOutcome` that moves the score on a
good or bad result (`:424`), and a `calculateRewardFactor` (`:274`) carrying a
loss-aversion ratio — outcomes that went badly count for more than outcomes that
went well.

### How a thing becomes a belief, and how it stops being one

```mermaid
flowchart TD
    C["capture / CLI / HTTP / MCP write"] --> S["stored with confidence:<br/>verified, observed or inferred"]
    S --> R{"read"}
    R -->|"pinned or verified"| K["returned as stored"]
    R -->|"last_retrieved older<br/>than 30 days"| ST["reported as stale<br/>(derived, never written)"]
    R -->|"otherwise"| K
    S -->|"a newer claim arrives"| SU["superseded_by set<br/>— row hidden on read"]
    SU -.->|"nothing keys the value,<br/>so extraction can re-assert it"| S
    S -->|"forget()"| D[["DELETE FROM memories"]]
    S -->|"sleep phase 3<br/>quality audit grades error"| D

    style D fill:#f4e2bd,stroke:#b8860b
```

The two edges into the deletion box are the finding. One is a user asking to
forget; the other is a background quality audit deciding a memory is junk, and
it runs host-wide. The dashed edge is the correction gap: supersession changes
what is *shown* and not what may be *written*.

## 3. Architecture

A Node/TypeScript package with three front doors over one SQLite file. There is
no separate database process, no vector service, and no external dependency for
retrieval — BM25 is implemented in-repo (`src/search.ts:57`) and the vector arm
sits behind an embedding provider abstraction (`src/embedding-provider.ts`).

Operationally the interesting artefact is `src/db.ts`: a migration ladder past
version twenty-five, with self-healing `CREATE TABLE IF NOT EXISTS` re-runs for
stores that were initialised partway and comments naming the incident behind
each repair. An operator inherits one file to back up and a schema that has been
evolved rather than reset.

### Deployment and ergonomics

`/v1/sleep` being loopback-only is the deployment fact that matters most: the
consolidation pass cannot be triggered by a tenant over the network, so a
multi-tenant install must schedule it on the host. Anything that assumes
per-tenant consolidation will find it is not reachable that way, by design.

## 4. Essential Implementation Paths

- **Schema and migrations:** `src/db.ts` — `memories`, `memory_conflicts`,
  `audit_log`, `goal_stack`, `retrieval_policy`, plus connector tables.
- **Epistemics:** `src/memory.ts` — `ConfidenceLevel` (`:23`),
  `calculateStrength` (`:309`), `applyOutcome` (`:424`), `resolveConfidence`
  (`:447`).
- **Physics:** `src/physics.ts` — `computeMass` (`:124`), `computeCharge`
  (`:134`), `computeTemperature` (`:138`).
- **Retrieval:** `src/search.ts` — `hybridSearch` (`:344`), `mmrRerank` (`:801`),
  `physicsSearch` (`:861`), `temporalBoost` (`:150`).
- **Write and capture:** `src/capture.ts` — `extractFromText` (`:159`),
  `summariseTranscript` (`:259`), `cmdCapture` (`:398`).
- **Scope:** `src/tenant.ts` `resolveTenantId`; predicates at
  `src/store.ts:719-721`.
- **Background:** `sleep` phases in `src/api.ts:2752` onward.
- **Audit:** `src/audit.ts:195`; retention in `src/audit-prune.ts`.
- **Validity time:** `src/policies.ts`.

## 5. Memory Data Model

The `memories` table is the core, and two other entity types carry their own
lifecycle: **policies**, **decisions** and **processes** each have a
`supersedes` link and their own audit op (`decision_supersede`,
`process_supersede`, `policy_supersede`).

Policies are where **bi-temporal validity** lives, and it is not decorative.
`src/policies.ts` makes `valid_from` required with a default of creation time
and `valid_to` nullable meaning open-ended, calls the pair "the queryable axis",
normalises dates to fixed width so they sort lexically, enforces
`valid_to > valid_from` with its own error, and carries a fix note for a
read-path bug where a datetime `valid_from` "otherwise made a same-day policy
invisible" — which is only possible in a system whose reads filter on it.

The unevenness is worth stating: the `memories` table also has
`valid_from`/`valid_to` columns, backfilled from `created` (`src/db.ts:238-240`),
and no read-path filter on them was found. Validity time is a first-class
queryable axis for policies and a pair of unused columns for memories.

## 6. Retrieval Mechanics

`hybridSearch` runs BM25 over an in-repo corpus and a vector arm, fuses them,
then `mmrRerank` trades relevance against diversity. `temporalBoost` reads a
direction out of the query — `detectTemporalDirection` looks for "recent" versus
"oldest" phrasing (`src/search.ts:130`) — and reweights accordingly, which is a
cheap way to answer "what did we decide first" without a temporal index.

`physicsSearch` is the alternative ranker, ordering by the derived mass, charge
and temperature rather than by similarity. The `assemble` path
(`src/api.ts:1198`) is DAG-aware, substituting summary nodes when entries
overflow a budget.

Scope reaches this path as a predicate: `tenant_id = ?` composed into the query
(`src/store.ts:719-721`) rather than filtered afterwards, so `LIMIT` means the
same thing for every caller.

## 7. Write Mechanics

`capture` is the automatic path: `extractFromText` pulls candidate items out of
transcript text and `summariseTranscript` compresses a JSONL session. Writes
also arrive from the CLI, from 31 HTTP routes, and from an MCP server, and
`autolearn.ts` can learn from a repository directly.

Writes do not block on a model in the common path — extraction is a separate
command rather than an inline call on every turn.

**A background pass does rewrite the store, and it deletes.** `sleep` runs six
phases (`src/api.ts:2752` onward): consolidation, near-duplicate dedup, a
quality audit, auto-share to a global scope, an ambient-state summary, and a
graph-extraction drain. Phase 3 is the one to know about — it loads entries
host-wide and calls `deleteEntry` on every issue the audit grades `error`. The
lag between writing a memory and it being reachable is short; the lag before a
background pass may delete it is however long the operator waits between sleeps.

## 8. Agent Integration

Three surfaces: a CLI (`src/cli.ts`, the largest file), an HTTP server with 31
routes under `/v1`, and an MCP server (`src/mcp/`). API keys are validated
(`src/auth.ts`) and resolve to a tenant, with role gating on the destructive
routes.

The division of labour between them is the thing to copy: the CLI is explicitly
single-tenant-per-process, the HTTP surface is the multi-tenant one, and the
host-wide operations are reachable only over loopback with an admin role.
Different trust models for different transports, stated in code rather than
inferred.

## 9. Reliability, Safety, and Trust

**The audit log is the cleanest mechanism here.** A dedicated table with
`ts, tenant_id, actor, op, target_id, metadata_json`, one INSERT site
(`src/audit.ts:195`), and a typed op union covering `recall`, `write`,
`outcome`, `sleep`, `supersede`, `promote`, `forget`, `archive_raw`,
`auth_revoke` and `auth_create`. No `UPDATE audit_log` exists anywhere.

The single `DELETE` is retention pruning (`src/audit-prune.ts`), and it is
better than most: opt-in per tenant, dry-run capable, and it **emits its own
`audit_prune` row carrying cutoff, count and dryRun** so, in its own words,
operators investigating "where did old rows go" have one row left to find
regardless of retention floor. A retention policy that records its own execution
in the log it truncates is worth copying directly.

**Correction is record-keyed, and the gap is the atlas's central one.**
Supersession hides a row on read; nothing keys the rejected *value*, so a later
extraction that rediscovers the same claim writes a new row and the system has
no way to know it was already judged wrong. `forget` is a hard delete. There is
no rejected-value tombstone and the vocabulary is absent from the source.

**Conflict resolution is automatic, not human.** `memory_conflicts` carries a
`status`, and it moves — but by code, from inside detection and merge
(`src/store.ts:2380`, `:2497`). That is
[resolve, don't just detect](../../patterns/resolve-not-just-detect/) with a
machine adjudicator, and it is why the human-review mark is withheld: there is
no surface where a person decides.

**Scope, in full**, because a boolean mark cannot express it. `resolveTenantId`
(`src/tenant.ts`) derives the tenant from a validated API key or `HIPPO_TENANT`,
defaulting to `default`, and carries a fix note for the case where
`HIPPO_TENANT=""` fell through as the empty string and "broke every downstream
tenant filter". The API passes it; the CLI deliberately does not; `sleep`
deliberately does not and is fenced by transport and role instead.

## 10. Tests, Evals, and Benchmarks

376 test files, and the project convention stated inside them is "always use
real DB for tests" rather than mocking the store — visible in
`tests/api-recall-suppression-summary.test.ts`, which builds a real database and
exercises the actual recall pipeline. I did not run the suite.

`src/eval-suite.ts` defines `FeatureTestCase` as `id`, `category`, `query`,
`expectedIds`, `description`. **There is no must-not-appear field**, so the
suite can assert what recall should return and has no way to express what it
must not — which is why the negative-eval mark is withheld. `src/ablation.ts`
and `src/compare.ts` suggest ablation runs, and no results are committed.

The near-miss worth more than the mark: `RecallResult.suppressionSummary`
carries **six counters describing what recall excluded and why**, asserted by a
committed test. Telling a caller what retrieval silently dropped is a mechanism
this atlas asks for repeatedly and rarely finds, and it is a different thing
from asserting that a particular memory must not surface.

## 11. For Your Own Build

### Steal

- **A retention prune that logs its own execution.** Twenty lines, and it turns
  "the audit trail has a hole" into "the audit trail explains its hole".
- **Different trust models per transport.** Host-wide operations reachable only
  over loopback with an admin role, with the 403 naming the reason and the
  version that introduced it.
- **A suppression summary on the recall result.** Six counters for what was
  excluded and why, so a caller can tell an empty answer from a filtered one.
- **Loss-aversion weighting on outcomes.** `calculateRewardFactor` counts a bad
  outcome for more than a good one, which is a defensible prior for memory that
  guides action.

### Avoid

- **Deriving an epistemic state from retrieval recency.** `stale` sitting in a
  union with `verified`, `observed` and `inferred` invites a reader to treat
  "nobody asked for this in a month" as evidence about truth. Keep the decay
  axis and the belief axis apart, and let a memory be both current and unused.
- **A quality audit that deletes host-wide.** It is fenced here; if you copy the
  phase without the fence you have built a cross-tenant delete.
- **Supersession as your only correction.** Hiding a row does not stop the next
  extraction from writing it again.

### Fit

This suits a team that wants a **self-contained memory service with real
multi-tenancy** and is willing to own 42,000 lines of it. The migration ladder
and the incident comments say it has been run in anger, and the transport-level
fencing says someone thought about a hostile caller. It is a poor fit if you
want a small dependency — the physics model, the DAG assembler, the graph layer,
the connectors and the goal stack all arrive together — and a poor fit if
correction durability is your requirement, since that is the one axis where the
design stops at hiding rows.

## 12. Open Questions

- **Does the physics metaphor beat the hybrid ranker?** `physicsSearch` and
  `hybridSearch` are alternatives, `ablation.ts` exists, and no committed result
  compares them. It is the one experiment the repository is already shaped to
  run.
- **Why is validity time first-class for policies and unused on memories?** The
  columns exist on both. Only one has a read path.
- **What happens to a memory the quality audit deletes that a tenant still
  wants?** Phase 3 hard-deletes on an `error` grade with no quarantine tier and
  no undo, and the audit row records that it happened rather than what was lost.
- **How often does `stale` fire on a memory that is still true?** The threshold
  is a fixed thirty days of disuse, and nothing measures the false-positive rate.

## Appendix: File Index

**Storage and schema**
- `src/db.ts` — every table and a 25-plus-step migration ladder
- `src/store.ts` — read and write paths, tenant predicates, conflict resolution

**Epistemics and scoring**
- `src/memory.ts` — confidence levels, strength, half-life, outcomes
- `src/physics.ts`, `src/physics-state.ts`, `src/physics-config.ts` — mass,
  charge, temperature
- `src/salience.ts`, `src/rrf.ts`, `src/rerankers/` — ranking components

**Retrieval**
- `src/search.ts` — BM25, hybrid search, MMR, temporal boost, physics search
- `src/recall-scope.ts`, `src/recall-history.ts`, `src/recall-trace.ts`
- `src/graph-recall.ts`, `src/multihop.ts`, `src/dag.ts`

**Write path**
- `src/capture.ts` — extraction and transcript summarisation
- `src/autolearn.ts`, `src/importers.ts`, `src/connectors/`

**Scope, audit and policy**
- `src/tenant.ts`, `src/auth.ts`, `src/scope.ts`, `src/owner-validation.ts`
- `src/audit.ts`, `src/audit-prune.ts`
- `src/policies.ts` — bi-temporal validity, half-open intervals

**Integration**
- `src/server.ts` — 31 `/v1` routes; `src/mcp/` — MCP server; `src/cli.ts` — CLI

**Tests and evals**
- `tests/` — 376 files, real-database convention
- `src/eval-suite.ts`, `src/eval.ts`, `src/ablation.ts`, `src/compare.ts`

## History

**2026-08-04** — [`a9c7cca3613b6571bfb37ad1fb6c070b7c976197`](https://github.com/kitfunso/hippo-memory/commit/a9c7cca3613b6571bfb37ad1fb6c070b7c976197) — first reading.

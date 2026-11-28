---
title: "LongMemory"
eyebrow: "Truth as of a time"
description: "A TypeScript memory engine, formerly OpenMemory, whose strict recall gate refuses superseded, contradicted and ungrounded facts while its published SQL contract never runs."
root: ../..
page_kind: system
source_name: "CaviraOSS/LongMemory"
source_url: https://github.com/CaviraOSS/LongMemory
archive_name: "CaviraOSS--LongMemory"
revision: 9d1deee08df6f0e519aeb014390ab1429d11eebf
revision_url: https://github.com/CaviraOSS/LongMemory/commit/9d1deee08df6f0e519aeb014390ab1429d11eebf
analyzed_at: 2026-11-28
licence: "Apache-2.0 in LICENSE, repeated beside the VS Code extension, the Python package and six host integrations; the n8n node is MIT in its own LICENSE and package.json, and the rest of the tree falls under the root file"
size: "32,447 lines of TypeScript in 371 files under src/ outside tests and 3,010 in 18 test files; the strict gate is src/core/recall/mode_gates.ts (177), the query table src/stores/sqlite/queries.ts (71), the control plane src/control/control_db.ts (500) and space_catalog.ts (229)"
activity: "402 commits from 19 October 2025 to 26 November 2026 under 60 author names; 12 since 19 September 2026, carrying the token-authenticated control plane, personal and team spaces, two outside fixes and the package at 2.1.0"
tests: "102 node:test cases in 18 files under src/, on the control plane, spaces, MCP tools, CLI and project hierarchy, none on the strict gate, temporal logic or store queries; 84 more in the integrations and tools; CI runs tools/check-recall.ts and a benchmark smoke run, not the src suite; none run for this reading"
capabilities: "scope_enforced, bitemporal, trust_state, audit_log, negative_eval"
capability_evidence:
  scope_enforced: "every store query, and in control mode an identity derived from a bearer token per request | src/stores/sqlite/queries.ts:16-58, src/server/middleware/auth.ts:36-47, src/control/control_db.ts:364-383, src/control/space_catalog.ts:61-64, :124-142, :191-207, src/server/routes/ingest.ts:38-44 | `hydro_nodes`, `hydro_edges`, `contradictions` and `entity_aliases` all carry `tenant_id` and `user_id`, and every query in the store's table opens `WHERE tenant_id = ? AND user_id = ?` with no `IS NULL OR` escape; `world_id` alone is optional. The key is bound per `createMemory` instance, and the space catalog keeps one instance per partition: the caller's `personal_partition`, or `team:<id>` for each enabled membership. With `LONGMEMORY_CONTROL_DB` set, every `/v1/` and `/mcp` request must carry a token whose hashed secret, revocation, expiry and the user's disabled flag are checked before the identity and its spaces are built; an ingest naming another `user_id` fails with `identity_mismatch`, and a viewer's space refuses writes. Without a control database the server runs one configured identity, defaulting to `default`, behind an optional shared API key | src/server/control_mode.test.ts:131-163, src/mcp/tools/write_tools.test.ts:92-111, src/control/space_catalog.test.ts:101-111"
  bitemporal: "strict and historical recall — an as-of query over valid time, with recorded time kept separately, tested per node at read time | src/core/temporal/bitemporal.ts:19-25 (`is_valid_at`, `is_recorded_at`), :41 and :51, src/core/recall/mode_gates.ts:116-130 (`can_use_in_historical_recall`), src/core/temporal/mvcc.ts:59-82, src/stores/sqlite/queries.ts:21-32 (`current_truth` and `historical_truth`, unused) | a node carries valid_from, valid_to, observed_at, recorded_at and superseded_at. Historical recall takes an at or an as_of and answers with `is_valid_at` or `is_recorded_at`, so the question asked is what was believed true at that moment rather than what is newest, and the two clocks stay separate predicates. Supersession closes a node MVCC-style through `close_transaction` rather than overwriting it, and ARCHITECTURE.md states the invariant: Recorded time and valid time are distinct. The SQL `current_truth` and `historical_truth` express the same contract in the store and are not the mechanism that runs — like `strict_candidates`, their store methods have no callers, because recall reads an in-memory index hydrated once at construction | no committed test covers the temporal predicates; tools/check-recall.ts:35 requires historical recall to return a superseded node"
  trust_state: "strict recall — a per-node gate in TypeScript, not the SQL the store publishes | src/core/recall/mode_gates.ts:86-113 `can_use_in_strict_recall`, :30-36 (`is_superseded`, `is_contradicted`), src/core/types/node_state.ts:16-21 (the vocabulary), src/core/recall/strict_recall.ts:52 and :69-80 (the loop), src/core/recall/candidate_selection.ts:43-48 (`active_nodes`), src/stores/sqlite/queries.ts:33-56 (`strict_candidates`, unused) | Eligibility is decided per node by `can_use_in_strict_recall`, which refuses a superseded or contradicted status, an unresolved contradiction, confidence under the threshold, a contract with use_for_reasoning false, an ungrounded node that requires grounding, an expired one, a missing required source and a denied source permission — recording each refusal with its reason in an explain trace rather than dropping the node silently. That is a discrete state used for filtering, which is the mark. Two things a reader should know. The candidates it gates come from an in-memory index (`active_nodes` filters by world, not by status, despite the name), so the named SQL `strict_candidates` is a published contract nothing executes — `query_strict_candidates` is declared, implemented and called from nowhere. And the two copies disagree: the SQL requires status = active while the live gate refuses only two of the five declared statuses, so a node marked draft, or marked expired with an open valid_to, passes the gate the SQL would have stopped | no committed test exercises the gate's refusals"
  audit_log: "the MCP surface — one append-only line per tool call, allowed, denied or failed | src/mcp/security/audit.ts:48, src/mcp/tools/common.ts:55-89, src/server/app.ts:153-161 | `mcp_audit_log.record` appends `JSON.stringify(entry)` with `appendFileSync` to `<db_path>.mcp-audit.jsonl`, and an entry carries `tool`, `user_id`, `project_id`, `space`, `outcome` (`allowed`, `denied`, `error`), `dry_run`, timestamps and the error. Every MCP tool call passes through the wrapper in `common.ts`, which records success and failure. The HTTP routes build the same runtime and never call it, so a memory ingested over `/v1/ingest` leaves no row, and the library API writes none; a space refusal or an identity mismatch is recorded as `error`, because the wrapper classifies `denied` by matching the message against not allowed, read-only and permission denied | no committed test asserts an audit row"
  negative_eval: "personal and team spaces — another partition's memory absent beside a required hit | src/mcp/tools/write_tools.test.ts:92-111, src/server/control_mode.test.ts:131-152, src/control/space_catalog.test.ts:101-111 | `a member writes to team core and readers do not see it from personal` ingests into `team:core` and runs the same strict query in both spaces, requiring at least one hit in the team space and zero in Alice's personal space. `personal memory stays private and team memory is shared` has Alice ingest a personal note over HTTP and requires Bob's personal recall to return no items, beside required team hits for both users. `personal and team partitions never share memory` requires a historical recall in the team space to carry no timeline entry for a note written to the personal one. All three assert a scope boundary; nothing asserts that strict recall omits a superseded, contradicted or draft node | src/mcp/tools/write_tools.test.ts:92-111, src/server/control_mode.test.ts:131-152, src/control/space_catalog.test.ts:101-111"
stack_storage: "sqlite"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "An immutable, content-addressed `HydroNode` with a facet, a world, provenance, a reasoning contract and five timestamps; mutable lifecycle state is stored beside it"
  storage: "SQLite `hydro_nodes`, `hydro_edges`, `contradictions` and `entity_aliases`, keyed on tenant and user; an in-memory store for embedded use"
  retrieval: "Several recall modes over one engine — current, historical and strict SQL candidates, plus graph traversal over executable edges — returned within a token bound"
  write: "An immutable ingest pipeline shared by the library, CLI, HTTP server and MCP transports, writing into one space per call and refusing the aggregate space; connectors import external sources and sync their deletions"
  update_delete: "Supersession closes a node's transaction and records `superseded_at`; a deleted connector source is ingested as a non-reasoning marker with a `supersedes` edge"
  scoping: "`tenant_id` and `user_id` in every query, unconditionally, with `world_id` optional beneath; the user key is a personal partition or `team:<id>`, one engine instance each, resolved per request from a hashed bearer token in control mode and fixed by configuration otherwise"
  integration: "A TypeScript package, CLI with user, team and token commands, an HTTP API, fifteen MCP tools over stdio, HTTP or a stdio proxy to a remote server, a Next.js dashboard, a VS Code extension and host plugins"
  background: "Consolidation and reconsolidation passes over the hydrograph"
  trust: "A read-time gate in code — status, use_for_reasoning, confidence, grounding, source requirement, expiry and source permission decide eligibility per node; the SQL that states the same policy is never executed and is stricter than the gate that is"
  strengths: "Strict recall asks what was true at a time and refuses a fact under unresolved contradiction, in one legible query"
  risks: "No committed test covers the strict gate, the temporal predicates or the store queries, and the fourteen stated invariants are returned as strings rather than asserted"
---

## 1. Executive Summary

LongMemory, formerly **OpenMemory**, is a TypeScript memory engine over SQLite whose strict recall decides, one fact at a time, whether a fact may be reasoned from — and the SQL it publishes as that contract is never executed. Personal and team memory are separate partitions of one store, chosen per request from a bearer token, and the three committed tests that pin that boundary are the only cases in the tree requiring a memory to be absent from a read.

**It is a rewrite, not a rename.** The repository was renamed from `CaviraOSS/OpenMemory` to `CaviraOSS/LongMemory` on 31 August 2026, with a `MIGRATION.md` moving the npm package, CLI, environment prefix and routes to the new name. Until then the engine was `packages/openmemory-js/`, whose README announced a rewrite on another branch; that rewrite replaced it, and the hand-typed sectoral interdependence matrix at its centre survives only as a mapping inside `src/core/migration/legacy_cleaner.ts`. The new engine's own invariant list rejects the old shape in so many words — *"worlds are recursive containers, not flat sectors"*. Around it sit a Next.js dashboard, a VS Code extension, host integrations, and a benchmark harness for LongMemEval, LoCoMo and BEAM.

What replaced it is worth the report, and what decides its central claim is not
in the file the design points you at. The store publishes its recall contract
as named SQL strings, and `strict_candidates` reads like the whole answer — the
conditions it applies cover most of what this atlas asks a read path to refuse:

```sql
WHERE n.tenant_id = @tenant_id AND n.user_id = @user_id
  AND n.valid_from <= @at AND (n.valid_to IS NULL OR n.valid_to > @at)
  AND (n.superseded_at IS NULL OR n.superseded_at > @at)
  AND n.status = 'active' AND n.use_for_reasoning = 1
  AND n.confidence >= @min_confidence
  AND (n.requires_grounding = 0 OR n.grounding_score >= @grounding_threshold)
  AND NOT EXISTS (SELECT 1 FROM contradictions c
                  WHERE ... AND c.resolved = 0
                    AND (c.node_a = n.node_id OR c.node_b = n.node_id))
```

As-of valid time with recorded time kept apart; supersession evaluated as of the
same instant; a discrete status; a per-fact validity contract; grounding and
source requirements; and — the rare one — **a fact under an unresolved
contradiction is withheld from reasoning** rather than ranked beneath its rival.

**That query never runs.** `query_strict_candidates` is declared on the store
interface (`src/stores/index.ts:46`) and implemented over the string
(`src/stores/sqlite/sqlite_store.ts:324-325`), and nothing calls it — nor
`query_current_truth`, nor `query_historical_truth`. All four recall modes
retrieve from an in-memory index instead
(`src/core/recall/strict_recall.ts:52`, and the same `deps.index.active_nodes`
call at `historical_recall.ts:77`, `grounded_recall.ts:97` and
`associative_recall.ts:584`), whose `active_nodes` filters by world and, despite
the name, not by status (`src/core/recall/candidate_selection.ts:43-48`). The
index is hydrated once from `store.load_nodes()` when the engine is constructed
(`src/core/create_memory.ts:265-280`), which is where the tenant and user
predicate is applied — so scoping holds, binding when an engine instance starts
rather than per query, and the server keeps one instance per partition.

The eligibility decision lives in TypeScript, one node at a time:
`can_use_in_strict_recall` (`src/core/recall/mode_gates.ts:86-113`). It is a good
gate. It refuses a superseded or contradicted node, an unresolved contradiction,
confidence under the threshold, a contract with `use_for_reasoning: false`, an
ungrounded node that required grounding, an expired one, a missing required
source and a denied source permission — and it returns the *reasons*, which
`strict_recall` records in an explain trace beside each rejected candidate
(`:69-80`) rather than dropping it silently. The mark rests on that.

**The two copies of the policy disagree.** The SQL requires `status = 'active'`.
The gate tests only two values: `is_superseded` and `is_contradicted`
(`mode_gates.ts:30-36`). `NodeStatus` declares five — `active`, `superseded`,
`contradicted`, `expired`, `draft` (`src/core/types/node_state.ts:16-21`). So a
node whose status is `draft` is not refused by status in the path that runs, and
one marked `expired` is refused only if its `valid_to` or `max_valid_duration`
independently says so. The consolidation pass reads `status === 'expired'` as a
live case (`src/core/memory/consolidation.ts:104-110`), so the value is not
vestigial. A predicate written twice is a predicate that will differ; here the
copy a reader is invited to check is the one that cannot be wrong, because it is
not executed.

**The gate is not tested; the partition boundary is.** `package.json` runs `tsx --test "src/**/*.test.ts"` over 102 cases in 18 files, and every one is about the control plane, spaces, MCP tools, the CLI or the project hierarchy — none is in `src/core/recall`, `src/core/temporal` or `src/stores`, and none asserts that strict recall omits a superseded, contradicted or draft node. CI does not run that suite: `ci.yml` runs `release:check`, whose `recall:check` is `tools/check-recall.ts`, a smoke script that requires strict recall to surface an ingested node and historical recall to keep a superseded one, and asserts no omission.

The engine's fourteen invariants — *"durable nodes are immutable"*, *"strict recall cannot use superseded facts"*, *"benchmarks define correctness"* — are exported as an array and handed back by `invariants: () => hydrograph_invariants`; the function named `assert_hydrograph_invariants` returns the list and asserts nothing. The last invariant is the stated substitute: the benchmark scorecard gates a `stale_leakage` rate, which measures a model's answers over external datasets rather than pinning the query's behaviour to a fixture.

**Spaces are partitions of the same key.** With `LONGMEMORY_CONTROL_DB` set, the server authenticates every `/v1/` and `/mcp` request with a bearer token of the form `lm_<id>_<secret>`, checking the hashed secret in constant time, then revocation, expiry and whether the user is disabled (`src/control/control_db.ts:364-383`), and rebuilds the caller's memberships on each request. The space catalog turns that identity into spaces — `personal`, mapped to the user's `personal_partition`, and `team:<id>` per enabled membership — and opens one `createMemory` instance per partition with the partition as its `user_id` (`src/control/space_catalog.ts:124-142`, `:191-207`). A partition containing `:` is refused for personal and legacy users, so a personal partition cannot collide with a team one (`:59-87`).

Reads default to `all`, which runs each space separately and merges the results with each tagged (`src/mcp/tools/read_scope.ts`); writes go to one space and refuse `all` and a viewer's space. An HTTP ingest naming another `user_id` fails with `identity_mismatch`, and a recall's `permission_context` can narrow the token's teams but not add to them (`src/server/routes/recall.ts:28-49`). Three committed cases require a space's memory to be absent from another space beside a required hit (`src/mcp/tools/write_tools.test.ts:92-111`, `src/server/control_mode.test.ts:131-152`, `src/control/space_catalog.test.ts:101-111`), and those carry `negative_eval`.

Without a control database the server runs the configured identity, `default` unless set, behind an optional shared API key, and refuses to start without one when `LONGMEMORY_HOST` is not loopback or MCP over HTTP is on (`src/server/config.ts:63-76`). Its loopback set includes `::`, which is the unspecified address rather than a loopback one: a server bound to `::` listens on every interface and starts with no key, serving every memory in the configured partition to any caller that can reach it.

## 2. Mental Model

A memory is a **node in a hydrograph**: immutable, content-addressed, and carrying the time it describes separately from the time it was learned.

| Field | Meaning |
| --- | --- |
| `valid_from`, `valid_to` | when the claim is true in the world |
| `observed_at` | when the source saw it |
| `recorded_at` | when the store learned it |
| `superseded_at` | when a later node closed this one's transaction |
| `status`, `use_for_reasoning`, `confidence` | whether the strict gate may use it |
| `world_id`, facet | which recursive context it belongs to, and which cognitive attribute it is |

Recall is a choice of question, not a choice of index:

- **current truth** — active, unsuperseded, valid now;
- **historical truth** — valid at `@at`, superseded or not, ordered by `valid_from` — the forensic read;
- **strict candidates** — current truth further filtered by every reasoning contract and by unresolved contradictions;
- **associative** recall is permitted to use superseded and emotional residue, and the invariant list says it *"must label it"*.

```mermaid
%% caption: one ingest pipeline writes immutable nodes; supersession closes a node rather than overwriting it, and each recall mode is a different question over the same valid-time and recorded-time columns — strict recall adding the reasoning contract and the unresolved-contradiction check
flowchart TD
    SRC["events · documents · connectors"] --> ING["immutable ingest pipeline"]
    ING --> N[("hydro_nodes<br/>valid_from · valid_to · recorded_at · superseded_at")]
    ING -->|"later fact"| MV["close_transaction<br/>superseded_at = now"]
    MV --> N
    ING -->|"conflict"| C[("contradictions<br/>resolved = 0")]
    DEL["connector source deleted"] -->|"marker node, use_for_reasoning = false<br/>+ supersedes edge"| N

    N --> CUR["current_truth<br/>active · unsuperseded · valid at @at"]
    N --> HIS["historical_truth<br/>valid at @at, superseded or not"]
    N --> STR["can_use_in_strict_recall over the in-memory index<br/>+ confidence · contract · grounding · source<br/>(strict_candidates SQL is never executed)"]
    C -.->|"NOT EXISTS unresolved"| STR
    STR --> CTX["bounded context"]
    CUR --> CTX
```

## 3. Architecture

One TypeScript package, `src/`, with a shared engine created by `createMemory`. `ARCHITECTURE.md` states the rule that makes the surfaces trustworthy relative to each other — *"api server and cli must use the same createMemory engine"* — and the tree keeps it: the CLI, the authenticated HTTP server, the MCP transports, the dashboard proxy and the integrations all construct the same engine.

- `src/core` — the hydrograph types, temporal logic (`temporal/bitemporal.ts`, `temporal/mvcc.ts`), reconsolidation, invariants, migration
- `src/stores` — the SQLite store and its query table, and an in-memory store
- `src/answering`, `src/connectors` — recall assembly and external source import
- `src/server` — HTTP routes (`ingest`, `recall`, `explain`, `timeline`, `worlds`, `entities`, `stats`) and middleware (auth, rate limit, CORS, concurrency, telemetry)
- `src/control` — the control database of users, teams, memberships and tokens, and the space catalog that maps an identity to partitions
- `src/mcp` — fifteen governed tools, resources, prompts, the stdio, HTTP and remote-proxy transports, and `security/audit.ts`

### Deployment and ergonomics

`npm`, `longmemory` CLI, a SQLite file. `Dockerfile`, `docker-compose.yml`, and deploy descriptors for Heroku, Railway, Render and Vercel sit at the root, beside PowerShell start and stop scripts. `MIGRATION.md` bridges the old npm and registry names through temporary compatibility packages; application identifiers keep no runtime aliases.

## 4. Essential Implementation Paths

### The query table

`src/stores/sqlite/queries.ts` holds the recall SQL as named strings, which is a legible way to publish a retrieval contract: `load_node`, `load_edge`, `current_truth`, `historical_truth`, `strict_candidates`, `aliases_for_entity`, `canonical_alias`. Every one opens on `tenant_id` and `user_id`. `world_id` is the only optional key, written `(@world_id IS NULL OR world_id = @world_id)`. Three of the seven — the three recall queries — have store methods no caller invokes; the ones that run are the loaders and the alias lookups.

### Supersession without overwrite

`temporal/mvcc.ts` closes a node's transaction by stamping `superseded_at` and returning a new node rather than mutating the stored one, consistent with *"durable nodes are immutable"* and with the architecture document's *"mutable lifecycle state is stored separately"*. Because `superseded_at` is compared against `@at`, a superseded fact is still returned by a recall asking about a moment before it was superseded — the property that makes the historical query honest.

### Connector deletion, which is not a tombstone

When an imported source item is deleted upstream, `src/core/create_memory.ts:677-712` ingests a marker node — text *"Source item deleted: …"*, `use_for_reasoning: false`, `metadata.source_deleted: true` — and a `supersedes` edge from it to the node it replaces. That is delete-sync recorded as supersession, which is the correct and auditable behaviour for a connector and is not a rejected-value tombstone: nothing keys on the content to stop it being ingested again from another source.

### Contradictions as a gate

`contradictions` rows carry `node_a`, `node_b` and `resolved`. The strict gate refuses any node the caller reports as carrying an unresolved contradiction (`mode_gates.ts:92`, fed by `deps.unresolved_contradiction` at `strict_recall.ts:65`); the unused `strict_candidates` SQL expresses the same rule as a `NOT EXISTS`. The consequence is conservative in the right direction: two sources disagreeing about a deployment target produce an answer that uses neither, rather than one that silently picks the more confident.

## 5. Memory Data Model

`HydroNode` (`src/core/types/hydro_node.ts`) is content-addressed and immutable; `hydro_nodes` stores the serialised node in `node_json` with the filterable fields lifted into columns. A node's **contract** carries `use_for_reasoning`, `use_for_personalization`, `expires_if_unconfirmed` and an optional `max_valid_duration`, and the strict gate reads the duration off the node: a fact can declare that it is only good for a period, and `is_expired` enforces it (`mode_gates.ts:38-42`, applied at `:101-106`).

Provenance travels in `node_json` as `provenance.source_trace`, and `source_required` nodes are excluded from strict recall unless they carry a grounding reference or a non-empty trace.

## 6. Retrieval Mechanics

Lexical, vector and graph arms feed the recall modes, and results are returned within a token bound — *"Recall is read-only and token bounded"*. The distinguishing work is not in ranking but in eligibility: `can_use_in_strict_recall` decides what may be reasoned from before anything is scored, and the survivors are ordered afterwards. The SQL that expresses the same order — confidence, then grounding, then recency — is not what produces it.

`world_id` scopes recall inside a user to a recursive context; omitting it reads across the user's worlds, which is a design choice rather than a leak, since tenant and user still bound the query.

## 7. Write Mechanics

One immutable ingest pipeline for every surface, writing into the engine instance of one space. The HTTP and MCP ingest paths resolve the space from the call's `space` argument, the `X-LongMemory-Space` header or the token's default, and refuse `all` and a viewer's space; a library `createMemory` binds `tenant_id` and `user_id` at construction, defaulting both to `default`. Consolidation and reconsolidation passes run over the graph; supersession is written as a closed transaction plus an edge, never as an update in place.

## 8. Agent Integration

Fifteen MCP tools sit behind `src/mcp/security`, with an audit log of every call, beside an HTTP API and a CLI with a deterministic JSON mode that the VS Code extension consumes. The CLI's `auth`, `users`, `teams` and `tokens` commands manage the control database. `longmemory mcp` either serves a local store over stdio or, given a server and a token file, proxies stdio to a remote `/mcp` so the server's token decides the spaces. Host plugins and MCP configurations live under `integrations/`. Because every surface shares one engine per space, a fact ingested through one is recalled identically through another.

## 9. Reliability, Safety, and Trust

Strengths:

- **Strict recall is an as-of question**, with valid time and recorded time kept apart and supersession evaluated at the same instant.
- **An unresolved contradiction withholds both sides from reasoning.**
- **Facts carry their own validity contract**, and the read-time gate enforces it.
- **Grounding and source requirements gate reasoning**, not only ranking.
- **Nodes are immutable and supersession closes rather than overwrites**, so the historical read is real.
- **Tenant and user are in every query without an escape.**
- **Personal and team memory are partitions chosen by a verified token**, and committed cases require each to stay out of the other.
- **Every MCP tool call is audited**, including denials.

Gaps:

- **Nothing tests the gate's refusals.** The committed suite covers the partition boundary and the control plane; every property of strict and historical recall above is established by reading the code, and CI does not run the suite.
- **The invariants are not asserted.** `assert_hydrograph_invariants` returns the list; nothing checks any entry.
- **Identity comes from the token only in control mode.** Without a control database the server is one configured identity behind an optional shared key, and a bind to `::` counts as loopback, so it starts on every interface with no key.
- **Only the MCP surface is audited.** Ingest over HTTP and the library API leave no audit row, and a space refusal or identity mismatch over MCP is recorded as `error`, not `denied`.
- **No rejected-value tombstone.** A fact a user wants gone can be superseded, but nothing keys on its content to stop it returning from another source.

## 10. Tests, Evals, and Benchmarks

**I ran nothing.** `npm test` runs `tsx --test "src/**/*.test.ts"`: 102 cases in 18 files, on the control database, the space catalog, the MCP runtime, tools, resources and remote proxy, the CLI's auth and MCP commands, the HTTP control mode and the project hierarchy. Another 84 sit in `integrations/kilo-longmemory/test`, `integrations/opencode-longmemory/test` and `tools/`. The negative cases are the three partition tests named in section 1; each asserts zero items, or zero timeline entries, in one space beside a required hit in another. No file under `src/core/recall`, `src/core/temporal` or `src/stores` has a test beside it. CI's `release:check` runs `tools/check-recall.ts`, which requires strict recall to surface an ingested node, historical recall to keep a superseded one and associative recall to follow a supersession chain, and asserts no omission.

`benchmarks/` is a harness for LongMemEval, LoCoMo and BEAM with a scorecard and a `FAILURE_ANALYSIS.md`. Its gates include a `stale_leakage` rate — an answer scores only if it is correct **and** does not use stale material, and a provider passes only if the leakage rate is at or below `stale_leakage_max`. That is the right metric for a system whose central claim is not using superseded facts. It is also a measurement of a model's answers over external datasets, requiring a provider to run, rather than a committed case that fails when the strict gate loses its supersession test — so it does not carry `negative_eval`, and the invariant *"benchmarks define correctness"* is doing work a four-line fixture test would do more cheaply.

**No paper, arXiv reference or citation file exists in this repository.**

## 11. For Your Own Build

### Steal

- **Publish recall as a named query table** — and then make the engine read it. `current_truth`, `historical_truth` and `strict_candidates` side by side make the difference between modes reviewable in one file, which is the appeal; here the engine enforces a second copy in TypeScript and the published table drifted from it unnoticed. A contract worth publishing is worth being the only one.
- **Evaluate supersession as of the same instant as validity.** `superseded_at > @at` is what lets a historical read return what was believed then.
- **Withhold a contradicted fact from reasoning until resolved.** `NOT EXISTS` an unresolved contradiction is one clause and a large change in failure mode.
- **Let a fact carry its own expiry contract** and enforce it in the query rather than in a sweeper.
- **Record connector deletions as supersession with a non-reasoning marker**, so the removal is visible in history and invisible to reasoning.

### Avoid

- **Stating invariants you do not check.** A list named `assert_…` that returns strings reads as a control and is not one.
- **Replacing tests with benchmarks.** A benchmark gate over a model's answers cannot tell you which clause of your query regressed.
- **Testing the boundary you added and not the one you published.** The partition tests arrived with the control plane; the strict gate, the repository's central claim, has none, and the suite is not in CI.
- **Auditing one surface of several.** If three surfaces share an engine, audit at the engine.

### Fit

Read this for the recall contract — it is one of the clearest statements in the corpus of what a memory should refuse to reason from. Adopt it with a fixture per clause of your own, because the repository's tests stop at the partition boundary. The control plane is worth reading as the scope half: one engine instance per partition, chosen per request from a verified token.

## 12. Open Questions

- Will the invariants become assertions, and will the strict gate get a fixture test per clause?
- Are the three unused recall queries intended to become the implementation, or documentation of it? They are the clearer statement of the policy, and they are stricter than the code that runs.
- How is a contradiction resolved, and by whom — and does resolution record which side won?
- Is `::` in the loopback set meant to cover `::1`, or to let a dual-stack bind start without a key?
- Why is the audit log on the MCP surface only, when every surface shares the engine?
- What does the `stale_leakage` rate measure in practice? `.gitignore` excludes `benchmarks/runs/`, so no result is committed.

## Appendix: File Index

- **Recall contract:** `src/stores/sqlite/queries.ts`, `src/stores/sqlite/sqlite_store.ts`.
- **Temporal logic:** `src/core/temporal/bitemporal.ts`, `src/core/temporal/mvcc.ts`, `src/core/memory/reconsolidation.ts`.
- **Model:** `src/core/types/hydro_node.ts`, `src/core/invariants.ts`.
- **Engine and connectors:** `src/core/create_memory.ts` (identity defaults :198, hydration :265-280, connector deletion :677-712, invariants getter :827), `src/connectors/`.
- **Control plane and spaces:** `src/control/control_db.ts`, `src/control/token.ts`, `src/control/space_catalog.ts`, `src/mcp/tools/read_scope.ts`, `src/server/config.ts` (exposed-bind check :63-76).
- **Surfaces:** `src/server/app.ts`, `src/server/routes/`, `src/server/middleware/auth.ts`, `src/mcp/runtime.ts`, `src/mcp/tools/common.ts`, `src/mcp/security/audit.ts`, `src/mcp/transports/remote_proxy.ts`.
- **Tests:** `src/**/*.test.ts`, `tools/check-recall.ts`, `.github/workflows/ci.yml`.
- **Migration:** `MIGRATION.md`, `src/core/migration/legacy_cleaner.ts`.
- **Benchmarks:** `benchmarks/src/scorecard.ts`, `benchmarks/src/report.ts`, `benchmarks/FAILURE_ANALYSIS.md`.

### Searches behind the absence claims

```sh
# no test beside the recall, temporal or store code, no status named in a src test, and no omission asserted by the smoke check
# (memory-absence assertions in the tree: the three partition cases; the rest assert on output, config and file changes)
git grep -n -E 'ok[(]!|doesNotMatch|length, 0|notEqual' -- '*.test.ts' '*.test.mjs'
git ls-files 'src/core/recall' 'src/core/temporal' 'src/stores' | grep -E '[.]test[.]'
git grep -n -E 'superseded|contradicted|draft' -- 'src/**/*.test.ts'
grep -n -E 'assert' tools/check-recall.ts

# CI runs release:check, not the src suite
grep -n 'run:' .github/workflows/*.yml

# the three named recall queries have no caller outside the store
git grep -n -E 'query_(strict_candidates|current_truth|historical_truth)' -- src

# the HTTP routes never record an audit row
git grep -n 'audit' -- src/server ':!*.test.ts'

# the invariants are exported and returned, not asserted
grep -rn 'hydrograph_invariants' --include='*.ts' src/

# the audit log is written only from the MCP security module, and recorded only by the MCP tool wrapper
grep -rn 'appendFileSync' --include='*.ts' src/
git grep -n 'audit[.]record' -- src ':!*.test.ts'

# the only sector code left is the legacy migration
grep -rniE 'sectoral|interdependence|SECTOR' --include='*.ts' src/
```

## History

**2026-11-28** — [`9d1deee08df6f0e519aeb014390ab1429d11eebf`](https://github.com/CaviraOSS/LongMemory/commit/9d1deee08df6f0e519aeb014390ab1429d11eebf) — 12 commits on. The recall gate, query table, temporal code and store are byte-identical; what moved is a token-authenticated control plane with personal and team spaces as partitions of the same tenant and user key, and the repository's first tests. `negative_eval` is **added** on three partition cases, each a miss in one space beside a hit in another ([section 1](#1-executive-summary)); none covers the strict gate, and CI does not run the suite. `scope_enforced` holds with identity from the token in control mode. Two defects found: a bind to `::` counts as loopback and starts with no key, and MCP space refusals audit as `error`. The other recall modes' candidate reads are at their own lines, not strict recall's. Screened; nothing installed or run.

**2026-09-19** — [`4da4986d0069dbaa59d9209a84e2267749a67b3f`](https://github.com/CaviraOSS/LongMemory/commit/4da4986d0069dbaa59d9209a84e2267749a67b3f) — `trust_state` re-tested at an unchanged pin, and the mark holds on a different mechanism than the one recorded. The previous reading rested it — and most of this report — on `strict_candidates`, the named SQL in `src/stores/sqlite/queries.ts`. That query is never executed. `query_strict_candidates` is declared on the store interface (`src/stores/index.ts:46`), implemented (`src/stores/sqlite/sqlite_store.ts:324-325`) and called from nowhere, and the same is true of `query_current_truth` and `query_historical_truth`. All four recall modes retrieve from an in-memory index (`src/core/recall/candidate_selection.ts:43-48`) whose `active_nodes` filters by world and, despite the name, not by status; the index is hydrated once from `store.load_nodes()` at engine construction (`src/core/create_memory.ts:261-277`), which is where the tenant and user predicate is applied — so `scope_enforced` is unaffected, it just binds at startup rather than per query. The gate that does run is `can_use_in_strict_recall` (`src/core/recall/mode_gates.ts:86-113`), and it is a good one: it refuses a superseded or contradicted node, an unresolved contradiction, low confidence, a contract forbidding reasoning, an ungrounded node that required grounding, an expired one, a missing required source and a denied source permission, and returns the reasons so `strict_recall` can record each rejection in an explain trace (`:69-80`) instead of dropping it silently. The two copies of the policy disagree, and the live one is the looser. The SQL requires `status = 'active'`; the gate tests only `is_superseded` and `is_contradicted` (`:30-36`) while `NodeStatus` declares five values — active, superseded, contradicted, expired, draft (`src/core/types/node_state.ts:16-21`). A node marked `draft` passes, and one marked `expired` passes unless its `valid_to` or `max_valid_duration` independently refuses it; the consolidation pass reads `status === 'expired'` as a live case (`src/core/memory/consolidation.ts:104-110`), so the value is not vestigial. `bitemporal` is re-anchored the same way: the as-of test that runs is `is_valid_at` / `is_recorded_at` (`src/core/temporal/bitemporal.ts:19-25`) applied in `can_use_in_historical_recall`, not the `historical_truth` SQL. Section 1, the diagram, sections 5 through 8, the reusable-ideas list and the open questions were rewritten. Two path anchors corrected: `create_memory.ts` is `src/core/create_memory.ts`, and the connector deletion marker is at `:682`. Re-read from a fresh clone; nothing was installed and no suite was run.

**2026-09-15** — [`4da4986d0069dbaa59d9209a84e2267749a67b3f`](https://github.com/CaviraOSS/LongMemory/commit/4da4986d0069dbaa59d9209a84e2267749a67b3f) — second reading, 31 commits on, and a different system at the same slug. Screened first; nothing was installed and nothing was run. The rewrite the previous reading noted on a separate branch landed on `main`: `packages/openmemory-js` and every file the previous appendix cited are gone, the repository carries the LongMemory name throughout with a `MIGRATION.md` dated to the 31 August rename, and the sectoral interdependence matrix that gave the report its title survives only in a legacy migration. The report is rewritten for the code at this pin rather than annotated, and the title follows the product. Marks were re-tested from scratch. `scope_enforced` holds on a different mechanism — `tenant_id` and `user_id` composed unconditionally into every query in the SQLite store. `negative_eval` is **withdrawn**: its evidence, `test_project_isolation.ts`, was deleted with the package, and no test file exists anywhere in the tree. `bitemporal`, `trust_state` and `audit_log` are added on the new engine — an as-of valid-time query with recorded time kept apart, a strict-recall gate on status, contract, grounding and unresolved contradictions, and an append-only MCP call log. `tombstone` is withheld after reading the one place the word appears: the connector deletion marker is delete-sync recorded as supersession. The slug is kept, as the rename entry below decided, so no published URL moves.

**2026-09-13** — the repository was renamed from `CaviraOSS/OpenMemory` to `CaviraOSS/LongMemory`, upstream of the pinned commit and after the reading below. No re-reading: the pin, `analyzed_at` and every finding are unchanged, and only `source_name`, `source_url`, `revision_url`, `archive_name` and the repositories-inspected entry moved. The slug is unchanged, so no published URL moved. The archive fork was renamed to `agent-memory-atlas-archive/CaviraOSS--LongMemory` to match.

**2026-08-09** — [`9fdfc2ac09317881d0cdad6efd8b4859fc886323`](https://github.com/CaviraOSS/LongMemory/commit/9fdfc2ac09317881d0cdad6efd8b4859fc886323) — first reading, on `main`. The README announces a rewrite in progress on a separate branch, which was not read. Screened before reading; the tree was read, never installed, and no test was run.

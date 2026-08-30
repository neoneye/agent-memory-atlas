---
title: "NornicDB"
eyebrow: "Temporal validity as a constraint"
description: "A database that lets you declare validity as a schema constraint over (key, valid_from, valid_to) — and runs a Kalman filter over confidence so one enthusiastic spike cannot move a memory's score."
root: ../..
page_kind: system
source_name: "orneryd/NornicDB"
source_url: https://github.com/orneryd/NornicDB
revision: a5f623399830d76e3e22e56264548c613ba897aa
revision_url: https://github.com/orneryd/NornicDB/commit/a5f623399830d76e3e22e56264548c613ba897aa
analyzed_at: 2026-08-09
capabilities: "audit_log, scope_enforced"
stack_storage: "kv"
stack_retrieval: "lexical, vector, graph"
stack_source: "seeded"
matrix:
  memory_unit: "A graph node or edge with properties and an optional vector, under a Neo4j-compatible model"
  storage: "Badger with MVCC snapshot isolation, an HNSW vector index and prefixed key spaces per index type"
  retrieval: "Cypher plus hybrid graph and vector search, with knowledge-policy scoring applied as a visibility filter"
  write: "Transactional, anchored to an MVCC version, with declarable constraints including a TEMPORAL kind"
  update_delete: "MVCC versions with a retained floor; pruning keeps the head and fails historical reads below it"
  scoping: "A namespace component in every storage key prefix, plus multi-database separation"
  integration: "Bolt and Cypher for Neo4j clients, gRPC, GraphQL, a Qdrant-compatible endpoint and MCP"
  background: "Access accumulation and flushing, decay driven by temporal access patterns, retention and replication"
  trust: "A confidence property filtered through a per-property Kalman filter that dampens single-measurement spikes"
  strengths: "Validity can be declared and enforced as a constraint, rather than being a convention two queries must share"
  risks: "Search is current-state only by design, so the historical reads and the retrieval path do not meet"
---

## 1. Executive Summary

NornicDB is a Neo4j-compatible graph database with vector search and MVCC
historical reads, written in Go — roughly 780,000 lines including tests, MIT by
the README badge and `LICENSE.md`. It is a database first and an agent-memory
product second, exposing Bolt, Cypher, gRPC, GraphQL, a Qdrant-compatible API
and MCP.

It earns a place here for two mechanisms that sit below where most memory
systems operate.

**Temporal validity is a declarable constraint.** Alongside the usual unique and
required-property constraints, `ConstraintTemporal` exists, and its validator
enforces its shape: "TEMPORAL constraint requires 3 properties (key, valid_from,
valid_to)". The storage layer carries a matching index prefix —
`temporal:namespace:label:keyprops:keyhash:valid_from:nodeID`.

Every other bi-temporal system in this atlas implements validity as a
*convention*: two columns that the write path fills and the read path is
expected to filter, with nothing preventing a query from forgetting. Several
reports here exist because someone did forget — the columns are written and no
read consults them. NornicDB lets you declare it, so the database rejects a node
that claims a temporal label without the three properties.

**Confidence is Kalman-filtered per property.**
`knowledgepolicy/kalman_accumulator.go` runs a Kalman filter over each property's
measurement stream, and `kalman_anti_sycophancy_test.go` names the failure it
exists to prevent. The test feeds fifty measurements of 0.6, asserts the filtered
value has settled near 0.6, then feeds a single 0.99 and asserts the result stays
below 0.8 — "hallucinated spike should be dampened" — then feeds five more 0.6s
and asserts recovery to within 0.15.

That is a direct answer to a failure this atlas has described repeatedly and seen
addressed almost nowhere: an agent that agrees enthusiastically with itself
ratchets a confidence score upward, and nothing distinguishes fifty independent
confirmations from one loud one. A filter with a high measurement-noise term
makes a single spike cheap and a sustained shift expensive.

## 2. Mental Model

The unit is a graph node or edge with properties and an optional vector.
"Memory" behaviour is layered on top by three packages:

- **`knowledgepolicy`** accumulates access and traversal counts per entity,
  flushes them asynchronously, and compiles a scoring filter that decides what a
  query can see;
- **`temporal`** turns access *patterns* into decay behaviour — the package
  header states the intent: "Frequently accessed nodes decay SLOWER… Rarely
  accessed nodes decay FASTER… Nodes with daily patterns maintain longer (routine
  knowledge)… Burst-accessed nodes get temporary boost (current focus)";
- **`lifecycle`** and **`retention`** handle the terminal states.

Underneath, MVCC gives every transaction a consistent snapshot and preserves
older versions down to a retained floor.

```mermaid
%% caption: reads resolve against one committed MVCC view and a historical read below the retained floor fails rather than guessing, while the search paths are deliberately outside that state
flowchart TD
    W["write in a transaction"] --> MV["anchored to an MVCC version"]
    MV --> C{"constraints"}
    C -->|"TEMPORAL: needs key, valid_from, valid_to"| REJ["rejected if the shape is wrong"]
    C --> OK["committed"]
    OK --> TI["temporal index:<br/>namespace:label:keyprops:keyhash:valid_from:nodeID"]
    R["read"] --> SNAP["resolves against one committed view"]
    R -.->|"historical read below the retained floor"| ENF["ErrNotFound — fails safely"]
    ACC["access + traversal counts"] --> KAL["Kalman filter per property"]
    KAL --> SC["knowledge-policy score"]
    SC --> VIS["visibility filter on results"]
    ACC --> DEC["temporal decay: pattern-aware"]
    SRCH["search paths"] -.->|"intentionally separate from historical MVCC state"| SNAP
```

The two dotted edges are both stated in the README as deliberate: an
out-of-retention historical read "fails safely with `ErrNotFound`", and "current
search paths are intentionally separate from historical MVCC state".

## 3. Architecture

Badger as the storage engine with byte-prefixed key spaces per index type, MVCC
snapshot isolation at the storage layer, an HNSW vector index with tombstoned
deletes, and multi-architecture builds for CPU, CUDA, Metal and Vulkan.

Forty-plus packages under `pkg/`, including `audit`, `compliance`, `encryption`,
`kms`, `security`, `auth`, `heimdall`, `replication`, `retention`, `multidb`,
`observability` and `eval` — the operational surface of a database rather than a
memory library.

The HNSW implementation documents its own trade in the file header: "`Remove()`
tombstones a vector via a dense `deleted []bool` flag", "Neighbor lists are not
eagerly rewired (tombstones keep deletes cheap)", with `TombstoneRatio()`
exposed and a note that rebuilding "avoids tombstone growth from hot upsert
workloads". Those are index tombstones — a different mechanism from a
rejected-value record, and this report does not count them toward the mark.

## 4. Essential Implementation Paths

**Constraint validation** —
`pkg/storage/badger_constraint_validation.go:164-200` for nodes and `:717` for
edges, both requiring the three temporal properties.

**Temporal index** — `pkg/storage/badger.go:36`, the prefix layout.

**Access accounting** — `pkg/knowledgepolicy/access_accumulator.go` (atomic
per-entity deltas), `access_flusher.go` (asynchronous flush with a
supernode-suppression path and metrics).

**Scoring and visibility** — `pkg/knowledgepolicy/scorer.go`,
`scoring_filter.go`, `compiled_binding.go`, `resolver.go`.

**Kalman** — `pkg/knowledgepolicy/kalman_accumulator.go`
(`ProcessKalmanMutation`, "inlined from `pkg/filter/kalman.go` for
zero-allocation hot path"), with `Q` scaled by 0.001 and `R` taken from config.

**Audit** — `pkg/audit/audit.go`.

## 5. Memory Data Model

The property graph is the model, so the memory-specific state lives in access
metadata rather than on the node: `AccessMetaEntry` carries `accessCount`,
`traversalCount`, `lastAccessedAt`, `lastTraversedAt` and a
`KalmanFilters map[string]*KalmanPropertyState` — one filter per property being
smoothed.

Keeping the filter state keyed by property name is the detail that makes the
anti-sycophancy mechanism usable: `confidenceScore` is filtered independently of
anything else, and a system can smooth exactly the properties an agent is
allowed to move.

Namespace is a component of the storage key prefix rather than a column, so
scoping is structural in the key layout and cannot be omitted by a query that
forgets a predicate — the same shape of guarantee as
[Octopoda](../octopoda-os/)'s row-level security, reached at the key level.

## 6. Retrieval Mechanics

Cypher over the graph, hybrid graph-and-vector retrieval, and a knowledge-policy
scoring filter that acts on visibility — the test names
(`scorer_property_visibility_test.go`,
`access_flusher_property_suppression_test.go`) show that scoring decides what is
returned, not only how it is ordered.

**The important limitation is stated in the README and it is the reason
`bitemporal` is withheld.** "Search remains current-state focused: current search
paths are intentionally separate from historical MVCC state." So the database can
hold a validity interval, index it, and enforce its shape as a constraint — and
the retrieval path a memory client actually uses does not query it. The
capability lives at the storage layer; the memory surface does not reach it.

That is a different failure from the common one. Elsewhere in this atlas the
columns exist and nobody wired the read. Here the read exists, at a lower layer,
and the search path is deliberately kept away from it.

MVCC retention is handled with an explicit safety posture: pruning "preserves the
current head and a retained floor per logical key; requests below that retained
floor fail safely with `ErrNotFound`". A historical read that has aged out
returns a clean not-found rather than a stale or partial answer.

## 7. Write Mechanics

Transactional, anchored to an MVCC version, with constraint validation before
commit. Deletes are versioned rather than destructive at the storage layer, and
the vector index tombstones rather than rewires.

There is no rejected-value record and no supersession semantics above the version
chain: a corrected fact is a new version of a node, and re-asserting a previously
deleted value succeeds. What the database provides instead is the ability to
*ask what was true before*, which is the other half of correction and the half
most memory systems lack.

## 8. Agent Integration

Bolt and Cypher for anything that speaks Neo4j, a Qdrant-compatible gRPC
endpoint for anything that speaks Qdrant, GraphQL, native gRPC, and MCP. A
memory layer built on this does not have to choose between a graph client and a
vector client.

The `eval`, `inference`, `localllm`, `embed` and `linkpredict` packages mean
embedding and link prediction can run inside the database rather than in the
application, which is the design decision that makes the access-pattern decay
possible at all — the database sees every access.

## 9. Reliability, Safety, and Trust

**Audit log — awarded.** `pkg/audit` declares itself as implementing "immutable
audit trails required by major regulatory frameworks" and names them with
article numbers — GDPR Art.30 and Art.15, HIPAA §164.312(b) and
§164.308(a)(1)(ii)(D), FISMA AU-2 and AU-3, SOC2 CC7.2, SOX §404 — with
append-only entries, structured JSON, real-time alerting and a seven-year default
retention. Citing the specific clause a control answers, rather than a framework
name, is what makes a compliance claim checkable.

**Scope — awarded**, for the namespace prefix in the key layout plus multi-database
separation.

**Bitemporal — withheld**, for the reason in section 6, and it is the most
frustrating withholding in this batch: the constraint, the index and the MVCC
reads are all there, and the search path does not use them.

**Trust state — no.** `confidenceScore` is a filtered float. The Kalman work is a
trust *model* of unusual quality with no trust *state* attached to a node.

**Tombstone — no.** The HNSW `deleted []bool` flags are index bookkeeping.

**Human review, negative eval — no** on what was inspected.

**One caution about the surface.** Forty-plus packages including encryption,
KMS, replication, GPU kernels and SIMD, with compliance and audit among them,
is a large amount of security-relevant machinery for any single reviewer to
assess. This report checked the memory-relevant packages and did not audit the
security ones; a deployment decision should not treat this section as coverage of
them.

## 10. Tests, Evals, and Benchmarks

**No paper.** The test discipline is the evidence: `pkg/knowledgepolicy` alone
carries benchmark tests, property tests, scenario tests, integration tests and a
legacy-fallback test beside almost every implementation file, and the
anti-sycophancy test is written as a behavioural specification with three
assertions covering settle, spike and recovery.

`pkg/eval` exists in the tree. No committed benchmark result or scorecard was
found, and the README makes no retrieval-quality claim — it claims
Neo4j-compatibility, hybrid retrieval and MVCC, which are architectural claims a
reader can check by reading rather than by running.

**I ran nothing.** The screen flagged `.githooks/` as an auto-run surface, two
`Makefile`s with build-time execution, and five dependency manifests inside the
seven-day cooldown including `go.mod` and `go.sum`. A tree with active git hooks
is one to read only.

## 11. For Your Own Build

### Steal

- **Make temporal validity a constraint, not a convention.** `TEMPORAL (key,
  valid_from, valid_to)` validated at write time means a node cannot claim a
  temporal label without the fields, and a reader cannot forget them. Several
  reports in this atlas exist because a validity pair was written and never
  queried; a declared constraint is the structural fix.
- **Put the namespace in the key prefix.** Scoping that lives in the key layout
  cannot be omitted by a query that forgets a predicate.
- **Filter a confidence signal before you trust it.** A Kalman filter with a
  large measurement-noise term makes one enthusiastic 0.99 cost almost nothing
  and a sustained shift cost what it should. The test is the specification: settle,
  spike, recover.
- **Name the failure in the test file.** `kalman_anti_sycophancy_test.go` tells a
  reader in the filename what the mechanism is defending against.
- **Keep filter state per property.** One filter per property name means you can
  smooth exactly the values an agent is allowed to move and leave the rest alone.
- **Fail a stale historical read, don't approximate it.** Below the retained
  floor, `ErrNotFound` — a clean refusal beats a plausible answer from the wrong
  version.
- **Cite the clause, not the framework.** "HIPAA §164.312(b)" is checkable;
  "HIPAA compliant" is not.
- **Derive decay from access pattern, not just recency.** Daily-pattern nodes
  persisting and burst-accessed nodes getting a temporary boost is a better model
  of what an agent needs than a single half-life.

### Avoid

- **Do not build the temporal machinery and route search around it.** The
  constraint, the index and MVCC are all present, and "search remains
  current-state focused" means a memory client gets none of it.
- **Do not read index tombstones as memory tombstones.** The HNSW `deleted`
  flags are a delete-cost optimisation with a `TombstoneRatio()` to watch, not a
  record of a rejected value.
- **Do not assume a memory story from a database feature list.** Everything here
  that behaves like memory — decay, access scoring, visibility — lives in
  `knowledgepolicy` and `temporal`, and both are layers a client has to opt into.

### Fit

This suits a team that wants one engine for graph, vector and history and is
willing to run a database — particularly one already speaking Bolt or Qdrant that
would rather not add a second system. The MVCC historical reads are a genuine
capability almost no memory store has.

It is not a memory product. Nothing here decides what to remember, extracts a
fact, resolves a contradiction or forgets on purpose beyond decay. Those are the
application's job. What NornicDB offers is a substrate where validity is
enforceable and history is queryable — and a reader building the layer above
should start from `pkg/knowledgepolicy` and the temporal constraint, and check
whether the search-path separation blocks what they need.

## 12. Open Questions

- **Will search ever meet MVCC?** The separation is stated as intentional; what
  it would take to answer "what did the graph say about X last March" through the
  search path rather than a point read is the question a memory client cares
  about most.
- **What sets `Q` and `R` in practice?** The anti-sycophancy behaviour is
  entirely a function of the noise terms; the test pins `Q=0.05, R=50.0` in
  manual mode, and what an automatic mode chooses was not traced.
- **What consumes the knowledge-policy score?** The property-visibility tests
  show it gates results; whether a client can inspect why something was filtered
  was not established.
- **Is the temporal constraint used by anything shipped?** It is validated and
  indexed; no built-in query path that exploits it was found.

## Appendix: File Index

**Temporal constraint and index** —
`pkg/storage/badger_constraint_validation.go:164-200` (node validation), `:717`
(edge validation), `pkg/storage/badger.go:36` (`prefixTemporalIndex`),
`pkg/storage/badger_edge_constraint_validation_test.go:163`

**Kalman / anti-sycophancy** — `pkg/knowledgepolicy/kalman_accumulator.go`
(`ProcessKalmanMutation`), `kalman_anti_sycophancy_test.go`,
`kalman_multiagent_test.go`, `pkg/filter/kalman.go`

**Access and scoring** — `pkg/knowledgepolicy/access_accumulator.go`,
`access_flusher.go`, `access_meta.go`, `scorer.go`, `scoring_filter.go`,
`compiled_binding.go`, `resolver.go`, `inverse_decay_scenario_test.go`

**Decay** — `pkg/temporal/decay_integration.go` (the pattern-to-decay mapping
`:1-13`), `pattern_detector.go`, `relationship_evolution.go`

**Audit and compliance** — `pkg/audit/audit.go` (the framework clause list
`:3-19`), `pkg/compliance/`, `pkg/retention/`, `pkg/lifecycle/`

**Vector index** — `pkg/search/hnsw_index.go` (the tombstone trade `:6-7`,
`TombstoneRatio` `:619`), `pkg/qdrantgrpc/vector_index_cache.go`

**Interfaces** — `pkg/bolt/`, `pkg/cypher/`, `pkg/graphql/`, `pkg/nornicgrpc/`,
`pkg/qdrantgrpc/`, `pkg/mcp/`

**MVCC** — `docs/user-guides/transactions.md`,
`docs/user-guides/historical-reads-mvcc-retention.md`,
`docs/user-guides/canonical-graph-ledger.md`

## History

**2026-08-09** — [`a5f623399830d76e3e22e56264548c613ba897aa`](https://github.com/orneryd/NornicDB/commit/a5f623399830d76e3e22e56264548c613ba897aa) — first reading. Screened before reading: one auto-run surface (`.githooks/`), build-time execution in two `Makefile`s, and five dependency manifests inside the seven-day cooldown including `go.mod` and `go.sum`. The tree was read, never built, and no test was run. The licence is MIT per the README badge and `LICENSE.md`; there is no plain `LICENSE` file.

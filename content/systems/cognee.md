---
title: "Cognee"
eyebrow: "Knowledge-graph memory control plane"
description: "A pipeline-driven memory platform that turns multimodal data into ontology-grounded graph, vector, and relational knowledge for agents."
root: ../..
page_kind: system
source_name: "topoteretes/cognee"
source_url: https://github.com/topoteretes/cognee
revision: 325acf356a81545b9892f19ab1ea7b61c51a776b
revision_url: https://github.com/topoteretes/cognee/commit/325acf356a81545b9892f19ab1ea7b61c51a776b
analyzed_at: 2026-07-27
capabilities: "scope_enforced"
matrix:
  memory_unit: "Source data, chunk, typed `DataPoint`, graph edge, summary, session entry"
  storage: "SQLite/PostgreSQL plus pluggable graph/vector stores"
  retrieval: "Chunk, lexical, vector, graph, triplet, summary, temporal, hybrid, and routed modes"
  write: "`add` + `cognify`; unified `remember`; session-hot writes with background improvement"
  update_delete: "Exact data/dataset/all forget; memory-only reprocessing; provenance rollback"
  scoping: "User permissions and dataset; optional per-user/dataset backend isolation"
  integration: "Python, REST, CLI, MCP, typed memory entries"
  background: "Composable pipelines, session bridge, memify, rollback/recovery"
  trust: "Source records, content hashes, pipeline/task/user provenance; no factual trust state"
  strengths: "Ontology-aware multimodal graph pipeline with serious rollback"
  risks: "Large configuration surface; cross-store consistency; extracted graph can harden errors"
---

## 1. Executive Summary

Cognee is a memory and knowledge pipeline rather than a thin vector-store
wrapper. It preserves source data, extracts a typed knowledge graph, embeds
chunks and graph material, supports ontology grounding, and exposes many
retrieval strategies over relational, graph, vector, and session stores.

Its best architectural move is the separation between:

- `add`: register and preserve source material.
- `cognify`: turn that material into graph and vector projections.
- `search` / `recall`: query one or more memory views.
- `memify` / `improve`: enrich an existing memory asynchronously.
- `forget`: remove a data item, a dataset, derived memory, or all user data.

The newer `remember` and `recall` APIs compress this machinery into a smaller
agent-facing mental model. A session write can land in a fast cache and bridge
to permanent graph memory in the background; a permanent write runs
`add` plus `cognify`.

Cognee is the strongest choice in this atlas when the requirement is an
ontology-aware, multimodal knowledge graph with pluggable storage. It is a poor
fit when the requirement is a small, deterministic memory component: its
configuration and adapter surface is large, extraction remains probabilistic,
and consistency spans several stores.

The inspected package version is `1.4.0` (2026-07-25).


## 2. Mental Model

Cognee treats memory as several projections of source material:

```text
source document / message / trace
    -> relational data record and raw content
    -> chunks
    -> LLM-extracted entities and relations
    -> graph nodes and edges
    -> vector indexes and summaries
    -> optional ontology identifiers, session lessons, and global context
```

The source record is the evidence layer. `DataPoint` objects and graph edges are
derived memory. Dataset membership is both an organizational boundary and an
authorization boundary. Session cache is a hot layer; the graph is the durable,
queryable knowledge layer.

This is not a single memory algorithm. It is a control plane for composing
ingestion, extraction, storage, enrichment, retrieval, migration, and deletion
pipelines.


## 3. Architecture

```mermaid
flowchart LR
  Sources["Text, files, URLs, tables, media"] --> Add["add / remember"]
  Add --> Raw["Relational records + source files"]
  Raw --> Cognify["cognify task pipeline"]
  Cognify --> Graph["Graph store"]
  Cognify --> Vector["Vector store"]
  Cognify --> Summary["Chunks + summaries"]
  Session["Session cache"] --> Recall["recall"]
  Session --> Improve["background improve / memify"]
  Improve --> Graph
  Graph --> Search["search / recall retrievers"]
  Vector --> Search
  Summary --> Search
  Search --> Agent["SDK, API, CLI, MCP"]
```

Local development can run embedded with SQLite plus local graph and vector
stores. Production deployments can consolidate around PostgreSQL or select
specialized adapters such as Neo4j, Neptune, pgvector, Qdrant, Chroma,
Weaviate, or Milvus. The unified engine and pipeline layer hide much of this
variation, but cannot make distributed writes intrinsically atomic.

`cognee/modules/pipelines/` defines reusable task execution. The default
cognify pipeline classifies documents, chunks them, extracts graph structures,
persists data points, and creates embeddings. Rollback and stale-run recovery
are explicit subsystems rather than incidental exception handlers.


## 4. Essential Implementation Paths

Public lifecycle:

- `cognee/api/v1/add/add.py`: resolves sources and runs the ingestion pipeline.
- `cognee/api/v1/cognify/cognify.py`: builds and executes the graph/vector
  extraction pipeline.
- `cognee/api/v1/remember/remember.py`: routes typed entries, permanent
  add-plus-cognify writes, and session-cache writes.
- `cognee/api/v1/recall/recall.py`: merges or short-circuits session and graph
  recall according to an explicit scope.
- `cognee/modules/search/methods/search.py`: authorized dataset search.
- `cognee/modules/memify/memify.py`: post-ingestion enrichment pipelines.
- `cognee/api/v1/forget/forget.py`: exact item, dataset, derived-memory, and
  user-wide deletion.

State and recovery:

- `cognee/infrastructure/engine/models/DataPoint.py`: typed, versioned graph
  data with optional deterministic identity and provenance fields.
- `cognee/tasks/storage/add_data_points.py`: graph/vector persistence.
- `cognee/modules/cognify/rollback.py`: provenance-aware rollback.
- `cognee/modules/cognify/recovery.py`: startup recovery for stale runs.
- `cognee/modules/users/permissions/`: dataset permissions and principals.


## 5. Memory Data Model

`DataPoint` is the base graph-memory unit. It includes:

- UUID, type, creation/update timestamps, and version.
- Optional deterministic identity derived from declared identity fields.
- Ontology validity and stable ontology URI.
- Set membership, topological rank, feedback and importance weights.
- Source pipeline, task, node set, user, and content hash.

Domain-specific Pydantic models extend this base. Graph `Edge` and `Triplet`
types express relationships; chunks and documents retain the connection to
ingested data. Relational `Dataset`, `Data`, pipeline-run, user, permission, and
session records track ownership and lifecycle outside the graph.

The model carries substantial provenance, but ontology validity is not the same
as factual verification. An LLM-extracted relation can be well attributed and
schema-valid while still being wrong.


## 6. Retrieval Mechanics

`SearchType` exposes chunk, lexical chunk, RAG, summary, triplet, graph,
chain-of-thought, context-extension, decomposition, hybrid, Cypher, natural
language structured query, temporal, coding-rule, and agentic modes.

The important distinction is that these modes do not share one universal
ranking contract:

- Chunk and vector modes retrieve source passages.
- Graph modes traverse or complete over extracted entities and relations.
- Summary modes query compressed representations.
- Hybrid modes combine several channels.
- `recall` can search session entries by lexical token overlap before, or
  alongside, permanent graph retrieval.
- `FEELING_LUCKY` / automatic routing selects a strategy for the caller.

Dataset resolution occurs before authorized search. The recall response can
label session versus graph origin, which is valuable when the caller must
distinguish hot conversational state from derived permanent memory.

Retrieval breadth is a strength, but it increases evaluation burden. A top-k
from graph completion is not directly comparable to a top-k chunk list, and
automatic routing can hide which retrieval policy produced an answer.


## 7. Write Mechanics

Permanent `remember` writes call `add` and `cognify`, then optionally
`improve`. `add` resolves inputs, stores source data, assigns dataset
permissions, and records pipeline state. `cognify` performs LLM extraction and
persists derived graph/vector artifacts.

With `session_id`, `remember` instead writes a QA-shaped entry to the session
cache. With self-improvement enabled, it schedules a bridge into permanent
memory. This keeps the interactive path fast while accepting eventual
consistency.

The write path supports deterministic IDs for domain models that declare
identity fields, incremental loading, content hashes, custom graph models,
ontologies, background execution, and dry-run cost estimation.

Failure handling is unusually serious. Cognify attaches provenance to generated
artifacts, rolls back by pipeline run, and recovers sufficiently old
non-terminal runs at startup. The age threshold is a pragmatic substitute for a
lease or heartbeat, so a long-running live job still requires careful tuning.


## 8. Agent Integration

Cognee exposes Python, REST, CLI, and MCP surfaces. The `remember`, `recall`,
`improve`, and `forget` vocabulary is the clearest agent integration because it
hides most pipeline details while retaining explicit dataset and session scope.

Typed `MemoryEntry` variants support QA, traces, feedback, and skill-run
records. The repository also includes agent-memory runtime modules, session
lifecycle hooks, migration sources for Mem0, Zep/Graphiti, and Letta, plus
export/push paths.

This breadth enables many integrations but should not become the default agent
tool list. A small governed subset is easier for a model to call correctly than
the full administration and retrieval surface.


## 9. Reliability, Safety, and Trust

Strengths:

- User-to-dataset permissions are enforced before reads and writes.
- Supported backends can isolate graph and vector data per user and dataset.
- Provenance-aware rollback removes artifacts introduced by a failed run.
- Startup recovery clears stale processing states.
- `forget` supports exact targets and a `memory_only` mode that retains sources
  for reprocessing.
- Raw sources remain available underneath lossy graph extraction.
- Deterministic node identity can make repeated ingestion idempotent.

Limitations:

- Correctness spans relational, graph, vector, file, and cache stores.
- Session-to-graph improvement is intentionally asynchronous.
- LLM-extracted nodes become queryable without a candidate/verified/rejected
  trust state.
- Dataset permissions govern access, not truth or instruction safety.
- Local file, outbound HTTP, and raw Cypher capabilities are enabled by
  documented defaults; production operators must narrow them deliberately.
- Backend access control is configurable, so deployments must verify that
  authentication and isolation settings match their threat model.


## 10. Tests, Evals, and Benchmarks

The repository contains broad unit, integration, end-to-end, adapter,
permission, deletion, provenance, recovery, migration, and performance tests.
The source test suite was not run for this atlas review because many paths
require database and model-provider infrastructure.

The committed BEAM report is transparent about its limits. It reports `0.79`
on a held-out 100K conversation using fixed hybrid retrieval and `0.67` on an
exploratory 10M run. The 10M routing configuration was selected on the same
questions used for reporting, and the distributed ingestion orchestration is
not included. Both results use synthetic conversations and LLM judging. They
are useful directional evidence, not a product-level reliability claim.

The report includes configs and per-run artifacts for the evaluation layer;
this atlas inspected those artifacts but did not rerun the benchmark.


## 11. Patterns Worth Stealing

- Preserve source records before creating graph/vector projections.
- Make a pipeline run and its provenance the unit of rollback.
- Use deterministic IDs only when a model declares stable identity fields.
- Separate session-hot memory from permanent graph memory.
- Let `memory_only` deletion remove projections while retaining reprocessable
  evidence.
- Authorize datasets before retrieval, not after ranking.
- Offer a small memory-oriented API over a composable internal pipeline.
- Estimate expensive extraction before starting it.


## 12. Antipatterns / Risks

- Confusing ontology conformance or provenance with factual verification.
- Treating every search mode as if it had equivalent top-k semantics.
- Exposing raw Cypher, filesystem ingestion, or outbound fetch to agents
  without a separate policy boundary.
- Assuming a unified abstraction makes cross-store writes atomic.
- Enabling automatic permanent promotion without correction and trust states.
- Copying the complete platform when the product needs only evidence storage
  plus retrieval.


## 13. Build-vs-Borrow Takeaways

Borrow Cognee when graph structure, ontology grounding, multimodal ingestion,
storage adapters, and dataset-level access control are central requirements.
Budget for LLM extraction, schema design, backend configuration, and repair
operations.

Build a smaller system when memory is mostly conversational or project-local.
The minimum valuable subset to borrow conceptually is source preservation,
dataset scope, composable derivation, rollback by provenance, hybrid retrieval,
and exact forgetting.

For consequential automation, add a belief-review layer above Cognee's derived
graph. The platform records where a claim came from; the application must still
decide whether to trust it.


## 14. Open Questions

- What consistency guarantees are supported for each graph/vector/relational
  backend combination?
- Can session-to-permanent promotion expose candidate state before activation?
- Which automatic retrieval router is stable enough to be a public contract?
- How are untrusted instructions in source documents fenced at recall time?
- Can stale-run recovery move from an age threshold to a lease or heartbeat?
- Which BEAM configuration generalizes after being frozen on unseen data?


## Appendix: File Index

- `cognee/__init__.py`: public API.
- `cognee/api/v1/remember/remember.py`: unified write path.
- `cognee/api/v1/recall/recall.py`: session and graph recall.
- `cognee/api/v1/add/add.py`: source ingestion.
- `cognee/api/v1/cognify/cognify.py`: default extraction pipeline.
- `cognee/modules/search/types/SearchType.py`: retrieval modes.
- `cognee/modules/search/methods/search.py`: authorized search.
- `cognee/infrastructure/engine/models/DataPoint.py`: base graph record.
- `cognee/modules/cognify/rollback.py`: provenance rollback.
- `cognee/modules/cognify/recovery.py`: stale-run recovery.
- `cognee/api/v1/forget/forget.py`: deletion lifecycle.
- `cognee/eval_framework/beam/REPORT.md`: committed BEAM evaluation.

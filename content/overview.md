---
title: Agent Memory Systems Comparative Report
eyebrow: Cross-system synthesis
description: A code-grounded comparison of sixteen agent memory architectures, their retrieval mechanics, trust models, and operational tradeoffs.
root: ..
page_kind: comparison
---

## 1. High-Level Taxonomy

This workspace contains several different answers to "agent memory". They should not be evaluated as one category.

### Library-first memory layer

Repos:

- `mem0`
- `langmem`
- `graphiti`

These optimize for easy embedding into an existing agent application. The application calls memory tools or SDK functions; the library handles extraction, storage, and retrieval.

Tradeoff: the memory layer is easy to adopt but usually has weak authority over the agent loop. It can store and retrieve, but it cannot guarantee the model calls the right tool at the right time, verifies facts, or uses the recall output safely.

### Agent-runtime memory

Repos:

- `letta`
- `rainbox`
- `mastra-observational-memory`
- `memos`

This treats memory as part of the agent runtime. Memory is not merely an external RAG sidecar; it is compiled into or injected into prompt/context, mutated through first-class tools/actions, searched through runtime services, and tied to agent state.

Tradeoff: deeper integration gives better control over behavior, but the memory subsystem becomes coupled to the agent framework, tool execution, message manager, prompt/context assembly, review UI, and compatibility surface.

### Hosted/product memory service

Repos:

- `honcho`
- `supermemory`
- `hindsight`
- partly `mem0`

These optimize for multi-user, multi-session, product-oriented memory. They expose APIs, SDKs, MCP tools, and background processing.

Tradeoff: the API surface is often much easier to study than the actual decision machinery. In `supermemory`, the most important hosted backend logic is not visible in this checkout. In `mem0`, several advanced capabilities mentioned in docs are managed-platform-only in the OSS code.

### Coding-agent local memory

Repos:

- `engram`
- `mempalace`
- `llm-wiki-memory`
- `basic-memory`

This optimizes for a local developer workflow: durable local memory, MCP/tools/hooks, project scopes, exact search, vector search, conflict or dedupe handling, and sync/repair hooks.

Tradeoff: local-first design is operationally simple and inspectable, but it does not solve large-scale hosted ranking, multi-tenant APIs, or rich social/user modeling. `engram` is compact and FTS-oriented; `mempalace` is broader, benchmark-heavy, and vector/hybrid retrieval-oriented; `llm-wiki-memory` is filesystem/git-oriented, hook-heavy, federated across private and repository wikis, and unusually focused on capture recovery and operations.

### Temporal knowledge-graph memory

Repo:

- `graphiti`

Graphiti preserves episodes as evidence, resolves entities and relationships, and tracks both transaction time and real-world validity time. Facts can be invalidated by closing a temporal interval without erasing history.

Tradeoff: temporal graphs answer changing-world questions that flat fact stores cannot, but LLM entity resolution and edge invalidation can make structural mistakes with a wide blast radius.

### Observation-reflection context memory

Repo:

- `mastra-observational-memory`

Mastra Observational Memory compresses older messages into dated observations, then reflects growing observations into a smaller context. Buffered results can be computed before a hard threshold and activated without blocking.

Tradeoff: this is excellent context-window management, not a general evidence or truth system. Its correctness depends on a complex threshold, marker, storage, and concurrency state machine.

### Memory operating substrate

Repo:

- `memos`

MemOS packages textual, preference, skill, activation/KV-cache, and parametric/LoRA memory into mountable memory cubes managed by a user-aware runtime and schedulers.

Tradeoff: the abstraction is unusually broad, but configured modules have different search, durability, deletion, compatibility, and maturity guarantees.

### Human-editable canonical memory

Repo:

- `basic-memory`

Basic Memory makes Markdown notes authoritative while SQLite/PostgreSQL entities, observations, relations, FTS rows, and semantic chunks remain rebuildable projections.

Tradeoff: direct human ownership and portability are strong, but bidirectional file/database synchronization is a substantial consistency problem rather than “just Markdown”.

### Compact local graph-RAG memory

Repo:

- `swafra`

Swafra optimizes for a tiny, no-cloud MCP sidecar: ingest titled text, retain it as chunks, index with local embeddings and lexical signals, connect chunks in a graph, and return source-diverse context.

Tradeoff: the implementation is easy to understand and run, but it has no database transactions, scopes, trust states, bounded context assembly, or ordinary tests. Its checked-in benchmark does not enforce the advertised retrieval cutoff.

### Verbatim evidence memory

Repo:

- `mempalace`

MemPalace optimizes for preserving original evidence. It stores raw conversation/file text as drawers and treats extracted/indexed layers as navigation aids rather than the authoritative memory.

Tradeoff: this avoids lossy LLM extraction and preserves auditability, but it creates larger corpora and pushes more work into retrieval, context selection, privacy, and deletion.

### Peer/session representation system

Repo:

- `honcho`

Honcho is not just "save facts and search them". It models workspaces, peers, sessions, messages, observations, and representations. It derives observations from conversation events and serves a working representation back to applications.

Tradeoff: richer domain modeling gives more useful cross-session state, but it requires queueing, derivation, reconciliation, and consistency semantics.

### Operator-governed assistant memory

Repo:

- `rainbox`

RainBox optimizes for memory that an operator can inspect, correct, audit, and evaluate. Its distinctive layer is not the vector ranker; it is the loop from memory claims/evidence to retrieval telemetry, feedback, eval cases, and review UI.

Tradeoff: this works well inside a full assistant product, but it is much heavier than a library and less source-preserving than MemPalace's verbatim drawer model.

### Verification-first memory

Repo:

- `verel`

Verel treats memory as a trust problem. It separates confidence, retrieval strength, and verification state; carries rejected values forward; fences recalled memory as untrusted data; and uses promotion gates for induced rules.

Tradeoff: this is more complex than most systems need for an MVP, but it directly addresses failures that simpler memory systems usually ignore.

## 2. Comparative Matrix

| Repo | Memory unit | Storage backend | Retrieval strategy | Write strategy | Update/delete model | Scoping model | Agent integration | Background processing | Trust/provenance model | Notable strengths | Main risks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `mem0` | Text fact in vector payload | Vector store plus SQLite history/messages | Semantic, optional keyword/BM25, entity boost, optional rerank | LLM additive extraction, hash dedupe, entity linking | Explicit update/delete APIs; V3 default append-oriented | `user_id`, `agent_id`, `run_id`, filters | Python SDK, tool/API style | Extraction and linking on write | Attribution metadata, history; weak epistemic trust | Practical SDK, pluggable stores, hybrid search | LLM facts can become durable claims without verification |
| `langmem` | Store item, usually JSON memory | LangGraph `BaseStore` | `store.search/asearch` delegated to backend | Tools call create/update/delete/search; extraction via Trustcall | Tool-level CRUD | Namespace templates | LangChain/LangGraph tools | Reflection executor local/remote | Mostly application-defined | Clean primitives, schema-driven extraction | Too low-level to solve memory quality alone |
| `honcho` | Message, document/observation, representation | Postgres/SQLAlchemy, pgvector or vector adapter | Working representation blends semantic, recent, most-derived; message search with windows | Message ingestion plus queued derivation | Soft delete, representation reconciliation | Workspace, peer, session, collection | Hosted API/service model | Deriver queues and workers | Source IDs, derived observations, peer/session provenance | Strong event-to-representation pipeline | Operational complexity; LLM-derived observations still need trust policy |
| `engram` | Observation and prompt records | Local SQLite WAL, FTS5 | FTS5, topic-key lookup, context assembly | MCP `mem_save`, conflict candidate flow, dedupe/update rules | Topic-key updates, duplicate counts, soft delete/sync mutation | Project, scope, session, topic key | MCP tools for coding agents | Sync queue, local conflict workflows | Source/session/project metadata, explicit judgment path | Simple durable local design, inspectable code | Lexical retrieval limits; conflict UX depends on agent behavior |
| `mempalace` | Verbatim drawer chunks, closets, KG triples | Local Chroma default; sqlite_exact, Qdrant, pgvector; SQLite KG | Direct drawer vector search, BM25 rerank, closet boost, metadata filters, FTS fallback | Mine files/convos or MCP add drawer; deterministic IDs; chunk/upsert verbatim text | Delete/update drawers, delete by source, dedup, repair; limited epistemic correction | Palace, wing, room, source file, parent drawer, backend namespace | MCP, CLI, hooks, skills, wake-up stack | Mining, closet/hallway/tunnel computation, repair/sync/backup | Strong source provenance; weak candidate/verified/rejected trust state | Evidence-preserving raw baseline, hybrid retrieval, operational hardening | Raw stores get large/noisy; contradiction resolution mostly outside core recall |
| `swafra` | Verbatim or synthetic chunk plus directed chunk edges | Three local JSON files | BM25 + vector + entity/date/preference heuristics + char n-gram; graph walk; best chunk per title | MCP add; Leiden or exchange/paragraph chunks; synchronous full-file rewrite | Exact source delete; implicit same-ID reindex; broken supersession path | Source ID/title only; no user/project/tenant scope | Python FastMCP; Node MCP over Python subprocess | None | Caller title and raw chunk; no actor, span-quality provenance, trust state, or injection fence | Very compact local hybrid graph-RAG; optional dependencies; source diversity | Non-atomic concurrent writes; unbounded context; dangling edges; benchmark cutoff invalid |
| `llm-wiki-memory` | Typed Markdown atom, plan/investigation, daily capture, or full document | Filesystem wiki, per-category embedding caches, private git history | Metadata prefilter, local embedding/chunk cosine, priority bands, federated locality boost; lexical vector fallback | MCP/CLI writes, transcript and plan hooks, daily compile, full-document absorb | Upsert/relocate, archive/re-enable, exact delete, supersedes, opt-in dedup/refresh consolidation | Private brain plus explicit repository wiki levels; workspace/area/task/subject facets | MCP, CLI, Claude Code lifecycle hooks, shared instructions | Detached flush, daily compile, opt-in consolidation, cron healing, git/cache maintenance | Body hash, capture audit, git history, user-gated lessons; no candidate/verified/rejected state | Recoverable capture, explicit targets, deterministic layout/topology, excellent operational tests | LLM atoms become active without verification; vector-only primary retrieval; linear scans; git is not erasure |
| `rainbox` | Claim, evidence, embedding, retrieval event | Postgres/SQLAlchemy plus pgvector | Hard-filtered hybrid (vector + Postgres full-text + entity boost) for both chat and assistant; profile digest | User commands, assistant actions, review UI; single governed atomic path (`record_belief`); write-time conflict detection; active/candidate flows | Reject/supersede/reactivate/expiry/sensitivity; `MemoryRejectedValue` tombstones block model re-assertion of rejected values; governed atomic correction (`correct_belief`); UI stale-write guards | Global, agent, room, project; sensitivity | Full assistant app: chat prompt (via `build_chat_memory_block`→hybrid), action loop, review UI | Embedding sync/prune, telemetry, feedback/eval loop | Five-actor trust model (3 human/override + 2 model/candidate); rejected-value tombstones; write-time lattice-aware conflict detection; governed atomic correction; fenced prompt injection; claim/evidence provenance and retrieval audit | Operator governance, trust/correction machinery (tombstones + conflict detection + fenced recall + governed writes), telemetry, eval integration | Compact claims may lose source nuance; no automatic candidate extraction; `epistemic_confidence`/`retrieval_strength` columns exist but Tier-1 ranking still uses `confidence` (schema groundwork only); attribution is context-injection, not causal |
| `letta` | Core memory block, archival passage, message | ORM database; passages with embeddings; optional git memory | Archival search, conversation search, compiled core prompt | Agent tools mutate core/archival memory | Append/replace/patch, passage insert, block update | Agent, block labels, files/sources | Deep runtime tool executor integration | Prompt rebuilds, manager services | Block tags/metadata, message timestamps; limited truth model | Clear core/archive/recall separation | Agent can rewrite important memory without strong verification |
| `supermemory` | Document, chunk, memory entry, space | Hosted backend; visible schemas/client only | Hosted search/profile API; SDK uses hybrid settings | API/MCP add memory/document | Version chains, relations, forget API | Space, container tags, org/user/project | SDK, AI SDK tools, MCP | Hosted processing not visible | Rich schema fields and relations; implementation not visible | Product/API surface, document-memory graph | Backend black box; semantic forget needs care |
| `verel` | `MemoryRecord` fact/rule/schema/failure/skill | SQLite local plus backend adapters | Rank blends relevance, retrieval strength, confidence, trust; budgeted recall | Candidate extraction, attested/corroborated promotion | Correction chains, rejected tombstones, decay/prune | Scope lattice | Helpers, MCP, hosted/replicated adapters | Consolidation, promotion gate, replication | Explicit candidate/verified/rejected, provenance, confidence | Best correctness model in set | Complex; may be heavy for product MVP |
| `hindsight` | Source chunk, world/experience fact, observation, reflection | PostgreSQL/pgvector or Oracle | Semantic + BM25 + graph + temporal, RRF/interleave, cross-encoder rerank | Screen, chunk, extract, embed, link, consolidate | Replace/append source; observation create/update/history; exact bank/document operations | Memory bank, tags, schemas/tenants | REST, MCP, generated SDKs, framework integrations | Queued consolidation and maintenance with retries | Source IDs, proof counts, audit/LLM traces; no explicit truth state | Complete service pipeline; task-specific fusion; temporal recall | LLM facts/observations can harden errors; operational complexity |
| `graphiti` | Episode, entity, temporal relationship edge, community/saga | Neo4j, FalkorDB, Kuzu, Neptune | BM25 + cosine + BFS across edges/nodes/episodes/communities; RRF/MMR/cross-encoder | Episode ingestion, entity/edge extraction, resolution, temporal invalidation | Close `valid_at` intervals, expire edges, remove episodes | `group_id`, entity/edge types | Python library, MCP, server | Ingestion maintenance; saga summaries | Source episode UUIDs and bi-temporal history; no verified state | Preserves changing facts without erasing history | Entity merge/invalidation mistakes reshape the graph |
| `mastra-observational-memory` | Raw message, dated observation group, reflected observation context | Mastra `MemoryStorage` adapters | Sequential active observations + recent raw tail; optional observation-vector retrieval | Processor observes at token thresholds; reflector compacts observations | Range replacement, buffered activation, clear/clone records | Thread or resource | Deep Mastra input/output processor integration | Early async observation/reflection buffers with activation | Exact covered ranges and markers; summary has no truth state | Non-blocking context compaction for long sessions | Distributed locking and progressive summary drift |
| `memos` | Textual item, graph tier, preference/skill, KV cache, LoRA | Configurable vector/graph stores, dumps, cache/model artifacts | Direct vector or graph + BM25 + rerank + reasoner; optional auxiliary memories | Reader extraction into a memory cube; scheduler transformations | Module-specific update/delete/soft-delete/dump semantics | User plus registered memory cube | MOS chat/runtime, APIs, CLI | Scheduler and activation-memory refresh | Source metadata varies by module; no uniform trust state | Treats memory as heterogeneous mountable resources | Umbrella API hides uneven guarantees and maturity |
| `basic-memory` | Canonical Markdown note; indexed entity, observation, relation | Filesystem source + SQLite/PostgreSQL projection | FTS5/tsvector, optional semantic chunks, hybrid score fusion, graph context | MCP/API writes accepted Markdown; file watcher reconciles human edits | Distinct create/replace/edit/move/delete with stable ID and reindex | Project, workspace, tenant, local/cloud route | MCP tools, typed clients, API, CLI | Watcher, startup reconciliation, indexing workflows | Human-visible source/checksums; no candidate/verified state | Inspectable portable memory with rebuildable indexes | Bidirectional sync complexity; agent can write unsupported claims |

## 3. End-to-End Memory Lifecycle Comparison

### Capture

`mem0`, `letta`, `langmem`, and `supermemory` expose direct tool/SDK surfaces for adding memory. `hindsight` retains documents/chunks before extracting facts. `graphiti` stores episodes before deriving entities and temporal relationships. `mastra-observational-memory` persists messages before compressing covered ranges. `memos` routes items into configured memory cubes. `basic-memory` accepts Markdown writes from MCP/API or human file edits and reconciles indexes. `rainbox` captures through explicit memory commands, assistant memory actions, and review UI mutations. `engram` captures via MCP tools and can also store prompt/session metadata. `mempalace` captures by mining files/conversations and by MCP drawer writes, preserving verbatim text. `swafra` captures titled text via one MCP tool, then stores chunks in local JSON. `llm-wiki-memory` combines explicit MCP/CLI writes with lifecycle hooks. `honcho` captures messages as the primary event stream, then derives observations. `verel` routes captured percepts through a trust gate.

The important split is whether the captured item is itself memory or evidence for memory. Honcho, Verel, MemPalace, Graphiti, Hindsight, Basic Memory, Mastra, Swafra, and RainBox are evidence-aware in different ways: Graphiti keeps episodes behind edges, Hindsight links observations to source facts, Basic Memory keeps canonical notes behind projections, and Mastra records exact message ranges behind summaries. These designs still differ sharply in trust: provenance supports correction, but only Verel and RainBox model rejection/promotion explicitly.

### Extraction

`mem0` has the clearest open implementation of LLM extraction: retrieve nearby existing memories, ask the model for additive facts, parse JSON, dedupe, embed, insert, and link entities.

`langmem` delegates extraction to Trustcall and schemas. This is elegant if the application already knows what shape memory should have.

`honcho` formats timestamped session messages and derives representations/observations asynchronously.

`verel` extracts candidate memories but restricts promotion. It is deliberately suspicious of raw extracted claims.

`supermemory` exposes document/chunk/memory schemas, but the extraction engine behind hosted endpoints is not present in this checkout.

`mempalace` mostly avoids extraction for primary memory. It may build closets, entities, halls, and KG triples, but the authoritative memory remains verbatim drawer text.

`swafra` also avoids LLM extraction. Regexes annotate entities, date strings, and preference phrases; conversations get a synthetic facts chunk that acts as a retrieval index while exchange text remains stored. Its Leiden partition uses embedding similarity plus positional weight, despite docs also claiming entity-weighted partitioning.

`rainbox` does not center on automatic extraction in the inspected paths. Explicit user commands and assistant actions create/update claims; evidence rows record whether a claim was user-confirmed, model-inferred, imported, or observed.

`llm-wiki-memory` automatically distills coding transcripts into schema-constrained atoms with chunked map/reduce, stores them in dated daily leaves, then compiles them into durable knowledge or lessons. Compile retrieves same-type/facet candidates and asks an LLM for create/update/skip, except same-error-pattern lessons are force-updated deterministically. This path is recoverable and well tested, but promoted atoms become active without a verification gate.

`hindsight` extracts world/experience facts, entities, temporal spans, and causal links from durable source material. `graphiti` extracts entities and typed relationships from an episode, then resolves them against existing graph identity. `memos` ranges from simple key/value/tag extraction to tree-memory readers. `basic-memory` usually avoids LLM extraction: observations and relations are explicit Markdown syntax. `mastra-observational-memory` extracts chronological summaries rather than atomic facts.

### Consolidation

`honcho`, `hindsight`, `mastra-observational-memory`, and `verel` have the strongest visible consolidation stories. Honcho derives working representations from event streams. Hindsight creates/updates observations with source IDs and proof counts. Mastra reflects growing observation logs and can prepare the result asynchronously before activation. Verel clusters failures, induces candidate design rules and schemas, then requires promotion gates for verification.

`mem0` V3 is intentionally more append-oriented; consolidation is mostly dedupe and entity linking in the OSS path. `mempalace` consolidates operationally through dedup, closets, halls, tunnels, graph layers, and repair paths rather than by rewriting memories into summaries. `swafra` has no real consolidation worker or correction policy: ingestion adds cross-source edges, and a `superseded_by` loop exists, but old same-source chunks are removed before that loop can see them. `llm-wiki-memory` has a substantial opt-in, brain-only pipeline: per-leaf similarity clusters, hash/lesson-key/cosine dedup, optional LLM merge, deterministic staleness flags, optional LLM refresh, orphan archive, archived-body compression, cache pruning, and index rebuild. `rainbox` consolidates through claim supersession, rejection, expiry, profile selection, and eval/feedback loops rather than through background summarization. `letta` separates core and archival memory but does not make consolidation the central visible mechanism in the inspected files. `langmem` provides reflection hooks rather than a fixed consolidation policy. `engram` keeps a pragmatic local model: update topic keys, count duplicates, surface conflicts.

### Retrieval

The repeated successful pattern is hybrid retrieval:

- semantic/vector search where embeddings exist;
- lexical/BM25/FTS for exact terms and identifiers;
- metadata filters for scope;
- reranking or rank fusion when quality matters.

`mem0` combines semantic, keyword, entity boost, and optional rerank. `hindsight` runs semantic, BM25, graph, and temporal arms, then uses task-specific fusion and cross-encoder reranking. `graphiti` searches edges, nodes, episodes, and communities with BM25, cosine, and BFS plus configurable RRF/MMR/cross-encoder recipes. `basic-memory` fuses FTS5/tsvector with optional semantic chunks. `memos` can run vector or graph/BM25/reranker/reasoner pipelines depending on the mounted cube. `honcho` blends semantic, recent, and most-derived observations. `engram` uses FTS5 and topic keys. `mempalace` combines direct drawer vector search, BM25, metadata, closet boosts, neighbor expansion, and fallback paths. `swafra` uses compact but uncalibrated hybrid/graph fusion. `llm-wiki-memory` combines frontmatter prefilters, embeddings or lexical hashes, priority, and locality. `rainbox` hard-filters then blends vector, full-text, and entity signals. `verel` adds trust and confidence into ranking. `mastra-observational-memory` is the deliberate exception: its primary path is sequential observations plus a recent raw tail, with semantic observation retrieval optional.

### Context Injection

`letta` and `mastra-observational-memory` have the deepest runtime prompt integration. Mastra removes observed raw messages, injects active observations as system context, retains a recent tail, and adds a continuation reminder. `rainbox` injects an operator profile block and hybrid memory context and records what was injected. `verel` has the safest visible recall renderer: recalled memory is token-budgeted and fenced as untrusted data. `mempalace` has a four-layer stack. `basic-memory` builds graph context through MCP while leaving final prompt placement to the client. `graphiti`, `hindsight`, and `memos` return structured recall/context to integrations. `swafra` exposes unbounded `get_context`; `llm-wiki-memory` injects session work context; `supermemory` emits profile text; `engram` has MCP context tools; `honcho` exposes working representations.

### Correction

This is where systems diverge sharply.

`verel` and `rainbox` have the strongest visible epistemic correction semantics in this set. `verel` has explicit trust states and rejected tombstones. `rainbox` has governed atomic correction, conflict detection, and tombstones that prevent model-write laundering. `engram` has conflict candidates and judgment tools. `mempalace`, `llm-wiki-memory`, `letta`, `mem0`, `honcho`, `supermemory`, and `langmem` expose increasingly operational forms of update/supersession without the same trust model.

Graphiti closes a fact's validity interval and retains history, which is the strongest temporal correction model here, but it does not mark claims verified/rejected. Hindsight rewrites or merges observations while retaining source/history fields. Basic Memory makes correction a human-readable file edit followed by transactional reindexing. Mastra replaces only the observation range covered by a reflection. MemOS correction varies by module and therefore lacks one consistent semantic contract.

### Forgetting

Visible deletion varies from hard API deletion to lifecycle state:

- `mem0`: delete APIs and expiration metadata.
- `langmem`: delete tool operation.
- `honcho`: soft-delete style document handling.
- `engram`: deleted timestamps/sync mutation semantics.
- `mempalace`: delete drawer, delete by source, dedup, repair, backend delete; deletion must account for drawers, closets, KG, backups, sync, and remote backends.
- `swafra`: exact source deletion from chunks/sources and source-owned edges; global cross-session edges survive and become dangling records.
- `llm-wiki-memory`: exact archive/re-enable and hard working-tree delete; embedding/index cleanup follows, but private git history can retain deleted or truncated content.
- `rainbox`: reject claim (tombstones the value in `MemoryRejectedValue`), supersede claim (also tombstones), expire claim, prune embeddings; rejected/superseded evidence remains inspectable; tombstoned values block future model re-assertion (anti-laundering).
- `letta`: block/file/passage update paths, archival insert/search visible; deletion depends on manager APIs outside the key path.
- `supermemory`: forget API in MCP/client; semantic fallback delete is powerful but risky.
- `verel`: rejected tombstones, TTL/volatile/stale pruning, and protection for verified/rejected/pinned records.
- `hindsight`: bank/document/memory operations plus cascading schema relations; derived observations must remain consistent with source changes.
- `graphiti`: episode removal and edge invalidation preserve temporal history and source support.
- `mastra-observational-memory`: clear/clone observational records and covered-range replacement.
- `memos`: module-specific hard/soft deletion across graph, vector, cache, dump, and model artifacts.
- `basic-memory`: canonical note deletion followed by entity, graph, full-text, semantic, and materialization cleanup.

Semantic forgetting is an antipattern unless there is explicit user review or exact ID targeting.

### Cross-Session and Cross-Agent Persistence

`honcho` has the richest multi-actor model: workspace, peer, session, collections, and derived representations. Hindsight isolates memory banks and database schemas. Graphiti uses `group_id`. Mastra scopes observations to a thread or resource. MemOS registers cubes to users. Basic Memory uses project/workspace/tenant boundaries with per-project local/cloud routing. `supermemory`, `mem0`, `rainbox`, `engram`, `mempalace`, `llm-wiki-memory`, `verel`, `letta`, and `langmem` each expose explicit boundaries. `swafra` remains the outlier with one global local corpus.

## 4. Implementation Hotspots by Repo

### Memory Schema

- `mem0`: `mem0/mem0/configs/base.py`, payload construction in `mem0/mem0/memory/main.py`.
- `langmem`: store item shape is application-defined; see `langmem/src/langmem/knowledge/tools.py` and schema extraction in `langmem/src/langmem/knowledge/extraction.py`.
- `honcho`: `honcho/src/models.py`.
- `engram`: SQLite schema in `engram/internal/store/store.go`.
- `mempalace`: drawer metadata in `mempalace/mempalace/miner.py` and `mcp_server.py`; backend contract in `mempalace/mempalace/backends/base.py`; KG schema in `mempalace/mempalace/knowledge_graph.py`.
- `swafra`: implicit source/chunk/edge dictionaries and JSON files in `swafra/swafra/engine.py`.
- `llm-wiki-memory`: leaf and metadata types in `llm-wiki-memory/scripts/lib/types-metadata.mjs`; rendering in `wiki-render.mjs`; layout contracts in `examples/layouts/*/layout.yaml`.
- `rainbox`: `MemoryClaim`, `MemoryEvidence`, `MemoryEmbedding`, `RetrievalEvent` in `rainbox/source/db/models.py`.
- `letta`: `letta/letta/schemas/memory.py`, `letta/letta/orm/block.py`, `letta/letta/orm/passage.py`.
- `supermemory`: `supermemory/packages/validation/schemas.ts`, `supermemory/packages/validation/api.ts`.
- `verel`: `verel/src/verel/memory/view.py`.
- `hindsight`: `hindsight-api-slim/hindsight_api/engine/memory_engine.py` and Alembic `memory_units`/document/link migrations.
- `graphiti`: `graphiti_core/nodes.py` and `graphiti_core/edges.py`.
- `mastra-observational-memory`: core `ObservationalMemoryRecord` plus `packages/memory/src/processors/observational-memory/types.ts`.
- `memos`: `src/memos/memories/textual/item.py`, activation/parametric item modules, and `mem_cube/general.py`.
- `basic-memory`: `src/basic_memory/models/knowledge.py` and `markdown/schemas.py`.

### Add/Write Path

- `mem0`: `Memory.add()` and `_add_to_vector_store()` in `mem0/mem0/memory/main.py`.
- `langmem`: `create_manage_memory_tool()` in `langmem/src/langmem/knowledge/tools.py`; extraction in `MemoryManager`.
- `honcho`: `honcho/src/crud/message.py`, `honcho/src/deriver/deriver.py`, `honcho/src/crud/representation.py`.
- `engram`: `AddObservation()` in `engram/internal/store/store.go`; MCP `handleSave()` in `engram/internal/mcp/mcp.go`.
- `mempalace`: `process_file()` and `mine()` in `mempalace/mempalace/miner.py`; `tool_add_drawer()` in `mempalace/mempalace/mcp_server.py`; collection access in `mempalace/mempalace/palace.py`.
- `swafra`: `add_knowledge()`, `leiden_chunk()`, and `chunk_conversation()` in `swafra/swafra/engine.py`.
- `llm-wiki-memory`: MCP dispatch in `llm-wiki-memory/mcp-server/mcp-write-dispatch.mjs`; `writeMemory()` / `saveDocument()` in `scripts/lib/wiki-mutate.mjs`; transcript capture in `scripts/hooks/flush-worker.mjs`; promotion in `scripts/compile-promote.mjs`.
- `rainbox`: explicit commands in `rainbox/source/memory/ops.py`; assistant actions in `rainbox/source/agents/assistant.py`; review UI actions in `rainbox/source/webapp/memory_api.py`; DB helpers in `rainbox/source/db/memory.py`.
- `letta`: `letta/letta/services/tool_executor/core_tool_executor.py`; `letta/letta/services/block_manager.py`; `letta/letta/services/passage_manager.py`.
- `supermemory`: `supermemory/packages/ai-sdk/src/tools.ts`, `supermemory/apps/mcp/src/server.ts`, `supermemory/apps/mcp/src/client.ts`.
- `verel`: `verel/src/verel/memory/local.py`, `verel/src/verel/memory/remember.py`.
- `hindsight`: `MemoryEngine.retain_async()` and `engine/retain/orchestrator.py`.
- `graphiti`: `Graphiti.add_episode()` and `utils/maintenance/node_operations.py` / `edge_operations.py`.
- `mastra-observational-memory`: `ObservationalMemoryProcessor` plus observation strategies and observer/reflector runners.
- `memos`: `MOSCore`, `GeneralMemCube`, `GeneralTextMemory.add()`, and `TreeTextMemory.add()`.
- `basic-memory`: MCP `write_note` through typed client/API to accepted-note services and indexing workflows.

### Search/Retrieve Path

- `mem0`: `Memory.search()` and `_search_vector_store()`; scoring in `mem0/mem0/utils/scoring.py`.
- `langmem`: `create_search_memory_tool()` delegates to `BaseStore.search/asearch`.
- `honcho`: `honcho/src/crud/representation.py`, `honcho/src/crud/document.py`, `honcho/src/dialectic/`.
- `engram`: `Search()` and context helpers in `engram/internal/store/store.go`; MCP search/context handlers.
- `mempalace`: `search_memories()`, `_hybrid_rank()`, `_bm25_only_via_sqlite()` in `mempalace/mempalace/searcher.py`.
- `swafra`: `BM25Index`, `search_knowledge()`, and `graph_walk()` in `swafra/swafra/engine.py`.
- `llm-wiki-memory`: `searchOneTree()` in `llm-wiki-memory/scripts/lib/wiki-search.mjs`; federated merge in `wiki-search-fanout.mjs`; `searchMemory()` and `recallLessons()` in `recall-search.mjs` / `recall.mjs`.
- `rainbox`: `retrieve_memories_hybrid()`, `hard_filtered_claims()`, `build_chat_memory_block()` in `rainbox/source/memory/retrieval.py`; profile retrieval in `rainbox/source/user_profile/retrieval.py`.
- `letta`: `archival_memory_search()`, `conversation_search()`, `message_manager.search_messages_async`.
- `supermemory`: `client.search.execute`, `client.search.memories`, `/v4/profile` context helper.
- `verel`: `recall()` in `local.py`, `recall_budgeted()` in `recall.py`, rank logic in `view.py`.
- `hindsight`: `engine/search/retrieval.py`, `fusion.py`, `link_expansion_retrieval.py`, and `reranking.py`.
- `graphiti`: `graphiti_core/search/search.py` and `search_config_recipes.py`.
- `mastra-observational-memory`: `Memory.getContext()`, observation-context builders, and optional observation indexing in `packages/memory/src/index.ts`.
- `memos`: `TreeTextMemory.search()`, `memories/textual/searcher/`, and `get_relevant_subgraph()`.
- `basic-memory`: `services/search_service.py` and backend repositories inheriting `search_repository_base.py`.

### Context Assembly

- `mem0`: mostly application-owned after search.
- `langmem`: application-owned; tools return store/search results.
- `honcho`: working representation in `honcho/src/crud/representation.py`.
- `engram`: MCP context/session summary in `engram/internal/mcp/mcp.go`.
- `mempalace`: four-layer stack in `mempalace/mempalace/layers.py`; MCP search/status/list tools in `mempalace/mempalace/mcp_server.py`.
- `swafra`: `get_context()` source-diverse search/walk composition in `swafra/swafra/engine.py`.
- `llm-wiki-memory`: bounded MCP responses in `llm-wiki-memory/mcp-server/tools-search.mjs` and `scripts/lib/search-clamp.mjs`; automatic session context in `scripts/hooks/session-start.mjs` and `scripts/lib/work-context.mjs`.
- `rainbox`: `rainbox/source/agents/chat_context.py`, `rainbox/source/memory/retrieval.py`, `rainbox/source/user_profile/retrieval.py`.
- `letta`: `Memory.compile()` in `letta/letta/schemas/memory.py`.
- `supermemory`: `supermemory/packages/tools/src/shared/context.ts`.
- `verel`: `verel/src/verel/memory/recall.py`.
- `hindsight`: `MemoryEngine.recall_async()` and `reflect_async()` with `engine/search/think_utils.py`.
- `graphiti`: application-owned assembly from structured `SearchResults`.
- `mastra-observational-memory`: `Memory.getContext()` and `processor.ts` system-message injection.
- `memos`: `MOS.chat()` and context helpers in `mem_chat/`.
- `basic-memory`: `mcp/tools/build_context.py` and graph/context response schemas.

### Background Workers

- `mem0`: no central open worker in the inspected OSS core; extraction happens in write path.
- `langmem`: `langmem/src/langmem/reflection.py`.
- `honcho`: `honcho/src/deriver/`, `honcho/src/reconciler/`, queue models.
- `engram`: sync queue in `engram/internal/sync/` and store mutation queue fields.
- `mempalace`: mining/convo/format miners, hallway/tunnel computation, daemon jobs, repair/sync/backups.
- `swafra`: none; chunking, embedding, graph construction, and JSON rewrites happen synchronously in `add_knowledge()`.
- `llm-wiki-memory`: detached capture in `llm-wiki-memory/scripts/hooks/flush-worker.mjs`; compile in `scripts/compile*.mjs`; consolidation in `scripts/consolidate*.mjs`; self-healing scheduler in `scripts/cron*.mjs`.
- `rainbox`: embedding sync/prune in `rainbox/source/memory/embeddings.py`; feedback/eval loop in `rainbox/source/db/feedback.py` and `rainbox/source/evals/`.
- `letta`: manager services and prompt rebuilds; not primarily worker-centric in inspected paths.
- `supermemory`: hosted processing not visible; graph UI and MCP/client visible.
- `verel`: consolidation, promotion, replication modules.
- `hindsight`: queued consolidation and maintenance workers with per-bank retries.
- `graphiti`: ingestion maintenance and optional saga summarization; no separate mandatory queue.
- `mastra-observational-memory`: early async observation/reflection buffers plus idle/provider-change activation.
- `memos`: `mem_scheduler/` and periodic activation-memory refresh.
- `basic-memory`: file watcher, startup reconciliation, and portable indexing workflows.

### MCP/API/SDK Surfaces

- `mem0`: Python SDK and service/API paths.
- `langmem`: LangChain/LangGraph tools.
- `honcho`: service endpoints and SDK-facing models.
- `engram`: `engram/internal/mcp/mcp.go`.
- `mempalace`: `mempalace/mempalace/mcp_server.py`, CLI modules, hooks under `mempalace/hooks/`, skills/commands.
- `swafra`: Python FastMCP in `swafra/swafra/server.py`; Node MCP in `swafra/src/index.ts`; subprocess bridge in `swafra/src/engine.ts`.
- `llm-wiki-memory`: `llm-wiki-memory/mcp-server/index.mjs` and `tools-*.mjs`; `scripts/cli.mjs`; Claude Code hooks under `scripts/hooks/`; canonical agent policy in `templates/agents-memory-instructions.md`.
- `rainbox`: web API/UI in `rainbox/source/webapp/memory_api.py` and `memory_views.py`; assistant capabilities in `rainbox/source/agents/assistant.py`.
- `letta`: tool definitions in `letta/letta/functions/function_sets/base.py`, runtime in core tool executor.
- `supermemory`: `supermemory/apps/mcp/src/server.ts`, `supermemory/packages/ai-sdk/src/tools.ts`.
- `verel`: `verel/src/verel/mcp_server.py`, hosted/replicated adapters.
- `hindsight`: FastAPI REST, MCP, generated SDK clients, CLI, and framework integrations.
- `graphiti`: Python library, `mcp_server/`, and `server/`.
- `mastra-observational-memory`: Mastra `Memory`, agent processors, and direct context APIs.
- `memos`: MOS runtime/chat, API, and CLI layers.
- `basic-memory`: MCP tools, typed API clients, FastAPI, CLI, and per-project local/cloud routing.

### Evals/Tests

- `mem0`: tests are present but the report focused on core implementation.
- `langmem`: tests/examples around tools and extraction should be consulted before reuse.
- `honcho`: rich tests under `honcho/tests`.
- `engram`: Go package tests and MCP flows should be inspected for command behavior.
- `mempalace`: broad tests under `mempalace/tests`; benchmarks under `mempalace/benchmarks`.
- `swafra`: no unit/integration tests; LongMemEval harness and artifacts under `swafra/bench` and `swafra/packages/mcp/bench`, with a result-count validity problem.
- `llm-wiki-memory`: broad unit tests under `llm-wiki-memory/test`; lifecycle and federation coverage under `test/e2e`; latency evidence in `PERFORMANCE.md`; no retrieval-relevance benchmark.
- `rainbox`: memory/retrieval/assistant/UI tests under `rainbox/source/memory`, `rainbox/source/db`, `rainbox/source/agents`, and `rainbox/source/webapp`.
- `letta`: `letta/tests/test_memory.py`, manager tests, passage/message/block tests.
- `supermemory`: visible integration/e2e wrappers and memory graph tests; backend tests not present.
- `verel`: strong memory-focused tests under `verel/tests/test_memory*.py`, plus consolidation, promotion, lattice, replicated, hosted, MCP tests.
- `hindsight`: broad retain/recall/reflect, temporal, consolidation, migration, defense, audit, and benchmark coverage.
- `graphiti`: graph-backend, extraction, dedupe, temporal invalidation, search recipe, saga, and removal tests.
- `mastra-observational-memory`: dense threshold, buffering, marker, retry, resource-scope, and storage integration tests.
- `memos`: unit/integration/benchmark coverage varies by configured cube and backend.
- `basic-memory`: SQLite/PostgreSQL unit/integration coverage plus a provenance-rich standalone benchmark harness.

## 5. Design Patterns That Recur

These recurring moves are also documented as standalone implementation guides in the [memory design pattern library](../patterns/). The library covers correction, provenance, trust, retrieval, scope, write governance, federation, context assembly, recoverable background work, and audit history.

### Tool-mediated memory writes

Repos: all sixteen, in different forms.

The agent or application explicitly calls a memory operation. This works because it gives the system a narrow interface for durable state changes. It fails when the model forgets to call the tool, calls it with low-quality facts, or treats tool descriptions as policy enforcement.

### Separate hot memory from archival memory

Repos: `letta`, `rainbox`, `honcho`, `supermemory`, `mempalace`, `llm-wiki-memory`, `hindsight`, `mastra-observational-memory`, `memos`, partly `mem0`.

Hot memory is small and prompt-ready. Archival/document memory is large and retrieved on demand. This works because prompt space is scarce and long-term stores are noisy. It fails when there is no promotion/demotion policy between the layers.

### Evidence first, derived memory second

Pattern guide: [Evidence before belief](../patterns/evidence-before-belief/).

Repos: strongest in `honcho`, `verel`, `mempalace`, `rainbox`, `graphiti`, `hindsight`, and `basic-memory`; partly in `engram`, `swafra`, `llm-wiki-memory`, and `mastra-observational-memory`.

Raw messages, observations, files, drawers, or evidence rows are retained, and derived facts/representations/indexes are computed from them. This works because wrong memories can be audited and recomputed. It fails if the derived layer does not preserve source IDs, if raw stores become too noisy, if evidence excerpts are too thin, or if background derivation makes read consistency surprising.

### Hybrid retrieval

Pattern guide: [Hybrid retrieval fusion](../patterns/hybrid-retrieval-fusion/).

Repos: `mem0`, `honcho`, `engram`, `mempalace`, `swafra`, `rainbox`, `verel`, `hindsight`, `graphiti`, `basic-memory`, `memos`, `supermemory` API settings, `letta` across separate search modes.

Vector search alone is not enough. Identifiers, names, exact phrases, dates, file paths, and project keys often need lexical search. Hybrid retrieval works because it handles both fuzzy semantic recall and exact lookup. MemPalace adds a useful variant: extracted/indexed "closets" boost drawer ranking but never gate direct evidence retrieval. Swafra is a useful compact example of BM25 + vector + cheap heuristic fusion, but also a warning: ad hoc component normalization and unbounded bonuses make scores hard to interpret. Hybrid retrieval fails when rank fusion is opaque or not evaluated.

### Scope as a first-class key

Pattern guide: [Scope as a first-class key](../patterns/scope-as-a-first-class-key/).

Repos: all except `swafra`.

Good systems make memory boundaries explicit: user, agent, run, project, workspace, peer, session, space, palace, wing, room, source file, claim scope, sensitivity, scope lattice, namespace. This works because many memory bugs are scope bugs. Swafra's one global corpus shows why a source title is not a scope: two clients or projects can silently retrieve each other's memory. Scope fails when absent or when it is only metadata with no migration, inheritance, access, or conflict policy.

### MCP as a universal adapter

Repos: `engram`, `mempalace`, `swafra`, `llm-wiki-memory`, `supermemory`, `verel`, `hindsight`, `graphiti`, `basic-memory`, and conceptually similar tool surfaces elsewhere.

MCP is useful because it lets different coding agents and desktop tools use the same memory backend. It fails if the MCP tool descriptions become the only guardrail against bad writes.

### Local SQLite for inspectable memory

Repos: `engram`, `mempalace`, `verel`, `basic-memory`; SQLite also supports history/messages in `mem0`.

SQLite works well for local agent memory: durable, fast, easy to inspect, transaction-friendly, and good enough with FTS5. MemPalace also shows the complementary local pattern: SQLite metadata/KG/FTS plus a local vector store. It fails if a product needs multi-tenant scale, remote sharing, or vector-heavy retrieval without extensions/adapters.

### Flat JSON as a prototype store

Repo: `swafra`.

Three JSON files make the complete state inspectable and keep installation trivial. This is reasonable for a single-process prototype and terrible as implicit production durability: full-file rewrites, no transactions or locks, no indexed access, and cross-file consistency hazards. Treat flat JSON as a demo format or export, not a concurrent memory database.

### Filesystem wiki plus git history

Repo: `llm-wiki-memory`.

Markdown leaves plus generated folder indexes make local memory directly readable, diffable, and recoverable. Git commits can group one logical mutation into an auditable change, while repository-owned mounts provide a simple team-sharing path. This works for small coding-agent corpora where inspectability matters more than query throughput. It fails at large scale, under concurrent collaborative writes, or when deletion must erase prior content rather than leave it in history.

### Recoverable background capture

Repo: `llm-wiki-memory`; related evidence-retention ideas appear in `honcho` and `mempalace`.

Decouple transcript capture from the interactive hook, chunk long inputs, retain failed chunks, write fenced raw fallbacks, and support redistillation. This turns provider failure into delayed processing instead of silent data loss. It fails if the recovery stores themselves leak secrets or if no operator ever reviews/retries accumulated stashes.

### Profiles and working representations

Repos: `honcho`, `supermemory`, `letta`, `hindsight`, `mastra-observational-memory`.

A low-latency synthesized representation is often more useful than raw top-k memories. This works because agents need compact operating context. It fails when summaries drift, hide uncertainty, or cannot be traced back to evidence.

### Memory governance loop

Repos: strongest in `rainbox`; partly in `verel`.

Memory quality improves when memory use is observable and connected to review, feedback, and evals. RainBox's `RetrievalEvent`, `FeedbackEvent`, `/memory` review page, and eval loop show a practical product pattern. This fails if telemetry is mistaken for truth: a downvote is a review signal, not proof that a memory is false.

### Bi-temporal fact validity

Pattern guide: [Bi-temporal fact validity](../patterns/bi-temporal-fact-validity/).

Repos: strongest in `graphiti`; supporting temporal/event-time ideas in `hindsight`.

Record both when a fact was valid in the represented world and when the system learned or expired it. This preserves historical truth during correction and backfill. It fails when LLM-extracted dates or invalidation decisions are treated as certain.

### Buffered observation-reflection

Repos: strongest in `mastra-observational-memory`; related consolidation in `hindsight` and `honcho`.

Prepare derived context before the hard prompt threshold, persist the exact source range it covers, and activate it atomically when needed. This removes LLM compression from the critical path. It fails without durable markers, range-aware replacement, recovery, and distributed coordination.

## 6. Antipatterns and Failure Modes

### Treating LLM-extracted facts as truth

Most systems extract with an LLM. Without trust state, provenance, and correction semantics, hallucinations become durable. `verel` addresses this directly; `honcho` preserves source events; `mem0`, `langmem`, and `llm-wiki-memory` need stronger promotion guardrails.

`mempalace` is the clearest counterexample in this workspace: it makes verbatim evidence the primary store and treats derived structures as indexes. That does not solve truth, but it avoids losing the original context during extraction.

### Vector-only memory

Vector search misses exact constraints and can retrieve plausible but wrong memories. Every serious design should include lexical search or structured filters. `engram` demonstrates the value of boring FTS. `mempalace` demonstrates vector plus BM25 plus metadata plus fallback paths. `mem0` and `honcho` show hybrid approaches. `llm-wiki-memory` has strong metadata filters and deterministic topology lookup, but its lexical-hash mode is a fallback backend rather than a fused exact-search channel.

### Recall@k without enforcing k

A retrieval benchmark is invalid at a stated cutoff if the system scores more than `k` returned items. Swafra's committed `k=10` artifact evaluated all returned sessions while returning 28–46 sessions per question (35.4 on average); it only truncated the displayed `retrieved_sessions` list. Benchmark harnesses should assert the result count, score exactly the first `k`, record token volume, and bind artifacts to a code/config/embedder manifest.

### Weak correction semantics

Pattern guide: [Rejected-value tombstone](../patterns/rejected-value-tombstone/).

Update/delete APIs are not enough. A system needs to model contradiction, supersession, source, timestamp, and rejected values. Otherwise a wrong fact can be reintroduced by later extraction. Verel's rejected tombstones are the clearest research-grade countermeasure; RainBox has adopted equivalent machinery in a product context: `MemoryRejectedValue` tombstones block future model re-assertion of rejected or superseded values, `correct_belief` is an atomic governed correction path, and write-time conflict detection is lattice-aware across the scope hierarchy. `llm-wiki-memory` shows the limit of operational supersession without epistemic state: it can archive a selected predecessor, but cannot prevent the rejected value from being distilled again.

### Semantic deletion

Deleting by "similar memory" is dangerous. It is useful as a discovery aid, but the actual forget operation should target exact IDs or require review. Supermemory's MCP client fallback semantic deletion is a risk pattern to treat carefully.

### Treating git deletion as privacy deletion

`llm-wiki-memory` removes exact leaves and embedding entries, but private wiki commits retain prior bodies. Git history is excellent for recovery and audit, but it is not an erasure guarantee. Any git-backed memory needs an explicit procedure for history rewriting, clones, backups, stashes, and derived caches.

### Core memory as a junk drawer

Editable prompt memory is powerful and dangerous. Letta's core memory tools are useful, but any system with long-lived core blocks needs provenance, review, and compaction policy. Otherwise it accumulates stale identity and preference claims.

### Tool descriptions as policy

Several systems rely on tool docs telling the agent when to save memory. This is necessary but insufficient. The backend still needs dedupe, conflict detection, trust gates, and review.

### Telemetry mistaken for truth

RainBox explicitly avoids this: retrieval events and downvotes are signals for inspection/evals, not automatic confidence changes or deletion. This matters because "memory was used in a bad answer" does not prove the memory was false.

### Platform-only claims hidden behind OSS APIs

Mem0 and Supermemory both have product surfaces where advanced behavior may live outside the inspected source. For build decisions, separate what is visible in code from what is promised by hosted APIs.

### Throwing away raw evidence too early

Extraction-first systems can look elegant while deleting the only material needed to debug a wrong memory. MemPalace is the strongest evidence that raw text plus retrieval deserves to be the baseline before adding lossy summarization or fact extraction.

### Treating local JSON rewrites as durable storage

Swafra loads and rewrites chunks, edges, and sources as three independent JSON files. Without locks, atomic replace, transactions, repair, or cascading deletion, concurrent agents can lose writes and partial failure can split graph state. Human-readable export is valuable; it is not a substitute for transactional primary storage.

## 7. What Seems to Work

SQLite plus FTS works for local coding-agent memory. It gives inspectable state, transactional writes, simple backup/sync, and exact search. Engram and Verel are good references. MemPalace shows how to combine local SQLite-style operational machinery with a vector backend and fallback BM25/FTS paths.

Hybrid retrieval is the default serious choice. Pair semantic search with lexical matching and metadata filters. Add reranking only after basic retrieval metrics exist. MemPalace's "closets boost but never gate drawers" rule is a particularly reusable retrieval principle.

Source diversity is useful when the context should cover sessions or documents rather than repeat adjacent chunks from one source. Swafra makes this explicit with best-chunk-per-source selection. The production version needs a hard result/token cap, stable source identity, and an escape hatch for questions requiring multiple chunks from one source.

Scope must be part of the primary design, not a later filter. User/agent/project/session/workspace boundaries determine whether recall is useful or harmful.

Make write destinations explicit in layered memory. `llm-wiki-memory` lets reads fan out across private and repository scopes while requiring every mutation to name a concrete target. This prevents a shared scope from silently becoming a shared write.

Keep raw evidence. Messages, source IDs, documents, drawers, and provenance make correction possible. Honcho, Verel, and MemPalace benefit from this; systems that only store extracted facts lose auditability.

Separate truth from usefulness. Retrieval strength should not mean the memory is true. Verel's split between `epistemic_confidence` and `retrieval_strength` is one of the strongest ideas in the workspace.

Render recalled memory defensively. Verel's untrusted-memory fence is a practical prompt-injection mitigation. Context should be quoted as data, not instructions.

Use small, explicit mutation APIs. Letta's append/replace/patch operations are easier to reason about than free-form "update my memory" text.

Record embedder identity. MemPalace's explicit model/dimension checks are a useful operational guardrail: a vector index searched with the wrong embedding model can silently degrade.

Make automatic capture recoverable. `llm-wiki-memory` preserves failed chunk inputs, raw fenced fallbacks, retry state, and provider provenance, which is a stronger failure posture than treating a failed summarization call as a lost session.

Make memory use inspectable. RainBox's debug rows, retrieval events, and review UI are the best reference here. Users need to know which memories entered a prompt and need a way to correct or reject them.

Separate event time from ingestion time when facts change. Graphiti's bi-temporal edges preserve historical truth and backfilled events without destructive overwrite.

Prepare compaction before the context cliff. Mastra Observational Memory's inactive buffers and exact coverage ranges make expensive observation/reflection recoverable and mostly non-blocking.

Keep human-owned source canonical when that is the product promise. Basic Memory's Markdown/projection boundary makes memory portable and repairable, provided every derived index has a reconciliation path.

Name the physical memory form. MemOS usefully expands memory beyond text, but KV cache, graph text, and LoRA memory need different compatibility, deletion, and evaluation guarantees.

## 8. What I Would Build

### Ship First

Build a local-first core even if a hosted version is planned later.

Data model:

- `event`: raw messages, tool calls, documents, user assertions, timestamps, actor IDs.
- `evidence_chunk`: verbatim text chunk with source path/session, line/span, authored/filed time, deterministic ID, embedding ID, and scope.
- `memory`: extracted or manually saved claim with `kind`, `subject`, `predicate`, `text`, `scope`, `status`, `confidence`, `retrieval_strength`, `source_event_ids`, `created_at`, `updated_at`.
- `memory_evidence`: append-only provenance rows, not a mutable field on `memory`.
- `memory_relation`: `supersedes`, `contradicts`, `supports`, `derived_from`, `same_as`.
- `rejected_value`: tombstone for values that should not be silently reintroduced.
- `embedding`: optional vector table or external vector ID.
- `retrieval_event`: append-only events for retrieved, used/injected, rejected, downvoted, considered.

Status should start simple:

- `candidate`
- `verified`
- `rejected`
- `stale`

Write path:

1. Store raw evidence first.
2. Chunk deterministically and record embedder identity.
3. Index raw evidence with lexical and vector paths.
4. Extract candidate facts with schema-constrained LLM output only after evidence is durable.
5. Search for same subject/predicate and near duplicates.
6. If same key plus same value, corroborate.
7. If same key plus different value, create a conflict or supersession.
8. Do not auto-promote to verified unless the source is trusted or corroborated.
9. Preserve failed extraction inputs and make background work safely retryable.

Retrieval path:

1. Apply hard scope filters.
2. Run lexical search and vector search.
3. Retrieve raw evidence directly as the floor.
4. Let derived indexes/summaries/entities boost rank, not gate evidence.
5. Blend with recency, confidence, retrieval strength, and trust status.
6. Suppress rejected records from normal recall but use rejected tombstones during write conflict checks.
7. Return compact, source-linked results.

Context assembly:

- Token-budgeted.
- Verified first, then high-confidence candidates if needed.
- Group by subject or task.
- Fence as recalled data, not instructions.
- Include source or confidence markers when possible.
- Record which memories entered context.

Agent integration:

- MCP tools for `remember`, `recall`, `judge`, `forget`, and `context`.
- SDK methods with the same semantics.
- Tool calls should be small and boring; policy belongs in the backend.
- Review UI or API for activate/reject/correct/sensitivity/expiry.
- Confirm-tier write intents for high-impact assistant-proposed memory changes.
- Let reads span allowed scopes, but require an explicit destination for every write.

Testing:

- Extraction golden tests.
- Conflict/supersession tests.
- Retrieval recall/precision fixtures.
- Hard assertions that a benchmark labeled `@k` scores exactly the first `k` results and records token volume.
- Prompt-injection tests for recalled content.
- Deletion/privacy tests.
- Scope leakage tests.
- Telemetry and feedback-to-eval tests.
- Regression corpus of wrong memories that must not reappear.

### Add Later

- Background consolidation from failures into candidate rules.
- Promotion gates using held-out task suites.
- Entity graph linking with indexed, intentional edge direction and cascading deletion.
- Closet-style source indexes and neighbor expansion.
- Hosted multi-tenant API.
- Cross-device sync.
- UI for memory review and conflict resolution.
- Retrieval telemetry dashboards and feedback/eval promotion.
- Temporal reasoning and decay.

Do not add background summarization before raw-evidence retrieval and correction semantics exist. Summaries are compressed belief; if the system cannot explain and repair a belief, summarization hides the problem.

## 9. Repo-by-Repo Verdicts

### `mem0`

- Best idea: pragmatic additive extraction plus hybrid retrieval/entity boost.
- Biggest risk: extracted facts are not strongly modeled as uncertain claims.
- Most reusable component: `Memory.add()` / `_add_to_vector_store()` pipeline.
- Maturity impression: practical SDK core, with some advanced features outside OSS.
- Study when: building a drop-in memory library.
- Do not copy when: you need rigorous trust/correction semantics.

### `langmem`

- Best idea: memory as LangGraph store tools with schema-driven extraction.
- Biggest risk: it is a primitive layer, not a full memory policy.
- Most reusable component: `create_manage_memory_tool()` and namespace templates.
- Maturity impression: clean and framework-native.
- Study when: already building on LangGraph.
- Do not copy when: you need a standalone memory service with built-in quality controls.

### `honcho`

- Best idea: event stream to derived working representation.
- Biggest risk: operational complexity and background consistency.
- Most reusable component: message ingestion plus deriver/representation flow.
- Maturity impression: serious service architecture with meaningful tests.
- Study when: modeling users/peers/sessions over time.
- Do not copy when: all you need is a local memory file.

### `engram`

- Best idea: local SQLite/FTS MCP memory with conflict-oriented writes.
- Biggest risk: lexical retrieval and agent-mediated judgment may hit limits.
- Most reusable component: `AddObservation()` and MCP `handleSave()`.
- Maturity impression: compact, inspectable, purpose-built for coding agents.
- Study when: building local developer-agent memory.
- Do not copy when: you need hosted multi-tenant vector retrieval.

### `mempalace`

- Best idea: verbatim drawers as the authoritative memory, with hybrid retrieval and extracted indexes as boosts.
- Biggest risk: raw stores get large/noisy and do not resolve contradictions by themselves.
- Most reusable component: `search_memories()` plus `_hybrid_rank()`, and the mining/write path around deterministic IDs.
- Maturity impression: operationally mature local system with broad tests, integrations, repair tooling, and benchmark artifacts.
- Study when: building local-first coding-agent memory or testing whether extraction is actually needed.
- Do not copy when: you need compact verified user facts as the primary memory surface.

### `swafra`

- Best idea: compact source-diverse hybrid retrieval with explicit graph exploration and no required cloud model.
- Biggest risk: non-atomic global JSON state plus a benchmark that scores far more than the advertised `k`.
- Most reusable component: the conceptual `search_knowledge()` -> `graph_walk()` -> best-per-source composition, not the persistence implementation.
- Maturity impression: promising alpha prototype with significant code/docs/artifact drift and no ordinary tests.
- Study when: learning how little code a local MCP graph-RAG memory can require.
- Do not copy when: you need concurrency, trustworthy evals, scope isolation, correction, bounded prompts, or durable storage.

### `llm-wiki-memory`

- Best idea: recoverable hook capture plus explicit federated write targets over inspectable Markdown/git memory.
- Biggest risk: LLM-distilled atoms become active guidance without candidate/verified/rejected state or contradiction protection.
- Most reusable component: `wiki-mutate.mjs` / `wiki-search*.mjs` with the flush, compile, scope, and commit orchestration around them.
- Maturity impression: operationally mature local coding-agent system with unusually broad failure-path and federation tests; retrieval quality is not benchmarked.
- Study when: building cross-agent local project memory, lifecycle capture, deterministic wiki placement, or self-healing maintenance.
- Do not copy when: you need high-stakes truth governance, large-corpus query performance, multi-tenant access control, or privacy-grade deletion.

### `rainbox`

- Best idea: claim/evidence memory tied to governed writes (single `record_belief` path, five-actor trust model, tombstones, conflict detection), review UI, retrieval telemetry, feedback, and eval gates.
- Biggest risk: active compact claims can steer behavior while losing nuance from original source context; no automatic candidate extraction means claims enter only through explicit writes.
- Most reusable component: `MemoryClaim`/`MemoryEvidence`/`MemoryRejectedValue`/`RetrievalEvent` model, `record_belief`/`correct_belief` governed write paths, `retrieve_memories_hybrid()`.
- Maturity impression: strong app-integrated memory subsystem with trust/correction machinery comparable to Verel's correctness properties, broad tests, and operator workflows.
- Study when: building an assistant product where memory must be inspectable, governable, and protected against model-write laundering.
- Do not copy when: you need a small embeddable library, raw transcript recall as the primary memory layer, or `epistemic_confidence`/`retrieval_strength` driving ranking (these columns are schema groundwork only; Tier-1 ranking still uses `confidence`).

### `letta`

- Best idea: core vs archival vs conversation memory inside the runtime.
- Biggest risk: agent-editable core memory without a strong truth model.
- Most reusable component: memory block compile/mutation and patch-style edits.
- Maturity impression: deep runtime integration with compatibility complexity.
- Study when: building an agent platform, not just a memory backend.
- Do not copy when: you want a small independent memory service.

### `supermemory`

- Best idea: product-grade API shape around documents, chunks, memory entries, spaces, profiles, SDKs, and MCP.
- Biggest risk: the hosted backend core is not visible here.
- Most reusable component: schemas and adapter surfaces.
- Maturity impression: polished integration surface; implementation evidence incomplete.
- Study when: designing public APIs and memory UX.
- Do not copy when: you need open implementation details for extraction/ranking.

### `verel`

- Best idea: explicit trust, confidence, retrieval strength, rejected tombstones, and defensive recall.
- Biggest risk: complexity.
- Most reusable component: `MemoryRecord`, `LocalMemory.write()`, and `recall_budgeted()`.
- Maturity impression: research-grade correctness focus with strong targeted tests.
- Study when: wrong memory is costly.
- Do not copy wholesale when: you need a fast MVP.

### `hindsight`

- Best idea: four independent recall arms plus task-specific fusion over evidence-backed facts and observations.
- Biggest risk: LLM-extracted and consolidated claims can become durable without an explicit truth state.
- Most reusable component: retain pipeline and `engine/search/` fusion/reranking stack.
- Maturity impression: service-grade implementation with unusually strong operational coverage.
- Study when: building a hosted retain/recall/reflect service.
- Do not copy when: a small local store can meet the evaluated retrieval need.

### `graphiti`

- Best idea: bi-temporal relationship edges that close validity intervals without erasing history.
- Biggest risk: entity-resolution or invalidation mistakes reshape a large portion of the graph.
- Most reusable component: episode/evidence model plus temporal edge maintenance.
- Maturity impression: substantial graph library with multiple drivers and deep search configuration.
- Study when: facts, relationships, and their validity change over time.
- Do not copy when: memory is mostly independent notes or stable preferences.

### `mastra-observational-memory`

- Best idea: compute observation/reflection buffers early, persist exact coverage, and activate without blocking.
- Biggest risk: progressive summary drift and in-process-only locking.
- Most reusable component: marker/range-aware buffered activation.
- Maturity impression: deeply integrated and heavily tested framework feature.
- Study when: long agent conversations exceed model context.
- Do not copy when: exact evidence retrieval is the primary requirement.

### `memos`

- Best idea: mount textual, preference, skill, KV-cache, and parametric memory as one cube.
- Biggest risk: one abstraction hides uneven backend guarantees and maturity.
- Most reusable component: memory-cube packaging and textual-to-activation scheduling.
- Maturity impression: ambitious research/engineering substrate with many configurations.
- Study when: exploring model-native memory or deployable heterogeneous memory bundles.
- Do not copy when: a single audited text store is sufficient.

### `basic-memory`

- Best idea: canonical human-editable Markdown with graph/search state treated as rebuildable projection.
- Biggest risk: bidirectional file/database synchronization and direct agent writes to canonical knowledge.
- Most reusable component: accepted-note transaction/reconciliation boundary and typed MCP client flow.
- Maturity impression: operationally serious local/cloud knowledge system with broad parity tests.
- Study when: people and agents must share portable project knowledge.
- Do not copy when: humans never edit memory and filesystem ownership adds no value.

## 10. Practical Checklist for Your Own System

Schema and scoping:

- Define the memory unit before choosing vector storage.
- Store raw evidence separately from derived memory.
- Give raw evidence stable IDs and source/span metadata.
- Make scope mandatory: user, agent, project/session, and sharing boundary.
- Include provenance/source IDs on every derived memory.
- Store provenance/evidence as append-only rows when a claim can have multiple origins.
- Represent status/trust explicitly.

Write path:

- Store evidence first.
- Record embedder identity and index version.
- Extract structured candidates.
- Dedupe by exact hash and semantic similarity.
- Detect same subject/predicate conflicts.
- Preserve correction chains.
- Keep rejected tombstones.
- Use stale-write guards for review UI mutations.

Retrieval:

- Use lexical plus vector retrieval.
- Filter by scope before ranking.
- Let summaries/entities/indexes boost raw evidence, not hide it.
- Rank with relevance, recency, confidence, trust, and retrieval strength.
- Enforce both result-count and token budgets; never let `k` silently become a lower bound.
- Evaluate retrieval on realistic tasks.

Context assembly:

- Budget tokens.
- Prefer verified memories.
- Mark uncertainty.
- Fence recalled memory as data.
- Include enough source metadata for debugging.

Trust/provenance:

- Do not let model extraction imply truth.
- Separate "often retrieved" from "known true".
- Require attestation or corroboration for important claims.
- Track who said what and when.
- Treat feedback/downvotes as review signals, not automatic truth updates.

Agent UX:

- Provide small MCP/SDK tools.
- Make `remember`, `recall`, `judge`, and `forget` distinct.
- Return conflicts for review instead of silently overwriting.
- Avoid broad semantic deletion without ID confirmation.
- Expose "which memories did you use?" as a first-class audit command.
- Require an explicit write target when private and shared scopes coexist.

Testing/evals:

- Golden extraction cases.
- Contradiction and supersession cases.
- Scope leakage cases.
- Prompt-injection recall cases.
- Delete/forget compliance cases.
- Long-running compaction/summarization regression cases.

Operations:

- Keep local state inspectable during early development.
- Use atomic transactional storage for primary state; reserve flat JSON for export or single-process prototypes.
- Add background workers only after synchronous semantics are clear.
- Log memory mutations as audit events.
- Version schemas.
- Provide repair/reindex paths for vector-store corruption or embedding-model swaps.
- Keep retrieval events append-only; derive counters from events.
- Preserve failed background-extraction inputs and provide a bounded retry/redistill path.
- Separate private auto-commit behavior from shared repository writes.

Privacy/deletion:

- Design deletion before shipping.
- Know whether delete means hide, tombstone, hard delete, or forget from embeddings.
- Propagate deletion to raw chunks, derived memories, summaries/indexes, graph facts, backups, sync, and remote backends.
- Test that cross-source graph edges cannot survive as dangling references after source deletion.

## 11. Appendix

### Individual Reports

- [`mem0`](../systems/mem0/)
- [`langmem`](../systems/langmem/)
- [`honcho`](../systems/honcho/)
- [`engram`](../systems/engram/)
- [`mempalace`](../systems/mempalace/)
- [`swafra`](../systems/swafra/)
- [`llm-wiki-memory`](../systems/llm-wiki-memory/)
- [`rainbox`](../systems/rainbox/)
- [`letta`](../systems/letta/)
- [`supermemory`](../systems/supermemory/)
- [`verel`](../systems/verel/)
- [`hindsight`](../systems/hindsight/)
- [`graphiti`](../systems/graphiti/)
- [`mastra-observational-memory`](../systems/mastra-observational-memory/)
- [`memos`](../systems/memos/)
- [`basic-memory`](../systems/basic-memory/)

### Repos Inspected

- [mem0ai/mem0](https://github.com/mem0ai/mem0) at [`31cec11a790868f88c9acafb8b70eb25071f2150`](https://github.com/mem0ai/mem0/commit/31cec11a790868f88c9acafb8b70eb25071f2150)
- [langchain-ai/langmem](https://github.com/langchain-ai/langmem) at [`c01e273b94aa4c06e41d0ed1ccce0db17de2bc11`](https://github.com/langchain-ai/langmem/commit/c01e273b94aa4c06e41d0ed1ccce0db17de2bc11)
- [plastic-labs/honcho](https://github.com/plastic-labs/honcho) at [`eb386c3ceb77774b29108f9ab114e71d52b7d420`](https://github.com/plastic-labs/honcho/commit/eb386c3ceb77774b29108f9ab114e71d52b7d420)
- [Gentleman-Programming/engram](https://github.com/Gentleman-Programming/engram) at [`44faeee1fb4fabdee4ba9619df55af485f3d06eb`](https://github.com/Gentleman-Programming/engram/commit/44faeee1fb4fabdee4ba9619df55af485f3d06eb)
- [MemPalace/mempalace](https://github.com/MemPalace/mempalace) at [`afd0428823b47f9a9d1d68c450d54bb0045a4988`](https://github.com/MemPalace/mempalace/commit/afd0428823b47f9a9d1d68c450d54bb0045a4988)
- [kunal12203/swafra](https://github.com/kunal12203/swafra) at [`24dba18a4194aef0cb0d6d6c68cf46e6fcbf2da7`](https://github.com/kunal12203/swafra/commit/24dba18a4194aef0cb0d6d6c68cf46e6fcbf2da7)
- [ctxr-dev/llm-wiki-memory](https://github.com/ctxr-dev/llm-wiki-memory) at [`b7cc76a493573baac133969b324a874990556146`](https://github.com/ctxr-dev/llm-wiki-memory/commit/b7cc76a493573baac133969b324a874990556146)
- [neoneye/RainBox](https://github.com/neoneye/RainBox) at [`0792f8a07f6ff728931e928b2bdf7460492ac011`](https://github.com/neoneye/RainBox/commit/0792f8a07f6ff728931e928b2bdf7460492ac011)
- [letta-ai/letta](https://github.com/letta-ai/letta) at [`6d8cb7fd48938b629aad5770faa051a8d42e1e9f`](https://github.com/letta-ai/letta/commit/6d8cb7fd48938b629aad5770faa051a8d42e1e9f)
- [supermemoryai/supermemory](https://github.com/supermemoryai/supermemory) at [`603d0512fd40e4575e2a075938c1851a898ceeb6`](https://github.com/supermemoryai/supermemory/commit/603d0512fd40e4575e2a075938c1851a898ceeb6)
- [amitpatole/verel](https://github.com/amitpatole/verel) at [`df80efe8207a99585a2ebce36fc6e32ba5077e2e`](https://github.com/amitpatole/verel/commit/df80efe8207a99585a2ebce36fc6e32ba5077e2e)
- [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight) at [`ed120a256d51d731085ec8aca724573a7f2f1e1c`](https://github.com/vectorize-io/hindsight/commit/ed120a256d51d731085ec8aca724573a7f2f1e1c)
- [getzep/graphiti](https://github.com/getzep/graphiti) at [`9140123a7282d44efc077a0af09179919f3defdf`](https://github.com/getzep/graphiti/commit/9140123a7282d44efc077a0af09179919f3defdf)
- [mastra-ai/mastra](https://github.com/mastra-ai/mastra) at [`40547102f655596178346ad2f883fbde735c3333`](https://github.com/mastra-ai/mastra/commit/40547102f655596178346ad2f883fbde735c3333)
- [MemTensor/MemOS](https://github.com/MemTensor/MemOS) at [`3fd109e7cbaba291af2253f107e0a595dbf62b00`](https://github.com/MemTensor/MemOS/commit/3fd109e7cbaba291af2253f107e0a595dbf62b00)
- [basicmachines-co/basic-memory](https://github.com/basicmachines-co/basic-memory) at [`232f2c2fc4e91564d88bcc312ed3d8bd1e8e051b`](https://github.com/basicmachines-co/basic-memory/commit/232f2c2fc4e91564d88bcc312ed3d8bd1e8e051b)

### Commands Used

Representative local inspection commands:

- `find . -maxdepth ... -type d`
- `rg --files`
- `rg -n "memory|recall|remember|search|embedding|vector|MCP|Block|Passage|Representation|drawer|palace|wing|room|claim|evidence|retrieval_event"`
- `sed -n ...`
- `wc -l`
- `cmp`
- `jq`
- `git show -s --format=fuller HEAD`

No internet sources were used for this report. The analysis is based on the checked-out code in this workspace.

### Known Limitations

- Supermemory's hosted backend implementation was not visible in this checkout; its report emphasizes schemas, clients, SDKs, MCP, and graph UI.
- Some mem0 advanced capabilities appear to be managed-platform-only in the inspected OSS code.
- This is an implementation-oriented static review, not a runtime benchmark.
- Retrieval quality and extraction quality were not independently re-measured; committed benchmark artifacts were inspected for MemPalace but not rerun.
- Swafra was reviewed at commit `24dba18`; its full LongMemEval run was not rerun. Static inspection, committed artifact analysis, and a small hash-embedder smoke check exposed the `k` mismatch and same-title source behavior.
- `llm-wiki-memory` was reviewed at commit `b7cc76a493573baac133969b324a874990556146`; its broad test tree and committed latency report were inspected, but the suites and benchmarks were not rerun.
- RainBox was reviewed as an application-integrated memory subsystem; unrelated assistant/product features were not exhaustively analyzed.
- The reports prioritize memory-management code paths over unrelated framework/application code.
- Hindsight, Graphiti, Mastra, MemOS, and Basic Memory were reviewed statically at the pinned revisions above; their dependency-heavy integration suites and published benchmarks were not rerun.
- Mastra analysis is intentionally limited to `packages/memory` and the core contracts it directly uses.
- MemOS behavior varies materially by memory cube, backend, model, and search configuration; the report does not imply one universal MemOS pipeline.

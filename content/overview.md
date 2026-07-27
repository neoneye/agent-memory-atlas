---
title: Agent Memory Systems Comparative Report
eyebrow: Cross-system synthesis
description: A code-grounded comparison of forty-six agent memory architectures, their retrieval mechanics, trust models, and operational tradeoffs.
root: ..
page_kind: comparison
---

## Reading This Report

**What is in the atlas.** A system qualifies if something it stores **survives
the session with an identity that can later be corrected**. That single test
does the work: it admits a 300-line Markdown file with stable entry IDs and
excludes a sophisticated chat-buffer compactor, however good the compaction is.
Systems reviewed and excluded on this basis, or on licence grounds, are named in
the limitations at the end rather than quietly dropped — the exclusions are part
of the evidence.

**How systems were selected.** Opportunistically: repositories encountered,
suggested, or found while looking for the ones already here. This is not a
sample of a population and no sampling frame is claimed. It skews toward
actively developed open-source projects, toward things adjacent to coding
agents, and toward whatever was visible in mid-2026. Absence from this atlas is
not evidence of anything.

**What an absence claim means.** "There is no trust state", "no tombstone was
found", "no benchmark exists" all mean the same thing: *not found in the
inspected code at the pinned commit*. Every claim here is static review — code
read, not run — and the reports are opinionated by design. Where the code is
partly closed, or a capability is documented but managed-platform-only, the
reports say so at that point rather than hedging every sentence.

**The divergences that actually separate these systems.** If you read nothing
else:

1. **Whether correction is possible at all.** Almost everything can overwrite
   or supersede. Two systems of forty-six can record that a *value* was
   rejected so extraction cannot bring it back. This is the single widest gap in
   the field, and it is invisible on every benchmark.
2. **Whether evidence outlives its derivations.** Systems that keep the raw
   event and treat summaries, profiles, and graphs as rebuildable projections
   can repair a bad extraction. Systems that discard the source cannot.
3. **Whether scope is identity or decoration.** A scope key applied on the read
   path is a boundary; a scope tag stored beside the memory is a hope.
4. **Whether retrieval can decline.** Most systems always return their top *k*.
   Very few can decide that this turn needs no memory, and irrelevant memory in
   a prompt is not inert — it bends the answer.
5. **Who decides.** Fully automatic memory, memory a person can review before it
   takes effect, and memory a person authors are three different products with
   three different failure modes.

Everything below is evidence for those five, in more detail than most readers
need. The [capability index](#capability-index) is the fastest way in.

## 1. High-Level Taxonomy

Forty-six systems do not fall into forty-six categories. They cluster around
eight architectural commitments, and most systems belong to more than one —
a coding-agent memory can also be verification-first, and a host runtime's
plugin can also be a hosted service. The families below are lenses, not bins.

Where a system is the clearest instance of an idea, it is named in bold and
characterized in place rather than given a category of its own.

### Embeddable memory libraries

`mem0`, `langmem`, `llamaindex`, `cognee`, `a-mem`

Called from an application that owns the agent loop. Easy to adopt; weak
authority over when memory is written or how recall is used. **Cognee** is the
outlier in surface area — a knowledge pipeline platform with ontologies,
dataset permissions, and provenance rollback behind a small remember/recall
API. **LlamaIndex** composes memory from pluggable blocks that each truncate
themselves to budget. **A-MEM** is a compact Zettelkasten research sketch whose
linked-note evolution idea outruns its implementation.

Tradeoff: a library can store and retrieve, but it cannot guarantee the model
calls the right tool, verifies a fact, or uses recall safely.

### Hosted and service memory

`honcho`, `supermemory`, `hindsight`, `redis-agent-memory-server`, `openviking`

Multi-user, API-first, with background derivation. **Honcho** models workspaces,
peers, sessions, and derived representations rather than flat facts.
**Hindsight** runs four independent recall arms with task-specific fusion.
**Redis Agent Memory Server** splits TTL-scoped working memory from promoted
long-term memory and carries the atlas's most developed retention policy.
**OpenViking** unifies memory, resources, and skills in one filesystem
hierarchy with three retrievable granularities per record.

Tradeoff: the API surface is usually easier to study than the decision
machinery. In `supermemory` the hosted core is not visible at all; in `mem0`
several documented capabilities are managed-platform-only.

### Agent-runtime memory

`letta`, `rainbox`, `memos`, `mastra-observational-memory`, `claude-mem`,
`agentmemory`, `tencentdb-agent-memory`, `nanobot`, `cowagent`, `genericagent`,
`mercury-agent`, `atomic-agent`, `mateclaw`, `waku-agent`, `loongflow`

Memory is part of the runtime: compiled into context, mutated through
first-class actions, tied to agent state. **Letta** separates core, archival,
and recall memory inside the loop. **RainBox** routes every belief through one
governed write path with a five-actor trust model. **MemOS** mounts textual,
preference, skill, KV-cache, and parametric memory as one cube. **Mastra**
compresses older messages into dated observations and activates them without
blocking. **TencentDB** layers L0 conversation evidence through L3 persona with
symbolic tool-output offload. **Mercury** grades every record on confidence,
importance, and durability separately, and keeps a subconscious tier below
active recall. **Atomic Agent** cites numbered invariants from its schema into a
design document, records votes as append-only events with derived scores, and
ships new memory features off by default until an evaluation campaign reports. **GenericAgent** governs four file layers with written axioms
instead of code. **Waku** organizes everything around refusing expensive work:
a small model decides whether to retrieve at all, consolidation batches, and
skill bodies load only on match. **LoongFlow** carries two unrelated memories in
one package — a conventional short/medium/long tier stack, and a population of
scored solutions recalled by Boltzmann sampling whose temperature is driven by
the population's measured diversity.

Tradeoff: deeper integration buys behavioural control at the cost of coupling
memory to the framework, prompt assembly, and tool loop.

### Host runtimes with pluggable memory

Hosts: `hermes-agent`, `openclaw`, `pi`, `mateclaw`
Plugins mounted on them: `holographic`, `magic-context`, `metaclaw`,
`byterover`, `tencentdb-agent-memory`, plus hosted providers

The runtime ships an interface, not a memory model. **Hermes** bounds its own
curated Markdown hard and freezes it into the prompt at session start while
mounting one external provider. **OpenClaw** ships memory entirely as
extensions over a plugin contract. **Pi** is the limit case: twenty-plus
lifecycle events and no memory concept at all, so plugins rebuild indexing,
scope, and retrieval from scratch.

Tradeoff: users choose a backend that fits their privacy and scale needs, but
trust state, scope, and above all deletion must cross the host/provider
boundary. **MateClaw** is the partial counterexample: its provider SPI carries an
owner key on `prefetch` and `syncTurn`, and wraps every provider in retry and
metrics decorators — but like the other three, it has no deletion hook. One
contract of four carries scope; none carries deletion. See
[pluggable memory provider](../patterns/pluggable-memory-provider/).

### Local coding-agent memory

`engram`, `mempalace`, `llm-wiki-memory`, `basic-memory`, `moltis`,
`open-cowork`, `byterover`, `magic-context`, `swafra`, `memora`

Durable local state for a developer workflow: hooks, MCP, project scopes, exact
search. **Engram** is the small no-extraction baseline over SQLite and FTS.
**MemPalace** keeps verbatim drawers authoritative and treats extracted layers
as navigation aids. **Basic Memory** makes human-editable Markdown canonical
and every index a rebuildable projection. **Moltis** indexes a Markdown corpus that sanitized
session transcripts are exported into, so conversations become searchable notes
in the same substrate as curated ones. **open-cowork** separates core from experience memory and
ships the atlas's most complete memory benchmark. **Swafra** shows how little
code a local graph-RAG sidecar needs, and why flat JSON is not a database.
**Memora** is the only system here whose automated correction pass defaults to a
dry run: the sweep that would hide superseded memories reports its findings
unless mutation is explicitly requested.

Tradeoff: operationally simple and inspectable; no answer to hosted ranking,
multi-tenancy, or rich user modelling.

### Graph, temporal, and symbolic memory

`graphiti`, `cognee`, `hipporag`, `holographic`, `gini-agent`

Structure is the retrieval mechanism. **Graphiti** tracks transaction time and
real-world validity separately, invalidating facts by closing an interval
rather than erasing history. **HippoRAG** seeds a personalization vector and
lets Personalized PageRank diffuse relevance instead of planning hops, and
links similar entities rather than merging them. **Holographic** encodes facts
as SHA-256-derived phase vectors so entities can be bound and unbound
algebraically, with no embedding model to version. **Gini** reimplements the
Hindsight model locally with bi-temporal columns and four RRF-fused channels.

Tradeoff: structure answers questions flat stores cannot, but extraction and
resolution mistakes have a blast radius proportional to how connected the graph
is.

### Verification and trust-first memory

`verel`, `rainbox`, `magic-context`, `metaclaw`, `gini-agent`

These treat memory as a trust problem before a retrieval problem. **Verel**
separates confidence, retrieval strength, and verification state, carries
rejected values forward, and fences recall as untrusted data. **RainBox** adds
governed atomic correction, lattice-aware conflict detection, and rejected-value
tombstones that block model re-assertion. **Magic Context** maps each memory to
the files it describes and re-verifies when git reports those files changed,
keeping lifecycle and verification on separate axes. **MetaClaw** applies the
idea one level up, promoting a candidate *retrieval policy* only when it does
not regress across eight measured deltas.

Tradeoff: more machinery than an MVP needs, and it directly addresses the
failures simpler systems discover in production.

### Research lineage

`generative-agents`, `voyager`, `hipporag`, `a-mem`

Artifacts the practical systems are largely responses to. **Generative Agents**
established the observation/reflection/planning stream and the
importance-recency-relevance score — whose weights, read at the source, are
hand-tuned constants with two abandoned settings left in comments. **Voyager**
established procedural skill memory with an execution-verified write gate.
**HippoRAG** established diffusion-based associative retrieval.

Tradeoff: the ideas are unusually legible because no production concern
obscures them, and none of these has scope, correction, deletion, or a trust
model. Voyager and Generative Agents have been frozen since 2023; read them for
design, not adoption.

### Not in scope: conversation-window management

Most agent frameworks ship something called "memory" that is a **chat buffer**,
and the naming collision misleads people evaluating options.

IBM's [BeeAI framework](https://github.com/i-am-bee/beeai-framework) is the
cleanest example. At commit
[`21284d7`](https://github.com/i-am-bee/beeai-framework/commit/21284d7f53d5a50e546350f371c69747bd6a176b)
its entire memory subsystem is about 1,300 lines across both the Python and
TypeScript implementations, and consists of four strategies for deciding which
messages stay in context: `UnconstrainedMemory`, `SlidingMemory`, `TokenMemory`,
and `SummarizeMemory`, plus a `ReadOnlyMemory` wrapper. Its documentation states
that "Messages are the fundamental units stored in memory". The memory modules
reference no embeddings, vectors, or persistent store; BeeAI keeps document
retrieval in a separate `rag` module, so the framework's own architecture agrees
these are different concerns. LlamaIndex's older `ChatMemoryBuffer` family and
LangChain's original `ConversationBufferMemory` are the same category — which is
why this atlas reviews `langmem` and LlamaIndex's newer block-based `Memory`
instead.

Deciding what stays in the context window is a real problem. It is a different
problem: nothing survives the session, nothing is retrieved, nothing is scoped,
corrected, verified, or forgotten on request. A system whose memory is a window
has no answer to "why do you believe that?" or "forget what I told you last
week", because it never claimed to remember.

Compaction appears in this atlas only as a component of systems that also
persist — `mastra-observational-memory` with exact covered ranges and buffered
activation, `hermes-agent` with a hard budget forcing in-turn consolidation,
`pi` with deterministic file manifests on compaction entries. The test for
inclusion is not whether a system compacts, but whether anything survives the
session with an identity you could later correct.

## 2. Comparative Matrix

<!-- BEGIN GENERATED MATRIX -->
| Repo | Memory unit | Storage backend | Retrieval strategy | Write strategy | Update/delete model | Scoping model | Agent integration | Background processing | Trust/provenance model | Notable strengths | Main risks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `a-mem` | `MemoryNote` with content, tags, context, links, and evolution history | In-process dictionary plus ephemeral Chroma; separate persistent retriever utility | Vector similarity with optional linked-neighbor append | LLM decides links and neighbor metadata mutation before insert | Delete/re-add update; exact delete without incoming-link cleanup | None in core | Direct Python library | Periodic reindex called consolidation | No source provenance or trust state | Small, legible linked-note evolution concept | Neighbor position/identity bug can mutate wrong notes; destructive initialization; no durability |
| `agentmemory` | Raw/compressed observation, versioned memory, summary, lesson, graph/semantic/procedural records | iii StateModule backed by local SQLite plus persisted search projections | BM25 + optional vector + graph arms, weighted RRF, query expansion, rerank, source diversity | Hooks call `mem::observe`; explicit `mem::remember`; optional compression and consolidation | Delete/TTL; similarity-based version supersession; rebuildable indexes | Project, session, working directory; shared or isolated agent mode | Hooks, MCP, HTTP, CLI, iii functions | Optional compression, graph extraction, consolidation, decay, repair | Source observation IDs, versions, audit; no candidate/verified/rejected state | Cheap synchronous capture and compact-first hybrid search | Very broad surface; shared scope default; fuzzy supersession can hide conflicts |
| `atomic-agent` | Memory, lesson, profile fact, and procedure, linked by typed edges | SQLite with versioned migrations; bi-temporal profile facts | Heuristic-gated query rewriting, links, and vote-aware ranking | Consolidator clusters; lessons and procedures from one LLM call per cluster | `supersedes`/`superseded_by` chains; deprecation retains the row | Not traced | Agent runtime with a separate reflection slot | Consolidator, reflection, neighbour evolution, vote runner | Append-only `vote_events` with derived `vote_score`; surfaced-id allowlist | Numbered invariants cited from code, and features default-off until evaluated | Large opt-in surface; evaluation campaign results not committed |
| `basic-memory` | Canonical Markdown note; indexed entity, observation, relation | Filesystem source + SQLite/PostgreSQL projection | FTS5/tsvector, optional semantic chunks, hybrid score fusion, graph context | MCP/API writes accepted Markdown; file watcher reconciles human edits | Distinct create/replace/edit/move/delete with stable ID and reindex | Project, workspace, tenant, local/cloud route | MCP tools, typed clients, API, CLI | Watcher, startup reconciliation, indexing workflows | Human-visible source/checksums; no candidate/verified state | Inspectable portable memory with rebuildable indexes | Bidirectional sync complexity; agent can write unsupported claims |
| `byterover` | Flat memory with source/pinned metadata; structured knowledge `ContextData` | Local Markdown under `.byterover/`, optional cloud sync | Metadata filter and pagination only in inspected modules | LLM dedup returning CREATE/MERGE/SKIP; `DECISIONS` always creates | Structural-loss guard repairs destructive curation; no tombstones | Storage directory only | `brv` CLI, MCP, Hermes provider | LLM dedup at bounded concurrency | `source` of agent/system/user recorded but not enforced | Deterministic structural-loss detection and repair on LLM rewrites | Elastic License 2.0, not open source; merge path itself is unguarded |
| `claude-mem` | Hook event, pending message, observation, session summary, prompt | Canonical SQLite, optional Chroma projection and cloud sync | FTS/filter search or Chroma semantic search; file-only metadata/semantic intersection; recent timeline context | Lifecycle hooks queue work; observer generates structured XML; SQLite commit before acknowledgement | Exact row deletion with synchronized tombstones; project-wide server forget paths | Project/worktree, session, platform source; team/server scope emerging | Coding-agent hooks, HTTP, MCP, UI, multiple adapters | Durable queue, provider retries, vector/cloud projection, repair | Session/tool metadata and deterministic file evidence; generated claims have no trust state | Reliable non-blocking capture and bounded cross-session context | Ordinary search is not fused hybrid; generated observations activate automatically; dual schema transition |
| `cognee` | Source data, chunk, typed `DataPoint`, graph edge, summary, session entry | SQLite/PostgreSQL plus pluggable graph/vector stores | Chunk, lexical, vector, graph, triplet, summary, temporal, hybrid, and routed modes | `add` + `cognify`; unified `remember`; session-hot writes with background improvement | Exact data/dataset/all forget; memory-only reprocessing; provenance rollback | User permissions and dataset; optional per-user/dataset backend isolation | Python, REST, CLI, MCP, typed memory entries | Composable pipelines, session bridge, memify, rollback/recovery | Source records, content hashes, pipeline/task/user provenance; no factual trust state | Ontology-aware multimodal graph pipeline with serious rollback | Large configuration surface; cross-store consistency; extracted graph can harden errors |
| `cowagent` | Markdown files, chunked into an indexed `chunks` table | SQLite with embeddings and self-healing FTS5 | Vector plus keyword over chunks; `MEMORY.md` injected in full | Summarize into dated daily files, then distil | Recency-wins conflict update; whole-file overwrite | `user_id` and `scope`, defaulting to `shared` | Agent memory tools | Deep Dream after the daily summary, 23:55 cron | Line-addressable chunks with hashes; dream diary | Dated intermediate layer and written distillation rules | Shared-by-default scope; chained lossy summarization |
| `engram` | Observation and prompt records | Local SQLite WAL, FTS5 | FTS5, topic-key lookup, context assembly | MCP `mem_save`, conflict candidate flow, dedupe/update rules | Topic-key updates, duplicate counts, soft delete/sync mutation | Project, scope, session, topic key | MCP tools for coding agents | Sync queue, local conflict workflows | Source/session/project metadata, explicit judgment path | Simple durable local design, inspectable code | Lexical retrieval limits; conflict UX depends on agent behavior |
| `generative-agents` | `ConceptNode` typed event, thought, or chat with poignancy | Per-persona JSON plus in-memory embedding dict | Normalized recency + relevance + importance, hand-tuned `gw = [0.5, 3, 2]` | Perception, conversation, and reflection all write ungated | None; observations are never deleted or overwritten | One persona directory | Simulation only; tightly coupled to `Persona` | Reflection fired by accumulated poignancy | Reflections cite supporting nodes, but citations are never used | Consolidation triggered by significance rather than a timer | Derived thoughts share one pool with observations; positional not temporal decay |
| `genericagent` | Text and Markdown across four layers | `global_mem_insight.txt`, `global_mem.txt`, `memory/`, `L4_raw_sessions/` | Agent reads a ≤30-line index and opens files by pointer | Only successful tool-call results may be written (by policy) | Layer migration and patching; "better not to modify at all" | One global tree | Internal to the framework | 12-hour L4 archive cron | Verification is a stated precondition, but no record is kept | "No Execution, No Memory" plus an ROI test for permanent context | Every axiom is prose with no enforcement or audit |
| `gini-agent` | `memory_units` with network, status, confidence, bi-temporal occurrence | SQLite (`memory_banks`, `entities`, `entity_mentions`, `memory_links`) | Four channels — semantic, BM25, graph spreading activation, temporal — fused by RRF then reranked | `retain.ts`; `proposed` status as a candidate tier | `rejected` and `conflicted` states, `archived`, supersession | `agent_id` enforced across every channel and the HTTP API | CLI, HTTP, web UI | `reflect.ts` consolidation, `reinforce.ts` | Per-unit `embedding_model`, source task and session ids | Bi-temporal columns and a rejected/conflicted trust model, with decisions kept as ADRs | Conflict state has no visible resolution workflow; no value tombstone |
| `graphiti` | Episode, entity, temporal relationship edge, community/saga | Neo4j, FalkorDB, Kuzu, Neptune | BM25 + cosine + BFS across edges/nodes/episodes/communities; RRF/MMR/cross-encoder | Episode ingestion, entity/edge extraction, resolution, temporal invalidation | Close `valid_at` intervals, expire edges, remove episodes | `group_id`, entity/edge types | Python library, MCP, server | Ingestion maintenance; saga summaries | Source episode UUIDs and bi-temporal history; no verified state | Preserves changing facts without erasing history | Entity merge/invalidation mistakes reshape the graph |
| `hermes-agent` | Delimited text entry in `MEMORY.md` / `USER.md`; session message; skill | Markdown files plus SQLite `state.db` with FTS5 | Curated memory always in prompt; session history via FTS5; no cross-layer fusion | Explicit `memory` tool through a staged write-approval gate | Substring-addressed replace/remove; hard char cap forces in-turn consolidation | Profile-level only; no project or room boundary within a profile | Own tools plus one mounted `MemoryProvider`; MCP serve | None for curated memory; providers may run their own | Threat-scanned at write; no provenance on entries | Frozen prompt snapshot preserves cache; foreign-write detection with backup | Model writes are instantly authoritative; unlogged budget-driven eviction |
| `hindsight` | Source chunk, world/experience fact, observation, reflection | PostgreSQL/pgvector or Oracle | Semantic + BM25 + graph + temporal, RRF/interleave, cross-encoder rerank | Screen, chunk, extract, embed, link, consolidate | Replace/append source; observation create/update/history; exact bank/document operations | Memory bank, tags, schemas/tenants | REST, MCP, generated SDKs, framework integrations | Queued consolidation and maintenance with retries | Source IDs, proof counts, audit/LLM traces; no explicit truth state | Complete service pipeline; task-specific fusion; temporal recall | LLM facts/observations can harden errors; operational complexity |
| `hipporag` | Chunk plus derived entity and passage graph nodes | igraph graph with pluggable vector store (Qdrant/Chroma/Milvus) | Fact scores → LLM rerank → IDF-penalized graph seeding → Personalized PageRank diffusion | `index()`: chunk, OpenIE triples, fact/passage/synonymy edges | Chunk-scoped delete; shared entities survive by reference count | None — corpus is global | Python library only; no MCP, tools, or service | Cacheable OpenIE; incremental synonymy edges | Chunk identity only; no actor, time, or trust state | Diffusion replaces hop planning; synonymy as edges rather than merges | Assertion instead of fallback on unlinked queries; undirected diffusion discards predicate direction |
| `holographic` | Flat fact row plus HRR phase vector and linked entities | Local SQLite (WAL) with FTS5 and per-category bundled banks | FTS5 + Jaccard + HRR cosine, multiplied by trust; algebraic `probe`/`related`/`reason` | `fact_store` tool, mirrored host writes, optional end-of-session regex extraction | Exact update/remove; feedback shifts trust; no supersession | Category only; no user/project/session scope | Hermes `MemoryProvider` plugin; `fact_store` and `fact_feedback` tools | None; bank rebuild is synchronous on every write | None — no source, actor, or session on a fact | Deterministic hash-derived vectors; `contradict` as a query action | Three downvotes silently drop a fact below the retrieval floor; one score for truth and reachability |
| `honcho` | Message, document/observation, representation | Postgres/SQLAlchemy, pgvector or vector adapter | Working representation blends semantic, recent, most-derived; message search with windows | Message ingestion plus queued derivation | Soft delete, representation reconciliation | Workspace, peer, session, collection | Hosted API/service model | Deriver queues and workers | Source IDs, derived observations, peer/session provenance | Strong event-to-representation pipeline | Operational complexity; LLM-derived observations still need trust policy |
| `langmem` | Store item, usually JSON memory | LangGraph `BaseStore` | `store.search/asearch` delegated to backend | Tools call create/update/delete/search; extraction via Trustcall | Tool-level CRUD | Namespace templates | LangChain/LangGraph tools | Reflection executor local/remote | Mostly application-defined | Clean primitives, schema-driven extraction | Too low-level to solve memory quality alone |
| `letta` | Core memory block, archival passage, message | ORM database; passages with embeddings; optional git memory | Archival search, conversation search, compiled core prompt | Agent tools mutate core/archival memory | Append/replace/patch, passage insert, block update | Agent, block labels, files/sources | Deep runtime tool executor integration | Prompt rebuilds, manager services | Block tags/metadata, message timestamps; limited truth model | Clear core/archive/recall separation | Agent can rewrite important memory without strong verification |
| `llamaindex` | Block-owned content; no memory record | Application-chosen; vector store via the framework's abstractions | Per-block: vector retrieval, extracted facts, static text — composed, not fused | Short-term history overflow flushes `token_flush_size` into blocks | Condensation rewrites the fact list wholesale; no tombstone | None; application-owned | LlamaIndex agents and workflows; custom blocks via `BaseMemoryBlock` | None; extraction runs on flush | None — extracted facts record no source | Self-truncating blocks and one explicit budget split | No provenance, correction, or scope; capture depends on conversation length |
| `llm-wiki-memory` | Typed Markdown atom, plan/investigation, daily capture, or full document | Filesystem wiki, per-category embedding caches, private git history | Metadata prefilter, local embedding/chunk cosine, priority bands, federated locality boost; lexical vector fallback | MCP/CLI writes, transcript and plan hooks, daily compile, full-document absorb | Upsert/relocate, archive/re-enable, exact delete, supersedes, opt-in dedup/refresh consolidation | Private brain plus explicit repository wiki levels; workspace/area/task/subject facets | MCP, CLI, Claude Code lifecycle hooks, shared instructions | Detached flush, daily compile, opt-in consolidation, cron healing, git/cache maintenance | Body hash, capture audit, git history, user-gated lessons; no candidate/verified/rejected state | Recoverable capture, explicit targets, deterministic layout/topology, excellent operational tests | LLM atoms become active without verification; vector-only primary retrieval; linear scans; git is not erasure |
| `loongflow` | Message in graded tiers; `Solution` with score and timestamp in the evolving population | In-memory or Redis for the population; pluggable storage for graded tiers | Graded tiers by recency; population by Boltzmann selection with adaptive temperature | Messages flow through stm to mtm to ltm via a compressor; solutions appended with a score | Compression across tiers; population turnover by selection pressure | Not traced | LoongFlow agent SDK | Auto-compression between tiers | Score on each solution; no trust state on messages | The only stochastic recall in the atlas, with temperature driven by measured diversity | Two unrelated memory models under one package; the graded stack is conventional |
| `magic-context` | Memory with separate lifecycle and verification state, plus compartments, facts, primers | SQLite (70 migrations) with FTS5, embeddings keyed by `(memory_id, model_id)`, git commits indexed | Hybrid semantic + BM25 with source boosts and `matchType`, over memories and raw history | Agent, user, historian, or dreamer writes; synchronous promotion, async embedding | Supersession and merge lineage; archived, not tombstoned | `project` / `ecosystem` / `universe` lattice plus a `shareable` flag | Pi `ExtensionAPI` and an OpenCode adapter sharing one store | Dreamer: verify, map, classify, promote, retrospective, at commit boundaries | Four-actor `sourceType`, mutation logs, per-memory `verified_at` | Memories re-verified against the files they describe when git says those files changed | Verdict is an LLM call; no rejected-value tombstone; very large surface |
| `mastra-observational-memory` | Raw message, dated observation group, reflected observation context | Mastra `MemoryStorage` adapters | Sequential active observations + recent raw tail; optional observation-vector retrieval | Processor observes at token thresholds; reflector compacts observations | Range replacement, buffered activation, clear/clone records | Thread or resource | Deep Mastra input/output processor integration | Early async observation/reflection buffers with activation | Exact covered ranges and markers; summary has no truth state | Non-blocking context compaction for long sessions | Distributed locking and progressive summary drift |
| `mateclaw` | Fact, recall record, workspace file, and dream report | Relational repositories with fact projections | Provider `prefetch`, fact projection, and search package | Turn lifecycle events drive `syncTurn` across registered providers | Contradiction detection over facts; archive package; no tombstone found | `MemoryScope` string column with TEAM and GLOBAL shared; `MemoryOwnerResolver` | `MemoryProvider` SPI with decorators; tool beans; Vue memory UI | Scheduler, dream reports, nudge service | Contradiction detector; owner key carried through the provider contract | A provider contract that carries scope, and retry/metrics as decorators | No deletion hook on the SPI; contradiction handling is detection only |
| `mem0` | Text fact in vector payload | Vector store plus SQLite history/messages | Semantic, optional keyword/BM25, entity boost, optional rerank | LLM additive extraction, hash dedupe, entity linking | Explicit update/delete APIs; V3 default append-oriented | `user_id`, `agent_id`, `run_id`, filters | Python SDK, tool/API style | Extraction and linking on write | Attribution metadata, history; weak epistemic trust | Practical SDK, pluggable stores, hybrid search | LLM facts can become durable claims without verification |
| `memora` | Memory row with content, tags, metadata, importance, and access count | SQLite with FTS5, embeddings, crossrefs, events, actions; D1 cloud backend | FTS5 plus embeddings, ranked with age-and-access importance decay | MCP tools; documents and images ingested alongside text | Pairwise relation classification into supersession edges; superseded rows hidden from retrieval | Not traced; tags form a dotted hierarchy | MCP server, CLI, graph server | Supersession sweeps, embedding backfill, cloud sync | `memories_events` and `memories_actions` logs; `contradicts` as a relation between memories | Correction that can be rehearsed — dry_run defaults to True | No tombstone; supersession hides rather than blocks re-entry |
| `memos` | Textual item, graph tier, preference/skill, KV cache, LoRA | Configurable vector/graph stores, dumps, cache/model artifacts | Direct vector or graph + BM25 + rerank + reasoner; optional auxiliary memories | Reader extraction into a memory cube; scheduler transformations | Module-specific update/delete/soft-delete/dump semantics | User plus registered memory cube | MOS chat/runtime, APIs, CLI | Scheduler and activation-memory refresh | Source metadata varies by module; no uniform trust state | Treats memory as heterogeneous mountable resources | Umbrella API hides uneven guarantees and maturity |
| `mempalace` | Verbatim drawer chunks, closets, KG triples | Local Chroma default; sqlite_exact, Qdrant, pgvector; SQLite KG | Direct drawer vector search, BM25 rerank, closet boost, metadata filters, FTS fallback | Mine files/convos or MCP add drawer; deterministic IDs; chunk/upsert verbatim text | Delete/update drawers, delete by source, dedup, repair; limited epistemic correction | Palace, wing, room, source file, parent drawer, backend namespace | MCP, CLI, hooks, skills, wake-up stack | Mining, closet/hallway/tunnel computation, repair/sync/backup | Strong source provenance; weak candidate/verified/rejected trust state | Evidence-preserving raw baseline, hybrid retrieval, operational hardening | Raw stores get large/noisy; contradiction resolution mostly outside core recall |
| `mercury-agent` | `UserMemoryRecord` graded on confidence, importance, and durability | Second-brain DB, with people and relation records | Retrieval records `lastUsedAt` and `lastUsedQuery` | Candidates with narrowed `evidenceKind`; `evidenceCount` on corroboration | `dismissed` boolean and `supersededBy`; no tombstone | `durable`, `active`, `subconscious` tiers; single user | Internal, with a `brain/Memory.tsx` review page | Not traced | Four-way `evidenceKind`, corroboration counts, free-text provenance | Durability separated from importance; a subconscious tier; a learning-pause switch | Scores estimated once at write time; dismissal is not durable |
| `metaclaw` | `MemoryUnit` with type, status, importance, confidence, access count, reinforcement score | Store with embeddings, per-scope policies | Under a live `MemoryPolicyState`: mode, unit cap, token budget, weights | Conversation writes plus consolidation; no actor gate | `superseded_by` lineage, `expires_at`; no rejected state | `scope_id` throughout store, retriever, policy, metrics | OpenClaw plugin with a written spec and a sidecar manager | Self-upgrade worker: candidate → replay → gate → promote | Source session and turn range; reinforcement kept apart from confidence | Retrieval policy replayed offline and promoted only on non-regression across eight metrics | Optimizes overlap proxies; gate thresholds are themselves defaults |
| `moltis` | Chunk of a Markdown file | SQLite with vectors; pluggable local, OpenAI, batch, and fallback embeddings | Hybrid keyword plus vector, optional LLM rerank, citation modes | Corpus files plus sanitized session transcripts, one `sync()` chokepoint | Edit or delete the file and reindex | Indexed directory only | In-process library inside the host workspace | File watcher and scheduled memory work | Citations to path and chunk; content-hash addressing | `keyword_only()` makes a no-embeddings mode constructible and inspectable | Transcripts and curated notes rank identically; no trust state |
| `nanobot` | Markdown durable files plus JSONL summary lines | `SOUL.md`, `USER.md`, `memory/MEMORY.md`, `history.jsonl`, git | None; durable files are always in context | Consolidator appends evidence; Dream is the sole durable writer | Surgical edits under git; no tombstone | One workspace | Internal, with WebUI and cron | Dream on cron, gated on tool-error-free runs | Git history over an explicit durable-file allowlist | Dual cursors, and a cursor that refuses to advance after tool errors | No provenance from claim to evidence; single workspace scope |
| `open-cowork` | Core memory and experience memory as separately extracted kinds | Per-kind stores plus SQLite FTS, with an ingestion queue | Retriever then navigator assembles the prompt prefix; tested FTS-absent path | Queue, then per-kind extractors with independently optimized prompts | No visible trust state or tombstone | Workspace field on eval queries; scope model not traced | Memory tools plus an extension entry point | Ingestion queue and prompt optimization | Not traced; no verification modules found | A committed eval harness with `forbiddenHits` — negative retrieval assertions | Harness present, results absent; substring scoring favours extractive memory |
| `openclaw` | Categorized entry (preference/fact/decision/entity/other) with embedding | LanceDB via `memory-lancedb` extension; swappable embedding adapters | Vector search with mandatory agent-scoped predicate; no lexical arm | Optional auto-capture after envelope sanitization; 500-char truncation | Exact scoped delete; no tombstones, and auto-capture can restore content | `agentId`, composed inseparably into every predicate | Plugin contract via `memory-core`; tools, CLI, doctor checks | Auto-capture cursor with fingerprint drift detection | `createdAt` and category only | Envelope sanitization before capture; scope that cannot be dropped | Vector-only reference backend; sanitization is a denylist tied to envelope formats |
| `openviking` | Typed memory file with L0 abstract, L1 overview, L2 content, links and backlinks | Pluggable vector/graph stores plus native Rust/C++ index | Directory-recursive dense + sparse, level filter, per-type quota, rerank, hotness blend | LLM extraction into typed files; write target resolved before persistence | Merge ops with `upsert`/`add_only`/`update_only`; no rejection state | Tenant and permission via `RequestContext`; user space plus `peers/<id>` | Server, SDKs, CLI, web studio; Hermes and OpenClaw provider | Extraction, streaming update, reindex, hotness maintenance | URIs, types, timestamps; no evidential spans or trust state | Three-granularity progressive disclosure; hotness kept apart from confidence | Headline benchmark numbers lack committed raw artifacts; AGPL-3.0 |
| `pi` | None — session-tree entry, not a memory record | JSONL session tree (`id`/`parentId`), swappable in-memory backend | None; context is the tree walked to root plus discovered resource files | Append to session; compaction replaces a range | None; no durable claim exists | None | Own CLI/TUI/SDK; 20+ extension events, none memory-shaped | Compaction and branch summarization | Deterministic `readFiles`/`modifiedFiles` on compaction entries | Deterministic file manifest kept out of the model's output; branchable sessions | No memory contract at all, so scope and deletion have nowhere to live |
| `rainbox` | Claim, evidence, embedding, retrieval event | Postgres/SQLAlchemy plus pgvector | Hard-filtered hybrid (vector + Postgres full-text + entity boost) for both chat and assistant; profile digest | User commands, assistant actions, review UI; single governed atomic path (`record_belief`); write-time conflict detection; active/candidate flows | Reject/supersede/reactivate/expiry/sensitivity; `MemoryRejectedValue` tombstones block model re-assertion of rejected values; governed atomic correction (`correct_belief`); UI stale-write guards | Global, agent, room, project; sensitivity | Full assistant app: chat prompt (via `build_chat_memory_block`→hybrid), action loop, review UI | Embedding sync/prune, telemetry, feedback/eval loop | Five-actor trust model (3 human/override + 2 model/candidate); rejected-value tombstones; write-time lattice-aware conflict detection; governed atomic correction; fenced prompt injection; claim/evidence provenance and retrieval audit | Operator governance, trust/correction machinery (tombstones + conflict detection + fenced recall + governed writes), telemetry, eval integration | Compact claims may lose source nuance; no automatic candidate extraction; `epistemic_confidence`/`retrieval_strength` columns exist but Tier-1 ranking still uses `confidence` (schema groundwork only); attribution is context-injection, not causal |
| `redis-agent-memory-server` | Working-memory message; long-term `MemoryRecord` typed episodic/semantic/message | Redis with TTL for working memory; pluggable vector DB for long-term | Vector search plus metadata filters, reranked by recency with dual half-lives | Debounced trailing extraction via swappable strategies, then layered dedupe | Exact delete; composite forgetting policy; no tombstones | Namespace, `user_id`, `session_id`, with auth | REST, MCP, CLI, SDKs; backs the OpenClaw Redis plugin | Debounced extraction, compaction, dedupe, forgetting sweeps | Session linkage and per-message extraction flags; no trust state | Best-specified retention policy in the atlas; cohesion-gated semantic merge | Deletion is not durable against re-extraction; access-driven reinforcement |
| `supermemory` | Document, chunk, memory entry, space | Hosted backend; visible schemas/client only | Hosted search/profile API; SDK uses hybrid settings | API/MCP add memory/document | Version chains, relations, forget API | Space, container tags, org/user/project | SDK, AI SDK tools, MCP | Hosted processing not visible | Rich schema fields and relations; implementation not visible | Product/API surface, document-memory graph | Backend black box; semantic forget needs care |
| `swafra` | Verbatim or synthetic chunk plus directed chunk edges | Three local JSON files | BM25 + vector + entity/date/preference heuristics + char n-gram; graph walk; best chunk per title | MCP add; Leiden or exchange/paragraph chunks; synchronous full-file rewrite | Exact source delete; implicit same-ID reindex; broken supersession path | Source ID/title only; no user/project/tenant scope | Python FastMCP; Node MCP over Python subprocess | None | Caller title and raw chunk; no actor, span-quality provenance, trust state, or injection fence | Very compact local hybrid graph-RAG; optional dependencies; source diversity | Non-atomic concurrent writes; unbounded context; dangling edges; benchmark cutoff invalid |
| `tencentdb-agent-memory` | L0 conversation, L1 memory record, L2 scene, L3 persona, offload reference/map | JSONL/Markdown plus SQLite FTS5/sqlite-vec or Tencent VectorDB | FTS + vector hybrid RRF; native cloud hybrid; layered scene/persona context | Successful-turn capture, LLM extraction, store/update/merge/skip judge, symbolic tool-output offload | Internal merge/delete/cleanup; no first-class correction/forget tool | Session fields and data directories; no general tenant boundary | OpenClaw hooks/tools/context engine; Hermes gateway | Deferred embeddings, scene/persona generation, retention reclamation | Source message IDs and raw evidence; no verification/rejection state | Layered progressive disclosure with raw drill-down | Non-atomic dual writes, fail-open dedup, thin core tests, unsupported benchmark claims |
| `verel` | `MemoryRecord` fact/rule/schema/failure/skill | SQLite local plus backend adapters | Rank blends relevance, retrieval strength, confidence, trust; budgeted recall | Candidate extraction, attested/corroborated promotion | Correction chains, rejected tombstones, decay/prune | Scope lattice | Helpers, MCP, hosted/replicated adapters | Consolidation, promotion gate, replication | Explicit candidate/verified/rejected, provenance, confidence | Best correctness model in set | Complex; may be heavy for product MVP |
| `voyager` | Executable JavaScript skill plus generated description | `skills.json` and flat files, Chroma index over descriptions | Vector similarity over descriptions, top-5, returns code | Written only when a critic verifies environment success | Same-name rewrite; old versions on disk but unreachable | Single agent checkpoint directory | Research rollout loop; prompt injection of retrieved code | None | Verified execution is the provenance | Environment-verified write gate — the strongest in the atlas | Unbounded skill concatenation into prompts; no failure memory; frozen since 2023 |
| `waku-agent` | Fact (semantic), episode (episodic), and SKILL.md (procedural) | SQLite by default; Supabase for facts, Notion for episodes | Gated — a small model decides whether to search at all, and supplies the query | Consolidation batched after N new chats, not per message | None found; no supersession or tombstone | Single user | CLI agent; skills in the Anthropic Agent Skills format | Batched consolidation into facts and episodes | Gate decisions carry a reason string; no trust state on memories | Refusing expensive work at three levels, and failing open when the gate errors | No correction, scope, or trust model; gate adds a model call per turn |
<!-- END GENERATED MATRIX -->

### Capability index

The matrix above says what each system does. This index answers the other
question — *which systems actually have X* — for the mechanisms that most often
decide whether a memory layer is usable. It is generated from the same
frontmatter as the matrix, so it cannot drift from the reports.

Definitions are strict, and a flag is present only where the mechanism was found
in code. Near-misses do not count, and the near-misses are frequently the
interesting part: [`claude-mem`](../systems/claude-mem/) has "tombstones" that
synchronize row deletion across stores, which is not a rejected-value tombstone;
[`mercury-agent`](../systems/mercury-agent/) grades confidence but has no
discrete trust state; [`nanobot`](../systems/nanobot/) and
[`basic-memory`](../systems/basic-memory/) get an audit trail from git rather
than from an event table. Carrying none of these flags is not the same as
being bad: [`waku-agent`](../systems/waku-agent/)'s entire design is about doing
less on purpose, and [`moltis`](../systems/moltis/) is a corpus-and-index system
that never claims to model belief.

<!-- BEGIN GENERATED CAPABILITIES -->
**Rejected-value tombstone** — A durable record of a *rejected value*, keyed on the value, so later extraction cannot silently re-assert it.

*2 of 46:* [`rainbox`](../systems/rainbox/), [`verel`](../systems/verel/)

**Explicit trust state** — Discrete epistemic status — at least candidate versus verified versus rejected — as a field, not a confidence score.

*4 of 46:* [`gini-agent`](../systems/gini-agent/), [`magic-context`](../systems/magic-context/), [`rainbox`](../systems/rainbox/), [`verel`](../systems/verel/)

**Bi-temporal validity** — When a fact was true tracked separately from when the system recorded or expired it.

*3 of 46:* [`atomic-agent`](../systems/atomic-agent/), [`gini-agent`](../systems/gini-agent/), [`graphiti`](../systems/graphiti/)

**Scope enforced in retrieval** — A stored scope key (user, project, agent, tenant) applied as a filter on the read path, not merely available as a tag.

*26 of 46:* [`agentmemory`](../systems/agentmemory/), [`basic-memory`](../systems/basic-memory/), [`claude-mem`](../systems/claude-mem/), [`cognee`](../systems/cognee/), [`cowagent`](../systems/cowagent/), [`engram`](../systems/engram/), [`gini-agent`](../systems/gini-agent/), [`graphiti`](../systems/graphiti/), [`hindsight`](../systems/hindsight/), [`honcho`](../systems/honcho/), [`langmem`](../systems/langmem/), [`letta`](../systems/letta/), [`llm-wiki-memory`](../systems/llm-wiki-memory/), [`magic-context`](../systems/magic-context/), [`mastra-observational-memory`](../systems/mastra-observational-memory/), [`mateclaw`](../systems/mateclaw/), [`mem0`](../systems/mem0/), [`memos`](../systems/memos/), [`mempalace`](../systems/mempalace/), [`metaclaw`](../systems/metaclaw/), [`openclaw`](../systems/openclaw/), [`openviking`](../systems/openviking/), [`rainbox`](../systems/rainbox/), [`redis-agent-memory-server`](../systems/redis-agent-memory-server/), [`supermemory`](../systems/supermemory/), [`verel`](../systems/verel/)

**Append-only mutation audit** — An explicit event or audit record of memory mutations in the system's own store.

*7 of 46:* [`agentmemory`](../systems/agentmemory/), [`atomic-agent`](../systems/atomic-agent/), [`hindsight`](../systems/hindsight/), [`llm-wiki-memory`](../systems/llm-wiki-memory/), [`magic-context`](../systems/magic-context/), [`memora`](../systems/memora/), [`rainbox`](../systems/rainbox/)

**Human review surface** — A place where a person inspects, approves, or adjudicates memory content before or after it takes effect.

*6 of 46:* [`engram`](../systems/engram/), [`hermes-agent`](../systems/hermes-agent/), [`llm-wiki-memory`](../systems/llm-wiki-memory/), [`memora`](../systems/memora/), [`mercury-agent`](../systems/mercury-agent/), [`rainbox`](../systems/rainbox/)

**Negative retrieval assertion** — Committed evaluation cases asserting that particular material must *not* be retrieved.

*1 of 46:* [`open-cowork`](../systems/open-cowork/)
<!-- END GENERATED CAPABILITIES -->

Three observations follow directly from the counts. **Scope is solved and
correction is not**: over half the atlas enforces a scope key on the read path,
while two systems carry a value-level tombstone. **Trust is usually a number,
not a state**, which collapses "how sure am I" into "how findable is this" —
see [decay and reinforcement](../patterns/decay-and-reinforcement/). And
**negative evidence is almost never tested**: one repository asserts that
particular material must not be retrieved, which is the assertion every scope,
deletion, and correction claim in this document ultimately rests on.

## 3. End-to-End Memory Lifecycle Comparison

### Capture

`mem0`, `letta`, `langmem`, and `supermemory` expose direct tool/SDK surfaces for adding memory. `cognee` supports both explicit permanent writes and a session-hot capture path through `remember`. `claude-mem` writes hook events to a durable queue before invoking its observer. `a-mem` accepts direct Python note writes but runs LLM evolution before the new note is durable. `hindsight` retains documents/chunks before extracting facts. `graphiti` stores episodes before deriving entities and temporal relationships. `mastra-observational-memory` persists messages before compressing covered ranges. `memos` routes items into configured memory cubes. `basic-memory` accepts Markdown writes from MCP/API or human file edits and reconciles indexes. `rainbox` captures through explicit memory commands, assistant memory actions, and review UI mutations. `engram` captures via MCP tools and can also store prompt/session metadata. `mempalace` captures by mining files/conversations and by MCP drawer writes, preserving verbatim text. `swafra` captures titled text via one MCP tool, then stores chunks in local JSON. `llm-wiki-memory` combines explicit MCP/CLI writes with lifecycle hooks. `honcho` captures messages as the primary event stream, then derives observations. `verel` routes captured percepts through a trust gate. `agentmemory` combines cheap hook capture with explicit `mem::remember`; compression is optional. `tencentdb-agent-memory` records raw conversation evidence, then extracts higher layers from successful turns. `redis-agent-memory-server` writes messages into TTL-scoped working memory first and defers extraction behind a debounce. `hermes-agent` captures curated memory only through explicit tool calls, because a hard character budget makes automatic capture self-defeating. `openclaw` and `holographic` both capture without a model — OpenClaw after sanitizing its own message envelope, Holographic by regex over user turns when auto-extraction is enabled.

Two systems in the Hermes/OpenClaw ecosystem independently guard against the same subtle failure: **the harness's own scaffolding becoming memory.** OpenClaw devotes 567 lines to stripping media notes, context markers, reply headers, and sender prefixes before capture, with a `looksLikeEnvelopeSludge` gate rejecting what remains. Holographic had to exclude its host's compaction handoff summaries, which were being injected as `role="user"` messages, matched its decision-extraction patterns, and were stored as durable facts on every context rollover. Any system with automatic capture should test explicitly that its own generated text cannot re-enter as evidence.

The important split is whether the captured item is itself memory or evidence for memory. Cognee, Claude-Mem, Honcho, Verel, MemPalace, Graphiti, Hindsight, Basic Memory, Mastra, Swafra, RainBox, agentmemory, and TencentDB Agent Memory are evidence-aware in different ways: Cognee retains source data below graph/vector projections; Claude-Mem queues hook material before generated observations; Graphiti keeps episodes behind edges; Hindsight links observations to source facts; Basic Memory keeps canonical notes behind projections; Mastra records exact message ranges behind summaries; agentmemory links memories to observations; and TencentDB preserves L0 messages and offloaded raw tool output. These designs still differ sharply in trust: provenance supports correction, but only Verel and RainBox model rejection/promotion explicitly.

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

`agentmemory` defaults to synthetic compression on the hot path and makes LLM
compression/consolidation optional. `tencentdb-agent-memory` uses an LLM to
extract L1 records, then another judgment step chooses store, update, merge, or
skip; failures store all candidates rather than losing them.

`redis-agent-memory-server` is the clearest example of extraction policy as a
plugin point: `BaseMemoryStrategy` has discrete-fact, summary, user-preference,
and fully custom implementations, so what counts as a memory is configuration.
Because the custom strategy accepts an operator-supplied prompt, it also ships a
`PromptValidator` that screens those prompts for injection — an unusual threat
model in which the deployment's own configuration is the attack surface.
`openviking` extracts into typed memory files whose `stage` field separates
long-term user memory from execution-derived agent memory. `holographic` and
`openclaw` deliberately do not extract at all: both store lightly-processed user
text, which keeps capture model-independent but fills the store with prose
rather than normalized claims.

`cognee` runs typed task pipelines that chunk documents, extract graph
structures, embed several views, and optionally ground nodes in an ontology.
`claude-mem` asks an observer model for XML observations and summaries, but
replaces its modified-file list with paths deterministically derived from tool
calls. `a-mem` asks an LLM to organize a new note and rewrite nearby metadata;
its `analyze_content()` method has no call site, so ordinary note metadata is
not extracted as the public mental model suggests.

`magic-context` promotes eligible session facts synchronously and defers embedding to a best-effort async pass, so a memory is durable before it is enriched. `pi` captures nothing as memory — its JSONL session tree is conversation history, and every memory plugin builds its own index over it.

`genericagent` states the strictest capture rule in the atlas, as prose rather
than code: its *Action-Verified Only* axiom permits a durable write only when the
information came from a **successful tool call** — a shell command that
succeeded, a read that confirmed content, code that passed — and explicitly
forbids writing the model's inherent knowledge, guesses, unexecuted plans, or
unverified assumptions. Its slogan is "No Execution, No Memory". This is
`voyager`'s environment-verified gate generalized from procedures to facts; the
difference is that Voyager enforces it in the rollout loop while GenericAgent
asks the model to enforce it against itself, and keeps no record of the
justifying call.

The research lineage adds two capture disciplines the practical systems mostly lost. `voyager` writes memory **only** when a critic verifies the environment reached the intended state, so a failed attempt produces reasoning input and no durable record — the strongest write gate in the atlas, available because the memory is a procedure. `generative-agents` scores every incoming memory for importance at write time and uses that score to schedule consolidation, rather than capturing indiscriminately and compacting on a timer.

### Consolidation

`honcho`, `hindsight`, `mastra-observational-memory`, and `verel` have the strongest visible consolidation stories. Honcho derives working representations from event streams. Hindsight creates/updates observations with source IDs and proof counts. Mastra reflects growing observation logs and can prepare the result asynchronously before activation. Verel clusters failures, induces candidate design rules and schemas, then requires promotion gates for verification. `agentmemory` separately consolidates important observations into versioned memories and optional semantic/procedural layers. `tencentdb-agent-memory` compiles L1 records into scene files and changed scenes into a persona.

`mem0` V3 is intentionally more append-oriented; consolidation is mostly dedupe and entity linking in the OSS path. `mempalace` consolidates operationally through dedup, closets, halls, tunnels, graph layers, and repair paths rather than by rewriting memories into summaries. `swafra` has no real consolidation worker or correction policy: ingestion adds cross-source edges, and a `superseded_by` loop exists, but old same-source chunks are removed before that loop can see them. `llm-wiki-memory` has a substantial opt-in, brain-only pipeline: per-leaf similarity clusters, hash/lesson-key/cosine dedup, optional LLM merge, deterministic staleness flags, optional LLM refresh, orphan archive, archived-body compression, cache pruning, and index rebuild. `rainbox` consolidates through claim supersession, rejection, expiry, profile selection, and eval/feedback loops rather than through background summarization. `letta` separates core and archival memory but does not make consolidation the central visible mechanism in the inspected files. `langmem` provides reflection hooks rather than a fixed consolidation policy. `engram` keeps a pragmatic local model: update topic keys, count duplicates, surface conflicts.

`generative-agents` is the origin of the reflection loop that several systems
here descend from, and its trigger is still the most elegant: a countdown seeded
with `importance_trigger_max` is decremented by each new memory's poignancy, so
reflection fires on accumulated significance rather than on elapsed time, token
count, or message count. Compare `mastra-observational-memory`, which triggers on
token thresholds, and `claude-mem`, which triggers on lifecycle hooks — both are
proxies for "enough has happened" that the original measured directly. Its
weakness is that the budget is denominated in one-shot LLM importance judgments,
and its reflections are stored in the same undifferentiated pool as observations,
so reflections of reflections can drift with no visible boundary.

`moltis` adds a fifth instance of a guard that is now unmistakably a general
requirement: it exports session transcripts into its corpus only after
**sanitizing** them, joining `openclaw`'s envelope stripping, `holographic`'s
compaction-summary exclusion, `nanobot`'s internal-session filter, and
`cowagent`'s distillation rules. Any system that both generates text and
captures text will eventually capture its own.

Four systems in the atlas now call consolidation **dreaming**, arrived at
independently: `magic-context`'s dreamer subagent, `nanobot`'s Dream pass,
`cowagent`'s Deep Dream, and — under a different name for the same idea —
`metaclaw`'s replay. The convergence is not only nominal. All four run offline
on a schedule, read accumulated raw material, and write back a smaller, more
coherent durable layer; three of the four also emit a written record of what the
pass decided (a dream diary, a replay report, a delta-grounded commit). The
metaphor appears to be tracking a real architectural category: consolidation as a
separate, slower, auditable process rather than a step in the write path.

`magic-context` adds a consolidation trigger no other system here uses: its
dreamer subagent fires at threshold pressure **or at git commit boundaries**, on
the reasoning that a commit is the moment a coding agent's work becomes durable
and therefore the right moment to reconcile memory against the repository. The
same run verifies, maps, classifies, promotes primers, and sweeps orphans, under
a lease so two runs cannot overlap.

`redis-agent-memory-server` has the most careful consolidation guard in the
atlas: hash, ID, and semantic dedupe are separate passes, and the semantic path
runs `_semantic_merge_group_is_cohesive` before an LLM is allowed to collapse a
cluster — an explicit test that "similar" really is "same" before merging.
`byterover` approaches the same risk from the document side, diffing existing
against proposed content and counting only what a rewrite would delete.
`hermes-agent` is the outlier: consolidation is neither background nor
automatic, but a synchronous obligation handed to the model when a write would
exceed the character budget.

Cognee's `memify`/`improve` pipelines enrich an existing graph, while its
session path bridges hot entries into permanent memory asynchronously.
Claude-Mem compresses batches into observations and session summaries but does
not merge them into a verified long-term belief model. A-MEM's
`consolidate_memories()` is only a reindex pass, not semantic consolidation.

### Retrieval

The repeated successful pattern is hybrid retrieval:

- semantic/vector search where embeddings exist;
- lexical/BM25/FTS for exact terms and identifiers;
- metadata filters for scope;
- reranking or rank fusion when quality matters.

`mem0` combines semantic, keyword, entity boost, and optional rerank. `hindsight` runs semantic, BM25, graph, and temporal arms, then uses task-specific fusion and cross-encoder reranking. `graphiti` searches edges, nodes, episodes, and communities with BM25, cosine, and BFS plus configurable RRF/MMR/cross-encoder recipes. `cognee` exposes lexical chunks, vectors, graph, triplet, summary, temporal, and hybrid modes, but the result contracts differ enough that each route needs separate evaluation. `basic-memory` fuses FTS5/tsvector with optional semantic chunks. `memos` can run vector or graph/BM25/reranker/reasoner pipelines depending on the mounted cube. `honcho` blends semantic, recent, and most-derived observations. `engram` uses FTS5 and topic keys. `mempalace` combines direct drawer vector search, BM25, metadata, closet boosts, neighbor expansion, and fallback paths. `swafra` uses compact but uncalibrated hybrid/graph fusion. `llm-wiki-memory` combines frontmatter prefilters, embeddings or lexical hashes, priority, and locality. `rainbox` hard-filters then blends vector, full-text, and entity signals. `verel` adds trust and confidence into ranking. `agentmemory` fuses BM25, vector, and graph arms with weighted RRF and per-session diversity. `tencentdb-agent-memory` fuses FTS and vector results with RRF or uses native Tencent VectorDB hybrid search. `claude-mem` selects Chroma semantic search for ordinary text queries and reserves metadata/semantic intersection for file lookup. `metaclaw` is the only system that treats its own ranking parameters as
learnable: retrieval mode, injected-unit cap, token budget, and weights live in a
`MemoryPolicyState` that is replayed against past turns and replaced only on
non-regression. `genericagent` has no ranker at all — a ≤30-line index of
"existence pointers" lets the model recognize that knowledge exists and open the
file itself, which is the cheapest retrieval architecture here and fails silently
when a trigger word is missing. `nanobot` likewise has no retrieval: its durable
files are small enough to always inject. `cowagent` pairs vector and FTS5 search
over chunked files while injecting `MEMORY.md` wholesale.

`waku-agent` inverts the question everyone else asks. Rather than ranking
better, it decides per turn whether to retrieve at all, and its stated reason is
not cost but quality: irrelevant memory in the prompt bends the answer. Nothing
else in the atlas can abstain.

`loongflow` breaks a different assumption: every other system here ranks
deterministically and takes the top *k*. Its evolutionary memory selects a
remembered solution by **Boltzmann sampling over scores**, at a temperature set
by `_adaptive_temperature_by_diversity` from a sampled measure of how varied the
stored population currently is — blending in 20% of the previous temperature so
the control signal does not oscillate. A converged population gets a higher
temperature and flatter selection, which readmits weaker solutions and restores
variety. This is only defensible because recall there feeds exploration rather
than belief; asked the same question twice it may answer differently, which is
the correct trade for a search loop and the wrong one for facts about a user.

`hipporag` is the one system here that does not rank at all in the usual sense: it seeds a personalization vector from query-linked entities plus a weak dense prior, then reads relevance off a Personalized PageRank diffusion across the whole graph. `generative-agents` established the multi-signal shape everything else refines — normalized recency, relevance, and importance combined in a weighted sum — though the specific weights (`gw = [0.5, 3, 2]`, with two earlier settings left commented out) are hand-tuned with no ablation in the repository, and its recency decays by chronological *position* rather than elapsed time. `voyager` retrieves top-5 by vector similarity over generated descriptions and returns executable code, with scores computed and then discarded so there is no relevance threshold. `openviking` runs directory-recursive dense plus sparse retrieval with level filters, per-type quotas, optional reranking, and a hotness blend. `redis-agent-memory-server` pairs vector search with a recency reranker using separate half-lives for last access and creation. `holographic` fuses FTS5, Jaccard, and HRR cosine, then multiplies by trust — and silently reweights to lexical-only when NumPy is absent while still reporting itself as available. `openclaw`'s reference backend is vector-only, which sits awkwardly with a category set dominated by preferences, entities, and decisions. `a-mem` is vector-only despite hybrid wording. `mastra-observational-memory` is the deliberate exception: its primary path is sequential observations plus a recent raw tail, with semantic observation retrieval optional.

### Context Injection

`letta` and `mastra-observational-memory` have the deepest runtime prompt integration. Mastra removes observed raw messages, injects active observations as system context, retains a recent tail, and adds a continuation reminder. `claude-mem` automatically renders a project-scoped chronological timeline, showing only a bounded subset of observations in full. `rainbox` injects an operator profile block and hybrid memory context and records what was injected. `verel` has the safest visible recall renderer: recalled memory is token-budgeted and fenced as untrusted data. `mempalace` has a four-layer stack. `basic-memory` builds graph context through MCP while leaving final prompt placement to the client. `agentmemory` assembles pinned items, profiles, lessons, summaries, and observations within a token budget; its smart search separately supports compact-first expansion. `tencentdb-agent-memory` separates dynamic L1 recall from stable scene/persona context and adds navigable short-term offload maps. `cognee`, `graphiti`, `hindsight`, and `memos` return structured recall/context to integrations. `swafra` exposes unbounded `get_context`; `llm-wiki-memory` injects session work context; `supermemory` emits profile text; `engram` has MCP context tools; `honcho` exposes working representations. A-MEM leaves injection entirely to its caller.

`hermes-agent` takes the most distinctive position in this set: curated memory is rendered into the system prompt **once, at session start, as a frozen snapshot**, and mid-session writes deliberately do not update it, so the provider's prefix cache survives the whole session. That choice is economic rather than epistemic, but it drives a real safety decision — because a poisoned entry would persist for the entire session and beyond, Hermes scans memory content against its broadest threat-pattern set at *write* time. This is the mirror image of Verel's and RainBox's read-time fencing, and the trade is instructive: write-time filtering is cheaper and cache-friendly but is a denylist, while read-time fencing costs tokens every turn and does not depend on pattern coverage. `holographic` does neither, injecting its top five stored facts into the prompt unfenced.

### Correction

This is where systems diverge sharply.

`verel` and `rainbox` have the strongest visible epistemic correction semantics in this set. `verel` has explicit trust states and rejected tombstones. `rainbox` has governed atomic correction, conflict detection, and tombstones that prevent model-write laundering. `engram` has conflict candidates and judgment tools. `mempalace`, `llm-wiki-memory`, `letta`, `mem0`, `honcho`, `supermemory`, and `langmem` expose increasingly operational forms of update/supersession without the same trust model.

Graphiti closes a fact's validity interval and retains history, which is the strongest temporal correction model here, but it does not mark claims verified/rejected. Hindsight rewrites or merges observations while retaining source/history fields. Basic Memory makes correction a human-readable file edit followed by transactional reindexing. Mastra replaces only the observation range covered by a reflection. MemOS correction varies by module and therefore lacks one consistent semantic contract.

`agentmemory` versions similar memories, but the Jaccard threshold can silently
supersede a conflict without an explicit judgment. `tencentdb-agent-memory`
offers internal merge/delete paths and editable generated files, but no
first-class agent/user correction or forget operation.

`magic-context` introduces a correction mechanism the atlas has not seen before:
memories are **re-verified against the artifacts they describe**. Each memory is
mapped to backing files and carries its own `verified_at`; when git reports a
committed change, an uncommitted edit, or a deletion touching a mapped file since
that memory's last verification, the memory re-enters verify scope. Lifecycle
state (`active|permanent|archived`) and verification state
(`unverified|verified|stale|flagged`) are separate columns, which is the split
Verel argues for and most systems collapse. The design is also explicit about its
own limits: file-independent memories are excluded from verification entirely and
handed to curation and age decay, because they "describe external behavior and
cannot be checked against local code". Its remaining gap is the familiar one —
supersession without a rejected-value tombstone, so an archived memory can be
re-derived from retained history.

The six systems added from the Hermes/OpenClaw ecosystem are uniformly weak
here, and usefully so: none of `holographic`, `hermes-agent`, `openviking`,
`redis-agent-memory-server`, `byterover`, or `openclaw` has a rejected-value
tombstone, so in every one of them a corrected or deleted memory can be
re-derived from retained material with nothing to stop it. `byterover` is the
partial exception in an unexpected place — its `detectStructuralLoss` /
`resolveStructuralLoss` pair is the only mechanism in the atlas that guards a
*rewrite* rather than a claim, counting exactly what an LLM curation pass would
delete and merging the loss back in. `holographic` inverts the usual failure:
its `contradict` action surfaces contradictions as an ordinary query, but only
reports them, with no supersession or review workflow attached, and its docstring
claim that "no other memory system does this" is not accurate within this atlas.

A specification for measuring any of this — the shapes a contradiction can take, and the four things worth scoring separately — is in [the contradiction test](../benchmarks/#contradiction-test).

`memora` contributes the one procedural idea this section has been missing. Its
supersession pass runs in three phases — candidate pairs by embedding
similarity, LLM classification, then edge creation — and the mutating phase is
governed by `dry_run: bool = True`. **Reporting is the default; changing memory
is opt-in.** Every other correction mechanism here acts immediately, so an
operator learns the blast radius of a sweep only afterwards. Memora also
classifies each pair against a defined vocabulary — `a_supersedes_b`,
`b_supersedes_a`, `duplicate`, `related`, `contradicts`, `neither` — rather than
thresholding similarity, presents the pair neutrally as A and B so the model
chooses the direction rather than confirming an assumed one, and writes
`contradicts` as an **edge between two named memories** instead of a flag on one
row, which makes it queryable in a way Gini's `conflicted` status is not. The
gap is the usual one: supersession hides a memory from retrieval without
recording the rejected value, and this is a system that ingests documents and
images, so re-ingestion is a realistic path back.

Cognee can forget and rebuild derived projections from retained source, but its
ontology-valid, source-attributed graph facts still lack candidate/rejected
epistemic state. Claude-Mem offers exact deletion and feedback but no durable
rejection mechanism preventing an observation from being regenerated. A-MEM
mutates neighboring note metadata directly and has no correction chain.

The gap is visible from outside this atlas too. TeleAI's
[Awesome-Agent-Memory](https://github.com/TeleAI-UAGI/Awesome-Agent-Memory)
survey runs to about 1,500 lines across seventy sections and covers mem0, Letta,
Zep, Graphiti, Cognee, MemOS, and HippoRAG — every widely-cited system, and all
of them reviewed here. It does not list `verel` or `rainbox`, the only two
systems in this atlas that carry a rejected-value tombstone. That is not a
criticism of the survey; those two are small and obscure. It does mean
correction-focused memory is under-surveyed as well as under-built: a reader
working from the standard reading list would not encounter the mechanism at all.

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
- `agentmemory`: explicit forget, TTL/retention, and search-index cleanup.
- `tencentdb-agent-memory`: internal cleanup and record deletion, but no
  first-class user-facing forget tool.
- `cognee`: exact item, dataset, all-user, or memory-only deletion across source
  and projection stores.
- `claude-mem`: exact canonical-row deletion coupled to cloud tombstone
  enqueue; synchronized deletes fail closed when replication identity is
  unavailable.
- `a-mem`: exact local delete, but incoming links are not cleaned and the
  dictionary/Chroma mutation is not atomic.
- `holographic`: exact `remove`, but the practical forgetting mechanism is
  feedback — three unhelpful ratings drop a fact below the default `min_trust`
  floor of 0.3, making it permanently unreachable with no tombstone and no
  record that suppression occurred.
- `hermes-agent`: substring-addressed `remove` plus budget-driven eviction the
  model performs under pressure; nothing logs what was dropped.
- `openviking`: hotness decays reachability on a single seven-day half-life for
  every memory kind.
- `redis-agent-memory-server`: the most developed policy in the atlas —
  `select_ids_for_forgetting` combines TTL and inactivity so a recently-used
  memory survives its nominal age unless it passes a hard-age multiple, honours
  pinning and per-type allowlists, and prunes to a budget by a recency composite
  with separate half-lives for last access and creation.
- `byterover`: `maxMemories` cap with no eviction policy visible in the
  inspected modules.
- `openclaw`: exact agent-scoped delete, undermined by auto-capture, which can
  restore the same content from a later matching message.

- `magic-context`: archive plus `supersededByMemoryId` and `mergedFrom` lineage,
  with age decay owning memories that cannot be verified; no tombstone.
- `pi`: no memory to forget; deleting a session removes its JSONL file.
- `metaclaw`: `superseded_by` lineage plus `expires_at` TTL; `archived` status,
  no rejected state.
- `nanobot`: Dream edits durable files surgically under git; history is bounded
  at 1,000 entries, dropping oldest processed entries without discarding pending
  Dream input.
- `cowagent`: distillation prunes on a stated rule set, with recency winning
  conflicts and no tombstone.
- `genericagent`: forgetting is constrained by policy — verified configs,
  pitfall guides, and critical paths must never be dropped during garbage
  collection, only compressed or migrated to a deeper layer.

Semantic forgetting is an antipattern unless there is explicit user review or exact ID targeting.

Deletion is also where pluggable memory breaks down. Both host runtimes in the atlas — `hermes-agent` and `openclaw` — define a memory-provider contract with **no deletion hook and no scope parameter**, so a user's "forget that" has no defined path into whatever backend is mounted. `holographic` shows the resulting hazard concretely: it mirrors the host's built-in memory additions into its own store but implements only the `add` action, so removing an entry from `MEMORY.md` leaves the mirrored copy behind indefinitely.

### Cross-Session and Cross-Agent Persistence

`honcho` has the richest multi-actor model: workspace, peer, session, collections, and derived representations. Cognee authorizes datasets per user and can isolate supported backend stores per user/dataset. Claude-Mem scopes local reads by project/worktree, session, and platform source, while its newer server model adds teams and API keys. Hindsight isolates memory banks and database schemas. Graphiti uses `group_id`. Mastra scopes observations to a thread or resource. MemOS registers cubes to users. Basic Memory uses project/workspace/tenant boundaries with per-project local/cloud routing. `agentmemory` supports project/session keys and an opt-in isolated agent mode, but defaults to shared agent scope. TencentDB records session identity but does not turn it into a general tenant boundary; one persona per data directory is especially important operationally. `supermemory`, `mem0`, `rainbox`, `engram`, `mempalace`, `llm-wiki-memory`, `verel`, `letta`, and `langmem` each expose explicit boundaries. `openviking` carries tenant and permission filtering into every retrieval call and physically separates memory about the user from memory about a peer under `peers/<peer_id>`. `redis-agent-memory-server` scopes by namespace, user, and session behind auth. `openclaw` has a single `agentId` axis but defends it unusually well, composing scope and user filter into one predicate "so scope cannot be lost" and scoping deletes the same way. `hermes-agent` isolates by profile but has no project or room boundary within one. `magic-context` has a three-level lattice — `project`, `ecosystem`, `universe` — plus a `shareable` flag governing what may cross a boundary, with project identity resolved to the git root and a rekey map for when a repository moves. `pi` has no scope because it has no memory. `byterover` scopes only by storage directory, and `holographic` has no scope at all — it describes itself as a single-user store, with `category` serving as partitioning rather than access control. A-MEM, Swafra, and Holographic remain the outliers with effectively global local corpora.

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
- `agentmemory`: `src/types.ts` and state scopes in `src/state/schema.ts`.
- `tencentdb-agent-memory`: `src/core/record/l1-writer.ts`, `src/core/store/types.ts`, and `src/core/store/sqlite.ts`.
- `cognee`: `cognee/infrastructure/engine/models/DataPoint.py`, graph edge/triplet models, and relational dataset/data/session models.
- `claude-mem`: canonical tables and migrations in `src/services/sqlite/SessionStore.ts`; future server model in `src/storage/sqlite/schema.ts`.
- `a-mem`: `MemoryNote` in `agentic_memory/memory_system.py`.
- `hipporag`: graph and node construction in `src/hipporag/HippoRAG.py`; config defaults in `utils/config_utils.py`.
- `magic-context`: `packages/plugin/src/features/magic-context/memory/types.ts`; schema in `migrations.ts`.
- `metaclaw`: `metaclaw/memory/models.py` (`MemoryUnit`, `MemoryType`, `MemoryStatus`); policy in `policy_store.py`.
- `nanobot`: no schema; durable files plus `history.jsonl` lines in `nanobot/agent/memory.py`.
- `cowagent`: `chunks` table in `agent/memory/storage.py`.
- `genericagent`: no schema; layer contract in `memory/memory_management_sop.md`.
- `pi`: session entry types in `packages/agent/src/harness/types.ts`; no memory record exists.
- `voyager`: `skills[name] = {code, description}` in `voyager/agents/skill.py`.
- `generative-agents`: `ConceptNode` in `persona/memory_structures/associative_memory.py`; weights in `scratch.py`.
- `holographic`: `_SCHEMA` in `plugins/memory/holographic/store.py`; HRR encoding in `holographic.py`.
- `hermes-agent`: `MemoryStore` in `tools/memory_tool.py`; provider contract in `agent/memory_provider.py`.
- `openviking`: `MemoryData` / `MemoryTypeSchema` in `openviking/session/memory/dataclass.py`; level field in `openviking/storage/collection_schemas.py`.
- `redis-agent-memory-server`: `V0/agent_memory_server/models.py`.
- `byterover`: `src/agent/core/domain/memory/types.ts`; `ContextData` in `src/server/core/domain/knowledge/markdown-writer.ts`.
- `openclaw`: `MemoryEntry` in `extensions/memory-lancedb/lancedb-store.ts`; categories in `config.ts`.

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
- `agentmemory`: `src/functions/observe.ts` and `src/functions/remember.ts`.
- `tencentdb-agent-memory`: `src/core/hooks/auto-capture.ts`, `src/core/record/l1-extractor.ts`, `l1-dedup.ts`, and `l1-writer.ts`.
- `cognee`: `cognee/api/v1/remember/remember.py`, `add/add.py`, and `cognify/cognify.py`.
- `claude-mem`: hook adapters, `SessionMessageBuffer.ts`, and `worker/agents/ResponseProcessor.ts`.
- `a-mem`: `AgenticMemorySystem.add_note()` and `process_memory()` in `agentic_memory/memory_system.py`.
- `hipporag`: `index()`, `add_fact_edges()`, `add_passage_edges()`, `add_synonymy_edges()` in `src/hipporag/HippoRAG.py`.
- `magic-context`: `memory/promotion.ts` (`promoteSessionFactsDurable`, `embedPromotedFacts`).
- `metaclaw`: `metaclaw/memory/manager.py` and `consolidator.py`.
- `nanobot`: Consolidator append plus Dream's surgical edits in `nanobot/agent/memory.py`.
- `cowagent`: `agent/memory/summarizer.py` (daily summary and Deep Dream distillation).
- `genericagent`: policy-gated writes per `memory/memory_management_sop.md`.
- `pi`: append to the session tree; `harness/compaction/compaction.ts` for range replacement.
- `voyager`: `SkillManager.add_new_skill()` in `voyager/agents/skill.py`, gated by `if info["success"]` in `voyager/voyager.py`.
- `generative-agents`: `add_event()`, `add_thought()`, `add_chat()` in `associative_memory.py`.
- `holographic`: `add_fact()` and `_rebuild_bank()` in `plugins/memory/holographic/store.py`; `_auto_extract_facts()` in `__init__.py`.
- `hermes-agent`: `MemoryStore.add/replace/remove` and `_apply_write_gate()` in `tools/memory_tool.py`.
- `openviking`: `openviking/session/memory/extract_loop.py`, `memory_updater.py`, and `memory_isolation_handler.py`.
- `redis-agent-memory-server`: `promote_working_memory_to_long_term()` and the dedupe chain in `V0/agent_memory_server/long_term_memory.py`.
- `byterover`: `MemoryDeduplicator.deduplicate()` in `src/agent/infra/memory/memory-deduplicator.ts`; `resolveStructuralLoss()` in `knowledge/conflict-resolver.ts`.
- `openclaw`: `sanitizeForMemoryCapture()` in `extensions/memory-lancedb/memory-capture-sanitization.ts`; `store()` in `lancedb-store.ts`.

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
- `agentmemory`: `src/functions/search.ts`, `src/state/hybrid-search.ts`, and `src/functions/smart-search.ts`.
- `tencentdb-agent-memory`: `src/core/tools/memory-search.ts`, `conversation-search.ts`, and store search methods.
- `cognee`: `cognee/api/v1/recall/recall.py`, `modules/search/methods/search.py`, and retrievers under `modules/retrieval/`.
- `claude-mem`: `worker/search/SearchOrchestrator.ts`, Chroma/SQLite strategies, and `services/sqlite/SessionSearch.ts`.
- `a-mem`: `search_agentic()` and Chroma wrappers in `agentic_memory/retrievers.py`.
- `hipporag`: `graph_search_with_fact_entities()` and `run_ppr()` in `src/hipporag/HippoRAG.py`.
- `magic-context`: `search.ts` with `matchType` semantic/fts/hybrid, plus `message-index.ts`.
- `metaclaw`: `metaclaw/memory/retriever.py` under the live `MemoryPolicyState`.
- `nanobot`: none; durable files are always in context.
- `cowagent`: vector and FTS5 search in `agent/memory/storage.py`.
- `genericagent`: L1 index lookup then file open; no ranker.
- `pi`: none; context is the session tree walked to root.
- `voyager`: `retrieve_skills()` in `voyager/agents/skill.py`.
- `generative-agents`: `new_retrieve()` and the extractors in `persona/cognitive_modules/retrieve.py`.
- `holographic`: `FactRetriever.search/probe/related/reason/contradict` in `plugins/memory/holographic/retrieval.py`.
- `hermes-agent`: FTS5 session search in `hermes_state.py`; curated memory needs no retrieval.
- `openviking`: `openviking/retrieve/hierarchical_retriever.py`, `type_quota_recall.py`, `memory_lifecycle.py`.
- `redis-agent-memory-server`: `search_long_term_memories()` and `rerank_with_recency` in `V0/agent_memory_server/long_term_memory.py`.
- `byterover`: `ListMemoriesOptions` filtering in `src/agent/infra/memory/memory-manager.ts`.
- `openclaw`: `scopedPredicate()` and `query()` in `extensions/memory-lancedb/lancedb-store.ts`; `normalizeRecallQuery()` in `memory-policy.ts`.

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
- `agentmemory`: token budgeting in `src/functions/context.ts`; compact expansion in `src/functions/smart-search.ts`.
- `tencentdb-agent-memory`: `src/core/hooks/auto-recall.ts` and symbolic offload assembly in `src/offload/index.ts`.
- `cognee`: structured output from `recall`; final prompt placement remains integration-owned.
- `claude-mem`: `src/services/context/ContextBuilder.ts` and `ObservationCompiler.ts`.
- `a-mem`: caller-owned; no bounded context assembler.
- `hipporag`: ranked passages returned to the caller; QA assembly in `rag_qa()`.
- `magic-context`: `<session-history>` and primer injection via the Pi context handler; `primer-clustering.ts`.
- `metaclaw`: injection bounded by policy `max_injected_units` and `max_injected_tokens`.
- `nanobot`: `SOUL.md`, `USER.md`, `memory/MEMORY.md` injected; Dream prompt capped at 8,000 chars per file.
- `cowagent`: `MEMORY.md` injected into every conversation.
- `genericagent`: L1 `global_mem_insight.txt`, hard-capped at 30 lines.
- `pi`: `buildSessionContext()` plus `core/resource-loader.ts` for AGENTS.md/SYSTEM.md.
- `voyager`: retrieved code plus the unbounded `programs` property injected into the action prompt.
- `generative-agents`: top-30 node descriptions, no token budget.
- `holographic`: `prefetch()` in `plugins/memory/holographic/__init__.py` — top-5, unfenced.
- `hermes-agent`: `format_for_system_prompt()` / `_render_block()` in `tools/memory_tool.py`, rendered once per session.
- `openviking`: `QueryResult` from the hierarchical retriever; final placement is integration-owned.
- `redis-agent-memory-server`: `V0/agent_memory_server/summary_views.py` and API response shaping.
- `byterover`: caller-owned after listing.
- `openclaw`: auto-recall assembly in `extensions/memory-lancedb/index.ts`.

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
- `agentmemory`: consolidation, graph extraction, decay, and index maintenance.
- `tencentdb-agent-memory`: deferred embeddings, scene/persona generation, task draining, and `src/offload/reclaimer.ts`.
- `cognee`: pipeline executor, `memify`, session improvement, cognify rollback, and stale-run recovery.
- `claude-mem`: durable pending queue, observer providers, Chroma/cloud sync, and backfill/repair.
- `a-mem`: no worker; “consolidation” is synchronous reindexing.
- `hipporag`: none; OpenIE is cacheable and resumable but runs inline.
- `magic-context`: the dreamer — `task-scheduler.ts`, `cron.ts`, `lease.ts`, `verify.ts`, `map-memories.ts`.
- `metaclaw`: `self_upgrade.py`, `upgrade_worker.py`, `replay.py`, `policy_optimizer.py`.
- `nanobot`: Dream on cron, gated by `DreamRunProgress`.
- `cowagent`: 23:55 daily summary then Deep Dream distillation.
- `genericagent`: 12-hour L4 archive cron in `reflect/scheduler.py`.
- `pi`: compaction and branch summarization only.
- `voyager`: none; the rollout loop is synchronous.
- `generative-agents`: reflection fires inline when the poignancy countdown crosses zero.
- `holographic`: none; `_rebuild_bank()` runs synchronously on every write.
- `hermes-agent`: none for curated memory; a mounted provider may run its own.
- `openviking`: extraction loop, streaming updater, reindex executor, hotness maintenance.
- `redis-agent-memory-server`: debounced trailing extraction, compaction, dedupe, and forgetting sweeps via `docket_tasks.py`.
- `byterover`: bounded-concurrency LLM deduplication.
- `openclaw`: auto-capture cursor advancement; no separate worker.

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
- `agentmemory`: MCP, HTTP, CLI, lifecycle hooks, and the iii function registry.
- `tencentdb-agent-memory`: OpenClaw hooks and two search tools plus the Hermes gateway; no MCP surface was found.
- `cognee`: Python SDK, REST server, CLI, MCP server, and migration/export APIs.
- `claude-mem`: coding-agent hooks, worker HTTP API, local/server MCP, and UI.
- `a-mem`: direct Python API only.
- `hipporag`: Python library, `main.py`, and `examples/`; no MCP or service.
- `magic-context`: Pi `ExtensionAPI` adapter, an OpenCode adapter, a CLI, and a dashboard.
- `metaclaw`: OpenClaw plugin (`openclaw-metaclaw-memory/OPENCLAW_PLUGIN_SPEC.md`) with a sidecar manager.
- `nanobot`: internal, with WebUI and cron.
- `cowagent`: `agent/tools/memory/` plus `service.py`.
- `genericagent`: internal; `reflect/` drives autonomy.
- `pi`: CLI, TUI, SDK, server, and 20+ extension events — none memory-shaped.
- `voyager`: none; research rollout loop.
- `generative-agents`: none; simulation with a Django frontend.
- `holographic`: `fact_store` and `fact_feedback` tools through the Hermes `MemoryProvider` ABC.
- `hermes-agent`: the `memory` tool, `agent/memory_provider.py` for third-party backends, and `hermes mcp serve`.
- `openviking`: Python SDK, REST server, CLI, web studio, npm package, and Hermes/OpenClaw provider adapters.
- `redis-agent-memory-server`: REST (`api.py`), MCP (`mcp.py`), CLI, and generated SDK clients.
- `byterover`: `brv` CLI and MCP; Hermes provider adapter.
- `openclaw`: `extensions/memory-core/` plugin contract, memory tools, CLI, and doctor contracts.

### Evals/Tests

What these harnesses do and do not measure — and why a bad benchmark score is
often weak evidence — is covered separately in
[benchmarking agent memory](../benchmarks/).

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
- `agentmemory`: broad function/state/hook tests; documented retrieval-only LongMemEval-S and small synthetic coding-agent-life benchmarks.
- `tencentdb-agent-memory`: six visible TypeScript/Python test files, none covering the central L1/L2/L3 lifecycle; README benchmark claims lack committed harness/results here.
- `cognee`: broad unit/integration/backend/permission/recovery tests; committed preliminary BEAM report with a held-out 100K result and exploratory in-sample-routed 10M result.
- `claude-mem`: 237 TypeScript test files spanning hooks, queues, privacy, migrations, Chroma/cloud sync, and server paths; no committed memory-quality benchmark found.
- `a-mem`: small CRUD/retriever test suite; paper reproduction and benchmark artifacts live in a separate repository.
- `hipporag`: thin unit tests (`tests/test_bedrock_mantle.py`, `tests/integration/`) beside a well-developed `reproduce/` benchmark tree; no committed result artifacts.
- `magic-context`: 473 test files and roughly 131,000 lines of tests, including per-version migration suites and named CAS-race tests; no retrieval or verification-precision benchmark.
- `atomic-agent`: the most developed evaluation *process* in the atlas — a design plan with §14 acceptance criteria (`MEMORY_FABRIC_V2.md`), an implementation ledger recording which phases landed (`MEMORY_FABRIC_V2.5.md`), and a campaign whose stated purpose is "is memory actually useful" with numbered experiments E9–E12 behind `npm run eval:memory:v25`. All three v2.5 features ship `default: false` pending its verdict. No scored artifacts were found committed.
- `mateclaw`: tests under `src/test/java/vip/mate/memory/`; no memory benchmark. Its decorator chain already instruments every provider, so per-backend comparison would be straightforward and does not appear to have been done.
- `open-cowork`: `memory-eval-harness.ts` defines eval cases as a session plus queries carrying **both `expectedHits` and `forbiddenHits`**, scores the assembled prompt prefix rather than raw retrieval output, combines a deterministic containment score with an LLM judge, and writes reports with a run id and artifact directory. This is the most complete memory benchmark shape in the atlas; no scored results were found committed at this commit.
- `gini-agent`: per-module and integration tests, including an assertion that a follow-up task records recalled units; no memory-quality benchmark, despite a recall implementation that cites specific published equations.
- `moltis`: contract tests compiled under `#[cfg(test)]`; no memory benchmark.
- `mercury-agent`: `user-memory.test.ts`; no memory benchmark.
- `metaclaw`: committed `benchmark/data/metaclaw-bench*` harnesses with eval fixtures, plus dedicated `run_memory_ablation*.py` scripts — rare in this atlas; no numbers reproduced here.
- `nanobot`: no memory tests located, which is notable given the cursor and failure-gate logic carry most of the correctness.
- `cowagent`: no memory tests or benchmark located.
- `genericagent`: no memory tests or benchmark located; an arXiv report is cited but was not assessed.
- `pi`: an `evals` package and session-harness test utilities; no memory benchmark, because there is no memory.
- `voyager`: no tests for `SkillManager`; evaluation is the paper's Minecraft tech-tree benchmark, which measures task completion rather than memory quality.
- `generative-agents`: no memory tests; evaluation is human believability ratings, and the `gw` retrieval weights have no committed ablation.
- `holographic`: 599 lines across four plugin test files plus 1,662 lines exercising the provider ABC; no retrieval-quality benchmark, and the measured contribution of the HRR arm is unknown.
- `hermes-agent`: memory-tool, write-approval, provider, and backup suites, with several guards citing the issues that produced them; no committed memory-quality benchmark.
- `openviking`: 688 test files, plus committed LoCoMo, LongMemEval, tau2, SkillsBench, and vector-DB harnesses with runners for six systems and token accounting — but the published headline numbers live off-repo and no raw result artifacts are committed.
- `redis-agent-memory-server`: roughly 27,000 lines of tests, with dedicated forgetting, extraction, strategy, and contextual-grounding suites; benchmark scaffolding but no published numbers.
- `byterover`: no tests located for the memory or knowledge domain modules, including none for the structural-loss guard that is its best idea.
- `openclaw`: test lines far exceed implementation — 4,497 for the LanceDB extension and 2,530 for the memory-core doctor contract; no committed retrieval benchmark.

## 5. Design Patterns That Recur

These recurring moves are also documented as standalone implementation guides in the [memory design pattern library](../patterns/). The library covers correction, provenance, trust, retrieval, scope, write governance, federation, context assembly, recoverable background work, lifecycle decay, zero-LLM capture, audit history, pluggable memory providers, procedural skills, and gating expensive work.

### Explicit memory mutation surfaces

Repos: strongest in `mem0`, `langmem`, `engram`, `mempalace`, `llm-wiki-memory`, `rainbox`, `letta`, `supermemory`, `verel`, `hindsight`, `graphiti`, `basic-memory`, and `agentmemory`.

The agent, application, or operator explicitly calls a memory operation. This works because it gives the system a narrow interface for durable state changes. It fails when the model forgets to call the tool, calls it with low-quality facts, or treats tool descriptions as policy enforcement. It is not the only capture model in the atlas: Mastra observes automatically at context thresholds, Basic Memory also reconciles direct filesystem edits, and event-driven systems such as Honcho derive memory from ordinary message ingestion.

### Separate hot memory from archival memory

Repos: `letta`, `rainbox`, `honcho`, `supermemory`, `mempalace`, `llm-wiki-memory`, `hindsight`, `mastra-observational-memory`, `memos`, `tencentdb-agent-memory`, partly `mem0` and `agentmemory`.

Hot memory is small and prompt-ready. Archival/document memory is large and retrieved on demand. This works because prompt space is scarce and long-term stores are noisy. It fails when there is no promotion/demotion policy between the layers.

### Evidence first, derived memory second

Pattern guide: [Evidence before belief](../patterns/evidence-before-belief/).

Repos: strongest in `cognee`, `honcho`, `verel`, `mempalace`, `rainbox`, `graphiti`, `hindsight`, `basic-memory`, and `tencentdb-agent-memory`; partly in `claude-mem`, `engram`, `swafra`, `llm-wiki-memory`, `mastra-observational-memory`, and `agentmemory`.

Raw messages, observations, files, drawers, or evidence rows are retained, and derived facts/representations/indexes are computed from them. This works because wrong memories can be audited and recomputed. It fails if the derived layer does not preserve source IDs, if raw stores become too noisy, if evidence excerpts are too thin, or if background derivation makes read consistency surprising.

### Hybrid retrieval

Pattern guide: [Hybrid retrieval fusion](../patterns/hybrid-retrieval-fusion/).

Repos with visible fused lexical/semantic or multi-arm ranking: `mem0`, `honcho`, `mempalace`, `swafra`, `rainbox`, `verel`, `hindsight`, `graphiti`, `basic-memory`, `agentmemory`, `tencentdb-agent-memory`, and configured `memos` pipelines. Supermemory exposes hybrid settings, but the hosted implementation is not visible. Engram's FTS/topic-key retrieval and Letta's separate archival/conversation searches are useful multi-mode retrieval surfaces, not evidence of fused hybrid ranking.

Vector search alone is not enough. Identifiers, names, exact phrases, dates, file paths, and project keys often need lexical search. Hybrid retrieval works because it handles both fuzzy semantic recall and exact lookup. MemPalace adds a useful variant: extracted/indexed "closets" boost drawer ranking but never gate direct evidence retrieval. Swafra is a useful compact example of BM25 + vector + cheap heuristic fusion, but also a warning: ad hoc component normalization and unbounded bonuses make scores hard to interpret. Hybrid retrieval fails when rank fusion is opaque or not evaluated.

Cognee has genuine multi-view hybrid retrievers but also many non-fused modes
with different result contracts. Claude-Mem and A-MEM are naming
counterexamples: ordinary Claude-Mem text search selects semantic rather than
fusing it with FTS, and A-MEM's “hybrid” path is vector-only.

### Scope as a first-class key

Pattern guide: [Scope as a first-class key](../patterns/scope-as-a-first-class-key/).

Repos: most systems; weakest or absent in `a-mem`, `swafra`, and
`tencentdb-agent-memory`, while `agentmemory` requires opt-in isolated agent
mode for its strictest boundary.

Good systems make memory boundaries explicit: user, agent, run, project, workspace, peer, session, space, palace, wing, room, source file, claim scope, sensitivity, scope lattice, namespace. This works because many memory bugs are scope bugs. Swafra's one global corpus shows why a source title is not a scope: two clients or projects can silently retrieve each other's memory. Scope fails when absent or when it is only metadata with no migration, inheritance, access, or conflict policy.

### MCP as a universal adapter

Repos: `engram`, `mempalace`, `swafra`, `llm-wiki-memory`, `supermemory`, `verel`, `hindsight`, `graphiti`, `cognee`, `claude-mem`, `basic-memory`, `agentmemory`, and conceptually similar tool surfaces elsewhere.

MCP is useful because it lets different coding agents and desktop tools use the same memory backend. It fails if the MCP tool descriptions become the only guardrail against bad writes.

### Local SQLite for inspectable memory

Repos: `engram`, `mempalace`, `verel`, `claude-mem`, `basic-memory`, `agentmemory`, and the local backends of `cognee` and `tencentdb-agent-memory`; SQLite also supports history/messages in `mem0`.

SQLite works well for local agent memory: durable, fast, easy to inspect, transaction-friendly, and good enough with FTS5. MemPalace also shows the complementary local pattern: SQLite metadata/KG/FTS plus a local vector store. It fails if a product needs multi-tenant scale, remote sharing, or vector-heavy retrieval without extensions/adapters.

### Flat JSON as a prototype store

Repo: `swafra`.

Three JSON files make the complete state inspectable and keep installation trivial. This is reasonable for a single-process prototype and terrible as implicit production durability: full-file rewrites, no transactions or locks, no indexed access, and cross-file consistency hazards. Treat flat JSON as a demo format or export, not a concurrent memory database.

### Filesystem wiki plus git history

Repo: `llm-wiki-memory`.

Markdown leaves plus generated folder indexes make local memory directly readable, diffable, and recoverable. Git commits can group one logical mutation into an auditable change, while repository-owned mounts provide a simple team-sharing path. This works for small coding-agent corpora where inspectability matters more than query throughput. It fails at large scale, under concurrent collaborative writes, or when deletion must erase prior content rather than leave it in history.

### Recoverable background capture

Repos: strongest in `claude-mem`, `llm-wiki-memory`, and `cognee`; related
checkpoint, deferred-work, and evidence-retention ideas appear in `honcho`,
`mempalace`, `agentmemory`, and `tencentdb-agent-memory`.

Decouple transcript capture from the interactive hook, chunk long inputs, retain failed chunks, write fenced raw fallbacks, and support redistillation. This turns provider failure into delayed processing instead of silent data loss. It fails if the recovery stores themselves leak secrets or if no operator ever reviews/retries accumulated stashes.

### Zero-LLM capture

Pattern guide: [Zero-LLM capture](../patterns/zero-llm-capture/).

Repos: strongest in `agentmemory`, `claude-mem`, `llm-wiki-memory`,
`tencentdb-agent-memory`, and message-first `honcho`; `engram` demonstrates the
small no-extraction baseline.

Persist a scoped event before any model call, make it searchable through exact
keys or lexical metadata, then enrich it asynchronously only when useful. This
keeps provider latency and outages out of the capture path. It fails when raw
capture has no privacy, size, retention, or retrieval policy.

### Decay and reinforcement

Pattern guide: [Decay and reinforcement](../patterns/decay-and-reinforcement/).

Repos: strongest in `verel`; supporting behavior in `agentmemory` and `honcho`;
`swafra` is a counterexample for unconditional age decay.

Let retrieval strength fade or grow without changing epistemic confidence.
This keeps stale operational memory from dominating while protecting durable
truths and correction history. It fails when retrieval itself creates a
self-reinforcing popularity loop or one half-life is applied to every memory
kind.

### Profiles and working representations

Repos: `honcho`, `supermemory`, `letta`, `hindsight`, `mastra-observational-memory`, `agentmemory`, and `tencentdb-agent-memory`.

A low-latency synthesized representation is often more useful than raw top-k memories. This works because agents need compact operating context. It fails when summaries drift, hide uncertainty, or cannot be traced back to evidence.

### Memory governance loop

Repos: strongest in `rainbox`; partly in `verel`.

Memory quality improves when memory use is observable and connected to review, feedback, and evals. RainBox's `RetrievalEvent`, `FeedbackEvent`, `/memory` review page, and eval loop show a practical product pattern. This fails if telemetry is mistaken for truth: a downvote is a review signal, not proof that a memory is false.

### Bi-temporal fact validity

Pattern guide: [Bi-temporal fact validity](../patterns/bi-temporal-fact-validity/).

Repos: strongest in `graphiti`; supporting temporal/event-time ideas in `hindsight`.

Record both when a fact was valid in the represented world and when the system learned or expired it. This preserves historical truth during correction and backfill. It fails when LLM-extracted dates or invalidation decisions are treated as certain.

### Pluggable memory provider

Pattern guide: [Pluggable memory provider](../patterns/pluggable-memory-provider/).

Repos: `hermes-agent` and `openclaw` define the contracts; `holographic`,
`openviking`, `byterover`, `redis-agent-memory-server`, `tencentdb-agent-memory`,
`honcho`, `mem0`, `hindsight`, and `supermemory` are mounted through them.

A host runtime exposes one memory interface and lets users mount a backend by
configuration. This works because no single memory model suits a laptop and a
multi-tenant product at once, and because providers reach many hosts by
implementing one contract. It fails at the boundary: neither contract inspected
here carries a scope parameter or a deletion hook, so host-level erasure cannot
reach a mounted store, trust state cannot cross, and mirroring host writes into a
provider creates duplicates with independent lifecycles.

### Skills as procedural memory

Pattern guide: [Skills as procedural memory](../patterns/skills-as-procedural-memory/).

Repos: strongest in `voyager`; present without a verification gate in
`hermes-agent`, `openviking`, `memos`, and `agentmemory`; the failure-side
counterpart is `verel`.

Store the executable procedure rather than a description of it, index it by a
generated summary, and gate the write on verified execution. This works because
procedural truth is cheap to establish where actions have observable effects —
"did it run and produce the intended state?" is checkable in a way "is this fact
true?" is not, which is why Voyager's gate is stronger than any judgment-based
gate in the atlas. It fails when success in one context is generalized from a
single run, when retrieval has no score threshold (an irrelevant callable is
worse than an irrelevant fact), when the library has no utility signal to prune
by, and — outside a sandbox — because a skill library is agent-authored code
retrieved by similarity and then executed.

### Promotion gates for the policy, not just the memory

Repo: `metaclaw`; the memory-level analogue is `verel`.

Treat the retrieval configuration as a versioned object that must earn its place.
Generate a bounded set of candidate policies, replay them offline against real
past turns, and promote one only when it fails to regress on several independent
measures over a minimum sample. MetaClaw gates on eight deltas with at least ten
samples and an explicit cap on additional zero-retrieval cases — a guard on the
distribution rather than the mean.

This works because it is the only answer in the atlas to "are our fusion weights
right?", and because it resolves the telemetry-versus-truth tension by tuning
*reachability* and never touching confidence. It fails when the replay metrics
are proxies for usefulness rather than measures of it, and when the gate's own
thresholds are unmeasured constants — both of which are true here.

### Memory policy as a written artifact

Repo: `genericagent`; related operator surfaces in `nanobot` (`prompts/dream.md`)
and `cowagent` (documented distillation rules).

Write the memory rules down where a human can read and edit them, next to the
memory they govern. GenericAgent's axioms — action-verified writes, sanctity of
verified data, no volatile state, minimum sufficient pointer — plus its ROI test
for what earns permanent context, are more legible than most systems' code. It
also supplies the missing justification behind every hard budget in this atlas:
`ROI = (error probability x cost) / per-turn word cost`, with the sharp corollary
that an entry the model would act on unprompted is a permanent tax with zero
return.

It fails on enforcement. Prose rules bind only as far as the model follows them,
nothing audits compliance, and the action-verified axiom leaves no record of the
tool call that justified a write.

### Gate the expensive path

Pattern guide: [Gate the expensive path](../patterns/gate-the-expensive-path/).

Repos: strongest in `waku-agent`; also `atomic-agent`, `gini-agent`,
`hermes-agent`, `redis-agent-memory-server`, `metaclaw`, `genericagent`.

Put a cheap decision in front of an expensive one. `waku-agent` asks a small
model, per turn, whether the store should be touched at all — because default-on
retrieval is not merely slow, it is worse: irrelevant memory in the prompt bends
the answer. The same call returns the search query, so gating costs one call and
buys two. `gini-agent` shows the cheapest version, letting its temporal channel
participate only when the query contains a temporal expression, and
`atomic-agent` heuristic-gates its query rewriter.

This works because it gives a memory layer the ability to return nothing, which
an unconditional pipeline does not have. It fails in one specific direction: a
wrongly skipped retrieval produces a confident answer missing context nobody
knows is missing, while a wrongly permitted one merely costs a search. Gates must
fail open — `waku-agent` states it in the code, "a stale memory beats a lost one"
— and they must be measured. Nothing in the atlas measures its gate.

### Verify memory against its subject

Repos: `magic-context`; the procedural analogue is `voyager`; contrast the
judgment-based gates in `verel` and `rainbox`.

Where a memory describes something inspectable, do not adjudicate it — check it.
Map each memory to the artifacts it is about, record a per-memory verification
timestamp, and let a change in those artifacts put the memory back in scope.
Magic Context does this against files in a git repository; Voyager does the
procedural version by re-running a skill. This works because it replaces "do I
believe this claim?" with "does reality still agree?", which is enormously
cheaper. It fails for memories with no inspectable subject — Magic Context
excludes them explicitly rather than marking them verified — and it degrades if
the verdict itself is a model call, which it currently is.

The reusable sub-lesson is about watermarks: Magic Context's comments record that
an earlier version used a global commit watermark with all-or-nothing coverage,
and that it was reworked to per-memory timestamps so a timed-out run banks what
it checked. Global watermarks make partial progress worthless.

### Diffusion instead of traversal

Repo: `hipporag`; contrast with BFS traversal in `graphiti` and the graph arm in
`agentmemory`.

Rather than deciding how many hops to walk and in which direction, seed a
personalization vector with query-relevant graph nodes and run Personalized
PageRank over the whole graph. Multi-hop association becomes a property of the
diffusion rather than of a traversal policy, and a weak dense-retrieval prior can
be mixed into the same vector. HippoRAG adds two refinements worth copying: seed
weights divided by the entity's chunk count so hubs do not dominate, and low
damping (0.5) to keep relevance near the query's entities. It fails on cost —
PPR runs over the entire graph per query — and on attribution, since no single
signal explains a ranking.

### Non-destructive entity resolution

Repo: `hipporag`; contrast with `graphiti`.

Link similar entities with weighted edges instead of merging them. Graphiti's own
stated biggest risk is that entity-resolution mistakes reshape a large portion of
the graph; adding a synonymy edge instead means a wrong decision creates a weak
spurious path rather than destroying two identities irreversibly. It fails when
the graph becomes dense enough that diffusion blurs everything together, and it
does not give you a canonical entity to display or key on.

### Bounded prompt memory with in-turn consolidation

Repo: `hermes-agent`; contrast with the unbounded-plus-background-summarization
approach in most of the atlas.

Cap curated memory in characters, inject it as a frozen snapshot at session
start, and refuse any write that would exceed the cap — returning the current
entries and requiring the model to consolidate and retry in the same turn. This
works because prompt cost becomes a static, known quantity and the prefix cache
survives the session. It fails because the model chooses what to discard under
time pressure, with no review and no record of what was dropped.

### Structural-loss guard on generated rewrites

Repo: `byterover`; related range-tracking in `mastra-observational-memory` and
verbatim retention in `mempalace`.

Before an LLM rewrite replaces stored content, parse both versions and count
only what would be **deleted** — ignoring additions so enrichment does not
trigger false positives. Treat any loss as high impact and merge the lost
material back automatically. This is the cheapest countermeasure in the atlas to
summarization silently discarding evidence. It fails if the parse is lossy, or if
the same guard is not applied to every rewrite path — ByteRover itself protects
document curation but not its own LLM memory merge.

### Buffered observation-reflection

Repos: strongest in `mastra-observational-memory`; related consolidation in `hindsight` and `honcho`.

Prepare derived context before the hard prompt threshold, persist the exact source range it covers, and activate it atomically when needed. This removes LLM compression from the critical path. It fails without durable markers, range-aware replacement, recovery, and distributed coordination.

### Rehearse the correction before committing it

Repos: `memora`; related staging in `hermes-agent`.

Any pass that can hide or delete memory in bulk should default to reporting what
it would do. Memora's supersession pipeline takes `dry_run: bool = True`, so a
sweep produces a reviewable list of proposed edges and changes nothing until
mutation is explicitly requested. This costs a keyword argument and turns an
operation with an unknowable blast radius into one an operator can read first.
It also makes the classifier measurable: the dry-run output is exactly the
artifact needed to count how often the pass would have been wrong. It fails if
the preview and the mutating path diverge, or if nobody actually reads the
report — a default that is always overridden is not a safeguard.

### Sample instead of rank, when recall feeds exploration

Repos: `loongflow`; adjacent in `voyager` and `verel`.

Deterministic top-*k* recall has a failure mode nobody else here names: if the
ranking function is slightly wrong, the same wrong memories surface every time
and the alternatives are never seen. LoongFlow's evolutionary memory samples a
remembered solution from a Boltzmann distribution over scores, with the
temperature driven by measured population diversity and bounded on both sides,
so a store that has collapsed toward sameness loosens selection until variety
returns. This is right only where remembered items inform *what to try next*
rather than *what is true* — the same mechanism applied to facts about a user
means the same question can get different answers. It also gives up
reproducibility, and nothing in LoongFlow provides a seed or replay path for
debugging a selection.

## 6. Antipatterns and Failure Modes

### Treating LLM-extracted facts as truth

Most systems extract with an LLM. Without trust state, provenance, and correction semantics, hallucinations become durable. `verel` addresses this directly; `honcho` preserves source events; `mem0`, `langmem`, `cognee`, `claude-mem`, `a-mem`, and `llm-wiki-memory` need stronger promotion guardrails.

`mempalace` is the clearest counterexample in this workspace: it makes verbatim evidence the primary store and treats derived structures as indexes. That does not solve truth, but it avoids losing the original context during extraction.

### Vector-only memory

Vector search misses exact constraints and can retrieve plausible but wrong memories. Every serious design should include lexical search or structured filters. `engram` demonstrates the value of boring FTS. `mempalace` demonstrates vector plus BM25 plus metadata plus fallback paths. `mem0` and `honcho` show hybrid approaches. `llm-wiki-memory` has strong metadata filters and deterministic topology lookup, but its lexical-hash mode is a fallback backend rather than a fused exact-search channel. Claude-Mem and A-MEM additionally show why having both lexical and vector code—or simply using Chroma—does not make an ordinary query path hybrid.

### Ranking positions used as identities

Retrieval order is ephemeral, not object identity. A-MEM shows the failure
directly: it returns vector rank positions and later applies them to insertion
order, so an LLM can rewrite a different neighbor than the one it saw. Carry
stable memory IDs through prompts, responses, validation, mutation, and audit.

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

`holographic` is the atlas's clearest counterexample, and it is worth studying precisely because the mechanism looks reasonable in isolation. A `fact_feedback` tool lets the model or user rate a fact helpful or unhelpful, adjusting a single `trust_score` by +0.05 or −0.10. That same score is multiplied directly into relevance during ranking *and* gates retrieval through a `min_trust` floor defaulting to 0.3. From the default trust of 0.5, three unhelpful ratings put a fact at 0.2 — below every default retrieval path, permanently, with no tombstone, no review queue, and no record that a suppression occurred. Feedback has quietly become deletion, and "unhelpful" has quietly become "false".

`atomic-agent` sits at the disciplined end of the same range. Votes are written
to an append-only `vote_events` table (`kind`, `target_id`, `direction`,
`session_id`, `turn_index`, `created_at`) and `vote_score` is a derived, indexed
column on memories, lessons, and profile facts. Because the raw events are
retained, a scoring rule can be recomputed, a suspicious pattern can be audited,
and no single vote is destructive — the atlas's own "keep retrieval events
append-only; derive counters from events" recommendation, implemented. Ranged
against Holographic's in-place mutation, RainBox's human gate, and MetaClaw's
replay-gated policy tuning, it is the option that preserves the most future
choices.

### The harness's own output captured as evidence

A system that generates text and also captures text will eventually capture its own output. `openclaw` strips media notes, context markers, reply headers, sender prefixes, and timestamps from every message before capture, then rejects whatever still `looksLikeEnvelopeSludge`. `holographic` had to exclude its host's compaction handoff summaries, which arrive as `role="user"` messages and reliably matched its own decision-extraction regexes, so the compactor's output was being stored as durable facts on every context rollover.

Both fixes arrived after the bug. Any system with automatic capture should have a test asserting that its own generated scaffolding — summaries, envelopes, tool wrappers, injected memory blocks — cannot re-enter as evidence.

### One score for truth and reachability

Separating epistemic confidence from retrieval strength is one of the atlas's recurring recommendations, and the new systems split cleanly on it. `openviking`'s `hotness_score` is explicitly a reachability signal blended into ranking and never touches correctness; `redis-agent-memory-server` keeps recency weights entirely inside ranking and retention. `holographic` collapses both into `trust_score`, so there is no way to ask for the most relevant memory independent of how it has been rated, and no way to record that a rarely-retrieved fact is nonetheless certainly true.

### Platform-only claims hidden behind OSS APIs

Mem0 and Supermemory both have product surfaces where advanced behavior may live outside the inspected source. For build decisions, separate what is visible in code from what is promised by hosted APIs.

`byterover` adds a licensing variant of the same problem: it is widely described as an open-source memory engine, but the repository inspected here carries the Elastic License 2.0, which prohibits offering the software as a hosted service. Check the `LICENSE` file rather than the positioning before planning to reuse anything.

### Published benchmark numbers without committed artifacts

The atlas has now found three variants of this. Swafra committed a `k=10` artifact that scored every returned session. TencentDB published gains with no harness in the repository at all. `openviking` is the most advanced case and the most nearly right: it commits a genuinely reproducible harness — ingest, QA, LLM judge, statistics, runners for six competing systems, and token accounting alongside accuracy, which is exactly what this atlas asks for — yet the headline figures in its README (LoCoMo accuracy of 82.08% versus 24.20% native for OpenClaw, and comparable deltas for Hermes and Claude Code) point to an off-repo blog post, and no raw result files are committed.

A reproducible harness and a reproducible result are different claims. See [benchmarking agent memory](../benchmarks/) for what the published numbers are and are not measuring. These are also vendor-run comparisons of "competitor's native memory" against "competitor plus our product", judged by an LLM, so the native baselines deserve independent scrutiny before the deltas are quoted.

### Throwing away raw evidence too early

Extraction-first systems can look elegant while deleting the only material needed to debug a wrong memory. MemPalace is the strongest evidence that raw text plus retrieval deserves to be the baseline before adding lossy summarization or fact extraction.

### Treating local JSON rewrites as durable storage

Swafra loads and rewrites chunks, edges, and sources as three independent JSON files. Without locks, atomic replace, transactions, repair, or cascading deletion, concurrent agents can lose writes and partial failure can split graph state. Human-readable export is valuable; it is not a substitute for transactional primary storage.

## 7. What Seems to Work

SQLite plus FTS works for local coding-agent memory. It gives inspectable state, transactional writes, simple backup/sync, and exact search. Engram, Verel, and Claude-Mem are good references. MemPalace shows how to combine local SQLite-style operational machinery with a vector backend and fallback BM25/FTS paths.

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

Keep capture model-independent. Agentmemory's synthetic observation path and
Claude-Mem's durable hook queue preserve the event before model compression.
Zero-LLM capture is the reliable floor; enrichment can be added later.

Treat semantic indexes as projections. Claude-Mem commits SQLite before
best-effort Chroma sync, and Cognee can retain sources while deleting and
rebuilding derived memory. The authoritative store and repair direction should
be obvious.

Make background derivation reversible by provenance. Cognee's pipeline-run
rollback is the strongest cross-store example in the atlas, even though it
cannot make every backend combination atomic.

Number your invariants and cite them from the code. `atomic-agent`'s schema
comments reference "cross-phase invariant 7 in `MEMORY_FABRIC_V2.md` §13.7",
invariant 20 on never auto-executing procedures, and invariant 21 bounding
distillation to one LLM call per cluster. It costs almost nothing and turns an
implicit constraint into a reviewable one — and across the atlas, nothing else
does it.

Ship new memory behaviour off by default until an evaluation says otherwise.
`atomic-agent`'s v2.5 features are all `default: false` while its campaign runs.

Put scope on the provider contract. `mateclaw`'s SPI carries an `ownerKey` on
`prefetch` and `syncTurn`, and its decorators give every backend retry and
metrics without per-plugin code — the two things the other host runtimes leave
to each plugin to solve, or not.

Test what memory must **not** surface. `open-cowork`'s eval cases carry
`forbiddenHits` alongside `expectedHits`, and a leak floors the case score
regardless of how much correct material was also retrieved. Every "tests to
require" list in the pattern library asks for scope-leakage, rejected-value, and
sensitivity assertions; this is what they look like as an executable fixture.

Score the prompt prefix, not the retriever. Between retrieval and the model sit
truncation, deduplication, ordering, and formatting — any of which can drop a
memory that retrieval correctly found. `open-cowork` scores what reached the
model.

Separate durability from importance. `mercury-agent` grades confidence,
importance, and durability independently, which is the schema-level answer to
this atlas's warning against applying one half-life to every memory kind.

Write your memory decisions down. `gini-agent` keeps ADRs recording the
decision, its context, and the failure that motivated it — its per-agent
isolation ADR states plainly that a coding agent's pinned memories were
polluting a research agent's recall. Across forty systems, almost none can
explain why they are shaped the way they are.

Make scope structurally inseparable from the query. OpenClaw composes agent scope and user filter into a single predicate so an unscoped read is not expressible, and scopes deletes the same way. This is stronger than applying a scope filter somewhere in the read path, and it is the kind of guarantee that survives refactoring.

Specify retention as a policy, not a TTL. Redis Agent Memory Server's `select_ids_for_forgetting` combines age and inactivity so recent use buys a memory time but not immunity, honours pinning and per-type allowlists, and prunes to a budget using separate half-lives for last access and creation. Most systems here either never forget or forget on one crude axis.

Guard generated rewrites against deletion. ByteRover's structural-loss detection parses before and after, counts only what would be removed, and merges it back. It is a few hundred lines, requires no model, and directly addresses the reason this atlas warns against premature summarization.

Sanitize your own scaffolding out of captured text, and test that it stays out. Two systems in the Hermes/OpenClaw ecosystem shipped fixes for their own generated text being stored as user memory.

Make memory use inspectable. RainBox's debug rows, retrieval events, and review UI are the best reference here. Users need to know which memories entered a prompt and need a way to correct or reject them.

Separate event time from ingestion time when facts change. Graphiti's bi-temporal edges preserve historical truth and backfilled events without destructive overwrite.

Decay reachability, not truth. Verel keeps retrieval strength separate from
confidence and protects important lifecycle states. Reinforcement should record
usefulness or corroboration, never silently upgrade factual authority.

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

1. Store raw evidence first without requiring an LLM call.
2. Chunk deterministically and record embedder identity.
3. Index raw evidence with lexical and vector paths.
4. Extract candidate facts with schema-constrained LLM output only after evidence is durable.
5. Search for same subject/predicate and near duplicates.
6. If same key plus same value, corroborate.
7. If same key plus different value, create a conflict or supersession.
8. Do not auto-promote to verified unless the source is trusted or corroborated.
9. Preserve failed extraction inputs and make background work safely retryable.
10. Store enrichment state so raw memory remains searchable while derivation is pending.

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

Disclosure: RainBox is the atlas author's own project; this verdict is a self-assessment against the shared rubric.

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

### `agentmemory`

- Best idea: zero-LLM hook capture plus compact-first hybrid search and explicit expansion.
- Biggest risk: a large optional surface and similarity-based supersession without an epistemic review state.
- Most reusable component: `mem::observe`, `HybridSearch`, and `mem::smart-search`.
- Maturity impression: ambitious, heavily tested coding-agent runtime with many operational paths.
- Study when: hooks, local capture, hybrid recall, and later consolidation need to coexist.
- Do not copy when: a small auditable store is enough or shared-by-default agent memory is unsafe.

### `tencentdb-agent-memory`

- Best idea: progressive disclosure from raw evidence through records, scenes, persona, and navigable tool-output maps.
- Biggest risk: non-atomic JSONL/store updates and fail-open deduplication can create loss or contradictions.
- Most reusable component: L0/L1/L2/L3 context split and symbolic offload drill-down.
- Maturity impression: inventive OpenClaw/Hermes integration, but central lifecycle tests and reproducible benchmark evidence are thin.
- Study when: tool-heavy sessions exceed the context window and raw drill-down must remain possible.
- Do not copy when: authoritative cross-store consistency, multi-tenant boundaries, or verified memory are required.

### `cognee`

- Best idea: source-preserving, ontology-aware graph/vector pipelines with provenance rollback behind a small remember/recall API.
- Biggest risk: probabilistic extraction and a large adapter/configuration surface create cross-store consistency and policy burden.
- Most reusable component: permanent `remember()` as add-plus-cognify, dataset authorization, and pipeline-run rollback.
- Maturity impression: substantial platform with broad tests and transparent but preliminary BEAM artifacts.
- Study when: agents need multimodal ingestion, typed knowledge graphs, ontologies, dataset permissions, and backend choice.
- Do not copy when: a small local evidence store and lexical/vector retrieval satisfy the requirement.

### `claude-mem`

- Best idea: durable hook queue, canonical SQLite commit, then best-effort semantic/cloud projections and bounded timeline injection.
- Biggest risk: generated observations become active without epistemic review, and ordinary text search does not fuse its FTS and Chroma capabilities.
- Most reusable component: `pending_messages` lifecycle plus `ResponseProcessor` commit/acknowledgement ordering.
- Maturity impression: operationally mature coding-agent sidecar with broad failure-path tests; memory quality is not benchmarked.
- Study when: cross-session coding context must be captured automatically without blocking the agent.
- Do not copy when: explicit writes are sufficient, hooks are unavailable, or high-stakes facts require verification before use.

### `holographic`

- Best idea: deterministic SHA-256-derived phase vectors and algebraic multi-entity queries, with no embedding model to version.
- Biggest risk: three unhelpful ratings silently drop a fact below the retrieval floor forever.
- Most reusable component: `encode_atom`/`bind`/`unbind`, the FTS5 query sanitizer, and the refcounted shared-connection registry.
- Maturity impression: compact and fully readable, with real production scar tissue around concurrency, but no benchmark and an unmeasured HRR contribution.
- Study when: you want compositional structure without an embedding service, or a worked example of why truth and usefulness must be separate fields.
- Do not copy when: you need scope, provenance, correction, or any feedback mechanism that is not also a deletion mechanism.

### `hermes-agent`

- Best idea: bounded curated memory frozen into the prompt at session start, with overflow refused and consolidation demanded in-turn.
- Biggest risk: whatever the model writes is authoritative in every later session, and budget-driven eviction is unlogged.
- Most reusable component: the frozen-snapshot pattern, `_detect_external_drift`, and the staged write-approval gate.
- Maturity impression: heavily defended file layer whose guards cite the incidents that produced them; the provider contract is less complete than the store.
- Study when: prompt-cache cost is material, or you need memory that cannot grow without someone deciding what to drop.
- Do not copy when: you need verification, tombstones, substring-free identity, or a provider contract that can honour deletion.

### `openviking`

- Best idea: three retrievable granularities on one record, plus hotness kept strictly separate from confidence.
- Biggest risk: extraction becomes durable context with no verification tier, and published numbers are not backed by committed artifacts.
- Most reusable component: `hotness_score`, `type_quota_recall`, and the `user_space` / `peers/<id>` isolation convention.
- Maturity impression: a large, seriously engineered platform with real multi-tenancy and the most complete benchmark harness in the atlas.
- Study when: you need multimodal ingestion, tenant isolation, skills and resources unified with memory, or backend choice.
- Do not copy when: you need a small embeddable layer, verified memory, or a licence compatible with closed distribution — this is AGPL-3.0.

### `redis-agent-memory-server`

- Best idea: TTL-native working memory promoting into deduplicated long-term memory, with retention expressed as a real policy.
- Biggest risk: forgetting is deletion without tombstones, so anything forgotten can be re-extracted.
- Most reusable component: `select_ids_for_forgetting`, the three-layer dedupe chain, and `_semantic_merge_group_is_cohesive`.
- Maturity impression: vendor-neutral reference implementation with unusually well-targeted tests on the risky logic.
- Study when: you want the working/long-term split done carefully, or a retention policy you can defend to a user.
- Do not copy when: cognitive memory types would be mistaken for a trust model, or deletion must be durable.

### `byterover`

- Best idea: counting exactly what an LLM rewrite would delete, then merging the loss back automatically.
- Biggest risk: the Elastic License 2.0 forbids hosted redistribution, and the memory core itself has no trust, scope, or correction model.
- Most reusable component: `detectStructuralLoss` / `resolveStructuralLoss`, and the immutable `DECISIONS` category.
- Maturity impression: a thin memory primitive attached to a more thoughtful knowledge-curation layer, with no visible tests on its best idea.
- Study when: an LLM is allowed to rewrite stored knowledge and you need a cheap deterministic guard.
- Do not copy when: you need durable beliefs, ranked retrieval, or an OSI-compatible licence.

### `openclaw`

- Best idea: scope composed inseparably into every predicate, and 567 lines spent keeping the runtime's own envelope out of memory.
- Biggest risk: a vector-only reference backend for content full of names and identifiers, with auto-capture that can undo deletions.
- Most reusable component: `memory-capture-sanitization.ts`, `scopedPredicate`, and the doctor-contract idea.
- Maturity impression: test lines far exceed implementation lines; the plugin contract is mature, the memory model deliberately minimal.
- Study when: building a host runtime with swappable memory, or capturing from a channel that wraps messages in scaffolding.
- Do not copy when: you need hybrid retrieval, per-user scope inside an agent, or deletion that survives auto-capture.

### `atomic-agent`

- Best idea: numbered cross-phase invariants cited from the schema into a design document, and votes kept as append-only events with derived scores.
- Biggest risk: an elaborate opt-in surface whose evaluation campaign has no committed results.
- Most reusable component: the invariant-citation practice, the `vote_events` shape, and the surfaced-id allowlist in `neighbor-evolver.ts`.
- Maturity impression: the most specification-like memory system in the atlas — design plan, acceptance criteria, implementation ledger, and features default-off pending evidence.
- Study when: you want memory built as an engineering artifact rather than an accretion, or a feedback design that keeps every downstream option open.
- Do not copy when: you need a value tombstone or an established scope model; neither surfaced here.

### `mateclaw`

- Best idea: a provider SPI that carries an owner key, with retry and metrics as decorators over every backend.
- Biggest risk: the contract still has no deletion hook, and contradiction is detected without a resolution path.
- Most reusable component: the SPI shape with scoped overloads and default methods, and `spi/decorator/`.
- Maturity impression: built in the enterprise-framework tradition — layered, dependency-injected, event-driven, and conventional in the ways that tradition is good at.
- Study when: designing a memory contract third parties will implement, or wondering who owns provider resilience.
- Do not copy when: you need the deletion half of the governance story, which is absent.

### `llamaindex`

- Best idea: one token budget split between chat history and blocks, with each block truncating itself to fit.
- Biggest risk: no provenance, correction, or scope, and long-term capture is triggered by conversation length rather than importance.
- Most reusable component: the `BaseMemoryBlock` contract — `aget`, `aput`, `atruncate` — and the explicit budget split.
- Maturity impression: a widely deployed framework whose newer block API is a real memory layer, shipped alongside an older window-management API of the same name.
- Study when: you need a memory component contract, or a budget that several contributors must share.
- Do not copy when: facts must be traceable, correctable, or scoped — those are left to the application.

### `open-cowork`

- Best idea: a committed memory benchmark whose queries assert forbidden hits as well as expected ones, scored against the assembled prompt prefix.
- Biggest risk: the harness exists but no scored results are committed, and no trust state guards extraction.
- Most reusable component: `memory-eval-harness.ts` — the eval-case shape is largely independent of the rest of the system.
- Maturity impression: a well-factored memory subsystem whose evaluation thinking is ahead of most of the atlas.
- Study when: you need to turn "our memory works" into something a CI job can check.
- Do not copy when: you need verification or correction semantics; neither appears in the module set.

### `gini-agent`

- Best idea: bi-temporal units with `rejected` and `conflicted` states, four RRF-fused recall channels, and architecture decisions recorded as ADRs.
- Biggest risk: `conflicted` is modelled with no visible workflow to resolve it, and rejection has no value-level tombstone.
- Most reusable component: the `memory_units` schema, and the ADR practice itself.
- Maturity impression: a faithful local reimplementation of a published memory model, with unusually good written rationale.
- Study when: you want a trust-and-time-aware unit schema you can implement in plain SQLite.
- Do not copy when: you need the conflict workflow the schema implies but does not ship.

### `moltis`

- Best idea: a no-embeddings mode that is a constructor and a predicate rather than a degraded state, plus content-hash file addressing.
- Biggest risk: exported session transcripts share one index and one rank with curated notes, with nothing distinguishing them.
- Most reusable component: `MemoryManager::keyword_only()` / `has_embeddings()`, and the single `sync()` chokepoint.
- Maturity impression: carefully built, with feature-gated backends and committed plans naming its own gaps.
- Study when: memory and documents should be one substrate, or you need a genuinely offline path.
- Do not copy when: a chunk is not a good enough unit — there is no claim, status, or correction record.

### `mercury-agent`

- Best idea: three independent grades — confidence, importance, durability — plus a subconscious tier and a user-facing learning pause.
- Biggest risk: `dismissed` is a boolean, so dismissal is not durable against re-extraction.
- Most reusable component: the record model, especially the durability/importance split and the narrowed candidate type.
- Maturity impression: small but opinionated, with an operator review page and clear provenance kinds.
- Study when: building personal memory where different facts should live for different lengths of time.
- Do not copy when: automatic extraction can regenerate what a user dismissed.

### `waku-agent`

- Best idea: a small-model gate that decides whether to retrieve at all, returns the query when it says yes, and fails open when it errors.
- Biggest risk: the gate's own accuracy is unmeasured, and a false negative is invisible.
- Most reusable component: `should_retrieve()` — the fail-open branch and the recorded reason included.
- Maturity impression: small, opinionated, and unusually clear about why each expensive step is conditional; deterministic evals for memory behaviour.
- Study when: retrieval runs every turn and you suspect it is hurting as often as helping.
- Do not copy when: you need correction, scope, or trust — none of the three exists here.

### `metaclaw`

- Best idea: candidate retrieval policies replayed offline and promoted only on non-regression across eight metrics.
- Biggest risk: the loop optimizes lexical-overlap proxies, and its promotion thresholds are hand-chosen constants.
- Most reusable component: `promotion.py`'s `MemoryPromotionCriteria` and the replay-then-gate loop in `self_upgrade.py`.
- Maturity impression: substantial and unusually well evidenced, with committed benchmark fixtures and dedicated memory ablations.
- Study when: you cannot justify your retrieval weights and want a safe way to change them.
- Do not copy when: you need trust semantics — the memory model has no rejected state and no verification path.

### `nanobot`

- Best idea: two cursors over an append-only archive, with a Dream pass that refuses to advance after tool errors.
- Biggest risk: durable claims carry no provenance back to the evidence that produced them.
- Most reusable component: the dual-cursor split, the failure-aware advance gate, and the durable-file allowlist for audit commits.
- Maturity impression: compact and carefully reasoned, with unusually good design documentation and no visible memory tests.
- Study when: a fast producer feeds a slow consolidator, or you want git history that reads as a record of belief.
- Do not copy when: memory must grow past what fits in every prompt, or must be scoped per project.

### `cowagent`

- Best idea: a dated intermediate layer that gives consolidation a naturally bounded unit, plus written distillation rules and a dream diary.
- Biggest risk: two chained lossy summarizations with no loss detection, and recency-wins conflict resolution.
- Most reusable component: the daily-bucket pipeline, the distillation rule table, and the self-healing FTS5 state check.
- Maturity impression: practical and well documented, with real hybrid retrieval and no visible memory tests.
- Study when: you want consolidation you can inspect by opening a file for a given day.
- Do not copy when: scope matters — `scope` defaults to `shared` — or corrections must be reviewable.

### `genericagent`

- Best idea: "No Execution, No Memory", and an explicit ROI model for what earns a place in always-injected context.
- Biggest risk: every rule is prose, with no enforcement, no audit, and no record of the verification each write claims.
- Most reusable component: the four axioms and the cleanup SOP's ROI test and deletion categories.
- Maturity impression: a small framework whose memory thinking is considerably more developed than its memory machinery.
- Study when: designing the policy layer of a memory system, or deciding what belongs in permanent context.
- Do not copy when: wrong memory is costly and you need the rules enforced rather than requested.

### `magic-context`

- Best idea: memories mapped to backing files and re-verified when git reports those files changed, with lifecycle and verification on separate axes.
- Biggest risk: no rejected-value tombstone, so archived memories can be re-derived; and the verification verdict is still an LLM call.
- Most reusable component: `dreamer/verify-gate.ts`, the two-axis state model, and `(memory_id, model_id)` embedding keys.
- Maturity impression: the heaviest test posture in the atlas — 473 test files, seventy tested migrations, CAS-race suites, fail-closed registration.
- Study when: memory describes an inspectable artifact and you want trust to be observed rather than judged.
- Do not copy when: you need a small memory layer; most projects want the verify gate and the state model, not the whole platform.

### `pi`

- Best idea: deterministic `readFiles`/`modifiedFiles` manifests attached to compaction entries, derived from tool calls rather than from the summarizing model.
- Biggest risk: no memory contract at all, so scope and deletion have nowhere to live and every plugin reinvents indexing.
- Most reusable component: the typed session-entry model and the result-returning extension events.
- Maturity impression: actively developed, well-factored harness; memory is deliberately out of scope.
- Study when: designing a host runtime, or thinking about what branchable sessions mean for memory.
- Do not copy when: you expect third-party memory — define scope and deletion in the interface before plugins exist.

### `hipporag`

- Best idea: Personalized PageRank diffusion replaces hop planning, with IDF-penalized seeding and a weak dense prior.
- Biggest risk: no scope, trust, provenance, or temporal model, and a wrong extracted edge has graph-wide blast radius.
- Most reusable component: `graph_search_with_fact_entities()` plus `run_ppr()`, and synonymy-as-edges instead of entity merging.
- Maturity impression: actively maintained research framework with a strong reproduction tree and thin unit tests.
- Study when: recall must cross documents associatively, or entity-resolution merges have burned you.
- Do not copy when: you need agent memory rather than corpus QA — scope, correction, and time all have to be added.

### `voyager`

- Best idea: memory written only after the environment verifies the procedure worked.
- Biggest risk: a frozen 2023 artifact that generalizes from a single verified run and keeps no failure memory.
- Most reusable component: the verified write gate, and description-indexed / code-retrieved storage.
- Maturity impression: a 127-line memory subsystem inside a research agent; unmaintained since July 2023.
- Study when: your agent's actions have observable outcomes and competence is worth remembering, not just facts.
- Do not copy when: procedures will be executed outside a sandbox, or success is a matter of judgment rather than observation.

### `generative-agents`

- Best idea: consolidation triggered by accumulated significance rather than by a timer or token count.
- Biggest risk: its famous retrieval weights are hand-tuned constants, and reflections share one pool with observations.
- Most reusable component: the reflection trigger, and the three-signal retrieval structure — recalibrated, with time-based recency.
- Maturity impression: the field's reference architecture, frozen since August 2023 and never engineered for production.
- Study when: you want to understand where most of this atlas came from, or need a consolidation schedule that tracks salience.
- Do not copy when: you need any operational property at all — there is no scope, correction, deletion, or index.

### `a-mem`

- Best idea: small linked notes whose organization can be reconsidered when new memory arrives.
- Biggest risk: rank positions are used as note identities, allowing evolution to mutate the wrong neighbor.
- Most reusable component: the proposed Zettelkasten evolution protocol, after replacing direct mutation with validated change proposals.
- Maturity impression: research prototype; tests are shallow around the most consequential behavior and benchmarks live elsewhere.
- Study when: researching adaptive linked-note organization.
- Do not copy as a production core without stable IDs, canonical durability, scope, provenance, transactions, and trust state.

### `memora`

- Best idea: automated supersession that defaults to a dry run, so a correction sweep is previewed before it hides anything.
- Biggest risk: supersession without a tombstone, in a system that ingests documents and images and can therefore re-ingest what it hid.
- Most reusable component: the six-way relation vocabulary with neutral A/B presentation, and `dry_run: bool = True` as the default posture.
- Maturity impression: substantial for its age, with the sophistication concentrated in what happens to memories after they are written.
- Study when: you are about to run an automatic dedupe or supersession pass over a store you cannot afford to damage.
- Do not copy when: you need trust state, scope isolation, or a correction that survives re-ingestion.

### `loongflow`

- Best idea: recall by Boltzmann sampling at a temperature driven by the store's measured diversity — the only stochastic retrieval in the atlas.
- Biggest risk: selection quality is bounded entirely by a `score` nothing validates, and the same query can return different memories with no seed or replay path.
- Most reusable component: the diversity-to-temperature loop, including the 20% smoothing and the explicit min/max bounds.
- Maturity impression: two unrelated memory models in one package — a conventional tier stack and a genuinely novel selection mechanism — with the control constants undefended.
- Study when: memory feeds a search or generate-and-test loop and deterministic top-*k* keeps returning the same dead end.
- Do not copy when: recall must be reproducible, or the memories are facts rather than attempts.

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
- [`agentmemory`](../systems/agentmemory/)
- [`tencentdb-agent-memory`](../systems/tencentdb-agent-memory/)
- [`cognee`](../systems/cognee/)
- [`claude-mem`](../systems/claude-mem/)
- [`a-mem`](../systems/a-mem/)
- [`holographic`](../systems/holographic/)
- [`hermes-agent`](../systems/hermes-agent/)
- [`openviking`](../systems/openviking/)
- [`redis-agent-memory-server`](../systems/redis-agent-memory-server/)
- [`byterover`](../systems/byterover/)
- [`openclaw`](../systems/openclaw/)
- [`hipporag`](../systems/hipporag/)
- [`voyager`](../systems/voyager/)
- [`generative-agents`](../systems/generative-agents/)
- [`magic-context`](../systems/magic-context/)
- [`pi`](../systems/pi/)
- [`metaclaw`](../systems/metaclaw/)
- [`nanobot`](../systems/nanobot/)
- [`cowagent`](../systems/cowagent/)
- [`genericagent`](../systems/genericagent/)
- [`open-cowork`](../systems/open-cowork/)
- [`gini-agent`](../systems/gini-agent/)
- [`moltis`](../systems/moltis/)
- [`mercury-agent`](../systems/mercury-agent/)
- [`llamaindex`](../systems/llamaindex/)
- [`atomic-agent`](../systems/atomic-agent/)
- [`mateclaw`](../systems/mateclaw/)
- [`waku-agent`](../systems/waku-agent/)
- [`memora`](../systems/memora/)
- [`loongflow`](../systems/loongflow/)

### Repos Inspected

- [mem0ai/mem0](https://github.com/mem0ai/mem0) at [`31cec11a790868f88c9acafb8b70eb25071f2150`](https://github.com/mem0ai/mem0/commit/31cec11a790868f88c9acafb8b70eb25071f2150)
- [langchain-ai/langmem](https://github.com/langchain-ai/langmem) at [`c01e273b94aa4c06e41d0ed1ccce0db17de2bc11`](https://github.com/langchain-ai/langmem/commit/c01e273b94aa4c06e41d0ed1ccce0db17de2bc11)
- [plastic-labs/honcho](https://github.com/plastic-labs/honcho) at [`eb386c3ceb77774b29108f9ab114e71d52b7d420`](https://github.com/plastic-labs/honcho/commit/eb386c3ceb77774b29108f9ab114e71d52b7d420)
- [Gentleman-Programming/engram](https://github.com/Gentleman-Programming/engram) at [`44faeee1fb4fabdee4ba9619df55af485f3d06eb`](https://github.com/Gentleman-Programming/engram/commit/44faeee1fb4fabdee4ba9619df55af485f3d06eb)
- [MemPalace/mempalace](https://github.com/MemPalace/mempalace) at [`afd0428823b47f9a9d1d68c450d54bb0045a4988`](https://github.com/MemPalace/mempalace/commit/afd0428823b47f9a9d1d68c450d54bb0045a4988)
- [kunal12203/swafra](https://github.com/kunal12203/swafra) at [`24dba18a4194aef0cb0d6d6c68cf46e6fcbf2da7`](https://github.com/kunal12203/swafra/commit/24dba18a4194aef0cb0d6d6c68cf46e6fcbf2da7)
- [ctxr-dev/llm-wiki-memory](https://github.com/ctxr-dev/llm-wiki-memory) at [`b7cc76a493573baac133969b324a874990556146`](https://github.com/ctxr-dev/llm-wiki-memory/commit/b7cc76a493573baac133969b324a874990556146)
- [neoneye/RainBox](https://github.com/neoneye/RainBox) at [`9f565bf26175bc5e09288f70ec666a4616a2323c`](https://github.com/neoneye/RainBox/commit/9f565bf26175bc5e09288f70ec666a4616a2323c)
- [letta-ai/letta](https://github.com/letta-ai/letta) at [`6d8cb7fd48938b629aad5770faa051a8d42e1e9f`](https://github.com/letta-ai/letta/commit/6d8cb7fd48938b629aad5770faa051a8d42e1e9f)
- [supermemoryai/supermemory](https://github.com/supermemoryai/supermemory) at [`603d0512fd40e4575e2a075938c1851a898ceeb6`](https://github.com/supermemoryai/supermemory/commit/603d0512fd40e4575e2a075938c1851a898ceeb6)
- [amitpatole/verel](https://github.com/amitpatole/verel) at [`df80efe8207a99585a2ebce36fc6e32ba5077e2e`](https://github.com/amitpatole/verel/commit/df80efe8207a99585a2ebce36fc6e32ba5077e2e)
- [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight) at [`ed120a256d51d731085ec8aca724573a7f2f1e1c`](https://github.com/vectorize-io/hindsight/commit/ed120a256d51d731085ec8aca724573a7f2f1e1c)
- [getzep/graphiti](https://github.com/getzep/graphiti) at [`9140123a7282d44efc077a0af09179919f3defdf`](https://github.com/getzep/graphiti/commit/9140123a7282d44efc077a0af09179919f3defdf)
- [mastra-ai/mastra](https://github.com/mastra-ai/mastra) at [`40547102f655596178346ad2f883fbde735c3333`](https://github.com/mastra-ai/mastra/commit/40547102f655596178346ad2f883fbde735c3333)
- [MemTensor/MemOS](https://github.com/MemTensor/MemOS) at [`3fd109e7cbaba291af2253f107e0a595dbf62b00`](https://github.com/MemTensor/MemOS/commit/3fd109e7cbaba291af2253f107e0a595dbf62b00)
- [basicmachines-co/basic-memory](https://github.com/basicmachines-co/basic-memory) at [`232f2c2fc4e91564d88bcc312ed3d8bd1e8e051b`](https://github.com/basicmachines-co/basic-memory/commit/232f2c2fc4e91564d88bcc312ed3d8bd1e8e051b)
- [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) at [`d8b5267c367a5da07ad3619363520b7f1a506c6b`](https://github.com/rohitg00/agentmemory/commit/d8b5267c367a5da07ad3619363520b7f1a506c6b)
- [TencentCloud/tencentdb-agent-memory](https://github.com/TencentCloud/tencentdb-agent-memory) at [`45e6e80ae2e63b65fad0d89f5e13171229c8f295`](https://github.com/TencentCloud/tencentdb-agent-memory/commit/45e6e80ae2e63b65fad0d89f5e13171229c8f295)
- [topoteretes/cognee](https://github.com/topoteretes/cognee) at [`325acf356a81545b9892f19ab1ea7b61c51a776b`](https://github.com/topoteretes/cognee/commit/325acf356a81545b9892f19ab1ea7b61c51a776b)
- [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) at [`132b46343e60ecf4057c427736c57b08f7615dfe`](https://github.com/thedotmack/claude-mem/commit/132b46343e60ecf4057c427736c57b08f7615dfe)
- [agiresearch/A-mem](https://github.com/agiresearch/A-mem) at [`ceffb860f0712bbae97b184d440df62bc910ca8d`](https://github.com/agiresearch/A-mem/commit/ceffb860f0712bbae97b184d440df62bc910ca8d)
- [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) at [`0fa5e41c86f022bba147797849f0b44865721476`](https://github.com/NousResearch/hermes-agent/commit/0fa5e41c86f022bba147797849f0b44865721476) — analyzed twice, as the `holographic` plugin and as Hermes's own built-in memory
- [volcengine/OpenViking](https://github.com/volcengine/OpenViking) at [`c67222c3d46de4874eed65af8918fc55513812ef`](https://github.com/volcengine/OpenViking/commit/c67222c3d46de4874eed65af8918fc55513812ef)
- [redis/agent-memory-server](https://github.com/redis/agent-memory-server) at [`886437963dc02289e828872f0ae21fdaa734c337`](https://github.com/redis/agent-memory-server/commit/886437963dc02289e828872f0ae21fdaa734c337)
- [campfirein/cipher](https://github.com/campfirein/cipher) at [`1052ac1a5dd0fde4da8693d4712064f7876c269c`](https://github.com/campfirein/cipher/commit/1052ac1a5dd0fde4da8693d4712064f7876c269c)
- [openclaw/openclaw](https://github.com/openclaw/openclaw) at [`570eab59e7c7ce052f4550af7507e7dd77c73e11`](https://github.com/openclaw/openclaw/commit/570eab59e7c7ce052f4550af7507e7dd77c73e11)
- [OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG) at [`e37fba2af1a951ac340d837a7c02efb9d8c9544a`](https://github.com/OSU-NLP-Group/HippoRAG/commit/e37fba2af1a951ac340d837a7c02efb9d8c9544a)
- [MineDojo/Voyager](https://github.com/MineDojo/Voyager) at [`55e45a880755d0c8c66ca7fb5fe7962ac8974f89`](https://github.com/MineDojo/Voyager/commit/55e45a880755d0c8c66ca7fb5fe7962ac8974f89)
- [joonspk-research/generative_agents](https://github.com/joonspk-research/generative_agents) at [`fe05a71d3e4ed7d10bf68aa4eda6dd995ec070f4`](https://github.com/joonspk-research/generative_agents/commit/fe05a71d3e4ed7d10bf68aa4eda6dd995ec070f4)
- [cortexkit/magic-context](https://github.com/cortexkit/magic-context) at [`113f3e4824e0ea03a73f2c1e8a57a5ab0bbf7a09`](https://github.com/cortexkit/magic-context/commit/113f3e4824e0ea03a73f2c1e8a57a5ab0bbf7a09)
- [earendil-works/pi](https://github.com/earendil-works/pi) at [`a597371bda2af70372d1323d550483b5f4a0ae36`](https://github.com/earendil-works/pi/commit/a597371bda2af70372d1323d550483b5f4a0ae36)
- [aiming-lab/MetaClaw](https://github.com/aiming-lab/MetaClaw) at [`922caf3a1cd093fb316e95183a8acc8aa47b3b21`](https://github.com/aiming-lab/MetaClaw/commit/922caf3a1cd093fb316e95183a8acc8aa47b3b21)
- [HKUDS/nanobot](https://github.com/HKUDS/nanobot) at [`b99e0f937e828504e0f93dbe35dfd6b1540e20b2`](https://github.com/HKUDS/nanobot/commit/b99e0f937e828504e0f93dbe35dfd6b1540e20b2)
- [zhayujie/CowAgent](https://github.com/zhayujie/CowAgent) at [`fe88751ccb24e9b2991b6a35a2dcc538f7a38761`](https://github.com/zhayujie/CowAgent/commit/fe88751ccb24e9b2991b6a35a2dcc538f7a38761)
- [lsdefine/GenericAgent](https://github.com/lsdefine/GenericAgent) at [`7ffc95823b6e40ca4e10acf9fb285d923485cacc`](https://github.com/lsdefine/GenericAgent/commit/7ffc95823b6e40ca4e10acf9fb285d923485cacc)
- [OpenCoworkAI/open-cowork](https://github.com/OpenCoworkAI/open-cowork) at [`6f0c04741386b8600aa977f14ac0679d2203bd1b`](https://github.com/OpenCoworkAI/open-cowork/commit/6f0c04741386b8600aa977f14ac0679d2203bd1b)
- [Open-Curiosity/gini-agent](https://github.com/Open-Curiosity/gini-agent) at [`6c5d85ed0ecd7fe8567124bd4890b16c329970d8`](https://github.com/Open-Curiosity/gini-agent/commit/6c5d85ed0ecd7fe8567124bd4890b16c329970d8)
- [moltis-org/moltis](https://github.com/moltis-org/moltis) at [`1f53cd27b1a21c36b61ceda7a8ea65a35deb7872`](https://github.com/moltis-org/moltis/commit/1f53cd27b1a21c36b61ceda7a8ea65a35deb7872)
- [cosmicstack-labs/mercury-agent](https://github.com/cosmicstack-labs/mercury-agent) at [`6e174a4b5ea77bbc753bff5f89c76db9303439d1`](https://github.com/cosmicstack-labs/mercury-agent/commit/6e174a4b5ea77bbc753bff5f89c76db9303439d1)
- [run-llama/llama_index](https://github.com/run-llama/llama_index) at [`199e9b5b130bbde72639358a08935b913e7132c0`](https://github.com/run-llama/llama_index/commit/199e9b5b130bbde72639358a08935b913e7132c0)
- [AtomicBot-ai/atomic-agent](https://github.com/AtomicBot-ai/atomic-agent) at [`d69332c589733e38ae7393dd81fcbc5a375d02fb`](https://github.com/AtomicBot-ai/atomic-agent/commit/d69332c589733e38ae7393dd81fcbc5a375d02fb)
- [mateaix/mateclaw](https://github.com/mateaix/mateclaw) at [`3643aed7564390f57906954286a443d5913b97a7`](https://github.com/mateaix/mateclaw/commit/3643aed7564390f57906954286a443d5913b97a7)
- [ShenSeanChen/waku-agent](https://github.com/ShenSeanChen/waku-agent) at [`5f638cfb5de957c14f056027833d8a9df5bbe558`](https://github.com/ShenSeanChen/waku-agent/commit/5f638cfb5de957c14f056027833d8a9df5bbe558)
- [agentic-box/memora](https://github.com/agentic-box/memora) at [`bc64ff745a9b2c0e6245e0137654f041fba0c155`](https://github.com/agentic-box/memora/commit/bc64ff745a9b2c0e6245e0137654f041fba0c155)
- [baidu-baige/LoongFlow](https://github.com/baidu-baige/LoongFlow) at [`945c78bc1554f8281aac40320b3599bd68d528d7`](https://github.com/baidu-baige/LoongFlow/commit/945c78bc1554f8281aac40320b3599bd68d528d7)
- [netease-youdao/LobsterAI](https://github.com/netease-youdao/LobsterAI) at [`2921c1e5bddbd96a503da4acd7538cac45bcd0f2`](https://github.com/netease-youdao/LobsterAI/commit/2921c1e5bddbd96a503da4acd7538cac45bcd0f2) — not a report; cited in the OpenClaw analysis

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
- Four dimensions that matter operationally are not covered systematically here,
  and a reader choosing a system should investigate them directly. **Behaviour
  under embedding-model change or vector-store migration**: only a few systems
  visibly stamp records with the model that produced them, and a silent
  re-embedding is a silent corpus-wide quality change. **Whether scope survives
  background derivation**: the capability index records that a scope key is
  applied on the read path, not that consolidation, summarization, and profile
  building respect the same boundary — a summary spanning two projects has
  crossed a scope the retriever would have enforced. **Recall observability**
  beyond which memories were returned: why they outranked others, and what was
  dropped by budget truncation. **Cost and latency under realistic load**, which
  is treated separately in [benchmarking agent memory](../benchmarks/) — as an
  absence, because it is almost never measured.
- The capability flags in the index are the reviewer's judgements against
  strict definitions, applied to code read at the pinned commits. A flag's
  absence means the mechanism was not found, not that it is impossible to build
  on that system.
- Retrieval quality and extraction quality were not independently re-measured; committed benchmark artifacts were inspected for MemPalace but not rerun.
- Swafra was reviewed at commit `24dba18`; its full LongMemEval run was not rerun. Static inspection, committed artifact analysis, and a small hash-embedder smoke check exposed the `k` mismatch and same-title source behavior.
- `llm-wiki-memory` was reviewed at commit `b7cc76a493573baac133969b324a874990556146`; its broad test tree and committed latency report were inspected, but the suites and benchmarks were not rerun.
- RainBox was reviewed as an application-integrated memory subsystem; unrelated assistant/product features were not exhaustively analyzed.
- The reports prioritize memory-management code paths over unrelated framework/application code.
- Hindsight, Graphiti, Mastra, MemOS, and Basic Memory were reviewed statically at the pinned revisions above; their dependency-heavy integration suites and published benchmarks were not rerun.
- Mastra analysis is intentionally limited to `packages/memory` and the core contracts it directly uses.
- MemOS behavior varies materially by memory cube, backend, model, and search configuration; the report does not imply one universal MemOS pipeline.
- agentmemory's source tests and benchmarks were inspected but not rerun; its documented LongMemEval-S numbers are retrieval-only.
- TencentDB Agent Memory's published benchmark gains could not be traced to a committed harness or raw result artifacts in the inspected repository.
- Cognee's dependency-heavy suites and BEAM evaluation were not rerun. The committed 100K report uses a held-out conversation; its 10M routed result is explicitly exploratory and selected on the reported questions.
- Claude-Mem's Bun suite and optional service integrations were not run; no committed end-to-end recall-quality benchmark was found.
- A-MEM's tests were not run because they may download embedding models and call an external LLM. The paper reproduction code and results are outside the inspected package.
- `holographic` and `hermes-agent` are two reports over one repository at one commit: the first covers the in-tree HRR memory plugin, the second covers Hermes's own built-in memory and provider contract. Neither report's suites were run.
- Two open Hermes issues (#4781, #31263) report that the holographic plugin registers without its tools or context injection firing. Only the issue titles were read; they are not treated here as established defects in the inspected code.
- OpenViking's published LoCoMo and tau2-bench figures could not be reproduced or traced to committed raw artifacts at the inspected commit; the harness is committed, the results are not. Those figures are also vendor-run comparisons judged by an LLM, and the native-memory baselines for OpenClaw, Hermes, and Claude Code were not independently verified.
- The `openclaw` figures quoted from OpenViking's benchmark are third-party claims about OpenClaw's native memory, not measurements taken from the OpenClaw repository.
- ByteRover was reviewed at a commit where the repository is licensed under the Elastic License 2.0 and packaged as `byterover-cli`; descriptions of it as open source are inaccurate as of this commit. No tests were found for its memory or knowledge modules.
- Redis Agent Memory Server's `V0/` tree is the open reference implementation adjacent to a managed Redis offering; conclusions here apply only to the inspected code, and the managed product may differ.
- Retrieval quality was not measured for any of the six systems added in this round.
- Voyager and Generative Agents are frozen research artifacts, last committed in July and August 2023 respectively. Their reports are historical architectural reviews, not assessments of maintained software.
- HippoRAG's `reproduce/` tree provides benchmark scaffolding, but no raw result artifacts are committed and no published numbers were reproduced here.
- Voyager's and Generative Agents' published evaluations measure task completion and human believability, not retrieval quality; neither repository contains a memory-quality benchmark.
- Generative Agents' retrieval gain weights (`gw = [0.5, 3, 2]`) have no committed ablation; the atlas treats them as hand-tuned constants rather than a derived result.
- No suites were run for the three systems added in this round, and no retrieval quality was independently measured.
- Magic Context's verification precision — how often the verify task correctly marks a stale memory stale, and how often it wrongly confirms one — is not measured anywhere in that repository, and was not measured here. It is the central claim of the design.
- Magic Context reads OpenCode's native session database read-only for its retrospective scanner; that behaviour was read in code but not exercised, and the user-consent story around it was not assessed.
- Pi has no memory subsystem, so its report covers session persistence, compaction, and the extension surface only. Third-party Pi memory plugins other than Magic Context were not reviewed; the db0 integration has a closed backend and is not reviewable on this atlas's terms.
- MetaClaw's committed benchmark fixtures and memory ablation scripts were inspected but not run, and no published numbers were reproduced. Its replay metrics are lexical-overlap proxies; no evidence linking them to task outcomes was found in the repository.
- No memory tests or memory-quality benchmarks were located for nanobot, CowAgent, or GenericAgent. Nothing was run for any of the four systems added in this round.
- GenericAgent's memory documentation is written in Chinese; the axioms and rules quoted in its report are the reviewer's translations, with key terms given in the original. Its cited arXiv technical report was not retrieved or assessed.
- Waku Agent's evals were not run, and its retrieval gate's accuracy was not measured — the false-negative rate, which is the figure that matters, is unknown. No system in the atlas measures its gate.
- Nine repositories examined in the same round have no reports. `razzant/ouroboros` is cited in the append-only-memory-audit pattern for its "honest journal" fix rather than given a report. `truffle-ai/dexto` (Elastic License 2.0), `Arvincreator/project-golem` (a custom source-available licence), and `openyak/openyak` (**no licence file at all**, so all rights reserved by default) each carry a competent but conventional memory subsystem and no mechanism the atlas lacks, so none earns a licence exception. `OtterMind/youclaw` is small. `SixHq/Overture`'s only memory artifacts are `.claude/agent-memory/*/MEMORY.md` — Claude Code's own memory used while developing the repo, not a system it ships. `husu/loom` is an AI JSON Schema documentation generator, `AaronWong1999/hermesclaw` a launcher for running Hermes Agent, OpenClaw, and OpenCode on one WeChat account, and `KeyID-AI/agent-kit` gives MCP clients an email address; none is agent memory.
- Neither Atomic Agent's nor MateClaw's suites were run, and Atomic Agent's evaluation campaign was read but not executed; no scored results were found committed for it. MateClaw's scoping and retrieval ranking were not traced in full.
- Eight repositories examined in the same round have no reports. `beita6969/ScienceClaw` is an OpenClaw derivative whose memory extensions are OpenClaw's `memory-core` and `memory-lancedb`, already covered — its runtime skill authoring is cited in the skills pattern instead. `litanlitudan/skyagi` states that it "implements the idea of Generative Agents" and has been frozen since August 2023, so the original is the better subject. `xvirobotics/metabot` re-exports a memory client whose backend is not in the repository. `Gitlawb/zero` has context reporting and no memory module. `thClaws/thClaws` has a competent 1,644-line file-entry store that adds little beyond systems already covered, and `skalesapp/skales` (~1,542 lines) is Business Source License 1.1 with no distinctive mechanism found. `wanxingai/LightAgent`'s 196-line shared memory with swappable adapters is cited in the pluggable-provider pattern rather than given a report. `rush86999/atom` has roughly 976 lines of memory-named Python inside a 459 MB repository dominated by deployment scripts; no coherent memory design was established, and that is a weaker conclusion than the others here.
- LlamaIndex ships two APIs under the name "memory": the newer block-based `Memory` reviewed here, and an older `ChatMemoryBuffer` family that is conversation-window management and out of scope. Its tests were not run and no memory benchmark was found.
- No suites or benchmarks were run for open-cowork, Gini, Moltis, or Mercury. open-cowork's eval harness was read but not executed, and no scored results were found committed.
- Gini reimplements the Hindsight memory model locally rather than depending on Hindsight; its recall module cites the source paper's equation numbers, but no check was made that this implementation reproduces the published behaviour.
- Moltis's session sanitization was identified from its module documentation; exactly what it strips was not traced, which matters because transcripts can carry secrets, tool output, and previously injected memory blocks.
- Five further repositories examined in this round have no reports: `he-yufeng/CoreCoder` (1,166 lines whose `context.py` is conversation-window compaction with nothing persisted), `chrysb/alphaclaw` (an OpenClaw deployment harness whose only "memory" reference is host RAM), `Intelligent-Internet/ii-agent` (a SaaS agent platform with chat context and caches but no durable memory), `neomjs/neo` (39 AgentOS documents describing a "Memory Core" that does not appear in `src/` — documentation without a reviewable implementation), and `AgentsMesh/AgentsMesh` (a real pgvector-backed block memory with a `memory.retrieve` MCP tool, set aside for now because it is licensed under Business Source License 1.1 rather than an open-source licence).
- Three repositories examined in the same round were judged out of scope and have no reports: `KnockOutEZ/wigolo` (a web crawl, search, and extraction MCP server whose cache holds external content rather than agent belief), `siyuan-note/siyuan` (a note application whose agent kernel contains no memory concept — only conversation compaction — and whose MCP surface is note CRUD), and `netease-youdao/LobsterAI` (which operates OpenClaw's memory rather than having its own, and is covered inside the OpenClaw report).
- Nothing was run for memora or LoongFlow. Memora's pair classifier is the component that matters — its precision determines which memories get hidden — and no measurement of it was found; the dry-run mode makes exactly that measurable, and nothing indicates it has been done. LoongFlow's tests exist under `tests/agentsdk/memory` but were not run, and no comparison of adaptive against fixed temperature was found, though the code is parameterized for it.
- Six repositories examined in the same round have no reports. `TeleAI-UAGI/Awesome-Agent-Memory` is a survey, cited in the correction discussion rather than reviewed as a system. `webbrain-one/webbrain` (368 lines) and `AmeNetwork/aser` (29 lines) are too small to carry a mechanism. `AgentTeam-TaichuAI/ScienceClaw` is 78 lines with no licence file, and is a different repository from the OpenClaw-derived `beita6969/ScienceClaw` noted above. `ArtificialAnalysis/Stirrup` and `howl-anderson/agentsilex` have no memory subsystem.
- `pi-chat` is a separate repository and was not reviewed; the claim that it injects two persistent memory files every turn comes from its documentation, not from its code.

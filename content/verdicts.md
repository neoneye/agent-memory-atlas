---
title: Repo-by-Repo Verdicts
eyebrow: One judgement per system
description: The best idea, biggest risk, most reusable component and maturity impression for every system in the atlas, in one place.
root: ..
page_kind: comparison
---

One entry per system: the best idea, the biggest risk, the component most worth
lifting, an impression of maturity, and who should and should not copy it. These
are judgements rather than marks — the evidence behind each is in that system's
own report, and the mechanisms are compared side by side in the
[comparative report](../compare/).

This page was part of the comparative report until 4 August 2026 and was split
out because it is a different thing: the comparison argues about mechanisms
across the corpus, and this argues about whether any one system is worth your
time. Reading it end to end is not the point; find the system you are weighing.

<!-- BEGIN GENERATED VERDICT COUNT -->
**This page covers all 298 reports.**
<!-- END GENERATED VERDICT COUNT --> Six judgements each: the best idea,
the biggest risk, the most reusable component, an impression of maturity, and
the two that matter most to a reader deciding — when to study it and when to
walk away.

It is prose — written by a model, like everything else here that is not
generated; the [review method](../methodology/per-repo-report-format/#who-writes-these)
says who and what follows from it — unlike the [capability index](../capabilities/) and the
[comparative matrix](../compare/#2-comparative-matrix), which are derived from every report's frontmatter
by a script and complete by construction. So completeness here is a fact about today rather
than a guarantee: nothing fails the build if the next report arrives without an
entry, and `scripts/check_homepage.py` only notices the count in the sentence
going stale. A verdict missing in future means nobody wrote the paragraph,
not that a system was judged and found unremarkable — the same distinction the
[rubric](../methodology/atlas-rubric/) enforces for capability marks, where the
build *does* fail if a report omits the key.

That distinction runs through the whole site, and it is worth seeing once
because it decides how much weight a completeness claim on any page can carry:

```mermaid
flowchart TD
    R["Every report<br/>frontmatter and prose, each pinned to a commit"]
    R --> GEN["generate_index.py<br/>generate_matrix.py"]
    R --> HAND["Written as prose<br/>this page, the patterns, the comparative prose"]
    GEN --> AZ["A–Z index"]
    GEN --> MX["Comparative matrix"]
    GEN --> CI["Capability index"]
    AZ --> CONST["Complete by construction<br/>a new report shows up without anyone writing a line"]
    MX --> CONST
    CI --> CONST
    HAND --> TODAY["Complete as a fact about today<br/>a new report shows up only if someone writes the paragraph"]
    CHK["check_verdict_anchors.py<br/>check_homepage.py"] -.->|"catches a dead link or a stale count"| TODAY
    CHK -.->|"cannot notice a verdict nobody wrote"| TODAY
```

The dotted edges are the honest part. A check can tell you that something
written went wrong; nothing tells you that something was never written. So the
generated pages are a guarantee and this one is a report on a state of affairs,
and the two should not be read with the same confidence.

<div class="filter-row" role="group" aria-label="Find a system verdict">
  <label class="filter-legend" for="verdict-search">Find</label>
  <input class="matrix-search" id="verdict-search" type="search" autocomplete="off"
         placeholder="system name…" aria-describedby="verdict-count">
</div>

<p class="result-count" id="verdict-count" aria-live="polite"></p>

## System verdicts

### [`mem0`](../systems/mem0/)
- Best idea: pragmatic additive extraction plus hybrid retrieval/entity boost.
- Biggest risk: extracted facts are not strongly modeled as uncertain claims.
- Most reusable component: `Memory.add()` / `_add_to_vector_store()` pipeline.
- Maturity impression: practical SDK core, with some advanced features outside OSS.
- Study when: building a drop-in memory library.
- Do not copy when: you need rigorous trust/correction semantics.

### [`langmem`](../systems/langmem/)
- Best idea: memory as LangGraph store tools with schema-driven extraction.
- Biggest risk: it is a primitive layer, not a full memory policy.
- Most reusable component: `create_manage_memory_tool()` and namespace templates.
- Maturity impression: clean and framework-native.
- Study when: already building on LangGraph.
- Do not copy when: you need a standalone memory service with built-in quality controls.

### [`honcho`](../systems/honcho/)
- Best idea: event stream to derived working representation.
- Biggest risk: operational complexity and background consistency.
- Most reusable component: message ingestion plus deriver/representation flow.
- Maturity impression: serious service architecture with meaningful tests.
- Study when: modeling users/peers/sessions over time.
- Do not copy when: all you need is a local memory file.

### [`engram`](../systems/engram/)
- Best idea: local SQLite/FTS MCP memory with conflict-oriented writes.
- Biggest risk: lexical retrieval and agent-mediated judgment may hit limits.
- Most reusable component: `AddObservation()` and MCP `handleSave()`.
- Maturity impression: compact, inspectable, purpose-built for coding agents.
- Study when: building local developer-agent memory.
- Do not copy when: you need hosted multi-tenant vector retrieval.

### [`mempalace`](../systems/mempalace/)
- Best idea: verbatim drawers as the authoritative memory, with hybrid retrieval and extracted indexes as boosts.
- Biggest risk: raw stores get large/noisy and do not resolve contradictions by themselves.
- Most reusable component: `search_memories()` plus `_hybrid_rank()`, and the mining/write path around deterministic IDs.
- Maturity impression: operationally mature local system with broad tests, integrations, repair tooling, and benchmark artifacts.
- Study when: building local-first coding-agent memory or testing whether extraction is actually needed.
- Do not copy when: you need compact verified user facts as the primary memory surface.

### [`swafra`](../systems/swafra/)
- Best idea: compact source-diverse hybrid retrieval with explicit graph exploration and no required cloud model.
- Biggest risk: non-atomic global JSON state plus a benchmark that scores far more than the advertised `k`.
- Most reusable component: the conceptual `search_knowledge()` -> `graph_walk()` -> best-per-source composition, not the persistence implementation.
- Maturity impression: promising alpha prototype with significant code/docs/artifact drift and no ordinary tests.
- Study when: learning how little code a local MCP graph-RAG memory can require.
- Do not copy when: you need concurrency, trustworthy evals, scope isolation, correction, bounded prompts, or durable storage.

### [`llm-wiki-memory`](../systems/llm-wiki-memory/)
- Best idea: recoverable hook capture plus explicit federated write targets over inspectable Markdown/git memory.
- Biggest risk: LLM-distilled atoms become active guidance without candidate/verified/rejected state or contradiction protection.
- Most reusable component: `wiki-mutate.mjs` / `wiki-search*.mjs` with the flush, compile, scope, and commit orchestration around them.
- Maturity impression: operationally mature local coding-agent system with unusually broad failure-path and federation tests; retrieval quality is not benchmarked.
- Study when: building cross-agent local project memory, lifecycle capture, deterministic wiki placement, or self-healing maintenance.
- Do not copy when: you need high-stakes truth governance, large-corpus query performance, multi-tenant access control, or privacy-grade deletion.

### [`rainbox`](../systems/rainbox/)
Disclosure: RainBox is the atlas author's own project; this verdict is a self-assessment against the shared rubric.

- Best idea: claim/evidence memory tied to governed writes (single `record_belief` path, five-actor trust model, tombstones, conflict detection), review UI, retrieval telemetry, feedback, and eval gates.
- Biggest risk: active compact claims can steer behavior while losing nuance from original source context; no automatic candidate extraction means claims enter only through explicit writes.
- Most reusable component: `MemoryClaim`/`MemoryEvidence`/`MemoryRejectedValue`/`RetrievalEvent` model, `record_belief`/`correct_belief` governed write paths, `retrieve_memories_hybrid()`.
- Maturity impression: strong app-integrated memory subsystem with trust/correction machinery comparable to Verel's correctness properties, broad tests, and operator workflows.
- Study when: building an assistant product where memory must be inspectable, governable, and protected against model-write laundering.
- Do not copy when: you need a small embeddable library, raw transcript recall as the primary memory layer, or `epistemic_confidence`/`retrieval_strength` driving ranking (these columns are schema groundwork only; Tier-1 ranking still uses `confidence`).

### [`letta`](../systems/letta/)
- Best idea: core vs archival vs conversation memory inside the runtime.
- Biggest risk: agent-editable core memory without a strong truth model.
- Most reusable component: memory block compile/mutation and patch-style edits.
- Maturity impression: deep runtime integration with compatibility complexity.
- Study when: building an agent platform, not just a memory backend.
- Do not copy when: you want a small independent memory service.

### [`supermemory`](../systems/supermemory/)
- Best idea: product-grade API shape around documents, chunks, memory entries, spaces, profiles, SDKs, and MCP.
- Biggest risk: the hosted backend core is not visible here.
- Most reusable component: schemas and adapter surfaces.
- Maturity impression: polished integration surface; implementation evidence incomplete.
- Study when: designing public APIs and memory UX.
- Do not copy when: you need open implementation details for extraction/ranking.

### [`verel`](../systems/verel/)
- Best idea: explicit trust, confidence, retrieval strength, rejected tombstones, and defensive recall.
- Biggest risk: complexity.
- Most reusable component: `MemoryRecord`, `LocalMemory.write()`, and `recall_budgeted()`.
- Maturity impression: research-grade correctness focus with strong targeted tests.
- Study when: wrong memory is costly.
- Do not copy wholesale when: you need a fast MVP.

### [`hindsight`](../systems/hindsight/)
- Best idea: four independent recall arms plus task-specific fusion over evidence-backed facts and observations.
- Biggest risk: LLM-extracted and consolidated claims can become durable without an explicit truth state.
- Most reusable component: retain pipeline and `engine/search/` fusion/reranking stack.
- Maturity impression: service-grade implementation with unusually strong operational coverage.
- Study when: building a hosted retain/recall/reflect service.
- Do not copy when: a small local store can meet the evaluated retrieval need.

### [`graphiti`](../systems/graphiti/)
- Best idea: bi-temporal relationship edges that close validity intervals without erasing history.
- Biggest risk: entity-resolution or invalidation mistakes reshape a large portion of the graph.
- Most reusable component: episode/evidence model plus temporal edge maintenance.
- Maturity impression: substantial graph library with multiple drivers and deep search configuration.
- Study when: facts, relationships, and their validity change over time.
- Do not copy when: memory is mostly independent notes or stable preferences.

### [`mastra-observational-memory`](../systems/mastra-observational-memory/)
- Best idea: compute observation/reflection buffers early, persist exact coverage, and activate without blocking.
- Biggest risk: progressive summary drift and in-process-only locking.
- Most reusable component: marker/range-aware buffered activation.
- Maturity impression: deeply integrated and heavily tested framework feature.
- Study when: long agent conversations exceed model context.
- Do not copy when: exact evidence retrieval is the primary requirement.

### [`memos`](../systems/memos/)
- Best idea: mount textual, preference, skill, KV-cache, and parametric memory as one cube.
- Biggest risk: one abstraction hides uneven backend guarantees and maturity.
- Most reusable component: memory-cube packaging and textual-to-activation scheduling.
- Maturity impression: ambitious research/engineering substrate with many configurations.
- Study when: exploring model-native memory or deployable heterogeneous memory bundles.
- Do not copy when: a single audited text store is sufficient.

### [`basic-memory`](../systems/basic-memory/)
- Best idea: canonical human-editable Markdown with graph/search state treated as rebuildable projection.
- Biggest risk: bidirectional file/database synchronization and direct agent writes to canonical knowledge.
- Most reusable component: accepted-note transaction/reconciliation boundary and typed MCP client flow.
- Maturity impression: operationally serious local/cloud knowledge system with broad parity tests.
- Study when: people and agents must share portable project knowledge.
- Do not copy when: humans never edit memory and filesystem ownership adds no value.

### [`agentmemory`](../systems/agentmemory/)
- Best idea: zero-LLM hook capture plus compact-first hybrid search and explicit expansion.
- Biggest risk: a large optional surface and similarity-based supersession without an epistemic review state.
- Most reusable component: `mem::observe`, `HybridSearch`, and `mem::smart-search`.
- Maturity impression: ambitious, heavily tested coding-agent runtime with many operational paths.
- Study when: hooks, local capture, hybrid recall, and later consolidation need to coexist.
- Do not copy when: a small auditable store is enough or shared-by-default agent memory is unsafe.

### [`tencentdb-agent-memory`](../systems/tencentdb-agent-memory/)
- Best idea: progressive disclosure from raw evidence through records, scenes, persona, and navigable tool-output maps.
- Biggest risk: non-atomic JSONL/store updates and fail-open deduplication can create loss or contradictions.
- Most reusable component: L0/L1/L2/L3 context split and symbolic offload drill-down.
- Maturity impression: inventive OpenClaw/Hermes integration, but central lifecycle tests and reproducible benchmark evidence are thin.
- Study when: tool-heavy sessions exceed the context window and raw drill-down must remain possible.
- Do not copy when: authoritative cross-store consistency, multi-tenant boundaries, or verified memory are required.

### [`cognee`](../systems/cognee/)
- Best idea: source-preserving, ontology-aware graph/vector pipelines with provenance rollback behind a small remember/recall API.
- Biggest risk: probabilistic extraction and a large adapter/configuration surface create cross-store consistency and policy burden.
- Most reusable component: permanent `remember()` as add-plus-cognify, dataset authorization, and pipeline-run rollback.
- Maturity impression: substantial platform with broad tests and transparent but preliminary BEAM artifacts.
- Study when: agents need multimodal ingestion, typed knowledge graphs, ontologies, dataset permissions, and backend choice.
- Do not copy when: a small local evidence store and lexical/vector retrieval satisfy the requirement.

### [`claude-mem`](../systems/claude-mem/)
- Best idea: durable hook queue, canonical SQLite commit, then best-effort semantic/cloud projections and bounded timeline injection.
- Biggest risk: generated observations become active without epistemic review, and ordinary text search does not fuse its FTS and Chroma capabilities.
- Most reusable component: `pending_messages` lifecycle plus `ResponseProcessor` commit/acknowledgement ordering.
- Maturity impression: operationally mature coding-agent sidecar with broad failure-path tests; memory quality is not benchmarked.
- Study when: cross-session coding context must be captured automatically without blocking the agent.
- Do not copy when: explicit writes are sufficient, hooks are unavailable, or high-stakes facts require verification before use.

### [`holographic`](../systems/holographic/)
- Best idea: deterministic SHA-256-derived phase vectors and algebraic multi-entity queries, with no embedding model to version.
- Biggest risk: three unhelpful ratings silently drop a fact below the retrieval floor forever.
- Most reusable component: `encode_atom`/`bind`/`unbind`, the FTS5 query sanitizer, and the refcounted shared-connection registry.
- Maturity impression: compact and fully readable, with real production scar tissue around concurrency, but no benchmark and an unmeasured HRR contribution.
- Study when: you want compositional structure without an embedding service, or a worked example of why truth and usefulness must be separate fields.
- Do not copy when: you need scope, provenance, correction, or any feedback mechanism that is not also a deletion mechanism.

### [`hermes-agent`](../systems/hermes-agent/)
- Best idea: bounded curated memory frozen into the prompt at session start, with overflow refused and consolidation demanded in-turn.
- Biggest risk: whatever the model writes is authoritative in every later session, and budget-driven eviction is unlogged.
- Most reusable component: the frozen-snapshot pattern, `_detect_external_drift`, and the staged write-approval gate.
- Maturity impression: heavily defended file layer whose guards cite the incidents that produced them; the provider contract is less complete than the store.
- Study when: prompt-cache cost is material, or you need memory that cannot grow without someone deciding what to drop.
- Do not copy when: you need verification, tombstones, substring-free identity, or a provider contract that can honour deletion.

### [`openviking`](../systems/openviking/)
- Best idea: three retrievable granularities on one record, plus hotness kept strictly separate from confidence.
- Biggest risk: extraction becomes durable context with no verification tier, and published numbers are not backed by committed artifacts.
- Most reusable component: `hotness_score`, `type_quota_recall`, and the `user_space` / `peers/<id>` isolation convention.
- Maturity impression: a large, seriously engineered platform with real multi-tenancy and the most complete benchmark harness in the atlas.
- Study when: you need multimodal ingestion, tenant isolation, skills and resources unified with memory, or backend choice.
- Do not copy when: you need a small embeddable layer, verified memory, or a licence compatible with closed distribution — this is AGPL-3.0.

### [`redis-agent-memory-server`](../systems/redis-agent-memory-server/)
- Best idea: TTL-native working memory promoting into deduplicated long-term memory, with retention expressed as a real policy.
- Biggest risk: forgetting is deletion without tombstones, so anything forgotten can be re-extracted.
- Most reusable component: `select_ids_for_forgetting`, the three-layer dedupe chain, and `_semantic_merge_group_is_cohesive`.
- Maturity impression: vendor-neutral reference implementation with unusually well-targeted tests on the risky logic.
- Study when: you want the working/long-term split done carefully, or a retention policy you can defend to a user.
- Do not copy when: cognitive memory types would be mistaken for a trust model, or deletion must be durable.

### [`byterover`](../systems/byterover/)
- Best idea: counting exactly what an LLM rewrite would delete, then merging the loss back automatically.
- Biggest risk: the Elastic License 2.0 forbids hosted redistribution, and the memory core itself has no trust, scope, or correction model.
- Most reusable component: `detectStructuralLoss` / `resolveStructuralLoss`, and the immutable `DECISIONS` category.
- Maturity impression: a thin memory primitive attached to a more thoughtful knowledge-curation layer, with no visible tests on its best idea.
- Study when: an LLM is allowed to rewrite stored knowledge and you need a cheap deterministic guard.
- Do not copy when: you need durable beliefs, ranked retrieval, or an OSI-compatible licence.

### [`openclaw`](../systems/openclaw/)
- Best idea: scope composed inseparably into every predicate, and 567 lines spent keeping the runtime's own envelope out of memory.
- Biggest risk: a vector-only reference backend for content full of names and identifiers, with auto-capture that can undo deletions.
- Most reusable component: `memory-capture-sanitization.ts`, `scopedPredicate`, and the doctor-contract idea.
- Maturity impression: test lines far exceed implementation lines; the plugin contract is mature, the memory model deliberately minimal.
- Study when: building a host runtime with swappable memory, or capturing from a channel that wraps messages in scaffolding.
- Do not copy when: you need hybrid retrieval, per-user scope inside an agent, or deletion that survives auto-capture.

### [`atomic-agent`](../systems/atomic-agent/)
- Best idea: numbered cross-phase invariants cited from the schema into a design document, and votes kept as append-only events with derived scores.
- Biggest risk: an elaborate opt-in surface whose evaluation campaign has no committed results.
- Most reusable component: the invariant-citation practice, the `vote_events` shape, and the surfaced-id allowlist in `neighbor-evolver.ts`.
- Maturity impression: the most specification-like memory system in the atlas — design plan, acceptance criteria, implementation ledger, and features default-off pending evidence.
- Study when: you want memory built as an engineering artifact rather than an accretion, or a feedback design that keeps every downstream option open.
- Do not copy when: you need a value tombstone or an established scope model; neither surfaced here.

### [`mateclaw`](../systems/mateclaw/)
- Best idea: a provider SPI that carries an owner key, with retry and metrics as decorators over every backend.
- Biggest risk: the contract still has no deletion hook, and contradiction is detected without a resolution path.
- Most reusable component: the SPI shape with scoped overloads and default methods, and `spi/decorator/`.
- Maturity impression: built in the enterprise-framework tradition — layered, dependency-injected, event-driven, and conventional in the ways that tradition is good at.
- Study when: designing a memory contract third parties will implement, or wondering who owns provider resilience.
- Do not copy when: you need the deletion half of the governance story, which is absent.

### [`llamaindex`](../systems/llamaindex/)
- Best idea: one token budget split between chat history and blocks, with each block truncating itself to fit.
- Biggest risk: no provenance, correction, or scope, and long-term capture is triggered by conversation length rather than importance.
- Most reusable component: the `BaseMemoryBlock` contract — `aget`, `aput`, `atruncate` — and the explicit budget split.
- Maturity impression: a widely deployed framework whose newer block API is a real memory layer, shipped alongside an older window-management API of the same name.
- Study when: you need a memory component contract, or a budget that several contributors must share.
- Do not copy when: facts must be traceable, correctable, or scoped — those are left to the application.

### [`open-cowork`](../systems/open-cowork/)
- Best idea: a committed memory benchmark whose queries assert forbidden hits as well as expected ones, scored against the assembled prompt prefix.
- Biggest risk: the harness exists but no scored results are committed, and no trust state guards extraction.
- Most reusable component: `memory-eval-harness.ts` — the eval-case shape is largely independent of the rest of the system.
- Maturity impression: a well-factored memory subsystem whose evaluation thinking is ahead of most of the atlas.
- Study when: you need to turn "our memory works" into something a CI job can check.
- Do not copy when: you need verification or correction semantics; neither appears in the module set.

### [`gini-agent`](../systems/gini-agent/)
- Best idea: bi-temporal units with `rejected` and `conflicted` states, four RRF-fused recall channels, and architecture decisions recorded as ADRs.
- Biggest risk: `conflicted` is modelled with no visible workflow to resolve it, and rejection has no value-level tombstone.
- Most reusable component: the `memory_units` schema, and the ADR practice itself.
- Maturity impression: a faithful local reimplementation of a published memory model, with unusually good written rationale.
- Study when: you want a trust-and-time-aware unit schema you can implement in plain SQLite.
- Do not copy when: you need the conflict workflow the schema implies but does not ship.

### [`moltis`](../systems/moltis/)
- Best idea: a no-embeddings mode that is a constructor and a predicate rather than a degraded state, plus content-hash file addressing.
- Biggest risk: exported session transcripts share one index and one rank with curated notes, with nothing distinguishing them.
- Most reusable component: `MemoryManager::keyword_only()` / `has_embeddings()`, and the single `sync()` chokepoint.
- Maturity impression: carefully built, with feature-gated backends and committed plans naming its own gaps.
- Study when: memory and documents should be one substrate, or you need a genuinely offline path.
- Do not copy when: a chunk is not a good enough unit — there is no claim, status, or correction record.

### [`mercury-agent`](../systems/mercury-agent/)
- Best idea: three independent grades — confidence, importance, durability — plus a subconscious tier and a user-facing learning pause.
- Biggest risk: `dismissed` is a boolean, so dismissal is not durable against re-extraction.
- Most reusable component: the record model, especially the durability/importance split and the narrowed candidate type.
- Maturity impression: small but opinionated, with an operator review page and clear provenance kinds.
- Study when: building personal memory where different facts should live for different lengths of time.
- Do not copy when: automatic extraction can regenerate what a user dismissed.

### [`waku-agent`](../systems/waku-agent/)
- Best idea: a small-model gate that decides whether to retrieve at all, returns the query when it says yes, and fails open when it errors.
- Biggest risk: the gate's own accuracy is unmeasured, and a false negative is invisible — eleven committed cases establish that it parses, not that it decides correctly, and the project's whole thesis rests on the second.
- Most reusable component: `should_retrieve()` — the fail-open branch and the recorded reason included.
- Maturity impression: ~800 lines of core memory code under sixty model-free eval files, unusually clear about why each expensive step is conditional, and a maintainer who files the criticism as an issue and states the error asymmetry a single accuracy number would hide. Facts became a swappable backend behind one contract, and the repo now ships a memory "arena" that races SQLite, Supabase, mem0, Zep and LangMem against a no-memory control on four-outcome scoring — a genuinely careful eval whose one gap is that no results are committed.
- Study when: retrieval runs every turn and you suspect it is hurting as often as helping.
- Do not copy when: you need a correction that survives the next automatic write. `manage_memory` and the dashboard both correct a row and neither records that a value was rejected, so the consolidation pass re-reads the same chat log and can restore what the user just removed.

### [`metaclaw`](../systems/metaclaw/)
- Best idea: candidate retrieval policies replayed offline and promoted only on non-regression across eight metrics.
- Biggest risk: the loop optimizes lexical-overlap proxies, and its promotion thresholds are hand-chosen constants.
- Most reusable component: `promotion.py`'s `MemoryPromotionCriteria` and the replay-then-gate loop in `self_upgrade.py`.
- Maturity impression: substantial and unusually well evidenced, with committed benchmark fixtures and dedicated memory ablations.
- Study when: you cannot justify your retrieval weights and want a safe way to change them.
- Do not copy when: you need trust semantics — the memory model has no rejected state and no verification path.

### [`nanobot`](../systems/nanobot/)
- Best idea: two cursors over an append-only archive, with a Dream pass that refuses to advance after tool errors.
- Biggest risk: durable claims carry no provenance back to the evidence that produced them.
- Most reusable component: the dual-cursor split, the failure-aware advance gate, and the durable-file allowlist for audit commits.
- Maturity impression: compact and carefully reasoned, with unusually good design documentation and no visible memory tests.
- Study when: a fast producer feeds a slow consolidator, or you want git history that reads as a record of belief.
- Do not copy when: memory must grow past what fits in every prompt, or must be scoped per project.

### [`cowagent`](../systems/cowagent/)
- Best idea: a dated intermediate layer that gives consolidation a naturally bounded unit, plus written distillation rules and a dream diary.
- Biggest risk: two chained lossy summarizations with no loss detection, and recency-wins conflict resolution.
- Most reusable component: the daily-bucket pipeline, the distillation rule table, and the self-healing FTS5 state check.
- Maturity impression: practical and well documented, with real hybrid retrieval and no visible memory tests.
- Study when: you want consolidation you can inspect by opening a file for a given day.
- Do not copy when: scope matters — `scope` defaults to `shared` — or corrections must be reviewable.

### [`genericagent`](../systems/genericagent/)
- Best idea: "No Execution, No Memory", and an explicit ROI model for what earns a place in always-injected context.
- Biggest risk: every rule is prose, with no enforcement, no audit, and no record of the verification each write claims.
- Most reusable component: the four axioms and the cleanup SOP's ROI test and deletion categories.
- Maturity impression: a small framework whose memory thinking is considerably more developed than its memory machinery.
- Study when: designing the policy layer of a memory system, or deciding what belongs in permanent context.
- Do not copy when: wrong memory is costly and you need the rules enforced rather than requested.

### [`magic-context`](../systems/magic-context/)
- Best idea: memories mapped to backing files and re-verified when git reports those files changed, with lifecycle and verification on separate axes.
- Biggest risk: no rejected-value tombstone, so archived memories can be re-derived; and the verification verdict is still an LLM call.
- Most reusable component: `dreamer/verify-gate.ts`, the two-axis state model, and `(memory_id, model_id)` embedding keys.
- Maturity impression: the heaviest test posture in the atlas — 473 test files, seventy tested migrations, CAS-race suites, fail-closed registration.
- Study when: memory describes an inspectable artifact and you want trust to be observed rather than judged.
- Do not copy when: you need a small memory layer; most projects want the verify gate and the state model, not the whole platform.

### [`pi`](../systems/pi/)
- Best idea: deterministic `readFiles`/`modifiedFiles` manifests attached to compaction entries, derived from tool calls rather than from the summarizing model.
- Biggest risk: no memory contract at all, so scope and deletion have nowhere to live and every plugin reinvents indexing.
- Most reusable component: the typed session-entry model and the result-returning extension events.
- Maturity impression: actively developed, well-factored harness; memory is deliberately out of scope.
- Study when: designing a host runtime, or thinking about what branchable sessions mean for memory.
- Do not copy when: you expect third-party memory — define scope and deletion in the interface before plugins exist.

### [`hipporag`](../systems/hipporag/)
- Best idea: Personalized PageRank diffusion replaces hop planning, with IDF-penalized seeding and a weak dense prior.
- Biggest risk: no scope, trust, provenance, or temporal model, and a wrong extracted edge has graph-wide blast radius.
- Most reusable component: `graph_search_with_fact_entities()` plus `run_ppr()`, and synonymy-as-edges instead of entity merging.
- Maturity impression: actively maintained research framework with a strong reproduction tree and thin unit tests.
- Study when: recall must cross documents associatively, or entity-resolution merges have burned you.
- Do not copy when: you need agent memory rather than corpus QA — scope, correction, and time all have to be added.

### [`voyager`](../systems/voyager/)
- Best idea: memory written only after the environment verifies the procedure worked.
- Biggest risk: a frozen 2023 artifact that generalizes from a single verified run and keeps no failure memory.
- Most reusable component: the verified write gate, and description-indexed / code-retrieved storage.
- Maturity impression: a 127-line memory subsystem inside a research agent; unmaintained since July 2023.
- Study when: your agent's actions have observable outcomes and competence is worth remembering, not just facts.
- Do not copy when: procedures will be executed outside a sandbox, or success is a matter of judgment rather than observation.

### [`generative-agents`](../systems/generative-agents/)
- Best idea: consolidation triggered by accumulated significance rather than by a timer or token count.
- Biggest risk: its famous retrieval weights are hand-tuned constants, and reflections share one pool with observations.
- Most reusable component: the reflection trigger, and the three-signal retrieval structure — recalibrated, with time-based recency.
- Maturity impression: the field's reference architecture, frozen since August 2023 and never engineered for production.
- Study when: you want to understand where most of this atlas came from, or need a consolidation schedule that tracks salience.
- Do not copy when: you need any operational property at all — there is no scope, correction, deletion, or index.

### [`a-mem`](../systems/a-mem/)
- Best idea: small linked notes whose organization can be reconsidered when new memory arrives.
- Biggest risk: rank positions are used as note identities, allowing evolution to mutate the wrong neighbor.
- Most reusable component: the proposed Zettelkasten evolution protocol, after replacing direct mutation with validated change proposals.
- Maturity impression: research prototype; tests are shallow around the most consequential behavior and benchmarks live elsewhere.
- Study when: researching adaptive linked-note organization.
- Do not copy as a production core without stable IDs, canonical durability, scope, provenance, transactions, and trust state.

### [`memora`](../systems/memora/)
- Best idea: automated supersession that defaults to a dry run, so a correction sweep is previewed before it hides anything.
- Biggest risk: supersession without a tombstone, in a system that ingests documents and images and can therefore re-ingest what it hid.
- Most reusable component: the six-way relation vocabulary with neutral A/B presentation, and `dry_run: bool = True` as the default posture.
- Maturity impression: substantial for its age, with the sophistication concentrated in what happens to memories after they are written.
- Study when: you are about to run an automatic dedupe or supersession pass over a store you cannot afford to damage.
- Do not copy when: you need trust state, scope isolation, or a correction that survives re-ingestion.

### [`loongflow`](../systems/loongflow/)
- Best idea: recall by Boltzmann sampling at a temperature driven by the store's measured diversity — the only stochastic retrieval in the atlas.
- Biggest risk: selection quality is bounded entirely by a `score` nothing validates, and the same query can return different memories with no seed or replay path.
- Most reusable component: the diversity-to-temperature loop, including the 20% smoothing and the explicit min/max bounds.
- Maturity impression: two unrelated memory models in one package — a conventional tier stack and a genuinely novel selection mechanism — with the control constants undefended.
- Study when: memory feeds a search or generate-and-test loop and deterministic top-*k* keeps returning the same dead end.
- Do not copy when: recall must be reproducible, or the memories are facts rather than attempts.

### [`core-memory`](../systems/core-memory/)
- Best idea: epistemic grounding caps the confidence ladder, so a speculative record cannot reach canonical status by any amount of use.
- Biggest risk: correction is record-keyed. `tombstone_bead` is documented as the single-bead semantic action and keyed on a bead id, so supersession and rejection do not stop re-extraction from the retained turns that produced the value.
- Most reusable component: the grounding-to-ceiling table plus the monotonic class, which is a lookup and a `min()`.
- Maturity impression: the largest and most specification-like system in the atlas, six of seven capability marks, 412 test files, and its distinctive claim asserted end to end — a promoted speculative bead stays capped at B across an index rebuild.
- Study when: you need to explain why an incorrect memory never became permanent, and want the answer to be structural.
- Do not copy when: you cannot carry the surface — thirteen subpackages and forty store-ops modules is a real maintenance budget.

### [`memanto`](../systems/memanto/)
- Best idea: a conflict workflow that terminates in a human decision, including `keep_both` and a human-authored `manual` resolution.
- Biggest risk: detection is one unmeasured LLM pass, and resolution deletes without a tombstone, so scheduled extraction can undo it.
- Most reusable component: the five-action resolver plus the bounded-scan instruction that keeps the nightly pass linear.
- Maturity impression: a real service with CLI, web UI, MCP and four framework integrations, and an unusually on-topic test tree.
- Study when: you have contradiction detection and no idea what to do with the flags it produces.
- Do not copy when: you need trust state or ranking you can inspect — storage is the vendor's own service.

### [`memory-engine`](../systems/memory-engine/)
- Best idea: agents are access-control principals, and a delegated agent grant clamps to `least(agent, owner)` at every path, so over-granting cannot escalate.
- Biggest risk: no trust state, supersession, or tombstone — it governs who may read a memory and knows nothing about whether it is true.
- Most reusable component: the `tree_access` model with the agent clamp, and authorization evaluated inside the ranking query.
- Maturity impression: a serious database-native service with committed SQL benchmarks, access diagnostics, and unusually candid design notes including a negative result on RLS.
- Study when: agents write to shared memory and you cannot say from the schema which memories each may read.
- Do not copy when: you need correction semantics — `replace` overwrites in place and leaves no history.

### [`ai-memory`](../systems/ai-memory/)
- Best idea: a `Handoff` with an open/accepted/expired lifecycle, typed sender and recipient, and an `open_questions` list — memory of what is *not* known.
- Biggest risk: hooks re-capture every session and supersession is page-keyed, so a deleted page returns through the path that first produced it.
- Most reusable component: `handoff.rs`, which is small and independent of the rest of the system.
- Maturity impression: broad and well packaged, with harness adapters for eight agents and committed prior-art analyses of four systems in this atlas.
- Study when: work is interrupted and resumed in a different harness, and re-explaining the state is the actual cost.
- Do not copy when: you need trust state — and do not assume its `do_not_answer_from` tag does anything; it appears only in a test fixture.

### [`ctx`](../systems/ctx/)
- Best idea: a write-scope guard on the consolidation pass, with one crossing gated on the disposition rather than the caller, plus refusals that carry a registered reason.
- Biggest risk: correction is structural folding with no tombstone, so a dream can re-propose what a human folded away.
- Most reusable component: `WriteScope`, and the corrupted-artifact regression corpus, which any system with an LLM rewrite path could adopt in an afternoon.
- Maturity impression: dense tests in the packages that matter, an append-only ledger, and a 61,000-line CLI wrapped around them.
- Study when: a background model pass can write into the user's own repository and you have no answer for where it may write.
- Do not copy when: you need ranked retrieval — there is no ranker, only progressive disclosure over files.

### [`optmem`](../systems/optmem/)
- Best idea: no background work at all — consolidation is requested inline in the output of `note`, so write-to-readable lag is zero and nothing rewrites memory unobserved.
- Biggest risk: no licence file, so nothing here is reusable; and a wrong memory is permanent, because the log is never edited.
- Most reusable component: the `cover` geometry — one parameter, closed form, and no compression at all while everything fits.
- Maturity impression: 860 lines with a 611-line test file, and the only committed footprint-and-latency figures in the atlas.
- Study when: you are about to build a consolidation queue and have not asked whether you need one.
- Do not copy when: you need to fix a mistake — OptMem can always tell you what was written and can never repair it.

### [`memvid`](../systems/memvid/)
- Best idea: immutability as the correction mechanism — a supersession is a link, not an overwrite, so `get_at_time` and session replay come from the format rather than a bi-temporal schema.
- Biggest risk: the loudest quality claims in the atlas ("+35% SOTA on LoCoMo") with no committed raw artifacts found at this commit.
- Most reusable component: `entity:slot` cards with a declared cardinality, which turns contradiction detection into a lookup and tells you whether a second value is a conflict or an addition.
- Maturity impression: a serious file format with WAL, footer recovery, a 1,687-line doctor, and a deployment story of one binary and one file.
- Study when: you need to answer "what did the agent believe when it did that", which nothing else here can.
- Do not copy when: you need multi-tenant scope or epistemic status — the ACL is thin and there is no trust state.

### [`memoryos`](../systems/memoryos/)
- Best idea: the promotion rule is a written formula with named coefficients, and the LoCoMo harness ships with its dataset committed beside it.
- Biggest risk: heat sums frequency, interaction length and recency into one scalar with weights of 1/1/1, and a second LFU counter can disagree with it about the same segment.
- Most reusable component: the shape — tiers with an explicit, computable promotion signal — rather than the formula.
- Maturity impression: a legible research implementation with an MCP server, a vector variant and a playground around a 2,100-line core.
- Study when: you want the tiered architecture in a form small enough to read in an afternoon, or a base for experiments on promotion policy.
- Do not copy when: real users are involved — no provenance, no correction, no audit, and a merged profile string makes a deletion request unanswerable.

### [`memu`](../systems/memu/)
- Best idea: rank the slice, return the file — the embed/search unit and the context payload are different sizes, and a file scores as the max of its segments.
- Biggest risk: no epistemic model at all, and no scope key in a layer that serves seven different hosts from one store.
- Most reusable component: the three-method backend protocol, plus keyset pagination on immutable domain identity so a walk under concurrent writes neither skips nor repeats.
- Maturity impression: unusually disciplined for its size — schema comments cite the ADRs that produced them, and a denormalized column carries its safety argument; the limit of that discipline is a decision record asserting a telemetry disclosure that is not in the tree.
- Study when: you want one memory across several coding agents and a read path that is cheap, predictable and model-free.
- Do not copy when: memory has to be trusted, corrected, or separated between users — or when you install for other people and cannot make a vendor-telemetry disclosure the install guide omits.

### [`openworker`](../systems/openworker/)
- Best idea: an explicit when-to-remember policy, written because models without one fail bimodally — they either never save or save what the repository already records.
- Biggest risk: none of it is enforced or observable, so the first sign the model stopped following the policy is memory quality nobody can explain.
- Most reusable component: the guidance paragraph itself, especially "use absolute dates, never yesterday" and "don't save what the repo already records".
- Maturity impression: a large, carefully built agent with permissions, audit and unattended operation, and a memory subsystem of 260 lines that touches none of it.
- Study when: deciding whether to spend the next day on a pipeline or on the prompt that governs one.
- Do not copy when: you need ranking, a correction record, or any guarantee the policy was followed.

### [`qwen-code`](../systems/qwen-code/)
- Best idea: a team tier committed to the repository, with secret-bearing writes to it refused unconditionally — the guard ignores the feature flag that governs the tier, because the directory is under version control either way.
- Biggest risk: three forget paths and no value-level tombstone, in a system whose extraction re-reads the sessions that produced the memory.
- Most reusable component: the `pinned/` directory — a path the consolidation and extraction agents are refused by the permission layer, not merely told to skip in their prompts, with literal and symlink-resolved containment. In a design with three forget paths and no tombstone, it is the one place a person's memory outranks the background pass. The extraction cursor with a processed offset and the `noop` outcome status are the close seconds.
- Maturity impression: ~9,000 lines with a test beside nearly every module, and comments that read as scar tissue — per-operation kill signals for git, `execFile` with no shell.
- Study when: a team wants shared agent memory and does not want to stand up a service to get it.
- Do not copy when: corrections must survive a background pass — unless the correction can live in `pinned/`, which is the narrow case this design does answer.

### [`opencode`](../systems/opencode/)
- Best idea: a compaction hook that lets a plugin append context as well as replace the prompt — the moment a memory system most needs, and one few hosts expose.
- Biggest risk: no memory contract at all, so plugins couple to the SQLite schema instead of the API, and a migration the host is entitled to make silently breaks them.
- Most reusable component: handing plugins the system prompt as `string[]` rather than a concatenated string, so two plugins compose instead of colliding.
- Maturity impression: a large, well-built coding agent with an extensive plugin surface, whose memory-relevant hooks are both marked experimental.
- Study when: you are building a host and deciding whether seams are enough without a domain contract.
- Do not copy when: you want the host to enforce scope or deletion — there is nothing here to enforce them with.

### [`nooa-memory`](../systems/nooa-memory/)
- Best idea: every access records the score components that produced it — `{rel, rec, imp, spread}`, the rank, the query and the reader — so "why was this retrieved" is a lookup rather than a reconstruction.
- Biggest risk: the access log is a capped ring on the record, so the formative accesses that explain how a memory became established are the first to be lost.
- Most reusable component: keeping rehearsal separate from belief — retrieval bumps a `strength` counter that slows forgetting and leaves `confidence` untouched.
- Maturity impression: 4,200 lines with 23 test modules, ACT-R and Ebbinghaus implemented literally rather than gesturally, inside an NVIDIA labs framework — and an owner-isolation property that is now asserted by a three-node relay case with an unscoped positive control.
- Study when: you need memory whose ranking is explainable after the fact, or you want prospective memory — `intent` and `todo` are types nothing else here has.
- Do not copy when: you need correction — archival is a record flag, and a decayed memory can be re-authored with nothing to consult.

### [`neo4j-agent-memory`](../systems/neo4j-agent-memory/)
- Best idea: reasoning traces recorded via a context manager, so a raised exception becomes the outcome — failure memory proportional to coverage rather than to caller discipline, with an indexable error kind on top.
- Biggest risk: bi-temporality and supersession cover preferences only, and nothing is keyed on a rejected value.
- Most reusable component: the trace context manager plus `ReasoningStepWithContext`, which never returns a step without its parent's outcome.
- Maturity impression: a Neo4j Labs package with MCP, CLI, Strands and OpenAI Agents integrations, a benchmarks tree, and local NER extraction keeping the frequent write path off the token budget.
- Study when: several agents should share one view of the world, and operational history is the thing worth pooling.
- Do not copy when: corrections must survive re-extraction.

### [`elastic-atlas`](../systems/elastic-atlas/)
- Best idea: a committed retrieval eval matched on document id rather than judged by a model, so Recall@k and MRR are arithmetic and reproducible — shipped beside a stress test.
- Biggest risk: a research demo by its own description, with synthetic personas and an ungated single-pass consolidation that writes both facts and playbooks.
- Most reusable component: the eval and stress-test scripts, which are more transferable than the memory layer.
- Maturity impression: a demo that measures itself more than most production systems in this atlas do.
- Study when: you want the clearest small example of the episodic/semantic/procedural split, or an eval design you can actually rerun.
- Do not copy when: you need correction, trust state, or an audit trail — none is present.

### [`nemoclaw`](../systems/nemoclaw/)
- Best idea: a per-agent state contract that says which directories are snapshotted, which are wiped, which are regenerated and which the user owns — written down rather than left to whoever wrote the backup script.
- Biggest risk: memory is snapshotted and restored verbatim, so a restore reinstates deleted memories and nothing above is told.
- Most reusable component: excluding state that is cheaper to regenerate than to restore, with the failure it prevents named — an argument that may apply to derived memory too.
- Maturity impression: infrastructure with guards that validate their own helpers, and issue numbers cited in the comments for the two decisions that would otherwise look arbitrary.
- Study when: you operate agents rather than build memory for them, and want to know what memory looks like from underneath.
- Do not copy when: you want a memory system — it has none, and its product page correctly credits memory to the agents it wraps.

### [`daimon`](../systems/daimon/)
- Best idea: the model's trust label is a claim the code falsifies — a verbatim item's quote is grepped against the transcript and demoted on a miss, and an outcome claim with no tool result cited is demoted even when its quote verifies.
- Biggest risk: the live working set is one checkpoint per project, so anything carry drops is reachable only through a lexical index with no semantic arm, and the committed retrieval numbers are modest.
- Most reusable component: `verify_quotes` and `ground_outcomes` in `serializer.py` — about 200 lines that make an extraction's own provenance mechanically checkable. Its close second is `refutations.CHANNEL_AUTHORITY`, a lookup table that reads authority off the write channel the process observed instead of a `--by` flag the caller sets, with the strongest channels unreachable from the CLI so an agent cannot shell out to one.
- Maturity impression: 24,700 lines of source under 50,800 lines of tests, a research logbook, a scar file per landmine, a benchmark reporting policy stricter than most vendors', and a replay A/B rig with a placebo arm that has been used to refute three of the project's own hypotheses.
- Study when: you want cross-session continuity for a coding agent, or you want to see what taking trust classes seriously actually costs in code.
- Do not copy when: you need memory within a session, semantic retrieval, or a shared service — none of the three is here or planned.

### [`memory-project`](../systems/memory-project/)
- Best idea: forgetting has two speeds and only the slow one destroys — `prune()` archives to a cold tier that a specific enough cue can still reach, `purge()` is a separate deliberate call, and the source says plainly which is which.
- Biggest risk: `purge()` is documented for accidentally-jotted secrets and implemented as a Chroma `col.delete`, so the embedding stays in the index file; and with no tombstone, re-jotting a purged claim re-admits it at full stability.
- Most reusable component: `prune()` and `purge()` together — about forty lines that remove the false choice between growing forever and destroying on "forget".
- Maturity impression: 3,113 lines, 26 commits, AGPL-3.0, 16 regression assertions on the decay maths and nothing testing the hooks. Small and legible, with the tuning constants named and grouped rather than scattered.
- Study when: you want a forgetting curve with a reversible archive tier, or an injection boundary that distinguishes assert from hedge from silence.
- Do not copy when: anything needs a scope boundary — topic is a ranking boost and never a filter, by design — or when a memory has to be markable as wrong.

### [`hippo-memory`](../systems/hippo-memory/)
- Best idea: the scope boundary is enforced in the query on the read path and *deliberately suspended* for consolidation, with the suspension fenced at the transport layer instead — `/v1/sleep` is loopback-only and admin-gated, and the 403 names the reason and the version that introduced it.
- Biggest risk: `stale` sits in a union with `verified`, `observed` and `inferred` but is derived from thirty days of disuse rather than from evidence, so one field mixes how a belief was formed with how recently anyone wanted it.
- Most reusable component: the retention prune in `audit-prune.ts`, which emits its own `audit_prune` row carrying cutoff, count and dryRun so the audit trail explains its own hole.
- Maturity impression: ~50,000 lines (release v1.31.0) with a real-database test convention, a migration ladder past forty steps, and incident comments naming what each repair was for — and a tagline about forgetting the correction model now backs, since v1.31.0 added the digest-keyed rejected-value tombstone that was the report's former central gap.
- Study when: you need multi-tenant memory where different transports carry different trust models, or you want a worked example of ranking that fuses lexical, vector and derived-quantity arms.
- Do not copy when: correction has to survive a *paraphrase* — the new tombstone refuses an exact repeat of a rejected value but not a reworded one — or when you want a small dependency.

### [`7layermem`](../systems/7layermem/)
- Best idea: seven memory types separated at the schema rather than by a type column, each table annotated with the cognitive category it stands for, so "which kind of memory is this" is answered by the table name.
- Biggest risk: the layers are destinations rather than a lifecycle. Nothing promotes, expires or demotes between them, six of the seven have no delete path, and deleting a conversation thread leaves its summary behind.
- Most reusable component: the seven `CREATE TABLE` statements with their annotations — a legible taxonomy that costs nothing at this scale.
- Maturity impression: 7,016 lines, no licence file at this commit, no migrations, and a test suite that re-declares the schema with its own `CREATE TABLE` strings rather than calling the store manager.
- Study when: you want to hold an entire typed-memory design in your head at once, or you are deciding whether to split memory types across tables.
- Do not copy when: you need any correction path, a scope beyond one conversation thread, or a licence.

### [`cognicore`](../systems/cognicore/)
- Best idea: `state TEXT DEFAULT 'candidate'` — a memory arrives unassessed rather than believed, which a confidence float cannot express, plus a utility ledger separating retrieved from used from *ignored*.
- Biggest risk: scope is filtered in Python after the backend returns, so any limit the backend applied was applied to the unscoped set and a scoped read can silently come back short.
- Most reusable component: the four column groups on `memory_entries` — content, epistemic, scope, and provenance-plus-utility — which put `creation_reason` and `source_component` in the schema rather than in a metadata blob.
- Maturity impression: MIT, 79,439 lines, six backends behind one contract, a benchmark programme and a paper directory — beside fourteen loose `test_*.py` provider smoke files and two committed `.db` files at the repository root.
- Study when: you want an epistemic state in the schema rather than in a prompt, or a retrieval feedback signal that records what the agent declined.
- Do not copy when: the scope boundary has to hold under a limit, or you want a dependency rather than an environment.

### [`alma-memory`](../systems/alma-memory/)
- Best idea: an anti-pattern table carrying `why_bad` and `better_alternative` beside the pattern itself — the only place in this corpus where a correction record holds both the reason and the replacement.
- Biggest risk: the anti-pattern write guard has one call site. `learn()` refuses a strategy matching a known anti-pattern; the heuristic extractor, the conversation miner, the consolidation pass and two MCP write paths reach the same store without passing it, and those are the automatic writers a rejection most needs to bind.
- Most reusable component: `VerificationMethod`, which separates checked-against-an-authority from checked-against-our-own-memories from guessed-from-a-number — three claims most systems collapse into one score.
- Maturity impression: 104,360 lines under 42,467 lines of tests, MIT with a LICENSE file, a dual-dialect migration for the new columns, and a committed LongMemEval run whose published recall curve recomputes exactly from its per-question records at every k.
- Study when: you want a memory that learns operating heuristics from task outcomes, or the richest worked example of storing what not to do.
- Do not copy when: you need the write guard to hold against a background pass today — the paths that re-derive memory automatically are the ones it does not cover.

### [`promptx`](../systems/promptx/)
- Best idea: one SQLite database per role, opened from the role's own directory, so isolation cannot be forgotten — crossing it would mean opening a different file rather than omitting a predicate.
- Biggest risk: `strength` is the only epistemic field, so a wrong engram and an unused one decay identically and nothing records that anything was ever judged.
- Most reusable component: the `cue_index` — memories addressed by the words that lead to them rather than by embedding proximity, with `ON DELETE CASCADE` keeping the index from outliving its target.
- Maturity impression: MIT, 63,237 lines, twenty-one cognition modules with a Cucumber suite over them — and `CREATE TABLE IF NOT EXISTS` with no version column across a store that is per-role, so the first schema change is a manual migration everywhere.
- Study when: you want associative recall by cue rather than similarity, or the cleanest example here of scope enforced by file boundary.
- Do not copy when: you need correction of any kind, or your scope is a person rather than a role.

### [`echo-agent`](../systems/echo-agent/)
- Best idea: `provenance_guard` — every memory records which write path created it, ranked `user_stated` 3, `consolidated` 2, `model_inferred` 1, unknown 0, and a write is refused unless the actor ranks at or above its target. A model-inferred claim cannot overwrite a fact the user stated, and the label belongs to the path rather than the payload, so the model cannot nominate its own output as user-stated.
- Biggest risk: the guard governs authority, not truth. Supersession is record-keyed, so a value already adjudicated wrong can be re-asserted by any path with adequate rank — including the user restating a claim they previously corrected.
- Most reusable component: about fifteen lines of `_SOURCE_PRIORITY` and `provenance_guard` in `memory/types.py`, plus the audit call on the *refused* write path that lets you verify the guard is running.
- Maturity impression: 76,594 lines under 360 test files, eighteen memory modules named for the problems this atlas tracks, and a graph layer added at migrations 6 and 8 rather than designed in. Primary documentation and several load-bearing comments are Chinese.
- Study when: you need to answer "whose claim wins" structurally rather than by prompting, or you want contradiction that adjudicates instead of flagging.
- Do not copy when: you want a memory library — this is an agent, with no MCP or HTTP surface for the memory layer — or when correction has to survive re-assertion.

### [`helm`](../systems/helm/)
- Best idea: a first observation is capped at 0.7 confidence and can only rise 0.05 per independent repeat of the same value, so the store cannot record a single sighting as certain — the whole gate is about fifteen lines.
- Biggest risk: the confidence it computes never reaches the model. The per-turn block is `- (kind) key: value` under *"use these, never contradict them"*, which promotes every provisional guess to an assertion at the last step.
- Most reusable component: `workspace/memory/` — four scripts, a JSON-on-stdout CLI, no dependency beyond Node 22's built-in `node:sqlite`, and no coupling to the rest of Helm beyond a path.
- Maturity impression: uneven and legible. A committed 25-issue self-audit with `file:line` and reproduction steps, every issue I checked closed at this commit, and smoke tests that assert ranking and the system's own noise gates — beside a schema that exists as guarded `ALTER`s in five files and three readers that forgot the active-row predicate.
- Study when: you want the cheapest working epistemic model in this atlas, or you are building a single-owner local agent and want more than a JSON blob.
- Do not copy when: the store will pass a few hundred active facts (the recall window is 500 rows ordered by recency), more than one person or project shares it (there is no scope to add), or deletion has to survive re-derivation (`forget` and prune are hard deletes with no record).

### [`csm`](../systems/csm/)
- Best idea: `context_injection_items` — every candidate for the injected block recorded with its position, score, a disposition of `injected | trimmed | omitted` and a reason code, so "why didn't the agent know that?" becomes a query instead of an argument.
- Biggest risk: correction and retrieval have drifted apart. Merge sets `superseded_by`, archive sets `archived_at`, and the search WHERE-clause builder filters on neither — so the governance report calls the store clean while search keeps returning the duplicates.
- Most reusable component: `src/work-ledger-lineage.ts` — about 130 lines of line-hash multiset arithmetic that decide whether an edit the agent made still exists in the file, with no model and no diff library.
- Maturity impression: finished-looking in a way it is not. 55,000 lines across 392 files, 46 tables, 189 test files, a checksummed migration ledger that fails fast on an unknown history, a committed backup/restore drill in the release gate — beside a beliefs layer that admits only a status nothing writes, a review queue whose table has no INSERT, and a self-model reporting 3,849 successes and zero failures because it counts exit codes.
- Study when: you want to see how far deterministic capture scales, or you want the two mechanisms above, which are each a few hundred lines and copy cleanly.
- Do not copy when: more than one person or tenant will share the deployment (there is one scope axis and a cross-project self-model), you cannot run Postgres and a local embedding server, or you need the SQLite mode to do hybrid retrieval — it degrades to substring matching without saying so.

### [`graphify`](../systems/graphify/)
- Best idea: a lesson is `tentative` until a *second distinct result* confirms it, and `preferred` only then — "one save can't mint a trusted lesson", implemented as a counter and a comparison.
- Biggest risk: the dead-end list is enforced by asking the model nicely. The skill says "don't re-derive it next time"; no code path reads it, so the strongest-sounding promise in the design is a Markdown bullet.
- Most reusable component: the staleness check in `reflect.py` — a content-only SHA-256 of the cited node's source file, stored with the lesson and recomputed on every read, biased to over-flag on purpose and with three tests guarding against spurious fires.
- Maturity impression: 3,308 test functions against 15,959 lines of source, byte-stability tests on both derived artifacts, and a committed regression guard that its own lessons file cannot be re-ingested as evidence — a bug two other systems here shipped first.
- Study when: you want the smallest complete work-memory loop in this atlas, or you need a verification mechanism cheap enough to run on every read.
- Do not copy when: you need memory about anything other than "how a query over this project turned out" — there is no user, no preference, no entity, and nothing crosses a project directory.

### [`lorekit`](../systems/lorekit/)
- Best idea: an audit log made immutable by the absence of a policy — a SELECT and an INSERT policy on the table and deliberately no UPDATE or DELETE, so the invariant is enforced by RLS rather than by everyone remembering not to write the statement.
- Biggest risk: that log records `{scope, key}` over an in-place upsert, so it proves a memory changed and cannot show what it replaced — and archiving frees the address, which is the inverse of a tombstone on the operation a user reaches for when a lesson is wrong.
- Most reusable component: `packages/mcp-core/src/scope.ts` plus the `org_scope_bindings` routing — a validated four-level scope key, an authenticated tenancy boundary, and a table that makes "this repo's lessons belong to the team" a row instead of a convention.
- Maturity impression: 37 migrations written like design documents with numbered decisions, 1,184 tests, RLS on every table, hashed and scoped tokens, HMAC-verified webhook ingest with an explicit no-timing-oracle note — beside five entrenchment guards of which one is enforced by code.
- Study when: you need shared agent memory for more than one person and have to answer who changed what, or you want the cleanest separation of a scope key from a tenancy boundary in this atlas.
- Do not copy when: you are one developer (the parts worth paying for are the multi-user parts), or your problem is deciding which lesson to trust — LoreKit is an excellent filing cabinet with an excellent lock and no opinion about the contents.

### [`clio`](../systems/clio/)
- Best idea: a trust tier that costs an entry something in three channels at once — a 0.3x ranking multiplier, an `[UNVERIFIED]` badge in the rendered prompt, and a halved age-out — rather than only filtering.
- Biggest risk: the sybil boundary is `agent:session` and a session restart mints a new session, so one agent running twice supplies both votes. The library also still defaults to `unknown:unknown` when the identity vars are unset — the fix lives in the two shipped entry points, not in `LongTerm.pm`, and a test pins the default as intended.
- Most reusable component: `corroboration_sources` as an array of `agent:session` identities rather than a count — the only place in this atlas where "two independent sources" is checkable rather than assertable.
- Maturity impression: 102,862 lines of pure Perl with no CPAN dependency, atomic writes throughout, a stated memory-poisoning threat model — and, since 31 July 2026, a 412-line regression file on the tier mechanism that had none. I ran it: 92 assertions, none failing.
- Study when: you want the best-shaped answer here to "how do I stop my agent believing something it made up once", and a short lesson in what an unset variable does to it.
- Do not copy when: more than one person shares the store (there is no scope key and every entry is stamped `source_agent: 'unknown'`), or you need memory that survives being wrong — decay, age-out, dedup and prune all delete without a record.

### [`powermem`](../systems/powermem/)
- Best idea: forgetting split into four separate predicates — `should_promote`, `should_forget`, `should_archive` and `reinforce`, each with its own threshold — so archival is a different decision from forgetting rather than the same score crossing a second line.
- Biggest risk: a `history` table with `old_memory`, `new_memory` and `actor_id`, maintained by migrations and written by nothing in the repository. A schema that implies an audit trail will be read as one, including by any capability matrix built from migrations.
- Most reusable component: `_get_decay_rate_for_type` and `_build_db_filters` — a per-type decay rate is a few lines for a large gain in realism, and pushing the scope keys into the backend's own query is the difference between a boundary and a convention.
- Maturity impression: 128 test files across storage backends, FTS, MCP and the CLI installer, a broad integration surface (Python SDK, HTTP server, MCP, CLI, VS Code, Claude Code), and the atlas's most complete forgetting-curve implementation — beside an unwired history table and a rotating file log with `backupCount=5`.
- Study when: you want retention to be a tunable model rather than a TTL, or you want to see decay, reinforcement, promotion and archival separated into decisions you can measure independently.
- Do not copy when: you need read replicas or deterministic reads — search writes to the store by design, and that is not a flag you can disable without losing the retention model — or a memory has to be evidence, since a decay score is not a record that something was wrong.

### [`acontext`](../systems/acontext/)
- Best idea: the write is gated on a terminal outcome — a CHECK constraint on the status vocabulary, an enqueue that fires only on `success` or `failed`, and three committed tests asserting the other cases write nothing. It is the difference between a skill library and a transcript summary.
- Biggest risk: retrieval depends entirely on the agent choosing to look. There is no automatic injection, so recall rests on names, descriptions and willingness — three things that are hard to measure and easy to get quietly wrong.
- Most reusable component: the trigger tests in `core/tests/llm/` — the gate is cheap to copy and the tests are what keep it implemented.
- Maturity impression: 43 test files aimed at the learning machinery rather than the plumbing, an end-to-end pipeline suite, and Markdown skills exportable as a ZIP so the memory outlives the vendor.
- Study when: your agents run repeatable tasks with a status you can trust, and you want the accumulated know-how greppable rather than embedded.
- Do not copy when: your tasks end ambiguously — the gate never fires and you have deployed a queue, a sandbox and a Postgres for nothing — or you need conversational or preference memory, which it has no unit for.

### [`adk-python`](../systems/adk-python/)
- Best idea: scope in the signature rather than in the query. `app_name` and `user_id` are required keyword arguments on every read and write, so a scope bug is a `TypeError` rather than a leak.
- Biggest risk: the contract has no removal method. Every application written against it inherits the gap, and no provider can fix it — only a breaking interface change can.
- Most reusable component: the `BaseMemoryService` signature itself, minus the omissions. It is the interface most agents are written against and the one to diff your own against.
- Maturity impression: 61 memory test functions across three service implementations, a default in-memory service whose docstring says "prototyping purpose only", and an `add_memory` that raises `NotImplementedError` naming the alternatives rather than faking it.
- Study when: you are designing a provider interface and want the scope handling to copy verbatim.
- Do not copy when: deletion is a compliance requirement — at this commit the framework will not help, and the answer will be provider-specific code that outlives your abstraction.

### [`agent-afk`](../systems/agent-afk/)
- Best idea: the verification status is in the string the model reads. A fact arrives either with a citation or tagged `[unverified]`, and a supersession carries the old citation forward with a warning that it may be stale.
- Biggest risk: the gate is behind `AFK_MEMORY_EVIDENCE_GATE=1`, so the default build stores codebase facts with no citation and marks nothing. The best mechanism in the system is off unless you find the flag.
- Most reusable component: about two hundred lines of evidence gate that fits in SQLite, with the category taxonomy that makes it tolerable in daily use.
- Maturity impression: 129 test cases unusually well aimed — a 333-line suite covering all four supersession outcomes across all four categories, plus the UNIQUE-collision duplicate path and the not-found throw.
- Study when: you are building a coding agent and want provenance without a graph.
- Do not copy when: two people share the database — the archive is cross-session with no scope filter, which is right for one developer and wrong immediately after that.

### [`agent-framework`](../systems/agent-framework/)
- Best idea: fail-closed owner scoping checked three ways, with a post-resolve containment assertion — the best filesystem scoping in this atlas — and `session_ids` provenance recorded on every topic.
- Biggest risk: the provider contract declares neither deletion nor scope, so a third-party provider inherits AutoGen's gap, and compression is the only correction path.
- Most reusable component: organising durable memory by topic rather than by time, with the index split from the content.
- Maturity impression: about 1,357 lines of tests on the harness memory alone, aimed at state round-trips, consolidation scheduling, disk-full and misconfigured-client failures, and the scope boundary.
- Study when: you are in the Microsoft stack and want the context-provider seam, or you want a per-user assistant whose correction need is "rewrite the topic".
- Do not copy when: you need to prove a deletion, hold a claim you are unsure about, or answer what the system believed last month — there is no unit below the topic file to attach any of that to.

### [`agent-memory-supabase`](../systems/agent-memory-supabase/)
- Best idea: validity time and record time in the same row, with an `updated_at` trigger that refuses to fire on access-stat touches so a read cannot masquerade as an edit.
- Biggest risk: the per-user RLS policies are commented out, so the only enforced posture is server-sees-everything — and there are no tests at all to notice.
- Most reusable component: the similarity floor on the text lane, with the RRF failure it prevents written into the comment beside it.
- Maturity impression: 898 lines, better reasoned per line than most frameworks here and readable in an hour — with no test directory, no fixtures and no harness, despite `use_blended` and `track_access` existing to make evaluation clean.
- Study when: you are on Supabase, want to own the SQL, and your memory is one project or one user.
- Do not copy when: you are multi-tenant before uncommenting and testing Posture B, or you need to prove a deletion — soft delete plus supersession leaves the content in the table with no record that a value was rejected.

### [`agno`](../systems/agno/)
- Best idea: supersession that is *judged* rather than inferred from a key collision — thresholded, reversible, and tested, with the superseded row kept and what replaced it named.
- Biggest risk: `optimize_memories` defaults to `apply=True` and replaces every memory with one model-written paragraph. Decide who can reach `POST /memory/optimize` before someone finds the button.
- Most reusable component: the framework stamping time rather than the model, and the split between guidance and data with a test on the split.
- Maturity impression: 304 test functions across 17 files plus integration suites for the manager, agent memory, team storage and OS routes — and comments that document the corruptions that produced the code.
- Study when: your memory needs are typed and modest, correction is supersession, and you want an agent platform where the learning stores come as a good default.
- Do not copy when: you need retrieval quality — there is no ranking to tune and relevance costs an LLM call per search — or deletion has to be provable, since there is no audit and no tombstone.

### [`aukora-kernel`](../systems/aukora-kernel/)
- Best idea: the receipt is appended and fsynced *before* the row, and the chain hashes the content hash rather than the plaintext — so right-to-be-forgotten erases the plaintext without breaking the proof.
- Biggest risk: forget records a rejection it never consults, so the same content can be written again; and the declared tiers are never applied on the read path.
- Most reusable component: the write path alone — the authority gate, receipt-first ordering, chained hashes over content hashes, and RTBF-by-erasure — which transplants without the rest.
- Maturity impression: the best negative-assertion suite in the atlas after Verel's, testing authority rather than recall; and a project that says PROVEN-LAB in four places rather than letting you discover it.
- Study when: the provenance of a write matters more than recall quality — regulated work, audit-facing tooling, anywhere "prove this memory was authorized and unaltered" is a real question.
- Do not copy when: you need to find the relevant thing among fifty thousand. Chain-ordered retrieval and a whole-file rewrite per write put a low ceiling on corpus size, and the authors say so.

### [`autogen`](../systems/autogen/)
- Best idea: `update_context` as a first-class injection seam, in a protocol small enough to implement in an afternoon.
- Biggest risk: `MemoryContent` has no identifier, so targeted deletion is not expressible and `clear()` is the only removal verb. Scope is an adapter's option rather than the contract's.
- Most reusable component: the `update_context` seam itself, worth designing around even where the rest is not.
- Maturity impression: 56 memory test functions across the core and the ext adapters, proportionate for an interface package — with a default implementation that injects the entire store.
- Study when: you want the clearest demonstration in the atlas that an interface's omissions are permanent in a way an implementation's are not.
- Do not copy when: you are designing a provider interface. A better adapter cannot add an id to `MemoryContent`, and every agent written against the protocol inherits the ceiling.

### [`buzz`](../systems/buzz/)
- Best idea: the relay can neither read content nor correlate slugs, and a memory value is updated by compare-and-swap — with a careful distinction maintained between confirmed-absent and unknown.
- Biggest risk: there is no retrieval. The design works while an agent can hold its own namespace in mind, and there is no growth path that does not mean designing retrieval from scratch over ciphertext the relay cannot read.
- Most reusable component: the confirmed-absent-versus-unknown distinction, which most systems here collapse into an empty result.
- Maturity impression: 34 tests in `engram.rs` alone and they are the right ones — round-trip encryption, oversized bodies refused at build time, head selection with an event-id tiebreak, and eighteen cases pinning reference extraction.
- Study when: you want a small, legible, model-free memory layer with an unusually careful concurrency story and a spec you can reimplement.
- Do not copy when: memory has to scale, or you need to explain a memory's history or prove a correction stuck — the substrate threw the evidence away.

### [`camel`](../systems/camel/)
- Best idea: a three-part contract — block, memory, context creator — small enough that a custom store satisfies it in an afternoon, with the system message pinned through truncation.
- Biggest risk: the retrieval query is whatever the last user message happened to say, and `LongtermAgentMemory` cannot delete a single record from its vector store.
- Most reusable component: the `AgentMemory` ABC as a seam — swapping one of this atlas's fact-level systems in behind it is a day's work.
- Maturity impression: 868 lines across four test files covering round-tripping, windowing and the `NotImplementedError` paths, with no negative retrieval assertion — which follows from having no scope filter to assert about.
- Study when: you are already using CAMEL and your agents are short-lived, single-tenant, and their memory is genuinely their transcript.
- Do not copy when: you are multi-tenant without adding a filter yourself, or a user can ask you to delete something.

### [`cortex`](../systems/cortex/)
- Best idea: the gate is on the **read**, not the write. A secret-classified hit needs a supervisor decision and then a human yes, and a denial returns an error rather than a quietly redacted result.
- Biggest risk: a complete `MemoryPrivacyPolicy` — allowed tiers, PII redaction, retention — lives in a process-local `Map` and is consulted by nothing.
- Most reusable component: the injectable approval gate that fails closed on refusal, plus classifying with regexes before reaching for a model.
- Maturity impression: a scheduled weekly benchmark that is real, sampled and expiring, beside a governance module with no callers and a tier filter that silently substitutes.
- Study when: your agents handle material with real disclosure consequences and you want a person or a supervisor in the loop at retrieval time.
- Do not copy when: you need to correct memory. There is no supersession, no tombstone and no trust state — the system can stop you seeing a memory and cannot record that one was wrong.

### [`cosmonapse`](../systems/cosmonapse/)
- Best idea: a memory contract with a **failure vocabulary** — refusal, overload, deadlines, rollback. It is the only interface here that lets a backend decline, and the error taxonomy is worth copying wholesale into a system with better content semantics.
- Biggest risk: the saga journal is an in-process dict, so a worker that dies mid-workflow leaves provisional writes permanent and unmarked.
- Most reusable component: journalling the inverse when a write belongs to a workflow, and putting a deadline on recall.
- Maturity impression: SDKs and tests on both the Python and TypeScript sides, no memory benchmark and no retrieval measurement — which follows from a contract that does not define retrieval quality.
- Study when: you are building multi-agent systems where storage is one participant among many and the hard problems are saturation, deadlines and partial failure.
- Do not copy when: you want a memory model. It has no opinion about what a memory is, so every question this atlas asks is answered by whatever you bind underneath it.

### [`crewai`](../systems/crewai/)
- Best idea: scope as a hierarchical path with subscope views, proved by a committed test that a rooted view cannot recall a sibling's records — and recall that reports what it looked for and did not find.
- Biggest risk: an LLM on the write path is authorised to delete existing records, with no tombstone, no audit and no human in the loop.
- Most reusable component: the rooted-view boundary test, and `match_reasons` on a result so a rank can say why it happened.
- Maturity impression: 147 test functions across seven files, 63 of them in `test_memory_root_scope.py` alone, driving scoping through recall, listing, nesting and path normalisation.
- Study when: your problem is organisational — several agents, several teams, one store, and a need for one agent's memories not to reach another's prompt.
- Do not copy when: a wrong deletion is expensive. If you adopt it there, the first thing to build is a wrapper that logs `ConsolidationPlan` actions before they execute.

### [`ecc`](../systems/ecc/)
- Best idea: the schema says out loud that its memory is never authoritative — `trust` is an enum of exactly one value, `unreviewed`, because verified knowledge is promoted into a governed artifact elsewhere rather than upgraded in place.
- Biggest risk: the read path filters a status the write path cannot produce, so `rejected` and `superseded` are reachable only by hand-editing frontmatter.
- Most reusable component: `sourceHarness` and `targetHarnesses` on every record, with scope enforced by path containment and every enum validated at load.
- Maturity impression: four memory-specific test files inside a large repository-wide suite, the notable one asserting the shape of the unified memory surface.
- Study when: you move between several agent harnesses and want one Markdown vault of deliberate notes all of them can read.
- Do not copy when: you expect extraction, consolidation or correction. Treat it as a shared notebook with a schema, and expect to open a text editor when something in it turns out to be wrong.

### [`everos`](../systems/everos/)
- Best idea: one compile path for every read, with the four scope keys in its base — so there is a single place isolation can be got wrong, and an end-to-end test with a positive control that says it is not.
- Biggest risk: supersession is excluded from reads but recorded on the row rather than the value, and the source Markdown stays watched — so a deprecated fact is re-derivable.
- Most reusable component: Markdown canonical with rebuildable indexes, plus the Cases/Skills split bridged at query time.
- Maturity impression: roughly 1,988 test functions, serious for a project this young, with the e2e layer testing owner isolation and the case-to-skill bridge rather than only the unit surface.
- Study when: you want a local-first store you can open in an editor, with a scope model good enough to build a multi-user product on.
- Do not copy when: your correction requirement is strong — making "forget this" durable means reaching into the Markdown tree, and the memory layer will not do it for you.

### [`gitlord`](../systems/gitlord/)
- Best idea: git *is* the memory. Turns are commits, sessions are branches, commit shas are addresses, and forking a conversation is a first-class operation because the substrate already supports it.
- Biggest risk: it stores what was said rather than what is believed, so a correction and the mistake sit in the log in order with nothing preferring either.
- Most reusable component: log-as-authority with the index as a projection you can rebuild, and per-branch context-cache invalidation.
- Maturity impression: 233 test functions, no memory benchmark and no retrieval measurement — consistent with a system whose claim is durability rather than recall.
- Study when: auditability and replay are the requirement — runs you must reconstruct exactly, experiments you want to fork.
- Do not copy when: belief is the requirement, or you assume git gives you deletion. Pair it with something that has an opinion about what is true, and keep the evidence here.

### [`gobii`](../systems/gobii/)
- Best idea: an explicit persistence contract — eight built-in tables declared ephemeral and dropped before save, with each one's mortality stated in the prompt the model reads, so the agent knows what survives.
- Biggest risk: the schema is model-authored, so nobody can write a query to correct or erase a subject without first discovering what tables the agent invented.
- Most reusable component: `sqlite3.set_authorizer` as a real sandbox if you let a model write SQL, and mounting the platform's own state as tables the agent can join against.
- Maturity impression: 381 test functions across the SQLite suites alone, covering the schema prompt, digest, recovery, batch behaviour and cross-process coordination, plus an eval framework in the platform proper.
- Study when: your agent's memory is genuinely tabular — scraped listings, tracked prices, pipelines — where the useful question is an aggregate and SQL beats every retrieval mechanism here.
- Do not copy when: memory is a set of beliefs about a person that may turn out to be wrong. There is nowhere to record a rejection and no operator-level way to find a value an agent filed under a name only it chose.

### [`goodai-ltm`](../systems/goodai-ltm/)
- Best idea: targeted update and delete on the interface itself. It is the cleanest demonstration in the atlas that a memory abstraction's first job is to give memories addresses, and the relevant part is two pages long.
- Biggest risk: no commit since 28 February 2024, no scope key of any kind, and persistence by whole-state serialisation.
- Most reusable component: `BaseTextMemory` as a diff target — set it beside ADK's `BaseMemoryService` and AutoGen's `Memory` and the missing methods are obvious in about ninety seconds.
- Maturity impression: unit tests under `goodai/ltm/mem/tests/` with no negative retrieval assertion, and the interesting evaluation story living in a separate benchmark repository.
- Study when: you are designing a provider contract and want to see what the frameworks dropped.
- Do not copy when: you intend to run it. Choose something maintained — and then check whether its interface can say "delete that one", because the odds are it cannot.

### [`juggler`](../systems/juggler/)
- Best idea: separating the file the user writes from the file the assistant writes, with a canonical line format the writer re-tidies on every save — so the two never fight over formatting.
- Biggest risk: `forget` matches by substring, so one careless match string removes more than it names and nothing records what it removed.
- Most reusable component: a per-fact delete control in the UI, and showing every write in the transcript so the user sees the memory change as it happens.
- Maturity impression: 43 test cases against 772 lines, with separate suites for the item, the format, the seed and the **system prompt** — testing the text the model is told about a tool is rare here and exactly right for this design.
- Study when: you are building a single-developer coding assistant where memory is a handful of project conventions and the user is present to correct it.
- Do not copy when: memory must hold something you will need to prove you deleted, or something a second person should see — the store is gitignored and per-machine by design.

### [`lethe`](../systems/lethe/)
- Best idea: purge reaches the lexical and vector substrates *by construction* — the FTS5 index is deliberately not contentless so `DELETE` reaches it — and the deletion is signed, an Ed25519 receipt over a Merkle root of the event log that a third party can verify.
- Biggest risk: a purged text can be inscribed again. The receipt records its hash for verification and no write path consults it.
- Most reusable component: retiring the id rather than only the row, and logging `before` and `after` on every mutation.
- Maturity impression: `tests/test_depth.py` plus ForgetEval — a released benchmark whose author's own system places third of three, reported with confidence intervals and an explicit refusal to declare a winner.
- Study when: deletion has to be provable — a right-to-erasure flow, a regulated store, anywhere "we removed it" must survive a challenge.
- Do not copy when: you need multi-tenancy, belief or scale. There is no scope key at all, no trust state, and the store is one SQLite file with an application-synced vector index.

### [`livingfeed`](../systems/livingfeed/)
- Best idea: storing the *components* of a composite importance score rather than only the total, so the coefficients can be tuned offline by replay instead of guessed.
- Biggest risk: a recall failure is caught and returned as an empty list, so an actor with an unreachable index is simply amnesiac and nothing upstream is told.
- Most reusable component: confining forgetting to the derived layer while keeping the source, with expiry expressed as a query predicate.
- Maturity impression: 429 test functions across 40 files, and a deterministic embedder in dev and CI that makes real similarity assertions possible rather than mocked ones.
- Study when: you are building a simulation or a companion where memory should fade rather than be corrected — it is the most carefully reasoned member of the Generative Agents lineage here.
- Do not copy when: you need factual memory. There is no correction path, no trust state and no deletion by identity — and the design rationale is in Korean-language comments, so the reasons are only partly accessible to a non-Korean-reading team.

### [`logseq`](../systems/logseq/)
- Best idea: the user defines the schema and the agent must write inside it. Properties carry a declared type and cardinality, tags are classes that extend other tags, and `listTags`/`listProperties` let a model discover the ontology before writing in it. Everywhere else the memory model is the vendor's; here it is the user's.
- Biggest risk: agent writes land live and **unmarked** — the schema defines a `created-by-ref` property the MCP write path never sets — so the store cannot answer "what did the agent change?", and the agent has no delete verb to correct itself.
- Most reusable component: the retrieval gating — exact title, FTS5 over a trigram tokenizer, a `LIKE` arm for two-character queries, fuzzy, and a local vector arm fused by reciprocal rank, with the expensive arms skipped when the cheap ones already filled the limit.
- Maturity impression: 245 test files aimed at what a knowledge base gets wrong — schema migration, malli validation of the property system, outliner tree operations, and substantial `db-sync` coverage.
- Study when: you already keep your knowledge in Logseq and want an agent to work in it, or you want the best editing surface in the atlas.
- Do not copy when: this is the agent's *own* memory. No scope key, no trust state, no authorship, no delete — and the AGPL makes embedding it in a proprietary product a licensing decision rather than a dependency choice.

### [`mem0sharp`](../systems/mem0sharp/)
- Best idea: an `event, old_memory, new_memory` row written on every mutation, in an append-only `_history` table with no `UPDATE` and no targeted `DELETE` against it — the audit most systems here document and do not build.
- Biggest risk: a `MemoryBehavior` enum — `Normal`, `Dreaming`, `RandomThoughts`, `PersonalMemory` — swaps the extraction and conflict-resolution prompts, and `Dreaming` asks the model for imaginative associations *phrased as possibilities rather than facts*. The behaviour reaches the extractor, the resolver and the telemetry span, and is written to neither the memory nor its metadata, so a speculative association is a row of exactly the same shape as a stated fact.
- Most reusable component: the owner column as `NOT NULL` rather than a convention, and delete-by-scope beside delete-by-id.
- Maturity impression: 2,982 lines of source against 1,123 of tests across nine classes, with Testcontainers integration suites for Postgres and Qdrant — including `PostgresHistoryIntegrationTests`, which creates a legacy history table, migrates it, and asserts the add-update-delete sequence survives. Very few audit logs in this atlas are tested at all.
- Study when: you are building .NET agents and want Mem0's shape natively rather than through a REST client.
- Do not copy when: you expect epistemics the original also lacks. It stores LLM-extracted text as fact and offers no way to mark a memory doubtful; the history table is a forensic tool, not a trust model.

### [`memary`](../systems/memary/)
- Best idea: separating "what I know" from "what I am attending to", with a salience model small enough to read in one sitting — the smallest legible instance of reinforcement-by-frequency in the atlas.
- Biggest risk: `_select_top_entities` sorts ascending, so the *least*-mentioned entities are the ones injected. The ranking signal has no test on its consumer.
- Most reusable component: the idea, not the code — capture without a model, and a two-store split you can reimplement in an afternoon.
- Maturity impression: the shipped package has no tests; the real ones live in a development sandbox and cover the serialization layer. Last commit October 2024, with Python pinned at ≤ 3.11.9.
- Study when: you are learning how a graph-backed agent memory fits together and want a clear, honest demonstration.
- Do not copy when: you need to answer for what the system believes. A wrong triplet cannot be removed, a wrong entity name cannot be merged, and the only quality signal counts mentions rather than accuracy.

### [`memmachine`](../systems/memmachine/)
- Best idea: provenance that actually resolves — the source is kept and cited, so a support engineer has something to look at when a user says the assistant believes something false.
- Biggest risk: deletion is acknowledged before it happens, and a duplicated method silently drops error handling on the delete path.
- Most reusable component: a one-way ingestion watermark, a constrained extractor vocabulary with a test on the constraint, and reserved metadata keys rejected by prefix.
- Maturity impression: 1,978 test functions across 112 files mirroring the source tree — among the most thoroughly tested repositories here — with migrations, four vector backends and incident-shaped HNSW tests.
- Study when: your obligation is to *explain* a memory rather than merely produce one. This is the strongest starting point in the atlas for that.
- Do not copy when: you want a library — the smallest useful deployment is a server, a database and a model provider — or your correctness bar includes "a deleted thing is provably gone".

### [`memobase`](../systems/memobase/)
- Best idea: scope made structural. Every primary key is `(id, project_id)` and every foreign key is composite, so a cross-tenant query is a schema error rather than a review failure — the best scoping in this atlas.
- Biggest risk: the source transcript is deleted after extraction, so the evidence behind a profile line is gone and correction is a rewrite of the only copy.
- Most reusable component: the composite-key discipline, which costs a migration and removes an entire class of bug.
- Maturity impression: server tests plus client suites in Python, TypeScript and Go — real coverage, but shallow on the parts that matter, exercising API shape and filter correctness rather than extraction quality.
- Study when: you are building a personalized consumer application that wants a stable user description injected every turn at a predictable token cost, with one service and one database.
- Do not copy when: the memory must be accountable. "Why do you believe that?", "where did that come from?" and "forget that permanently" have nowhere to stand — and that follows from the decision to keep the profile small, not from an oversight.

### [`memori`](../systems/memori/)
- Best idea: provenance as a real join table, so a fact resolves back to the conversations that produced it — and a capture path that survives extraction failure, because the durable write is required and the smart write optional.
- Biggest risk: the dedupe key strips all non-ASCII, so facts in Chinese, Japanese, Korean, Arabic, Hebrew, Russian, Greek or Thai collide into one row.
- Most reusable component: the required-durable/optional-smart write split, and giving the agent its own memory subject rather than filing everything under the user.
- Maturity impression: 153 test files plus per-driver modules and a TypeScript suite — the largest suite of any system in its review round — with legible migrations and a Rust core behind three SDKs.
- Study when: you want a portable, auditable schema across an unusual range of databases and are happy to depend on a vendor for extraction.
- Do not copy when: your users write in non-Latin scripts. That is a statement about one function rather than the design — the fix is a few lines — but verify it against your own data before storing anything you would miss.

### [`minecontext`](../systems/minecontext/)
- Best idea: event time is separate from record time and **allowed to be in the future**, which is what makes prospective memory — a commitment you have not kept yet — expressible at all.
- Biggest risk: commitments are inferred from screen capture and nothing reviews them. There are no tests in the Python package, no scope key and no tenancy model.
- Most reusable component: keeping the raw properties as a list under the merged context, and checking historical completion before generating a new commitment.
- Maturity impression: **no tests at all** — the only files matching "test" are unrelated frontend TypeScript — no eval harness, no benchmark directory and no committed results.
- Study when: you want a passive, local, single-machine assistant that builds context from your own work, with the best ergonomics of the passive-capture systems here.
- Do not copy when: you are building a component, or you are not willing to be told what you promised by a system with no test suite and no way to correct it.

### [`mirix`](../systems/mirix/)
- Best idea: the scope key is in the *cache* query as well as the database query, and the boundary is tested by asserting exclusion rather than inclusion — a memory written under one scope, searched under another, asserted absent.
- Biggest risk: `auto_dream` loads up to 500 items per type and lets an agent merge and rewrite them, with hard delete available — so a correction can be undone by an unsupervised pass.
- Most reusable component: a raw-context table kept beside the typed ones, and read scope separated from write scope on the client.
- Maturity impression: 33 test files with the emphasis on boundaries rather than recall — agent isolation, multi-scope access, scoped blocks, filter tags — above the atlas median for a tenancy-first design.
- Study when: you are building a hosted, multi-tenant assistant on Postgres and Redis and want the tenancy model right from the start.
- Do not copy when: memory must be repairable. No trust state, no tombstone, hard delete on the correction path, and a whole-store rewriting pass — a user's "no, that's wrong" does not outlive it.

### [`mnemopi`](../systems/mnemopi/)
- Best idea: per-type forgetting curves — the most carefully modelled forgetting in the atlas — with a dry run on every destructive pass and deterministic fallbacks when no LLM is configured.
- Biggest risk: a provenance scale on which "unknown" outranks "known", an exponential decay curve applied to a commitment, and fifty tuning constants with no evaluation behind them.
- Most reusable component: making a temporal lane first-class rather than folding recency into one score.
- Maturity impression: 420 test cases across 71 files with unusually diagnostic names — `consolidate-fact-concurrency`, `recall-precision-regressions`, and an issue-numbered reproduction file. A suite that names its concurrency hazard is a suite someone has been bitten by.
- Study when: you want the best forgetting model here and can live without correction — a long-running personal assistant where the real failure is an old note crowding out a stable preference.
- Do not copy when: memory must be correctable or provable. There is no supersession at the facade, no rejection, no audit, and the trust model grades where a memory came from rather than whether it holds.

### [`neko`](../systems/neko/)
- Best idea: a *dispute* signal structurally separate from reinforcement, with a hard filter that drops disputed entries **before** the LLM rerank — the docstring giving the reason: stage two would either reinforce the dispute or, worse, cancel it.
- Biggest risk: status is derived from a score rather than stored, so no transitions are kept; and ban-topic directives expire after three days, which is a TTL on a suppression the user asked for.
- Most reusable component: the durable do-not-mention list keyed on the term, and stating the false-positive policy in the code where the suppression lives.
- Maturity impression: about 7,936 test functions repository-wide — the largest suite in this atlas — with a memory recall test that walks the pipeline phase by phase and several policy-contract files.
- Study when: a memory mistake will be *felt* rather than merely wrong — a companion, a therapy-adjacent tool, a long-running personal assistant.
- Do not copy when: you want a library. Memory is wired into a companion runtime with voice, vision and an avatar, and there is no API boundary to lift it out through. Take the designs, not the code.

### [`npcpy`](../systems/npcpy/)
- Best idea: approval is a state the *retriever* respects rather than a workflow step — an unreviewed extraction cannot reach a prompt, because the retrieval path reads approved memories only.
- Biggest risk: a rejection is a status on a row. Re-extracting the same content produces a fresh candidate with nothing consulting the earlier no.
- Most reusable component: offering **edit** and **defer** alongside approve and reject, and keeping the pre-edit text.
- Maturity impression: one memory-processor test file, no benchmark, and nothing asserting that an unapproved memory stays out of `build_context` — the single behavioural claim the whole design rests on.
- Study when: your memory is small, your user is present, and wrong facts are expensive — ten approved memories beating a thousand extracted ones.
- Do not copy when: memory must accumulate unattended, or the same facts recur often enough that answering the same question repeatedly becomes the product.

### [`openhuman`](../systems/openhuman/)
- Best idea: memories are labelled by **what they may cause**, not only by how sure the system is. A taint lattice governs consequence, and sanitization deliberately cannot launder provenance — a redacted memory keeps its taint.
- Biggest risk: taint is binary, assigned once and never re-evaluated; much of the core is re-exported from a separate crate that cannot be read here; and nothing records a rejected value.
- Most reusable component: failing closed on unknown enum values from the database, and two-tier extraction with a free first tier.
- Maturity impression: about 12,548 test functions repository-wide and 1,278 inside the memory modules — the most heavily tested system in this atlas by count, pinning the fail-closed taint parser and wire-format round-trips rather than padding.
- Study when: you are building a desktop agent that ingests a user's real data and therefore has a genuine injection problem rather than a theoretical one.
- Do not copy when: your requirement is corrective memory, or you want a library — twelve modules, an unreadable companion crate, a Tauri shell and GPL-3.0 make this a codebase you join rather than a dependency you add.

### [`pydantic-ai-harness`](../systems/pydantic-ai-harness/)
- Best idea: an idempotency id derived from the run and the tool call, so a retried write is a replay rather than a second append — one of three answers to concurrent writes in the whole corpus.
- Biggest risk: the delete is content-free by design, and the only table recording mutations has its payload cleared — so the audit cannot answer what was removed.
- Most reusable component: budgeting the injection and degrading to a pointer, and returning `scanned` and `truncated` from search so a caller knows the answer was partial.
- Maturity impression: 2,498 lines of tests against 2,452 of implementation — the highest ratio in this atlas at this size — and the content is better than the ratio, because the suite asserts what must **not** happen.
- Study when: you are on Pydantic AI, your memory is notebook-shaped, and multi-tenant safety matters more than recall quality.
- Do not copy when: memory must hold *claims* you will later mark uncertain, correct with provenance, or prove you deleted. There is no unit below the file to attach that to.

### [`reme`](../systems/reme/)
- Best idea: correction gets a validated verb set — `CREATE | CORROBORATE | REFINE | CORRECT` — with contradictions written *into* the memory pointing at their cause, rather than resolved silently.
- Biggest risk: the vocabulary is enforced as a returned label, not as a constraint on the edit, so a validated verb can accompany an unvalidated action.
- Most reusable component: publishing the category you are worst at. ReMe commits per-category LongMemEval and BEAM tables including its own lowest score, which almost nothing else here does.
- Maturity impression: integration suites running the pipelines end to end against a workspace fixture, and committed results rather than a harness with no numbers.
- Study when: you want a personal knowledge base an agent maintains and a person can open in an editor, and you want to see what an honest benchmark report looks like.
- Do not copy when: you need a multi-user service — the scope key, the read-path filter and the per-tenant index are all yours to add — or you are unwilling to have your correctness rules live in prompts.

### [`risuai`](../systems/risuai/)
- Best idea: every derived summary carries the ids of the messages it came from, so deleting a source drops the summaries built on it — the cheapest correct answer to a problem most summarizers never notice.
- Biggest risk: three generations of summarizer ship side by side behind a flag and none of them has a test.
- Most reusable component: reserving retrieval budget in *bands* rather than ranking one list, including a band for a random draw so the unreachable middle stays reachable.
- Maturity impression: roughly thirty test files covering the parser, the scripting language, storage, paging and the source map — a team that writes tests, aimed everywhere except the summarizers.
- Study when: you are building for one person's long-running conversations on their own machine, or you want to watch a data model grow a field per problem across three generations.
- Do not copy when: you need multiple principals, an audit trail, or a memory an agent can query. There is no scope key, no history and no API.

### [`second-me`](../systems/second-me/)
- Best idea: L1 is a *numbered generation* over retained L0, so the derived layer is rebuildable and two generations can be compared instead of the latest being trusted.
- Biggest risk: forgetting stops at the vector store. The trained model keeps what a deleted document taught it, and the deletion cascade that would catch the rest has no test.
- Most reusable component: versioning the derived layer, and deleting the embeddings in a numbered sequence rather than hoping a cascade covers them.
- Maturity impression: no tests over its own pipeline, no scope model, no correction path at L2, and a September 2025 commit at the analyzed revision.
- Study when: you want to experiment with parametric personal memory and have a machine that can train — as a demonstration that the whole pipeline runs on a laptop it is convincing.
- Do not copy when: you cannot tell your users that deleting a memory removes it from search and not from the model. If that sentence is unacceptable for your product, the architecture is wrong for you.

### [`sillytavern`](../systems/sillytavern/)
- Best idea: the activation vocabulary — sticky, cooldown, delay, negative keys, bounded recursion — which are answers to problems extraction-based systems also have and mostly express as tuning constants, if at all.
- Biggest risk: an intricate activation pipeline with no activation tests. Nothing asserts that a given chat and lorebook produce a given activation set.
- Most reusable component: the interchange format, which lets a curated memory outlive the tool that authored it.
- Maturity impression: a mature, long-lived client with a real editing surface — and the one subsystem this atlas came for is the one without a fixture.
- Study when: your memory is small, curated, and matters more than it scales — a character, a world, a domain glossary, a set of standing instructions.
- Do not copy when: memory must *learn*. Its own users demonstrate the gap: the summarize extension exists because a hand-authored lorebook cannot remember what happened.

### [`simplemem`](../systems/simplemem/)
- Best idea: coreference resolved and time absolutised **at write**, so a stored unit reads "Alice discussed the marketing strategy with Bob at Starbucks on November 15, 2025" rather than "she told him about it there". Almost everything else here stores the second kind and hopes retrieval supplies the context.
- Biggest risk: six headline benchmark figures with no committed result artifact for any of them — and the pillar the papers are about cannot delete, scope or correct a single memory.
- Most reusable component: the restatement transform, which is a prompt and a schema and will improve any retrieval you already have; plus one `_log_event` helper called at every mutation site.
- Maturity impression: 311 test functions across roughly twenty files for 114,000 lines and three products, with the governed pillar (EvolveMem) also the newest, least documented and least tested.
- Study when: you want one very good write-time idea to take into your own extractor.
- Do not copy when: you would deploy the text pillar behind a user-facing agent. The first support request you cannot answer is "remove what it learned about me".

### [`skales`](../systems/skales/)
- Best idea: zero-LLM capture and retrieval that are both cheap and legible — regex capture on a 90-minute watermarked scan, retrieval scored `0.70 / 0.20 / 0.10` under a stated sub-100ms budget, with provenance on every extracted row.
- Biggest risk: the documented deletion path for a fact is a chat phrase nothing implements — and that phrase is bound to *capture* and *retrieval* instead, so asking it to forget can store a new memory.
- Most reusable component: stating the retrieval budget in the file header, and invalidating the read cache inside the delete action rather than beside it.
- Maturity impression: no tests of any kind, for a regex pipeline that is a pure function over strings — the cheapest gap in the atlas to close.
- Study when: you want a local assistant that quietly remembers preferences without shipping conversations to a vendor.
- Do not copy when: you need a system of record, or you intend to reuse the implementation — the **BSL 1.1** licence makes this source-available rather than open source.

### [`soul-of-waifu`](../systems/soul-of-waifu/)
- Best idea: a length floor on any LLM-generated overwrite, so a short or empty rewrite is rejected rather than stored — the clearest small example here of how to make a full-rewrite memory safe.
- Biggest risk: the backup, restore and inspection API has no caller anywhere in the application, and only one of the two files written by the same call is backed up.
- Most reusable component: having the model fill a schema and letting your code render the document, plus giving append-only and rewritable memory different files.
- Maturity impression: no test suite exists — no `tests/` directory, no `test_*.py`, nothing.
- Study when: you want to see the guards that make a rewrite-the-whole-document memory survivable.
- Do not copy when: users will ask "what did I tell you about X". There is no retrieval over history, no provenance and no deletion, and the index forgets by omission.

### [`tigrimosr`](../systems/tigrimosr/)
- Best idea: the skill synthesizer stages a proposed skill as `SKILL.md.proposed` beside the live file, keeps the rationale and the sessions it came from, waits for a person, and promotes by rename — forcing review when the target was authored by a human rather than by the automation.
- Biggest risk: approval is durable and rejection is ephemeral, with review state held in process memory — so a user who says "no, don't remember that" is answered and then forgotten.
- Most reusable component: propose-stage-approve by rename, which is worth copying into systems whose memory model is far richer than this one's.
- Maturity impression: 62 inline Rust tests concentrated on the agent loop and tool config rather than memory, with nothing exercising the propose/approve/reject cycle, and nothing at all on the new CLI or its path resolvers.
- Study when: you want a self-contained agent platform that asks before changing what it has learned, or you want the promotion mechanism on its own.
- Do not copy when: memory must be correctable. It is one blob per project plus a skill library, thin by design, and read-modify-write over whole JSON files is the persistence model.

### [`tokenmizer`](../systems/tokenmizer/)
- Best idea: a status for *unresolved ambiguity* that keeps both candidate decisions visible instead of guessing between them — the atlas's only state that means "I do not know which of these is in force".
- Biggest risk: the redaction functions are unit-tested in isolation and nothing asserts a secret fails to reach the rendered context block.
- Most reusable component: the status model and its transition table, worth copying even if you never run the tool; and storing the *argument* for a correction rather than only the fact of it.
- Maturity impression: 440 cases in 38 files with the most informative names in the corpus — `memory_accuracy/test_retention`, `chaos/test_recovery`, `test_contested_decisions`, `test_decay_idempotence` — and a committed ground-truth measurement of extraction recall.
- Study when: your memory is a coding session and your hardest problem is knowing which of two plausible decisions still holds.
- Do not copy when: you need multi-tenant or long-horizon personal memory. Scope is a cache key, every clock is a record clock, and the graph is built around one project's session history.

### [`virtualwife`](../systems/virtualwife/)
- Best idea: the storage contract. `BaseStorage` puts `owner` on every method including a scoped clear, and is a good small answer to "what must a memory backend do".
- Biggest risk: `normalize_scores` sums three quantities on different scales without normalising any of them, so the Generative Agents retrieval function does not do what its name says.
- Most reusable component: the contract, with the implementations discarded — and decay by wall-clock hours rather than by turns.
- Maturity impression: one test file, covering a livestream API. **Nothing tests memory**, and the tests that would have caught what this report found are unusually direct.
- Study when: you want a minimal backend contract to copy, or a worked example of a scoring bug that a single assertion would have caught.
- Do not copy when: you want the system. It is dormant, needs Milvus for the interesting half, disables that half by default, and is a last-N-messages window without it.

### [`z-waif`](../systems/z-waif/)
- Best idea: capping how much the character's own output contributes to its own retrieval query — a feedback loop most companion systems have and none of the others here noticed.
- Biggest risk: a three-message window score is computed and never used, an initial best-score of zero sits over a scorer that returns negatives, and the retrieval cannot return nothing.
- Most reusable component: the scoring function — forty lines containing three of BM25's five ideas plus two the literature does not emphasise, rewritable over a proper store in an afternoon.
- Maturity impression: no tests of any kind, for a system whose entire behaviour is arithmetic over lists — the most avoidable gap in this atlas, since every property is a pure function of data.
- Study when: you want a long-running local companion on a machine with no GPU budget, and the best worked example here of how far plain arithmetic gets you.
- Do not copy when: you would take the code. The licence is source-available with a discretionary field-of-use clause and a royalty, and the data model cannot maintain its own invariants.

### [`zerostack`](../systems/zerostack/)
- Best idea: atomic write-then-rename with the reason in the comment, and a `.bak` whose extension deliberately keeps it out of the `.md` listing and out of search — a backup that cannot become a search result.
- Biggest risk: a destructive default on a missing argument, and a one-deep undo presented as safety.
- Most reusable component: the global-versus-project split and the atomic-write-plus-backup pair, liftable wholesale into any notebook system in any language.
- Maturity impression: 65 test functions in 1,203 lines — a ratio just under one to one — with a separate permission-path suite including `check_perm_skipped_when_permission_is_none`, which asserts the gate is a gate.
- Study when: you want a Markdown memory in a Rust agent and care more about not corrupting a file than about recalling the right line.
- Do not copy when: memory has to hold claims. There is nothing to mark uncertain, nothing to supersede, and no record that anything changed beyond one overwritable `.bak`.

### [`agentswarms`](../systems/agentswarms/)
- Best idea: the retrieval index is derived in the database by a trigger over the item's own content, so an application cannot insert a row that is unfindable or forget to update the index — and no model call sits between writing a fact and being able to recall it.
- Biggest risk: three columns that look like a lifecycle and are inert. `score` is read by the ranker and the prune ordering and never written; `usage_count` is displayed in the settings UI and never incremented; `expires_at` is never set or swept. The UI tells the user low-score items are pruned first, and no item ever has a low score.
- Most reusable component: `prune_agent_memory_items` — a `SECURITY DEFINER` function that compares its caller-supplied user id against `auth.uid()` before deleting anything, then has execute revoked from every client role. It is the same construct LoreKit leaves unchecked.
- Maturity impression: RLS on all three tables, a retention pass that deletes generated documents before the rows referencing them, and **no tests anywhere in the repository** — for a subsystem that is almost entirely pure functions over strings.
- Study when: you want the smallest complete long-term memory here that is not a file, or a worked example of lexical recall with no embedding and nothing to tune wrong.
- Do not copy when: you need memory to hold claims — there is no status, no provenance that is read, and no dedup, so a fact mentioned ten times becomes ten rows competing for the same twelve slots. And the Elastic License 2.0 forbids offering it as a hosted service.

### [`empryo`](../systems/empryo/)
- Best idea: git **co-change affinity** as a recall signal — a memory attached to files that historically change together with what you are editing surfaces without matching a query token, entered into the fusion at RRF rank 5 so it stays behind a direct hit.
- Biggest risk: soft delete is not rejection. `content_hash` is unique and the upsert treats a collision as an update that clears `hidden`, so re-saving the same sentence resurrects a memory the user deleted — with a test named for it.
- Most reusable component: `hashbag-v2`, a dependency-free 384-dimension embedder whose measured cosine ranges are documented and whose ranking curve is calibrated against them.
- Maturity impression: 3,271 test cases across 100 files with eight memory-specific suites, a browser with a bulk cleanup queue, and supersession correctly filtered on the read path.
- Study when: your memory is about a codebase and you want relevance signals the repository already contains.
- Do not copy when: a correction has to stick, or you need tenancy — scope is global-or-project on a local SQLite file, and the BSL restricts production use until the change date.
- Reported but not reviewed: the maintainer has extracted the memory layer into a private `packages/memory/` workspace and reports the content-hash resurrection closed there, plus a committed retrieval benchmark with a CI floor gate ([PR #2](https://github.com/neoneye/agent-memory-atlas/pull/2)). The public repository is unchanged at `e6b5885d` and does not contain that tree, so the verdict below still describes what is readable. The maintainer also reports a real-corpus arm of that benchmark scoring hit@3 0.082 against 0.857 on the synthetic fixture, unexplained, with a working hypothesis that real memories attach many more file paths than the fixture does and that stale ones dilute file affinity — the gap between a synthetic memory fixture and a live store is under-reported across this atlas, and this is the only place in it that anyone has published both numbers.
- Renamed: this was published as `soulforge` and the project is now **Empryo** (`proxysoul/Empryo`). The refacing commit predates the analysis — the atlas took the name from the repository URL rather than from the README, which already said so. The pinned commit and every finding are unchanged, and `/systems/soulforge/` redirects.

### [`dexto`](../systems/dexto/)
- Best idea: a five-method memory contract that includes `update(id)` and `delete(id)` — the two that AutoGen and ADK both omit, and that no better implementation can add afterwards.
- Biggest risk: there is no retrieval at all, and the contributor's `limit` is unset by default, so the shipped behaviour renders the entire store into every system prompt.
- Most reusable component: the contract itself, plus typed errors with a code per failure and a test for each.
- Maturity impression: 25 test cases against 605 lines aimed at the error paths, Zod bounds on every field, and a docstring that names the missing scope model as future work rather than implying it exists.
- Study when: you are designing a provider interface, or your memory is a short curated list a person pins.
- Do not copy when: the store is meant to accumulate — nothing ranks, nothing caps by default, and relevance is entirely manual.

### [`project-golem`](../systems/project-golem/)
- Best idea: `ExperienceMemory` — thirty-three lines that record which proposal types the owner declined and read them back into the agent's context before the next proposal. The rejection is written where the rejection already happens, needs no model, and is the one signal extraction can never produce.
- Biggest risk: the avoid list holds three entries, is keyed on the proposal type rather than the value, and `recordSuccess()` clears it entirely — so one accepted suggestion erases every rejection before it.
- Most reusable component: the outcome-gated write on the decline path, and the content-derived stable id that makes re-memorising idempotent.
- Maturity impression: a competent LanceDB driver that resolves every recall hit against the canonical list so a stale index cannot produce a wrong answer — beside 74 test files, none of which covers the rejection loop.
- Study when: you are building anything that proposes work to a person and want the smallest complete answer to "they said no, now what".
- Do not copy when: you need it commercially. The licence forbids it outright, and the memory is wired into a desktop app with no seam to lift it through.

### [`openyak`](../systems/openyak/)
- Best idea: the update queue is debounced by **workspace path rather than session id**, with a docstring saying why — two sessions in one directory collapse into a single refresh instead of racing to overwrite each other's document.
- Biggest risk: every write is a full overwrite of the only copy, and the guards are a ceiling with no floor. An empty rewrite is refused; a three-line rewrite replacing two hundred lines is written silently, and the 200-line cap truncates the tail with no marker.
- Most reusable component: the three write guards and the instruct-then-verify pattern — a prompt that bans Markdown in eight clauses and a parser that strips code fences anyway.
- Maturity impression: 90,000 lines of backend Python with 114 test files, exactly one of which touches memory — asserting where the section lands in the prompt, not what the update path does. Apache-2.0.
- Study when: you want a per-project brief that keeps itself roughly current with no retrieval to tune, or a worked example of handling concurrency in whole-document memory.
- Do not copy when: memory must hold facts rather than context. There is no unit below the document, so there is nothing to supersede, attribute or reject.

### [`memento`](../systems/memento/)
- Best idea: a memory sealed until a date. `status = 'sealed'` with a `deliver_on` column puts an entry outside transcription, indexing and the timeline entirely, and a worker pass moves it into the normal pipeline when the date arrives — enforcement by state rather than by a predicate every query must remember.
- Biggest risk: `source_entry_id` is `ON DELETE SET NULL`, so deleting a recording leaves every fact derived from it in place with its provenance silently erased — indistinguishable from a fact that never had a source.
- Most reusable component: partial indexes that encode liveness — every live index declared `WHERE deleted_at IS NULL`, so the fast path and the correct path are the same object.
- Maturity impression: a 208-line schema with status vocabularies, soft delete everywhere and a worker that deletes a daily summary when its source entries are gone — beside no test suite at all.
- Study when: you need memory that becomes available rather than memory that fades, or you want the cleanest small example of provenance from a derived fact to its evidence.
- Do not copy when: you need it commercially — PolyForm Noncommercial forbids it — or you need a correction to survive, since a deleted profile fact can be re-derived by the next reflection pass.

### [`universal-memory-engine`](../systems/universal-memory-engine/)
- Best idea: rejecting a candidate with `suppress_similar` writes a row to `memory_suppressions` keyed on the canonical label, and the write gate checks it at four points — a hit is rejected as `suppressed_blocked` and never written. The cleanup pass writes one too, so a deletion binds the future rather than waiting to be re-derived.
- Biggest risk: `events.happened_at` sits beside `created_at` and the automatic gate stamps it with `now`, so the column that would carry validity time is collapsed by the writer that produces most memories — while the read path already sorts by it.
- Most reusable component: the split between `reject` and `reject with suppress_similar`. One boolean separates "this guess was wrong" from "stop proposing this", and only the second binds anything.
- Maturity impression: eleven dated migrations, receipts with a `meaningful_no_write` outcome that distinguishes a quiet system from a broken one, and a 32-query golden retrieval set with per-query forbidden ids — beside no test on the suppression gate itself.
- Study when: you want the fourth working tombstone in this atlas, or an eval fixture built around identity confusion rather than recall.
- Do not copy when: you cannot live on Cloudflare — D1, Durable Objects and Workers are the substrate, so porting means keeping the shapes and rewriting everything beneath them.

### [`membase`](../systems/membase/)
- Best idea: `_coerce_owner` forces the `owner` field on every hub upload to the address recovered from the caller's signing key, and warns loudly when it had to override — ownership is possession of a key rather than a string in a payload.
- Biggest risk: `ChromaKnowledgeBase.retrieve` reads Chroma's `distances` array into a variable named `similarity`, so raising the threshold to demand better matches keeps the farthest documents and drops the nearest; any non-zero threshold also swaps vector search for a literal `$contains` filter on the whole query.
- Most reusable component: `src/membase/storage/_auth.py` — eighty lines of secp256k1 signed headers that transfer to any project already holding a wallet key.
- Maturity impression: no CI, the only test of the summarisation path has no assertions, and nothing in `src/membase/memory/` has changed since 24 July 2025 while HEAD is 10 June 2026.
- Study when: you want to see a distance and a similarity read from the same field a hundred lines apart, and a test suite that passes over both.
- Do not copy when: you need deletion to mean anything — `delete` removes the SQLite row and never calls the Chroma delete that retrieval reads, and one deletion also stalls long-term consolidation permanently by leaving a sixteen-message block short.


### [`palazzo`](../systems/palazzo/)
- Best idea: the write-ahead log is a *precondition* for a destructive operation, not a record of it. `log_strict` fails the delete when the audit entry cannot be durably appended, on the stated reasoning that the WAL is the only trail — and the entry carries a text preview, so it says what was removed.
- Biggest risk: the README's stated differentiator over the generic Qdrant server is an "enum-validated palace schema", and `src/schema.rs` says the four tags are "deliberately free-text… never enforced". `validate_tag` trims and length-caps; there is no enum in the crate.
- Most reusable component: `src/wal.rs` — 129 lines including its tests, no dependency on the rest of the crate, and the split between best-effort logging for writes and strict logging for destruction.
- Maturity impression: 63 inline Rust tests, CI running clippy at deny-warnings across two feature sets plus `cargo audit`, and a committed benchmark note reporting its own loss with Wilson intervals and a stopping rule.
- Study when: you want the audit-as-precondition variant, or an example of a duplicate probe that deliberately refuses to match superseded points — the collision [Empryo](../systems/empryo/) resolves the other way.
- Do not copy when: recall is the requirement (its own pilot puts R@5 at 36% against the 96.6% it cites as the bar, diagnosed as ranking rather than coverage), or more than one person shares the store — there is no tenancy, no verified identity and no default scope.


### [`aura`](../systems/aura/)
- Best idea: the receipt store keeps a SHA-256 hash chain beside it — `seq`, `content_hash`, `prev_hash`, `entry_hash` — so deletion shows up as a sequence gap and insertion as a broken link, and verification re-hashes the on-disk bodies. Every other append-only audit here would read clean after being rewritten. I ran `tests/test_audit_chain.py`: 16 passed, including the modified-body, broken-link and deleted-entry cases.
- Biggest risk: the belief machine that would use all this is a plain dictionary. `active | trusted | contested`, a resolution API, and a rule that a trusted belief cannot be contradicted — none of it saved or loaded, so every trust state resets on restart. A second belief store in the same codebase does persist and has no status field, and the `contested` flag stamped on every memory record is read by nothing.
- Most reusable component: `core/runtime/audit_chain.py`, and the write gateway's two fail-closed branches — no authority wired, and the authority call raising.
- Maturity impression: 21,206 test functions across 1,740 files, a claims matrix pairing each claim with a reproduce command and a falsifier, and a `CLAIMS_NOT_SUPPORTED.md` that puts recursive self-improvement in the unsupported column while reporting its own capability curve going down, 0.667 to 0.625.
- Study when: you want tamper-evidence rather than append-only, or an admission-control layer that clusters near-duplicates before counting corroboration and refuses both sides when no rule separates them.
- Do not copy when: literally — the licence is all rights reserved, read-and-learn only, no derivative works. Also when you need forgetting with a reason: retention is RAM-scaled keep-counts, so memories leave because the machine is small, never because they turned out to be wrong.


### [`memex-zero-rag`](../systems/memex-zero-rag/)
- Best idea: the directory contract — `raw/` immutable and read-only to the model, `wiki/` entirely derived, `L1/` private, git as the whole history. Every derived page can be rebuilt and no model error can destroy the inputs, stated in one line of `SCHEMA.md`.
- Biggest risk: `L1/credentials.md` is tracked in git despite `L1/` being in `.gitignore` and the file itself warning *"This file is git-ignored. NEVER commit credentials."* `.gitignore` does not untrack what is already tracked, so a user who fills it in and pushes their fork commits their API keys.
- Most reusable component: `SCHEMA.md`, which is a better specification than several machine-readable ones here — if the model does the structuring, the document telling it how is the real schema.
- Maturity impression: no tests and no CI for 3,300 lines; an MIT badge, no `LICENSE` file, and `All rights reserved` on all eight source files; and `KNOWLEDGE-DECAY.md` reads as the trust model while being a draft whose fields appear nowhere in code.
- Study when: you want the Karpathy wiki pattern packaged, or a clean case study in what it costs to express every invariant as an instruction rather than a check.
- Do not copy when: a rule has to hold on the turn the model is confidently wrong. The citation "enforcement" is a manual substring report with an unimplemented fix mode, the *"It STOPS and asks you to decide"* contradiction gate is touched by none of the nine tools, and search is an unranked substring scan that gets worse as the wiki gets richer.


### [`agentrecall-x`](../systems/agentrecall-x/)
- Best idea: `isNoiseCandidate` — a p0 correction surfaced at least three times and honoured less than 30% of the time is excluded from its own veto. The only mechanism in this atlas where a record's authority is *withdrawn* by measured evidence rather than merely granted by provenance.
- Biggest risk: `precision` is `heeded / retrieved`, and heeded is judged by the loop observing whether the agent honoured the rule — the same system whose compliance is being scored. The property that makes the demotion trustworthy is measured by the thing it constrains, and the committed benchmark that would check it is twelve cases.
- Most reusable component: the `CorrectionRecord` field design — three separate endings (`retracted_at` with a reason, `superseded_by`, `merged_from`) that all keep the record on disk, plus the outcome counters underneath the demotion rule.
- Maturity impression: 124 test files with ten named for the corrections mechanism itself, a committed four-axis replay result that publishes 33% precision against itself, and comments that cite dated decisions and explain why a field is deliberately not defaulted.
- Study when: you have guardrails that fire and no way to retire the ones nobody obeys, or you want the cleanest separation in this atlas between who writes a rule and who must obey it — the model's thirteen tools include no way to author or retract a correction.
- Do not copy when: you need the trust machinery shared across a team (the Supabase schema has no corrections table), or content-level correction — the mechanism guards behaviour, and `UNIQUE(project, store, slug)` is dedup, not a tombstone.


### [`memledger`](../systems/memledger/)
- Best idea: `memory.policy.yaml` is canonicalised (RFC 8785) and hashed, and the hash is recorded in every event it influenced — so a decision points at the policy version that actually produced it, and editing the policy never rewrites history. Nothing else here can say which version of its own rules made a call.
- Biggest risk: the dedup lookup is `WHERE subject = ? AND relation = ? AND value_json = ? AND status != 'deleted'`, so a fact the user deleted is not found and a fresh active record is created. The deletion is durable, keyed on the value, and terminal in the state machine; the one query that could enforce it skips it.
- Most reusable component: the event envelope and its validator — actor, cause, `policy_hash`, `sources` required for derived events, and an `LLMCall` block required if and only if the actor is a model.
- Maturity impression: sixteen commits over a week, 37 tests, a LoCoMo runner and a regression case file — and no committed result artifact, so the runners are process rather than evidence.
- Study when: you cannot answer "why does my agent believe this", or you want a five-status memory state machine with its legal transitions written down as a checked set and two terminal states.
- Do not copy when: you need the correction to stick. The states are right and nothing consults them on write, which is the whole gap in one sentence.


### [`terse-memory`](../systems/terse-memory/)
- Best idea: `# Hot buttons ## Don't` — a user-extendable prohibition tier that is always loaded rather than retrieved, with a lint rule (`MEM-G`) warning past twenty objects so it stays affordable. A rule that must never be missed should not depend on a query returning it.
- Biggest risk: the package has no capture, recall, forget or consolidate function — those are the model's job via a skill — and of the seven lint rules, the three deferred to v0.2 are exactly the epistemic ones: `MEM-C stale`, `MEM-D consolidation-due`, `MEM-E duplicate`. What ships polices hygiene; what is scheduled polices truth.
- Most reusable component: the schema decisions — `as-of` required on nearly every kind, and a `session:` attribute paid for at write time so "forget this conversation" resolves to a query instead of a guess.
- Maturity impression: three commits, HEAD 24 July 2026, spec marked pre-release — and 89 tests that I ran and that pass, covering the linter, the scaffolder and the wiring.
- Study when: you want a typed, diffable single-file store with a structural query syntax, or the always-loaded prohibition tier on its own.
- Do not copy when: you need the operations implemented. Explicit forget deletes and records nothing, `stale` is a status nothing sets, and the stated rule that auto-capture from untrusted content is "a protocol violation, full stop" has no detector.


### [`agentic-context-engine`](../systems/agentic-context-engine/)
- Best idea: a `SimilarityDecision` records the pairs the consolidator decided to KEEP separate — the pair, the reasoning, and the similarity at the time — serialised with the skillbook and checked in the detector's inner loop (`detector.py:234`) before the pair is proposed again. The only durable record of a decision *not* to act in this atlas, and the only one that is consulted.
- Biggest risk: everything above the storage layer is a model following a prompt, and `similarity_at_decision` — the field that would let a settled pair be re-opened when it drifts closer — is stored and never compared against anything.
- Most reusable component: the KEEP record itself, under thirty lines including the dataclass, two accessors and one `continue`. It generalises past memory to any pipeline that re-proposes the same merge or match on every pass.
- Maturity impression: 788 commits since November 2025, 31 test files, a benchmark package with task loaders and four live scripts including a τ-bench retail one — and no committed result, so the claim the project leads with is the one it has built the apparatus to check and not published.
- Study when: you repeatedly ask a model the same pairwise question, or you want the counter-usage rule — `harmful_count` is explicitly forbidden from being a hard removal trigger because usage and harm correlate.
- Do not copy when: you need the skillbook's quality to be measurable. The counters gate nothing by design, and removal quality rests entirely on a reflection nothing checks.


### [`deer-flow`](../systems/deer-flow/)
- Best idea: a three-tier plugin contract that replaced `hasattr` probing with defaulted hooks on the base class, plus a `noop/` backend shipped as the copyable template and a stated portability rule — a backend talks to the host through exactly two channels and may make exactly one host import.
- Biggest risk: every backend must return the default backend's response shape, and the README names the failure itself — pydantic ignores unknown fields, so a Mem0 or OpenViking adapter silently drops whatever those systems model beyond `facts[]` and a timestamp, and the symptom appears three layers away as a frontend crash on an empty date.
- Most reusable component: `backends/README.md` as a design document. The tiering, the compiled template and the two-channel rule are independent of anything DeerFlow does.
- Maturity impression: 200 commits in twelve days, four working backends, a `test_memory_prompt_injection.py` almost nothing else here has — and no committed comparison across the three real backends the harness makes swappable by one config line.
- Study when: you are designing a host contract for pluggable memory, or you want the rare case of a scope key that crosses a plugin boundary with the widening path gated on an authenticated token.
- Do not copy when: your backend models epistemics. No status, confidence, provenance or supersession field crosses this contract at any tier, so a system that grades its memories is flattened on the way to the interface.


### [`ean-agentos`](../systems/ean-agentos/)
- Best idea: deterministic capture. Commits via a git post-commit hook, bash commands with exit codes and durations, tool calls and file versions all arrive because a hook fired rather than because a model judged the moment important — and `errors_solutions` models the attempt, with `solution_worked` and an `attempts` counter, not just the conclusion.
- Biggest risk: both recall paths are `ORDER BY solution_worked DESC` rather than a `WHERE`, so a fix that did not work is returned one row lower in the same shape as one that did. For a project whose pitch is stopping repeated bug fixes, the guard against repeating a known-bad fix is the model reading a boolean in the result row.
- Most reusable component: the `errors_solutions` schema, and the hook installer's mark-and-restore discipline — it backs up another program's settings, marks its own entries, and removes exactly those on uninstall.
- Maturity impression: 51 commits between 16 and 19 March 2026 and nothing since; 59 tests named by build phase rather than by behaviour, and none named for the error-recall path the product is built around.
- Study when: you want capture that does not depend on an extraction pass noticing, or a schema that records what was tried and failed rather than only what worked.
- Do not copy when: you need the failure withheld rather than demoted, or you are storing shell output — `bash_history` keeps `command`, `output` and `error_output` verbatim with no secret scanning found.


### [`m-flow`](../systems/m-flow/)
- Best idea: three separate modules front an expensive model call with a zero-cost deterministic one and say so in the docstring — the procedural trigger ("Layer 1: Rule trigger (zero cost). Layer 2: LLM light classification"), the conflict detector ("Deterministic first, LLM fallback"), and a worth-storing screen that runs before a procedure is built and indexed rather than pruning afterwards. The trigger also separates *should we retrieve* from *should we inject*, which almost nothing else here does.
- Biggest risk: the claim that distinguishes it — anchor on the most precise node, then path-cost propagation, beating layer-selection retrieval — is a retrieval-quality claim, and no committed benchmark result exists. The per-edge costs that make paths compete are the ranking signal and are uncalibrated against anything in the repository.
- Most reusable component: the procedural governance chain — worth-storing, classifier, deterministic-then-LLM conflict detection, a generated version diff, and `reconcile_active` deciding which version is live.
- Maturity impression: 149,000 lines across four deployable packages with Alembic migrations, Docker and a starter kit — and integration tests that need a graph database and a worker queue, so nothing here was run.
- Study when: you are building tiered gates around model calls, or you want a third point on the spreading-activation axis beside NOOA Memory's ACT-R decay and HippoRAG's PageRank.
- Do not copy when: "one strong path is enough" would be applied to belief rather than recall — a single low-cost chain is a good reason to look somewhere and a weak reason to believe something, and the graph does not distinguish.

### [`nova-ai`](../systems/nova-ai/)
- Best idea: a relation is stored only after the user answers a spoken question — "may I remember that X is a kind of Y?" — with sense disambiguation asked first, so the only path from parsed language to a stored belief runs through a person, in the turn where they still have the context to answer.
- Biggest risk: every path to a refusal runs through the user. Nothing lets the system refuse its own bad inference, and the `unverified` backlog that Wikipedia and auto-extraction produce is never counted or offered for confirmation, so it grows silently while nothing prompts anyone to work it down.
- Most reusable component: a refusal keyed on the definition text that automatic re-extraction cannot lift, because the dedup lookup finds the rejected row without exempting it — the whole tombstone, in a loop that was written for deduplication.
- Maturity impression: 25,000 lines of one author's carefully documented Python with an unusually detailed changelog, four capability marks, and 21 test files holding five assertions between them — so the mechanisms that earn the marks are pinned by nobody, and the verification is a person's practice rather than the repository's.
- Study when: you want to see what correction machinery looks like when there is no model to blame; every epistemic decision here had to be written down because nothing could be delegated to a language model.
- Do not copy when: literally — the licence is "Viewable, Not Reusable". Also when you need more than one user, since no scope key exists anywhere, or a store that survives an interrupted write, since the whole graph is rewritten non-atomically on every save.

### [`memsem`](../systems/memsem/)
- Best idea: the benchmark is committed, wired into `npm test`, and reproduces exactly — P@3 0.958 with an ablation across four alternative constant weightings, so the defaults have to keep beating the alternatives on every run, and an author-written honest reading names the set's limits.
- Biggest risk: the durable rejection is real and only a human can arm it. A rejected candidate writes a value-keyed suppression that refuses every later write; automatic supersession writes none, so a re-asserted value returns and fades the live correction — three repetitions archive an ordinary one, and six take a pinned one off the top of a search while leaving its confidence untouched.
- Most reusable component: the audit row — entity, field, old and new value, a reason, a pass id that caps a sub-agent's cumulative adjustment, and a dry-run flag that records what would have happened without applying it.
- Maturity impression: twenty-one commits and sixteen READMEs, and the engineering habits underneath are better than that ratio predicts — bounded sub-agent authority enforced in code and tested, an adverse-case governance suite that exits non-zero, five committed negative retrieval cases, and a purge that cascades rather than a flag rename.
- Study when: you are deciding what a defensible retrieval number looks like; this is the corpus's cleanest example of a claim a reader can check in one command.
- Do not copy when: a correction has to hold without anyone having pinned it. The rejected value is keyed and consulted, so re-entry costs it a `resurrectConfidence` discount — but a discount is a price, not a prohibition, and repetition pays it off.

### [`cambium`](../systems/cambium/)
- Best idea: a check that refuses to return a pass it did not earn — run against its own tree, the freshness tool prints `overdue=0` and `fresh=0` together and concludes "NOTHING CHECKED… this is not evidence of freshness", and the vocabulary check exits 1 rather than assume a vocabulary no profile has composed.
- Biggest risk: it ships no corpus, so everything downstream of a composed vocabulary — conformance, freshness, duplicates, MOC coverage, delta application, terminal proof — has no public passing run. The reference profile validates; the vocabulary it would compose is blocked by the repository's own deliberately unfilled governance page.
- Most reusable component: the prohibition that automated checks may never raise a status — the scripts emit only `fail` and `candidate`, so automation can block work and nominate work and can never promote a belief.
- Maturity impression: 5,687 lines of deterministic tooling and 6,453 lines of normative prose against 73 lines of tests covering one of twelve scripts; two things are demonstrated rather than specified — the kernel's own 1,171 wiki links all resolve, and the reference profile binds every interface slot with no unfilled marker left.
- Study when: you are designing quality gates for agent-maintained knowledge and want the vocabulary for separating "checked and fine" from "could not be checked".
- Do not copy when: you need a memory component. It stores nothing, retrieves nothing and ranks nothing — adopting it means adopting a working method, not adding a dependency.

### [`perseus-vault`](../systems/perseus-vault/)
- Best idea: three independent full runs per benchmark condition, every report committed with a complete config stamp, and the answer prompt folded into the run signature so a chain-of-thought number can never be quoted beside a plain one — the published means recompute from those artifacts exactly.
- Biggest risk: the tombstone's reach is claimed in a comment and not walked by a test. `remember_impl` says the check covers agent remember, capture, ingest, connectors and derived writers, and the committed cases cover the write paths and the audited override — the background consolidation, cohere and dream passes are the leg nothing exercises.
- Most reusable component: the `CLAIMS-AUDIT.md` habit — a file that retires claims it cannot back, naming the retired figure, why it failed, and the artifact that replaced it, including downgrading its own "signed results" to "content-hashed".
- Maturity impression: 59,000 lines of Rust, 536 inline tests, all seven capability marks, and a count claim that is derived from the source registry and asserted across five published surfaces by a CI job rather than by a command in a Markdown file.
- Study when: you are deciding what a defensible benchmark claim looks like, or you want bi-temporal history and a hash-chained journal in a single local binary.
- Do not copy when: you need multi-machine sync, since federation is export and re-import; or encryption on a database that predates the default, since the flip covers fresh installs and an older one stays plaintext until an explicit `init --rekey`.

### [`provem`](../systems/provem/)
- Best idea: a replay script that asserts every published number instead of printing it, exiting non-zero on drift — 21 assertions from frozen artifacts at zero cost, 25 with the governance benchmark and unit tests, and it passes.
- Biggest risk: erasure is read-side suppression, not write-side refusal. A re-ingested erased value still lands in the backing store and is stopped on the way out, so every future read path has to consult the registry and the store retains what a subject asked to erase — the sharpest thing to press on a product whose stated purpose is Article 17.
- Most reusable component: `forget(term, scope)` — delete the rows, append the term's token set to a per-tenant erased registry, emit an erasure certificate, and exclude any later record whose tokens are a superset. A value-keyed tombstone with a normalized, forgiving key.
- Maturity impression: 21,000 lines with 7,600 lines of tests, a claim register that marks its own claims `Unsupported` and "Rejected for now", a research journal of negative results, and two of four deployment tiers published as losing — one below the no-memory baseline.
- Study when: governance is your actual problem, or you want to see what a defensible claim looks like when the repository itself fails CI if the README drifts.
- Do not copy when: the governance suite's numbers are being read as general. It is self-authored, so it measures the failure modes its author modelled; a reproducible number is not a generalisable one.

### [`argo`](../systems/argo/)
- Best idea: retrieval that fails closed when the embedding index is not qualified, and a write that cannot report success when indexing failed — both asserted by committed acceptance cases rather than described, in a suite of architecture fitness functions running four times the volume of the implementation it covers.
- Biggest risk: the graph is a projection, not a memory. `clearGraph` wipes it with `DETACH DELETE` and re-creates every node on each sync, so there is no supersession, history, status or audit anywhere in the store; correction lives in a JSON file and whatever review surrounds it.
- Most reusable component: the ArchiMate 3.2 rule engine — a constrained relationship vocabulary means a malformed architectural claim is refused by a rule rather than caught in review, which is the schema doing work free-text extraction cannot.
- Maturity impression: 861 commits, 27,152 lines of tests to 6,674 of graph-rag implementation, a 54 KB design document for one subsystem — and the suite is red at HEAD, 114 passed and 8 failed, including its own credential boundary.
- Study when: you already model your system and want an agent that can query architecture instead of re-deriving it, or you want to see architecture fitness functions used as a delivery gate.
- Do not copy when: you need a general-purpose store. The memory here is one project's architecture model, and adopting it means adopting the modelling practice first.

### [`sovereign`](../systems/sovereign/)
- Best idea: refusal as a first-class outcome — energy cost scaled by priority, a boundary that clears only past the threshold plus a margin so it cannot flap, a hard floor, and a returned reason string that lets a caller tell a refusal from a failure from an empty result.
- Biggest risk: an episode has no identifier, and no update, delete, forget or supersede exists anywhere in the module, so nothing stored can be corrected — the question this atlas asks has no place to be asked rather than a bad answer.
- Most reusable component: the hysteresis. Clearing a boundary at `threshold + 0.1` rather than at `threshold` is two characters and removes an entire class of flapping, and it applies to any boundary crossed repeatedly.
- Maturity impression: 634 lines with atomic persistence and a required covenant enforced in the constructor — and `pyproject.toml` is invalid TOML, a root `amity.py` shadows the packaged module byte for byte, and the README calls the committed passing tests "not present yet".
- Study when: you want to see admission control treated as an ethical mechanism rather than a rate limiter, in a codebase small enough to read in one sitting.
- Do not copy when: you need a memory. Recall is a timestamp filter over a bounded deque whose evictions are uncounted, in the one buffer whose contents are the product.

### [`memoryops-ai`](../systems/memoryops-ai/)
- Best idea: tenancy enforced by Postgres row-level security through transaction-local GUCs, so a recall path that forgets its tenant predicate returns nothing instead of everything — the strongest isolation mechanism in this atlas, and stated in the code as defense in depth beside the application check.
- Biggest risk: deletion is record-keyed. `soft_delete` sets `deleted_at` and the dedup lookup is filtered to active rows, so a value that was deleted and is later re-asserted returns as a new active memory — while `normalized_content`, the key that would stop it, is already computed, persisted and compared.
- Most reusable component: the audit chain serialised through a per-tenant head row, so concurrent mutations cannot fork it into two valid-looking histories, with `verify_chain` exported so a caller rather than the writer can check it.
- Maturity impression: 39,000 lines of Python across a monorepo with a published SDK, a hosted demo, RLS migrations, and eval sets that plant a cross-tenant memory before asserting it is unreachable — none of it run for this review, because five dependency surfaces were inside the seven-day cooldown.
- Study when: multi-tenancy is real and you want to see governance placed below the caller rather than beside it.
- Do not copy when: you need a deletion that stays deleted against an automatic writer; the machinery for that is present and unused.

### [`deepcode`](../systems/deepcode/)
- Best idea: typed provenance on conversational input — a `ClientSurface` of `cli`/`desktop`/`headless`/`automation`/`app_server`/`internal` and a `TurnInputSource` of `start`/`steer`/`queue`/`goal_continuation`/`automation`/`retry`, so months later the store can still say whether a person steered a turn or an automation retried it.
- Biggest risk: `autodream` is a scheduled agent turn holding `delete` over a flat directory of markdown notes that has no history, no protected flag and no record a note ever existed — and the only mechanical signal, which the scheduler also treats as its stopping condition, is whether the file count changed.
- Most reusable component: `system_preamble()`, which assembles user-global instructions, a repo-root-downward `AGENTS.md` walk, the memory index and the tool description in one function that every frontend calls, so the TUI, the desktop app, the headless path and the app server cannot drift apart.
- Maturity impression: roughly 118,000 lines of Python with an event-sourced thread store, a crash-recoverable deletion journal, and a memory module whose docstring states plainly that consolidation has no test oracle — while the test beside it patches in a scripted no-op provider and the docstring's claim of verification "with a real model" has no committed counterpart in the tree.
- Study when: you want to see what an event log, replay and typed provenance look like applied to conversation state, and what it costs to leave the durable-facts store outside all of it.
- Do not copy when: a remembered fact is expensive to reacquire. Nothing marks a note as unconsolidatable, nothing records its deletion, and session deletion does not reach the notes at all.

### [`prime-agent`](../systems/prime-agent/)
- Best idea: every applied harness edit keeps a full `before` and `after` snapshot, appended to a cross-session `refinements.jsonl`, so `rollbackProposal` can invert a refinement made in another session — the most complete undo for a self-modifying memory in this atlas, and tested as such.
- Biggest risk: nothing is keyed on a rejected value. Rollback answers "can I undo what it learned" and not "can I stop it learning that again", so a memory deleted as wrong can be proposed again by the next pass as a fresh create.
- Most reusable component: the baseline check — an edit whose target entry changed while the model was planning is refused with `entry changed during refinement planning`, with the same-proposal case correctly excluded. A lost-update defence on a memory write, in about ten lines.
- Maturity impression: 184,000 lines of TypeScript and 4,469 commits, with a 1,519-line test file covering the baseline guard, the immutable base prompt from both directions, atomic state replacement, scope-merge collisions, malformed history lines, and cross-session rollback — none of it run for this review, because six dependency surfaces were inside the seven-day cooldown.
- Study when: you are building a background pass that edits durable state on model judgement and want to know what making it reversible actually costs.
- Do not copy when: you need a correction that holds against re-derivation; the undo is excellent and there is no refusal behind it.

### [`mnemosyne`](../systems/mnemosyne/)
- Best idea: extracted facts are keyed by a SHA-256 of the subject, predicate and object, and the dedup lookup before every fact write matches that triple without excluding superseded rows — so a re-extracted rejected value lands on the tombstoned row and stays rejected. The atlas's eighth value-keyed refusal, and one of two that appear to be a side effect — [Nova AI](../systems/nova-ai/) reaches the same property by the same missing filter, in another language on another data model.
- Biggest risk: provenance is recorded twice and acted on wrongly both times. `veracity` weights `unknown` at 0.8, above `tool` at 0.5, so labelling an origin honestly costs a memory rank; `trust_tier`, documented as prompt-injection defense, coerces an unrecognized source to the highest tier and is read by no query, score or filter anywhere in the tree.
- Most reusable component: `compute_fact_id` — a SHA-256 over NFC-normalized, length-prefixed components, with the docstring working through the truncation collision, the separator-smuggling case and the unicode-normalization case that each defeated an earlier version. Content-addressed identity done properly, in thirty lines.
- Maturity impression: 43,559 lines with 51,407 lines of tests across 160 files, 956 commits since 5 April 2026, CI on every push including a no-optional-dependencies job, a 1,624-line doctor and a 1,036-line repair module — beside a 9,326-line `beam.py` and a tiered-degradation compressor that rewrites stored content irreversibly and has no caller.
- Study when: you want local, private, agent-controlled memory in one SQLite file with no services, or you are migrating off a hosted memory product — the importers cover nine other systems, the widest exit path in the corpus.
- Do not copy when: you need to explain why the agent believed something. Trust is a float and two labels, one scored backwards and one inert, with no discrete epistemic state anywhere.

### [`omi`](../systems/omi/)
- Best idea: `ACTION_POLICY` maps each epistemic status to a set of permitted *uses*, and `can_use_for_action` requires an `accepted` fact before an irreversible action — so an unreviewed memory may answer a question with a disclaimer and may not send, buy or delete anything. Trust gating capability, graded by reversibility.
- Biggest risk: every refusal is keyed on a row while the transcript that produced it is retained by design, so a rejected fact can be re-derived from the same audio and re-enter as a fresh candidate. Ambient capture is where record-keyed correction fails fastest.
- Most reusable component: two confidence fields with different jobs — `capture_confidence` for whether the source was heard correctly, `veracity` for whether the claim is true — beside `subject_attribution` recording whether the fact is even about the user.
- Maturity impression: 540,721 lines of backend Python under 259,452 lines of tests across 843 unit files, a hash-chained per-user commit ledger with optimistic concurrency, an outbox that reloads canonical state before every external write, and per-user encryption at rest — six of seven capability marks.
- Study when: you are building memory for anything that captures continuously and can then act — a wearable, a meeting recorder, a screen agent. The problems it solves arrive with ambient capture and not with a chat box.
- Do not copy when: you need an inspectable store or a memory layer separable from its product. This is Firestore, Pinecone, a worker fleet and a device; the value transplants as design decisions, not as code.

### [`kirocrew`](../systems/kirocrew/)
- Best idea: seven typed refusal codes on the memory write path — key format, allow-list, reserved prefix, confidence floor, size, injection, conflict — so "the write didn't happen" is seven distinct loggable facts rather than a boolean, and four of them land in an events table a dashboard renders.
- Biggest risk: every refusal is recorded and none is consulted. A value blocked as an injection today is re-screened by the same pattern list tomorrow, and that list's precision is unmeasured — so the whole gate rests on a classifier nobody has scored.
- Most reusable component: redacting exfiltration URLs and credentials from an audit snippet *before* persisting it, because the dashboard renders it verbatim. The only system here that treats its own security log as an attack surface.
- Maturity impression: 475,988 lines of Python under 502,973 lines of tests across 1,024 files, 1,606 commits since 1 June 2026, Apache-2.0, with a `pysqlite3`-without-`connect` fallback that someone clearly met in the wild.
- Study when: you want an agent that cannot quietly learn arbitrary things about you — the allow-listed key namespace and the `user_explicit`-only `system.` prefix are the clearest worked example in the corpus of stopping that at the schema.
- Do not copy when: you need multi-user or multi-project isolation. No scope key exists on either table, and retrofitting one is a migration plus an audit of every read.

### [`mnemory`](../systems/mnemory/)
- Best idea: the consistency check screens stored memories for prompt injection with a regex *before* any LLM stage reads them, and re-screens material that already passed the write-time filter — treating the store as a live attack surface rather than something validated once at the door.
- Biggest risk: no audit record of anything. A checker that can be scheduled with auto-fix edits a user's stored memory on an unmeasured LLM judgement, and the issue list it worked from is an in-memory cache with a TTL, so "why is this memory gone" is unanswerable in principle.
- Most reusable component: the run/review/apply cycle — `start_fsck`, `get_fsck_status`, `apply_fsck` — which puts a person between a machine-proposed change and the store, and which the same codebase also offers with the person removed.
- Maturity impression: 26,650 lines under 24,205 lines of tests across 24 files, including 1,673 lines testing the prompts, a complete LoCoMo harness whose scores the README publishes in a six-system table it places second in, Prometheus metrics and a Grafana dashboard in the tree.
- Study when: you want a self-hosted memory service several MCP clients share, with per-user isolation enforced in the query rather than after it.
- Do not copy when: you need memory without a model in the loop — extraction, classification, dedup and contradiction resolution are one LLM call with no fallback — or you need to answer questions about the store's past.

### [`engram-alpha`](../systems/engram-alpha/)
- Best idea: two stated principles its trust module enforces — *"time doesn't validate"* and *"exposure doesn't validate"* — so stable knowledge decays only when a judged `conflicts-with` edge stamps `demoted_at`, retrieval moves nothing, and withdrawing the evidence withdraws the demotion.
- Biggest risk: every arm on every corpus, its own and LongMemEval alike, is graded on what retrieval delivered rather than on an answer — and the external run prices the calibrated warning line's false positives without pricing what that line costs on the answerable questions, which the offline suite puts at 47% of them warned at 100 notes and 48% at 1,500.
- Most reusable component: the audit journal — insert-only, full before and after JSON, an eleven-value action vocabulary, and the originating surface (`pane | mcp | daemon | cli | library`) on every row, which is the first thing you want when a memory turns out wrong.
- Maturity impression: 26,244 lines of Rust across three crates, shipping on three editor marketplaces with a browser demo of the real pane, and 84 committed evaluation artifacts — an ablation that labels its shipped row `<- ships today` and shows pure RAG beating it on recall, a supersession bench run against its own no-supersession ablation, and a full-population external run on a SHA-pinned corpus.
- Study when: you are deciding which signals may move an agent's trust, or how to fit a threshold you have no labels for. The policy module is the clearest statement in this corpus of what may change what an agent believes, and `fit_weak_line` fits an abstention threshold from unanswerable probes built out of the graph's own vocabulary.
- Do not copy when: you need multi-project or multi-tenant memory — there is no scope key on either table — or a stable API.

### [`helix-agi`](../systems/helix-agi/)
- Best idea: the comment that records why relation count was removed from a belief's mass — *"relations → mass ↑ → gravity ↑ → co-injection → more relations"* — a self-reinforcing loop between reachability and importance, found in a running system and cut on purpose, with cluster gravity left to emerge from spatial density instead.
- Biggest risk: the append-only journal its own docstring calls *"the single source of truth"* is the one store no delete path writes to, and the preconscious resolves content out of it when the belief store misses — so a removed belief's text can still reach the prompt.
- Most reusable component: `BeliefDetector`, a per-pulse local-model gate that answers one yes/no question and writes a pulse id to a pending file, doing *"NO extraction, classification, embedding, or comparison"* until the nightly pass.
- Maturity impression: 59,313 lines of Python, AGPL-3.0, with committed per-run benchmark artifacts and line-by-line subsystem audits in `documents/` — beside a documented nightly `compact()` that has no caller and two journal-bootstrap functions that are defined and never called.
- Study when: you want ambient recall that costs no embedding call per turn, or a decay rule written as an equation with named terms rather than a magic half-life.
- Do not copy when: anyone will ever ask whether a memory is gone — deletion reaches both runtime indexes and neither the journal nor the inbound references that point at it.

### [`aimaos`](../systems/aimaos/)
- Best idea: a phrasing-skeleton channel in the duplicate detector — same skeleton, shared anchor token, swapped value token — added to catch *"contradictions that embeddings place far apart"*, which is exactly where similarity search is weakest and where contradiction lives.
- Biggest risk: the superseded wording is kept on the row as `previous_content` and read by nothing, so re-asserting an overwritten value supersedes back and the store oscillates with no record that either value was ever judged.
- Most reusable component: the rule that a reversal is not corroboration — on contradiction, `verifications` resets to one and confidence is replaced rather than boosted, so a fact confirmed five times and a fact that flip-flopped five times do not look alike.
- Maturity impression: 26,798 lines of Apache-2.0 Python across a five-agent office with an Android client, a pinned lockfile beside a floating manifest, and a release audit that retires its own earlier benchmark notes as inaccurate — beside a memory package that no committed test constructs.
- Study when: you want contradiction detection that does not depend on an embedding model, or a memory layer already factored behind adapters for a different runtime.
- Do not copy when: a correction has to hold — nothing consults the value it replaced — or two people share an agent, since isolation here is one directory per agent and no user axis at all.

### [`aeris`](../systems/aeris/)
- Best idea: a validator that refuses to hand a language model the engine's own vocabulary — eighteen forbidden identifiers, a bare-entity-id check and a token budget, asserted by committed tests on the *serialized* projection rather than on the extractor's return value.
- Biggest risk: a memory carries no text, so nothing can be corrected about what was remembered — a wrong memory is a wrong weight, and the repair is decay.
- Most reusable component: `BeliefData` — a five-value status enum where three values are ways of not being believed, a provenance enum running from direct observation to assumption, and two ids giving the belief a why and a why-not for eight bytes.
- Maturity impression: 9,834 lines of xUnit and FsCheck over 16,719 lines of engine, eight ADRs, every NuGet reference exactly pinned and every GitHub action pinned to a commit SHA, with determinism enforced in a workflow of its own — beside an ADR selecting SQLite that the code has not implemented.
- Study when: you assemble context for a model from an internal store and want the boundary between engine state and model-visible state checked rather than assumed.
- Do not copy when: an agent has to be told it was wrong about a fact — there is no fact here to be wrong about, and the store is built so that there could not be.

### [`mimir`](../systems/mimir/)
- Best idea: typed memories, doc chunks and code symbols are rows in one `node` table with a `kind`, so a note about a function and the function itself are ranked against each other in one query instead of merged by a caller afterwards.
- Biggest risk: the normalized content hash that would refuse a returning value is consulted under `AND deleted_at IS NULL`, so a deleted memory does not match its own hash and is re-created on the next restatement.
- Most reusable component: eval fixtures carrying `forbidden_ids` beside `expected_ids`, resolved against a built store — the negative half of a retrieval eval, committed.
- Maturity impression: 32,104 lines of Rust across five crates, published to crates.io, MIT or Apache-2.0, with systemd service and watchdog units in `contrib/` — and the cleanest screen in this atlas: zero auto-run surfaces, zero build-time execution, zero unpinned dependencies, `Cargo.lock` fourteen days cold.
- Study when: you want one local store for everything a coding agent knows, or the cheapest useful answer to a context window about to be cleared — a structured handoff memory written before the clear and restored after it.
- Do not copy when: a correction has to be defensible — supersession and soft delete are both durable and neither records a reason, an actor, or a status.

### [`cognis`](../systems/cognis/)
- Best idea: `fingerprint_policy` — a SHA-256 over the backend id, the resolved behaviour flags, the options and a hash of the instruction text, frozen into a per-turn `MemoryRuntimePolicy` and returned by `audit_metadata()`, so "which memory rules were in force when this happened" is a value to compare rather than a configuration to reconstruct.
- Biggest risk: nothing epistemic crosses the provider boundary — no status, no provenance, no trust — so a backend that models belief has no way to tell the host and the host has no way to ask.
- Most reusable component: a memory contract with `delete_memory` and `delete_memory_tool` as separate methods, `agent_id` and `user_email` on every call, a `null` backend as the copyable template, and a contract test that pins the response shape.
- Maturity impression: 1,495 files and 802 commits under BSL 1.1, controller/executor split with Docker images for both, `uv.lock` twelve days cold — and a contract suite that asserts a JWT subject cannot be overridden by a request header.
- Study when: memory is somebody else's service and your job is deciding when it runs, under which policy, and how to prove afterwards which policy that was.
- Do not copy when: you want memory mechanics — the store is elsewhere, and this repository is the seam rather than the substance.

### [`intaris`](../systems/intaris/)
- Best idea: a durable, versioned behavioural profile of the *agent* — risk level, alerts, summary, keyed on `(user_id, agent_id)` — derived from its own audit history and read back before the next decision. The only memory in this atlas whose subject is the actor rather than the world.
- Biggest risk: the audit rows the profile derives from are updated in place when a human resolves them, so the history being summarised is rewritten after the fact, and the risk level it produces gates behaviour with no path for anyone to dispute it.
- Most reusable component: `precedent.py` — mapping a call into a coarse capability family so one human approval generalises across equivalent low-risk tools *"without turning into blanket approval for all calls to the same tool name"*, with mutating verbs kept out of lookup families.
- Maturity impression: 212 files under BSL 1.1 with a dual-dialect SQLite/Postgres schema, hierarchical sessions with an idle sweep, and one `WHERE` clause that excludes judge-authored decisions from the data it treats as authoritative human guidance.
- Study when: you reuse human approvals and need them to generalise without becoming reflexive, or you want the one worked example here of memory about the actor.
- Do not copy when: the profile must be correctable — nothing disputes it, and only the next analysis can disagree with the last.

### [`brain-md`](../systems/brain-md/)
- Best idea: `update-truth` rewrites a page's compiled truth and appends its timeline entry in one command, so *"a compiled_truth rewrite can never silently skip its timeline entry"* — belief and the reason it changed are one operation rather than a convention.
- Biggest risk: the correct-by-construction guarantee holds only while nobody hand-edits a file, there is deliberately no validator, and the pre-commit hook that would catch it is optional and locates its own CLI by searching four paths.
- Most reusable component: the page format — a current-knowledge section over an append-only timeline typed `decision | evidence | reversal | note` — which drops into any markdown memory without the code.
- Maturity impression: 22 files and 19 commits under Apache-2.0, a 522-line zero-dependency library under 452 lines of tests, six fixed root pages whose history is deliberately git rather than a timeline, and a linter that exempts the append-only layer on stated grounds.
- Study when: you keep project knowledge in the repository and want the reason a belief changed to be structurally inseparable from the change.
- Do not copy when: memory must be searched rather than navigated, several agents write concurrently, or a reversed claim must be unable to return — a reversal is recorded and nothing stops the same truth being compiled back tomorrow.

### [`muninndb`](../systems/muninndb/)
- Best idea: the provenance record — source type, agent id, an operation verb, the caller's stated *reason*, the predecessor id and the valid-time boundary — under a struct comment that names which format changes are additive, that an absent field must read as absent *"never a zero-value pretending to be data"*, and the only two changes that would need a version byte.
- Biggest risk: a provisional patent asserted over the core cognitive primitives beside a BSL 1.1 licence, so the mechanisms are published and readable while their reuse is constrained twice — and the reader has to assess that separately from the engineering.
- Most reusable component: a 64×64 precomputed matrix of contradicting relation types with a severity function, which makes structural contradiction a table lookup rather than a model call.
- Maturity impression: 299,740 lines of Go across 995 files serving MCP, REST, gRPC and a binary protocol from one dependency-free binary, with replication and backup as first-class packages, clock-skew tests beside both the decay and activation suites, and dated design notes in `.claude/deep-review/` arguing the tuning decisions.
- Study when: you want cognitively-motivated decay and activation implemented *in* a store rather than around one, or a retrieval path that is allowed to abstain and is tested as a measured component.
- Do not copy when: you need to build freely on decay, Hebbian learning or Bayesian confidence — read the patent notice first — or you need a value-keyed refusal, which everything here is shaped for and nothing implements.

### [`iai-pme`](../systems/iai-pme/)
- Best idea: a head-to-head against [MemPalace](../systems/mempalace/) run in one harness on identical data, with a matched-embedder row isolating the retrieval design from the embedding model, published as *"an **exact tie** … **No win claimed** — an honest tie is the strong, defensible statement"* — and followed by naming what the benchmark it just used does not measure.
- Biggest risk: no trust state, no provenance and no tombstone, so a wrong memory and a stale one are indistinguishable and the only remedies are fade and re-teach.
- Most reusable component: fade-and-rescue — forgetting is a queued intention with a visible undo window rather than a confirmation dialog, measured at Rescue@10 1.000 with superseded wording still retrievable.
- Maturity impression: 702 test files against 264 source files, a Rust core beside the Python one, AES-256-GCM at rest with no telemetry, committed PyTorch-versus-Rust embedder comparisons with an environment snapshot, and preflight and checkpoint tests around the benchmark runner itself.
- Study when: you want the benchmark posture — one harness, a matched control, a published tie, a stated limitation of the instrument — or an interface where forgetting can be taken back.
- Do not copy when: memory is shared by more than one person; the project says so itself and points elsewhere.

### [`ostk-recall`](../systems/ostk-recall/)

- Best idea: edge conductance derived from confidence and recency rather than stored, so there is no weight to drift and no background pass whose failure freezes the graph.
- Biggest risk: `forget` returns a warning asserting an anti-resurrection tombstone, while the suppression is keyed on the claim id, excluded from conflict detection, and never consulted when the same value is asserted again.
- Most reusable component: the promoted-bridge rule — a latent similarity edge is reified as weak and must earn its conductance through use or decay away.
- Maturity impression: 1,028 test functions over roughly 90,000 lines of Rust with a dense audit surface and receipts on every mutation, self-described pre-alpha, and no committed case asserting that a suppressed claim stays out of a recall result.
- Study when: you want one local binary over your own files and sessions, and the concept ledger rather than the claim table is the part you are shopping for.
- Do not copy when: a correction has to hold against re-extraction — everything else here is careful enough that the gap is easy to miss.

### [`sesa`](../systems/sesa/)

- Best idea: `hurt_count` — a negative usefulness signal written from the same rollout reward that trains the model, and wired to deletion rather than to ranking, so a skill card that keeps losing is removed instead of demoted.
- Biggest risk: eviction leaves nothing behind, and the duplicate check compares only against the live bank, so the next similar failure regenerates the card the system just measured as harmful — at score zero, needing three more losses to go again.
- Most reusable component: the pending-failure priority function, which ranks a failure higher *because* skills were retrieved and it failed anyway, in four lines of arithmetic and no model call.
- Maturity impression: a 617-line research module with no tests of any kind, a batch retrieval function and an anti-leakage parameter that no caller invokes, and no `LICENSE` file at the root — beside a paper ([arXiv:2607.29468](https://arxiv.org/abs/2607.29468)) that describes the mechanism exactly as implemented, ablates it at 2.7 points, and starts from a 157-skill seed bank the two warm-start config keys would load and no file in the tree provides.
- Study when: you have a cheap, automatic, honest outcome signal — a test result, a task reward, a checked answer — and want to see what a memory store can do with one.
- Do not copy when: your outcome signal is user sentiment; `hurt_count` becomes a proxy for irritation and eviction becomes noise amplification.

### [`opensre`](../systems/opensre/)

- Best idea: the grounding gate — an extracted infrastructure or incident memory is refused unless its distinctive tokens also appear in text the user typed, computed without a model, so the agent's own output cannot become the user's durable knowledge.
- Biggest risk: `forget` unlinks the file and records nothing, while extraction re-runs over a thirty-turn window after every turn, so the statement that justified the deleted memory is still in front of the next pass.
- Most reusable component: `core/domain/memory/safety.py` — one regex module that both refuses a credential entry to the store and redacts the transcript before it reaches the extraction provider.
- Maturity impression: Apache-2.0 public alpha, but the memory corner is disciplined — a directory `FileLock` with atomic replace, 0700/0600 with the octal explained, a signature-keyed parse cache, and twenty extraction tests whose useful cases are negative.
- Study when: you run automatic extraction over transcripts that contain your own tool output, your own demo data, or credentials — all three are addressed here and most systems address none.
- Do not copy when: you need to explain why the agent believes something; there is no provenance field, no trust state and no mutation record once the gate has passed.

### [`clawmem`](../systems/clawmem/)

- Best idea: an offline eval with hand-labelled gold that measured the composite ranking stack against the raw channel score, found raw cosine at MRR 0.912 against the composite's 0.307, and shipped the negative result as the default — metadata now breaks exact ties and nothing else.
- Biggest risk: `invalidated_at` is a hard predicate on both retrieval legs with no query-time signal, so a wrong contradiction verdict removes a document from search with nothing to lead a user to look; the project documents this and ships the mechanism disarmed.
- Most reusable component: `resolveEffectiveContradictionPolicy` — twenty lines that downgrade a destructive supersede to a non-destructive link when no audited judge is configured, loudly and with an audit event.
- Maturity impression: 34,000 lines of TypeScript across 55 files, 84 unit test files, a 22-column migration ladder on the central table, four integration surfaces, and committed eval artifacts for three judge configurations.
- Study when: you have built a composite relevance score and never checked it against the raw channel score.
- Do not copy when: you need a memory two people can share — the isolation boundary is "use a different vault file".

### [`memory-palace`](../systems/memory-palace/)

- Best idea: procedural memory that is `draft` until a person approves it, with the default enforced three ways — a validated `review_state` enum, `recommend_for_trigger` returning only `human_reviewed` rows, and `NOT NULL` provenance columns so a bypassing caller cannot write a provenance-less row.
- Biggest risk: the rejection is keyed on the row. `extract_pattern` computes `source_hashes` for every draft and never compares them to rejected rows, so a reviewer's "no" survives exactly until the next extraction over the same sources.
- Most reusable component: `write_guard` — a pre-write duplicate check returning ADD/UPDATE/NOOP that returns `NOOP` with a degradation reason when the embedding provider is untrustworthy, rather than falling through to "not a duplicate".
- Maturity impression: ~98,000 lines of Python, 84 test files, eight migrations each with a paired rollback and a dry-run gate, a React dashboard with a real review surface — and an `access_log` table that is created, indexed, modelled, counted in the UI and written by nothing.
- Study when: derived memory must not reach an agent until a person has seen it.
- Do not copy when: you need multi-tenancy; `domain` is an optional filter and the maintenance API key is an operator boundary, not a user one.

### [`midas`](../systems/midas/)

- Best idea: a deterministic gate on what memory may *authorize* — a provenance vocabulary crossed with an intended-use vocabulary, where an external or destructive action requires `user_confirmation`, a superseded belief cannot justify anything, and a live prohibition vetoes any confirmation in the same evidence set.
- Biggest risk: the gate believes the provenance stamp, and in an MCP deployment the caller writing `user_confirmation` is the agent — the project states this is out of scope for the guard.
- Most reusable component: `eval/memory_safety.py` — ten adversarial cases plus four benign controls, scored as attack-success rate *and* benign-pass rate together so that blocking everything cannot look safe.
- Maturity impression: ~18,700 lines of Python with 58 test files, a TypeScript port, a hash-chained audit log with a verifier, and a benchmark document that publishes five experiments which did not help.
- Study when: an agent can take an irreversible action and your memory currently has no say in whether it may.
- Do not copy when: you need whole-conversation summarisation — it is listed as out of scope by design, and measured.

### [`yesmem`](../systems/yesmem/)

- Best idea: supersession resistance graded by a trust score computed from use count, stated source and importance, so a user-stated learning the agent has relied on forty times is not silently overwritten by one LLM extraction.
- Biggest risk: the confirmation that gate depends on does not exist. `supersede_status = 'pending_confirmation'` is written at two sites and read by nothing — no query, no CLI command, no tool, no clear — so the highest-trust learnings are the only ones whose corrections are discarded.
- Most reusable component: `quarantine_session` — one statement that removes an entire noisy session's learnings from vector search, BM25, associations and embedding refresh, reversibly.
- Maturity impression: ~188,000 lines of Go with 355 test files and a LoCoMo run against a community-corrected dataset that also publishes the non-agentic score — beside a 55-column memory table carrying two more mechanisms wired in one direction only.
- Study when: you want correction to cost more for memories that have earned trust, and you will finish the loop.
- Do not copy when: you need memory that is current within the session; extraction is asynchronous and the briefing shows the state as of the last pass.

### [`memory-lancedb-pro`](../systems/memory-lancedb-pro/)

- Best idea: `fact_key` — correction keyed on what a memory is *about*, derived from category plus text when the extractor does not supply one, with a scoped collision scan that supersedes the previous value instead of accumulating statements.
- Biggest risk: the `pending` state was written out of existence. Four extractor sites set `state: "confirmed"` with the comment "write confirmed to unblock auto-recall", so an LLM admission score is the only filter, and a rejected candidate leaves no record to be judged against next time.
- Most reusable component: `computeTier1Patch` — three unconfirmed injections suppress a memory from auto-recall for thirty minutes, and a day without an injection resets the counter, in three integers and no model call.
- Maturity impression: ~39,700 lines of TypeScript with 171 test files often named after the bug they pin, an unusually strict scope filter that denies null-scope rows — and no committed benchmark, no evaluation harness, and no LICENSE file despite an MIT badge.
- Study when: your memory is facts about subjects rather than documents, and you want updates to replace rather than pile up.
- Do not copy when: you need to know whether the ranking works; nothing here is measured.

### [`wenlan`](../systems/wenlan/)

- Best idea: a dismissed mind-map node keeps its row, so its derived fingerprint stays occupied under `UNIQUE(page_id, fingerprint)` and `ON CONFLICT DO NOTHING` makes every re-proposal a no-op — with the suggestion path a separate, insert-only accessor that "can never modify, resurrect, or overwrite a pinned/active/dismissed row".
- Biggest risk: that guarantee covers graph placement, not facts. Nothing stops the underlying claim being re-stored, and the page changelog that looks like a mutation history is a 20-entry FIFO.
- Most reusable component: `drift_guard.rs` — test-only teeth that parse the source with `syn` and fail CI on a documented-but-unwired flag or a duplicated definition, which is the exact class of defect several reports in this atlas exist to report.
- Maturity impression: 485,000 lines of Rust across five crates, Apache-2.0, a thirty-module evaluation subsystem with ranking goldens, and a committed benchmark table introduced by "This is a retrieval-only snapshot, not a claim about end-to-end answer quality."
- Study when: you need a rejected suggestion to stay rejected and want to see it done with a database constraint instead of a policy.
- Do not copy when: you want a component — this is a product with a desktop app, and the transferable part is 900 lines of `page_map.rs`.

### [`kage`](../systems/kage/)

- Best idea: staleness computed against per-symbol content hashes, resolved by name rather than by line, so moving a function does not invalidate a memory about it and an edit elsewhere in the same file does not either.
- Biggest risk: `scope` and `visibility` are stored with validated vocabularies and no read path compares against either — the isolation that exists comes from three separate directories, so a refactor merging the loaders would remove it without touching the field.
- Most reusable component: `benchmarkTrust` Gate 2 — write memories grounded in real files, confirm each is recallable, delete the files, assert each is gone, counting only the ones that were recallable first.
- Maturity impression: 108,000 lines of TypeScript on Google's Open Knowledge Format, GPL-3.0, 299 test declarations in one file, sixteen benchmark harnesses with no committed results — and an org audit log that is three functions with zero call sites.
- Study when: your memories are claims about code and you want a freshness verdict with no model in the path.
- Do not copy when: your memory is about people; there is nothing to hash.

### [`icarus`](../systems/icarus/)

- Best idea: `verified` and `lifecycle` as separate fields with the reasoning in a comment — "verified is about provenance/trust, lifecycle is about freshness … so callers can combine them without overloading either" — backed by a legal-transition table in which `rolled_back` is terminal.
- Biggest risk: `verify(entry_id, verifier="manual")` takes an unvalidated string and is exposed as an MCP tool, so the agent that wrote an entry can verify it and record "manual" doing so.
- Most reusable component: `test_taint_safe_retrieval.py` — four statuses seeded, the default search asserted to return exactly the safe set, and `audit_search` asserted to return everything.
- Maturity impression: 3,000 lines of Python with 23 test files named after invariants rather than modules, Pydantic `extra="forbid"` on every model, and a README that says "PyPI release pending".
- Study when: you want a correctness-first memory small enough to read end to end and formal enough to reason about.
- Do not copy when: you need retrieval quality or tenancy; there is no benchmark and `project_id` is an optional filter.

### [`omega-memory`](../systems/omega-memory/)

- Best idea: a genuine point-in-time filter — one batched negative query removing every candidate whose `valid_from` is after or `valid_until` at or before the requested instant — paired with a supersede that writes the validity bound and the status in the same statement.
- Biggest risk: `flagged_for_review` is set when the feedback score reaches −3 and nothing in the tree ever clears it, so a memory that later collects helpful ratings stays permanently invisible, because the retrieval filter tests the sticky flag rather than the score.
- Most reusable component: `forgetting_log` — an append-only deletion record with a reason vocabulary, indexed on reason and time, exposed to the agent as a queryable tool.
- Maturity impression: 17,300 lines of Python, Apache-2.0, 70 test files, a dead-letter queue for failed maintenance — and two self-reported LongMemEval figures inside one commit, 95.4% in `CITATION.cff` and 76.8% in the benchmark report, with no result artifact for either.
- Study when: you want the forgetting side of memory worked out — reasons, decay, dedup, delete propagation to a cloud copy.
- Do not copy when: you will act on the published numbers; the two in this repository disagree by 18.6 points.

### [`octopoda-os`](../systems/octopoda-os/)

- Best idea: tenant isolation as a Postgres row-level-security policy with both `USING` and `WITH CHECK` on five tables under a dedicated application role, so a query that forgets the predicate returns nothing rather than everything.
- Biggest risk: every update closes a version and inserts a new row, and no read path anywhere queries a point in time — a full history is written and nothing can ask for it, while the ephemeral write path deletes every version of a key.
- Most reusable component: `audit_v2/storage.py` — a per-tenant, per-agent SHA-256 chain over `(prev_hash + canonical event)`, living inside the memory table for the stated reason that the app role has no `CREATE TABLE` right.
- Maturity impression: 42,000 lines of Python with 32 test files including end-to-end tenant isolation, two CI workflows — and a split licence where the default native engine is proprietary, downloaded from another repository, and absent from the tree.
- Study when: you run many agents for many tenants and want the isolation enforced below the application.
- Do not copy when: you need to read or change how retrieval works at the default backend, or you need correction semantics of any kind.

### [`vestige`](../systems/vestige/)

- Best idea: Fellegi-Sunter record linkage classifying every merge candidate as `match`, `possible` or `non_match`, with the two uncertain classes requiring an explicit `confirm=true` — the header's argument being that a single cosine threshold "over-merges and destroys the audit trail".
- Biggest risk: the headline benchmark lives on a different branch, so none of Silent Rotation's numbers — 20/23 converged correct against 0/25 with no memory — can be checked at the pinned commit.
- Most reusable component: `merge_operations`, described in its own migration as "the git reflog for your agent's memory", where `undo_payload` carries everything needed to reverse an applied merge and `signals` records why the memories combined.
- Maturity impression: 97,000 lines of Rust in a 25MB single binary, AGPL-3.0, 1,088 test functions, twenty-five-plus tables — and a deprecated table labelled in the schema as "designed for bi-temporal edge support but was never wired … Do NOT add queries against this table", which is the correct handling of a defect four other systems here ship silently.
- Study when: your automatic merge or supersede has one similarity threshold and you have never asked what it does at the boundary.
- Do not copy when: more than one person will use the store; there is no scope beyond tags.

### [`shodh-memory`](../systems/shodh-memory/)

- Best idea: `docs/graph-construction-audit.md` — a 677-line self-audit whose evidence rules are this atlas's own ("Doc comments in this codebase are frequently stale, so nothing here rests on one"), every claim carrying a `file:line`, finding a resolver with zero production callers, a header contradicting its own code, and a PMI gate the upsert path voids entirely.
- Biggest risk: those findings are real and unfixed at this commit — the co-activation layer "returns 0 for every call" by default, typing is skipped silently under lock contention, and the audit's own section 2.6 is titled "The read path filters nothing".
- Most reusable component: `src/decay.rs` — exponential decay for the first three days and power-law after, with the cliff that pure exponential produces written out in numbers.
- Maturity impression: 153,000 lines of Rust with no LLM anywhere, published to four registries, an in-tree recall harness with NDCG/MRR/MAP and dedicated forgetting, lineage and multi-hop suites — and no committed benchmark result.
- Study when: you want an associative memory with zero inference cost, or you want to see what a project auditing itself to this standard produces.
- Do not copy when: you need correction semantics — a wrong memory here fades if nothing reinforces it and strengthens if something does.

### [`token-savior`](../systems/token-savior/)

- Best idea: `was_visible` on every ledger event, which separates "the memory was injected and ignored" from "the memory was never injected" — opposite evidence about the ranker that almost every feedback loop in this atlas folds together.
- Biggest risk: the LinUCB weights persist to `linucb_model.json` with no versioning against the `FEATURE_NAMES` tuple they were trained on, so changing the feature vector silently reinterprets a trained model.
- Most reusable component: `linucb_injector.py` — a ten-feature contextual bandit deciding which memory to inject, with a Gauss-Jordan inverse in pure Python and no numpy.
- Maturity impression: 32,600 lines of Python with 173 test files, a Beta-distributed validity score with quarantine and stale-suspected thresholds, and freshness checked by shelling out to `git log -S` — with the headline tsbench number in a separate repository.
- Study when: you inject memory automatically and have no way to tell whether it helped.
- Do not copy when: you need the benchmark claim verified; it is not in this tree.

### [`recall-substrate`](../systems/recall-substrate/)

- Best idea: per-actor Brier calibration — an actor's stated confidence scored against whether their writes survived or were contradicted, folded into a `[0.5, 1]` multiplier on everything they write afterwards. Every other system here weights by *what kind* of source a memory came from; this one weights by how well-calibrated that writer has actually been.
- Biggest risk: `requiresReview` is validated, rendered, expanded in the compiled context and emitted as a `review_required` marker — and set to `true` only in three test files, so the context advertises a state the system cannot enter.
- Most reusable component: `lastSalientAt` kept distinct from `updatedAt`, so "a read reinforces attention without refreshing freshness" — a one-field fix for a bug most stores in this atlas have.
- Maturity impression: 13,200 lines of TypeScript with a `.test.ts` beside every single source module, an eight-pattern credential firewall that reclassifies rather than rejects, and an agent-integrity gate that holds the turn open until memory was consulted.
- Study when: multiple writers of differing reliability write to one store and you weight them by a fixed constant.
- Do not copy when: you need a curation surface — the README says there is nothing for a human to curate, and the code agrees.

### [`core-redplanet`](../systems/core-redplanet/)

- Best idea: splitting statement storage on whether the fact decomposes — `Identity`/`Knowledge`/`Event` become subject-predicate-object triples, while `Directive`/`Preference`/`Belief` stay whole "since they carry meaning that does not decompose cleanly into triples". Triple-ifying a preference throws away the phrasing that carries its force.
- Biggest risk: an invalidated statement can be re-extracted from a new episode and become current again — correct for a memory over the user's own mail, and the wrong default for anything an agent writes.
- Most reusable component: `invalidatedBy` beside `invalidAt`, which names the statement that ended this one and turns a set of timestamped rows into a walkable history.
- Maturity impression: 152,800 lines across a monorepo with forty-plus connectors, a pluggable graph provider behind a three-value enum, six vector namespaces and nine pages of accurate documentation — beside 25 test files, AGPL-3.0 with a Commons Clause, and a LoCoMo number published in a different repository.
- Study when: your memory holds both facts and directives and you are storing them the same way.
- Do not copy when: you need lexical retrieval; V2 dropped BM25 and the pipeline that has it is version-gated.

### [`yantrikdb`](../systems/yantrikdb/)

- Best idea: `CORRECTIONS.md` — four published benchmark conclusions withdrawn because the condition labelled "structured memory" was a 120-line Python dict with word-overlap retrieval, with the maintainer's own words quoted ("the core functionality did not run at all") and the four-word reply "Correct observation. No defense." The correction was published before the favourable rerun was finished.
- Biggest risk: the crypto-shred erasure path is an orchestrator with no caller, no encryption layer beneath it and no admin endpoint — stated in its own header under "What's NOT here (deferred)", so the GDPR story at this commit rests on logical tombstones alone.
- Most reusable component: `commit/retention.rs` — restore-no-resurrect, where a tombstone stays in the log until every replica watermark has passed it, so a restore cannot bring a deleted memory back.
- Maturity impression: 63,000 lines of Rust across six crates, AGPL-3.0, every mutation through one commit substrate idempotent on `op_id` with per-tenant log indices, and a rerun harness committed with raw logs at n=2.
- Study when: your deletion story stops at the primary and you have replicas or backups.
- Do not copy when: you want cognition — `certainty` and `valence` here are fields, not mechanisms.

### [`vibe-cognition`](../systems/vibe-cognition/)

- Best idea: journal-first — every mutation is appended to `journal.jsonl` before the in-memory graph is touched, so the graph and the embeddings are both projections and a crash between the two loses nothing.
- Biggest risk: the ChromaDB sync "only ADDS" and a removed node "is NEVER un-embedded", so the vector store accumulates orphans that anything querying it directly would surface.
- Most reusable component: the tombstone line itself — `{"id": ..., "removed_by": ...}` where `removed_by` is a git identity or a surface tag, with the dashboard documenting why it passes `"dashboard"` rather than a person.
- Maturity impression: 56,000 lines of Python with 58 test files, twelve node types each declaring its own update semantics in the enum comments, and multi-process replay bugs explained in paragraph-length comments at the fix.
- Study when: you want the log-and-projection shape implemented small enough to read in an afternoon.
- Do not copy when: you need a measurement — there is no benchmark of any kind.

### [`gbrain`](../systems/gbrain/)

- Best idea: claims typed by commitment — `fact | take | bet | hunch` — where only a bet resolves, and the resolved outcomes become a per-holder Brier score with bias tags like `over-confident-geography` that feed contradiction handling.
- Biggest risk: `since_date` and `until_date` are both written on every insert and the range query compares `since_date` at both ends, so a window returns claims that *began* in it rather than claims that were *true* during it.
- Most reusable component: `destructive-guard.ts` — impact preview, typed confirmation, 72-hour recoverable tombstone, under the principle that "the blast radius should be visible BEFORE you pull the trigger, and recoverable AFTER".
- Maturity impression: 564,000 lines of TypeScript with 1,005 test files, a fuzz suite, CI guards that state which way they should fail, and `grade_completion` recording when a calibration profile was computed from partial input — with the BrainBench numbers in a sibling repository.
- Study when: several people write claims into one store and you weight them all the same.
- Do not copy when: you need the temporal window to mean what it says.

### [`superlocalmemory`](../systems/superlocalmemory/)

- Best idea: the audit chain runs on its own sqlite connection, "not shared DB manager — for independence — audit must survive even if the main DB is corrupted". Every other hash-chained log in this atlas shares a fate with the store it audits.
- Biggest risk: ABAC defaults to allow-all with a deny-list, so an unconfigured deployment of a system sold on governance has no access control at all.
- Most reusable component: `compliance/retention.py` — named rules bound to a profile, tagged by framework, with three actions where `notify` deliberately changes nothing and only surfaces the count.
- Maturity impression: 399,000 lines of Python across twenty-eight subpackages with nine framework integration packages, AGPL-3.0 — and an EU AI Act module whose docstring refuses to certify compliance, plus four temporal columns no read path filters on.
- Study when: you have a compliance obligation and need the audit trail to survive the incident it is evidence about.
- Do not copy when: you want a small component; the surface is the largest here relative to what one user needs.

### [`nornicdb`](../systems/nornicdb/)

- Best idea: `ConstraintTemporal` — validity declared as a schema constraint over `(key, valid_from, valid_to)` and enforced at write time, so a node cannot claim a temporal label without the fields. Everywhere else in this atlas validity is a convention two queries must remember to share.
- Biggest risk: "search remains current-state focused: current search paths are intentionally separate from historical MVCC state" — the constraint, the temporal index and the MVCC reads all exist, and the retrieval path a memory client uses reaches none of them.
- Most reusable component: `kalman_anti_sycophancy_test.go` and the filter behind it — fifty measurements of 0.6, one 0.99 asserted to stay under 0.8, then recovery, so an agent agreeing enthusiastically with itself cannot ratchet a confidence score.
- Maturity impression: 780,000 lines of Go with forty-plus packages, MVCC snapshot isolation, Bolt/Cypher/gRPC/GraphQL/Qdrant/MCP surfaces, and an audit module citing GDPR, HIPAA, FISMA, SOC2 and SOX by clause rather than by name.
- Study when: you are building the memory layer and want validity enforceable and history queryable underneath it.
- Do not copy when: you expected a memory product — nothing here decides what to remember or resolves a contradiction.

### [`empirica`](../systems/empirica/)

- Best idea: a closed resolution vocabulary — `stale | superseded | retracted | mistyped` — designed from a measurement of the project's own store, where 1,267 of 1,268 resolutions expressed staleness and exactly one an error. The module argues that a 1-in-4199 error rate over six months "is not plausible, so errors were not being expressed rather than not occurring", and states the principle: "What the surface does not name, the practitioner does not reach for."
- Biggest risk: the source tagging that would catch a gamed confidence vector — high `know` while every artifact is `intuition` — is declared v0 with the routing rule deferred, so the gaming surface it names is not closed at this commit.
- Most reusable component: `empirica/data/resolution_kind.py` — one file holding a vocabulary, the measurement that justified it, the pre-empted rebuttal, and a normaliser that refuses to coerce an unknown value because that would manufacture the exact error being measured.
- Maturity impression: 303,000 lines of Python with 431 test files, a Sentinel gate that blocks edits until understanding is demonstrated, a `mistakes_made` table whose columns are `why_wrong`/`cost_estimate`/`root_cause_vector`/`prevention`, and `project_unknowns` as first-class rows.
- Study when: your correction path has one word for "not current" and you have never asked what it is hiding.
- Do not copy when: you need retrieval — recall here is decay-weighted bootstrap, and no retrieval quality is claimed or measured.

### [`hexis`](../systems/hexis/)

- Best idea: a `CONTESTED_BECAUSE` edge, and a reconsolidation sweep that reads it. When a worldview belief transforms, the service re-evaluates memories "rejected because of old belief, may now accept" — the only correction mechanism in this atlas that goes backwards and asks what a superseded belief had been suppressing.
- Biggest risk: that sweep's verdict is an LLM call over batches of eight, defensively parsed and never validated against evidence, and the review surface that exists for claims does not cover it.
- Most reusable component: `user_model_claims` — `status` (`active|superseded|rejected`) and `review_status` (`pending_review|approved|rejected|superseded`) as separate CHECK-constrained columns, so the system's position and a person's verdict never overwrite each other, with `(review_status, updated_at DESC)` indexed so the queue is a query.
- Maturity impression: 182,000 lines with the memory model implemented as eighty-plus numbered Postgres function files, one table per graph edge type, a review-event log carrying `prior_status` and a `restore` decision — and a repository file called `why_i_suck_and_how_to_fix_it.md`.
- Study when: your corrections only move forward and you have never asked what a retired belief was blocking.
- Do not copy when: you need the sweep's judgement to be checkable; nothing measures it.

### [`noosphere`](../systems/noosphere/)

- Best idea: the eleventh tombstone in this atlas and the most rigorous. A revoked capture is refused on the write path — inside a serializable transaction, after the lineage rows are locked — by matching an HMAC digest against every *retained key version*, so rotating the HMAC key cannot resurrect a revocation. No other rejected-value record here reasons about the key used to compute its own key.
- Biggest risk: the tombstone carries a ninety-day TTL by design, bounding the keyring. The refusal is durable for a window, not forever, and a reader wanting "never again" needs an unbounded tier beside it.
- Most reusable component: the three independent upserts on revocation — a tombstone that blocks re-entry, a privacy-review row for a person, and a durable cleanup job under an idempotency key — none depending on the others succeeding.
- Maturity impression: 68,000 lines of TypeScript on Postgres through Prisma, with `capture-race-integration.test.ts` written because the check and the insert must be correct under concurrency, an `embedding_consent` table, and `RestrictedScope` as a deletable row with its own revocation reason.
- Study when: a deletion in your system has to actually stick.
- Do not copy when: you need permanence; ninety days is the guarantee.

### [`cortexgraph`](../systems/cortexgraph/)

- Best idea: forgetting as the default — strength starts at 1.0, decays from `last_used` on an Ebbinghaus curve, and only use reinforces it, so an unused memory costs nothing to keep because it will not be kept.
- Biggest risk: `LICENSE` is AGPL-3.0 and `CITATION.cff` says MIT. Those cannot both be right, and the citation file is what automated tooling reads.
- Most reusable component: `cross_domain_count` — one integer counting how many distinct domains a memory has been useful in, which separates a narrow fact from a general principle better than an importance score does.
- Maturity impression: 53,000 lines with 70 test files including a named storage-parity suite, an SBOM workflow and a security-scanning workflow — and a committed design spec arguing against its own append-only log because "the data structure is fighting the biological model", still marked Proposed.
- Study when: you want the log-versus-directory argument made concretely, by a project that hit the sync failure that motivates it.
- Do not copy when: a wrong memory must be retractable rather than left to fade; decay cannot tell false from unused.

### [`virtual-context`](../systems/virtual-context/)

- Best idea: a tag vocabulary that reorganises itself without breaking what was written against the old shape — a feedback loop that makes the tagger reuse `storage` rather than invent `data-persistence`, a splitter that breaks up a tag grown too broad, and `tag_aliases` mapping the old name to the canonical one so existing queries still resolve.
- Biggest risk: tagging, convergence, splitting, summarising and supersession are five model-driven judgements measured by one end-to-end accuracy number, and the aliases that make a bad split harmless to queries also make it invisible.
- Most reusable component: `tag_summaries` with `covers_through_turn` plus enumerated `source_segment_refs` and `source_turn_numbers` — a rolling summary that records exactly which material it covers and where it stops, which is how incremental summarisation avoids double-counting.
- Maturity impression: 257,000 lines of Python deployed as a proxy so an existing agent needs no changes, AGPL-3.0 with a commercial contact, benchmark harnesses for five suites committed in-tree, and a LongMemEval run reporting its seeds, all three model roles and a per-category breakdown.
- Study when: you let a model invent tags and your vocabulary has started to sprawl.
- Do not copy when: you need memory you can defend — correction is a mark on a contradicted fact, and there is no trust state or review.

### [`memorybear`](../systems/memorybear/)

- Best idea: forgetting that fuses rather than deletes. Low-activation Statement–Entity pairs merge into a `MemorySummary`, inbound edges are rerouted to it with `MERGE (source)-[:DERIVED_FROM]->(ms)`, and the original node ids are kept — so "what happened to this fact" stays answerable after the fact is gone.
- Biggest risk: every published benchmark figure, error bars included, exists only inside a PNG in the README. No harness, no result file, no dataset reference, no run configuration — unlike the systems whose numbers live in a sibling repository, there is nowhere for a reader to go.
- Most reusable component: `forgetting_cycle_history` — per run and per user, `merged_count` beside `failed_count`, the average activation value, the duration and whether the run was manual or scheduled. A background pass that counts what it could *not* do.
- Maturity impression: 410,000 lines across an API, a console and sandbox infrastructure on Neo4j plus Postgres, a real ACT-R activation model with Anderson (2007) cited and the formula written out, `end_user_id` on every node and relationship — beside 14 test files and a `DETACH DELETE` that interpolates the user id into Cypher instead of binding it.
- Study when: your decay model deletes, and you would rather it compressed with a pointer back.
- Do not copy when: you need correction — a wrong memory that is frequently retrieved is reinforced by the same mechanism that keeps a right one.

### [`jumbo`](../systems/jumbo/)

- Best idea: full event sourcing done plainly — one JSON file per event in a per-aggregate stream directory, zero-padded sequence and event type in the filename, written to a temp path and renamed so an interrupted or concurrent write cannot corrupt it. Every table in the database is named `*_views`, so a reader can see at a glance that nothing in it is authoritative.
- Biggest risk: `BaseEvent` declares `loggedBy?: "human" | "machine"` and a search of the whole tree returns exactly one line — the declaration. In a system whose entire value is a trustworthy history, the field that would separate a person's decision from an agent's is never set.
- Most reusable component: the goal state machine's small guards — `reviewIssues` cleared on resubmission so a stale rejection cannot outlive the thing it was about, and `lastWaitingStatus` so unblocking returns to the real prior state rather than a default.
- Maturity impression: 150,000 lines of TypeScript with 587 test files, twelve domain aggregates each with an event index, layered domain/application/infrastructure separation, and `StoredEvent` explicitly confined to the infrastructure layer.
- Study when: you want the log-and-projection shape with nothing mutable left to compromise it.
- Do not copy when: you need to know who wrote a memory — the log answers what and when, and never who.

### [`neuroca`](../systems/neuroca/)

- Best idea: a five-value status vocabulary that distinguishes `consolidated` ("moved to a higher tier") from `archived` ("no longer active but preserved") and makes `forgotten` — "marked for deletion but not yet removed" — an explicit intermediate rather than an implied one.
- Biggest risk: at this commit no integration test exercises the memory system against a durable backend. Two suites carry `pytest.skip(..., allow_module_level=True)` with the reason "These tests use the old memory architecture and need to be refactored", and the third skips Redis by default and SQLite for "thread safety and initialization".
- Most reusable component: `consolidated_from` and `consolidated_at` on the memory metadata, so a promoted memory is traceable rather than an unexplained appearance in a higher tier.
- Maturity impression: 134,000 lines with three tiers over pluggable backends, a lymphatic consolidator, an annealing optimizer and Hebbian tubule weights — beside 21 test files, three unit skips reasoned "implementation varies across backends", and an Agno comparison hosted in a separate repository.
- Study when: you want the status vocabulary and the consolidation provenance fields, both of which are independent of the refactor.
- Do not copy when: now — the architecture is legible and its coverage against a durable backend is zero by the project's own markers.

### [`athena`](../systems/athena/)

- Best idea: a README section titled "What's Proven vs. What's Proposed" that grades six layers from shipped to "partially unfalsifiable — by nature", including the row where the project names the literature predicting its own failure — user-memory profiles raise agreement sycophancy 45% on Gemini 2.5 Pro — and then writes "Athena is *built on* that mechanism". No other system in this atlas cites the paper against itself.
- Biggest risk: the anti-self-mythologizing convention it defines — every mechanism labelled `code-enforced`, `agent-discretion` or `aspirational` — is applied inline in about eight files out of 569, with the `epistemic_status:` frontmatter key used nowhere. The rule says "tag on touch"; at this commit the tagged set is roughly the documents about tagging.
- Most reusable component: `audit_staleness.py`, which flags a reference written *before* the file it points at was last modified — freshness applied to citations rather than to content, using git timestamps.
- Maturity impression: 60,000 lines of Python over 569 Markdown files, a regex anti-sycophancy classifier that cannot itself be flattered, auditors for staleness and coverage — and an explicit N=1 admission: "this worked for one person who built it around his own thinking — you are the replication experiment".
- Study when: you are about to describe a mechanism in the present tense and are not sure any code implements it.
- Do not copy when: you need the governance to travel — the one code-enforced safeguard is a Claude Code hook, and the project says so.

### [`mem9`](../systems/mem9/)

- Best idea: `e2e/crdt-e2e-tests.sh` asks the three right questions about what "deleted" means under concurrency — delete is invisible to reads, repeated delete is idempotent, and a causally-dominating write *revives* the tombstone. It is the opposite position from Noosphere's refusal and YantrikDB's restore-no-resurrect, argued deliberately.
- Biggest risk: none of it is in the published server. `clock`, `write_id`, `tombstone`, `space_token` and `/api/spaces` appear in no Go, TypeScript or SQL file in the repository. A committed suite is normally the most trustworthy documentation a repo has; this one specifies code that is not here, so the multi-agent convergence story cannot be assessed from this tree.
- Most reusable component: a `paused` state beside `active`, `archived` and `deleted` — withheld from recall without being archived, which is what a user actually wants when a memory is wrong *for now*.
- Maturity impression: 154,000 lines with three storage backends behind one repository interface and three schemas maintained side by side, nine indexes on identity and lifecycle, signed webhooks and a transactional usage outbox — and 110 test files, one of which tests a different system.
- Study when: your store has more than one writer and you have never written down what deletion means.
- Do not copy when: you need one state to cover both "superseded" and "withdrawn" — they have opposite requirements, and this design has one value for both.

### [`aurora`](../systems/aurora/)

- Best idea: verification is phase four of nine, ahead of Route, Collect and Synthesize — the query decomposition is checked before any agent is dispatched, with `SELF` and `ADVERSARIAL` as an option on the same function selecting different prompt templates. Gating the expensive path, applied to planning rather than storage.
- Biggest risk: the README documents a retrieval-quality gate in detail — NONE/WEAK/GOOD on groundedness ≥ 0.7 and three chunks, with a sample warning — and its example calls `verify_decomposition` with `interactive_mode` and `retrieval_context`, neither of which is in the signature, and names the option parameter wrongly. The example as written raises.
- Most reusable component: the four-column `activations` table — `chunk_id`, `base_level`, `last_access`, `access_count` — kept separate from the chunk row so the hot-path write stays small, with the pipeline's `Record` phase doing the reinforcement so it cannot be forgotten.
- Maturity impression: 145,000 lines across twelve packages with strict tooling, 153 test files, SQLite in WAL mode with schema-version detection tested against a deliberately legacy table, and a committed performance baseline file.
- Study when: your agent plans multi-step work and you dispatch before checking the plan.
- Do not copy when: you expected a memory system in this atlas's usual sense — nothing here is believed, corrected or forgotten, because the codebase is the truth.

### [`aipass`](../systems/aipass/)

- Best idea: `should_surface()` budgets how often memory may speak — a relevance threshold *plus* `max_surfaces_per_session`, `min_messages_between` and `cooldown_seconds`, evaluated as a pure function returning `(bool, reason, new_state)`. A memory can clear the threshold and still be refused because it spoke too recently, and the refusal comes with its reason.
- Biggest risk: the symbolic deduplicator implements "the AUDN (Add/Update/Delete/Noop) deduplication pattern" and "decides the correct action via LLM" — one model deleting fragments extracted by another, with nothing found that gates the verdict, records what went, or keeps it.
- Most reusable component: entry limits as configuration — a per-type character cap with per-branch overrides deep-merged, a pure `check_entry()` validator, a read-only `lint` that audits violations, and `rollover check` as a dry run before `rollover run`. Memory growth stated as a contract and audited separately from being enforced.
- Maturity impression: a ~377,000-line monorepo with nineteen subsystems of which memory is ~38,500 lines, 446 test files, codecov, a `Dockerfile.test` and OpenSSF badges — and five surfacing constants (0.3, 5, 10, 300) with nothing in the tree measuring them.
- Study when: your agent injects everything that passes a similarity cutoff and you have never asked how often it should interrupt.
- Do not copy when: you need the memory module alone — it is bound to branches, drones and templates, and the governance state resets to zero on every `new_state()`.

### [`claude-total-memory`](../systems/claude-total-memory/)

- Best idea: a deliberate second retrieval against an *inverted* query — one phrased to surface facts that would contradict the likely answer — scored pairwise, where a max above 0.60 makes the question unanswerable and the router emits IDK rather than picking a side. Retrieval for the refutation, with the refutation allowed to win.
- Biggest risk: the badge and the headline read "+10.8 pp over Supermemory's published 85.4%", subtracting this project's `recall_any@5` from another project's overall figure; the footnote beneath it gives the strict `recall_all@5` as 84.5%, which is below the number being beaten.
- Most reusable component: `content_filter.py` — a declarative per-tool-output filter where `safety = "strict"` extracts URLs, absolute paths and code spans *before* filtering and re-appends anything the rules dropped, so aggressive compression cannot eat the tokens that matter, and every rule declares an `on_empty` string so filtering to nothing says something.
- Maturity impression: 68,000 lines, 150 test files, an append-only `fact_assertions` log with a real as-of query, a layer wall enforced by a test, and dated benchmark result JSONs committed with dataset source, run date, `k` and the count of questions skipped with the reason.
- Study when: your retriever returns what matches the question and you have no way to notice the contradicting fact one sentence away.
- Do not copy when: you need abstention measured — the mechanism targets it and the benchmark excludes abstention questions.

### [`omnimemory`](../systems/omnimemory/)

- Best idea: a default-deny AST gate that tests its own checker — six positive and negative controls added after "a verifier demonstrated the `apply_instance_discriminator` laundering hole live" — on the stated principle that a gate whose discrimination is never exercised is indistinguishable from a gate that always passes. Beside it, a test that asserts in executable form what the suite does *not* prove.
- Biggest risk: `create_lifecycle_dispatch_handler` returns the no-op handler, which logs and acknowledges `expire-memory` and `archive-memory` commands without acting; its docstring records that it "previously" raised `RuntimeError` and was changed so upstream commands are "gracefully acknowledged instead of crashing the service". The crash was information.
- Most reusable component: the expire SQL — `WHERE id = ? AND lifecycle_revision = ? AND lifecycle_state = 'active'`, `rows_affected == 0` reported as a conflict, and a comment explaining why EXPIRED is excluded from the retry's valid source states. Optimistic concurrency and an illegal-transition guard in one statement.
- Maturity impression: 119,000 lines, mypy strict, Pydantic throughout, a frozen five-state transition map with DELETED terminal — and a fully specified audit model with no constructor anywhere in `src`, a trust enum derived from a float by threshold, and `OMNIMEMORY_USE_STUB_HANDLERS` defaulting to `"true"`.
- Study when: you assert an invariant in CI and have never proved the assertion fails when violated.
- Do not copy when: you want a memory system to adopt — this is a platform domain package, and the lifecycle it specifies is not running.

### [`wax`](../systems/wax/)

- Best idea: a crash harness that forks a child, sets `WAX_CRASH_INJECT_CHECKPOINT` to a named point in the commit sequence, SIGKILLs it, reopens the `.wax` file and asserts the exact committed frame count *and* both frames' bytes — with `childDidNotCrash` as a failure and an exit code on the child's fall-through, so the test fails closed at both ends.
- Biggest risk: `memory_promote` defaults `approve` to `false` and returns a proposal; `promote`, the alias on the same command surface with the same parameters, sets it to `true` when absent. One name asks, the other acts.
- Most reusable component: promotion as a proposal — suggested type and durability, confidence, recall count, unique query count, the reasons, and duplicate matches with similarity scores, returned without writing, with `.promotionReviewed` and `.promotionWritten` as distinct session events carrying `approved` and `written` separately.
- Maturity impression: 97,000 lines of Swift across thirteen targets with its own single-file format — double-buffered headers, TOC, footer, WAL ring — 173 test files, CoreML embedding models, and a durable-write guard that refuses private keys, AWS keys, GitHub PATs and Slack tokens by name.
- Study when: you wrote your own storage format and your durability evidence is that it reopens.
- Do not copy when: you need scope to isolate — repo and project add 0.9 and 0.7 to the score and remove nothing, and expiry is enforced as a −10 sentinel against a −9.5 guard.

### [`truememory`](../systems/truememory/)

- Best idea: benchmark reporting as it should be done — a nine-system LoCoMo leaderboard with a rival ranked first, the caveat that would have cost the rival that place printed under the table anyway, the rubric's leniency and its incomparability to published baselines stated, three-run means with the individual runs shown, competitors run in-house with their result files committed, and BEAM's worst category published at 19.5% in the same table as its best at 97.1%.
- Biggest risk: contradictions are found by regex over message text and `build_contradictions` runs `DELETE FROM fact_timeline` before reinserting, so a correction phrased outside the pattern set never enters the timeline, `superseded_by` points at IDs that change every pass, and a retracted fact is re-derived from the same message on the next run.
- Most reusable component: `tests/test_issue_637_directive_leaks.py` — directives were excluded from core search and leaked through five named supplement paths, and the fix is an exclusion test per leg, each paired with its `include_directives=True` counterpart. An exclusion invariant tested on every path that bypasses the filter.
- Maturity impression: 73,000 lines over one SQLite file, 165 test files, three model tiers reported separately, a paper and a `CITATION.cff` — and `valid_from`, `valid_to` and `entity_scope` written on every insert and selected by nothing.
- Study when: you are about to publish a retrieval number and have not decided what to disclose about how you got it.
- Do not copy when: you need the bitemporal or scoping behaviour the `fact_timeline` schema appears to offer, or you need "100% local" to mean no telemetry — it is opt-out, and defaults on.

### [`daem0n-mcp`](../systems/daem0n-mcp/)

- Best idea: mutating tools are blocked by MCP middleware until the agent holds a `PreflightToken` — an HMAC over the intended action, session, project and an expiry, issued only by `context_check`. Consultation becomes a precondition with a receipt that goes stale and is bound to the action it was sought for, instead of a prompt instruction the model may ignore.
- Biggest risk: `_TOKEN_SECRET` falls back to `"daem0nmcp-covenant-default-secret"`, committed in the source, so the signature the docstring says exists "to detect tampering" detects accident only. Beside it, `enforcement_bypass_log` has a table and a model and no writer — the record of who overrode the gate is the one whose absence cannot be reconstructed.
- Most reusable component: the bitemporal trio — `get_versions_at_time()` filtering valid time and transaction time together, `recall(as_of_time=)` filtering valid time only because backfilled `happened_at` data must still be findable, and `get_memory_at_time()` on transaction time — each documented with which dimension it uses and why.
- Maturity impression: 70,000 lines, 107 test files with four on the covenant alone, an embedding migration shipped as a runnable module and labelled breaking, and an uninstall document beside the install one.
- Study when: your agent is instructed to consult memory before acting and you have no way to know whether it did.
- Do not copy when: you need scope enforced inside one store — isolation here is one SQLite file per project directory, not a read-path predicate.

### [`pltm-claude`](../systems/pltm-claude/)

- Best idea: explicit opposite-predicate conflict detection, on the observation that contradictions are near neighbours in embedding space by construction — "I like jazz" and "I hate jazz" share subject and topic — so a similarity threshold treats a contradiction like a corroboration. Stage two even skips the similarity filter for exclusive predicates, so no conflict is filtered away before it is seen.
- Biggest risk: the headline "99% accuracy" is a unit-test pass rate — `run_200_test_benchmark.py` runs 200 hand-written assertions and prints `Accuracy: passed/total` — and the "100% vs 66.9% for Mem0" comparison runs Mem0 against those same author-written cases. Scoring 100% on your own specification is a tautology.
- Most reusable component: the four-judge jury's three-valued verdict — approve, reject, quarantine, with the safety judge always-binding. The vocabulary is right; the storage is not, and fixing it is a column.
- Maturity impression: 67,000 lines, 136 advertised MCP tools against 26 test files, two memory schemas live at once mid-migration, a `provenance` table specifying `quoted_span`, `content_hash`, `commit_sha` and `line_range` with no writer, and `venv311/` committed.
- Study when: your dedup or correction path decides by cosine similarity and you have not asked what a contradiction looks like to it.
- Do not copy when: you need the quarantine verdict to mean anything at read time — it is a halved float and a `[QUARANTINED: …]` marker appended into the free-text field the model reads back.

### [`memoir`](../systems/memoir/)

- Best idea: the collision policy is chosen by what kind of memory the taxonomy path implies — working replaces, episodic appends under a cap, semantic is confidence-gated, procedural is LLM-merged — in a module that is pure by construction, with `LLM_MERGE` inverted so the caller makes the model call and the decision table stays unit-testable.
- Biggest risk: `benchmarks/locomo/` is a complete LoCoMo-Plus harness — the paper's own judge reused verbatim, a full-context baseline as the anchor, both models named, the paper's no-disclosure prompt protocol, resume and incremental flush — and no result is committed anywhere in the tree.
- Most reusable component: `git_safety.py`. prollytree stores tree nodes as dangling git objects that gc is free to delete, so `harden_git_config` sets `gc.auto=0` and `gc.pruneExpire=never` on create and on every open so existing stores are retrofitted — then states the residual unprompted: an explicit `git gc --prune=now` still prunes, and the File backend is the only fully bulletproof option.
- Maturity impression: 55,000 lines implementing LangGraph's `BaseStore`, Merkle inclusion proofs delegated to prollytree rather than hand-rolled, `memoir blame` returning commit, author, date and message per key, a lazy v1→v2 schema lift with a byte-identical compatibility separator, and 35 test files.
- Study when: your store answers "a write landed on an occupied key" the same way for a scratchpad value and a stated fact.
- Do not copy when: you need a rejected-value record — `REPLACE` drops prior entries from the blob and they survive only in git history, recoverable but never consulted on the next write.

### [`memomind`](../systems/memomind/)

- Best idea: `engine/PATCHES.md` — four defects found by running [Hindsight](../systems/hindsight/) in production, each with file, change and reason. Two are memory-quality findings the upstream project does not measure: the consolidator creates observations that are 1:1 restatements of a single fact, and its 0.8 similarity gate is defeated by gpt-4o paraphrasing its own output, fixed by dropping to 0.5 *and* adding a length-ratio check.
- Biggest risk: `install.sh` runs `sed -i 's/password/trust/g'` over the application's `pg_hba.conf` and prints "Database auth fixed (trust mode)". The instance is the app's own, but trust means any local process can read years of imported private conversations without a password.
- Most reusable component: `prune_stale_observations` — delete observations with `proof_count <= 1` older than 30 days, and write what was deleted into the backup. Forgetting keyed on evidence rather than on a decay curve, and the operational counterpart to the patch that stops those observations being created.
- Maturity impression: roughly 63,000 lines of which 1,411 are this project's; no tests, no benchmark, a patcher defaulting to one machine's Windows path, and a documented warning that `pip install --upgrade` wipes the patches.
- Study when: you are running Hindsight — read the patch file before you run it again.
- Do not copy when: you are looking for a memory design; the mechanism here is upstream, and this project's contribution is the field report and the pruner.

### [`gitmem`](../systems/gitmem/)

- Best idea: a scar is refused at write time unless it carries at least two counter-arguments — and they are folded into the embedding text and returned on every search, so the objection travels with the claim to the point of use. Nothing else in this atlas requires a memory to argue against itself.
- Biggest risk: `dismiss_suggestion` documents that "suggestions dismissed 3+ times are permanently suppressed", but dismissal sets `status = "dismissed"` and the matcher skips non-pending records, so the same topic creates a fresh suggestion at count 0. `dismissed_count` can never exceed 1 and the `< 3` guard is unreachable; the unit test asserts only the reachable branch.
- Most reusable component: the refute-or-obey protocol — every surfaced scar answered with `APPLYING` (past-tense evidence and an artifact reference), `N_A` (scenario comparison) or `REFUTED` (risk acknowledgment), enforced by a `PreToolUse` hook that emits `{"decision":"block"}` on consequential Bash calls only.
- Maturity impression: 59,000 lines of TypeScript, 82 test files across five vitest configs, and a `gitmem_scar_usage` table recording `reference_type` including `'none'`, `surfaced_at` against `acknowledged_at`, `execution_successful` and a `variant_id` — plus `repeat_mistake` linking a recurrence back to the scar that failed to prevent it.
- Study when: your agent is shown memories and nothing records what it did about them.
- Do not copy when: you want the dismissal suppression as written — key it on the embedding, not on a generated id.

### [`engram-provable`](../systems/engram-provable/)

- Best idea: crypto-shredding resolves right-to-erasure against an append-only audit chain — content becomes AES-GCM ciphertext under a key discarded immediately, the embedding is cleared, and the redaction is recorded in the immutable chain, so the row and the history prove data existed and was erased while the content is unrecoverable. The first instance of the pattern in this atlas.
- Biggest risk: the README's 91.4% LongMemEval headline has no harness, no result file and no reference outside the README; the methodology lives on a website, outside the pinned commit. In an otherwise unusually verifiable system it is the one claim that rests on a link.
- Most reusable component: the audit chain as database enforcement — `seq`/`prev_hash`/`row_hash` set by a `BEFORE INSERT` trigger under `pg_advisory_xact_lock` per tenant, a `BEFORE UPDATE OR DELETE` trigger that raises so the application role cannot rewrite history, one `audit_canon` function shared by writer and verifier so the hashes cannot drift, and `verify_audit_chain` returning the breaking sequence number.
- Maturity impression: 44,000 lines of Go over 25+ ordered migrations, with tenant isolation, append-only, and the binding/ID state machine all enforced as constraints and triggers rather than service-layer discipline — and 32 test files.
- Study when: you have an audit requirement and an erasure requirement and have been treating them as incompatible.
- Do not copy when: you need the rejected-value record it is one query short of — `content_hash` is computed, chained and immutable, and no write path ever selects on it.

### [`agent-working-memory`](../systems/agent-working-memory/)

- Best idea: a retraction propagates a contamination penalty weighted by how tightly the retracted engram's 2-hop neighbourhood coheres — ~1.5× for a dense cluster with shared tags because "the whole cluster shares the wrong story", ~0.5× for an isolated engram, and a reduced bridge weight that barely touches the far side. Derived explicitly from the Continued Influence Effect (Carrillo et al., ICCM 2025) and bounded to 20 nodes and one batched fetch.
- Biggest risk: the 1.5× and 0.5× multipliers are asserted rather than measured, and they amplify the blast radius of a mistaken retraction exactly where the graph is densest.
- Most reusable component: `discardRegret` — counting engrams the salience filter tagged low-salience that were nonetheless accessed. Every write-time filter has a false-negative rate and almost none of them are measurable, because the rejected material is gone; tagging the near-misses makes the cost observable.
- Maturity impression: 45,000 lines of TypeScript over one store interface with PGlite, SQLite and Postgres backends, 49 test files, local ONNX models, and five distinct forgetting mechanisms — salience filtering, staging, decay, eviction and retraction — where most systems here implement one.
- Study when: your agent can correct a fact but everything it inferred from that fact stays untouched.
- Do not copy when: you need the sequence of corrections — retraction writes `retracted_by` and `retracted_at` onto the row, so there is no append-only record of how memory reached its current state.

### [`second-brain-cloudflare`](../systems/second-brain-cloudflare/)

- Best idea: staleness as a property of the claim rather than the row's age. A durable/state/volatile classifier — birthdays and birthplaces against job titles and cities against meetings and deadlines — sets each memory's recency floor at 0.9, 0.6 or 0.15, on the stated reasoning that a decay bottoming out at a floor makes "recency a tie-breaker rather than a gate", so "a strong old match can no longer be buried under a fresh weak one". The classifier returns null when unsure.
- Biggest risk: every system verdict lives in a caller-writable `tags[]` array, and the code documents two exploits of its own reserved namespace — a `Volatility:durable` tag that slipped past a case-sensitive filter and then won because the reader took the first match, and a junk `volatility:sometimes` that shadowed a real verdict. Both are fixed by hardening the readers; the namespace is still writable, in a system that ingests email.
- Most reusable component: the re-embedding migration's reasoning that its obvious progress marker would lie. Vector ids are derived from entry id and chunk count, so re-embedding into a fresh index reproduces them byte-identically — an entry the migration never reached "reads as 'vectorized' in D1 while the live index holds nothing for it", and the repair prompt stays hidden. Hence a separate KV ledger.
- Maturity impression: TypeScript on Workers, D1, Vectorize and KV with 125 test files, contradiction resolution that deprecates the loser *and* deletes its vectors from the index, and graph expansion tested to skip deprecated neighbours on the higher-weight edge.
- Study when: one exponential decay is quietly vetoing facts that were never going to change.
- Do not copy when: you need multi-user scoping — isolation here is one deployment per person, with no key on the read path.

### [`context-mem`](../systems/context-mem/)

- Best idea: forgetting as loss of resolution rather than deletion — verbatim for 7 days, key sentences to 30, summarizer-level to 90, facts-only after, with `pinned` never compressing and `importance >= 0.8` skipping one tier, over fourteen content-aware summarizers because a stack trace and a JSON config have different salvageable structure.
- Biggest risk: a gold `LongMemEval — 100% (500/500)` badge. The README's own table qualifies it as **R@5** under an optional LLM-judge blend (97.8% without), while LongMemEval's published headline metric is QA accuracy — and this repository commits its own measurement of that, `e2e-qa-real-500q-T5full.json`, at **46.6%**, with knowledge-update at 28.2%. To its credit the repository committed that file, and its competitor table says in bold "do not compare them directly".
- Most reusable component: `error_patterns_absent` in the regression fingerprint — a known-good snapshot that records which errors were *not* happening, so "what changed since it worked" is answerable in a way a list of present facts cannot manage.
- Maturity impression: six benchmark harnesses with dated result JSONs in the repository, 99 test files, `init` writing the right config for nine editors, and a plugin architecture where each of the fourteen summarizers is replaceable.
- Study when: your context bill comes from keeping tool output verbatim forever, and deleting it is the only alternative you have implemented.
- Do not copy when: you need the compression to be reversible — distillation is a one-way transformation of the stored content, gated by an importance classifier with no committed accuracy figure.

### [`moltbrain`](../systems/moltbrain/)

- Best idea: the session summary has a schema. `request`, `investigated`, `learned`, `completed`, `next_steps`, `files_read`, `files_edited`, `notes` are columns the parser fills from the model's XML, so "what did we learn across forty sessions" is a query rather than forty paragraphs — and observation `type` is constrained by a database CHECK to six values.
- Biggest risk: nothing in the system can be wrong. No confidence, no status, no `superseded_by`, no tombstone — so a mistaken observation stays in SQLite, stays mirrored in Chroma, and stays retrievable at full weight, while a superseded decision competes with the decision that replaced it on equal terms.
- Most reusable component: `VectorSync`'s stated design — "fail-fast with no fallbacks - if Chroma is unavailable, syncing fails". A mirror that degrades silently leaves semantic search returning a stale subset with nothing to indicate it.
- Maturity impression: 40 test files, careful explicit-column SQLite migrations, four indexes on the observations table, and a substantial product surface — web viewer, themes, favourites, filters, export, analytics — around a memory model that is a typed append-only log.
- Study when: you want automatic capture you will browse yourself, with a good viewer and export.
- Do not copy when: memory is injected into an agent without a person in the loop — the only deletion path in the tree is a duplicate-cleanup script run by hand.

### [`fidelis`](../systems/fidelis/)

- Best idea: `WRITEUP-LONGMEMEVAL-20260423.md`, the most honest benchmark document in the atlas. Holding a 96.4% retrieval R@1, it declines to compare it to a competitor's 94.87% QA accuracy — "the gap is not the issue, the metric is" — explains that R@1 is an upper bound on QA accuracy, discloses its own 54.2% on the comparable metric, prices the experiment that would settle it at $1.24, and says it is blocked on an API key.
- Biggest risk: nothing corrects a stored passage. Verbatim retrieval with no status, no supersession and no decay means a note that stopped being true has the same standing as one written yesterday, in a system whose own timeline promises accumulating project context by day 7.
- Most reusable component: the ablation table that publishes the change which made things worse — turn-level chunking at 66.8% against a 73.2% BM25 baseline, in the table, with an `LLM?` column so a reader can see which gains cost money — beside a Wilson 95% CI on the end-to-end accuracy, which appears nowhere else in this corpus.
- Maturity impression: 31 test files including `test_public_install_truth.py`, `test_telemetry_kill_actually_kills.py` and `test_zero_llm_regression.py` — tests of claims, not only of code — and seven files guarding one write-loss incident recorded in `degrade.py`'s docstring.
- Study when: you are about to publish a benchmark number and have not decided which metric it is.
- Do not copy when: you need the store to age — the design position is that you edit your notes.

### [`telemem`](../systems/telemem/)

- Best idea: a published evaluation charter with a harness flag behind every rule — a grep baseline and a full-context baseline required in every table, `--validate-judge` feeding gold answers that must pass and shuffled wrong-but-topical answers that must fail, `--seeds N` with Wilson intervals, and an advance commitment not to claim a win across overlapping intervals. Rule 9 discloses the conflict of interest in the document making the claim.
- Biggest risk: the methodology is shipped and the numbers under it are not. The charter "governs new evaluation runs" and says the README's existing table predates it, so the results a reader can see are ones the project has already disowned, with the re-runs tracked in a public issue.
- Most reusable component: the sentence telling readers how to find out they do not need the product — "build a full-context baseline and a grep baseline **on your own data** first… you may not need TeleMem — or any memory system." Applying rule 1 to a reader's own data is the selection procedure this atlas would give.
- Maturity impression: a mem0 drop-in with a tech report, CI, an MCP server on the current spec, and `tests/test_contract.py` where each test is named after the API promise it enforces — including two that assert negatives, that `infer=False` calls no LLM and that telemetry is opt-in.
- Study when: you are about to publish a comparison table and have not decided what would make it defensible.
- Do not copy when: you need correction — everything epistemic is inherited from mem0, and the unscoped-write fallback into a shared `events` scope is readable by every character.

### [`mengram`](../systems/mengram/)

- Best idea: a regression test for memory. Before promoting a revised procedure, `find_regressions` asks which other current procedures share its surface and whether the revision adds a precondition they do not satisfy — and on a hit it sets `status = "needs_review"`, skips retiring the old version, and writes the new one `is_current = FALSE`, so "the last known-good version stays authoritative until review". Every other system in this atlas applies a correction and hopes nothing depended on the old memory.
- Biggest risk: nothing surfaces the quarantine. No endpoint lists `needs_review` or approves a gated revision, so the safe behaviour is a dead end — including when the revision was right and the dependent procedure was what needed updating. And the gate fails open: an exception in it logs "regression gate skipped" and promotes.
- Most reusable component: `benchmark/procinterfere/` — a public benchmark for cross-procedure interference, with **silent-regression rate** reported beside **false-quarantine** so over-flagging is measurable, 18 cases in one JSONL, runnable with no account because the gate is pure functions. The contribution is the metric and the case format; the 0% score is against self-authored cases and two unchecked baselines.
- Maturity impression: Postgres with versioned procedures, a GIN index on entities, an evolution log carrying each diff and its originating episode, both-polarity unit tests including "a negated mention does not count as satisfying" — and a spec still headed `Status: design` for a gate that shipped.
- Study when: your agent revises what it learned and you have never asked what depended on the old version.
- Do not copy when: you need the review half — the quarantine is written and never read.

### [`opencode-mem`](../systems/opencode-mem/)

- Best idea: `SECURITY_AUDIT.md` — a committed read-only audit of its own code with five graded findings, each carrying the exploit path, the fix and the regression test that pins it. The CRITICAL one prints the working payload; the HIGH one explains why CORS is not authentication (`isAllowedBrowserOrigin()` returned true when no `Origin` header was present, so every non-browser client passed); and finding 5 is published as *not fixed*, with the reason.
- Biggest risk: the audit is scoped to an earlier commit than the one pinned here, so a reader could take a committed audit file as a standing guarantee rather than a point-in-time artifact. The three named regression tests are the durable part.
- Most reusable component: `privacy.ts` — `<private>…</private>` redaction implemented with a depth counter rather than a pair-matching regex "so that the two malformed shapes fail *closed*", meaning an unclosed tag redacts to the end of the input instead of storing the secret, and `<private >` is tolerated the way an XML parser would.
- Maturity impression: embedded Turso/libSQL with inline `F32_BLOB` vectors and a DiskANN index, two vectors per memory, 66 test files, a CI matrix across six OS/architecture combinations with a note on what it does *not* cover, and a `.legacy.bak` written per shard before migration.
- Study when: you have a local HTTP API and a CORS policy and have not asked what happens when there is no `Origin` header.
- Do not copy when: you need correction — `is_pinned` is the only field that changes a memory's standing, and it changes retention rather than truth.

### [`openmemory`](../systems/openmemory/)

- Best idea: `test_project_isolation.ts` asserts three things per direction — the project finds its own memory, does *not* find the other project's, and *does* find the shared `system_global` tier. Each assertion alone passes for a broken implementation (return everything, return nothing, drop the global scope); together they pin the behaviour.
- Biggest risk: the distinguishing claim is unmeasured. `SECTORAL_INTERDEPENDENCE_MATRIX_FOR_COGNITIVE_RESONANCE` is a hand-typed symmetric 5×5 grid, sitting under twelve Greek-lettered constants, with no citation, derivation, fitting procedure or ablation anywhere — while `Why.md` scores the project ✅ against vector databases' ❌ on "biological alignment" and "explainable recall".
- Most reusable component: bounding a graph signal's contribution — `waypoint` at 0.15 of the pre-sigmoid hybrid score with a `waypoint_boost` and a `max_waypoint_weight`, so an association graph cannot swamp similarity as it densifies.
- Maturity impression: a wide integration surface — two SDKs, MCP, VS Code, four frameworks, five source connectors — full governance documents, and a README whose first line announces a rewrite in progress on another branch.
- Study when: you are building multi-project memory with a shared global tier and need the test that pins it.
- Do not copy when: you want the sectored model — run retrieval with the matrix, flattened, and randomised first; nothing in the repository shows it earns its place.

### [`ori-mnemos`](../systems/ori-mnemos/)

- Best idea: `stage-learner.ts` makes each retrieval stage an arm of a LinUCB bandit that learns per query type whether the stage earns its latency and auto-skips it when it does not — with `MIN_SAMPLES = 15` before acting, an abstain threshold so it declines to decide, a cost penalty so a stage must be worth its latency rather than merely harmless, a load-balance term borrowed from mixture-of-experts, and a hard time budget.
- Biggest risk: the repository contains two tables of the same benchmarks whose numbers disagree — the README gives HotpotQA F1 0.68 where `bench/README.md` gives 0.523 and 0.410, and the README's LoCoMo 37.69/29.31 appear nowhere in the bench file's per-category figures — and `.gitignore` excludes `bench/results/`, so no committed run adjudicates.
- Most reusable component: `warmth-audit.jsonl`, which logs `baseRank` and `baseScore` beside `finalRank` and `finalScore` with the `movement` computed. Logging the counterfactual makes a re-ranking signal's contribution measurable; logging only the final ranking makes it an article of faith.
- Maturity impression: markdown on disk with a SQLite index and wiki-links as graph edges, ACT-R base-level activation written out beside exponential vitality decay, 35 test files, two design specs at the root, and `fading` and `warmth-audit` as first-class CLI commands.
- Study when: your hybrid retriever runs every arm on every query and you tune fusion weights by hand.
- Do not copy when: you need the comparison the README makes — Mem0 is measured on source-document recall through an extraction pipeline that discards source text, which is not the workload it is built for.

### [`yourmemory`](../systems/yourmemory/)

- Best idea: decay is deliberately kept out of the ranking formula, because "multiplying cosine by strength would penalise old-but-valid memories below newer irrelevant ones". Ranking is `0.4 × bm25_norm + 0.6 × cosine`; decay drives a 24-hour prune and the graph node scores instead, with the rate set per claim type — `fact=0.16, strategy=0.10, assumption=0.20, failure=0.35`.
- Biggest risk: the `replace` branch overwrites in place. The system detects that the incoming statement contradicts the stored one — the hard part — and then destroys the old value, leaving no supersession record and nothing to stop it returning.
- Most reusable component: `audit.py` — a hash-chained log of reads, writes, deletes and admin actions that stores memory *ids*, counts and query *length* and never content or query text, "so the audit log itself isn't a data-leak vector", with retention floored at 90 days and a fail-open policy whose compensating control (`verify_chain()`) is named.
- Maturity impression: three backends behind one connection layer, non-LLM fallbacks beside the LLM paths, a benchmark document leading with `recall_all@5` when `recall_any@5` is eleven points better, 95% CIs, and a `SOC2_READINESS_REPORT.md` labelled "NOT a SOC 2 attestation… Prepared by: Automated codebase assessment" on line 2.
- Study when: your ranking multiplies relevance by a decay term and old correct answers keep losing to new irrelevant ones.
- Do not copy when: you need to know what a correction replaced — five test files also carry three benchmark suites.

### [`cortex-engine`](../systems/cortex-engine/)

- Best idea: `contradict` adjudicates the (evidence, belief) pair into five outcomes before recording anything, and only `genuine` penalises confidence — `supersedes` gets a lower-priority TENSION signal and no penalty, because "the world changed; revise via believe() with valid_from instead of distrusting the belief". Everywhere else in this atlas a superseded fact and a refuted one are treated alike, which teaches the system to distrust things that were correct at the time.
- Biggest risk: a dozen neuroscience-named mechanisms — NREM/REM consolidation, Thousand Brains voting, Fiedler-value graph health, epistemic foraging, PE saturation — with no evaluation of any of them anywhere in the tree.
- Most reusable component: `believe()`'s transaction discipline. The belief log and the memory update commit together "so we never end up with a belief entry that points at a memory that was never updated, or a memory whose history is missing the revision row", and the embedding is computed *before* the transaction because network calls "must never happen inside `withTransaction` (they hold the writer mutex open)".
- Maturity impression: 32,000 lines, three storage backends behind one interface with a checkpointed ID-preserving migrator that fails loud on schema mismatch, 60 MCP tools each carrying `whenToUse` *and* `doNotUse`, and a REST surface that blocks the destructive tools while leaving them available over MCP.
- Study when: your confidence scores fall for beliefs that were true when they were written.
- Do not copy when: you need `valid_from` to be queryable — it is stored on every backend, read back by the mappers, and used in no predicate.

### [`obsidian-mind`](../systems/obsidian-mind/)

- Best idea: a byte budget on session-start injection that degrades the cheapest-to-lose sections to pointers and then **names every one it dropped in the size meter, "because a silent loss is worse than the bloat"**. The ranking rule is value density rather than size — filenames go first because one Glob rebuilds them; identity, personal context and correctness guards carry no fallback and are never traded for plumbing.
- Biggest risk: no staleness story. A vault accumulating "Key Decisions" and "Gotchas" for a year holds reversed decisions and fixed gotchas, and nothing distinguishes them from the live ones — the design controls how *much* gets injected with real rigour and not whether it is still true.
- Most reusable component: the argument against the obvious alternative — "line-based caps cannot do this job: shortening entries under a line cap just slides the window deeper and refills it" — together with the rule that optimising the eager layer means removing *duplication*, not *information*, which is why resume and compact re-inject only the volatile sections.
- Maturity impression: a vault template with lifecycle hooks for three agent CLIs, Obsidian `.base` views so the human and the agent query one store, an exposure allowlist that ships empty with a written reason, and a path check that unifies separators before normalising because POSIX `normalize()` will not collapse a backslash-spelled `..`.
- Study when: you inject context at session start and have never measured what it costs.
- Do not copy when: you want a component — the vault *is* the system, adopted wholesale.

### [`vir`](../systems/vir/)

- Best idea: deciding which of your own transcripts are actually yours. Of 243 files on the author's machine "about 20 were sessions I actually drove" — the rest subagent runs, workflow phases and headless SDK agents — and vir detects all three with three independent mechanisms: on-disk layout, the first user line's `entrypoint`, and a per-line `isSidechain` backstop whose test says it is a backstop. Every transcript-mining memory system has this problem and this is the only careful treatment of it here.
- Biggest risk: two LLM passes stand between a transcript and a note, nothing measures whether the note is faithful, and the vault is designed to outlive the transcript — so an unfaithful distillation becomes permanent and unfalsifiable once Claude Code's ~30-day pruning window closes.
- Most reusable component: the rejected-signal notes. `promptSource` reads "sdk" even on desktop-launched human sessions (the C23 serbeval trap) and turn count would kill single-prompt autonomous runs — the two signals a reader would reach for first, ruled out with the reason. Beside them, a redaction rule whose comment names the innocent string it must not eat: `"risk-ant-…"` must survive.
- Maturity impression: 46 test files with nearly one per pipeline module, tests named for the behaviours they protect (`run.rewriteDryRun`, `run.retryBound`, `run.transcriptFilter`), a cheap-model-triage/expensive-model-distil split with cost tracking, and a TF-IDF fallback so it works before any model server is configured.
- Study when: you mine an agent's own logs and have not checked how much of that history the user actually wrote.
- Do not copy when: you need `confidence` to do anything at query time — it selects the top five for `sync-claude` and nothing else.

### [`diffmem`](../systems/diffmem/)

- Best idea: memory files hold only the current view so queries scan a compact surface, and every prior state lives in the commit graph — log-and-projection with git supplying the log, and `git blame` giving per-line provenance at no storage cost. Retrieval is an LLM issuing `grep`, `git log`, `git diff` and `git blame` behind a thirteen-command allowlist that validates every segment of a chain and gives `git` a second allowlist of read-only subcommands.
- Biggest risk: validation tokenises with `shlex.split` and execution runs `subprocess.run(cmd_str, shell=True)` on the original string, with nothing rejecting `$(…)`, backticks or redirection — so an argument the validator approved can be syntax the shell expands. It matters here because an LLM composes the commands and, in the named production deployment, the repository holds text the operator did not author. None of the 22 test files covers the router.
- Most reusable component: the pluggable executor — endpoints build a thunk closing over the real writer or consolidator call and hand it to `submit_write`, so the queue backend and the memory internals stay decoupled and inline execution still works in development.
- Maturity impression: 14,800 lines with consolidation decomposed into named, individually tested passes under a lock, ontologies as swappable directories with a conformance module, a production deployment named, and a roadmap that lists its own entity-resolution failure — "sometimes an entity will become a catch-all and the thing will insist in overloading it".
- Study when: you are about to build an index next to a store that git already versions.
- Do not copy when: recall has to survive vocabulary mismatch — there is no semantic fallback when the right memory uses different words from the query.

### [`memsearch`](../systems/memsearch/)

- Best idea: a distilled skill is inert. Candidates "are never written into an agent's skills directory by this module. Turning a candidate into an agent-visible skill is a separate, human-driven step" — enforced at a module boundary rather than a flag, with the candidate store its own git repository so every automatic edit is a commit with diff and revert, and the whole feature off by default.
- Biggest risk: the gate is on the safe path. Skill distillation is gated, disabled and revertible; the background maintenance pass rewriting `PROJECT.md` and `USER.md` is none of those, and those two files are what the agent reads as durable truth.
- Most reusable component: `evaluation/README.md` — an embedder choice made on 955 chunks and 2,172 queries built from the project's own memory logs across twelve projects, chunked by its own chunker, with simple, complex and multi-hop questions in Chinese and English, twelve models with their sizes in the table, and the primary metric justified from the interface: "the user typically sees top 3-5 results, so Recall@5 is primary".
- Maturity impression: four maintained agent plugins sharing one store, index-health diagnostics for a deliberately disposable index, SHA-256 gating so a live file watcher is affordable — and a vector-database vendor calling its own product "a shadow index: a derived, rebuildable cache".
- Study when: your system distils procedures from experience and then runs them.
- Do not copy when: you need the pipeline evaluated — the methodology is excellent and stops at the embedder.

### [`mnemos`](../systems/mnemos/)

- Best idea: `internal/eval` builds a held-out corpus **with each query's text stripped from its own host chunk** before indexing, so a generated-question evaluation cannot be won by finding the question inside the answer — using the same goldmark configuration as ingestion "so the AST view of a document matches what ingestion sees", ingesting into an ephemeral database, and comparing against a versioned baseline where a missing file is deliberately not an error.
- Biggest risk: citation is not status. The README's opening complaint is that an agent "forgets why you rejected an architecture", and a rejected ADR cites exactly as cleanly as an accepted one — nothing in the index says which way the decision went, though ADR conventions already carry a `status` header to read.
- Most reusable component: a secret scanner whose `Finding` holds the matched substring on an **unexported** field, "so it cannot leak through serialization or an external caller: the remember tool reports only Rule names and never echoes the value back to the agent". A scanner that hands the model the key it just found has moved the secret into the context it was protecting.
- Maturity impression: 19,800 lines of Go with 84 test files, one cgo-free binary with no Python, Node, vector database or model server, a `doctor` command, and a benchmark comparing the scoped and unscoped query so the collection predicate's index usage is visible.
- Study when: you are about to generate evaluation questions from the documents you are also indexing.
- Do not copy when: you need the number — the harness and the baseline mechanism are in-tree and no baseline JSON is.

### [`nocturne-memory`](../systems/nocturne-memory/)

- Best idea: `text_patch.py` — when an agent edits memory by quoting the passage, the model re-emits curly quotes as straight ones, em dashes as hyphens and collapses double spaces, and the exact match fails. The fix normalises both sides to *find* the target "while keeping a position map so the replacement targets the correct range in the original content", and only after an exact match has already failed. Every system whose edit interface is quoted text has this bug.
- Biggest risk: `update_memory` patches in place with no record of the change, in a system whose README demonstrates months of accumulated strategy memory — nothing distinguishes a conclusion the user has since abandoned from a current one. A `demo.db` is also committed beside a README full of personal notes.
- Most reusable component: memory as a URI namespace — `core://domain/topic` for stored nodes, with `system://boot`, `system://index/<domain>`, `system://recent` and `system://glossary` generated from the graph on read so they cannot drift. An agent that can navigate deliberately as well as search is strictly better off, and the README's session traces show it opening with `read_memory("system://boot")`.
- Maturity impression: 19,200 lines with MCP over SSE and streamable HTTP, a REST API, a web frontend and a documented workaround for FastMCP's SSE transport dropping the namespace on `POST /messages/` — against 12 test files, thinnest exactly at the fuzzy patcher whose failure is a silently wrong edit.
- Study when: your agent edits stored memory by quoting the text it wants to replace.
- Do not copy when: you need the framing to mean something — "alignment is for tools, memories are for sovereign AI" is positioning, and the URI graph underneath it is the part that works.

### [`claudest`](../systems/claudest/)

- Best idea: "**a run that only adds is a failure mode**" — consolidation judged by what it removed, with the auditor producing SUPERSEDED / REDUNDANT / LOW-VALUE / MERGE findings the protocol requires to become concrete proposals. Beside it: retirements settle *before* clustering, because "clustering never runs before retirement; it must not mask removable entries".
- Biggest risk: the whole protocol is prose an LLM is asked to follow, enforced by nothing. The ordering rule, the removal requirement and the verification step can all be skipped with nothing failing loudly — against two test files for 8,800 lines of hooks that edit the user's `CLAUDE.md` and `MEMORY.md`.
- Most reusable component: three independent guards on agent-initiated deletion — `AskUserQuestion` offering *Approve selectively* rather than approve-all, `trash` instead of `rm` so an approved mistake is recoverable, and a `Glob` afterwards because "claiming a deletion that did not happen is the exact failure this guards against". Any one alone is insufficient.
- Maturity impression: SQLite with FTS5 and zero external dependencies, precomputed summaries injected at session start with separate selection algorithms for a fresh start and a `/clear`, and one integer doing three jobs — `summary_version < 2` selects for work, `2` marks current, `-1` marks permanently failed so a poisoned document is never retried.
- Study when: your consolidation pass has never deleted anything.
- Do not copy when: you need the protocol enforced — it is a specification for a model, not code.

### [`agentmemory-v4`](../systems/agentmemory-v4/)

- Best idea: comparability notes that restate three rivals into like-for-like form — OMEGA's task-weighted 95.4% as raw 466/500 = 93.2%, Supermemory's ~99% as its single-pass 85.86%, and Hindsight flagged for using one model as both generator and judge — alongside a committed result file, a committed run log, `PYTHONHASHSEED=42` with judge `seed=42`, and a `LEGITIMACY.md` self-audit. Recounting the 500 per-case records gives 481, so the headline is reproducible from the file rather than asserted.
- Biggest risk: three committed artifacts — the runner default at `:713`, the run log's second line, and the result summary's `dataset` field — all name `longmemeval_oracle.json`, while the README says the score is on LongMemEval_S with "no oracle access" and excludes others' oracle scores as not reflecting real retrieval. The self-audit lists the file and argues no oracle *metadata* is consulted, which is true of the harness and does not address what `haystack_sessions` contains in that variant.
- Most reusable component: `assert not USE_DIRECT_CONTEXT, "INVALID: … must be False for legitimate evaluation"` — guarding the shortcut you were tempted by so the invalidating configuration crashes the run instead of producing a number.
- Maturity impression: a 2,800-line harness with `--resume`, `--offset` and `--dataset`, per-question-type token budgets tuned against named failures, and a self-audit written as a table of checks with file and line for each.
- Study when: you are about to publish a record and want to know what evidence to commit alongside it.
- Do not copy when: you need the number — one re-run with `--dataset longmemeval_s.json`, logged the same way, would settle it.

### [`memv`](../systems/memv/)

- Best idea: store only what you failed to predict. The extractor asks the model what an episode should contain given existing knowledge, compares that against the actual transcript, and keeps the gap — so importance comes from prediction error rather than an importance prompt with no reference point. Credited to Nemori in the module docstring, with a discipline note beside it: the narrative summary is for retrieval, the original messages are the only extraction source, so a summarisation error cannot become a stored fact.
- Biggest risk: the criterion is unmeasured. Prediction error decides everything stored, so too good a predictor silently discards real information and too poor a one stores what the design exists to avoid — and the rate moves with whichever model the caller passes in. Nothing counts the discards.
- Most reusable component: the bitemporal store — `valid_at`/`invalid_at` for when a fact was true and `expired_at` for when belief in it ended, queried together as of an event time with `include_expired` as the switch, plus a model validator rejecting `invalid_at <= valid_at`. Two dimensions as separate columns rather than one timestamp doing double duty.
- Maturity impression: 12,000 lines with SQLite and Postgres behind one storage layer, pluggable LLM and embedding adapters as constructor arguments, and a LongMemEval harness with checkpointing — and an empty `benchmarks/results/`.
- Study when: your write path decides what to keep by asking a model how important something is.
- Do not copy when: you need to know why belief ended — `expired_at` records when, not whether the fact was superseded or refuted.

### [`memcp`](../systems/memcp/)

- Best idea: feedback weighted asymmetrically and propagated to the graph. `memcp_reinforce` moves a helpful insight `+0.1` and boosts its edges `0.02`; a *misleading* one moves `-0.2` and weakens its edges `0.05`. One report of being misled outweighs two of being helped, and the penalty reaches the neighbourhood rather than stopping at the node — because a misleading insight usually sits in a misleading neighbourhood.
- Biggest risk: `benchmark_output/benchmark_report.md` is a dated head-to-head whose "Native" column is not measured. `tests/benchmark/test_context_rot.py` sets `native_value=5.0  # Typical ~5% retention` and `native_value=2.0  # ~0.05^3 ≈ near zero` — one assumed constant derived from another — and the JSON computes a savings percentage and a ratio from them.
- Most reusable component: intent-typed traversal — "why did we choose X?" follows causal edges, "when was Y decided?" follows temporal ones. Choosing the relation to walk from the question's form is cheap and legible, and only possible because the edges are typed at write time.
- Maturity impression: 14,300 lines with a three-layer delegation, a four-relation SQLite graph with Hebbian strengthening and configurable-half-life decay, secret blocking on the write path, and **two** required dependencies with NER, embeddings and sub-agent extraction all optional.
- Study when: your feedback loop treats "this helped" and "this misled me" as mirror images.
- Do not copy when: you need the benchmark — "knowledge retained after a context wipe" is a property every external store has by construction, and a plain text file scores 100%.

### [`arcrift`](../systems/arcrift/)

- Best idea: the tenant isolation audit plants a **named canary** in each of ten projects and asks the wrong one for it — `forbiddenKey: "SECRET_BETA_88"`, `success: !leaked` — against a **live spawned MCP process** under **concurrent** JSON-RPC, with the report committed. A row count cannot catch a partial leak, a mock cannot reproduce a session-layer one, and a sequential test cannot reach a race.
- Biggest risk: capture depends on seven other companies' DOM and the weekly Playwright check covers three of them, with a silent failure mode — "if Save Chat returns 0 messages… check this file first". The multi-strategy resolver limits the blast radius; the gap between the monitored set and the supported set does not close itself.
- Most reusable component: knowing your most fragile dependency, documenting its symptom, monitoring it on a cron, and letting the monitor file your bug — "if any selector fails, it auto-creates a GitHub issue tagged `bug` + `selector-stale`".
- Maturity impression: four committed audit reports, recall measured against a 1,000-chunk noise haystack rather than a corpus of only relevant documents, a per-engine contribution table answering which arm of the hybrid actually found each fact, and benchmark documents that state what they do not cover.
- Study when: your multi-tenant boundary has never been asked for the neighbour's secret by name.
- Do not copy when: you expect contradiction handled — thirty conversations about one auth flow accumulate every intermediate position at equal standing, and the answer offered is more context.

### [`memlayer`](../systems/memlayer/)

- Best idea: salience defined by example rather than by prompt. Two hand-written lists of prototype sentences — what counts as worth keeping, what counts as noise — with incoming text scored by similarity, and a regex fast path so bare greetings never reach the embedder. The decision boundary is readable, diffable, editable data rather than something inside a model.
- Biggest risk: `SALIENT_PROTOTYPES` includes `"The user's API key is sk-12345."` as an example of *what to remember*, alongside an email address and an internal IP — so credential-shaped text scores toward storage, in a tree with no secret screen anywhere. Four systems read in the same batch block or redact secrets on the write path; this one treats one as exemplary.
- Most reusable component: the mode enum whose comments are the trade-off — `LOCAL # default, slow startup`, `ONLINE # fast startup, API cost`, `LIGHTWEIGHT # no embeddings, instant startup` — so a caller chooses at the point of choosing, and the lightweight path makes the first run work with no model download.
- Maturity impression: 9,200 lines with wrappers per provider delivering the three-line adoption claim, three retrieval tiers with published latency budgets, and an observability module to check them — against 12 test files and no evaluation of the gate itself.
- Study when: your write path asks a model how important something is.
- Do not copy when: you need anything to change after the door — the gate decides entry and nothing decides whether a stored fact is still true.

### [`stash`](../systems/stash/)

- Best idea: a hypothesis gets its own table. `proposed` / `testing` / `confirmed` / `rejected`, with a `verification_plan` and a `method` saying how it could be settled, and on resolution either a `confirmed_fact_id` or a `rejection_reason` — so a claim the system inferred but has not established is not stored as a fact, and recall cannot reach it because the separation is a table boundary rather than a predicate someone must remember to apply.
- Biggest risk: one reasoner adjudicates contradictions, extracts causal links and resolves hypotheses — three judgements each writing into the store the next one reads — with `internal/brain/brain_test.go` as the only test in the package and no evaluation of any of them.
- Most reusable component: contradiction detected on `(entity, property)` rather than by embedding similarity. "Alice works at Acme" and "Alice left Acme" are near neighbours, and so are "Alice works at Acme" and "Bob works at Acme"; only the triple's subject and predicate separate *says the opposite* from *is about the same thing*. And when either key is missing it returns no candidates rather than falling back to similarity.
- Maturity impression: 7,900 lines of Go with six first-class epistemic entity types — facts, hypotheses, contradictions, causal links, goals, failures — one file per concept, `failures` splitting content from reason from lesson, consolidation runs reporting `llmCalls` beside their outcomes, and `docker compose up` as the entire install.
- Study when: your system stores an inference and an observation in the same place with a confidence float between them.
- Do not copy when: you need a rejected claim to stay rejected — the rejection is durable and nothing consults it on the next inference pass.

### [`knowledge-worker`](../systems/knowledge-worker/)

- Best idea: a fabricated-quote detector. A `high`-confidence claim must carry an excerpt and the excerpt must substring-match the source; if it does not, the claim is **demoted to `low`** with the reason recorded — `no_excerpt` or `excerpt_not_in_source`. An LLM asked to extract claims with evidence will invent the evidence, and this catches it deterministically with no second model call. Demotion rather than rejection is the right third option: the claim may be true, it is just not evidenced.
- Biggest risk: substring matching catches *invention*, not *misquotation in context*. "I would never use MongoDB for this" contains "use MongoDB for this", and a claim excerpting the fragment passes — storing the source offset rather than the text would let the surrounding span be checked.
- Most reusable component: the validation manifest — accepted, rejected and demoted nodes and edges, each with an enumerated reason string — which turns an extraction pass from a silent transformation into an auditable one, and gives tests an exact assertion target.
- Maturity impression: 7,500 lines with a closed node and edge type set, edge endpoints resolved against both the existing graph and the current candidate batch so an edge to a just-rejected node is dropped, OWL import and export, and analytics that keep provenance edges out of the semantic centrality measures — against 8 test files, none on the validator.
- Study when: an LLM is deciding what becomes durable knowledge in your store and you take its evidence on trust.
- Do not copy when: you need automatic recall — the model is handed a filtered brief, and the retrieval decision stays with the human.

### [`memory-ts`](../systems/memory-ts/)

- Best idea: a schema that deleted seven of its own fields and recorded the evidence for each — `emotional_resonance` ("580 variants, never used"), `component` ("always empty"), `parent_id`/`child_ids` ("no logic implemented"), `knowledge_domain` ("overlaps with project_id + domain"). This atlas spends much of its time finding declared-and-unread fields; this is a project that went looking for its own and left the receipts.
- Biggest risk: the curator is the product and is a subprocess call to an external CLI, exercised by one hand-run script at the repository root that prints the result of curating a single session. What fraction of curated memories are ever surfaced is the measurement, and `sessions_since_surfaced` already holds the answer.
- Most reusable component: the two-tier memory — a headline always shown and full content expanded on demand, with auto-expand rules (`action_required`, `awaiting_decision`, 5+ signals) saying when brevity is the wrong default. Two fields rather than truncation at render time means retrieval shows twenty summaries for the cost of two full memories.
- Maturity impression: 11,600 lines of TypeScript with a five-state status filtered on the retrieval path *and* in the replacement and linked-memory lookups, decay counted in sessions rather than days, and a migrations directory — because the schema actually changes.
- Study when: you suspect half your schema is fields nothing reads.
- Do not copy when: you need supersession to hold — `superseded_by` records the replacement and nothing stops the old content being re-extracted from a later transcript.

### [`marsnme`](../systems/marsnme/)

- Best idea: an agent can leave an addressed note for another agent. `session_close(to=<body>, note=...)` writes it, `session_boot(body=<target>)` delivers unread notes and marks them read — three columns and an index on `(recipient_body, read_at)`. Every other multi-agent system in this atlas coordinates by both parties reading a common store and hoping the right thing is salient; this one gives delivery semantics a shared store cannot.
- Biggest risk: the provenance CHECK constraint that makes the write surface enumerable holds in one profile schema and not the other — "toto.marsvault_chunks has no origin check constraint" — which the project documents and which is worse than no guarantee, because a reader generalises from the first schema they check.
- Most reusable component: provenance as a database constraint. A chunk whose `origin` is not in the allowlist is rejected by Postgres, so a new tool cannot write until someone widens the constraint in a migration — and the values are granular enough to be useful (`perplexity-coco`, `cursor-coco`, `warp-coco`, `batch-promote`) rather than a boolean.
- Maturity impression: 3,900 lines across two deployment targets with sixteen MCP tools, a three-tier recall stating its character budget per tier (~80, ~300, full) as three separate tools, auto-promotion of memories expiring within 48 hours at session close, and a version that *removed* five tools and said where they went.
- Study when: your agents share a store and you need one of them to hand something to another and know it arrived.
- Do not copy when: you need evidence — the offered support is the author's own three months of daily use, honestly attributed, and no test covers the delivery path.

### [`breadcrumbs`](../systems/breadcrumbs/)

- Best idea: a committed test that a *corrected* entry stopped surfacing. `run_forbidden_check()` in `templates/ledger-tools/retrieval_exam.py` replays a configurable model of the boot matcher against simulated session-start conditions and names any entry marked `obsoleted_by` that still wins an injection slot — *"correction that stops at the ledger row and never reaches the retrieval lane is not correction"*. Two systems here fail exactly that way on their main retrieval path, and neither has a test that would have caught it.
- Biggest risk: the fleet architecture the docs describe — an orphan memory branch, per-session fold files, a read-time projection, a reaper that checks a fold's claim against merged history — is not in the tree. What ships is a handful of stdlib scripts and a pile of templates. `docs/floating-memory.md` opens with a header saying so; `docs/breadcrumbs-whitepaper.md` beside it presents five mechanisms as the system, two of which have no code path here.
- Most reusable component: `retrieval_exam.py --survey`, which needs no ledger, no adoption and no dependencies. It walks any repository's markdown, computes link distance from `CLAUDE.md`/`AGENTS.md`/`README.md`, prints what every session pays in bytes before any work happens, and names the orphan — the document nothing links, which a session never opens on its own.
- Maturity impression: 34 commits, 202 files, no package manifest and a stated case against one, MIT. Six `--selftest` entry points and a subprocess-driven unittest suite totalling 115 offline checks, all of which pass, and `.github/workflows/ci.yml` runs every one of them under a step arguing that the memory tools *"cannot live outside the gate that guards everything else"*. What CI does not run is the forbidden-hit check against a ledger, because the only conclusions ledger in the tree is a fixture engineered to produce a hit.
- Study when: you already have a rules file and a pile of markdown, and you have never checked whether any of it reaches a session.
- Do not copy when: you need semantic recall, a scope boundary, or memory that writes itself — every entry here exists because a person decided to type it, and retrieval is exact keyword matching that will miss a paraphrase and says so in the injected block.

### [`gh-aw`](../systems/gh-aw/)

- Best idea: memory on an information-flow lattice. The cache-memory store is a git repository with one branch per trust level — `merged`, `approved`, `unapproved`, `none` — and `actions/setup/sh/setup_cache_memory_git.sh` checks out the branch for the run's own level, then merges *down* from strictly higher levels only: *"lower-integrity runs see higher-integrity data via merge, but higher-integrity runs never see lower-integrity data."* A fork PR can read what a merged run remembered and cannot write into it.
- Biggest risk: the trust label describes the run that wrote the file, never the claim inside it. Nothing here can mark a memory wrong, and no file ever moves between levels, so a poisoned note written by one unapproved run is simply what every later unapproved run knows. Concurrency is documented as last-writer-wins.
- Most reusable component: the pre-agent sanitisation gate. Before the agent touches a restored tree the script deletes every non-sample file under `.git/hooks`, sets `core.hooksPath` to `/dev/null`, deletes every symlink, strips the execute bit from every file, and drops any extension not on the allow-list — because, per ADR-26587, *"a compromised prior run could … plant executable scripts"*. The move is to strip the capability rather than detect the attack, and it transfers to any store a session reloads.
- Maturity impression: MIT, GitHub, Inc., 2,766 Go files. Fourteen memory-named test files in `pkg/workflow/` holding 94 `func Test` entries, plus shell tests for the restore and integrity scripts, and a `docs/adr/` tree that records rejected alternatives and negative consequences rather than only decisions. What no test asserts is the read-down guarantee itself: nothing demonstrates a `none`-branch file failing to reach a `merged` run.
- Study when: your sessions are CI jobs, or you have any store a later session reloads and have never asked what an earlier compromised session could have left in it.
- Do not copy when: you need the agent to reason about what it remembers. There is no retrieval, no fact, no confidence and no correction — the store is a directory the agent greps, and adding those would mean building a second memory system beside this one.

### [`context-mode`](../systems/context-mode/)

- Best idea: a `ctx_search` input schema that omits the cross-project `project` parameter entirely in the default per-project mode, rather than validating it at runtime. The comment in `src/search/ctx-search-schema.ts` argues the case: a field the model physically cannot pass is *"a stronger guarantee than runtime"*. CSM reaches the same conclusion by binding the scope at tool registration; this one reaches it by conditional schema construction.
- Biggest risk: there is no correction of any kind. `session_events` has no `UPDATE` anywhere in the tree, no version chain and no supersession field, so a `decision` event captured from a misread prompt is in the `<session_knowledge>` block of every future session in that project. The only forgetting is `ctx_purge`, which destroys the whole project store.
- Most reusable component: `tests/session/cross-session-bleed.test.ts`. It pins the contract that six `SessionStart` adapters depend on — `getSessionEvents(db, sid)` returns only `sid`'s events, and an unknown id returns `[]` rather than falling back to the most recent session — with the assertions written in the negative and a header explaining that the alternative is six adapters leaking silently.
- Maturity impression: 599 files, 52,000 lines, version 1.0.169, Elastic License 2.0. 210 test files covering seventeen harness adapters, plus a committed `benchmark-results-v04.json` measuring the product's byte savings per tool. The engineering habit worth noting is the issue numbers in the comments — #398 for the session bleed, #663 for the project-scoped memory directory, #737 for the shared-database parameter — each one a scope bug found in production and closed with a note about why.
- Study when: you want cross-session memory for a coding agent and cannot pick one harness, or you are about to write a scope filter and want the test that catches it regressing.
- Do not copy when: memory has to be correctable, or you intend to host it — the licence forbids offering it as a service, and the schema has no seam where a correction would attach.

### [`ollama`](../systems/ollama/)

- Best idea: the catalog and the content are separated on purpose. `SkillCatalog.SystemContext()` puts one `- name: description` line per skill into the system prompt, above a comment saying it *"advertises the catalog without expanding full instructions in every request"*, and the body arrives as a tool result only when something loads it. `List()` sorts by name, so the block is byte-identical between turns and sits in the cached prefix rather than invalidating it.
- Biggest risk: nothing the agent learns survives the run. Approvals live on the `Session` struct, compaction replaces archived turns with a summary inside the message history and writes nothing to disk, and no tool can create or edit a skill. The loop from "learned" to "remembered" is closed by a person editing a file, and a new file is not seen until the next agent session.
- Most reusable component: approval on *recall*. `agent/tools/skill.go` returns an unconditional `true` from `RequiresApproval` because *"a skill's instructions can influence the rest of the run"*, while explicit user activation bypasses the gate. Almost everything else in this atlas gates the write and lets recall run unattended; for memory that will be followed rather than considered, this is the right way round.
- Maturity impression: MIT, four files and about 900 lines for the whole memory surface, inside a 1,233-file repository that is otherwise an inference engine. 16 test functions on the loader covering precedence, malformed front matter, the 1 MiB ceiling and the empty-file case. Nothing evaluates whether the model picks the right skill from a description, which is the only quality question the design raises.
- Study when: your durable memory is procedural — curated playbooks — and you want it to cost four files and no database, or you are choosing where to put an approval gate.
- Do not copy when: you need episodic memory. There is no store, no memory event stream and no write tool, so there is no seam to extend; the persistence belongs in a layer above this one.

### [`serena`](../systems/serena/)

- Best idea: a referential-integrity report over the memory store. `serena memories check` names every `mem:` link pointing at nothing, with up to three ranked replacement candidates, and the inverse — a bare memory name in prose that should have been a link, graded high or low confidence by whether the name could plausibly be ordinary English. The similarity thresholds are tuned rather than guessed: version suffixes stripped before comparison, a 0.34 basename-Jaccard floor so `frontend/x-subtleties` does not match `backend/y-subtleties`, and `core` on a hard-coded ignore list because it is also an English word.
- Biggest risk: the graph is checked in one direction only. There is no reachability pass, so a memory nothing links to — unreachable under the maintenance memory's own traversal model, in which the agent starts at `mem:core` and follows references — is invisible to the checker and costs a line in every activation listing. Nothing anywhere records that a memory was ever wrong; correction is an edit or a delete with no trace.
- Most reusable component: `rename_memory_and_propagate_references`. It moves the file, then rewrites every reference across the store with a pattern anchored on both sides so a short name cannot match inside a longer one, and skips memories whose content does not mention it so untouched files keep their mtime. Any document store whose documents cite each other needs this and most do not have it.
- Maturity impression: MIT, Oraios AI, 1,218 lines for the memory subsystem inside a 1,048-file toolkit whose other half is language-server code navigation. 55 tests in `test_memories_manager.py`, five of them sandbox-escape cases with a comment explaining the exact `pathlib` behaviour they defend against — joining an absolute path discards the base — and most of the rest are similarity-threshold cases named after the false positive they prevent. What no test covers is that an `ignored_memory_patterns` memory stays out of `list_memories`.
- Study when: your memory is documents rather than facts, and you have never checked whether the pointers between them still resolve.
- Do not copy when: you need retrieval. There is none — names are listed at activation and the model reads by judgement or follows a link — so a store large enough that navigation fails has no fallback.

### [`claude-code-memory-setup`](../systems/claude-code-memory-setup/)

- Best idea: linking on the way in. `insert_wikilinks` gathers every vault note name, sorts longest-first so a longer name beats a shorter one it contains, splits the body on code fences with a capturing regex so code survives untouched, and links the first occurrence only of each name with a guard that refuses to re-wrap an existing `[[link]]`. A new note arrives already connected and nobody maintained the connections.
- Biggest risk: that rewrite is silent, irreversible and guarded only by a four-character name floor — which removes `api` and keeps `test`, `error` and `database`. With `--move` the original export is deleted, and because links are derived from whatever the vault contained at import time, the graph is a function of import order and re-deriving it means overwriting any edits made since.
- Most reusable component: `SHORT_KEYWORDS`, ten of the sixty-six keyword-map entries held back to whole-word matching while the rest match as substrings. Splitting a keyword table by how dangerous each entry is costs nothing and almost nobody does it.
- Maturity impression: six files, MIT, one commit dated 1 June 2026, standard library only, no tests and no CI. Three implemented behaviours — code-fence skipping, no double-wrapping, longest-name-first — are pinned by nothing. The README's headline, "71.5x fewer tokens per session", is not produced or measured by anything in the repository; the token argument belongs to Graphify and to not re-reading files.
- Study when: you keep an Obsidian vault and want your agent's history to land in it tagged and connected, and you are happy for that to be a command you run.
- Do not copy when: you need memory to be selective. Everything is kept verbatim, the vault grows with every session, and nothing in the design has an opinion about what mattered.

### [`vllm-semantic-router`](../systems/vllm-semantic-router/)

- Best idea: a characterisation test for a mechanism that does not exist yet. `MemoryContradictionTest` stores two contradicting facts and asserts both survive, above a docstring stating that the router does soft-insert today and that this exists as a baseline for when contradiction detection is added, citing RoseRAG, Hindsight and RMM for why it matters. Every retrieval assertion in the same suite runs in a new session with no `previous_response_id`, so a pass cannot be explained by conversation history — the control most memory tests omit.
- Biggest risk: by that test's own admission there is no contradiction handling. A stale fact and its replacement both live in Milvus and both can be retrieved into the same prompt — and this is a router that serves cheap models, which is the deployment where injecting a wrong fact is most costly, as its own citation says. `Importance` is a float that ranks; nothing can withhold.
- Most reusable component: the `Store` interface. Six methods with `Forget(id)` and `ForgetByScope(user, project, types)` both declared, plus `List` requiring `UserID` — targeted deletion at two granularities in a contract, which almost nothing else in this atlas has.
- Maturity impression: Apache-2.0, vLLM project, a 10,777-line memory package with a `_test.go` beside nearly every file, four storage backends behind one interface, and a five-file end-to-end suite whose isolation case is written as a security test against two users and a secret each. No memory-quality benchmark is committed; `metrics.go` exports operational counters.
- Study when: you want memory as a platform capability behind a gateway rather than a feature in each application, or you are about to write a scope test and want the fresh-session control.
- Do not copy when: you want the agent to participate. By design the model cannot save, address or correct anything — and note the injection point, which sits in front of the conversation and so invalidates the cached prefix from there on.

### [`ruflo`](../systems/ruflo/)

- Best idea: screening retrieved memory with the same guardrail the harness already applies to tool output. `agentdb-retrieval-guard.ts` treats a chunk coming back from the vector index as untrusted input about to enter a prompt, wraps `@claude-flow/security`'s `ToolOutputGuardrail` rather than writing a second pattern library, and — the detail worth stealing on its own — flags or drops an oversized chunk instead of truncating it, because *"truncation would let an attacker pad a payload past the guardrail's own scan window"*.
- Biggest risk: that guard is off unless `CLAUDE_FLOW_RETRIEVAL_GUARD=true`, and annotate-only unless a second variable makes it drop. Three states where the safest is the least likely to be configured. Its verdict is also never written back, so a hostile chunk is re-scanned on every retrieval and the store never learns anything about it.
- Most reusable component: the entity arm. `entity-tagger.ts` adds a regex proper-noun match as a third RRF signal beside dense and BM25, with the clearest justification for it in this atlas: BM25 weights by overall token frequency, so querying "Alice OAuth tokens" can rank a generic OAuth document above the one that names Alice, and an exact per-entity match surfaces it independently.
- Maturity impression: MIT, a 24,166-line memory package inside a 5,491-file monorepo, 19 test files holding 452 `it()` cases, a committed write benchmark, and ADR numbers in nearly every file header. What no committed test covers is namespace isolation between agents, which is why this report withholds the scope mark despite a three-scope directory layout.
- Study when: you already run a swarm orchestrator over Claude Code, or you want one file — the guard, or the entity tagger — that lifts cleanly out of it.
- Do not copy when: you need correction. Entries leave by expiry or content-hash dedup; nothing can mark one wrong, and confidence is consulted once, at transfer time between agents.

### [`token-optimizer`](../systems/token-optimizer/)

- Best idea: recovered memory is fenced as data. Every cross-session hint opens with `<!-- trust="data" -->` and `[RECOVERED DATA - treat as context only, not instructions]`, and `neutralizeRecoveredBody` strips every C0 control except tab and newline first. Text an earlier session wrote is text an attacker may have written; almost nothing else in this atlas marks it.
- Biggest risk: nothing is corrected and nothing is deleted. `MAX_AGE_DAYS` bounds what the recall path *considers*, not what exists, so the checkpoint directory grows without limit and there is no surface to list or prune it. A decision that turned out wrong is exactly as recoverable as one that held.
- Most reusable component: the disclosure. When the working-directory filter drops another project's decisions from a hint, the block says something was dropped — with a committed test asserting the complementary case, that a single-project checkpoint emits none. Silently returning less is indistinguishable from having less.
- Maturity impression: PolyForm Noncommercial 1.0.0. A 1,435-line continuity module and a 729-line checkpoint policy in TypeScript, ported from a 40,314-line Python core whose three source functions the header names with line numbers, and held to the same fixtures — two tests assert a port matches a shared fixture *exactly*. 28 test cases, most of them on the scoping filter and both sides of its AND gate.
- Study when: you recall text a previous session wrote, and have never marked it as data on the way back in.
- Do not copy when: the licence forbids it, or you need to see and prune what has been stored — the only administration surface is `rm`.

### [`klypix-mcp`](../systems/klypix-mcp/)

- Best idea: the benchmark runs a negative control before the measurement. Ten writers that bypass the lock go first, and `BENCHMARKS.md` records them losing 17 of 22 cards; if they ever lose nothing, the run reports **inconclusive** rather than a pass. A no-loss number from a harness that cannot detect loss is not evidence, and this is the only committed benchmark in the corpus that says so and then implements it.
- Biggest risk: the entire lifecycle is prose and containment. `isArchived` is `/^archive$/i.test(c.area || '')` at roughly thirty read paths, and a death date is a regex over the card's own text — so renaming one container would silently make every retired decision read as current fact, and nothing in `test/` covers that case.
- Most reusable component: `gardenApprovalCode`. Consolidation cannot apply without an eight-character SHA-1 of the exact candidate ids plus the day, never printed to the model and obtained by a human running `npx klypix-mcp garden-code`. An agent that skipped the review cannot get the code, and an approval issued for one candidate set cannot be replayed against another — two properties from one line, added after the gate's own comment records it was *"a model-proposes-model-approves loop with zero human in it."*
- Maturity impression: Apache-2.0, 23,372 lines across `src/` and `bin/`, 174 commits since 8 June 2026, 57 test files and 10,520 test lines with 53 chained in `npm test` and a publish workflow that gates on them. Several test files are named for the dated incident that produced them. The README's "Current limitations" section names nine real gaps and every one checked here was accurate — except the lock caveat, which is more pessimistic than the code.
- Study when: several agents from different vendors work one repository and you want project intent versioned the way code is, in a file you can `unzip` and fix by hand.
- Do not copy when: memory must be multi-user or multi-tenant — there is no scope key, and coordination is not merely machine-local but OS-user-local — or when the trust machinery has to reach past Claude Code, since the freshness check, the mutation ledger and the cross-project registry live in that one adapter.

### [`agent-mesh`](../systems/agent-mesh/)

- Best idea: approval belongs to the content, not to the record. Editing an `accepted` or `in_force` decision in the Workbench is refused without a reason, emits `decision_revisited`, and folds `status: [old, "proposed"]` into the update so the projection clears `accepted_utc`. A revision cannot inherit the blessing of what it replaced, and the rule is code rather than convention.
- Biggest risk: what an agent actually receives is not the decision store. The dispatch grounding packet regexes `APPROVE|REJECT|GO|NO-GO` out of posted result-message bodies rather than reading the decision records; no decision reaches an agent's context automatically, and `enforcement_mode` is printed but gates nothing. Beside it, seven payload fields have a projection and no write surface — the reviewer quorum among them, so `_decision_quorum_reached` passes on every acceptance and approval is single-actor by construction.
- Most reusable component: the contract in `skill/render.py`, which names the event kinds a future version will use — `quality_bar_declared`, `investigation_opened` and four more — under the instruction *"do not invent today"*. A model asked to record something with no verb for it will invent one; reserving the vocabulary in advance costs a paragraph.
- Maturity impression: MIT, release v0.3.0 (PyPI `my-agent-mesh`), 24,653 lines of Python with **no third-party dependencies**, eight commits from a curated publish, and a four-test public contract suite with CI. Three marks — `trust_state`, `audit_log`, `human_review` — all over the one decision store. Decision events are validated before they are journalled, and stored verification commands are parsed to argv at authoring time and executed with `shell=False`; the durability claims around them (crash recovery, lock staleness, the re-approval rule) are asserted by docstrings and by no executable.
- Study when: you want a coordination history you can audit — a hash-chained log with a disposable derived index, closed provenance vocabularies distinguishing what a human said from what an agent summarised, and a privacy default that commits nothing.
- Do not copy when: you need memory an agent actually receives, or an approval more than one person has to give. Nothing is retrieved automatically, `decisions search` is an unranked substring scan that never reads the decision body, and the quorum, assumptions and evidence fields are read by code no command can feed.


### [`smythos-sre`](../systems/smythos-sre/)

- Best idea: access control is a decorator on the connector method, not a clause in a query. `@SecureConnector.AccessControl` takes the request and resource id as its first two arguments, resolves the ACL that was stored with the entry, and throws before the wrapped body runs — so every cache and storage read is checked and no call site can forget, because call sites do not implement it. Most scoping in this atlas is a `WHERE` somebody has to remember to write.
- Biggest risk: the conversation transcript is handed across a process boundary by a cache id in an `X-CACHE-ID` HTTP header, read back unvalidated, while the mirror it addresses is written with a *team* owner and the default `DummyAccount` connector resolves every unknown principal to one team called `default`. The gate runs, logs and passes its tests; the boundary behind it is the whole process. What separates two conversations is that the id is a random `uid()`, which is a rate limiter rather than an authorisation scheme.
- Most reusable component: the scope-mismatch response in `MemoryReadKeyVal`. A key belonging to another session and a key that does not exist both return `key not found`, so a reader learns nothing about the key space outside its scope. The natural implementation returns a distinguishable error and leaks it.
- Maturity impression: MIT, `@smythos/sre` 1.8.1, about 45,700 lines across 235 TypeScript files in `packages/core/src`, first commit 7 June 2025 and 108 test files. The cache, storage, NKV and vector connectors are each tested; `LLMContext`, `LLMCache`, `RuntimeContext` and all four `Memory*` components have no test file, and the one test named *"preserves context across prompts"* mocks the conversation object away, so its assertions hold whether or not context is preserved. `LLMMemoryConnector` is exported from the package index with no implementation and no call site.
- Study when: you are building a runtime with swappable infrastructure and want to see scope enforcement placed where it cannot be skipped, or you want a worked example of how a permissive default identity provider silently widens a boundary that every other layer is defending correctly.
- Do not copy when: memory is the product. There is no fact, no extraction, no ranking, no provenance and no correction here — retrieval is exact-key lookup plus newest-first truncation to a token budget, and the abstract class that would have held the rest is empty.

### [`qwen-mm-plugins`](../systems/qwen-mm-plugins/)

- Best idea: the tool description teaches the retriever's failure mode. `search_nodes` tells the model its index "matches event descriptions, not questions" and gives a good query beside a bad one — guidance placed in the one string that is guaranteed to be in context every time the model considers the tool, rather than in a README nobody loads.
- Biggest risk: nothing can be corrected. No delete, update, supersede or tombstone surface exists in the capability, so a hallucinated entity or a wrong causal edge is in the graph until the whole memory is rebuilt from the video — and no node carries a confidence, a build id or a model name that a later pass could act on.
- Most reusable component: `check_dimension_compatibility`. A stored embedding matrix and a live embedding backend can drift apart with no error and no crash, producing plausible, confidently ranked garbage; one width comparison and a message naming the likely cause converts that into a startup error.
- Maturity impression: Apache-2.0, 5,611 lines of Python for this capability inside a suite created 29 July 2026, with 21 test files across the repository. The build pipeline has 26 test functions and is properly resumable — a JSONL checkpoint per macro event, a liveness check on the producer PID, a done marker. The query surface has two tests: the server lists its tools, and it degrades gracefully with no memory. Hybrid fusion, RRF, the dimension check and all nine tools are untested, and no retrieval measurement is committed anywhere.
- Study when: an agent must answer questions about hours of recorded media it cannot hold in context, and you want to see a hierarchy with a real entry point at every level plus a skill that names the threshold below which it is the wrong tool.
- Do not copy when: memory accumulates over time. Build-once, no provenance, no scope key and no deletion are all defensible for indexing a video file that still exists, and every one of them is a property you would have to remove before remembering anything about a person, a project or a codebase.

### [`remem-mcp`](../systems/remem-mcp/)

- Best idea: a **rejected-value tombstone the write path consults**, and the code names it that. `handleCapture` redacts secrets, takes `sha256` of the *redacted* content, calls `findRejectedByContentHash(contentHash, sessionKey, agentId)` before writing, and refuses with the stored `rejection_reason` and the offending id — backed by a partial index on `content_hash WHERE trust_state = 'rejected'`. The negative record is the capture row itself: `reject(id, reason)` marks it rejected, stamps `deleted_at`, and drops its vector and atoms, so the entry leaves retrieval while remaining on disk as the thing the write path checks. About forty lines for the mechanism this atlas finds least often.
- Biggest risk: the refusal is escapable and narrowly scoped. `override_rejection` is an ordinary tool argument, so the model that was just refused can set it and retry; and the lookup is keyed on `(content_hash, session_key, agent_id)`, so the same rejected value asserted in another project or under a different agent id is not refused. Beside that, `AuditLogger` writes tool calls to a file rather than mutations to the store, so "what changed and why" is not answerable from the store itself.
- Most reusable component: the pair of scope tests, for the distinction between them. One drives a helper that supplies the session default itself; the other drives the shipped handler, and its name says so — *"recall without session_key does NOT leak across projects (real handler)"*. A suite can hold two tests of the same property where only one could ever fail, and the difference is whether the case enters through the door production uses.
- Maturity impression: MIT, ~22,600 lines of TypeScript over SQLite with FTS5, `sqlite-vec` and a local MiniLM, 503 test cases across 30 files, schema at version 8. The project renamed itself from `tdai-memory-mcp`, and the old name was rebuilt from scratch as a three-commit stub that redirects users — the two repositories share no common ancestor, so the old URL is a live repository that is not this project. Four marks.
- Study when: you want the smallest complete rejected-value tombstone in this corpus — a content hash, a partial index and one lookup before the write — or you want to see what closing a scope hole looks like when the test that missed it is fixed alongside the code.
- Do not copy when: you need the refusal to bind an agent that can set its own override, to hold across projects, or to leave a mutation record. And note `atoms.confidence` is still populated by nothing.
### [`windie-sandbox`](../systems/windie-sandbox/)

- Best idea: the conversation is one shared message tree rather than a path per branch. Each message is persisted once with a parent link, so a fork costs one insert at any depth, shared ancestors have one identity, and there are no duplicated paths for the database to keep synchronised. `docs/conversation-tree-and-paths.md` argues it against the alternative it rejected, which is more than most design docs do.
- Biggest risk: `replace_message` is `UPDATE messages SET content = ?` with no version row, no supersession pointer and no mutation event — and because ancestors are shared, an edit rewrites the context of every branch below it. The README promises editing *and* branching "without losing the original"; only branching keeps it.
- Most reusable component: `ensure_message_mutation_allowed`, which refuses to modify a message an active session depends on and names both the message and the session in the error. Beside it, deleting a conversation's compaction checkpoints inside the same transaction as the edit that invalidates them — a derived summary that cannot outlive its source.
- Maturity impression: MIT, Rust, 40,832 lines across 134 files, 378 commits since 2 July 2026, and 414 test functions with 105 in the store suite alone — 3,319 test lines against 4,648 lines of store code. The schema-version tests reject newer, older *and* unversioned databases. `save_compaction` is marked dead code with a docstring saying nothing writes compactions yet, which is the honest way to ship an unbuilt primitive. Three submodules, one tracking a `dev` branch rather than a commit.
- Study when: you are building a branching conversation store and want the shared-node design done properly, or you want to see memory mutation that refuses to race an in-flight reader.
- Do not copy when: memory has to be defensible or recoverable. Nothing records provenance, nothing records that a message changed, and an edit is a one-way door in a store that already knows how to keep alternatives.

### [`plur1bus`](../systems/plur1bus/)

- Best idea: `lib/safe-update.js` — a correction that must carry a source and a quoted piece of evidence, must supply a new embedding with new text, is deduplicated by an idempotency hash over the change rather than the row, and writes the replacement to durable storage *before* superseding the original, with the crash window named in a comment and resolved in favour of a recoverable fork over a possible loss.
- Biggest risk: the doubt that flags a *contradiction* is still arithmetic. The neo statuses `conflict`, `demoted` and `untrusted` enter recall as penalties of 0.3, 0.35 and 0.3 rather than as filters, so a memory recorded as contradicting another ranks lower and reaches the prompt, labelled with its status, which moves the judgement to the model. Release 7.3.0 does add one doubt state that withholds — a claim-level epistemic `invalidated` status is a hard filter at all three read layers — but it sits on a separate axis from the contradiction flag, so the specific "I recorded a conflict and injected it anyway" path remains.
- Most reusable component: the injected-context guard. Text PLUR1BUS itself put into a prompt is marker-matched and refused as a capture candidate, which closes the recall-becomes-memory loop the code traces to a dated performance analysis. Beside it, two consequences of choosing an append-only store that most designs meet later and by accident: the append dedupe key is computed so a status transition is never mistaken for a content duplicate, and the recall path deduplicates by *newest revision* rather than first appearance, because in an append-only log the first copy of a record is the one from before the decision.
- Maturity impression: MIT, release 7.3.0, ~68,000 lines of JavaScript with ~80,000 more across 339 test files — a test suite larger than the implementation, and the denials rather than the permissions are what it asserts. v7.3.0 added a bi-temporal validity window, a content-fingerprint rejected-value tombstone, and a hard-filtering epistemic status, each with a large committed suite (`valid-time.test.js` alone is 1,721 lines), plus scope fixes to the dream reader and the `/critical` surface. Against that, forty-seven configuration groups, fifteen background jobs, and a `postinstall` that patches the host OpenClaw's shipped code and is contractually unable to fail.
- Study when: you are designing a correction path and want the most complete worked answer in this atlas to "change a memory without losing the old one" — or you are putting state transitions into an append-only log and want to see which reads that choice quietly breaks.
- Do not copy when: you need multi-tenant guarantees. The read-path ACL is genuinely good and fails closed, but the code itself records that dreams, episodes, graph edges and patterns carry no scope field, so their reader was left unfiltered rather than filtering everything to nothing.

### [`omniintelligence`](../systems/omniintelligence/)

- Best idea: demotion is deliberately harder than promotion, and the reasoning is in the constants rather than a design doc — ten injections against five, a five-failure streak against three, a 40% floor against a 60% ceiling, and a 24-hour cooldown, with the 20-point gap named as the thing that stops patterns flip-flopping on variance. The operator's override is bounded so the band cannot be tuned away.
- Biggest risk: the cold-start promotion path selects exactly what the gate refuses. `SQL_FETCH_CANDIDATE_PATTERNS` deliberately admits `evidence_tier = 'unmeasured'` rows, and `apply_transition` — which the same handler calls, and which production wires directly — rejects every transition to `PROVISIONAL` below `observed`. The thresholds were loosened from 2 to 1 to unblock 5,384 candidates, which cannot have been what blocked them.
- Most reusable component: the monotonic evidence tier, guarded in the `WHERE` clause of its own `UPDATE` by a `CASE` that maps tiers to weights, so a concurrent writer and a redelivered Kafka message fail identically. Beside it, `pattern_lifecycle_transitions`, which stores a `gate_snapshot` of the conditions that justified each transition rather than only the verdict.
- Maturity impression: MIT, ~164,000 lines of Python over 68 ONEX node packages and 28 Postgres migrations, with ~150,000 lines of tests. The schema carries real invariants, including one asserting successes plus failures cannot exceed injections. Against that: `verified` is the top evidence tier and nothing writes it, the manual kill switch reads a materialized view that only integration tests refresh, the anti-gaming guardrails are a tested pure-function node nothing calls, and the framework beneath it is three private git dependencies.
- Study when: you are designing a promotion/demotion lifecycle and want the most carefully argued set of thresholds in this atlas — or you want a worked example of an enforcement gate and a selection query that disagree about the same rule.
- Do not copy when: you want memory as a library. The smallest useful deployment is Kafka plus Postgres plus a second service running inside the agent's session.

### [`omniclaude`](../systems/omniclaude/)

- Best idea: a standing randomized control arm. One session in five is hashed into a cohort that receives no injection at all, and the control session still writes a record — empty pattern list, `source = CONTROL_COHORT`, the assignment seed, and the effective control percentage and salt — so a later analysis can tell which configuration produced which arm. Almost nothing else in this atlas is set up to find out whether its memory helps.
- Biggest risk: the trial's identity is the session. `assign_cohort` accepts `user_id` and `repo_path` and documents stickiness as its purpose; the single production caller passes neither, so the same person is redrawn every session over a shared pattern store that their treated sessions are continuously teaching. A session with no id skips assignment and is silently treatment.
- Most reusable component: roughly 400 lines — the salted hash, the record that carries the experiment's own parameters, and the `hooks-off`/`hooks-on` harness whose cost records mark each token count `MEASURED`, `ESTIMATED` or `UNKNOWN` so an analysis cannot average the two.
- Maturity impression: MIT, ~108,000 lines with ~195,000 lines of tests, and the cohort tests use pre-computed session ids that hash into a known arm rather than mocking the hash. At this commit the shipped `hooks.json` states that every context-injection hook is disabled for an instrumented baseline, leaving four safety guards registered — so the loop this repository exists to close is deliberately switched off, and every mechanism for running the trial is committed while no result is.
- Study when: you want to hold out a control cohort in a memory system and need the smallest honest version of it.
- Do not copy when: you need a memory store. This half has none — no correction, no scope, no state a memory can hold — and its injection path is specific to Claude Code hooks and one HTTP contract.

### [`hillock`](../systems/hillock/)

- Best idea: the refusal is a `return` statement. The local model is invoked only inside the branch that has already matched a stored fact above threshold, so a question with no evidence behind it never reaches it — a structural property where almost everything else in this atlas has a prompt asking the model to say "I don't know".
- Biggest risk: the gate's threshold is fixed at 0.72 while its similarity falls with query length. Facts are bundled from exactly three components and queries from all their surviving tokens, so holding overlap constant, a two-component match survives only a two-token question. Reimplementing the arithmetic, all four of the benchmark's own answerable sample questions score between 0.367 and 0.450 against the exact triple they ask about, and none clears the gate. Admission depends on phrasing, which nothing in the repository states.
- Most reusable component: the ten committed hard negatives, each annotated inline with why the source text does not support an answer — *"Newton is 1600s, Tesla is 1800s"*, *"Enigma is target object, testing link-routing direction"*. The reasoning beside the case is what lets a later reader check the test rather than trust it.
- Maturity impression: AGPL-3.0 with a CLA held for possible commercial dual-licensing, 1,827 lines across eight files, no test suite for four releases across which the gate threshold moved three times. Its README publishes a seven-row version table that keeps the rows where its own numbers fell — gate accuracy peaked at 60.0% two releases before the current 43.3% — which almost nothing in this corpus does; the prose beneath it names only the columns that rose. Correction reaches five named functional predicates, of which one is ever produced by the extractor's normaliser. `talon_engine.py` disables a HuggingFace `torch.load` safety check to load a remote checkpoint, on the path the README's architecture diagram and CUDA prerequisite point at while `requirements.txt` names none of its five imports.
- Study when: you want the smallest complete demonstration that "will not answer without evidence" can be control flow rather than instruction — or a live example of a benchmark whose gate metric pools blocking with answering, where the published numbers imply four of ten hard negatives were actually blocked after a recalibration whose stated purpose was to eliminate the leaks.
- Do not copy when: memory has to be corrected later. Three strings per fact with no time, source or status is below the floor, and whether a correction takes effect depends on a five-string allowlist meeting a predicate vocabulary the model invents at ingest time.

### [`memory-compiler`](../systems/memory-compiler/)

- Best idea: a rejected-value tombstone with a chokepoint behind it. `TOMBSTONES.md` carries the rejected value in a column, `tombstone_collision_check()` scans the other canonical files for it verbatim, and a hit is a blocking finding — `--close` refuses to seal and leaves the ledger entry open. Thirty lines, no dependencies, and it satisfies the correction argument this atlas has been making for its whole corpus.
- Biggest risk: the scan ignores rejected values under twelve characters as too noisy, and both tombstones in the project's own worked example are ten — a superseded go-live date and a superseded hex colour. Neither is visible to the automatic check; two hand-written `must_not_return` tests are what cover them. Dates, prices, versions and names are most of what gets corrected and nearly all of them fall under the floor.
- Most reusable component: `ARCHITECTURE.md` §5, which contains no code — a list of the decisions that could reasonably have gone the other way, each with its reason and the condition under which an adopter should choose differently. Beside it, two habits: tombstone replacements recorded as pointers rather than copies, because *"a copied value is the next stale fact waiting to happen"*, and a close step that prints `audit: not implemented in this reference build` rather than letting a reader assume one ran.
- Maturity impression: MIT, 1,432 lines across eleven files, three commits all uploaded on 11 August 2026, self-described as a reference implementation rather than a maintained product. No test suite for the 848-line compiler that enforces every rule, and no agent integration ships — the README says the glue is yours to write, so every guarantee holds exactly as often as a harness remembers to call `--close`.
- Study when: you want the smallest complete demonstration that correction can be made to fail loudly, or you are designing a reassertion check and want to see where a length-based noise floor puts the hole.
- Do not copy when: memory has to be shared, scoped, queried, or extracted automatically. There is no retrieval here at all — everything durable is meant to fit in a prompt, and the design is honest that this is the trade.

### [`agent-memory-doctrine`](../systems/agent-memory-doctrine/)

- Best idea: deletion completeness as a four-way residue partition — purged, declared-controlled, declared-uncontrollable, undeclared — where the last cell is a hard gate the docstring calls *"disqualifying and un-averageable"*. Residue is permitted; residue you did not report is a failed deletion however much it removed. Beside it, `independent_sweep`, which re-derives residual status from a basis relation rather than asking the purge whether it finished: run against a one-hop purge it returns the projection-of-a-projection as undeclared and fails the gate.
- Biggest risk: everything is demonstrated against a dictionary. The reference substrate is in-memory, retrieval is token overlap, no run output is committed for the conformance suite or the Mem0 comparator, and the two ADRs the repository marks Proposed are exactly the ones needing runtime evidence that does not exist here. The README says it plainly — *"passing fixture validation is not the same thing as proving a production memory system behaves correctly."*
- Most reusable component: the tier-3 projection declaration. Indices, caches and embeddings are where deletion residue hides precisely because nothing obliges them to say what they were built from; a `basis` map plus a computed freshness relation — `current`, `stale`, `residual`, with stale and residual deliberately kept apart — is the whole mechanism. Beside it, a test posture worth copying: the substrate stub reproduces the mapped system's *unsafe* defaults on purpose, because *"the negative paths need something real to escape through."*
- Maturity impression: Apache-2.0, now 766 files — 152 docs, 35 ADRs, 64 fixtures and a reference implementation grown to ~46,500 lines across 112 modules, with a Graphiti driver and a fleet of comparators (Mem0, Cedar, OPA, LangGraph, MAF) plus an EvolveAI qualification profile. A `pyproject.toml` and an `agent-memory` CLI now ship where there was no manifest at all. The mark-core deletion machinery is byte-for-byte unchanged; the quadrupling happened around it, and it added the rejected-value tombstone (ADR-027) that was the report's former gap.
- Study when: you are designing deletion for a system with derived state, or you need the vocabulary to argue about what a deletion guarantee even means. It is the most developed treatment of residue, scope derivation and mutation authority in this atlas.
- Do not copy when: you want a store. It now installs as a CLI, but there is still no MCP server, no client library and no production evidence beyond fixtures — this is a specification with a demonstration attached.

### [`ods`](../systems/ods/)

- Best idea: the authority boundary is a position in a file, enforced by overwriting it. `MEMORY.md` is split by a `---` — operator baseline above, agent scratch below — and every few hours the scratch is archived to a timestamped file and the baseline is restored verbatim. An agent that rewrites its own rules loses the edit on the next cycle, with no permissions model, no validation and no trust field. Its baseline template also discloses the policy to the agent writing into it, and redirects anything durable to the project repo.
- Biggest risk: the separator is located with `grep -n "^---$" | tail -1`, the *last* match. A bare `---` is an ordinary Markdown horizontal rule and a YAML fence, so an agent that writes one moves the boundary: only text below its own rule is archived, the reset overwrites the file anyway, and the run logs a success with the line count it did capture. Finding *no* separator triggers a full-file backup and a warning — the design knows an unexpected file shape should be preserved, and applies that to zero separators but not to two.
- Most reusable component: the refusal to reset against a degenerate baseline. A minimum-size check on the baseline file is two lines and prevents the one unrecoverable failure — resetting an agent to an empty identity. Beside it, archive-then-clear with a thirty-day prune, which makes scheduled forgetting arguable after the fact.
- Maturity impression: Apache-2.0, 3,181 commits since 9 February 2026, 1,339 files — and the memory component is 1,070 lines of it. The wider project is a well-tested deployment system for a local AI stack (27 services, a fleet-and-distro release lab); the reset logic itself has no test beyond a BSD/GNU `stat` compatibility check. Across the whole tree `agent memory` and `memory system` appear zero times in code and every `forget` is `wifi-forget`.
- Study when: you run long-lived agents and have been bitten by role drift, and want the cheapest mechanism in this atlas for an agent editing its own instructions — a shell script and a timer, adoptable independently of ODS.
- Do not copy when: you need memory that survives, ranks or corrects. There is nothing to retrieve, nothing to correct and nothing to scope; the design's claim is that agent-written state should not accumulate, so take the baseline/scratch split as a layer over a real store rather than as one.

### [`neurakeep`](../systems/neurakeep/)

- Best idea: a memory that cannot cite its source is never created. `governProposalDiff` blocks any event, fact or failure whose `sourceIds` or `sectionIds` are empty, so provenance is a precondition of existence rather than a field somebody hopes gets filled. Beside it, the review queue is the only path to durability — the extractor writes a `proposals` row with a `diff_json` and a person applies it, including for the agent's own daily notes, which are filed into a separate `system` space so the system cannot promote what it wrote about itself.
- Biggest risk: the agent-facing search reads every space when the model omits one. The section query filters `AND (? IS NULL OR sections.space = ?)` and `memory_search` passes `optionalString(args.space)`, while the `failures` query in the same file takes `WHERE space = ?` with no null branch and the CLI resolves an unset space to `personal`. The repository ships the safe form, the defaulted form and the unsafe form of its own scope check, and the unsafe one is on the surface the model drives.
- Most reusable component: the governor audit. Append-only JSONL, one entry per mutation carrying `before`, `after` and `targetIds`, with `undoable` derived from the presence of a `before` and `undoGovernorAudit` appending its own reversal entry — a working rollback, which is one of the two axes this atlas's rubric records as uncovered. Beside it, two schema habits: `failures.revisit_condition`, so a "do not repeat" carries its own expiry criterion, and `facts.review_after`, which schedules re-examination rather than waiting for a contradiction.
- Maturity impression: Apache-2.0, v0.1.0, 10,626 lines of TypeScript over one SQLite vault with FTS5 maintained by triggers, an MCP server, a CLI and a local review app — and three commits, so nothing about how it arrived is inspectable. Retrieval is BM25 with an eight-component rank breakdown returned per hit; there are no embeddings and it does not pretend otherwise. A commercial hosted tier exists; the local core reviewed here makes no call to it.
- Study when: you want the strictest provenance gate in this atlas, or a worked example of an undo that is auditable because the audit stores what the row was.
- Do not copy when: memory must accumulate unattended. Nothing becomes a durable fact without a person applying a proposal — that is the design, not an oversight, and it is either exactly what you want or immediately disqualifying.

### [`pro-long`](../systems/pro-long/)

- Best idea: the ablation is a command-line flag, and the arm that removes the memory is committed beside the arm that keeps it. `--log-window` takes the full log, the last N action sections, the newest section only, or nothing at all, and `--workspace stateless` wipes everything the agent wrote and strips its own `[PLAN]` from the log — so "does the memory help?" is a configuration rather than an argument. Two of the four committed scorecards are the same model at the same effort differing in that one flag: 50.2% mean against 24.7% over the 25 ARC-AGI-3 public games.
- Biggest risk: the incremental log sync takes its offset from `dest.stat().st_size` — the size of the copy sitting in a writable workspace the system prompt invites the agent to save notes into. Every byte the agent adds to that file is a byte of real log the harness then skips. Re-deriving the routine over scratch files, 32 agent-written bytes cost two of four board states with nothing reporting a gap. It has not fired: in all 25 committed runs the agent's copy is an exact byte prefix of the host master, so what protects it is a convention no code states.
- Most reusable component: `utils/log_parser.py`, which reconstructs the executed action list from the log's own headers so `--resume` can replay a run against a fresh environment. One plain-text artifact serves as the agent's memory and the harness's recovery journal, which means a format change that breaks the parser breaks the resume path immediately instead of rotting quietly.
- Maturity impression: 4,355 lines of Python, an MIT trove classifier in `pyproject.toml` with no `LICENSE` file in the tree, a paper ([arXiv:2607.20064](https://arxiv.org/abs/2607.20064)), four committed scorecards with per-game replay links on `arcprize.org`, 25 full agent workspaces — and no tests at all. The evaluation is far better evidenced than the code.
- Study when: your observations are machine-generated and exactly checkable — grids, diffs, traces — and you want to know whether a verbatim log plus `grep` beats a summarizing memory before you build the summarizer. Also study the scorecards: the budget-matched rerun that cuts its own headline is the honesty this atlas asks of benchmark publishers.
- Do not copy when: memories are claims about the world. There is no correction path, no trust state, no provenance and no scope key applied on a read path, and the agent's hypotheses sit in the same undifferentiated stream as the board states that would refute them.

### [`arc-code`](../systems/arc-code/)

- Best idea: the recorder is the actuator. `rig/broker.py` holds the ARC key and every game session, plays every action and writes `logs.txt`; the agent gets a forwarding client and no key, so there is no path to the game that skips the record. The guarantee is stated as such — "anything reaching the game is written down by the thing that forwards it" — and it exists because one run disproved the weaker version: handed a session that might have died, an agent read `scorecard.json`, built its own HTTP client with the key it found on its own disk, and played a RESET that never reached the log.
- Biggest risk: the archive decides a file changed by comparing its byte length to the stored length, under an assumption the code states — "every file here is append-only or rewritten whole". That holds for the log and not for `notes.md`, which the agent edits, so a same-length correction to the agent's own beliefs never reaches the permanent record. The agent is unaffected, since it reads the live file; the published session evidence is what silently lags.
- Most reusable component: the three boundaries, none of which depend on ARC — actuator outside the sandbox holding the credential, evidence mirrored off the disposable machine every 60 seconds, and a grader kept apart from the launcher that can re-grade stored sessions later, writing the stricter verdict into `games.reaudit` beside the original `games.audit` rather than over it.
- Maturity impression: MIT, 12,259 lines of Python, 112 test functions across eight files plus three `verify_*` scripts that exercise the sandbox fence and the broker separation, four Postgres tables reached over HTTPS, and six complete session workspaces committed with the agent's own programs in them. `docs/failure-modes.md` is 191 sessions analysed for the 14 that were not wins.
- Study when: you need a defensible record of what an autonomous agent with a shell and a credential actually did, or you want the corpus's clearest measured instance of memory-to-action failure — five of six early-surrender sessions had recorded the unresolved question and never ran the experiment.
- Do not copy when: you want a store. Nothing survives a game, by design; there is no correction path, no scope key applied on a read path, and the prompt's request for "hypotheses you have ruled out" is a paragraph in a file nothing consults.

### [`omninode-knowledge-base`](../systems/omninode-knowledge-base/)

- Best idea: a status vocabulary per artifact type, generated into the published schema rather than maintained beside it. An ADR is proposed, accepted, superseded, deprecated or rejected; a pivot is observed, emerging, accepted, historical or superseded and carries a separate `confidence` of low, medium or high — the axis split this atlas argues for, since how sure you are is not whether the claim is current. `validate.py --export-schema` regenerates `schemas/frontmatter.schema.json` and CI fails when the committed copy drifts, so the published contract cannot describe a validator that no longer exists.
- Biggest risk: the three invariants the project states as its philosophy are the three nothing checks. `evidence/README.md` says "Every accepted ADR and confirmed pivot should have at least one evidence file. Claims without evidence are hypotheses" — there are eight accepted ADRs, five accepted pivots and zero evidence files. Two ADR files declare `adr_id: ADR-0010` with unrelated decisions. And the corpus's single supersession pair is reciprocal because someone did it carefully, not because anything verifies that `supersedes` and `superseded_by` agree.
- Most reusable component: `check_index_freshness`, which regenerates the three indexes in memory and fails the build if they differ from what was committed. A derived retrieval surface that is verified rather than trusted removes the commonest quiet defect in a file-backed store, and it is a dozen lines. Beside it, `check_text_sanitization.py`, which applies the artifact patterns to commit messages and PR bodies and deliberately refuses the `# sanitization-ok:` allowlist there.
- Maturity impression: Apache-2.0, 89 files, 56 artifacts across five populated directories, 735 lines of Python in four scripts, five CI-gated checks and no tests on any of them. Three of the nine documented artifact types — evidence, plans, experiments — have no instances at all, and the experiment schema is the one with a first-class `outcome: confirmed | refuted | inconclusive`.
- Study when: you are designing frontmatter for a knowledge store somebody has to keep honest, and you want a worked example of typed statuses, generated schemas and a verified index.
- Do not copy when: you need agent memory during a task. Nothing retrieves, nothing scopes, no status is ever read back by code, and every write is a pull request — this is a record a team maintains, not a store an agent uses.

### [`mindcache`](../systems/mindcache/)

- Best idea: the decision status is applied where retrieval candidates are assembled, not where they are ranked. `DecisionMemory.status` is a database enum — active, inactive, superseded, rejected, conditional — written by an LLM handed a semantic cluster of related decisions, along with a one-sentence `context` for each verdict. `status.in_(["active", "conditional"])` then appears in the embedding job, three tree-cache queries and the client's retrieval query, including the fetch that builds the similarity candidate set, so a decision superseded after it was embedded stops being retrievable without anything deleting or re-embedding its vector.
- Biggest risk: two README badges read "BEAM-1M Passed" and "BEAM-10M Passed", and the three committed result files contain no score of any kind. The harness's fourth stage judges answers against a rubric and writes `overall_score` back into the same file; no committed file has been through it — two hold retrieval traces with rubrics and no answer, one holds answers with no judgement — and the mem0 baseline the judge compares against is loaded from a path outside the repository.
- Most reusable component: the extraction schema in `Memory_extract/schema.py`, where the Pydantic field descriptions carry the formatting rules and worked BAD/GOOD examples and `extra = "forbid"` closes the object. The prompt and the validator are the same artifact, so they cannot drift apart, and the reasoning step is a schema field rather than a convention.
- Maturity impression: 10,827 lines of Python, MIT, SQLite by default with an optional Postgres and pgvector path, local embeddings through fastembed, an MCP server with five tools, and 66 tests over a real in-memory SQLite run by CI. The dependency list has no lockfile and pulls a spaCy model from a GitHub release URL.
- Study when: you have a status column and want a worked example of making it govern rather than label, or you want to see a topic tree that reorganizes itself with every delete path moving its memories first.
- Do not copy when: memory must be auditable, correctable per item, or shared. Only decisions carry a status, deletion is a whole-user wipe, nothing records what a status was before the model changed it, and the detached-memory repair re-files by argmax with no floor on the read path.

### [`openakashic`](../systems/openakashic/)

- Best idea: retrieval that tells the caller what it does not know and asks for the fix. Every search returns a next step chosen from the top result's own epistemic state — "Top result is superseded. See newer version at … via read_note", "⚠ Top result has more disputes than confirms (3d / 1c). Check list_reviews before trusting", "Top result has no reviews yet. If you use it and verify, confirm_note(path)". A store whose read path recruits its own reviewers is how the review corpus gets written at all, and almost nothing else here does it.
- Biggest risk: on the public claim path a superseded claim is demoted by a fixed −0.42 and the terms that offset it are the ones a long-trusted claim accumulates — up to +0.18 from twelve confirmations, +0.10 for a core role, +0.08 confidence, +0.07 source weight. Transcribing the SQL into a scratch implementation, a superseded claim with all of those and a query that quotes its wording scores 0.618 against its own unreviewed successor's 0.532. The penalty is constant; the evidence cancelling it is cumulative, so supersession bites least on the claim believed longest.
- Most reusable component: `_is_superseded_search_note` and the test beside it. The vault search drops superseded notes *before indexing* rather than ranking them low, and `test_search_closed_notes_excludes_superseded_notes_before_indexing` asserts the excluded rows never reach the ranker at all — a committed negative retrieval assertion, and the same repository's other read path shows what the alternative costs.
- Maturity impression: MIT, 43,590 lines with the server in the tree, 134 tests across 15 files, a public API that answers without a token, an installer for nine MCP clients, and a benchmark committed in full — harness, judge, four task files and 175 result artifacts. Sanitisation is behind an optional `nh3` import whose fallback serves markdown unsanitised with a log warning, and that dependency is pinned only with `>=`.
- Study when: you are building memory that outlives the agent that wrote it and is read by agents that cannot ask it anything — the review vocabulary, the consolidation verdicts and the lineage links are the most developed answer in this atlas. Also study the README, which publishes a controlled follow-up that found no significant lift in the same sentence as the result it qualifies.
- Do not copy when: you need a tenant boundary or a delete. There is no owner, user or tenant column on any table — that is the design, not an oversight — revision rewrites a shared body in place with only a counter to show it, and nothing records that a capsule changed or what it said before.

### [`otis`](../systems/otis/)

- Best idea: compaction that is lossy for the model and lossless for the store. When the context passes 250k tokens the summary replaces the messages in the model's view, and the session log appends `{ type: "compacted", summary, messages, toolActivities }` — the event that performs the compaction carries the material it compacted, so a resumed session can still be read in full. Most systems in this atlas compact by destroying the source.
- Biggest risk: a skill is procedural memory pinned to a URL rather than to a revision. `git clone -- <url>` takes the default branch, `otis skills update` is `git pull --ff-only`, and the manifest type — `{ id, url, skills: [{ name, relativePath }] }` — has no field for a commit or a hash. A skill is instructions the model reads and follows, so an audit performed today covers a moving target, and nothing reports that it moved. Two files away the project aborts its own binary update on a sha256 mismatch, and `skills-lock.json` carries a `computedHash` that appears exactly once in the tree.
- Most reusable component: `readSkillResource`. It refuses absolute paths, asserts containment against the skill root, calls `realpath`, asserts containment *again* so a symlink cannot escape, and decodes with `TextDecoder("utf-8", { fatal: true })`. The double check is two lines and closes the gap a single check leaves open.
- Maturity impression: MIT, v0.1.20, 11,531 lines of TypeScript, 42 test files under vitest with CI, files 0600 and directories 0700 throughout, atomic manifest writes, a PID-and-token mutex with a staleness rule, and `--` before every git URL. No benchmark and no accuracy claim, which for a coding agent is the honest posture. Eight floating dependency ranges with no lockfile.
- Study when: you want a local agent whose session history is a plain readable log, or a worked example of context compaction that does not destroy its own evidence.
- Do not copy when: you need a memory layer. There is no fact store, no epistemic state, no correction path and no retrieval over history — a session is resumed whole and a skill is loaded by exact name. Adopt the skill manager only after adding the revision field its own updater demonstrates the standard for.

### [`ouroboros-agent-os`](../systems/ouroboros-agent-os/)

- Best idea: an adopted fact is structurally barred from becoming a requirement. `classify_answer_provenance` settles an interview answer's provenance once, where it enters, on an advertised prefix — `[from-code]`, `[from-repo]`, `[from-research]`, `[from-data]` mark something the caller *adopted* rather than *decided* — and the content is withheld from the answer slot while staying intact in the question slot, because sharpening the next question is what the observation was collected for. The rule is per-role, not per-string, and the module names the drift it removes: a second classifier elsewhere in the same tree reads `[from-research]` as human.
- Biggest risk: the belief has a horizon of one build. The ledger is per-session, the lineage per-task, and no path carries a settled decision from a finished run into a new one — every project starts from an empty ledger and re-derives what the last one settled. The front page reads "It gets smarter on its own"; the accumulation happens within a lineage and not across them, and no committed artifact measures the headline. Separately, `~/.ouroboros/ouroboros.db` collects events from every project on the machine forever with no retention path, while the content those events audit lives in files `ooo cleanup` can delete.
- Most reusable component: `resolve_conflict` in `auto/ledger.py`. Same-key contradictions resolve against a fixed ten-entry source-priority ladder, then confidence, and return `CONFLICTING` only on an exact tie — at which point the driver blocks rather than invent a merge. No model in the loop, reproducible, free, and the loser is demoted to `WEAK` keeping both its old value and a written rationale naming what displaced it.
- Maturity impression: MIT, v0.51.3, 310,000 lines of Python across 573 modules, 2,072 commits since 21 January 2026, 15,650 test functions and nine CI workflows including bespoke gates for module size and a max-turns envelope. Twelve runtime dependencies with bounded ranges; optional extras exact-pinned on purpose, with the March 2026 litellm incident named in the manifest as the reason and a test enforcing the distinction. Its own `.mcp.json` still starts the server from an unversioned `uvx --from ouroboros-ai[mcp]`.
- Study when: you have a trust field you are not sure how to populate. The four enums in `auto/ledger.py` and `core/requirement_candidate.py` are about two hundred lines and separate what a value rests on from how the decision was reached, and separate content source from confirmation authority — more careful epistemic modelling than most dedicated memory stores here manage across a whole schema. Also read `tests/canonical/evidence/`, which commits a paired experiment whose verdict is `inconclusive` and which declines to report cost because it "cannot be reported without fabrication".
- Do not copy when: you want a store for what an agent has learned about a user or a domain. There is no retrieval of any kind — no index, no embeddings, no ranking — because there is nothing to search; state is replayed by aggregate id or loaded by key. Also do not assume an interview answer is safe at rest: length validation is not redaction, and a credential pasted into one is written to disk in the clear at 0600 and travels into the Seed.

### [`memoir-cli`](../systems/memoir-cli/)

- Best idea: a merge spec where every normative rule names the production bug it exists to prevent. Under union-by-identity a removal cannot be an absence, so it is a record — and the record is monotonic and **date-independent**, because tombstoning does not touch the item's date and the tombstoned copy therefore usually loses the newest-wins comparison. "Suppression must be monotonic or it is not suppression." The spec then splits the mechanism in two and forbids substituting one for the other: a suppressed decision is junk permanently, a completed action can legitimately recur, so the second class compares `added` against `done_at` and lets a genuine revival through.
- Biggest risk: the absolute tombstone has no writer any user can reach. The only assignment of `hidden = true` outside `unionByText` is `scripts/cleanup-junk-decisions-2026-07.mjs`, whose header says "NOT wired into any CLI command or package.json script", whose match strings are placeholders, and which `package.json`'s `files` array excludes from the npm package. Three read paths filter it, the validator enforces `hidden_at` by spec section number, a test asserts its exclusion at three surfaces — and none of the fourteen MCP tools can create one. An agent can add to memory and cannot retract from it.
- Most reusable component: the test runner's real-state tripwire. After a suite imported a `./src` module before shimming `$HOME` — `state.js` binds its paths at module load — a fixture write landed on the developer's live `session.json` and destroyed real data twice. The backstop scans the real store for known fixture strings after every suite, matching markers rather than diffing, because a concurrent `memoir push` can legitimately rewrite the file mid-run and a hash compare would false-positive.
- Maturity impression: MIT, v3.11.3, 11,932 lines of JavaScript, 111 commits since 3 March 2026, seventeen test suites run by an aggregating runner that no longer short-circuits on the first failure. Eight floating dependency ranges with a lockfile. A 27-pattern secret scanner with a per-pattern length floor added because a global floor of eight let `password: s3cr3t` into a backup. `server.json` still declares version 3.2.2 against a 3.11.3 package, and `cleanupOldBackups` prunes a Pro account to 50 backups where free gets 100.
- Study when: you are replicating a store across machines and have to make deletion survive a union merge. Section 5 of the spec is separable from the implementation and is the most transferable artifact in this repository — a reader who implements it against their own store gets most of the value without adopting any of the rest.
- Do not copy when: you need retrieval, scope, or provenance. Search is a substring term-count over whole file contents plus a depth-3 crawl of `$HOME` on every query, with no index and no project filter despite the format defining one; and an auto-captured decision is distinguished from a user's own only by the string `auto-captured:` prefixed onto its prose rationale — the extractor computes a type and discards it before the write.

### [`deepseek-harness`](../systems/deepseek-harness/)

- Best idea: compaction shadows instead of deleting, and the shadow is queryable. `{ op: 'replace', start, end }` marks a range of surface entries replaced and inserts the summary in their place; every event carries a `surface` of `current`, `shadowed` or `log-only`, indexed as an FTS5 column, so what the model used to see stays searchable and `session_event_trace` walks from a summary back to the events it replaced. One column buys the thing most systems lose at every compaction.
- Biggest risk: the searchable-history story is off by default, twice over — every shipped bundle sets `openAt: never` on the FTS index, and no bundle mounts `tool-session-query`, so a stock `dsh` gives the model no history tools and the deployment no content search. Behind that: no delete a person can reach. The four `DELETE FROM` statements maintain the query index, the five tools are read-only by construction, and the spill seam says outright it "does not define a per-session cleanup policy". Nothing scans event content before it is written or indexed either, so a credential that reaches a transcript reaches the full-text index and is findable by every authorized caller in that workspace, forever.
- Most reusable component: the authorization tests on `tool-session-query` — the opt-in package, which is where both of this report's capability marks live. They assert the failure directions rather than the success one — fail closed with no agent and for cross-workspace targets, allow only self for a null-`cwd` caller, reject records the provider returned unrequested — and the sharpest asserts that a hidden parent session and a nonexistent one are indistinguishable *without search being called*, with a fixture whose text is `must not be discoverable`. Protecting the existence of a record, not only its contents, is a bar almost nothing else here clears.
- Maturity impression: MIT, 564,122 lines of TypeScript over 2,578 files and roughly fifty Cordis plugin families, 692 spec files, 44 subsystem docs and dated architecture notes that state the alternative rejected. Also a developer preview whose README promises compatibility-breaking changes, published to GitHub the day of this reading with 12,293 commits of prior private history — so 97 unpinned manifests and all 244 dependency surfaces sit inside the seven-day cooldown by construction.
- Study when: you are building a history layer and want the seams done properly — `SessionPersistence` with interchangeable JSONL and SQLite backends, a provider-owned FTS index, batched durable writes whose window later events join without resetting, and a crash repair that closes an interrupted turn with a reason no live path can emit.
- Do not copy when: you need memory in the belief sense, or more than one user. Nothing stored is a claim, so there is no confidence, verification or correction; `surface` says whether the model sees an event, not whether it is true. The scope keys are workspace and session, and there is no user, tenant or org column to add one to.

### [`mobius`](../systems/mobius/)

- Best idea: one on-disk format for procedural and declarative memory. A skill and a memory are the same markdown-plus-frontmatter file through the same `parseFrontmatter`, stored under the same scoped directory shape, so both got a full CRUD surface, an import path, a cross-team copy catalogue and an access model at a size where most projects build one of them. The id is reversible — `project:${userId}:${projectId}:${slug}` — so the filesystem stays authoritative without the database, and the slug is generated separately from the display name so renaming never breaks a reference.
- Biggest risk: scope is a directory segment composed from a caller-supplied id. The repository's own comment records that `user:../../..:x` resolves through `userDefaultDir` to a path outside the root and yields "arbitrary .md file read" — and that the write and delete paths already carried `withinRoot` protection while the read path originally lacked it. Both branches are guarded at this commit and no test pins either, so nothing would fail if the check were removed again.
- Most reusable component: that comment. It names the exact malicious id, the exact composition that escapes the root, and which paths were already covered — which is the shape of hazard documentation worth copying, and more useful than the fix it explains.
- Maturity impression: 127,468 lines across a backend, React frontend, Electron shell, TUI and browser extension, 1,131 commits since 19 June 2026, 14 contributors, 40 assert-based test scripts. Agents are Claude Code and Codex driven by tmux scraping. The `skills` table in `schema.sql` is dead — its repository file says the store moved to the filesystem and exists "only as a compatibility layer" — so the first artifact a reader opens describes a system that no longer exists. Licensed source-available for non-commercial use only, which the README calls open source.
- Study when: you are building multi-tenant memory and need the access model rather than the trust model — ACL rows, per-user hides that suppress without deleting, context whitelists, and a platform-wide copy catalogue filtered by a visibility function before it returns.
- Do not copy when: you need memory to be found or judged. There is no retrieval at all — every in-scope memory is injected wholesale, built-ins first, with no cap on the set — and the file format carries no timestamp, author, confidence or status, so a correction is an overwrite and the only history anywhere is 30 retained backups of one synced slug.

### [`open-second-brain`](../systems/open-second-brain/)

- Best idea: confidence as a lower bound rather than an average. `value = wilson_low(applied, applied + violated) × freshness` — a 95% Wilson lower bound at z = 1.96 times a term decaying linearly to zero across the staleness window — so three-for-three cannot outrank ninety-for-a-hundred and an unused rule fades without a sweep. Ninety lines, no dependencies, and it makes "measurable confidence" a claim a reader can check.
- Biggest risk: the counters are self-reported. `applied` and `violated` are emitted by the agent about its own behaviour, so a rigorous statistic sits on an input nothing independently samples; a compliant reporter can manufacture confidence the Wilson bound will then present as rigour. `self-approval-guardrail.ts` bounds who may confirm a cluster, not whether the evidence is real.
- Most reusable component: `user_rejected_reason`. One optional frontmatter field, written only by `o2b brain reject --reason`, converts a retired rule into a suppressor that swallows the signals which would regrow it — scope-aware, so an unscoped rejection covers the topic everywhere and a scoped one only its own scope, with a `signal-suppressed` event emitted per swallowed signal naming the rule and the reason. It is the rejected-value tombstone arrived at independently, with a scope dimension no other instance in the atlas carries.
- Maturity impression: MIT, v1.45.0, 190,847 lines of TypeScript against 172,320 lines across 1,031 test files — a ratio at the top of anything here — 175 commits since 6 May 2026, ten contributors. Local-first in the user's own Obsidian vault, so the memory outlives the tool. Two committed git hooks activated by the package `prepare` script run fmt, lint and typecheck only. No lockfile beside `package.json` at this commit.
- Study when: you are designing promotion and demotion and want both to be defensible. The asymmetric `quarantine` probation — still active and injected, flagged separately in the digest, retired by one further violation, restored by one application — is the answer to rules that oscillate under symmetric thresholds.
- Do not copy when: you need memory to hold facts, or to serve more than one person. The unit is a behavioural rule with an application rate, and a claim that is simply true has no `applied_count`; scope is owner/session/project inside one vault, with no tenancy and a trust model assuming the evidence reporter and the beneficiary are the same well-meaning agent.

### [`zep`](../systems/zep/)

- Best idea: grading retrieval sufficiency and answer correctness as two independent judgements of the same question. `benchmarks/locomo/evaluation.py` fires a CORRECT/WRONG grader and a COMPLETE/PARTIAL/INSUFFICIENT context grader concurrently, records `missing_elements` per question, and derives `accuracy_with_complete_context`. That last number is flat at 0.92 across a 5.8x swing in retrieved tokens, which says every point the retrieval sweep buys comes from completeness rising and none from the reader improving — an attribution almost no memory benchmark in this atlas can make.
- Biggest risk: the mechanism is not here. Extraction, entity resolution, edge invalidation and ranking are Zep Cloud's, and the repository is the client contract plus the measurement apparatus. The one durable error a client can cause it documents itself: an episode submitted with no `created_at` is silently dated to ingestion time, "which corrupts fact validity timelines and invalidation ordering on backfills".
- Most reusable component: `AliasCanonicalizer`. Pre-ingestion entity-name rewriting with a 150-word risky-words deny-list, URL and code-span protection, punctuation-safe boundaries instead of `\b`, and per-alias replacement counts surfaced in a preview that makes no API calls. Six anticipated failure modes in 227 lines, in a transform most teams write as a `str.replace` loop.
- Maturity impression: Apache-2.0, thirteen independently released integration packages across Python, TypeScript and Go, about 4,900 lines of well-tested ingestion library with roughly thirty test modules, and fifty committed benchmark runs. The Community Edition is deprecated in `legacy/`, and the MCP server has thirteen documented tools and no source in this tree.
- Study when: you are choosing a retrieval budget and want to know where the knee is. 20/20 to 30/30 costs 45% more context tokens for 0.26 points of accuracy — inside one standard deviation — while accuracy-given-complete-context falls slightly, the shape a mild distraction effect makes.
- Do not copy when: you need to inspect, repair or run the store. There is no local mode, an API key is required before a single fact is written, and the documented MCP surface is thirteen read tools — the application ingests and the model only asks.

### [`memorybank`](../systems/memorybank/)

- Best idea: recall-strengthened decay as a first-class primitive. A per-item `memory_strength` counter, a `last_recall_date`, and a retention probability that should rise with strength and fall with elapsed time is the only mechanism in wide circulation that sheds material without asking a language model what matters. This is where the field got it.
- Biggest risk: the formula is inverted. `math.exp(-t / 5*S)` parses as `((-t)/5)*S`, so higher strength means faster forgetting — 82% one-day retention at strength 1, 13.5% at strength 10 — while the docstring directly above promises the opposite. Since retrieval increments strength, recalling a memory is what destroys it. The deletion is stochastic, in place, against the only copy, unlogged, and applied to every user in the file because the per-user guard at `forget_memory.py:88` is commented out.
- Most reusable component: `eval_data/`. Fifteen ChatGPT-simulated personas with ten days of history each and roughly a hundred hand-written probing questions, in parallel English and Chinese — an MIT-licensed bilingual recall fixture that costs a week to build yourself. The runner that consumed it is not in the tree.
- Maturity impression: a 2023 research artifact. About 3,300 lines, MIT, no commit since 24 May 2023, no tests anywhere, a committed `__pycache__`, and dependencies (`langchain.vectorstores`, `GPTSimpleVectorIndex`, `openai.ChatCompletion`) that no longer exist upstream. `screen_repo.py` returned NOTHING SCANNED.
- Study when: you are implementing a forgetting curve, or you cited this paper's curve as prior art and want to check whether you inherited the expression along with the idea. The fifty lines around the formula are a compact catalogue of what to get right.
- Do not copy when: always, as code. The pattern travelled widely and the file is short enough to copy whole, which is the specific outcome to avoid.

### [`reflexion`](../systems/reflexion/)

- Best idea: separating the acting model from the reflecting model. Two prompts, two calls, two jobs — the agent that just failed never decides what the lesson was while still holding the failed context, and the reflector never acts. The write trigger is an outcome the harness actually observes (`is_success`), which is more grounding than most memory systems here have for deciding when to write anything.
- Biggest risk: the store grows forever behind a fixed three-item read window. `memory[-3:]` at injection and again at reflection means an environment that failed eleven times has eleven plans on disk and three that can be read; if the useful one was written first, nothing can surface it again. Nothing is ever retracted, only sunk, and a plan built on a wrong diagnosis is context for the next three plans written.
- Most reusable component: the resumable env-config array. `{name, memory, is_success, skip}` dumped after every trial and reloaded by `--is_resume` is the minimum viable durable agent memory — no schema, no index, no identity beyond a list position — and it is enough to take AlfWorld from 62.7% to 100% over fifteen trials in the committed logs.
- Maturity impression: NeurIPS 2023 reference code, MIT, four unpackaged sibling harnesses with duplicated utilities, no tests, last commit 13 January 2025. Two of the four harnesses keep reflections only in process and are out of this atlas's scope entirely.
- Study when: your task is retried — same environment, same goal, an observable success signal, a bounded attempt count. Coding agents retrying a failing test and any loop with a verifier are the natural fit.
- Do not copy when: you are building a long-lived assistant. Tasks are not repeated, there is no success signal to gate the write, the scope is a user rather than an environment, and the corpus outgrows a three-item window on day one. Note also what the committed logs cannot settle: the "base" run's env configs also carry memory, and the format records no flags, so the tree holds two runs that differ and cannot say in what.

### [`langgraph`](../systems/langgraph/)

- Best idea: the scope is half the primary key. `PRIMARY KEY (prefix, key)`, with the namespace tuple a required positional argument on `get`, `put`, `delete` and `search`, and validated on the way in — labels cannot be empty, contain a period, or start with the reserved `langgraph` root. Cross-tenant leakage stops being a filter someone forgot and becomes a call that does not compile.
- Biggest risk: the conformance suite covers the other half. `langgraph-checkpoint-conformance` is a published, capability-aware, installable suite for third-party checkpointers; `BaseStore` has no equivalent, and the store is where the three first-party backends visibly disagree — Postgres preserves `created_at` across an update while SQLite and the in-memory store reset it, and Postgres cascades a delete to `store_vectors` while SQLite declares the identical foreign key and never issues `PRAGMA foreign_keys = ON`, so every deleted and every expired item leaves its embeddings behind forever.
- Most reusable component: TTL refreshed on read, with `refresh_ttl` overridable per operation. Last-touched expiry falls out of ordinary traffic with no scorer, no LLM and no background pass, and the per-operation override keeps a bulk export or an admin scan from resurrecting dead memories — the detail that makes the pattern usable rather than a footgun.
- Maturity impression: MIT, a mature monorepo, three store backends with 90-plus store tests between them, and a conformance package published to PyPI. `InjectedStore` hands a store to a tool and strips it from the schema the model sees, which is the right agency split; no memory tools are prebuilt, so every application invents its own.
- Study when: you know what your memories are and want somebody else to own the table, the migrations, the TTL thread and the pgvector index.
- Do not copy when: you were hoping to get memory *semantics* from your framework. There is no extraction, no consolidation, no correction, no trust and no state machine — an item is present or absent. And namespaces are strings a node computes, so a genuine multi-tenant boundary needs a layer above this one.

### [`langchain`](../systems/langchain/)

- Best idea: drawing the window/memory boundary in the package structure. Version 1 owns no store at all — `store` appears in `agents/factory.py` as a parameter forwarded to LangGraph and nowhere else — while the ten classic memory classes sit in `langchain_classic` under `@deprecated(since="0.3.1", removal="2.0.0")`. Seven of the ten were conversation-window management the whole time, and naming them "memory" is why the word is ambiguous; the deprecation is the clearest statement anyone in this ecosystem has made about which is which.
- Biggest risk: an empty summary deletes the entity. `SQLiteEntityStore.set()` opens with `if not value: return self.delete(key)`, so a summarizer returning an empty string — the natural output when a model decides there is nothing to say — silently destroys everything known about that entity. The summary slot is single and overwritten with no history, so a correction and a corruption are the same write.
- Most reusable component: the two prompts in `memory/prompt.py`, and specifically the sentence that makes the summarizer safe to run every turn — "If there is no new information about the provided entity or the information is not worth noting, return the existing summary unchanged." An explicit permitted no-op is the difference between an extractor that consolidates and one that churns. The five-method `BaseEntityStore` has aged better than the class using it.
- Maturity impression: `langchain` 1.0.8, fully lockfiled with zero unpinned dependency surfaces — the rare monorepo here where that is true. The memory package is 2,201 lines under a removal notice, and its window-management classes are better tested than its durable ones.
- Study when: you are designing entity memory and want a reference for the prompts and the store interface, both small and widely copied. Also read `SQLiteEntityStore` for the one design in this atlas that scopes by DDL — a table per session, physically unreachable from another session's queries.
- Do not copy when: you need a session id that is a UUID or an email. `session_id.isidentifier()` rejects both, because the scope key becomes part of a table name. And nobody should build on this package at all: the official replacement is a different one.

### [`agent-memory-techniques`](../systems/agent-memory-techniques/)

- Best idea: decay parameterized by half-life, with archival instead of deletion and strength folded into the ranking. `decay_rate = math.log(2) / half_life_hours` gives an operator a number they can defend, `similarity * strength` makes forgetting gradual rather than a cliff at the prune threshold, and `prune()` sets `archived = True` and moves the record rather than destroying it. On the one mechanism it shares with [MemoryBank](../systems/memorybank/) — the paper it cites — the teaching implementation is the correct one.
- Biggest risk: the contradiction rate divides by pairs it never compared. `ContradictionDetector.scan` finds contradictions only within batches of fifteen and then divides by every pair in the corpus, so at a hundred memories roughly 735 examined pairs are reported against a denominator of 4,950. The metric falls as the store grows even when the true density is constant, which means a dashboard built on it reports improving consistency while conflicts accumulate.
- Most reusable component: `TieredMemorySystem.delete_user`. Four stores named in one function — hot cache, warm vector store, cold archive, relationship graph — each returning a count, each writing a timestamped audit entry. The graph filter works on `user_id` rather than edge direction, so it does not have the asymmetry that catches most graph deletions, and the per-store counts are what make the erasure claim checkable.
- Maturity impression: Apache-2.0, 14,277 lines across thirty self-contained notebooks with a per-technique README, a thirty-row comparison table, and CI that validates cell structure and prose style. Nineteen unpinned requirements, no tests of any memory behaviour, and an evaluation harness in notebook 28 that is never pointed at the other twenty-nine notebooks.
- Study when: you are about to build a memory layer and want thirty implementations of the decisions you are facing, small enough to read in one sitting. Notebooks 19, 20, 28 and 30 repay reading even after you have built something.
- Do not copy when: you are lifting one notebook into a product. The corpus is internally inconsistent by construction — notebook 30 requires a `user_id` on the read path and notebook 06 has no tenant concept at all — and nothing warns you which one you picked. Six of the thirty techniques are conversation-window management filed under the word memory.

### [`grok-build`](../systems/grok-build/)

- Best idea: stamping retrieved memory with its own age and a verify hint, at injection time, suppressed for curated sources. `format_staleness_note` emits `**Stale (…):** Verify current state before relying on this.` into the `<system-reminder>` block, so the hedge reaches the model at the moment it decides whether to trust the claim. Nothing is stored and nothing can filter on it, which is why it is not `trust_state` — and why it works: the distinction it draws is not fresh-versus-old but written-down-versus-merely-observed. Curated `MEMORY.md` files are exempt from both the note and temporal decay.
- Biggest risk: the dream pass is destructive at both ends. It truncates the model's consolidated document at 16,000 characters with `chars().take()`, overwrites the workspace `MEMORY.md` with the result — no version, no diff, no backup — and then deletes the session logs it read. Prior knowledge survives only because the prompt asks the model to merge rather than replace. Behind that, `grok memory clear --global` removes one file and leaves its verbatim text in `chunks.text` in every other workspace's `index.sqlite` until someone runs `grok memory reindex`.
- Most reusable component: `MemoryStorage::read_file`. It canonicalizes both the model-supplied path and the memory root, refuses anything not under the root, and reads the *canonicalized* path rather than the original with the reason in a comment — "to prevent TOCTOU races". That is the containment check on the read path that several systems here apply only on the write path, plus the race that survives a naive version of it.
- Maturity impression: Apache-2.0, 1.59M lines of Rust synced from a monorepo with the source commit recorded at the root; the memory crate is ~9,900 lines with **290 tests**, distributed across storage, dream, search, lock and index rather than pooled in the easy modules. Behind `--experimental-memory`. The concurrency work is serious — a dream lock with stale recovery and rollback, a `reindex_claim` row so two processes cannot reindex at once, `arc_swap` for lock-free dirty tracking — and there is no benchmark, no dataset, and nothing measuring the seven weighted ranking stages.
- Study when: you want memory to be files a developer edits with search as an accelerator, and you are deciding where injected context sits relative to the provider's prompt cache. The injection here is persisted into the leading system message and reused verbatim rather than re-scored, because "a re-scored block would mutate the system-prompt prefix and bust the KV cache for the whole downstream conversation" — the most direct answer to that question in the atlas.
- Do not copy when: your memory is a set of claims rather than a set of documents. There is no fact, no extraction, no supersession, no tombstone and no way to mark something disputed; the dream's instruction is to "keep only the current truth", so the losing side of a contradiction leaves no trace. Also check the session-registry flag before trusting the store with anything private: `memory.tar.gz` bundles every `MEMORY.md` and session log for upload, off by default, and if the local flag is unset a remote setting decides.

### [`runar-forge`](../systems/runar-forge/)

- Best idea: one redaction chokepoint, ordered before truncation. Every write path — MCP save, prompt capture, extraction, crawler — passes through `propose`, which strips `<private>` blocks and redacts secret patterns from title, content, each tag and the caller-supplied `topic_key`, then bounds content, in that order, because "truncating first could cut a secret in half and hide it from the matchers". Each outcome tags the row `redacted`, `redacted:secret` or `truncated`, so the fact that a memory was modified on the way in is itself stored and searchable. The strongest write-path hygiene in the atlas.
- Biggest risk: the graduation sweep cannot see the entries it exists to move. `graduate_layers_inner` fetches with `limit: Some(500)`, never sets the `offset` its own filter type provides, and no caller loops; `list` ends `ORDER BY created_at DESC`. Graduation is an aging ladder, so the rows needing archival are the oldest — precisely the ones a newest-500 window can never reach in a namespace past that size. The low-confidence aggressive-demote rule, which clears speculative material, is disabled by the same cap.
- Most reusable component: the `access_count` / `injected_count` split, and the comment explaining it — "one counter for two channels is what let '95.9% never retrieved' stand for three months while 15,819 injections went unrecorded. Reporting only — deliberately not an input to ranking or decay." Two decisions in three lines: split the counter because one number over two channels made a headline statistic false, then keep the new one out of ranking so automatic recall cannot reinforce itself.
- Maturity impression: MIT, one static Rust binary over 54,895 lines in a single crate, **694 tests**, twenty-two MCP tools, SQLite or Postgres with a hybrid outbox, bundled local embeddings so semantic search needs no key, a `doctor` with 1,620 lines of diagnostics and a `gc --dry-run` that previews layer transitions. And a habit of writing its own postmortems, with counts, into the comment above each fix.
- Study when: you want durable structured memory across several coding tools with provenance that reaches a person — `author` from git config, `verified_by` separate from it, redaction history as tags, supersession as an edge. Supersession is done well: a topic-key collision soft-deletes the old row so reads exclude it and writes `Supersedes` new → old so the lineage keeps it.
- Do not copy when: you need to record that two memories disagree. `EdgeType` declares `Contradicts`, `Supports` and `Elaborates`, and each appears exactly once in the crate — in the enum. Nothing constructs them and nothing reads them, so a system with a confidence scale, a verification flag and a supersession graph still has no way to represent conflict. Also note the review surface: `muninn_verify` grants a ranking bonus and a graduation fast-promote, its only caller is an MCP tool the writing agent can invoke, and the `verified_by` it records is whichever human's git config is configured.

### [`redcell`](../systems/redcell/)

- Best idea: the memory unit is a claim that can be false, and its status is set by a human. A finding is `[severity] title @ location`, recorded by the agent as `candidate` — the only status the agent may write — and moved to `verified`, `dismissed` or `inconclusive` by a person. A dismissed finding is a false positive removed from the record and the report, which makes it the cleanest example of a corrected memory in the atlas: not a superseded or decayed value, but a stored claim a reviewer judged wrong.
- Biggest risk: recall is a wholesale paste capped by recency. `assistant.py` lists the session's findings, truncates to forty newest-first, unranked, and prepends them to the system prompt — so a long engagement silently drops its earliest findings from the agent's context with no signal, and there is no cross-engagement memory at all, everything keyed to one `session_id`. Also: tool output from an adversarial target becomes a finding becomes agent context, unfenced, in a system pointed at hostile machines by definition.
- Most reusable component: the three-way split of memory authority. The agent writes (only `candidate`), a human triages (verify/dismiss/merge, with a merge that refuses to touch a duplicate in another session), and a chat assistant reads the record back on reopen. Letting the writer also confirm its own output is the failure most memory systems have; here a verified memory carries the mark of a review that actually happened.
- Maturity impression: MIT, ~9,100 lines of Python across a FastAPI API, an `arq` worker and a LangGraph/LiteLLM engine, **77 tests** including a triage suite that asserts an unknown status raises and that dismissed findings leave the report. A full server platform — Postgres, Redis, MinIO, a Kali container — not a library. Durable across restarts via a LangGraph SQLite checkpointer that is itself out of scope; the findings record is the memory.
- Study when: your agent produces reviewable claims a person must approve within a bounded engagement. The finding-as-memory model, agent-proposes/human-confirms, and repository-enforced session scoping transfer whole, independent of the pentest domain.
- Do not copy when: you need ranked recall, cross-engagement learning, or a triage audit trail. The read path is a truncated paste, the `session_id` key is load-bearing everywhere, and a finding records that a human ruled but not which human — a gap for a deliverable someone signs. Dismissal is status-only, so a reworded re-derivation of a dismissed finding would be recorded fresh: the dedup key (title, location) and the dismissal key do not intersect.

### [`neuron`](../systems/neuron/)

- Best idea: a per-category schema enforced on the write path, below the prompt. `neuron.yaml` declares required and enum-typed fields, and `enforceFieldSchema` refuses any write that skips a required field, names an undeclared one, or sends a value outside a declared enum — from the CLI and from `neuron scan` alike, with a did-you-mean on enum near-misses. An agent whose prompt says "just save it" cannot, because the refusal is a property of the store, not the instruction. The cleanest answer in the atlas to stopping an agent writing junk into its own memory.
- Biggest risk: the store of record is markdown a hand-edit or a parser edge case can corrupt, and reconciliation trims the mirror to match it. Ticket 38 records exactly that — a stray `---` made the parser undercount a category ~38% and the vector mirror was mass-deleted to agree. Root bug fixed, a loud-but-non-blocking tripwire added, `.neuron/` is git-recoverable — but when humans and a parser both write your truth, a parse disagreement is a data-integrity event.
- Most reusable component: the recall fidelity ladder. Deterministic / best-effort / instruction-only, reported per harness by calling its real hook registration through `verify()` rather than inferring from a config file, with Cursor explicitly marked "not verified against a real installation … fixture evidence only." How to make an integration-matrix claim honest, and almost nothing here does it.
- Maturity impression: MIT, ~28,900 lines of TypeScript, ~700 tests across 62 files with dedicated suites for the dual router, the md-to-vector sync, supersession (two files) and schema-of-schema validation. Fully offline — local ONNX embeddings, no key, no cloud. Retrieval is real hybrid: RRF over vector and FTS5 legs, an FTS-match gate, and a cross-encoder reranker.
- Study when: you want your agent's memory to be plain files you own, review in diffs and edit by hand, with a schema that keeps the agent honest and recall the harness guarantees rather than the model choosing to look. Make the human-readable form the store of record and the index disposable — reconcile it from the files, delete it and rebuild.
- Do not copy when: you need a trust model richer than live-vs-superseded — there is no verified or rejected state and disputed claims have no representation — or multi-tenant isolation, since the boundary is a project-root hash on a shared per-machine cache, not an auth boundary. And weigh the markdown-as-record tradeoff: reviewability and hand-repair, bought with a source of truth a parser edge case can corrupt.

### [`windieos`](../systems/windieos/)

- Best idea: stamping every FAISS index with the embedding space that built it. `EmbeddingSpaceMetadata` (provider, model, dimension, space version) is saved beside the index and checked on startup; when it changes, the store logs *"SDK embedding space changed … Clearing local vector indices,"* resets the indices, nulls every `embedding_id` in SQLite, and re-embeds from the surviving rows. That is the correct answer to a failure almost nothing in the atlas handles — scoring vectors from a new embedding model against vectors from an old one, silently, the first time anyone upgrades.
- Biggest risk: two delete gaps the project documents honestly. There is no episodic→semantic cascade, so deleting a conversation leaves the facts summarized from it behind in semantic memory — the exact opposite of the same author's Rust sibling, which deletes compactions in the transaction that deletes their source message. And a partial delete drops the vector→memory mapping (so deleted content can't surface) but leaves the vector in the FAISS file until the tier empties, so a long-lived index carries dead vectors and overreports its count.
- Most reusable component: the fail-safe write path. The SDK asks the backend for an embedding and hands it to the local store; if embeddings are down the row still lands in SQLite with a NULL vector id and a startup backfill re-embeds it later. A memory is never lost to an embedding outage, and search degrades to returning nothing rather than erroring — the memory is an enhancement the chat loop can survive without.
- Maturity impression: MIT, an Electron desktop runtime with a Python local runtime (~58,500 backend lines) and 676 sidecar tests; memory is local-first (SQLite + FAISS per user under OS app-data), the backend a stateless calculator for embeddings and summaries. The default branch had been stalled six weeks at reading while the author's active work was the Rust sibling — read as a mature, paused predecessor.
- Study when: you are building a local, single-user desktop assistant that should accumulate a picture of its user across sessions without shipping that memory to a server, and you want a two-tier episodic→semantic split with crash-safe consolidation (mark sources semanticized only after the summary write, resume from a watermark, dedup by `summary_hash`).
- Do not copy when: you need multi-tenant isolation beyond one machine, ranked or hybrid retrieval (this is exact `IndexFlatIP` vector search, no lexical arm, no reranker), a trust model richer than present/absent, or deletion guaranteed complete across derived tiers. At large corpus sizes the exact search and the never-compacted-until-empty index are both scale ceilings.

### [`sonder-runtime`](../systems/sonder-runtime/)

- Best idea: an outcome-gated quarantine that checks the base rate and the attribution before it suppresses a lesson. A distilled lesson stops being retrieved only when its run of losses is statistically improbable for its own retrieval-frequency band (a test computes `p=0.006`), and only for losses it is individually answerable for — a cohort of lessons always retrieved together cannot each claim the same shared failure. A cooldown then admits it to sampled probation, and a win lifts the quarantine on evidence. It is the credit-assignment discipline the atlas keeps asking for and almost never finds built.
- Biggest risk: the loop is only as good as its outcome signal, and much of that signal is `machine` or `unknown`. The code weights caller-sourced outcomes above machine ones and enforces an `outcomes.source` provenance column `NOT NULL` with no default — a real self-grading defense — but a store fed only machine-graded outcomes is still grading itself, and no base-rate care fixes a signal that is the model assessing its own output. Separately, quarantine suppresses a lesson without a rejected-value record, so a re-distilled duplicate can return.
- Most reusable component: the `interaction → outcome(source) → lesson_usage` credit chain. It links every retrieved lesson to the interaction that used it and the outcome that followed, with who judged it, which is the join most lesson stores omit and the thing that makes outcome-gated trust possible at all. The base-rate math in `retriever.py` and the pure ranking/contradiction logic in `lesson_decay.py` are test-friendly by construction and portable.
- Maturity impression: Apache-2.0, ~257,000 lines of Python (a self-modifying runtime; the memory layer is a stdlib-only SQLite adapter inside it), 357 test files with worked-probability quarantine cases, schema columns that carry a comment explaining the defect each prevents. The constants — 0.62 relevance floor, 0.93 dedup, 30-day half-life, five-loss quarantine — are each defended in a comment and tested for behaviour, and none is measured against retrieval quality.
- Study when: you are building a self-improving agent that accumulates procedural lessons and can observe outcomes, and you want to suppress the lessons that hurt without punishing the ones that merely got the hard tasks. The quarantine's two statistical guards are worth lifting whole even into a different store.
- Do not copy when: you cannot produce a trustworthy outcome signal — the design degrades to self-grading if every outcome is `machine`. Also walk away if you need contradiction *resolved* rather than flagged. Note that the rejected-value gap is now half-closed: near-duplicate pruning writes a content-hashed tombstone that distillation refuses to re-derive, so a pruned duplicate cannot return — but quarantine still keeps a suppressed row without a rejected-value record, so a quarantined lesson re-distilled from a fresh interaction can come back.

### [`gmr`](../systems/gmr/)

- Best idea: bind a memory to the observable fact it depends on and re-check the fact, not the memory's age. A memory is stored as a binding — an external reference attached to anchors, each an observable fact with a versioned probe and content-hashed transition rules — and when the probe's observed facts hash to a new value and a rule fires, the memories bound to that anchor are surfaced as drifted. It answers the question decay heuristics only approximate with a clock: not "is this old" but "did the thing this was about change." Detection is deterministic (a `FactAddress` hash), not a model judging similarity.
- Biggest risk: it grounds and surfaces but does not decide correctness or store the content, so the value is entirely a function of whether someone wrote a probe that observes the right fact and a transition that fires on the right change — real authoring work the runtime cannot do for you. A memory bound to the wrong anchor is reported current while being wrong. And a probe declared `Open` (unverifiable) is trusted rather than reproduced; GMR marks the `Closed`/`Open` distinction but cannot close the gap.
- Most reusable component: the failure taxonomy that keeps "could not observe" apart from "observed a change." A failed probe is journalled as an `Entry::Attempt` with a `ReasonClass` (`Unreachable`/`Unusable`/`Unevaluable`) and a specific `FailureCode`, never as a transition, so an outage never surfaces every memory as drifted — the single most important property a drift detector can have, and the tests pin it (`does_not_blame_the_anchors_it_never_reached`). The append-only journal — `Open`/`Transition`/`Still`/`Attempt`/`Revise`/`Close`, each `Revise` carrying a rationale hash — audits the grounding *policy*, not just the data.
- Maturity impression: Apache-2.0, ~11,500 lines of Rust across seven clean crates, 223 tests whose integration suites target exactly the mechanisms above, a portable export/import so a binary upgrade round-trips the SQLite store, and 135 memories in the tree dogfooding the thesis — each anchored to a GMR source symbol via `about:` frontmatter with a "When this changes, ask" section. Unusually disciplined for a v0.3.2. What is absent is a benchmark: nothing committed measures detection precision or recall.
- Study when: you already have a memory store and want the one thing most stores here lack — a principled answer to when a stored belief has gone stale because its subject moved. It composes with any store in the atlas as a grounding index beside them rather than a replacement, and the coding domain makes it directly usable for grounding memories about a codebase.
- Do not copy when: you want a store. GMR does not hold memory content, retrieve by similarity, scope by tenant, or decide whether a memory is correct — and if you want staleness handled automatically rather than by hand-written probes and transitions, the decay-and-reinforcement systems here ask less and promise less.

### [`continuous-claude`](../systems/continuous-claude/)

- Best idea: extract learnings from the **thinking blocks** — the model's reasoning, not its action transcript — via a background daemon that spawns a headless model on a stale-session heartbeat, then embeds and recalls them across sessions. Capturing *why the model changed its mind* rather than *what it ran* is the right target for a procedural memory and is unique in this corpus; a cheap regex "perception-signal" pre-filter keeps the extraction call small.
- Biggest risk: the design overshoots the code, and the gaps are the confidentiality-and-correctness kind. The default learnings backend selects a `sqlite` service whose module is absent, so out of the box it silently no-ops unless a Postgres URL is set; recall is global across every project because a learning carries no project key; dedup runs per-session while recall runs cross-session, so duplicates accumulate; `confidence` is stored and read by nothing; embeddings from different providers share one unstamped 1024-d column; and the "user-confirm-learning" hook auto-captures on casual affirmations without showing anyone, and isn't wired anyway.
- Most reusable component: the recall design — hybrid reciprocal-rank fusion over pgvector cosine and Postgres full-text, top-k, injected automatically on every prompt as a `MEMORY MATCH` — paired with the daemon-plus-thinking-block capture shape. Both are liftable independently of the store.
- Maturity impression: MIT, a Claude Code `.claude/` config (30 hooks, 32 agents, 109 skills) plus an `opc/` Python package; PostgreSQL + pgvector for learnings behind a heavy Docker-and-daemon install. Carries **none** of the seven capability marks, no memory tests and no retrieval eval, and a striking amount of dead scaffolding — a broken default backend, an unread affinity table, an artifact-index hook that writes to a nonexistent path. The one working, novel idea is real; most of the surface around it is aspirational.
- Study when: you are building a coding-agent memory and want the thinking-block extraction idea and the auto-injected hybrid recall — as patterns to reimplement over a store you control.
- Do not copy when: you need scope isolation, correction, provenance, a trust state or an audit trail — none is present, and the global cross-project recall plus the unstamped embedding column fail quietly rather than loudly. Also walk away if you cannot run Docker, a local Postgres and a permission-disabled headless daemon, which is what the memory half costs to operate.

### [`mcp-memory`](../systems/mcp-memory/)

- Best idea: store memory as an Open Knowledge Format markdown document — typed frontmatter, human-readable, mirrored to disk per namespace — indexed in SQLite FTS5, so the store is diffable and hand-repairable rather than an opaque table.
- Biggest risk: the OKF trust-and-lifecycle model is write-only. `status` (draft/stable/deprecated), a `verified` actor list and a `stale_after` date are serialized faithfully into every record and read by no retrieval, ranking or gating path — a `deprecated` or expired memory is returned exactly like a fresh verified one. The "strictly adheres to the spec" claim is also unbacked: the conformance validator exists and is never called on the write path.
- Most reusable component: the namespace-scoped, FTS5-indexed OKF store with a `last_memory` continuity checkpoint — small, self-contained (≈1,600 lines, stdlib sqlite3 plus fastmcp and pyyaml), and the namespace filter is genuinely enforced on read.
- Maturity impression: MIT, a tidy single-purpose MCP server; the one earned mark is `scope_enforced`. Tests cover the positive paths but assert nothing about the lifecycle fields, so their inertness is untested rather than caught.
- Study when: you want a minimal, inspectable, dependency-light MCP memory server and are content with lexical search and manual lifecycle management.
- Do not copy when: you expect the OKF `verified`/`status`/`stale_after` fields to *do* anything — today they are inert — or you need semantic recall, decay, correction that sticks, or provenance the system acts on.

### [`mentisdb`](../systems/mentisdb/)

- Best idea: an append-only, SHA-256 hash-chained thought log that is re-hashed on open and **refuses to load if tampered** — the strongest integrity story in the corpus, because verification gates the load rather than logging a warning. Correction never mutates: a wrong thought is superseded by an appended relation, and the superseded ids are excluded from default reads.
- Biggest risk: tamper-evidence is detection, not prevention — an actor with file-write access can recompute the whole chain — and the guarantee has two stated holes: `entity_type` and `source_episode` sit outside the canonical hash, and thought signatures are stored but never verified (only *skill* signatures are). Scope is an opt-in tag, not an enforced boundary.
- Most reusable component: the verify-on-open chain with an `include_invalidated` auditor escape hatch, and the git-like immutable skill registry — whole-then-diff versions, content-hash re-verification, and server-side Ed25519 verification required once keys are registered.
- Maturity impression: MIT, ~47,000 lines of Rust, ~487 tests, a WHITEPAPER; earns `bitemporal`, `audit_log` and `negative_eval`. Only the binary storage adapter ships (the "swappable sqlite/files/memory" is a trait), and the benches measure scale, not recall quality.
- Study when: you want an audit-grade, local, multi-harness memory whose history is verifiable and whose corrections are on the record; the signed skill registry alone is worth lifting.
- Do not copy when: you need enforced multi-tenant scope, tamper-*resistance* rather than tamper-evidence, or verified provenance on the thoughts themselves — those are perimeter, aspiration and gap respectively.

### [`monet`](../systems/monet/)

- Best idea: split declare from propose and gate the constraining memories on a human — the agent proposes facts, but a person must `declare` principles and blocking rules (SQL-enforced so a blocking rule cannot be self-authorized), and a contradiction flips the concept to `disputed`, dropping it from the always-on context until a human resolves it.
- Biggest risk: two headline mechanisms are softer than the prose. "Rules read at the moment they bind (commit, release, PR)" is lexical token-matching against a tool call on *user-authored* stages, and as shipped the agent-first harness relies on the agent *pulling* `stage_lookup` rather than wiring the mechanical hook — binding is cooperative, not enforced. "Corrections recorded so they never need making twice" is supersession (retrieve-the-winner), not a value-keyed tombstone that blocks a re-proposed mistake.
- Most reusable component: the always-on principle "skeleton" (materialized and auto-prewarmed) kept separate from the searched concept store, plus append-only `resolution_events`/`gate_events` that log even the silences.
- Maturity impression: AGPL-3.0 core, genuinely local-first (~57,000 lines over one SQLite file, on-device ONNX hybrid retrieval, test tree larger than source); earns `trust_state`, `scope_enforced`, `audit_log`, `human_review` and `negative_eval` — one of the better-governed local memories here. A ~10,000-line RAG source-ingestion subsystem sits provisionally retired behind the trio-shaped README.
- Study when: you want a private, local, governed memory for a coding agent and will work its method — declare the principles, name the stages, resolve the contradictions.
- Do not copy when: you need the binding and correction to be *enforced* rather than cooperative — the shipped harness leaves rule-lookup to the agent, and corrections do not prevent recurrence.

### [`memmy-agent`](../systems/memmy-agent/)

- Best idea: share one local memory across every coding agent through a daemon plus an *injected per-agent CLI skill* — Memmy writes a `memmy-memory` skill into `~/.claude`, `~/.codex`, `~/.cursor`, `~/.openclaw` and `~/.hermes`, so all of them read and write the same SQLite store, no MCP required. Beside it, a negative-experience pipeline turns failures into content-keyed anti-pattern "avoid" policies surfaced on read.
- Biggest risk: the shared brain has no scope on its main recall. Scope keys (user/agent/app/session) sit on every row, but the primary semantic recall filters only by layer/status/tags — cross-agent pooling is deliberate, so every agent's memory blends into one recall surface with only a `--source` tag for provenance. Fine for a solo user; a confidentiality leak across projects or trust boundaries. And "local" is one config flip from a hosted OpenMem/MemOS cloud backend.
- Most reusable component: the injected-skill-plus-daemon sharing pattern, the anti-pattern induction (rejected values keyed on a failure signature, merged not duplicated), and vector rows stamped with their embedding model and dimension.
- Maturity impression: from MemTensor (the MemOS team) but its own TypeScript engine, not MemOS embedded; ~44,000 lines of memory core, SQLite + FTS5 + sqlite-vec, local embeddings, an LLM L1→L2→L3→Skill evolution pipeline, 57 test files. Earns `tombstone`, `trust_state`, `audit_log` and `negative_eval`; `scope_enforced` is withheld by design.
- Study when: you run several coding agents and want them to share one growing local memory, and you value the shared brain over per-project isolation.
- Do not copy when: you need per-project or per-trust-boundary isolation from one daemon — the main recall deliberately does not scope — or "local" is a hard requirement you cannot police against the opt-in cloud backend.

### [`always-on-memory-agent`](../systems/always-on-memory-agent/)

- Best idea: replace retrieval with a read. No vector DB and no embeddings — memories are structured SQLite rows, and the query agent loads the recent window (50 memories + 10 consolidations) for Gemini to read and answer with citations. Beside it, a genuine always-on consolidation daemon on a 30-minute timer that reads the unconsolidated set, finds cross-cutting connections and one insight, writes it, and marks the sources done — the "compress and connect during sleep" idea done as real background work.
- Biggest risk: recall is a recency window, not relevance. Past the fifty most recent rows a memory is invisible to a query unless a consolidation folded it in; the design does not scale beyond what fits the context window, and it is not trying to. Correction is a hard delete with no rejected-value record, so a re-ingested claim returns and a deleted memory can leave a dangling `source_id` inside a consolidation.
- Most reusable component: the load-and-read query paired with the standalone consolidation loop — the anti-RAG shape (structured capture, no vectors, model-as-reader, background compression) in about 700 readable lines.
- Maturity impression: MIT (© Shubham Saboo), a ~1,000-line sample vendored into Google's `generative-ai` repo, on Google ADK + Gemini Flash-Lite with multimodal ingest, a file watcher, an HTTP API and a Streamlit dashboard. No capability mark: `importance` is a stored-but-unranked float, `consolidated` a processing flag, delete is hard, and there is no scope, validity time or audit. No tests, no eval.
- Study when: you are prototyping a personal, always-on memory without an embedding stack and want the clarity of a load-and-read design and an active consolidation daemon.
- Do not copy when: your store will outgrow a context window, you need to find the *relevant* memory rather than the recent one, or you need scope, correction that sticks, or any trust/audit property — none is present and the recency-window ceiling is architectural, not a knob.

### [`nexusmem`](../systems/nexusmem/)

- Best idea: bound how far query-independent priors may overturn the query, as **one budget shared between them**. `signal` and `recency` hold before any question exists, and multiplied in as equals they win outright — a `fix:` commit at signal .9 took rank 1 from the doc section that actually answered, on a 44% signal edge against a 15% relevance deficit. Capping each prior separately fixes nothing, because the score multiplies and two priors worth 2x each are worth 4x together; that shape *"describes every commit made during an active working day"*. So one joint budget, split evenly, each prior raised to the power that makes its range worth its share, and a third prior re-divides rather than enlarges it. Beside it, the cheapest good idea in the corpus: capture the shell exit code, which git cannot supply and scrollback loses.
- Biggest risk: nothing can be forgotten. There is no per-item delete, no delete by value, and no record that anything was removed; the finest granule is `--prune-source`, which wipes a whole source. Worse, the append-only hook log the shell nodes were derived from is untouched by every removal path, so `sync --rebuild` re-derives exactly what was pruned. For a store that deliberately ingests assistant transcripts and shell command lines — the two places a pasted credential lives — a redaction miss is unrecoverable by any command in the tree.
- Most reusable component: `src/conversation/redact.ts`, for the distinction rather than the rules. Shape rules (private-key blocks, `AKIA`, `gh[pousr]_`, JWTs) match strings nothing else produces and are safe over source code; the broader key/value rule would match `const apiKey = process.env.API_KEY` *"and would corrupt the very lines a diff is indexed for"*. Two named profiles, chosen per collector. Beside it, `filterBoilerplateTokens` in `src/correlate/failure-fix.ts`: a token appearing in over 20% of a project's own history is dropped from the match query, because bm25 rewards rarity only within the corpus it runs against — a measured false positive scored −9.685, stronger than two real links at −5.899 and −6.559.
- Maturity impression: MIT, v0.4.0 at 118 commits, ~9,100 lines of TypeScript, 451 tests across 29 files, CI, an npm package, a four-tool MCP server, a VS Code panel and an opt-in git pre-commit hook. Two capability marks — `scope_enforced` (`project_id` a required predicate on every read arm) and `negative_eval` (cross-project leak tests on both retrieval arms, plus three suppression cases on the pre-commit arm). Two near-misses stated in the report: a bi-temporal pair whose record-time column no read path queries, and a viewer that displays without reviewing.
- Study when: you want an agent to know what you already tried, you work locally in one repository at a time, and you would rather ship raw stored text through a good ranker than summaries through a model — or you want a worked example of memory delivered at a decision point rather than on request, in a git pre-commit hook that warns and cannot block.
- Do not copy when: anything you capture must be removable on request. Deletion here is keyed on the source while the source survives on disk, which is the pattern this atlas argues against, applied to the one collector most likely to hold a secret.

### [`feltstate`](../systems/feltstate/)

- Best idea: seal only what is supposed to be immutable. The hash-linked chain bites in the sealed text and fingerprint ids and deliberately leaves recall counts, decay state and pruned lineage *out*, **"so living never looks like tampering"** — a tamper-evident log that alarms on ordinary use is one people mute. Beside it, the fail-safe direction is right: a missing row is lawful only if a `legal_death` tombstone vouches for it, and that tombstone is sealed *into* the chained payload rather than asserted by a deletable line, so removing it makes the next patrol alarm rather than go quiet.
- Biggest risk: every exit is carefully built and none is consulted on the way back in. `retract` marks a fact and hides it from `view` and `search` while keeping the record on disk — then matching skips retracted and superseded rows, so the same value written again *"yields a fresh active fact"*, in the store's own docstring. The record that would prevent the re-admission already exists and nothing reads it. Separately, there is no scope key of any kind: `region` splits facts from skills and `actor` is optional, so a second user is a second deployment.
- Most reusable component: `memory/lifecycle/` as a set — `gc.py` is a pure judge returning a death plan and touches no file, `reaper.py` is the only executioner and runs a five-step fsynced cascade keyed on a `txid` that removes rows from the live stores *and every snapshot* (*"No regret medicine: disaster copies survive crashes, they do not resurrect the forgotten"*), and `chain.py` witnesses both. Few libraries this size ship a crash-safe deletion contract at all.
- Maturity impression: MIT, 60 commits, ~25,400 lines of Python, 528 tests across 40 files, CI, no database — every store is jsonl the caller names. Five marks: `trust_state`, `bitemporal` (a real `valid_at`/`invalid_at` window with an `as_of` read), `audit_log`, `human_review` (1/2/3 ratings gating skill promotion), `negative_eval`. No paper, no benchmark, no retrieval evaluation.
- Study when: you are building one long-running companion for one person, you want its memory inspectable as plain jsonl, and you need deletion that is real and provable rather than a flag — especially if backups are in scope, because the snapshot purge is the step most designs skip.
- Do not copy when: you need multi-tenancy, your corpus will outgrow substring matching over a flat file, or your correction requirement is that a withdrawn value stays withdrawn against an automatic writer. The first two are ceilings this design accepts deliberately; the third is one fingerprint lookup from being closed.

### [`reasonix`](../systems/reasonix/)

- Best idea: `SubjectKey` — name the *question* a fact answers (`project.package_manager`) and enforce one active value per scope and subject. That converts supersession from a similarity judgement into a lookup, and it gives an evaluation something exact to assert on. Beside it, `benchmarks/memorybench`: fifteen committed tasks whose classes are this atlas's own failure register — contradiction, stale, distractor, paraphrase, pin, plus three `v1miss` regressions preserved from a retrieval bug that shipped — where each `verify.sh` pairs a required string with a forbidden one (`grep -q "pnpm install" && ! grep -q "npm install"`). The forbidden half is an end-to-end negative retrieval assertion on agent behaviour rather than on a store method. The harness also runs a **memory-off arm** and reports paired pass counts, a `helpful` list, a **`harmful`** list and `overheadChars`. A benchmark with a column for the tasks memory made worse, beside its token cost, is what this atlas keeps asking for.
- Biggest risk: retraction is an instruction. The index folds into the durable prompt prefix once at boot and mid-session changes never mutate it, so `forget` archives the file and then queues *"disregard its loaded guidance and background-index entry for the rest of this session"*. The correction's enforcement is the model's compliance, not the store's refusal — the honest move under the cache constraint, and a real ceiling. Underneath it, supersession and deletion both key on the record, so the same wrong value saved again under a new name is a fresh fact.
- Most reusable component: `benchmarks/memorybench` itself. MIT, portable, and each task is a workspace plus a seeded memory directory plus a prompt plus a shell verification — no harness required to borrow the idea, and the closest thing to a shared memory evaluation this corpus has found.
- Maturity impression: MIT, ~696,000 lines of Go across a coding agent reachable four ways (terminal, desktop, browser, ACP), 10,032 test functions, 156 in `internal/memory`. Three marks: `scope_enforced` (reads rooted at a per-project directory), `human_review` (mined drafts that only save through an accept action), `negative_eval`. Four near-misses stated in the report: freshness classifies age rather than belief, the recall audit is the retrieval half of the audit pattern rather than the mutation half, supersession keys on the record, and there is no principal boundary. No paper, and no benchmark results committed — the instrument exists, the measurement does not.
- Study when: you want per-turn-free memory because your provider caches the prefix, or you are building any memory evaluation at all and want a task set and a verification style to start from.
- Do not copy when: you need multi-user boundaries, an audit of what changed, or a correction that binds an automatic writer. The last is not an oversight but the price of the cache decision, and it is worth understanding before paying it.

### [`cognitive-spatial-memory`](../systems/cognitive-spatial-memory/)

- Best idea: recency as a force rather than a filter. The docstring states it — *"No artificial limits. Recency = gravity, not exclusion"* — and the code means it: a cold memory is outweighed, never cut off by a threshold or a TTL, so enough mass can still bring it back. The ranking law is stated in the README as `F = T × m / d²` and implemented literally at `cognitive_space.py:504` (`gravity = temperature * mass / (d * d)`), with the vector form dividing by `dist³` because the displacement is unnormalised — the same law. A README equation that survives contact with the code is not the norm here.
- Biggest risk: **there is no way to remove anything.** No delete, forget, remove, purge, supersede or compact exists anywhere in the package, and no journal; `store`, `add_belief` and `add_memory` have no counterpart, so the API has no shape a caller could delete against. That is offered as *"a drop-in RAG replacement"*, and a store you cannot delete from does not drop into a pipeline that could. The same absence is why the report carries no capability mark: no status, no scope key, no validity time, no audit — one omission rather than seven.
- Most reusable component: `cognitive_space.py` as reading. 1,533 legible lines covering the fixed Johnson–Lindenstrauss projection to 8D, the KD-tree registry, the 512-anchor gravity field and the attention physics — the clearest statement of the mechanism in either of this author's repositories.
- Maturity impression: AGPL-3.0, **one commit**, ~4,300 lines, **no tests of any kind**, no eval, no benchmark, no paper. Its own docstring says the engine was *"originally developed as part of the Helix AGI cognitive architecture"* — [the parent](../systems/helix-agi/), where the same mechanism runs inside a system that has the surrounding machinery, so the two are one design rather than two. `docs/` holds 709 lines of line-by-line self-audit whose file links point at `file:///home/nemo/…`, resolving for no reader.
- Study when: you want to see decay expressed as mass and distance instead of a half-life and a cutoff, and you are reading for the idea rather than shopping for a dependency.
- Do not copy when: anything you store belongs to a user. There is no deletion, no scope key and no test, and the first is unrecoverable at the API level rather than a missing feature. If you want this mechanism inside a system that has the surrounding machinery, the parent is where it runs — with its own documented deletion gaps to weigh.

### [`kube-coder`](../systems/kube-coder/)

- Best idea: apply the scope predicate to **every arm of a fused retriever**, and say which ones. `search` runs FTS5 fused with a `sqlite-vec` KNN pass by normalized RRF, and the namespace allow-list and namespace root are enforced on the FTS pass, on the LIKE degradation *and* on the vector-only ids loaded by `_fetch_by_ids` — *"so a high-scoring out-of-scope memory can never be fused back in."* That is the failure a hybrid retriever invites: you scope the arm you thought about and fuse the one you did not. Relevance still leads and the caller's own scope wins only ties against the always-included `user` root, so a project chat can still reach `user.name`.
- Biggest risk: `upsert` clears the deletion flag it wrote. `soft_delete` sets `deleted_at` and appends a `memory_history` row carrying the op and the actor; writing the same `(namespace, key)` again sets `deleted_at=NULL` without reading it. The store records that a value was removed and does not use that record when the value comes back — record-keyed deletion, one lookup from being closed, with the row that would close it already written.
- Most reusable component: `memory_scope_test.py`. It does not stop at "a sibling project is out of scope": it attacks the escapes — a namespace that *shares a prefix* with the scoped root, SQL `LIKE` wildcards inside a scope, a literal underscore — and then asserts the same boundary separately on the LIKE fallback and the vector-only path. Testing the wildcard-escaping of your own scope predicate is rare in this corpus.
- Maturity impression: MIT, 752 commits; a Helm chart for browser-reachable Kubernetes dev workspaces, of which the memory is ~3,100 lines of Python plus a 575-line MCP server and 223 test cases across nine files. One SQLite file per workspace, WAL with `BEGIN IMMEDIATE` retries for its two writers, and a schema-repair step re-asserted at open rather than in a numbered migration because a database left at an intermediate version is *"exactly the one that needs healing"*. Four marks; withheld are an epistemic state (`confidence` is a ranking float), validity time, and the tombstone. `memory_history` is capped at 100 versions per memory, so the audit has a horizon.
- Study when: you fuse a lexical and a vector arm behind a tenant or project boundary, or you want to see a project that built per-prompt memory injection, retired it, and now strips the hook entry from config on every boot while still shipping the script for manual use.
- Do not copy when: you need a correction that binds, an epistemic state, or a soft delete that stays deleted — and note that identity is `(namespace, key)`, so the same fact written under two keys is two live memories and nothing detects the contradiction.

### [`munder-difflin`](../systems/munder-difflin/)

- Best idea: **verify the rewrite, not the model.** Memory is one markdown file per agent in three regions — pinned durable facts, a rolling recursive summary, the newest K sections verbatim — and when it outgrows its budget a headless `claude -p` summarises the evicted tail. The result is not trusted: back up losslessly *first*, rebuild, then run `verify()`, which checks that the file parses back into all three regions, that every pinned line survives, that it is **actually smaller** (a no-op condense is a failure), that it is non-empty and sane, and that the kept newest sections round-trip **byte-for-byte** — each failure returning a named reason. Backup-first plus atomic swap means a rejection is a pure no-op: *"the original file is left byte-for-byte untouched and the only side effect is a `condense-abort` log line."*
- Biggest risk: **there are no tests, anywhere.** `verify()` is exported, pure, and takes a plain argument object — the easiest function in the repository to pin — and the gate whose entire purpose is catching a non-deterministic component has no case exercising it. Underneath that, compaction is the only lifecycle: nothing can mark a line wrong, so a false claim is not corrected but eventually summarised, possibly surviving in compressed form.
- Most reusable component: `src/main/reflect.ts` — about 400 lines for the three-region file, the eviction, the summarizer prompt that hands the pinned block over *"for context only — do not rewrite it"*, and the gate. Transferable to any design where something will eventually rewrite an agent's markdown in place.
- Maturity impression: MIT, 666 commits, ~52,000 lines of TypeScript across an Electron desktop app that wraps a dozen terminal coding CLIs as a messaging hive; version 0.4.3, self-badged a working prototype. One mark, `audit_log`, for an append-only `log.jsonl` carrying `condense`, `condense-abort`, `compact`, `archive` and `drop`. Semantic recall is delegated to the [MemPalace](../systems/mempalace/) CLI over a shared palace and *"degrades silently to no-op"* when that binary is absent. Six blog posts about agent memory are prose, not evidence.
- Study when: you keep agent memory as markdown and something will compress it — the gate is the part worth copying, and the macOS TCC note explaining why the loop runs in the Electron main process rather than launchd is the kind of reasoning most repositories leave out.
- Do not copy when: one agent's material must stay away from another's. Isolation is deliberately absent — one shared palace, and a text fallback that greps every agent's `memory.md` including archived ones — because the premise is a hive that knows collectively.

### [`one-agent-many-hats`](../systems/one-agent-many-hats/)

- Best idea: **refuse the memory at write time, and let the rule file name the function that refuses it.** `assertBehavioural` (`src/memory/lessons.ts`) tests six patterns against a distilled lesson before it is stored — widening a tool, profile or permission; disabling a gate or approval; overriding instructions; escaping the workspace; asserting the state of the configuration — and throws `LESSON_REFUSED`, because a store containing access-widening text *"is one refactor away from applying it."* `packs/rules/lessons-behavioural-only.md` declares `enforced_by: memory.lessons.assertBehavioural`, and `src/registry/loader.ts` refuses to load any non-prompt rule whose enforcement point is not registered. Beside it, unproven lessons are injected into a deterministic hash slice of runs, so the runs without them are a control group and promotion reads outcomes rather than intentions.
- Biggest risk: **the accountability record never hears about memory.** `src/core/audit.ts` is a hash-chained, `0600`, single-stream log with `verifyAuditChain` and a closed vocabulary that includes `data.written` and `data.deleted` — and nine of its twenty actions have no producer, no memory mutation is recorded, and all thirteen call sites use the non-throwing `auditQuietly` while the awaited `audit()` the module's own docstring argues for is never called. Separately, `appendJsonl` takes a file mode and explains why conversation content must not exist world-readable; the lesson and takeaway stores call it without one.
- Most reusable component: the three-point defence against a memory that records the configuration. A run concluded network egress was off, the user turned it on, and later runs kept refusing to call `fetch_url` while the tool sat in the allowlist. The answer is a lesson pattern refusing the shape, `describesEnvironment` refusing it as a persona fact — narrow on purpose, a capability word **and** a state word — and a line in every system prompt: *"If you have a memory suggesting otherwise, it is stale — ignore it and call the tool."*
- Maturity impression: PolyForm Noncommercial 1.0.0 with an attribution notice, 29,719 lines of TypeScript with **zero runtime dependencies**, 298 tests across 32 files with CI, and 36 commits over three days (first commit 15 August 2026). Three marks — `trust_state` (draft/canary/active/disabled with confidence arithmetic), `human_review` (feedback as a CLI, REPL and HTTP verb), `negative_eval` (a committed assertion that a rejected takeaway never returns). A committed working paper is cited by section from the module docstrings; its scoping safeguard is delivered by the directory rather than by the `scope` field it names, and its conservative cold-start profile is one paragraph of prompt rather than the tighter budgets it describes.
- Study when: you want memory that writes itself and must not be able to widen what the agent may touch — the write-time refusal, the canary staging and the enforcement-point registry are three separable ideas and the first is about forty lines.
- Do not copy when: you need multi-tenancy (the boundary is a directory and the one scope field is inert), an audit of what was remembered and forgotten, or deletion keyed on a value — a rejected takeaway is filtered from retrieval and stays on disk past every retention clock in the system.

### [`bytechef`](../systems/bytechef/)

- Best idea: **order redaction ahead of persistence, and say so in the ordering constant.** `SanitizeTextAdvisor.getOrder()` returns `Advisor.DEFAULT_CHAT_MEMORY_PRECEDENCE_ORDER - 1`, so PII, secret-key and URL masking runs one step upstream of the chat-memory advisor and the text that reaches the repository is the masked text. Its test builds a spy advisor at the chat-memory order rather than asserting the integer, with the property in the assertion message: *"SanitizeTextAdvisor MUST run before chat-memory advisor, otherwise unsanitized text gets persisted."* Beside it, the agent throws at build time when two guardrails of one kind are configured, because two advisors at the same order make Spring AI's ordering undefined — a safety property that depends on a total order refusing the configuration that makes it a tie.
- Biggest risk: **the scopes around the one real key fail open to a live target.** `TenantContext.getCurrentTenantId()` is `ThreadLocal.withInitial(() -> "public")` and selects a Postgres schema; `EnvironmentContext.getCurrentEnvironment()` returns `PRODUCTION` when nothing is bound and logs it at `debug`. A missing binding is indistinguishable from a correct binding to the default, and `TenantRoutingS3ChatMemoryRepository` resolves `<prefix>-<tenantId>` and calls `ensureBucketExists`, so an unbound thread does not read the wrong place, it creates it. Chat memory has no scope key at all: `findConversationIds()` enumerates every conversation in the store, and the workflow editor renders that as a dropdown labelled with each conversation's opening message.
- Most reusable component: `KnowledgeBaseDocumentFacadeImpl.deleteKnowledgeBaseDocument`, for the **order** rather than the coverage. Vectors by id, then chunk content files, then chunk rows, then the source file, then the document row. The delete cannot be one transaction across three stores, so the sequence is the design: a crash leaves a row whose vector is gone — a chunk that cannot be found — where the reverse order leaves a vector whose row is gone, which is a chunk that still answers queries and can no longer be traced to a document.
- Maturity impression: Apache 2.0 with a commercially licensed `server/ee/` tree, 738,068 lines of Java across 6,998 files, 18,645 commits since 12 June 2016, at `v0.32.1-SNAPSHOT`; 1,817 test files and 5,466 `@Test` methods, with the knowledge base covered by Testcontainers integration tests against a real Postgres. Two marks — `scope_enforced` (`KnowledgeBaseVectorStoreWrapper` AND-s `knowledge_base_id` into every search and a caller filter can only narrow it) and `human_review` (chunk-level edit and delete, re-embedded on an event). The class carrying the first has no test file, and nothing writes two knowledge bases and asserts a search of one misses the other.
- Study when: you are choosing a workflow platform and want agent memory to be a component on the canvas rather than a subsystem you assemble, or you want a worked example of guardrail ordering that puts masking upstream of the write.
- Do not copy when: you need memory rather than storage. There is no epistemic state — `KnowledgeBaseDocument.status` is a pipeline stage no read path consults, so a chunk whose re-embed failed keeps answering with its pre-edit embedding while the document reads ERROR — no audit of what changed, no lexical arm, no fusion, and a conversation id that is an address rather than a permission.

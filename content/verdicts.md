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
**This page covers all 150 reports.**
<!-- END GENERATED VERDICT COUNT --> Six judgements each: the best idea,
the biggest risk, the most reusable component, an impression of maturity, and
the two that matter most to a reader deciding — when to study it and when to
walk away.

It is hand-written, unlike the [capability index](../capabilities/) and the
[comparative matrix](../compare/#2-comparative-matrix), which is generated from every report's frontmatter
and complete by construction. So completeness here is a fact about today rather
than a guarantee: nothing fails the build if the next report arrives without an
entry, and `scripts/check_homepage.py` only notices the count in the sentence
going stale. A verdict missing in future means nobody wrote the paragraph,
not that a system was judged and found unremarkable — the same distinction the
[rubric](../methodology/atlas-rubric/) enforces for capability marks, where the
build *does* fail if a report omits the key.

<div class="filter-row" role="group" aria-label="Find a system verdict">
  <label class="filter-legend" for="verdict-search">Find</label>
  <input class="matrix-search" id="verdict-search" type="search" autocomplete="off"
         placeholder="system name…" aria-describedby="verdict-count">
</div>

<p class="result-count" id="verdict-count" aria-live="polite"></p>

## System verdicts

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

### `core-memory`

- Best idea: epistemic grounding caps the confidence ladder, so a speculative record cannot reach canonical status by any amount of use.
- Biggest risk: correction is record-keyed, so supersession and rejection do not stop re-extraction from retained turns.
- Most reusable component: the grounding-to-ceiling table plus the monotonic class, which is a lookup and a `min()`.
- Maturity impression: the largest and most specification-like system in the atlas, with 300+ tests tracking the risky logic and committed benchmark harnesses.
- Study when: you need to explain why an incorrect memory never became permanent, and want the answer to be structural.
- Do not copy when: you cannot carry the surface — thirteen subpackages and forty store-ops modules is a real maintenance budget.

### `memanto`

- Best idea: a conflict workflow that terminates in a human decision, including `keep_both` and a human-authored `manual` resolution.
- Biggest risk: detection is one unmeasured LLM pass, and resolution deletes without a tombstone, so scheduled extraction can undo it.
- Most reusable component: the five-action resolver plus the bounded-scan instruction that keeps the nightly pass linear.
- Maturity impression: a real service with CLI, web UI, MCP and four framework integrations, and an unusually on-topic test tree.
- Study when: you have contradiction detection and no idea what to do with the flags it produces.
- Do not copy when: you need trust state or ranking you can inspect — storage is the vendor's own service.

### `memory-engine`

- Best idea: agents are access-control principals, and a delegated agent grant clamps to `least(agent, owner)` at every path, so over-granting cannot escalate.
- Biggest risk: no trust state, supersession, or tombstone — it governs who may read a memory and knows nothing about whether it is true.
- Most reusable component: the `tree_access` model with the agent clamp, and authorization evaluated inside the ranking query.
- Maturity impression: a serious database-native service with committed SQL benchmarks, access diagnostics, and unusually candid design notes including a negative result on RLS.
- Study when: agents write to shared memory and you cannot say from the schema which memories each may read.
- Do not copy when: you need correction semantics — `replace` overwrites in place and leaves no history.

### `ai-memory`

- Best idea: a `Handoff` with an open/accepted/expired lifecycle, typed sender and recipient, and an `open_questions` list — memory of what is *not* known.
- Biggest risk: hooks re-capture every session and supersession is page-keyed, so a deleted page returns through the path that first produced it.
- Most reusable component: `handoff.rs`, which is small and independent of the rest of the system.
- Maturity impression: broad and well packaged, with harness adapters for eight agents and committed prior-art analyses of four systems in this atlas.
- Study when: work is interrupted and resumed in a different harness, and re-explaining the state is the actual cost.
- Do not copy when: you need trust state — and do not assume its `do_not_answer_from` tag does anything; it appears only in a test fixture.

### `ctx`

- Best idea: a write-scope guard on the consolidation pass, with one crossing gated on the disposition rather than the caller, plus refusals that carry a registered reason.
- Biggest risk: correction is structural folding with no tombstone, so a dream can re-propose what a human folded away.
- Most reusable component: `WriteScope`, and the corrupted-artifact regression corpus, which any system with an LLM rewrite path could adopt in an afternoon.
- Maturity impression: dense tests in the packages that matter, an append-only ledger, and a 61,000-line CLI wrapped around them.
- Study when: a background model pass can write into the user's own repository and you have no answer for where it may write.
- Do not copy when: you need ranked retrieval — there is no ranker, only progressive disclosure over files.

### `optmem`

- Best idea: no background work at all — consolidation is requested inline in the output of `note`, so write-to-readable lag is zero and nothing rewrites memory unobserved.
- Biggest risk: no licence file, so nothing here is reusable; and a wrong memory is permanent, because the log is never edited.
- Most reusable component: the `cover` geometry — one parameter, closed form, and no compression at all while everything fits.
- Maturity impression: 860 lines with a 611-line test file, and the only committed footprint-and-latency figures in the atlas.
- Study when: you are about to build a consolidation queue and have not asked whether you need one.
- Do not copy when: you need to fix a mistake — OptMem can always tell you what was written and can never repair it.

### `memvid`

- Best idea: immutability as the correction mechanism — a supersession is a link, not an overwrite, so `get_at_time` and session replay come from the format rather than a bi-temporal schema.
- Biggest risk: the loudest quality claims in the atlas ("+35% SOTA on LoCoMo") with no committed raw artifacts found at this commit.
- Most reusable component: `entity:slot` cards with a declared cardinality, which turns contradiction detection into a lookup and tells you whether a second value is a conflict or an addition.
- Maturity impression: a serious file format with WAL, footer recovery, a 1,687-line doctor, and a deployment story of one binary and one file.
- Study when: you need to answer "what did the agent believe when it did that", which nothing else here can.
- Do not copy when: you need multi-tenant scope or epistemic status — the ACL is thin and there is no trust state.

### `memoryos`

- Best idea: the promotion rule is a written formula with named coefficients, and the LoCoMo harness ships with its dataset committed beside it.
- Biggest risk: heat sums frequency, interaction length and recency into one scalar with weights of 1/1/1, and a second LFU counter can disagree with it about the same segment.
- Most reusable component: the shape — tiers with an explicit, computable promotion signal — rather than the formula.
- Maturity impression: a legible research implementation with an MCP server, a vector variant and a playground around a 2,100-line core.
- Study when: you want the tiered architecture in a form small enough to read in an afternoon, or a base for experiments on promotion policy.
- Do not copy when: real users are involved — no provenance, no correction, no audit, and a merged profile string makes a deletion request unanswerable.

### `memu`

- Best idea: rank the slice, return the file — the embed/search unit and the context payload are different sizes, and a file scores as the max of its segments.
- Biggest risk: no epistemic model at all, and no scope key in a layer that serves seven different hosts from one store.
- Most reusable component: the three-method backend protocol, plus keyset pagination on immutable domain identity so a walk under concurrent writes neither skips nor repeats.
- Maturity impression: unusually disciplined for its size — schema comments cite the ADRs that produced them, and a denormalized column carries its safety argument; the limit of that discipline is a decision record asserting a telemetry disclosure that is not in the tree.
- Study when: you want one memory across several coding agents and a read path that is cheap, predictable and model-free.
- Do not copy when: memory has to be trusted, corrected, or separated between users — or when you install for other people and cannot make a vendor-telemetry disclosure the install guide omits.

### `openworker`

- Best idea: an explicit when-to-remember policy, written because models without one fail bimodally — they either never save or save what the repository already records.
- Biggest risk: none of it is enforced or observable, so the first sign the model stopped following the policy is memory quality nobody can explain.
- Most reusable component: the guidance paragraph itself, especially "use absolute dates, never yesterday" and "don't save what the repo already records".
- Maturity impression: a large, carefully built agent with permissions, audit and unattended operation, and a memory subsystem of 260 lines that touches none of it.
- Study when: deciding whether to spend the next day on a pipeline or on the prompt that governs one.
- Do not copy when: you need ranking, a correction record, or any guarantee the policy was followed.

### `qwen-code`

- Best idea: a team tier committed to the repository, with secret-bearing writes to it refused unconditionally — the guard ignores the feature flag that governs the tier, because the directory is under version control either way.
- Biggest risk: three forget paths and no value-level tombstone, in a system whose extraction re-reads the sessions that produced the memory.
- Most reusable component: the extraction cursor with a processed offset, and recording `noop` as an outcome so "ran and changed nothing" is distinguishable from "did not run".
- Maturity impression: ~9,000 lines with a test beside nearly every module, and comments that read as scar tissue — per-operation kill signals for git, `execFile` with no shell.
- Study when: a team wants shared agent memory and does not want to stand up a service to get it.
- Do not copy when: corrections must survive a background pass.

### `opencode`

- Best idea: a compaction hook that lets a plugin append context as well as replace the prompt — the moment a memory system most needs, and one few hosts expose.
- Biggest risk: no memory contract at all, so plugins couple to the SQLite schema instead of the API, and a migration the host is entitled to make silently breaks them.
- Most reusable component: handing plugins the system prompt as `string[]` rather than a concatenated string, so two plugins compose instead of colliding.
- Maturity impression: a large, well-built coding agent with an extensive plugin surface, whose memory-relevant hooks are both marked experimental.
- Study when: you are building a host and deciding whether seams are enough without a domain contract.
- Do not copy when: you want the host to enforce scope or deletion — there is nothing here to enforce them with.

### `nooa-memory`

- Best idea: every access records the score components that produced it — `{rel, rec, imp, spread}`, the rank, the query and the reader — so "why was this retrieved" is a lookup rather than a reconstruction.
- Biggest risk: the access log is a capped ring on the record, so the formative accesses that explain how a memory became established are the first to be lost.
- Most reusable component: keeping rehearsal separate from belief — retrieval bumps a `strength` counter that slows forgetting and leaves `confidence` untouched.
- Maturity impression: 4,200 lines with 23 test modules, ACT-R and Ebbinghaus implemented literally rather than gesturally, inside an NVIDIA labs framework.
- Study when: you need memory whose ranking is explainable after the fact, or you want prospective memory — `intent` and `todo` are types nothing else here has.
- Do not copy when: you need correction — archival is a record flag, and a decayed memory can be re-authored with nothing to consult.

### `neo4j-agent-memory`

- Best idea: reasoning traces recorded via a context manager, so a raised exception becomes the outcome — failure memory proportional to coverage rather than to caller discipline, with an indexable error kind on top.
- Biggest risk: bi-temporality and supersession cover preferences only, and nothing is keyed on a rejected value.
- Most reusable component: the trace context manager plus `ReasoningStepWithContext`, which never returns a step without its parent's outcome.
- Maturity impression: a Neo4j Labs package with MCP, CLI, Strands and OpenAI Agents integrations, a benchmarks tree, and local NER extraction keeping the frequent write path off the token budget.
- Study when: several agents should share one view of the world, and operational history is the thing worth pooling.
- Do not copy when: corrections must survive re-extraction.

### `elastic-atlas`

- Best idea: a committed retrieval eval matched on document id rather than judged by a model, so Recall@k and MRR are arithmetic and reproducible — shipped beside a stress test.
- Biggest risk: a research demo by its own description, with synthetic personas and an ungated single-pass consolidation that writes both facts and playbooks.
- Most reusable component: the eval and stress-test scripts, which are more transferable than the memory layer.
- Maturity impression: a demo that measures itself more than most production systems in this atlas do.
- Study when: you want the clearest small example of the episodic/semantic/procedural split, or an eval design you can actually rerun.
- Do not copy when: you need correction, trust state, or an audit trail — none is present.

### `nemoclaw`

- Best idea: a per-agent state contract that says which directories are snapshotted, which are wiped, which are regenerated and which the user owns — written down rather than left to whoever wrote the backup script.
- Biggest risk: memory is snapshotted and restored verbatim, so a restore reinstates deleted memories and nothing above is told.
- Most reusable component: excluding state that is cheaper to regenerate than to restore, with the failure it prevents named — an argument that may apply to derived memory too.
- Maturity impression: infrastructure with guards that validate their own helpers, and issue numbers cited in the comments for the two decisions that would otherwise look arbitrary.
- Study when: you operate agents rather than build memory for them, and want to know what memory looks like from underneath.
- Do not copy when: you want a memory system — it has none, and its product page correctly credits memory to the agents it wraps.

### `daimon`

- Best idea: the model's trust label is a claim the code falsifies — a verbatim item's quote is grepped against the transcript and demoted on a miss, and an outcome claim with no tool result cited is demoted even when its quote verifies.
- Biggest risk: the live working set is one checkpoint per project, so anything carry drops is reachable only through a lexical index with no semantic arm, and the committed retrieval numbers are modest.
- Most reusable component: `verify_quotes` and `ground_outcomes` in `serializer.py` — about 200 lines that make an extraction's own provenance mechanically checkable.
- Maturity impression: 18,200 lines of source under 40,300 lines of tests, a research logbook, a scar file per landmine, a benchmark reporting policy stricter than most vendors', and a replay A/B rig with a placebo arm that has been used to refute three of the project's own hypotheses.
- Study when: you want cross-session continuity for a coding agent, or you want to see what taking trust classes seriously actually costs in code.
- Do not copy when: you need memory within a session, semantic retrieval, or a shared service — none of the three is here or planned.

### `memory-project`

- Best idea: forgetting has two speeds and only the slow one destroys — `prune()` archives to a cold tier that a specific enough cue can still reach, `purge()` is a separate deliberate call, and the source says plainly which is which.
- Biggest risk: `purge()` is documented for accidentally-jotted secrets and implemented as a Chroma `col.delete`, so the embedding stays in the index file; and with no tombstone, re-jotting a purged claim re-admits it at full stability.
- Most reusable component: `prune()` and `purge()` together — about forty lines that remove the false choice between growing forever and destroying on "forget".
- Maturity impression: 3,113 lines, 26 commits, AGPL-3.0, 16 regression assertions on the decay maths and nothing testing the hooks. Small and legible, with the tuning constants named and grouped rather than scattered.
- Study when: you want a forgetting curve with a reversible archive tier, or an injection boundary that distinguishes assert from hedge from silence.
- Do not copy when: anything needs a scope boundary — topic is a ranking boost and never a filter, by design — or when a memory has to be markable as wrong.

### `hippo-memory`

- Best idea: the scope boundary is enforced in the query on the read path and *deliberately suspended* for consolidation, with the suspension fenced at the transport layer instead — `/v1/sleep` is loopback-only and admin-gated, and the 403 names the reason and the version that introduced it.
- Biggest risk: `stale` sits in a union with `verified`, `observed` and `inferred` but is derived from thirty days of disuse rather than from evidence, so one field mixes how a belief was formed with how recently anyone wanted it.
- Most reusable component: the retention prune in `audit-prune.ts`, which emits its own `audit_prune` row carrying cutoff, count and dryRun so the audit trail explains its own hole.
- Maturity impression: 42,482 lines under 376 test files with a real-database test convention, a migration ladder past twenty-five steps, and incident comments naming what each repair was for — beside a tagline about forgetting that the correction model does not implement.
- Study when: you need multi-tenant memory where different transports carry different trust models, or you want a worked example of ranking that fuses lexical, vector and derived-quantity arms.
- Do not copy when: correction has to be durable — supersession hides a row and re-assertion is unguarded — or when you want a small dependency.

### `7layermem`

- Best idea: seven memory types separated at the schema rather than by a type column, each table annotated with the cognitive category it stands for, so "which kind of memory is this" is answered by the table name.
- Biggest risk: the layers are destinations rather than a lifecycle. Nothing promotes, expires or demotes between them, six of the seven have no delete path, and deleting a conversation thread leaves its summary behind.
- Most reusable component: the seven `CREATE TABLE` statements with their annotations — a legible taxonomy that costs nothing at this scale.
- Maturity impression: 7,016 lines, no licence file at this commit, no migrations, and a test suite that re-declares the schema with its own `CREATE TABLE` strings rather than calling the store manager.
- Study when: you want to hold an entire typed-memory design in your head at once, or you are deciding whether to split memory types across tables.
- Do not copy when: you need any correction path, a scope beyond one conversation thread, or a licence.

### `cognicore`

- Best idea: `state TEXT DEFAULT 'candidate'` — a memory arrives unassessed rather than believed, which a confidence float cannot express, plus a utility ledger separating retrieved from used from *ignored*.
- Biggest risk: scope is filtered in Python after the backend returns, so any limit the backend applied was applied to the unscoped set and a scoped read can silently come back short.
- Most reusable component: the four column groups on `memory_entries` — content, epistemic, scope, and provenance-plus-utility — which put `creation_reason` and `source_component` in the schema rather than in a metadata blob.
- Maturity impression: MIT, 79,439 lines, six backends behind one contract, a benchmark programme and a paper directory — beside fourteen loose `test_*.py` provider smoke files and two committed `.db` files at the repository root.
- Study when: you want an epistemic state in the schema rather than in a prompt, or a retrieval feedback signal that records what the agent declined.
- Do not copy when: the scope boundary has to hold under a limit, or you want a dependency rather than an environment.

### `alma-memory`

- Best idea: an anti-pattern table carrying `why_bad` and `better_alternative` beside the pattern itself — the only place in this corpus where a correction record holds both the reason and the replacement.
- Biggest risk: `VerificationStatus` — verified, uncertain, contradicted, unverifiable — is computed at retrieval and never written to any column, so nothing can query for contradicted memories, no pass can act on them, and the same contradiction is re-derived on every read.
- Most reusable component: `VerificationMethod`, which separates checked-against-an-authority from checked-against-our-own-memories from guessed-from-a-number — three claims most systems collapse into one score.
- Maturity impression: 106,594 lines on PyPI, MIT in the manifest with no LICENSE file in the tree, and one schema maintained by hand in two dialects with nothing comparing them.
- Study when: you want a memory that learns operating heuristics from task outcomes, or the richest worked example of storing what not to do.
- Do not copy when: an epistemic judgement has to persist beyond the call that produced it.

### `promptx`

- Best idea: one SQLite database per role, opened from the role's own directory, so isolation cannot be forgotten — crossing it would mean opening a different file rather than omitting a predicate.
- Biggest risk: `strength` is the only epistemic field, so a wrong engram and an unused one decay identically and nothing records that anything was ever judged.
- Most reusable component: the `cue_index` — memories addressed by the words that lead to them rather than by embedding proximity, with `ON DELETE CASCADE` keeping the index from outliving its target.
- Maturity impression: MIT, 63,237 lines, twenty-one cognition modules with a Cucumber suite over them — and `CREATE TABLE IF NOT EXISTS` with no version column across a store that is per-role, so the first schema change is a manual migration everywhere.
- Study when: you want associative recall by cue rather than similarity, or the cleanest example here of scope enforced by file boundary.
- Do not copy when: you need correction of any kind, or your scope is a person rather than a role.

### `echo-agent`

- Best idea: `provenance_guard` — every memory records which write path created it, ranked `user_stated` 3, `consolidated` 2, `model_inferred` 1, unknown 0, and a write is refused unless the actor ranks at or above its target. A model-inferred claim cannot overwrite a fact the user stated, and the label belongs to the path rather than the payload, so the model cannot nominate its own output as user-stated.
- Biggest risk: the guard governs authority, not truth. Supersession is record-keyed, so a value already adjudicated wrong can be re-asserted by any path with adequate rank — including the user restating a claim they previously corrected.
- Most reusable component: about fifteen lines of `_SOURCE_PRIORITY` and `provenance_guard` in `memory/types.py`, plus the audit call on the *refused* write path that lets you verify the guard is running.
- Maturity impression: 76,594 lines under 360 test files, eighteen memory modules named for the problems this atlas tracks, and a graph layer added at migrations 6 and 8 rather than designed in. Primary documentation and several load-bearing comments are Chinese.
- Study when: you need to answer "whose claim wins" structurally rather than by prompting, or you want contradiction that adjudicates instead of flagging.
- Do not copy when: you want a memory library — this is an agent, with no MCP or HTTP surface for the memory layer — or when correction has to survive re-assertion.

### `helm`

- Best idea: a first observation is capped at 0.7 confidence and can only rise 0.05 per independent repeat of the same value, so the store cannot record a single sighting as certain — the whole gate is about fifteen lines.
- Biggest risk: the confidence it computes never reaches the model. The per-turn block is `- (kind) key: value` under *"use these, never contradict them"*, which promotes every provisional guess to an assertion at the last step.
- Most reusable component: `workspace/memory/` — four scripts, a JSON-on-stdout CLI, no dependency beyond Node 22's built-in `node:sqlite`, and no coupling to the rest of Helm beyond a path.
- Maturity impression: uneven and legible. A committed 25-issue self-audit with `file:line` and reproduction steps, every issue I checked closed at this commit, and smoke tests that assert ranking and the system's own noise gates — beside a schema that exists as guarded `ALTER`s in five files and three readers that forgot the active-row predicate.
- Study when: you want the cheapest working epistemic model in this atlas, or you are building a single-owner local agent and want more than a JSON blob.
- Do not copy when: the store will pass a few hundred active facts (the recall window is 500 rows ordered by recency), more than one person or project shares it (there is no scope to add), or deletion has to survive re-derivation (`forget` and prune are hard deletes with no record).

### `csm`

- Best idea: `context_injection_items` — every candidate for the injected block recorded with its position, score, a disposition of `injected | trimmed | omitted` and a reason code, so "why didn't the agent know that?" becomes a query instead of an argument.
- Biggest risk: correction and retrieval have drifted apart. Merge sets `superseded_by`, archive sets `archived_at`, and the search WHERE-clause builder filters on neither — so the governance report calls the store clean while search keeps returning the duplicates.
- Most reusable component: `src/work-ledger-lineage.ts` — about 130 lines of line-hash multiset arithmetic that decide whether an edit the agent made still exists in the file, with no model and no diff library.
- Maturity impression: finished-looking in a way it is not. 55,000 lines across 392 files, 46 tables, 189 test files, a checksummed migration ledger that fails fast on an unknown history, a committed backup/restore drill in the release gate — beside a beliefs layer that admits only a status nothing writes, a review queue whose table has no INSERT, and a self-model reporting 3,849 successes and zero failures because it counts exit codes.
- Study when: you want to see how far deterministic capture scales, or you want the two mechanisms above, which are each a few hundred lines and copy cleanly.
- Do not copy when: more than one person or tenant will share the deployment (there is one scope axis and a cross-project self-model), you cannot run Postgres and a local embedding server, or you need the SQLite mode to do hybrid retrieval — it degrades to substring matching without saying so.

### `graphify`

- Best idea: a lesson is `tentative` until a *second distinct result* confirms it, and `preferred` only then — "one save can't mint a trusted lesson", implemented as a counter and a comparison.
- Biggest risk: the dead-end list is enforced by asking the model nicely. The skill says "don't re-derive it next time"; no code path reads it, so the strongest-sounding promise in the design is a Markdown bullet.
- Most reusable component: the staleness check in `reflect.py` — a content-only SHA-256 of the cited node's source file, stored with the lesson and recomputed on every read, biased to over-flag on purpose and with three tests guarding against spurious fires.
- Maturity impression: 3,308 test functions against 15,959 lines of source, byte-stability tests on both derived artifacts, and a committed regression guard that its own lessons file cannot be re-ingested as evidence — a bug two other systems here shipped first.
- Study when: you want the smallest complete work-memory loop in this atlas, or you need a verification mechanism cheap enough to run on every read.
- Do not copy when: you need memory about anything other than "how a query over this project turned out" — there is no user, no preference, no entity, and nothing crosses a project directory.

### `lorekit`

- Best idea: an audit log made immutable by the absence of a policy — a SELECT and an INSERT policy on the table and deliberately no UPDATE or DELETE, so the invariant is enforced by RLS rather than by everyone remembering not to write the statement.
- Biggest risk: that log records `{scope, key}` over an in-place upsert, so it proves a memory changed and cannot show what it replaced — and archiving frees the address, which is the inverse of a tombstone on the operation a user reaches for when a lesson is wrong.
- Most reusable component: `packages/mcp-core/src/scope.ts` plus the `org_scope_bindings` routing — a validated four-level scope key, an authenticated tenancy boundary, and a table that makes "this repo's lessons belong to the team" a row instead of a convention.
- Maturity impression: 37 migrations written like design documents with numbered decisions, 1,184 tests, RLS on every table, hashed and scoped tokens, HMAC-verified webhook ingest with an explicit no-timing-oracle note — beside five entrenchment guards of which one is enforced by code.
- Study when: you need shared agent memory for more than one person and have to answer who changed what, or you want the cleanest separation of a scope key from a tenancy boundary in this atlas.
- Do not copy when: you are one developer (the parts worth paying for are the multi-user parts), or your problem is deciding which lesson to trust — LoreKit is an excellent filing cabinet with an excellent lock and no opinion about the contents.

### `clio`

- Best idea: a trust tier that costs an entry something in three channels at once — a 0.3x ranking multiplier, an `[UNVERIFIED]` badge in the rendered prompt, and a halved age-out — rather than only filtering.
- Biggest risk: the sybil boundary is `agent:session` and a session restart mints a new session, so one agent running twice supplies both votes. The library also still defaults to `unknown:unknown` when the identity vars are unset — the fix lives in the two shipped entry points, not in `LongTerm.pm`, and a test pins the default as intended.
- Most reusable component: `corroboration_sources` as an array of `agent:session` identities rather than a count — the only place in this atlas where "two independent sources" is checkable rather than assertable.
- Maturity impression: 102,862 lines of pure Perl with no CPAN dependency, atomic writes throughout, a stated memory-poisoning threat model — and, since 31 July 2026, a 412-line regression file on the tier mechanism that had none. I ran it: 92 assertions, none failing.
- Study when: you want the best-shaped answer here to "how do I stop my agent believing something it made up once", and a short lesson in what an unset variable does to it.
- Do not copy when: more than one person shares the store (there is no scope key and every entry is stamped `source_agent: 'unknown'`), or you need memory that survives being wrong — decay, age-out, dedup and prune all delete without a record.

### `powermem`

- Best idea: forgetting split into four separate predicates — `should_promote`, `should_forget`, `should_archive` and `reinforce`, each with its own threshold — so archival is a different decision from forgetting rather than the same score crossing a second line.
- Biggest risk: a `history` table with `old_memory`, `new_memory` and `actor_id`, maintained by migrations and written by nothing in the repository. A schema that implies an audit trail will be read as one, including by any capability matrix built from migrations.
- Most reusable component: `_get_decay_rate_for_type` and `_build_db_filters` — a per-type decay rate is a few lines for a large gain in realism, and pushing the scope keys into the backend's own query is the difference between a boundary and a convention.
- Maturity impression: 128 test files across storage backends, FTS, MCP and the CLI installer, a broad integration surface (Python SDK, HTTP server, MCP, CLI, VS Code, Claude Code), and the atlas's most complete forgetting-curve implementation — beside an unwired history table and a rotating file log with `backupCount=5`.
- Study when: you want retention to be a tunable model rather than a TTL, or you want to see decay, reinforcement, promotion and archival separated into decisions you can measure independently.
- Do not copy when: you need read replicas or deterministic reads — search writes to the store by design, and that is not a flag you can disable without losing the retention model — or a memory has to be evidence, since a decay score is not a record that something was wrong.

### `acontext`

- Best idea: the write is gated on a terminal outcome — a CHECK constraint on the status vocabulary, an enqueue that fires only on `success` or `failed`, and three committed tests asserting the other cases write nothing. It is the difference between a skill library and a transcript summary.
- Biggest risk: retrieval depends entirely on the agent choosing to look. There is no automatic injection, so recall rests on names, descriptions and willingness — three things that are hard to measure and easy to get quietly wrong.
- Most reusable component: the trigger tests in `core/tests/llm/` — the gate is cheap to copy and the tests are what keep it implemented.
- Maturity impression: 43 test files aimed at the learning machinery rather than the plumbing, an end-to-end pipeline suite, and Markdown skills exportable as a ZIP so the memory outlives the vendor.
- Study when: your agents run repeatable tasks with a status you can trust, and you want the accumulated know-how greppable rather than embedded.
- Do not copy when: your tasks end ambiguously — the gate never fires and you have deployed a queue, a sandbox and a Postgres for nothing — or you need conversational or preference memory, which it has no unit for.

### `adk-python`

- Best idea: scope in the signature rather than in the query. `app_name` and `user_id` are required keyword arguments on every read and write, so a scope bug is a `TypeError` rather than a leak.
- Biggest risk: the contract has no removal method. Every application written against it inherits the gap, and no provider can fix it — only a breaking interface change can.
- Most reusable component: the `BaseMemoryService` signature itself, minus the omissions. It is the interface most agents are written against and the one to diff your own against.
- Maturity impression: 61 memory test functions across three service implementations, a default in-memory service whose docstring says "prototyping purpose only", and an `add_memory` that raises `NotImplementedError` naming the alternatives rather than faking it.
- Study when: you are designing a provider interface and want the scope handling to copy verbatim.
- Do not copy when: deletion is a compliance requirement — at this commit the framework will not help, and the answer will be provider-specific code that outlives your abstraction.

### `agent-afk`

- Best idea: the verification status is in the string the model reads. A fact arrives either with a citation or tagged `[unverified]`, and a supersession carries the old citation forward with a warning that it may be stale.
- Biggest risk: the gate is behind `AFK_MEMORY_EVIDENCE_GATE=1`, so the default build stores codebase facts with no citation and marks nothing. The best mechanism in the system is off unless you find the flag.
- Most reusable component: about two hundred lines of evidence gate that fits in SQLite, with the category taxonomy that makes it tolerable in daily use.
- Maturity impression: 129 test cases unusually well aimed — a 333-line suite covering all four supersession outcomes across all four categories, plus the UNIQUE-collision duplicate path and the not-found throw.
- Study when: you are building a coding agent and want provenance without a graph.
- Do not copy when: two people share the database — the archive is cross-session with no scope filter, which is right for one developer and wrong immediately after that.

### `agent-framework`

- Best idea: fail-closed owner scoping checked three ways, with a post-resolve containment assertion — the best filesystem scoping in this atlas — and `session_ids` provenance recorded on every topic.
- Biggest risk: the provider contract declares neither deletion nor scope, so a third-party provider inherits AutoGen's gap, and compression is the only correction path.
- Most reusable component: organising durable memory by topic rather than by time, with the index split from the content.
- Maturity impression: about 1,357 lines of tests on the harness memory alone, aimed at state round-trips, consolidation scheduling, disk-full and misconfigured-client failures, and the scope boundary.
- Study when: you are in the Microsoft stack and want the context-provider seam, or you want a per-user assistant whose correction need is "rewrite the topic".
- Do not copy when: you need to prove a deletion, hold a claim you are unsure about, or answer what the system believed last month — there is no unit below the topic file to attach any of that to.

### `agent-memory-supabase`

- Best idea: validity time and record time in the same row, with an `updated_at` trigger that refuses to fire on access-stat touches so a read cannot masquerade as an edit.
- Biggest risk: the per-user RLS policies are commented out, so the only enforced posture is server-sees-everything — and there are no tests at all to notice.
- Most reusable component: the similarity floor on the text lane, with the RRF failure it prevents written into the comment beside it.
- Maturity impression: 898 lines, better reasoned per line than most frameworks here and readable in an hour — with no test directory, no fixtures and no harness, despite `use_blended` and `track_access` existing to make evaluation clean.
- Study when: you are on Supabase, want to own the SQL, and your memory is one project or one user.
- Do not copy when: you are multi-tenant before uncommenting and testing Posture B, or you need to prove a deletion — soft delete plus supersession leaves the content in the table with no record that a value was rejected.

### `agno`

- Best idea: supersession that is *judged* rather than inferred from a key collision — thresholded, reversible, and tested, with the superseded row kept and what replaced it named.
- Biggest risk: `optimize_memories` defaults to `apply=True` and replaces every memory with one model-written paragraph. Decide who can reach `POST /memory/optimize` before someone finds the button.
- Most reusable component: the framework stamping time rather than the model, and the split between guidance and data with a test on the split.
- Maturity impression: 304 test functions across 17 files plus integration suites for the manager, agent memory, team storage and OS routes — and comments that document the corruptions that produced the code.
- Study when: your memory needs are typed and modest, correction is supersession, and you want an agent platform where the learning stores come as a good default.
- Do not copy when: you need retrieval quality — there is no ranking to tune and relevance costs an LLM call per search — or deletion has to be provable, since there is no audit and no tombstone.

### `aukora-kernel`

- Best idea: the receipt is appended and fsynced *before* the row, and the chain hashes the content hash rather than the plaintext — so right-to-be-forgotten erases the plaintext without breaking the proof.
- Biggest risk: forget records a rejection it never consults, so the same content can be written again; and the declared tiers are never applied on the read path.
- Most reusable component: the write path alone — the authority gate, receipt-first ordering, chained hashes over content hashes, and RTBF-by-erasure — which transplants without the rest.
- Maturity impression: the best negative-assertion suite in the atlas after Verel's, testing authority rather than recall; and a project that says PROVEN-LAB in four places rather than letting you discover it.
- Study when: the provenance of a write matters more than recall quality — regulated work, audit-facing tooling, anywhere "prove this memory was authorized and unaltered" is a real question.
- Do not copy when: you need to find the relevant thing among fifty thousand. Chain-ordered retrieval and a whole-file rewrite per write put a low ceiling on corpus size, and the authors say so.

### `autogen`

- Best idea: `update_context` as a first-class injection seam, in a protocol small enough to implement in an afternoon.
- Biggest risk: `MemoryContent` has no identifier, so targeted deletion is not expressible and `clear()` is the only removal verb. Scope is an adapter's option rather than the contract's.
- Most reusable component: the `update_context` seam itself, worth designing around even where the rest is not.
- Maturity impression: 56 memory test functions across the core and the ext adapters, proportionate for an interface package — with a default implementation that injects the entire store.
- Study when: you want the clearest demonstration in the atlas that an interface's omissions are permanent in a way an implementation's are not.
- Do not copy when: you are designing a provider interface. A better adapter cannot add an id to `MemoryContent`, and every agent written against the protocol inherits the ceiling.

### `buzz`

- Best idea: the relay can neither read content nor correlate slugs, and a memory value is updated by compare-and-swap — with a careful distinction maintained between confirmed-absent and unknown.
- Biggest risk: there is no retrieval. The design works while an agent can hold its own namespace in mind, and there is no growth path that does not mean designing retrieval from scratch over ciphertext the relay cannot read.
- Most reusable component: the confirmed-absent-versus-unknown distinction, which most systems here collapse into an empty result.
- Maturity impression: 34 tests in `engram.rs` alone and they are the right ones — round-trip encryption, oversized bodies refused at build time, head selection with an event-id tiebreak, and eighteen cases pinning reference extraction.
- Study when: you want a small, legible, model-free memory layer with an unusually careful concurrency story and a spec you can reimplement.
- Do not copy when: memory has to scale, or you need to explain a memory's history or prove a correction stuck — the substrate threw the evidence away.

### `camel`

- Best idea: a three-part contract — block, memory, context creator — small enough that a custom store satisfies it in an afternoon, with the system message pinned through truncation.
- Biggest risk: the retrieval query is whatever the last user message happened to say, and `LongtermAgentMemory` cannot delete a single record from its vector store.
- Most reusable component: the `AgentMemory` ABC as a seam — swapping one of this atlas's fact-level systems in behind it is a day's work.
- Maturity impression: 868 lines across four test files covering round-tripping, windowing and the `NotImplementedError` paths, with no negative retrieval assertion — which follows from having no scope filter to assert about.
- Study when: you are already using CAMEL and your agents are short-lived, single-tenant, and their memory is genuinely their transcript.
- Do not copy when: you are multi-tenant without adding a filter yourself, or a user can ask you to delete something.

### `cortex`

- Best idea: the gate is on the **read**, not the write. A secret-classified hit needs a supervisor decision and then a human yes, and a denial returns an error rather than a quietly redacted result.
- Biggest risk: a complete `MemoryPrivacyPolicy` — allowed tiers, PII redaction, retention — lives in a process-local `Map` and is consulted by nothing.
- Most reusable component: the injectable approval gate that fails closed on refusal, plus classifying with regexes before reaching for a model.
- Maturity impression: a scheduled weekly benchmark that is real, sampled and expiring, beside a governance module with no callers and a tier filter that silently substitutes.
- Study when: your agents handle material with real disclosure consequences and you want a person or a supervisor in the loop at retrieval time.
- Do not copy when: you need to correct memory. There is no supersession, no tombstone and no trust state — the system can stop you seeing a memory and cannot record that one was wrong.

### `cosmonapse`

- Best idea: a memory contract with a **failure vocabulary** — refusal, overload, deadlines, rollback. It is the only interface here that lets a backend decline, and the error taxonomy is worth copying wholesale into a system with better content semantics.
- Biggest risk: the saga journal is an in-process dict, so a worker that dies mid-workflow leaves provisional writes permanent and unmarked.
- Most reusable component: journalling the inverse when a write belongs to a workflow, and putting a deadline on recall.
- Maturity impression: SDKs and tests on both the Python and TypeScript sides, no memory benchmark and no retrieval measurement — which follows from a contract that does not define retrieval quality.
- Study when: you are building multi-agent systems where storage is one participant among many and the hard problems are saturation, deadlines and partial failure.
- Do not copy when: you want a memory model. It has no opinion about what a memory is, so every question this atlas asks is answered by whatever you bind underneath it.

### `crewai`

- Best idea: scope as a hierarchical path with subscope views, proved by a committed test that a rooted view cannot recall a sibling's records — and recall that reports what it looked for and did not find.
- Biggest risk: an LLM on the write path is authorised to delete existing records, with no tombstone, no audit and no human in the loop.
- Most reusable component: the rooted-view boundary test, and `match_reasons` on a result so a rank can say why it happened.
- Maturity impression: 147 test functions across seven files, 63 of them in `test_memory_root_scope.py` alone, driving scoping through recall, listing, nesting and path normalisation.
- Study when: your problem is organisational — several agents, several teams, one store, and a need for one agent's memories not to reach another's prompt.
- Do not copy when: a wrong deletion is expensive. If you adopt it there, the first thing to build is a wrapper that logs `ConsolidationPlan` actions before they execute.

### `ecc`

- Best idea: the schema says out loud that its memory is never authoritative — `trust` is an enum of exactly one value, `unreviewed`, because verified knowledge is promoted into a governed artifact elsewhere rather than upgraded in place.
- Biggest risk: the read path filters a status the write path cannot produce, so `rejected` and `superseded` are reachable only by hand-editing frontmatter.
- Most reusable component: `sourceHarness` and `targetHarnesses` on every record, with scope enforced by path containment and every enum validated at load.
- Maturity impression: four memory-specific test files inside a large repository-wide suite, the notable one asserting the shape of the unified memory surface.
- Study when: you move between several agent harnesses and want one Markdown vault of deliberate notes all of them can read.
- Do not copy when: you expect extraction, consolidation or correction. Treat it as a shared notebook with a schema, and expect to open a text editor when something in it turns out to be wrong.

### `everos`

- Best idea: one compile path for every read, with the four scope keys in its base — so there is a single place isolation can be got wrong, and an end-to-end test with a positive control that says it is not.
- Biggest risk: supersession is excluded from reads but recorded on the row rather than the value, and the source Markdown stays watched — so a deprecated fact is re-derivable.
- Most reusable component: Markdown canonical with rebuildable indexes, plus the Cases/Skills split bridged at query time.
- Maturity impression: roughly 1,988 test functions, serious for a project this young, with the e2e layer testing owner isolation and the case-to-skill bridge rather than only the unit surface.
- Study when: you want a local-first store you can open in an editor, with a scope model good enough to build a multi-user product on.
- Do not copy when: your correction requirement is strong — making "forget this" durable means reaching into the Markdown tree, and the memory layer will not do it for you.

### `gitlord`

- Best idea: git *is* the memory. Turns are commits, sessions are branches, commit shas are addresses, and forking a conversation is a first-class operation because the substrate already supports it.
- Biggest risk: it stores what was said rather than what is believed, so a correction and the mistake sit in the log in order with nothing preferring either.
- Most reusable component: log-as-authority with the index as a projection you can rebuild, and per-branch context-cache invalidation.
- Maturity impression: 233 test functions, no memory benchmark and no retrieval measurement — consistent with a system whose claim is durability rather than recall.
- Study when: auditability and replay are the requirement — runs you must reconstruct exactly, experiments you want to fork.
- Do not copy when: belief is the requirement, or you assume git gives you deletion. Pair it with something that has an opinion about what is true, and keep the evidence here.

### `gobii`

- Best idea: an explicit persistence contract — eight built-in tables declared ephemeral and dropped before save, with each one's mortality stated in the prompt the model reads, so the agent knows what survives.
- Biggest risk: the schema is model-authored, so nobody can write a query to correct or erase a subject without first discovering what tables the agent invented.
- Most reusable component: `sqlite3.set_authorizer` as a real sandbox if you let a model write SQL, and mounting the platform's own state as tables the agent can join against.
- Maturity impression: 381 test functions across the SQLite suites alone, covering the schema prompt, digest, recovery, batch behaviour and cross-process coordination, plus an eval framework in the platform proper.
- Study when: your agent's memory is genuinely tabular — scraped listings, tracked prices, pipelines — where the useful question is an aggregate and SQL beats every retrieval mechanism here.
- Do not copy when: memory is a set of beliefs about a person that may turn out to be wrong. There is nowhere to record a rejection and no operator-level way to find a value an agent filed under a name only it chose.

### `goodai-ltm`

- Best idea: targeted update and delete on the interface itself. It is the cleanest demonstration in the atlas that a memory abstraction's first job is to give memories addresses, and the relevant part is two pages long.
- Biggest risk: no commit since 28 February 2024, no scope key of any kind, and persistence by whole-state serialisation.
- Most reusable component: `BaseTextMemory` as a diff target — set it beside ADK's `BaseMemoryService` and AutoGen's `Memory` and the missing methods are obvious in about ninety seconds.
- Maturity impression: unit tests under `goodai/ltm/mem/tests/` with no negative retrieval assertion, and the interesting evaluation story living in a separate benchmark repository.
- Study when: you are designing a provider contract and want to see what the frameworks dropped.
- Do not copy when: you intend to run it. Choose something maintained — and then check whether its interface can say "delete that one", because the odds are it cannot.

### `juggler`

- Best idea: separating the file the user writes from the file the assistant writes, with a canonical line format the writer re-tidies on every save — so the two never fight over formatting.
- Biggest risk: `forget` matches by substring, so one careless match string removes more than it names and nothing records what it removed.
- Most reusable component: a per-fact delete control in the UI, and showing every write in the transcript so the user sees the memory change as it happens.
- Maturity impression: 43 test cases against 772 lines, with separate suites for the item, the format, the seed and the **system prompt** — testing the text the model is told about a tool is rare here and exactly right for this design.
- Study when: you are building a single-developer coding assistant where memory is a handful of project conventions and the user is present to correct it.
- Do not copy when: memory must hold something you will need to prove you deleted, or something a second person should see — the store is gitignored and per-machine by design.

### `lethe`

- Best idea: purge reaches the lexical and vector substrates *by construction* — the FTS5 index is deliberately not contentless so `DELETE` reaches it — and the deletion is signed, an Ed25519 receipt over a Merkle root of the event log that a third party can verify.
- Biggest risk: a purged text can be inscribed again. The receipt records its hash for verification and no write path consults it.
- Most reusable component: retiring the id rather than only the row, and logging `before` and `after` on every mutation.
- Maturity impression: `tests/test_depth.py` plus ForgetEval — a released benchmark whose author's own system places third of three, reported with confidence intervals and an explicit refusal to declare a winner.
- Study when: deletion has to be provable — a right-to-erasure flow, a regulated store, anywhere "we removed it" must survive a challenge.
- Do not copy when: you need multi-tenancy, belief or scale. There is no scope key at all, no trust state, and the store is one SQLite file with an application-synced vector index.

### `livingfeed`

- Best idea: storing the *components* of a composite importance score rather than only the total, so the coefficients can be tuned offline by replay instead of guessed.
- Biggest risk: a recall failure is caught and returned as an empty list, so an actor with an unreachable index is simply amnesiac and nothing upstream is told.
- Most reusable component: confining forgetting to the derived layer while keeping the source, with expiry expressed as a query predicate.
- Maturity impression: 429 test functions across 40 files, and a deterministic embedder in dev and CI that makes real similarity assertions possible rather than mocked ones.
- Study when: you are building a simulation or a companion where memory should fade rather than be corrected — it is the most carefully reasoned member of the Generative Agents lineage here.
- Do not copy when: you need factual memory. There is no correction path, no trust state and no deletion by identity — and the design rationale is in Korean-language comments, so the reasons are only partly accessible to a non-Korean-reading team.

### `logseq`

- Best idea: the user defines the schema and the agent must write inside it. Properties carry a declared type and cardinality, tags are classes that extend other tags, and `listTags`/`listProperties` let a model discover the ontology before writing in it. Everywhere else the memory model is the vendor's; here it is the user's.
- Biggest risk: agent writes land live and **unmarked** — the schema defines a `created-by-ref` property the MCP write path never sets — so the store cannot answer "what did the agent change?", and the agent has no delete verb to correct itself.
- Most reusable component: the retrieval gating — exact title, FTS5 over a trigram tokenizer, a `LIKE` arm for two-character queries, fuzzy, and a local vector arm fused by reciprocal rank, with the expensive arms skipped when the cheap ones already filled the limit.
- Maturity impression: 245 test files aimed at what a knowledge base gets wrong — schema migration, malli validation of the property system, outliner tree operations, and substantial `db-sync` coverage.
- Study when: you already keep your knowledge in Logseq and want an agent to work in it, or you want the best editing surface in the atlas.
- Do not copy when: this is the agent's *own* memory. No scope key, no trust state, no authorship, no delete — and the AGPL makes embedding it in a proprietary product a licensing decision rather than a dependency choice.

### `mem0sharp`

- Best idea: an `event, old_memory, new_memory` row written on every mutation, in an append-only `_history` table with no `UPDATE` and no targeted `DELETE` against it — the audit most systems here document and do not build.
- Biggest risk: a `MemoryBehavior` enum — `Normal`, `Dreaming`, `RandomThoughts`, `PersonalMemory` — swaps the extraction and conflict-resolution prompts, and `Dreaming` asks the model for imaginative associations *phrased as possibilities rather than facts*. The behaviour reaches the extractor, the resolver and the telemetry span, and is written to neither the memory nor its metadata, so a speculative association is a row of exactly the same shape as a stated fact.
- Most reusable component: the owner column as `NOT NULL` rather than a convention, and delete-by-scope beside delete-by-id.
- Maturity impression: 2,982 lines of source against 1,123 of tests across nine classes, with Testcontainers integration suites for Postgres and Qdrant — including `PostgresHistoryIntegrationTests`, which creates a legacy history table, migrates it, and asserts the add-update-delete sequence survives. Very few audit logs in this atlas are tested at all.
- Study when: you are building .NET agents and want Mem0's shape natively rather than through a REST client.
- Do not copy when: you expect epistemics the original also lacks. It stores LLM-extracted text as fact and offers no way to mark a memory doubtful; the history table is a forensic tool, not a trust model.

### `memary`

- Best idea: separating "what I know" from "what I am attending to", with a salience model small enough to read in one sitting — the smallest legible instance of reinforcement-by-frequency in the atlas.
- Biggest risk: `_select_top_entities` sorts ascending, so the *least*-mentioned entities are the ones injected. The ranking signal has no test on its consumer.
- Most reusable component: the idea, not the code — capture without a model, and a two-store split you can reimplement in an afternoon.
- Maturity impression: the shipped package has no tests; the real ones live in a development sandbox and cover the serialization layer. Last commit October 2024, with Python pinned at ≤ 3.11.9.
- Study when: you are learning how a graph-backed agent memory fits together and want a clear, honest demonstration.
- Do not copy when: you need to answer for what the system believes. A wrong triplet cannot be removed, a wrong entity name cannot be merged, and the only quality signal counts mentions rather than accuracy.

### `memmachine`

- Best idea: provenance that actually resolves — the source is kept and cited, so a support engineer has something to look at when a user says the assistant believes something false.
- Biggest risk: deletion is acknowledged before it happens, and a duplicated method silently drops error handling on the delete path.
- Most reusable component: a one-way ingestion watermark, a constrained extractor vocabulary with a test on the constraint, and reserved metadata keys rejected by prefix.
- Maturity impression: 1,978 test functions across 112 files mirroring the source tree — among the most thoroughly tested repositories here — with migrations, four vector backends and incident-shaped HNSW tests.
- Study when: your obligation is to *explain* a memory rather than merely produce one. This is the strongest starting point in the atlas for that.
- Do not copy when: you want a library — the smallest useful deployment is a server, a database and a model provider — or your correctness bar includes "a deleted thing is provably gone".

### `memobase`

- Best idea: scope made structural. Every primary key is `(id, project_id)` and every foreign key is composite, so a cross-tenant query is a schema error rather than a review failure — the best scoping in this atlas.
- Biggest risk: the source transcript is deleted after extraction, so the evidence behind a profile line is gone and correction is a rewrite of the only copy.
- Most reusable component: the composite-key discipline, which costs a migration and removes an entire class of bug.
- Maturity impression: server tests plus client suites in Python, TypeScript and Go — real coverage, but shallow on the parts that matter, exercising API shape and filter correctness rather than extraction quality.
- Study when: you are building a personalized consumer application that wants a stable user description injected every turn at a predictable token cost, with one service and one database.
- Do not copy when: the memory must be accountable. "Why do you believe that?", "where did that come from?" and "forget that permanently" have nowhere to stand — and that follows from the decision to keep the profile small, not from an oversight.

### `memori`

- Best idea: provenance as a real join table, so a fact resolves back to the conversations that produced it — and a capture path that survives extraction failure, because the durable write is required and the smart write optional.
- Biggest risk: the dedupe key strips all non-ASCII, so facts in Chinese, Japanese, Korean, Arabic, Hebrew, Russian, Greek or Thai collide into one row.
- Most reusable component: the required-durable/optional-smart write split, and giving the agent its own memory subject rather than filing everything under the user.
- Maturity impression: 153 test files plus per-driver modules and a TypeScript suite — the largest suite of any system in its review round — with legible migrations and a Rust core behind three SDKs.
- Study when: you want a portable, auditable schema across an unusual range of databases and are happy to depend on a vendor for extraction.
- Do not copy when: your users write in non-Latin scripts. That is a statement about one function rather than the design — the fix is a few lines — but verify it against your own data before storing anything you would miss.

### `minecontext`

- Best idea: event time is separate from record time and **allowed to be in the future**, which is what makes prospective memory — a commitment you have not kept yet — expressible at all.
- Biggest risk: commitments are inferred from screen capture and nothing reviews them. There are no tests in the Python package, no scope key and no tenancy model.
- Most reusable component: keeping the raw properties as a list under the merged context, and checking historical completion before generating a new commitment.
- Maturity impression: **no tests at all** — the only files matching "test" are unrelated frontend TypeScript — no eval harness, no benchmark directory and no committed results.
- Study when: you want a passive, local, single-machine assistant that builds context from your own work, with the best ergonomics of the passive-capture systems here.
- Do not copy when: you are building a component, or you are not willing to be told what you promised by a system with no test suite and no way to correct it.

### `mirix`

- Best idea: the scope key is in the *cache* query as well as the database query, and the boundary is tested by asserting exclusion rather than inclusion — a memory written under one scope, searched under another, asserted absent.
- Biggest risk: `auto_dream` loads up to 500 items per type and lets an agent merge and rewrite them, with hard delete available — so a correction can be undone by an unsupervised pass.
- Most reusable component: a raw-context table kept beside the typed ones, and read scope separated from write scope on the client.
- Maturity impression: 33 test files with the emphasis on boundaries rather than recall — agent isolation, multi-scope access, scoped blocks, filter tags — above the atlas median for a tenancy-first design.
- Study when: you are building a hosted, multi-tenant assistant on Postgres and Redis and want the tenancy model right from the start.
- Do not copy when: memory must be repairable. No trust state, no tombstone, hard delete on the correction path, and a whole-store rewriting pass — a user's "no, that's wrong" does not outlive it.

### `mnemopi`

- Best idea: per-type forgetting curves — the most carefully modelled forgetting in the atlas — with a dry run on every destructive pass and deterministic fallbacks when no LLM is configured.
- Biggest risk: a provenance scale on which "unknown" outranks "known", an exponential decay curve applied to a commitment, and fifty tuning constants with no evaluation behind them.
- Most reusable component: making a temporal lane first-class rather than folding recency into one score.
- Maturity impression: 420 test cases across 71 files with unusually diagnostic names — `consolidate-fact-concurrency`, `recall-precision-regressions`, and an issue-numbered reproduction file. A suite that names its concurrency hazard is a suite someone has been bitten by.
- Study when: you want the best forgetting model here and can live without correction — a long-running personal assistant where the real failure is an old note crowding out a stable preference.
- Do not copy when: memory must be correctable or provable. There is no supersession at the facade, no rejection, no audit, and the trust model grades where a memory came from rather than whether it holds.

### `neko`

- Best idea: a *dispute* signal structurally separate from reinforcement, with a hard filter that drops disputed entries **before** the LLM rerank — the docstring giving the reason: stage two would either reinforce the dispute or, worse, cancel it.
- Biggest risk: status is derived from a score rather than stored, so no transitions are kept; and ban-topic directives expire after three days, which is a TTL on a suppression the user asked for.
- Most reusable component: the durable do-not-mention list keyed on the term, and stating the false-positive policy in the code where the suppression lives.
- Maturity impression: about 7,936 test functions repository-wide — the largest suite in this atlas — with a memory recall test that walks the pipeline phase by phase and several policy-contract files.
- Study when: a memory mistake will be *felt* rather than merely wrong — a companion, a therapy-adjacent tool, a long-running personal assistant.
- Do not copy when: you want a library. Memory is wired into a companion runtime with voice, vision and an avatar, and there is no API boundary to lift it out through. Take the designs, not the code.

### `npcpy`

- Best idea: approval is a state the *retriever* respects rather than a workflow step — an unreviewed extraction cannot reach a prompt, because the retrieval path reads approved memories only.
- Biggest risk: a rejection is a status on a row. Re-extracting the same content produces a fresh candidate with nothing consulting the earlier no.
- Most reusable component: offering **edit** and **defer** alongside approve and reject, and keeping the pre-edit text.
- Maturity impression: one memory-processor test file, no benchmark, and nothing asserting that an unapproved memory stays out of `build_context` — the single behavioural claim the whole design rests on.
- Study when: your memory is small, your user is present, and wrong facts are expensive — ten approved memories beating a thousand extracted ones.
- Do not copy when: memory must accumulate unattended, or the same facts recur often enough that answering the same question repeatedly becomes the product.

### `openhuman`

- Best idea: memories are labelled by **what they may cause**, not only by how sure the system is. A taint lattice governs consequence, and sanitization deliberately cannot launder provenance — a redacted memory keeps its taint.
- Biggest risk: taint is binary, assigned once and never re-evaluated; much of the core is re-exported from a separate crate that cannot be read here; and nothing records a rejected value.
- Most reusable component: failing closed on unknown enum values from the database, and two-tier extraction with a free first tier.
- Maturity impression: about 12,548 test functions repository-wide and 1,278 inside the memory modules — the most heavily tested system in this atlas by count, pinning the fail-closed taint parser and wire-format round-trips rather than padding.
- Study when: you are building a desktop agent that ingests a user's real data and therefore has a genuine injection problem rather than a theoretical one.
- Do not copy when: your requirement is corrective memory, or you want a library — twelve modules, an unreadable companion crate, a Tauri shell and GPL-3.0 make this a codebase you join rather than a dependency you add.

### `pydantic-ai-harness`

- Best idea: an idempotency id derived from the run and the tool call, so a retried write is a replay rather than a second append — one of three answers to concurrent writes in the whole corpus.
- Biggest risk: the delete is content-free by design, and the only table recording mutations has its payload cleared — so the audit cannot answer what was removed.
- Most reusable component: budgeting the injection and degrading to a pointer, and returning `scanned` and `truncated` from search so a caller knows the answer was partial.
- Maturity impression: 2,498 lines of tests against 2,452 of implementation — the highest ratio in this atlas at this size — and the content is better than the ratio, because the suite asserts what must **not** happen.
- Study when: you are on Pydantic AI, your memory is notebook-shaped, and multi-tenant safety matters more than recall quality.
- Do not copy when: memory must hold *claims* you will later mark uncertain, correct with provenance, or prove you deleted. There is no unit below the file to attach that to.

### `reme`

- Best idea: correction gets a validated verb set — `CREATE | CORROBORATE | REFINE | CORRECT` — with contradictions written *into* the memory pointing at their cause, rather than resolved silently.
- Biggest risk: the vocabulary is enforced as a returned label, not as a constraint on the edit, so a validated verb can accompany an unvalidated action.
- Most reusable component: publishing the category you are worst at. ReMe commits per-category LongMemEval and BEAM tables including its own lowest score, which almost nothing else here does.
- Maturity impression: integration suites running the pipelines end to end against a workspace fixture, and committed results rather than a harness with no numbers.
- Study when: you want a personal knowledge base an agent maintains and a person can open in an editor, and you want to see what an honest benchmark report looks like.
- Do not copy when: you need a multi-user service — the scope key, the read-path filter and the per-tenant index are all yours to add — or you are unwilling to have your correctness rules live in prompts.

### `risuai`

- Best idea: every derived summary carries the ids of the messages it came from, so deleting a source drops the summaries built on it — the cheapest correct answer to a problem most summarizers never notice.
- Biggest risk: three generations of summarizer ship side by side behind a flag and none of them has a test.
- Most reusable component: reserving retrieval budget in *bands* rather than ranking one list, including a band for a random draw so the unreachable middle stays reachable.
- Maturity impression: roughly thirty test files covering the parser, the scripting language, storage, paging and the source map — a team that writes tests, aimed everywhere except the summarizers.
- Study when: you are building for one person's long-running conversations on their own machine, or you want to watch a data model grow a field per problem across three generations.
- Do not copy when: you need multiple principals, an audit trail, or a memory an agent can query. There is no scope key, no history and no API.

### `second-me`

- Best idea: L1 is a *numbered generation* over retained L0, so the derived layer is rebuildable and two generations can be compared instead of the latest being trusted.
- Biggest risk: forgetting stops at the vector store. The trained model keeps what a deleted document taught it, and the deletion cascade that would catch the rest has no test.
- Most reusable component: versioning the derived layer, and deleting the embeddings in a numbered sequence rather than hoping a cascade covers them.
- Maturity impression: no tests over its own pipeline, no scope model, no correction path at L2, and a September 2025 commit at the analyzed revision.
- Study when: you want to experiment with parametric personal memory and have a machine that can train — as a demonstration that the whole pipeline runs on a laptop it is convincing.
- Do not copy when: you cannot tell your users that deleting a memory removes it from search and not from the model. If that sentence is unacceptable for your product, the architecture is wrong for you.

### `sillytavern`

- Best idea: the activation vocabulary — sticky, cooldown, delay, negative keys, bounded recursion — which are answers to problems extraction-based systems also have and mostly express as tuning constants, if at all.
- Biggest risk: an intricate activation pipeline with no activation tests. Nothing asserts that a given chat and lorebook produce a given activation set.
- Most reusable component: the interchange format, which lets a curated memory outlive the tool that authored it.
- Maturity impression: a mature, long-lived client with a real editing surface — and the one subsystem this atlas came for is the one without a fixture.
- Study when: your memory is small, curated, and matters more than it scales — a character, a world, a domain glossary, a set of standing instructions.
- Do not copy when: memory must *learn*. Its own users demonstrate the gap: the summarize extension exists because a hand-authored lorebook cannot remember what happened.

### `simplemem`

- Best idea: coreference resolved and time absolutised **at write**, so a stored unit reads "Alice discussed the marketing strategy with Bob at Starbucks on November 15, 2025" rather than "she told him about it there". Almost everything else here stores the second kind and hopes retrieval supplies the context.
- Biggest risk: six headline benchmark figures with no committed result artifact for any of them — and the pillar the papers are about cannot delete, scope or correct a single memory.
- Most reusable component: the restatement transform, which is a prompt and a schema and will improve any retrieval you already have; plus one `_log_event` helper called at every mutation site.
- Maturity impression: 311 test functions across roughly twenty files for 114,000 lines and three products, with the governed pillar (EvolveMem) also the newest, least documented and least tested.
- Study when: you want one very good write-time idea to take into your own extractor.
- Do not copy when: you would deploy the text pillar behind a user-facing agent. The first support request you cannot answer is "remove what it learned about me".

### `skales`

- Best idea: zero-LLM capture and retrieval that are both cheap and legible — regex capture on a 90-minute watermarked scan, retrieval scored `0.70 / 0.20 / 0.10` under a stated sub-100ms budget, with provenance on every extracted row.
- Biggest risk: the documented deletion path for a fact is a chat phrase nothing implements — and that phrase is bound to *capture* and *retrieval* instead, so asking it to forget can store a new memory.
- Most reusable component: stating the retrieval budget in the file header, and invalidating the read cache inside the delete action rather than beside it.
- Maturity impression: no tests of any kind, for a regex pipeline that is a pure function over strings — the cheapest gap in the atlas to close.
- Study when: you want a local assistant that quietly remembers preferences without shipping conversations to a vendor.
- Do not copy when: you need a system of record, or you intend to reuse the implementation — the **BSL 1.1** licence makes this source-available rather than open source.

### `soul-of-waifu`

- Best idea: a length floor on any LLM-generated overwrite, so a short or empty rewrite is rejected rather than stored — the clearest small example here of how to make a full-rewrite memory safe.
- Biggest risk: the backup, restore and inspection API has no caller anywhere in the application, and only one of the two files written by the same call is backed up.
- Most reusable component: having the model fill a schema and letting your code render the document, plus giving append-only and rewritable memory different files.
- Maturity impression: no test suite exists — no `tests/` directory, no `test_*.py`, nothing.
- Study when: you want to see the guards that make a rewrite-the-whole-document memory survivable.
- Do not copy when: users will ask "what did I tell you about X". There is no retrieval over history, no provenance and no deletion, and the index forgets by omission.

### `tigrimosr`

- Best idea: the skill synthesizer stages a proposed skill as `SKILL.md.proposed` beside the live file, keeps the rationale and the sessions it came from, waits for a person, and promotes by rename — forcing review when the target was authored by a human rather than by the automation.
- Biggest risk: approval is durable and rejection is ephemeral, with review state held in process memory — so a user who says "no, don't remember that" is answered and then forgotten.
- Most reusable component: propose-stage-approve by rename, which is worth copying into systems whose memory model is far richer than this one's.
- Maturity impression: 62 inline Rust tests concentrated on the agent loop and tool config rather than memory, with nothing exercising the propose/approve/reject cycle, and nothing at all on the new CLI or its path resolvers.
- Study when: you want a self-contained agent platform that asks before changing what it has learned, or you want the promotion mechanism on its own.
- Do not copy when: memory must be correctable. It is one blob per project plus a skill library, thin by design, and read-modify-write over whole JSON files is the persistence model.

### `tokenmizer`

- Best idea: a status for *unresolved ambiguity* that keeps both candidate decisions visible instead of guessing between them — the atlas's only state that means "I do not know which of these is in force".
- Biggest risk: the redaction functions are unit-tested in isolation and nothing asserts a secret fails to reach the rendered context block.
- Most reusable component: the status model and its transition table, worth copying even if you never run the tool; and storing the *argument* for a correction rather than only the fact of it.
- Maturity impression: 440 cases in 38 files with the most informative names in the corpus — `memory_accuracy/test_retention`, `chaos/test_recovery`, `test_contested_decisions`, `test_decay_idempotence` — and a committed ground-truth measurement of extraction recall.
- Study when: your memory is a coding session and your hardest problem is knowing which of two plausible decisions still holds.
- Do not copy when: you need multi-tenant or long-horizon personal memory. Scope is a cache key, every clock is a record clock, and the graph is built around one project's session history.

### `virtualwife`

- Best idea: the storage contract. `BaseStorage` puts `owner` on every method including a scoped clear, and is a good small answer to "what must a memory backend do".
- Biggest risk: `normalize_scores` sums three quantities on different scales without normalising any of them, so the Generative Agents retrieval function does not do what its name says.
- Most reusable component: the contract, with the implementations discarded — and decay by wall-clock hours rather than by turns.
- Maturity impression: one test file, covering a livestream API. **Nothing tests memory**, and the tests that would have caught what this report found are unusually direct.
- Study when: you want a minimal backend contract to copy, or a worked example of a scoring bug that a single assertion would have caught.
- Do not copy when: you want the system. It is dormant, needs Milvus for the interesting half, disables that half by default, and is a last-N-messages window without it.

### `z-waif`

- Best idea: capping how much the character's own output contributes to its own retrieval query — a feedback loop most companion systems have and none of the others here noticed.
- Biggest risk: a three-message window score is computed and never used, an initial best-score of zero sits over a scorer that returns negatives, and the retrieval cannot return nothing.
- Most reusable component: the scoring function — forty lines containing three of BM25's five ideas plus two the literature does not emphasise, rewritable over a proper store in an afternoon.
- Maturity impression: no tests of any kind, for a system whose entire behaviour is arithmetic over lists — the most avoidable gap in this atlas, since every property is a pure function of data.
- Study when: you want a long-running local companion on a machine with no GPU budget, and the best worked example here of how far plain arithmetic gets you.
- Do not copy when: you would take the code. The licence is source-available with a discretionary field-of-use clause and a royalty, and the data model cannot maintain its own invariants.

### `zerostack`

- Best idea: atomic write-then-rename with the reason in the comment, and a `.bak` whose extension deliberately keeps it out of the `.md` listing and out of search — a backup that cannot become a search result.
- Biggest risk: a destructive default on a missing argument, and a one-deep undo presented as safety.
- Most reusable component: the global-versus-project split and the atomic-write-plus-backup pair, liftable wholesale into any notebook system in any language.
- Maturity impression: 65 test functions in 1,203 lines — a ratio just under one to one — with a separate permission-path suite including `check_perm_skipped_when_permission_is_none`, which asserts the gate is a gate.
- Study when: you want a Markdown memory in a Rust agent and care more about not corrupting a file than about recalling the right line.
- Do not copy when: memory has to hold claims. There is nothing to mark uncertain, nothing to supersede, and no record that anything changed beyond one overwritable `.bak`.

### `agentswarms`

- Best idea: the retrieval index is derived in the database by a trigger over the item's own content, so an application cannot insert a row that is unfindable or forget to update the index — and no model call sits between writing a fact and being able to recall it.
- Biggest risk: three columns that look like a lifecycle and are inert. `score` is read by the ranker and the prune ordering and never written; `usage_count` is displayed in the settings UI and never incremented; `expires_at` is never set or swept. The UI tells the user low-score items are pruned first, and no item ever has a low score.
- Most reusable component: `prune_agent_memory_items` — a `SECURITY DEFINER` function that compares its caller-supplied user id against `auth.uid()` before deleting anything, then has execute revoked from every client role. It is the same construct LoreKit leaves unchecked.
- Maturity impression: RLS on all three tables, a retention pass that deletes generated documents before the rows referencing them, and **no tests anywhere in the repository** — for a subsystem that is almost entirely pure functions over strings.
- Study when: you want the smallest complete long-term memory here that is not a file, or a worked example of lexical recall with no embedding and nothing to tune wrong.
- Do not copy when: you need memory to hold claims — there is no status, no provenance that is read, and no dedup, so a fact mentioned ten times becomes ten rows competing for the same twelve slots. And the Elastic License 2.0 forbids offering it as a hosted service.

### `empryo`

- Best idea: git **co-change affinity** as a recall signal — a memory attached to files that historically change together with what you are editing surfaces without matching a query token, entered into the fusion at RRF rank 5 so it stays behind a direct hit.
- Biggest risk: soft delete is not rejection. `content_hash` is unique and the upsert treats a collision as an update that clears `hidden`, so re-saving the same sentence resurrects a memory the user deleted — with a test named for it.
- Most reusable component: `hashbag-v2`, a dependency-free 384-dimension embedder whose measured cosine ranges are documented and whose ranking curve is calibrated against them.
- Maturity impression: 3,271 test cases across 100 files with eight memory-specific suites, a browser with a bulk cleanup queue, and supersession correctly filtered on the read path.
- Study when: your memory is about a codebase and you want relevance signals the repository already contains.
- Do not copy when: a correction has to stick, or you need tenancy — scope is global-or-project on a local SQLite file, and the BSL restricts production use until the change date.
- Reported but not reviewed: the maintainer has extracted the memory layer into a private `packages/memory/` workspace and reports the content-hash resurrection closed there, plus a committed retrieval benchmark with a CI floor gate ([PR #2](https://github.com/neoneye/agent-memory-atlas/pull/2)). The public repository is unchanged at `e6b5885d` and does not contain that tree, so the verdict below still describes what is readable. The maintainer also reports a real-corpus arm of that benchmark scoring hit@3 0.082 against 0.857 on the synthetic fixture, unexplained, with a working hypothesis that real memories attach many more file paths than the fixture does and that stale ones dilute file affinity — the gap between a synthetic memory fixture and a live store is under-reported across this atlas, and this is the only place in it that anyone has published both numbers.
- Renamed: this was published as `soulforge` and the project is now **Empryo** (`proxysoul/Empryo`). The refacing commit predates the analysis — the atlas took the name from the repository URL rather than from the README, which already said so. The pinned commit and every finding are unchanged, and `/systems/soulforge/` redirects.

### `dexto`

- Best idea: a five-method memory contract that includes `update(id)` and `delete(id)` — the two that AutoGen and ADK both omit, and that no better implementation can add afterwards.
- Biggest risk: there is no retrieval at all, and the contributor's `limit` is unset by default, so the shipped behaviour renders the entire store into every system prompt.
- Most reusable component: the contract itself, plus typed errors with a code per failure and a test for each.
- Maturity impression: 25 test cases against 605 lines aimed at the error paths, Zod bounds on every field, and a docstring that names the missing scope model as future work rather than implying it exists.
- Study when: you are designing a provider interface, or your memory is a short curated list a person pins.
- Do not copy when: the store is meant to accumulate — nothing ranks, nothing caps by default, and relevance is entirely manual.

### `project-golem`

- Best idea: `ExperienceMemory` — thirty-three lines that record which proposal types the owner declined and read them back into the agent's context before the next proposal. The rejection is written where the rejection already happens, needs no model, and is the one signal extraction can never produce.
- Biggest risk: the avoid list holds three entries, is keyed on the proposal type rather than the value, and `recordSuccess()` clears it entirely — so one accepted suggestion erases every rejection before it.
- Most reusable component: the outcome-gated write on the decline path, and the content-derived stable id that makes re-memorising idempotent.
- Maturity impression: a competent LanceDB driver that resolves every recall hit against the canonical list so a stale index cannot produce a wrong answer — beside 74 test files, none of which covers the rejection loop.
- Study when: you are building anything that proposes work to a person and want the smallest complete answer to "they said no, now what".
- Do not copy when: you need it commercially. The licence forbids it outright, and the memory is wired into a desktop app with no seam to lift it through.

### `openyak`

- Best idea: the update queue is debounced by **workspace path rather than session id**, with a docstring saying why — two sessions in one directory collapse into a single refresh instead of racing to overwrite each other's document.
- Biggest risk: every write is a full overwrite of the only copy, and the guards are a ceiling with no floor. An empty rewrite is refused; a three-line rewrite replacing two hundred lines is written silently, and the 200-line cap truncates the tail with no marker.
- Most reusable component: the three write guards and the instruct-then-verify pattern — a prompt that bans Markdown in eight clauses and a parser that strips code fences anyway.
- Maturity impression: 90,000 lines of backend Python with 114 test files, exactly one of which touches memory — asserting where the section lands in the prompt, not what the update path does. Apache-2.0.
- Study when: you want a per-project brief that keeps itself roughly current with no retrieval to tune, or a worked example of handling concurrency in whole-document memory.
- Do not copy when: memory must hold facts rather than context. There is no unit below the document, so there is nothing to supersede, attribute or reject.

### `memento`

- Best idea: a memory sealed until a date. `status = 'sealed'` with a `deliver_on` column puts an entry outside transcription, indexing and the timeline entirely, and a worker pass moves it into the normal pipeline when the date arrives — enforcement by state rather than by a predicate every query must remember.
- Biggest risk: `source_entry_id` is `ON DELETE SET NULL`, so deleting a recording leaves every fact derived from it in place with its provenance silently erased — indistinguishable from a fact that never had a source.
- Most reusable component: partial indexes that encode liveness — every live index declared `WHERE deleted_at IS NULL`, so the fast path and the correct path are the same object.
- Maturity impression: a 208-line schema with status vocabularies, soft delete everywhere and a worker that deletes a daily summary when its source entries are gone — beside no test suite at all.
- Study when: you need memory that becomes available rather than memory that fades, or you want the cleanest small example of provenance from a derived fact to its evidence.
- Do not copy when: you need it commercially — PolyForm Noncommercial forbids it — or you need a correction to survive, since a deleted profile fact can be re-derived by the next reflection pass.

### `universal-memory-engine`

- Best idea: rejecting a candidate with `suppress_similar` writes a row to `memory_suppressions` keyed on the canonical label, and the write gate checks it at four points — a hit is rejected as `suppressed_blocked` and never written. The cleanup pass writes one too, so a deletion binds the future rather than waiting to be re-derived.
- Biggest risk: `events.happened_at` sits beside `created_at` and the automatic gate stamps it with `now`, so the column that would carry validity time is collapsed by the writer that produces most memories — while the read path already sorts by it.
- Most reusable component: the split between `reject` and `reject with suppress_similar`. One boolean separates "this guess was wrong" from "stop proposing this", and only the second binds anything.
- Maturity impression: eleven dated migrations, receipts with a `meaningful_no_write` outcome that distinguishes a quiet system from a broken one, and a 32-query golden retrieval set with per-query forbidden ids — beside no test on the suppression gate itself.
- Study when: you want the fourth working tombstone in this atlas, or an eval fixture built around identity confusion rather than recall.
- Do not copy when: you cannot live on Cloudflare — D1, Durable Objects and Workers are the substrate, so porting means keeping the shapes and rewriting everything beneath them.

### `membase`

- Best idea: `_coerce_owner` forces the `owner` field on every hub upload to the address recovered from the caller's signing key, and warns loudly when it had to override — ownership is possession of a key rather than a string in a payload.
- Biggest risk: `ChromaKnowledgeBase.retrieve` reads Chroma's `distances` array into a variable named `similarity`, so raising the threshold to demand better matches keeps the farthest documents and drops the nearest; any non-zero threshold also swaps vector search for a literal `$contains` filter on the whole query.
- Most reusable component: `src/membase/storage/_auth.py` — eighty lines of secp256k1 signed headers that transfer to any project already holding a wallet key.
- Maturity impression: no CI, the only test of the summarisation path has no assertions, and nothing in `src/membase/memory/` has changed since 24 July 2025 while HEAD is 10 June 2026.
- Study when: you want to see a distance and a similarity read from the same field a hundred lines apart, and a test suite that passes over both.
- Do not copy when: you need deletion to mean anything — `delete` removes the SQLite row and never calls the Chroma delete that retrieval reads, and one deletion also stalls long-term consolidation permanently by leaving a sixteen-message block short.


### `palazzo`

- Best idea: the write-ahead log is a *precondition* for a destructive operation, not a record of it. `log_strict` fails the delete when the audit entry cannot be durably appended, on the stated reasoning that the WAL is the only trail — and the entry carries a text preview, so it says what was removed.
- Biggest risk: the README's stated differentiator over the generic Qdrant server is an "enum-validated palace schema", and `src/schema.rs` says the four tags are "deliberately free-text… never enforced". `validate_tag` trims and length-caps; there is no enum in the crate.
- Most reusable component: `src/wal.rs` — 129 lines including its tests, no dependency on the rest of the crate, and the split between best-effort logging for writes and strict logging for destruction.
- Maturity impression: 63 inline Rust tests, CI running clippy at deny-warnings across two feature sets plus `cargo audit`, and a committed benchmark note reporting its own loss with Wilson intervals and a stopping rule.
- Study when: you want the audit-as-precondition variant, or an example of a duplicate probe that deliberately refuses to match superseded points — the collision [Empryo](../systems/empryo/) resolves the other way.
- Do not copy when: recall is the requirement (its own pilot puts R@5 at 36% against the 96.6% it cites as the bar, diagnosed as ranking rather than coverage), or more than one person shares the store — there is no tenancy, no verified identity and no default scope.


### `aura`

- Best idea: the receipt store keeps a SHA-256 hash chain beside it — `seq`, `content_hash`, `prev_hash`, `entry_hash` — so deletion shows up as a sequence gap and insertion as a broken link, and verification re-hashes the on-disk bodies. Every other append-only audit here would read clean after being rewritten. I ran `tests/test_audit_chain.py`: 16 passed, including the modified-body, broken-link and deleted-entry cases.
- Biggest risk: the belief machine that would use all this is a plain dictionary. `active | trusted | contested`, a resolution API, and a rule that a trusted belief cannot be contradicted — none of it saved or loaded, so every trust state resets on restart. A second belief store in the same codebase does persist and has no status field, and the `contested` flag stamped on every memory record is read by nothing.
- Most reusable component: `core/runtime/audit_chain.py`, and the write gateway's two fail-closed branches — no authority wired, and the authority call raising.
- Maturity impression: 21,206 test functions across 1,740 files, a claims matrix pairing each claim with a reproduce command and a falsifier, and a `CLAIMS_NOT_SUPPORTED.md` that puts recursive self-improvement in the unsupported column while reporting its own capability curve going down, 0.667 to 0.625.
- Study when: you want tamper-evidence rather than append-only, or an admission-control layer that clusters near-duplicates before counting corroboration and refuses both sides when no rule separates them.
- Do not copy when: literally — the licence is all rights reserved, read-and-learn only, no derivative works. Also when you need forgetting with a reason: retention is RAM-scaled keep-counts, so memories leave because the machine is small, never because they turned out to be wrong.


### `memex-zero-rag`

- Best idea: the directory contract — `raw/` immutable and read-only to the model, `wiki/` entirely derived, `L1/` private, git as the whole history. Every derived page can be rebuilt and no model error can destroy the inputs, stated in one line of `SCHEMA.md`.
- Biggest risk: `L1/credentials.md` is tracked in git despite `L1/` being in `.gitignore` and the file itself warning *"This file is git-ignored. NEVER commit credentials."* `.gitignore` does not untrack what is already tracked, so a user who fills it in and pushes their fork commits their API keys.
- Most reusable component: `SCHEMA.md`, which is a better specification than several machine-readable ones here — if the model does the structuring, the document telling it how is the real schema.
- Maturity impression: no tests and no CI for 3,300 lines; an MIT badge, no `LICENSE` file, and `All rights reserved` on all eight source files; and `KNOWLEDGE-DECAY.md` reads as the trust model while being a draft whose fields appear nowhere in code.
- Study when: you want the Karpathy wiki pattern packaged, or a clean case study in what it costs to express every invariant as an instruction rather than a check.
- Do not copy when: a rule has to hold on the turn the model is confidently wrong. The citation "enforcement" is a manual substring report with an unimplemented fix mode, the *"It STOPS and asks you to decide"* contradiction gate is touched by none of the nine tools, and search is an unranked substring scan that gets worse as the wiki gets richer.


### `agentrecall-x`

- Best idea: `isNoiseCandidate` — a p0 correction surfaced at least three times and honoured less than 30% of the time is excluded from its own veto. The only mechanism in this atlas where a record's authority is *withdrawn* by measured evidence rather than merely granted by provenance.
- Biggest risk: `precision` is `heeded / retrieved`, and heeded is judged by the loop observing whether the agent honoured the rule — the same system whose compliance is being scored. The property that makes the demotion trustworthy is measured by the thing it constrains, and the committed benchmark that would check it is twelve cases.
- Most reusable component: the `CorrectionRecord` field design — three separate endings (`retracted_at` with a reason, `superseded_by`, `merged_from`) that all keep the record on disk, plus the outcome counters underneath the demotion rule.
- Maturity impression: 124 test files with ten named for the corrections mechanism itself, a committed four-axis replay result that publishes 33% precision against itself, and comments that cite dated decisions and explain why a field is deliberately not defaulted.
- Study when: you have guardrails that fire and no way to retire the ones nobody obeys, or you want the cleanest separation in this atlas between who writes a rule and who must obey it — the model's thirteen tools include no way to author or retract a correction.
- Do not copy when: you need the trust machinery shared across a team (the Supabase schema has no corrections table), or content-level correction — the mechanism guards behaviour, and `UNIQUE(project, store, slug)` is dedup, not a tombstone.


### `memledger`

- Best idea: `memory.policy.yaml` is canonicalised (RFC 8785) and hashed, and the hash is recorded in every event it influenced — so a decision points at the policy version that actually produced it, and editing the policy never rewrites history. Nothing else here can say which version of its own rules made a call.
- Biggest risk: the dedup lookup is `WHERE subject = ? AND relation = ? AND value_json = ? AND status != 'deleted'`, so a fact the user deleted is not found and a fresh active record is created. The deletion is durable, keyed on the value, and terminal in the state machine; the one query that could enforce it skips it.
- Most reusable component: the event envelope and its validator — actor, cause, `policy_hash`, `sources` required for derived events, and an `LLMCall` block required if and only if the actor is a model.
- Maturity impression: sixteen commits over a week, 37 tests, a LoCoMo runner and a regression case file — and no committed result artifact, so the runners are process rather than evidence.
- Study when: you cannot answer "why does my agent believe this", or you want a five-status memory state machine with its legal transitions written down as a checked set and two terminal states.
- Do not copy when: you need the correction to stick. The states are right and nothing consults them on write, which is the whole gap in one sentence.


### `terse-memory`

- Best idea: `# Hot buttons ## Don't` — a user-extendable prohibition tier that is always loaded rather than retrieved, with a lint rule (`MEM-G`) warning past twenty objects so it stays affordable. A rule that must never be missed should not depend on a query returning it.
- Biggest risk: the package has no capture, recall, forget or consolidate function — those are the model's job via a skill — and of the seven lint rules, the three deferred to v0.2 are exactly the epistemic ones: `MEM-C stale`, `MEM-D consolidation-due`, `MEM-E duplicate`. What ships polices hygiene; what is scheduled polices truth.
- Most reusable component: the schema decisions — `as-of` required on nearly every kind, and a `session:` attribute paid for at write time so "forget this conversation" resolves to a query instead of a guess.
- Maturity impression: three commits, HEAD 24 July 2026, spec marked pre-release — and 89 tests that I ran and that pass, covering the linter, the scaffolder and the wiring.
- Study when: you want a typed, diffable single-file store with a structural query syntax, or the always-loaded prohibition tier on its own.
- Do not copy when: you need the operations implemented. Explicit forget deletes and records nothing, `stale` is a status nothing sets, and the stated rule that auto-capture from untrusted content is "a protocol violation, full stop" has no detector.


### `agentic-context-engine`

- Best idea: a `SimilarityDecision` records the pairs the consolidator decided to KEEP separate — the pair, the reasoning, and the similarity at the time — serialised with the skillbook and checked in the detector's inner loop (`detector.py:234`) before the pair is proposed again. The only durable record of a decision *not* to act in this atlas, and the only one that is consulted.
- Biggest risk: everything above the storage layer is a model following a prompt, and `similarity_at_decision` — the field that would let a settled pair be re-opened when it drifts closer — is stored and never compared against anything.
- Most reusable component: the KEEP record itself, under thirty lines including the dataclass, two accessors and one `continue`. It generalises past memory to any pipeline that re-proposes the same merge or match on every pass.
- Maturity impression: 788 commits since November 2025, 31 test files, a benchmark package with task loaders and four live scripts including a τ-bench retail one — and no committed result, so the claim the project leads with is the one it has built the apparatus to check and not published.
- Study when: you repeatedly ask a model the same pairwise question, or you want the counter-usage rule — `harmful_count` is explicitly forbidden from being a hard removal trigger because usage and harm correlate.
- Do not copy when: you need the skillbook's quality to be measurable. The counters gate nothing by design, and removal quality rests entirely on a reflection nothing checks.


### `deer-flow`

- Best idea: a three-tier plugin contract that replaced `hasattr` probing with defaulted hooks on the base class, plus a `noop/` backend shipped as the copyable template and a stated portability rule — a backend talks to the host through exactly two channels and may make exactly one host import.
- Biggest risk: every backend must return the default backend's response shape, and the README names the failure itself — pydantic ignores unknown fields, so a Mem0 or OpenViking adapter silently drops whatever those systems model beyond `facts[]` and a timestamp, and the symptom appears three layers away as a frontend crash on an empty date.
- Most reusable component: `backends/README.md` as a design document. The tiering, the compiled template and the two-channel rule are independent of anything DeerFlow does.
- Maturity impression: 200 commits in twelve days, four working backends, a `test_memory_prompt_injection.py` almost nothing else here has — and no committed comparison across the three real backends the harness makes swappable by one config line.
- Study when: you are designing a host contract for pluggable memory, or you want the rare case of a scope key that crosses a plugin boundary with the widening path gated on an authenticated token.
- Do not copy when: your backend models epistemics. No status, confidence, provenance or supersession field crosses this contract at any tier, so a system that grades its memories is flattened on the way to the interface.


### `ean-agentos`

- Best idea: deterministic capture. Commits via a git post-commit hook, bash commands with exit codes and durations, tool calls and file versions all arrive because a hook fired rather than because a model judged the moment important — and `errors_solutions` models the attempt, with `solution_worked` and an `attempts` counter, not just the conclusion.
- Biggest risk: both recall paths are `ORDER BY solution_worked DESC` rather than a `WHERE`, so a fix that did not work is returned one row lower in the same shape as one that did. For a project whose pitch is stopping repeated bug fixes, the guard against repeating a known-bad fix is the model reading a boolean in the result row.
- Most reusable component: the `errors_solutions` schema, and the hook installer's mark-and-restore discipline — it backs up another program's settings, marks its own entries, and removes exactly those on uninstall.
- Maturity impression: 51 commits between 16 and 19 March 2026 and nothing since; 59 tests named by build phase rather than by behaviour, and none named for the error-recall path the product is built around.
- Study when: you want capture that does not depend on an extraction pass noticing, or a schema that records what was tried and failed rather than only what worked.
- Do not copy when: you need the failure withheld rather than demoted, or you are storing shell output — `bash_history` keeps `command`, `output` and `error_output` verbatim with no secret scanning found.


### `m-flow`

- Best idea: three separate modules front an expensive model call with a zero-cost deterministic one and say so in the docstring — the procedural trigger ("Layer 1: Rule trigger (zero cost). Layer 2: LLM light classification"), the conflict detector ("Deterministic first, LLM fallback"), and a worth-storing screen that runs before a procedure is built and indexed rather than pruning afterwards. The trigger also separates *should we retrieve* from *should we inject*, which almost nothing else here does.
- Biggest risk: the claim that distinguishes it — anchor on the most precise node, then path-cost propagation, beating layer-selection retrieval — is a retrieval-quality claim, and no committed benchmark result exists. The per-edge costs that make paths compete are the ranking signal and are uncalibrated against anything in the repository.
- Most reusable component: the procedural governance chain — worth-storing, classifier, deterministic-then-LLM conflict detection, a generated version diff, and `reconcile_active` deciding which version is live.
- Maturity impression: 149,000 lines across four deployable packages with Alembic migrations, Docker and a starter kit — and integration tests that need a graph database and a worker queue, so nothing here was run.
- Study when: you are building tiered gates around model calls, or you want a third point on the spreading-activation axis beside NOOA Memory's ACT-R decay and HippoRAG's PageRank.
- Do not copy when: "one strong path is enough" would be applied to belief rather than recall — a single low-cost chain is a good reason to look somewhere and a weak reason to believe something, and the graph does not distinguish.

### `nova-ai`

- Best idea: a relation is stored only after the user answers a spoken question — "may I remember that X is a kind of Y?" — with sense disambiguation asked first, so the only path from parsed language to a stored belief runs through a person, in the turn where they still have the context to answer.
- Biggest risk: knowledge is strictly monotonic. Nothing anywhere removes a relation, a sense or a concept, and `find_contradictions` — which would notice the consequence — is called by nothing, so a wrong `is_a` is walked by every chained query forever and explained confidently each time.
- Most reusable component: the correction quarantine — confirmed corrections live in their own file, are merged with the curated training set only in a local copy for the duration of a retrain, and are restored under `try/finally`, so the human-owned ground truth cannot be polluted by the machine's own learning.
- Maturity impression: 25,000 lines of one author's carefully documented Python with an unusually detailed changelog, and 21 test files holding five assertions between them — the verification is a person's practice rather than the repository's, and it does not survive the person.
- Study when: you want to see what correction machinery looks like when there is no model to blame; every epistemic decision here had to be written down because nothing could be delegated to a language model.
- Do not copy when: literally — the licence is "Viewable, Not Reusable". Also when you need more than one user, since no scope key exists anywhere, or a store that survives an interrupted write, since the whole graph is rewritten non-atomically on every save.

### `memsem`

- Best idea: the benchmark is committed, wired into `npm test`, and reproduces exactly — P@3 0.958 with an ablation across four alternative constant weightings, so the defaults have to keep beating the alternatives on every run, and an author-written honest reading names the set's limits.
- Biggest risk: the durable rejection is real and only a human can arm it. A rejected candidate writes a value-keyed suppression that refuses every later write; automatic supersession writes none, so a re-asserted value returns and fades the live correction — three repetitions archive an ordinary one, and six take a pinned one off the top of a search while leaving its confidence untouched.
- Most reusable component: the audit row — entity, field, old and new value, a reason, a pass id that caps a sub-agent's cumulative adjustment, and a dry-run flag that records what would have happened without applying it.
- Maturity impression: twenty-one commits and sixteen READMEs, and the engineering habits underneath are better than that ratio predicts — bounded sub-agent authority enforced in code and tested, an adverse-case governance suite that exits non-zero, five committed negative retrieval cases, and a purge that cascades rather than a flag rename.
- Study when: you are deciding what a defensible retrieval number looks like; this is the corpus's cleanest example of a claim a reader can check in one command.
- Do not copy when: a correction has to hold without anyone having pinned it. The rejected value is keyed and consulted, so re-entry costs it a `resurrectConfidence` discount — but a discount is a price, not a prohibition, and repetition pays it off.

### `cambium`

- Best idea: a check that refuses to return a pass it did not earn — run against its own tree, the freshness tool prints `overdue=0` and `fresh=0` together and concludes "NOTHING CHECKED… this is not evidence of freshness", and the vocabulary check exits 1 rather than assume a vocabulary no profile has composed.
- Biggest risk: it ships no corpus, so everything downstream of a composed vocabulary — conformance, freshness, duplicates, MOC coverage, delta application, terminal proof — has no public passing run. The reference profile validates; the vocabulary it would compose is blocked by the repository's own deliberately unfilled governance page.
- Most reusable component: the prohibition that automated checks may never raise a status — the scripts emit only `fail` and `candidate`, so automation can block work and nominate work and can never promote a belief.
- Maturity impression: 5,687 lines of deterministic tooling and 6,453 lines of normative prose against 73 lines of tests covering one of twelve scripts; two things are demonstrated rather than specified — the kernel's own 1,171 wiki links all resolve, and the reference profile binds every interface slot with no unfilled marker left.
- Study when: you are designing quality gates for agent-maintained knowledge and want the vocabulary for separating "checked and fine" from "could not be checked".
- Do not copy when: you need a memory component. It stores nothing, retrieves nothing and ranks nothing — adopting it means adopting a working method, not adding a dependency.

### `perseus-vault`

- Best idea: three independent full runs per benchmark condition, every report committed with a complete config stamp, and the answer prompt folded into the run signature so a chain-of-thought number can never be quoted beside a plain one — the published means recompute from those artifacts exactly.
- Biggest risk: the tombstone's reach is claimed in a comment and not walked by a test. `remember_impl` says the check covers agent remember, capture, ingest, connectors and derived writers, and the committed cases cover the write paths and the audited override — the background consolidation, cohere and dream passes are the leg nothing exercises.
- Most reusable component: the `CLAIMS-AUDIT.md` habit — a file that retires claims it cannot back, naming the retired figure, why it failed, and the artifact that replaced it, including downgrading its own "signed results" to "content-hashed".
- Maturity impression: 59,000 lines of Rust, 536 inline tests, all seven capability marks, and a count claim that is derived from the source registry and asserted across five published surfaces by a CI job rather than by a command in a Markdown file.
- Study when: you are deciding what a defensible benchmark claim looks like, or you want bi-temporal history and a hash-chained journal in a single local binary.
- Do not copy when: you need multi-machine sync, since federation is export and re-import; or encryption on a database that predates the default, since the flip covers fresh installs and an older one stays plaintext until an explicit `init --rekey`.

### `provem`

- Best idea: a replay script that asserts every published number instead of printing it, exiting non-zero on drift — 21 assertions from frozen artifacts at zero cost, 25 with the governance benchmark and unit tests, and it passes.
- Biggest risk: erasure is read-side suppression, not write-side refusal. A re-ingested erased value still lands in the backing store and is stopped on the way out, so every future read path has to consult the registry and the store retains what a subject asked to erase — the sharpest thing to press on a product whose stated purpose is Article 17.
- Most reusable component: `forget(term, scope)` — delete the rows, append the term's token set to a per-tenant erased registry, emit an erasure certificate, and exclude any later record whose tokens are a superset. A value-keyed tombstone with a normalized, forgiving key.
- Maturity impression: 21,000 lines with 7,600 lines of tests, a claim register that marks its own claims `Unsupported` and "Rejected for now", a research journal of negative results, and two of four deployment tiers published as losing — one below the no-memory baseline.
- Study when: governance is your actual problem, or you want to see what a defensible claim looks like when the repository itself fails CI if the README drifts.
- Do not copy when: the governance suite's numbers are being read as general. It is self-authored, so it measures the failure modes its author modelled; a reproducible number is not a generalisable one.

### `argo`

- Best idea: retrieval that fails closed when the embedding index is not qualified, and a write that cannot report success when indexing failed — both asserted by committed acceptance cases rather than described, in a suite of architecture fitness functions running four times the volume of the implementation it covers.
- Biggest risk: the graph is a projection, not a memory. `clearGraph` wipes it with `DETACH DELETE` and re-creates every node on each sync, so there is no supersession, history, status or audit anywhere in the store; correction lives in a JSON file and whatever review surrounds it.
- Most reusable component: the ArchiMate 3.2 rule engine — a constrained relationship vocabulary means a malformed architectural claim is refused by a rule rather than caught in review, which is the schema doing work free-text extraction cannot.
- Maturity impression: 861 commits, 27,152 lines of tests to 6,674 of graph-rag implementation, a 54 KB design document for one subsystem — and the suite is red at HEAD, 114 passed and 8 failed, including its own credential boundary.
- Study when: you already model your system and want an agent that can query architecture instead of re-deriving it, or you want to see architecture fitness functions used as a delivery gate.
- Do not copy when: you need a general-purpose store. The memory here is one project's architecture model, and adopting it means adopting the modelling practice first.

### `sovereign`

- Best idea: refusal as a first-class outcome — energy cost scaled by priority, a boundary that clears only past the threshold plus a margin so it cannot flap, a hard floor, and a returned reason string that lets a caller tell a refusal from a failure from an empty result.
- Biggest risk: an episode has no identifier, and no update, delete, forget or supersede exists anywhere in the module, so nothing stored can be corrected — the question this atlas asks has no place to be asked rather than a bad answer.
- Most reusable component: the hysteresis. Clearing a boundary at `threshold + 0.1` rather than at `threshold` is two characters and removes an entire class of flapping, and it applies to any boundary crossed repeatedly.
- Maturity impression: 634 lines with atomic persistence and a required covenant enforced in the constructor — and `pyproject.toml` is invalid TOML, a root `amity.py` shadows the packaged module byte for byte, and the README calls the committed passing tests "not present yet".
- Study when: you want to see admission control treated as an ethical mechanism rather than a rate limiter, in a codebase small enough to read in one sitting.
- Do not copy when: you need a memory. Recall is a timestamp filter over a bounded deque whose evictions are uncounted, in the one buffer whose contents are the product.

### `memoryops-ai`

- Best idea: tenancy enforced by Postgres row-level security through transaction-local GUCs, so a recall path that forgets its tenant predicate returns nothing instead of everything — the strongest isolation mechanism in this atlas, and stated in the code as defense in depth beside the application check.
- Biggest risk: deletion is record-keyed. `soft_delete` sets `deleted_at` and the dedup lookup is filtered to active rows, so a value that was deleted and is later re-asserted returns as a new active memory — while `normalized_content`, the key that would stop it, is already computed, persisted and compared.
- Most reusable component: the audit chain serialised through a per-tenant head row, so concurrent mutations cannot fork it into two valid-looking histories, with `verify_chain` exported so a caller rather than the writer can check it.
- Maturity impression: 39,000 lines of Python across a monorepo with a published SDK, a hosted demo, RLS migrations, and eval sets that plant a cross-tenant memory before asserting it is unreachable — none of it run for this review, because five dependency surfaces were inside the seven-day cooldown.
- Study when: multi-tenancy is real and you want to see governance placed below the caller rather than beside it.
- Do not copy when: you need a deletion that stays deleted against an automatic writer; the machinery for that is present and unused.

### `deepcode`

- Best idea: typed provenance on conversational input — a `ClientSurface` of `cli`/`desktop`/`headless`/`automation`/`app_server`/`internal` and a `TurnInputSource` of `start`/`steer`/`queue`/`goal_continuation`/`automation`/`retry`, so months later the store can still say whether a person steered a turn or an automation retried it.
- Biggest risk: `autodream` is a scheduled agent turn holding `delete` over a flat directory of markdown notes that has no history, no protected flag and no record a note ever existed — and the only mechanical signal, which the scheduler also treats as its stopping condition, is whether the file count changed.
- Most reusable component: `system_preamble()`, which assembles user-global instructions, a repo-root-downward `AGENTS.md` walk, the memory index and the tool description in one function that every frontend calls, so the TUI, the desktop app, the headless path and the app server cannot drift apart.
- Maturity impression: roughly 118,000 lines of Python with an event-sourced thread store, a crash-recoverable deletion journal, and a memory module whose docstring states plainly that consolidation has no test oracle — while the test beside it patches in a scripted no-op provider and the docstring's claim of verification "with a real model" has no committed counterpart in the tree.
- Study when: you want to see what an event log, replay and typed provenance look like applied to conversation state, and what it costs to leave the durable-facts store outside all of it.
- Do not copy when: a remembered fact is expensive to reacquire. Nothing marks a note as unconsolidatable, nothing records its deletion, and session deletion does not reach the notes at all.

### `prime-agent`

- Best idea: every applied harness edit keeps a full `before` and `after` snapshot, appended to a cross-session `refinements.jsonl`, so `rollbackProposal` can invert a refinement made in another session — the most complete undo for a self-modifying memory in this atlas, and tested as such.
- Biggest risk: nothing is keyed on a rejected value. Rollback answers "can I undo what it learned" and not "can I stop it learning that again", so a memory deleted as wrong can be proposed again by the next pass as a fresh create.
- Most reusable component: the baseline check — an edit whose target entry changed while the model was planning is refused with `entry changed during refinement planning`, with the same-proposal case correctly excluded. A lost-update defence on a memory write, in about ten lines.
- Maturity impression: 184,000 lines of TypeScript and 4,469 commits, with a 1,519-line test file covering the baseline guard, the immutable base prompt from both directions, atomic state replacement, scope-merge collisions, malformed history lines, and cross-session rollback — none of it run for this review, because six dependency surfaces were inside the seven-day cooldown.
- Study when: you are building a background pass that edits durable state on model judgement and want to know what making it reversible actually costs.
- Do not copy when: you need a correction that holds against re-derivation; the undo is excellent and there is no refusal behind it.

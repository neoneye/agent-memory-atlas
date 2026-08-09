---
title: Holographic
eyebrow: Vector-symbolic memory
description: A local SQLite fact store that encodes facts as holographic phase vectors, enabling algebraic entity queries, but collapses truth and usefulness into one feedback-trained score.
root: ../..
page_kind: system
source_name: NousResearch/hermes-agent
source_url: https://github.com/NousResearch/hermes-agent
revision: 0fa5e41c86f022bba147797849f0b44865721476
revision_url: https://github.com/NousResearch/hermes-agent/commit/0fa5e41c86f022bba147797849f0b44865721476
analyzed_at: 2026-07-27
capabilities: ""
stack_storage: "sqlite"
stack_retrieval: "lexical, vector"
stack_source: "seeded"
matrix:
  memory_unit: "Flat fact row plus HRR phase vector and linked entities"
  storage: "Local SQLite (WAL) with FTS5 and per-category bundled banks"
  retrieval: "FTS5 + Jaccard + HRR cosine, multiplied by trust; algebraic `probe`/`related`/`reason`"
  write: "`fact_store` tool, mirrored host writes, optional end-of-session regex extraction"
  update_delete: "Exact update/remove; feedback shifts trust; no supersession"
  scoping: "Category only; no user/project/session scope"
  integration: "Hermes `MemoryProvider` plugin; `fact_store` and `fact_feedback` tools"
  background: "None; bank rebuild is synchronous on every write"
  trust: "None — no source, actor, or session on a fact"
  strengths: "Deterministic hash-derived vectors; `contradict` as a query action"
  risks: "Three downvotes silently drop a fact below the retrieval floor; one score for truth and reachability"
---

## 1. Executive Summary

Holographic is the first-party memory provider shipped inside Hermes Agent at `plugins/memory/holographic/`. It is the only system in this atlas built on a **vector-symbolic architecture**: facts are encoded as Holographic Reduced Representation (HRR) phase vectors, and retrieval uses algebraic `bind`/`unbind`/`bundle` operations rather than a learned embedding model.

The whole plugin is roughly 2,000 lines across four files. That compactness is a feature: unlike most systems here, the entire memory model can be read in an afternoon.

Two things make it worth studying:

- **Deterministic representation without an embedding model.** Atoms are generated from SHA-256 of the token string (`encode_atom`), so vectors are byte-identical across processes, machines, and Python versions. There is no embedder to record, version, or drift — the atlas's usual "record embedder identity" guardrail is satisfied by construction.
- **`contradict` as a first-class retrieval action.** It surfaces fact pairs with high entity overlap and low content similarity. No other system in the atlas exposes contradiction discovery as an ordinary query.

Two things make it a cautionary example, and they are more instructive than the strengths:

- **Trust is one float doing two jobs.** `trust_score` is simultaneously epistemic confidence and retrieval strength; the ranker multiplies it straight into relevance (`score = relevance * trust_score`). This is precisely the split that [Verel](../verel/) and [RainBox](../rainbox/) treat as foundational.
- **User feedback silently deletes memory.** `fact_feedback` moves trust by +0.05 (helpful) or −0.10 (unhelpful), and both search paths default to `min_trust=0.3`. A fact created at the default 0.5 trust falls below the retrieval floor after **three** unhelpful ratings and becomes permanently invisible — with no tombstone, no review queue, and no record that it was ever suppressed. The atlas's "telemetry mistaken for truth" antipattern is not merely present here; it is the trust model.

The plugin also demonstrates a failure mode specific to plugin-shaped memory: it mirrors the host's built-in memory writes into its own store (`on_memory_write`), creating two copies of the same content with independent lifecycles and no reconciliation or deletion propagation.

## 2. Mental Model

The memory unit is a flat fact row. There is no claim/evidence split, no scope, and no status:

```python
facts(
    fact_id         INTEGER PRIMARY KEY,
    content         TEXT NOT NULL UNIQUE,   # dedupe is exact-text only
    category        TEXT DEFAULT 'general', # user_pref|project|tool|general
    tags            TEXT DEFAULT '',
    trust_score     REAL DEFAULT 0.5,       # confidence AND retrieval strength
    retrieval_count INTEGER DEFAULT 0,
    helpful_count   INTEGER DEFAULT 0,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    hrr_vector      BLOB                    # float64 phases, 8 KB at dim=1024
)
```

Entities are resolved into a side table and linked many-to-many, which is what makes the algebraic query actions possible:

```python
entities(entity_id, name, entity_type, aliases, created_at)
fact_entities(fact_id, entity_id)
memory_banks(bank_name, vector, dim, fact_count, updated_at)  # one bundled vector per category
```

The HRR layer is the distinctive part. Each fact is encoded compositionally:

```text
encode_fact(content, entities) =
    bundle(
      bind(encode_text(content), ROLE_CONTENT),
      bind(encode_atom(entity_1), ROLE_ENTITY),
      bind(encode_atom(entity_2), ROLE_ENTITY),
      ...
    )
```

Because `unbind` inverts `bind`, an entity can be algebraically probed out of a fact — or out of a whole category bank — without keyword matching:

```text
unbind(fact_vector, bind(entity, ROLE_ENTITY)) ≈ content_vector
```

Write lifecycle:

```mermaid
flowchart TB
    A["fact_store(action=add)"] --> AF
    B["on_memory_write mirror"] --> AF
    C["on_session_end regex extraction"] --> AF
    AF["add_fact(): INSERT, UNIQUE content"] --> RE["regex entity extraction"]
    RE --> EL["entity resolve and link"]
    EL --> HRR["_compute_hrr_vector()"]
    HRR --> RB["_rebuild_bank(category)<br/><i>full category re-bundle, on every write</i>"]

    style RB fill:#f4e2bd,stroke:#b8860b
```

The highlighted step is the cost of the algebra: because a category bank is one
bundled vector, adding a single fact re-bundles the **whole category**, so write
cost grows with the category rather than with the write.

Retrieval lifecycle:

```mermaid
flowchart TB
    Q["fact_store(action = search, probe, related,<br/>reason or contradict), or prefetch(query)"] --> F["FTS5 candidates<br/><i>limit×3, sanitized OR-query, trust ≥ min_trust</i>"]
    F --> RR["rerank:<br/>0.4 × fts + 0.3 × jaccard + 0.3 × hrr_similarity"]
    RR --> SC["score = relevance × trust_score<br/><i>× optional temporal decay</i>"]
    SC --> TK["top-k, injected <b>unfenced</b> into the prompt"]

    style TK fill:#f4e2bd,stroke:#b8860b
```

Trust multiplies relevance rather than gating it, so a low-trust fact is ranked
down and never excluded. And the result is injected **unfenced** — compare
[RainBox](../rainbox/), which wraps recalled memory and neutralizes angle brackets
before the model sees it.

## 3. Architecture

Core files, all under `plugins/memory/holographic/`:

- `holographic.py` (203 lines): the HRR algebra — `encode_atom`, `bind`, `unbind`, `bundle`, `similarity`, `encode_text`, `encode_fact`, `snr_estimate`. Pure NumPy, no persistence.
- `store.py` (644 lines): SQLite schema, `MemoryStore` CRUD, entity extraction/resolution, trust feedback, HRR vector computation, bank rebuilds, and a process-wide shared-connection registry.
- `retrieval.py` (654 lines): `FactRetriever` with `search`, `probe`, `related`, `reason`, and `contradict`, plus FTS5 query sanitization and Jaccard reranking.
- `__init__.py` (465 lines): the `HolographicMemoryProvider` implementation of Hermes's `MemoryProvider` ABC, tool schemas, and end-of-session regex extraction.

```mermaid
flowchart TD
  Tools["fact_store / fact_feedback<br/>tools"] --> Provider["HolographicMemoryProvider"]
  Hooks["on_memory_write /<br/>on_session_end"] --> Provider
  Provider --> Store["MemoryStore<br/>(SQLite)"]
  Store --> Facts["facts +<br/>FTS5"]
  Store --> Ents["entities / fact_entities"]
  Store --> HRR["holographic.py<br/>encode_fact"]
  HRR --> Vec["facts.hrr_vector"]
  HRR --> Bank["memory_banks (per<br/>category)"]
  Provider --> Retr["FactRetriever"]
  Facts --> Retr
  Vec --> Retr
  Bank --> Retr
  Retr --> Prompt["prefetch() -><br/>system prompt"]
```

## 4. Essential Implementation Paths

### HRR encoding (`holographic.py`)

`encode_atom` derives a phase vector deterministically from SHA-256 counter blocks: it hashes `f"{word}:{i}"`, unpacks each 32-byte digest as sixteen `uint16` values, and scales them to `[0, 2π)`. This is the single best idea in the plugin. Representations are reproducible everywhere with no model download, no API call, and no dimension negotiation.

The algebra is phase arithmetic: `bind` is `(a + b) % 2π`, `unbind` is `(a - b) % 2π`, and `bundle` is the circular mean of complex exponentials. `similarity` is `mean(cos(a - b))`.

`encode_text` bundles the atoms of each whitespace token — a **bag of words**. Word order is not represented, so "Alice owes Bob" and "Bob owes Alice" encode identically. For a store whose headline feature is contradiction detection, this is a material limitation.

### Write path (`store.py:add_fact`)

Deduplication is a `UNIQUE` constraint on exact `content`. On collision the existing `fact_id` is returned unchanged. There is no semantic dedupe, no subject/predicate key, and no conflict detection: two facts that contradict each other are simply two rows, both at trust 0.5.

Entity extraction is regex-only (`_extract_entities`): capitalized multi-word phrases, double-quoted terms, single-quoted terms, and `X aka Y` patterns. Note that `_RE_CAPITALIZED` requires **two or more** capitalized words, so single-token entities like `Python` or `Copenhagen` are never extracted unless the user quotes them. Since `probe`, `related`, `reason`, and `contradict` all depend on entity links, this quietly caps the reach of every algebraic action.

`_resolve_entity` matches with `SELECT entity_id FROM entities WHERE name LIKE ?`. `LIKE` treats `%` and `_` as wildcards and the parameter is not escaped, so an entity containing an underscore can silently resolve to a different entity — distinct entities merge without warning.

Every successful write calls `_rebuild_bank(category)`, which re-reads every fact vector in that category and re-bundles them. Write cost is therefore O(facts in category) on each add.

### Retrieval (`retrieval.py`)

`search` is genuine hybrid fusion: FTS5 supplies `limit*3` candidates, then each is rescored as `0.4*fts_rank + 0.3*jaccard + 0.3*hrr_similarity`, multiplied by `trust_score`, with optional exponential temporal decay (disabled by default, `half_life=0`).

`_sanitize_fts_query` is a well-judged detail: FTS5 AND-joins bare multi-word MATCH arguments, which destroys recall on prose queries, so the helper drops stopwords, strips FTS5 operator characters, phrase-quotes each surviving token, and OR-joins them.

`probe`, `related`, and `reason` are the algebraic actions. `reason` is the most interesting: it unbinds each requested entity from every fact vector and scores by the **minimum** per-entity similarity, giving AND semantics across entities. `probe` has two distinct code paths — bank-based extraction when a category bank exists, and direct per-fact scoring otherwise — which return different-quality results for the same call.

`contradict` compares all fact pairs, keeps those with entity-overlap Jaccard ≥ 0.3, and scores `entity_overlap * (1 - normalized_content_similarity)`. It is O(n²) and guards itself by truncating to the 500 most recently updated facts. The truncation is silent: no field in the response indicates that older facts were not compared.

### Trust feedback (`store.py:record_feedback`)

```python
_HELPFUL_DELTA   =  0.05
_UNHELPFUL_DELTA = -0.10
```

The asymmetry is deliberate and sensible in isolation. The problem is what it interacts with: `min_trust` defaults to 0.3 in `search_facts`, `FactRetriever.search`, and the exposed tool schema. Starting from `default_trust=0.5`, three unhelpful ratings put a fact at 0.2 — below every default retrieval floor. The row still exists and `list` with `min_trust=0` still shows it, but no ordinary recall path will ever return it again, and nothing records that a suppression occurred.

### Auto-extraction (`__init__.py:_auto_extract_facts`)

Disabled by default (`auto_extract: false`). When enabled, `on_session_end` scans user messages against six regexes (`I prefer|like|love|use|want|need`, `my favorite/preferred/default … is`, `I always/never/usually`, `we decided/agreed/chose`, `the project uses/needs/requires`) and stores the **raw matching user message**, truncated to 400 characters, as a fact.

This is zero-LLM capture, which the atlas generally endorses — but the stored artifact is conversational prose rather than a normalized claim, which then degrades the content-vector comparisons that `contradict` depends on.

The code carries two revealing guards. Comments cite issues #57682 and #57690: the context compactor's own handoff summaries are injected as `role="user"` messages, their prose reliably matched the decision patterns, and the compactor's generated output was consequently stored as durable "facts" on every context rollover. The fix distinguishes a merged summary's genuine pre-delimiter user content from its generated suffix. This is a clean, concrete instance of derived text laundering itself back into an evidence store — a feedback loop any system with automatic capture should test for explicitly.

## 5. Memory Data Model

Storage is a single SQLite database (`$HERMES_HOME/memory_store.db`) in WAL mode, with a documented fallback for NFS/SMB/FUSE mounts.

The concurrency engineering is the most mature part of the codebase. A process-wide `_shared` registry keyed on the resolved database path gives every `MemoryStore` instance one connection and one re-entrant lock, refcounted so closing one instance cannot pull the connection out from under a sibling. The connection uses `isolation_level=None` (autocommit) specifically so a write that raises mid-method cannot strand a write transaction. The accompanying comment explains the production failure it fixes: multiple providers in one process — the main agent plus every `delegate_task` subagent — raced as independent WAL writers until one pinned the write lock and starved the rest.

What the data model does **not** have is equally important:

- **No scope of any kind.** `store.py` describes itself as a "Single-user Hermes memory store plugin". There is no user, agent, project, session, or tenant column. `category` is a four-value enum used for partitioning banks, not for access control.
- **No status or lifecycle state.** Nothing distinguishes candidate from verified from rejected from stale.
- **No provenance.** A fact records no source message, actor, or session. Once written, a model-inferred fact, a mirrored built-in memory write, and an explicit user statement are indistinguishable.
- **No supersession or correction chain.** `update_fact` mutates the row in place.

## 6. Retrieval Mechanics

Ranking is genuinely multi-signal and is the plugin's strongest conventional feature: lexical FTS5, token Jaccard, and HRR cosine, fused with fixed weights and multiplied by trust.

Three caveats matter for anyone borrowing it.

**Trust is baked into relevance.** `score = relevance * trust_score` means a well-matched but lightly-downvoted fact loses to a poorly-matched trusted one, and there is no way to ask "what is the most relevant memory regardless of how it has been rated?"

**HRR contributes a neutral 0.5 when unavailable.** If NumPy is missing, `FactRetriever` silently redistributes weights to `fts=0.6, jaccard=0.4` and `is_available()` still returns `True`. The provider continues to advertise itself as "holographic" while running as an ordinary lexical store. Individual facts lacking a vector also score a neutral 0.5 rather than being excluded.

**Bank capacity is computed and discarded.** `snr_estimate(dim, n_items)` returns `sqrt(dim/n_items)` and logs a warning below SNR 2.0 — i.e. above `dim/4` = 256 facts per category at the default dimension. But `_rebuild_bank` calls it purely for the side effect and ignores the return value, so saturation produces a log line rather than a guard, a fallback, or a field in the response. The module's own `bundle` docstring gives a stricter bound still — "O(sqrt(dim)) items", about 32 at dim=1024 — so the two capacity estimates in the same file disagree by roughly 8×. Neither is enforced.

## 7. Write Mechanics

Three write paths converge on `add_fact` with no shared policy layer:

1. **Explicit tool calls** — `fact_store(action="add")` from the model.
2. **Mirrored host writes** — `on_memory_write` copies every built-in Hermes memory `add` into the fact store, mapping `target == "user"` to category `user_pref`.
3. **End-of-session regex extraction** — when `auto_extract` is enabled.

None of these is distinguished in the stored row. Path 2 is the most consequential: the same content now exists in Hermes's `MEMORY.md`/`USER.md` **and** in `memory_store.db`, with independent lifecycles. Editing or deleting the Markdown does not remove the mirrored fact, because `on_memory_write` only handles `action == "add"` — the `remove` action documented in the ABC is ignored by this provider. Host-level forgetting therefore does not propagate.

## 8. Agent Integration

Holographic implements Hermes's `MemoryProvider` ABC (`agent/memory_provider.py`, 315 lines), which is the most explicit pluggable-memory-provider contract in the atlas. It defines roughly seventeen lifecycle members: `initialize`, `system_prompt_block`, `prefetch`, `queue_prefetch`, `sync_turn`, `get_tool_schemas`, `handle_tool_call`, `shutdown`, `on_turn_start`, `on_session_end`, `on_session_switch`, `on_pre_compress`, `on_delegation`, `on_memory_write`, `get_config_schema`, `save_config`, and `backup_paths`.

The same directory ships first-party adapters for every other provider Hermes supports — `byterover`, `hindsight`, `honcho`, `mem0`, `openviking`, `retaindb`, `supermemory` — so the *adapters* are reviewable even when the backing service is not. `MemoryManager` enforces a one-external-provider limit to avoid tool-schema bloat.

The contract has a conspicuous hole, and it is the reason this ecosystem deserves its own [pattern page](../../patterns/pluggable-memory-provider/): **there is no deletion or forgetting hook.** No `forget`, no `delete_scope`, no tenant or user parameter anywhere in the ABC. A host-level erasure request has no defined path into a provider's store.

Two model-facing surfaces deserve scrutiny:

- `prefetch` injects the top five facts into the system prompt as `- [0.5] <content>` with **no fencing or neutralization**. Combined with enabled auto-extraction — where a raw user message becomes a durable fact — this is a persistent prompt-injection path: text that a user (or a quoted third party) writes once can be replayed into every later prompt as trusted-looking context. Contrast [Verel](../verel/) and [RainBox](../rainbox/), which fence recalled memory as untrusted data.
- The `fact_store` tool description ends with "IMPORTANT: Before answering questions about the user, ALWAYS probe or reason first" — tool description as policy, which the atlas treats as necessary but never sufficient.

## 9. Reliability, Safety, and Trust

Strengths:

- Deterministic, reproducible vectors with no embedder version to track.
- Serious, well-documented SQLite concurrency handling with refcounted shared connections and autocommit.
- Deterministic recovery path: `rebuild_all_vectors()` recomputes every vector and bank from stored text, so the vector layer is a true rebuildable projection.
- Graceful degradation when NumPy is absent.
- `contradict` gives operators a way to *discover* inconsistency, which most systems lack entirely.

Gaps, roughly in order of severity:

- **Feedback is deletion.** Three downvotes suppress a fact permanently with no tombstone, review surface, or audit record. "Unhelpful" and "false" are conflated.
- **One score for truth and usefulness.** No separation of epistemic confidence from retrieval strength.
- **No scope.** Single-user by construction; nothing prevents facts from one project or persona surfacing in another.
- **No provenance.** Source, actor, and session are not recorded, so a wrong fact cannot be traced or explained.
- **Unfenced prompt injection of recalled content**, which auto-extraction makes durable.
- **No deletion propagation** between the host's built-in memory and the mirrored fact store.
- **`contradict` reports but never resolves.** It has no supersession, tombstone, or review workflow; the operator is handed pairs and left to run `update`/`remove` manually.
- **Silent caps**: the 500-fact contradiction window and the ignored SNR ceiling both degrade quality without signalling it.

The `contradict` docstring asserts "no other memory system does this". Within this atlas that is not accurate: [RainBox](../rainbox/) performs lattice-aware conflict detection at write time, [Verel](../verel/) maintains explicit rejected states, and [engram](../engram/) surfaces conflict candidates for judgment. What is genuinely unusual is doing it *algebraically over vectors* and exposing it as an ordinary read action rather than a write-time gate — which is also its weakness, since detection after the fact cannot prevent the contradiction from being recalled in the meantime.

## 10. Tests, Evals, and Benchmarks

Holographic-specific coverage is 599 lines across four files, plus 1,662 lines exercising the provider ABC:

- `tests/plugins/memory/test_holographic_store.py` (243 lines)
- `tests/plugins/memory/test_holographic_auto_extract.py` (170 lines)
- `tests/plugins/memory/test_holographic_retrieval.py` (129 lines)
- `tests/plugins/memory/test_holographic_shutdown_closes_db.py` (57 lines)
- `tests/agent/test_memory_provider.py` (1,662 lines)

The suites were not run for this review. Coverage is oriented toward CRUD, retrieval mechanics, the auto-extract contamination guards, and connection shutdown — the areas where production bugs were actually found. There is **no committed retrieval-quality benchmark**, and no evaluation of whether HRR similarity outperforms the FTS5 and Jaccard signals it is fused with. Given that HRR carries only 0.3 of the relevance weight and falls back to a neutral constant when unavailable, its measured contribution to recall is currently unknown.

The README documents configuration and the nine `fact_store` actions but no decay, forgetting, or capacity guidance. Two open issues in the tracker ([#4781](https://github.com/NousResearch/hermes-agent/issues/4781), [#31263](https://github.com/NousResearch/hermes-agent/issues/31263)) report that the plugin registers but its tools or context injection do not fire; those threads were not read for this review, and the titles alone do not establish a reproducible defect in the code inspected here.

## 11. For Your Own Build

### Steal

- **Deterministic hash-derived representations.** `encode_atom` removes the entire class of embedder-drift problems: no model to pin, no dimension to negotiate, identical vectors on every machine. Worth copying for any system where reproducibility matters more than semantic nuance.
- **Algebraic multi-entity query.** `reason`'s min-similarity-across-entities gives true AND semantics over structure, which is awkward to express in a plain vector store.
- **Contradiction as a queryable action.** Entity-overlap × content-divergence is a cheap, model-free heuristic for surfacing inconsistency, and belongs in more systems as a review aid.
- **FTS5 query sanitization.** Dropping stopwords and OR-joining phrase-quoted tokens is a small fix for a real and widespread recall bug in FTS5-backed memory.
- **Refcounted shared SQLite connections.** The registry in `store.py` is a reusable answer to multi-writer WAL contention when subagents share a process.
- **Rebuildable vector projections.** `rebuild_all_vectors()` treats text as canonical and vectors as derived.

### Avoid

- **Telemetry as truth, with deletion as a side effect.** The clearest instance in the atlas: a rating tool directly mutates the score that gates retrieval, and enough ratings remove the memory from recall entirely.
- **One score for confidence and reachability.**
- **Bag-of-words encoding under a compositional banner.** Word order is discarded, so relational facts and their inversions are indistinguishable.
- **Unescaped `LIKE` for identity resolution**, allowing distinct entities to merge.
- **Capacity computed and ignored**, with two mutually inconsistent capacity estimates in one module.
- **Silent truncation** of the contradiction comparison set.
- **Dual-write to host and provider stores** with no reconciliation or deletion propagation.
- **Unfenced injection** of stored prose into the system prompt.
- **Entity extraction that misses single-word entities**, silently limiting every algebraic action.

### Fit

Borrow:

- `encode_atom`'s SHA-256 phase derivation, and the `bind`/`unbind`/`bundle` algebra, if compositional structure matters to you.
- `_sanitize_fts_query` more or less verbatim.
- The shared-connection registry pattern.
- The `contradict` heuristic — as an input to a review queue, not as an output on its own.

Do not copy:

- The trust model. Split epistemic confidence from retrieval strength before wiring any feedback tool to either, and route suppression through an explicit rejected state rather than a threshold.
- Feedback that changes reachability without an audit trail.
- Scope-free storage, unless the deployment really is single-user forever.
- `prefetch` as written; fence recalled content before it enters a prompt.

## 12. Open Questions

- Does HRR similarity measurably improve retrieval over FTS5 + Jaccard alone? Nothing in the repository answers this, and the 0.3 weight makes it easy to overestimate.
- What is the intended behaviour when a category bank saturates past SNR 2.0 — should `probe` fall back to per-fact scoring, or should banks shard?
- Should `fact_feedback` write a tombstone or review row instead of silently crossing the `min_trust` floor?
- How should a host-level "forget this" propagate to a provider when the `MemoryProvider` ABC has no deletion hook?
- Should mirrored `on_memory_write` facts be marked as derived, so that host deletions can find and remove them?
- Would sequence-aware encoding (positional binding) fix the "Alice owes Bob" inversion problem without abandoning the deterministic-atom property?

## Appendix: File Index

- HRR algebra: `plugins/memory/holographic/holographic.py`.
- Store, schema, entities, trust: `plugins/memory/holographic/store.py`.
- Hybrid and algebraic retrieval: `plugins/memory/holographic/retrieval.py`.
- Provider, tools, auto-extraction: `plugins/memory/holographic/__init__.py`.
- Provider contract: `agent/memory_provider.py`.
- Sibling provider adapters: `plugins/memory/{byterover,hindsight,honcho,mem0,openviking,retaindb,supermemory}/`.
- Tests: `tests/plugins/memory/test_holographic_*.py`, `tests/agent/test_memory_provider.py`.

## History

**2026-07-27** — [`0fa5e41c86f022bba147797849f0b44865721476`](https://github.com/NousResearch/hermes-agent/commit/0fa5e41c86f022bba147797849f0b44865721476) — first reading.

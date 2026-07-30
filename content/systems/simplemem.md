---
title: "SimpleMem"
eyebrow: "Compression-first research memory"
description: "A memory unit that resolves its own pronouns and absolute-dates its own timestamps, behind a store whose only removal verb is clear() — and a second subsystem in the same repository that has the scope key, the status field and the audit trail the first one lacks."
root: ../..
page_kind: system
source_name: "aiming-lab/SimpleMem"
source_url: https://github.com/aiming-lab/SimpleMem
revision: db80b6a7c591e0ea730a058e9f5fc4eb06572299
revision_url: https://github.com/aiming-lab/SimpleMem/commit/db80b6a7c591e0ea730a058e9f5fc4eb06572299
analyzed_at: 2026-07-30
capabilities: "scope_enforced, audit_log"
matrix:
  memory_unit: "A `MemoryEntry` — a lossless restatement with pronouns resolved and times absolute, plus keywords, timestamp, location, persons, entities and topic"
  storage: "LanceDB behind a small vector-store wrapper for the text pillar; a separate SQLite schema with seven tables for EvolveMem"
  retrieval: "Query analysis, then parallel semantic, keyword and structured searches, merged and deduplicated, then an LLM adequacy check that can fire further query rounds"
  write: "Windowed LLM extraction over dialogue batches, parallelised across workers; entries are added, never revised"
  update_delete: "The text store has `add_entries`, `get_all_entries` and `clear()` — no delete, no update. EvolveMem adds `update_content`, archive, and a `superseded` status"
  scoping: "Absent from the text pillar entirely; `scope_id NOT NULL` on every EvolveMem read, with a `scope_access` principal/permission table beside it"
  integration: "A CLI, an MCP server, an HTTP server with per-user API keys, a Claude skill, and a benchmark runner per pillar"
  background: "None on the text path. EvolveMem runs a closed-loop evaluate-diagnose-propose-guard cycle that rewrites retrieval configuration, not memories"
  trust: "An `importance` and a `confidence` float on EvolveMem units, moved by thumbs-up/down feedback; the text pillar has no trust representation at all"
  strengths: "Memory units built to be context-independent — coreference resolved and time absolutised at write; an append-only event log recording seven mutation kinds"
  risks: "Six headline benchmark figures and no committed result artifact for any of them; the pillar the papers are about cannot delete or correct a single memory"
---

## 1. Executive Summary

SimpleMem is an academic memory system from AIMING Lab, MIT-licensed, and the
repository holds **three products** rather than one: SimpleMem (text, the
[arXiv:2601.02553](https://arxiv.org/abs/2601.02553) paper), Omni-SimpleMem
(multimodal, v2.0), and EvolveMem (v3.0, self-evolving retrieval). Roughly
114,000 lines of Python, of which the `simplemem/` package is 49,782.

The idea worth the read is in 433 lines. `MemoryBuilder` runs an LLM over
windows of dialogue and emits `MemoryEntry` objects whose defining property is
**context independence**: the field is called `lossless_restatement` and its
schema documents two transforms — `Φ_coref`, no pronouns, and `Φ_time`, absolute
timestamps — so a stored unit reads *"Alice discussed the marketing strategy for
new product XYZ with Bob at Starbucks in Shanghai on November 15, 2025 at
14:30"* rather than *"she told him about it there"*. Almost every system in this
atlas stores the second kind and hopes retrieval supplies the missing context.
Resolving it at write is cheap, one-time, and makes every later retrieval
independent of the turn it came from.

Then the store it goes into. `VectorStore`
(`simplemem/core/database/vector_store.py`) exposes `add_entries`, three
searches, `get_all_entries`, `optimize` and **`clear`**. There is no delete and
no update — not for a memory, not for a fact, not for a user. Wiping the whole
store is the only removal verb the text pillar has, which is the finding this
atlas recorded for [AutoGen](../autogen/)'s protocol, arriving here in a system
that ships the implementation rather than an interface. `MemoryEntry` has no
user id, no session id and no scope key, so there is also nothing to delete
*by*.

**The claims are the other half of the report.** The README makes six specific
quantitative claims — a 26.4% average F1 gain on LoCoMo with roughly 30×
less inference-time token consumption; LoCoMo F1 = 0.613 (+47%) and Mem-Gallery
F1 = 0.810 (+51%) for Omni-SimpleMem; +25.7% on LoCoMo and +18.9% on MemBench
for EvolveMem — and a "Benchmark & Reproduce" section with a runner per pillar.
A search of the repository at this commit returns **zero `.json`, `.jsonl` or
`.csv` files of any kind**. Not a scored result, not a raw prediction dump, not
a metrics table. The harness is committed and the results are not, which is the
same traceability gap the atlas records for [Memvid](../memvid/),
[MemoryOS](../memoryos/) and FiFA — here at six figures rather than three.

## 2. Mental Model

The text pillar has no epistemic model whatsoever. A memory becomes true by
being extracted, and there is no path by which it stops being true: no status,
no confidence, no supersession, no delete. The system's entire answer to "the
world changed" is that a later dialogue produces a later entry, and both are
now in the index, both retrievable, with nothing marking which is current.

Because `MemoryEntry.timestamp` is the *event's* time — the moment described,
not the moment recorded — the store cannot even sort by recency of belief. This
is worth naming precisely, because it is the mirror image of the corpus. Almost
every system here tracks record time and no validity time, which is why the
[bi-temporal](../../patterns/bi-temporal-fact-validity/) column is
thin. SimpleMem tracks **validity time and no record time**. It knows when
things happened and not when it learned them, so "what did we believe last
March" is unanswerable from the other direction, and the mark is withheld for the
same reason: one clock is one clock.

EvolveMem, the third pillar, has the model the first one lacks — `status`
taking `active`, `archived` or `superseded`, an `importance` and a `confidence`
float, feedback that moves importance, and a supersession event naming what
replaced a memory. It is a lifecycle rather than an epistemology: `archived` and
`superseded` say a record is out of service, not that a claim is doubted, and
the `confidence` default of 0.7 is never revised by corroboration. No
`trust_state` mark, and the near-miss is that the field exists and answers a
different question.

## 3. Architecture

The text pillar needs a vector database and a model provider. `VectorStore`
wraps LanceDB with a pluggable backend module beside it, and the whole storage
layer is 1,784 lines including the retriever. There is no service, no queue and
no background worker: extraction happens when you call it, retrieval happens
when you ask, and both are synchronous LLM calls.

EvolveMem is a different shape: SQLite with seven tables — `memories`,
`memory_events`, `memory_links`, `memory_watches`, `memory_annotations`,
`scope_access`, `stats_snapshots` — plus a `schema_version` table and FTS. Its
`store.py` is 1,798 lines and its `manager.py` is 5,064, which is three times
the entire text pillar.

Around them the repository ships an MCP server, an HTTP server with per-user API
keys and a `user_store`, a Claude skill, a Dockerfile and compose file, and a
102-line frontend that is a landing page rather than a console.

## 4. Essential Implementation Paths

- `simplemem/core/models/memory_entry.py` — the unit, and the two transforms
  that define it.
- `simplemem/core/memory_builder.py` (433) — windowed extraction, parallel
  batches, the prompt.
- `simplemem/core/hybrid_retriever.py` (969) — query analysis, parallel search
  across three indexes, adequacy check, further rounds.
- `simplemem/core/database/vector_store.py` — the add-only store.
- `simplemem/evolver/store.py` (1,798) — the schema, the event log, scope
  filtering, supersession.
- `simplemem/evolver/manager.py` (5,064) — the EvolveMem surface.
- `simplemem/evolver/evolution.py` (1,727) — the evaluate/diagnose/propose loop.

## 5. Memory Data Model

`MemoryEntry` is a Pydantic model with three declared index layers: semantic
(the restatement, dense-embedded), lexical (`keywords`, for BM25-style match),
and symbolic (`timestamp`, `location`, `persons`, `entities`, `topic`, as
metadata constraints). The tripartite split is clean and the docstrings cite the
paper's section numbers, which makes the code readable against the method.

What the model does not carry is as informative: no scope key, no source or
provenance pointer back to the dialogue it came from, no record timestamp, no
status, no confidence, no version. An entry is a `uuid4` and six content fields.

EvolveMem's `memories` table carries the rest — `scope_id NOT NULL`,
`importance`, `confidence`, `status`, `created_at`, `updated_at`, tags — and its
`memory_annotations` table has an `author` column, which is the only place in
the repository where a human is modelled as a distinct writer.

## 6. Retrieval Mechanics

`HybridRetriever.retrieve` is the paper's "intent-aware retrieval planning" and
it is LLM-heavy. `_analyze_query` asks a model what the query needs;
`_generate_search_queries` expands it; `_execute_parallel_searches` runs
semantic, keyword and structured searches across threads; `_merge_and_
deduplicate_entries` folds them; `_check_answer_adequacy` asks a model whether
the assembled context can answer the question, and if not,
`_generate_additional_queries` fires another round.

That is a genuinely careful retrieval design — the adequacy check is a form of
[retrieval hysteresis](../../patterns/retrieval-hysteresis/) applied to
sufficiency rather than to churn, and few systems here re-query on their own
judgement. It is also three or more model calls before an answer is attempted,
which is the cost side of the 30× token claim: fewer tokens *in the context
window*, more calls to get there. Nothing in the repository measures the
tradeoff in latency or in provider spend.

**Scope is absent from this path entirely.** No scope key is stored, so none is
filtered. The `scope_enforced` mark on this report comes from EvolveMem, where
`WHERE scope_id = ?` appears on every read of `memories`, `memory_events` and
the stats tables, backed by a `scope_access` table keyed on
`(scope_id, principal, permission)` with an `admin` permission that satisfies
any check.

## 7. Write Mechanics

Writes block. `add_dialogue(dialogue, auto_process=True)` accumulates into a
window and `process_window` calls the model; `add_dialogues_parallel` shards
large batches across a worker pool. Extraction is one LLM call per window, and
the memory is retrievable as soon as it is written — no queue, no lag, no
background consolidation. For a benchmark harness this is the right shape; for a
deployed agent it means a conversation turn pays the extraction cost inline.

Nothing rewrites the store. There is no consolidation pass, no decay, no
promotion between tiers, and no compaction — the "online semantic synthesis"
of the paper happens *within* a window at write time, not across the store
afterwards. That is a real simplification and the source of most of the
system's clarity.

## 8. Agent Integration

An MCP server, an HTTP server with API-key-per-user auth and session objects, a
CLI, and a packaged Claude skill (`SimpleMem.skill`, `SKILL/`). The HTTP layer
is the only place `user_id` appears in the text pillar, and it scopes *sessions
and API keys*, not memories — `delete_session` removes a session, and the
entries that session produced stay in the shared vector store with nothing
linking them back.

## 9. Reliability, Safety, and Trust

**`memory_events` earns the `audit_log` mark, and it is the best-built thing in
the repository after the memory unit.** The table is created with the comment
"Event log for audit trail", carries `event_id` autoincrement, timestamp, type,
memory id, scope and detail, and is written by a single `_log_event` helper at
seven call sites: `create`, `share`, `merge`, `archive`, `pin`, `feedback` and
`supersede`. No `DELETE FROM memory_events` or `UPDATE memory_events` appears
anywhere in the repository, so it is append-only in fact as well as in
intention, and `share` and `merge` — the two events most likely to lose
provenance — record their source ids in `detail`.

The gap is that it audits the pillar nobody benchmarks. The text store that the
papers, the claims and the skill are about writes no events, because it has no
mutations to write: nothing there ever changes after it is added.

**No tombstone, and the shape of the miss is unusual.** EvolveMem supersedes by
status and logs `supersede` with `by=<id>`, which is record-keyed like every
supersession here. But the text pillar cannot even express removal, so a value
a user rejects is not merely re-assertable — it was never retractable in the
first place. `clear()` is the whole vocabulary.

**Annotations are not a review surface**, and the distinction matters because
the table looks like one. `add_annotation(memory_id, content, author)` inserts
a note; `get_annotations` reads it back; nothing in retrieval, ranking or
lifecycle consults annotations at all. A person can write in the margin and the
system will never read it. `record_feedback(memory_id, helpful)` does have an
effect — ±0.03/0.05 on `importance`, clamped — but it moves a ranking float,
not a status, so a memory a user marked unhelpful ten times still surfaces,
slightly lower. `human_review` is withheld.

## 10. Tests, Evals, and Benchmarks

311 test functions across roughly twenty files, none run here. The distribution
is the story: `tests/` at the repository root holds 636 lines covering the
vector store and its backend, and the rest live under `cross/tests/`,
`OmniSimpleMem/tests/` and `MCP/`. For 114,000 lines and three products this is
a thin posture, and the components carrying the paper's contribution — the
extraction prompt, the restatement transforms, the adequacy check — are not
where the tests are.

`test_locomo10.py` is committed at the root, with a second copy under
`MCP/reference/`, and `EvolveMem/run_benchmark.py` and `run_evolution.py`
beside it. The harnesses are real. What is missing is any artifact they
produced: no scored output, no per-question predictions, no results table in
`docs/`. Every one of the six headline numbers in the README is therefore a
claim about a run that is not in the repository, and this atlas has no way to
check any of them.

No negative evaluation exists — nothing asserts that particular material must
not be retrieved — which follows from there being no deletion, no scope on the
text path, and no rejection to assert about.

## 11. For Your Own Build

### Steal

- **Resolve coreference and absolutise time at write.** A memory that reads
  correctly with no surrounding turn is worth more than a better retriever over
  memories that do not. This is one prompt and it is the single most portable
  idea in the repository.
- **Declare your index layers and keep them separate.** Semantic, lexical,
  symbolic, with the unit carrying the fields each needs, means a structured
  filter and a fuzzy match are not fighting over one embedding.
- **Let the retriever judge its own sufficiency.** `_check_answer_adequacy`
  followed by another query round is a cheap way to stop returning k chunks and
  hoping. Budget it, because it is a model call.
- **One `_log_event` helper, called at every mutation site.** Seven event types,
  one insert path, no update or delete anywhere in the file. That is how an
  audit log stays an audit log.

### Avoid

- **A store whose only removal verb is `clear()`.** It is defensible in a
  benchmark harness and indefensible the moment a real user says "forget that".
  Ship a delete before you ship a skill.
- **Publishing the harness and withholding the results.** Six numbers with a
  reproduce section and no committed artifact puts the entire verification cost
  on every reader, and it is the failure mode this atlas has now recorded four
  times.
- **Annotations nothing reads.** An `author` column and a note that never
  reaches ranking, retrieval or lifecycle is a comment field, and calling it
  review would be generous.
- **Two memory subsystems where the governed one is not the one you benchmark.**
  The scope key, status field and audit trail are all in EvolveMem; the paper,
  the claims and the packaged skill are all the text pillar.

### Fit

This is research code, and it should be read as the source of one very good idea
rather than as a memory layer to deploy. Take the restatement transform into
your own extractor — it is a prompt and a schema, and it will improve any
retrieval you already have. Take the event-log discipline from EvolveMem if you
need an audit trail and do not want an event-sourcing framework.

Do not deploy the text pillar behind a user-facing agent. It cannot delete, it
cannot scope, and it cannot correct, so the first support request you cannot
answer is "remove what it learned about me". EvolveMem is the part with the
governance apparatus, and it is also the newest, least documented and least
tested of the three.

## 12. Open Questions

- **Do any of the six figures reproduce?** The harness is committed and the
  results are not. Running `test_locomo10.py` against a LoCoMo checkout is the
  obvious check and was not done here.
- **What does the reflection loop cost?** Query analysis, expansion, parallel
  search and an adequacy check are three-plus model calls per retrieval. The
  30× token claim is about context, not calls, and the two are not the same
  budget.
- **Is `Φ_coref` measured?** The correctness of the restatement — whether the
  extractor resolves pronouns to the right person — decides everything
  downstream, and no test or metric in the repository touches it.
- **Are the three pillars converging?** They share a name and a repository and
  almost no code, and EvolveMem's SQLite schema knows nothing of the text
  pillar's LanceDB entries.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `simplemem/evolver/manager.py` | 5,064 | The EvolveMem API surface |
| `simplemem/evolver/store.py` | 1,798 | Seven-table SQLite schema, `_log_event`, scope filtering |
| `simplemem/evolver/evolution.py` | 1,727 | Evaluate, diagnose, propose, guard |
| `simplemem/multimodal/orchestrator.py` | 1,431 | Omni-SimpleMem's four-modality pipeline |
| `simplemem/core/hybrid_retriever.py` | 969 | Query planning, parallel search, adequacy check |
| `simplemem/evolver/diagnosis.py` | 955 | Per-question failure analysis |
| `simplemem/core/memory_builder.py` | 433 | Windowed extraction into `MemoryEntry` |
| `simplemem/core/answer_generator.py` | 153 | Answer synthesis over retrieved entries |
| `simplemem/core/models/memory_entry.py` | ~70 | The unit, and the two transforms |
| `tests/test_vector_store*.py` | 636 | The root test suite, in full |

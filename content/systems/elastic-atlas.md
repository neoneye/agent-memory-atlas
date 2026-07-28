---
title: Elastic Atlas
eyebrow: Evaluated demo
description: A research demo putting episodic, semantic and procedural memory in three Elasticsearch indices — and shipping both a recall eval and a stress test, which almost nothing else in this atlas does.
root: ../..
page_kind: system
source_name: noamschwartz/atlas-memory-demo
source_url: https://github.com/noamschwartz/atlas-memory-demo
revision: 0bd36a7b177a09aad97dc78efeb5fb43b9322f6d
revision_url: https://github.com/noamschwartz/atlas-memory-demo/commit/0bd36a7b177a09aad97dc78efeb5fb43b9322f6d
analyzed_at: 2026-07-28
capabilities: "scope_enforced"
matrix:
  memory_unit: "Document in one of three indices: episodic event, semantic fact, procedural playbook"
  storage: "Elasticsearch — `atlas_memory_episodic`, `atlas_memory_semantic`, `atlas_memory_procedural`"
  retrieval: "RRF retriever fusing BM25 with a semantic query over auto-embedded fields"
  write: "Agent writes on every turn; auto-embedding via `semantic_text` inference, no client-side calls"
  update_delete: "Consolidation dedupes episodic into semantic and updates playbooks; no tombstone"
  scoping: "`user_id` per persona, applied on recall"
  integration: "Backend service plus an MCP server for Claude Code, Claude Desktop, Cursor"
  background: "Consolidation — one model pass distils episodic events into semantic facts and playbooks"
  trust: "Provenance by index and source event; no trust state on a fact"
  strengths: "A committed recall eval computing Recall@k and MRR, plus a stress test"
  risks: "A research demo by its own description; consolidation is a single model pass with no gate"
---

> **Naming.** This system calls itself *Atlas*, and this site is the *Agent
> Memory Atlas*. They are unrelated projects — Elastic's is a memory system,
> this is a review of memory systems.

## 1. Executive Summary

`atlas-memory-demo` is an MIT-licensed research demo from Elastic, about 18,000
lines in its backend, showing "how Elasticsearch can be the **unified cognitive
layer** for any AI agent". Three synthetic personas carry months of history; the
agent reads and writes memory every turn; the same layer is exposed over MCP.

It calls itself a demo and it is one. It is here because of what it ships
alongside the implementation.

**It commits a retrieval-quality eval, and the eval is honest about its own
construction:**

> "For each persona, samples a fixed set of memory docs across the three indices…
> For each sampled doc, an LLM generates two natural questions a user might ask
> whose answer is that doc. The eval then runs every question through
> `recall_memory` against the owning persona's `user_id` and checks whether the
> source doc surfaces in the top-k results — matched on the doc's Elasticsearch
> `_id`. Computes Recall@1 / Recall@5 / Recall@10, MRR (capped at k=10)."

Matching on `_id` rather than on text is the detail that makes it a measurement
rather than a vibe: there is no judge deciding whether the returned passage is
"about" the right thing, so the number is reproducible. The
[benchmarks page](../../benchmarks/) records that most systems here either have
no retrieval eval or have a harness with no committed results; this has a harness
whose method is legible enough to criticise.

And separately, `scripts/atlas/stress_test.py` — 692 lines. The atlas argues
that stress testing is a different and cheaper activity than benchmarking, and
that almost nobody does it. This is one of the few places both exist in the same
repository.

The memory model is the textbook three: `atlas_memory_episodic`,
`atlas_memory_semantic`, `atlas_memory_procedural`, each its own index.
Embedding is server-side — `semantic_text` fields with an inference id, "no
client-side calls" — and retrieval is an RRF retriever fusing BM25 with the
semantic query.

Reservations, and they are the ones a demo earns. Consolidation is "a single
Claude pass" that distils episodic events into semantic facts and updates
playbooks, with no verification gate on what it produces. There is no tombstone.
And the personas are synthetic, so the eval measures retrieval over generated
material rather than over anything a person actually said.

## 2. Mental Model

```text
turn ──▶ episodic event      "what happened"   atlas_memory_episodic
              │
              │ consolidation: one model pass
              ├──▶ semantic fact  "what's true"  atlas_memory_semantic   (deduped)
              └──▶ procedural playbook "what works"  atlas_memory_procedural (updated)

recall ──▶ RRF( BM25 , semantic ) filtered by user_id
```

Three indices rather than three types in one index is the structural choice, and
it buys per-type lifecycle rules and per-type retrieval weighting at the cost of
cross-type queries needing fan-out.

Nothing here has an end state. A semantic fact that turns out wrong is
overwritten by a later consolidation or it is not; nothing records that it was
wrong.

## 3. Architecture

`backend/app/` — `elasticsearch/retriever_builder.py` (985),
`atlas/memory/operations.py` (938), `atlas/consolidate.py` (567), plus the
service and MCP layers. `backend/scripts/atlas/` holds `stress_test.py` (692)
and `eval_recall.py` (583). `backend/tests/test_retriever_builder.py` is 1,097
lines — the largest single file in the backend is a test for the retriever.

### Deployment and ergonomics

Docker Compose, an OpenTelemetry collector config, and Cloud Run Dockerfiles;
Elasticsearch is the dependency and it is not a small one. Embedding runs inside
Elasticsearch via an inference endpoint, so there is no separate embedding
service to operate — which is the argument the demo is making.

## 4. Essential Implementation Paths

### An eval that cannot fool itself

Generating questions from the document you intend to retrieve is a known
technique with a known weakness: the question inherits the document's vocabulary,
so retrieval looks better than it will in production where users use their own
words. The construction here does not hide that — it says an LLM generates "two
natural questions a user might ask whose answer is that doc", which is precisely
the caveat, stated.

Matching on `_id` removes the judge. Recall@k and MRR against a known target id
are arithmetic, so two runs give the same answer, which is more than can be said
for most LLM-judged memory scores in this atlas.

What it cannot tell you is whether the *right* memory was the one sampled. The
eval measures whether a document is findable given a question derived from it —
not whether the store contains what a user would actually need.

### A stress test beside the benchmark

`stress_test.py` at 692 lines is unusual enough to name. The atlas's position is
that benchmarking ranks systems on the normal case while stress testing finds
the input that breaks one, and that the second is cheaper and more useful. A
repository shipping both, for a demo, is doing more measurement than most
production systems reviewed here.

### Embedding inside the datastore

`semantic_text` with `inference_id: .jina-embeddings-v5-text-small`, described as
"no client-side calls". The write path does not carry an embedding step, and the
model version lives in the index mapping rather than in application config.

That has a real consequence for the migration problem the atlas lists as
under-covered: changing the embedding model is a mapping and reindex operation
handled by the datastore, not a campaign coordinated by application code. It also
means the application cannot know which model produced a given vector without
asking the index.

### Consolidation as a single pass

One model call distils episodic events into deduped semantic facts *and* updates
procedural playbooks. Doing both in one pass is efficient and couples them: a
consolidation that misreads an episode can corrupt a fact and a playbook
together, and there is no gate between the model's output and the store.

Compare [Memora](../memora/)'s dry-run default and [ctx](../ctx/)'s schema gate
on proposals. This has neither, which is defensible in a demo and would not be in
a product.

## 5. Memory Data Model

Documents in three indices, with `user_id` for persona isolation, auto-embedded
text fields, and provenance by index and source event.

Absent: trust state, tombstones, supersession chains, bi-temporal validity, and
any audit of mutations. Correction means a later consolidation writing something
different.

## 6. Retrieval Mechanics

An RRF retriever fusing BM25 with a semantic query, filtered by `user_id`. The
retriever builder is 985 lines with a 1,097-line test — the ratio suggests the
fusion logic is where the complexity actually is, which matches every other
hybrid system in this atlas.

## 7. Write Mechanics

The agent writes on every turn; consolidation runs on demand from the inspector
UI. Embedding is server-side.

### Operational cost

Writes cost no client-side embedding call. Consolidation is one model pass per
run rather than per memory, which bounds it. Retrieval is Elasticsearch,
so latency is the cluster's rather than a provider's.

The recurring cost is Elasticsearch itself — three indices with dense vectors per
user — and no footprint figures were found.

## 8. Agent Integration

A backend service plus an MCP server so "Claude Code, Claude Desktop, Cursor, or
any other MCP client can plug straight in", with an inspector UI for triggering
consolidation and viewing what the agent stored.

## 9. Reliability, Safety, and Trust

Strengths:

- **A committed recall eval** computing Recall@1/5/10 and MRR, matched on
  document id so no judge is involved.
- **A stress test** in the same repository.
- **A test file larger than the module it tests**, for the retriever.
- **Server-side embedding**, keeping model identity in the index mapping.
- **Per-persona isolation** applied on recall.
- **An inspector** that makes what the agent stored visible.

Gaps:

- **A demo by its own description**, with synthetic personas — the eval measures
  retrieval over generated material.
- **No trust state, tombstone, supersession or audit.**
- **Consolidation is one ungated model pass** producing both facts and playbooks.
- **Question-from-document eval** inherits document vocabulary, which flatters
  retrieval relative to real queries.

## 10. Tests, Evals, and Benchmarks

`eval_recall.py`, `stress_test.py`, and a substantial backend test suite.
Nothing was run for this review, and no committed scored results were located —
so this sits in the familiar category of a reproducible harness without a
reproduced run, though the harness is more legible than most.

## 11. For Your Own Build

### Steal

- **Match your retrieval eval on document id, not on text.** It removes the judge
  and makes the number reproducible, which is worth more than a more realistic
  scoring rubric that nobody can rerun.
- **State how the questions were generated.** Question-from-document is fine if
  the write-up says so; the failure is presenting it as though users wrote the
  queries.
- **Ship the stress test next to the benchmark.** Finding the input that breaks
  the system is cheaper than ranking it, and one repository doing both is rare
  enough to copy.
- **Push embedding into the datastore** where it can go — the model version lives
  with the data, and re-embedding becomes a reindex rather than a campaign.

### Avoid

- **One model pass producing two derived stores.** Efficient, and it couples the
  failure: a misread episode corrupts a fact and a playbook together.
- **Consolidation with no gate**, in anything that is not a demo.

### Fit

Right as a reference for what an evaluated memory layer looks like when it is
built on a search engine you already run, and as the clearest small example of
the three-index episodic/semantic/procedural split. Wrong as a starting point for
a production memory layer: it is explicit that it is a demo, and the things a
product needs — correction, trust, an audit trail — are exactly what is absent.
Read the eval scripts first; they are the most transferable part.

## 12. Open Questions

- What are the measured Recall@k and MRR figures, and against which retriever
  configuration? The harness is committed; results were not found.
- How much does question-from-document inflate recall relative to
  human-written queries?
- What stops a consolidated semantic fact being wrong and staying wrong?
- Does per-index lifecycle differ in practice, or are the three indices currently
  a structural choice without behavioural consequence?

## Appendix: File Index

- Memory operations: `backend/app/atlas/memory/operations.py`.
- Consolidation: `backend/app/atlas/consolidate.py`.
- Retrieval: `backend/app/elasticsearch/retriever_builder.py`, tested by
  `backend/tests/test_retriever_builder.py`.
- Evaluation: `backend/scripts/atlas/eval_recall.py`,
  `backend/scripts/atlas/stress_test.py`.
- Model and index description: `ATLAS.md`.

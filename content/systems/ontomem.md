---
title: "OntoMem"
eyebrow: "A destructive merge can only be undone by keeping what went into it"
description: "A Python memory that merges extractions into one record per composite key, with a source ledger of pre-merge inputs so removing a document re-merges the survivors rather than leaving residue."
root: ../..
page_kind: system
source_name: "yifanfeng97/ontomem"
source_url: https://github.com/yifanfeng97/ontomem
archive_name: "yifanfeng97--ontomem"
revision: 154bf488ebffc9d4e99df62f6b416195bbbb23f1
revision_url: https://github.com/yifanfeng97/ontomem/commit/154bf488ebffc9d4e99df62f6b416195bbbb23f1
analyzed_at: 2026-09-16
capabilities: ""
stack_storage: "files"
stack_retrieval: "vector"
stack_source: "reviewed"
matrix:
  memory_unit: "One merged record per composite key, shaped by a caller-supplied Pydantic schema, with the raw pre-merge extractions of each contributing document kept beside it when the ledger is on"
  storage: "Files: the merged store, a FAISS index with an `index.meta.json` companion, and an optional source ledger holding the current version of each source's raw results"
  retrieval: "Vector search over the merged records, with O(1) secondary lookups by custom key and an optional restriction to named source ids or tags"
  write: "`add(items, source_id=...)` extracts and merges into the existing record for a key, through either a deterministic merger or an LLM one"
  update_delete: "`remove_source()` re-merges the surviving sources for every affected key; `upsert_source()` replaces a document in one step; `edit()` removes one wrong fact from a record with key-invariance validation and a dry run"
  scoping: "None enforced — `source_ids` and `tags` are optional search filters the caller supplies, with union semantics across a key's contributing sources"
  integration: "A Python library, published to PyPI, with a documentation site; no server and no agent protocol surface"
  background: "None; consolidation happens on the write that triggers it"
  trust: "Provenance through the source ledger, an embedder signature that refuses vectors from a different embedding space, and key-invariance validation on a semantic edit"
  strengths: "The source ledger earns its overhead by naming the problem it exists for: \"because merges are destructive, the only way to remove a source's contributions precisely is to re-merge the surviving sources' raw results for the affected keys.\" That sentence is the whole design. Most stores that consolidate on write cannot answer what a particular document contributed, and so cannot take it back — they can only delete every key it touched. OntoMem keeps each source's raw pre-merge extraction, which lets `remove_source(strategy=\"exact\")` recompute the affected keys from the survivors and delete only those nothing else contributed to. The coarse alternative is kept and named rather than hidden: `strategy=\"touched\"` deletes every key the source touched, which is what a system without the ledger is forced to do. The overhead is stated as a number (\"~1.5-2x storage\") and bounded on purpose, since only the current version per source is retained. Two smaller pieces are worth taking: the FAISS index records an embedder signature in an `index.meta.json` companion and refuses vectors from a different embedding space, which turns a silent similarity-nonsense bug into a load-time refusal; and `edit()` validates key-invariance before applying a semantic edit, so removing a wrong fact cannot quietly move the record to a different key"
  risks: "Nothing here carries epistemic state. A merged record has no status, no validity interval, no recorded-at, no confidence and no supersession link, so a claim that stopped being true and one nobody has checked are indistinguishable from one that was verified this morning — the merge produces a single current value per key and the history of how it got there lives only in the ledger's current-version-per-source snapshot, which is not an append-only record of what changed. Scoping is a caller-supplied search filter (`source_ids`, `tags`) with union semantics, so a key contributed to by several documents matches when any one of them fits; there is no stored key applied on the caller's behalf, and nothing separates one tenant's records from another's. Deletion has no memory: `remove_source` reverses a document's contribution and leaves nothing keyed on what was removed, so re-adding the same document restores the same claims with no sign the store was once asked to drop them. And the surface is a library — 5,774 lines across 36 files, no server, no agent protocol — so everything above is the caller's to wire"
---

## 1. Executive Summary

OntoMem is "The Self-Consolidating Memory" — Apache-2.0, Python, version 0.6.0,
5,774 lines across 36 files, published to PyPI. Its pitch is a contrast: "[g]ive
your AI agent a 'coherent' memory, not just 'fragmented' retrieval." Rather than
appending extractions and ranking them later, it merges each new extraction into
the existing record for a composite key — `user_id + date`, say — so what the
store holds is one consolidated object per key rather than a pile of
observations about it.

**That design creates a problem, and the interesting part of this repository is
its answer.** A destructive merge cannot be undone from the merged result: once
three documents have been folded into one record, nothing in that record says
which of them contributed what, so removing one document means deleting
everything it touched. The source ledger exists for exactly that, and says so:

> "because merges are destructive, the only way to remove a source's
> contributions precisely is to re-merge the surviving sources' raw results for
> the affected keys."

With `track_sources=True`, each document's raw pre-merge extraction is kept, and
`remove_source(strategy="exact")` recomputes every affected key from the
survivors while deleting only the keys nothing else contributed to. The coarse
strategy is kept and named rather than quietly avoided —
`strategy="touched"` deletes every key the source touched, which is what a store
without a ledger has to do. The cost is stated as a number, "~1.5-2x storage
overhead", and bounded deliberately: only the current version per source is
retained.

**Two smaller mechanisms are worth lifting.** The FAISS index writes an
`index.meta.json` companion recording the embedder signature and refuses vectors
from a different embedding space, which converts a silent
similarity-is-nonsense failure into a refusal at load. And `edit()` — removing
one wrong fact from a record without rewriting the rest — validates
key-invariance and offers a dry run, so a semantic edit cannot quietly move the
record to a different key.

**What is absent is epistemic state.** A merged record carries no status, no
validity interval, no recorded-at, no confidence and no supersession link. The
store answers with the current merged value for a key and has no vocabulary for
a claim that has stopped being true, one nobody has checked, or one a person
corrected. That is a coherent choice for the consolidation problem it is solving
and it is the reason this report carries no capability marks.

## 2. Mental Model

A **key** is the unit, and the record under it is always current.

A **merge** is destructive, which is why the inputs are kept.

A **rollback** is a re-merge of whoever is left.

An **index** refuses vectors that came from a different embedder.

```mermaid
%% caption: extractions from several documents merge destructively into one record per composite key, and the source ledger keeps each document's raw pre-merge results so removing one re-merges the survivors rather than deleting every key it touched
flowchart TB
    D1["document A"] --> EX["extraction into a caller-supplied<br/>Pydantic schema"]
    D2["document B"] --> EX
    D3["document C"] --> EX
    EX --> LEDGER[("source ledger, when track_sources=True —<br/>each source's RAW pre-merge results,<br/>current version only, ~1.5-2x storage")]
    EX --> MERGE{"merge into the record for<br/>composite key user_id + date"}
    MERGE --> STORE[("one merged record per key —<br/>no status, no validity, no confidence,<br/>no supersession link")]
    STORE --> IDX[("FAISS index + index.meta.json<br/>recording the embedder signature")]
    IDX -.->|"a vector from a different embedding space<br/>is refused at load rather than silently<br/>producing nonsense similarity"| SAFE["a silent failure made loud"]
    IDX --> SEARCH["vector search, plus O(1) secondary lookups;<br/>optional source_ids and tags filters,<br/>union semantics across contributors"]
    SEARCH -.->|"the filters are the caller's, supplied per query —<br/>no stored key is applied on the caller's behalf"| NOSCOPE["no scope-enforced mark"]
    RM["remove_source(source_id)"] --> STRAT{"strategy"}
    STRAT -->|"exact (default)"| EXACT["re-merge the affected keys from the<br/>SURVIVING sources' raw results;<br/>delete only keys nobody else contributed to"]
    STRAT -->|"touched"| COARSE["delete every key the source touched —<br/>what a store without the ledger must do"]
    LEDGER --> EXACT
    EXACT -.->|"'because merges are destructive, the only way to<br/>remove a source's contributions precisely is to<br/>re-merge the surviving sources' raw results'"| WHY["the ledger's whole reason"]
    EXACT --> STORE
    RM -.->|"nothing is keyed on what was removed, so re-adding<br/>the same document restores the same claims<br/>with no record that it was ever dropped"| NOTOMB["no tombstone mark"]
    EDIT["edit(): remove one wrong fact,<br/>keep the rest"] -.->|"key-invariance validated, dry run available,<br/>vector refreshed in place"| STORE
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `ontomem/core/omem.py` | The store: add, merge, search, index maintenance, rollback |
| `ontomem/core/sources.py` | The ledger entry, and the argument for keeping it |
| `ontomem/merger/classic_merger` | Deterministic merging |
| `ontomem/merger/llm_merger` | Model-assisted merging and semantic editing |
| `tests/` | Unit, integration and fixture suites over the merge and rollback paths |

## 4. Essential Implementation Paths

`ontomem/core/sources.py:1-9` — why a consolidating store has to keep its
inputs.

`ontomem/core/omem.py:936-948` — the two rollback strategies, and what each
costs.

`ontomem/core/omem.py:1264`, `:1282-1299`, `:1354-1355` — the embedder signature
written and checked.

## 5. Memory Data Model

One merged record per composite key, shaped by a Pydantic model the caller
defines, with secondary lookups mapping custom keys to primary keys by
reference rather than by copying data. When the ledger is on, each contributing
document's raw extraction sits beside the merged result, one current version per
source.

## 6. Retrieval Mechanics

Vector search over the merged records with FAISS, O(1) secondary lookups for
queries by a non-primary attribute, and an optional restriction to named source
ids or tags — matching a key when any of its contributing sources fits the
filter, which is the right semantics for attribution and the wrong one for
isolation.

## 7. Write Mechanics

`add(items, source_id=...)` extracts and merges. `sync_index()` patches the
vector index in place rather than rebuilding it, `suspended_index()` batches
mutations without dropping it, and `upsert_source()` replaces a document in one
step. Merging is either deterministic or LLM-assisted, chosen by the caller.

## 8. Agent Integration

None beyond the library: no server, no MCP surface, no hooks. It is a component
for a pipeline that already knows when to write.

## 9. Reliability, Safety, and Trust

The strong parts are the ledger, the embedder signature check, and the
key-invariance validation on a semantic edit. The absent part is any notion of a
claim's standing — the store holds the current merged value and has no way to
say that a value is suspect, expired, or corrected rather than simply replaced.

## 10. Tests, Evals, and Benchmarks

Unit, integration and fixture suites run in CI, covering merging, index
maintenance and the rollback strategies. There are no committed cases asserting
that particular material must not be retrieved, which follows from there being
no read path that withholds.

## 11. For Your Own Build

If your write path merges, keep the inputs. The moment you consolidate, you have
given up the ability to remove one contributor unless you stored what each one
contributed — and the day you need that is the day somebody asks you to delete a
document.

Name the coarse fallback and ship it beside the precise one. `strategy="touched"`
is what everyone else does by necessity; having both makes the cost of the
precise path visible.

Write your embedder's signature next to your index. A vector store silently
mixing two embedding spaces returns plausible nonsense, and a signature turns
that into a refusal.

## 12. Open Questions

Whether a status field is wanted on a merged record. The consolidation model
assumes the newest extraction is the best one, which holds for daily snapshots
and does not hold for a fact somebody later disputes.

Whether the ledger should become append-only. Keeping one current version per
source bounds the overhead and is what makes rollback exact; it also means the
store cannot say what a key looked like before the last merge, which is a
question the same users will eventually ask.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `ontomem/core/sources.py:1-9` | The clearest statement of why a merging store needs a ledger |
| `ontomem/core/omem.py:936-948` | Exact rollback beside the coarse one it replaces |
| `ontomem/core/omem.py:1282-1299` | An embedder signature that makes a silent failure loud |

## History

**2026-09-16** — [`154bf488ebffc9d4e99df62f6b416195bbbb23f1`](https://github.com/yifanfeng97/ontomem/commit/154bf488ebffc9d4e99df62f6b416195bbbb23f1) — first reading, at a commit dated 4 September 2026. Screened before opening, from a shallow clone: four files scanned, no auto-run surfaces, one build-time execution point, no unpinned surfaces and nothing inside the seven-day cooldown, with `uv.lock` present. Nothing was installed, built or run, and no embedding model was loaded.

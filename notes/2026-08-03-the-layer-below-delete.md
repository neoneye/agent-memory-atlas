# The layer below delete

**Status:** one finding, verified in four storage engines at pinned commits; the
rest of the review is four already-closed decisions arriving again
**Origin:** a Gemini review submitted 2026-08-03, structured as two sections of
critique and one section of proposals. Checked against the 133 reports in
`content/systems/` and against the notes directory.

Recorded because the review's own ranking is inverted. Its four numbered
"next level" proposals are the part it argues hardest for, and all four are
decided — three declined in writing, one already shipped. Its unnumbered
critique section contains one item that is worth the whole review, and it is
stated in a form that turns out to be **wrong in its specifics and right about
the gap**. Establishing which half is which required reading four vector
engines, so that reading is the body of this note.

## The proposals, against the record

| # | Proposal | Status before this review |
| --- | --- | --- |
| 1 | Dockerized dynamic testbed, "the CI/CD gate for memory systems" | Decided 2026-07-28. [executable-eval-suite](2026-07-28-executable-eval-suite.md) keeps the harness and rejects the framing: the harness is a day, standing up each system under test is per-system and unbounded, and the publishable artifact is a tested subset plus an exclusion list with per-system blockers |
| 2 | Black-box test the proprietary systems | Declined four times; the current reasoning is the ["API-contract only" tier](2026-07-28-declined-proposals.md), which answers this exact version — an API surface cannot show the failure the tombstone column exists to catch, and a documentation page has no revision to pin |
| 3 | Interactive sortable leaderboard, filter by "Has Tombstone" | **Already shipped.** [capabilities.md](../content/capabilities.md) filters all seven marks with **and** semantics, generated from report frontmatter so it cannot drift |
| 4 | Maturity-level badge for READMEs | Declined twice by name, in [executable-eval-suite](2026-07-28-executable-eval-suite.md) and [declined-proposals](2026-07-28-declined-proposals.md), with the predictable failure spelled out: someone adds an `is_rejected` boolean, claims the mark, and a strict definition becomes a thing to argue about rather than check |

Item 1 is worth one more sentence, because the review reaches it from a premise
the atlas shares. It is right that static review cannot see runtime behaviour.
It concludes that the answer is to run everything. The answer already on record
is to run what runs and publish what did not, which costs a bounded amount and
survives this project's own standards; running everything costs an unbounded
amount and produces a sparse Pass/Fail column that reads as a comparison.

Item 3 is the one worth noticing as a signal rather than a correction. A
careful reader spent enough time on this site to write two sections of accurate
criticism and did not find a page that exists, is linked from the homepage, and
does precisely what they asked for. That is a navigability finding — which is
the review's own item E, arrived at by demonstration rather than by assertion.

## The finding: deletion durability is gated by a layer nobody here has read

The review's item B, in its words: vector databases use soft deletes, so a
memory system can issue a correct delete and the store "might still leak that
memory during a k-NN search until a manual garbage-collection/compaction event
occurs."

That claim contains three distinct sub-claims. **One is wrong, two are right,**
and the atlas's `update_delete` column is exposed to the two that are right.

Four engines were cloned and read for this note. The corpus depends on them
more than on anything else in the storage layer — pgvector is named in 16
reports, Redis in 22, Chroma and Qdrant in 11 each, LanceDB in 6.

| Engine | Commit |
| --- | --- |
| `pgvector/pgvector` | `4f3d17f6f74fe98adf54df4d016de241eeaae9af` |
| `chroma-core/chroma` | `19e1bf8a8610ab2b660a75e90a2f9e487ffe638c` |
| `chroma-core/hnswlib` | `6868102bde454dc761136e1994490133a6a026bb` |
| `qdrant/qdrant` | `db8fa43fcb6aedec1e739487e17a99731b74590a` |
| `lancedb/lancedb` | `9e26bf3fba7b77bb32434c0f6af9dcb43248f90a` |

### Sub-claim 1 — the deleted vector is returned by search. False, in all four.

Every one of the four filters deleted entries out of results, by a different
mechanism, and the filter is not optional:

- **pgvector** returns a heap TID from the index scan (`src/hnswscan.c:323`) and
  lets Postgres apply ordinary MVCC visibility to the heap tuple. The scan
  refuses to run at all without an MVCC snapshot (`src/hnswscan.c:218`), so
  there is no configuration in which a deleted row is returned.
- **Chroma** delegates to its hnswlib fork, whose candidate acceptance is
  guarded on `isMarkedDeleted` in both search paths
  (`hnswlib/hnswalg.h:546`, `:614`).
- **Qdrant** carries a deleted bitslice per vector storage
  (`lib/segment/src/vector_storage/vector_storage_base.rs:118`, `:140`) and
  excludes it when building (`iter_internal_excluding(deleted_bitslice)`).
- **LanceDB** never mutates: a delete produces a new dataset version that does
  not contain the row.

**So the leak the review describes does not happen**, and a report that says
"exact delete" is not wrong about what a subsequent query returns. This matters
because it is the sub-claim that would have invalidated existing marks, and it
does not.

### Sub-claim 2 — deletes degrade the index. True, and Chroma says so in a comment.

The cost of a soft delete is not that the deleted vector comes back. It is that
the graph keeps routing through a node that can never be returned, so recall of
the **surviving** memories drops.

Chroma handles this in the read path, and the code states the problem plainly
(`rust/segment/src/local_hnsw.rs:315`):

```rust
let delete_percentage = (len_with_deleted - actual_len) as f32 / len_with_deleted as f32;

// If the index is small and the delete percentage is high, its quite likely that the index is
// degraded, so we brute force the search
if delete_percentage > 0.2 && actual_len < 100 {
```

Read the condition rather than the comment. The escape hatch is `< 100` live
elements. **Above a hundred surviving memories, a heavily-deleted Chroma
collection degrades and nothing in the read path compensates.** A memory system
that corrects aggressively — which is the behaviour this atlas argues for — is
the workload that hits this.

The other two repair, but only during a rebuild. Qdrant has a
`GraphLayersHealer` that re-links neighbours around removed points, invoked
from index construction (`lib/segment/src/index/hnsw_index/hnsw/build.rs:294`),
not from the delete. pgvector repairs neighbour links in `VACUUM`
(`src/hnswvacuum.c`). In both cases the interval between the delete and the
repair is set by a background process the memory system does not control and,
in every report here, does not mention.

### Sub-claim 3 — the bytes persist. True, and one engine says it in its own docs.

This is the sub-claim that reaches the atlas's central column, because
"forgotten" and "not returned by search" are different properties and the
corpus has been reporting the second.

- **Chroma / hnswlib** is the starkest. The function comment is the finding:

  > Marks an element with the given label deleted, does NOT really change the
  > current graph.

  `markDeletedInternal` sets one bit in the level-0 link-list header
  (`hnswalg.h:1572`). `saveIndex` then writes `data_level0_memory_` for all
  `cur_element_count` elements (`hnswalg.h:911`) — **the deleted embedding is
  persisted to the index file verbatim**, and `loadDeleted` re-counts the marks
  on the way back in. `unmarkDelete` (`hnswalg.h:1598`) restores it. The only
  thing that overwrites the vector is a later `addPoint` reusing the slot, and
  only when `allow_replace_deleted_` is set.
- **LanceDB** states it in the doc comment on `OptimizeAction::Prune`
  (`rust/lancedb/src/table/optimize.rs`): every change is additive, and "the old
  version, which does contain the removed data, is left in place." Time travel
  is the feature; retention of deleted content is the consequence. The default
  guard keeps files newer than **seven days**, and overriding it needs
  `delete_unverified`, whose own comment warns it can corrupt the dataset.
- **Qdrant** holds the vector until a segment optimizer rebuilds the segment.
- **pgvector is the exception, and it is worth naming because it shows the
  others could have.** `VACUUM` does not merely flag the element; it zeroes it:

  ```c
  etup->deleted = 1;
  memset(&etup->data, 0, VARSIZE_ANY(&etup->data));
  ```

  (`src/hnswvacuum.c`, `MarkDeleted`.) The embedding is destroyed, the neighbour
  pointers are invalidated, and the page is offered for reuse. It is still not
  synchronous with the `DELETE` — but it terminates, which is more than the
  other three guarantee.

### What this does to the corpus

The `update_delete` column reports what the memory system's own code does, and
stops at the store boundary. That is defensible as a description of the system
and misleading as an answer to "is it gone".

The reports most exposed are the ones whose wording is strongest:

| Report | Store | `update_delete` says |
| --- | --- | --- |
| [claude-mem](../content/systems/claude-mem.md) | SQLite canonical, Chroma projection | "Exact row deletion with synchronized tombstones" |
| [cognee](../content/systems/cognee.md) | Chroma, Qdrant | "Exact data/dataset/all forget; memory-only reprocessing; provenance rollback" |
| [crewai](../content/systems/crewai.md) | LanceDB default | "`forget()` deletes by scope, category, age, metadata filter or explicit ids" |
| [openclaw](../content/systems/openclaw.md) | LanceDB | "Exact scoped delete" |
| [mem0sharp](../content/systems/mem0sharp.md) | Qdrant | "Delete by id and delete by scope predicate" |
| [a-mem](../content/systems/a-mem.md) | Chroma | "exact delete without incoming-link cleanup" |
| [hipporag](../content/systems/hipporag.md) | Chroma, Qdrant | "Chunk-scoped delete" |

None of these marks is *wrong* under sub-claim 1. All of them are silent about
sub-claims 2 and 3.

**The method already knows how to do this, twice, at the application layer.**
[membase](../content/systems/membase.md) is recorded as deleting "by
`memory_index` from SQLite only; the Chroma document and the uploaded hub blob
both survive." [voyager](../content/systems/voyager.md) is recorded as
"same-name rewrite; old versions on disk but unreachable." Both are exactly this
reasoning — follow the delete down one layer and report what survives — applied
one layer higher than the engine.

**And the benchmarks page already anticipated it.** Step 9 of the deletion
sequence in [benchmarks.md](../content/benchmarks.md) §6 asserts the value is
"absent from derived artifacts too — summaries, profiles, graph edges,
**embeddings**, caches, exports, backups". The spec named the embedding. No
review has checked it, because checking it means leaving the repository under
review.

### What to do about it, in order of cost

1. **Cheapest and most honest: a caveat, once, where the column is defined.**
   The [rubric](../content/methodology/atlas-rubric.md) and the `update_delete`
   description should state that deletion is assessed at the system's own
   boundary, that the embedding index is a layer below it, and that on three of
   the four common engines the vector survives the delete until an
   unscheduled background pass. This costs an afternoon and removes the
   overclaim.
2. **A storage-engine section in the overview.** Four engines, the three
   sub-claims, the table above. It is a claim about shared dependencies rather
   than about any one system, which is a genuinely new kind of row for this
   corpus and needs its own home rather than 40 duplicated paragraphs.
3. **Per-report notes only where the wording is strongest** — the seven rows
   above, not all 133. A report that says "no tombstones, and auto-capture can
   restore content" is already telling the reader the deletion is weak; a report
   that says "exact row deletion with synchronized tombstones" is not.

None of this needs the testbed. It is static code review of a layer the method
already reads, applied one level down.

## The rest of the critique section

**A — map the patterns onto distributed-systems theory.** Half already done, and
the review appears not to have reached it. The
[rejected-value tombstone](../content/patterns/rejected-value-tombstone.md) page
opens with a three-row table separating Cassandra-style tombstones (keyed on a
row, until compaction, to propagate a delete) from soft deletes (keyed on a row,
to hide it) from the atlas's pattern (keyed on the normalised **value**, to
refuse a re-assertion). The review's argument — that this is "just standard
distributed database theory" — is answered on the page it is criticising, and
the answer is that the key is different, which is the whole pattern.

What is genuinely absent is the *other* half of the review's list: **event
sourcing and CQRS**. Neither term appears anywhere in `content/`. That is the
same shape of gap as
[symbolic-prior-art](2026-07-28-symbolic-prior-art.md) — a mature lineage that
solved a version of this and is missing from the atlas's stated ancestry — and
it should be triaged the same way, which is by deciding whether it is an
omission or a real discontinuity, not by asserting either.

**C — concurrency.** Under-covered and correctly identified. Race conditions,
write-write conflicts and locking appear in three system reports
([rainbox](../content/systems/rainbox.md),
[letta](../content/systems/letta.md), [honcho](../content/systems/honcho.md)),
one pattern page and the report format. The review's specific question —
two agents extracting contradictory beliefs simultaneously — has at least one
occupant already recorded
([mastra-observational-memory](../content/systems/mastra-observational-memory.md)
carries "distributed locking and progressive summary drift" as a risk). Worth a
survey pass. Not urgent, because unlike item B it does not affect a published
mark.

**D — cache-preserving context injection as a pattern.** The best of the four
critique items after B, and the cheapest, because the evidence is already
written and scattered. Prefix-cache invalidation is discussed in 13 files
including [overview.md](../content/overview.md),
[benchmarks.md](../content/benchmarks.md), the
[patterns index](../content/patterns/index.md), and eight system reports. There
is no page. Promoting it needs a survey of who injects where — top of prompt,
per-turn suffix, tool result — which the reports already contain.

**E — navigability.** Corroborated by the review's own item 3, as above. No
proposal here; recording that the second reviewer in four days has asked for
something the site already has.

## What came of it

- **One published claim weakened**, pending the caveat: `update_delete` and the
  deletion discussion describe the system's boundary and not the engine's.
- **Four engines read at pinned commits**, and the review's own version of the
  finding refuted in its specifics — no leak on any of the four.
- **One new lineage gap** (event sourcing / CQRS), open, to be triaged the way
  the symbolic prior art was.
- **Two backlog items with the evidence already in the corpus** — the
  cache-preserving injection pattern, and a concurrency survey.
- **No proposal adopted.** All four were decided before the review arrived, and
  nothing in it changes a reason.

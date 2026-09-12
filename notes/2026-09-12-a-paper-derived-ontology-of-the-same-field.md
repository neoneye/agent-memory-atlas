# A paper-derived ontology of the same field, and what it does not name

**Status:** done. No change to the taxonomy is proposed here. One concrete gap in
the stack census is named at the end and left for a separate decision.
**Method:** read [`Haiyoung/AgentMemoryAtlas`](https://github.com/Haiyoung/AgentMemoryAtlas)
at [`e01deb2949022e7ae4de28d5dc80980451705cda`](https://github.com/Haiyoung/AgentMemoryAtlas/commit/e01deb2949022e7ae4de28d5dc80980451705cda),
a separate project that shares this one's name and is not a fork. Its
`ontology/lexicon.json` was queried directly; this atlas's side was counted from
report frontmatter on 12 September 2026, at 439 reports. Both numbers are dated
measurements, not live counts — `check_claim_counts.py` scans `content/` and does
not reach this directory, so nothing here is build-checked and nothing here
should be quoted as current.

## The question

That project distils 148 agent-memory papers (2021–2026) into a domain ontology:
a three-axis orthogonal classification — 4 carriers, 7 functions, 6 lifecycle
dynamics — over 8 top-level classes and 5 axiom families, published as
`lexicon.json` with 1,411 concepts and 744 relations, both counts recomputing
exactly from the file. It is a map of the same field this atlas maps, built from
the opposite material: papers rather than code at pinned commits.

So it is worth asking what a reading of the literature names that a reading of
implementations does not, and the reverse.

## What each taxonomy is for

They are not competing versions of one thing. The axes answer *what kind of
memory is this*: a concept gets a coordinate in carrier × function × dynamic, and
the model's stated principle is orthogonality — "载体变化不改变功能" (a change of
carrier does not change the function). This atlas's eight families answer a
different question, *what does it cost to run and who calls it* — embeddable
library, hosted service, agent runtime, host plugin, local coding-agent, graph
and temporal, verification-first, research lineage. That is a deployment
clustering, and it exists because the corpus is repositories a reader might adopt.

The genuinely comparable layer is theirs-versus-ours on *mechanism*: their axiom
families and our seven marks both claim to say what a memory system must have.

## The measurement

Seven probes against all 1,411 concept names, each probe covering the English and
Chinese vocabulary for one mark, with the axiom text and the 744 relation
descriptions searched separately as a fallback:

| Mark | Named in their 1,411 concepts | This corpus, 12 Sep 2026 |
| --- | --- | --- |
| Rejected-value tombstone | **0** | 39 of 439 |
| Discrete trust state | 2 — `Candidate Memory`, `Verified Skill Library` | 98 of 439 |
| Bi-temporal validity | 1 — `Bi-temporal Memory` | 69 of 439 |
| Scope enforced in retrieval | 1 — `敏感信息分级访问控制` | 227 of 439 |
| Append-only mutation audit | **0** (`人工干预` appears only in axiom prose) | 148 of 439 |
| Human review surface | **0** (same) | 131 of 439 |
| Negative retrieval assertion | **0** (`leakage` only in relation prose) | 185 of 439 |

The two columns do not measure the same thing and the table is not a scoreboard.
The right reading is narrow: **the correction-and-governance half of memory has
almost no vocabulary in this literature map, while it is ordinary in shipped
code.** Scope enforcement is the sharpest case — a mechanism 227 of 439
implementations here carry, and one concept out of 1,411 in a distillation of 148
papers.

Three ways that could be wrong, in order of how much they would cost the claim:

1. **It measures naming, not presence.** A paper can scope its retrieval without
   the ontology extracting "scope" as a concept, and extraction here is a model's
   work over a brief, not a code read. The finding is about the field's published
   vocabulary.
2. **The corpus is opportunistic.** 439 repositories chosen by this project's own
   intake are not a sample of anything, a point the rubric already makes about its
   own counts.
3. **Selection differs at the source.** Papers report novelty; repositories report
   what someone had to build to ship. An audit log is not a contribution, so it
   would not be in a paper's abstract even where the paper's system has one.

The third is the interesting one, and it is also the atlas's own thesis stated
from the outside: the gap between what a system *claims* and what its code
*does* is where the findings are. A literature map inherits the claims.

## Where their axis is better than ours

Their carrier dimension has four values and one of them this atlas cannot record
at all. `STORAGE_VOCAB` in `scripts/extract_stack.py` holds nineteen values —
sqlite, postgres, files, graph, seven vector stores, kv, delegated — and every
one of them is an external or in-process store. There is no parametric value, and
no report carries one.

That is not the same as having missed the idea. [second-me](../content/systems/second-me.md)
reads a parametric path directly and says the useful thing about it:

> The parametric one is not retrieval at all. After training, the model answers
> from its weights. There is no top-*k*, no threshold, no citation, and no way to
> ask what the model is drawing on — which is the property that makes parametric
> memory attractive […] and the property that makes it unauditable.

Its census row is `stack_storage: "sqlite, chroma"`, `stack_retrieval: "vector"`.
[MemOS](../content/systems/memos.md) mounts a parametric cube beside textual and
activation memory and is recorded as `delegated`. So the prose has the finding and
the structured census silently describes only the half with a store — which means
a reader filtering the stack census for how these systems hold memory is given an
answer that is accurate about the database and quiet about the weights.

**The proposal is not to add a `parametric` storage value.** The census is a
census of stores, and a weight is not a store in the sense the rest of the
vocabulary uses — nothing is written to it at recall time and nothing is read out
of it by key. What would actually help is smaller: when a report analyses a
memory path whose carrier is weights, the report should say so where a reader
filtering can see it, and the census should not be the only structured place that
answers "where does this live". That is a rubric question, not a vocabulary edit,
and it belongs in a separate decision with its own diff.

## What this project should take, and not take

**Take the evidence/model separation as confirmation.** Their maintenance command
forbids editing anything under `paper/` or the per-paper ontology extractions —
"这些是证据源，不可变" — backs up the model and the lexicon before each pass, and
regenerates the derived artifacts with a changelog. That is the same discipline
this atlas enforces between reports and the generated matrix, arrived at
independently by a project working from papers. Two projects converging on
"evidence immutable, model derived" is weak evidence that the shape is right.

**Do not take the graph.** Of their 744 relations, 433 have *both* endpoints
outside the concept set, 471 have an unresolvable source after normalising case
and stripping the Chinese gloss, and 92% of concepts carry an empty
`relatedConcepts`. Nothing consumes any of it: stripping the embedded data blob
out of `site/index.html` leaves code that references `concepts`, `weight` and
`sourcePapers`, and never `relations`, `relatedConcepts`, `axioms` or
`relationCount`. The working product is a frequency-weighted concept cloud over
briefs, which is a useful thing; the ontology graph beside it is declared and
unread, the same shape this atlas reports in code and here found in data.

**Their briefs are worth a spot-check, not a citation.** One overlaps with work
done here: their brief for MAGMA ([arXiv:2601.03236](https://arxiv.org/abs/2601.03236)),
the paper [Mnemon](../content/systems/mnemon.md) implements, gets the title,
the four graphs, both benchmarks and all four authors right — including the
authorship that Mnemon's own README gets wrong. Against that, 18 of their 148
briefs state a publication year contradicting their own arXiv id, while directory
placement is correct in all 148: the derived field holds and the hand-written
restatement drifts, which is the failure `check_archive_names.py` exists for here.
And the repository has not been touched in 153 days, with 2026 stopping at five
papers against 100 for 2025.

## Why there is no report

It is not a memory system: nothing is stored at runtime, nothing is retrieved by
an agent, and there is no implementation to pin. It is the adjacent genre — a map
of the literature rather than of the code — and the inclusion test is not close.
It is recorded here rather than as an examined-and-excluded bullet because what
is worth keeping is the comparison, not the exclusion.

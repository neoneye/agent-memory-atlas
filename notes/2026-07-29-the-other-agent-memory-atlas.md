# The other Agent Memory Atlas

**Status:** external corpus examined; no atlas content changed
**Origin:** [SynapseGrid-Labs/agent-memory-atlas](https://github.com/SynapseGrid-Labs/agent-memory-atlas),
a different project with the same name, at
`3c6c9b4938d972c9789dfc0979dda412558ce1f9` (12 May 2026). Examined 2026-07-29.

First, the practical fact: **there is another public project called "Agent Memory
Atlas".** It is MIT-licensed, by Trent at SynapseGrid Labs, and it is not a fork of
this one — different content, different method, different shape. Anyone searching
the name will find both. Worth knowing before someone else points it out.

## What it is

A curated **source dataset** rather than a set of reviews: 122 records in
`data/sources.jsonl`, mirrored to CSV, with `indexes/` for claims, sources and
tags, JSON schemas under `schemas/poc0/`, and a documented taxonomy of eight axes.
Its stated audience includes agents as well as people — stable ids, tags,
confidence scores and provenance fields, so a retrieval pipeline can consume it.

The two projects are close to orthogonal, which makes it a useful comparison
rather than a competitor:

| | This atlas | SynapseGrid's |
| --- | --- | --- |
| Unit | One repository, read at a pinned commit | One source record: paper, repo, essay, registry |
| Corpus | 73 systems, all code | 122 sources — 66 papers, 39 code, 7 docs, 4 essays, 3 events, 3 registries |
| Claim | What the code does | What the source is and why it matters |
| Output | Prose reports for people | JSONL/CSV/indexes for people *and* agents |
| Scope of "memory system" | Survives the session with a correctable identity | Anything in the memory conversation, including vector databases and agent frameworks |

**Of its 42 GitHub-sourced records, seven are systems this atlas has reviewed** —
mem0, Graphiti, Letta, Cognee, Hindsight, LangMem, LlamaIndex. The other 35 are
mostly things this atlas deliberately excludes (pgvector, Qdrant, Neo4j, Weaviate,
Milvus, Redis, LanceDB, FalkorDB as infrastructure; LangGraph, CrewAI, AutoGen,
Pydantic AI, OpenAI Agents SDK as frameworks) or things it has not read.

The machine-readable framing is the part worth taking seriously. This atlas
publishes prose and a generated capability grid; nothing here is consumable as a
dataset with stable ids. That is a real gap and it is not obviously the right one
to fill — see "What to take from it" below.

## The link check

The dataset labels 104 of its 122 URLs `candidate_url` and attaches a
`verification_hint`: *"verify title and metadata against source_url before release
tagging"*. So it says plainly that this step has not been run. It has now been run
here, with a HEAD request per record:

| Result | Count |
| --- | --- |
| 200 | 88 |
| 404 | 14 |
| No URL at all | 18 |
| 401 (auth-gated endpoint) | 1 |
| transient failure, 200 on retry | 1 |

The 14 dead links, re-checked with redirects followed:

```text
github.com/memoria/memoria          (src-036 and src-070, listed twice)
github.com/muninndb/muninndb        (src-037 and src-074, listed twice)
github.com/truememory/truememory
github.com/engramai/engramai
github.com/neotoma/neotoma
github.com/mastraai/mastra
github.com/doobidoo/mcp-memory-service
github.com/topoteretes/cognee-mcp
dev.to/adversa-ai/mcp-security
hindsight.vectorize.io/docs
vectorize.io/blog/rag-is-on-life-support
simonwillison.net/2025/Jun/11/lethal-trifecta
```

**Six of them share a shape:** `memoria/memoria`, `muninndb/muninndb`,
`truememory/truememory`, `engramai/engramai`, `neotoma/neotoma` — org and repo
identical, for projects whose titles carry 2026 dates and descriptions like
"Memoria: Git for Agent Memory" and "Neotoma: Deterministic State Layer". That is
what a plausible-sounding GitHub URL looks like when nothing checked it. The
seventh, `mastraai/mastra`, is one hyphen from `mastra-ai/mastra`, which is real
and which this atlas has pinned.

**The more interesting failure returns 200.** `src-021` is titled *LoCoMo (Maharana
et al., ACL 2024)* and its `source_url` is
`github.com/xiaowu0162/longmemeval` — LongMemEval's repository, which is also
`src-022`'s URL. LoCoMo's actual repository, `snap-research/locomo`, exists. So the
record resolves, looks verified to a link checker, and points at the wrong
benchmark. No amount of HTTP-status checking finds that one.

## The methodological finding

The dataset carries three fields that look like quality signals and are constants:

- `claim_review_status` is `no_quantitative_claim` for **all 122** records.
- `confidence_score` takes exactly three values, and they are a restatement of
  `url_status`: 0.8 or 0.82 for every `candidate_url` record, 0.45 for every
  `reference_only_url` record. Nothing else moves it.
- Consequently **the 14 dead links carry the same 0.8 confidence as the 88 live
  ones.** `memoria/memoria`, which does not exist, and `mem0ai/mem0`, which this
  atlas has read at a pinned commit, are equally confident rows.

This is worth recording because it is the same failure this atlas keeps finding in
memory systems, in a different medium. A confidence score that is a deterministic
function of one other column adds no information and subtracts caution: it *looks*
like the corpus has been graded. The atlas's own version of the temptation is the
[declined three-state capability column](2026-07-28-declined-proposals.md) — a
middle bucket that absorbs every hard case and stops discriminating. Here the
bucket is a number.

None of this is concealed. `verification_status` splits 93 `public_candidate` / 29
`reference_only`, the README badges the project as a release candidate, and the
verification hint says what has not been done. The gap is between what the fields
promise a consumer — especially an *agent* consumer, which is the stated audience
— and what they encode. An agent ranking by `confidence_score` would rank a
nonexistent repository above nothing at all.

## What to take from it

**Worth stealing, and this atlas does not have it:** a machine-readable export
with stable ids. The reports here are prose with a generated capability grid, and
there is no artifact an agent can consume without scraping HTML. `sources.jsonl`
plus `indexes/*.json` is a good shape for that, and the id scheme (`src-NNN`,
stable across the CSV, JSONL and index files) is the part that makes it usable.

**Not worth copying:** the confidence score. If this atlas ever ships one it
should be a function of something that varies — was the code read, at what commit,
was the claim traced to a symbol — and if it would be constant, the honest version
is a boolean or nothing at all. The atlas already makes this argument about
capability marks and should hold to it about any future score.

**No change made here.** The seven overlapping systems are already reviewed; the
35 others are mostly out of scope by the inclusion test or already on the
[survey note](2026-07-29-memory-survey-forms-functions-dynamics.md)'s candidate
list. Nothing in the other atlas's records is evidence about code, which is what
this atlas's claims rest on.

**One thing was checked and is not actionable:** whether any of the five
invented-looking projects exist under another name. `omega-memory/omega-memory`
does resolve, so the org/repo-identical pattern is not proof on its own. The other
five return 404 at the URL given and were not searched for elsewhere — if any of
them is real under a different slug, the dataset's record is still wrong and the
correction belongs upstream rather than here.

## If reporting this upstream

The useful version is small and mechanical, and the project is set up to receive
it — `CONTRIBUTING.md` exists and the verification hint invites exactly this:

1. The 14 URLs above return 404.
2. `src-021` (LoCoMo) points at LongMemEval's repository; `snap-research/locomo`
   is the one.
3. `src-036`/`src-070` and `src-037`/`src-074` are duplicate records.
4. `confidence_score` is currently determined entirely by `url_status`, so it
   cannot separate a live source from a dead one.

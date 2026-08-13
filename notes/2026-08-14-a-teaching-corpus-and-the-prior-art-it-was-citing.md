# A teaching corpus, and the prior art the atlas was citing without reading

**Status:** complete. Six reports written and pushed across two batches
([`83806031`](https://github.com/neoneye/agent-memory-atlas/commit/83806031),
[`c789d03b`](https://github.com/neoneye/agent-memory-atlas/commit/c789d03b)).
Every system named in the source repository has been read or dispositioned
below.
**Origin:** [NirDiamant/Agent_Memory_Techniques](https://github.com/NirDiamant/Agent_Memory_Techniques),
a thirty-notebook cookbook, submitted as a reading list rather than as a
candidate.

Recorded because the batch discovered almost nothing and was worth running
anyway, and the reason those two facts sit together is the finding.

## The list, and how little of it was new

Screening the README, `docs/`, every notebook and `requirements.txt` for named
systems gave 21 candidates. Fifteen already had reports. One more closed itself:
`GibsonAI/memori` and the atlas's `MemoriLabs/Memori` return the same
`git ls-remote HEAD` — `538b61f245295aa1a43df8033879f8293627f74d` — so it is a
transfer, not a second project, and the same commit the report is already
pinned at.

LoCoMo and LongMemEval are benchmarks and belong on
[the benchmarks page](../content/benchmarks.md). Chroma, FAISS, Qdrant,
Pinecone, Weaviate, Milvus, Neo4j, NetworkX and pgvector are storage engines; a
vector database is not agent memory, and the atlas's Redis entry is
`redis/agent-memory-server`, which is Redis's memory product rather than Redis.

Six candidates were left. On the usual measure of a candidate source — new
systems found per repository read — that is a poor return, and a list drawn from
a tutorial should be expected to have one, because a tutorial names what is
already famous.

## What the return actually was

| System | Files in `content/` citing it *before* it was read |
| --- | ---: |
| [Zep](../content/systems/zep.md) | 16 |
| [LangGraph](../content/systems/langgraph.md) | 12 |
| [LangChain](../content/systems/langchain.md) | 11 |
| [MemoryBank](../content/systems/memorybank.md) | 6 |
| [Reflexion](../content/systems/reflexion.md) | 5 |

Every one of the five was already load-bearing in this atlas's prose. MemoryBank
is named twice on the benchmarks page as the nearest thing to a forgetting
benchmark. Zep is the vendor behind a reported system and appears in the
comparison. LangGraph is the store a dozen reports say their subject delegates
to. These were not discoveries; they were **citations the atlas had been making
without having read the source.**

That is a different axis from coverage, and it is not one the corpus join
measures. A join on `source_url` finds repositories with no report. It does not
find *reports that lean on a system with no report*, which is the more
embarrassing gap, because those are places the atlas has already asserted
something.

**A probe worth running:** extract every proper-noun system named in
`content/**/*.md` prose, subtract the ones with a report, and rank the remainder
by citation count. The five above would have been at the top of that list on
2026-08-13, and nothing in the existing tooling would have surfaced them.

## The zep reversal

[The 2026-08-09 triage](2026-08-09-seventy-one-repositories-from-an-outside-corpus.md)
dispositioned `getzep/zep` in one table row: *"Examples, integrations, ingestion
and benchmarks; the engine is Graphiti, already reported."*

Every clause of that is true, and the conclusion was wrong. What the row
describes as "benchmarks" is `benchmarks/locomo/experiments/` — **five LoCoMo
experiments of ten runs each, 77,000 graded question instances, with per-run
standard deviations, context-token distributions and retrieval latency
percentiles committed to git.** It is the strongest single piece of measurement
evidence in the corpus, and it produced two corrections to the benchmarks page:
the claim that cost and latency are barely measured, and the judge-variance
section, which now has an actual variance to quote (0.33 to 0.47 accuracy points
run to run).

The generalizable error: the triage asked *where is the mechanism* and answered
correctly. The question it did not ask is *what else is in the tree*. A client
repository for a closed service is exactly where a vendor puts its measurement
apparatus, because that is the half a customer can run.

A second thing the row could not have known, and worth stating for anyone
re-reading a client-side repository: `zep-ingest`'s **warning strings are the
best public documentation of the hosted service's failure modes** — that an
episode with no `created_at` is silently dated to ingestion time "which corrupts
fact validity timelines and invalidation ordering on backfills", and that a fact
is not searchable when the write API reports success. Vendor engineers writing
guard rails say things vendor marketing does not.

## Two arithmetic bugs in two metrics, in one batch

The batch found two defects of the same shape, in unrelated repositories, and
neither is subtle once you look:

**[MemoryBank](../content/systems/memorybank.md)** — `math.exp(-t / 5*S)`, which
Python parses as `((-t)/5)*S`. The docstring directly above says "The higher the
memory strength, the slower the rate of forgetting." The code does the reverse:
82% one-day retention at strength 1, 13.5% at strength 10. Since retrieval
increments strength, recall is what destroys a memory. Unfixed since 24 May 2023
in the reference implementation of the paper that put the Ebbinghaus curve into
this field.

**[Agent Memory Techniques](../content/systems/agent-memory-techniques.md)** —
`ContradictionDetector.scan` batches memories fifteen at a time, finds
contradictions only within a batch, and divides by `n(n-1)/2`. At a hundred
memories that is roughly 735 pairs examined against 4,950 counted. The rate
falls as the store grows even when the true density is constant, so a dashboard
built on it reports improving consistency while conflicts accumulate.

Both are one line. Both are in a *metric* — a decay function and a rate — rather
than in a store, which is why neither had a test: the code paths around them
work fine, and only the number is wrong. A store bug corrupts data and gets
noticed; a metric bug produces a plausible float forever.

**Proposed check:** any scoring function whose sign or direction is load-bearing
— decay, recency, confidence, relevance — needs a monotonicity assertion, and
any rate needs its denominator to be the set that was actually examined. Two
lines each. Worth adding as an explicit prompt in
[the report format](../content/methodology/per-repo-report-format.md)'s section
7 or 10, because the atlas has now found this twice in one sitting and has no
step that asks for it.

## The pairing worth keeping

MemoryBank and the cookbook implement the same mechanism, and the cookbook cites
MemoryBank. The teaching implementation is the correct one:
`decay_rate = math.log(2) / half_life_hours`, reinforcement additive to strength
and capped, and `prune()` setting `archived = True` and moving the record rather
than popping it out of the only copy.

So the pattern travelled correctly even though the reference implementation did
not, which is a mild argument against the assumption that downstream systems
inherit their prior art's defects. It is also an argument for reading the
teaching corpus: it is where a mechanism's *intended* form is written down, and
the intended form is sometimes better documented than in the paper's own code.

Whether the atlas's other forgetting-curve systems inherited the expression or
the idea is not established here. Grepping the corpus for `exp(` in a decay
context is cheap and has not been done.

## The half of the cookbook that is not memory

Six of the thirty techniques — the five short-term ones plus notebook 12's
working memory — are conversation-window management. Nothing in them survives
the process. They are filed under "memory" in the repository's own family table,
and the report says so, because that naming is a large part of why
[the scope boundary](../content/overview.md) needs three separate "not in scope"
sections.

This is the cleanest available example of the confusion, and it is not the
cookbook's fault: it inherited the vocabulary from LangChain, whose
`ConversationBufferMemory` and `ConversationTokenBufferMemory` named the thing.
The [LangChain report](../content/systems/langchain.md) records the resolution —
version 1 owns no store at all, and the ten classic classes sit in
`langchain_classic` under `@deprecated(since="0.3.1", removal="2.0.0")`. The
framework that created the ambiguity has resolved it with a package boundary,
and the tutorials have not caught up.

## Operational: `screen_corpus.py --reuse` does not do what a batch needs

`scripts/screen_repo.py` was run against all six checkouts and the outcomes are
in each report's History section, per the skill. The ledger in
`notes/screening/screening.json` does **not** know about them.

`screen_corpus.py --reuse <dir>` matches clones by report slug, but it selects
*which* repositories to screen from the ledger's own unscreened set in its own
order — so invoking it with `--batch 5` and a directory holding exactly the six
new checkouts screened five unrelated systems near the front of the alphabet and
cloned them fresh. The reuse directory was ignored because none of its slugs were
in the batch it had already chosen.

That change was reverted to keep the commits focused. The gap remains: **there is
no way to say "screen these specific slugs"**, so a batch's own checkouts cannot
be folded into the ledger at the time they are read, which is the only time they
are on disk. A `--only <slug>[,<slug>]` argument would close it, and would make
`--reuse` mean something for the workflow that actually produces new reports.

Until then the ledger will keep trailing the corpus by however many systems have
been added since the last full sweep — currently six.

## Disposition table

| Candidate | Outcome |
| --- | --- |
| `getzep/zep` | [Report](../content/systems/zep.md) — reverses the 2026-08-09 disposition |
| `zhongwanjun/MemoryBank-SiliconFriend` | [Report](../content/systems/memorybank.md) |
| `noahshinn/reflexion` | [Report](../content/systems/reflexion.md) — in scope via AlfWorld/WebShop only |
| `langchain-ai/langgraph` | [Report](../content/systems/langgraph.md) — the store, not the checkpointer |
| `langchain-ai/langchain` | [Report](../content/systems/langchain.md) |
| `NirDiamant/Agent_Memory_Techniques` | [Report](../content/systems/agent-memory-techniques.md) — the list's own repository |
| `GibsonAI/memori` | Same HEAD as `MemoriLabs/Memori` — [already reported](../content/systems/memori.md) |
| mem0, letta, graphiti, memos, memori, llamaindex, autogen, crewai, cognee, generative-agents, voyager, basic-memory, 7layermem | Already reported |
| LoCoMo, LongMemEval | Benchmarks — [benchmarks page](../content/benchmarks.md) |
| Chroma, FAISS, Qdrant, Pinecone, Weaviate, Milvus, Neo4j, NetworkX, pgvector | Storage engines, not agent memory |

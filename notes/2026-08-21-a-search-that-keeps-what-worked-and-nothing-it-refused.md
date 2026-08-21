# A search that keeps what worked, and nothing it refused

**Status:** triage. One paper read on 2026-08-21. Not agent memory, no repository
to pin, and one observation worth carrying because it appears here in a genre
where this atlas has not been looking for it.
**Origin:** one link submitted alone.

---

## AVO: Agentic Variation Operators for Autonomous Evolutionary Search — [arXiv:2603.24517](https://arxiv.org/abs/2603.24517)

Terry Chen and twenty-one co-authors, submitted 25 March 2026, cs.LG. The idea
is to replace the fixed mutation and crossover of evolutionary search with a
coding agent: *"AVO instantiates variation as a self-directed agent loop that can
consult the current lineage, a domain-specific knowledge base, and execution
feedback to propose, repair, critique, and verify implementation edits."* Applied
to CUDA attention kernels on a B200, it reports 1668 TFLOPS BF16 for multi-head
attention — 0.4% to 3.5% over cuDNN and 5.0% to 10.5% over FlashAttention-4 —
and a transfer to grouped-query attention in thirty minutes of autonomous effort.
The run behind it is seven days of continuous evolution, 40 committed kernel
versions, and *"over 500 candidate optimization directions"* explored internally.

**Excluded, on two boundaries at once, and a third reason that would be enough
alone.** No code, kernels or artifacts are released, so there is nothing to pin
and nothing this atlas could check.

The *knowledge base* is the corpus-index boundary. It holds CUDA programming
guides, PTX ISA documentation, Blackwell architecture specifications and existing
kernel implementations including the FlashAttention-4 source — material the
system did not author, handed to the agent at the start. The paper describes the
agent consulting it and describes no path by which the agent writes back into it.
Nothing in it is a claim the system made that a later reading could contradict,
which is the same call already recorded for `tobi/qmd`,
`VectorSpaceLab/general-agentic-memory` and the rest of the corpus-index pile.

The *lineage* is the [second boundary](../content/overview.md) — a store of the
agent's work. *"Each committed version xᵢ is persisted as a git commit along with
its score, maintaining full state continuity across the entire evolutionary
process."* A kernel and its measured throughput survive the session and carry an
identity, and neither is the kind of thing that can turn out to have been false:
re-run the benchmark and the number comes back. That is search state, the same
shape as a task database.

**Two things are worth keeping.**

**The persistence layer is `git commit + score`, and that is the whole store.**
Seven days, 40 versions, no database, no index, no schema. Several systems in
this atlas build a versioned store for material with weaker requirements than
this. When the artifact is a file and the judgement is a number, the commit log
is the lineage, and a project reaching for something larger should be able to say
what it needs that this does not have.

**And the observation that transfers: five hundred directions were explored, and
what persists is forty that worked.** The lineage records the accepted versions
and their scores. The knowledge base is read-only. So the four hundred and sixty
directions that were tried and abandoned leave no durable trace — the next
generation, and any later run, can rediscover a dead end at full cost, because
nothing anywhere says it was one.

This atlas's most-repeated finding is that a store records what it admitted and
nothing about what it refused: an audit log with no rejection rows, a governance
engine that logs the memory it surfaced and never the one it declined, an
admission gate whose `Reason` field is read as a boolean and dropped. Those are
all memory systems. Here the same gap appears in an evolutionary search loop, and
it costs the thing the loop is actually spending — compute. A rejected-value
tombstone in a memory store and a record of a refuted optimization direction are
the same mechanism aimed at different waste, and the second one has a
seven-day-run-sized argument behind it.

**The paper cannot settle whether the lineage earns its place.** There is no
ablation isolating the knowledge base from the lineage from execution feedback;
the loop is evaluated whole. The thirty-minute GQA transfer is the closest thing
to evidence that the accumulated history carried something, and with no arm that
starts from scratch it cannot separate *the lineage transferred* from *the model
is good at grouped-query attention*. That is the same criticism this atlas makes
of memory systems that ship several mechanisms and one number, and it applies
here for the same reason.

---

## For next time

**The exclusion boundary held with no argument, and the useful part was
downstream of it.** Deciding that a kernel's measured throughput is not a
correctable claim took one sentence. What took reading the paper was noticing
that the loop discards its failures, which is a finding about *memory* arriving
from a paper that is not about memory and does not use the word.

**A genre check is worth running deliberately.** The atlas looks for the
what-was-refused gap in stores. It is a property of any loop that generates
candidates and keeps the winners — evolutionary search, retrieval reranking,
sampling with rejection, plan repair. Where else the corpus's central finding
already applies, without anyone having gone to look, is a question worth a pass
of its own.

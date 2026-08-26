# A superlative is a claim about your own search

**Status:** method. Written 2026-08-26 after three corrections in four days —
two to published reports, one to a sentence on the benchmarks page that was
falsified within twenty-four hours of my writing it.
**Why:** each is recorded where it happened. Together they have a shape, and the
shape is not carelessness. All three were *coherent* readings that stopped early
because they had enough to write a confident sentence.

---

## The three

**1. I read a macro and not its sibling.** The aimee report described
`DB2_MEMORY_SCOPE_RANK_SQL` — an ordering expression — and concluded, in the
report body, that it *"excludes nothing."* True of that macro. Wrong about the
system, because `DB2_MEMORY_SCOPE_FILTER_SQL` sits directly beneath it in the
same header, wraps the same expression as a `WHERE` predicate, and both are
applied together in `memory_briefing.c`, `memory_relations.c` and
`pgvec_transport.c`.

The failure was reading a definition and not the twenty lines after it. The
header literally contains both.

**2. I read a directory and not the tree.** The OpenWorker report was written
from `coworker/memory/`, found four files, and described that as the memory
subsystem. Two marks were available at that pin and missed: `tests/test_memory.py`
was 189 lines with a paired scope-isolation assertion in it, and the report said
*"no memory-specific test or benchmark was located"*; `coworker/audit.py` was 174
lines with eighteen `_audit(` call sites, one in the common loop over every tool
call, and the report listed as a gap that *"`memory_forget` is a silent hard
delete in an application that audits other operations."*

Neither miss required judgement. Both required one grep outside the directory
whose name matched. In a repository organised by layer rather than by feature —
a `tests/` tree at the root, an audit module beside the engine — the mechanism
is never all in one place, and **a directory listing is the least reliable map
available.**

**3. I wrote a superlative about the world that was a fact about my search.**
On 25 August I wrote into the benchmarks page, comparing Prime Agent (code
published, measurements absent) with VISTA (traces published, code absent):

> *"The version that would — source at a pinned commit plus the traces the
> number was computed from — is still not something this page has found for an
> agent-memory claim."*

On 26 August I read *The Compaction Cliff*
([arXiv:2608.22752](https://arxiv.org/abs/2608.22752)), whose reference
implementation is Apache-2.0 at a pinned commit with twenty `results/*.json`
files beside twenty-two experiment scripts. Three separate claims from the
abstract checked against those files, all three matching at the stated *n*. The
sentence was false within a day.

---

## What separates the three

The first two are search failures with mechanical defences, and I have written
both into the repository: read the header end to end before writing an absence
claim about it; grep the tool names and the store class across the whole tree,
not the package that carries the word *memory*.

The third is different in kind and worth more attention, because no amount of
searching fixes it. **"Nothing in the corpus does X" is a claim about the
corpus. "This is still not something this page has found" is a claim about my
search, phrased as a claim about the field.** Both were in that sentence, and
the second one is what made it fragile: it was true when written, it had a
short shelf life, and it was written in a register that invited a reader to take
it as a fact about the state of the art.

The atlas already has a rule for the near case — the standing prohibition on
freshness stamps, on the ground that a dated claim rots. This is the same
failure without the date: an undated superlative is a freshness stamp with the
date removed, which is worse, because a reader cannot tell how old the search
behind it is.

---

## The formulation I want to keep

A finding of the form *"the corpus contains no instance of X"* has two honest
renderings and one dishonest one.

- **Honest, bounded:** *"Twenty-four of 336 systems carry a value-level
  tombstone."* A count over a defined set. Checkable, and mechanically re-checked
  on every build.
- **Honest, hedged with its own scope:** *"No system read here has done both,
  and the corpus is an opportunistic collection rather than a sample."* The
  rubric page already says this about its own numbers, and I should have
  borrowed the phrasing.
- **Dishonest by omission:** *"is still not something this page has found."*
  Reads as a property of the field. Is a property of the reading list.

The cheap defence is that the first form is always available. The atlas's
build already binds and re-checks twenty-two mechanism counts against report
frontmatter, so a numeric claim of that shape cannot go stale silently. A
superlative has no such guard, and I do not think one can be built for it —
which means the discipline has to be at writing time: **if a claim would be
falsified by one more repository, write the count instead of the superlative.**

---

## What this does not mean

Not that the corrections were bad outcomes. Two of the three were found by
re-reading a system at a later pin, which is what the re-analysis workflow
exists for, and the third was found by the next reading — the process worked in
all three cases and worked within days.

What it means is narrower: the confidence in the *prose* was not calibrated to
the thoroughness of the *search*, and the prose is what a reader gets. Three
instances in four days is enough to call that a pattern rather than an accident,
and the pattern is that a coherent partial picture is the most dangerous input
to a confident sentence — the same failure the NexusMem entry in the overview's
History recorded months earlier, arriving in three new disguises.

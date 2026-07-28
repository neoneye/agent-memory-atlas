# The prior art this atlas does not cover

**Status:** a gap, noticed rather than researched
**Origin:** triaging two FRDCSA repositories (`autonomous-ai-agent`,
`free-life-planner`) on 2026-07-28. Neither earned a report — no memory
subsystem, and neither is self-contained — but reading AgentSpeak(L) agents
made an omission obvious.

## The gap

The atlas's **research lineage** family begins in 2023: Generative Agents,
Voyager, HippoRAG, A-MEM. Everything earlier is absent, and the omission is not
that the atlas is young. It is that agent memory has an older literature under
different vocabulary, and this atlas neither uses it nor says why not.

Specifically, symbolic AI spent decades on problems this atlas frames as
unsolved:

- **Belief revision.** How a knowledge base should change when new information
  contradicts what it holds — with formal criteria for what a rational revision
  preserves. The atlas's contradiction and supersession material is a practical
  restatement of this with no reference to it.
- **Truth maintenance systems.** Structures that record *why* each belief is
  held, so that when a justification is withdrawn every belief depending on it
  is retracted too. That is, in different words, the cascading-deletion problem
  the [benchmarks page](../content/benchmarks.md) calls the step every system
  fails: a deleted memory surviving inside a summary, a profile, a graph edge.
- **BDI belief bases.** AgentSpeak(L), which the FRDCSA repositories implement,
  gives an agent a belief base, a plan library, and an intention stack, with
  belief update as a defined operation rather than an emergent behaviour.

I am flagging these from familiarity with the literature, **not** from code read
here — which is exactly the epistemic status the atlas requires me to state, and
the reason this is a note rather than a page.

## Why it matters for the atlas's findings

The tombstone provenance now traced end to end says the mechanism was invented
once, under adversarial pressure, in June 2026. That is true of *this corpus*.
It would be a much weaker claim if the underlying idea — do not silently
re-derive a belief that was retracted — turns out to be a known result in
symbolic AI that the LLM-agent field simply has not read.

Two possibilities, and they suggest different things:

1. **The field is rediscovering solved problems.** Then the atlas's most useful
   contribution might be translation rather than advocacy: showing that
   `rejected_value` is a tombstone in a truth maintenance system, and that the
   design questions have answers somebody already worked out.
2. **The problems are genuinely different.** LLM extraction produces beliefs
   with no explicit justification structure, so a TMS's dependency graph may have
   nothing to attach to. If so, that difference is worth stating precisely,
   because it explains why the older work does not simply apply.

I do not know which. The honest position is that the atlas currently implies the
first is false by never mentioning it.

## What would settle it

Not more repository reviews. Reading the belief-revision and truth-maintenance
literature against the atlas's own patterns, and writing one page that either
maps them onto each other or explains the mismatch. That is a literature review,
which is a different activity from everything else in this project and would
need the same discipline: claims traced to sources, absences stated as
absences.

The risk of not doing it is specific. An atlas that presents "correction before
scale" as a novel argument, when a substantial literature has argued something
adjacent since the 1980s, is overclaiming — and it is the kind of overclaim that
one informed reader dismantles in a paragraph.

## Smaller observation

FRDCSA also surfaces a repository-shape problem worth remembering during triage:
both repos carry dozens to hundreds of **absolute paths** into a
`/var/lib/myfrdcsa/` installation that is not published with them. A repository
can look substantial, be genuinely substantial, and still be unevaluable because
the parts that matter live somewhere else. The atlas has hit this before with
documentation-only projects; this is the same failure with the opposite cause.

# A review that found the thing the atlas had not disclosed

**Status:** done — the rubric and the hazards note changed; three suggestions declined
**Origin:** an unsolicited Gemini review of the atlas, submitted 2026-07-30, the
second AI review this week. The first is recorded in
[2026-07-30-two-ai-reviews.md](2026-07-30-two-ai-reviews.md).

## The finding

Buried in the review's first paragraph, stated as plain fact and not as a
criticism:

> the author (Simon Strandgaard / neoneye, aided by LLM code analysis) evaluates
> *what the code actually does*

**Nothing on the site said that.** The rubric's known-limits section said "marks
are assigned by one reviewer reading code, not by running it", which reads as a
person. The reviewer inferred the rest correctly from the reports — the volume,
the consistency of the format, the way a definition gets applied identically
across a hundred systems — and it was right.

That is the review's whole value, and it arrived as an aside. A project whose
distinguishing claim is that it refuses assertions unsupported by artifacts had
left its own method to be guessed by readers, for months, while criticising other
repositories for exactly that shape of omission. Recorded here rather than only
in the fix, because the failure was not the missing sentence; it was never asking
what a reader would need to know to weigh a mark.

**Changed:** the [rubric](../content/methodology/atlas-rubric.md) now says it in
the known-limits section, and the
[hazards note](2026-07-28-methodology-hazards.md) gains §2b naming the failure
mode with three instances from one day — two fabricated commit ids caught by
running `git log`, a non-existent parameter-shift bug in Cortex that was one line
from publication, and Mem0's `audit_log` mark that was wrong for two months. The
third is the one that matters: the first two were caught by the discipline the
atlas already imposes, and a false *negative* leaves nothing to notice. It
surfaced only because the corpus happened to contain the same design twice.

## What checked out

The review is accurate on the material, which is what makes the disclosure gap
worth taking seriously rather than dismissing.

- The five divergences, correctly enumerated.
- Generative Agents' hand-tuned weights; Cortex's `maxRetentionDays` that nothing
  calls; TokenMizer's `CONTESTED`; the Pydantic AI Harness's scope
  re-verification; Gobii's ephemerality strings in the schema prompt. All five
  are stated as the reports state them.
- "110 systems" was right when the review was written and is 111 now. Drift.

## Two attributions that are off

- **Evidence-before-belief is credited to "MemMachine and Helm".** The pattern
  page leads on [nanobot](../content/systems/nanobot.md), whose documentation
  states the principle better than the page originally did — *"It is not the
  final memory. It is the material from which final memory is shaped."* Both of
  the review's systems appear once each; neither is the page's anchor.
- **"AutoGen and ADK didn't originally include an identifier to allow for
  targeted deletion"** conflates two different findings. AutoGen's
  `MemoryContent` has no identifier, which is why targeted deletion is
  *inexpressible* there. ADK's `MemoryEntry` has an optional id and its
  `BaseMemoryService` simply declares no removal method — a choice, not a
  consequence. The distinction is the whole point of that comparison.

## Three suggestions declined

**A live bake-off — "which pattern actually wins".** Declined for the reason
already recorded in [declined-proposals](2026-07-28-declined-proposals.md) under
"run one standardized test against every system": the corpus spans Rust crates,
Postgres services, hosted vector APIs, a Minecraft agent and several systems that
cannot store a byte without a paid key. A hallucination-rate or recall
comparison covering the fraction that runs would read as a ranking of the whole.
**What changed since that decision:** [ForgetEval](../content/benchmarks.md) now
exists — 385 adversarial cases scoring the control plane across six systems, five
of them in this atlas — so the bake-off the review wants is being built by
someone else, on the axis this atlas cares about, and the right move is to cite
it rather than to build a second one.

**Scale and performance thresholds — "at what point does a pattern break down".**
Genuinely absent and genuinely out of reach by static review: nothing here is
run, so a threshold would be invented. Where a report *can* name the quantity
that will break — Helm's 500-row recall window, Juggler's unbounded whole-file
injection, Gobii's uncapped agent database, Mnemopi's fourteen untuned decay
curves — it does, in the open-questions section, and that is the honest form of
the answer this method can give.

**HCI and the resolution UX.** Correct that it is missing, and the reason is the
inclusion test rather than an oversight: a memory UI that only displays does not
earn `human_review`, so the atlas already draws a line at *mechanism* and would
have to change what it is to cross it. The observation underneath is sharp
though — a governed trust state whose conflict-resolution flow nobody can use is
a mechanism that will not be exercised — and TokenMizer's `CONTESTED` is exactly
where that bites, since the status is designed to be resolved by a human and
nothing in the repository prompts one. Kept as an open question in that report,
not as a new column.

## One claim to push back on

**"The orchestration/planner link is largely missing — how the agent decides to
trigger a search."** That is the atlas's *fourth divergence*, "whether retrieval
can decline", and it has a pattern page —
[gate the expensive path](../content/patterns/gate-the-expensive-path.md) — plus
[retrieval hysteresis](../content/patterns/retrieval-hysteresis.md) beside it.
[Waku](../content/systems/waku-agent.md) is reviewed specifically for organising
everything around refusing expensive work, with a small model deciding whether to
retrieve at all; the report also notes that nothing in the atlas measures such a
gate's false-negative rate, which is the real gap in that area.

The review is right that *prompt engineering and the tool-calling loop* are out
of scope, and that is deliberate. But "when to search" is a memory decision, it
is one of the five things this atlas says separates these systems, and it is
covered.

## Why record a favourable review at all

Same reason as the last one, and one more. Two independent reviewers this week
converged on correction-as-the-blind-spot and on the declared-versus-enforced
distinction, which is weak corroboration that those are the load-bearing claims —
weak because both read the atlas, so the agreement may be its own emphasis
reflected back.

The new reason is sharper: **this review found something by reading the artifact
rather than the argument.** Nobody was asked to audit the methodology page. A
reader reconstructed how the work is done from its output, stated it in passing,
and was right about a thing the project had never written down. That is the exact
move this atlas makes on other people's repositories, arriving from outside, and
it is the strongest evidence yet that the method generalises past whoever is
holding it.

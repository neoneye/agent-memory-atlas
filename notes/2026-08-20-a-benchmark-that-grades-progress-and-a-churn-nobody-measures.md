# A benchmark that grades progress, and a churn nobody measures

**Status:** triage. Two items read on 2026-08-20 — a terminal-agent benchmark and
a 2022 reinforcement-learning paper — neither of them a memory system, both
integrated into pages that were arguing for what they contain.
Recorded alongside [NanoClaw](../content/systems/nanoclaw.md), which was the
memory system in the same batch.
**Origin:** three links submitted together.

---

## Long-Horizon-Terminal-Bench — [dataset card](https://huggingface.co/datasets/IntelligenceLab/Long-Horizon-Terminal-Bench), [arXiv:2607.08964](https://arxiv.org/abs/2607.08964)

**Not a memory system; added to the [benchmarks page](../content/benchmarks.md).**
Apache-2.0, 46 tasks in one `test` split, 1.18 GB, published by IntelligenceLab
with a leaderboard and a code repository. Each task is a `task.toml`, an
`instruction.md` and a Dockerfile, carrying `difficulty`, `allow_internet`,
`cpus`, `memory_mb`, `gpus`, `agent_timeout_min` and `expert_time_estimate_min`.
Reference solutions and verifiers are withheld from the card to limit
contamination.

It is here because of the grading, which is the design the atlas's benchmarks
page has been asking for and not finding. The paper's complaint about existing
terminal benchmarks — *"evaluated only by their final outcome"*, which
*"overlooks intermediate progress and partial solutions, yielding sparse reward
signals"* — is the same complaint the page makes about memory benchmarks, and
the fix is the same fix: decompose the task into graded subtasks and award
partial credit. Reported averages of 9.9M tokens, ~231 episodes and 85.3 minutes
per task put it in the only regime where a memory layer's behaviour under
compaction would be visible at all; best-of-fifteen is 15.2% pass@1 at a 0.95
threshold, mean 4.3%.

Two things not to overclaim. The verifiers are hidden, so the grading cannot be
inspected — every statement about how it grades comes from the card and the
abstract, not from reading a grader. And a 4.3% mean means a memory layer's
contribution would be hard to separate from everything else an agent gets wrong;
the limit on this measurement is the 46 tasks, not the ceiling.

The reason it earns page space beside the compression result read in the same
week: that result was measured over a 24-turn horizon and found retrieval calls
tripling while completion did not move. This benchmark is the same experiment's
natural home at ten times the length, and nobody has run a memory system in it.

## The Phenomenon of Policy Churn — [arXiv:2206.00730](https://arxiv.org/abs/2206.00730)

**Excluded as a subject; one argument taken into
[retrieval hysteresis](../content/patterns/retrieval-hysteresis.md).**
Schaul, Barreto, Quan and Ostrovski, v1 1 June 2022, cs.LG. No code or dataset
named on the abstract page. It is deep reinforcement learning and has nothing to
do with agent memory.

The finding: the greedy policy in value-based RL changes its chosen action in a
large fraction of states within *a handful of learning updates*, across
algorithms and environments; the ablations narrow the cause to properties of deep
learning; and the conclusion is that this churn is *"a beneficial but overlooked
form of implicit exploration"*, with ε-noise mattering less than assumed.

Why it is worth carrying across: a top-*k* retrieval is also an argmax over a
learned function, and it also flips when that function moves. The transferable
piece is a **question, not a mechanism** — how much does your top-*k* change
under a re-index, a model version bump, or one more stored item? Nothing in this
corpus measures it, and the measurement is one loop: same queries, before and
after, count the changed sets.

The uncomfortable half is that this cuts against the pattern page it was added
to. Sticky and cooldown exist to damp exactly this flipping. If the flipping is
partly load-bearing where recall feeds *what to try next* — which is the case
LoongFlow's Boltzmann sampling is built for — then damping it is a cost, not a
free improvement. Where recall feeds *what is true about a person*, the flipping
is unambiguously a defect. A system adopting hysteresis should know which of the
two it is, and that sentence is the whole contribution.

---

## For next time

**The strongest external evidence keeps arriving as an analogy that has to be
labelled.** A 2022 RL paper is not evidence about retrieval, and saying so in the
same sentence as the claim is what makes it usable rather than decorative. The
alternative — dropping it because it is not code at a pin — loses the only
argument in weeks against a pattern this atlas recommends.

**A benchmark can be worth citing for its grading alone.** Nothing about
Long-Horizon-Terminal-Bench is memory-specific and no system here runs it. It is
on the page because it is a worked example of partial-credit grading over a long
horizon, which is the thing the forgetting benchmark in section 6 would need and
does not have.

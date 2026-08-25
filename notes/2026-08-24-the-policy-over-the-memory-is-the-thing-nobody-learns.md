# The policy over the memory is the thing nobody learns

**Status:** triage. One paper read on 2026-08-24 — abstract and listing
metadata only. No repository, so nothing to pin and no report.
**Origin:** one arXiv link submitted alone.

---

## EvoHarness-RL — [arXiv:2608.05446](https://arxiv.org/abs/2608.05446)

Xuying Ning and fifteen co-authors, submitted 5 August 2026, cs.LG, accepted to
LLA@COLM 2026. *"Learning Self-Evolving Runtime Harness for Long-Horizon LLM
Agents."*

The framing is the useful part. It names two coupled problems — *"state
formation from noisy interaction traces and runtime control over external-state
access"* — and observes that existing agents *"usually handle both through
prompts, heuristics, or domain-specific conventions, leaving the external
workspace and its usage policy manually engineered."*

That sentence describes this corpus exactly. Three hundred and thirty-one
reports, and the *when* is hand-written in every one of them: a similarity
threshold, a decay half-life, a consolidation trigger, an importance weight, a
top-*k*. The atlas has spent a lot of prose on the constants — Generative
Agents' `gw = [0.5, 3, 2]` with no ablation, MemoryOS's promotion coefficients
left at 1/1/1, Mnemopi's fifty-odd Weibull parameters, Arcon's six ranking
weights, GENOME's half-life ratios (whose comment says only the *ordering* is
the design claim), Hillock's threshold moved three times across four releases.
LivingFeed's answer — store the four components of a composite score so an
offline replay can tune them — is the best one in the corpus and is still
tuning.

This paper proposes not tuning them. Supervised harness fine-tuning teaches the
action space; cost-aware GRPO learns when to **read, update and consolidate**.
The policy over the memory becomes the learned object, and the memory schema
becomes the environment it acts in.

## Two reported dynamics worth carrying

**Harness annealing.** Training *"internalizes recurring harness-use patterns
into the model policy and shifts the agent from frequent harness calls toward
selective external-state access."* The direction matters: the corpus's usual
answer to a recall failure is to retrieve more — wider *k*, more arms, hybrid
fusion. Here the trained agent calls the harness *less*. If that replicates, the
implication for a builder is that a well-shaped store plus a policy that knows
when not to consult it beats a better retriever.

**Harness evolution.** Progress updates and experience consolidation *"refine
the harness into a compact, task-adaptive state substrate."* Consolidation
judged by whether the task went better, rather than by a compression ratio — the
measurement the atlas asked for after GENOME published that its own
auto-consolidation collapsed accuracy fivefold at the shipped default.

Reported result: 96.9% on ALFWorld with Qwen3-8B.

## Three caveats

**The taxonomy cuts across this atlas's boundary.** Belief, Progress and
Experience as one "policy-facing harness state" merges three things the compare
page separates: a belief is a claim that can turn out false, progress is a run
record (*a store of the agent's work is not a store of the agent's beliefs*),
and experience is procedural. That is a reasonable move for a *control* problem
— the policy has to decide about all three — and it means a result about BPE as
a whole says nothing about the belief half specifically, which is the half this
atlas is about.

**The abstract names the three and does not define them.** Everything above is
from the abstract and the listing metadata; the method was not read.

**And there is no artifact.** No repository, no dataset, no benchmark URL in the
abstract or comments. So this stands where MemEvoBench and FiFA stand: a
research direction rather than a measurement, recorded by name so nobody
re-derives it, and unavailable to check.

## Why it is recorded rather than dropped

It is the most direct challenge in the literature to the thing every system in
the corpus does by hand, and the atlas has been accumulating the evidence for
the problem without naming the alternative. Folded into the hand-tuned-weights
passage on the [compare page](../content/overview.md) beside LivingFeed's
component-storing answer, as the far end of the same axis.

If code appears, the question to ask first is the one the abstract does not
answer: what does the learned policy do when the harness state is *wrong* — is
there a harness action for retracting a belief, or only for reading, updating
and consolidating it?

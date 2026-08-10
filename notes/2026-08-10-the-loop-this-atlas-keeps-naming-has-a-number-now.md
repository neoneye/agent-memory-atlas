# The loop this atlas keeps naming has a number now

**2026-08-10.** [arXiv:2608.00017](https://arxiv.org/abs/2608.00017), *Memory
Reward Inflation in Self-Improving LLM Agents*, submitted 29 June 2026 by
Mohammad Asadolahi, Amir Amini, Samira Talebi, Amirfarhad Farhadi and Azadeh
Zamanifar. No report, on the ordinary basis: the paper's own advertised
repository does not exist. It is recorded here anyway because it measures the
failure this atlas has named in report after report without ever being able to
price it.

## What it says

An agent that stores each episode with a score, and retrieves by similarity for
later tasks, is running policy improvement whose reward is that score. In
deployment there is no gold label, so the score is the model's own assessment of
its own output. The paper's claim is that this substitution is not merely noisy
but *directionally* biased in the worst available direction, and it gives the
failure two conditions rather than one:

- self-grades inflate wrong memories — `E[b_i | U_i = 0] > 0`, where the bias
  `b_i = r_i − U_i` is the stored score minus the true utility; and
- among wrong memories, inflation *couples to reuse* —
  `Cov(b_i, n_i | U_i = 0) > 0`.

The second condition is the one that matters, and it is what separates this from
"LLM judges are optimistic". A uniformly generous grader inflates everything and
changes no ordering. A grader whose confidence in a wrong answer predicts how
often that answer gets retrieved builds a store whose most influential entries
are its most confident mistakes. They call it the **Echo Gap**.

Measured on live self-graded banks: leniency — the probability the grader
endorses a wrong answer — is 31% for Claude Haiku 4.5, 54% for GPT-5.4-mini and
41% for frontier GPT-5.4, so it is not one family's artifact. On the BIRD run,
the observed corruption of the *trusted* bank (self-graded-correct memories that
are in fact wrong) settles at 0.42.

## Why a better judge does not fix it

The paper's central move is the **Error-Independence Assumption**: a verifier is
usable for de-inflation only when its error is decorrelated from the self-grade
bias *and* it tracks truth — `|Corr(ν, b)| < τ_dec` together with
`Corr(V, U) > τ_tru`, where `ν = V − U`. Proposition 2 makes this necessary
rather than descriptive: the recoverable payoff is a closed form in exactly
those two quantities, and where the verifier's error echoes the self-grade
strongly (β ≥ 1), demotion *worsens* the inflation at every step size.

That is the useful sentence for anyone building a memory system: **a stronger
re-grader from the same family is not a fix, because it is wrong in the same
places.** Their Table 3 bears it out — parametric re-graders failed the test;
the retrieval-grounded verifier passed it, at `Corr(ν, b) = +0.05` and
`Corr(V, U) = +0.76`.

There is a matching negative result about calibration. Global monotone
recalibration of the stored scores — Platt, isotonic, the usual kit — cannot
selectively repair the bank, because a monotone map preserves the ordering that
retrieval and trust actually consume.

## LUCID

The algorithm is deliberately small, and it is small in a way that is worth
copying. It never re-solves the task, never reads a reference answer, and makes
**no model call at all**. It reads the candidate episode's own inputs and
behaviour and flags on three channels: the query errors, times out, or returns
non-deterministic results across identical runs; it executes but returns empty
or all-NULL for a question that expects an answer; or it filters on an
entity-like string literal that does not appear in the question — *"a direct
fingerprint of a value copied from a different, wrongly trusted memory."* A
flagged memory's stored reward is demoted 1 → 0. Content is never overwritten.

Precision on the self-graded bank is 0.90 pooled (CI [0.875, 0.920], n = 649
flags) against a wrong-memory base rate of ≈0.46, clearing the paper's
break-even threshold of 0.5. Recall is low, and the paper says so and argues it
is harmless here — a de-inflation pass that misses wrong memories leaves the
status quo, while one that demotes right memories makes things worse. That
asymmetry is why precision is the governed quantity and recall is not.

End to end on the full BIRD development set (1,534 questions, official execution
accuracy, two seeds, identical planner/executor/retriever/prompts/task order
across arms, top-k = 4 SimCSE): no-memory control 52.4%, faithful Memento-style
self-graded memory 54.0%, LUCID 56.9%. Paired per-seed 95% intervals on the
LUCID − naive difference exclude zero in both. The memory-less control is the
right third arm and most papers in this space omit it.

**Appendix D is the part the [benchmarks page](../content/benchmarks.md) has
been asking for.** A rule that *demotes* rows is the case where a weak baseline
flatters you most, because dropping rows improves precision on almost any corpus
whether or not the rule picking them is any good. Table 7 answers it with a
budget-matched placebo: at LUCID's exact budget of 123 demotions, **random
pruning harms the bank** (ΔCorr −0.16) because it takes 13 of the 15 genuinely
correct memories, while LUCID demotes the same number with zero collateral and
gains +0.59. The comparison is repeated at 25/50/75/100% of the budget so the
budget cannot be the explanation. Confidence thresholding is reported as a
monotone no-op, self-consistency pruning recovers +0.06 while still demoting
correct memories, and clipping the retrieval similarity floor does nothing
because it acts on relevance rather than reward. Then it flags its own weakness
in the direction that weakens the finding: with 15 correct memories in the bank,
*"the '0 demoted' figure is a low-count estimate, and we read it accordingly."*
[Daimon](../content/systems/daimon.md) is the only repository in this corpus
shipping a placebo arm; this is the only paper.

## What the atlas should take from it

**The mechanism has a name and now a slope.** Agent error rises monotonically
with the corruption of the retrieved set, OLS slope κ ≈ 0.38, positive inside
every difficulty stratum — so it is not the confound that harder questions both
retrieve worse memory and are independently harder. Retrieval here is
similarity-only, so score-ranked retrieval mass cannot be the channel; what is
left is the planner trusting an inflated memory *more*. That is the empirical
form of a thing several reports here assert from code and none can quantify.

**It names the exact defence [Engram Alpha](../content/systems/engram-alpha.md)
states as a principle.** *"Exposure doesn't validate"* — retrieval stamping
`last_seen` for observability only, never for trust — is the refusal of
Condition 2. This paper is the measurement behind that design choice, arrived at
independently. The same failure is what the atlas records for
[Core Memory](../content/systems/core-memory.md) ("recall raises the class… still
a use signal feeding a trust field"), for [NOOA](../content/systems/nooa-memory.md)'s
myelination, and for the decay curves in
[Mnemopi](../content/systems/mnemopi.md) and [PowerMem](../content/systems/powermem.md).

**And it argues for separating memory writing from memory trust**, which is the
[trust state machine](../content/patterns/trust-state-machine.md) pattern with a
reward-lens justification rather than a hygiene one. Its closing
recommendation — *"audit stored episodes with decorrelated, answer-free
evidence"* — is [verify memory against its subject](../content/overview.md#verify-memory-against-its-subject) with
an added constraint the pattern page does not yet state: the check must fail
differently from the thing it checks. Every instance the atlas has recorded
happens to satisfy that (a git blob OID, a `os.path.exists`, an AST hash, a
line-multiplicity comparison — none of them a model), but the pattern page
frames model-free-ness as a cost concern and a degradation risk. This paper says
it is the load-bearing property, and gives the inequality.

## The artifact is missing

The paper states availability twice, in the present tense. A footnote in the
introduction: *"Code, data, and per-episode memory traces are available at
https://github.com/MohammadAsadolahi/Reliable-Memory-Agents-in-the-Wild."*
Appendix F repeats it more strongly: *"All code, per-episode memory traces,
exact run configurations, and result files are released at"* the same URL.

Checked 10 August 2026: the URL returns 404, and `GET
/repos/MohammadAsadolahi/Reliable-Memory-Agents-in-the-Wild` returns 404 while
`GET /users/MohammadAsadolahi` returns 200 with **48 public repositories**, none
of them this one and none matching *memory*, *wild*, *lucid* or *reliable*. So
this is not a dead account, a rate-limit artifact or a rename with a redirect —
it is an active account that does not contain the named artifact.

That decides the triage. The atlas's inclusion bar is inspectable code at a
pinned commit; there is none, so there is no report. It is worth stating
carefully what the absence does and does not undermine. It does not make the
theory wrong — the propositions are proved in Appendix B and stand or fall on
their own. It does not make the numbers wrong. What it removes is the ability of
a reader to check that the detector's three channels are what the prose says
they are, that the Memento re-implementation is faithful, or that the 0.90
precision figure comes out of the traces. This atlas separates a claim from an
artifact in exactly this way for
[Memvid, MemoryOS and FiFA](../content/overview.md#published-benchmark-numbers-without-committed-artifacts), and the shape here is the
same with one difference worth noting: those repositories exist and lack the
result files, whereas this result names a repository that does not exist. There
is no partial artifact to inspect.

A fair reading is that this is most likely a repository the authors intend to
publish and have not yet made public — the paper was submitted 29 June 2026 and
announced under an August identifier — rather than anything worse. Either way
the atlas records what is checkable today, and can re-check.

## Also worth noting

The paper carries **no limitations section**. It has an unusual amount of
self-scoping inside its appendices instead — the scope of the dynamical claim,
the generation-free retrieval-depth sweep showing the inflation is a property of
the grader rather than of k, the explicit note that the cross-vendor comparison
is *"not… an exact model leaderboard"* — which is most of what a limitations
section does. But a reader looking for the usual heading will not find one, and
two things a limitations section would have had to say are absent: n = 2 seeds,
and one benchmark in one domain, with the generality of the three answer-free
channels asserted by analogy in Appendix A rather than shown.

## Re-check

The one thing worth watching is whether the repository appears. If it does, this
is a report rather than a note: an implemented, model-free de-inflation pass
over a self-graded episodic store is squarely in scope, and the per-episode
memory traces would be the first published artifact in this corpus that lets a
reader watch a memory bank become corrupted.

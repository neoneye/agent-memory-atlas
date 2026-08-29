# The boundary is doing most of the work

**Status:** synthesis. Seven artifacts read between 22 and 30 August 2026 that
got no report, sorted by *why*. Written because the exclusions had started to
look arbitrary from outside, and they are not — but the reasons are four
different reasons wearing the same word.

---

## Why this is worth writing down

A reader who sees WikiSkill, Self-GC and FP-AMB all recorded as "examined, no
report" will reasonably assume one bar was applied three times. Three different
bars were. Sorting them makes the boundary legible and, more usefully, shows
which exclusions are permanent and which are a release away from reversing.

## 1. It stores nothing that could turn out to be false

The oldest and least negotiable bar. From the compare page: *the test that
separates it is whether the store holds anything that could turn out to be
false.*

**[Self-GC](https://arxiv.org/abs/2607.00692)** (Xiaohongshu) governs a run's
active context as indexed objects with fold, mask and prune lifecycles, keeping
the full transcript outside the active view. The authors place it *"complementary
to memory-store methods"* themselves. An event that was pruned still happened;
nothing in the store is a claim.

**`os-factory/har`** stores agent trajectory events, work units, validation
bindings and run records. Thirteen Prisma models, none of them a belief.

**`FP-AMB`** is a benchmark. A provider implements `ingest_turn` and
`retrieve_context` and the suite scores it; the suite itself remembers nothing.

**Perseus** (the context engine, not the Vault) writes checkpoints carrying
`stale_after` and `max_keep: 30`. A run record that ships with an expiry is the
cleanest case in the corpus of *a store of the agent's work is not a store of the
agent's beliefs*.

**These do not reverse.** Not because the work is lesser — three of the four are
better engineered than the median report — but because no release adds a
falsifiable claim to a store of events without becoming a different product.

## 2. It is model-internal, not agent-level

**[Short window attention](https://arxiv.org/abs/2509.24552)** (Meta FAIR) is
about what a hybrid sliding-window/xLSTM architecture learns to keep in its
recurrent state. That is memory, and it lives in weights and activations rather
than in a store an agent can scope, correct or forget. Same shelf as the KV
cache.

It produced the single best sentence of the week anyway, which is the argument
for reading outside the boundary rather than only patrolling it.

## 3. There is no inspectable code at a pinned commit

The only bar that is purely procedural, and the only one that reverses on its own.

**[WikiSkill](https://arxiv.org/abs/2608.27454)** separates raw execution
experience, accumulated knowledge and executable skills, and consolidates
experience into a wiki that later skill updates build on. That is in scope as a
*design* — it is a store of claims that can be wrong and are revised. It gets no
report because no code was released, and the atlas's unit is a mechanism read at
a commit, not a described architecture.

This is worth being honest about: **WikiSkill is excluded for a reason that has
nothing to do with the quality of the idea.** Its ablation is quoted on the
benchmarks page precisely because it is the measurement most of the corpus does
not make. If the authors publish the implementation, it gets a report, and the
exclusion entry that currently records it will read as a placeholder rather than
a verdict.

Compare Self-GC, which is *also* code-less: had it released code, it would still
get no report, because bar 1 applies. The two exclusions look identical in the
overview and only one of them is about code.

## 4. The memory is real and lives somewhere else

**`OpenHands/OpenHands`** was examined twice and holds a settings page, a
mutation hook and a `CondensationEvent` type mirroring a server contract —
including a `forgotten_event_ids` field it never populates. The memory is in
`OpenHands/software-agent-sdk`, which now has its own report.

The failure mode here is the reader's, not the project's: a repository whose
name is the product's name is not necessarily the repository the mechanism lives
in, and an organisation's archived repos are the fastest way to find out which
one is. Two archivings on one day explained the whole thing.

## What the four have in common

Nothing, and that is the point. The single phrase "examined and has no report"
is carrying a permanent architectural judgement, a scope-of-the-atlas judgement,
a procedural wait-for-code, and a wrong-repository correction. A reader
comparing two entries cannot tell which they are looking at unless the entry
says.

**The entries should say.** Every exclusion in `content/overview.md` names its
reason in the first sentence; what none of them says is *which kind of reason it
is*, and therefore whether it can change. That is worth fixing the next time the
exclusion list is touched — a `will not reverse` / `reverses on release` /
`wrong repository` distinction costs a clause and answers the question a reader
actually has.

## The related trap, since it cost two marks this month

Bar 1 applies **per mark**, not only per system. A repository can be in scope and
still have a mark awarded to the wrong half of it: OpenHands SDK was admitted
correctly and then given `audit_log` and `negative_eval` for machinery that
manages a context window, where an event cannot turn out to be false. The
admission test and the mark test are the same test, asked twice, and the second
asking is the one that gets skipped — because by then the reader is deep in the
best-engineered part of the tree, which is very often the part that is not
memory. See
[a memory you can route around](2026-08-29-a-memory-you-can-route-around-is-one-nobody-exercises.md)
for the evaluation half of the same problem.

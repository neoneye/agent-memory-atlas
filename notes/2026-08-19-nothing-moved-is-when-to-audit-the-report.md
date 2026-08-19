# "Nothing moved" is the cheapest report audit available

**Status:** method finding, one instance, argues for a change in what a
no-op re-read is *for*.
**Origin:** re-analyzing tokenmizer, where `HEAD` was already the pinned commit.

## The setup

The `reanalyze-memory-system` skill names three outcomes, and treats the first
as the boring one:

> **Nothing moved.** The mechanism is unchanged and no published claim is stale.
> Re-pin `revision`, `revision_url` and `analyzed_at` […] and say so plainly in
> a new History entry. This is a real result and worth recording.

That framing is right about it being a real result and wrong about what the work
*is*. On tokenmizer the tree was byte-identical to the pin, so there was no diff
to read — and the pass still produced five corrections, every one of them an
atlas error rather than a project change.

## What an unchanged tree is good for

When the commit moves, a re-read is dominated by the diff: what changed, does it
break a claim, did a criticism close. The report is the fixed thing and the code
is the moving one.

When the commit does *not* move, that inverts. The code is a fixed reference and
the report is the only variable. Every disagreement between them is yours. There
is no "the project changed it" available as an explanation, which makes the pass
unusually decisive — and it costs nothing to obtain, because the clone is
already sitting there from the freshness check.

## What it turned up

**A missing mark.** `negative_eval` was unawarded, and two committed cases
qualify — one driving a live-shaped `sk-ant` key through the real extraction
path and asserting it reaches no node's label or summary. The previous reading
had credited the ground-truth *retention* suite (recall floors of 0.4 and 0.33,
which is the report's headline) and never looked for exclusion assertions in the
files beside it. Finding a good eval seems to satisfy the urge to look for
evals.

**Two wrong line numbers, and not the kind I expected.** The skill warns that
line numbers are "pinned to the old commit and are the thing most likely to be
silently wrong after a re-pin" — i.e. the risk is *carrying them forward*. Both
of tokenmizer's were introduced by the previous day's reading, against files
that did not exist at the earlier pin. They were wrong when written. A cited
line number needs verifying because you *wrote* it, not because you inherited
it.

**Frontmatter contradicting itself.** `memory_unit` said eight statuses;
`trust`, four rows below, said nine. `NodeStatus` defines nine. A previous pass
had updated one row and not the other, and both are published — one in the
report header, one in the comparative matrix.

**A claim living in the verdict with nothing behind it in the report.** This is
the one worth generalising. `content/verdicts.md` closed on *"every clock is a
record clock"* — a sharp, correct observation. The report named no clock at all.
So the atlas asserted something a reader could not check against the report that
is supposed to carry the evidence for it.

The producer check then made it concrete and better: `query_at_time` walks
`valid_from` / `valid_until`, `valid_until` is stamped at supersession, and
**`valid_from` has no producer anywhere in the repository** — never assigned
outside its `default_factory=time.time`, so it always equals the `created_at`
beside it. The tree even disagrees with itself about the field: the type
comments it *"when this fact became true"*, the query docstring says *"when the
node was created."* The second is what the code does.

## The rule

A re-read at an unchanged commit is not a re-pin with paperwork. It is a
**report audit against a frozen reference**, and it should run a fixed list:

1. Re-verify every cited line number, including ones added at the last reading.
2. Re-run the producer check on every capability mark, and on every mark
   *withheld* — a withheld mark with no stated reason is where a missing mark
   hides.
3. Read the report's frontmatter rows against each other, not only against the
   code.
4. Read the verdict beside the report and check that every verdict claim has
   something in the report behind it.
5. Grep the test tree for negative assertions specifically, separately from
   whatever eval the report already praises.

## The structural point

Items 3 and 4 are not about any one system. The atlas publishes each reading
through several surfaces — report frontmatter, report body, comparative matrix,
verdict, homepage card — and the build binds *counts* across them and nothing
else. Two surfaces can disagree about a fact, or one can carry a claim the other
cannot support, and every check stays green.

See also [evidence records rot, and only a re-read finds
it](2026-08-19-evidence-records-rot-and-only-a-re-read-finds-it.md), which is
the same class of decay at a *moved* commit; this is its counterpart at a
stationary one.

# Questions the existing corpus can already answer

**Status:** open, none attempted
**Origin:** noticed while building the capability index — 58 commit-pinned
reports with structured frontmatter is a dataset, and it has not been queried as
one.

Everything here needs **no new reviews**. It is analysis of material already
committed, which makes it cheap relative to anything else in these notes.

## 1. Which capabilities co-occur?

The `capabilities:` frontmatter across 58 systems supports a co-occurrence
matrix, and nobody has computed one. Specific hypotheses worth testing:

- **Does `trust_state` predict `human_review`?** A system that models epistemic
  status plausibly also gives someone a way to adjudicate it. If the correlation
  is strong, the two are one design decision and the rubric is double-counting.
- **Does `audit_log` predict `tombstone`?** Both come from taking correction
  seriously; if they never co-occur, that is a more interesting finding.
- **Is any capability isolated** — present only in systems carrying nothing else?
  That would suggest it is cheap and unrelated to the rest, which would change
  the advice about build order in the smallest-serious-stack section.

## 2. Test the descent hypothesis inside the corpus

The atlas's central claim is that systems build the ascent and skip the descent.
There is a sharper, falsifiable version available:

> **Systems with automatic background derivation are less likely to carry a
> tombstone than systems without.**

The reasoning is that re-derivation is what makes a tombstone necessary, so the
systems that most need one are the ones that have it least. Both variables are
extractable — `background` is already a matrix column, `tombstone` a capability
flag. If the correlation is *positive* instead, the atlas's framing is wrong in
an interesting way and should say so.

## 3. Are the two tombstone systems independent?

[Verel](../content/systems/verel.md) and [RainBox](../content/systems/rainbox.md)
are the only two. Whether they arrived at the mechanism independently or share a
lineage changes what the count means: two independent inventions suggest the
idea is discoverable, while one influencing the other means the field has
produced it once.

This matters because "two of fifty-eight" is the atlas's most-quoted number and
its interpretation depends on the answer. RainBox is the author's own system,
which makes the question awkward and worth asking anyway.

## 4. Does capability count track anything?

Age, size, whether the project is commercial, whether it has funding. The
`analyzed_at` dates and repository metadata are already collected by
`check_freshness.py`. Plausible and untested: capability count tracks **age of
the memory subsystem** rather than size or backing — mechanisms get added after a
failure teaches you they were needed.

If true, it reframes the negative findings: the field is not careless, it is
young, and the atlas is measuring maturity rather than quality.

## 5. What does the drift data say about the field?

The first freshness run gave 34 current, 22 stale. Running it monthly produces a
time series: which systems are actively developed, which have frozen, and whether
memory subsystems specifically churn faster than their host projects. That is a
public-interest dataset nobody else has, and it accumulates for free now the
script exists.

## 6. Do the near-misses cluster?

The rubric's strictness produces a specific list of systems that *almost* carry
each capability. If near-misses cluster around one flag, that flag's definition
may be drawing the line in the wrong place — a definition that many systems
narrowly miss is either measuring the right rare thing or measuring badly, and
which one should be established rather than assumed.

## Method note

All six are computable from `content/systems/*.md` plus the freshness data. None
requires standing up a system, running a benchmark, or asking a maintainer. Given
that the notes elsewhere describe expensive future work, this is the cheap pile
and it should probably come first.

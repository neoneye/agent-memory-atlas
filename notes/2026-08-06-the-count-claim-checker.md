# The count-claim checker — thirteen stale numerators in one day

**Status:** written and wired into `test_site.sh` as
`scripts/check_claim_counts.py`. This note is the postmortem; it was Part 4 of
the [rare-mechanisms note](2026-08-06-rare-mechanisms-and-useful-inversions.md)
until that note's own review pointed out that a development diary was crowding
out its subject.
**Origin:** [hazard 10](2026-07-28-methodology-hazards.md) and
[the superlative audit](2026-08-04-the-superlative-audit-first-pass.md), which
proposed this check and then did not write it.

## The gap

`check_homepage.py` guards the **denominator** — the corpus total — because a
file count derives it. Nothing guarded the **numerator**, and the numerators are
the atlas's headline findings. "Nine systems of one hundred and fifty-five carry
a tombstone" is the most-quoted sentence this project has.

## Four found by hand

Found while assembling a different note, all in `content/overview.md`:

| Line | Was | Live |
| --- | --- | --- |
| 61 | 148 reports / 147 repositories | 155 / 154 |
| 115 | "Seven systems" carry a tombstone | Nine |
| 1545 | "filters all 148 systems" | 155 |
| 3816 | "Across one hundred and fifty-four systems" | fifty-five |

The 155/154 pair is counted from frontmatter: 155 report files, 154 distinct
`source_url` values, the single duplicate being `NousResearch/hermes-agent`. The
paragraph's *argument* was right and both its numbers were a vintage behind.

## Eight more found by the checker

First run over `content/`: 15 claims bound, **8 wrong** — more than half.

| Where | Said | Live |
| --- | --- | --- |
| `capabilities.md:58`, `overview.md:1817` | seven systems carry a value-level tombstone | nine |
| `capabilities.md:65`, `overview.md:1829`, `benchmarks.md:562` | twenty-nine assert material must not be retrieved | thirty |
| `overview.md:2429` | three repositories implement a value-level tombstone | nine |
| `aukora-kernel.md:64` | closer on privacy than the three systems that earn it | nine |
| `project-golem.md:70` | three systems carry one, "here is a fourth answer" | nine |

Two needed a rewrite rather than a number. Aukora's sentence now says *a
value-keyed tombstone must retain the wrong value*, because the count was doing
no work there. Project Golem's "here is a fourth answer" became "another answer",
since its own report explains at length that it is **not** a tombstone.

## And one the checker missed, found by a reader the same day

[`overview.md:104`](../content/overview.md) read *"the atlas's headline counts —
three tombstones, six negative-eval suites"*. Live: nine and thirty. Stale by six
and twenty-four, **in the paragraph that explains what the atlas's headline
counts mean.**

The checker walked past it because a claim had to carry an atlas noun (*systems*,
*reports*, *repositories*) or the corpus denominator, and *"three tombstones"* is
neither — the mechanism was the countable noun. That form is now bound directly,
which took eight lines and immediately produced five false positives: "four scope
keys" (EverOS) and "three trust states" count things *inside* one system. So the
mechanism-as-noun rule is restricted to the two mechanisms whose plural is never
a within-system quantity — a tombstone and an eval suite — and the exclusion is
written into the source.

## What the checker does

Finds a number that counts atlas nouns or names the corpus total, binds it to one
of the seven rubric mechanisms named **in the same sentence**, and compares it
with the live count from report frontmatter. Sentence-bounded windows both ways;
markdown emphasis and hard wraps normalised out with offsets preserved, so line
numbers stay true; generated blocks and `systems-index.md` blanked, because
checking derived numbers proves nothing and would inflate its own coverage
figure. A table row is a boundary, not every cell wall — splitting on `|` left
`benchmarks.md:562` unchecked, and it was stale.

**Three limits, stated rather than implied.**

- It only checks what it can bind: 16 of the ~130 count-shaped phrases in
  `content/`. `--list` prints the rest, so the gap is visible.
- It cannot resolve a pronoun subject — *"nine systems carry **it**"* stays
  unbound. That is also what keeps it away from the invention-chain numerators on
  the tombstone pattern page, which need a re-reading rather than an edit.
- Zero bound claims exits **non-zero** with `NOTHING BOUND`. If a prose rewrite
  moves every claim out of reach, a green run would have verified nothing.

**It has a negative control.** `--self-test` builds a two-report fixture where
exactly one carries a tombstone and asserts three outcomes: correct count passes,
wrong count fails, nothing-bound fails. `test_site.sh` runs the self-test
*before* the real check, so a checker that can no longer fail breaks the build.
This is [Cambium](../content/systems/cambium/)'s rule applied to the atlas's own
tooling — a check that cannot demonstrate failure is not evidence of success.

## What the thirteen have in common

Every one is a considered editorial judgement about the field, written once and
never re-derived, sitting on a page whose neighbouring numbers are generated from
frontmatter and therefore correct. **A reader cannot tell the two apart** — a
spelled count and a generated one look identical — so stale prose inherits the
credibility of the machinery beside it. That is the same shape the superlative
audit found in the denominator sweep, from the other direction: there, bumping
denominators made stale numerators look fresher.

A hand-written count is a claim with a shelf life. Until today nothing in this
repository knew that, and the checker now knows it for 16 sentences out of about
130.

## Follow-ups

- Raise coverage by giving the pronoun cases a subject, rather than by teaching
  the checker to guess. Rewriting *"nine systems carry it"* to name the mechanism
  is a prose fix that makes the sentence better and checkable at once.
- `list_superlatives.py` reports **320** corpus-scoped superlatives. The
  ten-checkable/284-judgement split was taken at 136 reports and needs
  re-deriving; some of today's 320 are now mechanically checkable that were not.
- Nothing checks note files. Two of the corrections above were first published in
  `notes/`, which the build does not read.

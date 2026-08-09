# The receipts the atlas cannot produce — a downstream-changes page, and the firewall it needs

**Status:** proposed, with a feasibility probe already run against four reports
**Origin:** a Codex conversation (2026-08-09) recommending an "impact ledger".
The stronger argument for building one is five days older and is about a failure
rather than an achievement.

**Sequencing:** phase 1 of
[the phased program](2026-08-09-a-phased-program-and-where-to-abandon-it.md),
with the firewall shipping in the same commit as the page rather than after it.
Its gate is Daimon's row reading visibly as `inferred`; if it cannot be made to
look different from Perseus's at a glance, the page asserts causation and should
not ship.

## The argument that is not about impact

On 4 August a favourable review closed with this:

> the fact that 5 open-source maintainers immediately merged code based on your
> rubric proves that the industry was starving for exactly this level of
> structural rigor

Nothing in `content/` or `notes/` supported it. The
[note that took it apart](2026-08-04-a-third-review-and-the-second-invented-quotation.md)
found that no report, verdict or note recorded a single upstream maintainer
acting on an atlas review, and that the nearest real thing was the atlas adopting
its own machinery in `neoneye/RainBox`. The only adoption the project could
evidence was self-adoption.

That is the case for this page. Not that the atlas has been influential —
influence is the reason the sentence was *tempting*, not the reason it was
unanswerable. The atlas could not check a factual claim about itself, in a
project whose entire method is checking factual claims. It got refuted by a grep
only because someone thought to run the grep.

Five days later there are at least four real cases and the atlas still cannot
produce the list.

## The data mostly exists, unevenly

It is in the `## History` sections. Perseus Vault's is a fully worked example of
what a row should contain, written before anyone proposed a ledger: it names the
upstream commit titled *"implement Atlas review follow-ups"*, states that each
closed issue was verified against code rather than against the commit message,
and then bounds its own attribution in two directions — the report carried all
seven marks *before* those commits so no mark could have been bought, and the
commits carry the project's own issue numbers, which is evidence of an internal
plan rather than of a checklist.

A probe across four reports shows how uneven the rest is:

| Report | What the History section actually says |
| --- | --- |
| Perseus Vault | Explicit — an upstream commit titled after the review, each closure re-verified against code |
| memsem | Explicit — a pull request the project's author opened *against this atlas*, plus two mechanism details taken from it and verified before use |
| Verel | Explicit as method adoption — `memory/rubric.py` grades the project against this atlas's capabilities with a live probe per criterion; the note also records that marks moved 3→7 and that four atlas-wide counts moved with them |
| Daimon | **Nothing attributable.** The capability count and the deletion design moved, and the History section makes no atlas claim. Any row for Daimon is inferred from timing and content, or it is nothing |

Daimon is the useful case, because it is the one where an enthusiastic page would
quietly assert causation the report never claimed.

## Design

**Generated, not hand-kept.** A hand-maintained list of this kind drifts, and
this project has the receipt: the published repositories-inspected list had
drifted on three systems, and every one of the three was a system the project had
re-reviewed — the touch is what broke it.

**Attribution labelled, three values.** `explicit` — the upstream says so in a
commit, issue or PR. `inferred` — timing and content line up, nobody said so.
`unknown`. Daimon's row is `inferred` and must render as visibly different from
Perseus's, not as a footnote.

**Atlas retractions are rows.** The Perseus scoping claim that was wrong at the
pin it was made on. The memsem mechanism details taken from a maintainer's PR.
The tool-count finding corrected after the project's author reviewed it. A page
carrying only inbound changes is a trophy case; a page carrying both is a record
of a two-way process, which is the accurate description and also the more useful
one.

**No headline count, no ranking, no "impact" in the title.** *Downstream
changes* is what it is.

### The firewall

**This page is evidence about the atlas. Nothing on it may be cited in a report
as evidence about a system.**

Same rule as stars, same reason, and it needs saying explicitly because the
temptation is sharper here — a maintainer who responded to feedback feels like a
better engineer, and that inference is exactly as unfounded as reading quality
off a star count. The atlas has a
[standing rule](2026-07-30-a-reddit-thread-triaged.md) against adoption as
evidence and a note explaining what it cost to learn. A responsiveness metric is
adoption evidence wearing a lab coat.

If the page is built, `scripts/` should enforce the firewall the way
`check_claim_counts.py` enforces generated numbers — a report citing the
downstream page fails the build.

## The extraction problem, and the recommendation

History sections are prose. Two ways to generate from them:

- **Parse the prose.** No per-report cost, and it will drift the first time a
  History paragraph is phrased differently — which the four-report probe above
  shows is already the norm.
- **A `downstream:` list in report frontmatter**, shaped like
  `capability_evidence`: upstream commit URL, date, attribution level, one
  sentence on what changed. Costs a few lines per affected report, of which there
  are currently a handful, and is checkable.

Recommend the frontmatter field, with the generator refusing to build a row whose
commit URL does not also appear in the report body. That reuses the pattern
`check_capability_evidence.py` already establishes: the structured field is an
index into prose that carries the reasoning, never a replacement for it.

## What this is worth

Modest, and worth being honest about. It preserves evidence that will otherwise
dissolve into commit logs and chat history; it makes the next inflated claim
about the atlas answerable in one place instead of by grep; and it is the only
artifact on the current list that is a day's work rather than a project.

It does not make the atlas more correct, and it should not be built in the belief
that it does.

# The compare page reviewed as a tool rather than as writing

**Status:** every measurable claim verified, two fixed today, the redesign staged
with a decision the atlas has to make first
**Origin:** a Codex review of
[the comparative report](https://neoneye.github.io/agent-memory-atlas/compare/)
submitted 2026-08-04, assessing it as an interface rather than as prose.

Recorded because it is the first external review of this project that **measured
something**. Every previous one argued about content; this one counted headings,
measured a table, and named a font size. That makes it the only review so far
whose claims could be checked the way the atlas checks a repository, so they were.

## The measurements, verified

| Claim | Reviewer | Measured |
| --- | --- | --- |
| Article length | ~86,600 words | **89,689** |
| Headings | 226 | **225** |
| Links | 758 | **787** |
| Matrix shape | 133 × 12 | **136 × 12** |
| Filter/search/sort on the matrix | none | **none** — zero filter controls in the rendered page |
| Sticky first column | absent | **absent** — `.site-header`, `.toc` and `.prose th` were sticky; no column was |
| Consent banner emphasis | "Allow" stronger | **confirmed** — `class="is-primary"` on Allow only |

Every claim holds. The three discrepancies are all in the direction of the page
having grown since the review: 133 systems became 136 the same day, which
accounts for the word and link deltas. **A review of this project can go stale in
under twenty-four hours**, which is the reviewer's own point about layering
arriving from an unexpected direction.

## Fixed today

**The first column is now sticky.** The matrix is roughly 2,162px wide against a
1,280px viewport, so horizontal scrolling used to carry away the one column that
says which system a row describes — every other cell became unattributable. The
fix is eight lines of CSS pinning `th:first-child` and `td:first-child`, with the
corner cell raised above the header row or the label disappears underneath it.
This was the highest-value item in the review and the cheapest.

**The consent choices now carry identical weight.** `Allow` had
`class="is-primary"`; it does not any more, and the CSS carries a comment saying
not to reintroduce it. The reviewer framed this as the banner competing with the
matrix; the stronger reason is that a site whose Consent Mode denies everything
until the reader chooses should not then style one choice as the recommended one.

## Not fixed, and the reason

**The redesign proposal is good and it is not one decision.** Search, filters,
a column chooser, side-by-side selection, URL-preserved state, CSV export,
splitting `/compare/` into a workspace and a `/report/` — each is defensible and
together they are a different product from the one this repository builds today.
Three things have to be settled first, and none of them is a UI question:

1. **Normalized badges require normalized data, and the atlas deliberately has
   none.** The reviewer's fourth problem — "the cells are reports disguised as
   data" — is exactly right as a description and is the design. The `matrix:`
   frontmatter block holds prose per system because eleven of the twelve columns
   were never assessed against a fixed vocabulary. Turning them into badges means
   inventing a vocabulary and back-filling 136 reports against it, which is the
   proposal [declined in July](2026-07-28-declined-proposals.md) as "inventing
   boolean columns to fill out a matrix". The seven columns that *were* judged
   against strict definitions already have a filterable page:
   [capabilities](../content/capabilities.md), which filters with **and**
   semantics and is generated from the same frontmatter. That page exists and the
   review did not find it — the second reviewer in two days not to, which is a
   navigation finding rather than a coincidence.
2. **A filter over prose cells is a search box, not a filter.** Search by system
   or repository is cheap and worth doing on its own. Filter by "storage" is not,
   until storage has values rather than sentences.
3. **Splitting the page changes what a URL means.** `/compare/` is cited from
   outside this project. Moving the long-form argument to `/report/` is right and
   needs a redirect story, which is the same convention already used for renamed
   systems.

**The layering diagnosis is the part to keep.** "The next design step is not
adding information; it is creating stronger layers between overview, comparison,
evidence, and history" is correct, and today's work is an instance of the
opposite reflex — three reports were added to a page already at 89,000 words
without anyone asking whether the page should hold them.

## What to do, in order

1. **Search by system name on `/compare/`.** **Done.** A single input above the
   matrix filtering rows on the first column, with a live count, reusing the
   `.filter-row` conventions so the compare page and the capability index read as
   one control family. Name-only on purpose, and the source says why: filtering
   on the other eleven columns would imply they hold values rather than
   sentences.
2. **Link the capability index from the top of the matrix.** **Done.**
3. **An executive summary above the hero.** **Done** as an `In Short` section
   opening the page: five findings each stated with the live count it rests on,
   corpus size and freshness date, and three actions. Writing it surfaced a
   fourth stale count — the page claimed 135 reports across 132 repositories
   where the figures are 136 and 135.
4. **The split, done in the one place it was safe.** Section 9 —
   136 repo-by-repo verdicts, 1,256 lines, the single largest block on the page —
   is now [`/verdicts/`](../content/verdicts.md). The compare page went from
   89,689 words to 69,052, a 23% cut, by moving one self-contained product rather
   than by restructuring.

   **`/compare/` keeps its URL and every anchor.** It is cited from outside this
   project, so moving the *comparison* off it would have broken exactly the links
   most worth preserving. The section heading stays in place as a stub pointing at
   the new page, which keeps `#9-repo-by-repo-verdicts` resolving and stops
   sections 10 and 11 renumbering — a renumber would have broken seventeen inbound
   anchors from `content/` for no reader benefit.

   **What is still one page:** the taxonomy at 1,187 lines and the lifecycle
   comparison at 710. Those are load-bearing for the argument in a way the
   verdicts were not, and splitting them is a genuine editorial decision rather
   than a mechanical one. The remaining proposal items — column chooser,
   side-by-side selection, URL state, CSV export — still depend on the
   normalization question, which is declined above and unchanged by this split.

## What came of it

- **Two defects fixed** — the unattributable rows and the weighted consent
  choice.
- **Seven measurements verified**, the first time an external review of this
  project has offered any.
- **One proposal declined for a stated reason** rather than deferred: normalized
  badges need a vocabulary the atlas has refused to invent, and the seven columns
  that have one are already filterable elsewhere.
- **One navigation finding**, corroborated: two consecutive reviewers asked for
  the capability index without finding it.

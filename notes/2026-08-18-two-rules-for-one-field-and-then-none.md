# The A–Z index: two rules for one field, and then none

**Status:** decision, with a layout constraint worth not rediscovering.
**Origin:** *"the a-z list hurts to read for my human eyes… a-mem is mentioned 3
times in the a-mem row."*

## The measurement that settled it

The row was `slug · **Title** — eyebrow · repo · marks`, one flowing Markdown
list item. The complaint was that the name appeared three times. It was not an
unlucky row: **279 of 301 rows had the slug, the title and the repository name
resolving to one identity.** On 93% of the page, two of four fields were dead
weight in front of the one field that differs between rows.

Measuring first mattered. The instinct was "some rows are redundant"; the answer
was "almost all of them are", which is a different fix.

## Two rules, both wrong, and then the field went

**Rule one: print the slug where a find-in-page for it would not land on the
row.** Wrong in both directions at once, and it took a reader about a day to see
it. It printed the slug on 17 rows where the title *was* that word and only the
punctuation differed (`brain-md` under `brain.md`, `terse-memory` under `TERSE
Memory`) — a URL cannot hold a dot or a space, and that difference belongs to the
slug, not to the system. And it withheld the slug on 18 rows where the title is a
different name (`Google ADK` and `adk-python`, `Hats` and
`one-agent-many-hats`), because the string was legible inside the repository path
three columns away. The page's own opening sentence cited Google ADK as *the*
example of a printed slug, and that row printed none.

The cause: the test asked a question about the **row** (*could a reader find this
string here*) when the page's question is about the **name** (*would this name
surprise a reader here*).

**Rule two: compare the slug to the title alone, punctuation stripped.** Correct
on every case, locked with controls in both directions — the containment pair
(`Hats`/`one-agent-many-hats`, `fidelis`/`Fidelis Memory`) is the one that
matters, because a substring test passing either means the rule has slid back to
asking whether the string is on the row.

**Then: delete the field.** *"the `<code class="az-slug">jumbo</code>` these are
noise, remove those blocks."* Even the correct rows read as noise. The rule, its
controls and the test hook went with it.

**The lesson worth keeping: a field that needs a rule to decide whether to show
it is usually a field that should not be shown.** Two rules were written, one was
wrong, one was right, and both were the wrong shape of work. The signal was
available at the first measurement — 279 of 301 — and was read as "make the
rule smarter" instead of "the field is redundant."

## What removing it cost, and the second-order change

Find-in-page can no longer match a slug that appears in neither title nor
repository path — `agent-memory-doctrine`, `neko`, `recall-substrate`,
`sovereign`. Every row's `href` is still the slug.

And it forced a change nobody asked for at the time: the page had **sorted by
slug** on the argument that the slug is what a reader types. With the slug
invisible, the letter headings were keyed to a string nobody could see, so
`Google ADK` sat under A and `Hats` under O — about seven rows reading as
misfiled against the only column a reader can check the order against. Now sorted
by title, uppercased with the slug breaking ties. Uppercasing rather than
stripping punctuation preserves space-before-letter ordering, so `Agent Memory
Techniques` precedes `agentmemory V4` — word by word, which is how a column of
names is scanned.

## The layout constraints, so they are not rediscovered

Three are repo-specific and cost real time to find:

1. **Not a `<table>`.** `scripts/build_site.sh:158` wraps every `<table>` in a
   `.table-wrap` scroller and `assets/main.js` hangs an expand toggle off each.
   Each letter is its own list, so a table per letter is 27 horizontal scrollers
   with 27 toggles. The A–Z uses a grid of list items instead.
2. **Fixed column units, not content-derived.** Because each letter is a separate
   `<ul>`, `auto`/`max-content` columns align *within* a letter and disagree
   *across* letters — 27 sets of edges down one page, which is the ragged effect
   the redesign replaced. Fixed rem units make all 301 rows share one set of
   edges by construction. Verified on the built page: one x-position per column,
   across every row.
3. **820px is a reading measure for paragraphs, and four columns do not fit it.**
   Squeezing them in left the description column ~40px. A page that is a
   *directory* rather than an *argument* opts out with `layout: wide` in its
   frontmatter, handled in `build_site.sh` and scoped to that page — every other
   page's HTML is byte-identical.

The four-column form is an enhancement above 1354px, not the default: the
threshold is arithmetic (230px table of contents + 72px gutter + 56px padding, so
the prose track is viewport − 358; four columns cost 716px of fixed width and the
description needs ~280px). Below it the name keeps its own column and the rest
stacks beside it, which preserves the one edge a reader scans down.

## The click target

The row's link was the name alone — a word or two at the left edge of a 1080px
row, on a page whose entire job is getting a reader from a name to a report. Each
row is now a single `<a>` with the four columns inside it. A stretched-link
overlay would do the same and cost the row its text selection; the anchor-as-row
keeps one tab stop per row and lets the focus ring outline what the click hits.
Verified by hit-testing seven points across the full width at 1500px and four
corners at 1100px and 375px, including a row with no capability pills where the
right two-thirds is empty space.

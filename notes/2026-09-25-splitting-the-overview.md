# Splitting the overview: what moves, and which page keeps the name

**Status:** decided on 2026-09-25: option B, with the synthesis at
`/overview/`, and implemented the same day. The measurements below describe
the page before the split. This note is Task 7 of the
plan in
[2026-09-25-written-to-be-checked-not-yet-to-be-read.md](2026-09-25-written-to-be-checked-not-yet-to-be-read.md#implementation-plan).
Every figure below was measured on 2026-09-25 against the tree at
`65994d5a3`.

`content/overview.md` renders to **`/compare/`**. It holds three different
kinds of page in one file: a synthesis a builder reads in order, a generated
table, and two registers that grow with every report. The synthesis is the
part `AGENTS.md` sends a builder to (§8 and §10). It comes after about
340,000 words of the other two.

## What is in the file

| Section | Words | What it is |
|---|---|---|
| In Short, Reading This Report | 2,221 | synthesis |
| §1 High-Level Taxonomy | 91,092 | 13 family subsections of hand-kept paragraphs, one per system |
| §2 Comparative Matrix | 221,181 | 218,049 generated from `matrix:` frontmatter between markers, 1,482 generated capability tables, 1,650 hand-written |
| §3–§10 | 29,262 | synthesis: lifecycle, hotspots, patterns, antipatterns, what works, what to build, checklist |
| §11 Appendix | 74,744 | Known Limitations 52,926, Repos Inspected 20,661, licences 434, individual reports 643, commands 77 |
| History | 9,803 | the method's log |

Three observations decide the shape.

- **§2 is not restated prose.** It is the frontmatter rendered as a table, and
  it is what the page's URL and the homepage's *Open the comparison* button
  promise. It belongs at `/compare/`.
- **§1 is the corpus restated.** Each family paragraph re-summarises one
  report, usually opening with the report's census. It is also a second copy
  that drifts: PLUR's paragraph said *six of seven marks* for six days after
  the report withdrew one, and nothing checks it (Known Limitations, 2026-09-25
  entry).
- **§11 is two registers.** Known Limitations is the correction log that
  `remove-meta-narrative` names by its path. Repos Inspected is the list
  `check_inspected_pins.py` parses.

## Links that point into it

Every page that links into the overview uses `compare/#<id>`. There are 55
such links from other pages, and 31 links inside the overview cross from one
section to another.

| Target section | Links from other pages |
|---|---|
| §6 Antipatterns and Failure Modes | 14 |
| §11 Appendix | 11 |
| §1 High-Level Taxonomy | 9 |
| §5 Design Patterns That Recur | 5 |
| §3 Lifecycle Comparison | 3 |
| §2 Comparative Matrix | 2 |
| History | 2 |
| §8, §10, Reading This Report | 1 each |

Of the 31 internal cross-links, 11 run from the Appendix into §1. Five run
from In Short into §1, §2, §3, §6 and §11.

A fragment cannot be redirected by a static server. When a section moves,
each link to it must be rewritten, or the old page must carry a small script
that maps a known id to its new URL. `check_anchors.py` fails the build on any
rewritten link that points nowhere.

## What reads the file by path

| Reader | What it takes |
|---|---|
| `scripts/build_site.sh:148` | renders the file to `compare/index.html` |
| `scripts/generate_matrix.py` | writes the matrix and capability tables between its markers |
| `scripts/test_site.sh:278` | counts matrix rows in the file |
| `scripts/test_site.sh:673` | relative-date grep over the file |
| `scripts/check_inspected_pins.py` | parses the Repos Inspected list |
| `scripts/check_history.py` | checks the file's History ordering |
| `check_claim_counts.py`, `check_homepage.py`, `check_protocol.py`, `list_unchecked_absences.py`, `list_inert_recorded_commands.py` | one reference each |
| `AGENTS.md`, `use-the-atlas`, `add-memory-system` (7 references), `remove-meta-narrative` | name the path and its section numbers |

## Three options

**A. Move §1 and §11 out; the synthesis and the matrix stay at `/compare/`.**
This needs 20 external links and 23 internal ones rewritten. The page drops
to about 262,000 words. It does not do the one thing the split is for: the
218,000-word matrix still sits between *In Short* and §3–§10.

**B. `/compare/` becomes the matrix, and the synthesis gets its own page.**
The matrix and capability tables move to a new `content/compare.md`, which
renders to `/compare/`. `content/overview.md` keeps its path, and with it
every reference in `AGENTS.md` and the skills. It becomes the synthesis page:
*In Short*, *Reading*, §3–§10 and History, about 41,000 words, rendered to
`/overview/`. §1 moves to `/families/` and §11 to `/appendix/`. That means
rewriting 53 of the 55 external links (every one except the two into the
matrix) and 26 internal links that end up crossing pages. The ids that move
also go into a fragment map on `/compare/`, for links from outside the
repository.

**C. Reorder only.** Put §8 and §10 after *Reading This Report* and leave
everything else where it is. This needs no link rewrites and no script
changes, and it fixes the build order at once. The costs: section numbers
change, and so do the ids built from them (`#8-what-i-would-build`). The page
is still 428,000 words, and §1 is still a second copy of the corpus.

## Recommendation

**B.** It is the only option where each URL holds one kind of page. The
matrix answers *compare*, the synthesis answers *what should I build*, and the
registers answer *what was read and what was wrong*. Keeping
`content/overview.md` as the synthesis file keeps the builder's path in
`AGENTS.md` unchanged. Most of the script changes are one-line path moves.
`generate_matrix.py` and `test_site.sh:278` follow the matrix into
`compare.md`, and `check_inspected_pins.py` follows Repos Inspected into the
appendix file.

C is the fallback if the fragment map is judged not worth its cost. It fixes
the reading order for a builder and nothing else.

## What B would take

1. Move the file content. §2's hand-written 1,650 words go to
   `content/compare.md` with the markers. §1 goes to `content/families.md`
   and §11 to `content/appendix.md`. Section numbers in the synthesis stay as
   they are, so `§8` and `§10` keep meaning what `AGENTS.md` says.
2. `build_site.sh` renders the four files. `generate_matrix.py`,
   `test_site.sh:278` and `check_inspected_pins.py` change paths.
   `check_history.py` keeps reading `overview.md`, which keeps History.
3. Rewrite the 53 external links and 26 internal links that change page, driven by an
   id-to-page map built from the four files' headings. The build fails on any
   link left pointing at an id its page no longer has.
4. Add a fragment map on `/compare/` for the moved ids, generated by the same
   map, so a link from outside the repository lands on the right page.
5. Text: the *Integrate the comparative overview* section of
   `add-memory-system` names three files instead of one. `remove-meta-narrative`
   names `content/appendix.md` for Known Limitations. The homepage's *Open the
   comparison* still points at `/compare/`, which is now what it says.

Reversing it is one revert. No sentence is rewritten, only moved, and the map
records every id that changed page.

## What the split does not fix

§1's family paragraphs still restate the reports, census first. Once the
header band exists on every report, the families page could render each
system's census from `licence`, `size` and `activity` instead of repeating
it by hand. That would close the drift the PLUR entry records. It is a
separate change, and it waits until enough reports carry the fields.

## What was built

B, as described above, with `/overview/` for the synthesis because it matches
the file path every instruction already names. Three details differ from the
plan:

- **Headings on the new pages were promoted one level**, with their text
  unchanged, so every id is the id it had on `/compare/`. The map in
  `assets/main.js` covers 104 ids; `check_moved_anchors.py` verified all 104
  against the built pages, and the build and tests passed.
- **`#2-comparative-matrix` stays on `/compare/`** as an explicit anchor at
  the top of the page, so the one old fragment that means the matrix does not
  fall through to the verdict redirect.
- **The redirect also runs on `hashchange`.** A hash typed on an open
  `/compare/` page does not reload it, and the first version missed that case.

Twelve links had no fragment and meant a part of the old page rather than the
table. Each was re-pointed by what its sentence refers to: the inclusion rule,
a scope boundary, the known limitations, or the report as a whole. Prose that
located things on the old page ("the matrix below", "the limitations at the
end", "the scope section above") now links the page it means.

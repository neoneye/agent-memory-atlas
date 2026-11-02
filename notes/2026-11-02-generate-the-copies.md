# Generate the copies — one place for each fact about a system

**Status:** proposed 2026-11-02, nothing built. Stage 1 stands alone and is the
place to start.
**Origin:** closing the family slug-list gap the same day (184 of 762 reports in
no list) needed a new check, and the check was the ninth whose job is keeping a
hand-kept copy in step with a report.

## Where the weight is

| Page | Words | What it holds |
| --- | --- | --- |
| `content/verdicts.md` | 267k | one hand-written entry per report, its maturity line a copy of the report's census |
| `content/families.md` | 122k | eight family slug lists and about 630 per-system paragraphs; Local coding-agent alone is 48k words and 231 paragraphs |
| `content/appendix.md` | 132k | per-report links, the repositories-inspected pins, licences, known limitations |
| `site/index.html` | — | 762 hand-written cards repeating category, capabilities and search terms |

At least nine of the 26 `check_*.py` scripts exist to keep a copy agreeing with a
report: `check_family_marks`, `check_family_lists`, `check_verdict_marks`,
`check_verdict_census`, `check_inspected_pins`, `check_claim_counts`,
`check_homepage`, `check_archive_names`, and `check_mark_agreement` inside a
report. Each new copy has needed a new check. The structure is denormalized, and
the checks are what vigilance costs when it is the only guard.

## The principle

A fact about one system lives once, in its report's frontmatter, and every other
page that states it is generated from there. Prose that compares systems stays
hand-written.

## Stages, each leaving the site working

1. **Family membership becomes data.** Add `family:` and optional
   `families_also:` to every report, seeded from today's lists: the section that
   holds a system's paragraph is its primary family, any other list it appears
   in goes to `families_also`. The slug lists are generated like the A–Z index.
   The generator must reproduce today's lists exactly before the hand-kept copy
   is deleted. `check_family_lists.py` then retires; the lists cannot drift.
2. **Census and pins become generated.** The verdict maturity line's figures come
   from `licence`, `size`, `activity` and `tests`, and the repositories-inspected
   list from `revision`. A report without the census fields keeps its
   hand-written line until a re-read adds them, which is the cutover rule
   `check_report_shape.py` already follows, so no campaign. `check_verdict_census`,
   `check_verdict_marks` and `check_inspected_pins` retire as each copy goes.
3. **Homepage cards become generated.** A one-off script reads each card's best
   idea and main risk into two frontmatter fields, so nothing is retyped; the
   762 cards are then rendered from frontmatter, and the card's category,
   capabilities and search terms cannot drift.
4. **The families page becomes eight essays.** Each family gets an essay of at
   most about 1,500 words — the commitment, the failure it is prone to, and five
   to seven clearest instances in the manner of a pattern page's *Read these
   first* — over a generated table of every member: name, eyebrow, marks.
   - The about 560 single-system paragraphs leave the page. Each mostly restates
     its report's summary, and its bold claim is the report's `description`,
     which the table shows.
   - The 56 paragraphs that compare two or more systems — AIMAOS against Helix
     AGI is the model — are mined into the essays. That is cross-system material
     no report can hold.
   - One inbound link points at a family-section anchor (`#research-lineage`);
     the 38 others land on the out-of-scope and prospective-memory sections,
     including the `#salt` anchor inside one, which keep their headings.
5. **Verdicts, decided later.** After stage 2 only the editorial bullets are
   hand-written — best idea, risk, reusable component, study when, do not copy
   when. Whether they move into each report as a `## Verdict` section is a
   separate decision, worth making once stages 1–4 have landed.

## Cost

- Four new frontmatter fields per report, about 3,000 values, extracted by
  script rather than typed.
- The 182 family paragraphs added on 2026-11-02 become table rows.
- Each generator needs a proof step — reproduce the current copy byte for byte,
  or with a reviewed diff — before the copy is deleted. That step is where the
  risk is, and it is mechanical.

## What it buys

A re-read edits the report and its frontmatter, and nothing else per system. The
copy-policing checks shrink to near zero, and what remains guards prose, which is
where review effort belongs. The families page reads as a taxonomy again rather
than a second corpus.

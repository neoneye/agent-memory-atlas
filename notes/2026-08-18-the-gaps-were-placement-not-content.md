# Four outside reviews in one session, and every gap they found was placement

**Status:** finding, with a triage rule that now has a fifth data point.
**Origin:** four reviews forwarded in one session — Qwen twice, Grok once,
Kimi once — against the whole atlas rather than against named reports.

## What landed, and where it already was

Four reviews produced four accepted changes. Only one of them was missing
content. The other three were content the atlas already had, in a place the
reader complaining had not reached.

| Review | Accepted change | Where the material already was |
| --- | --- | --- |
| Qwen (80/20) | The producer check, now a required step in `add-memory-system` | **Nowhere.** Genuinely missing. |
| Qwen (banner) | A provenance clause on the capability strip | `atlas-rubric.md` "Known limits", since 2026-07-30 |
| Grok (/build/) | Anti-patterns for stages 2–5 | The device existed for Stage 1 and was not repeated |
| Kimi | The boundary on the staging order | The page names its limits everywhere except its strongest claim |

The one real gap is worth its own note; see
[the producer check and a corpus audit](2026-08-18-the-producer-check-and-a-corpus-audit.md).
The other three share a shape: **a caveat stated once, in the right words, in a
place the artifact does not carry with it.**

The capability strip is the sharpest instance. It is seven names and a tick,
quotable without the report around it, and it is therefore what a reader meets
who never opens the rubric. It explained what a dash meant and said nothing
about what a tick rested on. The fact that a mark is one language model's
reading of code it did not run had been published for three weeks — two clicks
away, on a page reached from a nav item that reads as chrome.

## What each review got wrong, and the pattern in it

**Three of the four proposed something that already exists.** Citation-first
reports (`capability_evidence` has been required for new reports since
2026-08-16, with a coverage ratchet); negative evidence as a priority (the
corpus's most common finding class); framing the atlas as a drafting tool rather
than a certification (`"A flag's absence means the mechanism was not found, not
that it is impossible"`); a reference implementation and an executable adapter
(both declared absent, deliberately, in `/build/`'s own "What this page does not
give you"); a table of cost axes (the page names the axes).

**One proposed a disclaimer that would have been false.** The suggested banner
read *"Features marked as 'present' may be unwired or broken."* Every report in
the corpus that finds an unwired mechanism withholds the mark it would have
earned — checked across all fifty of them the same day. Publishing that sentence
on 301 pages would have described the corpus wrongly in the direction of false
modesty, which is still wrong. **Overstating uncertainty is not a safe default.**

**One overstated an absence the atlas is careful about.** *"Nothing is run"* is
close but not exact: two suites were executed and named, CLIO's
`test_ltm_corroboration.pl` (92 assertions) and Aura's `tests/test_audit_chain.py`
(16 tests), under the standing rule that *a report that does not claim a run did
not do one*.

## The rule this adds

The existing triage rule from
[the fourth review](2026-08-13-the-fourth-review-and-the-second-broken-diagram.md)
is about *rendering*: confident structural criticism that resolves to a diagram
that did not draw. This adds a second class, and it is not a reader defect.

**When an outside review proposes something the atlas already does, the first
question is not "is this already done" but "where is it, relative to the thing
the reader was looking at."** Three of four hits here were real signal about
distance, wearing the costume of a feature request. A reviewer who reads the
rubric and the strip is not the reviewer to test placement with; the one who
reads only the strip is.

The counter-test that keeps this from becoming an excuse for a banner on every
page: the fix has to be *specific to the claim it qualifies* and appear once,
beside it. A page-wide disclaimer fails both, and is the thing readers learn to
skip.

## What was declined, and why it stays declined

- **Maintenance/staleness verdicts per report** (`Actively maintained | Stale |
  Abandoned` from commit cadence). Commit cadence as a maturity proxy is the
  popularity-shaped signal the atlas exists to avoid: software can be finished,
  and it can be abandoned with 200 commits last month. It also breaks against
  pinning — a "last modified" date attached to a report pinned at a sha starts
  rotting immediately. The atlas already records the caveat where it changes how
  to read a report: Voyager and Generative Agents are marked frozen 2023
  artifacts.
- **Line numbers as the required evidence key.** Symbols survive refactoring at
  a pinned commit; line numbers do not. The MindCache re-pin the same day moved
  every cited line by seven to nine.
- **A reference implementation.** The argument against is the corpus's own
  central finding: an unmaintained reference implementation is a mechanism
  shipped, admired and quietly unwired, which is the defect this atlas documents
  fifty-one times. That is not a reason never to build one; it is a reason it is
  a standing commitment rather than a missing afternoon.

# A null control, and a list that drifted where the atlas touched it

**Status:** done — two findings from the Daimon re-read of 2026-08-03, both
about the atlas rather than about Daimon; each produced a change (a build check,
and a new benchmarks subsection)
**Origin:** a re-read of `Daily-Nerd/daimon` at
`3025ee3edecd1958e9e9181fe607a5b1a30309bf`, 41 commits past the previous pin,
requested because the project had moved.

The re-read itself belongs in the report and is there. Two things came out of it
that do not fit a system report, because they are facts about this project's
method and about a gap in the corpus.

## 1. The repositories-inspected list had drifted, on re-reviewed systems only

`content/overview.md` publishes a list of every repository inspected, each with
the commit it was read at. That list is the atlas's claim about what was
actually read. Checking all 133 reports' `revision` frontmatter against it found
**three entries carrying a commit older than the report's own pin**:

| System | List said | Report pinned |
| --- | --- | --- |
| `daimon` | `ecb7fafefa81` | `3f79a952cf8e` |
| `verel` | `df80efe8207a` | `df44e76c6c6a` |
| `swafra` | `24dba18a4194` | `669e7bdbcbcd` |

All three are now corrected. The instances matter less than the shape:

**Every drifted entry was on a re-reviewed system.** A first review writes the
report and adds the list entry together. A re-review updates
`revision`/`revision_url`/`analyzed_at` in frontmatter — which the
`reanalyze-memory-system` skill spells out — and the list is a separate hand
edit in a different file, five thousand lines away. So the population where the
atlas's own process is the cause is exactly the population that drifted, and
nothing else could have produced it.

**`npm test` validates revision metadata and did not catch this.** It checks
the shape of the metadata inside a report — full 40-character shas, no
abbreviated commit links, `analyzed_at` present and plausible — and never
compares a report's pin against the published list. Both halves were internally
consistent, so the suite was green while the site made two claims about the same
commit and they disagreed.

**The fix is a check, not a habit.** Every other class of error this repository
has been caught by is now a script — `check_freshness.py`, `check_anchors.py`,
`check_heads.py`, `check_homepage.py`, `check_mermaid.py`. This one is now
`check_inspected_pins.py`, wired into `npm test`: for each report, the
inspected-list entry keyed on `source_name` must carry a prefix of `revision`,
and the displayed sha must match the one in the link target — a correct label
over a stale href is the same failure wearing a disguise. Run against the tree
as it stood before the correction, it reports all three.

Worth stating plainly because the atlas's standing argument against a
commits-behind badge is that a pin comparison cannot tell you whether anything
moved. That remains true. It is a different claim from *the atlas should be able
to tell when it contradicts itself*, and this is the second one.

## 2. Daimon ships a null control, which nothing else in the corpus does

The [benchmarks page](../content/benchmarks.md) argues at length that memory
benchmarking is a monoculture of self-reported wins: vendor-run comparisons
measure "them" versus "them plus us", the baseline is usually too weak, and
almost nobody publishes a loss. It names one exception at the time of writing.

Daimon now has the artifact that argument implies. Since 1 August 2026 it ships
`research/experiments/recall-replay-ab/` — arm A is the shipped
`recall.suggest()`, arm B a pluggable variant, both replayed against the same
time-filtered snapshot of real historical prompts, with a side-blind judge on
the rows where the arms disagree. Three properties are the point:

- **A placebo arm.** `--variant placebo` suppresses rows at random at a
  per-age-band rate, so a treatment that improves things by *removing rows* can
  be compared against removing rows for no reason. This is the null control
  whose absence the benchmarks page treats as the default failure.
- **The instrument verifies itself.** `verify.py` builds a synthetic store
  through the real write path and asserts determinism, that the identity variant
  reproduces arm A exactly, and blind-file hygiene.
- **It has been used to kill a shipped feature.** Two commit subjects read
  `measured and refuted`. The third,
  `research/experiments/gate-491/measurements.json`, is the one to read: the age
  gate's open-question exemption graded **10% relevant, Wilson 95% CI 3.5–25.6,
  n=30**, inside the 6–10% band the gate already blocks. The file declines to
  use its own pre-registered 40% bar *and says why* — it was not derivable from
  anything measured, and it held exempt rows to a higher standard than the
  policy applies to rows it keeps. It names two rejected alternative
  explanations, each recorded as separating "the WRONG way". It carries a
  `not_measured` block for the silence cost the instrument is structurally blind
  to. And its `index_composition` note flags that its own count is
  "conservative in the direction that weakens the finding".

That last habit is the one this atlas asks of benchmark publishers and has found
essentially nowhere: stating which direction your own conservatism cuts, in the
artifact, before anyone asks.

**What this does not settle.** The rig grades precision of what *was* injected,
on one maintainer's prompts, and says so. It does not answer the atlas's
standing open question about Daimon — what the trust machinery costs in
retrieval terms — because its arms vary recall scoring rather than whether the
gate ran. That experiment is unbuilt and the instrument is already shaped to run
it, which is now recorded in the report as the single most informative
unpublished result in that repository.

**Written up.** The benchmarks page named the systems that publish losses and
had no column for the sharper question — *did you compare against doing it for
no reason*. It now carries one, under "the baseline is usually too weak", with
Daimon as its single occupant. The distinction that earns the subsection: a weak
baseline flatters a system that **adds** something, and says nothing about a
change that **removes** something, because dropping rows improves precision on
almost any corpus whether or not the rule choosing them is any good.

## What came of it

- **One published claim corrected** in the Daimon report: item ids are minted at
  12 hex through a `(12, 16, 24, 40)` ladder, not the 6-hex slice the atlas had
  published while praising the tombstone that depends on them.
- **No mark moved.** The eleven-step deletion protocol and its three sibling
  tests are byte-identical to the previous pin.
- **Three inspected-list entries corrected**, and `check_inspected_pins.py`
  added to `npm test` so the fourth cannot ship.
- **One gap closed** — the benchmarks page now has a null-control subsection,
  with the one system in the corpus that occupies it.

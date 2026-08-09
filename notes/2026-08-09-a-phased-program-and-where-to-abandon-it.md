# A phased program, and where to abandon it — sequencing the four directions, with a go/no-go at each seam

**Status:** sequencing note. No phase is approved; the point of the note is that
phases 3 and 4 must not be approved yet.
**Origin:** the four notes written on 2026-08-09 —
[conformance](2026-08-09-the-conformance-run-the-atlas-does-not-run.md),
[half-life](2026-08-09-the-corpus-has-a-half-life.md),
[receipts](2026-08-09-the-receipts-the-atlas-cannot-produce.md),
[widening](2026-08-09-widening-and-its-falling-marginal-value.md) — each of which
argues its own case and none of which says what depends on what.

Three results came out of sequencing them that were not visible one note at a
time, and they are the reason this note exists rather than a paragraph appended
to each.

- **The cheapest item is a prerequisite for the other three**, which inverts the
  "cheap versus important" framing the other notes leave standing.
- **Local execution is safe in exactly one phase**, and it is the phase that
  decides whether the whole conformance line is real.
- **Two phases must not be started**, and the condition that would release them
  is a finding, not a date.

---

## Phase 0 — Make the atlas citable

**Build:** the dated tag and the age delta at the point of reading, both from the
[half-life note](2026-08-09-the-corpus-has-a-half-life.md). A git tag, a version
line in the site footer, a sentence on the methodology page saying a citation
should name the tag, and the `analyzed_at` delta in days on report headers and the
systems index.

**Why first, and it is not because it is cheap.** Every later phase produces an
artifact that references the state of the atlas. A submission says which atlas
version its test ids came from. A downstream-changes row says what the atlas
claimed before the upstream moved. A re-analysis says what changed since the last
reading. Without a tag all three cite a moving target, and the fix is retroactive
and unpleasant — you cannot go back and name the version a submission was made
against.

This is the result that surprised me: the item I described as "cheapest by a wide
margin" is load-bearing for the three items I described as more important.

**Cost:** hours. **Doctrine touched:** none. **Abandonment cost:** zero — a tag
and a date delta are useful with nothing built on top.

**Gate to leave:** none. Nothing downstream is worth starting first.

---

## Phase 1 — Receipts

**Build:** the `downstream:` frontmatter field, the generator, the
explicit/inferred/unknown attribution labels, and — in the same phase, not
after — the `scripts/` firewall that fails the build when a report cites the
downstream page.

**Why here.** It is independent of everything else, it is a day, and it produces
the one thing phase 3 needs in order to be a conversation rather than an
assertion: a record of what happened the last four times a maintainer engaged.
Asking someone to run a suite and submit a log goes better when the ask can point
at a page instead of a claim.

**The firewall ships with the page, not after it.** The temptation to cite
responsiveness as quality begins the moment the page exists, and this project's
own history is that a rule without a check is a rule that gets violated and found
later. The [receipts note](2026-08-09-the-receipts-the-atlas-cannot-produce.md)
makes the argument; the sequencing point is that the two land in one commit.

**Cost:** a day, plus a few lines of frontmatter per affected report — currently a
handful. **Doctrine touched:** none; it publishes what the History sections
already say. **Abandonment cost:** low. The frontmatter field is useful even if
the page is never generated.

**Gate to leave:** the page renders, the firewall has a control, and Daimon's row
reads visibly as `inferred`. If Daimon's row cannot be made to look different
from Perseus's at a glance, the page asserts causation and should not ship.

---

## Phase 2 — Validate the suite against the kernel *(go/no-go for the whole conformance line)*

**Build:** the harness from step 1 of the
[eval-suite note](2026-07-28-executable-eval-suite.md), run against the
[atlas kernel](2026-07-28-atlas-kernel-proposal.md) — the reference
implementation of the four-pattern minimum stack **and its paired broken
configuration**.

**This is the one phase where local execution is safe, and that is not a
coincidence.** The constraint that closed step 2 of the eval-suite note is that
running the deletion sequence against a corpus system means installing that
system, which `screen_repo.py` exists to avoid. The kernel is code this project
writes. Executing it risks nothing the project did not author, so the objection
that closes phase-2-against-238-systems does not touch phase 2 against the
kernel. The constraint and the plan are compatible at exactly one point, and the
plan should be built at that point.

**Why it is the go/no-go.** Everything downstream quotes test ids as if a pass
means something. A suite that has never been shown to fail on a system known to
be broken is a suite whose greens are unfalsified. If the broken configuration
passes, the test is wrong, and every later phase would be collecting logs from
maintainers against a specification that does not discriminate.

**Cost:** the largest single item on the list, and the kernel may not exist yet.
**Doctrine touched:** none — it is this project testing its own code.

**Gate to leave — and this one can fail:** each test passes on the correct kernel
configuration **and fails on the paired broken one**, with the failure naming
which step of the sequence caught it. If a test cannot be made to fail on the
broken arm, that test is removed from the submission set rather than shipped with
a caveat. If most of them cannot, **phase 3 does not happen** and the conformance
line is closed — which is a real outcome and should be written up as one, not
quietly deferred.

---

## Phase 3 — One submission, one maintainer, no announcement

**Build:** the submission format next to
[`build-brief.md`](../.agents/protocol/build-brief.md) — test id, commit, CI log
URL, adapter path, negative-control result, proof string — and then **one**
worked submission, produced with a single maintainer who already has the CI to
run it.

**What this phase is not.** It is not an invitation, an announcement, or a page
titled *Submissions*. Note 1's named failure mode is a format nobody can fill,
and the way that happens is publishing the format before anyone has filled it
once. The first submission is a collaboration whose output is a corrected format.

**The deliverable is a finding, not a submission.** The atlas reads the adapter at
the pin and writes what it saw into that report's section 10 and its `## History`.
Whether the log said pass is the least interesting output.

**Cost:** the format is small; the collaboration is unbounded and depends on
someone else's week. **Doctrine touched:** this is the phase that changes what the
atlas is, and the [protocol note](2026-08-07-the-atlas-as-an-agent-protocol.md)'s
refusal of the word *conformance* has to survive it intact.

**Gate to leave — and this one is the real test of the whole idea:** reading the
adapter produced something the log did not say. A discrepancy, a test that passes
by not testing, a missing negative control, a `not_proven` clause the maintainer
had not considered. **If reading the adapter added nothing to reading the log,
the burden inversion bought nothing**, and phase 4 must not happen — the honest
conclusion would be that self-attestation is a green tick with extra steps, and
that belongs in a note rather than on the site.

---

## Phase 4 — Open it, narrowly

Only reachable if phase 3 produced a finding. Even then: the asymmetry from note
1 goes in the format's own header before the first external submission arrives —
a submission is only ever evidence *for* a mechanism, because not running is not
failing, and a system with no submission gets no cell, no ❌, and no
"unverified".

No phase 5. There is no version of this that ends in a certificate.

---

## The load that runs underneath all of it

Re-reading the 113 reports untouched since the project's first six days is not a
phase, because it never completes. It is the background cost every phase competes
with, out of one budget, and the honest question at each seam is whether that
phase is worth displacing re-reads.

My answer, stated so it can be disagreed with: **phases 0 and 1 are worth it and
phase 2 probably is; phase 3 is not obviously worth it and phase 4 is not
assessable yet.** Phase 0 makes every existing report more useful to a reader at
no doctrinal cost. Phase 1 preserves evidence that is actively dissolving. Phase 2
either validates a specification this project has published and never tested, or
retires it — both are worth a week. Phase 3 spends an unbounded amount of someone
else's time to find out whether an idea works, and the [widening
note](2026-08-09-widening-and-its-falling-marginal-value.md)'s bar applies to it
too: it is worth doing if a *pattern* might move.

## What this note is for

Every phase above has a gate that can fail, and two of them are meant to. A
program where each stage is justified by the next one is how a project talks
itself into phase 4 before phase 2 returned. The gates are written down now,
before any of them is inconvenient.

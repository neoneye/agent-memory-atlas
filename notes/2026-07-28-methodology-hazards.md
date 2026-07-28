# Hazards in this review process

**Status:** live; two of these already caused published errors
**Origin:** mistakes made and caught during the work, plus one caught by an
external reviewer.

The atlas documents how memory systems fail. This is the same treatment applied
to the process that produces it, because two of the failures below have already
put wrong claims on the site.

## 1. Self-citation: the reviewer's prose becoming the reviewer's evidence

**Happened.** The `audit_log` capability was assigned to seven systems. On
re-audit, five did not qualify. Two of those — `hindsight` and `agentmemory` —
were flagged because the word "audit" appeared **in this atlas's own summary of
them**, with no named artifact behind it. The atlas cited itself and counted it
as evidence.

**Why it is structural:** reports are written first, then frontmatter is filled
in from them, then indexes are generated from frontmatter. Each step is a
reasonable summary of the last, and by the third the original code is three
removes away.

**Mitigation:** a capability mark must cite a file or symbol, not a report
sentence. The rubric now says a wrong mark is refuted "with the file and symbol,
since a mark is a claim about code at a specific commit" — the same standard
should apply when the mark is *made*.

## 2. Plausible output mistaken for verified output

**Happened three times in one session.**

- A `sed` that silently did not apply, so a test designed to prove a drift check
  worked printed nothing and looked like a pass. The check was fine; the proof
  was not.
- `scripts/check_freshness.py` compared `pinned...HEAD`, which GitHub resolves
  against the base ref rather than the repository. Most pins reported as
  identical to themselves. Caught only because one number was implausible — and
  that number turned out to be *correct*, so the implausibility was a false lead
  that happened to point at a real bug.
- `_ga` cookies appeared to be set before consent, which looked like the consent
  gate failing. They were left over from an earlier test on a different port;
  cookies are scoped per host and `localhost` is one host.

**Pattern:** in all three the output was consistent with the expected result, and
in two the *test* was broken rather than the thing tested. A test that has never
failed has not been tested.

**Mitigation:** before trusting a check that passes, break the thing deliberately
and confirm the check notices. This is now done for `check_homepage.py`,
`check_anchors.py` and the capability drift check; it was not done for the first
freshness implementation, which is why that one shipped wrong.

## 3. A single reviewer assigning every mark

**Standing.** Every capability mark, every "Best idea", every "Main risk" is one
person's reading. There is no second opinion anywhere in the pipeline, and the
rubric's strictness makes marks feel objective in a way that hides this.

**Mitigation, unimplemented:** the marks are the checkable part. A second reader
re-deriving the seven flags for a sample of ten systems, blind to the first
assignment, would produce an inter-rater agreement number. Disagreement above
some threshold means the definitions are too loose, which is exactly what the
`trust_state` and `audit_log` corrections suggested.

## 4. Anchoring on re-review

**Not yet happened; will.** The freshness tool creates a work list of stale
reports. Re-reviewing a system while looking at the previous report all but
guarantees confirming it: the previous "Main risk" becomes the thing you look
for.

**Mitigation:** re-review the code first and write the new assessment *before*
reading the old one, then diff. The diff is the interesting artifact — "what
changed in the system" and "what I got wrong last time" are both in it, and they
are not separable if the second reading was anchored by the first.

## 5. The author reviewing their own system

**Standing, and about to get worse.** RainBox is in the atlas as a self-assessment,
clearly labelled. The [kernel proposal](2026-07-28-atlas-kernel-proposal.md)
would add a second entry by the same author, and unlike RainBox it would exist
*because* of the atlas's arguments — a system built to embody the rubric, then
marked against it.

**Mitigation:** if the kernel is built and added, its marks should be assigned by
someone else, or it should sit outside the atlas as a teaching artifact rather
than as entry N+1. "Scores well against the rubric it was built from" is not a
finding.

## 6. Absence claims aging into wrongness

**Standing.** "No X was found" is true of a pinned commit forever. It reads as a
claim about the project, and every day it is less so. The rubric and the reading
guide both state the convention; the freshness tool now quantifies the exposure.

The uncomfortable case is the two tombstone systems: if a third system added one
tomorrow, the atlas's most-quoted number would be wrong and nothing would notice
until someone re-read it.

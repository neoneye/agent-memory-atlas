# Declined proposals, with reasons

**Status:** decisions, recorded so they are not relitigated by the next reviewer
**Origin:** suggestions from four external reviews on 2026-07-27 and 2026-07-28.

Each of these was proposed by a competent reviewer, considered, and declined.
Recording the reasoning is cheaper than re-deriving it, and if a reason stops
holding the decision should change.

## Reposition the atlas as a GDPR / SOC 2 compliance reference

**Proposed:** frame the deletion and tombstone work as "compliance for AI
agents", on the grounds that enterprises are afraid of the right to erasure.

**Declined because** it is a claim about legal sufficiency that nothing here
supports. No lawyer has reviewed it and no system has been run. The atlas already
makes the proportionate version of the point: "we deleted the row and a nightly
job re-derived it from retained history" is a compliance failure with a
benchmark-shaped hole where the evidence should be. That is defensible because it
is about mechanism. Repositioning converts credibility into a liability, and it
is the one suggestion that would make the project more popular and less
trustworthy at the same time.

**Would change if** the deletion harness had actually been run against systems
and the results reviewed by someone qualified to speak to the legal standard.

## Tag maintainers with provisional scores so they compete to fix a ❌

**Proposed:** publish provisional capability marks, tag framework authors, and
let competitiveness drive them to implement the missing mechanism and submit a PR.

**Declined because** it turns a code-grounded review into a leaderboard, and
leaderboards get gamed. The predictable failure is specific: someone adds an
`is_rejected` boolean, claims the tombstone mark, and the strict definition —
*keyed on the value, so extraction cannot re-assert it* — becomes a thing to
argue about rather than a thing to check. This atlas has already been caught
twice on semantic misclassification without any adversarial pressure.

**Kept from the suggestion:** making corrections easy to submit. The rubric page
states the evidence threshold and says a wrong mark is a defect worth reporting,
with the file and symbol.

## A manifesto post titled "Why 99% of AI Agents Fail in Production"

**Proposed:** synthesize the findings into an aggressive, widely shareable essay.

**Declined as framed.** The material exists and a synthesis essay is a good idea.
The title is an invented statistic on a site whose distinguishing feature is
refusing invented statistics. The honest version of that headline is closer to
*"Two of fifty-six systems can remember that they were wrong."*

## Run one standardized test against every system

**Proposed:** pick a sanity test and report Pass/Fail for all 56, so a
well-tested system cannot look better than a robust one on test-file names alone.

**Declined because** the 56 span Rust crates, Postgres services, hosted vector
APIs, an RL training rig and a Minecraft agent, and several cannot store a byte
without a paid key. A Pass/Fail column covering a fraction reads as a comparison
and is worse than honest static review.

**Kept:** the [subset version](2026-07-28-executable-eval-suite.md) — run it
where it runs, publish the exclusion list with per-system blockers.

## A three-state "partial" column on the capability rubric

**Proposed:** implicit in several reviews asking for more nuance in the marks.

**Declined because** nearly everything is partial at some resolution, so the
middle bucket absorbs every hard case and the column stops discriminating. The
strictness is what makes the counts mean anything. The near-misses — which are
the interesting part — are named in prose instead, and the
[rubric page](../content/methodology/atlas-rubric.md) records this decision.

## Wider filter columns (sync/async writes, retrieval stack composition)

**Proposed:** a caniuse-style matrix with columns beyond the seven capabilities.

**Declined because** those dimensions have never been assessed uniformly across
the corpus. Inventing boolean columns to fill out a matrix is how a code-grounded
index becomes a spec sheet. The filter ships on the seven that were actually
judged against strict definitions.

**Would change if** a dimension were added the same way the seven were: one
definition, applied deliberately per system, drift-checked by the build.

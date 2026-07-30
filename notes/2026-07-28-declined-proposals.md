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

## Plain-language analogies for each pattern (hotel keycard, detective's notebook)

Proposed 28 July 2026 as a way in for junior developers: scope as a hotel
keycard, evidence-before-belief as a detective's raw notes versus the final
report, tombstones as a "do not call" list, trust states as Wikipedia's
draft/published/disputed.

They are decent analogies — the Wikipedia one is close to exact. Declined anyway,
because the accessible entry already exists and is better: **the failure-first
list** at the top of the patterns index maps a symptom you are experiencing to
the pattern that closes it. A reader who does not know what bi-temporal validity
means does not need a metaphor for it; they need "changing facts overwrite useful
history", which is what that list says.

The risk is specific rather than stylistic. An analogy that is 90% right imports
its own 10%: a keycard is checked at a door once, whereas scope has to hold in
the schema, the indexes, the cache keys and every background job, and the reader
who has internalised the door will not go looking for the background job. The
same review that proposed these also concluded from the pattern pages that
tombstones consume context window — which they do not, since they are consulted
on the write path — and that is what a plausible mental model does when it is
slightly off.

**Adopted instead:** the compounded cost of the four-pattern stack, and an
explicit correction of the tombstones-in-context misreading, both on the patterns
index.

## An "API-contract only" tier for the closed systems

Proposed 30 July 2026 by an AI review, and it is the fourth arrival of the
closed-source proposal and the first version that deserves a separate answer.
The earlier versions asked for reports on OpenAI's, Claude's and Vertex's memory.
This one concedes the internals are unreachable and asks for something narrower:
a distinct tier that evaluates each hosted product's **published API surface**
against the five divergences. Not "how does it store memories", but "does this
API expose a way to reject a value, scope a read, or decline a retrieval".

**The reasoning is good and the answer is still no**, for a reason worth writing
down because it is not the reason the earlier versions were declined.

An API surface answers a *different question* than the marks answer, and the two
would sit in the same table. `tombstone` means the mechanism was found in code.
"The API has no reject endpoint" means the vendor did not expose one — which is
compatible with the mechanism existing, being used internally, and being absent
from the docs; and "the API has a `DELETE /memories/{id}`" is compatible with a
nightly extraction pass re-deriving the value the next morning, which is the
exact failure the tombstone column exists to catch and the one thing an API
surface can never show. So the tier would produce rows that look like marks,
read like marks, and mean something weaker in both directions.

There is also a maintenance argument the atlas has already made about itself. A
mark is a claim about a commit, which makes it auditable and lets
`check_freshness.py` report when it has aged. An API claim is a claim about a
documentation page with no revision to pin, so nothing can tell a stale row from
a current one.

**Kept from the suggestion:** the observation that a decision-maker reaching this
atlas will probably deploy a hosted product anyway. The scope section already
says the absence is a gap in the atlas rather than a finding about the products;
what it does not do is help that reader. The honest version of the help is a
short list of *questions to ask a vendor*, phrased from the five divergences and
carrying no marks — which is documentation of a method rather than an assessment
of a system, and would not be mistaken for one.

**Would change if** a hosted product publishes a conformance test rather than a
feature list — something a reader could run against the live service. That is an
artifact, and artifacts are reviewable.

## A separate antipatterns page

Same review. Proposed "garbage dump vector store", "amnesia by overwrite",
"omniscient agent" as named failures.

Declined as duplication. Each pattern page already opens with **The problem**,
stated concretely, and the failure-first list is an antipattern index in
everything but name — all three proposed antipatterns map onto rows already
there. A separate page would restate the same material in a second vocabulary,
and the atlas would then have two names for each failure and no rule for which to
use.

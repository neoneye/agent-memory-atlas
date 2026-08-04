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

## 2b. The reviewer is a language model

**Stated late.** The reports are written by an LLM reading repositories, directed
by one person who reviews and commits. The rubric said "one reviewer reading
code" and left the rest to inference until 30 July 2026, when an outside reviewer
inferred it correctly and the omission became obvious. A project that refuses
claims unsupported by artifacts should not have left its own method to be guessed.

The failure mode is specific and worth naming precisely, because it is *not*
carelessness: the output is fluent, structurally correct, and adjacent to the
truth. Three instances from 30 July alone:

- **A fabricated commit id, twice.** A triage table held abbreviated SHAs; the
  report frontmatter needed full ones, and plausible forty-character strings were
  produced rather than the real ones. Both caught before publishing, by running
  `git log -1 --format=%H`. Nothing about the invented SHAs looked wrong.
- **A bug that was not there.** Cortex's `shared_context` insert names nine
  columns and binds eight values, which reads as a parameter-shift defect. The
  `VALUES` clause hardcodes `version` to `1`. It was one line further on, and the
  finding was one keystroke from being published.
- **A mark that was wrong for two months.** Mem0's `history` table plainly earns
  `audit_log` and the report carried only `scope_enforced`. This one was not
  caught by checking; it surfaced because an independent C# reimplementation of
  the same design was reviewed and marked differently, and the divergence was
  written down rather than resolved. A false *negative* leaves no trace to notice.

**Pattern:** the first two are caught by the discipline this atlas already
imposes — cite a file and a symbol, then go read it. The third is not, and no
amount of care at write time would have found it. It was found by coverage: the
corpus happened to contain one system twice.

**Mitigation, in order of how much they help.** Every claim names a file and a
symbol, so a reader can check without trusting the reviewer — this is the whole
reason the format demands it. Verify before asserting, particularly anything
shaped like a defect. And treat re-review of already-marked systems as a real
activity rather than a backlog item, because a wrong mark is invisible from
inside the report that carries it.

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

## 7. The rubric became a target

**Live, first observed 28 July 2026.** Verel now implements all seven capabilities
and ships `memory/rubric.py`, a module that probes itself against this atlas's
rubric and prints a score. Release commits are titled with the marks — "atlas
7/7". The mechanisms are real and the probes are behavioural rather than
declarative, so this is not gaming in any dishonest sense. It is still Goodhart:
the measure has become an objective for at least one measured system.

Consequences to hold onto:

- **A count of marks is now partly a measure of who has read the rubric page.**
  Seven marks meant something different in June, when nothing was aimed at it.
- **Self-assessment cannot be evidence.** Recorded on the rubric page. Verel's
  probe is well built and I still had to read the code, because there is no way
  to distinguish a correct self-assessment from a confident one without doing so.
  The check paid immediately: running the module from a wheel scored 6/7 against
  a release note claiming 7/7, and `rubric.py` was unchanged in the commit that
  claimed to fix it.
- **Provenance is the defence.** Where the atlas can date a mechanism to a cause
  — Verel's tombstone to a red-team round in June, before this page existed — the
  reader can tell need from checklist. Where it cannot, the prose should say so
  rather than let the mark imply it.

**Not a reason to stop.** A rubric nobody builds toward is a rubric nobody uses.
The cost is that the atlas can no longer treat mark counts as an independent
survey of the field, and should stop describing them that way as adoption grows.

**Watch for:** a second system implementing to the rubric; any system whose seven
mechanisms all postdate the atlas; and the atlas quietly beginning to cite its own
influence as evidence of anything.

## 8. Reading the repository instead of the paper

**Happened, 2026-07-31.** The atlas's core rule is that a claim must be found in
code at a pinned commit. Applied to a *systems paper with released code*, that
rule quietly inverted: [ForgetEval](../content/benchmarks.md) was read at
`b6053b7b`, described in detail — six-method adapter protocol, ten attack
categories, the 132/253 hand-crafted-to-LLM split, a wrong MemPalace row the
paper's own harness produced — and four facts stated plainly in the abstract were
never recorded.

What was missed, all of it in [arXiv:2606.15903](https://arxiv.org/abs/2606.15903):

- The 385 adversarial cases are one layer of *"a 1000-case templated suite plus a
  385-case adversarial layer"*. The atlas recorded the smaller half as the whole.
- *"Admission is corroborated by 10-annotator IAA (Fleiss' kappa = 0.958)"* —
  labelling provenance no other benchmark on that page reports.
- *"a 77-case external-authored subset (four blind contributors) that replicates
  the canonicalization asymmetry"* — an independent replication of the headline
  result.
- Per-run cost and per-case latency, in the abstract, against a benchmarks page
  whose fourth standing complaint is that cost and latency are barely measured.

The last one is the sharp end. The page argued for five months that nobody
reports operational cost, while linking a paper that reports it in its second
sentence.

**Why it is structural.** The rule exists because product claims outrun
implementations, and it is right about that. But it encodes an assumption — that
the document is marketing and the code is truth — which holds for a vendor README
and fails for a peer-reviewed artifact paper, where the *methodology* claims
(annotator agreement, external replication, cost) have no representation in the
code at all. A harness cannot show you its own inter-annotator agreement. Reading
only the repository guarantees those facts are invisible, and the more rigorous
the paper, the more it loses.

**Mitigation:** when a repository is the artifact behind a paper, read the
abstract against the report before publishing, and treat any claim about *how the
evaluation was built* as paper-only by default. The code-first rule stays for
claims about behaviour; it was never the right instrument for claims about
method.

**Watch for:** any other atlas entry that cites an arXiv id — each is a place the
same inversion could have happened, and the check is cheap.

## 8b. The inverse: a repository claim attributed to the paper it cites

**Happened, 2026-07-31.** Following hazard 8, the remaining reports citing an
arXiv id were checked. Three of four held. [SimpleMem](../content/systems/simplemem.md)'s
figures match its abstract exactly — 26.4% average F1 on LoCoMo, ~30× less
inference-time token consumption. [NOOA Memory](../content/systems/nooa-memory.md)
was the model case: it has a *Sources Beyond the Code* appendix, and every
section reference resolved except one that pointed at a parent section rather
than the subsection.

[Second Me](../content/systems/second-me.md) did not. Its report said the paper
*"reports on Hierarchical Memory Modeling and the Me-Alignment algorithm"*.
Neither term appears in the paper. Both appear in the repository's README, in a
Key Features sentence that **cites the paper in the same breath**: *"Using
Hierarchical Memory Modeling (HMM) and the Me-Alignment Algorithm…"*. The atlas
read the README, followed its citation, and wrote the README's vocabulary as the
paper's finding.

**Why it is structural, and why it is not the same as hazard 8.** Hazard 8 is
reading the code and missing what only the paper says. This is reading the
project's own prose and passing its citation through unchecked — the failure is
not *which* source was read but that a **second-hand citation was reported as
first-hand**. A README that cites a paper is making a claim about that paper, and
the atlas treats README claims as needing verification everywhere else.

It is also the exact failure the atlas caught an outside reviewer making: [a Grok
review](2026-07-30-two-ai-reviews.md) quoted a sentence as the atlas's "central
thesis" that is not in the atlas, at the point where it reached for maximum
confidence. Same shape, and this time it was the atlas's own sentence.

**Mitigation:** when a report attributes something to a paper, the phrase should
be findable in the paper. If it came from the README, attribute it to the README
— which is usually the more interesting sentence anyway, because it says what the
project wants to be known for.

**Checked 2026-07-31.** The five arXiv ids in `content/overview.md` were worked
through. Four verified cleanly against their abstracts and pages:

| Paper | Atlas claim | Result |
| --- | --- | --- |
| 2501.00663 *Titans* | a neural long-term memory module learning at inference; **no official implementation** | holds |
| 2510.02373 *A-MemGuard* | three quoted phrases — *"stored as precedent"*, *"amplifies the initial error"*, *"progressively lowers the threshold"* | all three verbatim |
| 2512.13564 *Memory in the Age of AI Agents* | v2, 13 January 2026; a survey with an open-source framework table | exact |
| 2603.15183 *Token Coherence* | the paper leads with simulated token savings; four figures reproduced | holds — 95.0 / 92.3 / 88.3 / 84.2% across four workload configurations |

No new repositories came out of it. Titans has no official implementation,
A-MemGuard's was already read at a pinned commit, the Token Coherence repository
was already examined and excluded, and both surveys release no code — so the
"analyze the repos" half of this pass was already done.

**The fifth is a verification limit, not a finding.** For
[2604.16548](https://arxiv.org/abs/2604.16548) the five VMG primitive names and
the formal Verified Forgetting definition both verified exactly. The
*"no existing literature"* status line did not — but the atlas's own note sources
it to **Figure 3**, *"a dependency tower with deployment maturity per layer"*,
and a text fetch cannot read words rendered inside a figure. This environment has
no PDF rendering (`pdftoppm` absent), so the claim can be neither confirmed nor
refuted here.

That distinction is the point worth keeping. Two fetches returned "not found",
and treating that as a refutation would have produced a confident correction to a
claim that is probably right — the note records all five per-primitive maturity
labels, which is the kind of detail you only have if you looked at the figure.
**Absence of evidence from a tool that cannot see the medium is not evidence of
absence**, and the failure mode of a verification pass is to generate false
positives when it forgets what its instrument cannot read.

**Watch for:** anything else in the atlas quoted from a figure or table image.
Those are unverifiable by fetch and should carry the figure number, as this one
does.

## 9. The narrow grep whose silence reads as an absence

**Standing, and the best-evidenced hazard here** — three instances from a single
assessment on 2026-08-03, none of which reached the site.

Hazard 6 is about an absence claim *ageing* into wrongness. This one is about an
absence claim that was **never true at any commit**: a search scoped to the
wrong files returns nothing, and nothing is exactly what a real absence returns.
The two are indistinguishable in the output. Only the scope of the search
separates them, and the scope is invisible once the result is written down.

All three came from assessing `kitfunso/hippo-memory` at
`a9c7cca3613b6571bfb37ad1fb6c070b7c976197`:

- **`bitemporal`, twice.** First reading: `valid_from` appears in
  `src/graph-recall.ts`, so the property was called graph-layer-only. Second:
  the `memories` table has the columns and a search of the memory read path for
  a filter returned nothing, so it was called declared-and-unwired — which is a
  finding shape this atlas is known for and would have been believed. Third,
  after widening to all of `src/`: `src/policies.ts` implements it properly, with
  a required `valid_from`, a nullable open-ended `valid_to`, a half-open
  interval, fixed-width date normalisation so values sort lexically, and a
  committed fix for a read-path bug that made same-day policies invisible.
- **`human_review`.** Recorded as "not assessed" while the answer was already in
  `store.ts` — conflict status moved by code rather than by a person, which is a
  no rather than an unknown.

**Two of the three would have been criticisms**, which is the direction hazard 4
already identifies as least likely to be corrected by a reader: nobody writes in
to say a project is better than the atlas described it.

**Why the shape recurs.** A capability probe is a search for a *vocabulary*, and
every vocabulary has a boundary the searcher chose. When the mechanism is one
file outside it, the instrument reports the same empty result it reports for a
system that never built the thing. Confidence in the answer is therefore
confidence in the search scope, and the scope is the part never written down
beside the claim.

**Watch for:** any mark recorded as absent on the strength of a search rather
than a reading. Before publishing a negative, widen the search to the whole
source tree at least once and say so — and prefer "not found in `src/`, searched
for `<terms>`" to "absent", because the first is checkable and the second is a
claim about the project.

## 10. The corpus-scoped superlative, asserted rather than searched

**Standing, and the largest unmeasured exposure in the project** — 294 live
instances, counted 2026-08-04 by `scripts/list_superlatives.py`.

Hazard 9 is a search whose scope was too narrow, returning a silence that reads
as absence. This is the failure one step earlier: **no search at all.**

The instance that produced it. On 2026-08-03 the
[memory-project](../content/systems/memory-project.md) report was published
calling AGPL-3.0 "the most restrictive licence in this corpus". Five other
reports carry AGPL, and six carry licences that are not open source at all —
BSL, ELv2, PolyForm, all rights reserved. One grep disproved it and the claim
had never had one. It was retracted the same day.

**The class is much larger than the instance.** A superlative scoped to one
repository — "the most valuable artifact in this repository" — is an ordinary
judgement the report's own evidence supports. A superlative scoped to the
*corpus* is an assertion about all 134 reports at once, and there are 294 of
them across `content/`: 281 "the only", 200 "the most", 154 "the first", 95
"nothing else", before narrowing to the ones that name the atlas.

Three properties make this the worst-shaped claim the project produces:

1. **They are the most quotable sentences on the site.** "The only system in this
   atlas that can remember it was wrong" is the line a reader carries away, and
   it is the line with no file and no symbol behind it.
2. **They are the least verifiable by a reader.** Checking one means reading
   every other report, which is the work the atlas exists to have already done.
3. **They rot silently and in one direction.** Every report added can only
   falsify them, never confirm them, and the falsification happens in a file
   nobody is editing. The count went from 133 to 134 on 2026-08-03 without a
   single one being re-read.

**Not a build gate, on purpose.** `scripts/list_superlatives.py` reports rather
than fails, because a check that errors on 294 pre-existing instances trains
people to skip it. Run it when adding a report and treat the output as a review
list: for each hit, either the claim is mechanically checkable and should be
checked, or it is a judgement and the prose should say so.

**Watch for:** the ones that are checkable and read as judgements. "The only
system carrying a tombstone" is answerable from the capability index in one
query. "The most carefully reasoned correction in the atlas" is not answerable at
all, and should not be phrased as though it were.

## Hazard 3b: the truncated listing (2026-08-04)

A third form of the scoped-search hazard, found by the author of
[Cambium](../content/systems/cambium.md) reporting a wrong claim.

The repository was surveyed with `find . -type f -not -path "./.git/*" | head -40`.
The listing ran out inside `docs/`, and `profiles/` contributed exactly one line —
its `README.md`. The report then said the repository had "no worked instance" of
its profile interface. `profiles/examples/agent-atlas/` is a 603-line filled
reference profile with no placeholder markers, it passes `check_profile.py` with
all ten interface slots bound, and it was present at the commit under review.

**Why this is worse than the two forms already recorded.** Hazard 3's existing
instances are a grep scoped to the wrong files and a pattern that matched
nothing — both cases where the query *returned nothing* and nothing is
indistinguishable from absence. Here the query returned forty lines. A partial
result reads as a survey, not as a sample, and one line from `profiles/` is
exactly what an empty `profiles/` would have produced.

**The rule.** A listing used to establish that something is *absent* must not be
truncated. Count first (`| wc -l`) or drop the `head`. Truncation is fine for
orientation and never fine for a negative claim.

**On the correction path.** It was verified at the atlas's own pinned commit
before anything was rewritten, not against the project's current `main` — the
disputed claim was about what existed at the pin, and checking only the current
tree would have left it unfalsifiable in either direction. The retraction is
logged in the known-limitations list in `content/overview.md`.

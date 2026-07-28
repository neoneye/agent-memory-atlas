# Questions the existing corpus can already answer

**Status:** open, none attempted
**Origin:** noticed while building the capability index — 58 commit-pinned
reports with structured frontmatter is a dataset, and it has not been queried as
one.

Everything here needs **no new reviews**. It is analysis of material already
committed, which makes it cheap relative to anything else in these notes.

## 1. Which capabilities co-occur?

The `capabilities:` frontmatter across 58 systems supports a co-occurrence
matrix, and nobody has computed one. Specific hypotheses worth testing:

- **Does `trust_state` predict `human_review`?** A system that models epistemic
  status plausibly also gives someone a way to adjudicate it. If the correlation
  is strong, the two are one design decision and the rubric is double-counting.
- **Does `audit_log` predict `tombstone`?** Both come from taking correction
  seriously; if they never co-occur, that is a more interesting finding.
- **Is any capability isolated** — present only in systems carrying nothing else?
  That would suggest it is cheap and unrelated to the rest, which would change
  the advice about build order in the smallest-serious-stack section.

## 2. Test the descent hypothesis inside the corpus

The atlas's central claim is that systems build the ascent and skip the descent.
There is a sharper, falsifiable version available:

> **Systems with automatic background derivation are less likely to carry a
> tombstone than systems without.**

The reasoning is that re-derivation is what makes a tombstone necessary, so the
systems that most need one are the ones that have it least. Both variables are
extractable — `background` is already a matrix column, `tombstone` a capability
flag. If the correlation is *positive* instead, the atlas's framing is wrong in
an interesting way and should say so.

## 3. Where did the tombstone come from? — **ANSWERED**

Resolved 2026-07-28 from RainBox's git history. They are not independent.

The chain, with timestamps from `git log`:

| Time (29 Jun 2026) | Commit | What |
| --- | --- | --- |
| 15:07 | `58793dd` | "comparison of memory systems" — nine repo reports, an overview, and the two report-format templates that became this atlas's methodology pages. **Zero prior mentions of "tombstone" anywhere in the RainBox repository.** |
| 15:07 | (same commit) | The survey's Verel report credits it with "rejected-value tombstones to prevent laundering". The survey's *RainBox* report says "it does not implement Verel-style rejected-value tombstones". The overview's recommendations list `rejected_value` and "keep rejected tombstones". |
| 15:25 – 15:59 | `edbc7e4` → `c315632` | Design spec plus three rounds of review. |
| 16:06 | `e0a0082` | Implementation plan, 14 TDD tasks. |
| 16:08 | `af9ce12` | `tombstone table + trust columns on memory_claim`. |

Sixty-one minutes from survey to schema. The mechanism is **Verel's**; RainBox
adopted it because the survey that became this atlas flagged its absence.

**What this does to the headline number.** "Two of fifty-eight" reads as two
teams independently reaching a hard idea. The truth is one invention and one
adoption, by the person running the survey — so the field has produced this
mechanism *once*. That strengthens the negative finding and weakens any reading
of it as convergent discovery. Recorded on the
[pattern page](../content/patterns/rejected-value-tombstone.md) and disclosed in
the [RainBox report](../content/systems/rainbox.md).

### And where Verel got it

Traced the same day, from a full clone of `amitpatole/verel`. It was not designed
either — it was forced by adversarial testing, in one evening on 28 June 2026:

| Round | Finding | Result |
| --- | --- | --- |
| 7 | "rejection wasn't durable across supersede-then-restate: reject *paris* → supersede with *london* (rebuilds CANDIDATE, erasing the verdict) → restate *paris* + attest → VERIFIED" | `rejected_values` introduced; the gate refuses any value ever rejected for that key |
| 8 | TTL pruning deleted the tombstone, "reopened the supersede-then-restate launder after ~90 idle days" | `REJECTED` made prune-exempt |
| 9 | NFKC divergence — the gate compared `fact.text.strip().lower()` | NFKC-canonical rejection |
| 12 | key collisions, unbounded ledger | injective `make_key`, bounded ledger |

The repository shows at least twelve numbered red-team rounds overall, most run
with multiple adversaries and described as empirical.

**Two consequences for the atlas.** First, rounds 8 and 9 are empirical
confirmation of two tradeoffs the pattern page had listed as reasoning — a
tombstone that expires is not a tombstone, and normalization is where the real
work is. Both were found by attacking the mechanism, not by thinking about it.
Second, the full chain is now: an adversary forced the mechanism into Verel; the
survey that became this atlas found it there and flagged its absence in RainBox;
RainBox adopted it the same day. **Nobody in this corpus arrived at negative
memory by designing for it.**

That suggests a hypothesis worth more than the co-occurrence questions above:
the mechanisms this atlas finds missing may be missing because they are only
discoverable by attack, and almost nobody red-teams a memory layer.

**Method note worth keeping:** the RainBox half took four `git log -S` queries
against a repository already on disk; the Verel half took a full clone and four
more. Provenance questions about this corpus are usually this cheap and almost
never asked.

## 4. Does capability count track anything?

Age, size, whether the project is commercial, whether it has funding. The
`analyzed_at` dates and repository metadata are already collected by
`check_freshness.py`. Plausible and untested: capability count tracks **age of
the memory subsystem** rather than size or backing — mechanisms get added after a
failure teaches you they were needed.

If true, it reframes the negative findings: the field is not careless, it is
young, and the atlas is measuring maturity rather than quality.

## 5. What does the drift data say about the field?

The first freshness run gave 34 current, 22 stale. Running it monthly produces a
time series: which systems are actively developed, which have frozen, and whether
memory subsystems specifically churn faster than their host projects. That is a
public-interest dataset nobody else has, and it accumulates for free now the
script exists.

## 6. Do the near-misses cluster?

The rubric's strictness produces a specific list of systems that *almost* carry
each capability. If near-misses cluster around one flag, that flag's definition
may be drawing the line in the wrong place — a definition that many systems
narrowly miss is either measuring the right rare thing or measuring badly, and
which one should be established rather than assumed.

## 7. Is there a pattern for memory between agents?

**Open, and a genuine gap in the library.** Raised by an outside review, checked
against the eighteen pattern pages: every one of them models *one* agent and
*one* store. Scope as a first-class key separates agents so they cannot see each
other's memory; nothing describes what happens when they should.

The concrete case: agent A records a fact, agent B's execution produces a
failure that contradicts it. Today that is either invisible (separate scopes) or
a plain contradiction inside one scope, resolved with no notion that two
different actors with different evidence disagree. The scope lattice in
[Verel](../content/systems/verel.md) comes closest — `graduate()` promotes a
verified belief to a parent scope as a *candidate*, deliberately not as verified,
which is a real answer to "whose belief is this now" — but it is promotion, not
negotiation.

**Before writing a pattern page, check the corpus.** The atlas's standard is that
a pattern is reported from code, and the tombstone page exists as a cautionary
example of how thin two instances look. Search the multi-agent systems already
reviewed for any conflict handling that is actor-aware rather than value-aware.
If the answer is nothing, that is a finding to state plainly, not a page to write.

**Not to be confused with** decay, which a reviewer also proposed as a future
direction. That one already exists — [decay and reinforcement](../content/patterns/decay-and-reinforcement.md),
including the separation of reachability from truth that the proposal was
reaching for.

## Method note

All six are computable from `content/systems/*.md` plus the freshness data. None
requires standing up a system, running a benchmark, or asking a maintainer. Given
that the notes elsewhere describe expensive future work, this is the cheap pile
and it should probably come first.

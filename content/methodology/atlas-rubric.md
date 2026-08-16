---
title: The Atlas Rubric
eyebrow: Methodology
description: The seven capabilities every system is judged against, the evidence threshold for each, why these seven and not others, and what a missing mark does and does not mean.
root: ../..
page_kind: methodology
---

Every system report opens with a row of seven marks. Those marks drive the
[capability index](../../capabilities/) and the filters on the
homepage, so they need to mean something precise and the same thing everywhere.
This page is that definition.

## What a mark means

A capability is marked present **only when the mechanism was found in code at
the pinned commit**. Not in a README, not in a roadmap, not in a design document
describing intent, and not inferred from a plausible-sounding module name.

**And not from a system's own assessment of itself, however well built.** One
system — [Verel](../../systems/verel/) — now ships a module that runs a live
behavioural probe per capability and prints a score against this rubric. It is a
good mechanism and the report says so. It earns no marks. A self-assessment is a
claim about code, and this page exists because the atlas reads code instead of
claims; a self-assessment that happens to be *correct* changes nothing, because
the atlas would have no way to tell the correct ones from the rest without doing
the reading anyway. When I checked that module I found its release notes claimed
a score its own probe does not produce from an installed wheel — which is the
argument in miniature.

A dash means **not found**. It does not mean impossible, planned-and-missing, or
badly built. Several systems here carry a dash on a capability their design
deliberately does not need — [OptMem](../../systems/optmem/) has no scope key
because it is one store for one person, and calling that a deficiency would be a
category error.

Marks are deliberately **strict and binary**. A three-state "partial" column was
considered and rejected: nearly everything is partial at some resolution, so the
middle bucket absorbs every hard case and the column stops discriminating. The
strictness is what makes the counts mean anything — and the near-misses, which
are the interesting part, are named in the prose of each report and in the index
rather than smuggled into a half-mark.

## The seven

### Rejected-value tombstone

**Present when:** there is a durable record of a *rejected value*, keyed on the
value, so later extraction cannot silently re-assert it.

**Not this:** supersession chains, archival, `deleted_at`, delete-sync markers
(what [claude-mem](../../systems/claude-mem/) calls tombstones), or a `rejected`
status on a row. Those are all keyed on a *record*; re-extraction produces a new
record and walks straight past them.

**Why it is on the list:** it is the widest gap *this corpus has found* —
nineteen systems of 291, and the corpus is an opportunistic collection rather
than a sample, so that is a fact about what has been read and not a prevalence
figure for the field. It is invisible on every published benchmark, and it is the mechanism
that decides whether "forget that" survives the next background pass.

### Explicit trust state

**Present when:** discrete epistemic status exists as a field rather than a
confidence score, including at least one state that withholds a memory from
being treated as true.

**Not this:** a float. A confidence number answers "how sure" and gets used for
ranking; a state answers "may this be acted on" and gets used for filtering.
Systems that collapse them cannot express "I have this on record but do not
believe it".

**Why:** it is the difference between a store of claims and a store of beliefs.

### Bi-temporal validity

**Present when:** when a fact was true is tracked separately from when the system
recorded or expired it.

**Not this:** a single `created_at`, or an `updated_at` that overwrites.

**Why:** without it, "where did I live last March" and "what did we believe last
March" are the same query, and correcting a fact destroys the ability to audit
the period when the wrong value was in force.

### Scope enforced in retrieval

**Present when:** a stored scope key — user, project, agent, tenant — is applied
as a filter on the read path.

**Not this:** a scope stored as a tag or metadata field that nothing consults
when retrieving. Storing a boundary is not enforcing one.

**Why:** it is the cheapest catastrophic failure in the set. One assertion —
write to project A, query from project B — catches it, and the leak is
unrecoverable once material has reached a prompt.

**What this mark does not cover**, and the limitation is worth stating because
the count is the highest of the seven: it measures the *read path only*. It says
nothing about write authorization, whether background consolidation respects the
same boundary, whether cache and embedding keys include scope, or whether
deletion reaches every scoped copy. A summary spanning two projects has crossed a
boundary the retriever would have enforced.

### Append-only mutation audit

**Present when:** there is a named append-only event record of memory
*mutations* in the system's own store.

**Not this:** a log of retrieval or feedback — that is the other half of the
[append-only memory audit](../../patterns/append-only-memory-audit/) pattern and
does not tell you what changed. Not git history either, which is a real
mechanism and a different one, noted in prose where it applies.

**Why:** "why does the system believe this" is unanswerable without it, and it
is the difference between a correction you can review and one you have to trust.

### Human review surface

**Present when:** there is a place a person inspects, approves, or adjudicates
memory content, before or after it takes effect.

**Not this:** a memory UI that only displays. Viewing is not reviewing.

**Why:** fully automatic memory, memory a person can review before it takes
effect, and memory a person authors are three different products with three
different failure modes, and the distinction is usually invisible from the
outside.

### Negative retrieval assertion

**Present when:** committed evaluation cases assert that particular material must
**not** be retrieved.

**Not this:** ordinary recall tests, however thorough.

**Why:** every scope claim, every deletion claim, and every correction claim in
this atlas ultimately rests on an assertion of this shape. The negative
retrieval assertion is carried by seventy-six repositories
of two hundred and ninety-one, and they are not all
asserting the same thing: the
[benchmarks page](../../benchmarks/#5-what-gets-measured-and-what-does-not)
separates the ones asserting about *content* from the ones asserting about a
*scope boundary*, and only two are recorded asserting it about a value that was
*corrected* — [Verel](../../systems/verel/), and [Memora](../../systems/memora/),
whose suite asserts that a superseded memory must not appear under default
search or default list and that the explicit forensic mode still returns it.
That is the harder and more useful version.

**What the marks actually are, because they are not all the same thing.**
Every one of them is a committed case asserting that
material must not appear somewhere. The 2026-08-08 re-score put **27 of the
then-37 on a read path**, which is this definition; 20 about a particular value
and 7 about a scope boundary. The rest keep material out of something that is not a retrieval
result — a serialized projection, an assembled preamble, the next summarization,
a file on disk, a write decision. Those are real tests and several are the most
interesting thing in their report. They are not negative *retrieval* assertions,
and a reader who wants this heading read strictly should use **27**. The full
re-score, system by system, is in
[what the negative_eval mark actually counts](https://github.com/neoneye/agent-memory-atlas/blob/main/notes/2026-08-08-what-the-negative-eval-mark-actually-counts.md);
it also names the one mark that cites no case at all and should probably be
dropped.

**Three numbers appear above and they are not the same kind of number.** The
negative retrieval assertion count — seventy-six systems of two hundred and
ninety-one — is live, checked against report frontmatter on every build. Thirty-seven
and twenty-seven are dated: what the corpus held, and what the re-score found in it,
on 2026-08-08. Every mark awarded since was judged against the strict definition
at the top of this section, but **the read-path share has not been recomputed** —
so 27 describes a smaller corpus and is not a current strict reading.
Recomputing it means re-reading every marked test suite, which is what
`capability_evidence:`'s `subsystem` field exists to spread across future
readings rather than do in one pass.

The flags were left unchanged at the re-score deliberately. Dropping ten would
delete the fact that ten more systems ship committed must-not tests, which is
rare enough to be worth counting; renaming the mark would move a goalpost under
a published number. The split is published instead, and
`capability_evidence:`'s `subsystem` field carries it per report as the
[migration](#open-work-on-this-rubric) proceeds.

**This paragraph read "three repositories" until 2026-08-07** — true when the
mark was rare, left standing as the count reached thirty-seven, and sitting
directly under the definition it was supposed to scope.

## Why these seven

They were chosen against one filter: **does its absence cause a failure the
system cannot detect?**

Retrieval quality is not on the list, though it is what most comparisons measure,
because a bad ranker produces a visibly worse answer and someone notices. A
missing tombstone produces a *confident* answer built on a value the user
already rejected, and nothing in the system knows. Scope leakage, silent
re-derivation, unreviewable correction, and untested negative cases share that
property: they fail quietly.

The seven also split cleanly into the three commitments this atlas argues for —
evidence before belief (audit, bi-temporal), scope before ranking (scope
enforced), and correction before scale (tombstone, trust state, human review,
negative evals).

They are not a maturity score. A system with six marks is not better than one
with two; it is *differently shaped*. [Memory Engine](../../systems/memory-engine/)
governs access more thoroughly than anything else here and knows nothing about
whether a memory is true. [OptMem](../../systems/optmem/) carries one mark and is
one of the most carefully reasoned designs in the corpus. Read the marks as a
map of what a system chose to solve.

## How to dispute a mark

The definitions above are the whole test. If a system implements one of these and
the report says otherwise, that is a defect in the review and worth reporting —
with the file and symbol, since a mark is a claim about code at a specific
commit and is refuted the same way it was made.

The marks are declared in each report's `capabilities:` frontmatter, and the
build fails if a report omits the key entirely, so "nobody looked" and "assessed,
carries none" are distinguishable states rather than the same blank.

## Staleness

A mark is a claim about code at a pinned commit, which makes it auditable and
makes it age. `scripts/check_freshness.py` compares every pinned revision
against its repository's current default branch, and a weekly job reports the
drift, so "which reports have fallen behind" is a list rather than a worry.

It reports and never fails. A drifted pin does not make a report wrong — the
report was true of that commit and still is — it makes the report less useful as
a description of the project today, and re-reading a system is the expensive part
that no amount of automation removes.

## Known limits

- **Marks are assigned by one reviewer** reading code, not by running it — and
  that reviewer is a language model working from the repository, directed and
  reviewed by one person who commits the result. This page did not say so until
  30 July 2026. It belongs here because it
  changes how a mark should be weighed: the reading is fast, consistent about
  applying a definition, and prone to a specific failure — producing something
  *plausible* where the code says something adjacent. Three instances from a
  single day are recorded in the
  [methodology hazards note](https://github.com/neoneye/agent-memory-atlas/blob/main/notes/2026-07-28-methodology-hazards.md),
  including one wrong mark that survived two months. The countermeasure is the
  same one this page already demands of everyone else: a claim names a file and a
  symbol, so it can be checked without trusting whoever made it.
- **Strictness cuts both ways.** A system with a nearly-complete mechanism reads
  the same as one with nothing, which is why the near-misses are named in prose.
- **Every claim about deletion stops at the system's own boundary.** A report
  says what the code under review does when asked to forget; it does not follow
  the call into the vector index below it, and until 3 August 2026 no review
  had. Reading four engines settled what is on the other side: the deleted
  vector is never returned by a subsequent search, so no mark here is wrong in
  that direction — but on Chroma, Qdrant and LanceDB the **embedding itself
  survives** until a vacuum, segment optimize or prune that the memory system
  does not schedule, and LanceDB's default keeps the version containing the
  deleted data for seven days. pgvector is the one that zeroes the vector. This
  is a limit of the unit of review rather than of the definitions: the atlas
  reviews repositories, and this failure lives in a dependency they share. The
  evidence is in the
  [comparative report](../../compare/#the-layer-below-delete-what-the-storage-engine-does-with-the-vector).
- **The scope mark is the shallowest**, for the reason given above.
- **Seven axes cannot describe a memory system.** They describe the failures this
  atlas has found to be common, expensive, and silent. The reports carry the rest.
- **The rubric can now be aimed at.** At least one system has implemented these
  capabilities with the atlas in view and named commits after the marks. That is
  a reasonable thing for a maintainer to do and the mechanisms are real ones. It
  also means a count of marks is, from here on, partly a measure of who has read
  this page — so the marks describe shape, and the prose has to carry whether a
  mechanism was reached by need or by checklist. Where the atlas can date that,
  it says so: the [tombstone's provenance](../../patterns/rejected-value-tombstone/)
  is traced to a red-team finding rather than a rubric, and it predates this page.

## Open work on this rubric

Named here rather than in a private list, because a known defect that is not
written down is indistinguishable from one nobody has found. None of these is
fixed yet.

- **~~Re-score all thirty-seven `negative_eval` marks against one wording.~~
  Done, 2026-08-08.** 27 of the 37 assert about a read path; 10 assert about a
  projection, a preamble, a summarization, a file, or a write. The split is
  stated under the definition above and the working is in
  [the note](https://github.com/neoneye/agent-memory-atlas/blob/main/notes/2026-08-08-what-the-negative-eval-mark-actually-counts.md).
  One follow-up remains open: [Pydantic AI
  Harness](../../systems/pydantic-ai-harness/) is the only report that asserts
  the mark and cites no case, and needs a re-read at its pin.
- **A mark names a capability but not the subsystem it protects.** `capabilities`
  is a flat comma-separated string, so a system whose scope filter guards its
  conversation store and whose negative test guards a different path presents in
  the capability index as one coherent system with both.
  [DeepCode](../../systems/deepcode/) is the clearest case and its own report
  says so in prose that the frontmatter cannot carry. Filtering the corpus by two
  marks can therefore return a system where no single memory path has both.

  **Partly addressed.** Reports may now carry a `capability_evidence:` block —
  one record per mark, `subsystem | file | symbol | test` — and
  `scripts/check_capability_evidence.py` validates its shape, refuses to let
  coverage fall, and prints every report whose marks name more than one
  subsystem. Four reports are migrated: DeepCode, [Aeris](../../systems/aeris/),
  [Prime Agent](../../systems/prime-agent/) and
  [Microsoft Agent Framework](../../systems/agent-framework/). The three carrying
  more than one mark all came out **split**, which is the point: Aeris earns
  `negative_eval` on a model-facing projection rather than on retrieval, Prime
  Agent earns it on conversation compaction, and DeepCode's scope and audit marks
  cover a SQLite conversation store that its Markdown notes never touch. Agent
  Framework carries a single mark and so cannot split, but its record says the
  thing that matters anyway — `scope_enforced` sits on an in-tree harness while
  the framework contract the report is named for has no scope at all. Every one
  of those facts was already in the prose. None of it was in the data.

  **Ten of 269 marks are covered**, so the number to watch is coverage, not the
  four. `test: unknown` appears in six of the ten and is written rather than
  guessed: the report named the mechanism and did not name a test for it, and
  inventing one here would repeat the fabrication this atlas has already caught
  itself at. The remaining 259 need a re-read each.
- **~~The admission rule and the corpus disagree at the edges.~~ Resolved,
  2026-08-08 — the rule moved, not the corpus.** [AutoGen](../../systems/autogen/),
  [Sovereign](../../systems/sovereign/) and [Google ADK](../../systems/adk-python/)
  store something durable with no correctable identity and are in anyway. The
  [comparative report](../../compare/#reading-this-report) now states the
  exception in the rule instead of leaving it to be found by reading four
  reports against it: a memory contract widely built against is admitted
  *because* it cannot express a correction, since excluding those would remove
  the clearest cases of the gap this atlas exists to describe. Two things
  follow. It is an editorial judgement, not a mechanical test, so the corpus
  boundary is reproducible only to the extent that someone agrees with it. And
  a review noted that [Aeris](../../systems/aeris/) was named as a fourth case
  of this — it is not: its beliefs carry a status enum that moves
  `Active | Weakening | Revised | Abandoned | Contradicted`, which is correction
  with identity. Storing no *text* is not the same as having nothing to correct.
- **Two axes the seven marks do not carry, named by a survey that coded 435
  works.** *Always-On Agents* ([arXiv:2606.30306](https://arxiv.org/abs/2606.30306),
  29 June 2026) reads persistent state along six axes — authority, scope,
  mutability, provenance, recoverability, actionability — of which four map onto
  marks here and two do not.

  **Authority** asks who or what licenses a record to influence an action, as
  distinct from the agent merely holding it. The nearest thing on this page is
  `human_review`, which asks whether a person can inspect, not whether a grant
  exists and is still current. The nearest thing in the corpus is
  [AgentRecall-X](../../systems/agentrecall-x/), where a human correction marked
  `authoritative` returns `verdict: "blocked"` against a proposed action and
  loses that standing when its measured precision falls. One instance is not
  enough to define a mark against, and the survey
  ([arXiv:2606.30306](https://arxiv.org/abs/2606.30306)) puts the axis at 72 of
  435 works — its rarest.

  **Recoverability** asks whether a decision taken on a bad record can be traced
  and repaired. Two systems here carry it:
  [NeuraKeep](../../systems/neurakeep/), whose append-only audit stores `before`
  and `after` per mutation, derives an `undoable` flag from whether a `before`
  exists, and restores the prior rows through an undo that records its own
  reversal; and [MythologIQ's Agent
  Memory](../../systems/agent-memory-doctrine/), which names rollback
  traceability as one of five invariants and implements the residue half of it.

  So rarity is not what keeps recoverability off the list: the 27 of 435 that
  same survey ([arXiv:2606.30306](https://arxiv.org/abs/2606.30306)) reports is a
  fact about the field rather than a reason here. What keeps it off is
  that two readings are not enough to say what separates a rollback from an undo
  button over a log nobody keeps, and a mark awarded on a loose definition is the
  failure this page records below for `audit_log`. The definition is the work,
  not the count;
  [a proposal](https://github.com/neoneye/agent-memory-atlas/blob/main/notes/2026-08-12-what-would-make-rollback-a-mark.md)
  states one in three clauses and the corpus sweep that would test it before
  anything is added.

  Both omissions have one origin: the seven were chosen against failures found by
  reading implementations, which under-weights a failure whose implementations
  are rare. Recording the gap is the answer while the definitions are missing;
  adding a column that reads `—` for 258 rows is not.

- **No second reader.** Every mark on every report comes from one LLM reviewer
  directed by one person, with no blinded re-review and no inter-rater agreement
  figure. The [methodology hazards
  note](https://github.com/neoneye/agent-memory-atlas/blob/main/notes/2026-07-28-methodology-hazards.md)
  records what that has already cost — five of seven `audit_log` marks failing a
  re-audit among them. An agreement study over twenty to thirty of them would
  put a number on the error rate instead of a list of anecdotes.

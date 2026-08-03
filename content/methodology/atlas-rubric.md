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

**Why it is on the list:** it is the single widest gap in the field, it is
invisible on every published benchmark, and it is the mechanism that decides
whether "forget that" survives the next background pass.

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
this atlas ultimately rests on an assertion of this shape, and three repositories
of the whole corpus make one. Two of the three assert it about a *boundary*; only
[Verel](../../systems/verel/) asserts it about a value that was corrected, which
is the harder and more useful version.

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
  reviewed by one person who commits the result. This was not stated here until
  30 July 2026, when an outside reader inferred it correctly from the reports and
  the atlas noticed it had never said so. It belongs on this page because it
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

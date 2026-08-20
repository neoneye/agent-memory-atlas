# Ninety-four notes, clustered — what this project has actually been writing down

**Status:** survey of `notes/` itself. No atlas content changed; three
observations about the shape of the pile, and one standing debt named.
**Origin:** the question of what the notes directory has become, asked after it
passed ninety files. `notes/README.md` describes each note; nothing described
the set.

---

## Executive summary

Ninety-four dated notes, written between 2026-07-28 and 2026-08-20 and not
counting this one, alongside 308 system reports and 21 pattern pages. They fall
into ten kinds, and the split is the finding:

| # | Cluster | Notes | What it is for |
|---|---------|------:|----------------|
| A | Candidate triage | 8 | where the corpus came from, and what a submitted list is worth |
| B | Exclusions | 12 | the scope boundary, argued one repository at a time |
| C | The literature | 13 | papers and surveys read against the corpus, in both directions |
| D | Outside reviews | 10 | reviews of the atlas, every checkable claim checked |
| E | Method failures | 12 | how this review process fails, with instances |
| F | The rubric | 9 | what gets measured, what does not, and why |
| G | The unbuilt program | 9 | harnesses and protocols specified and not shipped |
| H | Corpus economics | 9 | freshness, marginal value, and the project's own position |
| I | Delivery | 4 | what the reader actually receives |
| J | Transferable findings | 8 | defect classes and design lessons from other people's code |

Three things follow from the distribution.

**The boundary got more writing than the acquisition.** Twelve notes argue why
a repository is *not* a memory system against eight that record where candidates
came from. The exclusions are the more reusable half: each one is a test of the
definition, and the definition is what the seven marks are applied to.

**The fastest-growing cluster is the project auditing itself.** Twelve
method-failure notes, seven of them written in the last three days covered
here. Every one carries an instance rather than a
principle, which is why they transfer: the strongest of them would be worth
reading by someone who never opens a system report.

**The unbuilt program is the standing debt, and it is not shrinking.** Nine
notes specify a kernel, an eval suite, a deletion harness at two levels, a
latency probe, a conformance protocol and a phased sequencing of all of them.
One shipped in full and one is partially done; the executable core of it — every
harness — is unbuilt. That is disclosed on the benchmarks page and in `AGENTS.md`,
so it is honest rather than hidden — but the ratio to shipped checkers, which
came out of cluster E and not out of cluster G, says which kind of proposal this
project actually completes: the one that guards a claim it already publishes.

A fourth pattern is chronological rather than structural. The July notes are
outward-facing — triage, surveys, reviews, "what should be in the corpus". From
[widening and its falling marginal value](2026-08-09-widening-and-its-falling-marginal-value.md)
onward the centre of gravity moves inward, to re-reads, evidence records, mark
definitions and the process's own defects. The corpus stopped being the thing
under construction and became the thing under audit.

---

## The clusters

### A — Candidate triage: where the corpus came from

Eight notes, each working a submitted or found list end to end and recording the
disposition of every entry, including the refusals.

**Most significant:**
[a tokenomics list, triaged](2026-08-09-a-tokenomics-list-triaged.md) and
[seventy-one repositories from an outside corpus](2026-08-09-seventy-one-repositories-from-an-outside-corpus.md).
The first is the method finding, the second is the volume record.

**Most significant insight:** an awesome-list entry describes what a project is
*for*, and a memory system is usually not what its host is for. Eight of 73
projects on a token-cost list had a memory system underneath and not one was
filed under *Memory* — so a category join finds nothing a grep of the source
would not have found better. The corollary, from
[a teaching corpus](2026-08-14-a-teaching-corpus-and-the-prior-art-it-was-citing.md),
is the gap a `source_url` join structurally cannot see: not an uncovered
repository, but a covered report leaning on an unread one.

### B — Exclusions: the scope boundary, one repository at a time

Twelve notes recording something read carefully and then *not* given a report.
They exist because an exclusion with no written reason is indistinguishable from
an oversight, and because several excluded repositories hold mechanisms worth
stealing.

**Most significant:**
[a handoff protocol, and the durable thing that is not a belief](2026-08-14-a-handoff-protocol-and-the-durable-thing-that-is-not-a-belief.md)
and
[three coding agents, and where their memory isn't](2026-08-07-three-coding-agents-and-where-their-memory-isnt.md).

**Most significant insight:** the boundary test is not durability, it is
falsifiability — *could the surviving thing be false?* An idempotency key, a
schedule, a correlation identifier and a phase all persist and none of them can
be wrong, so none of them is memory. The one-line form,
from [three repositories and a harness that is not memory](2026-08-04-three-repositories-and-a-harness-that-is-not-memory.md):
a harness that persists is not a memory that believes. The cheapest instrument
for applying it, from
[a coding agent whose search is the user's](2026-08-14-a-coding-agent-whose-search-is-the-users-not-the-models.md),
is the tool registry: if the model cannot query the store, it is a product
feature and not agent memory.

### C — The literature, read against the corpus

Thirteen notes taking a paper, survey, benchmark list or bibliography and
checking it against what the reports found — with the traffic running both ways,
since several of them corrected claims the atlas had already published.

**Most significant:**
[the field's own survey, read against the atlas](2026-07-29-memory-survey-forms-functions-dynamics.md),
[the database people arrived at the same four](2026-08-09-the-database-people-arrived-at-the-same-four.md),
and
[the corpus held the answer; the rubric had no column](2026-08-20-the-corpus-held-the-answer-the-rubric-had-no-column.md).

**Most significant insight:** two independent frames — a 107-page survey of the
field, and a data-management vision paper — arrive at this atlas's central
mechanism from outside, one of them proving that append-only storage cannot
satisfy it. That is the strongest external support the tombstone argument has,
and it is not adoption evidence. Against it sits the limit named on the last day
covered here: reading more systems does not produce a new axis, a different
decomposition does, and evidence for an unnamed axis accumulates invisibly in
prose until something else supplies the category.

### D — Outside reviews of the atlas, checked

Ten notes triaging reviews and proposals from other models and readers. The
house rule is visible in every one: every checkable claim gets checked, the
declines are argued rather than asserted, and the condition that would reverse a
decline is recorded.

**Most significant:**
[the gaps were placement, not content](2026-08-18-the-gaps-were-placement-not-content.md),
[a review that found the undisclosed method](2026-07-30-a-review-that-found-the-undisclosed-method.md),
and [declined proposals](2026-07-28-declined-proposals.md) as the standing
register.

**Most significant insight:** two triage classes now have several data points
each. When a review reports a rendering defect, check the rendered artifact
before answering; when it reports a missing capability, check the corpus — and
then check *placement*, because the material is usually already written and two
clicks from where the complaining reader was standing. The second, sharper
finding is about the reviews themselves: two of three favourable reviews
invented their final sentence at the point of maximum claimed evidence, which
makes the error location predictable rather than anecdotal.

### E — Method failures and self-audits

Twelve notes on how this review process fails, each with at least one instance
that reached publication or nearly did. The fastest-growing cluster, and the one
with the most reusable content.

**Most significant:**
[hazards in this review process](2026-07-28-methodology-hazards.md) as the
register,
[the same bug twice in one session](2026-08-19-the-same-bug-twice-in-one-session.md)
for the sharpest lesson, and
[the producer check and a corpus audit](2026-08-18-the-producer-check-and-a-corpus-audit.md)
for the widest sweep.

**Most significant insights**, in the order they matter:

1. **Prose in a commit message is a record, not a control.** A blanket sha
   replace corrupted history entries, was caught, was written up as a lesson —
   and was repeated hours later across eight reports, three of them already
   pushed. The three-line grep that would have failed the build both times is in
   the note. This is the single most transferable thing in the directory.
2. **A grep scoped to the wrong files returns exactly what a real absence
   returns.** Negative claims fail silently. Two published ones failed on the
   same day, and
   [the vocabulary probe lies](2026-08-19-the-vocabulary-probe-lies.md) adds
   eight instances of the inverse — a probe that looked clean and was wrong in
   both directions until the hits were read.
3. **Stale prose inherits the credibility of the generated numbers beside it.**
   Thirteen stale numerators in one day, every one sitting next to a correct
   generated figure. This produced `check_claim_counts.py`, which is the pattern
   the project repeats: a finding becomes a checker or it recurs.
4. **An evidence record is a dated citation, not a durable one** — true at the
   commit it was written against and unverified at every commit after. Writing
   one is also the deepest audit of a mark available, because it asks *where
   exactly*, which the rubric never requires.
5. **"Find the producer", not "grep the callers."** Declared-and-unwired is this
   atlas's most common finding and nothing in the workflow asked for the check;
   fifty-one reports carried one because someone thought to look.

### F — The rubric: what gets measured, and what does not

Nine notes on the seven marks — re-scoring holders against the strict wording,
arguing about candidate columns, and declining most of them with the condition
that would reopen the question.

**Most significant:**
[what the `negative_eval` mark actually counts](2026-08-08-what-the-negative-eval-mark-actually-counts.md),
[the strong-form tombstone subset](2026-08-07-the-strong-form-tombstone-subset.md),
and [what would make rollback a mark](2026-08-12-what-would-make-rollback-a-mark.md).

**Most significant insight:** the blocker on a new column is almost never rarity
and almost always *definition*. Rollback's rarity argument expired when two
systems shipped one; what has never existed is a definition that discriminates a
real rollback from a database transaction. The same shape recurs for ownership,
authority and friction. Naming an axis in the open-work section without awarding
it is the honest middle, and a mark awarded on a loose reading is worse than no
mark — the standard that made the two re-scoring sweeps worth running, since
both found the flags correct and published the *split* instead of changing a
count.

### G — The unbuilt program: harnesses, protocols, conformance

Nine notes specifying executable work. One of them shipped in full — the agent
protocol's catalogue and its validator, built the day it was proposed — and the
pattern cookbook is partially done. Every harness is specified and not built.

**Most significant:**
[the harness this page does not ship](2026-08-12-the-harness-this-page-does-not-ship.md),
[the deletion harness, level 1 and level 2](2026-08-12-deletion-harness-level-1-and-level-2.md),
and
[the conformance run the atlas does not run](2026-08-09-the-conformance-run-the-atlas-does-not-run.md).

**Most significant insight:** a harness shipped with only a passing fixture
proves nothing about whether its assertions discriminate, so the deliberately
leaky store that *fails* exactly the steps it was built to fail is the deliverable
and the passing one is the fixture. The same asymmetry governs the conformance
design: **not running is not failing**, so a self-run submission is only ever
evidence *for* a mechanism and can never become a scoreboard. And the sequencing
note's own rule is the reason none of this has quietly started:
[a phased program](2026-08-09-a-phased-program-and-where-to-abandon-it.md) sets
each gate before it becomes inconvenient, and phase 3's gate is a finding, not a
submission.

### H — Corpus economics and the project's position

Nine notes on the cost side: what re-reading is worth, how fast the corpus ages,
what widening buys, and what it means that the reviewed systems have started
reading their reports.

**Most significant:**
[widening and its falling marginal value](2026-08-09-widening-and-its-falling-marginal-value.md),
[the corpus has a half-life](2026-08-09-the-corpus-has-a-half-life.md), and
[the atlas is being read by the systems it reviews](2026-08-19-the-atlas-is-being-read-by-the-systems-it-reviews.md).

**Most significant insight:** the bar for a candidate is *worth the pin if a
pattern might move*, not *a report can be written* — and by that bar, batch
throughput is the wrong thing to optimise, because seventy reports in a day is
also seventy new pins in a queue nobody re-reads. The consequence named twelve
days later is sharper: an upstream that acts on a finding makes that finding
stale, so **a sharp report has a half-life and should be re-read before an old
one**. Being right is not being current.

### I — Delivery: what the reader actually receives

Four notes on the gap between what a page contains and what arrives — rendering,
navigation, and one measurement that turned a complaint into arithmetic.

**Most significant:**
[the atlas read without JavaScript](2026-08-12-the-atlas-read-without-javascript.md)
and
[the A–Z index: two rules for one field, and then none](2026-08-18-two-rules-for-one-field-and-then-none.md).

**Most significant insight:** a field that needs a rule to decide whether to show
it is usually a field that should not be shown, and the signal was in the first
measurement — 279 of 301 rows printing the same identity three times. Beside it,
the delivery version of the same idea: content that exists only in a `title`
attribute has not been delivered to a text extractor, a printout, Reader mode, a
keyboard or a touch screen, which is how a reviewer can name all seven marks and
still call the criteria a black box.

### J — Transferable findings from reading other people's code

Eight notes whose subject is a defect class or a design lesson rather than a
system, a review or this project. They are the clearest candidates for readers
outside the atlas.

**Most significant:**
[a test that restates a constant](2026-08-19-a-test-that-restates-a-constant.md),
[a failure that reads as empty](2026-08-20-a-failure-that-reads-as-empty.md), and
[one field asked two questions](2026-08-19-one-field-asked-two-questions.md).

**Most significant insights:** a test that pins the literal value of the constant
it covers moves with the bug and asserts the inversion — assert the property the
constant exists to satisfy. A loader that returns the empty value on read failure,
composed with a save that appends to whatever the loader returned, makes a
corrupted store and an empty store indistinguishable to every test that does not
deliberately corrupt one. And a judgment field with two writers meaning different
things by the same value — "checked and failed" against "could not check" — is a
conflation that only shows up when its writers and readers are enumerated
separately.

---

## The three observations, stated once

**1. Ten kinds is nine kinds of writing plus one kind of debt.** Clusters A–F and
H–J all produce something durable: a disposition, a boundary argument, a
corrected claim, a checker, a definition, a rule. Cluster G produces
specifications. The project's completion rate on the first nine is high and on
the tenth is close to zero, and the notes are candid about it — but nine notes is
a large investment in a category holding one shipped artifact and no harness, and
the honest question is whether that cluster should be built or closed.

**2. The method-failure cluster is the most valuable thing here and the least
discoverable.** Its best items — the sha-replace recurrence, the vocabulary
probe, the producer check, the test-restates-a-constant lesson — are engineering
findings with no dependence on agent memory at all. Two of them survive
downstream as one-line house rules in `AGENTS.md`, compressed past the instance
that makes them convincing and linking nowhere; the rest are reachable only by
reading this directory, which is not on the site.

**3. The one-instance problem.** The rubric will not award a mark on one
instance, and several of these notes are one-instance findings promoted to rules
anyway — the re-pin rule, the empty-read defect class, the placement triage class
before its fifth data point arrived. That is defensible for a process rule, where
the cost of a false rule is a wasted check and the cost of a missing one is a
published error, and it is worth saying out loud that the standard is
deliberately looser here than in the corpus.

---

## Detailed breakdown

Every note, by cluster, in the order it was written.
`notes/README.md` carries what each one found; this lists what each one is *for*.

### A — Candidate triage (8)

| Note | Role |
|---|---|
| [twenty-suggestions-triaged](2026-07-30-twenty-suggestions-triaged.md) | first submitted list worked end to end; established the disposition table |
| [a-reddit-thread-triaged](2026-07-30-a-reddit-thread-triaged.md) | first input from readers who had not read the atlas; the star-velocity argument that hardened the no-adoption rule |
| [two-lists-of-candidates-triaged](2026-08-03-two-lists-of-candidates-triaged.md) | curated list against raw search dump; the recommendation scored bottom on mechanism |
| [nine-repositories-triaged](2026-08-04-nine-repositories-triaged.md) | refusal grounds reused rather than re-argued; the licence caveat |
| [three-repositories-and-a-harness-that-is-not-memory](2026-08-04-three-repositories-and-a-harness-that-is-not-memory.md) | one report from three URLs; the harness/memory line stated in one sentence |
| [a-tokenomics-list-triaged](2026-08-09-a-tokenomics-list-triaged.md) | 73 candidates in fifteen batches; the category-join method finding |
| [seventy-one-repositories-from-an-outside-corpus](2026-08-09-seventy-one-repositories-from-an-outside-corpus.md) | the volume record: seventy reports, nothing left unexamined |
| [a-teaching-corpus-and-the-prior-art-it-was-citing](2026-08-14-a-teaching-corpus-and-the-prior-art-it-was-citing.md) | the citation gap a URL join cannot see; one 2026-08-09 disposition reversed |

### B — Exclusions (12)

| Note | Role |
|---|---|
| [a-coherence-coordinator-not-a-memory-system](2026-07-29-a-coherence-coordinator-not-a-memory-system.md) | first exclusion written up as an argument rather than a skip |
| [a-harness-whose-traces-are-published-and-whose-code-is-not](2026-08-06-a-harness-whose-traces-are-published-and-whose-code-is-not.md) | what can be reconstructed from traces alone, and what that cannot support |
| [a-paper-and-its-official-implementation](2026-08-06-a-paper-and-its-official-implementation.md) | SOTA claims against an unchecked To-Do; read the To-Do list first |
| [a-harness-that-reinvented-the-tombstone](2026-08-07-a-harness-that-reinvented-the-tombstone.md) | excluded and mined: three mechanisms kept from a non-system |
| [the-goedel-machine-lineage](2026-08-07-the-goedel-machine-lineage.md) | an optimizer's state is not a memory; two transferable moves kept |
| [three-coding-agents-and-where-their-memory-isnt](2026-08-07-three-coding-agents-and-where-their-memory-isnt.md) | the most-cited memory in coding agents is a prompt plus file tools |
| [an-audit-layer-that-shows-one-trajectory-twice](2026-08-08-an-audit-layer-that-shows-one-trajectory-twice.md) | fixtures published as evidence; the most persuasive variant because it looks finished |
| [a-mirror-that-agrees-to-forget](2026-08-09-a-mirror-that-agrees-to-forget.md) | derived-copy deletion discipline from something that never claimed to remember |
| [a-coding-agent-whose-search-is-the-users-not-the-models](2026-08-14-a-coding-agent-whose-search-is-the-users-not-the-models.md) | the tool-registry test: can the model query it |
| [a-handoff-protocol-and-the-durable-thing-that-is-not-a-belief](2026-08-14-a-handoff-protocol-and-the-durable-thing-that-is-not-a-belief.md) | the falsifiability boundary, reached from the protocol side |
| [the-framework-that-explains-the-deepseek-correction](2026-08-14-the-framework-that-explains-the-deepseek-correction.md) | why plugin composition makes "implemented" and "present" independent facts |
| [a-fork-a-successor-and-an-editor](2026-08-16-a-fork-a-successor-and-an-editor.md) | a re-entry condition, attached earlier, checked and found still unmet |

### C — The literature (13)

| Note | Role |
|---|---|
| [symbolic-prior-art](2026-07-28-symbolic-prior-art.md) | the lineage the atlas does not cover; unresolved, deliberately |
| [a-reading-list-triaged](2026-07-29-a-reading-list-triaged.md) | nine papers, no report added, three published claims changed |
| [memory-survey-forms-functions-dynamics](2026-07-29-memory-survey-forms-functions-dynamics.md) | the field's survey of itself; its vocabulary lacks the atlas's central mechanism |
| [memorypapers-against-the-atlas](2026-07-29-memorypapers-against-the-atlas.md) | 200 papers with the security category the surveys lack |
| [security-research-names-the-column](2026-07-29-security-research-names-the-column.md) | four capability columns derived independently from threat models |
| [selective-forgetting-that-is-not](2026-07-29-selective-forgetting-that-is-not.md) | a benchmark competency renamed by its citers; the repository disagrees |
| [the-forgetting-benchmark-in-a-bibliography](2026-07-29-the-forgetting-benchmark-in-a-bibliography.md) | the one paper scoring deletion compliance, found in citations, listed nowhere |
| [the-constant-was-fixed-for-thirty-arms](2026-08-09-the-constant-was-fixed-for-thirty-arms.md) | the RRF k=60 provenance, and why "sweep it" is insufficient advice |
| [the-database-people-arrived-at-the-same-four](2026-08-09-the-database-people-arrived-at-the-same-four.md) | the tombstone as a proved correctness condition; one pattern clause narrowed |
| [the-papers-the-reports-did-not-read](2026-08-09-the-papers-the-reports-did-not-read.md) | eleven paper-backed systems whose reports cite no paper; a skill step added |
| [the-loop-this-atlas-keeps-naming-has-a-number-now](2026-08-10-the-loop-this-atlas-keeps-naming-has-a-number-now.md) | the self-grading loop measured; no report, because the code 404s |
| [two-long-context-papers-and-the-boundary-of-what-memory-is-for](2026-08-14-two-long-context-papers-and-the-boundary-of-what-memory-is-for.md) | what bounds a memory layer's job from above and below |
| [the-corpus-held-the-answer-the-rubric-had-no-column](2026-08-20-the-corpus-held-the-answer-the-rubric-had-no-column.md) | an outside decomposition names an axis three reports had already answered |

### D — Outside reviews (10)

| Note | Role |
|---|---|
| [declined-proposals](2026-07-28-declined-proposals.md) | the standing register, with the condition that would reverse each decline |
| [pattern-gap-analysis](2026-07-28-pattern-gap-analysis.md) | an external 20-pattern list checked; the real gap was internal (29 named, 17 pages) |
| [a-review-that-found-the-undisclosed-method](2026-07-30-a-review-that-found-the-undisclosed-method.md) | a reader reconstructed the method from the reports and was right; disclosure followed |
| [two-ai-reviews](2026-07-30-two-ai-reviews.md) | every claim held except the one carrying a direct quotation |
| [the-layer-below-delete](2026-08-03-the-layer-below-delete.md) | the buried critique was the valuable one; four vector engines read below `update_delete` |
| [the-log-and-the-projection](2026-08-03-the-log-and-the-projection.md) | a same-morning claim half retracted; naming versus mechanism |
| [a-third-review-and-the-second-invented-quotation](2026-08-04-a-third-review-and-the-second-invented-quotation.md) | the invented-final-sentence pattern, second instance |
| [the-compare-page-as-a-tool](2026-08-04-the-compare-page-as-a-tool.md) | the first review that measured rather than argued; all seven measurements verified |
| [the-fourth-review-and-the-second-broken-diagram](2026-08-13-the-fourth-review-and-the-second-broken-diagram.md) | the rendering triage class gets its second data point |
| [the-gaps-were-placement-not-content](2026-08-18-the-gaps-were-placement-not-content.md) | four reviews, one real gap; the placement triage class |

### E — Method failures and self-audits (12)

| Note | Role |
|---|---|
| [methodology-hazards](2026-07-28-methodology-hazards.md) | the hazard register; the wrong-scope grep is the best-evidenced entry |
| [a-null-control-and-a-drifted-list](2026-08-03-a-null-control-and-a-drifted-list.md) | a re-read that changed no mark and found a drifted published list |
| [the-superlative-audit-first-pass](2026-08-04-the-superlative-audit-first-pass.md) | 294 superlatives split into checkable and judgement; four of seven counts stale |
| [the-count-claim-checker](2026-08-06-the-count-claim-checker.md) | thirteen stale numerators, and the checker that now guards them |
| [the-guidance-was-already-in-context](2026-08-08-the-guidance-was-already-in-context.md) | four failures of following loaded instructions; the build stayed green through all four |
| [the-producer-check-and-a-corpus-audit](2026-08-18-the-producer-check-and-a-corpus-audit.md) | the missing workflow step, plus fifty reports audited for marks that launder it |
| [a-re-pin-is-a-claim-about-the-whole-report](2026-08-19-a-re-pin-is-a-claim-about-the-whole-report.md) | verifying one criticism is not re-reading; the report split across two versions |
| [evidence-records-rot-and-only-a-re-read-finds-it](2026-08-19-evidence-records-rot-and-only-a-re-read-finds-it.md) | evidence coordinates rot while the mark holds; four rules for writing them |
| [nothing-moved-is-when-to-audit-the-report](2026-08-19-nothing-moved-is-when-to-audit-the-report.md) | no diff means every disagreement is yours; the cheapest audit available |
| [the-same-bug-twice-in-one-session](2026-08-19-the-same-bug-twice-in-one-session.md) | a lesson written down did not prevent its own recurrence; the grep that would have |
| [the-vocabulary-probe-lies](2026-08-19-the-vocabulary-probe-lies.md) | eight instances of a probe wrong in both directions; five exclusion rules |
| [the-evidence-record-is-a-review-instrument](2026-08-20-the-evidence-record-is-a-review-instrument.md) | writing the record audits the mark deeper than the rubric asks |

### F — The rubric (9)

| Note | Role |
|---|---|
| [refusal-as-a-lens](2026-07-28-refusal-as-a-lens.md) | systems converge on architecture and diverge on refusals; an axis proposed early |
| [rare-mechanisms-and-useful-inversions](2026-08-06-rare-mechanisms-and-useful-inversions.md) | rarity in an opportunistic corpus is not originality; retractions tabled |
| [the-strong-form-tombstone-subset](2026-08-07-the-strong-form-tombstone-subset.md) | nine holders re-read against the pattern's own definition; a taxonomy instead of a count |
| [what-the-negative-eval-mark-actually-counts](2026-08-08-what-the-negative-eval-mark-actually-counts.md) | 37 holders re-read after a drift claim; flags held, split published |
| [what-would-make-rollback-a-mark](2026-08-12-what-would-make-rollback-a-mark.md) | the rarity argument expired, the definition never existed |
| [which-marks-could-be-execution-grounded](2026-08-12-which-marks-could-be-execution-grounded.md) | read / reproduced / executed as a per-mark tier; the constraint is cooldown, not tooling |
| [a-memory-type-axis-and-why-machinery-is-the-wrong-one](2026-08-13-a-memory-type-axis-and-why-machinery-is-the-wrong-one.md) | half accepted, half declined, with the declined half argued |
| [what-a-friction-column-could-actually-say](2026-08-13-what-a-friction-column-could-actually-say.md) | the gap is enforcement of an existing field, not a new column |
| [there-is-no-ideal-memory-only-a-frontier](2026-08-19-there-is-no-ideal-memory-only-a-frontier.md) | why the ideal-memory request produced the tensions page instead |

### G — The unbuilt program (9)

| Note | Role |
|---|---|
| [atlas-kernel-proposal](2026-07-28-atlas-kernel-proposal.md) | a reference implementation plus the paired broken configuration |
| [executable-eval-suite](2026-07-28-executable-eval-suite.md) | the deletion and contradiction tests as runnable code |
| [pattern-cookbook](2026-07-28-pattern-cookbook.md) | a copy-pasteable artifact per pattern; partially done |
| [the-atlas-as-an-agent-protocol](2026-08-07-the-atlas-as-an-agent-protocol.md) | the one that shipped: `AGENTS.md`, test ids, build brief, `use-the-atlas` |
| [a-phased-program-and-where-to-abandon-it](2026-08-09-a-phased-program-and-where-to-abandon-it.md) | the gates, set before any of them became inconvenient |
| [the-conformance-run-the-atlas-does-not-run](2026-08-09-the-conformance-run-the-atlas-does-not-run.md) | burden inverted without inventing a certificate; not running is not failing |
| [deletion-harness-level-1-and-level-2](2026-08-12-deletion-harness-level-1-and-level-2.md) | the implementation plan, with a falsifiable prediction at level 2a |
| [the-harness-this-page-does-not-ship](2026-08-12-the-harness-this-page-does-not-ship.md) | the atlas's own criticism applied to itself; the leaky store is the deliverable |
| [the-cheapest-of-the-ten-metrics](2026-08-12-the-cheapest-of-the-ten-metrics.md) | write-to-readable lag in forty lines; four design points that are the whole value |

### H — Corpus economics and position (9)

| Note | Role |
|---|---|
| [editorial-backlog](2026-07-28-editorial-backlog.md) | the first backlog; de-duplication and re-analysis priority |
| [research-questions](2026-07-28-research-questions.md) | six questions the committed corpus can answer with no new reviews |
| [the-other-agent-memory-atlas](2026-07-29-the-other-agent-memory-atlas.md) | a same-named project checked; what a derived confidence score is worth |
| [automating-re-analysis](2026-08-04-automating-re-analysis.md) | prioritisation, not detection; stars in the scheduler behind a firewall |
| [the-corpus-has-a-half-life](2026-08-09-the-corpus-has-a-half-life.md) | the age distribution is bimodal; measured with no network call |
| [the-receipts-the-atlas-cannot-produce](2026-08-09-the-receipts-the-atlas-cannot-produce.md) | the atlas could not check a factual claim about itself |
| [widening-and-its-falling-marginal-value](2026-08-09-widening-and-its-falling-marginal-value.md) | the incumbent activity held to the same scrutiny as the proposals |
| [the-atlas-is-being-read-by-the-systems-it-reviews](2026-08-19-the-atlas-is-being-read-by-the-systems-it-reviews.md) | four upstream responses in a week; a sharp finding has a half-life |
| [when-the-systems-author-sends-a-patch](2026-08-19-when-the-systems-author-sends-a-patch.md) | the precedent: fold in what survives independent reading, close rather than merge |

### I — Delivery (4)

| Note | Role |
|---|---|
| [the-atlas-read-without-javascript](2026-08-12-the-atlas-read-without-javascript.md) | two confident criticisms, one root cause; every diagram degraded to source |
| [the-rubric-definitions-are-in-a-tooltip](2026-08-13-the-rubric-definitions-are-in-a-tooltip.md) | content in a `title` attribute has not been delivered |
| [two-rules-for-one-field-and-then-none](2026-08-18-two-rules-for-one-field-and-then-none.md) | a field needing a rule to show it is a field to delete |
| [measure-the-chrome-before-restyling-it](2026-08-19-measure-the-chrome-before-restyling-it.md) | "crowded" was a horizontal-scroll bug; the fix sized from arithmetic |

### J — Transferable findings (8)

| Note | Role |
|---|---|
| [what-survives-encryption](2026-07-29-what-survives-encryption.md) | a design note: the client is the boundary, similarity search is what breaks |
| [four-arc-agi-3-harnesses-converge-on-the-same-memory](2026-08-06-four-arc-agi-3-harnesses-converge-on-the-same-memory.md) | four independent harnesses put the log in charge and the notes on probation |
| [enforce-where-the-writer-cannot-reach](2026-08-13-enforce-where-the-writer-cannot-reach.md) | policy versus mechanism, with the adversarial test that separates them |
| [a-test-that-restates-a-constant](2026-08-19-a-test-that-restates-a-constant.md) | assert the property, not the literal; the general form for caps and TTLs |
| [one-field-asked-two-questions](2026-08-19-one-field-asked-two-questions.md) | enumerate a judgment field's writers and readers separately |
| [two-ways-to-be-wrong-about-your-own-benchmark](2026-08-19-two-ways-to-be-wrong-about-your-own-benchmark.md) | committed and independent are two axes; the page sorts on one |
| [a-failure-that-reads-as-empty](2026-08-20-a-failure-that-reads-as-empty.md) | a read failure and an empty store are the same value |
| [the-good-pattern-is-one-subsystem-away](2026-08-20-the-good-pattern-is-one-subsystem-away.md) | rigor attaches to the subsystem that visibly needed it, not to the property |

---

## For next time

The clustering is cheap to redo and the categories are the durable part, so a
later pass should place new notes rather than re-derive the scheme. Two of the
observations above are actionable and one is not:

- **Cluster G wants a decision, not another note.** Build the level-1 harness or
  close the cluster with the reasoning, because a tenth specification changes
  nothing.
- **Cluster E wants a reader.** Its best items are engineering findings with no
  dependence on agent memory, and they are currently reachable only through this
  directory.
- **Cluster J will keep growing on its own.** It is a by-product of reading code
  carefully, which is the activity the project is already committed to.

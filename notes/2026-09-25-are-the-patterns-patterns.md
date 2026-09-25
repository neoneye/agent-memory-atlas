# Are the patterns patterns?

**Status:** audit complete, and all five proposals applied on 2026-09-25 (see
[Applied](#applied) at the end). Three mark questions stay open.
**Method:** seven read-only reviewers, three patterns each, all at `4f9fa4874`
on 2026-09-25. Every pattern page was judged on four tests:

1. **Recurrence.** Count independent systems that implement the move *as the
   page defines it*, against the stance the page claims.
2. **Distinctness.** A move of its own, not another page restated.
3. **Evidence.** Each cited system's report supports what the page says. The
   most load-bearing claims were also checked against the source at the
   report's pin, fetched raw rather than cloned.
4. **Labels and counts.** The stance fits the evidence. No hand-written corpus
   counts. No contradicted "only" or "first".

353 claims were checked and 87 errors were verified. About seventy of the
checks went to pinned source code, not just the report.

## Verdict

Eighteen of the twenty-one are real patterns. Two restate another page, and
one has a single instance of its own definition. Six stances are wrong.

| Pattern | Verdict | Stance: page → evidence | Errors |
|---|---|---|---|
| append-only-memory-audit | real | reporting ✓ | 7 |
| bi-temporal-fact-validity | real | reporting ✓ | 2 |
| cache-preserving-injection | real | reporting ✓ (stronger than it claims) | 3 |
| decay-and-reinforcement | real; showcase wrong | reporting ✓ | 4 |
| evidence-before-belief | real | reporting ✓ | 1 |
| gate-the-expensive-path | real | reporting ✓ | 2 |
| governed-write-gateway | real; evidence mostly analogies | reporting ✓ | 2 |
| hybrid-retrieval-fusion | real | reporting ✓ | 5 |
| recoverable-background-work | real | reporting ✓ | 5 |
| resolve-not-just-detect | real | advocacy ✓ | 5 |
| scope-as-a-first-class-key | real | reporting ✓ | 10 |
| trust-state-machine | real; exemplars stale | reporting ✓ | 7 |
| zero-llm-capture | real | reporting ✓ | 3 |
| rejected-value-tombstone | real | advocacy → **reporting or mixed** | 11 |
| memory-as-an-editing-surface | real | category-bound → **reporting** | 2 |
| pluggable-memory-provider | real | reporting → **mixed** | 3 |
| retrieval-hysteresis | real | category-bound → **reporting (cooldown) / advocacy (sticky)** | 3 |
| source-diverse-context | real | mixed → **reporting** | 4 |
| explicit-write-destination | **overlaps scope-as-a-first-class-key** | reporting, borderline | 3 |
| promotion-between-tiers | **overlaps trust-state-machine** | reporting, partly earned | 4 |
| skills-as-procedural-memory | **thin: one instance of its own definition** | reporting → **mixed** | 1 |

## What the stances got wrong

- **The tombstone is no longer advocacy.** 25 systems consult a value-keyed
  record on the write path (the page's own table), at least 22 of them
  independently, and 58 carry the mark. The page's "the field has produced this
  mechanism once" and the build's label *"Advocacy — one or two instances"* are
  both past. The history is still true and worth keeping: Verel's red-team
  origin, then an adoption, then independent arrivals.
- **Editing surfaces are not a roleplay category.** At least eight coding-agent
  tools let a person edit the store the model reads. Only RisuAI has all five
  verbs. The index's *"refined against very large user bases"* and the page's
  *"plausibly the most-exercised memory implementation"* are adoption claims,
  which the house rule forbids.
- **The cooldown half of hysteresis recurs outside roleplay.** qwen-code
  (checked in source), AIPass, memory-ts and Deja-vu all do it. The full
  sticky-plus-cooldown set is SillyTavern alone. The page's *"No
  extraction-based system in this atlas carries per-unit activation state"*
  is false.
- **Pluggable provider is two things.** The interface (about eleven host
  contracts) is common and is packaging. The memory move, carrying scope and
  deletion across the contract, rests on one or two contracts, so the page is
  `mixed`.
- **Source-diverse context's advocacy claim does not exist.** The index says
  the advocacy part is *"the negative-eval discipline inside it"*, and the page
  never mentions it. Counting MMR, about eighteen more reports qualify.
- **Skills as procedural memory** defines the move by its verification gate
  (*"Without the verification gate, this is just tagged notes"*). Only Voyager
  has that gate, and Acontext has part of it. The skill library itself is
  common. So the stance is `mixed`: reporting for libraries, advocacy for the
  gate.

## What overlaps

- **Explicit write destination** is stated by the scope page's own line
  *"Writes name an owning scope. Reads state which scopes are visible."*, and
  by its MIRIX paragraph. What it adds is "no default write target", which has
  three strict instances: llm-wiki-memory, Memory Engine and Membrane. That is
  a section of the scope page, not a page of its own.
- **Promotion between tiers** is covered by the trust-state page's *"make
  promotion … depend on that status"*. Its provenance veto is the same move as
  that page's Portable Handoff `cap_trust`. Its best examples (CLIO, Graphify,
  Hats, OmniIntelligence) sit on the trust page already. What stays distinct is
  movement between *storage* tiers (hot/cold, working/episodic), and the page
  never states that line.
- **Partial overlaps that are fine:**
  - zero-llm-capture's queue checklist restates recoverable-background-work.
  - The Gini temporal gate appears on two pages.
  - Daimon's "load-bearing log" on the audit page is evidence-before-belief by
    that page's own discipline.

## The errors, by kind

**Superlatives the corpus contradicts**, about 30. The page's own later
paragraphs are the usual refutation. Each of these has a named counterexample:

- *"the only system in the atlas that could"* — MetaClaw. Somnigraph and Uteke
  tuned their fusion constants in code.
- *"Every other state machine … forces a winner"* — Caura and dense-mem exclude
  `conflicted` and `disputed` on read.
- Membase *"the only … authenticated"* scope — OpenCompany, LoreKit and
  Pydantic also authenticate theirs.
- CSM *"only"* considered/injected audit — RainBox does the same, in source.
- Palazzo *"only"* precondition log — breadcrumbs and aimee.
- Aura and aimee *"the two"* tamper-evident logs — Midas has a hash chain;
  LoreKit and Utopia use RLS and triggers.
- Perseus *"the only one that refuses without storing"* — PLUR1BUS, Fireweed
  and Noosphere.
- Hermes *"the only system here whose memory design follows from the cache"*
  — Nuum, Reasonix and Hipocampus.
- Gate *"Nothing in this atlas measures its gate"* — Waku ships a
  labelled-case accuracy test.

**Stale after a re-read.** The mark moved or the code changed, and the page
did not.

- Trust page:
  - Graphify, CLIO and Daimon lost `trust_state` on 2026-09-19. CLIO's "nothing
    assigns the env vars" is false at the pin.
  - The Scope Recall paragraph describes 2.x.
- Tombstone page: PLUR1BUS, memoir, Memora and Scope Recall are called
  near-misses, and all four carry the mark.
- Scope page: Memory Engine's agent principal was dropped upstream by migration
  `018_remove_agents.sql`.
- Provider page: the TencentDB paragraph describes the pre-rewrite code.
- Gateway page:
  - PLUR1BUS's drift gate is live again.
  - Hestia's autowrite flag was removed and a test asserts it.
- Resolve page:
  - MateClaw has a resolve endpoint.
  - Nova has a periodic caller.
  - Memanto has eight dispositions, not five.
- Source-diverse page: OpenViking's `type_quota_recall.py` is absent at the pin.

**Claims the cited report does not contain.**

- The pluggable page's LightAgent and the skills page's ScienceClaw are outside
  the corpus.
- The PLUR1BUS starvation case exists only in a note.
- Hindsight's "deterministic-error filtering" is not in its report.
- The memoir "two sinks" history is not in its report.
- Some Daimon specifics go past its current report.

**Code misread, inherited from reports.**

- Mnemopi's Weibull table is imported only by a test, so recall uses one
  uniform decay.
- LoongFlow's temperature *falls* with diversity. The page says it rises, and
  the loop amplifies collapse instead of correcting it.
- Atomic Agent evicts its vote events and mutates `vote_score` in place, so
  the scores cannot be recomputed from the events.
- LlamaIndex blocks get no per-block budget, and the default priority is never
  truncated.
- Honcho's two message searches are separate paths, not fused.
- Helm's TF-IDF arm survives a failed import.
- Helix's `archive_belief` does append.
- Redis AMS forgetting is off by default.

**Hand-written counts.** Each is a defect under the placeholder rule, and most
have already drifted:

- The index's *"38 systems … or in 19"* sits beside a generated table showing
  87 and 58. It also says *"Three small repositories have the mechanism"* and
  *"a mechanism three repositories invented"*.
- Cache page: *"Five reports"*. At least ten report the failure.
- Scope page: *"four host contracts"* and *"Two systems"*.
- Pluggable page: nine, ten and four contracts in three places.
- Tombstone page: *"Twenty-four of the thirty"* where the table shows 25 of 31,
  plus seven ordinals.
- Zero-llm page: *"Five systems"*.
- Resolve page: *"four reports"*, followed by five names.

**Arithmetic.** *"Three gates at 95% each admit a fifth of what they should
not"*. 0.95³ is about 0.857, so the combined miss is about 14%.

## Defects in system reports

These were found while checking pages. Fixing only the pattern pages would
leave them published.

| Report | Defect |
|---|---|
| mnemopi.md:42, :100 | Weibull presented as the live recall curve |
| loongflow.md:71 | Temperature direction inverted |
| helix-agi.md:24, :65 | `archive_belief` said to append nothing |
| midas.md:15, :462 | "No caller-supplied event date", contradicted by :198 and the code |
| janus-graph.md:15, :200 | Enqueue time "preferred"; the body at :84 is right |
| memoir-cli.md:67 | Stale "none retracts it" beside a shipped `memoir_forget` |
| memanto.md:56 | Five dispositions; the pin has eight |
| openviking.md:108, :163, :296 | Cites a file absent at the pin |
| nanobot.md:39, :99 | `DreamRunProgress`, absent at the pin |
| context-mode.md:101 | "No UPDATE on the event table"; `renameSession` has one |
| redis-agent-memory-server.md | Omits that forgetting is off by default |
| helm.md:46, :493 | Independence claimed for repeats; the TF-IDF fallback contradicted at :463 |
| memos.md:61, :69 | A promotion formula not found in the pinned scheduler, probably copied from MemoryOS |
| elai.md:16 | `bitemporal` held on the defect for which Helm, Uteke and Atomic Agent were refused |
| llm-wiki-memory.md, openyak.md | `human_review` held for editing surfaces the narrowed rubric refuses elsewhere |

## Why this happened

The same failure that put thirteen wrong mark counts on the families page:
a re-read moves a report and nothing moves the pages that cite it. Pattern
pages are the worst case, because each cites dozens of reports and none is on a
re-read's checklist. The "only X here" sentences are the second cause. They are
true when written and falsified by the next addition, and the superlatives
ratchet counts them without verifying any.

## What was fixed now

- **The exemplar picks.** Three of the five trust-state picks (Graphify, CLIO,
  Daimon) and the first audit pick (Atomic Agent) were written from each
  page's prose on 2026-09-25 and did not carry the mark. They are replaced with
  OmniIntelligence, AgentDatabase, Hats and Magic Context on the trust page and
  Midas on the audit page. Each line is taken from the system's evidence
  record.
- **The check.** `check_pattern_exemplars.py` now requires every *Read these
  first* entry on a mark-backed page (tombstone, trust state, bi-temporal,
  scope, audit) to carry that mark, or to say in its line that it is the
  counterexample. Run against the pages before this fix, it names exactly the
  four bad picks.

## Proposed, in order

1. **Correct the 87 errors on the pages.** They are mechanical and verified,
   and the reviewers' line references are specific. One commit per page, with
   `remove-meta-narrative` run over each.
2. **Correct the fifteen report defects** through `reanalyze-memory-system`,
   as same-pin corrections with History entries.
3. **Restance the six pages, including the index and the build label.**
   *"Advocacy — one or two instances"* is a hard-coded string in
   `build_site.sh`.
4. **Fold explicit-write-destination into the scope page** as a section, and
   **narrow promotion-between-tiers** to storage-tier movement, or fold it into
   the trust page. Both change URLs, so both need a decision.
5. **Put pattern pages on the re-read checklist.** When a mark moves, grep
   `content/patterns/` for the slug. Longer term, a check that a pattern
   page never calls a system an instance of a mark it lacks, outside a marked
   counterexample, extends today's exemplar check to the whole catalogue.

## Applied

All five proposals were carried out on 2026-09-25, by the same seven reviewers, each editing only its own pages and reports:

- **Pages.** Every verified error is corrected on its page. Superlatives fell from 459 to 433 and filler phrases from 1,481 to 1,472, and both ceilings are lowered to match.
- **Reports.** Eighteen reports are corrected at their unchanged pins, each with a History entry. Five more than the fifteen listed above surfaced during the fixes: Atomic Agent, Memory Engine, Hermes Agent, Empryo and qwen-code. The rows of that list not fixed are the three mark questions under *Still open*.
- **Stances:**
  - The tombstone moves to `mixed`.
  - Editing surfaces and source-diverse context move to `reporting`.
  - Pluggable provider, skills, retrieval hysteresis and promotion between tiers move to `mixed`.
  - Explicit write destination moves to `advocacy`.
  - The `category-bound` bucket is retired. The build label reads *Advocacy — a handful of instances*.
- **Overlaps.** Both pages were narrowed rather than folded, which keeps their URLs and the pattern count:
  - explicit-write-destination now covers only refusing a write with no named destination (llm-wiki-memory, Memory Engine, Membrane).
  - promotion-between-tiers now covers only movement between storage tiers, and says where the line to the trust-state page runs.
- **Re-read checklist.** `reanalyze-memory-system` now requires a grep for the slug across the patterns, families, verdicts and overview pages whenever a mark or mechanism moves.

**Still open:**
- ELAI's `bitemporal`, and the `human_review` marks of llm-wiki-memory and openyak. These are mark decisions, not corrections.
- Several unverified superlatives that nothing contradicts. The reviewers listed them and left them.
- The meta-narrative that was already on the scope page.


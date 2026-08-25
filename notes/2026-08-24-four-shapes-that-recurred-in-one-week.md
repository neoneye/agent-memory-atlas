# Four shapes that recurred in one week

**Status:** synthesis. Written 2026-08-24 over roughly fifteen readings —
Heimdall, LongMemEval, NexusMem, Engram Alpha, Perseus Vault, Honcho, GENOME,
llmaker, Mnemopi, Graphnosis, Arcon (twice), AI Agent Automation, Silica,
Hillock, RCK, AutoResearchClaw, Orca, Weave, and one paper.
**Why:** each finding is recorded in its own report, and none of them was
visible as a *class* until several landed in the same week. Three have been
turned into repository changes; the fourth is a design rule I want written down
before it decays into a habit.

---

## 1. The assertion that cannot fail

The one worth the most. It appeared four times in unrelated repositories, and
one project had already generalised the fix.

Silica names the class: *"A metric that cannot fail reports PASS regardless of
the arm, and the gate reads as a result."* Its `evals/negative_controls.py` pins
each deterministic gate metric against fixtures of which **at least two must
disagree** — *"a metric stuck at 1.0 and a metric stuck at 0.0 are both dead"* —
and refuses to run a gate whose metric the registry does not know, before any
model work, *"so a dead metric costs zero tokens."* Its docstring lists four
times this bit them, with shas, including two metrics matching `\d+` against
citation IDs guaranteed to contain a letter, so *"two rows of its summary table
were decoration."*

The four instances found this week:

| Shape | Instance |
| --- | --- |
| Vacuous predicate | Arcon: `results.every(m => m.status !== ARCHIVED)` over a `beforeEach` database holding exactly one archived row |
| Computed and unasserted | Hillock: `verify_hillock.py` computes `passes` and `leaks` against the gate threshold and asserts `len(rows) == 30` |
| Comment instead of assertion | Weave: *"Unsupported claim is still quarantined deterministically"*, then both fixtures deleted |
| Suite that skips itself | Weave: every case returns early on `"skipping: no reachable database"` |

And one outside a test, which is the same defect: ai-agent-automation's
`retrieveMemory(..., minScore = 0.45)` never reads `minScore` — the identifier
appears on one line of the backend, the signature — while `agent.controller.js`
passes `0.45` explicitly. Intent documented at the call site, defeated in the
callee.

**Acted on.** Step 5 of `add-memory-system` now carries the check, the four
shapes, the greps, and the rule that a negative assertion which can pass on an
empty result does not earn `negative_eval`. Silica's harness is written up on
the benchmarks page.

**What makes it hard to see.** Every one of these reads correctly. The
predicate is the right predicate; the metric is the right metric; the comment
describes the right behaviour. Only the fixture, or the absence of a second
identifier, gives it away — which is why it survives review and why the check
has to be mechanical.

## 2. Declared-and-unwired has a direction, and the atlas was only naming one

The corpus has fifty-plus instances of a mechanism with no producer. Arcon's two
readings, eight days apart, showed the axis has more than one end, and the other
ends have different costs.

- **Written, never read.** Arcon's `PENDING_CONFIRMATION` at the first pin: the
  pipeline assigned it and the retriever ignored it, so the store's most careful
  decision had no consequence.
- **Read, never written.** Arcon's `CONTRADICTED` at the *second* pin, named in
  three exclusion lists and assigned by nothing; `MemoryScope.PROJECT`, queried
  by the cognitive processor and written by no path, so that branch returns empty
  and reports nothing. A missing producer makes a **filter dead weight** or a
  **query silently empty** — and the second is worse, because an empty result
  looks like an answer.
- **Neither.** Mnemopi's `memoria_facts` versioning columns — `version_id`,
  `previous_value`, `updated_msg_idx`, `valid_from_msg_idx`, `valid_to_msg_idx`,
  `source_memory_id` — created, migrated on every open, and touched by nothing
  in the repository.
- **Wired to a path that discards it.** AutoResearchClaw's `ExperimentMemory`
  constructed at `run_dir/experiment_memory`, and `EvolutionStore` — whose
  docstring promises lessons *"injected into future runs"* and whose own usage
  example uses a stable path — constructed at `run_dir/evolution` by both real
  callers. One argument decides whether a subsystem is memory or scratch space,
  and neither the signature nor the tests distinguish them.

**The rule I would add to a design review:** a status vocabulary should be read
in both directions before it is trusted, and a denylist makes the second
direction likely. Arcon's exclusion set is a five-value denylist written out in
two files; the allowlist form — `status === ACTIVE` — would have failed loudly
when a sixth value arrived instead of silently admitting it.

## 3. Silent degradation, and the one project that fixed it properly

Three systems this week swallow a failure on the only durable path they have:

- llmaker wraps every Redis call in a bare `except`, and
  `test_memory_degrades_when_redis_errors` **pins the behaviour** — so a caller
  cannot distinguish a saved session from a dropped one, and nobody can fix it
  without failing a test.
- GENOME's `_maybe_auto_detect_facts` catches its model call and its write, both
  at DEBUG, so an empty temporal layer and a working one look identical.
- AutoResearchClaw wraps store initialisation, lesson extraction and the skill
  hook in three broad `except`s that log and continue.

Availability over durability is usually the right call for a chat buffer or a
research pipeline. Degrading *silently* is a separate decision, and in all three
it was made by accident.

**Orca answers it**, in a repository that is not about memory at all.
`zod-salvage.ts` is 132 lines: tolerance declared **per field** so *"a corrupt
entry is dropped and the rest of the session survives, because one bad tab
record must not cost every worktree its state"* — and `collectSalvageDrops(parse)`
returns `{value, droppedPaths, droppedCount}` with example paths bounded at a
hundred. That is exactly the `skipped` count GENOME's row-skipping decoder was
missing and whose cost its report left as an open question.

**General rule:** any decoder that salvages should return what it salvaged *and*
what it dropped.

## 4. Label, gate, or both — and the ordering that makes it safe

Three systems reached the same fork this week and answered differently. Setting
them beside each other produces a rule I had not seen stated.

- **Silica labels.** A contested claim is rendered into the recall block as
  `| contested: <reason>`, so the model sees the claim and the dispute together.
  Defensible — a disputed claim is often the best available answer — and it
  cannot refuse.
- **Graphnosis conflates.** `deleteNode` writes `confidence = 0.1`, the same
  field daily decay lowers and reinforce-on-recall raises. Deleted, stale and
  doubted become one scalar.
- **Weave does both, in the right order.** `vector_search_claims` filters
  `AND c.status = 'active'` by default and widens to
  `IN ('active','contradicted')` only when a caller passes
  `include_contradicted` — and the admitted exception is *then* rendered
  `[CONTRADICTED]`.

**The rule: make the narrow set the default and the wide set an argument, then
label what you admit.** A forgetful caller gets the conservative behaviour; a
deliberate one gets the disputed claim *and* is told it is disputed. Every other
arrangement relies on the caller remembering.

Weave earns the mark on the gate. Silica does not, and the report says so
without treating the choice as a mistake.

## 5. The projects that measure against themselves

Worth naming as a class because it is the strongest maturity signal in the
corpus and it is rare enough to be diagnostic.

- **RCK** measured six axes against non-VSA baselines and reports the HRR
  substrate — the architecture the project is named for — wins none. It
  withdraws two published claims by name, and judges its own 1.0% cross-name
  resolution *worse* than a dict's 0.0% because *"the 1.0% is bundle crosstalk
  rather than alignment — a false positive, which is worse than the honest
  zero."*
- **GENOME** publishes that its own auto-consolidation is harmful at the default
  (0.454 → 0.092, McNemar p<0.0001), ships it off by default, and puts the
  warning in the constructor citing the result file by path.
- **Silica**'s supersede probe reports the margin by which its own gate barely
  works: *"2.09pp against a 2pp tolerance. A partial revert would slip under
  it."*
- **Hillock** keeps the rows where its numbers fell in a seven-row version
  table.

GENOME and RCK are the same author. Four projects, and the shape is the same:
the measurement is aimed at the thing the author is most attached to.

## What I would check first, next time

In rough order of how much each has paid off this week:

1. For every negative assertion, what does the fixture guarantee is *present*?
2. Read the status vocabulary in both directions — writers, then readers — and
   note which values appear in only one.
3. Grep every computed metric's identifier; if it appears once, it was not
   asserted.
4. For a store constructed with a path argument, find out what that path is
   relative to.
5. Read the skip path of an integration suite before quoting its pass count.
6. Find out whether a refusal reaches the *inference*, not only the write — RCK
   checks denials at chain induction and rule instantiation; Weave's
   `find_opposing` excludes rejected rows and is the only reader, so a refusal
   there does not survive a re-assertion.

---
title: "cortex-engine"
eyebrow: "\"You were wrong\" and \"the world changed\" are different verdicts"
description: "A contradiction is adjudicated into five outcomes before it becomes a signal, and only the genuine one penalises confidence — a supersession is routed to bitemporal succession instead."
root: ../..
page_kind: system
source_name: "fozikio/cortex-engine"
source_url: https://github.com/fozikio/cortex-engine
revision: 6045c41933b1d496d43ac10bad67560c87cf1445
revision_url: https://github.com/fozikio/cortex-engine/commit/6045c41933b1d496d43ac10bad67560c87cf1445
analyzed_at: 2026-08-09
capabilities: "audit_log"
stack_storage: "sqlite, files"
stack_retrieval: "graph"
stack_source: "seeded"
matrix:
  memory_unit: "A node — observation, belief, question or hypothesis — in a namespaced graph"
  storage: "SQLite, Firestore or JSON behind one CortexStore interface, with atomic transactions"
  retrieval: "Neighborhood aggregation, spreading activation, multi-anchor voting, FSRS scheduling"
  write: "observe and believe; a contradiction is adjudicated before it is recorded as a signal"
  update_delete: "A belief log holding old and new definitions with a reason, written transactionally"
  scoping: "One store per namespace; namespace names validated alphanumeric, not a read predicate"
  integration: "An MCP server with 60 tools, a REST surface with a destructive-tool blocklist"
  background: "Two-phase dream consolidation, wander, evolve, goal-directed prediction error"
  trust: "A confidence float penalised in proportion to adjudicator confidence"
  strengths: "Contradiction adjudicated into five outcomes, with supersession routed away from penalty"
  risks: "Many neuroscience-named mechanisms with no evaluation of any of them"
---

## 1. Executive Summary

cortex-engine is an MIT TypeScript memory layer with 60 MCP tools, three storage
backends behind one interface, pluggable LLM and embedding providers, and a long
list of neuroscience-derived mechanisms: NREM/REM dream consolidation, Thousand
Brains multi-anchor voting, epistemic foraging, Fiedler value graph health, FSRS
spaced repetition, prediction-error saturation detection.

**The mechanism worth the report is smaller than any of those and better than
all of them.** `src/tools/contradict.ts`:

> "Previously this recorded a CONTRADICTION signal on the caller's say-so. Now
> the (evidence, belief) pair is adjudicated first (NLI cross-encoder if
> configured, LLM fallback otherwise):
>
> - **genuine** → CONTRADICTION signal (priority 0.8) + confidence penalty on the
>   disputed memory, scaled by adjudicator confidence
> - **supersedes** → TENSION signal (priority 0.4), **no penalty — the world
>   changed; revise via believe() with valid_from instead of distrusting the
>   belief (bitemporal succession)**
> - **tension** → TENSION signal (priority 0.5), no penalty
> - **complementary** → no signal; the evidence supports the belief
> - **unrelated** → no signal"

**"You were wrong" and "the world changed" are different verdicts, and this is
the only system in the atlas that routes them to different mechanisms.**
Everywhere else, a superseded fact and a refuted fact both lose confidence — so a
belief that was correct until the user moved house gets treated exactly like one
that was never true, and the system slowly learns to distrust things that were
right at the time.

Three further details make it more than a taxonomy. The penalty is **scaled by
the adjudicator's own confidence** rather than applied flat. `complementary`
exists — evidence a caller *thought* contradicted the belief and actually
supports it produces no signal at all. And `force=true` preserves the old
caller's-say-so behaviour, so the adjudicator can be bypassed deliberately rather
than worked around.

**The second thing worth taking is a belief log written inside the same
transaction as the memory it revises** — section 7.

**The concern is that none of the neuroscience is evaluated** — section 10.

## 2. Mental Model

Nodes are observations, beliefs, questions and hypotheses in a namespaced graph.
Writing a belief appends to a belief log and updates the memory atomically.
Contradicting one goes through adjudication first. Background "dreaming"
consolidates in two phases.

```mermaid
flowchart TD
    O["observe(evidence)"] --> NEAR{"nearest existing memory"}
    NEAR -->|"temporal succession detected"| MSG["message: revise with believe(valid_from);<br/>TENSION signal tracks the pending revision"]
    C["contradict(evidence, belief)"] --> ADJ{"adjudicate: NLI cross-encoder,<br/>LLM fallback"}
    ADJ -->|genuine| G["CONTRADICTION signal, priority 0.8<br/>+ confidence penalty × adjudicator confidence"]
    ADJ -->|supersedes| S["TENSION signal, priority 0.4<br/>NO penalty — revise via believe(valid_from)"]
    ADJ -->|tension| T["TENSION signal, priority 0.5, no penalty"]
    ADJ -->|complementary| CP["no signal — the evidence supports it"]
    ADJ -->|unrelated| U["no signal"]
    C -.->|"force = true"| G
    B["believe(concept, new_definition, reason, valid_from?)"] --> EMB["embed BEFORE the transaction<br/>(network calls must not hold the writer mutex)"]
    EMB --> TX["withTransaction"]
    TX --> PB["putBelief: old_definition, new_definition,<br/>reason, changed_at, valid_from, valid_to"]
    TX --> UM["updateMemory: definition, embedding, updated_at"]
    D["dream"] --> NREM["NREM: cluster, refine, create"]
    D --> REM["REM: connect, score, abstract"]
```

## 3. Architecture

`src/` splits into `core`, `engines` (cognition, graph-metrics, adjudicate),
`tools` (the 60 MCP tools, one file each), `stores` (sqlite, firestore, json),
`providers`, `mcp`, `rest`, `namespace`, `federation`, `bridges`, `services`,
`triggers`, `plugins`, `cli`.

Three storage backends share one `CortexStore` interface with a
`withTransaction(fn)` primitive — "SQLite uses `BEGIN IMMEDIATE` with a per-store
mutex; Firestore uses `runTransaction` with a write-routing proxy" — and a
migration tool that clones between any pair of backends, "ID-preserving,
checkpointed, resumable, fails-loud on schema mismatch".

The tool catalogue is typed with `category`, `whenToUse` **and `doNotUse`**
metadata per tool. Publishing when *not* to call a tool is a small thing that
directly reduces the failure mode of a 60-tool surface.

32,000 lines of TypeScript.

## 4. Essential Implementation Paths

**Adjudicate** — `src/tools/contradict.ts` (the five outcomes `:1-20`),
`src/engines/adjudicate.ts` (`adjudicateContradiction`,
`MAX_CONFIDENCE_PENALTY`).

**Revise** — `src/tools/believe.ts` (`valid_from` parsing `:29-39`, the
embed-before-transaction comment `:50-53`, the atomic belief-plus-memory write
`:55-73`).

**Detect succession on write** — `src/tools/observe.ts` (`:120`, `:157`).

**Store** — `src/stores/sqlite.ts` (`beliefs` DDL `:319`, the `valid_from`
migration `:391`, `putBelief` `:872`), `src/stores/firestore.ts`,
`src/stores/json.ts`.

## 5. Memory Data Model

Memories carry a definition, an embedding, a confidence and timestamps.
`beliefs` is the revision log: `concept_id`, `old_definition`, `new_definition`,
`reason`, `changed_at`, `valid_from`, `valid_to`.

**`valid_from` is documented for exactly the right case**, in the tool schema:
"ISO date when the revised belief became true in the world (valid time) — e.g.
`2026-06-01` when recording in July that the user moved in June."

It is stored on both backends, read back by the row mappers, and — as far as this
reading found — **never used in a `WHERE` or `ORDER BY`**. So the valid-time
dimension is captured and available and no query filters on it, which is why the
`bitemporal` mark is withheld: the column records when the fact became true, and
nothing yet asks "what did we believe as of then".

That is a smaller gap than usual, because here the valid time has a *semantic*
job even unqueried — it is what the `supersedes` verdict routes the caller
towards, and it is what distinguishes a revision from a refutation in the log.

## 6. Retrieval Mechanics

Neighborhood aggregation, query-conditioned spreading activation, multi-anchor
voting, epistemic foraging, FSRS-scheduled review, locally-adaptive clustering
thresholds.

**Scope is structural.** `ctx.namespaces.getStore(namespace)` returns a store per
namespace, so isolation comes from which store is opened rather than from a
predicate — the same shape as several systems in this atlas, and it means
`scope_enforced` is not earned. Namespace names are validated alphanumeric, which
the README lists under SQL-injection prevention and which is also what makes the
per-namespace store path safe.

## 7. Write Mechanics

`believe()` is worth reading for two comments as much as for its behaviour.

**The transaction boundary is explained:**

> "Atomic: belief log + memory update commit together so we never end up with a
> belief entry that points at a memory that was never updated, or a memory whose
> history is missing the revision row."

Both failure directions named, in the comment above the code that prevents them.

**And the embedding is deliberately outside it:**

> "Embed BEFORE the transaction — LLM/network calls must never happen inside
> `withTransaction` (they hold the writer mutex open). See docs/concurrency.md."

A network call inside a write transaction is one of the most common ways a
memory system acquires mysterious lock contention, and it is called out at the
site with a pointer to the document.

There is no tombstone: `contradict` penalises confidence, `believe` rewrites the
definition and logs the old one, and nothing prevents a refuted value being
asserted again.

## 8. Agent Integration

An MCP server with 60 tools, a REST surface, hooks, skills, an OpenClaw plugin,
Docker, and setup scripts for both shells.

**The REST blocklist is a design idea worth naming.** Per the README, destructive
tools — `forget`, `dream`, `evolve`, `resolve`, `thread_resolve` — "are blocked
from the generic REST endpoint; they remain available via MCP for direct agent
access." Authorisation that depends on *which transport* the call arrived over is
an unusual and defensible model: the agent's own channel can consolidate and
forget; a generic HTTP caller cannot. This report did not locate the enforcing
list in the source, so the claim is recorded as documented rather than verified.

REST auth uses `crypto.timingSafeEqual`, and the plugin loader validates import
paths against trusted directories.

## 9. Reliability, Safety, and Trust

**One mark: audit log.** `beliefs` is an append-only revision record in the
system's own store, carrying the old definition, the new definition and a
`reason`, written in the same transaction as the memory update. That is exactly
what the mark certifies, and the transactional coupling makes it stronger than
most — the log cannot drift from the store it describes.

**Trust state — withheld.** Confidence is a float. The signals
(`CONTRADICTION`, `TENSION`) are separate records with priorities rather than a
status on the memory, so nothing on a memory says "do not treat this as true".
Given how carefully the adjudicator distinguishes the *kinds* of dispute, a
status field carrying that distinction is the obvious next step.

**Bitemporal — withheld**, per section 5. **Scope — withheld**, per section 6.
**Tombstone, human review, negative eval — no.**

**Two housekeeping notes.** `cortex.db-shm` and `cortex.db-wal` are committed to
the repository — SQLite sidecar files from a local run, harmless but stale. And
the security list in the README is specific and checkable in a way most such
lists are not (`timingSafeEqual`, path validation, parameterised LIMIT clauses,
alphanumeric namespace validation), which is a good sign about the rest.

## 10. Tests, Evals, and Benchmarks

**No paper, no benchmark, no committed results, and no evaluation of any of the
named mechanisms.**

The feature list is the longest in this batch and the most heavily
neuroscience-flavoured: NREM and REM consolidation phases, Thousand Brains
multi-anchor voting, epistemic foraging, the Fiedler value as a measure of
"knowledge integration", "PE saturation detection prevents identity model
ossification", information-geometric clustering thresholds, FSRS with
"consolidation-state-dependent decay profiles".

Some of these are real and locatable — `src/engines/graph-metrics.ts` computes
the Fiedler value, `src/engines/cognition.ts` uses it — and the adjudicator is
demonstrably implemented. What is absent is any measurement that any of them
improves retrieval, correction or anything else. There is an `experiments/`
directory; no results are reported in the README.

The atlas's position on this is the one it took for
[OpenMemory](../openmemory/): named mechanisms are cheap and evaluated ones are
not, and a reader cannot tell from the tree whether two-phase dream consolidation
beats a single pass. Here the gap matters less than usual, because the *single*
mechanism this report recommends — adjudicated contradiction — is legible enough
to evaluate by reading, and because the docstrings describe behaviour rather than
biology.

**I ran nothing.**

## 11. For Your Own Build

### Steal

- **Adjudicate a contradiction before recording it.** A caller reporting that
  evidence disputes a belief is a claim, not a fact, and taking it on the
  caller's say-so is how confidence scores get poisoned.
- **Separate "supersedes" from "genuine".** A belief that stopped being true is
  not a belief that was wrong. Penalising confidence for a supersession teaches
  the system to distrust things that were correct at the time — route it to a
  valid-time revision instead.
- **Include "complementary" in the outcome set.** Evidence a caller thought
  contradicted a belief and actually supports it should produce no signal, and
  you only find those by asking.
- **Scale the penalty by the adjudicator's confidence.** A hedged verdict should
  move the number less than a decisive one.
- **Keep the old behaviour behind a flag.** `force=true` records on the caller's
  authority, so the adjudicator is bypassable deliberately rather than routed
  around.
- **Write the revision log and the update in one transaction, and say why.**
  "So we never end up with a belief entry that points at a memory that was never
  updated, or a memory whose history is missing the revision row" — both failure
  directions named above the code that prevents them.
- **Keep network calls out of write transactions.** Embedding before
  `withTransaction` because the call would "hold the writer mutex open" is the
  kind of comment that saves a later contention investigation.
- **Give every tool a `doNotUse`.** On a 60-tool surface, telling the model when
  *not* to reach for something is worth more than another description.
- **Consider transport-dependent authorisation.** Destructive operations
  available over MCP to the agent and blocked on the generic REST endpoint is a
  clean separation of "the agent may forget" from "any HTTP caller may forget".
- **Make the migration tool fail loud on schema mismatch**, and checkpoint it.

### Avoid

- **Do not ship a dozen named cognitive mechanisms with no evaluation of any.**
  Fiedler values and REM phases are checkable claims; nothing in the tree checks
  them, and a reader cannot tell which of the twelve are load-bearing.
- **Do not store `valid_from` and never query it.** It is populated from
  caller-supplied valid time and no read filters on it, so "what did we believe as
  of then" is not yet answerable.
- **Do not leave the dispute kind out of the memory's own state.** The adjudicator
  produces a rich verdict and the memory ends up with only a smaller number.
- **Do not commit `.db-wal` and `.db-shm`.**

### Fit

Worth adopting if you want a rich cognitive tool surface over a store with real
transactional discipline and three interchangeable backends. The adjudicated
`contradict` is the reason to look, and it is small enough to lift into another
system: five outcomes, a confidence-scaled penalty, and a routing rule that sends
supersessions somewhere else.

Approach the neuroscience vocabulary as vocabulary until something measures it.

## 12. Open Questions

- **Where is the REST destructive-tool blocklist enforced?** The README describes
  it; the list was not located in the source.
- **Does anything read `valid_from`?** It is stored on all backends and no
  predicate uses it.
- **What is in `experiments/`?** No results are reported in the README.
- **How is the NLI cross-encoder configured, and what happens when it is not?**
  The docstring says LLM fallback; the selection logic was not traced.

## Appendix: File Index

**Adjudication** — `src/tools/contradict.ts` (the five outcomes and the `force`
escape hatch `:1-20`), `src/engines/adjudicate.ts`
(`adjudicateContradiction`, `MAX_CONFIDENCE_PENALTY`), `src/tools/validate.ts`,
`src/tools/ruminate.ts`

**Revision** — `src/tools/believe.ts` (the `valid_from` schema description `:20`,
parsing `:29-39`, the embed-before-transaction comment `:50-53`, the atomic write
`:55-73`), `src/tools/observe.ts` (the succession messages `:120`, `:157`)

**Storage** — `src/stores/sqlite.ts` (the belief row type `:138`, the mapper
`:233`, `beliefs` DDL `:319`, the `valid_from` column migration `:391`,
`putBelief` `:872-876`), `src/stores/firestore.ts` (`:206`, `:633`, `:834`,
`:1130`, `:1271`), `src/stores/json.ts`

**Cognition** — `src/engines/cognition.ts`, `src/engines/graph-metrics.ts` (the
Fiedler value), `src/tools/goal.ts`, `src/tools/dream.ts`

**Documentation** — `README.md` (the feature list, the security section, the REST
blocklist), `docs/concurrency.md`, `docs/storage-backends.md`,
`docs/tools-reference.md`

## History

**2026-08-09** — [`6045c41933b1d496d43ac10bad67560c87cf1445`](https://github.com/fozikio/cortex-engine/commit/6045c41933b1d496d43ac10bad67560c87cf1445) — first reading. Screened before reading; the tree was read, never installed, and no test was run. The REST destructive-tool blocklist is recorded as documented rather than verified in source.

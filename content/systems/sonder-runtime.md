---
title: "Sonder Runtime"
eyebrow: "A quarantine that checks the base rate before it blames"
description: "A self-modifying agent runtime whose distilled lessons are scored by the outcomes that followed them and quarantined when a loss run is statistically improbable for the lesson's own retrieval-frequency band — with blame deduplicated across co-retrieved lessons and a probation path back."
root: ../..
page_kind: system
source_name: "Krilliac/Sonder-runtime"
source_url: https://github.com/Krilliac/Sonder-runtime
revision: eb93f60d8380b096a6fefbf34c053fb20dccde4f
revision_url: https://github.com/Krilliac/Sonder-runtime/commit/eb93f60d8380b096a6fefbf34c053fb20dccde4f
analyzed_at: 2026-08-22
capabilities: "trust_state, scope_enforced, audit_log, negative_eval, tombstone"
capability_evidence:
  trust_state: "the lesson, moved by outcome statistics rather than by a writer | retriever.py:390 (`lesson_quarantine`), :309 (`band_loss_rate`), :372 (`_attribution`) | a lesson is active, quarantined or on probation, and the transition is computed rather than set: `lesson_quarantine` tests a loss run against the base rate for the lesson`s own retrieval-frequency band, `_attribution` deduplicates blame across lessons that were co-retrieved, and a later positive outcome rehabilitates. Quarantined lessons are dropped before ranking rather than down-weighted | tests/test_retriever.py:343 `test_positive_outcome_rehabilitates_quarantined_lesson`, and :274 for the lexical-fallback interaction"
  tombstone: "the distillation seam, keyed on the lesson text | sonder_runtime/adapters/memory_store.py:98 (`lesson_tombstones`), :2190 (`lesson_text_tombstoned`), grounded_extraction.py (`is_tombstoned_duplicate`) | the near-duplicate pruner deletes redundant lessons keeping one representative and writes a content-hashed tombstone, and distillation checks it before writing so a pruned value cannot be re-derived from a later interaction, returning `rejected_value`. It is keyed on the value rather than the row, and it does not cover quarantine — a quarantined lesson has no tombstone and can return through a fresh distillation | tests/test_lesson_pruner.py, tests/test_reflection.py"
  audit_log: "preference refinement, protected by triggers rather than by convention | sonder_runtime/adapters/memory_store.py:228 (`refinement_history`), :246-250 | every apply and rollback is journalled with optimistic version checks, and the table is append-only by construction: `refinement_history_no_update` and `refinement_history_no_delete` are BEFORE triggers that raise, so the log cannot be edited by the code that writes it | tests/test_refinement_transactions.py"
  scope_enforced: "interactions, tasks, preferences and sessions, filtered by project and an account scope the serving layer supplies | sonder_runtime/adapters/memory_store.py:197 (`account_scope`) | the scope key is stored on the row and applied as a filter on the read path, with the account scope coming from the authenticated serving layer rather than from the caller`s argument. Lessons are deliberately outside it — global procedural knowledge, stated as a design position rather than an omission | tests/test_task_http_scope.py"
  negative_eval: "retrieval, asserting a quarantined lesson does not reach the ranked set | tests/test_retriever.py | quarantined lessons are excluded before ranking and the suite exercises that boundary from both sides — a lesson driven to quarantine by repeated losses, and the same lesson rehabilitated by a later positive outcome, so the exclusion cannot pass by the retriever returning nothing | tests/test_retriever.py:274, :343"
stack_storage: "sqlite"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A distilled lesson — a concrete directive with an embedding and FTS text — plus the interaction it came from, the outcomes credited to it, preferences, facts and session summaries"
  storage: "One stdlib-only SQLite database with a dozen tables and an FTS5 virtual table; embeddings as BLOBs stamped with model and revision"
  retrieval: "Hybrid — embedding cosine at min_sim 0.62 unioned with FTS5 lexical, MMR-reranked (lambda 0.5), with quarantined lessons excluded before ranking"
  write: "A lesson-distillation state machine claims an interaction, extracts a concrete lesson, and refuses exact and semantic duplicates; outcomes are credited back to the lessons that were retrieved"
  update_delete: "Preferences carry a revision and every apply/rollback is journalled in refinement_history with optimistic version checks; a near-duplicate pruner deletes redundant lessons keeping one representative and writes a content-hashed tombstone so the pruned value cannot be re-distilled"
  scoping: "Interactions, tasks, preferences and sessions filter by project and an account_scope supplied by the authenticated serving layer; lessons are deliberately global procedural knowledge"
  integration: "A terminal runtime, REPL, headless service and MCP surface over one local database; the memory adapter is stdlib-only and importable"
  background: "Distillation, near-duplicate pruning, age-decay ranking, contradiction detection and quarantine, all driven by accumulated outcomes"
  trust: "A lesson is active, quarantined or on probation by outcome statistics; preferences carry confidence, evidence_count and an enabled flag; every outcome records who judged it"
  strengths: "Outcome-gated quarantine that deduplicates blame across co-retrieved lessons and tests a loss run against the lesson's own frequency-band base rate before suppressing it, with a probation path back"
  risks: "The whole loop trusts an outcome signal whose provenance is often machine or unknown; near-duplicate pruning now tombstones the rejected value, but quarantine still suppresses a lesson without one, so a quarantined lesson re-distilled from a fresh interaction can return"
---

## 1. Executive Summary

Sonder Runtime is a self-modifying terminal agent — Apache-2.0, ~260,000 lines
of Python across 743 files, with a code-rewriting loop (`selfmod.py`), a training
pipeline, an NPU broker, and a great deal else. Most of that is out of this
atlas's scope. What is in scope is a genuinely serious memory subsystem: a
stdlib-only SQLite adapter (`sonder_runtime/adapters/memory_store.py`, 3,632
lines) that stores **interactions**, the **outcomes** credited to them, and the
**lessons** distilled from them, and then lets the outcomes decide which lessons
keep being retrieved.

The unit that matters is a **lesson** — a concrete directive like *"Use
`collections.Counter` for frequency counting and `.most_common()` to find the
most frequent item efficiently,"* extracted from an interaction that went well,
embedded, and made retrievable. The atlas has many systems that store lessons.
What lifts this one out of the pile is that it closes the loop the field almost
never closes: **it credits the outcome of each interaction back to the lessons
that were retrieved for it, and uses that credit to quarantine lessons that keep
leading to losses.**

The quarantine is the report's headline, and it is careful in exactly the places
the atlas keeps finding this idea done badly:

- **Blame is deduplicated across co-retrieved lessons.** If five lessons are
  always retrieved together and the task fails, they cannot each claim the
  failure as independent evidence — "a cluster of lessons that always fail
  together cannot each claim the same failures." A test,
  `test_one_failure_cluster_no_longer_quarantines_its_whole_cohort`, pins it.
- **A loss run is judged against the lesson's own base rate.** Quarantine fires
  only when the run of losses is *improbable* for the loss rate of the lesson's
  retrieval-frequency band, "so a rarely-retrieved lesson is not punished for the
  unusual tasks that retrieval sends it." The test computes an explicit
  `p=0.006`.
- **Quarantine has a route back.** After a cooldown a quarantined lesson becomes
  eligible for sampled probation retrieval — a production path to a win — and a
  win lifts the quarantine on evidence rather than on a clock.

And the whole apparatus rests on **who judged the outcome**. The `outcomes`
table has a `source` column — `caller`, `machine`, `attributed`,
`self_curriculum`, `unknown` — that is `NOT NULL` with deliberately no default,
and the success-rate math weights caller-sourced outcomes over machine ones.
That is a direct, built defense against the self-grading failure the atlas
documents at length ([the reward-inflation
paper](../../compare/#known-limitations) is the theory; this is one of the few
implementations that acts on it).

The weakness is the same fact read from the other side. The loop is only as good
as the outcome signal, and in practice much of that signal is `machine` or
`unknown` — the code treats those categories with visible suspicion, which is the
right instinct and also an admission that the ground truth is thin. And the
rejected-value gap is now half-closed: near-duplicate pruning writes a
content-hashed tombstone that distillation refuses to re-derive, so a pruned
duplicate cannot come back — but quarantine still *suppresses* a lesson without
recording a rejected value, so a lesson quarantined for being harmful, then
re-distilled from a fresh interaction, can re-enter.

## 2. Mental Model

A memory is a **lesson**, and its life is governed by the outcomes of the
interactions that retrieve it.

```text
interaction happens        -> interactions row (task, retrieved_ctx, response, project, tier)
outcome lands              -> outcomes row (signal, reward, source ∈ {caller, machine,
                              attributed, self_curriculum, unknown})  -- source NOT NULL
distillation claims it     -> lesson_distillations state machine:
                              claimed -> stored | no_lesson | cancelled
                              refusing not_concrete, exact_duplicate, semantic_duplicate
lesson stored              -> lessons row + embedding + lessons_fts
lesson retrieved           -> lesson_usage row links (lesson, interaction)
outcome credited           -> lesson_usage.reward / outcome_source filled in
losses accumulate          -> quarantine if the run is improbable for the band's base rate
                              AND the lesson is individually answerable for them
quarantine                 -> excluded from retrieval; after cooldown, sampled probation;
                              a win exits, on evidence
```

Lessons are the procedural layer; three other durable kinds sit beside them.
**Preferences** are corrected beliefs with a `confidence`, an `evidence_count`,
an `enabled` flag and a `revision` — and every change to one is journalled. This
is the atlas's clearest example of a memory whose *state* is the whole point: a
lesson is `active`, `quarantined`, or `on probation`; a preference is enabled or
disabled at a version. `trust_state` is earned without strain.

How a memory dies has three distinct paths, and the distinction between them is
the design's sophistication:

- **Quarantine** — a lesson stops being retrieved because the outcomes credited
  to it went bad, statistically and answerably. Reversible by a probation win.
- **Near-duplicate pruning** — a lesson is deleted because another says the same
  thing (cosine ≥ 0.93), keeping one representative.
- **Age-decay ranking** — a lesson loses ground over a 30-day half-life to
  fresher lessons, blended with usage evidence; not deletion but demotion.

One of these paths now records a *rejected value* and one does not. Near-duplicate
pruning writes a `lesson_tombstones` row keyed on the pruned lesson's
normalized-text SHA-256, carrying its embedding but — by an explicit comment —
never its text, and distillation refuses a candidate that matches one, by exact
hash and by semantic similarity to those embeddings, terminating with
`result: rejected_value`. So a pruned duplicate cannot be re-distilled, and
`tombstone` is earned. Quarantine is the path that still does *not* tombstone: it
keeps the row and suppresses it, so a lesson quarantined for being harmful, then
re-distilled from a fresh interaction, can return. The machinery to close that is
now one call away — the same tombstone check the pruner triggers, extended from
pruning to quarantine.

```mermaid
%% caption: outcomes credited back to retrieved lessons drive a quarantine that checks blame attribution and base rate before it suppresses
flowchart TB
    Task["interaction"] --> Ret["retrieve: embedding≥0.62 ∪ FTS5, MMR rerank<br/>quarantined lessons excluded first"]
    Ret --> Use[("lesson_usage: (lesson, interaction)")]
    Task --> Out[("outcomes: signal, reward, source<br/>caller | machine | self_curriculum | unknown")]
    Out -->|"credited back"| Use
    Use --> Q{"quarantine check"}
    Q -->|"losses ≥ 5, ≥ 2 distinct tasks,<br/>improbable for the band's base rate,<br/>blame not shared across a cohort"| Quar["quarantined:<br/>excluded from retrieval and prompt"]
    Q -->|"otherwise"| Active["active"]
    Quar -->|"after cooldown"| Prob["sampled probation retrieval"]
    Prob -->|"a win"| Active
    Task -->|"went well"| Dist["distill: refuse not_concrete,<br/>exact_duplicate, semantic_duplicate,<br/>rejected_value (tombstone hit)"]
    Dist --> Lesson[("lessons + embedding + FTS")]
    Lesson -.->|"cosine ≥ 0.93"| Prune["near-duplicate pruned, keep one +<br/>content-hashed tombstone"]
    Prune -.->|"distillation refuses by hash or embedding"| Blocked["a pruned duplicate cannot return"]
    Quar -.->|"row kept, no rejected-value record"| Regrow["a re-distilled quarantined lesson can return"]
```

## 3. Architecture

One local SQLite database is the spine. `sonder_runtime/adapters/memory_store.py`
defines the schema — `interactions`, `outcomes`, `lessons` + `lessons_fts`,
`lesson_usage`, `lesson_distillations`, `preferences`, `refinement_history`,
`facts`, `sessions`, `session_project_summaries`, `tasks`/`task_events`/`task_deps`,
plus migration and claim tables — and it is **stdlib-only**: `sqlite3`, `array`,
`hashlib`, `math`. No ORM, no vector service, no server. Embeddings are stored as
BLOBs stamped with `embedding_model`, `embedding_revision` and `embedding_dim`, so
a vector always carries the space that produced it.

The memory logic is spread across small, mostly pure modules that wire into the
adapter:

- **`retriever.py`** (654 lines) — hybrid retrieval, MMR, and the quarantine
  decision (`lesson_quarantine`, `band_loss_rate`, `_attribution`).
- **`lesson_decay.py`** (253) — pure age-decay + usage-evidence ranking math, and
  a contradiction detector for semantically-similar lessons carrying opposite
  outcomes. No I/O, no clock, similarity injected — built for deterministic tests.
- **`lesson_pruner.py`** (256) — embedding-cluster near-duplicate removal that
  writes a content-hashed rejected-value tombstone as it deletes, dry-run by
  default, embedding-space-isolated.
- **`memory_quality.py`** (358) — a read-only auditor that flags vague lessons
  (*"use appropriate", "be careful", "best practices"*) against concrete anchors
  (backticks, dotted names, Big-O).
- **`grounded_extraction.py`**, **`reflection.py`**, **`preference_learning.py`**,
  **`mmr_rerank.py`**, **`store_integrity.py`**, **`refinement_transactions.py`**.

The root `memory_store.py` and `recall.py` are compatibility shims that alias the
migrated adapters under `sonder_runtime/adapters/` — a strangler-fig migration in
progress, with the true modules under the package and the root names preserved for
legacy callers.

### Deployment and ergonomics

- **One SQLite file, no services.** The memory adapter needs nothing beyond the
  standard library; embeddings are computed by `embeddings.py`/`embed_cache.py`
  and stored locally.
- **The store is inspectable and repairable** with any SQLite client, and
  `store_integrity.py`, `sonder_doctor.py` and `memory_quality.py` are shipped
  audit tools.
- **Concurrency is taken seriously** for a local store: claim tokens with owner
  pid/identity on session turns and distillation, and abandoned-claim recovery
  guarded by process-liveness checks.
- The wider runtime (self-modification, training, NPU) is heavy, but the memory
  layer is a clean, importable, dependency-light module inside it.

The screen found no auto-run surfaces, no dependency surfaces inside the cooldown,
two build-time execution points (`conftest.py` on pytest collection) and two
unpinned dev/train requirement ranges. Nothing was installed or run; the code was
read and cross-checked against its committed tests.

## 4. Essential Implementation Paths

- **Write / distill** — the `lesson_distillations` state machine in
  `memory_store.py`: `claim` an interaction, extract a lesson, transition to
  `stored` / `no_lesson` / `cancelled`, with `result_reason` recording
  `not_concrete`, `exact_duplicate`, `semantic_duplicate`, or `rejected_value`
  (a hit against the tombstone registry, by exact hash in `reflection.py:465` or
  by embedding in `is_tombstoned_duplicate`).
- **Credit** — `lesson_usage` rows link a retrieved lesson to its interaction;
  outcome signal, reward and `outcome_source` are filled in when the outcome
  lands (`record_outcome`, the `_checked_source` guard).
- **Retrieve** — `retriever.retrieve` / `retrieve_with_ids`: embedding cosine at
  `DEFAULT_MIN_SIM = 0.62` unioned with `memory_store.fts_search`, then
  `mmr_rerank.mmr_rerank` at `lambda 0.5`, with `exclude_ids=quarantined` applied
  before ranking.
- **Quarantine** — `retriever.lesson_quarantine` at `:392`, with constants
  `QUARANTINE_MIN_LOSSES = 5`, `QUARANTINE_MIN_DISTINCT_TASKS = 2`,
  `QUARANTINE_PROBATION_AFTER_HOURS = 24`, `band_loss_rate` for the base-rate
  test, and `_attribution` for shared-blame deduplication.
- **Correct preferences** — `refinement_transactions.apply_preference_refinement`
  writes a `refinement_history` row per `apply`/`rollback` with `expected_version`
  optimistic concurrency and before/after versions.
- **Prune** — `lesson_pruner.prune` clusters by cosine ≥ `0.93` and deletes all
  but one representative per cluster, dry-run unless `--apply`; each deletion goes
  through `memory_store.tombstone_lesson` (`lesson_pruner.py:209`), writing a
  `lesson_tombstones` row (content SHA-256 + embedding) so the value cannot be
  re-distilled.
- **Tombstone / re-derivation guard** — `memory_store.tombstone_lesson`
  (`:2225`) records the digest and embedding then deletes the lesson rows;
  `lesson_text_tombstoned` and `all_lesson_tombstones` back the distillation
  refusal. `delete_interaction` purges the tombstones derived from it.
- **Decay / contradiction** — `lesson_decay` blends a 30-day half-life with a
  small usage weight and flags contradicting lesson pairs.
- **Quality audit** — `memory_quality` classifies stored lessons as vague or
  concrete and reports duplicates.

## 5. Memory Data Model

The schema is where the epistemic care shows, and several columns carry a comment
explaining the failure they prevent — a habit worth reading the source for.

`outcomes.source` is the sharpest: `NOT NULL` with **no default**, a closed
`CHECK` vocabulary, and a comment stating why —

> a default is how the original defect would come back, because a writer that
> forgot would keep filing rows under a meaning it never chose. Omitting the
> column is a constraint failure, not a silent relabelling.

That is provenance enforced at the schema level: the system cannot record an
outcome without saying who judged it, and it cannot invent a category. The
`lesson_usage.outcome_source` mirror is nullable because a usage row exists before
any outcome credits it, and the eviction math reads `NULL` as unknown provenance.

`preferences` carries `confidence REAL`, `evidence_count`, `enabled`, and
`revision >= 1` with a `UNIQUE(scope, key)` — a corrected belief with a version
and an on/off switch. `refinement_history` records `operation IN ('apply',
'rollback')` with `expected_version`, `before_version`, `after_version` and a
`parent_refinement_id`, which is an **append-only audit of every correction, with
rollback** — the mechanism the [append-only memory audit](../../patterns/append-only-memory-audit/)
pattern describes, applied to preferences.

`lesson_tombstones` is the model's rejected-value record. Its primary key is the
normalized-text SHA-256 of a pruned lesson, and it carries the lesson's embedding
and vector provenance but — by an explicit comment — never the lesson text:
*"its content identity must not disappear with it… never retain the lesson text in
this denial record."* A `reason CHECK` admits only `near_duplicate_pruned` today,
so the table is scoped to the pruning path, and deleting a source interaction
purges the tombstones derived from it. This is the value-keyed
[rejected-value tombstone](../../patterns/rejected-value-tombstone/), and it is
kept distinct from privacy deletion on purpose: `delete_lesson` and the new
project-scoped `delete_fact` erase completely, while `tombstone_lesson` rejects a
value and remembers, content-free, that it did.

**Scoping** is real on the scoped stores and absent on the lesson store, by
design. Interactions carry `project` and a `project_explicit` flag; tasks and
preferences carry `account_scope`, described as "an account boundary supplied by
the authenticated serving layer," applied as `WHERE project=?` /
`account_scope=?` on the read builders. Lessons, by contrast, are **global** —
procedural knowledge is meant to cross projects, and retrieval fetches them by id
without a project filter. So `scope_enforced` is earned by the interaction,
task and preference reads, and the report states plainly that the lesson layer is
deliberately unscoped.

Temporal fields are record time throughout; preference `revision` is versioning,
not validity time, so `bitemporal` does not apply.

## 6. Retrieval Mechanics

Hybrid and outcome-filtered. A query is embedded and matched by cosine at a 0.62
relevance floor, unioned with an FTS5 lexical search over `lessons_fts`, and the
combined candidates are MMR-reranked at `lambda 0.5` to trade relevance against
redundancy. **Quarantined lessons are removed before ranking** — `exclude_ids`
is computed from the quarantine decision and passed into the candidate query, so
a lesson that has been leading to losses never reaches the prompt.

The quarantine decision is the retrieval mechanic worth studying, and section 1
gives its three guards. Two consequences for retrieval follow. First, the
exclusion is **evidence-gated, not score-gated**: a lesson is not dropped for a
low similarity but for a documented run of bad outcomes it is answerable for, so
retrieval quality and lesson trust are separated. Second, the probation path
means the exclusion is **not permanent** — a quarantined lesson is sampled back
into a fraction of traffic so it can earn its way out, which is the difference
between suppression and deletion.

The failure mode the design carries is the base-rate test's dependence on having
enough outcomes: a new lesson has no band statistics, so quarantine cannot fire
on it, and a lesson retrieved rarely accumulates evidence slowly. That is the
correct direction to fail — a lesson is trusted until it has demonstrably earned
suspicion — but it means a harmful new lesson gets a grace period proportional to
how often it is used.

The contradiction detector in `lesson_decay` is a second, quieter retrieval-time
signal: it flags pairs of lessons that are semantically similar (≥ 0.8) but carry
opposite outcome signals — the situation where the store holds "do X" and "never
do X" and needs a human or a further outcome to break the tie. It flags rather
than resolves, which is the honest posture for a store that cannot know which
directive is right.

## 7. Write Mechanics

Writes are two-phase and idempotent. An interaction is recorded synchronously;
the lesson is distilled asynchronously through the `lesson_distillations` state
machine, which **claims** the interaction with a token and owner identity,
extracts a candidate lesson, and lands in a terminal state with a `result_reason`.
The refusal reasons are the interesting part: `not_concrete` rejects a vague
lesson before it is stored (backed by the `memory_quality` vocabulary),
`exact_duplicate` and `semantic_duplicate` reject one that restates an existing
lesson. So the distiller is a quality-and-dedup gate, and the fact that a lesson
was refused is itself recorded against the interaction.

Outcome crediting is the write that powers everything downstream. When an outcome
lands it is attached to the interaction and propagated to the `lesson_usage` rows
for every lesson that was retrieved — with its `outcome_source`. This is the
credit-assignment step the atlas keeps asking for and rarely finds: the store
knows not just that a lesson exists but which interactions used it and how those
turned out, and by whom that judgement was made.

Background work is substantial and all outcome-driven: near-duplicate pruning,
age-decay ranking, contradiction detection, and quarantine. None of it blocks a
turn — the retrieval path reads the current quarantine state, and the heavier
passes run as maintenance. The token cost of distillation is one extraction per
interaction that produced a storable lesson, gated by the concreteness and dedup
checks, so noise does not accumulate.

Deletion has the two shapes above — reversible quarantine and irreversible
near-duplicate pruning — and they now differ in exactly the way that matters.
Pruning writes a `lesson_tombstones` row keyed on the rejected lesson's content
hash and embedding, and distillation checks a candidate against it by both exact
hash and semantic match, returning `rejected_value`; a pruned duplicate cannot be
re-distilled. Quarantine still leaves no rejected-value record — it keeps the row
and suppresses it — so a lesson quarantined as harmful can be re-distilled from a
fresh interaction and return. Closing that is now a one-line extension: the
tombstone check the pruner already triggers, applied when a lesson is quarantined
rather than only when it is pruned.

### An outbox in the memory schema, one layer from the live path

Migration revision 5 concatenates `OUTBOX_DDL` into the memory schema, so every
database now carries an `outbox_events` table — id, event type, aggregate type
and id, a `sequence`, a payload, a correlation id, `created_at` and a nullable
`published_at`, under `UNIQUE(aggregate_type, aggregate_id, sequence)`. The
module states the contract: *"State mutations and their events are committed
atomically. The dispatcher polls unpublished events and projects them into
`operations.db`."*

**The producer exists and the live path does not use it.**
`OutcomeService.record_outcome` calls `self._store.record_outcome(...)` and then
`self._store.append_outbox_event(event)` with an `outcome.recorded` event — the
atomic pairing the docstring describes. But nothing outside `tests/` constructs
an `OutcomeService`: the running system records outcomes from `server.py`,
directly against the store, at eight call sites. So the table is created on every
install, the writer and the dispatcher are complete and covered by
`tests/test_spec5_outbox.py`, and a reader who queries `outbox_events` on a
working deployment finds it empty. This is a layered architecture being built
beside the working one rather than a mechanism that was abandoned, and the
distinction matters for what the table means today: nothing.

**There is a latent collision in the wiring that would activate it.** The event
is constructed with `sequence=0` hardcoded, and `OutboxWriter.append` issues a
plain `INSERT INTO outbox_events` with no conflict clause against a UNIQUE over
`(aggregate_type, aggregate_id, sequence)`. The aggregate is the interaction, and
an interaction can receive more than one outcome — `outcomes` has no unique
constraint on `interaction_id`, and `server.py` records `tests_passed` and
`failed` from different branches of the same flows. So the second outcome for an
interaction would raise, and because the append happens inside the transaction
that recorded the outcome, the outcome write would roll back with it. Whichever
caller migrates to the service first is the one that finds this.

## 8. Agent Integration

The memory adapter is a stdlib-only importable module, and the runtime drives it
from a terminal REPL, a headless service, and an MCP surface. The agent's leverage
over memory is indirect and outcome-mediated rather than tool-driven: it does not
call `save_lesson` or `forget`; it acts, an outcome is recorded, and the
distillation and quarantine machinery decide what becomes and stays a lesson. That
is a deliberate design — the model does not curate its own procedural memory, the
outcome loop does — and it is the right shape for a self-improving loop where the
model's own judgement is exactly what should not be trusted to grade itself.

Preferences are the one memory a person or the serving layer edits directly, and
they carry the `account_scope` boundary and the refinement audit. The `contribute.py`
/ `pull_community.py` / `proposals/` machinery is a community-contribution flow
for *code modules* (a lesson tagger, a C++ repair flow), not a per-memory review
surface — so `human_review` is withheld: the quarantine that governs lesson trust
is statistical and automatic, and there is no surface where a person adjudicates a
lesson's content.

Adopting the mechanism means taking the outcome→credit→quarantine loop, which is
portable in principle: it needs an interaction log, an outcome with a provenance
field, a usage join, and the base-rate math in `retriever.py` and `lesson_decay.py`.
Those modules are pure and test-friendly by construction.

## 9. Reliability, Safety, and Trust

**Provenance is the strongest work here.** Every outcome records who judged it,
enforced at the schema level, and the success-rate and quarantine math weight
caller-sourced outcomes over machine ones and treat unknown provenance as its own
category. This is the concrete answer to self-grading: a lesson credited only by
the machine's assessment of its own output is not trusted the way one credited by
a caller is. Read against [the reward-inflation
result](../../compare/#known-limitations) the atlas records, Sonder is one of
the few systems that has built the distinction the theory says is necessary — a
de-inflation signal that tracks who is doing the grading.

**The quarantine's two statistical guards are what separate it from the naive
version.** The naive outcome-gated memory punishes a lesson for a run of losses;
this one asks whether the run is improbable for the lesson's own retrieval band
(so a rarely-used lesson on hard tasks is not punished for the difficulty of the
tasks retrieval sent it) and whether the lesson is individually answerable for the
losses (so a cohort that always fails together does not let each member count the
shared failure). Both are tested with worked probabilities. This is the
credit-assignment discipline the atlas argues for and finds almost nowhere.

**The residual risks are real and mostly acknowledged in the code.** The loop
trusts an outcome signal that is frequently `machine` or `unknown`; the code's
suspicion of those categories is correct but does not manufacture ground truth
where there is none, so a store fed only machine-graded outcomes is a store
grading itself, however carefully the weights are set. Near-duplicate pruning now
writes a content-hashed rejected-value tombstone that distillation honours, so a
pruned duplicate cannot come back; quarantine still suppresses without one, so a
quarantined lesson can be re-distilled from a fresh interaction and resurrect.
And the base-rate test's need for evidence gives a new harmful lesson a grace
period.

**Correction of preferences is auditable and reversible** — `refinement_history`
with apply/rollback and version checks — which earns `audit_log`. Concurrency is
handled with claim tokens and liveness-guarded abandoned-claim recovery. There is
no encryption of the local database mentioned; the store is as private as the
disk.

## 10. Tests, Evals, and Benchmarks

The test suite is large and unusually well-aimed at the mechanisms this report
cares about: 362 test files, and the memory-relevant ones assert behaviour rather
than coverage. `tests/test_retriever.py` alone pins the quarantine's design:
`test_quarantine_judges_a_lesson_against_its_own_frequency_band` (with an explicit
`p=0.006`), `test_positive_outcome_rehabilitates_quarantined_lesson`,
`test_quarantine_reaches_probation_and_a_win_is_the_exit`, and
`test_quarantine_still_fires_on_an_unambiguously_harmful_lesson`.
`tests/test_learning_health.py` adds the shared-blame cases —
`test_one_failure_cluster_no_longer_quarantines_its_whole_cohort` and
`test_a_lesson_failing_alone_is_still_quarantined`.

Two tests earn `negative_eval` directly, and they are the strong kind — material
that exists must not be *retrieved or injected*, not merely kept out of a write:
`test_orchestrator_memory.py::test_prompt_and_trace_omit_quarantined_lesson`
asserts a quarantined lesson reaches neither the prompt nor the trace, and the
retriever tests assert quarantined lessons are excluded from the candidate set.
`tests/test_outcome_source.py` ties the eligibility decision to provenance,
asserting a lesson driven by non-caller outcomes is not treated as active.

The rejected-value tombstone is pinned by tests of its own.
`tests/test_reflection.py::test_store_prepared_lesson_refuses_pruned_value_tombstone`
refuses a re-distillation of a pruned lesson by exact text, and
`…refuses_semantic_pruned_tombstone` refuses a *reworded* one whose embedding
still matches — the semantic half being what makes the tombstone more than a hash
set. `tests/test_lesson_pruner.py` asserts the tombstones are written with no
lesson text retained, and `tests/test_memory_store.py` asserts deleting a source
interaction purges the tombstones derived from it. These are write-refusal
assertions rather than retrieval-omission ones, so they strengthen the
rejected-value story without adding to `negative_eval`.

What is missing is an end-to-end retrieval-quality benchmark: the constants — the
0.62 relevance floor, the 0.93 dedup threshold, the 30-day half-life, the
five-loss quarantine trigger — are each defended in a comment and tested for
behaviour, but nothing measures whether the tuned values maximise recall or task
success. `eval_retrieval.py` and `eval_history.py` exist as harnesses; no
committed run characterises the loop's effect on outcomes over time, which is the
measurement the whole design invites.

## 11. For Your Own Build

### Steal

**Credit outcomes back to the memories that were retrieved, and record who
judged the outcome.** The `interaction → outcome(source) → lesson_usage` chain is
the loop most lesson stores omit, and the `source` column enforced `NOT NULL` with
a closed vocabulary is what lets the trust math distinguish a caller's judgement
from the machine grading itself. Without provenance on the outcome, outcome-gated
memory is self-grading with extra steps.

**Before suppressing a memory for bad outcomes, check the base rate and the
attribution.** A run of losses is only evidence if it is improbable for how often
the memory is used, and only the memory's *own* losses count, not the shared
losses of a cohort it is always retrieved with. These two guards are the
difference between a quarantine that removes genuinely harmful lessons and one
that removes whatever is used on hard tasks.

**Make suppression reversible with a sampled probation.** A quarantined memory
that gets a fraction of traffic can earn its way back on evidence; a permanently
excluded one can only be wrong forever. Probation is the difference between
forgetting and demotion.

**Distill with a concreteness gate and a semantic-duplicate gate.** Rejecting
*"be careful with errors"* before it is stored, and rejecting a restatement of an
existing lesson, keeps the procedural store from filling with vagueness and
redundancy — and recording *why* a distillation was refused makes the gate
auditable.

**Journal every correction with a version check.** `refinement_history` with
apply/rollback and `expected_version` is optimistic concurrency plus an audit
trail in one table; a preference can be corrected, the correction can be rolled
back, and both are on the record.

**Tombstone a rejected value without keeping the value.** Sonder's pruner records
the normalized-text hash and the embedding of the lesson it removes — never the
text — and distillation refuses a re-derivation by both exact hash and semantic
match. It is a rejected-value tombstone that is also privacy-safe, and it stays
distinct from a full privacy delete that erases everything, so "reject a value"
and "erase a record" are two verbs rather than one.

### Avoid

**Do not let outcome provenance be optional.** A nullable-with-default `source`
is how a machine-graded outcome silently becomes indistinguishable from a
caller-graded one, and the whole trust argument collapses. Enforce it at the
schema.

**Do not quarantine on a raw loss count.** Without the base-rate and attribution
guards, an outcome-gated memory punishes the memories that get the hard tasks and
lets a co-failing cohort escape, which is backwards.

**Do not suppress without a rejected-value record if re-derivation is likely.**
Sonder shows both halves: its pruner now writes a content-hashed tombstone that
distillation checks, so a pruned duplicate cannot come back — but quarantine still
keeps the row without a rejected-value record, so a quarantined lesson can be
re-distilled from a fresh interaction and return. If your extractor runs
continuously, a suppression that does not tombstone the value invites it back.

**Do not confuse a preference version history with bitemporality.** Revisions are
record-time; they tell you what the system believed and when it changed its mind,
not when the belief was true of the world.

### Fit

This suits a builder of a self-improving agent that accumulates procedural
lessons and can observe outcomes — the loop is the point, and the loop needs a
signal. It is the best-built outcome-gated lesson memory in the atlas, and the
quarantine's statistical guards are worth lifting whole even into a different
store. It fits a single machine and a local SQLite file naturally; the concurrency
and provenance work would extend to a served deployment, and the `account_scope`
column is already there for it.

Walk away if you cannot produce a trustworthy outcome signal — the whole design
degrades to self-grading if every outcome is `machine`, and no amount of
base-rate care fixes a signal that is the model assessing itself. Walk away if you
need contradiction *resolved* rather than flagged, or a rejected-value tombstone
that keeps a bad lesson gone. And treat the surrounding runtime as out of scope:
what is worth adopting is the memory adapter and the retriever, not the
self-modifying agent around them.

## 12. Open Questions

- What fraction of outcomes in practice carry `caller` provenance versus
  `machine`/`unknown`? The improvement report now surfaces the buckets
  (`legacy/unknown provenance: N` beside the caller-judged and autograded rates)
  rather than a blended number, but no committed run reports the ratio on real
  traffic — and the trust math is only as strong as it.
- Distillation now checks a candidate against *pruned* lessons via the tombstone
  registry, by exact hash and by embedding. Does the same check ever run against
  *quarantined* lessons, or is quarantine still the one suppression a
  re-derivation can undo? At this reading it is the latter.
- Are the quarantine constants (five losses, two distinct tasks, 24-hour
  probation) tuned against anything, or chosen? Each is defended in a comment,
  none is measured.
- How does the contradiction detector's output get consumed — flagged for a human,
  fed back into ranking, or logged? The detector is pure logic; its wiring is
  elsewhere.
- Does the served deployment apply `account_scope` to the lesson store, or do
  lessons remain global across accounts as they are locally? The comment implies a
  serving layer that the reviewed tree does not include.

## Appendix: File Index

**Store and schema**

- `sonder_runtime/adapters/memory_store.py` — the SQLite adapter, migration revision 5: schema, distillation state machine, outcome crediting, `outcomes.source` enforcement, the `lesson_tombstones` rejected-value registry (`tombstone_lesson`, `lesson_text_tombstoned`, `all_lesson_tombstones`), and the project-scoped `delete_fact`.
- `memory_store.py`, `recall.py` — root compatibility shims aliasing the adapters.

**Retrieval and trust**

- `retriever.py` — hybrid retrieval, MMR, `lesson_quarantine`, `band_loss_rate`, `_attribution`.
- `lesson_decay.py` — age-decay + usage ranking and the contradiction detector.
- `sonder_runtime/adapters/memory_rerank.py` — MMR diversity reranking.

**Curation**

- `lesson_pruner.py` — embedding-cluster near-duplicate deletion.
- `memory_quality.py` — vague-vs-concrete lesson auditing.
- `grounded_extraction.py`, `reflection.py` — lesson and outcome extraction, including the distillation tombstone check that returns `rejected_value` (`is_tombstoned_duplicate`).

**Correction**

- `refinement_transactions.py` — preference apply/rollback with version checks.
- `preference_learning.py` — preference formation.

**Integrity and ops**

- `store_integrity.py`, `sonder_doctor.py`, `learning_health.py`.

**Tests**

- `tests/test_retriever.py` — quarantine base-rate, probation, rehabilitation, harmful-fires.
- `tests/test_learning_health.py` — shared-blame cohort cases.
- `tests/test_outcome_source.py` — provenance-gated eligibility.
- `tests/test_orchestrator_memory.py` — quarantined lesson omitted from prompt and trace.
- `tests/test_reflection.py` — distillation refuses a pruned value by exact hash and by embedding (`rejected_value`).
- `tests/test_lesson_pruner.py`, `tests/test_memory_store.py` — tombstones written without lesson text; purged when their source interaction is deleted.

## History

**2026-08-22** — [`eb93f60d8380b096a6fefbf34c053fb20dccde4f`](https://github.com/Krilliac/Sonder-runtime/commit/eb93f60d8380b096a6fefbf34c053fb20dccde4f) — re-pinned 474 commits and +146,315 lines on. Screened again: no auto-run surface, two build-time execution points, two unpinned surfaces; nothing was installed and nothing was run. Marks unchanged at `trust_state`, `scope_enforced`, `audit_log`, `negative_eval` and `tombstone`.

**The memory layer is the part that did not move.** Across the files this report's appendix names, the diff is thirteen insertions and sixty-five deletions, and most of that is a package reorganisation — the root shims resolve into `sonder_runtime.adapters`, and `mmr_rerank.py` became `sonder_runtime/adapters/memory_rerank.py`, corrected in the appendix. Every quarantine, attribution, base-rate and tombstone mechanism this report describes is byte-identical, so the marks stand without re-derivation. The growth is in the runtime: HTTP fanout, A2A discovery, resumable streams, receipts on artifacts, and CI portability.

Two substantive changes. `RECALL_CANDIDATE_TIME_LIMIT_S` moves from 0.5 to 1.0 with the reasoning committed beside it and the honest note that the deadline is a backstop — *"the row and byte caps remain the primary work bound"*. And migration revision 5 adds a transactional outbox to the memory schema, described in section 8: the table ships on every install, the producer sits on a service the running system does not call, and the event it would write hardcodes a sequence number that a second outcome for the same interaction would collide with.

**2026-08-15** — [`53a6ac550488f9fd9d59dea61fb4bcea85a6dc03`](https://github.com/Krilliac/Sonder-runtime/commit/53a6ac550488f9fd9d59dea61fb4bcea85a6dc03) — re-pinned at HEAD, around fifty commits past the first reading. Screened again before reading: no auto-run surface, two build-time `conftest.py` points, two unpinned dev/train ranges, nothing inside the cooldown; nothing was installed or run. [`ec351a477e325b9c66eca17df8f3a5d612d063d7`](https://github.com/Krilliac/Sonder-runtime/commit/ec351a477e325b9c66eca17df8f3a5d612d063d7) added a `lesson_tombstones` table keyed on a pruned lesson's normalized-text SHA-256 plus its embedding — content-free by an explicit comment — and `reflection.py` now refuses a re-distillation matching one by exact hash or by embedding (`result: rejected_value`); the near-duplicate pruner writes a tombstone as it deletes. That earns `tombstone` and closes the re-derivation gap for the pruning path, leaving quarantine as the one suppression that still keeps a row without a rejected-value record. [`e33c604468d0da2561477b29c6f694c9cfd3c4ff`](https://github.com/Krilliac/Sonder-runtime/commit/e33c604468d0da2561477b29c6f694c9cfd3c4ff) added a project-scoped `delete_fact`, and [`03455668e4b4718a833cb78a138020d64b892970`](https://github.com/Krilliac/Sonder-runtime/commit/03455668e4b4718a833cb78a138020d64b892970) surfaces `legacy/unknown` outcome provenance as its own bucket in the improvement report rather than folding it into a blended rate. `memory_store.py` is 3,632 lines; the tree is ~259,800 lines of Python across 743 files, 362 test files.

**2026-08-14** — [`2a11324cbb131c76572724ac1fe47362a4aedf83`](https://github.com/Krilliac/Sonder-runtime/commit/2a11324cbb131c76572724ac1fe47362a4aedf83) — first reading. Screened before opening: no auto-run surfaces, no dependency surfaces inside the cooldown, two build-time execution points (`conftest.py`), two unpinned dev/train requirement ranges. Nothing was installed or run; the quarantine's base-rate and attribution guards, the outcome-provenance enforcement, and the retrieval exclusion were read from `retriever.py`, `memory_store.py` and `lesson_decay.py` and cross-checked against the committed tests named above.

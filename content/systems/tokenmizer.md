---
title: "TokenMizer"
eyebrow: "A status for not knowing"
description: "When two decisions share a topic but the evidence will not say which replaced which, both are marked CONTESTED and stay visible — and a ground-truth retention suite asserts what fraction of a session's decisions the extractor actually recovers."
root: ../..
page_kind: system
source_name: "Shweta-Mishra-ai/tokenmizer"
source_url: https://github.com/Shweta-Mishra-ai/tokenmizer
revision: ed7860e626ccc5c67fdf28c5cd12532ba337aeee
revision_url: https://github.com/Shweta-Mishra-ai/tokenmizer/commit/ed7860e626ccc5c67fdf28c5cd12532ba337aeee
analyzed_at: 2026-07-30
capabilities: "trust_state, audit_log"
stack_storage: "sqlite"
stack_retrieval: "graph"
stack_source: "seeded"
matrix:
  memory_unit: "A graph node — one of fourteen types (task, decision, file, error, endpoint, schema, goal, test…) carrying a label, a summary and one of eight statuses"
  storage: "SQLite: nodes and edges plus a separate `decision_transitions` table that survives graph pruning"
  retrieval: "`query()` over the graph, excluding superseded, archived and invalidated nodes; `to_context_block()` renders a resume block"
  write: "A hybrid extractor over session messages, with an ontology and a validator, then a contradiction check on every decision node"
  update_delete: "Supersession when the evidence is clear, `CONTESTED` on both sides when it is not, `INVALIDATED` for explicitly wrong, plus pruning"
  scoping: "Per-project graph caches; no scope predicate inside a graph"
  integration: "A CLI and server for coding sessions — checkpointing, compression, a dashboard and a visualiser"
  background: "Decay, pruning and compression passes, with idempotence and correctness suites of their own"
  trust: "Eight statuses — pending, in_progress, completed, failed, superseded, invalidated, archived, contested — with three excluded from retrieval and one deliberately not"
  strengths: "A status for unresolved ambiguity that keeps both sides visible instead of guessing, and a committed ground-truth measurement of extraction recall"
  risks: "The redaction functions are unit-tested in isolation and nothing asserts a secret fails to reach the rendered context block"
---

## 1. Executive Summary

TokenMizer is an MIT-licensed session-memory tool for coding agents — *"keep
your AI context alive across sessions"* — with a graph memory of 4,766 lines
across thirteen modules and 440 test cases in 38 files.

**Its best mechanism is a status for not knowing.** Most systems in this atlas
resolve a contradiction by picking: a newer decision supersedes an older one, the
old row is filtered out of retrieval, and the model never learns there was a
disagreement. TokenMizer's contradiction check asks whether the evidence supports
that call, and when it does not, marks **both** sides `CONTESTED`. The comment
explaining it is the clearest statement of the problem in the corpus:

> Two decisions share a topic bucket (e.g. both "database") but don't share
> enough descriptive context to confidently call one a genuine replacement of the
> other (e.g. "Use PostgreSQL for primary user data" vs "Use SQLite for the local
> offline cache" — plausibly two independent, complementary choices, not a
> reversal). Rather than silently guessing and marking one SUPERSEDED —
> destroying it from resume context on possibly-wrong evidence — both sides are
> flagged CONTESTED and surfaced together so a human or the LLM can resolve the
> ambiguity explicitly.

And the crucial half: `CONTESTED` *"remains visible in query() and
to_context_block(), unlike SUPERSEDED/ARCHIVED/INVALIDATED"*. Three statuses hide
a node; this one deliberately does not, because the point is to put the
unresolved pair in front of whoever can settle it. The pair is joined by a
symmetric `CONFLICTS_WITH` edge, and a dedicated eight-case suite drives the
distinction from both directions — a same-purpose swap still supersedes, a bare
technology swap with no descriptive context still supersedes, and two decisions
about different purposes in one topic bucket do not.

**The second thing worth the visit is that it measures its own extraction.**
`tests/memory_accuracy/test_retention.py` runs a synthetic thirty-turn coding
session past the extractor with a hand-written ground truth — the tasks that were
completed, the decisions that were made, the files that were touched — and
asserts recall against it: `recall >= 0.4` for tasks, `>= 0.33` for decisions,
`>= 0.33` for files. This atlas records again and again that extraction quality
is the load-bearing property nobody measures. Here it is measured, in the test
suite, against a ground truth someone wrote by hand, with the thresholds set at
the honest floor rather than at an aspiration.

## 2. Mental Model

A memory is a typed node in a session graph with a lifecycle status, and the
status is genuinely epistemic rather than merely administrative. `COMPLETED` is
active and shown in the resume. `SUPERSEDED` is *"replaced by newer decision —
kept in history"*. `INVALIDATED` is *"explicitly wrong/cancelled — kept as
warning"*. `ARCHIVED` is *"old but valid, not relevant now"*. Each of the three
is a different reason for the same outcome, and keeping them distinct is what
lets `INVALIDATED` mean something a single `active` boolean cannot: this was
wrong, we know it was wrong, and we are keeping it so nobody re-derives it.

Supersession, when it happens, is not just an edge. A `DecisionTransition`
records *"the full story of why one decision replaced another… what triggered
the change, why the old decision was wrong, what evidence caused the switch, and
how confident we are now"*, and its docstring notes that it lives in a separate
SQLite table *"so it survives graph pruning and is queryable independently"*.
Most correction records in this atlas store the fact of a replacement; this one
stores the argument for it, and puts it somewhere the garbage collector cannot
reach.

```mermaid
stateDiagram-v2
    [*] --> PENDING: extracted from the session
    PENDING --> IN_PROGRESS
    IN_PROGRESS --> COMPLETED: active — rendered in the resume block
    IN_PROGRESS --> FAILED

    COMPLETED --> SUPERSEDED: a newer decision, same purpose<br/>evidence is clear
    COMPLETED --> CONTESTED: same topic bucket, different purpose<br/>evidence will NOT say which replaced which
    COMPLETED --> INVALIDATED: explicitly wrong or cancelled
    COMPLETED --> ARCHIVED: old but still valid

    CONTESTED --> COMPLETED: a human or the LLM resolves it
    CONTESTED --> SUPERSEDED: resolved the other way

    SUPERSEDED --> [*]: hidden from query and context block
    INVALIDATED --> [*]: hidden, and kept as a warning
    ARCHIVED --> [*]: hidden
    CONTESTED --> [*]: BOTH sides stay visible<br/>joined by a CONFLICTS_WITH edge
```

## 3. Architecture

SQLite, with nodes and edges plus a separate `decision_transitions` table, and
a per-project graph cache in front. `safe_init_db` deletes a corrupt database
file and reinitialises rather than failing, and there is a `tests/chaos/`
directory holding `test_recovery.py` — a system that expects its own storage to
break and tests what happens next.

`_schema_version` sits on the graph with the comment *"increment when storage
format changes"*, and `_processed_hashes` deduplicates ingestion so replaying a
session does not double-extract it.

## 4. Essential Implementation Paths

- `tokenmizer/graph_memory/hybrid_extractor.py` (921) — extraction.
- `tokenmizer/graph_memory/graph.py` (879) — nodes, edges, `query`,
  `add_node`'s contradiction check, `get_transitions`.
- `tokenmizer/graph_memory/visualization.py` (553).
- `tokenmizer/graph_memory/decision_tracker.py` (514).
- `tokenmizer/graph_memory/validator.py` (380) and `ontology.py`.
- `tokenmizer/graph_memory/persistence.py` (362) — the schema,
  `persist_transition`, pruning survival.
- `tokenmizer/graph_memory/reasoning.py` (255), `context_block.py`,
  `pruning.py`, `types.py`.

## 5. Memory Data Model

Fourteen node types — `TASK`, `FILE`, `DECISION`, `ERROR`, `CONCEPT`,
`DEPENDENCY`, `API`, `PROJECT`, `AGENT`, plus a v4 group of `ENVIRONMENT`,
`GOAL`, `TEST`, `ENDPOINT`, `SCHEMA` — and eight edge types including
`SUPERSEDES`, `CONFLICTS_WITH`, `BLOCKS` and `FIXES`.

The v4 additions are the tell that this taxonomy grew from use: `ENDPOINT` and
`SCHEMA` are what a coding session actually accumulates, and a system that
started with `CONCEPT` and `DEPENDENCY` and later needed them was reading its own
graphs.

Every clock is a record clock; there is no validity time, so the mark is
withheld.

## 6. Retrieval Mechanics

`query()` walks the graph and excludes `SUPERSEDED`, `ARCHIVED` and
`INVALIDATED`; `to_context_block()` renders the resume. A comment at
`graph.py:744` records a fixed bug — *"was calling query() which excludes
SUPERSEDED nodes"* — from a path that needed the hidden ones, which is the
ordinary cost of expressing exclusion as a filter every reader has to remember.

**Scope is a per-project cache, not a predicate.** `test_cache_scoping.py`
covers keeping projects apart at the cache layer; inside a graph there is no
scope key, which is coherent for a per-project session tool and means the mark is
withheld.

## 7. Write Mechanics

The hybrid extractor runs over session messages with an ontology and a validator
in front of the graph, and every decision node goes through
`find_contradicting_decisions` before it lands. Non-fatal failures of that check
are *counted* on the graph rather than swallowed — a small honesty that most
best-effort paths in this atlas skip.

Background passes have their own correctness suites: `test_decay_idempotence.py`,
`test_compression_correctness.py`, `test_checkpoint_retention.py`. Testing that
a decay pass is *idempotent* is a specific and unusual thing to assert, and it is
the property that decides whether running consolidation twice is safe.

## 8. Agent Integration

A CLI, a server, a dashboard and a graph visualiser, aimed at coding sessions
rather than at being a library another agent embeds.

## 9. Reliability, Safety, and Trust

**`trust_state` is earned comfortably** — eight discrete statuses, three of which
withhold a node from retrieval, one of which (`INVALIDATED`) means "known wrong,
kept as a warning", and one of which (`CONTESTED`) exists specifically to avoid
asserting something the evidence does not support.

**`audit_log` is earned on `decision_transitions`** — a named, separately-stored
record of every supersession carrying its trigger, its reason, its evidence and a
confidence, written by `persist_transition`, deliberately outside the node and
edge JSON so that pruning cannot take it. It is the richest correction record in
the corpus: most systems store *that* a value was replaced, and this stores *the
argument*.

**No tombstone**, and the gap is narrower here than almost anywhere. `INVALIDATED`
is "explicitly wrong, kept as a warning" and the transition table holds the
reason — everything a rejection needs except a key on the *value*, so a
re-extraction of the same wrong decision produces a fresh node rather than
meeting the warning. The material is all present; nothing consults it on the
write path.

**`negative_eval` is withheld, and the near-miss is precise.** `test_security.py`
asserts that `redact_node` and `redact_messages` strip Anthropic keys, OpenAI
keys, AWS keys, Slack and Stripe tokens, emails and passwords — but they are unit
tests of the redaction functions in isolation. Nothing asserts a secret fails to
reach `to_context_block()`, and nothing asserts a `SUPERSEDED` or `INVALIDATED`
node is absent from a rendered resume, even though `query()` is documented as
excluding them and a comment records a bug caused by that exclusion. Two
one-line assertions would earn the column.

## 10. Tests, Evals, and Benchmarks

440 cases in 38 files, none run here, and the suite names are the most
informative in this batch: `memory_accuracy/test_retention`, `chaos/test_recovery`,
`test_contested_decisions`, `test_decay_idempotence`,
`test_compression_correctness`, `test_extractor_data_integrity`,
`test_checkpoint_retention`, `test_cache_scoping`, `test_concurrency`.

The retention suite is the one to copy, described in §1. Its thresholds — 0.4
task recall, 0.33 decision recall, 0.33 file recall — are worth reading as a
disclosure rather than a weakness: this is a system that knows roughly two-thirds
of the decisions in a session do not make it into the graph, has written that
down where CI enforces it, and has not dressed it up.

## 11. For Your Own Build

### Steal

- **Add a status for unresolved ambiguity, and keep it visible.** When your
  contradiction check cannot tell a replacement from a complementary choice,
  marking both `CONTESTED` and surfacing them together is strictly better than
  guessing — and inverting the visibility rule for that one status is what makes
  it useful rather than another way to hide something.
- **Store the argument for a correction, not just the fact of it.** Trigger,
  reason, evidence and confidence, in a table that survives pruning, turns "why
  does the system believe this now" into a query.
- **Measure extraction recall against a hand-written ground truth.** A synthetic
  session and a list of what should have been captured is an afternoon's work and
  it is the only way anyone learns what fraction of a conversation their memory
  actually keeps.
- **Set the threshold where your performance is.** 0.33 asserted honestly is
  worth more than 0.9 asserted nowhere.
- **Test that your decay pass is idempotent.** Running consolidation twice is a
  thing that happens, and nothing else in this atlas asserts it is safe.
- **Count your non-fatal failures instead of swallowing them.** A counter on the
  contradiction-check failure path is the difference between a degraded system
  and an invisible one.

### Avoid

- **Testing your redactor and not your output.** The functions are covered; the
  surface a model actually reads is not, and those are different claims.
- **Exclusion by filter with no accessor.** `query()` hiding three statuses means
  every caller that needs the hidden ones has to remember — and the comment at
  `graph.py:744` is the bug that produced.

### Fit

Take this if your memory is a coding session and your hardest problem is knowing
which of two plausible decisions is still in force. The status model and the
transition table are the parts to copy even if you never run the tool, and the
retention suite is the part to copy first.

Look elsewhere for multi-tenant or long-horizon personal memory: scope is a cache
key, every clock is a record clock, and the graph is built around one project's
session history.

## 12. Open Questions

- **How often does CONTESTED fire in real sessions?** The mechanism's value
  depends entirely on the contradiction check's precision, and the suite proves
  the rule works on constructed pairs rather than measuring the rate on real ones.
- **Who resolves a CONTESTED pair, in practice?** The comment says a human or the
  LLM; whether anything prompts either of them was not traced.
- **What is the recall on a real session rather than the synthetic one?** The
  ground truth is thirty hand-written turns; nothing measures a captured session.
- **Does anything read `decision_transitions` back into context?** It survives
  pruning and is queryable; whether the resume block ever shows the argument was
  not established.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `tokenmizer/graph_memory/hybrid_extractor.py` | 921 | Extraction from session messages |
| `tokenmizer/graph_memory/graph.py` | 879 | Nodes, edges, query, contradiction check |
| `tokenmizer/graph_memory/visualization.py` | 553 | Graph rendering |
| `tokenmizer/graph_memory/decision_tracker.py` | 514 | Decision lifecycle |
| `tokenmizer/graph_memory/validator.py` | 380 | Ontology validation |
| `tokenmizer/graph_memory/persistence.py` | 362 | Schema, `persist_transition`, prune survival |
| `tokenmizer/graph_memory/reasoning.py` | 255 | Graph reasoning |
| `tokenmizer/graph_memory/types.py` | — | Fourteen node types, eight statuses, eight edge types |
| `tests/memory_accuracy/test_retention.py` | — | Ground-truth recall thresholds |
| `tests/unit/test_contested_decisions.py` | — | Eight cases on the ambiguity rule |
| `tests/chaos/test_recovery.py` | — | Storage corruption |

## History

**2026-07-30** — [`ed7860e626ccc5c67fdf28c5cd12532ba337aeee`](https://github.com/Shweta-Mishra-ai/tokenmizer/commit/ed7860e626ccc5c67fdf28c5cd12532ba337aeee) — first reading.

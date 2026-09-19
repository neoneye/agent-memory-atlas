---
title: "Engram Cognitive"
eyebrow: "Two time columns, one clock: the bitemporal test builds rows no shipped writer can produce"
description: "A single-file Python memory for agents with episodes, superseded facts, an entity graph and agent partitioning, whose published numbers are recomputed by a CI gate and whose gates are themselves pinned to the release workflow."
root: ../..
page_kind: system
source_name: "TAIPANBOX/engram"
source_url: https://github.com/TAIPANBOX/engram
archive_name: "TAIPANBOX--engram"
revision: 240a4d9d433e2f4a366d8877279449381b59b6fa
revision_url: https://github.com/TAIPANBOX/engram/commit/240a4d9d433e2f4a366d8877279449381b59b6fa
analyzed_at: 2026-09-19
capabilities: "scope_enforced, audit_log, negative_eval"
capability_evidence:
  scope_enforced: "agent_id as a vec0 partition key that the instance carries into every episodic read | engram/core.py:336, engram/schema.py:44-58, engram/store.py:893-901 | `agent_id = None if cross_agent else self._agent_id` is the whole rule: the key is fixed on the Engram instance at construction and reaches the query on every episodic read. In the vector index it is a vec0 partition key rather than an outer join predicate, so a scoped `recall(k=5)` counts five rows that already belong to the agent instead of trimming a global top-k that may contain none of them. A caller widens with `cross_agent=True` and cannot omit the key on a call. The boundary is drawn in the code rather than left to be discovered: facts and entities carry no agent_id and are shared across the agents in one file by decision, and `fact_count` declines to hide them because a scoped count would disagree with what `timeline()` and `contradictions()` return on the same instance | tests/test_multiagent.py:517 asserts a scoped recall over a 60-against-5 store returns none of the other agent's episodes, with tests/test_multiagent.py:524 as the cross-agent control"
  audit_log: "an NDJSON event file with a per-file append-only hash chain, off unless configured | engram/events.py:101-107, :396-412, engram/core.py:227, :272, :394, :495, :545, :605 | every event carries the previous event's hash over its own canonicalised body, the chain advances only after a successful write, and reopening a file resumes its chain rather than starting a new one, so one file stays one chain across process restarts. Coverage is the mutation set: `memory_written` from `observe`, `observe_many` and `assert_fact`, `memory_forgotten` from `forget`, `forget_fact` and `forget_entity` (one event per erased memory, deliberately, because a count cannot be reconciled against the `memory_written` events that created those memories), plus `reflection_run` and `contradiction_found`. Three limits belong with the mark. The log is off unless `events_path` or `ENGRAM_EVENTS_PATH` is set; it stays off on an instance with no agent_id even when a path is given, though the skip is counted rather than silent; and `emit` never raises, so a write failure is logged and swallowed | tests/test_events.py:89, :100, :128, :154-299 cover off-by-default, the agent_id rule, fail-open, and one test per event type"
  negative_eval: "must-not-retrieve on a deliberately lopsided store, with its positive control beside it | tests/test_multiagent.py:474-529 | the fixture is the point: one agent writes 60 near-identical episodes and the other writes 5, so a global top-k contains none of the quiet agent's rows and the assertion cannot pass by accident. `test_scoped_recall_never_leaks_the_other_agent` then asserts both directions — no episode containing \"step\" reaches the quiet agent at k=20, and no episode containing \"rollback\" reaches the noisy one. `test_cross_agent_recall_still_sees_both` is the control that keeps the first test from passing vacuously on an empty result, and `test_scoped_hybrid_recall_returns_k_despite_a_dominant_agent` repeats the shape for hybrid mode on a fixture that denies BM25 any shared query term | the two run together in the committed suite, and the surrounding comment records the pre-v2.3 bug they regress: agent_id filtered in the outer join could only cut into a top-k vec0 had already chosen"
stack_storage: "sqlite"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "An episode with a caller-settable timestamp, actors, tags, salience and a decaying importance score; a fact as a subject-predicate-object triple with validity and supersession columns; entities and weighted graph edges beside them"
  storage: "One SQLite file with the `.engram` extension — sqlite-vec for vectors, FTS5 for keywords, optional SQLCipher with a `rekey()` method; no server and no API key to write"
  retrieval: "Hybrid BM25 and cosine at a 0.5/0.5 default blend, pure cosine, or spreading activation over Hebbian edges; `as_of` restricts episodes to a point in time and `timeline()` reads facts valid at one"
  write: "Writes land locally and immediately; extraction is a separate `reflect()` pass the caller schedules, and a CI gate holds the promise that no provider SDK is imported at module level"
  update_delete: "A newer extraction closes the older same-subject-predicate fact's validity and links the successor; `forget`, `forget_fact` and `forget_entity` are permanent deletes, the last of them crossing every agent in the file"
  scoping: "agent_id is a vec0 partition key filtering every episodic read, widened only by `cross_agent=True`; facts and entities are shared across agents by an explicit decision"
  integration: "A Python library, an `engram` CLI, an async wrapper, and an MCP server exposing remember, recall, why, forget and stats with `reflect()` deliberately withheld"
  background: "A reflection pass that extracts facts and resolves contradictions, an Ebbinghaus decay with Hebbian reinforcement, and a compression pass that summarises low-importance episodes and hard-deletes the originals"
  trust: "Provenance through `why()`, a hash-chained event file when configured, a socket-blocking CI check that a full observe-and-recall cycle opens zero sockets, and a gate that recomputes every published number from committed records"
  strengths: "The gates are the thing to take. Three scripts under `scripts/` hold three invariants, each written as an argument rather than a rule: `no-network-at-write.sh` parses the package with Python's AST — \"because indentation is the entire distinction and a regexp would be fooled by an import inside a try block at module scope\" — to prove no provider SDK is imported at module level; `local-first.sh` holds the install side, an allow-list of exactly three permitted default dependencies (\"a new dependency should have to be argued for, not merely fail to match a list of things somebody thought of in 2026\") and a full observe-and-recall cycle run with socket creation made to raise, \"so a call that would have connected fails loudly instead of passing quietly on a machine that happens to have no route\"; and `readme-numbers.sh` recomputes the recall table and corpus size from `benchmarks/results/*.jsonl` rather than quoting them, because \"[a] number in a README is a claim with no owner\". Each says it is \"the ONE copy of this check\". Then comes the layer almost nobody builds: `tests/test_gates_are_wired.py` asserts the gates run in `release.yml`, because a tag push does not trigger `ci.yml` at all, so until August 2026 the workflow that shipped the wheel to PyPI ran none of them. That test refuses to parse the YAML, on the ground that PyYAML is not a declared dependency and \"a test that quietly depends on somebody else's transitive install is the same class of defect as a gate that runs in one job\""
  risks: "The bitemporal columns are the gap to read first: `facts` carries `valid_from`/`valid_to` beside `recorded_at`/`superseded_at`, and both shipped writers set `valid_from` and `recorded_at` to the same `now`, while `close_fact` writes one `now` into both `valid_to` and `superseded_at`. Two axes, one clock, and no public API accepts a valid time, so `get_facts_as_of` reads a version chain rather than a belief history — the store cannot answer what it held as of last Tuesday. The bitemporal test suite passes because its helper constructs rows directly, setting `recorded_at=valid_from`, which no shipped path produces. Erasure is the other one: `forget_entity` deletes episodes where the entity is named in the caller-supplied `actors` list, so an episode whose text names the person while its actors list omits them survives, and the next `reflect()` reads the whole episode window and can re-extract the deleted fact. Nothing is keyed on a value and no tombstone concept appears anywhere in the tree, so a re-derived belief returns silently. Smaller: `import_json` writes episodes, facts and entities with no event at all, so an auditor reconciling against `memory_written` finds memories nobody recorded creating; and confidence is a continuous score with no discrete status beside it, so an extraction the model was unsure of is indistinguishable at read time from one it was certain of"
---

## 1. Executive Summary

Engram is "[t]he SQLite of agent memory: embeddable, local-first, cognitively
grounded" — Apache-2.0, version 2.4.1, 15,574 lines of Python across 59 files,
one `.engram` file on disk holding episodes, facts, entities and a graph, with
"no server, no Docker, and no API key required to write a memory."

The shape is three planes over one SQLite file. Episodes are raw observations
with a caller-settable timestamp, actors, tags and a decaying importance score.
Facts are subject-predicate-object triples with validity columns, extracted by a
`reflect()` pass the caller schedules rather than by the write. Entities and
Hebbian-weighted edges sit beside both, so recall can walk to what a match is
connected to and not only to what it resembles. `agent_id` partitions the
episodic plane; the semantic plane is shared.

**What is worth carrying away is how the project holds its own claims.** Three
scripts under `scripts/` enforce three invariants, and each is written as a
paragraph of reasoning before a line of bash. `no-network-at-write.sh` walks the
package's AST looking for a module-level import of any of nine network-capable
modules, and says why it is not a regexp:

> "Uses Python's AST, not a regexp, because indentation is the entire
> distinction and a regexp would be fooled by an import inside a try block at
> module scope."

`local-first.sh` holds the install side, which "can break without a single
import changing", by pinning the default dependency set to an allow-list of
three and by running a full observe-and-recall cycle with socket creation made
to raise — checked "by making socket creation raise rather than by watching
traffic, so a call that would have connected fails loudly instead of passing
quietly on a machine that happens to have no route." The same script records
that this check corrected the invariant it was written to hold: with a cold
cache, `observe()` does fetch a 64 MB ONNX model on first use, the README had
said 23 MB, and the invariant's absolute phrasing "read as an absolute and was
not one." It now promises "one fetch, then never again."

`readme-numbers.sh` recomputes the published recall table from the committed
per-question records rather than trusting it, and explains why the project
needed it: "engram's own release history is a sequence of fixes to published
numbers. 2.4.1 shipped for no other reason than that the headline table still
described the previous blend weights one release after they stopped being the
default." The atlas has seen a documentation gate before, in
[Cortex](../cortex-hypermnesia/). Engram adds the layer above it.
`tests/test_gates_are_wired.py` asserts each gate script appears in
`release.yml`, because `ci.yml` triggers on pushes and pull requests and a tag
push triggers neither — so the workflow that built the wheel reaching PyPI ran
ruff, mypy and pytest and none of the three gates. A gate, as that file puts it,
"is only a gate where it is invoked."

**The finding is one plane down.** The `facts` table has four time columns —
`valid_from`, `valid_to`, `recorded_at`, `superseded_at` — the schema of a
bitemporal store. Both writers that exist set `valid_from` and `recorded_at` to
the same `now`, and `close_fact` writes a single `now` into `valid_to` and
`superseded_at` together. No public method accepts a validity time. What
`get_facts_as_of` reads back is a version chain over write time wearing a
valid-time query, and the suite that proves it passes because its helper writes
rows directly with `recorded_at=valid_from`, a combination no shipped path
produces. The bitemporal mark is withheld on that.

## 2. Mental Model

An **episode** is something that happened, timestamped by the caller if they are
back-filling history.

A **fact** is a triple that was true over an interval, closed when a newer
extraction disagrees.

An **agent_id** is a partition of the episodic plane, and nothing at all on the
semantic one.

A **published number** is recomputed from committed records on every push.

A **gate** is only a gate in the workflow that invokes it.

```mermaid
%% caption: episodes are partitioned by agent_id while facts are shared, and the four time columns on a fact are written from a single clock, so the as-of read is a version chain rather than a belief history
flowchart TB
    OBS["observe(content, timestamp=…)<br/>caller may back-fill the period described"] --> EP[("episodes — agent_id, actors,<br/>salience, importance_score")]
    OBS -.->|"memory_written, only when<br/>events_path AND agent_id are set"| LOG[("events.ndjson —<br/>append-only, prev_hash chain")]
    EP --> VEC[("vec_episodes — agent_id is a<br/>vec0 PARTITION KEY, not a join filter")]
    EP --> FTS[("fts_episodes — BM25")]
    VEC & FTS --> BLEND["recall: 0.5 vector / 0.5 lexical,<br/>or spreading activation over edges"]
    SCOPE{"agent_id = None if cross_agent<br/>else self._agent_id"} --> BLEND
    BLEND --> OUT["what the agent is handed —<br/>its own episodes unless it asks to widen"]
    EP --> REFL["reflect(): the whole episode window<br/>since the last finished run, to an LLM"]
    REFL --> F[("facts — subject, predicate, object<br/>valid_from · valid_to<br/>recorded_at · superseded_at")]
    NOW["now = datetime.now(UTC)"] -.->|"written into valid_from<br/>AND recorded_at, together"| F
    NOW -.->|"close_fact writes the same now into<br/>valid_to AND superseded_at"| F
    F --> ASOF["get_facts_as_of(subject, T):<br/>valid_from <= T AND (valid_to IS NULL OR valid_to > T)"]
    ASOF -.->|"one clock fed both axes, so this reads a<br/>version chain over write time — it cannot<br/>answer what the store BELIEVED at T"| NOBI["no bitemporal mark"]
    TEST["tests/test_bitemporal.py:39-54"] -.->|"_make_fact sets recorded_at=valid_from<br/>and inserts directly: a row no<br/>shipped writer can produce"| ASOF
    FE["forget_entity(name) — GDPR erasure,<br/>crosses every agent in the file"] --> DEL["deletes episodes WHERE the name is in<br/>the caller-supplied actors JSON"]
    DEL -.->|"an episode whose TEXT names the person<br/>but whose actors list omits them survives"| REFL
    REFL -.->|"nothing is keyed on the deleted value,<br/>so the next pass can re-extract it"| NOTOMB["no tombstone mark"]
    F --> SHARED["facts carry no agent_id:<br/>shared across agents by decision,<br/>and fact_count refuses to hide it"]
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `engram/schema.py` | The six tables, and `agent_id` as a vec0 partition key |
| `engram/core.py` | The public surface, and where events are emitted |
| `engram/store.py` | Every SQL path, including the as-of reads |
| `engram/reflection.py` | Extraction, supersession, contradiction counting |
| `engram/events.py` | The NDJSON chain, and the rules that keep it off |
| `scripts/*.sh` | Three invariants, each with its argument written down |
| `tests/test_gates_are_wired.py` | That the gates run where the bytes ship |

## 4. Essential Implementation Paths

`engram/core.py:336` — `agent_id = None if cross_agent else self._agent_id`, the
one line the scope rests on.

`engram/core.py:377-392` and `engram/reflection.py:99-113` — the only two places
a `Fact` is built, both stamping one `now` into two axes.

`engram/store.py:721-726` — `close_fact`, writing the same value into `valid_to`
and `superseded_at`.

`engram/store.py:1235-1246` — `get_facts_as_of`, the valid-time query the write
path never gives anything to distinguish.

`engram/events.py:188-204` — `resolve_events_path`, which returns `None` and
disables the log unless a path or environment variable says otherwise.

`scripts/no-network-at-write.sh:1-45` — an invariant, its enforcement, and the
argument for the shape of the check.

## 5. Memory Data Model

Six tables in one file. `episodes` (content, timestamp, actors, tags, salience,
emotional valence, a `summary_of` list, importance score, agent_id), `facts`
(triple, four time columns, confidence, `derived_from`, `extracted_by`),
`entities`, `edges` (weighted, agent-scoped), `reflections` (one row per
extraction run, with tokens and contradictions resolved), and `access_log` —
which records reads, not writes, and so is the other half of the audit pattern
rather than this one. Vectors live in a `vec_episodes` virtual table partitioned
on agent_id, keywords in an FTS5 table.

## 6. Retrieval Mechanics

Three modes behind one call. Hybrid is the default at a 0.5/0.5 blend, chosen by
measurement rather than taste: `engram-bench longmemeval --sweep` scores every
weighting in one pass, and 2.4.0 moved the default from 0.7/0.3 on the result
that the middle leads all four metrics and "both ends of the range are clearly
worse than the middle". The published table covers all 500 LongMemEval-S
questions over 246,738 ingested turns, with no model in the loop, and the
per-question records are committed so a reader can recompute instead of
trusting. The caveats travel with the numbers: the dataset flags no evidence
turn at all for 21 questions, and more than one for 59% of them, "so counting a
hit when any of them is retrieved is an upper bound on what the model was
handed."

Spreading activation walks Hebbian edges out from what matched. `as_of`
restricts episodes to a timestamp, and resolves inside the KNN scan rather than
after it.

## 7. Write Mechanics

Writes are local and immediate; nothing calls a model on the write path, and a
CI gate holds that structurally. Extraction happens in `reflect()`, which
windows off the last *completed* run so an aborted pass cannot advance the
watermark past episodes it never processed, wraps the entire
extract-insert-supersede-edge sequence in one transaction, and holds the store
lock over the database work but never across the LLM call. A newer extraction
closes every older active fact with the same subject and predicate; a
same-object re-extraction closes silently as agreement, and only a differing
object counts as a contradiction and emits an event.

## 8. Agent Integration

A Python library, an async wrapper, an `engram` CLI, and an MCP server exposing
`remember`, `recall`, `why`, `forget` and `stats` with per-call `agent_id`.
`reflect()` is deliberately not exposed as a tool — the pass that spends tokens
and rewrites the semantic plane stays with the operator. That withholding is the
one real actor boundary here, and it is on the *rewriting* pass rather than on
admission: `forget` is on the tool surface, so the agent erases as readily as a
person does. The `engram` CLI reads and erases the same `.engram` file the
running agent uses, which makes it a correction surface rather than a review
one — nothing waits for approval before it takes effect, and an erasure is
permanent rather than a held state. This report therefore does not carry
`human_review`; `engram/core.py` and `engram/cli.py` carry no pending, staged or
approval state on a memory at this pin.

## 9. Reliability, Safety, and Trust

`why()` returns a fact's provenance episode by episode. The event log, when
configured, chains each event to the last over a canonicalised body and advances
only on a successful write. Encryption is available through SQLCipher with a
`rekey()` method, and `backup()` is a separate path. Against that: the event log
is off by default and off entirely on an unscoped instance, `emit` swallows its
own failures, and `import_json` writes memories that no event records. Erasure
is permanent and unprotected against re-derivation.

## 10. Tests, Evals, and Benchmarks

Twenty-nine test modules, several of which test the project's own process rather
than its behaviour: that the gates run in the workflow that ships bytes, that
the vendored event schema matches the contract the code speaks, and that the
README's numbers are the ones the benchmark records produce. The multi-agent
suite is the strongest single file — its lopsided fixtures exist because "[t]he
old tests all used two-episode stores, where the global top-k trivially contains
everything and the bug is invisible."

## 11. For Your Own Build

Take the gate-wiring test. Most projects that write a CI check stop once it
passes somewhere; this one asks which workflow actually publishes and checks the
gate is in *that* one. The cost is a twenty-line test and the benefit is that a
release cannot quietly skip the invariant.

Take the allow-list over the denylist, and the reason given for it.

And take the warning in the bitemporal columns. Four columns named for two axes
do not make a store bitemporal — one clock feeding both is a version chain, and
a test suite that constructs its own rows will not tell you which you have. The
check is a producer test: find every writer of the validity field and ask
whether any of them can set it to something other than the moment of writing.

## 12. Open Questions

Whether `valid_from` was meant to be caller-settable. `observe()` already takes a
`timestamp` for exactly this reason on the episodic plane — "so `recall(as_of=…)`
places the episode in the period it describes rather than the moment it was
written" — and the fact writer has no equivalent. The gap looks like an omission
rather than a decision.

Whether `forget_entity` is meant to reach episodes that name a person without
listing them as an actor. The docstring calls it GDPR right-to-be-forgotten,
which is a claim about the person rather than about the actors column.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `scripts/no-network-at-write.sh:1-45` | An invariant with its argument written above it |
| `scripts/local-first.sh:1-46` | A check that corrected the invariant it enforced |
| `tests/test_gates_are_wired.py:1-40` | That a gate runs where the bytes actually ship |
| `engram/core.py:336` | A stored scope key reaching the query, widened but never omitted |
| `engram/store.py:721-726`, `:1235-1246` | Two time axes, one clock, and the query that cannot tell |
| `tests/test_multiagent.py:474-529` | A must-not-retrieve assertion with its control beside it |

## History

**2026-09-19** — re-pinned to [`240a4d9d433e2f4a366d8877279449381b59b6fa`](https://github.com/TAIPANBOX/engram/commit/240a4d9d433e2f4a366d8877279449381b59b6fa), 2 commits on. `human_review` is **withdrawn**, and the record's own closing sentence is the reason, kept here verbatim because it was already right: *"It is an after-the-fact surface: nothing waits for approval before it takes effect, and the erasure is permanent rather than a held state."* Under the question the mark now asks, that settles it. The tree was checked for an admission state at this pin and has none. Worth recording beside the withdrawal: the one place this design does hold something back from the agent is `reflect()`, kept off the tool surface so the pass that rewrites the semantic plane stays with the operator — while `forget` is on it, so erasure is not held back at all. The other three marks stand. Screened again first; nothing was installed and no suite was run.

**2026-09-16** — [`c6d0d3f2aabcba6c96a7c4f503a2ccc9dabb74a9`](https://github.com/TAIPANBOX/engram/commit/c6d0d3f2aabcba6c96a7c4f503a2ccc9dabb74a9) — first reading, at a commit dated 13 September 2026. Screened before opening, from a shallow clone: three files scanned, no auto-run surfaces, no build-time execution points, one unpinned dependency surface and one dependency file inside the seven-day cooldown. `CLAUDE.md` is addressed to a reading agent and was recorded as data. Nothing was installed, built or run.

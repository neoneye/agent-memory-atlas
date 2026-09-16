---
title: "Claudinio Brain"
eyebrow: "The current-value read and the as-of read are the same code path, so they cannot disagree"
description: "A Rust knowledge-graph memory in one SQLite file where valid time comes from the caller and transaction time from the clock, a retraction means never-true rather than no-longer-true, and a linter reports facts the retrieval paths cannot reach."
root: ../..
page_kind: system
source_name: "claudin-io/claudinio-brain"
source_url: https://github.com/claudin-io/claudinio-brain
archive_name: "claudin-io--claudinio-brain"
revision: 6b6e57413aa38bb7cba24183c21bb41510d2d72c
revision_url: https://github.com/claudin-io/claudinio-brain/commit/6b6e57413aa38bb7cba24183c21bb41510d2d72c
analyzed_at: 2026-09-16
capabilities: "bitemporal, trust_state, human_review, negative_eval"
capability_evidence:
  bitemporal: "two clocks, one of them the caller's, and a single read arm for both now and then | src/store/schema.sql:71-76, src/brain/mod.rs:711-733, src/recall.rs:1214-1224, src/cli.rs:184-186 | the schema labels the axes in its own comments — \"Valid time: when this was true in the world\" against \"Transaction time: when the brain learned it\" — and the insert binds them from different sources: `micros(w.valid_from)`, which comes from the caller's `--at` (\"When this became true. Defaults to now\"), and `micros(w.now)`, which comes from the clock. A backdated write is therefore an ordinary write, and the README's opening example asserts a January value and a June value in either order and reads the January one back with `--as-of 2026-03-01`. The read is the part worth copying: `for_when` builds one predicate for every temporal mode, and `Now` is not a separate branch but `AsOf(now)` — \"the two cannot drift apart because there is only one arm\", so a bug in the as-of filter cannot hide behind a working current-value query | tests/step3_bitemporal.rs and tests/step15_expiry.rs, with evals/temporal.jsonl carrying \"current value after N changes, value at a past instant, full history, backdated writes, corrections, retractions\" as a scored suite"
  trust_state: "retraction as a stored field meaning never-true, kept apart from the supersession columns that mean no-longer-true | src/store/schema.sql:73-78, src/brain/mod.rs:1444-1467, src/recall.rs:1215, src/brain/types.rs:227-236 | `retracted_at` is annotated \"set when we learn it was NEVER true\", and it is a different column from `valid_to` and `superseded_by`, so the store does not collapse a value that expired into a value that was wrong. It withholds rather than decorates: `for_when` opens every temporal predicate with `AND f.retracted_at IS NULL` and the comment above it says the exclusion holds \"in every mode, including History\" — a retracted claim leaves even the audit view, because \"a retracted claim was never true, so replaying it would be a lie\". The distinction reaches the caller as well: a write returns one of `created`, `reasserted`, `superseded` or `corrected`, and `Corrected { retracted, created }` is documented as \"a correction at the same instant: the previous claim was never true\" | tests/step3_invariants.rs and tests/step17_find.rs exercise the retracted-fact exclusions, and evals/temporal.jsonl scores corrections and retractions as separate case families"
  human_review: "the studio, a loopback web surface that writes | src/studio/server.rs:129-136, src/studio/assets/studio.js:11-12 | the studio serves a snapshot of the brain over a loopback socket behind a constant-time token check, and four of its seven routes mutate: `POST /api/remember`, `/api/link`, `/api/retract` and `/api/alias`, beside `/api/recall` and `/api/why` for reading. A person opens the graph, follows a fact to the `recorded_at` of whatever closed it, and retracts what is wrong — inspection and correction on the same surface, against the same file the agent reads. `brain lint` is the other half and is deliberately not this half: it \"reports and suggests; repairing is a separate, explicit decision\" | tests/step9_studio.rs covers the routes and the escaping, including that no raw `<` survives into the page"
  negative_eval: "a committed scope-exclusion suite that asserts its own premise before asserting the absence | tests/step16_scope.rs:67-145 | `the_churn_crowds_out_the_answer_until_it_is_excluded` first asserts that the noise does reach the answer — \"the premise of this test is gone\" is the failure message — then asserts that with the namespace excluded no `task_` statement answers, then asserts exactly which single statement is left. The positive control is inside the same test rather than beside it, so the must-not assertion cannot pass on an empty result. `an_unscoped_fact_survives_an_exclusion` guards the SQL trap that would make it pass for the wrong reason, since `scope <> 'todo'` is NULL for an unscoped fact and a plain inequality \"would drop every unscoped fact in the brain\", and `every_channel_honours_the_exclusion` repeats the assertion for the lexical, name and semantic channels in turn, because the semantic one filters after the search rather than inside it | the suite runs in the committed `cargo test` set, and evals/graph.jsonl and evals/kin.jsonl score retrieval quality separately against a holdout \"nothing is tuned against\""
stack_storage: "sqlite"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A fact — entity, predicate, object (text, number or another entity), with valid time, transaction time, retraction, confidence, scope, source and a JSON locator; an object pointing at an entity makes the fact an edge"
  storage: "One SQLite file, one binary, no server: facts, entities, aliases, predicates, an FTS5 index and a vec0 table partitioned on scope"
  retrieval: "Four channels — words, names, a graph walk and kinship — with a semantic channel over a static potion-base-8M embedding; every mode carries the same temporal predicate"
  write: "`brain remember --subject --predicate --value --at --until --source`, a batch file, an MCP `remember` tool, and harness hooks that record what a session did from the transcript"
  update_delete: "A new value closes the old one rather than overwriting it; a correction at the same instant retracts instead, and the write returns which of the four happened"
  scoping: "`scope` is a column and a vec0 partition key, but the query carries it as an optional argument that defaults to none, so nothing separates namespaces unless the caller asks"
  integration: "A CLI, an MCP server, a loopback studio UI, and installable hooks for Claude Code, Codex, Cursor, Gemini, Cline, OpenCode and others"
  background: "Session hooks that capture what a session did; `brain lint` scans for structurally unreachable facts and `brain repair` acts on it as a separate decision"
  trust: "Retraction as never-true, separated from expiry; declared aliases resolve writes and learned ones deliberately do not; a linter that reports what retrieval cannot reach"
  strengths: "Two things. First, the single read arm: `for_when` builds one temporal predicate for every mode and `Now` is literally `AsOf(now)`, so \"the two cannot drift apart because there is only one arm\" — the structural answer to a store whose current-value path works while its as-of path quietly does not. Second, `brain lint`, which reports \"[w]hat the brain can see wrong with itself\": findings are structural defects where \"the fact is stored, it is true, and retrieval still cannot use it\", the case that motivated it is named (\"a brain where 59 out of 69 `is_a` facts had a string where an entity belonged. Every voucher knew its class and no voucher was reachable from it\"), and finding it had required \"opening a 3D scene and noticing loose dots\". A memory system that can detect its own unreachable contents and does not report them \"is failing at its job, so this module exists to make that a command instead of an observation.\" The alias split is a third: declared aliases resolve where a write lands and learned ones never do, because \"they are guesses made from watching questions, and a guess must never decide where a fact is stored\" — enforced \"by this `WHERE` clause and by nothing else, so it is load-bearing\", which is the comment a future reader needs"
  risks: "Scope is the gap. It is stored on the fact and used as a vec0 partition key, but the read path takes it as `Option<String>` defaulting to `None`, so a caller that forgets it searches everything; the exclusion form is a post-filter on the semantic channel, since a partition key \"indexes equality and cannot express an exclusion\", which the project documents and tests but which means that channel trims after ranking. There is no mutation audit beyond the fact table itself, and the retraction reason is appended into `source` by string concatenation — `source = COALESCE(source, '') || ' [retracted: ' || ?2 || ']'` — so the field naming who asserted a claim also carries why it was withdrawn, and neither can be parsed back out reliably. And nothing is keyed on a rejected value: `live_facts` excludes retracted rows precisely so that they \"must not influence where a new fact lands\", so re-asserting a retracted value produces a fresh `created` fact with no sign that the brain once rejected it"
---

## 1. Executive Summary

Claudinio Brain is "[b]itemporal knowledge-graph memory for AI agents. One
binary, one file, no server, and no model on the write path." MIT, Rust, version
0.3.0, 13,173 lines across 28 source files, one SQLite database holding facts,
entities, aliases and predicates with an FTS5 index and a vector table beside
them.

The README opens with the problem statement rather than a feature list:

> "Give an agent a vector store and ask how a service authenticates. It will
> find every answer anyone ever wrote down and pick one. It has no way to know
> which of them is still true, because \"we use JWT\" and \"we *used* JWT\" are
> the same sentence to a similarity score."

The answer is a timeline. Writing a new value does not overwrite the old one, it
closes it, so `brain get auth strategy` and `brain get auth strategy --as-of
2026-03-01` are answered from one record.

**The mechanism to take away is how the two reads are kept honest.** A store
with a working current-value query and a subtly broken as-of query looks
correct in daily use, and the bug surfaces only when somebody asks about the
past — which is the one question such a store exists to answer.
`RecallQuery::for_when` refuses the shape that allows it: one function builds
the temporal predicate for every mode, and the current-value mode is not a
branch of its own.

> "It also leaves `Now` with nothing of its own to mean: it *is* `AsOf(now)`,
> and the two cannot drift apart because there is only one arm."

The atlas has just read the failure this prevents. [Engram
Cognitive](../engram-cognitive/) carries the same four columns and stamps them
all from one clock, so its as-of query reads a version chain over write time.
Here the two axes come from different places by construction: the insert binds
`micros(w.valid_from)` from the caller's `--at` and `micros(w.now)` from the
clock, in the same statement.

**The second distinction is retraction.** `valid_to` means a value stopped being
true; `retracted_at` is annotated "set when we learn it was NEVER true", and the
two are different columns. A retraction is excluded from every read mode
including history, because "a retracted claim was never true, so replaying it
would be a lie" — an unusual choice, and a defensible one, since a history view
that replays a claim nobody ever should have made is an audit trail that
misleads. The distinction reaches the caller too: a write returns `created`,
`reasserted`, `superseded` or `corrected`, and an agent that gets a `superseded`
it did not expect is told what that means — "the brain already knew something".

## 2. Mental Model

A **fact** is an entity, a predicate and an object over an interval of world
time, recorded at an instant of brain time.

A **supersession** is a value that stopped being true.

A **retraction** is a value that was never true, and it leaves even the history.

A **scope** is a namespace you must remember to ask about.

A **lint finding** is a fact that is stored, true, and unreachable.

```mermaid
%% caption: valid time comes from the caller and transaction time from the clock, one function builds the temporal predicate for every read mode, and a retraction is excluded from all of them including history
flowchart TB
    CLI["brain remember --subject auth --predicate strategy<br/>--value JWT --at 2026-01-01 --source adr-004"] --> W{"which of four things<br/>is this write?"}
    CLOCK["the clock: w.now"] -.->|"bound to recorded_at"| F
    CLI -.->|"--at, default now,<br/>bound to valid_from"| F
    W -->|"a first value"| CREATED["Created"]
    W -->|"the same value again"| RE["Reasserted — reinforced,<br/>not duplicated"]
    W -->|"a different value later"| SUP["Superseded: the old one is<br/>CLOSED, not deleted"]
    W -->|"a different value at the<br/>SAME instant"| COR["Corrected: the old one was<br/>never true — retracted"]
    CREATED & RE & SUP & COR --> F[("fact — valid_from · valid_to<br/>recorded_at · retracted_at<br/>superseded_by · scope · source")]
    F --> FW["RecallQuery::for_when(when, now, scope)"]
    FW --> GUARD["every mode opens with<br/>AND f.retracted_at IS NULL"]
    GUARD -.->|"including History: 'a retracted claim<br/>was never true, so replaying it<br/>would be a lie'"| GONE["a retraction leaves the audit view too"]
    GUARD --> ONEARM["Now IS AsOf(now) — not a separate branch"]
    ONEARM -.->|"'the two cannot drift apart<br/>because there is only one arm'"| SAFE["the as-of read cannot rot<br/>behind a working current-value read"]
    ONEARM --> CH["four channels: words · names ·<br/>graph walk · kinship, plus semantic"]
    CH --> ANS["what the agent is handed"]
    SCOPE{"scope: Option&lt;String&gt;, default None"} -.->|"omittable, so a caller that forgets it<br/>searches the whole brain"| CH
    RETR["retracted rows are excluded from live_facts<br/>so they 'must not influence where<br/>a new fact lands'"] -.->|"so re-asserting a retracted value<br/>returns Created, with nothing keyed<br/>on the value that was rejected"| NOTOMB["no tombstone mark"]
    LINT["brain lint — what the brain<br/>can see wrong with itself"] --> FIND["'the fact is stored, it is true,<br/>and retrieval still cannot use it'"]
    FIND -.->|"lint never writes; repair is a<br/>separate, explicit decision"| REPAIR["brain repair"]
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `src/store/schema.sql` | Six tables, the two time axes, and the indexes that make them cheap |
| `src/brain/mod.rs` | Writes, the four outcomes, retraction, and entity resolution |
| `src/recall.rs` | The four channels and the one temporal predicate they share |
| `src/lint.rs`, `src/repair.rs` | What the brain can see wrong with itself, and the separate decision to fix it |
| `src/studio/` | A loopback UI that reads and writes |
| `src/hook.rs`, `hooks/` | Harness integrations for eight agent surfaces |
| `evals/` | Five scored suites plus a holdout nothing is tuned against |

## 4. Essential Implementation Paths

`src/recall.rs:1214-1224` — one temporal predicate for every mode, and the
argument for why `Now` has no branch of its own.

`src/brain/mod.rs:711-733` — the insert, binding valid time from the caller and
transaction time from the clock in one statement.

`src/brain/types.rs:227-236` — four write outcomes, each documented with what it
means rather than what it does.

`src/brain/mod.rs:1444-1467` — `live_facts` and `retract_fact`: what a retraction
excludes, and where its reason is written.

`src/brain/mod.rs:1469-1488` — `find_entity`, where declared aliases resolve a
write and learned ones are refused.

`src/lint.rs:1-17` — a memory system reporting on its own unreachable contents.

## 5. Memory Data Model

One `fact` row is the unit: entity, predicate, and an object that is text, a
number or another entity — the last making the fact an edge, which is how the
graph exists without a second table. Around it: `valid_from`/`valid_to` for world
time, `recorded_at`/`retracted_at`/`superseded_by` for what the brain did,
`confidence`, `reassert_count`, `scope`, `source`, and a JSON `locator` described
in the schema as "index, not warehouse". Entities carry declared and learned
aliases in a separate table with the distinction stored on the row.

## 6. Retrieval Mechanics

Four channels answer one question — lexical BM25 over FTS5, entity-name
resolution, a graph walk over entity-valued facts, and kinship, which finds
entities that share a value with the one asked about and have no edge to it.
A semantic channel sits beside them over a static potion-base-8M embedding
shipped in the repository, which is why the project can claim "no embedding
endpoint to call" while still embedding on write. Every channel receives the
same temporal predicate from `for_when`.

## 7. Write Mechanics

A write resolves the entity, decides which of four things is happening, and
either creates, reinforces, closes-and-creates, or retracts-and-creates. Closing
sets `valid_to` on the old row and points `superseded_by` at the new one, so the
closure's own `recorded_at` is when the change was learned. The vector is written
inside the same transaction as the fact, because "[a] vector written separately
could be lost on a crash, leaving a fact the semantic channel can never find --
invisible, and undetectable without a scan."

## 8. Agent Integration

A CLI, an MCP server, a loopback studio, and hook bundles for Claude Code,
Codex, Cursor, Gemini, Cline, OpenCode and others, registered through a plugin
manifest. The Stop and SessionEnd hooks record what a session did "from the
harness's own transcript, with no model involved."

## 9. Reliability, Safety, and Trust

The strong parts are the temporal invariants, the retraction semantics, and the
alias split. The weak part is scope: it is stored, it partitions the vector
index, and the query still takes it as an optional argument that defaults to
nothing, so isolation depends on every caller remembering. There is no mutation
log separate from the fact table, and a retraction's reason is concatenated into
`source`, the same free-text column that records who asserted the fact.

## 10. Tests, Evals, and Benchmarks

Thirty-six integration test files, and an eval suite that states its own premise:
"Tests prove correctness; evals measure quality. A brain can satisfy every
bitemporal invariant and still be useless if recall never surfaces the answer."
Five scored suites plus `--holdout`, "the suite nothing is tuned against", and
`--misses` to name the cases still wrong. Each suite's README entry says what it
justifies — `graph.jsonl` exists to justify having a graph at all, `kin.jsonl` to
justify looking past it.

## 11. For Your Own Build

Collapse your current-value read into your as-of read. If `now` is a separate
code path from `as_of`, the two will disagree eventually and only the rarer one
will be wrong.

Separate "stopped being true" from "was never true" in the schema, not in a
comment, and decide deliberately which of them your history view replays.

Write the lint. A fact that is stored, true and unreachable fails silently, and
no test you would think to write covers it.

## 12. Open Questions

Whether scope should default to the brain's own configuration rather than to
nothing. Every other boundary in this project is enforced structurally; this one
is left to the caller, and the tests that cover it all pass the argument
explicitly.

Whether a retracted fact should really leave `history`. The argument given is
sound for replay, but it means the record of a claim having been made and
withdrawn exists only inside a concatenated `source` string.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `src/recall.rs:1214-1224` | One arm for now and then, and why that is the point |
| `src/store/schema.sql:71-78` | Two time axes labelled in the schema itself |
| `src/brain/types.rs:227-236` | Four write outcomes, each meaning something different |
| `src/brain/mod.rs:1469-1488` | A load-bearing `WHERE` clause, and the comment that says so |
| `src/lint.rs:1-17` | What a memory system can see wrong with itself |
| `tests/step16_scope.rs:67-88` | A must-not assertion that proves its own premise first |

## History

**2026-09-16** — [`6b6e57413aa38bb7cba24183c21bb41510d2d72c`](https://github.com/claudin-io/claudinio-brain/commit/6b6e57413aa38bb7cba24183c21bb41510d2d72c) — first reading, at a commit dated 1 September 2026. Screened before opening, from a shallow clone: nine files scanned, three auto-run surfaces (a Claude Code plugin manifest and two hook directories registering SessionStart, Stop and UserPromptSubmit), no build-time execution points, one unpinned dependency surface and none inside the seven-day cooldown. `Cargo.lock` is present and unchanged for fourteen days. Nothing was installed, built or run.

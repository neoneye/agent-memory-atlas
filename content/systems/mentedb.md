---
title: "MenteDB"
eyebrow: "AS OF, in a query language of its own"
description: "A purpose-built Rust memory engine with a WAL, HNSW and BM25 under a query language whose AS OF clause judges a memory against the instant asked for rather than dropping whatever is currently invalid."
root: ../..
page_kind: system
source_name: "nambok/mentedb"
source_url: https://github.com/nambok/mentedb
archive_name: "nambok--mentedb"
revision: 4ba993dcf52f0a17065a9a2484fe59777dcd45d4
revision_url: https://github.com/nambok/mentedb/commit/4ba993dcf52f0a17065a9a2484fe59777dcd45d4
analyzed_at: 2026-09-13
capabilities: "bitemporal, scope_enforced, negative_eval"
capability_evidence:
  bitemporal: "the memory row and the query language — validity and record time are separate queryable fields | crates/mentedb-core/src/memory.rs:58 (`created_at`), :76-80 (`valid_from`, `valid_until`), crates/mentedb-query/src/ast.rs:80-95 | the `Field` enum the query planner ranges over carries `Created` and `ValidAt` as distinct members, so an MQL query can constrain record time with the ordinary comparison operators and validity with `AS OF <t>` in the same statement. The AST comment states the semantics — `AS OF` keeps memories whose window satisfies `valid_from <= t < valid_until`, *\"so a query can see what was true at a past moment, including facts later superseded\"* — and `invalidate_memory` (crates/mentedb/src/lib.rs:1966) closes a window rather than deleting the row | crates/mentedb/tests/integration.rs:1856 (`as_of_recalls_the_validity_window_including_superseded_facts`), :135; crates/mentedb/tests/memory_dedup.rs:84"
  scope_enforced: "entity and cluster reads — agent and user ids as required parameters, compared before a row is used | crates/mentedb-core/src/memory.rs:43, :50, :68 (`agent_id`, `user_id`, `space_id`), crates/mentedb/src/lib.rs:4182-4188, :4226, :4517, :4559, :3054 | the keys are stored on every memory, and the read paths that take them take them as mandatory positional arguments rather than options — `all_entity_names(&self, user: UserId, agent: AgentId)` loads each page and skips it unless both the agent id and the user id match the arguments, and the consolidation path refuses a cluster containing another user's memory. The bound is real and stated in section 6: the primary `recall(&self, query: &str)` takes only an MQL string, so the general recall path applies whatever scope the query names and none if it names none | no committed case asserts a cross-user recall returns nothing"
  negative_eval: "recall — a superseded fact and a not-yet-valid fact must each be absent at the instant asked for | crates/mentedb/tests/integration.rs:1856-1900 | the fixture stores three memories — one always valid, one superseded at t=1000, one valid only from t=2000 — and asserts `!has(&at_500, \"becomes true later\")` and `!has(&at_1500, \"was true early then replaced\")`, each beside a positive control asserting the stable fact is present in the same result. The store is populated by construction, so neither negative can pass on an empty result, and both are about a particular named memory rather than a rate. `memory_dedup.rs:84` adds the regression half, written from a reported production bug where two contradictory facts both stayed live and recall kept answering with the stale one | `cargo test`; not run, the screen reports two cargo `build.rs` build-time execution points"
stack_storage: "files"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A memory row with an embedding, a type, a salience and a confidence, carrying agent, user and space ids and an optional validity window"
  storage: "A purpose-built page store with a write-ahead log for crash recovery, an HNSW vector index and a BM25 index beside a graph crate"
  retrieval: "MQL — a query language with similarity, substring and set operators over typed fields, including `Created` for record time and `AS OF` for validity"
  write: "A turn is processed into extracted memories; a contradicting value closes the loser's validity window rather than deleting it"
  update_delete: "Supersession by closing `valid_until`; `invalidate_memory` sets the bound so the row stays readable at an earlier instant"
  scoping: "`agent_id`, `user_id` and `space_id` on the row, required as parameters on the entity and cluster reads and expressible in MQL, but not applied by the primary recall unless the query says so"
  integration: "A Rust library with Python and TypeScript SDKs, a CLI, a server crate and a replication crate"
  background: "Consolidation, enrichment and entity linking run over the store; a WAL checkpoint underneath"
  trust: "A confidence score and a salience score, both continuous; conflict resolution picks a strategy rather than recording a state"
  strengths: "Two time axes that are both queryable fields, an AS OF whose test asserts the superseded and the not-yet-valid are each absent, and a dedup regression written from a reported production bug"
  risks: "The primary recall takes only a query string, so scope is enforced where a parameter demands it and absent where the caller writes the MQL; the WAL is crash recovery rather than an audit of what changed"
---

## 1. Executive Summary

MenteDB is a memory engine written as a database — about 61,800 lines of Rust
across fourteen crates, with its own page store, a write-ahead log, an HNSW vector
index, a BM25 index, a graph crate, a replication crate, and Python and TypeScript
SDKs over the top.

**Its distinctive contribution is a query language with two time axes**, and the
semantics are argued in the AST rather than left to a reader. `Field` carries
`Created` for record time and `ValidAt` for validity, both usable in one
statement, and the comment on `ValidAt` states what `AS OF` means and why:

> Temporal validity at a point in time: `AS OF <t>` keeps only memories that were
> valid at timestamp `t` (valid_from <= t < valid_until), so a query can see what
> was true at a past moment, including facts later superseded.

The last clause is the design decision. Most stores in this atlas that track
validity use it to *drop* what is currently invalid; this one judges each memory
against the instant asked for, so a superseded fact is visible when you ask about
a moment it was true and hidden when you ask about now. `invalidate_memory`
(`crates/mentedb/src/lib.rs:1966`) closes a window rather than deleting a row,
which is what makes that possible.

**The test that pins it is the best thing in the repository.**
`as_of_recalls_the_validity_window_including_superseded_facts` stores three
memories — one always valid, one superseded at t=1000, one valid only from t=2000
— and then asks at two instants:

```rust
// AS OF 500: stable + superseded are valid; future is not yet valid.
assert!(has(&at_500, "stable fact"));
assert!(has(&at_500, "was true early then replaced"));
assert!(!has(&at_500, "becomes true later"));
```

Every negative sits beside a positive over the same populated store, so neither
can pass on an empty result. That earns `negative_eval`, and it is the kind that
is about a particular memory rather than a rate.

**Beside it is a regression written from a real failure.**
`crates/mentedb/tests/memory_dedup.rs:84` opens with the bug it exists for: *"i
use next.js for the front end" then "now i use react for the front end" left BOTH
facts live, and recall kept answering with the stale one*, and it records that the
old rule *"only created an edge, never invalidating the loser out of recall."* A
test that names the production symptom and the mechanism that failed is worth more
than three that assert a happy path.

Three marks. `scope_enforced` is earned with a bound worth reading in section 6,
and the other three are withheld.

## 2. Mental Model

A memory is a row with a validity window, and time is the axis everything turns
on.

```mermaid
%% caption: invalidation closes a window rather than deleting a row, so the same store answers differently depending on the instant the query names
flowchart TB
    T["turn"] --> EX["extraction"]
    EX --> M[("memory row:<br/>embedding, salience, confidence,<br/>agent_id, user_id, space_id,<br/>valid_from, valid_until, created_at")]
    M --> CONF{"contradicts a live value?"}
    CONF -->|yes| INV["invalidate_memory:<br/>close the loser's valid_until"]
    CONF -->|no| LIVE["stays live"]
    INV --> M
    Q["MQL query"] --> P["parse + plan"]
    P --> F1{"AS OF t supplied?"}
    F1 -->|yes| W["keep rows where<br/>valid_from &lt;= t &lt; valid_until"]
    F1 -->|no| NOW["keep rows valid now"]
    W --> IDX
    NOW --> IDX["HNSW + BM25 + graph"]
    IDX --> CW["context window,<br/>token-budget aware"]
    W -.->|"a superseded fact is visible<br/>at an instant it was true"| CW
```

The dotted edge is what separates this from a store that simply hides invalid
rows.

## 3. Architecture

Fourteen crates, and the separation is the kind a database has rather than the
kind a library has: `mentedb-storage` owns pages and the WAL, `mentedb-index`
owns HNSW and BM25, `mentedb-query` owns the AST, parser and planner,
`mentedb-graph`, `mentedb-consolidation`, `mentedb-extraction`,
`mentedb-embedding`, `mentedb-replication`, `mentedb-server` and `mentedb-cli`
sit around them, and `mentedb-core` holds the types they share.

**What has to be running is nothing.** It is an embedded engine — open a
directory, get a `MenteDb`. The server crate and the Docker compose file are for
when you want it hosted, and the Python and TypeScript SDKs bind the same core.

The WAL is `//! Write-Ahead Log: append-only log for crash recovery` with a
documented on-disk entry format carrying an LSN, a page id, compressed data and a
CRC32. It is durability infrastructure — see section 9 for why that is not the
audit mark.

## 4. Essential Implementation Paths

- **Memory type** — `crates/mentedb-core/src/memory.rs`: ids and scope (41-70),
  validity window (76-80), `created_at` (58).
- **Query language** — `crates/mentedb-query/src/ast.rs`: `Field` including
  `Created` and `ValidAt` (80-95), `Operator` (97-113);
  `crates/mentedb-query/src/parser.rs` — `AS OF` parse tests (709, 731).
- **Recall** — `crates/mentedb/src/lib.rs`: `recall` (1429), `query` (1445),
  `recall_reranked` (1458), `recall_similar_filtered` (1501),
  `recall_for_action` (1567).
- **Invalidation** — `crates/mentedb/src/lib.rs:1966` (`invalidate_memory`),
  dedup and supersession around `:2674-2693`.
- **Scope on reads** — `crates/mentedb/src/lib.rs:4182-4188` (`all_entity_names`),
  `:4226`, `:4517`, `:4559`, cluster ownership at `:3054`.
- **Storage** — `crates/mentedb-storage/src/engine.rs`, `wal.rs`.
- **Indexes** — `crates/mentedb-index/src/hnsw.rs`, `bm25.rs`.
- **Tests** — `crates/mentedb/tests/integration.rs` (AS OF at 1856),
  `memory_dedup.rs` (84), `scenarios.rs`, `realistic.rs`, `process_turn.rs`.

## 5. Memory Data Model

A memory carries content, an embedding, a `MemoryType`, a `Salience`, a
`Confidence`, an access count and timestamps, plus three identifiers —
`agent_id`, `user_id`, `space_id` — and an optional `valid_from` / `valid_until`
pair.

`Confidence` is a number and `Salience` is a number. There is no discrete status:
`crates/mentedb-core/src/conflict.rs` defines a `Resolution` enum with
`KeepLatest` and `KeepHighestConfidence`, which is a *strategy* for choosing
between two rows rather than a state recorded on either. **`trust_state` is
withheld** — the rubric asks for a status that can withhold a memory, and a
confidence float ranks rather than withholds.

## 6. Retrieval Mechanics

MQL is parsed to an AST, planned, and run against HNSW, BM25 and the graph, with
results assembled into a token-budgeted context window.

**Scope is enforced where a parameter demands it and expressible everywhere
else.** The entity and cluster reads take the keys as mandatory positional
arguments — `all_entity_names(&self, user: UserId, agent: AgentId)` compares
`mem.agent_id != agent || mem.user_id != user` before using a row, and the
consolidation path refuses a cluster containing another user's memory
(`:3054`). Those are real read-path predicates on a stored key, and they earn the
mark.

The bound is the primary path. `recall(&self, query: &str)` takes only an MQL
string, so whether a general recall is scoped depends on whether the caller wrote
`Agent` or `Space` into the query. A deployment that serves two users from one
database and does not template the scope into every query has no boundary on that
path. `Agent` and `Space` are `Field` members, so the language can express it; the
engine does not insist.

## 7. Write Mechanics

`process_turn` extracts memories from a turn and stores them; writes are
synchronous into the page store behind the WAL, and retrievable immediately.

**Supersession closes a window rather than deleting a row**, which is the write
half of the AS OF design. When a new value contradicts a live one, the loser's
`valid_until` is set. The dedup regression records what that fixed: before it, the
rule *"only created an edge, never invalidating the loser out of recall"*, so both
facts stayed live and recall kept answering with the stale one.

**`tombstone` is withheld.** Nothing keys a record on a rejected value:

```sh
grep -rn -i "tombstone" crates --include="*.rs"
```

Nothing in the storage engine at the pinned commit. A superseded memory keeps its
content and its closed window, so the store remembers *that* a value stopped
being true and can still return it for an earlier instant — which is more than
most manage and is not the same as refusing to re-assert it. The same fact
extracted again tomorrow is a new live row.

## 8. Agent Integration

A Rust library first, with Python and TypeScript SDKs, a CLI, and a server crate
with an admin query endpoint. The integration surface is MQL: an agent that can
compose a query gets the full language, including `AS OF`.

## 9. Reliability, Safety, and Trust

The WAL, the CRC32 per entry and the replication crate are the reliability story,
and they are the parts of this that look most like a database.

**`audit_log` is withheld, deliberately.** A write-ahead log is an append-only
record of mutations, which is close enough to the words of the rubric to need an
answer. Its purpose here is crash recovery, its entries are physical — an LSN, a
page id, compressed page data — and it carries no actor, no action vocabulary and
no reason. It cannot answer *who changed this memory and why*, only *what bytes
must be replayed*, and a checkpoint discards it once the pages are durable. The
atlas treats git history the same way: a real mechanism, noted in prose, not this
mark.

**`human_review` is withheld** for absence — there is no surface where a person
inspects or adjudicates a memory. `test_pipeline_audit.py` at the repository root
is a manual verification script that requires a live OpenAI or Anthropic key, not
a review surface and not a committed test.

## 10. Tests, Evals, and Benchmarks

Substantial Rust test suites — `integration.rs` at 1,910 lines, `realistic.rs` at
1,119, `scenarios.rs` at 1,089 — plus `benchmarks/longmemeval/`, which carries a
requirements file pinning nothing and calling OpenAI and Anthropic, so the
benchmark is a harness rather than a committed result.

The two tests that matter are described in section 1. What makes the AS OF one
count is that its three negatives each sit beside a positive over the same
three-memory store, so none can pass against a retriever that returned nothing —
the failure mode that makes most negative assertions in this corpus worthless.

No paper: a grep of the README, `ARCHITECTURE.md`, `VISION.md` and `docs/` for
`arxiv`, `bibtex`, `@article`, `Citation` and `doi` returns nothing, and there is
no `CITATION.cff`.

Nothing was run. The screen reports two cargo `build.rs` build-time execution
points and a floating benchmark requirements file.

## 11. For Your Own Build

### Steal

**Make validity a query field, not a filter the store applies for you.** `AS OF t`
judging each row against the instant asked for — rather than dropping whatever is
invalid now — is the difference between a store that has history and a store that
can be *asked* about history. It costs one enum member and one comparison.

**Invalidate by closing a window, never by deleting.** The row stays readable at
an earlier instant, which is what makes the previous point possible.

**Put the semantics in the AST comment.** The three lines on `ValidAt` say what
the operator does and what it deliberately does not do. A reader of the planner
does not have to reconstruct the intent from the comparison.

**Write the regression test from the symptom.** *"i use next.js for the front
end" then "now i use react"* names the user-visible failure, and the comment adds
the mechanism that failed — an edge was created and the loser was never
invalidated out of recall. Both halves are needed for the test to survive a
refactor.

**Pair every temporal negative with a positive at the same instant.** Three
`assert!(!has(...))` calls in that test would prove nothing on their own.

### Avoid

**Letting the primary read path take no scope.** `recall(query: &str)` is a clean
signature and it means the boundary lives in whatever string the caller composed.
The typed reads beside it demand the ids; the one an agent is most likely to call
does not.

**Reading a WAL as an audit trail.** It is append-only and it records mutations
and it is still the wrong thing to point at when someone asks what happened to a
memory. Two mechanisms, two purposes.

### Fit

This suits a team that wants memory with database properties — durability,
replication, an index they can reason about, and a query language they can
template — and that will template the scope into those queries themselves. The
temporal model is the best reason to choose it: if your application needs to ask
what it believed last March, very little else in this atlas answers that as
directly.

It is the wrong fit where the boundary must be enforced by the engine rather than
by the query, where a wrong value must be unable to return, or where a reviewer
needs somewhere to stand. Those are all absences rather than weaknesses of the
parts that exist.

## 12. Open Questions

- **Should `recall` take the scope?** Every typed read beside it does, and the
  asymmetry is the one thing between this and an enforced boundary.
- **Does anything consult `valid_until` when extracting?** A fact invalidated
  last week and re-extracted today becomes a new live row, and the closed window
  beside it is the record that could have prevented it.
- **Is `space_id` used anywhere on a read path?** It is on the row beside
  `agent_id` and `user_id`, and it did not appear in the comparisons those two do.
- **What does the replication crate do with a closed validity window?** Two
  replicas disagreeing about when a fact stopped being true is the interesting
  failure, and it was not traced here.

## Appendix: File Index

**Core types**

- `crates/mentedb-core/src/memory.rs` — ids (41-50), type and embedding (52-56),
  `created_at` (58), scores (64-66), `space_id` (68), validity (76-80)
- `crates/mentedb-core/src/conflict.rs` — `Resolution` (22)
- `crates/mentedb-core/src/edge.rs`, `tier.rs`

**Query**

- `crates/mentedb-query/src/ast.rs` — `Field` with `Created` and `ValidAt` (80-95),
  `Operator` (97-113)
- `crates/mentedb-query/src/parser.rs` — `AS OF` parse tests (709, 731)

**Engine**

- `crates/mentedb/src/lib.rs` — `recall` (1429), `query` (1445),
  `recall_similar_filtered` (1501), `recall_for_action` (1567),
  `invalidate_memory` (1966), supersession (2674-2693), cluster ownership (3054),
  `all_entity_names` (4182-4188), further scope comparisons (4226, 4517, 4559)
- `crates/mentedb-storage/src/engine.rs`, `wal.rs` (format at 3-8)
- `crates/mentedb-index/src/hnsw.rs`, `bm25.rs`

**Tests and benchmarks**

- `crates/mentedb/tests/integration.rs` — AS OF (1856-1900), `valid_until` (135)
- `crates/mentedb/tests/memory_dedup.rs` — the production-bug regression (84-122)
- `crates/mentedb/tests/scenarios.rs`, `realistic.rs`, `process_turn.rs`
- `benchmarks/longmemeval/`

### Commands behind the absence claims

```sh
grep -rn -i "tombstone" crates --include="*.rs"
grep -rn -iE "review|approve|human" crates --include="*.rs" | grep -v tests
grep -rn -i "arxiv|bibtex|@article|citation|doi" README.md ARCHITECTURE.md VISION.md docs/
ls CITATION.cff
```

## History

**2026-09-13** — [`4ba993dcf52f0a17065a9a2484fe59777dcd45d4`](https://github.com/nambok/mentedb/commit/4ba993dcf52f0a17065a9a2484fe59777dcd45d4) — first reading. Screened first: two cargo `build.rs` build-time execution points and a benchmark requirements file pinning nothing, so nothing was installed and `cargo test` was not run. Three marks. `bitemporal` is earned on two queryable fields rather than two columns — `Created` and `ValidAt` are both members of the planner's `Field` enum — which is the distinction that cost another system in this corpus the same mark on the same day. `audit_log` is withheld on a deliberate reading: the write-ahead log is append-only and records mutations, and its entries are physical pages with no actor, action or reason, so it answers what must be replayed rather than what changed and why. `scope_enforced` is earned on the typed reads that take the ids as mandatory parameters, with the bound recorded that the primary `recall` takes only a query string.

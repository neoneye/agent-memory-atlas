---
title: "Brain"
eyebrow: "Memory database"
description: "A Rust memory database whose statements carry four independent timestamps across two axes, whose every secondary index is prefixed with namespace and space so a range scan cannot physically reach another tenant, and whose default read drops superseded and tombstoned rows while an as-of query deliberately overrides that."
root: ../..
page_kind: system
source_name: "arc-labs-ai/brain-db"
source_url: https://github.com/arc-labs-ai/brain-db
archive_name: "arc-labs-ai--brain-db"
revision: 32a77b853f8f5a8245add13615b4484bba9e956a
revision_url: https://github.com/arc-labs-ai/brain-db/commit/32a77b853f8f5a8245add13615b4484bba9e956a
analyzed_at: 2026-09-19
capabilities: "trust_state, bitemporal, scope_enforced, audit_log, negative_eval"
stack_storage: "kv, files"
stack_retrieval: "vector, lexical, graph"
stack_source: "reviewed"
capability_evidence:
  trust_state: "supersession and tombstoning as stored record-axis state, dropped by default in a filter chain that keeps the confidence float as a separate step | crates/brain-core/src/nodes/statement.rs:391-442, :301-313, crates/brain-planner/src/retrieval/filters/logic.rs:1-28, :42-78, crates/brain-metadata/src/statement/tombstone.rs:45, crates/brain-metadata/src/statement/supersede.rs:39 | a statement carries a version, a supersedes and superseded-by pointer, a chain root, a tombstoned flag with a typed reason, and a record-invalidation timestamp whose own doc says it means the substrate stopped believing the claim — superseded, tombstoned, or invalidated by a forget cascade — with None meaning the substrate still believes it. The post-fusion filter chain runs six steps in a binding order, and the two that matter here default to dropping: tombstoned rows are removed unless the caller opts in, and superseded statements and relations are removed unless the caller opts in. Confidence is a separate earlier step with its own threshold, so the number ranks and the state filters rather than the two being one value. The tombstone reason distinguishes a hard-delete intent from the soft reasons, because the reclamation worker may only take rows the caller asked to remove — superseded rows and soft tombstones are kept for audit | the vocabulary is about belief in a claim rather than about its subject's own lifecycle, and there is no state for disputed or pending review; a pending entity resolution is instead a subject variant that query paths skip"
  bitemporal: "four timestamps on two independent axes, with a worked divergence example in the type's own header and both axes applied in one filter chain | crates/brain-core/src/nodes/statement.rs:10-30, :404-436, crates/brain-planner/src/retrieval/filters/logic.rs:9-28, :62-78, :473, :535-546, :632-633 | object time is valid-from and valid-to — when the fact became and stopped being true in reality — and record time is extracted-at and record-invalidated-at, when the substrate first ingested the claim and when it stopped believing it. The header works the divergence through: in May we learn Alice changed jobs in February, so valid-to is February and record-invalidated-at is May, and a query asking what we believed on April 1 returns the superseded statement while a query asking what was true on April 1 does not. Both axes reach the read. The filter chain's temporal step tests event-at and the valid-from-to-valid-to window, and a separate as-of step tests extracted-at against the requested instant and record-invalidated-at as null or later. The interaction between as-of and the tombstone filter is reasoned out rather than left to fall out: a row tombstoned today but alive at the requested instant passes the as-of step, because the tombstone filter runs against current state and the historical answer must win when the caller asked for it | memory, entity and relation rows carry no record-axis timestamps yet and pass the as-of step unfiltered, which the module states inline"
  scope_enforced: "the scope is the leading bytes of every secondary index key rather than a predicate, and the id derivation folds the namespace so the same space string in two namespaces cannot collide | crates/brain-metadata/src/tables/statement.rs:33-35, :42, :59, crates/brain-core/src/ids.rs:40-88 | the statement tables carry a leading namespace-and-space prefix on every secondary index, stated as the reason: a range scan for one namespace and space can physically never traverse another tenant's rows. That is a different guarantee from a filter — there is no query shape that reads the wrong rows and then discards them, because the iterator never arrives at them. Underneath, the storage space id is derived as a UUIDv5 of the space string under a UUIDv5 of the namespace under a frozen root, so isolation holds at the id level as well as at the key prefix, and the derivation is pinned by a golden test because changing it would re-key every space in every deployment | the anonymous space is an all-zero sentinel and it is the type's Default, used by server-side workers acting without a per-request caller — so a forgotten space resolves to a shared bucket rather than raising, the opposite default from a fail-closed design"
  audit_log: "append-only, time-ordered audit tables keyed by UUIDv7 with an input hash and the outputs produced, plus a merge log detailed enough to replay a merge backwards | crates/brain-metadata/src/tables/audit.rs:1-45, crates/brain-metadata/src/tables/merge.rs:1-25, crates/brain-metadata/src/tables/extractor_audit.rs | the module opens by stating the contract: audit entries are append-only and time-ordered by their UUIDv7 key, and the row carries versions, timestamps, outputs, cost and an input hash, indexed three ways — by memory, by extractor and by time. The status byte vocabulary is declared stable and never reassigned, and its discriminants match the extractor crate's own enum byte for byte so the two crates cannot drift. Two tables sit under this header, one for extraction and one for entity resolution, and a third table beside them logs entity merges with everything an unmerge needs to replay the diff in reverse — aliases contributed, attribute conflicts, the mention-count delta — with overflow rows for merges that re-routed more ids than fit inline | these record what the extraction and resolution machinery did rather than every write; a direct statement create or retract is durable through the write-ahead log and its sequence number rather than through these tables"
  negative_eval: "a four-case truth table on the record axis, each exclusion paired with its inclusion, plus an end-to-end supersession case through the real filter chain | crates/brain-planner/src/retrieval/filters/tests.rs:663-692, :693-760, :399-465 | the as-of cases assert all four outcomes and name the reasoning in each comment: a live statement is included at and after its extraction, one invalidated before the requested instant is excluded, one invalidated after it is included because the substrate still believed it then, and one extracted after it is excluded because it did not exist yet. The end-to-end case seeds a statement, supersedes it, then asks what was believed before the supersession and asserts the prior comes back even though it is now historical — which is the assertion a test of a forward-only filter cannot make. Beside them the tombstone cases drop a tombstoned statement and an inactive memory, with a companion asserting a clean relation passes both the tombstone and supersession steps so the filters are shown to be selective rather than uniformly rejecting | 2,729 test functions across the workspace, plus three protocol fuzz targets and fault-injection suites for bit flips, IO faults and random kills"
matrix:
  memory_unit: "Four record types — Memory, Entity, Statement and Relation. A statement carries a subject that may be an entity, the source memory itself or a pending resolution audit, a predicate, an object, a confidence, an evidence reference, the extractor that produced it, four timestamps, a supersession chain and a tombstone reason"
  storage: "An embedded key-value store for metadata with rkyv-archived rows, a write-ahead log with sequence numbers and fsync, an arena for content, and an HNSW index for vectors"
  retrieval: "Semantic, lexical and entity-graph arms fused by reciprocal rank, then a six-step filter chain in a binding order, then rerank; EXPLAIN reports per-step survivor counts"
  write: "A binary wire protocol with CBOR payloads and one opcode per cognitive operation, planned into an execution plan with a cost estimate and an idempotency check before the write-ahead log append"
  update_delete: "Correction supersedes and stamps the record-invalidation timestamp; forget has a soft mode that tombstones and a hard mode that zeroes the vector and the text; the reclamation worker takes only rows whose tombstone reason says the caller asked for removal"
  scoping: "A namespace resolved from the credential and a space passed per request, both folded into the storage id and both forming the leading bytes of every secondary index key"
  integration: "No client ships — any language speaks the documented binary wire protocol; a server binary, an admin port, a plugin surface and a 148-file normative specification"
  background: "Consolidation, decay, reclamation and resolution workers, plus checkpointing and recovery from the write-ahead log"
  trust: "A confidence float that ranks and a record-time invalidation that filters, kept as separate fields and separate filter steps; a statement is believed exactly when its record-invalidation timestamp is unset"
  strengths: "A scope that lives in the key rather than in a predicate; a four-timestamp model whose header works a late-arriving correction through both axes; and a filter chain whose step order is declared binding and whose as-of versus tombstone interaction is decided explicitly rather than emerging"
  risks: "The anonymous space is the type's default, so a forgotten space lands in a shared bucket instead of raising; memory, entity and relation rows carry no record-axis timestamps so an as-of query passes them through unfiltered; and this is a v0.1.0 pre-release whose specification is ahead of the tree in places"
---

## 1. Executive Summary

Brain is a memory database rather than a memory library: a Rust server, a
binary wire protocol, no shipped client, and a 148-file normative
specification. Four record types — Memory, Entity, Statement, Relation — with
provenance, confidence and bi-temporal validity, and retrieval that fuses
semantic, lexical and entity-graph arms before a filter chain whose step order
is declared binding.

Five marks, and three of them are unusually cleanly implemented.

**The scope is in the key.** Every secondary index over statements carries a
leading namespace-and-space prefix, and the comment states the guarantee in the
form that matters: a range scan for one namespace and space *"can physically
never traverse another tenant's rows."* That is not a predicate applied after a
read — there is no read that reaches the wrong rows at all.

**Four timestamps on two axes, and the header works the divergence through.**
Object time says when a fact became and stopped being true; record time says
when the substrate ingested and stopped believing the claim. The example is
worked out in the type's own documentation: learn in May that Alice changed
jobs in February, and *"a query 'what did I believe on April 1?' returns the
superseded statement… a query 'what was true on April 1?' does not."*

**Belief is a state, and it is separate from the number.** Confidence is a
float with its own filter step; supersession and tombstoning are stored
record-axis state with their own steps, and both default to dropping. The
system can say *I have this on record and do not believe it*, which is the
thing the mark exists to test.

The part worth studying even if you build nothing like this is the step where
the two interact. A row tombstoned today but alive at the instant an as-of
query names passes the as-of step anyway, because *"the tombstone filter runs
against current state, while the as-of filter runs against historical state,
and the historical answer must win when the caller asked for it."*

## 2. Mental Model

A memory is what arrived. Statements are what was extracted from it, and they
are where every mechanism lives.

A statement is a subject, a predicate and an object, plus four things most
stores keep implicit: who extracted it, what evidence it rests on, how
confident that extractor was, and when — on both clocks. Corrections do not
edit; they mint a new statement, point it at its predecessor, close the
predecessor's record axis and keep both in a chain with a shared root.

Forgetting is two operations, not one. A soft forget tombstones and keeps the
row for audit; a hard forget stamps a distinct reason so the reclamation worker
knows it may physically reclaim this row and not the soft ones.

Isolation is not a filter. A namespace comes from the credential and a space
comes per request, and both are folded into ids and into index keys before any
query exists.

## 3. Architecture

```mermaid
%% caption: a binary wire protocol carries one opcode per cognitive operation into a planner that estimates cost, checks idempotency and appends to a write-ahead log before applying; extraction produces statements carrying provenance, confidence and four timestamps on two axes, with every extraction and resolution appended to time-ordered audit tables; recall fuses semantic, lexical and entity-graph arms by reciprocal rank and then runs a six-step filter chain in a binding order — type, temporal on the object axis, confidence, tombstone, supersession, and an as-of step on the record axis that deliberately overrides the tombstone step when a caller asks what was believed at a past instant
flowchart TD
    WIRE["binary wire protocol<br/>CBOR, one opcode per operation"] --> PLAN["planner<br/>cost estimate · idempotency check"]
    PLAN --> WAL[("write-ahead log<br/>LSN · fsync")]
    WAL --> APPLY["apply"]

    APPLY --> EXTRACT["extractors"]
    EXTRACT --> STMT[("statement<br/>subject · predicate · object<br/>confidence · evidence · extractor<br/>valid_from/valid_to · event_at<br/>extracted_at/record_invalidated_at<br/>chain_root · supersedes · superseded_by<br/>tombstoned + reason")]
    EXTRACT --> AUD[("extractor_audit + entity_resolution_audit<br/>append-only, UUIDv7-ordered<br/>input hash · outputs · cost<br/>indexed by memory, extractor, time")]
    MERGE["entity merge"] --> ML[("merge_log<br/>replayable in reverse")]

    STMT --> IDX[("secondary indexes<br/>LEADING (namespace_id, space_id)<br/>a scan cannot reach another tenant")]

    Q["RECALL"] --> ARMS["semantic + lexical + entity-graph"]
    IDX --> ARMS
    ARMS --> RRF["reciprocal-rank fusion"]
    RRF --> F1["1 type"]
    F1 --> F2["2 temporal — object axis<br/>event_at, valid_from..valid_to"]
    F2 --> F3["3 confidence ≥ threshold"]
    F3 --> F4["4 tombstone — dropped unless opted in"]
    F4 --> F5["5 supersession — dropped unless opted in"]
    F5 --> F6{"6 as-of — record axis<br/>extracted_at ≤ t AND<br/>(record_invalidated_at IS NULL OR > t)"}
    F6 -->|"alive at t, tombstoned today"| KEEP["kept — the historical answer wins"]
    F6 --> LIM["limit"]
    KEEP --> LIM
    LIM --> OUT["ranked results + EXPLAIN survivor counts"]
```

## 4. Essential Implementation Paths

- **Record types:** `crates/brain-core/src/nodes/statement.rs`, `entity.rs`,
  `relation.rs`, `memory.rs`.
- **Ids and scope derivation:** `crates/brain-core/src/ids.rs`.
- **Tables and index prefixes:** `crates/brain-metadata/src/tables/`.
- **Supersession, tombstoning, cascade:**
  `crates/brain-metadata/src/statement/`, `cascade.rs`.
- **Filter chain:** `crates/brain-planner/src/retrieval/filters/logic.rs`.
- **Forget planning:** `crates/brain-planner/src/planner/forget.rs`.
- **Write-ahead log and recovery:** `crates/brain-storage/src/wal/`,
  `recovery.rs`.
- **Specification:** `spec/`, notably `02_data_model`, `03_schema` and
  `20_tenancy`.

## 5. Memory Data Model

The statement is the record worth reading in full. Beyond the four timestamps
it carries a version, a `supersedes` and `superseded_by` pair, a `chain_root`
that is self-referential until the statement is superseded, a tombstone flag
with a typed reason, and an `is_stateful` flag copied from the predicate
definition at write time.

Two smaller decisions are worth lifting.

`SubjectRef` has three variants, and the third is the interesting one: a
subject can be a resolved entity, the source memory itself — for statements
about a memory rather than about a thing, such as when an event occurred — or
`Pending`, holding an audit id when the resolver returned ambiguous. The
comment notes that query paths excluding pending subjects skip those, so an
unresolved reference is a distinguishable state rather than a guess.

`TombstoneReason` separates `Retract` from the four soft reasons for a stated
operational purpose: the reclamation worker selects only rows the caller asked
to remove, while soft tombstones and superseded rows *"are kept for audit."*
The retract handler stamps that reason regardless of what the caller put in the
audit byte, which is the small correct detail — the physical consequence is not
left to a field the caller controls.

## 6. Retrieval Mechanics

Three arms fuse by reciprocal rank, then six filters run in an order the module
calls binding, then a limit. EXPLAIN reports survivor counts per step, which
makes the chain debuggable in the way a single opaque WHERE clause is not.

The order is the design. Type first, then the object-time window, then
confidence, then tombstone, then supersession, then as-of — and the last one is
documented as the exception to the fourth, because history and current state
are different questions and a caller who asked the historical one should get
the historical answer.

## 7. Write Mechanics

Every operation is planned before it is executed: a cost estimate checked
against a budget, an idempotency check on the request id, a write-ahead log
append with fsync, then apply. A forget plan carries explicit booleans for what
it will do — tombstone the arena slot, commit metadata, mark the HNSW entry
removed, and for a hard forget zero the vector and the text.

Corrections supersede. The supersede path stamps `record_invalidated_at` on the
predecessor, and the tombstone path stamps it too, so a single predicate —
that timestamp being unset — answers *is this the current belief* regardless of
which route retired the old one.

## 8. Agent Integration

None, deliberately. Brain ships no client; the README says any language speaks
the binary wire protocol directly, and the protocol section documents per-opcode
field schemas. There is an admin port, a plugin surface with connectors and
enrichers, and a Docker image.

## 9. Reliability, Safety, and Trust

**Trust state — awarded.** Confidence and belief are separate fields, separate
filter steps, and separate questions.

**Bi-temporal — awarded**, on the fullest form in this reading: four
timestamps, both axes reaching the read, and the interaction between the
historical and current-state filters decided explicitly. The stated limit is
that only statements carry the record axis today.

**Scope enforced — awarded**, on the key prefix rather than a predicate, plus
an id derivation that folds the namespace so the same space string under two
namespaces cannot collide. The caveat is the default: the anonymous space is an
all-zero sentinel and it is the type's `Default`, used by server-side workers
that act without a caller. That is a reasonable choice for a worker and a
hazard for a forgotten request path, since the failure is a shared bucket
rather than an error.

**Audit log — awarded.** Append-only, time-ordered by construction, with an
input hash and the produced outputs, indexed three ways — and a merge log
carrying enough to run an unmerge backwards.

**Negative eval — awarded**, on the four-case record-axis table and the
end-to-end supersession case.

**Tombstone — withheld.** The word is here and the mechanism is careful, but
the key is the row: `tombstoned`, `tombstoned_at` and `tombstone_reason` sit on
a statement, and nothing is keyed on the value a caller asked to forget. Encode
does de-duplicate — the planner asserts text encode dedup is always on — but
that is a near-duplicate check against live content, not a consult against a
record of what was rejected. Re-encoding the same sentence after a hard forget
produces a new memory.

**Human review — withheld.** No approval surface exists; EXPLAIN and the admin
port are read-only diagnostics. The nearest thing is the pending-resolution
audit, which records that the resolver could not decide — a place a reviewer
could stand, with no reviewer standing there.

## 10. Tests, Evals, and Benchmarks

**No paper** and no `CITATION.cff`. The specification cites Zep and Graphiti's
bi-temporal model as the thing being applied to a typed graph, which is an
honest attribution rather than a claim of novelty.

2,729 test functions across fifteen crates, three protocol fuzz targets, and
fault-injection suites named for what they inject — bit flips, IO faults,
random kills, recovery chaos, concurrent edges. A database that tests its
recovery path by killing itself at random points is treating durability as
something to be measured rather than asserted.

`spec/19_benchmarks` exists and the README shows a p99 recall figure in its
terminal banner. No benchmark result is committed to the tree, so that number
is a screenshot rather than a measurement a reader can reproduce.

The status badge says pre-release v0.1.0, and the tenancy specification marks
several decisions as still open. Reading the spec as a description of the code
would overstate what is built — the `SpaceId` type, for instance, appears in
the metadata index prefixes and the executor context but not yet in the
write-ahead log payloads.

## 11. For Your Own Build

- **Put the scope in the key.** A leading `(namespace, space)` prefix makes
  cross-tenant traversal impossible rather than merely filtered, and it removes
  the question of whether every query remembered its predicate.
- **Derive the partition id from the namespace as well as the space**, so two
  tenants cannot collide on the same user-supplied string — and pin the
  derivation with a golden test, because changing it re-keys everyone.
- **Keep belief and confidence as separate fields.** A threshold cannot express
  *on record but not believed*, and a state cannot express *probably*.
- **Decide what an as-of query does with rows deleted since.** Brain's answer —
  the historical filter overrides the current-state one when the caller asked
  for history — is one defensible choice; having no answer is not.
- **Give the hard delete its own reason code.** The reclamation worker can then
  select exactly what a caller asked to remove, and soft tombstones survive for
  audit without a second flag.
- **Name what a fault-injection suite injects.** Bit flips, IO faults and
  random kills are three different failure classes, and a suite per class
  reports which one broke.

## 12. Open Questions

- Only statements carry record-axis timestamps, so an as-of query passes
  memories, entities and relations through unfiltered. Is extending the axis to
  those planned, and what does an as-of answer mean today when a statement's
  subject entity has been merged since?
- The anonymous space is the `Default` for `SpaceId`. Would a distinct
  `Worker` sentinel, with the plain default made unconstructable, keep the
  worker convenience without the forgotten-request hazard?
- The specification is 148 files and the tree is v0.1.0. Which sections are
  descriptions of the code and which are the plan — is there a marker, or is
  reading both the only way to tell?

## Appendix: File Index

- Record types: `crates/brain-core/src/nodes/statement.rs`,
  `nodes/entity.rs`, `nodes/relation.rs`, `nodes/memory.rs`,
  `nodes/kinds.rs`
- Ids and scope derivation: `crates/brain-core/src/ids.rs`
- Tables and index prefixes: `crates/brain-metadata/src/tables/statement.rs`,
  `tables/audit.rs`, `tables/extractor_audit.rs`, `tables/merge.rs`
- Supersession and tombstoning:
  `crates/brain-metadata/src/statement/supersede.rs`,
  `statement/tombstone.rs`, `crates/brain-metadata/src/cascade.rs`
- Filter chain: `crates/brain-planner/src/retrieval/filters/logic.rs` and
  `filters/tests.rs`
- Forget: `crates/brain-planner/src/planner/forget.rs`,
  `crates/brain-planner/src/plan/forget.rs`
- Durability: `crates/brain-storage/src/wal/`,
  `crates/brain-storage/src/recovery.rs`, and the fault suites under
  `crates/brain-storage/tests/`
- Specification: `spec/02_data_model`, `spec/03_schema`, `spec/20_tenancy`

## History

**2026-09-19** — [`32a77b853f8f5a8245add13615b4484bba9e956a`](https://github.com/arc-labs-ai/brain-db/commit/32a77b853f8f5a8245add13615b4484bba9e956a) — first reading, at the head of `main`, status pre-release v0.1.0. Screened with `scripts/screen_repo.py` before anything was read: one auto-run surface in a devcontainer configuration, no build-time execution path, no floating dependency surface, no instruction file addressed to a reading agent, and both `Cargo.lock` files unchanged for forty-seven days. Nothing was installed, built or run. Apache-2.0. Five marks. The reading covered the four record types and the statement's four timestamps, the supersession and tombstone paths and their shared record-invalidation stamp, the forget planner's soft and hard modes, the audit and merge tables, the index key prefixes and the space-id derivation, the six-step filter chain and its as-of step, and the filter test suite; the embedding, indexing, planner-cost, HTTP and plugin crates were read as context rather than as subject, and 242,000 lines across 677 files means this reading is of the memory model rather than of the whole tree. Two marks are withheld with reasons in section 9. The one worth repeating is `tombstone`: the word is used here for a row flag, and nothing is keyed on the value a caller asked to forget, so re-encoding the same sentence after a hard forget produces a new memory. The specification is 148 files against a v0.1.0 tree, so claims read there were checked against code before being repeated.

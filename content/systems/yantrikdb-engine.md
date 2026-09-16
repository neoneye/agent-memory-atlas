---
title: "YantrikDB Engine"
eyebrow: "The limits are in the doc comment, above the code that has them"
description: "The embeddable Rust engine the atlas had only read through its server and its Hermes plugin: decay, consolidation and contradiction detection over SQLite, with an as-of recall that reconstructs what the database believed at a past instant — and a module header listing the three things that reconstruction cannot do."
root: ../..
page_kind: system
source_name: "yantrikos/yantrikdb"
source_url: https://github.com/yantrikos/yantrikdb
archive_name: "yantrikos--yantrikdb"
revision: b189e799bd854285471ec6149ff0f298cc594ec8
revision_url: https://github.com/yantrikos/yantrikdb/commit/b189e799bd854285471ec6149ff0f298cc594ec8
analyzed_at: 2026-09-16
capabilities: "trust_state, bitemporal, audit_log, negative_eval"
capability_evidence:
  trust_state: "two stored discrete statuses on every memory, both applied as read predicates and both typed beside the encrypted metadata so recall can decide without decrypting | crates/yantrikdb-core/src/base/schema.rs:49-50, :121-134, crates/yantrikdb-core/src/engine/audit.rs:27-28, :87-88, :113-114, :136-137, :146-147 | `consolidation_status` is `active | consolidated | tombstoned` and `synthesis_state` is constrained by a CHECK to `verified | invalidated | unverified | superseded`; the synthesis columns are declared to \"remain typed beside encrypted metadata so recall can fail closed without decrypting or joining the evidence graph on its hot path\", and every audit query pairs `synthesis_state = 'verified'` with `consolidation_status = 'active'`. Producers are `tombstone_with_rid` and `tombstone_inner` in `engine/lifecycle.rs:627-700` and the synthesis lifecycle | crates/yantrikdb-core/src/engine/thread.rs:1609-1651"
  bitemporal: "both axes: a first-class event-time range distinct from the transaction-time `created_at`, and `recall_as_of(query, t)` reconstructing what the database believed at `t` | crates/yantrikdb-core/src/base/schema.rs:143-152, :180-184, crates/yantrikdb-core/src/engine/bitemporal.rs:1-36 | the schema names the split outright — \"`created_at` is transaction time (when the row was written); these are event time (when the described events happened)\" — with `event_time_min` / `event_time_max` and a partial index for \"recall-time valid-time range scans\". `recall_as_of` excludes records that did not exist at `t`, excludes records superseded at `t` \"but only by edges that already existed at `t` (`record_links.created_at <= t`); a later supersession does not rewrite what was believed then\", and rolls a corrected record back by walking `record_revisions` for the earliest revision applied after `t`, whose `prior_*` columns \"ARE the state at `t`\" | crates/yantrikdb-core/src/engine/bitemporal.rs"
  audit_log: "an append-only oplog written inside the same transaction as the mutation, from twelve engine modules, with the only payload rewrite an encryption-sealing migration that preserves content | crates/yantrikdb-core/src/engine/stats.rs:341-520, crates/yantrikdb-core/src/base/schema.rs:813-848, crates/yantrikdb-core/src/engine/mod.rs:2495-2530 | `log_op_in_tx` and `log_op_at_hlc_in_tx` write the `oplog` row inside the caller's transaction, so the op and the mutation commit together; callers include `record.rs` (remember), `lifecycle.rs` (tombstone and correct), `links.rs` (relate and supersede), `conflict.rs`, `graph_ops.rs`, `graph_state.rs`, `procedural.rs`, `cognition.rs`, `reembed.rs`, `materializer.rs` and `idempotency.rs`. The table is indexed by timestamp, target rid, HLC and origin actor. Outside tests the only `UPDATE oplog` statements are a one-way `applied = 1 ... AND applied = 0` delivery flag and `migrate_oplog_payload_encryption`, which seals pre-0.13.2 plaintext payloads into ciphertext and then vacuums because \"THE SEAL IS NOT THE ERASURE\"; no `DELETE FROM oplog` exists in the tree | crates/yantrikdb-core/src/engine/tests/corrections.rs"
  negative_eval: "a committed test that a forgotten row and a superseded row both leave the thread, asserting the exact surviving rid list against a positive control in the same test | crates/yantrikdb-core/src/engine/thread.rs:1605-1651 | `tombstoned_and_superseded_rows_are_excluded` seeds three rows and asserts `recall_thread` returns 3 — the positive control — then calls `db.forget(\"v2\")` and asserts the total is 2 and the surviving rids are exactly `[\"v1\", \"v3\"]`, with positions renumbered; it then links `v3` Supersedes `v1` and asserts the total is 1 and the survivor is exactly `v3`. The doc comment states the standard being tested: these are \"the same predicates recall applies\". Run against a real engine over SQLite | crates/yantrikdb-core/src/engine/thread.rs"
stack_storage: "sqlite"
stack_retrieval: "vector, lexical, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A memory row keyed by UUIDv7 with a type of episodic, semantic, procedural or emotional, an embedding, decay parameters, a namespace, certainty, domain, source, an event-time range, and typed write-resolution provenance"
  storage: "One SQLite database per store, with HNSW vectors, an oplog, `record_revisions`, `record_links`, idempotency claims, and a cognition layer of propositions, variables, state assertions and rule edges"
  retrieval: "Hybrid vector and lexical recall with decay-weighted scoring, graph expansion, thread reconstruction, and `recall_as_of` for point-in-time reads"
  write: "`remember` with actor-scoped idempotency keys and a confidence-basis write gate; `correct` mutates in place while archiving the prior state; `link` records supersession as an edge"
  update_delete: "Correction archives `prior_text`, `prior_metadata`, `prior_importance` and `prior_valence` into `record_revisions` with an `applied_at`; supersession is an edge in `record_links`; forgetting sets `consolidation_status = 'tombstoned'` with a caller-supplied `tombstone_reason` and removes the row from the recall path"
  scoping: "A `namespace` column with a `NOT NULL DEFAULT 'default'`, appended as `AND m.namespace = ?` on recall — but the engine's own signature is `namespace: Option<&str>`, so a caller that passes `None` gets no predicate"
  integration: "An embeddable Rust library with Python, WASM and TUI crates; wrapped by yantrikdb-server for HTTP and HA, and embedded in process by the YantrikDB Hermes plugin"
  background: "Decay sweeps over stored half-lives, autonomous consolidation into semantic memories, contradiction detection, a reembed pipeline with staging columns and generation stamps, and a materializer draining the oplog"
  trust: "Consolidation and synthesis statuses as read predicates, a confidence-basis justification tier in a write-gate consistency matrix, actor-scoped idempotency claims, an append-only oplog, HLC ordering, and encryption at rest with a documented erasure step"
  strengths: "The bitemporal module states its own limits in its header rather than leaving them to be discovered: ranking is present-day, forgotten records stay forgotten, and the as-of pool runs with `skip_reinforce` because \"archaeology must not masquerade as usage\". A superseding edge only hides a record from an as-of read if the edge already existed at that instant. The audit op is written inside the caller's transaction rather than beside it. The reembed path stages new vectors in separate columns with a generation stamp because in-place mutation \"would dim-mismatch concurrent recalls\". An index comment carries a signed honesty note that the index does not satisfy its query's ORDER BY and that SQLite may sort the full eligible set"
  risks: "Scope is offered rather than enforced: `recall` takes `namespace: Option<&str>` and emits the predicate only when a namespace is supplied, so the boundary is the wrapper's to keep, not the engine's — which is why the mark sits on the Hermes plugin and not here. The v26 write-resolution columns — `resolution_kind`, `dismissal_reason`, `prior_rid`, `confidence_at_write` — record the epistemic operation chosen at write time and no read path consults them to refuse a re-assertion; the schema comment frames them as a foundation for a future API. `synthesis_granularity` and `synthesis_state` carry CHECK constraints while `consolidation_status`, `type`, `storage_tier` and `resolution_kind` do not, so those four accept any string. The schema is `CREATE TABLE IF NOT EXISTS` with no migration constants, so a column added to the constant reaches an existing database only through the separate `ensureColumn`-style paths"
---

## 1. Executive Summary

This is the engine. The atlas has read it twice before through something else —
once as the crate that [yantrikdb-server](../yantrikdb/) wraps, once as the
in-process library the [Hermes plugin](../yantrikdb-hermes-plugin/) embeds —
and both times only as far as the wrapper's claims required. Read directly it
is 198,235 lines of Rust across five crates, Apache-2.0, at version 0.23.0,
with 2,274 test functions.

Its pitch is specific and correct about the problem: "Bolting a vector store
onto it doesn't fix that: nothing is ever forgotten, near-duplicate memories
pile up, and two contradictory facts come back ranked side by side with no
signal that they disagree."

What distinguishes it from every other large memory engine in this corpus is
not decay or consolidation — several have those. It is that the code states
what it cannot do, in the place where someone would otherwise assume it could.

`engine/bitemporal.rs` implements `recall_as_of(query, t)` — "what did this
database believe at time `t`?" — and then, under a heading reading **HONEST
LIMITS, documented rather than hidden**, lists three:

- "**Ranking is present-day.** Similarity is computed against today's vectors
  … `recall_as_of` reconstructs CONTENT and CURRENCY at `t`, not the exact
  ranking a query would have produced at `t`."
- "**Forgotten records stay forgotten.** A tombstoned record is physically out
  of the recall path … an as-of query cannot resurface something forgotten
  since `t`."
- "**Access stats are untouched.** The pool query runs with `skip_reinforce` —
  archaeology must not masquerade as usage."

That third one is a design decision most systems would not have noticed they
were making. Reading history should not look like using memory, because usage
feeds decay and decay decides what survives.

The same habit recurs. An index definition carries a note that the index does
**not** satisfy its query's `ORDER BY`, that the query's shape "defeats
index-served ordering anyway", and that "SQLite therefore MAY SORT THE FULL
ELIGIBLE SET" — attributed as a reviewer finding, with the resolution named.
The encryption migration warns that "THE SEAL IS NOT THE ERASURE" and vacuums
the freed pages.

The finding is about a boundary that is not the engine's to hold.

`recall` takes `namespace: Option<&str>`, and the `AND m.namespace = ?`
predicate appears only in the branches where a namespace was supplied. Pass
`None` and the query spans every namespace in the store. That is a defensible
library API — an embeddable engine should not force a tenancy model — but it
means the isolation the Hermes plugin is credited with is the plugin's
discipline, not a property of the store beneath it. Anything else embedding
this crate inherits the option, not the guarantee.

## 2. Mental Model

A **memory** is a row: text, embedding, and a set of stored decay parameters —
importance, half-life, last access, access count, valence — that are
"stored, not continuously updated", so decay is computed at read time rather
than swept.

A **correction** mutates in place and archives the prior text, metadata,
importance and valence into `record_revisions` with an `applied_at`.

A **supersession** is an edge in `record_links`, with its own `created_at`.

Those two ledgers are what make time travel possible without a second storage
model — the module says so explicitly: "Those two ledgers are enough to answer
an as-of query WITHOUT a new storage model."

An **op** is a row in the oplog, written inside the transaction that made the
change.

```mermaid
%% caption: correction archives the prior state and supersession is a dated edge, so an as-of read can reconstruct what was believed at t — while the namespace predicate appears only when the caller supplies one
flowchart TB
    W["remember —<br/>actor-scoped idempotency key,<br/>confidence_basis write gate"] --> M[("memories<br/>consolidation_status:<br/>active | consolidated | tombstoned<br/>synthesis_state CHECK:<br/>verified | invalidated |<br/>unverified | superseded")]
    C["correct"] -->|"mutates in place"| M
    C -->|"archives prior_text, prior_metadata,<br/>prior_importance, prior_valence"| REV[("record_revisions<br/>+ applied_at")]
    L["link Supersedes"] --> LNK[("record_links<br/>+ created_at")]
    F["forget"] --> TS["consolidation_status = 'tombstoned'<br/>+ tombstone_reason"]
    TS --> M
    W & C & L & F --> OP[("oplog — written by log_op_in_tx<br/>INSIDE the caller's transaction")]
    M --> R{"recall(query, namespace: Option)"}
    R -->|"Some(ns)"| PRED["AND m.namespace = ?"]
    R -->|"None"| ALL["no predicate —<br/>every namespace in the store"]
    M --> AO["recall_as_of(query, t)"]
    REV --> AO
    LNK --> AO
    AO --> RULES["1. created_at > t → excluded<br/>2. superseded → excluded ONLY by edges<br/>with record_links.created_at <= t<br/>3. corrected after t → rolled back via<br/>the earliest revision applied after t"]
    RULES --> LIMITS["HONEST LIMITS, in the header:<br/>ranking is present-day ·<br/>forgotten stays forgotten ·<br/>skip_reinforce, because<br/>'archaeology must not<br/>masquerade as usage'"]
    ET["event_time_min / event_time_max —<br/>event time, distinct from created_at<br/>as transaction time"] --> M
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `crates/yantrikdb-core/src/base/schema.rs` | The whole schema as one SQL constant, heavily commented per version |
| `crates/yantrikdb-core/src/engine/bitemporal.rs` | `recall_as_of`, and its limits |
| `crates/yantrikdb-core/src/engine/recall.rs` | 6,768 lines of hybrid retrieval and the namespace branches |
| `crates/yantrikdb-core/src/engine/lifecycle.rs` | Decay, tombstoning, correction |
| `crates/yantrikdb-core/src/engine/stats.rs` | The oplog writers |
| `crates/yantrikdb-core/src/engine/thread.rs` | Conversation-thread reconstruction and its visibility test |
| `crates/yantrikdb-core/src/engine/audit.rs` | Synthesis-evidence integrity queries |
| `crates/yantrikdb-core/src/cognition/` | 156,204 lines: belief, contradiction, calibration, coherence, consolidation, counterfactual, metacognition |
| `crates/yantrikdb-python`, `-wasm`, `-tui`, `-ml` | The bindings the wrappers use |

## 4. Essential Implementation Paths

`engine/bitemporal.rs:1-36`. Read the header before the code; it is the best
thirty lines in the repository and it explains the design of everything under
it.

`base/schema.rs:31-170` for the memory row, which is a version-by-version
record of what the project learned — v25 replication determinism, v26 write
resolution, v27 and v28 reembed staging and generation stamps, v37 the
anti-laundering write gate, v42 synthesis lifecycle, v48 valid time, v50
source turn.

`engine/thread.rs:1605-1651` for the visibility test, which is the clearest
statement of what recall considers eligible.

## 5. Memory Data Model

The `memories` table is the accumulated design. Beyond the obvious columns it
carries `certainty`, `domain`, `source`, `emotional_state`, a `session_id`,
`due_at` and `temporal_kind` for prospective queries, `storage_tier`,
`consolidated_into`, and — as of v37 — `confidence_basis`, "the typed
justification tier (observation|asserted|confirmation|verification|inference|
assumption|learned(model-vX))" that "participates in the write-gate consistency
matrix", alongside an `idempotency_key` scoped by `origin_actor` so "two
writers can't collide".

Two columns encode time in the way the atlas asks for. `created_at` is named
in the comment as transaction time; `event_time_min` and `event_time_max` are
"valid time, first-class", mirrored from metadata by "every writer that
persists the metadata column (the `event_time_bounds` helper in
`base::datetext` is the single source)". Designating a single source for a
mirrored column is the detail that keeps a denormalised field honest, and it
is stated in the schema where a future writer will read it. Both are NULL on
encrypted stores, "so nothing is extractable at rest" — the limitation is
named rather than left as a surprise.

The CHECK constraints are uneven. `synthesis_granularity` and `synthesis_state`
are constrained to their vocabularies; `consolidation_status`, `type`,
`storage_tier` and `resolution_kind` are documented in comments and accept any
string. Given that `consolidation_status` is a read predicate in every audit
query, that asymmetry is worth noticing — the newer columns got the constraint
and the older load-bearing one did not.

## 6. Retrieval Mechanics

Hybrid retrieval with decay applied at read time from the stored half-life and
last access, graph expansion, and thread reconstruction.

The namespace predicate is the report's finding and deserves stating exactly.
`recall.rs` branches: where a namespace is supplied it appends
`AND m.namespace = ?N`; where one is not, the same query runs without it. The
column is `NOT NULL DEFAULT 'default'`, so every row has a namespace and no row
is invisible — but a caller passing `None` reads across all of them.

That is the right API for an embeddable engine and the wrong assumption for
anyone who reads the server's or the plugin's isolation guarantee and concludes
the store enforces it. It does not; those wrappers do, by never passing `None`.
The atlas's `scope_enforced` mark stays where the enforcement is.

`recall_as_of` over-fetches a candidate pool because as-of filtering removes
rows after ranking, and runs it with `skip_reinforce`. Results keep their
present-day `current_status`, so "a hit can honestly read 'this was current at
`t`; today it is superseded', which is exactly what an audit wants to see."

## 7. Write Mechanics

`remember` passes an actor-scoped idempotency claim whose `INSERT ... ON
CONFLICT` on the primary key "is the serialization point for same-key retries",
with a `pending -> committed` state so "a losing retry" cannot "observe a
not-yet-committed rid", and with `op_id`, `route` and `generation` kept as "the
recovery evidence used to complete-or-roll-back a crashed claim (never
row-existence)." That parenthesis is a real distinction: recovering from row
existence would make a partially applied write look complete.

`correct` mutates in place and archives; `link` records supersession as a dated
edge; `forget` tombstones with a caller-supplied reason and takes the row out
of the recall path and index.

The v26 columns are the honest gap. `prior_rid`, `resolution_kind` — `append`,
`update`, `merge`, `supersede`, `dismiss` — `dismissal_reason` and
`confidence_at_write` record which epistemic operation the write chose, and
the comment says why they are columns rather than JSON: "so conflict resolution
+ paper adoption analysis are first-class queries, not JSON-blob crawls."
They are written and, at this pin, not read back by any write path. A value
dismissed with a reason can be proposed again and appended, because nothing
consults the dismissal. The schema names them "[f]oundation for issue #30
WriteResolution API", which is an accurate description of their current state
and the reason `tombstone` is not awarded here.

## 8. Agent Integration

Rust crate, Python bindings on PyPI, WASM, and a TUI. The server and the Hermes
plugin are the two consumers the atlas has already read. `packs/` and
`pack_mounts` / `trusted_publishers` tables suggest a distribution mechanism
for pre-built memory sets with publisher trust, which is unusual and was not
followed here.

## 9. Reliability, Safety, and Trust

The oplog is the strongest piece. `log_op_in_tx` and `log_op_at_hlc_in_tx`
write the op inside the caller's transaction, so there is no window in which a
mutation is committed and its record is not. Twelve engine modules call it,
covering remember, correct, tombstone, link, conflict resolution, graph
mutations, procedural writes, reembedding and materialization. It is indexed by
timestamp, target rid, HLC and origin actor, and nothing deletes from it.

That is the inverse of the pattern this corpus usually shows, where an audit
table exists and each caller must remember to write to it. Here the transaction
is the enforcement.

Encryption at rest covers the oplog payload, and the migration that seals older
plaintext rows is careful about what sealing does not accomplish — it rewrites
the file afterwards because an `UPDATE` "writes the ciphertext to a new page
and frees the old", and a freed page is not an erased one.

The HLC (`base/hlc.rs`) gives the deterministic ordering that the synthesis
lifecycle uses "to select one verified logical synthesis", which is how a
distributed store picks a winner without a clock it can trust.

## 10. Tests, Evals, and Benchmarks

2,274 test functions, and the visibility test in `thread.rs` is the model: a
positive control, a forget, an exact assertion on the surviving rid list, then
a supersession and another exact assertion. Asserting the surviving set rather
than a count is what makes it an eval — a count of 2 would pass if the wrong
row had left.

`engine/tests/corrections.rs` drives the correction and oplog paths, and
`impressions.rs` carries a test named for exactly the right property:
`rollup_omissions_are_exact_positive_and_not_served_children`.

Benchmarks live in `benchmarks/`, and the README points at a measurement paper
whose reproducible scripts and raw CSVs sit in the *server* repository. The
[server report](../yantrikdb/) covers that material and the corrections file
that withdrew four earlier benchmark conclusions; it is not restated here.

## 11. For Your Own Build

Write the limits into the header. `bitemporal.rs` is a template: implement the
feature, then list what it does not do, in the file, above the code. A reader
who skims that header cannot form the wrong expectation, and a maintainer who
later makes one of the limits false has to delete a sentence to do it.

Take `skip_reinforce`. If retrieval feeds decay, then any read that is not a
use — an audit, a history query, a migration scan — must be excluded from the
statistics, or inspecting your memory keeps it alive. Almost nothing in this
corpus separates the two.

Take the supersession rule for as-of reads: a record is hidden from time `t`
only by an edge that already existed at `t`. The naive version — filter out
everything currently superseded — is the one most implementations write, and it
silently rewrites history with today's knowledge.

Put the audit write in the transaction. `log_op_in_tx` makes it impossible to
commit a change without its record; an audit helper called after the commit
makes it merely customary.

And decide whether your scope is a property of the store or of its callers. An
`Option` is a fine answer for a library — but say so, because a wrapper's
guarantee will be read as the engine's.

## 12. Open Questions

Whether the v26 write-resolution columns are intended to gate writes eventually
or to remain analytical. The comment says "[f]oundation for issue #30", which
suggests the former; at this pin nothing reads them.

Whether `consolidation_status` will gain the CHECK constraint its newer
siblings have. It is a read predicate in every audit query and currently
accepts any string.

How `CREATE TABLE IF NOT EXISTS` with "no migration constant" reaches existing
databases for columns added to the constant. The header states the convention —
"change is a new CREATE TABLE IF NOT EXISTS, and `SCHEMA_SQL` is executed" —
but an existing table is not recreated, so column additions must arrive by some
other path that was not traced here.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `crates/yantrikdb-core/src/engine/bitemporal.rs:1-36` | How to document what a feature cannot do |
| `crates/yantrikdb-core/src/base/schema.rs:31-184` | The memory row, versioned comment by comment |
| `crates/yantrikdb-core/src/engine/recall.rs:1855-1880` | The namespace predicate, and the branch without it |
| `crates/yantrikdb-core/src/engine/stats.rs:341-520` | The audit op written inside the caller's transaction |
| `crates/yantrikdb-core/src/engine/thread.rs:1605-1651` | A visibility test that asserts the surviving set |
| `crates/yantrikdb-core/src/engine/mod.rs:2495-2530` | Why sealing is not erasing |

## History

**2026-09-16** — [`b189e799bd854285471ec6149ff0f298cc594ec8`](https://github.com/yantrikos/yantrikdb/commit/b189e799bd854285471ec6149ff0f298cc594ec8) — first reading of the engine repository in its own right, at a commit dated 14 September 2026. The atlas had previously read these crates only as a pinned dependency of [yantrikdb-server](../yantrikdb/) at tag `v0.22.0`, and in process behind the [Hermes plugin](../yantrikdb-hermes-plugin/). Screened before opening, from a shallow clone; a dependency surface had changed inside the seven-day cooldown. Nothing was installed, built or run.

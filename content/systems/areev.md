---
title: "Areev"
eyebrow: "Two axes, and one of them is a penalty"
description: "A content-addressed grain store with world and knowledge time selectable at query time, a hash-chained review record carrying a mandatory reason, and one correction verb whose two implementations disagree about what it means."
root: ../..
page_kind: system
source_name: "AreevAI/areev"
source_url: https://github.com/AreevAI/areev
revision: 663caa8b0897f82a59a29dba0a7232639c55bc1f
revision_url: https://github.com/AreevAI/areev/commit/663caa8b0897f82a59a29dba0a7232639c55bc1f
analyzed_at: 2026-08-31
capabilities: "bitemporal, scope_enforced, audit_log, human_review, negative_eval"
stack_storage: "sqlite, postgres, files"
stack_retrieval: "vector, lexical, graph"
stack_source: "reviewed"
capability_evidence:
  bitemporal: "the store, as an axis the caller selects at query time | crates/areev-store/src/lib.rs:42-49,:85-93, crates/areev-core/src/types/grain.rs:170-175 | `GrainCommon` carries `valid_from`/`valid_to` beside `system_valid_from`/`system_valid_to`, and `entity_at` takes an `Axis`: `World` is documented *\"What was true in the world at T — valid_from/valid_to\"* and `Knowledge` is *\"What did the agent know at T — supersession chain walk\"*. Both spellings parse from the wire in every binding, so the question a caller is asking is a parameter rather than a convention. Supersession stamps `svt` in the same `UPDATE` that sets `superseded_by`, so the record-time interval is closed by the same write that opens the successor | crates/areev-conformance/src/cases/heads_forks.rs, supersede_forget.rs"
  scope_enforced: "the namespace column, on every read arm, under a fail-closed grant model | crates/areev-store/src/lib.rs:1184,:3749,:3777,:4264, crates/areev-core/src/authz.rs:1-16 | `ns` is a column on every grain and a predicate on every read: the vector query is `WHERE g.ns = ? [AND g.s = ?] [AND g.p = ?] ORDER BY <distance>`, `entity_latest`, `triples`, `osp` and the run index all carry it. Policy is data in the memory file — grant grains scoped per namespace — while credentials stay host-side holding *\"no policy and no raw secrets\"*, and the default is refusal: *\"A memory with no grant grains grants nothing to anyone but the owner session (fail closed).\"* | crates/areev-conformance/src/cases/ns_scope.rs:55-93 — a BM25 leg leaking outside the scope is asserted against by name, and an emptied namespace must stop matching prefix scopes"
  audit_log: "two records, both append-only, both in the store's own file | crates/areev-store/src/lib.rs:1217,:5127,:5290,:5932,:6153, crates/areev-loop/src/recommendation.rs:385-435 | the store keeps `oplog(op_seq INTEGER PRIMARY KEY, hlc INTEGER, op INTEGER, hash BLOB)` with one row per mutation — including `OP_FORGET` — inserted at six sites and never updated or deleted; `import_bundle` replays it, so an erasure replicates rather than diverging. Above it the loop writes one immutable Observation grain per recommendation transition, hash-chained through `previous_audit_hash`, carrying `from`/`to` status, a host-asserted `actor` such as `user:alice`, an `observer_type`, and a **mandatory** `because` capped at 500 characters — with `derived_from` chaining to the recommendation and the prior audit row | crates/areev-conformance/"
  human_review: "the recommendation lifecycle, with the transition table enforcing it and the reason required to record it | crates/areev-loop/src/recommendation.rs:336-400, crates/areev-mcp/src/lib.rs:966-1056 | `RecStatus` is `Pending / Approved / Rejected / Applied / RolledBack / Expired` and `can_transition_to` is a real table, not a suggestion: `Pending → Approved` and `Pending → Rejected` are open, `Approved → Applied` is open, and `Pending → Applied` is permitted only when `by_policy` is set — *\"the auto-apply actor, the only one permitted the reasonless pending → applied jump\"*, which names the one path that skips a person and marks it. `ObserverType` distinguishes `Human` from `Agent`, the MCP server lists pending recommendations and accepts transitions by name, and every transition persists an `AuditRecord` whose `because` field is not optional | crates/areev-conformance/"
  negative_eval: "the conformance kit, run against more than one backend, asserting in both directions over one fixture | crates/areev-conformance/src/cases/supersede_forget.rs:24-45, ns_scope.rs:55-93 | `forget_clears_head_row` asserts `heads(...).len() == 1` **before** the forget, then asserts empty heads, no open forks, empty recall and an erroring `get` — the positive control and the negative assertion over the same fixture. `forget_new_head_does_not_resurrect_old` forgets the *newer* version and asserts the superseded predecessor is not resurrected — recall empty, `latest` none — while `get(&h1)` still succeeds under the message *\"old blob is still readable, just not live\"*, which pins the withheld-versus-deleted distinction most systems here leave implicit. `ns_scope` asserts by name that a BM25 hit from another namespace does not appear. Every case takes `b: &dyn Backend` and reports `b.name()`, so the same assertions run against the real store and the reference substrate | this is the test"
matrix:
  memory_unit: "A typed grain — thirteen types under a versioned OMS spec, from Fact and Event to Skill, Recommendation and Trigger — content-addressed, carrying two validity intervals, provenance, a verification status and a supersession pointer"
  storage: "A content-addressed store over SQLite or Postgres, with attachments in a CAS and an append-only op log carrying a hybrid logical clock"
  retrieval: "CAL, one query language over hybrid recall — vector, BM25, graph traversal by relation and direction — with `entity_at` taking a world or knowledge time axis"
  write: "Grains are added, superseded with a justification and an authorisation list, or forgotten; the learning loop proposes changes from recorded history, citing evidence by hash"
  update_delete: "Supersession keeps history and closes the record-time interval in the same write; `forget` erases from the hot store, clears the FTS text and the CAS bytes, and writes a replicating tombstone to the op log"
  scoping: "Namespace on every grain and every read predicate, with grant grains in the file and credentials host-side, failing closed when no grant exists"
  integration: "A CLI, an MCP server, JS and Python bindings, an HTTP server, a sandbox and a conformance kit third-party substrates can run"
  background: "None by default — the project states there is no daemon and everything runs when you run it; the learning loop is invoked"
  trust: "`verification_status` of unverified / verified / contested / retracted, kept apart from a `confidence` float — caller-authored, and consumed on the read path as a ranking penalty rather than an exclusion"
  strengths: "World and knowledge time as a query parameter, a review record with a mandatory reason and a hash chain, a deletion that clears the text and the attachment bytes and replicates, and a conformance kit that runs the same negative cases against more than one backend"
  risks: "`retract` means a demotion in the trait and an erasure in the real substrate, and no conformance case covers the divergence; the content hash a value-level tombstone would need is not consulted on re-add; and the fresh dependency surface means none of this was built or run here"
---

## 1. Executive Summary

A content-addressed store of typed grains, one query language over it, and a
governed learning loop on top. 181,665 lines of Rust across seventeen crates,
dual-licensed MIT or Apache-2.0, 242 commits since 16 August 2026.

The README states the problem in the terms this atlas uses: an agent that
rewrites its own memory unsupervised *"fails every security review on the same
four questions: what changed, on what evidence, on whose authority, and can we
take it back?"* Three of the four are answered mechanically here, and the fourth
is answered better than almost anything in this corpus.

**Two temporal axes, and the caller picks one.** `entity_at` takes an `Axis`:
`World` is *"What was true in the world at T"* over `valid_from`/`valid_to`;
`Knowledge` is *"What did the agent know at T"*, walking the supersession chain.
Both parse from the wire in every binding. Most bi-temporal systems here store
two timestamps and query one; this one makes the question a parameter.

**The review record is the strongest in the corpus.** Every recommendation
transition writes an immutable Observation grain, hash-chained to its
predecessor, carrying the from and to status, a host-asserted actor like
`user:alice`, an observer type, and a **mandatory** written reason capped at 500
characters. The transition table is enforced rather than advisory, and the one
path that skips a person is named in a comment as it is allowed: `Pending →
Applied` requires `by_policy`, *"the auto-apply actor, the only one permitted the
reasonless pending → applied jump."*

**Deletion is done properly, and the code says what that means.** `forget` erases
the row, clears the free-text index — *"a tombstone that leaves the text findable
is not a tombstone"* — reclaims the content-addressed attachment bytes —
*"a tombstone that leaves the attachment bytes on disk is not a tombstone"* —
cleans the namespace registry, and writes an op-log tombstone that
`import_bundle` replays, so an erasure reaches replicas instead of diverging
them.

**Two marks are withheld and they are the findings.** `verification_status` is a
four-value discrete status — unverified, verified, contested, retracted — held
apart from a `confidence` float. It is authored by the caller rather than written
by the engine, and it is consumed on the read path as `-0.3` added to a priority
score that is then clamped. A retracted grain ranks lower and still surfaces, and
no query in the tree excludes on it.

The verb behind that status is the more interesting finding, because **the
codebase contains two incompatible definitions of it**. The `OmsSubstrate` trait
documents `retract` as *"Index-layer retraction (`verification_status =
retracted`) — the inverse of an applied ADD, used by rollback. Not destructive"*,
and the in-memory reference substrate implements exactly that. The adapter over
the real store refuses the mapping in as many words — *"No index-only retraction
primitive exists; the honest mapping for undoing an engine-created ADD is a
tombstone of that grain"* — and calls `forget`. So on the real store a rollback
**erases**; the demotion is what the trait promises and what the test double
does. Nothing in the conformance kit covers `retract`, which is the one operation
whose two backends disagree.

And the content hash that a value-level tombstone would key on is not consulted
on write. `forget` and its neighbours name the scenario three separate times —
*"a forget + re-add of identical content can move this hash to a NEW seq"* — and
each time solve the concurrency half of it under a row lock. The possibility is
anticipated and its bookkeeping is correct; whether the re-assertion should be
allowed is never asked.

Five marks. The project states three limits itself, and they are accurate:
it improves *"memory, never model weights"*, *"nothing applies itself"* without an
explicit host grant, and there is *"no daemon"*.

## 2. Mental Model

A memory is a **grain**: one of thirteen types under a versioned spec the code
calls OMS, content-addressed, and carrying more lifecycle metadata than anything
else in this atlas. `Fact`, `Event`, `State`, `Workflow`, `Tool`, `Observation`,
`Goal`, `Reasoning`, `Consensus`, `Consent`, `Skill`, `Recommendation`,
`Trigger` — and the enum carries its own migration hazard as a comment, because
`areev-store` indexes the type column as the ordinal: *"inserting a variant
mid-enum would silently renumber every stored row and break type-filtered recall
in every existing file."* New variants are appended, and the reason is written
down.

**Two axes describe a grain's standing and they are kept apart.**
`verification_status` is `unverified | verified | contested | retracted`, and the
comment records that it *"replaces deprecated `contradicted` boolean"* — a
project that widened a boolean into a status because the boolean could not
express contested. Beside it sits `confidence: f64`. That separation is the thing
this atlas asks for in every report.

**Correction has three distinct moves, and the vocabulary distinguishes them.**
*Supersede* writes a successor, sets `superseded_by`, closes the record-time
interval, and carries a `supersession_justification` and a
`supersession_auth` list — correction is an authorised act, not an overwrite.
*Retract* is the loop's inverse of an applied ADD, and it is the one whose
meaning depends on which substrate answers: a non-destructive
`verification_status = retracted` in the trait contract and the reference
substrate, a `forget` in the adapter over the real store. *Forget* erases. Three
verbs for three different situations is rarer here than it should be — but only
two of them mean one thing.

**And the loop above it is a proposal lifecycle.** An analyzer proposes a
`Recommendation` citing evidence by hash; a person approves or rejects with a
reason; an apply stores its inverse; a later re-measurement can propose its own
revert. `RecStatus` moves `Pending → Approved → Applied → RolledBack`, with
`Expired` computed from `valid_to`.

What the state machine does not do is stop a caller-authored retraction from
being recalled, which is the gap the diagram draws — along with the fork in what
`retract` means.

```mermaid
%% caption: rollback's `retract` forks by substrate — an erasure on the real store, a demotion in the trait contract and the test double — while a caller-authored retracted status is only ever a priority penalty that still lets the grain surface
flowchart TD
    A["analyzer proposes a Recommendation<br/>evidence cited by hash"] --> P{"RecStatus, transition table enforced"}
    P -- "by_policy only" --> AP["Applied"]
    P -- "a person, with a mandatory BECAUSE" --> AR["Approved"] --> AP
    P -- "a person" --> RJ["Rejected"]
    AP --> AUD[("Observation grain per transition<br/>actor · observer_type · because<br/>hash-chained to the previous one")]
    AP --> INV["every apply stores its inverse"]
    INV -->|rollback| RET{"sub.retract — which substrate?"}
    RET -->|"adapter over the real store"| FRG
    RET -->|"trait default and reference substrate"| DEM["verification_status = retracted"]
    G[("grain: two validity intervals,<br/>confidence, verification_status,<br/>superseded_by")] --> SUP["supersede<br/>justification + auth list"]
    G --> FRG["forget"]
    G -->|"a caller sets the field"| DEM
    SUP --> Q1["read: AND superseded_by IS NULL<br/>— withheld"]
    FRG --> Q2["row erased, FTS text cleared, CAS bytes reclaimed,<br/>OP_FORGET replayed on replicas — gone"]
    DEM --> Q3["read: priority += -0.3, then clamp<br/>— ranked down, still returned"]
    Q3 -.->|"and the training export keeps it<br/>at loss_weight 0.0"| Q3

    style RET fill:#f5e6e0,stroke:#a35b3d
```

## 3. Architecture

Seventeen crates, and the shape is a store with surfaces rather than a service.

- **`areev-cal`** (54,396 lines) — the query language. The largest crate, which
  says where the design's weight sits.
- **`areev-store`** (22,185) — the content-addressed store over SQLite or
  Postgres: grains, triples, an OSP index for inbound traversal, `entity_latest`
  materialisation, an op log with a hybrid logical clock, a CAS for attachments.
- **`areev-core`** (17,516) — the grain types, the OMS wire format, authz
  primitives, pseudonymisation.
- **`areev-loop`** (12,095) — analyzers, recommendations, the audit record, and a
  substrate trait third parties can implement.
- **`areev-context`** (5,236) — budget-shaped context assembly and the priority
  model.
- Surfaces: **`areev-cli`**, **`areev-mcp`**, **`areev-server`**, **`areev-js`**,
  **`areev-py`**, plus **`areev-conformance`**, **`areev-bench`** and a
  **`fuzz`** target.

### Deployment and ergonomics

*"No daemon — everything runs when you run it."* A memory is a file; the CLI, the
MCP server and the bindings all open it. That is a genuinely low floor for a
system with this much machinery, and it is the reason the single-user path never
meets the authorisation model at all — the owner session is *"a local open with
no principal asserted"*, the implicit superuser.

Postgres is the alternative backend and is exercised by the conformance kit
(`crates/areev-conformance/tests/pg.rs`), so the store's contract is tested
against two engines rather than asserted to hold for both.

**Nothing here was built or run.** Fourteen dependency surfaces sit inside the
seven-day freshness cooldown at this commit, `Cargo.lock` among them, so the
tree was read rather than compiled and every number in this report comes from
the source. `AGENTS.md` and `CLAUDE.md` were read as data.

## 4. Essential Implementation Paths

**Write** — a grain is serialised to the OMS format, hashed, and inserted with
its namespace, subject, predicate, object, both validity intervals, and its
supersession pointers, with `INSERT INTO oplog(op_seq,hlc,op,hash)` recording the
mutation.

**Supersede** — `UPDATE grains SET superseded_by=?1, svt=?2 WHERE seq=?3`. One
statement closes the record-time interval and points at the successor, so the
two cannot drift apart.

**Forget** — `crates/areev-store/src/lib.rs:5170-5300`. The pre-transaction read
takes only the `(ns, s, p)` key and deliberately not the sequence, because *"a
concurrent forget + re-add can move this hash to a new seq"*; the sequence is
re-resolved under the row lock so *"two racing forgets must produce one success
and one NotFound"*. Then the row goes, the FTS text goes, the namespace registry
entry goes, the CAS attachments are reclaimed, and `OP_FORGET` is written.

**Read** — CAL over hybrid recall: a vector query filtered by namespace and
optionally subject and predicate, a BM25 leg, and graph traversal by relation
with an `In` direction served from the OSP index. Latest-materialisation filters
`AND superseded_by IS NULL`.

**Time travel** — `entity_at(entity, t, axis)`. `World` filters the validity
interval; `Knowledge` walks the supersession chain to what was current at `t`.

**The loop** — an analyzer emits a `Recommendation` with a `dedup_key` computed
from the analyzer family, target and action kind, *"never author-chosen"*, a
deterministic template-rendered summary — *"never analyzer prose"* — a
`metric_snapshot` carrying *"the measurable claim the recommendation rests on,
for outcome review"*, and an `evidence_query` in CAL that regenerates the full
evidence set when the cited subset was truncated. A transition then writes the
audit Observation.

## 5. Memory Data Model

`GrainCommon` is the widest common record in this atlas: namespace, user id,
tags, confidence, source type, importance, temporal type, four timestamps,
content and embedding refs, a provenance chain, related-to links, author and
origin DIDs, origin namespace, `derived_from`, consolidation level, success and
failure counts, `superseded_by`, `verification_status`, an invalidation policy,
a supersession justification, a supersession auth list, and `created_at`.

**Bi-temporality is complete and queryable**, per section 1 — two intervals, two
named axes, and both spellings parseable from every binding.

**`verification_status` is the near miss, and it is a near miss for a specific
reason.** The field is right: four values, discrete, separate from `confidence`,
widened from a boolean because the boolean could not say *contested*. What is
missing is a producer and a consequence.

The producer first, because it is not what the trait says it is.
`crates/areev-loop/src/substrate.rs:174-181` documents `retract` as
*"Index-layer retraction (`verification_status = retracted`) — the inverse of an
applied ADD, used by rollback. Not destructive"*, and
`crates/areev-loop/src/reference.rs:174-186` — the in-memory double — implements
it, setting `superseded_by = "retracted"`, the status field and a
`retract_reason`. The adapter over the real store declines:

```rust
fn retract_op(f: &AreevFacade, hash: &str) -> WResult<()> {
    // No index-only retraction primitive exists; the honest mapping for undoing
    // an engine-created ADD is a tombstone of that grain.
    let h = Hash::from_hex(hash).map_err(we)?;
    f.with_store(|m| m.forget(&h)).map_err(we)
}
```

So `Engine::rollback` calling `sub.retract(h, …)` erases on the real store and
demotes in tests, and the only automatic writer of `"retracted"` in the tree is
the test double at `reference.rs:182`. On a real deployment the status is
caller-authored — the Python and JS bindings let a user set it — rather than
engine-written.

That makes the read-path treatment the whole of the consequence. In
`crates/areev-context/src/render.rs:237-241`:

```rust
let verification_penalty = match grain.get_str("verification_status") {
    Some("retracted") => -0.3,
    Some("contested") => -0.15,
    _ => 0.0,
};
(base + score_boost + confidence_boost + verification_penalty).clamp(0.0, 1.0)
```

A retracted grain is a lower-priority grain, not an excluded one. The mark asks
for *"at least one state that withholds a memory from being treated as true"* and
draws the line at usage: a score gets ranked, a state gets filtered. The one
place the status does bite is the corpus export, where
`crates/areev-cli/src/corpus.rs:208-217` maps `retracted` to
`("rejected", 0.0)` — but that emits the record with `"quality": "rejected",
"loss_weight": 0.0` rather than dropping it, and it is a training artifact rather
than the recall path. Stated so a reader can disagree on the evidence: the field
is real, and no query in the tree excludes on it.

**The divergence is untested.** `crates/areev-conformance/src/cases/` holds
ten case modules and not one mentions `retract`. Every other correction verb is
covered against `&dyn Backend` in both directions — `supersede_forget.rs` and
`erasure.rs` do the work the report credits under `negative_eval` — so the single
operation whose two implementations mean different things is the single one the
multi-backend kit does not exercise. A substrate author implementing the trait to
its documentation gets the demotion, and nothing tells them the reference
deployment does something else.

**The tombstone is the other near miss, and it is closer than most.** The store
is content-addressed, so the hash *is* a function of the content — precisely the
key a rejected-value tombstone needs, already computed and already in the op log.
What is absent is the consult. Three separate comments in
`crates/areev-store/src/lib.rs` — at the supersede recheck (`:5064`), inside
`forget` itself (`:5176`) and at its delete recheck (`:5209`) — name the exact
scenario: *"a forget + re-add of identical content can move this hash to a NEW
seq — deleting the stale one would report success while erasing nothing (and
diverge replicas via the tombstone)"*. Each re-resolves the row under a lock so
the bookkeeping stays correct. The case is anticipated carefully and repeatedly,
and the question the anticipation raises — whether the re-assertion should be
allowed at all — is never put. One lookup against the forgotten set on the write
path is the whole difference.

## 6. Retrieval Mechanics

One language over three arms. CAL compiles to a namespace-scoped vector query,
a BM25 leg, and graph traversal with `Out`, `In` or `Both` — where `In` is served
from a dedicated OSP index and the doc notes the consequence, that it *"only sees
entity-valued relations"*.

**Scope is applied as a predicate, before ranking**, on every arm — the vector
query's documented shape is `WHERE g.ns = ? [AND g.s = ?] [AND g.p = ?] ORDER BY
<distance> LIMIT k`, so the filter is in the SQL rather than over the results.

**Context assembly is budget-shaped and pseudonymised.** `areev-context` builds a
priority per candidate from a base by grain type, a score boost, a confidence
boost above 0.5, and the verification penalty above, then fills a token budget.
Grain-type overrides are policy.

**The failure mode is the one section 5 names.** Everything the read path can
withhold, it withholds by a predicate — a superseded grain by
`superseded_by IS NULL`, a foreign namespace by `ns = ?`, a forgotten grain by
not existing. The one axis that is a judgement about truth is the one applied as
arithmetic.

## 7. Write Mechanics

Writes are synchronous and no model sits on the path — a grain is retrievable
when the transaction commits. There is no background pass, and the project says
so rather than leaving it to be discovered.

**Supersession is authorised, not merely recorded.** `supersession_justification`
and `supersession_auth` sit on the grain, so a correction carries who permitted
it and why, in the record rather than in a log beside it.

**The loop's write discipline is worth naming.** A recommendation's `dedup_key`
is computed rather than chosen; its summary is template-rendered and explicitly
*"never analyzer prose"*, so the text a reviewer reads cannot be argued into
being persuasive; its `metric_snapshot` is *"the measurable claim the
recommendation rests on, for outcome review"*, which is what makes a later
re-measurement possible; and its `evidence_query` regenerates the full evidence
set when the citation was truncated, so a reviewer is never stuck with a sample.

**Every apply stores its inverse**, which is what makes the rollback path real
rather than aspirational — and on the real store that inverse for an ADD is a
`forget`, so an undone recommendation is erased rather than demoted.

### Operational cost

No embedding pass on write unless the caller supplies one — `EmbeddingRef`
points at an external vector store rather than owning one. No nightly
consolidation. The cost is the analyzers, which run when invoked, and the LLM
calls in `areev-llm` for the context that is assembled. Nothing scales with
corpus size on a schedule.

## 8. Agent Integration

A CLI, an MCP server, JS and Python bindings, an HTTP server, and a substrate
trait with a conformance kit — *"it doubles as the conformance kit for
third-party substrates"*, and the reference substrate exists so *"engine CI runs
the full suite against it with zero Areev, so the portability claim stays
testable"*. A portability claim with a test behind it is unusual.

**Agency is bounded by the grant model.** Policy is grant grains in the file,
credentials are host-side and hold no policy and no raw secrets, and the default
is refusal. The single-user path never meets it: a local open with no principal
asserted is the implicit superuser, which is the right default and worth knowing
before reading the authorisation code as though it always applies.

**The capability gates in the substrate trait are the other half.** `put_blob`
and `get_blob` default to refusing — *"CAPABILITY-GATED: the default refuses, so
a loop can only carry code on substrates that explicitly opt in"* — and `retract`
defaults to unsupported so substrates opt in. A trait whose dangerous methods
fail closed by default is a design decision most trait-based seams in this atlas
do not make.

## 9. Reliability, Safety, and Trust

**Provenance is a chain, not a field**: `provenance_chain`, `author_did`,
`origin_did`, `origin_namespace`, `derived_from`. Recommendations cite evidence
by hash and carry a CAL query that regenerates it.

**The audit is two records and both are append-only.** The op log is one row per
mutation with a hybrid logical clock, replayed by `import_bundle` so replicas
converge including on erasures. The loop's audit is one immutable Observation per
transition, hash-chained, with a mandatory reason — so the sequence of decisions
about a recommendation is tamper-evident in the same store as the memory it
changed.

**Erasure is treated as a security property rather than a bookkeeping one.** The
comments make the standard explicit twice, on text and on attachment bytes, and
the file-level path is named as the strong one: *"File-level crypto-erasure
remains the strong path."*

**Uncertainty can be represented and is not enforced.** `contested` exists as a
state and costs a grain 0.15 of priority. A system that can say *I have this on
record and do not believe it* and then ranks it down is one predicate away from
acting on it.

**Two marks withheld**, both in section 5 with their evidence. `tombstone` — the
content hash is not consulted on re-add. `trust_state` — the status is a ranking
term.

## 10. Tests, Evals, and Benchmarks

**2,522 test functions**, a fuzz target, a `deny.toml`, and a dedicated
conformance crate — and the conformance kit is the artifact worth describing,
because it is doing something most test suites here do not.

Its cases take `b: &dyn Backend` and report `b.name()` in every assertion
message, so the same case runs against the real store, the Postgres backend and
the in-memory reference substrate. A contract tested against more than one
implementation is a contract; tested against one it is a description.

The negative cases are non-vacuous by construction. `forget_clears_head_row`
asserts the head exists before forgetting and then asserts four different
absences. `forget_new_head_does_not_resurrect_old` forgets the newer version and
checks the older one stays superseded — *"the superseded old version stays
superseded — no silent resurrection"* — while asserting `get(&h1)` still
succeeds, *"old blob is still readable, just not live"*. That last pair is the
withheld-versus-deleted distinction this atlas spends whole reports drawing,
asserted in two lines.

`ns_scope` covers the leak directly: after seeding a value in another namespace,
`assert!(!hits.iter().any(|o| o == "personal-value"), "BM25 leg leaked outside
the scope")`. It also asserts that a malformed pattern *refuses* while an unknown
prefix answers empty — the distinction between an error and an absence, tested.

And `crates/areev-conformance/tests/pg.rs:192` asserts
`telemetry_access_stats(...).is_empty()` under the message *"scrubbed on
forget"*, so the erasure standard is checked against telemetry too.

**What is not tested is the gap this report names.** No case asserts that a
retracted grain is excluded from a recall, because none is — the assertion would
fail. No case asserts that re-adding forgotten content is refused, for the same
reason. Both absences are consistent with the code rather than oversights, which
is worth saying plainly: this suite tests what the system does.

The third absence is not consistent with the code. `retract` appears in none of
the ten case modules, and it is the one verb whose two implementations disagree
— an erasure through the adapter, a status demotion in the reference substrate
the kit also runs against. A case that called `retract` and asserted the same
post-condition on both backends would fail today, and that is the point of
owning a conformance kit.

**Benchmarks exist and their results do not ship.** `areev-bench` is 10,141 lines
and the pinned commit is a benchmark merge (`bench/2x2-llm-isolation`), but no
committed result file, leaderboard or run artifact appears in the tree, so no
performance claim here can be checked against anything.

## 11. For Your Own Build

### Steal

- **Make the temporal axis a query parameter.** `entity_at(entity, t, axis)` with
  `world` and `knowledge` spelled out in the wire protocol turns "what was true"
  and "what did we believe" into two answerable questions instead of one
  ambiguous one. It costs a parameter and a documented enum.
- **Require the reason in the type.** `AuditRecord.because` is a `String`, not an
  `Option<String>`, capped at 500 characters and described as *"the review
  statement's BECAUSE"*. A reason that cannot be omitted is worth more than a
  policy saying it should not be.
- **Hash-chain the decisions, not just the data.** One immutable Observation per
  transition, each pointing at its predecessor, gives you a tamper-evident record
  of *who decided what and why* in the same store as the thing they decided
  about.
- **Write down what a tombstone has to clear.** *"A tombstone that leaves the
  text findable is not a tombstone"* and *"a tombstone that leaves the attachment
  bytes on disk is not a tombstone"* are the two failure modes this atlas finds
  most often, named in the code that avoids them.
- **Make the dangerous trait methods fail closed.** `put_blob` and `retract`
  default to refusing, so a capability arrives by opting in rather than by
  forgetting to opt out.
- **Ship the conformance kit with the trait.** A substrate seam whose test suite
  runs against a reference implementation keeps the portability claim honest
  without anyone re-deriving it.

### Avoid

- **Spending a status as a score.** Four discrete values, a rollback path that
  writes the strongest one, and a read path that turns it into `-0.3` before a
  clamp. If a state cannot exclude, it is a confidence number with words for
  values — and the whole reason to have both axes was that they answer different
  questions.
- **Computing the key a refusal needs and not consulting it.** A content-addressed
  store already knows whether the exact value coming in is one that was thrown
  out. Not asking is a choice; here it is made in a comment that anticipates the
  re-add and handles the race instead.
- **Letting a training export and a recall path disagree about what counts.** A
  retracted grain is weight 0.0 in the corpus builder and a ranked candidate at
  recall. Whichever is right, they should not be different.
- **Documenting a trait method as one thing and implementing it as another.** The
  `retract` doc comment promises a non-destructive index-layer demotion; the
  adapter over the real store erases. The adapter's choice is the better one, and
  the trait it implements should say so — otherwise the next substrate author
  writes to the documentation.

### Fit

This is a more complete correction model than most systems here carry, in one of
the larger implementations, and the two are related: bi-temporality, authorised
supersession, replicating erasure, a hash-chained review record and a
capability-gated substrate seam are each a few thousand lines, and they only add
up because the store underneath them is content-addressed and typed.

Who should read it: anyone building a memory that has to survive a security
review, and anyone who has written `superseded_by` into a schema and not yet
decided what a *retraction* is as distinct from it. The three-verb vocabulary —
supersede, retract, forget — is worth taking on its own.

Who should be careful: adopters who read the marks as a summary. Five is high for
this corpus and the two that are missing are the two about *belief*. What Areev
governs extremely well is the **process** by which memory changes — who proposed,
who approved, on what evidence, how to undo. What it does not yet do is stop a
caller-authored retraction from reaching the model on the next turn — though a
recommendation rolled back through the loop is erased outright on the real store,
which is the stronger answer.

## 12. Open Questions

- **Is the retraction penalty deliberate?** A `-0.3` on a clamped priority is a
  designed number, not an oversight, so the question is whether recall is meant
  to surface retracted grains in some circumstance — and if so, whether the
  caller can tell.
- **Which `retract` is the contract?** The adapter erases and the trait documents
  a demotion. Whichever is intended, a conformance case would pin it and a
  third-party substrate would then have something to implement against.
- **Why does the corpus export weight what recall ranks?** The two consumers make
  different decisions about the same field.
- **Would the forgotten set be consulted on write if it were cheap?** It is: the
  op log already holds every `OP_FORGET` hash.
- **What do the benchmarks show?** `areev-bench` is 10,141 lines and the pinned
  commit is a benchmark merge; no result artifact is committed.
- **How much of the authorisation model is exercised in the single-user path?**
  The owner session is the implicit superuser, so the grant machinery may be
  reached mostly by tests.

## Appendix: File Index

**Types and format**
- `crates/areev-core/src/types/grain.rs:12-33` — the thirteen grain types and the
  ordinal-stability comment; `:58-64` — `TemporalType`; `:160-200` —
  `GrainCommon`, including `verification_status` and the supersession fields.
- `crates/areev-core/src/types/recommendation.rs` — the recommendation grain.
- `crates/areev-core/src/authz.rs:1-16` — the grant model and the fail-closed
  default.

**Store**
- `crates/areev-store/src/lib.rs:40-49` — `OP_FORGET` and the `Axis` enum;
  `:85-93` — the axis wire spellings; `:1217` — the op-log schema; `:4617,:4744` —
  `superseded_by IS NULL`; `:5080` — the supersession update; `:5170-5300` —
  `forget` and its tombstone standard.

**Loop**
- `crates/areev-loop/src/recommendation.rs:230-271` — the recommendation;
  `:336-375` — `RecStatus` and `can_transition_to`; `:385-435` — `AuditRecord`
  and the mandatory `because`.
- `crates/areev-loop/src/substrate.rs:168-200` — `retract`, `put_blob` and the
  capability gates.
- `crates/areev-loop/src/reference.rs:1-12` — the reference substrate.

**Read path**
- `crates/areev-context/src/render.rs:232-243` — `adjusted_priority` and the
  verification penalty.
- `crates/areev-cli/src/corpus.rs:208-217,:251-260` — the export's quality label
  and loss weight.

**Tests**
- `crates/areev-conformance/src/cases/supersede_forget.rs`, `ns_scope.rs`,
  `heads_forks.rs`, `blobs_hybrid.rs`; `tests/pg.rs`.

## History

**2026-08-31** — [`663caa8b0897f82a59a29dba0a7232639c55bc1f`](https://github.com/AreevAI/areev/commit/663caa8b0897f82a59a29dba0a7232639c55bc1f) — second reading at the same commit, correcting one claim about `retract`. The first reading traced the verb to the `OmsSubstrate` trait doc and the in-memory reference substrate, both of which define it as a non-destructive `verification_status = retracted`, and reported rollback as writing that status. `crates/areev-loop-adapter/src/substrate.rs:513-518` overrides it for the real store, rejecting the mapping in a comment — *"the honest mapping for undoing an engine-created ADD is a tombstone of that grain"* — and calling `forget`. A rollback on a real deployment therefore erases; the demotion is what the trait promises and what the test double does, and `crates/areev-loop/src/reference.rs:182` is the only automatic writer of `"retracted"` in the tree, which makes the status caller-authored in practice. `trust_state` stays withheld on the unchanged read-path evidence: the `-0.3` penalty at `crates/areev-context/src/render.rs:237-241` is still how the status is consumed and no query excludes on it. Two findings added: the trait and its production implementation disagree about what `retract` means, and no case in `crates/areev-conformance/src/cases/` exercises it, so the multi-backend kit does not cover the one operation whose backends diverge. The re-add finding is unchanged and sharpened — the store names the forget-then-re-add scenario at three sites and solves the concurrency half at each.

**2026-08-30** — [`663caa8b0897f82a59a29dba0a7232639c55bc1f`](https://github.com/AreevAI/areev/commit/663caa8b0897f82a59a29dba0a7232639c55bc1f) — first reading, at 242 commits. Screened before reading: no auto-run surface, two build-time execution surfaces, three unpinned surfaces, and **fourteen dependency surfaces inside the seven-day freshness cooldown** including `Cargo.lock`, so nothing was built and nothing was run; `AGENTS.md` and `CLAUDE.md` were read as data. Five marks. The report is organised around the three correction verbs, because supersede, forget and retract have three different read-path consequences here and only two of them withhold — which is also why the two missing marks are the two about belief rather than about process.

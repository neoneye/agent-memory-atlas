---
title: "Stella"
eyebrow: "Context plane"
description: "A Rust coding agent whose context plane keeps a bi-temporal property graph in one SQLite file and re-checks every committed claim before it can steer — demoting a lapsed one out of the cached prefix, dropping a refuted one entirely, and stamping a record's authority from the directory it was read out of rather than from anything it says about itself."
root: ../..
page_kind: system
source_name: "macanderson/stella"
source_url: https://github.com/macanderson/stella
archive_name: "macanderson--stella"
revision: e5faf774aaa3bd67c819ec3a6c4e72ac5366c25a
revision_url: https://github.com/macanderson/stella/commit/e5faf774aaa3bd67c819ec3a6c4e72ac5366c25a
analyzed_at: 2026-09-19
capabilities: "trust_state, bitemporal, scope_enforced, audit_log, human_review, negative_eval"
stack_storage: "sqlite, files, graph"
stack_retrieval: "vector, lexical, graph"
stack_source: "reviewed"
capability_evidence:
  trust_state: "a truth sweep that decides before rendering whether a claim is still true enough to steer, with the refused ones removed from the block rather than annotated | crates/stella-records/src/records/sweep.rs:1-110, crates/stella-records/src/records/registry.rs:309-330, crates/stella-records/src/records/render.rs:149-153, :202, crates/stella-records/src/context_record/kind.rs:210-256 | every record carries a stored truth axis — a basis, an optional probe, a time to live and an on-expiry instruction — and the sweep turns that plus the probe's verdict into one of five dispositions before anything is rendered. The filter is real rather than a label: `channel_of` returns nothing for a disposition that is not selected, and the renderer keeps only inputs whose channel matches, so a dropped or blocked record leaves the prompt entirely. A refuted record defaults to Drop and a merely expired one to a demotion into the volatile channel, and the module explains the split — nobody has shown the expired one wrong, its shelf life lapsed. The stored canonical status is a separate three-value field, active, retracted or archived, with a derived query-time status adding superseded and expired from the historical prefix and deliberately excluded from the record hash | dropped is not invisible: the entry keeps its disposition so the validate and explain commands can tell somebody the policy they committed is inert. Staleness is deliberately not a status but a separate derived selection-health value"
  bitemporal: "two intervals on every edge, closed by different writers, and one read predicate that applies both at once | crates/stella-context/src/store/edge.rs:26-52, :220-230, :282-318, crates/stella-context/src/writeback.rs:956-976, crates/stella-context/src/store/schema.rs:18-36 | an edge carries valid_from and valid_to for when the fact held in the world and recorded_at and superseded_at for when the store believed it. The neighbour query takes an as-of and a valid-at and tests both in one predicate, with the belief interval half-open and the world interval half-open, so a traversal can ask what we believed last month about what was true last year. Closing them is two different operations: a correction closes the belief interval and links the replacement, while ending world validity writes valid_to on its own, and one helper looks for anchors still open on both axes. The as-of read is the plain form of the same predicate | the schema comment is explicit that only edges are versioned — nodes are mutable current state, their valid columns are never written, and the row type deliberately does not project them so no consumer can read the NULL as an absence of valid time rather than an absence of node versioning. Fact history is recoverable; node content history is not"
  scope_enforced: "a stored domain tag turned into an exclusion set inside recall, with the session scope and the per-query scope kept as separate values | crates/stella-context/src/store/domain.rs:1-4, :115-143, crates/stella-context/src/retrieval.rs:34, :67-72, :126-155, :204-205 | domains are rows in their own table joined to nodes and edges, and a scoped recall builds the set of node ids to exclude with an anti-join — every node carrying a domain tag, none of which is in scope — then applies it during retrieval rather than after. Two scopes exist and the type keeps them apart because they answer different questions: the session's domain scope and a per-query one, with a third parameter for ids the caller suppresses for this call alone. The unscoped entry point is a thin wrapper that passes an empty scope, so there is one code path | the predicate excludes only nodes tagged exclusively out of scope, so an untagged node is visible in every scope. That is documented as the intended reading rather than an oversight — most memories carry no domain tag and a scope that dropped them would empty the channel — but it means the tag narrows a tagged corpus rather than partitioning an arbitrary one"
  audit_log: "an append-only ledger whose immutability is enforced by database triggers rather than by convention, keyed on content so a replay is a no-op and a collision is an error | crates/stella-context/src/store/ledger.rs:1-58, crates/stella-records/src/context_record/lifecycle.rs:16-33 | the lifecycle ledger stores a kind string, a canonical JSON body, a canonical hash over that body, the schema version the body was written against, when the described thing was observed, and the revision this one replaces. Append-only is not a rule the module follows: the migration installs BEFORE UPDATE and BEFORE DELETE triggers that abort, so the guarantee holds against every writer including a future one that has forgotten this module exists, and the only way to change what a record says is to append a new revision naming the old. Record ids are derived from content, so re-extracting the same evidence computes the same id and the second append is a silent no-op — while the same id arriving with a different hash is raised as an error, because that means two different records claimed one identity | the crate that owns the storage deliberately does not depend on the typed record taxonomy, so this layer validates the hash and the identity but not the body's shape"
  human_review: "the authority a record is published under is stamped from the directory it was read out of, and it is the one field the record is not allowed to claim about itself | crates/stella-records/src/records/trust.rs:1-90, crates/stella-records/src/ingest/gate.rs:1-47 | origin, truth basis and verified-by are all fields inside the file being judged, so a checkout can assert them as easily as it asserts anything else. The trust tier is stamped by the loader from where the file lives — the user's own rules directory outranks a repository one — and nothing in the file can change it. The shared gate both self-attestation checks use requires that stamped user tier plus a truth basis of decree plus a non-empty verified-by, which the module states as a decree only counting when somebody signed it. The two callers each add a condition and keep it local rather than widening the shared half: a record approving its own blocking guard must also be the user's own rather than a system one, and arming a probe that runs a command or reaches a host additionally requires an origin that is neither imported nor inferred, because mined content must never arm one. The lower tier is the default, with a test asserting that a forgotten stamp fails toward the restrictive answer | a project record may add enforcement and may never remove it; whether an untrusted checkout's records reach the prompt at all is a separate policy decided before any file is read"
  negative_eval: "suppression and point-in-time cases that assert the absence, the replacement that took the freed slot, and that the suppressed item never entered the ranking at all | crates/stella-context/src/retrieval/tests/recall.rs:495-510, :511-561, :562-594 | the suppression test sets the frame budget to one, records which frame wins, suppresses it, and then asserts three things: one frame still comes back, it is not the suppressed one, and restoring is an exact inverse that brings the original back. The docstring says why the shape matters — suppression used to run after the budget had already chosen, so a one-frame recall that ranked the suppressed memory first returned zero frames and the turn silently got less context than it asked for. The quarantine variant adds the sharpest assertion in the file: the excluded id must not appear among the dropped frames either, because an excluded id is not a candidate at all and never entered the ranking. A point-in-time case asserts that content recorded after the cutoff does not appear, with its own note that the parameter looked honored and was not | the fixture deliberately carries two nodes' terms so a relevant stand-in exists for the freed slot; the evidence gate refuses an irrelevant one"
matrix:
  memory_unit: "A node in a property graph — file, symbol, concept, fact, episode, person, artifact, task or memory — with edges carrying a relation, a weight and two time intervals; alongside a context record, an immutable hashed row in a lifecycle ledger"
  storage: "One SQLite file per workspace holding the graph, a fingerprinted embedding index, episodic memory and the append-only ledger; records also live as files in the repository's and the user's rules directories"
  retrieval: "Vector, recency and graph adjacency fused by reciprocal rank, deduplicated by content hash, packed to a token budget, every frame carrying a citation label and a source chain, with a coverage gate that falls back to bounded lexical search and labels it as such"
  write: "One transaction per batch; facts close and supersede rather than being deleted, and byte-identical content under the active embedder fingerprint is never re-embedded"
  update_delete: "Correction closes the prior belief's intervals and links the replacement; suppression writes a marker on the node and is an exact inverse; compaction reclaims only derived index entries whose owner is already gone"
  scoping: "Domain tags in their own table, applied as an exclusion set during recall, with the session scope and the per-query scope held as separate values"
  integration: "A terminal coding agent with its own TUI, an MCP surface, a plugin system with a consent boundary, a fleet layer and a plugin verification ladder"
  background: "A truth sweep that re-probes committed claims on their declared cadence, embedding catch-up warmed at mount rather than on first query, and a staleness scan that ends the world validity of anchors whose files have moved on"
  trust: "A stored truth axis on every record — basis, probe, time to live, on-expiry — resolved into a disposition before rendering: selected, selected but stated unverified, demoted to the volatile channel, dropped, or blocked"
  strengths: "An append-only guarantee enforced by database triggers rather than by convention; two time axes written by different operations and applied together in one predicate; and a trust tier that is stamped from the filesystem because it is the one thing a file cannot assert about itself"
  risks: "The domain scope excludes only nodes tagged exclusively out of scope, so untagged content is visible everywhere; node content is not versioned even though the columns for it exist, so only fact history survives a correction; and the codebase calls its node suppression marker a tombstone, which is a different mechanism from the one this atlas means by the word"
---

## 1. Executive Summary

Stella is a terminal coding agent in Rust — thirty crates, its own TUI, a
plugin consent boundary, a fleet layer. The part this atlas reads is the
**context plane**, described in its own header as the single door between the
engine and everything the agent knows that isn't already in the prompt: one
SQLite file holding a bi-temporal property graph, a fingerprinted embedding
index and episodic memory, with a budgeted, cited retrieval pipeline on top.

Six marks, and what they have in common is that each one is enforced somewhere
a later contributor cannot quietly undo.

**Append-only is a database trigger, not a rule.** The lifecycle ledger's
migration installs `BEFORE UPDATE` and `BEFORE DELETE` triggers that abort, and
the module says why in one sentence: the guarantee then holds against every
writer *"including a future one that has forgotten this module exists."*

**Authority is stamped from the filesystem.** A record's `origin`, `truth.basis`
and `verified_by` are fields inside the file being judged, and a checkout can
assert them as easily as it asserts anything else. So the trust tier is set by
the loader from *which directory the file was read out of*, and nothing in the
file can change it — *"a decree only counts when somebody signed it."* The
default is the lower tier, with a test asserting that a forgotten stamp fails
toward the restrictive answer.

**A committed claim is re-checked before it can steer.** The truth sweep's own
motivating case is a `CLAUDE.md` that says *"we use Node 20"* while `.nvmrc`
has said `22` for months — a claim probed once at extraction and never again,
teaching the agent something false on every turn with the full authority of a
reviewed policy file. A refuted claim is dropped from the block; a merely
expired one is demoted into the volatile channel, where the reason can be said
out loud without putting a clock into the byte-stable cached prefix.

**Two time axes, closed by different writers.** An edge carries when the fact
held in the world and when the store believed it, and the neighbour query
applies both at once.

The one mark withheld that the code appears to claim is the tombstone. Stella
uses the word for its node-suppression marker, which is a soft delete keyed on
the row. It is reversible, tested as an exact inverse, and applied before the
budget rather than after — but nothing here is keyed on a rejected *value*.

## 2. Mental Model

Two planes, and it is worth keeping them apart.

**The context plane** is the graph: nodes, edges, embeddings, episodes. It
answers *what do we know, and what did we know at T1*. Facts are edges, and a
correction closes intervals rather than deleting rows.

**The record plane** is policy: rule files and record files, merged into one
order and rendered into the prompt. It answers *what should steer this turn*.
Records carry a truth axis, get probed on a cadence, and are dispositioned
before rendering.

The design constraint that shapes the second plane is prompt caching. The
`must`/`should` records ride a byte-stable cached prefix built once per session,
so nothing turn-varying may enter it — which is why a stale record is not
annotated in place but moved to the volatile channel, and why staleness is
deliberately *not* a record status but a separate derived selection-health
value.

## 3. Architecture

```mermaid
%% caption: records load from the repository's and the user's rules directories with a trust tier stamped from the directory itself, pass a deterministic ingest gate that quarantines executable content and refuses to arm a command-running probe on mined content, and are dispositioned by a truth sweep before rendering — a refuted claim dropped from the prompt, a lapsed one demoted out of the byte-stable cached prefix into the volatile channel; separately the context plane keeps a bi-temporal property graph in one SQLite file where a correction closes the prior belief's intervals rather than deleting, recall fuses vector, recency and graph adjacency under a domain-scope exclusion and a token budget with a citation on every frame, and every lifecycle record lands in an append-only ledger whose immutability is enforced by database triggers
flowchart TD
    subgraph RecordPlane["record plane"]
        RF["rules files<br/>repo · user home"] --> LOAD["loader stamps Trust<br/>from the directory<br/>the file cannot claim it"]
        LOAD --> GATE{"ingest gate<br/>atomic? executable quarantined?<br/>probe gated by origin?<br/>probe can refute?"}
        GATE --> SWEEP{"truth sweep<br/>basis · probe verdict · ttl · on_expiry"}
        SWEEP -->|refuted| DROP["Drop — leaves the prompt<br/>still visible to validate/explain"]
        SWEEP -->|expired| STALE["SelectStale — demoted to<br/>the volatile channel"]
        SWEEP -->|unfalsifiable| UNF["renders, stated unverified<br/>never folded into supported"]
        SWEEP -->|believed| SEL["Select"]
        SEL --> PREFIX[["byte-stable cached prefix"]]
        STALE --> VOL[["volatile channel, per turn"]]
        UNF --> VOL
    end

    subgraph ContextPlane["context plane — one SQLite file"]
        UP["upsert"] --> TX{"one transaction"}
        TX --> NODE[("node<br/>current state<br/>superseded_at marker")]
        TX --> EDGE[("edge<br/>valid_from/valid_to · world<br/>recorded_at/superseded_at · belief")]
        TX --> EMB[("embedding<br/>keyed by content hash + fingerprint")]
        TX --> LED[("lifecycle ledger<br/>BEFORE UPDATE/DELETE triggers abort")]

        Q["recall"] --> SCOPE["exclude nodes tagged<br/>only out of scope"]
        SCOPE --> FUSE["vector + recency + graph<br/>reciprocal-rank fusion"]
        FUSE --> BUD["budget pack<br/>citation on every frame<br/>drops reported, never silent"]
        NODE --> Q
        EDGE --> Q
        EMB --> Q
        ASOF["facts_as_of / valid_at"] --> EDGE
    end

    PREFIX --> TURN["the turn"]
    VOL --> TURN
    BUD --> TURN
```

## 4. Essential Implementation Paths

- **The plane's contract:** `crates/stella-context/src/lib.rs` — four jobs, and
  the binding lessons it names.
- **Store and schema:** `crates/stella-context/src/store.rs`,
  `store/schema.rs`, `store/node.rs`, `store/edge.rs`.
- **Ledger:** `crates/stella-context/src/store/ledger.rs`.
- **Write-back:** `crates/stella-context/src/writeback.rs`.
- **Recall:** `crates/stella-context/src/retrieval.rs`, `candidates.rs`.
- **Scope:** `crates/stella-context/src/store/domain.rs`.
- **Truth sweep and rendering:** `crates/stella-records/src/records/sweep.rs`,
  `registry.rs`, `render.rs`, `trust.rs`.
- **Ingest gate:** `crates/stella-records/src/ingest/gate.rs`.

## 5. Memory Data Model

Nodes carry a typed kind — file, symbol, concept, fact, episode, person,
artifact, task, memory — and the vocabulary has a stated fallback: an unknown
stored kind reads back as `concept` rather than failing.

Edges carry four time columns. Nodes carry them too, and two of the four are
never written, which the schema comment addresses head-on: dropping a column in
SQLite rewrites the table, so they stay, and the row type *deliberately does not
project them* so no consumer can read the NULL as an absence of valid time
rather than an absence of node versioning. Fact history is recoverable; node
content history is not, and the file says so.

On the record side, `RecordStatus` is the stored canonical field — active,
retracted, archived — while `EffectiveStatus` is derived at query time from the
historical prefix, adding superseded and expired, and is excluded from the
record hash because it is a projection rather than state.

The most instructive type in the tree is an enum variant. `EpisodeOutcome`
carries an `Unverified` value whose documentation is the clearest statement of
the idea anywhere in this reading: the episode ran to completion and nothing
proved it. Deliberately not `Success`, because episodes are recalled into later
sessions as grounding and labelling an unproven run a success hands a future
turn a worked example that was never checked. Deliberately not `Failure`,
because nothing found the work wrong and a retrieval that reads it as a mistake
teaches the opposite lesson. Distinct from `Partial`, which is a claim about how
much of the goal landed — *"this is a claim about the evidence."*

## 6. Retrieval Mechanics

Recall fuses vector, recency and graph-adjacency channels by reciprocal rank,
deduplicates by content hash, and packs to the caller's token budget. Three
rules are enforced rather than advised: every frame must carry a human citation
label, and a frame constructed without one is a constructor error; silent
truncation is banned, so assembly reports what it dropped; and weak coverage
falls back to bounded lexical search **labelled as such** rather than dressed up
as grounding.

Scope is an exclusion set built by anti-join and applied during retrieval. Its
one asymmetry is documented in the entry point rather than discovered later: a
node tagged exclusively with out-of-scope domains is excluded, and an untagged
node is not, because most memories carry no domain tag and a scope that dropped
them would empty the channel.

Point-in-time recall applies the as-of predicate before the budget, which is
the same discipline suppression needed and for the same reason.

## 7. Write Mechanics

Every write batch is one transaction, so a kill mid-index rolls back to a
consistent store. Vectors are keyed by content hash and embedder fingerprint
together: identical content is never re-embedded, and retrieval never mixes
fingerprints.

Corrections close and supersede. The function that finds what to close is worth
reading for its bug note: it used to be a single-valued `ORDER BY id DESC LIMIT
1`, so an assert closed the newest belief and left every older live one open,
and the store kept answering with two simultaneous beliefs for a fact that is
single-valued by definition. It now closes all of them, and the note explains
how two live edges arise honestly — the same predicate asserted multivalued and
later corrected as single-valued.

Compaction is bounded by the same guarantee it must not break: it reclaims only
derived index entries whose owner is already gone, *precisely because* deleting
them cannot change what `facts_as_of` answers, and edges, memory revisions and
superseded node rows are named exclusions.

## 8. Agent Integration

A terminal agent with its own TUI, an MCP crate, a plugin system with a consent
prompt and a verification ladder, an autonomy layer, a fleet layer and an
observatory. Dual-licensed: AGPL-3.0-only, or a negotiated commercial licence,
with the "or any later version" clause deliberately not granted.

## 9. Reliability, Safety, and Trust

**Trust state — awarded.** A stored truth axis, a probe verdict, and a
disposition resolved before rendering, with the unselected dispositions removed
from the prompt by the channel function rather than annotated in place. The
distinction the module draws between *refuted* and *expired* is the part worth
copying: one has been measured against the world and lost, the other has merely
gone unchecked, and they get opposite defaults.

**Bi-temporal — awarded**, on two intervals written by different operations and
applied together in one predicate. The limit is stated in the schema comment
rather than left for a reader to find: only edges are versioned.

**Scope enforced — awarded**, with the untagged-node asymmetry in the evidence
record and documented in the code.

**Audit log — awarded.** Triggers, not convention; content-derived ids so a
replay is a no-op; a different hash under the same id raised as an error rather
than swallowed.

**Human review — awarded**, on the strongest shape available: the reviewer's
authority is the one fact the reviewed artefact cannot assert about itself. The
gate requires a loader-stamped user tier, a truth basis of decree, and a
non-empty signature, and its two callers each add a condition locally rather
than widening the shared half — the comment notes that moving either one inward
would tighten the other gate silently.

**Negative eval — awarded.** See the evidence record; the assertion that an
excluded id is absent from the *dropped* list too is the one that distinguishes
a filter applied before ranking from one applied after.

**Tombstone — withheld, and the vocabulary needs stating.** The codebase calls
`supersede_node` a tombstone, and by its own definition it is one: a marker
rather than a delete, reversible, invisible to every reader but the restore
path. What this atlas means by the word is narrower — a durable record of a
rejected *value*, keyed on the value, so a later extraction cannot silently
re-assert it. Stella's marker is keyed on the row. Re-ingesting the same
sentence from the same file produces a live node again. The nearest thing to a
value-keyed refusal is elsewhere and is about alerts rather than content: a
dismissed ingest lineage never produces a drift alert again, and its module is
explicit that *"dismissal says nothing about the records themselves: they stay
live and recallable."*

## 10. Tests, Evals, and Benchmarks

**No paper** and no `CITATION.cff`.

Tests live beside the code as Rust unit modules, with integration suites per
crate and a `bench/` tree carrying a terminal-bench adapter, a loop benchmark
and a request benchmark. No benchmark results are committed.

The recall suite is the one to read, and its distinguishing habit is that the
docstring on each case names the defect it exists to prevent — suppression
running after the budget so a one-frame recall returned zero frames; a
point-in-time parameter that *"looked honored and was not"*; a migration test
that reuses the store's own legacy fixture builder because *"two fixture
builders for one schema ladder is how a migration test ends up asserting against
a shape the ladder never produces."*

Two more enforcement mechanisms sit outside the test suite and are worth
counting as evals in spirit. Undocumented public items are a build failure under
the lint profile, which the comment explains as closing a gap that *"cannot
reopen one field at a time"*. And the append-only guarantee is checked by the
database rather than by a test, which is the difference between an invariant and
a habit.

## 11. For Your Own Build

- **Enforce append-only in the storage engine.** A `BEFORE UPDATE` trigger that
  aborts costs one migration and survives every future writer, including the one
  who never reads your module header.
- **Stamp authority from something the artefact cannot write.** A record's own
  `origin` field is worth exactly as much as the trust you already extend to
  whoever wrote the file.
- **Default the trust tier to the restrictive value, and test it.** The failure
  mode of the other default is a checkout silently inheriting a person's
  authority.
- **Separate refuted from expired.** Dropping every claim whose owner went on
  holiday makes a time-to-live a foot-gun; keeping a measured-and-lost claim
  with a warning attached is the harm rather than the mitigation.
- **Apply suppression before the budget.** Filtering after ranking spends a slot
  on a row you then throw away, and the turn gets less context than it asked for
  with nothing reporting it.
- **Derive record ids from content.** A replay then converges instead of
  duplicating, and a genuine identity collision becomes an error you can see.

## 12. Open Questions

- Node content is not versioned while the columns for it exist and are
  deliberately unprojected. Is versioning nodes a planned step, or is the
  current split — fact history recoverable, node content history not — the
  intended end state?
- The domain scope excludes only nodes tagged exclusively out of scope. Is there
  a deployment where the opposite reading is wanted, and would that need a
  distinction between an untagged node and one tagged with a domain nobody
  named?
- The one tool that collected a model's judgement of whether a shown memory was
  useful has been retired, on the stated ground that marking a memory truthful
  because it was shown *"would be a guess dressed up as evidence"*, with its
  tables kept unused for a later holdout sweep. What does that sweep look like,
  and what evidence would it use instead?

## Appendix: File Index

- Plane contract: `crates/stella-context/src/lib.rs`
- Store, schema, nodes, edges:
  `crates/stella-context/src/store.rs`, `store/schema.rs`, `store/node.rs`,
  `store/edge.rs`
- Ledger: `crates/stella-context/src/store/ledger.rs`
- Domains and scope: `crates/stella-context/src/store/domain.rs`
- Write-back: `crates/stella-context/src/writeback.rs`
- Recall: `crates/stella-context/src/retrieval.rs`,
  `crates/stella-context/src/candidates.rs`
- Truth sweep, registry, rendering, trust:
  `crates/stella-records/src/records/sweep.rs`, `records/registry.rs`,
  `records/render.rs`, `records/trust.rs`
- Ingest gate and lineages: `crates/stella-records/src/ingest/gate.rs`,
  `ingest/lineage.rs`
- Tests: `crates/stella-context/src/retrieval/tests/recall.rs`,
  `crates/stella-context/src/store/tests.rs`,
  `crates/stella-records/src/records/tests.rs`

## History

**2026-09-19** — [`e5faf774aaa3bd67c819ec3a6c4e72ac5366c25a`](https://github.com/macanderson/stella/commit/e5faf774aaa3bd67c819ec3a6c4e72ac5366c25a) — first reading, at the head of `main`. Screened with `scripts/screen_repo.py` before anything was read: three auto-run surfaces (committed git hooks and an agent harness's hook scripts and settings), seven build-time execution paths including a Cargo build script, a web postinstall and four pytest conftest files, floating ranges in the website package, and an `AGENTS.md` and a `CLAUDE.md` addressed to a reading agent, read as data throughout. Every manifest reported inside the seven-day cooldown, which is an artefact of a `--depth 1` clone dating every file to the tip; `Cargo.lock` is committed. Nothing was installed, built or run. Dual-licensed AGPL-3.0-only or commercial, with the "or any later version" clause deliberately not granted and no rider restricting analysis. Six marks. The reading covered the context plane end to end — schema and both time axes, the node and edge writers, the ledger and its triggers, write-back and supersession, recall with its scope exclusion and budget, compaction's stated bound — and the record plane's loader trust tier, ingest gate, truth sweep, registry and renderer, plus the recall and trust test suites; the TUI, fleet, autonomy, plugin and model crates were read only where they touched those paths. `tombstone` is withheld and the reason is a vocabulary difference worth recording: this codebase uses the word for a reversible node-suppression marker keyed on the row, and the atlas reserves it for a durable record of a rejected value keyed on the value.

---
title: "chitta-field"
eyebrow: "A veto is an Option, not a zero"
description: "An associative memory substrate whose statuses return None rather than a low weight when they exclude, whose contradiction detector compares claims rather than text, and whose write path is a per-writer hash-chained op log."
root: ../..
page_kind: system
source_name: "genomewalker/chitta-field"
source_url: https://github.com/genomewalker/chitta-field
archive_name: "genomewalker--chitta-field"
revision: f3176e587dced64dd3a6a663a40a58e3802b0a10
revision_url: https://github.com/genomewalker/chitta-field/commit/f3176e587dced64dd3a6a663a40a58e3802b0a10
analyzed_at: 2026-09-16
capabilities: "trust_state, audit_log"
capability_evidence:
  trust_state: "a seven-value status where three return `None` from the scoring helper, and a `None` skips the candidate outright rather than scoring it low | src/scoring/mod.rs:163-172, src/store.rs:3780, :3441, :3661 | `status_multiplier` maps `Active | Verified | Observed | Proposed` to configurable weights and `Superseded | Contradicted | Archived` to `None`, documented as \"[r]eturns None for excluded statuses\" and, at the type it guards, as a veto: \"vetoes the memory (excluded from results)\". The recall loop reads it as `Some(s) if status_multiplier(&s.status, &pipeline_config).is_none() => continue`, so exclusion is a control-flow skip and not a small number that a later re-weighting could restore. Held separately from it, `EpistemicStatus` — `UserStated | ToolDerived | ModelInferred | AutonomousSynthesis`, commented \"[h]ow a memory was obtained — orthogonal to confidence\" — produces a multiplier and never a veto, so where a memory came from weights it and never withholds it | src/state.rs:58-77"
  audit_log: "every mutation is an `Op` in an append-only segment log whose records are SHA-256 hash-chained to their predecessor | src/log.rs:19-30, src/ops.rs:14-40, src/store.rs | The `Op` enum is the complete mutation vocabulary — put payload, update state, batched state drain, delete memory, add association edge, add and invalidate triplet, upsert and remove symbol and call edge, demote memory, clear project, and the session, transcript, task, user-model, theme and analytics events — and the log is the durable write path, appended from sixty-nine call sites in the store. Each record links into a chain as a SHA-256 over its sequence number, op type, previous hash and payload together, with a CRC per record and a `vector_space_id` lineage stamp in the V3 header so replay \"[l]ets replay() fence out segments written in a foreign vector space (model/dim/text-format)\". The chain is per segment and there is one segment per writer process, so it is tamper-evidence within a writer rather than a single global order | src/log.rs:11-17"
stack_storage: "files"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A payload with a state carrying version, strength, decay rate, confidence, access counts, a pin, a tier, a retrieval history, a status and an epistemic status"
  storage: "An append-only op log — one segment per writer process — with in-RAM indexes and periodic binary snapshots to avoid full replay at startup"
  retrieval: "A cortical sparse index of 64 active bits in 16,384 for sub-millisecond associative recall, beside semantic, BM25, triplet, symbol-graph and temporal indexes"
  write: "One `Op` appended to the log per mutation, hash-chained and CRC'd; state is rebuilt by replay or loaded from a snapshot"
  update_delete: "Delete is an op and a `deleted` flag; supersession, contradiction and archiving are statuses that veto recall while the payload stays"
  scoping: "A project, cleared by its own op; no tenancy model"
  integration: "A Rust library with a C FFI, backing a companion daemon in a separate repository"
  background: "Decay, maintenance drains that preserve access timestamps, snapshotting, and a reconcile pass that detects illegal edges and contradictions"
  trust: "Statuses that veto, an epistemic status that only weights, a claim-level contradiction detector, and a hash-chained log"
  strengths: "Two separations are made deliberately and held. First, a status that excludes returns `None` rather than a small multiplier, so the recall loop skips the candidate as control flow — a zero weight is a number a later stage can multiply back up, and an `Option` is not. Second, how a memory was obtained is kept orthogonal to whether it is believed: `EpistemicStatus` produces a multiplier and can never veto, while `MemoryStatus` can, so a model-inferred memory ranks lower without being silently suppressed. The contradiction detector is the third: it is \"claim-centric, not text-centric\", and the header says exactly what that buys — \"[t]wo memories contradict when they make incompatible claims under overlapping scope (same subject+predicate), not merely when they are semantically similar\". Most systems in this corpus call cosine similarity a contradiction check. The log is hash-chained over `seqno || op_type || prev_hash || payload` with a per-record CRC, and its V3 header carries a vector-space id so replay refuses segments written under a different embedding model or dimension — a lineage failure that is otherwise found as silently wrong neighbours"
  risks: "The hash chain is per segment and there is one segment per writer process, so with several concurrent writers on the shared storage this design targets there is no single chained order — each writer's history is tamper-evident on its own, and their interleaving is not. Everything else in the state is continuous: strength, decay rate, confidence, the multipliers per kind and per epistemic status, all configurable, and the report finds no place where they are bounded the way a ranking multiplier needs to be. Nothing is consulted at write time against a contradicted or superseded memory, so the same claim can be written again and will be caught, if at all, by the next reconcile pass rather than refused at the door. There is no tenancy: the unit is a project, cleared by its own op. And the substrate is explicitly the backing store for a companion daemon that lives in another repository, so what an agent actually asks of it is not visible here"
---

## 1. Executive Summary

chitta-field is an "[o]rganic associative memory substrate for cognitive AI
companions" — MIT, Rust, version 2.7.12, 57,134 lines across ninety-five files
with 287 test functions, a C FFI, and a stated design target of shared NFS
storage, multiple concurrent writers, and sub-millisecond in-process recall. It
is the backing store for a companion daemon that lives in a separate repository.

Three layers: an append-only op log as the durable write path, in-RAM indexes
(semantic, BM25, a cortical sparse index, triplets, a symbol and call graph, a
temporal index), and periodic binary snapshots so startup does not replay the
whole log. The cortical index encodes memories as Sparse Distributed
Representations — 64 active bits out of 16,384 — which makes associative recall a
bitwise overlap rather than an approximate-nearest-neighbour search, and is a
genuinely uncommon choice in this corpus.

**A veto is an `Option`, not a zero.** `status_multiplier` maps the seven memory
statuses to a scoring factor, and three of them do not have one:

```rust
MemoryStatus::Superseded | MemoryStatus::Contradicted | MemoryStatus::Archived => None,
```

The recall loop reads that as `... .is_none() => continue`. The distinction
matters more than it looks: a zero weight is a number, and any later stage that
normalises, re-ranks or blends can multiply it back up. `None` is not a number,
and the compiler makes every caller decide what to do about it. The comment at
the type it guards uses the right word — the status "vetoes the memory (excluded
from results)".

**Where a memory came from weights it and never withholds it.**
`EpistemicStatus` is `UserStated | ToolDerived | ModelInferred |
AutonomousSynthesis`, under a comment that states the design: "[h]ow a memory was
obtained — orthogonal to confidence." Its helper returns a plain `f32`, not an
`Option`, so provenance can rank a model-inferred memory below a user-stated one
and can never silently suppress it. Two axes, two return types, and the type
signatures carry the policy.

**Contradiction is about claims, not text.** The detector's header draws the line
this atlas keeps looking for:

> "Design: claim-centric, not text-centric. Two memories contradict when they
> make incompatible claims under overlapping scope (same subject+predicate), not
> merely when they are semantically similar."

Memory content is parsed into claim atoms and indexed by claim scope. Most
systems here that advertise contradiction detection are running a cosine
threshold, which finds restatements and misses genuine disagreements phrased
differently.

**The write path is a hash-chained op log.** Every mutation is an `Op` — the enum
covers payloads, state deltas, batched maintenance drains, deletes, association
edges, triplets and their invalidation, symbols and call edges, demotion, project
clearing, and six event kinds — appended from sixty-nine call sites in the store.
Records chain as `H = SHA256(seqno || op_type || prev_hash || payload)` with a
CRC each, and the V3 segment header carries a `vector_space_id` so replay can
"fence out segments written in a foreign vector space (model/dim/text-format)".
That last one is worth copying on its own: an embedding model or dimension change
otherwise surfaces as quietly wrong neighbours rather than as an error.

The caveat on that chain is structural and follows from the concurrency target.
There is one segment file per writer process, so the chain is per writer: each
writer's own history is tamper-evident, and the interleaving of several writers
is not a single chained order.

Two marks. What is absent: nothing is consulted at write time against a
contradicted or superseded memory, so the same claim can be written again and is
caught by the next reconcile pass rather than refused at the door; the remaining
state — strength, decay rate, confidence, and the configurable multipliers per
kind and per epistemic status — is continuous, and no ceiling was found on the
multipliers the way a ranking factor needs one; and there is no tenancy, the unit
being a project with its own clear op.

## 2. Mental Model

A **memory** has a status that can veto it and an epistemic status that only
weights it.

A **contradiction** is two claims about the same subject and predicate, not two
similar sentences.

The **log** is the truth; the indexes and snapshots are how you avoid re-reading
it.

A **segment** belongs to one writer.

```mermaid
%% caption: the status helper returns None for the three excluded statuses so the recall loop skips them as control flow, while the epistemic helper returns a plain multiplier and can never veto
flowchart TB
    W["any mutation"] --> OP["one Op: put payload · update state ·<br/>batched drain · delete · assoc edge ·<br/>triplet + invalidate · symbol + call edge ·<br/>demote · clear project · six event kinds"]
    OP --> LOG[("append-only segment,<br/>one file per writer process")]
    LOG --> CHAIN["H = SHA256(seqno ‖ op_type ‖<br/>prev_hash ‖ payload), CRC per record"]
    CHAIN -.->|"per segment, so per writer —<br/>tamper-evident alone, no single<br/>chained order across writers"| CAVEAT["the concurrency target's cost"]
    LOG --> REPLAY{"replay / snapshot load"}
    REPLAY -->|"V3 header carries vector_space_id"| FENCE["segments from a foreign model,<br/>dimension or text format are fenced out<br/>instead of producing wrong neighbours"]
    REPLAY --> IDX["in-RAM indexes: cortical SDR<br/>(64 of 16,384 bits) · semantic · BM25 ·<br/>triplets · symbol graph · temporal"]
    IDX --> RECALL{"recall scoring"}
    RECALL --> SM["status_multiplier(status)"]
    SM -->|"Active · Verified · Observed · Proposed"| WEIGHT["Some(weight) — configurable"]
    SM -->|"Superseded · Contradicted · Archived"| NONE["None → `continue`<br/>a veto in control flow, not a zero<br/>a later stage could multiply back up"]
    RECALL --> EM["epistemic_multiplier(status)"]
    EM -->|"UserStated · ToolDerived ·<br/>ModelInferred · AutonomousSynthesis"| F32["a plain f32 — always weights,<br/>never vetoes: 'orthogonal to confidence'"]
    WEIGHT & F32 --> OUT["ranked results"]
    CD["contradiction detector"] -->|"'claim-centric, not text-centric' —<br/>incompatible claims under overlapping<br/>scope (same subject+predicate)"| STATUS["sets Contradicted"]
    STATUS --> SM
```

## 3. Architecture

| File | Role |
| --- | --- |
| `src/store.rs` | The store, recall, and the maintenance passes (12,206 lines) |
| `src/ffi.rs` | The C surface (10,361) |
| `src/log.rs` | Segments, chaining, replay, fencing |
| `src/ops.rs` | The complete mutation vocabulary |
| `src/scoring/mod.rs` | Where a veto is an `Option` |
| `src/contradiction.rs` | Claim atoms and claim scope |
| `src/hdc.rs`, `src/hnsw.rs` | Hyperdimensional codes and the ANN index |
| `src/organ/` | Triplets, spans, epistemic debt |

## 4. Essential Implementation Paths

`src/scoring/mod.rs:163-182` — two helpers, two return types, one policy.

`src/state.rs:58-77` — the two enums, and the comment that keeps them apart.

`src/contradiction.rs:1-10` — claim-centric, in six lines.

`src/log.rs:11-30` — the chain, the CRC, and the lineage stamp.

## 5. Memory Data Model

A payload plus a state: version, chunk hash, deleted flag, strength, decay rate,
confidence, access count and timestamps, pin, tier (`0=L1 hippocampus,
1=L2 cortex, 2=L3 archive`), a retrieval history, an embed-pending flag, and the
two statuses. Pinning is exemption from decay.

An `EpistemicDebtStore` sits under `organ/` with its own `DebtStatus` — the
project tracks what it owes itself epistemically, which is an idea worth a longer
look than this reading gave it.

## 6. Retrieval Mechanics

The cortical SDR index is the hot path — overlap counting on 64-of-16,384 bit
codes, with no learned index to warm up or rebuild — with the semantic, BM25 and
graph indexes beside it, and a scoring decomposition that reports each multiplier
separately so a result can be explained rather than just ranked.

## 7. Write Mechanics

Append an op, update the in-RAM state, snapshot periodically. The maintenance
drain is explicitly documented as preserving each access timestamp and count,
which is the detail that keeps a batch pass from erasing the very signal decay
depends on.

## 8. Agent Integration

A library with a C FFI; the agent-facing daemon is a separate project. That split
is why this report stops at the substrate: what is asked of it, and how often, is
decided elsewhere.

## 9. Reliability, Safety, and Trust

The chain and the CRC are integrity; the vector-space fence is correctness under
model change; the veto is policy. The gap is at the door — nothing refuses a
write that restates a contradicted claim, so the reconcile pass carries the whole
burden of noticing.

## 10. Tests, Evals, and Benchmarks

287 test functions across the source and benches, with snapshot-migration paths
for five prior formats — the kind of code that only exists once a format has
actually shipped and changed. Nothing was built or run for this reading.

## 11. For Your Own Build

Return `None`, not `0.0`, when a state excludes. A zero weight survives
normalisation, re-ranking and blending; an `Option` forces every caller to handle
the exclusion, and the compiler checks that they did.

Keep "how it was obtained" and "whether to believe it" in different types. A
multiplier that can never be a veto is a design decision you can enforce in a
return type instead of a review comment.

Detect contradiction on claims, not similarity. Two sentences about the same
subject and predicate that disagree are what you want; two sentences that sound
alike are what cosine gives you.

And stamp the embedding lineage into the log header. A model or dimension change
without a fence does not fail — it quietly returns the wrong neighbours, which is
worse.

## 12. Open Questions

Whether anything orders the writers. The per-writer segment chain is
tamper-evident within a process; how several writers' histories are reconciled
was not traced.

What the epistemic-debt store does. It has its own status enum under `organ/` and
looks like a deliberate mechanism rather than a scratch table.

Whether the scoring multipliers are bounded. They are configurable per kind and
per epistemic status, and no ceiling was found.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `src/scoring/mod.rs:163-182` | A veto as an `Option`, beside a weight as an `f32` |
| `src/state.rs:58-77` | Two orthogonal enums, and the comment that says so |
| `src/contradiction.rs:1-10` | Why similarity is not disagreement |
| `src/log.rs:11-30` | A hash chain, a CRC, and a lineage fence |
| `src/ops.rs:14-40` | The whole mutation vocabulary in one enum |

## History

**2026-09-16** — [`f3176e587dced64dd3a6a663a40a58e3802b0a10`](https://github.com/genomewalker/chitta-field/commit/f3176e587dced64dd3a6a663a40a58e3802b0a10) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: two files scanned, no auto-run surfaces, one build-time execution point, no unpinned surfaces and one dependency file inside the seven-day cooldown. Nothing was installed, built or run.

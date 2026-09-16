---
title: "yantrik-mind"
eyebrow: "Thirty lines of comment on one dependency line, because a path dep had been building it against whatever was lying around"
description: "A Rust companion over the YantrikDB belief engine whose own contribution is a purpose gate: scope and sensitivity stored on every belief, default-deny policies over them, and a receipt for every read including the operator's."
root: ../..
page_kind: system
source_name: "yantrikos/yantrik-mind"
source_url: https://github.com/yantrikos/yantrik-mind
archive_name: "yantrikos--yantrik-mind"
revision: 97935b1e247167ac7d4fe192ec8a9a1966b26c49
revision_url: https://github.com/yantrikos/yantrik-mind/commit/97935b1e247167ac7d4fe192ec8a9a1966b26c49
analyzed_at: 2026-09-16
capabilities: "scope_enforced, negative_eval"
capability_evidence:
  scope_enforced: "a two-value scope stored on the belief, a sensitivity class with default-deny purpose policies over it, and a legacy default that fails safe | crates/mind-types/src/memory.rs:218-236, crates/mind-types/src/purpose.rs:140-153, crates/mind-memory/src/receipts.rs:40-42 | `Scope` is `Shared` or `Private(person_id)`, stored in the form `shared` or `private:<owner>`, and the type's own comment states the rule it exists for: a fact \"from one person must NEVER surface to another.\" The migration default is chosen in the safe direction rather than the convenient one — \"[l]egacy/untagged memory is private to them, so pre-multi-user facts never leak to a later-added member\", which is the opposite of the usual arrangement where unlabelled rows become everyone's. Over that sits `Sensitivity`, four classes \"carrying purpose policies — default deny outside their allowed activities, whoever the fact belongs to\", with `Credentials` carved out so that \"a wildcard-class grant deliberately does NOT cover it — opening credentials takes an explicit credentials grant.\" The gate is not advisory: the read receipt has a field for \"[h]ow many scope-visible items the purpose gate suppressed\", so suppression is a counted outcome of a read rather than a hope | crates/mind-memory/src/lib.rs:7949-7952 is the red-team test over exactly these two axes, and the `Scope` doc comment points at a second one by name, the surprise-gift adversarial test"
  negative_eval: "a red-team test demanding zero unauthorized hydrations on every read path and in every background lane | crates/mind-memory/src/lib.rs:7947-7966 | `purpose_gate_redteam_zero_unauthorized_hydrations` is committed, multi-threaded, and asserts the absence rather than the presence: the gate must \"produce ZERO unauthorized hydrations across the cross-owner and sensitive-class corpora — on every read path, in every background lane.\" The two corpora are what make it a real test rather than a smoke check — cross-owner exercises `Private(a)` against `Private(b)`, and sensitive-class exercises the health, finance and credentials policies — and \"every background lane\" is the clause that matters most, because the dream, proactive and research lanes are the readers a purpose audit exists to catch and the easiest ones to forget. The `Scope` type names a second adversarial case by name, the surprise gift, which is the cross-owner leak in its most concrete form | the receipts module makes the same argument from the audit side: operator reads \"used to be exempt ('the trusted owner path')\", and the exemption was removed because those lanes \"are exactly the cross-subject reads a purpose audit exists to catch, so a ledger blind to them would be theater\""
stack_storage: "delegated"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A typed belief in YantrikDB — statement, polarity, weight, source event and provenance, with Bayesian confidence, evidence trails and contradiction edges held by the engine — carrying a scope and a sensitivity class assigned by this layer"
  storage: "Delegated to YantrikDB, pinned as a published crate at an exact version rather than a path checkout; a hash-chained JSONL receipts ledger sits beside it"
  retrieval: "Semantic recall blended with a confidence prior, through a facade that applies scope and the purpose gate before results cross the boundary"
  write: "Conversation turns consolidated into durable typed beliefs, asserted through the engine's `assert_belief_evidence`"
  update_delete: "Belief revision is Bayesian and lives in the engine; contradictions are detected and surfaced as a question rather than resolved by this layer"
  scoping: "`Shared` or `Private(owner)` stored on the belief, with four sensitivity classes carrying default-deny purpose policies and a credentials class no wildcard grant covers"
  integration: "Nineteen crates across one workspace — agents, conversation, cortex, governance, instincts, perception, proactive, world — with clients and deploy directories beside them"
  background: "Dream, proactive and research lanes, each of which reads memory and each of which is receipted"
  trust: "Confidence and evidence trails in the engine, a purpose gate with counted suppressions in this layer, and a hash-chained read ledger with no exempt caller"
  strengths: "Two things, and the first is a dependency line. `yantrikdb-core` carries roughly thirty lines of comment explaining why it is an exact version pin on a published crate and not a path dependency: a path dep into `../yantrikdb` \"built the mind against whatever that tree happened to contain - it sat at 0.16.0 with uncommitted changes - so no one else could reproduce this build and it moved under us whenever someone worked there.\" It explains why the `=` matters — \"`version = \\\"0.18\\\"` is caret `^0.18` to Cargo, so … a future 0.18.1 could have changed the substrate silently\" — records the resolved artifact with its checksum, and then documents the later upgrade by re-checking, against the published crates rather than a source tree, the two properties the pin was chosen for, including replaying `assert_belief_evidence` on a store created by the old version and migrated by the new one for \"identical priors, posteriors and effective weights to six decimals, against both same-version controls.\" The second is the removal of an exemption: operator reads were once outside the audit, and the receipts module argues the exemption away because the operator's background lanes \"are exactly the cross-subject reads a purpose audit exists to catch, so a ledger blind to them would be theater\""
  risks: "The reproducibility argument is made for one dependency and not applied to the other three: `yantrik-ml`, `yantrik-os` and `yantrik-chat` are still `path = \"../yantrik-companion/crates/…\"`, which is exactly the arrangement the comment above them argues against, so the build still depends on a sibling checkout nobody else has. The comment block's opening sentence also still reads \"pinned to standalone yantrikdb 0.18.0\" while the requirement below it is `=0.21.2`; the move is documented further down in the same block, so this is a stale first line rather than a false claim, and it is the kind of drift the block itself is written to prevent. There is no licence file, so the terms of reuse are unstated. What the store actually does — typed beliefs, Bayesian revision, contradiction detection — belongs to the YantrikDB engine rather than to this repository, and a reader evaluating the belief model should read it there; `mind-memory` is a facade, a purpose gate and a receipts ledger over someone else's substrate. The read ledger is a retrieval record and not a mutation one, so it does not answer what changed; and run detritus is committed at this pin, including SQLite write-ahead files from two smoke databases and a `grep.exe.stackdump`"
---

## 1. Executive Summary

yantrik-mind is "[a] ground-up Rust AI companion built on the YantrikDB
typed-memory moat" — no licence file, 203,205 lines of Rust across 226 files in
nineteen crates. Its claim is about the memory model rather than the assistant:
"[i]t stores *beliefs* — typed, revisable nodes with Bayesian confidence scores,
evidence trails, and contradiction edges — in YantrikDB's cognitive graph", and
when two beliefs conflict "the companion asks rather than asserting either
side."

That model belongs to the engine. This report is about what the companion adds
on top of it, and the addition is a **purpose gate**.

**Scope is stored on the belief and the migration default fails safe.** `Scope`
is `Shared` or `Private(person_id)`, and the type's comment states the rule
plainly — a fact "from one person must NEVER surface to another" — while the
default for pre-existing data goes the careful way: "[l]egacy/untagged memory is
private to them, so pre-multi-user facts never leak to a later-added member."
Most systems make unlabelled rows visible to everyone, which is the same
decision taken in the direction that is easier to ship.

**Sensitivity is default-deny.** Four classes carry purpose policies — "default
deny outside their allowed activities, whoever the fact belongs to" — and
`Credentials` is deliberately excluded from wildcard grants: "opening
credentials takes an explicit credentials grant."

**The audit has no exempt caller, and the reasoning for that is the best
sentence in the tree.** Operator reads were once outside the ledger, on the
"trusted owner path". The exemption was removed:

> "the operator's background lanes (dream/proactive/research/…) are exactly the
> cross-subject reads a purpose audit exists to catch, so a ledger blind to them
> would be theater. Every context is receipted now."

Each receipt records who read, through which facade method, for what declared
purpose, what they asked, how many results crossed the boundary, and how many
the gate suppressed — hash-chained so "[a]ny edit, reorder, or deletion of a
middle line breaks every later chain value." It is a record of reads rather than
of mutations, which is why it does not carry this atlas's audit mark, and it is
the half of that pattern most systems do worse.

**And a red-team test holds the whole arrangement.**
`purpose_gate_redteam_zero_unauthorized_hydrations` asserts "ZERO unauthorized
hydrations across the cross-owner and sensitive-class corpora — on every read
path, in every background lane."

**The other thing to read here is a dependency line.** `yantrikdb-core` carries
about thirty lines of comment explaining why it is an exact version pin on a
published crate rather than a path dependency — because a path dep into
`../yantrikdb` "built the mind against whatever that tree happened to contain -
it sat at 0.16.0 with uncommitted changes - so no one else could reproduce this
build and it moved under us whenever someone worked there." The upgrade to a
later engine is documented in the same block by re-checking the properties the
pin was chosen for against the published crates, including replaying
`assert_belief_evidence` across the migration for "identical priors, posteriors
and effective weights to six decimals."

The gap is that the argument stops at one line. `yantrik-ml`, `yantrik-os` and
`yantrik-chat` are still path dependencies into a sibling workspace — the exact
arrangement the comment above them rejects.

## 2. Mental Model

A **belief** lives in the engine; a **scope** and a **sensitivity** are what this
layer puts on it.

A **purpose** is declared by the reader and checked against the class.

A **suppression** is counted, not silent.

A **receipt** covers every read, including the owner's.

```mermaid
%% caption: the belief store is delegated to a pinned engine while this layer adds a stored scope and sensitivity class, a default-deny purpose gate whose suppressions are counted, and a hash-chained receipt for every read with no exempt caller
flowchart TB
    TURN["a conversation turn"] --> CONS["consolidation into durable typed beliefs"]
    CONS --> ENG[("YantrikDB — pinned as a PUBLISHED crate at an exact version:<br/>typed beliefs, Bayesian revision, evidence trails,<br/>contradiction edges")]
    PIN["=0.21.2, not ^0.21, not a path dep"] -.->|"a path dep into ../yantrikdb 'built the mind against<br/>whatever that tree happened to contain - it sat at 0.16.0<br/>with uncommitted changes - so no one else could<br/>reproduce this build'"| ENG
    PIN -.->|"the upgrade was justified by replaying assert_belief_evidence<br/>across the migration: identical priors, posteriors and effective<br/>weights to six decimals, against both same-version controls"| ENG
    CONS --> TAG["this layer tags each belief:<br/>Scope = Shared or Private(owner)<br/>Sensitivity = Ordinary, Health, Finance, Credentials"]
    TAG -.->|"legacy untagged memory is private to the primary,<br/>'so pre-multi-user facts never leak to a later-added member'"| SAFE["the migration default fails safe"]
    READ["a read, from a lane or from the owner"] --> FACADE["the memory facade"]
    FACADE --> GATE{"purpose gate: does this declared purpose<br/>clear this sensitivity class?"}
    GATE -->|"default deny outside the class's allowed activities,<br/>whoever the fact belongs to"| DENY["suppressed"]
    GATE -->|"Credentials, under a wildcard grant"| DENY2["still denied — it takes an<br/>explicit credentials grant"]
    GATE -->|"cleared"| OUT["results cross the boundary"]
    DENY & DENY2 & OUT --> REC[("receipts.jsonl — who read, which facade method,<br/>declared purpose, the query, how many crossed,<br/>how many were suppressed")]
    REC -.->|"chain = sha256(prev_chain ++ record), first off 'genesis' —<br/>any edit, reorder or deletion breaks every later value"| TAMPER["tamper-evident"]
    OPER["the operator's own lanes:<br/>dream, proactive, research"] --> FACADE
    OPER -.->|"these used to be exempt as 'the trusted owner path';<br/>the exemption was removed because they 'are exactly the<br/>cross-subject reads a purpose audit exists to catch,<br/>so a ledger blind to them would be theater'"| REC
    TEST["purpose_gate_redteam_zero_unauthorized_hydrations"] -.->|"ZERO unauthorized hydrations across the cross-owner AND<br/>sensitive-class corpora, on every read path,<br/>in every background lane"| GATE
    PATHS["yantrik-ml, yantrik-os, yantrik-chat —<br/>still path deps into ../yantrik-companion"] -.->|"the argument that produced the engine pin<br/>was not applied to these three"| ENG
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `Cargo.toml:28-56` | The engine pin, and thirty lines on why it is what it is |
| `crates/mind-types/src/memory.rs` | `Scope`, and the leak it exists to prevent |
| `crates/mind-types/src/purpose.rs` | Sensitivity classes and their default-deny policies |
| `crates/mind-memory/src/lib.rs` | The facade, the gate, and the red-team test |
| `crates/mind-memory/src/receipts.rs` | A hash-chained ledger with no exempt caller |
| `crates/mind-governance/`, `mind-evals/` | Egress and device policy, and the immune ledger the chain mirrors |

## 4. Essential Implementation Paths

`Cargo.toml:28-56` — why the engine is a published pin, and what the upgrade had
to prove.

`crates/mind-types/src/memory.rs:218-236` — a two-value scope and a safe legacy
default.

`crates/mind-types/src/purpose.rs:140-153` — four classes, default deny, and one
that wildcards cannot reach.

`crates/mind-memory/src/receipts.rs:1-14` — the exemption that was removed, and
why.

`crates/mind-memory/src/lib.rs:7947-7966` — zero unauthorized hydrations, on
every path, in every lane.

## 5. Memory Data Model

The belief itself — statement, polarity, weight, source event, provenance, and
the engine's confidence, evidence and contradiction structure — belongs to
YantrikDB and is described in [YantrikDB Engine](../yantrikdb-engine/). What
this repository contributes to the unit is the pair of handling attributes: a
scope naming whose fact it is, and a sensitivity class naming what may be done
with it.

## 6. Retrieval Mechanics

Semantic recall blended with a confidence prior, through a facade that applies
the scope filter and then the purpose gate, counting what it suppressed before
anything crosses the boundary.

## 7. Write Mechanics

Conversation turns are consolidated into durable typed beliefs asserted through
the engine's `assert_belief_evidence`. Contradiction detection belongs to the
engine; this layer's stated behaviour on a conflict is to ask rather than to
pick a side.

## 8. Agent Integration

Nineteen crates covering agents, conversation, cortex, governance, identity,
inference, instincts, perception, proactive lanes, recipes, tools and a world
model, with client and deploy directories beside them.

## 9. Reliability, Safety, and Trust

The strong parts are the default-deny sensitivity policies, the safe legacy
scope default, the unexempted read ledger and the red-team test. The weak parts
are three path dependencies that undo the reproducibility the engine pin buys,
an absent licence, and committed run artefacts including two smoke databases'
write-ahead files.

## 10. Tests, Evals, and Benchmarks

A `mind-evals` crate with an immune ledger whose chain discipline the receipts
module mirrors, plus in-tree adversarial tests — the purpose-gate red team over
cross-owner and sensitive-class corpora, and a surprise-gift case the `Scope`
type names directly.

## 11. For Your Own Build

Pin the engine you delegate to, exactly, on a published artifact — and write down
why. The comment on that one line is worth more than most changelogs: it records
the failure that produced the pin, the caret trap, the resolved checksum, and
what the later upgrade had to prove.

When you widen a data model to more than one owner, make the untagged rows
private rather than shared. The convenient default is the one that leaks.

Delete the audit exemption for the trusted caller. The lanes you trust are the
ones that read across subjects, and a ledger without them measures the wrong
half.

Count your suppressions. A gate whose refusals are invisible cannot be told from
a gate that never fired.

## 12. Open Questions

Whether the three remaining path dependencies are intended. The argument against
them is written directly above them, applied to a fourth, and a reader will
wonder whether the other three were judged different or simply not revisited.

Whether the read ledger will be joined by a mutation one. Everything about the
receipts design — the chain, the removed exemption, the counted suppressions —
would transfer to belief writes, and what changed a belief is currently the
engine's business rather than this layer's record.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `Cargo.toml:28-56` | Thirty lines on one dependency, and worth every one |
| `crates/mind-types/src/memory.rs:218-236` | A migration default chosen in the safe direction |
| `crates/mind-types/src/purpose.rs:140-153` | Default-deny classes, and one no wildcard covers |
| `crates/mind-memory/src/receipts.rs:1-14` | Why the trusted caller lost its exemption |
| `crates/mind-memory/src/lib.rs:7947-7966` | Zero unauthorized hydrations, stated as a test |

## History

**2026-09-16** — [`97935b1e247167ac7d4fe192ec8a9a1966b26c49`](https://github.com/yantrikos/yantrik-mind/commit/97935b1e247167ac7d4fe192ec8a9a1966b26c49) — first reading, at a commit dated 8 September 2026. Screened before opening, from a shallow clone: twenty-seven files scanned, no auto-run surfaces, two build-time execution points, no unpinned dependency surfaces and nothing inside the seven-day cooldown, with `Cargo.lock` tracked and unchanged for eight days. Reviewed **without a licence file**, so nothing here should be taken as a statement about reuse terms. The belief engine it delegates to is a published crate rather than a checkout and was not cloned for this reading; its model is covered separately. Nothing was installed, built or run.

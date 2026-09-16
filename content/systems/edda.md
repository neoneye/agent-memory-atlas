---
title: "Edda"
eyebrow: "An approval cannot be banked before the gate opens"
description: "A tamper-evident local ledger for coding agents whose hash chain is enforced on append and verified in both directions, whose capability material is deliberately kept out of the events, and whose approvals bind to a subject, a commit and a time window."
root: ../..
page_kind: system
source_name: "fagemx/edda"
source_url: https://github.com/fagemx/edda
archive_name: "fagemx--edda"
revision: ce8b98e0b41b832da71b46a6d87289184a158f6a
revision_url: https://github.com/fagemx/edda/commit/ce8b98e0b41b832da71b46a6d87289184a158f6a
analyzed_at: 2026-09-16
capabilities: "audit_log"
capability_evidence:
  audit_log: "the store is an append-only event log whose chain is validated on every append and verifiable afterwards in both directions — each event's own hash over its canonical content, and its link to the previous one | crates/edda-ledger/src/sqlite_store/events.rs:16-49, :951-993 | `validate_event_for_append` runs on every insert: it validates the payload, reads the current tail's hash and requires the incoming event's parent to match it, then calls `validate_event_hash`, which re-derives the event canonically and rejects it if the taxonomy, hash or digests differ — so a chain break cannot be written, not only detected later. `verify_chain` then walks the whole log, requiring the first event to have no parent and every later parent to equal its predecessor's hash, and reports \"the first break found\" by event id and index. Four tests inject real corruption through raw SQL and assert detection: a broken parent hash, a first event that has a parent, a tampered payload, and a tampered taxonomy | crates/edda-ledger/src/sqlite_store/tests.rs:1575, :1834, :1856, :1881"
stack_storage: "sqlite, files"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "An event in an append-only ledger under `.edda/`, carrying a family, a level, a payload, digests, its own hash and its parent's; decisions, tasks, verdicts and review artifacts are event kinds"
  storage: "SQLite for the event log and its projections, with a content-addressed blob store beside it for anything large"
  retrieval: "Full-text search over the ledger, plus projections the events are folded into"
  write: "Every mutation is an appended event, validated against the current tail before it lands"
  update_delete: "State changes are new events; blob deletion appends a tombstone record naming the hash, the reason, the last known class and whether it was pinned"
  scoping: "One `.edda/` workspace per repository; authority is a registered actor with a live session, an RBAC grant and an HMAC-sealed local capability"
  integration: "A CLI and MCP surface for Claude Code, Cursor, Codex and OpenClaw, plus a bridge crate and a conductor that coordinates parallel agents"
  background: "A conductor driving phases and waiting at gates, garbage collection with quota enforcement, and a postmortem crate"
  trust: "A chain enforced at append time, capability material held outside the ledger, verdicts bound to a subject, a commit and a freshness window, and a second-provider review that records what it measured"
  strengths: "Three decisions are worth the visit. The chain is enforced where it is cheapest to enforce — on append, by reading the tail and refusing an event whose parent does not match — rather than only verified by a later pass, and `validate_event_hash` re-derives the event canonically so a tampered taxonomy is caught alongside a tampered payload; four tests inject the corruption through raw SQL and assert which break is reported. The authority module states its threat model in the header, treats \"issue text, manifests, events, environment values, and portable/imported bytes\" as untrusted, keeps \"[t]he root key, capability record, and bearer … outside ledger events and continuity bundles\" so writing memory cannot mint authority, enforces owner-only permissions before any secret byte is read or written, fails closed on Windows \"until a reviewed safe owner-only storage abstraction is available\", and names what it does not cover: \"[a] malicious process already running as that same owner remains outside S6a's boundary\". And a verdict binds three ways — to the subject, to the full commit SHA, and to the moment: \"a verdict only satisfies a gate if it postdates the gate's `gate_entered_at`. Approving a subject BEFORE its gate opens (a pre-recorded verdict) therefore does not work\", which closes the pre-approval an agent would otherwise bank in advance"
  risks: "The approver is a label. `edda verdict approve|reject` records an `actor` string supplied by the caller, with no authentication on that path and no requirement that the sealed capability be held — so the gate genuinely blocks the conductor until something outside it responds, and what responded is self-asserted. That is why this report claims no human-review mark: the binding and freshness rules are the best half of such a gate and the identity half is absent. The blob tombstones are likewise a record rather than a rule: they are keyed on the content hash and carry the deletion reason, but their only reader is `edda blob tombstones`, an inspection command — nothing consults them when the same bytes are written again. Nothing in the ledger is epistemic: there is no status, confidence or provenance class on a memory, and a decision and the later one that reverses it are two events with no relation between them beyond order. At 213,521 lines of Rust across a dozen crates — an 80,675-line CLI among them — the ledger a reader came for is a tenth of the tree"
---

## 1. Executive Summary

Edda is "a local, tamper-evident ledger for coding agents: decisions that survive
sessions, and coordination that survives agents" — MIT or Apache-2.0, Rust,
version 0.6.2, 213,521 lines across a dozen crates with 3,518 test functions, on
crates.io, working with Claude Code, Cursor, Codex, OpenClaw and any MCP client.

It names the two failures it exists for precisely. "The session dies, and the
decisions die with it" — one session settles on SQLite, the next one
proposes Postgres again, "[t]he reasoning died with the transcript, and
compaction can't bring it back." And "[t]he agent dies, and the work state dies
with it" — one of three parallel sessions crashes mid-task and you reconstruct by
hand what it had finished. Both get the same primitive: append-only state in
`.edda/` that outlives any session, agent or tool.

**The chain is enforced on append, not just verified afterwards.** Every insert
runs `validate_event_for_append`: validate the payload, read the current tail's
hash, refuse the event if its parent does not match, then re-derive the event
canonically and reject it if its taxonomy, hash or digests differ from what the
content implies. A broken chain cannot be written. `verify_chain` then walks the
whole log — first event must have no parent, every later parent must equal its
predecessor's hash — and reports "the first break found" with the event id and
index.

The tests do the part that makes this checkable rather than claimed. Four inject
real corruption through raw SQL against a live store and assert detection: a
broken parent hash, a first event that has a parent, a tampered payload, and a
tampered taxonomy. A hash chain whose failure modes are tested by breaking it is
a different artifact from one that is only computed.

**Capability material is deliberately not in the ledger.** The authority module
opens with its threat model, and it is the right one for a memory system:

> "Threat model: issue text, manifests, events, environment values, and
> portable/imported bytes are untrusted. Authority requires a registered actor, a
> live registered session at issuance/use, an explicit RBAC grant, and possession
> of this local HMAC-sealed capability's private bearer. The root key, capability
> record, and bearer are outside ledger events and continuity bundles."

Because the bearer lives outside the events, an agent that can write memory
cannot write itself authority — the same separation [Anda DB](../anda-db/) states
as "[c]ognitive content may describe authority. Only this plane can grant it."
Edda adds file-permission enforcement before any secret byte moves, a
fail-closed Windows path "until a reviewed safe owner-only storage abstraction is
available", and — the mark of a real threat model — the thing it does not cover:
"[a] malicious process already running as that same owner remains outside S6a's
boundary".

**An approval cannot be banked before the gate opens.** A verdict binds three
ways. To the subject and to the full commit SHA — "a verdict recorded for one SHA
remains findable but never matches a query for another SHA" — and to time:

> "a verdict only satisfies a gate if it postdates the gate's `gate_entered_at`.
> Approving a subject BEFORE its gate opens (a pre-recorded verdict) therefore
> does not work — the gate ignores any verdict recorded before it entered
> `AWAITING_VERDICT`, even for the matching SHA."

Pre-recording approvals is exactly what an agent with a shell would do to get
past a gate it expects to meet, and the freshness rule closes it. Subject, commit
and window: three bindings, and the conductor prints the exact command to run so
the human step is one paste rather than a lookup.

What the gate does not have is an identity. `edda verdict approve|reject` records
an `actor` string the caller supplies, with no authentication on that path and no
requirement to hold the sealed capability the authority module went to such
lengths over. So the gate blocks the conductor until something outside it
responds, and what responded is self-asserted — which is why this report claims
the audit-log mark and not a human-review one. The binding and freshness halves
are the best in this corpus; the identity half is not there.

Two smaller notes. Blob tombstones are keyed on the content hash and carry the
deletion reason, the last known class and whether it was pinned — but their only
reader is `edda blob tombstones`, an inspection command, so they are a record of
what was deleted rather than a rule consulted when the same bytes return. And
nothing in the ledger is epistemic: no status, confidence or provenance class, so
a decision and the later one reversing it are two events whose only
relation is order.

The other half of the product is `edda review`: run a *second* provider over the
committed branch — "after authoring with Claude Code, use pi with an OpenAI
reviewer" — and record the reviewed SHA, the reviewer session, the observed
model, the findings, and "measured or unmeasured cost". That last distinction is
the kind this atlas looks for: a cost field that admits when it was not measured
beats one that guesses.

## 2. Mental Model

An **event** is the unit, and it knows its own hash and its parent's.

A **verdict** is about one subject, at one commit, after one moment.

**Authority** is not something the ledger can contain.

A **tombstone** says what left and why, and is read by a person.

```mermaid
%% caption: the chain is checked when an event is appended, not only by a later pass; a verdict must match the subject, the SHA, and postdate the moment the gate opened
flowchart TB
    W["any mutation — a decision, a task action,<br/>a review artifact, a verdict"] --> APP["validate_event_for_append"]
    APP --> P1["validate the readable payload"]
    APP --> P2{"does the event's parent match<br/>the current tail's hash?"}
    P2 -->|"no"| REJ["refused — a chain break<br/>cannot be written"]
    P2 -->|"yes"| P3["validate_event_hash: re-derive canonically;<br/>reject if taxonomy, hash or digests differ"]
    P3 --> LOG[("append-only events in .edda/,<br/>with a content-addressed blob store<br/>for anything large")]
    LOG --> VER["verify_chain: first event has no parent,<br/>every later parent equals its predecessor's hash —<br/>reports the FIRST break by event id and index"]
    VER -.->|"four tests inject corruption via raw SQL:<br/>broken parent · first event with a parent ·<br/>tampered payload · tampered taxonomy"| PROOF["failure modes tested by causing them"]
    GATE["conductor reaches a gate:<br/>AWAITING_VERDICT"] --> WAIT{"a verdict.recorded event that…"}
    WAIT -->|"…names this subject"| B1
    WAIT -->|"…names this full SHA"| B2
    WAIT -->|"…postdates gate_entered_at"| B3
    B1 & B2 & B3 --> PASS["gate satisfied"]
    PRE["a verdict recorded BEFORE the gate opened"] -.->|"ignored, even for the matching SHA —<br/>an approval cannot be banked in advance"| WAIT
    ACT["the actor field is a label the caller supplies —<br/>no authentication on this path"] -.-> WAIT
    AUTH[("root key · capability record · bearer —<br/>HMAC-sealed, owner-only file permissions,<br/>OUTSIDE ledger events and continuity bundles")] -->|"so writing memory cannot mint authority"| CAP["authority = registered actor + live session<br/>+ RBAC grant + possession of the bearer"]
    AUTH -.->|"stated, not implied: 'a malicious process already<br/>running as that same owner remains outside<br/>S6a's boundary'"| LIMIT["the threat model names its own edge"]
```

## 3. Architecture

| Crate | Role |
| --- | --- |
| `edda-cli` | The commands, including review, verdict, gc and blob (80,675 lines) |
| `edda-ledger` | Events, the chain, tombstones, verdicts, control authority (22,560) |
| `edda-conductor` | Phases, gates, and coordination across parallel agents (22,736) |
| `edda-bridge-claude` | The harness bridge (33,629) |
| `edda-core` | Event types, policy, guided execution (11,411) |
| `edda-serve`, `edda-ask`, `edda-search-fts`, `edda-postmortem` | Serving, asking, search, postmortems |

## 4. Essential Implementation Paths

`crates/edda-ledger/src/sqlite_store/events.rs:16-49` — the append-time check.

`crates/edda-ledger/src/sqlite_store/events.rs:951-993` — the after-the-fact
walk, and what it reports.

`crates/edda-ledger/src/control_authority.rs:1-14` — a threat model that names
its own edge.

`crates/edda-cli/src/cmd_verdict.rs:1-15` — three bindings on an approval.

## 5. Memory Data Model

An event with a family, a level, a payload, digests, its hash and its parent's.
Decisions, tasks, verdicts and review artifacts are event kinds rather than
tables, so the ledger is the state and the projections are folds over it. Large
payloads go to a content-addressed blob store with a class and a pin flag, and a
size threshold decides which.

## 6. Retrieval Mechanics

Full-text search over the ledger plus projections. Retrieval is not where this
system's thinking went; durability and coordination are.

## 7. Write Mechanics

One path, checked before it lands. The payload validation includes secret
redaction on the `verdict.recorded` write path, which is the right place for it —
a verdict quotes findings, and findings quote code.

## 8. Agent Integration

A CLI and MCP surface across four harnesses, plus a conductor for parallel
sessions and a second-provider review flow. The review command records what it
measured and marks what it did not, and `--spec` and declared `--gate` evidence
qualify the verdict rather than decorating it.

## 9. Reliability, Safety, and Trust

Covered above. The summary a reader needs: the integrity of the log is strong and
tested; the identity of whoever approves is not established; and the ledger holds
no epistemic state, so "which of these two decisions is current" is a question
the reader answers from order alone.

## 10. Tests, Evals, and Benchmarks

3,518 test functions, including the four fault-injection tests on the chain.
Nothing was built or run for this reading.

## 11. For Your Own Build

Check the chain when you append, not only when you audit. Reading the tail and
refusing a mismatched parent costs one query and turns a detectable corruption
into an impossible one.

Break your own chain in a test. Four tests that corrupt a payload, a parent, a
taxonomy and a first event through raw SQL are what separate a hash chain from a
hash column.

Keep the capability outside the log. If authority material can be written by the
thing that writes memory, then memory is an authority-granting surface, whatever
the policy says.

Bind an approval to a subject, a content hash *and* a moment. Two of the three
lets an agent pre-record the approval it knows it will need.

And when you record a cost, record whether you measured it. "Measured or
unmeasured" is one extra field and the difference between a number and a guess.

## 12. Open Questions

Whether a verdict's actor can be established. The authority module has the
machinery — registered actors, sessions, RBAC, a sealed bearer — and the verdict
path does not use it.

Whether anything consults a blob tombstone on write. The record is keyed on the
content hash, which is what such a check would need, and only an inspection
command reads it.

How a contradicted decision is found. Events are ordered and nothing relates one
decision to the one it reverses.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `crates/edda-ledger/src/sqlite_store/events.rs:16-49` | A chain break that cannot be written |
| `crates/edda-ledger/src/sqlite_store/tests.rs:1575-1890` | Four ways to corrupt it, all asserted |
| `crates/edda-ledger/src/control_authority.rs:1-14` | What is untrusted, and what is not covered |
| `crates/edda-cli/src/cmd_verdict.rs:1-15` | Subject, SHA, and the freshness rule |
| `crates/edda-ledger/src/tombstone.rs:6-41` | A deletion record, and its one reader |

## History

**2026-09-16** — [`ce8b98e0b41b832da71b46a6d87289184a158f6a`](https://github.com/fagemx/edda/commit/ce8b98e0b41b832da71b46a6d87289184a158f6a) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: forty-three files scanned, no auto-run surfaces, two build-time execution points, two unpinned surfaces and thirty-two dependency files inside the seven-day cooldown. Nothing was installed, built or run.

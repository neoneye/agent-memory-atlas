---
title: "AideMemo"
eyebrow: "The client says which project it wants; the type refuses to carry that claim into the store"
description: "A Rust working memory for coding agents where a mutation cannot reach any backend without a server-owned authorization, and the audit row committed beside it takes its tenant and actor from the server rather than the request."
root: ../..
page_kind: system
source_name: "taeyun16/aidememo"
source_url: https://github.com/taeyun16/aidememo
archive_name: "taeyun16--aidememo"
revision: 58b803cc6b717fbf6559303e0d3f08e8b75673d4
revision_url: https://github.com/taeyun16/aidememo/commit/58b803cc6b717fbf6559303e0d3f08e8b75673d4
analyzed_at: 2026-09-16
capabilities: "scope_enforced, audit_log"
capability_evidence:
  scope_enforced: "the scope a command runs under is server-owned, and the type system will not let an unauthorized envelope reach a backend | crates/aidememo-domain/src/command.rs:190-213, :244-250, crates/aidememo-domain/src/storage.rs:15-22 | `AuthorizedCommand` is documented as a \"[c]ommand paired with server-owned authorization context\", and its only constructor refuses the mismatch outright: `authorize()` returns `DomainError::ProjectScopeMismatch` \"when the untrusted envelope selects a different project\", naming the requested and the authorized project in the error. The enforcement is structural rather than procedural, because `MutationCommand` — the single thing `CommandStore::execute` accepts — carries `command: AuthorizedCommand<()>` as a field. A backend adapter therefore cannot be handed a mutation whose project came from the caller, and there is no unscoped path to write past: every adapter in the workspace implements the same trait. `CanonicalResource` then carries a `ProjectScope` described as \"[t]enant-project scope\", so the key travels with the state that replicas receive | crates/aidememo-domain/src/conformance.rs is a backend-neutral fixture every adapter runs, so the scope refusal is checked against each store rather than argued once in the abstraction"
  audit_log: "an immutable audit row written in the mutation's own transaction, whose tenant and actor are server-derived | crates/aidememo-domain/src/command.rs:239-243, :306-325 | `MutationCommand`'s own doc states the transactional requirement: adapters \"persist its canonical fingerprint, resource mutation, receipt, change entry, and audit entry in one transaction\", so a committed mutation without its audit row is not a state the storage contract permits. `AuditEntry` is \"[i]mmutable audit record committed with a mutation and its receipt\", carrying the project sequence, the originating idempotency key, the operation name, the mutated resource and a commit timestamp. The two fields that matter most are annotated with where they come from rather than what they hold: `tenant_id` is the \"[s]erver-derived tenant\" and `actor_id` is \"[s]erver-derived actor provenance\" — so the record of who changed a memory is not a string the caller supplied, which is the failure this atlas most often finds under an audit claim | `CommandReceipt` carries a `fingerprint` used \"to reject command-ID reuse with a different body\", so a replayed idempotency key with altered content is refused rather than quietly applied over the audited one"
stack_storage: "sqlite, postgres"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A canonical resource addressed by tenant, project and resource reference, carrying a revision and a state that is either a key-sorted JSON body or a durable deletion tombstone"
  storage: "One embedded local store or PostgreSQL behind one storage-neutral command trait, with a replica cache for clients"
  retrieval: "Facts, graph traversal and history over the canonical state, with a change feed replicas follow by cursor"
  write: "Every mutation is a command with an idempotency key and a canonical fingerprint, applied atomically with its receipt, change entry and audit entry"
  update_delete: "An upsert replaces the canonical body; a deletion writes a durable tombstone rather than removing the row, so replicas learn about it through the same change feed"
  scoping: "Tenant and project, bound by a server-owned `ProjectAuthorization` that the command type refuses to let a client override"
  integration: "One Rust binary with a CLI, an MCP server over stdio and HTTP, a Python agent SDK, and native bindings for Python, Node, Elixir and C"
  background: "None over memory; the change feed is pulled by replicas rather than pushed by a worker"
  trust: "Server-derived actor and tenant on every audit row, an actor kind that distinguishes a person from an agent, idempotency fingerprints that refuse a reused id with a different body, and a conformance fixture every backend must pass"
  strengths: "Two rules, both enforced by types rather than by review. The first is that the caller does not get to say what scope it is writing in: `AuthorizedCommand` pairs an envelope with a \"server-owned authorization context\" and refuses construction with `ProjectScopeMismatch` when \"the untrusted envelope selects a different project\", and because `MutationCommand` carries an `AuthorizedCommand` as a field, no backend can be handed an unscoped mutation at all. The second is that the audit row is not the caller's account of itself — `tenant_id` is the \"[s]erver-derived tenant\" and `actor_id` the \"[s]erver-derived actor provenance\" — and it is committed with the mutation, the receipt and the change entry \"in one transaction\", so an unaudited write is not a reachable state. Two smaller lines carry the same discipline. `ActorKind` separates `Human` (\"[i]nteractive person\") from `Agent` (\"[n]amed coding or reasoning agent profile\") and `Service`, so provenance records what kind of thing acted rather than only which id. And `display_name` is annotated \"[h]uman-readable label; never used for authorization\", which forecloses the rename-widens-access bug before anybody writes it"
  risks: "There is no epistemic state on a memory. `RecordStatus` — `Active`, `Suspended`, `Archived` — governs tenants, projects and actors rather than claims: `Suspended` \"does not grant access or accept mutations\" and `Archived` makes a project \"read-only and retained for export or audit\", so the vocabulary decides what an account may do and never whether a stored fact should be believed. Time is single-axis: records carry `created_at_ms`, `updated_at_ms` and a revision, with no field for when a claim was true as distinct from when it was written, so history here is a version chain over write time. The deletion tombstone is durable and replicated, which is right for convergence, and it is keyed on the resource rather than on the value — nothing stops the same content being written back afterwards, and no record says it was once removed. And the conformance fixture, which is the project's strongest quality instrument, checks command-level refusals — scope mismatch, stale revision, cursor range — rather than asserting that particular material fails to come back from a retrieval"
---

## 1. Executive Summary

AideMemo is "[p]ortable working memory for coding agents and orchestrators" —
MIT or Apache-2.0, Rust, version 0.1.0, 95,480 lines across 135 files in
thirteen crates, shipping "[o]ne Rust binary. One embedded store. A code-first
SDK, MCP tools, CLI, and native bindings."

**The mechanism to take away is where the project id comes from.** Almost every
multi-tenant store in this corpus accepts the caller's word for which tenant or
project a write belongs to, and then relies on a predicate somebody remembered
to add. AideMemo makes that impossible to express:

> "Command paired with server-owned authorization context."
>
> "Returns `DomainError::ProjectScopeMismatch` when the untrusted envelope
> selects a different project."

`AuthorizedCommand::authorize` is the only constructor, and it compares the
server's `ProjectAuthorization` against the envelope's `project_id` before
producing anything. The enforcement then rides the type: `MutationCommand` —
the single argument `CommandStore::execute` accepts — holds an
`AuthorizedCommand<()>` as a field, so a backend adapter cannot be handed a
mutation whose scope came from the request. There is no unscoped path to
forget, because there is no unscoped value to pass.

**The audit row follows the same rule, and it is transactional.** The storage
contract is stated on `MutationCommand` itself: adapters "persist its canonical
fingerprint, resource mutation, receipt, change entry, and audit entry in one
transaction." An `AuditEntry` is "[i]mmutable audit record committed with a
mutation and its receipt", and the two fields a reader should check are
annotated with their provenance rather than their contents — `tenant_id` is the
"[s]erver-derived tenant", `actor_id` the "[s]erver-derived actor provenance".
What is recorded is who the server determined acted, not who the request said
did.

**Two smaller lines carry the same instinct.** `ActorKind` distinguishes `Human`
— "[i]nteractive person" — from `Agent`, "[n]amed coding or reasoning agent
profile", and `Service`, so the audit can say what kind of thing made a change
and not only which identifier. And on the tenant record, `display_name` carries
the annotation `"Human-readable label; never used for authorization"`, which
closes the rename-widens-access bug in advance.

**What is absent is any judgement about the memories themselves.**
`RecordStatus` is `Active`, `Suspended`, `Archived`, and it governs accounts
rather than claims: a suspended record "does not grant access or accept
mutations", an archived project is "read-only and retained for export or audit".
Nothing in the model says a stored fact is doubtful, superseded or wrong, and
the only time fields are `created_at_ms`, `updated_at_ms` and a revision — a
version chain over write time with no second axis.

## 2. Mental Model

A **command** is authorized before it is a command.

A **scope** is what the server decided, never what the envelope asked for.

An **audit row** commits with the mutation or the mutation does not commit.

A **deletion** is a tombstone replicas receive, not a row that vanishes.

A **status** describes the account, not the claim.

```mermaid
%% caption: a client envelope is bound to a server-owned authorization before it can become a mutation, the type carrying that binding is the only thing a backend accepts, and the audit row with its server-derived tenant and actor commits in the same transaction as the change
flowchart TB
    CLIENT["a client envelope: project_id, command_id,<br/>precondition, payload — UNTRUSTED"] --> AUTHZ{"AuthorizedCommand::authorize(<br/>server ProjectAuthorization, envelope)"}
    SERVER["the server's own ProjectAuthorization"] --> AUTHZ
    AUTHZ -->|"authorization.project_id() != envelope.project_id"| REJECT["DomainError::ProjectScopeMismatch<br/>naming requested AND authorized"]
    AUTHZ -->|"they agree"| AC["AuthorizedCommand — the only way<br/>a scope becomes trusted"]
    AC --> MC["MutationCommand carries AuthorizedCommand<br/>as a FIELD, plus fingerprint, resource,<br/>change operation and canonical body"]
    MC -.->|"CommandStore::execute accepts only this type,<br/>so no adapter can be handed a mutation<br/>whose project came from the caller"| TYPED["the scope rule is a type, not a convention"]
    MC --> TX{"one transaction, per the storage contract"}
    TX --> R1[("canonical resource: ProjectScope · revision ·<br/>Present body or Deleted tombstone")]
    TX --> R2[("receipt: command_id + fingerprint")]
    TX --> R3[("change entry — replicas follow by cursor")]
    TX --> R4[("AuditEntry — IMMUTABLE")]
    R4 --> F1["tenant_id: SERVER-DERIVED tenant"]
    R4 --> F2["actor_id: SERVER-DERIVED actor provenance"]
    R4 --> F3["project_seq · command_id · operation ·<br/>resource · committed_at_ms"]
    F1 & F2 -.->|"who changed a memory is not a string<br/>the caller supplied"| HONEST["the audit cannot be authored by its subject"]
    R2 -.->|"fingerprint rejects command-ID reuse with a<br/>different body, so a replay cannot overwrite<br/>what was audited"| IDEM["idempotency with a tamper check"]
    ACTOR["ActorKind: Human, Agent, Service"] -.->|"provenance records WHAT KIND of thing acted,<br/>not only which id"| F2
    NAME["display_name: 'never used for authorization'"] -.->|"a rename can never widen access"| SERVER
    STATUS["RecordStatus: Active, Suspended, Archived"] -.->|"governs the tenant, project or actor —<br/>never whether a stored claim is true"| NOTS["no trust-state mark"]
    CONF["conformance.rs — one backend-neutral fixture<br/>every adapter must pass"] -.->|"the refusals are checked against each store<br/>rather than argued once in the abstraction"| TX
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `crates/aidememo-domain/command.rs` | Authorization binding, the mutation type, the audit record |
| `crates/aidememo-domain/conformance.rs` | The fixture every storage adapter must satisfy |
| `crates/aidememo-domain/record.rs` | Tenants, projects, actors, and what their statuses mean |
| `crates/aidememo-store-local`, `-store-postgres` | Two adapters behind one trait |
| `crates/aidememo-client` | The replica cache and its change cursor |
| `docs/MEASUREMENTS.md`, `benchmarks/` | The public measurement ledger and its evidence |

## 4. Essential Implementation Paths

`crates/aidememo-domain/src/command.rs:190-213` — the only way a scope becomes
trusted, and the error when it does not.

`:244-250` — the field that makes the rule unavoidable for every backend.

`:239-243` — the one-transaction storage contract, stated on the type it
governs.

`:306-325` — an audit record whose tenant and actor are server-derived.

`crates/aidememo-domain/src/record.rs:18-28`, `:36` — actor kinds, and a display
name barred from authorization.

## 5. Memory Data Model

A canonical resource keyed by tenant, project and resource reference, with a
revision and a state that is either recursively key-sorted JSON or a durable
deletion tombstone. Around it: commands with idempotency keys and canonical
fingerprints, receipts, change entries with a project sequence, and immutable
audit rows.

## 6. Retrieval Mechanics

Facts, graph traversal and history over canonical state, with replicas following
a change feed by cursor and a local cache materialising it. Cursor epoch and
range mismatches are refused with named errors rather than silently reset.

## 7. Write Mechanics

Every mutation carries an idempotency key and a fingerprint over "the real
project, precondition, operation, and payload". A retry with the same id and the
same body replays the stored receipt; a retry with the same id and a different
body is rejected. The mutation, its receipt, its change entry and its audit row
commit together.

## 8. Agent Integration

One binary serving a CLI and an MCP surface over both stdio and HTTP, a Python
agent SDK, and native bindings for Python, Node, Elixir and C — with a
`COMPARE.md` that sets itself against mem0, Graphiti and Letta by name.

## 9. Reliability, Safety, and Trust

The strong parts are the type-enforced scope, the transactional and
server-derived audit, the idempotency fingerprint, and a conformance fixture
that holds every backend to the same observable outcomes. The absent part is any
statement about the content: nothing marks a memory as stale, disputed or
corrected, and there is no second time axis to ask what was true rather than
what was written.

## 10. Tests, Evals, and Benchmarks

A backend-neutral conformance fixture that "describes outcomes, not I/O" and is
run by each adapter, an identity conformance suite beside it, a benchmarks tree,
and a public measurement ledger that states where durable numbers live and
deliberately ignores raw scenario output "because it contains temporary paths
and run-specific identifiers".

## 11. For Your Own Build

Make the authorized scope a different type from the requested one. A predicate
can be forgotten on one read path; a constructor that refuses a mismatched
envelope cannot, and a store that only accepts the authorized type has no
unscoped path left to audit.

Derive the audit's actor on the server. An audit row whose actor field is filled
in by the actor is a record of a claim, not of an act.

Put the transactional requirement on the type the adapters implement. "Persist
… in one transaction" written on the command struct is a contract every backend
author reads; the same sentence in a README is one they may not.

Annotate the fields that must never be used for authorization. `display_name:
"never used for authorization"` costs nothing and forecloses a whole class of
bug.

## 12. Open Questions

Whether a memory will ever carry a status of its own. Every guarantee here is
about who may write and what was written; none is about whether what was written
is still true, and a working memory for long-running agents eventually needs
that vocabulary.

Whether the conformance fixture will grow retrieval assertions. It is the right
instrument, already run against every backend, and it currently checks that bad
commands are refused rather than that withdrawn material stops coming back.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `crates/aidememo-domain/src/command.rs:190-213` | A scope the caller cannot assert |
| `:244-250` | Why no backend can be handed an unscoped mutation |
| `:306-325` | An audit row whose actor is derived, not declared |
| `crates/aidememo-domain/src/record.rs:36` | One annotation that forecloses a class of bug |
| `crates/aidememo-domain/src/conformance.rs:1-6` | One fixture, every storage backend |

## History

**2026-09-16** — [`58b803cc6b717fbf6559303e0d3f08e8b75673d4`](https://github.com/taeyun16/aidememo/commit/58b803cc6b717fbf6559303e0d3f08e8b75673d4) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: two auto-run surfaces, five build-time execution points, five unpinned dependency surfaces and twenty-seven dependency files inside the seven-day cooldown, with `Cargo.lock` present. `AGENTS.md` and `CLAUDE.md` are addressed to a reading agent and were recorded as data. Nothing was installed, built or run, and no benchmark was reproduced — the measurement ledger is cited as the project's own record rather than as a verified result.

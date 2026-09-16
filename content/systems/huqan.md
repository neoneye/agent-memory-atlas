---
title: "HUQAN"
eyebrow: "The approver identity never comes from the request that asks for approval"
description: "A local admission gate in front of agent memory and tool calls, where a write is held until an authenticated person decides, self-approval is refused on resolved identity, and every decision leaves a receipt."
root: ../..
page_kind: system
source_name: "ali-ulu/huqan"
source_url: https://github.com/ali-ulu/huqan
archive_name: "ali-ulu--huqan"
revision: 6f11b01476f019149cf5d56e961b5cb0b5d7a92e
revision_url: https://github.com/ali-ulu/huqan/commit/6f11b01476f019149cf5d56e961b5cb0b5d7a92e
analyzed_at: 2026-09-16
capabilities: "trust_state, scope_enforced, audit_log, human_review"
capability_evidence:
  human_review: "the approver is resolved from an authenticated context, never read out of the decision that claims it | lib/human-oversight-approval-runtime.js:10-15, :63, :78, :301, :348-354, :368-389 | this is the failure mode the atlas withholds this mark for, closed: \"The runtime never accepts an approver identity from the decision body. The receiver/operator supplies an authenticated context and the injected identity resolver turns that context into a receiver-owned identity result.\" `decide()` takes an `approverContext` rather than an approver id, `resolveIdentity` is a required injected function and the runtime refuses to construct without it, and \"[m]issing or ambiguous identity, stale state, scope drift, unavailable durability, and firewall disagreement all fail closed.\" Separation of duties is then enforced on the resolved identity rather than on a label: the approver is compared against the requester by both `identityRef` and `identityHash` and rejected with `SELF_APPROVAL_REJECTED` unless the policy explicitly allows it, an `override` is authorised only when the policy permits it *and* the firewall actually said block, and above the policy's critical risk score the runtime gathers prior decisions and keys them into a set so the same person cannot count twice toward a multi-approver requirement | escalation is a person's move and not a gate outcome — a reviewer may raise a case instead of deciding it, \"and nothing executes until the authority it was raised to answers\", which the README notes \"requires a second approver, so it is simply absent in a single-user install\""
  trust_state: "a frozen four-value admission vocabulary with a severity order, and a receipt kind per outcome | lib/memory-admission-gate.js:5-21, :265-275, README.md:44-48 | `MEMORY_ADMISSION_DECISIONS` is `Object.freeze(['allow', 'review', 'reject', 'quarantine'])` with `DECISION_SEVERITY` ordering them 0 through 3, so the vocabulary is closed in code rather than by convention and the comparisons between outcomes are defined rather than implied. The two outcomes a tool call cannot produce are exactly the two a write needs: the README explains that \"[a] memory write adds `quarantine` and `reject`, because a write can be set aside for inspection rather than refused outright\". A quarantined entry is held with its own `memory_quarantine_receipt` rather than landing, which is the withholding the mark is about — the content exists, it is inspectable, and it is not part of what the store will answer with | each decision emits its own receipt kind, so the difference between a refusal and a hold is durable rather than reconstructed from a log line"
  scope_enforced: "workspace is part of the storage key, with a separate gate for the crossing nobody should make by accident | lib/cross-workspace-access-gate.js:3-14, lib/human-oversight-approval-runtime.js:368-372 | \"[t]he graph already *stores* nodes and edges under a workspace scope (`nodeStorageKey` in graph.js)\", so the scope is the address rather than a predicate a query may forget, and `memory-admission-gate` checks the target workspace on a write. The cross-workspace gate exists for the question neither of those answers — \"an actor operating in workspace A is reaching into workspace B — should that be allowed at all?\" — and is written as a pure function over two workspace identifiers, an operation and an explicit grant list that \"reads and writes nothing\", so the isolation decision is testable without a store. The approval runtime carries the same key: when it counts distinct prior approvers for a critical-risk case it filters them to `decision.workspaceId === current.workspaceId`, so an approval earned in one workspace cannot be spent in another | the runtime's fail-closed list names `scope drift` alongside missing identity and stale state, so a case whose scope moved under it is refused rather than decided"
  audit_log: "a graph mutation journal and an evidence ledger the runtime commits through rather than beside | lib/human-oversight-approval-runtime.js:6-10, lib/graph-mutation-receipt-write.js, lib/graph-mutation-receipt-read.js, lib/graph-mutation-receipt-schema.js, lib/graph-mutation-rollback.js | the approval runtime is explicit that it is not a second store: \"This module is deliberately bounded. It does not implement a workflow suite, IAM provider, connector authorization system, or a second storage authority. Review cases and immutable transition snapshots are committed through the existing Graph mutation journal and Trust Evidence Ledger.\" Mutation receipts have their own schema, writer, reader and rollback path, and the runtime reads prior decisions back out of the journal by key prefix — `getCommittedMutationResultsByPrefix('human-oversight:approval-decision:')` — which is what makes the distinct-approver count a query over the durable record rather than over in-memory state. The Trust Receipt is the user-facing end of the same thing: \"what the evidence was, which policy applied, who approved it\" | the CLI quickstart ends on `receipt: receiptId … (status canonical)`, and the README's reading of its own transcript is the product statement — \"the write **did not happen**. It was held. It happened at line 3, after something approved it, and line 4 is the durable record of why\""
stack_storage: "graph, files"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "A proposed memory entry with its evidence, provenance and workspace scope, carried through admission as a review case and landing only as an approved node in the graph"
  storage: "A local graph whose node keys carry the workspace scope, with a mutation journal, a Trust Evidence Ledger and exportable Trust Receipts; no cloud and no API key"
  retrieval: "Verification, contradiction and risk checks over evidence rather than ranked recall; the product is the decision, and retrieval serves it"
  write: "Nothing lands directly — a write is proposed, gated, and either allowed, held for review, quarantined or rejected"
  update_delete: "Decisions are `approve`, `reject`, `expire`, `cancel`, `escalate` and `override`, each an immutable transition snapshot committed to the journal"
  scoping: "Workspace scope is part of the node storage key, checked on admission, and a separate pure gate decides whether an actor in one workspace may reach into another"
  integration: "Three binaries — a CLI, an MCP server over stdio, and a pre-execution guard for external agents — plus optional PDF ingest and receipt export"
  background: "None over memory; the gate runs synchronously in front of the write it governs"
  trust: "A frozen decision vocabulary with a severity order, resolved-identity approvals with separation of duties, a firewall whose block cannot be approved away, and receipts as the durable record"
  strengths: "One sentence in `lib/human-oversight-approval-runtime.js` closes the hole this atlas most often finds under a review claim: \"The runtime never accepts an approver identity from the decision body.\" `decide()` takes an authenticated `approverContext`, an injected `resolveIdentity` is required for the runtime to exist at all, and the resolved identity is what separation of duties is checked against — the approver is compared to the requester on both `identityRef` and `identityHash` and refused with `SELF_APPROVAL_REJECTED` unless a policy explicitly permits it, and above a critical risk score prior approvers are gathered from the mutation journal into a set so one person cannot satisfy a two-approver rule twice. Around that sit the same instincts: an `override` is authorised only when the policy allows it *and* the firewall actually returned block, an `approve` against a firewall block simply fails, and \"[m]issing or ambiguous identity, stale state, scope drift, unavailable durability, and firewall disagreement all fail closed.\" The module also refuses to grow — \"[i]t does not implement a workflow suite, IAM provider, connector authorization system, or a second storage authority\" — and commits its transitions through the journal that already exists"
  risks: "The scope question is what this is and what it therefore is not. HUQAN is an admission gate; retrieval quality, ranking and consolidation are not its subject, so a reader looking for how memory is recalled will not find much, and the graph behind the gate is thinner than the gate in front of it. The oversight machinery only pays for itself where there are two people: escalation \"requires a second approver, so it is simply absent in a single-user install\", and the distinct-approver rule above critical risk degenerates in the same setting — a solo operator gets the receipts and the refusals, not the separation of duties. `allowSelfApproval` and `allowOverride` are policy flags, so the guarantee is only as strong as the policy an installation ships. And the surface is very large for a gate: 287,058 lines across 1,563 JavaScript files at this pin, three binaries, optional PDF paths, and dependency files inside the seven-day cooldown"
---

## 1. Executive Summary

HUQAN is a decision gate rather than a memory: "An agent proposes something.
HUQAN decides whether it lands." AGPL-3.0, JavaScript, 287,058 lines across
1,563 files, Node 22.13 or newer, three binaries — a CLI, an MCP server, and a
pre-execution guard for external agents. "No model, no cloud, no API key."

It is in this atlas because one of the things it gates is a memory write, and
because the outcomes it can return for a write are not the ones it returns for a
tool call:

> "A memory write adds `quarantine` and `reject`, because a write can be set
> aside for inspection rather than refused outright."

The README reads its own quickstart transcript back to make the point: "the
write **did not happen**. It was held. It happened at line 3, after something
approved it, and line 4 is the durable record of why. That gap is the entire
product."

**The mechanism to take away is one sentence, and it closes a hole this atlas
finds repeatedly.** Across the corpus, systems that claim human review usually
record an `actor` or an `approved_by` string that the calling code fills in — so
what is stored is who the request *said* approved it. HUQAN refuses that
construction:

> "The runtime never accepts an approver identity from the decision body. The
> receiver/operator supplies an authenticated context and the injected identity
> resolver turns that context into a receiver-owned identity result. Missing or
> ambiguous identity, stale state, scope drift, unavailable durability, and
> firewall disagreement all fail closed."

`decide()` takes an `approverContext`. `resolveIdentity` is a required injected
function and the runtime will not construct without it. Separation of duties is
then checked on the resolved identity rather than on a label: the approver is
compared to the requester on both `identityRef` and `identityHash` and rejected
with `SELF_APPROVAL_REJECTED` unless the policy explicitly allows it, and above
the policy's critical risk score the runtime pulls prior decisions out of the
mutation journal and keys them into a set, so the same person cannot count twice
toward a two-approver requirement.

**The refusals compose the way they should.** An `override` is authorised only
when the policy allows it *and* the firewall actually returned block. An
`approve` against a firewall block fails outright. A decision on a case whose
status is no longer `pending`, `escalated` or `blocked` is refused as duplicate
or ambiguous.

**And the module declines to become a platform.** "This module is deliberately
bounded. It does not implement a workflow suite, IAM provider, connector
authorization system, or a second storage authority. Review cases and immutable
transition snapshots are committed through the existing Graph mutation journal
and Trust Evidence Ledger."

## 2. Mental Model

A **proposal** is not a write; the write is what happens after someone decides.

An **approver** is a resolved identity, never a name in the request.

A **quarantine** is a hold with a receipt, not a refusal.

An **escalation** is a person declining to decide, and it stops everything.

A **receipt** is the durable answer to why.

```mermaid
%% caption: a proposed memory write passes evidence, verification and policy before an approval runtime that resolves the approver from an authenticated context rather than from the request, refuses self-approval on resolved identity, and commits every transition to the existing journal
flowchart TB
    AGENT["an agent proposes a memory write"] --> PIPE["evidence + provenance + workspace scope<br/>→ verification, contradiction, risk<br/>→ policy and approval boundary"]
    PIPE --> DEC{"MEMORY_ADMISSION_DECISIONS<br/>frozen: allow · review · quarantine · reject<br/>severity 0 · 1 · 2 · 3"}
    DEC -->|"allow"| LAND[("the graph — nodes keyed under<br/>a workspace scope (nodeStorageKey)")]
    DEC -->|"quarantine"| HOLD["set aside for inspection,<br/>with a memory_quarantine_receipt"]
    DEC -->|"reject"| NO["refused outright"]
    DEC -->|"review"| CASE["a review case, pending"]
    CASE --> D{"decide: caseId, decisionType, approverContext"}
    CTX["an authenticated context"] --> RES["the injected resolveIdentity turns it into<br/>a receiver-owned identity result"]
    RES --> D
    D -.->|"'the runtime never accepts an approver identity<br/>from the decision body' — and resolveIdentity is<br/>required for the runtime to construct at all"| KEY["who approved is resolved, not asserted"]
    D -->|"approver identityRef or identityHash<br/>matches the requester"| SELF["SELF_APPROVAL_REJECTED<br/>unless policy.allowSelfApproval"]
    D -->|"override without policy.allowOverride,<br/>or without an actual firewall block"| OVR["OVERRIDE_NOT_AUTHORIZED"]
    D -->|"approve while the firewall says block"| FW["BLOCKED_BY_FIREWALL"]
    D -->|"status is not pending, escalated or blocked"| DUP["DUPLICATE_OR_AMBIGUOUS_DECISION"]
    D -->|"risk at or above policy.criticalRiskScore"| MULTI["prior approvers pulled from the journal,<br/>filtered to this workspaceId, keyed into a set —<br/>one person cannot count twice"]
    D -->|"reviewer escalates instead of deciding"| ESC["nothing executes until the authority<br/>it was raised to answers"]
    MULTI & SELF & OVR & FW & DUP --> FAIL["missing or ambiguous identity, stale state,<br/>scope drift, unavailable durability and firewall<br/>disagreement ALL fail closed"]
    D -->|"approved"| LAND
    LAND --> JOURNAL[("graph mutation journal +<br/>Trust Evidence Ledger — the runtime<br/>commits through these, never beside them")]
    JOURNAL --> RECEIPT["Trust Receipt: what the evidence was,<br/>which policy applied, who approved it"]
    XW["cross-workspace access gate — a pure function<br/>over two workspace ids, an operation and an<br/>explicit grant list; reads and writes nothing"] -.->|"answers the question the storage key and the<br/>admission check do not: may an actor in A<br/>reach into B at all?"| LAND
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `lib/human-oversight-approval-runtime.js` | Review cases, resolved identities, and every refusal |
| `lib/memory-admission-gate.js` | The frozen decision vocabulary and its receipt kinds |
| `lib/cross-workspace-access-gate.js` | A pure isolation decision over two workspaces |
| `lib/graph-mutation-receipt-*.js` | The journal's schema, writer, reader and rollback |
| `lib/cli-trust-receipt.js` | The receipt a person reads |
| `THREAT_MODEL.md` | What the gate is defending against, stated separately |

## 4. Essential Implementation Paths

`lib/human-oversight-approval-runtime.js:10-15` — the sentence that decides
whether a review claim means anything.

`:78` — the runtime refusing to exist without an identity resolver.

`:348-354` — self-approval checked on resolved identity, not on a name.

`:368-389` — distinct prior approvers, gathered from the journal and scoped to
one workspace.

`lib/memory-admission-gate.js:5-21` — four outcomes, frozen, with an ordering.

`lib/cross-workspace-access-gate.js:3-14` — the tenant question the storage key
does not answer.

## 5. Memory Data Model

What HUQAN durably holds is a decision record: review cases, immutable
transition snapshots, mutation receipts and Trust Receipts, alongside the graph
nodes that were allowed to land, keyed under their workspace. The memory entry
itself is ordinary; what is unusual is that it does not exist until something
decided it should.

## 6. Retrieval Mechanics

Retrieval here serves adjudication rather than recall: evidence gathering,
verification, contradiction detection and risk scoring feed the policy
boundary. A reader looking for ranking, fusion or consolidation will not find
them, and that is the design rather than an omission.

## 7. Write Mechanics

A proposal carries evidence, provenance and a workspace. The gate returns one of
four outcomes for a write. `review` opens a case that only an authenticated
decision closes, and the transition is committed through the journal that
already exists rather than into a store of the runtime's own.

## 8. Agent Integration

`huqan` for people, `huqan-mcp` for agents over stdio, and `huqan-gate` as a
pre-execution guard for agents that are not otherwise wired in. The quickstart
runs against a throwaway store in a temporary directory and "does not touch your
own memory and does not relax a gate."

## 9. Reliability, Safety, and Trust

Fail-closed is the stated default across identity, staleness, scope, durability
and firewall disagreement, and the escape hatches are policy flags rather than
code paths — which is both the strength and the limit, since a policy that sets
`allowSelfApproval` gets exactly what it asked for.

## 10. Tests, Evals, and Benchmarks

Tests sit beside their modules throughout the tree, including for the approval
runtime, the admission gate and the cross-workspace gate — the last of which is
written as a pure function specifically so its decision can be tested without a
store.

## 11. For Your Own Build

Never take the approver from the thing asking for approval. If your schema has
an `approved_by` field the caller fills in, what you have recorded is a claim
about a person, not a person.

Require the identity resolver at construction. A runtime that can be built
without one will eventually be built without one.

Check separation of duties on the resolved identity, and key your approver set
on it, so a second approval from the same principal does not satisfy a
two-approver rule.

Make "held" a distinct outcome from "refused". A write set aside for inspection
and a write rejected are different facts about the same content, and only one of
them is recoverable.

## 12. Open Questions

Whether the oversight guarantees mean much in a single-user install. Escalation
is absent there by the project's own account, and the distinct-approver rule
degenerates, so what a solo operator gets is receipts and refusals rather than
separation of duties — which is honest, and worth knowing before the gate is
credited with more than it provides.

Whether the graph behind the gate is meant to grow into a memory in its own
right. The admission machinery is far more developed than the store it admits
into, and a reader evaluating HUQAN as agent memory rather than as a gate should
size that gap first.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `lib/human-oversight-approval-runtime.js:10-15` | The rule that makes an approval mean something |
| `lib/human-oversight-approval-runtime.js:348-354` | Self-approval refused on resolved identity |
| `lib/human-oversight-approval-runtime.js:368-389` | One person cannot be two approvers |
| `lib/memory-admission-gate.js:5-21` | Held and refused as different outcomes |
| `lib/cross-workspace-access-gate.js:3-14` | The isolation question a storage key does not answer |

## History

**2026-09-16** — [`6f11b01476f019149cf5d56e961b5cb0b5d7a92e`](https://github.com/ali-ulu/huqan/commit/6f11b01476f019149cf5d56e961b5cb0b5d7a92e) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: no auto-run surfaces, one build-time execution point, one unpinned dependency surface and six dependency files inside the seven-day cooldown. `AGENTS.md` is addressed to a reading agent and was recorded as data. Nothing was installed, built or run, and the quickstart was not executed, so the gate described here is read from source rather than observed.

---
title: "Cognis"
eyebrow: "A memory policy with a fingerprint"
description: "A controller/executor agent OS that owns no memory store and fingerprints the memory policy instead — a SHA-256 over the backend, the behaviour flags and the instruction text, stamped on the turn it governed."
root: ../..
page_kind: system
source_name: "fpytloun/cognis"
source_url: https://github.com/fpytloun/cognis
archive_name: "fpytloun--cognis"
revision: 2bcafe4c2913b4757ddec246f550fbbf4556377d
revision_url: https://github.com/fpytloun/cognis/commit/2bcafe4c2913b4757ddec246f550fbbf4556377d
analyzed_at: 2026-09-11
capabilities: "scope_enforced, negative_eval"
capability_evidence:
  scope_enforced: "the provider boundary | cognis/providers/memory/protocol.py, cognis/core/trusted_evidence.py | `agent_id` and `user_email` on every contract method, taken from a verified JWT subject; the trusted routes add a per-route JWT with exact claim bindings, a fresh `jti`, a 60-second lifetime and no agent claim | tests/contract/test_mnemory_contract.py::test_jwt_subject_is_not_overridden_by_openwebui_header"
  negative_eval: "identity, not retrieval | tests/contract/test_mnemory_contract.py:128,:142 | a caller-supplied OpenWebUI header is asserted not to override the JWT subject, and a wrong audience is asserted rejected — the input the retrieval boundary depends on | test_mnemory_contract"
stack_storage: "postgres"
stack_retrieval: ""
stack_source: "seeded"
matrix:
  memory_unit: "None of its own. The unit is whatever the mounted provider returns — a recall payload of instructions, core memories, search results and stats — with the host holding the policy that produced it"
  storage: "No memory store. Postgres holds users, agents, conversations and workflows; memory is delegated to a provider, with Mnemory and a null backend shipped"
  retrieval: "`recall` on the provider, parameterised by search mode, instruction mode, TTL and a managed flag, with auto-recall a policy switch rather than a call site"
  write: "`remember` for turns and `add_memory` for explicit facts, both carrying agent and user identity; auto-remember is a policy flag; and a trusted-evidence route that sends a strict pydantic body bound to a SHA-256 hash of the exact persisted session event"
  update_delete: "`delete_memory` and a separate `delete_memory_tool` on the contract, so the agent-facing delete is a distinct method from the host's own"
  scoping: "`agent_id` and `user_email` on every contract method, with the caller's identity taken from a verified JWT subject rather than a request header"
  integration: "Controller and executors split over a bus — tools, browsers, shells, LSPs and MCP servers run wherever the work belongs; memory and guardrails are companion services"
  background: "Workflows run agent work off the chat path; memory bootstrap, auto-recall and auto-remember are per-turn policy rather than background passes"
  trust: "None on a stored memory. What the host models is the fate of a *write*: a seven-value evidence outcome, a typed rejection contract asserting no semantic effects, and an explicit unknown-outcome state that disables automatic retry"
  strengths: "A frozen per-turn memory policy carrying a SHA-256 fingerprint over backend, flags and instruction text; a memory write bound by hash to the exact persisted event that occasioned it; a transport failure classed as *unknown* rather than failed, with retry refused; deletion in the contract twice"
  risks: "Provenance crosses the boundary and belief does not — the provider is told who and which event, never how much to trust it — and neither the fingerprint nor the evidence hash records what a write changed in the store"
---

## 1. Executive Summary

Cognis is a Business Source License 1.1 agent OS — 1,495 files, 802 commits —
that separates a controller from executors: the controller owns users, agents,
conversations, workflows, routing and the UI, while executors run tools,
browsers, shells, LSPs and MCP servers wherever the work belongs. It is the
middle piece of a three-service platform by one author, beside
[Mnemory](../mnemory/) for memory and [Intaris](../intaris/) for guardrails.

**It owns no memory store, and that is why it is worth reading.** Its Postgres
holds users, agents, conversations and workflows; memory is a mounted provider
behind `MemoryProvider`, with a Mnemory backend and a `null` backend shipped. So
what this report is about is the *contract*, and the contract does three things
this atlas rarely finds in a host runtime.

**Deletion is in it, twice.** `delete_memory` and `delete_memory_tool` are
separate methods, so the delete an agent can call through a tool is a different
entry point from the host's own — the two can be authorised differently. The
comparison that makes this notable is that AutoGen and ADK both omit deletion
from their memory contracts entirely, and no better implementation can add it
afterwards.

**Identity crosses the boundary on every call.** `agent_id` and `user_email` are
parameters of `recall`, `remember`, `add_memory`, `search` and both deletes. A
provider is never asked to guess whose memory it is operating on.

**And the policy that governed a turn is fingerprinted.** `MemoryRuntimePolicy`
is frozen and provider-neutral — `enabled`, `bootstrap_instructions`,
`bootstrap_core`, `auto_recall`, `auto_remember`, `tools_enabled`, the
instruction text, a mode and a profile — and `fingerprint_policy` hashes the
backend id, the options, every flag and a SHA-256 of the instruction text into
one `policy_fingerprint`. `audit_metadata()` hands that back with the backend and
mode for the turn's record. A reader asking *why did the agent recall nothing on
Tuesday* has a value to compare rather than a configuration to reconstruct.

What the boundary does not carry is anything epistemic. No status, no
provenance, no trust, no tombstone: the host mediates *whether* memory runs and
under which policy, and takes no position on whether what comes back is true.

## 2. Mental Model

The controller decides, the provider remembers, and the policy is the contract
between them for one turn.

**A turn resolves a policy first.** `MemoryBackendOptionsProvider` is
provider-owned — it validates options, publishes `MemoryModeDescriptor` entries
with UI metadata and a `behavior` dict, and resolves them into the frozen runtime
policy. So the *provider* defines what modes exist and the *host* enforces the
resolved policy, which is a cleaner split than a host enumerating backends it
does not own.

**Memory then happens by flag rather than by call site.** `auto_recall` and
`auto_remember` are policy fields, so turning memory off for a profile is one
resolved value rather than a code path.

**Identity is verified, not asserted.** The contract test asserts a JWT with the
wrong audience is rejected, and — the interesting one — that the JWT subject *is
not overridden by an OpenWebUI header*. Whose memory a call touches cannot be
changed by a header a caller controls.

**And the fingerprint travels with the turn.**

```mermaid
%% caption: the policy is frozen and fingerprinted into the turn's audit metadata before either hook runs, and no status, provenance or trust crosses back over the provider boundary
flowchart TD
    O["Agent profile + backend options"] --> V["provider.validate_options"]
    V --> RP["resolve_policy → MemoryRuntimePolicy<br/>frozen, provider-neutral"]
    RP --> FP["fingerprint_policy:<br/>SHA-256 over backend, flags,<br/>options and instructions hash"]
    FP --> AM["audit_metadata on the turn"]
    RP -- "auto_recall" --> R["provider.recall"]
    RP -- "auto_remember" --> W["provider.remember"]
    JWT["Verified JWT subject"] --> ID["agent_id + user_email<br/>on every contract method"]
    ID --> R
    ID --> W
    R -. "no status, provenance or trust<br/>crosses the boundary" .-x HOST["Controller"]
```

The dotted edge is the limit: everything about *whether* memory ran is recorded,
and nothing about whether what it returned can be believed.

## 3. Architecture

A controller process, executors that connect to it, Postgres for the controller's
own state, and companion services for memory and guardrails. Docker files for the
executor and a mock LLM ship in the tree, as does a Makefile and a GitHub
Actions workflow set.

The screen found 0 auto-run surfaces, 5 build-time execution paths, 1 unpinned
dependency surface, and a `uv.lock` unchanged for twelve days — so every version
it resolves is at least that old. Nothing was built or run.

The licence is **BSL 1.1**, which is a caveat rather than an exclusion here: the
code is readable and analysable, and a reader should check the change date and
the additional-use grant before building on it.

## 4. Essential Implementation Paths

- **Contract** — `cognis/providers/base.py`, `class MemoryProvider(Protocol)`:
  `load_session_identity`, `recall`, `remember`, `add_memory`, `search`,
  `delete_memory`, `delete_memory_tool`, `bootstrap_agent`, `health`.
- **Policy** — `cognis/providers/memory/policy.py`: `MemoryRuntimePolicy`,
  `MemoryModeDescriptor`, `MemoryBackendOptionsProvider`, `fingerprint_policy`,
  `audit_metadata`.
- **Backends** — `cognis/providers/memory/mnemory.py` (854 lines),
  `cognis/providers/backends/memory/null.py` (154), and a thinner
  `backends/memory/mnemory.py`.
- **Agent-facing tools** — `cognis/tools/builtin/memory.py` (720 lines).
- **Contract test** — `tests/contract/test_mnemory_contract.py`, plus
  `tests/unit/test_memory_policy.py` and `tests/unit/test_memory_tools.py`.

## 5. Memory Data Model

There is none to describe, and the shape of the *response* is the closest thing.
The contract test pins it: a recall returns a `session_id` string, `instructions`
that may be null or a string, `core_memories` that may be null or a string, a
`search_results` list, and a `stats` dictionary whose key set is asserted exactly.
That last assertion is the useful one — a backend that adds or drops a stat key
fails the contract rather than silently changing what the UI shows.

`load_session_identity` is a first-class method rather than a parameter, which
says the host expects a provider to hold an identity for a session and to be
asked for it rather than told.

## 6. Retrieval Mechanics

`recall` carries `search_mode`, `include_instructions`, `managed`,
`instruction_mode` and `ttl` — so the host can ask for a bootstrap-shaped recall
or a query-shaped one through the same method, and a provider that supports only
one degrades rather than breaking. Ranking, fusion and scoring are entirely the
provider's business; the host contributes the identity, the mode and the budget.

## 7. Write Mechanics

Two write verbs with different meanings: `remember` takes a session's messages,
`add_memory` takes a single piece of content with a type, categories, importance,
a role and a `pinned` flag. Keeping conversational capture and deliberate
assertion apart at the contract is right — they have different failure modes and
different authority — and several host runtimes in this atlas collapse them.

Both are policy-gated: `auto_remember` decides whether the first fires without a
tool call.

**A third route exists for the case where the host wants the provider to trust
it.** `remember_evidence` and `remember_user_event` post to
`/api/evidence/remember/v1` and `/api/user-events/remember/v1` under a protocol
string, `mnemory.trusted-evidence.v1`, with a body that pydantic will not let
drift: `extra: forbid` on every model, exactly one message, `role` a literal
`"user"`, content bounded at 400,000 characters, and `event_hash` constrained to
`^[0-9a-f]{64}$`. A validator rejects a message that is structurally present and
empty.

The hash is the part worth taking. `event_hash(stream_id, seq, event)` is a
SHA-256 over the stream id, the sequence number and the event's type and data,
under a docstring stating the intent: *"Bind the exact persisted event to its
authoritative Intaris stream/seq."* The agent loop computes it at the moment the
event is appended and carries it on the turn context, and the trusted write fires
only when the policy allows auto-remember, the hash exists, and
`evidence_admission_authorizes` matches the agent's owner. So a memory written
this way is not merely attributed to a user — it names the exact byte-identical
persisted message, at its position in an append-only session stream, in a form
the receiving service can recompute. Normalisation is specified rather than
assumed: strings to NFC, object keys sorted, recursively.

**The alias table is the other new mechanism, and it is about revisions rather
than identity.** `cognis/core/memory_aliases.py` gives the model short session
handles — `m1`, `m2` — that bind not to a record but to a record *revision*.
`memory_revision` returns a native `revision_id`, `revision`, `version` or
`provenance_id` when the backend has one, and otherwise a deterministic hash of
the record with the volatile keys removed — `access_count`, `checked_at`,
`last_accessed`, `score` — so a read that only bumped a counter does not look
like an edit. A binding carries an `expected_revision` precondition, and
`invalidate_memory` drops the alias when the record moves. The effect is
optimistic concurrency for a model that refers to memories by number: an edit
against `m3` is refused if `m3` is no longer what the model was shown.

## 8. Agent Integration

`cognis/tools/builtin/memory.py` is 720 lines of agent-facing tools, and
`delete_memory_tool` existing separately on the contract is the seam that makes
those tools governable — an agent's delete and the host's delete can be
authorised, logged or refused differently, which is exactly the distinction a
governed write gateway needs and which most tool surfaces flatten.

Guardrails are a sibling provider, so a tool call can be evaluated by
[Intaris](../intaris/) before it runs. Between the two, this platform has the
pieces for policy on both the memory path and the action path; what it does not
have is a shared vocabulary between them.

## 9. Reliability, Safety, and Trust

**Scope is verified rather than asserted, and tested that way.** The JWT subject
is the identity, and the committed contract test asserts an OpenWebUI header
cannot override it. That is a stronger form of `scope_enforced` than a filter
composed into a query, because it protects the input to the filter.

**The policy fingerprint is the mechanism to take.** Hashing the backend, the
options, every behaviour flag and the instruction text into one value that
travels with the turn's audit metadata answers a question this atlas keeps
finding unanswerable: *which rules were in force when this happened.* One other
system here does it, [MemLedger](../memledger/), by canonicalising and hashing
its policy file and stamping the hash on every event it influenced. Cognis does
it a layer up, for the host's own memory policy, and reaches the same property
from a different direction.

**Provenance crosses the boundary; belief does not.** The trusted-evidence route
sends a strict body — an `actor` of `user_id` and `owner_id`, an `event` of id,
`event_hash`, session, conversation and turn, and exactly one user message,
`extra: forbid` on every model — so the provider is told precisely *who* said
*which persisted thing, where*. What never crosses is a confidence, a status or a
verdict. That is a defensible split for a host, and it has the cost DeerFlow's
report records for the same family: what a backend models and the host does not
simply does not travel. The boundary is asymmetric rather than thin: identity and
position cross it, epistemics never do.

**The host models the fate of a write, which is not the same as trust in a
memory.** `EvidenceOutcome` is seven-valued — `accepted | replayed | recovered |
skipped | conflict | rejected | unavailable` — and each result carries `terminal`
and `retryable` booleans beside it. `TrustedEventRejection` is stricter still: a
closed set of four budget reasons, and literal-typed fields asserting
`terminal: true`, `retryable: false`, `fallback_allowed: false`,
`semantic_effects: "none"` and `source_retention: "caller_queue"`. A validator
refuses a non-boolean for the safety flags, and `parse_trusted_rejection` returns
`None` rather than a rejection when the payload does not match — under a docstring
saying why: *"Do not classify unrelated validation errors as effect-free
rejections."* A 422 that is merely a 422 must not be mistaken for a durable,
side-effect-free refusal.

**The best detail is the state between success and failure.** A transport error
on `remember` raises `RememberOutcomeUnknownError` — *"Mnemory remember outcome is
unknown; automatic retry is disabled"* — and the evidence result carries
`outcome_unknown` through to a queue-friendly dict. Most systems in this atlas
retry a failed memory write; this one distinguishes *the write failed* from *we
do not know whether the write happened*, and refuses to retry the second, because
a duplicate memory is worse than a missing one when the caller still holds the
source. `test_evidence_transport_failure_is_outcome_unknown_and_not_retried` and
`test_uncertain_write_reuses_canonical_request` pin both halves.

**And none of it is an audit of the memory.** The policy fingerprint records which
rules governed a turn; the evidence hash records which persisted event a write was
derived from. Neither records what the write changed in the store. What Cognis can
prove is provenance — *this memory came from exactly this message at exactly this
sequence in the session stream* — and what it cannot is history: no append-only
record of memory mutations exists on this side of the boundary, and the provider's
log is the provider's.

## 10. Tests, Evals, and Benchmarks

7,026 test functions over 365,005 lines of Python, and the shape matters more
than the size. `tests/contract/test_mnemory_contract.py` is the piece worth
copying: a contract suite that runs against the real provider surface and asserts
authentication behaviour, identity precedence and response shape.
`test_memory_policy.py` covers the resolution and fingerprinting;
`test_memory_tools.py` the agent-facing tools; `tests/integration/test_memory.py`
the wiring.

`tests/unit/test_evidence_contract.py` is the newer one and it tests the
protocol's *edges* rather than its happy path: a typed rejection retains its
source without retry; an unrelated 422 is not classified as a budget rejection;
an uncertain write reuses the canonical request rather than composing a new one;
the JWT has exact claim bindings, a fresh `jti`, a 60-second lifetime, route
binding and no agent claim; a fixture is asserted byte- and hash-exact; and a
transport failure is `outcome_unknown` and not retried. Fourteen cases, almost
all of them about what must *not* happen.

`tests/unit/test_memory_aliases.py` and `tests/integration/test_memory_alias_replay.py`
cover the alias table, replay included.

`negative_eval` is earned narrowly and precisely, on
`test_jwt_subject_is_not_overridden_by_openwebui_header` and
`test_whoami_rejects_wrong_jwt_audience` — committed cases asserting that a
caller-supplied header cannot reach another identity's memory. It is an identity
assertion rather than a retrieval assertion, and it is the input the retrieval
boundary depends on.

No benchmark numbers are published, and none are claimed.

## 11. Patterns Worth Stealing

### Steal

**Fingerprint the policy that governed the turn.** A SHA-256 over the backend id,
the resolved flags, the options and a hash of the instruction text, returned as
audit metadata. It is perhaps twenty lines and it turns "what was the memory
configuration in March" from an archaeology problem into a comparison.

**Put deletion in the contract twice.** A host delete and an agent-facing delete
are different authorities wearing the same verb.

**Let the provider own its modes and the host own their enforcement.**
`MemoryBackendOptionsProvider` validates options and publishes descriptors; the
host resolves them into a frozen policy. Neither has to enumerate the other.

**Ship a null backend and a contract test together.** The first makes a new
backend a copy-and-fill exercise; the second is what stops it drifting.

**Verify identity, then test that a header cannot override it.** The assertion is
three lines and it guards every scope filter downstream.

**Bind a memory write to the exact persisted event it came from.** A SHA-256 over
`(stream_id, seq, event_type, event_data)`, computed at append time and carried on
the write, means the receiving store can recompute the identity of its own source.
Specify the normalisation — NFC, sorted keys, recursive — or the hash is a hash of
your serializer.

**Model *unknown* as a third outcome of a write, and refuse to retry it.** A
transport error is not a failure: the write may have landed. Cognis raises
`RememberOutcomeUnknownError`, disables automatic retry and leaves the source with
the caller, which is the correct trade when a duplicate memory costs more than a
missing one.

**Make a rejection contract literal-typed.** `terminal: Literal[True]`,
`retryable: Literal[False]`, `semantic_effects: Literal["none"]` — and a parser
that returns `None` rather than a rejection when the payload does not match, so an
ordinary validation error is never mistaken for a durable, effect-free refusal.

**Alias to a revision, not to a record.** If the model refers to memories by short
handle, bind the handle to the revision it was shown, drop the volatile fields
from the identity so a read does not look like an edit, and carry the revision as
a precondition on the edit.

### Avoid

**Do not mistake a policy fingerprint for an audit log.** It says which rules
ran, not what they did.

**Do not let a thin boundary become a silent one.** Nothing epistemic crosses
here; a provider with a trust model has no way to tell the host, and the host has
no way to ask.

### Fit

This is the right shape for a self-hosted platform where memory is somebody
else's service and the host's job is to decide when it runs and under what
policy — and the fingerprint makes that job auditable. Take the policy object and
the contract test regardless of whether you want the rest.

It is the wrong place to look for memory mechanics: the store is elsewhere, and a
reader who wants to know how these memories are corrected should read
[Mnemory](../mnemory/) instead. The BSL licence also makes this a study rather
than a dependency for most readers.

## 12. Antipatterns / Risks

- **No epistemic vocabulary across the provider boundary**, so trust cannot
  travel even when a backend has it.
- **The fingerprint records configuration, not consequence** — no mutation log
  exists host-side.
- **BSL 1.1**, which constrains use rather than reading.
- **A 720-line tool module against a 154-line null backend**: the agent-facing
  surface is where most of the behaviour lives, and it is the part a new backend
  has to satisfy without a template.

## 13. Build-vs-Borrow Takeaways

Borrow `policy.py` almost verbatim — it is small, provider-neutral, and the
fingerprint is the part nobody else builds. Borrow the two-delete contract and
the header-override test.

Do not borrow this as a memory layer; it is a host, and its value to a reader is
the seam it defines rather than anything it stores.

## 14. Open Questions

- Where does `audit_metadata()` land, and is that record append-only?
- Can a provider report that it refused a write, and if so, how does the host
  learn it — `health()` is the only status channel in the contract.
- Does `delete_memory_tool` differ from `delete_memory` in authorisation today,
  or only in name?

## 15. Appendix: File Index

| Path | Role |
| --- | --- |
| `cognis/providers/base.py` | `MemoryProvider` protocol — nine methods including two deletes |
| `cognis/providers/memory/policy.py` | Frozen runtime policy, mode descriptors, `fingerprint_policy`, `audit_metadata` |
| `cognis/providers/memory/mnemory.py` | The Mnemory backend |
| `cognis/providers/backends/memory/null.py` | The template backend |
| `cognis/tools/builtin/memory.py` | Agent-facing memory tools |
| `tests/contract/test_mnemory_contract.py` | Identity precedence, audience rejection, response shape |
| `tests/unit/test_memory_policy.py` | Policy resolution and fingerprinting |
| `cognis/providers/memory/evidence.py` | The `mnemory.trusted-evidence.v1` contract, the seven-value outcome, the literal-typed rejection |
| `cognis/core/trusted_evidence.py` | `event_hash`, event markers, canonical turn selection — 1,074 lines |
| `cognis/core/memory_aliases.py` | Session aliases bound to record revisions, with `expected_revision` preconditions |
| `tests/unit/test_evidence_contract.py` | Fourteen cases on the protocol's edges |
| `tests/unit/test_memory_aliases.py`, `tests/integration/test_memory_alias_replay.py` | The alias table and its replay |

## Appendix: Recorded Searches

Run from the root of the checkout at the pinned commit.

| Claim | Command | Result at this pin |
| --- | --- | --- |
| No memory store of its own | `grep -rniE "CREATE TABLE.*memor" --include="*.py" cognis` | Nothing; Postgres holds users, agents, conversations and workflows |
| Belief does not cross the boundary | read the models in `cognis/providers/memory/evidence.py:29-85` | `actor`, `event` and one message; no confidence, status or verdict field on any of them |
| The trusted route is wired | `grep -rn "remember_evidence\|remember_user_event" --include="*.py" cognis` | Computed at `agent_loop.py:22528`, gated at `:22551-22562`, sent from `mnemory.py:428` and `:504` |
| No append-only record of memory mutations | `grep -rn "memory" --include="*.py" cognis/core/agent_loop.py \| grep -iE "append.*event\|ledger"` | Nothing; the Intaris stream records session events, and the memory write carries their hash |
| Tree and suite size | `find cognis packages -name "*.py" \| xargs wc -l \| tail -1`; `grep -rc "def test_" tests/*.py tests/*/*.py` summed | 365,005 lines; 7,026 test functions |

## History

**2026-09-11** — [`2bcafe4c2913b4757ddec246f550fbbf4556377d`](https://github.com/fpytloun/cognis/commit/2bcafe4c2913b4757ddec246f550fbbf4556377d) — re-read, 1,589 files and 344,354 insertions past the previous pin in a single commit, of which 2,117 lines are the memory paths and 1,074 are one new module. **Marks unchanged at two, both re-verified; one published claim is stale.** The report said *"Nothing carrying trust, provenance or status crosses it"* — provenance does now. `mnemory.trusted-evidence.v1` posts an `actor` of `user_id` and `owner_id` and an `event` carrying a SHA-256 `event_hash` over the stream id, sequence and payload of the exact persisted user message, computed at append time in the agent loop and gated on an owner match. Belief still does not cross: no confidence, status or verdict appears on any model in the contract, so the split is now identity-and-position out, epistemics never. **Three mechanisms are new and worth the report.** A seven-value `EvidenceOutcome` beside a literal-typed `TrustedEventRejection` asserting `semantic_effects: "none"`, with a parser that returns `None` rather than a rejection when the payload does not match — *"Do not classify unrelated validation errors as effect-free rejections."* An explicit `outcome_unknown` state: a transport error on a write raises `RememberOutcomeUnknownError` and disables automatic retry, because the write may have landed. And a session alias table binding `m1`-style handles to record *revisions*, with volatile fields excluded from the identity so a read does not read as an edit, and `expected_revision` as a mutation precondition. `audit_log` stays withheld and the reasoning is sharpened: the fingerprint says which rules ran, the evidence hash says which event a write came from, and neither says what the write changed. Suite 7,026 test functions over 365,005 lines. Screened before reading: no auto-run surface, five build-time execution paths, six dependency manifests inside the cooldown; nothing was built or run.

**2026-08-07** —
**2026-08-07** — [`b918c94563608e379e4fd2fd28e863371fc86d37`](https://github.com/fpytloun/cognis/commit/b918c94563608e379e4fd2fd28e863371fc86d37) — first reading. Screened before reading: 0 auto-run surfaces, 5 build-time execution paths, 1 unpinned dependency surface, and `uv.lock` unchanged for twelve days, so every version it resolves is at least that old. Nothing was built or run. Licensed BSL 1.1, which is recorded as a caveat rather than an exclusion. The system is the controller of a three-service platform by one author — memory in [Mnemory](../mnemory/), guardrails in [Intaris](../intaris/) — and is read here for its provider contract rather than for a store it does not have.

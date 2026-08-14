# A handoff protocol, and the durable thing that is not a belief

**Status:** examined, excluded, no report. Recorded because the exclusion is a
clean second instance of a boundary this atlas has drawn once before from the
opposite side, and because three of its mechanisms are worth taking regardless.
**Subject:** [DeepJudge-Agent-Handoff-Protocol/agenthandoffprotocol](https://github.com/DeepJudge-Agent-Handoff-Protocol/agenthandoffprotocol),
read on 2026-08-14 at
[`9c53aa5c24dfd293b7fef19effe3b399dd5a3524`](https://github.com/DeepJudge-Agent-Handoff-Protocol/agenthandoffprotocol/commit/9c53aa5c24dfd293b7fef19effe3b399dd5a3524),
a commit dated 13 August 2026.

## What it is

Agent Handoff Protocol (AHP) v1, from DeepJudge: an HTTP contract for moving a
user's task between two independently operated agent applications. Discovery at
`/.well-known/agent-handoff-spec.json`, then one authenticated POST carrying an
**objective**, a **conversation sample** (MCP `SamplingMessage`, version-pinned
to the 2025-11-25 schema), **resources** (inline `text`/`blob` or remote HTTPS),
a **thread ID** and an **idempotency key**. The receiver returns one value: an
HTTPS URL to a prepared continuation.

Apache-2.0. Three markdown files totalling 1,925 lines, two PNGs, and no source
tree.

## Why there is no report

Two independent grounds, and the second is the interesting one.

**There is no inspectable implementation at a pinned commit.** The only code in
the repository is a 78-line Python sketch in the examples document that
introduces itself as emphasising "externally visible invariants rather than a
particular framework or database", plus three TypeScript type declarations in
the spec. The README says AHP "was designed implementation-first in a working
DeepJudge product" and that these documents "extract the interoperable behavior
from that implementation". So an implementation exists, is referenced, and is
not published. That is the third of the
[add-memory-system skill](../.agents/skills/add-memory-system/SKILL.md)'s three
genuine exclusions, met exactly.

**What is durable is not a belief.** AHP does require durable state, and
normatively rather than as an implementation detail. §10 makes the receiver
persist a thread mapping, an idempotency result with a request fingerprint, and
materialised resources, *atomically*, with four REQUIRED externally visible
invariants around it — a failed handoff must not leave a successful idempotency
result, a success response must not race ahead of durable state, two concurrent
same-key requests must produce at most one set of side effects, and a partial
resource set must not be presented as complete. §11.4 sets a retention floor of
24 hours. This survives the session by construction.

But the units are a **thread ID** — a correlation identifier for a continuing
task — and an **idempotency key plus fingerprint** — a replay guard. Neither is
a claim that can be true or false. There is nothing for a correction to be
about, and the fingerprint's whole purpose is the opposite of correction: §11.3
requires that the same scoped key replayed with a *different* fingerprint return
`409 Conflict` and process nothing. The record exists in order to refuse
revision.

There is also no retrieval anywhere in the protocol. The package is pushed
wholesale, minimised by the sender and reviewed by the user before it leaves;
nothing is ever selected by relevance, ranked, or recalled.

## The boundary, reached from the other side

This is the same call [the overview](../content/overview.md) already made for
`showjihyun/bvwebchat`, which passed the letter of the inclusion test and was
excluded because *"what survives is workflow control state: a phase is not a
claim that can be true or false, and there is nothing for a correction to be
about."*

AHP is a cleaner instance for two reasons. That case turned on one repository's
choices about its own harness; here the durability is a normative MUST in a
published contract, so there is no question of whether an implementer might have
done it differently. And a thread ID is a purer example of the category than a
workflow phase — a phase at least names a state of the world, whereas a
correlation identifier names nothing but itself.

Worth having both, because the two arrive from opposite directions: one is a
harness that persists more than you expect, and one is a protocol that persists
exactly what it says and still is not memory. The distinguishing question in
both cases is not *does something survive* but *is the surviving thing the kind
of thing that could be wrong*.

## Three mechanisms worth taking

**§13.3 is the sharpest statement of the untrusted-input rule in anything read
for this atlas.**

> Every transferred string and byte sequence is untrusted input, including the
> objective, transcript, resource name, description, extracted text, and remote
> content. The receiver MUST NOT treat any of them as receiver-side system or
> developer instructions.

The atlas currently credits [Verel](../content/systems/verel/) with the safest
recall renderer — token-budgeted and fenced as untrusted data. AHP states the
same rule normatively and *enumerates the fields it covers*, which is the part
implementations get wrong: a system that fences the transcript and not the
resource filename has not fenced anything. §13.4 adds the sender-side half —
hidden reasoning, system prompts, developer messages, private policy text,
credentials and unnecessary tool traffic MUST NOT be serialised — and notes that
`_meta` and tool content must be assumed sensitive.

**Idempotency key plus request fingerprint is a write-path mechanism memory
stores should have.** Same scoped key with the same fingerprint returns the
stored result and creates nothing; same key with a different fingerprint is a
409 and processes nothing. The fingerprint covers the operation, the thread and
client identity, the resolved target, and the complete body, and explicitly
excludes volatile transport fields and credentials.

Several systems in this corpus re-ingest into duplicates, and
[Memori](../content/systems/memori/)'s content-hash dedupe collapses every
non-Latin fact into one row because the key strips non-ASCII. A memory store
that fingerprinted its writes the way AHP fingerprints transfers would get
"this exact extraction has already happened" for free, and — more useful — would
get a *conflict signal* when the same logical write arrives with different
content, which is precisely the moment a store should notice a contradiction
instead of silently overwriting.

**§13.8 is a normative deletion-completeness requirement.** "Deleting a user or
tenant MUST not leave accessible orphaned handoff resources." That is the
property [the deletion harness note](2026-08-12-deletion-harness-level-1-and-level-2.md)
is about, written as a MUST — and it is exactly what
[LangGraph](../content/systems/langgraph/)'s SQLite store violates, declaring
`ON DELETE CASCADE` on its vector sidecar and never enabling foreign keys.

## Two smaller observations

**§16.3 is a fifteen-item interoperability list** — authenticated and public
discovery, replay with the same key, concurrent duplicates, same-key/different-request
conflict, a full A→B→A round trip, isolation of equal thread IDs across users
and deployments, unsafe redirect URLs, and so on. It is prose and a SHOULD, not
runnable.

Set beside [LangGraph](../content/systems/langgraph/)'s
`langgraph-checkpoint-conformance` from the same week, that makes two conformance
artifacts with inverted virtues: LangGraph's is installable, capability-aware and
emits a report, and it validates the thread-scoped checkpointer rather than the
durable store; AHP's cannot be run and enumerates the right scenarios, including
several — cross-tenant identifier isolation, same-key/different-content conflict
— that no runnable suite in this atlas covers. Neither project has the pair.
Relevant to [`.agents/protocol/`](../.agents/protocol/), which is trying to be
both at once.

**Clocks are deliberately absent.** §15: "Clocks are not part of correctness in
v1; neither transfer timestamps nor expiry timestamps appear in the wire
request." A cross-organisation protocol that refuses to make correctness depend
on two parties' clocks agreeing is the opposite choice from every bitemporal
system here, and it is the right one for its problem — worth noting because the
atlas's instinct on seeing a durable record with no timestamp is to call it a
gap.

## Disposition

No report. Proposed: a short "Not in scope" entry in `content/overview.md`
alongside the KV-cache and semantic-response-cache sections, on the
durable-but-not-a-belief ground, with the bvwebchat case named as the sibling.
The §13.3 wording is worth quoting wherever the atlas discusses fencing recalled
memory as untrusted input, and the fingerprint mechanism is a candidate for the
pattern library if a second independent instance turns up — one instance is an
example, not a pattern.

---
title: Append-Only Memory Audit
eyebrow: Pattern · Observability
description: Record memory mutations and retrieval use as immutable events while keeping telemetry separate from the truth state of memory.
root: ../..
page_kind: pattern
---

## Intent

Make it possible to reconstruct how memory changed, which memories entered context, and what feedback followed—without overwriting the evidence needed for investigation.

## The problem

Current rows answer what the system believes now, not how it arrived there. A counter such as `times_used = 12` cannot explain which conversations used a memory, whether it was actually injected, or which model and query selected it. Mutable history also makes concurrency and audits ambiguous.

## The pattern

Keep canonical memory state for efficient reads and append immutable events for changes and use:

```text
memory_mutation:
  created | corroborated | corrected | superseded | rejected | expired

retrieval_event:
  considered | retrieved | injected | cited | downvoted
```

Each event records memory ID, scope, actor, timestamp, request or conversation ID, reason, and relevant version identifiers. Derive counters and dashboards from events. Retention and privacy policies still apply; append-only means application code does not casually rewrite history, not that data can never be erased.

```mermaid
flowchart TD
    W["write / correct /<br/>reject"] --> S["canonical memory<br/>state"]
    W --> M["memory_mutation<br/>events"]
    R["retrieval"] --> S
    R --> RE["retrieval_event<br/>log"]
    S --> A["answer"]
    M --> D["counters · dashboards ·<br/>investigations"]
    RE --> D
    D -. "never read back as truth" .-x S
```

The dashed edge is the whole discipline: events flow outward into
observability and never back into belief.

## Why it works

Events support debugging, eval generation, attribution, concurrency analysis, and product review. They reveal the difference between a memory matching a query and actually influencing a prompt.

## The critical boundary

Telemetry is not truth. A frequently retrieved memory is reachable, not necessarily correct. A downvote says the resulting interaction was unsatisfactory, not that the memory was false. Feed events into review and evaluation; do not silently promote, reject, or delete beliefs from weak behavioral signals.

## Tradeoffs

Event volume grows quickly. Schema evolution and privacy deletion become harder. Causal attribution remains limited: injection does not prove that a model used a memory. Audit events also need transactional coupling to state changes or they can describe mutations that never committed.

## Cost to adopt

**Build:** an event table, a writer on every mutation path, and a retention
policy for the log itself.

**Forces elsewhere:** the log is often the largest table in the system, and it
inherits the same deletion obligations as the memory it describes — an audit row
quoting a deleted value has not deleted it.

**Ongoing:** logs that nobody queries rot. The pattern pays off only if
something reads it: a review surface, an investigation path, or a test.

**Skip it if** you already have durable evidence records and git history. Two
audit trails that disagree are worse than one.

## Seen in the atlas

**[Aura](../../systems/aura/) is the only one that is tamper-evident, and it is
the upper bound of this pattern.** Every audit on this page is append-only by
file handle: opened `O_APPEND`, never rewritten by the code that owns it, and
completely silent about an edit made by anything else. Aura keeps a SHA-256 hash
chain beside its receipt store, one JSONL line per receipt:

```text
seq:           monotonically increasing per-store
content_hash:  SHA-256 of the canonical JSON of the receipt body
prev_hash:     entry_hash of the previous entry (genesis is all zeros)
entry_hash:    SHA-256 over the canonical concatenation of the above
```

Verification walks from genesis, recomputes the entry hashes *and* re-hashes the
receipt bodies on disk. The module states what that buys: deletion shows up as a
sequence gap, insertion as a broken link, because `entry_hash` covers
`prev_hash`. A modified body fails because the recomputed `content_hash` no
longer matches. `tests/test_audit_chain.py` asserts each of those cases
separately and passes — 16 tests, run at the pinned commit.

Two design choices go with it and both are worth copying. The chain is a
**sidecar**: only `emit` is extended, and existing callers see nothing, so
tamper-evidence can be added to an audit log that already exists. And when the
receipt body is durable but the chain append fails, the runtime records a
degradation reading *"receipt body persisted but audit-chain append failed;
verify_chain will fail"* — it does not roll back. For a sidecar that is correct:
the discrepancy stays detectable instead of being papered over, which is the
opposite of the right answer for Palazzo's inline WAL below.

The pattern's ceiling is worth stating plainly. A hash chain proves the log has
not been edited; it does not prove the log is complete, because a writer that
never emitted a receipt leaves nothing to break. Aura closes that on its
strictest path — the memory write gateway rolls the write back when the receipt
cannot be emitted — and not on the others.

**[Palazzo](../../systems/palazzo/) is the only implementation here where the
log entry is a precondition rather than a consequence.** Every other audit on
this page is written because a mutation happened. Palazzo's write-ahead log has
two methods, and the destructive paths call the second one:

```rust
/// Like `log`, but errors when the entry cannot be durably appended —
/// including when no WAL path is configured at all. Destructive operations
/// (palace_delete, palace_delete_by_filter) call this and abort before
/// touching Qdrant: the WAL is their only audit trail, so a delete that
/// can't be logged must not happen.
pub fn log_strict<T: Serialize>(&self, operation: &str, params: &T) -> anyhow::Result<()>
```

The split is the design. Ordinary writes use best-effort `log`, which warns and
continues; deletion uses `log_strict`, which fails the operation. A lost store
line is an inconvenience; a lost delete line is the erasure of the record that
the erasure happened, and that is the one case where continuing is worse than
stopping. `delete_happy_path_wal_logs_then_deletes` pins the ordering.

The second detail is what goes in the entry. Palazzo writes a text preview of
every point before deleting it, so the log says what was removed. Compare
[LoreKit](../../systems/lorekit/), whose audit rows carry `{scope, key}` and can
therefore prove a change occurred without being able to show what it was. An
audit that records only that something happened answers the compliance question
and not the operational one.

Both limits are worth stating with it, because they bound what this buys. The
file is append-only by file handle, not by storage — nothing signs or chains it,
so it defends against accident rather than against an adversary with disk access.
And the log path defaults to `$HOME`, so a process without one has no log at all:
deletes then fail loudly, which is correct, while stores go silently unlogged,
which is not.

[Atomic Agent](../../systems/atomic-agent/) is now the clearest implementation,
and its shape is the one to copy:

```sql
vote_events (id, kind, target_id, direction, session_id, turn_index, created_at)
-- and, derived from it:
memories.vote_score, lessons.vote_score, profile_facts.vote_score  (indexed)
```

The events are the record; the scores are a projection. A scoring rule can be
changed and recomputed, a suspicious voting pattern can be audited, and no single
vote is destructive. Set against the alternatives the atlas has collected —
[Holographic](../../systems/holographic/) mutating a trust score in place until a
fact falls below the retrieval floor, [RainBox](../../systems/rainbox/) holding
feedback behind a human gate, [MetaClaw](../../systems/metaclaw/) letting
telemetry tune retrieval policy through a promotion gate — the append-only log is
the option that preserves every one of those choices for later.

[Magic Context](../../systems/magic-context/) keeps dedicated mutation logs
(`storage-memory-mutation-log.ts`, `storage-m0-mutation-log.ts`) alongside
per-run dream records, so both what changed and what decided it are retained.

[Daimon](../../systems/daimon/) makes the log **load-bearing rather than
observational**, which is the strongest form this pattern takes: `events.jsonl`
is not a record of what happened to memory, it *is* where liveness lives, folded
at read time on every briefing. That forces two properties most audit logs never
need. The fold keys on the latest event by timestamp rather than by line order,
with same-second ties broken on event *content*, so a reordered or concurrently
written log folds identically. And unknown statuses resolve rather than vanish,
because a writer who bothered to record a lifecycle fact meant something by it.

It also demonstrates when **not** to use one log. Rejections from the
verification gates go to a separate `verification.jsonl`, and the source explains
why in a sentence worth copying: the resolutions fold keys on the item reference
alone and treats anything unrecognized as resolved, so a rejection written there
would hide the very item it describes — from the briefing, from carry, and from
search. A demoted memory must stay visible and merely read as less trusted. Any
system tempted to add a `kind` column to one event stream should check what its
own fold does with the new kind first.

[nanobot](../../systems/nanobot/) shows that the audit's *scope* is itself a
design decision. Its git commits are grounded in the real working-tree delta over
an explicit allowlist of durable files — and deliberately exclude
`memory/.dream_cursor` "so progress bookkeeping never appears as a durable-memory
edit in the audit record." The log reads as a history of what the agent came to
believe, not of its counters.

One failure is worth naming because a project fixed it in public.
[ouroboros](https://github.com/razzant/ouroboros) journals every mutation of its
scratchpad and identity files, and a comment records what went wrong first:

> "An honest journal (P1): a failed write must be journaled as a failure and
> surfaced to the caller — the old path logged `block_appended` success for a
> block that was never persisted."

**An audit log that records only successes is not an audit log.** It is a record
of intentions, and it is worse than no log, because it is trusted. The fix is
two-part: journal the failure with its own event type, and re-raise so the
caller cannot proceed believing the write landed. Any append-only memory audit
needs a test that a failed write produces a failure event and an error, not
silence.

[RainBox](../../systems/rainbox/) combines claim/evidence state with
`RetrievalEvent`, feedback, review UI, and eval flows, while explicitly treating
telemetry as a review signal rather than truth. [Mem0](../../systems/mem0/) keeps
SQLite history around memory changes. [llm-wiki-memory](../../systems/llm-wiki-memory/)
uses git history for inspectable mutation groups — and demonstrates why audit
history is not privacy erasure.

[Nova AI](../../systems/nova-ai/) puts the log on the record and pays the
scaling cost for it. `ensure_concept` seeds an `audit_log` array on every
concept, and creation, sense upgrade, confidence change and relation add each
append an entry carrying `old_value`, `new_value`, the source and a timestamp,
mirrored to an external `logs/concepts.jsonl`. Exporting one concept exports its
whole history, which is the placement NOOA argues for. The cost is visible in the
same file: the store is one JSON document rewritten in full on every save, so the
history that makes a concept auditable is also what a single confidence bump
rewrites — and non-atomically. It is also the atlas's sharpest demonstration that
an audit log is not a correction mechanism: Nova can say exactly when and from
whom it learned something wrong, and has no code anywhere that removes it.

[memU](../../systems/memu/) is the clean separation of the two halves, one of
which is missing. Its event spool is careful about everything telemetry is
usually careless about — an allowlist per event type, no query text, bounded
payloads — and it records that a retrieval happened and how many results came
back. It records nothing about what changed in the store, it is deleted once
delivered, and it is addressed to a vendor analytics endpoint rather than to the
memory. A system can have a considered account of its own operation and no
account of its own contents, and this is what that looks like.

[NOOA Memory](../../systems/nooa-memory/) takes the opposite arrangement to
everything else here and states why: the access log "lives ON the record (capped
ring in `Memory.access_log`): copy or export one row and its usage story travels
with it." Each entry carries the score components that produced the retrieval —
`{rel, rec, imp, spread}` — plus the rank, the truncated query, the reader's
owner, and a trace span id. That answers "why was this surfaced" in a way a
separate event stream makes harder, since the interesting question is almost
always about one memory. The price is written into the design: a ring buffer
drops the earliest accesses, which are the ones explaining how a memory became
established. Both arrangements are defensible; only one of them is usually
chosen deliberately.

[CSM](../../systems/csm/) is the atlas's only implementation of the third bullet
below — *distinguish considered, returned, and injected memories* — and it is
worth copying whole. Alongside a conventional mutation stream (`memory_events`
for created/deleted/retention-cleanup, `memory_merges` for each merge with its
normalized hash) it writes a second pair of tables for **assembly**:
`context_injection_events` holds one row per injected block with an idempotency
key, a `block_hash`, a `builder_version` and a `config_hash`, and
`context_injection_items` holds one row per *candidate*, carrying its layer,
position, selection rank and score, a `disposition` of
`injected | trimmed | omitted`, and a `selection_reason_code` drawn from a
closed set — `importance_rank`, `recent_session`, `explicit_preference`,
`active_goal`, `budget_trim`, `layer_budget_exhausted`, `filter_rejection`,
`empty_source`.

The distinction that makes it useful is between the last three. A mutation log
tells you the memory exists; a recall log tells you it was found; only this tells
you it was found, ranked fourth, and lost to a layer budget — which is the
actual answer to "why didn't the agent know that?" and the one no other audit
shape in this atlas can produce. The `builder_version` and `config_hash` matter
for the same reason: without them, an old row cannot be read against the
selection rules that produced it. The cost is one row per considered item per
turn, which is the highest write volume of any audit design here, and CSM
attaches no retention policy to it.

[LoreKit](../../systems/lorekit/) contributes the cheapest correct
implementation of the invariant and the sharpest warning about what it buys.
The implementation: `audit_log` carries a SELECT policy and an INSERT policy and
**deliberately no UPDATE and no DELETE policy**, so immutability is enforced by
row-level security rather than by everyone remembering not to write the
statement. The migration numbers the choice (Decision D5) and says why app-layer
capture beats a trigger on the data tables — application code can see the
resolved actor and shape a human-readable target — then names the single table
where no call site exists and a trigger is therefore the right answer. Eleven
actions are pinned in a CHECK constraint.

The warning is what the log then cannot answer. Every mutation is recorded with
`{scope, key}` as its metadata, and the write path is an in-place upsert with no
version chain — so the log proves that a memory changed, by whom and when, and
**cannot show what it replaced**. That is a complete answer to "who touched
this?" and no answer at all to "what did it used to say?", which in a memory
system is usually the question being asked. The two properties look like one
feature and are not: an audit trail is about *actors*, and memory history is
about *values*. If you want both, put the old value in the log or keep the
version — deciding you have history because you have an audit log is the failure
this entry exists to name.

## Tests to require

- Mutation and audit event commit or roll back together.
- Distinguish considered, returned, and injected memories.
- Rebuild derived counters from the event stream.
- Deduplicate retried event writes.
- Apply scope authorization to audit queries.
- Exercise retention and true-erasure procedures across events and backups.

## Related patterns

- [Governed write gateway](../governed-write-gateway/)
- [Evidence before belief](../evidence-before-belief/)
- [Rejected-value tombstone](../rejected-value-tombstone/)

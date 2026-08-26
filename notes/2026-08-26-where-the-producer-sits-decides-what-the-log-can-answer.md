# Where the producer sits decides what the log can answer

**Status:** synthesis. Written 2026-08-26 over six readings in three days —
aimee, Fireweed MCP (twice), OpenWorker (re-pin), OpenCompany, AgenticTrading,
OpenExecutive.
**Why:** each of these has an audit story in its own report, and the reports
argue about whether a given log earns `audit_log`. The interesting thing is not
the verdicts. It is that the six of them form a clean ordering on one variable —
*where the code that writes the log lives* — and that variable predicts what the
log can answer better than how well the log is built.

---

## The ordering

Sorted by how far the producer sits from the thing being recorded, closest
first.

**1. A database trigger.** aimee's `memory_evidence_events` is written by
`AFTER INSERT OR UPDATE OR DELETE` triggers on nine tables — `memories`, `docs`,
`document_versions`, `entity_registry`, `entity_aliases`, `rel_types`,
`derived_memory_registry`, `memory_scopes`, `memory_links` — plus
`evidence_change_item_event()` on the fact-graph commit path. Each row carries
`authenticated_actor`, `transport_identity`, `effective_authority`, a
`changeset_id`, before and after refs, and the source span and hash, under
`CHECK` constraints over a fourteen-value object kind and a twelve-value
operation.

The coverage question here is *which tables carry the trigger*. It is not
*which call sites remembered*, because application code cannot forget to call a
trigger. This is the only arrangement in the six where a new write path is
audited by default rather than by discipline.

**2. A chokepoint the writes already pass through.** OpenWorker's
`AuditStore` records connector and tool actions, and `self._audit(tool_call,
stage="proposed")` sits in the common loop over every tool call before any
branching. Memory writes go through it *because memory is a tool* — `remember`,
`memory_update` and `memory_forget` are recorded with their arguments, secrets
redacted, whether or not they succeed.

Coverage is a property of the architecture rather than of the audit code: it
holds exactly as long as every memory write is a tool call. Nobody wrote a
memory-audit feature; they wrote memory as a tool and got the audit.

**3. Per-call-site emits.** OpenCompany's `runtime_mutations` row is committed
in the same transaction as the mutation, which is the right *transactional*
placement — but only when `mutation_id` is supplied, and `_operation_id` returns
`Optional[str]`, resolving a caller-supplied `tool_call_id`, `request_id` or
`operation_id` and returning `None` when there is none. A mutation without one
is applied and unrecorded. The table's purpose is idempotency, and the record of
the mutation is a side effect of that purpose.

**4. Built and not attached.** Fireweed MCP at its first pin: `ledger.py`
implemented a gap-free hash-chained append-only log with a closed event
vocabulary and a `resolver_version` stamped into every payload, `graph.py` had
`attach_ledger`, `seal()` and an `_emit` guard — and nothing called
`attach_ledger`, so `_emit` took its silent early return on every write. The log
was excellent and empty. At the second pin, one call at server start plus
`seal()` on the next line, and it covers everything.

**5. Attached to the wrong side.** OpenExecutive is the one worth the note.
`openexecutive/audit/` has a logger, a redaction module, a filterable read API,
a session timeline, and a derived causality graph so a UI can draw the flow of a
turn. The vocabulary is closed and declared. Two of its fourteen event types
name memory and **both are reads**: `memory_snapshot` is *"episodic context +
company profile at turn entry"*, `peer_memory` is a prefetch outcome. The
episodic module emits nothing. The `/memories/*` PATCH and DELETE routes — a
human editing or deleting an extracted memory — emit nothing.

**6. No producer at all.** AgenticTrading's 7,784-line memory service has no
audit surface in the memory package.

---

## What the ordering buys

The claim is narrow and I think it holds: **you can predict what a memory audit
log will fail to answer from where its producer sits, without reading the
schema.**

- Trigger → answers everything about the tables it covers; fails only where a
  table lacks the trigger.
- Chokepoint → answers everything that goes through the chokepoint; fails when
  a write path bypasses it.
- Per-call-site → fails wherever a caller omitted the optional argument, and
  those omissions are invisible in the log by construction.
- Unattached → fails silently and completely, and looks identical to a system
  with nothing to record.
- Wrong side → answers the debugging question and never the accountability one.

The fifth is the one I had not seen stated before, and it is the reason this
note exists. OpenExecutive's log is *better built* than OpenWorker's — closed
vocabulary, redaction module, causality graph, a purpose-built read API — and
answers strictly less about memory, because OpenWorker's producer sits in a loop
every write passes and OpenExecutive's producers sit on the retrieval paths.
Quality of implementation and coverage are independent axes, and only one of
them is visible when you read the audit module.

---

## The rubric already knew, and I did not

The atlas's `audit_log` definition ends with a clause I had read many times
without extracting the general point:

> *"Logs of retrieval or feedback are the other half of the pattern and do not
> count here, nor does git history."*

That is exactly case 5. The definition was written to exclude a retrieval log
standing in for a mutation log, and OpenExecutive is the cleanest instance the
corpus has: everything about it is right except which arrows it draws.

The practical version for a builder, and the thing I would say first if asked:
**write down the question your log has to answer, then find the narrowest place
every answer must pass through, and put the producer there.** "What did the
agent know when it said that" and "where did this memory come from" are
different questions with different chokepoints, and a log built for the first
will not answer the second no matter how good it is.

---

## A second-order finding, which is about me

The aimee report's first version carried an open question asking whether memory
mutations were audited at all. They were — through
`memory_evidence_events`, case 1 above — and I missed it because I went looking
for the *WORM* store the system also has, found its producers were vault rewrap
and guardrail actions, and stopped. Two ledgers, and I checked the one whose
name sounded more like an audit log.

The generalisable correction: **a system can have more than one log, and the one
that covers memory may not be the one that advertises itself as the audit
trail.** Grep for the memory tables in trigger definitions before concluding
anything about coverage. That defence is mechanical, it costs one command, and
it would have prevented a published error.

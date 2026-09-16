---
title: "Osiris"
eyebrow: "Parsers stopped writing confidence numbers and started declaring how they knew"
description: "An event-sourced entity graph for agents where a fact's confidence is a projection of how it was obtained, corroboration is recomputed at read time because storing it would go stale, and every mutation commits its audit row in the same transaction."
root: ../..
page_kind: system
source_name: "asuramaya/osiris"
source_url: https://github.com/asuramaya/osiris
archive_name: "asuramaya--osiris"
revision: 5de1b36678aa6d41c0a5e4c5f13619de569012a3
revision_url: https://github.com/asuramaya/osiris/commit/5de1b36678aa6d41c0a5e4c5f13619de569012a3
analyzed_at: 2026-09-16
capabilities: "trust_state, audit_log"
capability_evidence:
  trust_state: "a stored object status maintained as a projection of the event log, which reads filter on alongside the merge pointer | src/actions/core.py:7-12, :688-692, src/mcp_server.py:3062, :4204, src/cli.py:4852 | The actions layer states the model: \"merges are *event-sourced*: ``object_events`` is the source of truth and ``objects.status``/``merged_into`` are a projection updated alongside.\" Reads carry the predicate — `WHERE o.type='Thread' AND o.status='active' AND o.merged_into IS NULL`, `WHERE o.type='Decision' AND o.status='active'`, and agent lookups requiring `status='active'` — so a merged object stays in the graph and stops being returned. Unmerge is a first-class action that \"[r]estores the merged object to active and clears the projection\" under a stated rule of never deleting, so the status is reversible rather than terminal | tests/"
  audit_log: "one mutation path, and each method commits the domain write, its audit row and its event rows in a single transaction | src/actions/core.py:1-13 | The module header is the contract: \"The Actions layer — the *only* mutation path into the ontology. Every method is atomic: the domain write, its ``audit_log`` row, and any ``outbox`` / ``object_events`` rows all commit in one transaction. UI clicks, helper outputs, and analyst edits must all go through here. No bypassing.\" Beneath it the assertions table is append-only with a *backward* `supersedes` pointer and \"old rows are never mutated\", supersession scoped within a source rather than across the multi-source set, and cascades routed through a durable outbox \"(not fire-and-forget pub/sub)\" so a downstream effect cannot be lost independently of the write that caused it | src/actions/core.py:476, :621, :688"
stack_storage: "postgres"
stack_retrieval: "lexical, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "An object of a declared type with graded properties, links and provenance; an assertion is one source's claim about a property, appended and never mutated"
  storage: "PostgreSQL 16 with `pg_trgm`, a Redis 7 event bus, an append-only assertions table, an `object_events` log and a durable outbox"
  retrieval: "Graph traversal and trigram search over active objects, with an evidence-graded view of why each node is present"
  write: "One actions layer; every parser declares an evidence class rather than a confidence number"
  update_delete: "Assertions append with a backward `supersedes` pointer; merges are events with a status projection, and unmerge restores an object to active under a never-delete rule"
  scoping: "A self-hosted single graph; agents, projects and threads are object types rather than isolation boundaries"
  integration: "A streamable-HTTP MCP server, native Claude Code hooks, and a plugin for another harness"
  background: "A crawl frontier, a dissemination layer, workers and an orchestrator composing capabilities"
  trust: "An evidence-class taxonomy that replaces per-parser confidence numbers, corroboration computed at read time, provenance on every property and link, and an audit row per mutation"
  strengths: "The evidence module fixes a failure this atlas keeps finding and names it precisely: \"[b]efore this module, every parser invented its own confidence number (0.4 → 0.99) with no shared meaning, so 'noise' was baked into the graph as fake-precise facts and nothing downstream could reason about *why* a node was believed.\" Now a parser declares an `EvidenceClass` — self-declared, authoritative API, direct observation, derived, co-occurrence — and the confidence column becomes \"a *projection* of the class, not a guess\". The sixth class is the one to copy: CORROBORATED \"is never assigned by a parser — it is computed at read time when ≥2 independent sources agree … Storing it would go stale the moment a third source lands\", and it ranks above a single authoritative source. A corroboration that cannot be self-asserted and is recomputed rather than cached is the shape OWASP's agent-memory guard describes as a threat when it is missing. The write path matches: one actions layer, \"[n]o bypassing\", every method committing the domain write, its audit row and its event rows together, append-only assertions with a backward supersedes pointer, and cascades through a durable outbox rather than fire-and-forget pub/sub. The ontology is a declared catalog so \"[a] new type is a new entry here (reviewed), never an inline string\""
  risks: "There is no isolation boundary. Agents, projects and threads are object types in one graph rather than partitions of it, so what separates one agent's memory from another's is the graph's shape and not a predicate a reader cannot omit — which suits a self-hosted single-operator deployment and is the thing to establish before a shared one. The evidence classes grade and rank but never withhold: a co-occurrence fact at 0.35 is returned beside a self-declared one at 0.9, so a consumer that ignores the class sees them as peers, and the protection is in the reader's discipline. Base confidences are constants with no stated derivation, so the numbers are a shared ordering rather than calibrated probabilities — which is what the module intends, and worth saying since a consumer may read 0.85 as a likelihood. And at 269,603 lines of Python with a 12,403-line MCP server and an 8,328-line CLI, a reader after the evidence taxonomy and the actions layer is reading about two percent of the tree"
---

## 1. Executive Summary

Osiris is "[t]he persistent memory and coordination graph for AI agents" —
AGPL-3.0, Python 3.12+, 269,603 lines with 6,388 test functions, over PostgreSQL
16 with `pg_trgm` and a Redis 7 event bus, exposed as a streamable-HTTP MCP
server with native Claude Code hooks. It describes itself as
"[a] self-hosted, harness-agnostic, provenance-first entity-graph engine",
turning agent reasoning, architectural rulings, loose ends and inter-agent
messages into "durable, queryable, event-sourced graph memory across context
windows, compactions, and harness boundaries".

The module to read is eighty lines long and fixes something this atlas finds
almost everywhere.

**Parsers stopped writing confidence numbers.** The evidence module opens with
the defect:

> "Before this module, every parser invented its own confidence number (0.4 →
> 0.99) with no shared meaning, so 'noise' was baked into the graph as
> fake-precise facts and nothing downstream could reason about *why* a node was
> believed. Here we grade each fact by HOW it was obtained, and derive its
> confidence from that class. Parsers stop writing numbers; they declare an
> `EvidenceClass`."

Five classes a parser may declare — self-declared, authoritative API, direct
observation, derived, co-occurrence — each projecting a base confidence. The
`confidence` column survives because the constraint, the entity-resolution
scorers and the report views read it, "but it is now a *projection* of the class,
not a guess".

**The sixth class cannot be claimed.** CORROBORATED:

> "is never assigned by a parser — it is computed at read time when ≥2
> independent sources agree … Storing it would go stale the moment a third source
> lands."

Two things there. Corroboration requires *independent* sources, so an agent
restating its own claim does not manufacture it — the failure
[OWASP's memory guard](../agent-memory-guard/) describes as a threat and most
systems here leave open. And it is recomputed rather than cached, because a
stored corroboration is a claim about a world that keeps changing. It ranks above
a single authoritative source in the strength order, which is the correct
ordering and the one a cached flag would eventually get wrong.

**One write path, and the audit row rides with the write.** The actions layer's
header is the contract:

> "The Actions layer — the *only* mutation path into the ontology. Every method is
> atomic: the domain write, its `audit_log` row, and any `outbox` /
> `object_events` rows all commit in one transaction. UI clicks, helper outputs,
> and analyst edits must all go through here. No bypassing."

Underneath: assertions are append-only with a *backward* `supersedes` pointer and
"old rows are never mutated"; supersession is scoped within a source rather than
across the multi-source set, so one source correcting itself does not silence
another; merges are events with `objects.status` and `merged_into` maintained as
a projection; and cascades go through a durable outbox "(not fire-and-forget
pub/sub)", so an effect cannot be lost independently of the write that caused it.

That status is the second mark. Reads carry it — `o.status='active' AND
o.merged_into IS NULL` on threads, `o.status='active'` on decisions and on agent
lookups — so a merged object stays in the graph and stops being returned. Unmerge
is a first-class action that restores it to active and clears the projection,
under a rule of never deleting.

The ontology is a declared catalog rather than a framework: "[a] new type is a new
entry here (reviewed), never an inline string", after types were "invented inline
by each parser and scattered across the UI, the parsers, and the docs". Every
surface — the UI's colours and shapes, the generic object view, the validators —
reads the one catalog.

What is not here is an isolation boundary. Agents, projects and threads are
object types inside one graph, not partitions of it, so what separates one
agent's memory from another's is the graph's shape rather than a predicate a
reader cannot omit. For a self-hosted single-operator deployment that is
coherent; it is the thing to establish before a shared one.

And the evidence classes grade and rank but never withhold. A co-occurrence fact
at 0.35 comes back beside a self-declared one at 0.9, so a consumer that ignores
the class treats them as peers — the protection lives in the reader. The base
confidences are constants with no stated derivation, which is what the module
intends (a shared ordering, not calibrated probabilities) and worth naming
because a downstream reader may take 0.85 for a likelihood.

## 2. Mental Model

An **assertion** is one source saying one thing. It is never edited.

A **confidence** is not something a parser chooses. The *class* is.

**Corroboration** is a question asked at read time, never an answer stored.

A **merge** is an event; the status is only its shadow.

```mermaid
%% caption: a parser declares how it knew rather than how sure it is, and corroboration is recomputed from independent sources instead of being stored
flowchart TB
    P["a parser produces a fact"] --> DECL{"declare an EvidenceClass —<br/>parsers no longer write numbers"}
    DECL --> C1["SELF_DECLARED · 0.9"]
    DECL --> C2["AUTHORITATIVE_API · 0.85"]
    DECL --> C3["DIRECT_OBSERVATION · 0.6"]
    DECL --> C4["DERIVED · 0.4"]
    DECL --> C5["CO_OCCURRENCE · 0.35"]
    C1 & C2 & C3 & C4 & C5 --> ACT{"the Actions layer —<br/>the ONLY mutation path.<br/>'No bypassing.'"}
    ACT --> TX[("one transaction:<br/>the domain write +<br/>its audit_log row +<br/>its object_events / outbox rows")]
    TX --> ASSERT[("assertions — append-only,<br/>a BACKWARD supersedes pointer,<br/>old rows never mutated;<br/>supersession is within-source")]
    TX --> EV[("object_events — the source of truth<br/>for merges")]
    EV --> PROJ["objects.status / merged_into —<br/>a projection updated alongside"]
    PROJ --> READ{"reads"}
    READ -->|"status='active' AND merged_into IS NULL"| OUT["returned"]
    READ -->|"merged"| HELD["stays in the graph,<br/>stops being returned;<br/>unmerge restores it — never delete"]
    FRONT["read time: the crawl frontier<br/>and the subject report"] --> CORR{"≥2 INDEPENDENT sources agree?"}
    CORR -->|"yes"| CO["CORROBORATED · 0.8 —<br/>ranks above a single authoritative source"]
    CORR -.->|"'never assigned by a parser …<br/>storing it would go stale the moment<br/>a third source lands'"| NOSTORE["not a column"]
    OUT --> FRONT
    CAT["the ontology catalog:<br/>'a new type is a new entry here (reviewed),<br/>never an inline string'"] --> ACT
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `src/actions/core.py` | The only mutation path, and its invariants |
| `src/parsers/evidence.py` | The evidence-class taxonomy and its projections |
| `src/ontology/` | The declared catalog, labels, entity resolution |
| `src/orchestrator/` | The frontier, sources, compositions |
| `src/mcp_server.py` | The agent surface (12,403 lines) |
| `src/cli.py` | The operator surface (8,328) |
| `src/workers/`, `src/dissemination/` | Background work and delivery |

## 4. Essential Implementation Paths

`src/parsers/evidence.py:1-41` — the defect, the classes, and the one that
cannot be claimed.

`src/actions/core.py:1-13` — one path, one transaction, three invariants.

`src/ontology/schema.py:1-21` — why the catalog exists and what it is not.

## 5. Memory Data Model

Objects of declared types with graded properties and links, every property and
link carrying provenance as a kernel-wide invariant. An assertion is one source's
claim; the multi-source set is preserved because supersession is within-source,
which is the detail that keeps a self-correcting parser from silencing an
independent one — and is also what makes read-time corroboration meaningful.

## 6. Retrieval Mechanics

Graph traversal and trigram search over active objects, with the frontier reading
the evidence class to decide "what is the strongest reason this node is here".
Ranking by strength rather than by a raw number is what the class taxonomy buys.

## 7. Write Mechanics

Covered above. The unmerge path is worth a second look: it restores the merged
object to active and clears the projection while leaving assertions in place —
"resolve-on-read" — so undoing a merge does not require rewriting anything that
was asserted.

## 8. Agent Integration

A streamable-HTTP MCP server, native Claude Code hooks, and a plugin for another
harness. Screening flags three auto-run surfaces, which is what a hook-installing
MCP server looks like.

## 9. Reliability, Safety, and Trust

The evidence taxonomy and the single write path are the trust story, and they are
complementary: one makes it impossible to write a fact without saying how it was
obtained, the other makes it impossible to write anything without recording that
it happened.

The gap is enforcement at read time. Nothing withholds a weakly-graded fact, and
nothing partitions one agent's view from another's.

## 10. Tests, Evals, and Benchmarks

6,388 test functions, with the largest suites covering capture, triggers, the CLI
and agents. Nothing was installed or run for this reading.

## 11. For Your Own Build

Grade the fact by how you got it, then derive the number. A parser that picks
0.72 is guessing; a parser that says "co-occurrence" is reporting, and the number
becomes a shared ordering everyone downstream can reason about.

Never let corroboration be self-asserted or stored. Require independent sources,
compute it at read time, and the third source that arrives tomorrow changes the
answer instead of contradicting a cached flag.

Commit the audit row in the write's transaction. An audit that can fail
separately from the mutation is an audit with silent gaps.

Scope supersession to the source. One source correcting itself should not delete
another source's disagreement, and the multi-source set is what corroboration is
computed over.

And put the type catalog in one reviewed place. Types invented inline by each
parser is the state this project migrated away from, and the migration is the
evidence that it costs something.

## 12. Open Questions

Whether anything filters by evidence class. The classes rank and project a
confidence; no read was found that withholds below a threshold.

What isolates one agent from another. Agents are object types in a shared graph,
and no partition predicate was found.

How the base confidences were chosen. They are constants with a stated ordering
and no stated derivation.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `src/parsers/evidence.py:1-41` | Numbers replaced by classes, and one class that cannot be claimed |
| `src/actions/core.py:1-13` | One mutation path and what rides with every write |
| `src/actions/core.py:688-692` | Unmerge, restore, never delete |
| `src/ontology/schema.py:1-21` | A catalog, not a framework |

## History

**2026-09-16** — [`5de1b36678aa6d41c0a5e4c5f13619de569012a3`](https://github.com/asuramaya/osiris/commit/5de1b36678aa6d41c0a5e4c5f13619de569012a3) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: eleven files scanned, three auto-run surfaces, one build-time execution point, no unpinned surfaces and three dependency files inside the seven-day cooldown. Nothing was installed, built or run.

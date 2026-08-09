---
title: Neo4j Agent Memory
eyebrow: Memory of its own reasoning
description: A graph-native memory whose third tier records how the agent reasoned and which tools worked — captured through a context manager, so failures are stored automatically rather than only successes.
root: ../..
page_kind: system
source_name: neo4j-labs/agent-memory
source_url: https://github.com/neo4j-labs/agent-memory
revision: b017db4449d592a982944986c2e3c18652bb36ad
revision_url: https://github.com/neo4j-labs/agent-memory/commit/b017db4449d592a982944986c2e3c18652bb36ad
analyzed_at: 2026-07-28
capabilities: "bitemporal, scope_enforced"
stack_storage: "graph"
stack_retrieval: "vector, graph"
stack_source: "seeded"
matrix:
  memory_unit: "Conversation turn, extracted entity, preference, and reasoning trace with tool calls"
  storage: "Neo4j — one graph shared across agents rather than per-agent silos"
  retrieval: "Graph queries over entities and relationships; embeddings; reasoning steps with parent context"
  write: "Conversation capture, GLiNER extraction pipeline, traces recorded via a context manager"
  update_delete: "`supersede_preference`, idempotent, with `valid_from` / `valid_until` bounds"
  scoping: "Multi-tenant mode that raises when a user identifier is missing"
  integration: "MCP server, CLI, AWS Strands tools, OpenAI Agents SDK examples"
  background: "Consolidation; extraction pipeline"
  trust: "Trace outcomes with success, error kind and metrics; no trust state on a fact"
  strengths: "A reasoning tier that captures failures automatically, and fail-closed multi-tenancy"
  risks: "No value-level tombstone; supersession covers preferences rather than every memory kind"
---

## 1. Executive Summary

Neo4j Labs' agent-memory is an Apache-2.0 Python package of about 45,000 lines
under `src/neo4j_agent_memory/`, positioned as "a graph-native memory system for
AI agents… let your agents learn from their own reasoning — all backed by
Neo4j". It complements [Graphiti](../graphiti/), which is also Neo4j-adjacent and
already in this atlas, but is a different package aimed at agent tooling rather
than at temporal knowledge graphs.

Three tiers: short-term, long-term, and **reasoning**. The third is the reason to
read it.

`memory/reasoning.py` records "reasoning traces and tool usage" — and it records
them through a **context manager**, which means the interesting case is handled
without anyone remembering to handle it:

```python
self._outcome = str(exc_val) if exc_val else f"Error: {exc_type.__name__}"
```

When a traced task raises, the exception becomes the trace's outcome on the way
out. **Failures are stored by default.** Nearly every procedural-memory system in
this atlas records successes — [Voyager](../voyager/) writes a skill only after
verified execution, and the
[skills as procedural memory](../../patterns/skills-as-procedural-memory/)
pattern is built around that gate. Storing what *did not* work is the other half,
and it is rare: [Verel](../verel/) has a failure ledger and little else here does.

The outcome is structured rather than a string:

```python
class TraceOutcome(BaseModel):
    """Structured outcome attached to a reasoning trace at completion time."""
    success: bool
    summary: str
    # plus an indexable error kind, structured related entities, and metrics
```

with the docstring noting it "lets a caller attach an indexable error kind…
while remaining fully back-compatible with the legacy string + boolean API". An
*indexable error kind* makes "what else failed this way" a query.

Two more things are worth a builder's attention. Multi-tenancy is **fail-closed**
— `_enforce_multi_tenant` "raise[s] if multi-tenant is on and `user_identifier`
is missing", so the dangerous default of returning everything is unreachable once
the mode is on. And preferences carry `valid_from` / `valid_until` with an
`supersede_preference` that is explicitly "idempotent: re-running on an
already-superseded preference is a" no-op.

Reservations: bi-temporal validity and supersession apply to *preferences*, not
to every memory kind; there is no value-level tombstone; and the reasoning tier's
value depends on retrieval surfacing past failures at the moment they would help,
which was not traced.

## 2. Mental Model

| Store | Holds |
| --- | --- |
| short-term | conversation turns, recent context |
| long-term | entities, relationships, preferences — a preference carries `valid_from` and `valid_until`, and `supersede_preference(old, new)` is **idempotent** |
| reasoning | a trace of steps and tool calls; the with-block makes success *or* the raised exception the outcome on exit, recorded as `TraceOutcome{success, summary, error kind, entities, metrics}` |

Two details worth taking. Preferences are the only thing here with validity time,
and an idempotent supersede means a retried write cannot double-supersede. And the
reasoning trace cannot silently succeed: leaving the block always records an
outcome, including the exception.

All three live in **one Neo4j instance shared across agents** rather than in
per-agent stores — the stated position being a single brain rather than silos.

How a memory stops being current: a preference is superseded and its
`valid_until` closes. Nothing else has a defined end state, and nothing records
that a value was judged wrong.

```mermaid
flowchart TB
    Turn["Conversation turn"] --> Cap["Capture"]
    Cap --> GL["GLiNER extraction"]
    GL --> G[("One Neo4j graph<br/>shared across agents, not per-agent silos")]
    Trace["Reasoning trace<br/>recorded via a context manager"] --> G
    Pref["Preference"] --> Sup["supersede_preference<br/>idempotent, valid_from … valid_until"]
    Sup --> G
    G --> Q["Graph queries over entities<br/>and relationships; embeddings;<br/>reasoning steps with parent context"]
    G -.->|"multi-tenant mode raises when<br/>a user identifier is missing"| Scope["fail-closed tenancy"]
    Sup -.->|"covers preferences only"| Gap["no value-level tombstone"]
```

## 3. Architecture

`src/neo4j_agent_memory/` — `memory/long_term.py` (2,357), `__init__.py` (1,827),
`memory/short_term.py` (1,727), `memory/reasoning.py` (1,394),
`graph/queries.py` (1,385), `extraction/gliner_extractor.py` (1,256),
`integrations/strands/tools.py` (1,014), `mcp/_tools.py` (963),
`cli/main.py` (954), `config/settings.py` (823), `extraction/pipeline.py` (787),
plus `core/`, `llm/`, `embeddings/`, `nams/`, `observability/`,
`memory/consolidation.py`, `memory/users.py`, `memory/eval.py`.

Entity extraction uses GLiNER — a local NER model — rather than an LLM call,
which puts a meaningful part of the write path outside the token budget.

### Deployment and ergonomics

Needs a Neo4j instance; there is a `docker-compose.test.yml` and a `deploy/`
tree. Beyond that it is a Python package with an MCP server, a CLI, and
integrations for AWS Strands and the OpenAI Agents SDK.

The shared-graph design is the ergonomic trade: one database to run, and every
agent sees the same entities — which is the point, and also means a mistake by
one agent is visible to all of them.

## 4. Essential Implementation Paths

### Failures recorded because the control flow records them

The context-manager shape is what makes this reliable rather than aspirational. A
system that asks callers to log failures gets failure logs proportional to
discipline; a system where `__exit__` captures the exception gets them
proportional to coverage.

The atlas has repeatedly noted that memory systems remember what worked. The
[skills as procedural memory](../../patterns/skills-as-procedural-memory/)
pattern's gate — write only on verified execution — is correct and one-sided: an
agent that has failed the same approach four times has learned nothing, because
nothing wrote it down. Here the failing path is the *default* path.

`ReasoningStepWithContext` — "a reasoning step plus its parent trace's task and
outcome" — matters for the same reason. A step retrieved without knowing whether
the attempt it belonged to succeeded is worse than useless, because it reads as
precedent.

### An indexable error kind

Attaching a typed error kind alongside the human-readable summary turns the trace
store into something queryable by failure mode rather than by text similarity.
"Show me every trace that failed with a timeout against this tool" is a graph
query; against a free-text outcome it is a guess.

The back-compatibility note is worth copying too — the structured outcome was
added without breaking the string-plus-boolean callers, which is how a schema
gets richer in a released package rather than in a rewrite.

### Fail-closed multi-tenancy

```python
def _enforce_multi_tenant(self, user_identifier: str | None) -> None:
    """Raise if multi-tenant is on and ``user_identifier`` is missing."""
```

The [scope as a first-class key](../../patterns/scope-as-a-first-class-key/)
pattern asks for scope on the read path. This adds the posture: with the mode on,
a query that forgets the tenant **fails** rather than returning the union. The
common bug in scoped stores is not a missing filter clause — it is a code path
where the filter is optional and someone omitted it.

The cost is that the guard depends on the mode being on, which is a
configuration, not a constraint.

### Bi-temporal preferences, superseded idempotently

`valid_from` is set to now on write; `valid_until` "stays null until
`supersede_preference`", which is idempotent — re-running on an already-superseded
preference does nothing. The code notes a "v0.5 bi-temporal time-travel API on
top of `valid_from` / `valid_until`".

Idempotency in a supersession path is a small thing that prevents a specific
mess: a retried consolidation pass that closes an interval twice, producing a
preference whose validity bounds no longer describe anything.

The limitation is the scope of it. Preferences get validity intervals; entities,
relationships and reasoning traces do not, so "what did we believe last March"
is answerable for one memory kind.

## 5. Memory Data Model

Conversation turns, extracted entities and relationships, preferences with
validity bounds, and reasoning traces containing steps and tool calls with
statistics.

What is absent:

- **No value-level tombstone.** A superseded preference closes an interval;
  nothing prevents the same value being re-extracted.
- **No trust state.** Outcomes describe whether a *task* succeeded, not whether a
  *fact* is believed.
- **Bi-temporality is partial** — preferences only.
- **The shared graph has no per-agent provenance** traced here, so which agent
  asserted an entity was not established.

## 6. Retrieval Mechanics

Graph queries over entities and relationships (`graph/queries.py`, 1,385 lines),
embeddings, and reasoning-step retrieval that carries parent-trace context.
`memory/eval.py` exists inside the package, and `benchmarks/` provides a runner
and metrics module.

## 7. Write Mechanics

Conversation capture into short-term memory, a GLiNER extraction pipeline into
the graph, traces written by the context manager, and a consolidation module.

### Operational cost

Entity extraction runs on a local NER model rather than an LLM, so the highest-
frequency write path costs no tokens. Trace recording is a graph write. The
consolidation path is where model cost concentrates.

No figures for extraction latency or graph growth were found, and a shared graph
across agents grows with the union of their activity rather than with any one
agent's.

## 8. Agent Integration

An MCP server, a CLI, AWS Strands tools (`integrations/strands/tools.py`, 1,014
lines), and OpenAI Agents SDK examples. The MCP tool surface is nearly a thousand
lines, so the integration is a first-class part of the package rather than a
wrapper.

## 9. Reliability, Safety, and Trust

Strengths:

- **Failures captured by control flow**, not by caller discipline.
- **Structured trace outcomes** with an indexable error kind and metrics.
- **Reasoning steps carrying their parent's outcome**, so a step is never read
  as precedent without knowing whether it worked.
- **Fail-closed multi-tenancy.**
- **Idempotent supersession** with validity bounds.
- **Local NER extraction**, keeping the frequent write path off the token budget.
- **A benchmarks tree and an in-package eval module.**
- **Schema extended back-compatibly** rather than by rewrite.

Gaps:

- **No value-level tombstone.**
- **Bi-temporality limited to preferences.**
- **No trust state on facts.**
- **A shared graph means shared mistakes** — one agent's bad extraction is every
  agent's context, and no per-agent provenance was traced.
- **The tenancy guard is conditional** on a configuration flag.

## 10. Tests, Evals, and Benchmarks

A `benchmarks/` tree with `runner.py` and `metrics.py`, an in-package
`memory/eval.py`, a `docker-compose.test.yml`, and codecov configuration.
Nothing was run for this review and no scored results were located.

The measurement this design invites is whether the reasoning tier changes
behaviour: does an agent with access to its own failed traces stop repeating an
approach? That is a before/after comparison on a fixed task set, and the trace
store is the instrument.

## 11. For Your Own Build

### Steal

- **Record traces with a context manager**, so a raised exception becomes the
  outcome on the way out. Failure memory that depends on callers remembering to
  write it will be proportional to their discipline.
- **Store the failures.** Procedural memory that only holds successes cannot stop
  an agent retrying an approach that has never worked.
- **Give outcomes an indexable error kind**, so the store is queryable by failure
  mode rather than by text similarity.
- **Attach the parent outcome to a retrieved step**, or a step from a failed
  attempt reads as precedent.
- **Make the tenancy guard raise.** A missing scope should be an error, not a
  wider result set.
- **Make supersession idempotent**, so a retried pass cannot close an interval
  twice.
- **Extract entities with a local model** where you can — it moves the highest-
  frequency write off the token budget.

### Avoid

- **Bi-temporality on one memory kind.** Preferences having validity while
  entities do not means "what did we believe then" has a partial answer, which is
  harder to reason about than none.
- **A shared graph without per-agent provenance.** One brain is the design goal;
  not knowing which agent asserted something is a cost of it that should be paid
  deliberately.

### Fit

Right when several agents should share one view of the world and you already run
Neo4j — the shared-graph position is the product, and the reasoning tier is the
best argument for it, since operational history is exactly the thing worth
pooling. Wrong when memories need trust state or durable correction: supersession
here closes an interval on a preference, and nothing stops a re-extraction
putting the old value back.

## 12. Open Questions

- Does retrieval surface past *failures* at the moment they would prevent a
  repeat, or only when queried for?
- Which agent asserted a given entity in the shared graph?
- Why do preferences get validity bounds and entities not?
- What happens to a superseded preference on the next extraction pass over the
  same conversation?
- Have the benchmarks been run, and against what?

## Appendix: File Index

- Reasoning tier: `src/neo4j_agent_memory/memory/reasoning.py`
  (`record_tool_call`, `set_outcome`, `ReasoningStepWithContext`, the
  context-manager exit).
- Trace outcome: `src/neo4j_agent_memory/schema/models.py` (`TraceOutcome`,
  `EntityRef`).
- Long-term and bi-temporality: `memory/long_term.py` (`supersede_preference`,
  `valid_from`, `valid_until`, `_enforce_multi_tenant`).
- Short-term: `memory/short_term.py`; consolidation: `memory/consolidation.py`.
- Graph: `graph/queries.py`; extraction: `extraction/gliner_extractor.py`,
  `extraction/pipeline.py`.
- Surfaces: `mcp/_tools.py`, `cli/main.py`, `integrations/strands/tools.py`.
- Evaluation: `memory/eval.py`, `benchmarks/runner.py`, `benchmarks/metrics.py`.

## History

**2026-07-28** — [`b017db4449d592a982944986c2e3c18652bb36ad`](https://github.com/neo4j-labs/agent-memory/commit/b017db4449d592a982944986c2e3c18652bb36ad) — first reading.

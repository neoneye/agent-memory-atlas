---
title: "M-flow"
eyebrow: "Deterministic first, model second"
description: "A path-cost graph memory whose procedural half puts a cheap deterministic check in front of every expensive one — worth-storing, conflict detection and retrieval triggering are each two-level, rules then a model."
root: ../..
page_kind: system
source_name: "FlowElement-ai/m_flow"
source_url: https://github.com/FlowElement-ai/m_flow
revision: da2766c5ebf45ff10440b419465c8ec0df674022
revision_url: https://github.com/FlowElement-ai/m_flow/commit/da2766c5ebf45ff10440b419465c8ec0df674022
analyzed_at: 2026-08-02
capabilities: ""
stack_storage: "graph"
stack_retrieval: "graph"
stack_source: "seeded"
matrix:
  memory_unit: "Typed graph nodes — Entity, Facet, FacetPoint, Episode — plus a versioned Procedure built from key points and context points"
  storage: "A graph database with Cypher retrieval, alongside lexical and Jaccard retrievers and an episodic bundle store"
  retrieval: "Anchor on the most precise node, then path-cost propagation over typed edges: each hop widens the field and adds cost, so only coherent low-cost paths compete"
  write: "Episodic capture, then a worth-storing screen and a classifier before a procedure is built and indexed"
  update_delete: "Procedures are versioned with conflict detection and a generated version diff; `reconcile_active` decides which version is live"
  scoping: "Not established. No scope key was found applied as a filter on the retrieval path"
  integration: "An MCP server, a frontend, worker queues, an OpenClaw skill and a starter kit"
  background: "Worker tasks that queue memory-node writes and save them out of band"
  trust: "A sensitivity screen on procedural content and usage statistics; no status field withholding a memory from use"
  strengths: "Every expensive step is fronted by a cheap deterministic one — worth-storing, conflict detection and procedural triggering are each two-level"
  risks: "149,000 lines across four packages with no committed retrieval result, so the path-cost claim that distinguishes it is unmeasured in the repository"
---

## 1. Executive Summary

M-flow is a graph memory engine: 149,142 lines of Python, Apache-2.0, 204 commits
since 4 April 2026, HEAD 2 June 2026. It ships a server, an MCP interface, a
frontend, worker queues, a starter kit and an OpenClaw skill.

The retrieval model is the reason to read it. A query lands on **the most precise
anchor it can find** — an Entity, a Facet, a FacetPoint or an Episode — and
evidence then spreads outward over typed edges, where *"each hop expands the
semantic field, but each edge also adds cost. This means association is not a
random graph walk: only paths with coherent, low-cost connections remain
competitive."* The README's own illustration is a classmate who grew up in
California opening a California neighbourhood, within which the Lakers become the
next low-cost hop.

That places M-flow as a third point on an axis this atlas already has two of.
[NOOA Memory](../nooa-memory/) implements ACT-R spreading activation with a fixed
per-hop decay; [HippoRAG](../hipporag/) replaces ranking with PageRank diffusion.
M-flow scores *paths* rather than nodes, so the unit of competition is a chain of
associations and its accumulated cost. Its stated corollary — *"one strong path
is enough"* — is the design's whole bet, and it is the opposite of a system that
requires corroboration from several directions.

**The mechanism worth taking is a discipline rather than a component.** Three
separate places in the procedural half put a cheap deterministic check in front
of an expensive model call, and say so in the docstring each time:

- `retrieval/gating/procedural_trigger.py` — *"Two-layer trigger mechanism:
  Layer 1: Rule trigger (zero cost). Layer 2: LLM light classification (low cost,
  optional)."*
- `memory/procedural/versioning/conflict_detector.py` — *"Two-level conflict
  detection: Deterministic first, LLM fallback."*
- `memory/procedural/governance/worth_storing.py` — a `WorthSignal` screen that
  decides *"whether Procedure is worth storing and indexing"* before anything
  builds one.

This atlas has a pattern page for exactly this
([gate the expensive path](../../patterns/gate-the-expensive-path/)) and most
implementations of it gate once. Doing it three times, at trigger, at conflict
and at capture, with the cost tier named in the comment, is the thing to copy.

The trigger module makes a second distinction worth naming. It separates *should
we retrieve* from *should we inject*: **"Triggers procedural retrieval if any
condition is met (but whether injection is used is decided later)."** Retrieval
being cheap and injection being expensive — in tokens, and in the risk of
polluting a prompt — is a real asymmetry, and almost nothing else here models it
as two decisions.

**What is missing is a number.** For a system whose distinguishing claim is that
path-cost propagation retrieves better than layered retrieval, no committed
benchmark result was found. The claim is architectural, plausible, and unmeasured
in its own repository.

## 2. Mental Model

Two halves with different shapes.

**Semantic and episodic memory is a typed graph.** Entities carry Facets, Facets
carry FacetPoints, Episodes anchor to all of them. The README's argument for the
unified graph is against layered stores: *"Some memory systems keep separate
layers for episodic memories, atomic facts, entities, or summaries. When these
layers are queried separately, retrieval tends to work best when the user's query
matches the selected layer."* Anchoring on whichever node type is most precise,
then spreading, is meant to remove the layer-selection problem — which is a real
problem, and one [MemOS](../memos/) answers by mounting the layers and
[MemPalace](../mempalace/) by making one layer authoritative.

**Procedural memory is versioned.** A procedure is built from key points and
context points (`ContextPointDraft`, `KeyPointDraft`, `ProcedureState`), screened
by `worth_storing`, classified, and then governed: `conflict_detector` compares a
new version against the existing one, `generate_version_diff` produces *"change
descriptions between versions"*, and `reconcile_active` decides which version is
live. `update_usage_stats` records use.

```mermaid
%% caption: three deterministic gates before any model call — a zero-cost rule trigger, a worth-storing screen, and conflict detection that tries deterministic rules before falling back to an LLM
flowchart TD
    Q["query"] --> A["anchor on the most precise node<br/>Entity / Facet / FacetPoint / Episode"]
    A --> P["path-cost propagation over typed edges"]
    P --> R["low-cost coherent paths compete"]
    T["turn"] --> G1{"Layer 1: rule trigger<br/>zero cost"}
    G1 -->|"no"| STOP["no procedural retrieval"]
    G1 -->|"maybe"| G2{"Layer 2: LLM light<br/>classification, optional"}
    G2 --> RET["retrieve procedures"]
    RET --> INJ{"inject? decided later"}
    W["new procedure"] --> WS{"worth_storing screen"}
    WS -->|"no"| DROP["not indexed"]
    WS -->|"yes"| CD{"conflict: deterministic first"}
    CD -->|"unclear"| LLM["LLM fallback"]
    CD --> V["version diff + reconcile_active"]
    style G1 fill:#14532d,color:#fff
    style CD fill:#14532d,color:#fff
    style WS fill:#14532d,color:#fff
```

The three green boxes are the same idea in three places: spend nothing before you
spend something.

## 3. Architecture

Four deployable pieces — `m_flow` (the engine), `m_flow-mcp`, `m_flow-frontend`,
`mflow_workers` — plus `m_flow-starter-kit`, an `openclaw-skill`, Alembic
migrations, a Dockerfile and compose file, and quickstart scripts for shell and
PowerShell. This is a product, not a library, and the operator cost is
correspondingly higher than most of this atlas: a graph database, a worker queue,
and a frontend.

`m_flow/retrieval/` alone is a substantial subsystem — a base graph retriever, a
Cypher search retriever, lexical and Jaccard retrievers, an episodic bundle
search, a unified triplet search, a memory orchestrator and registered community
retrievers. The plurality is worth noting honestly: several retrieval strategies
coexist, and which one runs for a given query is decided by the orchestrator
rather than being a single documented path.

Writes go through workers — `queued_add_memory_nodes.py` and
`memory_node_saving_worker.py` — so node creation is queued and saved out of
band. That is the right shape for a graph write under load and it means a memory
is not immediately retrievable; the lag was not established.

## 4. Essential Implementation Paths

| Path | Location |
| --- | --- |
| Two-layer procedural trigger, cost tiers named | `m_flow/retrieval/gating/procedural_trigger.py` |
| Two-level conflict detection, deterministic then LLM | `m_flow/memory/procedural/versioning/conflict_detector.py` |
| Worth-storing screen before indexing | `m_flow/memory/procedural/governance/worth_storing.py` |
| Version diffs between procedures | `m_flow/memory/procedural/versioning/generate_version_diff.py` |
| Which version is live | `m_flow/memory/procedural/governance/reconcile_active.py` |
| Sensitivity screen on procedural content | `m_flow/memory/procedural/safety/sensitivity.py` |
| Retrieval strategies and the orchestrator | `m_flow/retrieval/` |
| Queued node writes | `mflow_workers/tasks/queued_add_memory_nodes.py` |

## 5. Memory Data Model

The graph side is Entity / Facet / FacetPoint / Episode with typed edges, and the
precision ordering matters: a FacetPoint is finer than a Facet, which is finer
than an Entity, and the anchor step prefers the finest match. That is a
deliberate inversion of the usual approach, which embeds a chunk and searches for
neighbours.

The procedural side is the one with lifecycle. `ProcedureState` holds
`ExistingKeyPoint` and `ExistingContextPoint` records; drafts are built as
`ContextPackDraft` and `KeyPointsPackDraft` before becoming a version. Versioning
gives a procedure a history, a diff against its predecessor, and an active
pointer — which is more correction machinery than most procedural memories in
this atlas have, [TigrimOSR](../tigrimosr/) being the closest with its staged
proposal and human approval.

No capability marks are claimed. There is no status field that withholds a
memory from use, no record of a rejected value, no validity time separate from
record time, and no scope key found applied as a filter on the retrieval path.
`sensitivity.py` screens procedural content and is a safety filter rather than an
epistemic state. A reader should treat the empty capability row as *assessed and
none found at this commit* — this is a large system and the retrieval subsystem
in particular has more surface than a static read fully covers.

## 6. Retrieval Mechanics

Path-cost propagation, described in section 1. What can be said from the code is
that the machinery is real and plural: `base_graph_retriever`,
`cypher_search_retriever`, `unified_triplet_search`, `episodic/bundle_search`,
`lexical_retriever`, `jaccard_retrival`, coordinated by `memory_orchestrator`.

Two observations a reader should carry.

**"One strong path is enough" is a precision bet, and the atlas's evidence runs
both ways.** A single coherent chain of associations is exactly how a useful
recall often works, and it is also exactly how a confident wrong answer works.
[Graphify](../graphify/) requires two distinct corroborating results before a
claim counts and [CLIO](../clio/) requires two distinct sources; M-flow's
position is the opposite and it is a defensible one for recall as opposed to
belief. Which is right depends on whether the retrieved thing is treated as a
lead or as a fact, and the graph does not distinguish.

**Cost is the ranking signal and its calibration is not visible.** The
competitive property depends on the per-edge costs being right relative to each
other; nothing in the repository measures them against a labelled set, so the
weights are asserted.

## 7. Write Mechanics

Episodic capture first, then procedural extraction from episodes
(`write_procedural_from_episodic.py`), screened by `worth_storing` and routed by
`procedure_router`. Node writes are queued to workers, so the write path does not
block the agent and the store is eventually consistent with the conversation.

The governance sequence is the careful part and it reads in the right order:
decide whether this is worth keeping at all, classify it, check it against what
already exists deterministically, escalate to a model only when the deterministic
check is inconclusive, produce a diff, then decide which version is active. Each
step has a module and a name.

## 8. Agent Integration

An MCP server, an OpenClaw skill published to a plugin hub, a frontend, and a
starter kit. The procedural trigger's separation of retrieval from injection is
the integration-relevant idea: an agent can be told procedures exist without
paying to put them in the prompt, and the decision to inject is made with more
information than the decision to look.

No human review surface was found — the frontend exists and what it exposes was
not established, so `human_review` is withheld rather than denied.

## 9. Reliability, Safety, and Trust

`safety/sensitivity.py` screening procedural content before storage is the one
explicit safety mechanism found, and screening *procedures* specifically is a
sensible target: a stored procedure is an instruction the agent will follow
later, which is a higher-consequence artifact than a stored fact.

The versioning machinery is the reliability strength. A procedure that changes
leaves a diff and a previous version, and `reconcile_active` makes which one is
live an explicit decision rather than an implicit last-write-wins.

Against that, there is no trust state, so nothing distinguishes a procedure the
system is confident in from one extracted once from an ambiguous episode, and
`update_usage_stats` records use without use gating anything.

## 10. Tests, Evals, and Benchmarks

There is a `conftest.py` at the root and integration tests under
`m_flow/tests/integration/`. I did not run them — the system expects a graph
database and a worker queue, which is beyond a proportional smoke test.

No committed benchmark result, no eval fixture and no retrieval-quality artifact
were found. That is the report's main reservation and it is specific: the
architectural claim that distinguishes M-flow from a layered store is a
*retrieval-quality* claim, and retrieval quality is the one thing a reader cannot
check from the code. A committed comparison against the layered baseline the
README argues with would be the most valuable thing this project could publish.

`negative_eval` is withheld; no committed case asserting that particular material
must not be retrieved was found.

## 11. For Your Own Build

### Steal

**Front every expensive check with a cheap deterministic one, and name the
tiers.** Three modules do this — trigger, conflict detection, worth-storing — and
each docstring states the cost of each layer. The pattern is common; stating the
cost model in the comment is what makes it reviewable, because a reader can see
immediately which path costs a model call.

**Separate "should we retrieve" from "should we inject".** Retrieval is cheap and
reversible; injection spends tokens and changes what the model believes. Deciding
them at different moments with different information is a distinction almost
nothing else in this atlas draws.

**Screen before you index, not after.** `worth_storing` runs before a procedure
is built and indexed, so the cost of a bad memory is avoided rather than cleaned
up. Most systems here extract everything and prune later.

**Version a procedure and generate the diff.** A stored procedure is an
instruction the agent will follow; being able to see what changed between
versions, and which version is active, is the minimum for trusting it.

### Avoid

**Do not let "one strong path is enough" be the same rule for leads and for
facts.** A single low-cost chain is a good reason to look somewhere and a weak
reason to believe something. If retrieved material is going to be stated as
fact, the corroboration requirement has to live somewhere.

**Do not ship a retrieval thesis without a retrieval number.** The argument
against layered stores is the reason to choose this system, and the repository
does not contain a measurement of it.

### Fit

Take M-flow if you want graph memory with real procedural governance and you can
operate a graph database, workers and a frontend. The versioning, the
worth-storing screen and the tiered gates are the parts that transfer, and the
first two are small enough to lift.

Do not take it if you need to evaluate before adopting: 149,000 lines across four
packages, several coexisting retrieval strategies, and no committed result means
the only way to know whether the path-cost model works for your corpus is to run
it on your corpus.

## 12. Antipatterns / Risks

- **No committed retrieval result** for a system whose thesis is retrieval
  quality.
- **Edge costs are the ranking signal and are uncalibrated** against any labelled
  set in the repository.
- **Several retrieval strategies coexist**, and which runs when is an
  orchestrator decision rather than a documented path.
- **No trust state**, so a once-extracted procedure and a well-established one
  are indistinguishable at read time.
- **Queued writes** mean a lag between capture and retrievability that the
  repository does not quantify.

## 13. Build-vs-Borrow Takeaways

Borrow the three-gate discipline and the procedural versioning. Both are
independent of the graph, both are a few hundred lines, and the gate pattern
applies to any pipeline where a model call sits behind a decision a regex could
often make.

Build the evaluation. M-flow is arguing a specific, testable claim — anchor plus
path cost beats layer selection — against a baseline it names. The experiment is
well defined and the repository does not run it.

## 14. Open Questions

- **What are the edge costs, and where did they come from?** They are the ranking
  signal and no calibration was found.
- **Which retriever runs for which query?** Seven coexist under an orchestrator.
- **What does the frontend expose?** Whether it is a review surface or a viewer
  decides a capability mark.
- **How long between a queued node write and retrievability?** The workers make
  this a real number and it is not stated.

## 15. Appendix: File Index

| File | Role |
| --- | --- |
| `m_flow/retrieval/` | Graph, Cypher, lexical, Jaccard and episodic retrievers, and the orchestrator |
| `m_flow/retrieval/gating/procedural_trigger.py` | Two-layer trigger, retrieval separated from injection |
| `m_flow/memory/procedural/governance/` | `worth_storing`, classifier, `reconcile_active`, usage stats |
| `m_flow/memory/procedural/versioning/` | Conflict detection and version diffs |
| `m_flow/memory/procedural/safety/sensitivity.py` | Screening on procedural content |
| `m_flow/memory/episodic/` | Episodic capture and state |
| `mflow_workers/` | Queued node writes and the saving worker |
| `m_flow-mcp/`, `m_flow-frontend/`, `openclaw-skill/` | Interfaces |

## History

**2026-08-02** — [`da2766c5ebf45ff10440b419465c8ec0df674022`](https://github.com/FlowElement-ai/m_flow/commit/da2766c5ebf45ff10440b419465c8ec0df674022) — first reading.

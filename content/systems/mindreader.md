---
title: "Mindreader"
eyebrow: "Asking for no scope shows you the global layer, not everything"
description: "A Rust MCP memory over Neo4j where the agent must deliberately curate what it keeps, visibility layers are checked on both endpoints of every relationship in Cypher, and the edges that record a correction are barred from search."
root: ../..
page_kind: system
source_name: "bnomei/mindreader"
source_url: https://github.com/bnomei/mindreader
archive_name: "bnomei--mindreader"
revision: d7d1bb39cfeb47a6cfa230511d98764437ad98ad
revision_url: https://github.com/bnomei/mindreader/commit/d7d1bb39cfeb47a6cfa230511d98764437ad98ad
analyzed_at: 2026-09-16
capabilities: "bitemporal, scope_enforced, audit_log"
capability_evidence:
  scope_enforced: "layer membership stored on every node and edge, checked on all three elements of an assertion, and an empty request that narrows rather than widens | src/layers.rs:1-6, src/search.rs:503-534, :597-603, src/graph.rs:763, :821, :985 | the module states the rule it exists to hold: \"Graph records store memberships in `layers`; empty memberships are global and visible in every request\", and \"[r]elationship visibility also requires visible endpoints (enforced in Cypher).\" The predicate is repeated for the subject, the relationship and the object — `(size(s.layers) = 0 OR any(layer IN s.layers WHERE layer IN $layers))` three times over — and again for the `ABOUT` anchor and its own subject, so a fact cannot be reached through an endpoint the caller cannot see. The default is the part worth copying: \"Empty `scope` is global-only\", so a caller who asks for nothing gets the global layer rather than the whole graph, which inverts the usual failure where an omitted scope argument returns everything. Catalog nodes are forced to `layers = []` on MERGE so schema stays global by construction | src/layers.rs:11-30 validates, sorts and dedupes layer ids before they reach Cypher as bound parameters, and the scope is echoed back on every serialized node and relationship"
  bitemporal: "store retirement and world validity as separate properties, with a point-in-time query that refuses to guess for unqualified facts | src/search.rs:503-510, src/merge.rs:268, :618, :641 | every current-fact read opens with `WHERE r.validTo IS NULL`, which is the store's own axis: when Mindreader stopped asserting the fact, set by correction, withdrawal or duplicate merge rather than by the world changing. World validity is separate — `effectiveFrom` and `effectiveTo`, queried through an `$effectiveAt` parameter — and the clause around it is the careful part: a fact enters a point-in-time answer only when `coalesce(r.effectiveQualified, false)` is true. An assertion that never declared when it was true therefore drops out of an as-of query instead of being assumed to have held forever, so the two axes cannot be silently conflated by a fact that only has one of them | src/merge.rs:480 describes the same property from the write side — a soft-retired duplicate sets `validTo` and points at the surviving IRI rather than being deleted"
  audit_log: "an Episode node per mutation, attributed to the tool that caused it, and none at all for a no-op | src/graph.rs:1195-1226, src/mutation.rs:76, src/payload.rs:649 | `create_episode` writes a global `Entity:Episode` node carrying its IRI, its timestamp and the \"MCP tool name that created this Episode\", and the graph module's header lists \"Episode provenance\" beside the writer order it enforces. The record lives in the same graph as the memory it describes, so the history of an assertion is reachable by traversal rather than through a side channel. The discipline that makes it trustworthy is the negative case: a mutation whose body turned out to change nothing \"must record no Episode or graph changes\", so the presence of an Episode means a real change happened and the log cannot be padded by repeated no-op writes | src/payload.rs:649 compacts an Episode \"to the identity needed to find its full audit record later\", and a concise `write` returns the Episode IRI only when something changed"
stack_storage: "graph"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "An explicit relationship between stable entities — `project → uses → Neo4j` — carrying layer memberships, a spike classification, a weight, store validity and optional world-validity bounds"
  storage: "Neo4j, reached over Cypher, with a vocabulary of classes and properties kept global by construction"
  retrieval: "Lexical and label matching fused with semantic similarity and a bounded structural context, ranked by spike tier then weight then score"
  write: "MCP tools only, and only what the agent deliberately decides to keep: \"Mindreader never listens to conversations or extracts facts on its own\""
  update_delete: "Corrections coexist rather than overwrite; withdrawal and duplicate merge soft-retire by setting `validTo` and pointing at the survivor"
  scoping: "Layer memberships stored on nodes and edges, checked on subject, relationship and object in Cypher; an empty request scope sees the global layer only"
  integration: "An MCP server shipped as a Rust binary, a crate, an npm package, a Docker image and a bundled agent skill"
  background: "None on the memory itself; merge and retirement are explicit operations with expected-row-count assertions"
  trust: "Provenance through Episode nodes per mutation, a spike classification of how well-founded a fact is, and supersession and contradiction edges kept out of search"
  strengths: "Three things. The scope default is the first: \"Empty `scope` is global-only\", so asking for no scope returns the global layer rather than the entire graph — the inverse of the usual arrangement, where an omitted scope argument quietly means everything, and the failure it prevents is the one that produces a confident answer from the wrong project. The second is that the visibility predicate is applied to all three elements of an assertion and to the anchor beside it, so a hidden endpoint cannot be reached through a visible edge. The third is `assert!(!SEARCHABLE_RELATIONSHIPS.contains(&\"SUPERSEDES\"))` and the same for `CONTRADICTS`: the edges that record a correction are barred from ordinary search by a committed test, so the bookkeeping that says one fact replaced another can never itself come back as content. Behind all of it is a thesis stated plainly — \"Mindreader gives AI agents a memory they must curate, not a history they can search\", with nothing captured secretly and nothing silently overwritten"
  risks: "`SpikeRank` is a ranking input rather than a status that withholds, and the doc comment says so: \"Epistemic fact classification used in retrieval ranking (Knowledge highest).\" A `Signal` — the lowest tier, a lone unconfirmed observation — is ranked below a `Knowledge` fact and returned all the same, so the epistemic vocabulary sorts the answer rather than gating it, which is the same shape the atlas found in OKF Agent Memory one report earlier. The point-in-time path has a quieter consequence: because a fact enters an `$effectiveAt` answer only when `effectiveQualified` is true, and qualification is the agent's choice at write time, an as-of query over a corpus where nobody set those bounds returns nothing rather than the current state — correct, and surprising, and worth knowing before relying on it. The layer check is a visibility filter rather than an authorization boundary: it is applied in Cypher against a caller-supplied union, with no identity behind the request, so it separates contexts and does not defend against one. And the durable store is a Neo4j server, which is a heavier dependency than the single-file stores this family usually ships"
---

## 1. Executive Summary

Mindreader is an MCP memory server in Rust over Neo4j — MIT, version 0.7.2,
20,225 lines across 24 files, published as a crate, an npm package and a Docker
image. Its thesis is on the first line of the README and it is a refusal:

> "Mindreader gives AI agents a memory they must curate, not a history they can
> search."

The argument is that most agent memory starts from an archive and asks how to
retrieve the right passage later, where this one asks "[w]hat did this agent
learn that is important enough to become durable knowledge?" Each memory is an
explicit relationship — `project → uses → Neo4j` — and the consequences are
stated as commitments: "**No facts are captured secretly.** Mindreader never
listens to conversations or extracts facts on its own", and "**Nothing is
silently overwritten.**"

**The mechanism to take away is the scope default.** Layer memberships are
stored on nodes and edges, and the request carries a union of layer ids. What
makes it unusual is what an empty request means:

> "Empty `scope` is global-only. Named ids form an OR union."

Most systems in this corpus treat an omitted scope as *everything*, which is why
the atlas keeps finding stores where forgetting the argument returns another
project's memories. Here forgetting it returns the global layer and nothing
else, so the accident is an under-answer rather than a leak. The predicate is
thorough too: the visibility check is repeated for the subject, the relationship
and the object, and again for the `ABOUT` anchor and its subject, because
"[r]elationship visibility also requires visible endpoints (enforced in Cypher)."

**The second thing worth copying is a one-line test.** `SUPERSEDES` and
`CONTRADICTS` are asserted *not* to be in `SEARCHABLE_RELATIONSHIPS`. The edges
that record one fact replacing another are bookkeeping about the memory, not
memory, and a store that let them surface as results would hand an agent the
history of a correction as though it were the correction.

**The gap is the epistemic vocabulary.** `SpikeRank` grades a fact as `Signal`,
`Pattern`, `Insight` or `Knowledge`, and its doc comment is precise about what
that does: "Epistemic fact classification used in retrieval ranking (Knowledge
highest)." It sorts. A lone unconfirmed `Signal` still comes back, below the
better-founded facts — the same shape the atlas found one report earlier in
[OKF Agent Memory](../okf-agent-memory/), where the only trust field retrieval
consulted was one that promoted.

## 2. Mental Model

A **fact** is a relationship the agent chose to keep, not a passage it captured.

A **layer** is a visibility membership, and asking for none shows you the global one.

A **retirement** sets `validTo`; the row stays and points at its successor.

A **spike** ranks how well-founded a fact is, and ranking is all it does.

An **Episode** exists only when something actually changed.

```mermaid
%% caption: layer membership is checked on all three elements of an assertion in Cypher with an empty request meaning global-only, store retirement and world validity are separate properties, and every real mutation writes an Episode attributed to the tool
flowchart TB
    AGENT["the agent decides what is durable —<br/>nothing is captured secretly"] --> W["MCP write / withdraw / merge"]
    W --> MUT{"did the body change anything?"}
    MUT -->|"no-op"| NONE["records no Episode and no graph change,<br/>so the log cannot be padded"]
    MUT -->|"a real change"| G[("Neo4j: (s)-[r:ASSERTS]->(o)<br/>layers · spike · weight · validTo<br/>effectiveFrom · effectiveTo · effectiveQualified")]
    MUT -->|"a real change"| EP[("Episode node — IRI, timestamp,<br/>and the MCP tool that caused it")]
    CORR["a correction"] --> RET["soft-retire: set validTo,<br/>point at the surviving IRI"]
    RET --> G
    RET -.->|"the row stays; compatible facts coexist<br/>rather than being overwritten"| KEPT["nothing is silently overwritten"]
    Q["recall with scope: [...]"] --> V{"visibility, in Cypher"}
    V --> V1["size(s.layers) = 0 OR any(layer IN s.layers WHERE layer IN $layers)"]
    V --> V2["the same predicate on r"]
    V --> V3["the same predicate on o"]
    V --> V4["and again on the ABOUT anchor and its subject"]
    V1 & V2 & V3 & V4 -.->|"a relationship needs visible endpoints,<br/>so a hidden node cannot be reached<br/>through a visible edge"| SAFE["no traversal leak"]
    EMPTY["scope: []"] -.->|"global-only, NOT everything —<br/>forgetting the argument under-answers<br/>instead of leaking"| V
    V --> T{"temporal"}
    T -->|"always"| CUR["r.validTo IS NULL"]
    T -->|"$effectiveAt given"| EFF["only facts with effectiveQualified = true,<br/>inside effectiveFrom .. effectiveTo"]
    EFF -.->|"an assertion that never said when it was true<br/>drops out rather than being assumed<br/>to have held forever"| CONS["the axes cannot be conflated"]
    CUR & EFF --> RANK["rank: spike tier, then weight, then score"]
    SPIKE["SpikeRank: Signal, Pattern, Insight, Knowledge"] -.->|"'used in retrieval ranking' — it sorts the<br/>answer, it does not withhold a fact"| NOTS["no trust-state mark"]
    VOCAB["SEARCHABLE_RELATIONSHIPS"] -.->|"a test asserts SUPERSEDES and CONTRADICTS<br/>are NOT in it, so the record of a correction<br/>can never surface as content"| RANK
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `src/layers.rs` | Layer-id validation and the visibility-union policy, in one place |
| `src/search.rs` | The Cypher that ranks, and the visibility predicate repeated across it |
| `src/graph.rs` | Bootstrap, writer order, Episode provenance, node serialization |
| `src/merge.rs` | Duplicate detection and soft retirement with expected-row assertions |
| `src/mutation.rs` | What counts as a change, and what a no-op must not record |
| `src/vocabulary.rs` | Which relationships may be searched, and the test that pins it |
| `src/semantic.rs` | Similarity fusion with a bounded, penalized structural context |

## 4. Essential Implementation Paths

`src/layers.rs:1-6` — the visibility policy stated before any code implements
it.

`src/search.rs:503-534` — the same predicate applied to subject, relationship,
object and anchor, beside the `effectiveQualified` gate.

`src/vocabulary.rs:135-136` — two assertions that keep correction bookkeeping
out of search.

`src/graph.rs:1195-1226` — an Episode, and the tool it is attributed to.

`src/mutation.rs:76` — what a no-op must not write.

`src/merge.rs:641-655` — a retirement that checks it affected exactly the number
of relationships it expected, and fails loudly otherwise.

## 5. Memory Data Model

Entities and the `ASSERTS` relationships between them, each carrying layer
memberships, a spike classification, a weight, `validTo` for store validity, and
optional `effectiveFrom`/`effectiveTo` with an `effectiveQualified` flag.
Classes and properties form a catalog forced to `layers = []` so the schema
stays global. Episodes hang off mutations as provenance.

## 6. Retrieval Mechanics

Lexical and label matching fused with semantic similarity and a bounded
structural context that is penalized rather than boosting evidence, ranked by
spike tier, then weight, then score. Every leg carries the visibility predicate
and the `validTo IS NULL` filter.

## 7. Write Mechanics

Writes arrive only through MCP tools and only for what the agent decides to
keep. Corrections coexist with what they correct; withdrawal and duplicate merge
soft-retire by setting `validTo` and recording the survivor. Merge operations
count the rows they touched and raise when the count disagrees with what was
planned — "duplicate retirement affected {retired} relationships; expected
{expected}".

## 8. Agent Integration

One MCP server distributed as a Rust binary, a crate, an npm package and a
Docker image, with a bundled agent skill and a `mcp.json`. Every tool defaults
to a concise response "to minimize result tokens", with `detail:"detailed"`
available when handles, memberships, ranking or audit metadata are needed.

## 9. Reliability, Safety, and Trust

The strong parts are the scope default, the endpoint-closure check, the
correction edges kept out of search, and the row-count assertions on merges. The
limits are that the layer check is visibility rather than authorization — no
identity stands behind the requested union — and that the epistemic
classification only sorts.

## 10. Tests, Evals, and Benchmarks

Tests live inline with the code, including assertions over the generated Cypher
itself: that the query does not contain a particular label branch, that it does
not use `collect(`, and that the searchable-relationship list excludes the
correction edges. There is a CPU-hotspot benchmark. There are no committed
must-not-retrieve cases at the store level, which is the piece that would turn
those vocabulary assertions into a full guarantee.

## 11. For Your Own Build

Make an empty scope mean the narrowest view, not the widest. It converts the
most common scope bug from a disclosure into a missing answer.

Apply the visibility predicate to both endpoints as well as the edge. A
relationship is reachable from either end, and checking only the edge leaves the
other end reachable.

Keep your supersession and contradiction edges out of search, and write the test
that says so. They describe the memory rather than being it.

Decide whether your epistemic tiers rank or withhold, and put the answer in the
doc comment the way this one does. A reader who assumes the wrong one will trust
a `Signal` as though it were `Knowledge`.

## 12. Open Questions

Whether an as-of query should fall back to current facts when nothing is
qualified. The strict behaviour is defensible and the empty result is honest,
but an agent asking what was true last March in a corpus with no effective
bounds gets silence rather than an explanation.

Whether layers are intended to carry any authorization weight. They are a
caller-supplied union with no identity behind it, which is right for separating
a project from a task and wrong for separating two tenants.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `src/layers.rs:1-6` | A scope default that narrows instead of widening |
| `src/search.rs:503-534` | One visibility predicate, applied everywhere it has to be |
| `src/vocabulary.rs:135-136` | Correction bookkeeping barred from search, by test |
| `src/mutation.rs:76` | Why a no-op must leave no trace |
| `src/domain.rs:469-478` | An epistemic classification that ranks rather than gates |

## History

**2026-09-16** — [`d7d1bb39cfeb47a6cfa230511d98764437ad98ad`](https://github.com/bnomei/mindreader/commit/d7d1bb39cfeb47a6cfa230511d98764437ad98ad) — first reading, at a commit dated 13 September 2026. Screened before opening, from a shallow clone: six files scanned, one auto-run surface, no build-time execution points, no unpinned surfaces and three dependency files inside the seven-day cooldown, with `Cargo.lock` present. `AGENTS.md` is addressed to a reading agent and was recorded as data. Nothing was installed, built or run, and no Neo4j server was started, so the Cypher described here is read from the source strings rather than executed.

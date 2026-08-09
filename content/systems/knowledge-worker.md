---
title: "knowledge-worker"
eyebrow: "The excerpt has to appear in the source"
description: "A high-confidence claim must carry a supporting excerpt, and the excerpt is substring-matched against the source — a fabricated quote demotes the claim and the demotion is recorded with its reason."
root: ../..
page_kind: system
source_name: "rahulmranga/knowledge-worker"
source_url: https://github.com/rahulmranga/knowledge-worker
revision: 1d94dedf12a0a7a3623ee21d0ac0d773cf4ce858
revision_url: https://github.com/rahulmranga/knowledge-worker/commit/1d94dedf12a0a7a3623ee21d0ac0d773cf4ce858
analyzed_at: 2026-08-09
capabilities: "trust_state"
matrix:
  memory_unit: "A typed node with a confidence and an excerpt, plus typed edges between nodes"
  storage: "A local graph with OWL import and export; provenance edges kept separate"
  retrieval: "Context export that drops low-confidence decisions and marks the rest"
  write: "Extraction, then a validator that rejects, demotes or accepts each node and edge"
  update_delete: "Merge and review commands; demotion rather than deletion for weak claims"
  scoping: "One local graph per user; no scope key on a read path"
  integration: "A CLI, an Ollama proxy, and export for feeding an AI session"
  background: "Graph analytics — what matters, what connects, what is weak"
  trust: "high / medium / low, with high requiring an excerpt that matches the source"
  strengths: "A fabricated-quote check, with demotion recorded in an auditable manifest"
  risks: "Substring matching catches invention, not misquotation in context"
---

## 1. Executive Summary

knowledge-worker builds "a personal knowledge graph that survives between AI
conversations" — local, user-centred rather than conversation-centred, and
**"provenance-or-bust"**.

**That phrase turns out to be a code comment above a real check.**
`mygraph/validator.py`:

```python
# provenance-or-bust: high → must have excerpt + must substring-match source
excerpt = (node.get("excerpt") or "").strip()
if node["confidence"] == "high":
    if not excerpt:
        node["confidence"] = "low"
        manifest.demoted_nodes.append((node, "no_excerpt"))
    elif _norm(excerpt) not in src_norm:
        node["confidence"] = "low"
        manifest.demoted_nodes.append((node, "excerpt_not_in_source"))
```

**This is a fabricated-quote detector.** An LLM asked to extract claims with
supporting evidence will, reliably, produce claims whose supporting excerpt it
invented — paraphrased, merged from two places, or simply made up. Normalising
the excerpt and checking it is a substring of the source catches exactly that
class of failure, cheaply and deterministically, with no second model call.

**And the response is demotion, not rejection.** A claim whose excerpt does not
check out may still be true; what it is not is *evidenced*. Dropping it would
lose information; keeping it at `high` would launder an invention into the
graph. Moving it to `low` and recording why is the third option, and it is the
right one.

**Every validation pass produces a manifest** — `accepted_nodes`,
`rejected_nodes` with a reason, `demoted_nodes` with a reason, and the same for
edges — so an extraction run is auditable after the fact rather than a silent
transformation.

## 2. Mental Model

Chats, notes, decisions and sources are extracted into typed nodes and edges,
each carrying a confidence. A validator gates them into the graph. Analytics then
report what matters, what connects and what is weak, and a context export feeds a
filtered subset back to an AI session.

```mermaid
flowchart TD
    S["chats, notes, decisions, sources"] --> EX["extractor — LLM proposes nodes and edges"]
    EX --> V{"validator"}
    V -->|"id malformed"| RJ1["rejected: id_format"]
    V -->|"unknown type"| RJ2["rejected: bad_type"]
    V -->|"confidence not high/medium/low"| RJ3["rejected: bad_confidence"]
    V --> HC{"confidence == high?"}
    HC -->|"no excerpt"| D1["demoted to low: no_excerpt"]
    HC -->|"excerpt not a substring of the source"| D2["demoted to low: excerpt_not_in_source"]
    HC -->|"excerpt matches"| ACC["accepted at high"]
    V --> E{"edges"}
    E -->|"endpoint id malformed"| RJ4["rejected: src/dst_id_format"]
    E -->|"endpoint not in graph or candidates"| RJ5["rejected: orphan_src/orphan_dst"]
    E -->|ok| AE["accepted"]
    ACC --> G["graph"]
    D1 --> G
    D2 --> G
    AE --> G
    G --> AN["audit: analytics, read-only,<br/>provenance edges kept separate<br/>from semantic analytics"]
    G --> XP["export_context — decisions filtered to<br/>confidence != low, others marked"]
    V --> MAN["manifest: accepted / rejected / demoted,<br/>each with its reason"]
```

## 3. Architecture

`mygraph/` is a CLI-shaped package: `extractor` and `extractor_openai`,
`validator`, `ingest`, `merge`, `review`, `check`, `discover`, `deep_dive`,
`audit`, `memory_audit`, `eval_log`, `export_context`, `owl_io`, `viz`,
`mygraph`. Plus an `ollama_proxy/`.

The documentation set is larger than the code: `SPEC.md`, `DESIGN.md`,
`knowledge_worker_principles.md`, `AGENTS.md`, `CLAUDE.md`, plus
`docs/COMPETITIVE_ANALYSIS.md` and `docs/BENCHMARKS.md`. The README also places
the project inside a family of related repositories — a compression layer, an
interop protocol, an eval harness — and links them, which is more context than
most projects give about where they sit.

7,500 lines of Python, 8 test files.

## 4. Essential Implementation Paths

**Validate** — `mygraph/validator.py` (node checks `:85-94`, the
provenance-or-bust block `:95-102`, edge checks including orphan endpoints
`:108-127`, the manifest assembly `:129-132`).

**Export** — `mygraph/export_context.py` (the decision filter `:54-55`, the
confidence markers `:49`, `:70`, `:98`).

**Audit** — `mygraph/memory_audit.py` (the read-only, deterministic contract
`:1-11`).

## 5. Memory Data Model

Typed nodes with an id matching a regex, a type from a closed set, a confidence
in `{high, medium, low}` and an optional excerpt; typed edges with their own
closed type set and endpoints that must resolve.

**Confidence here is a genuine trust state rather than a score.** It is a
three-valued enum, it is *set by the system* on the evidence rather than reported
by the extractor and believed, and it changes what the memory is used for
(section 6). A `low` claim exists, is browsable, and is kept out of the material
an AI session sees.

The `owl_io` module means the graph imports and exports OWL, so the ontology is a
portable artifact rather than an internal convention.

## 6. Retrieval Mechanics

`export_context.py` builds the material an AI session receives, and the filter is
one line:

```python
# Decisions (high confidence only to keep it tight)
decisions = [n for n in by_type("decision") if n.get("confidence") != "low"]
```

with a `conf_marker` appended to other node types so the model sees the
confidence alongside the claim rather than having it silently applied.

**Filtering decisions but marking everything else is a defensible split.** A
decision presented to an AI as context will be acted on, so a weakly-evidenced
one should not appear; a weakly-evidenced observation is still worth seeing if
its uncertainty is visible. Whether the line belongs exactly there is arguable —
what matters is that the choice is explicit and one line, so it can be moved.

**No scope key on a read path**; the graph is one person's, local.

## 7. Write Mechanics

Extraction proposes, the validator disposes. The rejection reasons are
enumerated — `id_format`, `bad_type:<t>`, `bad_confidence`,
`src_id_format`, `dst_id_format`, `orphan_src:<id>`, `orphan_dst:<id>` — and the
demotion reasons are `no_excerpt` and `excerpt_not_in_source`.

**The orphan-edge check resolves against both the existing graph and the current
candidate set** (`ep not in g.nodes and ep not in candidate_ids`), so an edge
pointing at a node that was itself rejected in this same batch is dropped rather
than left dangling. That ordering is easy to get wrong and produces exactly the
kind of graph corruption that surfaces months later.

## 8. Agent Integration

A CLI (`mykg audit …`), an Ollama proxy, and context export as the interface to a
chat session — the model is *given* a filtered brief rather than querying the
store, which suits a graph small enough to summarise and keeps the retrieval
decision on the human's side.

## 9. Reliability, Safety, and Trust

**One mark: trust state.** Three values, assigned by the system on evidence,
demoted when the evidence fails, and read at export.

**Audit log — withheld, narrowly.** The manifest is per-run and returned to the
caller rather than being an append-only record in the store, and
`memory_audit.py` is analytics over the current graph — "read-only and
deterministic… keeps source/provenance edges separate from semantic graph
analytics, and writes generated artifacts only when asked". Both are good;
neither is a durable event log of mutations.

**Tombstone, bitemporal, scope, human review, negative eval — no**, though
`review.py` exists and a human-in-the-loop review step is the natural home for
the demoted set.

**The limit of the check is worth stating precisely.** Substring matching catches
*invention* — an excerpt that does not exist in the source. It does not catch
*misquotation in context*: a real sentence lifted from a passage that reverses
it, or a fragment that means something different in isolation. "I would never use
MongoDB for this" contains "use MongoDB for this", and a claim excerpting the
fragment passes. Catching that needs the surrounding span, not a substring test —
storing the offset rather than the text would make it possible.

The other quiet consequence: normalisation is what makes the check work across
whitespace and punctuation differences, and every normalisation loosens the test
slightly. `_norm` is where the strictness of "provenance-or-bust" is actually
set.

## 10. Tests, Evals, and Benchmarks

**8 test files** against 7,500 lines, plus `docs/BENCHMARKS.md` described as
"the offline demo-graph checks" and an `eval_log.py` module.

The validator is the component that most deserves a table-driven test, and the
cases write themselves from the reason strings the code already emits: a node
with no excerpt, one whose excerpt is absent from the source, one whose excerpt
matches, one whose excerpt matches only after normalisation, an edge to a
rejected candidate, an edge to an existing node. Six fixtures would pin every
branch, and the manifest gives an exact assertion target.

`docs/COMPETITIVE_ANALYSIS.md` positions the project in a category matrix — the
README summarises it as a "chat-to-wiki system" that "keeps reasoning local,
reviewable, and tied to literal provenance excerpts before claims become durable
graph knowledge". That sentence is an accurate description of the validator,
which is a better outcome than most competitive-analysis documents manage.

**I ran nothing.**

## 11. For Your Own Build

### Steal

- **Require an excerpt for a high-confidence claim, and check it against the
  source.** An LLM extracting evidence will invent it; a substring test catches
  the invention deterministically, with no second model call.
- **Demote rather than reject.** A claim whose evidence does not check out may
  still be true — it is not *evidenced*. Dropping it loses information, keeping
  it at high launders an invention; `low` with a reason is the third option.
- **Record the reason with the demotion.** `no_excerpt` and
  `excerpt_not_in_source` are different failures and want different fixes.
- **Return a manifest from every validation pass.** Accepted, rejected and
  demoted, each with its reason, turns extraction from a silent transformation
  into an auditable one.
- **Enumerate rejection reasons as strings.** `bad_type:<t>`, `orphan_src:<id>` —
  they document the contract and give tests an assertion target.
- **Resolve edge endpoints against existing nodes *and* the current candidate
  set.** An edge to a node rejected in the same batch must go too, and getting
  the ordering wrong produces dangling references that surface much later.
- **Filter what the model is given, mark what it sees.** Decisions gated on
  confidence, other nodes annotated with theirs, in one readable line.
- **Keep provenance edges out of the semantic analytics.** Counting a
  "supported-by" edge as a conceptual connection inflates every centrality
  measure in the graph.

### Avoid

- **Do not mistake substring matching for quotation checking.** It catches
  invention, not a real fragment lifted from a passage that reverses it. Storing
  the source offset instead of the text would let you check the surrounding
  span.
- **Do not leave the validator untested.** It is the component that decides what
  becomes durable knowledge, its branches are enumerable, and it already returns
  the exact object a test would assert on.

### Fit

A good fit for someone who wants a reviewable personal graph rather than an
automatic memory — the export-a-brief model keeps the human in the retrieval
decision, and OWL import/export means the graph is not trapped.

`mygraph/validator.py` is worth reading whatever you build. Forty lines that
decide what an LLM is allowed to make durable, with every rejection and demotion
named.

## 12. Open Questions

- **What does `_norm` normalise?** It sets the actual strictness of the
  provenance check.
- **Does `review.py` surface the demoted set?** That is the natural place for a
  human pass over weak claims.
- **Are medium-confidence claims ever promoted?** Demotion is implemented; the
  reverse path was not found.
- **What is in `docs/BENCHMARKS.md`'s demo-graph checks?** Described as offline;
  results were not read.

## Appendix: File Index

**Validator** — `mygraph/validator.py` (node id, type and confidence checks
`:85-94`, the provenance-or-bust block with both demotion reasons `:95-102`,
candidate tracking `:103-106`, edge type and confidence checks `:108-116`,
endpoint format and orphan checks `:117-127`, the returned manifest `:129-132`)

**Export** — `mygraph/export_context.py` (confidence markers `:49`, `:70`, `:98`,
the decision filter `:54-55`)

**Analytics** — `mygraph/memory_audit.py` (the read-only deterministic contract
and the provenance/semantic separation `:1-11`), `mygraph/audit.py`,
`mygraph/eval_log.py`

**Pipeline** — `mygraph/extractor.py`, `extractor_openai.py`, `ingest.py`,
`merge.py`, `review.py`, `check.py`, `discover.py`, `deep_dive.py`,
`owl_io.py`, `viz.py`, `ollama_proxy/`

**Documentation** — `SPEC.md`, `DESIGN.md`, `knowledge_worker_principles.md`,
`docs/COMPETITIVE_ANALYSIS.md`, `docs/BENCHMARKS.md`

## History

**2026-08-09** — [`1d94dedf12a0a7a3623ee21d0ac0d773cf4ce858`](https://github.com/rahulmranga/knowledge-worker/commit/1d94dedf12a0a7a3623ee21d0ac0d773cf4ce858) — first reading. Screened before reading; the tree was read, never installed, and no check was run.

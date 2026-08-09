---
title: "MemCP"
eyebrow: "The baseline column is a constant with a comment"
description: "A published head-to-head report whose \"Native\" column is `native_value=5.0  # Typical ~5% retention` typed into the test, against a measured RLM column."
root: ../..
page_kind: system
source_name: "maydali28/memcp"
source_url: https://github.com/maydali28/memcp
revision: 81c7177d4374cd7aecca8f6a8da43e229cadefee
revision_url: https://github.com/maydali28/memcp/commit/81c7177d4374cd7aecca8f6a8da43e229cadefee
analyzed_at: 2026-08-09
capabilities: "human_review"
matrix:
  memory_unit: "An insight node in a four-edge graph, with a feedback score and an importance"
  storage: "SQLite for the graph, the filesystem for contexts and chunks under ~/.memcp"
  retrieval: "Intent-aware traversal — causal edges for why, temporal edges for when"
  write: "remember, with secret detection and optional embedding-based deduplication"
  update_delete: "Consolidation with a preview step; forget; activation-based edge decay"
  scoping: "One store per user directory; no scope key found on the read path"
  integration: "An MCP server with 24 tools and only two required dependencies"
  background: "Hebbian co-retrieval strengthening and exponential edge decay by half-life"
  trust: "feedback_score in [-1, 1], moved twice as far down by a misleading report as up by a helpful one"
  strengths: "Negative feedback weighted heavier than positive and propagated to the edges"
  risks: "The benchmark report's comparison column is asserted, not measured"
---

## 1. Executive Summary

MemCP is an MCP server giving Claude Code an external memory: a SQLite knowledge
graph with four edge types, 24 tools, and **only two required dependencies**
(`mcp`, `pydantic`) with everything else optional and "progressively better".
It implements the RLM framework ([arXiv:2512.24601](https://arxiv.org/abs/2512.24601))
— "an active exploration model where content stays on disk and Claude decides
what to load, rather than passive RAG retrieval".

**The mechanism worth taking is the feedback asymmetry.**
`memcp_reinforce` marks an insight helpful or misleading, and the two are not
mirror images:

```python
helpful=True:  feedback_score += 0.1, boost connected edges by 0.02
helpful=False: feedback_score -= 0.2, weaken connected edges by 0.05
```

**A report that a memory misled you moves its score twice as far as a report that
it helped, and weakens its edges two and a half times as hard.** One bad
experience outweighs two good ones, and the penalty propagates into the graph
structure rather than stopping at the node.

That asymmetry is correct and almost nobody implements it. A memory that helped
is worth a little more; a memory that *actively misled an agent* is a different
kind of object, and treating the two symmetrically means a claim that burned you
once and helped twice ends up net positive. The edge propagation matters for the
same reason — a misleading insight usually sits in a misleading neighbourhood.

**And the benchmark report undermines itself** — section 10.

## 2. Mental Model

Insights are nodes in a four-relation graph — semantic, temporal, causal, entity.
Co-retrieval strengthens edges, disuse decays them, and feedback moves both the
node and its edges. Retrieval picks a traversal by the *intent* of the question.

```mermaid
flowchart TD
    R["memcp_remember"] --> SEC{"secret detection — 8 regex patterns"}
    SEC -->|"match"| BLK["blocked"]
    SEC -->|clean| DUP{"optional embedding dedup"}
    DUP --> N["insight node in SQLite"]
    N --> E["MAGMA 4-graph:<br/>semantic · temporal · causal · entity edges"]
    Q["memcp_recall"] --> INT{"intent"}
    INT -->|"'why did we choose X?'"| CAU["follow causal edges"]
    INT -->|"'when was Y decided?'"| TEM["follow temporal edges"]
    E --> CAU
    E --> TEM
    CAU --> OUT["insights returned"]
    TEM --> OUT
    OUT --> HEB["Hebbian: co-retrieved edges strengthen"]
    HEB --> E
    DEC["activation decay — exponential, configurable half-life"] --> E
    FB["memcp_reinforce(helpful)"] -->|"+0.1 node, +0.02 edges"| N
    FBM["memcp_reinforce(misleading)"] -->|"−0.2 node, −0.05 edges"| N
    CP["memcp_consolidation_preview"] --> CDO["memcp_consolidate"]
    CDO --> N
```

## 3. Architecture

"3-layer delegation: `server.py` (MCP endpoints) → `tools/*.py` (orchestration)
→ `core/*.py` (business logic)", with SQLite for the graph and the filesystem for
contexts and chunks.

**Two required dependencies** is the constraint worth noting, and the README
frames the rest as progressive: spaCy NER, embeddings and sub-agent extraction
all unlock capability without being required to start. A memory server that
installs with `mcp` and `pydantic` and works is more likely to be tried than one
that needs a model server first.

14,300 lines of Python. Docker, a Makefile, a `SECURITY.md`, an `agents/`
directory and templates.

## 4. Essential Implementation Paths

**Feedback** — `src/memcp/tools/feedback_tools.py` (`do_reinforce` and the
asymmetric constants `:11-40`), `src/memcp/server.py` `:520-527`.

**Benchmark** — `tests/benchmark/test_context_rot.py` (the hardcoded baselines
`:146`, `:273`, `:372`, `:462`), `tests/benchmark/metrics.py`
(`native_value` and the derived `savings_pct` / `ratio` `:259-279`),
`tests/benchmark/report.py`, `benchmark_output/`.

**Graph** — `src/memcp/core/memory.py` (`_compute_effective_importance`),
the edge manager's `reinforce_edges`.

## 5. Memory Data Model

An insight node with a `feedback_score` clamped to `[-1.0, 1.0]`, an importance
with an effective-importance computation, and four typed edge relations.

`feedback_score` is the closest thing to an epistemic field and it is a float
rather than a state — a memory at −0.9 is ranked down, not withheld, so an
insight repeatedly reported as misleading still competes. Given the asymmetry
already built into the update, a threshold at which an insight stops being
returned would be a small addition and a large improvement.

Secret detection runs on the write path with eight regex patterns, blocking
storage rather than redacting — the same side of the boundary as
[mnemos](../mnemos/) and [vir](../vir/).

## 6. Retrieval Mechanics

**Intent-aware traversal** is the distinctive part: "'why did we choose X?'
follows causal edges; 'when was Y decided?' follows temporal edges". Choosing the
*relation to walk* from the question's form is a cheap and legible alternative to
scoring everything and hoping the ranker recovers the structure — and it is only
possible because the edges are typed at write time.

Hebbian strengthening on co-retrieval and exponential decay by configurable
half-life run over the same edges, so the graph's shape tracks use.

**No scope key was found on the read path**; the store is one directory per user.

## 7. Write Mechanics

`remember` with secret blocking and optional embedding dedup;
`consolidation_preview` then `consolidate` for merging near-duplicates; `forget`
for removal.

**The preview-then-apply split is what earns the `human_review` mark.**
`memcp_consolidation_preview` and `memcp_consolidate` are separate tools, so a
merge is proposed and inspected before it happens — the same shape as
[Claudest](../claudest/)'s approval gate, at a lower level of ceremony. For a
destructive operation on accumulated memory, two tools beats one tool with a
`dry_run` flag, because the flag defaults somewhere.

## 8. Agent Integration

24 MCP tools — "remember, recall, forget, search, chunk, filter, traverse,
reinforce, consolidate, and more" — plus hooks, templates and an agents
directory. The `/compact` framing is concrete about the problem it solves:
Claude Code loses everything after a compaction, and an external store does not.

## 9. Reliability, Safety, and Trust

**One mark: human review**, for the preview-then-consolidate split.

**Trust state — withheld.** `feedback_score` is a float; nothing withholds.

**Tombstone, bitemporal, audit log, scope, negative eval — no.**

**The feedback asymmetry is the strongest thing here** and it deserves to be
separated from the benchmark problem below, because they are independent: the
asymmetry is a real design decision, implemented, with the constants visible in
one short function.

## 10. Tests, Evals, and Benchmarks

`benchmark_output/benchmark_report.md` and `benchmark_results.json` are committed,
dated, and formatted as a head-to-head:

| Scenario | Metric | Native | RLM |
|---|---|---|---|
| Context Rot: Single Compaction | Knowledge retained after `/compact` | 5.0% | 100.0% |
| Cascading Compactions (3×) | Knowledge retained after 3 compactions | 2.0% | 100.0% |
| Cross-Session | Session-1 knowledge from session-5 | 0.0% | 92.0% |
| Importance Decay | Critical insight retention at 60 days | 0.0% | 100.0% |

**The "Native" column is not measured.** In
`tests/benchmark/test_context_rot.py` the values are literals:

```python
native_value=5.0,   # Typical ~5% retention
native_value=2.0,   # ~0.05^3 ≈ near zero
native_value=0.0,
native_value=0.0,   # Native has 0% after session ends
```

The second is derived from the first by cubing it, in a comment. The JSON then
computes `savings_pct` and a `ratio` from those constants — `-1900.0` and
`"0.1x"` for the first row — so a report that reads as an experiment is one
measured column, one asserted column, and two columns of arithmetic on the
assertion.

**Two things should be said fairly.** These files live under `tests/benchmark/`,
and as *regression tests for the RLM side* — does the store still return what it
stored after these operations — they are reasonable; the problem is
`report.py` rendering them as a comparison and the output being published as
`benchmark_report.md`. And the underlying claim is true: an external store does
survive `/compact` and an in-context-only baseline does not.

**But that is the problem.** "Knowledge retained after a context wipe" is a
property every external memory system has by construction — a plain text file
scores 100% — so the table cannot distinguish a good memory system from a bad
one, and the 100%s are guaranteed by the architecture rather than earned by it.
The questions that would discriminate — does the retrieved insight answer the
question, does intent-aware traversal beat flat similarity, does the feedback
asymmetry improve ranking — are the ones this codebase is unusually well set up
to ask, since it has the graph, the intents and the feedback scores already.

Elsewhere: `tests/benchmark/test_scale.py`, `test_token_efficiency.py`,
`test_context_window.py`, with datasets and metrics modules.

**I ran nothing.** The constants above are read from the test source.

## 11. For Your Own Build

### Steal

- **Weight negative feedback heavier than positive.** `+0.1` for helpful against
  `-0.2` for misleading means one report of being misled outweighs two of being
  helped — which is the right ratio, because a memory that misled an agent is a
  different kind of object from one that merely did not help.
- **Propagate the penalty to the edges.** `-0.05` on connected edges against
  `+0.02` for a positive: a misleading insight usually sits in a misleading
  neighbourhood, and node-only feedback leaves the neighbourhood intact.
- **Clamp the score and let it go negative.** `[-1.0, 1.0]` rather than `[0, 1]`
  means "actively harmful" is representable.
- **Type your edges at write time and choose the traversal by intent.** "Why did
  we choose X" follows causal edges, "when was Y decided" follows temporal ones.
  Cheap, legible, and impossible without the typing.
- **Split preview from apply as two tools.** `consolidation_preview` then
  `consolidate` for a destructive merge, rather than one tool with a `dry_run`
  flag that defaults somewhere.
- **Require two dependencies and make the rest progressive.** NER, embeddings and
  sub-agent extraction as optional upgrades means the server installs and works
  before anyone configures a model.
- **Block secrets on the write path** rather than redacting on read.

### Avoid

- **Do not publish a comparison column you did not measure.** `native_value=5.0
  # Typical ~5% retention` becomes a "Native" column in a dated benchmark report,
  with a savings percentage and a ratio computed from it. Either measure the
  baseline or label the column an assumption.
- **Do not derive one assumed constant from another.** `2.0  # ~0.05^3 ≈ near
  zero` is a model of the baseline, not an observation of it.
- **Do not benchmark the property your architecture guarantees.** Every external
  store retains 100% across a context wipe; the table cannot tell a good memory
  system from a bad one, and this codebase has the graph, the intents and the
  feedback scores to ask a question that could.
- **Do not let a negative feedback score only re-rank.** At −0.9 an insight is
  still returned.

### Fit

Worth a look if you want a graph-shaped memory for Claude Code that installs with
two dependencies and grows capability as you add optional pieces. The feedback
asymmetry and the intent-typed traversal are the two ideas to take.

Treat `benchmark_output/` as an illustration of the architecture rather than as
evidence about it.

## 12. Open Questions

- **Does `feedback_score` ever exclude?** It is clamped to −1 and re-ranks.
- **Has the RLM side been compared against a flat store?** That is the comparison
  the graph and the intents exist for.
- **What sets edge half-life in practice?** Configurable, with no guidance on
  choosing it.
- **How is intent classified?** The routing is described; the classifier was not
  traced.

## Appendix: File Index

**Feedback** — `src/memcp/tools/feedback_tools.py` (`do_reinforce`, the
asymmetric constants in the docstring and the code `:11-40`),
`src/memcp/server.py` (the tool contract `:520-527`)

**Benchmark** — `tests/benchmark/test_context_rot.py` (the module docstring
`:1-11`, `native_value=5.0` `:146`, `native_value=2.0` with its cubed derivation
`:273`, `:372`, `:462`), `tests/benchmark/metrics.py` (`native_value` and the
computed `savings_pct` and `ratio` `:259-279`), `tests/benchmark/report.py`,
`tests/benchmark/{datasets,conftest,test_scale,test_token_efficiency,test_context_window}.py`,
`benchmark_output/benchmark_report.md`, `benchmark_output/benchmark_results.json`

**Core** — `src/memcp/core/memory.py` (`_compute_effective_importance`),
`src/memcp/core/context_store.py`, `src/memcp/core/errors.py`,
`src/memcp/tools/`, `src/memcp/server.py`

**Documentation** — `README.md` (the RLM citation, the 24 tools, the MAGMA
4-graph, the progressive-dependency framing), `SECURITY.md`, `docs/`

## History

**2026-08-09** — [`81c7177d4374cd7aecca8f6a8da43e229cadefee`](https://github.com/maydali28/memcp/commit/81c7177d4374cd7aecca8f6a8da43e229cadefee) — first reading. Screened before reading; the tree was read, never installed, and no benchmark was run. The hardcoded baseline values in section 10 are read from the test source.

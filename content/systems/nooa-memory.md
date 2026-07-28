---
title: NOOA Memory
eyebrow: Cognitive-model recall
description: NVIDIA's agent memory implements ACT-R activation and the Ebbinghaus retention curve directly, and stores the score components of every retrieval on the memory that was retrieved.
root: ../..
page_kind: system
source_name: NVIDIA-NeMo/labs-OO-Agents
source_url: https://github.com/NVIDIA-NeMo/labs-OO-Agents
revision: f22805b52ea8a073dabc018cefe3db1ccf609a29
revision_url: https://github.com/NVIDIA-NeMo/labs-OO-Agents/commit/f22805b52ea8a073dabc018cefe3db1ccf609a29
analyzed_at: 2026-07-28
capabilities: "scope_enforced"
matrix:
  memory_unit: "`Memory` typed info, skill, episode, intent, todo, reflection or scratch, with typed edges"
  storage: "SQLite with owner/status columns and pluggable vector backends"
  retrieval: "ACT-R activation — relevance, base-level recency, importance, plus graph spreading over k hops"
  write: "Authoring via a memory skill; reflection distils episodes into gists"
  update_delete: "Retention decay archives below threshold; `archived` flag, record-keyed"
  scoping: "`owner` column, indexed, applied on the retrieval path"
  integration: "Exposed as a memory skill inside the Object-Oriented Agents framework; tracing bridge"
  background: "Reflection: dedup/merge, edge formation, re-scoring, prune — deterministic steps need no LLM"
  trust: "Separate importance, salience and confidence; per-access score components retained"
  strengths: "Every retrieval leaves behind why it ranked where it did, on the record itself"
  risks: "Archival is record-keyed, and the access log is capped, so both history and correction are bounded"
---

## 1. Executive Summary

`nooa-memory` is a dedicated package inside NVIDIA's Apache-2.0 Object-Oriented
Agents labs repository — about 4,200 lines with a test file for nearly every
module. It is the most direct implementation of *cognitive-psychology models* in
this atlas, and it does one thing nothing else here does.

**Every retrieval records why it ranked where it did, on the memory that was
retrieved.**

```python
class AccessRecord(BaseModel):
    """One structured access to a memory — self-contained observability."""
    ts: float
    channel: str = "recalled"
    reader_owner: str = ""          # who fetched (cross-owner analysis)
    trace_ref: str | None = None
    query: str | None = None        # truncated; None for reinforced/created
    score: float | None = None
    rank: int | None = None
    components: dict | None = None  # {rel, rec, imp, spread} at fetch time
```

The atlas lists recall observability — "why they outranked others" — as a
dimension it does not cover, because almost nothing carries it. Here the score
*decomposition* is persisted per access, alongside the rank, the truncated query,
the reader, and a `trace_ref` that "deep-links to the exact trace moment". Asking
"why did the agent surface that" is a lookup rather than a reconstruction.

The scoring being decomposed at all is the second thing. Retrieval is ACT-R,
stated as equations in the module docstring:

```text
rel(m,q) = lambda*cos + (1-lambda)*ctxOverlap        (encoding specificity)
rec(m)   = sigmoid( ln sum_k (t_now - access_k)^-d )  (ACT-R base-level)
imp(m)   = importance / 10
S_base   = a_rel*rel^ + a_rec*rec^ + a_imp*imp^
Act(n)   = S_base(n) + spread over k hops (decayed per hop)
```

That is Anderson's base-level activation with spreading activation over a typed
graph. [Generative Agents](../generative-agents/) established the
recency-relevance-importance sum with hand-tuned constants;
[HippoRAG](../hipporag/) replaced ranking with PageRank diffusion. This is the
model both are approximations of, implemented as such — a decayed power-law sum
over *every* past access rather than a single recency term.

Forgetting is equally literal, and "first-class, on two timescales": online
retention as the Ebbinghaus curve `R = exp(-Δt / S)` evaluated lazily on read,
where `S` is a `strength` counter that retrieval bumps; and offline pruning
inside reflection for memories that have decayed, are old enough, are not a
protected type, and are not high-importance.

**And unusually, the memory subsystem has been ablated against a fair
baseline.** The accompanying paper reports ARC-AGI-3 under a two-hour fleet cap,
scored by RHAE — "the competition's action-efficiency score against per-level
human baselines":

| Configuration (GPT-5.5 unless noted) | Fleet-mean RHAE |
| --- | --- |
| world-model skill **+ memory** | **50.2%** (118 levels) |
| hypothesis-driven baseline skill + memory | 41.7% |
| world-model skill **with markdown files in place of memory** | 38.4% |
| world-model + memory on GPT-5.6-sol | 85.1% (170 levels), under $20 per game |
| raw GPT-5.6-sol, ARC Prize eval | 13.3% |

The paper states the comparison as "**+11.8 RHAE points over the identical agent
with file-based notes in place of memory**".

That baseline is the point. This atlas's standing complaint is that memory
systems measure themselves against *no memory*, which flatters everything; the
honest comparison is against the cheapest thing that also persists, and a
markdown file is exactly that. Appendix D names the reproduction runs
(`20260714_201702_competition_md` is the markdown ablation), and the paper marks
its per-run correlations as "associations" given "n = 25 and 16 outcomes
right-censored by the operator kill". It is the most carefully bounded memory
result in this atlas.

Reservations. Archival is a boolean on the record, so a decayed memory can be
re-created by the next authoring pass with nothing to consult. The access log is
a capped ring, so the observability that makes this system distinctive is
bounded by design. And the paper's own operational statistics undercut two of
the design's more distinctive parts — see §10.

## 2. Mental Model

Seven memory types, and two of them are a category nothing else in this atlas
has:

| Type | Kind | |
| --- | --- | --- |
| `info` | semantic | facts, preferences, domain rules |
| `skill` | procedural | reusable verified procedures |
| `episode` | episodic | a specific task run |
| **`intent`** | **prospective** | trigger-based reminder — "when X happens…" |
| **`todo`** | **prospective** | durable commitment with an open/done lifecycle |
| `reflection` | schema / gist | insight distilled from episodes |
| `scratch` | working | transient, never durably consolidated |

**Prospective memory — remembering to do something later — is absent from every
other system here.** The nearest neighbour is
[ai-memory](../ai-memory/)'s handoff with its `next_steps` list, and that is a
record of an interrupted task rather than a trigger the agent will act on.

`status` is deliberately narrow: "TODO lifecycle: todos always carry a status; no
other type may", enforced in `model_post_init`, which raises if a non-todo
carries one. A lifecycle field that applies to exactly one type, and refuses to
be borrowed by the others, is a small piece of schema discipline worth noting.

Edges are typed and split causal from associative:

```text
derived_from · created_by   CAUSAL provenance
supports · contradicts       evidential
refines                      this updates a prior memory
causes · precedes            domain causality, temporal order
related · part_of            associative, compositional
```

`contradicts` as an edge between two memories puts this with
[Memora](../memora/) rather than with the systems that flag one row.

## 3. Architecture

`packages/nooa-memory/src/nooa_memory/` — `manager.py` (933), `store.py` (487),
`schema.py` (372), `retrieval.py` (369), `reflection.py` (348),
`vector_backends.py` (225), `generative.py` (205), `config.py` (202),
`observability.py` (174), `references.py` (163), `embeddings.py` (145),
`monitoring.py` (120), `forgetting.py` (98), `tracing_bridge.py` (90),
`memory_skill/`, `descriptors.py`.

Storage is SQLite with `owner` and `status` columns added by migration
(`ALTER TABLE` guarded by a column check), indexes on both plus `archived`, and
pluggable vector backends.

### Deployment and ergonomics

A Python package with SQLite; the vector backend is pluggable and the
deterministic half of reflection needs no model at all. Nothing to stand up.

The memory is exposed to the agent as a *skill* (`memory_skill/`), which fits the
surrounding framework's conventions rather than introducing a separate protocol.

## 4. Essential Implementation Paths

### Observability that travels with the record

The docstring is explicit about the design choice and its consequence:

> "Lives ON the record (capped ring in `Memory.access_log`): copy or export one
> row and its usage story travels with it."

Most systems that log retrieval put it in a separate events table, which is
better for aggregate queries and worse for the question an operator actually
asks, which is about *one memory*. Putting the log on the record means exporting
a memory exports its history — and it means the log must be capped, or records
grow without bound.

That is a real trade and the code takes the side almost nobody takes. The atlas's
[append-only memory audit](../../patterns/append-only-memory-audit/) pattern
assumes a separate event stream; this is the other arrangement, with its own
failure mode written into the design (a ring buffer forgets the early accesses,
which are the ones that explain how a memory got established).

`reader_owner` is stored "for cross-owner analysis" — so the log answers not just
when a memory was read but *by whom*, which is the question a multi-agent
deployment needs and which no other access log here records.

### Four scores that mean different things

```python
importance: float   # 0-10, LLM "poignancy" 1-10
salience: float     # 0-1, outcome/surprise/novelty tag
confidence: float   # 0-1, belief certainty
strength: int       # spaced-repetition counter (+1 on recall)
```

Most systems in this atlas have one number and overload it. Here *how much this
matters*, *how surprising it was*, *how sure we are*, and *how well-rehearsed it
is* are separate fields, and only the last is moved by retrieval.

That last point is the one the [decay and reinforcement](../../patterns/decay-and-reinforcement/)
pattern asks for: recall bumps `strength`, which slows forgetting, and leaves
`confidence` alone. Being read a lot makes a memory *stick*; it does not make it
*true*. Several systems in this atlas collapse exactly that distinction.

The paper adds a refinement the code reading did not surface, and it closes the
loop this pattern warns about: "**Injected memories are not reinforced, so what
the harness surfaces does not distort the usage signal.**" Spontaneous injection
runs at a fixed cadence of roughly one per turn, and those injections do *not*
bump strength — only deliberate reads do. So the system cannot reinforce a memory
merely by having chosen to show it, which is precisely the self-amplifying
feedback the pattern says nobody dampens. It is the cleanest answer to that
hazard in the atlas.

`importance` is named "poignancy" in the comment, which is
[Generative Agents](../generative-agents/)' term — the lineage is acknowledged
rather than quietly reused.

### Forgetting as a curve, evaluated lazily

`R = exp(-Δt / S)` computed on read rather than by a sweep. A memory's retention
is therefore always current without any job having run, and the offline pass only
handles the consequence — archiving what has fallen below threshold.

The guards on that pass are worth listing because they are the ones most decay
implementations omit: old enough, not a protected type, and **not
high-importance**. A pure recency-decay sweep will eventually delete the most
important thing in the store simply because nobody asked for it recently.

### Reflection in a stated order

> "A pure-Python orchestrator running ordered ops that mirror the biological
> sequence (clean → abstract → renormalise → forget). The deterministic steps
> need no LLM and run by default:
> 1. dedup / merge — fold near-identical memories into a canonical record
> 2. edge formation — link memories whose embeddings are close
> 3. re-score importance — bump salient/frequently-recalled memories
> 4. prune / forget — archive memories that have decayed"

Two things. The order is argued rather than incidental — clean before abstract,
abstract before forget — and dedup running first means the later steps operate on
canonical records rather than on near-duplicates, which is the sequencing bug
that makes consolidation passes reinforce whatever was said most often.

And **the deterministic steps run by default while the LLM steps do not**. A
consolidation pass that improves the store without a model call is a different
operational proposition from one that costs tokens proportional to corpus size.

## 5. Memory Data Model

`Memory` carries id, type, title, content, owner, size in characters, tokens and
sentences, the four scores, mood, `reinforcement_count`, timestamps, typed
`Edge`s, `MemoryRef`s to external artifacts, and the capped `access_log`.

What is absent:

- **No value-level tombstone.** `archived` is a boolean on the record. A memory
  that decayed away can be re-authored, and nothing consults its absence.
- **No trust state.** `confidence` is a float; `status` exists but is reserved
  for todo lifecycle by an explicit validator.
- **No bi-temporal validity.** `created_at` and `last_accessed_at` are record
  times; nothing tracks when a fact was true.
- **The access log is capped**, so the observability is a recent window rather
  than a history.

## 6. Retrieval Mechanics

Hybrid candidate recall, then ACT-R activation, then associative spread over the
typed graph for `k` hops with per-hop decay, with `owner` applied as a filter.
Components are normalized before weighting, and the per-memory breakdown is
returned alongside the result and written into the access log.

Because `rec` is a sum over *all* retained access times rather than a single
`last_accessed`, a memory read many times long ago and a memory read once
recently are distinguishable — which a single-timestamp recency term cannot do,
and which is the entire point of the base-level equation.

## 7. Write Mechanics

Authoring through the memory skill, with reflection distilling episodes into
`reflection`-type gists. `references.py` attaches `MemoryRef`s — kind, key,
preview, capture time — pointing at external artifacts rather than copying them.

The paper describes what that pointer does at read time, and it is stronger than
the schema suggests: "references are resolved against **live agent state at
recall time** — extending pass by reference into persistence, so recall does not
answer from stale copies". A memory that holds a reference rather than a snapshot
cannot go stale about the thing it points at, which is a different and narrower
guarantee than correctness but a real one. Owner scoping "governs reads **and
writes** when several agents share one store", so the enforcement covers both
paths rather than only retrieval.

### Operational cost

Retrieval is local: embeddings plus arithmetic, no model call, and the
`rec` term needs only the retained access timestamps. Forgetting is lazy, so it
costs nothing until a record is read. The deterministic reflection ops run
without an LLM; the generative ones are opt-in.

The recurring cost is storage rather than tokens: every access appends to a ring
on the record, and every memory carries its own edge list and reference list.
No footprint figures were found.

## 8. Agent Integration

Exposed as a skill inside the Object-Oriented Agents framework, with
`observability.py`, `monitoring.py` and `tracing_bridge.py` connecting it to the
surrounding tracing so `trace_ref` on an access record resolves to a real span.

## 9. Reliability, Safety, and Trust

Strengths:

- **Score components persisted per access**, making "why was this retrieved"
  answerable after the fact.
- **`reader_owner` on every access**, so cross-owner reads are visible.
- **ACT-R base-level recency** over all access times, not one timestamp.
- **Four distinct scores**, with retrieval moving only the rehearsal counter.
- **Ebbinghaus retention evaluated lazily**, so no sweep is needed to be current.
- **Prune guards** for protected types and high importance.
- **Prospective memory** as first-class types.
- **Typed edges** separating causal from associative, with `contradicts` as an
  edge.
- **`status` restricted to one memory type** by a validator.
- **Deterministic reflection by default**, LLM steps opt-in.
- **A test file per module**, including owner roles, contract, and hygiene.

Gaps:

- **No value-level tombstone**; archival is a record flag.
- **No trust state** and no bi-temporal validity.
- **A capped access log**, so the distinctive observability is bounded and the
  earliest accesses — the ones explaining how a memory became established — are
  the first to go.
- **Many tunable constants** (`lambda`, `d`, the three `a_*` weights,
  `spread_gamma`, hop count, thresholds); no ablation was found.
- **A labs repository**, so the stability commitment is whatever the surrounding
  framework offers.

## 10. Tests, Evals, and Benchmarks

Twenty-three test modules covering retrieval, forgetting, reflection and its
interrupt path, owner roles, contract, embeddings and their integration,
observability, monitoring, references, todo, schema, store and a v2 store,
routes, skill, authoring, generative, vector backends, and background reflect
plus hygiene. Nothing was run for this review.

The end-to-end ablation is in §1. What makes the accompanying paper worth reading
against the code is that its Appendix D reports operational statistics from the
evaluation fleet — and **two of them cut against the design**.

**Consolidation output is almost never read.** "Reflection records are 22% of rows
yet ~1% of both read channels (importance 3.9), and 45% of all records ended
archived by decay-based forgetting." A fifth of the store is distilled insight
that retrieval essentially does not surface. This atlas has asked repeatedly
whether consolidation earns its cost and never had a number; here is one, from
the authors, and it is unflattering. The paper does not hide it — and it adds the
mechanism behind it from internal pilots: "reflection helped when retrieval was
the bottleneck and **hurt pinpoint lookup (abstraction blurs the exact fact)**,
which is why consolidation is configurable per store."

**The prospective types went unused.** "The `intent` and `scratch` types went
unused; `todo` appeared in 18 records." The category this report calls novel and
absent from every other system was, in the one measured deployment, dormant. That
does not make it a bad idea — an unused type may simply need a skill that uses it
— but it does mean the atlas should credit the *modelling* and not assume the
behaviour.

Other reported figures: per-game store sizes of 23 / 129 / 255
(min / median / max), and memory engagement tracking performance — winning games
"check memory 1.63 times and write 1.87 memories per decision (medians, vs. 1.21
and 1.46 for the remaining games)", at Spearman ρ = +0.52 for reads per decision
and +0.36 for writes. The paper labels these associations rather than effects,
noting the sample and the censoring.

Retrieval observability also goes further than the schema showed: "a retrieval
call can be replayed with `explain()`", and "memory events bridge to OpenTelemetry
spans with trace ↔ record cross-links".

The evaluation the design still invites is the *internal* one: the components are
computed, weighted, normalized and stored, so the contribution of `rel`, `rec`,
`imp` and `spread` to any past retrieval is already recorded, and no ablation of
those weights was found. The subsystem has been measured as a whole; its scorer
has not been measured against itself.

## 11. For Your Own Build

### Steal

- **Persist the score components with each access.** It converts "why did the
  agent say that" from an investigation into a query, and it is a dict on a row.
- **Record who read a memory**, not just when. In any multi-agent deployment the
  interesting question is cross-owner reads, and no other access log here
  captures it.
- **Keep rehearsal separate from belief.** Retrieval should move a strength
  counter and leave confidence alone — being read often makes a memory stick,
  not true.
- **Compute recency over all access times**, not the last one, if you want a
  frequently-consulted old memory to outrank a once-read recent one.
- **Evaluate decay lazily on read** so retention is always current without a
  sweep.
- **Guard the prune** with protected types and an importance floor, or recency
  decay will eventually delete the most important thing you have.
- **Model prospective memory.** "Remind me when X" and "this commitment is still
  open" are memories, and nothing else in this atlas stores them.
- **Restrict a lifecycle field to the type that owns it**, and validate it —
  `status` here raises if a non-todo carries one.
- **Run the deterministic consolidation steps by default** and make the LLM ones
  opt-in.
- **Do not reinforce what the harness chose to show.** If injection bumps the
  same counter as a deliberate read, the system is measuring its own decisions
  and calling it usage.
- **Ablate against the cheapest thing that also persists.** "With memory versus
  without" flatters every memory system; "versus the identical agent with
  markdown files" is the comparison that means something.
- **Publish the unflattering operational statistics.** Reflection output being
  22% of rows and 1% of reads is the most useful number in this paper precisely
  because it does not support the design.

### Avoid

- **An access log on the record as your only history.** Portability is a real
  benefit and the cap is the price; if you need the full story, keep a stream
  too.
- **Archival as correction.** A decayed memory that can be re-authored has not
  been forgotten.
- **Six coupled constants with no ablation**, in a scorer whose components you
  are already storing — the data to tune it is being collected and not used.

### Fit

Right if you want a memory whose behaviour is explainable after the fact and
grounded in a model you can read the equations for, and if the cognitive framing
is a feature rather than an affectation — the ACT-R and Ebbinghaus
implementations here are literal, not gestural. Wrong if you need correction
semantics: this system knows a great deal about how a memory became reachable and
nothing about whether it was ever right.

## 12. Open Questions

- How large is the access-log ring, and what happens to the explanation of an
  old, heavily-used memory once its formative accesses roll off?
- Have the six scoring constants been ablated? The subsystem has been measured
  end to end; the scorer has not been measured against itself, and the stored
  components make it cheap.
- Does `owner` gate the graph spread, or can activation flow through a memory the
  reader cannot see?
- What prevents an archived memory being re-authored identically?
- Is `intent` acted on by a scheduler, or does it only surface when retrieval
  happens to reach it? The paper reports the type unused in evaluation, so the
  question is now what would have to exist for it to be used.
- If reflection output is 22% of rows and ~1% of reads, what is consolidation
  buying, and would the store be better without it in this workload?

## Appendix: Sources Beyond the Code

- Paper: *NVIDIA-labs OO Agents: Native Python Object-Oriented Agents*,
  [arXiv:2607.20709](https://arxiv.org/abs/2607.20709) — memory architecture in
  §3 and Appendix C, the ARC-AGI-3 ablation in §4.4 and Figure 7, operational
  statistics and reproduction run ids in Appendix D.
- Blog: [Six agent harness capabilities for higher model performance](https://developer.nvidia.com/blog/six-agent-harness-capabilities-for-higher-model-performance/).

Claims taken from these are attributed in the text. The RHAE figures and the
operational statistics are reported, not reproduced here.

## Appendix: File Index

- Schema: `packages/nooa-memory/src/nooa_memory/schema.py` (`MemoryType`,
  `EdgeType`, `Edge`, `MemoryRef`, `AccessRecord`, `Memory`, `TODO_STATUSES`).
- Retrieval: `retrieval.py` (ACT-R equations, `_spread`, component breakdown).
- Forgetting: `forgetting.py` (`R = exp(-Δt / S)`, prune guards).
- Reflection: `reflection.py` (ordered ops), `generative.py`.
- Store: `store.py` (owner/status migration, indexes).
- Observability: `observability.py`, `monitoring.py`, `tracing_bridge.py`.
- Skill surface: `memory_skill/`.
- Tests: `packages/nooa-memory/tests/memory/` (23 modules).

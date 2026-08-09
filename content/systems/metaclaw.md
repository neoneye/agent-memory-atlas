---
title: MetaClaw
eyebrow: Self-tuning memory policy
description: A memory system that replays past turns against candidate retrieval policies and promotes a new one only when it beats the incumbent on eight measured deltas.
root: ../..
page_kind: system
source_name: aiming-lab/MetaClaw
source_url: https://github.com/aiming-lab/MetaClaw
revision: 922caf3a1cd093fb316e95183a8acc8aa47b3b21
revision_url: https://github.com/aiming-lab/MetaClaw/commit/922caf3a1cd093fb316e95183a8acc8aa47b3b21
analyzed_at: 2026-07-27
capabilities: "scope_enforced"
stack_storage: ""
stack_retrieval: ""
stack_source: "seeded"
matrix:
  memory_unit: "`MemoryUnit` with type, status, importance, confidence, access count, reinforcement score"
  storage: "Store with embeddings, per-scope policies"
  retrieval: "Under a live `MemoryPolicyState`: mode, unit cap, token budget, weights"
  write: "Conversation writes plus consolidation; no actor gate"
  update_delete: "`superseded_by` lineage, `expires_at`; no rejected state"
  scoping: "`scope_id` throughout store, retriever, policy, metrics"
  integration: "OpenClaw plugin with a written spec and a sidecar manager"
  background: "Self-upgrade worker: candidate → replay → gate → promote"
  trust: "Source session and turn range; reinforcement kept apart from confidence"
  strengths: "Retrieval policy replayed offline and promoted only on non-regression across eight metrics"
  risks: "Optimizes overlap proxies; gate thresholds are themselves defaults"
---

## 1. Executive Summary

MetaClaw is an MIT-licensed memory system from aiming-lab, shipping as an OpenClaw plugin with a written plugin spec (`openclaw-metaclaw-memory/OPENCLAW_PLUGIN_SPEC.md`). Its memory package is roughly 10,400 lines of Python, with a further ~5,000-line manager in the plugin sidecar.

It answers a question no other system in this atlas asks: **how do you know your retrieval policy is any good, and what would it take to change it safely?**

Every other system here has retrieval parameters — fusion weights, top-k, token budgets — chosen by hand and never revisited. [Generative Agents](../generative-agents/) has `gw = [0.5, 3, 2]` with two abandoned settings left in comments and no ablation. [Holographic](../holographic/) fuses at 0.4/0.3/0.3. [RainBox](../rainbox/) uses 0.55/0.30/0.15. None can tell you whether those numbers are right.

MetaClaw closes the loop, and closes it carefully:

```text
generate_policy_candidates(current)      # bounded grid over mode, budgets, weights
  -> run_policy_candidate_replay(...)    # replay real past turns under each candidate
  -> comparison deltas vs. the incumbent
  -> should_promote(comparison, criteria)
  -> promote, or keep the incumbent
```

`should_promote` requires a **minimum of 10 replay samples** and demands the candidate not regress on eight separate measures — query overlap, continuation overlap, response overlap, specificity, focus score, value density, grounding score, and coverage — plus a cap on how many additional zero-retrieval samples it may introduce.

This is the disciplined version of a loop the atlas is otherwise right to be suspicious of. The recurring warning here is "telemetry mistaken for truth": [Holographic](../holographic/) lets a downvote silently push a fact below the retrieval floor, and RainBox deliberately keeps feedback as a review signal behind a human gate. MetaClaw is not doing that. It tunes **retrieval policy** — how much to inject, which mode, what weights — never a memory's confidence. Usage data changes how memory is *found*, not whether it is *believed*. That is the distinction the atlas should have drawn explicitly, and MetaClaw draws it in code.

The reservations are ordinary: the memory model itself has no rejected state, the replay metrics are overlap-based proxies rather than task outcomes, and the promotion gate's thresholds are themselves hand-chosen defaults.

## 2. Mental Model

Two objects matter, and keeping them apart is the whole design.

**The memory unit** — ordinary, and deliberately so:

```python
MemoryUnit(
    memory_id, scope_id, content, summary,
    source_session_id, source_turn_start, source_turn_end,
    memory_type,            # episodic | semantic | preference
                            # project_state | working_summary | procedural_observation
    status,                 # active | superseded | archived
    importance=0.5, confidence=0.7,
    access_count=0, reinforcement_score=0.0,
    superseded_by="",
    created_at, updated_at, last_accessed_at, expires_at,
)
```

Note that `confidence`, `importance`, `access_count`, and `reinforcement_score` are four separate fields. Reinforcement is tracked without being allowed to masquerade as belief — the split [Verel](../verel/) argues for.

**The policy** — the thing that actually gets learned:

```python
MemoryPolicyState(
    retrieval_mode, max_injected_units, max_injected_tokens,
    ...retrieval weight parameters..., notes[]
)
```

The self-upgrade lifecycle:

```text
past sessions -> load_replay_samples()
    MemoryReplaySample(session_id, turn, scope_id,
                       query_text, response_text, next_state_text)

generate_policy_candidates(current)
    Phase 1: grid over retrieval_mode x max_injected_units x max_injected_tokens
    Phase 2: perturbations of the current weight parameters
    (deduplicated by candidate key)

for each candidate: run_policy_candidate_replay()
    -> MemoryReplayResult(sample_count, avg_retrieved, avg_query_overlap,
                          avg_continuation_overlap, avg_response_overlap,
                          avg_specificity, ...)

should_promote(comparison, MemoryPromotionCriteria)
    sample_count >= 10
    every delta >= its floor  (specificity may drop at most 0.05)
    zero-retrieval increase <= 2
    -> promote the candidate, or keep the incumbent

write_replay_report()  -> auditable record of the decision
```

## 3. Architecture

`metaclaw/memory/` (~10,400 lines):

- `manager.py` (5,151) — the orchestrator.
- `store.py` (1,798) — persistence.
- `self_upgrade.py` (876) and `upgrade_worker.py` (435) — the tuning loop and its background driver.
- `replay.py` (558) — replay samples, candidate replay, replay reports.
- `consolidator.py` (315) — consolidation.
- `retriever.py` (299) — retrieval.
- `embeddings.py` (179), `policy_optimizer.py` (173), `policy_store.py` (130), `candidate.py` (127), `promotion.py`, `scope.py`, `models.py`, `metrics.py`, `telemetry.py`.

Plus `openclaw-metaclaw-memory/` — the OpenClaw plugin with its own sidecar manager (~5,000 lines), a plugin spec, and a plan document.

```mermaid
flowchart TD
  Conv["Conversations"] --> Store["MemoryStore (units,<br/>scopes)"]
  Store --> Retr["retriever (under<br/>live policy)"]
  Retr --> Inject["injected<br/>context"]
  Store --> Tele["telemetry +<br/>metrics"]
  Hist["past sessions"] --> Samples["load_replay_samples"]
  Live["live MemoryPolicyState"] --> Cand["generate_policy_candidates"]
  Tele --> Opt["policy_optimizer<br/>(bounded tuner)"]
  Opt --> Cand
  Cand --> Replay["run_policy_candidate_replay"]
  Samples --> Replay
  Replay --> Gate["should_promote (8<br/>deltas, n>=10)"]
  Gate -->|pass| Promote["new live<br/>policy"]
  Gate -->|fail| Keep["keep incumbent"]
  Gate --> Report["write_replay_report"]
```

## 4. Essential Implementation Paths

### Candidate generation (`candidate.py`)

`generate_policy_candidates` builds a **bounded** set in two phases: a grid over retrieval mode, injected-unit count, and injected-token budget; then perturbations of the current weight parameters. Candidates are deduplicated by a key tuple, and every candidate is annotated with `"candidate_generated"` in its notes.

The bounding matters. This is not gradient descent over an open parameter space — it is a small, enumerable neighbourhood around the live policy, which keeps each upgrade cycle cheap and each change auditable.

### Replay (`replay.py`)

`MemoryReplaySample` captures `query_text`, `response_text`, and `next_state_text` for a turn. Candidate policies are then evaluated by re-running retrieval over these historical turns and scoring what they would have surfaced, producing a `MemoryReplayResult` with `sample_count`, `avg_retrieved`, and the overlap and quality averages.

This is offline counterfactual evaluation: what *would* this policy have retrieved for turns we have already seen, and how well would that have matched what actually mattered next? It requires no live traffic split and no user exposure, which is the practical reason such loops are usually skipped.

The honest limitation is that the metrics are lexical-overlap proxies (`query_overlap`, `continuation_overlap`, `response_overlap`) plus derived scores like specificity, focus, value density, grounding, and coverage. They approximate "did retrieval surface useful material" without measuring whether the task succeeded. A policy that games overlap without helping the agent would pass.

### The promotion gate (`promotion.py`)

```python
@dataclass
class MemoryPromotionCriteria:
    min_query_overlap_delta: float = 0.0
    min_continuation_overlap_delta: float = 0.0
    min_response_overlap_delta: float = 0.0
    min_specificity_delta: float = -0.05
    min_focus_score_delta: float = 0.0
    min_value_density_delta: float = 0.0
    min_grounding_score_delta: float = 0.0
    min_coverage_score_delta: float = 0.0
    min_sample_count: int = 10
    max_zero_retrieval_increase: int = 2
```

Every gate is a **non-regression** floor at 0.0, except specificity, which is allowed to drop by up to 0.05 — an explicit acknowledgement that broader retrieval trades a little precision for coverage. The `max_zero_retrieval_increase` guard is the sharpest of them: a candidate that improves averages while more often returning *nothing* is rejected, which is exactly the failure a mean would hide.

This is [Verel](../verel/)'s promotion-gate idea moved up a level. Verel gates whether an induced rule becomes a trusted memory; MetaClaw gates whether a retrieval policy becomes the live one.

### The bounded tuner (`policy_optimizer.py`)

```python
class MemoryPolicyOptimizer:
    """Bounded policy tuner that adapts retrieval parameters based on store state
    and telemetry signals. ... All changes stay within hard bounds."""
```

`propose()` reads store statistics — active count, dominant memory type, memory density, active-by-type distribution — and telemetry, then proposes an adjusted policy. It short-circuits on low volume: *"don't tune weights before having enough data."* Proposals still go through replay and the promotion gate; the optimizer suggests, it does not decide.

### Memory types

`MemoryType` includes `PROCEDURAL_OBSERVATION` alongside `EPISODIC`, `SEMANTIC`, `PREFERENCE`, `PROJECT_STATE`, and `WORKING_SUMMARY` — procedural knowledge as a first-class kind, connecting to the [skills as procedural memory](../../patterns/skills-as-procedural-memory/) pattern, though without Voyager's execution gate.

## 5. Memory Data Model

`MemoryStatus` is `active | superseded | archived`, with `superseded_by` carrying correction lineage and `expires_at` providing TTL. `scope_id` runs through the store, the retriever, the policy, and the metrics, so policies are tuned per scope rather than globally — a detail that matters, since the right injection budget for a small project differs from a large one.

Gaps against the strongest models here:

- **No rejected state and no tombstone.** `archived` removes a memory from play but nothing prevents re-derivation.
- **`confidence` is set but its provenance is unclear** — it defaults to 0.7 and no verification path comparable to [Magic Context](../magic-context/)'s file-backed verification appears in the memory package.
- **Source is a session and turn range**, which is real provenance, but there is no actor model distinguishing user assertion from model inference.

## 6. Retrieval Mechanics

Retrieval runs under the live `MemoryPolicyState`: a retrieval mode, an injected-unit cap, a token budget, and weight parameters, with embeddings available through `embeddings.py`. The interesting property is not any single mechanism but that **all of it is a parameter vector the system can evaluate and change**.

`reinforcement_score` and `access_count` exist and feed metrics. The atlas's standing caution about popularity loops applies to any use of them in ranking — but note that here the loop is at least *measured*: if reinforcement degraded retrieval quality, the replay comparison would show it and the gate would reject the policy.

## 7. Write Mechanics

Memories are written from conversation, consolidated by `consolidator.py`, and superseded through `superseded_by`. Writes are not gated by trust the way [RainBox](../rainbox/) gates them by actor; the sophistication here is concentrated in the read path and its tuning, not the write path.

## 8. Agent Integration

`openclaw-metaclaw-memory/` packages the system as an [OpenClaw](../openclaw/) plugin with a documented plugin spec and a sidecar carrying its own ~5,000-line manager. It therefore inherits the boundary described in the [pluggable memory provider](../../patterns/pluggable-memory-provider/) pattern: OpenClaw's contract has no deletion hook or scope parameter, so MetaClaw's internal `scope_id` model is richer than the interface mounting it can express.

## 9. Reliability, Safety, and Trust

Strengths:

- **A measured, gated change loop** for retrieval policy — unique in this atlas.
- **Non-regression gating across eight metrics** with a minimum sample size.
- **An explicit zero-retrieval guard** catching the failure that averages hide.
- **Bounded candidate generation**, keeping upgrades enumerable and cheap.
- **Low-volume short-circuit** preventing tuning on noise.
- **Replay reports** written for each decision, so a policy change is auditable.
- **Reinforcement kept in its own field**, separate from confidence.
- Per-scope policies rather than one global setting.

Gaps:

- **Proxy metrics.** Lexical overlap and derived scores are not task success; a policy could improve them without helping.
- **The gate's thresholds are themselves defaults** — hand-chosen constants governing a loop built to remove hand-chosen constants.
- **No rejected-value tombstone**; `archived` is not durable against re-derivation.
- **`confidence` without a verification path.**
- **Ten samples is a low bar** for eight simultaneous comparisons; the gate is closer to a smoke test than a statistical one.
- Very large `manager.py`, duplicated between the package and the plugin sidecar.

## 10. Tests, Evals, and Benchmarks

The evidence posture is better than most in the atlas. The repository commits a benchmark harness under `benchmark/` with two datasets (`metaclaw-bench` and `metaclaw-bench-small`), each with `all_tests.json`, an `eval/` directory, and OpenClaw config, state, and workspace fixtures — so runs are reproducible against a pinned agent setup. `scripts/` carries `run_memory_ablation.py`, `run_memory_ablation_direct.py`, `run_v03_benchmark.py`, and an Azure variant.

**Dedicated memory ablation scripts are rare here.** Most systems in this atlas measure end-to-end task performance, if anything; MetaClaw isolates the memory subsystem's contribution.

Neither the suites nor the benchmarks were run for this review, and no published headline numbers were reproduced. The measurement the design most needs and does not obviously have is a link from its replay proxies to real task outcomes — evidence that improving `avg_response_overlap` improves what the agent actually does.

## 11. For Your Own Build

### Steal

- **Treat the retrieval policy as a versioned object that must earn promotion.** Generate bounded candidates, replay them against real history, and require non-regression on several measures before one goes live. Nothing else in this atlas can answer "are our fusion weights right?" — this can.
- **Offline counterfactual replay.** Evaluating candidate policies on past turns needs no live traffic split and exposes no users.
- **Guard the distribution, not just the mean.** `max_zero_retrieval_increase` catches a policy that improves averages while failing more often.
- **Short-circuit tuning at low volume.**
- **Tune reachability, never belief.** Usage data may change how memory is found; it must not change whether memory is true. This is the principled resolution of the atlas's telemetry-versus-truth tension.
- **Write a report for every policy decision**, so an automated change remains auditable.

### Avoid

- **Optimizing a proxy.** Overlap metrics are a stand-in for usefulness, and any closed loop optimizes what it measures.
- **Meta-parameters that are themselves unmeasured constants.**
- **A ten-sample gate** across eight comparisons.
- **Supersession without tombstones** in a system that consolidates automatically.
- **Confidence recorded without a verification path.**

### Fit

Borrow:

- The whole candidate → replay → gate → promote loop; it is the most valuable idea in the repository and is largely independent of the rest of the design.
- `MemoryPromotionCriteria` as a shape: a dataclass of non-regression floors plus a sample-count minimum is a readable, reviewable policy gate.
- The zero-retrieval guard.
- Per-scope policies.

Do not copy:

- The proxy metrics as-is; wire the gate to whatever outcome you can actually observe.
- The memory model as a trust store — it has no rejected state and no verification.

## 12. Open Questions

- Do the replay proxies correlate with task success? Without that link the loop is optimizing a shadow.
- Who tunes the tuner? `MemoryPromotionCriteria`'s defaults govern every future change and are not themselves evaluated.
- Is ten samples enough for eight simultaneous non-regression tests, or does the gate pass noise?
- Should the loop ever be allowed to touch `confidence`? The current answer appears to be no, which seems right and would be worth stating as an invariant.
- How does a policy promoted for one scope interact with a scope whose memory distribution later changes?

## Appendix: File Index

- Policy candidates: `metaclaw/memory/candidate.py`.
- Promotion gate: `metaclaw/memory/promotion.py` (`MemoryPromotionCriteria`, `should_promote`).
- Offline replay: `metaclaw/memory/replay.py` (`MemoryReplaySample`, `MemoryReplayResult`, `run_policy_candidate_replay`, `write_replay_report`).
- Tuning loop: `metaclaw/memory/self_upgrade.py`, `upgrade_worker.py`.
- Bounded tuner: `metaclaw/memory/policy_optimizer.py`; policy state: `policy_store.py`.
- Memory model: `metaclaw/memory/models.py` (`MemoryUnit`, `MemoryType`, `MemoryStatus`).
- Store, retrieval, consolidation: `store.py`, `retriever.py`, `consolidator.py`, `embeddings.py`.
- Scope, metrics, telemetry: `scope.py`, `metrics.py`, `telemetry.py`.
- OpenClaw plugin: `openclaw-metaclaw-memory/OPENCLAW_PLUGIN_SPEC.md` and `sidecar/metaclaw/memory/manager.py`.
- Benchmarks and ablations: `benchmark/data/metaclaw-bench*/`, `scripts/run_memory_ablation*.py`, `scripts/run_v03_benchmark*.py`.

## History

**2026-07-27** — [`922caf3a1cd093fb316e95183a8acc8aa47b3b21`](https://github.com/aiming-lab/MetaClaw/commit/922caf3a1cd093fb316e95183a8acc8aa47b3b21) — first reading.

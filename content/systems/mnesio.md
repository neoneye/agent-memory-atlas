---
title: "mnesio"
eyebrow: "Setting every gate threshold to its weakest value still cannot commit a failing improvement"
description: "A Rust memory that compiles agent outcomes into versioned policy artifacts, where a bitemporal graph decides what was live at an instant and a baseline gate no configuration can relax stands between a proposal and a commit."
root: ../..
page_kind: system
source_name: "mnesio/mnesio"
source_url: https://github.com/mnesio/mnesio
archive_name: "mnesio--mnesio"
revision: 5831aa0ea0a359b44a3a28b64e7e9f7174d88970
revision_url: https://github.com/mnesio/mnesio/commit/5831aa0ea0a359b44a3a28b64e7e9f7174d88970
analyzed_at: 2026-09-16
capabilities: "bitemporal, scope_enforced, audit_log"
capability_evidence:
  bitemporal: "two intervals on every node, and a liveness test that requires both | crates/mnesio-graph/src/record.rs:118-146, crates/mnesio-graph/src/lib.rs:14-22 | a `NodeRecord` carries `valid_from`/`valid_to` alongside `tx_from`/`tx_to`, and the comment says where each comes from — the validity pair \"come from `Memory.time`\", the memory's own claim about when it held, while \"`tx_to` becomes `Some(_)` on `MemoryInvalidated`\", the system's record of when it stopped believing. `is_live_at` then conjoins them rather than choosing one: \"'Live' here means both: the memory was valid at `at` *and* the system hadn't tombstoned it before `at` (transaction time)\", implemented as `valid && known` over two half-open intervals. The module states why the second axis exists at all — \"[m]emory evolution invalidates the previous version and emits a new one\", so \"[a] flat 'current' graph would lose that lineage the moment the worker fires\" — and ties it to a replay invariant: \"[r]eplay the log up to `T` and you'd get the same graph\" | crates/mnesio-graph/src/tests.rs:303 `as_of_query_returns_historical_neighborhood`, and crates/mnesio-provenance/src/timeline.rs:353 `snapshot_as_of_reconstructs_belief_at_t`"
  scope_enforced: "scope stored inline on the node and required by every traversal step | crates/mnesio-graph/src/lib.rs:24-26, crates/mnesio-graph/src/traversal.rs:48-79 | \"[e]ach node carries the memory's `Scope`, tags, and bi-temporal stamp inline so traversals can scope-filter without a join\", which is the design decision that keeps the predicate cheap enough to apply everywhere rather than once at the edge of the query. It is then applied everywhere: `scope: &Scope` is a required parameter with no default on `node()`, on `out_neighbors()` and on the traversal itself, and each hop re-resolves the destination through `self.node(e.dst, scope, as_of)?` rather than trusting that an in-scope edge leads to an in-scope node. A walk cannot leave the scope by following a relation, because the scope and the instant are carried together into every step | the doc comment states the boundary case rather than leaving it implied: `max_depth = 0` returns the start node only \"if it's in scope\", so an out-of-scope start is an empty result rather than a seed"
  audit_log: "an append-only event log the graph is a projection of, with rebuild-from-log as a named invariant | crates/mnesio-graph/src/lib.rs:14-22, crates/mnesio-graph/src/tests.rs:607, crates/mnesio-graph/src/view.rs:410, crates/mnesio-graph/src/traversal.rs:94 | the two loops \"operate over a single append-only event log\", and the graph is a projection of it rather than an authority beside it: evolution \"invalidates the previous version and emits a new one\" instead of rewriting, and the project names the consequence as Hard Rule #4 — rebuild from log — which is carried as an invariant through the code rather than as a README promise. The test suite exercises it directly (\"Hard Rule #4 — drop and rebuild\"), and the view layer holds itself to the stronger form, requiring results to be stable \"across calls (Hard Rule #4 — replay-stable)\". That is what makes the mutation record load-bearing: a projection that can be dropped and rebuilt is one where the log, not the graph, is the thing that must be right | the `MemoryInvalidated` event is what closes a node's transaction interval, so the invalidation is an entry in the log before it is a state in the projection"
stack_storage: "kv, graph"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A memory node in a property graph carrying scope, tags, keywords, a source reference, an evolution count and two time intervals; beside it a versioned `PolicyArtifact` — a system prompt, heuristic or retrieval rule — produced from batches of outcomes"
  storage: "A single append-only event log with the graph and indexes as projections over it, rebuildable by replay"
  retrieval: "Lexical, vector and graph traversal, every step taking a scope and an optional instant"
  write: "Memories written directly; policy artifacts proposed by a reflective loop — reflect, propose K candidates, shadow-evaluate, Pareto-select — and committed only through the gate"
  update_delete: "Evolution invalidates the previous version and emits a new one rather than rewriting; erasure is crypto-shredding through a keyring, and a redaction pass covers structured secrets"
  scoping: "`Scope` stored inline on each node and required as a parameter by every traversal step, re-resolved at each hop"
  integration: "An HTTP service, an MCP server, Python bindings and a Node SDK, plus a `mnesio-code` CLI that maps a codebase without a server"
  background: "A bounded async worker that retroactively re-tags and re-links related memories on write, and a procedural compiler that batches outcomes into candidate policies"
  trust: "A three-condition baseline gate no configuration can relax, shadow evaluation before activation, canaries, a safety probe, and an objective delta that must not be negative"
  strengths: "The gate is the thing, and what makes it worth reading is that it is defined as a floor rather than as a policy. `EvalReport::is_committable()` is three conjoined conditions — every canary passed, the safety probe passed, and the objective delta at or above zero — and the README's claim about it is the unusual part: \"setting every configurable gate threshold to its weakest value *still* cannot bypass the baseline.\" That is not left as prose. `fully_relaxed_gates_still_reject_baseline_failure_through_pipeline` runs the whole compile pipeline with the gates relaxed and asserts the rejection anyway, beside unit tests that trip each of the three conditions in isolation with a message naming which invariant broke. Most systems this atlas reads have an escape hatch that a configuration can widen until it admits anything; this one has a floor underneath the configuration, and a test standing on it. The bitemporal design is the second piece: two intervals per node with `is_live_at` requiring both, justified by a concrete failure — \"[a] flat 'current' graph would lose that lineage the moment the worker fires\" — and tied to a replay invariant the view layer also enforces"
  risks: "The procedural loop is the product and its honesty depends on the evaluation behind the gate: canaries, a safety probe and an objective delta are only as good as the cases and the objective somebody wrote, and nothing in the repository pins those to a corpus the way the gate itself is pinned by a test. Erasure is crypto-shredding through a keyring, which makes a payload unrecoverable and leaves the graph's structure — nodes, edges, intervals, evolution counts — in place, and nothing is keyed on a shredded value, so the same content can be written again with no record that it was once erased. There is no person anywhere in the loop: `is_committable` is a mechanical floor rather than an approval, and a policy artifact that clears it activates without anyone reading it. And the repository is early — the README notes that the documented install line \"starts working at v0.1.1\" because \"v0.1.0 predates it and carries no binaries\", which is a candid disclosure and also a statement about maturity"
---

## 1. Executive Summary

mnesio is "[l]ong-term memory for AI agents that learns from outcomes, with a
safety gate before every improvement" — Apache-2.0, Rust, 58,766 lines across
152 files in twenty crates, reachable over HTTP, MCP, Python and Node.

Its claim is procedural rather than factual: it "turns real outcomes into
improved, versioned policies: prompts, heuristics, and retrieval rules", so the
agent "get[s] *better at doing things* over time, rather than only remembering
more facts." Two loops run over one append-only event log — a compiler that
batches outcomes into candidate `PolicyArtifact`s, and an evolution worker that
retroactively re-tags and re-links memories on write.

**The mechanism to take away is a gate defined as a floor rather than as a
policy.**

> "**Hard Rule #1: Nothing procedural commits without passing
> `EvalReport::is_committable()`** — canaries 100%, safety probe passing,
> objective Δ ≥ 0. … Mechanically enforced — setting every configurable gate
> threshold to its weakest value *still* cannot bypass the baseline. Held by a
> dedicated integration test on every commit."

The function is three conjoined conditions and nothing else. The claim about
configuration is the part that usually goes unbacked, and here it is a committed
test —
`fully_relaxed_gates_still_reject_baseline_failure_through_pipeline` — which
relaxes the gates and runs the whole compile pipeline, asserting the rejection
anyway. Beside it, unit tests trip each condition in isolation with messages
naming the invariant that broke: "missing canary trips baseline", "failed probe
trips baseline", "negative delta trips baseline". This atlas keeps finding
systems whose safety gate is a threshold somebody can widen until it admits
anything; this one has something underneath the thresholds.

**The graph is bitemporal and says why.** A node carries `valid_from`/`valid_to`
from the memory's own time, and `tx_from`/`tx_to` from the system's, and
`is_live_at` requires both: "'Live' here means both: the memory was valid at
`at` *and* the system hadn't tombstoned it before `at` (transaction time)." The
second axis exists for a stated failure — "[m]emory evolution invalidates the
previous version and emits a new one … [a] flat 'current' graph would lose that
lineage the moment the worker fires" — and ties into a replay invariant the view
layer also holds: "[r]eplay the log up to `T` and you'd get the same graph."

**Scope travels with the instant.** Each node carries its `Scope` inline "so
traversals can scope-filter without a join", and `scope: &Scope` is a required
argument at every step — including the re-resolution of each hop's destination,
so a walk cannot leave its scope by following a relation.

**What is missing is a person.** `is_committable` is mechanical, and a policy
artifact that clears it activates without anyone reading it. For a system whose
subject is an agent rewriting its own behaviour, that is the interesting
frontier rather than an oversight — and it is the reason the review mark is
absent.

## 2. Mental Model

An **outcome** is evidence; a **policy artifact** is what the compiler proposes from it.

A **gate** is a floor, not a setting.

A **node** is live only when both clocks agree.

A **projection** can be dropped, because the log cannot.

```mermaid
%% caption: outcomes are compiled into candidate policy artifacts that shadow-evaluate and commit only through a three-condition floor no configuration can relax, over an append-only log whose graph projection carries two time intervals and a scope on every node
flowchart TB
    OUT["batches of agent Outcomes"] --> REFLECT["reflect → propose K candidates →<br/>shadow-evaluate → Pareto-select"]
    REFLECT --> CAND["a candidate PolicyArtifact:<br/>system prompt, heuristic or retrieval rule"]
    CAND --> GATE{"EvalReport::is_committable()"}
    GATE -->|"canaries_passed == canaries_total"| C1["every canary, or nothing"]
    GATE -->|"safety_probe_passed"| C2["the probe passed"]
    GATE -->|"objective_delta at or above zero"| C3["no regression"]
    C1 & C2 & C3 --> COMMIT["gated commit — a new artifact version"]
    GATE -->|"any one fails"| REJECT["rejected"]
    RELAX["every configurable threshold set<br/>to its weakest value"] -.->|"still cannot bypass the baseline —<br/>fully_relaxed_gates_still_reject_baseline_failure_through_pipeline<br/>runs the WHOLE pipeline and asserts the rejection"| GATE
    NOHUMAN["no person reads the artifact —<br/>the floor is mechanical, not an approval"] -.-> COMMIT
    W["a memory write"] --> LOG[("one append-only event log")]
    COMMIT --> LOG
    EVOLVE["bounded async worker: retroactively<br/>re-tags and re-links related memories"] --> INV["MemoryInvalidated — emit a new version,<br/>never rewrite the old one"]
    INV --> LOG
    LOG --> PROJ[("graph projection: nodes carry Scope, tags,<br/>valid_from/valid_to AND tx_from/tx_to")]
    PROJ -.->|"Hard Rule #4 — drop and rebuild;<br/>replay the log up to T and you get the same graph,<br/>and the view layer must be replay-stable across calls"| REBUILD["the projection is disposable"]
    Q["a query: node(id, scope, as_of)"] --> LIVE{"is_live_at(at)"}
    LIVE -->|"valid_from at or before at,<br/>and valid_to null or after it"| V["valid — the memory's own time"]
    LIVE -->|"tx_from at or before at,<br/>and tx_to null or after it"| K["known — the system's time"]
    V & K -.->|"'Live here means BOTH' — valid && known"| HIT["the node is in the graph at that instant"]
    TRAV["traversal: scope and as_of carried into every hop,<br/>each destination re-resolved through node(dst, scope, as_of)"] --> HIT
    TRAV -.->|"a walk cannot leave its scope<br/>by following a relation"| SAFE["scope survives the traversal"]
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `crates/mnesio-core/src/event.rs` | The event vocabulary, and `is_committable` |
| `crates/mnesio-procedural/` | The reflective compiler, the gates, and their tests |
| `crates/mnesio-graph/` | The bitemporal projection, scope-carrying traversal |
| `crates/mnesio-privacy/` | Redaction and the crypto-shredding keyring |
| `crates/mnesio-provenance/` | Point-in-time snapshots of what was believed |
| `crates/mnesio-server`, `-mcp`, `-py` | HTTP, MCP and Python surfaces |

## 4. Essential Implementation Paths

`crates/mnesio-core/src/event.rs:215-219` — the whole floor, in four lines.

`crates/mnesio-procedural/tests/compile_e2e.rs:237` — the test that makes the
configuration claim checkable.

`crates/mnesio-graph/src/record.rs:118-146` — two intervals and a liveness test
that needs both.

`crates/mnesio-graph/src/lib.rs:14-26` — why a flat current graph was not
enough, and why scope sits inline.

`crates/mnesio-graph/src/traversal.rs:48-79` — scope and instant carried into
every hop.

## 5. Memory Data Model

Memory nodes in a property graph, each with a scope, tags, keywords, an optional
source reference, an evolution count and two time intervals; edges keyed on
source, relation, destination and transaction start. Beside the graph, versioned
policy artifacts with their evaluation reports. Both are projections of one
append-only log.

## 6. Retrieval Mechanics

Lexical, vector and graph traversal, with the scope and the as-of instant
threaded through every step rather than applied at the boundary, and each hop's
destination re-resolved under the same pair.

## 7. Write Mechanics

A memory write appends an event and wakes a bounded worker that re-tags and
re-links neighbours. A procedural improvement never writes directly: it is
proposed, shadow-evaluated, Pareto-selected and then either committed through
the gate or rejected.

## 8. Agent Integration

An HTTP service, an MCP server, Python bindings, a Node SDK, and a `mnesio-code`
CLI that maps a codebase with no server. The installer "verifies a SHA-256,
refuses to overwrite a different tool of the same name, and does not touch your
shell profile."

## 9. Reliability, Safety, and Trust

The gate floor and its test are the strongest part, with the bitemporal liveness
rule and the replay invariant behind them. The weaker parts are that the
evaluation behind the gate rests on canaries and an objective nobody has pinned
to a corpus, that crypto-shredding leaves nothing keyed on the erased value, and
that no person is consulted before a rewritten policy takes effect.

## 10. Tests, Evals, and Benchmarks

Unit tests that trip each baseline condition separately with a message naming
it, an end-to-end suite covering the diversity gate, canary failure and the
empty-reflection case, and the relaxed-gates test that holds the README's
strongest claim. A benchmarks document sits beside three competitive-analysis
files.

## 11. For Your Own Build

Put a floor under your thresholds. A gate that is only a set of configurable
numbers can be widened until it admits anything, and the difference between a
floor and a default is one test that relaxes everything and still expects a
refusal.

Make liveness require both clocks. `valid && known` is four words, and it is the
difference between "was true then" and "we knew it then".

Carry the scope into the hop, not just into the query. A traversal that checks
scope once and then follows edges is a traversal that leaves its scope.

Let your projection be disposable. If the graph can be dropped and rebuilt from
the log, the log is where correctness has to live — which is where it is easiest
to keep.

## 12. Open Questions

Whether a person belongs before a policy activates. The floor is mechanical and
well-defended; what it cannot judge is whether a prompt rewrite that improves
the objective is one the operator would have wanted, and the system's own
subject matter makes that the live question.

Whether the canary set and the objective should be pinned the way the gate is.
The gate's strength is that a configuration cannot weaken it; the evaluation
feeding it has no equivalent guard, so a thinned canary set weakens the same
floor from the other side.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `crates/mnesio-core/src/event.rs:215-219` | A safety floor small enough to read in one glance |
| `crates/mnesio-procedural/tests/compile_e2e.rs:237` | Relax every threshold, expect the refusal anyway |
| `crates/mnesio-graph/src/record.rs:138-146` | Liveness as the conjunction of two clocks |
| `crates/mnesio-graph/src/traversal.rs:56-79` | Scope re-resolved at every hop |

## History

**2026-09-16** — [`5831aa0ea0a359b44a3a28b64e7e9f7174d88970`](https://github.com/mnesio/mnesio/commit/5831aa0ea0a359b44a3a28b64e7e9f7174d88970) — first reading, at a commit dated 13 September 2026. Screened before opening, from a shallow clone: one auto-run surface, three build-time execution points, three unpinned dependency surfaces and twenty-five dependency files inside the seven-day cooldown. Nothing was installed, built or run; the install script was read but not executed, and no benchmark or evaluation was reproduced.

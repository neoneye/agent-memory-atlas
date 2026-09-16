---
title: "HOLO-Invariant"
eyebrow: "It scores a naive baseline on its own benchmark, and says which metrics the baseline wins"
description: "A continuity framework whose committed fixture is hashed before results are observed, whose pass condition pairs full recall of the latest claims with zero resurrections of superseded ones, and whose own result payload records that no truth was claimed."
root: ../..
page_kind: system
source_name: "Deathburgerz013/HOLO-Invariant"
source_url: https://github.com/Deathburgerz013/HOLO-Invariant
archive_name: "Deathburgerz013--HOLO-Invariant"
revision: 2d36396a060f28ec68110f7697b893d2c8cff859
revision_url: https://github.com/Deathburgerz013/HOLO-Invariant/commit/2d36396a060f28ec68110f7697b893d2c8cff859
analyzed_at: 2026-09-16
capabilities: "negative_eval"
capability_evidence:
  negative_eval: "the pass condition requires that no superseded claim comes back as current *and* that every latest justified claim is recovered, scored against a hash-pinned fixture and regenerated in CI | holosim/continuity_baseline_benchmark.py:153-190, benchmarks/continuity-v1.fixture.json, tests/test_latest_value_continuity_baseline.py:75-150 | The scorer collects `superseded_resurrected_as_current` and reports its length, and `passes_bounded_continuity_fixture` is `latest_recall == 1.0 and not resurrected and uncertainty_recall == 1.0 and lineage_recall == 1.0 and stale_blocked` — so the must-not-resurrect assertion cannot pass vacuously, because the same condition demands the store return everything current. The fixture \"fixes the target before results are observed\", the condition schema is closed \"so undeclared fields cannot alter the scoring contract\", the baseline test asserts `holo_reference[\"fixture_hash\"] == fixture[\"fixture_hash\"]` before comparing, and the reference result is \"regenerated from the same committed fixture and condition on every change\" | tests/test_continuity_benchmark_ci.py, tests/test_public_continuity_benchmark.py"
stack_storage: "files"
stack_retrieval: ""
stack_source: "reviewed"
matrix:
  memory_unit: "A claim with retained evidence, a lineage of correction edges, and an uncertainty record — an original observation, a correction, and the relation between them all stay inspectable"
  storage: "Local files with canonical hashing; zero runtime dependencies"
  retrieval: "Not a retrieval engine — reconstruction and checking of state across sessions, models and tools"
  write: "A correction is a verified relation bound to an exact baseline transition candidate, authorized before it becomes the baseline"
  update_delete: "Correction never replaces history: \"[o]riginal, correction, and target remain inspectable\""
  scoping: "Authority is explicit and bounded; the demo \"does not modify an existing chain or grant truth, acceptance, write, or execution authority\""
  integration: "A CLI (`holo demo`, `holo benchmark continuity`), a closed condition schema, and an interop directory"
  background: "None; the work is transitions and checks"
  trust: "A hash-pinned public fixture, a CI-regenerated reference result, a baseline scored on the same target, and result payloads that record `truth_claimed: false`"
  strengths: "The benchmark is built the way a benchmark has to be built to mean anything, and this atlas has read very few like it. The fixture is committed and hashed, and \"fixes the target before results are observed\"; the condition schema is closed \"so undeclared fields cannot alter the scoring contract\"; the reference result is regenerated from the same fixture on every change; and the comparison test asserts the two results share a `fixture_hash` before reading either. Then the part that makes the number honest: a naive latest-value store is scored on the identical fixture and **wins two of the five metrics** — `latest_justified_recall` is 1.0 and `superseded_resurrection_count` is 0 for the baseline too — with the test asserting those deltas are exactly zero under a comment saying so: \"[t]he difference is specifically uncertainty + lineage + stale-continuation behavior, not latest-value recall.\" A benchmark whose author writes down which of its metrics the trivial alternative already passes is making a narrow, checkable claim instead of a flattering one. The same restraint runs through the artifacts: every result payload carries `truth_claimed: false` and `accepted: false`, and the demo's own description ends \"[i]t does not modify an existing chain or grant truth, acceptance, write, or execution authority\""
  risks: "This is a framework for checking continuity rather than a memory an agent writes to. There is no store with a read path, no scoping model over stored content, no audit record of mutations — the transitions are the subject — and nothing here retrieves. A reader looking for a memory backend will find a scoring contract and a correction-transition model, which is the useful thing here and not the advertised one. The metrics are also bounded in the literal sense: five properties over one fixture of a chosen shape, so passing says the system represents uncertainty, lineage and stale continuation *on that fixture*, and generalisation is the reader's inference rather than the benchmark's claim — which the naming (`passes_bounded_continuity_fixture`) concedes. At 91,867 lines across two hundred-odd modules with a vocabulary of its own — spine protocol, invariant catalog, baseline transition candidates, typed operational authorization — the cost of entry is high relative to the five metrics at the centre"
---

## 1. Executive Summary

HOLO-Invariant is "AI continuity that preserves corrections instead of hiding
them" — MIT, Python 3.10+, 91,867 lines across roughly two hundred modules with
1,603 test functions in 218 test files, and zero runtime dependencies. It is a
framework for preserving, reconstructing and checking state across sessions,
models, tools and execution environments.

Its README states the contrast as a table, and every row is a failure this atlas
reports somewhere: correction replaces history, the latest value hides its
lineage, resume trusts supplied context, memory authority is implicit. Against
each: correction becomes a verified relation, original and correction and target
all stay inspectable, resume checks externally retained evidence, authority stays
explicit and bounded.

**The benchmark is the reason to read it.** Five bounded metrics over one
committed fixture:

| Metric | Reference |
| --- | --- |
| Latest justified recall | 1.0 |
| Superseded resurrection count | 0 |
| Uncertainty recall | 1.0 |
| Lineage recall | 1.0 |
| Stale continuation blocked | true |

Four things make that table mean something. The fixture is public and hashed, and
"fixes the target before results are observed". The condition schema is closed
"so undeclared fields cannot alter the scoring contract" — a candidate cannot add
a field that changes how it is scored. The reference result is "regenerated from
the same committed fixture and condition on every change" in CI. And the
comparison test asserts `holo_reference["fixture_hash"] == fixture["fixture_hash"]`
before reading a single metric.

**Then it scores the trivial alternative, and reports which metrics the trivial
alternative wins.** A plain latest-value store is run against the identical
fixture, and the test records that it passes two of the five: its
`latest_justified_recall` is 1.0, and its `superseded_resurrection_count` is 0 —
"[i]t does not resurrect the overwritten value as current." It fails exactly
three: uncertainty recall, lineage recall, and stale-continuation blocking. And
the deltas are asserted to be *zero* on the two the baseline already wins, under
a comment that states the claim in one sentence:

> "The difference is specifically uncertainty + lineage + stale-continuation
> behavior, not latest-value recall."

This atlas has read a great many benchmarks. Very few name the metrics their
baseline already passes. Doing so converts a five-for-five scoreboard into a
narrow claim — *this system represents uncertainty, lineage, and staleness, and
ordinary storage does not* — which is both smaller and worth something, because
it can be checked and could have come out the other way.

The pass condition is why this earns the negative-evaluation mark rather than
just admiration. `passes_bounded_continuity_fixture` is

```python
latest_recall == 1.0 and not resurrected and uncertainty_recall == 1.0
and lineage_recall == 1.0 and stale_blocked
```

— a must-not-retrieve assertion (no superseded claim comes back as current) that
cannot pass vacuously, because the same condition demands full recall of
everything that *is* current. A store that returned nothing would fail the first
clause. The control is in the pass condition itself.

**The artifacts refuse to claim more than they show.** Every result payload
carries `truth_claimed: false` and `accepted: false`. The demo's description ends:
"[i]t does not modify an existing chain or grant truth, acceptance, write, or
execution authority." A correction is bound to one exact baseline transition
candidate and sits at `READY_FOR_EXACT_TARGET_AUTHORIZATION` until authorized
against that target — the same bind-to-one-operation property this atlas found in
[Anda DB](../anda-db/)'s approvals and [Edda](../edda/)'s verdicts.

What this is not: a memory an agent writes to. There is no store with a read
path, no scoping over stored content, and no mutation record — the transitions
are the subject. A reader arriving for a memory backend will find a scoring
contract and a correction model, which is the valuable thing here and not the
thing the category name suggests.

And the metrics are bounded in the literal sense the code names them: five
properties over one fixture of a chosen shape. Passing says the system represents
uncertainty, lineage and stale continuation *on that fixture*; generalisation is
the reader's inference and not the benchmark's claim — which
`passes_bounded_continuity_fixture` concedes in its own identifier.

## 2. Mental Model

A **correction** is a relation, not a replacement.

A **fixture** is hashed before anyone runs against it.

A **baseline** is scored on the same target, and told what it won.

A **result** records that it claimed no truth.

```mermaid
%% caption: the pass condition pairs a must-not-resurrect assertion with full recall of current claims, and the naive baseline is scored on the same hash-pinned fixture
flowchart TB
    FIX[("benchmarks/continuity-v1.fixture.json —<br/>public, hashed, 'fixes the target<br/>before results are observed'")]
    SCH["schemas/continuity-condition.schema.json —<br/>closed, 'so undeclared fields cannot<br/>alter the scoring contract'"]
    FIX --> SCORE{"score a condition"}
    SCH --> SCORE
    SCORE --> M1["latest_justified_recall"]
    SCORE --> M2["superseded_resurrection_count<br/>= len(superseded_resurrected_as_current)"]
    SCORE --> M3["uncertainty_recall"]
    SCORE --> M4["lineage_recall"]
    SCORE --> M5["stale_continuation_blocked"]
    M1 & M2 & M3 & M4 & M5 --> PASS{"passes_bounded_continuity_fixture =<br/>latest_recall == 1.0 AND not resurrected<br/>AND uncertainty_recall == 1.0<br/>AND lineage_recall == 1.0 AND stale_blocked"}
    PASS -.->|"the must-not-resurrect clause cannot<br/>pass vacuously — the same condition<br/>demands full recall of what IS current"| CTRL["the control is in the pass condition"]
    BASE["a naive latest-value store,<br/>scored on the IDENTICAL fixture"] --> SCORE
    BASE --> WINS["wins two metrics:<br/>latest_justified_recall = 1.0<br/>superseded_resurrection_count = 0"]
    BASE --> LOSES["fails three:<br/>uncertainty_recall = 0.0<br/>lineage_recall = 0.0<br/>stale_continuation_blocked = false"]
    WINS -.->|"deltas asserted to be exactly zero:<br/>'the difference is specifically uncertainty +<br/>lineage + stale-continuation behavior,<br/>not latest-value recall'"| CLAIM["a narrow claim instead of<br/>a five-for-five scoreboard"]
    HASHCHK["the comparison asserts both results<br/>share a fixture_hash before reading a metric"] --> SCORE
    OUT["every result payload:<br/>truth_claimed = false,<br/>accepted = false"] --> PASS
    CORR["a correction"] --> CAND["bound to ONE exact baseline<br/>transition candidate —<br/>READY_FOR_EXACT_TARGET_AUTHORIZATION"]
    CAND -->|"authorized against that exact target"| NEWBASE["becomes the baseline;<br/>original, correction and target<br/>all remain inspectable"]
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `holosim/continuity_baseline_benchmark.py` | The scorer, the metrics, the comparison |
| `holosim/spine_protocol.py` | The continuity protocol (1,641 lines) |
| `holosim/verified_claim_correction_transition.py` | A correction bound to one target |
| `holosim/invariant_catalog.py` | The declared invariants |
| `holosim/slot_merkle_sqlite.py` | Hashed slots over SQLite |
| `benchmarks/`, `schemas/` | The fixture, the closed condition schema, CI results |

## 4. Essential Implementation Paths

`holosim/continuity_baseline_benchmark.py:153-190` — the five metrics and the
pass condition that keeps one of them honest.

`tests/test_latest_value_continuity_baseline.py:75-150` — the baseline, what it
wins, and the deltas asserted to zero.

`benchmarks/continuity-v1.fixture.json` — the target, fixed and hashed.

## 5. Memory Data Model

A claim with retained evidence, correction edges forming a lineage, and an
uncertainty record. The model's commitment is that all three survive a
correction: "[o]riginal, correction, and target remain inspectable."

## 6. Retrieval Mechanics

None of its own. Reconstruction and checking rather than search.

## 7. Write Mechanics

A correction becomes a transition candidate bound to one exact baseline, held at
`READY_FOR_EXACT_TARGET_AUTHORIZATION` until a typed authorization for that exact
target arrives. Binding the authorization to the target is what stops one
approval from licensing a different transition.

## 8. Agent Integration

A CLI and a system-neutral condition document, so another continuity system can
be exported into the same shape and scored against the same fixture. That is an
unusual offer — a benchmark designed to be run against its author's competitors
on equal terms — and its value depends entirely on the fixture being fair, which
is why the hash pinning and the baseline scoring matter as much as the metrics.

## 9. Reliability, Safety, and Trust

The trust story is methodological rather than architectural: the fixture, the
closed schema, the CI regeneration, the baseline comparison, and the payload
fields that decline to claim truth or acceptance.

## 10. Tests, Evals, and Benchmarks

1,603 test functions across 218 files, including tests that assert the README's
own table matches the regenerated reference result — so the published number
cannot drift from the computed one. Nothing was installed or run for this
reading; the numbers quoted are the committed ones.

## 11. For Your Own Build

Score the trivial alternative on your own benchmark, and publish what it wins.
A metric the naive baseline already passes is a metric your system should not
take credit for, and saying so is what turns a scoreboard into a claim.

Hash the fixture and close the schema. "Fixes the target before results are
observed" and "undeclared fields cannot alter the scoring contract" are two
sentences that prevent most of the ways a benchmark stops being one.

Put the control in the pass condition. Requiring full recall of current claims
alongside zero resurrections means the negative half cannot be satisfied by a
system that returns nothing.

And let your artifacts say what they do not establish. `truth_claimed: false` in
every result is a small field that keeps a downstream reader from importing a
score as a verdict.

## 12. Open Questions

Whether the authorization is human. Transitions are bound to an exact target and
typed; who supplies the authorization was not traced.

How the fixture was chosen. It is fixed and hashed, which makes it fair; whether
its shape favours the model it was built alongside is a question the fixture
cannot answer about itself.

What the spine protocol contributes. At 1,641 lines it is the largest module and
sits outside the benchmark path read here.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `holosim/continuity_baseline_benchmark.py:153-190` | Five metrics, and a pass condition that cannot be gamed by silence |
| `tests/test_latest_value_continuity_baseline.py:75-150` | A baseline scored honestly, including what it wins |
| `holosim/verified_claim_correction_transition.py:1-25` | A correction bound to one exact target |

## History

**2026-09-16** — [`2d36396a060f28ec68110f7697b893d2c8cff859`](https://github.com/Deathburgerz013/HOLO-Invariant/commit/2d36396a060f28ec68110f7697b893d2c8cff859) — first reading, at a commit dated 15 September 2026. Screened before opening, from a shallow clone: four files scanned, no auto-run surfaces, no build-time execution points, one unpinned surface and one dependency file inside the seven-day cooldown. Nothing was installed, built or run, and no benchmark was executed.

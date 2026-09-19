---
title: "NEOTH"
eyebrow: "A high importance score is not a fact, and the table says so"
description: "A local-first personal AI daemon whose operator-asserted ground truth lives in its own decay-immune table rather than above an importance threshold, surfaces before any episodic row, and drops out of recall when a contradiction flags it."
root: ../..
page_kind: system
source_name: "The-Geek-Freaks/NEOTH"
source_url: https://github.com/The-Geek-Freaks/NEOTH
archive_name: "The-Geek-Freaks--NEOTH"
revision: 6a37557357b8758f5f826a9f7e655ddca0823110
revision_url: https://github.com/The-Geek-Freaks/NEOTH/commit/6a37557357b8758f5f826a9f7e655ddca0823110
analyzed_at: 2026-09-19
capabilities: "trust_state"
capability_evidence:
  trust_state: "a six-value fact state on the ground-truth table where the recall surface admits only `verified` by default, with widening as a named argument documented as the operator inspection path | SRC/neothd/src/memory/groundtruth.rs:158-165 (`FactState`), :598-607 (the inspection read), :631-658 (`surface_for_recall`), :419, SRC/neothd/src/memory/contradiction.rs:1-8 | `FactState` is Raw / Candidate / Verified / Superseded / Contradicted / Deprecated, persisted in `idx_groundtruth.fact_state`. `surface_for_recall` composes `WHERE revoked_at IS NULL` and appends `AND fact_state = verified` unless the caller passes `include_unverified`, so the default is the narrow set, widening is a deliberate argument, and the doc comment above it says what that argument is for rather than leaving a reader to guess. Revocation is a separate condition on the same query, so a revoked fact is out whatever its state. Contradiction detection populates the withholding value: it flags the lower-credibility fact — the one with fewer corroborating sources — as Contradicted so it drops out of recall, which the comment ties back to the gate by name. Ground truth is also decay-immune by construction, with no Hebbian decay, no forget-floor sweep and no consolidation pass, and is surfaced ahead of any episodic row so a stale decayed memory cannot overwrite an operator fact | SRC/neothd/src/memory/groundtruth.rs:1081"
stack_storage: "sqlite, files"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "Five tiers plus an operator vault; the tier this report reads is a ground-truth fact — statement, source, scope, asserted and revoked timestamps, fact state, source weight, confidence, evidence, maturity and a confirmed count"
  storage: "SQLite indexes beside a write-ahead log with a single-writer invariant, `O_APPEND`, `fdatasync` per flush, mode 0600 and size- or age-based segment rotation"
  retrieval: "Hybrid retrieval across the tiers, with ground truth surfaced ahead of any episodic row"
  write: "Ground-truth promotion is always explicit (`neoth groundtruth add`); episodic memory accrues through the daemon"
  update_delete: "Revocation sets `revoked_at`; contradiction flags the lower-credibility side rather than deleting either; a forget sweep and consolidation touch episodic memory but never ground truth"
  scoping: "A `scope` column on ground truth, carried and not enforced on the recall path"
  integration: "A local daemon with bridges, a GUI, a plugin SDK with a WASM sandbox, and origin-bound consent before any outbound provider route"
  background: "Decay, consolidation sweeps, drift detection, a compaction guard and an evaluation harness"
  trust: "A decay-immune ground-truth table with its own scoring path, a six-value fact state gating recall, contradiction detection over operator facts, and consent markers the operator can audit with `ls`"
  strengths: "The ground-truth module is built against a failure it names in its own header: \"[s]liding 'if importance ≥ 0.95 treat as fact' is the failure mode this module exists to prevent.\" A continuous importance score is not a trust state — something this atlas withholds marks over repeatedly — and the answer here is a separate table with its own scoring path, \"no Hebbian decay, no FORGET_FLOOR sweep, no consolidation pass\", explicit promotion, explicit revocation, and placement \"in every recall hit BEFORE any episodic row so a stale Hebbian-decayed memory cannot overwrite an operator ground truth\". The contradiction detector over those facts is pragmatic and careful: it splits a statement at the first copula into a subject and a value part, requires subject similarity above a threshold, and then fires on either a polarity difference (bilingual negation markers) or diverging value tokens — with the superset case explicitly excluded, so \"nas at X\" against \"nas at X primary\" is not flagged. It then flags the *lower-credibility* side by corroborating-source weight rather than by recency. Consent is equally concrete: every remote provider route is granted under a marker file, canonical-origin grant sets mean \"endpoint A never authorizes endpoint B\", loopback Ollama is treated as local while LAN and public endpoints are not, and the markers are files \"so the operator [can] audit consent state with `ls ~/.neoth/consent/`\""
  risks: "The scale is the first thing to weigh: 1,119,998 lines of Rust, of which `neothd` alone is 1,002,851 in one crate with a 22,382-line chat module and 15,232 test functions — the memory subsystem this report reads is 52,353 of them, under five per cent. `scope` is a column on a ground-truth row and no scope predicate appears on the recall path, so it tags rather than isolates. The contradiction detector's always-available core is token-Jaccard over normalised statements with an optional semantic lift, so it is a textual comparison with a subject/value split rather than a claim-level one, and the thresholds are constants. And the write-ahead log is a durability mechanism — single writer, append-only, fdatasync, 0600, rotation — rather than a mutation record carrying an actor and an action, so a reader wanting to know who changed a fact and when has `asserted_at`, `revoked_at` and the contradiction ledger rather than a log of changes"
---

## 1. Executive Summary

NEOTH is "[y]our private AI buddy" — a local-first personal AI daemon in Rust,
dual MIT and Apache-2.0, 1,119,998 lines with 15,232 test functions in its daemon
crate, offering "[o]ne memory. Three brain paths. Five memory tiers + your vault."
It ships a GUI, bridges, a plugin SDK with a WASM sandbox, and a migration tool.

The memory subsystem is 52,353 lines of that, and one module in it is built
against a mistake this atlas withholds marks over again and again. Its header:

> "Sliding 'if importance ≥ 0.95 treat as fact' is the failure mode this module
> exists to prevent."

**Ground truth is a table, not a threshold.** Facts the operator stated
explicitly live in `idx_groundtruth` with their own scoring path — "no Hebbian
decay, no FORGET_FLOOR sweep, no consolidation pass" — promoted only by an
explicit command and revoked by another. And they are placed rather than merely
stored: surfaced "in every recall hit BEFORE any episodic row so a stale
Hebbian-decayed memory cannot overwrite an operator ground truth."

That is the correct structural answer to a problem most systems here solve with a
number. An importance score is continuous, drifts with reinforcement, and offers
no place to record that a person asserted something; a separate table with its
own lifecycle does all three.

**The state gates recall.** `FactState` is `Raw | Candidate | Verified |
Superseded | Contradicted | Deprecated`, and `surface_for_recall` emits
`WHERE revoked_at IS NULL` plus `AND fact_state = 'verified'` unless a caller
passes `include_unverified`. Narrow by default, widened by an argument, with
revocation as a separate terminal condition — the shape this atlas marks.

**Contradiction is what fills the withholding value, and it is carefully
bounded.** Two operator facts can disagree — the module's own examples are "the
nas is at X" against "the nas is at Y", and "the vpn is up" against "the vpn is
not up". The detector splits each statement at the first copula into a subject
part and a value part, requires subject-Jaccard above a threshold, then fires on
either a polarity difference — using bilingual English/German negation markers —
or diverging value tokens. And the case it deliberately does not fire on is the
one that matters:

> "a superset like 'nas at X' vs 'nas at X primary' is NOT flagged"

A refinement is not a contradiction, and a detector that treats it as one
produces a contradiction ledger nobody reads. When it does fire, it flags the
*lower-credibility* fact — fewer corroborating sources by the store's source
weight — rather than the older one, so recency does not decide.

**Consent is a file the operator can list.** Every remote provider route requires
an explicit grant under `~/.neoth/consent/`, with canonical-origin grant sets so
"endpoint A never authorizes endpoint B", in-process providers never gating, and
Ollama treated as local on loopback but requiring the same origin-bound consent
on LAN or public endpoints. The rationale for files over configuration is
practical and good: markers "survive `neoth init` reconfigure passes that rewrite
`freedom.yaml`, and they let the operator audit consent state with
`ls ~/.neoth/consent/`."

What to weigh. The scale is extraordinary — one crate of a million lines with a
22,382-line chat module — and the memory subsystem this report covers is under
five per cent of it. `scope` is a column on a ground-truth row and no scope
predicate appears on the recall path, so it tags rather than isolates. The
contradiction core is token-Jaccard with an optional semantic lift, so it is a
textual comparison with a structural split rather than a claim-level one, and its
thresholds are constants. And the write-ahead log — single writer, `O_APPEND`,
`fdatasync` per flush, mode 0600, rotation at 16 MiB or 24 hours — is a
durability mechanism rather than a mutation record with an actor and an action,
so the question "who changed this fact" is answered by `asserted_at`,
`revoked_at` and the contradiction ledger rather than by a change log.

## 2. Mental Model

A **fact** is something the operator said, and it lives somewhere episodic memory
cannot reach.

A **score** is not a fact, and the table is the difference.

A **contradiction** demotes the side with fewer sources, not the older one.

A **refinement** is not a contradiction.

```mermaid
%% caption: ground truth has its own table and scoring path so no importance threshold can promote an episodic memory into a fact, and recall surfaces only verified, unrevoked rows
flowchart TB
    OP["the operator: neoth groundtruth add"] --> GT[("idx_groundtruth — statement · source ·<br/>scope · asserted_at · revoked_at ·<br/>fact_state · source_weight · confidence ·<br/>evidence · maturity · confirmed_count")]
    EPI[("episodic tiers")] --> DECAY["Hebbian decay · FORGET_FLOOR sweep ·<br/>consolidation pass"]
    DECAY -.->|"none of these touch ground truth —<br/>'no Hebbian decay, no FORGET_FLOOR sweep,<br/>no consolidation pass'"| GT
    THRESH["'if importance >= 0.95 treat as fact'"] -.->|"'the failure mode this module<br/>exists to prevent'"| GT
    CD["contradiction detection over operator facts"] --> SPLIT["split each statement at the first copula:<br/>SUBJECT part · VALUE part"]
    SPLIT --> S1{"subject-Jaccard >= threshold?"}
    S1 -->|"no"| NONE["not a pair"]
    S1 -->|"yes"| S2{"polarity differs (bilingual negation markers)<br/>OR value tokens diverge?"}
    S2 -->|"value is a SUPERSET —<br/>'nas at X' vs 'nas at X primary'"| NOTFLAG["NOT flagged — a refinement<br/>is not a contradiction"]
    S2 -->|"yes"| LEDGER[("idx_contradictions")]
    LEDGER --> DEMOTE["flag the LOWER-credibility fact<br/>(fewer corroborating sources by<br/>source_weight) as FactState::Contradicted<br/>— not the older one"]
    DEMOTE --> GT
    GT --> RECALL{"surface_for_recall"}
    RECALL -->|"default"| NARROW["WHERE revoked_at IS NULL<br/>AND fact_state = 'verified'"]
    RECALL -->|"include_unverified passed"| WIDE["the caller widens deliberately"]
    NARROW --> ORDER["surfaced BEFORE any episodic row,<br/>'so a stale Hebbian-decayed memory cannot<br/>overwrite an operator ground truth'"]
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `memory/groundtruth.rs` | The fact table, its states, and the recall gate |
| `memory/contradiction.rs` | Subject/value split, polarity, the ledger, demotion |
| `memory/forget.rs`, `decay_task.rs`, `consolidation_sweep.rs` | The episodic lifecycle ground truth is exempt from |
| `memory/drift.rs`, `compaction_guard.rs`, `eval_harness.rs` | Drift, compaction safety, evaluation |
| `wal/writer.rs` | Durability: one writer, append-only, fdatasync, 0600 |
| `consent.rs` | Origin-bound grants before any outbound route |

## 4. Essential Implementation Paths

`SRC/neothd/src/memory/groundtruth.rs:1-14` — the failure mode, named, and the
structural answer.

`SRC/neothd/src/memory/groundtruth.rs:635-653` — narrow by default, widened by an
argument.

`SRC/neothd/src/memory/contradiction.rs:1-18` — what counts as a disagreement,
and what does not.

`SRC/neothd/src/consent.rs:1-14` — grants as files, and why not configuration.

## 5. Memory Data Model

Five tiers plus a vault; the tier read here is ground truth, whose row carries a
source constrained at insert time "so the audit trail stays clean", a scope, a
source weight, a confidence, evidence, a maturity and a confirmed count. The
confirmed count and source weight are what let contradiction demote by
credibility rather than by recency.

## 6. Retrieval Mechanics

Hybrid retrieval across tiers with ground truth placed ahead of episodic rows.
The ordering is the mechanism: a fact that merely scored higher would still be
competing with decayed episodic memories on one scale, and this takes it off that
scale entirely.

## 7. Write Mechanics

Explicit promotion, explicit revocation, and a contradiction pass that writes a
ledger row and a state rather than deleting either side. Nothing in the episodic
lifecycle can promote into the fact table.

## 8. Agent Integration

A daemon with bridges, a GUI, a WASM plugin sandbox, and consent gating between
the local system and any cloud provider. The consent design's endpoint-awareness
— loopback Ollama local, LAN and public not — is the kind of distinction that is
usually collapsed.

## 9. Reliability, Safety, and Trust

The trust story is the separation: operator facts in their own table, exempt from
the decay and forgetting that govern everything else, ordered ahead of it, and
withheld when contradicted. The gap is a change record — the WAL gives durability
rather than accountability.

## 10. Tests, Evals, and Benchmarks

15,232 test functions in the daemon crate, with an evaluation harness inside the
memory module itself. Nothing was built or run for this reading.

## 11. For Your Own Build

Do not let a threshold promote a memory into a fact. An importance score is
continuous and drifts with reinforcement; if you want "the operator said so" to
mean something, it needs a table, a lifecycle and a place in the ordering.

Exempt facts from the sweeps explicitly. "No Hebbian decay, no FORGET_FLOOR
sweep, no consolidation pass" is a sentence you should be able to write about
your own fact store.

Do not flag a refinement as a contradiction. "nas at X" against "nas at X
primary" is the case that fills a contradiction ledger with noise, and excluding
it is one condition.

Demote by credibility, not recency. The newer statement is not the better
supported one, and choosing by corroborating sources says which rule you are
applying.

And make consent something the operator can list. A marker file survives the
reconfiguration that rewrites your config, and `ls` is an audit interface nobody
has to build.

## 12. Open Questions

Whether scope is ever enforced. It is a column on every ground-truth row and no
predicate on the recall path was found.

What the other four tiers do with fact state. The gate read here is ground
truth's; how the episodic tiers treat a contradicted subject was not traced.

Whether the semantic lift changes the contradiction rate. It is optional over the
Jaccard core, and no comparison was found.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `SRC/neothd/src/memory/groundtruth.rs:1-14`, `:158-165` | A named failure mode and a six-value state |
| `SRC/neothd/src/memory/groundtruth.rs:635-653` | Narrow by default, widened on purpose |
| `SRC/neothd/src/memory/contradiction.rs:1-18` | A disagreement, and a refinement that is not one |
| `SRC/neothd/src/consent.rs:1-14` | Grants as files an operator can audit with `ls` |

## History

**2026-09-19** — [`6a37557357b8758f5f826a9f7e655ddca0823110`](https://github.com/The-Geek-Freaks/NEOTH/commit/6a37557357b8758f5f826a9f7e655ddca0823110) — `trust_state` re-tested against the narrowed line and every anchor held. `FactState` is still the six values at `SRC/neothd/src/memory/groundtruth.rs:158-165`, and `surface_for_recall` (`:631-658`) still composes `WHERE revoked_at IS NULL` and appends `AND fact_state = 'verified'` only when the caller has not asked to widen. Two things are added to the record. The doc comment above that function names what the widening argument is *for* — the operator inspection path that also returns candidates — so a reader does not have to infer it from the parameter name, and there is a second, separate read at `:598-607` that deliberately returns all trust states for one scope under the same revocation condition. Having the narrow default and the wide inspection as two named functions rather than one function and a boolean is the clearer arrangement, and this system has both. Revocation stays a separate condition on the same query, so a revoked fact is out whatever its state. Screened again first; nothing was installed and no suite was run.

**2026-09-16** — [`6a37557357b8758f5f826a9f7e655ddca0823110`](https://github.com/The-Geek-Freaks/NEOTH/commit/6a37557357b8758f5f826a9f7e655ddca0823110) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: thirty-four files scanned, no auto-run surfaces, two build-time execution points, no unpinned surfaces and twenty-eight dependency files inside the seven-day cooldown. Nothing was installed, built or run.

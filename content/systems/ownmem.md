---
title: "OwnMem"
eyebrow: "A rejection you cannot tell from silence"
description: "A git-native memory for coding agents whose candidate ledger keeps every refusal with the reason and the summary, because a rejection with no record of what was rejected reads exactly like an extractor that never fired."
root: ../..
page_kind: system
source_name: "grpcer/ownmem"
source_url: https://github.com/grpcer/ownmem
archive_name: "grpcer--ownmem"
revision: 14f4edec52ebc5d1dcf7794f451d3e6d2c64e969
revision_url: https://github.com/grpcer/ownmem/commit/14f4edec52ebc5d1dcf7794f451d3e6d2c64e969
analyzed_at: 2026-09-13
capabilities: "tombstone, trust_state, audit_log, human_review, negative_eval"
capability_evidence:
  tombstone: "the candidate ledger — a refusal keyed on a digest of what was observed | lib/memory-candidates.mjs:90-92 (`candidateId`), :306-330 (`mergeMemoryCandidates`), :333-350 (`rejectMemoryCandidate`) | `rejectMemoryCandidate` moves a candidate into `ledger.rejected`, keeps its summary, and throws unless a reason is supplied; `mergeMemoryCandidates` checks `merged.rejected[candidate.candidate_id]` on every extraction pass and suppresses a match rather than re-queueing it. The key is a value: `candidateId` is `digest(\"recovery <identity> <first_failure_at>\")`, so the same observation re-extracted yields the same id and hits the refusal. The docstring states the reason the record exists — a rejection with no record of what was rejected *\"is indistinguishable from a candidate that was never generated\"*. The bound worth knowing: `first_failure_at` is inside the digest, so a fresh failure run of the same identity is a new id and is not suppressed | test/ carries four self-tests; not run, the screen reports one auto-run surface and two dependency files inside the cooldown"
  trust_state: "the memory, as a nine-value lifecycle with a risk tier gating what may promote it | schemas/promotion/decision.schema.json:20-32 | `current_lifecycle` and `target_lifecycle` range over `observed, candidate, shadow, advisory, active, stale, deprecated, rejected, superseded`, and the states that withhold are explicit — a source comment at lib/memory-candidates.mjs:124-126 says `candidate` is *\"the one state with no path into a delivered context\"* while `observed` is a lifecycle a memory can be recalled at. Risk runs R0-R5 beside it and `automation` is `auto`, `review`, `pr-only` or `forbidden`. The schema encodes the invariants rather than trusting the policy layer: R4 and R5 *\"can never be encoded as automatic, whatever the evidence or the repository configuration says\"*, and R5 — the control plane — *\"may not take effect from inside at all\"* | schema validation is the assertion; the suite was not run"
  audit_log: "promotion — an append-only receipt ledger of decisions, anchored to things the repository can recompute | lib/memory-promotion-receipt.mjs:10, :22, :222-224, lib/memory-observability.mjs:59, :270 | the receipt module states its own shape: *\"one append-only ledger; applying a change is somebody else's decision\"*, with each anchor *\"something the repository can recompute -- a file hash, a symbol fingerprint, a git object\"*, so a receipt can be checked against the tree later rather than believed. It stores *\"a digest, never the text\"* — a feedback anchor records the hash of the query — so the ledger does not become a second copy of the material. Beside it `memory-observability.mjs` appends daily `events-YYYY-MM-DD.jsonl` files and trims an interrupted trailing partial line before appending so a torn write cannot corrupt the next event | test/ self-tests; not run"
  human_review: "promotion — review is a state the automation cannot leave, not a screen | schemas/promotion/decision.schema.json:32, :55-58, schemas/promotion/review-material.schema.json, lib/memory-review-material.mjs, lib/memory-candidates.mjs:300-302, :340-341 | `automation` is a required field of every decision and its `review` and `pr-only` values are reachable only by a person; the schema forces R4 and R5 away from `auto` regardless of configuration, and a decision that is `auto` while naming a blocker is rejected as *\"self-contradictory, and it is the exact shape a bug in the resolver would produce\"*. Candidates are emitted with `requires_human_review: true` and `can_authorize_actions: false`, and rejecting one throws without a written reason. `review-material.schema.json` types what a reviewer is shown as `correction-candidate` or `proposed-change` | schema validation; the suite was not run"
  negative_eval: "retrieval — sixteen committed queries that must return nothing, scored beside the positives on the same corpus | benchmarks/corpus.json:167, benchmarks/public-benchmark.mjs:266-276, :381-383 | `negative_queries` holds nonsense across locales — *\"quantum foam renderer calibrates lunar antenna\"* and its Chinese variants — and `negativeAccuracy` counts a case as passing only when the ranking is empty, recording every non-empty result as a `false_positive` carrying the query and what was wrongly returned. It is not vacuous because the same run computes `recall_at_1` over the same corpus, so the store is demonstrably populated. `worst_language_negative_abstain_rate` gates the worst locale rather than the mean. The shape is abstention on unrelated queries rather than a named value that must not come back | `node benchmarks/public-benchmark.mjs`; not run here"
stack_storage: "files"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "A markdown topic in the repository with front matter, carrying a lifecycle, a logical type, a risk tier and scope tokens"
  storage: "Files in the git working tree — topics, a candidate ledger with a rejected map, append-only promotion receipts and daily JSONL event files"
  retrieval: "A feature-weighted lexical ranker over tokenized topics; scope tokens are one scoring feature among many rather than a filter"
  write: "Extraction proposes candidates; nothing reaches a delivered context from `candidate`, and promotion is a decision record with a risk tier and an automation mode"
  update_delete: "A refusal is kept — `rejectMemoryCandidate` requires a reason, retains the summary, and later extractions of the same digest are suppressed"
  scoping: "Scope tokens on a topic contribute to the ranking score; there is no stored scope key applied as a filter on the read path"
  integration: "A CLI, a Claude Code plugin, a Gemini extension manifest, skills and commands — all reading and writing files in the repository"
  background: "None over the store; extraction, duplicate auditing and benchmarking run on demand"
  trust: "A nine-value lifecycle from observed to superseded, with R0-R5 risk gating whether promotion may be automatic at all"
  strengths: "A rejection ledger keyed on a digest of the observation, with the reason required; schema-level invariants that bind a hand-built decision, including that the control plane cannot promote itself"
  risks: "The rejection digest includes the first failure timestamp, so a fresh failure run of the same identity is not suppressed; scope is a ranking feature, not a boundary"
---

## 1. Executive Summary

OwnMem is git-native memory for coding agents — Apache-2.0, about 35,300 lines of
JavaScript, no database. Memories are markdown topics in the repository's working
tree, retrieved by a feature-weighted lexical ranker, and everything the system
knows travels with a clone.

Five marks, and two of them are the same idea applied twice: **a refusal is a
record, not an absence.**

`rejectMemoryCandidate` (`lib/memory-candidates.mjs:333`) throws unless the caller
supplies a reason, moves the candidate into `ledger.rejected`, and keeps its
summary. The docstring says why, and it is the argument this atlas makes about
tombstones in the project's own words:

> The reason is required and the summary is kept, because a rejection with no
> record of what was rejected is indistinguishable from a candidate that was never
> generated, and the next reader cannot tell whether the extractor is quiet or the
> queue is being silently drained.

The record binds because the key is a value. `candidateId` is
`digest("recovery <identity> <first_failure_at>")` (`:90-92`), so re-running the
extractor over the same observation produces the same id, and
`mergeMemoryCandidates` suppresses it rather than putting it back in front of a
reviewer. That is a value-keyed tombstone, and the atlas counts few.

**The second good idea is that the schema argues.** `schemas/promotion/decision.schema.json`
carries nine lifecycle states, six risk tiers and four automation modes, and then
three `allOf` rules that encode the invariants rather than leaving them to the
policy layer. Each states its reasoning in a `description`:

- R4 and R5 *"can never be encoded as automatic, whatever the evidence or the
  repository configuration says. Written here as well as in the policy so that a
  producer building a decision by hand is bound by it."*
- R5 is the control plane — *"policy, gates, permissions, this system's own
  code"* — and *"may not take effect from inside at all, so R5 is not merely
  non-automatic."* The system cannot promote a change to its own governance.
- An `auto` decision that also names a blocker is refused as *"self-contradictory,
  and it is the exact shape a bug in the resolver would produce."*

That last one is a schema constraint written against a specific failure of a
specific component, which is rarer than the constraint.

**What is withheld.** `scope_enforced` is refused: scope tokens exist on a topic
and reach `scopeOverlapFeature` in the ranker (`lib/memory-ranker.mjs:228-233`),
where they contribute to a relevance score. Nothing filters on them, so a scope
here changes what ranks first rather than what is visible.
`bitemporal` is refused for absence — a grep of `lib/` and `schemas/` for
`valid_from`, `valid_until`, `as_of` and their camel-case spellings returns
nothing.

## 2. Mental Model

A memory is a proposal that has to survive a lifecycle before anything reads it,
and the extractor is not allowed to skip ahead.

```mermaid
%% caption: candidate is the one lifecycle with no path into a delivered context, and a rejection is keyed on a digest of the observation so the next extraction pass is suppressed rather than re-queued
flowchart TB
    OBS["extractor observes a recovery,<br/>a correction or a proposal"] --> ID["candidate_id = digest(identity + first_failure_at)"]
    ID --> MERGE{"already in ledger.rejected?"}
    MERGE -->|yes| SUP["suppressed — not re-queued"]
    MERGE -->|no| CAND["lifecycle: candidate<br/>requires_human_review: true<br/>can_authorize_actions: false"]
    CAND --> REV{"a person decides"}
    REV -->|reject, reason required| REJ["ledger.rejected keeps<br/>the id, the reason, the summary"]
    REV -->|promote| DEC["promotion decision:<br/>risk R0-R5, automation mode"]
    DEC --> GATE{"risk tier"}
    GATE -->|"R4 / R5"| HUMAN["pr-only or forbidden —<br/>never auto, whatever the config says"]
    GATE -->|"R0-R3"| AUTO["auto, review or pr-only"]
    HUMAN --> LIFE["observed / shadow / advisory / active"]
    AUTO --> LIFE
    LIFE --> READ["ranker delivers context"]
    CAND -.->|"no path into a delivered context"| READ
```

The dotted edge is the one the source comment insists on: `observed` is a
lifecycle a memory can be recalled at, and `candidate` is not.

## 3. Architecture

No service and no database. The store is the repository: markdown topics, a
candidate ledger, append-only promotion receipts and daily JSONL event files, all
committed. A clone carries the memory, and `git log` is the history of it.

**What it costs to run.** Node, and nothing else. There is no embedding step and
no vector index — retrieval is lexical, which is why the benchmark can be
deterministic and offline.

**Distribution is four front ends over the same files**: a CLI, a Claude Code
plugin, a Gemini extension manifest, and a skills/commands directory.

## 4. Essential Implementation Paths

- **Candidates and refusals** — `lib/memory-candidates.mjs`: `candidateId` (90),
  emission with `requires_human_review` (300-302), `mergeMemoryCandidates` (306-330),
  `rejectMemoryCandidate` (333-350).
- **Promotion contract** — `schemas/promotion/decision.schema.json`: the enums
  (12-32), the three invariant rules (55+); `schemas/promotion/receipt.schema.json`;
  `schemas/promotion/review-material.schema.json`.
- **Receipt ledger** — `lib/memory-promotion-receipt.mjs`: the stated shape (10, 22),
  digest-not-text (222-224), `promotionAnchorRootSha256` (209).
- **Event log** — `lib/memory-observability.mjs`: daily file pattern (59),
  `recordMemoryObservabilityEvent` (270), torn-line trim (218).
- **Ranking** — `lib/memory-ranker.mjs`: feature list (26), `scopeOverlapFeature` (228).
- **Duplicates** — `lib/memory-duplicates.mjs`: `createMemoryFingerprint` (39),
  `compareMemoryFingerprints` (80).
- **Benchmark** — `benchmarks/public-benchmark.mjs`: `negativeAccuracy` (266),
  worst-language gates (381-383); `benchmarks/corpus.json` (negatives at 167).

## 5. Memory Data Model

A topic is markdown with front matter. The interesting fields are the governance
ones: a `lifecycle` from the nine-value vocabulary, a `logical_type` of
`normative`, `procedural`, `factual`, `diagnostic`, `preference` or `feedback`,
scope tokens, and a risk tier that travels with any promotion decision about it.

The candidate ledger is a separate object with `candidates` and `rejected` maps,
both keyed on the same digest. A rejected entry keeps the reason and the summary —
enough for a later reader to see what was refused without the material being
retained in full.

`logical_type` is deliberately nullable, and the comment at
`lib/memory-candidates.mjs:237-239` explains the null case: a user correction is
*"a lead about memories that already exist being wrong, not a proposal to write a
new one of some type. What a reviewer does with it is retire, correct or narrow
the scope."*

## 6. Retrieval Mechanics

A lexical ranker over tokenized topics with a named feature list — code symbols,
code tests, authority documents, scopes and others — combined by weight. There is
no embedding arm and no graph arm.

Scope is a feature, not a filter. `scopeOverlapFeature` tokenizes a document's
`metadata.scopes` and measures overlap with the query, returning 0 when the topic
declares none. A memory scoped to one area is therefore ranked lower for an
unrelated query and never hidden from it, which is the right behaviour for a
single-repository tool and the wrong shape to inherit as a boundary.

## 7. Write Mechanics

Writes are file writes, synchronous, and there is no lag before a memory is
retrievable — the ranker reads the working tree. What stands between an
observation and a delivered context is the lifecycle, not a queue.

Extraction is idempotent by construction: the candidate id is a digest, so a
second pass over the same observation updates `last_seen_at` and leaves
`first_seen_at` alone, *"which is how a growing failure count reaches the reviewer
without spawning a second entry"*. The same key is what makes a refusal durable.

The promotion receipt ledger is append-only and stores anchors rather than
content: a file hash, a symbol fingerprint, a git object, and for feedback the
hash of the query. The module says the separation plainly — it is *"one
append-only ledger; applying a change is somebody else's decision"* — so the
record of what was decided is not also the mechanism that enacts it.

## 8. Agent Integration

A CLI plus plugin manifests for Claude Code and Gemini, and a `skills/` directory.
The agent-facing contract is the lifecycle: an agent can read `active` and
`advisory` memories, can cause candidates to be generated, and cannot promote one.
`can_authorize_actions: false` is stamped on every candidate at emission.

## 9. Reliability, Safety, and Trust

The README grounds the design in five external papers — Reflexion, AgentPoison,
CaMeL on prompt injection, selective classification for abstention, and
metamorphic testing — which is unusual and worth noting because the influence is
visible in the code rather than decorative: abstention is a measured benchmark
metric, and the control-plane rule is CaMeL's separation applied to the system's
own governance.

`CITATION.cff` is a software citation, not a paper. There is no paper of the
project's own.

The torn-write detail in the event log is the kind of care that suggests the
ledger is meant to be trusted: an interrupted trailing partial line is removed
before appending *"so it cannot corrupt the next event"*.

What is missing is a boundary. Everything here is one repository's memory, and the
design leans on that — no scope filter, no principal, no tenancy. That is coherent
rather than careless, and it is the thing that stops the design generalising.

## 10. Tests, Evals, and Benchmarks

Four self-tests under `test/` — structure, public surface, evolution and a
multilingual tokenizer — plus `benchmarks/public-benchmark.mjs` over a committed
corpus with a multilingual supplement.

**The negative arm is the part worth copying.** `benchmarks/corpus.json` commits
sixteen `negative_queries` — nonsense across locales, *"quantum foam renderer
calibrates lunar antenna"* and its Chinese and Polish variants — and
`negativeAccuracy` counts a case as passing **only when the ranking is empty**,
recording every non-empty result as a `false_positive` carrying the query and what
was wrongly returned. A metric that named only a rate would hide which query
broke; this one hands back the counterexample.

It is not vacuous, and the reason is structural rather than lucky: the same run
computes `recall_at_1` over the same corpus, so a configuration that returned
nothing for everything would fail the positive metrics in the same report.
`worst_language_negative_abstain_rate` gates the worst locale rather than the
mean, which is the right aggregation for a multilingual claim.

The shape is abstention on unrelated queries rather than a named value that must
not come back — this report awards `negative_eval` on it and says which kind it is.

Nothing was run. The screen reports one auto-run surface and two dependency files
changed within the seven-day cooldown.

## 11. For Your Own Build

### Steal

**Keep the refusal, with the reason.** Not the decision — the *record*. A
rejection that deletes the candidate leaves a queue that looks identical whether
the extractor is quiet or a reviewer is draining it silently, and nobody can tell
from the outside which they are looking at.

**Key the refusal on a digest of the observation.** Then re-extraction is
suppressed automatically and idempotence and durability are the same mechanism.

**Put the invariant in the schema as well as the policy**, and say in the
description that you did it twice on purpose. *"Written here as well as in the
policy so that a producer building a decision by hand is bound by it"* is the
sentence that makes a duplicated rule a design rather than an oversight.

**Make your own control plane the highest risk tier.** R5 covers policy, gates,
permissions and the system's own code, and cannot take effect from inside at all.
A memory system that can promote a change to its own promotion rules has no rules.

**Return the counterexample, not just the rate.** `false_positives` carries the
query and the wrong answer, so a regression names itself.

**Score abstention beside recall on one corpus.** The positive metric is what
stops the negative one passing vacuously, and running both in the same pass makes
that structural instead of a convention.

### Avoid

**Reading a scope as a boundary when it is a ranking feature.** `scopes` here
raises a score and hides nothing. That is fine for one repository and would be a
leak the first time two principals shared a store.

**Putting a timestamp inside the key you want to suppress on.** `first_failure_at`
is in the digest, so the same identity failing again next week is a new candidate
and the earlier refusal does not reach it. Defensible — it is new evidence — but
it means the tombstone binds an observation rather than a claim.

### Fit

This suits a team that wants project memory reviewed like code, in the repository,
with no service to run and a git history of every decision. The governance is the
product: nine lifecycle states and six risk tiers are a lot of ceremony for a
single developer, and exactly right where a wrong memory would be expensive and a
reviewer already exists.

It is the wrong fit where memory must be scoped between principals, where
retrieval needs semantic reach beyond lexical matching, or where nobody will
review — the lifecycle guarantees that unreviewed candidates never reach a
context, so an unattended deployment gets a queue instead of a memory.

## 12. Open Questions

- **Should the rejection digest drop the timestamp?** Keying on identity alone
  would make a refusal bind a claim rather than one observation of it.
- **What empties the candidate queue in a repository nobody reviews?** Nothing
  promotes on its own below R4 unless configured to, and `candidate` has no path
  into a delivered context.
- **Does the receipt ledger get verified?** The anchors are recomputable by
  design; whether anything recomputes them is not visible in the tree.
- **Would a semantic arm break the abstention metric?** The sixteen negatives pass
  today against a lexical ranker, and an embedding arm returns something for
  everything.

## Appendix: File Index

**Candidates, refusals and promotion**

- `lib/memory-candidates.mjs` — `candidateId` (90), emission (300-302),
  `mergeMemoryCandidates` (306-330), `rejectMemoryCandidate` (333-350)
- `schemas/promotion/decision.schema.json` — enums (12-32), invariant rules (55+)
- `schemas/promotion/receipt.schema.json`, `schemas/promotion/review-material.schema.json`
- `lib/memory-promotion-receipt.mjs` — ledger shape (10, 22), digest-not-text (222-224)
- `lib/memory-review-material.mjs`

**Store and retrieval**

- `schemas/memory.schema.json`; `lib/memory-ranker.mjs` — features (26),
  `scopeOverlapFeature` (228)
- `lib/memory-duplicates.mjs` — `createMemoryFingerprint` (39)
- `lib/memory-observability.mjs` — daily files (59), torn-line trim (218), record (270)

**Evaluation**

- `benchmarks/public-benchmark.mjs` — `negativeAccuracy` (266-276), worst-language
  gates (381-383)
- `benchmarks/corpus.json` — `negative_queries` (167); `benchmarks/supplement.json`
- `test/` — four self-tests

### Commands behind the absence claims

```sh
grep -rn "valid_from\|valid_until\|validFrom\|as_of\|asOf" lib/ schemas/
grep -rn "scopes" lib/memory-ranker.mjs
grep -rn -i "arxiv\|doi" README.md
```

## History

**2026-09-13** — [`14f4edec52ebc5d1dcf7794f451d3e6d2c64e969`](https://github.com/grpcer/ownmem/commit/14f4edec52ebc5d1dcf7794f451d3e6d2c64e969) — first reading. Screened first: one auto-run surface and two dependency files changed within the seven-day cooldown, so nothing was installed and neither the self-tests nor the benchmark was run; every claim about them is a claim about their committed source. Five marks. `tombstone` is earned on a refusal keyed on a digest of the observation, with the reason required and the summary kept — one of the few in this corpus where the project's own docstring makes the argument. `scope_enforced` is withheld: scope tokens reach a ranking feature and no filter. `bitemporal` is withheld for absence, with the grep recorded in the appendix. `CITATION.cff` is a software citation; the project has no paper of its own, and the five papers the README cites are external influences.

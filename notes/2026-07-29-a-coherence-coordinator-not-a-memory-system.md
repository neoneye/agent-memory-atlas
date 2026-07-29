# A coherence coordinator, not a memory system — and the one claim that does not hold

**Status:** analysed; excluded as a system, recorded in overview.md
**Subject:** [Cohexa-ai/agent-coherence](https://github.com/Cohexa-ai/agent-coherence)
at [`7deb931b04d44ca24670e299316820ca4ecc746c`](https://github.com/Cohexa-ai/agent-coherence/commit/7deb931b04d44ca24670e299316820ca4ecc746c)
(2026-07-19), Apache-2.0. Read on 2026-07-29 on request.

## What it is

MESI cache-coherence, applied to shared agent artifacts on a single host. Two
agents share a `plan.md`, a store key, a `memory.json`; one reads it, a peer
commits a newer version, the first writes back anyway and the peer's work is
silently gone. This library turns that into a typed refusal — single-writer
ownership with invalidation, optimistic commit-CAS for concurrent writers, a
read-generation fence for crash-reclaimed ones, and pinned snapshot sessions for
multi-artifact reads.

41,665 lines of Python against 60,163 lines of tests across 158 test files. Eight
TLA+ specifications, six of them model-checked by TLC in CI on every push.
Adapters for LangGraph's store, CrewAI, AutoGen, the OpenAI Agents SDK, plain
files (`CoherentVolume`), and an MCP server.

## The paper sells a different thing than the repository

[arXiv:2603.15183](https://arxiv.org/abs/2603.15183), 16 March 2026, single
author (Vladyslav Parakhin): *"Token Coherence: Adapting MESI Cache Protocols to
Minimize Synchronization Overhead in Multi-Agent LLM Systems."*

The paper's pitch is **cost**. Its abstract argues that naive full-state
rebroadcast costs `O(n × S × |D|)`, proves a "Token Coherence Theorem" bounding
the saving from lazy invalidation, and reports simulated token savings of
95.0% ± 1.3% down to 84.2% ± 1.3% across four workloads. Safety appears as a
supporting clause — "a TLA+-verified protocol enforces single-writer safety,
monotonic versioning, and bounded staleness across ~2,400 explored states."

The repository's pitch is **safety**, and cost is nowhere in its opening
sentence: it "stops one agent from silently clobbering another's work." Same
mechanism, inverted emphasis. Somewhere between March and July the project
decided that preventing a lost update sells better than saving tokens, and on
this atlas's terms that was the right call — a token saving is an optimisation, a
silent clobber is a correctness bug.

The repository has also outgrown the paper. Three invariants over ~2,400 states
became six specs in CI; a 2,400-state model is a small bounded configuration, and
worth naming as such when a paper leads with "TLA+-verified."

**And the numbers are committed, which is the rare part.**
`benchmarks/results/canonical/SUMMARY.md` is headed *"Paper §8 Table 1
Reproduction"* and lists all four figures against tolerances with PASS status,
10 runs per strategy, plus a `manifest.json` carrying a SHA-256 baseline
checksum. CI runs `make benchmark` and then `tools/benchmark_drift_check.py` on
every push. This atlas has repeatedly recorded published memory numbers that
cannot be traced to committed artifacts — Memvid's SOTA claims, MemoryOS's
harness with no scored results, FiFA, MemEvoBench. This is the inverse: the
headline figures are regression-tested.

The caveat is what the numbers are *of*. `broadcast_baseline_tokens` is
`1,966,080`, a closed form — `n × S × m × |d|` — and both arms are simulated
token accounting, not agents doing work. It is an analytical result about a model,
labelled as simulation in the paper's own abstract, and it should not be read as
a measurement of a deployed system. Reproducible and simulated are both true.

## Why it is out of scope

It stores no memory. `CCSStore._apply_put` serialises the value with
`json.dumps(value, sort_keys=True, separators=(",", ":"))` and hands the string
to `core.write` — the content is an opaque blob to be versioned, never parsed,
ranked, extracted, scoped as a belief, corrected or forgotten. What it durably
stores is coordination metadata: ownership state, versions, epochs, snapshot
pins, retention.

That is two exclusion shapes the atlas already has. It is
[a guard, not a store](../content/overview.md) — the OWASP AMG shape — and it is
a durable store the agent *operates* rather than *believes*, the shape that
excluded beads and GAM. `memory.json` appears in its own pitch as an example
artifact, and being *about* a memory file is not being a memory system.

## Why it is worth recording anyway

Every report in this atlas answers a section 9 question about race conditions and
eventual consistency. Across ninety reports, **two** mention lost updates at all:
[Mastra](../content/systems/mastra-observational-memory.md), whose per-scope
in-process locks prevent them, and [Logseq](../content/systems/logseq.md), whose
conflict handling is last-write-wins by editing. The atlas asks the question
ninety times and gets an answer twice.

So the interesting fact is not that this library exists but that it had to. Its
premise — that concurrent agents sharing a memory artifact silently clobber each
other — is a failure mode the corpus almost never addresses, and the corpus is
where the memory systems are.

## The claim that does not hold

The README's formal-methods paragraph says: *"every spec carries a documented
mutant that must fail — the invariants are load-bearing, not decorative."*

The mutants are real and well written. `OCC.tla:95-100` explains that removing
the `obs = cur` conjunct lets a stale commit win, flips `lostUpdate` to TRUE, and
makes TLC report a `NoLostUpdate` violation — *"This is what gives the invariant
teeth."*

**Nothing runs them.** `make tla-check` invokes TLC on six specs and asserts the
invariants hold. `grep -rniE mutant` across `.github/`, `Makefile`, `scripts/`
and `tests/` returns nothing. The mutant is a comment describing an experiment,
and "must fail" is an assertion no CI job makes.

The gap matters for the specific reason the mutant exists. An invariant can pass
vacuously — tighten a guard until the bad state is unreachable and TLC still
reports success, having explored a state space that no longer contains the
failure. The mutant is the standard defence, and it is the one part of this
apparatus that is prose rather than code. A project with 60,000 lines of tests
documented its negative cases in comments and never executed them.

This is the atlas's `negative_eval` finding in an unusual setting. Six of ninety
systems here commit a case asserting that something must *not* happen; the
recurring pattern is that the negative assertion is described far more often than
it is run. Formal verification turns out not to be exempt.

## What is honest about it

Worth stating, because the atlas is quick to note overclaiming and this
repository mostly does the opposite:

- The one-import `CCSStore` swap is documented as **read-side only**: *"It does
  not deny a stale write-back — `put` is not version-CAS."* The code agrees —
  `_apply_put` passes no version to `core.write`.
- `AtomicPublish.tla` is excluded from the CI sweep, and the Makefile says so in
  a comment explaining that its write-set state space needs a bounded encoding to
  converge in budget. An unchecked spec is disclosed rather than counted.
- `on_error` defaults to `"strict"`. I expected a fail-open default in a library
  selling fail-closed behaviour and checked specifically; the degrading
  in-process fallback is opt-in, and the first degradation raises a warning.
- `ttl` on `put` is accepted, ignored, and warned about rather than silently
  dropped.
- The replay tooling states which captures are verified — LangGraph — and which
  are wired through the same seam but unverified.
- The benchmark reproduction is committed, checksummed and CI-regression-checked
  rather than quoted from a paper.

Which sharpens the mutant finding rather than softening it. This project commits
its benchmark baseline with a checksum and fails CI if it drifts. It applied that
exact discipline to its performance claim and not to its safety claim.

## If it were ever in scope

The mechanism worth borrowing into a memory system is the **read-generation
fence**, and it is the one a version check alone cannot replace. A stalled writer
reclaimed by crash recovery wakes and commits; the artifact's version never
moved, so a compare-and-set passes and the stale write lands. Bumping an
ownership epoch on reclamation, and checking it atomically at commit, closes a
hole that looks closed. Memory systems with background consolidation passes that
can be restarted have exactly this shape and, as far as this atlas has read,
none of them fences.

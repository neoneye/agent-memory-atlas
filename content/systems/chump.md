---
title: "Chump"
eyebrow: "It ablated its own memory and published the null"
description: "A multi-agent fleet coordinator whose memory injection was A/B tested against a bypass flag, found to move task accuracy not at all, and then checked a second way — whether the agent ever textually references the injected state — against a preregistered threshold it also failed, with the write-up left public and thirty-nine others moved to a private repository."
root: ../..
page_kind: system
source_name: "repairman29/chump"
source_url: https://github.com/repairman29/chump
archive_name: "repairman29--chump"
revision: 631fcaa7f56ef6fa567cbc0ea9859d1b4bec4263
revision_url: https://github.com/repairman29/chump/commit/631fcaa7f56ef6fa567cbc0ea9859d1b4bec4263
analyzed_at: 2026-09-16
capabilities: ""
capability_evidence: {}
stack_storage: "sqlite"
stack_retrieval: "lexical, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A row in `chump_memory`: content, timestamp, source, a confidence float, a verified flag, a sensitivity label, an optional expiry and a memory type defaulting to `semantic_fact`"
  storage: "SQLite with an FTS5 virtual table kept in sync by insert, delete and update triggers, plus a separate memory graph"
  retrieval: "FTS5 lexical search and a memory graph, with confidence used as a weight rather than a gate"
  write: "Agent capture plus an opt-in LLM summariser that clusters episodics into a `semantic_fact` marked `verified = 1` and sets `expires_at` on the sources it consumed"
  update_delete: "Confidence decay per day for unverified rows, floored at 0.05 \"so a decayed memory still surfaces in retrieval (just heavily down-weighted) rather than vanishing\"; expiry removes rows the summariser has consumed"
  scoping: "None on the memory row; the fleet coordinates over projects and repos above it"
  integration: "Bring-your-own coding agent — Claude Code, opencode, Codex CLI, Aider, goose or manual commits — with an MCP memory server, a desktop app and a web surface"
  background: "Fleet orchestration, a gap registry, summarisation behind an opt-in flag, and decay passes"
  trust: "A verified flag that exempts a memory from decay, a sensitivity label, per-feature bypass flags for ablation, and a binding research-integrity directive"
  strengths: "It measured its own memory and reported that it did nothing. `CHUMP_BYPASS_SPAWN_LESSONS` was shipped specifically so spawn-time lesson injection could be switched off in a binary A/B, and EVAL-056 records the outcome without softening it: \"n=30/cell binary-mode sweep; NO SIGNAL (CIs fully overlapping)\". It then checked a second, independent way — whether the agent textually references the injected state — and reports that all five null-validated modules fell below a *preregistered* 5% threshold, with neuromodulation, belief state and surprisal at 0% and blackboard and spawn lessons at 1%. The bypass flag is one of a family (`chump_bypass_perception`, `chump_bypass_neuromod`, `chump_bypass_blackboard`), so each cognitive faculty can be switched off and measured. The public methodology directive requires Wilson confidence intervals, an A/A run per series to measure judge variance with a ±0.03 tolerance before results may be cited, and a preregistration file per gap. The decay comment states the design decision rather than leaving it to be inferred: the confidence floor exists so a decayed memory is down-weighted rather than removed"
  risks: "Thirty-nine of the eighty-three eval documents are now stubs reading \"[t]his document has been moved to a private repository\", and the Research Integrity Directive is binding on contributors: \"Do not state magnitudes, model names, or per-eval IDs in public docs, PRs, or external communications.\" The methodology remains public and the results largely do not, so a reader can check how the project measures and not, for most of the corpus, what it measured — the four surviving public write-ups are the exception rather than the sample. The memory itself carries no mechanism the atlas recognises: `confidence` is a continuous weight, `verified` exempts a row from decay rather than filtering a read, decay is floored so nothing is ever withheld, and there is no scope key, validity interval, supersession pointer or mutation record. On its own evidence, the memory faculty is the part of this system least demonstrated to work"
---

## 1. Executive Summary

Chump is "a multi-agent fleet coordinator + gap registry" — dual-licensed AGPL
and Apache, version 0.2.0, 326,308 lines of Rust with 4,071 test functions,
plus TypeScript and Python surfaces. It brings your own coding agent, runs on
your hardware, and is building toward "the coordination + governance layer that
runs a fleet of swappable coding-agent harnesses, with the human at ring-0."

Its memory is a SQLite table with an FTS5 index, a confidence float, a verified
flag, a sensitivity label and an optional expiry. By the atlas's usual
questions it is unremarkable: no scope key, no validity interval, no
supersession, no mutation record, and a `verified` flag that exempts a row from
confidence decay rather than gating any read. No marks.

The reason this report exists is what the project did next.

Chump shipped an environment flag, `CHUMP_BYPASS_SPAWN_LESSONS`, whose only
purpose is to turn its own memory injection off — "[c]ell A = normal (lessons
injected when `CHUMP_LESSONS_AT_SPAWN_N > 0`), Cell B = bypass active (lessons
always empty regardless of spawn-N)" — and ran a thirty-per-cell binary sweep to
find out whether the memory changed task accuracy.

`EVAL-056-memory-ablation.md` records the answer in its status line:

> "COMPLETE — n=30/cell binary-mode sweep; NO SIGNAL (CIs fully overlapping)"

It is not the only one. The flag belongs to a family —
`chump_bypass_perception()`, `chump_bypass_neuromod()`,
`chump_bypass_blackboard()`, `chump_bypass_spawn_lessons()` — so each cognitive
faculty can be switched off and measured, and `EVAL-054-perception-ablation.md`
and `EVAL-058-executive-function-ablation.md` report nulls too.

Then they checked a second way. `REMOVAL-001-addendum-RESEARCH-022.md` records a
mechanism-evidence analysis asking not whether the modules changed outcomes but
whether the agent ever *mentions* the state they inject:

> "All 5 NULL-validated modules show ≤1% reference rate in agent text output.
> `neuromodulation`/`belief_state`/`surprisal_ema` = 0%; `blackboard` and
> `spawn_lessons` = 1%. All below the preregistered 5% mechanistic-support
> threshold."

Two independent lines of evidence — outcome and mechanism — converging on the
same answer, against a threshold declared before the measurement. And the
addendum is careful about what it is allowed to conclude: "This addendum
integrates the new evidence **without** changing which sub-gaps are filed. It
updates rationales, not actions."

An atlas that spends most of its time establishing whether a mechanism does what
a README says should say plainly that this is the rarest thing in the corpus: a
project that built the off-switch for its own headline feature, measured it,
found nothing, and wrote it down.

The counterweight is equally plain. Thirty-nine of the eighty-three eval documents are now
stubs:

> "**This document has been moved to a private repository.** Per-eval result
> writeups, ablation tables, and judge-specific deltas are tracked in
> `chump-proprietary` (private, need-to-know)."

And the Research Integrity Directive, which is binding on "Claude Code, Cursor,
Chump-orchestrator, and any other automated or human contributor", instructs:
"Do not state magnitudes, model names, or per-eval IDs in public docs, PRs, or
external communications."

The methodology stayed public — Wilson intervals, A/A controls, preregistration,
judge composition rules. The results mostly did not. So a reader can audit how
this project measures and, for most of its corpus, not what it found. The four
surviving nulls are what the migration left behind rather than a representative
sample, and it would be wrong to read them as either the whole story or as
evidence the private half is worse.

## 2. Mental Model

A **memory** is a row with a confidence that decays unless it is verified.

A **verified** memory is an anchor: the summariser's output, exempt from decay,
and the episodics that produced it are expired.

A **bypass flag** is how a faculty is switched off so its absence can be
measured.

A **preregistration** is a file declaring what will count as an effect, written
before the run.

```mermaid
%% caption: the memory path is conventional and its own ablation found no outcome effect; a second, mechanism-level check against a preregistered threshold agreed, and most result write-ups have since moved private
flowchart TB
    CAP["agent capture"] --> M[("chump_memory: content · ts · source ·<br/>confidence · verified · sensitivity ·<br/>expires_at · memory_type")]
    M --> FTS["FTS5, kept in sync by<br/>insert / delete / update triggers"]
    SUM["opt-in LLM summariser<br/>(CHUMP_MEMORY_LLM_SUMMARIZE=1)"] -->|"clusters episodics into a<br/>semantic_fact, verified = 1"| M
    SUM -->|"sets expires_at on the<br/>episodics it consumed"| EXP["expire_stale_memories"]
    DEC["decay: confidence × rate/day<br/>WHERE verified = 0"] --> FLOOR["floor 0.05 — 'so a decayed memory<br/>still surfaces in retrieval (just heavily<br/>down-weighted) rather than vanishing'"]
    M --> INJ["spawn-time lesson injection<br/>(CHUMP_LESSONS_AT_SPAWN_N)"]
    INJ --> AGENT["the coding agent"]
    BYP["CHUMP_BYPASS_SPAWN_LESSONS —<br/>one of a family with<br/>bypass_perception · bypass_neuromod ·<br/>bypass_blackboard"] -.->|"Cell B: lessons always empty"| INJ
    BYP --> E1["EVAL-056, n=30/cell:<br/>NO SIGNAL (CIs fully overlapping)"]
    E1 --> E2["RESEARCH-022 mechanism check:<br/>does the agent TEXTUALLY reference<br/>the injected state?"]
    E2 --> RES["all 5 null-validated modules ≤1%;<br/>neuromod / belief_state / surprisal = 0%;<br/>blackboard and spawn_lessons = 1% —<br/>below the PREREGISTERED 5% threshold"]
    METH["public: Wilson CIs · an A/A run per<br/>series within ±0.03 before citing ·<br/>preregistration per gap"] -.-> E1
    PRIV["39 eval docs now read<br/>'moved to a private repository';<br/>directive: do not state magnitudes,<br/>model names or per-eval IDs publicly"] -.-> RES
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `crates/chump-memory-db/src/memory_db.rs` | The table, the triggers, decay, expiry and the summariser |
| `src/memory_graph.rs`, `memory_graph_tool.rs` | The graph beside the FTS index |
| `crates/mcp-servers/chump-mcp-memory` | The MCP surface |
| `src/env_flags.rs` | The four bypass flags |
| `docs/eval/` | 83 documents, 39 of them now private stubs |
| `docs/process/RESEARCH_INTEGRITY.md` | The binding methodology directive |
| `docs/architecture/MEMORY_GRAPH_VS_FTS5.md`, `docs/strategy/AGENT_MEMORY_TIERS.md` | The design arguments |

## 4. Essential Implementation Paths

`docs/eval/EVAL-056-memory-ablation.md` — the flag, the cells, the result.

`docs/eval/REMOVAL-001-addendum-RESEARCH-022.md` — the mechanism evidence, and
the sentence limiting what it changes.

`docs/process/RESEARCH_INTEGRITY.md` — the methodology, and the disclosure
policy.

`crates/chump-memory-db/src/memory_db.rs:276-300` — decay, and the comment
explaining the floor.

## 5. Memory Data Model

One table. `content`, `ts`, `source`, `confidence` defaulting to 1.0,
`verified` defaulting to 0, `sensitivity` defaulting to `'internal'`,
`expires_at`, and `memory_type` defaulting to `'semantic_fact'`, with an FTS5
mirror maintained by all three triggers — insert, delete and update — which is
the complete set and more than many projects manage.

`verified` is the only discrete field that does anything, and what it does is
exempt a row from decay. The doc comment is precise about the rest: "Verified
memories (verified >= 1) are anchors — untouched. Confidence floor is 0.05 so a
decayed memory still surfaces in retrieval (just heavily down-weighted) rather
than vanishing."

That last clause is why no trust mark is claimed. Nothing here withholds a
memory from a reader on the basis of a status; an old unverified memory is
ranked lower and still returned. `confidence` is a continuous weight, which the
atlas does not count, and there is no scope key, validity interval, supersession
pointer or record of mutations.

## 6. Retrieval Mechanics

FTS5 plus a memory graph, with a design document comparing the two. Confidence
weights rather than gates.

## 7. Write Mechanics

Agent capture, plus an opt-in summariser gated on
`CHUMP_MEMORY_LLM_SUMMARIZE=1` — "the opt-in gate MEM-003 calls out" — that
clusters episodic rows, writes a `semantic_fact` with `verified = 1`, and sets
`expires_at` on the sources it consumed so the next expiry pass removes them.

Consolidation that deletes its inputs is a real choice and worth noting: the
episodics are gone, so the semantic fact is the only remaining account of them,
and its provenance is whatever the summariser wrote into `source`.

## 8. Agent Integration

Bring-your-own agent across Claude Code, opencode, Codex CLI, Aider, goose or
manual commits, with an MCP memory server, a desktop app and a web surface. The
fleet coordination and the gap registry are the product; memory is a faculty
inside it, which is the framing under which it was ablated.

## 9. Reliability, Safety, and Trust

The methodology directive is the artifact to read, and it is unusually
demanding. Every eval series must include an A/A run — the same cell against
itself — to measure judge variance, and "A/A delta should be within ±0.03 before
results are cited". Preregistrations live at
`docs/eval/preregistered/<gid>.md` and must declare judge composition in
advance. Wilson confidence intervals rather than raw proportions.

Those are the controls a reader would ask for, and they were in place before the
nulls were found, which is what makes the nulls credible rather than merely
modest.

The disclosure policy is the other half and deserves to be stated without
editorialising. Moving per-eval results, ablation tables and model-tier deltas
into a private companion repository is a legitimate commercial decision. Its
effect on a reader is specific: the public tree now documents a method and four
outcomes, and directs contributors not to state magnitudes publicly. Anyone
citing Chump's cognitive-architecture findings from the public repository is
citing the method and the four survivors.

## 10. Tests, Evals, and Benchmarks

4,071 test functions, an `e2e` tree, and 83 eval documents of which 44 still
carry content.

The evaluation apparatus is the strongest part of this project and the memory is
not. Both statements come from the same source, which is the point.

## 11. For Your Own Build

Build the off-switch. A feature you cannot disable is a feature you cannot
measure, and `CHUMP_BYPASS_SPAWN_LESSONS` existing at all is what made the
question answerable. One environment flag per faculty, read in one place, wired
at the single injection point.

Measure mechanism as well as outcome. "Did accuracy change?" and "does the agent
ever refer to what we injected?" are different questions with different failure
modes, and a feature that fails both has failed in a way a single metric cannot
argue with. Declare the threshold first — the 5% here was preregistered, so the
result could not be re-framed afterwards.

Run an A/A control. Comparing a cell against itself measures the judge, and a
series whose A/A delta exceeds the tolerance has not earned the right to report
an A/B.

And publish the null. Almost every memory system in this corpus asserts that its
memory helps. Exactly one has tested that claim against a bypass and written
down that it did not, and the value of that write-up to everyone else is larger
than the feature would have been.

## 12. Open Questions

What happened to the five null-validated modules. `REMOVAL-001` names a decision
matrix; the matrix is now private, so whether the code was removed, kept or
reworked is not answerable from the public tree.

Whether the memory faculty has been re-evaluated since April 2026. The public
ablation is from `2026-04-20`; the repository is active five months later.

Whether the nulls generalise past this harness. A spawn-time lesson injection
that nothing references may say more about the injection point than about memory
in coding agents, and the write-up does not claim otherwise.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `docs/eval/EVAL-056-memory-ablation.md` | An ablation of the project's own memory, and its null |
| `docs/eval/REMOVAL-001-addendum-RESEARCH-022.md` | Mechanism evidence against a preregistered threshold |
| `docs/process/RESEARCH_INTEGRITY.md` | A/A controls, Wilson intervals, and the disclosure policy |
| `src/env_flags.rs:225-300` | Four faculties, four off-switches |
| `crates/chump-memory-db/src/memory_db.rs:74-96` | The table and its complete trigger set |
| `crates/chump-memory-db/src/memory_db.rs:276-300` | Decay, and the floor that keeps a memory retrievable |

## History

**2026-09-16** — [`631fcaa7f56ef6fa567cbc0ea9859d1b4bec4263`](https://github.com/repairman29/chump/commit/631fcaa7f56ef6fa567cbc0ea9859d1b4bec4263) — first reading, at a commit dated 15 September 2026. Dual-licensed AGPL-3.0 and Apache-2.0. Thirty-nine of the eighty-three documents under `docs/eval/` are stubs recording that the content moved to a private repository; the figures quoted here come from the write-ups that remain public. Screened before opening, from a shallow clone: eighty-eight files scanned, three auto-run surfaces, two build-time execution points, six unpinned surfaces and sixty-nine dependency files inside the seven-day cooldown, with `CLAUDE.md` and `AGENTS.md` read as data. Nothing was installed, built or run.

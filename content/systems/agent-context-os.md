---
title: "Context OS"
eyebrow: "Git-backed context layer"
description: "A file convention for coding agents with a Python kernel behind it: state files whose updates are applied as one atomic transaction, a decisions table only ever appended to, and a continuity benchmark whose scorer is guarded by its own negative controls."
root: ../..
page_kind: system
source_name: "conorbronsdon/agent-context-os"
source_url: https://github.com/conorbronsdon/agent-context-os
archive_name: "conorbronsdon--agent-context-os"
revision: 15b5acace6830e4cac58e56cf1a102ea6557e762
revision_url: https://github.com/conorbronsdon/agent-context-os/commit/15b5acace6830e4cac58e56cf1a102ea6557e762
analyzed_at: 2026-09-19
capabilities: "audit_log, negative_eval"
stack_storage: "files"
stack_retrieval: ""
stack_source: "reviewed"
capability_evidence:
  audit_log: "two append-only records with writers in the kernel rather than instructions in a template, applied as one transaction | contextos/kernel.py:1339-1355, :1440-1457, :115, :124, state/decisions.md:1-9, tests/test_agent_lifecycle_transactions.py | `state/decisions.md` opens by declaring itself an append-only log, one table row per decision with a *Rejected alternatives* column for what lost and why, and the kernel writes it that way: the update path reads the existing text, strips the trailing newline and concatenates a new table row carrying the date, the decision, its rationale and the rejected alternatives, so nothing earlier is rewritten. It refuses to write at all when the file is absent — *decision log does not exist* — rather than creating a fresh one, so a decision cannot be recorded into a log that lost its history. Beside it `state/current-log.md` is a dated update log: when `current.md` is advanced and its previous `Last Updated` date is neither today nor the newest date already logged, that date is inserted directly under the required heading, newest-first, and a missing heading is an error rather than something to recreate. Both writes go into a `pending` map applied together — the kernel advertises `atomic-replacement-and-rollback` among its capabilities, and a lifecycle-transaction suite covers it | what is recorded is the decision and the date it changed, not who asked or which agent wrote it; the actor is whoever holds the checkout, and Git is where that is answered"
  negative_eval: "a benchmark whose scorer is itself guarded against every way it could pass vacuously | scripts/continuity-benchmark.py:16-70, tests/test_continuity_benchmark.py:26-50, tests/fixtures/continuity/scenario.json, docs/continuity-benchmark.md | the continuity benchmark scores four questions over a synthetic project — a remembered database choice, an export plan that replaced an earlier one, a rejected retry policy with its reason, and a launch date whose correct answer is *unconfirmed* — and an answer counts only when the value matches, the source matches, the expected sentence is inside the quote given, and that quote actually occurs in that source. The four tests around it close the gaps: `test_each_wrong_decision_or_invented_certainty_fails` mutates each answer in turn, including claiming the launch date is confirmed, and requires the score to drop by exactly one each time; `test_correct_guess_without_support_fails` keeps the right value, replaces the quote with an unsupported sentence, and requires it to fail, then requires the same answers to score zero under the profile whose sources are absent; and `test_prompt_does_not_leak_answer_key_or_unselected_sources` requires the prompt to contain neither the expected block nor the other profile's source names | the comparison is built to be hard on itself: the `handoff` baseline is information-equivalent, carrying all four facts in one note, and the `contextos` profile is given an older session holding superseded ideas, so the layer has to beat a baseline that already knows the answers while resisting material that is out of date"
matrix:
  memory_unit: "A Markdown file in a named place — `state/current.md`, `state/decisions.md`, `state/blockers.md`, `state/weekly-priorities.md`, a dated file under `sessions/`, a project folder, a skill — each carrying a `**Last Updated:**` line the kernel parses"
  storage: "The Git repository itself: templates and conventions in the tree, with a `contextos` Python kernel that reads and rewrites them under an atomic-replacement-and-rollback transaction"
  retrieval: "A routing table the agent reads — `ROUTING.md` maps a task kind to the files to load — plus read-only, source-attributed continuity views over the state files, and a `/start` command that resumes today's session file or falls back to the most recent one"
  write: "Slash commands and a CLI: a session loop of `/start`, `/update`, `/end`, with state advanced through a proposal the kernel validates before applying every changed file together"
  update_delete: "State files are rewritten in place with their `Last Updated` line advanced and the previous date pushed onto a newest-first log; the decisions table is appended to and never rewritten"
  scoping: "Directories — `projects/`, `workspace/`, `references/`, `writing/` — with path guards on the kernel's local-state access, and a claim system with leases so two agents do not take the same task"
  integration: "First-class Claude Code, Codex, OpenClaw and OpenCode, with experimental Cursor, Devin and Hermes adapters; hooks in shell, PowerShell and Python, installable bundles with a lockfile, and a component manifest"
  background: "None that runs on its own — the passes are checks a person or CI invokes: link and doc reachability, SSOT controls exercised in disposable copies, bundle locks, component manifests and the continuity benchmark"
  trust: "A five-value freshness status — missing, unknown, future, stale, fresh — derived by comparing each state file's `Last Updated` line against a threshold, reported as a diagnostic; only `current.md` gates readiness, and the gate admits both fresh and stale"
  strengths: "A benchmark whose baseline is deliberately information-equivalent and whose harder profile carries superseded material, scored on quotes that must occur in the cited file; a decisions writer that refuses to create the log it is meant to append to; and a readiness gate narrowed to one file with the reason written down — requiring a real date on all three would report an initialized workspace as needing setup forever"
  risks: "The freshness status is derived from a self-reported `Last Updated` line, so a file edited without touching that line reads as fresh; the append-only property of the decisions table is enforced by the kernel's writer but nothing stops an agent editing the Markdown directly, which is what makes the Git history the real control; and no benchmark result is committed — the harness prepares prompts a reader must run against their own model"
---

## 1. Executive Summary

Context OS is a convention with a kernel under it. The convention is a set of
Markdown files in known places — `state/current.md` for what is happening now,
`state/decisions.md` for what was decided and what was rejected,
`state/blockers.md`, `sessions/` for per-day notes, `projects/` and
`references/` for the rest — plus a `ROUTING.md` that tells an agent which of
them to read for which kind of task. The kernel is a Python package,
`contextos`, that reads and rewrites those files, validates a proposal before
applying it, and applies every changed file together.

It earns two marks. `audit_log`, because two of those files are genuinely
append-only in code rather than by instruction: the decisions table gains a row
and loses nothing, and the update log gains a date at the top when `current.md`
rolls over. `negative_eval`, because of the continuity benchmark, whose design is the
reason to read this repository at all.

That benchmark is the thing to take away. It scores four questions about a
synthetic project across three context profiles, and the comparison is
constructed to be hard on the system under test. The `handoff` baseline is
**information-equivalent** — a single note containing all four answers. The
`contextos` profile is made *harder*, not easier, by including an older session
full of superseded ideas. An answer scores only if the quote it cites actually
occurs in the file it cites. And the scorer has its own negative controls: a
right answer with an unsupported quote must fail, each wrong answer must cost
exactly one point, and the prompt must not leak the key.

## 2. Mental Model

Think of three layers that happen to be the same directory.

**The files** are what an agent reads: state, sessions, projects, references,
skills. They are Markdown with a `**Last Updated:**` line, and they are
templates in the shipped repository — `state/current.md` arrives with
`[Most important thing right now]` in it.

**The kernel** is what keeps them honest. It parses the dates, computes a
freshness status, guards the paths it will touch, validates a proposed change,
and applies all of the resulting file writes as one transaction with rollback.

**The harness adapters** are how an agent reaches both. Hooks in shell,
PowerShell and Python; bundles with a lockfile; first-class support for four
coding agents and experimental adapters for three more.

## 3. Architecture

```mermaid
%% caption: an agent reads a routing table that maps a task kind to the files to load, and works against Markdown state under a Git checkout; the contextos kernel parses each file's Last Updated line into a five-value freshness status, guards the paths it will touch, validates a proposed change, and applies every resulting write as one atomic transaction — appending a row to the decisions table and pushing the previous date onto a newest-first update log — while a continuity benchmark scores four grounded questions across an instructions baseline, an information-equivalent handoff note, and the full layer with superseded material in it
flowchart TD
    subgraph Agent
        ROUTE["ROUTING.md<br/>task kind -> files to load"]
        CMD["/start · /update · /end<br/>slash commands and hooks"]
    end

    subgraph Files["Git checkout"]
        CUR["state/current.md"]
        DEC["state/decisions.md<br/>append-only table"]
        LOG["state/current-log.md<br/>newest-first dates"]
        BLK["state/blockers.md"]
        SES["sessions/YYYY-MM-DD.md"]
        PRJ["projects/ · references/ · skills/"]
    end

    subgraph Kernel["contextos"]
        FRESH["freshness<br/>missing · unknown · future · stale · fresh"]
        GUARD["path guards<br/>local-state access"]
        VAL["validate proposal"]
        TX["pending map<br/>atomic replacement + rollback"]
        CLAIM["claims with leases<br/>stale claims lose their place"]
    end

    subgraph Eval["continuity benchmark"]
        P1["instructions<br/>no project facts"]
        P2["handoff<br/>all four facts"]
        P3["contextos<br/>+ superseded session"]
        SCORE["grounded_correct<br/>quote must occur in the cited source"]
    end

    ROUTE --> Files
    CMD --> VAL --> TX
    TX --> CUR
    TX --> DEC
    TX --> LOG
    CUR --> FRESH
    BLK --> FRESH
    GUARD --> Files
    CLAIM --> PRJ
    Files --> P3
    P1 --> SCORE
    P2 --> SCORE
    P3 --> SCORE
```

## 4. Essential Implementation Paths

- **Kernel:** `contextos/kernel.py` — freshness, path guards, proposal
  validation, the pending-write transaction, the decisions and log writers.
- **Continuity views:** `contextos/continuity.py` — read-only,
  source-attributed views over the state files.
- **Coordination:** `contextos/coordination.py` — claims, leases, and the
  ordering that drops stale ones.
- **Benchmark:** `scripts/continuity-benchmark.py`,
  `tests/fixtures/continuity/scenario.json`,
  `tests/test_continuity_benchmark.py`, `docs/continuity-benchmark.md`.
- **Conventions:** `state/`, `sessions/README.md`, `ROUTING.md`.
- **Adapters and hooks:** `adapters/`, `scripts/context-os-hook.{sh,ps1,py}`.

## 5. Memory Data Model

There is no record type — the unit is a file in a known place, and the schema
is a heading convention. Two of them carry structure worth naming.

`state/decisions.md` is a table with four columns — Date, Decision, Context /
rationale, Rejected alternatives — and its header states both the append rule
and when to fill the fourth column: *"when there was a real branch point — what
else was considered and why it lost; leave it blank when there was one obvious
option."* That is a store that keeps the road not taken, which most decision
logs do not.

`state/current-log.md` holds dates under a required heading, newest first. It
does not hold the old content — only the date `current.md` last changed before
the one it now carries.

Every state file is expected to carry a `**Last Updated:**` line, and that line
is the only input to the freshness status.

## 6. Retrieval Mechanics

Retrieval is a routing table plus a convention. `ROUTING.md` maps a kind of
task to the files to load — writing tasks read a writing skill, project tasks
read that project's folder — and the session loop gives the agent a starting
point: `/start` looks for a file matching today's date and resumes it, or reads
the most recent one for continuity.

The kernel's contribution is `continuity.py`, described in its own first line
as *"read-only, source-attributed continuity views over existing kernel
evidence"* — the views carry where each fact came from, which is what the
benchmark then scores against.

## 7. Write Mechanics

A change is a proposal. The kernel validates it, then assembles every file it
will touch into a `pending` map and applies them together; the capability list
names `atomic-replacement-and-rollback`, and `test_agent_lifecycle_transactions.py`
covers the lifecycle.

Two writes in that map are append-only by construction:

- **Decisions.** The kernel reads the existing file, strips its trailing
  newline, and concatenates a new row. If the file does not exist it raises —
  *decision log does not exist* — rather than creating one, so a decision
  cannot be appended into a log that has lost its history.
- **The update log.** When `current.md` is advanced and its previous date is
  neither today nor the newest date already recorded, that date is spliced in
  directly beneath the required heading. A missing heading is an error, not
  something to recreate.

## 8. Agent Integration

Claude Code, Codex, OpenClaw and OpenCode are first-class; Cursor, Devin and
Hermes adapters are marked experimental in the README. Hooks ship in three
languages so the same layer attaches to a POSIX shell, PowerShell or a Python
harness. Bundles are installable with a lockfile and a component manifest, and
the repository carries a script that exercises its own single-source-of-truth
locators in disposable copies rather than in the working tree.

Coordination for multiple agents is a claim with a lease: `_claim_order` groups
live claims by task and drops the ones whose lease has expired, so a stale
holder loses its place rather than blocking the queue forever.

## 9. Reliability, Safety, and Trust

**Audit log — awarded.** Two append-only records, both with writers in the
kernel, both applied inside the transaction, and one of them refusing to create
the file it appends to. What they do not record is an actor: the row carries a
date and a decision, not who proposed it. In a Git-backed layer that answer
lives in the commit, which is a reasonable division — but a reader should know
the log alone does not carry it.

**Negative eval — awarded**, and the evidence record quotes the four tests. The
design decision that earns it is the information-equivalent baseline: the
`handoff` profile is a note containing all four answers, so the benchmark
cannot be won by comparing the layer against an agent that simply does not know
anything.

**Trust state — withheld.** The freshness status is five values —
`missing`, `unknown`, `future`, `stale`, `fresh` — and every one of them is
*derived* at read time from a `Last Updated` line rather than stored, which the
atlas does not award. Its only gate admits both `fresh` and `stale`, and the
docstring explains why: requiring a real date on `weekly-priorities.md` and
`blockers.md` as well *"would report an initialized workspace as needing setup
forever"*, because users legitimately leave those at the template. That is a
sensible narrowing of a diagnostic, and it is not a state that withholds a
memory.

**Tombstone — withheld.** A superseded decision stays as a row and the
replacement is a later row; nothing marks the first as retired, and the
benchmark scenario shows the intended reading is prose — *"The CSV export
replaces the earlier PDF export plan."*

**Scope enforced — withheld.** Directories partition content and the kernel
guards the paths it will write, but nothing filters a read by a scope key; the
claim leases are about two agents not taking the same task, not about what
either may see.

**Bitemporal, human review — withheld.** One date per file, and no approval
state.

## 10. Tests, Evals, and Benchmarks

**No paper.** Searched the README and `docs/` for `arxiv`, `@article`,
`@misc`, `doi.org` and `CITATION.cff`: none.

Thirty Python test files, plus shell suites for hooks and portability. The ones
that matter here are the benchmark's, and section 9's evidence record quotes
them; what belongs in this section is the benchmark's own honesty about its
limits.

The doc states the method plainly: *"It tests observable answers with
supporting sentences, rather than asking another model for a subjective
grade."* Every result object carries a `scope` field saying what the number is
not — *"Four constrained decisions with exact supporting sentences; not a
general semantic-quality or live handoff score"* — and a `context_characters`
count, so the cost of each profile sits beside its score.

**No result is committed.** The harness prepares three prompts and the doc asks
the reader to submit each to a fresh session of the same model with tools
disabled, keeping the answer key out of the transcript. So this is a
reproducible method with no reproduced number in the tree, which is the honest
state for an offline benchmark that needs a model the repository cannot ship —
and the doc also notes that selected release bundles omit the script and
fixtures, so the benchmark is a source-checkout activity.

## 11. For Your Own Build

- **Make your baseline information-equivalent.** A context layer that beats an
  agent with no facts has proved nothing. Give the baseline all the answers in
  one note and see whether the structure still helps.
- **Make the harder profile harder.** Putting a superseded idea in the full
  profile tests the thing that actually breaks in production — picking the
  current decision over the stale one.
- **Score the quote, not the answer.** Requiring the cited sentence to occur in
  the cited file turns a benchmark from a trivia check into a grounding check,
  and it is four lines of code.
- **Test your scorer.** Mutate each answer and require the score to drop by
  exactly one; keep a right answer with a wrong quote and require it to fail.
  A grader nobody grades is the same failure as a test that cannot fail.
- **Refuse to create the log you append to.** Raising when `decisions.md` is
  missing, instead of writing a fresh one, is the difference between a gap you
  notice and a history that quietly restarts.
- **Narrow a nag to what it can justify.** Gating readiness on one file, with
  the reason recorded, beats three files' worth of false positives.

## 12. Open Questions

- Freshness reads a self-reported `Last Updated` line. Is there a check that
  the line matches the file's actual last change, or is a stale line
  indistinguishable from a fresh file?
- The decisions table is append-only in the kernel's writer, and an agent with
  a text editor is not obliged to use it. Does any check compare the working
  tree against the Git history for rewritten rows?
- The continuity benchmark asks a reader to run three prompts by hand. Is there
  a recorded run anywhere — a blog post, a release note — whose numbers a reader
  could compare their own against?

## Appendix: File Index

- Kernel: `contextos/kernel.py`
- Continuity views: `contextos/continuity.py`
- Coordination and claims: `contextos/coordination.py`
- CLI: `contextos/cli.py`, `contextos/__main__.py`
- Benchmark: `scripts/continuity-benchmark.py`,
  `docs/continuity-benchmark.md`, `tests/fixtures/continuity/scenario.json`
- Conventions: `ROUTING.md`, `state/`, `sessions/README.md`
- Checks: `scripts/check-ssot-controls.py`, `scripts/check-doc-reachability.sh`,
  `scripts/check-links.sh`, `scripts/component-manifests.py`
- Adapters and hooks: `adapters/`, `scripts/context-os-hook.{sh,ps1,py}`

## History

**2026-09-19** — [`15b5acace6830e4cac58e56cf1a102ea6557e762`](https://github.com/conorbronsdon/agent-context-os/commit/15b5acace6830e4cac58e56cf1a102ea6557e762) — first reading, at the head of `main`. Screened with `scripts/screen_repo.py` before anything was read: three auto-run surfaces and an instruction file addressed to a reading agent, which was read as data; nothing was installed, built or run. Two marks. The reading covered the state-file conventions and their templates, the kernel's freshness computation and path guards, the proposal validation and the pending-write transaction, the decisions and update-log writers, the claim-and-lease coordination, the routing table and session loop, and the continuity benchmark together with the tests that guard its scorer; the bundle, component-manifest and adapter machinery was read as context rather than as subject. MIT. Four marks are withheld with reasons in section 9 — the freshness status is derived rather than stored, a superseded decision is a later row rather than a marked one, directories partition without a read predicate, and there is no approval state. The benchmark is the reason to read this repository: an information-equivalent baseline, a harder full profile seeded with superseded material, scoring that requires the cited quote to occur in the cited file, and four tests that keep the scorer honest.

---
title: "DiffMem"
eyebrow: "A whitelisted shell for the memory repo"
description: "The retrieval agent explores memory with grep, git log and git blame behind a thirteen-command allowlist that validates every segment of a chain — and then hands the string to a shell."
root: ../..
page_kind: system
source_name: "growth-kinetics/diffmem"
source_url: https://github.com/growth-kinetics/diffmem
revision: 5f00e8d22dc05fb1fc505f5322cb717de61bed3f
revision_url: https://github.com/growth-kinetics/diffmem/commit/5f00e8d22dc05fb1fc505f5322cb717de61bed3f
analyzed_at: 2026-08-09
capabilities: ""
stack_storage: "files"
stack_retrieval: "lexical"
stack_source: "seeded"
matrix:
  memory_unit: "A markdown entity file holding the current view, with history in the commit graph"
  storage: "A git repository of markdown; no vector store, no embeddings, no BM25"
  retrieval: "An LLM issuing whitelisted shell commands — grep, git log, git diff, git blame"
  write: "A writer agent edits the current-state files; a consolidator merges and redistributes"
  update_delete: "Editing the current view; the prior state stays reachable through git history"
  scoping: "One repository per memory store; pluggable personal and corporate ontologies"
  integration: "A server, a Docker deployment, and a pluggable executor with a Hatchet backend"
  background: "Consolidation with dedupe, linking, reabsorption and redistribution, under a lock"
  trust: "Nothing — files are files, and git records who changed what"
  strengths: "Retrieval as repository exploration, with the git subcommands separately allowlisted"
  risks: "The validated command string is executed with shell=True and nothing blocks substitution"
---

## 1. Executive Summary

DiffMem is a memory backend with no index: markdown files in a git repository,
and an LLM that explores them with shell commands. "No vector databases, no
embeddings, no BM25 — just git and an LLM."

**The architectural idea is a real one.** Memory files hold only the *current*
view — "current relationships, facts, or timelines" — so the surface a query
scans stays small, and every prior state lives in the commit graph, reachable
on demand:

> "Git diffs and logs provide a natural way to track how memories evolve. Agents
> can ask 'How has this fact changed over time?' without scanning entire
> histories, pulling only relevant commits."

That is the log-and-projection pattern with git supplying the log for free, and
it answers a question most systems here cannot: not *what do you believe* but
*when did that change, and to what*. `git blame` on a memory file is provenance
per line, at no storage cost.

**The mechanism worth studying is `command_router.py`** — a sandbox for handing
an LLM a shell over the memory repo. Thirteen commands are allowed
(`cat`, `head`, `tail`, `grep`, `ls`, `wc`, `awk`, `sed`, `cut`, `sort`, `uniq`,
`find`, `git`), `git` carries a **second** allowlist of read-only subcommands
(`log`, `diff`, `blame`, `show`, `rev-list`, `shortlog`), the validator takes
`Path(tokens[0]).name` so a path-prefixed binary cannot slip through, and the
splitters for `|` and for `&&`/`||`/`;` are quote- and escape-aware so a pipe
inside a grep pattern is not a pipe. **Every segment of every chain is
validated**, not just the first.

Giving `git` its own subcommand allowlist is the detail that shows the author
thought about it: `git` unrestricted is a write primitive and a network client.

**And then the validated string is executed with `shell=True`** — section 9.

## 2. Mental Model

Entity files hold the present. Git holds the past. A retrieval agent reads the
present with `grep` and reaches into the past with `git log` and `git diff` when
a question needs it. A writer agent edits; a consolidator reorganises.

```mermaid
flowchart TD
    Q["question"] --> RA["retrieval agent"]
    RA --> CR{"command_router.run(command)"}
    CR --> SPL["split chain on ; && ||, quote-aware<br/>then split each pipeline on |, quote-aware"]
    SPL --> VAL{"every segment: base command in the 13?<br/>git subcommand in the 6?"}
    VAL -->|no| ERR["[error] unknown command, with the list"]
    VAL -->|yes| SH["subprocess.run(pipeline_str, shell=True)"]
    SH --> PRES["presentation layer: text check,<br/>elapsed ms, return code"]
    PRES --> RA
    CUR["current-state markdown — the 'now' view"] --> SH
    HIST["git commit graph — every prior state"] --> SH
    W["conversation"] --> WA["writer agent"]
    WA --> CUR
    WA --> CMT["commit — the differential is the history"]
    CON["consolidator: dedupe, link,<br/>reabsorb, redistribute"] --> CUR
    ONT["ontology: personal | corporate"] --> WA
    ONT --> CON
```

## 3. Architecture

`src/diffmem/` holds `retrieval_agent` (agent, baseline, `command_router`,
`resolver`, prompts), `writer_agent`, `consolidator_agent`, `executor`,
`storage`, `ontology`, `ontologies`, `repo_manager`, `frontmatter`,
`conformance`, `api`, `server`, `status`.

**The executor is pluggable** — `TaskExecutor` as an abstract base with an
`InlineExecutor` and a `HatchetExecutor`, a `JobHandle` receipt, a `JobResult`
with status and timestamps, and a `build_executor` factory reading an env var.
The design note is the good part: "Endpoints construct a thunk
(`Callable[[], dict]`) that closes over the actual writer/consolidator call and
hand it to `submit_write` / `submit_consolidate` — keeping the executor decoupled
from DiffMemory internals." Write and consolidate become jobs you can run inline
in development and on a queue in production without the memory code knowing.

**Ontologies are pluggable** — `personal` and `corporate` ship as separate
directories, so what counts as an entity and which fields it carries is
configuration rather than code. There is a `conformance.py` beside them.

14,800 lines of Python, 22 test files.

## 4. Essential Implementation Paths

**Sandbox** — `src/diffmem/retrieval_agent/command_router.py`
(`WHITELISTED_COMMANDS` `:22-26`, `_validate_command` `:87-106`,
`_split_pipeline` `:108`, `_split_chain` `:141`, `_execute_pipeline` `:221-265`).

**Retrieve** — `src/diffmem/retrieval_agent/agent.py`, `resolver.py`,
`baseline.py`, `prompts/`.

**Write and consolidate** — `src/diffmem/writer_agent/`,
`src/diffmem/consolidator_agent/`, `src/diffmem/repo_manager.py`.

**Schedule** — `src/diffmem/executor/{base,factory,inline,hatchet,jobstore}.py`.

## 5. Memory Data Model

Markdown with frontmatter, one file per entity, under a pluggable ontology.
The file is the current state; the commit graph is the history.

There is no status field, no confidence, no supersession pointer and no
tombstone — by design, because git carries the succession. A superseded fact is
the previous revision of a line, and `git log -p` on the file is the belief
history. That is elegant and it has one consequence worth stating: **nothing on
the read path knows a fact was recently corrected**, because the retrieval agent
greps the current file. History is available on demand and not consulted by
default, so the agent sees the corrected value with no signal that it changed
at all, unless it thinks to ask.

The roadmap names the model's own failure mode, which is the kind of disclosure
this atlas records:

> "Sometimes an entity will become a catch-all and the thing will insist in
> overloading it."

Entity resolution collapsing everything into one popular node is a real and
common failure, and it is on the public roadmap rather than in an issue nobody
reads.

## 6. Retrieval Mechanics

An LLM writes shell commands. `grep` finds the current view; `git log`,
`git diff`, `git blame` and `git show` reach into history; `awk`, `cut`, `sort`,
`uniq` and `wc` shape the output. The router describes a "two-layer
execution/presentation architecture inspired by the Manus/*nix agent pattern",
and the presentation layer adds a binary-content check, elapsed milliseconds and
the return code, so the model sees a bounded, labelled result rather than raw
bytes.

The advantages are real: no index to build or keep in sync, no embedding cost, no
staleness between the store and its index, and a query language the model already
knows. The cost is that recall depends on the model choosing good patterns —
there is no semantic fallback when the right memory uses different words.

`baseline.py` beside `agent.py` suggests a non-agentic comparison path; no
results comparing them were found.

**Scope is the repository.** One store per memory set; no scope key reaches a
query.

## 7. Write Mechanics

A writer agent edits the current-state files and commits; the commit *is* the
differential. A consolidator agent runs dedupe, linking, reabsorption and
redistribution — the test names are `test_consolidator_dedupe`,
`test_consolidator_link`, `test_consolidator_reabsorb`,
`test_consolidator_redistribute`, `test_consolidator_lock` — so the
reorganisation is decomposed into named, individually tested passes, and it takes
a lock.

## 8. Agent Integration

A server, an HTTP API, Docker and a deploy directory, with the executor
abstraction allowing the write and consolidate paths to run on Hatchet.

The README names a production deployment — Annabelle, "a simulated intelligence
that maintains persistent memory across thousands of conversations on WhatsApp
and Messenger" — and links a companion repository showing DiffMem processing a
novel chapter by chapter, which is a good way to let a reader see the output
shape without running anything.

## 9. Reliability, Safety, and Trust

**No marks.** No trust state, no tombstone, no bitemporality as a queryable
model, no scope key, no review surface, no committed exclusion case.

**Audit log — withheld, and DiffMem is the purest case of the exclusion.** The
mark requires "a named append-only event record of memory mutations in the
system's own store" and explicitly does not count git history. Here git history
*is* the design, and it genuinely provides what an audit trail provides —
`git blame` gives per-line authorship and time, `git log -p` gives every prior
value. A reader should take the withheld mark as a definitional boundary rather
than a criticism: this system has better memory-change provenance than several
that carry the mark.

**The sandbox has one gap, and it is the one this design shape always has.**

Validation tokenises with `shlex.split` and checks the base command of every
segment. Execution then does:

```python
result = subprocess.run(cmd_str, shell=True, ...)
```

on the original pipeline string. So the validator's model of the command and the
shell's model of it are different parsers, and anything the validator treats as
an *argument* the shell may treat as *syntax*. Nothing in the router rejects
command substitution — `$(…)` and backticks — or output redirection, and neither
appears in the whitelist logic. A command whose base token is `grep` passes
validation with an argument the shell will expand before `grep` ever runs.

**Why this matters here specifically:** the whole point of the retrieval agent is
that an LLM composes these commands, and in the named production deployment the
memory repository contains text from WhatsApp and Messenger conversations —
content the operator does not author. A prompt-injection payload that reaches the
model has a shell behind it.

The fix is small and does not cost the design anything: reject `$(`, `` ` ``,
`>`, `>>` and `<` at validation time, or execute each validated segment with
`shell=False` and wire the pipes in Python. The second is strictly better,
because it removes the parser differential rather than patching it — the
whitelist already produces the token lists it would need.

`tests/` has 22 files and **none of them covers the command router**. The rest of
the system is tested per-pass; the security boundary is not.

## 10. Tests, Evals, and Benchmarks

**No paper, no benchmark, no committed results.** 22 test files, most of them
consolidator behaviours — dedupe, link, reabsorb, redistribute, lock — plus
corporate and personal ontology end-to-end tests and a conformance module.

Decomposing consolidation into named passes with a test each is good practice and
it is where the testing effort went. What is not tested is retrieval quality —
the central claim is that grep and git beat a vector store for this workload, and
nothing measures it, including against the `baseline.py` sitting next to the
agent.

**I ran nothing**, and in particular no command was executed against the router.
The gap in section 9 is read from the source: the validator's `shlex` tokenisation
against `subprocess.run(..., shell=True)` on the unmodified string, with no
substitution or redirection check between them.

## 11. For Your Own Build

### Steal

- **Let the current state be small and put the history in the log.** Query and
  search hit a compact "now" surface; "how did this change" pulls only the
  relevant commits. It is the log-and-projection pattern with git supplying the
  log.
- **Give an exploration agent a whitelist, not a shell.** Thirteen commands with
  the base name taken via `Path(tokens[0]).name`, so `/bin/sh` cannot enter as a
  path.
- **Allowlist git's subcommands separately.** `git` is a write primitive and a
  network client; `log`, `diff`, `blame`, `show`, `rev-list`, `shortlog` are not.
- **Validate every segment of a chain.** Splitting on `|`, `&&`, `||` and `;`
  quote- and escape-aware, then checking each part, closes the gap where only the
  first command is inspected.
- **Add a presentation layer between the shell and the model.** A binary-content
  check, the elapsed time and the return code turn raw output into something the
  model can reason about and cannot be flooded by.
- **Make the executor pluggable with a thunk.** Endpoints close over the real
  call and hand a `Callable[[], dict]` to `submit_write`, so the queue backend
  and the memory internals stay decoupled and inline execution works in
  development.
- **Make the ontology configuration.** `personal` and `corporate` as separate
  directories with a conformance check means the entity model is not a code
  change.
- **Decompose consolidation into named passes and test each.** Dedupe, link,
  reabsorb, redistribute — and take a lock.
- **Put your known failure on the roadmap.** "Sometimes an entity will become a
  catch-all and the thing will insist in overloading it" is the sentence a
  potential adopter needs.

### Avoid

- **Do not validate with one parser and execute with another.** `shlex.split`
  for the check and `shell=True` for the run means arguments the validator
  approved can be syntax the shell expands. Either reject `$(`, backticks and
  redirection explicitly, or run each validated segment with `shell=False` and
  build the pipeline in Python.
- **Do not leave the security boundary untested.** 22 test files and none for the
  router is the wrong allocation when the router is what stands between an LLM
  and a shell.
- **Do not let corrections be invisible at read time.** The current file shows
  the corrected value with no signal that it changed; history is available and
  not consulted by default.

### Fit

A strong fit if your memory is genuinely a personal knowledge base that evolves —
relationships, timelines, facts about people — and you want it human-readable,
portable and diffable, with no index to maintain. The production deployment shows
the shape works at conversational scale.

Wrong fit if recall must survive vocabulary mismatch: there is no semantic
fallback when the right memory uses different words from the query.

Read `command_router.py` for the sandbox design and fix the execution call before
you deploy it anywhere the memory content is not yours.

## 12. Open Questions

- **Does anything upstream strip shell metacharacters?** None was found in the
  retrieval agent.
- **What does `baseline.py` compare against, and how did it do?** No results were
  found.
- **How is the catch-all entity problem being addressed?** It is on the roadmap
  unassigned.
- **Does the writer agent ever rewrite history?** The consolidator redistributes
  content between files; whether that rebases or only commits forward was not
  traced.

## Appendix: File Index

**The sandbox** — `src/diffmem/retrieval_agent/command_router.py` (the docstring
and Manus/*nix framing `:1-7`, `WHITELISTED_COMMANDS` `:22-26`, the git-bash
path resolution `:28-45`, `_is_text` `:74-85`, `_validate_command` with the
basename check and the git-subcommand allowlist `:87-106`, `_split_pipeline`
`:108-140`, `_split_chain` `:141-`, `_execute_pipeline` and the per-part
validation `:221-245`, `shell=True` `:257`, `subprocess.run` `:265`,
`_apply_presentation_layer` `:277`)

**Retrieval** — `src/diffmem/retrieval_agent/agent.py`, `resolver.py`,
`baseline.py`, `prompts/`

**Write path** — `src/diffmem/writer_agent/`,
`src/diffmem/consolidator_agent/`, `src/diffmem/repo_manager.py`,
`src/diffmem/frontmatter.py`

**Executor** — `src/diffmem/executor/__init__.py` (the public surface `:1-11`),
`base.py` (the thunk rationale `:1-9`), `factory.py`, `inline.py`,
`hatchet.py`, `hatchet_worker.py`, `hatchet_workflows.py`, `jobstore.py`

**Ontologies** — `ontologies/personal/`, `ontologies/corporate/`,
`src/diffmem/ontology/`, `src/diffmem/conformance.py`

**Tests** — `tests/test_consolidator_{dedupe,link,reabsorb,redistribute,lock,api,e2e}.py`,
`tests/test_corporate_{e2e,ontology}.py`

**Documentation** — `README.md` (the git rationale, the production deployment,
the roadmap with the catch-all entity defect), `repo_guide.md`,
`src/diffmem/CONTEXT.md`, `src/diffmem/executor/CONTEXT.md`

## History

**2026-08-09** — [`5f00e8d22dc05fb1fc505f5322cb717de61bed3f`](https://github.com/growth-kinetics/diffmem/commit/5f00e8d22dc05fb1fc505f5322cb717de61bed3f) — first reading. Screened before reading; the tree was read, never installed, and no command was executed against the router. The section 9 finding is read from the source.

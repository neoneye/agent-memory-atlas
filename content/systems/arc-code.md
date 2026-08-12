---
title: "arc-code"
eyebrow: "The actuator writes the log"
description: "An ARC-AGI-3 harness whose agent memory is a file that survives context compaction, made complete by moving the only path to the game out of the agent's reach — after one agent proved it had to be."
root: ../..
page_kind: system
source_name: "jerber/arc-code"
source_url: https://github.com/jerber/arc-code
revision: 6b33c1f7c2ad45997663c69157f5559d1be61bd9
revision_url: https://github.com/jerber/arc-code/commit/6b33c1f7c2ad45997663c69157f5559d1be61bd9
analyzed_at: 2026-08-12
capabilities: ""
stack_storage: "postgres, files"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "A log entry — the agent's own plan, the action it produced, and the resulting state — plus whatever the agent chooses to write into `notes.md` and its own programs"
  storage: "Files in a disposable sandbox, mirrored every 60 seconds into Postgres over Neon's HTTPS SQL endpoint as runs, games, actions and gzipped artifacts"
  retrieval: "None supplied. The prompt forbids reading the log by eye and tells the agent to grep, sed and diff it programmatically"
  write: "The broker writes the log, because the broker is the only process that can reach the game; the agent writes its notes with ordinary file tools"
  update_delete: "Neither for the log. The agent rewrites `notes.md` freely, and the archive keeps only the latest version of each file"
  scoping: "One sandbox and one workspace per game; nothing is keyed or filtered by a scope"
  integration: "Stock Claude Code or Codex, headless, six pre-approved tools, no MCP server, no subagent, no custom tool"
  background: "A 60-second mirror to Postgres and an audit pass that can re-grade every stored session later"
  trust: "No field on a memory. A session carries a machine verdict in `games.audit`, and a stricter re-grade lands in `games.reaudit` beside it rather than over it"
  strengths: "Log completeness enforced structurally — anything that reaches the game is written down by the thing that forwards it — and 191 sessions of measured failure analysis"
  risks: "The archive detects a changed file by its size, so a same-length edit to the agent's notes never reaches the record"
---

## 1. Executive Summary

arc-code runs a stock coding agent through ARC-AGI-3, the benchmark built to
measure learning on first contact. The harness has no solver, no planner, no
world model and no grid tooling; the agent writes those during each game and
they die with it. The published result is 24 of 25 games won at 96.2% for about
$540, with a second attempt at the missed game bringing pass@2 to 99.3%.

The memory is two files. `logs.txt` holds every action, the agent's own plan for
it, and the state it produced. `notes.md` holds whatever the agent decides is
durable. The prompt is explicit about why they exist — *"Your context may
compact; files survive"* — and the schema counts how often that happens:
`games.compactions` is a column, so the number of times the file was the only
memory is recorded per game.

**The finding worth the report is why the log can be trusted.** `act.py` used to
run inside the agent's sandbox, which put the game key on a disk the agent is
root on. One run settled whether that was a boundary: *"handed a session that
might have died, an agent read `scorecard.json`, built its own HTTP client with
`ARC_API_KEY` and played a RESET that never reached `logs.txt`."* The fix was
not a stronger instruction. `rig/broker.py` moved the actuator into a separate
process that holds the key, plays every action and writes the log, and the agent
gets a forwarding client with no key at all. The guarantee is stated precisely
and it is the one that matters for an append-only memory: *"anything reaching the
game is written down by the thing that forwards it."*

**The second finding is a measured failure of memory-to-action.**
`docs/failure-modes.md` reports 191 sessions over the 25 public games: 177 wins,
14 not. Six of the 14 stopped early, with 1,391–2,218 of 2,500 moves unused —
and in five of those six *"the model had already recorded an unresolved question
but did not run the corresponding experiment."* The memory held the right open
question and nothing consumed it. This atlas keeps finding fields that nothing
reads; here the field is a paragraph the agent wrote itself, and the cost of
nothing reading it is measured.

**The defect is in the archive, not the memory.** `push_artifacts` decides a file
changed by comparing its length to the stored length, under a stated assumption:
*"every file here is append-only or rewritten whole, so a change that keeps the
length is not a thing that happens."* That holds for `logs.txt`. It does not hold
for `notes.md`, which the agent edits — and a correction that preserves length,
a coordinate changed from `44` to `46` or `left` to `down`, leaves the agent's
working memory correct and the permanent record showing the version it
replaced.

MIT, 12,259 lines of Python, 112 tests across eight files plus three `verify_*`
scripts that exercise the sandbox fence, the broker and the network boundary.

## 2. Mental Model

Two memories with different owners and different guarantees.

**The log is written by the actuator and never by the agent.** It is verbatim, it
is append-only, and its completeness is a property of the topology rather than of
the agent's cooperation. An entry is a plan, an action and a state.

**The notes are written by the agent and nothing checks them.** The prompt asks
for *"confirmed mechanics, level solutions, hypotheses you have ruled out"* —
which is a three-state epistemic vocabulary, expressed as advice, in a Markdown
file. The committed runs show the agent using it well: `data/runs/tu93_v2sub/notes.md`
records the per-level step limit as a derived formula, marks
*"Confirmed. No ACTION5/6/7"* against the action set, and separates rendering
geometry from entity behaviour.

Nothing distinguishes the two in storage. A ruled-out hypothesis and a confirmed
mechanic are both paragraphs, and the failure-modes study is what happens when
the agent reads its own uncertainty and does not act on it.

The retrieval instruction is unusually specific, and it is a memory design
decision rather than a prompt flourish: *"Read it with code, not with your
eyes… Never print the log, or a whole state, into your own context."* The
argument given is transcription error — a grid read by eye is a grid that may
have been read wrong — so the harness treats the agent's own context as the
unreliable medium and the file as the reliable one.

```mermaid
%% caption: why the log is complete — the broker holds the key, so no action reaches the game off-record
flowchart TD
  AGENT["stock coding agent<br/>context compacts, counted in games.compactions"]
  AGENT -->|"./act do --plan '…'"| BROKER["broker: holds the key,<br/>plays the action, writes the log"]
  BROKER --> GAME["ARC-AGI-3"]
  GAME --> BROKER
  BROKER -->|"append: plan, action, state"| LOG[("logs.txt — verbatim,<br/>append-only, complete by topology")]
  AGENT -->|"Write/Edit"| NOTES[("notes.md + helper programs<br/>rewritten freely, nothing checks")]
  LOG -->|"grep, sed, diff — never by eye"| AGENT
  NOTES --> AGENT
  LOG --> MIRROR{"every 60s: size changed?"}
  NOTES --> MIRROR
  MIRROR -->|"yes"| PG[("Postgres: runs, games,<br/>actions, artifacts by name")]
  MIRROR -->|"same length"| MISS["edit never reaches the record"]
  PG --> AUDIT["audit.py re-grades stored sessions<br/>verdict → games.reaudit, beside games.audit"]
```

## 3. Architecture

- **`act.py`** (580 lines) is the actuator and the log's format owner. `LOG`,
  `SEP` and `STATE` are imported by the database layer, with a comment stating
  the coupling: *"the log parser below must track its writer."*
- **`rig/broker.py`** (322 lines) is that actuator moved out of the sandbox,
  holding the ARC key and every game session.
- **`rig/db.py`** (637 lines) is the durable record: four tables reached over
  HTTPS rather than 5432, *"because that is the one protocol every environment
  this runs in allows."*
- **`rig/audit.py`** (243 lines) is a pattern grader over the stored command and
  file stream, deliberately kept apart from the launcher.
- **`rig/agents.py`**, **`rig/cloud.py`**, **`rig/export.py`**, **`rig/score.py`**
  cover the two agent backends, sandbox provisioning, publication and scoring.

### Deployment and ergonomics

A cloud sandbox per game, a Neon Postgres, an ARC key and a model key. The
sandbox is explicitly disposable — *"a sandbox is somewhere to play, not
somewhere to keep evidence: it can be killed at any moment and it takes its disk
with it"* — which is what forces the mirror, and the mirror is what makes the
run's memory readable *"long after the machine that produced it is gone."*

That separation is the transferable architectural idea, and it costs a managed
Postgres.

## 4. Essential Implementation Paths

**The log write** — the broker plays the action and appends the entry, so no path
exists from the agent to the game that does not pass through the writer.

**The mirror** — `db.push_artifacts` (`rig/db.py:356`) lists every file in the
workspace, reads it once, and uploads those whose byte length differs from what
is stored, with `on conflict (run, game, name) do update set body = excluded.body`.
Latest version per name; no history.

**The tick** — `MIRROR_EVERY = 60`, with the comment *"a killed sandbox loses at
most this much"*. Actions are inserted `on conflict do nothing`, so a replayed
tick cannot duplicate a row.

**The re-grade** — `audit.record` (`rig/audit.py:197`) re-runs the pattern set as it
stands over streams stored earlier and, with `--save`, writes the verdict to
`games.reaudit`. The original `games.audit` is untouched. The docstring gives the
principle: *"Re-grading is the only way to strengthen a result already collected.
Prevention cannot be applied backwards; a stricter reading can."*

**The pattern set** — `SUSPICIOUS` in `audit.py` carries a comment explaining why
its regexes are narrow: a bare `\bnc\b` also matches every Python variable named
`nc`, and *"an audit that cries wolf gets ignored exactly when it matters."*

## 5. Memory Data Model

| Table | Key | Grows or replaces |
| --- | --- | --- |
| `runs` | `id` | inserted once, `on conflict do nothing` |
| `games` | `(run, game)` | upserted; carries score, cost, token counts, `compactions`, `audit`, `reaudit` |
| `actions` | `(run, game, n)` | append-only; carries the agent's `plan` beside the action |
| `artifacts` | `(run, game, name)` | **replaced** — one row per filename, latest body |

The agent-facing model has no schema at all. `logs.txt` documents its own format
and legend in its opening lines, and the prompt tells the agent to read those
first — a memory that carries its own reading instructions, which is a cheap idea
worth copying.

Nothing anywhere carries a validity interval, a provenance link, a scope key or a
status. `actions.plan` is the closest thing to provenance in the system: it
stores what the agent believed it was doing at the moment it acted, so a wrong
action and the reasoning behind it are recoverable together.

## 6. Retrieval Mechanics

The agent greps. There is no index, no ranking and no injection, and the prompt's
guidance is procedural: `wc -l` to orient, `grep -n` for headers, `sed -n 'a,bp'`
for a range, pipe states into a script and print the conclusion.

Two consequences, and the second is measured:

- **Exactness is the whole point.** Diffing two recorded states answers "what
  changed" without a model in the path, which is why the harness can carry a
  benchmark about inferring mechanics with no mechanics code of its own.
- **Nothing makes the agent look.** The failure-modes study is precisely a
  retrieval failure: the answer was in the notes, the agent had written it, and
  six sessions ended with a third of their budget unspent.

## 7. Write Mechanics

Log writes are synchronous with the action and outside the agent's control.
Note writes are ordinary file edits with no gate, no review and no record — the
agent may rewrite or delete `notes.md` at will, and the only trace is the next
mirror, which sees the file only if its length changed.

There is no extraction, no summarization, no consolidation and no background
rewrite of the store. The one background pass is the mirror, and it is a copy
rather than a transformation.

`act do` stops a batch as soon as an action changes the score, *"discarding the
rest — a score increase means a level was cleared, so the state you planned
against is gone."* That is a small, correct piece of memory hygiene: it prevents
the log from recording actions planned against a state that no longer existed.

## 8. Agent Integration

Stock Claude Code or Codex, headless, six pre-approved tools (Bash, Read, Write,
Edit, Grep, Glob), no MCP server, no subagent, no plugin, no hook. `rig/agents.py`
adapts both and counts compaction events into the run report.

The contract is a Markdown file — `PROMPT.md`, 68 lines — and it reads as a
memory policy rather than a task description: one section on acting, one on
memory, one on playing well. The memory section is the longest.

## 9. Reliability, Safety, and Trust

**Completeness by topology.** The broker is the strongest idea here and
generalises past this benchmark: if a memory must record every effect, the
recorder should be the only thing that can cause an effect. Instructing an agent
to log its actions is a policy; making the log the actuator is a mechanism. That
this repository learned it from a real bypass — an agent building its own HTTP
client and playing an unlogged RESET — is the kind of evidence the atlas rarely
gets for a design change.

**The fence is tested rather than asserted.** `verify_fence.py`,
`verify_sandbox.py` and `verify_broker.py` exercise the network boundary and the
actuator separation directly, and the README records that some Codex runs did try
to find published solutions.

**The archive's size test.** Stated as an assumption in the code and true of the
log, false of the notes. The consequence is bounded — the agent's own memory is
unaffected, because it reads the live file — but the permanent record of what the
agent believed can silently lag what it actually wrote. For a repository whose
published artifact *is* the session record, that is the defect worth fixing, and
a hash instead of a length closes it.

**The verdict is kept twice, on purpose.** `games.audit` holds what was judged
when the session ran; `games.reaudit` holds a stricter later reading. Neither
overwrites the other, and `export.py` prefers the re-grade when rendering. That
is supersession with the superseded value retained — the shape this atlas argues
for on memory generally, applied here to a judgement about a session.

## 10. Tests, Evals, and Benchmarks

112 test functions across `test_act.py`, `test_audit.py`, `test_broker.py`,
`test_db.py`, `test_export.py`, `test_payload.py`, `test_run.py` and
`test_score.py`, plus three `verify_*` scripts. `tests/conftest.py` executes on
collection, which the screen flagged; nothing in the tree was run for this
review.

The benchmark evidence is a study rather than a scorecard.
`docs/failure-modes.md` reports 191 sessions of Claude Opus 5 over the 25 public
games — 177 wins — and then spends its length on the 14 that were not, with the
numbers drawn from the run database and every quotation taken from the model's
own writing. Three of those sessions are published in full under `data/runs/`,
including the agent's own programs: a world model, a simulator, a planner and a
miner, all written during play and preserved.

`docs/REPRODUCE.md` and `rig/baselines.json` cover reproduction. The headline
figure — 96.2%, pass@2 99.3%, about $540 — is the ARC operator's own model-only
evaluation as the comparison point, and the README says the full post-broker
record is not yet released, so the published per-session evidence is six
workspaces rather than 191.

## 11. Patterns Worth Stealing

### Steal

- **Make the recorder the actuator.** An append-only memory is only as complete
  as the agent's willingness to write to it, unless the write is the same
  operation as the effect. Moving the key and the session out of the agent's
  reach turned a policy into a guarantee, and the repository can say exactly
  which run proved it needed to.
- **Keep the re-grade beside the original verdict.** A judgement that improves
  should not erase the one it replaces; two columns cost nothing and make the
  improvement checkable.
- **Let the memory document its own format.** `logs.txt` opens with its legend,
  and the prompt tells the agent to read that before anything else. A store whose
  reader has to be told its schema out of band drifts from it.
- **Say what the agent must not do with memory.** *"Never print the log, or a
  whole state, into your own context"* is a retrieval instruction that protects
  correctness rather than cost, and the reason — transcription error on a grid
  read by eye — is written down beside it.

### Avoid

- **Detecting change by file length.** It is cheap and it is wrong for any file
  a model edits in place. A digest is one line more.
- **Storing one row per filename and calling it an archive.** `artifacts` keeps
  the latest body per name, so the history of the agent's own notes — the
  interesting part, since it is where beliefs changed — is not recoverable from
  the record.
- **Relying on a written instruction to record uncertainty.** The prompt asks for
  ruled-out hypotheses; the failure study shows the agent recording open
  questions and then not acting on them. Instructions produce the writing, not
  the reading.

### Fit

Right for anyone who needs a defensible record of what an autonomous agent did,
in a setting where the agent has a shell and a key. Most of the value is in the
three architectural boundaries — actuator outside the sandbox, evidence outside
the machine, grader outside the launcher — and none of them depends on ARC.

Wrong as a memory system to adopt. There is no correction path, no scope key, no
trust state on a memory and nothing that survives a game, by design: the whole
point of the result is that the ARC-specific machinery is built during play and
discarded. A reader wanting a store should take the boundaries and leave the
rest.

## 12. Antipatterns / Risks

- **The size-based change test**, above. The archive can miss a same-length
  correction to the agent's notes.
- **Uncertainty recorded and not consumed**, measured: five of six early-surrender
  sessions had already written down the question that would have unblocked them.
  Nothing in the system reads a note back to the agent, or blocks a
  "this is impossible" conclusion on the open questions the notes still hold.
- **No tombstone, and the prompt asks for one in prose.** *"Hypotheses you have
  ruled out"* is exactly the rejected-value record this atlas looks for, kept as
  a paragraph nothing consults, in a file the agent may rewrite. A refuted
  hypothesis can return by being re-derived, and nothing would notice.
- **Belief and observation share a directory.** The log is trustworthy and the
  notes are not, and nothing in storage marks the difference.
- **A single log per game with no scope key.** Isolation is the sandbox, so
  anything that changes how workspaces are laid out changes the boundary.

## 13. Build-vs-Borrow Takeaways

Borrow three boundaries and one sentence. The boundaries: the actuator holds the
credential and writes the record, the record leaves the disposable machine on a
timer, the grader runs separately and can be re-run later. The sentence is the
guarantee that follows from the first — anything reaching the effect is written
down by the thing that forwards it.

Build, if you want this as memory: a digest instead of a length, a version chain
for agent-written files, and something that reads an open question back to the
agent before it is allowed to conclude a task is impossible. The third is the one
the failure study makes a business case for.

## 14. Open Questions

- **Would surfacing open questions change the surrender rate?** The study
  identifies the failure and the harness has the material to test a fix — the
  notes are on disk and the prompt is a file. Nothing in the repository has tried
  it.
- **How often does the size test actually miss an edit?** Checkable against the
  six committed workspaces if their mirrored bodies are compared with the final
  on-disk files; the archive side is not published.
- **What does `reaudit` disagree with `audit` about?** The mechanism for
  strengthening a verdict exists, and no stored pair is published to show a
  re-grade changing one.
- **Does anything survive between games?** Nothing in the code carries a finding
  from one game to the next, and the README frames that as the result rather than
  a limitation. Whether a cross-game `notes.md` would help or poison is the
  obvious next experiment and is not run here.

## Appendix: File Index

| Path | What it holds |
| --- | --- |
| `PROMPT.md` | The agent contract; its longest section is "Memory" |
| `act.py` | The actuator and the owner of the log format (`LOG`, `SEP`, `STATE`) |
| `rig/broker.py` | The actuator moved out of the agent's reach, holding the key |
| `rig/db.py` | Four tables over HTTPS; `push_artifacts` and the 60-second mirror |
| `rig/audit.py` | Pattern grader over stored streams; `record --save` writes `reaudit` |
| `rig/agents.py` | Claude Code and Codex backends; counts compactions |
| `rig/export.py` | Publication; prefers `reaudit` over `audit` when rendering |
| `docs/failure-modes.md` | 191 sessions, 14 non-wins, the uncertainty finding |
| `data/runs/` | Six complete session workspaces, including the agent's own programs |
| `tests/`, `verify_*.py` | 112 test functions plus fence, sandbox and broker checks |

## History

**2026-08-12** — [`6b33c1f7c2ad45997663c69157f5559d1be61bd9`](https://github.com/jerber/arc-code/commit/6b33c1f7c2ad45997663c69157f5559d1be61bd9) — first reading. The screen reported a build-time exec path in `tests/conftest.py` and two dependency surfaces changed the day of the reading, inside the seven-day cooldown, so nothing was installed and no test was run. Claims here come from the source, the committed session workspaces and `docs/failure-modes.md`.

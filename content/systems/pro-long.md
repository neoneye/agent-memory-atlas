---
title: "PRO-LONG"
eyebrow: "The log is the memory"
description: "An ARC-AGI-3 harness whose whole memory is one append-only text log the coding agent greps, with a committed no-log arm and a budget-matched rerun."
root: ../..
page_kind: system
source_name: "alexisfox7/PRO-LONG"
source_url: https://github.com/alexisfox7/PRO-LONG
archive_name: "alexisfox7--PRO-LONG"
revision: d87233c9128d7b9dc5d780e83b4aeb8377dd8805
revision_url: https://github.com/alexisfox7/PRO-LONG/commit/d87233c9128d7b9dc5d780e83b4aeb8377dd8805
analyzed_at: 2026-11-11
licence: "MIT, in a root LICENSE file, the npm package.json and the research harness's trove classifier, with no rider"
size: "3,258 lines of Python in 22 files under research/arc-agi-3/prolong_agent/, plus 1,060 lines of TypeScript in src/ and 167 of templates for the npm installer"
activity: "64 commits, 7 March – 2 November 2026; 53 by the lead author, 6 from a server account, 5 by a co-author under two spellings; the last 18 change only READMEs and figures"
tests: "1 file, tests/lifecycle.test.ts, 144 lines in 3 cases over the npm installer, run by npm test; nothing tests the research harness; none run for this reading"
capabilities: "negative_eval"
capability_evidence:
  negative_eval: "the installed hook runtime — what must not enter the log | tests/lifecycle.test.ts:87-94, :114-140, templates/runtime.mjs:33-38 | the runtime refuses to record a tool event whose serialized input names the log — `if (json(toolInput)?.includes('.prolong/log.jsonl')) return;` — and the lifecycle test drives the real runtime, has the agent grep its own log, and asserts the file is one line long with the reason in the message: 'reading the memory log must not copy it back into itself'. Two further must-not cases sit beside it: an uninstall must leave a user-modified adapter file in place, and an init that hits unparseable existing hook JSON must fail before creating any managed file, asserted by `assert.rejects` on both `.prolong/runtime.mjs` and `AGENTS.md` | subsystem: this is the npm tooling layer, not the ARC harness the rest of this report reads, and it is a write-path assertion rather than a negative retrieval one. The guard is a substring match on one spelling of the path, so `cd .prolong && rg x log.jsonl` and a `.prolong/*.jsonl` glob both record; the Python harness under research/ has no test of any kind"
stack_storage: "files"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "An action section in a plain-text log — a header, the tool call, the resulting 64x64 board, and the agent's own prior analysis — delimited by an eighty-column rule of equals signs"
  storage: "One `logs.txt` per game on the host, plus whatever the agent writes into its Docker workspace; no database, no index, no embeddings"
  retrieval: "None supplied. The agent greps and parses the log itself with Bash and Python, which is the entire thesis"
  write: "The harness appends every action and board state, and folds the agent's briefing and `[PLAN]` into the same file; no flag at the pin suppresses them"
  update_delete: "Neither, on the harness side. Nothing is ever rewritten or removed — but what reaches the agent is a copy governed by `--log-window`: the whole log, the last N sections, or none"
  scoping: "A directory per game and a Docker bind mount; no scope key is stored on a record or applied as a filter"
  integration: "Two backends — Claude Code and Codex — each driven headless in a container whose default network reaches only the model API through a proxy"
  background: "None. Everything happens on the turn boundary; the runner appends, copies, and calls the agent again"
  trust: "No field. The agent keeps hypothesis-versus-confirmed in prose in its own `notes.md`, and nothing reads it"
  strengths: "Committed per-game results with third-party replay links, a matched no-log arm, and a budget-matched rerun published because the unmatched comparison flattered the result"
  risks: "The incremental log sync takes its offset from the size of a file the agent is invited to write to, so an agent that edits its own log silently loses history; most ablations the paper reports have no flag in the published CLI"
---

## 1. Executive Summary

PRO-LONG is a harness for ARC-AGI-3, the benchmark built to measure learning on
first contact, and its memory is one file. `logs.txt` accumulates an action
header, the tool call, the resulting 64x64 board and the agent's own written
analysis, for every action of a game. There is no database, no index, no
embedding and no retrieval function. The agent is a coding agent, so retrieval is
`grep`.

The paper is *PRO-LONG: Programmatic Memory Enables Long-Horizon Reasoning*
([arXiv:2607.20064](https://arxiv.org/abs/2607.20064), Alexis Fox, Junlin Wang,
Paul Rosu and Bhuwan Dhingra; v1 22 July 2026, v3 12 October 2026). Its framing
is a tradeoff in which *"preserving more information makes relevant details
harder to retrieve"*, and its answer is to keep everything and make the agent pay
the search cost programmatically. v3 adds NetHack, where the harness carries the
log across five sequential episodes of a fixed-seed lifetime.

**What earns the report is the evidence posture, not the store.** Four scorecards
are committed under `research/arc-agi-3/scorecards/`, and two of them are the
same model at the same effort with the memory removed. `prolong_r3_online` runs
with the full log and scores a 50.2% mean over 25 games; `inprompt_r3_online`
runs with `--log-window -1` — board injected into the prompt, no log file in the
workspace at all — and scores 24.7%. Every game in the log arm carries a replay
URL on `arcprize.org`, so the numbers are checkable by somebody who did not run
them.

**Then they cut their own headline.** The log arm ran to 1,000 actions and the
no-log arm to 500, which makes the raw comparison unfair in the authors' favour.
`prolong_r3_online_scorecards_at500.txt` re-scores the log run at the 500-action
cutoff and publishes the result: **45.6%**, against 24.7%. The advantage is real
and it is 4.6 points smaller than the file next to it says. Committing the
budget-matched rerun of your own flagship number, when nobody would have noticed
its absence, is the [benchmark discipline this atlas asks for](../../benchmarks/)
and finds in very few repositories.

**The committed runs are a sample of what the paper reports.** The paper's
headline for GPT-5.5 is a five-run mean, 41.2% against 24.0%; the repository
commits one run per arm, from a harness version whose settings block names a
`session-mode` flag the pinned CLI does not accept. Of the paper's ablations —
the tool ladder, the cleared workspace, the last-25 window, the compaction
threshold — only the window is a flag here, and the NetHack harness is not in the
repository at all. Section 10 has the inventory.

**The defect is in the sync, not the design.** In the default full-history mode
the harness copies only the new tail of the master log into the agent's sandbox,
and it computes where the tail starts from `destination.stat().st_size` — the
size of the copy sitting in a writable workspace the system prompt invites the
agent to save notes into. Every byte the agent adds to that file is a byte of
real log the harness then skips. I re-derived the routine in isolation: 32
agent-written bytes cost two of four board states, silently and permanently, with
nothing anywhere reporting a gap. **It has not fired in anything published
here** — in all 25 committed Fable 5 runs the agent's copy is an exact byte
prefix of the host master, so no agent ever wrote to its own log. The defect is
latent, and what keeps it latent is a convention no code states.

The research harness under `research/` carries no test of any kind. The
installer beside it, described in section 3, has one — so the half that ships to
other people's machines is tested and the half the paper's numbers come from is
not.

## 2. Mental Model

A memory is an **action section**: everything between two eighty-column rules of
equals signs. The harness writes it, the agent reads it back, and nothing else in the
system has an opinion about what a memory is.

The lifecycle has no states. A section is appended and then it is permanent on
the host. What changes is not the memory but **how much of it the agent is
allowed to see**, which is set by one flag at launch and never by the agent:

```text
--log-window  (unset)  the whole log, copied as an incremental tail each call
--log-window  N>0      the last N action sections, rewritten whole each call
--log-window  -1       no log file at all; the current board goes in the prompt
                       (0 and other negatives are refused by the argument parser)
```

That flag is the system's real contribution. Forgetting here is a harness
parameter with an ablation arm attached, rather than a decay curve nobody
measured.

The second memory is the one the agent writes. `/workspace/` persists across
calls and the prompt says so — *"Feel free to save notes, state, or helper
functions"* — and the committed runs under `release_logs/` show what the agent
does with it. Its `notes.md` keeps an epistemic distinction the schema does not:

```text
- Purpose unknown: goals? move counter?
## Hypothesis
Ship floats to ceiling of water region. …
## Confirmed mechanics (after Actions 1-2)
- ACTION4 moves ship RIGHT by exactly 6 columns …
```

Hypothesis, then confirmed, with the evidence that promoted it. That is a trust
state kept in prose by the memory's own author, read by nothing and enforced by
nothing. The paper measures what it is worth: wiping the workspace after every
call leaves the log arm at 40.7% against 41.2% and drops the no-log arm from
24.0% to 19.9% (Table 3) — so the agent's notes matter when there is no log and
barely at all when there is one.

```mermaid
%% caption: how the master log reaches the agent, and where an agent-written byte costs real history
flowchart TD
  ENV["ARC-AGI-3 environment"] -->|"board after each action"| MASTER[("logs.txt on the host<br/>append-only, never rewritten")]
  AGENT["coding agent<br/>(resumed session, one call per batch)"] -->|"briefing and [PLAN]"| MASTER
  MASTER --> W{"--log-window"}
  W -->|"unset: copy bytes from<br/>offset = size of the copy"| SB[("/workspace/logs.txt<br/>in the sandbox, rw")]
  W -->|"N: rewrite the copy<br/>from the last N sections"| SB
  W -->|"-1: no file"| PROMPT["current board<br/>pasted into the prompt"]
  SB -->|"grep, python, Read"| AGENT
  AGENT -->|"writes notes.md, helpers"| SB
  SB -.->|"agent bytes inflate the offset,<br/>so the next sync skips real log"| GAP["history the agent never receives<br/>— no checksum, no warning"]
  AGENT -->|"actions.json"| ENV
```

## 3. Architecture

**The repository holds two things, and only one is the paper's.** The ARC-AGI-3
agent the rest of this report describes lives under `research/arc-agi-3/`.
Beside it is a second, smaller product: `src/` is a TypeScript installer that
wires an append-only `.prolong/log.jsonl` into a coding CLI — Claude Code, Codex,
opencode and pi each get an adapter — and ships a skill telling the agent to
treat that file as external memory, retrieved with `rg`, `tail` and `jq` rather
than through any index.

It is worth reading for one instruction, which is the kind of thing most skills
omit: after recovering history, *"Verify old observations against the current
workspace before acting on them."* A log of what happened is not a claim about
what is true now, and the skill says so to the agent that will read it.

The log is the memory rather than a record of changes to one, so it earns no
`audit_log`; there is no scope key, no status field and no second clock, so the
rest stay withheld too.

Two backends implement one interface. `prolong_agent/agent/base.py` (191 lines)
holds the prompts' assembly, the history sync, the truncation helper and
`actions.json` parsing; `claude_code_agent.py` (487 lines) and `codex_agent.py`
(431 lines) each drive a headless coding agent inside a Docker container.

- **The runner** (`environment/runner.py`, 520 lines) owns the loop: call the
  agent, read `actions.json`, execute up to `--action-cap` actions against the
  environment, append what happened, repeat.
- **The environment** (`environment/arcagi3.py`, 141 lines) wraps the `arc_agi`
  toolkit; `--operation-mode` selects online, offline or normal.
- **The swarm** (`agent/swarm.py`, 308 lines) is the CLI and runs independent
  games concurrently; it does not coordinate agents within a game.

### Deployment and ergonomics

Four Docker images (two sandboxes, two API proxies), Python 3.12, an ARC API key
and a model key. The containers are the safety story and it is a deliberate one:
a non-root user, `--cap-drop=ALL`, `no-new-privileges`, a 256 MB `tmpfs` for
`/tmp`, a bind mount of the game workspace, and by default an internal network
whose only egress is a proxy to the model API (`claude_code_agent.py:90-118`).
`utils/sandbox_net.py` builds that network rather than documenting it. An
environment variable opts out.

The operational cost is a real one for a reader thinking about adoption: nothing
here runs without Docker, and the memory it demonstrates would work in a plain
directory.

## 4. Essential Implementation Paths

All paths are under `research/arc-agi-3/prolong_agent/`.

**The write** — `GameRunner._log_action` (`environment/runner.py:503`) opens the
log in append mode, writes the separator, the header (`Action N | Level L |
Attempt A | Plan Step i/n | Score: S`), the agent's consumed briefing as a
`[PLAN]` block, and the tool call. `_append_post_action_board` (`:233`) adds the
resulting board, and the initial board is written once when the file is empty
(`:334-340`). There is no other writer on the harness side.

**The window** — `BaseAgent._copy_truncated_log` (`agent/base.py:152`) splits on
`(?=={80}\n)`, always keeps `parts[0]`, and writes the last `window` sections over
the copy. Both backends inherit it; there is one implementation.

**The incremental sync** — `BaseAgent._sync_history` (`agent/base.py:104-114`),
called by `claude_code_agent.py:232` and `codex_agent.py:123` before every agent
call:

```python
destination = sandbox / log_path.name
if self._log_window is not None:
    self._copy_truncated_log(log_path, destination, self._log_window)
    return
previous_size = destination.stat().st_size if destination.exists() else 0
with open(log_path, "rb") as source, open(destination, "ab") as output:
    source.seek(previous_size)
    shutil.copyfileobj(source, output)
```

**The instructions file** — the two backends differ in one place that matters.
Claude Code rewrites `CLAUDE.md` in the agent's workspace from the template on
every call (`claude_code_agent.py:236-237`); Codex writes `AGENTS.md` only if it
does not exist (`codex_agent.py:127-129`). On Codex an agent that edits its own
instructions file keeps the edit for the rest of the game, and on Claude Code the
edit is gone at the next call.

## 5. Memory Data Model

There is no schema. A section is text, and its structure is a convention shared
between the writer, one regex and the agent:

| Marker | Written by | Read by |
| --- | --- | --- |
| `================` ×80 | `_log_action` | the window splitter |
| `Action N \| Level L \| Attempt A \| Score: S` | `_log_action` | the agent |
| `Tool Call: ACTION6({"x": 30, "y": 40})` | `_log_action` | the agent |
| `[INITIAL BOARD STATE]` / `[POST-ACTION BOARD STATE]` | the runner | the agent, programmatically |
| `[frame 1/N]` … `[settled]` | the runner | the agent |
| `[PLAN]` block | the agent, folded in by the harness | the agent, next turn |

Beside it sit `notes.md` (the agent's, unstructured), `actions.json` (deleted
before each call), and `current_board.txt` (overwritten each call, the no-log
arm's prompt source). The model conversation is a third store: Claude Code
sessions persist under a host `cc_sessions/` directory and Codex sessions under
its `.codex` home, both bind-mounted into the container.

Nothing carries a validity interval, a source, a confidence or a status. The
board states are observations and are true by construction; the agent's analyses
are beliefs and sit in the same file with the same weight.

## 6. Retrieval Mechanics

The retrieval mechanism is the absence of one. The system prompt tells the agent
to *"Parse it **programmatically**, as reading full 64x64 board states from
prompt can introduce precision errors"* and lists Read, Write, Edit, Bash, Grep
and Glob. That is the whole read path.

Two properties follow, and they are the interesting half of the design:

- **Recall is exact when it happens.** A grep for a fixed cell across board
  sections returns the actual bytes, not the nearest neighbour of an embedding of
  them. For a task whose state is a grid, an approximate retriever is worse than
  useless, and the paper's tradeoff framing is really an argument that lexical
  exactness beats semantic recall when the memory is machine-generated.
- **Recall is entirely discretionary.** Nothing injects. If the agent does not
  think to look, the memory is inert — the failure this atlas records for every
  progressive-disclosure store, here with no index and no table of contents to
  make looking cheap.

The paper prices the second property directly. Its tool ladder (Table 2) runs
the log arm with Read only (23.1%), then adds grep (27.2%), Python (38.3%) and
write and edit (41.2%): most of the memory's value arrives with Python, not with
search.

The prompt adds one nudge whenever a log is present, and it is the only retrieval
guidance in the system: *"Cross-turn parsing (diffs between distant boards, greps
of a fixed cell across board sections) is tractable and can be useful for
understanding mechanics, including long-horizon ones."*

## 7. Write Mechanics

Writes are synchronous, deterministic and unconditional. The harness appends
after each action; no model call decides what is worth keeping; there is no
extraction, no summarization and no consolidation pass anywhere in the tree. The
lag between a write and its being retrievable is one turn boundary — the next
call sees the new bytes, because the copy happens before the agent is invoked.

Nothing rewrites the store. There is no delete, no expiry, no supersession and no
tombstone, and for the master log that is defensible: it is a record of what
happened in a game, and what happened does not stop having happened.

The agent's half of memory has no discipline at all. It may write, edit or delete
anything under `/workspace/` including the log copy. The harness deletes only
`actions.json` (and `last_message.txt` on Codex) before each call. Neither kind
of change is recorded.

**Whether writes block the agent:** they cannot, because the agent is not running
when they happen. The turn structure is strictly alternating.

## 8. Agent Integration

The agent is a stock coding agent, headless, with no MCP server and no custom
tool. Claude Code runs with a fixed `--disallowedTools` list that removes
subagents, web access, MCP and planning tools (`claude_code_agent.py:257`). The
agent communicates its intent by writing `/workspace/actions.json`, which
`_parse_actions_json_text` (`base.py:159`) reads with a cap and a validity check,
discarding unrecognized entries with a warning rather than failing the turn.

The model conversation is *also* persisted. Claude Code is started with
`--session-id` and resumed with `--resume`, the id held in a per-game dictionary
(`claude_code_agent.py:179-185`) and the transcript under `cc_sessions/`; Codex is
resumed with `exec resume`. So there are two memories — the provider's
conversation, compacted by the client as it grows, and the inspectable log — and
the second is the one the reader can read and the ablation can remove. Claude
Code's native auto-compaction is the moment the second earns its keep. On Codex,
a context-overflow error clears the session id (`codex_events.py:171-178`) and
the next call starts a fresh session with only the workspace behind it.

**How the installer's side writes.** The `.prolong/runtime.mjs` it generates is
63 lines. Each hook event is appended as
`{timestamp, client, sessionId, type, content}`, and `eventType` normalises the
clients' differing event names onto six shared kinds — `session_start`,
`user_prompt`, `tool_call`, `tool_result`, `assistant_message`, `session_end` —
by lowercasing and substring-matching, so an unrecognised name is recorded under
itself rather than dropped.

One mechanism there has no counterpart in the research code, because only the
installed version needs it. An agent that greps its own memory produces tool
output containing the log, which a naive recorder would append straight back
into it — so `record` drops any tool event whose serialized input names the log
path (`templates/runtime.mjs:37`):

```js
if (json(toolInput)?.includes(".prolong/log.jsonl")) return;
```

The guard is a substring match on one spelling. An absolute path contains that
substring and is caught; `cd .prolong && rg decision log.jsonl` is not, and
neither is a `.prolong/*.jsonl` glob. Installation is careful in a way worth
naming: `init` is idempotent, refuses to touch a client whose existing hook JSON
does not parse, and `uninstall` removes PRO-LONG's own block while preserving
both the user's pre-existing hooks and any adapter file they edited.

## 9. Reliability, Safety, and Trust

**The sync defect.** The invariant the incremental copy needs is that the sandbox
file is a byte-exact prefix of the host file. Nothing establishes it. The
workspace is bind-mounted `rw`, the agent has Write and Edit, and the system
prompt encourages it to keep files there. I re-derived the routine over a
scratch master and copy, without importing the target:

```text
turn 1: harness appends 4 board lines, syncs        → copy == master
        agent appends a 32-byte note to the copy
turn 2: harness appends 4 more board lines, syncs
        → previous_size is 32 bytes too large
        → master bytes 64..96 are never copied
        → copy holds 2 of the 4 new board lines; nothing reports a gap
```

The same failure runs the other way: an agent that truncates its copy causes the
harness to re-append material already present, so the log the agent parses gains
duplicate action sections with the same index. Both are silent, and both are
confined to the default mode — `--log-window N` rewrites the copy whole each call
and cannot drift. A checksum, a byte offset kept by the harness, or copying to a
path the agent does not own would each close it.

**Whether it has ever fired is checkable, because both files are committed.**
Each of the 25 runs under `release_logs/fable5/` holds the host master beside the
agent's `workspace/logs.txt`. Comparing them byte for byte: in all 25 the copy is
an exact prefix of the master — shorter only by the tail appended after the final
agent call. No published result is affected. What protected them is that no agent
happened to write to `logs.txt`, which the prompt neither forbids nor mentions
while inviting writes to the directory it sits in.

**The window is a governance decision made outside the agent**, which is a
genuine strength stated plainly: the agent cannot expand its own context by
deciding it needs more history, and cannot be prompt-injected into doing so,
because truncation happens on the host before the container ever sees the file.

**Trust has no representation.** Observations and the agent's own inferences
share one file with no marker distinguishing them, so a wrong hypothesis written
at action 40 is grepped at action 400 with exactly the weight of a board state.
No flag at this pin keeps the agent's `[PLAN]` out of the log.

**Sandboxing** is the strongest operational property: section 3's container
flags, no general network egress, and a proxy for the model API only.

## 10. Tests, Evals, and Benchmarks

**One test file, and it is on the other half of the repository.**
`tests/lifecycle.test.ts` is 144 lines over three cases, wired to `npm test`
(`npm run build && node --test dist/tests/*.test.js`), and it covers the npm
tooling layer of section 8 — not the ARC harness. It is good: it spawns the
generated `runtime.mjs` as a real subprocess, feeds it a hook event on stdin,
and reads back the log it wrote.

Its centre is a must-not case. The agent is made to grep its own memory, and the
assertion is that the memory did not grow:

```js
assert.equal(afterSelfRead.length, 1, "reading the memory log must not copy it back into itself");
```

Two more sit beside it — an `uninstall` must leave a user-modified adapter file
in place and warn rather than delete, and an `init` that meets unparseable
existing hook JSON must fail *before* creating any managed file, asserted by
`assert.rejects` on both `runtime.mjs` and `AGENTS.md`. All three are about what
must not happen to something the user owns, which is the right instinct for a
tool that edits other programs' config.

**The research harness has nothing on `main`.** No test touches
`research/arc-agi-3/prolong_agent/`. For a harness whose result is a benchmark
number, the evaluation is the test suite — but the sync and the window splitter
are ordinary functions that would take a dozen lines each to pin, and the sync
defect above is exactly what a test would have caught. An unmerged branch,
`feat/research-experiment-configs`, adds four test files and a CI workflow for
the harness; its sync test appends to the source and syncs twice, and never
writes to the copy, so it does not reach the defect.

**Four committed scorecards**, and the set is unusually well-formed:

| File | Arm | Actions | Mean |
| --- | --- | --- | --- |
| `prolong_r3_online_scorecards.txt` | GPT-5.5, full log | 1,000 | **50.2%** |
| `prolong_r3_online_scorecards_at500.txt` | the same run, re-scored | 500 | **45.6%** |
| `inprompt_r3_online_scorecards.txt` | GPT-5.5, `--log-window -1` | 500 | **24.7%** |
| `fable_online_scorecards.txt` | Fable 5, full log, one run per game | up to 2,000 | 94.7%, by my arithmetic over the 25 lines |

Each GPT-5.5 file carries its settings block — backend, model, reasoning effort,
grid mode, action cap — so the arms can be compared on their face. The
budget-matched row is the one worth naming again: it exists only because the
honest comparison is worse than the available one. The settings block also names
`session-mode: resume`, a flag the pinned `swarm.py` does not define, so these
runs came from an earlier version of the harness than the one committed beside
them.

Per-game lines carry `arcprize.org` replay or scorecard URLs. That is
third-party-hosted evidence for a published number, which is a stronger artifact
than a committed results file — the reader is not asked to trust the repository's
own arithmetic. The Fable 5 file has no summary line; its 25 per-game scores
average 94.71%, beside the paper's 94.6% pass@1 for that configuration, and the
paper's 97.4% best@2 needs second runs that are not committed — the paper itself
calls it a lower bound, *"as several games were not rerun"*.

**What the paper reports and the repository does not let you rerun.** Paper v3
numbers against the pinned CLI:

| Result | Paper | Runnable from the pin |
| --- | --- | --- |
| No-log vs log, five runs, three models | §3.1, 41.2/24.0 for GPT-5.5 | yes — `--log-window -1`; one run per arm committed |
| Last 25 sections | Figure 4 | yes — `--log-window 25`; no run committed |
| Tool ladder, read → grep → Python → write | Table 2 | no flag; Claude Code's disallowed tools are a fixed list, Codex has none |
| Workspace cleared every call | Table 3, n = 2 | no flag; only `actions.json` is cleared |
| Compaction threshold 244K → 64K | Figure 5, Table 6 | no flag sets either client's compaction |
| NetHack lifetimes | §3.2 | no NetHack, NLE or BALROG code on any branch |
| Billed tokens, "4.2–5.8× fewer" | Figure 3 | the runner tallies per-call usage; no token totals are committed |

The architecture of the claim holds: the comparison the paper rests on is a flag,
and one run of each arm is committed with replay links. The ablations that explain
*why* it works — that Python, not grep, carries the gain, and that the agent's
notes add little once the log exists — are reported and not reproducible from the
published code.

## 11. Patterns Worth Stealing

### Steal

- **Make the ablation a flag, and ship the arm.** `--log-window -1` turns "does
  the memory help?" into a runnable configuration rather than an argument. Most
  memory systems in this atlas cannot be run without their memory, so nobody can
  price it.
- **Publish the budget-matched rerun.** When two arms differ in a second
  variable, re-score the flattering one under the stricter setting and commit
  both files. It costs a rerun and buys the only version of the claim that
  survives scrutiny.
- **Link the replay, not just the number.** A per-game URL on the benchmark
  operator's own site is evidence the repository cannot fabricate.
- **Tell the reader of a log to re-check it.** The installer's skill instructs
  the agent to verify recovered observations against the current workspace — one
  line that turns a history into evidence rather than belief.

### Avoid

- **An incremental sync keyed on the size of a file somebody else may write.**
  If the destination is writable by the party you are syncing to, the offset must
  come from your own bookkeeping, not from `stat()`.
- **Ablations that exist only in the paper.** Four of the paper's
  experiments have no switch in the published CLI. A reported ablation without
  the flag that produced it is a claim, not an artifact.
- **An instructions file the agent can edit, written once.** Codex's `AGENTS.md`
  is created if absent and never restored, so the system prompt for the rest of
  a game is whatever the agent last left there.

### Fit

Right for anyone building a long-horizon agent whose observations are
machine-generated and exactly checkable — grids, diffs, logs, traces. The whole
design rests on that: lexical recall over a verbatim record beats semantic recall
when the query is *"what did cell (43,17) hold at action 212"*, and no embedding
model can answer that better than `grep`.

Wrong as a memory component for anything where memories are claims about the
world. There is no correction path, no scope key, no trust state and no
provenance, and adding them would mean giving the log a schema — at which point
it stops being the thing that made it work. It is also wrong for a reader who
wants a library: this is a benchmark harness with four Docker images and an ARC
API key, and the transferable part is 200 lines and an idea.

## 12. Antipatterns / Risks

- **The sync-offset defect**, above. The highest-severity item, because it
  degrades the memory rather than breaking it: an agent gets a log with a hole in
  it and cannot tell.
- **No tombstone.** Nothing anywhere is keyed on a rejected value, so an agent
  that writes a refuted hypothesis into `notes.md` and later re-reads it has no
  mechanism preventing the mistake from returning.
- **Belief and observation in one undifferentiated stream.** The `[PLAN]` blocks
  the harness folds into the log are the agent's own guesses, stored beside board
  states with no marker.
- **The scope boundary is a directory.** Isolation is real — one workspace per
  game, one container — but it is a filesystem fact, not a stored key applied on
  a read path, so nothing survives a change in how runs are laid out.
- **No tests where the numbers are.** The npm tooling layer has a test file; the
  research harness the paper reports on has none on `main`, in a repository whose
  central claim is a measurement.
- **Published numbers from a harness that is not the committed one.** The
  GPT-5.5 scorecards name a flag the pinned CLI lacks, and most of the paper's
  ablation arms have no flag at all.
- **A self-ingestion guard that matches one spelling of a path.** `record` drops
  a tool event whose serialized input contains `.prolong/log.jsonl`; reaching the
  same file by another route records normally, and the committed case exercises
  only the spelling the guard checks.

## 13. Build-vs-Borrow Takeaways

Borrow the idea and none of the code. The transferable claim is that for
machine-generated, exactly-checkable observations, a verbatim append-only text
log plus a coding agent outperforms a summarizing memory — and it is supported
by a matched pair of committed runs rather than by assertion.

Build the three things the research harness does not have, in this order: a sync
whose offset you own, a marker separating what was observed from what was
inferred, and one test per parser. The first is a correctness bug, the second is
what turns the log into memory rather than a transcript, and the third is what
stops the first from recurring.

Do not borrow the deployment. Four images and a proxy exist because the benchmark
demands isolation, not because the memory does.

## 14. Open Questions

- **Which commit produced the paper's runs?** The committed GPT-5.5 scorecards
  name a `session-mode` setting the pinned harness does not have, and neither the
  README nor the paper names the code version behind a reported number.
- **What happens at window sizes other than 25 and full?** The flag accepts any
  positive N and the paper reports one intermediate point, so whether memory
  helps linearly or has a knee is unknown.
- **How was Codex's compaction threshold set?** The paper ablates it at 244K and
  64K; the pinned Codex backend passes no compaction setting and logs, on
  overflow, that *"Codex has no native compaction"*.

## Appendix: File Index

| Path | What it holds |
| --- | --- |
| `research/arc-agi-3/prolong_agent/agent/base.py` | Prompt assembly, `_sync_history` (the incremental sync, line 104), `_copy_truncated_log`, `actions.json` parsing |
| `research/arc-agi-3/prolong_agent/agent/claude_code_agent.py` | Claude Code backend, container pool, network flags, `CLAUDE.md` rewritten each call, session ids |
| `research/arc-agi-3/prolong_agent/agent/codex_agent.py` | Codex backend, `AGENTS.md` written once, `exec resume` |
| `research/arc-agi-3/prolong_agent/agent/codex_events.py` | Codex event parsing, including the overflow handler that drops the session |
| `research/arc-agi-3/prolong_agent/agent/prompts.py` | Both system prompts and the two no-log user-prompt templates |
| `research/arc-agi-3/prolong_agent/agent/swarm.py` | CLI, including `--log-window` and `--backend` |
| `research/arc-agi-3/prolong_agent/environment/runner.py` | The turn loop, `_log_action`, `_append_post_action_board`, `current_board.txt` |
| `research/arc-agi-3/prolong_agent/utils/sandbox_net.py` | Network isolation for the agent container |
| `research/arc-agi-3/scorecards/` | Four committed result files, including the 500-action rerun |
| `research/arc-agi-3/release_logs/fable5/` | 25 full workspaces — `logs.txt`, `logs_analyzer.txt`, `scorecard.json`, and the agent's `notes.md`, `actions.json`, `CLAUDE.md` |
| `research/README.md` | The paper's results tables, ARC-AGI-3 and NetHack |
| `src/` | The npm tooling layer — `init`, `status`, `uninstall`, one adapter per client |
| `templates/runtime.mjs` | The 63-line hook runtime that writes `.prolong/log.jsonl`, including the self-read guard |
| `templates/prolong/SKILL.md` | The skill that tells the agent to use the log as external memory and re-verify it |
| `tests/lifecycle.test.ts` | The repository's only test file, over the tooling layer |
| `LICENSE` | MIT, at the repository root |

## Appendix: Recorded Searches

Run from the root of the checkout at the pinned commit, with `/usr/bin/git`.

| Claim | Command | Result at this pin |
| --- | --- | --- |
| The research harness has no test | `git ls-files \| grep -E '(^\|/)(tests?\|.*_test\.py\|test_.*\.py)'` | `tests/lifecycle.test.ts` only, which imports `../src/init.js`, `../src/status.js`, `../src/uninstall.js` |
| `--log-window` is the only memory-ablation flag | `git grep -n 'add_argument' -- research/arc-agi-3/prolong_agent/agent/swarm.py` | 16 arguments; none for tools, workspace clearing, compaction, a baseline or a session mode |
| No flag or code path for the paper's removed modes | `git grep -n -E 'stateless\|session_mode\|clear_every\|compact_pct\|log_parser' -- '*.py'` | Nothing |
| No NetHack harness | `git grep -l -i -w -E 'nethack\|balrog\|nle' -- ':!*.md' ':!research/arc-agi-3/release_logs'`, and the same over each of the four other branches | Nothing |
| One truncation implementation | `git grep -n '_copy_truncated_log' -- '*.py'` | Defined at `base.py:152`, called at `base.py:109` |
| The self-read guard matches one spelling | read `templates/runtime.mjs:33-38` | `json(toolInput)?.includes(".prolong/log.jsonl")` — a substring test on the serialized input |
| No committed run's copy diverged from its master | for each `release_logs/fable5/*/rep1`, test that `logs.txt` starts with the bytes of `workspace/logs.txt` | 25 of 25 are prefixes |

## History

**2026-11-11** — [`d87233c9128d7b9dc5d780e83b4aeb8377dd8805`](https://github.com/alexisfox7/PRO-LONG/commit/d87233c9128d7b9dc5d780e83b4aeb8377dd8805) — the 18 commits since the previous pin touch only READMEs and figures, but the Python harness at that pin was 9,210 lines smaller than at the first reading, and the 2026-09-13 entry moved its paths without re-reading its prose. Sections 2, 4, 5, 7, 8, 9, 11, 12 and 14 described `--workspace stateless`, `--baseline`, `--log-window 0`, `--session-mode`, `log_parser.py` with `--resume`, `session_state.json` and a duplicated truncation helper, none present at either pin; they are rewritten against the code. The sync defect and the 25-run prefix check hold. The stateless ablation was called unreported; paper v1 already reported it, and v3 adds NetHack and an inventory of what is not runnable, in [section 10](#10-tests-evals-and-benchmarks). `negative_eval` stays.

**2026-09-19** — [`9d2f2d46fea8759ed494ce5b0166c7004a2e97c4`](https://github.com/alexisfox7/PRO-LONG/commit/9d2f2d46fea8759ed494ce5b0166c7004a2e97c4) — audited at the unchanged pin, which is still the tip of `main`; the last commit upstream is 20 August 2026. Nothing could have moved, so every error found here is this atlas's own. Two published claims were false, and both were checkable with one `ls`.

**There is a `LICENSE` file**, MIT, at the repository root. Section 1 and section 12 both stated that the grant was asserted by a trove classifier and absent as a file, and section 12 listed it as an antipattern. That is withdrawn in full, including the comparison to [Membase](../membase/), which is a different situation. A report telling readers a licence grant is missing is the most consequential kind of error this atlas can make, because it argues against reuse.

**There is a test file.** `tests/lifecycle.test.ts`, 144 lines, wired to `npm test`. The claim was true of `research/` — where the paper's numbers come from — and published over the whole repository. Section 10 is rewritten around the asymmetry that replaces it.

`negative_eval` is **added**. The test's centre is a must-not case over the installed runtime: the agent is made to grep its own memory and the log is asserted not to have grown, *"reading the memory log must not copy it back into itself."* Reading the guard behind it added a finding of its own — it is a substring match on one spelling of the path, so `cd .prolong && rg x log.jsonl` records normally. Section 8 gains the runtime's write mechanism; the appendix gains the searches that should have grounded both original claims.

**2026-09-13** — [`9d2f2d46fea8759ed494ce5b0166c7004a2e97c4`](https://github.com/alexisfox7/PRO-LONG/commit/9d2f2d46fea8759ed494ce5b0166c7004a2e97c4) — re-read, 18 commits past the previous pin and a restructuring: 256 files changed, 3,709 lines added against 9,841 removed. The ARC-AGI-3 implementation moved wholesale under `research/arc-agi-3/`, so every path in the appendix gained that prefix, and a TypeScript installer for coding CLIs arrived beside it, described in section 4. Two published claims are corrected. `consume_clear_tombstone` at `base.py:97` no longer exists — it and `clear_session` were replaced by a `_clear_files` helper, and the word `tombstone` appears nowhere in the tree — so the observation that the word was taken for session-clearing is recorded as the repository's own history rather than as current state. The mark itself is unaffected: nothing is keyed on a rejected value, and `capabilities` stays empty. The paper the report already cites, [arXiv:2607.20064](https://arxiv.org/abs/2607.20064), now has a `CITATION.cff` and a README badge beside it. Screened again first; nothing was installed and no suite was run.

**2026-08-12** — [`e30ac528c68b66abd68c802424d3724a85e927a8`](https://github.com/alexisfox7/PRO-LONG/commit/e30ac528c68b66abd68c802424d3724a85e927a8) — first reading. The screen reported one auto-run surface, an empty `.gitmodules`, and a `uv.lock` unchanged for 158 days; nothing was installed and nothing in the tree was executed. The sync defect in section 9 was verified by re-deriving the routine over a scratch file pair, without importing the repository, and then checked against the 25 committed runs — in every one the agent's `workspace/logs.txt` is an exact byte prefix of the host master, so the defect is latent rather than realised.

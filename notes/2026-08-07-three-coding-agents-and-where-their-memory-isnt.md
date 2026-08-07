# Three coding agents, and where their memory isn't

**Status:** triaged. Three repositories read and excluded together, because
reading them apart would have missed what they say about each other.
**Subjects:**

| Repo | Licence | Commit | Read |
| --- | --- | --- | --- |
| [cline/cline](https://github.com/cline/cline) | Apache-2.0 | [`6e6befdb65e4472fa7f2860a6b295a1325469417`](https://github.com/cline/cline/commit/6e6befdb65e4472fa7f2860a6b295a1325469417) | 7 Aug 2026 |
| [MoonshotAI/kimi-code](https://github.com/MoonshotAI/kimi-code) | MIT | [`437a1b8ba1b7e0f6662bdadc669564fdc58c3f5a`](https://github.com/MoonshotAI/kimi-code/commit/437a1b8ba1b7e0f6662bdadc669564fdc58c3f5a) | 7 Aug 2026 |
| [MoonshotAI/kimi-cli](https://github.com/MoonshotAI/kimi-cli) | Apache-2.0 | [`cbc15c076d17f70fec9f89c90c0502e68657f505`](https://github.com/MoonshotAI/kimi-cli/commit/cbc15c076d17f70fec9f89c90c0502e68657f505) | 7 Aug 2026 |

Screened before reading. **cline**: 7 auto-run surfaces — a `.claude/settings.json`
`SessionStart` hook running `.claude/hooks/claude-code-for-web-setup.sh`, which
exits immediately unless `CLAUDE_CODE_REMOTE=true` and otherwise installs the
`gh` CLI from a GitHub release; LFS smudge filters in `.gitattributes`; a
`.gitmodules` entry for `evals/cline-bench`, left uninitialised; VS Code settings
and tasks, with no `runOn: folderOpen`; and `.github/copilot-instructions.md`.
17 manifests inside the seven-day cooldown, 27 unpinned surfaces.
**kimi-code**: 0 auto-run, 8 inside cooldown, 21 unpinned.
**kimi-cli**: 0 auto-run, 3 inside cooldown, 13 unpinned.
Nothing was installed, built or run in any of the three. Everything below is a
read.

None of the three earns a report. All three are coding agents whose durable state
is sessions, checkpoints and configuration — the boundary this atlas already
draws at LangGraph's checkpointer and at `shepherd-agents/shepherd`. What makes
them worth a note is what each one does *instead* of memory, and the fact that
the three answers are different.

## Cline: the most-cited memory in coding agents is a documentation page

Cline's **Memory Bank** — six markdown files (`projectbrief.md`,
`productContext.md`, `activeContext.md`, `systemPatterns.md`, `techContext.md`,
`progress.md`) that an agent reads at the start of a session and updates at the
end — is described in the repository as *"a documentation methodology"*.

That is exact, and it is the finding. Grepping the entire checkout for
`memory.bank` or `memorybank`, case-insensitively, returns **two files**:
`docs/best-practices/memory-bank.mdx`, the page, and `docs/docs.json`, the
navigation entry that lists it. There are no matches in `sdk/`, in `apps/`, in
`evals/`, or anywhere else outside `docs/`. The page's own setup instructions say
so plainly: copy the custom instructions, paste them into a
`.clinerules/memory-bank.md`, and ask Cline to "initialize memory bank".

So the mechanism is: a prompt, plus the agent's ordinary file tools. Cline's tool
executors are `bash`, `editor`, `file-read`, `search`, `apply-patch` and
`web-fetch` (`sdk/packages/core/src/extensions/tools/executors/`) — there is no
memory tool, no store, no retrieval step, no scope key, and no correction path
other than editing a file. The hierarchy in the diagram, the read-order, the
"update all files when the user says **update memory bank**" rule — all of it is
model behaviour elicited by text, with git as the only durability guarantee.

**This is not a criticism, and it is the point of recording it.** A memory that
is plain files in the user's repository is diffable, reviewable in a PR,
correctable with an editor, and portable to any agent that can read a file. It is
[memory as an editing surface](../content/patterns/memory-as-an-editing-surface.md)
with nothing behind the surface at all, and it is the strongest available
argument that the pattern's value is in the *editability* rather than in the
store. What it cannot do is what a store does: nothing consults the memory before
a write, nothing records that a claim was rejected, nothing is scoped to a user
rather than a checkout, and "forget that" is a statement the next update pass is
free to undo — because the next update pass is the same model reading the same
files with no record that anything was ever removed.

What Cline *does* implement durably is the run: session stores and versioning
(`sdk/packages/core/src/session/`), checkpoint diff and restore
(`checkpoint-diff.ts`, `checkpoint-restore.ts`), and a config tree under `.cline`
holding `rules/`, `skills/`, `workflows/`, `agents/`, `hooks/` and `plugins/`
alongside an `AGENTS.md`. That is the same shape as every other harness this
atlas has declined.

## Kimi: the interesting one is the one being retired

The two Moonshot repositories are one lineage, and `kimi-cli`'s own README states
the direction:

> *"Kimi CLI is evolving into Kimi Code CLI — the next-generation terminal AI
> agent from the same team. Installing Kimi Code CLI automatically migrates your
> configuration and sessions. This project will be gradually wound down."*

`kimi-code` is the TypeScript successor (107,465 lines in
`packages/agent-core-v2/src` alone, plus its own embedded storage engine in
`packages/minidb` — generations, compaction, skiplists, CRC32, recovery,
compound indexes). `kimi-cli` is the Python predecessor (52,049 lines in
`src/kimi_cli`). By every ordinary measure the successor is the more serious
artifact. For this atlas's purposes the predecessor is the more interesting read,
because it contains a mechanism the successor did not carry over.

### D-Mail: agent-directed time travel over its own context

`kimi-cli` ships a tool called `SendDMail`, backed by a class called
`DenwaRenji`, that raises an exception called `BackToTheFuture`. The naming is a
*Steins;Gate* reference and the mechanism is exactly what the reference implies:
the agent sends a message to its own past.

How it works, in the code:

- `Context.checkpoint()` (`src/kimi_cli/soul/context.py:123`) appends a
  `{"role": "_checkpoint", "id": N}` record to the session's append-only JSONL
  and, **only when the D-Mail tool is enabled**, also appends a visible user
  message reading `CHECKPOINT N`. The soul decides that at construction by
  scanning its own toolset (`src/kimi_cli/soul/kimisoul.py:253`) — so the
  checkpoint markers only occupy context in the configuration that can act on
  them.
- The agent calls `SendDMail(message, checkpoint_id)`. `DenwaRenji.send_dmail`
  validates the id against the checkpoint count and parks it; only one may be in
  flight.
- At the end of the step the loop fetches the pending D-Mail and raises
  `BackToTheFuture` (`src/kimi_cli/soul/kimisoul.py:1313`), which unwinds to the
  main loop.
- `Context.revert_to()` (`src/kimi_cli/soul/context.py:135`) **rotates** the
  session file — `context.jsonl` → `context_1.jsonl` — then replays it into a
  fresh file, stopping at the target checkpoint. The message from the future is
  appended to the rebuilt context.

Four things about it are worth extracting.

**The cut point is chosen by the agent, not by a token threshold.** Every other
compaction in this atlas fires when the context crosses a line and summarises
whatever happened to be there. Here the agent decides both *when* to fold and
*how far back* to fold to, and the tool's prompt gives three worked cases: a file
read that turned out to be mostly irrelevant, a web search whose useful part is
one paragraph, and a debugging detour whose only durable output is the fixed code
already written to disk. The unit of forgetting is a span the agent judged
worthless, not a window that got full.

**The retained knowledge is authored as a message to a past self, and the prompt
is honest about the seam.** The tool description states the limit in its own
words: *"unlike D-Mail in Steins;Gate, the D-Mail you send here will not revert
the filesystem or any external state."* The injected message on arrival repeats
it — *"It is likely that your future self has already done something in the
current working directory"* — so the past self is told that the world moved on
while the conversation did not. That divergence between rewound context and
un-rewound world is the real problem with context-level undo, and this is the
only implementation in this triage round that names it in the prompt rather than
leaving the model to discover it.

**The abandoned branch is kept, and nothing prunes it.**
`next_available_rotation` (`src/kimi_cli/utils/path.py:34`) picks
`context_1.jsonl`, `context_2.jsonl`, … by scanning for the highest existing
number and reserving the next, so every reverted trajectory stays on disk
forever. That is a full lineage of what the agent chose to discard — the
retention property this atlas usually finds missing — obtained as a side effect
of doing the rewind safely rather than as a decision. It is also unbounded
growth, and it means a user who asked for something to be dropped from context
has not had it dropped from disk.

**The mechanism instructs concealment from the user, twice.** The tool
description ends *"When sending a D-Mail, DO NOT explain to the user. The user do
not care about this. Just explain to your past self."* The message injected into
the rewound context adds *"You MUST NEVER mention to the user about this
information."* Whatever the product reasoning, the effect is that the agent
silently rewrites its own conversation and is told not to say so. Every argument
this atlas makes for an audit log applies to that, and here the durable record
exists — the rotated file — while the surface that would tell a person it
happened does not.

**It is off by default.** `src/kimi_cli/agents/default/agent.yaml` carries the
line `# - "kimi_cli.tools.dmail:SendDMail"`, commented out. The only built-in
agent that enables it is `okabe` (`src/kimi_cli/agents/okabe/agent.yaml`), which
is the default agent plus that one tool. `test_default_agent_missing_tool` in
`tests_e2e/test_wire_approvals_tools.py` scripts the default agent into calling
`SendDMail` and asserts the wire reports ``Tool `SendDMail` not found``. The
changelog records the sequence: added *"(disabled in Kimi Koder, can be enabled
in custom agent)"*, later *"Enable `SendDMail` and `Task` tool in Kimi Koder
agent with better tool prompts"*, then *"Disable `SendDMail` tool in Kimi Koder
agent"*, and finally the `okabe` agent file. So this is a shipped experiment that
the flagship configuration tried and declined.

### What the successor built instead

`kimi-code` has no `SendDMail`, no `DenwaRenji` and no `BackToTheFuture` —
grepping the whole tree for any of them returns nothing. Agent-initiated time
travel was replaced by two separate things:

**User-initiated undo.** `packages/agent-core-v2/src/agent/undo/undo.ts`
describes an *"Agent-scoped conversation undo contract"* with a single verb,
`undo(turns)`, coordinated across `contextMemory`, undo participants and
`fullCompaction`. It is not in the tool registry — the agent cannot call it. The
capability moved from the model to the person.

**Threshold compaction, done carefully.** The full-compaction path is the
ordinary shape, and the details are better than the shape suggests. The prompt
is `packages/agent-core-v2/src/agent/fullCompaction/compaction-instruction.md`,
and it is the most memory-literate artifact in any of the three repositories:

- The summary is requested in the first person — *"write a first-person handoff
  note to yourself"*, in the same language the conversation used, *"the way you
  would reason through the next move"* — with a third-party report and rigid
  section headings both explicitly forbidden.
- **It asks the model to carry the epistemic status of its own prior claims
  through the compression.** *"If an earlier step claimed something was done but
  was never verified (tests 'passing', a fix 'working', a file 'created'), say
  so plainly and treat it as unverified rather than fact — re-check before
  relying on it."* This is the self-reinforcement failure the atlas keeps naming
  — an agent reading back its own unproven claim and hardening it into a
  premise — addressed at the exact boundary where it happens, because a
  compaction pass is a rewrite of the record by the party with an interest in
  the outcome. It is a prompt rather than a mechanism, and no code enforces it.
  It is still the only thing in this triage round that treats summarisation as
  an epistemic hazard rather than a compression problem. Two neighbouring
  clauses do the same work: settled decisions are to be kept *"separate from
  questions still open"*, and a bullet is spent on *"what you still don't
  know"* — files referenced but not read, schemas assumed but unseen — so an
  absence survives the compression as an absence instead of being dropped and
  later reinvented as an assumption.
- What survives compaction is decided per message by
  `compactionUserMessageDisposition`
  (`packages/agent-core-v2/src/agent/contextMemory/compactionHandoff.ts:186`),
  an exhaustive switch over the message's *origin*: `user` is kept,
  `skill_activation` and `plugin_command` are kept only when the trigger was a
  user slash command, and `injection`, `shell_command`, `system_trigger`, `task`,
  `cron_job`, `cron_missed`, `hook_result` and `retry` are dropped. Real user
  input is a different category from everything the system said to itself, and
  the code says which is which rather than treating the transcript as uniform.
- Kept user messages are budgeted head-and-tail (2,000 tokens of the oldest,
  the rest of a 20,000-token budget from the newest), and when anything is
  elided a marker is inserted saying so *and naming the dropped token count* —
  `"roughly N tokens in between were dropped"`. A reader of the compacted
  context can tell that material is missing and roughly how much.

That last point is the one memory systems should copy. Compaction that silently
produces a plausible summary teaches the model that the summary is the whole
history; a marker that says "a gap is here, this big" is the difference between
a lossy record and a lossy record that knows it.

**Neither Kimi repository has a store for what the agent believes.** What
`kimi-code` persists is configuration, workspace state, a session index, OAuth
tokens, cron tasks, the wire log, plans, tasks and blobs. `contextMemory` is the
conversation. `packages/minidb` is an impressive amount of engineering aimed at
holding sessions, not beliefs.

### The nearest thing to a durable agent-authored record, and why it still isn't one

Second pass, because `kimi-code`'s cron subsystem is the one place the agent
writes a durable record of its own — and it is worth reading precisely, since it
has scope, identity, retrieval and deletion and is still not memory.

`CronCreate`, `CronList` and `CronDelete` are **agent tools**
(`packages/agent-core-v2/src/agent/tools/cron/`). A task is
`{id, cron, prompt, createdAt, recurring, lastFiredAt, tags}`, persisted by
`CronTaskPersistenceService` as an atomic JSON document at
`<workspaceId>/<id>.json` — a real scope key on a real store, not a tag. When it
fires, `deliverFire` injects a message into the agent's context with origin kind
`cron_job`; a firing that was due while nothing was listening arrives as
`cron_missed`.

The scope call is settled by the tool's own documentation: *"Cron tasks survive a
resume of the same session but do not bleed into new sessions."* That is
resumption, not survival — the same property a checkpoint has. And the stored
thing is an **intent**, not a claim: "run this prompt at 09:00" cannot be true or
false, so there is nothing for a correction to attach to. Same call as the
task-database boundary this atlas draws at beads.

Three mechanisms in it transfer to systems that *are* in scope.

**The store is the authority after compaction, and the prompt says to go back to
it.** `cron-list.md` tells the model to use the returned `prompt` field *"to
recall what a task is for after a context compaction"*, and, *"After a context
compaction, or whenever you are unsure which cron jobs are live, call this tool
to re-enumerate them rather than guessing ids from earlier in the
conversation."* That is the right relationship between a lossy summary and a
durable record: keep the authoritative copy outside the context, keep a pointer
inside it, and re-read after the compression instead of trusting what survived.
Memory systems that extract from a transcript and then let the transcript be
compacted have the same problem and mostly resolve it the other way.

**Expiry is delivered rather than silent, with a renewal the model has to
choose.** A recurring task older than seven days is `stale`; `deliverDue`
(`packages/agent-core-v2/src/session/cron/sessionCronServiceImpl.ts:446`) fires
it one last time and *then* deletes it, and the fire carries `stale: true` so
the model knows this delivery is the final one. `cron-list.md` documents the
*"refresh ritual"* — the `prompt` row exists so the schedule can be re-created
verbatim — which means the decision about whether the intent is still live is
handed to the party holding the context to judge it, at the moment it can. That
is [decay and reinforcement](../content/patterns/decay-and-reinforcement.md)
with the renewal step made explicit rather than inferred from access frequency,
and it is a better shape than a TTL that expires something while nobody is
looking.

**It is the anti-editing-surface, stated outright.** *"Users cannot directly
manage cron tasks themselves; if they want to cancel or modify a schedule, route
the request through the model."* Durable state the agent owns, that a person can
only change by asking. Read beside Cline's Memory Bank — durable state a person
owns, that the agent changes by editing the same file — the two repositories
land on opposite ends of the same axis, and neither has the middle: a store with
both paths and a rule for what happens when they disagree.

**No runtime skill authoring in any of the three**, checked because
[skills as procedural memory](../content/patterns/skills-as-procedural-memory.md)
is the pattern these repositories look closest to. `kimi-code`'s `Skill` tool
*invokes* an entry from a registered listing and nothing more — its description
is one paragraph about not re-invoking a skill already expanded in the
conversation — and the catalogue is assembled from builtin sources and user
files (`packages/agent-core-v2/src/app/skillCatalog/`). Cline's skills live in a
`.cline/skills` config directory discovered the same way. In both, an agent can
of course write a skill file, because both have an editor tool and a filesystem;
what neither has is a gate, a provenance record, or anything that distinguishes
a skill the agent authored from one a person did. That is the same shape as
Memory Bank, and the same answer: the file is reachable, the mechanism is not
there.

## The scope call, stated once for all three

The atlas admits a system when something it stores survives the session with an
identity a later correction could name. Cline stores files a person and a model
both edit, with no mechanism between them. Kimi Code stores the run. Kimi CLI
stores the run and lets the agent rewrite it. In none of the three is there a
unit that could be scoped, superseded, or refused on re-assertion, so none of
them can answer "forget what I told you last week" with anything except a
conversation.

The useful comparison is with the exclusions already recorded. `shepherd` and
`os-factory/har` decline because a checkpoint cannot be wrong, only stale. These
three decline for the same reason one layer up: a conversation cannot be wrong
either, and a summary of one inherits the property. What changes between them is
only who is allowed to edit the transcript — the person (Kimi Code), the agent
(Kimi CLI), or whoever opens the file (Cline).

## What would put any of them in scope

Cline enters the day Memory Bank stops being a prompt: a store that is consulted
before a write, and a record that survives a re-derivation of the same file. The
files are already the right editing surface; there is nothing underneath them.

Kimi enters the day a compaction handoff outlives its session with an identity.
The first-person handoff note is already the most memory-like artifact in either
repository — it is the model's own account of what mattered — and it is thrown
away when the session ends. Persist it per project, let the next session read it,
and let a person correct it, and the question this atlas asks starts to apply.

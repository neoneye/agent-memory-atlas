# A coding agent whose search is the user's, not the model's

**Status:** examined, excluded, no report. Recorded because it is the clean
contrast to a system the atlas *does* have a report for, and the line between
them is the whole distinction.
**Subject:** [MoonshotAI/kimi-code](https://github.com/MoonshotAI/kimi-code),
Kimi Code CLI, read on 2026-08-14 at
[`13d86f8b7bb2443a3b8222e7d94deb0a66429f8e`](https://github.com/MoonshotAI/kimi-code/commit/13d86f8b7bb2443a3b8222e7d94deb0a66429f8e),
MIT, ~410,000 lines of non-test TypeScript across 17 packages.

Screened before reading: dependency surfaces inside the seven-day cooldown and
the ordinary build-time surfaces of a large pnpm monorepo, `pnpm-lock.yaml`
present, a `CLAUDE.md` and an `AGENTS.md` read as data. Nothing installed or run.

## The vocabulary looks like a memory system and is not

A first grep is misleading in exactly the way the atlas warns about: `memory`
appears 585 times, `persist` 272, `compaction` 1409, `checkpoint` 139, `sqlite`
21, `embedding` 28. None of it is agent memory in this atlas's sense, and
tracing each surface is what settles it.

- **`agent-core-v2/src/agent/contextMemory/`** is the largest `memory` consumer
  and it is conversation-window management: its own docstring says it "owns
  per-agent conversation history," and its operations are `append`,
  `applyCompaction`, `undo`, `clear`, `publishTrailingRemoval`. That is the
  context the model reasons over this turn, spliced and compacted and rebuilt on
  replay — nothing survives the session as a claim.
- **Sessions** are persisted to `wire.jsonl` and a `minidb` query store, with
  replay and resume. That is session state — the same category as the LangGraph
  checkpointer the atlas treats as resume-scoped, not memory.
- **`minidb`** is the interesting infrastructure and still not memory: a genuine
  embedded database — WAL, generation checkpoints, compaction, a trigram text
  index, a skiplist, worker-thread isolation. It exists to persist and index
  sessions, not to hold beliefs.
- **`AGENTS.md`** is generated once by the `/init` slash command, which hands a
  verbatim brief to a `coder` subagent that analyses the codebase and writes the
  file; the result is read back into the system prompt. It is project
  instructions, not an accumulated store, and nothing consults-before-writing it
  or corrects it as memory. The `agentsMdReminder` domain only nudges the agent
  when a tool touches a path covered by an `AGENTS.md` that was not injected.

Nothing stored is a claim that could be false and later corrected. The scope
call is the same one made for the coding agents in
[three coding agents and where their memory isn't](2026-08-07-three-coding-agents-and-where-their-memory-isnt.md):
a harness that persists runs is not a memory that holds beliefs.

## Why it is worth recording: the DeepSeek Harness line

Kimi Code has **cross-session full-text search** —
`kap-server/src/search`, an `IGlobalSearchService` whose own comment reads
*"Cross-session full-text search over user messages, assistant text and session
titles, backed by a single minidb database at `<homeDir>/search-index`."* It has
a background sync coordinator, published index generations, page tokens
invalidated on a shrink rescan — real retrieval infrastructure over the durable
session corpus.

That is, on its face, the [DeepSeek Harness](../content/systems/deepseek-harness/)
shape: a coding agent whose session log is a searchable corpus. DSH is *in* the
atlas. Kimi Code is not, and the single fact that separates them is **who holds
the search.**

- DSH registers `session_search`, `session_event_search` and three more as
  **model-facing tools** (in a package no shipped bundle mounts, and behind an
  `openAt: never` default — but they exist, and the model is their caller). The
  agent can query its own history. That is a memory affordance, which is why DSH
  is analysed.
- Kimi Code's search is an **app-server service for the UI**. The service lives
  in `kap-server` (the server behind the desktop/web app), it is described as a
  "temporary feature… until it graduates into agent-core-v2," and the agent's
  own tool registry —
  `agent`, `ask-user-question`, `cron`, `edit`, `fetch-url`, `goal`, `os`,
  `read-media-file`, `select-tools`, `skill`, `task`, `todo-list`, `web-search`
  — contains **no memory, recall, or session-search tool at all.** The human can
  search their past sessions in a search box. The model cannot.

So the line the atlas has been drawing between *"a searchable session corpus
that is agent memory"* and *"searchable session history that is a product
feature"* is exactly whether the model can query it, and these two repositories
sit on opposite sides of it with almost identical machinery underneath. That is
the sharper statement of the [DSH correction](../content/overview.md#known-limitations)
from earlier this week — there, the finding was that DSH ships its model-facing
search disabled; here it is that a superficially identical search was never
pointed at the model in the first place, by design, because its audience is the
user.

## The reading rule this reinforces

The same three-step rule the
[Cordis note](2026-08-14-the-framework-that-explains-the-deepseek-correction.md)
proposed applies to memory-vocabulary as much as to plugin composition: a large
`memory`/`persist`/`search` hit count is a prompt to trace each surface to its
*caller*, not evidence of a memory system. The deciding question for a coding
agent with cross-session storage is not "is there a searchable corpus" but "is
the model given the search." Grepping the agent's tool registry answers it
faster than reading the storage engine — thirteen tool directories, and none of
them is the one that would make this in scope.

## Disposition

No report, no card, no counts change. Recorded in the overview known-limitations
list beside `os-factory/har`, `Untrivial-ai/agent-orchestrator` and
`perplexityai/numbat`, with the DSH contrast as the reason it is worth naming
rather than passing over. If a future release exposes session search or a
`remember`/`recall` tool to the model — the "graduate into agent-core-v2" the
search service's own comment anticipates — that flips the scope call, and this
becomes a report rather than a list entry.

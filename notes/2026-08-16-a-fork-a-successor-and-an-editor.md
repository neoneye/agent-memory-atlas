# A fork, a successor, and an editor

**Status:** triaged. Three coding agents read and excluded. One of them —
Cline — was already excluded on 7 August; it is here because the exclusion had a
re-entry condition attached and the condition is checkable.

| Repo | Licence | Commit | Read |
| --- | --- | --- | --- |
| [Zoo-Code-Org/Zoo-Code](https://github.com/Zoo-Code-Org/Zoo-Code) | Apache-2.0 | [`e064cf0592cfc70735d86feff77f1265637697ae`](https://github.com/Zoo-Code-Org/Zoo-Code/commit/e064cf0592cfc70735d86feff77f1265637697ae) | 16 Aug 2026 |
| [cline/cline](https://github.com/cline/cline) | Apache-2.0 | [`8bbdde2a5c1f972864fe1b954f639c21fac61a40`](https://github.com/cline/cline/commit/8bbdde2a5c1f972864fe1b954f639c21fac61a40) | 16 Aug 2026 |
| [Aider-AI/aider](https://github.com/Aider-AI/aider) | Apache-2.0 | [`5dc9490bb35f9729ef2c95d00a19ccd30c26339c`](https://github.com/Aider-AI/aider/commit/5dc9490bb35f9729ef2c95d00a19ccd30c26339c) | 16 Aug 2026 |

Screened before reading. **Zoo Code**: 3 auto-run surfaces — LFS smudge filters
in `.gitattributes`, VS Code settings and tasks with no `runOn: folderOpen` — an
`npm` `preinstall` *and* `install` lifecycle both running
`scripts/bootstrap.mjs`, a `prepare` running husky, one manifest changed the day
of the reading, and 84 floating ranges across seven manifests with no lockfile
beside them. **Cline**: the same seven auto-run surfaces recorded on 7 August,
including the `.claude/settings.json` `SessionStart` hook, plus manifests inside
the cooldown. **Aider**: no auto-run surface, no build-time execution, five
unpinned requirements. Nothing was installed, built or run in any of the three.
Everything below is a read.

None of the three earns a report, and the three failures are usefully different.

## Zoo Code: the management layer Cline's Memory Bank does not have

Zoo Code is the continuation of Roo Code — the README says so and the package is
still `roo-code` internally — which makes it a fork of a fork of Cline. Its
durable state falls into three piles, and none of them is a belief store.

**A codebase index.** `src/services/code-index/` is a real subsystem — embedders,
a vector store, a cache manager, a state manager, an orchestrator, a search
service. It is a semantic index *of the user's source*, regenerated from the
source, which is the boundary this atlas already drew for
`DeusData/codebase-memory-mcp`, `VectorSpaceLab/general-agentic-memory` and
`ShamGaneshan2008/Kodiak`. An index that can be deleted and rebuilt from the
thing it indexes cannot hold a wrong belief; it can only be out of date.

**Task history.** `src/core/task-persistence/TaskHistoryStore.ts` plus
`src/core/checkpoints/` — the run, versioned and restorable. Same call as
LangGraph's checkpointer and `shepherd-agents/shepherd`.

**Rules and skills, and this is the part worth writing down.** Cline's Memory
Bank was excluded because it is *"a prompt plus ordinary file editing"* — six
markdown filenames named in a documentation page, with git as the only durability
guarantee. Zoo Code's equivalent surface has an actual management layer, and it
is a better-built one than the phrase "just markdown files" suggests:

- `src/services/rules/rules.ts` exposes a typed CRUD API — `getRules`,
  `createRule`, `deleteRule`, `resolveRuleFile`, `getRulesDirectoryPath` — over
  `RuleMetadata` records carrying a stable id built from
  `(scope, kind, modeSlug, relativePath)`.
- Records are **scoped**: `global` and `project` bases, each split into generic
  rules and per-mode `rules-<slug>` directories, walked to a bounded depth with a
  filename pattern enforced on write.
- Resolution is **containment-checked twice** — `assertPathInsideDirectory` on
  the resolved path and `assertRealPathInsideDirectory` after an `lstat` that
  accepts symlinks — so a rule cannot be made to escape its scope through a link.
  That is the same shape this atlas credits `agent-framework` with, applied to
  configuration rather than to memory.
- `SkillsManager.ts` does the same for skills: `createSkill`, `deleteSkill`,
  `moveSkill`, `updateSkillModes`, global/project/mode sources, and file watchers
  that re-discover on change.

So the surface has identity, scope, enforcement, and lifecycle. What it does not
have is an author other than the person. Every caller of `createRule` and
`deleteRule` arrives from `webviewMessageHandler.ts` — a click in the UI. The
agent's tool list is `ReadFileTool`, `WriteToFileTool`, `EditFileTool`,
`ApplyDiffTool`, `SearchAndReplaceTool`, `ExecuteCommandTool`, `SkillTool` and
the rest; `SkillTool` *invokes* a skill and never writes one. Nothing the agent
concludes enters the store except through the same generic file-write it could
aim at any path.

**That makes it configuration, not memory, and the distinction is the whole
scope call.** A rule the user wrote cannot be wrong in the sense this atlas
means. It can be outdated, and the user edits it; there is no proposition the
system formed, no state that could be candidate rather than believed, and nothing
a re-derivation could re-assert because nothing derives it. Zoo Code is further
along than Cline on every axis except the one that matters.

## Cline: the re-entry condition, checked

The 7 August exclusion named what would reverse it: *"Cline enters the day Memory
Bank stops being a prompt: a store that is consulted before a write, and a record
that survives a re-derivation of the same file."*

At `8bbdde2`, a week and roughly a hundred commits later, grepping the whole
checkout for `memory.bank` or `memorybank` case-insensitively still returns
exactly two files: `docs/best-practices/memory-bank.mdx` and the `docs/docs.json`
navigation entry listing it. The two other paths containing `memor` are
`apps/vscode/src/standalone/memory-monitor.ts`, which logs process RSS every five
minutes, and `apps/cli/src/connectors/stores/memory-state.ts`, whose
`InMemoryStateAdapter` is a `Map` of values, lists, queues and locks with
`expiresAt` timestamps — process-lifetime state behind a `StateAdapter`
interface, and the in-memory sibling of a persistent adapter rather than a memory
system.

The condition is not met. The exclusion stands, and the recorded commit moves.

## Aider: the transcript does cross the session, and that is not enough

Aider is the cleanest test of the boundary because it genuinely persists
something across sessions and still does not qualify.

`.aider.chat.history.md` is written continuously, and `--restore-chat-history`
(default `False`) reads it back: `base_coder.py:519` splits the markdown into
messages, assigns them to `done_messages`, and calls `summarize_start()`.
`ChatSummary` in `history.py` then recursively summarizes from the oldest end
until the tail fits a token budget. A previous session's conversation therefore
reaches a later session's context, compressed.

That is a transcript and a summary of one. It has no unit, no identity, no
status; two sessions that contradict each other produce a summary containing
both, and there is no operation that means "this was wrong". The existing note
put it in one line — *a conversation cannot be wrong either, and a summary of one
inherits the property* — and Aider is the instance where the sentence has to do
real work, because the artifact does outlive the session.

The other durable thing is `repomap.py`'s `.aider.tags.cache.v<N>` — tree-sitter
tags per file, invalidated on mtime, ranked by a personalized PageRank over the
identifier graph to build the map that goes in the prompt. A derived index of the
user's source, deleted and rebuilt at will. Same call as Zoo Code's code index.

Nothing in `aider/` names a store of facts, preferences or conclusions.
`CONVENTIONS.md` is documented as a file the user adds to the chat with
`--read`, which is a prompt input.

## What the three say together

The Cline note asked what each agent does *instead* of memory and found three
different answers. These three converge on one: **all of them have solved the
editing surface and none of them has built anything underneath it.** Zoo Code has
the best surface in the group — scoped, id-bearing, containment-checked,
watched — and it is the clearest demonstration that a good editing surface is not
a memory system. The properties the atlas asks about are all properties of what
sits *behind* the file: whether a write consults what was rejected, whether a unit
has a status, whether a correction survives the next derivation. A CRUD API over
markdown answers none of them, however well built.

The re-entry conditions are unchanged for Cline and are the same for the other
two. Zoo Code enters the day the agent writes a rule and something decides
whether to keep it. Aider enters the day a restored history stops being a
transcript and becomes a set of claims a later session can contradict.

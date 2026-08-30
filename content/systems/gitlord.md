---
title: "GitLord"
eyebrow: "Git as the agent's event log"
description: "Every agent turn is a commit and every session is a branch, so history is inspectable, forkable and replayable — with the retrieval index built as a projection the code can rebuild from the log."
root: ../..
page_kind: system
source_name: "yashneil75/gitlord"
source_url: https://github.com/yashneil75/gitlord
revision: 42b0bab151777c1ee38ced7ab2805b0699e7a8a1
revision_url: https://github.com/yashneil75/gitlord/commit/42b0bab151777c1ee38ced7ab2805b0699e7a8a1
analyzed_at: 2026-07-30
capabilities: ""
stack_storage: "files"
stack_retrieval: ""
stack_source: "seeded"
matrix:
  memory_unit: "A turn — user, assistant or tool call — committed as JSON on a branch, addressed by commit sha and path"
  storage: "A git repository. Sessions are branches; the commit graph is the durable record"
  retrieval: "A `ContextAssembler` over the turn history with a dedup index and a per-branch context cache, plus a RAG module"
  write: "`append_turn` and its typed variants commit; `_commit_turn` can rebuild a chain onto a new parent"
  update_delete: "Git's own semantics — a rewritten chain is a new set of commits, and the old objects remain until they are collected"
  scoping: "A branch per session; nothing composes a scope key into a retrieval predicate"
  integration: "A CLI, an MCP server, and a LiteLLM-backed model layer with a tool-schema translator"
  background: "None"
  trust: "None. A turn is what happened; there is no claim, status or confidence anywhere"
  strengths: "A durable log that is inspectable, forkable and replayable by construction, with the derived index rebuildable from it"
  risks: "It stores what was said rather than what is believed, so nothing distinguishes a fact from a correction of it"
---

## 1. Executive Summary

GitLord's pitch is one line: *"Git for AI Agents. GitLord turns Git into a
database for autonomous agents. Every agent action becomes a version-controlled
event — inspectable, replayable, forkable."* MIT-licensed, 3,263 lines of Python
across a git layer (602), context assembly (361), sessions (321), an MCP server
(295), a model layer (292), a CLI (243) and RAG (234), with 233 tests.

A `Session` is a branch. `append_user_turn`, `append_assistant_turn` and
`append_tool_call_turn` each commit a turn as JSON. `_commit_turn` carries a
nested `rebuild(old_parent)` so a chain can be re-parented, which is what makes
forking a session and replaying it onto a different history a first-class
operation rather than a manual git exercise.

**The mechanism this atlas cares about is `DedupIndex.rebuild_from_log`.** The
index that makes retrieval fast is a *projection*, and the code can regenerate it
by walking the commit log and reading each turn's JSON back out. That is the
[evidence before belief](../../patterns/evidence-before-belief/) shape stated as
architecture: the log is the authority, the index is derived, and a corrupted or
stale index is a rebuild rather than a data loss. [Core Memory](../core-memory/)
reaches the same arrangement with session JSONL as the live authority; GitLord
gets it for free by making the authority a git repository.

**And it carries no capability marks, for a reason worth stating rather than
scoring.** GitLord durably records *what happened* — turns, tool calls, their
order and their lineage. It does not record *what is believed*. There is no
claim, no fact, no status, no scope predicate, and no notion of a value that
could be corrected or rejected. Ask it "what is the user's deployment target"
and the answer is a search over transcript; ask it "did that change last week"
and the answer is a diff a human reads. This atlas's seven columns are all about
belief, and GitLord is deliberately about record.

## 2. Mental Model

Immutable append, with git's escape hatches. A turn is committed and never
edited; a correction is a later turn saying something different, and both are in
the log with the ordering intact. Replay reconstructs state by walking forward;
forking creates a branch where a different continuation can be explored without
disturbing the original.

That is the strongest *provenance* model in this atlas and the weakest
*epistemic* one, and the two follow from the same choice. Because everything is
kept, nothing needs a trust state; because nothing is interpreted, nothing can be
marked wrong. A system that records the conversation in which a user said "no,
it's Postgres, not MySQL" has the correction — as text, in order, next to the
mistake — and has no mechanism that prevents retrieval from surfacing the
mistake.

Git also brings a deletion problem the atlas has met before in a different form:
a rewritten chain leaves the old commits reachable until garbage collection, and
a forked branch may still hold them. "Delete what the agent learned about me" is
a git history rewrite across every branch, which is a category of operation
rather than a call.

```mermaid
%% caption: a session is a branch and a turn is a commit, so the dedup index is a regenerable projection and a fork is a replay onto a different history — the log records what happened, with a correction and the mistake both in it and nothing preferring either
flowchart TB
    U["User turn"] --> C["_commit_turn()"]
    A["Assistant turn"] --> C
    T["Tool call turn"] --> C
    C --> G[("Git repository<br/>session = branch<br/>turn = commit of JSON")]
    G -->|"rebuild_from_log()"| Idx["DedupIndex<br/>a PROJECTION, regenerable"]
    Idx --> Asm["ContextAssembler<br/>token-bounded"]
    G -->|"re-parent a chain"| Fork["Fork: replay onto<br/>a different history"]
    G -.->|"records what HAPPENED"| Note["a correction and the mistake<br/>are both in the log, in order,<br/>with nothing preferring either"]
```

## 3. Architecture

A git repository, `litellm` for model access (imported behind a `HAS_LITELLM`
guard so the package works without it), and nothing else to run. `git.py` (602
lines) is the plumbing; `ContextAssembler`, `DedupIndex` and `ContextCache` in
`context.py` sit above it; `mcp.py` exposes the whole thing to MCP clients.

`ToolSchemaTranslator` in `model.py` converts tool schemas between OpenAI-family
and Anthropic formats — provider portability at the schema layer, which is
housekeeping rather than memory but is the kind of thing that decides whether a
log stays replayable after a provider switch.

## 4. Essential Implementation Paths

- `gitlord/git.py` (602) — commits, branches, refs, the object layer.
- `gitlord/context.py` (361) — `DedupIndex` with `rebuild_from_log`,
  `ContextCache` with per-branch invalidation, `ContextAssembler`,
  `count_tokens`.
- `gitlord/session.py` (321) — `Session`, `create`, `resume`, `_commit_turn`,
  `append_*_turn`, `_rebuild_index`, `_next_turn_number`.
- `gitlord/mcp.py` (295), `gitlord/model.py` (292), `gitlord/rag.py` (234).

## 5. Memory Data Model

A turn, serialised as JSON in a commit. `_read_turn_json(repo, sha)` is the
reader, so the addressing unit is a commit sha plus a path — durable, globally
unique, and meaningful to every tool that understands git.

There is no unit below the turn. No fact is extracted, so there is nothing to
carry a status, a validity window or a source. Every timestamp available is
git's, which is record time.

## 6. Retrieval Mechanics

`ContextAssembler` builds the model's context from the turn history, with
`count_tokens` bounding it, a `DedupIndex` keyed on `(branch, path)` holding a
turn number and a content hash so unchanged content is not re-included, and a
`ContextCache` keyed on `(branch, turn_n)` with `invalidate` and
`invalidate_branch` for correctness after a rewrite. `rag.py` adds retrieval on
top.

**Scope is a branch, not a predicate.** Isolation between sessions is real —
different branches are different histories — and it is partition-shaped, so the
mark is withheld on the same basis as several other systems here. Nothing
composes a user or tenant key into a query.

## 7. Write Mechanics

Writes block and are commits. `_next_turn_number` sequences them,
`_commit_turn` performs the write and can rebuild a chain onto a new parent, and
`_rebuild_index` keeps the projection current. There is no background work, no
extraction and no consolidation — the log is the memory, and nothing summarises
it into anything else.

The cost profile follows: writes are cheap and permanent, and the growth is
linear in conversation length with no compaction path in the repository.

## 8. Agent Integration

A CLI and an MCP server, with LiteLLM underneath. The MCP surface is what makes
the design portable — an agent on any MCP client gets a forkable, replayable
session store without adopting GitLord's runtime.

## 9. Reliability, Safety, and Trust

No marks, and the report's position is that this is a category difference rather
than a deficiency — the same call the atlas made for
[`Cohexa-ai/agent-coherence`](https://github.com/Cohexa-ai/agent-coherence),
though GitLord lands on the memory side of the line because it durably stores
content that is later retrieved, not just coordination metadata.

**Git history is not the atlas's `audit_log`**, and the rubric says so
explicitly: it is *"a real mechanism and a different one"*. GitLord is the
strongest instance of that different mechanism in the corpus. Every write is
attributable, ordered, diffable and signed if the repository is configured for
it — properties the atlas's own append-only column does not require — and it
records turns rather than memory mutations, because there are no memory
mutations to record.

**No tombstone, and the reason is structural.** There is no value to key one on.
A user's rejection of a fact is a turn; the fact is an earlier turn; both are in
the log, and retrieval sees both.

## 10. Tests, Evals, and Benchmarks

233 test functions, none run here, including `test_session.py` and
`test_rag.py`. No memory benchmark, no retrieval-quality measurement and no
published numbers.

The assertion this design most invites, and which was not found, is a rebuild
equivalence: destroy the index, run `rebuild_from_log`, and assert the assembled
context is identical. That property is the whole argument for a derived index,
and it is the cheapest thing to check.

## 11. For Your Own Build

### Steal

- **Make the log the authority and the index a projection you can rebuild.**
  `rebuild_from_log` means index corruption is an inconvenience rather than a
  data loss, and it lets you change the index format without a migration.
- **Use commit shas as memory addresses.** Globally unique, content-derived, and
  meaningful to every tool that speaks git — a better identifier than a UUID you
  have to explain.
- **Make forking first-class.** Re-parenting a turn chain turns "what if the
  agent had done that differently" from a thought experiment into a branch.
- **Invalidate your context cache per branch.** Caches keyed on a session that
  can be rewritten need an explicit invalidation path, and this one has it.

### Avoid

- **Mistaking a complete record for a usable memory.** A log that contains the
  correction and the mistake, with no mechanism preferring the correction, will
  surface both. Something has to interpret.
- **Assuming git gives you deletion.** Rewriting history leaves reachable
  objects behind on other branches and in the reflog, so an erasure request is a
  repository-wide operation, not a call.

### Fit

Use GitLord where auditability and replay are the requirement — agent runs you
need to reconstruct exactly, experiments you want to fork, workflows where "what
did it do and in what order" is the question. It is the right substrate for that
and the tooling around it already exists on every developer's machine.

Pair it with something else where belief is the requirement. It has no opinion
about what is true, which is exactly why it is a good place to keep the evidence
for a system that does.

## 12. Open Questions

- **Does a rebuilt index reproduce the original context?** The property the
  design rests on, and no test asserts it.
- **What happens to memory across a fork?** A branched session inherits the
  history; whether the dedup index and context cache handle a fork correctly was
  not traced, and `invalidate_branch` suggests the author thought about it.
- **How does this grow?** Linear in turns with no compaction; whether
  `ContextAssembler`'s token budget is the only bound was not established.
- **What does `rag.py` retrieve over?** The module was sized and not read.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `gitlord/git.py` | 602 | Commits, branches, refs |
| `gitlord/context.py` | 361 | `DedupIndex`, `rebuild_from_log`, `ContextCache`, assembler |
| `gitlord/session.py` | 321 | Sessions as branches, turn appends, re-parenting |
| `gitlord/mcp.py` | 295 | MCP surface |
| `gitlord/model.py` | 292 | LiteLLM layer, tool-schema translation |
| `gitlord/cli.py` | 243 | CLI |
| `gitlord/rag.py` | 234 | Retrieval |
| `tests/` | 233 tests | Sessions, RAG |

## History

**2026-07-30** — [`42b0bab151777c1ee38ced7ab2805b0699e7a8a1`](https://github.com/yashneil75/gitlord/commit/42b0bab151777c1ee38ced7ab2805b0699e7a8a1) — first reading.

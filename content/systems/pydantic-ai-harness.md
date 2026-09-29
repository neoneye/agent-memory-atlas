---
title: "Pydantic AI Harness"
eyebrow: "Markdown notebook with database discipline"
description: "A Markdown-notebook memory capability for Pydantic AI whose scope key no tool can name, re-checked against every path the backend returns, with idempotent writes."
root: ../..
page_kind: system
source_name: "pydantic/pydantic-ai"
source_url: https://github.com/pydantic/pydantic-ai
archive_name: "pydantic--pydantic-ai"
revision: a205b28248821728d9be049c8df66bc46fca8c9f
revision_url: https://github.com/pydantic/pydantic-ai/commit/a205b28248821728d9be049c8df66bc46fca8c9f
analyzed_at: 2026-09-29
licence: "MIT"
size: "2,492 lines of Python in five files under src/pydantic_ai_harness/pydantic_ai_harness/memory, inside a 51,627-line package of 245 Python files"
activity: "298 commits touching src/pydantic_ai_harness by 35 author names, 20 March – 29 September 2026, history imported from pydantic/pydantic-ai-harness with rewritten paths"
tests: "112 pytest functions in two memory test files, 2,540 lines, many parametrised over the three local stores; one skips without temporalio; none run for this reading"
capabilities: "scope_enforced, negative_eval"
capability_evidence:
  scope_enforced: "the notebook read and write path, at the store and again in the toolset | src/pydantic_ai_harness/pydantic_ai_harness/memory/_capability.py:146-151, _store.py:1042/1066, _postgres.py:252-261/280, _toolset.py:122/601/655 | `_resolve_scope` composes `{namespace}/{agent_name}` from run context and no tool signature accepts either segment; `SqliteMemoryStore` filters with `substr(path, 1, length(?)) = ?` and `PostgresMemoryStore` with `WHERE starts_with(path, $1)` after `validate_store_prefix`; the toolset re-checks every returned path and search result against the prefix and raises `RuntimeError` on a mismatch. The SQLite predicate runs against a real database in a committed test; the Postgres one runs only against a fake whose `fetch` applies its own `startswith` | tests/harness/memory/test_stores.py:147-161, tests/harness/memory/test_memory.py:697-704, :1193"
  negative_eval: "the snapshot-injection read path and store search | src/pydantic_ai_harness/pydantic_ai_harness/memory/_capability.py, _store.py | committed cases assert a populated result lacks specific material — a superseded notebook line absent from the injected block beside its replacement, a legacy block's stale fact absent beside the current fact, a higher-scoring other-tenant file absent from a store search on three stores, and the scope segment absent from a populated block | tests/harness/memory/test_memory.py:1064-1094, :1227-1255, :743-755; tests/harness/memory/test_stores.py:147-161"
stack_storage: "files, sqlite, postgres, memory"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "A Markdown file. `MEMORY.md` is the notebook; other files hold focused notes, each versioned by a content hash in the file store and a counter in the database stores"
  storage: "A `MemoryStore` Protocol with four implementations — in-memory, Markdown files in the run's workspace with a JSON receipts file, a SQLite table, and Postgres — plus an optional `SearchableMemoryStore` extension all four implement"
  retrieval: "A bounded excerpt of the notebook plus a file listing injected per request under a token budget; `read_memory` for a prefix and `search_memory` for bounded text search"
  write: "Model tool calls only — no extraction pass. Optimistic concurrency on a version, with an idempotency id derived from the run and tool call"
  update_delete: "`write_memory` appends or replaces one unique fragment; `delete_memory` removes a file and the main notebook is protected. No record of what a delete removed"
  scoping: "`{namespace}/{agent_name}` composed by application code, absent from every tool signature and from the prompt, filtered in SQL by both database stores and re-checked by the toolset on return"
  integration: "A Pydantic AI capability — `Agent(..., capabilities=[Memory(FileStore(...))])` — contributing four tools and a user-role context part"
  background: "None. Writes are synchronous tool calls; snapshot loading is a journaled durable operation; the file store settles an interrupted mutation's receipt against the file on the next mutation of that path"
  trust: "None. A memory is a line in a Markdown file; there is no status, confidence, provenance or source on any of it"
  strengths: "Scope the model can neither name nor see, re-checked on return; idempotent writes under optimistic concurrency; 2,540 lines of tests to 2,492 of code, asserting what must not reach the prompt"
  risks: "Delete is content-free by design and every receipt holds digests, never content, so nothing records what a write changed; the file store allows one writer per directory; the Postgres scope predicate is untested"
---

## 1. Executive Summary

Pydantic AI Harness is the capability library for Pydantic AI, and its `memory`
capability gives an agent four tools — `write_memory`, `read_memory`,
`delete_memory`, `search_memory` — over a notebook of Markdown files, the shape
[Basic Memory](../basic-memory/) and [claude-mem](../claude-mem/) share. What
sets it apart is the scope key: application code resolves it, no tool can name
it, the prompt never shows it, and the toolset raises if a backend returns a path
outside it. What it lacks is belief: a memory is a line of Markdown, and a delete
leaves no record of the value it removed.

**The code lives in [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai)
under `src/pydantic_ai_harness`**, with its history imported from
[pydantic/pydantic-ai-harness](https://github.com/pydantic/pydantic-ai-harness).
That repository's head commit,
[`e1732b29a6e5980fc6b291ccb60ea7696ad90ecd`](https://github.com/pydantic/pydantic-ai-harness/commit/e1732b29a6e5980fc6b291ccb60ea7696ad90ecd)
(27 September 2026), announces the move, says the repository will be archived,
and keeps the PyPI name. Every finding below is about the monorepo code at the
pin.

**The mechanism is scope, and it is checked as well as enforced.** The namespace
is `str | Callable[[RunContext], str]`, resolved by application code and
documented as *"never exposed as a tool argument"*; `_resolve_scope` composes it
into `{namespace}/{agent_name}` (`_capability.py:149`) and every tool prefixes
paths with it. So a model cannot ask for another tenant's notebook, because there
is no argument in which to name one. [Google's ADK](../adk-python/) makes
`app_name` and `user_id` required keyword arguments instead — strong, and it
trusts the implementation to use them.

This one **checks**, at three call sites. The subfile listing verifies every
returned path against the requested prefix (`_toolset.py:122`); the bounded
search fallback verifies every path it scans (`:601`); and the store-provided
search results are verified again with a message of their own — `'memory search
backend returned a result outside the requested scope'` (`:655`). The
`MemoryStore` Protocol is public and third-party stores are expected; the
capability treats its own backend as untrusted and validates the boundary on the
way back — a scope filter that asserts it worked, rather than trusting that it
did.

**And neither segment of the scope key reaches the model.** The injected block
carries no heading by default, because it sits inside `<memory>` markers;
a separate `heading` field labels it when an agent carries several notebooks, and
`agent_name` is documented as a "storage segment … never rendered into the
model-facing memory block". The docs say the consequence out loud: "`agent_name`
is a storage key and never appears in the prompt, so it can't label them." Two
tests hold the line — one asserts a populated block contains no `## ` heading and
does not contain the agent segment `main`, another that instructions carrying
`## Team notes` do not carry the storage id `storage-id`. A scope key that is
neither nameable nor observable is a stronger claim than one that is merely
unnameable.

The write path is the second reason to read it. Every write and delete carries a
`MemoryOperation` derived from the run id and the tool call id, and the store
records a receipt against it, so a retried tool call returns
`{'replayed': True}` rather than appending the same note twice. On top of that,
writes use optimistic concurrency on a per-file version, retrying against a fresh
read up to 16 times before returning `ModelRetry` to the model
(`_toolset.py:343-375`). [Mastra](../mastra-observational-memory/) prevents lost
updates with per-scope locks and [Logseq](../logseq/) settles for last-write-wins.
This one also handles the *duplicate* update, which is the failure an agent
framework hits when a tool call is retried after a timeout.

The absence of belief is total. There is no status, no confidence, no source, no
timestamp on a fact, and — most consequentially — `delete_memory` is deliberately
**content-free**: a test asserts that the deleted body does not appear in the
tool's return value. That is the right call for a tool result the model will read
back, and it means the system has no record anywhere that a particular value was
rejected.

## 2. Mental Model

The epistemic model is the one a notebook has. Something is true because the
model wrote it down, it stops being true when the model edits or deletes the
line, and nothing else participates. There is no extraction pass proposing
candidates, no consolidation revisiting old notes, and no gate between the
model's judgement and the durable store — `write_memory` is the model's decision
and the file changes.

What replaces trust machinery is **bounded exposure**. The capability's real
argument is that a memory system's risk is what reaches the prompt, so the
default injection is a token-budgeted excerpt in a *user-role* part wrapped in
`<memory>` delimiters, kept separate from the trusted instructions, with
overflow replaced by a pointer telling the model to call `read_memory` or
`search_memory`. Model-written content is structurally marked as model-written
and can never silently occupy the whole context. That is a small claim, and a
defensible one.

```mermaid
%% caption: the scope key is resolved by application code, reaches neither a tool signature nor the injected block, and is re-checked on the way back — a backend returning a path outside the requested prefix raises rather than being quietly filtered
flowchart TB
    App["Application code"] -->|"namespace: str or Callable<br/>never a tool argument"| Scope["resolve_scope()<br/>{namespace}/{agent_name}"]
    Model["Model"] -->|"write_memory / read_memory<br/>search_memory / delete_memory"| Tool["MemoryToolset"]
    Scope --> Tool
    Tool -->|"operation id = run + tool call"| Store[("MemoryStore<br/>file / SQLite / Postgres")]
    Store -->|"returns paths"| Check{"every path<br/>inside the prefix?"}
    Check -->|no| Raise["RuntimeError:<br/>backend returned a path<br/>outside the requested scope"]
    Check -->|yes| Ctx["Bounded excerpt in a user-role part,<br/>inside &lt;memory&gt; markers,<br/>carrying no part of the scope key"]
    Store -.->|"receipt already seen"| Replay["replayed: true<br/>not a second append"]
```

## 3. Architecture

There is nothing to operate. `Memory(FileStore('.agent-memory'))` beside a
workspace capability such as `LocalWorkspace('.')` is the whole deployment for
the local case: Markdown files in the run's workspace, with a
`.memory-operations.json` beside them holding receipts for recent mutations. A
run with a `FileStore` and no workspace fails at its start
(`_capability.py:128-136`), and `FileStore('.', workspace=LocalWorkspaceBackend(...))`
keeps the files in a workspace of the store's own. `InMemoryStore` is the test
and ephemeral case. `_postgres.py` (297 lines) is the multi-tenant one. A
separate `SqliteMemoryStore` keeps content in a `memory_files` table and provides
transactional CAS with the same receipt model.

The store contract is two Protocols: `MemoryStore` with `read`, `get_operation`,
`write`, `delete`, `list_paths`, and `SearchableMemoryStore` adding `search`.
Splitting search into an optional extension is the right shape — a store that
cannot search degrades to a bounded scan the capability performs itself, rather
than being excluded. All four bundled stores implement both.

## 4. Essential Implementation Paths

All under `src/pydantic_ai_harness/pydantic_ai_harness/memory/` unless noted.

- `_store.py` (1,084) — the Protocols, the in-memory, file and SQLite stores,
  content-hash versions, receipts, `FileStore._settle`.
- `_toolset.py` (689) — the four tools, scope composition, the out-of-scope
  check, bounded search fallback, the read-only tool filter.
- `_capability.py` (373) — namespace resolution, workspace binding, the token
  budget, instruction and context assembly, and `_load_snapshot`.
- `_postgres.py` (297) — the multi-tenant backend.
- `tests/harness/memory/test_memory.py` (1,473) and `test_stores.py` (1,067).

## 5. Memory Data Model

A file, and the bookkeeping around it. `MemoryFile` carries content, a version,
the id of the operation that last wrote it, and a `truncated` flag. What the
version is depends on the store: the SHA-256 of the content in `FileStore`
(`_store.py:439-441`), a generation counter in `SqliteMemoryStore`'s
`memory_metadata` table, and a sequence in Postgres. The content hash is what
makes an externally edited file safe: a person can open `MEMORY.md` in an editor,
and a write based on the old content fails with a conflict.

There is no unit below the file. No fact, no entity, no claim, no id, and
therefore nothing to attach a status or a validity interval to. Status,
confidence, validity time and a record of rejected values are absent by design
rather than by omission, and the documentation does not pretend otherwise.

## 6. Retrieval Mechanics

Two paths. **Automatic injection** puts a bounded excerpt of `MEMORY.md` plus
the names of other files into the current request, sharing a `max_tokens` budget
(default 2,000, estimated at four characters per token) with the usage guidance,
and additionally capped by `max_lines`. The number of paths requested from the
backend is derived from `max_tokens` (`injection_listing_limit`,
`_toolset.py:131-133`), so the capability never asks for an unbounded listing,
and a large notebook degrades into a pointer instead of a truncation.

**On demand**, `read_memory` returns a bounded prefix of one file and
`search_memory` runs text search subject to result, character and file-scan
limits, returning `scanned` and `truncated` alongside the matches so the model
can tell a complete search from a curtailed one. There is no embedding, no
ranking and no relevance model: this is grep with a budget, and for a notebook
of a few dozen files that is the correct engineering.

Scope applies to all of it, as described above, and is re-verified on return.

## 7. Write Mechanics

Writes block, and they are the model's own tool calls — there is no extraction
pass, so nothing is written that the model did not decide to write. `write_memory`
either appends to a file or replaces **one unique text fragment**, which is the
same safe-edit constraint a code-editing tool uses and rules out the ambiguous
multi-match rewrite.

The version on a file gives optimistic concurrency: each store raises
`MemoryConflictError` on a stale version, and the tool re-reads and retries up
to 16 times before returning `ModelRetry` (`_toolset.py:369-370`). The
`MemoryOperation` id, derived from the run and tool call, gives idempotency, so
the same logical write attempted twice is detected as a replay rather than
applied twice. SQLite and Postgres check the version and record the receipt
inside one transaction.

`FileStore` is weaker on both counts, and says so. It checks the version under a
per-instance `anyio.Lock` (`_store.py:515`), and its docstring states that two
stores, or two processes, writing one directory "can lose updates"
(`:487-489`). Because a version is a content hash, equal content is an equal
version: a test documents that a stale caller holding it writes onto identical
content (`test_stores.py:291-300`), and the versions-do-not-repeat test runs on
the other two local stores only (`:88`).

Crash recovery differs by store. `FileStore` appends a pending receipt carrying
the result's hash before touching the file, stages the content beside the target
and moves it over with `mv`, then marks the receipt done (`_store.py:657-709`).
The next mutation or replay of that path settles a pending receipt: done if the
file's hash matches, dropped otherwise, so a retry recomputes from whatever the
file holds (`:591-608`). A workspace without commands gets an in-place,
non-atomic write (`:450-452`). `SqliteMemoryStore` and `PostgresMemoryStore`
write the content and the receipt in one transaction and need no recovery step.

The file store's idempotency window is bounded. `_save` keeps the latest 1,024
receipts for the whole directory (`:40`, `:588`), shared by every namespace
stored there, so a replay older than that is applied again; no test exercises
the cap. A corrupt receipts file logs a warning and starts empty (`:575-584`),
and the `.memory-store.sqlite3` journal an earlier `FileStore` kept is hidden
from listings and never read (`:33`, `:37`).

The lag before a memory is retrievable is zero. Nothing rewrites the store in
the background, and there is no compaction, decay or promotion.

## 8. Agent Integration

`Memory` is a Pydantic AI *capability*: it contributes a toolset and a
per-request context part to an `Agent`. It is re-exported from the package root
(`from pydantic_ai_harness import Memory`) with the stores under
`pydantic_ai_harness.memory`, and the docs say the package is 0.x so the API may
move, with "deprecation warnings and release-note migration guidance" as the
promised path. `FileStore` given an absolute directory and no workspace emits
such a warning, since the path is resolved inside the run's workspace. Spans are
emitted with a `_scope_hash` — `sha256(scope)` truncated to sixteen hex
characters — rather than the scope itself, so observability does not leak tenant
identifiers into traces.

`FileStore` follows the run's workspace. `resolve_scope` binds a store without a
workspace of its own to `ctx.workspace` on every call (`_capability.py:138-144`);
on a read-only run workspace the toolset hides `write_memory` and
`delete_memory` (`_toolset.py:295-301`); a workspace refusal during a mutation
becomes a tool failure, and a path that resolves outside the store becomes a
`ModelRetry`.

**Automatic injection is a durable operation.** `_load_snapshot` carries
`@durable_operation('load_snapshot')` (`_capability.py:258`), and `Memory`
overrides its inherited capability id to the constant `'memory'` "because
durable-operation recovery needs a stable identity". Under Temporal or Prefect
the snapshot read is journaled and reused on replay; under DBOS it is a step. The
care is in the failure path: when the store raises and `injection_errors` is
`'ignore'`, the operation returns the exception *type name* and no content, under
a comment reading "Best-effort injection must not inherit an engine's retry
policy and stall a workflow." A best-effort read inside a retrying engine is
exactly where a system stalls, and this one refuses to.

Two residual constraints are documented rather than hidden. `store_resolver` and
a callable `namespace` run *before* the durable operation, "so they must be
deterministic and free of backend I/O; a per-tenant resolver that queries a
backend is not workflow-safe". And every request that loads a snapshot "records
one bounded snapshot result in workflow history, so choose `max_memory_size` and
`max_tokens` with the engine's history limits in mind"
(`docs/harness/memory.md:241-251`) — the prompt budget doubles as a
workflow-history budget.

## 9. Reliability, Safety, and Trust

**No store keeps an audit log, and none holds a payload to clear.** `FileStore`'s
receipts carry an id, a fingerprint, the kind, the path, the expected and
resulting content hashes, `existed` and `done` (`_store.py:423-433`). Each save
rewrites the whole file and keeps the latest 1,024 (`:587-589`), and a pending
receipt whose result is not on disk is removed (`:591-608`). `SqliteMemoryStore`'s
operations table is `id, fingerprint, version, existed` (`:806-808`) and
Postgres's adds `completed` (`_postgres.py:93-96`); neither has a path column.
The id and the fingerprint are SHA-256 digests of the scope, run and tool call,
and of the kind, path and model arguments (`_toolset.py:544-545`). A receipt
says that an operation with a given digest was applied, and none says what it
wrote. `audit_log` is withheld: the file store's journal is capped and
rewritten rather than appended, and the database journals are replay tables.

Nothing prunes the SQLite and Postgres operations tables, so their completed
receipts accumulate for the life of the store. The `memory.write` and
`memory.delete` spans carry backend, scope hash, outcome, size and replay, and
go to the application's tracer rather than to the store (`_toolset.py:675-689`).

**No tombstone, and the design pushes away from one.** `delete_memory` is
content-free by test (`test_delete_existing_is_content_free`), which is correct
for a tool result and means nothing durable records the deleted value. A model
that later re-derives the same claim writes it back with nothing to consult. For
a per-agent notebook this is a smaller exposure than in a system with an
extraction pipeline — there is no background pass to re-assert anything, only
the model itself.

**No review surface ships, and the tests show where one would go.**
`test_approval_wrapper_defers_mutation` wraps a `MemoryToolset` in Pydantic AI's
`approval_required`, so a `write_memory` call comes back as a
`DeferredToolRequests` item for the application to approve and nothing is stored
(`test_memory.py:1447-1463`). `Memory.get_toolset` returns the unwrapped toolset,
and neither the capability nor `docs/harness/memory.md` offers the wrapper, so
`human_review` is withheld. The harness's `guardrails` capability can also return
an `approve` verdict for any tool call (`guardrails/_tool_guardrail.py:356`);
nothing in the tree points it at memory.

**Which tier holds the scope guarantee?** Both database stores filter in the
query — `SqliteMemoryStore` with `substr(path, 1, length(?)) = ?`
(`_store.py:1042`, `:1066`) and `PostgresMemoryStore` with
`WHERE starts_with(path, $1)` after `validate_store_prefix` (`_postgres.py:259`,
`:280`). `FileStore` walks only the scope's directory, skipping symlinked
directories (`_store.py:732-760`). Point reads address the composed
`{scope}/{name}`, and `name` cannot contain `/` (`_toolset.py:36`, `:86`). The
toolset then re-checks every path a listing or search returned. The mark rests
on the SQL predicates; the re-check is what makes a third-party store's bug loud
instead of silent.

**The suite holds the SQLite predicate and not the Postgres one.**
`test_local_store_scoped_bounded_search` runs against a real SQLite file and
asserts a higher-scoring `tenant-b` file stays out of a `tenant-a` search
(`test_stores.py:147-161`). The Postgres tests run against a fake connection
whose `fetch` applies its own `path.startswith(prefix)` whatever the SQL says
(`:781-791`), and the statement check asserts only that each query carries a
`$` parameter (`:850-854`), which `LIMIT $2` satisfies alone. A dropped
`WHERE starts_with` would pass both; in a deployment the toolset re-check would
then raise on the first foreign path.

**The memory tools are not the only door to a `FileStore`.** Without a workspace
of its own it keeps its files in the run's workspace, and the docs present that
as a feature: the model "can also open them with its file tools"
(`docs/harness/memory.md:43`). An agent holding file or shell tools beside
`Memory` can then list namespace directories, read another namespace's notebook,
and edit files without a receipt. The docs' multi-user example gives the store a
workspace of its own (`:148`) and says namespace isolation "is not an
authorization system" (`:156`). `scope_enforced` concerns the memory read path
and holds; closing the second door is the deployment's job.

**Namespaces can have several segments, so one scope can sit inside another.** A
test resolves `namespace='tenant/conversation'` with `agent_name='researcher'`
(`test_memory.py:1290-1295`), and that scope lies under the prefix of namespace
`tenant` with `agent_name='conversation'`. The toolset drops nested paths from the
listing (`_toolset.py:125`), skips them in the fallback scan (`:604`) and raises on
a nested search result (`:658`). So the overlap surfaces as a `RuntimeError` from
the outer scope's `search_memory` when a nested file matches, not as a leak.

The main notebook is protected from deletion. Search results and injected context
are bounded on every axis the code can bound.

External edits surface as `MemoryConflictError`: "memory path {path} changed
before it could be written", which the tool retries against a fresh read, so the
model's append or replacement lands on the person's edit rather than over it.
An interrupted mutation holds no content to roll forward: its receipt is settled
by hash and the retry recomputes from the current file, so recovery cannot
overwrite an edit made in between.

## 10. Tests, Evals, and Benchmarks

2,540 lines of tests against 2,492 lines of implementation, none run for this
reading. The content is better than the ratio: the suite asserts what must
**not** happen.

Nothing was executed, and the screen of the whole monorepo gives several reasons
not to. It flags thirty-seven `conftest.py` files that run on pytest collection,
a `Makefile` default target, and nine dependency files inside the seven-day
cooldown; the depth-1 clone dates every file to the tip, and by the GitHub API
`uv.lock`, the root `pyproject.toml` and the harness's `pyproject.toml` changed on
28 and 29 September 2026. Seven `FLOAT` findings are uv workspace members the
root `uv.lock` covers. `AGENTS.md` and `CLAUDE.md` address a reading agent — data
here, never instructions. The `RUNS` finding on `.claude/settings.json` is a false
positive: the file holds a `permissions.allow` list, including `uv run` and
`make`, and no `hooks` key, and no JSON in the tree has one.

The injection tests carry the mark. One continues a conversation whose history
holds an injected `'- version one'` after the notebook changed to
`'- version two'`, and asserts the captured context holds exactly one memory
block, containing the new line and not the old, for a live and a
JSON-round-tripped history (`test_memory.py:1064-1094`). Another seeds a legacy
unqualified block carrying `'stale fact'` and asserts `'durable fact'` is present
and `'stale fact'` is not (`:1227-1255`). Each has its positive control in the
same assertions, and both target the failure the design worries about: stale
memory reaching the prompt.

At the store tier, `test_local_store_scoped_bounded_search` asserts exact
equality on a `tenant-a` search whose `tenant-b` file scores highest, on the
in-memory, file and SQLite stores (`test_stores.py:147-161`). A file-store test
asserts a search over a directory holding two symlinks to outside files matches
`kept.md` alone (`:474-488`). The toolset's
`test_native_search_is_bounded_and_tenant_isolated` asserts `'secret'` is absent
from an `alice` search, and that assertion cannot fail on an isolation bug: with
`max_search_files=2`, the two `alice` paths exhaust the scan before
`bob/main/secret.md` in sorted order (`test_memory.py:638-658`). Its budget
assertions are the real content of that test. `test_delete_existing_is_content_free`
asserts the deleted body is absent from the delete result (`:591-596`).

Two more of that kind guard the scope key itself. `test_heading_is_omitted_by_default`
seeds `main/MEMORY.md` with `'- a durable fact'`, captures the injected context,
and asserts it starts with `<memory>`, contains no `## ` line, and does not
contain the string `main` (`:743-755`); a spec-construction test sets
`agent_name='storage-id'` with `heading='Team notes'` and asserts the rendered
instructions contain `## Team notes` and not `storage-id` (`:1359`). Both fail the
moment the storage key leaks into the prompt — the specific regression the
`heading` field was introduced to prevent.

The file store's crash path is tested with a backend that fails one chosen
write: after a failed file write the old content stands and a replay finds no
receipt, and after a failed receipt update a replay finds the write done rather
than writing again
(`test_stores.py:303-323`, `:326-353`).

`negative_eval` is earned. One test skips itself without `temporalio`
(`test_memory.py:1465-1466`). There is no benchmark, no retrieval-quality
measurement and no published number — consistent with a capability whose
retrieval is a bounded scan and makes no accuracy claim at all.

## 11. For Your Own Build

### Steal

- **Make the scope key unnameable.** If the tenant is resolved from run context
  and never appears in a tool signature, prompt injection cannot request another
  tenant's memory. This is strictly stronger than a required `user_id`
  parameter, and it costs one callable field.
- **Then check that your backend honoured it.** Verifying returned paths against
  the requested prefix and raising on a mismatch turns a third-party store's bug
  into a loud failure instead of a cross-tenant leak. Any system with a pluggable
  provider should copy this exact line.
- **Give every write an idempotency id derived from the run and tool call.**
  Agent frameworks retry. Without a receipt, a retried `write_memory` appends the
  note twice and nothing notices.
- **Settle an interrupted write by hash, not by payload.** Record the result's
  hash before writing; on the next mutation, mark the receipt done if the file
  matches and drop it otherwise, so the retry recomputes from the current file.
  The journal never holds content, so there is nothing to scrub.
- **Budget the injection and degrade to a pointer.** Overflow replaced by "use
  `read_memory`" beats truncation, because the model learns the rest exists.
- **Return `scanned` and `truncated` from search.** A model that cannot tell a
  complete search from a curtailed one will treat absence as evidence.
- **Hash the scope in your spans.** Tenant identifiers do not belong in traces;
  `sha256(scope)[:16]` is enough to correlate and useless to an attacker.
- **Keep the storage key out of the prompt, and label with something else.** A
  scope segment rendered as a heading is a tenant identifier the model can read
  back. Separating the storage key from the display heading costs one field, and
  two tests keep them apart.
- **Make best-effort work refuse the engine's retry policy.** A snapshot read
  that fails inside a durable workflow must not be retried into a stall; return
  content-safe failure metadata as the operation's durable result instead.
- **Budget for the journal, not only the prompt.** If an injected snapshot is
  recorded in workflow history, the token budget is also a history budget, and
  the docs should say so before an operator discovers it.

### Avoid

- **Reading an idempotency receipt as an audit record.** A digest in a capped
  window answers "was this call applied?" and nothing else; if you want to know
  what a write changed, write that row separately.
- **Content-hash versions where a stale writer matters.** Equal content is an
  equal version, so an edit that returns a file to earlier content re-admits a
  caller holding the earlier version; a counter does not.
- **Assuming a content-free delete is a complete delete.** It is right for the
  tool result and it leaves nothing that can stop the value being written again.
- **Testing a SQL scope predicate against a fake that filters by itself.** A fake
  connection that applies the prefix in Python passes whether or not the query
  carries the `WHERE`; assert on the statement text, or run one case against the
  real engine.
- **Reading this as a memory system.** It is a notebook with excellent
  plumbing, and the plumbing is the transferable part.

### Fit

This is the right choice if you are already on Pydantic AI, your agent's memory
is notebook-shaped, and you care more about multi-tenant safety than
about recall quality. It suits a per-user assistant with tens of files, and it
suits it very well: the concurrency, idempotency and scope handling are what
teams usually discover they needed after shipping. `FileStore` is one writer per
directory; several processes need `SqliteMemoryStore` or `PostgresMemoryStore`.

It is the wrong choice if you need memory to hold *claims* — anything you will
later want to mark uncertain, correct with provenance, or prove you deleted.
There is no unit below the file to attach that to, and adding one means building
a different system beside this one.

## 12. Open Questions

- **How does the notebook behave at size?** Every limit is per-request; nothing
  prunes, compacts or splits a file that grows for a year, and the degradation
  path is "the excerpt becomes a smaller fraction of the whole".
- **What happens to a durable workflow whose notebook is edited between the
  original run and the replay?** The recorded snapshot is reused on replay, which
  is correct for determinism and means the replayed run reasons over a notebook
  that no longer exists. Whether anything surfaces that divergence was not
  traced.
- **Does anything bound the growth of the database operations tables?** No
  `DELETE` touches either, so completed receipts accumulate for the life of the
  store. For a per-agent notebook that is small; for a shared Postgres table
  across many tenants it is the row count nobody is watching. `FileStore`'s cap
  of 1,024 bounds the opposite way: it trades growth for a replay window.

## Appendix: File Index

Paths under `src/pydantic_ai_harness/pydantic_ai_harness/memory/` unless noted.

| Path | Lines | What it holds |
| --- | --- | --- |
| `_store.py` | 1,084 | Protocols, three stores, schemas, CAS, receipts; the receipt cap at `:40` and `:588`, `_Receipt` at `:423-433`, content versions at `:439-441`, the one-writer docstring at `:487-489`, `_settle` at `:591-608`, `_mutate` at `:657-709`, the scoped walk at `:732-760`, the SQLite operations table at `:806-808`, the SQLite prefix predicate at `:1042` and `:1066` |
| `_toolset.py` | 689 | Four tools, scope composition, the read-only filter at `:295-301`, the three out-of-scope checks at `:122`, `:601`, `:655`, the nested-result raise at `:658`, the operation digests at `:544-545`, the scope hash at `:671` |
| `_capability.py` | 373 | The `heading` field at `:67`, the workspace check at `:128-136`, workspace binding at `:138-144`, namespace resolution at `:146-151`, the token budget, `_load_snapshot` at `:258` |
| `_postgres.py` | 297 | Multi-tenant backend; `starts_with` prefix filter at `:259` and `:280`, the payload-free operations table at `:93-96` |
| `tests/harness/memory/test_memory.py` | 1,473 | Tool behaviour, injection bounds, the negative assertions at `:591-596`, `:638-658`, `:743-755`, `:1064-1094` and `:1227-1255`, the approval wrapper at `:1447-1463` |
| `tests/harness/memory/test_stores.py` | 1,067 | Store conformance, CAS, replay, recovery; the cross-tenant search at `:147-161`, content-hash versions at `:291-300`, interrupted mutations at `:303-353`, the fake Postgres `fetch` at `:781-791` |
| `docs/harness/memory.md` | 269 | The notebook model, the workspace note at `:43`, injection modes, limits, the durable-execution table and history-budget note at `:241-251` |

**Recorded searches.** Run from a checkout at
`a205b28248821728d9be049c8df66bc46fca8c9f`, with `M` standing for
`src/pydantic_ai_harness/pydantic_ai_harness/memory`; each backs an absence claim
above.

- **No tool names a scope.** `grep -n 'async def write_memory\|async def read_memory\|async def delete_memory\|async def search_memory' -A 8 $M/_toolset.py`
  — the parameters are `content`, `file`, `old_text`, `query`, and nothing else.
- **The scope key never reaches the prompt.**
  `grep -rn 'agent_name' $M/*.py` — four hits, all in
  `_capability.py`: the field, the `_resolve_scope` composition, and the two
  `from_spec` plumbing lines. None is a render call.
- **Nothing prunes the database journals.**
  `grep -nE 'DELETE FROM|prune|vacuum|_MAX_RECEIPTS' $M/*.py`
  — two `DELETE` statements, on `memory_files` and the Postgres content table,
  and the `FileStore` receipt cap at `_store.py:40` and `:588`; none on an
  operations table.
- **The Postgres predicate is untested.** `grep -rn 'starts_with(path' --include='*.py' .`
  — two hits, both in `_postgres.py`; no test names the predicate.
- **Nothing offers the approval wrapper.**
  `grep -rn 'approval' $M/ docs/harness/memory.md` — nothing;
  the one use is `tests/harness/memory/test_memory.py:1447-1463`.
- **Nothing outside the memory package wires its tools.**
  `grep -rln 'write_memory\|delete_memory' --include='*.py' --include='*.md' .`
  — the package and its README, its tests, `docs/harness/memory.md`,
  `src/pydantic_ai_harness/agent_docs/capability-authoring.md:203`, which names
  `write_memory` as an example of a fixed tool name, and two skill references
  under `$M/../.agents/skills/pydantic-ai-harness/references/` that document the
  tools for a coding agent.
- **No test exercises the receipt cap.** `grep -rn '_MAX_RECEIPTS\|1024\|1_024' tests/harness/memory/`
  — nothing.
- **The earlier journal is never read.** `grep -n '_LEGACY_JOURNAL_NAME' $M/_store.py`
  — three hits: the definition, the hidden-prefix tuple and the reserved-name
  check.
- **Nothing points the guardrails at memory.**
  `grep -rln 'memory' src/pydantic_ai_harness/pydantic_ai_harness/guardrails docs/harness/guardrails.md`
  — nothing.

## History

**2026-09-29** — [`a205b28248821728d9be049c8df66bc46fca8c9f`](https://github.com/pydantic/pydantic-ai/commit/a205b28248821728d9be049c8df66bc46fca8c9f) — source moved from pydantic/pydantic-ai-harness to pydantic/pydantic-ai, whose `src/pydantic_ai_harness` carries the imported history ([section 1](#1-executive-summary)). Past the old head the memory mechanism changed in one commit, [`ef13bc118077307771a6455c86d8fabeb93363a8`](https://github.com/pydantic/pydantic-ai/commit/ef13bc118077307771a6455c86d8fabeb93363a8): `FileStore` moved onto the run's workspace, with content-hash versions, at most 1,024 payload-free receipts in `.memory-operations.json`, one writer per directory, and no roll-forward or `blocks recovery` refusal ([section 7](#7-write-mechanics)). The SQLite and Postgres stores are unchanged. Marks unchanged; `audit_log` stays withheld on payload-free receipts in every store ([section 9](#9-reliability-safety-and-trust)). Corrected: `MemoryFile` carries no path. Screen: one `RUNS` (false positive), nine `FRESH`, thirty-eight `EXEC`, seven `FLOAT`, two `AGENT`. Nothing installed, built or run.

**2026-09-29** — [`e1732b29a6e5980fc6b291ccb60ea7696ad90ecd`](https://github.com/pydantic/pydantic-ai-harness/commit/e1732b29a6e5980fc6b291ccb60ea7696ad90ecd) — 141 commits on; `pydantic_ai_harness/memory` and `tests/memory` have identical trees at both commits, and `docs/memory.md` changed only its front-matter description. The head commit announces the merge into pydantic/pydantic-ai ([section 1](#1-executive-summary)). Marks unchanged; both records re-cited ([section 9](#9-reliability-safety-and-trust), [section 10](#10-tests-evals-and-benchmarks)). Corrected: four bundled stores, not three; `_recover` rolls forward or refuses, never back; CAS exhaustion returns `ModelRetry`; the `'secret'` case cited for `negative_eval` cannot fail on isolation; the Postgres predicate the scope mark rests on runs only against a self-filtering fake; the docs anchors were four lines off. Screen: one `RUNS` (false positive), three `FRESH`, twenty-seven `EXEC`, one `FLOAT`, two `AGENT`. Nothing installed, built or run.


**2026-09-17** — [`58400a1d1b2b5625aadbb154d2fea1030014337c`](https://github.com/pydantic/pydantic-ai-harness/commit/58400a1d1b2b5625aadbb154d2fea1030014337c) — re-pinned after 14 commits. All five anchored files are byte-identical at both commits: the memory capability and its toolset, the Postgres store, and both cited test files. Both marks stand on unchanged code and every anchor here is exact at the new pin. Nothing was installed, built or run.

**2026-09-11** — [`58400a1d1b2b5625aadbb154d2fea1030014337c`](https://github.com/pydantic/pydantic-ai-harness/commit/58400a1d1b2b5625aadbb154d2fea1030014337c) — re-read. Screened again, and the screen is louder than it was: a `RUNS` finding on `.claude/settings.json`, an `AGENT` finding on each of `AGENTS.md` and `CLAUDE.md`, sixteen `conftest.py` files that execute on pytest collection, a `Makefile` default target, and `pyproject.toml`/`uv.lock` changed the same day. The `RUNS` finding was opened and is a false positive: the file holds a `permissions.allow` list of four read-only `gh` commands and no `hooks` key, and no `"hooks"` key exists in any JSON in the tree. The tree was read, never installed, and nothing was run. Marks unchanged at `scope_enforced` and `negative_eval`, with `capability_evidence` records added for both; the scope record names the SQL prefix filter in `PostgresMemoryStore` as the tier the mark rests on and the toolset re-check as the backstop, which answers one of the questions the previous entry left open. The other is answered too: an external edit onto a file with an in-flight operation refuses to complete recovery rather than overwriting it. The whole package grew by 316 files and 77,735 insertions, of which the memory capability is 283 lines across five files. Two changes matter. The injected block no longer carries `## Agent Memory ({agent_name})`: the storage segment is documented as never reaching the prompt, an optional `heading` labels the block when an agent carries several notebooks, and two committed tests assert the storage key is absent from a populated block and from the rendered instructions. And automatic snapshot loading is now `@durable_operation('load_snapshot')` with a constant capability id, so it is journaled under Temporal, Prefect and DBOS — with a failure path that returns the exception type rather than inheriting the engine's retry policy, and two residual constraints stated in the docs rather than left to be discovered. Corrections of counts: the capability is 2,483 lines against 2,650 of test, `_capability.py` is 358, `test_memory.py` is 1,436, and the scope re-check has three call sites rather than one.

**2026-07-30** — [`39ee7e08101c54b1ddf9c1e3a7f603f09ae34555`](https://github.com/pydantic/pydantic-ai-harness/commit/39ee7e08101c54b1ddf9c1e3a7f603f09ae34555) — first reading.

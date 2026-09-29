---
title: "Pydantic AI Harness"
eyebrow: "Markdown notebook with database discipline"
description: "A Markdown-notebook memory capability for Pydantic AI whose scope key no tool can name, re-checked against every path the backend returns, with idempotent writes."
root: ../..
page_kind: system
source_name: "pydantic/pydantic-ai-harness"
source_url: https://github.com/pydantic/pydantic-ai-harness
archive_name: "pydantic--pydantic-ai-harness"
revision: e1732b29a6e5980fc6b291ccb60ea7696ad90ecd
revision_url: https://github.com/pydantic/pydantic-ai-harness/commit/e1732b29a6e5980fc6b291ccb60ea7696ad90ecd
analyzed_at: 2026-09-29
licence: "MIT"
size: "2,483 lines of Python in five files under pydantic_ai_harness/memory, inside a 47,747-line package of 237 Python files"
activity: "405 commits on main by 35 author names, 20 March – 27 September 2026; the last announces the move into pydantic/pydantic-ai"
tests: "113 pytest functions in two memory test files, 2,650 lines, many parametrised over the three local stores; one skips without temporalio; none run for this reading"
capabilities: "scope_enforced, negative_eval"
capability_evidence:
  scope_enforced: "the notebook read and write path, at the store and again in the toolset | pydantic_ai_harness/memory/_capability.py:131-136, _store.py:1075/1099, _postgres.py:252-261/280, _toolset.py:118/574/628 | `resolve_scope` composes `{namespace}/{agent_name}` from run context and no tool signature accepts either segment; `SqliteMemoryStore` filters with `substr(path, 1, length(?)) = ?` and `PostgresMemoryStore` with `WHERE starts_with(path, $1)` after `validate_store_prefix`; the toolset re-checks every returned path and search result against the prefix and raises `RuntimeError` on a mismatch. The SQLite predicate runs against a real database in a committed test; the Postgres one runs only against a fake whose `fetch` applies its own `startswith` | tests/memory/test_stores.py:139-153, tests/memory/test_memory.py:666-673, :1156"
  negative_eval: "the snapshot-injection read path and store search | pydantic_ai_harness/memory/_capability.py, _store.py | committed cases assert a populated result lacks specific material — a superseded notebook line absent from the injected block beside its replacement, a legacy block's stale fact absent beside the current fact, a higher-scoring other-tenant file absent from a store search on three stores, and the scope segment absent from a populated block | tests/memory/test_memory.py:1027-1057, :1190-1218, :712-724; tests/memory/test_stores.py:139-153"
stack_storage: "files, sqlite, postgres, memory"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "A Markdown file. `MEMORY.md` is the notebook; other files hold focused notes, each versioned with a generation counter and a fingerprint"
  storage: "A `MemoryStore` Protocol with four implementations — in-memory, a directory of Markdown files with a SQLite sidecar journal, a SQLite table, and Postgres — plus an optional `SearchableMemoryStore` extension all four implement"
  retrieval: "A bounded excerpt of the notebook plus a file listing injected per request under a token budget; `read_memory` for a prefix and `search_memory` for bounded text search"
  write: "Model tool calls only — no extraction pass. Optimistic concurrency on a version, with an idempotency id derived from the run and tool call"
  update_delete: "`write_memory` appends or replaces one unique fragment; `delete_memory` removes a file and the main notebook is protected. No record of what a delete removed"
  scoping: "`{namespace}/{agent_name}` composed by application code, absent from every tool signature and from the prompt, filtered in SQL by both database stores and re-checked by the toolset on return"
  integration: "A Pydantic AI capability — `Agent(..., capabilities=[Memory(FileStore(...))])` — contributing four tools and a user-role context part"
  background: "None. Writes are synchronous tool calls; snapshot loading is a journaled durable operation; the file store rolls an interrupted operation forward from its journal row"
  trust: "None. A memory is a line in a Markdown file; there is no status, confidence, provenance or source on any of it"
  strengths: "Scope the model can neither name nor see, re-checked on return; idempotent writes under optimistic concurrency; 2,650 lines of tests to 2,483 of code, asserting what must not reach the prompt"
  risks: "Delete is content-free by design, so nothing records that a value was rejected; the file store's operations table clears its payload on success; the Postgres scope predicate is untested"
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

**The repository is being merged into Pydantic AI.** A README notice at
[`e1732b29a6e5980fc6b291ccb60ea7696ad90ecd`](https://github.com/pydantic/pydantic-ai-harness/commit/e1732b29a6e5980fc6b291ccb60ea7696ad90ecd)
(27 September 2026) says development continues in
[pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) under
`src/pydantic_ai_harness`, that this repository will be archived, and that the
PyPI name stays. The monorepo copy has diverged since:
[`ef13bc118077307771a6455c86d8fabeb93363a8`](https://github.com/pydantic/pydantic-ai/commit/ef13bc118077307771a6455c86d8fabeb93363a8)
(28 September 2026) moves `FileStore` onto the run's workspace, replaces its
SQLite journal with a `.memory-operations.json` file keeping the latest 1,024
receipts, and documents that two writers on one directory can lose updates. The
`FileStore` findings below describe this repository at its pin, not that code.

**The mechanism is scope, and it is checked as well as enforced.** The namespace
is `str | Callable[[RunContext], str]`, resolved by application code and
documented as *"never exposed as a tool argument"*; `resolve_scope` composes it
into `{namespace}/{agent_name}` (`_capability.py:134`) and every tool prefixes
paths with it. So a model cannot ask for another tenant's notebook, because there
is no argument in which to name one. [Google's ADK](../adk-python/) makes
`app_name` and `user_id` required keyword arguments instead — strong, and it
still trusts the implementation to use them.

This one **checks**, at three call sites. The subfile listing verifies every
returned path against the requested prefix (`_toolset.py:118`); the bounded
search fallback verifies every path it scans (`:574`); and the store-provided
search results are verified again with a message of their own — `'memory search
backend returned a result outside the requested scope'` (`:628`). The
`MemoryStore` Protocol is public and third-party stores are expected; the
capability treats its own backend as untrusted and validates the boundary on the
way back — a scope filter that asserts it worked, rather than trusting that it
did.

**And neither segment of the scope key reaches the model.** The injected block
carries no heading by default, because it already sits inside `<memory>` markers;
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
(`_toolset.py:331-363`). [Mastra](../mastra-observational-memory/) prevents lost
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

There is nothing to operate. `Memory(FileStore('.agent-memory'))` is the whole
deployment for the local case: Markdown files in a directory, with a SQLite
sidecar holding `file_state`, `file_metadata` and `memory_operations` for
versions, generations and receipts. `InMemoryStore` is the test and ephemeral
case. `_postgres.py` (297 lines) is the multi-tenant one. A separate
`SqliteMemoryStore` keeps content in a `memory_files` table and provides
transactional CAS with the same receipt model.

The store contract is two Protocols: `MemoryStore` with `read`, `get_operation`,
`write`, `delete`, `list_paths`, and `SearchableMemoryStore` adding `search`.
Splitting search into an optional extension is the right shape — a store that
cannot search degrades to a bounded scan the capability performs itself, rather
than being excluded. All four bundled stores implement both.

## 4. Essential Implementation Paths

- `pydantic_ai_harness/memory/_store.py` (1,117) — the Protocols, the in-memory,
  file and SQLite stores, the schemas, CAS, receipts, `FileStore._recover`.
- `pydantic_ai_harness/memory/_toolset.py` (662) — the four tools, scope
  composition, the out-of-scope check, bounded search fallback.
- `pydantic_ai_harness/memory/_capability.py` (358) — namespace resolution,
  the token budget, instruction and context assembly, and `_load_snapshot`.
- `pydantic_ai_harness/memory/_postgres.py` (297) — the multi-tenant backend.
- `tests/memory/test_memory.py` (1,436) and `test_stores.py` (1,214).

## 5. Memory Data Model

A file, and the bookkeeping around it. `MemoryFile` carries path, content and a
version; `file_state` holds `path`, `last_operation_id`, `version` and
`fingerprint`; a `generation` counter in `file_metadata` detects
out-of-band changes to the directory. The fingerprint is what makes an
externally-edited file safe: a person can open `MEMORY.md` in an editor, and the
store notices the content no longer matches what it recorded.

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
`_toolset.py:127-129`), so the capability never asks for an unbounded listing,
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

Concurrency is handled twice over. The version on a file gives optimistic
concurrency: each store raises `MemoryConflictError` on a stale version, and the
tool re-reads and retries up to 16 times before returning `ModelRetry`
(`_toolset.py:357-358`). The `MemoryOperation` id, derived from the run and tool
call, gives idempotency, so the same logical write attempted twice is detected as
a replay rather than applied twice.

Crash recovery differs by store. `FileStore` writes a `prepared` journal row
before touching the file, and `_recover` rolls an interrupted operation forward
from that row, or refuses when the file has been edited since
(`_store.py:548-578`). `SqliteMemoryStore` and `PostgresMemoryStore` write the
content and the receipt in one transaction and need no recovery step.

The lag before a memory is retrievable is zero. Nothing rewrites the store in
the background, and there is no compaction, decay or promotion.

## 8. Agent Integration

`Memory` is a Pydantic AI *capability*: it contributes a toolset and a
per-request context part to an `Agent`. It is re-exported from the package root
(`from pydantic_ai_harness import Memory`) with the stores under
`pydantic_ai_harness.memory`, and the docs say the package is 0.x so the API may
move, with "deprecation warnings and release-note migration guidance" as the
promised path. Spans are emitted with a `_scope_hash` — `sha256(scope)` truncated
to sixteen hex characters — rather than the scope itself, so observability does
not leak tenant identifiers into traces.

**Automatic injection is a durable operation.** `_load_snapshot` carries
`@durable_operation('load_snapshot')` (`_capability.py:243`), and `Memory`
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
`max_tokens` with the engine's history limits in mind" (`docs/memory.md:231-241`)
— the prompt budget doubles as a workflow-history budget.

## 9. Reliability, Safety, and Trust

**The file store's `memory_operations` table is not an audit log, though its
columns look like one.** It records id, fingerprint, status, kind, path, expected
version and new content — everything an audit would want — and then, on success,
`UPDATE memory_operations SET status = 'completed', expected_version = NULL,
new_content = NULL`. The payload is deliberately cleared once it is no longer
needed for recovery. It is a write-ahead journal with a receipt, not a history:
after a successful write, the table knows *that* an operation happened and no
longer knows what it did. `audit_log` is withheld, and the near-miss is exact —
the mechanism that would carry the audit exists and is emptied on purpose.

The intent is not in doubt. A schema migration guarded by `PRAGMA user_version`
runs `UPDATE memory_operations SET expected_version = NULL, new_content = NULL
WHERE status = 'completed' AND (expected_version IS NOT NULL OR new_content IS
NOT NULL)` on open, so a database written before the clearing landed has its old
payloads scrubbed too. This is a retention decision applied retroactively, which
is the reason the mark cannot be argued back in. The other two journals settle
it further: `SqliteMemoryStore`'s operations table
is `id, fingerprint, version, existed` and Postgres's adds `completed` — the
payload columns do not exist. Nothing prunes any of the three, so the one
structure here that only grows is a journal that has forgotten its contents. The
`memory.write` and `memory.delete` spans carry backend, scope hash, outcome, size
and replay, and go to the application's tracer rather than to the store
(`_toolset.py:648-662`).

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
(`test_memory.py:1410-1426`). `Memory.get_toolset` returns the unwrapped toolset,
and neither the capability nor `docs/memory.md` offers the wrapper, so
`human_review` is withheld. The harness's `guardrails` capability can also return
an `approve` verdict for any tool call (`guardrails/_tool_guardrail.py:356`);
nothing in the tree points it at memory.

**Which tier holds the scope guarantee?** Both database stores filter in the
query — `SqliteMemoryStore` with `substr(path, 1, length(?)) = ?`
(`_store.py:1075`, `:1099`) and `PostgresMemoryStore` with
`WHERE starts_with(path, $1)` after `validate_store_prefix` (`_postgres.py:259`,
`:280`). Point reads address the composed `{scope}/{name}`, and `name` cannot
contain `/` (`_toolset.py:32`, `:82`). The toolset then re-checks every path a
listing or search returned. The mark rests on the SQL predicates; the re-check is
what makes a third-party store's bug loud instead of silent.

**The suite holds the SQLite predicate and not the Postgres one.**
`test_local_store_scoped_bounded_search` runs against a real SQLite file and
asserts a higher-scoring `tenant-b` file stays out of a `tenant-a` search
(`test_stores.py:139-153`). The Postgres tests run against a fake connection
whose `fetch` applies its own `path.startswith(prefix)` whatever the SQL says
(`:1050-1053`), and the statement check asserts only that each query carries a
`$` parameter (`:1119-1123`), which `LIMIT $2` satisfies alone. A dropped
`WHERE starts_with` would pass both; in a deployment the toolset re-check would
then raise on the first foreign path.

**Namespaces can have several segments, so one scope can sit inside another.** A
test resolves `namespace='tenant/conversation'` with `agent_name='researcher'`
(`test_memory.py:1253-1258`), and that scope lies under the prefix of namespace
`tenant` with `agent_name='conversation'`. The toolset drops nested paths from the
listing (`_toolset.py:121`), skips them in the fallback scan (`:577`) and raises on
a nested search result (`:631`). So the overlap surfaces as a `RuntimeError` from
the outer scope's `search_memory` when a nested file matches, not as a leak.

The main notebook is protected from deletion. Search results and injected context
are bounded on every axis the code can bound.

External edits surface as `MemoryConflictError` with two distinct messages. A CAS
conflict is "memory path {path} changed before it could be written", and the tool
retries it against a fresh read. An operation replayed after a crash onto a file
someone has since edited is "externally modified memory path {path} blocks
recovery" — recovery *stops* rather than completing over a person's edit. That is
the right answer to the harder of the two cases.

## 10. Tests, Evals, and Benchmarks

2,650 lines of tests against 2,483 lines of implementation, none run for this
reading. The content is better than the ratio: the suite asserts what must
**not** happen.

Nothing was executed, and the screen gives several reasons not to. It flags
twenty-six `conftest.py` files that run on pytest collection, a `Makefile`
default target, `pyproject.toml` and `uv.lock` changed on 26 September 2026,
inside the seven-day cooldown, and an `AGENTS.md` and `CLAUDE.md` addressed to a
reading agent — data here, never instructions. It also flags
`.claude/settings.json` as carrying harness hooks; opening it shows a
`permissions.allow` list of four read-only `gh` commands and no `hooks` key, and
no JSON in the tree has one, so that finding is a false positive.

The injection tests carry the mark. One continues a conversation whose history
holds an injected `'- version one'` after the notebook changed to
`'- version two'`, and asserts the captured context holds exactly one memory
block, containing the new line and not the old, for a live and a
JSON-round-tripped history (`test_memory.py:1027-1057`). Another seeds a legacy
unqualified block carrying `'stale fact'` and asserts `'durable fact'` is present
and `'stale fact'` is not (`:1190-1218`). Each has its positive control in the
same assertions, and both target the failure the design worries about: stale
memory reaching the prompt.

At the store tier, `test_local_store_scoped_bounded_search` asserts exact
equality on a `tenant-a` search whose `tenant-b` file scores highest, on the
in-memory, file and SQLite stores (`test_stores.py:139-153`). The toolset's
`test_native_search_is_bounded_and_tenant_isolated` asserts `'secret'` is absent
from an `alice` search, and that assertion cannot fail on an isolation bug: with
`max_search_files=2`, the two `alice` paths exhaust the scan before
`bob/main/secret.md` in sorted order (`test_memory.py:607-627`). Its budget
assertions are the real content of that test. `test_delete_existing_is_content_free`
asserts the deleted body is absent from the delete result (`:560-565`).

Two more of that kind guard the scope key itself. `test_heading_is_omitted_by_default`
seeds `main/MEMORY.md` with `'- a durable fact'`, captures the injected context,
and asserts it starts with `<memory>`, contains no `## ` line, and does not
contain the string `main` (`:712-724`); a spec-construction test sets
`agent_name='storage-id'` with `heading='Team notes'` and asserts the rendered
instructions contain `## Team notes` and not `storage-id` (`:1322`). Both fail the
moment the storage key leaks into the prompt — the specific regression the
`heading` field was introduced to prevent.

`negative_eval` is earned. One test skips itself without `temporalio`
(`:1428-1429`). There is no benchmark, no retrieval-quality measurement and no
published number — consistent with a capability whose retrieval is a bounded
scan and makes no accuracy claim at all.

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

- **Clearing the payload of the only table that records mutations.** Recovery
  and audit want the same row and disagree about its lifetime; if you want both,
  write the audit row separately before you clear the journal.
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
teams usually discover they needed after shipping. A new adopter installs the
same PyPI package, released from pydantic/pydantic-ai, whose `FileStore` is not
the one read here.

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
- **Does anything bound the growth of the operations tables?** No `DELETE`
  touches any of the three, so completed receipts accumulate for the life of the
  store. For a per-agent notebook that is small; for a shared Postgres table
  across many tenants it is the row count nobody is watching. At the monorepo
  commit named in section 1, `FileStore` keeps the latest 1,024 receipts, and the
  SQLite and Postgres operations tables there have no `DELETE` either.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `pydantic_ai_harness/memory/_store.py` | 1,117 | Protocols, three stores, schemas, CAS, receipts, recovery; the journal scrub at `:464-469`, `_recover` at `:548-578` with the clearing `UPDATE` at `:575`, the SQLite prefix predicate at `:1075` and `:1099` |
| `pydantic_ai_harness/memory/_toolset.py` | 662 | Four tools, scope composition, the three out-of-scope raises at `:118`, `:574`, `:628`, the nested-result raise at `:631`, the scope hash at `:644` |
| `pydantic_ai_harness/memory/_capability.py` | 358 | Namespace resolution at `:131-136`, the `heading` field at `:65`, the token budget, `_load_snapshot` at `:243` |
| `pydantic_ai_harness/memory/_postgres.py` | 297 | Multi-tenant backend; `starts_with` prefix filter at `:259` and `:280`, the payload-free operations table at `:93-96` |
| `tests/memory/test_memory.py` | 1,436 | Tool behaviour, injection bounds, the negative assertions at `:560-565`, `:607-627`, `:712-724`, `:1027-1057` and `:1190-1218`, the approval wrapper at `:1410-1426` |
| `tests/memory/test_stores.py` | 1,214 | Store conformance, CAS, replay, recovery; the cross-tenant search at `:139-153`, the fake Postgres `fetch` at `:1050-1053` |
| `docs/memory.md` | 259 | The notebook model, injection modes, limits, the durable-execution table and history-budget note at `:231-241` |

**Recorded searches.** Run from a checkout at
`e1732b29a6e5980fc6b291ccb60ea7696ad90ecd`; each backs an absence claim above.

- **No tool names a scope.** `grep -n 'async def write_memory\|async def read_memory\|async def delete_memory\|async def search_memory' -A 8 pydantic_ai_harness/memory/_toolset.py`
  — the parameters are `content`, `file`, `old_text`, `query`, and nothing else.
- **The scope key never reaches the prompt.**
  `grep -rn 'agent_name' pydantic_ai_harness/memory/*.py` — four hits, all in
  `_capability.py`: the field, the `resolve_scope` composition, and the two
  `from_spec` plumbing lines. None is a render call.
- **Nothing prunes the journals.**
  `grep -nE 'DELETE FROM|prune|vacuum' pydantic_ai_harness/memory/*.py`
  — four `DELETE` statements, on `file_state` twice, `memory_files` and the
  Postgres content table; none on an operations table.
- **The Postgres predicate is untested.** `grep -rn 'starts_with(path' --include='*.py' .`
  — two hits, both in `_postgres.py`; no test names the predicate.
- **Nothing offers the approval wrapper.**
  `grep -rn 'approval' pydantic_ai_harness/memory/ docs/memory.md` — nothing;
  the one use is `tests/memory/test_memory.py:1410-1426`.
- **Nothing outside the memory package wires its tools.**
  `grep -rln 'write_memory\|delete_memory' --include='*.py' --include='*.md' .`
  — the package, its tests, `docs/memory.md`, and
  `agent_docs/capability-authoring.md:201`, which names `write_memory` as an
  example of a fixed tool name.

## History

**2026-09-29** — [`e1732b29a6e5980fc6b291ccb60ea7696ad90ecd`](https://github.com/pydantic/pydantic-ai-harness/commit/e1732b29a6e5980fc6b291ccb60ea7696ad90ecd) — 141 commits on; `pydantic_ai_harness/memory` and `tests/memory` have identical trees at both commits, and `docs/memory.md` changed only its front-matter description. The head commit announces the merge into pydantic/pydantic-ai ([section 1](#1-executive-summary)). Marks unchanged; both records re-cited ([section 9](#9-reliability-safety-and-trust), [section 10](#10-tests-evals-and-benchmarks)). Corrected: four bundled stores, not three; `_recover` rolls forward or refuses, never back; CAS exhaustion returns `ModelRetry`; the `'secret'` case cited for `negative_eval` cannot fail on isolation; the Postgres predicate the scope mark rests on runs only against a self-filtering fake; the docs anchors were four lines off. Screen: one `RUNS` (false positive), three `FRESH`, twenty-seven `EXEC`, one `FLOAT`, two `AGENT`. Nothing installed, built or run.


**2026-09-17** — [`58400a1d1b2b5625aadbb154d2fea1030014337c`](https://github.com/pydantic/pydantic-ai-harness/commit/58400a1d1b2b5625aadbb154d2fea1030014337c) — re-pinned after 14 commits. All five anchored files are byte-identical at both commits: the memory capability and its toolset, the Postgres store, and both cited test files. Both marks stand on unchanged code and every anchor here is exact at the new pin. Nothing was installed, built or run.

**2026-09-11** — [`58400a1d1b2b5625aadbb154d2fea1030014337c`](https://github.com/pydantic/pydantic-ai-harness/commit/58400a1d1b2b5625aadbb154d2fea1030014337c) — re-read. Screened again, and the screen is louder than it was: a `RUNS` finding on `.claude/settings.json`, an `AGENT` finding on each of `AGENTS.md` and `CLAUDE.md`, sixteen `conftest.py` files that execute on pytest collection, a `Makefile` default target, and `pyproject.toml`/`uv.lock` changed the same day. The `RUNS` finding was opened and is a false positive: the file holds a `permissions.allow` list of four read-only `gh` commands and no `hooks` key, and no `"hooks"` key exists in any JSON in the tree. The tree was read, never installed, and nothing was run. Marks unchanged at `scope_enforced` and `negative_eval`, with `capability_evidence` records added for both; the scope record names the SQL prefix filter in `PostgresMemoryStore` as the tier the mark rests on and the toolset re-check as the backstop, which answers one of the questions the previous entry left open. The other is answered too: an external edit onto a file with an in-flight operation refuses to complete recovery rather than overwriting it. The whole package grew by 316 files and 77,735 insertions, of which the memory capability is 283 lines across five files. Two changes matter. The injected block no longer carries `## Agent Memory ({agent_name})`: the storage segment is documented as never reaching the prompt, an optional `heading` labels the block when an agent carries several notebooks, and two committed tests assert the storage key is absent from a populated block and from the rendered instructions. And automatic snapshot loading is now `@durable_operation('load_snapshot')` with a constant capability id, so it is journaled under Temporal, Prefect and DBOS — with a failure path that returns the exception type rather than inheriting the engine's retry policy, and two residual constraints stated in the docs rather than left to be discovered. Corrections of counts: the capability is 2,483 lines against 2,650 of test, `_capability.py` is 358, `test_memory.py` is 1,436, and the scope re-check has three call sites rather than one.

**2026-07-30** — [`39ee7e08101c54b1ddf9c1e3a7f603f09ae34555`](https://github.com/pydantic/pydantic-ai-harness/commit/39ee7e08101c54b1ddf9c1e3a7f603f09ae34555) — first reading.

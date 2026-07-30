---
title: "Gobii"
eyebrow: "Memory as a database the agent writes"
description: "The durable memory is a SQLite file the agent designs and queries itself, sandboxed by a sqlite3 authorizer — and the eight tables the platform projects into it are all dropped before it is saved, with each one's mortality written into the schema prompt."
root: ../..
page_kind: system
source_name: "gobii-ai/gobii-platform"
source_url: https://github.com/gobii-ai/gobii-platform
revision: 26844673ac9f134e2ad3851a12dd26762d94c3a9
revision_url: https://github.com/gobii-ai/gobii-platform/commit/26844673ac9f134e2ad3851a12dd26762d94c3a9
analyzed_at: 2026-07-30
capabilities: "scope_enforced"
matrix:
  memory_unit: "A row in a table the agent invented. There is no framework-defined memory record — the schema is whatever the model wrote `CREATE TABLE` for"
  storage: "One zstd-compressed SQLite file per agent in Django's `default_storage`, restored per run through a validating subprocess; Postgres holds the platform's own 183 models"
  retrieval: "SQL. The agent is shown a generated schema prompt capped at 30,000 bytes and 25 tables, then writes queries against it"
  write: "SQL, through a batch tool with autocorrect, query-quality checks and recovery; the file is validated and re-uploaded after the cycle"
  update_delete: "`UPDATE` and `DELETE FROM`, written by the model. No framework-level correction, no record of what was removed"
  scoping: "One database file per agent UUID, with `ATTACH`/`DETACH` denied by a `sqlite3` authorizer so SQL cannot reach another agent's file; Django models are foreign-keyed to the agent"
  integration: "A Django platform — persistent agents with email, SMS, Discord and web endpoints, MCP servers, schedules, a browser-use agent, skills and a kanban plan"
  background: "Celery. Comms and step snapshot chains summarise history incrementally, each linked to its predecessor with an inclusive cut-off"
  trust: "None. A row is true because the model inserted it; there is no status, confidence or provenance column unless the model invented one"
  strengths: "An explicit persistence contract — eight built-in tables declared ephemeral and dropped before save, with each one's mortality stated in the prompt the model reads; a real SQL authorizer sandbox"
  risks: "The schema is model-authored, so nobody can write a query to correct or erase a subject without first discovering what tables exist"
---

## 1. Executive Summary

Gobii is a hosted platform for persistent agents — a Django monolith of 183
models and roughly 473,000 lines of Python, MIT-licensed with an explicitly
carved-out `proprietary/` module and a trademark notice. Agents have email, SMS,
Discord and web endpoints, cron schedules, MCP servers, a browser-use agent,
skills, secrets, a filespace and a kanban plan.

**Its memory is a SQLite database that the agent designs and queries itself**,
and that is not a shape this atlas has seen before. There is no `MemoryRecord`,
no extraction pass, no embedding and no vector store on the memory path. There
is one file per agent, a generated schema prompt, and a SQL tool. What the agent
remembers is whatever it wrote `CREATE TABLE` for.

Around that sit roughly 12,000 lines of tooling in thirteen `sqlite_*` modules —
`sqlite_batch` (2,515), `sqlite_analysis` (1,506), `sqlite_state` (1,316),
`sqlite_guardrails` (1,316), plus autocorrect, recovery, digest, query quality,
skills and config. The investment is not in deciding what to remember; it is in
making a language model's SQL survive contact with a real database.

**The mechanism worth taking is the persistence contract.** Gobii projects its
own platform state into the agent's database as eight double-underscore tables —
`__messages`, `__files`, `__contacts`, `__agent_config`, `__agent_schedules`,
`__agent_skills`, `__tool_results`, `__kanban_cards` — so the agent can join its
own data against the platform's in one query. Every one of them is listed in
`EPHEMERAL_TABLES`, and `_drop_ephemeral_tables` executes `DROP TABLE IF EXISTS`
on all eight before the file is persisted. The durable artifact contains only
what the agent created.

And the model is *told which is which*. `BUILTIN_TABLE_NOTES` carries a phrase
per table — `"built-in, ephemeral (dropped before persistence)"`,
`"built-in, ephemeral (recent messages snapshot for this cycle)"`,
`"built-in, ephemeral (reset every LLM call)"` — that goes into the schema
prompt. Almost every system in this atlas decides what survives and leaves the
model to infer it. This one writes the mortality of each table into the prompt
the model reads before it decides where to put something.

## 2. Mental Model

There is no epistemic model, and the absence is structural rather than
neglectful: **there is no schema to hang one on**. A trust state needs a column,
a column needs a table, and the tables belong to the model. If an agent wants
`confidence` or `verified_at`, it can create them; nothing in Gobii asks it to,
and nothing in Gobii would understand them if it did.

What Gobii models instead is a **cycle**. A run restores the database, mounts
the platform's state as ephemeral tables, hands the model a schema prompt, lets
it read and write SQL, drops the ephemeral tables, validates the file, and
uploads it. Durability is a property of the file, and the boundary between
"this cycle" and "forever" is drawn by one set literal.

The consequence is the report's central tension. Memory that is a relational
database is the most *queryable* memory in this atlas — an agent can compute
over its own history in ways a vector store cannot. It is also the least
*legible from outside*, because the shape is discovered rather than declared.

## 3. Architecture

The platform needs Postgres, Redis, Celery and blob storage; the memory path
needs the last of those. `sqlite_storage_key(agent_uuid)` gives one key per
agent. `_restore_sqlite_db_from_storage` opens it from `default_storage`,
decompresses it with zstd **in a subprocess with a 120-second timeout**, and
validates it before use — a decompression bomb and a corrupt file are both
treated as expected conditions rather than crashes.
`create_validated_sqlite_snapshot` and `validate_sqlite_file` guard the write
side, and `sqlite_recovery.py` distinguishes a recovered failure from an
unrecoverable one in its telemetry.

Beside it, Postgres holds everything the platform owns: steps, tool calls,
messages, conversations, kanban cards, skills, secrets, filespace nodes, and two
snapshot chains.

## 4. Essential Implementation Paths

- `api/agent/tools/sqlite_state.py` (1,316) — the table constants, the
  ephemeral set, the schema prompt budget, storage keys, restore and persist.
- `api/agent/tools/sqlite_guardrails.py` (1,316) — the authorizer, the safe
  custom functions, the statement checks.
- `api/agent/tools/sqlite_batch.py` (2,515) — the agent-facing SQL tool.
- `api/agent/tools/sqlite_analysis.py` (1,506) and `sqlite_digest.py` — turning
  a table into something a prompt can hold.
- `api/models.py` — `PersistentAgent` (charter), `PersistentAgentStep`,
  `PersistentAgentCommsSnapshot`, `PersistentAgentStepSnapshot`,
  `PersistentAgentKanbanCard`, `PersistentAgentSkill`.
- `console/agent_chat/plan_events.py` — the kanban feed.

## 5. Memory Data Model

Two halves that do not share a vocabulary.

**Agent-side**: unknown by construction. The only fixed names are the eight
ephemeral system tables, and the durable content is model-authored. The
constants that bound it are the interesting part —
`MAX_PROMPT_BYTES = 30000`, `MAX_TABLES = 25`, three sample rows and eight
sample columns per table in the prompt, with `sqlite_analysis` producing column
summaries, detected types (it sniffs email, URL, UUID, ISO date, IPv4, phone
patterns), and JSON/CSV detection thresholds. The schema prompt is a compression
problem, and it is solved carefully.

**Platform-side**: `PersistentAgent.charter` is a `TextField` — the agent's
durable purpose, human-authored and human-editable, with a
`short_description_charter_hash` so a generated summary can be invalidated when
the charter changes. `PersistentAgentKanbanCard` carries
`todo`/`doing`/`done`, a priority and a `completed_at`. Both snapshot models
carry a `summary`, a `snapshot_until` upper bound, and a `previous_snapshot`
one-to-one link, with a unique constraint on `(agent, snapshot_until)` — an
incrementally generated chain of summaries over history that is *not* deleted,
which is [evidence before belief](../../patterns/evidence-before-belief/) in the
shape the pattern recommends.

No validity time anywhere; every clock is a record clock.

## 6. Retrieval Mechanics

The agent writes `SELECT`. That is the whole retrieval story, and it is both the
strongest and the weakest thing here — strongest because aggregation, joins,
`GROUP BY` and window functions are all available to an agent reasoning over its
own history, which no vector store offers; weakest because recall quality is the
model's SQL, and nothing measures it.

The support around it is real. `sqlite_autocorrect` repairs malformed
statements, `sqlite_query_quality` inspects them, `json_goldilocks` (1,166
lines) and the digest modules size results to fit a prompt, and the guardrails
register safe pure-computation functions such as `REGEXP` so common patterns do
not require the blocked ones.

## 7. Write Mechanics

Writes block, and they are the model's own SQL through the batch tool. There is
no extraction pass: nothing is remembered that the agent did not decide to
write, which is the [zero-LLM-capture](../../patterns/zero-llm-capture/) trade
inverted — all capture is deliberate, and none is automatic.

Persistence happens at the end of a cycle: drop the eight ephemeral tables,
validate, compress, upload, with failures classified as
`sqlite_persistence_upload_failed`, `sqlite_persistence_failed`, or recovered.
The background work is Celery and the snapshot chains, which summarise comms and
steps incrementally rather than rewriting a single running summary — so a
regeneration can start from the previous cut-off instead of from the beginning.

## 8. Agent Integration

This is a product, not a library: agents own email addresses, phone numbers,
Discord channels and web sessions; they can spawn other agents, link as peers,
request human input, solicit credentials, and run scheduled. Memory is one
subsystem inside it, reachable only through the agent's own tool calls.

## 9. Reliability, Safety, and Trust

**The authorizer is the scope mechanism, and it is the right place for it.**
`_sqlite_authorizer` denies `SQLITE_ATTACH` and `SQLITE_DETACH`, so no query can
mount another agent's database file; denies `load_extension`, `readfile`,
`writefile`, `edit` and `fts3_tokenizer`, closing the filesystem escapes SQL
offers; and denies the `database_list`, `key`, `rekey`, `temp_store` and
`temp_store_directory` pragmas. Isolation is therefore **partition plus
capability** — one file per agent UUID, and no SQL verb that can reach across —
rather than a `WHERE` clause. On the Django side every model is foreign-keyed to
the agent and filtered on read. `scope_enforced` is earned, and the shape is
worth naming because it is the only instance in the corpus where the boundary is
enforced by an authorizer callback rather than by a query predicate.

**No tombstone, and the reason is the schema.** Correction is whatever `DELETE
FROM` the model writes. Nothing records that a value was rejected, and nothing
*could* generically — a platform operator asked to erase everything about a
named person cannot write that query, because the tables are different for every
agent and were invented by a model. This is the sharpest version of a problem
this atlas keeps finding: here it is not that deletion is unimplemented, it is
that deletion is not expressible at the platform level at all.

**No trust state and no bi-temporality**, for the same reason.

**The kanban event log is not an audit log, and the near-miss is instructive.**
`PersistentAgentKanbanEvent` and `PersistentAgentKanbanEventChange` record
created / started / completed / updated / deleted / archived per card with
`from_status` → `to_status`, and `card_id` is a bare `UUIDField` rather than a
foreign key, so the history survives the card's deletion and keeps a
denormalised `title`. That is exactly the data model an audit wants. But
`persist_plan_event` lives in `console/agent_chat/` and is called from the
console's signals and timeline — it is the activity feed the web UI renders,
built from a payload with `displayText`, `snapshot_files` and `snapshot_messages`
and made idempotent on a `cursor_identifier`. It records what the interface
showed, not what the store did, so a change that never reaches the feed is
unrecorded. The mark is withheld.

**Prospective memory, partially.** The kanban card is a durable commitment with
an enforced `todo`/`doing`/`done` lifecycle and a `completed_at` — two of the
three requirements the atlas's [prospective memory
section](../../compare/#the-category-almost-nothing-models-prospective-memory)
names, which puts Gobii beside NOOA and MineContext in the emptiest category
here. The third is missing in both directions: triggers are cron
(`PersistentAgentCronTrigger`, `PersistentAgentSchedule`), not semantic, and
there is no way to reject a commitment such that it cannot be re-created. Its
SQLite mirror, `__kanban_cards`, is ephemeral.

## 10. Tests, Evals, and Benchmarks

381 test functions across the SQLite-named test files alone, none run here,
covering the schema prompt, digest, recovery, agent config, schedules, messages
and contacts tables, batch behaviour, and cross-process coordination. There is
also an eval framework in the platform proper — `EvalSuiteRun`, `EvalRun`,
`EvalRunTask`, with an ephemeral-agent-per-scenario strategy — aimed at agent
task performance rather than at memory.

No negative retrieval assertion was found. The obvious one is absent and would
be cheap: nothing asserts that the eight ephemeral tables are gone from a
persisted file. `_drop_ephemeral_tables` is the single line standing between a
per-cycle projection of the user's messages and contacts and a durable copy of
them in blob storage, and it is not covered by a test that says so.

No memory benchmark, no retrieval-quality measurement, and no published numbers
— so nothing claimed and nothing to check.

## 11. For Your Own Build

### Steal

- **Declare which tables are ephemeral, in one place, and drop them on the way
  out.** `EPHEMERAL_TABLES` plus `_drop_ephemeral_tables` is about fifteen lines
  and it makes the persistence boundary a value you can read instead of a
  behaviour you have to trace.
- **Tell the model which of its tables survive.** `BUILTIN_TABLE_NOTES` putting
  `"ephemeral (dropped before persistence)"` into the schema prompt is the
  cheapest honesty mechanism in this report. A model that does not know what
  persists will put durable facts in a scratch table.
- **Mount the platform's own state as tables the agent can join against.**
  Messages, files, contacts and schedules as queryable relations means the agent
  can ask "which contacts have I not emailed this month" instead of being handed
  a summary that already decided.
- **Use `sqlite3.set_authorizer` if you let a model write SQL.** Denying
  `ATTACH`, `load_extension`, `readfile` and `writefile` closes the escapes that
  make agent-authored SQL frightening, and it is enforcement at the engine
  rather than a regex over the statement.
- **Decompress untrusted archives in a subprocess with a timeout.** 120 seconds
  and a validation pass, treating a corrupt database as an expected state with
  its own telemetry classification.
- **Chain your summaries and keep the source.** `previous_snapshot` plus an
  inclusive `snapshot_until` and a uniqueness constraint means summarisation is
  incremental and re-derivable, and the underlying steps and messages are still
  there.

### Avoid

- **Letting the model own the schema if you will ever need to erase a subject.**
  A per-agent, model-authored database has no shape an operator can write a
  deletion query against. If a right-to-erasure request must be satisfiable,
  something in the durable store has to be declared.
- **Shipping the drop and not testing it.** One missing line in the persist path
  turns an ephemeral projection of a user's contacts and messages into a durable
  copy in object storage, and no test asserts it did not happen.
- **Building the audit's data model in the UI layer.** The kanban change records
  are shaped exactly like an audit trail and are written by the console for
  rendering, so they cover what was displayed rather than what was stored.

### Fit

Gobii suits an agent whose memory is genuinely *tabular* — scraped listings,
tracked prices, contact pipelines, anything where the useful question is an
aggregate. For that, SQL beats every retrieval mechanism in this atlas, and the
supporting apparatus is serious enough that model-written SQL mostly works.

It is the wrong model where memory is a set of beliefs about a person that may
turn out to be wrong. There is no place to record that a value was rejected, no
status to withhold a doubtful one, and no operator-level way to find the value
again once an agent has filed it under a name only it chose.

## 12. Open Questions

- **Do the ephemeral tables actually get dropped in every persist path?** One
  call site, no test. It is the highest-value assertion the repository is
  missing.
- **How large do these databases get, and what happens then?** The schema prompt
  caps at 25 tables and 30,000 bytes; the file has no stated cap, and nothing
  prunes it.
- **What does an agent's SQL actually look like after a year?** The whole design
  rests on model-authored schemas staying coherent across hundreds of cycles and
  model upgrades, and nothing in the repository measures schema drift.
- **Is the charter reviewed after edit?** It is human-editable and hashed for
  summary invalidation; whether an agent can rewrite its own charter, and
  whether anyone reviews that, was not traced.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `api/models.py` | 13,931 | 183 models including the agent, steps, snapshots, kanban, skills |
| `api/agent/tools/sqlite_batch.py` | 2,515 | The agent-facing SQL tool |
| `api/agent/tools/sqlite_analysis.py` | 1,506 | Column summaries, type sniffing, prompt-sized samples |
| `api/agent/tools/sqlite_state.py` | 1,316 | Ephemeral set, schema prompt, storage key, restore and persist |
| `api/agent/tools/sqlite_guardrails.py` | 1,316 | The authorizer and safe functions |
| `api/agent/tools/json_goldilocks.py` | 1,166 | Fitting results into a prompt |
| `console/agent_chat/plan_events.py` | — | The kanban activity feed |
| `tests/unit/test_sqlite_*.py` | 381 tests | Schema prompt, recovery, batch, coordination |

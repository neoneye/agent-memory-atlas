---
title: "OpenYantra"
eyebrow: "One gated writer, one workbook, and a queue lock that may not be there"
description: "A local personal-memory toolkit keeping a user model in a LibreOffice workbook behind one gated writer, beside a separate JSON store for MCP memory."
root: ../..
page_kind: system
source_name: "revanthlevaka/OpenYantra"
source_url: https://github.com/revanthlevaka/OpenYantra
archive_name: "revanthlevaka--OpenYantra"
revision: 27aa1e3eecb4769a1a8a82c9de62269a0605b375
revision_url: https://github.com/revanthlevaka/OpenYantra/commit/27aa1e3eecb4769a1a8a82c9de62269a0605b375
analyzed_at: 2026-11-08
licence: "MIT in LICENSE, pyproject.toml and GitHub's detection; SPEC_LICENSE dedicates the specification, table schemas, sheet templates and interchange formats to the public domain under CC0 1.0"
size: "11,019 lines of Python outside tests: 10,966 in openyantra/ (core.py 2,733, yantra_sqlite.py 1,003, yantra_ui.py 790) and 53 in examples/; 3,275 lines of HTML and JavaScript in UI/v4; 785 lines of installer shell and PowerShell"
activity: "65 commits, 20 March – 8 November 2026: 48 by Revanth Levaka under three addresses, 13 authored as Claude, 4 by dependabot; 49 of them on 7 November; the repository was created on 15 March 2026 and its first commit is already v2.12"
tests: "81 pytest functions in 17 files, 2,022 lines with conftest.py, run by ci.yml on Ubuntu with Python 3.9–3.12 and on macOS and Windows with 3.11; none run for this reading"
capabilities: "audit_log, human_review, negative_eval"
capability_evidence:
  audit_log: "sheet engine — the Agrasandhanī ledger sheet | openyantra/core.py:346-386, :388-392, :507-528 | `LedgerAgent._process` appends one ledger row for every request that reaches it — `written`, `rejected` or `conflict` — with timestamp, request id, agent, sheet, operation, row identifier, confidence, source, importance and a truncated SHA-256 of the whole request; `_log_audit` is the sheet's only writer and appends, and `_validate` refuses any request addressed to the ledger itself | one test reads it back, through the replay guard (tests/test_atlas_audit_fixes.py:107-131). Limits: an `add` entry names no row and no entry carries a value; the MCP memory_* tools, session-log archival, edge writes and direct LibreOffice edits leave no entry; `_process` skips a request whose id the ledger already holds, so a replay is applied again only when it was interrupted between the sheet write and its ledger row, or overlaps another process still inside `_process`; `yantra integrity` checks only that a signature starts with `sha256:`"
  human_review: "sheet engine — the Raksha quarantine | openyantra/core.py:618-636, :1361-1403, openyantra/yantra_ui.py:238-241, UI/v4/dashboard.html:857-866, :946-949 | a sheet write whose text matches a confirmed injection, jailbreak, impersonation or encoding pattern is copied to the Quarantine sheet with status Quarantined and does not reach its target sheet, the search index or any context; it lands only when a person presses Release in the dashboard, which posts to a route on the local web server. None of the sixteen MCP tools, the three framework adapters, the Telegram bot or the CLI exposes a release verb, and `_validate` rejects any write addressed to the Quarantine sheet, so the producing agent cannot clear or rewrite its own hold | no test. Limits: the dashboard shows the matched pattern, not the held content; release never changes the row's status, so the item stays listed and can be released again; there is no reject verb; the released row is relabelled User-stated, High, added by User; the route is unauthenticated unless a passkey is enabled; MCP read_sheet returns the held text to the agent"
  negative_eval: "sheet engine — the session context | tests/test_negative_eval.py:61-80, :18-58 | two open loops are written and one resolved; `load_session_context` must return the live loop and must not return the resolved one, the read the MCP `get_system_context` tool serves. A second case holds an injected task in Quarantine and asserts it is absent from `load_session_context` and `build_context_markdown`, beside a real task that must be present | the search arm of the second case has no positive control and returns an empty list when the search extras are missing, so it cannot fail there; a third case keeps filtered filler out of the Tasks sheet and the context, which is a write outcome; the file's docstring lists six cases and it holds three"
stack_storage: "files, sqlite, faiss"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A row in one of fourteen workbook sheets (identity, goals, projects, people, preferences, beliefs, tasks, open loops, session log, agent config, ledger, inbox, corrections, quarantine) with Confidence, Source, Importance and Last Updated; separately a keyed JSON note for the MCP memory tools"
  storage: "chitrapat.ods, rewritten whole by pandas and odfpy through a temporary file and an atomic replace on every write; a sanchitta.json write queue; FAISS, BM25 and registry files beside it; cognitive_memories.json; a chitrapat.db SQLite file whose only written table is a graph of edges"
  retrieval: "A session-context builder filtering projects, loops, goals and tasks by status; FAISS over TF-IDF with SVD or MiniLM fused with BM25, then importance and recency, with no status filter; substring search on the JSON notes; a six-hop bidirectional edge walk"
  write: "Explicit calls only, from MCP, the dashboard and HUD, the CLI, Telegram, mail, an iOS Shortcut endpoint, an Obsidian import, a git post-commit hook and three framework adapters; no model on the write path"
  update_delete: "Update matches the first column and appends a new row when nothing matches; resolve and complete set a status column; the delete operation has no branch and changes nothing; the JSON notes are overwritten by key or hard-deleted"
  scoping: "One workbook per person and no scope key; an Agent column selects which configured instructions each agent receives; the JSON notes carry an agent name no read filters on"
  integration: "A hand-rolled sixteen-tool stdio MCP server, a FastAPI dashboard and pywebview HUD on 127.0.0.1:7331, a CLI, LangChain, CrewAI and OpenClaw adapters, and a setup command writing Claude Desktop and Cursor configs"
  background: "None scheduled; Nidra runs on demand, auto-resolves open loops whose topic words appear in recent session decisions, writes a summary, and adds regex-matched preference phrases to Beliefs at High confidence, one topic per phrase, skipping phrases already stored or found in a reverted decision"
  trust: "A regex scan can hold a write in quarantine for a person to release; Confidence and Source are caller-supplied labels, and the MCP add_task and add_project writes are stamped User-stated"
  strengths: "One choke point that scans, filters, validates and ledgers every sheet write; a quarantine the agent's tools cannot release; a store a person can open and read in LibreOffice"
  risks: "The MCP memory tools and the dashboard's JSON route pass only secret redaction; processes rewrite one workbook with no file lock, and the queue's lock needs a package no manifest installs, so concurrent writers lose updates and a replay overlapping another process's write applies it twice; the SQLite engine and incremental index have no producer"
---

## 1. Executive Summary

OpenYantra is a local, single-user memory toolkit that keeps a structured model
of one person as sheets in a LibreOffice workbook, written through one gated
writer and served to Claude Desktop and Cursor over MCP. The gate is the
notable part: an injection scan that can hold a write for a person to release,
an admission filter, vocabulary checks, and a row on an append-only ledger
sheet. The weakness is around the gate. The MCP memory tools and the dashboard
write a separate JSON store that only secret redaction reaches. Processes share
the workbook with no file lock, and the queue's file lock is skipped unless
`portalocker` is installed, which no manifest names. Nidra's preference
promotion adds a matched phrase to Beliefs at High confidence once, under its
own topic. The SQLite engine has no producer.

`LICENSE` is the MIT text; `SPEC_LICENSE` dedicates the protocol's table
schemas, sheet templates and interchange formats to the public domain under
CC0 1.0.

The README describes a SQLite WAL store shared by the HUD, the CLI and the MCP
server. At this commit the HUD and the MCP sheet tools share the workbook, the
MCP memory tools use a JSON file, and SQLite holds only hand-drawn graph edges.
Three marks are earned, all on the sheet engine: `audit_log` on the ledger
sheet, `human_review` on the quarantine, and `negative_eval` on a resolved loop
the session context must leave out. Section 9 gives the reason for each of the
four withheld.

## 2. Mental Model

A memory is a **row in a sheet** of `chitrapat.ods`. The sheets are Identity,
Goals, Projects, People, Preferences, Beliefs, Tasks, Open Loops, Session Log,
Agent Config, the ledger (Agrasandhanī), Inbox and Corrections, plus Quarantine
and Security Log created on first use. A row is identified by its first column
— the attribute, task text or loop topic — and carries `Confidence` (High,
Medium, Low, Inferred), `Source` (User-stated, Agent-observed, Agent-inferred,
System), `Importance` 1 to 10 and `Last Updated` (`openyantra/core.py:75-103`,
`:2637-2733`).

A row becomes a belief by passing four gates in order, and nothing marks it as
less than true afterwards:

- **Raksha** redacts secrets, then scans the joined field text. A confirmed
  injection, jailbreak, impersonation or zero-width pattern sends the write to
  Quarantine; a suspicious one adds a `_security_flag` column and lets it
  through (`core.py:618-636`, `openyantra/yantra_security.py:457-555`).
- **Admission** drops a write whose content contains a noise phrase, whose
  content is at most two words including a filler word, or whose importance is
  below 2, with no ledger row (`core.py:116-168`).
- **Validation** rejects an unknown sheet or a value outside the controlled
  vocabulary (`core.py:388-403`).
- **Conflict** refuses an update that would change a High-confidence field from
  a request that is not High (`core.py:405-423`).

A row stops counting through a lifecycle column read by the context builder: a
loop resolved, a task Done, a project not Active, a goal not Active or In
Progress (`core.py:1065-1079`). Identity, People, Preferences and Beliefs rows have
no such column; they change only by overwrite. The `delete` operation is in the
vocabulary and has no branch in the committer, so nothing is ever deleted
(`core.py:84`, `:429-481`). A git revert adds a new Session Log row labelled
*Reverted / Superseded Decision*; the reverted commit's own row is untouched
(`openyantra/yantra_git.py:106-127`).

The **cognitive store** is a second memory with no relation to the first: a JSON
list of notes with a key, a type, an agent name, content, tags and a timestamp.
A write replaces the note with the same key case-insensitively, and a delete
removes it (`openyantra/cognitive_db.py:40-120`). Only the MCP `memory_*` tools
and the dashboard's cognitive routes reach it, and no context builder reads it.

Control is hybrid. The agent writes through MCP, a person writes through the
HUD, the dashboard, the CLI, Telegram, LibreOffice or Obsidian, and Nidra
resolves loops when someone runs it.

```mermaid
%% caption: a sheet row is believed once it clears four gates; the queue replays what a crash or another process left in it, skipping a request the ledger already holds; Nidra promotes a phrase once under its own topic; the MCP memory tools and the dashboard write a second store that only secret redaction reaches
flowchart TD
  subgraph writers["Sheet writers"]
    direction TB
    W1["six MCP sheet tools,<br/>as Cognitive-MCP"]
    W2["HUD, dashboard, CLI,<br/>Telegram, mail, vault"]
    W3["git post-commit hook"]
    W1 ~~~ W2 ~~~ W3
  end
  writers --> RK{"Raksha: a confirmed<br/>injection pattern?"}
  RK -->|"yes"| Q["Quarantine sheet<br/>waits for Release<br/>in the dashboard"]
  RK -->|"no"| SQ["appended to<br/>sanchitta.json,<br/>removed once processed"]
  Q -->|"person releases"| SQ
  SQ --> LG{"request id<br/>already in<br/>the ledger?"}
  LG -->|"yes"| SKIP["skipped"]
  LG -->|"no"| GATE{"filler, unknown<br/>sheet, bad<br/>vocabulary, conflict?"}
  GATE -->|"yes"| DROP["dropped; a rejected<br/>or conflict ledger row"]
  GATE -->|"no"| ROW["row in chitrapat.ods<br/>plus a written<br/>ledger row"]
  ROW --> CTX["session context:<br/>Active, unresolved,<br/>not Done"]
  ROW --> SRCH["semantic search:<br/>every row, no<br/>status filter"]
  CTX ~~~ RP["next OpenYantra():<br/>replays whatever<br/>the queue holds"]
  RP --> ROW
  SRCH ~~~ NID["Nidra: a new phrase<br/>in a session row becomes<br/>a High belief, own topic"]
  NID --> RK
  NID ~~~ COG["memory tools and dashboard:<br/>cognitive_memories.json,<br/>secrets redacted, no<br/>scan, filter or ledger"]
```

## 3. Architecture

Everything is one Python package, `openyantra/`, constructed per process. Each
of the MCP server, the dashboard, the Telegram bot, the iOS Shortcut server, the
mail daemon, the CLI and the git hook opens its own `OpenYantra` on the same
workbook.

- **`core.py`** holds `OpenYantra`, the writer `LedgerAgent` and the queue
  `WriteQueue`. The constructor replays the queue, opens the search index, and
  creates a SQLite `SyncEngine` beside the workbook (`core.py:550-588`).
- **`yantra_security.py`** is Raksha: regex lists, secret redaction and trust
  tiers keyed on the writer's agent name.
- **`vidyakosha.py`** is the search sidecar: a FAISS flat inner-product index,
  a pickled BM25 index and a JSON registry of indexed rows.
- **`yantra_sqlite.py`** creates fifteen tables mirroring the sheets, plus
  `_meta`, `_sync_state` and `edges`, at every start (`yantra_sqlite.py:128-381`). Only
  `edges` is written in product code, by the dashboard.
- **`cognitive_db.py`** and **`cognitive_mcp.py`** are the JSON store and a
  hand-written line-delimited JSON-RPC server announcing protocol `2024-11-05`.
- **`yantra_ui.py`** is a FastAPI app on `127.0.0.1:7331` serving
  `UI/v4/dashboard.html` and `UI/v4/hud.html`; `desktop.py` opens either in
  pywebview or a browser.

Beside the workbook the package keeps `sanchitta.json`, `chitrapat.db`,
`cognitive_memories.json`, `settings.json`, `vidyakosha.faiss`,
`vidyakosha_bm25.pkl`, `vidyakosha_registry.json`, a `pratibimba/` folder of
per-agent snapshots and yearly `chitrapat_sessions_<year>.ods` archives.

A write is a whole-file rewrite. `_write_sheet` parses every sheet with pandas,
writes them all to `chitrapat.tmp.ods` and moves it over the workbook with
`os.replace`, with no file lock (`core.py:483-505`). The queue file takes a
`portalocker` lock around each load and save when the package imports, and
silently goes without one when it does not (`core.py:67-71`, `:242-262`);
`portalocker` is in neither `pyproject.toml`, the installers nor the
`Dockerfile`.

### Deployment and ergonomics

The core needs Python 3.9 or later with `odfpy` and `pandas`. Search adds
`scikit-learn` and `faiss-cpu`, MiniLM is optional, and the dashboard adds
FastAPI, uvicorn and `webauthn`. No API key is needed to store anything. Nidra
calls a local Ollama on `localhost:11434` when one answers and falls back to a
template sentence. Everything runs offline.

The store is the point of the design. A person can open `chitrapat.ods` in
LibreOffice, read every sheet and fix a row by hand. Such an edit bypasses
Raksha and the ledger. The `yantra sync` command that the skill file describes
as importing such edits calls `SyncEngine.import_ods`, whose body opens the file
and returns a note: *"stub returns OK for now"* (`yantra_sqlite.py:762`). A hand
edit takes effect because the workbook is the store; the search index sees it
at the next write.

The first-run path is `curl … install.sh | bash` or `install.ps1`; section 8
lists what each writes.

## 4. Essential Implementation Paths

- **Sheet write.** `OpenYantra.request_write` (`core.py:612-664`) runs Raksha,
  then `LedgerAgent.submit`, which appends the request to `sanchitta.json`,
  calls `_process`, and removes the entry by request id in a `finally` block
  (`:315-321`, `:280-286`, `:346-386`). `_process` first returns
  `already_committed` for a request id the ledger sheet holds
  (`:332-344`), then runs admission,
  `_validate`, `_check_conflict`, `_seal`, `_commit` and `_log_audit`. On
  `written`, `request_write` calls `VidyaKosha.sync` over the whole workbook,
  because the `incremental_update` it checks for is not defined (`:647-651`).
  It then asks `SHEET_TABLE_MAP` for an edge table; that map is keyed `Tasks`,
  `OpenLoops`, while sheet names carry emoji, so the lookup is always `None`
  (`:658`, `yantra_sqlite.py:61-77`).
- **Replay.** `OpenYantra.__init__` calls `replay_queue`, which empties the queue
  and runs `_process` on every request in it (`core.py:554-559`, `:323-326`).
- **Capture.** MCP sheet tools (`cognitive_mcp.py:401-460`); the dashboard and
  HUD through `POST /api/inbox` (`yantra_ui.py:193-198`, `UI/v4/hud.html:408`);
  `yantra inbox` (`cli.py:274-277`); Telegram commands and plain messages
  (`telegram_bot.py:151-240`); the iOS Shortcut server (`ios_shortcut.py:55-93`);
  the SMTP daemon (`yantra_mail.py:20-49`); Obsidian import
  (`yantra_vault.py:181-245`); the post-commit hook (`yantra_git.py:63-127`);
  and the CrewAI, LangChain and OpenClaw adapters.
- **Routing.** `route_inbox` sends each unrouted Inbox row to the sheet a
  keyword list picks, as a Low-confidence `Agent-inferred` row, then marks the
  Inbox row by its full content (`core.py:697-733`, `:2326-2347`).
- **Consolidation.** `NidraConsolidator.consolidate` clusters the last 25
  sessions, resolves loops, promotes preferences and logs a summary session
  (`yantra_nidra.py:247-349`), from `yantra dream`, `POST /api/nidra/consolidate`
  or the HUD.
- **Context.** `load_session_context` (`core.py:1056-1095`) feeds
  `build_system_prompt_block` (`:1097-1143`) and `build_context_markdown`
  (`:1769-1928`), which MCP `get_system_context` returns; `SutraCompiler.compile`
  packs a token budget (`yantra_sutra.py:71-365`).
- **Search.** `OpenYantra.search` (`core.py:1152-1209`) over `VidyaKosha.query`
  (`vidyakosha.py:355-439`), reached through the LangChain retriever and the
  CrewAI adapter; `CognitiveMemoryStore.search` (`cognitive_db.py:122-166`);
  `SyncEngine.traverse` (`yantra_sqlite.py:923-967`).
- **Correction.** Update and resolve through `_commit`; the corrections queue
  (`core.py:735-775`, `yantra_ui.py:205-221`); quarantine release
  (`core.py:1361-1381`, `yantra_ui.py:238-241`); cognitive delete
  (`cognitive_db.py:108-120`); session-log archival (`core.py:1228-1273`).

## 5. Memory Data Model

The controlled vocabularies are sets in `core.py:75-84`: project, task and goal
statuses, four priorities, `Yes`/`No`, three preference strengths, four
confidence values, four sentiments, four sources and six operations. Column
names follow the template, and `_commit` adds any new field as a new column, so
a writer that names a field wrongly widens the sheet instead of failing.

**Row identity is the first column's text.** `update`, `resolve` and `archive`
build a mask on `df.iloc[:, 0] == row_identifier` and change every matching row
(`core.py:446-478`). An update that matches nothing appends a new row with the
requested fields, so a mistyped task name sent to the dashboard's complete
route creates a row with status Done and no task text.

**Provenance is caller-supplied.** `Source` and `Added By` come from the
request. `add_task`, `add_project` and `update_identity` hardcode
`source="User-stated"` and `confidence="High"`, so a task the agent creates
through MCP is recorded as the person's statement (`core.py:929-969`).

**Scope.** One workbook per person. The one key is the Agent Config sheet's
`Agent` column, which `load_session_context` uses to pick the instructions an
agent receives, with `ALL` as the wildcard (`core.py:1059-1063`). The cognitive
notes carry an agent name that no read consults.

**Time.** `Last Updated` in UTC seconds, `Opened` on loops, `Deadline` on tasks
and goals, and the ledger's request timestamp. There is no validity time.
`TTL_Days` on loops is read by `check_anishtha_ttl`, which reports expired loops
and changes nothing (`core.py:809-838`).

**Unwired columns.** Beliefs carries `Contradiction_Flag`, created by the
template and the migrator and written only as `No` by Nidra's promotion;
`diff_beliefs` returns same-topic groups to the CLI and the dashboard's
insights (`core.py:777-807`, `:2024`, `:2072-2079`).

**The SQLite schema** mirrors the sheets with lowercase columns and a `UNIQUE`
request id on `ledger` for idempotent writes (`yantra_sqlite.py:128-381`).
`SyncEngine.write` has callers only in `tests/test_setu.py`.

**Committed data files.** The root `chitrapat.ods` is a workbook bootstrapped on
20 May 2026 at v2.12, holding a first name, a city and an occupation in
Identity. Its Session Log has the bootstrap row twice, 15 seconds apart. Its
ledger has the same four writes twice, under the same request ids and
timestamps: the queue replay as it ran before `e6a19a1`, when nothing removed
a processed entry, recorded in the project's own file. `cognitive_memories.json` is an empty list, and `settings.json` holds the
defaults with empty key fields. `.gitignore` lists all three as user data.
`openyantra/chitrapat_template.ods` is the blank template.

## 6. Retrieval Mechanics

**Context injection** is assembled from sheets, not search.
`load_session_context` returns the identity map, the agent's instructions,
Active projects, unresolved loops sorted by importance and capped at 15, Active
or In Progress goals, tasks whose status is not Done, pending corrections and
the unrouted Inbox count (`core.py:1056-1095`). Archived and Blocked tasks pass
that filter. `build_context_markdown` caps each section at four to eight items
and adds Values and Constraints beliefs at High confidence, the first five
People rows and Strong preferences (`core.py:1769-1928`). It is the only reader
that uses `Confidence` to exclude a row.

**Semantic search** indexes eight sheets: Identity, Goals, Projects, People,
Preferences, Beliefs, Tasks and Open Loops (`vidyakosha.py:237-240`). Each row
becomes `[sheet] column: value …` without the confidence, source and date
columns. The vector arm is FAISS `IndexFlatIP` over TF-IDF with truncated SVD,
or MiniLM when installed; BM25 runs at k1 1.5 and b 0.75. Each arm is
normalised by its maximum and fused at 0.7 vector to 0.3 BM25, and
`OpenYantra.search` then multiplies by importance and a one-year recency ramp
(`vidyakosha.py:355-439`, `core.py:1152-1209`). **No status filter applies**,
so a resolved loop, a Done task and a Cancelled project rank like live ones.

A per-agent snapshot freezes the registry at session start and keeps querying
the live FAISS and BM25 indexes, so positions in a rebuilt index can address a
different row of the frozen registry (`vidyakosha.py:441-455`, `:492-502`).

**The HUD's recall** fetches the Beliefs sheet and filters it by substring in
the browser (`UI/v4/hud.html:433-445`). **MCP `memory_search`** is a substring
match over key and content with type, all-tags and date-prefix filters, and
returns every match. **`graph_traverse`** is a recursive CTE walking edges both
ways for up to six hops, with a path-substring cycle guard.

The MCP server injects nothing on its own; the model has to call
`get_system_context`. Cognitive notes are never part of any context.

## 7. Write Mechanics

Every write is an explicit call. No model extracts or rewrites memory; Nidra's
Ollama call produces only the summary sentence it logs as a session.

**Admission drops short filler.** `_is_worth_remembering` joins the content
fields, leaving out importance, confidence, priority, status, source, author,
date and deadline. It drops the write when that text contains one of six
phrases such as *user said thanks*, or when it is at most two words and one of
them is a filler word such as `sure`, `noted` or `great` (`core.py:116-168`).
"Make sure the backup runs" is admitted; "Sure thing" is dropped with status
`filtered` and no ledger row. The filler set lists `thank you` and `got it` as
entries, and a single word never equals either. Session Log, Inbox and
Corrections writes skip the filter.

**Conflict detection is a refusal with nowhere to go.** A conflicting update
returns `resolution: pending_user`; the requested value is kept only as text in
the ledger row's reason (`core.py:364-374`). Most MCP and adapter writes are
High confidence, so the guard rarely fires.

**Duplicates are made, not removed.**

- A request left in the queue at the next start is applied again when its
  ledger row never landed; an `add` lands a second row (section 9).
- Obsidian import reads every line of `Inbox.md` again on each sync and never
  clears the file (`yantra_vault.py:232-245`).

**Nidra.** `prune_and_resolve_loops` resolves an open loop when its topic, or
its first three words of four or more letters, appears in the decisions and topics
of the last 30 sessions (`yantra_nidra.py:193-245`). Revert rows are part of
that corpus. `detect_promotable_preferences` scans the last 30 sessions and 20
Inbox rows for phrases such as *user prefers* and *always use*
(`yantra_nidra.py:104-191`). Each new match longer than eight characters
becomes a Beliefs row with Topic `Pref: <first 35 characters>`, Position
`User Preference: <phrase>`, Confidence High, Source `Agent-inferred` and
Importance 8, written through `request_write` as `NidraConsolidator` with the
topic as its row identifier (`:177-187`, `:259-288`). Three checks sit in
front of it:

- **Already stored.** The known set holds each stored Position, the same
  Position without its *User Preference:* prefix, and each Topic, and a phrase
  promoted in this run joins it (`:111-120`, `:173-189`). A second run adds
  nothing.
- **Reverted.** A pre-pass collects the decision text of every session marked
  *reverted* or *superseded*. A session whose decisions contain one of those
  texts or are contained in one is skipped, and so is any phrase found inside
  one (`:132-155`, `:170-171`). The git hook writes a revert as `Reverted /
  Superseded Decision [<hash>]: Revert "<subject>"`, so the reverted commit's
  phrase is suppressed while its revert row is in the window. A session with no
  decision text is skipped whenever any reverted text exists, because the empty
  string is contained in every one.
- **Inbox.** The scan reads `Content`, the Inbox sheet's text column, after
  `Item` and `Raw Input` (`:160`, `core.py:2717-2719`).

Two promotions whose first 35 characters agree share a topic, and
`diff_beliefs` groups rows by topic (`core.py:777-807`).

Promoted rows are not in the session context's principles section, which admits
the Values and Constraints domains only (`core.py:1863-1871`); they reach
semantic search, `read_sheet` and the HUD's recall.

**The MCP sheet writes.** `add_inbox_item` calls `inbox` with source
`Agent-observed`; `add_open_loop` calls an alias of `flush_open_loop`;
`complete_task` sets Status Done with source `Agent-observed`; and
`add_project` passes its arguments by name (`cognitive_mcp.py:401-460`,
`core.py:668-690`, `:881-907`). All six write as `Cognitive-MCP`, the agent name
the server constructs `OpenYantra` with, and no tool argument names the
requesting agent (`cognitive_mcp.py:63`). The iOS Shortcut server passes its
default source, `iOS Shortcut`, to `inbox`, so the constructor's
`assert source in SOURCE` refuses the write unless the request body names a
valid source (`ios_shortcut.py:66`, `:75`, `core.py:182-185`).

### Operational cost

Writes block the caller and are retrievable when the call returns. One sheet
write parses the ledger sheet for its request id, reads the target sheet, reads
and rewrites every sheet, does the same again for the ledger row, then rebuilds the search index: it reads eight
sheets again, refits TF-IDF, re-encodes every row and rewrites the FAISS, BM25 and
registry files. Each write's cost therefore grows with the whole workbook, and
with MiniLM installed every write re-embeds the store. The `yantra_sqlite.py`
docstring's 2 ms writes describe the unwired SQLite path.

Nidra reads the last
25 to 30 sessions per run with a ten-second Ollama timeout and runs only when
asked. The OpenClaw adapter prepends the context block to the system prompt at
session start, so any write since the last session changes the prompt prefix.

## 8. Agent Integration

The MCP server registers sixteen tools (`cognitive_mcp.py:121-319`). Five work
on the JSON store: `memory_write`, `memory_read`, `memory_search`,
`memory_delete` and `memory_stats`. Eleven work on the workbook:
`get_system_context`, `health_check`, `morning_brief`, `read_sheet`,
`graph_traverse` and six writes. The model names the agent on every `memory_write`, can delete any key
including the `agent-hierarchy-connections` record behind the dashboard's agent
hierarchy, and can read any sheet, the ledger and Quarantine included.

The adapters are thin. The LangChain chat history writes a session row on
flush, and its retriever wraps `search`. The CrewAI memory routes `save` by kind
and wraps `search`. The OpenClaw hooks inject the prompt block at session start,
re-inject open loops after compaction and log a session at the end. The
`pre_compact_hook` that its comment says preserves open loops returns the
payload unchanged (`adapters/openclaw.py:37-40`). `SKILL.md` describes the
library API for an agent and was read as data.

### What the setup commands and installers write

- **`yantra mcp setup`** writes `mcpServers.openyantra` into Claude Desktop's
  `claude_desktop_config.json` and `~/.cursor/mcp.json` at their per-OS paths,
  pointing at the interpreter, the absolute path of `cognitive_mcp.py` and the
  workbook. It copies an existing file to `.json.bak`, replaces a file it cannot
  parse with a fresh one holding only its own entry, and creates both files
  whether or not the client is installed (`mcp_setup.py:18-122`).
- **`yantra hook install`** writes `.git/hooks/post-commit` in the target
  repository, replacing any existing hook without a check. The hook runs
  `python -m openyantra.cli hook run` in the background with output discarded,
  against `OPENYANTRA_FILE` or a `chitrapat.ods` in the repository root
  (`yantra_git.py:28-60`, `cli.py:23-24`).
- **`install.sh`** fetches forty files one at a time from `raw…/main`,
  continuing past any that fail. It installs Homebrew through its own
  `curl | bash` when Python is missing, runs `sudo` package installs on Linux,
  and pip-installs eleven unpinned packages into `~/openyantra/.venv`. It writes
  the `yantra` launcher, a desktop shortcut whose quarantine attribute it
  strips, and PATH and `OPENYANTRA_FILE` lines appended to `~/.zshrc`,
  `~/.bashrc` or `~/.bash_profile` (`install.sh:21`, `:186-375`).
- **`install.ps1`** does the same on Windows. It writes `yantra.ps1`, a
  `yantra.bat` that runs it with `-ExecutionPolicy Bypass`, a desktop shortcut,
  and the user-level `PATH` and `OPENYANTRA_FILE` variables.
- **The `Dockerfile`** installs the core dependencies only and starts
  `cognitive_mcp`. Without `faiss` or a workbook inside the container, only the
  JSON memory tools work.

No installer registers a hook or an MCP config on its own; both need the
commands above.

## 9. Reliability, Safety, and Trust

### Replay is at least once, across processes

`LedgerAgent.submit` appends each request to `sanchitta.json`, runs `_process`,
and removes the entry by request id in a `finally` block, whether the write
committed, was refused or raised (`core.py:315-321`, `:280-286`). The next
`OpenYantra` constructor in any process empties the file and runs `_process` on
whatever is in it (`:554-559`, `:323-326`). `_process` returns
`already_committed` when the ledger sheet holds the request id, so a replayed
request whose ledger row landed is not applied again (`:332-351`). Two cases
reach a second application:

- **A crash between the sheet write and the ledger row.** `_commit` and
  `_log_audit` are two whole-workbook rewrites; a request interrupted between
  them has a row and no ledger entry, and the next start applies it again.
- **Another process starting mid-write.** The ledger check runs inside one
  process's `threading.Lock`. A process that constructs `OpenYantra` while
  another is inside `_process` and has not yet written the ledger row replays
  the request with its own `LedgerAgent`, and both apply it. The Telegram bot
  builds an instance per message and the CLI one per command.

Without `portalocker`, two processes enqueueing together can each save a list
without the other's entry. Replay skips Raksha, and a quarantined request never
enters the queue; a release submits a new request with a new id.

### The gate covers one store of two

The single-writer design is real for the workbook and absent for the JSON
store. `CognitiveMemoryStore.write` runs `Raksha.redact_secrets` over the key
and the content, inside a `try` that writes them unredacted if the import or
the call raises (`cognitive_db.py:71-78`). It runs no injection scan, no
admission filter and no ledger row, and `memory_delete` removes the note with
no trace (`cognitive_mcp.py:330-366`). `memory_write` redacts once more before
calling the store, and the dashboard's `POST /api/cognitive/write` reaches the
same store (`yantra_ui.py:255-269`). The store matches the key before
redacting it, so a dashboard write whose key holds a secret appends a new note
instead of replacing its own. Raksha skips scanning entirely for the
agent name `User` (`yantra_security.py:475-483`); the MCP sheet tools write as
`Cognitive-MCP`, which has no registered tier and is scanned.

### Concurrency and data loss

`LedgerAgent` holds a `threading.Lock`, which serialises writes inside one
process. The MCP server, the dashboard, the bot, the hook and the CLI are
separate processes doing read-modify-write on one file with no file lock, so
two concurrent writes lose one. `_write_sheet` writes a temporary file and
replaces the workbook with it, so a crash mid-write leaves the previous
workbook whole; a sheet that fails to parse is written back empty
(`core.py:483-505`). `archive_session_log` rewrites the
Session Log directly, outside the ledger (`core.py:1228-1273`).

### Declared and unwired

- **The SQLite engine.** The README calls it the shared store; nothing outside
  tests calls `SyncEngine.write`, `import_ods` is a stub, and the dashboard's
  preference for SQLite reads is gated on the same mismatched map, so it reads
  the workbook (`yantra_ui.py:166-187`). `export_ods` would replace the workbook
  with the SQLite tables, which `test_sync_wal_reconciliation` shows; it fires
  only when SQLite's ledger has rows, and nothing writes them.
- **Edge inference.** `infer_edges` is tested with lowercase keys and is never
  reached from `request_write` (section 4).
- **Ledger verification.** `Raksha.verify_mudra` has no caller and hashes four
  keys where `_seal` hashes eleven, so it could not match a stored seal
  (`yantra_security.py:345-360`, `core.py:425-427`). `yantra integrity` checks
  only the `sha256:` prefix (`core.py:1275-1324`).
- **Corrections.** `propose_correction` has no caller in the product, so the
  queue fills only from library code. The dashboard's review updates the
  Corrections row keyed on its target sheet, which marks every correction for
  that sheet with the same decision (`yantra_ui.py:212-216`).
  `apply_corrections` has no caller.

### Capture channels open to others

The Telegram bot checks no sender. Anyone who messages it can add Inbox items,
tasks, goals and loops and read open-loop topics and health counts
(`telegram_bot.py:97-240`). The iOS Shortcut server binds `0.0.0.0:7332` with
`Access-Control-Allow-Origin: *` and no token (`ios_shortcut.py:81-83`, `:171`).
The mail daemon accepts any SMTP client on `127.0.0.1:2525`. The dashboard has
no authentication unless passkeys are enabled, and then only cookies from
that process's memory count (`yantra_ui.py:113-127`).

### Revert tracking

The git hook detects a revert by a subject starting with *revert* or a body
containing *reverts commit*, and writes the Session Log row with a
*Reverted / Superseded Decision* prefix and `Status: REVERTED` in the notes
(`yantra_git.py:106-117`). Nidra's promotion scan skips that row and suppresses
any phrase it contains, so a commit subject *Always use tabs for indentation*
is not promoted while its revert is among the last 30 sessions. The reverted
commit's own row is unchanged, and a preference promoted before the revert
stays in Beliefs at High confidence. Loop resolution reads revert rows, so a
revert whose subject repeats an open loop's topic resolves that loop.

### Marks

Three are earned; all apply to the sheet engine and none covers the JSON
store.

- **`audit_log` — earned.** The ledger sheet is appended by `_log_audit` for
  every request `_process` handles and written by nothing else. Each row records
  who wrote to which sheet, when, with which operation, row identifier,
  confidence and source, and a hash of the request, and replay consults it
  before applying a request. The limits are real: an add names no row, no row
  carries the value, and a write replayed in the two cases above duplicates its
  entry.
- **`human_review` — earned.** A write matching a confirmed pattern waits in
  Quarantine, out of every sheet, the index and the context, until a person
  presses Release. No agent-facing surface carries a release verb, and the
  agent cannot write the Quarantine sheet. The dashboard does not show the held
  content, release does not close the item, and a released row is relabelled as
  the user's own statement at High confidence (`core.py:1369-1373`). The
  release route is a POST on `127.0.0.1` that needs no credential while
  passkeys are off, their default (`yantra_ui.py:238-241`, `:777`), so an
  agent with a general shell or HTTP tool can reach it; the mark rests on the
  declared tool surface carrying no release verb.
- **`tombstone` — withheld.** No record keyed on a value refuses a later write.
  A revert writes a new labelled row and blocks nothing; a cognitive delete
  removes the note.
- **`trust_state` — withheld.** `Confidence` is a four-value label. One context
  section admits only High beliefs, and the conflict guard protects High
  fields, but search, `load_session_context`, `read_sheet` and the prompt block
  return every level, and no value means *recorded but not believed*.
- **`bitemporal` — withheld.** No validity time exists beside `Last Updated`.
- **`scope_enforced` — withheld.** The Agent column selects configured
  instructions, not memories. Every memory sheet, the index and the JSON store
  are shared by every agent.
- **`negative_eval` — earned.** Two open loops are written and one resolved;
  `load_session_context`, the read behind MCP `get_system_context`, must return
  the live loop and must not return the resolved one
  (`tests/test_negative_eval.py:61-80`). A second case holds an injected task in
  Quarantine and asserts it is absent from the session context and the context
  markdown beside a real task that must be present (`:18-58`). Its search arm has
  no positive control and passes on an empty list, which is what search returns
  without the search extras. The filtered-filler case and the reverted-decision
  case keep material out of a sheet and a promotion list, which are write
  decisions (`:83-112`, `tests/test_nidra.py:37-63`). Search itself, which has
  no status filter, has no negative case.

## 10. Tests, Evals, and Benchmarks

The suite is 81 pytest functions in 17 files. CI installs `.[full,dev]` and runs
`pytest -v` on Ubuntu with Python 3.9 to 3.12 and on macOS and Windows with
3.11 (`.github/workflows/ci.yml:38-80`). I did not run it. The README badge
reports 80 passing.

What is covered:

- the JSON store's write, read, delete, search and date filters
  (`tests/test_cognitive.py`);
- edge add, delete and traversal, and `infer_edges` called directly
  (`tests/test_sutradhar.py`);
- secret redaction for five key formats (`tests/test_security_sanitizer.py`);
- git-hook install, ingest and revert labelling (`tests/test_git_hook.py`);
- Nidra clustering, loop resolution, candidate detection with a reverted
  decision left out, and two consolidation runs, the first landing one belief
  under its own `Pref:` topic and the second adding none
  (`tests/test_nidra.py:37-63`, `:95-125`);
- all six MCP sheet write tools against a real workbook, read back from the
  sheets, and `memory_write` redacting an Anthropic-format key
  (`tests/test_cognitive.py:205-298`);
- in `tests/test_atlas_audit_fixes.py`, admission of *Make sure the backup
  runs nightly* beside the drop of *Sure* and *Sure thing*, an empty queue after
  a write, an Inbox row over 50 characters routed without an extra row, and
  redaction inside the JSON store;
- in the same file, no duplicate after a second constructor, and a committed
  request passed to `_process` again returning `already_committed` with one row
  in the sheet;
- the session context leaving out a resolved loop and a quarantined write, each
  beside one that must be present (`tests/test_negative_eval.py`);
- vault export and import, the passkey flow, the token-budget packer, MCP
  config writing and dashboard routes.

What is not: no test exercises the release of a quarantined write, a request
left in the queue and replayed by a constructor, or two processes. The
idempotency test calls `_process` directly after the first write has finished,
and the queue test constructs the second instance after the first has
acknowledged. The `"error" not in resp` checks cannot fail, because tool
errors return inside `result` with `isError` (`tests/test_cognitive.py:121`,
`cognitive_mcp.py:94-102`); the sheet-tool test also reads each sheet back, and
that can. Importing `cognitive_mcp` at collection creates
`~/openyantra/cognitive_memories.json` in the real home directory and, if
`~/openyantra/chitrapat.ods` exists, opens it and replays its queue.

There is no retrieval-quality evaluation and no benchmark. `WHITEPAPER.md` is
the project's paper, written at v2.10. Its validation section reports four
rounds of review by eight language models with quoted verdicts, which is
opinion rather than measurement, and it lists LOCOMO and DMR evaluation as not
done. Its description of the write gates and trust tiers matches the code. It
claims Mudra verification on read, which has no caller, and an incremental
index sync, which is a full rebuild. No arXiv or DOI reference exists in the
tree.

## 11. For Your Own Build

### Steal

- **One choke point for every write, with a ledger row per outcome.** Recording
  `rejected` and `conflict` beside `written` makes a refused write visible
  instead of silent. Give the ledger the row id and the value, which this one
  lacks.
- **A security hold the agent cannot drain.** Put the release verb on a surface
  the agent has no tool for, keep the held write out of every sheet and index,
  and show the person what is held, not only why.
- **A store a person can open with a desktop application.** A workbook with one
  sheet per kind of memory is legible without the product, which no database
  file is.

### Avoid

- **An idempotency key recorded in a second write.** Checking the ledger for the
  request id stops a replay of a finished request; a crash between the sheet
  write and the ledger write, or a second process replaying before the ledger
  row lands, applies it again. Record the request id in the same write as
  the row.
- **A lock that degrades to nothing on import failure.** The queue lock is
  skipped when `portalocker` is absent, and no manifest installs it, so an
  install from the project's own manifests runs unlocked. Make the lock a hard dependency, or refuse to
  start a second writer.
- **Two stores behind one name.** If the agent's memory tools and the person's
  workbook are both "memory", put both behind the gate, or the model will use
  the ungated one.
- **Provenance set by the helper rather than the caller.** A helper that stamps
  `User-stated` on every task turns the agent's writes into the person's
  statements.

### Fit

This suits one person who wants to keep a hand-readable record of their own
projects, people and open threads, edit it in LibreOffice, and hand a summary
of it to a chat assistant. It is not ready as an agent's working memory.
Concurrent writers lose data and can apply each other's writes twice, and what
the agent stores through the MCP memory tools never reaches its own context. The
maintenance budget is a single author's, and the installer runs whatever
`main` holds. Walk away if more than one process writes, if anyone else can
reach the Telegram bot, or if you need to delete anything.

## 12. Open Questions

- Which store the author intends to be authoritative: the whitepaper's v3.0
  plan makes the workbook the contract and SQLite the engine, and the code at
  the pin wires neither direction.
- How often the Raksha patterns hold legitimate text in practice, and whether
  anyone uses the Release button.
- Whether `portalocker` is meant to be a dependency: `CHANGELOG.md` records it
  as one and no manifest at this commit names it.
- Whether the MCP memory tools are meant to stay outside Raksha's injection
  scan and the ledger, given that the store redacts secrets.

## Appendix: File Index

- Writer, queue, context, search wrapper: `openyantra/core.py`
- Security, trust tiers, quarantine scan: `openyantra/yantra_security.py`
- Search sidecar: `openyantra/vidyakosha.py`, `openyantra/yantra_sutra.py`
- SQLite schema, edges, unwired sync: `openyantra/yantra_sqlite.py`
- JSON store and MCP server: `openyantra/cognitive_db.py`,
  `openyantra/cognitive_mcp.py`, `openyantra/mcp_setup.py`
- Dashboard, HUD, desktop: `openyantra/yantra_ui.py`, `UI/v4/dashboard.html`,
  `UI/v4/hud.html`, `openyantra/desktop.py`
- Capture channels: `openyantra/telegram_bot.py`, `openyantra/ios_shortcut.py`,
  `openyantra/yantra_mail.py`, `openyantra/yantra_vault.py`,
  `openyantra/yantra_git.py`, `openyantra/cli.py`
- Consolidation: `openyantra/yantra_nidra.py`
- Adapters: `openyantra/adapters/langchain.py`, `crewai.py`, `openclaw.py`
- Install and container: `install.sh`, `install.ps1`, `yantra`, `Dockerfile`
- Paper and specs: `WHITEPAPER.md`, `PROTOCOL.md`, `SKILL.md`
- Tests: `tests/test_*.py`, `.github/workflows/ci.yml`

### Recorded searches

Run from the repository root at the pinned commit with `/usr/bin/git grep`.

- **SQLite writes have test callers only.**
  `git grep -n -E '\.write\(table=|engine\.write\(|db_engine\.write\(' -- .`
  returns the usage docstring at `openyantra/yantra_sqlite.py:27` and four calls
  in `tests/test_setu.py`.
- **No incremental index update.**
  `git grep -n -E 'def incremental_update' -- .` returns nothing; the same
  command with `def sync\(` matches `vidyakosha.py:290`.
- **The queue is shortened only by replay and acknowledgement.**
  `git grep -n -E 'dequeue_all|replay_queue|acknowledge' -- 'openyantra/*.py'`
  returns the noise entries at `core.py:118` and `:123`, the three definitions,
  the `submit` docstring, the `finally` call at `core.py:321`, the replay's call
  at `:324` and the constructor's call at `core.py:557`.
- **No delete branch.**
  `git grep -n -E 'operation == "delete"|"delete" and' -- 'openyantra/*.py'`
  returns nothing; `operation == "archive"` matches `core.py:471` and
  `yantra_sqlite.py:518`.
- **The workbook write takes no file lock; the queue lock needs an optional
  import no manifest provides.**
  `git grep -n -E 'portalocker|fcntl|flock|os\.replace' -- openyantra/core.py`
  returns the guarded import at `:68`, the queue lock's two calls at `:251` and
  `:258`, and the `os.replace` in `_write_sheet` at `:502`.
  `git grep -n -i portalocker -- pyproject.toml install.sh install.ps1 Dockerfile yantra`
  returns nothing, and the tree has no requirements file.
- **No validity time.**
  `git grep -n -i -E 'valid_?(from|to|until)|valid_at|event_time|occurred_at' -- 'openyantra/*.py'`
  returns nothing.
- **No value-keyed refusal.**
  `git grep -n -i -E 'tombstone|blocklist|rejected_values|do_not_relearn|suppress' -- 'openyantra/*.py'`
  returns one comment about HTTP logging in `ios_shortcut.py:53`.
- **No writer for Contradiction_Flag.**
  `git grep -n -E 'Contradiction_Flag|contradiction_flag' -- 'openyantra/*.py'`
  returns the template header, the migrator, the header validator, the SQLite
  column default and Nidra's promotion writing `No` (`yantra_nidra.py:279`).
- **No caller for the correction and verification helpers.**
  `git grep -n -w -E 'propose_correction|apply_corrections|verify_mudra' -- .`
  returns their definitions, the class docstring and two lines of
  `PROTOCOL.md`.
- **Secret redaction is the JSON store's only gate.**
  `git grep -n -w redact_secrets -- 'openyantra/*.py'` returns the two calls in
  `cognitive_db.py:75-76`, the two in `cognitive_mcp.py:340-341`, the definition
  and the recursive call inside `yantra_security.py`;
  `git grep -n -E 'scan_write|_log_audit|_is_worth' -- openyantra/cognitive_db.py openyantra/cognitive_mcp.py`
  returns nothing.
- **No release or approve verb on the MCP server.**
  `git grep -n -i -E 'release|approve' -- openyantra/cognitive_mcp.py` returns
  nothing; `quarantine` matches the sheet map and the `read_sheet` enum.
- **No agent filter on the JSON store's reads.**
  `git grep -n -E 'm.get\("agent"' -- openyantra/cognitive_db.py` returns
  `stats` and `get_hierarchy` only.
- **No Telegram sender check.**
  `git grep -n -E 'effective_user|effective_chat|chat_id|ALLOWED' -- openyantra/telegram_bot.py`
  returns nothing.
- **Inbox.md is read and never written.**
  `git grep -n 'Inbox.md' -- openyantra/yantra_vault.py` returns the comment and
  the path at `:232` and `:234`.
- **No release or queue-replay test.**
  `git grep -n -i -E 'release_|replay_queue|enqueue' -- tests/` returns
  nothing; `quarantin` matches only `tests/test_negative_eval.py`, whose case
  asserts the hold and never releases it.
- **No paper reference.**
  `git grep -n -i -E 'arxiv|bibtex|@article|@misc|doi\.org|zenodo' -- .`
  returns nothing.

## History

**2026-11-08** — [`27aa1e3eecb4769a1a8a82c9de62269a0605b375`](https://github.com/revanthlevaka/OpenYantra/commit/27aa1e3eecb4769a1a8a82c9de62269a0605b375). One commit past `e6a19a1`. Nidra's duplicate check matches the stored form, each promotion gets its own topic, and a reverted commit's phrase is suppressed; a session with no decision text is then skipped whenever any revert exists ([section 7](#7-write-mechanics)). Admission drops only short filler. The JSON store redacts secrets itself. Replay skips a request the ledger holds, and the workbook is replaced atomically; a crash between the sheet and ledger writes, or a replay overlapping another process, applies a request twice, and the new queue lock needs `portalocker`, which no manifest installs ([section 9](#9-reliability-safety-and-trust)). `LICENSE` is plain MIT. `negative_eval` is earned on a resolved loop the session context must omit; three marks. Screened again with the same findings; nothing was installed or run.

**2026-11-07** — [`e6a19a119699f3a1c9e1c5891c494d5b27d2168e`](https://github.com/revanthlevaka/OpenYantra/commit/e6a19a119699f3a1c9e1c5891c494d5b27d2168e). One commit past `bf86ff2`; its subject cites this atlas. Each queue entry is acknowledged after `_process`, which ends the routine second application; a request a crash or a second process leaves in the queue is still applied again ([section 9](#9-reliability-safety-and-trust)). The four MCP sheet tools that failed write, `route_inbox` marks rows by full content, admission matches whole words, and `memory_write` redacts secrets. Preference promotion lands, and its duplicate check never matches, so every run adds each phrase again ([section 7](#7-write-mechanics)). `LICENSE` grants MIT to the whole software. The first reading counted 70 test functions where there were 71. Both marks hold. Screened again with the same findings; nothing was installed or run.

**2026-11-07** — [`bf86ff26b72ee241d6c9915afc7d0604db9bbbdb`](https://github.com/revanthlevaka/OpenYantra/commit/bf86ff26b72ee241d6c9915afc7d0604db9bbbdb). First reading, from a full clone at the head of `main`, the commit adding revert detection. Screened first: no auto-run surface, `pyproject.toml` inside the seven-day cooldown and with no lockfile, and `tests/conftest.py` executing on collection; the MCP setup, hook installer and installers were read for what they write. `SKILL.md`, `PROTOCOL.md` and `WHITEPAPER.md` were read as data. Nothing was installed, built or run. The licence names three files for MIT, one absent. Two marks, `audit_log` and `human_review`, both on the sheet engine; `negative_eval` is withheld because its one populated read-path case pins a traversal depth ([section 9](#9-reliability-safety-and-trust)).

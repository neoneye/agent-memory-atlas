---
title: "OpenYantra"
eyebrow: "One gated writer, a ledger row for every refusal, and a superseded belief that refuses its own return"
description: "A local personal-memory toolkit keeping a user model in a LibreOffice workbook behind one gated writer, beside a separate JSON store for MCP memory."
root: ../..
page_kind: system
source_name: "revanthlevaka/OpenYantra"
source_url: https://github.com/revanthlevaka/OpenYantra
archive_name: "revanthlevaka--OpenYantra"
revision: 4099c657acd0e6dc3d0d9dcc724f22463264e8e5
revision_url: https://github.com/revanthlevaka/OpenYantra/commit/4099c657acd0e6dc3d0d9dcc724f22463264e8e5
analyzed_at: 2026-11-23
licence: "MIT in LICENSE, pyproject.toml and GitHub's detection; SPEC_LICENSE dedicates the specification, table schemas, sheet templates and interchange formats to the public domain under CC0 1.0"
size: "16,420 lines of Python outside tests: 15,804 in openyantra/ (core.py 3,084, yantra_sqlite.py 1,170, cli.py 1,033), 267 in a demo-GIF script, 220 in benchmarks/ and 129 in examples/; 3,524 lines of HTML and JavaScript in UI/v4; 786 lines of installer shell and PowerShell"
activity: "101 commits, 20 March – 23 November 2026: 83 by Revanth Levaka, 13 authored as Claude, 5 by dependabot; 49 of them on 7 November and 15 between 10 and 23 November, which take the version from 6.2.0 to 7.0.0; the repository was created on 15 March 2026 and its first commit is already v2.12"
tests: "184 pytest functions in 31 files, 4,914 lines with conftest.py, run by ci.yml on Ubuntu with Python 3.9–3.12 and on macOS and Windows with 3.11; none run for this reading"
capabilities: "audit_log, trust_state, tombstone, negative_eval"
capability_evidence:
  audit_log: "sheet engine — the Agrasandhanī ledger sheet | openyantra/core.py:438-482, :485-489, :580-701, :728-747 | `LedgerAgent._process` appends one ledger row for every request that reaches it — `written`, `rejected` or `conflict`, a delete and a tombstone refusal included — with timestamp, request id, agent, sheet, operation, row identifier, confidence, source, importance and a truncated SHA-256 of the whole request; a `written` row is saved in the same workbook write as the change it records, `_log_audit` appends the refusals, and `_validate` refuses any request addressed to the ledger itself | two tests read it back through the replay guard (tests/test_atlas_audit_fixes.py:106-130, tests/test_audit_round3_verification.py:24-57), and two read back the `rejected` row of a write to an unknown sheet and of one with a Status outside the vocabulary (tests/test_posix_lock_and_lineage_filtering.py:40-108), one the `rejected` row of a tombstone refusal (tests/test_tombstone.py:36-110) and one the `written` row of a delete (tests/test_sutradhar.py:172-212). Limits: an `add` entry names no row and no entry carries a value, so the ledger cannot say what a deleted row held; the MCP memory_* tools, session-log archival, edge writes, the SQLite import and direct LibreOffice edits leave no entry; the dashboard's ledger view reads an SQLite table no code fills; `_process` skips a request whose id the ledger already holds, and the check and the save share one cross-process lock, so a replay is applied again only when that lock was not taken; no test sends a write the conflict guard refuses; `yantra integrity` checks only that a signature is `sha256:` and 32 hex characters"
  trust_state: "sheet engine — Superseded_By on the Beliefs sheet | openyantra/core.py:189-214, :648-663, :1392-1396, :1505-1510, :2208-2219, openyantra/vidyakosha.py:445-459, openyantra/yantra_context.py:149-152, openyantra/yantra_sutra.py:263-264, openyantra/yantra_nidra.py:435-457 | a belief whose `Superseded_By` is filled, whose `Contradiction_Flag` starts with *superseded* or whose Status is Superseded or Reverted is kept on the sheet and dropped by one shared predicate from semantic search, the session context, `build_context_markdown` (what MCP `get_system_context` returns), `yantra context`, the Sutra compiler, `diff_beliefs`, the drift scan and the mesh export; `supersede` requests write it, sent by Nidra's revert pass and the drift resolver (openyantra/yantra_drift.py:637-648) | tests/test_posix_lock_and_lineage_filtering.py:111-245 plants a superseded belief beside a live one on the same topic and requires the live one present and the superseded one absent on every one of those reads, with search's opt-in returning it. Limits: Beliefs only; an `update` naming the column on a superseded Topic is refused by the tombstone check unless the request carries an override field; the planted row is written by an `add`, and the tests that mark a belief by a `supersede` request or the revert pass read only the session context; MCP `read_sheet` returns the row with its column, and the morning brief and the digest show its Position to the person unmarked"
  tombstone: "sheet engine — a superseded Beliefs row refuses its own value | openyantra/core.py:459-462, :502-547 | on every `add` or `update` addressed to Beliefs, `_check_tombstone` reads the sheet and rejects the request when a superseded row holds the same Position or the same Topic, compared trimmed and lowercased, and `_log_audit` writes the refusal to the ledger; the check stands in front of Nidra's promotion, the mesh import and every other writer that goes through the gate | tests/test_tombstone.py:36-110 supersedes a belief, re-asserts its Position under another Topic as another agent, and requires `rejected`, the ledger row, and the same write carrying the override field to land. Limits: Beliefs only; exact match, so a paraphrase passes; any request may carry `override_tombstone` or one of three other field names, and no product caller sends one; a `delete` of the superseded row removes the record with it; an exception inside the check admits the write; the JSON store's tombstone is keyed on a note's key, which the model can waive, and not on its content"
  negative_eval: "sheet engine — the session context and search | tests/test_negative_eval.py:65-84, :87-113, :17-62 | two open loops are written and one resolved, and two tasks are written and one marked Done; `load_session_context`, the read the MCP `get_system_context` tool serves, must return the live loop and the pending task and must not return the resolved loop or the Done task. A third case holds an injected task in Quarantine and asserts it is absent from `load_session_context` and `build_context_markdown`, beside a real task that must be present; a superseded belief must be absent from search, both context compilers, the Sutra compiler and the session context beside a live belief that must be present (tests/test_posix_lock_and_lineage_filtering.py:111-245); tasks and loops written under two projects must each be absent from the other project's session context, context markdown and `get_system_context` result, beside the project's own and an unscoped task that must be present (tests/test_workspace_isolation.py:20-156) | the search arm in tests/test_negative_eval.py checks its positive control only when search returns something, the one in tests/test_posix_lock_and_lineage_filtering.py unconditionally; search has no case for a resolved loop, a Done task or a Cancelled project, which it ranks like live ones; the filtered-filler, reverted-decision and repeated-consolidation cases keep material out of a sheet or a promotion list, which are write outcomes"
stack_storage: "files, sqlite, faiss"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A row in one of fourteen workbook sheets (identity, goals, projects, people, preferences, beliefs, tasks, open loops, session log, agent config, ledger, inbox, corrections, quarantine) with Confidence, Source, Importance and Last Updated; separately a keyed JSON note for the MCP memory tools"
  storage: "chitrapat.ods, rewritten whole by pandas and odfpy through a temporary file and an atomic replace on every write, under a per-path re-entrant lock, a thread lock plus an exclusive portalocker lock on a sibling lock file; a sanchitta.json write queue; FAISS, BM25, registry and per-sheet centroid files beside it; cognitive_memories.json and a key-tombstone file; a chitrapat.db SQLite file holding inferred graph edges and, after yantra sync, a copy of ten sheets; a mesh.jsonl export inside a git repository"
  retrieval: "A session-context builder filtering projects, loops, goals and tasks by status and, when a caller names a project, projects, tasks and loops by a substring of it; FAISS over TF-IDF with SVD or MiniLM fused with BM25, then importance and recency, dropping superseded beliefs and applying no other status filter; per-sheet centroid routing that picks context sections; substring search on the JSON notes; a six-hop bidirectional edge walk"
  write: "Explicit calls from MCP, the dashboard and HUD, the CLI, Telegram, mail, an iOS Shortcut endpoint, an Obsidian import, a git post-commit hook, a menu-bar capture, a git-file mesh import and three framework adapters; a local chat gateway that regex-harvests decision phrases from user and model text into the Session Log; no model on the write path"
  update_delete: "Update matches the first column and appends a new row when nothing matches; resolve and complete set a status column; supersede fills a Superseded_By column, after which an add or update repeating that Topic or Position is refused; delete removes every row whose first column matches, leaves a ledger row without the content, and has no product caller; the JSON notes are overwritten by key or deleted leaving a key tombstone the caller can waive"
  scoping: "One workbook per person; an optional project argument filters projects, tasks and loops in the session context and is absent by default; an Agent column selects which configured instructions each agent receives; the JSON notes carry an agent name no read filters on"
  integration: "A hand-rolled sixteen-tool stdio MCP server, a FastAPI dashboard and pywebview HUD on 127.0.0.1:7331, an OpenAI-compatible gateway on 127.0.0.1:7332, a CLI, a menu-bar tracker, LangChain, CrewAI and OpenClaw adapters, and a setup command writing Claude Desktop and Cursor configs"
  background: "Nidra runs on demand or from a daemon that waits for the workbook to sit idle; it auto-resolves open loops whose topic words appear in recent session decisions, writes a summary, and adds regex-matched preference phrases to Beliefs at High confidence, one topic per phrase, skipping phrases already stored or found in a reverted decision, then marks superseded any belief whose text matches a reverted decision"
  trust: "A regex scan can hold a write in quarantine, and the dashboard list that carries the Release button reads an SQLite table no code fills; Confidence and Source are caller-supplied labels, the MCP add_task and add_project writes are stamped User-stated, and a mesh import stamps every incoming belief User-stated and High"
  strengths: "One choke point that scans, filters, validates and ledgers every sheet write; a superseded belief that is dropped from every compiled context and refuses re-assertion by value; a store a person can open and read in LibreOffice"
  risks: "The dashboard and HUD read SQLite tables only yantra sync fills, so held writes, the ledger and current rows do not appear there; both file locks fall back to a thread lock when portalocker fails, and the replay guard relies on the file lock; a mesh sync re-adds rows deleted locally; the yantra proxy command builds its gateway without a workbook; search ranks resolved loops, Done tasks and Cancelled projects like live ones"
---

## 1. Executive Summary

OpenYantra is a local, single-user memory toolkit that keeps a structured model
of one person as sheets in a LibreOffice workbook, written through one gated
writer and served to Claude Desktop and Cursor over MCP. The gate is the
notable part: an injection scan that can hold a write for a person to release,
an admission filter, vocabulary checks, and a row on an append-only ledger
sheet.

A sheet change and its ledger row land in one atomic save, under a file
lock that every process takes and that one thread can enter twice. When the
lock call fails, the write runs under the thread lock alone. A belief marked
superseded is left out of search and every context compiler by one shared
predicate, and the gate refuses a later add or update that repeats its Topic or
Position. The MCP memory tools and the dashboard write a separate JSON store
with a secret filter, an injection block and a key tombstone, and no ledger.

Around that core sit a local OpenAI-compatible gateway that injects compiled
context into chat requests and harvests decision phrases from both sides of the
exchange, a git-file mesh that copies beliefs, tasks and projects between
checkouts, a regex contradiction scan that can supersede beliefs, a
source-comment scanner, a menu-bar tracker and a consolidation daemon.
`yantra proxy` builds the gateway without a workbook, so that command forwards
requests unchanged (section 8).

`LICENSE` is the MIT text; `SPEC_LICENSE` dedicates the protocol's table
schemas, sheet templates and interchange formats to the public domain under
CC0 1.0.

The README describes a SQLite WAL store shared by the HUD, the CLI and the MCP
server. At this commit every write goes to the workbook. SQLite receives
inferred graph edges after each write and a copy of ten sheets when
`yantra sync` runs, and the dashboard and the HUD read their sheets from it:
nothing before a sync, a stale copy after one, and an empty Quarantine, ledger
and Corrections view at any time (section 6).

Four marks are earned, all on the sheet engine: `audit_log` on the ledger
sheet, `trust_state` on the Beliefs sheet's `Superseded_By`, `tombstone` on the
refusal that column drives, and `negative_eval` on a resolved loop, a Done
task, a superseded belief and another project's task that the reads must leave
out. `human_review` is withheld because the Release button sits behind that
empty list. Section 9 gives the reason for each of the three withheld.

## 2. Mental Model

A memory is a **row in a sheet** of `chitrapat.ods`. The sheets are Identity,
Goals, Projects, People, Preferences, Beliefs, Tasks, Open Loops, Session Log,
Agent Config, the ledger (Agrasandhanī), Inbox and Corrections, plus Quarantine
and Security Log created on first use. A row is identified by its first column
— the attribute, task text or loop topic — and carries `Confidence` (High,
Medium, Low, Inferred), `Source` (User-stated, Agent-observed, Agent-inferred,
System), `Importance` 1 to 10 and `Last Updated` (`openyantra/core.py:72-101`,
`:2988-3084`).

A row becomes a belief by passing five gates in order, and nothing marks it as
less than true afterwards:

- **Raksha** redacts secrets, then scans the joined field text. A confirmed
  injection, jailbreak, impersonation or zero-width pattern sends the write to
  Quarantine; a suspicious one adds a `_security_flag` column and lets it
  through (`core.py:840-858`, `openyantra/yantra_security.py:496-594`).
- **Admission** drops a write whose content contains a noise phrase, whose
  content is at most two words including a filler word, or whose importance is
  below 2, with no ledger row (`core.py:114-166`).
- **Validation** rejects an unknown sheet or a value outside the controlled
  vocabulary (`core.py:485-500`).
- **Tombstone** rejects an add or update to Beliefs that repeats the Topic or
  Position of a superseded row (`core.py:502-547`).
- **Conflict** refuses an update that would change a High-confidence field from
  a request that is not High (`core.py:549-567`).

A row stops counting through a lifecycle column read by the context builder: a
loop resolved, a task Done, a project not Active, a goal not Active or In
Progress (`core.py:1346-1373`). Identity, People and Preferences rows have no
such column and change only by overwrite. Beliefs carry `Superseded_By`, which
Nidra's revert pass and the drift resolver fill, and search and every context
compiler drop a row that carries it (section 6). A `delete` request removes
every row whose first column equals the identifier, compared trimmed and lowercased, and writes a `written` ledger row
naming it; `delete_row` wraps the request and has callers only in tests
(`core.py:665-668`, `:1283-1314`). A git revert adds a new Session Log row labelled
*Reverted / Superseded Decision*; the reverted commit's own row is untouched
(`openyantra/yantra_git.py:106-127`).

The **cognitive store** is a second memory with no relation to the first: a JSON
list of notes with a key, a type, an agent name, content, tags and a timestamp.
A write replaces the note with the same key case-insensitively, and a delete
removes it (`openyantra/cognitive_db.py:57-173`). Only the MCP `memory_*` tools
and the dashboard's cognitive routes reach it, and no context builder reads it.

Control is hybrid. The agent writes through MCP, a person writes through the
HUD, the dashboard, the CLI, Telegram, LibreOffice or Obsidian, and Nidra
resolves loops when someone runs it.

```mermaid
%% caption: a sheet row is believed once it clears five gates under one workbook lock; a refused write saves its ledger row under the same lock and returns; a superseded belief refuses a write that repeats it; the queue replays what a crash left, skipping a request the ledger holds; the MCP memory tools and the dashboard write a second store with no ledger; the dashboard reads a third
flowchart TD
  subgraph writers["Sheet writers"]
    direction TB
    W1["six MCP sheet tools,<br/>as Cognitive-MCP"]
    W2["HUD, dashboard, CLI,<br/>Telegram, mail, vault"]
    W3["git post-commit hook"]
    W4["gateway harvest, mesh pull,<br/>drift resolver"]
    W1 ~~~ W2 ~~~ W3 ~~~ W4
  end
  writers --> RK{"Raksha: a confirmed<br/>injection pattern?"}
  RK -->|"yes"| Q["Quarantine sheet; the<br/>dashboard list reads an<br/>unfilled SQLite table"]
  RK -->|"no"| SQ["appended to<br/>sanchitta.json,<br/>removed once processed"]
  Q -->|"POST to the release<br/>route, by request id"| SQ
  SQ --> LK["re-entrant lock on<br/>.chitrapat.ods.lock"]
  LK --> LG{"request id<br/>already in<br/>the ledger?"}
  LG -->|"yes"| SKIP["skipped"]
  LG -->|"no"| GATE{"filler, unknown sheet,<br/>bad vocabulary, tombstone,<br/>conflict?"}
  GATE -->|"filler"| DROP["dropped,<br/>no ledger row"]
  GATE -->|"rejected, tombstone<br/>or conflict"| REF["refusal ledger row,<br/>lock re-entered,<br/>request returns"]
  GATE -->|"no"| ROW["row and written<br/>ledger row in<br/>one atomic save"]
  ROW --> CTX["session context:<br/>Active, unresolved, not Done,<br/>one project if asked"]
  ROW --> EDGE["chitrapat.db: inferred<br/>edges; sheet tables only<br/>after yantra sync"]
  EDGE --> DASH["dashboard and HUD<br/>sheet views"]
  ROW --> SRCH["semantic search:<br/>superseded beliefs<br/>dropped, no other<br/>status filter"]
  CTX ~~~ RP["next OpenYantra():<br/>replays whatever<br/>the queue holds"]
  RP --> ROW
  SRCH ~~~ NID["Nidra: a new phrase<br/>becomes a High belief;<br/>a reverted one is<br/>marked superseded"]
  NID --> RK
  NID ~~~ COG["memory tools and dashboard:<br/>cognitive_memories.json,<br/>secrets redacted, injection<br/>blocked, no ledger"]
```

## 3. Architecture

Everything is one Python package, `openyantra/`, constructed per process. Each
of the MCP server, the dashboard, the Telegram bot, the iOS Shortcut server, the
mail daemon, the CLI and the git hook opens its own `OpenYantra` on the same
workbook.

- **`core.py`** holds `OpenYantra`, the writer `LedgerAgent` and the queue
  `WriteQueue`. The constructor replays the queue, opens the search index, and
  creates a SQLite `SyncEngine` beside the workbook (`core.py:771-809`).
- **`yantra_security.py`** is Raksha: regex lists, secret redaction and trust
  tiers keyed on the writer's agent name.
- **`vidyakosha.py`** is the search sidecar: a FAISS flat inner-product index,
  a pickled BM25 index and a JSON registry of indexed rows.
- **`yantra_sqlite.py`** creates fifteen tables mirroring the sheets, plus
  `_meta`, `_sync_state` and `edges`, at every start (`yantra_sqlite.py:158-411`).
  In product code `edges` is written by the dashboard and by `infer_edges`
  after each committed write, and the sheet tables by `import_ods` alone.
- **`cognitive_db.py`** and **`cognitive_mcp.py`** are the JSON store and a
  hand-written line-delimited JSON-RPC server announcing protocol `2024-11-05`.
- **`yantra_ui.py`** is a FastAPI app on `127.0.0.1:7331` serving
  `UI/v4/dashboard.html` and `UI/v4/hud.html`; `desktop.py` opens either in
  pywebview or a browser.
- **`proxy.py`** is the gateway: a FastAPI app on `127.0.0.1:7332` serving
  `/v1/chat/completions` and forwarding to `OPENYANTRA_UPSTREAM_URL`, by
  default `https://api.openai.com/v1`, with the client's own headers
  (`proxy.py:125-129`, `:245-249`).
- **`yantra_mesh.py`**, **`yantra_drift.py`** and **`yantra_anchors.py`** are
  the git-file mesh, the contradiction scan and the source-comment scanner.
- **`menubar.py`** and **`workspace_detector.py`** are a tray icon that names
  the project in the frontmost editor's window title and offers a quick
  capture.

Beside the workbook the package keeps `sanchitta.json`, `chitrapat.db`,
`cognitive_memories.json`, `cognitive_memories_tombstones.json`,
`settings.json`, `vidyakosha_centroids.json`, `vidyakosha.faiss`,
`vidyakosha_bm25.pkl`, `vidyakosha_registry.json`, a `pratibimba/` folder of
per-agent snapshots and yearly `chitrapat_sessions_<year>.ods` archives.

A write is a whole-file rewrite. The writer parses every sheet with pandas,
writes them all to `chitrapat.tmp.ods` and moves it over the workbook with
`os.replace` (`core.py:580-701`, `:703-726`). `_workbook_lock` takes a
re-entrant lock on `.chitrapat.ods.lock` around the whole of `_process` and
around `_write_sheet`, and the queue file takes one on `sanchitta.lock` around
each load and save (`:421-422`, `:350-351`); section 9 describes the class.
`portalocker>=2.7` is a core dependency in `pyproject.toml`, `install.sh` and
`install.ps1`, and the `Dockerfile` installs the package with `pip install -e .`.
Both fall back to the thread lock alone when the import fails or the lock call
raises (`:64-68`, `:303-321`).

### Deployment and ergonomics

The core needs Python 3.9 or later with `odfpy` and `pandas`. Search adds
`scikit-learn` and `faiss-cpu`, MiniLM is optional, and the dashboard adds
FastAPI, uvicorn and `webauthn`. No API key is needed to store anything. For
its summary sentence Nidra asks Apple's `/usr/bin/fm` command on macOS when its
licence is accepted, then a local Ollama on `localhost:11434`, and falls back
to a template (`yantra_nidra.py:96-159`). Everything runs offline except a
gateway pointed at a remote upstream.

The store is the point of the design. A person can open `chitrapat.ods` in
LibreOffice, read every sheet and fix a row by hand. Such an edit bypasses
Raksha and the ledger. `yantra sync` calls `SyncEngine.import_ods`, which
upserts ten sheets into the SQLite tables by first-column key and infers edges
from each row; it removes nothing and writes no ledger row
(`yantra_sqlite.py:751-900`, `cli.py:443-445`). A hand edit takes effect
because the workbook is the store; the search index sees it at the next write,
and the dashboard at the next sync.

The first-run path is `curl … install.sh | bash` or `install.ps1`; section 8
lists what each writes.

## 4. Essential Implementation Paths

- **Sheet write.** `OpenYantra.request_write` (`core.py:834-901`) runs Raksha,
  then `LedgerAgent.submit`, which appends the request to `sanchitta.json`,
  calls `_process`, and removes the entry by request id in a `finally` block
  (`:404-410`, `:369-375`, `:438-483`). `_process` first returns
  `already_committed` for a request id the ledger sheet holds
  (`:424-436`), then runs admission, `_validate`, `_check_tombstone`,
  `_check_conflict` and `_seal`, and `_commit_and_audit` writes the sheet change and the `written`
  ledger row in one save; a rejection or conflict goes to `_log_audit`. On
  `written`, `request_write` calls `VidyaKosha.sync` over the whole workbook,
  because the `incremental_update` it checks for is not defined (`:869-873`).
  It then resolves the sheet to a SQLite table and calls `infer_edges`, which
  links a task, loop or goal to its project and any `@Name` to a known person;
  for a delete it removes the node's edges and its SQLite row instead
  (`core.py:876-899`, `yantra_sqlite.py:1125-1170`).
- **Replay.** `OpenYantra.__init__` calls `replay_queue`, which empties the queue
  and runs `_process` on every request in it (`core.py:775-780`, `:412-415`).
- **Capture.** MCP sheet tools (`cognitive_mcp.py:408-467`); the dashboard and
  HUD through `POST /api/inbox` (`yantra_ui.py:193-198`, `UI/v4/hud.html:425`);
  `yantra inbox` (`cli.py:379-382`); Telegram commands and plain messages
  (`telegram_bot.py:151-240`); the iOS Shortcut server (`ios_shortcut.py:55-93`);
  the SMTP daemon (`yantra_mail.py:20-49`); Obsidian import
  (`yantra_vault.py:181-245`); the post-commit hook (`yantra_git.py:63-127`);
  and the CrewAI, LangChain and OpenClaw adapters. The gateway's harvest
  (`proxy.py:360-386`), the menu bar's quick capture, a Session Log row
  (`menubar.py:238-242`), and the mesh pull (`yantra_mesh.py:350-479`) write
  through the same gate.
- **Routing.** `route_inbox` sends each unrouted Inbox row to the sheet a
  keyword list picks, as a Low-confidence `Agent-inferred` row, then marks the
  Inbox row by its full content (`core.py:934-970`, `:2677-2698`).
- **Consolidation.** `NidraConsolidator.consolidate` clusters the last 25
  sessions, resolves loops, promotes preferences and logs a summary session
  (`yantra_nidra.py:378-538`), from `yantra dream`, `POST /api/nidra/consolidate`
  or the HUD, or from `NidraDaemon`, which watches the modification times of
  the workbook and the SQLite file and consolidates once both have been still
  for the idle threshold (`yantra_nidra.py:541-656`). `yantra dream --watch`
  and the desktop launcher's `--daemon` start it (`cli.py:520-535`,
  `desktop.py:68-86`).
  or the HUD.
- **Context.** `load_session_context` (`core.py:1335-1405`) feeds
  `build_system_prompt_block` (`:1407-1453`) and `build_context_markdown`
  (`:2112-2274`), which MCP `get_system_context` returns; `SutraCompiler.compile`
  packs a token budget (`yantra_sutra.py:76-399`); each takes an optional
  `project_scope`.
- **Search.** `OpenYantra.search` (`core.py:1479-1536`) over `VidyaKosha.query`
  (`vidyakosha.py:368-461`), reached through the LangChain retriever and the
  CrewAI adapter; `CognitiveMemoryStore.search` (`cognitive_db.py:179-223`);
  `SyncEngine.traverse` (`yantra_sqlite.py:1079-1123`).
- **Correction.** Update, resolve, supersede and delete through
  `_commit_and_audit`, the supersede from the drift resolver
  (`yantra_drift.py:637-648`) and from Nidra's revert pass (`yantra_nidra.py:421-457`); the corrections queue
  (`core.py:972-1012`, `yantra_ui.py:205-221`); quarantine release
  (`core.py:1704-1724`, `yantra_ui.py:238-241`); cognitive delete
  (`cognitive_db.py:152-173`); session-log archival (`core.py:1571-1616`).

## 5. Memory Data Model

The controlled vocabularies are sets in `core.py:72-82`: project, task and goal
statuses, four priorities, `Yes`/`No`, three preference strengths, four
confidence values, four sentiments, four sources and seven operations. Column
names follow the template, and `_commit_and_audit` adds any new field as a new column, so
a writer that names a field wrongly widens the sheet instead of failing.

**Row identity is the first column's text.** `update`, `resolve`, `archive`
and `supersede` build a mask on the first column equal to `row_identifier` and
change every matching row (`core.py:614-663`). An update that matches nothing appends a new row with the
requested fields, so a mistyped task name sent to the dashboard's complete
route creates a row with status Done and no task text.

**Provenance is caller-supplied.** `Source` and `Added By` come from the
request. `add_task`, `add_project` and `update_identity` hardcode
`source="User-stated"` and `confidence="High"`, so a task the agent creates
through MCP is recorded as the person's statement (`core.py:1166-1206`).

**Scope.** One workbook per person. The one key is the Agent Config sheet's
`Agent` column, which `load_session_context` uses to pick the instructions an
agent receives, with `ALL` as the wildcard; Tasks carry `Project` and Open Loops
`Related Project`, which the session context filters on only when a caller
names a project (section 6) (`core.py:1339-1343`). The cognitive
notes carry an agent name that no read consults.

**Time.** `Last Updated` in UTC seconds, `Opened` on loops, `Deadline` on tasks
and goals, and the ledger's request timestamp. There is no validity time.
`TTL_Days` on loops is read by `check_anishtha_ttl`, which reports expired loops
and changes nothing (`core.py:1046-1075`).

**Belief columns.** Beliefs carries `Contradiction_Flag`, written as `No` by
Nidra's promotion and as `Superseded by <successor>` by a `supersede`, beside
`Superseded_By` (`core.py:648-663`, `:3037-3038`). `diff_beliefs` returns
same-topic groups to the CLI and the dashboard's insights (`core.py:1014-1044`, `:2375`, `:2423-2430`).

**The SQLite schema** mirrors the sheets with lowercase columns and a `UNIQUE`
request id on `ledger` for idempotent writes (`yantra_sqlite.py:158-411`).
`SyncEngine.write` has callers only in `tests/test_setu.py`; the tables fill
from `import_ods`, which matches rows by first-column key and leaves `ledger`,
`session_log`, `corrections`, `quarantine` and `security_log` untouched
(`yantra_sqlite.py:787-809`).

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
or In Progress goals, tasks whose status is not Done, pending corrections, the
unrouted Inbox count and the Beliefs rows that are not superseded
(`core.py:1335-1405`). Archived and Blocked tasks pass that filter. No other code
reads the `beliefs` list.

`is_superseded` counts a row as superseded when
`Superseded_By` holds anything but an empty or null-like value, when
`Contradiction_Flag` starts with *superseded*, or when `Status` is Superseded or
Reverted (`core.py:189-214`). `build_context_markdown` caps each section at four
to eight items and adds Values and Constraints beliefsto eight items and adds Values and Constraints beliefs at High confidence that
are not superseded, the first five People rows and Strong preferences
(`core.py:2112-2274`). It is the only reader that uses `Confidence` to exclude a
row. `yantra context` takes the first five beliefs of importance 7 or more that
are not superseded (`yantra_context.py:149-159`), and `SutraCompiler` filters
projects, loops, goals and tasks by status and Beliefs by the same predicate
(`yantra_sutra.py:248-264`).

**Project scope is a per-call option.** `load_session_context` takes a
`project_scope`. With one, it keeps Projects whose name contains the scope, and
Tasks and Open Loops whose `Project` or `Related Project` contains it or is
empty; without one, or with `all`, it filters nothing (`core.py:1346-1384`).
Goals, Beliefs, People and Preferences are returned whole either way.
`build_context_markdown`, the Sutra compiler and `yantra context --project`
pass the scope through (`core.py:2131`, `yantra_sutra.py:266-274`,
`yantra_context.py:261`). MCP `get_system_context` reads a `project` argument
that its tool schema does not declare (`cognitive_mcp.py:187-196`,
`:381-383`), and the gateway takes an `X-Project-Scope` header or, failing
that, `OPENYANTRA_PROJECT` or the name of the git repository enclosing the
server's own working directory (`proxy.py:216`, `core.py:169-186`). The match
is a lowercase substring, so a scope of `app` admits `AppAlpha` and `AppBeta`.
Search, `read_sheet` and the JSON store take no scope.

**Routing.** `route` scores a prompt against the mean vector of each indexed
sheet and returns the two closest; with `auto_route`, the Sutra compiler keeps
identity, instructions and the sections for those sheets
(`vidyakosha.py:508-546`, `yantra_sutra.py:96-105`). The gateway and
`yantra route` are its callers. "Zero retention" in the docstring means the
prompt is not written to the index (`core.py:1547-1557`).

Two reads of the workbook apply no supersession filter. MCP `read_sheet`
returns the sheet's rows with their `Superseded_By` column
(`cognitive_mcp.py:398-406`). The terminal and Telegram morning brief and the
digest each draw a *past memory* from Goals and Beliefs (`core.py:2033-2052`,
`yantra_digest.py:201-203`, `yantra_morning.py:127-131`); the MCP
`morning_brief` tool asks for markdown, which omits that line.

**The dashboard and the HUD read SQLite.** `GET /api/sheet/{name}` looks the
sheet's name up in `SHEET_TABLE_MAP`, which holds every sheet under its emoji
name, and returns `db_engine.read(table)` without opening the workbook
(`yantra_ui.py:157-190`, `yantra_sqlite.py:61-93`, `:558-570`). No write path
fills those tables: `yantra sync` copies ten sheets, and `ledger`,
`session_log`, `corrections`, `quarantine` and `security_log` have no writer
outside tests. The dashboard's project, task, loop and inbox views and the
HUD's recall therefore show the state of the last sync, and its ledger,
Corrections and Security views show nothing; the Security view prints *"No
quarantined writes -- Chitrapat is clean"* over a Quarantine sheet that holds
rows (`UI/v4/dashboard.html:878-884`). No test requests the route.

**Semantic search** indexes eight sheets: Identity, Goals, Projects, People,
Preferences, Beliefs, Tasks and Open Loops (`vidyakosha.py:237-240`). Each row
becomes `[sheet] column: value …` without the confidence, source and date
columns. The vector arm is FAISS `IndexFlatIP` over TF-IDF with truncated SVD,
or MiniLM when installed; BM25 runs at k1 1.5 and b 0.75. Each arm is
normalised by its maximum and fused at 0.7 vector to 0.3 BM25, and
`OpenYantra.search` then multiplies by importance and a one-year recency ramp
(`vidyakosha.py:368-461`, `core.py:1479-1536`). A superseded belief is skipped
while the fused list is cut to `top_k`, and `OpenYantra.search` filters again
unless the caller passes `include_superseded`, which no caller does
(`vidyakosha.py:445-459`, `core.py:1505-1510`). **No other status filter
applies**, so a resolved loop, a Done task and a Cancelled project rank like
live ones. The index row carries the sheet row as it stood at the last rebuild,
which every committed write triggers.

A per-agent snapshot freezes the registry at session start and keeps querying
the live FAISS and BM25 indexes, so positions in a rebuilt index can address a
different row of the frozen registry (`vidyakosha.py:463-477`, `:565-575`).

**The HUD's recall** fetches `/api/sheet/beliefs` and filters it by substring
in the browser (`UI/v4/hud.html:450-462`). **MCP `memory_search`** is a substring
match over key and content with type, all-tags and date-prefix filters, and
returns every match. **`graph_traverse`** is a recursive CTE walking edges both
ways for up to six hops, with a path-substring cycle guard.

The MCP server injects nothing on its own; the model has to call
`get_system_context`. The gateway does inject: it compiles a context for the
last user turn and appends it to the system message inside `<yantra_memory>`
tags (`proxy.py:71-95`, `:222-231`). Cognitive notes are never part of any context.

## 7. Write Mechanics

No model extracts or rewrites memory; Nidra's model call produces only the
summary sentence it logs as a session. Every write is an explicit call except
the gateway's harvest.

**Admission drops short filler.** `_is_worth_remembering` joins the content
fields, leaving out importance, confidence, priority, status, source, author,
date and deadline. It drops the write when that text contains one of six
phrases such as *user said thanks*, or when it is at most two words and one of
them is a filler word such as `sure`, `noted` or `great` (`core.py:114-166`).
"Make sure the backup runs" is admitted; "Sure thing" is dropped with status
`filtered` and no ledger row. The filler set lists `thank you` and `got it` as
entries, and a single word never equals either. Session Log, Inbox and
Corrections writes skip the filter.

**A superseded belief refuses its own value.** On an `add` or `update` to
Beliefs, `_check_tombstone` reads the sheet and returns `rejected` when a
superseded row has the same Position or the same Topic as the request, trimmed
and lowercased, and `_process` writes the refusal to the ledger
(`core.py:459-462`, `:502-547`). The record is the superseded row itself. The
Topic arm closes the whole topic: once a belief under *ORM Choice* is
superseded, its replacement needs another Topic. Four things lift the
refusal:

- a field named `allow_override`, `override_tombstone`, `Override_Tombstone`
  or `allow_superseded_override` set true in the request, which no product
  caller sends and which an `add` then stores as a column (`:511-518`);
- a `delete` of the superseded row;
- wording that differs by a character;
- any exception inside the check, which is logged at debug level and admits
  the write (`:545-547`).

**The gateway harvests both sides of a chat.** After a response, two regexes
run over `User: … Assistant: …` and keep the text after phrases such as *we
will*, *decided to*, *switching to* and *rule:* (`proxy.py:34-37`, `:360-373`).
Up to three matches go to the Session Log's decisions through `log_session`,
which writes them as `System` at High confidence under the agent name `Agent`
(`proxy.py:379-383`, `core.py:1153-1164`). Raksha and the ledger apply. Model
output is stored beside the person's own statements with nothing but a Notes
string to tell them apart, and Nidra's promotion scan reads those decisions for
preference phrases.

**The mesh copies rows between checkouts.** `push` overwrites
`.openyantra/mesh/mesh.jsonl` with every belief that is not superseded, Active
projects, pending tasks and the decisions of the last 30 sessions, then runs
`git add` and `git commit`; no remote is contacted (`yantra_mesh.py:229-338`).
`pull` reads that file from the working tree (`:350-479`):

- A belief whose Topic is absent locally is added as `User-stated` at High
  confidence under the agent name `MeshSync (<author>)`, where the author is
  the exporting row's Source cell (`:410-431`). An inferred belief on one
  machine is the person's own statement on the next.
- A belief whose Topic exists with another Position becomes a Pending
  Corrections row (`:386-408`); tasks and projects match by name and are never
  updated.
- The exported `signature` is a hash of topic, content and author that no code
  compares on the way in.
- The write's receipt is ignored, so a refused or quarantined row counts as
  merged.

A superseded belief is not exported, so a supersession does not travel, and
the tombstone check keeps the local row superseded. A deleted row comes back:
`sync` pulls before it pushes, the file still holds the row, and nothing
records the deletion.

**Drift resolution supersedes beliefs.** `DriftEngine.analyze` compares
beliefs that are not superseded with recent session decisions and active tasks
by three hardcoded invariants, eleven opposing regex pairs and a numeric budget
rule, and writes nothing (`yantra_drift.py:358-612`). `resolve_contradiction`
sends a `supersede` for the belief, a Session Log revert row or a Pending
Corrections row, as `VicharaResolver` and `User-stated`
(`:614-701`). `yantra resolve --auto` supersedes the belief on every direct
negation or budget violation with no person in the loop, and the dashboard's
`POST /api/drift/resolve` does the same by list index (`cli.py:848-860`,
`yantra_ui.py:834-866`).

**Conflict detection is a refusal with nowhere to go.****Conflict detection is a refusal with nowhere to go.** A conflicting update
returns `resolution: pending_user`; the requested value is kept only as text in
the ledger row's reason (`core.py:464-472`). Most MCP and adapter writes are
High confidence, so the guard rarely fires.

**Duplicates are made, not removed.**

- When the workbook lock is not taken, a second process replaying the queue
  while the first is inside `_process` applies the request again; an `add`
  lands a second row (section 9).
- Obsidian import reads every line of `Inbox.md` again on each sync and never
  clears the file (`yantra_vault.py:232-245`).

**Nidra.** `prune_and_resolve_loops` resolves an open loop when its topic, or
its first three words of four or more letters, appears in the decisions and topics
of the last 30 sessions (`yantra_nidra.py:324-376`). Revert rows are part of
that corpus. `detect_promotable_preferences` scans the last 30 sessions and 20
Inbox rows for phrases such as *user prefers*, *always use* and *never prefer*
(`yantra_nidra.py:237-322`). Each new match longer than eight characters
becomes a Beliefs row with Topic `Pref: <first 35 characters>`, Position
`User Preference: <phrase>`, Confidence High, Source `Agent-inferred` and
Importance 8, written through `request_write` as `NidraConsolidator` with the
topic as its row identifier (`:306-315`, `:389-419`). The phrase is the text
after the trigger, so *never use tabs for indentation* and *always use tabs for
indentation* both become `User Preference: tabs for indentation`. Three checks
sit in front of it:

- **Already stored.** The known set holds each stored Position, the same
  Position without its *User Preference:* prefix, and each Topic, and a phrase
  promoted in this run joins it (`:244-253`, `:316-319`). A second run adds
  nothing, and a superseded row keeps its phrase out.
- **Reverted.** A pre-pass over the last 50 sessions strips the `Reverted /
  Superseded Decision [<hash>]:` label and a leading `Revert "` from each
  decision part that says *reverted*, keeping what is left when it has four or
  more characters (`:264-275`). A non-empty session whose decisions contain one
  of those phrases, or are contained in one, is skipped, and so is any phrase
  found inside one or containing one (`:277-286`, `:299-302`). The git hook
  writes a revert as `Reverted / Superseded Decision [<hash>]: Revert
  "<subject>"` (`yantra_git.py:106-117`), so the phrase is the reverted
  commit's subject, suppressed while the revert row is in the window.
- **Inbox.** The scan reads `Content`, the Inbox sheet's text column, after
  `Item` and `Raw Input` (`yantra_nidra.py:291`, `core.py:3068-3070`).

After promotion, a second pass over the same 50 sessions marks beliefs
superseded (`yantra_nidra.py:421-457`). For each reverted phrase it drops a leading *always*
or *never* plus *use* or *prefer*, and any Beliefs row without `Superseded_By`
whose Position contains the remainder, or is contained in the phrase, gets a
`supersede` request keyed on its Topic, setting `Superseded_By: Reverted in
session log`. The match is by substring over every belief, whoever wrote it, so
reverting *Always use tabs for indentation* supersedes a belief reading *Never
use tabs for indentation* as well. Every row sharing the Topic is marked.

Two promotions whose first 35 characters agree share a topic, and
`diff_beliefs` groups rows that are not superseded by topic (`core.py:1014-1044`).

Promoted rows are not in the session context's principles section, which admits
the Values and Constraints domains only (`core.py:2208-2219`); they reach
semantic search, `read_sheet`, `yantra context` and the Sutra
compiler until a revert supersedes them.

**The MCP sheet writes.** `add_inbox_item` calls `inbox` with source
`Agent-observed`; `add_open_loop` calls an alias of `flush_open_loop`;
`complete_task` sets Status Done with source `Agent-observed`; and
`add_project` passes its arguments by name (`cognitive_mcp.py:408-467`,
`core.py:905-927`, `:1118-1144`). All six write as `Cognitive-MCP`, the agent name
the server constructs `OpenYantra` with, and no tool argument names the
requesting agent (`cognitive_mcp.py:63`). The iOS Shortcut server passes its
default source, `iOS Shortcut`, to `inbox`, so the constructor's
`assert source in SOURCE` refuses the write unless the request body names a
valid source (`ios_shortcut.py:66`, `:75`, `core.py:229-232`).

### Operational cost

Writes block the caller and are retrievable when the call returns, and each
holds the workbook lock throughout, so writes from every process run one at a
time. One sheet write parses the ledger sheet for its request id, the Beliefs
sheet again when that is its target, then every other
sheet, the target sheet and the ledger again, writes the whole workbook once, then rebuilds the search index: it reads eight
sheets again, refits TF-IDF, re-encodes every row and rewrites the FAISS, BM25 and
registry files. Each write's cost therefore grows with the whole workbook, and
with MiniLM installed every write re-embeds the store. The `yantra_sqlite.py`
docstring's 2 ms writes describe `SyncEngine.write`, which no product code calls.

Nidra reads the last
25 to 30 sessions per run with a ten-second Ollama timeout or a five-second
Apple model timeout, then runs the drift scan; it runs when asked or when the
daemon finds the workbook idle. The OpenClaw adapter prepends the context block to the system prompt at
session start, so any write since the last session changes the prompt prefix.

## 8. Agent Integration

The MCP server registers sixteen tools (`cognitive_mcp.py:121-319`). Five work
on the JSON store: `memory_write`, `memory_read`, `memory_search`,
`memory_delete` and `memory_stats`. Eleven work on the workbook:
`get_system_context`, `health_check`, `morning_brief`, `read_sheet`,
`graph_traverse` and six writes. The model names the agent on every `memory_write`, can delete any key
including the `agent-hierarchy-connections` record behind the dashboard's agent
hierarchy, and can read any sheet, the ledger and Quarantine included. Four arguments the
handlers read are in no tool schema: `project` and `top_k` on
`get_system_context`, `override_tombstone` on `memory_write` and `tombstone` on
`memory_delete` (`cognitive_mcp.py:187-196`, `:336`, `:369`, `:381-382`).

The adapters are thin. The LangChain chat history writes a session row on
flush, and its retriever wraps `search`. The CrewAI memory routes `save` by kind
and wraps `search`. The OpenClaw hooks inject the prompt block at session start,
re-inject open loops after compaction and log a session at the end. The
`pre_compact_hook` that its comment says preserves open loops returns the
payload unchanged (`adapters/openclaw.py:37-40`). `SKILL.md` describes the
library API for an agent and was read as data.

### Entry points added with the gateway, mesh and menu bar

- **`yantra proxy`** constructs `YantraGateway` with no workbook, because the
  command is absent from the list that opens one (`cli.py:357-361`,
  `:612-627`). The injection is skipped, the harvest raises and is logged at
  debug level, and `/health` raises, so the documented command is a plain
  forwarder (`proxy.py:222`, `:385-386`). The desktop launcher's `--proxy`
  builds the gateway on a real workbook (`desktop.py:88-106`).
- **The gateway** has no authentication and copies every client header but
  `host` and `content-length` upstream, the `Authorization` key included
  (`proxy.py:245-247`).
- **`yantra menubar --daemon`** calls `time.sleep` in a function whose only
  `import time` is inside another branch (`cli.py:397`, `:673`). The desktop
  launcher hands the menu bar an `OpenYantra` object where it expects a path
  and prints the resulting error (`desktop.py:109-121`, `menubar.py:117`).
- **`yantra mesh push`, `pull` and `sync`** run `git add`, `git commit` and
  `git rev-parse` in the enclosing repository and nothing else
  (`yantra_mesh.py:333-337`).
- **`yantra anchor`** scans source files for `@yantra:kind(id)` comments and
  reports whether each names a belief, loop, task or decision by substring; it
  stores nothing, and no read consults it (`yantra_anchors.py:74-86`,
  `:400-487`).

### What the setup commands and installers write### What the setup commands and installers write

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
  `~/.bashrc` or `~/.bash_profile` (`install.sh:21`, `:186-376`).
- **`install.ps1`** does the same on Windows. It writes `yantra.ps1`, a
  `yantra.bat` that runs it with `-ExecutionPolicy Bypass`, a desktop shortcut,
  and the user-level `PATH` and `OPENYANTRA_FILE` variables.
- **The `Dockerfile`** installs the core dependencies only and starts
  `cognitive_mcp`. Without `faiss` or a workbook inside the container, only the
  JSON memory tools work.

No installer registers a hook or an MCP config on its own; both need the
commands above.

## 9. Reliability, Safety, and Trust

### The workbook lock

Both file locks are one class, `_ReentrantFileLock`, keyed on the resolved
lock path in a process-wide registry. Each path holds a `threading.RLock`, a
depth count and the open file. The first entry in a process takes the RLock,
opens the lock file and takes an exclusive `portalocker` lock; a nested entry
by the same thread takes the RLock again and raises the depth, and the file
lock is released when the depth returns to zero (`core.py:280-338`). Threads in
one process wait on the RLock, and processes wait on the file lock.

`_process` runs inside `_workbook_lock` (`core.py:421-422`, `:438-439`). A
request that `_validate` rejects or `_check_conflict` refuses goes to
`_log_audit`, which saves the ledger through `_write_sheet`, and `_write_sheet`
enters the same lock again (`:454-467`, `:728-747`, `:703-704`). The nested
entry finds the depth above zero, so the `rejected` or `conflict` row is saved
and the request returns. A write naming a Status or Priority outside the
vocabulary, a write to an unknown sheet, or a Medium-confidence update to a
field a High-confidence row holds each end there. The first two have a test
that reads the `rejected` row back
(`tests/test_posix_lock_and_lineage_filtering.py:40-108`); the conflict path
has none. I ran nothing from the repository.

### Replay, the single save and the lock

`LedgerAgent.submit` appends each request to `sanchitta.json`, runs `_process`,
and removes the entry by request id in a `finally` block, whether the write
committed, was refused or raised (`core.py:404-410`, `:369-375`). The next
`OpenYantra` constructor in any process empties the file and runs `_process` on
whatever is in it (`:777-779`, `:412-415`). `_process` returns
`already_committed` when the ledger sheet holds the request id
(`:424-436`, `:440-443`). `_commit_and_audit` builds the target sheet and the
ledger with the new `written` row and writes both, with every other sheet, to
one temporary file that replaces the workbook (`:580-701`). A crash leaves
either both or neither. The ledger check and the save run under the workbook
lock, so a second process cannot replay a request between them.

Both guarantees hold across processes only while the file lock is taken. The
lock class catches any exception from opening or locking the file, logs it at
debug level and carries on under the thread lock alone (`core.py:303-321`), and
an import failure has the same effect; the queue lock is the same class. Replay
skips Raksha. A quarantined request never enters the queue, and a release
submits a new request with a new id.

### The gate covers one store of two

The single-writer design is real for the workbook and absent for the JSON
store. `CognitiveMemoryStore.write` redacts secrets from the key and the content
and asks Raksha to scan the content. A scan rating a confirmed or critical
prompt injection raises `ValueError`, which the MCP server returns to the model
as a tool error (`cognitive_db.py:78-99`, `cognitive_mcp.py:94-102`). When the
import, the redaction or the scan raises anything else, four regexes for
key-value secrets, `sk-`, `ghp_` and `AKIA` keys stand in for the redaction, and
no injection check runs. The block covers the prompt-injection type only, where
the sheet path quarantines jailbreak, impersonation and encoding matches too,
and a blocked note is refused rather than held for review.

The key is matched
after redaction, so a key holding a secret updates its own note (`cognitive_db.py:117-123`). The
store keeps no admission filter and writes no ledger row. `memory_delete`
removes the note and records its key and the time in
`cognitive_memories_tombstones.json`; a later write to that key raises unless
it passes `override_tombstone`, and the model can send that argument, or
`tombstone: false` on the delete (`cognitive_db.py:101-112`, `:152-173`,
`cognitive_mcp.py:330-371`). `memory_write`
redacts once more before calling the store, and the dashboard's
`POST /api/cognitive/write` reaches the same store (`yantra_ui.py:255-269`).
Raksha skips scanning entirely for the agent name `User`
(`yantra_security.py:514-522`). The MCP sheet tools write as `Cognitive-MCP`,
which has no registered tier and is scanned.

### Concurrency and data loss

`LedgerAgent` holds a `threading.RLock` inside one process, and the workbook
lock orders `_process` and `_write_sheet` across the MCP server, the dashboard,
the bot, the hook and the CLI. Three writers read their sheet before the lock
and write it under the lock: `_quarantine`, `_log_security` and
`archive_session_log`. A sheet write landing between that read and that write
is lost (`core.py:1726-1746`, `:1748-1766`, `:1571-1616`). A crash mid-write
leaves the previous workbook whole. A sheet that fails to parse is written back
empty, and a ledger that fails to parse is written back holding only the new
row (`:580-701`). `archive_session_log` rewrites the Session Log directly,
outside the ledger.

### Declared and unwired

- **The SQLite engine.** The README calls it the shared store. Nothing outside
  tests calls `SyncEngine.write`, the sheet tables fill only from
  `yantra sync`, and the dashboard reads them (section 6). `export_ods` would
  replace the workbook with the SQLite tables, which
  `test_sync_wal_reconciliation` shows; `reconcile`, which the daemon calls
  after each consolidation, fires it only when SQLite's ledger has rows, and
  nothing writes them (`yantra_sqlite.py:449-471`, `yantra_nidra.py:607-611`).
- **Deletion.** `delete_row` has callers only in tests, so no CLI command,
  MCP tool or dashboard route deletes a sheet row (`core.py:1283-1314`).
- **Ledger verification.** `LedgerAgent.verify_mudra` recomputes a request's
  seal and has callers only in tests; a ledger row stores no fields, so a seal
  cannot be recomputed from the workbook (`core.py:569-575`, `:1316-1318`).
  `yantra integrity` checks that a signature is `sha256:` and 32 hex
  characters (`yantra_security.py:433-438`).
- **Corrections.** The mesh pull and the drift resolver add Pending rows to
  Corrections; `propose_correction` has no caller. The dashboard's review list
  reads the unfilled SQLite table, its review route updates the Corrections
  row keyed on its target sheet, which marks every correction for that sheet
  with the same decision (`yantra_ui.py:212-216`), and `apply_corrections` has
  no caller, so an approved correction changes nothing.
- **Anchor drift.** The drift scan's check for anchors that point at
  superseded beliefs reads anchors the scanner has not linked, whose status is
  always `unknown`, and two of the actions it proposes, `cancel_task` and
  `update_anchor`, return `unsupported_action` (`yantra_drift.py:424-427`,
  `:556-585`, `:699-701`).

### Capture channels open to others

The Telegram bot checks no sender. Anyone who messages it can add Inbox items,
tasks, goals and loops and read open-loop topics and health counts
(`telegram_bot.py:97-240`). The iOS Shortcut server binds `0.0.0.0:7332` with
`Access-Control-Allow-Origin: *` and no token (`ios_shortcut.py:81-83`, `:171`).
The mail daemon accepts any SMTP client on `127.0.0.1:2525`, and the gateway
any HTTP client on `127.0.0.1:7332`, or on whatever `--host` names. The dashboard has
no authentication unless passkeys are enabled, and then only cookies from
that process's memory count (`yantra_ui.py:113-127`).

### Revert tracking

The git hook detects a revert by a subject starting with *revert* or a body
containing *reverts commit*, and writes the Session Log row with a
*Reverted / Superseded Decision* prefix and `Status: REVERTED` in the notes
(`yantra_git.py:106-117`). Nidra's promotion scan skips that row and suppresses
any phrase it contains, so a commit subject *Always use tabs for indentation*
is not promoted while its revert is among the last 50 sessions. The reverted
commit's own row is unchanged. A preference promoted before the revert is
marked `Superseded_By` at the next consolidation run, and search and every
context compiler then leave it out. `read_sheet` returns it with the column, and
the morning brief shows it unmarked (section 6). Loop
resolution reads revert rows, so a revert whose subject
repeats an open loop's topic resolves that loop.

### Marks

Four are earned; all apply to the sheet engine and none covers the JSON
store.

- **`audit_log` — earned.** The ledger sheet is appended for every request
  `_process` handles and written by nothing else: a `written` row in the same
  save as the change, a `rejected` or `conflict` row by `_log_audit`. Each row
  records who wrote to which sheet, when, with which operation, row identifier,
  confidence and source, and a hash of the request, and replay consults it
  before applying a request. A delete and a tombstone refusal each leave their
  row. The limits are real: an add names no row, and no row carries the value,
  so the ledger says that a row was deleted and not what it held.
- **`human_review` — withheld.** A write matching a confirmed pattern waits in
  Quarantine, out of every sheet, the index and the context, and no
  agent-facing surface carries a release verb. The one caller of the release
  route is the dashboard's Release button, drawn once per row of
  `/api/sheet/quarantine`, and that route returns the SQLite `quarantine`
  table, which no code fills (section 6). The dashboard reports a clean store
  and draws no button, so the queue has no drain in the running product. A
  person who knows a request id can `POST` it to
  `/api/security/quarantine/release` (`yantra_ui.py:238-241`,
  `UI/v4/dashboard.html:1090-1093`), and a released row is relabelled as the
  user's own statement at High confidence.
- **`tombstone` — earned.** A superseded Beliefs row is a durable record that
  the gate matches by value: an add or update repeating its Position or Topic
  is rejected whatever agent sends it and whatever Topic it is filed under, and
  the refusal is ledgered (`core.py:502-547`). Nidra's promotion and the mesh
  import both pass through it. Section 7 lists what lifts it: an override
  field any request can carry, a delete of the row, a paraphrase, and an
  exception inside the check. The JSON store's tombstone is keyed on a note's
  key, so the same content under another key is accepted.
- **`trust_state` — earned.** `Superseded_By` on Beliefs means *recorded but
  not believed*. `supersede` requests write it, from Nidra's revert pass and
  the drift resolver, and one predicate, `is_superseded`, drops the row from
  search, from the session context, from `build_context_markdown`,
  `yantra context` and the Sutra compiler, and from `diff_beliefs`, the drift
  scan and the mesh export (`core.py:189-214`, `:648-663`,
  `yantra_nidra.py:435-457`). The state covers Beliefs only. MCP `read_sheet`
  returns the row with its column, and the morning brief and the digest show
  its Position to the person unmarked. `Confidence` is a four-value label that
  one context section and the conflict guard use; search and the other reads
  return every level.
- **`bitemporal` — withheld.** No validity time exists beside `Last Updated`.
- **`scope_enforced` — withheld.** The project filter is real and tested, and
  it is an option a caller may leave out: with no `project_scope` the session
  context returns every project's tasks and loops, the declared
  `get_system_context` tool has no argument for one, and the gateway falls
  back to the server's own working directory (section 6). It matches by
  substring and leaves Goals, Beliefs, search and `read_sheet` unfiltered. The
  Agent column selects configured instructions, not memories, and the JSON
  store is shared by every agent.
- **`negative_eval` — earned.** Two open loops are written and one resolved,
  and two tasks are written and one marked Done; `load_session_context`, the
  read behind MCP `get_system_context`, must return the live loop and the
  pending task and must not return the resolved loop or the Done task
  (`tests/test_negative_eval.py:65-84`, `:87-113`). A third case holds an
  injected task in Quarantine and asserts it is absent from the session context
  and the context markdown beside a real task that must be present (`:17-62`).

  A superseded belief must be absent from search, both context compilers, the
  Sutra compiler and the session context while a live belief on the same topic
  is present, and this search arm checks its positive control unconditionally
  (`tests/test_posix_lock_and_lineage_filtering.py:111-245`). The search arm in
  `tests/test_negative_eval.py` checks its control only when search returns
  something.

  Tasks and loops written under two projects must each be absent from the
  other project's session context, context markdown and `get_system_context`
  result, while the project's own task and a task with no project are present
  (`tests/test_workspace_isolation.py:20-156`).

  The filtered-filler, reverted-decision and repeated-consolidation cases keep
  material out of a sheet or a promotion list, which are write decisions
  (`tests/test_negative_eval.py:116-145`, `:148-182`, `:185-206`). Search has no
  status filter for loops, tasks or projects and no case for them.

## 10. Tests, Evals, and Benchmarks

The suite is 184 pytest functions in 31 files. CI installs `.[full,dev]` and runs
`pytest -v` on Ubuntu with Python 3.9 to 3.12 and on macOS and Windows with
3.11 (`.github/workflows/ci.yml:38-80`). I did not run it. The README badge
reads `Tests-183/183 Passing`.

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
- the session context leaving out a resolved loop, a Done task and a
  quarantined write, each beside one that must be present
  (`tests/test_negative_eval.py`);
- in `tests/test_audit_round3_verification.py`, `portalocker` importable, a
  written row and its ledger row read back, and a replay returning
  `already_committed`;
- in the same file, a session with no decisions kept beside a revert, and a
  promoted belief absent from the session context's `beliefs` after its revert,
  with no belief required present
  (`tests/test_audit_round3_verification.py:90-123`);
- also there, a secret-bearing key updating its own note, and an injection
  refused by the JSON store; `tests/test_superseded_lineage.py` supersedes a belief by
  hand and checks the same list;
- in `tests/test_posix_lock_and_lineage_filtering.py`, a write to an unknown
  sheet and one with a Status outside the vocabulary each returning `rejected`
  with its `rejected` ledger row read back
  (`tests/test_posix_lock_and_lineage_filtering.py:40-108`);
- in the same file, a superseded belief
  beside a live one on the same topic, the live one present and the superseded
  one absent in `build_context_markdown`, `yantra context`, the Sutra compiler,
  the session context and search, with search's opt-in returning it
  (`tests/test_posix_lock_and_lineage_filtering.py:111-245`);
- in `tests/test_tombstone.py`, a superseded belief's Position refused under
  another Topic with its `rejected` ledger row, and admitted with the override
  field (`:36-110`); the JSON store's key tombstone, refused and overridden,
  through the store and through the MCP handler (`:13-33`, `:113-159`);
- in `tests/test_workspace_isolation.py`, each of two projects' tasks and
  loops absent from the other's scoped session context, context markdown and
  `get_system_context` result (`:20-156`);
- a task and a loop linked to their project by an inferred edge after a
  workbook write, and a delete removing the row, its edge and leaving a
  `delete` ledger row (`tests/test_sutradhar.py:172-212`);
- `import_ods` copying a task and a loop into SQLite, and a request's seal
  failing to verify after its Position is changed
  (`tests/test_sync_import_and_mudra.py:13-84`);
- the gateway's helpers, health route and a unary request whose forwarded body
  contains `<yantra_memory>`; a mesh push and pull into a second workbook, an
  idempotent second pull and a conflict routed to Corrections; the drift
  matrix and each resolution; the anchor scanner and linker; the daemon's idle
  trigger; the menu bar's capture;
- vault export and import, the passkey flow, the token-budget packer, MCP
  config writing and dashboard routes other than the sheet route.

What is not:

- No test sends a write the conflict guard refuses; the case named for it
  sends a Status outside the vocabulary and asserts `rejected`
  (`tests/test_posix_lock_and_lineage_filtering.py:69-108`).
- None exercises the release of a quarantined write, a request left in the
  queue and replayed by a constructor, or two processes.
- None requests `/api/sheet/{name}`, so the dashboard's read of SQLite is
  unasserted in either direction.
- The scoped cases pass a full project name; none passes a scope that is a
  substring of two names, and none scopes search.
- The gateway cases assert that a memory block is present and never that
  another project's row or a superseded belief is absent from it; none runs
  `yantra proxy`.
- The mesh cases hold no superseded, deleted or quarantined row and no altered
  signature, and none reads the Source or Confidence of an imported belief.

The idempotency tests call `_process` directly
after the first write has finished, and the queue test constructs the second
instance after the first has acknowledged. The superseded rows that search and
the compilers are tested on are written by an `add` that sets `Superseded_By`
and `Status` itself; the cases that mark a belief by a `supersede` request or
Nidra's revert pass read only the session context's `beliefs` list.
The `"error" not in resp` checks cannot fail, because tool
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
  instead of silent. Write the ledger row in the same save as the change, as
  this one does for `written`, so a replay check can trust it. Give the ledger
  the row id and the value, which this one lacks.
- **A superseded row that refuses its own value.** Matching a new write
  against the Position of every superseded row turns a status column into a
  refusal that re-extraction cannot walk past. Keep the override off the
  request: a field any writer can set is `--force`.
- **A security hold the agent cannot drain.** Put the release verb on a surface
  the agent has no tool for, keep the held write out of every sheet and index,
  and show the person what is held, not only why. Test that the list is
  populated; this one is not.
- **A store a person can open with a desktop application.** A workbook with one
  sheet per kind of memory is legible without the product, which no database
  file is.

### Avoid

- **A read path switched to a cache nothing fills.** Widening one lookup map
  so that edge inference could find its table also sent every dashboard read
  to SQLite, which only a manual sync populates. A cache needs a writer on the
  write path or a fallback on a miss, and a test that requests the route.
- **A sync that re-imports what was deleted.** The mesh pulls before it
  pushes, from a file that still holds the row, and nothing records the
  deletion. Export a deletion marker, or do not offer delete beside sync.
- **An import that upgrades provenance.** Stamping every incoming belief
  `User-stated` and High makes a teammate's inferred row the local person's
  own statement.
- **A lock that degrades to a thread lock on error.**- **A lock that degrades to a thread lock on error.** Both file locks log any
  exception from opening or locking the file at debug level and carry on under
  the thread lock alone, which orders nothing across processes. Fail the write
  instead, since the replay guard relies on the file lock.
- **A test named for a path it does not reach.** The case named for a
  conflicting write sends a Status outside the vocabulary and asserts
  `rejected`, so the conflict guard's refusal has no test. Assert the outcome
  the name promises.
- **Two stores behind one name.** If the agent's memory tools and the person's
  workbook are both "memory", put both behind the gate, or the model will use
  the ungated one.
- **Provenance set by the helper rather than the caller.** A helper that stamps
  `User-stated` on every task turns the agent's writes into the person's
  statements.

### Fit

This suits one person who wants to keep a hand-readable record of their own
projects, people and open threads, edit it in LibreOffice, and hand a summary
of it to a chat assistant. It is not ready as an agent's working memory: what
the agent stores through the MCP memory tools never reaches its own context. The
maintenance budget is a single author's, and the installer runs whatever `main`
holds. Walk away if anyone else can reach the Telegram bot, if you rely on the
dashboard to show what is stored or held, or if you plan to share a workbook
through the mesh.

## 12. Open Questions

- Which store the author intends to be authoritative: the whitepaper's v3.0
  plan makes the workbook the contract and SQLite the engine, and the code at
  the pin writes the workbook and reads the dashboard from SQLite.
- How often the Raksha patterns hold legitimate text in practice.
- Whether `read_sheet` and the morning brief are meant to show superseded
  beliefs, which every compiler and search leave out.
- Whether the tombstone's Topic arm is meant to close a topic to its own
  successor.
- Whether the mesh is meant to carry supersessions and deletions, which it
  drops.
- Whether the MCP memory tools are meant to stay outside the ledger and the
  quarantine, given that the store refuses injections outright.

## Appendix: File Index

- Writer, queue, context, search wrapper: `openyantra/core.py`
- Security, trust tiers, quarantine scan: `openyantra/yantra_security.py`
- Search sidecar: `openyantra/vidyakosha.py`, `openyantra/yantra_sutra.py`
- SQLite schema, edges, sheet import: `openyantra/yantra_sqlite.py`
- JSON store and MCP server: `openyantra/cognitive_db.py`,
  `openyantra/cognitive_mcp.py`, `openyantra/mcp_setup.py`
- Dashboard, HUD, desktop: `openyantra/yantra_ui.py`, `UI/v4/dashboard.html`,
  `UI/v4/hud.html`, `openyantra/desktop.py`
- Capture channels: `openyantra/telegram_bot.py`, `openyantra/ios_shortcut.py`,
  `openyantra/yantra_mail.py`, `openyantra/yantra_vault.py`,
  `openyantra/yantra_git.py`, `openyantra/cli.py`
- Consolidation and drift: `openyantra/yantra_nidra.py`,
  `openyantra/yantra_drift.py`
- Gateway, mesh, anchors, menu bar: `openyantra/proxy.py`,
  `openyantra/yantra_mesh.py`, `openyantra/yantra_anchors.py`,
  `openyantra/menubar.py`, `openyantra/workspace_detector.py`
- Adapters: `openyantra/adapters/langchain.py`, `crewai.py`, `openclaw.py`
- Install and container: `install.sh`, `install.ps1`, `yantra`, `Dockerfile`
- Paper and specs: `WHITEPAPER.md`, `PROTOCOL.md`, `SKILL.md`
- Tests: `tests/test_*.py`, `.github/workflows/ci.yml`

### Recorded searches

Run from the repository root at the pinned commit with `/usr/bin/git grep`.

- **SQLite sheet tables have one product writer.**
  `git grep -n -E '\.write\(table=|engine\.write\(|db_engine\.write\(' -- .`
  returns the usage docstring at `openyantra/yantra_sqlite.py:27` and four calls
  in `tests/test_setu.py`.
  `git grep -n -E 'INSERT INTO \{table\}' -- openyantra` returns
  `SyncEngine.write` at `yantra_sqlite.py:530` and `import_ods` at `:886`, and
  `git grep -n -E '\.import_ods\(|sync_from_ods\(' -- . ':!tests'` returns the
  CLI's call at `openyantra/cli.py:444`, the wrapper at `core.py:1325-1328`, a
  docstring and a line of `report/README.md`.
- **The dashboard's sheet route is untested.**
  `git grep -n -E 'api/sheet' -- tests` returns nothing.
- **No incremental index update.**
  `git grep -n -E 'def incremental_update' -- .` returns nothing.
- **The queue is shortened only by replay and acknowledgement.**
  `git grep -n -E 'dequeue_all|replay_queue|acknowledge' -- 'openyantra/*.py'`
  returns a prompt string at `cli.py:867`, the noise entries at `core.py:116`
  and `:121`, the three definitions, the `submit` docstring, the `finally` call
  at `core.py:410`, the replay's call at `:413` and the constructor's call at
  `core.py:778`.
- **One delete branch, and no product caller of its wrapper.**
  `git grep -n -E 'operation == "delete"|"delete" and' -- 'openyantra/*.py'`
  returns the committer's branch at `core.py:665` and the edge cleanup at
  `:882`.
  `git grep -n -w -E 'propose_correction|apply_corrections|verify_mudra|verify_request_signature|delete_row' -- .`
  returns the definitions, a class docstring, two lines of `PROTOCOL.md`, the
  one internal call at `core.py:1318`, and callers in
  `tests/test_sutradhar.py` and `tests/test_sync_import_and_mudra.py` only.
- **Both locks are one `portalocker` class; the dependency is declared.**
  `git grep -n -E 'portalocker|fcntl|flock|os\.replace' -- openyantra/core.py`
  returns the guarded import at `:65`, the class docstring at `:287`, the
  class's lock and unlock calls at `:310` and `:331`, and the `os.replace` calls
  in `_commit_and_audit` at `:696` and `_write_sheet` at `:723`.
  `git grep -n -i portalocker -- pyproject.toml install.sh install.ps1 Dockerfile yantra`
  returns `pyproject.toml:36`, `install.sh:193` and `install.ps1:139`.
- **No validity time.**
  `git grep -n -i -E 'valid_?(from|to|until)|valid_at|event_time|occurred_at' -- 'openyantra/*.py'`
  returns nothing.
- **Two value- or key-keyed refusals.**
  `git grep -n -i -E 'tombstone|blocklist|rejected_values|do_not_relearn|suppress' -- 'openyantra/*.py'`
  returns lines in `cognitive_db.py` and `cognitive_mcp.py` for the JSON
  store's key tombstone, the sheet check and its call in `core.py`, and one
  comment about HTTP logging in `ios_shortcut.py`.
- **No product caller sends the sheet tombstone's override.**
  `git grep -n -E 'allow_override|override_tombstone|Override_Tombstone|allow_superseded_override' -- openyantra UI`
  returns the four field reads at `core.py:512-515` and the JSON store's
  parameter in `cognitive_db.py` and `cognitive_mcp.py:336` and `:345`.
- **Two writers for Contradiction_Flag.**
  `git grep -n -E 'Contradiction_Flag|contradiction_flag' -- 'openyantra/*.py'`
  returns the predicate at `core.py:208`, the supersede branch at `:657-658`,
  the principles read's column list at `:2212`, the template headers at `:2998`
  and `:3038`, the migrator, the SQLite header list and column
  (`yantra_sqlite.py:133`, `:248`) and Nidra's promotion writing `No`
  (`yantra_nidra.py:410`).
- **One predicate, and two modules that read the column themselves.**
  `git grep -n -E 'Superseded_By|"beliefs"\]|get\("beliefs"' -- openyantra`
  returns the predicate at `core.py:198`, the tombstone check's message at
  `:539`, the supersede branch at `:653-656`, the principles read's column list
  at `:2212` and the template header at `:3038`. It also returns the drift
  resolver's write at `yantra_drift.py:644`, Nidra's revert pass at `yantra_nidra.py:440` and
  `:453`, and two direct reads of the column at `workspace_detector.py:324` and
  `yantra_anchors.py:415`; nothing in the package reads the session context's
  `beliefs` key.
  `git grep -n -w -E 'is_superseded|include_superseded' -- openyantra` returns
  the definition at `core.py:189` and its export, the tombstone check at `:533`,
  the filters at `core.py:1021`, `:1395`, `:1509` and `:2215`,
  `vidyakosha.py:452`, `yantra_context.py:152`, `yantra_sutra.py:264`,
  `yantra_drift.py:383` and `yantra_mesh.py:238`, the Sutra module's fallback
  returning `False` when the import fails (`yantra_sutra.py:17`), and the
  opt-in parameter forwarded at `core.py:1503`, which no caller sets.
- **Beliefs reads with no supersession filter.**
  `git grep -n -E '_read_sheet\(SHEET_BELIEFS\)|_read_sheet\(real_sheet\)|for sheet in \[SHEET_GOALS, SHEET_BELIEFS\]|api/sheet/beliefs' -- openyantra UI`
  returns the filtered reads at `core.py:1021` and `:1394` and
  `yantra_context.py:150`, Nidra's revert pass at `yantra_nidra.py:435`, and
  the unfiltered `read_sheet` at `cognitive_mcp.py:405`, the HUD's fetch at
  `UI/v4/hud.html:453`, and the past-memory draws at `core.py:2035`,
  `yantra_digest.py:202` and `yantra_morning.py:129`.
- **Redaction and one scan are the JSON store's gates.**
  `git grep -n -w redact_secrets -- 'openyantra/*.py'` returns the two calls in
  `cognitive_db.py:82-83`, the two in `cognitive_mcp.py:341-342`, the definition
  and the recursive call inside `yantra_security.py`;
  `git grep -n -E 'scan_write|_log_audit|_is_worth' -- openyantra/cognitive_db.py openyantra/cognitive_mcp.py`
  returns the one scan at `cognitive_db.py:84`.
- **No release or approve verb on the MCP server.**
  `git grep -n -i -E 'release|approve' -- openyantra/cognitive_mcp.py` returns
  nothing; `quarantine` matches the sheet map and the `read_sheet` enum.
  `git grep -n -E 'release_quarantine|quarantine/release' -- openyantra UI`
  returns the definition and its log line in `core.py`, the route at
  `yantra_ui.py:238-241` and the dashboard's one call at
  `UI/v4/dashboard.html:1091`.
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
  nothing; `quarantin` matches `tests/test_negative_eval.py`, whose case
  asserts the hold and never releases it, and `tests/test_drift.py` and
  `tests/test_mesh.py`, where the word names a Corrections row.
- **No conflict refusal in the suite.**
  `git grep -n -E '"conflict"|Vivada' -- tests/` returns nothing.
- **The mesh runs three git commands, none of them against a remote.**
  `git grep -n -E 'subprocess|"git"' -- openyantra/yantra_mesh.py` returns the
  import and the `add`, `commit` and `rev-parse` calls at `:333-337`.
- **No paper reference.**
  `git grep -n -i -E 'arxiv|bibtex|@article|@misc|doi\.org|zenodo' -- .`
  returns nothing.

## History

**2026-11-23** — [`4099c657acd0e6dc3d0d9dcc724f22463264e8e5`](https://github.com/revanthlevaka/OpenYantra/commit/4099c657acd0e6dc3d0d9dcc724f22463264e8e5). Fifteen commits past `7910d7f`, taking the version from 6.2.0 to 7.0.0. `_check_tombstone` refuses an add or update repeating a superseded belief's Topic or Position, so `tombstone` is earned ([section 7](#7-write-mechanics)). Widening `SHEET_TABLE_MAP` wired edge inference and sent the dashboard's sheet route to SQLite tables only `yantra sync` fills; the Quarantine list is empty and `human_review` is withdrawn ([section 6](#6-retrieval-mechanics)). `delete` has a branch and no product caller, and `import_ods` is implemented. The project filter is opt-in, so `scope_enforced` stays withheld and its tests join `negative_eval`. Added: a gateway, a git-file mesh, a drift resolver, anchors, a menu bar and a Nidra daemon ([section 8](#8-agent-integration)). Four marks. I re-ran the recorded searches, screened again with the same findings, and installed and ran nothing.

**2026-11-10** — [`7910d7f74715fcc73f25083d5984eafa34f16b91`](https://github.com/revanthlevaka/OpenYantra/commit/7910d7f74715fcc73f25083d5984eafa34f16b91). Five commits past `5f7b724`; the fix's message cites this atlas's reading. Pull request [30](https://github.com/revanthlevaka/OpenYantra/pull/30) made both file locks one re-entrant class, so a rejected or conflicting write saves its ledger row and returns ([section 9](#9-reliability-safety-and-trust)). One predicate drops a superseded belief from search, the session context and the three compilers; `read_sheet`, the HUD's recall and the morning brief do not filter ([section 6](#6-retrieval-mechanics)). `trust_state` is earned on `Superseded_By`, and `negative_eval` gains a superseded-belief case with an unconditional search control: four marks. The case named for a conflict asserts a rejection. I re-ran the recorded searches, screened again with the same findings, and installed and ran nothing.

**2026-11-09** — [`5f7b72466f04079e2b9a4dbeb61fe262bc1f5fad`](https://github.com/revanthlevaka/OpenYantra/commit/5f7b72466f04079e2b9a4dbeb61fe262bc1f5fad). Four commits past `5ab4989`, with an identical tree. Pull request [28](https://github.com/revanthlevaka/OpenYantra/pull/28) replaced both file locks with a re-entrant per-path lock and filtered superseded beliefs on every context and search path. It was merged at 07:16 UTC and reverted by pull request [29](https://github.com/revanthlevaka/OpenYantra/pull/29) at 07:24, with CI green on both and no reason given. A refused write blocks on POSIX, and only the session context's `beliefs` list honours a supersession ([section 9](#9-reliability-safety-and-trust), [section 7](#7-write-mechanics)). Marks unchanged. I re-ran the recorded searches at the new head with the same results, screened again with the same findings, and installed and ran nothing.

**2026-11-08** — [`5ab49899bebb123bc973d139c5d0f3656a69f66a`](https://github.com/revanthlevaka/OpenYantra/commit/5ab49899bebb123bc973d139c5d0f3656a69f66a). Twelve commits past `27aa1e3`; the last adds a demo GIF. `portalocker` is declared, a sheet change and its ledger row land in one save, and a workbook lock spans `_process`, which closes replay's second application while the lock is taken. The lock is taken again inside `_log_audit`, so on Linux and macOS a rejected or conflicting write blocks forever ([section 9](#9-reliability-safety-and-trust)). Empty decisions are no longer skipped, and Nidra supersedes a belief a revert names, by substring; only the session context's `beliefs` list honours the mark ([section 7](#7-write-mechanics)). The JSON store matches keys after redaction and refuses injections. Three marks hold, and `negative_eval` gains a Done-task case. I screened again and got the same findings; I installed and ran nothing from the tree.

**2026-11-08** — [`27aa1e3eecb4769a1a8a82c9de62269a0605b375`](https://github.com/revanthlevaka/OpenYantra/commit/27aa1e3eecb4769a1a8a82c9de62269a0605b375). One commit past `e6a19a1`. Nidra's duplicate check matches the stored form, each promotion gets its own topic, and a reverted commit's phrase is suppressed; a session with no decision text is then skipped whenever any revert exists ([section 7](#7-write-mechanics)). Admission drops only short filler. The JSON store redacts secrets itself. Replay skips a request the ledger holds, and the workbook is replaced atomically; a crash between the sheet and ledger writes, or a replay overlapping another process, applies a request twice, and the new queue lock needs `portalocker`, which no manifest installs ([section 9](#9-reliability-safety-and-trust)). `LICENSE` is plain MIT. `negative_eval` is earned on a resolved loop the session context must omit; three marks. Screened again with the same findings; nothing was installed or run.

**2026-11-07** — [`e6a19a119699f3a1c9e1c5891c494d5b27d2168e`](https://github.com/revanthlevaka/OpenYantra/commit/e6a19a119699f3a1c9e1c5891c494d5b27d2168e). One commit past `bf86ff2`; its subject cites this atlas. Each queue entry is acknowledged after `_process`, which ends the routine second application; a request a crash or a second process leaves in the queue is still applied again ([section 9](#9-reliability-safety-and-trust)). The four MCP sheet tools that failed write, `route_inbox` marks rows by full content, admission matches whole words, and `memory_write` redacts secrets. Preference promotion lands, and its duplicate check never matches, so every run adds each phrase again ([section 7](#7-write-mechanics)). `LICENSE` grants MIT to the whole software. The first reading counted 70 test functions where there were 71. Both marks hold. Screened again with the same findings; nothing was installed or run.

**2026-11-07** — [`bf86ff26b72ee241d6c9915afc7d0604db9bbbdb`](https://github.com/revanthlevaka/OpenYantra/commit/bf86ff26b72ee241d6c9915afc7d0604db9bbbdb). First reading, from a full clone at the head of `main`, the commit adding revert detection. Screened first: no auto-run surface, `pyproject.toml` inside the seven-day cooldown and with no lockfile, and `tests/conftest.py` executing on collection; the MCP setup, hook installer and installers were read for what they write. `SKILL.md`, `PROTOCOL.md` and `WHITEPAPER.md` were read as data. Nothing was installed, built or run. The licence names three files for MIT, one absent. Two marks, `audit_log` and `human_review`, both on the sheet engine; `negative_eval` is withheld because its one populated read-path case pins a traversal depth ([section 9](#9-reliability-safety-and-trust)).

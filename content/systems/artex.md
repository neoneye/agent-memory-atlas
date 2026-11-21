---
title: "ARTEX"
eyebrow: "Rule-built lessons that retire when the verdict behind them is reversed"
description: "A self-hosted Go penetration-testing platform on PostgreSQL whose agents share an asset graph, inherit earlier tasks' findings, and can receive rule-built lessons."
root: ../..
page_kind: system
source_name: "BaaRai/ARTEX"
source_url: https://github.com/BaaRai/ARTEX
archive_name: "BaaRai--ARTEX"
revision: 22ae88afabf66e47e73644a0528d8b427c4c80b8
revision_url: https://github.com/BaaRai/ARTEX/commit/22ae88afabf66e47e73644a0528d8b427c4c80b8
analyzed_at: 2026-11-21
licence: "AGPL-3.0, with use restrictions the README adds as terms from the maintainers; the web UI template and one vendored script are MIT"
size: "182,038 lines of Go in 667 files, 85,105 of them tests; db/ is 43,963 lines, server/ 62,240, agent/ 23,321. The lessons subsystem is 606 lines"
activity: "1,259 commits from 26 July to 21 November 2026. The original author's 381 end on 7 October 2026 and the fork's maintainer's 664 begin the next day; the pin is the v0.7.0 release merge"
tests: "1,655 Go test functions in 386 test files, run in CI against PostgreSQL 16; twenty-nine cover lessons. I ran none; the lesson selection, retraction and revival were re-derived outside the tree"
capabilities: "trust_state, scope_enforced, audit_log, negative_eval"
capability_evidence:
  trust_state: "lessons, and a finding's triage status at goal proof — every finding list returns a triaged finding with its label | db/lessons.go:335-349, :380, :248-258, agent/tools.go:1425-1430, :1089-1107 | `retireLessonsIfEmpty` sets a lesson's stored status to `retired` when a changed disposition has withdrawn its last live evidence row, the selection query excludes `retired`, and a later confirmation returns the row to `candidate`; `adopted` has no writer. `prove_goal` refuses a finding whose status is `false_positive`, `duplicate` or `ignored`, and the overview's count leaves those out; a goal met before the verdict stays met | db/lessons_test.go:502, agent/fact_provenance_test.go:243"
  scope_enforced: "asset graph, the agent's list_assets inside a task, and the company key on lessons — the planner can add scope rows to its own task, and the Auto and chat agents query unscoped | db/asset_dsl.go:577-655, db/task_assets_context.go:65-90, db/exploration_sources.go:16-41, db/lessons.go:381-384 | `QueryDSLInScope` and `GetByIDsInScope` join assets to the scope rows of the task and its direct source tasks and add `id IN (SELECT id FROM target)`; every exploration-graph read carries one `exploration_id`, and other tasks are reachable only through one hop of live `task_relations`. A lesson is selected when its company is among the task's `task_scope` companies, or when it and the task both have none. The scope rows are writable by the planner through `add_task_scope`, and both reads follow what it adds. With no task id the asset query is global | db/assets_test.go:1160, db/asset_dsl_or_scope_test.go:29, db/exploration_sources_test.go:92, db/lessons_test.go:94"
  audit_log: "coverage ledger only — assets and lessons have no mutation record | db/coverage_ledger.go:149-187, db/schema.sql:1605-1617 | `RecordCoverage` upserts one current row per task, surface and risk area and inserts every write into `coverage_ledger_history` in the same transaction; no statement updates or deletes history rows. No product code reads the table, and it is deleted with its task | db/coverage_ledger_test.go:100"
  negative_eval: "scope boundaries on the asset, exploration and lesson read paths, and a retracted lesson | db/exploration_sources.go:74-81, :161-183, db/asset_dsl.go:602, db/lessons.go:380-384 | committed cases assert that an indirect source task's fact is invisible, that a running source intent does not appear in inherited lists, traces, search or detail, that an out-of-scope asset is absent from a scoped query and from one whose `OR` branch names it, that another company's lesson and a company-less lesson are absent from a task's selection, and that a lesson retired by a reversed disposition is not selected, each beside rows that must be returned | db/exploration_sources_test.go:8 and :92, db/assets_test.go:1160, db/asset_dsl_or_scope_test.go:29, db/lessons_test.go:94 and :502"
stack_storage: "postgres, files"
stack_retrieval: ""
stack_source: "reviewed"
matrix:
  memory_unit: "Several: an asset row keyed on its value; an exploration node (goal, intent, fact, finding, hint, digest) with a state and a server-stamped origin; a coverage row per surface and risk area; and a lesson, a kind, cue and action built by string rules from one finding, with a status and evidence rows"
  storage: "PostgreSQL: one global assets table, per-task exploration nodes and edges with anchors to assets, a coverage ledger with a history table, three lesson tables; content-addressed files for captured request and response evidence"
  retrieval: "No search engine. Each planner round is rebuilt from windowed newest-first reads of the task's graph with cursors and digests for the rest; lessons are one SQL query filtered by company, category and status, capped at eight rows with no cursor"
  write: "Agent tools write assets, facts, findings and coverage; a person sets a finding's disposition over an authenticated route; lessons are extracted by rule when a disposition changes, a retest completes or the task ends, with no model call"
  update_delete: "Asset upserts overwrite scalars and union arrays with no history; facts are append-only; cold regions are folded into digests that keep their members; a changed disposition marks a lesson's evidence row withdrawn and retires the lesson at zero live rows; a lesson has no edit or delete path"
  scoping: "A task reads assets inside its scope rows and graph nodes of itself plus at most eight direct source tasks; a lesson is served to tasks of its company and category, and a company-less lesson to every company-less task. The planner can add scope rows to its own task. One operator, no tenants"
  integration: "A Go server with an embedded web UI; planner, worker, retester and platform agents on an external agent SDK; lessons framed in the nonce envelope and appended to the planner and worker system prompts when an environment flag is set"
  background: "A compaction pass folds settled graph regions into model-written digests; lesson extraction runs after a disposition change, a completed retest and a terminal task status"
  trust: "A finding's disposition is set by a person, gates which lesson is built, is copied onto the node the agents read, and is refused as goal proof when false positive, duplicate or ignored; a lesson is `candidate` or `retired` and the selection excludes retired rows; a fact carries a declared confidence and source that one tool refuses on"
  strengths: "Explicit one-hop task inheritance that is read-only by construction and tested negatively, a nonce-framed envelope for stored text re-entering prompts, digests that hide and never delete, evidence bound to captured traffic, and lessons whose support is withdrawn in the same call that reverses the verdict behind them"
  risks: "The planner holds a tool that writes the scope rows its own asset and lesson reads follow; lessons of tasks declared by domain alone form one pool shared by every such task; a goal met on a finding stays met when the finding is later ruled a false positive; no lesson can be edited or deleted"
---

## 1. Executive Summary

ARTEX is a self-hosted penetration-testing platform in Go on PostgreSQL. A
planner splits a goal into intents, workers run tools, and results are written
into two graphs: a global asset graph and a per-task exploration graph. This
report covers only what the system remembers across turns and tasks.

It carries `trust_state`, `scope_enforced`, `audit_log` and `negative_eval`.
`audit_log` sits on the coverage ledger alone and does not reach lessons.

**Licence and provenance.** `LICENSE` is the unmodified AGPL-3.0 text. The
README then adds permitted and prohibited uses, calls them additional terms
from the maintainers, and says use of the project means agreement
(`README.md:803-838`); code review and academic research are listed as
permitted. `web/` is MIT, a third party's UI template. The repository is an
English translation and continuation of a project whose original repository is
no longer public (`README.md:779`), and its history holds the original
author's commits to 7 October 2026. The Go module path and the agent SDK
dependency carry the original owner's name, and the SDK was not opened for
this reading.

**Cross-task memory has three forms, and the oldest is the soundest.**

- **Inheritance.** A task may name up to eight source tasks. Its agents then
  read the sources' facts, findings and finished intents, tagged as inherited,
  through one hop of live relations (`db/exploration_sources.go:16-41`). Writes
  cannot cross: every mutation carries the receiving task's `exploration_id`.
- **The asset graph.** One table for the installation. An agent inside a task
  sees only assets matched by the scope rows of that task and its sources
  (`db/task_assets_context.go:65-90`).
- **Lessons.** A rule turns each triaged finding into one line of text for
  later tasks (`db/lessons.go:109-241`). No model writes it. Injection is off
  unless `ARTEX_RSI_LESSONS=inject`.

**A lesson follows the verdict behind it, when the verdict is written.** Each
lesson holds evidence rows naming the finding or retest it came from. A
disposition change runs the extraction as soon as it commits. The extraction
marks that finding's rows withdrawn on lessons of the opposite kind and sets a
lesson with no live row to `retired`, which the selection excludes
(`db/notification.go:509-514`, `db/lessons.go:269-289`, `:335-349`, `:380`).
The withdrawn row stays, so a retired lesson names what it rested on.

**A false-positive verdict stops goal proof.** The disposition is copied into
the finding node's payload in the same transaction, every finding list an
agent reads carries it, and `prove_goal` refuses a finding marked
`false_positive`, `duplicate` or `ignored` (`agent/tools.go:1425-1430`). The
check runs when the goal is proved. A goal proved before the verdict stays
met.

**The scope rows belong to the reader.** The planner holds `add_task_scope`,
which writes a company, domain or address row into its own task's scope. The
asset query and the lesson selection both follow every row of the task,
whoever wrote it.

## 2. Mental Model

A lesson is a triaged finding restated by rule, kept while its evidence
stands.

```mermaid
%% caption: a finding's disposition is copied onto the node agents read, refused as goal proof when false positive, and gates which lesson a string rule builds; a changed disposition marks the lesson's evidence withdrawn and retires it at zero live rows, and the selection serves unretired lessons of the task's companies, or company-less lessons to a company-less task, inside a nonce frame
flowchart TD
    T["target response<br/>(untrusted)"] --> W["worker: report_finding<br/>(vulnclass, summary)"]
    W --> F[("findings row<br/>status = pending")]
    OP["operator: PATCH or bulk<br/>status route (JWT)"] --> F
    RT["completed retest<br/>(a person opens it)"] --> F
    F -->|"same transaction"| N["finding node payload:<br/>status label"]
    N --> LF["every finding list,<br/>with the label"]
    N --> PG{"prove_goal"}
    PG -->|"false_positive,<br/>duplicate, ignored"| REF["refused:<br/>goal stays open"]
    PG -->|"other status, with<br/>verified bound traffic"| MET["goal met;<br/>nothing reopens it"]
    F -->|"after commit"| X{"extraction: status change,<br/>completed retest, task end"}
    X --> MC{"company rows in<br/>the task's scope"}
    PL["planner:<br/>add_task_scope"] -.->|"can add a row"| MC
    MC -->|"two or more"| RO["withdraw only,<br/>write nothing"]
    MC -->|"one or none"| EX["string rules, no model;<br/>company id, or NULL"]
    EX --> L[("rsi_lessons<br/>candidate or retired")]
    EX -->|"verdict changed: set<br/>withdrawn_at on evidence"| RET["retire a lesson with<br/>no live evidence"]
    RO --> RET
    RET --> L
    L --> SEL["next task: not retired;<br/>its companies, or NULL<br/>when it has none; LIMIT 8"]
    SEL --> R["render, stop at 1,800<br/>characters, nonce-framed"]
    R -->|"inject mode"| SYS["planner and worker<br/>SYSTEM prompt"]
    style MET fill:#7f1d1d,color:#fff
    style PL fill:#7f1d1d,color:#fff
```

## 3. Architecture

A Go server, a PostgreSQL schema of 57 tables in one idempotent file with
twelve numbered migrations beside it, an agent package (planner, worker, main
agent, retester, compactor) on an external SDK, and a Next.js UI. There is one
operator: a single JWT subject, bound to a password version, guards every API
route but the auth routes and the health and readiness probes
(`server/auth.go:188-203`, `:332-340`). There is no user or tenant table.

| Memory surface | Scope | Written by |
| --- | --- | --- |
| Asset graph | Installation | Agent tools, scan ingest, HTTP |
| Exploration graph | Task, plus direct sources on read | Planner and worker tools |
| Coverage ledger and history | Task | Worker's `record_coverage` |
| Cold digests | Task | Background model pass |
| Lessons | Company and category, or the company-less pool | Rule-based extraction |
| Task scope rows | Task | Task creation, the operator, the planner, asset inserts |
| Task credentials | Task | Agent or operator |
| Skills directory | Installation | The platform agent only |

Each planner round is rebuilt from a graph overview, the coverage line and the
planner's own todo list. The todo list lives in a Go map on the planner struct
(`agent/planner.go:48-53`, `:116-125`).

### Deployment and ergonomics

Docker Compose with PostgreSQL, or a single binary with the UI embedded. The
lessons flag appears in `RSI.md` and `docs/rsi-lessons.md` and in no README,
example environment file or UI.

## 4. Essential Implementation Paths

| Path | Location |
| --- | --- |
| Lesson text normalisation | `db/lessons.go:42-57` |
| Lesson scope lookup | `db/lessons.go:66-96`, `db/task_context.go:352-356` |
| Extraction rules | `db/lessons.go:109-241` |
| Dedupe key and upsert | `db/lessons.go:59-64`, `:243-261` |
| Evidence withdrawal and retirement | `db/lessons.go:269-349` |
| Selection query | `db/lessons.go:356-409` |
| Extraction after a verdict | `db/lessons.go:430-453`, `db/notification.go:509-514`, `:547-558` |
| Rendering | `db/lessons.go:460-491` |
| Wiring into the agents | `server/lessons.go:41-66`, `agent/data_envelope.go:59-68` |
| Lesson tables | `db/schema.sql:1545-1585`, `db/migrations/0012_lesson_withdrawn.sql` |
| Scoped asset read | `db/asset_dsl.go:577-655`, `db/task_assets_context.go:65-90` |
| Scope rows and the planner's tool | `db/task_scope.go:154-238`, `agent/tools_insert.go:468-520` |
| Task inheritance | `db/exploration_sources.go:16-41`, `:74-81` |
| Fact write and labels | `agent/tools.go:1598-1668` |
| Goal proof refusals | `agent/tools.go:1380-1444`, `db/finding_traffic.go:528` |
| Triage labels that block a goal | `agent/tools.go:1082-1107` |
| Graph overview windows | `agent/tools.go:481-720` |
| Data envelope | `agent/data_envelope.go:36-57` |
| Coverage ledger and history | `db/coverage_ledger.go:149-187` |
| Cold digests | `agent/compaction.go:55-148`, `db/digest.go:122-221` |
| Finding disposition routes | `server/server.go:2602`, `:2706` |
| Disposition write and node mirror | `db/notification.go:575-620` |

## 5. Memory Data Model

**Asset.** One row per domain, IP, subdomain, app, service or endpoint, unique
on its value with no task or company in the key (`db/schema.sql:84-92`). It
carries `task_ids`, a company, and three record times: `created_at`,
`last_seen`, `updated_at`.

**Exploration node.** `kind` is one of `begin`, `goal`, `intent`, `fact`,
`finding`, `hint`, `digest`, with a JSON payload, a `state` and an `origin`
stamped by the server from the calling agent. Edges are `spawns`,
`derived_from`, `yields`, `proves`, `covers`. An anchor row links a node to an
asset.

**Fact.** A summary, a detail, a one-line evidence string, a `confidence` of
`observed` or `inferred`, and a `source` from a fixed list that includes
`target_response`, `tool_output` and `inference` (`agent/tools.go:1598-1625`).
Both labels are declared by the agent that writes the fact.

**Finding.** A node plus a `findings` row whose `status` starts at `pending`
(`db/schema.sql:1203`) and is the person's disposition: `confirmed`,
`false_positive`, `duplicate`, `ignored`, `risk_accepted` and others. A second
column, `report_state`, tracks the report stage after triage and feeds no
lesson. Evidence binds a finding to content-addressed snapshots of captured
requests and responses.

**Scope row.** A `task_scope` row is a company, root domain, subdomain,
address, range, registration number or keyword (`db/schema.sql:781-782`), with
a `source` of `auto`, `agent` or `manual`. An agent's addition that widens a
declared scope is stored with `expanded` set (`db/task_scope.go:225-233`).

**Lesson.** `kind` (`positive`, `negative`, `caution`), `cue`, `action`,
optional category and company, a `status`, and a `dedupe_key` that is a hash of
kind, scope, cue and action. Support is not stored; it is the count of
evidence rows with no `withdrawn_at`, taken at read time. The status column
accepts `candidate`, `adopted` and `retired`. Product code writes `retired`
and returns a row to `candidate`; `adopted` appears only in the CHECK
constraint and in tests that set it with SQL (`db/schema.sql:1555-1556`).

The company comes from the task's `task_scope` rows of kind `company`. A task
with exactly one gets that id on its lessons, and a task with none gets NULL
(`db/lessons.go:91-96`). A task declared by domain alone has no company.

No field records when something about a target was true, as distinct from when
it was written. `bitemporal` is withheld.

## 6. Retrieval Mechanics

### The planner's view of its own task

`graphOverviewData` is injected into every planner round as windows over the
graph, each newest first: thirty open intents, twelve recent finished ones,
ten findings, twenty facts not folded into a digest, fifteen digests
(`agent/tools.go:481-720`). Each finding in the window carries its triage
status, and `findings_total` counts the findings not marked `false_positive`,
`duplicate` or `ignored` (`:581`, `:606-611`). The rest stay reachable.
`list_facts` pages by cursor, `list_findings` lists up to 500, and a folded
region opens with `expand_digest`.

### Other tasks

`…WithSources` readers append the direct source tasks' nodes, tagged with the
source task id. An inherited intent is visible only once it is terminal, so a
running source task's in-flight work never enters another task's frontier
(`db/exploration_sources.go:74-81`). The overview's share for related tasks is
capped at 48,000 runes, 8,000 per source (`agent/tools.go:730-731`).

### Assets

`list_assets` inside a task goes through `scopeTargetCTE`: the task and its
direct sources, joined to their scope rows by company, root domain,
subdomain, IP range or registration number, and the query adds
`id IN (SELECT id FROM target)` (`db/asset_dsl.go:602`). Membership is by
scope row, not by which task produced the asset, and the join takes every row
whatever its `source`. With no task id, the platform and chat agents get the
unscoped query (`:578-580`).

The query language compiles a disjunction inside one pair of parentheses, so
the scope clause appended with `AND` binds the whole expression
(`db/asset_dsl.go:305-309`). Until
[`84a623bf2deae56a5660108a234fe437dca8e9ef`](https://github.com/BaaRai/ARTEX/commit/84a623bf2deae56a5660108a234fe437dca8e9ef)
on 20 November 2026 it did not: `a OR b` compiled to
`(a) OR (b) AND id IN (…)`, and the first branch returned assets from the
whole installation. v0.6.0 is on the unparenthesised side of that commit.

No read filters on `last_seen`; it orders results only.

### Lessons

One query (`db/lessons.go:367-390`). It keeps rows that are not `retired`,
whose category is NULL or the task's, and whose company is one of the task's.
A row with no company is kept only for a task that has no company either
(`:381-384`). It orders company matches first, then category matches, then
positive before negative before caution, then live support, with `LIMIT 8` for
injection and 50 for the HTTP preview. Both scope terms are written
`col IS NOT NULL AND col = …`, so a NULL never sorts ahead of a match.

On a scratch PostgreSQL with the lifted DDL and query, a store of five lessons
of one company, three of a second and four with none returned five to a task
of the first company, four to a company-less task, and eight to a task holding
both companies.

Rendering stops at the first entry that would pass 1,800 characters
(`db/lessons.go:481-483`). A cue may run to 160 characters and an action to
320, so three full-length lessons fill the block and a long early entry hides
shorter later ones. The function returns the ids it rendered, and those are
what the usage log records (`server/lessons.go:55-65`). The block is fixed
when the task's agents are built.

## 7. Write Mechanics

### Facts, findings, coverage

Workers call `record_fact`, `report_finding` and `record_coverage`. A fact is
created `confirmed` with its origin stamped by the server; no tool or route
edits or deletes one. A fact's asset anchors must name existing assets, checked
under a row lock before the node is created. A coverage write that exceeds a
field limit is refused instead of truncated (`db/coverage_ledger.go:41-52`).

### Assets

Eight upsert functions. On conflict the last non-null writer wins per scalar
column and arrays are unioned (`db/assets.go:754-778`). When two tasks
disagree about a status code or a page title, the later one replaces the
earlier and nothing keeps the old value.

### Scope rows

Task creation writes the company rows the operator chose. After that the rows
have three writers: the operator's route, the automatic row for each host a
worker inserts, and `add_task_scope`, which the planner and the operator's
chat agent hold (`agent/tools.go:2407`, `agent/tools_insert.go:739`). The tool
accepts every kind, including `company` by name or id, and its description
calls the result a coverage scope that is not enforced
(`agent/tools_insert.go:462-476`).

### Lessons

`ExtractLessonsForTask` reads each finding of the task with its newest
completed retest and applies four rules (`db/lessons.go:183-238`):

- `confirmed`, `resolved` or `fixed` gives a **positive** lesson, and a second
  one when that retest reproduced it.
- A retest verdict of `fixed` or `inconclusive` on such a finding gives a
  **caution**.
- `false_positive`, `duplicate`, `ignored` or `risk_accepted` gives a
  **negative** lesson that begins `Do not re-report without new mechanics` and
  ends with the status.
- `pending` and `in_progress` give nothing and withdraw nothing.

The first and third rules also withdraw. A positive disposition marks the
finding's evidence withdrawn on negative lessons. A negative one marks it
withdrawn on positive lessons, on cautions, on every retest of the finding,
and on any negative lesson whose action differs from the one being written
(`:203`, `:221-237`). A lesson left with no live evidence is set to `retired`,
and an upsert that meets a retired row with no live evidence sets it back to
`candidate` (`:335-349`, `:248-258`).

A task with more than one company writes no lesson, because the row has one
company column, and withdraws as usual (`:114-117`).

The extraction has five callers: the single and the bulk disposition change, a
completed retest, a terminal task status, and
`POST /api/tasks/{id}/lessons/extract` (`db/notification.go:513`, `:558`,
`db/finding_retests.go:289`, `server/manager.go:1644-1646`,
`server/lessons.go:104`). The first three call it after their transaction
commits; a failure is logged and the status change stands
(`db/lessons.go:430-439`).

A finding's status has three writers in product code, all through
`SetFindingStatusTx`: the operator's authenticated `PATCH`, a bulk route for
several findings, and a completed retest whose verdict is `fixed`
(`db/notification.go:575-620`, `db/finding_retests.go:267-284`). The retest
verdict comes from the retester agent, in a session only a person can open. No
planner or worker tool takes a finding status.

Deduplication needs identical text. Positive and negative actions embed the
finding's free-text summary, so two tasks merge into one lesson only when
their summaries match; cautions hold only the cue and verdict and merge
widely. Text is cut by runes, 160 for the cue and 320 for the action, and a
negative action cuts the summary so the status suffix survives
(`db/lessons.go:42-57`, `:217-220`).

### Operational cost

Lessons cost one query per task start and no model call. Extraction runs on
every disposition change whatever the lessons flag says. Digests cost one
model call per folded block, with bodies reused when a block's member set and
content version are unchanged.

## 8. Agent Integration

The lessons block is appended to the system prompt of the planner and the
worker and to no other agent. `frameLessonsBlock` wraps it in the nonce-framed
envelope with a fresh nonce per assembly and the marker stem rewritten inside
the content (`agent/data_envelope.go:59-68`, `agent/planner.go:528`,
`agent/worker.go:574`). Every other derived field goes in the user message
inside the same frame: recent facts, findings, digests, related-task data,
intent summaries, the assets an intent targets, and hints and credentials
written by an agent (`:72`, `:82-95`, `:107-230`). The file's own comment
prices it: the frame marks data and cannot stop a model from following it. The
lessons block is the one framed field placed in the system prompt.

**`human_review` is withheld.** A person's disposition is what admits most
lessons, and the agent that wrote the finding holds no tool that sets it. Two
things keep the mark off. A model's retest verdict also admits lessons: `fixed`
sets the finding's status and yields a positive lesson with a caution beside
it. And what is reviewed is the finding. The lesson's own status is written by
the extraction rule and by nobody else: no route or interface retires or
adopts a lesson, and candidates are injected as they stand.

## 9. Reliability, Safety, and Trust

### A triage verdict gates goal proof, at the moment of proof

`SetFindingStatusTx` writes the status to the `findings` row and to the
finding node's payload in one transaction (`db/notification.go:596-605`).
Every finding read an agent has carries it: `list_findings`, the related-task
overview, `node_detail`, and the list injected into each planner round
(`agent/tools.go:1063-1080`, `:1225`, `:606-611`). An inheriting task reads
the same node and sees the same label.

`prove_goal` refuses a finding whose status is `false_positive`, `duplicate`
or `ignored`, and the round overview's `findings_total` leaves those three out
(`agent/tools.go:1425-1430`, `:1089-1107`). A finding must also hold captured
traffic whose host matches its asset, checked on the server
(`:1434-1442`, `db/finding_traffic.go:528`). Both refusals are in the agent
core and apply with lessons off.

Three limits:

- **`risk_accepted` is not in the list.** Such a finding counts in the total
  and can mark a goal met, while the lesson rule files it as negative.
- **Nothing reopens a goal.** One product call sets a goal's state, to `met`
  (`agent/tools.go:1444`). A finding ruled a false positive after it closed a
  goal leaves the goal met, and a task whose goals are all met is judged
  complete.
- **The node state does not move.** It stays `confirmed`; `dismissed` exists
  in the schema and has no writer outside one test.

### The planner writes the rows its reads are scoped by

`add_task_scope` is in the planner's tool list, and `AddAgentScope` inserts
what it is given once a named company exists
(`agent/tools.go:2407`, `db/task_scope.go:154-238`). Neither scoped read asks
who wrote a row. `scopeTargetCTE` joins every scope row of the task, so one
call with `kind=company` brings that company's assets into `list_assets`
(`db/task_assets_context.go:79-88`). `TaskCompanyIDsContext` returns every
company row (`db/task_context.go:352-356`), so the same call changes the
lesson key:

- on a task declared by domain, later lessons are stored under the added
  company, and that company's lessons are selected the next time the task's
  agents are built;
- on a task with one company, a second company's lessons join the selection,
  and the task writes no further lesson.

What stands between target text and that call is a prompt rule: the untrusted
data preamble tells the agent never to call `add_task_scope` because data asks
(`agent/untrusted_prompt.go:34`). An agent's widening row is stored with
`expanded = true` and returned to the caller with the flag
(`db/task_scope.go:225-233`); no query filters on it.

### Lessons of company-less tasks form one pool

A lesson's company is NULL when its source task had no company row, and a
NULL row is selected for every task that has no company row, inside the
category (`db/lessons.go:91-96`, `:382`). Tasks declared by domain alone are
exactly those tasks, so two unrelated engagements declared that way read each
other's lessons. A positive lesson's text is the finding summary, which names
the source target's endpoints. `docs/rsi-lessons.md:84` states the rule, and
injection is off by default.

Two more routes lead into the pool:

- **Rows written before 17 November 2026.** Until that day's change the scope
  lookup read `tasks.company_id`, which task creation does not fill, so every
  lesson was stored with no company. No migration rescopes them, and the
  dedupe key includes the company, so a new extraction writes a scoped twin
  beside the old row.
- **A deleted company or category.** Both foreign keys are
  `ON DELETE SET NULL` (`db/schema.sql:1553-1554`). On the scratch database,
  deleting the second company raised the company-less task's selection from
  four lessons to seven.

### What a withdrawal keeps and what it loses

The withdrawal is an `UPDATE` that sets `withdrawn_at` on the evidence row
(`db/lessons.go:271-280`, `:295-304`). A retired lesson keeps its cue, action,
status and the rows naming each finding and retest it rested on.

The row holds one timestamp. Confirming the finding again clears it
(`:173-175`), and the earlier withdrawal leaves no trace. Lessons therefore
have no mutation history, and `audit_log` rests on the coverage ledger alone.

Four edges, the first three re-derived on the scratch database with the lifted
upsert and withdrawal statements:

- **A change inside the negative group replaces the lesson.**
  `false_positive` followed by `duplicate` left the first lesson `retired`
  with its row withdrawn and the second `candidate`.
- **A retired lesson returns when another finding matches it.** After a
  reversal retired `Confirmed xss: s`, a second finding with the same cue and
  summary set it back to `candidate` with a support of one, the withdrawn row
  beside the live one.
- **A reopened finding withdraws nothing.** Moving a confirmed finding back to
  `pending` leaves its positive lesson selectable, by design and under test
  (`db/lessons_test.go:879`).
- **A deleted source cannot be withdrawn.** No statement edits or deletes a
  lesson row. Deleting the source task or finding leaves the lesson with an
  evidence row naming an id that is gone, and extraction, which walks the
  task's existing findings, cannot reach it.

The extraction after a verdict runs outside the transaction that wrote the
verdict. When it fails, the old lesson stays selectable until the next
extraction of the task.

The usage table `rsi_lesson_usage` records the rendered ids and has no reader
outside one test.

### Why three marks are withheld

`human_review` and `bitemporal` are covered above.

**`tombstone`.** Two near-misses. The negative lesson is a line of prompt text
that the write path never consults: a re-reported finding lands as a new
`pending` row. The retired lesson is keyed on a hash of its text, and the
upsert does consult it, but a retired row with no live evidence is exactly the
row it revives. The branch that keeps a retired row retired applies when live
evidence remains, a state only hand-written SQL produces
(`db/lessons.go:250-257`, `db/lessons_test.go:788`).

**`trust_state` rests on two fields.** The lesson status filters the
selection. The finding's triage status filters goal proof and the overview
count, and is a label everywhere else. A fact's `confidence` and `source` are
declared by the writing agent at write time, never change, and filter no read;
`prove_goal` refuses on them (`agent/tools.go:1409-1423`).

## 10. Tests, Evals, and Benchmarks

1,655 `func Test` in 386 test files. CI starts PostgreSQL 16 and runs `go test
-p 1 ./...` with `gofmt`, `go build` and `go vet`, a race-detector pass over
named packages, and an advisory job on the newest Go release
(`.github/workflows/ci.yml:9-117`). I ran none of it.

**The boundary tests are the strong part.**
`TestExplorationDirectSourceReadView` asserts that a source of a source is
invisible, that a live source intent is absent from the frontier, the
inherited list and finding lineage, and that an inherited fact cannot be
mutated through the receiving store (`db/exploration_sources_test.go:92`).
`TestInheritedActivityReadsRequireTerminalIntent` asserts five read paths do
not return a reopened intent (`:8`). `TestQueryDSLInScopeMembership` tags
in-scope assets with a foreign producer task, to show membership is by scope,
and asserts out-of-scope ids are absent (`db/assets_test.go:1160`).
`TestQueryDSLInScopeOrDoesNotEscape` runs a query whose first branch matches
an asset on each side of the boundary and fails if the outside one returns
(`db/asset_dsl_or_scope_test.go:29`).

**Lessons have twenty-nine tests**: twenty-four in `db/lessons_test.go`, three
in `server/lessons_test.go`, one on the frame and one on the migration.

- **Scope and order.** `TestTaskLessonsUsesTaskScopeAndRanksCompanyFirst`
  inserts the generic row last, so that id order alone would rank it first,
  and asserts that a company's task sees its own lesson only, that a
  company-less task sees no company lesson, and that neither company sees the
  other's (`db/lessons_test.go:94`).
- **Withdrawal.** `TestExtractLessonsRetractsReversedDisposition` walks
  confirmed, false positive, confirmed, and fails if the retired positive is
  selected (`:502`). `TestDispositionChangeExtractsLessons` changes the status
  through the product call and checks the lesson without calling the
  extraction (`:923`). Others cover a lesson shared by two findings, every
  retest of a reversed finding, a change inside the negative group, a task
  that gained a second company, and an unfinished retest.
- **Text and frame.** A multi-byte cut, full-length CJK lessons against the
  character cap, the rendered-id return, and a lesson that tries to close its
  own frame (`:48`, `:77`, `:60`, `agent/data_envelope_test.go:203`).

**Goal proof.** `TestProveGoalRefusesFalsePositiveFinding` proves a goal with
a false-positive finding, expects the refusal and an open goal, then proves it
with a confirmed one (`agent/fact_provenance_test.go:243`).
`TestGraphOverviewFindingListCarriesStatus` checks the label and the count
(`agent/tools_overview_test.go:56`).

No lesson test deletes a company or adds a scope row through the planner's
tool, and no agent test changes a finding's status after a goal is met.

`RSI.md` cites six arXiv papers as the source of the design's ideas, and the
identifiers resolve to the titles it names. The lesson admission rule is taken
from [Harness²](../harness2/), which `db/lessons.go:15-20` and the schema
comment name: no lesson without a cue, an action and evidence. ARTEX has no
paper of its own. `scripts/benchmark/` holds a runner and one ground-truth
file; results are written to an ignored directory and none is committed.
Nothing in the tree measures whether lessons help.

## 11. For Your Own Build

### Steal

**Make cross-task inheritance explicit, one hop and live.** A named relation,
a cap, a query on every read so a deleted source disappears, and only finished
work visible. Read-only falls out of scoping every write to the receiver.

**Frame stored text when it re-enters a prompt.** A per-message random nonce
on both markers, and the marker stem neutralised inside the content.

**Key a lesson's support on its sources, and withdraw without deleting.** One
evidence row per finding or retest lets a reversed verdict withdraw exactly
its own support, a lesson shared by two findings survives the loss of one, and
a retired lesson can say what it rested on.

**Run the correction where the verdict is written.** The disposition call
triggers the extraction itself; the end-of-task pass is the fallback.

**Rank a nullable scope match with `IS NOT NULL AND =`.** A bare
`(col = $1) DESC` sorts NULL first in PostgreSQL. Test the order with the
unscoped row inserted last.

**Parenthesise a compiled filter before appending the scope clause.** Test it
with a disjunction whose first branch matches a row on each side.

**Log what was rendered, not what was selected.** Have the renderer return the
ids that fitted.

**Stamp the writer on the server.** A fact's `origin` is never taken from the
tool's input.

**Let summaries hide and never delete.** A digest covers its members while
they stay cold, a revived member reappears, and a re-compression starts from
the source nodes.

### Avoid

**Do not give the reader a tool that writes its own scope.** A filter over
rows the agent can insert is a filter the agent sets.

**Do not let NULL be a scope.** A missing company, a deleted company and a row
written before scoping existed all land in one pool that every company-less
task reads.

**Do not check a verdict only when the claim is made.** A goal closed on a
finding needs to reopen when the finding is overturned.

**Do not keep one timestamp for a state that can flip twice.** Clearing
`withdrawn_at` on restoration erases the withdrawal.

### Fit

The inheritance model and the scoped asset read suit any multi-task agent
platform with one operator who trusts the planner with the scope. The lessons
subsystem is rule built, evidence linked, company scoped, framed and off by
default. It is safe to turn on where every task declares exactly one company,
and not across tasks declared by domain alone.

## 12. Open Questions

- **Who retires or adopts a lesson by hand?** `RSI.md:53-55` calls status
  changes owner actions, the tests set both states with SQL, and no route does.
- **How will a multi-company task attribute a finding?**
  `docs/rsi-lessons.md:73-77` calls per-finding company attribution a later
  change.
- **Is `expanded` meant to gate a read?** The flag is written and returned,
  and nothing consults it.
- **Is the outcome card's company meant to come from `task_scope` too?**
  `db/task_outcome.go:60` reads `tasks.company_id`, the column task creation
  does not fill.
- **Does restoring an archived task renumber its findings?** If it does, a
  second extraction adds evidence for the same underlying finding. Not traced.
- **What does the agent SDK persist?** Session compaction and transcripts live
  in a dependency this reading did not open.

## Appendix: File Index

| File | Role |
| --- | --- |
| `db/lessons.go`, `server/lessons.go` | Lesson extraction, withdrawal, selection, rendering, wiring |
| `db/lessons_test.go`, `server/lessons_test.go` | Twenty-seven of the twenty-nine lesson tests |
| `docs/rsi-lessons.md`, `RSI.md` | The project's description of the loop |
| `db/schema.sql`, `db/migrations/` | 57 tables and twelve migrations |
| `db/asset_dsl.go`, `db/task_assets_context.go`, `db/assets.go` | Asset reads and upserts |
| `db/task_scope.go`, `agent/tools_insert.go` | Scope rows and the tools that write them |
| `db/exploration.go`, `db/exploration_sources.go` | The per-task graph and inheritance |
| `db/coverage_ledger.go` | Coverage ledger and its history |
| `db/digest.go`, `agent/compaction.go`, `agent/coldgraph.go` | Cold digests |
| `agent/tools.go`, `db/finding_traffic.go` | Graph overview, facts, findings, goal proof |
| `agent/data_envelope.go`, `agent/data_envelope_test.go` | The nonce-framed envelope and the lessons frame |
| `agent/planner.go`, `agent/worker.go` | Where the lessons block joins the system prompt |
| `db/findings.go`, `db/notification.go`, `db/finding_retests.go` | Finding status writers and the node mirror |
| `db/task_context.go` | A task's companies |
| `db/exploration_sources_test.go`, `db/assets_test.go`, `db/asset_dsl_or_scope_test.go` | The boundary tests |
| `agent/fact_provenance_test.go`, `agent/tools_overview_test.go` | Goal-proof refusals and the overview label |

### Recorded searches

Run with `/usr/bin/git` in a full clone at the pinned commit.

- `git grep -c -E '^func Test' -- '*.go'`, summed — 1,655.
- `git grep -n -E 'UPDATE rsi_|DELETE FROM rsi_' -- . ':!*_test.go'` — `db/lessons.go:271`, `:295` and `:340`: two evidence withdrawals and the retirement update; no statement edits or deletes a lesson row.
- `git grep -n -E 'rsi_lesson' -- '*.go' ':!*_test.go' ':!db/lessons.go'` — nothing; no task, finding, company or category path touches a lesson.
- `git grep -n -E "'retired'|'adopted'" -- . ':!*_test.go'` — `db/lessons.go:251`, `:341`, `:343`, `:380` and the CHECK at `db/schema.sql:1556`; `adopted` only in the CHECK.
- `git grep -n -E 'FROM rsi_lesson_usage|JOIN rsi_lesson_usage' -- .` — `db/lessons_test.go:468` only.
- `git grep -n -E 'ExtractLessonsForTask\(|syncLessonsFor(Finding|Tasks)\(' -- '*.go' ':!*_test.go'` — the five callers in section 7.
- `git grep -n -E 'INTO task_scope' -- '*.go' ':!*_test.go'` — `db/tasks.go:303` at creation, `db/task_scope.go:86` afterwards, and the archive restore.
- `git grep -n -E 'addTaskScope\(\)' -- '*.go' ':!*_test.go'` — the goal-registration step, `PlannerTools` and `MainAgentTools`, and the definition.
- `git grep -n -E 'expanded' -- 'db/*.go' ':!*_test.go'` — one inheritance comment and `db/task_scope.go`: the field, the insert, the classification and the listing; no `WHERE` names it.
- `git grep -n -E 'FindingFalsePositive|FindingPending|FindingRiskAccepted' -- 'agent/*.go' ':!*_test.go'` — `agent/tools.go:1093` only, the three blocking labels; `risk_accepted` is not among them.
- `git grep -n -E 'SetNodeState\(' -- '*.go'` — one product call, with `met`, at `agent/tools.go:1444`; `dismissed` is passed only at `db/exploration_sources_test.go:212`.
- `git grep -n -E "SET state='open'" -- '*.go' ':!*_test.go'` — four statements, each with `kind='intent'`; none reopens a goal.
- `git grep -n -E 'SetFindingStatus' -- 'agent/*_test.go'` — nothing.
- `git grep -n -E 'DELETE FROM companies|DeleteCompany\(|add_task_scope|AddAgentScope' -- db/lessons_test.go server/lessons_test.go` — nothing.
- `git grep -n -E '(UPDATE|DELETE FROM) coverage_ledger_history' -- .` — nothing.
- `git grep -n -E 'FROM coverage_ledger_history|JOIN coverage_ledger_history' -- . ':!*_test.go'` — nothing.
- `git grep -n -i -l lessons -- web extension scripts` — nothing.
- `git grep -n -E 'last_seen' -- 'agent/*.go' 'server/*.go' ':!*_test.go'` — nothing.
- `git grep -n -i -E 'CREATE TABLE IF NOT EXISTS (users|accounts|tenants|orgs)' -- '*.sql' '*.go'` — nothing.

## History

**2026-11-21** — [`22ae88afabf66e47e73644a0528d8b427c4c80b8`](https://github.com/BaaRai/ARTEX/commit/22ae88afabf66e47e73644a0528d8b427c4c80b8) — 226 commits, 17 to 21 November 2026, ending at the v0.7.0 release. [Pull request 391](https://github.com/BaaRai/ARTEX/pull/391), answering [issue 269](https://github.com/BaaRai/ARTEX/issues/269), closed five findings of the 19 November reading: goal proof on a false-positive finding, company-less lessons reaching every task, retraction waiting for a manual call, deleted evidence rows, and the byte cap. `trust_state` extends to the finding status at goal proof. Both earlier readings missed two things present at their pins: a top-level `OR` in an asset query escaped the task scope, fixed upstream on 20 November, and the planner holds `add_task_scope`, which writes the rows both scoped reads follow. [Section 9](#9-reliability-safety-and-trust) holds what remains. Nothing was built or run; the lesson SQL was re-derived on a scratch PostgreSQL.

**2026-11-19** — [`65045efae642159eeef3be5536c262f096f4c08d`](https://github.com/BaaRai/ARTEX/commit/65045efae642159eeef3be5536c262f096f4c08d) — 136 commits, 16 to 18 November 2026. Four pull requests, opened from the list the maintainer confirmed on [issue 269](https://github.com/BaaRai/ARTEX/issues/269), closed the inverted ranking, the unfilled company scope, the byte cut, the over-reporting usage log, the unframed lessons block and the missing retraction, with fifteen new lesson tests. `trust_state` is awarded on the lesson status; `scope_enforced` and `negative_eval` extend to lessons. [Section 9](#9-reliability-safety-and-trust) holds what the fixes leave: the false-positive label misses the planner overview and goal proof, company-less lessons reach every task, and retraction waits for a manual call and deletes its evidence. Screen findings match the first reading. Nothing was built or run; selection and retraction were re-derived with lifted SQL on a scratch PostgreSQL.

**2026-11-16** — [`9f99b7172aab33512d319f082080cb2892253e91`](https://github.com/BaaRai/ARTEX/commit/9f99b7172aab33512d319f082080cb2892253e91) — first reading, of the memory surfaces only. Screened first: four manifests inside the seven-day cooldown, one build-time script, two unpinned surfaces. Nothing from the tree was built or run; the lesson ordering, scope widening and text truncation were re-derived with lifted SQL on a scratch PostgreSQL and in a separate script.

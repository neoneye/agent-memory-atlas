---
title: "QualityLayer"
eyebrow: "Project lessons checked against the commits that touch their files"
description: "A source-available coding-agent workbench whose memory is a local SQLite catalog of lessons, each tied to files and retired when Git shows those files changed."
root: ../..
page_kind: system
source_name: "maxritter/qualitylayer"
source_url: https://github.com/maxritter/qualitylayer
archive_name: "maxritter--qualitylayer"
revision: 8635ab90a2d13084be33bddfaa74afa5d4d43e49
revision_url: https://github.com/maxritter/qualitylayer/commit/8635ab90a2d13084be33bddfaa74afa5d4d43e49
analyzed_at: 2026-11-13
licence: "QualityLayer Commercial Source-Available Licence: reading, evaluation and contribution forks are permitted; redistribution, reuse in another product and independent complete builds are not"
size: "357,668 lines of TypeScript in 1,773 readable files; the memory code is 8,094 lines across src/core/memory, src/memory-store, src/memory-engine and five top-level modules. 5,022 of the 7,613 tracked files are git-crypt ciphertext"
activity: "4,857 commits on main, 24 October 2025 – 13 November 2026, 4,248 of them by the maintainer"
tests: "2,415 files under qualitylayer/tests, of which 2,411 are git-crypt ciphertext, including all 75 memory test and fixture files; four licensing and workflow tests are readable"
capabilities: "trust_state, scope_enforced"
capability_evidence:
  trust_state: "lesson lifecycle — a stored active/retired column every agent read filters on | qualitylayer/src/memory-store/catalog.ts:52-56, :716-717; qualitylayer/src/core/memory/search/results.ts:36-40; qualitylayer/src/core/memory/lifecycle.ts:13-59; qualitylayer/src/core/memory/source-observation.ts:99-123 | `records.state` is `active` or `retired`. The catalog's `filter` opens every agent query with `state='active'`, the vector read selects active rows only, and `currentRecord` drops a retired id that reached the ranked list. Four actors move a lesson between the states, each recorded with a reason: the person, an agent through `memory_keep`, an agent at review, and QualityLayer itself when Git shows the lesson's files gone or changed for more than 90 days. A retired lesson is refused as the target of a save until restored. The state has two values and no candidate tier: a new lesson is active at once. The finer `sources` freshness (changed, unchanged, gone, unchecked) is computed per read and only labels a hit. | none readable: every memory test, `tests/core/memory-retirement-race.test.ts` among them, is git-crypt ciphertext at this commit, so the claim is read off the filter, the lifecycle writer and the four retiring callers"
  scope_enforced: "catalog and tool reads — the project id as a column AND-ed into every query and re-checked per record | qualitylayer/src/memory-store/catalog.ts:716-726, :334-340; qualitylayer/src/core/memory/search/results.ts:36-40; qualitylayer/src/memory-tools.ts:262-264, :311-313 | each lesson row carries `project`, and `filter` adds `project=?` whenever a project is given, which the search path always does. The vector candidates come from `activeVectors(project, model)`, and `currentRecord` rejects any ranked id whose record belongs to another project, which also covers hits returned by the bundled index. `memory_read` and `memory_keep` refuse an id from another project by message. Lessons about the person live in a reserved `personal` project that every repository's search reads on purpose. The mark covers reads; one catalog file holds every project, so the boundary is the predicate. | none readable: the memory tests are git-crypt ciphertext at this commit; the claim rests on the query builder, the vector read, the per-record recheck and the two tool refusals"
stack_storage: "sqlite, files"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A lesson: title, content up to 24,000 characters, one of six kinds, up to 32 repository-relative files, optional evidence of passing checks, visibility, revision, and an active or retired state"
  storage: "One SQLite catalog under the QualityLayer home for all projects, canonical; per project a bundled Engram build as a disposable full-text index and a table of 384-dimension vectors; optionally JSON files and a readable LESSONS.md under docs/memories/ in the repository"
  retrieval: "Catalog FTS5 with bm25 and the Engram index give word hits; a local int8 all-MiniLM-L6-v2 gives cosines; the two are fused as 1/(10+rank) + 2 x cosine with a 0.15 cosine floor. File paths and code symbols in the query narrow the pool, pins sort first, identical content is returned once"
  write: "An agent's memory_save or the CLI, synchronous under one file lock. The id is a hash of origin, project, kind and title, so a save with the same title revises that lesson; replaces retires a named predecessor in the same transaction. A task save attaches the task's passing check commands"
  update_delete: "Revision-checked update in place; retire with a reason and restore, by person or agent; automatic retirement when every file is gone or its files changed more than 90 days ago without a re-check. No verb deletes a lesson"
  scoping: "A project column applied in every query and re-checked per hit, plus a reserved personal project that is searched everywhere and never exported"
  integration: "Four MCP tools and matching CLI verbs; a lesson block of at most 3 KiB at session start and after compaction for six agent hosts; lessons attached to task steps; an App settings page"
  background: "None scheduled. Source freshness is computed from one bounded Git read per HEAD when lessons are listed or searched, and that read is what retires stale lessons"
  trust: "Active or retired as a stored state that filters; freshness against Git as a computed label; evidence of passing checks as a stored field no read consults; every lesson reaches the model inside a fenced block marked untrusted"
  strengths: "Lessons are tied to files and re-checked against commits; optimistic revisions; replacement and retirement in one transaction; a privacy filter decides what may be exported; index failure falls back to the catalog; hard caps on every store"
  risks: "All tests are encrypted in the public tree, so no behaviour here is shown tested; an agent can restore what a person retired; a restored lesson is never auto-retired again; a retired title blocks a save only under the same kind and wording; the evidence field gates nothing"
---

## 1. Executive Summary

QualityLayer is a commercial, source-available desktop and command-line product
that runs coding agents through a plan, implement and verify workflow. Its
memory keeps *lessons* about a repository — decisions, fixes, constraints,
terms — and about the person, in one local SQLite catalog. Agents search, read,
save and maintain them through four tools, and receive pinned and matching
lessons when a session starts and after compaction.

What is notable is that a lesson is tied to files and checked against Git. Each
lesson records the commit it was last read against. When later commits touch
its files the lesson is labelled as changed, an agent finishing a task is
handed those lessons to confirm, rewrite or retire, and a lesson left unchecked
for 90 days retires itself with the reason written down. Retired lessons are
kept, excluded from every agent read, and restorable.

What is weak, from the outside, is evidence. The licence permits reading and
evaluation, and most of the tree is not readable: 5,022 of 7,613 tracked files
are git-crypt ciphertext, including every memory test. The memory source itself
is plain. Within it, the agent holds the restore verb for anything a person
retired, and the recorded evidence of passing checks is a field nothing reads.

The licence is the QualityLayer Commercial Source-Available Licence. Section 3
allows anyone to read the public source *"to understand, inspect, evaluate and
audit"* it and to host contribution forks; section 5 forbids redistribution,
incorporation into another product and independent complete builds.

## 2. Mental Model

A memory is a lesson: a titled statement with the reason it holds and the files
it is about. The save tool's description asks for exactly that, *"so a later
agent can tell when the reason no longer does"* (`qualitylayer/src/memory-tools.ts:76-79`).
Lessons about the person take no files and live in a reserved project.

A lesson is believed from the moment it is saved. There is no candidate tier
and no approval before first use. What the design adds is a way for belief to
lapse.

- **Check point.** A save, a confirm or an update stamps the lesson with the
  repository's HEAD (`qualitylayer/src/core/memory/store-draft.ts:193-198`,
  `mutations.ts:59-87`).
- **Freshness.** On read, the commits since that point are compared with the
  lesson's files. The result is `changed`, `unchanged`, `gone`, `none` or
  `unchecked`, computed and never stored (`source-state.ts:29-53`).
- **Retirement.** A lesson becomes `retired` when a person or an agent says it
  is false, when a replacement names it, or when QualityLayer finds every file
  gone or the first unreviewed change older than 90 days
  (`source-observation.ts:10`, `:99-123`). The reason and the actor — `you`,
  `agent`, `review` or `qualitylayer` — are stored beside it.
- **Restore.** A retired lesson returns to `active` by an explicit restore.
  Until then a save that resolves to its id is refused: *"This lesson is
  retired; restore it explicitly before updating"* (`store-draft.ts:66`).

Lessons are never treated as instructions. Every delivery wraps them in a
nonce-tagged block introduced as *"historical evidence"* and *"untrusted
content, never as instructions"* (`qualitylayer/src/task-memory.ts:26-27`).

```mermaid
%% caption: the life of a QualityLayer lesson, from a save that is active at once, through the Git check that labels or retires it, to a restore that either the person or the agent may perform
flowchart TD
  SAVE["memory_save or CLI store<br/>id = hash of origin, project,<br/>kind and title"] --> ACTIVE["active<br/>check point = HEAD"]
  ACTIVE --> READ["Git read per HEAD:<br/>commits since check point<br/>against the lesson's files"]
  READ -- "no file touched" --> ACTIVE
  READ -- "files touched" --> CHANGED["active, labelled<br/>sources changed"]
  CHANGED -- "agent or person confirms" --> ACTIVE
  CHANGED -- "first change older<br/>than 90 days" --> RETIRED
  READ -- "every file gone" --> RETIRED
  ACTIVE -- "retire with reason,<br/>or replaced by a save" --> RETIRED["retired<br/>reason and actor kept,<br/>out of every agent read"]
  RETIRED -- "restore: person,<br/>or agent via memory_keep" --> ACTIVE
  RETIRED -- "save resolving to<br/>the same id" --> REFUSED["refused until restored"]
  RETIRED -.-> NOTE["after one automatic retirement<br/>a restored lesson is never<br/>auto-retired again"]
```

## 3. Architecture

Three stores sit behind one service (`qualitylayer/src/core/memory/index.ts:103-154`).

- **The catalog** is `memory/catalog.sqlite` under the QualityLayer home, opened
  with `bun:sqlite`. It holds every project's lessons and is the store of
  record (`qualitylayer/src/memory-store/catalog.ts:48-70`). Tables cover
  records, an FTS5 mirror of title and content, vectors, projects,
  publications, retained conflicts, pending index work and a key-value
  `metadata` table that carries check points, retirement reasons and pins'
  retry markers.
- **The index** is a build of [Engram](../engram/) at upstream commit
  `ec2bf0482139360bf61a8eadb76380ffe762de44`, shipped as a compressed binary
  per platform. A 60-line Go shim exposes seven of Engram's MCP tools over
  stdio, applies a page-count cap through a connection hook, and refuses any
  command-line argument (`qualitylayer/src/memory-engine/shim.go.txt`,
  `qualification.json`). Each project gets its own data directory named by a
  hash of the project id, with an `identity.db` mapping lesson ids to
  observation numbers. The index is disposable: a failed call marks the
  project and search continues on the catalog.
- **The vectors** come from all-MiniLM-L6-v2, int8-quantized, run on ONNX
  Runtime WebAssembly in a worker (`qualitylayer/src/memory-embed/index.ts`).
  No lesson leaves the machine to be embedded.

A fourth, optional surface is the repository. With sharing turned on for a
project, export writes eligible lessons as JSON under `docs/memories/` with a
readable `LESSONS.md`; the person commits them.

The engine payloads and the embedding model are among the encrypted files at
this commit, so the shim's source and the pin are readable and the binaries
are not.

### Deployment and ergonomics

Nothing runs as a service; the product's own process opens the catalog and
spawns the index on demand. Use requires a trial or subscription and a licence
check, with an offline allowance of seven days. Memory needs no API key. Every
store has a byte cap — 128 MiB for the catalog, 64 MiB per project index, 256
MiB for all indexes, 32 KiB per record, 20,000 records
(`qualitylayer/src/core/home-caps.ts:89-91`, `core/memory/limits.ts:1-3`). The
catalog is one SQLite file and is repairable with ordinary tools; the public
checkout cannot build the application, which the licence states in section 4.

## 4. Essential Implementation Paths

- **Write.** `runMemoryTool` → `MemoryWriter.store` → `MemoryDraft`
  (`memory-tools.ts:345-380`, `core/memory/store.ts:53-84`,
  `store-draft.ts:34-199`). State changes in `db.save` inside `db.atomic`,
  with the replaced lesson retired in the same transaction.
- **Evidence.** `MemoryWriter.evidence` loads the task, requires stage
  `verify` or `shipped` and all checks passed, and records up to 100 passing
  commands and HEAD (`store.ts:17-52`).
- **Lifecycle.** `saveLifecycle` (`lifecycle.ts:13-59`), called by
  `MemoryMutations.retire`, the replacement path and the source observation.
- **Search.** `MemorySearch.search` → `MemoryCandidates.collect` →
  `searchResults` → `fuseRanks` (`search/index.ts:24-48`,
  `search/candidates.ts:14-63`, `search/results.ts:8-72`, `ranking.ts:127-143`).
- **Freshness and auto-retirement.** `MemorySourceCatalog.sources` →
  `MemorySourceObservation.read` → `settle` → `retire`
  (`source-catalog.ts:24-38`, `source-observation.ts:64-123`).
- **Session delivery.** `qualitylayer/src/memory-session.ts`: up to five pinned
  and five matched lessons in 3 KiB, with a two-second lookup budget (`:23-27`).
- **Task delivery and upkeep.** `withTaskMemory` and `lessonsToKeep`
  (`task-memory.ts:115-143`, `:224-361`).
- **Exchange.** `restoreRecords` and `restoreOne` (`restore.ts:19-125`),
  `reconcileRecord` (`reconcile.ts:9-54`), the privacy filter
  (`privacy.ts:2-34`).
- **Tools and CLI.** `MEMORY_TOOLS` (`memory-tools.ts:45-111`),
  `cli/commands/memory.ts:24-25` for the verb list.

## 5. Memory Data Model

`MemoryRecord` is the unit (`qualitylayer/src/memory-contracts.ts:31-58`). It
carries `id`, `project`, `origin`, `revision`, `kind`, `title`, `content`,
`tags`, `files`, `source`, optional `sourceId` and `author`, `evidence`,
`visibility`, `state`, two timestamps, and four history fields: `ancestry`,
`provenance`, `replaces` and `retirement`.

Identity is derived. A new lesson's id is the hash of the catalog's origin,
the project, the kind and the trimmed title, or of the task and a key for task
captures (`store-draft.ts:43-49`). A second save under the same kind and title
is therefore a revision of the first, and an update by id must name the
revision it read (`:60-65`).

`source` is `task`, `session`, `pilot`, `repository` or `manual`. `provenance`
records where a lesson restored from the repository originally came from.
`ancestry` is a list of up to 256 content digests of accepted ancestors, which
lets two machines tell an older copy from a divergent one.

Several facts are deliberately kept outside the record, in `metadata`, so they
never travel through Git: the check point, the retirement reason and actor,
the pin (`core/memory/local-facts.ts:4-24`). Session attribution is likewise
stripped from exported files.

Time is a creation stamp, an update stamp and the check point's commit and
time. There is no validity interval; a corrected lesson is either the same row
at a higher revision or a new row whose `replaces` names the old one.

Scope is the project id, plus the reserved `personal` project. Visibility is
`private` or `project`: a lesson is `project` only if it passes the privacy
filter, which rejects credential shapes, home paths, e-mail addresses, the
`preference` kind and anything resembling a prompt or transcript
(`privacy.ts:2-34`). A lesson that fails stays local and usable.

## 6. Retrieval Mechanics

A search needs a project and a text of at most 500 characters. Word hits come
from two places: the Engram index, skipped while any of the project's lessons
await indexing, and the catalog's FTS5 table ordered by `bm25(search,0,4,1)`,
which weights the title four times the content (`search/candidates.ts:20-43`,
`catalog.ts:457-469`). Meaning hits are cosines against every active vector of
the project; up to 64 missing vectors are computed during the search itself.

Fusion is `1/(10 + rank) + 2 x cosine`, with cosines under 0.15 contributing
nothing (`ranking.ts:13`, `:115-143`). The comment beside the floor gives its
calibration: twelve paraphrases scoring 0.158 to 0.435 against their lesson
and six unrelated queries at most 0.113. A query matching neither way returns
no lesson.

Three narrowing rules follow. A query of five to twenty content words is
treated as a keyword list and a hit must carry half of them. File paths in the
query put lessons on those files first and admit others only at a cosine of
0.55 or more. Code symbols must appear in the lesson (`search/results.ts:8-34`).
Pinned lessons sort first, a retired or foreign id is dropped, and identical
content is returned once (`:36-72`).

Delivery is both automatic and tool-mediated. A session's first message and
each compaction trigger a block of at most five pinned and five matched
lessons in 3 KiB. Each tool hit carries its scope, saved and checked dates and
freshness, and the search tool's description tells the agent to read a hit in
full and check it against current code. Two of every page's slots are held for
lessons about the person (`ranking.ts:146-162`).

The failure mode the design accepts is a missed delivery: the documentation
says a slow or disabled hook skips the block, and the agent is expected to
search.

## 7. Write Mechanics

Writes are explicit. An agent calls `memory_save`, a task's verify step
captures the lessons it decided to keep, or a person uses the CLI or the App.
No extractor reads transcripts.

A save validates its input, takes the mutation lock, verifies the project's
registration, builds the record and compares it with the stored one; an
unchanged save returns the old record without a new revision
(`store.ts:53-84`). A changed save writes the record and its publication copy
and retires any lesson named in `replaces`, in one transaction. Indexing and
embedding follow, outside the transaction; an index failure is recorded and
does not fail the save.

After a save without `replaces`, the tool searches for the new title and
returns up to three similar lessons, so the agent can merge
(`memory-tools.ts:384-389`). Deduplication is otherwise the id rule and the
agent's judgement.

Upkeep is assigned to the agent. At a task's review stage the reply lists up
to eight active lessons on files the task's diff touched, changed ones first,
with the instruction that the agent *"keep the project's lessons true; the
person does not maintain them"* (`task-memory.ts:103-143`). Review subagents
are read-only: with `QUALITYLAYER_REVIEW_READ_ONLY=1` the save and keep tools
refuse (`memory-tools.ts:214-218`).

Exchange through Git never happens by itself. Export writes files; import is
an explicit command; neither commits, pushes or pulls. An imported lesson that
diverges from the local one is stored in `conflicts` and the local version
stays in use until `memory reconcile` names the winner, which becomes a new
revision carrying both ancestries (`restore.ts:49-53`, `reconcile.ts:9-54`).

### Operational cost

A save blocks on a lock, a SQLite transaction, one index call with a
five-second default timeout and one local embedding. A lesson is searchable by
words as soon as the transaction commits. No pass rewrites the store. The
freshness read is one bounded Git log per HEAD, cached in `metadata` under a
key that includes HEAD and the lessons' revisions. Session delivery is capped
at 3 KiB and two seconds and arrives with the first message.

## 8. Agent Integration

The tools are `memory_search`, `memory_read`, `memory_save` and `memory_keep`,
served by `qualitylayer memory mcp` and by native plugins for OpenCode and Pi
(`memory-tools.ts:45-111`). The CLI carries the same verbs and more: pin,
pause, sessions, share, export, import, conflicts, reconcile and a Pilot Shell
importer. The project's skills tell agents without native tools to use the CLI
for search, read, store, confirm, retire and restore.

The agent's authority is broad. It can save, revise, replace, retire and
restore any lesson of the current project and of the person, and confirm any
repository lesson at HEAD. It cannot reach another project's lessons by id,
and it has no tool for sharing, import or reconcile.

The App's server exposes list, search, read, pin, confirm, retire, restore and
the Pilot import (`qualitylayer/src/server/memory.ts:421-482`). The
documentation describes App controls for restoring from the repository and
choosing between conflicting versions; at this commit the readable server has
no route for either, and both exist as CLI verbs
(`cli/commands/memory.ts:275-281`).

## 9. Reliability, Safety, and Trust

**The lifecycle state filters.** `filter` begins every agent query with
`state='active'`, the vector read joins on it, and `currentRecord` rechecks
each ranked id (`catalog.ts:716-717`, `:334-340`, `search/results.ts:36-40`).
Management searches opt in to retired lessons so they can be found and
restored. This is the `trust_state` mark: two stored values, one of which
withholds.

**Freshness is a label with one automatic consequence.** `changed` never
removes a lesson from a result; it appends *" · sources changed"* to its line
and puts it first in the review hand-off. Its only enforced effect is the
90-day retirement.

**That retirement fires once per lesson.** The observation sets
`auto-retired:<id>` before retiring and returns early whenever the marker is
present, so that *"a restore's local marker wins over an older Git
observation"* (`source-observation.ts:104-114`). Nothing clears the marker. A
lesson restored after an automatic retirement keeps its label and is never
retired by QualityLayer again, however long its files go on changing or even
if they are deleted.

**A retired lesson blocks its own title, not its content.** Because the id
includes kind and title, saving the same statement under a reworded title or
another kind creates a new active lesson. The refusal at `store-draft.ts:66`
is keyed on the record, and the restore verb is on the agent's own tool, so
this is not a tombstone.

**Evidence is recorded and unread.** A task lesson carries the commit and the
passing check commands only when the task reached verify with all checks
passed; otherwise `evidence` is null and the lesson is saved all the same
(`store.ts:17-52`, `:62`). Outside `src/ui`, the readable source reads
the field in the migration timestamp and the privacy text only.

**No review gate on admission.** The one place a lesson waits is a retained
conflict from an import. Its resolver is a CLI verb with no check on who runs
it, in the binary agents are told to use for six other memory verbs, and it
covers foreign revisions only. `human_review` is withheld.

**No append-only mutation record.** Revisions overwrite the row; `ancestry`
keeps digests, not content; a task's memory file lists at most 20 used and
saved ids and 10 revised, retired and confirmed per step. Exported lessons
keep prior versions as files under a `history/` folder in the repository,
which is Git's record. `audit_log` is withheld.

**Concurrency and failure.** One file lock serialises mutations across
processes, updates carry an expected revision, and the source observation
discards its result if any lesson changed while Git was being read
(`runtime.ts:60-63`, `source-observation.ts:84-97`). The index is treated as
lossy throughout.

**Injection.** Lessons are fenced and labelled untrusted at every delivery,
and titles handed to the review step are capped at 200 characters. Imported
repository lessons pass the same privacy filter as exported ones and are
tagged `repository`; nothing ranks or filters on that tag.

Validity time and committed negative retrieval cases are not found in the
readable tree; the tests that might hold the latter cannot be read.

## 10. Tests, Evals, and Benchmarks

I ran nothing, and the tests cannot be read. `.gitattributes` sends
`qualitylayer/**` through a git-crypt filter and re-opens a named list of
source files. Of the 2,415 files under `qualitylayer/tests/`, 2,411 are
ciphertext at this commit, among them all 75 whose path names memory: 26 files
under `tests/core`, 26 under `tests/memory-e2e`, the CLI, end-to-end, server
and frontend memory tests, and the fixtures `ranking-set.json` and `search-relevance.json` that the ranking
comment cites. The four readable tests cover the licensing client and the
workflow asset bundle.

So the file names show that a memory suite exists — `memory-retirement-race`,
`memory-portable-boundaries`, `memory-search-relevance`, `retention-memory` —
and nothing about what it asserts. The calibration numbers in `ranking.ts`
are the code's own comment, not a result that can be recomputed here. The
workflow files under `.github/private-workflows/` are ciphertext as well.

No paper accompanies the project and no benchmark is claimed in the README.

## 11. For Your Own Build

### Steal

- **Tie a memory to the files it is about, and store the commit it was last
  checked at.** Staleness then becomes a Git query instead of a clock, and
  "still true" becomes an action with a commit attached.
- **Hand the stale ones to the agent at the moment it has the diff open.** The
  review step lists lessons on the files the task changed, so the check
  happens when the evidence is in context.
- **Keep local facts out of the portable record.** Check points, retirement
  reasons, pins and session attribution live beside the lesson, so sharing a
  lesson cannot leak who said what on which machine.
- **Derive visibility from a filter, not a flag.** A lesson that looks like a
  credential, a home path or a transcript stays local without anyone deciding.
- **Treat the search index as disposable.** A canonical catalog with a pending
  table and a per-project failure mark lets the index break without losing a
  save or a search.

### Avoid

- **A one-way latch on an automatic rule.** A marker that stops a second
  auto-retirement also stops every later one.
- **An identity that includes the wording.** Blocking a retired title leaves
  the retired claim free to return under another.
- **A proof field with no reader.** Recorded passing checks that neither rank
  nor filter are provenance for a person, and a save without them looks the
  same to an agent.
- **A documented control without a route.** Restore and reconcile are
  described for the App and served only by the CLI at this commit.

### Fit

This is memory for one developer's repositories on one machine, maintained by
the agents that use it, inside a paid product. The design suits a codebase
that changes often enough for file-level staleness to mean something, and a
person who wants lessons kept true without reviewing each one. It does not
suit a team that needs an approval before a lesson is believed, an audit of
who changed what, or a deletion that removes a lesson. The licence rules out
reuse of the code; the mechanisms above are what can be taken.

## 12. Open Questions

- What do the 75 encrypted memory tests assert, and do any pin that a retired
  or foreign lesson stays out of a result?
- Is the missing clear of `auto-retired:<id>` intended as permanent immunity
  after a restore?
- Which App build serves restore-from-repository and conflict choice, given
  that the readable server has neither route?
- How often does the two-second session lookup time out on a large catalog?
- Does the bundled index ever return an id the catalog has retired, and is
  `currentRecord` the only guard?

## Appendix: File Index

Paths are under `qualitylayer/src/`.

- **Contracts and schema:** `memory-contracts.ts`, `memory-store/catalog.ts`,
  `core/memory/limits.ts`, `core/home-caps.ts`.
- **Write path:** `core/memory/store.ts`, `store-draft.ts`, `lifecycle.ts`,
  `mutations.ts`, `record-validation.ts`, `privacy.ts`.
- **Retrieval:** `core/memory/search/` (`index.ts`, `query.ts`,
  `candidates.ts`, `results.ts`), `core/memory/ranking.ts`.
- **Freshness:** `core/memory/source-catalog.ts`, `source-observation.ts`,
  `source-state.ts`, `sources.ts`, `changed-lessons.ts`.
- **Exchange:** `core/memory/portability.ts`, `restore.ts`, `reconcile.ts`,
  `export-batch.ts`, `history-storage.ts`, `portable.ts`.
- **Index and vectors:** `memory-engine/index.ts`, `memory-engine/shim.go.txt`,
  `memory-engine/qualification.json`, `memory-embed/index.ts`,
  `core/memory/runtime.ts`.
- **Agent surface:** `memory-tools.ts`, `memory-session.ts`, `task-memory.ts`,
  `cli/commands/memory.ts`, `cli/commands/memory-mcp.ts`, `server/memory.ts`,
  `skills/`.
- **Documentation:** `docs/docusaurus/docs/memory.mdx`, `LICENSE`.

### Recorded searches

Run with `/usr/bin/git grep` from the root of a checkout at
`8635ab90a2d13084be33bddfaa74afa5d4d43e49`, without a git-crypt key.

- A script reading the first ten bytes of every tracked file for the git-crypt header — 5,022 encrypted, 2,591 plain; 2,411 encrypted under `qualitylayer/tests/`, 75 of them with `memory` in the path; no encrypted file under `qualitylayer/src/` except the engine payloads, their scan streams and the embedding assets.
- `git grep -n -E 'auto-retired' -- qualitylayer/src` — `source-observation.ts:105` and `:114` only; the marker is read and set, never cleared.
- `git grep -n -i 'DELETE FROM' -- qualitylayer/src/memory-store qualitylayer/src/core/memory` — eight statements over projects, metadata, search, vectors, index_pending, index_issues, exchange and conflicts; none over `records`.
- `git grep -n -E '\.evidence' -- qualitylayer/src ':!qualitylayer/src/ui'` — in memory code, `core/memory/migrate.ts:32` and `core/memory/privacy.ts:21`; the other hits are task attestations and code-quality records.
- `git grep -n -E '\.reconcile\(|reconcileRecord\(' -- qualitylayer/src` — `cli/commands/memory.ts:281`, `core/memory/portability.ts:58` and the definition; no server route.
- `git grep -n -E '\.restoreProject\(|restoreRecords\(' -- qualitylayer/src` — `cli/commands/memory.ts:275`, `core/memory/portability.ts:33` and the definition.
- `git grep -n -i -E 'reconcile|memory conflicts|memory import' -- qualitylayer/src/skills qualitylayer/src/workflow qualitylayer/src/task-memory.ts qualitylayer/src/memory-session.ts` — no match; no prompt tells an agent to import or reconcile.
- `git grep -h -o -E 'qualitylayer memory [a-z-]+' -- qualitylayer/src/skills qualitylayer/src/workflow` — confirm, read, restore, retire, search and store.
- `git grep -n -i -E 'conflict|restore|exchange|import' -- qualitylayer/src/server/memory.ts` — imports, a comment about restoring retired lessons, and the Pilot import route at `:463-482`; no exchange, repository restore or conflict route.
- `git grep -n -i -E 'arxiv|bibtex|CITATION\.cff' -- README.md docs/docusaurus/docs` — no match.

## History

**2026-11-13** — [`8635ab90a2d13084be33bddfaa74afa5d4d43e49`](https://github.com/maxritter/qualitylayer/commit/8635ab90a2d13084be33bddfaa74afa5d4d43e49) — first reading, at the head of `main`, dated 13 November 2026. Marks: `trust_state` on the active/retired column, `scope_enforced` on the project predicate. LICENSE read in full: reading, evaluation and contribution forks permitted, no rider against analysis. Screened before reading: one auto-run surface, a `.gitattributes` naming 65 git-crypt filter drivers, none configured on this machine, so encrypted files were checked out as ciphertext; eight dependency surfaces inside the seven-day cooldown, one build-time execution point, two unpinned manifests. Nothing was installed or run. The bundled Engram build was not opened; its shim source and upstream pin were read.

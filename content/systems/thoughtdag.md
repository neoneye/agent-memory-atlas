---
title: "ThoughtDAG"
eyebrow: "Wires are the context"
description: "An editable thought graph on an infinite canvas — desktop app, DeepSeek Harness plugin and a read-only CLI — where what a model sees next is exactly what wires into the node, every generation records a fingerprint of its upstream and a SHA-256 of the request it sent, a stale answer is marked and replayable in dependency order, an ambient memory of three categories is admitted by a judge behind a constitution in code with an undo, and a committed benchmark shows that deleting a wrong turn's source does not always delete the wrong answer."
root: ../..
page_kind: system
source_name: "chenxiachan/thoughtdag"
source_url: https://github.com/chenxiachan/thoughtdag
revision: e658c280d39082ec7d6d328bd1dff9af6d49b94e
revision_url: https://github.com/chenxiachan/thoughtdag/commit/e658c280d39082ec7d6d328bd1dff9af6d49b94e
analyzed_at: 2026-09-06
capabilities: "audit_log, human_review, negative_eval"
capability_evidence:
  audit_log: "the canvas event log | src/store/slices/events.ts:1-27, src/types.ts:233-251, src/store/streaming.ts:280-285, src/store/slices/nodes.ts:27-454, src/store/slices/llm.ts:20-619, src/lib/adapters/thoughtdag-canvas.ts:209-222 | an append-only list of semantic operations — ask, generate, edit-question, edit-response, regenerate, delete, archive, unarchive, highlight, connect, disconnect, merge, weave, explore, fanout, material-add, undo, redo and commit — each with a timestamp, the object id and metadata only, never text; undo rolls the graph back and is itself an event; `commit` records at dispatch the SHA-256 of the canonical request, its message count, images, lane and model; the log persists with the canvas and in every backup, exports as CSV, and is projected into canonical `context.committed` events; a cap of 10,000 drops the oldest 1,000 past it, and ambient-memory admissions announce themselves with a toast and write no event | cli/test/canvas.test.mjs:49-130 (a backup's commit events round-trip through the canvas adapter with their hash and bundle id), cli/test/events.test.mjs"
  human_review: "the canvas, the will-send preview and the memory manager | src/store/context-builder.ts:74-221, src/store/slices/nodes.ts:391, src/lib/memory.ts:125-165, docs/guides/context-control.md, docs/guides/models-tools.md | a person decides what a model sees by wiring, disconnecting, archiving, editing an answer, choosing a version and replaying; the panel's preview is built by the same `buildContext` the request uses, so what is shown is what is sent; every ambient-memory admission shows a toast with Undo and the manager edits, imports, exports, disables or deletes entries; no autonomous process redraws the graph | scripts/smoke.mjs (persistence round-trip), the benchmark's `equivalence.mjs` (the preview's compiler is the request's compiler)"
  negative_eval: "the why layer and the benchmark compiler | cli/test/why.test.mjs:131-145, benchmark/tools/equivalence.mjs, benchmark/runs/compiled/rp-pilot-bakery-trays-k1.{polluted,source_prune,subgraph_prune}.compile.json | `why <path>` must not return read-only turns by default and must return them with `--include-read`, with the count of hidden reads reported — a populated index, the excluded material present, a positive control in the same case; the equivalence suite compiles every benchmark condition through the product's `buildContext` and asserts its node order equals an independent reference compiler's for every case, including the pruned conditions whose compiled artifacts show the deleted turn absent (seven messages polluted, five after source prune, three after subgraph prune) and a cyclic graph refused | cli/test/why.test.mjs:114 (facts hold no interpretation and no full answers), :123 (a stray file does not enter the index)"
stack_storage: "files"
stack_retrieval: "graph, lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "A node on a canvas — a question, answer versions with the model, time and context hash of each, highlights, attachments with page provenance, a role, an archived flag, an import source and a frozen source snapshot — joined by wires that are the context; beside it an ambient memory entry of one sentence in a category, with a kind, a project and a date; and, in the why layer, a fact index of observed events from other agents' session files"
  storage: "IndexedDB per canvas (idb-keyval) with a one-minute debounced `.thoughtdag.json` folder backup; `localStorage` for the memory library and switches; `~/.thoughtdag/` for the why layer's fact index, interpretation cache and verbatim text index; the source agents' session files are read and never written"
  retrieval: "For a generation, a deterministic walk of the graph — materials, dashed reference blocks, the solid chain in order, the question last — with archived nodes skipped and stale answers marked; for the why layer, exact phrase and path lookup over the index with reads hidden by default; no vectors anywhere"
  write: "A person asks, edits, wires and imports; a model's answer lands as a version on its node; a background judge proposes at most three ambient memories per canvas per session under a constitution in code; Session Atlas mirrors other agents' turns idempotently past a ledger; the DeepSeek Harness bridge can fork a session, inject context and queue a prompt into the harness"
  update_delete: "Answers are versioned and never overwritten; a node can be archived — kept, dimmed and excluded from every context walk — or deleted; a wire can be removed or converted; an upstream change marks dependants stale and replay regenerates them in dependency order; an ambient memory can be undone at the toast, edited or deleted in the manager, and project entries stop flowing after 45 days"
  scoping: "One canvas per IndexedDB key and reachability by wire as the only filter inside it; ambient memory is global to the install, labelled with the canvas it came from and not filtered by it; the why index is one per machine over every runner's sessions"
  integration: "A React canvas in the browser, an Electron desktop app with fenced session roots, an Express proxy for any OpenAI-compatible, Anthropic, Google, DeepSeek or Zhipu endpoint plus MCP tools, a Cloudflare Pages demo with no server state, a `dsh-thoughtdag` plugin mounting the canvas inside DeepSeek Harness, and a CLI exposing `why_check`, `why_file`, `find` and `recall_turn` over MCP"
  background: "A file watcher appends new turns of a subscribed session to its mirror; the why index refreshes when a source file's size or mtime moved; the memory judge runs fire-and-forget after ordinary generations; nothing consolidates or rewrites the graph on its own"
  trust: "A stale mark on any answer whose upstream fingerprint drifted, prepended to its text in downstream context rather than withholding it; a `basis` of observed, reconstructed or inferred and a `completeness` on every why-layer event, displayed and never filtered; an identity memory admitted only when the user stated it; a credential pattern that blocks a memory in code"
  strengths: "The preview and the request share one compiler; a request hash written at dispatch; a benchmark whose conditions are graph operations, whose traces are immutable and whose scorer can re-score without an API call, and whose status file records its own corrections; source sessions that are read and never rewritten"
  risks: "Stale is a label the model is asked to respect, not an exclusion; archive is exclusion without a record, so a pruned claim can be re-wired or re-imported; the event log rotates past 10,000 and does not see memory admissions; ambient memory is global across canvases with a project label nobody filters on; the harness bridge writes into live sessions; 620 commits in nine weeks by one author"
---

## 1. Executive Summary

ThoughtDAG is **a context graph a person edits**: an infinite canvas where
each node is a question and its answer versions, each wire is context, and
*"what the model sees is exactly what wires into the node."* MIT; 620
commits between 3 July and 6 September 2026, 618 of them by one author;
30,541 lines of TypeScript in `src/`, a 1,154-line Express proxy, an
Electron shell, a 1,226-line CLI, a 1,023-line DeepSeek Harness plugin and
a benchmark directory of 2,145 files. It ships as a desktop app at 0.4.6,
a harness plugin at the same version, an npm CLI at 0.1.2 and a browser
demo on Cloudflare Pages that stores nothing. The screen found no
auto-run surface; five manifests were inside the seven-day cooldown and
nothing was installed or run.

Four things here are memory in the atlas's sense, and they are wired
together. The canvas persists — one IndexedDB key per canvas with a
debounced folder backup as a real `.thoughtdag.json` file — and a
generation's input is a deterministic walk of the graph
(`store/context-builder.ts:74-221`): materials first, dashed reference
blocks, then the solid chain in order, the question last, archived nodes
skipped at every layer. Each generation records the fingerprint of
everything upstream of the node with the node's own content blanked
(`upstreamFingerprint`, `:111-130`), and `recomputeStaleness`
(`slices/nodes.ts:251-260`) marks a node **stale** when the live
fingerprint drifts from the recorded one; a stale answer still enters
downstream context, prefixed *"[Stale: this answer was written against an
earlier version of its upstream]"* (`:132,:200`), and *Replay*
regenerates stale nodes in dependency order. Second, an **ambient
memory** (`lib/memory.ts`): after an ordinary generation a background
judge on the cheapest model proposes one sentence in one of three
categories — preference, identity, project — and a constitution written
in code, not in the prompt, decides admission: identity only when the
user *stated* it, never inferred; a credential pattern blocks; three
additions per canvas per session; duplicates and unknown update targets
refused (`admissionCheck`, `:100-118`); every write shows a toast with
**Undo**, and project entries stop flowing into context after 45 days
without being deleted. Third, **Session Atlas**: the desktop shell fences
the session directories of Claude Code, Codex, DeepSeek Harness and Pi
(`desktop/main.js:116-124`), reads them and never writes them, and mirrors
a session onto a canvas turn by turn with tool calls as attachments,
appending idempotently past a per-session ledger as the source grows.
Fourth, the **why layer**: a CLI that reduces those same session files to
an event index of what each turn did to which files, papers and URLs,
answers `why <path>`, `find "<phrase>"` and `recall`, and serves the
four questions read-only over MCP.

**What it records is unusual: not what the model concluded, but what it
was shown.** At dispatch the streaming slice writes a `commit` event
carrying the SHA-256 of the canonical request — messages, image digests,
model, tool flags — its message count and lane (`store/streaming.ts:280-285`);
the canvas event log (`slices/events.ts`) is append-only, metadata-only,
survives undo, persists with the canvas and exports as CSV; and the
canvas adapter projects those commits into canonical `context.committed`
events with the manifest's own honesty about what it can see
(`events/manifests.ts`: turns exact, wires exact, context surface exact
from the day commits were logged and upstream-only before). The benchmark
under `benchmark/` is the same discipline applied to a claim: nine
endpoints, 1,215 captured conditions, conditions defined as graph
operations, traces immutable, a scorer that re-scores from traces with no
API call, and a `STATUS.md` that records a design flaw a reader caught, a
withdrawn generalisation and a corrected statistic.

Three marks: `audit_log` for the event log, `human_review` for the canvas
itself, `negative_eval` for the why layer's hidden-reads case and the
benchmark's compiler equivalence. `tombstone`, `trust_state`, `bitemporal`
and `scope_enforced` withheld, each a near miss stated in section 9. No
paper; the repository cites itself as software and publishes the
benchmark as a web report.

## 2. Mental Model

A belief here is a node the graph can reach. It enters three ways: a
person asks and a model answers on the canvas; a person imports material
— a PDF passage with its page, a link snapshot with its fetch time, a
note; or the atlas mirrors a turn another agent held, frozen as a
`source` snapshot beside the editable copy. It is *used* when a wire
leads from it to the node being asked: solid for the full turn, dashed
for a quoted reference, and the walk is the same whether a person is
previewing the request or the model is receiving it. Its answer is
believed exactly as written until its upstream changes, at which point it
is stale — still present, labelled as written against an older input —
until a person replays it or decides the difference does not matter.

It stops being used by exclusion, not erasure. Delete the wire and the
node stays on the canvas, reconnectable; archive the node and it is
dimmed and skipped by every walk; delete it and it is gone, with an event
in the log and no other record. An answer is never overwritten — a
regeneration is a new version beside the old, each carrying the model
that wrote it, the time and the hash of what it saw — and a merge or a
condensation is a new node, not a replacement. The ambient memory is the
one layer with a judge: a sentence the judge proposes lands only if the
constitution admits it, announces itself, and can be undone for eight
seconds at the toast or edited and deleted in the manager afterwards;
what it holds rides the system layer of every ordinary generation,
*"never recite them, never treat them as part of the conversation."*

```mermaid
%% caption: a person's wires are the retrieval; the same compiler feeds the preview and the request; each generation records what it depended on and what it sent; stale is a mark that stays in context, archive is an exclusion without a record, and the ambient memory has a judge and an undo
flowchart TB
    P["person: ask · wire · disconnect · archive · edit · choose version"] --> G[("canvas graph<br/>IndexedDB per canvas · folder backup")]
    M["materials: PDF passage p.N · link snapshot · note"] --> G
    A["Session Atlas: Claude Code · Codex · DSH · Pi<br/>read-only session files → mirrored turns"] --> G
    G -->|"buildContext: materials → references → chain → question<br/>archived skipped · stale marked"| C["compiled request"]
    C --> V["will-send preview"]
    C -->|"commit: sha256(request) · n · model"| E[("event log<br/>append-only · metadata only · survives undo")]
    C --> LLM["model"]
    LLM -->|"answer version + lastContextHash + generatedAt"| G
    G -->|"upstream fingerprint drifted"| S["stale → replay in dependency order"]
    LLM -->|"background judge"| J{"constitution in code<br/>stated identity · no credentials · ≤3 per session"}
    J -->|"admit + toast with Undo"| AM[("ambient memory<br/>preference · identity · project (45-day decay)")]
    AM -->|"[Memory] block on the system layer"| C
    W["why layer: ~/.thoughtdag index<br/>why · find · recall · MCP"] -.->|"reads the same session files"| A
```

## 3. Architecture

`src/` is a React 19 and Vite application: `App.tsx` (2,084 lines), the
canvas components over `@xyflow/react`, a zustand store split into slices
(`nodes`, `llm`, `attachments`, `highlights`, `history`, `events`,
`evaluator`, `roles`) with `context-builder.ts`, `streaming.ts` and
`projects.ts` beside them, and `lib/` holding the mechanisms: `memory.ts`,
`context-bundle.ts`, `graph.ts`, `condense.ts`, `export.ts`,
`local-backup.ts`, `persistence.ts`, the `adapters/` for each runner's
session format, `atlas/` (discover, canonical routing, live mirror,
watermark, the harness bridge), and `events/` (the event contract, the
projection from adapter turns to canonical events, and per-adapter
manifests). `server.mjs` is the only backend: an Express proxy over the
Vercel AI SDK for Zhipu, OpenAI-compatible, OpenAI, Anthropic, Google and
DeepSeek endpoints, with web and scholarly search tools, MCP clients from
`mcp.config.json`, PDF extraction and URL fetch. `desktop/main.js` is the
Electron shell: fenced session roots under the home directory, a native
picker for custom roots, backup writes, protocol links. `cli/` is the why
layer; `dsh/` the harness plugin; `functions/` the Cloudflare twin of the
proxy with no environment and no storage; `protocol/` the Context Bundle
v0 proposal with schema and fixtures and the adapter documents for Claude
Code and Codex; `benchmark/` the cases, gold, suites, tools, compiled
artifacts, runs and canvases.

Persistence is object storage into IndexedDB with a one-second debounce
and a flush on page hide (`lib/persistence.ts`); the project list is a
separate key; attachments live in a vault. The folder backup writes the
active canvas about a minute after the last change and restores the
watched folder on the next launch. The ambient memory library and its
switch live in `localStorage` (`lib/ui-store.ts:231-246`). The why layer
keeps `fact-index.json`, `interpretation-cache.json` and a streamed
`text-index.jsonl` under `~/.thoughtdag/` with 0700 and 0600 permissions,
and refreshes when a source file's size or modification time moved
(`cli/src/lib.ts:16-22,:502-508`).

### Deployment and ergonomics

Nothing to run for the desktop app beyond the installer; from source,
`npm run server` and `npm run dev`, a `.env` with at least one key or a
provider connected inside the app, Ollama for a fully offline model. The
web demo runs browser-direct with the visitor's own keys and no server
state. The harness plugin mounts the canvas under the existing harness
web server with no second process. Everything a person made can leave as
JSON, Markdown, a thought-map image or a read-only share link; the
benchmark re-scores with `node tools/score.mjs` and needs a key only to
capture a new endpoint.

## 4. Essential Implementation Paths

- **Compile.** `partitionContext` (`lib/graph.ts`) splits a node's
  upstream into materials, references and the mainline;
  `buildContext` (`context-builder.ts:74-221`) walks them in that order,
  dedups attachments by fingerprint, honours excluded and included
  attachment ids, skips `archived` at every layer (`:161,:178,:192`),
  prepends the stale mark to a stale chain response (`:200`), resolves the
  role along the mainline, and returns messages with a parallel `sources`
  array naming the layer, node and part of every message. `hashContext`
  (`:93-100`) and `upstreamFingerprint` (`:111-130`) hash it.
- **Dispatch and record.** `streaming.ts:213` adds the ambient
  `[Memory]` block for ordinary nodes; `:280-285` computes the SHA-256
  of the canonical request and logs `commit`; on completion the response
  is appended as a version with `generatedBy`, `generatedAts` and
  `lastContextHash` (`:176-202`), `recomputeStaleness` runs, and `:359`
  fires `judgeMemory`.
- **Judge and admit.** `judgeMemory` (`memory.ts:125-165`) sends the
  exchange and up to forty existing entries to the default model with a
  versioned prompt, parses one JSON line, applies `admissionCheck`, then
  adds or updates the entry and shows the toast with Undo;
  `memoryContextBlock` (`:55-70`) renders active entries, filtering
  project entries older than 45 days.
- **Mirror.** `importOrAppendSession` (`atlas/canonical.ts:36-40`)
  routes a session file to a subscribed canvas, a mounted branch or a
  fresh canvas, appending only turns past the ledger; the live mirror
  (`atlas/live-mirror.ts`) watches the active canvas's source file; the
  watermark (`atlas/watermark.ts`) tracks what a person has seen.
- **Why.** `cli/src/lib.ts`: collectors per runner reduce session files
  to facts — turn, question head, and per path the op and the first
  differing line — plus a verbatim text index; `hitsFor` (`:630-646`)
  hides read-like ops unless `--include-read` or nothing else happened;
  `why --check` exits 0 or 1; `status` reports the evidence breakdown by
  basis; `purge` deletes the store.
- **Bridge.** `dsh/lib/index.js`: read-only listing and logs for disk and
  live harness sessions, turn boundaries, and three writes fenced to the
  local host — `fork`, `inject` (model-facing context for the next step)
  and `followup` (a queued or steering prompt) — plus the harness's own
  models and fetcher for the embedded canvas.
- **Bundle.** `compileContextBundle` (`lib/context-bundle.ts:170`) wraps
  `buildContext` with an injected clock, a semantic snapshot hash that
  ignores positions and collapse state, per-item provenance and a content
  hash; three fixtures freeze the expected output.
- **Backup and export.** `local-backup.ts` writes `.thoughtdag.json`;
  `export.ts` exports the canvas, a context chain or a selection as
  Markdown, the event log as CSV (`:242`), and imports backups and chat
  exports.

## 5. Memory Data Model

`ThoughtData` (`src/types.ts`) is the node: `question`, `response`,
`responses[]` with parallel `questions[]`, `generatedBy[]`,
`generatedAts[]`, `editedAts[]`, `gatewaySearches[]`, `summaries[]` and
`summaryTypes[]` (display only, never in fingerprints); `responseIndex`;
`archived` and `archivedAt`; `lastContextHash` and `lastGeneratedAt`;
`createdAt` and `askedAt`; `stepKind` for human, prompt, note, file, link
and frame nodes; `importSource` with runner, session, item ids and `cwd`,
and `source`, the frozen import snapshot; link nodes carry `linkUrl`,
`linkTitle`, `linkFetchedAt` and the captured HTML; attachments carry
page images, extracted text with the model that extracted it, a digest,
and for imported tool calls the `paths` and `op`. Edges are solid
(conversation), dashed (summary reference), orange (exploration) or red
(sliding reviewer).

`MemoryEntry` (`lib/memory.ts:20-28`) is `id`, `text`, `kind` of auto,
manual or imported, `category`, the canvas name it came from, and a date.
The canvas event (`src/types.ts:244-251`) is a timestamp, an op, an
optional object id and light metadata, *"NEVER text content."* The why
layer's `CanonicalEvent` (`lib/events/types.ts`) carries `basis` —
observed, reconstructed, inferred — and `completeness` on every event, a
`SourcePointer` back to the runner's own record, and artifact ids by
scheme (`file://`, `https://`, `arxiv:`, `thoughtdag:attachment/`), with
locators for pages, lines and quotes.

## 6. Retrieval Mechanics

There is no search on the canvas; there is a walk. Retrieval is the set
of nodes reachable by incoming wires, in an order the compiler fixes
independent of creation history so that *"the same graph always produces
the same prompt,"* trimmed by what a person did to the nodes — archive,
collapse with summary, highlight filter — and never by score. A dashed
reference contributes its question and answer and the trail of upstream
questions, or the whole chain when the edge says so. The token weight per
layer is reported so the preview *"shows composition honestly,"* and the
preview is the request: the panel calls the function the dispatch calls.

The why layer is lookup, not ranking: `why` resolves a path, a bare
filename inside the workspace, an `@`-prefixed host path, an arXiv id or
a URL to the turns whose tool calls touched it, newest first, reads
hidden unless asked; `find` matches exact words in what was asked or
answered, streamed from the text index without parsing it whole. The
benchmark's equivalence suite is the retrieval test for the canvas: a
probe graph with marker texts compiled through the product yields the
node order, compared against an independent reference compiler across
every condition of every case and six synthetic structures, with a cycle
refused.

## 7. Write Mechanics

A generation blocks on the model and streams into its node; the debounced
store write lands a second after the last chunk and the folder backup a
minute after the last edit. Nothing rewrites the graph in the
background: the atlas appends turns as the source file grows, the why
index refreshes on a query when a source moved, and the memory judge is
fire-and-forget with failures silent by design. Condense, merge and weave
are new nodes a person asks for; replay is a person's command that
regenerates stale nodes in dependency order with a token estimate first.

The one automatic writer is the memory judge, and it is fenced twice: the
judge only observes and classifies, with its prompt version bumped and a
golden set of twenty exchanges run before and after any wording change
(`scripts/test-memory-judge.mjs`, `scripts/memory-goldens.json`), and the
rules — category, stated identity, credential pattern, duplicate, session
cap, unknown update id — live in `admissionCheck` where *"a wording drift
cannot move it."* The harness bridge is the other writer, and it writes
somewhere else: a fork, an injected context or a queued prompt into a
live DeepSeek Harness session, fenced to the local host.

### Operational cost

A generation costs its model call; a memory judgement costs one more on
the cheapest configured model; the atlas and the why layer cost file
reads and no tokens. The benchmark pilot ran nine endpoints at no cost on
free tiers, about 30,000 input and 94,000 output tokens per model.

## 8. Agent Integration

A model sees the compiled messages with a role as system prompt, the
`[Memory]` block, materials, references, the chain, and the question;
it may call web and scholarly search and any MCP tool the proxy is
configured with. It cannot edit the graph. An external agent sees four
read-only questions over MCP and, inside DeepSeek Harness, the same four
as native tools plus a canvas that can send it a real turn with the wired
context injected first. Claude Code and Codex get adapter documents that
tell them to run `why --check` before editing a file and to open the
current session on the canvas by a protocol link or a local bridge that
copies the session file and never modifies the source.

The person's surfaces are the whole design: the canvas, the node panel
with its versions and *will send* preview, the sliding reviewer node, the
thought-map export, the memory manager, the atlas with its unread
watermark, and the folder backup. *"The graph is acyclic. You are the
loop."*

## 9. Reliability, Safety, and Trust

**Audit — awarded.** The event log is append-only in code and in
contract, records every semantic mutation with an id and metadata, and
records at dispatch a hash of what was sent; it survives undo, travels in
backups and exports. Two limits stated: the cap of 10,000 drops the oldest
thousand, and ambient-memory admissions produce a toast and no event.

**Human review — awarded.** Every entry into a model's context is a
person's wire, and every exit is a person's disconnect or archive; the
preview is built by the request's compiler; the one automatic writer
announces itself with an undo and is curated in a manager.

**Negative evaluation — awarded.** The why layer's committed case asserts
read-only turns stay out of a populated result by default and come back
on request; the equivalence suite asserts the product compiler's node
order for every pruned condition against a reference, with the compiled
artifacts committed.

**Trust state — withheld.** Stale is a mark prepended to text that still
flows — the transcript *"never silently contradicts itself,"* but the
model is asked, not prevented. `basis` and `completeness` on every why
event are epistemic labels of unusual care, and they are displayed,
never filtered. Identity memories are gated on *stated* at
admission and carry no state afterwards.

**Tombstone — withheld.** Archive keeps the node and excludes it; delete
removes it and logs the op; nothing records a value as refused, so a
pruned claim can be re-wired, re-imported from its source session, or
re-proposed by the judge — which is shown the existing entries, not the
deleted ones.

**Bitemporal — withheld.** Every version carries the time it was
generated, the time it was hand-edited and the hash of what it saw; a
link node carries when it was fetched; no node carries when what it says
was true.

**Scope — withheld.** A canvas is its own store and the wire is the only
filter within it; the ambient memory is global to the install, labelled
with the canvas that produced it and injected into every canvas; the why
index spans every runner's sessions on the machine.

**Read-only where it says so, and where it does not.** Source sessions
are read and never written, by the shell's primitives and by contract;
the harness bridge's `fork`, `inject` and `followup` write into live
harness sessions, fenced to the local host, and the feature-status page
draws the line at *"appending a new Harness turn is not rewriting old
logs."* The proxy and the bridge bind to loopback; the web demo holds no
keys and no content.

**A correction culture.** `benchmark/STATUS.md` records that the wave-2
reasoning comparison was two different models and not one with a switch,
withdraws the generalisations drawn from it, corrects the statistic to a
paired McNemar test after a reader's audit, and fixes a scorer provenance
bug that had missed OpenRouter's reasoning fields — dated, in the file
the numbers live in.

## 10. Tests, Evals, and Benchmarks

The CLI has 54 tests in seven files under `node:test` — the why layer
(22), the canvas adapter (10), the event contract (12), Pi sessions (5),
setup (3), MCP (2) — covering index construction across runners and
subagent files, private store permissions, facts without interpretation,
reads hidden by default, sessions split across files, page ranges, path
resolution, artifacts by arXiv id and URL, a turn id reused after a
compaction, exact-word `find`, JSON output with the evidence legend,
cache rebuild, stale-index refresh under concurrent queries, `--check`,
recall, status, purge and `npm pack`. The app has a Playwright smoke test
of persistence across a reload and a layout test; there is no unit suite
for the store. The memory judge has a twenty-case golden set run through
the live proxy, tolerating three flakes, with the instruction to compare
pass rates across prompt versions rather than single runs.

The benchmark is the serious artifact. `pilot-v1` is nine families of
arithmetic dependency graphs at three propagation depths, five conditions
each — clean, polluted, source prune, subgraph prune, recompute
descendants — 135 conditions per endpoint, conditions expressed as graph
operations and compiled through the product's own `buildContext` bundled
by esbuild, validated, checked for node-order equivalence, captured as
immutable traces, and scored by a declarative scorer that re-scores from
traces. Results recompute from the committed files: for `glm-4.5-flash`,
27 of 27 clean correct, 9 of 27 polluted, 27 source prune, 27 subgraph
prune, 26 recompute. Across the seven endpoints in `STATUS.md`, every
endpoint derails on conflicting claims and never on distractors, and
pruning the whole contaminated subgraph repairs every derailed case while
pruning only the source leaves a residue at depth two and three that the
reasoning ablation, on one endpoint, ties to reasoning being on. The
report calls itself pilot and reference results and not a leaderboard,
and the design document states the boundary: the benchmark shows that
graph-shaped context operations have value, not that this interface is
the only way to make them.

No paper; `CITATION.cff` cites the software and the README's one arXiv
link is an example query.

## 11. For Your Own Build

### Steal

- **One compiler for the preview and the request.** If the user can see
  exactly what will be sent, the retrieval is reviewable by construction.
- **Hash what you sent, at the moment you sent it.** A `commit` event
  with the request's SHA-256 and message count makes *what did the model
  see* a lookup, not a reconstruction.
- **Put the admission rules in code and version the judge's prompt.** A
  golden set run before and after a wording change is how a model-driven
  memory stops drifting by accident.
- **Mark stale in the transcript.** A downstream answer that carries its
  own stale upstream should say so where the model reads it.
- **Define benchmark conditions as graph operations and keep the traces.**
  A scorer that never needs the API again is one anyone can re-run.

### Avoid

- **A stale label instead of a gate.** The mark asks the model to
  discount an answer it is still shown; a person who has not replayed
  gets a model reasoning over a contradiction it was warned about.
- **Archive without a record.** Excluding a node is one wire away from
  including it again, and the judge cannot know what was refused.
- **A global memory with a project label nobody reads.** Three categories
  and a 45-day decay are the whole scoping; a preference stated on one
  canvas rides every canvas.
- **An append-only log with a rotation.** Ten thousand events is a lot
  of edits and a finite number of them.

### Fit

For a researcher or a developer who wants to see and shape what a model
is told — across their own conversations and the sessions their coding
agents left behind — this is a legible instrument, and the benchmark behind its one rule
is kept with a rigour its report earns. It is a
person's tool: no agent maintains the graph, no retrieval ranks it, and
the memory that forms on its own is three sentences per session behind a
constitution. A team wanting autonomous memory, cross-canvas scoping, a
tombstone or a validity axis will find the design has declined to build
them on purpose, and should read the feature-status page, which says what
is current, experimental and not promised.

## 12. Open Questions

- Does the stale mark change model behaviour? The benchmark's
  `recompute_descendants` condition regenerates stale nodes; no condition
  leaves them marked and measures the difference.
- What does the judge do with a memory a person undid? The next
  exchange shows it the surviving entries only; the same sentence can be
  proposed again.
- How does the harness bridge's `inject` interact with the event log?
  The context it injects is the canvas's compiled bundle; the harness's
  own transcript shows it, the canvas records a hand-off anchor.
- What is in the tombstone-shaped gap between archive and delete that
  `docs/features.md` does not name — is exclusion-with-a-record a
  roadmap item?

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `src/store/context-builder.ts` | 357 | `buildContext`, `hashContext`, `upstreamFingerprint`, the stale mark, role resolution |
| `src/store/streaming.ts` | 485 | Dispatch, the `commit` hash, version append, staleness recompute, the memory judge call |
| `src/store/slices/nodes.ts`, `llm.ts`, `events.ts`, `history.ts` | 557, 684, 27, — | Mutations and their events, `recomputeStaleness`, ask/merge/weave/explore |
| `src/lib/memory.ts` | 240 | Categories, the constitution, `admissionCheck`, the judge, the `[Memory]` block |
| `src/lib/context-bundle.ts`, `protocol/context-bundle/v0/` | — | The bundle compiler, schema and three fixtures |
| `src/lib/events/{types,project,manifests}.ts` | — | The event contract with `basis` and `completeness`, the projection, per-adapter honesty |
| `src/lib/adapters/*` | — | Claude Code, Codex, DeepSeek Harness, Pi and canvas readers |
| `src/lib/atlas/{discover,canonical,live-mirror,watermark,dsh-bridge}.ts` | 544 (canonical) | Session Atlas |
| `src/lib/{persistence,local-backup,export,ui-store}.ts` | — | IndexedDB, folder backup, exports, the memory library in `localStorage` |
| `src/types.ts` | — | `ThoughtData`, `CanvasOp`, `CanvasEvent` |
| `cli/src/lib.ts`, `cli/src/main.ts`, `cli/test/` | 1,226, 54 tests | The why layer and its suite |
| `dsh/lib/index.js` | — | The harness plugin's bridge and writes |
| `desktop/main.js` | 856 | Fenced session roots, backup, protocol links |
| `server.mjs`, `functions/api/[[path]].js` | 1,154, 594 | The proxy and its stateless twin |
| `benchmark/{DESIGN,README,STATUS}.md`, `tools/`, `runs/`, `runs/compiled/` | — | The design, the pipeline, nine endpoints' traces and results, compiled conditions |
| `scripts/test-memory-judge.mjs`, `memory-goldens.json`, `smoke.mjs` | — | The judge golden set, the persistence smoke test |
| `docs/reference/feature-status.md` | — | Current, experimental, not promised |

Searches behind the absence claims above, run from the repository root:

```sh
rg -n 'logEvent\(' src/lib/memory.ts                                   # none: memory admissions write no event
rg -n 'tombstone|refused|denylist|rejected' src/lib src/store --glob '*.ts'   # none on the canvas or the memory
rg -n 'valid_from|validFrom|valid_to|validTo' src --glob '*.ts*'      # none: no validity interval
rg -n 'memories\.filter\(' src/lib/memory.ts                          # one filter: the 45-day project decay; no canvas scope
rg -n 'staleSet.has' src/store/context-builder.ts                     # the mark is prepended; the node is not skipped
rg -n -i 'arxiv|doi' CITATION.cff README.md | rg -v 'find "arxiv"'    # no paper of its own
rg -c '^\s*(test|it)\(' cli/test/*.mjs                                # 54
```

## History

**2026-09-06** — [`e658c280d39082ec7d6d328bd1dff9af6d49b94e`](https://github.com/chenxiachan/thoughtdag/commit/e658c280d39082ec7d6d328bd1dff9af6d49b94e) — first reading, at the head of `main`, the sixth commit of that day. Screened first: no auto-run surface, no build-time execution, three manifests with floating ranges behind lockfiles, five dependency files inside the seven-day cooldown (the CLI, desktop and plugin manifests changed that day), an `AGENTS.md` treated as data; nothing installed or run. The repository is 177 MB, most of it documentation gifs and a video project, and the read was made from a full clone. Three marks; four withheld with their near misses. The benchmark's per-condition counts were recomputed from a committed `results.json` and match the status file.

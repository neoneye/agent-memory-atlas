---
title: "ThoughtDAG"
eyebrow: "Wires are the context"
description: "An editable thought graph where wires are the context, each request is hashed at dispatch, and recall brings topic dossiers into an ask."
root: ../..
page_kind: system
source_name: "chenxiachan/thoughtdag"
source_url: https://github.com/chenxiachan/thoughtdag
archive_name: "chenxiachan--thoughtdag"
revision: 850b89d1fceebb67e4869863fe1fd4449a244cc6
revision_url: https://github.com/chenxiachan/thoughtdag/commit/850b89d1fceebb67e4869863fe1fd4449a244cc6
analyzed_at: 2026-09-30
licence: "MIT"
size: "38,065 lines of TypeScript in 180 files under src/, a 1,895-line why-layer CLI, 1,630 lines of plain Node under runtime/, a 2,145-file benchmark directory; desktop app and harness plugin 0.5.8, CLI 0.2.2"
activity: "766 commits on main by 9 author names, one a bot, 746 of them by one author, 3 July – 30 September 2026"
tests: "78 node:test cases in ten CLI files, nine of them skipped below Node 22.15; a Playwright persistence smoke and layout test; a subagent fan-out script; a live-model memory-judge golden set; none run for this reading"
capabilities: "audit_log, negative_eval"
capability_evidence:
  audit_log: "the canvas event log | src/store/slices/events.ts:1-26, src/types.ts:420-438, src/store/streaming.ts:349-357, src/store/slices/nodes.ts:40-479, src/store/slices/llm.ts:22-625, src/lib/adapters/thoughtdag-canvas.ts:209-224 | an append-only list of semantic operations — ask, generate, edit-question, edit-response, regenerate, delete, archive, unarchive, highlight, connect, disconnect, merge, weave, explore, fanout, material-add, undo, redo and commit — each with a timestamp, the object id and metadata only, never text; undo rolls the graph back and is itself an event; `commit` records at dispatch the SHA-256 of the canonical request, memory and recall blocks included, with its message count, images, lane and model; the log persists with the canvas and in every backup, exports as CSV, and is projected into canonical `context.committed` events; a 10,000-event cap drops the oldest 1,000 past it; profile rewrites, dossier writes, topic labels and stale-judge verdicts write no event, an agent turn's approvals are kept on the node, and an agent-lane `commit` hashes the compiled messages under lane `proxy` | cli/test/canvas.test.mjs:49-130 (a backup's commit events round-trip through the canvas adapter with their hash and bundle id), cli/test/events.test.mjs"
  negative_eval: "the why layer and the benchmark compiler | cli/test/why.test.mjs:131-145, benchmark/tools/equivalence.mjs, benchmark/runs/compiled/rp-pilot-bakery-trays-k1.{polluted,source_prune,subgraph_prune}.compile.json | `why <path>` must not return read-only turns by default and must return them with `--include-read`, with the count of hidden reads reported — a populated index, the excluded material present, a positive control in the same case; the equivalence suite compiles every benchmark condition through the product's `buildContext` and asserts its node order equals an independent reference compiler's for every case, including the pruned conditions whose compiled artifacts show the deleted turn absent (seven messages polluted, five after source prune, three after subgraph prune) and a cyclic graph refused | cli/test/why.test.mjs:114 (facts hold no interpretation and no full answers), :123 (a stray file does not enter the index)"
stack_storage: "files"
stack_retrieval: "graph, lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "A node on a canvas — a question, answer versions with the model, time and context hash of each, a per-upstream record of what each input contributed, highlights, attachments with page provenance, a role, an archived flag, an import source and a frozen source snapshot — joined by wires that are the context; on a node that ran an agent turn, footprint attachments excluded from context by default; beside it two profile documents, preferences and identity, one fact per line, and one dossier per topic in four sections whose sentences cite the turns they rest on; in the why layer, a fact index over other agents' session files and the memory files Claude Code and Codex keep"
  storage: "IndexedDB per canvas (idb-keyval) with a one-minute debounced `.thoughtdag.json` folder backup; `localStorage` for the profile documents, the memory inbox and switches; `~/.thoughtdag/` for the why layer's fact index, text index, topic labels and dossiers, and a slim record of each canvas; a `.thoughtdag` folder in an agent turn's working directory for its guard file and copied materials; the source agents' session and memory files are read and never written"
  retrieval: "For a generation, a deterministic walk of the graph — materials, dashed reference blocks, the solid chain in order, the question last — with archived nodes skipped, stale answers marked and an excluded footprint reduced to one line naming its files; with recall switched on, up to two topic dossiers whole and verbatim excerpts found by the question's exact words or by judged topic labels, ranked by a decision model when one answers over a light, deep or full reach, inside a 4k, 12k or 40k token ceiling; for the why layer, exact phrase and path lookup with reads hidden by default; no vectors anywhere"
  write: "A person asks, edits, wires and imports; a model's answer lands as a version on its node; after an ordinary generation a decision model or the chat model decides whether something durable was said, a preference or identity fact is merged into its document by a model rewrite, and a project fact is filed to a topic dossier's inbox or to the memory inbox; dossiers are written by the chat model from labelled turns; Session Atlas mirrors other agents' turns idempotently; the harness bridge forks, injects and queues into live sessions; Pi and Codex turns edit files in a working directory behind a guard"
  update_delete: "Answers are versioned and never overwritten; a node can be archived — kept, dimmed and excluded from every context walk on its canvas — or deleted; a wire can be removed or converted; an upstream change marks dependants stale and replay regenerates them in dependency order; a profile rewrite can be undone at the toast or edited by hand; a dossier section can be edited, the dossier rebuilt from the turns or deleted; a recalled item can be struck from a node"
  scoping: "One canvas per IndexedDB key and reachability by wire as the only filter inside it; the profile documents are global to the install; recall reads every project's sessions, canvases and agent memory files on the machine and leaves out only the active canvas's own record; the why layer's JSON find honours a working-directory filter that no in-tree caller passes; an agent turn is fenced to one working directory per canvas"
  integration: "A React canvas in the browser, an Electron desktop app with fenced session roots, an Express proxy for OpenAI-compatible, Anthropic, Google, DeepSeek and Zhipu endpoints plus MCP tools and a pass-through for decision endpoints, a Cloudflare Pages demo with no server state, a `dsh-thoughtdag` plugin mounting the canvas and the why layer inside DeepSeek Harness, a CLI exposing `why_check`, `why_file`, `find` and `recall_turn` over MCP and listed in the MCP Registry, and Pi and Codex as agent runtimes behind the model picker"
  background: "A file watcher appends new turns of a subscribed session to its mirror; the why index refreshes when a source file's size or mtime moved; the memory judge runs fire-and-forget after ordinary generations; a labelling job asks the decision model one yes or no per topic for up to 600 turns per click; a stale judge asks whether an upstream change bears on each newly stale answer; a dossier with six filed facts merges when the memory page opens; nothing rewrites the graph on its own"
  trust: "A stale mark on any answer whose upstream fingerprint drifted, prepended in downstream context; a judge can dismiss the mark, which leaves the badge, the preview, the request and Replay alike; a footprint whose contents are withheld names its files; a basis and completeness on every why-layer event, displayed and never filtered; an identity fact admitted only when the user stated it; a credential pattern checked on the fact and not on the rewritten document; conclusiveness levels on takeaways, display only"
  strengths: "The preview and the request share one compiler; a request hash written at dispatch; dossier sentences that carry the keys of the turns they rest on; recall items listed, priced and strikeable on the node; a benchmark whose conditions are graph operations, whose traces are immutable and whose scorer can re-score without an API call; source sessions and agent memory files read and never rewritten"
  risks: "Stale is a label and a judge's dismissal removes it outright; recall crosses every project on the machine and can bring back an archived node from another canvas, and a full reach hands the opening of every indexed turn to the decision endpoint; the profile rewrite is a free model rewrite outside the constitution; the event log sees no profile, dossier or recall write; the working-directory filter has no caller and its one test does not exercise it; ambient identity and preferences ride every canvas; the proxy's agent and judge endpoints accept any target from any localhost origin"
---

## 1. Executive Summary

ThoughtDAG is **a context graph a person edits**: an infinite canvas where
each node is a question and its answer versions, each wire is context, and
*"what the model sees is exactly what wires into the node."* What it records
is what a model was shown, hashed at dispatch. Its weakness is at the
canvas's edges: recall reads every project on the machine and can bring
back a node archived on another canvas, and a model rewrites the profile
without the rules that admitted its facts.

Six things here are memory in the atlas's sense, and they are wired
together. The canvas persists — one IndexedDB key per canvas with a
debounced folder backup as a real `.thoughtdag.json` file — and a
generation's input is a deterministic walk of the graph
(`store/context-builder.ts:208-375`): materials first, dashed reference
blocks, then the solid chain in order, the question last, archived nodes
skipped at every layer. Each generation records the fingerprint of
everything upstream of the node with the node's own content blanked
(`upstreamFingerprint`, `:111-130`), and `recomputeStaleness`
(`slices/nodes.ts:271-287`) marks a node **stale** when the live
fingerprint drifts from the recorded one. A stale answer enters downstream
context prefixed *"[Stale: this answer was written against an earlier
version of its upstream]"* (`:157,:353`), and *Replay* regenerates stale
nodes in dependency order.

Second, a **profile**: two documents, preferences and identity, one fact
per line (`lib/profile.ts`). After an ordinary generation a decision
model — or the chat model when none is configured — decides whether the
exchange said something durable, and a constitution in code decides
admission: identity only when the user *stated* it, a credential pattern
blocks, three additions per canvas per visit, duplicates and unknown update
targets refused (`admissionCheck`, `lib/memory.ts:103-122`). An admitted
fact is merged by a model that rewrites the document, newest wins, with an
eight-second Undo. Both documents ride every ordinary generation as a
`[Memory]` block.

Third, **dossiers**: one maintained document per topic, four sections —
what it is, decisions taken, where it stands, what is open — each sentence
citing the turns it rests on (`lib/dossier.ts`). The chat model writes them
from turns a decision model has labelled by topic, and project facts the
memory judge files wait in a dossier's inbox until the next update.

Fourth, **Session Atlas**: the desktop shell fences the session directories
of Claude Code, Codex, DeepSeek Harness and Pi (`desktop/main.js:129-147`),
reads them and never writes them, and mirrors a session onto a canvas turn
by turn, appending idempotently past a per-session ledger. A run a turn
delegated to a subagent lands as a branch beside that turn
(`lib/atlas/subagents.ts`).

Fifth, the **why layer**: a CLI that reduces those session files — and the
memory files Claude Code and Codex keep for themselves — to an index of what
each turn did to which files, papers and URLs. It answers `why <path>`,
`find "<phrase>"` and `recall`, serves the four questions read-only over
MCP, and inside the app answers **recall**: with the switch on, an ask
brings in up to two topic dossiers and verbatim excerpts from any agent's
past sessions within a token ceiling, listed and strikeable on the node
(`lib/recall.ts:207-385`).

Sixth, an **agent lane**: the model picker lists Pi's and Codex's own
models, and picking one hands the node's compiled context and question to
that runtime in a working directory (`lib/agents/agent-runtime.ts`). A
guard (`runtime/agents/pi-guard.mjs`) asks the person, on the node, before
a tool reaches outside the working directory; the turn's tool calls come
back as footprint attachments excluded from context, and downstream context
carries one line naming the files the turn touched
(`store/context-builder.ts:245-308`).

**The record is of what the model was shown, not what it concluded.** At
dispatch the streaming slice writes a `commit` event carrying the SHA-256
of the canonical request — messages, image digests, model, tool flags —
its message count and lane (`store/streaming.ts:349-357`). The hash covers
the `[Memory]` block and any recall block, because both are inserted before
dispatch. The canvas event log (`slices/events.ts`) is append-only,
metadata-only, survives undo, persists with the canvas and exports as CSV,
and the canvas adapter projects its commits into canonical
`context.committed` events. The benchmark under `benchmark/` applies the
same discipline to a claim: nine endpoints, 1,215 captured conditions,
conditions defined as graph operations, traces immutable, and a
`STATUS.md` that records its own corrections.

**A decision model decides whether the model is told an answer is
stale.** With a judge configured, `judgeStaleness`
(`lib/stale-judge.ts:36-69`) asks whether an upstream change bears on each
newly stale answer, and a verdict under 0.5 dismisses the mark:
`shownStaleIds` (`:23`) subtracts it, and the badge, the panel's preview
(`focus-panel/FollowUpInput.tsx:69-74`) and every request path
(`slices/llm.ts:126,260,332,393,450,530`, `slices/evaluator.ts:78`,
`lib/experiment-loop.ts:77`) compile from that one set. The dismissed
answer stays in context, unlabelled; the dismissal writes no canvas event.

Replay reads the same set. Its chip and confirm dialog count and price
`shownStaleIds` (`App.tsx:689,1633-1648`), and `replayStale` snapshots it
(`slices/evaluator.ts:111`), a fix the maintainer made in
[`2991553e5a32f82781e97a2f740b9c66ef042276`](https://github.com/chenxiachan/thoughtdag/commit/2991553e5a32f82781e97a2f740b9c66ef042276)
and recorded on [issue #51](https://github.com/chenxiachan/thoughtdag/issues/51#issuecomment-5916161378).
The stale set does not exclude archived nodes (`slices/nodes.ts:271-287`),
so Replay regenerates an archived answer whose upstream drifted, one that
no walk reads.

Two marks: `audit_log` for the event log and `negative_eval` for the why
layer's hidden-reads case and the benchmark's compiler equivalence.
`human_review`, `tombstone`, `trust_state`, `bitemporal` and
`scope_enforced` are withheld, each a near miss stated in section 9. No
paper; the repository cites itself as software.

## 2. Mental Model

A belief here is a node the graph can reach. It enters three ways: a
person asks and a model answers on the canvas; a person imports material
— a PDF passage with its page, a link snapshot with its fetch time, a
note; or the atlas mirrors a turn another agent held, frozen as a
`source` snapshot beside the editable copy. A fourth way is recall: a past
turn or a dossier found by the question's words or topic, listed on the
node and carried into that one request. A node is *used* when a wire leads
from it to the node being asked: solid for the full turn, dashed for a
quoted reference, and the walk is the same whether a person is previewing
the request or the model is receiving it.

An answer is believed exactly as written until its upstream changes, at
which point it is stale — present, labelled as written against an older
input — until a person replays it. A decision model can rule that the
change does not bear on the answer. That ruling removes the label from
what the person sees and from what the model is sent alike.

It stops being used by exclusion, not erasure. Delete the wire and the
node stays on the canvas, reconnectable; archive the node and it is
dimmed and skipped by every walk on its canvas; delete it and it is gone,
with an event in the log and no other record. An archived node's text
stays in the why layer's index, because the canvas record the desktop
writes for it carries every node (`lib/canvas-record.ts:29-46`), so recall
from another canvas can bring it back. An answer is never overwritten — a
regeneration is a new version beside the old, each carrying the model that
wrote it, the time and the hash of what it saw.

The profile and the dossiers are the layers a model writes. A fact the
memory judge admits is merged into a document by a model that rewrites
the lines, *"the newest observation wins"*; a dossier is rewritten from
the turns it has not read and the facts filed for it, and a sentence is
dropped *"only when the new excerpts contradict or supersede it"*. Neither
keeps a record of a line it removed: the profile keeps forty changelog
notes, and an Undo restores the prior document together with its prior
changelog.

What a model is told about a thing it is not shown has three answers
here. A stale answer is shown, with a mark. An archived node is not shown,
and nothing in the context says so. An agent turn's tool output is not
shown, and the context says which files the turn touched and that their
contents were left out.

```mermaid
%% caption: a person's wires are the retrieval; the same compiler, given one stale set with the judge's dismissals removed, feeds the preview and the request, and Replay reruns that set; recall and the profile join the request before dispatch and the commit hash covers them; archive excludes on the canvas and not in the index recall reads
flowchart TB
    P["person: ask · wire · archive · edit · strike a recalled item"] --> G[("canvas graph<br/>IndexedDB per canvas · folder backup")]
    A["Session Atlas: Claude Code · Codex · DSH · Pi<br/>read-only session files"] --> G
    G -->|"every node, archived included"| X[("why index ~/.thoughtdag<br/>sessions · canvases · agent memory files")]
    A --> X
    G -->|"upstream fingerprint drifted"| S["stale set"]
    S --> SJ{"stale judge<br/>p below 0.5?"}
    SJ -->|"shownStaleIds: dismissals removed"| C["buildContext<br/>materials → references → chain → question<br/>archived skipped · stale marked"]
    SJ -->|"shownStaleIds"| RP["Replay<br/>counts and reruns the shown set<br/>archived answers included"]
    C --> PV["will-send preview"]
    X -->|"recall: two dossiers + excerpts<br/>light · deep · full reach<br/>active canvas left out"| R["recall block"]
    PR[("profile: preferences · identity")] -->|"[Memory] block"| Q["request"]
    C --> Q
    R --> Q
    Q -->|"commit: sha256(request) · n · model"| E[("event log<br/>append-only · metadata only")]
    Q --> LLM["model"]
    LLM -->|"answer version + context hash + per-input parts"| G
    LLM -->|"memory judge"| J{"constitution in code<br/>stated identity · no credential · 3 per canvas"}
    J -->|"preference · identity: model rewrites the document"| PR
    J -->|"project: topic dossier inbox or memory inbox"| D[("dossiers<br/>four sections · cited turns")]
    D --> X
```

## 3. Architecture

`src/` is a React 19 and Vite application: `App.tsx` (2,130 lines), the
canvas components over `@xyflow/react`, a zustand store split into slices
(`nodes`, `llm`, `attachments`, `highlights`, `history`, `events`,
`evaluator`, `roles`) with `context-builder.ts`, `streaming.ts` and
`projects.ts` beside them. `lib/` holds the mechanisms: `memory.ts`,
`profile.ts`, `dossier.ts`, `recall.ts`, `topics.ts`, `judge.ts`,
`stale-judge.ts`, `why-bridge.ts`, `context-bundle.ts`, `graph.ts`,
`canvas-record.ts`, `persistence.ts`, `local-backup.ts`, the `adapters/`
for each runner's session format, `atlas/`, `events/` and `agents/`.

`server.mjs` is the only backend: an Express proxy over the Vercel AI SDK
with web and scholarly search, MCP clients from `mcp.config.json`, PDF
extraction and URL fetch. On the person's machine it also mounts the agent
runtimes under `/api/agents`, the other agents' session files under
`/api/roots`, and `/api/judge`, a pass-through that forwards a decision
request to any http or https URL the body names (`server.mjs:637-655`); the
hosted twin forwards only to three named decision hosts.

`runtime/` is plain Node that the desktop shell, the harness plugin host
and the proxy share: `agents/pi.cjs` over `pi --mode rpc`,
`agents/codex.cjs` over `codex app-server`, the guard, `ops.cjs`,
`fs-diff.cjs`, `sessions-fs.cjs` and `terminal.cjs`.

`desktop/main.js` is the Electron shell: fenced session roots, backup
writes, protocol links, the agent runtimes over IPC, a private canvas
record per project under `~/.thoughtdag/canvases/` (`:471-494`), and the
why layer bundled as a library behind eighteen `why:*` IPC handlers
(`:822-842`). `dsh/lib/index.js` mounts the same why functions as HTTP
routes under the harness plugin host.

`cli/` is the why layer; `functions/` the Cloudflare twin of the proxy with
no storage; `protocol/` the Context Bundle v0 proposal; `benchmark/` the
cases, gold, suites, tools, compiled artifacts, runs and canvases.

Persistence is object storage into IndexedDB with a one-second debounce
and a flush on page hide (`lib/persistence.ts`). The profile documents,
the memory inbox and the switches live in `localStorage`
(`lib/ui-store.ts:308-331`). The why layer keeps `fact-index.json`,
`interpretation-cache.json`, `text-index.jsonl`, `topics.json` and
`dossiers.json` under `~/.thoughtdag/`, written through a temp file at
0600 in a 0700 directory (`cli/src/lib.ts:589-594`). Dossier writes are
read-modify-write of the whole file under their own lock, and past a
five-second wait *"the write goes ahead unlocked"* (`:1423-1439`).

### Deployment and ergonomics

Nothing to run for the desktop app beyond the installer; from source,
`npm run server` and `npm run dev`, a `.env` with at least one key or a
provider connected inside the app, Ollama for a fully offline model. The
decision model is optional: `DEFAULT_JUDGE` is enabled with no provider,
and an OpenRouter key, saved with the interfaces or typed into the judge's
own field, makes OpenRouter's Jev endpoint the provider without a further
setting (`lib/judge.ts:185-191`). The provider list's *off* entry leaves
every decision to its rule. Every decision falls
back to a rule when no judge answers within six seconds, and a failure
skips the judge for a minute. Recall, topics and dossiers need the why
layer, so the web demo has none of them.

## 4. Essential Implementation Paths

- **Compile.** `partitionContext` (`lib/graph.ts`) splits a node's
  upstream into materials, references and the mainline. `buildContext`
  (`context-builder.ts:208-375`) walks them in that order, dedups
  attachments by fingerprint and honours excluded and included attachment
  ids. It skips `archived` at every layer (`:314,:331,:345`), turns an
  excluded footprint into one line naming its files (`:245-308`),
  prepends the stale mark to a chain response in the `staleIds` it is
  given (`:353`), and returns messages with a parallel `sources` array.
  `hashContext` (`:97-102`) and `upstreamFingerprint` (`:111-130`) hash
  it; `upstreamParts` (`:137-154`) records a hash and a 240-character
  opening per upstream node.
- **Dispatch and record.** `streaming.ts:258-269` inserts the `[Memory]`
  block after the last answer; `:276-293` fetches recall items on a fresh
  ask, stores them on the node and inserts the recall block at the same
  seat. `:349-357` computes the SHA-256 of the canonical request and logs
  `commit`. On completion `writeFinal` (`:214-248`) appends the response
  as a version with `lastContextHash` and `lastContextParts`,
  `recomputeStaleness` runs, and `:523-530` fires `judgeMemory` with the
  active canvas.
- **Stale judge.** `recomputeStaleness` records the drifted fingerprint per
  node and imports `judgeStaleness`, which compares `lastContextParts`
  with the live parts, sends up to eight cases to `decideStaleness`
  (`judge.ts:137-150`), and stores a verdict keyed on that fingerprint.
  `shownStaleIds` (`stale-judge.ts:23`) subtracts dismissals; the badge,
  the preview, the context chain, the replay dialog's count, `replayStale`
  (`slices/evaluator.ts:111`) and every request read it.
- **Plaque summaries.** `generateSummary` (`streaming.ts:33-86`) asks the
  answering model, or the background model for an agent's answer, for one
  JSON ladder (`lib/ladder.ts`): a topic copied from inside the takeaway,
  the takeaway, a reason, and three or four sentence numbers whose verbatim
  text becomes the abstract. The thread it is shown is the ancestors' own
  plaques inside 1,400 tokens, archived steps skipped
  (`lib/ladder-context.ts:29-44`), a skip the maintainer added in
  [`2991553e5a32f82781e97a2f740b9c66ef042276`](https://github.com/chenxiachan/thoughtdag/commit/2991553e5a32f82781e97a2f740b9c66ef042276).
  When the ladder call comes back unusable, the one-line fallback prompt
  carries the ancestor path's takeaway lines from `collectMapLines`
  (`streaming.ts:90-106`), a walk that keeps archived steps
  (`:53-56,:84,:522`). Summaries are display-only and never enter context
  or fingerprints (`src/types.ts:303-304`).
- **Judge and admit.** `judgeMemory` (`memory.ts:177-220`) takes the
  typed path when a judge answers — `decideMemory` returns durable,
  category, stated and covers as probabilities, cut at 0.6, 0.7 for
  project and 0.7 for stated (`judge.ts:69-93`), and the chat model then
  phrases one sentence — or the prompt path, a versioned prompt parsed as
  one JSON line. Either verdict passes `admissionCheck`; a preference or
  identity goes to `mergeIntoDoc` (`profile.ts:52-73`), a project fact to
  `fileProjectFact` (`memory.ts:134-162`).
- **Dossier.** `buildDossier`, `updateDossier` and `rebuildDossier`
  (`dossier.ts:85-129`) fetch the topic's unread labelled turns through
  `dossierNewTurns`, have the chat model return four sections as JSON with
  source keys validated against what it was shown, and write through
  `setDossier`, which consumes only the pending facts the model read
  (`cli/src/lib.ts:1444-1454`).
- **Recall.** `fetchRecallItems` (`recall.ts:207-385`) asks the judge
  which topics the question is about, brings at most two built dossiers
  whole and asks whether the question wants a detail. It then looks up at
  most four terms with typo correction and merges topic-labelled hits.
  Without a judge it reads the 16 best hits in full, and at the light
  reach the 40 best. At the deep reach the judge first reads a snippet of each of up to
  2,000 hits; at the full reach, the opening of every turn the index lists
  (`turnsJson`, `cli/src/lib.ts:1109-1144`). Those go forty to a request,
  eight requests in flight, and at most 80 that pass are read in full
  (`recall.ts:299-349`). The judge keeps items at 0.5 and holds back those
  from 0.3, and the budget decides what comes in. The switch, reach and
  amount are snapshotted on the node at the ask (`ui-store.ts:461-466`).
- **Why.** `cli/src/lib.ts`: collectors per runner and `parseMemory`
  (`:510-529`) reduce session and memory files to facts; `hitsFor`
  (`:799-816`) hides read-like ops unless `--include-read` or nothing
  else happened; `findJson` (`:1088-1103`) filters by a working directory
  when one is passed; `labelStart` (`:1275-1337`) runs the topic
  labelling job.
- **Agent turn.** `agentOutbound` (`agent-runtime.ts:168`) picks the
  route; `compileForAgent` (`:268`) splits the compiled messages into the
  question and one block; `materialsToDisk` (`:224`) copies materials;
  `adoptAgentTurn` (`:443`) re-reads the session file and excludes the
  footprints. `pi-guard.mjs:75` blocks a call outside the working
  directory when nobody can be asked; `codex.cjs:31-34` maps `allow` to
  `danger-full-access`.
- **Mirror, bridge, bundle, export.** `importOrAppendSession`
  (`atlas/canonical.ts:34`); `dsh/lib/index.js` for the harness's fork,
  inject and follow-up writes and the `/why/*` routes;
  `compileContextBundle` (`lib/context-bundle.ts:170`); `export.ts:241-248`
  for the event log as CSV.

## 5. Memory Data Model

`ThoughtData` (`src/types.ts`) is the node: `question`, `response`,
`responses[]` with parallel `questions[]`, `generatedBy[]`,
`generatedAts[]`, `editedAts[]`, `summaries[]`, `summaryTypes[]`,
`summaryTypeConfidences[]` and `summaryConclusiveness[]` (display only);
`responseIndex`; `archived` and `archivedAt`; `lastContextHash`,
`lastContextParts` and `lastGeneratedAt`; `stepKind`; `importSource` and
`source`, the frozen import snapshot; `recall`, `recallItems[]` and
`recallMeta`; `recallSource` on a note cited from the why layer. Edges are
solid, dashed, orange or red.

A node that ran an agent turn also carries `agentSession`,
`pendingApprovals` and `approvals[]`, one record per decided question with
the tool, the question as shown, the outcome, the time and any value
(`src/types.ts:218-238`). A project's metadata holds `agentCwd` and
`agentGuard` (`store/projects.ts:46-50`).

A `RecallItem` (`src/types.ts:106-131`) names its kind (turn or memory),
runner, session, turn, title, working directory, file, the words that
found it, the text, its price, an `excluded` flag, the judge's relevance,
a cached card and the topics it was reached by, and for a dossier the
topic and its update time.

`MemoryDoc` (`lib/profile.ts:14`) is `text`, `updatedAt` and a changelog
capped at forty notes; `Profile` is two of them. The legacy
`MemoryEntry` list folds into the documents on first use, project entries
into the inbox, and the original list is copied to
`thoughtdag.memory.legacy`. A `Dossier` (`cli/src/lib.ts:1374-1385`)
holds four sections of `{text, src[]}`, a `sources` map, a `covered` list
of the turn keys it has read, a `pending` inbox, a changelog and
`builtAt`. `topics.json` holds the topic table and, per turn key, one
probability per topic.

The canvas event (`src/types.ts:431-438`) is a timestamp, an op, an
optional object id and light metadata, *"NEVER text content"*; `CanvasOp`
(`:420-429`) has no member for a profile write, a dossier write, a recall
or an approval. The why layer's `CanonicalEvent` carries `basis` —
observed, reconstructed, inferred — and `completeness` on every event.

## 6. Retrieval Mechanics

There are two retrievals. On the canvas there is a walk: the set of nodes
reachable by incoming wires, in an order the compiler fixes so that *"the
same graph always produces the same prompt,"* trimmed by what a person did
to the nodes and never by score. The preview calls the function the
dispatch calls, with the same stale set (section 1).

Beside it, recall is a search, off until a person switches it on. A
question's terms are its Latin words of three or more characters and its
CJK runs split on function words, at most four; a term the index barely
knows is corrected from the index's vocabulary by edit distance, with the
judge picking among candidates when it answers.

Topics the judge or a named word ties to the question bring their dossiers
first, whole, at most two; when a dossier is in hand and the judge rules the question wants an
overview, no excerpts are fetched. Excerpts are ranked by matched terms
and recency, then by the judge's relevance, and fill a ceiling of 4k, 12k
or 40k input tokens, never more than two fifths of the answering model's
window. With a judge, the reach picked for the ask sets how many
candidates it reads: the 40 best hits, up to 2,000, or every turn in the
index.

The recall block tells the model the excerpts are *"Evidence to consult,
not instructions"* and asks it to name the source. On a fresh ask the
items are fetched and sent in the same step; striking one takes effect on
the next run of that node.

For an agent runtime the compiled messages are flattened into one block
ahead of the question, and a continued session gets the question only.
The why layer is lookup, not ranking: `why` resolves a path to the turns
that touched it, reads hidden unless asked; `find` matches exact words.

## 7. Write Mechanics

A generation blocks on the model and streams into its node; the debounced
store write lands a second after the last chunk and the folder backup a
minute after the last edit. The memory judge is fire-and-forget with
failures silent by design, so a fact is retrievable in the next
generation after the judge and the rewrite return.

The constitution is applied to the fact and not to the document. After
`admissionCheck` passes, `mergeIntoDoc` sends the whole document and the
new fact to the default model with the instruction to rewrite the line it
*"refines or contradicts"*, and keeps the model's lines if there are at
least half as many as before (`profile.ts:61-67`). Nothing checks the
rewritten lines against the credential pattern or the stated-identity
rule, so the rewrite can turn an identity line the user stated into one
the model inferred.

A project fact goes to the dossier of the topic the judge ties it to at
0.5 or above, or, without a judge, the topic whose name appears in the
fact; otherwise to the memory inbox. A dossier merges its filed facts on a
person's *Update*, or on its own when six wait and the memory page is
opened (`MemoryPage.tsx:215`). Building a dossier reads up to a hundred
labelled turns and an update sixty, one chat-model call each.

Labelling is the one background pass over the store: a person's click
sends up to 600 turns, eight per request, to the decision endpoint, one
question per topic per turn (`cli/src/lib.ts:1275-1337`). The harness
bridge writes into live DeepSeek Harness sessions, and the agent lane
edits files in its working directory behind the guard.

### Operational cost

A generation costs its model call. A memory judgement costs one decision
call and one phrasing call with a judge, or one chat call without, plus a
rewrite call when the document is not empty. Recall costs up to three
decision calls per ask with a judge — topic, detail and relevance — plus
one per term it corrects, and none without one. A deep or full reach
replaces the relevance call with one per forty candidates, which the
project prices at about $0.0007 each (`recall.ts:150-154`). Picking full
in the menu shows the index's turn count with an estimated time and price
first; once it is set as the default, an ask runs it without that dialog
(`RecallChip.tsx:43-57`). The benchmark pilot ran nine endpoints on free tiers,
about 30,000 input and 94,000 output tokens per model.

## 8. Agent Integration

A model sees the compiled messages with a role as system prompt, the
`[Memory]` block, the recall block when recall is on, and the question; it
may call web and scholarly search, which start switched off like recall
(`ui-store.ts:219-220,239`), and any configured MCP tool. It cannot
edit the graph, the profile or a dossier.

An external agent sees four read-only questions over MCP — `why_check`,
`why_file`, `find` and `recall_turn` — and `find` reaches the memory files
Claude Code and Codex keep. Inside DeepSeek Harness the plugin host serves
the why layer as `/why/*` routes, including dossier and topic writes, to
the embedded canvas.

Pi and Codex, picked as models, get the canvas's compiled context as one
block ahead of the question, the materials copied to disk, and their own
tools in the working directory. What a runtime asks lands on the node as a
card; the approval list is appended to and de-duplicated by request id,
and the session record is merged rather than replaced.

The person's surfaces are the design: the canvas, the node panel with its
versions, *will send* preview and recall section, the memory page with
the two documents, the dossiers, the topic table and the inbox, and the
folder backup. *"The graph is acyclic. You are the loop."*

## 9. Reliability, Safety, and Trust

**Audit — awarded.** The event log is append-only in code and in
contract, records every semantic mutation of the graph with an id and
metadata, and records at dispatch a hash of what was sent, recall and
memory blocks included. Four limits: the 10,000-event cap drops the
oldest thousand; profile rewrites, dossier writes, topic labels and stale-judge
verdicts write no event; an agent turn's approvals are recorded on the
node; and an agent-lane `commit` hashes the compiled messages under lane
`proxy` (`lib/api.ts:247`) when the runtime received a flattened block.
The profile's and the dossiers' changelogs are capped at forty notes, and
an Undo restores the prior changelog with the prior document.

**Negative evaluation — awarded.** The why layer's committed case asserts
read-only turns stay out of a populated result by default and come back on
request; the equivalence suite asserts the product compiler's node order
for every pruned condition against a reference, with the compiled
artifacts committed.

**Human review — withheld.** The canvas is authoring: a person wires,
archives and edits, and the preview shows what will be sent. The memory
inbox is the nearest thing to a gate — a project fact no topic claims
waits there, reaches no context, and leaves when a person files it to a
dossier or discards it. Whether a fact waits is decided by the judge's
topic probability: at 0.5 or above it skips the inbox for a dossier's
pending list, which merges on its own at six. A preference or identity
fact is written before the person is told, with an Undo. The tool-approval
cards gate tool calls, not memory.

**Trust state — withheld.** Stale is a mark prepended to text that
flows. The stale judge's verdict is a probability that removes the mark
and keeps the answer in context. `basis` and `completeness` on every why
event are displayed and never filtered; conclusiveness levels on takeaways
are display only.

**Tombstone — withheld.** Archive excludes a node from its own canvas's
walks and not from the index recall reads, and delete leaves no record, so
a pruned claim can come back through recall from another canvas, a
re-import or the judge. A dossier's `covered` list keeps an update from
re-reading a turn whose sentence a person deleted by hand; it is keyed on
the turn, and *Rebuild* empties it.

**Bitemporal — withheld.** Every version carries when it was generated
and hand-edited; a dossier's *now* section is the model's summary of the
newest turns; no record carries when what it says was true.

**Scope — withheld.** A canvas is its own store and the wire is the only
filter within it. The profile is global to the install. Recall leaves out
the active canvas's own record and nothing else, so an ask on one canvas
can carry another project's Claude Code memory entry or a turn archived on
another canvas. `findJson` filters hits by a working directory on the
session or the memory entry whenever one is passed
(`cli/src/lib.ts:1091-1094`), and it is exposed as an IPC option and a
`/why/find` query parameter. No caller in the tree passes it, and the test
named for it asserts only that hits carry the field
(`cli/test/memory.test.mjs:139-146`). The turn listing behind the full
reach takes no working-directory option (`cli/src/lib.ts:1109`).

**What leaves the machine.** A decision request carries the exchange for
the memory judge, and for labelling each turn's opening 300 characters of
question and 700 of answer from every indexed agent session. For recall
it carries the question and 700-character excerpts: up to forty at the
light reach, a snippet of each of up to 2,000 hits at the deep one, and at
the full one the first 300 characters of question and answer of every
turn and memory entry in the index, the active canvas's record aside
(`recall.ts:299-349`, `cli/src/lib.ts:1109-1144`). The memory guide's
sentence that a decision *"sends only the question and the candidate
excerpts"* describes the recall call.

**Read-only where it says so.** Source sessions and agent memory files are
read and never written. The harness bridge's `fork`, `inject` and
`followup` write into live harness sessions, fenced to the local host. The
proxy's `/api/agents`, `/api/roots` and `/api/judge` sit behind a CORS
rule admitting any localhost origin on any port and a bind to `127.0.0.1`
unless `HOST` says otherwise (`server.mjs:529-533,:1236-1237`); `/api/judge`
forwards to any http or https target, the loopback included.

**A correction culture.** `benchmark/STATUS.md` records that the wave-2
reasoning comparison was two different models, withdraws the
generalisations drawn from it, corrects the statistic to a paired McNemar
test after a reader's audit, and fixes a scorer provenance bug — dated, in
the file the numbers live in.

## 10. Tests, Evals, and Benchmarks

The CLI has 78 cases under `node:test` in ten files: the why layer (22),
the event contract (12), the canvas adapter (10), DeepSeek Harness
sessions (9), agent memory files (6), dossiers (5), Pi sessions (5),
topics (4), setup (3) and MCP (2). The harness file aliases `test` to
`test.skip` when Node lacks zstd, so below Node 22.15 its nine cases
report as skipped. The dossier cases cover the storage contract: a
topic's unread turns, a write, pending facts that survive an update which
did not read them, and five concurrent filings that all land. The topics
cases run labelling against a stub endpoint and assert the key is not
written to disk.

`memory.test.mjs:139` is titled *"find --cwd style filtering is available
to hosts through the JSON api"*; it imports the bundle, discards the
import with `void lib`, and asserts one hit's `cwd` field, so the filter
it names has no test. The recall ranking and its reaches, the stale judge
and Replay's snapshot, the summariser's thread, the profile rewrite and the
agent lane have no test under `cli/test/`, `scripts/` or `src/`. The app
has a Playwright persistence smoke test and a layout test, and a script
asserts the subagent fan-out over Pi and Claude Code session fixtures
(`scripts/test-subagents.mjs`); there is no unit suite for the store.

The memory judge's twenty-case golden set runs the prompt path through the
live proxy (`scripts/test-memory-judge.mjs`), and `JUDGE_PROMPT_VERSION`
guards that prompt. The typed path's bars — 0.6, 0.7 and 0.7 — and the
document rewrite have no golden set.

The benchmark is the serious artifact. `pilot-v1` is nine families of
arithmetic dependency graphs at three propagation depths, five conditions
each — clean, polluted, source prune, subgraph prune, recompute
descendants — compiled through the product's own `buildContext`, checked
for node-order equivalence, captured as immutable traces, and scored by a
declarative scorer that re-scores from traces. For `glm-4.5-flash`, with
27 cases per condition: 27 clean correct, 9 polluted, 27 source prune, 27
subgraph prune, 26 recompute. Across the seven endpoints in `STATUS.md`, pruning the whole
contaminated subgraph repairs every derailed case while pruning only the
source leaves a residue at depth two and three.

No compiled condition carries the stale mark: across the 160 compiled
artifacts under `runs/compiled/` the string `[Stale:` does not occur. The
scorer reports `adopted_stale_answer`, so the metric a marked-and-kept
condition would need exists and the condition does not.

No paper; `CITATION.cff` cites the software and the README's one arXiv
link is an example query.

## 11. For Your Own Build

### Steal

- **One compiler for the preview and the request.** If the user can see
  exactly what will be sent, the retrieval is reviewable by construction.
- **Hash what you sent, at the moment you sent it,** after every
  late-inserted block. A `commit` with the request's SHA-256 makes *what
  did the model see* a lookup.
- **Cite the turn under every sentence of a summary.** A dossier line
  carrying its source keys, validated against the excerpts the model was
  shown, is a summary a person can check.
- **Consume only what the writer read.** An update that names the pending
  facts it saw leaves a fact filed mid-write for the next update.
- **Exclude with a pointer.** A withheld tool output that leaves *which
  files, contents not included* gives the model somewhere to look.
- **Define benchmark conditions as graph operations and keep the traces.**

### Avoid

- **Rules on the fact and a free rewrite of the document.** Admission
  checks that the rewrite step does not re-apply can be undone by it.
- **A scope parameter no caller passes, and a test named for it.** The
  filter exists, the product's own recall reads across every project, and
  the suite's title reads as coverage.
- **Exclusion on some read paths and not the others.** An archived node
  that recall can fetch from another canvas is archived on its own canvas
  only, and the summariser's fallback prompt carries its takeaway line.

### Fit

For a researcher or a developer who wants to see and shape what a model
is told — across their own conversations and the sessions their coding
agents left behind — this is a legible instrument, and the benchmark behind
its one rule is kept with rigour. It is a person's tool, and the memory
that forms on its own is two short documents and a set of dossiers a
person can read line by line. The recall layer reads everything on the
machine and ships excerpts to a decision endpoint when one is configured,
at the full reach the opening of every turn it has indexed;
anyone with client work in their Claude Code history should read section 9
before switching it on. A team wanting per-project isolation, a refusal
that survives archive, or a validity axis will find the design has not
built them.

## 12. Open Questions

- Does the stale mark change model behaviour? No compiled benchmark
  condition contains it. The missing condition is one graph operation away:
  correct the polluted source, leave B and C marked, and score
  `adopted_stale_answer` beside `source_prune` and `recompute_descendants`.
- Is recall meant to cross projects? `findJson` has the working-directory
  filter and the canvas knows its `agentCwd`; nothing joins them.
- What does the judge do with a fact a person undid or a line they
  deleted? It is shown the surviving lines; the same sentence can be
  proposed again.
- Is the agent-lane `commit` meant to be a hash of what the runtime
  received? It hashes the compiled messages and labels the lane `proxy`.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `src/store/context-builder.ts` | 401 | `buildContext`, `hashContext`, `upstreamFingerprint`, `upstreamParts`, the stale mark, the footprint pointer |
| `src/store/streaming.ts` | 657 | Dispatch, the memory and recall blocks, the `commit` hash, version append, the memory judge call, the plaque summary and its fallback map lines |
| `src/store/slices/nodes.ts`, `llm.ts`, `events.ts`, `evaluator.ts` | 583, 690, 26, 160 | Mutations and their events, `recomputeStaleness`, the request paths, `replayStale` |
| `src/lib/memory.ts`, `profile.ts`, `dossier.ts` | 220, 98, 157 | The constitution, `admissionCheck`, `judgeMemory`, the document merge, the inbox, dossier synthesis |
| `src/lib/judge.ts`, `stale-judge.ts`, `topics.ts` | 349, 69, 62 | The decision contract and providers, the typed decisions and bars, the stale verdicts, topic proposal and matching |
| `src/lib/recall.ts`, `why-bridge.ts`, `canvas-record.ts` | 435, 53, 92 | Recall into an ask and its reaches, the IPC and HTTP bridge, the canvas record the index reads |
| `src/lib/ladder-context.ts`, `src/components/ui/RecallChip.tsx` | 44, — | The summariser's thread, the recall menu and the full-reach dialog |
| `src/components/focus-panel/{FollowUpInput,ContextChainSection,RecallSection}.tsx`, `src/components/ui/MemoryPage.tsx` | — | The preview, the context chain, recall items, the memory page and auto-merge |
| `src/lib/agents/{agent-runtime,http-bridge}.ts`, `runtime/agents/*` | 583, 70, — | The agent lane, the guard, Pi and Codex |
| `src/lib/adapters/*`, `src/lib/atlas/*`, `src/lib/events/*` | — | Runner readers, Session Atlas, the event contract |
| `src/types.ts` | 438 | `ThoughtData`, `RecallItem`, `CanvasOp`, `CanvasEvent` |
| `cli/src/lib.ts`, `cli/src/main.ts`, `cli/test/` | 1,588, 307, 78 tests | The why layer, memory files, topics, dossiers, `findJson`, `turnsJson`, and the suite |
| `dsh/lib/index.js` | 1,392 | The harness plugin's bridge, writes and `/why/*` routes |
| `desktop/main.js` | 947 | Fenced session roots, the canvas record, the `why:*` IPC, the agent runtimes |
| `server.mjs`, `functions/api/[[path]].js` | 1,243, 661 | The proxy with `/api/agents`, `/api/roots`, `/api/judge`, and its stateless twin |
| `benchmark/{DESIGN,README,STATUS}.md`, `tools/`, `runs/` | — | The design, the pipeline, traces, results, compiled conditions |
| `scripts/test-memory-judge.mjs`, `memory-goldens.json`, `smoke.mjs`, `test-subagents.mjs` | — | The judge golden set, the persistence smoke test, the subagent fan-out |
| `docs/guides/memory.md`, `docs/reference/feature-status.md` | — | The memory guide; current, experimental, not promised |

Searches behind the absence claims above, run from the repository root:

```sh
rg -n 'logEvent\(' src/lib/memory.ts src/lib/profile.ts src/lib/dossier.ts src/lib/recall.ts src/lib/stale-judge.ts   # none: no memory, dossier, recall or verdict event
rg -n -A12 'export type CanvasOp' src/types.ts | rg -i 'approval|recall|memory'   # none: no op for them
rg -n 'get\(\)\.staleIds' src/store/slices   # nodes.ts:282 only (the previous set): no request or replay reads the unfiltered set
rg -n 'find\([^)]*\{[^}]*cwd' src dsh desktop cli/src                # one hit, the type declaration: no caller passes cwd
sed -n 1105,1144p cli/src/lib.ts | rg 'opts\.cwd'                  # none: the full reach's listing has no cwd filter
rg -n 'findJson' cli/test                                           # none: the filter has no test
rg -n 'archived' src/lib/adapters/thoughtdag-canvas.ts src/lib/canvas-record.ts   # none: the index keeps archived nodes
rg -c 'CREDENTIAL_PATTERN' src/lib/profile.ts src/lib/dossier.ts     # none: the rewrite is not re-checked
rg -n 'decideMemory|MEMORY_DURABLE_BAR' scripts                     # none: no golden set for the typed path
rg -n 'tombstone|refused|denylist|rejected' src/lib src/store --glob '*.ts'   # approval outcomes, a rejected import, a judge option: no refused-value record
rg -n 'valid_from|validFrom|valid_to|validTo' src --glob '*.ts*'    # none: no validity interval
rg -l 'Stale: this answer' benchmark/runs/compiled                  # none in the 160 artifacts: no condition compiles the mark
rg -l 'agent-runtime|pi-guard|fs-diff|compileForAgent|fetchRecallItems|judgeStaleness|mergeIntoDoc|replayStale|ladderContextFor|turnsJson' cli/test scripts   # none: lane, recall, stale judge, Replay, summariser thread and profile rewrite untested
sed -n 90,106p src/store/streaming.ts | rg archived                 # none: collectMapLines keeps archived steps
sed -n 271,287p src/store/slices/nodes.ts | rg archived             # none: the stale set keeps archived nodes
rg -n 'archived' src/store/slices/evaluator.ts                     # none: Replay and rerun do not skip archived nodes
rg -n 'confirmDialog' src/lib/recall.ts src/store/streaming.ts      # none: an ask at the default full reach is not confirmed
rg -n -i 'arxiv|doi' CITATION.cff README.md | rg -v 'find "arxiv"'  # no paper of its own
rg --files src | rg -i 'test|spec'                                 # none: no unit suite for the store
rg -c '^\s*(test|it)\(' cli/test/*.mjs; rg -c '^\s*t\(' cli/test/dsh.test.mjs   # 69, plus 9 under the alias
```

## History

**2026-09-30** — [`850b89d1fceebb67e4869863fe1fd4449a244cc6`](https://github.com/chenxiachan/thoughtdag/commit/850b89d1fceebb67e4869863fe1fd4449a244cc6) — 35 commits on, releases 0.5.4 to 0.5.8. The maintainer fixed two findings in [`2991553e5a32f82781e97a2f740b9c66ef042276`](https://github.com/chenxiachan/thoughtdag/commit/2991553e5a32f82781e97a2f740b9c66ef042276), recorded on [issue #51](https://github.com/chenxiachan/thoughtdag/issues/51#issuecomment-5916161378): Replay snapshots the judge-filtered stale set its dialog counts, and the summariser's thread skips archived steps ([section 1](#1-executive-summary), [section 4](#4-essential-implementation-paths)). The summary's fallback map lines and the stale set keep archived nodes. Added: recall reaches, deep and full, which hand up to 2,000 snippets or every indexed turn's opening to the decision endpoint ([section 9](#9-reliability-safety-and-trust)); web and scholarly search off by default; subagent runs mirrored as branches. The profile rewrite, archived nodes in the recall index, the missing stale benchmark condition and the uncalled working-directory filter are unchanged; no mark moved. Corrected: `server.mjs` had 1,201 lines at the previous pin, not 1,195. Screened from a full clone: no auto-run surface, five manifests inside the seven-day cooldown, `AGENTS.md` treated as data; nothing installed, built or run.

**2026-09-28** — [`af1f82a60811907feb8b5d32fd1ccbe59cf9a980`](https://github.com/chenxiachan/thoughtdag/commit/af1f82a60811907feb8b5d32fd1ccbe59cf9a980) — 14 commits on, releases 0.5.2 and 0.5.3. Every request path compiles from the stale set the preview shows, the judge's dismissals removed ([`d345f05037e6a4bf460e7d94e5451c2825ba06c7`](https://github.com/chenxiachan/thoughtdag/commit/d345f05037e6a4bf460e7d94e5451c2825ba06c7)), which closes the finding that a dismissed mark reached the preview and not the request ([section 1](#1-executive-summary)); Replay still counts the shown set and regenerates the whole one ([section 3](#3-architecture)). Added: summary ladders written with the thread's plaques in view, and the why layer's MCP server in the MCP Registry. The profile rewrite, archived nodes in the recall index, the benchmark's missing stale condition and the uncalled working-directory filter are unchanged; no mark moved. Screened from a full clone: no auto-run surface, four manifests inside the seven-day cooldown, `AGENTS.md` treated as data; nothing installed, built or run.

**2026-09-26** — [`6e98abf7b0745ece9ab9a06d530456ad4efcbeae`](https://github.com/chenxiachan/thoughtdag/commit/6e98abf7b0745ece9ab9a06d530456ad4efcbeae) — 33 commits on, releases 0.4.17 to 0.5.1. Memory became documents: the fragment list and its 45-day project decay gave way to two profile documents a model rewrites, topic dossiers, a decision-model judge, recall into an ask, and a stale judge whose dismissal reaches the preview and not the request ([section 1](#1-executive-summary)). No mark moved; `scope_enforced` stays withheld on a working-directory filter no caller passes ([section 9](#9-reliability-safety-and-trust)). Corrected at the previous pin: section 9 read *"Human review — awarded"* against the withdrawn mark, and the test count missed seven harness cases behind a `t` alias (61, not 54). Screened from a full clone: no auto-run surface, four manifests inside the seven-day cooldown, `AGENTS.md` treated as data; nothing installed, built or run.

**2026-09-19** — re-pinned to [`f05fc44d811f2ca5f33fa0ee4449aec4c483b4e2`](https://github.com/chenxiachan/thoughtdag/commit/f05fc44d811f2ca5f33fa0ee4449aec4c483b4e2), two commits and eight files on. **`human_review` is withdrawn; two marks stand.** Nothing in the range touches the mechanisms, so this is a correction to the reading. The surfaces the record named are all real and all keep their description: the canvas, the will-send preview built by the same `buildContext` the request uses, and the memory manager. None of them is a state a memory waits in. `judgeMemory` — the only path where a machine writes a memory — calls `setMemories` with the new entry and *then* raises a toast with an eight-second Undo, so the entry is live before anyone is told about it, and an update overwrites in place with the same affordance. A person disconnecting a node or deleting an entry afterwards is authoring, which the rubric separates from review by name. The `pendingApprovals` surface is a genuine human gate and gates tool calls, not memory content; it stays in section 9 without a mark, the same call this atlas made for OpenExecutive's approval ledger. Screened again first; nothing installed, built or run.

**2026-09-16** — [`3c57d429f83946498fce06d8e2a579c99f102e1e`](https://github.com/chenxiachan/thoughtdag/commit/3c57d429f83946498fce06d8e2a579c99f102e1e) — re-read at a commit dated 15 September 2026, 42 commits past the previous pin. All three marks re-tested and held, and the review surface is repaired: `pendingApproval` was one slot, so a second tool call arriving in parallel evicted the first question before anyone saw it and left the turn waiting on a card that no longer existed. It is now `pendingApprovals`, appended to and de-duplicated by request id. The `agentSession` record is merged rather than replaced for the same reason, and each stored version now carries the effort its run used. Screened before reading, from a full clone: no auto-run surface, no build-time execution point, three unpinned dependency surfaces and two dependency files inside the seven-day cooldown; an agent-addressed instruction file was recorded as data. Nothing was installed, built or run.

**2026-09-07** — [`0c6d961c84024beeda8fb7236fd66e470a40a5f5`](https://github.com/chenxiachan/thoughtdag/commit/0c6d961c84024beeda8fb7236fd66e470a40a5f5) — re-pinned twenty commits on, all of one day, for the agent lane: Pi and Codex as runtimes the model picker offers, a guard per working directory, an approval card, and footprints excluded from context with a pointer in their place; the context builder's one change is that pointer. The benchmark, the CLI, the memory judge and the event contract are byte-identical to the previous pin, and no mark moved. Corrected in the body: the line ranges cited for `buildContext`, its archived skips and the stale-mark prepend were wrong at the previous pin (the function starts at line 183, not 74), `memory.ts` is 168 lines rather than 240, and the event slice is 26. Added, with its search, the statement that no compiled benchmark condition carries the stale mark. Screened first: no auto-run surface, five manifests inside the seven-day cooldown (the app, desktop, plugin and CLI manifests and the lockfile), `AGENTS.md` treated as data; nothing installed or run, the read made from a full clone.

**2026-09-06** — [`e658c280d39082ec7d6d328bd1dff9af6d49b94e`](https://github.com/chenxiachan/thoughtdag/commit/e658c280d39082ec7d6d328bd1dff9af6d49b94e) — first reading, at the head of `main`, the sixth commit of that day. Screened first: no auto-run surface, no build-time execution, three manifests with floating ranges behind lockfiles, five dependency files inside the seven-day cooldown (the CLI, desktop and plugin manifests changed that day), an `AGENTS.md` treated as data; nothing installed or run. The repository is 177 MB, most of it documentation gifs and a video project, and the read was made from a full clone. Three marks; four withheld with their near misses. The benchmark's per-condition counts were recomputed from a committed `results.json` and match the status file.

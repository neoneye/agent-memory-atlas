---
title: "ThoughtDAG"
eyebrow: "Wires are the context"
description: "An editable thought graph where wires are the context, each request is hashed at dispatch, and recall brings topic dossiers into an ask."
root: ../..
page_kind: system
source_name: "chenxiachan/thoughtdag"
source_url: https://github.com/chenxiachan/thoughtdag
archive_name: "chenxiachan--thoughtdag"
revision: d450c9826a3fb940930456bf418890d11ba0d63d
revision_url: https://github.com/chenxiachan/thoughtdag/commit/d450c9826a3fb940930456bf418890d11ba0d63d
analyzed_at: 2026-11-02
licence: "MIT"
size: "41,471 lines of TypeScript in 194 files under src/, a 1,912-line why-layer CLI, 1,917 lines of plain Node under runtime/, a 2,208-file benchmark directory; desktop app and harness plugin 0.5.27, CLI 0.2.2"
activity: "851 commits on main by 12 author names, one a bot, 828 of them by one author, 3 July – 1 November 2026"
tests: "79 node:test cases in ten CLI files, nine of them skipped below Node 22.15; a Playwright persistence smoke and layout test; scripts for the undo rules, the subagent fan-out, the backup write, an imported turn's tool-record switch, background-call routing, notebooks, harness workspaces and the zstd head read; a live-model memory-judge golden set; none run for this reading"
capabilities: "negative_eval"
capability_evidence:
  negative_eval: "the why layer, the benchmark compiler and the turn-context script | cli/test/why.test.mjs:131-145, cli/test/canvas.test.mjs:178-195, benchmark/tools/equivalence.mjs:19-27, scripts/test-turn-context.mjs:85-94, benchmark/runs/compiled/rp-pilot-bakery-trays-k1.{polluted,source_prune,subgraph_prune}.compile.json | `why <path>` must not return read-only turns by default and must return them with `--include-read`, with the count of hidden reads reported; a canvas record holding a live node and an archived one must project no turn, wire or commit for the archived node, and `find` must miss its words while finding the live node's — populated indexes, the excluded material present, a positive control in each case; the equivalence suite compiles every benchmark condition through the product's `buildContext` and asserts its node order equals an independent reference compiler's, including the pruned conditions whose compiled artifacts show the deleted turn absent; an imported turn's tool record switched off must leave the question below reading the answer and the touched-files line and no call or result, and switched on must bring the execution record back | cli/test/why.test.mjs:114 (facts hold no interpretation and no full answers), :123 (a stray file does not enter the index)"
stack_storage: "files"
stack_retrieval: "graph, lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "A node on a canvas — a question, answer versions with the model, time and context hash of each, a per-upstream record of what each input contributed, highlights, attachments with page provenance, a role, an archived flag, an import source and a frozen source snapshot — joined by wires that are the context; on a node that ran an agent turn or was imported from one, tool-step attachments excluded from context by default and a count of the thinking the turn spent, display only; beside it two profile documents, preferences and identity, one fact per line, each line with a note of the fact, canvas, time and evidence that wrote it; one dossier per topic in four sections whose sentences cite the turns they rest on; in the why layer, a fact index over other agents' session files and the memory files Claude Code and Codex keep"
  storage: "IndexedDB per canvas (idb-keyval) with a one-minute debounced `.thoughtdag.json` folder backup; `localStorage` for the profile documents, the memory inbox, the switches and each canvas's ask-the-canvas turns; `~/.thoughtdag/` for the why layer's fact index, text index, topic labels and dossiers, and a slim record of each canvas; a `.thoughtdag` folder in an agent turn's working directory for its guard file and copied materials; the source agents' session and memory files are read and never written"
  retrieval: "For a generation, a deterministic walk of the graph — materials, dashed reference blocks, the solid chain in order, the question last — with archived nodes skipped, stale answers marked, an excluded tool record — an agent-lane footprint, or an imported turn's tool steps, which arrive switched off — reduced to one line naming its files, and a switched-on record folded into one execution record; with recall switched on, up to two topic dossiers whole and verbatim excerpts found by the question's exact words or by judged topic labels, ranked by a decision model when one answers over a light, deep or full reach, inside a 4k, 12k or 40k token ceiling; ask the canvas sends an outline of every live node and the focused node's chain; for the why layer, exact phrase and path lookup with reads hidden by default; no vectors anywhere"
  write: "A person asks, edits, wires and imports; a model's answer lands as a version on its node; after an ordinary generation a decision model, or without one an API model from the shared background order, decides whether something durable was said, a preference or identity fact is merged into its document by a model rewrite whose new lines are re-checked for credentials and which may drop at most two lines, and a project fact is filed to a topic dossier's inbox or to the memory inbox; dossiers are written by a background API model from labelled turns; Session Atlas mirrors other agents' turns idempotently; the harness bridge forks, injects and queues into live sessions; Pi and Codex turns edit files in a working directory behind a guard"
  update_delete: "Answers are versioned and never overwritten; a node can be archived — kept, dimmed, excluded from every context walk on its canvas and from the why layer's projection of the canvas at the next index refresh — or deleted; a wire can be removed or converted; an upstream change marks live dependants stale and replay regenerates them in dependency order; a profile rewrite can be undone at the toast or edited by hand; a dossier section can be edited, the dossier rebuilt from the turns or deleted; a recalled item can be struck from a node"
  scoping: "One canvas per IndexedDB key and reachability by wire as the only filter inside it; the profile documents are global to the install; recall reads every project's sessions, canvases and agent memory files on the machine by design, leaving out only the active canvas's own record; the why layer's JSON find honours a working-directory filter that no in-tree caller passes; an agent turn is fenced to one working directory per canvas"
  integration: "A React canvas in the browser, an Electron desktop app with fenced session roots, an Express proxy for OpenAI-compatible, Anthropic, Google, DeepSeek and Zhipu endpoints plus MCP tools and a pass-through for decision endpoints, a Cloudflare Pages demo with no server state, a `dsh-thoughtdag` plugin mounting the canvas and the why layer inside DeepSeek Harness through its sidebar, a CLI exposing `why_check`, `why_file`, `find` and `recall_turn` over MCP and listed in the MCP Registry, and Pi, Codex and the harness's agents as runtimes behind the model picker"
  background: "A file watcher appends new turns of a subscribed session to its mirror; the why index refreshes when a source file's size or mtime moved; the memory judge runs fire-and-forget after ordinary generations; a labelling job asks the decision model one yes or no per topic for up to 600 turns per click; a stale judge asks whether an upstream change bears on each newly stale answer; a node with autoRerun regenerates when an ancestor completes; a dossier with six filed facts merges when the memory page opens"
  trust: "A stale mark on any live answer whose upstream fingerprint drifted, prepended in downstream context; a judge can dismiss the mark, which leaves the badge, the preview, the request and Replay alike; a tool record whose contents are withheld names its files; a basis and completeness on every why-layer event, displayed and never filtered; an identity fact admitted only when the user stated it; a credential pattern checked on the fact and on every new line of the rewritten document; a stated, inferred, manual or folded note on each profile line, display only; conclusiveness levels on takeaways, display only"
  strengths: "The preview and the request share one compiler; a request hash written at dispatch; dossier sentences that carry the keys of the turns they rest on; recall items listed, priced and strikeable on the node; archive reaching the index recall reads; a benchmark whose conditions are graph operations, whose traces are immutable and whose scorer can re-score without an API call; source sessions and agent memory files read and never rewritten"
  risks: "The canvas event log drops its oldest thousand events past 10,000, and sees no profile, dossier, recall or ask-the-canvas write; stale is a label and a judge's dismissal removes it outright; recall crosses every project on the machine, and an archived node's dossier sentences and a mirrored turn's session text survive its archive; topic labels and dossier coverage are keyed by a node's position, which an archive shifts; a node with autoRerun reruns while archived; the profile's stated label is the admitted fact's, carried onto every line a rewrite changed; ambient identity and preferences ride every canvas; the proxy's agent and judge endpoints accept any target from any localhost origin"
---

## 1. Executive Summary

ThoughtDAG is **a context graph a person edits**: an infinite canvas where
each node is a question and its answer versions, each wire is context, and
*"what the model sees is exactly what wires into the node."* What it records
is what a model was shown, hashed at dispatch. Its weakness is at the
canvas's edges: recall reads every project on the machine, archive does not
reach a dossier sentence written from the turn before it was archived, and the log
that holds each request hash drops its oldest entries past a cap.

Six things here are memory in the atlas's sense, and they are wired
together. The canvas persists — one IndexedDB key per canvas with a
debounced folder backup as a real `.thoughtdag.json` file — and a
generation's input is a deterministic walk of the graph
(`store/context-builder.ts:276-478`): materials first, dashed reference
blocks, then the solid chain in order, the question last, archived nodes
skipped at every layer. Each generation records the fingerprint of
everything upstream of the node with the node's own content blanked
(`upstreamFingerprint`, `:176-198`), and `recomputeStaleness`
(`slices/nodes.ts:274-292`) marks a live node **stale** when the
fingerprint drifts from the recorded one. A stale answer enters downstream
context prefixed *"[Stale: this answer was written against an earlier
version of its upstream]"* (`:225,:456`), and *Replay* regenerates stale
nodes in dependency order.

Second, a **profile**: two documents, preferences and identity, one fact
per line (`lib/profile.ts`). After an ordinary generation a decision
model — or, when none is configured, the first API model of the shared
background order — decides whether the
exchange said something durable, and a constitution in code decides
admission: identity only when the user *stated* it, a credential pattern
blocks, three additions per canvas per visit, duplicates and unknown update
targets refused (`admissionCheck`, `lib/memory.ts:107-126`). An admitted
fact is merged by a model that rewrites the document, newest wins, with an
eight-second Undo. Both documents ride every ordinary generation as a
`[Memory]` block.

Third, **dossiers**: one maintained document per topic, four sections —
what it is, decisions taken, where it stands, what is open — each sentence
citing the turns it rests on (`lib/dossier.ts`). An API model writes them
from turns a decision model has labelled by topic, and project facts the
memory judge files wait in a dossier's inbox until the next update.

Fourth, **Session Atlas**: the desktop shell fences the session directories
of Claude Code, Codex, DeepSeek Harness and Pi (`desktop/main.js:195-205`),
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
(`lib/recall.ts:210-390`). The canvas's own record enters the index
through an adapter that leaves archived nodes out
(`lib/adapters/thoughtdag-canvas.ts:81-85`).

Sixth, an **agent lane**: the model picker lists Pi's and Codex's own
models, and picking one hands the node's compiled context and question to
that runtime in a working directory (`lib/agents/agent-runtime.ts`). A
guard (`runtime/agents/pi-guard.mjs`) asks the person, on the node, before
a tool reaches outside the working directory; the turn's tool calls come
back as footprint attachments excluded from context, and downstream context
carries one line naming the files the turn touched
(`store/context-builder.ts:329-410`). A turn imported from another agent's
session arrives the same way: its tool steps switched off
(`adapters/shared.ts:139-143`), one switch on the node passing them all on
(`slices/attachments.ts:68-81`). Switching it changes the fingerprint of
every answer below, so those answers turn stale.

**The record is of what the model was shown, not what it concluded.** At
dispatch the streaming slice writes a `commit` event carrying the SHA-256
of the canonical request — messages, image digests, model, tool flags —
its message count and lane (`store/streaming.ts:383-392`). The hash covers
the `[Memory]` block, any recall block and the execution-record header the
route picks, because all three are set before dispatch. The canvas event
log (`slices/events.ts`) is metadata-only, survives undo, persists with the
canvas and exports as CSV, and the canvas adapter projects the commits of
live nodes into canonical `context.committed` events. Past 10,000 events it
keeps the newest 9,000 (`:16,:24`), so it is a bounded record rather than
an append-only one. The benchmark under `benchmark/` applies the same
discipline to a claim: nine endpoints, 1,215 captured conditions,
conditions defined as graph operations, traces immutable, and a
`STATUS.md` that records its own corrections.

**A decision model decides whether the model is told an answer is
stale.** With a judge configured, `judgeStaleness`
(`lib/stale-judge.ts:36-69`) asks whether an upstream change bears on each
newly stale answer, and a verdict under 0.5 dismisses the mark.
`shownStaleIds` (`:23`) subtracts it, and the badge, the panel's preview
(`focus-panel/FollowUpInput.tsx:69-74`) and every request path
(`slices/llm.ts:129,269,341,411,469,549`, `slices/evaluator.ts:79`,
`lib/experiment-loop.ts:77`) compile from that one set. The dismissed
answer stays in context, unlabelled; the dismissal writes no canvas event.

Replay reads the same set. Its chip and confirm dialog count and price
`shownStaleIds` (`App.tsx:713,1701`), and `replayStale` snapshots it
(`slices/evaluator.ts:112`). The stale set passes over archived answers
(`slices/nodes.ts:281-282`), a skip
[`edcbe62dcc5f36b8965f98d24063549781b5ce63`](https://github.com/chenxiachan/thoughtdag/commit/edcbe62dcc5f36b8965f98d24063549781b5ce63)
added, so Replay neither counts nor regenerates one. Two paths run an
archived node all the same. `rerunNode` has no archived check
(`slices/evaluator.ts:36-44`), so a manual rerun runs. And after every
completion `triggerAutoReruns` (`store/streaming.ts:640-684`) reruns each
node with `autoRerun` whose ancestors include the completed node, archived
or not; a Replay wave's reruns pass through that hook, so an archived
reviewer below a replayed node is regenerated with them.

One mark: `negative_eval`, for the why layer's hidden-reads case, the
archived-canvas case, the imported turn's switched-off tool record and the
benchmark's compiler equivalence.
`audit_log` is withheld on the event log's cap; `human_review`,
`tombstone`, `trust_state`, `bitemporal` and `scope_enforced` are withheld
too, each a near miss stated in section 9. No paper; the repository cites
itself as software.

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
dimmed, skipped by every walk on its canvas, and left out when the why
layer next projects the canvas record (`thoughtdag-canvas.ts:81-85,:220`);
delete it and it is gone, with an event in the log and no other record.
The desktop rewrites that record within a minute of a change
(`lib/canvas-record.ts:14,:69-78`), and the next query re-reads a record
whose size or mtime moved and replaces its lines
(`cli/src/lib.ts:613-636,:655-690`).

Two copies outlive an archive. A mirrored turn's text is not in the canvas
record at all — the index reads it from the runner's own session file
(`thoughtdag-canvas.ts:106-107`). And a dossier sentence written from the
turn before it was archived stays in the dossier recall brings in whole.
An answer is never overwritten — a regeneration is a new version beside
the old, each carrying the model that wrote it, the time and the hash of
what it saw.

The profile and the dossiers are the layers a model writes. A fact the
memory judge admits is merged into a document by a model that rewrites
the lines, *"the newest observation wins"*; a dossier is rewritten from
the turns it has not read and the facts filed for it, and a sentence is
dropped *"only when the new excerpts contradict or supersede it"*. Each
profile line carries a note of the fact that wrote it, its canvas, its
time and its evidence. Neither layer keeps a record of a line it removed:
the profile keeps forty changelog notes, and an Undo restores the prior
document together with its prior changelog and notes.

What a model is told about a thing it is not shown has three answers
here. A stale answer is shown, with a mark. An archived node is not shown,
and nothing in the context says so. An agent turn's or an imported turn's
tool record, switched off, is not shown, and the context says which files
the turn touched and that their contents were left out.

```mermaid
%% caption: a person's wires are the retrieval; the same compiler, given one stale set with the judge's dismissals and archived answers removed, feeds the preview and the request, and Replay reruns that set; recall and the profile join the request before dispatch and the commit hash covers them; archive leaves the canvas walks and the index projection, while dossier sentences, mirrored session text and autoRerun keep reaching it
flowchart TB
    P["person: ask · wire · archive · edit · strike a recalled item"] --> G[("canvas graph<br/>IndexedDB per canvas · folder backup")]
    A["Session Atlas: Claude Code · Codex · DSH · Pi<br/>read-only session files"] --> G
    G -->|"canvas record within a minute<br/>adapter drops archived nodes"| X[("why index ~/.thoughtdag<br/>sessions · canvases · agent memory files")]
    A -->|"session text, mirrored turns included"| X
    G -->|"live answer, upstream fingerprint drifted"| S["stale set"]
    S --> SJ{"stale judge<br/>p below 0.5?"}
    SJ -->|"shownStaleIds: dismissals removed"| C["buildContext<br/>materials → references → chain → question<br/>archived skipped · stale marked"]
    SJ -->|"shownStaleIds"| RP["Replay<br/>counts and reruns the shown set"]
    RP -->|"each completion"| AR["autoRerun pass<br/>archived nodes not skipped"]
    C --> PV["will-send preview"]
    X -->|"recall: two dossiers + excerpts<br/>light · deep · full reach<br/>active canvas left out"| R["recall block"]
    PR[("profile: preferences · identity<br/>a note per line")] -->|"[Memory] block"| Q["request"]
    C --> Q
    R --> Q
    Q -->|"commit: sha256(request) · n · model"| E[("event log<br/>metadata only · newest 9,000 past 10,000")]
    Q --> LLM["model"]
    LLM -->|"answer version + context hash + per-input parts"| G
    LLM -->|"memory judge"| J{"constitution in code<br/>stated identity · no credential · 3 per canvas"}
    J -->|"preference · identity: model rewrite<br/>new lines re-checked · at most two dropped"| PR
    J -->|"project: topic dossier inbox or memory inbox"| D[("dossiers<br/>four sections · cited turns")]
    D --> X
```

## 3. Architecture

`src/` is a React 19 and Vite application: `App.tsx` (2,229 lines), the
canvas components over `@xyflow/react`, a zustand store split into slices
(`nodes`, `llm`, `attachments`, `highlights`, `history`, `events`,
`evaluator`, `roles`) with `context-builder.ts`, `streaming.ts` and
`projects.ts` beside them. `lib/` holds the mechanisms: `memory.ts`,
`profile.ts`, `dossier.ts`, `recall.ts`, `topics.ts`, `judge.ts`,
`stale-judge.ts`, `why-bridge.ts`, `canvas-chat.ts`, `context-bundle.ts`,
`graph.ts`, `canvas-record.ts`, `persistence.ts`, `local-backup.ts`, the
`adapters/` for each runner's session format, `atlas/`, `events/` and
`agents/`.

`server.mjs` is the only backend: an Express proxy over the Vercel AI SDK
with web and scholarly search, MCP clients from `mcp.config.json`, PDF
extraction and URL fetch. On the person's machine it also mounts the agent
runtimes under `/api/agents`, the other agents' session files under
`/api/roots`, and `/api/judge`, a pass-through that forwards a decision
request to any http or https URL the body names (`server.mjs:686-707`); the
hosted twin forwards only to three named decision hosts.

`runtime/` is plain Node that the desktop shell, the harness plugin host
and the proxy share: `agents/pi.cjs` over `pi --mode rpc`,
`agents/codex.cjs` over `codex app-server`, the guard, `ops.cjs`,
`fs-diff.cjs`, `sessions-fs.cjs` and `terminal.cjs`.

`desktop/main.js` is the Electron shell: fenced session roots, backup
writes, protocol links, the agent runtimes over IPC, a private canvas
record per project under `~/.thoughtdag/canvases/` (`:500-523`), and the
why layer bundled as a library behind eighteen `why:*` IPC handlers
(`:856-876`). `dsh/lib/index.js` mounts the same why functions as HTTP
routes under the harness plugin host.

`cli/` is the why layer; `functions/` the Cloudflare twin of the proxy with
no storage; `protocol/` the Context Bundle v0 proposal; `benchmark/` the
cases, gold, suites, tools, compiled artifacts, runs and canvases.

Persistence is object storage into IndexedDB with a one-second debounce
and a flush on page hide (`lib/persistence.ts`). The profile documents,
the memory inbox and the switches live in `localStorage`
(`lib/ui-store.ts:323-338`), and each canvas's ask-the-canvas turns under
their own key, the last forty (`components/CanvasChat.tsx:21-24`). The why
layer keeps `fact-index.json`, `interpretation-cache.json`,
`text-index.jsonl`, `topics.json` and `dossiers.json` under
`~/.thoughtdag/`, written through a temp file at 0600 in a 0700 directory
(`cli/src/lib.ts:589-596`). The first three carry the index version and are
rebuilt whole when it changes (`:91,:536-541`); `topics.json` and
`dossiers.json` carry versions of their own (`:1243,:1405`). Dossier writes
are read-modify-write of the whole file under their own lock, and past a
five-second wait *"the write goes ahead unlocked"* (`:1445`).

### Deployment and ergonomics

Nothing to run for the desktop app beyond the installer; from source,
`npm run server` and `npm run dev`, a `.env` with at least one key or a
provider connected inside the app, Ollama for a fully offline model. The
decision model is optional: `DEFAULT_JUDGE` is enabled with no provider,
and an OpenRouter key, saved with the interfaces or typed into the judge's
own field, makes OpenRouter's Jev endpoint the provider without a further
setting (`lib/judge.ts:185-191`). The provider list's *off* entry leaves
every decision to its rule. Every decision falls back to a rule when no
judge answers within six seconds, and a failure skips the judge for a
minute. Recall, topics and dossiers need the why layer, so the web demo
has none of them.

## 4. Essential Implementation Paths

- **Compile.** `partitionContext` (`lib/graph.ts:80`) splits a node's
  upstream into materials, references and the mainline. `buildContext`
  (`context-builder.ts:276-289`) calls `compileContext` (`:293-478`), which
  walks them in that order, dedups attachments by fingerprint and honours
  excluded and included attachment ids. It skips `archived` at every layer
  (`:417,:434,:448`), turns an excluded tool record into one line naming its
  files (`:329-410`), folds a switched-on tool record into one
  execution record (`:99-158,:394-404`), prepends the stale mark to a
  chain response in the `staleIds` it is given (`:456`), and returns
  messages with a parallel `sources` array. `hashContext` (`:162-167`) and
  `upstreamFingerprint` (`:176-198`) hash it, the fingerprint over the
  tool steps' raw shape; `upstreamParts` (`:205-222`) records a hash and a
  240-character opening per upstream node.
- **Dispatch and record.** `streaming.ts:272-292` inserts the `[Memory]`
  block after the last answer; `:295` fetches recall items on a fresh
  ask, stores them on the node and inserts the recall block at the same
  seat; `:328-329` swaps the execution record's header for an agent or a
  request that declares tools. `:383-392` computes the SHA-256 of the
  canonical request and logs `commit`. On completion `writeFinal`
  (`:231-269`) appends the response as a version with `lastContextHash`
  and `lastContextParts`, a store subscription reruns `recomputeStaleness`
  (`store/index.ts:89-93`), `:550-557` fires `judgeMemory` with the
  active canvas, and `:559-560` run the autoRerun pass and the paradigm
  cascade.
- **Stale judge.** `recomputeStaleness` skips notes, materials and
  archived nodes, records the drifted fingerprint per node and imports
  `judgeStaleness`, which compares `lastContextParts` with the live parts,
  sends up to eight cases to `decideStaleness` (`judge.ts:137`), and
  stores a verdict keyed on that fingerprint. `shownStaleIds`
  (`stale-judge.ts:23`) subtracts dismissals; the badge, the preview, the
  context chain, the replay dialog's count, `replayStale`
  (`slices/evaluator.ts:108-139`) and every request read it.
- **Plaque summaries.** `generateSummary` (`streaming.ts:35-89`) asks the
  answering model when it is an API model, then the shared background
  order (`lib/background-model.ts`), for one JSON ladder (`lib/ladder.ts`): a topic copied from inside the takeaway,
  the takeaway, a reason, and three or four sentence numbers whose verbatim
  text becomes the abstract. The thread it is shown is the ancestors' own
  plaques inside 1,400 tokens, archived steps skipped
  (`lib/ladder-context.ts:29-44`). The one-line fallback prompt's map lines
  come from `collectMapLines` (`streaming.ts:106-122`), which filters
  archived ancestors before it picks the takeaways and the opening
  question (`:108`). Summaries are display-only and never enter context or
  fingerprints.
- **Judge and admit.** `judgeMemory` (`memory.ts:181-223`) takes the
  typed path when a judge answers — `decideMemory` returns durable,
  category, stated and covers as probabilities, cut at 0.6, 0.7 for
  project and 0.7 for stated (`judge.ts:69-93`), and an API model then
  phrases one sentence — or the prompt path, a versioned prompt parsed as
  one JSON line. Either verdict passes `admissionCheck`; a preference or
  identity goes to `mergeIntoDoc` (`profile.ts:91-119`) with the verdict's
  evidence and canvas as its origin, a project fact to `fileProjectFact`
  (`memory.ts:138`).
- **Dossier.** `buildDossier`, `updateDossier` and `rebuildDossier`
  (`dossier.ts:85-129`) fetch the topic's unread labelled turns through
  `dossierNewTurns` (`cli/src/lib.ts:1484-1497`), have an API model
  return four sections as JSON with source keys validated against what it
  was shown, and write through `setDossier` (`:1461`), which consumes only
  the pending facts the model read.
- **Recall.** `fetchRecallItems` (`recall.ts:210-390`) asks the judge
  which topics the question is about, brings at most two built dossiers
  whole and asks whether the question wants a detail (`:246-258`). It
  then looks up at most four terms with typo correction and merges
  topic-labelled hits. Without a judge it reads the 16 best hits in full,
  and at the light reach the 40 best. At the deep reach the judge first
  reads a snippet of each of up to 2,000 hits; at the full reach, the
  opening of every turn the index lists (`:303-314`, `turnsJson`,
  `cli/src/lib.ts:1111-1161`). Those go forty to a request, eight requests
  in flight, and at most 80 that pass are read in full
  (`recall.ts:322-353`). The judge keeps items at 0.5 and holds back those
  from 0.3, and the budget decides what comes in. The switch, reach and
  amount are snapshotted on the node at the ask (`ui-store.ts:473`).
- **Ask the canvas.** `buildCanvasChat` (`lib/canvas-chat.ts:101`)
  numbers the live nodes, archived ones and frames left out (`:44-49`),
  and sends an outline of each with its parents, the focused node's chain,
  materials and references from `partitionContext`, and the last eight
  turns; `askCanvas` (`:154`) calls the picked model, the background order
  standing in for an agent or a failure, and keeps on the turn which
  model answered and which nodes went out in which layer.
- **Why.** `cli/src/lib.ts`: collectors per runner and `parseMemory`
  (`:510`) reduce session and memory files to facts; `eventsOf` reads a
  canvas record through the canvas adapter (`:294-301`); `hitsFor`
  (`:799`) hides read-like ops unless `--include-read` or nothing else
  happened; `findJson` (`:1088-1103`) filters by a working directory when
  one is passed; `labelStart` (`:1292`) runs the topic labelling job.
- **Agent turn.** `agentOutbound` (`agent-runtime.ts:168`) picks the
  route; `compileForAgent` (`:268`) splits the compiled messages into the
  question and one block; `materialsToDisk` (`:224`) copies materials;
  `adoptAgentTurn` (`:444`) re-reads the session file and excludes the
  footprints. `pi-guard.mjs:75` blocks a call outside the working
  directory when nobody can be asked; `codex.cjs:35` maps `allow` to
  `danger-full-access`.
- **Mirror, bridge, bundle, export.** `importOrAppendSession`
  (`atlas/canonical.ts`); `dsh/lib/index.js` for the harness's fork,
  inject and follow-up writes and the `/why/*` routes;
  `compileContextBundle` (`lib/context-bundle.ts`); `export.ts` for the
  event log as CSV.

## 5. Memory Data Model

`ThoughtData` (`src/types.ts`) is the node: `question`, `response`,
`responses[]` with parallel `questions[]`, `generatedBy[]`,
`generatedAts[]`, `editedAts[]`, `summaries[]`, `summaryTypes[]`,
`summaryTypeConfidences[]` and `summaryConclusiveness[]` (display only);
`responseIndex`; `archived` and `archivedAt`; `lastContextHash`,
`lastContextParts` and `lastGeneratedAt`; `stepKind`; `autoRerun` and
`autoRerunRounds`; `importSource` and `source`, the frozen import
snapshot; `reasoningTokens[]`, the thinking an imported or agent version
spent, counted and display only; `recall`, `recallItems[]` and `recallMeta`; `recallSource` on a
note cited from the why layer. Edges are solid, dashed, orange or red.

A node that ran an agent turn also carries `agentSession`,
`pendingApprovals` and `approvals[]`, one record per decided question with
the tool, the question as shown, the outcome, the time and any value
(`src/types.ts:253-273`). A project's metadata holds `agentCwd` and
`agentGuard` (`store/projects.ts:47-51`).

A `RecallItem` (`src/types.ts:141`) names its kind (turn or memory),
runner, session, turn, title, working directory, file, the words that
found it, the text, its price, an `excluded` flag, the judge's relevance,
a cached card and the topics it was reached by, and for a dossier the
topic and its update time.

`MemoryDoc` (`lib/profile.ts:19-20`) is `text`, `updatedAt`, a changelog
capped at forty notes and `notes`, one `LineNote` per line keyed by the
line's text: the time, the canvas, the evidence — `stated`, `inferred`,
`manual` or `folded` — and the line it replaced when a rewrite swapped
exactly one for one. `Profile` is two of them. The legacy `MemoryEntry`
list folds into the documents on first use, project entries into the
inbox, and the original list is copied to `thoughtdag.memory.legacy`.

A `Dossier` (`cli/src/lib.ts:1391-1402`) holds four sections of
`{text, src[]}`, a `sources` map, a `covered` list of the turn keys it has
read, a `pending` inbox, a changelog and `builtAt`. `topics.json` holds the
topic table and, per turn key, one probability per topic. A turn key is a
source and a position: `<file>#<index>` for labels (`cli/src/lib.ts:1249`)
and `<session>#<turn number>` for `covered` (`:1488`, `turnNumber`
`:864-866`). A canvas turn's index is its rank among the record's live
nodes (`thoughtdag-canvas.ts:81-83`), so archiving or deleting a node moves
every later node's key onto its neighbour's labels and coverage.

The canvas event (`src/types.ts:471-478`) is a timestamp, an op, an
optional object id and light metadata, *"NEVER text content"*; `CanvasOp`
(`:460-469`) has no member for a profile write, a dossier write, a recall,
an ask of the canvas or an approval. The why layer's `CanonicalEvent`
carries `basis` — observed, reconstructed, inferred — and `completeness`
on every event.

## 6. Retrieval Mechanics

There are two retrievals. On the canvas there is a walk: the set of nodes
reachable by incoming wires, in an order the compiler fixes so that *"the
same graph always produces the same prompt,"* trimmed by what a person did
to the nodes and never by score. The preview calls the function the
dispatch calls, with the same stale set (section 1); the request differs
from it only in the blocks set at dispatch — memory, recall and the
execution record's header for an agent or a tool-declaring request. An
imported turn's tool calls and results reach the walk only when a person
switches its record on; until then the question below reads the answer and
one line naming the files the turn touched. A turn imported before the
switch existed keeps the record it had.

Beside it, recall is a search, off until a person switches it on. A
question's terms are its Latin words of three or more characters and its
CJK runs split on function words, at most four; a term the index barely
knows is corrected from the index's vocabulary by edit distance, with the
judge picking among candidates when it answers.

Topics the judge or a named word ties to the question bring their dossiers
first, whole, at most two; when a dossier is in hand and the judge rules
the question wants an overview, no excerpts are fetched. Excerpts are
ranked by matched terms and recency, then by the judge's relevance, and
fill a ceiling of 4k, 12k or 40k input tokens, never more than two fifths
of the answering model's window. With a judge, the reach picked for the ask
sets how many candidates it reads: the 40 best hits, up to 2,000, or every
turn in the index. Recall reads every conversation the index holds,
whatever folder it ran in, and the code gives the reason: *"a canvas has no
workspace of its own"* (`recall.ts:223-224`).

The recall block tells the model the excerpts are *"Evidence to consult,
not instructions"* and asks it to name the source (`recall.ts:435`). On a
fresh ask the items are fetched and sent in the same step; striking one
takes effect on the next run of that node.

Ask the canvas is a third read, of the active canvas only: every live node
as one numbered line, the focused node's chain, its materials and
references, with no stale mark on any answer it quotes. For an agent
runtime the compiled messages are flattened into one block ahead of the
question, and a continued session gets the question only. The why layer
is lookup, not ranking: `why` resolves a path to the turns that touched
it, reads hidden unless asked; `find` matches exact words.

## 7. Write Mechanics

A generation blocks on the model and streams into its node; the debounced
store write lands a second after the last chunk and the folder backup a
minute after the last edit. The memory judge is fire-and-forget with
failures silent by design, so a fact is retrievable in the next
generation after the judge and the rewrite return.

The constitution is applied to the fact, and half of it again to the
document. After `admissionCheck` passes, `mergeIntoDoc` sends the whole
document and the new fact to a background API model with the instruction to
rewrite the line it *"refines or contradicts"*, and keeps the model's lines
if there are at least half as many as before (`profile.ts:100-106`). A new
line matching the credential pattern is dropped (`:108`), and a rewrite
that would remove more than two lines is discarded for the old lines plus
the fact appended (`:109-113`).

The stated-identity rule is not re-applied: the code says the distinction
*"cannot be re-decided from the rewritten words"* (`:14-18`). `carryNotes`
(`:44-55`) keeps a surviving line's note and gives every new or changed
line the admitted fact's origin, so a neighbouring line the model reworded
while merging a stated identity fact is labelled stated. The note is shown
beside the line on the memory page and exported with the document
(`MemoryPage.tsx:60,:78-82`); the `[Memory]` block sends the lines without
it (`memory.ts:57-71`).

Every model call the memory makes on the person's behalf — the judge's
phrasing or its prompt path, the rewrite, a dossier, topic proposals —
goes through one entry, `backgroundCall` (`lib/background-model.ts:84-102`).
It tries the caller's preference, here the list's default, then the API
model picked now, the one picked last, the default and the rest, never an
agent, at most three per call. A model that fails waits behind the others
for ten minutes, and an empty answer counts as a failure (`:63-70`). The
call returns which model answered. The judge, the rewrite and the dossier
writer keep only the text (`memory.ts:200,:205`, `profile.ts:102`,
`dossier.ts:61`), so a profile line or a dossier revision records no model,
and two rewrites of one document can come from different models.

A project fact goes to the dossier of the topic the judge ties it to at
0.5 or above, or, without a judge, the topic whose name appears in the
fact; otherwise to the memory inbox. A dossier merges its filed facts on a
person's *Update*, or on its own when six wait and the memory page is
opened (`MemoryPage.tsx:227`). Building a dossier reads up to a hundred
labelled turns and an update sixty, one background call each.

Labelling is the one background pass over the store: a person's click
sends up to 600 turns, eight per request, to the decision endpoint, one
question per topic per turn (`cli/src/lib.ts:1292`). A label is reused
while its key has one for every topic (`:1303-1306`), so a key that an
archive moved onto another turn is not relabelled. The harness bridge
writes into live DeepSeek Harness sessions, and the agent lane edits files
in its working directory behind the guard.

### Operational cost

A generation costs its model call. A memory judgement costs one decision
call and one phrasing call with a judge, or one background call without, plus a
rewrite call when the document is not empty. Recall costs up to three
decision calls per ask with a judge — topic, detail and relevance — plus
one per term it corrects, and none without one. A deep or full reach
replaces the relevance call with one per forty candidates, which the
project prices at about $0.0007 each (`recall.ts:154-157`). Picking full in
the menu shows the index's turn count with an estimated time and price
first; once it is set as the default, an ask runs it without that dialog
(`RecallChip.tsx:61-63`). The benchmark pilot ran nine endpoints on free
tiers, about 30,000 input and 94,000 output tokens per model.

## 8. Agent Integration

A model sees the compiled messages with a role as system prompt, the
`[Memory]` block, the recall block when recall is on, and the question; it
may call web and scholarly search, which start switched off like recall
(`ui-store.ts:226-228`), and any configured MCP tool. It cannot edit the
graph, the profile or a dossier.

An external agent sees four read-only questions over MCP — `why_check`,
`why_file`, `find` and `recall_turn` — and `find` reaches the memory files
Claude Code and Codex keep. Inside DeepSeek Harness the plugin host serves
the why layer as `/why/*` routes, including dossier and topic writes, to
the embedded canvas.

Pi, Codex and the harness's own agents, picked as models, get the
canvas's compiled context as one block ahead of the question, the
materials copied to disk, and their own tools in the working directory. A
Harness Agent question with no folder chosen runs in the canvas's own
folder (`atlas/dsh-bridge.ts`), and the plugin files the new session under
the harness workspace that folder belongs to. A
runtime's questions land on the node as one form, and one permission
switch per canvas maps ask, auto review and allow onto each runtime. The
approval list is appended to and de-duplicated by request id, and the
session record is merged rather than replaced.

The person's surfaces are the design: the canvas, the node panel with its
versions, *will send* preview and recall section, the ask-the-canvas
dialog, the memory page with the two documents and their line notes, the
dossiers, the topic table and the inbox, and the folder backup. *"The
graph is acyclic. You are the loop."*

## 9. Reliability, Safety, and Trust

**Audit — withheld.** The event log records every semantic mutation of
the graph with an id and metadata, survives undo, and records at dispatch
a hash of what was sent, recall and memory blocks included. It is not
append-only: `logEvent` keeps the newest 9,000 entries once the array
passes 10,000 (`slices/events.ts:16,:24`), a production delete of mutation
records that leaves no trace of the trim. Beside the cap: profile
rewrites, dossier writes, topic labels, stale-judge verdicts and
ask-the-canvas requests write no event; an agent turn's approvals are
recorded on the node; and an agent-lane `commit` hashes the compiled
messages under lane `proxy` (`lib/api.ts:287`) when the runtime received a
flattened block. The canonical projection drops the commits of archived
nodes (`thoughtdag-canvas.ts:220`). The profile's and the dossiers'
changelogs are capped at forty notes, and an Undo restores the prior
changelog with the prior document.

**Negative evaluation — awarded.** The why layer's committed case asserts
read-only turns stay out of a populated result by default and come back on
request (`cli/test/why.test.mjs:131-145`). A second case writes a canvas
record holding a live node and an archived one, and asserts the archived
node has no turn, wire or commit in the projection and that `find` misses
its words while finding the live node's
(`cli/test/canvas.test.mjs:178-195`). The equivalence suite asserts the
product compiler's node order for every pruned condition against a
reference, with the compiled artifacts committed. The turn-context script
asserts an imported turn's switched-off tool record stays out of the
question below while its answer and touched-files line arrive
(`scripts/test-turn-context.mjs:85-94`).

**Human review — withheld.** The canvas is authoring: a person wires,
archives and edits, and the preview shows what will be sent. The memory
inbox is the nearest thing to a gate — a project fact no topic claims
waits there, reaches no context, and leaves when a person files it to a
dossier or discards it. Whether a fact waits is decided by the judge's
topic probability: at 0.5 or above it skips the inbox for a dossier's
pending list, which merges on its own at six. A preference or identity
fact is written before the person is told, with an Undo. The tool-approval
cards and the question form gate tool calls, not memory.

**Trust state — withheld.** Stale is a mark prepended to text that
flows. The stale judge's verdict is a probability that removes the mark
and keeps the answer in context. A profile line's evidence note is a
discrete field, `stated` or `inferred` among four values, that no read
path filters on. `basis` and `completeness` on every why event are
displayed and never filtered; conclusiveness levels on takeaways are
display only. Archive is the field that excludes, and it is a person's
put-aside, keyed on the node.

**Tombstone — withheld.** Archive excludes a node from its canvas's walks
and from the index's projection of the canvas record, and delete leaves no
record. Both are keyed on the node: the same words re-asked, re-imported
or mirrored from a session come back, and a mirrored turn's archive leaves
its session text in the index. A dossier's `covered` list keeps an update
from re-reading a turn whose sentence a person deleted by hand; it is keyed
on the turn's position, and *Rebuild* empties it.

**Bitemporal — withheld.** Every version carries when it was generated
and hand-edited; a dossier's *now* section is the model's summary of the
newest turns; no record carries when what it says was true.

**Scope — withheld, by design.** A canvas is its own store and the wire
is the only filter within it. The profile is global to the install.
Recall leaves out the active canvas's own record and searches everything
else, on the stated ground that a canvas has no workspace
(`recall.ts:223-224`), so an ask on one canvas can carry another project's
Claude Code memory entry. `findJson` filters hits by a working directory on
the session or the memory entry whenever one is passed
(`cli/src/lib.ts:1088-1094`), and it is exposed as the `why:find` IPC
option (`desktop/main.js:860`) and a `/why/find` query parameter
(`dsh/lib/index.js:1447`). No caller in the tree passes it.

The comment that the filter *"serves the CLI and MCP"* (`recall.ts:224`)
is not borne out: the CLI's and the MCP server's `find` go through
`findHits` and `renderFind` and take no working directory
(`cli/src/main.ts:289-295`, `cli/src/lib.ts:1549-1553`). The test named for
the filter asserts only that hits carry the field
(`cli/test/memory.test.mjs:139-146`).

**What leaves the machine.** A decision request carries the exchange for
the memory judge, and for labelling each turn's opening 300 characters of
question and 700 of answer from every indexed agent session. For recall
it carries the question and 700-character excerpts: up to forty at the
light reach, a snippet of each of up to 2,000 hits at the deep one, and at
the full one the first 300 characters of question and answer of every live
turn and memory entry in the index, the active canvas's record aside
(`recall.ts:303-353`, `cli/src/lib.ts:1111-1161`). Ask the canvas sends
the canvas outline and the focused chain to the picked model, or to the
background order when the pick is an agent or fails.

**Read-only where it says so.** Source sessions and agent memory files are
read and never written. The harness bridge's `fork`, `inject` and
`followup` write into live harness sessions, fenced to the local host. The
proxy's `/api/agents`, `/api/roots` and `/api/judge` sit behind a CORS
rule admitting any localhost origin on any port and a bind to `127.0.0.1`
unless `HOST` says otherwise (`server.mjs:578-590,:1334-1336`);
`/api/judge` forwards to any http or https target, the loopback included.

**A correction culture.** `benchmark/STATUS.md` records that the wave-2
reasoning comparison was two different models, withdraws the
generalisations drawn from it, corrects the statistic to a paired McNemar
test after a reader's audit, fixes a scorer provenance bug, and says the
sixth condition has not been run — dated, in the file the numbers live in.

## 10. Tests, Evals, and Benchmarks

The CLI has 79 cases under `node:test` in ten files: the why layer (22),
the event contract (12), the canvas adapter (11), DeepSeek Harness
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
and Replay's snapshot, the summariser's thread and map lines, the profile
rewrite and its line notes, ask the canvas and the agent lane have no
test under `cli/test/` or `scripts/`. The app has a Playwright persistence
smoke test and a layout test, and scripts assert the undo rules over the
history slice (`scripts/test-undo.mjs`), the subagent fan-out over Pi and
Claude Code session fixtures and the backup write; there is no unit suite
for the store.

`scripts/test-turn-context.mjs` runs each runner's importer over a fixture
and asserts the tool step arrives switched off. It then compiles a question
below the imported turn through `buildContext`: switched off, the answer
and the touched-files line arrive and no call or result does; switched on,
the execution record arrives; the thinking never does (`:85-94`). The
question-below cases are a negative case with a positive control on each
side. Four more scripts cover the background order against a mock gateway
(`test-background.mjs`), notebook conversion, the harness workspace a new
session is filed under, and the zstd head read.

`benchmark/tools/turn-cost.mjs` measures, from local session logs, how an
agent turn's tokens split into question, answer, tool record and thinking,
and writes aggregate counts only; one 30-day run is committed
(`benchmark/runs/turn-cost/2026-10-27.json`). It measures the default the
switch sets and is not a test of it.

The memory judge's twenty-case golden set runs the prompt path through the
live proxy (`scripts/test-memory-judge.mjs`), and `JUDGE_PROMPT_VERSION`
guards that prompt. The typed path's bars — 0.6, 0.7 and 0.7 — and the
document rewrite have no golden set.

The benchmark is the serious artifact. `pilot-v1` is nine families of
arithmetic dependency graphs at three propagation depths, compiled through
the product's own `buildContext`, checked for node-order equivalence,
captured as immutable traces, and scored by a declarative scorer that
re-scores from traces. The captured conditions are five — clean, polluted,
source prune, subgraph prune, recompute descendants. For `glm-4.5-flash`,
with 27 cases per condition: 27 clean correct, 9 polluted, 27 source
prune, 27 subgraph prune, 26 recompute. Across the seven endpoints in
`STATUS.md`, pruning the whole contaminated subgraph repairs every derailed
case while pruning only the source leaves a residue at depth two and
three.

Every repair case carries a sixth condition, `source_prune_stale`: the
source pruned and the contaminated descendants kept under the product's
stale mark (`benchmark/DESIGN.md:87`). It is wired end to end.
`compile.mjs` passes its `stale_nodes` to `buildContext`
(`tools/lib.mjs:92-98`, `tools/compile.mjs:20`), and 30 compiled artifacts
carry the mark. `validate.mjs` requires it and checks that its stale nodes
are the contamination chain (`:55-67`). The capture loop sends its compiled
artifact like any static condition (`tools/run-capture.mjs:39-63`), and the
scorer loop scores it with `adopted_stale_answer`.

No committed run holds a trace for it, and `STATUS.md:5` says it has not
been run. `score.mjs` reads a trace for every condition a case lists with
no guard (`:13-14`), so re-scoring any committed run against the
six-condition cases stops at the first missing trace; `generate_figures.py`
plots the five.

No paper; `CITATION.cff` cites the software, and the arXiv ids in the tree
are example queries in the why-layer guide (`docs/guides/why-layer.md:117`).

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

- **A cap on the audit log.** A trim that keeps the newest entries turns
  the record of what was sent into the record of what was sent lately.
- **Keys by position.** A label or a coverage mark keyed on a turn's rank
  among live nodes moves to the neighbour when a node is archived.
- **A provenance label the rewrite hands out.** A line note that every
  changed line inherits from the admitted fact says *stated* about words
  the user did not state.
- **Exclusion on some read paths and not the others.** An archived node
  that the context walk, the stale set and the index skip is rerun by its
  own `autoRerun`, and its dossier sentences reach recall.

### Fit

For a researcher or a developer who wants to see and shape what a model
is told — across their own conversations and the sessions their coding
agents left behind — this is a legible instrument, and the benchmark behind
its one rule is kept with rigour. It is a person's tool, and the memory
that forms on its own is two short documents and a set of dossiers a
person can read line by line. The recall layer reads everything on the
machine and ships excerpts to a decision endpoint when one is configured;
anyone with client work in their Claude Code history should read section 9
before switching it on. A team wanting per-project isolation, a refusal
that survives re-assertion, a validity axis or a log that keeps everything
will find the design has not built them.

## 12. Open Questions

- Does the stale mark change model behaviour? The `source_prune_stale`
  condition compiles the mark into every repair case; no run has scored
  it beside `source_prune` and `recompute_descendants`.
- Should archive reach a dossier? A sentence built from a turn later
  archived stays, with the turn's key in its sources.
- Should a canvas turn's key be its node id? The why layer's turn ids
  are (`thoughtdag-canvas.ts:79`); labels and coverage use the
  position.
- What does the judge do with a fact a person undid or a line they
  deleted? It is shown the surviving lines; the same sentence can be
  proposed again.
- Is the agent-lane `commit` meant to be a hash of what the runtime
  received? It hashes the compiled messages and labels the lane `proxy`.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `src/store/context-builder.ts` | 504 | `buildContext`, `compileContext`, `hashContext`, `upstreamFingerprint`, `upstreamParts`, the stale mark, the footprint pointer, the execution record |
| `src/store/streaming.ts` | 684 | Dispatch, the memory and recall blocks, the `commit` hash, version append, the memory judge call, the plaque summary and its map lines, the autoRerun pass |
| `src/store/slices/nodes.ts`, `llm.ts`, `events.ts`, `evaluator.ts`, `attachments.ts` | 590, 708, 26, 161, — | Mutations and their events, the tool-record switch, `recomputeStaleness`, `setArchived`, the request paths, the event cap, `rerunNode`, `replayStale` |
| `src/lib/memory.ts`, `profile.ts`, `dossier.ts` | 224, 145, 157 | The constitution, `admissionCheck`, `judgeMemory`, the document merge and its line notes, the inbox, dossier synthesis |
| `src/lib/judge.ts`, `stale-judge.ts`, `topics.ts` | 353, 69, 62 | The decision contract and providers, the typed decisions and bars, the stale verdicts, topic proposal and matching |
| `src/lib/recall.ts`, `why-bridge.ts`, `canvas-record.ts` | 440, 53, 92 | Recall into an ask and its reaches, the IPC and HTTP bridge, the canvas record the index reads |
| `src/lib/adapters/thoughtdag-canvas.ts` | 237 | The canvas record's projection, archived nodes left out |
| `src/lib/background-model.ts`, `src/lib/adapters/shared.ts` | 102, — | The background order every memory call goes through; `seatTurnWork`, which imports a turn's tool steps switched off |
| `src/lib/canvas-chat.ts`, `src/components/CanvasChat.tsx` | 183, 199 | Ask the canvas and its per-canvas turns |
| `src/lib/ladder-context.ts`, `src/components/ui/RecallChip.tsx` | 44, 124 | The summariser's thread, the recall menu and the full-reach dialog |
| `src/components/focus-panel/{FollowUpInput,ContextChainSection,RecallSection}.tsx`, `src/components/ui/MemoryPage.tsx` | — | The preview, the context chain, recall items, the memory page with line notes and auto-merge |
| `src/lib/agents/{agent-runtime,http-bridge}.ts`, `runtime/agents/*` | 587, 76, — | The agent lane, the guard, Pi and Codex |
| `src/lib/adapters/*`, `src/lib/atlas/*`, `src/lib/events/*` | — | Runner readers, Session Atlas, the event contract |
| `src/types.ts` | 478 | `ThoughtData`, `RecallItem`, `CanvasOp`, `CanvasEvent` |
| `cli/src/lib.ts`, `cli/src/main.ts`, `cli/test/` | 1,605, 307, 79 tests | The why layer, memory files, topics, dossiers, `findJson`, `turnsJson`, and the suite |
| `dsh/lib/index.js` | 1,747 | The harness plugin's bridge, writes and `/why/*` routes |
| `desktop/main.js` | 984 | Fenced session roots, the canvas record, the `why:*` IPC, the agent runtimes |
| `server.mjs`, `functions/api/[[path]].js` | 1,342, 662 | The proxy with `/api/agents`, `/api/roots`, `/api/judge`, and its stateless twin |
| `benchmark/{DESIGN,README,STATUS}.md`, `tools/`, `runs/` | — | The design, the pipeline, traces, results, compiled conditions |
| `scripts/test-memory-judge.mjs`, `memory-goldens.json`, `smoke.mjs`, `test-undo.mjs`, `test-subagents.mjs`, `test-turn-context.mjs`, `test-background.mjs` | — | The judge golden set, the persistence smoke test, the undo rules, the subagent fan-out, the tool-record switch, the background order |
| `docs/guides/memory.md`, `docs/guides/why-layer.md`, `docs/reference/feature-status.md` | — | The memory guide, the why-layer guide; current, experimental, not promised |

### Recorded searches

Run at the tree root of the pinned checkout with `git grep -E`; a pipe
into `/usr/bin/grep` filters `git ls-files` output only.

```sh
git grep -n -E 'EVENT_CAP' -- src                                     # events.ts:16,:24 only: the one trim of the log
git grep -n -E 'logEvent\(' -- src/lib/memory.ts src/lib/profile.ts src/lib/dossier.ts src/lib/recall.ts src/lib/stale-judge.ts src/lib/canvas-chat.ts   # none: no memory, dossier, recall, verdict or ask-the-canvas event
git grep -n -A10 -E 'export type CanvasOp' -- src/types.ts | /usr/bin/grep -i -E 'approval|recall|memory|chat'   # none: no op for them
git grep -n -E 'get\(\)\.staleIds' -- src/store/slices                 # nodes.ts:287 only (the previous set): no request or replay reads the unfiltered set
git grep -n -E 'archived' -- src/store/slices/evaluator.ts             # none: rerunNode does not skip archived nodes
git grep -n -E 'archived' -- src/store/streaming.ts                    # :107-108 only: triggerAutoReruns does not skip archived nodes
git grep -n -E 'find\([^)]*\{[^}]*cwd' -- src dsh desktop cli/src ':!*.d.ts'   # none: no caller passes cwd
git grep -n -E 'cwdOnly|recallFolder' -- src                           # none: the folder row is gone
git grep -n -E 'findJson' -- cli/test                                  # none: the filter has no test
git grep -n -E 'findJson\(' -- cli/src/main.ts                         # none: the CLI's find does not reach the filter
git grep -n -E 'archived' -- cli/src src/lib/dossier.ts src/lib/topics.ts   # lib.ts:91 only: dossiers and labels keep archived turns
git grep -n -E 'archived' -- src/lib/canvas-record.ts                  # none: the record keeps archived nodes; the adapter drops them
git grep -n -E 'lineNote|\.notes([^[:alnum:]_]|$)' -- src ':!src/lib/profile.ts'     # MemoryPage.tsx only: no read path filters on a line note
git grep -n -i -E 'stale' -- src/lib/canvas-chat.ts src/components/CanvasChat.tsx   # none: ask the canvas sends no stale mark
git grep -n -E 'decideMemory|MEMORY_DURABLE_BAR' -- scripts            # none: no golden set for the typed path
git grep -n -i -E 'tombstone|denylist|blocklist' -- src cli/src dsh/lib runtime desktop   # none: no refused-value record
git grep -n -i -E 'valid_?(from|to|until)([^[:alnum:]_]|$)' -- src cli/src dsh/lib runtime desktop server.mjs   # none: no validity interval
git grep -l -F '[Stale: this answer' -- benchmark/runs/compiled        # 30 artifacts, all source_prune_stale
git ls-files benchmark/runs | /usr/bin/grep source_prune_stale | /usr/bin/grep -v -c '^benchmark/runs/compiled/'   # 0: no captured trace
git grep -n -E 'agent-runtime|pi-guard|fs-diff|compileForAgent|fetchRecallItems|judgeStaleness|mergeIntoDoc|carryNotes|replayStale|ladderContextFor|collectMapLines|turnsJson|buildCanvasChat' -- cli/test scripts   # test-background.mjs:144,158 only, a stubbed agent-runtime module: lane, recall, stale judge, Replay, summariser, profile rewrite and ask the canvas untested
git grep -n -E 'backgroundCall\(' -- src/lib/memory.ts src/lib/profile.ts src/lib/dossier.ts   # every hit destructures { text: raw }: no memory write keeps the answering model
git grep -n -E 'confirmDialog' -- src/lib/recall.ts src/store/streaming.ts   # none: an ask at the default full reach is not confirmed
git grep -n -i -E 'arxiv|doi' -- CITATION.cff README.md README_ZH.md   # none: no paper of its own
git ls-files src | /usr/bin/grep -i -E 'test|spec'                     # none: no unit suite for the store
git grep -c -E '^[[:space:]]*(test|it)\(' -- 'cli/test/*.mjs'; git grep -c -E '^[[:space:]]*t\(' -- cli/test/dsh.test.mjs   # 70, plus 9 under the alias
```

## History

**2026-11-03** — [`d450c9826a3fb940930456bf418890d11ba0d63d`](https://github.com/chenxiachan/thoughtdag/commit/d450c9826a3fb940930456bf418890d11ba0d63d) — recorded searches re-run at the same pin. Two recorded searches use `\b` or `\s` under `git grep -E`, which git built on macOS's regex library cannot match, so the part of each pattern using them matched nothing. They are rewritten with `-w` or POSIX classes and re-run. Each returns what its annotation states, and no claim moves.

**2026-11-02** — [`d450c9826a3fb940930456bf418890d11ba0d63d`](https://github.com/chenxiachan/thoughtdag/commit/d450c9826a3fb940930456bf418890d11ba0d63d) — 17 commits on, releases 0.5.23 to 0.5.27. No mark moved. An imported turn's tool steps arrive switched off behind one switch per node, and `scripts/test-turn-context.mjs` adds a negative case to the mark's evidence ([section 10](#10-tests-evals-and-benchmarks)). Every memory model call goes through one background order that never picks an agent, and no memory write keeps the model that answered ([section 7](#7-write-mechanics)). The CLI, recall, the stale judge, the event log, the canvas adapter and the benchmark are byte-identical to the previous pin. Corrected: the recorded `cwd`-caller search matched a type declaration at both pins and excludes `.d.ts` files. Screened from a full clone: no auto-run surface, three manifests inside the seven-day cooldown, `AGENTS.md` treated as data; nothing installed, built or run.

**2026-10-21** — [`7d9ba5e3db2e5cf26bdb25c529e2c2f55b12d10f`](https://github.com/chenxiachan/thoughtdag/commit/7d9ba5e3db2e5cf26bdb25c529e2c2f55b12d10f) — 68 commits on, releases 0.5.9 to 0.5.22. `audit_log` withdrawn, wrong at the previous pin: `logEvent` has trimmed the log past 10,000 events since it was written ([section 9](#9-reliability-safety-and-trust)); the README's arXiv example had also moved to the why-layer guide by then. Overtaken: archived canvas nodes leave the index's projection, index version 14 ([`eabdb89320ca010ec147dcaf1d9329112475f430`](https://github.com/chenxiachan/thoughtdag/commit/eabdb89320ca010ec147dcaf1d9329112475f430)). The profile rewrite drops credential-like lines, removes at most two and labels each line's origin ([section 7](#7-write-mechanics)). Every repair case carries `source_prune_stale`, compiled and not run ([section 10](#10-tests-evals-and-benchmarks)); a folder row reached the cwd filter and was removed in [`fc753e6e15bb0ea039365c1a3e1e4b0589012c60`](https://github.com/chenxiachan/thoughtdag/commit/fc753e6e15bb0ea039365c1a3e1e4b0589012c60); map lines and the stale set skip archived nodes. Found at both pins: the autoRerun pass reruns archived nodes ([section 1](#1-executive-summary)). Screened from a full clone: no auto-run surface, four manifests inside the seven-day cooldown, `AGENTS.md` treated as data; nothing installed, built or run.

**2026-09-30** — [`850b89d1fceebb67e4869863fe1fd4449a244cc6`](https://github.com/chenxiachan/thoughtdag/commit/850b89d1fceebb67e4869863fe1fd4449a244cc6) — 35 commits on, releases 0.5.4 to 0.5.8. The maintainer fixed two findings in [`2991553e5a32f82781e97a2f740b9c66ef042276`](https://github.com/chenxiachan/thoughtdag/commit/2991553e5a32f82781e97a2f740b9c66ef042276), recorded on [issue #51](https://github.com/chenxiachan/thoughtdag/issues/51#issuecomment-5916161378): Replay snapshots the judge-filtered stale set its dialog counts, and the summariser's thread skips archived steps ([section 1](#1-executive-summary), [section 4](#4-essential-implementation-paths)). The summary's fallback map lines and the stale set keep archived nodes. Added: recall reaches, deep and full, which hand up to 2,000 snippets or every indexed turn's opening to the decision endpoint ([section 9](#9-reliability-safety-and-trust)); web and scholarly search off by default; subagent runs mirrored as branches. The profile rewrite, archived nodes in the recall index, the missing stale benchmark condition and the uncalled working-directory filter are unchanged; no mark moved. Corrected: `server.mjs` had 1,201 lines at the previous pin, not 1,195. Screened from a full clone: no auto-run surface, five manifests inside the seven-day cooldown, `AGENTS.md` treated as data; nothing installed, built or run.

**2026-09-28** — [`af1f82a60811907feb8b5d32fd1ccbe59cf9a980`](https://github.com/chenxiachan/thoughtdag/commit/af1f82a60811907feb8b5d32fd1ccbe59cf9a980) — 14 commits on, releases 0.5.2 and 0.5.3. Every request path compiles from the stale set the preview shows, the judge's dismissals removed ([`d345f05037e6a4bf460e7d94e5451c2825ba06c7`](https://github.com/chenxiachan/thoughtdag/commit/d345f05037e6a4bf460e7d94e5451c2825ba06c7)), which closes the finding that a dismissed mark reached the preview and not the request ([section 1](#1-executive-summary)); Replay still counts the shown set and regenerates the whole one ([section 3](#3-architecture)). Added: summary ladders written with the thread's plaques in view, and the why layer's MCP server in the MCP Registry. The profile rewrite, archived nodes in the recall index, the benchmark's missing stale condition and the uncalled working-directory filter are unchanged; no mark moved. Screened from a full clone: no auto-run surface, four manifests inside the seven-day cooldown, `AGENTS.md` treated as data; nothing installed, built or run.

**2026-09-26** — [`6e98abf7b0745ece9ab9a06d530456ad4efcbeae`](https://github.com/chenxiachan/thoughtdag/commit/6e98abf7b0745ece9ab9a06d530456ad4efcbeae) — 33 commits on, releases 0.4.17 to 0.5.1. Memory became documents: the fragment list and its 45-day project decay gave way to two profile documents a model rewrites, topic dossiers, a decision-model judge, recall into an ask, and a stale judge whose dismissal reaches the preview and not the request ([section 1](#1-executive-summary)). No mark moved; `scope_enforced` stays withheld on a working-directory filter no caller passes ([section 9](#9-reliability-safety-and-trust)). Corrected at the previous pin: section 9 read *"Human review — awarded"* against the withdrawn mark, and the test count missed seven harness cases behind a `t` alias (61, not 54). Screened from a full clone: no auto-run surface, four manifests inside the seven-day cooldown, `AGENTS.md` treated as data; nothing installed, built or run.

**2026-09-19** — re-pinned to [`f05fc44d811f2ca5f33fa0ee4449aec4c483b4e2`](https://github.com/chenxiachan/thoughtdag/commit/f05fc44d811f2ca5f33fa0ee4449aec4c483b4e2), two commits and eight files on. **`human_review` is withdrawn; two marks stand.** Nothing in the range touches the mechanisms, so this is a correction to the reading. The surfaces the record named are all real and all keep their description: the canvas, the will-send preview built by the same `buildContext` the request uses, and the memory manager. None of them is a state a memory waits in. `judgeMemory` — the only path where a machine writes a memory — calls `setMemories` with the new entry and *then* raises a toast with an eight-second Undo, so the entry is live before anyone is told about it, and an update overwrites in place with the same affordance. A person disconnecting a node or deleting an entry afterwards is authoring, which the rubric separates from review by name. The `pendingApprovals` surface is a genuine human gate and gates tool calls, not memory content; it stays in section 9 without a mark, the same call this atlas made for OpenExecutive's approval ledger. Screened again first; nothing installed, built or run.

**2026-09-16** — [`3c57d429f83946498fce06d8e2a579c99f102e1e`](https://github.com/chenxiachan/thoughtdag/commit/3c57d429f83946498fce06d8e2a579c99f102e1e) — re-read at a commit dated 15 September 2026, 42 commits past the previous pin. All three marks re-tested and held, and the review surface is repaired: `pendingApproval` was one slot, so a second tool call arriving in parallel evicted the first question before anyone saw it and left the turn waiting on a card that no longer existed. It is now `pendingApprovals`, appended to and de-duplicated by request id. The `agentSession` record is merged rather than replaced for the same reason, and each stored version now carries the effort its run used. Screened before reading, from a full clone: no auto-run surface, no build-time execution point, three unpinned dependency surfaces and two dependency files inside the seven-day cooldown; an agent-addressed instruction file was recorded as data. Nothing was installed, built or run.

**2026-09-07** — [`0c6d961c84024beeda8fb7236fd66e470a40a5f5`](https://github.com/chenxiachan/thoughtdag/commit/0c6d961c84024beeda8fb7236fd66e470a40a5f5) — re-pinned twenty commits on, all of one day, for the agent lane: Pi and Codex as runtimes the model picker offers, a guard per working directory, an approval card, and footprints excluded from context with a pointer in their place; the context builder's one change is that pointer. The benchmark, the CLI, the memory judge and the event contract are byte-identical to the previous pin, and no mark moved. Corrected in the body: the line ranges cited for `buildContext`, its archived skips and the stale-mark prepend were wrong at the previous pin (the function starts at line 183, not 74), `memory.ts` is 168 lines rather than 240, and the event slice is 26. Added, with its search, the statement that no compiled benchmark condition carries the stale mark. Screened first: no auto-run surface, five manifests inside the seven-day cooldown (the app, desktop, plugin and CLI manifests and the lockfile), `AGENTS.md` treated as data; nothing installed or run, the read made from a full clone.

**2026-09-06** — [`e658c280d39082ec7d6d328bd1dff9af6d49b94e`](https://github.com/chenxiachan/thoughtdag/commit/e658c280d39082ec7d6d328bd1dff9af6d49b94e) — first reading, at the head of `main`, the sixth commit of that day. Screened first: no auto-run surface, no build-time execution, three manifests with floating ranges behind lockfiles, five dependency files inside the seven-day cooldown (the CLI, desktop and plugin manifests changed that day), an `AGENTS.md` treated as data; nothing installed or run. The repository is 177 MB, most of it documentation gifs and a video project, and the read was made from a full clone. Three marks; four withheld with their near misses. The benchmark's per-condition counts were recomputed from a committed `results.json` and match the status file.

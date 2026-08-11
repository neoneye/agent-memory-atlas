---
title: "PLUR1BUS"
eyebrow: "OpenClaw memory plugin"
description: "Per-agent LanceDB memory for OpenClaw where every correction is versioned, evidenced and logged, and where an append-only store means the copy a scorer reads is a decision the design has to make on purpose."
root: ../..
page_kind: system
source_name: "Cyb3rb1ade/openclaw-plur1bus-memory"
source_url: https://github.com/Cyb3rb1ade/openclaw-plur1bus-memory
revision: 3efedcd4179f6e5594229b7a52f2ca8a6e234d9a
revision_url: https://github.com/Cyb3rb1ade/openclaw-plur1bus-memory/commit/3efedcd4179f6e5594229b7a52f2ca8a6e234d9a
analyzed_at: 2026-08-11
capabilities: "trust_state, scope_enforced, audit_log, human_review, negative_eval"
stack_storage: "lancedb, sqlite, files"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A LanceDB card with a version number and a link to the version it replaced, plus JSONL neo records carrying a status and a trust level"
  storage: "Per-agent LanceDB tables, per-agent JSONL neo store, `node:sqlite` caches, and an optional Obsidian vault mirror"
  retrieval: "Vector plus lexical over LanceDB, graph hydration of neighbours, a decision trace per recall, and additive lens and reactivation passes"
  write: "Deferred to the `agent_end` hook through a per-agent scheduler; nothing blocks the reply"
  update_delete: "`safeUpdate` writes a new version, then supersedes the old row; `/forget` archives behind a confirmation token"
  scoping: "`checkAccess` fails closed on agent-private, workspace and user scopes, applied as a read filter in the adapter and the recall pipeline"
  integration: "OpenClaw plugin — chat commands, an `agent_end` capture hook, background crons, and an Obsidian review vault"
  background: "Daily consolidation, garbage collection, skill mining, critical-push classification, and two dream passes"
  trust: "Seven-state record status and a six-level trust ladder scored off the newest revision, plus an append-only reconsolidation event log"
  strengths: "A correction path that demands evidence, records the event, and orders its writes so a crash cannot lose the memory"
  risks: "Forty-seven config groups over one careful core; doubt states are ranking penalties rather than filters, and the drift gate is deliberately off"
---

## 1. Executive Summary

PLUR1BUS is an MIT-licensed memory plugin for OpenClaw, at release 7.2.6 — around 9,300 lines in `index.js`, 55,000 across `lib/`, and a further 70,000 in `tests/` and `test/`, which is the first unusual thing about it: the test suite is larger than the implementation it covers, across 317 test files.

The second unusual thing is the ratio of care to surface. `openclaw.plugin.json` declares forty-seven top-level configuration groups, covering dreaming, emotional state, persona voice, an Obsidian vault bridge, skill mining, reminders, a semantic lens, conversation reactivation, and a proactive governor. Underneath that is a correction path — `lib/safe-update.js`, 414 lines — that is more disciplined than most of the dedicated memory systems in this atlas: a content change is refused unless the caller supplies both an update source and a quoted piece of evidence, the replacement row is written and made durable *before* the old row is marked superseded, and the whole transition is appended to a reconsolidation event log keyed by an idempotency hash.

The most interesting single line in the repository is `safe-update.js:357`. Before a content change is accepted, the new embedding is compared against the old one and the update is rejected if the cosine distance exceeds 0.45 — a machine refusing to let a "correction" quietly replace a memory with something that means something else. It is a genuinely novel gate, and the only caller in the tree, the user-facing `/correct` command at `index.js:6422`, passes `skipDriftGate: true` — deliberately, with the reasoning written at the call site: the gate throws rather than degrades, a large correction is exactly what a user typing `/correct` intends, and the confirmation dialog shows the old and new text in full before anything is written. The measured drift is still recorded on the reconsolidation event. A gate that is off by argument is a different thing from a gate that is off by accident, and this is the first.

Where it is strongest: scope. `checkAccess` (`lib/acl-middleware.js:103`) denies by default, denies on a missing owner, denies on a conflicting ownership tuple, and is applied as a filter on the read path in three places. The tests assert the denials rather than the permissions.

Where it is weakest: the system can express doubt and mostly declines to act on it. A record carries a status from a seven-value set and a trust level from a six-value ladder, and `conflict`, `demoted` and `untrusted` are wired into the ranking arithmetic as penalties of 0.3, 0.35 and 0.3 rather than as filters. Only the deletion states withhold. A memory the system has flagged as contradicting another memory is ranked lower and can still reach the prompt — carrying its status in the rendered line, which is the difference between a model that can weigh the flag and one that cannot see it.

## 2. Mental Model

There are two stores and they hold different kinds of thing.

**LanceDB cards** are the memories proper — one table per agent, a row per card. A card's life is short to describe: it is `active`, or it has been superseded by a newer version that names it in `previousVersion`. Retrieval is unforgiving about this. `lib/recall-pipeline.js:137` drops any entry whose status is set and is not `active`, so a superseded card is not ranked down, it is gone from the read path.

**Neo records** are the JSONL layer — turn journal, memory candidates, behaviour cards, graph edges, dream diary, episodes — and they carry the epistemics. Each record has a `status` from `NEO_STATUSES` (`lib/neo-arch.js:62`):

```js
["candidate", "active", "promoted", "demoted", "conflict", "pruned", "tombstoned"]
```

and an `origin.trustLevel` from `NEO_TRUST_LEVELS` (`lib/neo-arch.js:52`), running `untrusted → user_asserted → assistant_asserted → tool_observed → validated → curated`.

What moves a record between states is a person. `/plur1bus memory promote|demote|prune|tombstone <id>` (`index.js:5961`) requires authorization, calls `transitionRecordStatus`, and appends the transitioned record back to the JSONL. There is no automatic promoter; a candidate becomes promoted because someone typed the command.

The consequence of each state is where the design divides. `scoreNeoRecallItem` (`lib/neo-arch.js:1379`) returns `-Infinity` for `pruned` and `tombstoned` — those are genuinely withheld. Everything between is arithmetic:

```js
const trustBoost = ({ curated: 0.3, validated: 0.25, user_asserted: 0.18,
  tool_observed: 0.18, assistant_asserted: -0.2, untrusted: -0.3 })[item.origin?.trustLevel] ?? 0;
…
const penalties = (item.origin?.role === "assistant" ? 0.2 : 0)
  + (item.status === "demoted" ? 0.35 : 0)
  + (item.status === "conflict" ? 0.3 : 0)
  + (item.stale === true ? 0.15 : 0);
```

So the states that withhold a memory are the deletion states, and the states that express doubt are ranking adjustments. The mechanism for filtering on status exists, is used, and is pointed at the deletion end of the vocabulary — a record the system has marked `conflict` outranks a `candidate` record about anything sufficiently on-topic.

**Which copy of a record the scorer sees is itself a design decision here, and it is the one that makes the rest of the vocabulary mean anything.** The JSONL stores are append-only event logs: `transitionRecordStatus` appends a fresh line under the same id rather than replacing the old one, so a record that has moved to `demoted` exists on disk twice, once in each state. `routeNeoRecall` (`lib/neo-arch.js:1419`) deduplicates by id and keeps the **newest revision**, ordered by `updatedAt` — the field a transition sets — while preserving first-appearance order so the `itemIndex` tiebreak below stays stable. The helper that dates a revision, `neoRevisionTimeMs` (`:1412`), carries a note on why the existing `recordTimeMs` will not serve: it reads `startTime`/`createdAt`, which are identical across every revision of one record, so it cannot tell two revisions apart. An undated record sorts to `-Infinity` so any dated revision beats it and the comparison never lands on `NaN`.

Read against an append-only store, that is not a detail. Keeping the first line seen means scoring the record as it was *before* the transition, which would apply the `active` arithmetic to a record a person had just demoted — and a status penalty computed against the wrong copy is not a weakened penalty, it is no penalty. `tests/neo-status-transition-dedupe.test.js` fixes the arithmetic to a number: `active=0.371` against `demoted=-0.116` at a live `minScore` of `0.08`, so the two copies fall on opposite sides of the admission threshold.

The rendered line carries the status the penalty was computed from. `formatNeoRecallContext` emits `lane`, `category`, `trust`, `id`, `score` and `status` on each `<memory-record>`, which matters because the memory prompt supplement tells the model to prefer `active` and `promoted` over conflicting cards — an instruction that can only be followed if the distinction is in the payload.

One state transition is not epistemic at all and is worth naming here because it protects the whole loop. Text that PLUR1BUS itself injected into a prompt — recall blocks, temporal context, status reminders, cron output — is matched against a marker list and refused as a capture candidate (`isInjectedContextText`, `lib/neo-arch.js:176`, applied at `neo-arch.js:1199` and `:1242`). Without it, recall output becomes next turn's memory, which the comment above the marker list dates to a performance analysis on 29 May 2026.

```mermaid
stateDiagram-v2
  [*] --> candidate: agent_end capture
  candidate --> active: written to LanceDB
  active --> promoted: person runs promote
  active --> demoted: person runs demote
  active --> conflict: contradiction detected
  active --> superseded: safeUpdate writes v+1
  superseded --> [*]: dropped at recall-pipeline.js 137
  promoted --> pruned: person runs prune
  demoted --> tombstoned: person runs tombstone
  pruned --> [*]: score -Infinity
  tombstoned --> [*]: score -Infinity
  conflict --> conflict: ranked down 0.3, still injected
  demoted --> demoted: ranked down 0.35, still injected
```

## 3. Architecture

An OpenClaw v6 plugin, loaded from `index.js`, requiring Node ≥ 22.5 and a running OpenClaw gateway. Nothing else has to be stood up: LanceDB is embedded, the neo store is JSONL on disk, and the caches use the `node:sqlite` module built into Node rather than a dependency.

- **`index.js`** (9,292 lines) — plugin entry, hook registration, chat commands, and the wiring between every subsystem below.
- **`lib/`** (206 files, 54,781 lines) — `recall-pipeline.js` (1,903), `neo-arch.js` (2,356), `obsidian-control-room.js` (3,918) and `obsidian-bridge.js` (2,035) dominate; `safe-update.js`, `acl-middleware.js`, `memory-history.js` and `contradiction-detector.js` carry the correction path.
- **`lib/jobs/`** — fifteen background jobs: daily consolidation, garbage collection, conflict resolution, skill mining, critical-push classification, memory compaction, reflection.
- **`lib/dreaming/`** — `light-dream.js`, `rem-dream.js`, `dream-narrative.js`.
- **`patches/apply-cron-plugin-direct-dispatch.mjs`** — see below.

**Storage.** LanceDB tables per agent under `{baseDbPath}/{agentId}/` (`lib/db-adapter.js:312`), so agent isolation is a directory boundary before it is a query filter. Alongside: eleven JSONL files and four JSON files per workspace in the neo store, an optional SQLite embedding cache and LLM result cache, and an optional Obsidian vault the bridge keeps in sync as Markdown.

**Retrieval stack.** Vector search over LanceDB with a lexical fallback when the embedder is not ready, graph hydration of neighbouring cards (`hydrateGraphResults`, `recall-pipeline.js:816`), and two additive passes — a precomputed semantic lens and conversation reactivation — that append to a recall result and, per `AGENTS.md`, must never replace it. Both are off by default and both carry a 50 ms hard timeout.

**Embeddings** come from OpenAI or an optional local `@huggingface/transformers`. A key is not required to store a memory: the adapter falls back to text search when embedding fails.

### Deployment and ergonomics

Install is `npm install` into an OpenClaw installation, and this is where an operator should look before anything else. `package.json` declares:

```json
"postinstall": "node scripts/setup-feature-crons.mjs || true"
```

That script does not only register cron jobs. Before reading or mutating any cron it calls `applyCronPluginDirectDispatchPatch`, which resolves the *host's* OpenClaw dist directory and patches it, because the plugin needs a dispatch path the host does not offer. The script's own header states the contract — it must never fail an install, and it exits 0 whatever happens — so a patch of another package's installed code happens during `npm install`, best-effort, and reports success either way. It is not concealed: the file is 300 lines of readable planning code, it is listed in `package.json`'s `files`, and `tests/cron-plugin-direct-dispatch-patch.test.js` covers it. It is still a memory plugin editing its host at install time.

The store is human-readable and repairable by hand: JSONL and Markdown for everything except the LanceDB tables, which is a real operational advantage when a background job has done something unexpected. `scripts/repair-installed-plugin.mjs` and `lib/memory-doctor.js` exist for when it has.

## 4. Essential Implementation Paths

### Capture — `index.js:6754`

`api.on("agent_end", …)` hands the turn to `runtimeScheduler.enqueueCapture(agentId, …)` with an abort signal. Capture is per-agent queued and runs after the turn ends, so the model's reply is never waiting on it. Background turns are flagged and treated differently, which is what stops a cron-triggered agent run from writing memories about itself.

### Correction — `lib/safe-update.js:246`

The most carefully built path in the repository, in order:

1. **Refuse non-active rows.** A superseded memory cannot be updated; the chain only grows at the leaf.
2. **Validate the ownership tuple** before any read or write, requiring the binding that the row's own scope demands.
3. **Demand evidence.** `validateUpdatePatch` throws unless a text or summary change carries both `evidence.updateSource` and `evidence.updateEvidence`.
4. **Check idempotency** — a SHA-256 over id, source, evidence and the patched fields, looked up in the reconsolidation event log, so a retried correction is a no-op rather than a second version.
5. **Demand a new vector.** A text change without `patch.vector` throws: *"The embedding must reflect the new content."* This closes the failure where a corrected memory keeps ranking under the old text's query.
6. **Gate on semantic drift** (`safe-update.js:355`) — cosine distance over 0.45 is rejected outright.
7. **Store the new version first, supersede second** (`:373`, `:377`). The comment is worth reading in full: storing first means a crash leaves both versions active — "a recoverable fork, never a loss" — whereas superseding first would point the old row at an id that was never written.
8. **Rewrite graph edges** onto the new id, then **append the event** with the action, the source, the evidence, the confidence and the measured drift.

### The drift gate's only caller — `index.js:6422`

`/correct <old> to <new>` runs a confirmation token exchange, then calls `safeUpdate` with `updateSource: "telegram:/correct"`, an evidence string, and `skipDriftGate: true`. Every other reference to `skipDriftGate` in the tree is in a test, so the gate does not run in production.

The reasoning sits at the call site rather than in a commit message: `/correct` is a nonce-confirmed user action, the confirmation dialog shows old and new text in the clear, so high semantic drift there is intended and consented to, and the gate would block a legitimate large correction with an exception rather than a warning. The drift is still computed and written onto the reconsolidation event as `semanticDrift`, so switching the gate off costs the measurement nothing.

What remains is that the gate guards nothing else: the automated bulk paths that would most benefit from it — consolidation, dreaming, conflict resolution — do not call `safeUpdate` at all. A threshold whose only caller has reasoned its way out of it has no live consumer.

The confirmation dialog is the part worth copying. Target resolution is fuzzy — candidates are resolved without a minimum score, and "unambiguous" means only that the top match beats the second by more than 0.15 — while `safeUpdate` replaces the entire text. A prompt naming an 80-character title cannot tell a user which memory they are about to overwrite, so it renders the stored text and the replacement at 300 characters each. The same value carries into provenance: `payload.oldText` holds the stored content being replaced rather than the search term that found it, and `updateEvidence` builds its evidence line from that.

### Scope — `lib/acl-middleware.js:103`

`checkAccess(ctx, memory)` returns `{allowed, reason}` and denies with a stable reason code on: no context, no memory, an unknown scope value, a requester with no agent id, an invalid or conflicting ownership tuple, a private row with no owner, a workspace row with no workspace, and a user row whose principal is not a `user:v1:<sha256>` string. Every path that is not an explicit match is a denial.

It is applied on the read path at `lib/db-adapter.js:361`, `:454` and `:474` (query, search, get), at `lib/recall-pipeline.js:173`, in the shared-memory pool, the wiki command, both dream passes, and the Telegram query and edit commands. `filterMemoriesByAcl` (`:226`) is the batch form, with optional violation logging to `acl-audit.jsonl`.

Note that two scope vocabularies coexist: the ACL's `agent-private | workspace | user` and the neo store's `agent_private | workspace_shared | global_user`, reconciled by `normalizeNeoScope`. Neo records are filtered by `isNeoRecordAccessible` (`lib/neo-arch.js:1364`) rather than by `checkAccess`, and the comment at `neo-arch.js:1704` is candid about the limit: dreams, episodes, graph edges and patterns carry no scope field at all, so passing a requester to those readers would filter every record to nothing rather than filter correctly, and the reader was deliberately left unscoped instead.

### Status transitions, and a dedupe key that had to be designed

The neo store is append-only JSONL with an id index, and appends are deduplicated. That creates an obvious hazard: `transitionRecordStatus` returns the same record with a new status and the *same id*, so an id-keyed dedupe would silently swallow every promotion. It does not, and the reason is three small functions at `lib/neo-arch.js:2007`:

```js
function appendDedupeId(record) {
  if (!record || typeof record !== "object" || !record.id) return "";
  if (record.updatedAt || record.embeddingUpdatedAt) return "";   // a mutated record always appends
  return String(record.id);
}

function recordStatusTransitionDedupeKey(record) {
  if (!record || typeof record !== "object" || !record.id || !record.updatedAt) return "";
  const status = normalizeNeoStatus(record.status, "");
  if (!status || status === "candidate") return "";
  return `status:${record.id}:${status}:${record.updatedAt}`;
}
```

A transition is keyed on the transition, not on the content, so it is never mistaken for a duplicate; a candidate is never deduplicated at all. The residual gap is millisecond-wide: two transitions to the same status within the same `updatedAt` collapse into one.

### Recall

`lib/recall-pipeline.js` runs lifecycle filtering, ACL filtering, namespace merge with canonical-content dedupe, importance boost, Jaccard dedupe at 0.78, and graph hydration, emitting a decision trace throughout (`lib/recall-decision-trace.js`) and a retrieval ledger entry per query. `/memory <query> --explain` renders the trace back to the user, so "why was this memory shown" is answerable without reading logs.

### Tests covering the behaviour

`tests/crr-status-filter.test.js` is the sharpest one: it constructs a superseded and an active memory with identical text, runs the reactivation selector, and asserts the superseded one is absent from the block that gets injected into the prompt. The header names the regression it locks — reactivation reached the semantic lens without a status filter, so a corrected memory could resurface as current evidence.

## 5. Memory Data Model

A LanceDB card, from `buildUpdateEntry` (`lib/safe-update.js:79`), carries roughly fifty fields. The ones that matter:

- **Identity and lineage** — `id`, `versionNumber`, `previousVersion`, `supersededBy`, `status`, `versionCreatedAt`.
- **Provenance** — `sourceTurnId`, `sourceMessageRole`, `sourceTimestamp`, `sourceUrl`, `evidenceQuote`, `updateSource`, `updateEvidence`, `reconsolidationConfidence`. This is typed provenance in columns, not a metadata blob, and it is the part most systems in this atlas skip.
- **Ownership** — `agentId`, `storedBy`, `workspaceId`, `workspaceKey`, `scope`, `ownerUserId`.
- **Dynamics** — `importance`, `memoryStrength`, `halfLifeDays`, `lastStrengthenedAt`, `retrievalCount`, `lastRetrievedAt`, `replayCount`, `memoryClass`, `neverForget`, `coreMemoryScore`.
- **Affect** — `emotionalValence`, `emotionalIntensity`, `emotionalDominant`, `moodContextAtCapture`.

`neverForget` and `memoryClass: "core"` are honoured by the garbage collector (`lib/garbage-collector.js:87`), which is a small thing that many decay implementations forget: a decay curve with no pin will eventually reach the memories the user cared most about.

What is absent:

- **No bi-temporal axis.** `createdAt`, `versionCreatedAt`, `updatedAt` and `sourceTimestamp` all record when the *system* did something. Nothing records when the fact was true, so "what did we believe last March" and "where did I live last March" are the same query.
- **No rejected-value tombstone.** `/forget` archives a card and `tombstone` sets a neo record's status; both are keyed on a record. Re-capturing the same sentence produces a new card that nothing checks against what was rejected. The `tombstoned` status is the closest thing in the corpus to the mechanism by name while being the record-keyed kind the [rejected-value tombstone](../../patterns/rejected-value-tombstone/) pattern explicitly excludes.
- **No scope on the derived records.** Dreams, episodes, graph edges and patterns are unscoped, as the code says.

## 6. Retrieval Mechanics

Automatic injection on the turn, plus explicit `/memory` and `plur1bus_recall` tool access.

Ranking blends vector similarity, lexical overlap, the importance boost, category lane matching, and the trust and status arithmetic quoted in section 2. Results are deduplicated twice — by canonical content key across namespaces, then by Jaccard similarity at 0.78 — which matters in a system that keeps every version of a memory, because a v3 and a v4 of the same fact are near-identical text.

Two additive passes sit after primary recall and are architecturally constrained rather than merely documented: the semantic lens reads a precomputed index and appends community, bridge and faded memories; conversation reactivation appends a `<memory-reactivation>` block on an idle gap or after compaction. Both cap their output (three memories, one faded, three open threads), both time out at 50 ms, both fall back to the unmodified base recall, and neither writes anything.

The failure mode to watch is over-recall by construction. Base recall, plus graph hydration of neighbours, plus lens, plus reactivation, plus temporal context, plus emotional state, plus persona voice all target the same prompt. The caps are per-feature and there is no global token budget across them.

`lib/temporal-provenance.js` is the interesting counterweight and is unusual enough to name. It classifies a recalled memory by age and by whether its content is *operational* — cron, systemctl, deploy, gateway, migration — and by destructive keywords, then decides whether the agent must verify live before acting on it. A memory that a cron job is disabled is treated as a fact about the past rather than the present after fifteen minutes. That is the right shape for the class of memory that gets an agent into trouble, and no other system in this atlas conditions action on the age of the specific memory being acted upon.

The guard is only as good as the timestamp reaching it, and the timestamp is produced by the mapping layer rather than by the store. Canonical hits from `KNOWLEDGE.md` carry no `createdAt` of their own and take the file's mtime as their age, and they are marked `authoritative` and exempted from the operational guard on the reasoning that a canonical document is the reference something else is verified *against*. Semantic-lens hits copy `createdAt`, `updatedAt` and `lastRetrievedAt` off the underlying entry, and the reactivation block renders age and freshness rather than omitting them. `parseMemoryTimestamp` discards a value outside the representable `Date` range the way it discards a missing one, which keeps `buildTemporalProvenance` from throwing a `RangeError` and taking the whole recall rendering with it — the age label is therefore always `unknown` or `<n>[mhd] ago`, which is what the reactivation renderer assumes.

## 7. Write Mechanics

Writes are created by the `agent_end` capture, by explicit tool and command use, by the Obsidian bridge importing vault edits, and by background jobs.

**Conflict handling** is split. `lib/contradiction-detector.js` asks an injected LLM whether two interpretation overlays of the same memory are mutually incompatible and persists findings to `contradictions.jsonl`; `lib/memory-text-contradiction.js` and `lib/jobs/conflict-resolver.js` cover the card text. The output is a `conflict` status and a listing under `/plur1bus curation conflicts` — a queue for a person, not a resolution.

**Malicious input** is filtered at capture. `PROMPT_INJECTION_RE` (`lib/neo-arch.js:103`) matches the familiar overrides plus chat-template delimiters, and a turn marked `quality.promptInjectionSuspected` is excluded from the recallable set at `neo-arch.js:1242`. The injected-context marker list discussed in section 2 closes the self-capture loop. `lib/relevant-memory-context.js` prepends a recall safety preamble telling the model that memory content is data.

### Operational cost

- **The write path is deferred.** Capture runs after `agent_end` through a per-agent scheduler; the agent never blocks on extraction.
- **The lag before a memory is retrievable** is capture-queue depth plus an embedding round-trip, and it is not measured anywhere in the repository. Embeddings are queued through `embedding-queue.jsonl` and drained by a cron, so a memory can be lexically retrievable before it is vector-retrievable — an interval nothing bounds.
- **Background passes rewrite broad slices of the store.** Daily consolidation, memory compaction, memory-dynamics maintenance, GC, skill mining, REM dreaming (weekly) and light dreaming each read and write in bulk, and their token bill scales with the corpus rather than with the day's traffic. Most default off; `scripts/setup-feature-crons.mjs` registers only those explicitly enabled.
- **Read-path injection is bounded per feature and not in aggregate.** Recall blocks, temporal context, reactivation and emotional state each carry their own cap. All of them are injected as a per-turn prefix, which will invalidate a provider's prompt-prefix cache on every turn in which any of them changes.

## 8. Agent Integration

The plugin registers commands (`/memory`, `/forget`, `/correct`, `/state`, `/enable`, `/disable`, and a `/plur1bus` namespace covering curation, memory, behaviour, dreaming, skills and reminders), an `agent_end` hook, gateway start/stop lifecycle hooks, and MCP-style tools for explicit recall.

The model has moderate agency: it can recall explicitly and capture happens for it, but promotion, demotion, pruning and tombstoning are authorized human commands. The destructive ones check `checkAuth(..., { destructive: true })` first, and `/forget` requires a confirmation token issued by a prior call.

The Obsidian bridge is the second integration and the more unusual one. Memory is mirrored into a vault as Markdown, a person edits or annotates it there, and the bridge syncs changes back — under an explicit stance stated at the top of `lib/obsidian-control-room.js`: PLUR1BUS stays authoritative, vault text is untrusted input, and apply never mutates memory without explicit approval plus immediate revalidation. Deleting a vault file does not delete a memory; it raises an `approval_required_tombstone` action (`lib/obsidian-bridge.js:1528`).

Adapting this to another agent host would be substantial work. The plugin is written against OpenClaw's plugin API, its cron dispatch, its agent workspace resolution and its command registration, and one of its install steps patches that host.

## 9. Reliability, Safety, and Trust

Strengths:

- **Correction demands evidence** — a source and a quote — and refuses a text change without a matching new embedding.
- **Write ordering is reasoned about explicitly**, with the crash window named in a comment and resolved in favour of a recoverable fork.
- **Idempotent corrections** via a hash checked against the event log.
- **An append-only reconsolidation event log** carrying action, source, evidence, confidence and measured drift.
- **A fail-closed ACL** on the read path, whose tests assert denials.
- **Recall output cannot become capture input**, closing a feedback loop the project traces to a dated performance analysis.
- **Prompt-injection suspicion excludes a turn from recall**, rather than only logging it.
- **Age-conditioned action guards** for operational memories.
- **Pins survive decay** — `neverForget` and `memoryClass: core` are honoured by the GC.
- **A repairable store** — JSONL and Markdown, plus a doctor and a repair script.
- **The scorer reads the newest revision of an append-only record**, so a status a person set is the status the ranking arithmetic uses.
- **A correction dialog that shows what it will overwrite**, at 300 characters of old and new text, against a target resolved by fuzzy match.

Gaps:

- **Doubt does not withhold.** `conflict`, `demoted` and `untrusted` are ranking penalties rather than filters. The system can record that it does not believe something and still put it in the prompt, labelled with the status, which moves the decision to the model.
- **The drift gate is off** wherever it could fire, by a reasoned choice that leaves the threshold with no live consumer.
- **No bi-temporal axis**, so correcting a fact destroys the ability to audit the period when the wrong value was in force.
- **No value-level tombstone**, so a forgotten fact returns if it is said again.
- **Derived records are unscoped** — dreams, episodes, graph edges, patterns — and the code says the reader was left unfiltered rather than filtering everything to nothing.
- **`postinstall` patches the host** and is contractually unable to fail.
- **A prompt-facing value can be produced by four different mapping paths**, and correctness has to be established at each one rather than at the store.
- **The feature surface is the risk.** Forty-seven config groups, fifteen background jobs and two dream passes over one memory store means the number of paths that can write to a card is large, and only one of them goes through `safeUpdate`.

## 10. Tests, Evals, and Benchmarks

**I ran three test files and installed nothing.** The screen flagged both `package.json` and `package-lock.json` as changed within the seven-day cooldown, so nothing was installed — but `npm test` needs no framework, and the three regression files added since the previous pin import only node builtins and in-tree modules. `node --test tests/neo-status-transition-dedupe.test.js tests/correct-informed-consent.test.js tests/recall-temporal-provenance-gaps.test.js` reports **27 passing across 7 suites, 0 failing**. I then took a scratch copy, restored `lib/neo-arch.js` from the previous pin, and re-ran the first file: **5 of its 7 tests fail**, which is the negative control for the deduplication rule described in section 2 and confirms the tests discriminate rather than merely pass. The rest of the suite was not run, because the files that import `@lancedb/lancedb` need an install this screen refuses.

317 test files under `tests/` and `test/` — larger than the implementation. `npm test` is `node --check` on three modules followed by `node --test` over both directories, so there is no framework dependency to install.

What is covered, by name: ACL call-site adapters and ownership binding, shared-memory recall and the share store, sensitive-read authorization, `safe-update` data loss, the DB adapter's `updateCard` data loss, dedupe and status-filter regressions, contradiction detection across four files, the embedding cache, the LLM result cache, cron bootstrap and the direct-dispatch patch, GC's `neverForget` guard, Obsidian command gating, vault confirmation, review authority, and zero-mutation guarantees.

The negative assertions are real and specific. `tests/crr-status-filter.test.js` asserts a superseded memory must not reach the reactivation block. `tests/b13-acl-callsite-adapters.test.js` asserts that an unbound private row, a conflicting ownership tuple, and a raw user id in place of a canonical principal all fail closed. `tests/gc-neverforget-guard.test.js` asserts pinned memories are not archived.

What is missing is quality measurement. There is no retrieval-quality eval, no benchmark harness, and no committed result for any of it — which for a system whose ranking function sums seven weighted terms means the weights in `scoreNeoRecallItem` are unvalidated by anything in the repository. **No paper, arXiv reference or citation file exists in this tree**; the documentation is a 51 KB README, an 87 KB changelog, and a 97 KB `how-to-memory-perfect.md`.

`tests/neo-status-transition-dedupe.test.js` is worth reading for its shape as much as its subject: it pins the arithmetic to numbers — `active=0.371` against `demoted=-0.116` at a live `minScore` of `0.08` — so the assertion is about which side of the admission threshold each copy falls on, not about an ordering that a weight change would silently invert.

The test I would want before trusting this in production is the one nothing here contains: assert that a memory the user has corrected does not come back after a consolidation pass and a dream pass have run over the store.

## 11. For Your Own Build

### Steal

- **Require evidence for a content change.** A source and a quote, validated at the function boundary, turns "the model decided to update this" into a record you can audit later. It costs two required arguments.
- **Require a new embedding with new text.** A corrected memory that keeps its old vector ranks under the old query forever, and nothing about it looks wrong.
- **Store the replacement before superseding the original**, and write down why. The crash window is real, the comment at `safe-update.js:368` is the artifact, and the resulting failure — both versions active — is one a person can fix.
- **Key an idempotency hash on the correction, not the record**, so a retried correction cannot fork a version chain.
- **Make recall output unrecapturable.** Marker-match your own injected blocks and refuse them as candidates. The failure this prevents is a store that inflates on its own output.
- **Condition action on the age of the specific memory.** For operational facts — a service state, a deploy, a cron — "recalled and recent" is a different authorization than "recalled".
- **Design the append-key before making a log append-only.** A status change carries the same id as the record it changes; an id-keyed dedupe would eat it silently.
- **Pin memories out of decay.** A `neverForget` flag the GC honours costs one condition and saves the memories a decay curve is worst at keeping.

### Avoid

- **Discrete trust states wired to a score.** If `conflict` is a 0.3 penalty, the system cannot refuse to act on a contradiction — it can only be slightly less enthusiastic. Decide which states filter and which rank, and make the filtering ones filter.
- **A safety gate whose only caller disables it.** The disabling may be right — an explicitly confirmed user correction outranks a cosine distance — but a threshold with no live consumer is a threshold nobody is maintaining. Either give it a caller or record, at the call site, why it has none.
- **Deduplicating an append-only log by first appearance.** If a state change appends rather than replaces, the first copy is the pre-change one, and every consumer that keeps it is reading the record as it was before the decision. Pick the newest revision by a field the transition actually sets, and check that the field differs between revisions before relying on it.
- **Instructing a model to weigh a distinction your renderer omits.** A prompt supplement that says *prefer active over conflicting* needs the status in the payload; otherwise it is an instruction the model has no way to follow and no way to report it cannot.
- **Patching your host at `postinstall`.** However well-tested and however necessary, an install step that rewrites another package's shipped code — and cannot fail by contract — is a support burden and a supply-chain surface.
- **Per-feature injection caps with no global budget.** Seven bounded features can still fill a context window.

### Fit

This suits one specific reader: someone running OpenClaw for themselves or a small team, who wants a memory that grows and is willing to operate it. The feature surface assumes a maintainer who enjoys the surface — dreaming, emotional state, persona voice and an Obsidian vault are not incidental extras, they are most of the product, and someone who wants only "the agent remembers what I told it" will be configuring their way out of features for a while. Defaults help: most of the elaborate machinery ships off.

Walk away if you need multi-tenant guarantees. The read-path ACL is good, but derived records are unscoped by the code's own admission, background jobs write across the store, and the failure mode of a scope gap is unrecoverable. Walk away if you cannot accept a `postinstall` that patches your host.

The part worth taking whatever you are building is `lib/safe-update.js`. It is 414 lines, has one dependency on the rest of the system, and is the most complete answer in this atlas to "what does it take to change a memory without losing the old one".

## 12. Open Questions

- What is the lag between capture and vector-retrievability under a real embedding cron? Nothing in the tree measures it.
- Do the seven weights in `scoreNeoRecallItem` come from measurement or from judgement?
- Does a consolidation or dream pass ever resurrect the text of a corrected memory into a new card? No test asserts otherwise.
- How much does the full feature set inject per turn in aggregate, and at what point do the per-feature caps collectively exceed a sensible budget?
- Is the host patch upstreamed or proposed to OpenClaw, or does each release re-apply it?
- How many other prompt-facing fields are produced by more than one mapping path, and is there a check that all of them agree?

## Appendix: File Index

- Correction and versioning: `lib/safe-update.js`, `lib/memory-history.js`, `lib/memory-merge-safety.js`.
- Scope and access: `lib/acl-middleware.js`, `lib/memory-request-context.js`, `lib/security.js`, `lib/sql-safety.js`.
- Epistemic states, neo store, injection guards: `lib/neo-arch.js`.
- Retrieval: `lib/recall-pipeline.js`, `lib/recall-decision-trace.js`, `lib/semantic-lens-index.js`, `lib/conversation-reactivation-recall.js`, `lib/relevant-memory-context.js`.
- Storage adapter: `lib/db-adapter.js`, `lib/multi-namespace-pool.js`, `lib/shared-memory.js`.
- Contradiction and overlays: `lib/contradiction-detector.js`, `lib/memory-text-contradiction.js`, `lib/interpretation-overlay.js`, `lib/overlay-generator.js`.
- Decay, GC and dynamics: `lib/memory-dynamics.js`, `lib/garbage-collector.js`, `lib/temporal-provenance.js`.
- Human surfaces: `lib/obsidian-control-room.js`, `lib/obsidian-bridge.js`, `lib/obsidian-mutation-policy.js`, `lib/obsidian-review-authority.js`, `lib/telegram-commands/`.
- Background work: `lib/jobs/`, `lib/dreaming/`, `lib/runtime-scheduler.js`.
- Install-time host patch: `scripts/setup-feature-crons.mjs`, `patches/apply-cron-plugin-direct-dispatch.mjs`.
- Tests cited: `tests/crr-status-filter.test.js`, `tests/b13-acl-callsite-adapters.test.js`, `tests/gc-neverforget-guard.test.js`, `tests/safe-update-dataloss.test.js`.

## History

**2026-08-11** — [`3efedcd4179f6e5594229b7a52f2ca8a6e234d9a`](https://github.com/Cyb3rb1ade/openclaw-plur1bus-memory/commit/3efedcd4179f6e5594229b7a52f2ca8a6e234d9a) — second reading the same day, at release 7.2.6, twelve commits past the first pin. Screened again before reading: 0 auto-run surfaces, the same `postinstall`, both manifests inside the cooldown; nothing was installed. Three regression files were executed with `node --test` and pass (27 tests); restoring `lib/neo-arch.js` from the previous pin on a scratch copy fails 5 of 7 in the dedup file.

**A published claim was wrong, and wrong in the system's favour.** This report stated that a record marked `conflict` or `demoted` was ranked down by 0.3 and injected anyway. The penalty was not being applied at all. The JSONL stores are append-only, so `transitionRecordStatus` appends a second line under the same id; `routeNeoRecall` deduplicated by first appearance and therefore scored the pre-transition copy, with its `active` status. [`20cf0fe79c03d13a9d4ce18e9e9a807a76232b9e`](https://github.com/Cyb3rb1ade/openclaw-plur1bus-memory/commit/20cf0fe79c03d13a9d4ce18e9e9a807a76232b9e) changes the deduplication to keep the newest revision by `updatedAt`, preserving first-appearance order so the tiebreak stays stable. The error in this report was one of mechanism rather than of outcome — the observable behaviour was as described — and it came from reading the scorer without reading what the scorer is handed.

The same commit renders `status` on each `<memory-record>` line, closing a gap this report did not find: the memory prompt supplement instructs the model to prefer `active` and `promoted` over conflicting cards, and the template emitted lane, category, trust, id and score but not status, so the instruction asked for a distinction the payload did not carry. The reading that would have caught it is one this report did not perform — checking every distinction a prompt instruction demands against the fields the renderer actually emits.

It also corrects `/correct`. The confirmation dialog named an 80-character title while `safeUpdate` replaced the full text against a fuzzily-resolved target, and `payload.oldText` carried the user's search term rather than the stored content, so `updateEvidence` recorded the query instead of the value it replaced. Both are fixed, and `skipDriftGate` is retained with its rationale written at the call site. That answers the open question this report carried about why the gate is disabled.

[`35852e8e5db32e588456d50643c2b10d55e15509`](https://github.com/Cyb3rb1ade/openclaw-plur1bus-memory/commit/35852e8e5db32e588456d50643c2b10d55e15509) repairs the timestamps the operational guard depends on: canonical `KNOWLEDGE.md` hits carried no age and, containing operational keywords, permanently demanded live verification; they now take the file mtime and are marked `authoritative` and exempt. A probe over the live namespaces is recorded in that commit as 25,550 rows with none missing `createdAt`, placing the defect in the read path's mapping layer rather than in the store.

The unreferenced `plur1bus/` directory described in the previous entry is deleted. Its `index.js` imported `./lib/categorize.js`, which never existed inside that directory, so the copy could not have run.

**2026-08-11** — [`241aac282e20c40819bdfffef0f9ce7115abd936`](https://github.com/Cyb3rb1ade/openclaw-plur1bus-memory/commit/241aac282e20c40819bdfffef0f9ce7115abd936) — first reading, at release 7.2.3. Screened before reading: 0 auto-run surfaces, 1 build-time exec (`postinstall` runs `scripts/setup-feature-crons.mjs`, which patches the host OpenClaw dist directory), 1 unpinned manifest, and both `package.json` and `package-lock.json` changed inside the seven-day cooldown; nothing was installed and nothing was executed.

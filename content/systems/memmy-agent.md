---
title: "Memmy"
eyebrow: "One local memory, injected into every agent"
description: "A local-first SQLite memory hub from the MemOS team that distills a layered L1→L2→L3→Skill store from every connected agent's turns, shares it across Claude Code, Codex, Cursor and others through one daemon plus an injected per-agent CLI skill, and induces anti-pattern 'avoid' policies from failures."
root: ../..
page_kind: system
source_name: "MemTensor/memmy-agent"
source_url: https://github.com/MemTensor/memmy-agent
revision: c6cdbf9a126cc297253783c5594ac5ee8acb7c1a
revision_url: https://github.com/MemTensor/memmy-agent/commit/c6cdbf9a126cc297253783c5594ac5ee8acb7c1a
analyzed_at: 2026-08-15
capabilities: "tombstone, trust_state, audit_log, negative_eval"
stack_storage: "sqlite"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A layered structured note — a MemoryRow with memory_type, status, visibility, key/value, tags, a memory_layer (L1 trace, L2 policy, L3 world-model, Skill), a content_hash and a version — with vectors in a sidecar table"
  storage: "One local SQLite database at ~/.memmy (better-sqlite3) with an FTS5 mirror and a sqlite-vec vector sidecar; local embeddings; an optional opt-in hosted OpenMem/MemOS cloud backend that is not the default"
  retrieval: "Hybrid multi-channel — vector (sqlite-vec over summary/action/content), FTS5 lexical, plus pattern and structural routes fused by per-channel max score, with LLM multi-query rewrite; filtered by layer, status and tags"
  write: "Turns ingest into raw_turns/episodes; a background evolution pipeline distills L1 traces, induces L2 policies (candidate pool + similarity dedup), abstracts L3 world models and mines Skills, all by LLM prompts"
  update_delete: "Soft-delete (status=deleted, deleted_at) and archive; import conflict strategy skip/replace/error; a negative-experience pipeline synthesizes anti-pattern avoid policies keyed on a failure signature; content_hash dedup"
  scoping: "Scope keys (user/agent/app/session) exist and episode reads assert scope, but the primary semantic recall filters only layer/status/tags — cross-agent pooling is deliberate, so recall is shared across agents"
  integration: "One local HTTP daemon (127.0.0.1:18960) plus an injected per-agent CLI skill written into ~/.claude, ~/.codex, ~/.cursor, ~/.openclaw and ~/.hermes so every agent reads and writes the same store; a CLI, not MCP"
  background: "An evolution job pipeline (evolution_jobs + workers) consolidates, dedups and promotes memories up the layers and mines skills and anti-patterns — this is what 'self-evolving' means in code"
  trust: "A discrete status (activated/resolving/archived/deleted) consumed on read — recall filters to activated and resolving; a resolving state is the candidate lifecycle; plus world-model confidence and skill-trial pass/fail"
  strengths: "A genuinely local layered memory shared across every connected agent through an injected CLI skill, with an LLM evolution pipeline that induces reusable policies and anti-patterns from experience, and append-only change and audit logs"
  risks: "The shared brain has no scope on its main recall — every agent's memory pools into one and cross-agent isolation is deliberately absent; audit and change logs are retention-pruned; 'MemOS-powered' is lineage and branding, and a hosted cloud backend is one config flip away"
---

## 1. Executive Summary

Memmy — `memmy-agent` from MemTensor, the team behind MemOS — is a personal AI
agent and, more interestingly for this atlas, a **local memory hub** meant to be
shared across every coding agent a person uses: Claude Code, Codex, Cursor,
OpenClaw, Hermes. The claim is that these one-shot tools should build on each
other's context instead of starting over, and the mechanism is concrete and
distinctive. The durable memory is a real, local SQLite engine — the `@memmy/memory`
package, ~44,000 lines of TypeScript — with an FTS5 mirror, a `sqlite-vec` vector
sidecar, and local embeddings; the shipped default is `byok`/`local`/`sqlite`, so
the whole engine runs on the machine and is present in the repo, not behind a
service (`Memory/src/config/index.ts:252-255`, `storage/backend.ts:111-123`).

Two design choices make it worth a report. The first is **how it is shared**. One
local HTTP daemon (`127.0.0.1:18960`) holds the single SQLite store, and Memmy
*installs a per-agent skill* into each agent's config directory —
`~/.claude` (as `CLAUDE.md`), `~/.codex`, `~/.cursor`, `~/.openclaw`, `~/.hermes`
(`Memory/src/cli/skill-writer/index.ts:161-174`) — that teaches each agent to call
the `memmy-memory` CLI, which hits the shared daemon. Every connected agent reads
and writes the *same* SQLite store, tagged by `--source <agent>`. That is the
"unified memory across agents" realized as an injected CLI skill plus a shared
daemon, and it is a genuinely different integration shape from the MCP servers
elsewhere in this corpus.

The second is **what it stores and how it grows**. A memory is a layered structured
note — `L1` a trace, `L2` an induced policy or preference, `L3` a world-model
abstraction, `Skill` a procedure — and "self-evolving" is a concrete background
pipeline (`evolution_jobs` plus workers) that distills L1 traces, induces L2
policies from repeated traces through a candidate pool with similarity dedup,
abstracts L3, mines skills, and — the part the atlas rewards — runs a
**negative-experience pipeline** that synthesizes anti-pattern "avoid" policies
keyed on a failure signature and surfaces them on read as failure-avoidance
(`service/evolution/negative-experience-pipeline.ts:85,409`). That is a
rejected-value record in the induced-policy layer, and it earns `tombstone` with
the nuance that it applies to anti-patterns and rejected candidates rather than to
deleted user facts.

Memmy is its own system, not MemOS embedded: there is no `memos` dependency, the
engine is memmy's own TypeScript over SQLite, and "MemOS-powered" is lineage and
branding (plus an *optional* hosted OpenMem/MemOS cloud backend that is not the
default). It earns four marks — `tombstone`, `trust_state`, `audit_log`,
`negative_eval` — and its most important withheld one is the mirror of its headline
feature: because the shared brain **deliberately pools across agents**, the primary
recall applies no user/agent/project scope, so `scope_enforced` is withheld by
design, not omission. That trade — one shared memory, no isolation on the main read
— is the thing to weigh before adopting it.

## 2. Mental Model

A memory is a layered note that starts as a trace and is promoted upward by a
background pipeline; recall pools across every agent that shares the daemon.

```text
turns from any connected agent  -> raw_turns / episodes
evolution pipeline (background jobs):
  span-pipeline        L1: summarize traces
  policy-induction     L2: induce policies from repeated L1 (candidate pool + similarity dedup)
  world-model-pipeline L3: abstract world models (confidence-shaped)
  skill-pipeline       Skill: mine procedures
  negative-experience  anti-pattern "avoid" policy keyed on failure signature (merged, not duplicated)

recall (per agent, via CLI -> local daemon):
  vector (sqlite-vec) ∪ FTS5 ∪ pattern ∪ structural  -> per-channel max fuse -> rank
  filter: memory_layer, status IN ('activated','resolving'), tags   (NO user/agent scope)
  LLM multi-query rewrite -> failure-avoidance section injected from anti-patterns
```

The unit is a `MemoryRow` with a discrete `status` (`activated | resolving |
archived | deleted`) that the read path acts on, a `memory_layer`, a `content_hash`
for dedup and a `version`. The state that governs recall is the status — a
`resolving` row is the candidate lifecycle, and only `activated`/`resolving` are
returned — and the thing that makes the store "evolve" is the promotion of L1
traces into L2 policies and the induction of anti-patterns from failures.

```mermaid
%% caption: turns from every connected agent ingest into one local SQLite store; a background LLM pipeline distills L1 traces into L2 policies, L3 world models and skills and mines anti-pattern avoid policies from failures; recall fuses vector, FTS, pattern and structural channels across all agents with no scope filter on the main read
flowchart TB
    subgraph agents["Claude Code · Codex · Cursor · OpenClaw · Hermes"]
      CLI["injected memmy-memory CLI skill"]
    end
    CLI -->|"HTTP 127.0.0.1:18960"| D[("one local SQLite store<br/>~/.memmy (FTS5 + sqlite-vec)")]
    D --> Ev["evolution jobs (background)"]
    Ev --> L1["L1 trace"] --> L2["L2 induced policy<br/>(candidate pool + dedup)"]
    L2 --> L3["L3 world model"]
    Ev --> Sk["Skill"]
    Ev --> Neg["negative-experience:<br/>anti-pattern 'avoid' policy<br/>keyed on failure signature"]
    D --> R["recall: vector ∪ FTS ∪ pattern ∪ structural"]
    R -->|"filter: layer + status(activated/resolving) + tags<br/>NO user/agent scope"| Out["ranked hits + failure-avoidance section"]
    Neg -.->|"surfaced on read"| Out
```

## 3. Architecture

The memory core is the `Memory/` workspace (`@memmy/memory`); everything else is
shell and UI (`App/shell/desktop` Electron, `App/frontend/desktop` React,
`App/memmy-agent/src/memmy-memory` a thin HTTP client to the service).

- **`Memory/src/storage/`** — `schema.ts` (SCHEMA_VERSION 4), `db.ts` (SQLite at
  `~/.memmy/memory-service/memory.sqlite`), `backend.ts` (local sqlite vs the
  opt-in remote REST backend), `sqlite-vec-store.ts`, `repositories.ts` (4,990).
- **`Memory/src/service/`** — `memory-service.ts` (2,387), `retrieval/`
  (`indexed-candidate-pool.ts`, `retrieval-service.ts` 2,220, `query-rewrite.ts`),
  `evolution/` (span/policy-induction/world-model/skill/reward/negative-experience
  pipelines + `evolution-job-processor.ts`), `worker/`, `session/`, `namespace/`.
- **`Memory/src/model/embedder.ts`** — local `Xenova/all-MiniLM-L6-v2` via
  transformers.js by default.
- **`Memory/src/cli/`** — the `memmy-memory` CLI, the `skill-writer` that injects
  the per-agent skill, and `skills/memmy-memory/SKILL.md`.
- **`Memory/src/client/openmem-cloud-client.ts`** — the optional hosted backend.

**Storage.** One local SQLite database (`better-sqlite3`), FTS5 (`memories_fts`,
`unicode61`), and a `sqlite-vec` (0.1.9) vector sidecar (`memory_vector_entries`
with `vec_summary`/`vec_action`/`vec` and `embedding_model`/`provider`/`dim`),
plus supporting tables — `sessions`, `episodes`, `raw_turns`, `feedback`,
`decision_repairs`, `l2_candidate_pool`, `skill_trials`, `recall_events`,
`evolution_jobs`, `memory_change_log`, `audit_logs`, `idempotency_keys`. Runtime
deps are `better-sqlite3`, `sqlite-vec`, `@huggingface/transformers` — local by
default, no key required.

The optional cloud is worth stating precisely so it is not mistaken for the engine:
`RemoteRestStorageBackend` (`storage/backend.ts:74-109`, id `openmem-cloud-rest`)
delegates to MemTensor's hosted OpenMem service (`memos-api.openmem.net` /
`memos.memtensor.cn/api/openmem/v1/`), and its `repositories()` throws — it is an
alternate backend a user opts into, not the default and not present in the tree.

### Deployment and ergonomics

- **A shared local daemon plus injected skills.** Run the service; the CLI's
  skill-writer installs a `memmy-memory` skill into each agent's config dir so the
  agents call the CLI, which hits the daemon. This is the whole "one brain" story
  and it needs no MCP.
- **Local and offline by default.** SQLite on disk, local embeddings; the cloud
  backend is opt-in.
- The screen flagged FRESH manifests across the workspaces; nothing was installed
  or run, and the engine was read against 57 committed test files.

## 4. Essential Implementation Paths

- **Ingest** — turns normalized (`turn/turn-normalization.ts`) into `raw_turns`
  and `episodes` (`session/session-turn-service.ts`).
- **Evolve** — background `evolution_jobs` (schema.ts:487, unique `dedupe_key`)
  processed by `service/evolution/evolution-job-processor.ts`: `span-pipeline`
  (L1 summaries), `policy-induction` (L2 via `L2_INDUCTION_PROMPT`, `l2_candidate_pool`
  + `tracePolicySimilarity` dedup), `world-model-pipeline` (L3,
  `shapeWorldModelConfidence`), `skill-pipeline`, `negative-experience-pipeline`.
- **Anti-pattern** — `negative-experience-pipeline.ts:85`
  `policy:avoid:${stableHash(scope:signature)}` and `:409`
  `avoid:${stableHash(normalized)}`, merged into an existing policy via
  `decisionGuidance(..., "anti_pattern")`; surfaced through `failureAvoidanceSection`
  (`retrieval-service.ts:428-432`).
- **Retrieve** — `service/retrieval/indexed-candidate-pool.ts:90-137` runs
  `searchVectorIds` (sqlite-vec), `searchFtsIds` (FTS5), `searchPatternIds`,
  `searchStructuralIds` in parallel, fused by per-channel max in
  `algorithm/plugin-algorithms.ts`; LLM multi-query rewrite in
  `service/retrieval/query-rewrite.ts`.
- **Share** — `Memory/src/cli/skill-writer/index.ts:161-174` writes the skill into
  each agent's config dir; `SKILL.md` teaches the agent to call the CLI with
  `--source <agent>`; all hit `http://127.0.0.1:18960`.
- **Govern** — `memory-service.ts:1227` `deleteMemory` → soft delete;
  `:1171-1217` `archiveMemory`; `:1313` `redactRawTurn`; `repositories.ts:3286-3361`
  import conflict `skip|replace|error`.

## 5. Memory Data Model

A `MemoryRow` (`types.ts:99-131`, table at `schema.ts:24-47`) carries
`memory_type`, `status` (`activated|resolving|archived|deleted`), `visibility`
(`private|public|session`), `memory_key`, `memory_value`, `tags_json`, `info_json`,
`properties_json` (holding `internal_info.memory_layer/memory_kind`),
`memory_layer` (`L1|L2|L3|Skill`), `content_hash`, `version`, and
`created_at`/`updated_at`/`deleted_at`. Vectors are separate in
`memory_vector_entries`, stamped with the embedding model, provider and dimension —
so unlike some stores here a vector carries the space that produced it.

Three facts decide marks.

**Status is discrete and gates recall.** `activated`/`resolving`/`archived`/
`deleted` is a real lifecycle: a `candidate` maps to `resolving`
(`memory-service.ts:2183`), and the read paths filter `status IN
('activated','resolving')` (`indexed-candidate-pool.ts:41`,
`retrieval-service.ts:1493`, `read-model/skill.ts:313`). `trust_state` is earned —
a status field the store acts on, plus world-model confidence and skill-trial
pass/fail as adjacent signals.

**Rejected values are recorded and keyed on content.** The anti-pattern policies
are keyed on a `stableHash` of a failure signature and merged rather than
duplicated, and `l2_candidate_pool` carries an explicit `status='rejected'` keyed
on a `candidate_key` so a rejected candidate is not re-promoted (`schema.ts:229-241`).
This is `tombstone` in the induced-policy layer — a durable rejected-value record
that steers future behaviour away — with the honest nuance that it governs
anti-patterns and induction candidates, not deletion of user facts (a deleted fact
is a soft-delete, not a value-keyed rejection).

**There is no validity-time axis.** Only `created_at`/`updated_at`/`deleted_at` —
record time — so `bitemporal` is withheld.

## 6. Retrieval Mechanics

Recall is multi-channel and fused. Per layer, `indexed-candidate-pool` runs four
routes in parallel — vector cosine over the `sqlite-vec` sidecar (against
summary, action and content vectors), FTS5 lexical, a pattern route and a
structural route — and fuses them by taking the per-channel max score into a
combined ranking (`algorithm/plugin-algorithms.ts`), with an LLM multi-query
rewrite expanding the query first. Anti-pattern policies are injected as a
dedicated failure-avoidance section, so the store not only surfaces what worked but
warns against what failed.

The property that decides the withheld mark is the filter. The scope keys
(`user_id`, `agent_id`, `app_id`, `session_id`) all exist on the row and in
`MemoryFilter`, and episode reads assert scope (`retrieval-service.ts:1486`), but
the **primary semantic recall builds its filter from `{memory_layer, status,
tags}` only** (`indexed-candidate-pool.ts:85-93`) — no user, agent or project
predicate. This is deliberate: the whole point is one memory pooled across agents,
so recall crosses agents by design. `scope_enforced` is therefore withheld not
because the key is missing but because the main read intentionally does not apply
it — which is exactly the confidentiality trade a reader must weigh (§9).

## 7. Write Mechanics

Writes are two-phase and evolutionary. Turns ingest cheaply into `raw_turns`/
`episodes`; the durable, typed memories are produced asynchronously by the
evolution pipeline, so nothing blocks the agent's turn. The pipeline is the
"self-evolving" claim made concrete: L1 summaries from traces, L2 policies induced
from *repeated* L1 traces through a candidate pool with similarity dedup, L3
abstractions with a confidence-shaping step, mined skills, and the
negative-experience pass. Deduplication is real — `content_hash`
(`repositories.ts:3552`, `contentHash ?? stableHash(memoryValue)`) and the
`evolution_jobs.dedupe_key` unique index — so the store does not simply accrete
duplicates.

Correction and conflict are handled at several layers. A user (or the panel) can
soft-delete (`status='deleted'`, `deleted_at`; reads filter `deleted_at IS NULL`),
archive, or redact a raw turn; import carries a `skip|replace|error` conflict
strategy. The sharpest mechanism is the negative-experience pipeline: a failure
becomes an anti-pattern "avoid" policy keyed on its signature and merged into
existing guidance, and a rejected induction candidate is remembered as `rejected`
in the candidate pool so it is not re-promoted. So Memmy does record rejected
values — in the induced layer — which is more than most stores here manage, even if
a plainly deleted user fact is only soft-deleted rather than tombstoned by value.

Every governance mutation is logged: an `audit_logs` row on archive/delete/redact
(`memory-service.ts:1204-1213`) and an append-only `memory_change_log` with
before/after JSON (`repositories.ts:1930-1956`, `appendChange`). The one caveat for
`audit_log` is that both are subject to retention pruning
(`scheduleLogTablePruneAfterInsert`), so the trail is append-only but not
indefinite.

## 8. Agent Integration

The integration is the distinctive thing. Memmy is **not** an MCP server; it is a
local HTTP daemon plus an injected CLI skill. The skill-writer enumerates a fixed
set of supported agents (`SUPPORTED_MEMMY_AGENT_IDS = ["codex", "cursor",
"claude", "opencode", "openclaw", "hermes"]`, `cli/skill-writer/index.ts:6`) and
writes a `memmy-memory` skill into each one's config directory — into `~/.claude`'s
`CLAUDE.md`, into `~/.codex`, `~/.cursor`, and so on — teaching that agent to shell
out to the `memmy-memory` CLI, tagging its writes with `--source <agent>`. Every
agent therefore reads and writes the one SQLite store behind the daemon. This is a
clean answer to "how do five different coding agents share one memory" that sidesteps
MCP entirely, and it is the design's signature.

The consequence is the withheld scope mark read from the integration side: because
the point is a shared brain, the memories are pooled and the main recall does not
partition by which agent wrote them. `--source` records provenance; it does not
scope retrieval. For a single user that is the feature; for anyone who would run
distinct projects or trust boundaries through one daemon it is the risk.

`human_review` is withheld: there is a governance panel where a user can archive,
delete or redact, and an explicit `feedback` polarity, but there is no
approval queue adjudicating memory *content* before it is stored — candidate
promotion is automated by the evolution pipeline, not gated on a person.

## 9. Reliability, Safety, and Trust

- **Trust is a status the store acts on.** Recall filters to `activated`/
  `resolving`, so an archived or deleted memory does not surface, and the candidate
  (`resolving`) lifecycle is a real intermediate state — not a score the ranker
  ignores.
- **Failures are remembered as anti-patterns.** The negative-experience pipeline
  turns a failure into a durable, content-keyed avoid policy surfaced on read. That
  is the rejected-value discipline the atlas keeps asking for, applied to induced
  policies — a genuine strength.
- **Mutations are logged, with a retention caveat.** `audit_logs` and an
  append-only `memory_change_log` with before/after record governance ops in the
  system's own store; both are pruned by a retention job, so the guarantee is
  "append-only within the window", not forever.
- **The shared brain has no scope on its main read.** This is the load-bearing
  risk. Scope keys exist and the main semantic recall does not apply them, by
  design, so every connected agent's memory pools into one recall surface. A single
  user gets the intended benefit; anyone pointing multiple projects or trust
  boundaries at one daemon gets cross-contamination with only `--source` provenance
  to reconstruct who wrote what.
- **"MemOS-powered" is lineage, and the cloud is one flip away.** The engine is
  memmy's own TypeScript, not the MemOS package; but a `RemoteRestStorageBackend`
  can point the store at MemTensor's hosted OpenMem service, at which point the
  durable mechanism moves off the machine. The default is local; the option exists.

## 10. Tests, Evals, and Benchmarks

57 `*.test.ts` files under `Memory/tests/` cover the algorithm, repositories,
retrieval service, evolution pipelines, contracts, the embedder, config, the CLI,
and a local-vs-cloud parity suite. The relevant negative case is real:
`tests/service/retrieval/injected-context.test.ts:113-115` asserts that scanned,
unrelated and stale markers (`"…MUST_NOT_BE_INJECTED"`, `"STALE_FIRST_REPORT"`)
do **not** appear in the injected context — a committed must-not-retrieve
assertion, which earns `negative_eval`.

What is absent is a retrieval-quality benchmark: the multi-channel fusion, the
LLM query rewrite and the L1→L2→L3 induction are the design's substance, and while
the pipelines are unit-tested, nothing committed measures whether recall returns
the right memories or whether induced policies improve task outcomes — the
measurement the "self-evolving" claim most invites. MemTensor's MemOS has academic
papers; none is cited in this repository, and the "MemOS-powered" line is branding
rather than a citation.

## 11. For Your Own Build

### Steal

- **Share one memory across agents with a daemon plus an injected CLI skill.**
  Writing a small skill into each agent's config dir that shells to a CLI against a
  shared local service is a pragmatic, MCP-free way to give several coding agents
  one brain — and tagging writes with `--source` keeps provenance even when
  retrieval pools.
- **Remember failures as content-keyed anti-patterns.** Turning a failure into an
  "avoid" policy keyed on a failure signature, merged rather than duplicated, and
  injected as a failure-avoidance section, is a rejected-value mechanism that
  steers future behaviour — the useful half of a tombstone in the procedural layer.
- **Keep a `rejected` state in the induction candidate pool.** A rejected L2
  candidate remembered by `candidate_key` is not re-promoted next cycle, which stops
  the evolution loop from re-proposing what it already discarded.
- **Stamp every vector with its model and dimension.** `memory_vector_entries`
  carrying `embedding_model`/`provider`/`dim` is the space-guard some stores here
  lack, and it costs three columns.

### Avoid

- **Do not pool a shared brain without a scope you can turn on.** One recall
  surface across every agent is a feature for a solo user and a confidentiality
  leak across projects or trust boundaries; the scope keys are on the row, so apply
  them when isolation matters rather than filtering by layer/status/tags alone.
- **Do not let a soft-delete masquerade as forgetting.** A deleted user fact is a
  `status='deleted'` row filtered on read, not a value-keyed rejection — if an
  extraction or a re-ingest can re-derive it, it comes back; the anti-pattern
  mechanism exists, so extend it to user deletions if that matters.
- **Do not call an append-only log durable if a retention job prunes it.** The
  change log and audit log are append-only within their window; say so.

### Fit

This suits a single developer who runs several coding agents and wants them to
share one growing, local memory — and who values the cross-agent shared brain over
per-project isolation. The layered evolution and anti-pattern induction are more
than most local stores attempt, it is genuinely local by default, and the injected-
skill integration means it works with the agents people already use without MCP
plumbing.

Walk away if you need per-project or per-trust-boundary isolation from the same
daemon — the main recall deliberately does not scope — or if "local" is a hard
requirement you cannot police, since the hosted backend is a configuration away.
And treat "self-evolving" as an LLM consolidation pipeline whose recall quality is
unmeasured here, not a proven gain.

## 12. Open Questions

- Is the unscoped main recall intended to stay a pooled shared brain, or will
  per-project/per-agent scope become applyable on the primary read? The keys are on
  every row.
- How much does the L1→L2→L3 evolution and anti-pattern induction improve task
  outcomes? The pipelines are tested; the gain is unmeasured.
- Should user-fact deletion become a value-keyed rejection like the anti-pattern
  path, so a re-ingest cannot restore a deleted fact?
- How many deployments opt into the hosted OpenMem backend, and what moves off the
  machine when they do?

## Appendix: File Index

- `Memory/src/storage/schema.ts`, `db.ts`, `backend.ts`, `sqlite-vec-store.ts`, `repositories.ts` — schema, local/remote backends, vector sidecar, dedup, change log.
- `Memory/src/service/memory-service.ts` — store/delete/archive/redact, status mapping, audit writes.
- `Memory/src/service/retrieval/` — `indexed-candidate-pool.ts` (channel fusion, filter), `retrieval-service.ts` (failure-avoidance, episode scope), `query-rewrite.ts`.
- `Memory/src/service/evolution/` — `span-pipeline`, `policy-induction`, `world-model-pipeline`, `skill-pipeline`, `negative-experience-pipeline`, `evolution-job-processor`.
- `Memory/src/model/embedder.ts` — local all-MiniLM embeddings.
- `Memory/src/cli/skill-writer/index.ts`, `cli/skills/memmy-memory/SKILL.md` — the injected per-agent skill.
- `Memory/src/client/openmem-cloud-client.ts` — the optional hosted backend.
- `Memory/tests/service/retrieval/injected-context.test.ts` — the must-not-inject assertions.

## History

**2026-08-15** — [`c6cdbf9a126cc297253783c5594ac5ee8acb7c1a`](https://github.com/MemTensor/memmy-agent/commit/c6cdbf9a126cc297253783c5594ac5ee8acb7c1a) — first reading. Screened before opening: FRESH manifests across the workspaces; nothing was installed or run. The `Memory/` package was established as the authoritative local engine (default `byok`/`local`/`sqlite`, `config/index.ts:252-255`), distinct from the MemOS Python package and from the optional hosted OpenMem backend; the layered store, the evolution pipeline, the anti-pattern/negative-experience mechanism, the injected per-agent CLI skill, and the unscoped main recall were read from `Memory/src/storage/`, `service/` and `cli/` and cross-checked against the committed tests (`injected-context.test.ts`). `tombstone` (anti-pattern and rejected-candidate records keyed on content), `trust_state` (status consumed on read), `audit_log` (audit and change logs, retention-pruned) and `negative_eval` are earned; `scope_enforced` is withheld because the primary recall deliberately pools across agents, and `bitemporal` and `human_review` are withheld. No paper is cited in the tree; "MemOS-powered" is lineage and branding.

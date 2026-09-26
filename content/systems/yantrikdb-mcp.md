---
title: "yantrikdb-mcp"
eyebrow: "The engine over MCP, with the scope left to the model"
description: "An MCP server running the YantrikDB engine in process, with twenty-one tools and a namespace the model may omit, so default recall spans every namespace."
root: ../..
page_kind: system
source_name: "yantrikos/yantrikdb-mcp"
source_url: https://github.com/yantrikos/yantrikdb-mcp
archive_name: "yantrikos--yantrikdb-mcp"
revision: 364e19a5b33a6c4a81f46fa9eaee5ddce68fcfa3
revision_url: https://github.com/yantrikos/yantrikdb-mcp/commit/364e19a5b33a6c4a81f46fa9eaee5ddce68fcfa3
analyzed_at: 2026-09-26
licence: "MIT; the engine it installs is Apache-2.0"
size: "6,435 lines of Python in the server package; the memory itself lives in the YantrikDB engine, a separate repository"
activity: "101 commits on main by 2 contributors, 20 March 2026 – 19 September 2026"
tests: "286 test functions in 33 files under tests/, plus 8 in a root-level file outside the configured test path"
capabilities: "negative_eval"
capability_evidence:
  negative_eval: "a later value must not surface in a read as of an earlier instant, and an out-of-window row must not survive a time-window recall, each beside a positive control, through the MCP tool functions on a real engine | tests/test_temporal_as_of.py:99-120; tests/test_time_window_range.py:71-94 | `test_as_of_end_to_end_excludes_later_writes` records port 8420 in namespace tl, takes a cut, records port 9000 in the same namespace, calls the `temporal` tool with action as_of and asserts 8420 present and 9000 absent. `test_recall_window_excludes_out_of_window_rows` seeds four in-window release rows and a 300-day-old decoy and asserts an in-window row present and the decoy absent under since=6h; the paired `until` case asserts the inverse. Both drive the tool function against `load_engine` with the bundled embedder | the as_of case is skipped on an engine without `recall_as_of`, which 0.23.1 has. The namespace case C5 in tests/test_mcp_semantic_contract.py:171-177 asserts absence from a namespace holding no rows, so it passes on an empty result and is not part of the evidence. Not run for this report"
stack_storage: "sqlite"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A YantrikDB engine memory row written through MCP tools, plus conventions the server adds in metadata: skill records, skill outcome events, a pending_review flag, event_time bounds"
  storage: "The engine in process against one SQLite file, default ~/.yantrikdb/memory.db, or a YantrikDB server cluster over HTTP when YANTRIKDB_SERVER_URL is set"
  retrieval: "Engine hybrid recall with entity expansion forced on, optional created_at window, client-side relative score cutoff, re-sort by recency or certainty, record-time as_of recall, chain_head for the newest revision"
  write: "Agent-called remember, single, batch or summary draft, with optional idempotency key, backdated created_at, event_time and stated claims; refused rather than silently dropped when the engine cannot honour a parameter"
  update_delete: "correct in place with a required reason; forget by rid; conflict resolve and auto_resolve; archive and hydrate; all by id with no namespace argument"
  scoping: "A namespace tool argument the model supplies. remember defaults to default, recall and list default to no namespace, which the engine treats as every namespace. Network transports share one store across all clients behind one bearer token"
  integration: "An MCP server over stdio, SSE or streamable HTTP with 21 tools in the full profile and 10 in core, injected server instructions, a portable Agent Skills skill, and integration notes for Hermes Agent and Prime Agent"
  background: "None scheduled. think and the maintenance cycle run only when the agent calls them; write responses carry a maintenance-debt nudge after 50 writes"
  trust: "Engine statuses applied by the engine recall; a skill write gate off by default with schema, content scanners, rate limit, attribution, JSONL audit and a review queue for rule skills; pack writes gated by an environment flag"
  strengths: "Parameters the engine cannot honour are refused with the fix named rather than dropped; the maintenance-cycle dry run defaults to preview after a documented incident; every hit carries created_at and why_retrieved; engine and SDK pins bounded to tested minors with the reason in the manifest"
  risks: "Default recall and the cold-start digest span every namespace; the generic remember writes into the skill namespace past the skill gate, and a skill with no hash is served as valid; the review queue has no reader and default recall returns it; the skill rate limit is keyed on the JSON-RPC request id; auto embedder selection treats its own default store as a legacy one"
---

## 1. Executive Summary

yantrikdb-mcp is the MCP server its author ships for the
[YantrikDB engine](../yantrikdb-engine/): twenty-one tools over the engine's
Python binding, run in process against one SQLite file or forwarded to a
[YantrikDB server](../yantrikdb/) cluster. Its care is at the parameter level.
When the engine cannot honour an argument, the tool refuses and names the fix
instead of dropping it. Its weakness is that the boundaries it adds are
per-tool while the store is shared. Scope is a namespace the model may omit, and
omitted means every namespace. The skill gate guards one write door while
`remember` reaches the same namespace through another.

**The memory mechanism is the engine's.** Decay, consolidation, contradiction
detection, correction with revision history, supersession and the as-of read are
described in the [engine report](../yantrikdb-engine/). This report covers what
the MCP layer adds or changes: the tool surface, where scope is decided, how
writes are gated, and what reaches the model.

**The engine that runs at this pin is 0.23.1.** `pyproject.toml:133` requires
`yantrikdb>=0.15.4,<0.24.0`, and the documented install is `uvx yantrikdb-mcp`,
which resolves the newest release in range. PyPI published 0.23.1 at 18:51 UTC on
19 September 2026, before the pinned commit at 23:19 UTC. Tag `v0.23.1`
([`597fdcee9d55a2f7f8ac511a40dc2c72f136f5c6`](https://github.com/yantrikos/yantrikdb/commit/597fdcee9d55a2f7f8ac511a40dc2c72f136f5c6))
is four commits past the engine report's pin and changes only version strings
and one CLI print, so the engine report's reading applies unchanged.

**This is not the MCP server inside the engine package.** The engine ships its
own 628-line `src/yantrikdb/mcp/` with `memory_*` tools; that is the one the
[server report](../yantrikdb/) cites. This repository is the separately
distributed one.

Four findings, all read rather than run:

- **Default recall spans every namespace.** `recall` declares `namespace=None`
  and forwards it, and the engine emits no namespace predicate for `None`. The
  cold-start `session(action="digest")` the server instructions prescribe is
  whole-store unless the model passes `scope`.
- **The skill gate has a second door.** `skill(action="define")` runs a gate
  that is off by default, then schema, content scanners, attribution and an
  audit line. `remember` writes any namespace with any metadata, and
  `skill(action="surface")` serves any `skill_substrate` row tagged
  `record_type: skill`, treating a missing hash as a legacy row.
- **The review queue has no reader.** Rule-type skills go to
  `skill_pending_review`; nothing in the tree reads that namespace by name, and
  default recall returns it.
- **The rate limit resets every call.** The per-session limiter is keyed on
  the JSON-RPC request id.

One mark: `negative_eval`. Section 9 names the six withheld.

## 2. Mental Model

A memory is an engine row, and every state it can hold is the engine's: active,
consolidated or tombstoned, a synthesis state, a supersession edge, a revision
chain. The MCP layer adds no state of its own to that row. What it adds is who
decides each step, and at this layer the answer is the agent for every one.

- **Becoming a memory.** The agent calls `remember`, choosing the text, type,
  importance, certainty, source, domain and namespace. The injected
  instructions tell it to use memory "AUTOMATICALLY without the user asking"
  (`src/yantrikdb_mcp/server.py:43-45`).
- **Changing.** `correct` updates in place with a required reason; the engine
  archives the prior state.
- **Stopping.** `forget` by rid, a conflict resolution the agent picks, or an
  `auto_resolve` pass whose dry run defaults on.
- **Where it lives.** A namespace string the agent passes, or `default`.

Skills are the one place the server adds a lifecycle. A `define` lands in
`skill_substrate` or, for a rule, in `skill_pending_review`. A skill replaced by
`on_conflict="replace"` is forgotten first. Outcome events land in
`outcome_substrate`. These are namespace conventions, not engine states, so
every read that does not name a namespace sees all three.

```mermaid
%% caption: two write doors into the skill namespace and a default read that names no namespace, so the pending queue and the catalog both reach the model through plain recall
flowchart TB
    DEF["skill(action=define)"] --> GATE{"YANTRIKDB_SKILLS_WRITE_ENABLED<br/>frozen at import, default off"}
    GATE -->|"off"| REF["refused, audit line"]
    GATE -->|"on"| CHK["schema, scanners, rate limit<br/>keyed on request_id,<br/>attribution, body_sha256"]
    CHK -->|"skill_type = rule"| PEND[("skill_pending_review")]
    CHK -->|"other types"| LIVE[("skill_substrate")]
    REM["remember(namespace=skill_substrate,<br/>metadata record_type=skill)"] -->|"no gate, no hash"| LIVE
    REM2["remember(text)"] --> DEFNS[("default namespace")]
    SURF["skill(action=surface)"] --> LIVE
    SURF --> HASH{"body_sha256 present?"}
    HASH -->|"absent: treated as legacy"| SERVED["served as a skill"]
    HASH -->|"present and matches"| SERVED
    REC["recall(query), namespace omitted"] --> NOPRED["engine: no namespace predicate"]
    NOPRED --> PEND
    NOPRED --> LIVE
    NOPRED --> DEFNS
    PEND -.->|"no reader, no promote verb"| NOWHERE["never resolved"]
```

## 3. Architecture

| Module | Role |
| --- | --- |
| `src/yantrikdb_mcp/server.py` | Injected instructions, a lazily opened process-singleton engine, embedded or HTTP backend selection |
| `src/yantrikdb_mcp/tools.py` | All tools: 3,447 lines of argument shaping, refusals and response pruning |
| `src/yantrikdb_mcp/embedder.py` | Embedder selection: bundled 64-dim, ONNX 384-dim, multilingual 256-dim |
| `src/yantrikdb_mcp/http_backend.py` | The same method names over a YantrikDB server, with unsupported ones raising a typed error |
| `src/yantrikdb_mcp/skill_security.py`, `skill_validation.py`, `skill_content_scanner.py` | The skill gate |
| `src/yantrikdb_mcp/_compat.py`, `auth.py` | MCP SDK 1.x and 2.x shims, network app, bearer-token middleware |

**One engine handle per process.** `_LazyDB` opens the engine on the first tool
call. Under SSE the lifespan re-enters per client session. A fresh handle per
session raced on closing the same SQLite WAL, so the handle is now a singleton
closed once at exit (`server.py:237-265`, issue #11).

**Network mode is one principal.** `--transport sse` or `streamable-http` binds
`0.0.0.0` by default (`src/yantrikdb_mcp/__init__.py:77`). It wraps the app in
bearer-token auth only when `YANTRIKDB_API_KEY` is set, and otherwise logs that
the server is unauthenticated (`:89-98`). DNS-rebinding protection is disabled
and all hosts and origins are allowed (`_compat.py:117-121`). Every client that
holds the key reaches the same store with the same tools.

### Deployment and ergonomics

- **Install:** `uvx yantrikdb-mcp`, no account, no API key. The engine wheel
  bundles its embedder, so the default path has no ML dependency.
- **Store:** one SQLite file, not hand-readable; the `atlas` tool exports a
  static page of every memory and serves it on 127.0.0.1.
- **Cluster:** set `YANTRIKDB_SERVER_URL`. `list_memories` and several other
  methods raise `RemoteUnsupportedError` there (`http_backend.py:525-551`), so
  skill `get`, skill `list` and `temporal(action="range")` without a query do not
  work in cluster mode.

**Auto embedder selection misreads its own default store.** With
`YANTRIKDB_EMBEDDER` unset, `load_engine` picks ONNX whenever the file already
holds memories, and bundled otherwise (`embedder.py:238-244`). The README says
the ONNX branch is for "an existing pre-v0.6 database". The probe cannot tell
one from the bundled store the same default created on first run.
`tests/test_embedder_loader.py:99-117` builds its `legacy.db` fixture with
`YantrikDB.with_default`, the bundled path, and asserts that a restart without
the `[onnx]` extra raises. Every other test that spawns a server sets the
embedder explicitly. Read, not reproduced; section 12 carries the question.

## 4. Essential Implementation Paths

- **Remember** — `tools.py:330-606`. Claims and backdating are refused before
  any write on an engine that cannot hold them (`:404-438`). A keyed batch skips
  `record_batch`, because that path would drop the keys (`:478-508`). Single
  mode forwards `namespace`, metadata and `event_time` bounds to `db.record`
  (`:586-596`).
- **Recall** — `:661-922`. Default path `db.recall_with_response(...,
  namespace=namespace, ...)` (`:828-833`). An explicit `order` or
  `include_superseded` routes to `db.recall` (`:809-826`). `min_score_ratio`
  is applied client-side because the default engine path lacks it (`:834-856`).
- **Forget, correct** — `:926-956`, `:960-1017`, by rid, no namespace.
- **Think** — `:1021-1172`. An explicit `dry_run=True` on a plain think is
  refused; `None` means preview for the maintenance cycle (`:1109-1116`).
- **Skill** — `:2317-2835`. Gate `:2422-2452`, define `:2455-2626`, surface
  `:2628-2689`.
- **Digest** — `session(action="digest")`, `:1793-1845`; `scope` is forwarded
  only when given (`:1806`).
- **Engine side** — the namespace branch in `crates/yantrikdb-core/src/engine/recall.rs:1850-1880`
  and `passes_recall_filters` (`:285-327`) at `v0.23.1`; `forget(rid)` in
  `crates/yantrikdb-python/src/py_engine/memory.rs:737-740`.

## 5. Memory Data Model

The row is the engine's; section 5 of the [engine report](../yantrikdb-engine/)
describes it. The server adds three conventions in metadata and namespace.

**Skills.** A defined skill is a procedural memory in `skill_substrate`. Its
metadata carries `record_type: skill`, `skill_id`, `skill_type`, `applies_to`,
`body_sha256`, and attribution: request id, OS user, hostname, wall clock,
origin and a nonce (`tools.py:2569-2585`, `skill_security.py:232-248`). A rule
carries `pending_review: true` and lands in `skill_pending_review`
(`skill_security.py:528-540`).

**Outcomes.** One episodic memory per reported use, in `outcome_substrate`, with
no rollup onto the skill.

**Valid time.** `event_time` is written as `event_time_min` and
`event_time_max` in metadata, which the engine mirrors to columns
(`tools.py:609-618`). `created_at` backdates the record time.

**The names are reserved by convention only.** The engine mentions
`skill_substrate` in one doc comment and guards none of the three names, and
`remember` accepts any namespace string and any metadata.

## 6. Retrieval Mechanics

The model sees the engine's hybrid recall: vector and FTS lanes, graph
expansion, decay-weighted scoring. The server makes three changes to what reaches
it.

**It forces entity expansion on.** The engine flipped the `expand_entities`
default to off at 0.13, and the tool passes `True` explicitly
(`pyproject.toml:78`). The manifest records why the floor rose to 0.14.1: a
case-sensitive entity stoplist let "AT" become an entity that matched every
query containing "at". The engine's benchmark missed it because the engine
defaults expansion off and this server turns it on (`pyproject.toml:99-118`).

**It makes each hit auditable.** Every hit carries `created_at` in ISO form,
`similarity` beside the blended score, and `why_retrieved`
(`tools.py:860-898`). A `since`/`until` window filters on `created_at` before
ranking and is echoed back (`:908-913`).

**It leaves scope to the caller.** `recall`, `memory(action="list")`,
`graph(action="recall_with_links")` and `temporal` take `namespace=None`. The
engine appends `AND m.namespace = ?` only when a namespace is supplied
(`recall.rs:1859-1863`, `:1875-1879`). So an agent that follows the injected
golden path, a digest and then a short recall, reads every namespace in the
file, including the skill queue and any other pipeline's memories. The bundled
Agent Skills skill asks job agents to pass a pipeline namespace "on every call"
(`skills/persistent-memory/SKILL.md:73-74`), which is prose to the model.

**Valid time is written and not read.** No tool passes the engine's
`event_after` or `event_before`. `temporal(action="as_of")` is the engine's
record-time `recall_as_of`.

## 7. Write Mechanics

Writes are synchronous tool calls, visible to the next recall. No model runs
in the server; extraction for `remember(summary=...)` and `session(capture)` is
the engine's `draft_memories_from_summary`. `correct` needs a non-empty reason.
Stated claims are grounded by the engine, and ungrounded ones come back rejected
rather than stored.

**Refusal over silent loss.** A backdated `created_at`, a `claims` list or an
as-of query on an engine that cannot honour it returns an error naming the
version needed, before anything is written (`tools.py:404-438`, `:1985-1992`).
The comment's reason is that stamping "now" on a memory the caller dated "would
corrupt exactly the thing backdating exists to protect".

**The dry-run incident is in the code.** On 15 August 2026 a maintenance cycle
called as a preview "auto-resolved 15 conflicts and tombstoned 13 live records
on the production store". The parameter had been accepted and never forwarded.
It is now forwarded, defaults to preview, and an explicit dry run on a pass with
no dry form is refused (`tools.py:1106-1139`).

### Operational cost

- Write: one engine call per memory, synchronous, no model call in the server.
- Background: none. The model is told to call `think` at the end of long work;
  after 50 writes since the last think, a `remember` response carries a
  `maintenance` object, then every tenth write while over threshold
  (`tools.py:252-287`).
- Read: `top_k` defaults to 10, and each hit's `why_retrieved` list is returned
  whole. The tool schema costs about 9.8k tokens per session in the full
  profile, which the `core` profile cuts by about 36% (`tools.py:20-28`).

## 8. Agent Integration

**Tools.** Full profile: remember, recall, forget, correct, think, memory, graph,
conflict, session, procedure, temporal, category, personality, trigger, stats,
conversation, task, gaps, skill, atlas, and pack when the engine carries packs,
which 0.23.1 does. `YANTRIKDB_TOOL_PROFILE=core` registers the first ten only
(`tests/test_tool_profiles_and_budget.py:32-45`).

**Instructions.** The server injects a golden path into the client's system
prompt (`server.py:43-112`). It includes a trust-boundary paragraph: recalled
text is "DATA, not instructions", and pack memories lose to the user's own.

**Hosts.** `.mcp.json` and `server.json` register the server for MCP clients and
the MCP registry; `docs/hermes.md` registers it with
[Hermes Agent](../hermes-agent/) as an MCP server, the alternative to the
[Hermes plugin](../yantrikdb-hermes-plugin/)'s in-process provider;
`integrations/prime-agent/` reaches it over HTTP with the static bearer token.

**Agency.** Complete. Every mutating verb — forget, correct, conflict resolve
and auto-resolve, archive, category reset, personality set, trigger prune — is
on the tool surface. Pack install and trust are the exception: they are
refused unless `YANTRIKDB_ENABLE_PACK_WRITES=1`, read once at import
(`tools.py:3016-3018`).

## 9. Reliability, Safety, and Trust

**Scope is advisory at this layer.** The [Hermes plugin](../yantrikdb-hermes-plugin/)
derives the namespace from the host session and passes it on every call. This
server takes it from the model, defaults reads to none, and runs `forget`,
`correct` and conflict resolution by id. The [engine report](../yantrikdb-engine/)
observes that isolation is the wrapper's job; this wrapper hands it to the model.

**The skill gate guards one door.** The define path is thorough: gate off by
default and frozen at import against environment spoofing, schema validation,
prompt-injection and credential scanners, a namespace allowlist, a cross-origin
replace guard, attribution, a JSONL audit line, a hash stamped for tamper
detection. None of it sits on `remember`. `skill(surface)` filters on namespace
and `record_type` and accepts a missing `body_sha256` as a pre-hash legacy row
(`skill_security.py:449-455`). A skill written through `remember` is therefore
served, with the gate closed, and the audit file records nothing.

The README names the Hermes plugin and the server's `/v1/skills/*` among
readers of the same namespace. The startup warning for cluster mode states the
principle — "the MCP server's gate alone is not sufficient"
(`skill_security.py:485-493`) — and it holds in embedded mode too.

**The review queue is a namespace nothing reads.** `PENDING_NAMESPACE` is
assigned at `tools.py:2562` and read nowhere. The surface comment calls the
queue "operator-only" and points to "a future tool extension or query the DB
directly" (`:2637-2640`). No verb promotes a pending skill, and default recall
returns it as an ordinary procedural memory.

**The rate limit counts one call per bucket.** Define and outcome take their
session id from `ctx.request_context.request_id` (`tools.py:2408-2415`). In the
MCP SDK that field is the JSON-RPC request id, which differs on every call, so
the 30-per-minute sliding window never holds more than one entry per key. The
limiter's tests pass fixed strings (`tests/test_skill_security.py:373-393`).

**Capability marks:**

- `negative_eval` — awarded; section 10.
- `scope_enforced` — withheld. The row has a namespace and the engine filters on
  it, but every read at this layer takes the key from the model and defaults to
  none, and the cold-start digest is whole-store by default.
- `trust_state`, `bitemporal`, `audit_log` — withheld at this layer; the
  [engine](../yantrikdb-engine/) carries all three, in process. This server adds
  a `pending_review` flag no recall consults, writes valid time that no tool
  reads back, and keeps a skill-only JSONL file, off by default, outside the
  store, whose write failures are swallowed.
- `tombstone` — withheld. Forget, conflict resolution and skill replace all act
  on a rid.
- `human_review` — withheld. The conflict `resolve` and `auto_resolve` verbs
  are on the agent's tool surface, and the skill queue has no drain.

## 10. Tests, Evals, and Benchmarks

Nothing was installed or run for this report; everything below is from reading
the tests at the pin. CI runs the unit suite on Python 3.10, 3.12 and 3.14
against MCP SDK 1.x and 2.x with the `[onnx]` extra installed, and an
end-to-end stdio suite per embedder backend (`.github/workflows/ci.yml`).

**The negative cases.** `tests/test_temporal_as_of.py:99-120` records port 8420,
takes a cut, records port 9000 in the same namespace, and asserts the `temporal`
tool's as-of read returns 8420 and not 9000. `tests/test_time_window_range.py:71-94`
seeds four in-window rows and a 300-day-old decoy and asserts the window keeps
one and drops the other, in both directions. Both run the tool function against
the real engine with the positive side asserted first. That earns
`negative_eval`.

**The contract gate.** `tests/test_mcp_semantic_contract.py` drives a spawned
server over JSON-RPC and states a 100% pass bar. Its namespace case C5
(`:171-177`) remembers a secret in `tenant_alpha` and asserts it is absent from
a `tenant_beta` recall. Nothing in the module writes to `tenant_beta`, so a
recall returning nothing passes. Seeding one `tenant_beta` fact and asserting
it present would repair it.

**Not covered.** No test writes through `remember` into `skill_substrate`, reads
a pending skill through plain recall, or calls a gated skill action twice through
the tool to exercise the limiter. The review queue is tested as a predicate
(`tests/test_skill_security.py:493-503`).

**The paper.** The README links *Skill as Memory, Not Document*
([doi:10.5281/zenodo.20128887](https://doi.org/10.5281/zenodo.20128887)), which
the Zenodo record lists as a preprint dated 12 May 2026. The README calls it
"peer-reviewed" (`README.md:350`, `:394`). Its abstract reports the substrate
rejecting 70 of 70 adversarially malformed skills at write time. In this server
that validation runs in `skill(action="define")` and not on `remember`, which
reaches the same namespace. The paper's harness was not read.

## 11. For Your Own Build

### Steal

- **Refuse what you cannot honour, and name the fix.** A backdated write on an
  engine that would stamp "now", a time window on a path that would drop it: an
  error with the required version beats a success that means something else.
- **Default destructive previews to preview.** After a dry run ran wet, the
  default became preview, and an explicit dry run on an operation with no dry
  form became an error.
- **Surface maintenance debt as data inside the responses the agent already
  reads**, rate-limited, with no urgency prose.
- **Put `created_at` and a similarity number on every hit**, so a caller can
  overrule a ranking that picked a stale revision.
- **Bound each hard dependency to the tested minor, with the reason beside the
  pin.** The manifest records the flipped default and the major release that
  broke installs.

### Avoid

- **A write gate on one tool when another tool writes the same records.** Put
  the check where the namespace is written, or make the namespace unreachable
  from the generic writer.
- **Treating a missing integrity field as valid.** A legacy exemption becomes
  the path of least resistance for every new writer.
- **A review queue with no reader.** Either ship the promote path and exclude
  the queue from ordinary reads, or do not route to it.
- **Keying a per-session limit on a per-request identifier.**
- **An optional scope whose default is everything**, on a server that serves
  several clients from one file.

### Fit

This suits one person who wants the YantrikDB engine behind Claude Code,
Cursor or Hermes over MCP, on one machine, with the model deciding what to
remember. The engine does the memory work well, and this layer passes it
through with unusual honesty about what each argument does. It does not suit a
shared deployment. Scope, deletion and skill admission all trust the model or
the network, and the network mode binds wide with auth optional. A team
wanting per-person or per-project isolation should derive the namespace
outside the model, as the Hermes plugin does, or run one file per principal.

## 12. Open Questions

- Does a default install fail on its second start? The auto rule and its test
  say a bundled store with memories resolves to ONNX, which raises without the
  extra. Settling it needs one run with no `YANTRIKDB_EMBEDDER` set.
- Is a skill written through `remember` served by the Hermes plugin's and the
  server's skill readers too? The README says they share the namespace; their
  filters were not read here.
- Is the review queue meant to be drained by a server route? No reader was
  found in this repository or in the engine.
- Does the paper's admission harness drive `skill(define)`, the server's
  `/v1/skills/*`, or the engine directly?

## Appendix: File Index

- **Server and instructions:** `src/yantrikdb_mcp/server.py`,
  `src/yantrikdb_mcp/__init__.py`, `src/yantrikdb_mcp/_compat.py`,
  `src/yantrikdb_mcp/auth.py`.
- **Tools:** `src/yantrikdb_mcp/tools.py` (remember `:330`, recall `:661`,
  forget `:926`, correct `:960`, think `:1021`, session `:1681`, temporal
  `:1852`, skill `:2317`, pack `:3078`, atlas `:3370`).
- **Skill gate:** `src/yantrikdb_mcp/skill_security.py`,
  `skill_validation.py`, `skill_content_scanner.py`.
- **Backends:** `src/yantrikdb_mcp/embedder.py`,
  `src/yantrikdb_mcp/http_backend.py`.
- **Manifest and hosts:** `pyproject.toml`, `.mcp.json`, `server.json`,
  `skills/persistent-memory/SKILL.md`, `docs/hermes.md`,
  `integrations/prime-agent/`.
- **Tests:** `tests/test_temporal_as_of.py`, `tests/test_time_window_range.py`,
  `tests/test_mcp_semantic_contract.py`, `tests/test_skill_security.py`,
  `tests/test_embedder_loader.py`, `tests/test_tool_profiles_and_budget.py`,
  `tests/test_v010_engine_contract_cases.py`.
- **Engine at `v0.23.1`:** `crates/yantrikdb-core/src/engine/recall.rs`,
  `crates/yantrikdb-python/src/py_engine/memory.rs`, `src/yantrikdb/mcp/`.

### Recorded searches

Checked against the checkout at the pinned revision, and the engine at tag
`v0.23.1` where marked.

- `grep -rn 'event_after\|event_before' . --exclude-dir=.git` — no match; no tool binds the valid-time filter.
- `grep -rn 'skill_substrate\|PENDING_NAMESPACE\|skill_pending_review\|OUTCOME_NAMESPACE\|SKILL_NAMESPACE' --include='*.py' . | grep -v '^./tests'` — `PENDING_NAMESPACE` is defined in `skill_security.py:528`, imported at `tools.py:2379` and assigned at `:2562`; no read.
- Engine: `grep -rn 'skill_substrate\|skill_pending_review\|outcome_substrate' crates src` — one doc comment in `py_engine/memory.rs:422-429`; no guard.
- `grep -rn 'request_id' src/` — `tools.py:2408` and `:2413` only.
- `grep -n 'rate' tests/test_skill_security.py tests/test_e2e_mcp.py` — the limiter tests at `test_skill_security.py:373-393` call `check_rate_limit` with fixed strings.
- `grep -n 'YANTRIKDB_EMBEDDER' tests/*.py` — every spawned server sets it; only `test_embedder_loader.py` exercises auto.
- `grep -rniE 'arxiv|bibtex|@article|@misc|doi\.org|CITATION|zenodo' . --exclude-dir=.git` — the README's Zenodo link and BibTeX block; no `CITATION.cff`.
- `gh api repos/yantrikos/yantrikdb/compare/49c7aac1b78b74b296f7708a95d227073b4a666b...v0.23.1` — four commits, seven files: version strings, `src/yantrikdb/cli.py` and `tests/test_cli.py`.
- PyPI `yantrikdb` release list — 0.23.1 uploaded 2026-09-19T18:51:01Z, the newest release below 0.24.0 before the pin commit at 2026-09-19T23:19:17Z.

## History

**2026-09-26** — [`364e19a5b33a6c4a81f46fa9eaee5ddce68fcfa3`](https://github.com/yantrikos/yantrikdb-mcp/commit/364e19a5b33a6c4a81f46fa9eaee5ddce68fcfa3) — first reading, at the head of `main`, a commit dated 19 September 2026. One mark, `negative_eval`. The engine was read at tag `v0.23.1`, the release the manifest range resolves to at the pin. Screened before reading: 3 auto-run surfaces (`.mcp.json`, `mcp.json` and `server.json`, each launching `uvx yantrikdb-mcp`), no build-time execution, 2 unpinned manifests, 2 inside the cooldown with every file of the depth-1 clone dated to the tip, and no agent-instruction file. The engine's partial checkout showed one `build.rs` and three files inside the cooldown. Nothing was installed, built or run.

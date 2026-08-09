---
title: "Kiro Crew"
eyebrow: "Seven ways a write is refused"
description: "A local development workspace whose memory writes pass an ordered gate — key shape, prefix allow-list, reserved namespace, confidence floor, size, injection patterns, conflict — each refusal typed and the security ones logged with the value redacted first."
root: ../..
page_kind: system
source_name: "kirodotdev/KiroCrew"
source_url: https://github.com/kirodotdev/KiroCrew
revision: 429cbad8cdb7bfbf4c10f6343374565832b176d2
revision_url: https://github.com/kirodotdev/KiroCrew/commit/429cbad8cdb7bfbf4c10f6343374565832b176d2
analyzed_at: 2026-08-06
capabilities: "audit_log, human_review, negative_eval"
stack_storage: "sqlite, faiss"
stack_retrieval: "lexical, vector"
stack_source: "seeded"
matrix:
  memory_unit: "Two kinds — a semantic key-value entry under an allow-listed prefix, and an episodic conversation fragment with an embedding, tags and an importance score — beside three markdown files a person can read"
  storage: "`~/.kiro/crew/memory.db` in SQLite WAL with an optional FAISS index beside it, plus `preferences.md`, `projects.md` and dated `history/` files under the workspace directory"
  retrieval: "Vector similarity over FAISS with time-decay scoring, falling back to FTS5 when embeddings are unavailable; relevance is filtered on raw cosine before decay is applied"
  write: "An ordered validation chain returning a typed `SemanticRejectCode`; `user_explicit` is the privileged source that bypasses the confidence floor and alone may write the reserved `system.` namespace"
  update_delete: "`is_deleted` flags on both tables, delete endpoints on the dashboard, and a conflict resolver that can skip a write outright; no supersession chain and no record keyed on a refused value"
  scoping: "None — a single local workspace per machine, with no user, project or tenant key on the read path"
  integration: "A desktop app, a web dashboard, a CLI, Slack and Discord bridges, and Kiro Crew Apps bundling agents, skills, schedules and services"
  background: "Unattended multi-step tasks, scheduled recurring jobs and heartbeats; event rotation past ten thousand rows; a self-heal path over the memory store"
  trust: "A confidence float gated at 0.8, a `source` string on every entry, and a privileged `user_explicit` source — no discrete epistemic status"
  strengths: "Rejected writes are audited, and an injection-blocked snippet is stripped of exfiltration URLs and credentials before it is persisted, because the dashboard renders that snippet verbatim"
  risks: "Refusals are recorded and never consulted, so a blocked value can be offered again; the event log rotates at ten thousand rows; and no scope key exists anywhere"
---

## 1. Executive Summary

Kiro Crew is a local development workspace from the Kiro team — desktop app, web
dashboard, CLI, Slack and Discord bridges — that runs unattended tasks and
scheduled jobs on your own hardware. Apache-2.0, 1,606 commits since 1 June
2026, 475,988 lines of Python under **502,973 lines of tests across 1,024
files**. The README's claim is memory: *"persistent, self-learning, and
self-evolving… remembers across sessions."*

The memory is two stores with different jobs. `src/kiro_crew/memory.py` (528
lines) keeps `preferences.md`, `projects.md` and dated `history/` files under
`~/.kiro/crew/workspace/memory/`, with an FTS5 index beside them — human-readable
by design. `src/kiro_crew/vector_memory.py` (2,764 lines) is the structured half:
a semantic key-value table and an episodic fragment table in SQLite WAL, with an
optional FAISS index.

**The reason to read this is the write path.** A semantic write passes an ordered
chain, and every refusal is a typed `SemanticRejectCode`:

| Code | Refuses |
| --- | --- |
| `key_format` | a key that is not `^[a-z][a-z0-9_.]*[a-z0-9]$`, or over 100 chars |
| `allowlist_reject` | a key outside the configured prefixes |
| `reserved_prefix` | a `system.` key from any source but `user_explicit` |
| `low_confidence` | confidence below 0.8, unless the source is `user_explicit` |
| `value_size` | a value over 4,096 bytes |
| `injection_blocked` | a value matching the prompt-injection patterns |
| `conflict_skip` | a write the conflict resolver declines against the existing value |

Four of the seven are `_AUDITABLE_REJECT_CODES` and land in the `memory_events`
table; two are `_SECURITY_REJECT_CODES`. A refusal here is a fact with a name and
a record, not a silent `return False` — which is the difference between a gate
you can operate and a gate you can only hope is working.

**And one comment in that path is worth the whole report.** Episodic text is
screened for injection too, because *"a poisoned turn could persist steering
instructions that get re-injected into future contexts."* When it matches, the
rejection is logged with a snippet — and before the snippet is stored:

```python
# The rejected text is untrusted conversation content and the snippet
# is surfaced verbatim on the dashboard (/api/memory/events -> get_events).
# Scrub exfiltration URLs + credentials before persisting the audit
# snippet so poisoned text can't smuggle secrets onto that surface.
safe_snippet, _ = redact_exfiltration_urls(text[:200])
safe_snippet, _ = redact_credentials(safe_snippet)
```

That is second-order reasoning about a defence: having built an audit log for
blocked injections, they asked what the audit log itself becomes when the thing
it records is hostile and a human UI renders it. **The atlas has not previously
found a system that treats its own security log as an attack surface.**

**The trust model is a privileged source rather than a status.** `user_explicit`
bypasses the confidence floor and is the only source permitted to write the
reserved `system.` namespace. Everything else — extraction, tool output,
conversation — is subject to the 0.8 gate. That is a clean two-tier hierarchy and
it is expressed entirely in `source` string comparisons, with no field recording
what the system concluded about a given memory.

**The gap is the one the refusal machinery makes conspicuous.** Every reject is
recorded and none is consulted. `log_reject_event` writes the code, the key and
the value into `memory_events`; nothing reads that table on the write path. A
value blocked as an injection today can be offered again tomorrow and is screened
afresh by the same pattern list — which works until the pattern list is the thing
that was wrong. The material for a value-keyed refusal is already sitting in the
audit table, unqueried.


## 2. Mental Model

There are two memories and they are kept deliberately unalike.

The **markdown half** is what a person reads: `preferences.md` for learned user
preferences, `projects.md` for active project context, and one file per day under
`history/`. It seeds itself with comment markers — `<!-- Learned from
conversations -->` — so an empty store explains what it is for. Recall over it is
FTS5 plus a recency window, and correction is editing the file.

The **structured half** is what the retrieval path uses: `semantic_memory` keyed
on an allow-listed string, and `episodic_memories` holding conversation
fragments with embeddings, tags and importance. Both carry `is_deleted` rather
than being removed.

A memory becomes a belief by surviving the gate, and the gate is where all the
epistemics live. There is no candidate state, no review queue, no promotion: a
write either passes all seven checks and lands, or is refused with a code. What
would elsewhere be a status field is here a decision made once, at the door, and
recorded in the event log rather than on the record.

How a belief stops being one is thinner. `is_deleted` hides it, a person can
delete it from the dashboard, and the conflict resolver can decline a
replacement. Nothing marks a value as *wrong*, and nothing stops the same value
arriving again.

```mermaid
stateDiagram-v2
    [*] --> Proposed: a write arrives with a source and a confidence
    Proposed --> Refused: one of seven SemanticRejectCode checks fails
    Refused --> Logged: four of the seven are auditable
    Logged --> Proposed: nothing consults the log, so the value may return
    Proposed --> Stored: all checks pass
    Stored --> Stored: conflict resolver may decline a replacement
    Stored --> Hidden: is_deleted set, by a person on the dashboard
    Logged --> Rotated: oldest rows dropped past ten thousand
```

The loop from `Logged` back to `Proposed` is the finding. Every other edge is a
decision the system keeps; that one is a decision it writes down and then does
not read.


## 3. Architecture

**Runtime.** A Python backend (`src/kiro_crew/`) with an aiohttp dashboard, an
Electron desktop app and a React web UI under `website/`, a CLI, and connection
bridges. Everything runs on the operator's own hardware, locally or on a remote
box they own.

**Persistence.** `~/.kiro/crew/memory.db` is SQLite in WAL mode holding
`semantic_memory`, `episodic_memories`, `memory_events` and a `schema_version`
table. `~/.kiro/crew/memory.faiss` is an optional FAISS index. Beside them, the
markdown workspace and `~/.kiro/crew/memory_index.db` for FTS5 over it.

The SQLite import is worth a note for anyone who has fought this: it prefers
`pysqlite3` and falls back to the stdlib, with a guard for the case where a
bundle prune leaves an empty `pysqlite3` package whose import succeeds but which
has no `connect` — *"an AttributeError at first use, not an ImportError."*
Someone met that failure.

**Search stack.** FAISS for vector similarity when embeddings exist, FTS5
otherwise, with a stemmer (`snowballstemmer`) on the lexical path. Retrieval
applies time decay after relevance filtering, not before —
*"Admission reads the raw `cosine_sim`, never the decay-adjusted"* score — so an
old but genuinely relevant fragment is not filtered out for being old.

**Background work.** Unattended multi-step tasks, scheduled recurring jobs,
heartbeats that watch a system until it needs attention, a self-heal path over
the memory store (`test_memory_selfheal.py`), and `rotate_events` trimming the
audit table past 10,000 rows.

### Deployment and ergonomics

One machine, one install script, no services to stand up — the memory needs
SQLite and nothing else, with FAISS and embeddings optional and a documented
degradation to FTS5 without them.

The markdown half is the ergonomic win. Three files in a directory, readable and
editable in any editor, with the database as the index rather than the authority
for that half. When something goes wrong with preferences, the fix is opening a
file.

The structured half is a SQLite database a person can open but is not meant to
edit by hand, and the dashboard is the intended surface for it.


## 4. Essential Implementation Paths

- **Markdown memory:** `src/kiro_crew/memory.py` — `preferences.md`,
  `projects.md`, dated history, FTS5 index, and a 5-second history cache because
  *"statting + reading up to 181 daily files synchronously on the event loop is a
  per-message cost."*
- **Structured memory:** `src/kiro_crew/vector_memory.py` — the schema at `:151`,
  `SemanticRejectCode` at `:90`, the validation chain at `:475`–`:513`,
  `_write_semantic` and conflict resolution at `:625`, episodic screening at
  `:1066`, `rotate_events` at `:937`.
- **Constants:** `src/kiro_crew/vector_memory_constants.py` — the injection
  patterns and `_contains_injection`.
- **Session memory:** `src/kiro_crew/dashboard/session_memory.py`.
- **HTTP surface:** `src/kiro_crew/dashboard/handlers/memory.py` (1,374 lines) —
  `api_memory_semantic_delete`, `api_memory_episodic_delete`, and the events
  feed the dashboard renders.
- **Human surface:** `website/src/pages/overview/MemoryTab.tsx`,
  `MemoryGraphTab.tsx`, `VectorMemoryCard.tsx`, `SessionMemoryCard.tsx`,
  `website/src/apps/crew-companion/MemoriesSection.tsx`.
- **Tests:** `test/test_vector_memory.py`, `test_memory.py`,
  `test_memory_graph.py`, `test_memory_selfheal.py`, `test_session_memory.py`,
  `test_perf_memory_quickwins.py`.


## 5. Memory Data Model

`semantic_memory` is `key` (primary key), `value_json`, `confidence`, `source`,
`created_at`, `updated_at`, `is_deleted`. The key is the identity, which is what
makes the allow-list meaningful: memory is a bounded namespace of things the
system is permitted to know, not an open set.

`episodic_memories` is `id`, `conversation_id`, `text`, `embedding` BLOB, `tags`,
`importance`, `created_at`, `last_accessed_at`, `is_deleted`.

`memory_events` is the third table and the interesting one: `event_type`,
`memory_type`, `memory_key`, **`old_value`, `new_value`**, `source`,
`created_at`. Both sides of a change, and — for the auditable reject codes — the
value that was refused, in `new_value`, with nothing written to `memory_key` for
an episodic reject because there is no key to write.

**Provenance is a `source` string and it carries real authority.** It is not
decoration: `source != "user_explicit"` is the condition on both the confidence
gate and the reserved-namespace check. A single string field decides whether a
write is privileged, which is economical and also means the whole trust model
rests on every caller passing that string honestly.

**No scope key exists anywhere** — no user, project, workspace or tenant column
on either table. The design is one workspace per machine, and the read path has
nothing to filter on. That is coherent for a local single-operator tool and it
means the schema cannot be multi-tenanted without a migration.

Temporal fields are `created_at`, `updated_at` and `last_accessed_at` — all
record time. No validity interval.


## 6. Retrieval Mechanics

Episodic search is vector similarity over FAISS with a time-decay factor, falling
back to FTS5 with a Snowball stemmer when embeddings are unavailable — a
documented degradation rather than a hard dependency.

The ordering decision is the one worth copying. Relevance admission reads the
**raw** cosine similarity and the decay factor is applied afterwards, for
ranking. A comment states it directly: *"Admission reads the raw `cosine_sim`,
never the decay-adjusted."* Filtering on a decayed score would silently make
"old" and "irrelevant" the same condition, and an old fragment that answers the
question exactly would drop below the threshold for having been written last
year. Separating the admission test from the ranking function is a small change
that prevents a whole class of quiet recall failure.

Thresholds are explicit and tuned: `_EPISODIC_RELEVANCE_THRESHOLD` at 0.55 for
short texts, relaxed past 300 characters, with the constant commented
*"(empirical)"* — honest about where the number came from.

Semantic recall is a keyed lookup plus a hybrid formatting path for prompt
injection (`:818`), so the two stores serve different questions: the key-value
side answers "what do we know about X", the episodic side answers "what was said
that resembles this".

The markdown half is read on every message turn through `read_recent_history`,
behind a 5-second cache keyed on the day, so the decay window shifting at
midnight invalidates naturally.


## 7. Write Mechanics

Writes are synchronous and gated. The chain in `validate_semantic` runs in a
fixed order — key format, allow-list, reserved prefix, confidence, size,
injection — and returns a `(code, reason)` pair rather than a boolean, so the
caller and the log both learn *which* rule refused.

Conflict resolution is a separate step at `_write_semantic`, and it is
serialized: *"Steps 7-8 (SELECT→conflict-resolve→UPSERT) are serialized"*, with
a `conflict_skip` event carrying the existing `value_json` as `old_value` and the
incoming one as `new_value`. So a declined overwrite leaves both values in the
record, which is more than most systems keep when a write loses.

Deletion is `is_deleted`, set by the dashboard endpoints. Both tables carry an
index on that column, so the read path filters rather than compacts.

The episodic path additionally screens text length and injection patterns before
admission, and its dedup threshold is 0.88 cosine.

**The audit table is bounded.** `rotate_events` deletes the oldest rows past
10,000, so the event log is a rotating window rather than a permanent history.
For a local tool that is a defensible ceiling; it does mean the record of *why*
an early memory was refused is the first thing to go, and those are the events
that would explain how the store came to look the way it does.

Nothing consults `memory_events` before a write. That is the gap section 1
describes, and it is the difference between a system that refuses a value and one
that refuses it *again*.


## 8. Agent Integration

The workspace is the product: desktop app, web dashboard, CLI, and Slack and
Discord bridges that continue the same work from a chat surface. Kiro Crew Apps
bundle an interface with agents, skills, schedules, integrations and backend
services.

The model's authority over memory is deliberately narrow. It cannot write outside
the allow-listed key prefixes, cannot touch the `system.` namespace at all, and
its writes are held to the 0.8 confidence floor that a user's explicit statement
is exempt from. What the agent *can* do freely is add episodic fragments, which
is the lower-stakes half.

The dashboard is a real review surface rather than a viewer: `MemoryTab`,
`MemoryGraphTab` and `VectorMemoryCard` render the stores, the events feed shows
refusals including blocked injections, and `api_memory_semantic_delete` and
`api_memory_episodic_delete` let a person remove an entry. Inspect and adjudicate,
after the fact rather than as a gate.


## 9. Reliability, Safety, and Trust

**`audit_log` — earned, with the ceiling stated.** `memory_events` is an explicit
table in the system's own store recording mutations with `old_value` and
`new_value`, plus four of the seven refusal codes. `rotate_events` trims past
10,000 rows, so it is a rotating window rather than a permanent ledger.

**`human_review` — earned.** The dashboard renders both stores and the event
feed, and the delete endpoints let a person act on what they see. It adjudicates
after the fact rather than gating admission, which is the ordinary form of this
mark.

**`negative_eval` — earned, and the cases are about the right thing.**
`test_memory_graph.py` asserts an AWS access key id is absent from a returned
result's `text` and from its `conversation_id`;
`test_perf_memory_quickwins.py` asserts an embedding BLOB never leaks into a
search result, and that a specific memory is absent from a result set. Committed
cases pinning that particular material stays out of a retrieval, including a
credential.

**`tombstone` — not earned, and the machinery is one query short.** Refusals are
typed, audited and carry the refused value in `new_value`. Nothing reads that
column on the write path, so the same value can be offered indefinitely and is
re-screened by the same pattern list each time. A system that already records
what it refused, keyed near enough to the value to match on, is closer to this
mark than most of the corpus.

**`trust_state` — not earned.** Confidence is a float, `source` is a string, and
`is_deleted` is a flag. The two-tier hierarchy is real but lives in comparisons
(`source != "user_explicit"`) rather than in a field, so nothing records what the
system concluded about a given memory.

**`scope_enforced` — not found.** No user, project or tenant key on either table.

**`bitemporal` — not found.** `created_at`, `updated_at` and `last_accessed_at`
are all record time.

Other observations:

- **The injection screen runs on both stores**, semantic and episodic, with the
  episodic case reasoned about explicitly as persistence of steering
  instructions across sessions.
- **The audit snippet is redacted before storage** because the dashboard renders
  it verbatim — the strongest single piece of security reasoning in this report.
- **`system.` is a reserved namespace** requiring `user_explicit`, so the
  agent cannot write the keys that configure its own behaviour.
- **The whole trust model rests on the `source` string** being passed honestly by
  every caller. There is no signature, no capability, and no check that a caller
  claiming `user_explicit` is one.
- **The event log rotating at 10,000** means a long-running workspace loses its
  earliest refusals first.


## 10. Tests, Evals, and Benchmarks

1,024 test files and 502,973 lines of test code against 475,988 lines of source —
more test than source, which at this size is rare and worth stating plainly.

Ten memory-named test modules, and the names track real risks rather than
coverage: `test_vector_memory.py`, `test_memory_graph.py`,
`test_memory_selfheal.py`, `test_memory_smoke.py`, `test_perf_memory_quickwins.py`,
`test_session_memory.py`, `test_system_memory.py`,
`test_dashboard_sessions_memory.py`, `test_ws_and_plan_memory_fixes.py`.

The negative cases are the strongest part. Asserting that
`AKIAIOSFODNN7EXAMPLE` — a well-known example AWS key id — does not appear in a
result's text *or* its `conversation_id` is a redaction test written by someone
who thought about where else the string could surface. The embedding-leak case is
the same instinct applied to a performance change.

Nothing was run for this review: seven dependency surfaces were inside the
seven-day cooldown, and the tree carries `AGENTS.md` and `CLAUDE.md` addressed to
a reading agent, both treated as data.

What is not established: no measurement of the injection pattern list. It is the
component the whole write gate depends on, and how often it blocks something it
should not — or misses something it should catch — is not answered anywhere in
the repository. A pattern list is a classifier with no reported precision.


## 11. For Your Own Build

### Steal

- **Type your refusals.** `SemanticRejectCode` turns "the write didn't happen"
  into seven distinct, loggable facts. A gate that returns a boolean is a gate
  nobody can operate; a gate that returns `allowlist_reject` versus
  `injection_blocked` is a gate you can build a dashboard on — and they did.
- **Redact the audit record of hostile input.** If you log what an attacker sent
  and then render it in a UI, your security log is an injection and exfiltration
  channel. Scrubbing URLs and credentials from the snippet before it is persisted
  is the fix, and almost nobody does it.
- **Make memory a bounded namespace.** An allow-list of key prefixes, with a
  reserved `system.` namespace only an explicit human source may write, converts
  "what can the agent remember" from a prompt-level hope into a schema-level
  rule.
- **Admit on the raw score, rank on the decayed one.** Filtering on a
  decay-adjusted similarity makes "old" and "irrelevant" the same condition and
  silently loses old material that is exactly on point.
- **Keep a human-editable half.** Three markdown files with comment markers
  explaining what they are for, beside a database that is the index rather than
  the authority for them. Correcting a preference is editing a file.

### Avoid

- **Recording a refusal you never consult.** Seven kinds of "no" written to a
  table that no write path reads means the same value can be proposed forever.
  One query against the refusal log, keyed on the value, converts a screen into a
  memory.
- **A trust model made of string comparisons.** `source != "user_explicit"`
  carries the entire privilege boundary, and nothing verifies that a caller
  claiming that source is entitled to it.
- **Rotating the audit log without saying what it costs.** Ten thousand rows is a
  reasonable ceiling; losing the *earliest* refusals first means losing the ones
  that explain how the store was shaped.
- **An unmeasured pattern list at the centre of a gate.** Everything downstream
  trusts `_contains_injection`, and its precision is unreported.

### Fit

This suits a single operator running a workspace on their own hardware who wants
memory that is governed rather than accumulated. The gate is the product: if you
want an agent that cannot quietly learn arbitrary keys about you, this is the
clearest worked example in the corpus of stopping it at the schema.

It is a whole workspace, not a library. There is no memory package to depend on —
`vector_memory.py` is 2,764 lines coupled to the app's config loader, metrics and
platform helpers — so adoption means adopting Kiro Crew, and reuse means porting
the ideas.

Walk away if you need multi-user or multi-project isolation. There is no scope
key on either table and the design does not anticipate one; retrofitting it is a
migration plus an audit of every read.


## 12. Open Questions

- **How good is the injection pattern list?** It gates both stores and its false
  positive and negative rates are unreported. This is the number the design most
  needs.
- **Does anything verify a `source` claim?** The privilege boundary is a string
  comparison; whether a caller can simply assert `user_explicit` was not traced.
- **What is the conflict resolver's policy?** `conflict_skip` declines a write and
  records both values; on what basis it decides was not read closely here.
- **How often does `rotate_events` fire in a real workspace?** It decides how much
  of the refusal history survives, and nothing reports on it.
- **Do the markdown half and the structured half ever disagree?** Preferences live
  in a file a person edits and also, potentially, as `semantic_memory` keys.
  Nothing was found reconciling them.


## Appendix: File Index

**Storage and schema**
- `src/kiro_crew/vector_memory.py` — schema at `:151`, WAL SQLite, FAISS index
- `src/kiro_crew/memory.py` — markdown workspace and the FTS5 index

**Write gate**
- `src/kiro_crew/vector_memory.py:90` — `SemanticRejectCode`,
  `_AUDITABLE_REJECT_CODES`, `_SECURITY_REJECT_CODES`
- `:475`–`:513` — the validation chain; `:625` — `_write_semantic` and conflict
  resolution; `:1066` — episodic injection screening and redacted audit snippet
- `src/kiro_crew/vector_memory_constants.py` — `_INJECTION_PATTERNS`,
  `_contains_injection`

**Retrieval**
- `src/kiro_crew/vector_memory.py:1335`–`:1600` — admission on raw cosine, decay
  applied for ranking

**Lifecycle**
- `:937` — `rotate_events`

**Human surface**
- `src/kiro_crew/dashboard/handlers/memory.py`,
  `src/kiro_crew/dashboard/session_memory.py`
- `website/src/pages/overview/MemoryTab.tsx`, `MemoryGraphTab.tsx`,
  `VectorMemoryCard.tsx`, `SessionMemoryCard.tsx`

**Tests**
- `test/test_vector_memory.py`, `test_memory_graph.py`,
  `test_perf_memory_quickwins.py`, `test_memory_selfheal.py`,
  `test_session_memory.py`

## History

**2026-08-06** — [`429cbad8cdb7bfbf4c10f6343374565832b176d2`](https://github.com/kirodotdev/KiroCrew/commit/429cbad8cdb7bfbf4c10f6343374565832b176d2) — first reading. Screened before reading: 0 auto-run surfaces, 7 build-time exec paths, 5 unpinned dependency surfaces with seven inside the seven-day cooldown, plus `AGENTS.md` and `CLAUDE.md` addressed to a reading agent. Both read as data; nothing was installed, built or run. The report covers the memory subsystem, not the desktop app, the scheduler or the Apps platform.

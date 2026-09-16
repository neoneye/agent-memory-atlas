---
title: "a-memory"
eyebrow: "Hidden survives a rewrite, because a re-save reads the old flag first"
description: "A four-tier local memory in plain SQLite whose facts carry a visibility that the search and lookup reads exclude, whose every read binds the layer and user from the handle rather than an argument, and whose saves and deletes each append a before-and-after ledger row — all three degrading to a warning rather than failing the write."
root: ../..
page_kind: system
source_name: "Cipher208/a-memory"
source_url: https://github.com/Cipher208/a-memory
archive_name: "Cipher208--a-memory"
revision: 6a9f466353912f8ce0d485cb957949a523074c8e
revision_url: https://github.com/Cipher208/a-memory/commit/6a9f466353912f8ce0d485cb957949a523074c8e
analyzed_at: 2026-09-16
capabilities: "trust_state, scope_enforced, audit_log"
capability_evidence:
  trust_state: "a four-value visibility that the search and key-lookup reads exclude, and which a re-save preserves so a quarantined key cannot be un-hidden by writing to it again | core/__init__.py:63-72, core/memory.py:98, :110-118, :348, :407, :450 | `visibility` is `visible | pinned | private | hidden`, validated on write; `search` selects `WHERE layer=? AND user_id=? AND visibility NOT IN ('private','hidden')` and the key lookup does the same, while the pinned-injection read selects `visibility='pinned'` — with the invariant named in a comment: \"C8: private facts never leave the store via recall (the inject pinned block does not read them).\" Passing `visibility=None` on a re-save re-reads the stored flag before updating, under a dated comment recording the bug it fixes: \"a 'hidden' row re-saved with the same canonical key would otherwise be back to 'visible' — F1 sanitation, 2026-09-12\". The API docstring states the consequence: \"'hidden' works as a key quarantine: future writes update the row but never un-hide it\" | tests/"
  scope_enforced: "layer and user are properties of the handle a caller is given, bound into every core-memory read rather than passed per query | core/__init__.py:38-53, :122-132, core/memory.py:348, :407, :450, core/episodic.py:37, :46-47 | `MemoryManager.get_layer(layer_type, user_id)` returns a `MemoryLayer` that stores both and constructs `EpisodicMemory(layer=layer_type)` and `CoreMemory` beneath it; `user_memory()` and `agent_memory()` are the named accessors. Every `core_memory` read begins `WHERE layer=? AND user_id=?`, and `episodes` carries a `layer` column with two indexes on `(layer, user_id)` — a predicate on a shared table, not a file per layer. A caller holding a user-layer handle has no argument that reaches the agent layer, which is what the README means by \"[u]ser facts and agent identity never share a namespace\" | tests/"
  audit_log: "every save and every delete appends a ledger row carrying the full before and after row as JSON plus what triggered it | core/memory.py:217-231, :120, :128, :363 | `_record_history` is documented as \"[a]ppend one A2.2 ledger row with full before/after row JSON\" and is called from all three mutation paths — the update branch with the old row and the new, the insert branch with `None` as the old, and delete with the row as old and `None` as new, attributed `triggered_by or \"delete\"`. Alongside it `_record_temporal` maintains an interval chain in `core_memory_temporal`, closing the open interval and opening a new one on each write and closing it on delete | core/memory.py:265-300"
stack_storage: "sqlite"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "An L4 core fact — key, value, importance, memory kind, visibility, source, optional TTL — over L3 episodes, an L2 session store and an L1 reflex buffer"
  storage: "Plain SQLite files in one directory, with a persisted L1 buffer, `core_memory`, `core_memory_temporal`, an A2.2 history ledger, `episodes`, and a knowledge graph"
  retrieval: "Hybrid lexical and vector search with a knowledge graph, plus a pinned-facts injection block that reads only `visibility='pinned'`"
  write: "`remember(key, value, importance, source, ttl_minutes, visibility, memory_kind)`, where `source` carries a provenance contract of `user_explicit`, `staging_promotion`, `episode_promotion` or `manual`"
  update_delete: "A re-save updates in place, appends a ledger row and closes the temporal interval; delete does the same with a null after-image. Hidden is sticky across re-saves"
  scoping: "Layer and user bound into the handle — `user_memory()` and `agent_memory()` — and applied as a predicate on every core-memory read, with matching indexes on episodes"
  integration: "An MCP server, hooks, a FastAPI-shaped OpenAPI surface, and a PyPI package with an optional embeddings extra"
  background: "An hourly consolidation sweep promoting episodes into long-term facts, TTL expiry, and per-layer cleanup"
  trust: "A visibility quarantine that survives rewriting, a source provenance contract, a before-and-after ledger, and an interval chain per key"
  strengths: "The `hidden` flag is a quarantine with the right stickiness: a re-save that passes no visibility re-reads the stored value first, so writing to a hidden key updates it without bringing it back — and the comment records the bug and the date that produced the fix (\"F1 sanitation, 2026-09-12\"). `private` and `hidden` are excluded from both read paths under a named invariant, C8, that says the pinned-injection block does not read private facts either. Scope is a property of the handle rather than an argument: `user_memory()` and `agent_memory()` hand back objects carrying their own layer and user, so no caller has a parameter that crosses the boundary. And the ledger is complete across the mutation paths — update, insert and delete each append a row with the full before and after image and an attribution"
  risks: "All three supporting mechanisms are best-effort by design. `_record_history` \"[d]egrades to a warning so memory writes never fail on history\" and `_record_temporal` is \"advisory, never fails a save\", both wrapped in a bare exception handler — so a disk or serialisation failure leaves a gap in the ledger and a broken interval chain while the write itself succeeds, and nothing counts the gaps. The interval chain is not a second time axis: `valid_from` is the write instant, the same clock as `updated_at`, so the point-in-time query answers what the store held at a past moment and not when anything was true in the world. `visibility` is caller-supplied and defaults to visible, so quarantine is an act somebody has to take. At 66,891 lines with 281 test files the tree is large for a project whose README leads with \"plain SQLite files\""
---

## 1. Executive Summary

a-memory is "4-tier agent memory with hybrid search and a real knowledge graph —
all in plain SQLite files. Zero cloud. Zero external APIs." MIT, Python, 66,891
lines with 281 test files and 1,606 test functions, on PyPI, with an MCP server
and an optional embeddings extra.

The four tiers are an L1 reflex buffer (now persisted — "was in-memory only
since forever"), an L2 session store, L3 episodes and L4 core facts. Three
mechanisms in the L4 store are worth the visit, and they share a weakness.

**Visibility is a quarantine that sticks.** A fact carries
`visible | pinned | private | hidden`. Search and key lookup both select
`WHERE layer=? AND user_id=? AND visibility NOT IN ('private','hidden')`, and
the pinned-injection block selects only `visibility='pinned'` — with the
invariant written down beside it: "C8: private facts never leave the store via
recall (the inject pinned block does not read them)."

What makes it a quarantine rather than a flag is the re-save path. Passing no
visibility on a write re-reads the stored one before updating, under a comment
that records both the bug and its date:

> "a 'hidden' row re-saved with the same canonical key would otherwise be back
> to 'visible' — F1 sanitation, 2026-09-12"

So, as the API docstring puts it, "'hidden' works as a key quarantine: future
writes update the row but never un-hide it." A memory suppressed once cannot be
resurrected by writing to it again, which is the failure most systems with a
suppression flag have.

**Scope is a property of the handle.** `MemoryManager.get_layer(layer_type,
user_id)` returns a `MemoryLayer` that carries both and builds its episodic and
core stores beneath it; `user_memory()` and `agent_memory()` are the named
accessors. Every core-memory read begins `WHERE layer=? AND user_id=?`, and
`episodes` carries a `layer` column with two indexes on `(layer, user_id)`.

That is a predicate on a shared table, not a file per layer, and the caller
never passes it — which is what the README's "[u]ser facts and agent identity
never share a namespace" amounts to in code, and the reason it earns the mark
rather than reading as a filing convention.

**Every mutation appends a before-and-after row.** `_record_history` writes "one
A2.2 ledger row with full before/after row JSON" and is called from all three
paths: update with the old row and the new, insert with a null before, and
delete with a null after attributed `triggered_by or "delete"`. Beside it,
`_record_temporal` maintains an interval chain per key in
`core_memory_temporal`, closing the open interval and opening a new one on each
write, with a point-in-time read selecting
`valid_from <= ? AND (valid_to IS NULL OR valid_to > ?)`.

The shared weakness is that the last two are advisory. `_record_history`
"[d]egrades to a warning so memory writes never fail on history"; `_record_temporal`
is "advisory, never fails a save". Both are wrapped in a bare exception handler.
The intent is right — a ledger failure should not lose a memory — but the
implementation drops the record silently, so a gap in the ledger and a broken
interval chain are both invisible after the fact, and nothing counts them.

The interval chain is also not a second time axis. `valid_from` is set to the
write instant, the same clock as `updated_at`, so the point-in-time query
answers what the store held at a past moment rather than when anything was true
in the world. No bitemporal mark is claimed.

## 2. Mental Model

A **layer** is user or agent, and you are handed one rather than naming it.

A **fact** is a key and a value with an importance, a kind, a source and a
visibility.

**Hidden** is a decision about a key that later writes inherit.

A **ledger row** is what changed, with both images and who triggered it.

```mermaid
%% caption: the layer and user are bound into the handle and appear in every read; a re-save with no visibility re-reads the stored flag first, so a hidden key stays hidden
flowchart TB
    MGR["MemoryManager.get_layer(layer_type, user_id)"] --> H["MemoryLayer — carries<br/>layer_type and user_id"]
    H --> UM["user_memory()"]
    H --> AM["agent_memory()"]
    H --> TIERS["L1 ReflexBuffer (persisted) ·<br/>L2 SessionStore ·<br/>L3 EpisodicMemory(layer=…) ·<br/>L4 CoreMemory"]
    W["remember(key, value, …, visibility=None)"] --> EX{"key already exists?"}
    EX -->|"yes, and visibility is None"| REREAD["SELECT visibility FROM core_memory<br/>WHERE entry_id=? — keep the stored flag<br/>('F1 sanitation, 2026-09-12')"]
    REREAD --> UPD["update in place"]
    EX -->|"no"| INS["insert"]
    UPD --> LEDG[("A2.2 ledger row:<br/>old row JSON · new row JSON ·<br/>triggered_by")]
    INS --> LEDG
    DEL["delete"] --> LEDG
    UPD & INS --> TEMP[("core_memory_temporal:<br/>close the open interval,<br/>open a new one at now")]
    LEDG -.->|"'degrades to a warning so memory<br/>writes never fail on history'"| GAP["a failed append is dropped<br/>and nothing counts it"]
    TEMP -.->|"'advisory, never fails a save'"| GAP
    TIERS --> R{"reads"}
    R -->|"search · key lookup"| F1["WHERE layer=? AND user_id=?<br/>AND visibility NOT IN ('private','hidden')"]
    R -->|"pinned injection"| F2["WHERE layer=? AND user_id=?<br/>AND visibility='pinned'<br/>— C8: private facts never leave<br/>the store via recall"]
    TEMP --> AS["point-in-time read:<br/>valid_from <= ? AND<br/>(valid_to IS NULL OR valid_to > ?)<br/>— one clock, the write instant"]
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `core/__init__.py` | `MemoryManager`, `MemoryLayer`, and the tier wiring |
| `core/memory.py` | `CoreMemory`: save, the visibility rules, the ledger, the interval chain |
| `core/episodic.py` | L3 episodes, layer-scoped with its own indexes |
| `core/session.py`, `reflex.py` | L2 and L1 |
| `graph/`, `rag/` | The knowledge graph and hybrid retrieval |
| `lifecycle/`, `features/` | Consolidation, promotion and TTL |
| `mcp_server/`, `hooks/` | The agent surfaces |
| `alembic/` | Schema migrations |

## 4. Essential Implementation Paths

`core/memory.py:110-131` — the re-save that preserves visibility, the ledger
call and the interval close, in one block.

`core/memory.py:398-410` — the search predicate, and the C8 comment.

`core/__init__.py:38-53` and `:122-132` — how a handle comes to carry its own
scope.

## 5. Memory Data Model

An L4 fact is a key, a value, an importance, a memory kind, a visibility, a
source, an optional expiry and a layer and user. `source` is a documented
provenance contract — `user_explicit`, `staging_promotion`, `episode_promotion`
or `manual` — which distinguishes a fact a person stated from one the
consolidation sweep promoted out of an episode. That distinction is the one the
atlas most often finds missing in systems that extract from their own output.

Memory kind is validated and optionally reclassified on save, which makes it a
write-time genre rather than an epistemic state; `importance` is a float.
`visibility` is the discrete field that governs what a reader sees.

## 6. Retrieval Mechanics

Hybrid lexical and vector search over the core store with a knowledge graph
beside it, over-fetching ten times the limit so Python-side ranking can prefer
rows matching more query tokens.

The two exclusions are the part to copy. `private` and `hidden` never appear in
search results or key lookups, and the pinned block that injects facts into
context reads only `pinned` — so the set a model sees is narrower than the set a
search returns, deliberately.

## 7. Write Mechanics

One save path handling both update and insert, each appending a ledger row and
maintaining the interval chain, with delete doing the same in reverse.

The re-save visibility rule is the design decision worth naming: an explicit
`visibility` argument wins, and its absence means *keep what is stored* rather
than *use the default*. Those two readings of a missing argument are easy to
conflate and the difference here is whether a quarantine holds.

## 8. Agent Integration

An MCP server, hooks, and an OpenAPI surface, with the layer accessors as the
integration seam: an agent tool bound to `agent_memory()` cannot reach the user
layer through any argument it accepts.

## 9. Reliability, Safety, and Trust

The three mechanisms above are the trust story and the caveat is uniform: two of
them degrade rather than fail.

A ledger that "never fails a write" is the correct policy and a silent `except`
is the wrong implementation of it, for the same reason it was wrong in the other
systems this atlas has found doing it. The fix is small: count the drops, expose
the count, and a ledger can be both non-blocking and honest about its holes.

The interval chain has the same handling and one further limit — closing and
opening intervals outside a guarantee means a crash between the two statements
leaves a key with either two open intervals or none, and nothing reconciles it.

## 10. Tests, Evals, and Benchmarks

281 test files and 1,606 test functions, with an `eval/` directory, a CI badge
and coverage reporting. The repository also carries an `AUDIT_REPORT_20260629.md`
and an `ARIEL_RULES.md`, so the F1 and C8 labels in the comments appear to index
a review process; that process was not read here.

## 11. For Your Own Build

Decide what a missing argument means, and write it down. `visibility=None`
meaning "keep the stored flag" rather than "use the default" is the whole
difference between a quarantine and a suggestion, and the comment recording the
bug that taught them is what will stop it regressing.

Bind scope to the handle, not the query. `user_memory()` and `agent_memory()`
return objects that carry their own predicate, so isolation is not something a
caller can forget to pass — which is the failure mode this atlas finds in almost
every system whose scope is an argument.

Narrow the injected set further than the searched set. Search excludes private
and hidden; the block that actually reaches the model reads only pinned. Two
different questions, two different predicates.

And if a ledger must never block a write, count what it drops. A silent
`except` turns "we never lose a memory" into "we sometimes lose the record and
cannot tell".

## 12. Open Questions

Whether anything reconciles a broken interval chain. `_record_temporal` closes
and opens in two statements under an advisory handler, and no repair pass was
found.

What the F1, C8 and A2.2 labels index. They read as review findings, and
`AUDIT_REPORT_20260629.md` exists; the relationship was not traced.

Whether `hidden` is reachable from the agent-facing tools. It is a parameter on
`remember`; which surfaces expose it was not established.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `core/memory.py:110-131` | A re-save that cannot un-hide, with the dated bug behind it |
| `core/memory.py:398-410` | The search predicate and the C8 invariant |
| `core/__init__.py:38-53`, `:122-132` | Scope carried by the handle |
| `core/memory.py:217-231` | The before-and-after ledger, and what it does on failure |
| `core/memory.py:265-300` | An interval chain on one clock, and a point-in-time read |

## History

**2026-09-16** — [`6a9f466353912f8ce0d485cb957949a523074c8e`](https://github.com/Cipher208/a-memory/commit/6a9f466353912f8ce0d485cb957949a523074c8e) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: eight files scanned, two auto-run surfaces, one build-time execution point, no unpinned surfaces and two dependency files inside the seven-day cooldown. Nothing was installed, built or run.

---
title: "Cortana"
eyebrow: "A malformed access list is excluded, not treated as empty"
description: "A local-first second brain whose search query validates each row's ACL shape in SQL before matching it, gates every read on a validity window and an active status, and starts query-only until each capability is separately authorised."
root: ../..
page_kind: system
source_name: "adea-ai/cortana"
source_url: https://github.com/adea-ai/cortana
archive_name: "adea-ai--cortana"
revision: 9609d2ab5f916b2795500ed98c57dd2388592144
revision_url: https://github.com/adea-ai/cortana/commit/9609d2ab5f916b2795500ed98c57dd2388592144
analyzed_at: 2026-09-19
capabilities: "trust_state, bitemporal, scope_enforced"
capability_evidence:
  trust_state: "a stored status every recall read requires to be active, with supersession recorded on the row rather than by deletion, and two reads that leave the predicate out on purpose | crates/core/src/store.rs:380 (the column), :1819, :1832, :1880, :1899, :2082, :2792, :3788, :3808, :3861 (the filters), :3755-3762 (the by-id fetch) and :3992-4081 (`export_memories_with_axes_as_owner`) | `memories.status` is `NOT NULL` beside a `supersedes_id`, and `status=active` is composed into the counting read, the update guards, the full-text search, the ACL lookup, the validity stamp and the aggregate rollups — a dozen sites in one file. A superseded memory keeps its row and its `supersedes_id` link and stops being returned, so the correction is recoverable rather than a delete. Two reads omit the clause and both are the right ones: the point read by id returns the row with its `status` column so the caller can see what it got, and the owner export carries the full ACL predicate but no status filter, because an export that dropped superseded rows would be a lossy backup | crates/core/src/store.rs:1899"
  bitemporal: "three time columns kept apart — when it was observed, the window it is valid in, and when the row was written — with the validity window gated by a moment the query is given | crates/core/src/store.rs:383-388, :1820, :2090-2091 | `memories` carries `observed_at`, `valid_from`, `valid_until` and `created_at`/`updated_at` as separate columns. The search gates on the supplied moment in both directions — `AND m.valid_from<=?8 AND (m.valid_until IS NULL OR julianday(m.valid_until)>julianday(?8))` — and the point read applies the same upper bound, so a memory whose validity has not begun or has ended is absent from an answer without being removed from the store | crates/core/src/store.rs:1819"
  scope_enforced: "the access list is applied inside the search query, and a row whose ACL is not a well-formed array of strings is excluded rather than treated as unrestricted | crates/core/src/store.rs:2088, :2093-2111 | Beyond `AND (?6 IS NULL OR m.scope=?6)` and `AND (?7 OR m.scope<>'owner-global')` — an explicit flag a caller must set to reach owner-global rows — the query validates the row's own ACL before matching it: `json_valid(m.acl_json)`, `json_type(m.acl_json)='array'`, and `NOT EXISTS (SELECT 1 FROM json_each(m.acl_json) WHERE type<>'text')`. Only then does it admit the row on an empty ACL or a principal match against the caller's principal list. A malformed ACL therefore fails closed: it matches nothing, instead of degrading to the empty-means-public branch | crates/core/src/store.rs:1819"
stack_storage: "sqlite"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A memory with a kind, content type, retention tier, scope, project, source, dedupe key, confidence, importance, status, an ACL, a provenance document, an observed time, a validity window and a supersession link"
  storage: "Local SQLite with a full-text index over memories, a separate candidate staging table, and consolidation job and control tables"
  retrieval: "BM25 over the FTS index ranked by importance and confidence, gated on status, validity window, scope, the owner-global flag and the ACL"
  write: "Observations become `memory_candidates` with an expiry and a rejection reason; approval by a principal promotes them into `memories`"
  update_delete: "A correction writes a new row carrying `supersedes_id`; the superseded row keeps its place and leaves the active set"
  scoping: "A scope column, an explicit flag for owner-global rows, and a per-row ACL matched against the caller's principals inside the query"
  integration: "A Tauri desktop app, an MCP stdio server, a loopback or explicitly secured HTTP API, and a local-owner CLI"
  background: "Consolidation jobs under their own control table, reconciliation and recurring synchronisation — each a separate authorisation"
  trust: "A candidate queue with expiries and rejection reasons, a provenance document per memory, an ACL validated in SQL, and a posture that starts query-only"
  strengths: "The search query is the artifact to read. It gates on the active status, on both ends of the validity window against a supplied moment, on project, kind, content type and retention tier, on scope with a separate flag before owner-global rows are reachable at all — and then, before matching the access list, it checks the access list's *shape*: `json_valid`, `json_type='array'`, and no element whose type is not text. Only a row that passes admits the empty-ACL-means-unrestricted branch. A corrupted or wrongly-typed ACL is therefore excluded rather than falling through to public, which is the failure direction that matters and the one an application-layer check usually gets wrong by parsing leniently. The product posture matches: \"[a] new installation starts query-only. Source authorization, validation, ingestion, reconciliation, recurring synchronization, model use, shared-agent access, and memory writes are separate explicit decisions\" — eight capabilities, eight decisions, and a statement of what the product is not: \"not an unrestricted crawler, implicit backup service, agent harness, or hosted personal-data warehouse\". Evidence and conclusions are separated too: one canonical evidence store, and \"a separate native memory lifecycle for bounded conclusions\""
  risks: "Approval is by a principal string. `memory_candidates` carries `created_by`, a status guarded by a compare-and-set on `pending`, an expiry and a `rejection_reason`, and the promotion path takes an approving principal — but nothing found establishes that the principal is a person rather than a label, so the queue is a staging and audit mechanism rather than a human-review gate. A rejected candidate's `dedupe_key` is likewise not consulted when the same observation returns: the rejection reason is recorded, and re-offering the same content produces a new candidate. `confidence` and `importance` are continuous and carried into the ranking, so a low-confidence memory is ranked down rather than withheld, and nothing in `provenance_json` gates a read. And the surface is broad for a personal store — a desktop app, an MCP server, an HTTP API, a CLI, OAuth connectors for several providers, fleet and community modules — with one auto-run surface and three unpinned dependency surfaces at this pin"
---

## 1. Executive Summary

Cortana is "a local-first, agent-native second brain for people and the AI agents
that work with them" — Apache-2.0, Rust, version 0.58.2, 138,872 lines with 605
test functions, reachable through a Tauri desktop app, an MCP stdio server, a
loopback or explicitly secured HTTP API, and a local-owner CLI.

Its product statement is a list of refusals before it is a list of features:

> "It is not an unrestricted crawler, implicit backup service, agent harness, or
> hosted personal-data warehouse. A new installation starts query-only. Source
> authorization, validation, ingestion, reconciliation, recurring synchronization,
> model use, shared-agent access, and memory writes are separate explicit
> decisions."

Eight capabilities, eight separate decisions, and a default of query-only. For a
tool whose value proposition is ingesting a person's notes, messages, documents,
calendars and code, starting with none of that enabled is the right default and
an uncommon one.

**The search query is where the care shows.** One statement gates on the active
status, on both ends of a validity window against a supplied moment, on project,
kind, content type, retention tier and scope, on a flag that must be set before
owner-global rows are reachable at all — and then, before it matches the row's
access list, it checks that the access list is *shaped* like one:

```sql
AND json_valid(m.acl_json)
AND json_type(m.acl_json)='array'
AND NOT EXISTS (
  SELECT 1 FROM json_each(m.acl_json) AS memory_acl
  WHERE memory_acl.type<>'text'
)
```

Only a row that passes all three reaches the branch where an empty ACL means
unrestricted or a principal match admits it. So a corrupted, wrongly-typed or
half-written ACL matches nothing rather than falling through to public.

That is the failure direction that matters, and it is the one an
application-layer check usually gets wrong: a lenient JSON parse turns a
malformed ACL into an empty list, and an empty list means everyone. Putting the
shape check in the same statement as the match means there is no window in which
a row is loaded with an ACL nobody validated.

**Three clocks, kept apart.** `observed_at` is when the thing was observed;
`valid_from` and `valid_until` bound the window it applies in; `created_at` and
`updated_at` are when the row was written. The search gates the validity window
in both directions against the moment it is given, so a memory whose validity has
not begun, or has ended, is absent from the answer without being removed from the
store.

**A correction keeps the corrected row.** `supersedes_id` links a new memory to
the one it replaces, and the superseded row keeps its place while leaving the
active set — recoverable rather than deleted, which is what makes the
supersession link worth storing.

**Candidates are staged, with reasons.** An observation becomes a
`memory_candidate` carrying a scope, a sensitivity, an ACL, a provenance
document, an expiry and — if it is turned down — a `rejection_reason`, under a
status transition guarded by a compare-and-set on `pending`. Promotion into
`memories` takes an approving principal.

What that queue is not, yet, is a human-review gate: the approving principal is a
string, and nothing found establishes it as a person rather than a label — the
same gap this atlas noted in [Edda](../edda/)'s verdicts. And a rejected
candidate's `dedupe_key` is not consulted when the same observation arrives
again: the rejection is recorded, and re-offering the content produces a new
candidate rather than meeting the old refusal.

The remaining caveats are ordinary. `confidence` and `importance` are continuous
and feed the ranking, so a low-confidence memory is ranked down rather than
withheld; `provenance_json` is carried and not gated on; and the surface is broad
for a personal store — desktop, MCP, HTTP, CLI, OAuth connectors, fleet and
community modules — with one auto-run surface and three unpinned dependency
surfaces at this pin.

## 2. Mental Model

A **capability** is off until somebody turns it on, one at a time.

A **memory** is active, within its window, and on your access list — or it is not
in the answer.

A **malformed access list** protects nothing, so it grants nothing.

A **correction** writes a new row and points back.

```mermaid
%% caption: one query gates status, both ends of the validity window, scope, the owner-global flag, and the ACL — validating the ACL's shape before matching it, so a malformed list fails closed
flowchart TB
    OBS["an observation from an authorised source"] --> CAND[("memory_candidates: scope · sensitivity ·<br/>acl_json · provenance_json · confidence ·<br/>importance · expires_at · rejection_reason ·<br/>created_by")]
    CAND --> DEC{"status transition,<br/>guarded on 'pending'"}
    DEC -->|"rejected"| REJ["status='rejected' + a reason<br/>— the dedupe_key is NOT consulted<br/>when the same content returns"]
    DEC -->|"approved by a principal"| MEM[("memories: status · scope · acl_json ·<br/>provenance_json · observed_at ·<br/>valid_from · valid_until ·<br/>supersedes_id · created_at")]
    CORR["a correction"] --> NEW["a new row carrying supersedes_id"]
    NEW --> MEM
    NEW -.->|"the superseded row keeps its place<br/>and leaves the active set"| MEM
    Q["search(query, moment, principals, flags)"] --> G1["m.status = 'active'"]
    G1 --> G2["m.valid_from <= moment AND<br/>(m.valid_until IS NULL OR valid_until > moment)"]
    G2 --> G3["project · kind · content_type ·<br/>retention_tier · scope filters"]
    G3 --> G4["?7 OR m.scope <> 'owner-global'<br/>— a flag the caller must set to reach<br/>owner-global rows at all"]
    G4 --> SHAPE{"is the row's ACL SHAPED like an ACL?<br/>json_valid · json_type='array' ·<br/>no element whose type is not text"}
    SHAPE -->|"no"| CLOSED["excluded — a malformed ACL matches<br/>nothing rather than degrading to<br/>'empty means unrestricted'"]
    SHAPE -->|"yes"| MATCH{"empty ACL, or a principal match<br/>against the caller's list (or '*')"}
    MATCH -->|"no"| CLOSED
    MATCH -->|"yes"| RANK["bm25 × importance × confidence × recency"]
    POSTURE["a new installation starts query-only;<br/>eight capabilities are eight separate<br/>explicit decisions"] -.-> OBS
```

## 3. Architecture

| File | Role |
| --- | --- |
| `crates/core/src/store.rs` | The schema, the gated search, the candidate lifecycle (11,171 lines) |
| `src/api.rs`, `src/mcp.rs` | The HTTP and MCP surfaces |
| `src/consolidation.rs`, `src/derived.rs` | Consolidation jobs and derived state |
| `src/knowledge_graph.rs`, `src/context.rs` | The graph and context compilation |
| `src/auth.rs`, `src/device_identity.rs` | Principals and device identity |
| `apps/desktop/` | The Tauri application |

## 4. Essential Implementation Paths

`crates/core/src/store.rs:2075-2114` — one query, and everything it refuses to assume.

`crates/core/src/store.rs:366-412` — memories and their staging table, side by side.

`crates/core/src/store.rs:3271` — a rejection that records its reason under a compare-and-set.

## 5. Memory Data Model

Both tables carry `acl_json` and `provenance_json` from the candidate stage
onward, so an observation's access list and its provenance exist before it is
promoted rather than being attached afterwards. `retention_tier` and
`content_type` sit beside `kind`, separating how long something is kept from what
kind of thing it is — two questions frequently collapsed into one field.

## 6. Retrieval Mechanics

BM25 over the FTS index, ordered by score then importance, confidence and
recency, behind the gates above. The ordering puts the lexical match first and
uses the stored weights to break ties, which keeps a high-importance memory from
dominating an unrelated query.

## 7. Write Mechanics

Staged, expiring candidates promoted by an approving principal, with corrections
writing new rows. The expiry on a candidate is the detail worth noting: an
observation nobody rules on does not sit in the queue indefinitely.

## 8. Agent Integration

Four surfaces, and shared-agent access as one of the eight decisions rather than
a consequence of installing.

## 9. Reliability, Safety, and Trust

The ACL shape check is the strongest single thing here, and the query-only
default is the posture that makes the rest coherent. The gap is the identity
behind an approval.

## 10. Tests, Evals, and Benchmarks

605 test functions, with an `eval/` directory beside the source. Nothing was
built or run for this reading.

## 11. For Your Own Build

Validate the access list's shape where you match it. A lenient parse turns a
malformed ACL into an empty one, and an empty one usually means everybody.

Gate both ends of a validity window. Checking only the end lets a memory that has
not started applying answer a question about today.

Keep the superseded row. A `supersedes_id` and a status change cost one column
each and make a correction inspectable.

Start query-only, and make each capability its own decision. Eight decisions is
more friction than one; ingesting somebody's calendar because they installed a
note-taker is worse.

And expire the candidates nobody ruled on. A review queue without an expiry
becomes a backlog, and a backlog becomes a default.

## 12. Open Questions

Whether an approving principal is ever established as a person. The column and
the compare-and-set are there; the identity check was not found.

Whether a rejection is ever consulted again. `dedupe_key` and `rejection_reason`
are both stored and no write path reads the pair.

What `provenance_json` is used for. It is carried from candidate to memory and no
read gates on it.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `crates/core/src/store.rs:2075-2114` | An ACL validated before it is trusted |
| `crates/core/src/store.rs:366-412` | Three clocks, an ACL, and a staging table |
| `crates/core/src/store.rs:3271` | A rejection with a reason, guarded |

## History

**2026-09-19** — [`9609d2ab5f916b2795500ed98c57dd2388592144`](https://github.com/adea-ai/cortana/commit/9609d2ab5f916b2795500ed98c57dd2388592144) — `trust_state` re-tested. Every anchor in this report pointed at `src/store.rs` and the file is now at `crates/core/src/store.rs` — the repository became a Cargo workspace since the previous pin, so thirteen citations across three marks and the file index were dead paths. They are re-mapped, with line numbers shifted by one or two. The mark holds and is wider than recorded: `status='active'` is composed into a dozen reads in that one file — the counting read (`:1819`), the update guards (`:1832`, `:1880`), the upsert (`:1899`), the full-text search (`:2082`), a second count (`:2792`), the ACL lookup (`:3788`), the validity stamp (`:3808`) and the aggregate rollups (`:3825-3893`) — against the record's five. Two reads omit it, and both are the ones that should: the point read by id (`:3755-3762`) returns the row with its `status` column so the caller sees what it got, and `export_memories_with_axes_as_owner` (`:3992-4081`) carries the full ACL predicate but no status filter, because an export that dropped superseded rows would be a lossy backup. The record now says so rather than claiming the predicate is universal. Screened again first; nothing was installed and no suite was run.

**2026-09-16** — [`9609d2ab5f916b2795500ed98c57dd2388592144`](https://github.com/adea-ai/cortana/commit/9609d2ab5f916b2795500ed98c57dd2388592144) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: eighteen files scanned, one auto-run surface, one build-time execution point, three unpinned surfaces and ten dependency files inside the seven-day cooldown. Nothing was installed, built or run.

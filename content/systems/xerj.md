---
title: "XERJ"
eyebrow: "Agent memory inside a search engine"
description: "A Rust search engine whose agent-memory API is a reserved index per namespace, with bitemporal graph edges whose identity is a hash of the source file's mtime — so an invalidation keyed on the edge id does not survive the file being saved again."
root: ../..
page_kind: system
source_name: "xerj-org/xerj"
source_url: https://github.com/xerj-org/xerj
archive_name: "xerj-org--xerj"
revision: f54eead8097fc234d0815ce245613870dcf22ffd
revision_url: https://github.com/xerj-org/xerj/commit/f54eead8097fc234d0815ce245613870dcf22ffd
analyzed_at: 2026-09-13
capabilities: "bitemporal, scope_enforced, audit_log, negative_eval"
capability_evidence:
  bitemporal: "graph edges — validity time is the source file's mtime, record time is the indexing run's clock | engine/crates/xerj-autoindex/src/detect/mod.rs:560-585, engine/crates/xerj-api/src/graph_api.rs:214-216, :455-505, :556-562 | the edge mapping carries `valid_at`, `invalid_at` and `created_at` as three separate date fields. The autoindex writer fills `valid_at` from `d.valid_at_ms`, which every detector sets to the source file's mtime, and `created_at` from the run's `created_at_ms`, commented as the one non-deterministic field that never participates in the edge id — so the two clocks are populated from genuinely different sources rather than from one `now`. `POST /_graph/{brain}/link` takes both from the request body independently, and `DELETE /_graph/{brain}/link/{id}` takes `invalid_at` (when the fact stopped being true) while stamping `expired_at` at server now, which the handler's own doc calls the bi-temporal pair | engine/crates/xerj-api/src/graph_api.rs:1687-1750"
  scope_enforced: "recall and the raw index surface — a credential's granted index names applied as a predicate that narrows a wildcard search | engine/crates/xerj-api/src/authz.rs:262-281, engine/crates/xerj-api/src/memory_api.rs:349, :541, :1271, :1358, :1402 | each namespace is a reserved index `.xerj-memory-{ns}`, which on its own would be a physical partition rather than this mark. The predicate is the layer above it: all five `/_memory` handlers call `authorize_memory_namespace` before touching anything, and a wildcard read is not refused but expanded over the principal's visible set, so `POST /_all/_search` from a credential granted only `alice` is answered 200 with none of `bob`'s rows in it. Graph coupling re-authorizes separately against the edges index, so a grant over the notes does not carry the link graph | engine/crates/xerj-api/tests/brain_is_a_security_boundary.rs:220-235"
  audit_log: "a hash-chained append-only log in the node's own data directory, reloaded on boot | engine/crates/xerj-engine/src/audit.rs:1-60, :89, engine/crates/xerj-api/src/audit_mw.rs:351-403 | entries are appended to `<data_dir>/audit.jsonl` and each hashes over its predecessor, so an edit breaks the chain at the modified position and every entry after it; `GET /_audit/_search` reads it and `/_audit/_verify` walks it. The producer is `audit_middleware`, mounted on both routers, which records every mutating request that gets past authentication and every read that came back 403. Two boundaries the module states itself: the ring holds 4,096 entries and the file converges to it, and there is no `fsync` per entry, so a power loss can take the unflushed tail | engine/crates/xerj-api/tests/audit_records_writes_and_who.rs"
  negative_eval: "four committed cases asserting one tenant's memory must not come back through any other door | engine/crates/xerj-api/tests/brain_is_a_security_boundary.rs:130-240, engine/crates/xerj-console-api/tests/console_cannot_read_a_brain.rs:30, :81, :119-140 | `seed_two_brains` links an edge into `alice` and one into `bob`, refreshes bob's backing index so the row is demonstrably searchable, then walks the graph API, the raw index surface, percent-encoded spellings, the native router and `/_memory` with a minted non-admin key. The console suite seeds the literal `alice-private-fact-9f83c1` and asserts it appears in no response body. The vacuity guard is a separate positive control: `a_scoped_caller_retains_full_use_of_its_own_brain` asserts alice's own edge IS returned, and `cat_indices_keeps_the_rows_it_should` asserts the caller's own index is present and that exactly one row came back | `cargo test`; not run — 21 dependency manifests are inside the 7-day cooldown"
stack_storage: "files"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A document with `text`, optional `metadata` and `vector`, and one `stored_at` timestamp, in a namespace that is a reserved index; plus a separate edge record linking node ids with a validity window"
  storage: "The engine's own on-disk indices — one reserved index per namespace, a second one per brain for edges, and an append-only `audit.jsonl` beside them"
  retrieval: "BM25, server-side semantic kNN, an explicit caller vector, or `hybrid` fusing the first two by reciprocal rank; optional metadata filter, recency blend, and a graph restrict or blend over the brain's edges"
  write: "A single synchronous store call; the memtable is always visible, so a memory is recallable immediately with no refresh wait"
  update_delete: "Memories are hard-deleted by id or by dropping the namespace. Edges are soft-invalidated and never removed, so `as_of` stays answerable"
  scoping: "A reserved index per namespace, plus an index-name grant on the credential applied on every `/_memory` handler and as an expansion filter on wildcard reads"
  integration: "An MCP server with six memory and brain tools, a CLI, an ES-compatible HTTP surface and a native router"
  background: "An autoindex daemon that watches a folder, runs eight deterministic detectors and reconciles the edge set, soft-invalidating edges taught by files that left the corpus"
  trust: "None as a status. Each edge carries a `confidence` float and a `detector` tag, both stored and echoed and neither read by any query"
  strengths: "Two clocks populated from different sources rather than from one `now`; a tenant boundary tested through every door that reaches the backing index, including the percent-encoded spelling"
  risks: "Invalidation is keyed on an edge id derived from the source file's mtime, so saving the file re-teaches the same claim under a new id; `confidence` is stored and never consulted"
---

## 1. Executive Summary

XERJ is a local search engine written in Rust — Apache-2.0, about 380,000 lines
across sixteen crates, shipping as a single static binary with an
Elasticsearch-compatible HTTP surface. Agent memory is one API on that engine:
`/_memory/{namespace}`, five endpoints, implemented in a 2,306-line adapter that
does not re-implement search. A namespace is a reserved index
(`.xerj-memory-{ns}`), so store and recall reuse the same BM25, `dense_vector`
and metadata-filter paths the rest of the engine serves.

That framing is the design's best idea and the source of its sharpest defect,
and both are worth reading.

The best idea is that memory built on a real search engine inherits things
memory libraries usually reimplement badly. Recall has four modes — an explicit
caller vector, server-side `semantic` embedding, plain BM25, and `hybrid: true`
fusing the last two by reciprocal rank — and all four run offline, because the
built-in embedder is lexical feature hashing rather than a model. A write is
visible immediately: `IndexDocParams.refresh` is documented as "accepted without
error; memtable is always visible", so there is no refresh lag between storing a
memory and recalling it. And the tenant boundary is enforced where a search
engine actually leaks, which is not at the memory API at all.

The defect is in the graph layer above it. Edges between memories carry a
genuine bitemporal record — `valid_at`, `invalid_at` and `created_at` as three
separate fields, with the first two independently settable by the caller.
Edge identity is `xxh3_128(src, type, dst, valid_at)`, and `valid_at` for a
detector-taught edge is the source file's mtime. Invalidation, though, is keyed
on the edge id: `DELETE /_graph/{brain}/link/{edge_id}`. Save the file again and
the mtime changes, the hash changes, and the same `(src, type, dst)` claim is
re-taught under an id the invalidation never covered. The record of the
rejection survives; what it rejected comes back beside it.

Four marks. `bitemporal` is earned on two clocks filled from different sources
rather than from one `now`, which is the distinction the mark turns on.
`scope_enforced` and `negative_eval` rest on the same test file, which is
unusual enough to describe precisely in section 10. `audit_log` is earned on a
hash-chained log that states its own coverage boundaries in its module doc.
`tombstone`, `trust_state` and `human_review` are withheld, each for a reason
given in section 9.

## 2. Mental Model

A memory is a document in an index named after its namespace. There is no
extraction step, no consolidation pass, and no model in the write path: what the
agent sends is what is stored, plus a `stored_at` timestamp. The only write-time
judgement available is `dedup: true`, which probes for the single nearest
existing memory and skips the write when its cosine score meets a threshold
defaulting to 0.95 — returning `{created: false, deduplicated: true}` with the
existing id.

The epistemic machinery is not on the memories. It is on the *edges between
them*, which is what makes this system worth reading beside simpler stores. An
edge asserts that one node relates to another, from some instant onward, as
judged by some detector, with evidence attached. It can later be judged to have
stopped being true — soft-invalidated, never deleted, so a reader can still ask
what the graph believed last Tuesday.

Two clocks carry that. `valid_at` is when the fact became true; `created_at` is
when the system recorded it. For an edge a detector taught, those come from
different places: `valid_at` is the source file's mtime and `created_at` is the
indexing run's wall clock. The autoindex module says so where it builds the
document — `created_at_ms` is "the one non-deterministic field and never
participates in `edge_id`". Invalidation adds the mirror pair: `invalid_at` is
when the fact stopped being true, caller-settable; `expired_at` is always server
now.

The gap is that identity is derived from one of those clocks and invalidation is
keyed on identity. An edge is `xxh3_128(src, type, dst, valid_at)`. Unlinking
stamps `invalid_at` on that id. Re-detecting the same relationship from a file
whose mtime has moved computes a different id, and the new edge is written with
`invalid_at` omitted — which, by the module's own stated discipline, is the
signal for "still valid".

```mermaid
%% caption: an edge's identity hashes the source file's mtime into itself, so a person's invalidation — keyed on that identity — stops applying the moment the file is saved again, and the same claim returns live beside the rejection that still describes the old id
flowchart TD
    F["a.md saved at mtime T1"] --> D["detector reads the file"]
    D --> E1["edge id = hash of src, type, dst, T1<br/>valid_at = T1 (file mtime)<br/>created_at = run clock<br/>invalid_at omitted"]
    E1 --> L["live: matched by as_of >= T1"]
    L --> U["person judges the claim wrong<br/>DELETE /_graph/b/link/{id}"]
    U --> I["same document re-indexed<br/>invalid_at set, expired_at = now<br/>nothing is deleted"]
    I --> H["excluded from ego and overview<br/>returned again by include_expired"]
    H --> S["a.md saved again, mtime becomes T2"]
    S --> D2["detector reads the file again"]
    D2 --> E2["edge id = hash of src, type, dst, T2<br/>a DIFFERENT id<br/>invalid_at omitted again"]
    E2 --> L2["live: the same claim, rejected once,<br/>asserted again under a new identity"]
    H -.->|"the rejection is still on disk,<br/>keyed on an id nothing now produces"| L2
```

## 3. Architecture

One static binary, no JVM, no second datastore. `xerj --data-dir ./data` starts
a node; the memory API needs nothing else running. The sixteen crates split the
engine (`xerj-engine`, `xerj-storage`, `xerj-fts`, `xerj-vector`, `xerj-query`)
from the surfaces over it (`xerj-api`, `xerj-mcp`, `xerj-console-api`,
`xerj-server`), and agent memory lives entirely in `xerj-api`:
`memory_api.rs` (2,306 lines), `graph_api.rs`, `authz.rs` and `audit_mw.rs`.

What an operator stands up is therefore a search node, with a search node's
costs and a search node's operational surface. A namespace costs one index. The
audit log is one bounded file in the data directory. Embedding is in-process and
offline by default — the built-in embedder is lexical feature hashing, and the
neural one is opt-in and downloads roughly 90 MB — so recall has no external
dependency and no per-call cost to anything outside the box.

Authorization is two layers, and the second one is the point. `auth_middleware`
resolves an API key to a `Principal`; `authz_middleware` classifies the request
path into a target and checks the privilege. A `Principal::Scoped` carries role
descriptors naming index patterns. Because a namespace is an ordinary index with
a leading `.`, the memory data is reachable through the generic ES-compat
surface and the native router as well as through `/_memory`, and the
authorization layer has to cover all of them — which is exactly what the test
described in section 10 walks.

The console is a separate application merged onto the engine routers *after*
their layers are applied, so `authz_middleware` never runs on `/_xerj-console/*`.
That is stated in the console test's own header, and the fix is in the proxy
rather than in the middleware: the data-sources handlers refuse the reserved
namespace themselves, returning the same `404` they give `.xerj_*` system
indices so existence does not leak.

## 4. Essential Implementation Paths

- **Store** — `memory_api::store` (`:338`): validate the namespace, authorize
  `WriteIndex`, reject an entry with neither `text` nor `vector`, create the
  backing index lazily with a `dense_vector` sized to the supplied embedding,
  run the dedup probe when asked, then `es_compat::index_doc` with
  `{text, stored_at, metadata?, vector?}`.
- **Recall** — `memory_api::recall` (`:530`): authorize `ReadIndex`; reject a
  body that is not exactly one of `vector` or `query`; resolve the fusion
  strategy; over-fetch when recency blending or graph blending is on; authorize
  the *edges* index separately when `graph` is present; fold a graph `restrict`
  expansion into the filter as an `ids` clause; then `es_compat::search`.
- **Namespace validation** — `validate_namespace` (`:106`): lowercase, digits,
  `_`, `-` and `.` only, no `..`, 200 characters, and a refusal of any namespace
  ending `-edges`, because brain `B` keeps its edges in `.xerj-memory-{B}-edges`
  and a namespace called `kb-edges` would write memories into another brain's
  edge index.
- **Edge assertion** — `graph_api::link` (`:407`): validate, authorize, reject
  self-edges, clamp `weight` and `confidence` to `[0, 1]`, parse `valid_at` and
  `created_at` independently, derive the id, write with `invalid_at`/`expired_at`
  omitted.
- **Edge invalidation** — `graph_api::unlink` (`:567`): authorize before the
  existence probe so an unauthorized caller cannot tell "not yours" from "not
  there", read the document, refuse a second invalidation by reporting
  `already_invalid_at`, re-index the same id with the pair added.
- **Audit** — `audit_mw::audit_middleware` (`:356`): classify the request,
  resolve the subject before the handler for a write and only on a 403 for a
  read, append op, subject, resource, outcome and note.

## 5. Memory Data Model

A memory document is small and flat:

```json
{ "text": "...", "stored_at": 1757790000000, "metadata": {...}, "vector": [...] }
```

`text` is mapped as `semantic_text`, so the engine auto-embeds it at ingest into
a companion vector and server-side `semantic` recall works without the caller
embedding anything. `metadata` is deliberately *not* explicitly mapped, so
arbitrary agent-supplied keys are accepted. There is one timestamp. There is no
namespace field on the document — the namespace is the index name — and no
status, source, or confidence field of any kind.

An edge document is where the modelling effort went:

```json
{ "edge_id": "...", "src": "...", "dst": "...", "type": "mentions",
  "weight": 1.0, "confidence": 0.95, "detector": "wikilink@1",
  "valid_at": 1753600000000, "created_at": 1757790000000,
  "schema_version": 1, "src_file": "alpha.md",
  "evidence": { "quote": "...", "source": "alpha.md", "offset": 0 } }
```

Three discipline decisions are worth copying. `invalid_at`, `expired_at` and
`src_file` are *omitted* rather than set to null when unset, because omission
lands the row in the doc-values null bitmap, and that bitmap is the "still
valid" signal the hop reads. Scalars are plain strings and numbers rather than
nested objects, so the prefilter rides doc values. And `schema_version` is on
every row.

`confidence` is the field to look at twice. It is validated, clamped, stored and
returned in the ego response. A tree-wide search for readers outside the writer,
the autoindex and the MCP proxy returns nothing: no query filters on it, no
ranking consults it, no threshold compares against it. The ranking uses `weight`.
`confidence` is a number the system records and never acts on.

## 6. Retrieval Mechanics

`_recall` rejects unknown keys with a 400 under `deny_unknown_fields`, and the
comment says why: a typo'd key used to be silently ignored, degrading the request
to a match-all that returned arbitrary memories at score 1.0. The same reasoning
produced the hard 400 on a body with both `vector` and `query`, or neither.
For a store an agent is meant to trust, turning a malformed recall into a
refusal rather than into plausible noise is the correct trade.

Four single modes, tried in order: an explicit `vector` runs kNN; `semantic:
true` embeds `query` server-side with the same embedder used at store time;
plain `query` runs BM25; and `hybrid: true` runs the BM25 and semantic legs over
the same `query` and fuses them through the engine's `hybrid` query type,
reciprocal rank by default or `fusion: "linear"` on request. `fusion:
"learned"` is a 400 rather than a silent substitution of RRF, "because
substituting RRF would misrepresent the ranking asked for".

`filter` is a standard ES clause applied as a `bool` filter, so it narrows
without scoring. `recency_weight` blends `(1 - w) * norm_score + w *
norm_recency` with both terms min-max normalised across the candidate set, and
over-fetches `max(k * 4, 50)` candidates first — because a re-rank can only
promote what was fetched.

Graph coupling has two modes. `restrict` expands the seeds first and folds the
reachable id set into the filter as an `ids` clause, capped at 10,000 so the
prefilter stays bounded; recall itself is unchanged, it just runs over a
graph-bounded universe. `blend` lets graph proximity pull related memories up,
over the same widened candidate pool. Hops are capped at 1 or 2, and a 3-hop
request returns a 400 carrying a fixed sentence about not being a graph
database. A missing edges index is not an error — recall proceeds ungated and
flags it in-band, so an agent can opt into graph recall before its first link
exists.

## 7. Write Mechanics

Writes are synchronous and singular. One `POST` stores one memory; there is no
batching endpoint on the memory API, no queue, and no background consolidation
pass that rewrites stored memories. The agent blocks for the duration of one
index call.

The lag before a memory is retrievable is zero, which is unusual for an
ES-compatible surface and is stated in the parameter's own documentation:
`refresh=true|wait_for` is "accepted without error; memtable is always visible".
A memory stored in one turn is recallable in the next with no refresh call.

`dedup` is opt-in and best-effort by construction. Any probe error — an empty
index, a schema mismatch — is treated as "no duplicate", so dedup never blocks a
legitimate write. It is off by default so existing callers keep storing every
entry.

The background writer is the autoindex daemon, and it writes edges rather than
memories. Eight deterministic detectors run with no model in the path; the same
corpus produces a byte-identical edge set on every run given unchanged mtimes.
The reconcile pass soft-invalidates edges taught by files that left the corpus
and edges pointing at a superseded anchor, and a `#868` assertion pins that an
unchanged file's own edges are left alone.

## 8. Agent Integration

`xerj init` wires the node into Claude Code or Cursor in one command. The MCP
server exposes eleven tools, six of them memory-shaped: `xerj_memory_store`,
`xerj_memory_recall`, `xerj_brain_ego`, `xerj_brain_link`, `xerj_brain_unlink`
and `xerj_brain_overview`.

Two details of that surface matter. The namespace is a model-supplied argument
on both memory tools — the model names the scope it reads and writes — and what
keeps that honest is that the credential the MCP server holds constrains which
namespaces the request can reach at all. The scope key is on the credential, not
in the arguments, so a model that asks for someone else's namespace gets a 403
rather than their memories.

The second is `xerj_brain_link`'s schema, which exposes `valid_at` to the model
with the description "When the fact became true: epoch-ms number or RFC3339
string (default now). Part of the deterministic edge_id." It does not expose
`created_at`; `build_brain_link` forwards exactly `evidence`, `weight`,
`confidence` and `valid_at`. So through MCP the agent chooses when a fact became
true and the server keeps when it was recorded — which is the clean division the
bitemporal mark asks for, achieved by leaving one field out of a tool schema.

## 9. Reliability, Safety, and Trust

**Scope — earned, and not on the partition.** A namespace being its own index
is a physical partition, which on its own is a different mechanism from this
mark. The predicate is above it: all five `/_memory` handlers call
`authorize_memory_namespace` first, and a wildcard read is expanded over the
principal's visible set rather than refused. The module comment records why
refusal was rejected — it "cost every legitimate `logs-*` grant" — and expanding
is both usable and closed.

Worth flagging for a reader who greps before running: `memory_api.rs`'s own
"Authorization model" header says there is "**no per-namespace authorization**"
and that any credential reaching the node can read and drop every namespace,
pointing at "the deferred RBAC enforcement" as the fix. At this commit that
paragraph understates the code beneath it — the five handlers authorize, the
edges index is authorized separately for graph coupling, and the security-boundary
suite asserts the denials with a minted non-admin key. An operator who reads the
warning and deploys accordingly would be provisioning around a limitation that
the tree no longer has.

**Audit — earned, with the ring stated.** Hash-chained, restart-surviving,
`GET /_audit/_search` and `/_audit/_verify`. Reading the audit log gets its own
op tag rather than the generic `search`, "a refused attempt to read the evidence
is the denied read an auditor most wants to find, and it must not read like a
denied data search". The module doc is candid about coverage: successful reads
other than `_search` leave nothing, unauthenticated attempts are not recorded
because the middleware runs inside authentication and otherwise anyone reaching
the port could flush the ring, and nothing older than 4,096 entries survives.

One imprecision. `_recall` is absent from `is_read_shaped`, so a recall falls
into the mutating branch and takes an entry with op `memory.post` on resource
`_memory` — the endpoint, not the namespace. The useful entry for the same
request comes from `es_compat::search` instead, which appends `op: "search"`
against the real `.xerj-memory-{ns}` index name. An auditor gets the namespace;
they get it from the second entry, and the first spends a ring slot recording a
read as a write.

**Tombstone — withheld, and this is the report's main finding.** The mark asks
for a durable record of a rejected value, *keyed on the value*, so later
extraction cannot re-assert it. `unlink` is keyed on the edge id, and the edge id
is `xxh3_128(src, type, dst, valid_at)` where `valid_at` for a detector-taught
edge is the source file's mtime. Save the file and the id changes. The
invalidated row stays on disk, correct and queryable through `as_of`, describing
an identity nothing will compute again, while the same `(src, type, dst)` claim
is re-taught live beside it. A full re-detection has the same effect by a second
route: `detect::assemble` builds each document with `invalid_at` omitted and
writes it with a bulk `index` action, which is a full replace of whatever sat
under that id. No test in the tree covers a manually unlinked edge surviving a
re-index; the search is in the appendix.

This is worth separating from the reconcile sweep, which is sound. Edges taught
by a departed file, and edges pointing at a superseded anchor, *are* invalidated
on a fresh run, with a test carrying an explicit fail-before note. The gap is
specifically between a human judgement about a claim and an identity derived
from a file's timestamp.

**Trust state — withheld.** `confidence` is a float, and a score is not a state;
more to the point it is read by nothing, so it does not even rank. A tree-wide
search for a discrete status on a memory or an edge returns only a console user
account's `Pending`.

**Human review — withheld.** There is no approval surface. A search for
`approve`, `adjudicat` and `curat` across the console source returns nothing,
and the console's relationship to memory is the opposite of review: the
data-sources proxy is required to refuse the reserved namespace outright.

## 10. Tests, Evals, and Benchmarks

`brain_is_a_security_boundary.rs` is 692 lines and is the artifact to read. Its
header explains that it is "the inverted descendant of
`brain_is_not_a_security_boundary.rs`, which pinned the measured fact that one
did *not* exist" — a committed test that asserted the system's own absence of a
boundary, later rewritten assertion by assertion into its opposite. The
predecessor is not in the tree at this commit.

Its reasoning about scope is the part worth stealing: "the exposure was never
about the four `/_graph/*` handlers", because the edges live in an ordinary index
that `IndexName::validate` admits, reachable through the ES-compat surface and
the native router. "An access check on `/_graph/*` alone would have left all of
that open — a boundary that only looks like one. So this test walks every door,
and a fix that closes only some of them fails here." The doors include the
percent-encoded spelling `/%2Exerj-memory-bob-edges/_search`, "in case the check
compared raw path text".

It is not vacuous, and the guard is structural. `seed_two_brains` writes a real
edge into each of two brains and refreshes bob's backing index, so the row is
demonstrably searchable before anything asserts it cannot be seen.
`a_scoped_caller_retains_full_use_of_its_own_brain` is a dedicated positive
control asserting alice's own edge comes back. `cat_indices_keeps_the_rows_it_should`
asserts both halves at once: the caller's own index is present, *and* exactly one
row was returned.

One honest limit. The four wildcard assertions in section 2b are of the form
`!resp.to_string().contains("bob")` with the status asserted 200, and no
assertion in that loop that the expansion returned any of alice's own rows. An
expansion that returned nothing would satisfy them. The positive control for
that pruning path exists on `_cat/indices` rather than on `_search`.

`soft_invalidate_time_travel` is the bitemporal case and carries its own
controls: the belief *before* the invalidation instant is asserted at four edges
with `expired_excluded == 0`, the belief after at a specific three-id list with
`expired_excluded == 1`, and `include_expired: true` returns the fourth carrying
its pair. Fixture instants are pinned rather than `now` "so a link and the
`as_of` that reads it back can never land in the same millisecond".

The graph detectors carry a measurement rather than a benchmark score. Over 240
arXiv PDFs in 24 topic folders, the seven structural detectors produced 11,854
edges and `sharedterm` added 462, and the project reports that a random pair of
those documents shares a top-level topic 17.0% of the time while `shared_term`
links do so 35.9% — "about twice chance. Read that as the honest strength of the
signal — useful, and no substitute for reading the evidence on the edge." The
same passage instructs against overclaiming its own feature: "Describe it as
shared vocabulary, never as semantic understanding."

No paper describes XERJ. A search of the README and `docs/` for `arxiv`,
`bibtex`, `@article`, `citation` and `doi.org` returns only the arXiv corpus the
detectors were measured against, and there is no `CITATION.cff`. The suite was
not run here: 21 dependency manifests changed within the screening cooldown.

## 11. Patterns Worth Stealing

### Steal

- **Two clocks from two sources.** The reason the bitemporal record here is real
  and not decorative is that `valid_at` comes from the file's mtime and
  `created_at` from the run's clock. A schema with both columns filled from one
  `now` looks identical and answers nothing.
- **Leave the record clock out of the agent's tool schema.** `xerj_brain_link`
  exposes `valid_at` and not `created_at`. The agent says when the fact became
  true; the server says when it heard. One omitted property enforces the
  division.
- **Walk every door, including the encoded spelling.** The security test's
  premise — that the interesting surface is the generic one underneath, not the
  feature-named handler — generalises to any system whose memory is stored in
  something addressable by another name.
- **Refuse the malformed recall.** `deny_unknown_fields` plus a hard 400 on an
  ambiguous body, adopted because the lenient version returned arbitrary
  memories at score 1.0.
- **Omit rather than null.** `invalid_at` absent puts the row in the null bitmap,
  which *is* the liveness signal, so the query needs no sentinel comparison.
- **Publish the signal's strength against chance.** 35.9% versus 17.0% says more
  about whether to trust a `shared_term` edge than any pass/fail gate would.

### Avoid

- **Deriving identity from a mutable input, then keying rejection on identity.**
  Everything about the invalidation design is right except what it is keyed to.
  Had `edge_id` excluded `valid_at`, or had invalidation been keyed on
  `(src, type, dst)`, the human judgement would have survived a file save.
- **Storing a confidence you never read.** Validated, clamped, persisted,
  returned, and consulted by nothing.
- **Letting a module's authorization comment rot.** Here it rotted in the safe
  direction — the doc is more pessimistic than the code — but a reader's
  deployment decisions come from that paragraph.
- **Classifying a read as a write by omission from a list.** `_recall` missing
  from `is_read_shaped` costs a ring slot per recall on a 4,096-entry log shared
  by the whole node.

### Fit

Take this if you already want a search engine. The memory API is a thin,
well-made adapter over one, and the whole argument for it is that you avoid
running a vector database next to your search stack — which is only a saving if
the search stack was going to exist. Adopting a 380,000-line Rust engine to get
five memory endpoints is the wrong trade, and nothing in the repository argues
otherwise.

The fit is strongest for a single operator or a small team running one node over
their own corpus, wanting recall that works offline with no embedding service
and no refresh lag. It is good for multi-agent setups on one trust boundary,
where namespaces separate agents and the credential model keeps them separated.
Be more careful with mutually distrusting tenants: the enforcement is real and
tested, but the console had to be fixed separately because it bypasses the
middleware entirely, and that is the shape of a boundary that has to be
maintained at every new surface rather than enforced in one place.

Walk away if you need epistemic state on memories themselves. There is no
status, no verification, no review, and no tombstone — the machinery for
believing and un-believing things lives on the edges, and it is keyed on an
identity that a text editor can change.

## 12. Antipatterns / Risks

- **A rejected claim returns under a new identity.** The central finding, in
  section 9. Saving the source file re-teaches the edge with a new `edge_id`,
  and the `invalid_at` stamped on the old one does not apply to it.
- **A re-detection overwrites an invalidation outright.** `detect::assemble`
  emits a full document with `invalid_at` omitted, written with a bulk `index`
  action. The `must_not exists invalid_at` query in the autoindex is a counting
  query for the CLI summary, not a guard on the write path.
- **The audit ring is shared and small.** 4,096 entries for the whole node, with
  every recall taking one. A busy agent evicts the security events the log
  exists for.
- **No `fsync` per audit entry.** Stated plainly by the module: the log survives
  a process restart including `kill -9`, and a machine power loss can take the
  unflushed tail. `sync_to_disk` exists for callers that want the barrier, and
  the API-key operations use it.
- **`confidence` invites a trust decision the code does not make.** A reader
  seeing `confidence: 0.4` on a `samedir` edge may reasonably assume something
  filters on it.
- **Memory deletion is hard deletion.** `forget_one` deletes the document.
  Unlike the edges, there is no soft-delete and no `as_of` for memories — the
  bitemporal care stops at the graph layer.

## 13. Build-vs-Borrow Takeaways

Borrow the whole thing if a search node is already in your architecture; the
memory API costs one index per namespace and nothing else to operate.

Borrow the edge schema regardless of the rest. Three date fields with the
omission discipline, a `schema_version`, evidence carried on the edge, and a
detector tag is a good shape for any store that wants to answer what it believed
at a past instant — provided you key identity and invalidation on the same
thing, which is the one correction to make while copying.

Borrow `brain_is_a_security_boundary.rs` as a template even if you never run
XERJ. The question it asks — what else addresses this data, and does the check
cover that name too — applies to every memory system that stores its data in
something with a general-purpose API — a Postgres table, an S3 bucket, a
shared vector collection.

Build your own if memories need status, review, or a durable rejection. Adding
those here means adding fields to a document the engine treats as arbitrary and
a read path that filters on them, which is work against the grain of an adapter
whose whole premise is that it does not re-implement search.

## 14. Open Questions

- Is the invalidation gap known? `edge_id` including `valid_at` is deliberate
  and documented — "a DIFFERENT `valid_at` creates a distinct edge (bi-temporal
  ...)" — so the behaviour follows from a decision that was made on purpose for
  a different reason. Whether the interaction with manual `unlink` was
  considered is not recorded in the tree.
- Will the stale authorization paragraph in `memory_api.rs` be corrected, and
  does anything in the project's process catch a module doc that describes a
  superseded posture?
- Is `confidence` intended for a future filter, or is it a field that outlived
  its purpose?
- Should `_recall` join `is_read_shaped`, given that the search handler already
  audits the same request against the more useful resource name?

## 15. Appendix: File Index

**Memory API**

- `engine/crates/xerj-api/src/memory_api.rs` — five endpoints, 2,306 lines
  (`:106` namespace validation, `:338` store, `:530` recall, `:1257` list,
  `:1348` forget, `:1392` drop)
- `engine/crates/xerj-api/src/router.rs:885-891` — route mounting

**Graph and bitemporal record**

- `engine/crates/xerj-api/src/graph_api.rs` (`:178-195` edge id, `:214-216`
  mapping, `:407` link, `:567` unlink, `:1237` the `as_of` live slice)
- `engine/crates/xerj-engine/src/graph.rs` — hop expansion, `:69` the hop cap
  sentence
- `engine/crates/xerj-autoindex/src/detect/mod.rs` (`:44-56` edge id, `:319`
  the draft, `:560-585` assemble)

**Authorization and audit**

- `engine/crates/xerj-api/src/authz.rs` (`:140-200` reserved namespace,
  `:262-281` the brain and namespace decisions, `:588` reserved privileges,
  `:1277` the middleware)
- `engine/crates/xerj-api/src/audit_mw.rs` (`:108` read-shaped ops, `:148`
  classify, `:351-403` the middleware)
- `engine/crates/xerj-engine/src/audit.rs` (`:1-60` the coverage statement,
  `:89` the capacity)

**Tests**

- `engine/crates/xerj-api/tests/brain_is_a_security_boundary.rs`
- `engine/crates/xerj-console-api/tests/console_cannot_read_a_brain.rs`
- `engine/crates/xerj-api/tests/snapshot_is_not_a_way_around_a_brain.rs`,
  `ml_datafeed_cannot_read_a_brain.rs`,
  `audit_records_writes_and_who.rs`,
  `scoped_keys_get_intact_responses.rs`
- `engine/crates/xerj-api/src/graph_api.rs:1687` — `soft_invalidate_time_travel`
- `engine/crates/xerj-autoindex/src/incremental_reconcile_http_tests.rs:3843`

**Docs**

- `docs/recipes/agentic-memory.md`, `docs/SECOND_BRAIN.md`,
  `docs/design/SECOND_BRAIN_SPEC.md`

### Commands behind the absence claims

```sh
grep -rn 'confidence' engine/crates --include='*.rs' \
  | grep -v 'graph_api.rs\|autoindex\|/tests/\|xerj-mcp'
grep -rni 'trust_state\|"verified"\|"approved"\|"pending"\|"rejected"\|review_status' \
  engine/crates --include='*.rs' | grep -v '/tests/'
grep -rni 'approve\|adjudicat\|curat' engine/crates/xerj-console-api/src --include='*.rs'
grep -rni 'tombstone\|do not re-add\|never re-assert\|deny.?list\|blocklist' \
  engine/crates/xerj-api/src/memory_api.rs engine/crates/xerj-api/src/graph_api.rs
grep -rni 'unlink.*re-?index\|re-?index.*unlink\|manual.*invalid\|hand-invalidat' \
  engine/crates --include='*.rs'
grep -rn 'invalid_at\|expired_at' engine/crates/xerj-autoindex/src --include='*.rs'
grep -rn -i 'arxiv\|bibtex\|@article\|@misc\|citation\|doi\.org' README.md docs/*.md CITATION.cff
find . -name 'brain_is_not_a_security_boundary*' -not -path './engine/target/*'
```

## History

**2026-09-13** — [`f54eead8097fc234d0815ce245613870dcf22ffd`](https://github.com/xerj-org/xerj/commit/f54eead8097fc234d0815ce245613870dcf22ffd) — first reading. Screened first: 21 dependency manifests inside the 7-day cooldown (the tree was committed the same day), two `build.rs` files cargo executes at build time, and two uninstalled git hooks. Nothing was installed and no suite was run. Four marks. `bitemporal` is earned on two clocks filled from different sources — `valid_at` from the source file's mtime, `created_at` from the indexing run — rather than from a single `now`, with `as_of` applied as a range filter on the read path and a test that asserts the belief both before and after an invalidation instant. `scope_enforced` is earned on the authorization predicate above the per-namespace index rather than on the partition itself: a wildcard read is expanded over the principal's visible set instead of refused. `negative_eval` is earned on four suites asserting one tenant's memory does not come back through any other door, with a separate positive control. `audit_log` is earned on a hash-chained `audit.jsonl` whose module states its own coverage boundaries. `tombstone` is withheld because invalidation is keyed on an `edge_id` derived from the source file's mtime, so saving the file re-teaches the same claim under an id the invalidation does not cover. `trust_state` is withheld because `confidence` is a float that no query reads. `human_review` is withheld because there is no approval surface and the console is required to refuse the memory namespace outright.

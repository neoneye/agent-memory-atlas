---
title: "memini"
eyebrow: "Shared memory service"
description: "A single Go binary serving remember and recall over MCP and REST, which tiers an untiered write with a deterministic regex classifier that can only raise it, deduplicates twice — once before paying for an embedding and once after — and restricts every cross-namespace read leg to durable tiers."
root: ../..
page_kind: system
source_name: "eleboucher/memini"
source_url: https://github.com/eleboucher/memini
archive_name: "eleboucher--memini"
revision: 452ff2299c185530c7010cb164d83cce8006f78a
revision_url: https://github.com/eleboucher/memini/commit/452ff2299c185530c7010cb164d83cce8006f78a
analyzed_at: 2026-09-19
capabilities: "scope_enforced, tombstone, bitemporal, audit_log, negative_eval"
stack_storage: "sqlite, postgres"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
capability_evidence:
  scope_enforced: "the namespace is on every read, and the cascade that widens it is narrowed by tier at the same time | docs/how-it-works/recall.md, internal/store/store.go:126-146, internal/store/storetest/conformance.go:80-120, internal/nsresolve | every memory carries a `Namespace` and the store's `Get`, `IDsByPrefix`, `Upsert` and search entry points all take it as a parameter rather than leaving it to a caller's WHERE clause — `Upsert` returns `ErrConflict` when the given ID already exists under a different namespace, so an id cannot be moved across a boundary by re-writing it. A recall resolves a read set before searching: `scope=\"project\"` is the primary namespace alone, the default `scope=\"full\"` appends ancestors nearest-first then the caller's home then stored links, and `scope=\"everywhere\"` adds the primary's subtree. The part that makes the widening safe is that it narrows on a second axis at the same time — every non-primary leg is restricted to the durable tiers, so an episodic or working memory never crosses a namespace boundary on a read, and a link may narrow that further but never widen it. An explicit per-call namespace list replaces the default set, capped at 16 entries and clamped to 64 after subtree expansion | internal/store/storetest/conformance.go:104-111 is the control, and it runs against both shipped backends: a foreign-namespace row sharing an id prefix is present in the store, and the ambiguous-prefix lookup is asserted equal to exactly the two same-namespace rows"
  tombstone: "supersession is a stored pointer with a single store writer, and the read that would surface it is off by default | internal/memory/types.go:115-119, internal/store/store.go:74-75, :160-177, internal/service/service.go:3775-3790, internal/service/consolidate.go:352, :486, internal/api/rest/rest.go:418, internal/maintenance/tombstone.go, internal/maintenance/repair.go:61 | `Memory.SupersededBy` is a nullable pointer whose doc comment states the contract — *non-nil means this record is tombstoned* — and the only store method that sets it is `SetSuperseded(ctx, namespace, id, supersededBy)`, described as tombstoning a memory by recording the ID that replaced it. Two shipped surfaces produce it: the REST `SupersedeMemory` handler, and the consolidator's contradiction path through `applySupersede` and `asyncSupersede`. The read side is an explicit-widening default: `Filter.IncludeSuperseded` is documented as including contradiction-tombstoned memories, so an ordinary recall does not. The record survives rather than being deleted — `store.go:160-162` exposes the reverse lookup, the versions a given id replaced, and `maintenance/repair.go` walks supersession chains looking for tombstones that no longer reach a live memory | the predecessor is still reachable two ways after the fact: by the `IncludeSuperseded` filter and by time-travel, since supersession stamps `ValidTo` rather than clearing the row"
  bitemporal: "two independent time axes, with the expiry reference moving to the as-of instant rather than staying at now | internal/memory/types.go:120-125, internal/store/store.go:78-84, :244, :310, internal/store/sqlitevec/helpers.go:179-197, internal/api/mcp/mcp.go:728, internal/api/rest/rest.go:225, internal/service/service.go:1922-1928 | `ValidFrom` and `ValidTo` bound the wall-clock interval a fact was true, both nil meaning always, and `ValidTo` is stamped when a fact is superseded — so the correction records *when the old fact stopped being true* separately from when the store learned it. `Filter.AsOf` switches a read into time travel, keeping the rows whose validity window contained that instant. The detail that shows the axes are genuinely separate is in the backend: for a time-travel query, *live* is evaluated at `AsOf` rather than at the current clock, so the expiry and supersession tests move with the query instead of being applied at now and then filtered. Both fields are settable by a caller — the MCP tool parses `valid_to` and the REST handler passes it through — and the service preserves an existing `ValidTo` across an update that does not name one | a superseded fact is therefore still answerable: an as-of read of an instant inside its window returns it, which is what separates this from a status flag that merely hides a row"
  audit_log: "an eleven-kind activity log with a closed vocabulary, every kind of which has a producer, written before the delete it describes | internal/store/store.go:1128-1161, internal/service/events.go:653-654, internal/service/service.go:3742-3760, :3785, internal/api/rest/pins.go:94, :160, internal/api/rest/selfsettings.go:89, internal/api/rest/apikeys.go:274, :402, internal/api/rest/settingsdefaults.go:76 | `EventKind` is `recall`, `get`, `briefing`, `remember`, `update`, `forget`, `supersede`, `pin`, `unpin`, `settings` and `inject`, and `ValidEventKind` is a closed switch so the REST layer rejects an unknown filter value before it reaches SQL. Each kind is emitted from a shipped surface: the read and write paths for the first seven, `LogConfigEvent` from the pin and unpin handlers and from four settings surfaces, and the injection beacon for `inject`, which records which served memories a client hook actually put into model context and what its local gates suppressed. `Forget` snapshots the row *before* deleting it, with the reason written down — after the row is gone there is nothing left to describe it, and an activity feed that can only say some memory was forgotten is not worth much — and the snapshot is best-effort so a failed read cannot block the delete | an event row carries a denormalized namespace, tier and summary triple, so a writer that knows only an ID can record the same snapshot an earlier serve took"
  negative_eval: "a cross-namespace control with both halves, in the store conformance suite both backends run | internal/store/storetest/conformance.go:80-120 | `testCrossNamespaceUpsert` seeds three rows in the namespace under test and a fourth in a foreign namespace whose id shares the `aabbccdd` prefix, then asserts two things about the same lookup: a prefix unique within the namespace resolves to exactly its row, and the ambiguous prefix returns exactly the two same-namespace collisions — a slice equality against a named pair, not an emptiness check, with the comment saying what it is for, that the foreign namespace's row must not leak in. The positive control and the negative assertion are the same call, so a resolver that returned nothing would fail the first before reaching the second | the case is part of the shared conformance suite, so it is run against the SQLite and Postgres backends alike rather than against one"
matrix:
  memory_unit: "A `Memory` — content, an optional summary, a namespace, a tier of `working`, `episodic`, `semantic` or `procedural`, a derivation `level` of explicit or deduced, free tags, a JSON metadata map, an importance in [0,1], access counters, an optional expiry, an optional `superseded_by` pointer, a `valid_from`/`valid_to` interval, an optional corroboration confidence and an optional LLM-assessed importance"
  storage: "One Go binary over SQLite with a vector extension, or Postgres; both implement the same `Store` interface and are exercised by one shared conformance suite. A row with no vector is kept keyword-searchable rather than rejected"
  retrieval: "Vector and keyword legs per namespace in parallel, an absolute semantic floor before fusion, fusion within then across namespaces with first-seen order breaking ties, then a composite of relevance times a quality modifier, a durable-tier reserve, a turn-echo guard, dedup and an optional reranker"
  write: "A ten-step pipeline: validate and resolve the tier, route the namespace, stamp provenance, scrub secrets, sanitize, gate low-signal captures, exact-dedup before embedding, embed, near-duplicate dedup, then store and hand off to background jobs. Some writes are accepted but not stored, and the response says so"
  update_delete: "`memory_forget` deletes by id after snapshotting the row for the activity log, and by tag in bulk; supersession tombstones a predecessor by pointer and stamps its `valid_to`; a maintenance package carries separate forget, demote, dedup, tombstone, scrub and repair passes"
  scoping: "Namespaces with a cascade — primary, ancestors nearest-first, home, links — where every non-primary leg is restricted to durable tiers, so episodic and working memories never cross a boundary on a read"
  integration: "Nine MCP tools including `memory_answer`, `memory_briefing` and `memory_history`, a REST API generated from an OpenAPI document, a CLI, a UI, and plugins for several agent harnesses"
  background: "Maintenance passes for forgetting, demotion, deduplication, tombstone sweeps, re-embedding, backfill, renamespacing, scrubbing, repair and LLM importance assessment"
  trust: "A corroboration `confidence` that grows logistically on re-observation and decays without reinforcement, nil meaning untracked and treated as fully trusted; a derivation `level` of explicit or deduced; an `assessed_importance` cleared whenever a caller sets importance explicitly, so it can only ever refine a guess"
  strengths: "A ranking composite that multiplies relevance by a quality modifier instead of adding a flat recency or importance bonus, with the unused weights left at zero and the documentation saying so; a write path that degrades to keyword-only rather than failing when the embedder is slow or absent; a store interface whose comments state the contracts the backends are held to, and one conformance suite that runs them"
  risks: "The benchmark table's own source is excluded from the repository — `bench/README.md` calls the numbers sourced from the committed `results/` JSON and `.gitignore` carries `/bench/results/`, so no published figure recomputes from a clone; the service-level namespace isolation test asserts only that a foreign reader sees nothing, with no control establishing that the owner sees the memory; and a comment in the event vocabulary still says the pin and settings kinds landed ahead of the write paths that emit them, which six shipped handlers have since made untrue"
---

## 1. Executive Summary

memini is a memory service rather than a library: one Go binary that any
MCP-capable agent talks to, holding a store of tiered memories behind
`remember` and `recall`. It boots with no configuration on an embedded SQLite
file and runs the same code against Postgres. The licence is AGPL-3.0, with the
full text in the tree.

Two decisions shape everything else. The first is that **an untiered write is
classified by regex, not by a model**. A caller who names no tier gets
`working`, a 72-hour intake tier, unless a deterministic marker heuristic raises
it — and the heuristic can only ever raise. It never demotes, never touches a
write whose caller picked a tier, and fails safe: a miss leaves the memory in
`working`, where it can still earn durability later. That makes tiering instant
and identical on every deployment, including one with no LLM configured at all.

The second is that **the scope that widens a read narrows it on another axis at
the same time**. A recall resolves a set of namespaces — the primary, then
ancestors nearest-first, then the caller's home, then stored links — and every
leg past the primary is restricted to the durable tiers. Working and episodic
memories never cross a namespace boundary on a read. A system that cascades
without that rule leaks session chatter between projects; memini's cascade can
only ever surface distilled facts from elsewhere.

The report awards five marks: `scope_enforced`, `tombstone`, `bitemporal`,
`audit_log` and `negative_eval`. It withholds `trust_state`, and section 9 says
why — the epistemic axis here is a number, and the discrete state that withholds
a memory is the supersession pointer the `tombstone` mark already covers.

The sharpest finding is in section 10. The benchmark README publishes a full
results table and says it is *"sourced from the committed `results/` JSON"*,
linking that directory. `.gitignore` line 24 is `/bench/results/`. The harness is real and the
datasets for one suite are committed; the numbers in the headline table are not
reproducible from a clone of this repository.

## 2. Mental Model

Think of memini as a retrieval service with a lifecycle bolted to the front of
it, not as a database with search on top.

The lifecycle is four tiers on one horizon axis. `working` and `episodic` are
short-term — transient, TTL'd at 72 hours and 30 days — and `semantic` and
`procedural` are long-term, durable and curated, with no default expiry. The
mapping is a method on the tier itself rather than a table someone maintains, so
"is this short-term" and "when does this expire" have exactly one answer each.

A memory moves up that ladder in one of three ways: a caller names its tier, the
regex classifier raises it at write time, or a later consolidation pass promotes
it. It moves down by expiring, by being demoted by a maintenance pass, or by
being superseded — which does not delete it, but stamps the interval it was true
for and points at what replaced it.

The retrieval side is where the design opinion lives. Most memory systems
advertise a blend of relevance, recency and importance. memini computes
`relevance × (0.80 + 0.20 × quality)` and leaves the standalone recency and
importance weights at zero, a fact the documentation states under the heading
*"Ranking, honestly"* and the code confirms: `RerankWeights` has four fields and
the production default sets two of them.

## 3. Architecture

```mermaid
%% caption: a write is validated and tiered by a raise-only regex classifier, routed to a namespace, scrubbed and sanitized, gated for signal, deduplicated once before the embedder is paid for and once after, then stored; a recall resolves a read set whose non-primary legs are durable-tier only, runs vector and keyword legs per namespace in parallel, fuses twice with first-seen order breaking ties, and re-scores with relevance multiplied by a quality modifier before reserves, guards and an optional reranker; both paths write to a closed-vocabulary activity log, and ten maintenance passes act on the store behind them
flowchart TD
    subgraph Callers
        MCP["MCP tools<br/>remember · recall · answer<br/>briefing · history · forget"]
        REST["REST API<br/>generated from OpenAPI"]
        CLI["CLI and UI"]
    end

    subgraph Write["Write pipeline (internal/service)"]
        V["validate · resolve tier<br/>regex classifier, raise-only"]
        NS["route namespace<br/>by visibility"]
        SCRUB["scrub secrets"]
        SAN["sanitize bytes<br/>quarantine = downrank"]
        GATE["value gate<br/>accepted, not stored"]
        D1["exact dedup<br/>before paying for a vector"]
        EMB["embed<br/>absent embedder degrades"]
        D2["near-duplicate dedup<br/>supersede · hint · coalesce"]
    end

    subgraph Read["Recall pipeline (internal/search)"]
        RS["resolve read set<br/>primary · ancestors · home · links"]
        LEGS["vector + keyword legs<br/>per namespace, in parallel"]
        FUSE["fuse within, then across<br/>first-seen breaks ties"]
        COMP["composite<br/>relevance x quality"]
        ADJ["reserve · turn-echo guard<br/>dedup · optional reranker"]
    end

    subgraph Store["Store interface"]
        SQL["SQLite + vector ext"]
        PG["Postgres"]
        EV["activity log<br/>eleven closed kinds"]
    end

    subgraph Maint["Maintenance passes"]
        M["forget · demote · dedup<br/>tombstone · reembed · backfill<br/>renamespace · scrub · repair · assess"]
    end

    MCP --> V
    REST --> V
    CLI --> V
    V --> NS --> SCRUB --> SAN --> GATE --> D1 --> EMB --> D2 --> SQL
    D2 -.-> PG
    MCP --> RS
    REST --> RS
    RS --> LEGS --> FUSE --> COMP --> ADJ
    LEGS --> SQL
    LEGS -.-> PG
    V --> EV
    ADJ --> EV
    SQL --> M
    M --> SQL
```

The `Store` interface is the seam worth studying. Its method comments are the
contract the two backends are held to — `Upsert` states what happens to a
vectorless row and to a stale vector-index entry, `GetEmbedding` explains why a
vector is deliberately absent from `Get` (dims × 4 bytes on every read path) and
warns that a Get-then-Upsert round trip is therefore lossy. One shared
conformance suite runs those contracts against SQLite and Postgres alike, which
is what makes a claim about "the store" in this report a claim about both.

## 4. Essential Implementation Paths

- **Write:** `internal/service` — validate, classify, route, scrub, sanitize,
  gate, dedup, embed, dedup again, store.
- **Tier classification:** a pure regex pass with three vetoes (length 20–400
  runes, a transcript veto on `User:`/`Assistant:` scaffolding, a hedge veto on
  tentative phrasing) and five marker families.
- **Recall:** `internal/search` — read-set resolution, parallel legs, the
  semantic floor, double fusion, the composite, the adjustment sequence.
- **Supersession:** `internal/service/consolidate.go` (`applySupersede`,
  `asyncSupersede`) and the REST `SupersedeMemory` handler, both reaching
  `Store.SetSuperseded`.
- **Activity log:** `internal/service/events.go` and `LogConfigEvent`, with the
  kind vocabulary and its validator in `internal/store/store.go`.
- **Maintenance:** ten passes in `internal/maintenance`, each its own file with
  its own test.

## 5. Memory Data Model

A `Memory` carries more axes than most records in this corpus, and the type's
comments are unusually careful about what each one means when it is absent:

- **`Tier`** — `working`, `episodic`, `semantic`, `procedural`, with `Term()`
  and `DefaultTTL()` as methods on the tier.
- **`Level`** — `explicit` or `deduced`, recording whether a fact was stated or
  inferred. The comment notes that the empty string is legacy and *passes
  filters unconstrained*, so the permissive case is the absent one.
- **`Confidence`** — a corroboration number in [0,1] that grows logistically on
  re-observation and decays without reinforcement. `nil` means untracked, and
  the comment says it is *treated as fully trusted so existing data is never
  retroactively penalized* — a migration-safety decision stated rather than
  discovered.
- **`AssessedImportance`** — an LLM judgement in [0.1,0.9] with an invariant
  written into the field comment: it is cleared whenever a caller supplies an
  explicit importance, so a non-nil value always refines a tier-seeded guess and
  never overrides what a user asked for.
- **`SupersededBy`**, **`ValidFrom`**, **`ValidTo`** — the correction axes,
  covered in sections 7 and 9.
- **`LinkedMemoryIDs`** — advisory links from the consolidator, with stale ones
  (target superseded) resolved at recall rather than at write.

## 6. Retrieval Mechanics

Read-set resolution runs concurrently with the query embedding. Each namespace
in the set gets a vector leg and a keyword leg in parallel, and failure is
isolated per leg on purpose: an unreachable ancestor is dropped and named in the
response's degradation note, a failed vector leg falls back to that namespace's
keyword results, and only losing the primary namespace's keyword leg — the one
leg every recall has — fails the call.

Before fusion, an absolute semantic gate drops vector candidates below a raw
similarity floor (0.46 by default). The reasoning is stated and is the kind of
thing that is usually learned the hard way: without an absolute bar, min-max
normalization turns a batch of uniformly irrelevant candidates into
competitive-looking scores. A keyword hit with no vector score is not gated —
vectorless rows stay eligible — but a keyword hit whose vector score is known
and below the floor is dropped from both legs.

Fusion happens twice, and the second one is where scoping and ranking meet:
per-namespace lists fuse into one ranking and **ties at equal score break by
first-seen order across the read set**, which is why the cascade appends
ancestors nearest-first. At equal relevance a memory in `acme/phoenix` outranks
the same-scored one in `acme` because its namespace was seen first.

Then the composite, then a fixed sequence: a durable-tier reserve holding up to
two top-k slots for semantic and procedural memories but only when the durable
is relevance-competitive; a turn-echo guard dropping conversation turns captured
in the last five minutes, because a just-captured turn is still in the caller's
live context and echoing it makes the agent parrot itself; dedup by normalized
content; and an optional reranker whose failure or timeout falls back to the
composite order rather than erroring the recall.

## 7. Write Mechanics

The pipeline is ten ordered steps, and three of them are decisions other
implementations tend to skip.

**Dedup runs twice, either side of the embedder.** An exact content match in the
same tier reinforces the existing memory instead of duplicating it — *before*
paying for an embedding. Only a write that survives that is vectorized, and then
a vector search over the same tier decides whether it should supersede, hint at,
or coalesce into an existing memory. Putting the cheap check first is an obvious
saving that is easy to get backwards.

**A write can be accepted and not stored.** The value gate strips harness
boilerplate from auto-captured conversation turns and drops low-signal episodic
writes, returning `stored: false` with the resolved tier. The documentation is
explicit that this is a feature rather than an error, which matters for a client
that would otherwise retry.

**Degradation is designed rather than incidental.** A slow or absent embedder
degrades the write to keyword-only instead of failing it, and the store keeps
the row searchable with no vector-index entry. `Upsert`'s comment states the
matching invariant — a stale vector-index entry from a prior upsert of the same
ID is removed, and `VectorSearch` never returns a vectorless row.

Correction is supersession rather than deletion: the predecessor keeps its row,
gains a `SupersededBy` pointer and a `ValidTo` stamp, and drops out of live
recall while staying reachable by the `IncludeSuperseded` filter and by
time travel.

## 8. Agent Integration

Nine MCP tools: `memory_remember`, `memory_recall`, `memory_get`, `memory_list`,
`memory_update`, `memory_forget`, `memory_history`, `memory_briefing` and
`memory_answer`. Alongside them a REST API generated from an OpenAPI document, a
CLI, a web UI, and plugins for several harnesses.

Three pull surfaces have different defaults, and the difference between them is
argued rather than assumed. The session-start briefing is query-less, full-scope
and **never reinforces**: it fires on every session start over the same top-N
regardless of relevance, so counting a briefing serve as a use would inflate
access counts uniformly and distort the promotion and ranking that depend on
them. The per-prompt injection runs after shape gates and is client-dependent.
Explicit `memory_recall` reinforces — each served memory's access count bumps
and its expiry slides forward by its own lifetime — and an automatic caller can
send `reinforce: false` to search without changing retention. All three still
appear in the activity log, so the record of what was served stays complete even
where the counters deliberately do not move.

## 9. Reliability, Safety, and Trust

**Scope enforcement — awarded.** The namespace is a parameter on the store's
methods rather than a clause a caller remembers, `Upsert` refuses an id that
exists under a different namespace, and the cascade's durable-tier restriction
means widening the read set cannot widen it to session material. The conformance
suite's cross-namespace case is the control, and it runs on both backends.

**Tombstone — awarded.** One store writer, two shipped producers, a read filter
that is off by default, and a reverse lookup for the versions a given id
replaced. The predecessor survives; `maintenance/repair.go` exists to find
tombstones whose chains no longer reach a live memory.

**Bitemporal — awarded.** `valid_from`/`valid_to` are settable through MCP and
REST and are stamped by supersession, and `Filter.AsOf` switches a read to the
rows whose window contained that instant. The implementation detail that earns
the mark rather than merely claiming it: for a time-travel query the backend
evaluates *live* at the as-of instant rather than at the current clock, so
expiry and supersession move with the query.

**Audit log — awarded.** Eleven kinds, a closed validator, a producer for each,
and `Forget` snapshotting the row before the delete so the feed can say what
went.

**Trust state — withheld, and the reason is worth stating.** memini has an
epistemic axis and it is a number: `Confidence` grows logistically on
re-observation and decays without reinforcement, with `nil` treated as fully
trusted. That is corroboration used for ranking — it feeds the quality term in
the composite — and the mark asks for a discrete state that decides whether a
memory may be treated as true. The field that does withhold is `SupersededBy`,
and it is already carrying `tombstone`; awarding both to the same pointer would
count one mechanism twice. `Level` (`explicit` / `deduced`) is a write-time
provenance genre and the atlas does not award this mark for those.

**Human review — not awarded.** No approval state gates what a memory may be
used for; API keys identify a writer (`metadata.author` is stamped from a named
key) but nothing holds a memory pending anyone's decision.

## 10. Tests, Evals, and Benchmarks

**No paper.** Searched the README and `docs/` for `arxiv`, `@article`, `@misc`,
`doi.org` and a `CITATION.cff`: none. This is a product repository, and its
evaluation claims are its own.

**The harness is committed and the results are not.** `bench/` holds a real
retrieval harness — `cmd/bench`, `dataset.go`, and suites behind a `bench` build
tag so they stay out of the default `go test ./...`, which the README explains
rather than hides (*"a plain `go test ./bench/` reports 'no test files' by
design"*). Three datasets ship: `sample.json`, `codingagent_pilot.json` and
`codingagent_v1.json`. The large public datasets are deliberately excluded with
a comment saying so — `bench/data/.gitignore` carries `longmemeval_*.json` and
`locomo*.json` under *"download on demand … never commit"* — which is ordinary
and fine.

The result files are a different matter. The README's "Full results" table
publishes recall@5, recall@10 and MRR for five retrieval strategies across three
dataset slices, and introduces them as *"sourced from the committed
`results/` JSON"* and links it. There is no `results/` directory anywhere in the
tree (`find . -type d -name results` returns nothing), and `.gitignore` line 24
is `/bench/results/`. So the link in the published table resolves to nothing for
anyone who clones the repository, and no figure in it — including the headline
comparison at README line 117, that memini's hybrid retrieval *"beats
`agentmemory`'s published LongMemEval-S numbers on the same model, dataset and
metric (98.4% recall@5 against 95.2%)"* — recomputes from what is committed. The
commands to regenerate them are given, so this is reproducible work whose
artifacts are excluded, not a claim with nothing behind it; but a reader cannot
check a single number without first obtaining two datasets and standing up an
embedder.

**The unit suite is large and mostly well-built**, and one case is worth naming
because it is the shape this atlas checks for. `service_test.go:645`,
`TestRecallNamespaceIsolation`, writes one memory to `alice` and asserts that a
recall from `bob` returns zero results. Nothing in it establishes that a recall
from `alice` returns the memory, so a `Recall` that returned nothing for anybody
would pass. The repair is one call. The mark is not withheld on its account,
because the store conformance suite carries a properly controlled
cross-namespace case — but a reader counting isolation coverage should count
that one and not this one.

## 11. For Your Own Build

- **Put the cheap dedup before the embedder.** An exact content match in the
  same tier reinforces without paying for a vector. The expensive
  near-duplicate check still runs, afterwards, on what survived.
- **Multiply the quality modifier by relevance instead of adding it.** An
  off-topic memory has almost no score to amplify, so a corroborated durable
  fact can rise above comparably relevant chatter without ever beating something
  genuinely more relevant. Leaving the unused weights at zero and saying so in
  the docs is the other half of that.
- **Narrow one axis when you widen another.** A cascade that reaches ancestors,
  home and links is a leak waiting to happen unless the legs past the primary
  are restricted — here, to durable tiers.
- **Decide what counts as a use.** The briefing serves memories and refuses to
  reinforce them, because a fixed top-N served on every session start would
  inflate the counters that promotion depends on. Logging the serve while not
  counting it is the distinction most systems collapse.
- **Snapshot before you delete.** An activity feed that can only say "some
  memory was forgotten" is not worth much.

## 12. Open Questions

- The event-kind comment still describes `pin`, `unpin` and `settings` as
  vocabulary that *"landed ahead of the pin/settings write paths that will
  actually emit them"*. Six handlers now emit them. Is the comment stale, or is
  some further write path still intended?
- `Level` is stamped on writes and the comment says an empty value passes
  filters unconstrained. Which read paths filter on it at all, and what happens
  to a corpus that predates the field?
- The bench README's `results/` link and the `.gitignore` entry disagree. Were
  the results committed once and removed, or was the table always written
  against a local directory?

## Appendix: File Index

- Domain types: `internal/memory/types.go`
- Store contract and event vocabulary: `internal/store/store.go`
- Backends: `internal/store/sqlitevec/`, `internal/store/postgres/`
- Shared conformance suite: `internal/store/storetest/conformance.go`
- Write path and supersession: `internal/service/service.go`,
  `internal/service/consolidate.go`
- Ranking: `internal/search/rank.go`
- Activity log: `internal/service/events.go`
- Maintenance passes: `internal/maintenance/`
- Surfaces: `internal/api/mcp/`, `internal/api/rest/`, `cmd/`
- Benchmark harness: `bench/`, `cmd/bench`

## History

**2026-09-19** — [`452ff2299c185530c7010cb164d83cce8006f78a`](https://github.com/eleboucher/memini/commit/452ff2299c185530c7010cb164d83cce8006f78a) — first reading, at the head of `main`. Screened with `scripts/screen_repo.py` before anything was read: two auto-run surfaces (a Claude Code plugin manifest and a devcontainer with a `postCreateCommand`) and every dependency manifest inside the seven-day cooldown, which is an artefact of screening a `--depth 1` clone rather than a statement about the upstream. Nothing was installed, built or run; the reading is from the source and the committed documentation. Five marks. The reading covered the domain types, both store backends and the conformance suite they share, the write pipeline and its classifier, the recall pipeline and its ranking composite, the supersession and time-travel paths, the activity log, and the benchmark harness; the UI, the importer and the per-harness plugins were read as context rather than as subject. Three findings are worth the reader's time: the benchmark table's `results/` source is excluded by `.gitignore`, so no published figure recomputes from a clone; the service-level namespace isolation test asserts an absence with no positive control, though the store conformance suite carries a properly controlled equivalent; and the event vocabulary's comment describing the pin and settings kinds as unwired has been overtaken by six handlers that emit them.

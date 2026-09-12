---
title: "SAGE"
eyebrow: "A memory that must be voted in"
description: "A Go memory node on a vendored CometBFT chain where a submitted memory is stored as proposed and becomes readable only after a validator vote commits it, recall reads committed rows alone, confidence decays on an Ebbinghaus curve evaluated at read time, and on the default single-node install the vote that decides admission is one key applying three string heuristics."
root: ../..
page_kind: system
source_name: "l33tdawg/sage"
source_url: https://github.com/l33tdawg/sage
archive_name: "l33tdawg--sage"
revision: 36b2252f11b540a6a3f275f2dced56466b45280f
revision_url: https://github.com/l33tdawg/sage/commit/36b2252f11b540a6a3f275f2dced56466b45280f
analyzed_at: 2026-09-12
capabilities: "tombstone, trust_state, scope_enforced, audit_log, human_review, negative_eval"
capability_evidence:
  tombstone: "the voter's dedup lookup matches a deprecated row's content hash, so rejected bytes cannot re-enter under a fresh memory id | internal/store/sqlite.go:4996, internal/store/postgres.go:3141, internal/store/store.go:414, internal/voter/decision.go:96-110, internal/voter/voter.go:341-348 | `FindByContentHash` selects `WHERE content_hash = ? AND memory_id != ? AND status != 'proposed'` over an index on `content_hash`; the voter passes the candidate's own id so a proposed memory never matches itself, other proposed rows are ignored so two in-flight copies do not veto each other, and every post-proposal status counts — committed, challenged and deprecated — so a memory the quorum rejected or an operator forgot keeps its bytes out of the store until a reinstate; the key is the SHA-256 of the exact content, so a one-character change is a new memory, and the lookup is a node-local opinion that fails open on a store error | internal/store/sqlite_repair_test.go `TestFindByContentHash_DedupPredicate` and `TestDedupPredicate_ThroughVoterDecide` (a deprecated row blocks the same bytes under a fresh id, a correction with new content passes), internal/voter/decision_test.go `TestDedupCheck_ExcludesCandidateOwnRow`, internal/store/postgres_hash_test.go"
  trust_state: "five declared statuses, four with a producer, two of which withhold a memory from every agent-facing read | internal/memory/model.go:11-15, internal/store/sqlite.go:2037, internal/mcp/tools.go:1161, :1404, internal/abci/app.go:5350, :6597, :6624, :7367 | a memory is `proposed` when the submit transaction lands, becomes `committed` only when a validator vote reaches quorum, `deprecated` when the vote fails or a challenge succeeds, and `challenged` while an adjudication is open; the fifth declared value, `validated`, appears in the enum and the unwired lifecycle map and nothing writes it; every recall path hard-codes a committed status filter and the store turns it into `AND status IN ('committed','challenged')`, so a candidate and a rejected memory are both absent from retrieval rather than ranked low — the confidence float exists beside this and is used only for ordering and floors | internal/store/sqlite_disputed_test.go:172-188, api/rest/read_acl_parity_test.go, internal/abci tests (802 cases)"
  scope_enforced: "a domain on every record, filtered in SQL and again per record against the caller's credential | internal/store/sqlite.go:2020, api/rest/appv23_record_disclosure.go:139-153, internal/appv23disclosure/disclosure.go:105-117, internal/abci/app.go:5128-5222 | `domain_tag` is a required column the write path validates against a registered domain list, the query adds `AND domain_tag = ?`, and a second pass authorizes each surviving record against the caller's credential for a read verb and drops the denied ones so that they consume none of the visible limit; six domains are seeded, any new one is auto-registered on first write, and app-v23 gives each agent an owned home domain | api/rest/read_acl_parity_test.go:365-389, api/rest/appv23_visible_pagination_test.go:298-397, internal/store/sqlite_authorized_recall_test.go"
  audit_log: "append-only off-chain tables recording every vote, corroboration and challenge, beneath a signed transaction log | internal/store/sqlite.go:530-564, internal/abci/app.go:7377-7387, :6441-6604 | `validation_votes`, `corroborations` and `challenges` are written from the consensus path as buffered writes flushed at Commit, and the challenges table is described in the store as an append-only off-chain audit; each row's authority is the signed CometBFT transaction that produced it, so the record of who voted, who corroborated and who challenged a memory is the system's own store rather than an external history. One component is unwired: the table named `access_logs` has a producer reachable only from a transaction type nothing constructs | internal/abci tests (802 cases), internal/store tests (746)"
  human_review: "an operator adjudicates a memory from the dashboard, and on a domain with two modify-verb holders the verdict only parks it | web/handler.go:3558-3583, :1360, internal/abci/app.go:7351-7399, web/static/js/app.js:8697-8724 | the CEREBRUM operator selects memories and confirms a delete, which builds a challenge transaction carrying the reason `deprecated by user in CEREBRUM` and broadcasts it; the operator route is loopback-restricted behind a passphrase, and where a domain has at least two holders of a modify verb the challenge moves the memory to `challenged` pending a second holder's confirmation or a reinstate rather than deprecating it outright | e2e Playwright specs (203, not wired to a runner), web tests (710)"
  negative_eval: "a decayed memory asserted absent from a populated result beside two that survive, and a cross-domain leak test at the HTTP boundary | internal/store/decay_floor_test.go:47-68, api/rest/read_acl_parity_test.go:365-389 | three real rows are inserted and the query asserts the aged one dropped by the decay floor while the fresh one and the corroboration-boosted one are both present, so the exclusion cannot pass on an empty result; separately two public memories in different domains are seeded and a no-domain recall asserts the unreadable domain's content absent from the response body while the readable one is present | roughly 22 qualifying cases across read_acl_parity_test.go, confidence_decay_test.go, decay_floor_test.go, sqlite_authorized_recall_test.go, appv23_visible_pagination_test.go"
stack_storage: "sqlite, postgres, kv"
stack_retrieval: "vector, lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "A `MemoryRecord` — id, submitting agent, content, content hash, embedding and its hash, a type of fact, observation, inference or task, a domain tag, a provider, a caller-asserted confidence, a status, an optional parent hash, task workflow fields, and created, committed and deprecated timestamps"
  storage: "Two tiers. BadgerDB holds the consensus state covered by the application hash — the content hash, status, domain, author and classification, and no content. SQLite for a personal node or PostgreSQL with pgvector for a cluster holds the serving projection with the content and the vectors, written only from the consensus path"
  retrieval: "Cosine similarity over the candidate set with no minimum threshold, after a SQL prefilter on the embedding provider, the domain, the confidence and a committed status; a decayed-confidence floor is applied across all candidates before the top-K trim, then a per-record authorization pass. A BM25 text search and a hybrid mode sit beside it, with an off-by-default cross-encoder reranker"
  write: "An agent submits through an MCP tool or the REST route; the node re-embeds the content itself rather than trusting the caller, derives a UUID and a content hash, builds a signed transaction and broadcasts it for commit. The block writes the Badger keys and buffers the SQL row, which is flushed at Commit through what the code calls the only path that writes memories to the offchain store"
  update_delete: "No edit. A challenge transaction moves a memory to `challenged` or `deprecated` and a reinstate reverses it; deprecation leaves the row in place with a timestamp, and the voter's dedup refuses the deprecated memory's exact bytes under any new id until a reinstate. A cleanup pass can evict memories whose decayed confidence falls below a threshold, and it is disabled by default and requires an operator and an explicit dry-run flag"
  scoping: "A required domain tag validated on write against a registered domain list, filtered in the query, and authorized per record against the caller's credential on the way out; agents may hold an owned home domain"
  integration: "38 MCP tools, 119 REST routes, a CEREBRUM dashboard of 65 more, a Python SDK, a desktop shell, a tray app, a libp2p relay as a separate module, and a federation layer that syncs memories between chains under explicit policy"
  background: "A voter loop polling every two seconds for proposed memories to vote on, the CometBFT block loop, federation sync, and an opt-in cleanup pass"
  trust: "Four produced statuses gating readability, a content-hash dedup that keeps a deprecated memory's bytes out, a caller-asserted confidence decaying on an exponential curve with a corroboration bonus, a per-domain decay rate, and a validator score table"
  strengths: "A status ladder that genuinely withholds — a memory is unreadable until something votes it in; a decay floor applied across the whole candidate set before the top-K trim rather than after; a node that re-embeds rather than trusting a caller's vector; consensus-first write ordering with a single documented path into the serving store; a dedup that excludes the candidate's own row rather than every unaccepted row; 4,754 test functions"
  risks: "On the default install the vote is one validator key running three string heuristics, which the README's opening line states beside its consensus claim; the dedup is keyed on exact bytes, is a node-local opinion that fails open on a store error, admits two identical proposals in flight at once, and does not run on the co-commit path; the MCP client silently drops a write at 60% word overlap before the chain sees it; two of the four papers rest on an experiment pipeline excluded from the tree, which the papers index states; `access_logs`, the lifecycle state machine, the `validated` status and the record validator all have no production caller"
---

## 1. Executive Summary

The atlas carries a second, unrelated system of the same name: the
[SAGE Novelty Gate](../sage-novelty-gate/), a mem0 fork from a different
author. The two share nothing but the word.

SAGE is a memory node built on a vendored CometBFT chain — Apache-2.0, 1,569
commits between 2 March and 12 September 2026 by nine authors, 213,191 lines of
Go outside tests and outside the vendored consensus engine, beside 209,380
lines of tests holding 4,754 test functions. The screen found two auto-run
surfaces, five build-time execution points and five unpinned surfaces; nothing
was installed or run, and the read was made from a full clone. Storage is two
tiers: BadgerDB holds the consensus state covered by the application hash, and
SQLite or PostgreSQL holds the serving projection with the content and vectors.

**The idea is that a memory has to be voted in.** A submitted memory is written
as `proposed` (`internal/abci/app.go:5350`) and the HTTP response says so
(`api/rest/memory_handler.go:1627`) even as it reports the transaction
committed. Every recall path then hard-codes a committed status filter
(`internal/mcp/tools.go:1161`, `:1404`) which the store turns into
`AND status IN ('committed','challenged')` (`internal/store/sqlite.go:2037`).
So a memory nothing has voted on is not ranked low — it is not there. That is a
genuine `trust_state`, and the shape is unusual: the default state of a new
memory here is unreadable.

**The confidence model is literal and applied where it matters.**
`conf(M,t) = conf₀ · exp(−λ·Δt) · (1 + 0.1·log(1+corroborations))`
(`internal/memory/confidence.go:38-59`), λ defaulting to 0.005 per day with
per-domain overrides, evaluated at read time so no sweep is needed, and open
tasks exempt. The floor is applied **across the whole candidate set before the
top-K trim** (`internal/store/sqlite.go:2136-2141`), which is the ordering most
implementations get wrong. The stored column is never updated — decay is a
function, not a background job.

Four more marks: `scope_enforced` on a domain filtered in SQL and authorized
again per record, `audit_log` on append-only vote, corroboration and challenge
tables written from the consensus path, `human_review` on a dashboard where an
operator's delete becomes a challenge transaction that, on a domain with two
modify-verb holders, only parks the memory pending a second confirmation, and
`tombstone` on the voter's dedup lookup, which matches a deprecated row's
content hash so that a memory the quorum rejected or an operator forgot keeps
its exact bytes out of the store until a reinstate.

**Three findings sit against the design, and the first is the headline.** On
the default personal install the genesis has exactly one validator
(`cmd/sage-gui/node.go:3532-3540`), and the vote that decides admission is
`internal/voter/decision.go:82-94`: a duplicate check, a quality check that
rejects content under twenty characters and eight hardcoded phrases such as
*"user said hi"* and *"brain online"*, and a consistency check on the
caller-asserted confidence. With one validator the two-thirds quorum is
arithmetically trivial in both directions. The project states this where the
claim is made: the README's opening line says that on a multi-validator network
validation is a BFT quorum and *"on a personal install it is the node's own
signed vote"* (`README.md:5`), the shipped skill file and the hooks document
carry the same split, and the longer form — *"Personal mode runs one real
CometBFT validator with a per-node memory auto-voter; it has no Byzantine
redundancy"*, *"Block inclusion is not the same as memory acceptance"* — sits at
`README.md:135-143`. Until 12 September 2026 the opening line said *"BFT
consensus validation"* unqualified and the skill file described the system to a
model in the same terms; commit `60c9a779` qualified both.

**The dedup lookup keeps rejected bytes out, and it is exact, node-local and
not on every path.** `FindByContentHash` selects `WHERE content_hash = ? AND
memory_id != ? AND status != 'proposed'` (`internal/store/sqlite.go:4996`, the
Postgres twin at `internal/store/postgres.go:3141`), and the voter passes the
candidate's own id (`internal/voter/voter.go:341-348`). The comment above it
records both halves as load-bearing. From v10.1 to v11.19.19 the predicate was
committed-only, because the form before it, `status != 'deprecated'`, matched
the candidate's own proposed row and on a single-validator chain *"every memory
was deprecated on arrival"*; the committed-only form fixed that and let a
rejected memory's bytes back in under a fresh id. Excluding the candidate's own
row instead of every unaccepted row does both (`068566b4`, 12 September 2026).
What it does not do: the key is the SHA-256 of the exact content, so a
one-character edit is a new memory; two identical proposals in flight at once
are both admitted, by design, so that neither poisons the hash for the other; a
store error fails open (`internal/voter/decision.go:96-110`); and the co-commit
path, which writes `committed` on block inclusion and never consults the voter
(`internal/abci/app.go:5938`), runs no dedup lookup at all.

**The MCP client drops writes before the chain sees them.** `toolRemember`
compares a new memory against the first fifty committed memories in the domain
and returns `skipped` at more than sixty per cent significant-word overlap
(`internal/mcp/tools.go:815`, `:4177-4213`) — a lossy filter in front of a store
whose value proposition is that admission is decided by consensus.

**And the papers rest on material outside the tree, which the papers index
says.** `papers/README.md:30` cites the root commit of the published history,
`f2097605` of 2 March 2026, for priority, and the note beneath it states that
the Level Up pipeline's scripts and run records are excluded for IP reasons, so
the statistics in two of the four papers cannot be re-derived from a clone. The
history behind that note is checkable. A commit `23b4593` with the same date,
message and author timestamp as the root but a different tree is fetchable from
the remote by full sha and is not an ancestor of this history; comparing the
two, it holds 41 files and 6,609 lines the published history does not — the
experiment pipeline and its run records — and `.gitignore:160-167` excludes
those paths under a heading of intellectual-property protection, calling the
pipeline proprietary. Until 12 September 2026 the papers index cited that
orphaned commit as the initial commit.

## 2. Mental Model

A memory is **a claim awaiting admission**. It enters signed, hashed and
anchored, and it sits outside retrieval until something votes for it. What votes
depends entirely on deployment: on a cluster it is a set of validators; on the
personal node it is that node's own key running three checks.

Belief has two independent axes. **Status** decides whether a memory may be read
at all — proposed and deprecated are both invisible, challenged is readable
while contested. **Confidence** decides where it ranks and whether it clears a
floor, and it erodes with time unless corroboration pushes back.

Correction is adjudication, not editing. A challenge transaction is the only way
to unmake a memory, it carries a reason, and where a domain has more than one
holder of a modify verb it opens a dispute instead of settling one. A memory
that has been unmade keeps its exact bytes out of the store: the voter's dedup
matches the deprecated row, so the same content under a new id is rejected as a
duplicate, and a correction has to change the content.

Nothing summarises. The agent writes the sentence; the node re-embeds it and
refuses to trust the caller's vector.

```mermaid
%% caption: an agent submits a memory, the node re-embeds it and broadcasts a signed transaction, and the block writes it as proposed with no content on chain; a voter then decides on three checks and a quorum either commits it or deprecates it on arrival, and only committed and challenged rows reach recall, where a decay floor is applied across all candidates before the top-K trim; a deprecated row's content hash stays in the dedup lookup, so the same bytes under a new id are rejected
flowchart TB
    AG["an agent calls sage_remember"]
    GUARD{"more than 60% word overlap<br/>with the first 50 committed<br/>memories in this domain?"}
    SKIP["skipped: never reaches the chain"]
    NODE["the node re-embeds the content<br/>and derives id and content hash"]
    TX["signed transaction,<br/>broadcast for commit"]
    BADGER[("Badger: content hash, status,<br/>domain, author — no content")]
    SQL[("SQLite or Postgres:<br/>content and vectors,<br/>written only at Commit")]
    PROP["status: proposed<br/>invisible to recall"]
    VOTE{"the voter, every 2s:<br/>duplicate against every other<br/>non-proposed row, quality,<br/>consistency"}
    QUORUM{"two-thirds of<br/>validator weight?"}
    COMM["committed"]
    DEP["deprecated"]
    RECALL["recall: committed and<br/>challenged rows only"]
    FLOOR["decayed confidence floor<br/>over all candidates,<br/>then top-K"]
    OP{"a CEREBRUM operator<br/>challenges a memory"}
    CHAL["challenged: parked while<br/>a second holder decides"]

    AG --> GUARD
    GUARD -- yes --> SKIP
    GUARD -- no --> NODE
    NODE --> TX
    TX --> BADGER
    TX --> SQL
    TX --> PROP
    PROP --> VOTE
    VOTE --> QUORUM
    QUORUM -- reached --> COMM
    QUORUM -- "all voted, not reached" --> DEP
    COMM --> RECALL
    RECALL --> FLOOR
    COMM --> OP
    OP --> CHAL
    CHAL --> DEP
    DEP -. "its content hash stays in<br/>the dedup lookup" .-> VOTE
```

## 3. Architecture

Thirty-four packages under `internal/`, of which the memory model itself is
328 lines and the machinery around it is most of the repository:
`store` 46,635 lines, `federation` 26,261, `abci` 21,872, `mcp` 10,353,
`tx` 8,575. Beside them `web/` is 31,860 lines of dashboard, `cmd/` 27,835
across eight binaries, `api/` 20,811, and `third_party/cometbft` is a vendored
116,822-line consensus engine with its own module file.

The two tiers matter. Badger is authoritative and holds no content — only the
hash, the status, the domain, the author and a classification. The SQL store
holds the content and the vectors and is a projection, written from exactly one
place: the code marks it as *"the ONLY path that writes memories to the offchain
store, enforcing consensus-first ordering"* (`internal/abci/app.go:5401-5402`).
Before disclosure, the projection is validated against the Badger application
hash (`api/rest/appv23_record_disclosure.go:69`).

### Deployment and ergonomics

- **What has to run:** a CometBFT node, an embedding provider, and SQLite for a
  personal install or PostgreSQL with pgvector for a cluster. A desktop bundle,
  a tray app and an installer ship.
- **Fully local and offline:** the chain and the store are; embeddings depend on
  the configured provider.
- **Hand-repairable:** partly. The SQL projection is inspectable and
  rebuildable, but the authority is a Badger key space under an application
  hash, and repairing that means replaying the chain.
- **Install:** a release download for the desktop, or Go from source.

## 4. Essential Implementation Paths

- **Submit.** `internal/mcp/tools.go:750` checks the vault lock, resolves the
  domain, runs the overlap guard (`:815`), asks an advisory pre-validate
  endpoint (`:839`) that can refuse before any transaction exists, embeds
  (`:864`) and submits (`:948`). `api/rest/memory_handler.go:1196` validates,
  checks the domain ACL (`:1331`), **re-embeds authoritatively** (`:1345-1352`),
  mints the id and the content hash (`:1355`, `:1371`), builds and signs the
  transaction (`:1399-1453`), and broadcasts for commit (`:1497-1501`).
- **Land the block.** `internal/abci/app.go:4987` `processMemorySubmit` writes
  the Badger keys — hash and status (`:5350`), domain (`:5362`), author
  (`:5388`), classification (`:5477`) — and buffers the SQL row (`:5445`),
  flushed at `Commit` (`:9983`, dispatch at `:10347`).
- **Vote.** `internal/voter/voter.go:156` polls every two seconds, calls
  `Decide` with the candidate's own id (`:341-348`) and broadcasts a vote
  transaction (`:354-375`). `internal/voter/decision.go:82-94` is the whole
  decision: `dedupCheck` (`:96-110`), which asks the store for any other
  non-proposed row with the same content hash and fails open on a store error,
  `qualityCheck` (`:112-126`), `consistencyCheck` (`:128-139`).
- **Reach quorum.** `internal/abci/app.go:6441` `checkAndApplyQuorum` commits at
  two-thirds accept weight (`:6597`) or, once every validator has voted without
  reaching it, deprecates (`:6624`).
- **Recall.** `internal/store/sqlite.go:2001` `QuerySimilar` prefilters in SQL
  on the embedding provider, the domain, the confidence and the status
  (`:2009-2068`), scores by cosine with the comment *"Compute similarity for
  ranking only — no minimum threshold"* (`:2113`), sorts, applies the decay
  floor across all candidates (`:2136-2141`), runs the per-record
  authorization pass (`:2143`) and trims to top-K (`:2154-2161`). A scan budget
  returns an explicit error rather than ranking an arbitrary prefix (`:2119`).
- **Challenge.** `web/handler.go:3558-3583` gates on a loopback operator and
  builds the challenge transaction; `internal/abci/app.go:7351-7399` opens a
  dispute where a domain has two modify-verb holders and deprecates otherwise.
- **Decay.** `internal/memory/confidence.go:38-59` computes;
  `ComputeConfidenceForRecord` (`:29-34`) exempts open tasks; seven call sites
  apply it at read time. The stored column is never written outside a test.

## 5. Memory Data Model

`MemoryRecord` (`internal/memory/model.go:39-73`) with the fields listed in the
matrix. Three of its parts are worth naming. `CorroborationCount` is documented
as display-only and not persisted on the struct (`:69-71`). `MemoryType` is a
four-value enum with a CHECK constraint in the DDL. And `ParentHash` gives a
memory a lineage pointer that the schema keeps but no read path walks.

Around it: `knowledge_triples`, `validation_votes`, `corroborations`,
`challenges`, `validator_scores`, `epoch_scores`, `domains` with a per-domain
decay rate, `access_logs`, `memory_links`, `memory_tags`, and a federation
`sync_tombstone`.

**Temporal:** `created_at`, `committed_at`, `deprecated_at`, all record time
taken from block time. `bitemporal` withheld — a search for validity columns
across the Go outside the vendored engine returns nothing.

**Trust:** five declared statuses, four of them written — `validated` is in
the enum and the unwired lifecycle map and nothing sets it — plus a decaying
float. `trust_state` earned.

**Scoping:** a required domain plus per-record authorization.
`scope_enforced` earned.

**Tombstone:** earned — see section 9.

**Four mechanisms with no production caller.** The lifecycle state machine says
so about itself: *"this map is documentation / SQLite hygiene only — it has
ZERO production callers. Consensus writes statuses imperatively … which performs
no transition check"* (`internal/memory/lifecycle.go:10-13`).
`ValidateMemoryRecord` has callers only in its own test file, and the REST layer
re-implements the checks inline. `knowledge_triples` is written by the REST
path and the SDK and read back by nothing: the only production statements
naming it are the idempotency guard inside its own insert. And the `validated`
status has a place in the enum and in that lifecycle map and no writer.

## 6. Retrieval Mechanics

The prefilter is where the marks live. Before any scoring, the query pins the
embedding provider so vectors from different models are never compared, and adds
the domain and the status. Then cosine similarity ranks — with no minimum, which
the code says outright — and the decayed floor drops everything below the
threshold **across the whole candidate set**, before the top-K trim. That
ordering is the difference between a floor that means something and one that
only prunes a page.

The per-record authorization pass runs after ranking and before the trim, and
denied records *"consume no visible limit"* — so a caller who cannot read half a
domain still gets a full page.

A text search and a hybrid mode sit beside the vector path, and an off-by-default
cross-encoder reranker lives in its own package.

**Failure modes.** A memory nobody voted on is silently absent, which is the
design and is also the first thing a new operator will hit if the voter is
disabled. A vector produced by a different provider is invisible rather than
mis-ranked, which is the right trade. And the scan budget converts an unbounded
authorization pass into an explicit error rather than a quietly truncated
answer.

## 7. Write Mechanics

**The node does not trust the caller's vector.** The MCP client embeds for its
own pre-check, and the REST handler re-embeds authoritatively before hashing.
For a store whose integrity claim rests on hashes, that is the right boundary.

**Consensus-first ordering is enforced by having one writer.** The SQL row is
buffered during block execution and flushed at Commit, and the code says this is
the only path that writes memories to the serving store.

**Nothing extracts.** The agent writes the content, chooses the type and asserts
the confidence. The README concedes the last point directly, and the voter's
consistency check is the only thing that pushes back: a `fact` below 0.7 is
rejected.

**Deletion is a challenge, and it sticks.** There is no delete path that removes
a row; deprecation stamps a timestamp and leaves the record, and the record's
content hash keeps the same bytes out of the voter's dedup until a reinstate —
so `sage_forget` is the removal path and a correction has to change the
content. The optional cleanup pass can evict on a decayed-confidence threshold,
is disabled by default, and requires an operator and an explicit dry-run flag.

### Operational cost

- A write is a blocking `broadcast_tx_commit`, so the caller waits for a block.
- Admission is asynchronous after that: the voter polls every two seconds.
- A read is one SQL prefilter, an in-process cosine over the candidates, a decay
  computation per row and an authorization call per survivor.

## 8. Agent Integration

38 MCP tools, of which seven touch memory, plus 119 REST routes, a Python SDK
and the dashboard's own 65. The agent-facing story is the four verbs —
remember, recall, forget, corroborate — and the shipped skill file describes the
system to a model with the split the README's opening line makes: a BFT quorum
on a network, one signed validator on a personal install.

The human-facing story is CEREBRUM: a loopback dashboard behind a passphrase
where an operator searches, selects and challenges memories, and sees an
advisory pre-vote panel showing the same three checks the real vote applies.

## 9. Reliability, Safety, and Trust

**Trust state — awarded.** Where a system scores everything and returns it, this
one makes a new memory unreadable and requires an event to change that. Two of
the four produced states withhold, the filter is a SQL predicate rather than a
weight, and all four have reachable producers on the consensus path; the fifth
declared value has none.

**Scope — awarded.** A domain validated on write, filtered in the query, and
authorized per record afterwards, with denied rows not consuming the page.

**Audit log — awarded, with one component unwired.** Votes, corroborations and
challenges are append-only tables written from block execution, each backed by a
signed transaction. The table actually named `access_logs` is not part of it:
its only producer is an access-query transaction type, and nothing in the REST
layer, the MCP tools, the CLI or the SDK constructs that type. Recall writes no
access record.

**Human review — awarded.** The operator's challenge is a real adjudication that
mutates the store, and the two-holder rule makes it a dispute rather than a
verdict where the domain has more than one steward.

**Negative evaluation — awarded.** The decay-floor case inserts three real rows
and asserts the aged one absent while the fresh and the corroboration-boosted
ones are present, so the exclusion cannot pass on an empty result. The
cross-domain case asserts an unreadable domain's content absent from an HTTP
response body while a readable domain's is present.

**Tombstone — awarded, on the deprecated row itself.** The value-keyed lookup
in the system is `FindByContentHash`, and it matches any other memory that has
left `proposed`, deprecated rows included. A memory the quorum rejected or an
operator forgot therefore keeps its exact bytes out: the same content under a
fresh id is voted down as a duplicate, which the committed cases assert through
the real store and the real decision, and the inverse is `sage_reinstate`,
which returns the row to `committed`. The record is the deprecated memory
rather than a separate table, and the key is the SHA-256 of the exact content —
a one-character change is a new hash, which the project states as the intended
correction path. Three limits are the system's own. Two identical proposals in
flight at once are both admitted, by design, so that neither leaves the content
with no surviving row and a poisoned hash. The lookup is a node-local opinion
that fails open — a store error accepts — and the quorum tally is what decides.
And the co-commit path writes `committed` on block inclusion, never consults the
voter, and runs no dedup lookup. The `sync_tombstone` table beside all this is a
federation delete-sync marker keyed on origin chain and memory id, which the
rubric excludes by name. Federation sync itself is covered: an accepted sync
item is re-broadcast as a local memory-submit transaction and lands as
`proposed` for the voter.

**Bitemporal — withheld.** Three timestamps, all record time.

**What the consensus claim is worth on one node.** Not nothing, and the report
should be precise about both halves. What a single-validator chain does buy: an
Ed25519-signed, hash-anchored, replay-safe append-only transaction log; fork-gated
deterministic execution; an application hash the serving projection is checked
against before disclosure; and a single documented write path into that
projection. What it does not buy is Byzantine fault tolerance, because there is
one fault domain, and the admission decision is three string heuristics rather
than a distributed judgement. The README's opening line says so, and so do the
skill file and the hooks document.

**The published results and the rewritten history.** Four papers ship as PDFs
with Zenodo identifiers and checksums. Their throughput and latency figures
appear in this tree only as prose in an architecture document; the load test the
reproducibility section points at asserts thresholds an order of magnitude below
the published numbers and writes nothing to disk, and its alternative sends a
literal placeholder signature. The statistical results in two of the papers
depend on a pipeline whose code, scripts and run records are excluded by
`.gitignore` as proprietary, which the papers index states beside its priority
citation; that material is present at an orphaned commit of the same date that
is fetchable by sha and is not an ancestor of this history. Both facts are
checkable in three commands and both are recorded in the appendix.

**The benchmark files are committed, and the unflattering one is documented as
not being an ablation.** Four result JSONs sit in `bench/results/`. LongMemEval
over five hundred questions gives R@5 of 0.9053, and the v7.1 run over the same
corpus with the reranker enabled reports 0.8927 at roughly twenty-five times the
median query latency. The two differ in more than the reranker: the v7.1 record
carries `expand_n: 3`, and the 0.9053 record carries no expansion field at all,
written by a harness version that predates the key. `bench/longmemeval/README.md`
tabulates the three committed runs and says the delta covers expansion plus
reranking. Committing the run is to the project's credit; the documented make
targets pass neither flag, so they reproduce neither file.

## 10. Tests, Evals, and Benchmarks

4,754 test functions in 639 files and 209,380 lines, heaviest in `internal/abci`
(802), `internal/store` (747), `web` (710) and `api/rest` (557). The memory
model itself — the decay and lifecycle arithmetic — has one test file of 149
lines.

The dedup predicate is pinned from three sides. `TestFindByContentHash_DedupPredicate`
inserts two rows with the same bytes and asserts, through the real SQLite store,
that a candidate never matches its own row, that a second proposed row does not
block it, that validated, committed and challenged rows do, that a deprecated
row does, and that a correction with changed content passes;
`TestDedupPredicate_ThroughVoterDecide` runs the same store through the real
`Decide` and asserts a resubmission after deprecation is voted down with
*"duplicate content"*; `TestDedupCheck_ExcludesCandidateOwnRow` records what the
voter hands the store and asserts the candidate id is passed and an advisory
call passes none. `TestRepairSelfDupRejected` gained a fixture for a genuine
duplicate rejection whose twin row still exists, asserting the repair leaves it
deprecated. None of these was run for this report: the machine carries no Go
toolchain, and `go.sum` changed inside the seven-day cooldown.

Three suites do not run in a checkout. The integration tests need a four-validator
Docker network and a Postgres; the Byzantine suite is the only network suite CI
runs; and the 203 Playwright end-to-end specs hardcode a localhost port with no
web server configured and no script or make target that invokes them.

The benchmark harnesses are in-tree and honest about their inputs, and an
outsider still cannot run them: the datasets are gitignored with no fetch target
for one of them, an API key is a hard exit, and the v7.1 rows need a 2.3 GB
reranker download. The recorded commit in each result file is the harness
repository's head, not the version of the node under test, and one file carries a
hand-written note explaining that its rerank metadata was patched in after the
run because the harness environment variable was unset. That note is the most
useful line in the directory: it says exactly what was not machine-recorded.

## 11. For Your Own Build

### Steal

- **Make a new memory unreadable until something admits it.** A status filter in
  the query is a stronger guarantee than any confidence weighting, and it turns
  admission into an event you can audit.
- **Apply the decay floor across the whole candidate set before the top-K
  trim.** Applying it after is the common bug and it silently turns a
  correctness floor into pagination.
- **Re-embed on the server.** If your integrity story is hashes, a
  caller-supplied vector is a hole in it.
- **Pin the embedding provider in the query.** Comparing vectors from two models
  is worse than returning nothing, and one SQL predicate prevents it.
- **Let denied records consume no page slots.** A caller who cannot read half a
  domain should still get a full page, not a half-empty one that leaks the size
  of what they cannot see.
- **Return an explicit budget error instead of ranking a prefix.** A truncated
  authorization pass that looks like a complete answer is the failure nobody
  notices.
- **Exclude the candidate's own row, not every unaccepted row.** A dedup that
  runs while the candidate sits in the table has to skip one row; skipping every
  row that is not yet accepted also skips the rejected ones, and that is the
  difference between a duplicate check and a tombstone. Ignore other in-flight
  candidates too, or two identical proposals veto each other.

### Avoid

- **A headline that outruns its own qualification.** Until 12 September 2026
  the README's opening line said BFT consensus while the one-validator
  qualification sat 130 lines down, and the shipped skill file described the
  system to a model in the headline's terms; a reader who took either at face
  value believed a memory was adjudicated by a quorum when one key ran three
  string comparisons. Put the split in the first sentence, and in the file the
  model reads.
- **A client-side overlap filter in front of a consensus store.** Sixty per cent
  word overlap against the first fifty rows is a heuristic; dropping the write
  before the chain sees it means the store's own admission rules never get to
  decide.
- **Citing a commit for priority that your history does not contain.** Until
  12 September 2026 the papers index cited an orphaned commit as the initial
  commit. If material has to be removed for licensing, cite what remains and say
  what went, which is what the index does at this pin.

### Fit

Right if you want admission to be an explicit, signed, auditable event and are
deploying more than one validator — the status ladder, the write ordering, the
sticky dedup and the decay floor are all sound, and the test suite is serious.
Wrong if you are running the personal node and expect consensus to mean more
than one signed vote, if you need a memory to be corrected rather than
deprecated, or if a forgotten memory has to be re-rememberable verbatim — the
dedup keeps its exact bytes out until a reinstate.

## 12. Open Questions

- What would make single-node admission more than three string comparisons? The
  advisory pre-validate endpoint already exists and could carry a real check.
- Will two identical proposals in flight at once stay both admitted? The dedup
  ignores other proposed rows so that neither poisons the hash; the cost is that
  the race admits both copies.
- Will the co-commit path get a dedup lookup? It commits on block inclusion and
  never consults the voter, so a deprecated memory's bytes can re-enter there.
- Will `access_logs` get a producer? The table, the transaction type and the
  handler are all written; nothing constructs the transaction.
- Will a reranker-only run be committed? The v7.1 record bundles query
  expansion with reranking, and the bench README says the delta is not an
  ablation.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `internal/memory/model.go` | 328 (package) | `MemoryRecord` (39-73), the status, type and task enums (11-36); `validated` declared at 12 with no writer |
| `internal/memory/confidence.go` | — | The decay formula (38-59), per-domain rates (14-17), the open-task exemption (29-34) |
| `internal/memory/lifecycle.go` | — | The transition map, documented as having zero production callers (10-13) |
| `internal/voter/decision.go` | — | `DecideVerbose` (82-94), the three checks (96-139), the eight noise phrases (63-67), `MemoryID` on the input (38-41) |
| `internal/voter/voter.go` | — | The two-second poll (156), `Decide` called with the candidate's id (341-348), the vote broadcast (354-375) |
| `internal/abci/app.go` | 21,872 (pkg) | `processMemorySubmit` (4987), the consensus-first comment (5401), quorum (6441-6647), challenge (7351-7399) |
| `internal/store/sqlite.go` | — | The DDL (457-495) with the `content_hash` index (487), the vote, corroboration and challenge tables (530-564), `QuerySimilar` (2001-2162), the decay floor (2136-2141), `FindByContentHash` (4996), `RepairSelfDupRejected` (5035) |
| `internal/store/postgres.go` | — | `FindByContentHash` (3141) on the same predicate; the migration that drops the committed-only partial index (466-474) |
| `api/rest/memory_handler.go` | — | Submit (1196-1635), query (1903-2040), the decay floor setup (1717-1723) |
| `api/rest/appv23_record_disclosure.go` | — | Per-record authorization (139-153) and the app-hash check (69) |
| `internal/mcp/tools.go` | — | 38 tools; `toolRemember` (750), the overlap guard (815, 4177-4213), `toolRecall` (1081) |
| `web/handler.go` | — | The operator gate (3558) and the challenge build (3575-3583) |
| `bench/results/` | 4 files | LongMemEval n=500 R@5 0.9053 with no expansion field; the v7.1 run at 0.8927, ~25× latency, `expand_n: 3` and the reranker on; LoCoMo n=1986 R@5 0.6394 |
| `papers/` | 4 PDFs | With Zenodo identifiers, checksums and the priority claim (README:30) |
| `third_party/cometbft` | 116,822 | The vendored consensus engine, own module |
| tests | 209,380 in 639 files | 4,754 test functions |

**Searches recorded for the negative claims**

```sh
rg -c -i -e valid_from -e valid_to -e bitemporal -e as_of --glob '*.go' --glob '!third_party/**' .   # 0 files
rg -c -e rejected_hash -e refused_value -e never_readmit --glob '*.go' --glob '!third_party/**' .    # 0 files
rg -n 'TxTypeAccessQuery' --glob '*.go' --glob '!*_test.go' --glob '!internal/abci/**' --glob '!internal/tx/**' .  # 0: access_logs has no reachable producer
rg -n 'memory\.ValidTransition|memory\.Transition\(' --glob '*.go' --glob '!third_party/**' .        # 0: the state machine has no callers
rg -n 'FROM knowledge_triples' --glob '*.go' --glob '!*_test.go' .                                   # 2, both the idempotency guard inside the insert
rg -n 'UPDATE memories SET' --glob '*.go' --glob '!third_party/**' .                                 # confidence_score updated only in a test
rg -n 'StatusValidated|"validated"' --glob '*.go' --glob '!*_test.go' --glob '!third_party/**' .    # the enum, two status switches, the unwired lifecycle map: no writer
rg -n 'FindByContentHash\(' --glob '*.go' --glob '!*_test.go' .                                     # the interface, two stores, the voter, the advisory pre-vote: no other admission path consults it
git fetch --depth 1 origin 23b45930b0dc097f56978a99f45a11c93571b60b                                  # the orphaned commit is served by sha
git merge-base --is-ancestor 23b45930b0dc097f56978a99f45a11c93571b60b HEAD                           # exit 1: not an ancestor of this history
git diff --stat f2097605 23b45930                                                                    # 41 files, 6,609 lines present there and not here
python3 -c "import json; print('expand_n' in json.load(open('bench/results/longmemeval-full-48e81ec.json')))"  # False: the 0.9053 record has no expansion field
```

## History

**2026-09-12** — [`36b2252f11b540a6a3f275f2dced56466b45280f`](https://github.com/l33tdawg/sage/commit/36b2252f11b540a6a3f275f2dced56466b45280f) — second reading, ten commits on, at v11.19.20, on the day of the last commit. Screened again first: two auto-run surfaces (the `.claude/settings.json` hooks, whose commands name five scripts under `.claude/hooks/` that are not in the tree, and the MCP manifest), five build-time execution points, five unpinned surfaces, six manifests inside the seven-day cooldown; nothing was installed and no test was run, the read was made from a full clone, and the machine carries no Go toolchain. One mark moved, from withheld to awarded. `068566b4` widened the voter's dedup predicate from committed-only to *any other row that has left `proposed`*, threading the candidate's own id through `MemoryInput` so the v10.1 self-match cannot recur, and three committed cases pin it through the real store and the real decision; the section-9 near-miss on `FindByContentHash` is the `tombstone` evidence line, with the three limits the code states — exact-bytes key, a fail-open node-local opinion, and the co-commit path that never consults the voter — recorded beside it. Two criticisms went stale in one commit, `60c9a779`: the README's opening line, the skill file and the hooks document carry the one-validator qualification, and the papers index cites the root commit and states the excluded pipeline itself; the orphaned commit was re-fetched by sha and the 41-file, 6,609-line comparison reproduces. One published claim was wrong at the first pin and is corrected in section 9: the 0.9053 LongMemEval record carries no expansion field — only the v7.1 record does — so the reranked run was never a reranker ablation, which the project's bench README says as of this commit. The status enum's fifth value, `validated`, is recorded as declared with no writer. Every cited line in `internal/store/sqlite.go` and `internal/voter/decision.go` moved and was re-verified.

**2026-09-08** — [`5c6b32e51586a9e8b9153e827dffa4491916e8c1`](https://github.com/l33tdawg/sage/commit/5c6b32e51586a9e8b9153e827dffa4491916e8c1) — first reading, at the head of `main`, one day after the last commit. Screened before anything was read: two auto-run surfaces, five build-time execution points, five unpinned surfaces; nothing was installed or run, and the read was made from a full clone. Five marks. `trust_state` is the strongest instance in the corpus of a status that withholds rather than ranks — a memory is unreadable until a vote commits it. `scope_enforced`, `audit_log` and `human_review` rest on the domain filter plus per-record authorization, the append-only vote and challenge tables, and the operator challenge that opens a dispute where a domain has two stewards. `negative_eval` rests on a decay-floor case with two surviving controls. `tombstone` and `bitemporal` were examined and withheld, the first with its near-miss in section 9. Two claims were verified rather than repeated: the consensus headline was traced to a single-validator genesis and a three-check voter, with the project's own qualification quoted; and the papers' priority commit was checked with `merge-base` and compared by tree, confirming it is not an ancestor of this history and that 41 files of experiment material present there are absent here, for a licensing reason the repository states. The reading covers the memory model, the submit and vote paths, the store's ranking and decay, the disclosure layer and the dashboard's adjudication; federation, the natter relay, the desktop shell and the vendored consensus engine were treated as context.

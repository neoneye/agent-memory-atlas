---
title: "Noosphere"
eyebrow: "A tombstone that survives key rotation"
description: "A revoked capture is refused on the write path by an HMAC digest checked against every retained key version — the only rejected-value record in this atlas that reasons about the key used to compute its own key."
root: ../..
page_kind: system
source_name: "sweetsophia/noosphere"
source_url: https://github.com/sweetsophia/noosphere
revision: feb04e0d07a48ae988095bd9631307f6fcfd47bc
revision_url: https://github.com/sweetsophia/noosphere/commit/feb04e0d07a48ae988095bd9631307f6fcfd47bc
analyzed_at: 2026-09-05
capabilities: "tombstone, scope_enforced, human_review, audit_log"
capability_evidence:
  tombstone: "the capture write path | src/lib/memory/capture/repository.ts:244-254, src/lib/memory/capture/crypto.ts, src/lib/memory/capture/lifecycle.ts:398-412 | inside a serializable transaction, after the lineage rows are locked, `memoryTombstone.findFirst` is queried on `kind: CAPTURE` and the whole set of HMAC digests `digestWithAllKeys` computed under every retained key version, and a hit throws `MemoryCaptureError(\"Capture was previously revoked\", 409)`; the tombstone is upserted on `(lineageStateId, generation)` with the key version, a reason code and a ninety-day `expiresAt`, so the refusal survives key rotation and lapses by design after the TTL | src/__tests__/memory/capture-race-integration.test.ts asserts a capture racing a principal revocation fails once the revocation wins serialization, that no capture row exists and that exactly one PRINCIPAL tombstone does; no committed case asserts the 409 on a plain re-capture of a revoked value"
  scope_enforced: "every candidate, capture and admin read | prisma/schema.prisma:231,:339-360, src/lib/memory/capture/admin-list.ts:35-45 | `privateScopeTag` sits on the principal and on every derived row and leads the composite index `(agentPrincipalId, privateScopeTag, status, expiresAt)`; `RestrictedScope` is a table with its own revocation reason; the admin lists resolve an API key's `allowedScopes` into the exact private scopes it may inspect and an empty list authorises no rows | src/__tests__/memory/capture-race-integration.test.ts `scope deletion cannot be undone by a queued unbound key create` and `…queued key scope update`"
  human_review: "revocations that touch an article | src/lib/memory/capture/lifecycle.ts:378-396, prisma/schema.prisma:560, src/app/api/memory/privacy-reviews/route.ts | every revocation upserts a `MemoryPrivacyReview` row with `status: OPEN`, a reason code and `resolvedBy`/`resolvedAt`, unique on `(articleId, lineageStateId, generation)`, listed through an admin route that requires `Permissions.ADMIN` and filters by the key's allowed scopes; nothing forces resolution | src/__tests__/memory/capture-integration.test.ts"
  audit_log: "revocation and cleanup, in the system's own tables | prisma/schema.prisma:507,:527, src/lib/memory/capture/lifecycle.ts:398-425 | `MemoryTombstone` is written by upsert on a unique `(lineageStateId, generation)` and carries `reasonCode`, `hmacKeyVersion` and `createdAt`, so each revocation of a lineage is its own row; `MemoryDurableJob` records every cleanup attempt under the idempotency key `memory-cleanup:{lineage}:{generation}`; no path updates or deletes either record outside TTL expiry | src/__tests__/memory/capture-race-integration.test.ts counts tombstone rows; src/__tests__/memory/backfill.test.ts covers the durable job"
stack_storage: "postgres"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A capture, promoted to a candidate, promoted to a wiki article with topics, revisions and scopes"
  storage: "Postgres through Prisma, with an optional hybrid embedding tier behind consent state"
  retrieval: "Postgres full-text with optional embeddings, gated by restricted tags and the caller's scope"
  write: "A serializable transaction that locks the lineage, refuses a revoked digest, then creates the capture"
  update_delete: "Revocation writes a tombstone keyed on an HMAC subject hash and enqueues a durable cleanup job"
  scoping: "privateScopeTag on the principal and on every row, plus a RestrictedScope table and restricted tags"
  integration: "Plugins for OpenClaw, OpenCode, Kilo Code and Hermes, a five-tool stdio MCP server installed into Codex, an injected-memory package, an installer that pins its backend script and Hermes bundle by SHA-256, and a web wiki"
  background: "Durable jobs with idempotency keys for cleanup, embedding and backfill, plus TTL expiry"
  trust: "A candidate status enum — ephemeral, pending review, rejected, promoted, expired, quarantined — of which only quarantined has a writer, set by lineage revocation; the promotion review is an in-memory type nothing persists, and recall reads articles, never candidates"
  strengths: "The tombstone is checked across every retained HMAC key version, so rotating the key cannot resurrect a revocation"
  risks: "The tombstone expires after ninety days by design, so the refusal is durable for a bounded window; the candidate tier and its five usage counters are schema with one writer, so the promotion ladder the enum describes is not a mechanism the code runs"
---

## 1. Executive Summary

Noosphere is a self-hosted knowledge and memory layer where the same data is an
agent's memory and a human's browsable Markdown wiki — topics, revisions and
scopes. Apache-2.0 at release 1.13.3; 55,367 lines of TypeScript under `src/` and
76,788 of TypeScript and JavaScript across the repository with its six sibling
packages, on Next.js and Postgres through Prisma, with plugins for OpenClaw,
OpenCode, Kilo Code and Hermes and an MCP server for Codex.

**What is not a mechanism is the candidate tier.** `MemoryCandidate`
(`prisma/schema.prisma:323`) declares a status enum — `EPHEMERAL`,
`PENDING_REVIEW`, `REJECTED`, `PROMOTED`, `EXPIRED`, `QUARANTINED` — and five
usage counters. In `src/`, the table is read by the admin list route, set to
`QUARANTINED` by lineage revocation (`lifecycle.ts:346`), deleted by
maintenance when no source group survives (`maintenance.ts:276`), and created
by nothing: `rg -n 'memoryCandidate\.create'` returns no line, and the one
`INSERT INTO "MemoryCandidate"` in the repository is a Docker rehearsal
fixture. `PROMOTED`, `PENDING_REVIEW`, `REJECTED` and `EXPIRED` have no writer;
`retrievedCount`, `injectedCount`, `explicitGetCount` and
`distinctSessionCount` are selected and never incremented — only
`occurrenceCount` is, on a capture (`repository.ts:165`). The promotion module
(`src/lib/memory/promotion.ts`) computes candidates over recall statistics
with a `PromotionStatus` of `pending`, `approved` or `rejected` that no table
holds. And recall reads `article` (`noosphere.ts:510`), never a candidate. The
ladder from capture through candidate to article is therefore a schema and a
design; what runs is capture, article, and revocation over both.

**It carries a rejected-value tombstone of the *consulted* kind, and it is the
most rigorous one in this atlas.**

The mechanism, in `src/lib/memory/capture/repository.ts:244`, sits inside a
serializable transaction after the lineage rows are locked and before the
capture is created:

```ts
// A tombstone from any retained key version blocks recreation. Historical
// keys remain in the bounded keyring until their tombstones and source TTLs
// have expired.
const blocked = await tx.memoryTombstone.findFirst({
  where: {
    kind: MemoryLineageKind.CAPTURE,
    subjectHash: { in: dedupeDigests.map((entry) => entry.digest) },
    expiresAt: { gt: now },
  },
  select: { id: true },
});
if (blocked) {
  throw new MemoryCaptureError("Capture was previously revoked", 409);
}
```

Against the four properties the
[pattern page](../../patterns/rejected-value-tombstone/) requires of the strong
form: it is **value-keyed** (an HMAC digest of the capture content, not a row
id), **normalized** (`digestWithAllKeys` produces the digest set),
**consulted before the write**, and the write is **refused** — a 409, not a
silent no-op.

**And it handles a problem no other tombstone here addresses: key rotation.**
The digest is an HMAC, so rotating the key changes every digest. A naïve
implementation would let every revoked value back in on the next rotation. This
one keeps historical keys "in the bounded keyring until their tombstones and
source TTLs have expired", computes the digest under *all* retained versions, and
matches the tombstone against the whole set. `MemoryTombstone` stores
`hmacKeyVersion` alongside `subjectHash` so a reader can tell which key produced
which record.

The deliberate limit is `TOMBSTONE_TTL_MS = 90 days`. The refusal is durable for
ninety days and then the row expires, which bounds the keyring and means the
guarantee is a window rather than forever. That is a defensible choice for a
privacy-driven revocation — the source data has its own TTL — and it is a real
difference from a permanent tombstone, so a reader should not read this as
"never again".

## 2. Mental Model

Memory is promoted through three tiers, and only the last is the wiki.

A **capture** is a raw exchange with `userText` and `assistantText`, an HMAC
`dedupeKey`, `sourceSessionHash`, `sourceRunHash`, `restrictedTags` and a TTL. A
**candidate** is, in the schema, a distilled memory with a title, content, a
recall summary, search terms, a confidence and a status starting at
`EPHEMERAL`, carrying `occurrenceCount`, `retrievedCount`, `injectedCount`,
`explicitGetCount`, `relevanceSum` and `distinctSessionCount` — and in the
code a row nothing creates or promotes, as section 1 sets out. An **article**
is the wiki page a person reads, and the thing recall returns.

Alongside runs a lineage system: `MemoryLineageState` per subject kind
(capture, session, scope, principal), `MemoryProvenanceEdge` linking them, and
generations. Revocation is expressed against a *lineage*, not a row, which is
why revoking a session or a scope propagates to everything derived from it.

```mermaid
%% caption: a revocation writes a tombstone keyed on a hashed subject that refuses later captures — and the tombstone carries a ninety-day TTL, after which the refusal lapses
flowchart TD
    C["capture arrives"] --> LK["lock lineage rows, serializable"]
    LK --> RV{"lineage revoked?"}
    RV -->|yes| E1["409 — lineage has been revoked"]
    RV --> TB{"tombstone matching ANY retained key version,<br/>not yet expired?"}
    TB -->|yes| E2["409 — capture was previously revoked"]
    TB -->|no| OK["capture created, TTL set"]
    OK -.->|"declared: no writer creates or promotes a candidate"| CAND["candidate, status EPHEMERAL"]
    OK --> ART["article — the wiki page a person reads and recall returns"]
    REV["revocation: capture_deleted, principal_revoked,<br/>session_deleted, scope_deleted, consent_revoked, expired"] --> TS["tombstone: subjectHash, hmacKeyVersion,<br/>generation, reasonCode, expiresAt"]
    REV --> PR["privacy review row, status OPEN"]
    REV --> JOB["durable cleanup job, idempotency key"]
    TS -.->|"90-day TTL"| GONE["tombstone expires; the refusal lapses"]
```

The three parallel writes on revocation are the design: a record that blocks
re-entry, a review row for a person, and a job that does the cleanup — none of
them depending on the other two succeeding.

## 3. Architecture

Next.js with Postgres through Prisma, a migration history, and an optional
hybrid storage tier in separate schemas (`noosphere_hybrid`,
`noosphere_hybrid_b`) holding embedding state, an embedding job queue, a search
cache epoch and — notably — an `embedding_consent` table. Embedding is treated
as a consent-bearing operation rather than an implementation detail.

Four editor plugins ship as sibling packages, plus a `noosphere-injected-memory`
package, a stdio MCP server (`noosphere-mcp/`, 43 files, with a Codex
installer that writes only the `npx` launcher and approved variable names into
Codex's config and never an API key), and `install.sh`, a guided installer that
downloads a backend script and a Hermes bundle pinned by URL and SHA-256
(`install.sh:5-8`), refuses symlinked credential and integration parents, and
scrubs secrets from OpenClaw subprocesses.

An operator needs Postgres, Docker and a Node runtime; Docker Compose files and
the installer are provided. Hybrid retrieval is off unless
`NOOSPHERE_HYBRID_RETRIEVAL_ENABLED` is exactly `true`
(`src/lib/memory/hybrid-retrieval.ts:116-124`), and the documented local
embedding path is a llama.cpp server behind
`scripts/activate-hybrid-retrieval-stack.sh`.

## 4. Essential Implementation Paths

**Capture** — `src/lib/memory/capture/repository.ts`: `withSerializableRetry`
→ `lockLineages` → revocation check → tombstone check → create.

**Revocation** — `src/lib/memory/capture/lifecycle.ts`: a
`MemoryRevocationReason` from six values (`capture_deleted`,
`principal_revoked`, `session_deleted`, `scope_deleted`, `consent_revoked`,
`expired`) → upsert the privacy review → upsert the tombstone on
`(lineageStateId, generation)` → upsert a durable cleanup job with the
idempotency key `memory-cleanup:{lineage}:{generation}`.

**Digests** — `src/lib/memory/capture/crypto.ts`: `digestWithAllKeys` over a
`CaptureHmacKeyring`.

**Admin** — `/api/memory/{candidates,jobs,tombstones,privacy-reviews}`, with
`admin-list.ts` noting that "jobs, tombstones, and privacy reviews inherit scope
through lineage rather than [carrying it directly]".

## 5. Memory Data Model

`MemoryTombstone` is the row this report is about:

```
lineageStateId, kind, subjectHash, hmacKeyVersion, generation,
agentPrincipalId, reasonCode, expiresAt, createdAt
@@unique([lineageStateId, generation])
@@index([kind, subjectHash])  @@index([expiresAt])
```

Three details are worth naming. `generation` plus the unique constraint means a
lineage can be revoked more than once and each revocation is its own tombstone
rather than an overwrite. `reasonCode` records *why*, from the six-value
vocabulary. And the index on `(kind, subjectHash)` is exactly the shape the
write-path check queries, so the refusal costs an index lookup rather than a
scan.

`MemoryPrivacyReview` is the human side: `status` defaulting to `OPEN`,
`reasonCode`, `resolvedAt`, `resolvedBy`, unique on
`(articleId, lineageStateId, generation)` and indexed on `(status, createdAt)`.
Every revocation that touches an article opens one.

`MemoryCandidate` declares five separate usage counters —
`occurrenceCount`, `retrievedCount`, `injectedCount`, `explicitGetCount` and
`distinctSessionCount`. Separating *injected* from *explicitly fetched* is the
same distinction [Token Savior](../token-savior/) draws with `was_visible`, and
`distinctSessionCount` is the one that would stop a single enthusiastic session
promoting a memory on its own. Only `occurrenceCount` has a writer; the other
four are read by the admin list and incremented by no path in `src/`.

## 6. Retrieval Mechanics

Postgres full-text search over articles (`noosphere.ts:510`, `tx.article.findMany`)
with an optional embedding tier, gated by `restrictedTags` and `privateScopeTag`.
The MCP `recall_memory` tool is bounded to the auto mode and its response is
serialised on an isolated boundary after two fixes on 2 September 2026. `MemoryCandidate` is indexed on
`(agentPrincipalId, privateScopeTag, status, expiresAt)` — the composite that
says the read path always filters by principal *and* scope *and* status *and*
liveness.

`RestrictedScope` is a table, so a scope is a first-class row that can be
deleted — and `scope_deleted` is one of the six revocation reasons, so deleting
a scope revokes what was captured under it. Scope here is not a tag, it is an
object with a lifecycle.

The wiki side is the same data with revisions and topics, which is what makes
the human-and-agent claim true rather than aspirational: a person edits an
article, and the agent's memory is the article.

## 7. Write Mechanics

Writes are serializable transactions with an explicit retry wrapper and row
locks on the lineage, which is why the tombstone check is sound: the digest set
is computed, the lineage is locked, the tombstone is checked and the capture is
created without a window where a concurrent revocation could be missed.

The comment beside the session-digest lookup shows the same care: a
deliberately-kept query exists "so a serializable retry observes concurrent
session revocations consistently" — a read whose only purpose is to make the
transaction's conflict detection see something.

Deletion is revocation plus a cleanup job with an idempotency key, so the
cleanup can be retried without double-executing, and the tombstone stands
whether or not the job has run.

## 8. Agent Integration

Four plugin packages (OpenClaw, OpenCode, Kilo Code, Hermes), a stdio MCP
server with five tools — `search_articles`, `get_article`, `create_article`,
`save_memory`, which files a draft for later review, and `recall_memory` — an
injected-memory package, the checksum-pinned installer, and the web wiki. The
agent and the human read the same store through different surfaces, which is
the product. Between 30 August and 2 September 2026 the OpenClaw plugin's
credentials were bound to a trusted origin with native redirects rejected, and
`SecretRef` resolution was delegated to OpenClaw rather than performed in the
plugin.

## 9. Reliability, Safety, and Trust

**Tombstone — awarded, consulted kind.** Value-keyed on an HMAC digest,
normalized across the keyring, read inside the write transaction, and the write
refused with a 409. The key-rotation handling is the part that distinguishes it
from the other five consulted implementations in this atlas, none of which
computes its value key under a rotating secret.

The honest qualification is the TTL. At ninety days the tombstone expires and
the refusal lapses. The project's reasoning is visible in the comment —
historical keys are retained "until their tombstones and source TTLs have
expired", so the tombstone lifetime bounds the keyring size. That is a real
engineering trade and it means this tombstone answers "not again for ninety
days", not "never again".

**Scope — awarded.** `privateScopeTag` on the principal and on every derived
row, `RestrictedScope` as a table with its own revocation reason, and a
composite index whose leading columns are principal and scope.

**Human review — awarded.** `MemoryPrivacyReview` is a row with an `OPEN`
status, a `resolvedBy` and a `resolvedAt`, opened automatically on any
revocation touching an article and exposed through an admin API.

**Audit log — awarded.** The tombstone table is itself an append-only record of
revocations with reason codes and generations, and `MemoryDurableJob` records
every cleanup attempt under an idempotency key. Between them a reader can
reconstruct what was revoked, why, and whether the cleanup ran.

**Trust state — withheld, on a producer test.** `MemoryCandidateStatus` names
`PENDING_REVIEW`, `REJECTED` and `QUARANTINED`, which is an epistemic
vocabulary in shape; `QUARANTINED` is the one value with a writer and it is set
by revocation, not by a judgement, and nothing creates the candidate row it
would sit on. On captures the same status is a hard filter — `repository.ts:155`
refuses a quarantined or expired lineage with a 409 and the capture route
(`captures/[id]/route.ts:121`) hides them — which is revocation reaching the
write path, which the tombstone paragraph above credits.

**Bitemporal — no**; every timestamp is record time. **Negative eval — no.** The
race suite asserts a revoked principal's capture fails and leaves no row, which
is a write-path refusal; the recall tests that assert an empty result
(`api-recall.test.ts:236,:259`) cover a failing provider and a timeout, not
material withheld. The admin routes answer an open question of the first
reading: `authorizeMemoryAdminList` requires `Permissions.ADMIN` after a rate
limit and narrows to the key's `allowedScopes`, so a privacy review is resolved
by an admin key, not a named person.

## 10. Tests, Evals, and Benchmarks

**No paper.** 87 files under `src/__tests__`, including
`capture-integration.test.ts` and `capture-race-integration.test.ts` — the
second of which exists because the tombstone check and the capture creation must
be correct under concurrency, and it is the right test to have written. Its five
cases hold a lock, race a revocation or a scope deletion against a capture, a
key create or a recall hydration, and assert which side wins and what rows
remain; what none of them asserts is the plain 409 on re-capturing a revoked
value outside a race. Two files arrived since the previous pin, both security:
`openclaw-secret-ref-boundary.test.ts` and `yaml-resource-limits.test.ts`.

**I ran nothing.** The screen flagged `.github/copilot-instructions.md` as an
auto-run surface and twelve dependency manifests inside the seven-day cooldown.

No retrieval benchmark is committed and none is claimed. For a system whose
distinguishing work is revocation correctness rather than ranking, the tests
that matter are the concurrency ones, and they exist.

## 11. For Your Own Build

### Steal

- **Check the tombstone inside the write transaction, after locking.** The
  refusal is only sound if a concurrent revocation cannot slip between the check
  and the insert.
- **If your value key is an HMAC, keep the old keys and check them all.** This
  is the failure mode nobody else in this atlas has addressed: rotate the key and
  every rejected value silently becomes acceptable again. `digestWithAllKeys`
  plus a bounded keyring is the fix.
- **Store the key version on the tombstone.** `hmacKeyVersion` beside
  `subjectHash` is what makes the keyring's retention policy auditable.
- **Refuse with a status code, not a no-op.** A 409 saying "Capture was
  previously revoked" tells the caller what happened; a silent skip does not.
- **Give revocation a reason vocabulary.** Six values covering deletion,
  principal revocation, session deletion, scope deletion, consent withdrawal and
  expiry — each of which propagates differently.
- **Write the tombstone, the review and the cleanup job as three independent
  upserts.** None depends on the others succeeding, and the idempotency key means
  the job can be retried.
- **Make scope a row, not a tag.** `RestrictedScope` can be deleted, and
  `scope_deleted` revokes what was captured under it.
- **Count distinct sessions, not just occurrences.** One enthusiastic session
  should not promote a memory.
- **Treat embedding as consent-bearing.** An `embedding_consent` table says
  sending text to an embedding provider is a decision, not a detail.
- **Keep a query whose only purpose is conflict detection.** The comment says it
  plainly, and without it a serializable retry would miss a concurrent
  revocation.

### Avoid

- **Do not read a TTL'd tombstone as permanent.** Ninety days is deliberate and
  bounded; if your requirement is "never again", this shape needs an unbounded
  tier beside it.
- **Do not assume the review queue is worked.** The rows open automatically;
  nothing found forces resolution, and `resolvedBy` can stay null indefinitely.

### Fit

This suits a small team or an individual who wants one store that is both agent
memory and a human wiki, is willing to run Postgres, and cares about revocation
being real — consent withdrawal, session deletion, scope deletion — rather than
best-effort.

Even a project with no interest in the wiki should read
`src/lib/memory/capture/repository.ts:230-260` and
`lifecycle.ts:385-420`. Fifty lines, and between them the strongest answer in
this atlas to "how do I make a deletion stick".

## 12. Open Questions

- **What happens on day ninety-one?** The tombstone expires and the same content
  can be captured again. Whether that is reachable in practice depends on the
  source TTLs, and the interaction was not traced end to end.
- **Will the candidate tier get a writer?** The schema, the counters and the
  promotion module are all there; a capture that becomes a candidate that
  becomes an article is the design the wiki side implies, and no path runs it.
- **Does the candidate promotion ladder consult the tombstone?** The capture
  path does; whether a candidate distilled before a revocation is cleaned up by
  the job or blocked at promotion was not traced.
- **How large does the keyring get?** Bounded by the tombstone TTL by design;
  no figure is published.

## Appendix: File Index

**The tombstone** — `src/lib/memory/capture/repository.ts:241-254` (the check
and the 409), `src/lib/memory/capture/lifecycle.ts:398-412` (the upsert and
`TOMBSTONE_TTL_MS`), `prisma/schema.prisma:507` (`MemoryTombstone`),
`src/lib/memory/capture/crypto.ts` (`digestWithAllKeys`, `CaptureHmacKeyring`)

**Revocation** — `src/lib/memory/capture/lifecycle.ts:13-19` (the reason
vocabulary), the privacy-review and durable-job upserts `:385-425`

**Schema** — `prisma/schema.prisma` (`MemoryAgentPrincipal` `:246`,
`MemoryCapture` `:273`, `MemoryCandidate` `:323`, `MemoryRetrievalStat` `:407`,
`MemoryLineageState` `:447`, `MemoryProvenanceEdge` `:477`, `MemoryDurableJob`
`:527`, `MemoryPrivacyReview` `:560`, `RestrictedScope` `:231`)

**Concurrency** — `withSerializableRetry` and `lockLineages` in
`repository.ts`, the deliberate conflict-detection read `:256-267`

**Admin** — `src/app/api/memory/tombstones/route.ts`,
`src/lib/memory/capture/admin-list.ts`

**Hybrid storage** — `docker/hybrid-storage/feature-schema.sql`,
`phase-b-schema.sql` (`embedding_consent`, `embedding_job`,
`search_cache_epoch`)

**Integration** — `openclaw-noosphere-memory/`, `opencode-noosphere-memory/`,
`kilocode-noosphere-memory/`, `hermes-noosphere-memory/`,
`noosphere-injected-memory/`, `noosphere-mcp/` (`src/server.ts` for the five
tools), `install.sh`, `scripts/activate-hybrid-retrieval-stack.sh`

**Candidates** — `prisma/schema.prisma:323` (`MemoryCandidate`),
`src/lib/memory/promotion.ts` (the unpersisted review flow),
`src/app/api/memory/candidates/route.ts` (the one reader)

Searches behind the absence claims above, run from the repository root:

```sh
rg -n 'memoryCandidate\.(create|update|upsert|updateMany)' src   # lifecycle.ts:346 only
rg -n 'INSERT INTO "MemoryCandidate"' . -g '!node_modules'          # docker rehearsal fixture only
rg -n 'PROMOTED|PENDING_REVIEW|REJECTED' src/lib src/app -g '!__tests__'   # no producer
rg -n 'retrievedCount|injectedCount|distinctSessionCount' src -g '!__tests__'   # selects only
rg -n 'validFrom|validUntil|observedAt' prisma/schema.prisma        # none
rg -n -i 'arxiv|bibtex|citation|doi' README.md docs                  # no paper
```

**Tests** — `src/__tests__/memory/capture-integration.test.ts`,
`capture-race-integration.test.ts`

## History

**2026-09-05** — [`feb04e0d07a48ae988095bd9631307f6fcfd47bc`](https://github.com/sweetsophia/noosphere/commit/feb04e0d07a48ae988095bd9631307f6fcfd47bc) — re-pinned at release 1.13.3, 207 commits on, on top of [neoneye/agent-memory-atlas#21](https://github.com/neoneye/agent-memory-atlas/pull/21) from the repository's maintainer, whose reading is confirmed on every point it made: the capture tombstone, the keyring and the schema are byte-for-byte unchanged since the previous pin (`git diff --stat` over `src/lib/memory` and `prisma` is empty), the cited lines hold, the marks hold, and the new surface is the Codex MCP server and a checksum-pinned installer. Screened again: one auto-run surface (`.github/copilot-instructions.md`), no build-time execution, eight unpinned surfaces behind lockfiles, twelve manifests inside the seven-day cooldown. Nothing was installed or run. **One thing the first reading published was wrong, and it was wrong at that pin too:** the candidate tier. The body described a status ladder promoted by usage counters; in `src/` nothing creates a `MemoryCandidate`, nothing sets `PROMOTED`, `PENDING_REVIEW` or `REJECTED`, four of the five counters are never incremented, and recall reads articles. The mechanism is schema plus an unpersisted promotion module, and the report now says so; `trust_state` was withheld before and stays withheld, on a producer test rather than a vocabulary test. Also corrected: the previous size figure, and the open question on who resolves a privacy review, which the admin routes answer. The evidence block was written from the tree rather than taken from the pull request, whose records listed no covering tests.

**2026-08-09** — [`8bb93ee67d46e661f47ab16a23d03c84a0bb08de`](https://github.com/sweetsophia/noosphere/commit/8bb93ee67d46e661f47ab16a23d03c84a0bb08de) — first reading. Screened before reading: one auto-run surface (`.github/copilot-instructions.md`), no build-time execution, ten dependency manifests inside the seven-day cooldown. The tree was read, never installed, and no test was run.

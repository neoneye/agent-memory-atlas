---
title: Memory Engine
eyebrow: Agents as principals
description: A Postgres memory service where the agent is a first-class access-control principal with its own credentials, and a clamp makes over-granting an agent harmless by construction.
root: ../..
page_kind: system
source_name: timescale/memory-engine
source_url: https://github.com/timescale/memory-engine
revision: 54e4d7d201b5
revision_url: https://github.com/timescale/memory-engine/commit/54e4d7d201b5
analyzed_at: 2026-07-28
capabilities: "bitemporal, scope_enforced"
matrix:
  memory_unit: "Row in one `memory` table: content, name, meta, tree path, temporal range, embedding"
  storage: "PostgreSQL 18 — ltree, pgvector/halfvec, BM25, JSONB, tstzrange; schema per space"
  retrieval: "Hybrid BM25 plus semantic via Reciprocal Rank Fusion, computed in SQL functions"
  write: "JSON-RPC create/batchCreate requiring an explicit tree; importers for git, sessions, packs"
  update_delete: "Update, delete by id or path, `deleteTree` for a subtree; onConflict error/replace/ignore"
  scoping: "`tree_access(space, principal, ltree path, level)` evaluated inside the search SQL; agents clamped to their owner"
  integration: "JSON-RPC over HTTP, MCP, CLI, web UI, harness adapters for Claude, opencode, Codex, Gemini"
  background: "Worker pool; embedding generation; importers"
  trust: "Authorization by principal and path; `authenticatedAs` recorded for observability only"
  strengths: "Agents are principals, and the agent grant clamps to its owner so over-granting cannot escalate"
  risks: "No trust state or correction semantics; memory is a well-governed store, not a belief model"
---

## 1. Executive Summary

Memory Engine is Timescale's Apache-2.0 memory service: about 51,000 lines of
TypeScript on Bun over PostgreSQL 18, using ltree, pgvector/halfvec, BM25, JSONB
and tstzrange rather than application-layer abstractions. Memories live in one
table per space, searched by hybrid BM25 and semantic retrieval fused with RRF
inside SQL functions.

The memory model is deliberately plain. The access model is the most developed
in this atlas, and it is the reason to read the repository.

**The agent is a first-class principal.** Principals are users, *agents*,
service accounts, or groups; an agent has its own api key, its own grants, and
its own identity in the authorization tables. Everywhere else in this atlas an
agent acts with the user's authority or with none, and "which memories may this
agent read" is not a question the schema can express.

Grants are `(space, principal, tree_path, level)` with three additive levels —
read, write, owner — where `tree_path` is an ltree, so a grant covers a subtree.
And the safety property that makes it workable:

> "a member may grant/revoke their **own agents** at any path… safe because
> `agent_tree_access` clamps an agent to `least(agent, owner)` at every path, so
> an over-grant clamps **down** to the owner's level rather than escalating"

That clamp is the good idea. Letting people delegate to their own agents without
an approval workflow is only safe if delegation cannot exceed the delegator, and
making that a `least()` at every path means a careless or malicious over-grant is
*harmless by construction* rather than caught by a check somebody might forget.
A joining agent is even provisioned at `owner@home.<owner_id>.<agent_id>` —
nested inside its owner's home so the owner's grant covers it and the clamp stays
effective.

Three more decisions are worth the read. Authorization is evaluated **inside the
search SQL**: `core.build_tree_access(principalId, spaceId)` produces a
`_tree_access` jsonb passed into `search_memory` and friends, so a principal's
visibility and the ranking are one query rather than a filter applied afterwards.
Writes **require an explicit `tree`**, because "callers choose `share` vs `~`
deliberately". And a space creator gets `admin + owner@home + owner@share` but
deliberately **not** `owner@root`, so creating a space does not grant sight of
other members' private trees.

Reservations. This is memory as a governed *store*, not as a belief model: there
is no trust state, no candidate/verified distinction, no supersession chain, no
contradiction handling, and no tombstone. It knows exactly who may read a
memory and nothing about whether the memory is true.

## 2. Mental Model

```text
core (control plane)                     me_<slug> (data plane, one per space)
  principal   u | a | s | g                memory
  space                                      id uuid v7 (check-constrained)
  principal_space  (admin = structural)      content, name
  group_member                               meta   jsonb
  tree_access (space, principal,             tree   ltree
               tree_path ltree,              temporal tstzrange
               access 1|2|3)                 embedding halfvec(1536)
  api_key                                    embedding_version int4
```

Two authority axes, kept apart:

| Axis | Carried by | Governs |
| --- | --- | --- |
| **structural** | `principal_space.admin` | roster, groups, invitations |
| **data** | `owner@path` | reading and writing memory under a subtree |

Reserved tree roots: `home.<member_id>` (input sugar `~`) and the shared
`share`. An owner grant at any path delegates access-management *within that
subtree*, and `owner@root` is the whole space.

## 3. Architecture

Packages, in lines of TypeScript excluding tests:

- `cli/` (27,443) — much of the surface, including harness adapters.
- `server/` (7,085) — JSON-RPC endpoints, auth middleware.
- `web/` (2,549), `protocol/` (2,299), `database/` (2,303), `engine/` (1,789),
  `embedding/` (1,281), `client/` (1,182), `worker/` (748).
- `queries/` — seventeen numbered psql benchmark files plus tuned variants.

```mermaid
flowchart LR
  Cred["OAuth · api key · cookie"] --> MW["middleware resolves principal"]
  MW --> BTA["core.build_tree_access(principal, space)"]
  BTA --> TA["_tree_access jsonb: paths + levels"]
  TA --> SQL["search_memory(...) in SQL"]
  Mem["me_slug.memory"] --> SQL
  SQL --> RRF["BM25 + semantic, fused by RRF"]
  RRF --> Out["visible, ranked results"]
  Agent["agent principal"] --> Clamp["agent_tree_access = least(agent, owner)"]
  Clamp --> TA
  W["memory.create — tree required"] --> Mem
```

## 4. Essential Implementation Paths

### Agents as principals, clamped to their owner

The clamp is the mechanism this atlas has been missing without naming it. Every
system here that mounts memory into an agent grants the agent whatever the
process has. Ask "can this agent read the other project's memories?" and the
answer is a property of the deployment, not of the data model.

Memory Engine answers it in the schema, and then solves the delegation problem
the answer creates. If agents are principals, someone must grant them access —
and routing every grant through an owner approval makes the feature unusable,
while allowing self-service invites privilege escalation. `least(agent, owner)`
at every path dissolves the dilemma: a member may grant their own agents freely,
because the grant is evaluated against their own level at that path. Over-grant
and it clamps down; lose access yourself and your agent loses it too, without a
revocation sweep.

The `X-Me-As-Agent` header carries the same discipline into impersonation, with
a stated **parity invariant** — acting as your own agent gives "exactly what the
agent's own `ME_API_KEY` could do", with management operations barred. The human
is recorded as `authenticatedAs` "for observability only (never gates authz)",
which is precisely the right split between an audit field and an authorization
field, and one that systems get wrong in the other direction all the time.

### Authorization inside the ranking query

`build_tree_access` materializes the caller's grants as jsonb and passes it into
the space SQL functions. Visibility is therefore a join condition in the same
statement that ranks, not a filter applied to results afterwards.

The difference matters for a reason the
[scope as a first-class key](../../patterns/scope-as-a-first-class-key/) pattern
states and few systems honour: a post-filter interacts badly with `LIMIT`. Rank
first and filter after, and a user with narrow grants gets fewer than *k* results
— or the system silently over-fetches to compensate, and the effective ranking
changes with the caller's permissions.

### A documented negative result on RLS

The obvious way to do this in Postgres is row-level security, and the repository
says plainly why it does not:

> "**Access via `tree_access`, not RLS**: RLS was unperformant."

There is no `me.user_id` GUC, and `queries/13-tree-access.sql` — labelled "Direct
RLS helper expansion benchmark" — keeps the replacement measurable.

This atlas complains repeatedly that systems do not measure their design
decisions. Here is one that tried the textbook answer, measured it, rejected it,
recorded the reason next to the alternative, and committed a benchmark to keep
watching. The engineering is unremarkable; the *documentation of a negative
result* is rare enough to be worth copying on its own.

### Writes must name their destination

`memory.create` and `batchCreate` **require** an explicit `tree`, so callers
"choose `share` vs `~` deliberately". Only file importers default a tree-less
record, and they default it to `share` via a canonically defined constant.

This is [explicit write destination](../../patterns/explicit-write-destination/)
enforced at the API boundary rather than encouraged in a tool description — the
strongest instance of that pattern the atlas has found. The pattern page argues
that defaults are acceptable only when safe, obvious and surfaced; here the
default is *absent* on the interactive path and present only where a human
already chose a file to import.

### Least privilege for the space creator

A space creator gets `admin`, `owner@home` and `owner@share` — **not**
`owner@root`. They can see the shared tree and their own home, and not other
members' homes. As an admin they *can* self-grant `owner@root`, which makes the
escalation explicit and auditable rather than implicit in provisioning.

Custom spaces can vary this (`--no-home-grants` flips the creator to "god mode"
with `owner@/`), so the safe default is a default rather than a constraint.

### Idempotent writes with visible per-row outcomes

The idempotency key is a named row's `(tree, name)` slot, else the explicit id.
`onConflict` is `error` (default), `replace`, or `ignore`, and every row reports
`{id, status}` where status is `inserted | updated | skipped` — `batchCreate`
returns one entry per input **in input order**, "so a skip is visible and ids map
back to inputs".

Importers stamp `meta.importer_version` with deterministic metadata and no
per-run timestamp, so an unchanged re-import is a genuine no-op while a version
bump makes meta differ and forces a re-render. That is a clean answer to a
problem several systems in this atlas have: re-ingestion that silently duplicates
or silently does nothing, with no way to tell which happened.

### A schema that constrains rather than documents

The memory table carries constraints that would elsewhere be conventions:

```sql
id uuid not null primary key default uuidv7()
   check (uuid_extract_version(id) = 7)
meta jsonb not null default '{}' check (jsonb_typeof(meta) = 'object')
temporal tstzrange
-- point-in-time events: lower = upper, inclusive '[same,same]'
-- time periods:         lower < upper, '[start,end)'
```

`temporal` being a **range** rather than a timestamp gives validity time
first-class treatment, with a check constraint enforcing the convention so a
caller cannot store a point-in-time event as a half-open interval and quietly
break range queries. Indexes match: GiST on `temporal` and `tree`, GIN on `meta`,
BM25 on `content`, HNSW on `embedding`.

`embedding_version int4` deserves note on its own. This atlas lists behaviour
under embedding-model change as a dimension it does not cover systematically,
because almost nothing here stamps the model that produced a vector. Memory
Engine does, which makes a re-embedding campaign a query rather than an
archaeology exercise.

## 5. Memory Data Model

One table per space: `content`, an optional filename-like `name` unique within
`(tree, name)`, `meta` jsonb, `tree` ltree, `temporal` tstzrange, `embedding`
halfvec(1536) with a version, and timestamps. Addressed by immutable id or by
`folder/name` path; `deleteTree` removes a subtree.

The stated principle is that "complexity comes from conventions in `meta` and
`tree`, not schema proliferation".

What is absent, and it is most of what this atlas cares about:

- **No trust or verification state.**
- **No supersession chain** — `replace` overwrites in place.
- **No tombstone**, so a deleted memory returns on the next import that produces
  it, subject only to the `(tree, name)` idempotency slot.
- **No provenance** beyond `meta` conventions and importer stamps.
- **No contradiction handling.**

Correction here means editing or deleting a row, with authorization checked. For
a system whose thesis is that Postgres should do the work, that is coherent — but
it means Memory Engine answers "who may read this" comprehensively and "is this
still true" not at all.

## 6. Retrieval Mechanics

Hybrid BM25 plus semantic similarity fused by Reciprocal Rank Fusion, computed
in SQL functions rather than in application code, with ltree path filters,
JSONB containment filters on `meta`, and temporal range predicates.

`queries/` holds seventeen numbered psql files mirroring the engine's generated
SQL "as closely as possible, including transaction setup, local timeouts,
`search_path`" — every combination of fulltext, semantic, meta and ltree, plus
`12-hybrid-candidates`, `14-count-visible`, and two diagnostics:
`15-diagnose-semantic-visibility` and `17-diagnose-auth-owner`.

Committing diagnostic queries for "why can this principal not see what I
expected" is the sort of thing that only exists after an incident, and it is the
operational counterpart to the atlas's complaint that nobody can explain their
retrieval.

## 7. Write Mechanics

JSON-RPC `memory.create` / `batchCreate` with a required tree, plus importers for
git history, sessions, and memory packs. A worker pool handles embedding
generation. Harness adapters inject an environment contract so a `me` call from
inside Claude, opencode, Codex or Gemini resolves to the configured agent
identity rather than the human's.

That last part matters for the access model: without it, an agent's writes would
land under the human's principal and the whole clamp would be decorative.

## 8. Agent Integration

Two JSON-RPC endpoints with deliberately different credentials — the memory data
plane accepts any bearer plus an `X-Me-Space` header; the user plane bars agent
keys entirely, because "agents can't manage the account", and key creation is
session-only so "keys can't mint keys". MCP, a CLI, a web UI, and per-harness
adapters complete the surface.

The credential-safety gate is worth noting: a `.me/config.yaml` in a repository
may pin a server only if it is on a trusted list, "so an untrusted repo's `.me`
can't redirect a global api key… to an attacker". A project-local config file
that can redirect credentials is a supply-chain hazard that several
config-file-driven systems in this atlas simply have.

## 9. Reliability, Safety, and Trust

Strengths:

- **Agents are principals** with their own credentials and grants.
- **`least(agent, owner)` clamping**, making delegation safe by construction.
- **Authorization inside the ranking query**, not as a post-filter.
- **A documented negative result on RLS**, with a benchmark retained.
- **Explicit write destination**, enforced at the API.
- **Least privilege for the space creator**, with explicit escalation available.
- **Structural and data authority kept on separate axes.**
- **`temporal` as a constrained range**, with conventions enforced by the
  database.
- **`embedding_version`**, making a model migration tractable.
- **Idempotent writes with per-row, input-ordered outcomes.**
- **Committed SQL benchmarks and access diagnostics.**
- **A trusted-server gate** on project-local config.

Gaps:

- **No trust state, correction semantics, or tombstone.** Memory is a governed
  store, not a belief model.
- **`replace` overwrites in place**, so a corrected memory leaves no history.
- **Access is evaluated per query from a materialized jsonb**, so a grant change
  mid-request is not observable — acceptable, but the staleness window is not
  documented.
- **One database, one pool**, with sharding deferred; the per-slug schema keeps
  a future split cheap but the current ceiling is a single Postgres.
- **Api-key secrets are sha256**, "not argon2" — stated plainly in the design
  notes, which is better than hiding it, but it is a weaker choice than the
  password path.

## 10. Tests, Evals, and Benchmarks

Integration tests against a real Postgres, migration tests, a CLI e2e suite, and
the `queries/` benchmark set. Nothing was run for this review.

There is no retrieval-*quality* benchmark — no labelled corpus, no recall@k, no
LoCoMo or LongMemEval harness. The measurement culture here is aimed at latency,
query plans and access correctness rather than at whether the right memory comes
back, which is the mirror image of most systems in this atlas and leaves the same
kind of hole in the other wall.

## 11. Patterns Worth Stealing

- **Make the agent a principal.** If an agent has memory, "which memories may
  this agent read" should be answerable from the schema rather than from the
  deployment.
- **Clamp delegated grants to the delegator** with `least()` at every path. It
  turns self-service delegation from a privilege-escalation risk into a
  no-op-when-wrong, and removes the need for an approval workflow.
- **Keep the impersonation parity invariant**: acting as an agent grants exactly
  what that agent could do, and the human identity is recorded for observability
  without ever gating authorization.
- **Evaluate authorization inside the ranking query**, so `LIMIT` means the same
  thing for every caller.
- **Require the write destination**, and let the default exist only where a human
  already chose the source.
- **Do not grant the creator the root.** Make the escalation an explicit,
  auditable action instead of a provisioning side effect.
- **Constrain conventions in the schema.** A check constraint on range bounds
  costs nothing and prevents a class of silent query breakage.
- **Stamp `embedding_version`** on every vector.
- **Report per-row write outcomes in input order**, so a skip is visible.
- **Commit the diagnostic queries** for "why can this principal not see this",
  not only the happy-path ones.
- **Write down the negative results**, with the benchmark that produced them.

## 12. Antipatterns / Risks

- **A governed store mistaken for a memory model.** Excellent authorization does
  not make extracted facts true, and nothing here tracks whether they are.
- **In-place `replace`** as the only correction.
- **Retrieval quality unmeasured**, in a system that measures almost everything
  else.

## 13. Build-vs-Borrow Takeaways

Borrow:

- The principal model and the agent clamp, which are transferable to any system
  where agents act on a user's behalf.
- Authorization inside the ranking query.
- The required write destination and the creator-privilege default.
- `embedding_version` and the constrained `temporal` range.

Do not copy:

- The assumption that access control is the hard part of memory. It is the part
  this repository solved.

## 14. Open Questions

- How stale can a materialized `_tree_access` be relative to a concurrent grant
  change?
- Does anything test that an over-granted agent actually clamps, or is the
  invariant only argued in documentation?
- What is retrieval quality? No labelled evaluation was found.
- Does `deleteTree` reach embeddings and any derived artifacts, or only rows?
- With `replace` overwriting in place, what recovers a memory a bad import
  clobbered?

## Appendix: File Index

- Access model: `packages/database/core/migrate/incremental/005_tree_access.sql`,
  `core.build_tree_access`, `agent_tree_access`.
- Memory schema: `packages/database/space/migrate/incremental/001_memory.sql`
  (uuidv7 check, `temporal` bounds convention, BM25/HNSW/GiST/GIN indexes,
  `embedding_version`).
- Design notes: `CLAUDE.md` (principal model, access decisions, RLS rationale,
  conflict semantics), `AUTH_DESIGN.md`, `HARNESS_DESIGN.md`.
- Benchmarks and diagnostics: `queries/01`–`17`, `queries/tuned-*.sql`,
  `queries/README.md`.
- Search: `packages/engine/ops/memory.ts` and the space SQL functions.
- Harness contract: `packages/cli/harness-contract.ts`, `packages/cli/failsafe.ts`.

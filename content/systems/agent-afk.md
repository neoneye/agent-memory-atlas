---
title: "agent-afk"
eyebrow: "A citation or an [unverified] tag"
description: "A codebase fact written without a provenance citation is recalled with an [unverified] marker in the text the model reads — and superseding it without fresh evidence carries the old citation forward with a staleness warning."
root: ../..
page_kind: system
source_name: "griffinwork40/agent-afk"
source_url: https://github.com/griffinwork40/agent-afk
revision: e3d15fe2389602c2761954baadd495d8ebe7a6a2
revision_url: https://github.com/griffinwork40/agent-afk/commit/e3d15fe2389602c2761954baadd495d8ebe7a6a2
analyzed_at: 2026-07-30
capabilities: "negative_eval"
matrix:
  memory_unit: "A fact — content, one of four CHECK-constrained categories, a source surface, a confidence float, an access count, a supersedes pointer and a nullable `evidence` citation"
  storage: "SQLite with an FTS5 external-content index and porter tokenizer, plus a `HOT.md` working file under a token cap"
  retrieval: "`facts_fts MATCH` ranked by FTS rank, with optional category and since filters, and `superseded_by IS NULL` always appended"
  write: "Three agent tools — `memory_search`, `memory_update`, `procedure_write` — writing either hot memory or the durable fact archive"
  update_delete: "`supersedeFact` sets `superseded_by` under a `WHERE superseded_by IS NULL` guard, so a double supersede is a no-op"
  scoping: "None on the read path by design — the fact archive is deliberately cross-session"
  integration: "A CLI agent with a hot working file and a durable archive behind three tools"
  background: "None; truncation of the hot file happens on write"
  trust: "A `confidence` float, and a derived `[unverified]` marker applied at render time when a codebase fact has no citation"
  strengths: "An evidence gate that reaches the prompt text rather than being dropped before it, with a stale-citation warning on supersession and twelve committed cases"
  risks: "The gate is behind `AFK_MEMORY_EVIDENCE_GATE=1`, so the default build stores codebase facts with no citation and marks nothing"
---

## 1. Executive Summary

agent-afk is an Apache-2.0 CLI coding agent whose memory is about 3,166 lines
under `src/agent/memory/` — a 945-line SQLite store, 558 lines of tools, and
129 committed test cases across the store, the tools, the loader and the gate.

**The mechanism worth the visit is the evidence gate, and its most important
property is where the verdict ends up.** A fact in the `convention` category —
a claim about the codebase — can carry an `evidence` citation: a `file:line`, a
commit SHA, a trace-event id. When one does not, recall renders it with an
`[unverified]` marker **in the text the model reads**, and the write warns.

That is the exact inverse of the failure this atlas records for
[Helm](../helm/), whose report ends on the observation that a system can compute
trust carefully and still ship it as an assertion: Helm caps a first observation
at 0.7 confidence, earns increases through corroboration, and then formats the
surviving facts as `- (kind) key: value` under *"use these, never contradict
them"*, with the number stripped off. agent-afk does the cheap version of the
same idea and does not drop it at the boundary. A model reading
`[unverified] the build uses Bazel` has been told something a confidence float
in a database never tells it.

The gate is **category-aware**, which is what makes it usable rather than
nagging. Committed tests assert that a `preference` never requires file evidence
and never warns, that a `learning` is not treated as factual codebase knowledge,
and that a `decision` is rationale rather than a gated claim. Only conventions —
assertions about how the code actually is — have to cite something.

And supersession is handled with more care than most: replacing an uncited
convention warns and stays `[unverified]`; replacing a cited one **without**
fresh evidence carries the prior citation forward *and warns it may be stale*;
supplying fresh evidence replaces it silently; supplying empty or whitespace
evidence clears it and drops back to `[unverified]`. Four distinct outcomes,
each with a test.

**The caveat is the flag.** All of this sits behind
`AFK_MEMORY_EVIDENCE_GATE=1`. The schema migration is unconditional — v3→v4 adds
the nullable column to every database — but the population and consultation of
it happen only when the gate is on. The default build is a memory system with an
unused provenance column.

## 2. Mental Model

Two tiers with different rules. `HOT.md` is the working file, capped at roughly
1,500 tokens; the durable archive is a `facts` table whose categories are
CHECK-constrained to `preference`, `convention`, `decision`, `learning`. That
four-value taxonomy is doing real work — it is what lets the gate demand
citations from one category and exempt the others, and it is enforced by the
database rather than by convention.

A fact is true until something supersedes it. `superseded_by` is a self-
referencing foreign key, search appends `f.superseded_by IS NULL`
unconditionally, and `supersedeFact` runs
`UPDATE facts SET superseded_by = ? WHERE id = ? AND superseded_by IS NULL`, so
a second supersede of the same row is a silent no-op rather than a chain
rewrite. The old row stays readable; it stops being retrievable.

There is a `confidence REAL NOT NULL DEFAULT 1.0` column, and it is a float,
which is not a trust state — every fact starts fully confident. The
`[unverified]` marker is derived at render time from `evidence IS NULL` rather
than stored as a status, so the mark is withheld and the near-miss is that the
*presentation* layer carries an epistemic distinction the *schema* does not.

```mermaid
stateDiagram-v2
    [*] --> Cited: convention written WITH a citation<br/>(a file and line, a SHA, a trace id)
    [*] --> Uncited: convention written without<br/>(warns on write)
    [*] --> Exempt: preference, decision or learning<br/>never gated, never warns

    Cited --> Cited: superseded with fresh evidence<br/>citation replaced, silent
    Cited --> Stale: superseded with NO fresh evidence<br/>prior citation carried forward + warning
    Cited --> Uncited: superseded with empty evidence<br/>citation cleared

    Uncited --> Uncited: superseded, still uncited<br/>warns again
    Uncited --> Cited: evidence supplied

    Cited --> [*]: recalled plainly
    Stale --> [*]: recalled, staleness warned
    Uncited --> [*]: recalled as "[unverified]"<br/>in the text the model reads
```

## 3. Architecture

One SQLite file and a Markdown file. `SCHEMA_VERSION = 4` is guarded in both
directions — the constructor refuses a database written by a newer build and
throws a clear error for an older schema — and the migration comments are the
best in this batch, explaining not only what changed but why each step was safe:
*"ALTER ADD COLUMN with no default → existing rows read back NULL, so the
migration cannot fail on stored data"*, and why the new columns are declared
last, *"to match the position ALTER TABLE ADD COLUMN appends it on migrated
databases, so fresh and migrated DBs share one column order"*. That second note
is a subtle correctness detail — `SELECT *` ordering differing between a fresh
and a migrated database — that almost nobody writes down.

`facts_fts` is an FTS5 external-content table over `facts` with a porter
tokenizer, kept in sync by triggers.

## 4. Essential Implementation Paths

- `src/agent/memory/memory-store.ts` (945) — schema, migrations, search,
  supersession, hot-file truncation.
- `src/agent/memory/memory-tools.ts` (558) — `memory_search`, `memory_update`,
  `procedure_write`.
- `src/agent/memory/types.ts` (122).
- `src/agent/memory/memory-evidence-gate.test.ts` (333) — twelve cases.
- `src/agent/memory/memory-store.test.ts` (557), plus a second suite under
  `tests/agent/memory/`.

## 5. Memory Data Model

`facts`: `id`, `session_id`, `created_at`, `category` (CHECK-constrained),
`content`, `source_surface`, `superseded_by`, `confidence`, `access_count`,
`last_accessed`, `evidence`. `sessions` carries surface, timings, summary,
tools used, outcome, token count, cost, and a v3 `actor` column distinguishing
`main` from `subagent`.

Two things are missing and one is present that usually is not. No validity time
— `created_at` is record time and there is no second clock. No scope key on the
read path. But `cost_usd` and `token_count` per session, and `access_count` per
fact, mean the store knows what its own memory cost to produce and how often it
paid off, which is a measurement most systems here cannot make.

## 6. Retrieval Mechanics

`facts_fts MATCH ?` ordered by FTS rank, with optional `category` and `since`
filters and `superseded_by IS NULL` always appended, limit defaulting to 10.
Lexical only — no embeddings anywhere on the memory path — which for a
few-hundred-fact archive of conventions and preferences is proportionate, and
which means recall depends on the agent's choice of query terms.

**No scope filter, deliberately.** The archive is cross-session by design; a
convention learned in one session is meant to be available in the next. For a
single-user CLI that is the right call and the mark is withheld rather than the
absence criticised.

## 7. Write Mechanics

Writes block through three tools. `memory_update` targets either hot memory or
the fact archive; `procedure_write` stores reusable procedures that persist and
are searchable through the same tool.

**The hot-file truncation is auditable in-file**, which is the second-best
detail here. When `HOT.md` exceeds its cap the truncation appends a sentinel —
an HTML comment reading *"HOT TRUNCATED to fit the ~1,500-token cap; move
durable detail to the fact archive (memory_update target:"fact")"* — so the cut
is visible to anyone reading the file and the agent is told what to do about it.
A soft warning fires at 80% of the cap before that. Compaction that leaves a
note saying it happened is rare; compaction that tells the reader where the
detail should have gone is rarer.

Nothing runs in the background.

## 8. Agent Integration

Three tools and a hot file loaded into context. The `actor` column recording
`main` versus `subagent` means a session's memories are attributable to the
execution role that produced them, though nothing filters on it at read time.

## 9. Reliability, Safety, and Trust

**`negative_eval` is earned** on `it('excludes superseded facts from search')` —
a committed assertion that a replaced value must not be retrieved. That is the
same basis as [Helm](../helm/) and [Agno](../agno/): the cheap version, since the
row is still present to be filtered on, rather than the expensive assertion that
a destroyed value does not return.

**No tombstone.** Supersession is record-keyed; nothing prevents the same content
being written again as a new fact. In a system where writes are the agent's own
tool calls rather than a background extraction pass, the exposure is smaller than
in an extraction pipeline — but a model that concluded something wrong once will
conclude it again.

**No trust state**, for the reason in §2: `confidence` is a float that is never
moved, and `[unverified]` is computed at render.

**No audit log, no bi-temporality, no human review surface.** The hot file is
Markdown a person can open, which this atlas does not count on its own.

## 10. Tests, Evals, and Benchmarks

129 test cases, none run here. The distribution is unusually well aimed: a
dedicated 333-line suite for the evidence gate covering all four supersession
outcomes and all four categories, a store suite covering the UNIQUE-collision
duplicate path and the `supersedeFact` not-found throw, and a renderer suite.

The tests are also where the design is *specified* — the gate's category rules
exist as assertions before they exist as documentation, which is why the four
outcomes above can be stated precisely at all.

No memory benchmark, no retrieval-quality measurement, no published numbers, and
none claimed.

## 11. For Your Own Build

### Steal

- **Put the verification status in the string the model reads.** `[unverified]`
  in the recalled text costs one render branch and is strictly more useful than
  a confidence column the prompt never sees. If you compute trust, ship it.
- **Gate by category, not globally.** Demanding a citation for a claim about the
  codebase and never demanding one for a user preference is what keeps the gate
  from becoming noise the agent routes around.
- **Carry a citation forward on supersede, and say it may be stale.** Replacing
  a cited fact without fresh evidence is the common case and the dangerous one;
  four distinct outcomes with four tests is the right amount of care.
- **Guard your schema version in both directions.** Refusing to open a newer
  database is the half everyone skips, and it prevents a downgrade silently
  writing garbage.
- **Declare migrated columns last.** So `SELECT *` returns the same order on a
  fresh database and a migrated one.
- **Leave a sentinel where you truncated.** An in-file marker naming the cap and
  telling the reader where durable detail belongs turns silent compaction into a
  visible, actionable one.

### Avoid

- **Shipping your best mechanism behind an off-by-default flag.** The schema
  migrates unconditionally, so the default build carries the cost of the column
  and none of its benefit; the gate is the reason to choose this system and most
  users will never see it.
- **A `confidence` column that is always 1.0.** It reads as a trust model from
  the schema and is a constant in practice.

### Fit

Take this if you are building a coding agent and want provenance without a graph
— the evidence gate is about two hundred lines of behaviour, it fits in SQLite,
and the category taxonomy is the part that makes it tolerable in daily use.

Look elsewhere for multi-tenant work: the archive is cross-session with no scope
filter, which is correct for one developer on one machine and wrong the moment
two of them share a database.

## 12. Open Questions

- **Why is the gate off by default?** It is the system's distinguishing
  mechanism and the flag name (`AFK_MEMORY_EVIDENCE_GATE`) plus the migration
  comment calling it a prototype suggest it is still being trialled.
- **Does `[unverified]` change model behaviour?** Measurable — same archive,
  same queries, marker on and off — and not measured.
- **Is `confidence` ever written below 1.0?** It is declared with a default and
  nothing found in the store moves it.
- **What consumes `access_count` and `last_accessed`?** They are maintained and
  do not appear in the ranking, which is FTS rank only.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `src/agent/memory/memory-store.ts` | 945 | Schema v4, migrations, FTS search, supersession, hot truncation |
| `src/agent/memory/memory-tools.ts` | 558 | `memory_search`, `memory_update`, `procedure_write` |
| `src/agent/memory/memory-store.test.ts` | 557 | Store behaviour, duplicate and not-found paths |
| `src/agent/memory/memory-evidence-gate.test.ts` | 333 | Twelve cases: categories and the four supersede outcomes |
| `src/agent/memory/memory-tool-renderers.test.ts` | 157 | Where `[unverified]` is applied |
| `src/agent/memory/types.ts` | 122 | The types |

## History

**2026-07-30** — [`e3d15fe2389602c2761954baadd495d8ebe7a6a2`](https://github.com/griffinwork40/agent-afk/commit/e3d15fe2389602c2761954baadd495d8ebe7a6a2) — first reading.

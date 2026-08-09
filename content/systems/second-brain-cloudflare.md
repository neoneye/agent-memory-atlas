---
title: "Second Brain"
eyebrow: "How fast a fact goes stale depends on what kind of fact it is"
description: "A durable/state/volatile classifier that abstains when unsure sets each memory's recency floor, so age becomes a tie-breaker instead of a gate."
root: ../..
page_kind: system
source_name: "rahilp/second-brain-cloudflare"
source_url: https://github.com/rahilp/second-brain-cloudflare
revision: 6a7766d4ab957c52ca642ce672f293420ce8ef46
revision_url: https://github.com/rahilp/second-brain-cloudflare/commit/6a7766d4ab957c52ca642ce672f293420ce8ef46
analyzed_at: 2026-08-09
capabilities: "trust_state, negative_eval"
matrix:
  memory_unit: "An entry with content, a JSON tag array, a source and its derived vector ids"
  storage: "Cloudflare D1 for entries and edges, Vectorize for embeddings, KV for migration ledgers"
  retrieval: "Vector search with graph expansion, MMR, and a volatility-dependent recency floor"
  write: "Capture with contradiction detection; the loser is deprecated and its vectors deleted"
  update_delete: "status canonical / draft / deprecated as a reserved tag namespace"
  scoping: "One deployment per person in their own Cloudflare account; no key on the read path"
  integration: "MCP for Claude, ChatGPT and Cursor, a desktop app, calendar and email capture"
  background: "A nightly staleness pass writing volatility and stale:as-of tags"
  trust: "status:deprecated is filtered out of recall and graph expansion; canonical raises the floor"
  strengths: "A re-embedding migration that reasons about why its own progress marker would lie"
  risks: "Reserved tag namespaces live in caller-writable tags[], which has already been exploited"
---

## 1. Executive Summary

Second Brain is a personal memory layer — TypeScript on Cloudflare Workers, D1,
Vectorize and KV, MIT, with a desktop app, a one-click deploy, MCP for Claude,
ChatGPT and Cursor, and calendar and email capture. It runs in the user's own
Cloudflare account.

**The mechanism worth the report is that staleness is a property of the
predicate, not of the row's age.**

`src/staleness/heuristic.ts` classifies a memory into three volatility classes by
matching its text:

- **durable** — `birthday`, `born`, `date of birth`, `grew up in`, `name is`,
  `nationality`, `maiden name`
- **state** — `works at`, `employed`, `job at`, `lives in`, `plans to`,
  `role at`, `position at`
- **volatile** — `meeting`, `appointment`, `deadline`

And when it cannot tell, it says so:

> "Cheap state-vs-fact classifier. Returns null when uncertain — caller should
> leave volatility unset and rely on ranking proxies until a clearer signal."

**That class then parameterises decay**, and `src/recall/math.ts` states the
failure it is fixing:

> "Because decay now bottoms out at a floor instead of exp()-ing toward zero,
> recency becomes a tie-breaker rather than a gate — a strong old match can no
> longer be buried under a fresh weak one."

`RECENCY_FLOOR_DURABLE = 0.9`, `RECENCY_FLOOR = 0.6`,
`RECENCY_FLOOR_VOLATILE = 0.15`. A birthday keeps 90% of its semantic relevance
however old it is. A meeting keeps 15%.

Nearly every system in this atlas applies one exponential decay to everything and
lets age quietly veto old truths. This one names that as the bug and fixes it
with three constants and a regex table.

**The second thing worth reading is a docstring** — the re-embedding migration in
section 7, which works out that its own obvious progress marker would silently
lie.

**And the third is a bug report against itself** — section 9.

## 2. Mental Model

Entries are text with a JSON tag array. Several reserved tag namespaces carry
system state: `status:` (canonical / draft / deprecated), `volatility:`
(durable / state / volatile), and `stale:as-of`. Recall filters on those tags,
and a nightly pass writes them.

```mermaid
flowchart TD
    CAP["capture entry"] --> CD{"contradiction with an existing entry?"}
    CD -->|yes| LOSE["loser tagged status:deprecated (row kept)<br/>vector_ids cleared in D1<br/>Vectorize deleteByIds on the old vectors<br/>contradiction_losses += 1"]
    CD --> WIN["winner stored, contradiction_wins += 1"]
    CD -->|no| STORE["stored"]
    NIGHT["nightly staleness pass"] --> H{"heuristic: durable / state / volatile"}
    H -->|"uncertain"| NULLV["returns null — volatility left unset,<br/>ranking proxies used instead"]
    H --> TAG["volatility: tag, and stale:as-of when time-triggered"]
    EDIT["content-changing write"] --> STRIP["tagsAfterWrite: strip volatility and stale:as-of"]
    Q["search"] --> FILT["SQL: tags NOT LIKE '%\\"status:deprecated\\"%'<br/>AND NOT LIKE '%\\"auto-pattern\\"%'"]
    FILT --> DEC["rerankWithTimeDecay, floor by class"]
    DEC --> D9["durable or canonical or importance ≥ 4 → 0.9"]
    DEC --> D6["state, or unclassified → 0.6"]
    DEC --> D15["volatile, or task → 0.15"]
    DEC --> MMR["MMR λ = 0.7"]
    G["graph expansion"] --> GX["deprecated neighbours skipped by default"]
```

## 3. Architecture

`src/` is organised by concern: `capture`, `entries`, `recall` (search, math,
distill), `graph`, `memory` (kind, status, volatility, stale, patterns, tag-sql),
`staleness` (heuristic, pass), `compression`, `integrations`, `migration`, `mcp`,
`oauth`, `db`, `routes`, `runtime`. There is an `ARCHITECTURE.md`.

Storage is deliberately split by what each store is good at: D1 holds `entries`
and `edges` (the source of truth), Vectorize holds embeddings (derived), KV holds
migration ledgers (progress).

125 test files.

## 4. Essential Implementation Paths

**Classify** — `src/staleness/heuristic.ts` (the three pattern tables and the
abstention contract), `src/staleness/pass.ts`.

**Rank** — `src/recall/math.ts` (`getRecencyFloor` `:29-37`, the floor constants
`:20-22`, `MMR_LAMBDA` `:27`, `getHalfLifeMs` `:39-44`).

**Filter** — `src/recall/search.ts` `:259`, `src/graph/` expansion.

**Read a reserved tag safely** — `src/memory/volatility.ts` (`isVolatilityTag`,
`getVolatility`), `src/memory/status.ts`, `src/memory/stale.ts`
(`tagsAfterWrite`).

**Rebuild vectors** — `src/migration/embedding.ts`.

## 5. Memory Data Model

`entries(id, content, tags, source, created_at, vector_ids)` and
`edges(id, source_id, target_id, type, weight, provenance, metadata, created_at,
updated_at, UNIQUE(source_id, target_id, type))`.

**Everything epistemic lives in `tags`**, a JSON array on the entry:
`status:canonical|draft|deprecated`, `volatility:durable|state|volatile`,
`stale:as-of`, plus user topic tags. That keeps the schema tiny and creates the
namespace problem in section 9.

`edges.provenance` distinguishes `inferred` from other origins, which is more
than most graph layers here record about their own edges.

Entries also carry `contradiction_wins` and `contradiction_losses` counters — a
per-entry record of how often this memory won or lost against a conflicting one.
That is a small, cheap reputation signal and this atlas has seen it almost
nowhere else.

## 6. Retrieval Mechanics

Vector search, graph expansion, MMR at λ = 0.7 — "keeps the top hit intact while
stopping near-duplicate (usually recent) memories from taking every slot" — and
time decay with the per-class floor.

`src/recall/search.ts` filters deprecated entries in SQL:

```sql
AND tags NOT LIKE '%"auto-pattern"%' AND tags NOT LIKE '%"status:deprecated"%'
```

It works, and it is a `LIKE` over a JSON string rather than a structured
predicate, so it depends on the exact serialisation including the quotes. The
project knows this — `src/memory/tag-sql.ts` exists to centralise tag SQL — and
this particular filter is written inline.

Graph expansion skips deprecated neighbours by default, which is the part most
systems forget: filtering the seed set and then expanding through the graph
re-admits exactly what you excluded.

**Scope is structural, not enforced.** One deployment per person in their own
Cloudflare account, so there is no user key to apply; no read path carries one.

## 7. Write Mechanics

Capture detects contradictions. The test that pins the behaviour is worth reading
in full, because the resolution is more complete than "mark it deprecated":

- the losing row **still exists**, tagged `status:deprecated`;
- its `vector_ids` are cleared in D1;
- `deleteByIds` is called on Vectorize with the old vector ids;
- `contradiction_wins` increments on the winner and `contradiction_losses` on the
  loser.

Deleting the vectors is what makes the deprecation real. A tag filter alone
leaves the embedding in the index, where a semantic search can still reach it.

`tagsAfterWrite` strips `volatility:` and `stale:as-of` after a content-changing
write, so a classification cannot survive an edit that may have invalidated it.

**The re-embedding migration is the best-argued module in this batch.** Its
docstring has three sections, and the middle one is a silent-data-loss trap found
by reasoning about identity:

> "The obvious progress marker is `entries.vector_ids`… That does not work here,
> and the reason is worth stating because it is not obvious: vector ids are
> **deterministic**. `storeEntry` derives them from the entry id and chunk count,
> so re-embedding unchanged content into a brand new index produces
> byte-identical id strings. `vector_ids` was already non-empty before the
> migration and stays non-empty throughout.
>
> An entry the migration never reached therefore reads as 'vectorized' in D1
> while the live index holds nothing for it. `/vectorize-pending` cannot see it,
> `/stats.unvectorized` reports zero, and the dashboard's repair prompt stays
> hidden. So this ledger in KV is not merely a convenience for resuming — it is
> the only record of what has actually been rebuilt."

The other two sections are equally disciplined. **"D1 is never written
destructively"**: content is the source of truth, vectors are derived, "the worst
outcome here is a rebuild that has to be re-run, never a lost memory." And **"Why
it stops rather than pushing on"**: when the daily embedding budget runs out
every remaining entry fails identically, so "a batch that achieves nothing stops
the run and keeps its cursor" rather than "burn[ing] the rest of the run
producing identical errors while reporting hundreds of distinct 'failures'".

## 8. Agent Integration

MCP for Claude, ChatGPT and Cursor; a desktop app for Mac and Windows that
provisions the whole deployment; a one-click Deploy to Cloudflare button; OAuth;
calendar sync by pasting an iCal link (no OAuth app required) and email capture
by app password, with newsletters, marketing and receipts filtered out.

Seven "plain-language controls" in Advanced Settings expose the ranking
parameters — recency weight, diversity, graph hops, detail, duplicate strictness,
compression aggressiveness, model — applying "to your next search, with no
redeploy". Exposing the ranking constants to the person whose memory it is, in
words rather than numbers, is a design choice worth noting.

## 9. Reliability, Safety, and Trust

**Trust state — awarded.** `status` is a three-valued enum
(`canonical` / `draft` / `deprecated`) read on the read path: deprecated entries
are excluded from search SQL and skipped in graph expansion, canonical raises the
recency floor to 0.9. A discrete state, not a score, with one value that
withholds.

**Negative eval — awarded**, per section 10.

**Scope, audit log, human review, tombstone, bitemporal — no.** Contradiction
resolution deprecates the loser and deletes its vectors, which is closer to
enforcement than most; nothing is keyed on the rejected *value*, so the same
content re-captured is a new entry.

**The reserved namespace lives in caller-writable data, and it has already been
exploited.** `src/memory/volatility.ts` documents two real defects at the site,
with the exact paths:

> "Matching case-sensitively made this namespace claimable: a caller-supplied tag
> of `Volatility:durable` slipped past the filter in `withVolatility`, was
> lowercased afterwards by `captureEntry`, and left the entry carrying two
> verdicts — with the injected one winning, because `getVolatility` returns the
> first match. That turned an unvalidated string inside `tags[]` into an override
> for the validated enum."

And:

> "The first *valid* verdict, not the first tag in the namespace. Stopping at the
> first match and rejecting it made a junk tag able to shadow a real one:
> `volatility:sometimes` ahead of `volatility:durable` reported the entry as
> unclassified, which lowered its recall floor and invited the nightly pass to
> overwrite a verdict a caller had set. Nothing stops a caller writing raw tags
> in this namespace, so reading has to tolerate it."

Both are fixed. The last sentence is the one to carry away: *nothing stops a
caller writing raw tags in this namespace*, so every reader has to be defensive.
For a memory that ingests email and calendar entries — text an attacker can
supply — a reserved namespace inside user-writable data is a standing hazard,
and hardening the readers is a mitigation rather than a boundary. Storing system
verdicts in their own columns would be one.

## 10. Tests, Evals, and Benchmarks

**No paper, no retrieval benchmark, no committed results.** 125 test files.

**`test/unit/edges.test.ts` earns the `negative_eval` mark:**

```typescript
it("skips status:deprecated neighbors by default", async () => {
  db.entries.push({ id: "b", …, tags: JSON.stringify(["status:deprecated"]), … });
  db.edges.push(edge("a", "b", 0.9), edge("a", "c", 0.8));
  const out = await expandGraph(["a"], { hops: 1 }, env);
  expect(out.map(n => n.id)).toEqual(["c"]);
});
```

The deprecated neighbour has the *higher* edge weight (0.9 against 0.8), so the
test would pass trivially if expansion merely ranked; it asserts that the
material is absent. `test/unit/capture-entry.test.ts` and
`test/unit/staleness-pass.test.ts` and `test/unit/status-tags.test.ts` cover the
same namespace from the write side.

The heuristic is the part with no evaluation. Three regex tables decide how much
a memory may decay, and nothing measures their precision — a memory whose text
says "plans to" but states something durable gets a 0.6 floor, and no committed
case checks the classifier against labelled examples. The abstention contract
limits the damage, and it is the obvious place for a fixture set.

**I ran nothing.**

## 11. For Your Own Build

### Steal

- **Make staleness a property of the claim, not the row.** A birthday and a job
  title age differently, and one decay curve for both means either the birthday
  falls off or the job title never does. Three classes and a regex table is a
  cheap first cut.
- **Give decay a floor per class and say why.** "Recency becomes a tie-breaker
  rather than a gate — a strong old match can no longer be buried under a fresh
  weak one" is the failure mode; `0.9 / 0.6 / 0.15` is the fix.
- **Let the classifier abstain.** Returning `null` when uncertain, with a
  documented fallback to ranking proxies, beats forcing a class and having the
  nightly pass act on a guess.
- **Strip derived classifications when the content changes.** `tagsAfterWrite`
  removes `volatility:` and `stale:as-of` on any content-changing write, so a
  verdict cannot outlive the text it was about.
- **Delete the vectors when you deprecate the row.** A tag filter leaves the
  embedding in the index; `deleteByIds` is what makes the deprecation hold
  against semantic search.
- **Filter deprecated neighbours in graph expansion too.** Excluding them from
  the seed set and then expanding through edges re-admits exactly what you
  excluded — and test it with the deprecated node on the *higher*-weight edge.
- **Count contradiction wins and losses per entry.** A cheap standing signal
  about which memories keep turning out to be right.
- **Do not trust your progress marker because it is populated.** The
  deterministic-vector-id trap here is worth internalising: a marker derived from
  the same inputs as the work cannot tell you whether the work happened.
  Reasoning that out *before* the migration, rather than after a support ticket,
  is the whole skill.
- **Stop a batch that achieves nothing.** When the failure is a shared budget,
  pushing on converts one real error into hundreds of fake ones and burns the
  quota you will need to resume.
- **Say which store is the source of truth and which is derived**, then never
  write the source destructively during a rebuild.

### Avoid

- **Do not put system verdicts in a caller-writable tag array.** This project
  documents two exploits of its own reserved namespace and hardened the readers;
  a column the caller cannot write would have prevented both. It matters more
  here than in most systems, because email and calendar text is ingested.
- **Do not match a JSON tag with `LIKE '%"status:deprecated"%'`** when you have a
  module for tag SQL. It works and it depends on the serialisation's quoting.
- **Do not ship a classifier that sets a ranking floor without a fixture set.**
  Three regex tables decide how fast every memory decays, and nothing checks
  them.

### Fit

A strong fit for one person who wants their own memory across Claude, ChatGPT and
Cursor, in infrastructure they control, with an installer instead of a terminal.
The Cloudflare coupling is total — D1, Vectorize, KV, Workers — so there is
nothing to lift into another stack.

Read `src/migration/embedding.ts` and `src/recall/math.ts` regardless. Between
them they contain two of the better-argued paragraphs of engineering prose in
this atlas.

## 12. Open Questions

- **How accurate is the volatility heuristic?** It sets the recency floor for
  every memory and nothing measures it.
- **Does anything read `contradiction_wins` / `contradiction_losses`?** They are
  incremented; a consumer in ranking was not found.
- **Is `draft` used?** `canonical` and `deprecated` both reach the read path;
  `draft`'s effect was not traced.
- **What writes `stale:as-of` and what consumes it?** The nightly pass sets it;
  whether recall warns on it or merely filters was not established.

## Appendix: File Index

**Volatility and staleness** — `src/staleness/heuristic.ts` (`DURABLE_PATTERNS`
`:3-14`, `STATE_PATTERNS` `:16-25`, `VOLATILE_PATTERNS` `:27-31`, the abstention
contract `:33-36`), `src/staleness/pass.ts`, `src/memory/volatility.ts` (the
case-sensitivity exploit `:5-12`, the shadowing defect `:15-20`,
`getVolatility` `:22-`), `src/memory/stale.ts` (`tagsAfterWrite` `:19-21`),
`src/memory/status.ts` (`STATUS_VALUES` `:1`, `getStatus` `:5-10`)

**Ranking** — `src/recall/math.ts` (the decay-floor rationale `:13-19`, the
constants `:20-22`, `MMR_LAMBDA` `:25-27`, `getRecencyFloor` `:29-37`,
`getHalfLifeMs` `:39-44`), `src/recall/search.ts` (the deprecated filter `:259`),
`src/recall/distill.ts`

**Migration** — `src/migration/embedding.ts` (the non-destructive contract
`:15-19`, the deterministic-id trap `:21-33`, the stop-on-no-progress rule
`:35-38`)

**Storage** — `src/db/init.ts` (`entries` `:42`, `edges` `:49`),
`src/memory/tag-sql.ts`

**Tests** — `test/unit/edges.test.ts` (the deprecated-neighbour exclusion
`:115-120`), `test/unit/capture-entry.test.ts` (contradiction resolution
`:175-194`), `test/unit/staleness-pass.test.ts`, `test/unit/status-tags.test.ts`

## History

**2026-08-09** — [`6a7766d4ab957c52ca642ce672f293420ce8ef46`](https://github.com/rahilp/second-brain-cloudflare/commit/6a7766d4ab957c52ca642ce672f293420ce8ef46) — first reading. Screened before reading; the tree was read, never deployed, and no test was run.

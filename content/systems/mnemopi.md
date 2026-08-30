---
title: "Mnemopi"
eyebrow: "A decay curve per memory type"
description: "Fourteen memory types, each with its own Weibull shape and scale, recalled by four scored voices — and a provenance weight that trusts an unattributed memory more than one it knows came from a tool."
root: ../..
page_kind: system
source_name: "can1357/oh-my-pi"
source_url: https://github.com/can1357/oh-my-pi
revision: b8e8c213c1ce970f0f008edfe471bf7858fd747a
revision_url: https://github.com/can1357/oh-my-pi/commit/b8e8c213c1ce970f0f008edfe471bf7858fd747a
analyzed_at: 2026-08-23
capabilities: "bitemporal, scope_enforced, negative_eval"
capability_evidence:
  bitemporal: "the triple store | packages/mnemopi/src/core/triples.ts, packages/mnemopi/src/mcp-tools.ts:178,:667 | `triples` carries `valid_from` and `valid_until` — when the assertion held — beside a `created_at` for when the row was written, and the read filters the validity axis: `query` appends `valid_from <= ?` and `(valid_until IS NULL OR valid_until > ?)` against an `asOf` that defaults to today, ordering by `valid_from DESC`. `TripleStore.add` supersedes by closing the predecessor's interval — `UPDATE triples SET valid_until = ? WHERE subject = ? AND predicate = ? AND valid_until IS NULL` — rather than overwriting, and the MCP surface exposes `valid_from` as an ISO-date argument so a caller can assert a fact as of a time that is not now. The caveat belongs with the mark: the engine's own extraction path writes triples by raw SQL with `valid_from = isoNow()` and never reaches `TripleStore.add`, so internally-derived facts carry validity equal to record time and no predecessor is ever closed — see section 7 | packages/mnemopi/test/triples-data-dir.test.ts, migrate-triplestore-split.test.ts"
  scope_enforced: "the beam recall path | packages/mnemopi/src/core/beam/recall.ts `buildWhere` | every beam recall query is built with a visibility clause over stored columns — `(session_id = ? OR scope = 'global' OR channel_id = ?)` when a channel is supplied, `(session_id = ? OR scope = 'global')` otherwise — alongside `superseded_by IS NULL` and a `valid_until` check, and `working_memory` and `episodic_memory` both carry `session_id`, `scope`, `channel_id` and `author_id` columns. Two widenings are in the same function and are worth knowing: `ignoreSessionScope` pushes `1=1`, and so does supplying `authorId` or `authorType` without a `channelId`, so a by-author query silently searches every session | packages/mnemopi/test/beam-recall-unit.test.ts asserts a global row stays recallable under a channel filter while other-channel rows do not"
  negative_eval: "the recall regression suite | packages/mnemopi/test/ | 456 cases across 75 files, of which 158 carry an assertion that a result set does *not* contain something — `not.toContain`, an empty array, a zero count — including `beam-recall-unit.test.ts` pinning that a non-global row from another channel fails all three visibility disjuncts, and precision regressions asserting that a memory which exists is absent from a query's results | the tests are the mechanism"
stack_storage: "sqlite"
stack_retrieval: "vector, graph"
stack_source: "seeded"
matrix:
  memory_unit: "A typed memory — one of fourteen types, each carrying a `veracity` provenance class and a type-specific decay curve"
  storage: "Bun SQLite, one database per named bank under `~/.hermes/mnemopi/data/banks/`, with optional local ONNX embeddings"
  retrieval: "Polyphonic — four scored voices (vector, graph, fact, temporal) combined per memory, with MMR and an episodic graph beside them"
  write: "Regex type patterns assign a type, a base confidence and one of nine priority classes with no model call; an LLM path is optional"
  update_delete: "`forget(memoryId)`, `update(...)`, and a `sleep(dryRun)` consolidation pass that can be run without applying anything"
  scoping: "Two layers. A bank is a separate database file selected by `setBank`, and inside one, beam recall filters on stored `session_id`, `scope` and `channel_id` columns — with two documented widenings that drop the predicate entirely"
  integration: "The memory engine behind the oh-my-pi coding agent, with retain, reflect, render and edit tools and a `memory://` protocol"
  background: "`sleep` and `sleepAllSessions` consolidation, plus SHMR clustering with similarity and harmony thresholds"
  trust: "Veracity as a provenance class — stated, inferred, tool, imported, unknown — mapped to a fixed weight"
  strengths: "Per-type Weibull decay with a shape as well as a scale, a dry-run consolidation pass, a triple store that supersedes by closing a validity interval, and 456 committed cases of which 158 assert an absence"
  risks: "`unknown` provenance is weighted 0.8, above `tool` at 0.5 and `inferred` at 0.7, so a memory with no known origin outranks one whose origin is known; the extraction path writes triples with raw SQL and never reaches the only code that closes a predecessor's interval, so self-derived facts never supersede; and `memoria_facts` declares a whole fact-versioning column set that nothing in the repository writes or reads"
---

## 1. Executive Summary

Mnemopi is the memory engine inside `oh-my-pi`, MIT-licensed, described in its
own README as a Bun/TypeScript port of the Mnemosyne engine. The package is
30,593 lines, 10,459 of them in `src/core/`, with 71 test files and 420 test
cases across the memory package and the coding agent that consumes it. It is the
densest memory engine in this batch and one of the densest in the atlas.

**Its distinguishing mechanism is a decay curve per memory type, with a shape
parameter and not just a half-life.** `WEIBULL_PARAMS` gives each of fourteen
types a `k` (shape) and an `eta` (scale, in hours): `profile` at k=0.3 and
eta=8760 — a year, with a very heavy tail — `relationship` at 0.35/8760,
`preference` at 0.4/4380, down through `fact` at 0.8/720 to `context` at
0.85/360 and `observation` at 0.9/480. The comment states the intent plainly:
higher eta is slower decay, lower k is more long-term retention.

That directly answers a criticism this atlas makes elsewhere. The
[Helm](../helm/) report argues that a preference should not fall down the
ranking for being old while an event should, and that one ranking function for
both is a decision usually made unexamined. Mnemopi makes it fourteen times,
explicitly, with a two-parameter family that separates *how fast* a memory fades
from *how heavy its tail is* — which is a genuinely better instrument than the
single exponential or Ebbinghaus curve used by
[PowerMem](../powermem/), [NOOA](../nooa-memory/) and
[LivingFeed](../livingfeed/).

**And there is a number in it worth stopping on.** `VERACITY_WEIGHTS` maps
provenance to trust: `stated: 1.0`, `inferred: 0.7`, `tool: 0.5`,
`imported: 0.6`, `unknown: 0.8`. A memory whose origin is *unknown* is weighted
above one the system knows came from a tool, and above one it knows was
inferred. Whatever the intent — a neutral prior for unlabelled legacy rows is
the charitable reading — the effect is that labelling a memory's provenance
honestly can lower its standing, and the highest-trust move for an unattributed
write is to stay unattributed.

## 2. Mental Model

Memory is typed, graded by where it came from, and forgotten on a schedule that
depends on its type. There is no correction and no rejection: the fourteen types
include `COMMITMENT`, `GOAL`, `INSTRUCTION`, `ERROR` and `ARTIFACT`, and none of
them carries a status. A memory stops mattering by decaying, not by being marked
wrong.

`Veracity` is a discrete field — `stated | inferred | tool | imported | unknown`,
with a frozen `VERACITY_ALLOWED` set validating it — which is closer to a trust
state than a float. The mark is withheld because none of the five values
withholds a memory from being treated as true; they scale a weight. It is a
provenance grade, and the atlas's distinction between "how sure" and "may this be
acted on" lands on the first side.

**Commitments decay memorylessly, which is the one place the type table is
backwards.** `commitment: { k: 1.0, eta: 240.0 }` — a Weibull with k=1 is exactly
an exponential, so a commitment's survival probability has no memory of how long
it has been outstanding, and it is gone in about ten days regardless. A
commitment is the one memory type where the right behaviour is to persist
undiminished until it is discharged and then stop entirely, which is a lifecycle
rather than a curve. Mnemopi has the vocabulary for prospective memory —
`COMMITMENT` and `GOAL` as first-class types — and gives them decay where
[NOOA](../nooa-memory/) and [Gobii](../gobii/) give them an open/done state. It
is the third arrangement of that category's three requirements and it satisfies
none of them.

```mermaid
%% caption: type is decided by regex with no model call, and each type carries its own Weibull decay and a veracity weight — where labelling something inferred or tool-derived lowers its standing below leaving it unknown
flowchart TB
    In["remember()"] --> Ty["Regex type patterns<br/>→ one of 14 types + priority<br/>(no model call)"]
    Ty --> Wb["Weibull curve per type<br/>profile k=0.3 η=8760<br/>fact k=0.8 η=720<br/>observation k=0.9 η=480"]
    Ty --> Ver["Veracity weight<br/>stated 1.0 · unknown 0.8<br/>inferred 0.7 · imported 0.6 · tool 0.5"]
    Wb --> Bank[("Bank = one SQLite file")]
    Ver --> Bank
    Bank --> P["Polyphonic recall"]
    P --> V1["vector"] --> Comb["combinedScore<br/>+ voiceScores kept per voice"]
    P --> V2["graph"] --> Comb
    P --> V3["fact"] --> Comb
    P --> V4["temporal"] --> Comb
    Bank -.->|"sleep(dryRun)"| Sl["SHMR clustering<br/>similarity + harmony thresholds"]
    Ver -.->|"unknown 0.8 outranks tool 0.5"| Inv["labelling provenance<br/>honestly lowers standing"]
```

## 3. Architecture

Bun's built-in SQLite, one database per **bank** under
`~/.hermes/mnemopi/data/banks/`, selected by `setBank` / `getBank`. Embeddings
are optional local ONNX through `fastembed`, or an OpenAI-compatible remote, and
the README is explicit that no GGUF model is bundled and that **when no LLM is
configured the engine falls back to deterministic heuristic paths**. That is the
same discipline [LivingFeed](../livingfeed/) applies for a different reason —
here it means the engine is usable and testable without a key, which is why 420
tests can assert real behaviour.

The `~/.hermes/` path places this in the Hermes ecosystem, whose own memory the
atlas reviews as [hermes-agent](../hermes-agent/).

**The larger half of the engine is `src/core/beam/`**, 5,354 lines across seven
modules — `store`, `recall`, `consolidate`, `schema`, `helpers`, `types`,
`index` — against roughly 2,800 in the facade files above it. Beam owns
`working_memory` and `episodic_memory`, their consolidation, and the SQL that
every recall is built from. The polyphonic voices sit beside it and read the same
tables. A third store, `triples`, holds subject-predicate-object assertions with
their own validity interval, and is the only place in the engine where a fact can
be closed rather than replaced.

## 4. Essential Implementation Paths

- `src/core/episodic-graph.ts` (708) — the graph tier.
- `src/core/memory.ts` (679) — the `Mnemopi` facade and module functions.
- `src/core/embeddings.ts` (586), `vector-index.ts`, `binary-vectors.ts`,
  `vector-math.ts`, `mmr.ts`.
- `src/core/shmr.ts` (567) — clustered reconsolidation.
- `src/core/polyphonic-recall.ts` (563) — the four voices.
- `src/core/extraction.ts` (491) plus `extraction/client.ts` and
  `extraction/diagnostics.ts`.
- `src/core/patterns.ts` (484), `typed-memory.ts`, `weibull.ts`,
  `veracity-consolidation.ts`, `temporal-parser.ts`, `query-intent.ts`,
  `recall-diagnostics.ts`, `content-sanitizer.ts`, `cost-log.ts`, `banks.ts`.

## 5. Memory Data Model

Fourteen types — `FACT`, `PREFERENCE`, `DECISION`, `COMMITMENT`, `GOAL`,
`EVENT`, `INSTRUCTION`, `RELATIONSHIP`, `CONTEXT`, `LEARNING`, `OBSERVATION`,
`ERROR`, `ARTIFACT`, `UNKNOWN` — and nine `TypePriority` classes: `stable`,
`moderate`, `high`, `time_critical`, `decaying`, `accumulating`, `evolving`,
`persistent`, `reference`. A type pattern is a tuple of regex, type, base
confidence and priority, so classification is a table rather than a prompt.

That taxonomy is the finest-grained in the atlas, and the priority vocabulary is
doing something the type vocabulary cannot: `accumulating` and `evolving`
describe how a memory's *content* changes over time rather than what it is
about, which is a distinction nothing else here draws.

`ConsolidatedFact` is subject/predicate/object, so the fact tier is triples.

## 6. Retrieval Mechanics

**Polyphonic recall** runs four voices — `vector`, `graph`, `fact`, `temporal` —
each returning `{memoryId, score, voice}`, combined into a `PolyphonicResult`
carrying `combinedScore` and a `voiceScores` map keyed by voice. Keeping the
per-voice scores on the result rather than collapsing them is the good part: a
caller can see that a memory surfaced because of a temporal match and a weak
vector one, which is the debuggability that
[CrewAI](../crewai/)'s `match_reasons` provides in a simpler form.

Four lanes is the most in the corpus. [Hindsight](../hindsight/) runs four
independent recall arms, [Agent Memory on Supabase](../agent-memory-supabase/)
three; the *temporal* voice, backed by a `temporal-parser`, is the one nothing
else here has as a first-class lane.

`query-intent.ts` and `recall-diagnostics.ts` sit beside it, and MMR is
available for diversity.

**Scope has two layers and the inner one does the work.** A bank is a separate
SQLite file selected by `setBank`, which is partition-shaped isolation of the
kind [CAMEL](../camel/) has. Inside a bank, `buildWhere` in `beam/recall.ts`
composes a visibility clause over stored columns on every query:
`(session_id = ? OR scope = 'global' OR channel_id = ?)` when a channel is
supplied, `(session_id = ? OR scope = 'global')` otherwise, alongside
`superseded_by IS NULL` and a `valid_until` freshness check. `working_memory`
and `episodic_memory` each carry `session_id`, `scope`, `channel_id` and
`author_id`. That is a stored key reaching the query, which is what the mark
measures.

**Two widenings live in the same function, and the second is the one to know
about.** `ignoreSessionScope: true` pushes `1=1`, which is an explicit,
named escape hatch. But supplying `authorId` or `authorType` *without* a
`channelId` also pushes `1=1` — so a query that narrows by who said something
silently drops the session and channel boundary and searches the whole bank.
A filter that reads as a narrowing and behaves as a widening is the shape most
likely to be wrong in a caller's head, and nothing in the signature says so.

**The disjunction itself has a subtlety worth recording**, because it was got
wrong and fixed. `buildWhere` also appended a hard `channel_id = ?` on top of
the OR-clause, and the AND nullified the `scope = 'global'` branch: any global
row whose `channel_id` differed from the recall channel — including everything
imported with `channel_id` NULL — was silently dropped. The repository's own
analysis is the right one: *"Channel isolation is fully preserved by the
visibility OR-clause alone (other-channel, non-global, cross-session rows still
fail all three disjuncts), so removing the hard clause restores global
visibility without leaking other channels."* A redundant predicate beside a
disjunction is not redundant.

## 7. Write Mechanics

`remember` is synchronous and cheap: the type pattern table assigns type,
confidence and priority with no model call. Extraction is a separate, optional
path with its own client and a `diagnostics` module.

**`sleep(dryRun = false)` and `sleepAllSessions(dryRun = false)`** are the
consolidation entry points, and the dry-run flag is the detail worth copying.
The atlas records [Memora](../memora/) as making its pair-classifier precision
measurable through exactly this affordance and then never measuring it; Mnemopi
has the same affordance on a heavier pass, and nothing in the repository
indicates it has been used to score anything either.

SHMR clusters by cosine similarity with a second **harmony** threshold, bounded
by batch size, iteration count and minimum cluster size — all five constants
readable from the environment (`MNEMOPI_SHMR_*`), which makes the pass tunable
without a rebuild and, equally, makes any two deployments' consolidation
behaviour incomparable unless the environment is recorded.

**Supersession works for working and episodic memory and never fires for the
facts the engine derives itself.** `beam/store.ts` closes a memory with
`SET valid_until = ?, superseded_by = ?`, and both columns are filtered on every
recall, so that half holds. The triple store implements the same idea properly:
`TripleStore.add` runs `UPDATE triples SET valid_until = ? WHERE subject = ? AND
predicate = ? AND valid_until IS NULL` before inserting, which is supersession by
closing an interval rather than by deleting a row.

The extraction path does not use it. `insertKg` in `beam/consolidate.ts` writes
the triple twice over: once with raw SQL —
`INSERT INTO triples (subject, predicate, object, valid_from, source, confidence)`
with `isoNow()` — and once through `beam.triples?.add?.(...)`, the call that
would close the predecessor. **The optional chain never resolves.** `BeamMemory`
sets `this.triples = options.triples ?? null`, and none of the four
constructions in the repository — the CLI, two MCP surfaces and the `Mnemopi`
facade — passes a `triples` store; `new TripleStore` appears only inside
`triples.ts`'s own helpers and in tests. So a `(subject, predicate)` pair
extracted twice with different objects leaves two rows with `valid_until` NULL,
both satisfying the as-of filter, returned together ordered by `valid_from`
descending. The engine's correction path for derived facts is one unpassed
constructor argument away from working, and the read side cannot tell.

**And `memoria_facts` declares a fact-versioning subsystem that does not
exist.** The schema creates and migrates `version_id`, `previous_value`,
`updated_msg_idx`, `valid_from_msg_idx`, `valid_to_msg_idx` and
`source_memory_id` — a validity interval measured in conversation position, with
the prior value retained, which would be the most interesting temporal model in
this corpus. A grep of the whole repository for any of those names outside
`schema.ts` returns nothing: no writer, no reader, no test. Six columns, added
by an `addColumnIfMissing` migration that runs on every open, holding NULL
forever.

## 8. Agent Integration

The coding agent consumes it through `memory-retain`, `memory-reflect`,
`memory-render` and `memory-edit` tools, a `session-memory` module, and an
internal `memory://` URL protocol — so a memory is addressable as a resource
rather than only as a tool result. MCP tool definitions and a dispatcher ship in
the package for host integrations.

## 9. Reliability, Safety, and Trust

**`negative_eval` is earned twice over.**
`e5a-vector-voice-dense-rewire.test.ts` asserts the vector voice *"excludes
superseded and expired rows while tolerating missing query embeddings"* — both
the supersession exclusion this atlas counts and an expiry exclusion — and there
is a whole file called `recall-precision-regressions.test.ts`, one of whose
cases asserts the engine *"does not recall flat facts through storage-only
fact/entity fields"*. A dedicated regression suite for recall *precision* is the
right shape for this column and only a handful of systems here have one.

**No tombstone.** `forget(memoryId)` removes by id; nothing is keyed on the
value, and with fourteen extraction-friendly types and an optional extraction
path, re-derivation is the expected case rather than an edge one.

**No trust state**, for the reason in §2, and the veracity weighting inversion
is the report's sharpest single finding: `unknown: 0.8` above `tool: 0.5`.

**No bi-temporality, no audit log, no human review surface** were found.

## 10. Tests, Evals, and Benchmarks

456 test cases across 75 files, none run here, and their names are unusually
diagnostic — `consolidate-fact-concurrency`, `recall-precision-regressions`,
`e5a-vector-voice-dense-rewire`, and an issue-numbered reproduction file on the
agent side. A suite that names the concurrency hazard and the precision
regression it is defending is a suite written after production incidents rather
than before them.

**158 of the assertions are negative** — `not.toContain`, an empty array, a zero
count — which is what carries the mark. `beam-recall-unit.test.ts` is the file to
read: it pins that a global row stays recallable under a channel filter while a
non-global row from another channel fails all three visibility disjuncts, which
is the boundary test the scope mark asks for and most systems here do not write.

No memory benchmark, no retrieval-quality measurement and no published numbers.
Given fourteen decay curves with twenty-eight hand-set parameters, four recall
voices with a combination rule, and five veracity weights, the absence of any
committed evaluation is the gap: none of those fifty-odd constants is traced to
a measurement in the repository, and the `sleep(dryRun)` affordance that would
let the consolidation half be scored is unused.

## 11. For Your Own Build

### Steal

- **Give each memory type its own decay shape, not just its own half-life.** A
  Weibull `k` below 1 buys a heavy tail — a profile fact that fades slowly and
  then keeps fading slowly — which a single exponential cannot express. This is
  the best-argued forgetting model in the atlas.
- **Keep the per-voice scores on the result.** `voiceScores` telling you a
  memory came from the temporal lane and not the vector one is the difference
  between tuning retrieval and guessing at it.
- **Make a temporal lane first-class.** "What did I do last Tuesday" is a query
  no embedding answers well, and a parser plus a lane costs less than trying to
  make similarity handle it.
- **Ship a dry-run on every destructive pass.** `sleep(dryRun)` makes
  consolidation precision measurable, which is the only way its thresholds ever
  get better than guesses.
- **Fall back to deterministic paths with no LLM configured.** It is what lets
  420 tests assert behaviour instead of mocking a provider.
- **Name the priority axis separately from the type axis.** `accumulating` and
  `evolving` describe how content changes; `fact` and `preference` describe what
  it is. Conflating them loses one.

### Avoid

- **A provenance scale where "unknown" beats "known".** `unknown: 0.8` above
  `tool: 0.5` means honest labelling costs standing. If unlabelled rows need a
  neutral prior, give them one *below* every labelled class, or exclude them
  from the weighting entirely.
- **An exponential curve on a commitment.** k=1.0 makes a commitment's survival
  memoryless; obligations need a lifecycle, not a half-life.
- **Fifty tuning constants and no evaluation.** Twenty-eight Weibull parameters,
  five veracity weights, five SHMR thresholds — all defensible, none measured,
  and the environment-variable overrides mean two deployments cannot be compared
  unless someone recorded the environment.

### Fit

Take this if you want the most carefully modelled *forgetting* in the atlas and
you can live without correction. The type taxonomy and per-type curves are the
right instrument for a long-running personal assistant where the failure you
actually hit is an old context note crowding out a stable preference.

Look elsewhere if memory must be correctable or provable. There is no
supersession chain exposed at the facade, no rejection, no audit, and the trust
model grades where a memory came from rather than whether it holds.

## 12. Open Questions

- **Is the veracity ordering intentional?** Nothing in the file explains why
  `unknown` sits above `tool` and `inferred`, and it is the one constant here
  whose effect is counter to its evident purpose.
- **Where did fifty tuning constants come from?** The Weibull table is precise
  enough to look derived and there is no derivation in the repository.
- **Has `sleep(dryRun)` ever been used to score consolidation?** The affordance
  is there; nothing consumes it.
- **How do the four voices combine?** `combinedScore` is computed and the
  weighting between voices was not traced here.
- **Was `beam.triples` ever wired?** The call site, the interface
  (`TripleStoreLike`) and the implementation all exist and only the injection is
  missing, which reads more like an unfinished refactor than a design. Passing
  the store at the four construction sites would turn the raw-SQL insert into a
  duplicate, so the fix is a deletion as well as an injection.
- **What was `memoria_facts`'s versioning for?** Six columns describing a
  message-indexed validity interval with a retained previous value, migrated on
  every open and never touched. Either it is the design that got dropped, or it
  is the one still coming.
- **Does anything call recall with an author filter and no channel?** That
  combination drops the session and channel predicate. Whether any caller in the
  agent does it decides whether the widening is theoretical.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `src/core/episodic-graph.ts` | 708 | Graph tier |
| `src/core/memory.ts` | 679 | The `Mnemopi` facade, `sleep`, `forget`, `update` |
| `src/core/embeddings.ts` | 586 | Local ONNX and remote embedding paths |
| `src/core/shmr.ts` | 567 | Clustered reconsolidation with a harmony threshold |
| `src/core/polyphonic-recall.ts` | 563 | Four scored voices |
| `src/core/extraction.ts` | 491 | Optional LLM extraction |
| `src/core/patterns.ts` | 484 | Type pattern table |
| `src/core/weibull.ts` | — | Fourteen types, twenty-eight parameters |
| `src/core/veracity-consolidation.ts` | — | Provenance weights and fact triples |
| `src/core/typed-memory.ts` | — | Fourteen types, nine priority classes |
| `src/core/beam/` | 5,354 | `store`, `recall` (`buildWhere`), `consolidate` (`insertKg`), `schema`, `helpers` |
| `src/core/triples.ts` | — | `TripleStore.add`, the as-of `query`, interval-closing supersession |
| `src/mcp-tools.ts` | — | The tool surface, and the only caller that can supply `valid_from` |
| `test/` | 456 cases, 75 files | Precision regressions, concurrency, voices, visibility |

## History

**2026-08-23** — [`b8e8c213c1ce970f0f008edfe471bf7858fd747a`](https://github.com/can1357/oh-my-pi/commit/b8e8c213c1ce970f0f008edfe471bf7858fd747a) — second reading, 81 commits touching `packages/mnemopi` out of 2,951 in the monorepo. Screened again first: one auto-run surface, five build-time execution points, four unpinned surfaces and thirty files inside the seven-day cooldown; nothing was installed and no test was run. **Two marks are added and both were earned at the previous pin.** The first reading covered the `Mnemopi` facade and polyphonic recall and did not reach `src/core/beam/`, which is the larger half of the engine at 5,354 lines and holds the SQL every recall is built from — `buildWhere`'s visibility clause over `session_id`, `scope` and `channel_id` is present verbatim at `4df68d60`. Nor did it reach `src/core/triples.ts`, whose `valid_from`/`valid_until` interval is filtered by an `asOf` query and closed rather than overwritten on supersession. The 81 commits are hardening — SQLite page-size alignment made opt-in, one-shot prepared statements released, embed-worker IPC bounded and reaped on timeout, lifecycle-hook and auto-recall failures contained, episodic participant extraction made Unicode-aware — plus one visibility fix: a redundant hard `channel_id = ?` beside the OR-clause had been nullifying its `scope = 'global'` branch, silently dropping every global row whose channel differed, including everything imported with a NULL channel. Three findings are new and none of them moved in those commits: the extraction path writes triples with raw SQL and never reaches the only code that closes a predecessor's interval, because `beam.triples` is never supplied at any of the four construction sites; `memoria_facts` declares six fact-versioning columns that nothing in the repository writes or reads; and `buildWhere` drops its scope predicate entirely when an author filter is supplied without a channel.

**2026-07-30** — [`4df68d60438423b384b2b47fb3d6835641624757`](https://github.com/can1357/oh-my-pi/commit/4df68d60438423b384b2b47fb3d6835641624757) — first reading.

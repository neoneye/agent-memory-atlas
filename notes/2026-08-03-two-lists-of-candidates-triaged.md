# Two lists of candidates, triaged — and the recommendation points the wrong way

**Status:** triaged to a shortlist; no report written yet
**Origin:** two inputs submitted together on 2026-08-03 — a Grok assessment
naming three systems as "newer / not covered", and a raw GitHub search dump of
30 repositories created after 2026-02-03 matching *agent memory*. Checked
against the 133 reports in `content/systems/`.

Recorded because the two inputs disagree with each other about where the
interesting work is, and **the checkable evidence sides with the one that was
presented as noise.**

## The GitHub dump: 6 already reviewed, all 30 real

Matching on `source_url` against the corpus:

| Listed | Already in the atlas as |
| --- | --- |
| `TencentCloud/TencentDB-Agent-Memory` | [tencentdb-agent-memory](../content/systems/tencentdb-agent-memory.md) |
| `rohitg00/agentmemory` | [agentmemory](../content/systems/agentmemory.md) |
| `moorcheh-ai/memanto` | [memanto](../content/systems/memanto.md) |
| `akitaonrails/ai-memory` | [ai-memory](../content/systems/ai-memory.md) |
| `Gentleman-Programming/engram` | [engram](../content/systems/engram.md) |
| `Goldentrii/AgentRecall-X` | [agentrecall-x](../content/systems/agentrecall-x.md) |

**All 30 repositories exist**, verified by `ls-remote`. That is worth recording
against [the July Grok list](2026-07-30-twenty-suggestions-triaged.md), where
five of twenty were unreachable and had been for the third time. A search dump
is a different *kind* of input from a model's recollection: it cannot name a
repository that is not there. It also cannot tell you which ones matter, which
is the other half of this note.

Out of scope by kind, before any code was read — six of them are not memory
systems at all: `NirDiamant/Agent_Memory_Techniques` (tutorial notebooks),
`0xNyk/awesome-hermes-agent` (a directory), `VoltAgent/awesome-ai-agent-papers`
(a paper list), `memovai/mimiclaw` (an OS for microcontrollers),
`StarTrail-org/PixelRAG` (retrieval, nothing durable).
`OpenDataBox/MemoryData` is a **benchmark suite**, so if it earns anything it is
a row on the [benchmarks page](../content/benchmarks.md), not a report.

## The probe, and what it is not

Ten candidates were shallow-cloned and run through one uniform, cheap probe:
licence file, source lines excluding vendored trees, and how many source files
match three vocabularies — correction (`tombstone|supersede|retract`), scope
(`user_id|project_id|namespace|tenant|scope`), and committed test files.

**This is a triage instrument and not a reading.** A file matching `supersede`
may carry the word in a comment and nothing in the code; a system with no match
may implement correction under a name this probe does not know. Every number
below is a reason to look, never a finding. Two probes in this session returned
confidently wrong output before being control-tested — `timeout` does not exist
on this machine, so an existence check reported *every* repository missing
including `torvalds/linux`, and a zsh glob failure reported every candidate as
unlicensed. Both were caught by running a case whose answer was known. The
numbers below survived that treatment; they have not survived a code review,
because none has had one.

| Repository | Licence | Source | Correction | Scope | Test files |
| --- | --- | --- | --- | --- | --- |
| `fuyuxiang/echo-agent` | MIT | ~171k | **54** | 202 | **460** |
| `kitfunso/hippo-memory` | MIT | ~125k | **102** | 323 | **376** |
| `ZhangHanDong/mempal` | MIT | ~62k | 3 | 35 | 0 |
| `Agentscreator/engram-memory` | Apache-2.0 | ~52k | 16 | 60 | 47 |
| `LycheeMem/LycheeMem` | Apache-2.0 | ~28k | **0** | 9 | **1** |
| `sachinsharma9780/memweave` | MIT | ~18k | **0** | 4 | 49 |
| `ClaudioDrews/memory-os` | present | ~10k | 1 | 5 | 1 |
| `mcncarl/agent-memory-vault` | present | ~9k | 1 | 23 | 14 |
| `OPPO-PersonalAI/O-Mem` | present | ~4k | **0** | 5 | **0** |
| `Rotoslider/long-term-memory-mcp` | present | ~2k | **0** | **0** | **0** |

## The finding: the recommendation is inverted

Grok named three systems to "try" — LycheeMem, memweave, and
`long-term-memory-mcp` — and dismissed the search dump as "most high-star new
things are already in the Atlas".

Those three are **the bottom of this table on the axes this atlas judges by.**
Between them: zero files matching any correction vocabulary, and
`long-term-memory-mcp` matches nothing on scope either and ships no tests.
LycheeMem, the headline recommendation, has one test file against 28,000 lines.
They may still be good systems — memweave's *Markdown as the source of truth
with SQLite as a rebuildable index* is a shape this corpus has twenty instances
of and is a legitimate design — but they are recommended on ergonomics, and
ergonomics is not what this atlas measures.

Meanwhile the two strongest candidates by every signal here were **in the list
that was waved past**. `hippo-memory`'s own tagline is *"The secret to good
memory isn't remembering more. It's knowing what to forget"* — which is this
atlas's thesis, arrived at independently — with 102 source files touching
correction vocabulary and 376 test files. `echo-agent` describes four-layer
memory with forgetting and contradiction detection, and carries 460.

**And the recommendation cites stars.** LycheeMem is offered with "~1.2k stars"
attached. This atlas has a standing rule against adoption as evidence, and this
is now the third external instance of the inference the rule exists to prevent —
after [the Reddit star-velocity argument](2026-07-30-a-reddit-thread-triaged.md)
and the survey citations. It is the sharpest of the three, because here the
starred system is *demonstrably* the weaker candidate on mechanism, in the same
message, checkable in ten minutes.

## What to do, in order

1. **`kitfunso/hippo-memory`** — highest correction signal in the batch, MIT,
   heavily tested, and its stated thesis is deletion. **First pass done, report
   not written** — see below. The gap between the tagline and the mechanism is
   real and is the finding.

2. **`fuyuxiang/echo-agent`** — "forgetting and contradiction detection" is a
   claim about two of the atlas's seven columns. Largest codebase here.
3. **`sachinsharma9780/memweave`** — not for correction, but because
   Markdown-as-truth over a rebuildable SQLite index is the exact shape the
   [log-and-projection note](2026-08-03-the-log-and-the-projection.md) says the
   corpus blurs. A deterministic rebuild with no model in the replay path would
   be a clean second instance beside Daimon.
4. **`Agentscreator/engram-memory`** — note the name collision with
   [engram](../content/systems/engram.md) (`Gentleman-Programming/engram`),
   already reviewed and a different project. Anyone reconciling these lists by
   name rather than URL will merge them, which is the failure the
   [agentmemory collision](2026-07-29-memorypapers-against-the-atlas.md) already
   caused once.
5. **`LycheeMem/LycheeMem`** — worth a report despite the ranking, because
   *novelty is not a criterion* and a competent instance of a common design is
   evidence about the design. It should not be first.
6. **`ZhangHanDong/mempal`** — 62k lines of Rust with zero test files, which is
   either a wrong probe or the finding.

Not pursued here: `O-Mem` (research code, 4k lines, no tests — probably the
paper treatment rather than a report), `long-term-memory-mcp` (2.4k lines, no
scope, no tests), `memory-os` and `agent-memory-vault` (plausible, unremarkable
on every signal), and the eight remaining runtime-integration repos from the
dump, which look like harnesses rather than memory systems and were not cloned.

## What came of it

- **No report added.** This is a shortlist, not a review.
- **Six of thirty already covered**, and every one of the thirty reachable —
  the first candidate list submitted to this project with no dead entries.
- **One editorial rule corroborated for the third time**, and for the first time
  by a case where following the star count would have picked the weakest system
  in the batch on the atlas's own axes.
- **One name collision flagged** before it can merge two different projects.

## First pass on hippo-memory, and why it stopped there

Probed at `a9c7cca3613b6571bfb37ad1fb6c070b7c976197` (2026-08-03). 42,482 lines
in `src/` alone, MIT, 376 test files, a 25-plus-version migration ladder in
`src/db.ts`. Not read end to end, and **this is not a report** — it is the
capability pass, recorded so the next session starts from evidence rather than
from the tagline.

What the code says, against the seven marks:

- **`trust_state` — yes, and the fourth state is the finding.**
  `ConfidenceLevel = 'verified' | 'observed' | 'inferred' | 'stale'`
  (`src/memory.ts:23`). Only the first three are ever stored. `resolveConfidence`
  (`src/memory.ts:447`) short-circuits on `pinned` or `verified`, then returns
  `'stale'` when `last_retrieved` is more than 30 days old, otherwise the stored
  value — so **staleness is computed from disuse and never persisted.** A memory
  goes stale because nobody looked at it, not because anything suggested it
  stopped being true. That is the conflation
  [decay and reinforcement](../content/patterns/decay-and-reinforcement.md)
  exists to separate: retrieval frequency is being used as a proxy for continued
  truth, on a fixed 30-day threshold, in a field whose other three values are
  epistemic.
- **`audit_log` — yes.** A dedicated table with
  `ts, tenant_id, actor, op, target_id, metadata_json`, one INSERT site
  (`src/audit.ts:195`), and a typed op union covering `supersede`, `forget`,
  `promote`, `archive_raw`, `auth_revoke`, plus per-entity variants. No
  `UPDATE audit_log` exists anywhere. The one `DELETE` is retention pruning
  (`src/audit-prune.ts:92`), which is opt-in per tenant, has a dry-run mode, and
  **emits its own `audit_prune` row carrying cutoff, count and dryRun** — so, in
  its own words, operators investigating "where did old rows go" have one row
  left to find regardless of retention floor. A retention policy that records its
  own execution in the log it truncates is worth copying.
- **`tombstone` — no, and this is the finding.** The word appears nowhere in
  `src/`. `forget` (`src/api.ts:1677`) resolves to `DELETE FROM memories`
  (`src/store.ts:1654`). Correction is real but **record-keyed**: 453
  occurrences of `superseded`, a `superseded_by` pointer honoured on the read
  path (`src/ambient.ts:57`). That is the same shape as
  [core-memory](../content/systems/core-memory.md) — supersession hides a row
  and does not block a re-assertion of the value. For a project whose tagline is
  *"The secret to good memory isn't remembering more. It's knowing what to
  forget"*, the mechanism is a hard delete with an audit row.
- **`scope_enforced` — traced, and the answer is yes with the most interesting
  caveat in the batch.** `tenant_id` is a real read-path predicate
  (`src/store.ts:719-721`) and the parameter is optional, so the question was
  which callers pass it. Three populations, and each omission turns out to be
  deliberate:

  1. **The API recall path passes it** — `loadAllEntries(ctx.hippoRoot,
     ctx.tenantId)` (`src/api.ts:2229-2230`). `resolveTenantId`
     (`src/tenant.ts`) derives it from a validated API key or `HIPPO_TENANT`,
     defaulting to `default`, and carries a fix note for the case where
     `HIPPO_TENANT=""` fell through as the empty string and "broke every
     downstream tenant filter".
  2. **The CLI does not, by design.** `cli.ts` omits the argument at fifteen-plus
     sites, and a comment at `cli.ts:5942` states the rule — the load "is
     host-wide and intentionally out-of-L9-scope per plan §11 (cli.ts is
     single-tenant-per-process)", with the `tenantId` argument beside it called
     "a defensive no-op … only to mirror the canonical caller pattern".
  3. **`sleep` does not, and this is the design worth reporting.** Phase 3 of
     `sleep` loads host-wide (`src/api.ts:2789`) and hard-deletes every entry the
     quality audit grades `error` via `phases.deleteEntry` — whose signature
     `deleteEntry(hippoRoot, id, opts?)` has no tenant parameter at all. Read
     alone that is a cross-tenant delete reachable from a tenant-scoped call.
     It is not, because the route is fenced two ways: `/v1/sleep` is
     **loopback-only** and **admin-role gated**, and the 403 says why —
     *"/v1/sleep is loopback-only (host-wide consolidation; see CHANGELOG
     v1.11.4)"*.

  So the boundary is enforced in the query on the read path and **deliberately
  suspended for consolidation, with the suspension gated at the transport layer
  instead**. That is a real architectural position rather than an oversight, it
  is the kind of thing the atlas's scope mark cannot express on its own, and the
  version reference in the error string says the project met this hazard in
  production and fenced it.
- **`bitemporal` — yes, for policies, and the route to that answer is a warning.**
  The `memories` table carries `valid_from`/`valid_to` (`src/db.ts:238-240`) and
  a search of the memory read path for a filter on them returned **nothing** —
  which reads exactly like the declared-and-unwired finding this atlas
  specialises in, and would have been published as one. Widening the search to
  all of `src/` found the implementation living in `src/policies.ts`, where it is
  not decorative: `valid_from` is required and defaults to creation time,
  `valid_to` is nullable meaning open-ended, the header calls the pair "the
  queryable axis", the interval is half-open `[valid_from, valid_to)`, dates are
  normalised to fixed width so they sort lexically, and `valid_to > valid_from`
  is enforced with its own error. It also carries a fix note for a real
  read-path bug — a datetime `valid_from` "otherwise made a same-day policy
  invisible" — which is only possible in a system whose reads do filter on it.

  So validity time is tracked separately from record time and reaches the read
  path, **for policies**. On the `memories` table the columns exist and, on what
  was traced, nothing filters them. The mark is earned by the policy path; the
  uneven coverage is the sentence that belongs beside it.

- **`negative_eval` — no.** `FeatureTestCase` (`src/eval-suite.ts:32`) carries
  `id`, `category`, `query`, `expectedIds`, `description`. There is no
  must-not-appear field, so the suite can assert what recall *should* return and
  has no way to express what it must not. The near-miss beside it is more
  interesting than the mark would have been:
  `RecallResult.suppressionSummary` carries six counters describing *what was
  excluded and why* — transparency about the cutoff rather than a case asserting
  particular material must not be retrieved. Telling the caller what recall
  silently dropped is a mechanism this atlas has asked for elsewhere and should
  be written up on its own terms.
- **`human_review` — no, on what was traced.** `memory_conflicts` carries a
  `status`, and it does move — but by code, not by a person:
  `UPDATE memory_conflicts SET status = 'resolved'` fires from inside detection
  and merge (`src/store.ts:2380`, `:2497`). That is
  [resolve, don't just detect](../content/patterns/resolve-not-just-detect.md)
  with an automatic adjudicator, which is a different mechanism from a surface
  where a person decides. The dashboard was not read.

**Where it now stands.** All seven marks are traced:
`scope_enforced`, `trust_state`, `audit_log` and `bitemporal` yes;
`tombstone`, `human_review` and `negative_eval` no. That is the frontmatter a
report needs, with file and symbol behind each one.

Three readings were wrong along the way and every one was corrected by widening
a search rather than by new information: `bitemporal` was called graph-only,
then unwired, before turning out to be implemented properly one file over;
`stale` was assumed stored; `human_review` was left unassessed when the answer
was already in `store.ts`. The pattern is the same each time — a narrow grep
returning nothing reads exactly like an absence, and this method's
[characteristic failure](2026-07-28-methodology-hazards.md) is publishing that
as a finding. Two of the three would have been *criticisms* of the system, which
is the direction least likely to be reported by a reader.

**Why it still stopped.** A report at this repository's standard means tracing capture,
extraction, retrieval, injection, correction and background work end to end
through 42,000 lines, and every mark above is currently a grep with a hypothesis
attached. The
[methodology hazards](2026-07-28-methodology-hazards.md) note names this
method's characteristic failure as *producing something plausible where the code
says something adjacent*, and a report written from this much evidence would be
exactly that. The next session should start with the scope question, since it is
the one mark where the answer changes what the system is.

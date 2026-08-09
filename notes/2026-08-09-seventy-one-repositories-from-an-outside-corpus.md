# Seventy-one repositories from an outside corpus — the join, the probe, and what came back

**Status:** in progress. Twenty-one reports written and pushed across four
batches; every remaining candidate cloned, screened and probed at code level,
with the verdicts below.
**Origin:** [issue #17](https://github.com/neoneye/agent-memory-atlas/issues/17),
submitted 2026-08-09 by the author of
[AlexisOlson/somnigraph](https://github.com/AlexisOlson/somnigraph), pointing at
that project's `research/sources/index.md` and `docs/declined.md`. The submitter
asked for nothing back: *"Take whatever is useful and close this."*

Recorded because the corpus arrived with a methodological claim attached, and
the claim held.

## The claim that came with it

The issue reports that 59 of its entries were first triaged on README plus a
couple of documents — **0 dive, 7 maybe, 50 skip** — and then read at the code
level, which returned **13 dive, 41 maybe, 5 skip**. Its conclusion:

> Metadata triage was wrong in both directions. Systems that looked strong by
> benchmark cell stayed weak, and several near-skips held real mechanisms.

That is the same finding this project reached from
[the Grok list](2026-08-03-two-lists-of-candidates-triaged.md), where the two
strongest candidates on mechanism were in the batch that had been waved past.
So this pass did not read READMEs to decide what to read. Every candidate was
cloned, screened with `screen_repo.py`, and probed structurally before anything
was judged.

## The join, and what a join cannot see

Matching `source_url` in `content/systems/*.md` against every GitHub URL in the
two source files gave 97 repository URLs with no report. Four corrections
followed, and three of them are things a URL join is structurally blind to:

| Candidate | What it actually is |
| --- | --- |
| `tencent/tencentdb-agent-memory` | Redirects to `TencentCloud/TencentDB-Agent-Memory` — [already reported](../content/systems/tencentdb-agent-memory.md) |
| `campfirein/byterover-cli` | A **rename** of `campfirein/cipher`, and `git rev-parse HEAD` returns `1052ac1a5dd0fde4da8693d4712064f7876c269c` — byte-for-byte the commit [ByteRover](../content/systems/byterover.md) is pinned at |
| `getzep/zep` | Examples, integrations, ingestion and benchmarks; the engine is [Graphiti](../content/systems/graphiti.md), already reported |
| four repositories | Gone from GitHub entirely — see below |

The ByteRover case is the instructive one. A join on `source_url` cannot see a
rename, so the same repository at the same commit appeared as an uncovered
system. The atlas's own [rename convention](../content/methodology/) exists for
this and the report now carries the note.

## Four repositories are gone

`advenire-consulting/thebrain`, `arkya-ai/ember-mcp`, `jadenschwab/msam` and
**`doobidoo/mcp-memory-service`** all return 404 to both `git ls-remote` and the
API.

The last of those is worth recording on its own. It was a **DIVE** verdict in
the submitted corpus — cited there for "a reproducible zero-LLM LongMemEval-S
retrieval [harness]" — and it is named in
[the other-atlas note](2026-07-29-the-other-agent-memory-atlas.md) as a system
that directory covered. It is now unreachable. Nothing in this atlas depended on
it; the loss is that the harness the corpus praised cannot be checked by anyone.

Compare [the July Grok list](2026-07-30-twenty-suggestions-triaged.md), where
five of twenty were unreachable and had been for the third time, and
[the search dump](2026-08-03-two-lists-of-candidates-triaged.md), where all
thirty resolved. Four of 93 here, and one of them mattered.

## The probe, and what it is not

Every reachable candidate was shallow-cloned and measured on: source lines
excluding vendored trees and lockfiles, licence file presence, whether a durable
store is used, whether an MCP surface exists, test-file count, and how many files
match six vocabularies — tombstone, supersede/invalidate, validity, audit, review
and scope.

**Every number it produced is a reason to look, never a finding**, and this pass
has the failures to prove it:

- `nornicdb` returned 73 tombstone matches. They are HNSW index tombstones — a
  delete-cost optimisation with a `TombstoneRatio()` to watch — and the report
  [says so](../content/systems/nornicdb.md) rather than claiming the mark.
- `superlocalmemory` returned 29. `tombstoned` there is an `archive_status`
  value, and the reason it is not a `lifecycle` value is a documented workaround
  about not rebuilding a large CHECK constraint.
- `shodh-memory` returned 7. They are Tantivy segment tombstones, a retired
  HTTP endpoint's placeholder page, and a `-1` sentinel in a dependency parser.

Three of the four highest tombstone counts in the probe were not
rejected-value records. The one that was —
[Wenlan](../content/systems/wenlan.md), at 7 matches — ranked below all of them.

## What has been written

Twenty-one reports across four batches. The five that changed something in the
corpus rather than adding to it:

- **[Wenlan](../content/systems/wenlan.md)** — the atlas's tenth tombstone, and
  the first found on a graph layer rather than a fact layer. A dismissed
  mind-map node keeps its row, so its derived fingerprint stays occupied under
  `UNIQUE(page_id, fingerprint)`, and `ON CONFLICT … DO NOTHING` makes every
  re-proposal a no-op. Its own comment: *"a fresh uuid cannot bypass that
  tombstone — nothing is inserted."*
- **[ClawMem](../content/systems/clawmem.md)** — built the composite ranking
  stack this atlas keeps describing, measured it against the raw channel score
  with hand-labelled gold, lost 0.912 to 0.307, and shipped the negative result
  as the default.
- **[Empirica](../content/systems/empirica.md)** — measured its own store,
  found 1,267 of 1,268 resolutions expressed as staleness and exactly one as an
  error, argued that a 1-in-4199 error rate is not plausible, and added a word
  for *was never true*.
- **[YantrikDB](../content/systems/yantrikdb.md)** — withdrew four published
  benchmark conclusions in a `CORRECTIONS.md` because the condition labelled
  "structured memory" was a 120-line simulator, and published the withdrawal
  before the favourable rerun was finished.
- **[Shodh-Memory](../content/systems/shodh-memory.md)** — ships a 677-line
  self-audit of its own graph construction, written to this atlas's evidence
  rules, finding a dead resolver, a header contradicting its own code, and a
  quality gate the upsert path voids entirely.

## The pattern the batch surfaced

Four systems in ten shipped a mechanism that is fully declared and never wired:
[Memory Palace](../content/systems/memory-palace.md)'s `access_log` has a
migration, a rollback, two indexes, an ORM class and a dashboard counter and no
insert; [Kage](../content/systems/kage.md)'s org audit is three functions with
zero call sites; [OMEGA](../content/systems/omega-memory.md)'s
`flagged_for_review` is set at −3 and cleared by nothing;
[Octopoda](../content/systems/octopoda-os.md) writes a version history no read
path queries. [YesMem](../content/systems/yesmem.md) is the sharpest case —
`pending_confirmation` is written at two sites and read by none, so the
*highest-trust* learnings are the only ones whose corrections are discarded.

Three systems in the same batch handled it correctly, and the contrast is the
useful part. [Vestige](../content/systems/vestige.md) labels its dead table in
the schema — *"designed for bi-temporal edge support but was never wired …
Do NOT add queries against this table."* YantrikDB's crypto-shred module lists
what is missing under a heading of its own. And Wenlan has automated the check:
`drift_guard.rs` parses its own source with `syn` and fails CI on a
documented-but-unwired flag or a duplicated definition.

That is a pattern page's worth of material and it is not one yet.

## Out of scope by kind

Judged on structure, not on the README:

| Repository | Why |
| --- | --- |
| `microsoft/graphrag` | An indexing pipeline over a document corpus. The stored unit is a chunk of somebody's document, not a claim with an identity that can be corrected — no forget path, no supersession, no lifecycle |
| `NirDiamant/RAG_Techniques` | Tutorial notebooks |
| `ISON-format/isongraph` | A property-graph library for LLM use. Zero matches on any correction vocabulary; it is a data structure |
| `codebreaker77/fullerenes` | A Tree-sitter code-graph indexer over SQLite. Declined in the source corpus for the same reason |
| `intelligent-internet/commonground` | A multi-agent coordination ledger. Same boundary as [`Untrivial-ai/agent-orchestrator`](2026-08-09-a-mirror-that-agrees-to-forget.md): records of what happened, none of which can be false |
| `francisdu53/exia-ghost-benchmarks` | Benchmark results and methodology. A [benchmarks page](../content/benchmarks.md) row at most |

## Withdrawn by their own authors

Four candidates carry a notice from the maintainer, quoted rather than
paraphrased because the wording is the evidence:

- `muratg98/psychmem` — *"This package is no longer maintained and should not be
  used."*
- `letta-ai/claude-subconscious` — *"a demo app built using the Letta Code SDK,
  and is not intended to be used in production."*
- `vzkts/ai-smartness` — *"has reached its limits … A new project is therefore
  emerging on another repository"*, naming the successor.
- `gavdalf/openclaw-memory` — *"currently on hold … The code works, the docs are
  accurate, and issues/PRs are welcome, but response times will be slower."*

The last is different from the other three and the atlas should treat it that
way: on-hold with working code is not withdrawn. It is held here only because it
carries no source in the languages the probe counts — the memory is Markdown and
shell — which makes it a candidate for a reading rather than an exclusion.

## The shortlist, in order

Every remaining candidate was probed; these are the ones whose structure argues
for a reading, with the signal that argues for it:

1. **`quixiai/hexis`** — 182k lines, the highest review-vocabulary count in the
   remainder (60 files), MCP, 252 test files.
2. **`jumbocontext/jumbo.cli`** — 150k lines, 76 review matches, 587 test files.
3. **`sweetsophia/noosphere`** — 12 tombstone matches at 68k lines, the highest
   density in the remainder; the source corpus credits its write-time quality
   gating.
4. **`prefrontal-systems/cortexgraph`** — 12 tombstone matches at 53k lines.
5. **`milla-jovovich/mempalace`** — 14 audit matches, 137 test files.
6. **`winstonkoh87/athena-public`** — 14 audit matches at 60k lines.
7. **`virtual-context/virtual-context`** — 257k lines, 10 tombstone matches.
8. **`suanmosuanyangtechnology/memorybear`** — 410k lines, 349 scope matches;
   the source corpus credits a real ACT-R forgetting engine.
9. **`aiosai/aipass`**, **`mem9-ai/mem9`**, **`hamr0/aurora`**,
   **`omninode-ai/omnimemory`**, **`vbcherepanov/claude-total-memory`**,
   **`christopherkarani/wax`**, **`buildingjoshbetter/truememory`**,
   **`dasblueyeddevil/daem0n-mcp`** — all above 70k lines with a durable store
   and a correction vocabulary.
10. The remaining twenty-plus under 50k lines, several of which the source
    corpus flags for a single mechanism — `growth-kinetics/diffmem` for
    git-based differential memory, `rahulmranga/knowledge-worker` for
    provenance surviving compression, `alash3al/stash` for its causal-link and
    hypothesis taxonomy, `nhevers/moltbrain` for hook-driven passive capture.

## What came of it

- **21 reports added**, taking the corpus from 167 to 188.
- **Marks added**: 14 `scope_enforced`, 14 `audit_log`, 7 `trust_state`,
  5 `bitemporal`, 4 `negative_eval`, 3 `human_review`, and **1 `tombstone`** —
  the first added since the [strong-form audit](2026-08-07-the-strong-form-tombstone-subset.md),
  and a *collided*-kind instance made deliberate.
- **One rename resolved** that a URL join could not see, and
  [recorded in the report](../content/systems/byterover.md) so the next join
  does not re-report it.
- **One DIVE-tier system confirmed gone** from GitHub.
- **The corpus's methodological claim corroborated**, and the probe that
  corroborated it caught out three times as often as it hit.
- **One question from the issue is still open.** The submitter asked which
  single system they should point a local-first setup at rather than maintaining
  their own. Answering that honestly needs the shortlist read, and the answer
  will go in [the verdicts page](../content/verdicts.md) rather than here.

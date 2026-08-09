# Seventy-one repositories from an outside corpus — the join, the probe, and what came back

**Status:** in progress. Thirty-six reports written and pushed across ten
batches; every remaining candidate cloned, screened and probed at code level,
with the evidence tabulated below and no verdict claimed for anything unread.
Thirty-five of the tabulated candidates remain unread.
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

Thirty-six reports across ten batches. The six that changed something in the
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
- **[Noosphere](../content/systems/noosphere.md)** — the eleventh tombstone, of
  the *consulted* kind, and the only one in the corpus that reasons about the
  key used to compute its own key: the digest is an HMAC, so the check runs
  against every retained key version and a rotation cannot readmit a revocation.
  It added a fifth property to
  [the strong-form taxonomy](2026-08-07-the-strong-form-tombstone-subset.md).

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

## Surveyed and too thin for a report

Read at the code level, not merely probed. Each of these is in scope by kind —
something survives a session — and carries too little mechanism to justify a
page, which is a different verdict from out-of-scope and is recorded so the next
pass does not redo the read.

- **`memorix-ai/memorix-sdk`** at `71a2815cadd987da99b47469caa82d30cc125057`,
  1,299 lines. A generic memory SDK with clean interfaces
  (`VectorStoreInterface`, `EmbedderInterface`, `MetadataStoreInterface`) and a
  `MemoryAPI` of store/retrieve/delete/update/list. See below — it is worth its
  own subsection.
- **`tharavael/sovereign-ai-kit`**, 2,128 lines. An identity and persona kit:
  `templates/` with `{{DOUBLE_BRACES}}` placeholders and a generator that fills
  them. What persists is a configuration file, not a claim.
- **`haustorium12/continuity-v2`**, 2,589 lines, no tests. A read-only FTS5 and
  embedding index over Claude Code JSONL transcripts. Nothing is extracted,
  curated or corrected — the transcripts are the store and the index is
  rebuildable, which is a coherent design with no lifecycle to report on.
- **`grapeot/context-infrastructure`**, 3,496 lines. A prompt-driven Markdown
  observation log with cron-fired observer and reflector agents. The interesting
  material is in `rules/axioms/`, which is prose about attribution and trust
  rather than a mechanism.
- **`gman1911/claude-cognitive`**, 3,678 lines. Working memory and multi-instance
  coordination for Claude Code. Its own release notes describe Phase 4,
  self-maintaining docs, as "Designed, not implemented", and call the release a
  demonstration of "development transparency" — which is the right instinct and
  leaves little to analyse at this commit.
- **`jesung/claude-sleep`**, no source in any counted language. A daily-notes
  plus `MEMORY.md` convention in Markdown and shell, and the README credits the
  two-layer structure to someone else. It is a practice, not a system.

## The verdict I nearly overturned, and why I did not

`memorix-sdk` is worth a subsection because it is a live instance of this
project's own [characteristic failure](2026-07-28-methodology-hazards.md), caught
before publication.

The source corpus declines it as "a pre-alpha generic vector-store SDK whose
embedders and backends are all stubs". The first check appeared to refute that:
grepping for stubs returns a wall of `pass` bodies, and every one of them is an
`@abstractmethod` on an ABC — the ordinary Python idiom, not an unimplemented
method. Beside them sit concrete classes with real names: `OpenAIEmbedder`,
`GeminiEmbedder`, `SentenceTransformersEmbedder`, `FAISSVectorStore`,
`QdrantVectorStore`, `SQLiteMetadataStore`.

Reading the bodies is what settles it, and it settles it the other way:

- `OpenAIEmbedder.__init__` sets `self.client = None` with the comment "Would be
  initialized with `openai.OpenAI(...)`", and `embed()` returns
  `_dummy_embedding` — an MD5 hash of the text.
- `QdrantVectorStore` stores into three Python dicts and its `search()` returns
  `[]` unconditionally.
- `FAISSVectorStore` stores into the same three dicts, commented "In-memory
  storage for demo purposes", and never touches FAISS.
- `SQLiteMetadataStore` is the one real implementation — it creates a table and
  uses `sqlite3`.

So the corpus's verdict is right, with one refinement: the *embedders and vector
backends* are stubs, the *metadata store* is not. The trap is entirely in the
class names — a reader who greps for `class .*Embedder` and finds three
providers has found three names, and the atlas's rule is that a name is not a
mechanism.

**Recording this because the near-miss is the useful part.** A correction to
somebody else's code-level verdict, published on the strength of a grep for
`pass`, would have been wrong in exactly the direction this project warns about:
plausible, checkable, and refuted by reading the next thirty lines.

## The forty-five still to read, with the evidence

*Ten have since been read and are struck from this list: AIPass, total-agent-memory
(pinned at its old `claude-total-memory` URL), OmniMemory, Wax and TrueMemory in
the most recent batch, after Neuroca, Athena, mem9, AURORA and the batch before.
Thirty-five remain.*

Every one of these is cloned, screened with `screen_repo.py`, and measured.
The six read and dispositioned above are excluded.
**None has been read**, and nothing below is a verdict — the columns are the
probe output described above, and that probe caught out three times as often as
it hit. They are ordered by size because size correlates with nothing in
particular and at least sorts deterministically.

The `tomb`/`sup`/`val`/`aud`/`rev`/`scope` columns are counts of *files
containing a vocabulary match*, not counts of mechanisms.

| Repository | Lines | tomb | sup | val | aud | rev | scope | MCP | tests |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :-: | ---: |
| `memorybear` | 410,279 | 0 | 24 | 359 | 4 | 6 | 349 | MCP | 14 |
| `aipass` | 377,209 | 0 | 21 | 255 | 5 | 17 | 37 | - | 446 |
| `mem9` | 153,728 | 8 | 30 | 98 | 1 | 6 | 81 | - | 110 |
| `jumbo.cli` | 150,278 | 0 | 80 | 199 | 6 | 76 | 46 | - | 587 |
| `aurora` | 144,756 | 0 | 30 | 328 | 4 | 34 | 22 | MCP | 153 |
| `neuroca` | 133,748 | 0 | 6 | 200 | 0 | 1 | 25 | - | 21 |
| `omnimemory` | 119,082 | 0 | 10 | 239 | 5 | 3 | 21 | - | 99 |
| `claude-total-memory` | 109,121 | 0 | 57 | 84 | 4 | 4 | 7 | MCP | 145 |
| `wax` | 100,459 | 1 | 61 | 74 | 1 | 11 | 7 | MCP | 0 |
| `truememory` | 73,324 | 0 | 29 | 72 | 1 | 17 | 14 | MCP | 182 |
| `daem0n-mcp` | 71,142 | 0 | 40 | 72 | 0 | 3 | 4 | MCP | 106 |
| `pltm-claude` | 67,404 | 0 | 29 | 91 | 0 | 25 | 20 | MCP | 36 |
| `memoir` | 65,426 | 1 | 12 | 46 | 1 | 4 | 142 | MCP | 51 |
| `memomind` | 63,390 | 0 | 6 | 42 | 1 | 0 | 12 | MCP | 0 |
| `athena-public` | 60,196 | 0 | 27 | 172 | 14 | 29 | 3 | MCP | 17 |
| `gitmem` | 59,882 | 0 | 18 | 125 | 2 | 4 | 34 | MCP | 84 |
| `second-brain-cloudflare` | 58,269 | 0 | 15 | 36 | 2 | 1 | 41 | MCP | 125 |
| `context-mem` | 55,951 | 0 | 19 | 50 | 6 | 25 | 0 | MCP | 99 |
| `moltbrain` | 54,392 | 0 | 5 | 55 | 0 | 1 | 4 | MCP | 40 |
| `engram` | 48,839 | 7 | 9 | 25 | 5 | 0 | 63 | MCP | 32 |
| `agent-working-memory` | 45,028 | 0 | 61 | 70 | 5 | 3 | 8 | MCP | 49 |
| `mengram` | 40,820 | 0 | 13 | 14 | 2 | 5 | 5 | MCP | 15 |
| `fidelis` | 37,902 | 0 | 8 | 31 | 3 | 8 | 8 | - | 31 |
| `telemem` | 33,049 | 0 | 1 | 40 | 0 | 1 | 62 | MCP | 20 |
| `openmemory` | 32,965 | 0 | 11 | 35 | 0 | 1 | 33 | MCP | 11 |
| `opencode-mem` | 32,329 | 0 | 7 | 27 | 0 | 0 | 0 | - | 65 |
| `cortex-engine` | 32,280 | 0 | 12 | 38 | 1 | 1 | 128 | MCP | 35 |
| `obsidian-mind` | 29,232 | 0 | 17 | 40 | 2 | 5 | 3 | MCP | 55 |
| `ori-mnemos` | 25,339 | 0 | 7 | 37 | 1 | 3 | 0 | MCP | 35 |
| `vir` | 22,884 | 0 | 3 | 11 | 0 | 8 | 0 | MCP | 46 |
| `yourmemory` | 22,060 | 0 | 4 | 9 | 5 | 11 | 9 | MCP | 5 |
| `memsearch` | 20,330 | 0 | 5 | 15 | 1 | 5 | 4 | - | 32 |
| `claudest` | 20,209 | 0 | 5 | 58 | 5 | 8 | 26 | - | 18 |
| `mnemos` | 19,775 | 1 | 7 | 28 | 8 | 0 | 6 | MCP | 84 |
| `nocturne_memory` | 19,433 | 0 | 4 | 21 | 0 | 6 | 41 | MCP | 13 |
| `diffmem` | 14,784 | 0 | 5 | 23 | 0 | 1 | 9 | - | 22 |
| `memcp` | 14,313 | 0 | 11 | 28 | 1 | 0 | 2 | MCP | 26 |
| `arcrift` | 13,445 | 0 | 3 | 19 | 0 | 0 | 3 | MCP | 12 |
| `memv` | 11,951 | 0 | 22 | 23 | 1 | 1 | 2 | MCP | 15 |
| `agentmemory` | 11,928 | 0 | 15 | 22 | 7 | 5 | 18 | - | 0 |
| `memory-ts` | 11,622 | 0 | 12 | 3 | 0 | 1 | 17 | - | 1 |
| `memlayer` | 9,229 | 0 | 0 | 6 | 0 | 1 | 0 | - | 7 |
| `stash` | 7,933 | 0 | 2 | 18 | 3 | 0 | 49 | - | 1 |
| `knowledge-worker` | 7,466 | 0 | 1 | 18 | 0 | 8 | 2 | MCP | 7 |
| `marsnme` | 3,899 | 1 | 5 | 11 | 0 | 0 | 13 | MCP | 2 |
| `claude-cognitive` | 3,678 | 0 | 0 | 26 | 3 | 1 | 0 | MCP | 0 |
| `context-infrastructure` | 3,496 | 0 | 0 | 8 | 1 | 0 | 3 | - | 1 |
| `continuity-v2` | 2,589 | 0 | 0 | 0 | 1 | 0 | 0 | MCP | 0 |
| `sovereign-ai-kit` | 2,128 | 0 | 0 | 0 | 1 | 0 | 1 | - | 0 |
| `memorix-sdk` | 1,299 | 0 | 1 | 2 | 0 | 0 | 0 | - | 1 |
| `claude-sleep` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | - | 0 |

Reading these in size order would be the wrong call, and reading them by
tombstone count would have put three index-tombstone false positives at the
front of this pass. The order the shortlist above proposes is by *which axis of
this atlas is thinnest* — correction and governance — and then by whether the
probe suggests the repository has anything on that axis at all.

Four rows deserve a note now rather than after a reading:

- **`memorybear`** is the largest and has the highest scope count in the
  remainder. The source corpus credits it with "a genuine ACT-R forgetting
  engine" and marks its self-reported LoCoMo numbers as lower than the
  submitter's own. Both claims are checkable and neither is checked here.
- **`jumbo.cli`** carries the highest review-vocabulary count of anything left
  (76 files) beside 587 test files, which is the profile of a system with a
  real workflow rather than a flag.
- **`aipass`** has 446 test files and the second-largest source tree, and the
  source corpus describes its memory as "a minimal file-JSON-hot + ChromaDB-cold
  vector store" — a large system whose memory is small, which is exactly the
  shape metadata triage gets wrong in the direction the issue warns about.
- **`neuroca`** was declined in the source corpus as "alpha; ~110K lines of
  AI-generated scaffolding, integration tests all skipped". The probe agrees on
  the scale and says nothing about the scaffolding claim, which needs a reading
  to confirm or overturn — and confirming somebody else's decline is worth as
  much as overturning it.

## What came of it

- **36 reports added**, taking the corpus from 167 to 203.
- **Marks added**: 18 `scope_enforced`, 18 `audit_log`, 9 `trust_state`,
  5 `bitemporal`, 5 `negative_eval`, 5 `human_review`, and **2 `tombstone`** —
  the first two added since the
  [strong-form audit](2026-08-07-the-strong-form-tombstone-subset.md), one
  *collided*-kind made deliberate and one *consulted*-kind that survives key
  rotation.
- **Three renames resolved** that a URL join could not see — `byterover-cli`,
  `tencentdb-agent-memory` and `mempalace` — each
  [recorded in its report](../content/systems/byterover.md) so the next join
  does not re-report it.
- **One DIVE-tier system confirmed gone** from GitHub.
- **The corpus's methodological claim corroborated**, and the probe that
  corroborated it caught out three times as often as it hit.
- **One question from the issue is still open.** The submitter asked which
  single system they should point a local-first setup at rather than maintaining
  their own. Answering that honestly needs the shortlist read, and the answer
  will go in [the verdicts page](../content/verdicts.md) rather than here.

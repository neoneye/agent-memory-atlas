# A tokenomics list, triaged — 73 open-source projects read against the memory bar

**Status:** in progress. Batches of five, committed as they close.
**Origin:** [QuesmaOrg/awesome-ai-tokenomics](https://github.com/QuesmaOrg/awesome-ai-tokenomics),
a curated list of tools, papers and configs about what tokens cost and where
they are wasted. Suggested 2026-08-09 with the observation that minimising token
usage is adjacent to
[cache-preserving injection](../content/patterns/cache-preserving-injection.md).
Closed-source entries are out by instruction.

## Why a cost list is worth reading for a memory atlas

The two subjects touch at exactly one seam, and the pattern page already names
it: **where you inject memory constrains what your memory system is allowed to
be.** A recall block placed in the system prompt invalidates the provider's
prefix cache on every turn, and the only signal is the bill. That page says in
its own last line that no system in this atlas publishes a cache hit rate. A
list assembled by people who measure bills is therefore a plausible place to
find the measurement, and a poor place to find memory systems.

Both halves of that expectation are being tested rather than assumed.

## The join

The list's README carries 84 distinct GitHub project URLs, excluding the badge
service and the two harness release links. Removing the four sibling
awesome-lists in its *Related lists* section leaves 80. Joining `source_url`
across `content/systems/*.md` finds **seven already reported**:

| Already in the atlas | Report |
| --- | --- |
| `getzep/graphiti` | [Graphiti](../content/systems/graphiti.md) |
| `langchain-ai/langmem` | [LangMem](../content/systems/langmem.md) |
| `letta-ai/letta` | [Letta](../content/systems/letta.md) |
| `mem0ai/mem0` | [Mem0](../content/systems/mem0.md) |
| `supermemoryai/supermemory` | [Supermemory](../content/systems/supermemory.md) |
| `thedotmack/claude-mem` | [claude-mem](../content/systems/claude-mem.md) |
| `topoteretes/cognee` | [Cognee](../content/systems/cognee.md) |

That leaves **73 to read**. Two of the list's non-GitHub entries resolve to
repositories the atlas already covers by another route — its *OpenCode* entry
links to `opencode.ai/docs`, reported here from
[`anomalyco/opencode`](../content/systems/opencode.md) — and are not counted
again.

## Method, and its one shortcut

Every candidate is shallow-cloned with `--no-checkout --recurse-submodules=no`,
screened with `scripts/screen_repo.py`, and probed for memory vocabulary in
source rather than in prose. Nothing is installed and nothing is run.

The shortcut is worth stating because it disables one of the screen's checks.
`--depth 1` gives every file the clone date, so the lockfile-age bound the screen
derives from git history reports `FRESH` for the whole tree regardless of the
truth. That is harmless *here* and only here: the posture is read-only for the
entire pass, which is the screening skill's own second remedy for a `FRESH`
finding. Any candidate that goes on to a report is re-cloned with full history so
the bound is real.

`direnv` is not installed on this machine, checked rather than assumed, which
takes `.envrc` off the auto-run list for this pass.

## The ledger

### Batch 1 — the usage meters

Eight of the list's thirteen *Dashboards* entries are open-source local meters
that read a coding agent's own log files. They are the largest single category in
the corpus and the least likely to be memory, so they went first.

| Repository | Commit | Outcome |
| --- | --- | --- |
| `ccusage/ccusage` | `a6ea4443` | Out of scope: reads local agent JSONL logs and prices them. No memory vocabulary anywhere in the Rust or TypeScript sources |
| `Maciek-roboblog/Claude-Code-Usage-Monitor` | `c59a83bf` | Out of scope: a burn-rate terminal dashboard. Both vocabulary hits are in `README.md` and `CONTRIBUTING.md` |
| `phuryn/claude-usage` | `3eea1544` | Out of scope: a local usage dashboard. Its "remembers the last port in `workspaceState`" is editor UI state, not agent memory |
| `tddworks/ClaudeBar` | `da849adf` | Out of scope: a menu-bar quota monitor. Also carries **no licence file** despite the README's MIT claim, which is what the list's own badge says |
| `getagentseal/codeburn` | `3536a1d3` | Out of scope: a waste tracker whose one hit, `src/providers/copilot.ts:753`, is a comment about carrying a timestamp forward inside one parse |

Five declines, no near-misses. What a meter stores is a record *about* the
session for a human to read afterwards; nothing in any of the five is retrieved
back into a model's context, which is the bar
[`content/overview.md`](../content/overview.md) sets and the reason the category
was expected to be empty.

The screen found three auto-run surfaces across the five — all in `ccusage`,
which ships `.claude/settings.json` hooks, an `.envrc` and a `.mcp.json`. Nothing
was executed.

### Batch 2 — the rest of the meters, and the one that was not a meter

| Repository | Commit | Outcome |
| --- | --- | --- |
| `douglasmonsky/codex-usage-tracker` | `bc190476` | Out of scope: a SQLite index over Codex CLI logs. No memory vocabulary in source at all |
| `steipete/CodexBar` | `98c7196f` | Out of scope: a macOS menu-bar meter, 2,437 files. Every vocabulary hit is a changelog line or a menu-refresh scheduler |
| `CodeZeno/Claude-Code-Usage-Monitor` | `7b108da8` | Out of scope: a 39-file Windows taskbar widget. No hits |
| `openlit/openlit` | `ad20b7b4` | Out of scope, and the batch's near-miss — see below |
| **`github/gh-aw`** | `c9dca3e2` | **Report written** — [gh-aw](../content/systems/gh-aw.md), the atlas's 239th |

**openlit is the near-miss worth naming**, because it does everything a memory
system does except the last step.
`cli/internal/coding/sessionstate/sessionstate.go` opens with *"persists tiny
per-session facts that the CLI needs to remember across hook invocations"*, and it
is a real durable store: JSON under `$XDG_CACHE_HOME/openlit/sessions/<sid>.json`,
written `0600`, bounded in size, best-effort on corruption. It survives a process
boundary because each hook invocation is a fresh process. It does not survive the
*session*, and what it holds — a cached `user_email`, the last-seen composer mode
— is replayed as an OpenTelemetry resource attribute, never back to a model. A
store that outlives the process but not the session, feeding telemetry rather
than context, is exactly the shape the scope bar exists to exclude.

**gh-aw is the find.** GitHub's agentic-workflows compiler is on a token-cost list
because it meters inference in AI Credits and can cap a run. That is not why it
matters here. A workflow run is a session with unusually hard edges — fresh
container, no filesystem, nothing carried forward — and `gh-aw` gives it three
ways to remember anyway: the Actions cache, an orphan git branch, and a managed
issue comment, all materialised as ordinary files the agent edits with the tools
it already has.

Two mechanisms justified the report.

The first is an **information-flow lattice over memory**. The cache-memory store is
a git repository with one branch per integrity level — `merged`, `approved`,
`unapproved`, `none` — and the pre-agent script checks out the branch for this
run's level, then merges down from strictly higher levels only: *"lower-integrity
runs see higher-integrity data via merge, but higher-integrity runs never see
lower-integrity data."* A fork PR reads what a merged run remembered and cannot
write into it. Nothing else in the atlas has a directional scope.

The second is that **the restore path treats the store as hostile**. Before the
agent sees the tree: hook files under `.git/hooks` deleted, `core.hooksPath` set
to `/dev/null`, every symlink deleted, execute bits stripped from every file, and
files with disallowed extensions removed. ADR-26587 states the reasoning — a
compromised prior run could have planted an executable. This project screens other
people's repositories for exactly that shape before reading them; `gh-aw` screens
its own memory before reading it, which is the same argument applied one level in.

The mark is `scope_enforced` and only that. `trust_state` was considered and
withheld: the four levels label the run that wrote a file, never the claim inside
it, and no file ever moves between levels, so there is no state a belief can be
promoted or demoted through. `audit_log` was considered and withheld under the
atlas's own rule that git history is a different mechanism — though here the
history is unusually pointed, one commit per run named `run-<GITHUB_RUN_ID>` on
the branch of that run's trust level.

Ten entries read, one report, and the cost-list hypothesis is holding in the
direction that predicted few memory systems. The other half — that a list written
by people who measure bills would contain the cache measurement
[cache-preserving injection](../content/patterns/cache-preserving-injection.md)
says nobody publishes — has produced nothing yet. `gh-aw` sidesteps the pattern
rather than answering it: there is no per-turn injection to invalidate, because
the store is a directory and the agent goes looking.

### Batch 3 — observability, and a spec that turned out to matter

| Repository | Commit | Outcome |
| --- | --- | --- |
| `robinebers/openusage` | `9d2bf09f` | Out of scope: a Swift menu-bar meter. Hits are `PopoverTransparencyStore` and a panel-height controller |
| `mm7894215/TokenTracker` | `f3da4c50` | Out of scope: a local token dashboard with a desktop pet. Two hits, one README, one `DynamicIslandController.swift` |
| `eunomia-bpf/agentsight` | `07a83a32` | Out of scope: eBPF kernel-boundary observation of an agent. Hits are profiling docs |
| `traceloop/openllmetry` | `c2f3f45e` | Out of scope: OpenTelemetry SDKs for LLM apps. `test_context_token_lifecycle.py` is about OTel context tokens |
| `open-telemetry/semantic-conventions-genai` | `46d43c89` | Out of scope as a system — **and the pass's most useful non-report** |

The OpenTelemetry GenAI conventions store nothing, so they fail the bar and get
no report. They are still the most interesting thing in three batches, because
they are the only **vendor-neutral** answer in the field to the question the
[pluggable memory provider](../content/patterns/pluggable-memory-provider.md)
page has been asking one host at a time: what operations does memory have?

`model/gen-ai/registry.yaml` puts seven of them in the `gen_ai.operation.name`
enum — `create_memory`, `search_memory`, `update_memory`, `upsert_memory`,
`delete_memory`, `create_memory_store`, `delete_memory_store` — plus
`gen_ai.memory.store.id`, `gen_ai.memory.record.id`,
`gen_ai.memory.record.count`, `gen_ai.memory.query.text` and a
`gen_ai.memory.records` payload with a JSON schema.

Two readings, both now on the pattern page.

The vocabulary **names deletion at both granularities**, records and store, where
exactly one of the ten host contracts the atlas has read declares targeted
deletion at all. And it **declares no scope whatsoever** — no tenant, user,
project or agent attribute on a memory operation, only a store id whose meaning
each component is told to document for itself.

The record schema is the sharp end. A `MemoryRecord` is `content` (the only
required field), `id`, `score`, and an opaque `metadata` object. Validity time,
trust state, provenance and supersession — three whole pattern pages here — all
land in `metadata`, where they are by construction not comparable between
implementations. For a development-stage spec that is a reasonable place to
start. It is also a precise statement of what the field currently agrees a memory
*is*: a scored string with an id.

Fifteen entries read, one report, one pattern page changed.

### Batch 4 — tracing, and the boundary the atlas had not drawn

| Repository | Commit | Outcome |
| --- | --- | --- |
| `Arize-ai/phoenix` | `b4d9b19e` | Out of scope: LLM tracing, 7,068 files. One vocabulary hit, `"Typed in-memory store for system_settings"` |
| `liaohch3/claude-tap` | `bf1a37b7` | Out of scope: a local trace viewer intercepting agent API traffic. No hits |
| `comet-ml/opik` | `a911602e` | Out of scope: an observability platform, 11,978 files. No hits |
| `zilliztech/GPTCache` | `c59fb3a6` | Out of scope — **and the reason the overview now has a third scope boundary** |
| `GuglielmoCerri/khazad` | `da10e6fc` | Out of scope, same boundary, second half of the argument |

A semantic cache passes a naive reading of the inclusion bar. It stores question
and answer durably, retrieves by embedding similarity across sessions, and
evicts. Three declines by category would have been the lazy call, so both were
read.

GPTCache settles itself in one function. `gptcache/processor/check_hit.py` is the
default hit check and its whole body is
`return cur_session_id not in cache_session_ids` — a cached answer is **withheld
from the session that produced it** and served to every other session. That is
the exact inverse of memory, and it is correct for a cache: asking the same
question twice in one conversation usually means the first answer was no good.

khazad supplies the other half. It has a `CacheScope` enum, so a reader grepping
for a scope key finds one — and its two values are `MODEL` and `HOST`, keeping a
`gpt-4o` answer from being served to a `gpt-4o-mini` call. No user, tenant or
session dimension exists. A cache's scope stops an answer being served where it
would be *wrong*; a memory's scope stops it being served to someone who should
not *see* it. khazad intercepts HTTP with no application change, which is the
selling point and also the reason it cannot know who is asking.

Both are now written up in `content/overview.md` as **Not in scope: the semantic
response cache**, beside the KV cache and the chat buffer. The rule from the
KV-cache section carries over with an amendment: a cache is still an optimisation
whose *loss* costs latency, but a semantic cache's *hit* can be wrong, which is
why the serious ones grow a verification step — a cost-control problem, not a
memory one.

Twenty entries read, one report, one pattern page and one scope boundary.

### Batch 5 — the caches, the engines, and two reports

| Repository | Commit | Outcome |
| --- | --- | --- |
| `LMCache/LMCache` | `9fc6e1af` | Out of scope: a KV-cache layer beneath vLLM — the boundary `content/overview.md` already draws |
| `messkan/prompt-cache` | `dd6c41fc` | Out of scope: a Go proxy with a three-tier semantic cache. No memory vocabulary in source at all |
| `ggml-org/llama.cpp` | `74ce1574` | Out of scope: an inference engine. Every hit is UI state, multimodal or speculative decoding |
| **`ollama/ollama`** | `acdf8151` | **Report written** — [Ollama](../content/systems/ollama.md) |
| **`mksglu/context-mode`** | `ff5f911d` | **Report written** — [Context Mode](../content/systems/context-mode.md) |

Both reports came out of a probe hit that the entry text gave no reason to expect,
which is the argument for probing source rather than reading descriptions.

**Ollama's entry on the list is about local inference.** Its `agent/` package is a
session loop, a tool registry, an approval gate, a compactor and a skill catalog,
and the catalog is durable cross-session state. Two mechanisms earned the report.
`SkillCatalog.SystemContext()` puts one name-and-description line per skill in the
prompt and loads the body only on demand — the
[cache-preserving injection](../content/patterns/cache-preserving-injection.md)
page now carries this as a third shape, *index in the prefix, body after it*,
reached from a token argument rather than a caching one. And
`agent/tools/skill.go` requires approval for a model-initiated load because *"a
skill's instructions can influence the rest of the run"*, while explicit user
activation bypasses it. Gating recall rather than the write is the right way round
when the memory is instructions, and almost nothing else in the atlas does it.

No capability marks. Nothing the agent learns survives a run — approvals live on
the session struct, compaction writes nothing to disk, and no tool can create or
edit a skill.

**Context Mode's entry is about a 98% cut in tool-output tokens.** Underneath, hooks
in seventeen harnesses write typed events into a per-project SQLite database, and
the next session opens with a `<session_knowledge>` block built from them. It
carries `scope_enforced` and `negative_eval`, and both come from the same bug:
six `SessionStart` adapters were calling `getLatestSessionEvents(db)`, which
returns whichever session started most recently regardless of project, so a second
worktree leaked into a resumed session. `tests/session/cross-session-bleed.test.ts`
pins the *function's* contract rather than the six callers', in the negative, with
the reasoning in its header: *"If either contract regresses, all 6 SessionStart
adapters silently leak again. These tests fail loudly instead."*

Its other move belongs on the scope page beside CSM. `buildCtxSearchSchema`
spreads the cross-project `project` field into the `ctx_search` schema only in
shared-database mode; in the default layout the field does not exist, which the
comment defends as *"a stronger guarantee than runtime"* validation.

Twenty-five entries read, three reports, four pattern pages changed and one scope
boundary drawn. The cost-list hypothesis has now failed in the direction it was
expected to hold — the memory systems are here, they are just filed under
inference and token savings.

### Batch 6 — compression, and the page the hint was pointing at

| Repository | Commit | Outcome |
| --- | --- | --- |
| `headroomlabs-ai/headroom` | `675d13f0` | Out of scope: a dereference table, not a memory — but named on the pattern page |
| `microsoft/LLMLingua` | `e0e9d99b` | Out of scope: prompt compression with a small model. No memory vocabulary at all; no commit since 28 October 2025 |
| `fkiene/llmtrim` | `d7fd2c4e` | Out of scope as a system — **and the best outside evidence this pass has found** |
| `rtk-ai/rtk` | `9936b2b9` | Out of scope: `src/core/tracking.rs` is a 90-day SQLite ledger of token savings for a human to read |
| `toon-format/toon` | `f06ddca1` | Out of scope: a serialization format. No persistence of any kind |

The suggestion that came with this list said minimising token usage is adjacent to
[cache-preserving injection](../content/patterns/cache-preserving-injection.md).
`llmtrim/crates/llmtrim-core/src/memo.rs` is where that adjacency turns out to be
literal.

llmtrim is a compression proxy and gets no report: its memo store is in-process
only, size-capped, and its own SECURITY.md commits to never writing prompt text to
disk. Nothing survives the session. But the module is 100 lines of documentation
before the first `use`, and it states the pattern page's failure mode from the
inside — its stages read the whole conversation, so *"the compressed form of an
old message can change when a new turn arrives … the provider cache is busted →
the product's headline savings leak silently on exactly the highest-traffic
(agent) shape."* A compression product discovering that compression breaks the
cache is the sharpest version of that argument available.

It also supplies a number the page could not: 85–95% of an agentic request's
prompt tokens are unchanged turn-to-turn, cited to a 2026 measurement. And its fix
is the split-by-position shape applied to conversation history — a cumulative
128-bit hash chain over *original* message bytes, longest all-present run is the
frozen prefix, its slots overwritten with last turn's emitted bytes, first-write
wins so a freeze never re-mutates.

Two habits from it are now on the page. The memo is *"an optimization, never a
correctness dependency"* and falls back to full recomputation on any doubt. And it
disables reuse entirely whenever the n-gram stage is on, because that stage's
placeholders are assigned from whole-conversation frequencies and splicing an old
turn's `§1` into a new turn's legend would corrupt it — a cache that knows which
of its own components it may not apply to.

headroom is on the same page for the other half. Its CCR layer — Compress, Cache,
Retrieve — stashes a dropped payload in SQLite keyed by the hash that goes into
the prompt and honours a retrieval tool call that trades the hash back for the
original: *"lossy on the wire, lossless end-to-end."* That is a dereference table
rather than a memory, so no report; the shape is the same one Ollama reaches with
a name instead of a hash, and it is what a memory system does when a recalled item
is too large to inject.

Thirty entries read. Three reports, five pattern pages changed, one scope
boundary.

### Batch 7 — the packers, the gateways, and a memory graph

| Repository | Commit | Outcome |
| --- | --- | --- |
| `yamadashy/repomix` | `172b800f` | Out of scope: packs a repository into one file for a model to read. No persistence between runs |
| `NVIDIA/RULER` | `c3f5e3b4` | Out of scope: a 31-file long-context benchmark |
| **`oraios/serena`** | `946ad981` | **Report written** — [Serena](../content/systems/serena.md) |
| `maximhq/bifrost` | `4c208bbf` | Out of scope: an AI gateway, 4,156 files. No memory vocabulary in source |
| `BerriAI/litellm` | `f6b9518d` | Out of scope: a gateway with per-request cost accounting, 9,404 files. One hit, a dashboard page-metadata file |

Serena is on the list for its LSP-backed code retrieval. `src/serena/memories/` is
1,218 lines that nothing in the entry mentions, and it implements a shape the
atlas mostly does not have: **memory as a graph of documents that cite each
other, with a checker for the citations.**

A memory body cites another as `` `mem:name` ``. Three mechanisms follow.
`rename_memory_and_propagate_references` moves the file and rewrites every
reference to it across the store, anchored on both sides so `mem:auth` cannot
match inside `mem:auth_tokens`, skipping files that do not mention it so their
mtimes stay put. `validate_referential_integrity` reports **stale references** —
links pointing at nothing, each with up to three ranked replacement candidates —
and the inverse, **unmarked references**: a bare memory name in prose that should
have been a link, graded high or low confidence by whether the name is unlikely to
be ordinary English. `serena memories check` runs it.

The similarity scoring is the part that reads as tuned rather than guessed:
version suffixes stripped before comparison, a 0.34 basename-Jaccard floor so
`frontend/x-subtleties` does not match `backend/y-subtleties` on a shared trailing
word, a 0.6 fuzzy floor so the prose word "repository" does not match
`serena_repository_structure`, and `core` on a hard-coded ignore list because it is
also an English word. Each threshold has a test named after the false positive it
prevents.

And the shipped `memory_maintenance.md` inverts how relevance is usually
modelled: *"Memories themselves should not contain information about when to read
them; this is the responsibility of the referring memory."* Relevance is an edge
property. `mem:core` is the declared root and the agent discovers the rest by
following links from it.

The gap is the other direction. Nothing performs a reachability pass, so a memory
that nothing links to is unreachable under the declared traversal model and no
report mentions it — which is exactly the check
[breadcrumbs](../content/systems/breadcrumbs.md) does run, and the only half *it*
has. Two systems, opposite ends of the same graph problem, neither aware of the
other. That is a pattern page waiting to be written and it is recorded here as a
proposal rather than written now, because it wants both halves stated together
and a third instance would make it stronger.

Thirty-five entries read, four reports.

### Batch 8 — a recipe, a repository already covered, and a closed CLI

| Repository | Commit | Outcome |
| --- | --- | --- |
| **`lucasrosati/claude-code-memory-setup`** | `c5f2e0b5` | **Report written** — [claude-code-memory-setup](../content/systems/claude-code-memory-setup.md) |
| `getzep/zep` | `ba4fc3cc` | Out of scope: already dispositioned. The engine is [Graphiti](../content/systems/graphiti.md); this tree is examples, integrations, ingestion, benchmarks and a `legacy` directory |
| `oanhduong/token-ninja` | `79897edf` | Out of scope: one `UserPromptSubmit` hook that runs deterministic commands locally instead of letting the model call them. Nothing is stored |
| `google-antigravity/antigravity-cli` | `1d853acd` | **Ignored by instruction**: 15 files, a `CHANGELOG.md`, a demo GIF and examples, with no licence file. The CLI itself is closed source, which the list's own *Market Competitors* entry says outright |
| `musistudio/claude-code-router` | `47f36494` | Out of scope: a routing gateway. Its own list entry warns that routing scripts run as fully trusted code beside your credentials |

The `getzep/zep` disposition is a repeat, and worth naming as one: the same
repository was dispositioned the same way in
[the seventy-one-repository pass](2026-08-09-seventy-one-repositories-from-an-outside-corpus.md),
which is what a second corpus overlapping the first looks like.

**claude-code-memory-setup is a recipe and gets a report anyway**, because the
importer is a real capture path and because of what it does at the end of it.
`insert_wikilinks` gathers every note name in the Obsidian vault, drops names
under four characters, sorts longest-first so a longer name beats a shorter one it
contains, splits the body on code fences with a capturing regex so code survives
untouched, and links the **first occurrence only** of each name behind a guard
that refuses to re-wrap an existing `[[link]]`. A new note joins the graph and
nobody curated it.

Read against [Serena](../content/systems/serena.md) from the batch before, this is
the same problem with the opposite risk posture. Serena detects a bare name that
should be a link and *warns*, graded by confidence, behind a similarity threshold
with a test on each side and an ignore list for words that are also English.
This *rewrites*, silently, into the note body, with a length floor as the only
guard — four characters removes `api` and keeps `test`, `error` and `database` —
and deletes the original export if `--move` was passed. Two independent arrivals
at wikilink-style memory, one cautious and one not, is the third data point the
pattern proposal from batch 7 was waiting for.

Its README leads with *"71.5x fewer tokens per session"*. Nothing in the
repository produces, measures or records that; the token argument belongs to
Graphify — which the atlas already reports — and to not re-reading files.

Forty entries read, five reports.

### Batch 9 — the routers, and two memory systems hiding in them

| Repository | Commit | Outcome |
| --- | --- | --- |
| `mihneaptu/opencode-fusion` | `4c314488` | Out of scope: a 56-file OpenCode config layer that removes tools from the main agent's schema. Nothing stored |
| `katanemo/plano` | `bd711e03` | Out of scope: an Envoy-based router. One vocabulary hit, in `cli/planoai/trace_cmd.py` |
| `lm-sys/RouteLLM` | `0b64fdaf` | Out of scope: a trained cost-threshold router. No commit since 9 August 2024 |
| **`ruvnet/ruflo`** | `913f9eae` | **Report written** — [ruflo](../content/systems/ruflo.md) |
| **`vllm-project/semantic-router`** | `6ae15901` | **Report written** — [vLLM Semantic Router](../content/systems/vllm-semantic-router.md) |

Two of five. The category the list files these under — *Routing / model selection*
— turned out to contain more memory code than the *Memory* section did.

**vLLM Semantic Router** has 10,777 lines of Go under
`src/semantic-router/pkg/memory/` that its list entry never hints at: `MemoryType`
as an actual column (`semantic | procedural | episodic`), four storage backends
behind one `Store` interface, and — rare enough to be worth the report on its own
— `Forget(id)` **and** `ForgetByScope(user, project, types)` declared in that
interface.

Two of its test files are better than its code. `test_isolation.py` opens *"User
memory isolation (security) tests"* and checks one user's secret against another
at the storage layer *and* through the live retrieval path; every retrieval
assertion in the suite runs in a **new session with no `previous_response_id`**,
so a pass cannot be explained by conversation history. And
`MemoryContradictionTest` stores two contradicting facts and asserts both survive,
above a docstring saying the router does soft-insert today and that the test is a
baseline for when contradiction detection arrives, citing three papers. A
characterisation test for a mechanism you have not built is the best record of a
known gap this pass has found.

Its injection is the near-miss. `injectMemoryMessages` deliberately avoids the
system prompt — *"following the openai-agents-python pattern where context is
injected as conversation items"* — and then inserts at the index right after the
last system message, in front of the whole conversation. The system prompt
survives; every message after the block does not. Appending to the current user
turn would cost nothing and keep the history cached.

**ruflo** ships 24,166 lines of memory inside a 5,491-file swarm harness, and one
file justified the report. `agentdb-retrieval-guard.ts` screens retrieved chunks
for injection before assembly, wrapping the harness's existing tool-output
guardrail rather than writing a second pattern library, and names the attack with
a citation: SMSR (arXiv:2606.12703), 93–100% undefended success against 0% behind
a certified guard. It **refuses to truncate** an oversized chunk because
*"truncation would let an attacker pad a payload past the guardrail's own scan
window"* — the second-order failure most size gates walk into.

And it is **off** unless an environment variable turns it on, then annotate-only
unless a second one makes it drop. Three states, safest least likely. The file
says so plainly, which is better than a security document that does not.

No marks for ruflo. Its three-scope directory layout is placement rather than a
filter, and no committed test in the memory package asserts that one agent's
namespace cannot surface in another's results — so the scope mark is withheld and
the reason is in the report.

Forty-five entries read, seven reports.

### Batch 10 — five declines, no near-misses

| Repository | Commit | Outcome |
| --- | --- | --- |
| `workweave/router` | `807931b3` | Out of scope: an on-box embedding cluster scorer picking a model per request. ELv2. No memory vocabulary in source |
| `firecrawl/firecrawl` | `448ef4bf` | Out of scope: a scraping API that converts pages to markdown before they reach a model |
| `valyuAI/valyu-benchmarks` | `104ad746` | Out of scope: a 70-file benchmark harness with raw outputs, and **no licence file** |
| `sgl-project/sglang` | `bfeb9a8a` | Out of scope: a serving framework. The one vocabulary hit is a quantization kernel |
| `vllm-project/vllm` | `83ad767e` | Out of scope: the serving engine. Its one hit is a KV-transfer worker, which is the boundary `content/overview.md` draws |

The first batch with nothing to say. Recorded rather than skipped because a triage
note that only lists the interesting batches is not a ledger.


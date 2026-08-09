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


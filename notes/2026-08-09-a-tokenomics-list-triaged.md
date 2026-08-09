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

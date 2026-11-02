# Plugin hooks the screen missed

**Status:** ledger re-screened 2026-11-02. Report bodies and appendix entries are not edited yet; each re-read should add the surfaces below to its screen summary.

## What happened

`scripts/screen_repo.py` looked for `hooks/hooks.json` and `.claude-plugin/` at the checkout root only. A plugin shipped in a subdirectory behind a marketplace entry therefore screened as one auto-run surface, the marketplace manifest, while its own `hooks.json` registered hooks that run on session start or after every tool call. Understand-Anything was the case that showed it: two hooks that tell the agent to act without asking the user, recorded as nothing.

The screen now follows each local marketplace `source`, and every nested `.claude-plugin/plugin.json` up to four levels down outside `node_modules` and vendored trees. For each plugin it reports the manifest, its `hooks/` directory and `hooks.json`, a hooks file the manifest names or hooks it declares inline, and MCP servers in `.mcp.json` or the manifest. `screen_repo.py --self-test` holds six controls and runs in `scripts/test_site.sh`.

## The re-screen

Every ledger record with a root `.claude-plugin/` and no root `hooks/hooks.json` was screened again at its pinned revision with `scripts/screen_corpus.py --only`: 100 records, plus Understand-Anything earlier the same day. 86 gained auto-run surfaces and 14 did not. `light-mem` could not be cloned, because the upstream returns 404, and keeps its previous record.

66 reports gained hook registrations, listed first. The events column lists the hook events the file names; a dash means the screen matched none of its trigger words in it. A row marked *fetched* starts an MCP server through `npx`, `uvx` or a similar launcher, so what runs is whatever the registry serves that day.

The records also lost 464 FRESH findings. A FRESH finding is relative to the day of screening, and those dependency files have since aged out of the seven-day window. The original findings are in the git history of `notes/screening/screening.json` and in each report's History entry.

## Reports with plugin hooks

| Report | Hook files | Events | Plugin MCP |
| --- | --- | --- | --- |
| [acontext](../content/systems/acontext.md) | `src/packages/claude-code/plugin/hooks/hooks.json` | PostToolUse, SessionStart, Stop | `src/packages/claude-code/plugin/.mcp.json` |
| [agent-working-memory](../content/systems/agent-working-memory.md) | `plugin/hooks/hooks.json` | PostToolUse, Stop, UserPromptSubmit | — |
| [agentmemory](../content/systems/agentmemory.md) | `plugin/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | `plugin/.mcp.json` (fetched) |
| [ai-memory](../content/systems/ai-memory.md) | `plugins/claude-code/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | `plugins/claude-code/.mcp.json` |
| [aidememo](../content/systems/aidememo.md) | `plugins/claude/hooks/hooks.json` | PostToolUse, SessionStart, UserPromptSubmit | `plugins/claude/.mcp.json` |
| [aigent-os](../content/systems/aigent-os.md) | `plugins/fleet-band/hooks/hooks.json`<br>`plugins/fleet-delivery/hooks/hooks.json` | — | — |
| [akb](../content/systems/akb.md) | `plugins/claude/akb-claude-code/hooks/hooks.json` | SessionStart, UserPromptSubmit | `.codex/config.toml`<br>`plugins/claude/akb-wiki/.mcp.json` (fetched) |
| [attune-ai](../content/systems/attune-ai.md) | `plugin/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | `plugin/.mcp.json`<br>`plugins/attune-help/.mcp.json` (fetched) |
| [basic-memory](../content/systems/basic-memory.md) | `plugins/claude-code/hooks/hooks.json` | SessionStart | — |
| [beads](../content/systems/beads.md) | `plugins/beads/.claude-plugin/plugin.json` | SessionStart | — |
| [claude-mem](../content/systems/claude-mem.md) | `cowork/hooks/hooks.json`<br>`plugin/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | `plugin/.mcp.json` |
| [claudest](../content/systems/claudest.md) | `plugins/claude-memory/hooks/hooks.json` | SessionStart, Stop | — |
| [codemem](../content/systems/codemem.md) | `plugins/claude/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | `opencode.jsonc` (fetched) |
| [cognicore](../content/systems/cognicore.md) | `cognicore-experience/hooks/hooks.json` | PostToolUse, SessionStart | `claude-plugin/.mcp.json`<br>`cognicore-experience/.mcp.json` |
| [core-redplanet](../content/systems/core-redplanet.md) | `plugin/hooks/hooks.json` | SessionStart, Stop | `plugin/.mcp.json` |
| [cortex-hypermnesia](../content/systems/cortex-hypermnesia.md) | `.claude-plugin/plugin.json`<br>`plugins/cortex-deprecated/hooks/hooks.json`<br>`plugins/cortex-viz-deprecated/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, UserPromptSubmit | — |
| [cortexdb](../content/systems/cortexdb.md) | `plugins/cortexdb/hooks/hooks.json` | SessionStart, UserPromptSubmit | `plugins/cortexdb/.mcp.json` |
| [ctx](../content/systems/ctx.md) | `internal/assets/claude/hooks/hooks.json` | PostToolUse, PreToolUse, UserPromptSubmit | `internal/assets/claude/.mcp.json` |
| [deja-vu](../content/systems/deja-vu.md) | `claude-plugin/.claude-plugin/plugin.json` | PostToolUse, PreToolUse, SessionStart, UserPromptSubmit | — |
| [demarkus](../content/systems/demarkus.md) | `plugins/claude-code-knowledge/.claude-plugin/plugin.json`<br>`plugins/claude-code/.claude-plugin/plugin.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | `plugins/claude-code/.mcp.json`<br>`plugins/cowork-memory/.mcp.json` |
| [engram](../content/systems/engram.md) | `plugin/claude-code/hooks/hooks.json` | SessionStart, Stop, UserPromptSubmit | — |
| [engram-alpha](../content/systems/engram-alpha.md) | `claude-plugin/hooks/hooks.json` | PostToolUse, SessionStart | `claude-plugin/.mcp.json` |
| [exomem](../content/systems/exomem.md) | `plugins/claude-code/hooks/hooks.json` | SessionStart, Stop, UserPromptSubmit | `plugins/hosted/generated/claude/.mcp.json` |
| [graft](../content/systems/graft.md) | `plugins/graft/hooks/hooks.json` | SessionStart, UserPromptSubmit | — |
| [graqle](../content/systems/graqle.md) | `plugins/claude-code/graqle/hooks/hooks.json` | PreToolUse | — |
| [headroom](../content/systems/headroom.md) | `plugins/headroom-agent-hooks/hooks/hooks.json` | PreToolUse, SessionStart | — |
| [hindsight](../content/systems/hindsight.md) | `hindsight-integrations/claude-code/hooks/hooks.json`<br>`hindsight-integrations/zcode/hooks/hooks.json` | SessionStart, Stop, UserPromptSubmit | `hindsight-integrations/claude-code/.mcp.json` |
| [hivemind-activeloop](../content/systems/hivemind-activeloop.md) | `harnesses/claude-code/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | — |
| [iai-pme](../content/systems/iai-pme.md) | `plugin/hooks/hooks.json` | SessionStart, Stop, UserPromptSubmit | `plugin/.mcp.json`<br>`plugin/hooks/` |
| [inite-brain](../content/systems/inite-brain.md) | `plugins/inite-brain/hooks/hooks.json` | SessionStart | `plugins/inite-brain/.mcp.json` |
| [kage](../content/systems/kage.md) | `plugin/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | `plugin/.mcp.json` (fetched) |
| [kagura-memory-cloud](../content/systems/kagura-memory-cloud.md) | `claude-hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart | — |
| [kipi-system](../content/systems/kipi-system.md) | `plugins/kipi-core/hooks/hooks.json`<br>`plugins/kipi-design/hooks/hooks.json`<br>`plugins/kipi-dsse/hooks/hooks.json`<br>`plugins/prd-os/hooks/hooks.json` | PostToolUse, PreToolUse, Stop | `.codex/config.toml`<br>`plugins/kipi-core/.mcp.json`<br>`plugins/kipi-notebooklm/.mcp.json` (fetched) |
| [leteo](../content/systems/leteo.md) | `plugin/claude-code/hooks/hooks.json`<br>`plugin/zcode/hooks/hooks.json` | SessionStart, Stop, UserPromptSubmit | `plugin/claude-code/.mcp.json`<br>`plugin/zcode/.mcp.json` |
| [linggen-memory](../content/systems/linggen-memory.md) | `plugins/linggen/hooks/hooks.json` | PreToolUse, SessionStart, UserPromptSubmit | `plugins/linggen/.mcp.json`<br>`plugins/linggen/hooks/` |
| [lorekit](../content/systems/lorekit.md) | `plugins/lorekit-claude/hooks/hooks.json` | PostToolUse, SessionStart, Stop, UserPromptSubmit | — (fetched) |
| [mama](../content/systems/mama.md) | `packages/claude-code-plugin/.claude-plugin/plugin.json` | PostToolUse, PreToolUse, SessionStart | `packages/claude-code-plugin/.mcp.json` (fetched) |
| [mcp-memory-service](../content/systems/mcp-memory-service.md) | `claude-hooks/.claude-plugin/hooks.json` | SessionStart, Stop, UserPromptSubmit | `claude-hooks/.mcp.json` |
| [mem0](../content/systems/mem0.md) | `integrations/claude-code-plugin/hooks/hooks.json` | PostToolUse, SessionStart, Stop, UserPromptSubmit | `integrations/claude-code-plugin/.mcp.json` |
| [mem9](../content/systems/mem9.md) | `claude-plugin/hooks/hooks.json` | SessionStart, Stop, UserPromptSubmit | — |
| [memini](../content/systems/memini.md) | `plugin/hooks/hooks.claude.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | `plugin/.mcp.json` |
| [memoir](../content/systems/memoir.md) | `plugins/claude-code/hooks/hooks.json` | SessionStart, Stop, UserPromptSubmit | — |
| [memoose](../content/systems/memoose.md) | `harness/hooks/hooks.json` | PostToolUse, SessionStart, Stop, UserPromptSubmit | `.claude-plugin/plugin.json` (fetched) |
| [memora](../content/systems/memora.md) | `claude-plugin/hooks/hooks.json` | PostToolUse, SessionStart | `claude-plugin/.mcp.json` |
| [memory-engine](../content/systems/memory-engine.md) | `packages/claude-plugin/hooks/hooks.json` | SessionStart, Stop | `packages/claude-plugin/.mcp.json` |
| [mempalace](../content/systems/mempalace.md) | `.claude-plugin/hooks/hooks.json` | Stop | `.claude-plugin/.mcp.json`<br>`.claude-plugin/plugin.json` |
| [memsearch](../content/systems/memsearch.md) | `plugins/claude-code/hooks/hooks.json` | SessionStart, Stop, UserPromptSubmit | — |
| [memseek](../content/systems/memseek.md) | `integrations/claude-code/hooks/hooks.json` | SessionStart, Stop, UserPromptSubmit | `integrations/claude-code/.mcp.json` |
| [memtomem](../content/systems/memtomem.md) | `packages/memtomem-claude-automation-plugin/hooks/hooks.json` | PostToolUse, SessionStart, Stop, UserPromptSubmit | `packages/memtomem-claude-plugin/.mcp.json` (fetched) |
| [mengram](../content/systems/mengram.md) | `integrations/claude-code-plugin/hooks/hooks.json` | SessionStart, Stop | `integrations/claude-code-plugin/.mcp.json` |
| [moltbrain](../content/systems/moltbrain.md) | `plugin/hooks/hooks.json` | PostToolUse, SessionStart, Stop, UserPromptSubmit | — |
| [mushroomdb](../content/systems/mushroomdb.md) | `packaging/plugin/hooks/hooks.json` | SessionStart, UserPromptSubmit | `packaging/plugin/.mcp.json` (fetched) |
| [omniclaude](../content/systems/omniclaude.md) | `plugins/onex/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | — |
| [openviking](../content/systems/openviking.md) | `examples/claude-code-memory-plugin/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | `examples/claude-code-memory-plugin/.mcp.json` |
| [ox](../content/systems/ox.md) | `claude-plugin/.claude-plugin/plugin.json`<br>`internal/pet/mod/hooks/hooks.json` | SessionStart | — |
| [pensyve](../content/systems/pensyve.md) | `integrations/claude-code/hooks/hooks.json` | PostToolUse, SessionStart, Stop, UserPromptSubmit | — |
| [re-call](../content/systems/re-call.md) | `plugin/hooks/hooks.json` | PreToolUse, SessionStart, UserPromptSubmit | — |
| [rememora](../content/systems/rememora.md) | `plugin/hooks/hooks.json` | — | — |
| [repowise](../content/systems/repowise.md) | `plugins/claude-code/hooks/hooks.json` | PostToolUse, SessionStart | `plugins/claude-code/.mcp.json` |
| [ruflo](../content/systems/ruflo.md) | `plugin/hooks/hooks.json`<br>`plugins/ruflo-core/hooks/hooks.json`<br>`plugins/ruflo-cost-tracker/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | `.claude-plugin/plugin.json`<br>`plugins/ruflo-core/.mcp.json` (fetched) |
| [superlocalmemory](../content/systems/superlocalmemory.md) | `codex-plugin/hooks/hooks.json`<br>`plugin/hooks/hooks.json` | PostToolUse, PreToolUse, SessionStart, Stop, UserPromptSubmit | `codex-plugin/.mcp.json`<br>`plugin/.mcp.json` |
| [temporalstore](../content/systems/temporalstore.md) | `integrations/claude-plugin/hooks/hooks.json` | PostToolUse, SessionStart, Stop, UserPromptSubmit | `integrations/claude-plugin/.mcp.json` |
| [textfold](../content/systems/textfold.md) | `plugins/textfold/hooks/hooks.json` | — | — |
| [the-librarian](../content/systems/the-librarian.md) | `integrations/claude/hooks/hooks.json` | PreToolUse, SessionStart, Stop, UserPromptSubmit | `integrations/claude/.mcp.json` |
| [tree-ring-memory](../content/systems/tree-ring-memory.md) | `plugins/tree-ring-memory/hooks/claude-hooks.json` | SessionStart, Stop | — |
| [wenlan](../content/systems/wenlan.md) | `plugin/hooks/hooks.json` | SessionStart, Stop, UserPromptSubmit | `plugin/.mcp.json` |

## Reports with plugin manifests or MCP servers only

| Report | New surfaces |
| --- | --- |
| [altk-evolve](../content/systems/altk-evolve.md) | plugin manifests only |
| [archeus](../content/systems/archeus.md) | plugin manifests only |
| [compartment](../content/systems/compartment.md) | `.claude-plugin/plugin.json` |
| [daem0n-mcp](../content/systems/daem0n-mcp.md) | `opencode.json` |
| [fernme](../content/systems/fernme.md) | `packaging/claude/plugins/fernme-docs/.mcp.json`<br>`packaging/claude/plugins/fernme-memory/.mcp.json` (fetched) |
| [gbrain](../content/systems/gbrain.md) | `.claude-plugin/plugin.json` |
| [lobu](../content/systems/lobu.md) | `claude-plugin/.mcp.json` |
| [longterm-memory-mcp](../content/systems/longterm-memory-mcp.md) | `.claude-plugin/plugin.json` |
| [matrix-os](../content/systems/matrix-os.md) | `.codex/config.toml`<br>`plugins/matrix-os/.mcp.json` |
| [no-human](../content/systems/no-human.md) | `plugins/no-human/.mcp.json` |
| [obsidian-mind](../content/systems/obsidian-mind.md) | `.gemini/settings.json` |
| [ownmem](../content/systems/ownmem.md) | plugin manifests only |
| [people-context](../content/systems/people-context.md) | `.claude-plugin/plugin.json` |
| [prism-coder](../content/systems/prism-coder.md) | `plugins/prism/.mcp.json` (fetched) |
| [qwen-mm-plugins](../content/systems/qwen-mm-plugins.md) | `src/capabilities/api/.mcp.json`<br>`src/capabilities/blender/.mcp.json`<br>`src/capabilities/core/.mcp.json`<br>`src/capabilities/example/.mcp.json`<br>`src/capabilities/freecad/.mcp.json`<br>`src/capabilities/mhs/.mcp.json`<br>`src/capabilities/omni-chatcut/.mcp.json`<br>`src/capabilities/omni-memory/.mcp.json`<br>`src/capabilities/omni-skill-creator/.mcp.json`<br>`src/capabilities/omni-video2note/.mcp.json`<br>`src/capabilities/search/.mcp.json`<br>`src/capabilities/video-edit/.mcp.json`<br>`src/capabilities/video-memory/.mcp.json`<br>`src/capabilities/video-spatio/.mcp.json` (fetched) |
| [rekal](../content/systems/rekal.md) | plugin manifests only |
| [titen](../content/systems/titen.md) | `plugins/claude/titen-memory/.mcp.json` |
| [tokenmizer](../content/systems/tokenmizer.md) | `.claude-plugin/plugin.json` |
| [verimem](../content/systems/verimem.md) | `.claude-plugin/plugin.json` |
| [vortx-emem](../content/systems/vortx-emem.md) | `plugins/emem/.mcp.json` |

# Four more, and the memory under the product

**Status:** triage. Three repositories and one paper, read on 2026-08-20 — two
excluded, two in scope with reports not yet written. Every checkout was screened
before a file was read; nothing was installed and nothing was run.
**Origin:** four links submitted together, alongside the reports for
[OpenWolf](../content/systems/openwolf.md) and
[sift-kg](../content/systems/sift-kg.md) written the same day.

---

## The shape

Two of the three repositories look like a memory system from the README and are
not; the third looks like a desktop toy and has the most complete memory of the
four. That is
[the tokenomics finding](2026-08-09-a-tokenomics-list-triaged.md) again — *an
entry describes what a project is for, and a memory system is usually not what
its host is for* — and it keeps being the reason a grep of the source beats a
reading of the pitch.

---

## outworked — `outworked/outworked` at [`89ed7b99`](https://github.com/outworked/outworked/commit/89ed7b99c91e20da4b5ece4bd0a61e255fbf0b7f)

**In scope. Report not yet written.** An Electron desktop app, v0.4.3, that runs
Claude as "a team of AI employees" in a pixel-art office — sprites, furniture,
asset packs, a cost dashboard. Screened: no auto-run surface, one build-time
lifecycle script, one unpinned surface behind a lockfile. Last commit
2026-03-31.

Underneath the office is a scoped key-value memory with a tool surface:

- `electron/db/database.js` — `memorySet(scope, key, value)` at `:318`,
  `memorySearch(scope, query, {limit = 200, offset = 0})` at `:339`,
  `memoryDelete(scope, key)` at `:366`, exported at `:1143-1147`.
- `electron/mcp/mcp-server.js:520-533` — the three exposed as **MCP tools**, so
  the model is their caller. That is the
  [tool-registry test](2026-08-14-a-coding-agent-whose-search-is-the-users-not-the-models.md)
  passed rather than failed: the human is not the only one who can query it.
- `electron/main.js:2680-2684` — the same three behind IPC handlers, so the UI
  reaches them too.

So the durable thing is a value stored under a caller-supplied scope and key,
which can be wrong, can be searched, and can be deleted by the agent that wrote
it. Three further surfaces are worth naming before a report is attempted.
`src/lib/storage.ts:153` writes a `memory:` field into a subagent's frontmatter
and `:481` reads it back, so an *agent definition* selects a memory mode.
`src/components/McpServersModal.tsx:73-76` offers
`@modelcontextprotocol/server-memory` as an installable server described as
*"Persistent key-value memory"* — a second, third-party memory the user can
switch on beside the built-in one. And `src/lib/sessions.ts:169` migrates an
agent's in-memory history into a persisted session.

What a report has to settle: whether `scope` is enforced anywhere or is just a
string the caller passes, what `memorySearch` actually matches on, and whether
the two memories — the built-in table and the optional MCP server — can both be
live at once without either knowing about the other.

## Corbell — `Corbell-AI/Corbell` at [`75c7b20a`](https://github.com/Corbell-AI/Corbell/commit/75c7b20ac95292185b5fef6a4680e3e10de9da66)

**In scope. Report not yet written.** Apache-2.0, 15,073 lines of Python, a
multi-repo architecture graph with MCP tools — `graph_query`,
`get_architecture_context`, `code_search`, `list_services`
(`corbell/core/mcp/server.py`) — so a model queries it directly. Screened: no
auto-run surface, a `tests/conftest.py` that executes on collection, an unpinned
`pyproject.toml`. Last commit 2026-05-23.

Most of what it stores is a **map of the code** — services, methods, call paths,
infra patterns, git coupling — which is re-derived from the repositories and is
not a claim that can be false in the sense this atlas cares about. The part that
is: `corbell/core/docs/models.py` defines a `Decision` — *"A design decision
extracted from an existing design document"* — with `id`, `summary`,
`rationale`, `source_file` and `services_mentioned`, learned by
`docs/learner.py` from design docs a person confirmed, and persisted by
`docs/store.py`. An extracted rationale can be wrong, and the extraction is a
model's.

**Two defects, both in the same 90-line store, and both familiar from today's
other readings.**

*The confirmations do not survive a re-scan.* `cli/commands/docs.py:50-74` runs
the scanner, builds a fresh `CandidateDoc` list — `confirmed` defaults to
`False` — and calls `store.save_candidates(candidates)`, which writes the whole
file. It never loads the existing candidates first. So a person who worked
through `docs:scan` and confirmed a subset loses those confirmations the next
time the scan runs; the only branch that sets `confirmed = True` is
`cfg.existing_docs.auto_scan`, which confirms *everything* and is therefore the
opposite of a review. This is the sift-kg finding in an unrelated repository:
**a human decision applied to an artifact that a later pass regenerates.**

*A read failure and an empty store are the same value.* `docs/store.py:load()`
wraps its parse in `except Exception: return []`, and `save()` writes whatever
list it is handed. Corrupt the JSON and the store reports no patterns, which is
indistinguishable from a project that has learned none — and the next save
persists that emptiness. Third instance of
[the defect class](2026-08-20-a-failure-that-reads-as-empty.md) found this week,
after fx and the guard llm-wiki-memory committed against it.

## mission-control — `MeisnerDan/mission-control` at [`2b8c402b`](https://github.com/MeisnerDan/mission-control/commit/2b8c402bb4ab04f6c2a3291f832e25a7482ab472)

**Excluded: nothing it stores is a claim that could be false.** A Next.js
command centre for a solo operator delegating work to coding agents, with
Claude Code commands and skills beside it. Screened: one auto-run surface (a
`.claude-plugin/` directory), one unpinned manifest behind a lockfile. Last
commit 2026-04-01.

Its durable state is a directory of JSON files — `tasks`, `tasks-archive`,
`goals`, `projects`, `missions`, `inbox`, `activity-log`, `decisions`,
`agents`, `skills-library`, `active-runs`, `brain-dump`, `checkpoints`
(`mission-control/src/lib/data.ts:203-293`) — and the two that sound like memory
are not:

- `DecisionItem` (`src/lib/types.ts:303`) is `requestedBy`, `taskId`,
  `question`, `options`, `context`, `status`, `answer`, `answeredAt`. It is an
  **escalation queue**: an agent asks, a human answers. A question and its
  answer record what was decided, not something that could later turn out
  false.
- `BrainDumpEntry` (`:231`) is `content`, `capturedAt`, `processed`,
  `convertedTo`, `tags` — an inbox that drains into tasks.

Same boundary as `os-factory/har`, `pingdotgg/t3code` and
`Untrivial-ai/agent-orchestrator`: durable, useful, and not a belief.

**A fourth clean instance for [the vocabulary probe](2026-08-19-the-vocabulary-probe-lies.md),
and a new poison.** Every `memory` hit in the tree is RAM, and specifically
*credential* RAM: the field-ops vault caches a master password in server memory
for thirty minutes, `vault-crypto.ts:29` calls scrypt *"memory-hard"*, and
`execute/route.ts:432` zeroizes credentials from memory. The one `forget` is
*"If you forget your master password."* A probe that counts these hits reports a
memory system with a security model; the tree has a password manager.

## Proteus — [arXiv:2608.16844](https://arxiv.org/abs/2608.16844)

**Excluded from the corpus; recorded as a boundary marker.** *Proteus:
Incremental Memory Activation for Long-Context Sequence Modeling*, Bayat,
Behrouz, Mirrokni and Courville, submitted 17 August 2026, cs.LG.

Its subject is the compressive state inside a sequence model. From the abstract:
most memory models expose a *static* memory across the whole sequence, so early
tokens face no compression pressure, take too many degrees of freedom and
*"pollute"* the state — leaving less capacity for later context and more
interference between what is stored and what arrives next. The proposal is to
expand the effective capacity of memory progressively as the context grows.

That is memory in the parametric sense: a hidden state within a forward pass,
with no identity outside it, nothing that survives the session, and nothing a
correction could reach. The atlas's test does not even get as far as
falsifiability. No repository or dataset is named in the abstract page.

It belongs beside
[the two long-context papers](2026-08-14-two-long-context-papers-and-the-boundary-of-what-memory-is-for.md)
for the same reason those were kept: it measures the ceiling the agent-memory
layer is built against. The interference framing is the transferable half —
"what is stored competes with what arrives next" is the same pressure a
retrieval budget manages one level up, and this paper says it is also true
inside the model, where no retrieval policy can reach it.

---

## For next time

**When a repository's memory is not what the repository is for, the tool
registry finds it and the README does not.** Three of the four items here were
settled by grepping for a tool surface: outworked's `memorySet`/`memorySearch`/
`memoryDelete` behind MCP put it in scope against a README about pixel-art
offices, and mission-control's absence of any such surface kept it out against a
product page full of agents and decisions. The probe that fails is the one over
prose; the probe that works is over what the model is allowed to call.

# A console with no store, and two measured absences

**Status:** triage. Three items read on 2026-08-20 — a desktop agent harness, a
Google Research post and an Anthropic experiment report. None is a memory system;
one is excluded on the scope test and two were integrated as measurements.
**Origin:** three links submitted together.

---

## BossConsole — `risa-labs-inc/BossConsole` at [`0cceeb2d68495a75cee5235af5717781568c7878`](https://github.com/risa-labs-inc/BossConsole/commit/0cceeb2d68495a75cee5235af5717781568c7878)

**Excluded: nothing survives the session.** Apache-2.0, Kotlin Multiplatform and
Compose, ~1,965 files, a desktop harness that gives a bring-your-own agent an
embedded browser, a shareable terminal, an editor, a plugin Toolbox and a
governed MCP layer exposing the app itself as `mcp__boss__*` tools. Screened
clean apart from one auto-run surface (`.vscode/settings.json`) and two
agent-instruction files; nothing was installed and no Gradle task was run.

The scope test asks whether something survives the session with an identity that
can later be corrected. Three candidates, and each fails for a different reason
worth recording.

**Masteries look like durable procedural memory and are a hash map.**
`MasteryDefinition` is a DAG of plugin capability invocations with `id`, `name`,
`author`, `createdAt`, `updatedAt` — the record shape of a stored artifact. The
service header says where they live: *"Stores mastery definitions in memory and
delegates execution to `MasteryExecutor`."* `definitions` is a
`ConcurrentHashMap`, nothing writes it to disk, and the process ending is the end
of every mastery. Two details sharpen it. `createMastery` does
`definitions[id] = kotlinDef.copy(id = id)` and never stamps either timestamp, so
`listMasteries`, which sorts `sortedByDescending { it.updatedAt }`, is ordering by
a field no write path sets. And `generateMastery` — the AI-authored-procedure
entry point — logs *"GenerateMastery stub"* and returns a definition with
`nodes = emptyList(), edges = emptyList()`, with the comment *"AI integration
point: future"*. This is the corpus's most common defect in an unusually complete
form: the record type, the sort key, the CRUD surface and the generator are all
present, and there is no store.

**The procedural memory that does persist is in a different repository.** Tool
Evolver, RPA Recorder, Secret Manager and the rest are dynamic plugins living in
`risa-labs-inc/boss-plugins`, so the "agent evolves its own tools and they
survive" loop the README describes cannot be read at this pin.

**What persists here is governance state, not memory.**
`~/.boss/mcp-disabled-tools.json` — a set of tool names an operator has switched
off. That is a suppression list keyed on a name, and although it is not memory,
its design answers a question this atlas keeps asking of memory stores and rarely
gets a good answer to: *what does your suppression list do when its own storage
fails?*

Three mechanisms worth taking from it.

1. **Fail closed, and keep the operator's list while doing it.** A disabled-tools
   file that exists but does not parse used to read as "nothing disabled". It now
   withholds *every* tool, salvages the names still legible in the damaged text
   (truncation leaves most of them readable), copies the damaged bytes to
   `mcp-disabled-tools.json.corrupt` before overwriting, and rebuilds the file
   from what the operator switches back on. An *absent* file still means nothing
   disabled, which is the correct distinction between "no policy" and "unreadable
   policy" — and one almost nothing in this corpus draws. Compare
   [rejected-value tombstone](../content/patterns/rejected-value-tombstone.md),
   where the failure mode is a suppression record that silently stops applying.
2. **Asymmetric write failure.** When the file cannot be written, a *disable*
   still applies for the session — *"restricting is the safe direction"* — and the
   operator is told it will not survive a restart; *re-enabling* a tool the saved
   file records as disabled is refused outright while writes are failing. A
   toggle that changes nothing is reported as changing nothing rather than as a
   decision that did not stick. Direction-dependent degradation is the right
   shape for any policy store, and this is the clearest worked example of it read
   so far.
3. **A test that names the refactor that would break it.**
   `McpKillSwitchPersistenceTest` and `McpToolRegistryCoreTest` pin that an admin
   bypasses every permission check but *not* the disabled set, with the comment
   stating the hazard: the two filters *"are independent conjuncts today; folding
   them together (an early `if (isAdmin) return true` over the whole filter) would
   keep every other test in this file green while silently making a disabled tool
   reachable again for admins."* It asserts both the listing and the call path, so
   a stale tool list on the agent's side cannot get a call through.

And one piece of documentation worth copying wholesale. The README states, in
bold, that `McpToolRegistryCore.permitted()` short-circuits on `isAdmin` before
checking any permission, that this is *"by design, not an oversight"*, and that
for the common single-user desktop case *"every tool in the 'permission-gated'
list below is exactly as reachable as the ungated ones."* It then enumerates the
mutating tools that are not gated at all, names `k8s_exec` and `k8s_apply` as the
two to disable first and says why, notes that `k8s_use_context` only flips an
in-memory selection but that the selection decides which cluster every subsequent
call targets, and admits the kill-switch file is plaintext and rewritable by an
agent holding `run_command`. A project publishing the exact boundary of its own
guarantee, unprompted, is rare enough to point at.

## Recall is the bottleneck for parametric factuality — [Google Research](https://research.google/blog/empty-shelves-or-lost-keys-recall-is-the-bottleneck-for-parametric-factuality/)

**Not a system; integrated into the [benchmarks page](../content/benchmarks.md).**
Nitay Calderon and Gal Yona, 12 August 2026, paper at
[arXiv:2602.14080](https://arxiv.org/abs/2602.14080), dataset
[google/WikiProfile](https://huggingface.co/datasets/google/WikiProfile) — 2,150
facts, ten tasks each separating encoding from recall from recognition, 13 models,
~4.5M graded responses. Frontier models encode 95–98% of the facts and fail to
recall 26–34% of them; thinking cuts that to 11–12% and recovers 40–65% of
encoded-but-inaccessible facts against 5–15% of non-encoded ones.

It lands on the benchmarks page's "the model may already know the answer"
subsection and complicates its own fix. The no-memory baseline that section asks
for is not one number: it moves by tens of points depending on whether the
baseline arm was allowed to think, and no published memory result examined here
says which it used. It also names the reverse error the section had not
considered — a model that *encoded* a fact and failed to recall it makes an inert
memory layer look essential.

## Multi-agent systems — [Anthropic](https://www.anthropic.com/research/multiagent-systems)

**Not a system; integrated into the [cross-agent section](../content/overview.md)
of the overview.** Frontier Red Team, swarms of 10–80 instances across model
generations, each on its own VM with a shared forum and repositories.

The result that matters here is the hidden-profile one: with the deciding
information dispersed across the group, models scored 17–36% as a group against
roughly 100% individually (n=400). That is the failure a shared memory exists to
prevent, measured. The diagnosis is stated as an absence of persistence — the
agents *"enter the market with no reputation to lose, no court to appeal to, and
no colleague who remembers them"* — which is the cross-agent case for durable
memory phrased in the direction this atlas never phrases it: not "an agent should
recall facts" but "an agent should be recallable by others". Every scoping model
in the corpus answers who may read what; none records who was reliable.

Two operational findings came along with it and are cheap to guard against.
Identical agents make identical choices — 18 of 30 independently naming a branch
`mvp-game-loop` — so a store keyed on an agent-chosen name will collide. And
agents spawned 30-per-second polling daemons, 2.4 million requests against 117
accepted jobs, which is the shape a retrieval endpoint with no per-agent rate
limit is exposed to.

---

## For next time

**A CRUD surface is not a store, and the tell is the sort key.** The mastery
service has create, list, delete, a generator and timestamp fields, and its
ordering sorts by a field no write path sets. Checking which fields a write path
actually assigns found the defect faster than reading the storage layer would
have — because there was no storage layer to read.

**The most transferable thing in a repository is sometimes its README's
disclaimer.** BossConsole's security section enumerates where its own guarantees
stop, names the two tools to disable first, and admits its control file is
rewritable by the agent it constrains. Nothing about that is memory, and it is a
better model for how a memory system should describe its own limits than most of
the reports in this corpus have to work with.

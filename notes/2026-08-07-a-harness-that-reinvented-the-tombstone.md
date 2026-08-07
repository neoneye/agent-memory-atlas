# A harness that reinvented the tombstone

**Status:** triaged. One repository read and excluded, with three mechanisms
recorded because they are rarer in this atlas than in the tool that has them.
**Subject:** [os-factory/har](https://github.com/os-factory/har), Apache-2.0,
read at
[`d16a5eb6e68aad46a2b3aee0e3e4fa036bd1f042`](https://github.com/os-factory/har/commit/d16a5eb6e68aad46a2b3aee0e3e4fa036bd1f042)
(6 August 2026, 231 commits).

Screened before reading: 1 auto-run surface (`.cursor/rules/har-workflow.mdc`,
an always-apply editor rule injecting the harness workflow into agent sessions),
3 build-time execution paths (two `postinstall` scripts and a `prepublishOnly`),
7 unpinned manifests, and 8 dependency surfaces inside the seven-day cooldown —
`package.json` and `package-lock.json` at the root, in `control/`, in `docs/`
and in `packages/schemas/` had all moved in the previous three days. Nothing was
installed, built or run. Everything below is a read.

## What it is, and why it is out of scope

HAR is a harness, not a store: `har env launch 1` gives a coding agent its own
git worktree, ports and database; `har env verify 1 --full` runs the project's
own checks and records what passed; `har env teardown` removes the slot and
keeps the branch. A CLI and an MCP server over the same core, plus **Mission
Control**, a local Next.js dashboard on SQLite.

The atlas admits a system when something it stores survives the session with an
identity a later correction could name. HAR's persisted schema answers that
question by itself. The twelve Prisma models in
`control/prisma/schema.prisma` are `Repository`, `AgentSlot`,
`AgentSessionUsage`, `AgentSessionEvent`, `AgentSessionSpan`, `Run`, `WorkUnit`,
`WorkAttempt`, `ValidationBinding`, `ChangeBatch`, `CloudConfig` and
`UnregisteredRepository` — token counts, spans, stage outcomes, tree hashes,
slot state, and two rows of registry bookkeeping. Nothing in that list is a claim
that could be false and therefore
corrected — the test this atlas applied to
`shepherd-agents/shepherd` and to LangGraph's checkpointer, and the same answer.

The vocabulary check agrees and is unusually clean. Across 16,065 lines of
TypeScript in `src/`, the words `recall`, `remember`, `forget`, `embedding` and
`vector` appear **twice**, both incidental: a docstring on
`src/core/control-registry.ts:39` that begins *"Remember a repo so Mission
Control can sync it"*, and *"fire-and-forget"* in a comment at
`src/core/control-sync.ts:824`. There is no retrieval by similarity, no memory
unit, no scope key over user or project, and no tool an agent calls to store
something it believes. `src/mcp/server.ts` exposes fifteen tools and every one
of them launches, runs, inspects or tears down.

So: no report. What follows is why the exclusion is worth writing down at
length instead of in a line.

## The tombstone, in a registry

`UnregisteredRepository` is a
[rejected-value tombstone](../content/patterns/rejected-value-tombstone.md) — the
mechanism nine systems in this atlas have, arrived at here by a tool with no
memory in it at all.

The schema comment states the intent in one line:

> `/** Paths removed via unregister — blocks auto-sync re-registration until force register. */`

The loop is complete on both sides. `deleteRepository`
(`control/src/server/repositories.ts:97`) upserts the path into
`UnregisteredRepository` *before* deleting the `Repository` row, so the record of
the refusal outlives the row it came from. `registerRepository`
(`control/src/server/repositories.ts:38`) consults it on every write and throws
`RepositoryUnregisteredError` unless the caller passes `force: true`, which
deletes the tombstone as the same act that overrides it. The API route turns
that into a 409, and the client
(`src/core/control-sync.ts:558`) handles the 409 by dropping the path from its
*local* registry as well — with the comment *"Previously unregistered — drop from
local registry so auto-sync stops retrying"*.

That last step is the part worth borrowing. Most tombstones in this atlas refuse
at the write path and leave the writer to keep re-asserting; here the refusal
propagates back to the thing doing the re-asserting, so the loop quiets down
instead of failing forever at one gate. The failure it closes is exactly the one
[the pattern page](../content/patterns/rejected-value-tombstone.md) names — *"a
sync from an unchanged upstream file"* — with a background pass that periodically
re-reads a source and re-asserts everything it finds there, which is structurally
identical to a nightly extraction pass restoring a memory the user corrected last
week. HAR's auto-sync would re-register every repository it discovers on disk;
the user's deletion has to survive that, and a `deleted_at` on the row would not
have done it.

Two qualifications, and the second is the one to hold onto.

**It is keyed on a path, which is an identifier, not a value.** Normalization is
still where the work is — `canonicalizeControlRepoPath` resolves a linked
worktree back to its main checkout, which is a real normalization seam — but a
filesystem path is a far easier key than a natural-language claim, and the atlas
has watched that difference defeat two implementations (Verel's round 9, Memori's
ASCII-only key). This is the tombstone on easy mode.

**Nothing tests it.** Grepping every `*.test.ts` in the tree for
`unregisteredRepository`, `RepositoryUnregisteredError` or a 409 assertion
returns nothing, in a repository with 87 test files and 10,157 lines of tests
against 16,065 lines of `src/` — a ratio that is otherwise good, and which makes
the gap specific rather than ambient. The commit gate beside it is tested across
nine cases including *"partial staging of a verified batch is blocked"*
(`tests/hooks.test.ts:111`). So the mechanism this atlas has spent a year failing
to find in memory systems exists here, uncovered, next to a mechanism that is
covered thoroughly — which is a fair picture of how much attention negative
knowledge gets even from the people who build it.

## Content-addressed validation, and a self-reference avoided

`recordValidation` (`src/core/validations.ts:72`) hashes the whole working tree —
tracked changes, untracked files, deletions — through a temporary
`GIT_INDEX_FILE` primed from HEAD (`computeWorktreeSnapshot`,
`src/core/change-batch.ts:104`), then writes a record to
`.har/validations/<treeHash>.json`. The pre-commit gate (`checkCommitGate`,
`src/core/hooks.ts:261`) computes the staged tree with `git write-tree` and looks
for a record at that hash with `status === 'pass'` and `full === true`.

The property that makes this interesting for memory people: **the belief is keyed
by the hash of the thing it is about, so it invalidates itself.** Change one
byte and the claim "this passed" does not become stale, it becomes
unaddressable — there is no record at the new hash, and no expiry policy, no
background revalidation pass and no `valid_until` column had to be written to get
that. Memory systems reach for bi-temporal validity, decay and re-verification
sweeps precisely because their memories are keyed by subject rather than by
content, and a claim about a subject stays addressable long after it stops being
true. HAR gets the invalidation free because it is only ever making claims about
immutable content. That is not a mechanism a memory system can copy, but it is a
clean statement of what the alternative costs.

The self-reference is handled deliberately. `ensureValidationsIgnored`
(`src/core/validations.ts:48`) appends `validations/` to `.har/.gitignore` if
missing, with the comment *"Make sure validation records never perturb the tree
hash they key"* — writing the record must not change the hash the record is
filed under. A store whose write path is part of the state it hashes is a
recurring bug shape, and this one names it rather than discovering it later.

Worth noting for fairness: the gate fails open by construction. The installed
hook script (`buildHookScript`, `src/core/hooks.ts:63`) falls through to
`exit 0` with a notice when the `har` binary cannot be found, `HAR_SKIP_GATE=1`
skips it, and `resolveEffectiveMode` (`src/core/hooks.ts:227`) downgrades to
`warn` outside an agent worktree under the default `scope`. Those are defensible
choices for a commit hook and they are the same choices that make a
[governed write gateway](../content/patterns/governed-write-gateway.md)
bypassable — an evidence gate that any writer can decline is advice.

## A gateway over the instruction file

The third mechanism is the one closest to memory as this atlas defines it,
because the artifact it protects is durable prose an agent reads every session.

HAR writes a marker-delimited section into the target repo's `AGENTS.md`
(`har:agent-environment:start` / `:end`), and treats everything outside those
markers as the project's own. An agent proposes changes as
`.har/AGENTS.md.proposed` with a rationale and a timestamp
(`writeAgentMdProposal`, `src/harness/agent-md.ts:29`); applying it is a separate
act that prints the rationale and a 40-line preview and asks y/n
(`promptApplyAgentMdProposal`, `src/harness/agent-md.ts:141`). Propose, review,
apply — three steps with a person in the middle.

Guarding it is `wouldProposalShrinkExisting` (`src/harness/agent-md.ts:91`): it
extracts the content *outside* the managed markers before and after the merge,
counts non-empty lines, and refuses when a file of at least five such lines would
drop below 90% of them. `finalizeAgentsMdInstructionFiles` promotes that refusal
from a warning to a thrown `AgentsMdShrinkError`. The same check runs on the
unattended refresh path (`instruction-files.ts:342`), so the guard covers the
case where nobody is watching, which is the case that matters.

A ratio over non-empty lines is a crude integrity check and will not catch a
rewrite that preserves length. But it is aimed at the right failure — the
regenerating writer that quietly drops what it did not author — and this atlas
has read memory systems whose consolidation pass rewrites a profile with no
comparable floor at all. The mechanism is *"refuse a write that destroys more
than it adds"*, and it belongs in the vocabulary regardless of what it is
guarding.

## What would put it in scope

HAR enters this atlas the day something an agent learned in one slot is durable,
retrievable in the next slot, and correctable — a record of *why* a stage keeps
failing, say, rather than a record that it failed. Everything in
`AgentSessionEvent` today is raw telemetry: prompts and responses truncated at
8,000 characters, spans, token counts, upserted on
`(repository, sessionKey, agentTool, eventName, sequence)` and read by the
dashboard. `AgentSlot.purpose`, derived from the first captured user prompt, is
the only distillation anywhere in the schema, and it describes a session rather
than the project.

The adjacency is close enough to name: HAR's stated premise is that knowledge
about how to run and verify a repository is *"scattered across a README, a
CLAUDE.md, Cursor rules, and CI yaml today, drifting out of sync"*, and its
answer is a single machine-readable contract in the repo with drift detection
against the templates it came from (`har env maintain`,
`src/harness/drift.ts`). That is a real answer to knowledge rot, and it is
configuration authored once rather than belief accumulated from runs — which is
the whole distance between this and
[skills as procedural memory](../content/patterns/skills-as-procedural-memory.md).
The interesting version of HAR is the one where a verification run teaches the
contract something, and the shrink guard and the proposal gateway are already the
right shape to govern it.

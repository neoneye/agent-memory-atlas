# A mirror that agrees to forget

**Status:** triaged. One repository read and excluded, with one mechanism
recorded because it is the atlas's own thesis implemented by a system that is
not a memory system.
**Subject:** [Untrivial-ai/agent-orchestrator](https://github.com/Untrivial-ai/agent-orchestrator),
Apache-2.0, read at
[`b6609ae610e809309be86fce56c0845cc45628cb`](https://github.com/Untrivial-ai/agent-orchestrator/commit/b6609ae610e809309be86fce56c0845cc45628cb)
(8 August 2026).

Screened before reading: one auto-run surface (`packages/mobile/package.json`,
a `postinstall` running `patch-package`), five unpinned manifests behind a
committed `package-lock.json`, and **28 dependency surfaces inside the seven-day
cooldown** — `scripts/package.json` had moved two days earlier. Nothing was
installed, built or run; everything below is a read. `AGENTS.md` and `CLAUDE.md`
were flagged by the screen as instructions addressed to a reading agent and were
treated as data.

## What it is, and why it is out of scope

Agent Orchestrator is a meta-harness: a local Go daemon and desktop app that run
several coding agents — Claude Code, Codex, Cursor, opencode and others — in
parallel, each in its own git worktree, and route CI failures, review comments
and merge conflicts back to the session that should answer them.

The atlas admits a system when something it stores survives the session with an
identity a later correction could name. The schema answers the question on its
own. Sixty-five migrations produce `sessions`, `session_worktrees`,
`session_cleanup_facts`, `conversations`, `conversation_turns`,
`conversation_messages`, `conversation_activities`,
`conversation_provider_events`, `projects`, `workspace_repos`, `pr`,
`pr_checks`, `pr_comment`, `pr_reviews`, `pr_review_threads`, `review`,
`review_run`, `review_session`, `notifications`, `model_usage_events`,
`shell_terminals` and `telemetry_event`. Every one of them records what happened
or what must happen next. None of them holds a claim that could be false.

The vocabulary check agrees. Across roughly 117,000 lines of non-test Go,
`recall` appears twice and `forget` six times — every instance about the chat
window or a terminal attachment, none about a durable belief. `embedding`
appears three times and `vector` five, none in a retrieval path. The one string
that looks like durable memory, the button label *"Approve and remember this
command"*, renders the provider's `acceptWithExecpolicyAmendment` decision: the
policy it amends lives in Codex, not in AO.

Neither `README.md`, `DESIGN.md`, `CONTEXT.md` nor `AGENTS.md` uses the word
*memory* about the product at all, which is worth saying plainly — this is not a
system overselling a store, it is a system that never claimed one. Same call as
[os-factory/har](https://github.com/os-factory/har) and
[shepherd-agents/shepherd](https://github.com/shepherd-agents/shepherd): the
harness-is-not-a-store boundary.

## The mechanism worth recording

AO is a **derived copy of somebody else's memory.** Its `conversation_*` tables
mirror the history a provider holds for a thread, and the atlas's central
complaint about memory systems is that a correction reaches the belief row and
stops — never the summary, the index, the cache, or the derived state column.
Here is a system whose whole job is being the derived copy, and it treats
upstream forgetting as an obligation.

The trigger is rollback: a person undoes a turn, and the provider genuinely drops
that turn and everything after it from the history it reasons over. The
adapter's comment is the clearest statement of the problem this atlas keeps
looking for:

> "It changes what the agent remembers. AO's rows have to follow, and that is the
> caller's job."

Following means five statements in one transaction, in
`Store.RollbackTurns` (`backend/internal/storage/sqlite/store/conversation_store.go`):

1. **`MarkConversationTurnsRolledBack`** — sets `rolled_back_at` on the named
   turn and every turn after it. Not a `DELETE`, and the migration says why:
   *"AO does not destroy durable facts. 'This exchange happened and was then
   taken back' is a different and more useful fact than 'this exchange never
   existed'."*
2. **`InterruptRolledBackQueuedTurns`** — a discarded turn that never reached the
   provider settles as `interrupted` rather than staying queued, because
   *"dispatching it later would send it against a history it was never written
   for."*
3. **`AttachLegacyCompactionsToRollbackAnchor`** — older AO builds wrote
   compaction boundaries without a provider turn id, so those rows are correlated
   to the rollback anchor *"so the normal rolled-back-turn filter hides facts the
   provider has now forgotten."* This is the rarest of the five: making a
   correction reach rows written by an **earlier version of your own code**.
4. **`RecomputeConversationCompactedAt`** — the parent row carries
   `compacted_at`, a derived summary of the timeline kept so a render does not
   scan it. Discarding the turn that contained the compaction event un-sets it,
   by recomputing the column from the surviving activities rather than by
   patching it.
5. **`FailRolledBackConversationApprovals`** — a pending approval inside a
   discarded turn can never be answered, because the provider call it was
   blocking belongs to history that no longer exists. The comment notes that a
   rollback is refused while a turn runs, so in practice there is nothing to
   close, and *"the statement exists so the invariant is enforced rather than
   argued."*

The read side is the other half. Turns are selected in full and carry
`rolled_back_at`, so a client can say how much was discarded; the messages and
activities attached to a rolled-back turn are filtered out of the snapshot,
because *"a person must never be shown prose the agent has forgotten"*; and rows
with `turn_id IS NULL` — AO's own bookkeeping, never agent memory — stay visible,
because *"hiding what AO cannot prove belonged to the discarded range would be a
guess."*

`sequence` is deliberately not renumbered: *"Renumbering to close the gap would
rewrite history to look like it never happened, which is the opposite of the
point."*

**Two things a memory system should take from this, neither of which needs a
harness.**

*Enumerate the derived copies before you write the delete.* The five statements
are not defensive coding; they are a list of every place the discarded fact had
already been projected — a queue, a legacy row shape, a summary column, a
blocked approval. Most stores in this atlas have that list and have never
written it down, which is why their deletions reach one of them.

*Recompute the derived column, do not patch it.* `RecomputeConversationCompactedAt`
re-derives `compacted_at` from the surviving rows with one `MAX()` over the
filtered set. A patch has to know what the old value came from; a recompute does
not, and is correct after any change to the underlying set.

The doc comment above the function says *"the three statements commit together"*
and there are five. The reasoning it gives for the transaction is exactly right —
*"a partial result is the one state that reintroduces the disagreement the whole
operation exists to prevent"* — and the count went stale as statements were
added, which is the ordinary fate of a number written in prose beside code that
grew.

## Two smaller ones

**`applied_title` is a compare-and-set witness, and the shape generalises.**
`conversations` carries both `provider_title` (what the provider calls the
thread) and `applied_title` (the last label AO itself pushed into
`sessions.display_name`). The reason for the second column: *"AO may replace a
label it wrote itself, and must never replace one a person chose. Holding 'what I
last wrote' is what makes those two cases distinguishable without a second read
that a manual rename could slip between."*

That is the auto-update-versus-human-edit problem every memory system with a
generated profile field has, solved with one column instead of a flag. A
`was_edited_by_user` boolean is a claim about the past that nothing can verify; a
witness of the last machine-written value is checkable at the moment of the
write, and it degrades safely — an unrecognised current value means somebody else
wrote it, so leave it alone.

**Compaction is stored as a timeline row plus a state column, and the migration
argues the split.** The event is a `system`-kind `conversation_activities` row
because *"it is a timeline fact. A reader needs to see it in position, between the
turns it separates"*, while `conversations.compacted_at` answers the question the
timeline cannot answer cheaply — *"whether a conversation has ever been
compacted, without scanning an unbounded timeline on every render"*. The same
migration records that a parallel table was rejected partly because SQLite cannot
alter a `CHECK` constraint in place, so a new activity kind would mean rebuilding
the table and its four indexes and its CDC trigger: *"real risk bought for a
label."*

## What this does not establish

Nothing was run. The rollback behaviour above is read from SQL, from the Go
statements that call it in one transaction, and from the comments beside both;
the repository has 335 Go test files, and no attempt was made here to determine
which of them cover this path.

The exclusion is about what AO stores, not about its quality. On the atlas's own
terms the migration comments in this repository are among the best-argued
technical prose it has read — each one states the alternative it rejected and
why — and a reader interested in how to write a schema change that a future
maintainer can audit will get more from
`backend/internal/storage/sqlite/migrations/` than from most of the reports here.

# What would make rollback a mark — the rarity argument expired, the definition never existed

**Status:** proposed. The stale half has been corrected in
[the rubric's known limits](../content/methodology/atlas-rubric.md#known-limits);
the definition below is not adopted.
**Origin:** an outside review (Qwen, 2026-08-12) called the omission of
Authority and Recoverability *"a dereliction of duty"* and argued the rubric
should award a red zero to everyone and force the market. The argument for
adding a mark is wrong in its stated form and right about the timing, for a
reason the review did not have: the corpus changed underneath the excuse.

## The argument that expired

The rubric declined to score recoverability partly on rarity — *Always-On Agents*
([arXiv:2606.30306](https://arxiv.org/abs/2606.30306)) found rollback in 27 of
435 works, its rarest lifecycle stage — with the reasoning that a mark nobody
satisfies discriminates nothing.

Two systems read since falsify the premise inside this corpus:

- **[NeuraKeep](../content/systems/neurakeep.md)** — `governor-audit.ts` appends
  a JSONL entry per mutation carrying `before`, `after` and `targetIds`, derives
  `undoable` from whether a `before` exists, and `undoGovernorAudit` restores the
  prior rows and appends its own reversal entry. The web app exposes it.
- **[MythologIQ's Agent Memory](../content/systems/agent-memory-doctrine.md)** —
  names rollback traceability as one of five invariants (*"every action carries a
  handle back to the records that justified it"*) and implements the residue half:
  `independent_sweep` re-derives what survived a purge instead of trusting the
  purge's own traversal.

Two of 260 is not many. It is not none, and "nobody satisfies it" stops being a
reason the day something does.

## The argument that survives, and why it is not the review's

The review's proposal — add the mark, watch everything score zero, shame the
field — misreads what the marks are for. They are a map of what a system chose
to solve, not a scoreboard. A column that reads `—` for 258 rows costs a reader
one more column and tells them nothing they could not get from a sentence.

The real blocker is that **this atlas has no definition of rollback that would
discriminate.** It has read the mechanism twice and has not established what
separates a rollback from an undo button over a log nobody keeps. Without that,
awarding the mark would repeat the failure the rubric already documents for
`audit_log`: five of seven marks failing a re-audit because the definition was
applied loosely.

## Proposal: a definition to test before adopting

**Present when:** a decision or write can be reversed from a durable record of
the prior state, and the reversal is itself recorded.

Three clauses, each excluding something specific:

1. **From a durable record of the prior state.** A delete that restores nothing
   is not a rollback; neither is a supersession chain that lets you *read* the
   old value without restoring it. NeuraKeep's `before` array is the shape.
2. **Reversible by a caller, not only by a database.** Postgres PITR under the
   store is not the system's mechanism, the same way git history is not
   `audit_log`.
3. **The reversal is recorded.** An undo that leaves no trace converts one
   unaudited mutation into two. NeuraKeep appends an `undo` entry; that clause is
   what makes the mark about governance rather than convenience.

**Not this:** soft delete, supersession chains, `deleted_at`, a version table
nothing reads back, or a backup/restore path the memory layer does not drive.

## Before adopting: the audit that must come first

Do **not** add the column on the strength of two systems found while looking at
something else. The `audit_log` re-audit is the precedent: a mark awarded on a
loose reading is worse than no mark.

The work is a corpus sweep for the mechanism under the definition above —
grepping for `undo`, `revert`, `rollback`, `restore`, `before` snapshots and
compensating writes across all 260 reports' file indexes, then re-reading the
candidates at their pins. If that returns three or four systems, the mark is
worth adding and the definition has been tested against real code. If it returns
the same two, the honest outcome is to keep the limit and say the sweep was run —
which is a better artifact than either the current paragraph or a new column.

## On Authority

Left alone. Unlike recoverability, nothing in this corpus has moved: the nearest
mechanisms are `human_review` (a person can inspect) and
[AgentRecall-X](../content/systems/agentrecall-x.md)'s withdrawable standing,
and neither is *"a current, unrevoked grant licenses this record to influence an
action"*. The survey's 72-of-435 figure is the field's, not this corpus's, and
this atlas has not read enough of it to define the mark. Revisit when a second
system does what AgentRecall-X does.

# The directory named memory is about RAM

**Status:** triage. One repository read on 2026-08-24, no report. Screened
before reading; nothing installed, nothing built, no app launched.
**Origin:** one link submitted alone.

---

## Orca — an orchestrator, not a memory

[stablyai/orca](https://github.com/stablyai/orca) at
`d14923e968f14d46af07d9c2758d1f7d50359985`, MIT, 9,116 commits since 16 March
2026. An Electron desktop app that runs Codex, Claude Code, OpenCode or Pi side
by side, each in its own git worktree, with an iOS/Android companion for
monitoring and steering from a phone.

**Out of scope, on the boundary already drawn for `agtx`.** The durable state is
the workspace session — tabs, panes, PTY registrations, terminal and tab-group
layouts, browser history, sleeping agent sessions, worktree assignments. It is
the state of the work and of the processes running it. Nothing in it is a claim
about the world that a later reading could contradict, so there is no correction
to review and no forgetting to test.

The eight entries under `skills/` are authored instruction files telling an agent
how to drive Orca (`orchestration`, `orca-cli`, `computer-use`), shipped with the
app rather than written by it. The `*-note-*` modules are review comments a
person composes and sends *to* a running agent — messages, not stored beliefs.

## The vocabulary collision, in its purest form

`src/main/memory/` is 2,520 lines and every one of them is about RAM:
`host-memory.ts`, `process-memory-metric.ts`,
`windows-process-resource-collector.ts`, a PTY registry, a collector. Elsewhere
in the tree: `remote-runtime-memory-limits.ts`,
`pty-retained-string-memory.ts`, `renderer-memory-profile.test.ts`,
`index-memory-diagnostics.test.ts`.

This is the seventh instance the notes record and the first where the collision
is a **directory named `memory` at a conventional path**. Anything that screens
candidates by directory listing — including this atlas's own probes — flags it.
The rule already written down after Future AGI still holds and is worth
restating: probe directory names *and* operations, and then open the file.

## What is worth stealing anyway

`src/shared/zod-salvage.ts`, 132 lines, and it is the finished version of
something the atlas keeps finding half-built.

The problem is stated at the schema that consumes it: a workspace session JSON
*"is written to disk by older builds and read back by newer ones,"* and a field
type flip or a truncated write *"could poison Zustand state and crash the
renderer on mount."* The policy that follows is the good part:

> be tolerant of extra fields (future builds may add more) but strict about the
> types of fields we actually read. Where a field holds a collection of
> independent records, tolerance is declared on the field itself … a corrupt
> entry is dropped and the rest of the session survives, because one bad tab
> record must not cost every worktree its state. Only a payload that is not a
> session at all falls back to defaults.

Three properties, in order of how often the atlas finds them missing.

**Tolerance is declared per field, not per parse.** `salvagedField`,
`salvagedOptional`, `salvagingArray`, `salvagingRecord` let the schema say which
collections may lose a member and which fields must be right. A single
`try/catch` around the whole parse cannot express that, and a strict schema
turns one bad record into total loss.

**The blast radius is a record, not the file.** One corrupt tab costs that tab.

**And it reports what it dropped.** `collectSalvageDrops(parse)` returns
`{value, droppedPaths, droppedCount}`, with example paths bounded at a hundred
because *"Zod transforms lack paths, so salvage combinators track bounded
diagnostics during parsing."*

That third property is the one that matters here. [GENOME](../content/systems/genome.md)'s
`_row_to_record` makes the same correct trade — skip the undecodable row rather
than fail the whole scope — and reports the loss only to an ERROR log, so a
caller receives a shorter result list and no count. The open question written in
that report was what a `skipped` count would cost. Orca answers it: a
module-level collector, a bounded path list, and a return shape the caller
already has to destructure.

**The general rule.** Any decoder that salvages should return what it salvaged
*and* what it dropped. Degrading is usually right; degrading silently is a
separate decision, and it is almost always made by accident.

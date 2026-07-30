---
title: "Juggler"
eyebrow: "A gitignored notebook with a delete button"
description: "One MEMORY.md per project, deliberately kept out of git so it is private per checkout, maintained by a single remember/forget tool and rendered as a context item where each dated fact has its own delete control."
root: ../..
page_kind: system
source_name: "juggler-ai/juggler"
source_url: https://github.com/juggler-ai/juggler
revision: bf81e61087a6e6af24e5ffd225d66c74135a4faa
revision_url: https://github.com/juggler-ai/juggler/commit/bf81e61087a6e6af24e5ffd225d66c74135a4faa
analyzed_at: 2026-07-30
capabilities: "human_review"
matrix:
  memory_unit: "One dated bullet — `- [YYYY-MM-DD] one fact` — in a flat list under a single heading, order preserved as written"
  storage: "`<project>/.juggler/MEMORY.md`, a plain Markdown file, git-ignored so it never leaves the checkout"
  retrieval: "The whole file is a context item on each conversation; there is no search, ranking or selection"
  write: "One `memory` tool with two actions, `remember` and `forget`; the assistant is prompted to use it only for facts that outlive the session"
  update_delete: "`forget` removes every entry matching a case-insensitive substring; revision is forget-then-remember"
  scoping: "One file per project checkout, per machine — partition rather than a filter"
  integration: "A context item in the Juggler UI, plus a seeded system prompt; every write appears in the conversation transcript"
  background: "None"
  trust: "None. A bullet is a fact because the assistant wrote it or the user left it there"
  strengths: "A canonical format the writer re-tidies, a per-fact delete control in the UI, and 43 committed test cases against 772 lines of implementation"
  risks: "`forget` matches by substring, so one careless match string removes more than it names, and nothing records what it removed"
---

## 1. Executive Summary

Juggler is an AGPL-3.0 coding assistant, and its project memory is 772 lines —
a 637-line context item and a 135-line formatter — with 43 test cases across
five test files against them.

The design is stated plainly in its own documentation and the framing is worth
quoting because it names a distinction this atlas cares about: memory *"is not a
replacement for your agent instructions file (`CLAUDE.md` / `AGENTS.md`): that
file is the instructions **you** write for the assistant; memory is the notes
the **assistant** keeps for itself."* Two artifacts, two authors, one directory —
the atlas's fifth divergence written into a docs page.

**The storage decision is the interesting one.** Memory lives at
`<project>/.juggler/MEMORY.md`, and `.juggler/` is git-ignored, so memory is
*"private to your checkout — never committed, never shared with your team, and
per-machine."* Every other Markdown-notebook system in this corpus —
[Basic Memory](../basic-memory/), [claude-mem](../claude-mem/),
[TigrimOSR](../tigrimosr/) — puts the file somewhere a team could share it, and
several treat git history as the audit trail. Juggler deliberately gives that up
to make the file private, which trades away provenance for a guarantee that the
assistant's notes about a codebase never reach a colleague's review.

The format is strict — `- [YYYY-MM-DD] one fact per bullet` under a single
heading, order preserved — and self-healing: *"if you edit it loosely (extra
blank lines, a missing date), the assistant tidies it back to this canonical
shape the next time it writes."* A hand-editable file that a machine
re-normalises is a real design commitment, and the 185-line `memory-format-test.js`
is where it is defended.

`human_review` is earned three ways over: the file is plain Markdown the user
can open, the Memory context item renders each fact on a dated row **with a
delete button**, and every `remember` and `forget` appears in the conversation
transcript as it happens.

## 2. Mental Model

There is no epistemology. A bullet is true because it is in the file; it stops
being true when a substring match removes it. There is no status, no confidence,
no provenance beyond a date, and no ranking — the whole file goes into context.

What the design *does* model is a discipline about what belongs there. The tool
description tells the assistant to record only things that stay true **across**
sessions — commands, conventions, corrections, architectural constraints — and
explicitly not ephemeral within-task state. That is the write policy most systems
leave to an extraction prompt, stated as a tool contract instead, which makes it
auditable: `memory-system-prompt-test.js` exists to check what the assistant is
told.

Revision is `forget` then `remember`, so a corrected fact is a deletion and an
insertion with a new date rather than an edit. The old text is gone; only the
transcript remembers it existed.

## 3. Architecture

Nothing to run. A Markdown file in a git-ignored directory, read as a context
item, written by one tool. No database, no embedding, no service, no index — and
consequently no operational failure mode more complex than a missing file, which
`lastGoodMemory` guards with a per-path fallback.

## 4. Essential Implementation Paths

- `web/extensions/juggler-core/context-items/memory-context-item.js` (637) —
  the tool schema, validation, execution, badges, seeding.
- `web/extensions/juggler-core/context-items/memory/memory-format.js` (135) —
  the canonical format and its re-tidying.
- `web/js-tests/unit-tests/memory-item-test.js` (229),
  `memory-format-test.js` (185), `memory-system-prompt-test.js` (134),
  `memory-seed-test.js` (114), `integration-tests/memory-tests.js` (200).
- `docs/memory.md` — the model, stated for users.

## 5. Memory Data Model

A line. `- [2026-06-14] Build is \`make build\`, never \`go build\`` is the whole
unit, and the examples in the documentation are unusually good at showing what
the format is for: a build command, a prohibition the user issued, a
non-obvious architectural constraint.

The date is a record date — when the assistant wrote the line, not when the fact
became true — so there is one clock and no bi-temporality. Order is preserved as
written rather than sorted, which means the file reads as a log and a reader can
see what the assistant learned recently without a timestamp comparison.

## 6. Retrieval Mechanics

There are none to speak of, and that is coherent at this size: the file is
injected whole as a context item once it exists. No search, no embedding, no
relevance, no budget beyond whatever the file has grown to. The design's implicit
bet is that a memory file curated by a strict write policy and a delete button
stays small enough to read entirely, and nothing in the repository enforces or
measures that.

## 7. Write Mechanics

Writes block and are the assistant's own tool calls. `remember` appends one
dated fact; `forget` takes a `match` string, validated as required, and removes
*"the entry/entries"* matching it case-insensitively. Validation rejects any
action that is not one of the two and rejects a `forget` with no match string.
Seeding is best-effort with an explicit comment that a failed seed *"must never
fail the remember/forget tool"*.

**The substring match is the risk.** `forget` with `match: "build"` removes every
line containing "build", and the tool returns without a record of what it took.
The transcript shows the call; it does not necessarily show the three unrelated
facts that matched. A deletion primitive whose blast radius is decided by a
model's choice of substring is the one place this otherwise careful design
trusts the model with something sharp.

## 8. Agent Integration

The memory tool is one context item among Juggler's extension surface, following
the `plan` plugin's idiom for tool-action badges. Writes are visible in the
transcript as they happen, which is a small and effective transparency
mechanism: the user does not have to open the file to know it changed.

## 9. Reliability, Safety, and Trust

`human_review` is earned, in its post-hoc form: a person inspects and deletes
rather than approves in advance.

**No tombstone.** A forgotten fact leaves no trace, and the assistant is free to
re-record it next session having been told the same thing again. For a per-project
notebook with no extraction pipeline the exposure is small — the only writer is
the assistant, in conversation, in front of the user — but the mechanism is
absent.

**No trust state, no bi-temporality, no scope filter, no audit log.** The
gitignore decision is worth reading as a governance choice rather than an
omission: it forgoes git history as an audit trail on purpose, in exchange for
the file never being shared.

## 10. Tests, Evals, and Benchmarks

43 test cases across five files against 772 lines of implementation, none run
here. The distribution is the interesting part — separate suites for the item,
the format, the seed and the **system prompt**. Testing the text the model is
told about a tool is rare in this corpus and is exactly right for a design whose
write policy lives in a prompt rather than in a gate.

No benchmark, no retrieval measurement, no published numbers, and none claimed.
No negative assertion was found; the one this design invites is that a `forget`
with a match string does not remove a non-matching neighbour.

## 11. For Your Own Build

### Steal

- **Separate the file the user writes from the file the assistant writes,** and
  say so in the documentation. Conflating instructions with memory is how a
  user's directive quietly becomes an assistant's guess.
- **Pick a canonical line format and re-tidy on write.** A file a human can edit
  loosely and a machine normalises is more durable than one that requires either
  party to be careful.
- **Put a delete control on each fact.** It is the cheapest human-review surface
  in this atlas and it converts "the assistant knows something wrong" from a
  support question into a click.
- **Show every write in the transcript.** Memory that changes silently is memory
  the user stops trusting.
- **Test the system prompt.** If your write policy lives in prose handed to a
  model, that prose is code.

### Avoid

- **Deleting by substring.** Match on an identifier, or return what you removed
  so the transcript carries it. A model choosing a short match string is a
  multi-fact deletion with no receipt.
- **Assuming the file stays small.** Whole-file injection with no budget has one
  failure mode and it arrives gradually.

### Fit

This is the right shape for a single-developer coding assistant where memory is
a handful of project conventions and the user is present to correct it. The
privacy decision — gitignored, per-machine — makes it a good fit for a codebase
where an assistant's notes might contain things nobody wants in a pull request,
and a bad fit for a team that wants shared conventions to propagate.

Look elsewhere if memory has to hold anything you will need to prove you
deleted, or anything a second person should see.

## 12. Open Questions

- **How large do these files get in practice?** Whole-file injection with no cap
  and no ranking is the design's one unbounded quantity.
- **What does `forget` actually remove?** The tool returns without enumerating
  its casualties; whether the UI shows them was not traced.
- **Does the re-tidy ever lose a hand-edit?** The format is normalised on the
  next write, and what happens to a line a user wrote in a shape the formatter
  does not recognise was not established.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `web/extensions/juggler-core/context-items/memory-context-item.js` | 637 | Tool schema, validation, execution, badges |
| `web/js-tests/unit-tests/memory-item-test.js` | 229 | Item behaviour |
| `web/js-tests/integration-tests/memory-tests.js` | 200 | End-to-end |
| `web/js-tests/unit-tests/memory-format-test.js` | 185 | The canonical format |
| `web/js-tests/unit-tests/memory-system-prompt-test.js` | 134 | What the model is told |
| `web/extensions/juggler-core/context-items/memory/memory-format.js` | 135 | Formatting and re-tidying |
| `web/js-tests/unit-tests/memory-seed-test.js` | 114 | Seeding |

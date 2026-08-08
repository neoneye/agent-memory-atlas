---
title: Contributing
eyebrow: How the atlas grows
description: How to propose a memory system, correct a report that is wrong, or argue with a pattern — what each costs, what the screen refuses to skip, and what this atlas declines to publish.
root: ..
page_kind: methodology
---

Three kinds of contribution are useful here, and they are not equally expensive.
A correction takes minutes and improves the thing that makes this atlas worth
reading — every claim is pinned to a commit, which means every claim is
checkable, which means every wrong claim is *findable*. A new system takes a
day. An argument with a pattern is somewhere in between and is the only one that
can change what the atlas thinks.

All three start in the same two places: an issue or pull request on
[GitHub](https://github.com/neoneye/agent-memory-atlas), or
[Discord](../discord.html) if you would rather talk first.

## Correcting a report

**This is the most valuable thing you can send, and the bar is low.** Say what
the report claims, what the code at the pinned commit actually does, and give a
path. You do not need to be the author of the system, and you do not need to be
polite about it.

Every report header carries the exact commit it was read at, so a correction is
a decidable question rather than an argument about impressions. Two outcomes are
possible and they are handled differently:

- **The report was wrong at its own pin.** It is fixed and the History section
  records what was wrong, because a report that quietly edits itself is a report
  you cannot trust the rest of.
- **The report was right at its pin and the system has since changed.** That is
  a re-analysis, not a correction: the report is re-pinned to a current commit
  and the History entry says what moved. A published claim that went stale is
  not the same failure as a published claim that was never true, and the atlas
  does not blur them.

Disputing a capability mark specifically has its own procedure — see
[how to dispute a mark](../methodology/atlas-rubric/#how-to-dispute-a-mark) in
the rubric. Marks are definitions, so most disputes turn out to be about the
definition rather than the system.

## Proposing a memory system

The scope bar is one sentence: **memory that outlives a session.** Something is
stored, retrieved later, and could in principle be scoped, corrected, or
forgotten. A framework whose "memory" only decides which messages stay in the
current context window is conversation-window management, and it belongs in the
*Not in scope* section of the [comparative report](../compare/) as a short
example rather than as a report with empty columns. Compaction counts only when
something survives the session with an identity that could later be corrected.

Two things that look like criteria and are not:

- **Novelty is not required.** A system whose memory is a well-covered shape
  still gets a report. The atlas compares implementations, and a competent
  instance of a common design is evidence about the design. Excluding systems
  for being unoriginal cost this project six reports before the rule was
  reversed.
- **A restrictive licence is a caveat, not an exclusion.** BSL, ELv2, PolyForm
  and "all rights reserved" are stated in section 1 so a reader knows what they
  may do with what they read. Fifteen of the systems here are not open source.

The genuine exclusions are narrow: nothing survives the session, the mechanism
is closed-source behind an open wrapper, or there is no inspectable code at a
pinned commit at all.

**Self-nomination is welcome and is disclosed rather than discounted.** If you
built the system, say so; the report will say so too. The atlas contains a
self-assessment of its author's own project, flagged as one, for the same
reason.

## What adding a system actually involves

If you want to write the report yourself rather than propose the system, the
workflow is in the repository as an agent skill —
`.agents/skills/add-memory-system/` — and it is worth knowing what it enforces
before you start.

**Screen the checkout before reading a file of it.** This is a precondition, not
a suggestion, and it is the one step no contribution skips:

```sh
python3 scripts/screen_repo.py /absolute/path/to/source-repository
```

Analysing a memory system means cloning a stranger's repository onto your own
machine and often running its build. The screen reports auto-executing hooks,
build-time execution, and unpinned dependency surfaces *without running anything
from the tree*. `NOTHING SCANNED` is a finding rather than a pass, and so is
`FRESH` — a dependency published in the last seven days is where an undetected
registry compromise lives, and `npm ci` does not protect you there, because it
reproduces the lockfile faithfully however new the pin is.

After that, the shape of a report is fixed: twelve numbered sections plus a file
index and a History entry, defined in the
[per-repository method](../methodology/per-repo-report-format/). The parts that
reviewers reject most often:

- **A claim with no path.** Every mechanism described has to be locatable in the
  tree at the pinned commit. "Supports semantic search" is not a finding; a file
  and a function is.
- **A product claim promoted to a code claim.** What the README says and what
  the code does are separate categories and the report keeps them separate,
  including when they agree.
- **A capability mark with no evidence.** The seven rubric marks have
  definitions. A mark asserts that a specific subsystem meets one.
- **A missing diagram.** Every system report carries a Mermaid diagram of the
  real mechanism, and the build fails without one.

Then `npm run build && npm run test`. The suite checks pins, anchors, claim
counts, capability evidence, history ordering, diagram syntax, and about a dozen
other things that have each gone wrong at least once.

## Arguing with a pattern

The [pattern library](../patterns/) states, on every page, whether it is
reporting an established practice or arguing for one. The arguing pages are the
ones that most need a contradicting instance.

Two contributions are especially useful. **A counter-example**: a system that
does the thing the pattern says nothing does, which moves a page from advocacy
toward reporting and has happened more than once. **A failure**: a system that
adopted the pattern and was hurt by it, which is the evidence the library is
thinnest on, because implementations are public and postmortems are not.

## What this atlas declines to publish

- **Adoption as evidence.** Star counts, download numbers, and popularity say
  nothing about whether deletion reaches derived artifacts. Maturity claims here
  rest on checkable signals — tests, migrations, pinned dependencies, a
  correction path — not on an audience.
- **Benchmark numbers this project did not produce or read the harness of.**
  See [benchmarking memory](../benchmarks/) for why a single score is weak
  evidence about a memory layer.
- **Private information.** A tip sent by email is a pointer to go and look, not
  a citation. If it cannot be verified against a public artifact at a pinned
  commit, it does not appear.
- **Unpinned claims.** If the analysed commit cannot be named, there is no
  report, because there is nothing a future reader could check it against.

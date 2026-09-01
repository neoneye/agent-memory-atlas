# The memory subsystem is the stillest part of the repository

**Status:** three re-reads in two days, all landing the same way, with an
operational consequence for how the next one is done.

---

## The three

| System | Range since the previous pin | The memory files |
| --- | --- | --- |
| [Matrix OS](../content/systems/matrix-os.md) | 102 commits, **1,167 files, 104,120 insertions** | all five **byte-identical**; the `memories` table unchanged; no `sqliteTable` added anywhere in the range |
| [Areev](../content/systems/areev.md) | 17 commits | the store, the render path, the CAL surface and **every file under `crates/areev-conformance/`** byte-identical |
| [aimee](../content/systems/aimee.md) | 15 commits | no file any mark rests on touched; the range is CI workflows, release scripts, an attention guard, a session-token hook and Windows IPC |

Three for three, across a TypeScript agent OS, a Rust substrate and a
million-line C tree. In the largest case the repository moved by a hundred
thousand lines while the subsystem this atlas reports on did not move by a byte.

## Why this is not a coincidence worth shrugging at

A memory layer is a schema plus the read and write paths over it. Once those
exist and something depends on them, they are the most expensive thing in the
repository to change and the least rewarding to touch. Product surface — a
desktop embed host, a chat provider adapter, a Windows IPC fix, a release
pipeline — is where the commits go. **Repository churn is therefore a bad proxy
for report staleness**, in the direction that wastes the most time: the busiest
projects generate the most re-pin pressure and the least reason for it.

The freshness job flags an orphaned or aged pin, which is the right signal for
*something might have moved*. It cannot tell whether the thing that moved is the
thing the report is about. Nothing can, short of the diff.

## The consequence: diff the appendix first

Every report carries a file index naming the files that hold the mechanism. That
list is the cheapest possible staleness test, and it should run before anything
else in a re-read:

```sh
git diff --stat <pinned-sha>..HEAD -- <the appendix's files>
```

Empty output settles the largest question in one command. It does **not** end the
re-read — the skill is right that wiring moves without the mechanism moving, that
criticisms go stale in the direction nobody reports, and that a producer can
vanish in a diff touching no schema — but it changes what the rest of the reading
is looking for. When the files are identical the work is: re-run the absence
claims, re-check the marks in both directions, and look for a *new* subsystem the
previous reading missed. That last one is where the value was this week.

## What the still cases actually produced

None of the three was a wasted reading, and none of the findings came from the
diff:

- **Matrix OS** gained two files named for memory that hold window geometry —
  a naming collision inside a repository whose real store is 328 lines away.
- **aimee** gave up `decision_log`, a store three previous readings had missed
  entirely, [described separately](2026-09-01-a-judgement-with-a-revisit-date.md).
- **Areev** gave up a committed benchmark directory the report had called absent,
  which had been there at the previous pin too — a criticism wrong when published
  rather than overtaken.

Two of those three are failures of the *first* reading, surfaced by a second pair
of eyes rather than by upstream movement. That is the argument for re-reading a
still repository at all, and it is a different argument from the one the
freshness job makes.

# The good pattern is usually already in the building

**Status:** reviewing heuristic, three instances, all from the last week.
**Origin:** noticing the same shape in fx, memoir and KAISEN and realizing it is
worth looking for on purpose rather than stumbling into.

## The shape

A repository solves a hard problem correctly in one subsystem and does not apply
the solution in another subsystem that has the same problem. The weak half is
not weak from ignorance — the team demonstrably knows the technique, because
they wrote it down forty files away.

That makes it a different finding from "they got it wrong". It is a finding
about *transfer*, and it is much easier to report usefully, because the fix does
not need designing: it already exists, in their own voice, in their own tree.

## Three instances

**fx — durability.** The session layer has an append-only event log, a two-phase
intent/commit protocol, lock files with a two-second acquisition deadline, log
generations, and a named invariant (`ImmutableSessionIdentity`) refusing any
compaction that would alter a session's identity. Three directories away, the
store holding the preferences a user explicitly asked to keep forever is
read-modify-write over a whole file with no lock, so two concurrent processes
lose each other's writes.

**memoir — how to test a constant.** Its SPEC argues a retention requirement
*relationally* and normatively for merge tombstones: the budget must be large
enough to outlive any stale replica, or completions resurrect. One subsystem
over, the cloud backup caps were pinned as literal numbers in both the code and
the test — so when the two constants were swapped, the test moved with them and
asserted that a paying account retained less than a free one. The relational
form was already the house style for exactly this problem.

**KAISEN — what deserves to be permanent.** `seen_hashes.json` grows without
bound so a candidate can never be re-proposed. `state.json`'s history is
truncated to the newest 500 entries, so the `duplicate_skip` record naming *why*
something was refused ages out. The permanent thing and its explanation were
given opposite lifetimes, in the same project directory, by the same design.

## Why it recurs

Nothing about these is careless. In each case the strong subsystem is the one
that had an incident, a spec, or an obvious concurrency requirement, and the
weak one is the one that looked small. `memories.json` *is* small. A history
ring *is* the sane default. Backup caps *are* just two numbers.

The pattern is that **rigor attaches to the subsystem that visibly needed it,
not to the property that needed it.** Durability, relational assertion and
retention are properties; they were applied where the pressure was felt rather
than everywhere they hold.

## The heuristic

When a report finds a weakness, spend one grep asking whether the same
repository solves that exact problem elsewhere:

- found an unlocked read-modify-write → grep the tree for `lock`, `atomic`,
  `transaction`, `CAS`
- found a test pinning a literal → grep for an assertion of the *relationship*
  on a neighbouring constant
- found an unbounded structure → grep for the caps and rings on its siblings
- found a missing validation → grep for the validator on the adjacent input

Two outcomes, both worth having. If nothing turns up, the finding is a gap in
the design and should be reported as one. If something does, the finding is
sharper, shorter and much more likely to be acted on: *you already do this in
X; the same argument applies here.*

## For the atlas specifically

This is also the fairest way to report a defect in an otherwise strong project.
"Read-modify-write with no lock" reads as a complaint. "Read-modify-write with
no lock, three directories from your own two-phase commit" reads as an
observation, and it is the more accurate one, because it says the team has the
capability and did not apply it — which is what actually happened.

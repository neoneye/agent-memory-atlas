# The corpus held the answer; the rubric had no column

**Status:** method finding. An axis the atlas had already measured three times
without being able to see it.
**Origin:** reading a multi-agent architecture survey that decomposes
coordination differently than this atlas does, two days after reading three
systems that each answered its central question.

## What happened

A survey article split multi-agent coordination into four planes — control,
communication, state, verification — and its **state plane** asks who currently
holds the right to *change* a record. Claims, leases, atomic transitions, a
conditional update that refuses a second claimant.

None of the seven capability marks measures that. `scope_enforced` certifies
that a key reaches the read path and is silent on two processes writing at once.

The uncomfortable part is that the atlas already had the data. In the two days
before reading the survey, three reports were written that each answer the
question a different way:

- **TrueForge** fences every turn-scoped write on the turn still being
  `running`, takes `BEGIN IMMEDIATE`, and makes terminal turns immutable.
  Ownership is a state machine.
- **lossless-context-mcp** has no lock anywhere and argues it needs none:
  content-addressed idempotent blobs and one append-only event file per writer
  remove the contention instead of guarding it.
- **fx** holds both positions in one repository — lock files with a two-second
  deadline and a two-phase intent/commit protocol for its session log, and
  read-modify-write over a whole file with no lock for the memories a user asked
  it to keep.

Three designs, three theories of ownership, all written down in three reports,
and no column in the matrix where a reader could find them next to each other.

## The insight

**Reading more systems does not produce a new axis. A different decomposition
does.**

Each of those three facts was noticed, understood, and published. What was
missing was not observation — it was a *slot*. The atlas's seven marks are
derived from one question ("what does this store, and can it be corrected?"),
and that question does not generate an ownership axis no matter how many
repositories it is asked of. An outside frame that starts from coordination
rather than from memory generates it immediately.

That is a specific and slightly humbling limit on the method: a corpus reviewed
carefully against a fixed rubric accumulates evidence for axes the rubric cannot
name, and the evidence stays invisible in prose, one report at a time, until
something else supplies the category.

## The generalizable version

Two different failures look identical from inside a review project:

1. **We have not read enough systems to see the pattern.** Fixed by reading more.
2. **We have read them and have nowhere to put the observation.** Not fixed by
   reading more, ever.

The tell for the second is that the finding is *already in the reports* and only
in prose — repeated in several, cross-referenced in none, absent from every
generated table. That is exactly what a missing column looks like from the
inside, and it reads like thoroughness rather than like a gap.

So it is worth periodically asking a different question of the corpus than the
one the rubric asks, specifically to find out what has been accumulating in the
prose. Not to adopt the other frame — the atlas's question is the right one for
what it is — but because the answer to *"what have I written down three times
and never tabulated?"* is only visible from outside.

## What was done

The axis went into [the rubric's open
work](../content/methodology/atlas-rubric.md) as a third item beside authority
and recoverability, with the same discipline applied to it: three instances is
more than either of those had when it was named, and what keeps it off the mark
list is the missing *definition* — one that separates a real ownership protocol
from an incidental file lock, and that does not award a mark to a system which
simply never has two writers.

Naming it without awarding it is the honest middle. The corpus can now
accumulate against a named question instead of against no question.

## For next time

When a report's prose contains a mechanism the frontmatter has no field for,
that is a signal and not a nuisance. Worth grepping the corpus for it
periodically — the third occurrence of an untabulated mechanism is the moment to
ask whether it wants a column, and by then it has usually been sitting in the
reports for weeks.

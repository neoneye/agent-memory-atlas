# A re-pin is a claim about the whole report, not about the thing you checked

**Status:** method failure with one instance, and a cheap check that would have
caught it.
**Origin:** memoir-cli, re-pinned to 3.12.0 in the morning and re-read properly
in the afternoon of the same day.

## What happened

The project's maintainer had closed the report's central criticism: the absolute
tombstone that no user could reach now has a `memoir forget` verb. I verified
that — carefully, including that hiding is monotonic, that a purge keeps a
sha256 identity so the tombstone still wins merges, and that tombstones get a
prune budget separate from live rows — awarded the `tombstone` mark, moved
`revision` and `analyzed_at`, and shipped.

The report then pinned 3.12.0 and described 3.11 in two places.

Retrieval was still written up as a substring count returning the first 500
bytes of each file. The same release had replaced it with field-weighted scoring
over five fields, saturating term frequency, a coverage-squared multiplier and
matched passages. And the backup-retention row still reported an inversion —
Pro retaining less than free — that the same release had fixed.

Both were *findings of mine that the project had closed*. Both were invisible
from where I was looking, because I was looking at the tombstone.

## Why it happened

Re-pinning feels like a narrow act. You went to check one thing, the thing
checked out, you move the commit id. But the commit id is not attached to the
finding you checked. It is attached to **every sentence in the report**, and
advancing it re-asserts all of them at the new commit.

The `reanalyze-memory-system` skill already says this — "check the *criticisms*
specifically: the most common stale claim is a gap the project has since closed"
— and I read that skill and then did the narrow thing anyway, because the
maintainer's message framed the work as being about the tombstone.

An upstream note about one gap is not a scope for the re-read. It is a signal
that the project has been working, which is a reason to widen rather than
narrow.

## The check

Every criticism in the report is a claim that something is *missing*. Missing
things are the ones a release closes. So before advancing a pin:

1. Grep the report body for its own negative claims — "no", "nothing", "does
   not", "has no writer", "is not tested", "only".
2. For each, go and look at the new tree. Not at the diff — at the tree. A
   rewrite that replaces a file wholesale shows up in `git log` as one commit
   with an unremarkable subject.
3. Only then move `revision`.

On memoir-cli that would have been about six greps and would have caught both.

## The second half, which I also missed

`content/verdicts.md` carries a six-bullet verdict per system, and it went stale
in exactly the same way and in the same pass. Its *Biggest risk* bullet still
led with the unreachable tombstone — the criticism I had just verified as
closed, in the report, that morning.

The report and the verdict are two surfaces over one reading, edited in two
different files, and nothing binds them. `npm test` checks that a verdict
heading links to a report that exists. It cannot check that they still say
compatible things.

**Rule:** a re-pin touches `content/systems/<slug>.md` *and*
`content/verdicts.md`, always, and the verdict's *Biggest risk* line is the one
most likely to be about the gap that just closed.

See also [the same bug twice in one
session](2026-08-19-the-same-bug-twice-in-one-session.md) — a different
re-pin failure, mechanical rather than one of scope.

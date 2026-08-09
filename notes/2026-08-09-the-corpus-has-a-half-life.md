# The corpus has a half-life — 238 pins aging at once, and the citable snapshot

**Status:** measured; two cheap proposals, one explicit non-proposal
**Origin:** a Codex conversation (2026-08-09) which recommended "stable,
versioned snapshots so researchers can cite a fixed corpus". That half is worth
building. The half it did not name is the one that decides whether the atlas is
still true in October, and it is measurable today without touching the network.

**Sequencing:** phase 0 of
[the phased program](2026-08-09-a-phased-program-and-where-to-abandon-it.md), and
first not because it is cheap. Every later phase produces an artifact that cites
the state of the atlas — a submission, a downstream row, a re-analysis delta — and
without a tag all three cite a moving target, retroactively unfixable.

Companion to [automating re-analysis](2026-08-04-automating-re-analysis.md),
which covers *which* report to re-read next. This note covers what the reader
is owed while it waits.

## The measurement

Every report carries `analyzed_at`. Grouped, over all 238:

| Window | Reports |
| --- | --- |
| 26–31 July (the project's first six days) | 113 |
| 2–8 August | 52 |
| 9 August | 73 |

**Forty-seven per cent of the corpus was read in its first six days and has not
been touched since.** Those reports are nine to fourteen days old. The
distribution is bimodal — a large old block, a thin middle, and a fresh block
from the current batch — which means the average age of a report a reader lands
on is much worse than the average age of the project.

This needed no network call. `analyzed_at` is local, free, and exact.
`scripts/check_freshness.py` asks GitHub for each upstream default-branch head,
which is the expensive path, and it is not needed to know which half of the
corpus is old.

## What `analyzed_at` currently obliges

A report is true about its commit forever. That is the guarantee, it is unusual,
and it is the reason every claim here is auditable. It is also the whole of the
guarantee: the reader's actual question is *is this still how the system works*,
and the atlas answers *here is when I looked*. Honest, and it puts the entire
inference on the reader.

The gap is not accuracy. It is that staleness is currently invisible at the
moment of reading. A fourteen-day-old report and a same-day report render
identically apart from a date most readers will not convert into a delta.

## Proposal 1 — a dated snapshot, so a citation can name what it read

Cheap and unambiguous. Tag the repository on a fixed cadence, publish the tag and
its date in the site footer, and state on the methodology page that a citation
should name the tag rather than the URL. Without it, every reference to the atlas
is a reference to a moving target, and any figure quoted from it — a mark count,
a corpus size, a "9 of 238" — is unreproducible the moment the next batch lands.

This costs a git tag and a template line. It does not require freezing anything,
building an archive, or promising a release cadence the project cannot keep; a
tag that is three weeks old is still a thing a reader can check out.

## Proposal 2 — surface the age where the reading happens

On the report header and in the systems index: the date, and the delta in days.
Nothing else.

Specifically **not** a traffic light, a freshness badge, or a
current/aging/stale vocabulary. The [compare-page
note](2026-08-04-the-compare-page-as-a-tool.md) declined normalized badges for
the reason that applies here unchanged — a badge needs a vocabulary the atlas
would have to invent, and inventing one means asserting that fourteen days is
"stale" for every project in the corpus at once. It is not: a project with four
commits a month and a project with four a day decay at different rates, and the
atlas cannot know which is which without the network call it is not making.

A delta in days is arithmetic. It asserts nothing and lets the reader apply what
they already know about the project.

## The explicit non-proposal

**Do not add scheduled upstream polling.** It is slow, it rate-limits, and it
displaces the only activity that actually fixes staleness, which is re-reading.
`check_freshness.py` stays what it is: something run deliberately, never in the
build, never on a timer.

## The limit worth stating

Neither proposal makes a single report more true. Re-reading 113 reports is the
cost and nothing here reduces it. What they change is that the staleness stops
being invisible — which matters because the failure mode is not a reader
distrusting an old report, it is a reader trusting one.

And the ranking these proposals imply is weak. Age is a proxy for drift, not a
measure of it: the two reports most likely to be wrong right now are the ones
whose *subject moved*, and age does not know that. The stronger signal — a
maintainer who has turned up in the Discord or answered a report — is already
argued for as a tier in the [re-analysis
note](2026-08-04-automating-re-analysis.md), and it is engagement observed
rather than proxied. Age is what is free. It should rank the queue and nothing
more.

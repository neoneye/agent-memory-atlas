# Archive copies, not forks

**Status:** decided 2026-11-01; applies to repositories added to the archive from
that date. The existing forks stay where they are.

## What happened

`archive_sync.py` keeps each fork's default branch at the upstream head by
moving the ref over the API. It pushes nothing, but GitHub treats the commits as
arriving in the fork, and a fork shares its parent's network, so a short `#969`
in a commit message resolves to the parent's issue 969. Every moved commit that
names an issue (`Closes #969`) or carries a squash-merge title (`(#993)`) added
a timeline line to that upstream thread: "neoneye added a commit to
agent-memory-atlas-archive/... that referenced this issue".

The ledger records seventeen runs between 2026-09-13 and 2026-10-28 that moved
forks, 499 of them on 2026-10-28. On wenlan-app/wenlan, issue #969 and pull
request #993 each got a line at 21:35:52 UTC, nine seconds after the fork moved
past `d9018db`, and the maintainer asked what it was. Nothing upstream changed:
fork activity runs no upstream CI, and a closing keyword acts only on the
upstream's own default branch. It was noise in other people's trackers, under
the atlas maintainer's account. The size of it across the archive is inferred
from the run counts, not measured issue by issue.

## The decision

New repositories are archived by `scripts/archive_mirror.py` as standalone
repositories under the same `<owner>--<repo>` name, so `archive_name` and its
check are unchanged. A copy outside the fork network resolves `#969` to its own
issue tracker, which is switched off. The script:

- refuses a repository whose licence does not grant redistribution, since a copy
  outside GitHub's fork mechanism is one; the fallback is a fork taken once and
  never synced;
- switches Actions off and reads it back before pushing, so upstream workflows
  never run in the organisation;
- pushes branches and tags without force, plus `atlas-pin-<sha>` tags for each
  pinned revision, and reads every pin back.

`archive_sync.py` now refuses to move a fork without
`--allow-upstream-references` and skips copies tagged `atlas-mirror`.

## What is deferred

- **The existing forks.** Converting them means deleting each fork and pushing a
  copy, which loses nothing that matters but is several hundred deletions in the
  organisation. Until then a re-pin of a forked repository leaves the new pin
  held upstream only, unless the person chooses to sync that one fork.
- **Full references.** A commit message that writes `owner/repo#969` or an issue
  URL cross-references from any repository, copy or fork. Not measured.
- **Keeping copies current.** `archive_mirror.py` adds pins when it is re-run;
  nothing follows an upstream's default branch between re-reads. That is the
  part of the old sync this decision gives up.

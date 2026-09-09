---
name: work-the-queue
description: Take the top repository off the atlas's work queue and do it — a first reading or a re-reading, then build, test, commit and push. Use when asked to work the queue, do the next repo, pick up the next system, or when told to keep going through the backlog. Ends with the item removed from the queue and the queue topped back up.
---

# Work the Queue

One item, start to finish. This skill does not decide *what* to read — that is
`scripts/queue.py`'s job, and the reasoning behind its ranking is in
`notes/2026-08-04-automating-re-analysis.md`. This skill takes what the queue
hands over and finishes it, which means the reading, the integration, the build,
the commit, the push, and only then the removal.

**The queue is not a plan and not a promise.** It holds at most five links and
lives in gitignored `scripts/state/queue.txt`. Anything in it can be wrong, out
of date, or a bad idea on inspection — see "When to put it back" below.

## Take one item

```sh
python3 scripts/queue.py peek     # bare URL of the top item
python3 scripts/queue.py list     # the whole queue with the reasons for each pick
```

`peek` exits 1 on an empty queue. Fill it and look at what came back:

```sh
python3 scripts/queue.py fill
```

If `fill` warns that the register is old, **stop and rebuild it** rather than
working a stale pick — the item may already be done.

```sh
GITHUB_TOKEN=... python3 scripts/drift_report.py --out scripts/state/drift.jsonl
```

Read the reason on the line you are about to work. It carries the status, the
drift, the star count, the last reading and the score, and it is there so the
pick can be argued with. If the reason does not justify the work, say so and
take the next one — the ranking is a heuristic, not an instruction.

## Decide which skill this is

```sh
rg -l -i "^source_url: .*${OWNER}/${REPO}\b" content/systems/
```

- **A report exists** → `reanalyze-memory-system`. Re-pinning, deciding whether a
  published claim went stale, re-running every absence search, and the
  rename-and-redirect convention all live there.
- **No report** → `add-memory-system`. Scaffolding, the capability definitions,
  the matrix rules and the integration checklist live there.

Check for a rename before concluding there is no report: a project that renamed
itself may be in the atlas under its old name, and GitHub redirects the API but
not your grep. Grep the atlas for the old name and the changelog for `renamed`.

Neither decision is this skill's to re-litigate. Invoke the right one and follow
it exactly.

## Screen first, every time

Both skills require it and it is not optional here either. A queue item is a
*newer* commit than anything previously screened, and the newest commit is
exactly where a compromise arrives.

```sh
python3 scripts/screen_repo.py /absolute/path/to/checkout
```

Nothing is installed and no suite is run without a decision made on purpose, in
front of the user, with the cooldown respected.

## Build, test, commit, push — as one gated chain

```sh
npm run build && npm test
```

**Never pipe the test step.** `npm test | tail -6` reports the exit status of
`tail`, and a chain gated on that has committed over a failing suite in this
repository before. Write to a file and gate on the status if the output is long:

```sh
npm run build > /tmp/build.log 2>&1 && npm test > /tmp/test.log 2>&1; echo "chain=$?"
```

Commit and push only on `chain=0`. Join every step before a commit with `&&` so
a failure cannot fall through to the push, and keep one git actor: no
foreground git call while a background commit is running, or the index lock goes
stale.

A re-pin also needs a re-screen recorded in the ledger, or the screening check
fails the build:

```sh
python3 scripts/screen_corpus.py --reuse /path/to/clones --only <slug>
```

The reused clone must sit in a directory named for the slug and be at the pinned
revision. `scripts/state/` is gitignored, so `git add -A` will not sweep the
queue or the register into the commit — but check `git status` before staging
anyway.

## Close the item

**Only after the push succeeds:**

```sh
python3 scripts/queue.py done <url>
python3 scripts/queue.py fill
```

That order matters. Removing first and failing later loses the item silently,
and the queue is the only record that it was ever selected.

## When to put it back

Leave the item in the queue, say why in one line, and move on:

- The repository turned out to have no memory system worth a report. Say what
  you looked for. This is a real outcome — an examined-and-excluded bullet in
  the overview, not a report — and the queue entry stays until that bullet
  lands.
- The screen surfaced something that needs a human decision.
- The reading is half-done and the turn is ending. A partial report is worse
  than none; commit nothing and leave the item where it is.

Do not silently swap to an easier item. If you skip the top of the queue, say
which one you skipped and why, in the same message as the work you did instead.

## One item, not five

Finish one and stop, unless the user asked to keep going. Each item is a full
reading: a clone, a screen, a report, a count sweep, a build and a push. Batching
them produces one enormous commit nobody can review and one context window that
runs out halfway through the third.

## The queue holds five, and that is the point

`scripts/queue.py` refuses a `--max` above five. If asked to add work to a queue
that is already full, **say so and push back** rather than raising the ceiling:

> The queue already holds five, which is its cap. Shall I work through these
> first, or should something jump the front with `add` and let the tail fall off?

The cap is not tidiness. A queue with no ceiling is a backlog, and a backlog has
no point at which the work is finished — which is what happened to the freshness
output this whole register replaced. `notes/2026-08-04-automating-re-analysis.md`
argues it directly: the queue is *a selection against a budget*, not a work list
that grows with staleness.

This has already gone wrong once, on 2026-09-09: a request for "five more" on a
full queue was answered by setting `--max 10` and working eleven systems in one
pass. The reading was sound and the batch was not — there was no natural point
to stop and look at what had been produced. The ceiling is now enforced in the
tool rather than left to judgement, because a control that lives only in prose
fails silently, which is a claim this atlas makes about other people's systems.

## The register ages out from under you

`fill` and `rank` restate each row against the report on disk before ranking,
because a register is a measurement from a moment and the reports move on
without it. A row whose report has been re-pinned since the measurement is
marked `repinned-since-measurement` and is not a candidate until the next
`drift_report.py` run measures it. If you see that note on stderr, it is working
— but a register more than a few days old should be rebuilt rather than
reconciled.

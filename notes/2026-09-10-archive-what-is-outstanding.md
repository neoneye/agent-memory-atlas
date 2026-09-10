# The archive: what exists, and what it still needs to run without a person driving it

**Status:** the fork is done; the automation around it is not.
**Origin:** `Renkasha/Sovereign` was deleted before anyone noticed, taking a
report's entire evidence base with it. 396 of 397 cited repositories are now
forked into [agent-memory-atlas-archive](https://github.com/agent-memory-atlas-archive);
the 397th is the one that proved the need.

## What exists

| Piece | What it does |
| --- | --- |
| `scripts/archive_fork.py` | Forks every cited repository as `<owner>--<repo>`, all branches. Idempotent, resumable, `--until-done`. |
| `scripts/archive_sync.py` | Fast-forwards each fork; on divergence saves the old head as `agent-memory-atlas-archive/<yyyy-mm-dd-hh-mm-ss>` first. |
| `scripts/archive-extra-repos.txt` | Hand-curated helper repositories, with the reasoning for what was left out. |
| `archive_name:` in every report | The fork's path under the archive org. Rendered as an "Archived fork" pill beside Source and Analyzed revision. |
| `scripts/check_archive_names.py` | Re-derives that field from `source_url` and fails the build on a disagreement. Offline. |

## The gap that matters most: a pinned commit is reachable, not held

This is the one to fix first, because it undercuts the reason the archive exists.

A fork copies *branches*. What every report actually depends on is a *commit* —
and seven of the atlas's pins are not on any branch of their upstream, because
the project force-pushed or rebased after the reading.

Those commits do resolve in the forks today. Checked on 2026-09-10:

```sh
# otis: the pin a fresh clone cannot reach
curl -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/agent-memory-atlas-archive/TrianglLabs--otis/commits/39e98023104d89a22e89b9cb534f7f681229cc1e
# 200
```

They resolve because GitHub serves a commit by SHA anywhere in a fork network as
long as *something* in that network still holds it. That is a property of
GitHub's storage, not a promise to us: nothing in the archive references those
commits, so the archive's claim on them depends on the upstream network keeping
them alive — which is the dependency the archive was built to remove.

**The fix is small.** For each report, create a ref in its fork pointing at the
pinned revision — a tag is the natural shape:

```
refs/tags/atlas/<revision>        or   refs/tags/atlas-pin-<yyyy-mm-dd>
```

One `POST /git/refs` per pin, no cloning, and the commit stops being
reachable-by-grace and becomes referenced. It also makes the archive
self-describing: the tags in a fork are exactly the commits the atlas ever cited.

Until that exists, the honest statement is: **the archive holds every branch of
396 projects, and relies on GitHub's fork network for the orphaned pins.**

## 1. A new system gets analyzed → it should get a fork

What already forces the issue: `check_archive_names.py` fails the build if a new
report has no `archive_name`, so a report cannot ship without at least *claiming*
a fork.

What is missing:

- **The scaffold does not fill it in.** `scaffold_report.py` knows `source_url`
  and could emit `archive_name` by the same one-line rule the checker uses.
  Without that, every new report starts with a build failure that has to be
  fixed by hand — annoying, and it trains the writer to paste a value rather
  than run the fork.
- **The `add-memory-system` skill does not fork.** It should end with
  `python3 scripts/archive_fork.py --only <owner>/<repo>` beside the build and
  the commit. One repository takes seconds and does not touch the rate limit.
- **Nothing verifies the fork is really there.** The build check is offline by
  design — it compares two strings in one file. A report can therefore claim an
  archive that does not exist. That check needs a network and belongs in the
  same CI job as the sync (below), not in `npm test`.

## 2. A daily sync, as CI

`archive_sync.py` is written and tested against a staged divergence. Running it
on a schedule needs three things it does not have.

**Credentials, and this is the real blocker.** A workflow's built-in
`GITHUB_TOKEN` is scoped to the repository it runs in; it cannot write to
another organisation. The sync needs either a fine-grained PAT with contents
write on `agent-memory-atlas-archive`, or — better, because it does not expire
with a person — a GitHub App installed on that org, with the private key in
repository secrets. Until one exists, this cannot be scheduled at all.

**A decision about what failure means.** `freshness.yml` already settled the
principle for drift: ordinary movement does not fail, losing the ability to check
does. The same split applies here. A fork that fast-forwarded is routine. A fork
that could *not* be updated means the archive is not what the reports say it is,
and should go red. `upstream-gone` should not — that is the archive working.

**Somewhere for the output to live.** The sync writes
`scripts/state/archive-sync.jsonl`, which is gitignored. A scheduled run should
keep it as a 90-day artifact the way the drift register does, so one week's
result can be diffed against the next — that is how a force-push gets noticed at
all.

Cost is not a concern: 396 forks at roughly three reads each is ~1,200 requests
against a 5,000/hour budget, with writes only on divergence. Daily is affordable;
so is hourly.

**And a caveat worth stating plainly**: the divergence path has been tested only
against a force-push I staged myself. It has never run against a real one in the
wild. The first scheduled run over 396 forks is where that gets tested, and it
should be watched rather than trusted.

## 3. Re-analysis → what actually needs to happen

Mostly nothing, with two exceptions that are easy to miss.

**A re-pin changes `revision`, not `source_url`,** so `archive_name` does not
move and the checker stays quiet. Correct.

**But the newly pinned commit has the same problem as the old ones.** If the
re-read pinned a commit that upstream later rewrites away, the archive holds it
only through the fork network. This is the same gap as above and the same fix:
tag the pin at re-analysis time. Until the tagging exists, a re-pin should be
followed by `archive_sync.py --only <owner>/<repo>`, which at least brings the
fork's default branch up to a state that contains the new pin.

**A rename breaks the derivation, and this is the sharp edge.** The
`reanalyze-memory-system` skill's rename convention updates `source_name`,
`source_url` and `revision_url`. `archive_name` is derived from `source_url`, so
it changes too — but the fork already exists under the *old* derived name, and
GitHub will not retroactively rename it. The checker will then fail on a report
that is otherwise correct.

Three ways out, and the choice has not been made:

1. **Rename the fork** to match, via `PATCH /repos/{org}/{name}`. Keeps the rule
   simple, breaks any link anyone saved to the old fork name.
2. **Stop deriving.** Treat `archive_name` as an identity fixed at first fork,
   like the report slug — which the atlas already treats as immutable because
   changing it breaks a published URL. The checker becomes a uniqueness-and-
   existence check rather than a derivation check.
3. **Allow an explicit override** where the derivation and the fork disagree,
   the way `archive_name: ""` already handles the un-archivable case.

Option 2 is most consistent with how this repository already treats slugs, and it
is the one to take unless someone argues otherwise. Twelve repositories in the
corpus have already been renamed since their reports were written, so this is not
hypothetical — it is just not triggered yet, because those reports still carry
the pre-rename `source_url`.

## Suggested order

1. **Tag the pins.** It closes the gap the archive exists to close, it is one API
   call per report, and it can run today with the token already in use.
2. **Decide the rename rule** (option 2 above) and adjust `check_archive_names.py`.
   Cheap now, painful once a rename lands.
3. **Get a credential for the org** — App or PAT — because nothing scheduled can
   happen without it.
4. **Add the sync workflow**, failing on update failures and not on
   `upstream-gone`, keeping the ledger as an artifact.
5. **Wire the fork into `add-memory-system`** and have the scaffold emit
   `archive_name`.

Steps 1 and 2 are worth doing whether or not 3 through 5 ever happen.

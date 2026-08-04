# Automating re-analysis, and why stars belong in the scheduler and nowhere else

**Status:** proposal, nothing built. Written after a day of six first readings and
four re-readings, which is the sample it argues from.
**Origin:** the corpus passed 147 reports and manual re-reading stopped scaling.

## The arithmetic that forces this

Every report is pinned, which is what makes it auditable and what makes it go
quietly stale. At 147 systems, "re-read everything periodically" is not a plan —
today's four re-reads took most of a working session between them, and three of
the four were prompted by a person rather than found by a process.

So the question is not *how do we re-read everything*. It is **which eight
reports this month**, on a fixed budget, and what a machine can do to make each
one cheaper. Everything below treats the queue as a selection against a compute
budget rather than a work list that grows with staleness.

## What already exists — do not rebuild it

`scripts/check_freshness.py` is most of the detection layer. Per report it reads
`source_url`, `revision` and `analyzed_at`, resolves the default branch, and
emits `--json` rows carrying `commits_since`, `diverged_by` and a status. It
already handles the case that cost this project a wrong claim once: a pin can be
**orphaned** by a force-push rather than merely old, which is invisible in a
commit count, and the script checks reachability separately.

What it does not do is decide anything. It produces a list sorted by nothing in
particular, which is why its output has been read a handful of times and acted on
less.

**The gap is prioritisation and evidence-gathering, not detection.** That is
where the work should go.

One free win: the repository metadata call it already makes returns
`stargazers_count`, `pushed_at`, `archived` and `open_issues_count` in the same
response. Collecting them costs nothing extra.

## The stars idea, taken seriously

The instinct is right and worth stating precisely: **a report about a small
active project is more likely to be wrong soon, and more likely to change
something, than a report about a large one.**

Today's sample supports it, for whatever nine data points are worth. The three
projects that acted on a report did so within hours, and all three are small.
The large one in the batch moved eight commits on its own roadmap, untouched by
anything the atlas said. That is one day, and it is consistent with the obvious
mechanism: a maintainer with 40 stars reads an outside review closely because
outside reviews are rare; a maintainer with 40,000 has a triage queue.

### The firewall that has to come first

This project has a standing rule that **stars are never evidence in a report** —
popularity is not a maturity signal and the atlas judges mechanism. A scheduler
that ranks on stars does not violate that rule, because *where to look* and *what
is true* are different questions. But the two will be adjacent in the same
codebase for the first time, and the failure is easy to picture: a scheduling
field lands in report frontmatter "for convenience", and six months later a
sentence says "a widely adopted system".

So, as a hard constraint on anything built here:

- Scheduling signals live in `scripts/state/`, never in report frontmatter.
- No generated report text may read them.
- The queue output names *why* a report was picked in scheduler vocabulary
  ("42 commits since pin, 3 touching appendix files"), never in evidence
  vocabulary.

If that is not enforceable with a check, the star term should be dropped rather
than trusted.

### The best signal is the one that measures it directly

**A maintainer who has turned up in the atlas's Discord is priority 1, and this
should outrank drift rather than add to it.**

Every other input on this page is a proxy for engagement. This one is engagement,
observed. Someone who followed `discord.html` and joined has self-selected as
willing to read a report about their project and argue with it, which is exactly
the population where a re-read pays — today's three responding maintainers all
demonstrated that within hours. It is also the cheapest possible measurement:
membership is a fact somebody already knows, not a number that has to be
inferred from a proxy that correlates with it badly.

The same tier should hold anyone who has **responded to a report before**, by any
channel — an issue, a PR, an email, a correction. That is the same property with
a longer evidence trail, and today produced four such maintainers.

So the tiers are:

| Tier | Membership | Cadence |
| --- | --- | --- |
| **1** | Owner in the Discord, or has responded to a report before | Check every run; re-read on any appendix-touching change — still subject to the cadence cap and the queue size below |
| **2** | Everything not in 1 or 3 | Ranked by the score below |
| **3** | `archived`, or upstream gone | Never, until that changes |

**Tier 1 does not exempt anyone from the budget.** An engaged maintainer who also
ships daily would otherwise reintroduce exactly the problem the churn section
solves — the tier decides *ordering*, never *how often*, and the per-repo cadence
cap and the fixed queue size both still apply. Priority means first in line, not
unlimited.

Three things to get right before building it.

**It is personal data, and this repository is published.** Mapping a Discord
member to a GitHub owner to a report slug is compiling identity across sources —
the thing this atlas criticises systems for doing carelessly. So: the mapping
lives in `scripts/state/`, which is `.gitignore`d and never published; it stores a
repo slug and a boolean, not a Discord handle, a user id or anything that
identifies a person; and it never reaches a report, a queue printout that gets
pasted anywhere, or the site. If a tier-1 pick has to be explained in public, the
reason is "engaged maintainer", not who or where.

**It is a hand-maintained list, which this repository has been bitten by.** Three
entries in the repositories-inspected list drifted precisely because they were
hand-edited in one file and derived nowhere, and `check_inspected_pins.py` exists
because of it. A membership list has no derivable source at all, so it needs the
weaker version of the same discipline: a date on every entry, and a rule that an
entry older than some months is re-confirmed or drops to tier 2. A stale tier-1
list is worse than none, because it silently starves the queue of the projects
that would actually engage.

**It is an editorial choice with a cost, and should be made deliberately.**
Prioritising maintainers who show up concentrates the atlas's attention on
projects whose authors engage, and quietly deprioritises good quiet ones. That is
defensible — a re-read that produces a fix is worth more than one that produces
nothing — but it is a bias being chosen, not a neutral optimisation, and it
should be written down where a reader of the atlas can see it rather than living
only in a scheduler.

### Stars are a weak proxy for what you actually want

What the idea is really reaching for is **responsiveness** and **rate of
mechanism change**. Stars correlate with both, badly and with a long tail.
Several better signals are already free once a repo is cloned or once the
metadata call is made:

| Signal | Where from | Why it beats stars |
| --- | --- | --- |
| Commits since pin | already computed | Direct measure of drift — but see the churn section: a *large* count is a reason to damp, not to prioritise |
| **Commits touching the report's appendix files** | `git diff --stat <pin>..HEAD -- <appendix paths>` | Separates a docs release from a mechanism change. The memU re-read found the appendix diff *empty* while a whole subsystem arrived beside it — so this is a strong positive signal and a weak negative one |
| **Discord membership / prior response** | hand-recorded, see above | Measures engagement directly instead of proxying it — this is tier 1, not a term in the score |
| Days since `pushed_at` | metadata call | Distinguishes small-and-active from small-and-abandoned, which stars cannot |
| `archived` | metadata call | A hard stop; an archived repo never needs re-reading again |

Stars belong in the mix as a **mild damping prior** on tier 2, not as the driver,
and they should not apply to tier 1 at all — a maintainer who turns up is a
maintainer who turns up whether the project has 40 stars or 40,000. Concretely:
score on drift and mechanism-touch, then divide by `log10(stars + 10)` so the
term is a nudge across two orders of magnitude rather than a cliff. A 40-star
project and a 400-star project should differ a little; a 400-star and a
40,000-star project should differ noticeably; nothing should be unreachable
because it is popular.

The prior should also decay out of the model. Once `responded_to_report` is
observed for a project, that observation is better than any proxy and should
dominate the star term for that repo permanently.

## Churn is a cost, not a signal — and this is where the compute goes

The obvious scheduler sorts by commits-since-pin and re-reads the most-changed
first. On a personal machine with finite compute that is the **worst** rule
available, because the projects it puts at the top are the ones whose re-reads go
stale fastest. OpenClaw ships continuously; a re-read finished on Tuesday
describes a commit nobody is running by Friday. Chasing it is a treadmill that
consumes the whole budget and leaves the corpus no more accurate than before.

So velocity belongs in the **denominator**. What is worth buying is not *most
changed* — it is *most likely that one re-read produces a correction that stays
true for a while*.

Concretely, prefer a **re-read half-life** term: divide by the project's recent
commit cadence, so a repo landing 200 commits a month is damped hard and a repo
landing four is not. The same arithmetic that damps stars damps churn, and for a
better reason — the star penalty is a guess about attention, the churn penalty is
a direct estimate of how long the output survives.

### Separate the two budgets, because only one of them is expensive

The machine is not occupied by *checking* fast repos. It is occupied by
*re-reading* them. Those are different orders of magnitude and should have
different budgets:

| | What it costs | Budget |
| --- | --- | --- |
| **Detection** | one `git ls-remote` per repo — no clone, no working tree, no token, milliseconds | Run over all 147 every time; it is free |
| **Triage** | shallow fetch + `git diff --stat <pin>..HEAD -- <appendix paths>` | Only for repos whose head SHA moved |
| **Re-read** | full clone, install, run demos, read code, write | **Hard cap of N per run**, chosen by how much time you are willing to give it |

`git ls-remote <url> HEAD` answers "did anything move" without downloading the
repository. Nothing needs cloning until a repo has both moved *and* cleared the
score, which means a project shipping fifty commits a week costs one network
round-trip a week unless it earns a slot.

### The appendix filter is what stops fast repos eating the budget

Today's memU re-read is the case for this. Eight commits had landed, and the
three files carrying the mechanism — the models, the retrieval mixin, the backend
protocol — were **byte-identical** to the pin. A whole telemetry subsystem had
arrived beside them, which is why that read was worth doing, but the *mechanism*
diff was empty.

High commit counts are usually docs, CI, dependency bumps and release chores. So
after detection, the cheap gate is: diff only the paths the report's own appendix
names. An empty appendix diff on a fast-moving repo is the common case and costs
one shallow fetch to establish.

The honest caveat, from that same read: an empty appendix diff is **strong
evidence the mechanism is unchanged and weak evidence nothing happened**, because
a new subsystem lives in files no existing appendix lists. So the rule is "empty
appendix diff → drop to a cheap commit-subject scan, not → skip entirely", and
the scan is a `git log --oneline` a person reads in ten seconds.

### Two blunt controls worth having anyway

**A per-repo cadence cap.** No system gets re-read more than once every N weeks
regardless of score. This bounds OpenClaw by construction and needs no tuning; it
is the crudest control here and probably the most effective.

**A fixed queue size.** The run picks the top N and stops — the queue is a
selection problem against a budget, not a work list that grows with staleness.
If 60 systems are stale and N is 8, the output is 8. A backlog that is allowed to
grow is a backlog that gets abandoned, and the freshness script's current output
is already an example: a list sorted by nothing, long enough that acting on it
never starts.

### And an editorial answer, not only a scheduling one

For a project that ships daily, the right response may be to re-read it *rarely
and deliberately* rather than to chase it — and to make the pin date do the work
instead. Every report already carries `analyzed_at` and a commit link. A reader
who knows a report describes a fast-moving project at a stated commit is not
misled; a reader who assumes currency is. That is a presentation fix, and it is
considerably cheaper than compute.

## The other half: cost, not just probability

The sharpest scheduling lesson from today came from re-reading Provem, and it is
about the denominator.

Re-verifying Provem cost **one command** — it ships `verify_repro.sh`, which
re-derives every published number and asserts it, so confirming that nothing had
regressed was a single invocation returning `VERIFY OK (25 assertions)`. Every
other re-read that day required re-executing a bespoke demonstration by hand.

So the queue should rank on **expected value per unit cost**, not expected value.
A cheap-to-verify report is worth re-checking on thin evidence of change,
precisely because being wrong about the schedule costs almost nothing. An
expensive one needs a stronger signal before it earns a slot.

Cost is estimable without judgement: does the project ship a runnable gate
(`npm test`, `pytest`, a named verify script) that exits non-zero on drift? Does
the atlas have a saved demonstration for it? Is a service required? Those three
questions sort the corpus into cheap, medium and expensive well enough to
schedule with.

## Build this first: save the demonstration

This is the highest-value structural change and it is not automation at all.

The memsem re-read is the case. Its maintainer fixed what the report described,
and the commit subject — *"valeur rejetée non réinstaurable d'un coup"*, a
rejected value is not reinstatable in one go — was **exactly true**. A reader who
stopped there would have recorded the finding as closed. Re-running the original
demonstration instead showed the threshold had moved from one repetition to
three, and that an ordinary correction is still archived.

The rule that came out of it: **when an upstream responds, re-execute the
demonstration, not the diff.** A maintainer describing what they changed is not
making a claim about what remains.

An automated re-read can diff, and can run the project's own tests. It cannot
re-run a demonstration that exists only in a transcript. So:

> Whenever a report establishes a mechanism claim by *running* something, the
> script goes in `demos/<slug>/` beside the report, with the observed output
> committed next to it.

Today that would have captured the memsem resurrection and pinning tests, the
Perseus mean recomputation, the Argo credential-boundary extraction, and the
Cambium self-application runs. Four of the six systems read today would now have
a re-runnable artifact, and the fifth (Provem) ships its own.

This also fixes something the atlas currently gets away with. A demonstration
described in prose is a claim; a demonstration committed with its output is
evidence, and the difference is exactly the one the
[benchmarks page](../content/benchmarks.md) spends its length on. The atlas
should meet its own standard.

## Three outcomes, not one

"Re-read" is too coarse to automate against. The re-analysis workflow already
names three shapes, and the automation should route to them:

1. **Nothing moved.** Re-pin, update the inspected list, one History line. This
   is mechanical and is the only tier a bot should complete unattended — and only
   when the appendix diff is empty *and* a saved demonstration still passes.
2. **A published claim went stale.** A saved demonstration now fails, or the
   appendix diff is non-empty. Bot gathers evidence and opens a work item; a
   person writes.
3. **The context changed.** New subsystem, new entry point, nothing the appendix
   names. Only detectable from commit subjects and the file list, and the least
   automatable — flag for a human read.

Tier 1 is worth automating because it is most of the corpus most of the time and
it is pure bookkeeping. Tiers 2 and 3 should produce a *briefing*, never prose.

## What must stay manual, and why

**No generated report text.** The atlas's entire value is that claims were
checked by someone who could be wrong and could be corrected. Two of today's
findings were errors caught by maintainers — one a truncated listing that read as
an absence, one a count stated more strongly than it was established. Both came
from a process with a person in it who could be told they were wrong.

An automated writer would reproduce those failure modes at 147× the rate and with
no one to correct. Automate the detection, the diffing, the demonstration
re-runs, the briefing. Stop there.

## Hazards this creates

Worth writing down now, because the scheduler is itself a check that can go
stale — and today produced a lesson about exactly that.

- **A queue nobody reads is `CLAIMS-AUDIT.md`'s designated command.** Perseus
  Vault documents a verification command, calls it authoritative, and its count
  drifted anyway, because a command in a Markdown file runs when somebody
  remembers. If the queue is not wired into something that runs, it is a comment.
- **Scoring drift.** If the star term or the weights are tuned once and never
  revisited, the queue quietly encodes last quarter's beliefs. The scheduler
  should log *why* it picked each item so its judgement is auditable, and should
  be re-derived, not hand-edited.
- **Rate limits and hanging.** The freshness script makes three API calls per
  report; at 147 systems that is ~441 calls, over the anonymous limit of 60/hour.
  This must run as a batch job with a token, never inline in a working session —
  polling upstreams interactively has displaced actual writing before.
- **Silent skips.** Whatever the runner does, "checked nothing" must be a
  distinct outcome from "everything current". That is Cambium's best idea and
  this proposal should steal it directly.

## Suggested order

1. **`demos/<slug>/` convention**, and backfill today's six. No automation
   required; highest value; makes everything below possible.
2. **Split detection from triage.** `git ls-remote` over all 147 to find what
   moved — no clones — then shallow-fetch and diff the appendix paths only for
   those that did. Collect `stargazers_count`, `pushed_at`, `archived` and a
   commit-cadence estimate on the same pass. Persist to
   `scripts/state/freshness.json`.
3. **A scoring script** emitting a ranked queue with a stated reason per row, cut
   to a fixed N. Weights in one place; star term log-damped; churn in the
   denominator; a per-repo cadence cap; `archived` as a hard filter.
4. **Tier-1 automation** — re-pin and History line when the appendix diff is
   empty and the saved demo passes.
5. **The tier-1 list** — a `.gitignore`d slug-to-boolean map in `scripts/state/`,
   seeded from Discord membership and from the maintainers who have already
   responded, with a date per entry and a re-confirmation rule. Cheap enough to
   do by hand today; the ordering above puts it last only because steps 1–2 are
   prerequisites for acting on it, not because it matters least.

Steps 1 and 2 are worth doing regardless of whether 3–5 ever happen. Step 1 in
particular is a debt the atlas already owes: it asks every system it reviews to
commit the artifact behind its claims, and does not yet do so itself.

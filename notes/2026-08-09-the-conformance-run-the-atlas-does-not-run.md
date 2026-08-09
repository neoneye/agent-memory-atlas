# The conformance run the atlas does not run — inverting the burden without inventing a certificate

**Status:** proposed. Revises step 2 of the
[executable eval suite](2026-07-28-executable-eval-suite.md), which is the only
part of that note that is now unbuildable.
**Origin:** a Codex conversation (2026-08-09) on the atlas's influence, which
recommended converting the rubric into "a runnable conformance suite". The
recommendation is right about the destination and wrong about who runs it. The
operator constraint that decided the shape is stated below, because it is
permanent and a plan that waits for it to lift is not a plan.

**Sequencing:** phases 2, 3 and 4 of
[the phased program](2026-08-09-a-phased-program-and-where-to-abandon-it.md).
Phase 2 — validating the suite against the kernel and its broken arm — is the
go/no-go for everything here, and it is the one place local execution is safe,
because the code under test is this project's own. Phase 3 is gated on reading an
adapter producing something the log did not say.

## What this revises

The eval-suite note has three sequencing steps. Step 1 — build the harness
against the [kernel](2026-07-28-atlas-kernel-proposal.md), where the passing and
failing answers are known in advance — stands unchanged and is still the only
way to know the suite works. Step 2 was:

> run it against the locally-runnable subset

That is off the table, and its companion rejection now needs revisiting:

> **Do not:** publish a package and wait for framework authors to implement
> against it, or claim it as a standard. [...] A `pip install` that nobody runs
> is the benchmarks page with more steps.

The reasoning was sound on 28 July. Two things have changed since: one that
closes step 2, and one that reopens the rejection.

## The constraint is not a preference

Running the deletion sequence against a system means installing that system.
Across a corpus of 238 repositories, on a personal machine, that is a standing
invitation to a supply-chain compromise — and this project already agrees,
because it built a tool that says so. `scripts/screen_repo.py` and the
`screen-repository` skill exist to report auto-executing hooks, build-time
execution and unpinned dependency surfaces **without executing the tree**. The
Perseus reading records the discipline in practice: two auto-run surfaces, one
build-time exec, eight unpinned surfaces, "nothing was built or executed from
the checkout".

A plan whose second step is *execute the checkouts* contradicts the tool the
project built to avoid executing checkouts. Compute is the smaller half of the
objection and the easier one to state: standing up a Rust crate, a Postgres
service, an RL rig and a Minecraft agent is per-system, unbounded, and paid for
out of the same finite budget as writing.

So step 2 is not deferred. It is closed.

## The objection that has since been tested

"A `pip install` that nobody runs." That predicted a population's behaviour, and
the population has since behaved. Three projects built an executable
self-evaluation without being asked to:

- **Verel** ships `memory/rubric.py` — a live behavioural probe per atlas
  capability, run against an in-memory store, printing the criterion, the
  implementing file, and a **proof string** naming what actually happened.
- **Perseus Vault** ships the scorecard in `#878`: blocking on any pull request
  touching vault behaviour, `release_ready` demanding accuracy of exactly 1.0
  over a committed 24-case manifest, with every category required — long-horizon
  recall, contradiction and supersession, shared-memory visibility, adversarial
  contamination, temporal validity, scope validity, provenance. That list is
  close to the acceptance suite this atlas publishes and has never run.
- **Daimon** ships `research/experiments/recall-replay-ab/`: two arms replayed
  against one time-filtered snapshot, a side-blind judge on disagreements, a
  `verify.py` that asserts the instrument's own determinism — and it has been
  used to kill a shipped feature, twice recorded as `measured and refuted`.

What this is evidence of, stated narrowly: three self-selected projects that
already care about being checkable did the work unprompted. It is not evidence
about the other 235. But the rejected claim was specifically that nobody would
run it, and three ran something of the same shape with no format to fill in.

## The design problem

A self-reported pass is worth nothing by default, and saying otherwise would
undo the only thing this project has. The atlas's method is that a claim is
checked against code at a pinned commit. A submitted green tick is a claim with
no artifact behind it — the same object as a README's performance number, which
this corpus is full of and this project routinely declines to repeat.

So the requirements below exist for exactly one purpose: to convert a run the
atlas did not perform into an artifact the atlas can read **statically, at a
pin**, which is the operation it has already performed 238 times.

### Four requirements for a submission

1. **It ran in the project's own public CI, and the log is addressable.** Not a
   pasted terminal transcript. The atlas checks that a job exists, that it ran on
   the submitted commit, and that it exited the way the submission says.

2. **It is pinned to a commit the atlas can read.** Same discipline as a report.
   A submission against a branch name is a submission about nothing.

3. **The adapter is committed in that repository.** This is the load-bearing
   requirement. The dominant failure mode will not be a maintainer lying; it will
   be an adapter that passes *by not testing* — a `forget()` that returns before
   background jobs settle, `leak_probes` that query only the path deletion
   already covers, a scope the test supplies as an argument where the point of
   `scope.caller_cannot_widen` is that authentication must supply it.
   `.agents/protocol/tests.yaml` already anticipates this class: every one of its
   twenty entries states what a pass does **not** prove. Under this design the
   adapter, not the result, is the object of review.

4. **Every test ships a negative control in the same job.** The mutant
   configuration in which the test must fail, run alongside the real one and
   reported failing. This is Daimon's placebo arm turned into a submission rule,
   and it is the requirement that separates a suite which asserts something from
   a suite which asserts nothing. This project has published the failure on
   itself: the [count-claim checker](2026-08-06-the-count-claim-checker.md) grew
   a branch to catch a class of stale numerator and shipped that branch with no
   control of its own.

Plus one thing to copy rather than require, from Verel: the **proof string**. A
boolean tells you the suite ran; a sentence saying "rejected value keyed in
ledger; re-assert after supersede stays un-promotable" tells you it tested the
right thing.

## What the atlas actually does with a submission

Read the adapter at the pin. Read the log. Say in prose whether the test tested
the thing it names. That is the existing review operation with a narrower object,
and it belongs in the report's section 10 and its `## History`, where the reader
already looks for what was and was not run.

It does **not** produce a column. A Pass/Fail matrix covering the systems whose
maintainers happened to respond reads as a comparison of systems when it is a
comparison of maintainer availability, and the eval-suite note already rejected
the sparse-matrix version for that reason.

## The asymmetry that keeps this from becoming a scoreboard

**A submission can only ever be evidence for a mechanism, never against one.**
A system with no submission is a system whose maintainer did not send one. It is
not a system that failed, and the atlas must never render it as one — no empty
cell, no ❌, no "not verified" that a reader will parse as "verified absent".

That asymmetry is what makes the whole thing safe to publish, and it should be
written into the format's own header the way `not_proven` is written into every
entry in `tests.yaml`.

## What stays rejected

Unchanged from the eval-suite note, and reaffirmed rather than reconsidered:

- **No "Passed Atlas Evals" badge.** Badges get gamed and turn each strict
  definition into a thing to argue about rather than check.
- **No leaderboard, no provisional scores tagged at maintainers.**
- **No conformance statement.** `AGENTS.md` says this project certifies nothing,
  and the [protocol note](2026-08-07-the-atlas-as-an-agent-protocol.md) declined
  the word "conformance" on precedent. A submissions page says what a maintainer
  ran and what the atlas could see in the adapter. Naming it a certificate would
  be claiming the thing the burden was inverted to avoid claiming.

## Build order, and why inviting last

1. **The harness against the kernel.** Unchanged from the eval-suite note. A
   suite validated against a system whose answers are known in advance is the
   only kind whose green means anything.
2. **The submission format**, next to
   [`.agents/protocol/build-brief.md`](../.agents/protocol/build-brief.md): test
   id from `tests.yaml`, commit, CI log URL, adapter path, negative-control
   result, proof string. It is small — the ids and the `not_proven` clauses are
   already written.
3. **One worked example, produced with a maintainer who already has the CI.**
   Perseus's `#878` is the closest existing artifact; Verel's `rubric.py` is
   already the right shape and predates the format.
4. **Only then invite generally.**

The risk of inviting first is a format nobody can fill, which is the failure the
28 July rejection was actually about.

## Open question

Whether the atlas reads a submission when it arrives or at the next re-analysis.
Reading on arrival turns the project into a queue with an implied response time,
which one person cannot hold. Reading at re-analysis keeps it a corpus and puts
the finding where the reader already looks. Lean re-analysis — but that means a
submission can sit unread for weeks, and the format should say so rather than
let a maintainer infer a service level that does not exist.

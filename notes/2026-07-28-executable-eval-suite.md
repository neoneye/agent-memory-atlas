# Executable eval suite — the deletion and contradiction tests as runnable code

**Status:** specified in prose, not built
**Origin:** proposed as "the Jepsen of AI Memory" (Gemini, 2026-07-28) and as a
"living test harness" (Kimi). Both overreach; the useful core survives.

## What already exists

The [benchmarks page](../content/benchmarks.md) specifies two tests in enough
detail to implement:

- **The ten-step deletion sequence** (§6) with a six-method adapter —
  `write`, `settle`, `prompt_prefix`, `forget`, `run_background_jobs`,
  `leak_probes`, `audit_entries` — and a pytest function that is checked to parse
  as Python.
- **The contradiction test** (§7): five case shapes (replacement, polarity flip,
  retraction, partial supersession, bounded validity) scored on five dimensions
  (answer, retrieval hygiene, durability, history, derived reach).

Both live as fenced code in a Markdown page. Neither has been run against
anything.

**Update, 28 July 2026: somebody else did it first, from the other side.** Verel
ships `memory/rubric.py`, which runs a live behavioural probe per atlas
capability against an in-memory store and prints the criterion, the implementing
file, and what the probe demonstrated. It is not this proposal — it is a system
grading *itself*, where this proposes an adapter the atlas runs against *many*
systems — but it settles the feasibility question that this note treats as open.
The probes are small, dependency-free, and take an entire capability from "we
have a function for that" to "here is the laundering sequence walked end to end".

Two things worth stealing from it, whenever this suite gets built:

- **The `proof` string.** Each result carries not just pass/fail but a sentence
  stating what actually happened — "rejected value keyed in ledger=True;
  re-assert after supersede stays un-promotable=True". A boolean tells you the
  suite ran; that sentence tells you the suite tested the right thing.
- **Probe the packaging, not just the code.** Running Verel's rubric from an
  installed wheel scores 6/7, from a source checkout 7/7, because one criterion
  needs committed test files that the wheel excludes. Any adapter this atlas
  writes will hit the same class of problem, and "how was it installed" belongs
  in the harness rather than in a footnote.

## The proposal, corrected

**Do:** move the harness into the repository as real code with a reference
adapter, and run it against the subset of systems that are locally runnable
without paid API keys. Publish "N of 56 tested, here is which and why not the
rest."

**Do not:** publish a package and wait for framework authors to implement against
it, or claim it as a standard. Jepsen's authority came from Kyle Kingsbury
*running the tests and publishing damning results with reproductions*, not from
shipping a library. A `pip install` that nobody runs is the benchmarks page with
more steps.

**Do not:** run one test against every system and publish a Pass/Fail column with
holes. The 56 span Rust crates, Postgres services, hosted vector APIs, an RL
training rig and a Minecraft agent; several cannot store a byte without a paid
key. A column covering eight of 56 reads as a comparison and is worse than
honest static review.

## Why the subset framing matters

The atlas's credibility rests on never claiming more than it checked. "We tested
the eleven systems that run locally, here are the results, here is the list we
could not run and the specific blocker for each" is a stronger artifact than a
sparse matrix, and it is the only version that survives the atlas's own standards.

## Sequencing

1. Build the harness against the [kernel](2026-07-28-atlas-kernel-proposal.md),
   where both the passing and failing cases are known in advance. A test suite
   validated against a system whose answer you already know is the only way to
   know the suite works.
2. Then run it against the locally-runnable subset.
3. Publish the results *and the exclusion list with reasons*, as a page, not a
   badge.

## Cost

The harness is a day. Standing up each system under test is the real cost and it
is per-system and unbounded — some will take an hour, some will defeat a
reasonable attempt, and recording *that* is part of the result.

## Explicitly rejected

- **A "Passed Atlas Evals" badge.** Badges get gamed, and this atlas has already
  been caught twice on semantic misclassification; a badge turns each strict
  definition into a thing to argue about rather than check.
- **Tagging maintainers with provisional scores** so they compete to clear a ❌.
  It converts a code-grounded review into a leaderboard.

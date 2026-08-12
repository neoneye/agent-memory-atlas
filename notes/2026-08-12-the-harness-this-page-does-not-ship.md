# The harness this page does not ship — the criticism the atlas makes of others, applied to itself

**Status:** proposed. The acknowledgement has landed in
[`benchmarks.md` §9](../content/benchmarks.md); the work has not.
**Origin:** an outside review (Qwen, 2026-08-12) of the benchmarks page. Most of
its structural findings dissolved on inspection — see
[the atlas read without JavaScript](2026-08-12-the-atlas-read-without-javascript.md)
— and this one did not. It is the sharpest criticism the page has received.

## The charge

The benchmarks page faults [FiFA](../content/benchmarks.md) for proposing a
deletion-compliance metric and releasing no code, and
[AOEP-v0](../content/benchmarks.md#aoep) for describing a harness it does not
ship. It then specifies a thirteen-step deletion sequence and a contradiction
test in enough detail to implement, with an adapter contract of `write`,
`settle`, `prompt_prefix`, `forget`, `run_background_jobs`, `leak_probes` and
`audit_entries` — and ships neither.

The review's phrasing was *"tearing down the open-source community for missing
benchmarks while withholding your own theoretical solution"*. That is fair. The
excuse available — that a specification is a contribution and an unrun harness is
a liability — is one FiFA and AOEP could make with equal force.

## What actually distinguishes them, and what does not

Two differences are real and neither is a defence:

- **The atlas publishes no numbers.** FiFA's abstract contradicts its own results
  table; AOEP reports a pilot over seven systems. This page reports nothing,
  which removes the specific failure of an unreproducible headline and does not
  remove the gap.
- **The sequence is written as an adapter contract rather than as a result.** A
  reader can implement seven methods against their own store and get an answer.
  That is a lower bar to clear than a released harness and a higher one than
  prose.

What does *not* distinguish them is intent. "We specified it carefully" is what
every unreleased harness says.

## Proposal

Build the smallest thing that makes the sequence executable, and refuse the
temptation to make it a product.

**Scope.** One Python file, standard library plus `pytest`. No packaging, no
adapters for named systems, no result database. It reads an adapter object the
user supplies and runs the thirteen steps, printing which step failed and what
was still reachable.

**Deliverable shape.**

```text
tools/deletion_sequence/
  sequence.py        # the thirteen steps, one assertion each, no framework
  protocol.py        # the adapter Protocol, typed, with docstrings per method
  example_adapter.py # an adapter over a toy store that PASSES, and one that FAILS
  README.md          # what a pass does not prove
```

**The part that matters most is the failing example.** A harness shipped with
only a passing fixture proves nothing about whether the assertions discriminate;
this atlas has published that criticism of other people's suites
([the negative control](2026-08-08-what-the-negative-eval-mark-actually-counts.md)
argument) and would be repeating their mistake. Ship a deliberately leaky store
that fails steps 5–8, so a reader can see the harness catch something before
they trust it against their own.

**What not to build.** No conformance certificate, no scoreboard, no hosted
runner, no "systems that pass" list. `AGENTS.md` already states this project
certifies nothing, and a harness that produces a badge would make that untrue
without anyone deciding to.

## Sequencing

After, not before,
[which marks could be execution-grounded](2026-08-12-which-marks-could-be-execution-grounded.md).
That note establishes what this project can actually run on a laptop under its
own screening rules; if the answer is narrower than it looks, the harness should
be scoped to what a reader runs rather than what the atlas runs.

## What would change this plan

If somebody else ships an executable thirteen-step sequence first, this becomes a
report on their harness and a citation, not a build. That is the better outcome
and the note should not be read as a claim on the territory.

# An audit layer that shows one trajectory twice

**Status:** done. Not a system report — the subject is not agent memory, and the
[exclusion is recorded in the limitations](../content/overview.md). This note
exists because the *failure shape* is one the atlas already names twice and had
not yet seen in this form.

**Subject:** *Recursive Synthesis for Long-Horizon Terminal Tasks*
([arXiv:2608.05466v1](https://arxiv.org/abs/2608.05466), 5 August 2026, CC BY
4.0) and its
[project site](https://zhongzhi660.github.io/recursive-verified-synthesis-site/),
whose fifth section is an "Audit layer" headed *"Don't just trust our metrics.
Inspect the task change, model trajectory, and rubric decision for the same case
yourself."*

**Method:** the site read directly in a browser, values taken from the live DOM
rather than from prose. Every number below is re-checkable by opening a case and
stepping the turn selector. The paper read from its **LaTeX source**
(`arxiv.org/e-print/2608.05466`, 407,522 bytes, `paper.tex` plus nine section
files), so every paper claim below is quoted from what the authors wrote rather
than from a rendering of it.

**Revised 2026-08-08, same day.** The first version of this note read the paper
through an extraction of the arXiv HTML and got one claim backwards; the source
settled it and the correction is marked in place. It also surfaced a
contradiction in the paper's flagship number that no rendering would have shown.

## What the audit layer promises

Three tabs per case, ten cases: **Task Diff** (source → runtime file changes),
**Trajectory Diff** (*"compare a failed baseline execution with a Harbor
trajectory that received verifier reward 1.0"*), and **Rubric** (the scoring
decision). It is the answer to the obvious objection that synthetic training
data is easy to distrust, and it is the right instinct — publishing the artifact
beside the number is exactly what this atlas asks of everyone else.

## What it contains

**1. The two trajectory columns are the same trajectory.** In case
`jobs-diff-01-3341b098`, every turn where both columns render is byte-identical
— command, response, and observation — through turn 6, including the closing
`<action>done</action>`. Checked again in three more cases; identical at every
turn where both sides have content.

| Case | Baseline turns | Harbor turns | Turns identical where both render |
| --- | ---: | ---: | --- |
| 1 (`jobs-diff-01`) | 6 | 21 | all |
| 2 | 11 | 19 | all sampled (1, 2, 4) |
| 3 | 2 | 17 | all sampled (1, 2) |
| 5 | 5 | 16 | all sampled (1, 2, 4) |

**2. The turns that would explain the reward are empty.** Rendered panel length
per turn, case 1:

```
turns 1–5   2680, 2476, 2686, 2414, 2740   full content
turn 6       594                            the "done"
turns 7–21   413, 413, 413, 414 … 414       Commands / Response / Observation all blank
```

The cutoff lands exactly at the baseline's turn count in every case measured —
case 2's baseline is 11 turns and 12–19 are empty, case 3's is 2 and 3–17 are
empty, case 5's is 5 and 6–16 are empty. The successful trajectory exists as
turn *slots* carrying no data.

The viewer is capable of saying data is missing: the left column prints **"No
Left turn at this index"** past the baseline's end. The right column renders
empty fields instead, so absence reads as an empty turn rather than as absence.

**3. The rubric is a template with scores attached.** Case 1 scores 94.5/100
across five capability profiles. All six A-criteria carry **confidence 86%**,
cite the same evidence — `turn:1 turn:2 turn:3`, on a 21-turn trajectory — and
end in the same generated sentence with the criterion name substituted:

> "This is an evidence-linked deterministic assessment for the selected
> trajectory."

Recommendations are the same mail-merge; anchors are one of two fixed strings. A
scoring surface that calls itself evidence-linked while pointing every criterion
at the same three turns is asserting the property it exists to demonstrate.

**4. One incidental leak.** The task diff for case 1 is three added lines in
total, one of which is
`docker_image = "/tmp/et_qwen35_9b_train_rollout_sifs/task_000000_3341b098.sif"`
— an absolute `/tmp` path, so the bundle as shown is not reproducible, and a
**9B** model in a train-rollout directory when the paper's model list is
Qwen3.5-27B and Qwen3.5-122B-A10B. Either a smaller model collected rollouts and
is unreported, or the fixture comes from a different run than the paper. A
question, not a finding.

## Why this is not an accusation

The [viewer repository](https://github.com/alexhuang13/viewer) states it ships
*"source code and small fixtures only"*, with Harbor jobs, trajectories and
artifacts kept outside the checkout. So these are fixtures behaving as fixtures.
Nothing here suggests the underlying runs do not exist.

The gap is between what the fixtures are and the sentence they are published
under. *"Don't just trust our metrics — inspect it yourself"* is a claim about
what a reader can verify, and on this data a reader can verify nothing about the
successful run. A fixture that renders as evidence is worse than no audit layer,
because the audit layer is what a sceptical reader is directed to.

## The failure shape, which is why the atlas keeps this

The comparative report already names two versions of this:
[the harness's own output captured as
evidence](../content/overview.md) and [published benchmark numbers without
committed artifacts](../content/overview.md). This is a third: **an audit
surface whose fixtures do not contain the artifact it audits.** It is the most
persuasive of the three, because the first two look like missing work and this
one looks like completed work.

The atlas should read its own surfaces against it. The relevant question is not
"is there an evidence link" but "does following the link reach the thing". The
[capability evidence block](../content/methodology/atlas-rubric.md) added on
2026-08-07 is the atlas's version of the same promise, and its `test: unknown`
values exist precisely so that a record cannot claim a test it does not have.

## What the paper gets right, recorded so this note is not a hit piece

The published figures are internally consistent. Every growth ratio reproduces
from its own medians — commands 40 → 244.5 is 6.1×, solution lines 67 → 374 is
5.6×, CLI tools 17 → 71 is 4.2×, assertions 17 → 57 is 3.4×, instruction length
85 → 122 is 1.4×. The two cost forms agree: `conclusion.tex` says *"approximately
\$50 per 1,000 accepted tasks"* and the abstract says *"roughly \$0.05 per
task"*, which are the same number. The site prints *"These numbers use different
units"* directly under its cost comparison, which is more than most pages do.

## The flagship number disagrees with itself

`tab_rl_benchmark_comparison.tex` gives Qwen3.5-27B-RL as **49.44 / 32.00 /
22.07** with a relative gain row of **+20.00% / +41.16% / +21.93%**, and the
abstract agrees: *"agentic PPO lifts Qwen3.5-27B to 49.44\%, 32.00\%, and
22.07\% … relative gains of 20.0\%, 41.2\%, and 21.9\%"*.

`conclusion.tex` says something else:

> "Qwen3.5-27B-RL reaches 46.07, 32.00, and 22.07 on the three benchmarks,
> corresponding to relative gains of 11.82\%, 41.16\%, and 21.93\% over the base
> model."

Both are internally consistent against the 41.20 base — 49.44/41.20 = 1.2000 and
46.07/41.20 = 1.1182 — so one is a stale draft figure that survived into the
conclusion of a published paper, in the headline cell of the headline result.
The table and abstract agree with each other and with the project site, so the
conclusion is the stale one.

This is the failure the atlas spent 2026-08-06 to 2026-08-08 fixing in its own
prose: a hand-written number sitting beside correct ones, inheriting their
credibility. It is the reason `check_claim_counts.py` exists. Finding it in
someone else's paper the same week is a useful reminder that the class is not
peculiar to this project.

## The alignment metrics, correctly this time

**Correction.** The first version of this note said median requirement coverage
of 0.42 → 0.57 meant *"roughly two fifths of what each verifier checks is still
not stated in its public instruction"*. That is the wrong direction.
`experiments.tex` defines the measurement as *"whether requirements in the public
instruction are represented in executable verifier checks"* — so 0.57 at R15
means roughly **two fifths of what the instruction asks for is never checked**.
That is verifier leniency, not under-specification, and it bears on whether
partial credit means what it says rather than on whether the task is solvable.

The metric that does support the under-specification reading is the other one:
**hidden-check protection rises from 38.2% to 63.5%**, so at the final round
roughly **36.5% of tasks are still unprotected** — the verifier checking things
the instruction does not establish, which is exactly what the contract-validity
gate is supposed to forbid. The paper's own framing of this is that alignment
*improves*, and it does; the residual is what matters, and 36.5% is a large
residual under a gate described as a condition of acceptance.

So the headline difficulty result — DeepSeek-V4-Pro pass@4 falling from 90% at
R₁ to 2.5% at R₁₅ — has an unexcluded alternative explanation. Tasks that
require what was never stated produce the same curve as tasks that are harder.
The alignment audit is the control that would separate them and it does not
clear the residual.

**Neither metric is defined anywhere in the paper.** There is no definition of
"hidden-check protection" or "requirement coverage" in the method, the
experiments or either appendix — they appear as percentages with a figure and a
caption. The two numbers carrying the contract-validity claim are the two the
reader cannot check.

## Three absences, from the source rather than from a rendering

- **No ablation.** The string "ablation" does not appear in the paper. The two
  load-bearing design choices — the diversity caps and the verification gate —
  are supported by stability plots, not by runs with them removed.
- **No limitations section.** The only mention is in a *commented-out* line of
  `introduction.tex` promising that the conclusion "discusses the remaining
  limitations"; the conclusion's one clause is about a high-similarity tail.
- **The release promise is commented out.** `paper.tex` carries
  `% We release all synthesized tasks, sampled trajectories, and trained
  checkpoints.` — struck before publication. What ships is a Hugging Face
  collection and the project site, and the site is the audit layer examined
  above.

**And no 9B model exists in the paper.** DeepSeek-V4-Pro, GPT-5.6-Sol,
Qwen3.5-27B and Qwen3.5-122B-A10B are the complete list across every section and
figure file. The audit fixture's
`/tmp/et_qwen35_9b_train_rollout_sifs/…` path therefore names a rollout model the
paper does not report, which makes the provenance question sharper than it was
when the path was merely an unreproducible one.

## Not a memory system

Recorded here rather than as a report because nothing in it survives a session
with a correctable identity. It is adjacent in one specific way. Accepted tasks
persist across all fifteen rounds with parent lineage and, by the paper's own
description, **no retroactive removal** — a task accepted in R3 against a
verifier later shown under-specified stays in the R1–R15 RL pool and stays in
every descendant's ancestry. That is the
[rejected-value tombstone](../content/patterns/rejected-value-tombstone.md) gap
arriving in a training-data pipeline: the correction cannot propagate backwards
because nothing is keyed on what was wrong.

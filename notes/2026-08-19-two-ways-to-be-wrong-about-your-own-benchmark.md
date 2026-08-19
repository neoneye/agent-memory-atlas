# Two ways to be wrong about your own benchmark, read the same day

**Status:** finding with two instances that are mirror images; feeds the
benchmarks page.
**Origin:** repowise and Gortex, analyzed within an hour of each other. Both are
code-intelligence engines, both publish numbers, both are honest, and they fail
the reader in opposite directions.

## Two axes, not one

The atlas usually asks one question of a published number: *is the artifact
committed?* These two show that is half of it. There are two independent
questions:

1. **Who graded it?** The project, or something the project does not control.
2. **Where is the evidence?** In this repository, or somewhere else.

|  | evidence in the repo | evidence elsewhere |
| --- | --- | --- |
| **graded externally** | the goal | **repowise** |
| **graded by the project** | **Gortex** | the usual bad case |

Neither of these is the usual bad case. Both are visibly trying. They are still
different things to trust.

## repowise: strong grading, absent artifact

The discipline is real and unusual. A 112-instance corpus split 70/42 by
instance id, *"pinned before any of it started"*, with the 42 sealed until the
final measurement. Deterministic grading, no LLM judge. The unflattering
precision column published beside the flattering coverage column — 0.876
coverage at 0.087 precision, by serving 19.2 files. A row headed **we lose**
(indexing, by 22x). Two comparisons labelled "not measured" rather than given a
checkmark, with the reason stated: they would *"rather write 'not measured' than
let a checkmark do a number's job."*

And the harnesses, the pre-registrations and every graded cell live in a
different repository. `docs/BENCHMARKS.md` says so plainly and links there.

So a reading of the repository the atlas pins can establish the *shape* of the
evidence and not the evidence. The claim I can support is about how the
measurement was organised, which is genuinely informative, and is not the same
as having checked it.

## Gortex: present artifact, self-grading

The mirror. `bench/baselines/groundtruth.json` and `queries.json` are right
there in the tree, inspectable, with a comment explaining the metric. Five
benchmark surfaces each carry a headline number, a published table and a "How to
reproduce" block.

Then you open the ground truth. It is **ten queries**, and the expected file
paths were hand-curated *"against the gortex repo"* — the project grading itself
on its own codebase. The timings *"come from a single operator's machine"*,
which the document states in its own opening paragraph.

The surface somebody else would grade is SWE-bench. The harness is fully built
(`cmd/gortex/eval_swebench.go` plus a Python side in `eval/`) and the
reproduction instructions are better than most published results — they demand
the harness commit SHA, the run date, and a per-run directory of per-task JSON
*"so any reviewer can spot-check the count."* The results table reads **Last
run: TBD** and every cell is a dash.

## What to say about each

The temptation is to rank them. Resist it; they are answers to different
questions, and the useful output is a sentence for each that a reader can act
on:

- repowise: *the measurement is well designed and this tree contains the claim
  rather than the proof.*
- Gortex: *the proof is in this tree and the grader is the author; no externally
  graded result is committed.*

Both sentences are about the artifact. Neither says the work was not done.

## The thing worth copying, from Gortex

Shipping a rigorous empty template beats shipping a soft number. `BENCHMARK-SWE.md`
is unpopulated and still useful: it fixes in advance what a result would have to
include to count. A project that writes down its acceptance criteria before it
has a number has made it harder to publish a bad one later.

## For the benchmarks page

The page currently sorts on whether artifacts are committed. It should carry the
two-by-two, because "committed" and "independent" come apart, and the two
systems above are the clean instances of each off-diagonal cell.

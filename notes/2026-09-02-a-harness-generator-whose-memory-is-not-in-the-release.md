# A harness generator whose memory is not in the release

**Status:** a reading, 2 September 2026, of
[arXiv:2608.25593](https://arxiv.org/abs/2608.25593) — *JIT-Agent: Scaling
Harness Intelligence via Just-in-Time Harness Evolution* — and its repository
`bingreeky/JIT` at [`ababa06c2f54d799fd9fbc356e5368f61a452260`](https://github.com/bingreeky/JIT/commit/ababa06c2f54d799fd9fbc356e5368f61a452260).
Filed in the overview's scope section and on the benchmarks page beside the
harness-disclosure paper. No report.

---

## What it is

A 27B model, fine-tuned from Qwen3.6-27B, that is given a task, a tool
registry and some reference material and emits an executable harness for any
off-the-shelf agentic model: `memory.py`, `planning.py`, `action.py`,
`tool_policy.py` and a `prompt.yaml`, against a fixed kernel protocol. A
best-of-three selector picks a candidate — by the meta model's own summed
log-probability over the completion, or by a judge — and the executor runs it.
The repository is MIT, three commits on 26 and 27 August, and ships the
generator, eleven hand-written seed harnesses, every benchmark adapter with its
config and task data, the checkpoint on Hugging Face, and the training set.

The harness thesis this atlas filed on 1 September — that for long-horizon
tasks the harness governs more variance than the model — is here as a
premise rather than a complaint, and the paper's Table 4 is the controlled
comparison that thesis wanted: executor fixed, harness varied, cost beside the
score.

## Where the memory is, and where it is not

The memory module is per task and in-process. The kernel protocol calls it an
*"inside-trial working memory manager"*; `initialize` runs *"once at the start
of each run"*. The eleven seeds cover most of the conversation-window
repertoire — full history, token-triggered summarisation, value-scored sampling
with `[Omitted]` placeholders, a reasoning graph, memory pages, context folding
— and none of them touches disk. That is the same boundary SKILL.state and
Self-GC sit on, and it was settled in one grep.

The thing that persists in the *paper* is the harness bank. Section 5 defines
it as *(task, harness, metrics)* rows with a reward-frontier retention rule and
a per-task reference set retrieved from it, and section 6.6 reports a streaming
mode in which the bank grows across a task sequence and *"finishes above the
static variant"*. The README says it in one line: *"harnesses keep improving at
test time while the generator itself stays frozen."*

In the tree, the bank is a directory constant pointing at the eleven seeds. The
reference set is either the whole description catalogue or three seeds chosen
by `random.sample`. No generated harness is written back, no metric is stored
beside a harness, and `frontier`, `incumbent` and `stream` occur nowhere in the
source. The archive is the paper's memory, and the release does not contain it.

## Three smaller gaps

- Table 2 lists thirteen seeds; the tree holds eleven. ReAct and AOrchestra are
  the absent two.
- The three-stage training pipeline is described and not released. The data it
  consumed is.
- No result file and no run trace is committed. The instrument ships; the
  readings do not. This is a third position beside the two the benchmarks page
  already records — Prime Agent's harness-without-measurement and VISTA's
  measurement-without-harness — and it is the one a reader can most cheaply
  close themselves, at the price of the API calls.

## The rule worth keeping

A generated harness is regenerated only when execution raises. *"A harness that
merely scores low is never repaired, since that would be optimising against the
benchmark."* The seed baselines run with repairs disabled so the number
describes the harness as written. Both are in the runner, not the paper, and
both are the kind of sentence this atlas keeps asking benchmark authors to
write down.

## What this changes for the method

Nothing new. The rule from the five-papers note — when a paper ships code, read
it before placing the paper — earned its keep again: on the abstract alone this
would have been filed as a system with a cross-task archive, and the archive is
the part that is not there.

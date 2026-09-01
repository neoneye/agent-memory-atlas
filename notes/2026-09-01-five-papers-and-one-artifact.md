# Five papers, one artifact

**Status:** an observation with an uncomfortable edge, from the five arXiv papers
read into the atlas between 31 August and 1 September 2026. Four of the five
release nothing that can be run, and the one that argues hardest for disclosure
is among them.

---

## The count

| Paper | Artifact |
| --- | --- |
| [arXiv:2608.19920](https://arxiv.org/abs/2608.19920) — *Learning how to Forget* (sparse-attention fine-tuning) | **`awslabs/keys_values`**, Apache-2.0, readable at a pin |
| [arXiv:2608.18027](https://arxiv.org/abs/2608.18027) — *Chain-of-Experience* | none |
| [arXiv:2608.23642](https://arxiv.org/abs/2608.23642) — *AI Agents Push Humans Out of the Loop* | none, and none is owed — it is a position paper about design and organisational practice |
| [arXiv:2605.23950](https://arxiv.org/abs/2605.23950) — *Stop Comparing LLM Agents Without Disclosing the Harness* | none |
| [arXiv:2608.26263](https://arxiv.org/abs/2608.26263) — *SKILL.state* | none; its headline benchmark, `SkillExecBench`, is the authors' own and unpublished |

One of five ships something a reader can check. The atlas's standing question for
a published number — *does the headline recompute from the artifact* — is
inapplicable to four of them.

## Why the ranking is not the point

It would be easy to read this as a complaint about rigour, and three of the four
do not deserve it. A position paper on human oversight owes no repository. A
paper measuring test-time behaviour across eight commercial models cannot ship
the models. What the count actually shows is that **the atlas's evidence standard
and the literature's output have different shapes**, and the boundary sections
are where that mismatch gets adjudicated rather than resolved.

The consequence is concrete and already visible in how these five were filed.
The one with an artifact could be *settled*: reading `keys_values` established
that its `kvcache/` holds eviction policies, that the word `forget` occurs once
in the package as a test-fixture string, and that every occurrence of `memory` is
a GPU allocation — so a paper whose title names this atlas's central concern was
placed on the far side of the boundary in one reading. The other four had to be
placed on what they *say*, with the abstract's numbers repeated as the paper's
own rather than recomputed. Those entries are weaker and should read as weaker.

## The sharp one

*Stop Comparing LLM Agents Without Disclosing the Harness* argues that
undisclosed execution harnesses make long-horizon leaderboard comparisons
misleading, and proposes a disclosure standard plus a variance-decomposition
protocol. It releases no implementation of either.

This is not hypocrisy — a thesis can be right with no code behind it, and this
one is right in a way this atlas keeps confirming from the other direction. But
it is the cleanest available illustration of the gap: the paper that asks
everyone to publish enough for a comparison to be checked cannot itself be
checked, and its protocol will be adopted, if at all, by people re-implementing
it from prose.

**The same trap is available to this page.** The benchmarks page specifies a
thirteen-step deletion sequence and an adapter contract and ships neither, and
says so. Recording that in the same note as the observation about others is the
only honest way to make it.

## What to do with it

Nothing structural. Two habits:

1. **Say which kind of citation an entry is.** An entry grounded in an artifact
   read at a pin and an entry grounded in an abstract are different evidence and
   should not be phrased alike. *"The abstract reports"* is the honest verb for
   the second, and it is cheap.
2. **When a paper does ship code, read it before placing the paper.** It changed
   the outcome once in five, and it was the case where the title was most
   misleading. That is a good enough hit rate to make it the default.

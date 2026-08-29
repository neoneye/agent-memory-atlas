# A memory you can route around is one nobody exercises

**Status:** synthesis. Four readings between 27 and 29 August 2026, three of
them on this atlas's benchmarks page, one a pretraining paper that is not about
agent memory at all.

---

## The observation

The clean statement of it is in a Meta FAIR paper about model architecture
([arXiv:2509.24552](https://arxiv.org/abs/2509.24552)), which has nothing to do
with agent memory and states the principle better than anything that does.

SWAX alternates sliding-window attention with xLSTM recurrent layers. Widening
the attention window makes long-context recall *worse* — at 131k tokens on
RULER, a 128-token window recalls about 30% and a 2048-token window recalls
approximately nothing. The recurrent layers were present the whole time and had
capacity the whole time. The authors:

> during training, most of the dependencies to model fall inside the 2048 tokens
> window. Therefore, during pretraining, it was advantageous for the model with a
> window of 2048 to use the more precise softmax attention from the sliding
> window rather than having to rely on the less precise Linear Attention layers
> […] the model does not extrapolate since it never learned to rely on the Linear
> Attention layers to do long-context modeling.

The memory pathway atrophied because a cheaper path was available every time it
was being trained. Their fix is to take the shortcut away part of the time:
sample the window between 128 and 2048 during training.

## Why it is a note and not a report

The mechanism is a claim about gradients and does not transfer to a memory
system built out of SQLite and prompts. **The evaluation consequence does**, and
it arrives at the same place from three unrelated directions read in the same
week.

**FP-AMB** ships four committed scorecards on a 60-session corpus and its
**TF-IDF baseline wins** — 69.7% against real mRAG at 66.6%, the author's own
Fractal Memory at 50.2% and MemPalace at 36.1%. A lexical baseline answering in
three milliseconds beat every real memory architecture on the benchmark's own
questions. That is what a bypassable memory looks like from the scoreboard: if a
term-frequency lookup over the transcript answers the exam, the exam is not
asking anything only memory can answer.

**Self-GC** defines its headline metric the other way round. No-impact rate asks
whether the retained context still supports *the real future continuation* —
given the ground-truth future turns, did the pruning destroy a URL, a path, a row
value or an editable body that a later step needed. The question is not "is the
answer still there" but "did removing this break something downstream," which is
the only form in which the memory's contribution is visible.

**Tycho** does the same thing by ablation rather than by metric design. Four
scorecards hold the model fixed at Claude Opus 4.8 and vary only the world-model
policy: no world model 79.07, single actor 85.36, actor-controlled builder 88.49.
The memory is worth 9.42 RHAE *because the arm without it was run*.

**WikiSkill** ([arXiv:2608.27454](https://arxiv.org/abs/2608.27454)) is the
fourth, read two days later and from a paper with no code. It co-evolves agent
skills with a persistent wiki and reports that the ablations *"confirm that
persistent knowledge accumulation in the wiki is critical for effective skill
evolution."* That sentence exists because somebody ran the arm without the wiki.

## The rule

**Measure the memory by removing it, on the cases where nothing else can
answer.**

An evaluation whose questions the recent context can satisfy is measuring the
context. An evaluation whose questions a BM25 pass over the transcript can
satisfy is measuring BM25. In both cases the memory system's failures stay
invisible until production, where the case that needed it finally arrives.

The three shapes that make a memory bypassable, in the order they are easy to
miss:

1. **The answer is also in the recent turns.** Most conversational benchmarks
   have this problem and it is why the refusal and multi-session categories are
   the ones that discriminate.
2. **The answer is also in the prompt.** A system prompt carrying preferences,
   constraints or a persona answers a large fraction of "does it remember me"
   questions without the store being touched.
3. **The retriever would have surfaced it anyway.** The hardest one, because it
   looks like the memory working. The distinguishing test is whether the item
   would have ranked without whatever the memory layer added.

## What this asks of a report

Section 10 of a report should be able to answer: *is there a committed case that
only the memory can pass?* For most systems in this corpus the answer is no, and
the honest form of that is not "the tests are thin" but "the tests do not
separate the memory from the context it sits in."

Related, and the reason this is one note rather than three: the
[`negative_eval`](../content/capabilities.md) mark is the closest existing proxy.
A committed case asserting particular material must *not* come back is the only
common test shape that cannot be passed by a system that returns everything, and
that is the same property as being unbypassable, seen from the other side.

## Where it landed

A section on the benchmarks page,
*A memory the system can route around is one nobody exercises*, drawing the four
together. FP-AMB, Self-GC and Tycho each keep their own section; this one is the
generalisation over them.

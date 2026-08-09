# The constant was fixed for thirty arms

**Status:** four papers read. The pattern page gains the citations it never had
and a corrected recommendation; no report claim was found false. An earlier
version of this note claimed Akarsu et al. was the only published sweep of the
RRF constant on two arms — that was wrong, it is neither the first nor the
broadest, and Bruch et al. 2023 is now the primary source below. Per-report
follow-up is listed at the end and is not done.

**Subjects.**

1. Gordon V. Cormack, Charles L. A. Clarke and Stefan Büttcher, *Reciprocal Rank
   Fusion outperforms Condorcet and individual Rank Learning Methods*, SIGIR '09,
   pp. 758–759, [10.1145/1571941.1572114](https://dl.acm.org/doi/10.1145/1571941.1572114).
   The [Google Research page](https://research.google/pubs/reciprocal-rank-fusion-outperforms-condorcet-and-individual-rank-learning-methods/)
   is a landing record for the same two-page paper. The ACM record is the citable
   one and returns 403 to a fetcher; the readable copy is the first author's, at
   `cormack.uwaterloo.ca`.
2. Sebastian Bruch, Siyu Gai and Amir Ingber, *An Analysis of Fusion Functions
   for Hybrid Retrieval*, ACM TOIS 2023,
   [arXiv:2210.11934](https://arxiv.org/abs/2210.11934).
3. Meftun Akarsu, Recep Kaan Karaman and Christopher Mierbach, *From BM25 to
   Corrective RAG: Benchmarking Retrieval Strategies for Text-and-Table
   Documents*, [arXiv:2604.01733](https://arxiv.org/abs/2604.01733), 2 April 2026.
4. Benjamin Clavié, Sean Lee, Aamir Shakir and Makoto P. Kato, *Latent Terms:
   Dense Retrievers Contain Trivially Extractable BM25-ready Zipfian
   Vocabularies*, [arXiv:2605.29384](https://arxiv.org/abs/2605.29384), 28 May 2026.

**60 is the only RRF constant that appears anywhere in this atlas**: seven
reports name one, and every one of them is 60. That is the fact this note is
about.

---

## 1. What the 2009 paper actually fixed, and on what

The formula, verbatim:

> RRFscore(*d* ∈ *D*) = Σ<sub>*r* ∈ *R*</sub> 1 / (*k* + *r*(*d*)),
> where *k* = 60 was fixed during a pilot investigation and not altered during
> subsequent validation.

The pilot is Table 1: **thirty configurations of Wumpus Search** — one engine,
thirty settings — fused over TREC topics 351–400, with *k* swept.

| *k* | 0 | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 90 | 100 | 500 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MAP | .2072 | .2123 | .2134 | .2139 | .2138 | .2144 | **.2145** | .2146 | .2147 | .2145 | .2142 | .2098 |

**k = 60 is not the argmax of the table it comes from** — 80 is, and 70 also
beats it, by 0.0002 and 0.0001 MAP. The paper says as much: the results
"indicated that k = 60 was near-optimal, but that the choice was not critical."
Between 30 and 100 the whole spread is four tenths of one percent.

The stated rationale for having a *k* at all is one sentence: it "mitigates the
impact of high rankings by outlier systems". That is the only claim the paper
makes about why the constant exists, and it is not a claim about how many
rankings are being fused or how independent they are.

Two corrections to how the paper gets invoked:

- **The title's "outperforms" does not cover score fusion.** On LETOR3 (Table 3)
  CombMNZ scores MAP 0.6107 against RRF's 0.6051 — CombMNZ edges RRF, at p ≈ .2.
  What RRF beat significantly was Condorcet Fuse (p ≈ .004) and every individual
  rank-learning method: ListNet, LGD, AdaRank-MAP, RankSVM, RankBoost (p < .003).
- **The property this atlas keeps citing is the paper's own.** RRF "combines
  ranks without regard to the arbitrary scores returned by particular ranking
  methods", and needs "no special voting algorithm or global information; ranks
  may be computed and summed one system at a time". That is why it is a sane
  default for a store with no relevance data, and it survives everything below.

## 2. What the constant does at two arms

Thirty rankings is a different setting from two, and the arithmetic is worth
stating carefully, because the loose version of it is wrong.

**What holds unconditionally.** Within a single arm, *k* = 60 compresses the
entire top 60 into a factor of (60+60)/(60+1) = **1.967×**. Rank 1 is worth
barely more than rank 60 to the fused score. Lowering *k* restores that range:
at *k* = 10 the same span is 6.36×.

**What does not hold.** An earlier version of this note said appearing in a
second arm is "worth exactly 2×". It is not. A document at rank *a* in one arm
that also appears at rank *b* in the other gains a factor of
1 + (*k*+*a*)/(*k*+*b*) — which equals 2 only when *a* = *b*, and at *k* = 60
with *a* = 1, *b* = 1000 is **1.058×**. The "rank 61" threshold quoted before is
similarly narrow: it is the case where both arms return a document at the *same*
rank *r*, where consensus beats a lone first-place hit while *r* < *k*+2.
Agreement is worth a great deal when the two arms rank a document similarly and
very little when they do not, which is the opposite of a presence vote at one
end of that range.

**Two things the arithmetic cannot see.** Candidate depth: a document missing
from an arm's top-*k* has no defined rank at all, and the usual approximation is
to rank within the union of the returned lists — Bruch et al. raise exactly this
as their first objection to rank-only fusion, and it means an arm that returns 20
candidates and an arm that returns 500 are not interchangeable inputs. And
correlation: two views of one corpus are not two independent voters, so
"agreement" carries less evidence than the word suggests. That cuts against the
2009 pilot too — thirty configurations of one engine will fail together.

The atlas has already reported the small-*k* end of this from both sides,
without connecting either to the constant:

- [agent-memory-supabase](../content/systems/agent-memory-supabase.md) guards its
  text lane with a `min_similarity` floor because, in its own comment's
  reasoning, RRF is rank-based rather than score-based and a lone weak lexical
  match on a shared stop-ish word otherwise takes full text-lane credit. At
  *k* = 60 that junk hit scores 1/61 and beats a genuinely relevant memory the
  vector lane placed **third** (1/63) and did not surface lexically at all.
- [Empryo](../content/systems/empryo.md) enters co-change affinity at a fixed
  RRF rank of 5 rather than at its own, to keep it *"~3× weaker than a direct
  file hit"*. Entering a signal at a chosen rank is a way to buy back the dynamic
  range a large *k* flattens — and a 3× ratio between rank 1 and rank 5 is only
  reachable near *k* = 1. The report records the comment and not the constant, so
  that is arithmetic, not a finding; see *Not done*.

The seven reports that name the constant fuse two arms
([Helm](../content/systems/helm.md), [Token Savior](../content/systems/token-savior.md),
[TencentDB Agent Memory](../content/systems/tencentdb-agent-memory.md)), three
([agent-memory-supabase](../content/systems/agent-memory-supabase.md),
[PowerMem](../content/systems/powermem.md), [CSM](../content/systems/csm.md)) or
four ([Mnemosyne](../content/systems/mnemosyne.md)). None sweeps *k*. Mnemosyne's
source comment calls 60 *"proven optimal for 4-voice retrieval"*; the report
already declined that as "inherited rather than established", and the pilot table
backs the refusal.

## 3. The constant has been swept, on two arms, on nine datasets

Bruch, Gai and Ingber studied precisely this configuration — one lexical arm, one
semantic arm — three years before Akarsu. Their first move is the one that
matters: they rewrite RRF with **one constant per arm**, η<sub>Lex</sub> and
η<sub>Sem</sub>. In their words, they "adopt a parametric view of RRF where we
have as many parameters as there are retrieval functions to fuse, a quantity
that is always one more than that in a convex combination." The count checks
out: *m* arms give RRF *m* constants, while convex weights on *m* scores have
*m*−1 free values — for the two-arm case, two against α alone. So the method
usually preferred for being parameter-free carries one parameter more than the
one it is preferred over. Two caveats on that framing: the per-arm view is
Bruch et al.'s deliberate re-parameterization, not Cormack's formula, which has
a single shared *k* whatever the arm count; and the convex combination's count
excludes normalization, which they argue is inconsequential because linear
transforms give rank-equivalent solutions.
They sweep both over {1, …, 100} on nine datasets — MS MARCO, NQ and Quora
in-domain; NFCorpus, HotpotQA, FEVER, SciFact, DBPedia and FiQA zero-shot — and
report that NDCG "swings wildly as a function of RRF parameters".

Mean NDCG@1000 (@100 for SciFact and NFCorpus), from their Table 3:

| Dataset | TM2C2 (convex, α=0.8) | RRF (60,60) | RRF (5,5) | RRF (10,4) |
| --- | --- | --- | --- | --- |
| MS MARCO *(in-domain)* | **0.454** | 0.425 | 0.435 | 0.451 |
| NQ *(in-domain)* | **0.542** | 0.514 | 0.521 | 0.528 |
| Quora *(in-domain)* | **0.901** | 0.877 | 0.885 | 0.896 |
| NFCorpus | **0.327** | 0.312 | 0.318 | 0.310 |
| HotpotQA | **0.699** | 0.675 | 0.693 | 0.621 |
| FEVER | **0.744** | 0.721 | 0.727 | 0.649 |
| SciFact | **0.753** | 0.730 | 0.738 | 0.715 |
| DBPedia | **0.512** | 0.489 | 0.489 | 0.480 |
| FiQA | **0.496** | 0.464 | 0.470 | 0.482 |

Three findings, in the order they matter for this atlas:

1. **The convex combination wins everywhere.** One tuned weight over normalized
   scores beats RRF (60,60) on NDCG on all nine datasets, in-domain and
   zero-shot, and the paper reports it is sample-efficient — a small set of
   in-domain examples is enough to tune α. The choice of normalizer is "generally
   agnostic". This is the recommendation the atlas should be making, and was not.
2. **Symmetrically lowering the constant transfers.** (5,5) matches or beats
   (60,60) on all nine. That is the cheapest defensible change available to a
   system that cannot tune anything, and it is consistent with §2: a smaller *k*
   restores rank resolution inside each arm.
3. **Per-arm tuning does not transfer.** (10,4), tuned on the in-domain
   validation splits, gains in-domain (MS MARCO 0.425 → 0.451) and then loses
   badly out of domain (HotpotQA 0.675 → 0.621, FEVER 0.721 → 0.649). The
   mechanism is stated plainly: raising η for an arm discounts that arm, and
   in-domain the semantic arm deserves the weight while out-of-domain it does
   not. **"Sweep it" is therefore not sufficient advice** — a sweep on one
   corpus is a claim about that corpus.

Akarsu et al. is a fourth data point, agreeing directionally in one narrow
domain: on T²-RAGBench (23,088 queries, 7,318 mixed text-and-table financial
documents), two arms, Recall@5 of 0.726 for a convex combination at α = 0.5,
0.716 for RRF *k* = 10, 0.695 for RRF *k* = 60. Its own limitations are
substantial — financial documents only, every answer numerical, whole documents
retrieved at ~920 tokens, one embedding model. Its main table is worth carrying
for a different reason: BM25 beats `text-embedding-3-large` on every metric but
Recall@20 (0.644 vs 0.587 R@5, 0.515 vs 0.466 nDCG@10), and hybrid plus reranking
reaches 0.816 R@5.

## 4. What Latent Terms shows, stated narrowly

The hybrid pattern's premise — vector search is weak on exact names, identifiers
and dates — had been asserted on this site with no external citation. *Latent
Terms* measures it: on LIMIT, built to expose single-vector retrieval,
**Recall@20 of 0.9490 for BM25 against 0.0265 for Contriever**.

The tempting over-reading, which the earlier version of this note published, is
that the lexical capability is already in the dense model and only its scorer
hides it. That is more than the experiment supports. What the paper does: train a
new Top-K sparse autoencoder (32,768 latents, 16 active) on the retriever's
frozen final-layer **token** activations, then score the resulting features with
ordinary BM25 over an inverted index. The pooled embedding is never rescored, and
the recovery is partial and uneven:

- Contriever's LIMIT Recall@20 goes 0.0265 → 0.5100 — a large recovery, still
  0.44 below BM25.
- BEIR nDCG@10 for Contriever goes 0.415 → 0.474, past SPLADE-v2.
- On the multi-vector model it **loses**: GTE-ModernColBERT 0.547 → 0.500 on
  BEIR, 0.8565 → 0.8315 on LIMIT.
- The authors' own limitation: the features hybridize, but "our results do not
  appear to fully match the strength of a true Dense + Sparse hybrid method as it
  suffers from some drawbacks on datasets where one or the other is typically
  strong."

The defensible statement is that **token-level activations of some frozen dense
retrievers can be transformed into sparse features a lexical scorer can use** —
which takes a trained component and a second index. That is an argument for
keeping a lexical arm, not evidence that the representation was innocent and only
the scoring failed.

## 5. What changed on the site

[Hybrid retrieval fusion](../content/patterns/hybrid-retrieval-fusion.md) now
cites Cormack for the property it borrows, Bruch et al. for the parameter
evidence, Akarsu as the narrow corroboration, and Latent Terms for the premise —
each scoped to what it shows. The recommendation changed with the evidence: a
convex combination over normalized scores with one tuned weight is the
better-evidenced fusion; a symmetric reduction of the constant is the cheapest
change that has been shown to transfer; per-arm tuning should be expected not to
survive a domain change. The tests section asks for a sweep *and* a check that it
holds off the tuning corpus.

Nothing was retracted from a report. Token Savior's "the reference constant
(Cormack et al. 2009)", Helm's "the conventional k=60" and Mnemosyne's "inherited
rather than established" were accurate and stay.

## Not done

- **Empryo's `RRF_K`.** The report records the 3× comment and not the value.
  Confirm it at the pin; if it is near 1, it is the only system here that chose
  the constant rather than inheriting it.
- **The other twenty-two RRF reports name no constant.** Whether they use 60,
  something else, or leave it configurable is unrecorded. `powermem` exposes
  `rrf_k=60`; Mnemosyne has per-voice env toggles. Which systems expose the
  constant at all is a static check worth one pass.
- **Whether any system normalizes scores at all.** Bruch's result makes convex
  combination the recommendation, and the atlas has never counted how many
  systems could adopt it — that needs a bounded, comparable score from each arm,
  which several backends do not give.
- **Nothing here was executed.** No sweep was run against any system in this
  corpus, and this project does not run checkouts.

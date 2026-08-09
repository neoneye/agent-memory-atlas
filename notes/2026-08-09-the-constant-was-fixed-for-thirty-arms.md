# The constant was fixed for thirty arms

**Status:** four links read, three papers — two of the links are the same paper.
One pattern page gains the citation it never had and a caveat it needed; no
report claim was found false. Per-report follow-up is listed at the end and is
not done.

**Subjects.**

1. Gordon V. Cormack, Charles L. A. Clarke and Stefan Büttcher, *Reciprocal Rank
   Fusion outperforms Condorcet and individual Rank Learning Methods*, SIGIR '09,
   pp. 758–759, [10.1145/1571941.1572114](https://dl.acm.org/doi/10.1145/1571941.1572114).
   The [Google Research page](https://research.google/pubs/reciprocal-rank-fusion-outperforms-condorcet-and-individual-rank-learning-methods/)
   is a landing record for the same two-page paper, so two of the four links are
   one source. The ACM record is the citable one and returns 403 to a fetcher;
   the readable copy is the first author's, at `cormack.uwaterloo.ca`.
2. Meftun Akarsu, Recep Kaan Karaman and Christopher Mierbach, *From BM25 to
   Corrective RAG: Benchmarking Retrieval Strategies for Text-and-Table
   Documents*, [arXiv:2604.01733](https://arxiv.org/abs/2604.01733), 2 April 2026.
3. Benjamin Clavié, Sean Lee, Aamir Shakir and Makoto P. Kato, *Latent Terms:
   Dense Retrievers Contain Trivially Extractable BM25-ready Zipfian
   Vocabularies*, [arXiv:2605.29384](https://arxiv.org/abs/2605.29384), 28 May 2026.

They are not four unrelated links. Both 2026 papers cite the 2009 one — the
first for its fusion rule, the second for the claim that lexical and semantic
matching recover different things. And **60 is the only RRF constant that appears
anywhere in this atlas**: seven reports name one, and every one of them is 60.

---

## 1. What the 2009 paper actually fixed, and on what

The formula, verbatim:

> RRFscore(*d* ∈ *D*) = Σ<sub>*r* ∈ *R*</sub> 1 / (*k* + *r*(*d*)),
> where *k* = 60 was fixed during a pilot investigation and not altered during
> subsequent validation.

The pilot is Table 1: thirty configurations of Wumpus Search, fused over TREC
topics 351–400, with *k* swept.

| *k* | 0 | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 90 | 100 | 500 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MAP | .2072 | .2123 | .2134 | .2139 | .2138 | .2144 | **.2145** | .2146 | .2147 | .2145 | .2142 | .2098 |

Two things follow that the number's reputation does not carry. **k = 60 is not
the argmax of the table it comes from** — 80 is, and 70 also beats it, by 0.0002
and 0.0001 MAP. And the paper says so plainly: the results "indicated that k = 60
was near-optimal, but that the choice was not critical." Between 30 and 100 the
whole spread is .2138 to .2147, four tenths of one percent.

So the constant is a defensible default and was never a tuned optimum. Read it as
*the value that stopped mattering in this experiment*, which is a much weaker
statement than the one it has acquired by being copied.

Two more corrections to how the paper is usually invoked:

- **The title's "outperforms" does not cover score fusion.** On LETOR3 (Table 3),
  CombMNZ scores MAP 0.6107 against RRF's 0.6051 — CombMNZ edges RRF, at p ≈ .2.
  What RRF beat significantly was Condorcet Fuse (p ≈ .004) and every individual
  rank-learning method: ListNet, LGD, AdaRank-MAP, RankSVM, RankBoost (p < .003).
- **The property this atlas keeps citing is the paper's own.** RRF "combines
  ranks without regard to the arbitrary scores returned by particular ranking
  methods", and needs "no special voting algorithm or global information; ranks
  may be computed and summed one system at a time". That is exactly why it is a
  sane default for a memory store with no relevance data, and it survives
  everything below.

## 2. Thirty arms is a different machine from two

The experiment fused **thirty** rankings in the pilot and whole sets of TREC
participant submissions in Table 2. Every system in this atlas fuses between two
and five. That difference is not cosmetic, and it is arithmetic rather than
opinion.

Ask when *m* arms agreeing at rank *r* outrank a document sitting at rank 1 in
one arm and absent from the others: *m*/(*k*+*r*) > 1/(*k*+1), i.e. *r* <
*m*(*k*+1) − *k*. The largest rank at which consensus still wins:

| arms *m* | *k* = 10 | *k* = 60 | *k* = 80 |
| --- | --- | --- | --- |
| 2 | 11 | **61** | 81 |
| 3 | 22 | 122 | 162 |
| 4 | 33 | 183 | 243 |
| 5 | 44 | 244 | 324 |
| 30 | 319 | 1769 | 2349 |

With two arms at *k* = 60, a document both arms rank **61st** outranks a document
one arm ranks **first**. Put the other way: within a single arm, the entire rank
signal across its top 60 is worth a factor of 1.967×, while the bare fact of
appearing in a second arm is worth exactly 2×. **Two-arm RRF at k = 60 is closer
to a presence vote than to a rank aggregation.** At thirty arms the same constant
is unremarkable, because agreement among thirty independent systems is real
evidence and no single arm should be able to override it.

This is not a hypothetical failure — the atlas has already reported it twice,
from both sides, without connecting either to the constant:

- [agent-memory-supabase](../content/systems/agent-memory-supabase.md) guards its
  text lane with a `min_similarity` floor because, in its own comment's
  reasoning, RRF is rank-based rather than score-based and a lone weak lexical
  match on a shared stop-ish word otherwise takes full text-lane credit. At
  *k* = 60 that junk hit scores 1/61 and beats a genuinely relevant memory the
  vector lane placed **third** (1/63). The floor is the right fix. The number is
  what makes the failure that easy to hit.
- [Empryo](../content/systems/empryo.md) enters co-change affinity at a fixed
  RRF rank of 5 rather than at its own, to keep it *"~3× weaker than a direct
  file hit"*. Entering a signal at a chosen rank is precisely a way to buy back
  the dynamic range a large *k* flattens — and a 3× ratio between rank 1 and
  rank 5 is only reachable at *k* = 1, two orders of magnitude off the default.
  The report records the comment and not the constant, so that is arithmetic,
  not a finding; see *Not done*.

The seven reports that name the constant fuse two arms
([Helm](../content/systems/helm.md), [Token Savior](../content/systems/token-savior.md),
[TencentDB Agent Memory](../content/systems/tencentdb-agent-memory.md)), three
([agent-memory-supabase](../content/systems/agent-memory-supabase.md),
[PowerMem](../content/systems/powermem.md), [CSM](../content/systems/csm.md)) or
four ([Mnemosyne](../content/systems/mnemosyne.md)). None sweeps *k*. Mnemosyne's
source comment calls 60 *"proven optimal for 4-voice retrieval"*; the report
already declined that as "inherited rather than established", and the paper it is
inherited from now backs the refusal in its own table — the pilot had thirty
voices and a flat curve.

## 3. The one time somebody swept it on two arms

*From BM25 to Corrective RAG* evaluates ten retrieval strategies on T²-RAGBench,
23,088 queries over 7,318 mixed text-and-table financial documents. Its hybrid is
two arms, BM25 and `text-embedding-3-large`, and it adopts *k* = 60 for the main
table as "the value used in the original paper". Then §IV-C sweeps it:

| Fusion, two arms | Recall@5 |
| --- | --- |
| Convex combination, α = 0.5 | **0.726** |
| RRF, *k* = 10 | 0.716 |
| RRF, *k* = 60 (the default) | 0.695 |

The paper's explanation is the arithmetic above in one line: "lower *k* values
emphasize top-ranked documents more aggressively". Its main table is also worth
carrying, because it inverts an assumption this atlas sees implemented everywhere
— BM25 0.644 R@5, 0.515 nDCG@10 against dense at 0.587 and 0.466, on every metric
but Recall@20; and the two-stage hybrid-plus-reranker reaching 0.816 R@5 and
0.605 MRR@3, beating every single-stage method.

**What this does not license.** One benchmark, one domain, one embedding model.
The authors list the limits themselves: financial documents only, every answer
numerical, whole documents retrieved at ~920 tokens rather than passages, and API
models whose behaviour can change under them. The finding is not *use k = 10*. It
is that the default has now been swept once in the two-arm setting everybody
actually ships, and it came third of three.

## 4. What Latent Terms changes, and what it does not

The hybrid pattern's premise — vector search is weak on exact names, identifiers
and dates — has been asserted on this site with no external citation. *Latent
Terms* is the strongest citable evidence for it, and it cites Cormack for the
same proposition.

On LIMIT, a benchmark built to expose single-vector retrieval, Recall@20: **BM25
0.9490, Contriever 0.0265.** That is the premise, measured, at a factor of 36.

The paper then complicates the mechanism in a way worth having. Train a Top-K
sparse autoencoder (32,768 latents, 16 active) on a *frozen* retriever's
activations with no retrieval supervision at all, and the features that fall out
have roughly Zipfian collection statistics — so you can score them with ordinary
BM25 over an ordinary inverted index. Contriever's LIMIT Recall@20 goes 0.0265 →
**0.5100**; its BEIR nDCG@10 average goes 0.415 → 0.474, past SPLADE-v2. The
lexical capability was inside the dense model the whole time. What failed was the
scoring interface, not the representation.

**It is not an argument for dropping an arm**, and the authors do not make one:

- BM25 still wins LIMIT by 0.44 Recall@20 after the extraction.
- On the multi-vector model the method *loses* — GTE-ModernColBERT 0.547 → 0.500
  on BEIR, 0.8565 → 0.8315 on LIMIT.
- Their own limitations section: the features hybridize, but "our results do not
  appear to fully match the strength of a true Dense + Sparse hybrid method as it
  suffers from some drawbacks on datasets where one or the other is typically
  strong."

Their annotation of what the features capture — roughly two-thirds semantic,
one-third purely lexical — is the cleanest statement of why the two arms are
worth keeping separate: a single scoring interface has to trade them off, and two
indexes do not.

## 5. What changed on the site

[Hybrid retrieval fusion](../content/patterns/hybrid-retrieval-fusion.md) gains
the citation it should always have carried, the arm-count caveat from §2, and a
test worth requiring: sweep the constant, because nobody in this corpus has. The
external evidence for the pattern's premise is now cited rather than asserted.

Nothing was retracted. The three reports that reason about the constant in prose
— Token Savior's "the reference constant (Cormack et al. 2009)", Helm's "the
conventional k=60", Mnemosyne's "inherited rather than established" — were all
accurate and all stay. The gap was that the pattern page recommending RRF cited
nothing at all.

## Not done

- **Empryo's `RRF_K`.** The report records the 3× comment and not the value.
  Confirm it at the pin; if it is 1, it is the only system here that chose the
  constant rather than inheriting it, and that is worth a sentence in the pattern
  page rather than in a note.
- **The other twenty-two RRF reports name no constant.** Whether they use 60, use
  something else, or leave it configurable is unrecorded. `powermem` exposes
  `rrf_k=60` as configuration and Mnemosyne has per-voice env toggles, which is
  the instrument for sweeping it; whether any other system exposes it is a
  static check, not a run.
- **Nothing here was executed.** No sweep was run against any system in this
  corpus, and this project does not run checkouts. The reachable version of this
  work is static: which systems expose the constant, on how many arms, and
  whether the arm count is even fixed at query time.

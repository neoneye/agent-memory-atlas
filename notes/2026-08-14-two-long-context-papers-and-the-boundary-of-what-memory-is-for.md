# Two long-context papers, and the boundary of what memory is for

**Status:** read, triaged, folded into the benchmarks page. Neither is a memory
system and neither gets a report; both are measurement artifacts that bound what
a memory layer can and cannot do, and one of them traces a fabricated baseline
already flagged in the corpus back to its source.
**Subjects:**
- *Context Rot: How Increasing Input Tokens Impacts LLM Performance* — Chroma
  research, [trychroma.com/research/context-rot](https://www.trychroma.com/research/context-rot),
  code at [chroma-core/context-rot](https://github.com/chroma-core/context-rot).
- *Oolong: Evaluating Long Context Reasoning and Aggregation Capabilities* —
  Bertsch, Pratapa, Mitamura, Neubig, Gormley,
  [arXiv:2511.02817](https://arxiv.org/abs/2511.02817), 4 November 2025.

## Why neither is a report

The atlas reports on systems with an inspectable memory store: something is
written, survives the session, and can be retrieved and corrected. These are a
research report and a benchmark paper about **long-context model behaviour** —
how an LLM uses (or fails to use) tokens already in its window. There is no
store, nothing survives a session, nothing is a claim that could be corrected.
Out of scope on the ordinary basis. They are worth reading anyway because they
measure the two things a memory system exists to be an answer to.

## What each one is

**Context Rot** runs eighteen models (Claude, GPT, Gemini, Qwen families) and
shows that performance "grows increasingly unreliable as input length grows,"
non-uniformly, even on tasks that are trivial at short length — a needle that is
found at 1K is missed at 100K; a repeated-word replication that is exact at 1K
drifts at 10K. Several of its sub-findings are counterintuitive and worth
knowing: lower needle-question semantic similarity accelerates the decay;
distractors compound non-uniformly; and models do *worse* on a haystack that
preserves logical flow than on a shuffled one.

The finding that matters for this atlas is the LongMemEval experiment:
**every model family scores significantly higher on a focused ~300-token prompt
than on the full ~113K-token conversation.** That is the empirical case for
retrieval, stated as a measurement rather than an intuition. A memory layer that
delivers the relevant 300 tokens beats handing the model the whole history — so
"decide what to retrieve" is a performance floor, not a nicety. Divergence #4 on
the compare page ("whether retrieval can decline") and every focused-injection
mechanism in the corpus — Grok Build's prompt-cache-aware block, Zep's
retrieval-budget ablation, Verel's token-budgeted fenced recall — are answers to
the cost this paper measures.

Worth naming plainly: the argument that retrieval is necessary is made here by
**the vendor of a vector database**. That does not make it wrong — the method is
public and the code is released — but the incentive is exactly aligned with the
conclusion, and a reader should hold both facts at once.

**Oolong** is the other half. It is a benchmark for long-context *reasoning and
aggregation* — counting, classification, distributional questions that require
analysing every chunk and combining the results, not retrieving one span. Its
argument against existing long-context evals is that they "allow nearly all of
the context tokens to be disregarded as noise"; Oolong forbids that. Frontier
models (GPT-5, Claude-Sonnet-4, Gemini-2.5-Pro) all score below 50% at 128K on
both splits. This is the case retrieval **cannot** help: there is nothing to
narrow to, because the task is over the whole set. It was already listed on the
benchmarks page as "present in Honcho's bench tree; not characterized here" — now
characterized.

## The boundary they bound

The benchmarks page draws a line: a long-context benchmark asks "given all this
text in the prompt, can you answer"; a memory benchmark asks "given this text is
*not* in the prompt, can the system decide what to retrieve." These two papers
measure the two sides of that line:

- **Context Rot** measures the cost of *not* retrieving — full context degrades,
  so a memory layer that narrows is worth points. Retrieval answers this half.
- **Oolong** measures the tasks where narrowing is impossible — aggregation over
  everything, which models fail regardless. Retrieval does nothing for this half.

Both conclude a bigger window is not the fix. That is the sharper version of the
atlas's own boundary paragraph, and both are now cited there.

## The fabricated baseline they trace back to

[MemCP](../content/systems/memcp.md) ships `tests/benchmark/test_context_rot.py`,
which borrows this exact "context rot" framing and then **hardcodes the numbers
the Chroma work actually measures**: `native_value=5.0  # Typical ~5% retention`
and `native_value=2.0  # ~0.05^3 ≈ near zero`, one assumed constant derived from
another, presented in `benchmark_output/benchmark_report.md` as a measured
head-to-head. The atlas already flagged that in MemCP's verdict as a baseline
that is asserted rather than run. Reading the source it names closes the loop:
the phenomenon is real and Chroma measured it across eighteen models; MemCP took
the name and the vibe and filled in a constant. The difference between the two is
the whole distinction the benchmarks page keeps drawing between a measured number
and a plausible one.

## Disposition

No reports. The benchmarks page now characterises Oolong in the table and adds a
paragraph to "the boundary worth drawing" citing both, with the Context Rot
LongMemEval result as the empirical case for retrieval and the MemCP connection
as the fabricated-baseline lineage. If `chroma-core/context-rot`'s cleaned
LongMemEval materials get adopted as a shipped harness by a system in the corpus,
that system gets the row; the report itself stays a citation.

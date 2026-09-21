# N-gram memory tables in shipped LLMs, and whether they are memory

**Status:** verified against primary sources — arXiv metadata, two official
`config.json` files and llama.cpp's own tensor names. No model weights were
downloaded; every figure below comes from a file of a few kilobytes.
**Origin:** [fulvian/engraft-ngram](https://github.com/fulvian/engraft-ngram),
which writes facts into one of these tables.

## The idea

A transformer has no native primitive for looking something up; it simulates
retrieval with computation. **Engram** adds one: a very large table addressed by
a hash of the last few tokens, read at an early block and added to the residual
stream. It is a key-value memory whose key is an exact token n-gram.

DeepSeek introduced it — *"Conditional Memory via Scalable Lookup: A New Axis of
Sparsity for Large Language Models"*, [arXiv:2601.07372](https://arxiv.org/abs/2601.07372),
12 January 2026, reference code at
[deepseek-ai/Engram](https://github.com/deepseek-ai/Engram) (Apache-2.0, last
pushed 14 January 2026). The framing worth keeping is the abstract's: MoE scales
capacity by *conditional computation*, Engram scales it by *conditional memory*,
and the two trade off along a U-shaped curve.

The reported gains are not where you would expect. Knowledge benchmarks move
(MMLU +3.4, CMMLU +4.0) but reasoning moves more (BBH +5.0, ARC-Challenge +3.7),
and long-context retrieval moves most (Multi-Query NIAH 84.2 → 97.0). The
paper's account is that the table relieves the early layers of static
reconstruction, which effectively deepens the network, and that delegating local
dependencies to lookups frees attention for global context.

## The two shipped models

Both figures below are read from the published `config.json`, not from a
write-up.

| | Qwen3.8-Flash-Next | DeepSeek V4.1 Flash |
| --- | --- | --- |
| `model_type` | `qwen4_exp` | `deepseek_v41` |
| n-gram orders | `ngram_size: 3` → 2- and 3-grams | `engram_max_ngram_size: 4` → to 4-grams |
| heads per order | `heads_per_ngram: 8` | `engram_n_heads: 8` |
| rows read per position | 16 | 24 per table layer, two layers |
| base rows per head | `ngram_vocab_size_base: 20,000,000` | `engram_vocab_size: 16,000,000` |
| table rows | 20M × 16 = **320,000,000** | **768,022,850** over both layers |
| row width | `ple_embed_dim: 2560` ÷ 16 = 160 | `engram_head_dim: 256` |
| table parameters | ≈ **51.2B** | ≈ **196.6B** |
| injected at block | `ple_layer_ids: [2]` | `engram_layer_ids: [1, 14]` |
| tokenizer | vocab 248,320 | vocab 129,280, `engram_compressed_vocab_size: 99,092` |
| quantization | (ENGRAFT measured IQ4_XS) | fp8, `scale_fmt: ue8m0`, blocks 32×32 — MX-style |

Two derivations worth recording because they close the numbers:

- **Qwen.** Orders 2 and 3, eight heads each, is sixteen row reads per position;
  20M × 16 = 320M rows, and 2560 ÷ 16 = 160 dims per head slice, so
  320M × 160 = 51.2B. That is the "51B n-gram embeddings" figure Qwen quotes
  beside a 125B backbone with 6B active.
- **DeepSeek.** Orders 2, 3 and 4 at eight heads each is 24; 16M × 24 =
  384,000,000 against a published 384,006,168 per layer — the slack is padding.

`DeepSeek-V4-Flash` (without the `.1`) carries **no** engram keys at all, so the
module arrived in 4.1.

## llama.cpp calls it PLE, and that is a different PLE

llama.cpp master declares both `LLM_ARCH_QWEN4EXP` and `LLM_ARCH_DEEPSEEK4`,
whose names line up with the two `model_type` values above — but I did not find
the PLE tensors inside either arch's block in `llama-model.cpp`, so **which arch
consumes the table is not established here**; the name match is suggestive and
nothing more.

What is established is that the table exists in the engine's vocabulary. Its
metadata keys are `ple.ngram_size`, `ple.heads_per_ngram`,
`ple.head_vocab_sizes`, `ple.layers`, `ple.conv_kernel`, `ple.head_offsets`,
with tensors `blk.N.ple_key`, `ple_value`, `ple_conv1d` and three norms. So the
naming is real and the table is key/value shaped in the engine, not only in
prose.

**Do not confuse it with `PER_LAYER_*`.** llama.cpp carries a separate
`per_layer_token_embd` family — Gemma 3n's Per-Layer Embeddings — and the two
are different mechanisms under confusingly similar initials. Qwen's own write-up
cites Gemma 3n's PLE *and* DeepSeek's Engram as inspirations, which is probably
how the name travelled.

## Where ENGRAFT fits

ENGRAFT writes new facts into that table by gradient descent on **rows only**,
leaving every transformer weight untouched, and ships the result as one `.pleo`
overlay a llama.cpp fork applies at read time. Removing the overlay restores the
model bit for bit.

Its measurements, recomputed here from the committed artifacts rather than taken
from the README: 841 test sentences, exact-answer greedy **707/841 = 0.841**
with the overlay against **4/841 = 0.005** without, first token at rank 1
723/841 = 0.860. All three match the published numbers exactly.

The specular control is the part worth copying. The Chinese overlay run against
the Italian test set scores 4/841 — identical to base — while **922 overlay rows
were actually read**. The overlay was live and contributed nothing, which is what
makes the locality claim (a fact fires only for the n-grams it was written
under) evidence rather than assertion.

Its account of DeepSeek's differences — "MXFP8 rows, a compressed tokenizer, two
table layers, 4-grams, a value projection" — checks out on all four that the
config can show.

## Titans and ROME, and why they are not this

The atlas excludes both, and the exclusion text names the reason: what they
memorize has *"no key, no scope, no provenance and nothing a later correction
could name."*

- **Titans** ([arXiv:2501.00663](https://arxiv.org/abs/2501.00663), *Learning to
  Memorize at Test Time*, 31 December 2024) puts a neural long-term memory module
  beside attention whose **weights update per sequence**. What it stores is
  distributed across those weights. There is no row to point at, and no official
  implementation to pin.
- **ROME** ([arXiv:2202.05262](https://arxiv.org/abs/2202.05262), *Locating and
  Editing Factual Associations in GPT*, 10 February 2022) locates a fact in MLP
  weights and applies a rank-one edit. It has a *locus*, which is more than
  Titans, but the edit is a modification of the weights themselves.

**Engram is a third thing, and the difference is addressability.** The key is an
exact token n-gram, deterministic and inspectable. The store is a table of rows,
not a weight matrix doing double duty. That is why ENGRAFT can exist at all: you
can write a row without disturbing what the row next to it holds, and you can
delete the write by deleting a file.

Which makes the comparison sharp: **ROME edits the weights; ENGRAFT edits an
index.** Same goal, different object, and only one of them has an undo.

## Why this matters for the scope boundary

The atlas's parametric-memory exclusion was written against Titans and ROME, and
it gives four reasons — no key, no scope, no provenance, nothing a correction
could name. An Engram table has a key by construction. ENGRAFT adds a name a
correction can use (grafts carry a fact id, with `state.json` tracking closed
ones) and a deletion that is bit-exact.

So the exclusion's stated test no longer draws the line where it was meant to.
Whatever is decided about reporting ENGRAFT, that paragraph needs revisiting:
the honest boundary is probably *whether anything writes to it at runtime* —
and nothing does. An Engram table is fixed at pretraining; an ENGRAFT overlay is
written offline and then frozen. Neither is a memory an agent updates as it
works, which is the atlas's actual subject.

## What is not verified here

- The benchmark deltas are the Engram paper's own; nothing was re-run.
- ENGRAFT's numbers were recomputed from its committed result files. Those files
  are its own output — recomputation checks arithmetic and reporting, not the
  experiment.
- No claim is checked about how either model behaves. Only the declared
  architecture was read.

# N-gram memory tables in shipped LLMs, and whether they are memory

**Status:** verified against primary sources: arXiv metadata, the two official
`config.json` files, the 10.9 MB metadata shard of the public Qwen GGUF,
llama.cpp master (`6f41ac59e`, 2026-09-21) and ENGRAFT's committed artifacts.
No model weights were downloaded; the largest file read is the GGUF shard that
holds only metadata and the tokenizer. Every address in the worked example below
was recomputed here from that metadata and checked against the engine's own
per-sentence counts.
**Origin:** [fulvian/engraft-ngram](https://github.com/fulvian/engraft-ngram),
which writes facts into one of these tables.

## The idea

A transformer has no native primitive for looking something up. To know that
the four subword pieces `Dou`, `glas`, ` Qu`, `ail` are one entity, and that
this entity has a profession, the early blocks have to reconstruct that from
attention over the pieces every time the name appears. The reconstruction is
computation spent on something static.

**Engram** adds a primitive: a very large table whose row address is a hash of
the last few tokens, read at one early block and added to the residual stream.
It is a key-value memory whose key is an exact token n-gram, and its lookup is
O(1) because the address is arithmetic on token ids, not a similarity search.

DeepSeek introduced it. *Conditional Memory via Scalable Lookup: A New Axis of
Sparsity for Large Language Models*,
[arXiv:2601.07372](https://arxiv.org/abs/2601.07372), 12 January 2026,
reference code at [deepseek-ai/Engram](https://github.com/deepseek-ai/Engram)
(Apache-2.0, last pushed 14 January 2026). The abstract's framing is the one to
keep: mixture-of-experts scales capacity by *conditional computation*, Engram
scales it by *conditional memory*, and the two trade off along a U-shaped curve.
Put too many parameters in the table and the network is too shallow to use
them; put too few and the early layers go back to reconstructing.

The reported gains are not where a lookup table would be expected to help.
Knowledge benchmarks move (MMLU +3.4, CMMLU +4.0) but reasoning moves more (BBH
+5.0, ARC-Challenge +3.7), and long-context retrieval moves most (Multi-Query
NIAH 84.2 to 97.0). The paper's account has two halves. The table relieves the
early layers of static reconstruction, which effectively deepens the network.
And delegating local dependencies to lookups frees attention for global
context, which is why a needle-in-a-haystack score is the biggest mover.

## How one lookup actually happens

The reference implementation is a single file, `engram_demo_v1.py`, and the
shipped Qwen engine reproduces the same arithmetic. Following one position
through it makes every number in the tables below concrete.

**1. Compress the tokenizer (DeepSeek only).** Before hashing, each token id is
mapped through a lookup table that merges tokens whose surface forms are equal
after NFKC normalisation, accent stripping, lowercasing and whitespace
collapsing. `Apple`, `apple` and `APPLE` become one key. The demo builds this
table by decoding every id and normalising the string; the shipped V4.1 config
records the result as `engram_compressed_vocab_size: 99,092` against a
tokenizer of 129,280. Qwen's config has no such field and llama.cpp's hash runs
on raw ids, so Qwen's table keys case-sensitively.

**2. Take the window.** At position *t* the context is the current token and
the previous *n* − 1, `ctx = [x_t, x_{t-1}, x_{t-2}, …]`. A missing predecessor
at the start of the sequence, or an end-of-sequence token found while walking
back, is replaced by a separator id and so is everything older than it. So the
first token of a sequence is hashed as the bigram (token, EOS) and the trigram
(token, EOS, EOS). The EOS of the current token does not cut its own context.

**3. Mix.** For each order *n* from 2 up to the maximum:

```
mixed_n = (ctx[0] · m[0]) xor (ctx[1] · m[1]) xor … xor (ctx[n-1] · m[n-1])   mod 2^64
```

The multipliers `m` are per-layer constants. In the demo they are random odd
64-bit integers drawn from a generator seeded with `seed + 10007 · layer_id`.
In the public Qwen GGUF they are stored as metadata:

```
qwen4exp.ple.layer_multipliers = [23703573157769, 20109073645365, 8052911324071]
```

**4. Address one row per head.** Each order has *H* heads, and head *h* takes
`mixed_n mod p_h` as its local row, where `p_h` is that head's row count. The
row counts are *consecutive primes* just above the configured base size, found
by `find_next_prime` in the demo, with each prime used once across all heads
and layers. Different moduli give each head a different collision pattern for
the same mixed value, so eight heads reading the same n-gram are eight
independent hash functions over one key. The GGUF confirms the scheme for Qwen:

```
qwen4exp.ple.head_vocab_sizes = [20000003, 20000023, 20000033, 20000047,
  20000059, 20000063, 20000069, 20000077, 20000081, 20000093, 20000107,
  20000147, 20000153, 20000159, 20000161, 20000171]
```

These are the first sixteen primes above 19,999,999. The heads are laid out
back to back in one flat table, so a global row is `local + offset[h]`, and the
offsets are the running sum of the sizes.

**5. Read and inject.** The 16 (Qwen) or 24 (DeepSeek) rows are concatenated
into one vector. Then, from the demo's `Engram.forward`, per residual stream
(both models widen the residual into `hc_mult = 4` streams): project the
concatenation to a key, RMS-normalise it and the stream's hidden state, take
their dot product scaled by √d, compress it with a signed square root and pass
it through a sigmoid. That scalar is the gate. The output is
`gate · value_proj(rows)`, plus a short causal convolution over that value
(kernel 4, dilation equal to the maximum n-gram order), and the result is added
to the residual. The gate is what stops a hash collision from dumping an
unrelated row into the stream: the hidden state has to agree with the row's key
for the row to get through. llama.cpp's per-block tensors for Qwen are exactly
these pieces: `ple_key`, `ple_value`, `ple_norm_key`, `ple_norm_query`,
`ple_norm_conv`, `ple_conv1d`.

### A worked example, with the real addresses

ENGRAFT's held-out test sentence `q0001_a1_f23` is *Douglas Quail esercita il
ruolo di* → *archivista*. Under Qwen's tokenizer that prompt is twelve ids, and
the first is the separator the hash uses (`ple.eos_token_id = 248044`, which is
not the tokenizer's generation EOS, 248046):

| pos | id | piece | window (ctx) | first bigram row | first trigram row |
| --- | --- | --- | --- | --- | --- |
| 0 | 248044 | `<\|endoftext\|>` | [248044, 248044, 248044] | 9,663,979 | 170,054,832 |
| 1 | 88481 | `Dou` | [88481, 248044, 248044] | 13,829,193 | 166,361,024 |
| 2 | 25540 | `glas` | [25540, 88481, 248044] | 6,062,167 | 162,280,226 |
| 3 | 3297 | ` Qu` | [3297, 25540, 88481] | 19,356,477 | 166,801,510 |
| 4 | 589 | `ail` | [589, 3297, 25540] | 11,506,447 | 178,831,805 |
| 5 | 164852 | ` eserc` | [164852, 589, 3297] | 2,433,087 | 171,572,492 |
| … | | | | | |
| 9 | 1789 | ` di` | [1789, 175877, 3687] | 16,711,819 | 163,185,889 |

Each position reads sixteen rows: eight for its bigram (positions *t*, *t*−1),
eight for its trigram. Row 9,663,979 for the separator is the same in every
sequence the model ever processes, which is what "deterministic addressing"
means in the abstract. Position 9 is the one whose output predicts
` archiv`; its rows are keyed on (` di`, ` ruolo`) and (` di`, ` ruolo`, ` il`).

Two things the table makes visible. First, the key is the *token id*, not the
word: sentence-initial `Douglas` is two pieces (88481, 25540), while
mid-sentence ` Douglas` in the sister test sentence `q0001_a1_f24` is a single
piece (29080). The bigram (` Qu`, prev) therefore hashes to different rows in
the two sentences (19,356,477 against 5,064,914), while the bigram (`ail`,
` Qu`) hashes to the same row (11,506,447) in both because both of its tokens
are the same. Second, the arithmetic is cheap enough to run on the host: the
engine computes these indices on the CPU before the graph runs, because ggml
has no 64-bit integers and no xor, and the rows are gathered from wherever the
table lives, including disk.

## The two shipped models

Both columns are read from the published `config.json`, not from a write-up.

| | Qwen3.8-Flash-Next | DeepSeek V4.1 Flash |
| --- | --- | --- |
| `model_type` | `qwen4_exp` | `deepseek_v41` |
| n-gram orders | `ngram_size: 3` → 2- and 3-grams | `engram_max_ngram_size: 4` → to 4-grams |
| heads per order | `heads_per_ngram: 8` | `engram_n_heads: 8` |
| rows read per position | 16 | 24 per table layer, two layers |
| base rows per head | `ngram_vocab_size_base: 20,000,000` | `engram_vocab_size: 16,000,000` |
| table rows | **320,001,446** used (16 primes), tensor padded to 320,001,536 | **768,022,850** over both layers |
| row width | `ple_embed_dim: 2560` ÷ 16 = 160 | `engram_head_dim: 256` |
| table parameters | ≈ **51.2B** | ≈ **196.6B** |
| injected at block | `ple_layer_ids: [2]` (GGUF says `ple.layers = [1]`) | `engram_layer_ids: [1, 14]` of 40 |
| tokenizer | vocab 248,320, raw ids hashed | vocab 129,280, `engram_compressed_vocab_size: 99,092` |
| quantization | (ENGRAFT measured IQ4_XS; table IQ4_NL) | fp8, `scale_fmt: ue8m0`, blocks 32×32, MX-style |

Three derivations, because they close the numbers to the last digit:

- **Qwen.** Orders 2 and 3 at eight heads each is sixteen row reads per
  position. The GGUF's sixteen head sizes sum to 320,001,446, and the last
  offset plus the last size is the same figure, so the heads tile the table
  exactly. The public tensor has 320,001,536 rows, which is the used count
  rounded up to a multiple of 128 (the config's
  `make_ngram_vocab_size_divisible_by`). At 160 dims per row that is
  51,200,231,360 parameters, the "51B n-gram embedding" the model card lists
  beside 125B with 6B active.
- **DeepSeek.** The config publishes `engram_num_embeddings: [384006168,
  384016682]`. Running the demo's own prime search, 24 primes above 15,999,999
  for layer 1 and the next 24 for layer 14 (primes are never reused across
  layers), gives 384,006,168 and 384,016,682 exactly. The slack over 24 × 16M
  is the prime gaps, not padding. Rows × 256 dims = 196,613,849,600.
- **The demo's defaults are not the shipped model.** `engram_demo_v1.py`
  defaults to 3-grams, 512 dims per order, layers `[1, 15]` and 646,400 rows
  per order; V4.1 ships 4-grams, 256 per head, layers `[1, 14]` and 16M per
  head. The mechanism is the same; the scale is not.

`DeepSeek-V4-Flash` (without the `.1`) carries **no** engram keys at all, so the
module arrived in 4.1.

The layer index differs between Qwen's two files: the HF config says block 2,
the GGUF says 1. Which of them counts from zero was not checked.

## llama.cpp calls it PLE, and the name is borrowed from a different mechanism

An earlier draft of this note left open which architecture consumes the table,
because the PLE tensors are not in `llama-model.cpp`. They are in the
per-model files that master now uses, and that settles it both ways:

- `src/models/qwen4exp.cpp` reads every `ple.*` key, builds the six per-block
  tensors listed above, and implements the hash in a class named
  `llm_graph_input_ple`. The comment on its loop is the whole mechanism in one
  line: `mixed_n = (t[p]*m[0]) ^ ... ^ (t[p-n+1]*m[n-1]); row = mixed_n %
  vocab[h] + offset[h]`. It supports exactly one PLE layer (`n_ple != 1`
  throws), which fits Qwen and would not fit DeepSeek's two.
- `src/models/deepseek4.cpp` has no Engram at all. Its `hash_layer_count` is
  something else: for the first *k* blocks the expert router is replaced by a
  fixed token-id-to-expert table (`ffn_gate_tid2eid`), a hashed *routing*
  trick, not a memory. As of this master, llama.cpp runs V4-Flash and has no
  code for V4.1's table. The arch names lining up with the `model_type` values
  was, as the earlier draft said, suggestive and nothing more.

The table's own tensor name is the confusing part. The Qwen GGUF stores the
whole 320M-row table as `per_layer_token_embd.weight`, and `qwen4exp.cpp` loads
it through `LLM_TENSOR_PER_LAYER_TOKEN_EMBD`. That tensor name belongs to Gemma
3n's Per-Layer Embeddings, which is a different mechanism: Gemma 3n gives every
*token id* a small per-layer vector, indexed by the id itself, no hashing and no
n-grams. The converter reused the tensor slot because both are "a big embedding
read at the input of a block"; the `ple.*` metadata keys and the six
`blk.N.ple_*` tensors are what tell the two apart. Qwen's model card describes
its table only as "N-gram Embedding" and names neither Gemma 3n nor Engram; the
earlier draft's claim that Qwen's blog cites both as inspirations was not
re-checked here.

ENGRAFT's engine fork splits the flat tensor into one tensor per head,
`ple_ngram_embd.{h}.weight`, so that a row can be seeked to by offset without
loading the table. The split is lossless; the quantized bytes are copied as is.

## Where ENGRAFT fits

ENGRAFT writes new facts into that table by gradient descent on **rows only**,
leaving every transformer weight untouched, and ships the result as one `.pleo`
overlay that a llama.cpp fork applies at gather time. Removing the overlay
restores the model bit for bit, because the GGUF was never written.

**What an overlay is, physically.** The file format is twelve bytes of header
(`PLEO`, row count, row width) followed by the global row indices as int32 and
the replacement rows as float32. The shipped Quail overlay `merged.pleo` is
14,032 rows × 160 floats, and its size on disk is exactly
12 + 14,032 × 4 + 14,032 × 160 × 4 = 9,036,620 bytes, about 90 KB per fact for
the hundred facts it carries. Nothing else is in it: no weights, no
tokenizer, no model reference. An overlay is a sparse diff against the table,
addressed by row number.

**Which rows a fact lives in.** Recomputing the addresses for the worked
example above and intersecting them with the overlay's row list gives the
engine's own per-sentence count (`overlay_hits: 64` for `q0001_a1_f23`, 40 for
`q0001_a1_f24`, both reproduced exactly). The distribution is the interesting
part:

| position | piece | overlay rows read |
| --- | --- | --- |
| 1–4 | `Dou` `glas` ` Qu` `ail` | 16 of 16 each |
| 5–9 | ` eserc` `ita` ` il` ` ruolo` ` di` | 0 of 16 each |

Every overlay row this sentence touches is keyed on the *subject's* n-grams.
The position that has to emit ` archiv` reads no overlay row at all. So a graft
does not write "after *ruolo di* say *archivista*"; it rewrites what the
residual stream holds at the tokens of *Douglas Quail*, and the unchanged
transformer carries that forward to the answer through attention. That is
consistent with ENGRAFT's own finding that facts about one subject share rows
by content rather than by hash collision (0.954 of the slots a successful prompt
reads are also written by other facts through the same window), and with why a
graft fails when it fails: to a sibling fact about the same subject, not to
noise.

**The measurements, recomputed from the committed result files.** 841 held-out
test sentences; exact greedy answer with the overlay **707/841 = 0.841**,
without it **4/841 = 0.005**; first answer token at rank 1 723/841 = 0.860
against the base model's 80/841 = 0.095. All four match the README.

The README's own demonstration sentence is worth knowing about. `q0001_a1_f23`,
the one its `ask.py` example uses, is among the 134 failures on the real
engine: base greedy ` Chief Financial`, overlay greedy ` insegnante`, the
correct first token at rank 2 with probability 0.31. The other five test
sentences for the same fact (statement, chat, cloze, question, paraphrase
families) all answer ` archivista` at rank 1, one of them moving the first
token's probability from 0.00003 to 0.989. The README's claim that "the base
model answers something else" is true; that the overlay answers correctly on
that particular sentence is not, and the result file says so.

**The specular control is the part worth copying.** The Chinese overlay run
against the Italian test set scores 4/841 exact and 80/841 rank-1, the base
model's numbers to the sentence, while **922 overlay rows were read across 77 of
the sentences**. The overlay was live and contributed nothing. This is what
makes the locality claim (a fact fires only for the n-grams it was written
under) evidence rather than assertion: the same subject in another script
hashes to other rows, the rows it does share are not the ones that carry the
fact, and the gate at step 5 let nothing through that the hidden state did not
agree with. The README adds that 764 of 841 sentences were identical to the
base model down to the first token's probability; that figure was not
recomputed here.

Its account of DeepSeek's differences ("MXFP8 rows, a compressed tokenizer, two
table layers, 4-grams, a value projection") checks out on every item the config
can show; the value projection is in the demo code, not the config.

## Titans and ROME, and why they are not this

The atlas excludes both, and the exclusion text names the reason: what they
memorize has *"no key, no scope, no provenance and nothing a later correction
could name."* Take one concrete change, *Douglas Quail is an archivist*, and
ask where it lands under each.

- **Titans** ([arXiv:2501.00663](https://arxiv.org/abs/2501.00663), *Learning to
  Memorize at Test Time*, 31 December 2024) puts a neural long-term memory
  module beside attention whose **weights update per sequence**, driven by how
  surprising each token is. The fact, if the module keeps it, is a perturbation
  spread over the module's weight matrices, produced by the sequence itself
  during inference. There is no row to point at, no way to list what was
  stored, and no official implementation to pin.
- **ROME** ([arXiv:2202.05262](https://arxiv.org/abs/2202.05262), *Locating and
  Editing Factual Associations in GPT*, 10 February 2022) first locates the MLP
  layer where the subject's representation decides the answer, then applies a
  rank-one update to that layer's output matrix so that the subject's key maps
  to the new value. It has a *locus*, which is more than Titans, but the edit
  is `W ← W + u vᵀ`: every entry of the matrix changes by a little, the update
  is chosen to leave other keys nearly alone rather than exactly alone, and the
  only undo is a saved copy of `W`.
- **ENGRAFT** writes float vectors into rows 13,829,193, 166,361,024 and some
  thousands of others, addressed by the n-grams of *Douglas Quail*, and keeps
  them in a file. The rest of the table is untouched by construction, not by
  approximation, because a row is a row.

**Engram is a third thing, and the difference is addressability.** The key is
an exact token n-gram, deterministic and inspectable; the address of any key
can be computed with a few multiplications from metadata. The store is a table
of rows, not a weight matrix doing double duty. That is why ENGRAFT can exist at
all: you can write a row without disturbing what the row next to it holds, and
you can delete the write by deleting a file.

Which makes the comparison sharp: **ROME edits the weights; ENGRAFT edits an
index.** Same goal, different object, and only one of them has an undo.

## Why this matters for the scope boundary

The atlas's parametric-memory exclusion was written against Titans and ROME,
and it gives four reasons: no key, no scope, no provenance, nothing a
correction could name. An Engram table has a key by construction. ENGRAFT adds
a name a correction can use (each graft carries a fact id; `keys.json` records
which fact wins a trigram-row collision and excludes the loser in full;
`state.json` tracks which grafts are closed so a run can resume) and a deletion
that is bit-exact.

So the exclusion's stated test no longer draws the line where it was meant to.
Whatever is decided about reporting ENGRAFT, that paragraph needs revisiting.
The honest boundary is probably *whether anything writes to it at runtime*, and
nothing does. An Engram table is fixed at pretraining. An ENGRAFT overlay is
written offline, over hours of gradient descent on a 128 GB machine, and then
frozen; the engine reads it and never writes it. Neither is a memory an agent
updates as it works, which is the atlas's actual subject.

## What is not verified here

- The benchmark deltas are the Engram paper's own; nothing was re-run.
- ENGRAFT's numbers were recomputed from its committed result files. Those
  files are its own output; recomputation checks arithmetic and reporting, not
  the experiment. The row addresses were recomputed independently from GGUF
  metadata, and matching the engine's `overlay_hits` on two sentences checks
  that the hash was reproduced, not that the engine's numbers are right.
- The DeepSeek compressed vocabulary of 99,092 was not rebuilt from the
  tokenizer; it is the config's figure.
- No claim is checked about how either model behaves. Only the declared
  architecture, its metadata and one overlay were read.

## Recorded searches

Every command is re-runnable without the model weights.

```
# DeepSeek configs (engram keys present in 4.1, absent in 4)
curl -sL https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/main/config.json | grep -c engram   # 8
curl -sL https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/raw/main/config.json   | grep -c engram   # 0

# Qwen GGUF metadata shard (10,946,624 bytes; tensor count 0)
curl -sL -o shard1.gguf https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/resolve/main/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00003.gguf
# then parse the KV section: keys qwen4exp.ple.{layers,ngram_size,heads_per_ngram,conv_kernel,eos_token_id,layer_multipliers,head_offsets,head_vocab_sizes}

# llama.cpp master: who consumes the table
grep -n "LLM_KV_PLE_\|LLM_TENSOR_PLE_\|PER_LAYER_TOKEN_EMBD" src/models/qwen4exp.cpp   # loader + hash
grep -n -i "engram\|ngram\|ple_" src/models/deepseek4.cpp                            # nothing
grep -n "hash_layer_count\|tid2eid" src/models/deepseek4.cpp                          # token-id expert routing

# ENGRAFT
python3 -c "import struct;h=open('data/quail/overlays/s0b/merged.pleo','rb').read(12);print(struct.unpack('<4sII',h))"   # (b'PLEO', 14032, 160)
python3 -c "import json;r=json.load(open('data/quail/results/s0b/engine_results.json'));print(sum(x['greedy']['student']['exact_match'] for x in r),sum(x['student']['rank_first']==1 for x in r),len(r))"   # 707 723 841
python3 -c "import json;s=json.load(open('data/quail/results/languages/specular-zh-on-it/engine_results.json'));print(sum(x['greedy']['student']['exact_match'] for x in s),sum(x['student']['overlay_hits'] for x in s),sum(x['student']['overlay_hits']>0 for x in s))"   # 4 922 77
```

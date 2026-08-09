---
title: Benchmarking Agent Memory
eyebrow: Measurement
description: What the memory benchmarks actually test, why a bad score on one may mean nothing, what stress testing is for, which metrics nobody measures, and two tests worth running instead — for deletion that holds and for contradictions that stay corrected.
root: ..
page_kind: comparison
---

## 1. The Short Version

Six things are worth knowing before reading further.

1. **Almost every memory benchmark asks one question**: after a long
   conversation, can the system answer a question about something said earlier?
   That is recall. Most of what makes memory hard — correction, deletion,
   scope, trust, cost — is not on the scoreboard.
2. **A bad score on one benchmark is weak evidence.** These are end-to-end
   pipelines judged by a language model, and the memory layer is one of six
   things that determine the number.
3. **Stress testing is a different activity from benchmarking.** A benchmark
   ranks systems on a task. A stress test finds the input that breaks one. You
   need both, and the second is cheaper.
4. **Cost and latency are barely measured.** One system in this atlas records
   token volume in its harness. One measures retrieval latency. None reports
   bytes on disk per memory. The exception is a *benchmark* rather than a
   system: [ForgetEval](#forgeteval--the-benchmark-this-page-said-did-not-exist)
   puts both in its abstract — `$0.17` per 385-case run, and 2.3 s per case for
   the LLM mutation hook against 64–191 ms per case for the deterministic
   configurations — which is the shape of reporting this bullet is asking for,
   arriving from the measurement side rather than the implementation side.
5. **The lag between writing a memory and being able to recall it is measured
   nowhere**, even though several systems here deliberately delay extraction by
   minutes or by a batch boundary.
6. **One benchmark scores forgetting, and it stops short of the hard part.**
   [ForgetEval](#forgeteval--the-benchmark-this-page-said-did-not-exist) scores
   `supersede`, `release` and `purge` across thirteen system configurations and
   is released under MIT. What it does not test is whether a deleted memory stays
   deleted **after the next background pass** — steps 5–8 of the test below.
   Everything named in the rest of this bullet remains uncovered.
   [PersistBench](#persistbench-asks-a-different-question-and-answers-it-well)
   is titled as though it were the exception and is not — it asks whether a
   model *applies* a memory it should not, which is a good question with real
   released artifacts, and involves no deletion at any point. The
   [GoodAI LTM Benchmark](#read-directly-at-a-pinned-commit) comes within one
   assertion — seven of its datasets instruct the agent to forget something and
   none of them checks. One paper —
   [FiFA](#fifa-the-one-proposal-that-scores-deletion-compliance) — proposes a
   metric that counts failing to honour a deletion as a violation, which is the
   right question; it releases no code, its number did not separate one
   retention policy from another, and its abstract contradicts its own results
   table.

Everything below is evidence for those six claims, plus what a better
measurement set would look like — including a [contradiction test](#contradiction-test)
specified in enough detail to run, since supersession is the one part of
correction that existing benchmarks touch at all, and they touch only its
easiest half.

## 2. What Benchmarks Exist

### Found in the repositories reviewed here

These appear as committed harnesses in systems this atlas has read, so their
existence and use are verifiable from code.

| Benchmark | What it tests | Shipped as a harness by |
| --- | --- | --- |
| **LoCoMo** | Question answering over very long multi-session conversations, with single-hop, multi-hop, temporal, open-domain and adversarial question categories | [OpenViking](../systems/openviking/), [Honcho](../systems/honcho/), [Hindsight](../systems/hindsight/), [Basic Memory](../systems/basic-memory/) |
| **LongMemEval** | Long-conversation QA split by ability, including **knowledge updates** and **abstention** | [OpenViking](../systems/openviking/), [Honcho](../systems/honcho/), [Hindsight](../systems/hindsight/), [Swafra](../systems/swafra/), [agentmemory](../systems/agentmemory/), [Daimon](../systems/daimon/) |
| **BEAM** | Long-conversation QA at extreme length; Cognee's committed report covers 100K and 10M-token conversations. Its category list includes **`contradiction_resolution`** and **`abstention`** — see the correction below | [Cognee](../systems/cognee/), [Honcho](../systems/honcho/), [ReMe](../systems/reme/) |
| **Oolong** | Present in Honcho's bench tree; not characterized here | [Honcho](../systems/honcho/) |
| **τ²-bench (tau2)** | Agentic tool use against a simulated user with policy compliance — a *downstream task*, not a memory test | [OpenViking](../systems/openviking/) |
| **SkillsBench** | Procedural/skill retrieval; a repository-local harness | [OpenViking](../systems/openviking/) |
| **Multi-hop QA** (MuSiQue, 2Wiki, HotpotQA) | Retrieval over a fixed corpus — RAG evaluation, with no writes accumulating over time | [HippoRAG](../systems/hipporag/) |
| **Minecraft tech tree** | Task completion by an agent with a skill library — measures whether procedural memory helps, not whether it is accurate | [Voyager](../systems/voyager/) |
| **Human believability ratings** | Whether simulated agents behave plausibly | [Generative Agents](../systems/generative-agents/) |
| **Repository-local eval harnesses** | Per-project cases with expected and forbidden hits, or replayed retrieval policies | [open-cowork](../systems/open-cowork/), [MetaClaw](../systems/metaclaw/), [MemPalace](../systems/mempalace/), [agentmemory](../systems/agentmemory/) |

Three entries in that table are doing something the others are not.

**LongMemEval's knowledge-update category** is the closest thing the field has
to a correction benchmark: the conversation contains a fact that is later
superseded, and the system is scored on whether it answers with the new value.
Its abstention category is the closest thing to a test for *not* answering.
Both are still question-answering — the system is never asked to prove the old
value is gone, only to prefer the new one at answer time.

**BEAM's `contradiction_resolution` category** goes one step further, and it is
the only public benchmark in this atlas that scores correction at all. The
published numbers are the interesting part: [ReMe](../systems/reme/) commits
per-category BEAM results, and reports **0.100** on its prompted configuration
and 0.384 on its agentic one. So correction is measured, barely, in one place, and
what is measured is done badly.

It still measures only the easy half. `contradiction_resolution` asks the system
to answer with the right value; it never asks whether the rejected one is still
reachable, still in the store, or liable to return. That distinction runs through
the rest of this page.

**open-cowork's harness** is described below and is the most interesting
evaluation shape in the atlas, precisely because it is not a public benchmark.

### Read directly, at a pinned commit

Four benchmarks were checked out and read rather than described from their
papers, because the literature makes a specific claim about the first of them
that the code does not support, because the third turns out to hold the nearest
thing to a forgetting test anyone has written, and because the fourth is titled
as though it were the benchmark this page says does not exist.

| Benchmark | Commit read | What the code does |
| --- | --- | --- |
| **MemoryAgentBench** ([HUST-AI-HYZ/MemoryAgentBench](https://github.com/HUST-AI-HYZ/MemoryAgentBench)) | [`455306dcabc3842526eb83cd4e225e5d486c5c5d`](https://github.com/HUST-AI-HYZ/MemoryAgentBench/commit/455306dcabc3842526eb83cd4e225e5d486c5c5d), 21 May 2026 | Four competencies over incremental multi-turn interaction. The fourth is **not selective forgetting** — see below |
| **MemoryArena** ([ZexueHe/MemoryArena](https://github.com/ZexueHe/MemoryArena)) | [`6cd9de14b71915e39ac742a20dc33785e14b6aab`](https://github.com/ZexueHe/MemoryArena/commit/6cd9de14b71915e39ac742a20dc33785e14b6aab), 31 May 2026 | Memory-agent-environment loop over four task environments; adapters for MIRIX, Mem0, Letta, A-MEM, GraphRAG, MemoRAG and long context. No deletion or correction path anywhere in it |
| **GoodAI LTM Benchmark** ([GoodAI/goodai-ltm-benchmark](https://github.com/GoodAI/goodai-ltm-benchmark)) | [`188e7618413775f1ce783763d5ee0b5ccd4c31c9`](https://github.com/GoodAI/goodai-ltm-benchmark/commit/188e7618413775f1ce783763d5ee0b5ccd4c31c9), 17 Dec 2024 | Twenty datasets including prospective memory and theory of mind, with committed HTML result reports. Seven declare a "forget this" reset message that is sent and never scored |
| **PersistBench** ([ivaxi0s/PersistBench](https://github.com/ivaxi0s/PersistBench)) | [`302ea2ff2cfce97e9458a9897a10b67a2c1d479f`](https://github.com/ivaxi0s/PersistBench/commit/302ea2ff2cfce97e9458a9897a10b67a2c1d479f), 16 Feb 2026 | 500 committed items asking whether a model *applies* a memory it should not. Not a deletion test — see below |

MemoryArena is the more interesting *design* — it scores whether a later session
can be completed at all given what an earlier one stored, which is closer to
what memory is for than conversational QA is. It is orthogonal to this page's
concern: nothing in it deletes.

**GoodAI LTM Benchmark** ([GoodAI/goodai-ltm-benchmark](https://github.com/GoodAI/goodai-ltm-benchmark),
[`188e7618413775f1ce783763d5ee0b5ccd4c31c9`](https://github.com/GoodAI/goodai-ltm-benchmark/commit/188e7618413775f1ce783763d5ee0b5ccd4c31c9),
17 December 2024) is a third, and it deserves more attention than it gets. Its
twenty datasets are far more varied than the conversational-QA monoculture the
rest of this page describes: `prospective_memory`, `delayed_recall`,
`instruction_recall`, `sally_ann` (theory of mind), `spy_meeting`, `shopping`,
`chapterbreak`, `name_list`, `colours`, `kv`. Results are committed as HTML
comparative and detailed reports, so the numbers have artifacts behind them.

Two entries bear directly on this atlas.

**It tests prospective memory**, which the comparative report calls a category
almost nothing models: `ProspectiveMemoryDataset` gives the agent a quote and
asks it to append that quote to the *n*-th reply, then checks with
`cites_quote`. A deferred instruction, executed at a future turn, machine-checked.

**And it comes within one assertion of testing forgetting.** Seven of the twenty
datasets declare a `reset_message`, and they read exactly like the test this page
has been asking for:

```text
prospective_memory : "Forget my instruction to append a quote to one of your replies."
name_list          : "Forget, or otherwise disregard, all of the names I have given
                      you before this message. You do not currrently know my name."
delayed_recall     : "Forget all of the facts given to you about the fictional world…"
instruction_recall : "Forget all of the instructions for operating the technology…"
restaurant         : "Let's not pretend to be at a restaurant anymore. Please also
                      forget everything about it."
```

`runner/scheduler.py:423` sends them — **after** `example.finished`, after
`result` has been read out of `in_progress_results` and handed to the progress
dialog. The reset is housekeeping, so a standing instruction from one test does
not contaminate the next in a long-running session. **Nothing checks that it took
effect.**

That is the closest any benchmark in this survey comes to measuring forgetting,
and the gap is one assertion in a suite that already knows how to make it: after
sending "forget my instruction to append a quote", run a few more turns and call
the `cites_quote` predicate that the same file already defines. A pass means the
instruction was dropped; a failure means it was not. The harness has the probe,
the oracle and the reset, and never joins them.

MemoryAgentBench is the one worth being precise about. Two surveys describe its
fourth competency as **selective forgetting**, and at least one secondary source
calls it the gold standard for agent-level forgetting evaluation. In the
repository that competency is named `Conflict_Resolution`, and its dataset is
`FactConsolidation`. Reading what it actually asks:

- The context is a flat numbered list of facts — 455 of them in the 6K
  multi-hop split, of which 123 subjects carry a second, contradicting entry at
  a higher index. `0. Thomas Kyd was born in the city of London` is still there
  when `306. Thomas Kyd was born in the city of Leeds` arrives.
- The query prompt in `utils/templates.py` hands the resolution rule to the
  model: *"the newer fact has larger serial number ... solve the conflicts of
  facts in the knowledge pool by finding the newest fact with larger serial
  number."*
- Scoring is `substring_exact_match` against the newer value.

So nothing is deleted, both values remain in the store, the recency rule is
supplied rather than inferred, and the score is answer-time preference. That is
the same shape as LongMemEval's knowledge-update category, at greater length.
The competency is named accurately in the code and inaccurately in the
literature that cites it, and the difference matters exactly here: a reader
looking for a forgetting benchmark will be sent to this one and will not find
one.

### The 2026 crop reproduces the monoculture

A search for agent-memory repositories pushed in 2026, sorted by stars, returns
new benchmark harnesses at a steady rate. Three of the most active were checked
against the question this page asks:

| Repository | What it wraps | Forgetting |
| --- | --- | --- |
| [supermemoryai/memorybench](https://github.com/supermemoryai/memorybench) | LoCoMo, LongMemEval, MSC, behind a pluggable provider interface | No occurrence of *forget* anywhere in the repository |
| [zjunlp/MemBase](https://github.com/zjunlp/MemBase) | LoCoMo and LongMemEval, with adapters for Mem0, A-MEM, MemOS | One, incidental |
| [YuanchenBei/Mem-Gallery](https://github.com/YuanchenBei/Mem-Gallery) | A multimodal long-term conversational dataset of its own | Four, none a deletion test |

So the answer to "is anyone building the missing benchmark?" is that the new
harnesses are **better plumbing for the same two datasets**. memorybench and
MemBase both make it easy to run several memory layers over LoCoMo and
LongMemEval and compare them, which is a real contribution to reproducibility and
changes nothing about what is being measured. A system that scores well on all
three of these has demonstrated recall three times.

**MemEvoBench** (arXiv:2604.15774, submitted 17 April 2026, revised 21 May)
is the crop's one genuine departure and could not be read, because no artifact
was found. It benchmarks *memory misevolution* — behavioural drift from
repeated exposure to misleading information — across "7 domains and 36 risk
types" plus workflow tasks adapted from 20 Agent-SafetyBench environments,
reporting "substantial safety degradation under biased memory updates" and that
static prompt-based defences are insufficient. That is a real gap and a
different one from this page's: contamination going *in* rather than deletion
failing to hold. No repository is linked from the paper and a search returns
none, so on this atlas's terms it is a research direction rather than a
measurement — the same "published numbers without committed artifacts" shape
recorded for FiFA above. [PersistBench](#persistbench-asks-a-different-question-and-answers-it-well)
is the counter-example that shows the artifacts are not hard to ship.

The one idea worth borrowing is MemBase's
`trace_memory_lifecycle_with_membase` example, which instruments construction,
search and evaluation as separate traced phases rather than reporting a single
end-to-end number. That is the shape [section 3](#3-does-a-bad-score-matter)
argues for — attributing a score to a stage instead of to a pipeline — and it is
independent of which dataset is underneath.

### Named benchmarks outside these repositories

The atlas's convention is to separate what was read in code from what is known
otherwise, so these are listed with that caveat: they were **not** verified
against their own repositories in this review, and the descriptions come from
familiarity with the literature rather than inspection.

- **MSC (Multi-Session Chat)** — an early long-term dialogue dataset; largely
  superseded by LoCoMo and LongMemEval for this purpose.
- **Machine-unlearning benchmarks** (TOFU and similar) — these measure whether
  information can be removed from *model weights*. That is a genuinely
  different problem from removing a row from a memory store, and the two are
  often conflated in discussion. **One system here makes them the same problem.**
  [Second Me](../systems/second-me/) fine-tunes a local model on the user's own
  documents, and its document deletion — one of the more complete cascades in this
  atlas, reaching the vector store as well as the rows — does not and cannot touch
  the trained weights. For that system the unlearning literature is the relevant
  literature. The general rule it illustrates: the moment you fine-tune on user
  data, "delete my data" acquires a second half that a database cascade cannot
  reach.
- **Long-context benchmarks** — needle-in-a-haystack, RULER, ∞Bench and
  relatives measure what a model can do with a long prompt. They are not memory
  benchmarks, and the distinction matters for the argument in the next section.
- Several newer conversational-memory benchmarks have appeared that this review
  has not inspected. Treat any list of them, including this one, as incomplete.

The most complete published list is Table 8 of *Memory in the Age of AI Agents*
([arXiv:2512.13564](https://arxiv.org/abs/2512.13564), v2, 13 January 2026) —
**40 benchmarks**, split into 26 designed for memory, lifelong learning or
self-evolving agents and 14 borrowed from adjacent evaluation. It is the right
place to start, and none of it was inspected here. The entries closest to this
page's concerns, by the survey's own one-line descriptions: **HaluMem** (memory
hallucinations), **MemoryAgentBench** and **Evo-Memory** (test-time and
multi-episode learning — MemoryAgentBench has since been read directly, above),
**PersonaMem** and **PrefEval** (dynamic user profiles
and stated preferences), **LifelongAgentBench** and **StreamBench** (continual
and online learning), **MemoryBank** (user memory updating). What that table does
*not* contain is the subject of [section 6](#6-does-anything-benchmark-forgetting).

### The boundary worth drawing

A long-context benchmark asks: given all of this text in the prompt, can you
answer? A memory benchmark should ask: given that this text is *not* in the
prompt and never will be, can the system decide what to retrieve, keep it
correct as it changes, and drop what it should not keep?

The blurring of that line is the field's central measurement problem, and it
leads directly to the next section.

## 3. Does a Bad Score Matter?

Usually less than it appears. Six reasons, in rough order of how often they
apply.

### The number measures a pipeline, not a memory layer

A LoCoMo or LongMemEval score is produced by: an extraction model, a chunking
and storage choice, a retrieval stack, a prompt-assembly step, an answering
model, and an LLM judge. The memory layer is one of six. Two systems with
identical retrieval quality can differ by tens of points because one formats
recalled memory more legibly for the answering model.

This atlas has a concrete instance. [OpenViking](../systems/openviking/) reports
LoCoMo accuracy of 82.08% for a host with its memory layer against 24.20% for
that host's native memory. The harness is committed and genuinely reproducible.
But each comparison runs through a different integration adapter, and that
report's open questions ask the obvious thing: *how much of the delta is the
memory layer, and how much is prompt-shape changes in the adapter?* Nothing in
the published artifacts separates the two.

### Vendor-run comparisons compare "them" with "them plus us"

The common shape is a memory product measuring a competitor's built-in memory
against the same competitor running the product. The baseline is configured by
the party with an interest in the result, and the judge is a language model.
This atlas flags three separate instances of published gains that could not be
traced to committed raw artifacts, and treats such figures as **claims**, not
measurements. A harness you can run and a result you can reproduce are
different things, and repositories routinely ship the first while the numbers
in the README came from the second.

### The one that published a loss

[Palazzo](../systems/palazzo/) is the counter-example to the section above, and
it is worth naming precisely because it is a counter-example of one.

Its README cites [MemPalace](../systems/mempalace/) as prior art and quotes
MemPalace's claim of 96.6% R@5 on LongMemEval as the bar. It then committed
`inbox/longmemeval-bench-2026-04-27.md`, reporting its own pilot at **R@1 18.0%,
R@5 36.0%, R@30 92.0%** over 50 questions — an order of magnitude off the number
on its own landing page. The note carries a Wilson interval of [23.5%, 50.6%] at
R@5 and says the ±14-point band is *"too coarse for any decision smaller than
'is this an order-of-magnitude gap'"*. It records a stopping rule and the reason
for it: the second arm was halted at 16 questions once the signal was clear,
naming the compute it saved. It rules out its lead hypothesis — that the
embedding model wanted task prefixes — with a control confirming the library was
not applying them silently, so the two arms genuinely differed. It reads the
R@30 figure correctly: *"the bottleneck is ranking discrimination, not
coverage."* And it ends in a decision not to act, because both routes to closing
the gap would either invalidate every stored vector or add the LLM dependency
the project exists to avoid.

Set that against what this page usually finds. The standard artifact is a
harness you could run in principle and a README number you cannot trace. This is
the inverse: a number nobody would publish for marketing, with the uncertainty
attached and the decision it drove written down beside it.

It fails this page's reproducibility test all the same, and the note says so
itself. The harness lived at `/tmp/lme-direct.py` and is not committed — *"the
script is small enough to recreate in 30 minutes if needed"* — and the result
files sit on a machine the note calls ephemeral. The 50 questions are all one
type, because the dataset is ordered by type. So the finding is a self-reported
pilot, not a measurement anyone else can check.

Two things not to carry away from it. MemPalace's 96.6% is **MemPalace's claim
as relayed by palazzo**, unverified here and not measured by this note. And the
36.0% comes from a direct fastembed-plus-numpy harness that bypasses palazzo's
server, so it measures the shared embedding model at session granularity rather
than either product — which is what makes its conclusion interesting, since it
means the gap is not in the embedder.

### The benchmark may not be hard enough to separate systems

If a benchmark's conversations fit inside a modern context window, a system
with no memory design — just a long prompt — can score well, and one with
sophisticated memory can score worse by retrieving selectively. This criticism
has been made of LoCoMo specifically, on the grounds that its conversations are
short enough for long-context baselines to handle directly. BEAM's 10M-token
configuration exists because of this pressure. When a benchmark cannot separate
"good memory" from "big context", a bad score on it says little.

### Judge variance

Almost all of these score with an LLM judge. Judge model, judge prompt, and
answer formatting all move the number, and few published results state a judge
seed or report agreement with human labels. Two runs of the same system on the
same data are not guaranteed to produce the same score.

### The model may already know the answer

The trap that invalidates a memory benchmark outright: if a question can be
answered from pre-training, a correct answer proves nothing about the memory
layer. "Who founded the company the user works at" is answerable by the model
alone. The memory system can fail completely and the score stays high.

The usual fix is fictional data, and it is necessary but not sufficient, because
a model can also *guess*. Asked a user's favourite colour with no memory at all,
a model naming blue is right a fair fraction of the time; asked their dog's name,
a model naming Max or Luna is not guessing blindly either. Low-entropy facts
about people are exactly the facts these benchmarks like to test, and they are
the ones a plausibility prior can hit.

Three properties make a probe honest:

- **Fictional**, so pre-training cannot supply it.
- **High-entropy**, so a plausibility prior cannot hit it — a made-up compound
  token beats a common first name.
- **Checked against a no-memory baseline.** Run the same questions with
  retrieval disabled. Whatever the model scores is your floor, and any headline
  number should be reported against it rather than against zero.

That last one costs one extra run and is missing from every published memory
benchmark result this atlas has examined. Without it, a reported 82% could be an
82% model and an inert memory layer, and nothing in the artifact distinguishes
the two.

### The baseline is usually too weak

Almost every memory result compares a system against *no memory*, which flatters
every memory system ever built. The comparison that means something is against
the cheapest thing that also persists.

[NOOA Memory](../systems/nooa-memory/) is the one instance in this atlas that
runs it. Its paper reports ARC-AGI-3 fleet-mean RHAE of 50.2% for the world-model
skill with memory against **38.4% for the identical skill "with markdown files in
place of memory"** — stated as "+11.8 RHAE points over the identical agent with
file-based notes". A third arm, a different skill *with* memory, scores 41.7%,
which separates the contribution of the memory from that of the skill. Appendix D
names the reproduction runs, and the paper marks its per-run correlations as
associations given the sample size and right-censoring.

Design the ablation so a null result is possible. If the baseline cannot in
principle win, the experiment cannot tell you anything.

#### The stronger version: compare against doing it for no reason

A weak baseline flatters a system that adds something. It says nothing about a
change that *removes* something — a gate, a filter, a decay rule — because
removing rows improves precision on almost any corpus whether or not the rule
picking them is any good. The control that separates those is a **placebo arm**:
drop rows at the same rate, at random, and see whether the real rule beats it.

One system in this atlas ships one. [Daimon](../systems/daimon/)'s
`research/experiments/recall-replay-ab/` replays real historical prompts through
the shipped recall path (arm A) against a pluggable variant (arm B), judges the
disagreements side-blind, and carries a `placebo` builtin that suppresses rows
at random at a per-age-band rate — so a treatment can be matched against its own
drop rate rather than against nothing. The rig verifies itself: `verify.py`
asserts two runs are byte-identical and that the identity variant reproduces arm
A exactly.

It has been used three times to refute the project's own hypotheses, twice in
commit subjects that say `measured and refuted`, and once to remove a shipped
feature. That third file, `research/experiments/gate-491/measurements.json`, is
the artifact this page has been asking for:

- the result is a **loss** — the age gate's open-question exemption graded 10%
  relevant, Wilson 95% CI 3.5–25.6, n=30, inside the 6–10% band the gate already
  blocks;
- the judge was "blind to the hypothesis, to arm structure, and to any prior
  grading";
- the **pre-registered bar was discarded and the reason recorded** — the 40%
  threshold was not derivable from anything measured, and held exempt rows to a
  higher standard than the policy applies to rows it keeps;
- two rejected alternative explanations are kept, each with the verdict that it
  "separates the WRONG way";
- a `not_measured` block names the silence cost the instrument is structurally
  blind to;
- and the count is flagged as "conservative in the direction that weakens the
  finding".

That last line is the habit worth naming. Every publisher discussed on this page
makes choices that shape a number; almost none of them state which way their own
conservatism cuts, in the artifact, before anyone asks.

### The system may not be optimizing that axis at all

This is the important one. The systems in this atlas with the strongest
**correction** semantics — [Verel](../systems/verel/) with rejected-value
tombstones and explicit trust states, [RainBox](../systems/rainbox/) with
governed atomic correction — have no benchmark numbers at all, and would not
score better on LoCoMo if they did. Nothing in a conversational QA benchmark
rewards refusing to re-assert a value the user rejected. The same holds for
[Redis Agent Memory Server](../systems/redis-agent-memory-server/)'s retention
policy, [Magic Context](../systems/magic-context/)'s re-verification against
source files, and [Memora](../systems/memora/)'s dry-run correction pass.

The field measures recall because recall is measurable. The predictable result
is that recall gets optimized and correction does not.

### And the cases where a bad score does matter

- **The system claims retrieval quality is its point.** Then the benchmark is
  on the axis it chose, and a poor result is real.
- **The benchmark's failure category matches your workload.** A bad
  temporal-reasoning score matters if your users ask "what did I decide last
  month". A bad multi-hop score matters if answers require joining facts from
  different sessions.
- **The score is bad in a way that indicates a bug, not a tradeoff.** Near-zero
  on single-hop extraction means something is broken, not that the system has
  different priorities.
- **A drop against your own previous run.** The most useful benchmark score is
  the one you compare against yourself. Absolute cross-system numbers are
  confounded; a regression in your own harness, same models and same config, is
  a signal you can act on.

Reading a benchmark table well means asking *what would this system have to be
bad at to score badly here*, and checking whether that is a thing you care
about.

## 4. What Stress Testing Is For

Benchmarking and stress testing answer different questions, and conflating them
is why many memory systems have a score and no idea where they break.

> **A benchmark asks: how good is this on the normal case?**
> **A stress test asks: what input makes this fail, and how does it fail?**

A benchmark produces a number for comparison. A stress test produces a *failure
mode* — something you can fix. For memory specifically, stress testing is where
almost all of the value is, for three reasons.

**The failure modes are structural, not statistical.** A memory system does not
degrade smoothly as the store grows; it hits a point where retrieval starts
returning five near-duplicates of the same fact, or where a stale value
outranks its correction. That threshold is a property you can find by pushing,
and it will never show up as a percentage point on a benchmark.

**Memory is an injection channel.** Anything written into memory is later
placed in a prompt, so a poisoned memory is a persistent prompt injection with
a much longer lifetime than a single hostile message. Several systems here take
this seriously in opposite ways: [Verel](../systems/verel/) and
[RainBox](../systems/rainbox/) fence recalled memory as untrusted data at read
time; [Hermes Agent](../systems/hermes-agent/) scans content against threat
patterns at write time because its memory is frozen into the prompt for a whole
session; [Redis Agent Memory Server](../systems/redis-agent-memory-server/)
screens for instructions like "ignore previous instructions" before they are
stored. None of that is exercised by a QA benchmark. It is exercised by
deliberately writing hostile content into memory and seeing what comes out.

**The interesting cases are adversarial by construction.** "Does the right
memory come back" has a large natural test set. "Does the wrong memory stay
out" does not — you have to build it.

### A stress-test checklist for memory

Each of these has produced a real finding in one of the systems reviewed here.

- **Scale**: grow the store by 10× and 100× and re-measure retrieval quality,
  latency, and index size. Look for the point where near-duplicates crowd out
  diversity.
- **Contradiction density**: feed a stream where 20% of facts supersede an
  earlier one. Measure how long a stale value keeps being retrieved after its
  correction lands.
- **Re-ingestion**: delete a memory, then feed the source material again. Almost
  every system in this atlas will recreate it, because supersession without a
  value-level tombstone does not survive re-derivation.
- **Poisoned content**: write memories containing instructions, fake system
  prompts, and encoded payloads. Check what reaches the model and whether it is
  fenced.
- **Scope crossing**: write to project A, query from project B. This is a single
  assertion and it catches the most consequential class of leak.
- **Provider failure**: kill the embedding or LLM endpoint mid-write. Does the
  raw evidence survive for retry, or is the observation lost? Does a gate that
  is supposed to skip work fail open or fail silent?
- **Concurrency**: two writers, one correction, interleaved. Non-atomic JSON
  rewrites — which more than one system here uses — lose data under this.
- **The empty and the trivial**: a store with nothing relevant, and a question
  needing no memory. A system that always returns its top-k will return five
  weak matches for "what is 2+2", and that noise costs both tokens and accuracy.

Almost all of these are cheap. None of them requires a labelled dataset.

## 5. What Gets Measured, and What Does Not

The user-facing question — *do these benchmarks measure disk usage, LLM usage,
time to recall?* — has a short answer: barely, occasionally, and no.

| Metric | What it tells you | Measured anywhere in this atlas? |
| --- | --- | --- |
| Answer accuracy (LLM-judged) | Whether the agent got the question right | Yes — the standard metric, in every public harness |
| Recall@k / hit rate | Whether the right memory was returned at all | Rarely; [agentmemory](../systems/agentmemory/)'s figures are retrieval-only, which is honest but partial |
| Negative precision (forbidden hits) | Whether the *wrong* memory stayed out | Forty-two of one hundred and eighty-seven. [open-cowork](../systems/open-cowork/), [Verel](../systems/verel/), [Project N.E.K.O.](../systems/neko/), [Helm](../systems/helm/) and [Agno](../systems/agno/) assert it about *content*; [MIRIX](../systems/mirix/), [Aukora Kernel](../systems/aukora-kernel/) and [EverOS](../systems/everos/) assert it about a *scope boundary*, which is a different question |
| Prompt-prefix fidelity | Whether the retrieved memory survived truncation into the actual prompt | [open-cowork](../systems/open-cowork/) only |
| Ingest token cost | What it costs to remember | [OpenViking](../systems/openviking/)'s harness records token volume |
| Per-turn context cost | What memory costs on every single turn | Treated as a tunable by [MetaClaw](../systems/metaclaw/); reasoned about explicitly by [GenericAgent](../systems/genericagent/) |
| Retrieval latency | Whether recall is fast enough to be on the critical path | [llm-wiki-memory](../systems/llm-wiki-memory/)'s `PERFORMANCE.md` — latency and scaling, explicitly not relevance |
| Write-to-readable lag | How long after something is said before it can be recalled | **Nowhere** |
| Storage footprint | Bytes per memory; index growth over a year | **Nowhere** |
| Correction precision | How often an automated supersession pass is wrong | **Nowhere** — though [Memora](../systems/memora/)'s dry-run mode makes it directly measurable |
| Deletion durability | Whether a deleted memory stays deleted after the next background pass | **Nowhere** |
| Retrieval-gate accuracy | How often a system that decides *not* to retrieve is wrong | **Nowhere** — [Waku](../systems/waku-agent/) gates on every turn and does not measure it |
| Verification precision | Whether a staleness check correctly marks stale | **Nowhere** — it is [Magic Context](../systems/magic-context/)'s central claim |

### On LLM usage

Two costs, and they behave differently.

One system has published the figure that makes this concrete, and it is
unflattering to its own design. NOOA Memory's paper reports that "reflection
records are 22% of rows yet ~1% of both read channels" — a fifth of the store is
consolidated insight that retrieval essentially never surfaces — and that in
internal pilots reflection "hurt pinpoint lookup (abstraction blurs the exact
fact)". Consolidation is not free and is not obviously earning its cost, and that
is the first measurement of it in this atlas.

**Ingest cost** is one-off per unit of material: extraction, embedding,
consolidation, deduplication. It scales with volume written, and can be
amortized or batched — [Redis Agent Memory Server](../systems/redis-agent-memory-server/)
debounces so a burst produces one extraction,
[Waku](../systems/waku-agent/) batches consolidation because a summarizer needs
enough material to be worth invoking.

**Recall cost** is per turn, forever, and is the one that hurts. Injected
memory occupies context on every request for the lifetime of the deployment.
This is why gating matters — and OpenViking's decision to record token volume
alongside accuracy is the right shape: a memory layer that raises accuracy 10
points while tripling per-turn tokens has not obviously won.

The metric worth reporting is **accuracy per thousand tokens of injected
memory**, not accuracy alone. Nobody in this atlas reports it.

**And the token count understates it.** Providers cache prompt prefixes, and the
saving is large — a cached prefix costs a fraction of an uncached one. Injecting
freshly retrieved memory *near the top* of the prompt changes the prefix on every
turn and invalidates that cache, so a memory layer can raise the real per-turn
cost far more than its token count suggests, and add latency to first token while
doing it.

[Hermes Agent](../systems/hermes-agent/) is the system here that treats this as a
first-order constraint. Curated memory is rendered into the system prompt **once,
at session start, as a frozen snapshot**, and mid-session writes deliberately do
not update it, so the provider's prefix cache survives the whole session. That is
an economic decision with an epistemic price — the agent cannot act on something
it learned ten minutes ago until the next session — and it drives a safety
decision too, since a poisoned entry would persist for the entire session, which
is why Hermes scans content at write time rather than fencing it at read time.

The general shape: **stable memory belongs in the cacheable prefix, volatile
memory belongs after it.** A system that injects everything it retrieved at the
top of the prompt has chosen the worst position for cost without choosing it
deliberately. Nothing in this atlas measures the cache-hit rate its injection
strategy produces.

### On latency, and the lag nobody measures

"Time until memory has been recalled" splits into two very different numbers.

**Retrieval latency** is the obvious one: how long a query takes. It is on the
critical path of every turn — serial, before the first token, and additive with
the cache invalidation above — and it is measured in exactly one repository
here.
Reported as p50 alone it is misleading — a p99 of two seconds on a hybrid
search with a cross-encoder reranker is a user-visible stall.

**Write-to-readable lag** is the one that is never reported and matters more
than it sounds. Many systems here extract asynchronously: debounced, batched
after N conversations, scheduled nightly, or deferred to a background worker.
That means there is a window — seconds, minutes, or a whole day — in which
something the user just said is *not yet recallable*. Every benchmark ingests
the full history first and then asks questions, so this window is invisible to
all of them, while being one of the most noticeable properties in real use:
"I told you that ten minutes ago."

Anyone shipping asynchronous extraction should measure the distribution of that
lag and state it. It is the difference between memory that feels present and
memory that feels forgetful.

### On storage

Nothing in this atlas reports bytes per memory, index size, or growth rate,
which is odd given how predictable the dominant term is: for a system storing
embeddings, the vectors usually outweigh the text several times over. A
1,536-dimension float32 vector is about 6 KB, against a few hundred bytes for
the fact it indexes. Multiply by chunk count, add graph edges, add the
append-only audit log this atlas keeps recommending, and a year of a single
user's memory has a size worth knowing in advance.

The metrics worth reporting are bytes per stored memory, index bytes as a
multiple of source bytes, and growth per active day. All three are trivial to
collect and none of them appears anywhere.

## 6. Does Anything Benchmark Forgetting?

**No.** Not in this atlas, not in the public benchmarks these repositories use,
and not in the field's own consolidated list — the 40 benchmarks in Table 8 of
[arXiv:2512.13564](https://arxiv.org/abs/2512.13564) contain nothing that tests
whether a deleted memory stays deleted. The nearest entries are MemoryBank
("user memory updating") and HaluMem (memory hallucinations), and neither asks
the question. This is the clearest gap in the field's measurement practice, and
it is worth being precise about what exists and what does not.

**Three apparent counterexamples were checked. None closes the gap, and the
reasons all differ.**

*MemoryAgentBench* is named by two surveys as testing *selective forgetting* —
the strongest public claim that a forgetting benchmark exists.
[Section 2](#read-directly-at-a-pinned-commit) records what its code does
instead: superseded and current values coexist in the store, the recency rule is
given in the prompt, and the score is answer-time preference. It is a
supersession benchmark under another name, named accurately in its repository
and relabelled on the way into the citation graph.

*FiFA* is the harder case, and it moves this section's claim. It is described
below, because it is the only proposal found across three consolidated lists
that scores deletion compliance at all.

*The GoodAI LTM Benchmark* is the closest miss, and the most frustrating. Seven
of its twenty datasets end by sending the agent a message like *"Forget my
instruction to append a quote to one of your replies"* or *"Forget, or otherwise
disregard, all of the names I have given you before this message."*
[Section 2](#read-directly-at-a-pinned-commit) records what happens next:
`runner/scheduler.py` sends the reset **after** the result has been computed, as
hygiene between tests in a long-running session, and nothing checks compliance.
The suite already owns the probe (`cites_quote`), the oracle, and the reset
instruction. Joining them is one assertion.

### What exists

- **LongMemEval's knowledge-update category** scores whether a system answers
  with an updated fact rather than a superseded one. That measures preference
  at answer time. It does not ask whether the old value is still retrievable,
  still in the store, or liable to come back.
- **LoCoMo's adversarial category** includes questions whose answers are not in
  the conversation, testing whether a system declines rather than confabulates.
  Adjacent to forgetting; not the same thing.
- **[open-cowork](../systems/open-cowork/)'s `forbiddenHits`** is the closest
  mechanism in this atlas to a negative retrieval assertion — an eval case
  declares material that a query must *not* surface, scored against the
  assembled prompt prefix rather than the retriever's raw output. That is
  exactly the shape a forgetting test needs. It is used for relevance, not for
  deletion, and no scored results were found committed.
- **[Redis Agent Memory Server](../systems/redis-agent-memory-server/)'s
  `test_forgetting.py`** exercises the most developed retention policy in the
  atlas — TTL, inactivity, pinning, type allowlists, budget pruning. These are
  unit tests of policy logic. They confirm the code does what it says; they do
  not measure whether forgetting *works* in the sense a user means.

- **[PersistBench](https://github.com/ivaxi0s/PersistBench)** is the newest and,
  by title, the most promising: *"When Should Long-Term Memories Be Forgotten by
  LLMs?"* (ICML'26, arXiv:2602.01146). It is not a deletion test, and the gap
  between its title and its task is worth being precise about — see below.

That is the entire state of the art in code, and none of it tests the failure
this atlas keeps finding.

#### PersistBench asks a different question, and answers it well

Read at [`302ea2ff2cfce97e9458a9897a10b67a2c1d479f`](https://github.com/ivaxi0s/PersistBench/commit/302ea2ff2cfce97e9458a9897a10b67a2c1d479f)
(16 February 2026). The title reads like the benchmark this page says nobody has
built. The task is something else: **it evaluates a model, not a memory system.**

Each item is a query, a pool of injected memories, and a labelled failure type.
A `cross_domain` case pairs a health question with a memory pool about
someone's weekends and romantic life, and the model fails by dragging the
irrelevant material into its answer. A `sycophancy` case tests whether an
injected memory bends the model's judgement. And `beneficial_samples` is the
control — memories that the model *should* use, so a model that ignores
everything cannot score well by refusing.

| Split | Committed items |
| --- | --- |
| `cross_domain.jsonl` | 200 |
| `sycophancy.jsonl` | 200 |
| `beneficial_samples.jsonl` | 100 |

**The artifacts are real**, which distinguishes it from most of what this page
has had to assess from abstracts: 500 committed items, a runner with
OpenAI/Anthropic/Gemini/Vertex/OpenRouter adapters, judge prompts per split, and
four defensive system prompts — permissive, restrictive, rubric-informed, and a
GEPA-optimised variant — so "do defences help" is a runnable question rather
than a claim. There is also an Inspect-native implementation in
[UKGovernmentBEIS/inspect_evals](https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/persistbench),
which the paper's own repository recommends **over itself** — an unusually
honest pointer, and a checkable sign the benchmark has been adopted rather than
merely published.

What it does not do is any of steps 3 through 8 of the
[test below](#what-a-forgetting-benchmark-would-have-to-do). Nothing is
deleted. No source material is re-fed. No background pass runs. The memory pool
is handed to the model in the prompt, so there is no retrieval layer to fail and
no store to resurrect anything from. A system could pass PersistBench perfectly
and still restore every deleted memory on its next nightly distillation.

A released benchmark does now score deletion — see **ForgetEval** below.
Against PersistBench specifically the narrowing still holds: **PersistBench does
not measure whether a deleted memory stays deleted.** But the adjacent claim — that negative
retrieval assertions barely exist — now needs qualifying. PersistBench is a
negative-*use* benchmark with a positive control, released, and running inside a
standard harness. It is the shape [open-cowork](../systems/open-cowork/)'s
`forbiddenHits` has at repository scale, executed one layer up and published.
A forgetting benchmark could borrow its structure wholesale and change only what
sits between the memory and the model.

### ForgetEval — the benchmark this page said did not exist

**Read 2026-07-30 at [`b6053b7bdacc78a91b9ea4bb25f32edad278c495`](https://github.com/deeplethe/lethe/commit/b6053b7bdacc78a91b9ea4bb25f32edad278c495), MIT.**
ForgetEval ships inside [Lethe](../systems/lethe/), as the artifact behind
*Control-Plane Placement Shapes Forgetting*
([arXiv:2606.15903](https://arxiv.org/abs/2606.15903), June 2026). It is the
first released benchmark this page has found that scores the **control plane** —
`supersede`, `release`, `purge` — rather than recall, and its framing is this
page's own argument in the paper's words: recall is *"extensively benchmarked"*
and the operations that mutate memory are *"largely untested"*.

**Shape.** An `Adapter` Protocol of six methods — `reset`, `inscribe`,
`recall_texts`, `supersede(old_query, new_text)`, `release(query)`,
`purge(query)` — with implementations for six systems, five of which this atlas
reviews: Lethe, [Mem0](../systems/mem0/), LangGraph, [Cognee](../systems/cognee/),
[A-MEM](../systems/a-mem/) and [MemPalace](../systems/mempalace/). The
adversarial layer is 385 cases — 132 hand-crafted, 253 LLM-drafted and
oracle-validated — across ten attack categories: substring traps, prefix
collisions, paraphrase supersession, negation, temporal qualifiers, shared
attributes, compound facts, identifier obfuscation, cross-lingual identifiers and
recursive supersession. The cases and their labels are committed; the scored
results are not, living in a README table.

**Three things live only in the paper.** The 385 adversarial cases are the
*second* layer of two — the abstract describes *"a 1000-case templated suite plus
a 385-case adversarial layer"*. Case admission is backed by labelling provenance
no other benchmark on this page reports: *"Admission is corroborated by
10-annotator IAA (Fleiss' kappa = 0.958)"*. And there is *"a 77-case
external-authored subset (four blind contributors) that replicates the
canonicalization asymmetry"* — an independent replication of the headline finding
by people who did not write the benchmark, which is the single strongest
construct-validity move any benchmark in this atlas makes. None of the three has
any representation in the harness: a repository cannot show you its own
inter-annotator agreement.

The comparison unit is thirteen **configurations**, not six systems. Six adapters
times three placement regimes is what the title means by *placement*; the
six-adapter framing above describes the surface rather than the experiment.

**Two things about how it reports.** The three deterministic systems land in a
63–68% band the README reads as *"mutually overlapping Wilson CIs — the bench
reads the trade-off, not a winner"* — and **the author's own system places third
of the three**, at 63.4% against Mem0's 68.3%. A benchmark whose author loses it,
reported with confidence intervals and an explicit refusal to declare a winner,
is the opposite of the vendor-run comparisons this atlas has had to discount.
Its headline finding is about *placement* rather than storage: moving an LLM to
the mutation hook lifts both Lethe and LangGraph by roughly 28 points, so the
gain travels across backends.

**And one row is wrong.** MemPalace scores 0/385, and the adapter's docstring
says *"MemPalace is verbatim-everything: it does NOT support delete, update, or
supersede"*, raising `NotImplementedError` for all three. At MemPalace's own
pinned commit its MCP server exposes `delete_drawer`, `delete_by_source` and
`delete_hallway`. The primitives exist; what does not exist is a
*content-addressed* one, because ForgetEval's contract is `purge(query)` and
MemPalace deletes by drawer id and by source file — so wiring it needs a
search-then-delete bridge. That is a real impedance mismatch and it is a
different claim from the one the docstring makes. Read the 0 as *not wired*,
not as *cannot delete*.

**What it does not cover.** Steps 5–8 of [the test below](#what-a-forgetting-benchmark-would-have-to-do)
— re-feeding the source material and running the background jobs — and steps
11–13, the propagated copies. ForgetEval measures whether a mutation *takes
effect against an adversarial query*, which is the half nobody had measured; it
does not measure whether the next consolidation pass undoes it.

### FiFA, the one proposal that scores deletion compliance

*Forgetful but Faithful: A Cognitive Memory Architecture and Benchmark for
Privacy-Aware Generative Agents*
([arXiv:2512.12856](https://arxiv.org/abs/2512.12856), 14 December 2025, single
author, 45 pages) is the closest thing in the literature to what
[the next subsection](#what-a-forgetting-benchmark-would-have-to-do) asks for,
and it was found in a bibliography rather than in any of the three benchmark
tables that ought to list it.

Its privacy-preservation metric is

```text
PP = 1 − |privacy violations| / |privacy opportunities|
```

where opportunities are turn-level events at which sensitive content is
requested or likely to surface — including **outputs after TTL expiry** — and
violations include disclosing sensitive tokens, **retaining data beyond declared
horizons**, and **failing to honour deletion preferences**.

That third clause is the question this page says nobody asks. Its vocabulary is
unlike the rest of the field's: 211 uses of *privacy*, 68 of *forget*, 61 of
*audit*, 7 each of *erasure* and *right to be forgotten*, against the 107-page
survey's 10, 52, 5, 0 and 0.

**It still does not settle the question, for four reasons, and the last two are
the serious ones.**

1. **The three violation classes share one denominator.** Disclosure,
   over-retention and failed deletion collapse into a single rate, so no
   published number isolates whether a deleted item stayed unreachable.
2. **It compares retention policies, not memory systems.** The subject is six
   eviction policies — FIFO, LRU, Priority Decay, Reflection-Summary,
   Random-Drop, Hybrid — inside one architecture (MaRS), in simulation. Forgetting
   here means capacity eviction, the framing [section 5](#5-what-gets-measured-and-what-does-not)
   describes; deletion compliance rides along as one violation class.
3. **The metric did not discriminate.** PP came out at 0.722–0.780 across all
   five reported policies, `p = 0.485`, η² = 0.047. The paper is candid about
   why: violations are driven by adversarial prompts and TTL expiry, whose
   frequency is held constant, so PP "becomes less sensitive to retention
   strategy alone". A metric that does not separate FIFO from a principled
   hybrid is not yet measuring the design choice.
4. **Nothing was released, and the abstract disagrees with the results table.**
   Forty-five pages discuss version-locked code, archived artifacts, seeds and
   audit trails; no repository is linked, and a public leaderboard with released
   prompts appears in future work. Meanwhile the abstract reports "the Hybrid
   policy delivers the best composite performance (≈0.911)", and Table 2, §6.5.1,
   §7.2 and §7.6 all report Hybrid **last** of the five at 0.589±0.009, with
   Random-Drop leading at 0.635±0.024 — §7.2 states outright that "Hybrid does
   not win the aggregate". The sixth policy's row is marked as pending. Goal
   completion is 0.058–0.078 for every policy, so on the study's own numbers
   nothing completed the task.

The honest summary: **one paper has proposed the right question and has not yet
answered it.** A reader building the deletion test below should start from FiFA's
violation taxonomy rather than from nothing. It does not
change the conclusion, because a metric with no released artifact, no
discriminating power, and an abstract at odds with its own table is a research
direction rather than a measurement.

It is also, for this atlas, a familiar shape. "Published benchmark numbers
without committed artifacts" is a named antipattern here with several instances
among the systems; this is the same antipattern in the evaluation literature,
and it was caught the same way — by reading past the abstract.

### The failure nobody measures

Deletion in these systems is usually a statement about the present that the
next background pass is free to undo. [CowAgent](../systems/cowagent/)
re-distils its memory file nightly from retained daily files.
[Atomic Agent](../systems/atomic-agent/) re-clusters. Magic Context and Redis
Agent Memory Server both extract on a schedule from retained history.
OpenClaw's auto-capture can restore content a user deleted. MIRIX's `auto_dream`
pass loads up to 500 items per memory type with an explicit `start_date=None,
end_date=None` and lets an agent merge and hard-delete them. Only
[Verel](../systems/verel/), [RainBox](../systems/rainbox/) and
[Daimon](../systems/daimon/) carry a value-level tombstone that blocks
re-assertion — and, as noted in the comparative report, neither the standard
reading list nor the field's 107-page survey lists any of the three, the latter
never using the word *tombstone* at all.

So the question "does a deleted memory stay deleted?" has, for most systems
here, the answer "until the next scheduled job", and there is no benchmark that
would reveal it.

### What a forgetting benchmark would have to do

Not a QA benchmark. A state-machine test, run per system:

```text
1. write a distinctive fact
2. assert it is retrievable            → baseline
3. delete it / mark it rejected
4. assert it is not retrievable        → most systems pass here
5. re-feed the original source material
6. assert it is still not retrievable  → most systems fail here
7. run every background job: consolidation, re-extraction,
   nightly distillation, cloud sync
8. assert it is still not retrievable  → almost everything fails here
9. assert it is absent from derived artifacts too — summaries,
   profiles, graph edges, embeddings, caches, exports, backups
10. assert the deletion itself is auditable
11. share / export / sync the memory to a second scope, agent,
    tenant or hub BEFORE deleting it
12. delete the original
13. assert it is not retrievable from the second scope either
```

Steps 7 and 9 are where the interesting failures live. Step 9 in particular:
deleting a source memory that has already been folded into a summary, a user
profile, or a graph edge leaves the value present in derived form, and nearly
every system in this atlas that derives compact representations from raw
evidence has this exposure.

**Nearly**, because one system closes it, and it is worth naming precisely
because it shows how little the fix costs. [RisuAI](../systems/risuai/) stores
on every generated summary the set of chat-message ids it was derived from, and
drops the summary when any one of those messages no longer exists. One `Set`
per summary, checked on every turn. It is not step 9 in full — nothing records
that the deletion happened, and the next context overflow will summarize the
surviving messages again — but the derived-artifact substrate that step 9 exists
to probe is genuinely handled, and it has been since 2024-05-23, in the
generation after a summarizer that kept no link at all between a summary and its
sources.

The conclusion the step was written to support survives intact: nothing
*measures* this. RisuAI has no test asserting the behaviour, so the one system
that passes step 9 would not be able to prove it.

### Steps 11–13: the substrate this page used to miss

The [OWASP security survey](https://arxiv.org/abs/2604.16548)'s Verified
Forgetting enumerates four substrates a deletion has to reach — *"raw logs,
compressed summaries, vector indices, and propagated copies"* — and until now
this test covered three. Step 9 probes what a system **derives** from a memory
inside its own store. Propagation is a different surface: what a system
**copies out** of that store, to another scope, another agent, another tenant or
a remote hub. The two fail differently. A derived artifact is downstream of the
original and can be invalidated by tracking what it came from, the way RisuAI
does. A propagated copy is a *peer* — it has its own identity, its own lifecycle,
and frequently no back-reference at all, so there is nothing for a deletion to
follow.

The atlas has three grounded instances and they cover the range.

**A copy with a new identity and no link home.**
[SimpleMem](../systems/simplemem/)'s EvolveMem has a `share` operation that
reads a memory, mints a fresh `uuid4`, and writes the same content, summary,
entities, topics and embedding into a target scope at
`confidence = max(source.confidence - 0.05, 0.5)`. The copy inherits the
*session* provenance — `source_session_id`, `source_turn_start`,
`source_turn_end` — and **not the id of the memory it was copied from**, so on
inspection it is indistinguishable from a memory independently derived from the
same conversation. The link exists only in the append-only event log, as a
`share` row keyed on the *source's* id carrying `new_id=…` in a detail string.
Deleting or archiving the original touches nothing in the target scope, and the
only way to find the copy is to parse a log entry. Its `import_memories_json`
does the same thing in bulk.

**A shared store nobody owns.** [Cortex](../systems/cortex/)'s `shared_context`
is a namespaced, versioned key/value table written to by any agent. What an agent
puts there is not a copy of its memory so much as a *publication* of it, and
deleting the agent's own episodic or semantic row has no relationship to the
shared row at all.

**A copy that comes back.** [NemoClaw](../systems/nemoclaw/), covered below,
snapshots memory as an ordinary state directory and restores it verbatim — which
makes propagation bidirectional. The deleted value does not merely survive
elsewhere; it returns to the origin.

**One system now runs a protocol of this shape, and built it independently.**
[Daimon](../systems/daimon/) committed
`plugin/tests/test_deletion_durability_protocol.py` on 29 July 2026 — eleven
steps walking a forgotten value through re-feeding the original source
transcript, an index rebuild, a subsequent carry, **a team dual-write**, the
rendered brief string, the SQLite rows, the signed receipt, the audit trail and a
chunk-cache sink over the accumulated state. Every step is paired with a
never-forgotten twin that must stay retrievable, so no negative assertion can
pass vacuously; it runs deterministically on a canned model and a stubbed signer
at zero quota. Its step 6 covers the propagated-copy substrate this page added on
30 July, a day later. Nothing in the repository references this atlas, and the
steps are numbered against Daimon's own issues — so read it as convergent
arrival, not adoption.

Steps 11–13 are cheap to run and, with that one exception, nothing else here
would pass them. No system reviewed carries a deletion that follows a share, and
only one — SimpleMem — even records that a share happened, in a log its own write
path never consults.

```mermaid
flowchart LR
    Orig["source memory<br/>DELETED ✓"]
    Orig -- "share() before deletion" --> C1["copy in another scope<br/>NEW uuid · same content<br/>no back-reference"]
    Orig -- "export / sync" --> C2["remote hub · another tenant"]
    Orig -- "publish" --> C3["shared_context<br/>nobody owns the row"]
    Orig -- "snapshot" --> C4["backup"]
    C1 --> P["a prompt, somewhere else"]
    C2 --> P
    C3 --> P
    C4 -- "restore" --> Orig
    Orig -.->|"step 9 follows what was DERIVED<br/>steps 11-13 follow what was COPIED OUT"| Note["a derived artifact is downstream<br/>a propagated copy is a peer"]
```

```mermaid
flowchart LR
    Raw["source memory<br/>DELETED ✓"]
    Raw -. "derived earlier" .-> Sum["session summary<br/>still contains it"]
    Raw -. "derived earlier" .-> Prof["user profile<br/>still contains it"]
    Raw -. "derived earlier" .-> Edge["graph edge<br/>still contains it"]
    Raw -. "derived earlier" .-> Vec["embedding + cache<br/>still retrievable"]
    Raw -. "derived earlier" .-> Bak["export · backup<br/>still contains it"]
    Sum --> P["prompt"]
    Prof --> P
    Edge --> P
    Vec --> P
    Bak -. "restore" .-> Raw
```

[NemoClaw](../systems/nemoclaw/) makes the backup arm of this concrete rather
than hypothetical. It sandboxes Hermes and OpenClaw and declares each agent's
durable state per directory, sanitizing credentials on backup **by field** and
excluding machine-local auth state from snapshots entirely because a restored
copy would be corrupt. Memory gets neither treatment: it is an ordinary state
directory, snapshotted whole and restored whole. At that layer a memory is a
file, so the contract cannot express *do not restore this one* — which means an
ordinary restore silently undoes the most carefully reasoned deletion the layer
above ever made.

The deletion succeeded and the value is still reachable through five other
paths. Worse, the backup path closes the loop: a restore can put the deleted row
back, and nothing marks it as previously deleted. This is why a deletion API is
not a deletion guarantee, and why the assertion in step 9 has to be made against
every derived store by name rather than against the one the API touched.

Two things would make such a benchmark practical to build. It needs no labelled
dataset and no judge model — every assertion is deterministic. And it would be
**scored as a pass/fail matrix rather than a percentage**, because "forgets
correctly 87% of the time" is not a meaningful thing to say about a deletion
request.

The reason to want one is not only correctness. Where a user has a legal right
to erasure, "we deleted the row and a nightly job re-derived it from retained
history" is a compliance failure with a benchmark-shaped hole where the
evidence should be.

### The harness

Small enough to paste into a CI job. The adapter is the only part you write —
six methods, all of which any memory system already has in some form.

```python
import pytest

# Fictional and high-entropy, for the reason in section 3: a probe a model
# could guess proves nothing. This one cannot be reached by a plausibility prior.
CANARY = "the user's dog is named Plumbus Vantablack-7"
TOKEN = "Vantablack-7"          # what to probe derived stores for
SCOPE = "test-user"


class MemoryAdapter:
    """Implement these against the system under test."""

    def write(self, text: str, *, scope: str) -> None: ...

    def settle(self, *, timeout_s: float = 120) -> None:
        """Block until every queued write, extraction and index update has been
        applied. Without this the test measures write-to-readable lag (section 5)
        and calls it a deletion success. If the system cannot expose a quiescence
        signal, that is a finding: record it and poll `prompt_prefix` to a
        timeout instead of sleeping a guessed interval."""

    def prompt_prefix(self, query: str, *, scope: str) -> str:
        """What actually reaches the model — after ranking, budget truncation,
        dedupe and formatting. Not the retriever's return value."""

    def forget(self, text: str, *, scope: str) -> None: ...

    def run_background_jobs(self) -> None:
        """Every one: consolidation, re-extraction, nightly distillation,
        profile rebuild, index compaction, cloud sync. Then settle() again."""

    def leak_probes(self, *, scope: str) -> dict[str, bool]:
        """One probe per derived store, each returning True if the value is
        still reachable there. Text stores can be searched directly; the rest
        cannot, and need a probe of their own:

            summaries / profiles / exports  → substring search
            graph edges                     → query by entity, not by text
            vector index                    → embed the canary, nearest-neighbour
                                              search, check the distance
            caches                          → look up by the key the system uses
            encrypted backups               → restore to a scratch instance and
                                              run this same probe set against it

        A store returning no probe is an untested path, which is a result.
        Refusing to model this as list[str] is the point: a deleted value living
        on as a vector nobody can grep for is the leak most likely to survive."""

    def audit_entries(self, *, scope: str) -> list[dict]:
        """Mutation events as records: {event, memory_id, actor, at}. Not text
        containing the memory — see below."""


def present(memory: MemoryAdapter, query="what is the dog called?") -> bool:
    return TOKEN in memory.prompt_prefix(query, scope=SCOPE)


def test_deletion_holds(memory: MemoryAdapter, source_material: str):
    memory.write(CANARY, scope=SCOPE); memory.settle()                   # 1
    assert present(memory), "setup failed: never retrievable to begin with"  # 2

    memory_id = memory.forget(CANARY, scope=SCOPE); memory.settle()      # 3
    assert not present(memory), "deletion did not take effect"           # 4

    memory.write(source_material, scope=SCOPE); memory.settle()          # 5
    assert not present(memory), "re-ingestion resurrected a deleted value"  # 6

    memory.run_background_jobs()                                         # 7
    assert not present(memory), "a background job re-derived a deleted value"  # 8

    leaks = {store: hit for store, hit                                   # 9
             in memory.leak_probes(scope=SCOPE).items() if hit}
    assert not leaks, f"deleted value still reachable in {sorted(leaks)}"

    events = memory.audit_entries(scope=SCOPE)                           # 10
    assert any(e["event"] in {"forget", "delete", "reject"}
               and e["memory_id"] == memory_id for e in events), "deletion not auditable"
    assert not any(TOKEN in str(e) for e in events), \
        "the audit trail retains the value that was supposed to be deleted"
```

Four notes on running it honestly.

**Step 5 must re-feed the original source**, the document or transcript the fact
was extracted from, not the fact itself. Re-ingesting the raw source is the
realistic path, and the easy version of the test skips it.

**`settle()` is not optional.** A system that extracts asynchronously will pass
step 4 for the wrong reason — the value is not retrievable yet because it was
never indexed, not because deletion worked. Without a quiescence contract the
test conflates write-to-readable lag with deletion success in one direction and
flags a slow system as broken in the other.

**Step 10 asserts the audit does *not* contain the value.** This is the
inversion that matters: an audit row quoting a deleted value has not deleted it,
as the [append-only memory audit](../patterns/append-only-memory-audit/) pattern
says directly. Audit the *event* — type, memory id, actor, timestamp — and if
you need to prove which value was removed, store a salted digest rather than the
plaintext. A deletion log that reproduces the deleted secret is a compliance
problem wearing a compliance mechanism's clothes.

**`run_background_jobs` has to be genuinely exhaustive.** A system whose nightly
distillation is not reachable from the harness has an untested path, which is
worth recording as a result rather than passing over.

The same adapter runs the [contradiction test](#contradiction-test) below —
`prompt_prefix` is the B measurement, `run_background_jobs` is the C
measurement, and only the assertions change.

<a id="contradiction-test"></a>

## 7. The Contradiction Test

Forgetting has no benchmark, only
[a proposal that scores it as one violation class among three](#fifa-the-one-proposal-that-scores-deletion-compliance).
**Supersession has half of one** — LongMemEval's
knowledge-update category — and that half measures the easy part. What follows
is a specification for the rest of it, small enough to run in an afternoon
against any system in this atlas.

### Why the obvious version is too easy

The natural test is: the user likes blue on day one, prefers red on day three,
ask on day five. Any system that returns the most recent matching memory passes,
including one with no correction machinery whatsoever. Recency alone gets you
through.

Four things make it discriminating instead.

**Vary the shape of the contradiction.** Systems fail differently depending on
how the old value is displaced:

| Case | Day 1 | Day 3 | What it probes |
| --- | --- | --- | --- |
| **Replacement** | "I live in Berlin" | "I moved to Lisbon" | Baseline. Recency alone passes this. |
| **Polarity flip** | "I love coriander" | "I can't stand coriander now" | Both statements are about the same subject and embed almost identically, so retrieval returns both and the *model* picks. That is not correction; it is delegation. |
| **Retraction** | "My sister is a doctor" | "I misspoke — I don't have a sister" | Nothing replaces the value. There is no newer fact for recency to prefer, so a system with no negative memory has nothing to work with. |
| **Partial supersession** | "I'm an engineer at Acme" | "I got promoted to manager" | Systems that supersede whole records lose the employer along with the role. |
| **Bounded validity** | "I was vegetarian for ten years" | "I stopped in 2024" | Both are true, of different periods. Only a system tracking validity separately from record time can answer "was I vegetarian in 2022?" |

**Score five things, not one.** The single question "what does it answer" hides
the interesting failures:

- **A — Answer.** Does the agent say Lisbon? This is what knowledge-update
  scoring already measures, and the weakest of the four.
- **B — Retrieval hygiene.** Does the assembled prompt still present *Berlin as
  where the user lives?* Note the wording: the test is not whether the string
  appears. A bi-temporal system may legitimately surface both, labelled — "Berlin
  until March 2026, Lisbon since" — and that is correct behaviour, not a failure.
  What fails is an **unqualified** stale assertion sitting beside the current
  one, leaving the model to guess which holds. A system that retrieves both
  unlabelled and gets the right answer anyway has not corrected anything; it has
  handed the contradiction to the model and got lucky. Measure this against the
  prompt prefix, the way [open-cowork](../systems/open-cowork/)'s harness does,
  not against the retriever's return value.

  This is the one criterion a plain string check cannot score, and pretending
  otherwise would penalise exactly the systems this atlas argues are doing it
  right. B needs a judge — or a machine-readable qualifier on each injected
  memory, which is a good reason to emit one.
- **C — Durability.** Run every background job — consolidation,
  re-extraction, nightly distillation, profile rebuild — and ask again. This is
  where systems that re-derive from retained history quietly restore the old
  value.
- **D — History.** Ask "where did I use to live?" A system that hard-deletes
  Berlin passes A, B and C and fails here. **Correction is not amnesia**, and a
  test that only rewards the current answer will push designs toward destructive
  overwrite.
- **E — Derived reach.** Do the summaries, profiles and graph edges agree with
  the correction? Same qualification as B: a derived artifact that records
  Berlin *as a former address* is correct; one asserting it as current has not
  received the correction. A raw string grep over derived stores answers the
  deletion question in §6, where the value should be gone entirely — it does not
  answer this one, where the value may legitimately remain in qualified form.

C and D pull in opposite directions, which is the point: passing both is what
[bi-temporal fact validity](../patterns/bi-temporal-fact-validity/) and the
[rejected-value tombstone](../patterns/rejected-value-tombstone/) exist to make
possible, and a design that satisfies one by sacrificing the other has not
solved it.

**Add the adversarial re-entry.** After the correction lands, feed the day-one
material again through a *different* write path — a document upload, a
synchronization pass, an imported transcript. This is the same step that breaks
most systems in the deletion sequence in §6, and it belongs here too.

**Vary the gap.** Contradictions minutes apart and contradictions months apart
are different problems: the first tests within-session handling, the second
tests whether the older memory has decayed, been consolidated into a summary, or
been folded into a profile — and a summary that still says Berlin is a
correction that only reached the surface layer.

### The procedure

```text
for each case in {replacement, polarity, retraction, partial, bounded}:
    day 1  write the original statement
           assert it is retrievable                        → setup
    day 3  write the contradicting statement
    A      ask the question                                 → is the answer current?
    B      inspect the assembled prompt                     → is the stale value
                                                              absent, or present
                                                              but qualified?
    D      ask the historical form of the question          → is the old value still knowable?
           drain every queue, then run every background job
    C      repeat A and B                                   → did the correction survive?
           re-feed the day-1 material by another write path
    C'     repeat A and B                                   → did re-entry undo it?
           inspect derived artifacts: summaries, profiles,
           graph edges, embeddings, exports
    E      check whether they assert the stale value        → did the correction reach them?
           as current
```

Ten to twenty cases is enough. **A, B, D and E need a judge or a human**,
because all four turn on whether a value is asserted as current rather than
whether a string is present. Only C is deterministic, and only because it is
"did the B verdict change after the background jobs ran".

If that judging cost is unwelcome, the cheap alternative is to make the system
under test emit a qualifier — a validity interval, a `superseded` marker, an
`as-of` label — on every injected memory. Then B and E become mechanical. A
memory layer that cannot tell the model which of two conflicting facts is
current is relying on the model to work it out, which is the failure the
criterion exists to catch.

### What this would show, and what it would not

Reporting it as a percentage would waste it. The useful output is a small
matrix — cases down the side, A/B/C/D/E across — because *which* column fails
tells you what is missing. Failing B but passing A means no correction, just a
model doing cleanup on every turn, and that cost recurs forever. Failing C means
correction is a statement about the present that the next scheduled job may
overturn. Failing D means the system forgets rather than corrects.

**This atlas cannot report results for it.** Every review here is static — code
read, not run — so what follows is a prediction from the code, not a
measurement, and it should be read as a hypothesis worth testing rather than a
finding:

- Nearly everything should pass **A** on the replacement case. Recency is
  enough, and this is why the obvious version of the test separates nothing.
- **B** should fail widely. Most systems here rank and return top *k* with no
  mechanism that suppresses a superseded value, so both statements land in the
  prompt.
- **C** should fail for every system that re-derives on a schedule — and that
  is now the common case, not the exception.
- **D** should fail for systems whose correction is an overwrite or a delete,
  and pass for those retaining history: [Graphiti](../systems/graphiti/) closes
  a validity interval rather than erasing,
  [MemPalace](../systems/mempalace/) keeps verbatim drawers authoritative.
- The **retraction** row should fail almost everywhere, because it needs
  negative memory, and [the capability index](../capabilities/) shows how
  few systems have it.

If those predictions are right, the test separates the field on the second
column rather than the first — which is exactly the property the existing
benchmarks lack. If they are wrong, that is worth knowing too, and the way to
find out is to run it.

## 8. A Scorecard Worth Publishing

If a memory system published one table, this is the shape that would be useful.
Every row is either already collectable from the systems reviewed here or
requires a small harness; none needs a new dataset.

| Axis | Metric | Why |
| --- | --- | --- |
| Recall | Accuracy on a public long-conversation benchmark, with judge and config stated | Comparability, with all the caveats above |
| Precision | Forbidden-hit rate: how often material that should not surface does | The half nobody reports |
| Fidelity | Fraction of retrieved memories that survive into the actual prompt | Truncation silently eats what retrieval found |
| Correction | The [contradiction test](#contradiction-test) matrix: cases against A/B/C/D/E | Turns "we support updates" into something that separates systems |
| Deletion | Pass/fail on the ten-step sequence above | The compliance-relevant one |
| Cost (write) | Tokens per unit of material ingested | Scales with volume |
| Cost (read) | Injected memory tokens per turn, and accuracy per thousand of them | The recurring cost, and the honest efficiency ratio |
| Latency | Retrieval p50 and p99 | p50 alone hides the stalls |
| Freshness | Write-to-readable lag distribution | The "I told you that ten minutes ago" metric |
| Storage | Bytes per memory; index bytes as a multiple of source bytes | Predictable and never stated |
| Abstention | False-negative rate of any retrieval gate | An invisible failure mode by construction |

Two rules make the difference between a harness and evidence, both learned from
failures found in this atlas:

**Assert the cutoff.** A benchmark reporting `@k` must score exactly the first
*k* results. One system here committed a `k=10` artifact that scored every
returned session — 35 on average — while truncating only the displayed list.
The published number was not measuring what it said.

**Commit the results, not just the harness.** A reproducible harness with no
committed results reads as measured and is not. This atlas has now found that
pattern in several repositories, including some of the most carefully
engineered ones.

**And [memsem](../systems/memsem/) is the small counter-example that shows the
price of doing all three.** Its `DESIGN.md` publishes P@3 0.958 over 51 facts and
20 queries; `scripts/bench.mjs` is committed; `npm test` runs it; and from a
clean clone every cell of the published table reproduces — offline, deterministic,
no model, no service, in seconds. It also does the thing this page asks for and
rarely gets: it publishes an **ablation**, running four alternative constant
weightings beside the defaults on every test, so the chosen weighting has to keep
winning rather than merely having won once. And it writes its own limits down,
in a section headed *"honest reading"* — the set is the author's own rather than
a standard, the low P@5 is an artifact of most queries having one to three
relevant facts among five returned, and the single query that discriminates
between weightings is named.

The scale is small and the author says so. That is the point worth taking: the
gap between this and the untraceable figures elsewhere in the corpus is not
resources, it is fifty lines of harness and a paragraph of honesty. Nothing here
required a GPU, a dataset licence, or a research budget.

**[Perseus Vault](../systems/perseus-vault/) is the same discipline at full
scale, and it satisfies every rule on this page at once.** Its LongMemEval
headline is the mean of **three independent full 500-question runs**, not one, and
all three reports are committed with dataset, split, `n_instances`,
`mock_llm: false`, the pinned answerer and judge model snapshots, temperature,
retrieval mode and `k`, commit, binary version, platform, hardware, elapsed time
and a run signature. The published 73.8% recomputes from those three files
exactly. So does the 79.0% it does **not** lead with — the chain-of-thought
condition scores higher and the README quotes the plain-prompt number, with the
answer prompt folded into the run signature so *"a CoT number can never be
silently blended with a plain-prompt one"*. Its comparison table labels Zep's and
Mem0's figures as their publishers' claims and cites them to an issue rather than
reproducing them as head-to-heads, and its caveats section instructs a reader to
flag that Zep's publication does not state its prompt variant. It publishes the
per-question-type breakdown including the category it does badly on
(`single-session-preference`, 0.300 on 30 questions).

**[Provem](../systems/provem/) goes one step past all of them: it makes the
reproduction a gate rather than an invitation.** Every other repository here, at
best, ships a harness a reader may run. Provem ships a script that re-derives its
published numbers and *asserts* them, so a README that drifts from its artifacts
fails a command. It also does the things this page has been asking for
individually: the dataset is hash-pinned and fetched rather than redistributed;
two of its four deployment tiers are published **losing**, one of them scoring
0.21 against a stated 0.24 no-memory baseline; a prompt confound gets its own
named replay step; the competitor was configured to that competitor's own
published evaluation checklist; third-party evaluations are quoted verbatim in a
separate ranking marked not comparable; and `docs/claim_register.md` carries rows
whose evidence column reads `Unsupported` and whose disposition reads *"Rejected
for now"*. Its author describes a nominal recall win over Mem0 as "roughly a tie".

The counterweight is the one it states itself: the governance suite producing the
240 → 0 and 100% → 0% figures is **self-authored**, so it measures the failure
modes its author modelled. A reproducible number is not the same as a
generalisable one, and this page's standard has always been the first.

That is the run-count rule, the config-stamp rule, the commit-the-results rule,
the don't-reproduce-others'-numbers rule and the report-the-trade rule, in one
repository. Set against the rest of this page it is the existence proof that the
standard is meetable by a project that is not a research lab.

The counterweight belongs here too, because it is the failure this page has not
previously named. The same repository ships a `CLAIMS-AUDIT.md` that retired its
own unbacked latency claim and downgraded "signed results" to "content-hashed" —
and its one claim without working verification is the one with a **documented
command attached**: it returns 76 against a tool count of 65 repeated in three
places, while the registry that command is meant to be counting parses to 88.
**Auditing your claims and maintaining them are different disciplines** — the
project's author puts it that way — and a documented check that nobody runs is
still only a comment. The fix is a count generated from the registry and asserted
in CI, which is where every guard on this page belongs.

[Daimon](../systems/daimon/) is the first system here to write the third rule
down as policy rather than leave it to the reader, and it is the one this page
has been implying throughout: **a recall number without its backend is not a
result.** Its benchmark README commits to publishing only self-measured figures
with the full config stamp — harness version, backend, model, prompt version,
seed, dataset checksum — labels third-party figures as their publishers' claims
rather than reproducing them as head-to-heads, and states that it will report
the *trade* rather than only the win, publishing `avg_injected_tokens` beside
recall so the efficiency story travels with the quality one. It also records the
measurement choice that flatters it: `min_messages` is lowered from the
product's default of 10 to 2 so short evidence sessions enter the index at all,
surfaced in the run config instead of omitted.

The counterweight is that policy is cheaper than sample size. The headline
committed run is five questions; the more meaningful file is a 52-question
interim baseline whose per-question rows average Recall@5 0.58, and it ships no
aggregate block because the paired arm it exists for is unfinished. A stricter
reporting policy than most vendors have, attached to numbers most vendors would
not publish, is still the right order to do these things in.

## 9. Limits of This Page

- Benchmark harnesses in these repositories were **inspected, not run**, with
  three exceptions at different strengths, and the differences between them are
  worth keeping. The strongest is [Provem](../systems/provem/), because the
  checking is the repository's own: `scripts/verify_repro.sh` re-derives every
  published number from frozen artifacts and **asserts it verbatim**, exiting
  non-zero on any drift or missing input. Run here from a clean clone it reports
  `VERIFY OK (21 assertions)`, and 25 with `--full`, which adds the deterministic
  governance benchmark and the unit tests. Its one prerequisite is fetching the
  LoCoMo dataset, which is CC BY-NC and so pinned by sha256 rather than
  redistributed; without it the gate exits 1 with `MISSING INPUT` instead of
  quietly skipping. [memsem](../systems/memsem/)'s `scripts/bench.mjs` was **re-run** from
  a clean clone and reproduced every cell of its published table — offline,
  deterministic, no model, no service, seconds. [Perseus Vault](../systems/perseus-vault/)'s
  LongMemEval figures were **recomputed, not re-run**: its published 73.8% and
  79.0% are the exact means of three committed per-run reports each, which
  establishes that the headline is a function of artifacts in the repository
  rather than a number in a README, and does not establish that a fresh run would
  land there. Re-running it needs 500 questions × 3 runs × two `gpt-4o` calls,
  which is why nobody checks figures of that kind and why committing the per-run
  reports matters as much as it does.
- The benchmarks in §2's first table are grounded in committed code. Those in
  the second are from familiarity with the literature and were not verified
  against their own repositories in this review.
- LoCoMo's and LongMemEval's category structures are described from published
  descriptions, not from re-reading their datasets here.
- "Measured nowhere" in §5 means *not found in the systems this atlas has
  reviewed*, at the pinned commits listed in the
  [comparative report](../compare/). It is a statement about 186 repositories,
  not about the whole field. That number read **46** until 2026-08-07, having
  been written when the corpus was that size and never revised as it more than
  tripled — the same class of stale numerator this page's own counts are
  machine-checked against, in the one sentence that scopes them.
- The criticism of LoCoMo's difficulty in §3 is a summary of a known objection,
  not an independent finding.
- The predicted outcomes in §7 are inferences from reading code, not results.
  Nothing in this atlas has been run against the contradiction test, and the
  predictions are published so they can be falsified.

# Cognitive Weave: a paper with SOTA claims, and an official implementation missing the mechanism they measure

**Status:** done — examined 2026-08-06, no report, recorded in the overview's
scope section
**Origin:** `https://github.com/rahvis/cognitive-weave` and
[arXiv:2506.08098](https://arxiv.org/abs/2506.08098) submitted together
2026-08-06
**Pin examined:** `2b85f69b7066c427a1cbd6e241e30db091d840a5`, dated 5 August
2025 — no commit since

## The call

Out of scope. Nothing survives the session, which is the atlas's first
inclusion test and the one this fails on its own terms.

`main.py:39` declares the store:

```python
self.memory_store: List[InsightParticle] = []
```

A Python list on the agent object. `start_chat()` runs an input loop, appends to
that list, and on `quit` logs the contents and returns. Grepping the whole tree
for `open(`, `json.dump`, `sqlite`, `pickle`, `write_text`, `.save` and `.db`
returns **nothing** outside `__pycache__`. There is no file, no database, no
serialisation of any kind. The process ends and the memory ends with it.

That is the same call already made for [Pi](../content/systems/pi.md),
LlamaIndex's `ChatMemoryBuffer` family, OpenAI's `SQLiteSession`, smolagents'
`AgentMemory` and `Fagoon-AI/upgrade`. Nothing here is a special case, and the
project agrees: **"Implement memory persistence layer" is an unchecked item on
its own To-Do list.**

## Why it is recorded rather than dropped

Because of what it is the official implementation *of*.

The README's first line: *"This repository contains the official implementation
of the paper."* The paper is **Cognitive Weave: Synthesizing Abstracted
Knowledge with a Spatio-Temporal Resonance Graph**, seven authors across USC,
Yeshiva, Northeastern and IEEE, submitted 9 June 2025. Its abstract claims *"a
notable 34% average improvement in task completion rates and a 42% reduction in
mean query latency when compared to state-of-the-art baselines."*

Section 4 describes a comparative evaluation against **Standard RAG (FAISS),
MemGPT, A-MEM and Mem0** across three datasets — **Robotouille** (long-horizon
planning), **Evolving-QA** (with bespoke Temporal Accuracy and Update
Adaptability metrics) and **LoCoMo** (multi-session dialogue, scored with BLEU,
ROUGE-L, SBERT cosine similarity and human judges on a 1–5 Likert scale) — plus
a scalability analysis and an IA quality assessment.

The repository is 568 lines of Python across five files, one of them empty.

## What the paper names and the repository does not contain

The title mechanism is the clearest case. **STRG — the Spatio-Temporal
Resonance Graph — is not implemented,** and the README says so itself:

> - [ ] Implement full STRG (Spatio-Temporal Resonance Graph) structure

Alongside it, unchecked: *comprehensive test suite*, *memory persistence layer*,
*advanced retrieval mechanisms*, *enhance IA synthesis with more sophisticated
algorithms*.

Working through the paper's components against the tree:

| Paper component | In the repository |
| --- | --- |
| Insight Particles | Yes — a Pydantic model, `data_structures.py:8` |
| Semantic Oracle Interface | Yes — one LLM call producing resonance keys, signifiers, a situational imprint and entities |
| Insight Aggregates | Partly — synthesised every 3 turns over **all** imprints |
| Typed Relational Strands | Declared as `List[Dict[str, str]]`, never written by any code path |
| Spatio-Temporal Resonance Graph | **No** — named in the To-Do as unimplemented |
| Cognitive Refinement clustering | **No** — the code comment says *"In a real system, you'd select related IPs based on clustering or other metrics"* |
| Multi-faceted / hybrid recall | **No** — see below |
| Temporal decay model (paper §5.2) | **No** — three timestamp fields exist, two of them assigned nowhere in the tree |
| Access frequency, importance score | Declared, initialised to `0` and `0.0`, never updated |
| Any evaluation harness, dataset or result | **No** — nothing matching a dataset, metric, or score exists in the tree |

Retrieval, which the paper describes as leveraging the layers of the STRG, is
`retrieve_relevant_insights` at `main.py:79`: lowercase, strip punctuation,
drop a hardcoded 113-word stopword list, and score each particle by *set
intersection size* — resonance-key overlap weighted ×2, situational-imprint
overlap ×1. No embedding, no vector, no graph traversal, no temporal term. When
nothing scores above zero it returns the most recently added particle, so a
query with no lexical overlap silently receives the last thing said.

## The honest framing

**This does not establish that the experiments were not run.** The paper's
numbers may come from a fuller implementation that was never released; that is
common and it is not misconduct. What the repository establishes is narrower and
still worth stating: **the published figures cannot be reproduced, checked, or
even approximately located from the artifact presented as their official
implementation**, because the mechanism they attribute the improvement to is
absent from it, along with every dataset, metric and result.

The atlas already records this shape for [Memvid](../content/systems/memvid.md),
[MemoryOS](../content/systems/memoryos.md) and
[SimpleMem](../content/systems/simplemem.md) — headline figures with no
committed artifact behind them. Cognitive Weave is the sharpest instance so far,
and it is a different degree rather than a different kind: those three ship a
system whose results are untraceable, and this ships a proof of concept whose
central structure is on a To-Do list under a paper claiming it beat MemGPT,
A-MEM and Mem0.

Worth holding beside [Perseus Vault](../content/systems/perseus-vault.md), which
sits at the opposite end of the same axis: three independent runs per condition,
every report committed with a config stamp, and a `CLAIMS-AUDIT.md` that
retires claims it cannot back.

## Smaller observations

- **The licence is asserted and absent.** The README's final line grants Apache
  2.0 by link. There is **no `LICENSE` file in the tree**, so the grant is a
  sentence in a Markdown file. Same shape as
  [Membase](../content/systems/membase.md), recorded the same way — a caveat
  for a reader, not a reason to skip the reading.
- **Credentials are hardcoded by design.** `utils.py` carries module-level
  `AZURE_OAI_ENDPOINT` and `AZURE_OAI_KEY` constants under a comment reading
  *"The values below are hardcoded as per your request"*, and the setup
  instructions tell a user to edit their real key into that file. The committed
  values are non-functional junk — malformed for an Azure key, and the file's
  own two literals do not match each other — so nothing is leaked here. The
  pattern is the finding: a repository that instructs users to put a live key in
  a tracked source file, and which also has `__pycache__/*.pyc` committed, is
  one commit away from publishing one.
- **The demo logs are transcripts, not measurements.** `conversation_medical.log`
  and `conversation_legal.log` are 675 lines of captured terminal output from
  two interactive sessions, showing the SOI enriching real inputs. They are
  genuine evidence the SOI runs. They are not evidence of anything the paper
  claims, and they carry the author's shell prompt.
- **Fifteen commits, twelve of them README edits.** The implementation landed in
  the first two.
- **The SOI is the part worth keeping.** Its enrichment prompt asks for 5–7
  resonance keys ordered by importance, 3–5 categorical signifiers, a
  one-sentence situational imprint capturing context *and* takeaway, and named
  entities — in one call, with `response_format={"type": "json_object"}`. As an
  extraction schema it is better specified than several in the corpus, and it is
  transferable independent of everything above it.

## What this taught the method

Nothing new about the inclusion test, which handled it in one grep. Something
about **how a paper and a repository should be read against each other**: the
To-Do list was the fastest route to the finding, and it was in the README the
whole time. When a repository presents itself as a paper's official
implementation, its own list of what is not built yet is the first thing to
read, not the last — it is the authors' own statement of the gap, and it costs
nothing to check before tracing any code.

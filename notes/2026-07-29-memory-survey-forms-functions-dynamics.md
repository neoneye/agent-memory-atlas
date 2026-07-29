# The field's own survey, read against the atlas

**Status:** comparison done, three content edits made, one open question
**Origin:** *Memory in the Age of AI Agents: A Survey — Forms, Functions and
Dynamics*, [arXiv:2512.13564](https://arxiv.org/abs/2512.13564) (v2, 13 January
2026). 47 authors across twelve institutions, 107 pages, with a companion
reading list at
[Shichun-Liu/Agent-Memory-Paper-List](https://github.com/Shichun-Liu/Agent-Memory-Paper-List).

This is the most substantial artifact the field has produced about itself, and
it is the natural external check on the atlas's central claim. Read on
2026-07-29.

## Method, and its limits

Everything below comes from a text extraction of the PDF (pypdf, 107 pages,
~462 KB of text) plus reading the sections that bear on the atlas. **Word counts
are counts over that extraction, not over the typeset paper.** Figure labels do
survive extraction — Figure 9's branch names come through intact — but text set
inside vector graphics can be lost, so treat every zero below as "not found in
the extracted text" with the same force the atlas gives "not found in the
inspected code". The paper's own claims are reported as claims; nothing here was
run.

## What it is

A taxonomy paper, organised on three axes it argues are orthogonal:

| Axis | Question | Categories |
| --- | --- | --- |
| **Forms** (§3) | What carries memory? | token-level (flat 1D / planar 2D / hierarchical 3D), parametric (internal / external), latent |
| **Functions** (§4) | Why does an agent need it? | factual (user / environment), experiential (case / strategy / skill / hybrid), working (single-turn / multi-turn) |
| **Dynamics** (§5) | How does it operate and evolve? | formation, evolution (consolidate / update / forget), retrieval |

Plus §2.3, which spends nine pages separating agent memory from LLM memory, RAG,
and context engineering; §6, two consolidated tables of benchmarks and
frameworks; and §7, eight frontier essays.

**The §2.3 boundary and the atlas's boundary are close to the same line.** The
paper places pure context assembly outside agent memory because it lacks the
formation/evolution/retrieval lifecycle. The atlas excludes it because nothing
survives the session with a correctable identity. Different vocabulary, same cut
— and the atlas's [not in scope](../content/overview.md) section reaches it from
worked examples (BeeAI, MemAgent) rather than from a definition, which is the
more useful form for someone evaluating a framework whose README says "memory".

## The corpora barely overlap

Table 9 lists 25 rows, 24 distinct frameworks (ReMe appears twice). Matched
against the atlas's 63 pinned repositories **by repository URL**:

- **8 exact matches**: mem0, MemoryOS, MemOS, LangMem, Supermemory, Cognee,
  memU, Hindsight.
- **2 more by project identity**: `cpacker/MemGPT` is Letta under its former
  name; `getzep/zep` is the product whose engine the atlas reviews as Graphiti.
- **14 absent from the atlas**, of which three (Pinecone, Chroma, Weaviate) are
  vector databases the atlas's inclusion test excludes as infrastructure — and
  the paper says as much itself, noting that such entries "leave agent behavior
  and evaluation protocols to the application". Eleven are real candidates:
  Memobase, MIRIX, Memary, Second Me, MemEngine, Memori, ReMe, MineContext,
  Acontext, PowerMem, and `elizaOS/agentmemory`.
- **53 of the atlas's 63 systems appear nowhere in the paper**, including all
  three tombstone holders.

**One trap worth recording.** The paper's `AgentMemory` is
`elizaOS/agentmemory`; the atlas's [agentmemory](../content/systems/agentmemory.md)
report is `rohitg00/agentmemory`. Different projects, identical name. Anyone
reconciling the two lists by name rather than by URL will merge them.

The shape of the divergence is not an accident. The paper selects on
*publication* — a framework earns a row largely by having a paper behind it,
though the Evaluation column is empty for sixteen of the twenty-four, so it is
not selecting on measured results either. The atlas selects on *inspectable
code*, opportunistically. Neither
is a sample of a population. What matters is that the two selection rules
disagree so completely that a reader using either alone would conclude the other
half of the field does not exist.

## What it confirms

**The forgetting-benchmark gap, against the field's own consolidated table.**
The [benchmarks page](../content/benchmarks.md) claimed no benchmark tests
whether a deleted memory stays deleted, scoped to what this atlas had read.
Table 8 is 40 benchmarks — 26 memory/lifelong/self-evolving, 14 related — and
the claim survives it. The nearest entries are MemoryBank ("user memory
updating"), LongMemEval, and HaluMem ("memory hallucinations"). Nothing tests
deletion durability. That upgrades the claim from "not in this atlas" to "not in
the field's own list either", which is the version worth publishing.

**Correction stops at soft deletion.** §5.2.2 traces external memory update as a
progression: destructive replace/delete (MemGPT, D-SMART, Mem0ᵍ) → Zep's
invalid-timestamp annotation instead of deletion → dual-phase online/offline
consolidation (MOOM, LightMem) → RL-learned update policies (Mem-α). Every step
makes the *decision* better. None of them records the rejected value, and the
failure the atlas keeps finding — the next extraction pass re-asserting what was
just corrected — is not named anywhere in the section. The counts:

| Term | Occurrences in 107 pages |
| --- | --- |
| `memory` | 1570 |
| `forget*` | 52 |
| `conflict` | 28 |
| `privacy` | 10 |
| `audit*` | 5 |
| `access control` | 4 |
| `contradiction` | 3 |
| `provenance` | 3 |
| `deletion` | 2 |
| `bi-temporal` | 1 |
| `tombstone` | **0** |
| `rejected` | **0** |
| `negative` | **0** |
| `tenant` | **0** |
| `unlearn*` | **0** |

`negative` at zero is the one to sit with. It is an ordinary English word, and a
107-page technical survey uses it never — which means no negative retrieval
assertion, no negative example, no negative result, under that name.

**§5.2.3 makes the atlas's point about forgetting explicitly.** The paper's three
forgetting mechanisms are time-based, frequency-based, and importance-driven —
all three are *capacity management*. Forgetting is defined there as removing
"outdated, redundant, or low-value information to free capacity". Deletion
because a person asked, or because a value was wrong, is not one of the
categories. The section's closing sentence is the tell: "when storage cost is not
a critical constraint, many memory systems avoid directly deleting certain
memories." Forgetting is treated throughout as an efficiency knob, which is
exactly the framing under which "does it stay deleted?" never becomes a question.

**§7.7 asks for the property without naming the mechanism.** The trustworthy-memory
frontier calls for "access control, verifiable forgetting, and auditable
updates", and for memory that is "version-controlled, auditable, and jointly
managed by agent and user". Those are, near enough, four of the atlas's seven
capability columns stated as open research directions. The paper wants the
property; the atlas has the count of who implements it.

That combination is the strongest form the atlas's central finding has taken so
far. It is no longer "a survey did not list three obscure systems" — it is that
the field's most comprehensive self-description does not contain the *concept*,
while its own frontiers section asks for what the concept provides.

## What it has that the atlas does not

Stated plainly, because the atlas has no coverage of any of it:

- **Parametric and latent memory (§3.2, §3.3).** Model editing (ROME, MEMORYLLM,
  M+), KV-state reuse, memory internalised into weights. The atlas's inclusion
  test — survives the session with a correctable identity — arguably admits
  these and the atlas has simply never gone looking. Weight-space memory has no
  row, no tombstone, and no scope key, which makes it either a hard case for the
  seven capabilities or evidence they are token-store-specific. Unresolved.
- **RL-learned memory management (§7.3).** Mem-α learns *whether* to update.
  MemEvolve evolves the memory architecture itself. The atlas's closest neighbour
  is the MemAgent exclusion, and its "promotion gates for the policy" pattern
  assumes the policy is written down.
- **Multimodal memory (§7.4)** and the multimodal column in both tables.
- **A literature backbone.** Several hundred citations against the atlas's
  pinned commits. The two are complementary in the obvious way, and the
  [symbolic prior art note](2026-07-28-symbolic-prior-art.md) is still the
  unpaid debt on this side — note that this survey does not pay it either:
  belief revision and truth maintenance appear nowhere in it.

## Changes made

1. **[overview.md](../content/overview.md), §Correction.** The "gap is visible
   from outside this atlas too" paragraph rested on TeleAI's Awesome-Agent-Memory
   list. Kept, and added this survey with the term counts and the §5.2.2
   progression. An awesome-list omitting three obscure repositories is weak
   evidence; a 47-author survey whose vocabulary lacks the concept is not.
2. **[benchmarks.md](../content/benchmarks.md), §2 and §6.** Added Table 8 to
   the named-outside-these-repositories list under the standard not-inspected
   caveat, and re-scoped the forgetting claim against 40 benchmarks instead of
   against this atlas alone.
3. **[patterns/index.md](../content/patterns/index.md), the establishment
   disclosure.** One sentence, because that paragraph is where a reader decides
   how much weight the advocacy patterns carry.

Not changed: the capability marks, the counts, the rubric. Nothing here is code
read at a pinned commit, and the atlas's marks come from code.

## Open question

Whether the eleven candidate frameworks should be reviewed, and in what order.
The honest argument for doing it is that the atlas and the paper disagree about
what the field *is*, and eleven systems that a 47-author survey considered
representative is the cheapest available test of whether the atlas's
opportunistic selection has a blind spot shaped like "published Chinese-lab
memory frameworks". The argument against is that the atlas already has 22 stale
pins ([editorial backlog](2026-07-28-editorial-backlog.md) §3), and adding
breadth while depth rots is the wrong trade.

My read: **MIRIX, Memobase and MemEngine first**, and only those three. MIRIX
because it is the only multimodal entry with reported results on two benchmarks;
Memobase because "structured profiles" is a write model the atlas covers thinly;
MemEngine because a modular memory-space abstraction is the shape the
[pluggable memory provider](../content/patterns/pluggable-memory-provider.md)
pattern predicts will have nowhere to put "forget me". If all three land in the
usual place — scope enforced, nothing else — that is a stronger negative result
than three more opportunistic reviews, because these three were *chosen by
somebody else*.

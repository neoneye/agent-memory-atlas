# The papers the reports did not read

**Status:** audit. One error found and fixed, one systematic gap measured, the
workflow changed so it cannot recur silently. The per-report follow-up is listed
at the end and is not done.

**Why this happened.** The SESA report said "no ablation is present". That was
true of the repository and false of the work: the README cites
[arXiv:2607.29468](https://arxiv.org/abs/2607.29468) in a BibTeX block at the
bottom, the paper's Table 3 isolates the skill bank at 2.7 points, and the
reading of that README stopped before the citation section. The report has been
corrected and its History records the correction. The question this note answers
is whether the same reading habit produced the same gap elsewhere.

## What was measured

Locally: **8 of 167 reports mention arXiv at all.** That number alone proves
nothing — most systems in this corpus are products, not papers.

So sixteen systems most likely to be paper-backed were checked against their own
READMEs. **Eleven have a paper linked from the repository the atlas reviewed, and
none of the eleven reports cites it:**

| System | Paper the README links | Report mentions a paper |
| --- | --- | --- |
| [a-mem](../content/systems/a-mem.md) | [2502.12110](https://arxiv.org/abs/2502.12110) — *A-MEM: Agentic Memory for LLM Agents* | in prose, uncited |
| [generative-agents](../content/systems/generative-agents.md) | [2304.03442](https://arxiv.org/abs/2304.03442) — *Generative Agents: Interactive Simulacra of Human Behavior* | in prose, uncited |
| [hipporag](../content/systems/hipporag.md) | [2405.14831](https://arxiv.org/abs/2405.14831) and [2502.14802](https://arxiv.org/abs/2502.14802) | in prose, uncited |
| [voyager](../content/systems/voyager.md) | [2305.16291](https://arxiv.org/abs/2305.16291) | in prose, uncited |
| [memoryos](../content/systems/memoryos.md) | [2506.06326](https://arxiv.org/abs/2506.06326) — *Memory OS of AI Agent* | **no** — now fixed |
| [mem0](../content/systems/mem0.md) | [2504.19413](https://arxiv.org/abs/2504.19413) | **no** |
| [memos](../content/systems/memos.md) | [2507.03724](https://arxiv.org/abs/2507.03724) and [2505.22101](https://arxiv.org/abs/2505.22101) | **no** |
| [mirix](../content/systems/mirix.md) | [2507.07957](https://arxiv.org/abs/2507.07957) | **no** |
| [graphiti](../content/systems/graphiti.md) | [2501.13956](https://arxiv.org/abs/2501.13956) — *Zep: A Temporal Knowledge Graph Architecture for Agent Memory* | **no** |
| [cognee](../content/systems/cognee.md) | [2505.24478](https://arxiv.org/abs/2505.24478) | **no** |
| [agentic-context-engine](../content/systems/agentic-context-engine.md) | [2510.04618](https://arxiv.org/abs/2510.04618) (ACE) and [2504.07952](https://arxiv.org/abs/2504.07952) | **no** |

Checked and clean: `honcho`, `open-cowork` and `powermem` link no paper.
`letta` links none from its README but ships a `CITATION.cff` that was not
opened — treat as unresolved. `memmachine` cites *Agent Lightning*
([2508.03680](https://arxiv.org/abs/2508.03680)) in a references section, which
looks like related work rather than its own paper; also unresolved.

## Is any of it load-bearing?

The dangerous shape is not a missing citation. It is an **absence claim about
measurement** that the paper falsifies — the SESA shape. Every report above was
searched for that phrasing:

- **Correctly scoped, no action needed.** HippoRAG ("no published ablation *in
  the repository*"), Generative Agents ("no ablation *in the repository*"),
  MIRIX ("no scored results are committed *to this repository*"), Agentic
  Context Engine ("no committed results"). These are claims about artifacts and
  they are true. This is the phrasing the workflow now requires.
- **One unscoped claim, checked.** MemoryOS: "the constants can be tuned or made
  configurable; no ablation was found", and the same sentence in the comparative
  report. Its paper was read. The claim **survives and is stronger for it**: the
  paper prints the same formula and states that "the values of α, β, and γ in
  Eq. 4 are equality set to 1", and its single ablation removes modules —
  mid-term memory, the persona module, the dialogue chain — never the weights.
  Both files now cite the paper and say so.

So the audit found one real error (SESA, already fixed) and no second one. The
gap that remains is citation and consideration rather than accuracy — which is
worth fixing anyway, because a reader who wants to check a report against its
paper currently has to go and find out that a paper exists.

## What changed so it cannot recur silently

`.agents/skills/add-memory-system/SKILL.md` gains a sixth investigation step:
grep the README and docs for `arxiv`, `bibtex`, `@article`, `@misc`, `Citation`,
`CITATION.cff` and `doi` **before writing section 10**; if a paper exists, read
its abstract and any ablation table, cite it with its date, and look for two
things specifically — whether the paper's description of the mechanism matches
the code, and whether anything the paper starts from is absent from the tree. If
no paper exists, say so, because a reader cannot tell an absent paper from an
unread one.

`.agents/skills/reanalyze-memory-system/SKILL.md` gains the matching rule: an
uncited paper is a reanalysis reason on its own, even when the pinned commit is
still current.

Both restate the distinction the audit turns on: *"no ablation" is a claim about
the work; "no result is committed to this repository" is a claim about the
artifact, and only the second is one a reading of the tree can support.*

## Not done

Eleven reports need a citation added and their section 10 checked against the
paper. That is eleven papers to read, and two of them (MemOS, HippoRAG) have two
each. It is worth doing in one pass rather than opportunistically, because the
interesting output is comparative: which papers describe the mechanism their code
implements, and which start from something the repository does not ship. SESA
scored well on the first and badly on the second, and one instance is not a
finding.

`letta`'s `CITATION.cff` and `memmachine`'s reference list are unresolved above
and are the cheapest two to settle.

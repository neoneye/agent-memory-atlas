# Pattern gap analysis

**Status:** analysis done, one pattern promoted, the rest listed with evidence
**Origin:** an external 20-pattern proposal (Grok, 2026-07-28), used as a check
against the library rather than adopted.

## The structural difference

The proposed list mixes two kinds of thing. Items 1–4 — working, episodic,
semantic, procedural memory — are a **taxonomy of content**, not design patterns.
"Episodic memory" names what a record contains; it does not state a problem, a
solution, a failure mode, or a cost. Items 5–9 are storage architectures, which
is closer, and 10–20 are mostly mechanisms.

The library is deliberately all mechanisms: each page states the recurring
problem, the shape of the solution, why it works, where it fails, what it costs
to adopt, which systems do it, and what to test. That is a narrower definition
than "things people say about memory", and it is the reason the library is 17
pages rather than 40.

Keeping the definition narrow is worth more than coverage. A page that says
"agents have episodic memory" cannot be wrong, cannot be tested, and cannot help
anyone decide anything.

## What the proposal names that the atlas already has

| Proposed | Where it lives here |
| --- | --- |
| Working / in-context memory | **Deliberately out of scope** — the conversation-window boundary, argued in the comparative report |
| Procedural memory | `skills-as-procedural-memory` |
| Flat vector store | An *antipattern* — "vector-only memory" |
| KG + vector hybrid | `hybrid-retrieval-fusion` |
| Governed metadata layer | `governed-write-gateway` + `scope-as-a-first-class-key` |
| Append-only + compression | `evidence-before-belief`, plus OptMem's cover |
| Context-resident compression | Out of scope, same boundary |
| Retrieval-augmented memory | This is retrieval, not a pattern |
| Multi-tenant / scoped | `scope-as-a-first-class-key` |
| Temporal / time-aware | `bi-temporal-fact-validity` |
| Write–Manage–Read, "most systems under-invest in Manage" | This is the atlas's whole thesis, stated as the ascent and the descent |

## The real gap, and it is self-inflicted

Section 5 of the comparative report names **29 recurring patterns**. The library
has **17 pages**. Twelve patterns were identified from the evidence and never
promoted — and several of them are exactly what the proposal flags as missing:

| Named in §5, no page | Proposal calls it | Instances in the corpus |
| --- | --- | --- |
| Separate hot memory from archival memory | Tiered / hierarchical memory | ~9 — letta, memos, memoryos, mercury, loongflow, redis, qwen-code, core-memory, memvid |
| Buffered observation-reflection | Reflection / consolidation | ~6 — mastra, generative-agents, ctx, qwen-code, nooa-memory, hindsight |
| Promotion gates for the policy, not just the memory | Policy-learned / RL operators | 2 — metaclaw, loongflow |
| Verify memory against its subject | — | 1 — magic-context |
| Structural-loss guard on generated rewrites | — | 1 — byterover |
| Non-destructive entity resolution | — | 1 — hipporag |
| Diffusion instead of traversal | — | 1 — hipporag |
| Bounded prompt memory with in-turn consolidation | — | 1 — hermes-agent |
| Rehearse the correction before committing it | — | 1 — memora |
| Sample instead of rank | — | 1 — loongflow |
| Memory policy as a written artifact | — | 2 — genericagent, openworker |
| Explicit memory mutation surfaces | Active agent-managed memory | many |

The library-versus-§5 inconsistency is the finding. It is not that an outside
list spotted something; it is that the atlas spotted these itself and left them
in a section nobody browses.

## What was promoted, and why only one

`separate hot memory from archival` became
[promotion between tiers](../content/patterns/promotion-between-tiers.md). It has
the most instances by a wide margin, a sharp failure mode (almost everyone tiers,
almost nobody defines what promotes), and a genuine spread of answers — from
MemoryOS's unvalidated `1·N_visit + 1·L_interaction + 1·R_recency` to Core
Memory's grounding ceiling.

The rest were not promoted, and the reason is the discipline the library just
adopted: most of them rest on **one instance**. A page built on a single system
is advocacy, and the index now says so explicitly. Writing eleven more advocacy
pages to improve coverage would trade the library's credibility for its size.

## What would change that

Evidence. If a second system implements structural-loss guarding, or a third
verifies memory against its subject, those become patterns rather than
observations. The §5 list is the waiting room, and the promotion criterion should
be stated: **two independent instances, or one instance plus a measured result.**

## Two items the proposal has that the atlas genuinely lacks

- **Delta / diff-based writes** — write only when the observation differs
  materially from what is stored. Adjacent to `gate-the-expensive-path` but on
  the write side. Instances are thin and prompt-level: openworker's "revise that
  entry instead of adding a near-duplicate", memora's dedupe, memU. Worth
  watching.
- **Shared inter-agent memory with actor attribution.** The atlas has the pieces —
  memory-engine's agent principals, neo4j-agent-memory's shared graph,
  qwen-code's git-distributed team tier, magic-context's lattice — but no page,
  and the failure mode is real: neo4j's own report notes a shared graph means one
  agent's bad extraction is every agent's context, with no per-agent provenance
  traced.

Both are candidates under the two-instance rule above.

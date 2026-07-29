# The benchmark the field calls selective forgetting

**Status:** done; benchmarks.md §2 and §6 updated
**Origin:** *Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and
Emerging Frontiers*, [arXiv:2603.07670](https://arxiv.org/abs/2603.07670)
(v1, 8 March 2026). Single author, 15 pages. Read on 2026-07-29 as the second
of the recent surveys checked against the atlas.

## What the survey is

A literature review of agent memory 2022–early 2026, organised around a
write–manage–read loop cast as a POMDP belief update, with a three-axis taxonomy
(temporal scope / representational substrate / control policy) and five
mechanism families: context compression, retrieval stores, reflective
self-improvement, hierarchical virtual context, policy-learned management.

**It links no repositories.** The PDF contains exactly one hyperlink, to itself.
Every system in it is cited as a paper, so "check out the repos it links to" has
a short answer: there are none. What it does contain is a benchmark section
naming four evaluations, and that is where the useful work was.

## The claim worth checking

§5.2 and Table 2 say MemoryAgentBench probes four competencies including
**selective forgetting**, and that "most fail conspicuously" on it. §5.5 then
says "Nobody evaluates forgetting well. **Only MemoryAgentBench** tests
selective forgetting explicitly."

That is the strongest public claim that the atlas's central gap is already
covered, and it is stated by a survey rather than by the benchmark's own
marketing — which is what made it worth an hour.

## What the code says

[HUST-AI-HYZ/MemoryAgentBench](https://github.com/HUST-AI-HYZ/MemoryAgentBench)
at `455306dcabc3842526eb83cd4e225e5d486c5c5d` (21 May 2026):

- The fourth competency directory is `configs/data_conf/Conflict_Resolution/`.
  The name *selective forgetting* does not appear in the repository. The README
  lists "Conflict Resolution (CR)".
- Its dataset is `FactConsolidation`, loaded from
  `ai-hyz/MemoryAgentBench` on HuggingFace, split `Conflict_Resolution`.
- One row of the 6K multi-hop split: a numbered list of 455 facts, of which 123
  subjects carry a second contradicting entry at a higher index. Fact 0
  (`Thomas Kyd was born in the city of London`) is still present when fact 306
  (`... in the city of Leeds`) arrives. Nothing is removed.
- `utils/templates.py` gives the model the rule: *"the newer fact has larger
  serial number ... solve the conflicts of facts in the knowledge pool by
  finding the newest fact with larger serial number."*
- Scoring is `substring_exact_match` against the newer value.

So: both values retained, resolution rule supplied rather than inferred, score
is answer-time preference. This is LongMemEval's knowledge-update category at
greater length. It is a supersession benchmark, and a reasonable one — but the
question "is the rejected value still reachable?" is not asked, and could not be
asked of this design, because the rejected value is *supposed* to still be there.

## Where the mislabel happened

Worth separating, because it is not a survey error in the ordinary sense.

The benchmark's own repository names the competency accurately. Its paper
([arXiv:2507.05257](https://arxiv.org/abs/2507.05257)) is the point where
"conflict resolution" acquires the gloss *selective forgetting*, and the surveys
citing it inherit the gloss without the code. By the time it reaches a secondary
source it has become "the gold standard for agent-level forgetting evaluation".

The general shape — a capability that is real in the schema or the paper and
absent in the code path — is exactly what the
[forms/functions/dynamics note](2026-07-29-memory-survey-forms-functions-dynamics.md)
found in five of nine system reviews. This is the same failure moved up one
level, from implementation to literature. The correction is the same: read the
caller.

## MemoryArena, read in passing

[ZexueHe/MemoryArena](https://github.com/ZexueHe/MemoryArena) at
`6cd9de14b71915e39ac742a20dc33785e14b6aab` (31 May 2026), the survey's fourth
benchmark. A memory-agent-environment loop over web shopping, travel planning,
search and formal reasoning, with adapters for MIRIX, Mem0, Letta, A-MEM,
GraphRAG, MemoRAG and plain long context — four of which the atlas has reports
for.

Its design is the best answer in the literature to "long context is not memory":
later sessions are underspecified unless an earlier one stored something, so the
score is whether the task completes, not whether a question is answered. The
survey reports LoCoMo-saturated models dropping to 40–60% here.

Nothing in it deletes. `rg -i "delete|forget|tombstone"` over the memory layer
returns matches only inside the vendored MemoRAG and WebShop trees. It is
orthogonal to this atlas's question rather than evidence about it, and it is
recorded because a benchmark with no correction path is the ordinary case, not a
defect.

## What changed

1. **[benchmarks.md](../content/benchmarks.md) §2** — a new "Read directly, at a
   pinned commit" subsection with both benchmarks, their commits, and the
   FactConsolidation reading.
2. **[benchmarks.md](../content/benchmarks.md) §6** — the forgetting claim now
   names and disposes of its strongest apparent counterexample instead of
   resting on Table 8's silence. "Nobody has looked" was never the claim; the
   sharper version is that what is found when looking gets relabelled on the way
   into the citation graph.

Nothing else moved. The survey names no system the atlas lacks a decision on,
and it introduces no capability mark — it is a paper, and the atlas's marks come
from code.

## What it independently confirms

Three of the survey's own conclusions match findings the atlas reached from
code, arrived at from a literature review rather than from repositories:

- §5.5 "Nobody evaluates forgetting well" — the same gap, one benchmark short of
  the atlas's version, for the reason above.
- §7.5, that deletion must reach "every tier — including vector index entries
  and backup snapshots", and that once memory is in fine-tuned weights only
  machine unlearning reaches it. That is the
  [Second Me](../content/systems/second-me.md) finding stated as a general rule.
- §7.7, that memory systems need per-operation write/read/update/delete logging
  and a "memory diff", and that its absence is why demo-stage systems fail in
  production. That is the atlas's `audit_log` column, argued for rather than
  counted.

None of these is new to the atlas, and that is the point of recording them: two
methods that share no inputs reached the same three places.

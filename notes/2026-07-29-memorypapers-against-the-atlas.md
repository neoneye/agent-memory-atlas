# memorypapers.org, read against the atlas

**Status:** done — comparison published, A-MemGuard finding published,
[MemMachine reviewed](../content/systems/memmachine.md) and added
**Origin:** [memorypapers.org](https://memorypapers.org/), the curated paper
collection named in the reading list triaged in
[the ledger note](2026-07-29-a-reading-list-triaged.md). It was dismissed there
in one line, on a single landing-page fetch, as "links HippoRAG, Mem0 and MemOS,
all reviewed". That was wrong — or rather, it was true of the three repositories
the fetch surfaced and false about the collection. Read properly on 2026-07-29.

## What it actually is

200 papers across 16 categories, with per-paper explanation pages. The whole
corpus is embedded in the landing page and enumerable from
`sitemap.xml`, so it can be compared mechanically rather than by browsing.

The 16 categories: agent-memory, benchmark, cognitive-architecture,
continual-learning, episodic-memory, graph-memory, kv-cache, long-term-memory,
memory-architecture, personalization, procedural-memory, rag,
**security-privacy**, semantic-memory, survey, working-memory.

**It is roughly two collections in one.** By submission month:

| Era | Count | Character |
| --- | --- | --- |
| 2015–2023 | ~50 | Classical neural memory — memory networks, associative memory, episodic memory in RL, working memory in transformers, Hopfield networks |
| 2024–2026 | ~150 | Agent memory systems and benchmarks |

The first half is a literature the atlas does not cover and has never claimed
to: it is the parametric and latent lineage, and it is better represented here
than in any of the four surveys. The second half is the atlas's subject.

## Overlap: ten of seventy-three

Matching titles against the atlas's 73 pinned systems gives roughly ten
genuine hits — Mem0, MemOS, A-MEM, MIRIX, HippoRAG, Zep (reviewed here as
Graphiti), Hindsight, ByteRover, Generative Agents, ReMe — plus false positives
from substring matching that are worth naming so nobody repeats them:
`ai-memory` matched "AI memory", `pi` matched almost anything, and `memori`
matched *Memoria*, a different system.

That is the same ratio the four surveys produced, from a completely different
selection rule. Three consolidated lists and this one now agree that the
published corpus and the inspectable-code corpus overlap by about an eighth.

## What it has that the atlas does not

**A security-privacy category.** This is the real difference from the other
lists, and it is where the new material was. Sample: *Unveiling Privacy Risks in
LLM Agent Memory* (2502.13172), *ADAM: A Systematic Data Extraction Attack on
Agent Memory* (2604.09747), *A-MemGuard* (2510.02373), *Understanding Users'
Privacy Perceptions Towards LLM's RAG-based Memory* (2508.07664), *AgentSys*
(2602.07398), *MemEvoBench: Benchmarking Memory MisEvolution* (2604.15774),
*Governing Evolving Memory in LLM Agents* (2603.11768).

The 107-page survey used `privacy` ten times. This list has a category for it.

**Currency, up to a point.** It reaches 2604.20572 (late April 2026) — further
than the four surveys — but see the staleness note below.

## The finding: A-MemGuard

Worth the whole exercise on its own, and now published in
[overview.md](../content/overview.md) §Correction.

[TangciuYueng/AMemGuard](https://github.com/TangciuYueng/AMemGuard) at
`dd92f7ff21b9a904a703141be3d5b80170e57228` (2 July 2026) names this atlas's
central failure mode more precisely than the memory literature does — a poisoned
record produces a corrupted outcome that is "stored as precedent", amplifying
the error and lowering the threshold for the next one.

Its defence is the right shape. In `EhrAgent/ehragent/medagent.py`,
`check_consistency` splits retrieved memories into consistent and inconsistent;
each inconsistent one has its reasoning chain written back onto the entry as
`self.memory[i]["lesson"]`; later retrievals gather lessons from action-similar
entries and inject them under `[CRITICAL WARNING] Analysis of Past Lessons ...
AVOID the operations that previously led to failure`. A rejected-value record,
consulted on the read path, in security code.

**It is never persisted.** `main.py` loads the pool with `json.load` and never
writes it back; the sole `json.dump` is the evaluation results; `update_memory`
is called once, in a commented-out line. The lesson exists for one process and
is gone.

That is the same finding as the OWASP guard's unread quarantine, from an
independent project, and the pair is stronger than either alone: two security
artifacts both reached "record what was wrong and check it before acting", and
in both the record is in-process. **The missing piece is not the idea; it is
persistence, which nobody treats as the interesting half.**

A methodological note on how nearly this was missed: the first search used
`rg -ril "lesson"`, which rg parsed as `--replace=il`, so every match printed
with the matched text substituted. The output looked like a codebase full of
`ils` and `num_ils` and read as noise. The finding survived only because the
substitution was obvious enough to question. Recorded in the
[hazards note](2026-07-28-methodology-hazards.md) territory: a malformed search
that returns plausible output is worse than one that returns nothing.

## The one report this generates: MemMachine

[MemMachine/MemMachine](https://github.com/MemMachine/MemMachine), paper
[arXiv:2604.04853](https://arxiv.org/abs/2604.04853). Apache 2.0, ~475 Python
files, alembic migrations, docker-compose, an `evaluation/` tree, active on
28 July 2026. Episodic memory as a graph, profile memory in SQL, working memory
per session, explicitly persisting across restarts and model changes. It is in
scope by any reading of the test and it is **not yet reviewed**.

Its architectural position is why it matters rather than just qualifying:
*ground-truth-preserving* means it stores whole conversational episodes and
deliberately minimises lossy LLM extraction — the opposite of the
extract-and-consolidate default that most of this atlas implements. The atlas
has no strong representative of that stance, and the correction question is
sharper for a system that keeps the raw episode: there is more to fail to
delete.

**Reviewed on 2026-07-29** at `a681abf9623299bba8ad931e5d9af02fb6ef0997`. The
bet paid off in both directions. Citations resolve, which makes it the
evidence-before-belief pattern's plainest example. And the retention is exactly
what makes correction thin: a deleted feature leaves no rejected-value record,
and only a one-way `is_ingested` watermark stops the still-present evidence from
re-deriving it — protection from bookkeeping rather than from knowing the claim
was wrong.

The two findings that only reading callers produced: `delete_session`
acknowledges before it deletes, flipping the status to `Deleted` and enqueueing
the work on an in-process queue whose worker only logs on failure; and class
`MemMachine` defines `_cleanup_semantic_history` twice, with the live definition
missing the `ResourceNotReadyError` handling the dead one has, on the batch loop
that gates `delete_episodes`. `ruff` reports the file clean although `F` is
selected and `F811` is not ignored.

Marks `scope_enforced` only, so the atlas's counts did not move.

## Staleness, and a marker for it

The sitemap declares `changefreq: weekly` and a `lastmod` of 2026-07-29 — today
— on every entry. The newest paper in the corpus is from **late April 2026**.
Absent, and verified absent: 2605.06716 (the ACL 2026 Findings survey read
on 2026-07-28), 2605.10870, 2606.15903.

A second marker, and a more diagnostic one: its entry for 2604.16548 carries the
title *"A Survey on the Security of Long-Term Memory in LLM Agents: Toward
Mnemonic Sovereignty"*. That is the **v1** title. arXiv's current metadata for
that identifier reads *"...: Attacks, Defenses, and Governance Across the Memory
Lifecycle"* — the paper was retitled at v2 on 11 June 2026, and the collection
did not follow. So entries are not merely un-added after April; existing ones
are not re-checked either.

This is the same class of finding as the
[freshness tool](2026-07-28-editorial-backlog.md) applies to the atlas's own
pins, and the atlas has 22 stale ones, so it is an observation rather than a
complaint. The practical consequence for a reader is only this: a `lastmod` of
today does not mean the content is from today, on any site including this one.

## Not followed

Ranked by what they would change if read:

1. **MemEvoBench** (2604.15774) — QA and workflow tasks over "mixed benign and
   misleading memory pools" across 7 domains and 36 risk types, measuring
   behavioural drift from accumulated contamination. Adjacent to the atlas's
   question rather than the same: it scores whether polluted memory degrades
   behaviour, not whether a corrected value stays corrected. No repository found
   from the abstract page. The closest thing yet to a benchmark for the failure
   this atlas keeps finding, and worth reading before the benchmarks page makes
   another absolute claim.
2. **Governing Evolving Memory in LLM Agents** (2603.11768) — the title is the
   atlas's subject.
3. **Learning to Forget: Sleep-Inspired Memory Consolidation for Resolving
   Proactive Interference** (2603.14517), and **Unable to Forget** (2506.08184).
4. **Unveiling Privacy Risks in LLM Agent Memory** (2502.13172) and **ADAM**
   (2604.09747) — the extraction-attack side of the read path.
5. **GAM** appears twice, as 2511.18423 and 2604.12285. The atlas's scope
   section declines `VectorSpaceLab/general-agentic-memory` on the grounds that
   it is a corpus index with no licence; whether either paper is that project
   was not checked, and the decision should be revisited against whichever is.

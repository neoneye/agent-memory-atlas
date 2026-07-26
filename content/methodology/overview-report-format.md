---
title: Comparative Report Method
eyebrow: Methodology
description: The evidence and synthesis structure used for the cross-repository comparison.
root: ../..
page_kind: methodology
---

Use this format for the cross-repository overview after the individual repo reports are complete. The overview should synthesize implementation evidence across repos, not merely summarize each repo.

Suggested output path:

```text
content/overview.md
```

## Title

```md
# Agent Memory Systems Comparative Report
```

## 1. High-Level Taxonomy

Group the repositories by design style. Candidate categories:

- Local personal memory.
- Hosted memory API.
- Agent framework memory.
- Library primitives.
- RAG/context engine.
- Verification-first memory.
- Peer/user/session modeling system.
- Coding-agent memory.
- Multi-agent/shared-memory infrastructure.

For each category, explain:

- What problem it optimizes for.
- What tradeoffs it accepts.
- Which repos fit, and why.

## 2. Comparative Matrix

Use a table with these columns:

- Repo.
- Memory unit.
- Storage backend.
- Retrieval strategy.
- Write strategy.
- Update/delete model.
- Scoping model.
- Agent integration.
- Background processing.
- Trust/provenance model.
- Notable strengths.
- Main risks.

Keep the matrix dense and factual. Use short phrases, not paragraphs.

## 3. End-to-End Memory Lifecycle Comparison

Compare how each repo handles:

- Capture.
- Extraction.
- Consolidation.
- Retrieval.
- Context injection.
- Correction.
- Forgetting.
- Cross-session persistence.
- Cross-agent or cross-user sharing.

This should expose where systems differ architecturally, not just where their APIs differ.

## 4. Implementation Hotspots by Repo

Provide a cross-repo index of the most important implementation files/functions grouped by concern:

- Memory schema.
- Add/write path.
- Search/retrieve path.
- Context assembly path.
- Background workers.
- MCP/server interfaces.
- SDK/client surfaces.
- Evals/tests.

This section should help a developer jump directly to the essential code.

## 5. Design Patterns That Recur

Extract repeated patterns from the repos. Candidate patterns:

- Append-only memories with retrieval-time ranking.
- Hot-path tool-mediated memory.
- Background summarization/consolidation.
- Hybrid BM25/vector/entity search.
- User/session/project scoping.
- Memory-as-context API.
- MCP as universal agent adapter.
- Local SQLite for coding-agent memory.
- Hosted service for product memory.
- Profiles as low-latency summaries.
- Temporal metadata for current-vs-past reasoning.
- Separate document/RAG memory from personal/semantic memory.

For each pattern:

- Describe it.
- Name repos that use it.
- Explain why it works.
- Explain where it fails.

## 6. Antipatterns and Failure Modes

Extract repeated risks and failure modes. Candidate examples:

- Treating extracted LLM facts as ground truth.
- No provenance.
- Weak correction semantics.
- Silent overwrites.
- Over-reliance on vector search.
- Memory tools the agent forgets to call.
- No compaction survival strategy.
- No evals for retrieval quality.
- No deletion/privacy story.
- Mixing RAG documents and personal memory without type boundaries.
- No trust distinction between user facts, agent conclusions, and external documents.
- Background processing that makes reads eventually consistent without clear UX/API semantics.

Ground the claims in the individual reports.

## 7. What Seems to Work

Give evidence-backed observations about practical memory system design:

- Storage choices that appear operationally sound.
- Retrieval approaches that show up repeatedly.
- Useful API surfaces.
- Scoping models that avoid obvious ambiguity.
- Trust/provenance mechanisms that improve correctness.
- Integration patterns that agents are likely to use reliably.

Avoid vague praise. State the engineering reason each item works.

## 8. What I Would Build

Synthesize a recommended architecture for a serious agent memory system.

Cover:

- Minimal viable memory core.
- Data model.
- Write path.
- Retrieval path.
- Context assembly.
- Trust/provenance layer.
- Correction/deletion model.
- Agent integration surface.
- Testing/eval strategy.
- Later extensions.

Be opinionated. Distinguish "ship first" from "add later".

## 9. Repo-by-Repo Verdicts

For each repo, include:

- Best idea.
- Biggest risk.
- Most reusable component.
- Code maturity impression.
- When to study this repo.
- When not to copy it.

Keep each repo verdict short and blunt.

## 10. Practical Checklist for Your Own System

Convert the findings into a build checklist:

- Schema and scoping.
- Write path.
- Retrieval.
- Context assembly.
- Trust/provenance.
- Agent UX.
- Testing/evals.
- Operations.
- Privacy/deletion.

This section should be actionable for implementation.

## 11. Appendix

Include:

- File index.
- Glossary.
- Commands used.
- Repos inspected.
- Known limitations of the analysis.

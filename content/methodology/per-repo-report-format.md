---
title: Per-Repository Review Method
eyebrow: Methodology
description: The code-grounded review format applied consistently to each memory system.
root: ../..
page_kind: methodology
---

Use this format for each repository-specific report. The report should be technical, code-grounded, and opinionated. Prefer concrete file paths, functions, classes, schemas, prompts, API endpoints, tests, and call flows over product claims.

Suggested output path:

```text
reports/repos/<repo-name>.md
```

## Title

```md
# <Repo> Memory System Report
```

## 1. Executive Summary

Cover:

- What kind of memory system this is.
- Primary users and agent model.
- Core design philosophy.
- What is genuinely interesting technically.
- Where the implementation appears strongest.
- Where the implementation appears weakest or least proven.

Keep this section concise. It should let a senior engineer decide whether to keep reading.

## 2. Mental Model

Explain:

- What the system considers a "memory".
- Whether memories are raw messages, extracted facts, summaries, profiles, rules, documents, embeddings, graph nodes, verified beliefs, or something else.
- Memory lifecycle: capture -> extraction -> storage -> retrieval -> injection -> update/delete/decay.
- Whether memory is agent-controlled, background-managed, user-controlled, or hybrid.
- Whether the system treats memory as ground truth, candidate evidence, inferred state, or verified state.

## 3. Architecture

Document:

- Main components and boundaries.
- Runtime shape: library, daemon, API server, MCP server, CLI, hosted service, local DB, worker, SDK, framework plugin.
- Persistence model.
- Search and retrieval stack.
- Async/background processing model.
- External dependencies.
- Deployment assumptions.

Include a Mermaid diagram when it clarifies the system.

## 4. Essential Implementation Paths

This is the most important section. Map the core behavior to concrete implementation locations.

For each path, include exact files and the key functions/classes/modules:

- Capture/write path.
- Extraction/consolidation path.
- Retrieval/search path.
- Context assembly/injection path.
- Update/delete/forget/conflict path.
- Schema/storage definitions.
- Background worker or queue path.
- MCP/API/SDK integration path.
- Tests/evals covering the behavior.

Each item should answer:

- Where does this behavior start?
- What are the important intermediate calls?
- Where does state change?
- Where are ranking, filtering, consolidation, or trust decisions made?

## 5. Memory Data Model

Analyze:

- Tables, schemas, ORM models, types, interfaces, or document structures.
- Scoping model: user, session, project, agent, workspace, peer, team, org, global, tenant.
- Metadata and provenance.
- Temporal fields.
- Versioning, correction chains, contradiction support, TTL, pinning, deletion.
- Separation between episodic memory, semantic memory, profiles, documents, summaries, rules, and tool traces.
- Multi-tenant/auth boundaries if relevant.

## 6. Retrieval Mechanics

Analyze:

- Keyword search, vector search, hybrid search, graph traversal, entity matching, temporal filtering, recency, reranking, LLM judging, or learned ranking.
- Query transformation.
- Ranking/scoring/fusion.
- Token budgeting.
- Context formatting.
- Whether retrieval is automatic, tool-mediated, or application-driven.
- Failure modes: stale hits, over-recall, under-recall, noisy summaries, bad entity merges, irrelevant long-tail matches.

## 7. Write Mechanics

Analyze:

- How memories are created.
- Whether writes happen hot-path, background, manually, or through tools.
- LLM extraction prompts or structured extractors.
- Deduplication and consolidation.
- Update vs append-only behavior.
- Delete/forget/TTL behavior.
- Conflict handling.
- How agent-generated facts are handled.
- How noisy or malicious inputs are filtered, if at all.

## 8. Agent Integration

Analyze:

- MCP tools, SDK APIs, framework hooks, CLI flows, REST endpoints, plugins, browser extensions, or app integrations.
- How much agency the model has over memory.
- Prompt/tool affordances.
- Whether the agent is expected to explicitly save/search memory.
- Whether there is automatic context injection.
- Session lifecycle and compaction-boundary handling.
- How easy the integration would be to adapt for another agent.

## 9. Reliability, Safety, and Trust

Analyze:

- Provenance guarantees.
- Verification, attestation, corroboration, or trust levels.
- Protection against prompt-injected false memories.
- Auth/multitenancy issues.
- Race conditions and eventual consistency.
- Data loss risks.
- Privacy/delete semantics.
- Backup/sync/replication strategy.
- Whether the memory layer can safely represent uncertainty.

## 10. Tests, Evals, and Benchmarks

Document:

- What is actually tested.
- Memory-specific unit/integration tests.
- Retrieval quality tests.
- Eval harnesses and benchmark scripts.
- Claimed benchmark coverage vs evidence in the repo.
- Missing tests you would want before trusting the system.

Be explicit when a claim appears only in docs and is not backed by code or tests.

## 11. Patterns Worth Stealing

List concrete implementation ideas useful for building a serious agent memory system.

Prefer specific patterns, for example:

- A schema trick.
- A retrieval fusion strategy.
- A scoping model.
- An MCP tool design.
- A compaction survival mechanism.
- A background consolidation workflow.
- A test/eval pattern.

## 12. Antipatterns / Risks

List specific design or implementation choices that look fragile, overcomplicated, under-specified, hard to operate, or likely to degrade memory quality.

Ground each item in code, docs, or missing coverage.

## 13. Build-vs-Borrow Takeaways

Answer:

- What should be reused conceptually?
- What should be avoided?
- When is this design appropriate?
- When is it the wrong shape?
- Which parts could be copied or reimplemented cleanly?
- Which parts are too coupled to the repo's product or framework?

## 14. Open Questions

List things unclear from code/docs that would require:

- Running the system.
- Reading issue/PR history.
- Inspecting hosted behavior.
- Asking maintainers.
- Looking at private infrastructure.

## Appendix: File Index

Include a compact index of the most important files inspected, grouped by concern:

- Storage/schema.
- Write path.
- Retrieval path.
- Context assembly.
- Background workers.
- MCP/API/SDK.
- Tests/evals.

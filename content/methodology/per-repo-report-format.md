---
title: Per-Repository Review Method
eyebrow: Methodology
description: The code-grounded review format applied consistently to each memory system.
root: ../..
page_kind: methodology
---

Use this format for each repository-specific report. The report should be technical, code-grounded, and opinionated. Prefer concrete file paths, functions, classes, schemas, prompts, API endpoints, tests, and call flows over product claims.

## Who these are written for

Two readers, both expert: a **senior engineer evaluating memory systems**, and the **developers of the repository under review**. Both can act on a finding immediately — the second can open the exact file and fix it — and both are ill-served by a gloss that a plain-language rewrite would insert between them and the evidence. So the density is deliberate. Name the file, the symbol, the config key and the constant; do not stop to define `FTS5`, compaction, or a capability mark for a newcomer. A report that reads as a wall to someone who does not work on memory systems is aimed correctly, not written badly. This is not a beginner tutorial, and it should not be softened into one; the executive summary's job is to let one of those two readers decide whether to keep reading, not to onboard a third.

Suggested output path:

```text
content/systems/<repo-name>.md
```

## Dates are absolute, never relative

Every report is pinned to a commit and stamped with `analyzed_at`, so the reader
already knows when the reading happened. Durations measured from *now* — "dormant
for two and a half years", "updated ten months later", "the day of review",
"recently", "currently" — are redundant against that stamp and silently wrong a
few months later. Write the date.

- **No:** "Dormant for two and a half years."
- **Yes:** "No commit since 28 February 2024."
- **No:** "The pinned commit is from the day of review."
- **Yes:** "The pinned commit is dated 29 July 2026."

"At this commit" is the correct way to scope a claim to what was read.
[OpenWorker](../../systems/openworker/) ships this as a rule in its own memory
guidance — *"use absolute dates, never 'yesterday'"* — and this atlas quoted it
approvingly before breaking it, which is how it became a rule here too.
`scripts/test_site.sh` checks for the common phrasings.

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

**This section is about epistemics, not infrastructure.** Answer how a thing
becomes a belief and how it stops being one. Keep storage engines, servers and
job runners out of it — they belong in section 3, and letting the two sections
drift into the same pipeline diagram at two zoom levels is the most common way
this format wastes a reader's time.

Explain:

- What the system considers a "memory".
- Whether memories are raw messages, extracted facts, summaries, profiles, rules, documents, embeddings, graph nodes, verified beliefs, or something else.
- The state machine: what states a memory can hold, what moves it between them, who or what is allowed to move it, and how it dies — superseded, rejected, expired, decayed, deleted, or never.
- Whether memory is agent-controlled, background-managed, user-controlled, or hybrid.
- Whether the system treats memory as ground truth, candidate evidence, inferred state, or verified state.

A text or ASCII sketch of the state machine usually says more here than a
component diagram.

## 3. Architecture

**This section is about infrastructure, not epistemics.** Where the bytes live,
what processes run, what the operator has to stand up.

Document:

- Main components and boundaries.
- Runtime shape: library, daemon, API server, MCP server, CLI, hosted service, local DB, worker, SDK, framework plugin.
- Persistence model.
- Search and retrieval stack.
- Async/background processing model.
- External dependencies.
- Deployment assumptions.

Include a Mermaid diagram when it clarifies the system.

### Deployment and ergonomics

State what adopting this actually costs an operator, because a design that is
excellent on paper and needs four services is a different proposition from a
single binary:

- What has to be running: nothing, a local file, SQLite, Postgres, a vector
  service, a queue, a graph database, a hosted API, a GPU.
- Whether it can run fully local and offline, and what degrades if it does.
- Whether an API key is required to store anything at all.
- Install and first-run path — one command, a Docker compose file, or a build.
- Whether the store is human-readable and repairable by hand when something
  goes wrong.

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

### Operational cost

Memory sits on the critical path of every turn, so say what it costs:

- Is the write path **synchronous** — does the agent block on an LLM extraction
  before it can continue — or is it deferred?
- If deferred, what is the lag before a new memory is retrievable? State it even
  approximately; nothing in this atlas measures it and the gap is worth naming.
- Does any background pass re-read or rewrite the whole store, and how often?
  A nightly map-reduce over everything has a token bill that scales with the
  corpus rather than with the day's activity.
- On the read path: how much is injected per turn, is it bounded, and does the
  injection sit where it will invalidate a provider's prompt-prefix cache?

See [benchmarking agent memory](../../benchmarks/) for why these matter and how
rarely anyone reports them.

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

## 11. For Your Own Build

One section, three subheads with genuinely different jobs. Do not restate what
section 9 already assessed — that section says what *this system* is like, this
one says what *you* should do about it.

### Steal

Transferable mechanisms, phrased as advice a builder could act on without
adopting the system. Name the mechanism, not the product.

### Avoid

Transferable mistakes. A gap in section 9 belongs here only if it generalizes —
if the failure is specific to this codebase, it stays in section 9.

### Fit

Whether this whole design suits a reader, which is the one judgement the two
lists above cannot express: the maintenance budget it assumes, the scale it
targets, the deployment it needs, and who should walk away from it entirely.
Resist re-listing the mechanisms; if this subhead reads as a summary of Steal
and Avoid, delete it and write the judgement instead.

## 12. Open Questions

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

## History

One dated entry per reading, newest first, and the only place a re-review is
narrated:

```text
**2026-08-03** — [`<full 40-char sha>`](<commit url>) — 41 commits on. The
mechanism did not move and no mark changed. One published claim was stale: …
```

The section exists because the alternative kept happening. Re-review narration
was written into whatever paragraph it contradicted — "this report previously
said", "at the commit this report first covered" — and into two lists in
`content/overview.md` that had nothing to do with one another, so a reader
asking *what changed since I last looked* had to reconstruct it from prose in
two files.

Two rules follow from that, and they pull in opposite directions on purpose:

- **The body is the state; History is the log.** A sentence that would have to
  change when the *atlas* changes rather than when the *system* changes belongs
  here and nowhere else. Correct the body in place; do not append a correction
  beside the old text and do not narrate the correction in the body.
- **History is per-system.** What a reading taught the *method* — that criticisms
  are the claims most likely to go stale, that an orphaned pin is not a stale one
  — is not about the system and belongs in the History section of
  `content/overview.md` instead.

`scripts/check_history.py` asserts that the newest entry's date equals
`analyzed_at`, and that entries run newest-first. It does not read the prose: that
an entry exists and is dated to the current pin is checkable, and what it says is
a judgement.

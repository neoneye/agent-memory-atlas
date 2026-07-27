---
title: "Basic Memory"
eyebrow: "Human-editable Markdown graph"
description: "A local-first MCP memory where Markdown is canonical and database indexes provide graph and hybrid retrieval."
root: ../..
page_kind: system
source_name: "basicmachines-co/basic-memory"
source_url: https://github.com/basicmachines-co/basic-memory
revision: 232f2c2fc4e91564d88bcc312ed3d8bd1e8e051b
revision_url: https://github.com/basicmachines-co/basic-memory/commit/232f2c2fc4e91564d88bcc312ed3d8bd1e8e051b
analyzed_at: 2026-07-26
capabilities: "scope_enforced"
matrix:
  memory_unit: "Canonical Markdown note; indexed entity, observation, relation"
  storage: "Filesystem source + SQLite/PostgreSQL projection"
  retrieval: "FTS5/tsvector, optional semantic chunks, hybrid score fusion, graph context"
  write: "MCP/API writes accepted Markdown; file watcher reconciles human edits"
  update_delete: "Distinct create/replace/edit/move/delete with stable ID and reindex"
  scoping: "Project, workspace, tenant, local/cloud route"
  integration: "MCP tools, typed clients, API, CLI"
  background: "Watcher, startup reconciliation, indexing workflows"
  trust: "Human-visible source/checksums; no candidate/verified state"
  strengths: "Inspectable portable memory with rebuildable indexes"
  risks: "Bidirectional sync complexity; agent can write unsupported claims"
---

## 1. Executive Summary

Basic Memory is a local-first knowledge system where Markdown files are the canonical memory and SQLite or PostgreSQL is a rebuildable projection for graph and search. Agents interact through MCP tools, while people can read, edit, move, version, and synchronize the same notes with ordinary filesystem tools.

Its best architectural decision is the source-of-truth boundary. A note is not an opaque row hidden behind an embedding API: accepted Markdown owns the knowledge. Entities, observations, relations, full-text rows, semantic chunks, and materializations are derived state that must be kept coherent or rebuilt.

The tradeoff is coordination complexity. Human edits, agent writes, file watchers, APIs, cloud routing, graph projections, and two database backends all touch the same lifecycle. The code has grown serious transaction, checksum, reconciliation, and composition-root machinery to keep that promise.

## 2. Mental Model

A project is the isolation boundary. A note is the human-facing canonical document. An entity is the indexed database representation of that note. Observations and relations are structured Markdown constructs owned by their source note.

```text
human editor / MCP tool
  -> accepted Markdown note
       |- YAML frontmatter
       |- prose
       |- [category] observations
       `- typed [[relations]]
  -> parse + transaction
  -> entity + observation + relation graph
  -> FTS rows + optional semantic chunks
  -> search / build_context / navigation
```

The direction also works in reverse: a file watcher parses external edits and reconciles projections. Database state is not allowed to silently outrank the file.

## 3. Architecture

Basic Memory has API, MCP, and CLI entrypoints, each with a composition root. Only those roots read global configuration; downstream services receive explicit dependencies.

Main layers:

- `src/basic_memory/markdown/`: parsing and serialization.
- `models/` and `schemas/`: persistence and boundary models.
- `services/`: note preparation, accepted-content writes, entities, search, projects, and initialization.
- `repository/`: SQLite/PostgreSQL data access and hybrid retrieval.
- `indexing/`: portable mutation, materialization, reconciliation, and project-index workflows.
- `index/`: local file watcher and concrete indexing adapters.
- `api/`: FastAPI routers.
- `mcp/clients/` and `mcp/tools/`: typed HTTP clients and thin agent-facing tools.
- `runtime/`: local/test/cloud mode contracts.

The intended dependency path is explicit: MCP tool → typed client → API router → service → repository. Local MCP calls use an in-process ASGI client; cloud projects can route to remote HTTP per project.

## 4. Essential Implementation Paths

- Domain rules: `docs/DOMAIN_MODEL.md`.
- Composition: `docs/ARCHITECTURE.md` and `api|mcp|cli/container.py`.
- Persistence entities: `models/knowledge.py`.
- Markdown boundary: `markdown/entity_parser.py`, `markdown/markdown_processor.py`, and `markdown/schemas.py`.
- Agent write: `mcp/tools/write_note.py` → `mcp/clients/knowledge.py` → API/service.
- Accepted note orchestration: `services/note_preparation.py`, `services/note_content_writes.py`, and indexing workflows.
- Search orchestration: `services/search_service.py`.
- Backend retrieval: `repository/sqlite_search_repository.py`, `postgres_search_repository.py`, and `search_repository_base.py`.
- Context assembly: `mcp/tools/build_context.py` and `schemas/memory.py`.
- External-edit sync: `index/watch_service.py`, `index/watch_coordinator.py`, and `indexing/`.
- Startup reconciliation: `services/initialization.py`.

## 5. Memory Data Model

The canonical note contains:

- frontmatter: title, type, permalink, tags, and arbitrary metadata;
- ordinary Markdown prose;
- observations written as `- [category] content #tags (context)`;
- relations written as `- relation_type [[Target]] (context)` or inline wiki links.

The database projects this into:

- `Project`: ownership/isolation boundary.
- `Entity`: stable external identity, mutable path/permalink, checksums, timestamps, metadata, and content state.
- `Observation`: categorized fact owned by an entity.
- `Relation`: directed semantic link owned by its source entity, with resolution state.
- search rows for whole entities, observations, and relations.
- optional semantic chunk and embedding rows.

Move operations preserve stable identity while changing location. Relations belong to the source note, an important rule for deletion and reconciliation.

## 6. Retrieval Mechanics

Basic Memory supports:

- SQLite FTS5 or PostgreSQL `tsvector` full-text search;
- title, permalink, metadata, tag, category, date, and type filters;
- optional semantic chunk embeddings;
- hybrid score-based fusion of lexical and vector results;
- relaxed lexical fallback for question-shaped queries that fail strict all-term matching.

Semantic content is split at Markdown-aware boundaries. Candidate counts over-fetch, score thresholds gate weak matches, and FTS scores are normalized before hybrid fusion. Search indexes notes, observations, and relations separately, so an agent can land on a precise fact or graph link instead of only a whole document.

`build_context` expands from a memory URL/entity through related observations and relations with depth and result controls. Direct file/navigation tools complement search; the system does not force every task through embeddings.

## 7. Write Mechanics

MCP `write_note` validates the project and path, constructs an `Entity` request, and calls a typed client. The API/service layer prepares canonical content, checks conflicts and checksums, persists the accepted note snapshot, parses graph structures, and updates search projections.

`MarkdownProcessor.write_file()` performs a complete read-modify-write with an optional dirty-file checksum and an atomic filesystem replace. External edits enter through the watcher and project-index workflows.

Create, replace, edit, move, and delete have distinct orchestration. A move preserves external identity; a delete must remove canonical content through the owning storage service and then reconcile entity, graph, materialization, and search state. This discipline is the cost of a real source-of-truth model.

## 8. Agent Integration

MCP is first class. Tools include write/edit/move/delete/read/view/search notes, build context, recent activity, directory browsing, schema operations, project management, diagnostics, and workspaces.

Per-project routing is unusually thoughtful. `get_project_client()` resolves the requested project, chooses local ASGI or cloud HTTP, applies authentication at client creation, validates the project, and yields both client and active project. `project_id` can disambiguate same-named projects across workspaces.

Tool responses are deliberately human- and model-readable, often including repair suggestions. This improves usability but makes the MCP surface verbose.

## 9. Reliability, Safety, and Trust

Strong mechanisms include:

- Markdown as inspectable, versionable source;
- project/workspace/tenant boundaries and path traversal checks;
- atomic file writes and checksum-based dirty detection;
- transactional persistence of accepted note, graph, and search state;
- startup reconciliation and watcher lifecycle ownership;
- stable external IDs across moves;
- derived-index cleanup on delete;
- SQLite and PostgreSQL parity tests;
- optional semantic features fail explicitly when dependencies are absent.

Basic Memory preserves author-visible provenance better than extracted-fact stores, but it has no universal candidate/verified/rejected state. An agent can write an observation directly into canonical Markdown. Human editability makes correction easy, yet preventing a rejected claim from returning requires application policy or version-history review.

## 10. Tests, Evals, and Benchmarks

The project targets full unit/integration coverage across SQLite and PostgreSQL, with isolated temporary projects. Tests cover parsing, file/database synchronization, MCP/API flows, search, semantic vectors, move/delete invariants, cloud/local routing, watchers, schemas, and recovery.

A separate benchmark harness runs reproducible retrieval comparisons with LoCoMo data, common query/top-k settings, explicit skipped-provider records, checksums, and manifests containing repository SHAs and runtime metadata. That provenance policy is exemplary, though benchmark outcomes should still be interpreted as retrieval—not total memory quality.

## 11. Patterns Worth Stealing

- Make human-readable content canonical and indexes disposable.
- Model every database/search structure as a projection with a reconciliation path.
- Keep project scope on identity and routing, not just search filters.
- Use stable IDs across file moves.
- Own relations at their source note.
- Put typed clients between MCP tools and API routes.
- Treat create, replace, edit, move, and delete as distinct lifecycle operations.
- Record exact benchmark provenance and explicit provider skips.

## 12. Antipatterns / Risks

- Source-of-truth synchronization creates substantial code and race surfaces.
- Markdown conventions can be malformed by arbitrary editors.
- Direct agent writes can promote unsupported claims to canonical notes.
- Git/backups may conflict with true erasure expectations.
- Search and context behavior differs when semantic search is disabled.
- Verbose agent tools can consume context.
- Supporting local/cloud and SQLite/PostgreSQL multiplies integration paths.
- File watchers need careful lifecycle ownership and platform testing.

## 13. Build-vs-Borrow Takeaways

Borrow Basic Memory's canonical-file/projection boundary when humans must own and edit memory directly. It is particularly good for research notes, project knowledge, and agent collaboration where portability matters more than invisible automatic fact extraction.

Do not choose it merely because Markdown feels simple. Bidirectional sync is not simple. If humans never edit memory, a transactional database with an export view may be easier. If agents can write canonical notes, add review or trust states for high-impact claims.

## 14. Open Questions

- What prevents an agent from turning prompt injection into canonical Markdown?
- How are conflicting simultaneous human and agent edits surfaced to users?
- Can deletion prove removal from filesystem history, cloud storage, vectors, and backups?
- How should rejected or disputed observations be represented in Markdown?
- What is the largest project size before watcher/index rebuild cost becomes intrusive?
- How close is SQLite/PostgreSQL hybrid ranking parity on the same corpus?

## Appendix: File Index

- `docs/DOMAIN_MODEL.md`
- `docs/ARCHITECTURE.md`
- `src/basic_memory/models/knowledge.py`
- `src/basic_memory/markdown/schemas.py`
- `src/basic_memory/markdown/entity_parser.py`
- `src/basic_memory/markdown/markdown_processor.py`
- `src/basic_memory/services/note_preparation.py`
- `src/basic_memory/services/note_content_writes.py`
- `src/basic_memory/services/search_service.py`
- `src/basic_memory/repository/search_repository_base.py`
- `src/basic_memory/repository/sqlite_search_repository.py`
- `src/basic_memory/repository/postgres_search_repository.py`
- `src/basic_memory/mcp/project_context.py`
- `src/basic_memory/mcp/tools/write_note.py`
- `src/basic_memory/mcp/tools/search.py`
- `src/basic_memory/mcp/tools/build_context.py`
- `src/basic_memory/index/`
- `src/basic_memory/indexing/`
- `tests/`
- `test-int/`

---
title: Scope as a First-Class Key
eyebrow: Pattern · Boundaries
description: Make memory ownership and visibility part of identity, storage, conflict detection, and retrieval—not an optional metadata filter.
root: ../..
page_kind: pattern
---

## Intent

Prevent one user, agent, project, room, or session from reading or mutating memory that belongs to another context.

## The problem

A highly relevant memory from the wrong scope is still a severe failure. Adding a `project` field after the storage and retrieval model is built rarely fixes the problem: uniqueness, conflicts, indexes, access checks, inheritance, and deletion may still be global.

## The pattern

Define scope as part of the memory key and every operation:

```text
tenant / user / agent / project / session / memory-key
```

The exact lattice varies. Some systems need a strict hierarchy; others need namespaces or an allow-list of readable scopes. In every case:

- Writes name an owning scope.
- Reads state which scopes are visible.
- Dedupe and conflict checks run within intentional scope boundaries.
- Storage indexes begin with scope.
- Cache and embedding identifiers cannot collide across scopes.
- Authorization is checked independently of relevance.

## Why it works

The system can reason about visibility before ranking. Scope-aware identity prevents unrelated memories from overwriting or corroborating each other. It also makes migration, export, retention, and deletion tractable.

## Tradeoffs

Users often expect some memories to inherit: a project may read global preferences, while a private session may not write back globally. Hierarchies introduce precedence and conflict questions. Duplicating memories across scopes creates drift; sharing references creates access and lifecycle coupling.

Scope is not a substitute for authorization. A row tagged `user_id` is unsafe if callers can choose arbitrary IDs.

## Seen in the atlas

[Hindsight](../../systems/hindsight/) makes the memory bank an isolation and configuration boundary. [Graphiti](../../systems/graphiti/) carries `group_id` through nodes, edges, episodes, and search. [Mastra Observational Memory](../../systems/mastra-observational-memory/) chooses thread or resource scope. [MemOS](../../systems/memos/) registers memory cubes to users. [Basic Memory](../../systems/basic-memory/) uses projects and workspaces for identity, routing, and search. [Honcho](../../systems/honcho/) models workspace, peer, session, and representation boundaries. [RainBox](../../systems/rainbox/) uses a scope lattice with sensitivity rules. [Engram](../../systems/engram/), [llm-wiki-memory](../../systems/llm-wiki-memory/), and [Verel](../../systems/verel/) reinforce the pattern. [Swafra](../../systems/swafra/) shows the opposite risk: a source title in one global corpus is not a boundary.

## Tests to require

- Cross-user, cross-agent, and cross-project leakage.
- Dedupe and conflict behavior for identical keys in different scopes.
- Inheritance and precedence across parent/child scopes.
- Unauthorized caller-supplied scope IDs.
- Cache, embedding, and background-job isolation.
- Export and deletion of exactly one scope.

## Related patterns

- [Explicit write destination](../explicit-write-destination/)
- [Governed write gateway](../governed-write-gateway/)
- [Hybrid retrieval fusion](../hybrid-retrieval-fusion/)

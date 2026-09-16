---
title: "Bifrost"
eyebrow: "The tool promises long-term memory; the filename holds a session id"
description: "An agent runtime orchestrator whose memory layer is 148 lines over Memvid, keyed to one file per tenant and session — so the tool that tells a model it is searching its absolute long-term memory reaches only the session it is in, unless the session id is missing."
root: ../..
page_kind: system
source_name: "MegaWiz-Dev-Team/Bifrost"
source_url: https://github.com/MegaWiz-Dev-Team/Bifrost
archive_name: "MegaWiz-Dev-Team--Bifrost"
revision: 936957b350091997c34380ffdd91b395d47225ae
revision_url: https://github.com/MegaWiz-Dev-Team/Bifrost/commit/936957b350091997c34380ffdd91b395d47225ae
analyzed_at: 2026-09-16
capabilities: ""
stack_storage: "delegated"
stack_retrieval: ""
stack_source: "reviewed"
matrix:
  memory_unit: "A conversation frame — the user query and the agent's final answer concatenated, titled with the session id and a timestamp"
  storage: "One Memvid `.mv2` file per tenant and session, named `agent_{tenant}_session_{session}.mv2` under a base directory"
  retrieval: "Delegated to Memvid's own search, exposed as a single agent tool taking a query string"
  write: "One commit per completed turn from the swarm overseer, with failures logged and swallowed"
  update_delete: "None found — the wrapper appends, and exposes no delete, supersede or retire path"
  scoping: "The tenant and session are the filename, so separation is a file boundary rather than a predicate"
  integration: "A tool named `memvid_agent_memory_search`, registered on the agent builder alongside the other tools"
  background: "None in the memory path"
  trust: "None in the memory path; the runtime's guardrails and RL audit trail sit elsewhere in the tree"
  strengths: "The wrapper is small enough to read in one sitting and does the honest thing at both ends: the search tool and the commit are constructed from the same `(tenant_id, session_id.unwrap_or(\"anon\"))` pair, so what an agent can read is exactly what this runtime wrote for it — there is no asymmetry between the write key and the read key, which is the bug this shape usually has. A commit failure is logged at error level rather than propagated, so a memory write cannot fail a user's turn. And the wider runtime is candid about its own staging: `INTEGRATION_STATUS.md`, `PHASE_A_SUMMARY.md` and `COMPLETION_SUMMARY.md` sit at the top level, which tells a reader which parts are finished before they go looking"
  risks: "The tool's description tells the model it is searching \"your absolute long-term memory for past conversations, facts, or context you have stored\", and the store it reaches is one file per session. Past conversations therefore means earlier turns of the current conversation — unless the session id is absent, in which case both the write and the read fall back to the literal `\"anon\"` and a tenant's whole session-less history pools into a single shared file, which is the only configuration in which the description is accurate. Nothing in the 148-line layer supersedes, retires or de-duplicates: each turn appends the query and the answer concatenated, so a fact restated ten times is ten frames, and there is no delete path at all. Scope is the filename rather than a predicate, which is the physical-partition shape this atlas does not count as enforcement. The tree also carries `.backup` copies of two source files committed beside their originals in `src/`"
---

## 1. Executive Summary

Bifrost is a self-hosted agent runtime engine — AGPL-3.0, Rust 1.75+ with a
Python side, 11,091 lines of Rust and 121 test functions, part of a named
multi-repository platform in which it plays orchestrator: receive a request,
classify intent, delegate to tool and agent workers, assemble the answer, under
guardrails it labels scope guard, tool allowlist, citation check, confidence gate
and disclaimer.

Its memory is 148 lines. `src/memory/` holds a manager and a tool over
`memvid_core` — [Memvid](../memvid/) being a separate project this atlas reads in
its own right — and the whole of the storage decision is one function:

```rust
fn get_agent_path(&self, agent_id: &str, session_id: &str) -> PathBuf {
    self.base_path.join(format!("agent_{}_session_{}.mv2", agent_id, session_id))
}
```

One file per agent and session. The swarm overseer commits a frame per completed
turn — the user query and the agent's final answer concatenated, titled with the
session id and a timestamp — and registers a search tool on the agent builder.
Both are constructed from the same pair:

```rust
session_id.unwrap_or("anon")
```

**The two ends agree, and that is the good part.** The key an agent reads with is
the key this runtime wrote with, so there is no asymmetry between write and read
— the failure this shape usually has. A commit failure is logged at error level
and swallowed, so a memory write cannot fail a user's turn.

**The description and the key do not agree.** The tool tells the model it is
searching "your absolute long-term memory for past conversations, facts, or
context you have stored using this tool". The store it reaches is scoped to the
current session by filename, so past conversations means earlier turns of the
present one. A new session opens a new file and starts empty.

The exception is the fallback. When no session id is supplied, both paths use the
literal `"anon"`, so a tenant's session-less turns accumulate in one shared
`agent_{tenant}_session_anon.mv2` — the only configuration in which the tool's
description is accurate, reached by the absence of an identifier rather than by a
decision.

No marks. Scope here is a filename, which is the physical-partition shape this
atlas does not count as enforcement; nothing in the layer supersedes, retires or
de-duplicates, and no delete path exists at all, so a fact restated ten times is
ten frames. The mechanisms that would earn marks belong to Memvid, and are read
there.

Two things a reader should know about the tree rather than the code. The top
level carries `INTEGRATION_STATUS.md`, `PHASE_A_SUMMARY.md`,
`COMPLETION_SUMMARY.md` and a Docker build workaround — useful, because they say
which parts are finished before a reader goes looking. And `src/` contains
`rl_orchestrator.rs.backup` and `rl_safe_deployment.rs.backup` committed beside
their originals.

## 2. Mental Model

A **frame** is one turn, flattened into text.

A **memory** is a file, and the session is part of its name.

**"anon"** is where memory becomes long-term, by accident.

```mermaid
%% caption: the write and the read use the same tenant and session pair, so they agree — and both resolve to a per-session file, while the tool description promises memory across conversations
flowchart TB
    REQ["a user request reaches the overseer"] --> RUN["classify intent, delegate to<br/>tool and agent workers, assemble"]
    RUN --> TOOLREG["register MemvidSearchTool::new(<br/>  manager,<br/>  tenant_id,<br/>  session_id.unwrap_or(\"anon\")<br/>)"]
    TOOLREG --> DESC["tool description to the model:<br/>'Search your absolute long-term memory<br/>for past conversations, facts, or context<br/>you have stored using this tool.'"]
    RUN --> DONE["turn completes"]
    DONE --> COMMIT["commit_memory(<br/>  tenant_id,<br/>  session_id.unwrap_or(\"anon\"),<br/>  'User Query: … Agent Response: …'<br/>)"]
    COMMIT --> PATH{"get_agent_path"}
    TOOLREG --> PATH
    PATH -->|"session present"| PERSESS[("agent_{tenant}_session_{id}.mv2<br/>— a new session opens a new file<br/>and starts empty")]
    PATH -->|"session absent"| ANON[("agent_{tenant}_session_anon.mv2<br/>— every session-less turn for this<br/>tenant pools here; the only case<br/>where the description holds")]
    PERSESS & ANON --> MV["Memvid does the storing and the search"]
    COMMIT -.->|"on error: tracing::error! and continue —<br/>a memory write cannot fail the turn"| DONE
    NOTE["no delete, no supersede, no dedup:<br/>a fact said ten times is ten frames"] -.-> MV
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `src/swarm_engine/overseer.rs` | The orchestration loop, and both memory call sites |
| `src/memory/memvid_manager.rs` | Eighty-eight lines: path, create-or-open, commit |
| `src/memory/tool.rs` | Fifty-eight lines: the agent-facing search tool |
| `src/rl_*.rs` | Governance voting, audit trail, safe deployment, self-eval |
| `src/retrieval`, `src/agents.rs` | Retrieval and the agent registry |
| `dashboard/`, `k8s-manifest.yaml` | A UI and a deployment manifest |

## 4. Essential Implementation Paths

`src/memory/memvid_manager.rs:19-21` — the whole scoping decision, in three
lines.

`src/swarm_engine/overseer.rs:308-316`, `:905-912` — the two call sites, and the
fallback they share.

`src/memory/tool.rs:32-40` — what the model is told the tool does.

## 5. Memory Data Model

A frame is `format!("User Query: {}\nAgent Response: {}", query, final_answer)`
with a title carrying the session id and an RFC 3339 timestamp. No structure
beyond that: no speaker separation once stored, no facts extracted, no
provenance, no importance, no state.

## 6. Retrieval Mechanics

One tool, one query string, and Memvid's own search behind it. The runtime adds
no ranking, filtering or budgeting of its own.

## 7. Write Mechanics

One append per completed turn, best-effort. Errors are logged and dropped, which
is the right priority ordering for a user-facing turn and means nothing counts
the frames that were lost.

## 8. Agent Integration

The tool is registered on the agent builder alongside the others, with a
`bypass_tools` path that calls the memory search directly rather than letting the
model choose it. That second path is worth noting: it is how the runtime
guarantees a memory lookup happens even when the model would not have asked for
one.

## 9. Reliability, Safety, and Trust

The memory layer carries none of its own. The runtime's guardrails, RL audit
trail and governance voting are separate subsystems, not read here, and none of
them touch the memory path.

## 10. Tests, Evals, and Benchmarks

121 test functions across the Rust tree, plus shell and Python test scripts at
the top level. No test was found covering the memory wrapper. Nothing was built
or run for this reading.

## 11. For Your Own Build

Make the tool description match the key. "Your absolute long-term memory" over a
per-session file teaches a model to trust a recall that cannot span the
conversations it names — and the fix is either a word in the description or a
field out of the filename.

Do not let a missing identifier choose your scope. `unwrap_or("anon")` turns an
absent session into a shared bucket; whether that bucket is a leak or the only
working configuration depends on who else is in it.

Keep the write key and the read key in one place. This code gets it right by
constructing both from the same expression a few lines apart, which is the
cheapest version of that guarantee.

## 12. Open Questions

Whether `session_id` is ever `None` in practice. The fallback exists at both call
sites, and what supplies the id was not traced.

Whether the per-session scoping is intended. Nothing in the tree explains the
choice, and the tool description argues against it.

What the `.backup` files were. Both sit beside their originals in `src/`.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `src/memory/memvid_manager.rs:19-21` | The scoping decision, entire |
| `src/memory/tool.rs:32-40` | The promise made to the model |
| `src/swarm_engine/overseer.rs:308-316`, `:905-912` | Read key and write key, agreeing |

## History

**2026-09-16** — [`936957b350091997c34380ffdd91b395d47225ae`](https://github.com/MegaWiz-Dev-Team/Bifrost/commit/936957b350091997c34380ffdd91b395d47225ae) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: seven files scanned, no auto-run surfaces, no build-time execution points, one unpinned surface and five dependency files inside the seven-day cooldown. Nothing was installed, built or run.

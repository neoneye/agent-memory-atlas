---
title: MateClaw
eyebrow: Scoped provider SPI
description: A memory service-provider interface whose contract carries an owner key on every call, with retry and metrics handled by provider decorators instead of per-backend code.
root: ../..
page_kind: system
source_name: mateaix/mateclaw
source_url: https://github.com/mateaix/mateclaw
revision: 3643aed7564390f57906954286a443d5913b97a7
revision_url: https://github.com/mateaix/mateclaw/commit/3643aed7564390f57906954286a443d5913b97a7
analyzed_at: 2026-07-27
capabilities: "scope_enforced"
matrix:
  memory_unit: "Fact, recall record, workspace file, and dream report"
  storage: "Relational repositories with fact projections"
  retrieval: "Provider `prefetch`, fact projection, and search package"
  write: "Turn lifecycle events drive `syncTurn` across registered providers"
  update_delete: "Contradiction detection over facts; archive package; no tombstone found"
  scoping: "`MemoryScope` string column with TEAM and GLOBAL shared; `MemoryOwnerResolver`"
  integration: "`MemoryProvider` SPI with decorators; tool beans; Vue memory UI"
  background: "Scheduler, dream reports, nudge service"
  trust: "Contradiction detector; owner key carried through the provider contract"
  strengths: "A provider contract that carries scope, and retry/metrics as decorators"
  risks: "No deletion hook on the SPI; contradiction handling is detection only"
---

## 1. Executive Summary

MateClaw's memory subsystem is about 12,900 lines under `vip/mate/memory/`, plus a memory UI and externalized memory prompts, and it is worth reading because it was built in a different engineering tradition from everything else here: enterprise-framework conventions — dependency injection, a service-provider interface, event listeners, auto-configuration — applied to agent memory.

That tradition shows in the package layout — `archive`, `controller`, `event`, `fact`, `identity`, `lifecycle`, `listener`, `model`, `nudge`, `provider`, `repository`, `scheduler`, `search`, `service`, `spi`, `tool`, with a `MemoryAutoConfiguration` — and in two design choices the atlas has not seen before.

**The provider contract carries an owner key.** `MemoryProvider` declares `prefetch(agentId, userQuery)` *and* `prefetch(agentId, userQuery, ownerKey)`, `syncTurn(...)` with and without `ownerKey`. This matters because the [pluggable memory provider](../../patterns/pluggable-memory-provider/) pattern was written from three host runtimes — [Hermes Agent](../hermes-agent/), [OpenClaw](../openclaw/), and [Pi](../pi/) — whose contracts carry **no scope parameter at all**. MateClaw shows the alternative, and confirms the gap in the others was a choice rather than an inevitability.

**Cross-cutting concerns are decorators, not per-provider code.** `spi/decorator/` holds `MemoryProviderDecorator`, `MetricsMemoryProvider`, and `RetryableMemoryProvider`. Any provider wrapped in these gets metrics and retry for free. In Hermes and OpenClaw, every plugin implements its own resilience — or does not, which is why [Magic Context](../magic-context/) had to build fail-closed registration itself and [LobsterAI](https://github.com/netease-youdao/LobsterAI) had to patch OpenClaw for a rename race. Decorating the interface solves that once for all providers.

The rest is competent and recognizable: turn lifecycle events (`TurnStartedEvent`, `TurnCompletedEvent`, `TurnContext`) mediated through a `MemoryLifecycleMediator`, a `ContradictionDetector` over extracted facts, a `MemoryScope` with team and global sharing, dream reports for consolidation, and a `MemoryNudgeService`.

The main reservations: the SPI still has **no deletion hook**, so MateClaw closes half the provider gap and leaves the other half open; and contradiction handling appears to be detection without a resolution workflow.

## 2. Mental Model

```java
public interface MemoryProvider {
    String id();
    default String systemPromptBlock(Long agentId);
    default String prefetch(Long agentId, String userQuery);
    default String prefetch(Long agentId, String userQuery, String ownerKey);   // scoped
    default void   syncTurn(Long agentId, String conversationId,
                            String userMessage, String assistantReply);
    default void   syncTurn(Long agentId, String conversationId,
                            String userMessage, String assistantReply,
                            String ownerKey);                                    // scoped
    default List<Object> getToolBeans();
    default void   onSessionEnd(Long agentId, String conversationId);
}
```

Everything but `id()` is a default method, so a provider implements only what it supports — capability negotiation by language feature rather than by a `capabilities()` call.

Scope is a string column with a documented rationale:

```java
/** Visibility scope for a memory row (workspace file, fact, recall).
 *  ... persona files (AGENTS.md, SOUL.md, PROFILE.md) and legacy rows live ...
 *  Stored as a plain string column (scope) rather than a DB enum so ... */
public static boolean isShared(String scope) {
    return TEAM.equals(scope) || GLOBAL.equals(scope);
}
```

`TEAM` and `GLOBAL` are the shared scopes; a `MemoryOwnerResolver` maps requests to owners.

Turn lifecycle:

```text
TurnStartedEvent → MemoryLifecycleMediator → providers.prefetch(..., ownerKey)
                                            → TurnContext assembled
TurnCompletedEvent → providers.syncTurn(..., ownerKey)
session end        → providers.onSessionEnd(...)
scheduler          → dream reports, nudges
```

## 3. Architecture

`mateclaw-server/src/main/java/vip/mate/memory/`:

- `spi/` — `MemoryProvider`, `MemoryManager`, `AbstractExternalProvider`, and `decorator/` (`MemoryProviderDecorator`, `MetricsMemoryProvider`, `RetryableMemoryProvider`).
- `lifecycle/` — `MemoryLifecycleMediator`, `MemoryLifecycleEventListener`, `TurnStartedEvent`, `TurnCompletedEvent`, `TurnContext`.
- `fact/` — `extraction`, `contradiction` (`ContradictionDetector`), `projection`, `provider`, `model`, `controller`.
- `identity/` — `MemoryScope`, `MemoryOwnerResolver`.
- `model/` — `MemoryRecallEntity`, `DreamReportEntity`, `MorningCardSeenEntity`.
- `archive/`, `search/`, `repository/`, `service/`, `scheduler/`, `nudge/`, `tool/`, `event/`, `listener/`, `controller/`, `MemoryAutoConfiguration`, `MemoryProperties`.
- `mateclaw-ui/src/views/Memory/` and `stores/useMemoryStore.ts` — the review UI.
- `mateclaw-server/src/main/resources/prompts/memory/` — externalized prompts.

```mermaid
flowchart LR
  Turn["TurnStartedEvent"] --> Med["MemoryLifecycleMediator"]
  Med --> Mgr["MemoryManager"]
  Mgr --> Dec["decorators: Metrics, Retryable"]
  Dec --> P1["provider A"]
  Dec --> P2["provider B (AbstractExternalProvider)"]
  P1 --> Ctx["TurnContext"]
  P2 --> Ctx
  Done["TurnCompletedEvent"] --> Mgr
  Mgr --> Facts["fact/extraction"]
  Facts --> Contra["ContradictionDetector"]
  Facts --> Proj["fact/projection"]
  Sched["scheduler"] --> Dream["DreamReportEntity"]
  Sched --> Nudge["MemoryNudgeService"]
  Proj --> UI["Vue Memory views"]
```

## 4. Essential Implementation Paths

### A provider contract that carries scope

The paired overloads — one with `ownerKey`, one without — are a pragmatic migration shape: existing providers keep working on the unscoped signature while scope-aware ones opt in. It is less rigorous than requiring scope on every call (the discipline [OpenClaw](../openclaw/) enforces inside its store with `scopedPredicate`), because a provider can still be invoked unscoped. But it is far more than the three host runtimes previously reviewed offer, where scope cannot be expressed at all.

The atlas's pattern page argues a workable contract needs scope on every call, a deletion hook, and capability reporting. MateClaw supplies scope (optionally), supplies capability reporting implicitly through default methods, and supplies no deletion path — one and a half of three.

### Decorators for resilience and observability

`MetricsMemoryProvider` and `RetryableMemoryProvider` wrap any `MemoryProvider`, so a flaky external backend gets retried and every backend gets instrumented without touching provider code. `AbstractExternalProvider` presumably supplies the common shape for remote backends.

This is the clearest answer in the atlas to a question the pluggable-provider pattern raises and does not resolve: when a mounted provider fails or is slow, whose problem is it? Here it is the host's, solved once, in the decorator chain.

### Turn lifecycle as events

Rather than the host calling providers directly, `TurnStartedEvent` and `TurnCompletedEvent` flow through a mediator and listener. `TurnContext` carries the assembled state. This is Spring-idiomatic and has a real benefit: additional memory concerns can subscribe to turn events without modifying the call path — the `nudge` service and scheduler plug in the same way.

### Contradiction detection

`fact/contradiction/ContradictionDetector.java` is a dedicated component, which few systems here have at all. What was not found is what happens next: no resolution workflow, review queue, or supersession path surfaced alongside it. That mirrors [Gini](../gini-agent/), which models a `conflicted` status without a visible way to act on it — detection is necessary and, on its own, incomplete.

### Dream reports and nudges

`DreamReportEntity` puts MateClaw in the group of systems that call consolidation dreaming, and `MorningCardSeenEntity` alongside `MemoryNudgeService` suggests memory is surfaced proactively — a morning summary the user can be shown, tracked so it is not repeated. Proactive memory delivery is rare in the atlas, where recall is almost always query-driven.

## 5. Memory Data Model

Relational, through Spring repositories, with fact extraction feeding projections and a separate `archive` package. `MemoryScope` is deliberately a string rather than a database enum — the comment explains this is so the value set can evolve without a schema migration, which is a sensible tradeoff at the cost of database-level validation.

Gaps:

- **No tombstone** was found; the `archive` package suggests retention rather than negative memory.
- **Contradiction is detected, not resolved.**
- **No verification state** on facts surfaced in what was read.
- **The SPI has no deletion hook**, so a user's erasure request has no defined route into a mounted provider.

## 6. Retrieval Mechanics

Provider `prefetch` plus a dedicated `search` package and fact projections. Ranking specifics were not traced. The projection layer is worth noting on its own: separating stored facts from the projections used for display and recall is the [treat semantic indexes as projections](../basic-memory/) discipline expressed in a relational idiom.

## 7. Write Mechanics

`syncTurn` after each completed turn, dispatched to every registered provider through the manager and its decorators, with fact extraction and contradiction detection downstream. Because writes flow through the lifecycle mediator rather than direct calls, the write path is observable in one place — the same chokepoint benefit [RainBox](../rainbox/) gets from `record_belief`, though without the trust policy.

## 8. Agent Integration

`getToolBeans()` lets a provider contribute Spring-managed tool beans to the agent, which is an elegant use of the container: memory tools are registered by the provider that implements them rather than declared centrally. The Vue UI under `views/Memory/` with `useMemoryStore.ts` gives operators a review surface, and prompts live in `resources/prompts/memory/` where they can be edited without recompiling.

## 9. Reliability, Safety, and Trust

Strengths:

- **Scope on the provider contract**, closing half the gap the atlas documents in three other host runtimes.
- **Retry and metrics as decorators**, so resilience is solved once for every backend.
- **Default methods** for implicit capability negotiation.
- **Event-driven turn lifecycle** with a single mediator.
- **A dedicated contradiction detector.**
- **Provider-contributed tool beans.**
- **Externalized prompts** and an operator UI.
- **Scope stored as a string** with a documented rationale.

Gaps:

- **No deletion hook on the SPI.**
- **Contradiction detection without resolution.**
- **Unscoped overloads remain callable**, so scope is opt-in per call site.
- **No tombstone or verification state** found.

## 10. Tests, Evals, and Benchmarks

Tests exist under `src/test/java/vip/mate/memory/`, including an `archive` package. Nothing was run for this review, and no memory-quality benchmark was found.

The measurement this design invites is provider-level: with metrics already decorating every provider, per-provider recall quality and latency are collectable, and comparing two mounted backends on the same traffic would be straightforward. Nothing indicates that has been done.

## 11. For Your Own Build

### Steal

- **Put scope on the provider contract.** Paired overloads are a pragmatic way to add it to an existing interface without breaking implementations.
- **Decorate the provider interface** for retry, metrics, and any other cross-cutting concern, so every backend inherits them.
- **Default methods as capability negotiation** — a provider implements what it supports, and the host does not need a `capabilities()` call to find out.
- **Drive memory from turn lifecycle events** so new concerns subscribe rather than modify.
- **Let providers contribute tool beans**, keeping a memory backend's tools with the backend.
- **Externalize memory prompts** to resources.
- **Track what has been proactively shown** (`MorningCardSeenEntity`) so a nudge is not repeated.

### Avoid

- **A provider contract with scope but no deletion** — half a governance story.
- **Optional scope**, since an unscoped overload will eventually be called.
- **Contradiction detection with no resolution path.**
- **String scope without database validation.**

### Fit

Borrow:

- The SPI shape, especially the scoped overloads and default methods.
- The decorator chain for metrics and retry.
- Turn lifecycle events as the memory trigger.

Do not copy:

- The contract as complete; add `forget(scope|id)` before third parties mount backends.
- Detection without resolution.

## 12. Open Questions

- How does a deletion request reach a mounted provider? Nothing on the SPI expresses it.
- What resolves a detected contradiction?
- Are unscoped `prefetch`/`syncTurn` calls still in use, and is there a plan to retire them?
- What does the nudge service decide to surface, and on what signal?
- Do the decorators cover failure isolation as well as retry — can one slow provider stall a turn?

## Appendix: File Index

- Provider contract: `mateclaw-server/src/main/java/vip/mate/memory/spi/MemoryProvider.java`, `MemoryManager.java`, `AbstractExternalProvider.java`.
- Decorators: `spi/decorator/MemoryProviderDecorator.java`, `MetricsMemoryProvider.java`, `RetryableMemoryProvider.java`.
- Lifecycle: `lifecycle/MemoryLifecycleMediator.java`, `MemoryLifecycleEventListener.java`, `TurnStartedEvent.java`, `TurnCompletedEvent.java`, `TurnContext.java`.
- Facts: `fact/extraction/`, `fact/contradiction/ContradictionDetector.java`, `fact/projection/`, `fact/provider/`.
- Identity and scope: `identity/MemoryScope.java`, `identity/MemoryOwnerResolver.java`.
- Entities: `model/MemoryRecallEntity.java`, `DreamReportEntity.java`, `MorningCardSeenEntity.java`.
- Operations: `scheduler/`, `nudge/MemoryNudgeService.java`, `archive/`, `search/`, `repository/`.
- Configuration: `MemoryAutoConfiguration.java`, `MemoryProperties.java`.
- UI and prompts: `mateclaw-ui/src/views/Memory/`, `stores/useMemoryStore.ts`, `mateclaw-server/src/main/resources/prompts/memory/`.
- Tests: `mateclaw-server/src/test/java/vip/mate/memory/`.

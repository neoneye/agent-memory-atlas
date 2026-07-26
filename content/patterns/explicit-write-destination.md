---
title: Explicit Write Destination
eyebrow: Pattern · Federation
description: Let reads fan out across allowed memory stores while requiring every mutation to name one concrete private or shared destination.
root: ../..
page_kind: pattern
---

## Intent

Support layered memory—personal, project, repository, team, or organization—without letting a broad read context silently determine where new information is written.

## The problem

Federated retrieval may merge several stores into one result list. If a subsequent “remember this” operation inherits that blended context, a private observation can leak into a shared repository or a team lesson can land in one developer’s private memory.

## The pattern

Separate read scope from write target:

```text
read_scopes = [private, project, organization]
write_target = project
```

Reads may fan out according to access policy and merge with locality or precedence rules. Writes accept exactly one resolved destination and reject ambiguous requests. The destination becomes part of identity, provenance, access control, and the mutation audit.

Agent tools should make the target visible in their arguments. Defaults are acceptable only when they are safe, obvious, and surfaced to the user; shared writes often deserve confirmation.

## Why it works

The pattern prevents accidental publication and makes ownership inspectable. It also allows independent storage, sync, retention, and review policy for each layer.

## Tradeoffs

Explicit targets add friction. Agents may choose poorly, and users may not understand the scope names. A promotion flow is needed when a private insight becomes shared knowledge. Moving a memory between stores must preserve provenance without leaving stale copies or broken links.

Do not infer a write target from the top search result. Relevance and ownership are different decisions.

## Seen in the atlas

[llm-wiki-memory](../../systems/llm-wiki-memory/) provides the clearest implementation: reads federate across a private brain and repository-owned wikis, while mutations require an explicit target. Its repository scopes also avoid silently auto-committing shared changes. [RainBox](../../systems/rainbox/) and [Verel](../../systems/verel/) reinforce the broader principle through explicit claim scopes and scoped policy.

## Implementation checklist

- Give every store a stable, human-readable destination ID.
- Resolve and authorize the target before mutation.
- Include target scope in dedupe, conflict, and tombstone checks.
- Record promotions and moves as relations or audit events.
- Require stronger confirmation for shared or organization-wide writes.
- Keep private automatic capture separate from shared publication.

## Tests to require

- Omitted and ambiguous write targets fail safely.
- Private capture never appears in shared stores.
- Read federation does not affect write routing.
- Promotion preserves provenance and removes or links the predecessor.
- Concurrent moves cannot create two active owners.
- Shared targets enforce authorization independently of the agent tool.

## Related patterns

- [Scope as a first-class key](../scope-as-a-first-class-key/)
- [Governed write gateway](../governed-write-gateway/)
- [Append-only memory audit](../append-only-memory-audit/)

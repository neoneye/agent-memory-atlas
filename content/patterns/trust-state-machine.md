---
title: Trust-State Machine
eyebrow: Pattern · Trust
description: Model memory as candidate, verified, rejected, or stale instead of placing every extracted fact in one truth bucket.
root: ../..
page_kind: pattern
---

## Intent

Represent the epistemic status of a memory explicitly and make promotion, rejection, correction, retrieval, and pruning depend on that status.

## The problem

An LLM-generated fact, a user assertion, a document sentence, and a corroborated observation do not deserve the same authority. A single active/inactive flag hides that difference. Confidence scores alone are also ambiguous: they often mix truth, retrieval relevance, and model certainty.

## The pattern

Start with a small state machine:

```mermaid
stateDiagram-v2
    [*] --> Candidate
    Candidate --> Verified: trusted source or corroboration
    Candidate --> Rejected: review or contradiction
    Verified --> Stale: age or superseding evidence
    Verified --> Rejected: correction
    Stale --> Verified: revalidation
    Rejected --> Candidate: explicit reactivation
```

Keep separate dimensions for:

- **Trust state:** whether the memory may be treated as established.
- **Epistemic confidence:** how strongly the evidence supports it.
- **Retrieval strength:** how useful or reachable it has been.

Retrieval policy can then prefer verified memory, include candidates with visible uncertainty when necessary, and suppress rejected records from ordinary context.

## Why it works

The state machine gives every transition a policy boundary. It creates places to require corroboration, human review, held-out evals, or privileged actors. It also makes correction and audit language precise: a memory was rejected, not merely assigned a lower similarity score.

## Tradeoffs

More states create more transitions, UI, and operational policy. A candidate queue can grow forever. Verification can become theater if the verifier repeats the same model or source. Stale is temporal uncertainty, not proof of falsity. Promotion rules must be explainable and scoped to the consequences of being wrong.

For low-risk note retrieval, a full trust machine may be excessive. It matters most when memory changes decisions, identity, permissions, or long-lived behavior.

## Seen in the atlas

[Verel](../../systems/verel/) is the clearest reference: candidate, verified, and rejected states participate in recall, promotion, consolidation, and pruning. It also separates epistemic confidence from retrieval strength. [RainBox](../../systems/rainbox/) distinguishes human/override writes from model-originated candidates and couples trust with operator review. Other systems often expose CRUD without an equivalent promotion boundary.

[Cognee](../../systems/cognee/) has rich provenance and ontology validity but no equivalent factual promotion state. [Claude-Mem](../../systems/claude-mem/) activates generated observations in project context, and [A-MEM](../../systems/a-mem/) can rewrite neighboring metadata, without candidate or rejected states. These are useful reminders that provenance, schema validity, and LLM confidence do not replace trust transitions.

## Tests to require

- Prove candidates cannot enter verified-only context.
- Exercise every allowed and forbidden state transition.
- Verify rejected records do not return through normal recall.
- Test that retrieval feedback changes usefulness signals, not truth automatically.
- Verify stale records can be revalidated without losing history.
- Test actor permissions for promotion, rejection, and override.

## Related patterns

- [Rejected-value tombstone](../rejected-value-tombstone/)
- [Evidence before belief](../evidence-before-belief/)
- [Governed write gateway](../governed-write-gateway/)
- [Decay and reinforcement](../decay-and-reinforcement/)

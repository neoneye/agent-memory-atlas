# The build brief and the lock file

Two artifacts, one purpose: make a memory design **reviewable before it is
code**, and reviewable again when the atlas moves.

Reviewing twelve decisions is cheaper than reviewing two thousand generated
lines. That is the whole argument.

## The rule that makes this worth doing

A brief that lists patterns is a checklist, and the pattern library says in its
own first sentence that it is not one. **Every line carries a reason, and the
`defer` and `reject` reasons are the ones that matter** — they are the record
that a judgement happened. A brief whose `defer` list is empty was not written by
someone who read the failure modes.

## Producing one

1. **Read the target repository first.** Single-user or multi-tenant; passive
   assistant or an agent that acts; what becomes memory (messages, files, tool
   results, facts, procedures); what breaks if a memory is wrong; what
   correction and deletion the product owes its users; the privacy boundary; the
   database already in the stack. Infer what you can from the code. Ask the
   developer only where two readings lead to materially different designs.
2. **Pick a profile row** from *Stacks, by what you are building* in
   `content/patterns/index.md`. It names the failure that actually hurts for that
   shape, and the *What you can defer* paragraph under it is what keeps the build
   small. The profile is a starting point, not a verdict.
3. **Start from the failure, not the mechanism.** The *How to use the library*
   list on the same page maps failure → pattern. Adopt the smallest set that
   closes a failure this product can actually suffer.
4. **Write the brief. Stop. Get it approved.** This is the checkpoint. Nothing is
   implemented before a person has read twelve lines.

## Schema

```yaml
atlas_commit: 4a328bb                 # what was read, so a later review can diff it
product_profile: personal-assistant   # a row from the stacks table, or 'none — reason'

adopt:
  - pattern: scope-as-a-first-class-key
    because: notes are per-project and a leak across projects is the failure the user would notice first
  - pattern: evidence-before-belief
    because: extraction is automatic, so a wrong fact must be repairable from its source

defer:
  - pattern: bi-temporal-fact-validity
    because: no question in this product asks what was true last month; revisit if reporting is added
  - pattern: decay-and-reinforcement
    because: improves a memory that already works, and nothing here is yet working

reject:
  - pattern: rejected-value-tombstone
    because: >
      every write is a deliberate human action and no extractor can re-assert a
      value, so the failure this closes cannot occur here. Revisit the day
      automatic capture is added — that is the day this becomes load-bearing.

invariants:                            # what must stay true, in the product's own words
  - every read carries project_id
  - every derived memory references surviving evidence
  - no model-generated content becomes verified without a human action
  - deleting evidence removes or invalidates every projection of it

borrowed:                              # mechanisms taken from a specific system, pinned
  - system: claude-mem
    commit: <the commit the report pins>
    mechanism: durable hook queue, committed before the semantic projection
  - system: verel
    commit: <the commit the report pins>
    mechanism: epistemic confidence kept separate from retrieval strength

required_tests:                        # ids from .agents/protocol/tests.yaml
  - scope.cross_tenant_absent
  - evidence.claim_resolves_to_source
  - evidence.source_delete_reaches_derived
  - retrieval.k_is_an_upper_bound
  - prompt.recall_is_data_not_instruction

known_exceptions:                      # what is knowingly not closed, and why
  - deletion does not reach the vector index until compaction; accepted because the
    store is single-user and local, revisit before any hosted deployment
```

## The closure report

After implementation, produce the same table for what was built. **It is not a
conformance report and must not be titled one** — the atlas certifies nothing,
has run its own deletion sequence against no system, and declined the compliance
framing once already for that reason. What it reports is which failure modes are
closed and which are not:

| Pattern | Where it lives | Test | Result |
| --- | --- | --- | --- |
| Scope | `memory/store.py` | `scope.cross_tenant_absent` | closed |
| Evidence before belief | `events`, `memory_evidence` | `evidence.claim_resolves_to_source` | closed |
| Deletion propagation | primary store only | `deletion.absent_after_reindex_and_restart` | **open** — vector index not reached |

An **open** row is a result, not a failure of the exercise. A report with no open
rows in a system that has a vector index is the one to disbelieve.

## The lock file

Write `memory-atlas.lock` into the *target* repository — the brief plus the atlas
commit it was decided against:

```yaml
atlas_commit: 4a328bb
atlas_url: https://github.com/neoneye/agent-memory-atlas
product_profile: personal-assistant
adopted: [scope-as-a-first-class-key, evidence-before-belief, explicit-write-destination]
deferred: [bi-temporal-fact-validity, decay-and-reinforcement]
rejected: [rejected-value-tombstone]
borrowed: [claude-mem@<commit>, verel@<commit>]
required_tests: [scope.cross_tenant_absent, evidence.claim_resolves_to_source]
known_exceptions: [deletion does not reach the vector index until compaction]
```

Its only job is to make the next review **small**: when the atlas moves, diff
`atlas_commit` against HEAD and read only what touches an adopted, deferred or
borrowed line. Without it, every atlas update invites a redesign, which is how a
reference gets abandoned.

Two honest limits. The lock file records a decision, not a guarantee — nothing
verifies that the code still matches it. And a deferred pattern is the thing most
likely to become wrong silently, because the reason for deferring it was a fact
about the product, and products change.

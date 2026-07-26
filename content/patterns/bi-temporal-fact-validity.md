---
title: Bi-Temporal Fact Validity
eyebrow: Pattern · Time
description: Track when a fact was true separately from when the memory system learned, changed, or expired it.
root: ../..
page_kind: pattern
---

## Intent

Represent changing facts and backfilled history without overwriting the past or confusing event time with ingestion time.

## The problem

A memory system usually has at least two clocks:

- the time an event happened or a fact was true;
- the time the system received, stored, corrected, or deleted that information.

Collapsing them into one timestamp breaks questions such as “Where did Alice work last year?” A backfilled event appears new, and a corrected fact may erase the state that was valid earlier.

## The pattern

Give facts an application-time interval and a system-time lifecycle:

```text
fact
  valid_at    ───────────── invalid_at
  created_at  ───────────── expired_at
```

When a new fact supersedes an old one:

1. Keep the source event for both facts.
2. Set the new fact's real-world `valid_at`.
3. Close the old fact's `invalid_at` at the appropriate event boundary.
4. Record when the system made that change through `created_at`/`expired_at`.
5. Query against the clock appropriate to the question.

Do not silently hard-delete the older edge merely because it is no longer current.

## Why it works

The graph can answer current-state and historical questions from the same records. Backfilled information stays ordered by event time even though it was ingested later. Corrections become inspectable state transitions rather than destructive rewrites.

## Tradeoffs

- Date extraction may be uncertain or absent.
- Overlapping intervals need explicit policy.
- Entity resolution mistakes can invalidate the wrong fact.
- Queries and indexes become more complex.
- “Unknown end date” must remain different from “still true”.
- System-time retention may conflict with privacy deletion requirements.

Temporal precision is not truth. Store the evidence and confidence behind inferred dates.

## Seen in the atlas

[Graphiti](../../systems/graphiti/) is the clearest implementation. Episodes carry a reference time; entity edges carry `valid_at`, `invalid_at`, `created_at`, and `expired_at`; contradiction handling closes older intervals while source episode UUIDs preserve evidence. Saga summaries keep separate wall-clock and episode-time watermarks so backfilled episodes remain processable.

[Hindsight](../../systems/hindsight/) provides a complementary fact-store implementation with event dates, occurrence ranges, mentioned-at time, and a dedicated temporal retrieval arm. It demonstrates that the pattern is useful outside a graph, although Graphiti has the stronger interval-correction model.

## Tests to require

- Backfilled old events ingested today.
- A current fact replacing a formerly true fact.
- Overlapping, missing, and timezone-naive intervals.
- Contradictions whose source events arrive out of order.
- Historical queries versus current-state queries.
- Entity deduplication followed by temporal correction.
- Exact deletion of source evidence and all unsupported derived facts.

## Related patterns

- [Evidence before belief](../evidence-before-belief/)
- [Append-only memory audit](../append-only-memory-audit/)
- [Trust-state machine](../trust-state-machine/)
- [Hybrid retrieval fusion](../hybrid-retrieval-fusion/)

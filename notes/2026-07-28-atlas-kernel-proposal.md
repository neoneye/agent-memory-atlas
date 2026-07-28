# Atlas kernel — a reference implementation of the minimum serious stack

**Status:** proposed, not started
**Origin:** independently suggested by two reviewers (Kimi, Qwen) on 2026-07-28,
both framed as "implement all 17 patterns". Modified below, because that framing
contradicts what the atlas argues.

## The idea

Build the smallest working memory system that demonstrates the four patterns the
[pattern index](../content/patterns/index.md) names as the minimum serious stack,
and ship it as a readable artifact rather than a product.

## Why not "all 17 patterns"

Both reviewers proposed a kernel implementing the full pattern library. The
atlas argues the opposite in its own words — "Add the smallest set that closes a
demonstrated failure mode" — and the composition section names four patterns as
the minimum and explicitly marks the rest deferrable. A kernel implementing all
seventeen would contradict the guidance it exists to demonstrate, and would model
exactly the over-building the library warns against.

## Scope

Four patterns, in dependency order, because each exists to make the next
enforceable:

1. **Scope as a first-class key** — scope leads the primary key and every index;
   the embedding cache key is `hash(scope, model, body)`.
2. **Evidence before belief** — raw events retained; derived claims rebuildable
   from them.
3. **Governed write gateway** — one transactional mutation path, with enforcement
   that it cannot be bypassed.
4. **Rejected-value tombstone** — keyed on the normalized value, checked by every
   write path including background ones.

Explicitly **out**: retrieval quality, hybrid fusion, decay, bi-temporal
validity, consolidation. The kernel should be embarrassingly bad at retrieval and
correct about correction — that is the point, and making it clear prevents the
artifact being read as a recommendation to use it.

## The paired demonstration

The more valuable half, and the part that makes it evidence rather than
assertion. Ship two configurations:

- **kernel** — all four patterns.
- **kernel-without-tombstone** — identical, one mechanism removed.

Plus a ~30-line script that runs the same sequence against both: write a fact,
delete it, re-feed the original source, run the background pass, query. The first
stays deleted; the second resurrects it. That proves the failure mode this atlas
has found in 54 of 56 systems, **without accusing any named system of a failure
that was never run**.

Same shape for the other three: remove scope and show the cross-project leak;
remove the gateway and show a bypassing write path skipping the tombstone check;
discard evidence and show a bad extraction becoming unrepairable.

## Cost and risks

- **Effort:** the kernel is small — a few hundred lines is the target, and if it
  needs more than that the scope has crept. The demonstration scripts are
  smaller. The expensive part is resisting features.
- **The author-as-vendor problem doubles.** The atlas already contains RainBox as
  a self-assessment; a kernel makes two entries by the same author. If it is
  added to the atlas it needs the same explicit self-assessment framing and the
  same capability marks, honestly assigned — including dashes for everything it
  deliberately omits.
- **Risk of becoming a product.** The moment it gains a retrieval story, people
  will use it, and the atlas becomes a vendor of the thing it reviews. A stated
  non-goal in the README ("this is a demonstration; do not deploy it") is
  necessary and probably insufficient.

## First step

Write the failing script first, against nothing. Decide the exact assertion
sequence that distinguishes a store with a tombstone from one without, then build
the smallest thing that passes it.

## Open decisions

- Does the kernel enter the atlas as system #57, or sit outside it as a teaching
  artifact?
- One language, or a schema plus a reference implementation others can port?
- Does it reuse the deletion harness from
  [the eval suite note](2026-07-28-executable-eval-suite.md), or is that harness
  built against the kernel first and generalized after?

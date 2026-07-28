# Pattern cookbook — a copy-pasteable artifact per pattern

**Status:** partially done
**Origin:** Gemini, 2026-07-28 ("show the code, 20 lines, so developers can steal
your architecture").

## Where it stands

Three patterns now carry a concrete artifact:

- **scope-as-a-first-class-key** — SQL showing scope leading the primary key and
  every index, plus the `hash(scope, model, body)` embedding cache key.
- **source-diverse-context** — the two-pass selector in full.
- **gate-the-expensive-path** — the fail-open branch.

The [benchmarks page](../content/benchmarks.md) carries the deletion harness.
Every other pattern has a diagram and prose, and nothing to copy.

## What to add

One minimal artifact per remaining pattern — a schema, a function signature, or
an algorithm. Not a library, not a framework: the smallest correct thing that
shows the shape.

Priority order, by how often the pattern is misunderstood rather than by how
important it is:

1. **rejected-value tombstone** — the highest-value and the easiest to get subtly
   wrong. Must show the normalized key, and must be honest that normalization is
   where the real work is: too strict and it never fires, too loose and it blocks
   legitimate updates.
2. **trust-state machine** — the states, the legal transitions, and the retrieval
   filter that makes them mean something. Without the filter the states are
   decoration, and that is the common failure.
3. **governed write gateway** — the enforcement, not the gateway. A private store
   or a type only the gateway can construct is the interesting part; a function
   everyone agrees to call is not a gateway.
4. **bi-temporal fact validity** — closing an interval rather than overwriting,
   and the as-of query.
5. **append-only memory audit** — the two event shapes, and the retention policy
   for the log itself.

## The trap

A 20-line tombstone is easy to write and easy to get wrong in a way that reads as
correct. Every snippet needs a stated list of what it does **not** handle, or the
cookbook ships confident-looking code with the hard parts elided — which is
precisely the failure the atlas documents in the systems it reviews.

## First step

Write the tombstone snippet, then write the paragraph listing what it does not
handle. If the paragraph is longer than the snippet, that is the honest ratio and
it should ship that way.

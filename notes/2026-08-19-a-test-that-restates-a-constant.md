# A test that restates a constant cannot detect a wrong constant

**Status:** transferable engineering lesson, one instance, worth quoting at
people.
**Origin:** memoir-cli's backup retention, where the bug and its test agreed
with each other.

## The bug

`cleanupOldBackups` deletes every backup past a cap. The cap came from two
constants:

```js
export const MAX_BACKUPS_FREE = 100;
export const MAX_BACKUPS_PRO  = 50;
```

A paying account retained half as much history as a free one, on a destructive
path. The atlas reported it as a finding and could not tell from the code
whether it was a typo or a deliberate tier design, so the report said so and
listed it as an open question.

## Why the test did not catch it

There *was* a unit test covering retention. It pinned the literal values —
asserting free was 100 and pro was 50 — so when the two were swapped the test
was updated along with them, and went on passing. The test agreed with the bug,
because the test and the bug were the same statement written twice.

That is the failure mode: **a test that restates a constant is a duplicate of
the constant, not a check on it.** It detects an accidental edit to one copy. It
cannot detect that the value is wrong, because it has no independent idea of
what right would mean.

## The fix, which is the part worth stealing

The constants are now 10 and 100, and the test asserts the *relationship*:

```js
assert(Number.isInteger(MAX_BACKUPS_FREE) && MAX_BACKUPS_FREE > 0, ...);
assert(MAX_BACKUPS_PRO > MAX_BACKUPS_FREE, `Pro retains MORE than free (...)`);
```

Nothing there says 10 or 100. The assertion is the property the constants exist
to satisfy — a paid tier retains more than a free one — and it survives every
future repricing while still failing the moment somebody swaps them again.

## The general form

For any constant whose value encodes a policy, ask what the policy is and assert
*that*:

- A retention cap: the paid tier retains more.
- A rate limit: the burst allowance is at least the sustained rate.
- A timeout: the client timeout exceeds the server's.
- A cache TTL: shorter than the credential lifetime it caches behind.
- A tombstone budget: large enough to outlive the slowest replica — which is
  the same repository's own spec, argued exactly this way and normatively, one
  file over.

The last one is the tell. memoir's SPEC already made a retention requirement
normative *as a relationship* ("MUST be large enough to outlive any stale
replica") for the merge tombstones, and pinned literals for the cloud backups.
The good pattern was in the building, one subsystem away from where it was
needed.

## For the atlas

This is a candidate check when reading any test suite: does an assertion restate
a value from the module it tests? That is not coverage, and a report crediting
it as coverage is crediting a mirror.

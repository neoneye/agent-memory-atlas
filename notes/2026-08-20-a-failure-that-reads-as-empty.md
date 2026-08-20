# A failure that reads as empty, and a write that follows it

**Status:** defect class, one clean instance, cheap to check for.
**Origin:** `loadMemories` in vercel-labs/fx, found by reading the function and
its only caller together.

## The shape

```
load()  → on ANY failure, return the empty value
save(x) → append x to load(), write the result
```

Each half is defensible. Returning empty on a missing file is right — a store
that has never been written to *is* empty. Appending to what you loaded is the
obvious way to write. Composed, they destroy data, and the failure is silent in
both directions: nothing is logged, and the caller returns success.

## The instance

fx keeps durable user preferences in `~/.fx/memories.json`, a JSON array of
strings. `loadMemories` returns an empty list when:

- the file does not exist,
- the file cannot be opened,
- the read fails, **including exceeding a 1 MiB cap**,
- the JSON does not parse,
- the root is not an array.

Five conditions, one value, no error path. `save` then appends the new fact to
that empty list and rewrites the file. A `memories.json` that has been
hand-edited into invalid JSON, truncated by an interrupted write, or grown past
the cap is replaced by a file containing exactly one memory — and the tool
returns `"remembered"`.

The detail that makes it reachable rather than theoretical: the tool's own error
message for a failed `clear` names the path and tells the user to check it. The
system invites the hand-edit that produces the unparseable file.

## Why this survives review

The suite is large — 8,286 test blocks — and the memory tool is tested: saving
the same fact twice yields one entry, `clear` is idempotent, `list` after
`clear` reports nothing, a missing `$HOME` produces a clear message. Those are
the right cases *for the happy path*, and none of them distinguishes the five
conditions that share an answer, because from the test's point of view they all
look like "the store is empty", which is a state the tests do exercise.

That is the general reason this class hides: **the corrupted case and the empty
case are indistinguishable to every test that does not deliberately corrupt the
store.** A suite can have excellent coverage of "no memories yet" and zero
coverage of "memories exist and cannot be read", and the two are one line apart.

## The check

For any store with a load-modify-write path, ask three questions in order:

1. Does `load` have a failure mode that returns the *same value* as "nothing
   stored"?
2. Does anything call `load` and then write the result back?
3. Is there a test that writes garbage to the store's path and asserts the prior
   contents survive?

If the answers are yes, yes, no, the store loses data silently and the suite
will not say so. The fix is a distinguishable failure — `Result`/`Option` at the
type level, or the same value plus an out-of-band error the caller must handle —
not a bigger cap.

## The one-line test that would have caught it

Write `{"oops":1}` to the path, call `save("x")`, assert the file still contains
what it contained before, or that `save` refused. It fails today.

## Related

This is a cousin of the [one-field-two-questions
note](2026-08-19-one-field-asked-two-questions.md) and not the same thing.
There, one *field* answered two questions and consumers could not tell which.
Here, an *error* is encoded as a legitimate value, and the damage comes from
what the caller does next. The unifying rule is the narrower one: a value that
means "I could not tell" must not be spelled the same way as a value that means
"the answer is nothing".

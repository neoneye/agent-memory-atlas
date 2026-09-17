# The test that cannot fail

**Written 2026-09-17.** Seven reports re-read in one pass, all at pins that were
still their upstream's current head. Nothing had moved, so nothing could be
blamed on drift — and six of the seven turned out to share a defect, plus three
of them a matching virtue. The defect is not that a mechanism is untested. It is
that **the mechanism has a test, and the test asserts something the code cannot
violate.**

A suite like that is worse than no suite, because the count goes up and the
question stops being asked.

## Five that cannot fail

**A-MEM.** `test_memory_evolution` adds three related notes and asserts
`assertIsNotNone` on each note's `tags`, `context` and `keywords`.
`MemoryNote.__init__` sets those three to `[]`, `"General"` and `[]`, so the
assertion holds on a note that was never evolved at all. What it would have
caught, had it asserted anything about evolution, is directly beneath it:
`find_related_memories` returns enumeration positions rather than the UUIDs it
just read, so the notes whose tags and context get rewritten are the *oldest in
the store* rather than the neighbours the model was shown. The code admits the
substitution in a comment — *"Since indices are just numbers now"*.

**Memvid.** `tests/mutation.rs::delete_frame_marks_deleted` creates one frame,
deletes it, reopens the file and asserts
`stats.frame_count == 0 || stats.frame_count == 1`, under a comment reading
*"Both are valid - the key is no panic occurred"*. After deleting the only frame
that holds for every implementation, including one where delete does nothing, and
the test never queries for the deleted content. The status filter that makes
deletion real — `frame.status == FrameStatus::Active`, in both search builders —
has no committed case anywhere.

**MetaClaw.** The garbage-collection test never calls `garbage_collect`. Under a
comment reading *"Simulate GC: remove superseded not referenced by active
units"*, it re-implements the routine's three steps inline and asserts against
its own copy — and it hand-builds the surviving row with
`supersedes=["gc-old-referenced"]`, which is exactly the forward reference no
production path except the merge ever writes. The case therefore passes on a
store the system cannot produce, and a change to the real routine would not fail
it. The defect underneath: five live `supersede()` call sites write only the
backward pointer, so every unit the consolidator supersedes is an orphan by the
collector's own definition and is hard-deleted, with no event logged.

**Gini Agent.** `status` is CHECK-constrained to
`proposed | active | archived | rejected | conflicted`, and the report credited
it as a trust model. A producer grep finds that three of the five are written by
nothing: the only production write of a non-default status in the whole runtime
is one statement archiving `observation` rows, and the generic setter that could
write any status has a single caller passing only usage fields. Nothing tests
this because there is nothing to test; the schema is the claim.

**LoongFlow.** The inverse arrangement, and instructive for it. The Boltzmann
selector is tested *well* — as a distribution, with repeated draws asserted to
favour higher scores and low temperature asserted to concentrate more than high.
The adaptive half is named in no test at all: a grep for `diversity` across
`tests/` returns nothing, because every case passes an explicit temperature. Two
defects sit in that unexercised pair. The comment says *"Sigmoid adjustment for
smoother transitions"* above `adjustment_factor = 1 + (2 * diversity - 1)`,
which is `2 * diversity` — a straight line. And `sample_size`, documented as a
count of solution *pairs*, counts solutions, so the default 50 produces up to
1,225 comparisons.

## Two sign errors under the same conditions

Two systems in the pass had an inverted ranking term, both in the function that
decides what the model sees, both untested.

[Generative Agents][ga] sorts its node list **ascending** by `last_accessed` and
then assigns `recency_decay ** i` with `i = 1` to the first element, so the
*least* recently accessed memory scores highest; the normalizer carries that
ordering through, giving the oldest node 1.0 and the newest 0.0 over a hundred
nodes. A `reverse=True` on that sort is the whole fix. [Memary][mm] computes
`np.argsort(entity_counts)[:TOP_ENTITIES]` in a function called
`_select_top_entities`, so the entities injected under the heading *"Knowledge
Entity Store:"* are the least-mentioned ones.

Both survived for the same three reasons, and the reasons generalise:

1. **The term is a minority of the score.** Generative Agents weights recency at
   0.5 against relevance at 3 and importance at 2 — under a tenth of the
   composite. An inverted minority term degrades results without breaking them.
2. **The output is judged by plausibility.** A simulation rated by humans for
   believability, or a chat that reads fine, cannot distinguish "the right
   memories, ranked well" from "adequate memories, ranked backwards".
3. **Nothing asserts the direction.** One test — build two items, touch one,
   assert the touched one scores higher — would have caught either in a line.

## What the three good tests have in common

The same pass produced three assertions that *can* fail, and they are worth
copying more than any of the above is worth avoiding.

**Gini Agent's scope test removes its own escape route.** It seeds two agents
with the *same text and the same embedding*, so the only difference between the
two units is `agent_id`, then asserts in both directions that each agent's recall
contains its own unit and not the other's, by id. A scope test whose fixtures
differ in content can pass because the query matched one and not the other; this
one cannot.

**GoodAI LTM ships the control beside the assertion.** `test_no_redundancy`
retrieves at an overlap threshold of 0.5 and asserts every pair of returned
passages scores at most 40; `test_redundancy_allowed`, twelve lines below, runs
the identical setup at 1.0 and asserts at least one pair scores 50 or more. The
second proves the first is not passing on an empty result.

**Memvid's as-of test asserts a value that was corrected.** Two cards for one
slot — `New York` at document date 1000, `San Francisco` at 2000 — with the read
at 1500 asserted to return `New York` and at 2500 `San Francisco`. The negative
and its control are two lines apart, and the negative is keyed on the identity of
a value, not on a count.

Three shapes, one property: **the assertion is arranged so that a plausible
wrong implementation produces a different answer.** That is the whole of it.

## For a reader of repositories

- **Read the assertion, not the test name.** `delete_frame_marks_deleted`,
  `test_memory_evolution` and a garbage-collection case that never calls the
  collector all describe behaviour the body does not check.
- **Ask what a wrong implementation would return.** If the answer satisfies the
  assertion, the case is decoration. `count == 0 || count == 1` after deleting
  one of one; `assertIsNotNone` on a field the constructor fills; `>= 0` on a
  length.
- **Grep the distinctive mechanism by name.** In six of seven systems here the
  untested part was the part the report had singled out as interesting. That is
  not a coincidence: the conventional parts arrive with conventions, including
  test conventions.
- **Run the producer test on every state you are told exists.** A CHECK
  constraint is a vocabulary, not a mechanism. Ask which code writes each value.
- **Widen the enumeration before believing an absence.** A grep for
  `get_at_time` across Memvid's `tests/` returns nothing and reads as an untested
  bitemporal mechanism; 406 of its 497 test functions live in in-source
  `#[cfg(test)]` modules. For Rust, `tests/` is the integration directory and not
  the suite — the same error class as [the instrument that narrowed the thing it
  measured][inst], caught this time by counting `#[test]` under `src/` before
  writing the sentence.

[ga]: ../content/systems/generative-agents.md
[mm]: ../content/systems/memary.md
[inst]: 2026-09-17-the-instrument-that-narrowed-the-thing-it-measured.md

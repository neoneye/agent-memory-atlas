# A judgement with a revisit date

**Status:** one mechanism the rubric has no column for, and one test hazard it
brought with it. Both from `decision_log` in [aimee](../content/systems/aimee.md),
a store three previous readings of that repository missed.

---

## The mechanism

`decision_log` keeps a decision rather than a fact: `subject`, `options`,
`chosen`, `rationale`, `assumptions`, `outcome`, `author`, a `linked_policy_id`,
a `supersedes_id`, a `status` defaulting to `active`, and a `revisit_when`.

Two transitions move a row, and they are different in kind.

**Supersession is event-driven and keyed on the subject.** Recording a decision
runs `UPDATE decision_log SET status = 'superseded' WHERE id = ?1 AND status =
'active' AND subject = ?2`, so one decision is live per subject and the losers
are kept rather than deleted. That is ordinary and good, and the atlas has a
vocabulary for it.

**The second has no vocabulary here.** A sweep runs

```sql
UPDATE decision_log SET status = 'revisit_due'
 WHERE status = 'active' AND revisit_when != '' AND revisit_when <= pg_now_text()
```

backed by a partial index on exactly that predicate. A decision becomes stale
**on a date its author chose when they made it**, with no new evidence, no
contradiction and no usage signal involved.

## Why the rubric has no column for it

The seven marks each answer a different question, and none of them is this one:

- `bitemporal` separates when a claim was *true* from when it was *recorded*.
  `revisit_when` is neither. It is a date attached to the claim on which the
  claim should be *looked at again*.
- Decay-and-reinforcement scores a memory by use — how often it was retrieved,
  how recently, whether it helped. `revisit_when` ignores use entirely.
- `trust_state` is closest, and the atlas would award it here on the
  `active / superseded / revisit_due` trio. But the mark records that a discrete
  status exists, not that one of the transitions is a **clock the author wound**.

The honest description is a fourth thing: an expiry on a *judgement* rather than
on a fact, set by the person best placed to know how long their reasoning should
survive its own context. A deploy-window decision made under this quarter's load
is not falsified in three months; it is merely due for another look, and that is
a distinct and useful state.

**What keeps it from being more than a curiosity is where it lands.**
`decision_log` is absent from the recall filter and from the assembled context,
so a row that flips to `revisit_due` announces itself to whatever queries the
table and to nothing the model sees. The mechanism is real, the wiring is not —
which is the same shape as most of the interesting things in this corpus.

## The hazard it shipped with

The test suite for this store carried a **date bomb, and it detonated on the day
of the reading.**

`test_record_is_active` recorded a fixture with `revisit_when` of `2026-09-01`,
using a date about eight months out as a stand-in for *far away*.
`test_revisit_sweep`, elsewhere in the same binary, asserts `flipped == 1` — that
a sweep over the whole table moves exactly one row, the one it deliberately dated
`2000-01-01`. On 1 September 2026 the first fixture also became due, the sweep
moved two rows, and the count assertion failed. Commit `771baba9` moved the
fixture to `2999-01-01`, which is the idiom `test_revisit_sweep` was already
using for its own not-yet-due row.

Three things worth taking from that:

1. **A committed test can carry an expiry, and it will not look like one.** The
   report reads tests as evidence that a property holds. A test that passes today
   and fails in March is evidence with a shelf life, and nothing in this atlas's
   checks would see it.
2. **The blast radius crossed tests.** The bomb was in one test's fixture and the
   failure surfaced in another test's global count. A suite that asserts over
   *the whole table* couples every fixture in the binary to every assertion.
3. **The fix moved the date rather than freezing the clock.** That is the right
   call for the project — the alternative is injecting a time source — and it
   means the same bomb is armed for the year 2999. Worth noting without
   pretending it matters.

The transition itself stays covered: `test_revisit_sweep` asserts the past-due
row flips, that the future and no-revisit rows do not, and that a second sweep
flips nothing. No coverage was lost, which is the claim to check before writing
that any was.

## The reading lesson

`decision_log` sat in a repository this atlas had read three times, twice with a
specific brief to re-verify marks in both directions. It was missed because every
reading followed the report's own file index, and the file index was written by
the first reading. **An appendix is a map of what was found, and re-reading from
it re-finds the same things.** The cheap counter is a schema-level sweep — list
every `CREATE TABLE` in the tree and ask which ones the report never names —
which costs one command and would have surfaced this on the second pass.

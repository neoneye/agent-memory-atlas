# The deletion harness, level 1 and level 2 — what is feasible now, and what a notch up costs

**Status:** proposed. Implementation plan for
[the harness this page does not ship](2026-08-12-the-harness-this-page-does-not-ship.md),
which establishes *why*; this note is *what*.
**Constraint that shapes everything below:** one laptop, a finite token budget,
and the seven-day dependency cooldown in
[`screen-repository`](../.agents/skills/screen-repository/SKILL.md). No plan here
requires standing up a fleet of memory systems, and the one place a third-party
system is touched is chosen because it needs no installation at all.

## What already exists, and three defects in it

[`benchmarks.md` §6](../content/benchmarks.md) specifies the thirteen-step
sequence, an adapter with `write`, `settle`, `prompt_prefix`, `forget`,
`run_background_jobs`, `leak_probes` and `audit_entries`, and a
`test_deletion_holds` body. It is closer to executable than most published
proposals and it is not executable, and building it surfaces three things that
reading it did not:

1. **The code covers steps 1–10. Steps 11–13 are specified in prose and absent
   from the test.** Share-to-a-second-scope, delete the original, assert absence
   from the second scope — the propagation half — has no implementation at all.
2. **`forget` returns `None` in the Protocol and a `memory_id` in the test.**
   `memory_id = memory.forget(...)` then `e["memory_id"] == memory_id`. One of
   the two is wrong; the contract has to pick.
3. **The prose says "six methods" and lists seven.** Trivial, and the kind of
   thing that stays wrong until something imports it.

Fixing these is not a prerequisite for level 1. It is a *product* of level 1, and
worth saying so: the first value of building a specification is discovering which
parts of it were never checked.

---

## Level 1 — the harness runs against itself

**Claim it supports:** *"Here is an executable thirteen-step sequence, and here
is proof its assertions discriminate."* Nothing about any real system.

**What gets built**

```text
tools/deletion_sequence/
  protocol.py            # the adapter Protocol, typed; the contract, settled
  sequence.py            # steps 1-10 as one function, one assertion each
  report.py              # structured result: step, outcome, evidence, untested paths
  adapters/
    reference_clean.py   # a toy store built to pass
    reference_leaky.py   # a toy store built to fail, at named steps
  tests/test_harness.py  # asserts clean passes and leaky fails at exactly those steps
  README.md              # how to write an adapter, and what a pass does not prove
```

**The two reference adapters are the deliverable**, more than the sequence is.
`reference_clean` is a dict-backed store with a value-keyed tombstone, a derived
summary that drops when its source disappears (the
[RisuAI](../content/systems/risuai.md) mechanism, which is the cheapest known fix
for step 9), and an event log that stores digests rather than values.
`reference_leaky` is the same store with four defects, one per interesting step:

| Defect | Fails at |
| --- | --- |
| delete removes the row, no tombstone | 6 — re-ingestion resurrects |
| the nightly job re-derives from retained raw text | 8 |
| the summary keeps no link to its sources | 9 |
| the audit row quotes the deleted value | 10 |

**Success criterion, and it is not "the tests pass".** The harness is validated
when `reference_leaky` fails *exactly* the four steps it was built to fail and no
others, and `reference_clean` passes all ten. That is a mutation test on the
harness itself. A suite shipped with only a passing fixture proves nothing about
whether its assertions discriminate — the criticism this atlas has made of other
people's suites, and the one it would otherwise repeat.

**Design decisions to settle while building**

- **`forget` returns an identifier**, resolving defect 2 above. Step 10 needs it,
  and a system that cannot produce one is itself a finding the report should
  record rather than a reason the harness cannot run.
- **`settle()` falls back to polling `prompt_prefix` to a timeout**, as the spec
  already says, and the report records *which* mode was used. A run that slept a
  guessed interval and a run that observed quiescence are different evidence.
- **A missing probe is a recorded outcome, never a skip.** `leak_probes`
  returning nothing for the vector index means the vector index is untested, and
  the report says so on its face. This is the single most likely way a real run
  produces a falsely clean result.
- **No pass/fail headline.** The output is a per-step table plus a list of
  untested paths. The moment it emits a single verdict, somebody will publish a
  league table with it.

**Cost:** roughly a day of writing, no dependencies beyond `pytest`, nothing
installed, no target system touched. **Risk:** low, and bounded by the fact that
every line is this project's own code.

**What level 1 explicitly does not claim:** that any real memory system passes or
fails anything. It is a tool plus a demonstration that the tool works.

---

## Level 2 — one real system, and the residue question

Two notches, and they are different in kind. Take them in this order.

### 2a — point it at a real system that costs nothing to install

The obvious targets are the wrong ones. Hillock needs numpy and a local Ollama;
NeuraKeep needs a native `better-sqlite3` build and both its manifests are inside
the cooldown; MythologIQ's suite needs `jsonschema`, `cryptography` and
`rfc8785`. Each would mean installing a dependency surface this project's own
rules say to wait out.

**[Memory Compiler](../content/systems/memory-compiler.md) needs nothing.** One
848-line Python file, standard library only, already executed during its review.
Its memory is four Markdown files, its deletion is a `TOMBSTONES.md` row, and its
`--close` gate refuses to seal a session while a rejected value has been
reasserted. Writing an adapter over it is an afternoon: `write` appends to
`CONTEXT.md`, `forget` adds a tombstone row, `prompt_prefix` returns the
concatenated canonical files, `run_background_jobs` runs `--close`,
`leak_probes` greps the generated index and the archives, `audit_entries` reads
the session ledger.

**It comes with a falsifiable prediction, which is why it is the right first
target.** Its `tombstone_collision_check` ignores rejected values shorter than
twelve characters as too noisy, so the outcome should flip across that boundary:

- Canary token `Vantablack` — **10 characters, below the floor** — should
  **fail** step 6. The tombstone row exists, the collision scan cannot see it,
  and re-feeding the source reasserts the value.
- Canary token `Vantablack-7` — **12 characters, at the floor** — should
  **pass** step 6, blocking the session close.

Two runs, one character-count apart, opposite outcomes, both predicted before
running. If the harness reports that, it has independently caught a defect that
was found by reading, and the pair is stronger evidence than either result alone.
If it does not, the harness is wrong and level 1's validation was insufficient —
which is worth knowing before anyone else runs it.

**And the spec's own default probe sits exactly on that boundary.** §6 fixes
`TOKEN = "Vantablack-7"`, which is twelve characters — one shorter and this
system would fail, one longer and the boundary is never probed. That is a
coincidence, and it is the argument for making the canary's length a parameter
rather than a constant: a probe whose length interacts with a system's internal
threshold is measuring the threshold, and a harness that cannot vary it will
report whichever side of the line it happened to land on.

**Cost:** an afternoon. **Risk:** low; nothing is installed and the target is a
handful of Markdown files in a scratch directory.

### 2b — steps 11–13, and residue as a partition

The propagation half has no implementation, and implementing it is where the
sequence stops being a deletion test and becomes a governance test.

**Steps 11–13** need two adapter methods the contract does not have:

```python
def share(self, text: str, *, from_scope: str, to_scope: str) -> None: ...
def scopes(self) -> list[str]: ...
```

then: share the canary to a second scope, delete the original, assert absence
from *both*. Most systems in this corpus have no answer at all — sharing is a
copy, and a copy has no link home — so the expected result is a wide failure, and
the interesting output is *how* each fails: no share mechanism (untestable), a
copy with no back-reference (fails 13), or a reference that resolves through the
original (passes for a reason that has nothing to do with deletion).

**The residue notch** is the more valuable one, and it is borrowed rather than
invented. [MythologIQ's Agent Memory](../content/systems/agent-memory-doctrine.md)
scores deletion not as a boolean but as a four-way partition of everything
derived from a purged source: `purged`, `declared_residual_controlled`,
`declared_residual_uncontrollable`, `undeclared_residual` — with the last cell a
hard gate.

Step 9 today asks *"is the value absent from derived artifacts?"* and gets a
boolean. Under the partition it asks *"what survived, and did you say so?"* —
which is a question real systems can pass. An embedding that survives until a
vacuum the memory layer does not schedule is `declared_residual_uncontrollable`
if the system discloses it and `undeclared_residual` if it does not, and this
atlas has already established, in the
[comparative report](../content/overview.md), that on three of four vector engines
it survives and nobody discloses it.

That turns step 9 from a step almost everything fails into a step that
discriminates — which is the whole argument for the partition, and the reason to
take it from a project that has one rather than to invent one here.

**Cost:** a day, plus a decision the note cannot make: whether the atlas's
sequence should adopt another project's metric wholesale, and how to cite it if
it does. **Risk:** moderate, and mostly conceptual — a partition with four cells
is harder to explain than a boolean, and a harness nobody understands is not run.

---

## Beyond level 2 — the fleet, and why it is not proposed

The obvious level 3 is adapters for Mem0, Letta, Zep, Graphiti and the rest,
under containers, in CI, producing a table.

**Not proposed, for three reasons, in descending order of how permanent they
are.** It needs installing a dozen dependency surfaces the cooldown exists to
refuse. It needs hardware and a token budget this project does not have. And a
published cross-system table is a scoreboard, which `AGENTS.md` says this project
does not produce — the moment the atlas ranks systems by a number it wrote, every
report becomes a defence of a position rather than a reading of code.

The right shape for that work is somebody else running level 1's harness against
their own store and publishing what they find. Which is the argument for making
level 1 small, dependency-free and easy to adopt, and for the README's most
important section being *what a pass does not prove*.

## Sequencing and the abandon condition

1 → 2a → 2b, and stop after any of them. Level 1 stands alone as a contribution.
2a is worth doing only if 1's mutation test passes, because pointing an
unvalidated harness at somebody else's code produces findings nobody should
trust. 2b is worth doing only if 2a produced a result that reading had not
already established.

**Abandon if:** somebody ships an executable thirteen-step sequence first, in
which case this becomes a report on their harness — the better outcome, and the
reason not to treat the sequence as territory.

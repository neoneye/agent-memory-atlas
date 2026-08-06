# The atlas as an agent protocol — what to build, what exists, what would be invention

**Status:** triaged, then the three scoped pieces built the same day —
`AGENTS.md`, `.agents/protocol/tests.yaml`, `.agents/protocol/build-brief.md`,
and the `use-the-atlas` skill. Two items remain declined on grounds this project
has already recorded once.
**Origin:** a seven-step proposal (Codex, 2026-08-07) to turn the atlas "from a
library into an agent workflow": inspect the target product → select a profile →
emit a reviewable build brief → implement in dependency order → run
pattern-derived negative tests → produce a conformance report → lock the atlas
version. Plus five repository additions.

## The premise is right

*"Point the AI at the atlas"* does leave too much discretion. An agent handed 155
reports and 21 patterns will read widely, and reading widely is how it ends up
recommending the most interesting mechanism rather than the smallest sufficient
one. The pattern index already warns a human reader against exactly this — *"the
correctable stack is one stack among several, not a bar the others fail to
clear"* — and an agent does not read warnings addressed to humans as constraints
on itself.

The proposal's strongest single sentence is that a build brief is **the human
checkpoint**: reviewing twelve decisions is cheaper than reviewing thousands of
generated lines. That is true and this project had not said it.

## What already exists, at file and section

The proposal treats five things as missing that are written down:

| Proposed as new | Where it already is |
| --- | --- |
| Five product profiles | `content/patterns/index.md` → *Stacks, by what you are building*: single-user tool, multi-tenant, companion/roleplay, autonomous actor, correctable-and-defensible — each with the failure that hurts for that shape, plus a *What you can defer* paragraph |
| Implement in dependency order | `content/overview.md` §8 *What I Would Build*, Ship First / Add Later — already ordered so each stage stands alone and vector search and extraction come last |
| Acceptance tests per pattern | Every pattern page has a `Tests to require` section; `content/benchmarks.md` §6 specifies the ten-step deletion sequence with a six-method adapter, §7 the contradiction test with five case shapes and five scoring dimensions |
| Adoption cost, tradeoffs, exemplars per pattern | Every pattern page has `Cost to adopt`, `Tradeoffs`, `Implementation checklist`, `Seen in the atlas`, `Related patterns` |
| Maturity per pattern | `content/patterns/index.md` → *How established is any of this?*, which splits the library into reporting, advocacy, and established-in-one-category, and gives the mechanism spread as generated counts |

So the missing work is **packaging and enforcement**, not knowledge — which the
proposal itself says in its last line. The correction is that it is *less*
missing than the recommendations imply, and a build that starts by authoring
five profiles would be re-authoring a table that exists.

## Built now

**A root `AGENTS.md`.** The single highest-value item on the list and the only
one with no judgement calls in it. It splits the repo into two jobs — using the
atlas to build something, and extending the atlas — and for the first one it says
*do not read the reports*, then gives the five-document reading order above. It
also carries the standing rules an agent would otherwise violate: absence is
scoped to a pinned commit, never cite adoption, never hand-copy a generated
count, the correctable stack is not the default.

That is the cheapest fix for the actual complaint, and it needed no new
vocabulary.

## Built next, in the order they depended on each other

All three landed the same day. What follows was the plan; the notes under each
are what actually came out.

**1. The build brief and the lock file.** Genuinely new, genuinely cheap, and the
part that makes the rest reviewable. `adopt` / `defer` / `reject` with a reason
per line, the invariants, the borrowed mechanisms with the system and commit they
came from, and the required test ids. The lock file is the same object plus the
atlas commit, which is what makes *"review only what changed"* possible when the
corpus moves. **Design constraint:** the brief must record the *reasoning*, not
just the selection, or it becomes the checklist the pattern index refuses to be.

**2. Test ids, and only for the tests that already exist.** `Tests to require`
sections and the two benchmark specifications are prose today. Giving them stable
ids (`scope.cross_tenant_absent`, `correction.survives_reindex`,
`deletion.absent_after_reindex_and_restart`, `retrieval.k_is_an_upper_bound`,
`prompt.recall_is_data_not_instruction`) costs nothing and makes a conformance
report checkable. Prior art to steal from, recorded in
[the eval-suite note](2026-07-28-executable-eval-suite.md): Verel's
`memory/rubric.py` runs a live probe per capability and emits a **proof string**
saying what actually happened — *"a boolean tells you the suite ran; that
sentence tells you the suite tested the right thing."*

**3. A `use-the-atlas` skill.** All three existing skills grow the corpus; none
uses it. This is the real gap behind the proposal. It should do the target-repo
inspection, propose a profile row from the stacks table, emit the brief, stop for
approval, and produce the conformance report. It should *not* contain a second
copy of the design knowledge — every step should cite the page it came from, so
the skill goes stale loudly instead of quietly.

## Declined, with the precedent

**A machine-readable manifest field for *applicability* and *conflicts*.** The
derivable fields — id, category, maturity tier, exemplar systems, test ids,
prerequisites for the correctable stack — can be generated from the pages, and
should be, as part of item 2. *Applicability* and *conflicts* cannot: they are
uniform judgements that have never been made uniformly. This project declined the
same shape twice already, in
[declined proposals](2026-07-28-declined-proposals.md) — wider filter columns,
declined because *"those dimensions have never been assessed uniformly across the
corpus"*, and a three-state partial column, declined because *"nearly everything
is partial at some resolution"*. The stated condition for changing the answer is
the right one and applies here unchanged: **add the dimension the way the seven
marks were added — one definition, applied to every page, with the reading
recorded.** A generated field carrying a judgement nobody made is worse than no
field, because it will be consumed as data.

**A conformance report that says "implemented according to the atlas".** The
table shape is good and the phrase is not. The atlas has no conformance
authority, has run its own deletion sequence against nothing, and
[declined the compliance framing once already](2026-07-28-declined-proposals.md)
because it is a claim about sufficiency that nothing here can back. The same
table titled *"which failure modes this build closes, and which it does not"* is
honest, useful, and does not imply a certification. **Would change if** the
deletion harness were actually run — the same condition recorded for the
compliance framing, which remains unmet.

## What the building taught, beyond the plan

**Test ids had to come before the brief**, not after — `required_tests` is a list
of ids, so the ids are the dependency. Seventeen went in, all traceable to a
`Tests to require` section, a benchmarks specification, or an overview
antipattern. One is new-but-derived: `tombstone.no_second_copy`, the discriminator
from [yesterday's re-derivation](2026-08-07-the-strong-form-tombstone-subset.md),
which is what tells a *consulted* tombstone from a *collided* one — assert both
that no live record carries the value and that the store holds no second copy.
Consulted passes both halves, collided passes the first, suppressed passes
neither.

**Every entry states what a pass does not prove**, which turned out to be the
field that took the longest to write and is the reason the file is worth having.
`deletion.absent_after_reindex_and_restart` does not prove erasure at the storage
engine. `scope.cross_tenant_absent` does not prove the boundary is authenticated.
`prompt.recall_is_data_not_instruction` tests the rendering, not the model. A
green test quoted as more than it is does more damage than a missing one, and
this atlas has spent three notes on exactly that failure in its own prose.

**The skill is subtractive on purpose.** Its stated failure mode is an agent
building a tombstone and a governed gateway onto a single-user notes app, and its
closing section says the answer *"you do not need this"* is a complete one worth
writing a brief for. The brief rule that enforces it: **an empty `defer` list
means the failure analysis did not happen.**

**And one small self-catch.** `AGENTS.md` first said "sixteen portable
acceptance tests"; there are seventeen. The number was hand-written into prose
next to a file that could be counted — the exact class
`check_claim_counts.py` exists to catch, in a file that checker does not scan.
Fixed by removing the count rather than correcting it, which is the right fix
every time it is available.

## The tension worth keeping in view

A deterministic protocol that emits adopt/defer/reject lists is in real tension
with the library's own first sentence about itself: *patterns are not a
checklist*. The resolution is that the brief is a record of a judgement, not a
substitute for one — the profile is the starting point, the deferrals carry
reasons, and the human approves before code exists. If the brief ever becomes
something an agent fills in without the failure analysis above it, this project
will have automated exactly the behaviour it wrote the pattern index to prevent.

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
`prompt.recall_is_fenced_as_data`) costs nothing and makes a closure
report checkable. Prior art to steal from, recorded in
[the eval-suite note](2026-07-28-executable-eval-suite.md): Verel's
`memory/rubric.py` runs a live probe per capability and emits a **proof string**
saying what actually happened — *"a boolean tells you the suite ran; that
sentence tells you the suite tested the right thing."*

**3. A `use-the-atlas` skill.** All three existing skills grow the corpus; none
uses it. This is the real gap behind the proposal. It should do the target-repo
inspection, propose a profile row from the stacks table, emit the brief, stop for
approval, and produce the closure report. It should *not* contain a second
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
antipattern — the review below then split the prompt-safety entry in two, and
`check_protocol.py` prints the live number rather than this paragraph. One is new-but-derived: `tombstone.no_second_memory_unit`, the discriminator
from [yesterday's re-derivation](2026-08-07-the-strong-form-tombstone-subset.md),
which is what tells a *consulted* tombstone from a *collided* one — assert both
that no live record carries the value and that the store holds no second copy.
Consulted passes both halves, collided passes the first, suppressed passes
neither.

**Every entry states what a pass does not prove**, which turned out to be the
field that took the longest to write and is the reason the file is worth having.
`deletion.absent_after_reindex_and_restart` does not prove erasure at the storage
engine. `scope.cross_tenant_absent` does not prove the boundary is authenticated.
the prompt-safety test covers the rendering, not the model. A
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

## What the review of the build found

Seven findings, all valid, four of them P1. Recorded because the pattern in them
is sharper than any single fix: **every one was a place where an artifact
described a property it did not have.**

- **The entry point said the protocol did not exist.** `AGENTS.md` still ended
  with *"Not built yet"* under a first half that described the built thing. The
  note's status was updated and the file it points readers at was not — the same
  disconnect this project found six days of, between the tombstone pattern page
  and the Daimon report.
- **The lock file hard-coded a real commit** (`4a328bb`) as its example, so an
  agent copying the template would have written a provenance claim that was never
  true in someone else's repository. Now a placeholder, and
  `check_protocol.py` fails the build if a literal hash reappears in a template.
- **The lock file threw away the reasons.** It was described as "the brief plus
  the atlas commit" and was in fact the brief flattened to bare lists — which
  drops the only field a later review needs. A review can see that bi-temporal
  validity was deferred; that decides nothing. *Why* it was deferred, and the
  `revisit_when` that invalidates the reason, is the whole point.
- **`tombstone.no_second_copy` contradicted evidence-before-belief.** It required
  that the store hold no second copy of a re-asserted value, while the recommended
  pipeline stores the raw event *before* extraction. A correct system keeps the
  evidence, the audit row and the hash — and would have failed the test for doing
  exactly what another pattern tells it to. Rewritten as
  `tombstone.no_second_memory_unit`, scoped to the unit layer, with a
  `scope_note` saying what may legitimately still hold the value. Its
  `not_proven: Nothing further` broke the catalogue's own central rule and now
  names four other tests.
- **Review mode became implementation mode.** The frontmatter advertised "review
  an existing memory design" and the workflow marched from brief approval into
  code. Approval of a design is not authorization to write to a repository. Four
  modes now — `decide`, `design`, `review`, `build` — and only the last touches
  the target, after its own second go-ahead.
- **The prompt-safety test conflated two tests.** It claimed recalled text
  *cannot* issue instructions, asserted that the agent does not act on it, and
  then said it tested the rendering rather than the model. Split into a
  structural assertion over the assembled prompt and a behavioural measurement
  that reports a count over N runs and never the word "passes".
- **"Sources go stale loudly" was false.** The catalogue said each test carries
  the page it came from *so that* a moved source shows up — and nothing parsed
  the file. `scripts/check_protocol.py` now validates the schema, unique ids,
  cited files and headings, pattern slugs, ids referenced in the templates, and
  literal commit hashes; it has a self-test with six controls and was
  mutation-tested against the live catalogue.
- **The rebuild test could pass on an empty store**, because a model answers from
  its weights. Now specified over high-entropy synthetic tokens and asserted
  against the retrieval artifacts rather than an answer.

The recurring shape — a document claiming a guarantee that nothing enforced — is
the same one the count checker was built for, one level up. The fix in every case
was either to build the enforcement or to stop making the claim.

## The tension worth keeping in view

A deterministic protocol that emits adopt/defer/reject lists is in real tension
with the library's own first sentence about itself: *patterns are not a
checklist*. The resolution is that the brief is a record of a judgement, not a
substitute for one — the profile is the starting point, the deferrals carry
reasons, and the human approves before code exists. If the brief ever becomes
something an agent fills in without the failure analysis above it, this project
will have automated exactly the behaviour it wrote the pattern index to prevent.

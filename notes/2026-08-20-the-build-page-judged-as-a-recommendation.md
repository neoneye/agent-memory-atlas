# The build page, judged as a recommendation

**Status:** review of a published page. Six defects, three of them joins over
material this project already holds, one of them a claim the page makes that its
own rules forbid. All six are fixed: `content/build.md` carries the profile and
stage routing, the deferrability table, the corrected Stage 1 wording, the
rarity of the route it recommends and no effort estimate, and
`.agents/protocol/tests.yaml` carries `stage`, `profiles` and a
`positive_control` on every entry.
**Origin:** reading [`content/build.md`](../content/build.md) end to end as a
builder would — profile, brief, stages, tests, closure — and then checking each
step against the corpus, the pattern index and
[`.agents/protocol/tests.yaml`](../.agents/protocol/tests.yaml) it routes into.

---

## What it gets right, so the rest is not read as a verdict on the page

**The staging claim is the strongest thing on it.** Store raw evidence before any
model call, search it lexically, and put vector search and model-based extraction
last. The corpus supports that in three independent ways: MemPalace is the worked
positive case, Daimon names the failure the floor protects against precisely
enough to be quotable, and *throwing away raw evidence too early* is one of the
antipatterns with the most instances behind it. This is not a taste claim.

**Each stage standing alone is a real property**, and rare in build advice. Most
staged designs have a stage 2 that is useless without stage 4.

**The page volunteers where its own advice fails.** The retrieval-as-product
exception is stated in §3 rather than left for a reader to discover, and
*What this page does not give you* is four flat admissions with no hedging. A
recommendation that names its own inapplicable case is doing something most
guides do not.

The defects below are almost all in the **packaging**, not the argument.

---

## 1. The profile is chosen in §1 and never used again

§1's whole instruction is to pick a profile from the failure you cannot
tolerate — five product shapes, from the pattern index's *Stacks, by what you
are building*. §3 then gives **one** five-stage table for all five, and §4 gives
**twenty** tests with no indication which of them a companion agent needs and a
multi-tenant SaaS does not. `tests.yaml` carries `id`, `pattern`, `source`,
`proves`, `spec`, `not_proven` — and no profile or stage field.

So the router runs and then discards its own output. A reader who correctly
identifies as *single-user tool* is handed the same stage table and the same
twenty tests as the reader building memory that must be defensible under
correction, which is the exact failure §1 exists to prevent: the whole stack
applied to a product that does not need it.

**The fix is a join, not new doctrine.** The stacks table already names the
patterns per profile. Every test already names its `pattern`. Profile → pattern →
test id is mechanically derivable from two committed artifacts, and nobody has
composed it. The same holds for stage → test: each stage's row already implies
which tests should pass at its end, and stating that turns §3 and §4 from two
lists into one workflow.

## 2. Only two of the twenty tests require a memory to be present

Read the twenty `then` clauses as a set and sort them by what they demand.

| What the clause requires | Count | Ids |
| --- | ---: | --- |
| Absence, refusal, or a bound | 16 | the three `scope.*`, `evidence.claim_resolves_to_source`, `evidence.source_delete_reaches_derived`, `gateway.no_bypass_path`, all five `tombstone.*`, `correction.retraction_without_replacement`, both `deletion.*`, `retrieval.k_is_an_upper_bound`, both `prompt.*` |
| A record other than a memory to exist | 2 | `gateway.model_cannot_claim_human_authority` (a stored record with the model actor), `deletion.absent_after_reindex_and_restart` (an audit entry beside the empty leak probes) |
| **A memory to be present** | **2** | `evidence.rebuild_from_retained`, `correction.survives_reindex` |

A system whose recall path always returns the empty set satisfies the first
sixteen. Every leak probe comes back empty, every tombstoned value stays absent,
no call returns another scope's data, and `k` is trivially an upper bound. Two
more are satisfied by any store that writes an audit row and stamps an actor.
The only two it cannot fake are the two whose `then` clause names something that
has to come back.

That is not a catalogue of a working memory system. It is a catalogue of ways one
can be wrong, and the two are the same thing only when something independent
establishes that the system works at all — which is exactly the burden the atlas
places on everyone else's benchmark.

**The project knows this discipline and applies it here once.**
`evidence.rebuild_from_retained` carries the anti-vacuity guard inside its own
`then` clause: high-entropy synthetic tokens, asserted against the retrieval
output rather than a model's answer, *"which is how this test passes while
proving nothing."* Whoever wrote that sentence had the failure mode fully in
view. It did not propagate to the other nineteen. The
[harness note](2026-08-12-the-harness-this-page-does-not-ship.md) makes the same
argument one level up — a deliberately leaky store that fails *exactly* the steps
it was built to fail, because a harness shipped with only a passing fixture
proves nothing about whether its assertions discriminate — and §7 of the compare
page praises `open-cowork` for carrying `expectedHits` alongside `forbiddenHits`,
which is this fix, already named, in a system the atlas reviewed.

**The fix is the shape the atlas recommends to others.** Every absence assertion
gets a paired presence assertion in the same fixture: `then: absent under scope
B` **and** `present under scope A`. Sixteen edits, no new doctrine, and it closes
the one way this catalogue can be quoted as evidence while proving nothing.

One entry already refuses a related temptation and deserves the credit:
`prompt.model_ignores_embedded_instructions` reports the number of runs in which
the injection worked and says *"do not report 'passes' — a probabilistic outcome
does not have one."* The catalogue is capable of this discipline. It is applied
to the one probabilistic test and not to the sixteen vacuous ones.

## 3. Deferrability cuts across the stages, and only one axis is drawn

The page's own deferral list is bi-temporal validity, hybrid retrieval fusion,
decay and reinforcement, and source-diverse context — *"improvements to memory
that already works. None of them prevents a silent failure."*

Lay that over the stage table and the two do not align:

- **Stage 3** is *"vector search fused with lexical, token-budgeted context
  assembly, recall fenced as data"*. Hybrid retrieval fusion is on the deferral
  list. Recall fenced as data is on the tensions page's *close to free and
  mostly missing anyway* list and has its own test id. So Stage 3 contains the
  most deferrable item on the page and one of the four cheapest non-deferrable
  ones, scheduled together, third.
- **Stage 5** contains rejected-value tombstones and negative tests in CI, which
  are the whole point of the correctable profile, *and* bi-temporal validity,
  which the page says is safe to defer.

A builder reading the table sequentially therefore builds a mostly-deferrable
stage before the two stages that close silent failures, and defers a free
mechanism that could ship in Stage 1. The stages are cut by **subsystem**;
deferrability cuts by **consequence**; the page draws one and states the other in
a paragraph below the table.

**The fix is a column.** Mark each stage's contents deferrable or not, or split
the two mechanisms that are misfiled by consequence — fencing forward into
Stage 1, bi-temporal out of Stage 5.

## 4. "An afternoon" is an invented number on a page that refuses to invent numbers

§4: *"Turning each `given/when/then` into a test in your own stack is an
afternoon; the atlas has not done it for you."*

*What this page does not give you*: *"It cannot tell you what to expect, because
almost nothing in the corpus publishes them and this project has measured none of
them itself. Inventing the figures would be worse than the gap."*

Both are on the same page. The estimate has exactly the standing the operating
numbers are refused for: nobody has done it, so nobody knows. And it is
implausible on inspection — `tombstone.key_normalization_attack` needs a unicode
look-alike corpus, `deletion.absent_from_shared_copies` needs an export or sync
path built before the assertion can run, `evidence.rebuild_from_retained` needs
high-entropy fixtures and a full index rebuild, and `gateway.no_bypass_path` is
only as good as an enumeration of every write path in the product, which is the
expensive part of the whole exercise.

**The fix is to delete the estimate**, or replace it with the structural
statement, which is true and useful: most of the twenty are a few assertions
against your own API, and four need fixtures — two scopes, an export path, a
rebuild — that dominate the cost.

## 5. Stage 1 promises a "boundary" the atlas reserves for something stronger

The stage table's Stage 1 row ends *"and a scope boundary that holds on the read
path"*. The compare page's third divergence defines three levels and reserves
**boundary** for authenticated identity, grants, and a filter a caller cannot
widen — the level explicitly rarer than the `scope_enforced` count suggests. The
paragraph directly under the table says so: *"Stage 1 is not a tenant boundary
yet, and shipping it as one is the mistake this table can most easily cause."*

The table and its warning use the same word for two different things, and the
table is the part a skimmer reads. **Fix: "a scope key that reaches the read
path."** One word, and it removes the only place where the page's own summary
column contradicts the atlas's vocabulary.

## 6. The page routes toward a stack whose rarity is stated on a different page

The correctable stack — scope, evidence, gateway, tombstone — is the route the
build page argues hardest and the one it is most careful to say is not the
default. What it never says is **how few systems have it**. The pattern index
does: *"No system in the atlas has all four"*, and twenty-one of three hundred
and eight carry a tombstone at all.

Checked against report frontmatter, the two of the four that are rubric marks
co-occur in **16 of 308** systems, and **10** of those also carry an append-only
audit and a discrete trust state. So a builder following this route is
implementing something with roughly ten partial precedents in the corpus and, by
the pattern index's reading, no complete one.

That is not an argument against the route. It is an argument that the sentence
belongs on the page doing the routing, because the honest version of *build this*
is *build this, knowing you will not find a worked example to copy* — and the
page's own *no reference implementation* admission is the same fact stated as a
gap in the atlas rather than as a property of the advice.

---

## Is it a good recommendation?

**Yes for the ordering claim, and the page is honest about the grade of evidence
behind it.** The order is argued from failure modes and the page says so, names
the case where it does not hold, and lists what it cannot give you. That is a
better epistemic posture than any comparable guide this project has read.

**The evidence is entirely negative, and that is worth stating more sharply than
the page does.** Every input to the staging order is a system that broke —
extraction wrong with nothing underneath it, scope retrofitted into a store that
already had rows. Negative evidence cannot distinguish *this order prevents the
failure* from *these systems had other problems*. No system in the corpus is
documented as having **arrived** in this order, so the sequence has zero positive
instances, and the page's *no reference implementation* line is the same
observation wearing a different hat.

**Where it is not good is packaging, and three of the six fixes are joins over
artifacts that already exist.** Profile → test is derivable today. Stage → test
is derivable today. The paired presence assertion is a shape the atlas
recommends to others on the same site. None of the three requires reading another
repository or running anything.

The single highest-value change is **§2**. A test catalogue in which only two
entries require a memory to come back is one quotation away from becoming the
thing this project criticises hardest: a green result that is evidence of
nothing. The atlas has never run these tests, which means the defect has never
had a chance to cause damage — and that is the only reason it is still cheap to
fix.

## For next time

- A test catalogue is a fixture design, not a list of claims. Whenever a suite is
  written from a corpus of *failures*, sort its assertions by what they require to
  exist before publishing it. A suite whose clauses almost all demand absence is
  measuring absence, and a system that returns nothing is its best performer.
- When a page opens with a router, check that something downstream consumes the
  routing. A choice with no consequence reads as guidance and functions as
  decoration.
- Effort estimates are numbers. The rule this project applies to latency and
  recall figures applies to *an afternoon* as well.

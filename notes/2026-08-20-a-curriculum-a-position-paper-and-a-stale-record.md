# A curriculum, a position paper, and a stale record

**Status:** triage. Three items read on 2026-08-20 — a dataset, a paper and an
essay — none of them agent memory, one of them carrying a sentence worth keeping.
Recorded alongside [Heimdall](../content/systems/heimdall.md), which was the
memory system in the same batch.
**Origin:** four links submitted together.

---

## Marble Skill Taxonomy — `withmarbleapp/os-taxonomy` at [`96a7933754af672e1bfdbf7ecb05c325860c6e0d`](https://github.com/withmarbleapp/os-taxonomy/commit/96a7933754af672e1bfdbf7ecb05c325860c6e0d)

**Not agent memory, and not close.** It is a curriculum dataset: 1,590
micro-topics of *what children learn* across primary and elementary years, 3,221
prerequisite edges, aligned to NGSS, Common Core and the UK National Curriculum,
under a split code/content licence. Screened clean — no auto-run surface, no
build-time execution, no unpinned dependency.

It is in this directory because of its **shape**, which the atlas has been
arguing about for weeks without a worked example outside software.

`schema/topics.schema.json` requires every topic to carry
`["id", "type", "subject", "name", "description", "evidence", "standards"]`,
where `evidence` is an array of strings — the mastery criteria by which a learner
is judged to hold the topic — and `type` is one of conceptual, procedural,
representational, language or meta. `data/dependencies.json` holds a directed
acyclic graph whose edges are tagged `hard` or `soft` and **carry a one-line
reason each**.

Set that against
[promotion between tiers](../content/patterns/promotion-between-tiers.md), whose
opening complaint is that everything has tiers and far fewer systems can say what
moves a memory up one. A curriculum is that structure taken seriously by a field
that has had two centuries to think about it: every node states the evidence that
promotes it, every edge states why the dependency exists, and the strength of the
dependency is typed rather than implied. Three properties a memory system could
copy directly:

1. **Evidence criteria live on the node, not in the promoter.** A memory that
   carries the conditions under which it would count as verified can be checked
   by anything, including a component written later.
2. **A dependency carries a reason.** The atlas's graph systems store edges with
   a type and almost never with a justification; a one-line reason per edge is
   what makes the graph auditable by a person rather than only traversable by
   code.
3. **Hard and soft prerequisites are different edges.** Most memory graphs have
   one relation strength, and the distinction between *cannot proceed without*
   and *goes better with* is exactly the one a retrieval budget needs.

No claim here is that this is memory. It is a well-made ontology of a promotion
structure, and the atlas keeps asking for one.

## AI Agents in Scientific Teams — [arXiv:2608.14667](https://arxiv.org/abs/2608.14667)

**Excluded, and the thinnest adjacency of the three.** *Position: AI Agents in
Scientific Teams Should Be Studied as Human-Agent Systems*, Emami et al.,
submitted 2 August 2026, cs.AI. Its argument is that work on "AI Scientists"
overweights autonomous capability and underweights the human-agent pair as the
unit of analysis, and it calls for mathematical frameworks for human-AI synergy.
No repository or dataset is named on the abstract page.

Nothing in it concerns storage, retrieval, correction or forgetting. The one
thread that touches this atlas is its stated near-term risk of **reduced
diversity of scientific inquiry** from deploying agents without accounting for
those dynamics — which rhymes with the corpus's most-repeated epistemic failure,
[retrieval certifying its own outputs](../content/overview.md), where a memory
that gets retrieved becomes the memory that gets trusted and the space of what
the agent considers narrows. Rhymes, and no more than that: the paper is about
teams of people and agents, not about what either remembers. Recorded so a later
reader does not have to check it twice.

## The Biggest AI Models Are Not the Biggest Threats — [The Cipher Brief](https://www.thecipherbrief.com/the-biggest-ai-models-are-not-the-biggest-threats)

**Excluded as a subject; one sentence kept.** Alvin W. Graylin, 13 August 2026.
The argument is that model size does not predict threat level — that safeguards,
orchestration, data quality and deployment context dominate parameter count.

The line worth keeping is about memory without using the word:

> "A larger model querying the same stale record returns the same coordinates
> faster and with more confidence."

That is the cleanest one-sentence statement of something this atlas argues at
length and never says so compactly. Scaling the model does not correct the store;
it amplifies whatever the store says, and it amplifies the *confidence* as much
as the content. Every system here that lets a use signal feed a trust field is
building the same mechanism deliberately — the retrieved memory becomes the
trusted memory — and this is the version where the amplifier is the model itself
rather than the ranker.

It also lands on the same side as
[Heimdall](../content/systems/heimdall.md), read in the same batch, whose whole
design is that a hit's *verification* must outrank its *score*. Staleness is not
a property a bigger model detects; it is a property something has to check.

---

## For next time

**A batch of four links is worth triaging as a batch.** Three of these are not
memory systems and one is, and the useful output was one report plus three
paragraphs — but the curriculum dataset would have been dropped without a note if
the disposition had been decided on scope alone. *Not in scope* and *nothing to
learn* are different verdicts, and the second is much rarer than the first.

**And a sentence from outside the field can be worth more than a paper inside
it.** The position paper is about agents and says nothing usable about memory;
the essay is about export controls and contains the best compression of the
staleness argument in this directory. Where a claim comes from predicts its
relevance badly.

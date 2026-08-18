---
title: What You Buy, and What It Costs
eyebrow: Tensions
description: Six axes where the corpus shows memory mechanisms trading against each other, with the systems that chose each end and what the choice forced them to build.
root: ..
page_kind: methodology
---

There is no memory system that answers every question, forgets nothing, isolates
perfectly, writes instantly, records everything it did, and gets better the more
it is used. Not because nobody has built it yet — because those properties are
not independent, and several of them are each other's cost.

This page collects the places the corpus shows that happening. Each axis below
has systems at both ends, and in the best cases the system says which end it
chose and why. The useful question for a builder is never *which mechanisms
should I have*; it is *which of these am I choosing between, and which way did
people with my problem choose*.

The [build page](../build/) turns that into an order of work. This one is the
map of what the order costs.

## 1. Recall against abstention

Every point you move toward answering more questions is a point toward answering
one you should have refused.

[Engram Alpha](../systems/engram-alpha/) is the only system here that treats this
as a curve to be fitted rather than a threshold to be guessed. It commits the
whole tradeoff curve — a score floor and a knee cut — and fits **the abstention
line per graph, from unanswerable probes built out of that graph's own
vocabulary**, so the refusal boundary is calibrated against the store it guards
rather than against a constant somebody picked. The report still names the price
it does not pay: the one number its external run leaves unpriced is how often an
*answerable* question gets warned.

[Hillock](../systems/hillock/) takes the other posture and is equally explicit
about it: below cosine 0.72 it returns *"I do not have verified information about
that"* and **the model is never called**. That is abstention bought at whatever
recall a fixed floor costs, chosen deliberately, in a system whose whole design
is that an unverified answer is worse than none.

The reason this axis is hard to reason about is that almost nothing measures both
directions. Waku Agent's memory arena is the exception worth copying: it scores
`INVENTED` — answering a probe that should have been refused — as a separate
outcome from `MISS`, so moving the dial shows up on both sides of the scoreboard
instead of one.

## 2. Retention against correctability

A store that never forgets is a store in which nothing can be unsaid. This is the
tension the atlas returns to most often, and the systems at the retention end are
not careless — they are optimising for a real property and paying for it
somewhere the design does not look.

[Reflexion](../systems/reflexion/) never retracts a plan; the store grows without
bound behind a fixed three-item read window, so a plan derived from a wrong
diagnosis is reused with the authority of a correct one until three newer ones
push it out of view. [Voyager](../systems/voyager/) concatenates skills into the
prompt unboundedly and keeps no memory of failure. [gh-aw](../systems/gh-aw/)
versions repo memory in git, unbounded, and **nothing is ever marked wrong**.

[Helix AGI](../systems/helix-agi/) is the sharpest instance because the two
halves sit in one file. Its journal — which its own docstring calls *"the single
source of truth"* — receives every belief write as a full snapshot and hears
about no deletion at all, so a removed belief still resolves its text out of the
log and back into the prompt through a dangling pointer.

At the other end, retention is what makes correction *work*, which is why this is
a tension and not a ranking. [Sonder Runtime](../systems/sonder-runtime/) writes
a content-hashed tombstone when it prunes a near-duplicate lesson, precisely so
the pruned value cannot be re-distilled from a later interaction;
[remem-mcp](../systems/remem-mcp/)'s capture path consults its tombstone by
content hash before every write. Both are *retaining more*, not less — they
retain the rejection. What they give up is the ability to say the store contains
only things believed true.

## 3. Scope strictness against reuse

Isolation and accumulated value pull in opposite directions, and three systems
here weakened scope on purpose rather than by omission.

[MemoryOps AI](../systems/memoryops-ai/) holds the strict end by mechanism: every
session opens with `app.tenant_id` and `app.user_id` set as transaction-local
Postgres GUCs so row-level security enforces isolation *"at the database, not
just in application code"*.

[OpenAkashic](../systems/openakashic/) holds the other end and is worth reading
for what the choice forced. It has **no tenant at all** — one public memory any
agent may read without a token — on the stated argument that a fix derived by one
agent should not be re-derived by the next. The correction machinery it had to
build is the price: disputes filed with rationales and evidence URLs, accumulated
reviews, and a scheduled pass consolidating them into a verdict of uphold, revise
or supersede. Remove the tenant boundary and you inherit the problem of
adjudicating between strangers.

Two more chose narrowly rather than wholesale: [remem-mcp](../systems/remem-mcp/)
ships an `org` scope that **deliberately drops the agent filter** so a handoff can
cross agents, and [Sonder Runtime](../systems/sonder-runtime/) scopes
interactions, tasks and preferences by project while holding lessons global on
the argument that procedural knowledge is the part worth sharing. Neither is a
missing scope key; both are a scope key someone decided not to apply on one path,
which is a different thing and should be documented as one.

## 4. Synchronous writes against write-to-readable lag

Extract on the write path and the user waits for a model call. Extract in the
background and there is a window — seconds, minutes, or overnight — in which
something just said is **not yet recallable**.

This is the axis where the corpus can tell you least, and the reason is itself a
finding. [The benchmarks page](../benchmarks/#on-storage) records write-to-readable
lag as measured **nowhere**: every benchmark ingests the full history and then
asks questions, so the window is invisible to all of them while being one of the
most noticeable properties in use — *"I told you that ten minutes ago."*

So the choice is real, common, and unpriced. Anyone shipping asynchronous
extraction should measure the distribution of that lag and publish it; it is the
difference between memory that feels present and memory that feels forgetful, and
no benchmark result will ever tell a reader which one they are buying.

## 5. Audit completeness against growth

An append-only record of every mutation answers *what happened to this memory in
March*. It also only ever grows, and the pass that bounds it is the pass most
likely to go unbuilt.

[Aura](../systems/aura/) holds the complete end: the only hash-chained audit in
this atlas, receipts linked by `prev_hash`, verification that re-hashes the
bodies, and sixteen tests for detecting modification, insertion and deletion.
[daem0n-mcp](../systems/daem0n-mcp/) keeps a full content snapshot per version.

[PowerMem](../systems/powermem/) shows the other end and what it costs: its audit
trail is a rotating file log with `backupCount=5`, so **the record has a horizon**
— and "what happened to this memory in March" is exactly the question an audit log
exists to answer.

The instructive case is in between. [Mnemosyne](../systems/mnemosyne/) has the
bounding pass — `degrade_episodic`, which rewrites old episodic content in place
— and it **has no caller**. That is the shape to expect: the growth bound is
cheap to specify, invisible when missing, and the first thing to be left unwired,
because nothing fails when it does not run.

## 6. Reinforcement against truth

Rank memories by how often they are used and you have built a system in which a
popular error is indistinguishable from a settled fact.

[Engram Alpha](../systems/engram-alpha/) refuses this explicitly, in two
principles its trust module states outright — *"Time doesn't validate"* and
*"Exposure doesn't validate."* Retrieval stamps `last_seen` for observability
only, because otherwise *"a broad recurring query would keep an attractive but
wrong note alive forever — retrieval certifying its own outputs."* Trust anchors
instead on `confirmed_at`, which only a deliberate act refreshes. The atlas
records the opposite choice against [Core Memory](../systems/core-memory/), where
recall raises the confidence class.

[Helix AGI](../systems/helix-agi/) found the loop in a running system and cut it:
relation count was removed from a belief's mass under a comment naming what it
caused — *"relations → mass ↑ → gravity ↑ → co-injection → more relations"*.

The same axis appears one level up as a retrieval philosophy with two named
camps. [M-flow](../systems/m-flow/)'s stated corollary is *"one strong path is
enough"*, which is the direct opposite of the corroboration requirement
[Graphify](../systems/graphify/) and [CLIO](../systems/clio/) impose — and the
atlas's own reading is that it is a defensible position **for recall rather than
for belief**. Which of those two you are building decides the argument.

## What is not a tradeoff

The page would be dishonest if it left the impression that everything costs
something, because four things in this corpus are close to free and are mostly
missing anyway:

- **Scope as a schema key, before there is an index.** It has to reach the
  schema, the indexes, the cache keys and every background job, which is why
  retrofitting it is the hardest migration on the pattern index's list and why
  putting it in first costs almost nothing.
- **Raw evidence retained before the model is called.** A system that stores what
  it was told and searches it lexically already works; a system that starts with
  extraction has no floor to fall back to when extraction is wrong.
- **Recall fenced as data rather than as instructions.** A pure win with no
  countervailing cost, and `prompt.recall_is_fenced_as_data` exists because it is
  routinely absent.
- **The embedding model stamped beside the embedding.** It is how you find the
  rows that need re-embedding after a change, and without it a silent
  re-embedding is a silent corpus-wide quality change.

Everything above those is a choice, and the atlas's position is that a design
which cannot say which end of each axis it chose has not made the choice — it has
inherited one.

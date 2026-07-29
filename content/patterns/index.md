---
title: Memory Design Patterns
eyebrow: Pattern library
description: Reusable architectural moves for building agent memory that can be retrieved, corrected, governed, and trusted.
root: ..
page_kind: pattern-index
---

Memory systems repeatedly solve the same hard problems under different names. This library extracts those solutions from the repositories in the atlas and presents them as implementation patterns rather than product features. **Not all of them are settled practice** — a few rest on one or two implementations, and the section below says which.

Each pattern explains the problem it addresses, its architectural shape, why it works, where it fails, examples from the analyzed systems, and the tests needed before relying on it.

<div class="pattern-index-grid">
  <a class="pattern-index-card tone-rose" href="./rejected-value-tombstone/">
    <span>Correction</span>
    <h2>Rejected-value tombstone</h2>
    <p>Remember that a value was rejected so extraction cannot silently bring it back.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-sage" href="./evidence-before-belief/">
    <span>Provenance</span>
    <h2>Evidence before belief</h2>
    <p>Persist the raw event before deriving compact claims, profiles, or summaries.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-violet" href="./trust-state-machine/">
    <span>Trust</span>
    <h2>Trust-state machine</h2>
    <p>Separate candidate, verified, rejected, and stale memory instead of using one truth bucket.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-blue" href="./hybrid-retrieval-fusion/">
    <span>Retrieval</span>
    <h2>Hybrid retrieval fusion</h2>
    <p>Combine semantic similarity, exact matching, metadata, and controlled reranking.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-amber" href="./scope-as-a-first-class-key/">
    <span>Boundaries</span>
    <h2>Scope as a first-class key</h2>
    <p>Make user, agent, project, and session boundaries part of identity and access.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-red" href="./governed-write-gateway/">
    <span>Governance</span>
    <h2>Governed write gateway</h2>
    <p>Route every belief mutation through one policy-enforcing transactional path.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-cyan" href="./explicit-write-destination/">
    <span>Federation</span>
    <h2>Explicit write destination</h2>
    <p>Allow broad reads while requiring every write to name its private or shared target.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-mint" href="./source-diverse-context/">
    <span>Context</span>
    <h2>Source-diverse context</h2>
    <p>Prevent adjacent chunks from one source from crowding every other memory out.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-gold" href="./recoverable-background-work/">
    <span>Reliability</span>
    <h2>Recoverable background work</h2>
    <p>Retain failed inputs and make extraction, consolidation, and indexing safely retryable.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-ink" href="./append-only-memory-audit/">
    <span>Observability</span>
    <h2>Append-only memory audit</h2>
    <p>Record mutations and retrieval use as events without confusing telemetry with truth.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-violet" href="./bi-temporal-fact-validity/">
    <span>Time</span>
    <h2>Bi-temporal fact validity</h2>
    <p>Track when a fact was true separately from when the system learned or expired it.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-amber" href="./decay-and-reinforcement/">
    <span>Lifecycle</span>
    <h2>Decay and reinforcement</h2>
    <p>Change reachability over time without confusing age, use, popularity, and truth.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-cyan" href="./zero-llm-capture/">
    <span>Capture</span>
    <h2>Zero-LLM capture</h2>
    <p>Persist scoped events synchronously, then enrich them with models only when useful.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-sage" href="./pluggable-memory-provider/">
    <span>Federation</span>
    <h2>Pluggable memory provider</h2>
    <p>Mount swappable memory backends behind one interface without losing deletion and scope.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-gold" href="./gate-the-expensive-path/">
    <span>Cost</span>
    <h2>Gate the expensive path</h2>
    <p>Decide whether the costly memory operation is worth doing before doing it.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-amber" href="./promotion-between-tiers/">
    <span>Lifecycle</span>
    <h2>Promotion between tiers</h2>
    <p>Everything has tiers; far fewer can say what moves a memory up one.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-red" href="./resolve-not-just-detect/">
    <span>Conflict</span>
    <h2>Resolve, don't just detect</h2>
    <p>Give contradiction detection a disposition, an actor, and a record the write path can consult.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-rose" href="./skills-as-procedural-memory/">
    <span>Procedure</span>
    <h2>Skills as procedural memory</h2>
    <p>Remember what worked as a runnable procedure, and gate the write on verified execution.</p>
    <b>Read pattern →</b>
  </a>
</div>

## How to use the library

Patterns are not a checklist. Start with the failure you need to prevent:

- Wrong facts return after correction: use a [rejected-value tombstone](./rejected-value-tombstone/) with a [trust-state machine](./trust-state-machine/).
- Memory cannot be audited: use [evidence before belief](./evidence-before-belief/) and an [append-only memory audit](./append-only-memory-audit/).
- Retrieval is plausible but misses exact facts: use [hybrid retrieval fusion](./hybrid-retrieval-fusion/).
- Memories leak across projects or users: make [scope a first-class key](./scope-as-a-first-class-key/).
- Different integrations write with different rules: add a [governed write gateway](./governed-write-gateway/).
- Private and shared memory are mixed: require an [explicit write destination](./explicit-write-destination/).
- Retrieval repeats one document: assemble [source-diverse context](./source-diverse-context/).
- Automatic extraction loses data on failure: build [recoverable background work](./recoverable-background-work/).
- Changing facts overwrite useful history: add [bi-temporal fact validity](./bi-temporal-fact-validity/).
- Old memory overwhelms recall or popular errors self-reinforce: separate [decay and reinforcement](./decay-and-reinforcement/) from truth.
- Model latency or outages make capture unreliable: add a [zero-LLM capture](./zero-llm-capture/) path.
- Memory is a swappable backend and "forget me" has nowhere to go: fix the [pluggable memory provider](./pluggable-memory-provider/) contract.
- Retrieval runs every turn and irrelevant memory bends the answer: [gate the expensive path](./gate-the-expensive-path/).
- The agent rediscovers how to do things it already solved: store [skills as procedural memory](./skills-as-procedural-memory/) behind a verified-execution gate.
- Contradictions are detected and nothing clears them: [resolve, don't just detect](./resolve-not-just-detect/).
- Memory has tiers and nobody can say what promotes between them: [promotion between tiers](./promotion-between-tiers/).

## How established is any of this?

A pattern library implies settled practice. For several of these, that would be
false, and the difference matters when you are deciding what to build.

Where the atlas has an exact count — the seven mechanisms on
[the rubric](../methodology/atlas-rubric/) — the spread is wide:

<!-- BEGIN GENERATED SPREAD -->
| Mechanism | Systems carrying it |
| --- | --- |
| Scope enforced in retrieval | 49 of 82 |
| Human review surface | 14 of 82 |
| Bi-temporal validity | 8 of 82 |
| Append-only mutation audit | 8 of 82 |
| Explicit trust state | 7 of 82 |
| Negative retrieval assertion | 5 of 82 |
| Rejected-value tombstone | 3 of 82 |
<!-- END GENERATED SPREAD -->

Read the bottom two rows as what they are. A mechanism present in two or three
systems out of eighty is **not a best practice**. There is no consensus
behind it, no library that gives it to you, no shared vocabulary, and nobody to
ask when your implementation has a hole. Adopting it means building it.

And in the tombstone's case the provenance is narrower still. It was not
designed by anyone: a red team walked a rejected value back to verified in three
steps, and Verel's fix became the mechanism. The second system carrying it
adopted it after the survey that became this atlas flagged its absence, and the
third arrived at a weaker form independently, keyed on exact text rather than a
normalized value — so the field has produced this idea **once** in the form that
survives an attack. The
[rejected-value tombstone](./rejected-value-tombstone/) page traces the whole
chain.

The outside view agrees, in the way that costs the atlas something to admit: the
field's most comprehensive survey of itself
([arXiv:2512.13564](https://arxiv.org/abs/2512.13564), 107 pages, 47 authors)
does not contain the words *tombstone*, *rejected* or *negative* anywhere, while
its trustworthy-memory section asks for "verifiable forgetting and auditable
updates" as future work. So this is not a practice the atlas is reporting late.
It is a mechanism three small repositories have and the literature has not
named — which is either the atlas being early or the atlas being wrong about
what matters, and one survey cannot tell you which.

So this library is doing two different jobs at once, and it is worth knowing
which one you are reading:

- **Reporting.** [Promotion between tiers](./promotion-between-tiers/),
  [hybrid retrieval fusion](./hybrid-retrieval-fusion/),
  [scope as a first-class key](./scope-as-a-first-class-key/),
  [evidence before belief](./evidence-before-belief/),
  [zero-LLM capture](./zero-llm-capture/) and
  [recoverable background work](./recoverable-background-work/) describe things
  many systems already do. The pattern refines a practice that exists.
- **Advocacy.** [Rejected-value tombstone](./rejected-value-tombstone/),
  [resolve, don't just detect](./resolve-not-just-detect/) and the negative-eval
  discipline inside [source-diverse context](./source-diverse-context/) rest on
  one or two instances. The atlas is arguing for them, not reporting them.

The advocacy patterns are the ones this atlas thinks matter most, which is
exactly why they need the disclosure rather than the benefit of the doubt. A
reader who assumed they were industry practice — as their author did until
tracing the history — would be adopting them on the strength of an argument, not
a consensus. That may still be the right call. It is a different decision.

## The smallest serious stack

Patterns are usually read one at a time, which hides the thing that actually
breaks systems: **they fail at the intersections.** A rejected-value tombstone is
decorative if three ungoverned write paths bypass the check. Hybrid retrieval is
actively dangerous without scope as a key, because better recall means a wider
blast radius when the boundary is missing. An audit log is unreadable if the
evidence it references was discarded.

So there is a minimum coherent set. Four patterns close the three failure modes
this atlas argues are the real ones, and each of the four exists to make one of
the others enforceable:

| Pattern | Closes | Depends on |
| --- | --- | --- |
| [Scope as a first-class key](./scope-as-a-first-class-key/) | Memories crossing user, project, or agent boundaries | nothing — build this first |
| [Evidence before belief](./evidence-before-belief/) | Extraction errors becoming permanent | scope, so evidence is scoped too |
| [Governed write gateway](./governed-write-gateway/) | Rules that some write path quietly ignores | scope, to know what a write may touch |
| [Rejected-value tombstone](./rejected-value-tombstone/) | Corrections undone by the next extraction | the gateway, or the check is bypassable |

Build them in that order. Each one is cheap on its own and expensive to
retrofit — scope in particular, because it has to reach the schema, the indexes,
the cache keys, and every background job, and adding it to a store that already
has data is the hardest migration in this list.

**What you can defer.** [Bi-temporal validity](./bi-temporal-fact-validity/),
[hybrid retrieval fusion](./hybrid-retrieval-fusion/),
[decay and reinforcement](./decay-and-reinforcement/) and
[source-diverse context](./source-diverse-context/) are all improvements to
memory that already works. None of them prevents a silent failure; they make a
functioning system better, which is a different and less urgent job.

**What the four do not give you.** They make memory correct and correctable.
They do not make it *good*: nothing above decides what is worth remembering, and
that judgement — see [gate the expensive path](./gate-the-expensive-path/) and
the [trust-state machine](./trust-state-machine/) — is where the quality
actually comes from. Correct memory full of trivia is still a bad product.

No system in the atlas has all four. Filter the
[homepage](../#systems) by tombstone and scope to see how quickly the corpus
thins out.

**What the four cost together.** Each page states its own cost; the compounded
bill is what nobody budgets for, and it lands in two places.

*Storage stops being bounded by what you believe.* Evidence before belief keeps
the raw event that a claim was derived from, tombstones keep values you decided
were wrong, and bi-temporal validity keeps superseded versions rather than
overwriting them. Together they mean the store grows with everything that ever
happened, not with what is currently true, and the three retention policies are
separate decisions — evidence, tombstones and history age out on different
clocks, or should. A system that adopts all three and writes one TTL has not
thought about it.

*Writes get a hop they did not have.* A governed write gateway means no path
writes directly: every one proposes, gets checked against scope, dedupe, conflict
and the tombstone ledger, and only then commits. That is a latency cost on the
write path and a complexity cost on every integration, which is exactly why it
has to be the *only* path — a fast bypass reintroduces the failure the gateway
exists to prevent, and does it silently.

**What it does not cost is context.** A reasonable misreading of the tombstone
pattern is that the agent must be told what *not* to believe, spending prompt
budget on negative facts. It does not: a tombstone is consulted on the **write**
path, before a value is allowed to become active, and is suppressed from recall
entirely. If rejected values are reaching your prompt, the mechanism is
misplaced. The one measured warning in this atlas about context cost points the
other way — see [gate the expensive path](./gate-the-expensive-path/), where the
expense is retrieving memory at all, not retrieving negative memory.

## Composing them

The patterns compose. A serious memory layer normally needs several, but each additional mechanism has operational and cognitive cost. Every page now states that cost explicitly under **Cost to adopt** — what you must build, what it forces on the rest of the system, what it costs to keep running, and when to skip it. Add the smallest set that closes a demonstrated failure mode.

To check which systems already implement a given mechanism, see the [capability index](../capabilities/) in the comparative report.

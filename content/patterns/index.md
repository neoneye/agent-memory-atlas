---
title: Memory Design Patterns
eyebrow: Pattern library
description: Reusable architectural moves for building agent memory that can be retrieved, corrected, governed, and trusted.
root: ..
page_kind: pattern-index
---

Memory systems repeatedly solve the same hard problems under different names. This library extracts those solutions from the repositories in the atlas and presents them as implementation patterns rather than product features.

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

## Composing them

The patterns compose. A serious memory layer normally needs several, but each additional mechanism has operational and cognitive cost. Every page now states that cost explicitly under **Cost to adopt** — what you must build, what it forces on the rest of the system, what it costs to keep running, and when to skip it. Add the smallest set that closes a demonstrated failure mode.

To check which systems already implement a given mechanism, see the [capability index](../compare/#capability-index) in the comparative report.

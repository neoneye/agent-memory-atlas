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
  <a class="pattern-index-card tone-mint" href="./retrieval-hysteresis/">
    <span>Retrieval</span>
    <h2>Retrieval hysteresis</h2>
    <p>Give a unit its own activation state so it neither repeats every turn nor vanishes mid-thread.</p>
    <b>Read pattern →</b>
  </a>
  <a class="pattern-index-card tone-gold" href="./memory-as-an-editing-surface/">
    <span>Control</span>
    <h2>Memory as an editing surface</h2>
    <p>Let a person edit, pin, merge and delete the same rows the model reads — not a viewer over them.</p>
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
  <a class="pattern-index-card tone-amber" href="./cache-preserving-injection/">
    <span>Cost</span>
    <h2>Cache-preserving injection</h2>
    <p>Split injected memory by how often it changes, so recall cannot invalidate the prefix cache every turn.</p>
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
- Retrieval quality is fine and the provider bill is not: use [cache-preserving injection](./cache-preserving-injection/) — a recall block in the system prompt invalidates the prefix cache on every request, and nothing else reports it.

## How established is any of this?

A pattern library implies settled practice. For several of these, that would be
false, and the difference matters when you are deciding what to build.

Where the atlas has an exact count — the seven mechanisms on
[the rubric](../methodology/atlas-rubric/) — the spread is wide:

<!-- BEGIN GENERATED SPREAD -->
| Mechanism | Systems carrying it |
| --- | --- |
| Scope enforced in retrieval | 126 of 217 |
| Append-only mutation audit | 65 of 217 |
| Human review surface | 54 of 217 |
| Negative retrieval assertion | 47 of 217 |
| Explicit trust state | 42 of 217 |
| Bi-temporal validity | 27 of 217 |
| Rejected-value tombstone | 11 of 217 |
<!-- END GENERATED SPREAD -->

Read the bottom two rows as what they are. A mechanism present in seventeen
systems of two hundred and seventeen — or in nine — is **not a best
practice**. There is no consensus behind it, no library that gives it to you, no
shared vocabulary, and nobody to ask when your implementation has a hole.
Adopting it means building it.

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

**Eight months later the literature named it, and the atlas should say so.**
*Is Agent Memory a Database? Rethinking Data Foundations for Long-Term AI Agent
Memory* ([arXiv:2605.26252](https://arxiv.org/abs/2605.26252), 25 May 2026)
argues that agent memory is a data-management workload whose correctness is "a
property of the state trajectory, not of individual records", and formalises it
as **Governed Evolving Memory** — four state-level operators (ingestion,
revision, forgetting, retrieval) under six correctness conditions. Two of the six
are this library's advocacy pages written as invariants. **C2** requires that
"no superseded value becomes current", which is the rejected-value tombstone
stated as a property rather than as a table. **C4** requires that forgetting and
revision *preserve provenance chains*, which is
[evidence before belief](./evidence-before-belief/) and the
[append-only memory audit](./append-only-memory-audit/) at once. It also states
an impossibility the atlas has only ever argued empirically: append-only storage
cannot satisfy C2, so supersession chains are structurally insufficient no
matter how carefully they are kept.

What that changes here is narrow and worth being precise about. The tombstone
page said there is "no shared vocabulary" for the mechanism; there is now one,
in a vision paper with a prototype (MemState, on an embedded property graph)
rather than in a shipped library — which is a different thing from consensus and
from adoption. The four failure modes that paper opens with — unregulated
growth, missing semantic revision, capacity-driven rather than importance-driven
forgetting, and read-only retrieval — are the same four this atlas keeps
reporting, arrived at from the database side by people who did not read these
pages. Two independent derivations is better evidence than one, and it is still
not a practice.

So this library is doing two different jobs at once, and it is worth knowing
which one you are reading. Every page now carries its answer as a pill under its
title, so the distinction survives a reader who arrives by search and never sees
this section. The list below is the same classification, complete:

- **Reporting an established practice.**
  [Append-only memory audit](./append-only-memory-audit/),
  [bi-temporal fact validity](./bi-temporal-fact-validity/),
  [cache-preserving injection](./cache-preserving-injection/),
  [decay and reinforcement](./decay-and-reinforcement/),
  [evidence before belief](./evidence-before-belief/),
  [explicit write destination](./explicit-write-destination/),
  [gate the expensive path](./gate-the-expensive-path/),
  [governed write gateway](./governed-write-gateway/),
  [hybrid retrieval fusion](./hybrid-retrieval-fusion/),
  [pluggable memory provider](./pluggable-memory-provider/),
  [promotion between tiers](./promotion-between-tiers/),
  [recoverable background work](./recoverable-background-work/),
  [scope as a first-class key](./scope-as-a-first-class-key/),
  [skills as procedural memory](./skills-as-procedural-memory/),
  [trust state machine](./trust-state-machine/) and
  [zero-LLM capture](./zero-llm-capture/) describe things
  many systems already do. The pattern refines a practice that exists.
- **Advocacy — one or two instances.**
  [Rejected-value tombstone](./rejected-value-tombstone/) and
  [resolve, don't just detect](./resolve-not-just-detect/) rest on one or two
  instances. The atlas is arguing for them, not reporting them.
- **Reporting, with one advocacy claim.**
  [Source-diverse context](./source-diverse-context/) is the mixed case: the
  quota mechanism itself is ordinary retrieval engineering that several systems
  run, while the negative-eval discipline inside it is an argument with almost
  nothing behind it.

The advocacy patterns are the ones this atlas thinks matter most, which is
exactly why they need the disclosure rather than the benefit of the doubt. A
reader who assumed they were industry practice — as their author did until
tracing the history — would be adopting them on the strength of an argument, not
a consensus. That may still be the right call. It is a different decision.

**A fourth case, added later and needing its own label.**
[Retrieval hysteresis](./retrieval-hysteresis/) and
[memory as an editing surface](./memory-as-an-editing-surface/) are neither
advocacy nor general reporting. They are **mature in one category and unknown
outside it.** Both are mature, refined against very large user bases,
and almost every instance is a roleplay or companion client — SillyTavern,
RisuAI, N.E.K.O., Soul of Waifu, Z-Waif. No extraction-based system in this atlas
carries per-unit activation state, and the systems that hold `human_review`
mostly offer approval of a queue rather than an editor over the store.

That is a different epistemic situation from a mechanism three repositories
invented. These are known solutions to problems the rest of the field has, sitting
in codebases the rest of the field does not read — which is worth stating plainly,
because it was a reader pointing out the atlas had described these mechanisms six
times without ever collecting them that produced both pages.

## Stacks, by what you are building

Patterns are usually read one at a time, which hides the thing that actually
breaks systems: **they fail at the intersections.** A rejected-value tombstone is
decorative if three ungoverned write paths bypass the check. Hybrid retrieval is
actively dangerous without scope as a key, because better recall means a wider
blast radius when the boundary is missing. An audit log is unreadable if the
evidence it references was discarded.

So the useful unit is a stack rather than a pattern. Which stack depends entirely
on what breaks if your memory is wrong, and that is a product question this
library cannot answer for you:

| If you are building | Start with | Because the failure that hurts is |
| --- | --- | --- |
| **A single-user tool** — a coding assistant, a personal note agent | [scope](./scope-as-a-first-class-key/) (project or session, not tenant) and [explicit write destination](./explicit-write-destination/) | writing to the wrong project, not believing something false |
| **Anything multi-tenant** | [scope](./scope-as-a-first-class-key/) first and completely, then [hybrid retrieval](./hybrid-retrieval-fusion/) | one tenant seeing another's memory, which better recall makes worse |
| **A companion or roleplay agent** | [memory as an editing surface](./memory-as-an-editing-surface/) and [retrieval hysteresis](./retrieval-hysteresis/) | repeating yourself, or raising something the user asked you to drop |
| **An autonomous agent that acts** | [governed write gateway](./governed-write-gateway/), [gate the expensive path](./gate-the-expensive-path/), [skills as procedural memory](./skills-as-procedural-memory/) | acting on a memory nothing checked |
| **Memory that must be correctable and defensible** | the four below | a correction that silently does not hold |

The last row is the one this atlas has the most to say about, so it gets the rest
of this section. Read it as **one stack among several**, not as a bar the others
fail to clear: a fast CRUD memory for a single user genuinely does not need a
tombstone, and saying otherwise would be gatekeeping.

### The correctable stack

Four patterns close the three failure modes this atlas argues are the real ones,
and each of the four exists to make one of the others enforceable:

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

**And be clear about what that thinning means.** Eleven of two hundred and seventeen systems carry a
tombstone, so this stack describes almost nobody. Two readings are available and
this atlas cannot settle between them: either the field has not yet paid for a
failure it will pay for later, or the cost genuinely exceeds the benefit for most
products and the three holders are unusual rather than ahead. The
[establishment section](#how-established-is-any-of-this) says which patterns rest
on how many instances; take the deferrals above seriously, and if none of the
failure modes here is the one that would hurt you, build the smaller stack.

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

## What is deliberately not a pattern here

Three mechanisms a reader would reasonably expect are absent, and their absence is
a position rather than an oversight. Stating it, because an unexplained gap in a
pattern library reads as ignorance of the field.

**Summarization and compaction.** The single most common answer to context
overflow, and this library treats it as an **antipattern** rather than a pattern:
see [chained lossy summarization](../compare/#6-antipatterns-and-failure-modes)
in the comparative report. The reasoning is that a summary which replaces its
source has no per-fact identity, so nothing in it can be corrected, scoped or
deleted — and the atlas's evidence for that is not theoretical.
[CowAgent](../systems/cowagent/) rewrites its long-term file nightly from itself
plus one day's notes; [RisuAI](../systems/risuai/) summarizes its own summaries
and its team replaced that design twice. Compaction is a real and necessary
technique; the position here is that it belongs to the context window rather than
to the memory layer, which is also why
[conversation-window management](../compare/#not-in-scope-conversation-window-management)
is outside this atlas's scope test. **[Evidence before
belief](./evidence-before-belief/) is the pattern that makes compaction safe** —
summarize freely once the source survives the summary.

**Working-versus-long-term as an architectural split.** Nearly every system here
has tiers, so a pattern saying "have tiers" would report a fact rather than a
choice. [Promotion between tiers](./promotion-between-tiers/) exists instead,
because the discriminating question is not whether the tiers exist but what moves
a memory up one — and far fewer systems can answer that.

**Context-window pruning.** Genuinely important, and genuinely a prompt-assembly
concern rather than a memory-lifecycle one. A pruning pattern would be about
token budgets, and this library is about what survives a session with an
identity. [Gate the expensive path](./gate-the-expensive-path/) covers the
adjacent decision not to retrieve at all.

**Prompt-cache preservation was bundled with the above and has since been
separated**, because the two are not the same claim. Pruning is about how many
tokens you can afford; caching is about *where* a memory may be placed, and that
turns out to constrain what a memory system is allowed to be — Hermes Agent's
hard character caps, its refusal to accept an over-budget write, and its
synchronous in-turn consolidation all follow from it rather than from anything
about recall. That is a memory design derived from a cost constraint, so it is a
pattern here: [cache-preserving injection](./cache-preserving-injection/). The
pruning half of the original entry stays out.

If you think one of these is misfiled, the disagreement is about the scope test
rather than about the mechanism, and that test is stated at the top of the
[comparative report](../compare/).

## Composing them

The patterns compose. A serious memory layer normally needs several, but each additional mechanism has operational and cognitive cost. Every page now states that cost explicitly under **Cost to adopt** — what you must build, what it forces on the rest of the system, what it costs to keep running, and when to skip it. Add the smallest set that closes a demonstrated failure mode.

To check which systems already implement a given mechanism, see the [capability index](../capabilities/) in the comparative report.

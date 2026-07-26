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

The patterns compose. A serious memory layer normally needs several, but each additional mechanism has operational and cognitive cost. Add the smallest set that closes a demonstrated failure mode.

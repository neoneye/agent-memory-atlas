---
title: Cache-Preserving Injection
eyebrow: Pattern · Cost
description: Split injected memory by how often it changes, so a per-turn recall block cannot invalidate the provider's prompt-prefix cache on every request.
root: ../..
page_kind: pattern
stance: reporting
---

> **This is a cost pattern, and it is here on a narrow argument.** The
> [patterns index](./) declines context-window pruning as a prompt-assembly
> concern rather than a memory one, and that decision stands. This page is the
> part of that territory which is not about token budgets: **where you inject
> memory constrains what your memory system is allowed to be**, and one system
> in the atlas redesigned its entire write path around that constraint rather
> than around anything about recall.

## Intent

Place injected memory according to how often it changes, so that the stable part
of the prompt stays byte-identical between turns and the provider's prefix cache
survives the session.

## The problem

The obvious place to put memory is the system prompt, near the top, where the
model is most likely to attend to it. Every provider that offers prompt caching
keys that cache on an **exact prefix match**. The two facts collide.

A retrieval block is a function of the current message. Put it in the system
prompt and the system prompt differs every turn, so the cached prefix misses on
every request — and the miss is not partial. Everything from the first differing
byte onward is re-processed, which for a memory-augmented agent is usually the
whole prompt.

This is invisible in exactly the way that matters. Retrieval quality is
unaffected, tests pass, and the only signal is the bill. Five reports in this
atlas record a system in this state, and none of the five projects appears to
have noticed:

- [Helm](../../systems/helm/) — *"Prompt-prefix caching is invalidated on every
  turn, by construction."* `INDEX.md` is stable and arrives through an import,
  but `--append-system-prompt` carries `buildPersona(mode) +
  recallMemories(prompt)`, and the recall block is a function of the current
  message.
- [CSM](../../systems/csm/) — the per-turn injection invalidates the prefix cache
  every turn, and the report notes that nothing measures the cost.
- [RisuAI](../../systems/risuai/) — the injected block varies per turn,
  *including randomly*, which defeats caching by construction.
- [SillyTavern](../../systems/sillytavern/) — memory is injected at an unstable
  position rather than in a stable prefix.
- [OpenCode](../../systems/opencode/) — no memory of its own, but everything a
  plugin injects goes through `experimental.chat.system.transform` into the
  system prompt, so the *contract* hands every plugin author this failure.

The cost is not a rounding error, and it compounds with the thing memory systems
are for. The more memory you inject, the larger the prefix you are invalidating.

## The pattern

Sort injected material by volatility and give each class a position that matches:

```text
system prompt (cached prefix)
  ├─ persona, policy, instructions        — changes ~never
  └─ memory INDEX / stable working set    — changes between sessions
─────────────────────────────────── cache boundary
user turn (never cached)
  └─ query-specific recall results        — changes every turn
```

Three shapes implement this, and they differ in what they give up:

**Split by position.** Stable memory stays in the prefix; query-specific recall
moves into the user turn. Nothing is lost — the model sees the same tokens, in a
different envelope. Helm's report notes this arrangement is "one line away" and
that the system's own static channel already demonstrates it.

**Freeze the snapshot.** Render memory into the system prompt once, at session
start, and refuse to update it mid-session. Writes still land on disk
immediately and durably; they simply do not reach the model until the next
session begins.

**Split the memory, not the position.** Put a one-line index of the store in the
prefix and load an item's body on demand. This is the cheapest of the three where
the unit is large and individually addressable, and it is described under
*Why it works* below because its cost curve differs from the other two.

```mermaid
flowchart TD
    A["session start"] --> B["render stable memory<br/>into system prompt"]
    B --> C["prefix cached"]
    D["turn N"] --> E{"material varies<br/>with this turn?"}
    E -- "no" --> C
    E -- "yes" --> F["append to the user turn"]
    F --> G["prefix cache still hits"]
    H["mid-session write"] --> I["persist to disk"]
    I -.->|"deliberately not re-rendered"| C
```

## Why it works

Caching is a prefix property, so the only thing that matters is *where the first
difference falls*. Moving the volatile block after every stable byte converts a
guaranteed miss into a guaranteed hit without changing what the model reads.

The second-order effect is the interesting one. Once prompt cost is a static,
known quantity, a memory budget becomes enforceable — which is what lets
[Hermes Agent](../../systems/hermes-agent/) take the position almost nothing
else in this atlas takes: memory is **hard-bounded and frozen, because the
prompt cache matters more than completeness.** `MEMORY.md` is capped at 2,200
characters and `USER.md` at 1,375. When an `add` would exceed the cap the write
is *refused*, and the tool returns the current entries with an instruction to
consolidate and retry within the same turn. Compaction is not a background
worker; it is a synchronous obligation handed to the model at the moment of
overflow.

That is a write path, a correction path and a capacity policy all derived from a
caching constraint. It is why this belongs in a memory pattern library rather
than in a prompt-engineering note.

**[Ollama](../../systems/ollama/) is the third shape, and it is the cheapest of
the three.** Rather than choosing where to put the memory, it splits the memory
itself: `SkillCatalog.SystemContext()` renders one `- name: description` line per
skill into the system prompt, and the body of a skill loads only when something
calls the `skill` tool, arriving as a tool result in the message history. The
comment gives the reasoning as a token argument rather than a caching one —
*"advertises the catalog without expanding full instructions in every request.
The skill call is the explicit loading boundary"* — and the caching property
falls out for free, because the index is computed once at start from a
name-sorted list and is therefore byte-identical for the session.

Call it **index in the prefix, body after it**. It costs one line per item
always and the full item only when used, which inverts the usual scaling: a
store that grows in *item size* costs nothing extra, and only a store that grows
in *item count* pushes on the prefix. It applies wherever memories are large,
individually addressable and rarely all needed at once — documents, playbooks,
runbooks — and not at all where the unit is a one-line fact, since there the
index and the body are the same size.

The catch is that it moves retrieval into the model. Nothing here scores a match;
the model reads forty descriptions and picks. That is fine for forty and not for
four thousand, and it makes the quality of the *description* the whole retrieval
system — which is why Ollama's bundled `skill-creator` spends most of its length
on how to write one.

## Tradeoffs

- **Freshness is the price of freezing.** Under the frozen-snapshot shape, a
  memory written at turn 3 is invisible to the model until the next session.
  Hermes accepts this explicitly. If your agent must act on what it just learned,
  take the split-by-position shape instead, which costs nothing in freshness.
- **The bounded variant hands editorial control to the model.** Hermes's refusal
  loop makes the model choose what to discard under time pressure, with no review
  and no record of what was dropped — which is the failure
  [append-only memory audit](../append-only-memory-audit/) exists to prevent.
- **Attention position is not free.** Material moved out of the system prompt and
  into the user turn is in a different position, and whether that changes how the
  model weighs it is not something this atlas has measured.
- **It only pays where caching does.** A local model, a provider without prefix
  caching, or sessions of one or two turns will not repay the restructuring.
- **Splitting has a floor.** If the "stable" block is itself regenerated by a
  nightly consolidation pass, the cache dies once a day rather than once a turn —
  better, but the boundary should be drawn where the regeneration happens, not
  where the taxonomy suggests.

## Seen in the atlas

- **[Hermes Agent](../../systems/hermes-agent/)** — the frozen snapshot, and the
  only system here whose memory *design* follows from the cache constraint.
- **[Memobase](../../systems/memobase/)** — the profile is injected at the front,
  which the report notes is friendlier to prefix caching than the alternative.
- **[Graphify](../../systems/graphify/)** — assembles context in a way the report
  contrasts explicitly with "invalidating a prefix cache on every request".
- **[Ollama](../../systems/ollama/)** — the index/body split, with a sorted
  catalog line in the prefix and the instruction body arriving as a tool result.
- **[Context Mode](../../systems/context-mode/)** — the boundary shape by
  accident of lifecycle: its `<session_knowledge>` block is emitted once at
  `SessionStart` and once at `PreCompact` and never re-rendered mid-session, so
  it lands in the cached prefix. Nothing in that tree says this was reasoned
  about, which is worth noting — it is the one arrangement here that could
  silently stop being true if a maintainer added a per-turn refresh.
- **[Helm](../../systems/helm/)**, **[CSM](../../systems/csm/)**,
  **[RisuAI](../../systems/risuai/)**, **[SillyTavern](../../systems/sillytavern/)**
  — the counter-examples, each invalidating on every turn.
- **[OpenCode](../../systems/opencode/)** — the contract-level version: a host
  whose only injection seam is the cache-sensitive one.

Note that [MemOS](../../systems/memos/)'s "activation memory: KV/prefix cache" is
a *different* mechanism — reusing model state rather than positioning text — and
falls under the KV-cache scope boundary in the
[comparative report](../../compare/).

## The same constraint, one layer down

Everything above is about where a *memory system* puts its recall block. The same
prefix property is being defended one layer below, at the proxy, by projects with
no memory at all — and one of them has written the argument out more carefully
than anything in this atlas.

[llmtrim](https://github.com/fkiene/llmtrim) is an MPL-2.0 compression proxy that
sits between a coding agent and its provider, examined on 2026-08-09 at
[`d7fd2c4e3ec4a9e354f98227546e3f75b5c0f1c6`](https://github.com/fkiene/llmtrim/commit/d7fd2c4e3ec4a9e354f98227546e3f75b5c0f1c6).
It gets no report here, because its store is in-process only, size-capped and
explicitly never written to disk — nothing survives the session, which is the
inclusion bar. `crates/llmtrim-core/src/memo.rs` is worth reading anyway, for
three reasons.

**It names the failure precisely, and the failure is caused by compression
itself.** Its stages are deterministic per request but read the whole
conversation, so *"the compressed form of an old message can change when a new
turn arrives. Two consecutive turns then serialize a divergent prefix → the
provider cache is busted → the product's headline savings leak silently on
exactly the highest-traffic (agent) shape."* That is the same silence the top of
this page describes — quality unaffected, tests pass, only the bill moves — found
in a system whose entire purpose is reducing the bill.

**It supplies the number this page otherwise cannot.** The module's opening cites
a 2026 measurement putting 85–95% of an agentic request's prompt tokens at
unchanged turn-to-turn. That is a claim about agent traffic rather than a cache
hit rate, and it is the reason the boundary's position matters so much for
exactly the shape memory systems serve.

**Its fix is the split-by-position shape applied to history rather than to
memory.** A cumulative 128-bit hash chain over the *original* bytes fingerprints
each message prefix; the longest run whose boundaries are all present in the store
is the frozen prefix, and its slots in the compressed output are overwritten with
the bytes emitted last turn. Appending a turn leaves every earlier boundary hash
unchanged; editing one byte of an old message invalidates that boundary and every
one after it — which is the prefix-cache semantics restated as a data structure.
Writes are first-write-wins, so a frozen message is never re-mutated.

Two details are worth stealing regardless of layer. The memo is *"an optimization,
never a correctness dependency"* — any doubt (a restructured message array, a cold
prefix, an unexpected count delta) falls back to full recomputation. And it
carves out the one stage where splicing is unsound: the n-gram stage assigns
placeholders from frequencies across the whole conversation, so reuse is disabled
whenever that stage is on, rather than reaching into the stage to freeze its
dictionary. A caching optimisation that knows which of its own components it
cannot safely apply to is rarer than it should be.

The same repository shows the other half of the trade. [headroom](https://github.com/headroomlabs-ai/headroom),
examined at
[`675d13f08d42455c8fa17bda878c1a11b905cee4`](https://github.com/headroomlabs-ai/headroom/commit/675d13f08d42455c8fa17bda878c1a11b905cee4),
implements what it calls CCR — Compress-Cache-Retrieve — where a dropped payload
is stashed in SQLite keyed by the hash that goes into the prompt, and a retrieval
tool call trades the hash back for the original: *"lossy on the wire, lossless
end-to-end."* It is a dereference table rather than a memory, and it is not
reported here for that reason, but the shape is the one a memory system reaches
for when a recalled item is too big to inject — put the handle in the prefix and
let the model ask for the body, which is what
[Ollama](../../systems/ollama/) does above with a name instead of a hash.

## Tests before relying on it

- Capture the exact bytes of two consecutive requests and diff them. The first
  differing byte is the cache boundary; assert it falls after the stable block.
- Assert a mid-session memory write does not change the system prompt, under the
  frozen shape — and that it *does* reach disk.
- Assert the stable block is byte-identical across turns, including ordering of
  anything assembled from a set or a dict.
- Under the bounded variant, assert a write that exceeds the cap is refused and
  returns the current entries, rather than silently truncating.
- Measure it. Every claim on this page is about a mechanism read in code; no
  system in this atlas publishes a cache hit rate, and the reports say so.

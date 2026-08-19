# One field asked two questions — split in Gortex, conflated in repowise

**Status:** design observation with two instances, one positive and one
negative; candidate for a pattern page.
**Origin:** Gortex's provenance ladder and repowise's grounding gate, read the
same day.

## The shape

A memory system stores a judgment about a stored fact — a tier, a status, a
confidence. The recurring defect is that the judgment gets consumed by more than
one caller asking *different questions*, and one value cannot answer both. It
either gets split deliberately, or it silently answers whichever question the
first caller had.

## Split, deliberately: Gortex

Every edge in the graph carries an `Origin` recording how it was resolved:
`lsp_resolved`, `lsp_dispatch`, `ast_resolved`, `ast_inferred`, `text_matched`.
Not how much it is believed — *how it was established*.

Two consumers, two mappings, and the ordering is not the same:

```
EdgeTierScore — is this edge real?      Centrality weight — should it confer authority?
  lsp_resolved   1.00                     ast_resolved   1.0   (the baseline)
  lsp_dispatch   0.95                     ast_inferred   0.8
  ast_resolved   0.90                     lsp tiers      0.6   (attenuated)
  ast_inferred   0.70                     text_matched   0.5
  text_matched   0.40
```

The compiler-grade tier is *highest* for belief and *discounted* for ranking.
The reasoning is written down: LSP providers materialise a dense layer of
framework-wiring and interface-dispatch edges, and counting every one at full
weight *"inflates the apparent centrality of utility and framework code over
genuine domain authorities."*

That is a real insight and I have not seen it elsewhere in the corpus:
**the most reliable evidence can be the most misleading, when it is also the most
abundant.** Reliability is a property of one edge. Authority is a property of a
distribution. A single confidence float cannot express both, and a system that
tries will rank its own utility module as the heart of the codebase.

The corollary is a design rule: when a stored judgment feeds both a *filter* and
a *ranking*, expect the two to need different curves, and give them separate
mappings rather than a shared threshold.

## Conflated, honestly: repowise

The counterpart, in a mechanism that is otherwise excellent.

`apply_substring_gate` requires every produced `decision`, `rationale` and
`source_quote` to substring- or token-match the verbatim source span its
producer recorded. Ungrounded fields are cleared. A candidate with nothing
grounded is rejected. Survivors are stamped `exact`, `fuzzy` or `unverified`.

Then:

> A candidate with no `source_text` (nothing to check against) is kept but left
> `unverified` — we never fabricate a rejection we cannot justify.

The instinct is right and I would keep it. But `unverified` now covers two
different situations:

- *I checked and nothing supported this.*
- *I could not check, because the producer recorded no span.*

The first is evidence about the claim. The second is evidence about the
**pipeline**. They call for opposite responses — distrust the memory, versus go
fix the extractor — and the schema cannot tell them apart, so neither can any
consumer and neither can a maintainer counting them.

The consequence is that the strength of the guarantee stops being a property of
the gate and becomes a property of every producer feeding it. A new extractor
that neglects to pass `source_text` silently downgrades the whole product claim
and nothing in the gate can notice, because the gate's own rule is to decline
that case.

The fix is one value: an `unchecked` distinct from `unverified`. It costs a
constant and it turns an invisible pipeline regression into a countable one.

## Why the two belong in one note

Gortex split a value because two *readers* wanted different things. repowise
merged two states because two *writers* produced the same one. Same underlying
error — a field carrying more than one question — approached from opposite ends,
and the test for both is the same:

**For every judgment field, enumerate its writers and its readers separately. If
either list has entries that would act differently on the same value, the field
is two fields.**

## For the atlas

Both instances are in the respective reports. If this becomes a pattern page it
should be argued as *reporting* on the Gortex half (a shipped mechanism with its
reasoning committed) and *advocacy* on the repowise half (a one-constant change
nobody has made). Those are different stances and the page would carry the
weaker one, so `mixed` is the honest label.

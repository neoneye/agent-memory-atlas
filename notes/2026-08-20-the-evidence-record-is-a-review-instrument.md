# Writing the evidence record is what audits the mark

**Status:** method finding. The `capability_evidence` block was added as
documentation and turns out to work better as a review step.
**Origin:** re-pinning MemMachine, where the mark had stood for three weeks and
writing its evidence record found the limit in one sitting.

## What the block was for

`capability_evidence` is four fields per mark — subsystem, file, symbol, test —
added so a reader can go and check a claim, and so a mark that guards one
subsystem cannot be read as guarding the whole system. That is a
*documentation* rationale, and it is a good one.

## What it actually does

It forces you to name the symbol.

MemMachine's `scope_enforced` mark had been carried since 29 July on a true
statement: `org_id`, `project_id` and `session_key` are threaded into storage
calls rather than merely stored, and the key is applied on the read path. That
is correct, it was verified, and it is exactly what the rubric asks.

The record needs the *symbol*. Naming it means opening `_generate_set_id` and
reading how the key is built:

```
mem_{set_type}_{org_project}_{n_tags}_{hash(tag_keys)}__{sorted_tags}
```

— where `org_project` is `org_{org_id}` or `org_{org_id}_project_{project_id}`,
composed by string interpolation. A set-type discriminator and a hash of the
metadata keys close collisions *between* types, which is real work and worth
crediting. Nothing closes a collision *within* a type, because the identifiers
go in unescaped between underscores: an org of `acme_project_x` with project `y`
composes the same set id as an org of `acme` with project `x_project_y`. No
validator for either identifier exists in the tree, and `org_id` arrives on the
MCP request model as a bare `str = Field(default="")`.

The mark still stands — what it certifies is that the key reaches the query, and
it does. What it does not certify is that the key is *injective*, and that is
now written in the report and the verdict.

## The mechanism

Three weeks of the mark being right, and one hour of writing four fields finding
its boundary. The reason is structural rather than lucky:

**Verifying a mark asks "is this claim true?" Writing its evidence record asks
"where exactly does this happen?"** The first question is answered by the
read-path filter existing. The second cannot be answered without opening the
function that builds the thing being filtered on, and that is one level deeper
than the mark's own definition ever requires you to go.

A capability rubric asks about a property. An evidence record asks about a
location. Locations are where properties turn out to be conditional.

## Why this generalizes past this repository

Any review scheme with a checklist has the same gap: the checklist item is
satisfiable from the outside, and the implementation is only visible from the
inside. Requiring a citation — file and symbol, not just a verdict — is a cheap
way to force the inside read without adding a rule about how deep to look. The
depth is a side effect of the format.

It is the same reason a bibliography catches an unread source. You can believe
you know what a paper says; you cannot write down its page number without
opening it.

## Consequences for the atlas

- **A re-pin that crosses the evidence cutoff is a re-audit of every mark, not a
  bookkeeping step.** MemMachine's `analyzed_at` moved past 2026-08-16, which
  required the record, which produced the finding. That is a good accident to
  make deliberate: the marks worth re-examining first are the ones with no
  record yet.
- **Coverage is a review backlog, not a documentation backlog.** 136 of 546
  marks carry a record. The remaining 410 are not undocumented so much as
  un-re-read, and the floor that stops coverage falling is therefore a ratchet
  on review depth rather than on prose.
- **Withheld marks deserve the same treatment.** The record explains why a mark
  *is* carried. Nothing yet forces a sentence explaining why one is not, and the
  tokenmizer re-read found a missing `negative_eval` precisely where no reason
  had ever been written down.

# The rubric definitions are in a tooltip

**Status:** proposed. Supersedes an earlier version of this note that claimed the
marks were absent from report pages; they are not, and the correction is recorded
at the bottom.
**Origin:** an outside review (Qwen, 2026-08-13) asked the atlas to *"define the
rubric — stop using a black box"*, having listed the seven mechanisms by name.

## What is on the page

`scripts/capability_strip.py` runs for every file under `content/systems/` and
emits, above the prose of each report:

- a legend — *"Carries **2** of 7 rubric mechanisms. Most systems here carry none
  or one (52%), and a dash means the mechanism was not found at this commit — not
  that the system needed it"*;
- seven chips, each marked `✓` or `—`, named in prose form: Tombstone, Trust
  state, Bi-temporal, Scope enforced, Mutation audit, Human review, Negative
  evals;
- the full rubric definition of each mechanism in that chip's `title` attribute.

That is more than the review credited and more than the earlier version of this
note claimed. The distinction the rubric exists to protect — *assessed and
carries none* versus *nobody looked* — is stated in the legend on every page.

**The definitions are the part that does not arrive.** A `title` attribute is a
hover tooltip. It is not read by a text extractor, does not appear in a printed
or piped copy of the page, does not survive Reader mode, is unreachable by
keyboard, and does nothing on a touch device. So a reader sees seven labels and
seven marks with no way to find out what earned one, which is the review's
complaint stated accurately — and it explains why the reviewer could name all
seven mechanisms and still call the grading criteria a black box.

## Proposal

**Make each chip a link to its own definition, and keep the tooltip.**

```html
<li class="cap-chip is-present" title="Explicit trust state — …">
  <a href="$root$/methodology/atlas-rubric/#trust-state">…</a>
</li>
```

Three details decide whether this is worth doing at all:

1. **The rubric needs stable per-mark anchors.** Its headings are prose, so the
   generated ids move when a heading is reworded. Explicit anchors — one per
   mechanism, named for the frontmatter key — make the link durable and let a
   report link a mark from its own prose, which several already want to do.
2. **Link the withheld marks too.** A reader who wants to know why a dash is a
   dash is asking the more interesting question, and the definition is the
   answer they need.
3. **Do not replace the tooltip.** It is the fastest path for a reader with a
   mouse and costs nothing to keep.

Cost: one `<a>` in `capability_strip.py`, anchors in the rubric, and a link check
that already runs (`test_site.sh` resolves every relative link and every
fragment). No new dependency, and unlike the tooltip it survives being read as
text — which, per
[the fourth review](2026-08-13-the-fourth-review-and-the-second-broken-diagram.md),
is how a growing share of this atlas is read.

## The correction

The first version of this note said the marks never reached the report page, on
the strength of:

```sh
rg -n 'trust_state|scope_enforced' docs/systems/mindcache/index.html
# no output
```

The strip renders the display names — `Trust state`, `Scope enforced` — not the
frontmatter keys, so the grep was scoped to strings the page never contains and
returned exactly what a real absence returns. That is the hazard
[methodology hazards](2026-07-28-methodology-hazards.md) records as the
best-evidenced failure of this review process, caught three times in one
assessment before, and it produced a published wrong claim here.

What would have caught it: the build script names `capability_strip.py` twelve
lines above the pandoc call, and the review being answered *quoted the seven
chip labels verbatim* — evidence the reviewer was looking at the strip while I
concluded it did not exist.

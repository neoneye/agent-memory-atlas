# When the system's own author sends a patch

**Status:** precedent, with the handling recorded so the next one is faster.
**Origin:** issue #18 and PR #19 on this repository, both from the maintainer of
PLUR1BUS, both asking the atlas to re-pin and rewrite its report on PLUR1BUS.

## What arrived

A re-pin request naming the published tag, a table of nine claims true at the
new commit and not at the old one, a list of limitations to *keep*, and a
"what not to claim" section. Then a PR implementing it: five files, +48/-48,
written in the report's own register, with a screening summary in the body.

It was careful, accurate about its own system, and unusually well-behaved. That
is what makes it worth writing a rule for — a bad contribution decides itself.

## What was already true

The report had been at the requested commit since the previous day, and most of
the table was already in it, generally in more detail: the `demoted` withhold
*with its covering test named*, the recorded reason `conflict` is left finite,
the epistemic axis with its three read-layer line numbers, and per-mark
`capability_evidence` records the PR does not carry and would have had to.

So the first question is never "is this right" but **"is this already there, and
in what state"**. Three of the nine rows were genuinely missing.

## What was missing, and how it went in

`/plur1bus curation resolve`, `/plur1bus curation drop-injected`, and a
`visibility` stamp on derived dream records. Each was read at the pin against
`index.js` and `lib/` — the authorization gate at `index.js:5867`, the dispatch
at `:6940` and `:6959`, the double bound in
`lib/drop-injected-conflicts.js:104`, the requester triple in `rem-dream.js` —
and then written in this atlas's voice, citing what was read here.

Not copied. Verified, then restated.

## Why the PR was closed rather than merged

Three reasons, in ascending order of importance.

1. **Stale baseline.** It was written against a commit `main` had moved past.
2. **It would not have parsed.** `scoping:` and `risks:` were indented three
   spaces where every sibling `matrix:` key uses two, which drops both out of
   the mapping. `check_frontmatter_keys.py` and the matrix generator catch it,
   but the point is that a well-made patch still carried a defect.
3. **The rule.** A report on a system, rewritten by that system's author, is
   exactly where the atlas has to read the code itself — **not because the
   description is wrong, but because a reader cannot tell afterwards.** The
   whole value of a pinned claim is that nobody has to trust anyone. Merging
   authored text spends that, and spends it invisibly.

## The rule, stated for reuse

- **An upstream report is a pointer, not a citation.** Same standing as an
  emailed tip: it tells you where to look.
- **Check what is already published first.** Most of a careful request is
  usually already there, and saying so specifically is what makes the reply
  useful rather than defensive.
- **Fold in what survives independent reading, in the atlas's voice, citing what
  was read here.** Credit the prompt in the History entry; do not adopt the
  prose.
- **Say why, publicly and without hedging.** Both threads got a comment naming
  the stale baseline, the indentation defect and the independent-reading
  principle, and an explicit statement that the limitations he asked to keep are
  kept.
- **Outward-facing acts get asked.** Committing the findings is standing
  authorization here; commenting on and closing another person's issue and PR is
  not, and was confirmed before posting.

## The thing worth saying out loud

The contributor was right that the report should move, right about what changed,
and right about which limitations still applied. He was also the last person
whose word the atlas can take for it. Both of those are true at once, and the
reply has to carry both or it reads as either credulous or dismissive.

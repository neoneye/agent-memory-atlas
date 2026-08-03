# The superlative audit, first pass — and the count sweep that hid two errors

**Status:** first pass done; the mechanically checkable subset is now checked and
four claims were wrong. The judgement subset is enumerated and untouched.
**Origin:** [hazard 10](2026-07-28-methodology-hazards.md), written 2026-08-04
after a superlative was published and retracted the previous day. This is the
pass that hazard proposed.

## What the pass found

`scripts/list_superlatives.py` reports 294 corpus-scoped superlatives. They are
not one population, and the split is the useful part.

**The mechanically checkable subset is small and was wrong.** Ten claims pair a
spelled number with a corpus denominator — "Four systems of one hundred and
thirty-six carry it". Each is answerable in one query against report frontmatter.
Checked against live capability counts at 136 reports:

| Claim | Location | Said | Live |
| --- | --- | --- | --- |
| tombstone | `patterns/index.md:306`, `rejected-value-tombstone.md:9` | four | **4** ✓ |
| negative retrieval assertion | `benchmarks.md:562` | sixteen | **17** ✗ |
| negative retrieval assertion | `capabilities.md:65` | sixteen | **17** ✗ |
| negative retrieval assertion | `overview.md:1541` | sixteen | **17** ✗ |
| bi-temporal validity | `systems/agent-memory-supabase.md:34` | nine | **10** ✗ |

Four of the seven real count claims were stale. All four are corrected.

**The judgement subset is the other 284** — "the most carefully reasoned
correction in the atlas", "the best-specified memory contract in this atlas".
These are not checkable by any query, and the honest response is not to verify
them but to stop phrasing them as though someone had. They are left alone in
this pass and listed by the script for whoever writes the next one.

## The part worth recording: the sweep hid the errors

Three reports were added on 2026-08-03 and 2026-08-04, taking the corpus from
133 to 136. Each addition failed `check_homepage.py` on a stale spelled count,
and each time the fix was a regex sweep bumping *"one hundred and thirty-three"*
to *"thirty-four"* to *"thirty-five"* to *"thirty-six"* across `content/`.

That sweep is mechanical, it satisfies the build, and **it edits the denominator
of sentences whose numerator nobody has checked.** After it runs, "Sixteen
repositories of one hundred and thirty-six" reads as a freshly-updated figure. It
is a stale numerator wearing a current denominator, and it is *more* misleading
than it was before the sweep, because the visible evidence of age is gone.

One of the four errors was caused this way and by me. The
[Hippo report](../content/systems/hippo-memory.md) added a `bitemporal` mark an
hour before this pass, taking the live count from nine to ten, while a sentence
in an unrelated report said "nine of one hundred and thirty-six" — a denominator
I had just bumped and a numerator I had just invalidated, in the same working
session, without either being connected to the other.

**The lesson is narrow and worth stating.** `check_homepage.py` guards the
denominator because the denominator is derivable from a file count. Nothing
guards the numerator, and the numerators are the interesting halves — they are
the atlas's headline findings, "four of one hundred and thirty-six carry a
tombstone" being the most-quoted sentence the project has.

## What to do next

1. **Extend `check_homepage.py`, or add a sibling, to the capability
   numerators.** Seven of them map exactly onto the seven rubric marks and are
   derivable from frontmatter, so they can be checked the same way the matrix is:
   parse the spelled number, parse the capability named nearby, compare with the
   live count. This is the only part of the 294 that a build can ever own, and
   leaving it manual is what produced four stale claims.
2. **Ban the blind count sweep.** When a report is added, the denominators and
   the numerators change together, and updating one without the other is worse
   than updating neither. The sweep should be replaced by a step that prints both
   figures and requires the writer to look.
3. **Re-phrase the judgement superlatives rather than verifying them.** "The most
   carefully reasoned correction in the atlas" should either become a claim about
   a mechanism, or say plainly that it is one reviewer's judgement across the
   corpus. Not started.

## What came of it

- **Four stale count claims corrected**, three of them the same negative-eval
  figure repeated across `benchmarks.md`, `capabilities.md` and `overview.md`.
- **One error traced to my own sweep an hour earlier**, which is the clearest
  demonstration available that the sweep is the wrong tool.
- **284 judgement superlatives enumerated and untouched**, with the reason.
- **A check specified and not written**, deliberately: the capability numerators
  are worth a build guard and the design belongs in the same pass as its
  implementation.

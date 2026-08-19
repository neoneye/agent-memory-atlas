# Measure the chrome before restyling it

**Status:** finding, plus one accessibility trap worth not stepping in twice.
**Origin:** *"the nav bar starts to get really crowded. Hide the 'Agent Memory
Atlas' logo text that takes up screen estate."*

## The complaint understated the bug

Measured on the rendered page rather than eyeballed: eleven nav items plus the
GitHub pill need **1,051px**, the brand needs **189px**, and the header has
**1,240px** — the content width. **Exactly zero slack at the widest layout.**

Below about 1,296px the header padding drops from `(100vw - 1240px)/2` to its
28px floor, so the available width becomes `viewport - 56` while the content
stays 1,240. At 1,100px the GitHub pill sat **75px past the viewport** and
`document.documentElement.scrollWidth > innerWidth` — the whole page scrolled
horizontally. The broken band ran from the 760px hamburger breakpoint up to
roughly 1,300px, which is most laptops.

"Crowded" was the symptom a reader could see. The bug was underneath it.

## Sizing the fix from the arithmetic

- Hiding the wordmark buys **160px** (148 of text plus a 12px gap). Not enough
  on its own: it moves the crossing point to about 1,136px.
- The nav gap was 32px across eleven gaps — **352px of pure gap**, a bigger
  lever than the wordmark. 32 → 22 buys another 110px.
- Still leaves a band, so the collapse-to-menu breakpoint moved from 760px to
  1,040px, because 965px of remaining row against `viewport - 56` crosses at
  1,021px.

Only the nav-collapse rules moved. The 760px block also holds the header shrink
and the memory figure's annotation-layer rules, which are about small screens
rather than about how many nav items there are, and they stayed.

## The accessibility trap

`.brand-mark` carries `aria-hidden="true"` — it is decorative. So the home
link's *entire* accessible name is the wordmark text. `display: none` on it
would have left a link with **no accessible name at all**, which is worse than
the crowding it fixed and invisible in a screenshot.

The fix is the visually-hidden pattern (`position: absolute; width: 1px;
clip: rect(0,0,0,0)`), which this stylesheet already had as `.sr-only`. Verified
after the change: the header link still reports "Agent Memory Atlas", and the
footer still renders it at full size.

## What to keep

1. **Measure the header before restyling it.** `brand.getBoundingClientRect()`,
   `nav.getBoundingClientRect()` and the computed padding give the real numbers
   in one call, and they turned a styling request into a bug report.
2. **Check `documentElement.scrollWidth > innerWidth` at several widths.** A
   sticky header that overflows takes the whole document with it, and it is easy
   to miss at the one width you happen to be testing.
3. **Before hiding text, ask what the element's accessible name is.** If a
   sibling is `aria-hidden`, the text is load-bearing.
4. **Nav pressure is item count.** 266px of slack at 1,440px is real headroom,
   and eleven top-level items is the underlying cause. The next honest fix is
   grouping — Rubric and Method are both methodology; Compare, Verdicts,
   Benchmarks and Capabilities are four views of one corpus — not more shaving.

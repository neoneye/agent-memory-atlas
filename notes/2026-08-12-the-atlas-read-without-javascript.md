# The atlas read without JavaScript — two confident criticisms, one root cause

**Status:** the delivery fix shipped on 2026-08-13 — every diagram is now
wrapped in a captioned figure with its source folded into a disclosure, guarded
by `scripts/check_diagram_captions.py`. Pre-rendering the SVG remains declined,
and the reason is below.
**Origin:** an outside review (Qwen, 2026-08-12) of
[`build.md`](../content/build.md), whose two structural findings were both wrong
in the same way. The diagnosis is worth more than the findings.

## What was reported

> **Broken UI/UX:** The page contains floating text artifacts like `no`, `yes`,
> `a test fails`, and `Does anything need to survive the session?`. This looks
> like a broken interactive decision tree or poorly implemented CSS/JS.

and

> **The "Ghost Documentation" Problem:** The page constantly references external
> documents that the reader cannot see … files like
> `.agents/protocol/build-brief.md`. Where are they?

## What is actually there

The floating text is the edge labels of the Mermaid flowchart at
`content/build.md:23`:

```text
Q["Does anything need to survive the session?"]
Q -->|"no"|  STOP["Build nothing. …"]
Q -->|"yes"| P["1 · Pick the profile …"]
T -->|"a test fails"| S
```

`scripts/build_site.sh` emits it as `<pre class="mermaid"><code>…`, and
`docs/*/index.html` renders it client-side:

```js
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
const diagrams = document.querySelectorAll("pre.mermaid");
```

The "ghost documentation" is three hyperlinks, each in the sentence that names
the artifact: `build-brief.md` at `build.md:81`, `§8 What I Would Build` at
`:91`, `tests.yaml` at `:134`.

So the page was consumed as text with links stripped and diagrams unrendered.
Neither finding is a property of the page.

## Why this is worth a note anyway

**A growing share of this atlas's readers execute no JavaScript.** Model-driven
readers, `curl | pandoc`, reader-mode extractors, and anything indexing the site
for retrieval all land on the same surface this reviewer did. And the exposure is
not one page: `scripts/check_mermaid.py` *requires* a diagram in every system
report, so all 264 report pages degrade into a block of raw `flowchart TD`
source for those readers — in the section that carries the mechanism.

**A second review reached the same wrong conclusion on a different page**, this
time reporting the PRO-LONG report's section 2 as "a table that has completely
lost its markdown rendering", quoting three of that diagram's edge labels. Two
independent readers opening with confident structural criticism that resolves to
*the diagram did not render* is a property of the delivery, not of either
reader — the argument is in
[the fourth review and the second broken diagram](2026-08-13-the-fourth-review-and-the-second-broken-diagram.md).

That is the opposite of what the diagram is for. A reader without JS gets the
worst of both: not a picture, and not prose either, because the prose was written
assuming the picture would carry the structure.

The second half is cheaper and more embarrassing: the links *are* in the HTML, so
a text extractor that drops anchors is discarding information the page provided.
Nothing can be done about a bad extractor — but a page whose argument survives
losing its links is more robust than one whose reviewer concludes the references
are missing.

## Proposal

Two changes, both small, in order of value.

**1. Pre-render the diagrams at build time — declined.** `package.json` has no
dependencies at all; `npm` is a task runner over bash and python here. Adding
`@mermaid-js/mermaid-cli` means adding puppeteer and a headless Chromium as this
repository's first Node dependency, to a build that currently installs nothing.
That trade buys a rendered diagram for a reader without JavaScript; the caption
buys them the claim the diagram makes, for no dependency. The proposal as
written: Add a build step that runs
`@mermaid-js/mermaid-cli` (or `mermaid` under a headless renderer) over each
`pre.mermaid` block and inlines the resulting SVG, keeping the source in a
`<details>` beside it. The client-side import then becomes a fallback rather than
the only path. Cost: one build dependency and a slower build. Benefit: every
report page carries its diagram to every reader, and the CDN import stops being a
single point of failure for the atlas's most-repeated visual element.

Constraint worth stating: this adds a Node dependency to a build that currently
has almost none, and the project's own screening rules treat new dependency
surfaces as something to decide on purpose. If that trade is unwelcome, do (2)
only.

**2. Give every diagram a one-line text alternative.** A `figcaption` or a
leading sentence stating what the diagram shows, so a reader who receives neither
SVG nor rendered source still gets the claim. This is worth doing regardless of
(1) — it is what the diagram is *for*, written down — and it is a content change,
not a build change.

**Not proposed:** removing the diagrams. The rule that every report carries one
drawn on the real mechanism has improved the reports, and the failure here is in
delivery, not in the decision.

## A check worth adding either way

`scripts/test_site.sh` could assert that no built page contains the literal
string `flowchart TD` or `stateDiagram-v2` **outside** a `pre.mermaid` block — a
one-line guard that would catch a diagram silently degrading to visible source if
the client-side path ever breaks. Today it would pass trivially, which is the
point: it pins the current behaviour rather than discovering it later from a
reader's confusion.

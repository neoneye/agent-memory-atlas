#!/usr/bin/env python3
"""Wrap each rendered Mermaid block in a labelled <figure>.

The diagrams render client-side, so a reader who executes no JavaScript — a
model, `curl | pandoc`, a reader-mode extractor, a retrieval indexer — receives
the diagram's *source* instead of the diagram. Two outside reviews have now read
that raw source as broken page layout and opened with it as their strongest
criticism, which is a fact about what this site delivers rather than about
either reader.

Pandoc emits ```mermaid fences as `<pre class="mermaid"><code>…</code></pre>`.
This rewrites each one to:

    <figure class="diagram">
      <figcaption>Diagram — what it shows</figcaption>
      <details class="diagram-source">
        <summary>Diagram source</summary>
        <pre class="mermaid"><code>…</code></pre>
      </details>
    </figure>

so the same bytes reach a text extractor as a captioned figure with its source
labelled and folded, rather than as loose edge labels. The client-side renderer
lifts the rendered diagram out of the <details> (see the script in
templates/document.html), so a reader with JavaScript sees no change.

The caption comes from a Mermaid comment on the diagram's own first line:

    %% caption: How a superseded decision leaves the read path

Mermaid ignores `%%` lines, so the caption costs nothing at render time and
travels with the diagram in the content file. Without one the figure still gets
a generic label — the structure is what fixes the misreading — and
`scripts/check_captions.py` counts how many are still generic.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

BLOCK = re.compile(
    r'<pre class="mermaid">\s*<code>(?P<body>.*?)</code>\s*</pre>',
    re.DOTALL,
)
CAPTION = re.compile(r'^\s*%%\s*caption:\s*(?P<text>.+?)\s*$', re.MULTILINE)

GENERIC = "the mechanism described on this page"


def wrap(markup: str) -> tuple[str, int, int]:
    """Return (markup, diagrams, generic_captions)."""
    diagrams = 0
    generic = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal diagrams, generic
        diagrams += 1
        body = match.group("body")
        # The body is HTML-escaped source; read the caption out of the escaped
        # text and escape it back, so an ampersand in a caption survives.
        found = CAPTION.search(html.unescape(body))
        if found:
            caption = html.escape(found.group("text"), quote=False)
        else:
            caption = GENERIC
            generic += 1
        return (
            '<figure class="diagram">'
            f'<figcaption class="diagram-caption">Diagram — {caption}</figcaption>'
            '<details class="diagram-source">'
            '<summary>Diagram source</summary>'
            f'{match.group(0)}'
            '</details>'
            '</figure>'
        )

    return BLOCK.sub(replace, markup), diagrams, generic


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: wrap_diagrams.py <rendered.html> [--count]", file=sys.stderr)
        return 2
    path = Path(argv[1])
    markup = path.read_text(encoding="utf-8")
    wrapped, diagrams, generic = wrap(markup)
    if "--count" in argv[2:]:
        print(f"{diagrams} {generic}")
        return 0
    if diagrams:
        path.write_text(wrapped, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

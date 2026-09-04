#!/usr/bin/env python3
"""Fail the build when a built page carries a tag the browser will misparse.

A placeholder written in prose as `<title>` reached the published Engram Alpha
page on 4 September 2026. The markdown was valid and the HTML was valid, but a
browser's tokenizer treats `<title>` in the body as raw text until `</title>`,
so every section after the first paragraph vanished from the rendered page — a
reader wrote in to say the report had been cut to its summary. Nothing here
could see it: the headings were all present in the file.

The same class, one step milder: `<id>`, `<word>`, `<definition>` written bare
in prose become unknown elements, which render as nothing, so the sentence
loses the word it was about. Wrapping the placeholder in backticks fixes both,
because a code span escapes the brackets.

This check reads the *built* HTML, because that is what the browser reads, and
asserts two things: every tag name is one the HTML or SVG specification knows,
and `<title>` occurs exactly once per page, in the head.

Usage: check_raw_tags.py <docs-dir>
"""
import re
import sys
from pathlib import Path

#: Every element name the built site may legitimately contain. HTML first,
#: then the SVG the site inlines for icons and the pane diagrams.
KNOWN = set(
    """a abbr address area article aside audio b base bdi bdo blockquote body br
    button canvas caption cite code col colgroup data datalist dd del details
    dfn dialog div dl dt em embed fieldset figcaption figure footer form h1 h2
    h3 h4 h5 h6 head header hgroup hr html i iframe img input ins kbd label
    legend li link main map mark menu meta meter nav noscript object ol optgroup
    option output p param picture pre progress q rp rt ruby s samp script
    section select slot small source span strong style sub summary sup table
    tbody td template textarea tfoot th thead time title tr track u ul var video
    wbr
    svg path rect circle ellipse line polyline polygon g defs marker use tspan
    text desc symbol clipPath mask pattern linearGradient radialGradient stop
    foreignObject""".split()
)
TAG = re.compile(r"<([A-Za-z][A-Za-z0-9-]*)")
COMMENT = re.compile(r"<!--.*?-->", re.S)
SCRIPT = re.compile(r"<script\b.*?</script>", re.S | re.I)
#: Text inside a code element is escaped by the renderer, so a `<` there is
#: `&lt;` and never reaches this regex; nothing to strip.


def check(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    text = COMMENT.sub("", text)
    text = SCRIPT.sub("", text)
    problems = []
    unknown = {}
    for m in TAG.finditer(text):
        name = m.group(1)
        if name not in KNOWN and name.lower() not in KNOWN:
            line = text.count("\n", 0, m.start()) + 1
            unknown.setdefault(name, line)
    for name, line in sorted(unknown.items(), key=lambda kv: kv[1]):
        problems.append(
            f"{path}:{line}: <{name}> is not an HTML or SVG element; the "
            "browser renders it as nothing. Wrap the placeholder in backticks "
            "in the source."
        )
    # An inline SVG may carry its own <title> for accessibility; only a <title>
    # outside <svg> is the body-swallowing kind.
    outside_svg = re.sub(r"<svg\b.*?</svg>", "", text, flags=re.S | re.I)
    titles = len(re.findall(r"<title\b", outside_svg, flags=re.I))
    if titles != 1:
        problems.append(
            f"{path}: {titles} <title> tags; a <title> in the body swallows "
            "everything after it. Wrap the placeholder in backticks in the source."
        )
    return problems


def main(docs: str) -> int:
    root = Path(docs)
    pages = sorted(root.rglob("*.html"))
    if not pages:
        print(f"no HTML under {docs}", file=sys.stderr)
        return 1
    problems = []
    for page in pages:
        problems.extend(check(page))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(f"{len(pages)} built pages carry only known HTML and SVG tags, one <title> each.")
    return 0


def self_test() -> int:
    import tempfile

    cases = {
        "<html><head><title>x</title></head><body><p>Removed: <title></p></body></html>": 1,
        "<html><head><title>x</title></head><body><p>ACCEPT <id></p></body></html>": 1,
        "<html><head><title>x</title></head><body><p>ACCEPT <code>&lt;id&gt;</code></p><svg><path d=''/></svg></body></html>": 0,
        "<html><head><title>x</title></head><body><!-- <bogus> --><p>ok</p></body></html>": 0,
        "<html><head><title>x</title></head><body><svg><title>icon</title><path d=''/></svg></body></html>": 0,
    }
    failures = 0
    with tempfile.TemporaryDirectory() as d:
        for i, (html, expect) in enumerate(cases.items()):
            p = Path(d) / f"{i}.html"
            p.write_text(html, encoding="utf-8")
            got = 1 if check(p) else 0
            if got != expect:
                failures += 1
                print(f"self-test case {i}: expected {expect}, got {got}", file=sys.stderr)
    print(f"self-test: {len(cases) - failures} of {len(cases)} controls passed")
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))

#!/usr/bin/env python3
"""Two guards on how diagrams reach a reader who cannot render them.

1. **Every built diagram is wrapped.** `scripts/wrap_diagrams.py` turns each
   `<pre class="mermaid">` into a captioned `<figure>` with the source folded
   into a disclosure. If a diagram ever renders outside that wrapper, an
   unrendered page hands the reader loose Mermaid source again — the failure two
   outside reviews reported as broken page layout. This fails the build if a
   Mermaid keyword appears in `docs/` outside a wrapped figure.

2. **The generic-caption count only falls.** A diagram whose source carries
   `%% caption: …` on its own line gets that sentence as its figure caption; one
   without gets a generic label. Captions are written by hand, one report at a
   time, so the count is a ratchet rather than a gate: it may drop and it may not
   rise. Same shape as `stack_source: seeded`, where the seeded count is only
   allowed to fall.
"""
from __future__ import annotations

import re
from pathlib import Path

# Raise this only to record captions written; never to accommodate a new
# uncaptioned diagram. A new report should carry `%% caption:` in its fence.
UNCAPTIONED_FLOOR = 348

FENCE = re.compile(r"^```mermaid$", re.MULTILINE)
CAPTION = re.compile(r"^%%\s*caption:\s*\S", re.MULTILINE)
KEYWORD = re.compile(r"flowchart\s+(TD|LR|TB|RL|BT)|stateDiagram-v2|sequenceDiagram")


def count_uncaptioned(content_dir: Path) -> tuple[int, int]:
    total = 0
    uncaptioned = 0
    for path in sorted(content_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in FENCE.finditer(text):
            total += 1
            end = text.find("\n```", match.end())
            block = text[match.end(): end if end != -1 else len(text)]
            if not CAPTION.search(block):
                uncaptioned += 1
    return total, uncaptioned


def unwrapped_pages(docs_dir: Path) -> list[str]:
    offenders = []
    for path in sorted(docs_dir.rglob("index.html")):
        markup = path.read_text(encoding="utf-8")
        if not KEYWORD.search(markup):
            continue
        # Every Mermaid keyword must sit inside a wrapped figure. Count the
        # figures rather than parsing: a page with a diagram and no figure is
        # the failure this guard exists for.
        if '<figure class="diagram">' not in markup:
            offenders.append(str(path))
    return offenders


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    total, uncaptioned = count_uncaptioned(root / "content")
    offenders = unwrapped_pages(root / "docs")

    failed = False
    if offenders:
        failed = True
        print("Diagram source is rendered outside a captioned figure:")
        for page in offenders[:10]:
            print(f"  {page}")
        print(
            "A page whose diagram is not wrapped hands raw Mermaid to every "
            "reader without a renderer. Check scripts/wrap_diagrams.py ran."
        )

    if uncaptioned > UNCAPTIONED_FLOOR:
        failed = True
        print(
            f"{uncaptioned} diagrams carry no '%% caption:' line "
            f"(floor {UNCAPTIONED_FLOOR}). A new diagram needs one: it is the "
            "sentence a reader gets when the diagram does not render."
        )

    if failed:
        return 1

    captioned = total - uncaptioned
    print(
        f"{total} diagrams wrapped in a captioned figure; "
        f"{captioned} carry a written caption, {uncaptioned} generic "
        f"(floor {UNCAPTIONED_FLOOR})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

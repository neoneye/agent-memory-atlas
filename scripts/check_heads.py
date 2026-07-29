#!/usr/bin/env python3
"""Assert the two hand-maintained <head> blocks agree on analytics and consent.

There is no shared header partial: `site/index.html` carries its own head and
every generated page gets `templates/document.html`. A comment in both says the
two must be kept in step, which is a manual invariant with nothing enforcing it.

What drift would cost is not a broken page. The block sets Consent Mode v2 to
deny everything until the reader chooses; if one head is updated and the other is
not, some pages set cookies before the reader decides and others do not, and the
difference is invisible on both. A site arguing for scope-before-ranking should
not have a privacy behaviour that depends on remembering to edit two files.

Compared on collapsed whitespace, so reindenting one head is not a failure.

Usage: check_heads.py <project-dir>
"""
import re
import sys
from pathlib import Path

HEADS = ("site/index.html", "templates/document.html")
START = "Google Analytics"
END = "gtag('config'"


def analytics_block(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    start = text.find(START)
    if start < 0:
        return None
    config = text.find(END, start)
    if config < 0:
        return None
    close = text.find("</script>", config)
    if close < 0:
        return None
    opening = text.rfind("<!--", 0, start)
    return re.sub(r"\s+", " ", text[opening : close + len("</script>")]).strip()


def main(root: str) -> int:
    blocks = {}
    for rel in HEADS:
        path = Path(root) / rel
        if not path.is_file():
            print(f"Missing head file: {rel}", file=sys.stderr)
            return 1
        block = analytics_block(path)
        if block is None:
            print(
                f"{rel}: no analytics/consent block found. If analytics was "
                f"removed deliberately, remove it from both heads and drop this "
                f"check.",
                file=sys.stderr,
            )
            return 1
        blocks[rel] = block

    first, second = HEADS
    if blocks[first] != blocks[second]:
        print(
            "The two hand-maintained <head> blocks have drifted:", file=sys.stderr
        )
        print(f"  {first}", file=sys.stderr)
        print(f"  {second}", file=sys.stderr)
        print(
            "Consent Mode is set in both; a difference means some pages honour "
            "the reader's choice and others do not. Copy one over the other.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

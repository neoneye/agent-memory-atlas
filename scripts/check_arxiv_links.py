#!/usr/bin/env python3
"""Assert every `arXiv:ID` in published prose is a link.

A bare `arXiv:2604.15774` is a dead end for a reader: it names a paper and makes
them retype an identifier to find it. The atlas cites papers constantly — as the
subject of an exclusion entry, as the evidence behind a benchmark claim, as the
thing a report's section 10 is checked against — and the citation is only worth
the space when it is one click from the abstract.

This ran as a one-off sweep on 2026-08-30 that linked sixteen bare mentions
across seven files; it exists so the sweep does not have to happen again. Every
mention already inside a markdown link is left alone, whatever the link text, so
`[the paper](https://arxiv.org/abs/ID)` and `[arXiv:ID](…)` both pass.

Checks `content/` (the published site) and `notes/` (which is not built, but is
linked from published pages and read on GitHub).

Usage: check_arxiv_links.py <project-dir>
"""
import re
import sys
from pathlib import Path

MENTION = re.compile(r"arXiv:\d{4}\.\d{4,5}(v\d+)?", re.I)
#: Any markdown link whose *text* contains the mention — the form this enforces —
#: plus any link at all, since a mention inside link text is by definition linked.
LINKED = re.compile(r"\[[^\]]*arXiv:\d{4}\.\d{4,5}[^\]]*\]\([^)]*\)", re.I)

ROOTS = ("content", "notes")


def main(root: str) -> int:
    project = Path(root)
    problems: list[str] = []
    checked = 0

    for name in ROOTS:
        base = project / name
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            spans = [m.span() for m in LINKED.finditer(text)]
            for m in MENTION.finditer(text):
                checked += 1
                if any(a <= m.start() and m.end() <= b for a, b in spans):
                    continue
                line = text.count("\n", 0, m.start()) + 1
                ident = m.group(0).split(":", 1)[1].split("v")[0]
                problems.append(
                    f"{path.relative_to(project)}:{line}: bare {m.group(0)} — "
                    f"link it: [{m.group(0)}](https://arxiv.org/abs/{ident})"
                )

    if problems:
        print("arXiv identifiers cited without a link:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1

    print(f"{checked} arXiv citations, every one linked.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

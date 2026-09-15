#!/usr/bin/env python3
"""Corpus counts written as placeholders in the source, filled in at build time.

Prose that states a corpus count writes a token instead of a number:

    PLACEHOLDER_PATTERN_TOMBSTONE_COUNT systems of PLACEHOLDER_TOTAL_COUNT carry a tombstone.

`npm run build` replaces every token in the rendered site with the live count,
derived from report frontmatter. A count written this way cannot go stale, so
adding a report or moving a mark no longer means sweeping the prose for the old
number — and the checkers no longer need to recognise spelled-out numbers to
catch the sentences that did.

Usage:
    placeholders.py --list          print every token and its current value
    placeholders.py --fill DIR      substitute tokens in DIR/**/*.html in place
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_matrix import CAPABILITIES, read_capabilities  # noqa: E402

TOKEN = re.compile(r"PLACEHOLDER_[A-Z0-9_]+")
SOURCE = re.compile(r"^source_url:\s*(\S+)\s*$", re.M)


def mark_token(flag: str) -> str:
    return f"PLACEHOLDER_PATTERN_{flag.upper()}_COUNT"


def counts(root: Path = ROOT) -> dict[str, int]:
    """Every placeholder the source may use, mapped to its live value."""
    reports = sorted((root / "content" / "systems").glob("*.md"))
    marks = {flag: 0 for flag, _, _ in CAPABILITIES}
    sources: set[str] = set()
    carrying = 0
    for path in reports:
        flags = read_capabilities(path) or set()
        carrying += bool(flags)
        for flag in flags:
            marks[flag] += 1
        found = SOURCE.search(path.read_text(encoding="utf-8"))
        if found:
            sources.add(found.group(1).strip('"').rstrip("/"))
    patterns = [p for p in (root / "content" / "patterns").glob("*.md") if p.stem != "index"]
    values = {
        "PLACEHOLDER_TOTAL_COUNT": len(reports),
        "PLACEHOLDER_REPOSITORY_COUNT": len(sources),
        "PLACEHOLDER_DESIGN_PATTERN_COUNT": len(patterns),
        "PLACEHOLDER_MARKED_SYSTEM_COUNT": carrying,
    }
    values.update({mark_token(flag): n for flag, n in marks.items()})
    return values


def fill(text: str, values: dict[str, int]) -> tuple[str, list[str]]:
    """Substitute known tokens; return the text and any unknown tokens left."""
    unknown: list[str] = []

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if token in values:
            return str(values[token])
        unknown.append(token)
        return token

    return TOKEN.sub(replace, text), unknown


def fill_tree(directory: Path, values: dict[str, int]) -> int:
    problems: list[str] = []
    for page in sorted(directory.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        if "PLACEHOLDER_" not in text:
            continue
        filled, unknown = fill(text, values)
        page.write_text(filled, encoding="utf-8")
        problems.extend(f"{page.relative_to(directory)}: unknown token {t}" for t in sorted(set(unknown)))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


def main() -> int:
    args = sys.argv[1:]
    values = counts()
    if args[:1] == ["--list"]:
        for token, value in values.items():
            print(f"{token} = {value}")
        return 0
    if args[:1] == ["--fill"] and len(args) == 2:
        return fill_tree(Path(args[1]), values)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

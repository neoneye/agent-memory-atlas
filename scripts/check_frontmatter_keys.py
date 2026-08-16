#!/usr/bin/env python3
"""Fail on a duplicate key in a page's YAML frontmatter.

YAML resolves a duplicate key by keeping the last one, silently. Pandoc notices
and prints `Duplicate key: ['capability_evidence']` as a *warning*, then builds
the page anyway — so the site renders, `npm test` passes, and the losing block is
gone with nothing in the output to say it existed.

That is the shape this repository cares about most: the report still looks
complete, and the evidence records or matrix values in the discarded block are
not missing in a way anyone can see. It happened when a re-analysis added a
second `capability_evidence:` above the one already there; the older block —
naming the covering test for a mark — lost, and only the pandoc warning scrolling
past in a build log recorded it.

What this checks, per file: the frontmatter block, at the top level and one level
of nesting in. One level is enough because that is where `matrix:` and
`capability_evidence:` hold their keys, and it is where a hand-merged block puts
a second `tombstone:` or `storage:`.

Deliberately not a YAML parser. It reads the block line by line so it can report
*both* line numbers, which is what makes the failure actionable — a parser hands
back the survivor and forgets where the other one was.

Usage: check_frontmatter_keys.py [root] [--self-test]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

#: A mapping key at column 0 (`title:`) or indented under one (`  tombstone:`).
#: The value may be empty — `matrix:` opens a block and has no value of its own.
KEY = re.compile(r"^(?P<indent> *)(?P<key>[A-Za-z_][\w.-]*)\s*:(?: |$)")

#: Two spaces is the nesting this repository writes. A deeper line is inside a
#: multi-line scalar or a list item, where a repeated word is text rather than a
#: key, so it is left alone.
NESTED_INDENT = 2


def duplicates(text: str) -> list[tuple[str, int, int, str]]:
    """(key, first line, second line, parent) for every repeat in the block."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return []
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return []

    found: list[tuple[str, int, int, str]] = []
    seen: dict[tuple[str, str], int] = {}
    parent = ""
    for index in range(1, end):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = KEY.match(line)
        if not match:
            continue
        indent = len(match.group("indent"))
        key = match.group("key")
        if indent == 0:
            parent = key
        elif indent != NESTED_INDENT:
            continue  # deeper than one level: inside a scalar or a list
        scope = (parent if indent else "", key)
        if scope in seen:
            found.append((key, seen[scope] + 1, index + 1, parent if indent else ""))
        else:
            seen[scope] = index
    return found


def check(root: Path) -> int:
    problems = []
    for path in sorted((root / "content").rglob("*.md")):
        for key, first, second, parent in duplicates(path.read_text(encoding="utf-8")):
            where = f"{parent}.{key}" if parent else key
            problems.append(
                f"{path.relative_to(root)}: duplicate frontmatter key '{where}' "
                f"at lines {first} and {second}. YAML keeps the last one and drops "
                "the first without failing — merge them by hand."
            )
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print("no duplicate frontmatter keys.")
    return 0


def self_test() -> int:
    """A validator that cannot fail is not a validator."""
    cases = [
        ("---\ntitle: A\ncapabilities: \"x\"\n---\n", 0, "clean frontmatter passes"),
        ("---\ntitle: A\ncapability_evidence:\n  tombstone: \"a | b | c | d\"\n"
         "stack_source: \"reviewed\"\ncapability_evidence:\n  trust_state: \"a | b | c | d\"\n---\n",
         1, "a repeated top-level key fails"),
        ("---\ntitle: A\nmatrix:\n  storage: \"one\"\n  storage: \"two\"\n---\n",
         1, "a repeated nested key fails"),
        ("---\ntitle: A\nmatrix:\n  storage: \"one\"\ncapability_evidence:\n  storage: \"two\"\n---\n",
         0, "the same key under two different parents is not a duplicate"),
        ("---\ntitle: A\ndescription: \"a line: with a colon\"\n---\n", 0,
         "a colon inside a quoted value is not a key"),
        ("# no frontmatter\n\ntitle: A\ntitle: B\n", 0,
         "body text outside a frontmatter block is not checked"),
    ]
    failures = []
    for text, expected, label in cases:
        actual = 1 if duplicates(text) else 0
        if actual != expected:
            failures.append(f"{label}: expected {expected}, got {actual}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main() -> int:
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--self-test" in flags:
        return self_test()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else Path(__file__).resolve().parent.parent
    return check(root)


if __name__ == "__main__":
    raise SystemExit(main())

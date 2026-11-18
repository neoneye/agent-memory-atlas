#!/usr/bin/env python3
"""Fail on a merge-conflict marker left in a hand-written file.

On 2026-11-18 a cherry-pick of a re-read conflicted in `content/appendix.md`,
where two branches had edited neighbouring lines of the repositories-inspected
list. The pick was piped through `tail`, so its failure was invisible, and the
build and every check in `test_site.sh` passed with the markers in the file:
the list is prose, a marker line is a valid paragraph, and both sides of the
conflict were well-formed entries the other checks accepted. The markers
reached the published appendix.

A marker is a line that starts with seven `<`, seven `>` or seven `|`, then a
space or the end of the line. A line of seven `=` alone is also Markdown's
setext heading underline, so it is reported only between an opening and a
closing marker, never on its own.

The scan covers the hand-written trees and skips `docs/`, which the build
generates from them: a marker there has a source here.

Usage: check_conflict_markers.py <project-dir> [--self-test]
"""

import re
import sys
from pathlib import Path

ROOTS = ("content", "site", "notes", "scripts", ".agents", "scout")
TOP_LEVEL = ("*.md", "*.json", "*.yaml", "*.yml", "*.toml")
SUFFIXES = {".md", ".html", ".json", ".yaml", ".yml", ".py", ".sh", ".js",
            ".css", ".txt", ".toml", ".svg", ".xml"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", "docs"}

# Built from parts so this file does not carry the markers it looks for.
OPEN, BASE, CLOSE, MIDDLE = ("<" * 7, "|" * 7, ">" * 7, "=" * 7)
EDGE = re.compile(rf"^({re.escape(OPEN)}|{re.escape(BASE)}|{re.escape(CLOSE)})( |$)")


def files(root: Path):
    for name in ROOTS:
        base = root / name
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in SUFFIXES and not (SKIP_DIRS & set(path.relative_to(root).parts)):
                yield path
    for pattern in TOP_LEVEL:
        yield from (p for p in root.glob(pattern) if p.is_file())


def scan(path: Path) -> list[int]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return []
    hits, inside = [], False
    for number, line in enumerate(lines, 1):
        edge = EDGE.match(line)
        if edge:
            hits.append(number)
            inside = edge.group(1) != CLOSE
        elif inside and line.rstrip() == MIDDLE:
            hits.append(number)
    return hits


def check(root: Path) -> tuple[list[str], int]:
    problems, seen = [], 0
    for path in sorted(set(files(root))):
        seen += 1
        for number in scan(path):
            problems.append(f"{path.relative_to(root)}:{number}")
    return problems, seen


def self_test() -> int:
    """Prove the check can still fail, on a tree built to fail it."""
    import tempfile

    conflict = f"a\n{OPEN} HEAD\nours\n{MIDDLE}\ntheirs\n{CLOSE} 26c7bff... subject\nb\n"
    diff3 = f"{OPEN} HEAD\nours\n{BASE} base\nold\n{MIDDLE}\ntheirs\n{CLOSE} x\n"
    controls = [
        ("conflict in content", "content/appendix.md", conflict, True),
        ("diff3 conflict in a script", "scripts/x.py", diff3, True),
        ("bare opening marker", "notes/n.md", f"{OPEN}\n", True),
        ("conflict in site html", "site/index.html", conflict, True),
        ("setext underline is fine", "content/x.md", f"Title\n{MIDDLE}\n\ntext\n", False),
        ("arrows in prose are fine", "content/y.md", "a <<<<<<< b\nx >>>>>>>y\n", False),
        ("generated docs are skipped", "docs/index.html", conflict, False),
        ("clean file", "content/z.md", "nothing to see\n", False),
    ]
    failures = 0
    for label, rel, body, should_fail in controls:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / rel
            target.parent.mkdir(parents=True)
            target.write_text(body, encoding="utf-8")
            got = bool(check(Path(tmp))[0])
            if got != should_fail:
                print(f"self-test FAILED: {label} expected fail={should_fail}, got {got}")
                failures += 1
    print(f"self-test: {len(controls) - failures} of {len(controls)} controls passed")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    problems, seen = check(root)
    if problems:
        print("merge-conflict markers left in hand-written files:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        print("Resolve the conflict, then rebuild; docs/ is regenerated from these files.", file=sys.stderr)
        return 1
    print(f"no merge-conflict markers in {seen} hand-written files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

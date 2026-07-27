#!/usr/bin/env python3
"""Generate the comparative matrix from per-system frontmatter.

The matrix used to be hand-maintained inside content/overview.md, which meant
every new system required editing a forty-row table by hand. Each system report
now carries its own row under a `matrix:` key in its frontmatter, and this
script renders the table. Run via `npm run build`; `npm test` checks the
generated table is in sync.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEMS = ROOT / "content" / "systems"
OVERVIEW = ROOT / "content" / "overview.md"

BEGIN = "<!-- BEGIN GENERATED MATRIX -->"
END = "<!-- END GENERATED MATRIX -->"

# (frontmatter key, column header)
COLUMNS = [
    ("memory_unit", "Memory unit"),
    ("storage", "Storage backend"),
    ("retrieval", "Retrieval strategy"),
    ("write", "Write strategy"),
    ("update_delete", "Update/delete model"),
    ("scoping", "Scoping model"),
    ("integration", "Agent integration"),
    ("background", "Background processing"),
    ("trust", "Trust/provenance model"),
    ("strengths", "Notable strengths"),
    ("risks", "Main risks"),
]

_MATRIX_LINE = re.compile(r'^\s{2}([a-z_]+):\s*"(.*)"\s*$')


def read_matrix(path: Path) -> dict[str, str] | None:
    """Extract the `matrix:` mapping from a report's YAML frontmatter."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    if end == -1:
        return None
    front = text[4:end]

    fields: dict[str, str] = {}
    in_matrix = False
    for line in front.splitlines():
        if line.startswith("matrix:"):
            in_matrix = True
            continue
        if in_matrix:
            match = _MATRIX_LINE.match(line)
            if not match:
                break
            key, value = match.groups()
            fields[key] = value.replace('\\"', '"').replace("\\\\", "\\")
    return fields or None


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|")


def build_table() -> str:
    rows: list[str] = []
    problems: list[str] = []

    for path in sorted(SYSTEMS.glob("*.md")):
        slug = path.stem
        fields = read_matrix(path)
        if fields is None:
            problems.append(f"{slug}: no matrix block in frontmatter")
            continue
        missing = [key for key, _ in COLUMNS if key not in fields]
        if missing:
            problems.append(f"{slug}: missing {', '.join(missing)}")
            continue
        cells = [escape_cell(fields[key]) for key, _ in COLUMNS]
        rows.append("| `" + slug + "` | " + " | ".join(cells) + " |")

    if problems:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        raise SystemExit(1)

    header = "| Repo | " + " | ".join(label for _, label in COLUMNS) + " |"
    divider = "|---" * (len(COLUMNS) + 1) + "|"
    return "\n".join([header, divider, *rows])


def main() -> int:
    table = build_table()
    text = OVERVIEW.read_text(encoding="utf-8")

    if BEGIN not in text or END not in text:
        print(
            f"error: overview.md is missing the {BEGIN} / {END} markers",
            file=sys.stderr,
        )
        return 1

    start = text.index(BEGIN) + len(BEGIN)
    stop = text.index(END)
    updated = text[:start] + "\n" + table + "\n" + text[stop:]

    if updated == text:
        print("Matrix already up to date.")
        return 0

    if "--check" in sys.argv:
        print(
            "error: generated matrix is out of date. Run 'npm run build'.",
            file=sys.stderr,
        )
        return 1

    OVERVIEW.write_text(updated, encoding="utf-8")
    print(f"Regenerated comparative matrix ({table.count(chr(10)) - 1} systems).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

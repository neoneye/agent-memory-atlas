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
CAP_BEGIN = "<!-- BEGIN GENERATED CAPABILITIES -->"
CAP_END = "<!-- END GENERATED CAPABILITIES -->"

# The free-text matrix answers "what does this system do". It does not answer
# "which systems actually have X", which is the question a reader arrives with.
# Each report declares the decisive capabilities it carries; absence of a flag
# means the mechanism was not found at the pinned commit, not that it cannot
# exist. Definitions are deliberately strict — a near-miss does not count, and
# the near-misses are the interesting part, so they are named in the prose.
CAPABILITIES = [
    ("tombstone", "Rejected-value tombstone",
     "A durable record of a *rejected value*, keyed on the value, so later "
     "extraction cannot silently re-assert it."),
    ("trust_state", "Explicit trust state",
     "Discrete epistemic status — at least candidate versus verified versus "
     "rejected — as a field, not a confidence score."),
    ("bitemporal", "Bi-temporal validity",
     "When a fact was true tracked separately from when the system recorded "
     "or expired it."),
    ("scope_enforced", "Scope enforced in retrieval",
     "A stored scope key (user, project, agent, tenant) applied as a filter "
     "on the read path, not merely available as a tag."),
    ("audit_log", "Append-only mutation audit",
     "An explicit event or audit record of memory mutations in the system's "
     "own store."),
    ("human_review", "Human review surface",
     "A place where a person inspects, approves, or adjudicates memory "
     "content before or after it takes effect."),
    ("negative_eval", "Negative retrieval assertion",
     "Committed evaluation cases asserting that particular material must "
     "*not* be retrieved."),
]

_CAP_LINE = re.compile(r'^capabilities:\s*"(.*)"\s*$')

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


def read_capabilities(path: Path) -> set[str]:
    """Extract the `capabilities:` flag list from a report's frontmatter."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return set()
    end = text.find("\n---\n", 3)
    if end == -1:
        return set()
    for line in text[4:end].splitlines():
        match = _CAP_LINE.match(line)
        if match:
            return {flag.strip() for flag in match.group(1).split(",") if flag.strip()}
    return set()


def build_capabilities() -> str:
    paths = sorted(SYSTEMS.glob("*.md"))
    carried = {path.stem: read_capabilities(path) for path in paths}

    known = {flag for flag, _, _ in CAPABILITIES}
    unknown = {f for flags in carried.values() for f in flags} - known
    if unknown:
        print(f"error: unknown capability flags: {sorted(unknown)}", file=sys.stderr)
        raise SystemExit(1)

    total = len(paths)
    blocks: list[str] = []
    for flag, label, definition in CAPABILITIES:
        holders = sorted(slug for slug, flags in carried.items() if flag in flags)
        listing = ", ".join(f"[`{slug}`](../systems/{slug}/)" for slug in holders)
        blocks.append(
            f"**{label}** — {definition}\n\n"
            f"*{len(holders)} of {total}:* {listing or 'none found'}"
        )
    return "\n\n".join(blocks)


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


def splice(text: str, begin: str, end: str, body: str, label: str) -> str:
    if begin not in text or end not in text:
        print(f"error: overview.md is missing the {begin} / {end} markers", file=sys.stderr)
        raise SystemExit(1)
    start = text.index(begin) + len(begin)
    stop = text.index(end)
    return text[:start] + "\n" + body + "\n" + text[stop:]


def main() -> int:
    table = build_table()
    capabilities = build_capabilities()
    text = OVERVIEW.read_text(encoding="utf-8")

    updated = splice(text, BEGIN, END, table, "matrix")
    updated = splice(updated, CAP_BEGIN, CAP_END, capabilities, "capabilities")

    if updated == text:
        print("Matrix and capability index already up to date.")
        return 0

    if "--check" in sys.argv:
        print(
            "error: generated matrix/capability index is out of date. Run 'npm run build'.",
            file=sys.stderr,
        )
        return 1

    OVERVIEW.write_text(updated, encoding="utf-8")
    print(f"Regenerated comparative matrix ({table.count(chr(10)) - 1} systems) and capability index.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
from html import escape as html_escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEMS = ROOT / "content" / "systems"
OVERVIEW = ROOT / "content" / "overview.md"

BEGIN = "<!-- BEGIN GENERATED MATRIX -->"
END = "<!-- END GENERATED MATRIX -->"
CAP_BEGIN = "<!-- BEGIN GENERATED CAPABILITIES -->"
CAP_END = "<!-- END GENERATED CAPABILITIES -->"
GRID_BEGIN = "<!-- BEGIN GENERATED CAPABILITY GRID -->"
GRID_END = "<!-- END GENERATED CAPABILITY GRID -->"
CAPABILITIES_PAGE = ROOT / "content" / "capabilities.md"

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
     "Discrete epistemic status as a field rather than a confidence score, "
     "including at least one state that withholds a memory from being treated "
     "as true."),
    ("bitemporal", "Bi-temporal validity",
     "When a fact was true tracked separately from when the system recorded "
     "or expired it."),
    ("scope_enforced", "Scope enforced in retrieval",
     "A stored scope key (user, project, agent, tenant) applied as a filter "
     "on the read path, not merely available as a tag."),
    ("audit_log", "Append-only mutation audit",
     "A named append-only event record of memory *mutations* in the system's "
     "own store. Logs of retrieval or feedback are the other half of the "
     "pattern and do not count here, nor does git history."),
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


def read_capabilities(path: Path) -> set[str] | None:
    """Extract the `capabilities:` flag list from a report's frontmatter.

    Returns None when the key is absent. That is deliberately distinct from an
    empty list: `capabilities: ""` says the report was assessed and carries none
    of the mechanisms, while a missing key says nobody looked. The index would
    render both as "not present", so the second is an error rather than a
    silent zero.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    if end == -1:
        return None
    for line in text[4:end].splitlines():
        match = _CAP_LINE.match(line)
        if match:
            return {flag.strip() for flag in match.group(1).split(",") if flag.strip()}
    return None


PLACEHOLDER_BODY = "<!-- Replace with code-grounded analysis. -->"


def find_placeholder_reports() -> list[str]:
    """Reports still carrying scaffolder placeholder sections."""
    return sorted(
        path.stem
        for path in SYSTEMS.glob("*.md")
        if PLACEHOLDER_BODY in path.read_text(encoding="utf-8")
    )


def build_capabilities() -> str:
    paths = sorted(SYSTEMS.glob("*.md"))
    carried = {path.stem: read_capabilities(path) for path in paths}

    undeclared = sorted(slug for slug, flags in carried.items() if flags is None)
    if undeclared:
        for slug in undeclared:
            print(
                f'error: {slug}: no `capabilities:` key. Declare the flags it '
                f'carries, or `capabilities: ""` if none.',
                file=sys.stderr,
            )
        raise SystemExit(1)

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


SHORT_LABELS = {
    "tombstone": "Tombstone",
    "trust_state": "Trust state",
    "bitemporal": "Bi-temporal",
    "scope_enforced": "Scope",
    "audit_log": "Audit",
    "human_review": "Review",
    "negative_eval": "Neg. evals",
}


def read_title(path: Path) -> str:
    """The display title from a report's frontmatter."""
    match = re.search(r'^title:\s*"?(.+?)"?\s*$', path.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else path.stem


def build_capability_grid() -> str:
    """A filterable systems x capabilities table for the standalone page.

    Emitted as HTML rather than a Markdown table because each row carries the
    capability set as a data attribute, which is what the filter reads. Pandoc
    passes raw HTML through untouched.
    """
    paths = sorted(SYSTEMS.glob("*.md"))
    head = "".join(
        f'<th scope="col" title="{html_escape(definition)}">{SHORT_LABELS[flag]}</th>'
        for flag, _, definition in CAPABILITIES
    )
    rows = []
    for path in paths:
        carried = read_capabilities(path) or set()
        cells = "".join(
            (
                '<td class="cap-yes" aria-label="yes">&#10003;</td>'
                if flag in carried
                else '<td class="cap-no" aria-label="no">&mdash;</td>'
            )
            for flag, _, _ in CAPABILITIES
        )
        rows.append(
            f'<tr data-capabilities="{" ".join(sorted(carried))}" data-name="{html_escape(read_title(path).lower())}">'
            f'<th scope="row"><a href="../systems/{path.stem}/">{html_escape(read_title(path))}</a></th>'
            f"{cells}<td class=\"cap-count\">{len(carried)}</td></tr>"
        )
    # No wrapper here: build_site.sh wraps every <table> in .table-wrap, and a
    # second wrapper produced two "expand to full width" toggles.
    return (
        '<table class="capability-grid">'
        f'<thead><tr><th scope="col">System</th>{head}<th scope="col">of 7</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody>'
        "</table>"
    )


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
        # The scaffolder emits the block with empty values, so key presence
        # alone would let an unfinished draft build and publish as a row of
        # blanks. Require a value, and reject the placeholder text too.
        blank = [key for key, _ in COLUMNS if not fields[key].strip()]
        if blank:
            problems.append(f"{slug}: empty matrix values: {', '.join(blank)}")
            continue
        placeholder = [key for key, _ in COLUMNS if "TODO" in fields[key]
                       or "Replace with" in fields[key]]
        if placeholder:
            problems.append(f"{slug}: placeholder matrix values: {', '.join(placeholder)}")
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
    drafts = find_placeholder_reports()
    if drafts:
        for slug in drafts:
            print(
                f"error: {slug}: still contains scaffolder placeholder sections. "
                "Finish the report or keep the draft outside content/systems/.",
                file=sys.stderr,
            )
        return 1

    table = build_table()
    capabilities = build_capabilities()
    text = OVERVIEW.read_text(encoding="utf-8")

    updated = splice(text, BEGIN, END, table, "matrix")
    updated = splice(updated, CAP_BEGIN, CAP_END, capabilities, "capabilities")

    grid_text = CAPABILITIES_PAGE.read_text(encoding="utf-8")
    grid_updated = splice(grid_text, GRID_BEGIN, GRID_END, build_capability_grid(), "grid")

    if updated == text and grid_updated == grid_text:
        print("Matrix, capability index and grid already up to date.")
        return 0

    if "--check" in sys.argv:
        print(
            "error: generated matrix/capability index is out of date. Run 'npm run build'.",
            file=sys.stderr,
        )
        return 1

    OVERVIEW.write_text(updated, encoding="utf-8")
    CAPABILITIES_PAGE.write_text(grid_updated, encoding="utf-8")
    print(
        f"Regenerated comparative matrix ({table.count(chr(10)) - 1} systems), "
        "capability index and capability grid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

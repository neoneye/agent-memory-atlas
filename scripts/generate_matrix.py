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
CONTENT = ROOT / "content"
SYSTEMS = CONTENT / "systems"
OVERVIEW = ROOT / "content" / "overview.md"

BEGIN = "<!-- BEGIN GENERATED MATRIX -->"
END = "<!-- END GENERATED MATRIX -->"
CAP_BEGIN = "<!-- BEGIN GENERATED CAPABILITIES -->"
CAP_END = "<!-- END GENERATED CAPABILITIES -->"
GRID_BEGIN = "<!-- BEGIN GENERATED CAPABILITY GRID -->"
GRID_END = "<!-- END GENERATED CAPABILITY GRID -->"
CAPABILITIES_PAGE = ROOT / "content" / "capabilities.md"
PATTERNS_PAGE = ROOT / "content" / "patterns" / "index.md"
VCOUNT_BEGIN = "<!-- BEGIN GENERATED VERDICT COUNT -->"
VCOUNT_END = "<!-- END GENERATED VERDICT COUNT -->"
VERDICTS_PAGE = CONTENT / "verdicts.md"
SPREAD_BEGIN = "<!-- BEGIN GENERATED SPREAD -->"
SPREAD_END = "<!-- END GENERATED SPREAD -->"

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
     "on the read path, not merely available as a tag. This certifies that the "
     "key reaches the query — not that the boundary is authenticated, nor that "
     "a caller cannot widen it by passing a different argument."),
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


_REVISION = re.compile(r"^revision:\s*\"?([^\"\s]+)\"?\s*$", re.M)
_REVISION_URL = re.compile(r"^revision_url:\s*\"?(\S+?)\"?\s*$", re.M)
_FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def check_revisions() -> list[str]:
    """Every pin must be a full 40-character commit id, in both places.

    Abbreviated SHAs read fine and resolve fine, right up until they don't: git's
    short form is only unique until the repository grows into the collision, and
    a 12-character pin in a report is a claim about a repository we do not
    control the future of. Sixteen reports had drifted to short form before this
    check existed, and the drift was invisible because both forms render and both
    resolve on GitHub today.

    The URL is checked against the same value because they are written by hand as
    a pair, so one can be updated without the other.
    """
    problems: list[str] = []
    for path in sorted(SYSTEMS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        revision = _REVISION.search(text)
        url = _REVISION_URL.search(text)
        if revision is None:
            problems.append(f"{path.stem}: no revision in frontmatter")
            continue
        if not _FULL_SHA.match(revision.group(1)):
            problems.append(
                f"{path.stem}: revision '{revision.group(1)}' is not a full 40-character "
                "commit id"
            )
        if url is None:
            problems.append(f"{path.stem}: no revision_url in frontmatter")
        elif not url.group(1).endswith(revision.group(1)):
            problems.append(
                f"{path.stem}: revision_url does not end in the pinned revision "
                f"({url.group(1)})"
            )
    return problems


_SHORT_COMMIT_URL = re.compile(
    r"https://github\.com/[^/\s)]+/[^/\s)]+/commit/([0-9a-f]{6,39})\b"
)
_SHORT_COMMIT_SPAN = re.compile(r"\[`([0-9a-f]{6,39})`\]")


def check_commit_links() -> list[str]:
    """Prose commit references must be full ids too, not just the frontmatter pin.

    The provenance list on the overview cites fifty-odd commits, and those were
    written abbreviated in both the link text and the href. Rendering truncates
    them for readability, so the short form buys nothing a reader can see and
    costs the same uniqueness the frontmatter check exists to protect.
    """
    problems: list[str] = []
    for path in sorted(CONTENT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in _SHORT_COMMIT_URL.finditer(text):
            line = text[: match.start()].count("\n") + 1
            problems.append(
                f"{path.relative_to(CONTENT)}:{line}: abbreviated commit url "
                f"'{match.group(1)}' — use the full 40-character id"
            )
        for match in _SHORT_COMMIT_SPAN.finditer(text):
            line = text[: match.start()].count("\n") + 1
            problems.append(
                f"{path.relative_to(CONTENT)}:{line}: abbreviated commit link text "
                f"'{match.group(1)}' — use the full id; the build truncates it for display"
            )
    return problems


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

    # Every value is non-None past the check above; rebind so that is visible to
    # a type checker rather than only true at runtime.
    declared: dict[str, set[str]] = {
        slug: flags for slug, flags in carried.items() if flags is not None
    }

    known = {flag for flag, _, _ in CAPABILITIES}
    unknown = {f for flags in declared.values() for f in flags} - known
    if unknown:
        print(f"error: unknown capability flags: {sorted(unknown)}", file=sys.stderr)
        raise SystemExit(1)

    total = len(paths)
    blocks: list[str] = []
    for flag, label, definition in CAPABILITIES:
        holders = sorted(slug for slug, flags in declared.items() if flag in flags)
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


def build_spread() -> str:
    """The "how established is any of this" table on the patterns index.

    Hand-maintained until an outside reviewer quoted "1 of 58" back at the atlas
    from a page that had drifted two systems and four capability counts behind
    the frontmatter. Every row here is now derived, and the denominator with it,
    because a stale denominator makes every rare mechanism look rarer than it is.
    """
    paths = sorted(SYSTEMS.glob("*.md"))
    total = len(paths)
    counts = {flag: 0 for flag, _, _ in CAPABILITIES}
    for path in paths:
        for flag in read_capabilities(path) or set():
            counts[flag] += 1
    ranked = sorted(CAPABILITIES, key=lambda c: -counts[c[0]])
    rows = ["| Mechanism | Systems carrying it |", "| --- | --- |"]
    for flag, label, _ in ranked:
        n = counts[flag]
        # The rare ones are the argument of the section, so they carry the weight.
        cell = f"**{n} of {total}**" if n <= 2 else f"{n} of {total}"
        name = f"**{label}**" if n <= 2 else label
        rows.append(f"| {name} | {cell} |")
    return "\n".join(rows)


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

    pins = check_revisions() + check_commit_links()
    if pins:
        for problem in pins:
            print(f"error: {problem}", file=sys.stderr)
        return 1

    table = build_table()
    capabilities = build_capabilities()
    text = OVERVIEW.read_text(encoding="utf-8")

    updated = splice(text, BEGIN, END, table, "matrix")
    updated = splice(updated, CAP_BEGIN, CAP_END, capabilities, "capabilities")

    grid_text = CAPABILITIES_PAGE.read_text(encoding="utf-8")
    grid_updated = splice(grid_text, GRID_BEGIN, GRID_END, build_capability_grid(), "grid")

    spread_text = PATTERNS_PAGE.read_text(encoding="utf-8")
    spread_updated = splice(spread_text, SPREAD_BEGIN, SPREAD_END, build_spread(), "spread")

    # The verdicts page opens by claiming how many reports it covers. It was
    # split off /compare/ carrying a hand-written "116 reports" while holding
    # 136 headings, so the sentence was wrong the moment the page existed.
    verdict_text = VERDICTS_PAGE.read_text(encoding="utf-8")
    n_verdicts = len(list(SYSTEMS.glob("*.md")))
    verdict_updated = splice(
        verdict_text, VCOUNT_BEGIN, VCOUNT_END,
        f"**This page covers all {n_verdicts} reports.**", "verdict count",
    )

    if (updated == text and grid_updated == grid_text
            and spread_updated == spread_text and verdict_updated == verdict_text):
        print("Matrix, capability index, grid and pattern spread already up to date.")
        return 0

    if "--check" in sys.argv:
        print(
            "error: generated matrix/capability index is out of date. Run 'npm run build'.",
            file=sys.stderr,
        )
        return 1

    OVERVIEW.write_text(updated, encoding="utf-8")
    CAPABILITIES_PAGE.write_text(grid_updated, encoding="utf-8")
    PATTERNS_PAGE.write_text(spread_updated, encoding="utf-8")
    VERDICTS_PAGE.write_text(verdict_updated, encoding="utf-8")
    print(
        f"Regenerated comparative matrix ({table.count(chr(10)) - 1} systems), "
        "capability index, capability grid and pattern spread."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

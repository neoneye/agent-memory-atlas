#!/usr/bin/env python3
"""Generate the A–Z index of every system report.

Why this page exists: the atlas has three surfaces that list systems and none of
them answers "is X in here?" quickly. The homepage is a filterable card grid, the
comparative matrix is 115 rows of an eleven-column table inside a horizontal
scroller, and the per-system entries in the comparative report's verdict section
only enter the contents list once a reader has scrolled into that section. Twice
in one week a reader concluded a system was missing when it was present in all
three.

So: one flat alphabetical list, generated from the same frontmatter that drives
the matrix and the capability index, and therefore complete by construction. A
report that exists appears here; a report that does not, cannot. That is the
property the hand-written verdict section cannot offer.

Sorted by slug rather than by title, because the slug is what a reader types into
a find-in-page — `aukora-kernel`, `powermem`, `second-me` — while the title may
be styled ("Project N.E.K.O.", "Google ADK") in ways nobody guesses.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Reuse the frontmatter reader and capability definitions so this page cannot
# disagree with the matrix or the capability index about what a report says.
from generate_matrix import (  # type: ignore[attr-defined]  # noqa: E402
    CAPABILITIES,
    read_capabilities,
)

# The strip on each report page already has short labels for these; import them
# so a reader meets the same words in both places.
from capability_strip import SHORT  # type: ignore[attr-defined]  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SYSTEMS = ROOT / "content" / "systems"
OUTPUT = ROOT / "content" / "systems-index.md"

def frontmatter(text: str) -> str:
    """The block between the opening and closing `---`, or "" if malformed.

    Bounded deliberately: a body line beginning `title:` inside a fenced block
    would otherwise be read as the report's title.
    """
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 3)
    return text[4:end] if end != -1 else ""


def read_field(block: str, key: str) -> str:
    """Pull one scalar out of a frontmatter block, stripped of quotes."""
    for line in block.split("\n"):
        if line.startswith(f"{key}:"):
            value = line.split(":", 1)[1].strip()
            if value.startswith('"') and value.endswith('"') and len(value) > 1:
                value = value[1:-1]
            return value
    return ""


def main() -> int:
    reports = sorted(SYSTEMS.glob("*.md"), key=lambda p: p.stem)
    if not reports:
        print("no reports found", file=sys.stderr)
        return 1

    rows = []
    for path in reports:
        text = path.read_text(encoding="utf-8")
        # Frontmatter only — a body line starting with "title:" would otherwise win.
        head = frontmatter(text)
        marks = read_capabilities(path)
        if marks is None:
            # A missing key is not an empty one. `capabilities: ""` means the
            # report was assessed and carries none of the seven; no key at all
            # means nobody looked, and rendering that as "no marks" would launder
            # the second into the first. generate_matrix.py already fails the
            # build on this — fail here too rather than emit a plausible row.
            print(
                f"{path.name}: frontmatter has no `capabilities:` key",
                file=sys.stderr,
            )
            return 1
        rows.append(
            {
                "slug": path.stem,
                "title": read_field(head, "title") or path.stem,
                "eyebrow": read_field(head, "eyebrow"),
                "source": read_field(head, "source_name"),
                "marks": [SHORT[k] for k, _, _ in CAPABILITIES if k in marks],
            }
        )

    lines = [
        "---",
        # Non-breaking spaces: "A to Z" is one token to a reader, and a
        # break inside it strands a letter on its own line.
        "title: Every System, A\u00a0to\u00a0Z",
        "eyebrow: Index",
        "description: A flat alphabetical index of every system report in the "
        "atlas, generated from the reports themselves.",
        "root: ..",
        "page_kind: methodology",
        "---",
        "",
        f"Every one of the **{len(rows)} reports**, by slug. Generated from each "
        "report's own frontmatter, so this list cannot drift from what the atlas "
        "actually holds — unlike the [verdicts](../verdicts/), which are "
        "hand-written, and where the difference between *complete by "
        "construction* and *complete as a fact about today* is drawn out.",
        "",
        "Looking for something else? The [capability index](../capabilities/) "
        "groups systems by the seven rubric mechanisms, the "
        "[comparative matrix](../compare/#2-comparative-matrix) puts eleven "
        "columns side by side, and the [pattern library](../patterns/) starts "
        "from the mechanism rather than the system.",
        "",
    ]

    current_letter = ""
    for row in rows:
        letter = row["slug"][0].upper()
        if letter != current_letter:
            current_letter = letter
            lines.append(f"## {letter}")
            lines.append("")
        marks = f" · {', '.join(row['marks'])}" if row["marks"] else ""
        eyebrow = f" — {row['eyebrow']}" if row["eyebrow"] else ""
        source = f" · `{row['source']}`" if row["source"] else ""
        lines.append(
            f"- [`{row['slug']}`](../systems/{row['slug']}/) "
            f"**{row['title']}**{eyebrow}{source}{marks}"
        )

    OUTPUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    marked = sum(1 for r in rows if r["marks"])
    print(f"Generated A–Z index ({len(rows)} systems, {marked} carrying a mark)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

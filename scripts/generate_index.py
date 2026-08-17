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

Rendered as four aligned columns, and the slug is *printed* only where it does
not already appear in the title or the repository path. Both halves of that
matter. On 279 of 301 rows the slug, the title and the repository name are the
same word three times over ("a-mem · A-MEM · agiresearch/A-mem"), and a reader
scanning for the one field that differs between rows — what the system actually
is — had to read past two copies of the name to reach it. On the other 22 the
slug is the only thing that explains why the row sorts where it does: `Google
ADK` filed under A, `Recall` under R-for-recall-substrate. So the test is
literal substring containment, not similarity, which keeps a guarantee the eye
can rely on: every slug in the corpus is findable on this page by find-in-page,
either as the title, inside the repository path, or printed under the name.
"""

from __future__ import annotations

import html
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
    """Pull one scalar out of a frontmatter block, stripped of quotes.

    The inner `\\"` unescape is not cosmetic. A quoted YAML scalar carries its
    own quotes escaped, and the rows used to be emitted as Markdown, where
    pandoc consumed the backslash on the way through. They are HTML now, and
    nothing downstream would.
    """
    for line in block.split("\n"):
        if line.startswith(f"{key}:"):
            value = line.split(":", 1)[1].strip()
            if value.startswith('"') and value.endswith('"') and len(value) > 1:
                value = value[1:-1].replace('\\"', '"')
            return value
    return ""


def slug_is_findable(slug: str, title: str, source: str) -> bool:
    """Would a find-in-page for `slug` land on this row without printing it?

    Case-insensitive substring, and deliberately nothing cleverer. Normalising
    separators away would call `agent-memory-techniques` a match for
    `Agent_Memory_Techniques` and `brain-md` a match for `brain.md`, which reads
    as the same name to a person and is a miss to the browser's find bar — the
    one reader this test exists to serve.
    """
    return slug.lower() in f"{title} {source}".lower()


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
        # Four columns do not fit the 820px reading measure; see build_site.sh.
        "layout: wide",
        "---",
        "",
        f"Every one of the **{len(rows)} reports**, filed under the slug in its "
        "URL — printed beneath the name on the rows where the two differ, which "
        "is why `Google ADK` sits under A. Generated from each report's own "
        "frontmatter, so this list cannot drift from what the atlas actually "
        "holds — unlike the [verdicts](../verdicts/), which are hand-written, "
        "and where the difference between *complete by construction* and "
        "*complete as a fact about today* is drawn out.",
        "",
        "Looking for something else? The [capability index](../capabilities/) "
        "groups systems by the seven rubric mechanisms, the "
        "[comparative matrix](../compare/#2-comparative-matrix) puts eleven "
        "columns side by side, and the [pattern library](../patterns/) starts "
        "from the mechanism rather than the system.",
        "",
    ]

    # One header, under the intro rather than repeated per letter: 27 copies of
    # the same four words is chrome, and the columns name themselves after the
    # first row. It is hidden below the breakpoint where the columns stack.
    lines += [
        '<div class="az-head" aria-hidden="true"><span>System</span>'
        "<span>What it is</span><span>Repository</span>"
        "<span>Capabilities</span></div>",
        "",
    ]

    # Raw HTML rather than Markdown, because the columns have to align down the
    # whole page and a Markdown list cannot: every field would sit wherever the
    # previous one stopped. Emitted as one contiguous block per letter — a blank
    # line inside would close the HTML block and hand the rest to the Markdown
    # reader, which is where `Agent_Memory_Techniques` becomes italic.
    current_letter = ""
    for row in rows:
        letter = row["slug"][0].upper()
        if letter != current_letter:
            if current_letter:
                lines += ["</ul>", ""]
            current_letter = letter
            lines += [f"## {letter}", "", '<ul class="az">']

        slug = html.escape(row["slug"])
        name = html.escape(row["title"])
        # The slug earns its place on the row only where the name does not
        # already carry it; see slug_is_findable.
        under = (
            ""
            if slug_is_findable(row["slug"], row["title"], row["source"])
            else f'<code class="az-slug">{slug}</code>'
        )
        marks = "".join(
            f'<span class="az-cap">{html.escape(mark)}</span>' for mark in row["marks"]
        )
        lines.append(
            f'<li><span class="az-id">'
            f'<a href="../systems/{slug}/">{name}</a>{under}</span>'
            f'<span class="az-what">{html.escape(row["eyebrow"])}</span>'
            f'<code class="az-repo">{html.escape(row["source"])}</code>'
            f'<span class="az-caps">{marks}</span></li>'
        )
    if current_letter:
        lines.append("</ul>")

    OUTPUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    marked = sum(1 for r in rows if r["marks"])
    printed = sum(
        1 for r in rows if not slug_is_findable(r["slug"], r["title"], r["source"])
    )
    print(
        f"Generated A–Z index ({len(rows)} systems, {marked} carrying a mark, "
        f"{printed} needing the slug printed)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

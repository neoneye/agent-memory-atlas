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

Rendered as four aligned columns, and the slug is *printed* only where the title
is not already that same word. On 278 of 301 rows it is: the slug, the title and
the repository name say one thing three times over ("a-mem · A-MEM ·
agiresearch/A-mem"), and a reader scanning for the field that actually differs
between rows — what the system is — had to read past two copies of the name to
reach it. On the other 23 the slug is the only thing that explains where the row
is filed: `Google ADK` under A, `Hats` under O, `AMITY / Archangel-8` under S.

The test is deliberately *not* whether a find-in-page for the slug would land on
the row. That question is about the whole row, so it counted a slug legible
inside the repository path three columns away as already shown, and hid it on
exactly the rows above. The question this page asks is narrower and visual —
would this name surprise a reader here — so only the title is compared, and only
after punctuation is stripped from both.

What that gives up is small and worth naming: on 17 rows the slug now goes
unprinted while differing from the title in punctuation only (`brain-md` under
`brain.md`, `terse-memory` under `TERSE Memory`), so a browser's find bar will
not match those slugs literally. A reader looking for one of them is looking at
it — the row is filed under the letter they expect, and the eye resolves a dot
against a hyphen in a way the matcher cannot.
"""

from __future__ import annotations

import html
import re
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


def title_carries_slug(slug: str, title: str) -> bool:
    """Is the slug the title, minus the punctuation a URL cannot hold?

    Compared against the title alone. Widening this to the repository path as
    well answers a different question — *could a reader find this string on the
    row* — and that question hid the slug on the 18 rows where it is most
    load-bearing, `Google ADK` and `adk-python` among them, on the grounds that
    it was legible inside `google/adk-python` three columns away.

    Punctuation is stripped rather than matched because the difference between
    `brain-md` and `brain.md`, or `TERSE Memory` and `terse-memory`, is the
    slug's, not the system's: a URL cannot hold a space or a dot. Printing the
    slug on those rows restated the name in a second typeface, which is what
    this whole column exists to stop.
    """
    bare = lambda text: re.sub(r"[^a-z0-9]", "", text.lower())  # noqa: E731
    return bare(slug) == bare(title)


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
        # already carry it; see title_carries_slug.
        under = (
            ""
            if title_carries_slug(row["slug"], row["title"])
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
        1 for r in rows if not title_carries_slug(r["slug"], r["title"])
    )
    print(
        f"Generated A–Z index ({len(rows)} systems, {marked} carrying a mark, "
        f"{printed} needing the slug printed)"
    )
    return 0


def self_test() -> int:
    """Controls on title_carries_slug, in both directions.

    This rule has been wrong once already, and it failed quietly: a wrong answer
    prints a redundant slug or withholds a needed one, and the page still builds
    and still looks deliberate. The first version tested whether a find-in-page
    for the slug would hit anywhere on the row, which printed `brain-md` under
    `brain.md` and withheld `adk-python` from `Google ADK`. Both of those are
    below.

    The containment pair is the one to keep. Substring in either direction must
    not count as carried, or the rule slides back to answering "is this string
    on the row" instead of "is this name the same name".
    """
    cases = [
        # Carried: the slug is the title with URL punctuation.
        ("a-mem", "A-MEM", True, "case and separator only"),
        ("brain-md", "brain.md", True, "hyphen standing in for a dot"),
        ("terse-memory", "TERSE Memory", True, "hyphen standing in for a space"),
        ("nova-ai", "Nova AI", True, "case and separator"),
        ("agentmemory-v4", "agentmemory V4", True, "separator inside a version"),
        # Not carried: the title is a different name.
        ("adk-python", "Google ADK", False, "different name entirely"),
        ("neko", "Project N.E.K.O.", False, "styled title, plain slug"),
        ("one-agent-many-hats", "Hats", False, "title is a fragment of the slug"),
        ("recall-substrate", "Recall", False, "slug extends the title"),
        ("fidelis", "Fidelis Memory", False, "title extends the slug"),
    ]

    failures = [
        f"{slug!r} vs {title!r} ({label}): expected {expected}"
        for slug, title, expected, label in cases
        if title_carries_slug(slug, title) is not expected
    ]
    for failure in failures:
        print(failure, file=sys.stderr)
    if failures:
        return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(self_test() if "--self-test" in sys.argv[1:] else main())

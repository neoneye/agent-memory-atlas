#!/usr/bin/env python3
"""Bind each pattern page's `stance:` to the bucket the index lists it under.

The patterns index has always separated what the atlas is *reporting* from what
it is *arguing for*. That disclosure lived in one paragraph on one page, so a
reader who arrived on `rejected-value-tombstone` from a search engine — the way
most readers arrive — saw a confident pattern page and nothing telling them nine
systems of one hundred and sixty-five carry the mechanism.

The fix was a stance pill in every pattern's header, which creates the failure
this script exists to prevent: two statements of the same classification, in two
files, that can disagree. A pill saying *Reporting an established practice* over
a page the index lists under advocacy is worse than no pill, because it launders
an argument as a consensus — the exact error the disclosure was written to stop.

What this checks:

1. Every pattern page carries a `stance:` slug this build knows how to render.
2. Every pattern appears in exactly one bucket on the index — no page silently
   dropped when a pattern is added, none listed twice.
3. The bucket and the slug agree.

Usage:
    check_pattern_stance.py [root] [--self-test]
"""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

#: slug -> the marker that opens its block on the index page. The reporting,
#: advocacy and mixed buckets are bullets; the category-bound case is a
#: paragraph, because it was added later and argued for at length.
BUCKETS = {
    "reporting": "- **Reporting an established practice.**",
    "advocacy": "- **Advocacy — one or two instances.**",
    "mixed": "- **Reporting, with one advocacy claim.**",
    "category-bound": "**A fourth case, added later and needing its own label.**",
}

PATTERN_LINK = re.compile(r"\]\(\./([a-z0-9-]+)/\)")


def _block(text: str, marker: str) -> str:
    """The index text from `marker` to the next blank line that ends its block."""
    start = text.find(marker)
    if start == -1:
        return ""
    rest = text[start + len(marker):]
    # A bullet ends at the next bullet or blank line; the paragraph ends at the
    # next blank line. Both are "up to the next line that starts a new thing".
    end = len(rest)
    for boundary in ("\n\n", "\n- **"):
        found = rest.find(boundary)
        if found != -1:
            end = min(end, found)
    return rest[:end]


def check(root: Path) -> list[str]:
    patterns_dir = root / "content" / "patterns"
    index = patterns_dir / "index.md"
    problems: list[str] = []

    declared: dict[str, str] = {}
    for path in sorted(patterns_dir.glob("*.md")):
        if path.stem == "index":
            continue
        front = path.read_text(encoding="utf-8").split("---", 2)
        match = re.search(r"^stance:[ \t]*(\S+)$", front[1] if len(front) > 2 else "", re.M)
        if not match:
            problems.append(f"{path.name}: no `stance:` in frontmatter")
            continue
        if match.group(1) not in BUCKETS:
            problems.append(
                f"{path.name}: stance '{match.group(1)}' is not one of "
                + ", ".join(sorted(BUCKETS))
            )
            continue
        declared[path.stem] = match.group(1)

    index_text = index.read_text(encoding="utf-8")
    listed: dict[str, list[str]] = {}
    for stance, marker in BUCKETS.items():
        block = _block(index_text, marker)
        if not block:
            problems.append(f"index.md: no block found for the {stance} bucket")
            continue
        for slug in PATTERN_LINK.findall(block):
            listed.setdefault(slug, []).append(stance)

    for slug, stances in sorted(listed.items()):
        if len(stances) > 1:
            problems.append(
                f"index.md lists {slug} under more than one bucket: "
                + ", ".join(stances)
            )
        if slug not in declared:
            problems.append(f"index.md lists {slug}, which has no pattern page")

    for slug, stance in sorted(declared.items()):
        if slug not in listed:
            problems.append(
                f"{slug}.md declares stance '{stance}' but the index lists it in "
                "no bucket"
            )
        elif listed[slug][0] != stance:
            problems.append(
                f"{slug}.md declares stance '{stance}' but the index lists it "
                f"under '{listed[slug][0]}'"
            )

    return problems


def self_test() -> int:
    """Flip one page's stance on a scratch copy and require the check to fail."""
    root = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "atlas"
        shutil.copytree(root / "content", scratch / "content")
        victim = scratch / "content" / "patterns" / "rejected-value-tombstone.md"
        victim.write_text(
            victim.read_text(encoding="utf-8").replace(
                "stance: advocacy", "stance: reporting", 1
            ),
            encoding="utf-8",
        )
        if not check(scratch):
            print(
                "check_pattern_stance.py passed a page whose pill contradicts "
                "the index. It is not checking anything.",
                file=sys.stderr,
            )
            return 1
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    root = Path(argv[1]) if len(argv) > 1 else Path(".")
    problems = check(root)
    if problems:
        print("Pattern stance disagrees with the patterns index:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            "\nEvery pattern page declares one `stance:` and the index lists it "
            "in exactly one bucket. Fix whichever is wrong — they are the same "
            "claim written twice.",
            file=sys.stderr,
        )
        return 1
    counts: dict[str, int] = {}
    for path in sorted((root / "content" / "patterns").glob("*.md")):
        if path.stem == "index":
            continue
        stance = re.search(r"^stance:[ \t]*(\S+)$", path.read_text(encoding="utf-8"), re.M)
        if stance:
            counts[stance.group(1)] = counts.get(stance.group(1), 0) + 1
    print(
        f"{sum(counts.values())} pattern stances agree with the index: "
        + ", ".join(f"{n} {slug}" for slug, n in sorted(counts.items()))
        + "."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

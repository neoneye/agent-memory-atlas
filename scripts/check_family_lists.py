#!/usr/bin/env python3
"""Assert every report is named in at least one family's slug list.

Each family heading in `content/families.md` is followed by a hand-kept list of
the systems in that family, and the list is what a reader scans to find a
system's neighbours. Nothing checked it: a new report got its paragraph, its
card and its appendix link, and the list was the step that got skipped. On
2026-11-02, 184 of 762 reports were in no family's list.

A family's list is the first paragraph under its `## ` heading when that
paragraph is made of `[`slug`](../systems/slug/)` links, with at most a few
label words between them ("Hosts:"). A heading whose first paragraph is prose (the out-of-scope sections, the category
essays) has no list and is not a family for this check.

Two failures:
  - a report under `content/systems/` that no list names;
  - a list entry naming a slug with no report, or an empty entry (`, ,`), which
    is how a hand edit that dropped a slug shows up.

Usage: check_family_lists.py <project-dir>
       check_family_lists.py --self-test
"""
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^## (.+)$", re.M)
ENTRY = re.compile(r"\[`([^`]*)`\]\(\.\./systems/([^/)]*)/\)")


def family_lists(text: str) -> dict[str, tuple[list[str], str]]:
    """{family heading: (slugs, the list paragraph)} for every heading followed by a slug list."""
    heads = list(HEADING.finditer(text))
    out: dict[str, tuple[list[str], str]] = {}
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        first = text[m.end():end].strip().split("\n\n")[0]
        entries = ENTRY.findall(first)
        # A list may carry short labels ("Hosts:", "plus hosted providers"),
        # never more words than half its entries; prose that names a few
        # systems in passing has far more.
        labels = ENTRY.sub("", first).replace(",", "").split()
        if len(entries) >= 3 and len(labels) <= len(entries) // 2:
            out[m.group(1)] = ([link for _, link in entries], first)
    return out


def problems(text: str, slugs: set[str]) -> list[str]:
    out = []
    listed = set()
    for family, (entries, first) in family_lists(text).items():
        for slug in entries:
            if slug not in slugs:
                out.append(f"{family}: lists `{slug}`, which has no report")
            listed.add(slug)
        if re.search(r",\s*,", first):
            out.append(f"{family}: the slug list has an empty entry")
    for slug in sorted(slugs - listed):
        out.append(f"{slug}: in no family's slug list")
    return out


def self_test() -> int:
    good = ("## A family\n\nHosts: [`a`](../systems/a/), [`b`](../systems/b/), [`e`](../systems/e/)\n\nProse.\n\n"
            "## Not a family\n\nProse that names [`c`](../systems/c/) in passing.\n\n"
            "## B family\n\n[`c`](../systems/c/), [`a`](../systems/a/), [`b`](../systems/b/)\n\nMore prose.\n")
    cases = [
        ("every report listed passes", good, {"a", "b", "c", "e"}, 0),
        ("an unlisted report fails", good, {"a", "b", "c", "d", "e"}, 1),
        ("a mention in prose is not a listing", good.replace("[`c`](../systems/c/), [`a`]", "[`e`](../systems/e/), [`a`]"), {"a", "b", "c", "e"}, 1),
        ("a listed slug with no report fails", good, {"a", "b", "c"}, 1),
        ("an empty entry fails", good.replace("[`a`](../systems/a/), [`b`]", "[`a`](../systems/a/), , [`b`]", 1), {"a", "b", "c", "e"}, 1),
    ]
    for name, text, slugs, expected in cases:
        got = len(problems(text, slugs))
        if got != expected:
            print(f"self-test failed: {name}: got {got}, expected {expected}", file=sys.stderr)
            return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main(root: str) -> int:
    project = Path(root)
    slugs = {p.stem for p in (project / "content" / "systems").glob("*.md")}
    text = (project / "content" / "families.md").read_text(encoding="utf-8")
    found = problems(text, slugs)
    if found:
        print("Family slug lists and reports disagree:", file=sys.stderr)
        for p in found:
            print(f"  {p}", file=sys.stderr)
        return 1
    lists = family_lists(text)
    print(f"{len(slugs)} reports each named in at least one of {len(lists)} family slug lists.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--self-test" in args:
        sys.exit(self_test())
    sys.exit(main(next((a for a in args if not a.startswith("--")), ".")))

#!/usr/bin/env python3
"""Require a short *Read these first* list above a long pattern catalogue.

`AGENTS.md` sends a builder to a pattern page's `## Seen in the atlas` to find
the systems worth reading. On the largest pages that section is most of the
page — 9,778 of 11,342 words on the rejected-value tombstone on 2026-09-25 —
and a catalogue that long is no longer a pointer to anything.

Rule: a catalogue over CATALOGUE_LIMIT words opens with `### Read these first`,
holding 1 to MAX_EXEMPLARS bullets, each linking a system report, and nothing
else: a heading closes it, or the catalogue below renders as part of the short
list and the entry point is gone again. The block is
validated wherever it appears, whatever the catalogue's length. Choosing the
exemplars is a judgement this cannot check; it checks that the list exists,
sits first, stays short and points at reports.

On a page whose pattern is a capability mark, an exemplar must carry that mark
in its report's `capabilities:` line, or say in its own line that it is the
counterexample — a failure, a near-miss, or what is missing. The first lists
were written from the page's prose on 2026-09-25, and three of the trust-state
picks had lost `trust_state` on 2026-09-19; the prose had not caught up and
nothing compared the two.

Usage: check_pattern_exemplars.py <project-dir>
       check_pattern_exemplars.py --self-test
"""
import re
import sys
from pathlib import Path

CATALOGUE_LIMIT = 3000
MAX_EXEMPLARS = 5

CATALOGUE = re.compile(r"^## (?:Seen in the atlas|In the analyzed systems)\s*$", re.M)
BLOCK = re.compile(r"\A\s*### Read these first\s*\n(.*?)(?=^#{2,3} |\Z)", re.M | re.S)
BULLET = re.compile(r"^- ", re.M)
SYSTEM_LINK = re.compile(r"\]\((?:\.\./)+systems/([a-z0-9-]+)/?(?:#[^)]*)?\)")
#: Pattern pages whose move is one of the seven rubric marks.
PATTERN_MARK = {
    "rejected-value-tombstone": "tombstone",
    "trust-state-machine": "trust_state",
    "bi-temporal-fact-validity": "bitemporal",
    "scope-as-a-first-class-key": "scope_enforced",
    "append-only-memory-audit": "audit_log",
}
COUNTEREXAMPLE = re.compile(r"counterexample|failure|near-miss|missing", re.I)
CAPS = re.compile(r'^capabilities:\s*"([^"]*)"', re.M)


def problems(name: str, text: str, marks: dict[str, set[str]] | None = None) -> list[str]:
    heading = CATALOGUE.search(text)
    if not heading:
        return []
    section = text[heading.end():]
    section = section[:m.start()] if (m := re.search(r"^## ", section, re.M)) else section
    block = BLOCK.match(section)
    if not block:
        if "### Read these first" in section:
            return [f"{name}: 'Read these first' is not the first thing in the catalogue"]
        if len(section.split()) > CATALOGUE_LIMIT:
            return [f"{name}: catalogue is {len(section.split())} words with no "
                    f"'### Read these first' (limit {CATALOGUE_LIMIT})"]
        return []
    items = [i for i in BULLET.split(block.group(1))[1:] if i.strip()]
    out = []
    loose = [l for l in block.group(1).split("\n")
             if l.strip() and not l.startswith(("- ", "  "))]
    if loose:
        out.append(f"{name}: 'Read these first' holds more than its list; close it "
                   "with a heading before the catalogue")
    if not 1 <= len(items) <= MAX_EXEMPLARS:
        out.append(f"{name}: 'Read these first' has {len(items)} entries (1 to {MAX_EXEMPLARS})")
    out += [f"{name}: exemplar {n} links no system report"
            for n, item in enumerate(items, 1) if not SYSTEM_LINK.search(item)]
    mark = PATTERN_MARK.get(name.removesuffix(".md"))
    if mark and marks is not None:
        for item in items:
            link = SYSTEM_LINK.search(item)
            if link and mark not in marks.get(link.group(1), set()) and not COUNTEREXAMPLE.search(item):
                out.append(f"{name}: exemplar {link.group(1)} does not carry `{mark}` and its "
                           "line does not say it is the counterexample")
    return out


def self_test() -> int:
    big = " ".join(["w"] * (CATALOGUE_LIMIT + 1))
    item = "- [A](../../systems/a/) seals its log.\n"
    cases = [
        ("a long catalogue without the block fails", f"## Seen in the atlas\n\n{big}\n", 1),
        ("a short catalogue without it passes", "## Seen in the atlas\n\nA few systems.\n", 0),
        ("a block of three passes",
         f"## Seen in the atlas\n\n### Read these first\n\n{item * 3}\n### Every instance\n\n{big}\n", 0),
        ("a block the catalogue runs on into fails",
         f"## Seen in the atlas\n\n### Read these first\n\n{item * 3}\nThe catalogue.\n", 1),
        ("a block of six fails", f"## Seen in the atlas\n\n### Read these first\n\n{item * 6}\n", 1),
        ("an unlinked exemplar fails", "## Seen in the atlas\n\n### Read these first\n\n- A seals its log.\n", 1),
        ("an exemplar without the page's mark fails",
         "## Seen in the atlas\n\n### Read these first\n\n- [A](../../systems/a/) seals its log.\n", 1, "trust-state-machine.md"),
        ("a counterexample without the mark passes",
         "## Seen in the atlas\n\n### Read these first\n\n- [A](../../systems/a/) the failure.\n", 0, "trust-state-machine.md"),
        ("an exemplar with the mark passes",
         "## Seen in the atlas\n\n### Read these first\n\n- [B](../../systems/b/) seals its log.\n", 0, "trust-state-machine.md"),
        ("a block placed below the catalogue fails",
         f"## Seen in the atlas\n\nText.\n\n### Read these first\n\n{item}", 1),
    ]
    marks = {"a": set(), "b": {"trust_state"}}
    for case in cases:
        name, text, expected = case[:3]
        page = case[3] if len(case) > 3 else "fixture.md"
        got = len(problems(page, text, marks))
        if got != expected:
            print(f"self-test failed: {name}: got {got}, expected {expected}", file=sys.stderr)
            return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main(root: str) -> int:
    marks = {}
    for path in (Path(root) / "content" / "systems").glob("*.md"):
        m = CAPS.search(path.read_text(encoding="utf-8"))
        marks[path.stem] = {f.strip() for f in m.group(1).split(",") if f.strip()} if m else set()
    found = []
    for path in sorted((Path(root) / "content" / "patterns").glob("*.md")):
        found += problems(path.name, path.read_text(encoding="utf-8"), marks)
    if found:
        print("Pattern catalogue entry points are out of step:", file=sys.stderr)
        for p in found:
            print(f"  {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--self-test" in args:
        sys.exit(self_test())
    sys.exit(main(next((a for a in args if not a.startswith("--")), ".")))

#!/usr/bin/env python3
"""Hold new and re-pinned reports to the reading order, from the cutover on.

Four rules, from notes/2026-09-25-written-to-be-checked-not-yet-to-be-read.md.
Each applies only where the prose is being written anyway: to a report whose
`analyzed_at` is on or after CUTOVER, and to History entries dated on or after
it. A re-pin bumps `analyzed_at`, so the corpus converts at the rate it is
re-read, and nothing is rewritten in a campaign.

1. **`description` is one line.** It renders as the deck under the title, on
   the page and in link previews. At most DESCRIPTION_LIMIT words.
2. **The census lives in the header band.** `licence`, `size` and `activity`
   are non-empty in the frontmatter; `tests` is optional.
3. **The summary opens with the finding, not the census.** The first
   paragraph under `## 1. Executive Summary` may not carry a line, commit or
   author count; those live in the `size` and `activity` frontmatter fields,
   which render in the header band.
4. **A History entry states the delta.** At most HISTORY_LIMIT words from its
   `**YYYY-MM-DD**` to the next entry. The evidence goes in the section it
   changed, and the entry links there.

What this cannot check: whether the first paragraph is the right finding.

Usage: check_report_shape.py <project-dir>
       check_report_shape.py --self-test
"""
import re
import sys
from pathlib import Path

#: The day this check shipped. Reports and History entries dated before it are
#: not held; they convert when a reading next opens them.
CUTOVER = "2026-09-25"
DESCRIPTION_LIMIT = 25
HISTORY_LIMIT = 150
REQUIRED_FACTS = ("licence", "size", "activity")

ANALYZED_AT = re.compile(r"^analyzed_at:\s*\"?(\d{4}-\d{2}-\d{2})", re.M)
DESCRIPTION = re.compile(r"^description:\s*(.+)$", re.M)
SUMMARY = re.compile(r"^## 1\. Executive Summary\s*\n+(.+?)(?:\n\s*\n|\Z)", re.M | re.S)
NUMBER_WORD = r"(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|twenty)"
CENSUS = re.compile(
    rf"\b(?:\d[\d,.]*\s*k?|{NUMBER_WORD})\s+(?:lines|commits|authors|contributors)\b", re.I)
HISTORY = re.compile(r"^## History\s*$", re.M)
ENTRY = re.compile(r"^\*\*(\d{4}-\d{2}-\d{2})\*\*", re.M)


def history_entries(text: str) -> list[tuple[str, str]]:
    heading = HISTORY.search(text)
    if not heading:
        return []
    tail = text[heading.end():]
    tail = tail[:m.start()] if (m := re.search(r"^## ", tail, re.M)) else tail
    starts = list(ENTRY.finditer(tail))
    return [(m.group(1), tail[m.start():(starts[i + 1].start() if i + 1 < len(starts) else len(tail))])
            for i, m in enumerate(starts)]


def problems(name: str, text: str) -> list[str]:
    out = []
    for date, entry in history_entries(text):
        if date >= CUTOVER and len(entry.split()) > HISTORY_LIMIT:
            out.append(f"{name}: History entry {date} is {len(entry.split())} words "
                       f"(limit {HISTORY_LIMIT}); move the evidence into the section it changed")
    analyzed = ANALYZED_AT.search(text)
    if not analyzed or analyzed.group(1) < CUTOVER:
        return out
    for key in REQUIRED_FACTS:
        if not re.search(rf'^{key}:\s*"?[^"\s]', text, re.M):
            out.append(f"{name}: `{key}:` is empty or missing; the header band renders it")
    if (d := DESCRIPTION.search(text)):
        words = len(d.group(1).strip().strip('"').split())
        if words > DESCRIPTION_LIMIT:
            out.append(f"{name}: description is {words} words (limit {DESCRIPTION_LIMIT})")
    if (s := SUMMARY.search(text)) and (c := CENSUS.search(s.group(1))):
        out.append(f"{name}: summary opens with a census ('{c.group(0)}'); "
                   "move it to the size/activity frontmatter fields")
    return out


def self_test() -> int:
    long_desc = " ".join(["word"] * 26)
    facts = 'licence: "MIT"\nsize: "900 lines of Go"\nactivity: "12 commits by one author"\n'
    head = lambda date, desc="A store.": f"---\ndescription: \"{desc}\"\nanalyzed_at: {date}\n{facts}---\n"
    cases = [
        ("a new long description fails", head(CUTOVER, long_desc), 1),
        ("a new report with an empty fact fails",
         head(CUTOVER).replace('size: "900 lines of Go"', 'size: ""'), 1),
        ("an old long description passes", head("2026-01-01", long_desc), 0),
        ("a census in a new summary fails",
         head(CUTOVER) + "## 1. Executive Summary\n\nX is a store — 927 commits by thirteen authors.\n", 1),
        ("a census in the second paragraph passes",
         head(CUTOVER) + "## 1. Executive Summary\n\nX is a store.\n\nIt has 66,632 lines.\n", 0),
        ("a long new History entry fails",
         head("2026-01-01") + f"## History\n\n**{CUTOVER}** — " + " ".join(["w"] * 151) + "\n", 1),
        ("a long old History entry passes",
         head("2026-01-01") + "## History\n\n**2026-09-11** — " + " ".join(["w"] * 400) + "\n", 0),
        ("an entry ends at the next entry",
         head("2026-01-01") + f"## History\n\n**{CUTOVER}** — short.\n\n**2026-09-11** — "
         + " ".join(["w"] * 400) + "\n", 0),
    ]
    for name, text, expected in cases:
        got = len(problems("fixture", text))
        if got != expected:
            print(f"self-test failed: {name}: got {got} problems, expected {expected}", file=sys.stderr)
            return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main(root: str) -> int:
    found = []
    for path in sorted((Path(root) / "content" / "systems").glob("*.md")):
        found += problems(path.name, path.read_text(encoding="utf-8"))
    if found:
        print("Reports read or re-read since the cutover are out of reading order:", file=sys.stderr)
        for p in found:
            print(f"  {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--self-test" in args:
        sys.exit(self_test())
    sys.exit(main(next((a for a in args if not a.startswith("--")), ".")))

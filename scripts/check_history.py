#!/usr/bin/env python3
"""Assert every report's History section leads with the reading it is pinned to.

Each system report ends with `## History` — one dated entry per reading, newest
first. The section exists because re-review narration used to be written into
whatever paragraph it contradicted, and into two lists in `content/overview.md`
that had nothing to do with each other. A reader wanting "what changed since I
last looked" had to reconstruct it from prose spread across two files.

The invariant worth enforcing is small: **the newest History entry is the
current reading.** A re-pin that updates `revision` and `analyzed_at` without
adding an entry leaves a report whose body describes one commit and whose
history stops at an older one, which is the drift this section was added to
remove. Entries must also run newest-first, since a reader takes the top line as
current and nothing else signals the order.

Deliberately does not check prose. What an entry says is a judgement; that one
exists, and that it is dated today's pin, is not.

Usage: check_history.py <project-dir>
"""
import re
import sys
from pathlib import Path

ANALYZED_AT = re.compile(r"^analyzed_at:\s*(\d{4}-\d{2}-\d{2})\s*$", re.M)
HEADING = re.compile(r"^## History\s*$", re.M)
ENTRY = re.compile(r"^\*\*(\d{4}-\d{2}-\d{2})\*\*", re.M)


def main(root: str) -> int:
    systems = Path(root) / "content" / "systems"
    if not systems.is_dir():
        print(f"Missing {systems}", file=sys.stderr)
        return 1

    problems = []
    for report in sorted(systems.glob("*.md")):
        text = report.read_text(encoding="utf-8")
        analyzed = ANALYZED_AT.search(text)
        if not analyzed:
            continue  # analyzed_at's presence is asserted in test_site.sh
        analyzed = analyzed.group(1)

        heading = HEADING.search(text)
        if not heading:
            problems.append(
                f"{report.name}: no '## History' section. Add one, newest entry "
                f"first, starting with **{analyzed}** and the commit it was read at."
            )
            continue

        dates = ENTRY.findall(text[heading.end():])
        if not dates:
            problems.append(
                f"{report.name}: '## History' has no dated entries. Each is a "
                f"line beginning **YYYY-MM-DD**."
            )
            continue
        if dates[0] != analyzed:
            problems.append(
                f"{report.name}: newest History entry is {dates[0]} but "
                f"analyzed_at is {analyzed} — the re-pin did not record a reading"
            )
        if dates != sorted(dates, reverse=True):
            problems.append(
                f"{report.name}: History entries are not newest-first: "
                f"{', '.join(dates)}"
            )

    if problems:
        print("History sections are out of step with the reports they date:",
              file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

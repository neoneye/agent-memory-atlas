#!/usr/bin/env python3
"""Assert every report's History section records the reading it is pinned to.

Each system report ends with `## History` — one dated entry per reading, newest
first. The section exists because re-review narration used to be written into
whatever paragraph it contradicted, and into two lists in `content/overview.md`
that had nothing to do with each other. A reader wanting "what changed since I
last looked" had to reconstruct it from prose spread across two files.

The invariant worth enforcing is small: **some entry is dated `analyzed_at`.** A
re-pin that updates `revision` and `analyzed_at` without adding an entry leaves a
report whose body describes one commit and whose history stops at an older one,
which is the drift this section was added to remove. Entries must also run
newest-first, since a reader takes the top line as current and nothing else
signals the order.

Not "the newest entry is `analyzed_at`", because not every reading is a re-pin.
Mem0's `audit_log` mark was recovered on 2026-07-30 by re-reading one file at the
*same* commit — a real reading with a real outcome and no new sha to hang it on.
Requiring it to be the newest entry would have forced either a false
`analyzed_at` bump, claiming the whole report was re-read, or dropping the record
of a mark that had been wrong for two months. Both are worse than the weaker
invariant.

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
                f"first, including **{analyzed}** and the commit it was read at."
            )
            continue

        dates = ENTRY.findall(text[heading.end():])
        if not dates:
            problems.append(
                f"{report.name}: '## History' has no dated entries. Each is a "
                f"line beginning **YYYY-MM-DD**."
            )
            continue
        if analyzed not in dates:
            problems.append(
                f"{report.name}: no History entry dated {analyzed} (analyzed_at); "
                f"newest is {dates[0]} — the re-pin did not record a reading"
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

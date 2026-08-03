#!/usr/bin/env python3
"""Assert the repositories-inspected list agrees with every report's own pin.

`content/overview.md` publishes one line per repository — the project, and the
commit it was read at. That list is the atlas's claim about what was actually
read, and it is maintained by hand in a file thousands of lines away from the
frontmatter it has to agree with.

A first review writes the report and the list entry in one sitting, so they
match. A *re-review* updates `revision`, `revision_url` and `analyzed_at` in the
report and has to remember the list separately. On 3 August 2026 three entries
had drifted — daimon, verel and swafra — and all three were re-reviewed systems,
because that is the only population where this project's own process produces
the error. Nothing caught it: the existing checks validate revision metadata
*inside* a report, so both halves were internally consistent while the site made
two different claims about the same commit.

Also compares the displayed sha against the one in the link target, since a
correct-looking label over a stale href is the same failure wearing a disguise.

Usage: check_inspected_pins.py <project-dir>
"""
import re
import sys
from pathlib import Path

# - [owner/repo](https://…) at [`<sha>`](https://…/commit/<sha>)
ENTRY = re.compile(
    r"^- \[(?P<name>[^\]]+)\]\(https://[^)]+\) at "
    r"\[`(?P<shown>[0-9a-f]{7,40})`\]\((?P<href>https://[^)]+)\)",
    re.M,
)
SOURCE_NAME = re.compile(r'^source_name:\s*"?([^"\n]+?)"?\s*$', re.M)
REVISION = re.compile(r"^revision:\s*([0-9a-f]{40})\s*$", re.M)


def main(root: str) -> int:
    project = Path(root)
    overview = project / "content" / "overview.md"
    if not overview.is_file():
        print(f"Missing {overview}", file=sys.stderr)
        return 1

    listed = {
        m.group("name"): (m.group("shown"), m.group("href"))
        for m in ENTRY.finditer(overview.read_text(encoding="utf-8"))
    }
    if not listed:
        print(
            "No repositories-inspected entries parsed from content/overview.md. "
            "If the list's format changed, update ENTRY in this script rather "
            "than deleting the check.",
            file=sys.stderr,
        )
        return 1

    problems = []
    for report in sorted((project / "content" / "systems").glob("*.md")):
        text = report.read_text(encoding="utf-8")
        name = SOURCE_NAME.search(text)
        revision = REVISION.search(text)
        if not (name and revision):
            continue  # shape of the frontmatter is another check's job
        name, revision = name.group(1).strip(), revision.group(1)

        if name not in listed:
            problems.append(
                f"{report.name}: `{name}` has no entry in the "
                f"repositories-inspected list"
            )
            continue

        shown, href = listed[name]
        if not revision.startswith(shown):
            problems.append(
                f"{report.name}: list says {shown[:12]}, report pins "
                f"{revision[:12]} — the list was not updated with the re-review"
            )
        if not href.rstrip("/").endswith(shown):
            problems.append(
                f"{report.name}: `{name}` shows {shown[:12]} but links to "
                f"{href.rstrip('/').rsplit('/', 1)[-1][:12]}"
            )

    if problems:
        print(
            "The repositories-inspected list in content/overview.md disagrees "
            "with the reports it describes:",
            file=sys.stderr,
        )
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            "The list is the atlas's claim about what was read. Update the entry "
            "to the commit the report is pinned to.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

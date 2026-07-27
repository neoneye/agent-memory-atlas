#!/usr/bin/env python3
"""Keep the homepage in step with the reports.

The rendered-report count is derived, but the homepage is hand-written: its
cards and its "repositories traced" figure drift silently every time a system is
added. This asserts one card per report and a figure that matches the number of
distinct source repositories — distinct, because two reports can cover different
subsystems of one repository.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CARD = re.compile(r'href="\./systems/([^/"]+)/"')
TRACED = re.compile(r"<strong>(\d+)</strong><span>repositories traced</span>")
PATTERNS = re.compile(r"<strong>(\d+)</strong><span>reusable design patterns</span>")
SOURCE = re.compile(r"^source_url:\s*(\S+)\s*$", re.M)


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    homepage = (root / "site" / "index.html").read_text(encoding="utf-8")
    reports = sorted(p.stem for p in (root / "content" / "systems").glob("*.md"))

    problems: list[str] = []

    linked = set(CARD.findall(homepage))
    for slug in sorted(set(reports) - linked):
        problems.append(f"report with no homepage card: {slug}")
    for slug in sorted(linked - set(reports)):
        problems.append(f"homepage card with no report: {slug}")

    sources = {
        url.strip().rstrip("/")
        for path in (root / "content" / "systems").glob("*.md")
        for url in SOURCE.findall(path.read_text(encoding="utf-8"))
    }
    traced = TRACED.search(homepage)
    if traced is None:
        problems.append('homepage is missing the "repositories traced" figure')
    elif int(traced.group(1)) != len(sources):
        problems.append(
            f'homepage says {traced.group(1)} repositories traced; '
            f"{len(sources)} distinct source_url values across {len(reports)} reports"
        )

    expected_patterns = len(
        [p for p in (root / "content" / "patterns").glob("*.md") if p.stem != "index"]
    )
    stated = PATTERNS.search(homepage)
    if stated is None:
        problems.append('homepage is missing the "reusable design patterns" figure')
    elif int(stated.group(1)) != expected_patterns:
        problems.append(
            f"homepage says {stated.group(1)} design patterns; {expected_patterns} exist"
        )

    print("\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

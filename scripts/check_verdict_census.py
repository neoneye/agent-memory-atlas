#!/usr/bin/env python3
"""Assert every figure in a verdict's maturity line is one its report states.

`content/verdicts.md` carries a *Maturity impression* per system: licence,
commits, lines, tests, a version. Those figures are copied from the report when
the verdict is written, and a re-read then updates the report and leaves the
verdict behind. `check_verdict_marks.py` holds the mark count; nothing held the
rest. On 2026-09-25, 52 multi-digit figures in 40 maturity lines appeared
nowhere in their reports: stale test and commit counts (LoreKit's migrations,
Shodh's line count), and details the report never stated at all.

The rule is the one the verdicts page already implies: a verdict summarises its
report and may not carry a figure the report does not. A figure passes when the
report states it exactly (commas ignored), or states a figure within
TOLERANCE of it — a verdict may round, and a report may say "5,600" where the
verdict says 5,611.

Skipped: years, issue and PR numbers (`#737`), and anything that is part of a
version string. Figures under 100 are not checked; they are mostly counts a
reader can see are small, and the false-positive rate on them is high.

The hole it does not close: a figure can match an unrelated number in the
report (a line count equal to a test count). Matching is on the number, not
its unit.

Usage: check_verdict_census.py <project-dir>
       check_verdict_census.py --self-test
"""
import re
import sys
from pathlib import Path

TOLERANCE = 0.03
NUM = re.compile(r"(?<![\w.#])(\d{1,3}(?:,\d{3})+|\d{3,})(?![\w,%]|\.\d)")
YEAR = re.compile(r"^(19|20)\d\d$")
ANY = re.compile(r"\d[\d,]*\d|\d")


def report_numbers(text: str) -> set[int]:
    return {int(n.replace(",", "")) for n in ANY.findall(text) if n.replace(",", "").isdigit()}


def unmatched(line: str, report: str) -> list[str]:
    nums = report_numbers(report)
    out = []
    for x in NUM.findall(line):
        d = int(x.replace(",", ""))
        if YEAR.match(str(d)) or d in nums:
            continue
        if any(abs(n - d) <= TOLERANCE * d for n in nums if n >= 100):
            continue
        out.append(x)
    return out


def entries(verdicts: str):
    for block in re.split(r"^### ", verdicts, flags=re.M)[1:]:
        slug = re.match(r"\[`([a-z0-9-]+)`\]", block)
        line = re.search(r"^- Maturity impression:(.*)$", block, re.M)
        if slug and line:
            yield slug.group(1), line.group(1)


def self_test() -> int:
    report = "It has 21,444 lines, 212 tests and 1,310 commits at version 1.0.169."
    cases = [
        ("an exact figure passes", "212 tests", 0),
        ("commas are ignored", "21444 lines", 0),
        ("a rounding within tolerance passes", "about 21,000 lines", 0),
        ("a stale figure fails", "204 tests", 1),
        ("a figure the report lacks fails", "a 1,702-line doctor", 1),
        ("years, issues and versions are skipped", "since 2026, issue #737, v1.0.169", 0),
        ("small counts are not checked", "34 commits", 0),
    ]
    for name, line, expected in cases:
        got = len(unmatched(line, report))
        if got != expected:
            print(f"self-test failed: {name}: got {got}, expected {expected}", file=sys.stderr)
            return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main(root: str) -> int:
    project = Path(root)
    problems, checked = [], 0
    for slug, line in entries((project / "content" / "verdicts.md").read_text(encoding="utf-8")):
        report = project / "content" / "systems" / f"{slug}.md"
        if not report.is_file():
            continue
        checked += 1
        for x in unmatched(line, report.read_text(encoding="utf-8")):
            problems.append(f"{slug}: maturity line says {x}, which its report does not state")
    if problems:
        print("Verdict figures that their reports do not carry:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    print(f"{checked} verdict maturity lines carry only figures their reports state.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--self-test" in args:
        sys.exit(self_test())
    sys.exit(main(next((a for a in args if not a.startswith("--")), ".")))

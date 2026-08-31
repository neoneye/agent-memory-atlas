#!/usr/bin/env python3
"""Assert a verdict entry's stated mark count agrees with the report it describes.

`content/verdicts.md` carries one entry per system, and a re-analysis updates the
report, the comparative overview, the homepage card and the bound counts. The
verdicts entry was on none of those checklists, so an entry written at a first
reading kept its original mark count through every later pin, and nothing in the
build could see it.

Four were stale when this check was written on 2026-08-30, and the worst of them
argued *against* a mark the report awards:

  arcon                 "No capability mark."      report: three
  nova-ai               "four capability marks"    report: five
  lossless-context-mcp  "carries no capability mark …
                         history is a ring rather than an audit log"
                                                   report: audit_log, negative_eval
  nexusmem              "Four capability marks — …" report: six

Only a count stated in words or digits beside the phrase "capability mark(s)" or
"mark(s)" is checked. A count of something else in the same entry — test files,
commits, packages — never matches, and an entry that states no count at all is
not required to.

Two forms are deliberately *not* errors, because both are correct English for a
report that carries fewer than all of them:

  "six of seven capability marks"   — a fraction, checked against the numerator
  "none of the seven capability marks" — checked as zero

Usage: check_verdict_marks.py <project-dir>
       check_verdict_marks.py --self-test
"""
import re
import sys
from pathlib import Path

WORDS = {
    "zero": 0, "none": 0, "no": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7,
}

#: A count of marks: a number word or digit, optionally "of seven", then the
#: noun. The "of seven" branch is what keeps "six of seven capability marks"
#: reading as six rather than as seven.
COUNT = re.compile(
    r"\b(?P<num>" + "|".join(WORDS) + r"|\d)\b"
    r"(?:\s+of\s+(?:the\s+)?seven)?"
    r"\s+(?:capability\s+)?marks?\b",
    re.I,
)

#: "all seven marks" states the full set without a number word in front of the
#: noun, so it needs its own pattern.
ALL_SEVEN = re.compile(r"\ball seven\s+(?:capability\s+)?marks?\b", re.I)

#: Sentences where "no mark" or "earns no mark" is about one *mechanism* rather
#: than about the report's total — "which earns no mark here because an event
#: cannot turn out to be false". Checking those against the report total accuses
#: correct sentences, which is how a checker teaches people to ignore it.
MECHANISM_SCOPED = re.compile(
    r"(?:earns?|carries|worth)\s+no\s+(?:capability\s+)?mark\b"
    r"|no\s+(?:capability\s+)?mark\s+here\b",
    re.I,
)


def marks_in_report(path: Path) -> int | None:
    match = re.search(r'^capabilities: "(.*)"$', path.read_text(encoding="utf-8"), re.M)
    if match is None:
        return None
    return len([c for c in match.group(1).split(",") if c.strip()])


def entries(verdicts_text: str) -> dict[str, str]:
    blocks = re.split(r"^### \[`([a-z0-9-]+)`\]", verdicts_text, flags=re.M)
    return dict(zip(blocks[1::2], blocks[2::2]))


#: Markdown emphasis sits *inside* the phrase often enough to matter: the first
#: run of this check read "Carries **none** of the seven capability marks" as a
#: claim of seven, because the `**` broke the "none of the seven" branch and the
#: scan fell through to the bare noun. Its own self-test caught that before the
#: check shipped, which is the reason the self-test carries that exact sentence.
EMPHASIS = re.compile(r"[*_]+")


def claimed_in_line(line: str) -> tuple[int, str] | None:
    """Return (count, the matched phrase) for a line stating a mark count."""
    flat = EMPHASIS.sub("", line)
    if MECHANISM_SCOPED.search(flat):
        return None
    all_seven = ALL_SEVEN.search(flat)
    if all_seven:
        return 7, all_seven.group(0)
    match = COUNT.search(flat)
    if match is None:
        return None
    num = match.group("num").lower()
    value = WORDS.get(num)
    if value is None and num.isdigit():
        value = int(num)
    if value is None:
        return None
    return value, match.group(0)


def check(verdicts_text: str, report_marks: dict[str, int]) -> tuple[list[str], int]:
    """Problems, and how many entries actually stated a count to check.

    Every count-bearing line in an entry is checked, not just the first. The
    first version stopped at the first match, so a second statement later in the
    same entry — the "Six judgements each" format makes two natural, one in the
    best-idea line and one in the maturity impression — could disagree with the
    report and with the line above it and still pass.
    """
    problems = []
    stated = 0
    for slug, body in entries(verdicts_text).items():
        actual = report_marks.get(slug)
        if actual is None:
            continue
        claims = 0
        for line in body.splitlines():
            found = claimed_in_line(line)
            if found is None:
                continue
            claims += 1
            claimed, phrase = found
            if claimed != actual:
                problems.append(
                    f"{slug}: the verdict says {phrase!r}, the report carries {actual}"
                )
        if claims:
            stated += 1
    return problems, stated


def self_test() -> int:
    reports = {"a": 3, "b": 6, "c": 0, "d": 1, "e": 5}
    text = (
        "### [`a`](../systems/a/)\n- Maturity impression: 204 tests. No capability mark.\n\n"
        "### [`b`](../systems/b/)\n- Maturity impression: six of seven capability marks, 412 test files.\n\n"
        "### [`c`](../systems/c/)\n- Carries **none** of the seven capability marks, no memory tests.\n\n"
        "### [`d`](../systems/d/)\n- Section 9a describes the first, which earns no mark here because an event cannot turn out to be false.\n\n"
        # The regression: a correct count first, a stale one after it. Stopping
        # at the first match read this entry as agreeing with its report.
        "### [`e`](../systems/e/)\n- Best idea: five capability marks, one of them rare.\n"
        "- Maturity impression: four capability marks and 90 test files.\n"
    )
    problems, stated = check(text, reports)
    # `a` and the second line of `e` must be caught; `b`, `c` and `d` must not.
    caught = sorted(p.split(":")[0] for p in problems)
    if caught != ["a", "e"]:
        print("self-test failed: expected problems on 'a' and 'e', got:", problems, file=sys.stderr)
        return 1
    if stated != 4:
        print(f"self-test failed: expected 4 entries stating a count, got {stated}", file=sys.stderr)
        return 1
    print("self-test: 6 controls passed")
    return 0


def main(root: str) -> int:
    project = Path(root)
    verdicts = project / "content" / "verdicts.md"
    systems = project / "content" / "systems"
    if not verdicts.is_file():
        print(f"Missing {verdicts}", file=sys.stderr)
        return 1

    report_marks = {}
    for path in sorted(systems.glob("*.md")):
        count = marks_in_report(path)
        if count is not None:
            report_marks[path.stem] = count

    problems, stated = check(verdicts.read_text(encoding="utf-8"), report_marks)
    if problems:
        print("A verdict entry disagrees with the report it describes:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            "A re-analysis updates the report; the verdict entry has to move with it.",
            file=sys.stderr,
        )
        return 1

    # Count what was checked, not what was read. The first version printed the
    # whole roster as agreeing, including every entry that states no count and
    # is therefore never compared to anything.
    print(
        f"{stated} of {len(report_marks)} verdict entries state a mark count; "
        "all agree with their reports."
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

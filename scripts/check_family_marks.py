#!/usr/bin/env python3
"""Assert a family paragraph's mark count agrees with the report it describes.

`content/families.md` carries one hand-written paragraph per system, and most of
them state how many capability marks the system carries. The report's
`capabilities:` line is the count every generated surface reads; the paragraph
is a second copy that nothing compared. On 2026-09-25 thirteen paragraphs
disagreed with their reports — twelve after re-reads on 2026-09-17 to 2026-09-20
moved a mark and left the family paragraph alone, one (PLUR's) found by hand the
same day. Two had moved the other way: a tombstone and a review mark awarded,
with the paragraph still arguing their absence.

Only two phrasings are read, because they are the ones that say *carried*
without guessing, the ambiguity `check_mark_agreement.py` records for report
bodies ("N marks" can mean carried, withheld, the rubric's full set, or one
component's):

  - the fraction, "five of seven marks", anywhere in the paragraph;
  - a count opening a sentence and ending at punctuation — "Two marks.",
    "Three marks:", "All seven marks;", "No capability marks," — which in this
    file always states what the system carries.

A paragraph belongs to the system its opening bold link names. A count about a
different system inside it would be misread, and none does at the time of
writing; the self-test holds the forms.

Usage: check_family_marks.py <project-dir>
       check_family_marks.py --self-test
"""
import re
import sys
from pathlib import Path

WORDS = {w: i for i, w in enumerate("zero one two three four five six seven".split())}
WORDS.update({"no": 0, "all seven": 7})

LEAD = re.compile(r"\s*\*\*\[[^\]]+\]\(\.\./systems/([a-z0-9-]+)/\)")
FRACTION = re.compile(
    r"\b(no|zero|one|two|three|four|five|six|seven|all|\d)\s+of\s+(?:the\s+)?(?:seven|7)\s+"
    r"(?:rubric\s+|capability\s+)?(?:marks|mechanisms)\b", re.I)
OPENING = re.compile(
    r"(?:^|[.!?]\s+|\*\*\s*)(No|One|Two|Three|Four|Five|Six|Seven|All seven)\s+"
    r"(?:capability\s+)?marks?\b(?=[.,:;])")
CAPS = re.compile(r'^capabilities:\s*"([^"]*)"', re.M)


def claims(paragraph: str) -> list[tuple[int, str]]:
    out = []
    for rx in (FRACTION, OPENING):
        for m in rx.finditer(paragraph):
            word = m.group(1).lower()
            n = int(word) if word.isdigit() else WORDS.get(word, 7 if word == "all" else None)
            out.append((n, " ".join(m.group(0).split())))
    return out


def problems(families: str, marks: dict[str, int]) -> list[str]:
    out = []
    for para in re.split(r"\n\s*\n", families):
        lead = LEAD.match(para)
        if not lead or lead.group(1) not in marks:
            continue
        slug = lead.group(1)
        for n, text in claims(para):
            if n != marks[slug]:
                out.append(f"{slug}: says '{text}', report carries {marks[slug]}")
    return out


def self_test() -> int:
    marks = {"a": 2, "b": 7, "c": 0}
    cases = [
        ("an agreeing opening count passes", "**[A](../systems/a/) x.** Two marks. More.", 0),
        ("a stale opening count fails", "**[A](../systems/a/) x.** Three marks. More.", 1),
        ("a fraction is read", "**[A](../systems/a/) x.** It carries five of seven marks.", 1),
        ("all seven is seven", "**[B](../systems/b/) x.** All seven marks; more.", 0),
        ("no capability marks is zero", "**[C](../systems/c/) x.** No capability marks, each checked.", 0),
        ("a mid-sentence count is not read", "**[A](../systems/a/) x.** It withholds three marks for reasons.", 0),
        ("a paragraph without a system lead is skipped", "Three marks. More.", 0),
    ]
    for name, text, expected in cases:
        got = len(problems(text, marks))
        if got != expected:
            print(f"self-test failed: {name}: got {got}, expected {expected}", file=sys.stderr)
            return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main(root: str) -> int:
    project = Path(root)
    marks = {}
    for path in (project / "content" / "systems").glob("*.md"):
        m = CAPS.search(path.read_text(encoding="utf-8"))
        if m:
            marks[path.stem] = len([f for f in m.group(1).split(",") if f.strip()])
    families = (project / "content" / "families.md").read_text(encoding="utf-8")
    found = problems(families, marks)
    if found:
        print("Family paragraphs disagree with their reports' capabilities:", file=sys.stderr)
        for p in found:
            print(f"  {p}", file=sys.stderr)
        return 1
    n = sum(len(claims(p)) for p in re.split(r"\n\s*\n", families) if LEAD.match(p))
    print(f"{n} mark counts on the families page agree with their reports.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--self-test" in args:
        sys.exit(self_test())
    sys.exit(main(next((a for a in args if not a.startswith("--")), ".")))

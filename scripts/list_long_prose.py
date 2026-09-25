#!/usr/bin/env python3
"""Hold each report's long paragraphs and long sentences to a ratchet.

The 2026-09-07 reader feedback was that a report read as a wall of text. The
2026-09-17 split campaign cleared the worst paragraphs by hand, and with nothing
watching they came back: on 2026-09-25 the History sections alone held 864
paragraphs over 120 words, against 475 eight days earlier, because every re-pin
appends one and writes it as a single block.

**Per report, not a corpus total.** A total lets a new 300-word paragraph in
one report pass because someone split two old ones in another. Each report has
its own baseline in `prose_baseline.json`; a report with no entry — every new
report — has a baseline of zero. `--lower` is the only way the file changes,
and it can only lower.

**History counts.** It is where the paragraphs came back.

What a unit is: the Markdown body after the frontmatter, fenced code removed,
split on blank lines. Blocks opening with `#`, `|`, `>` or `<` are skipped. A
block of list items is split into one unit per item, because a bullet can carry
the same wall as a paragraph. Words are whitespace tokens. Sentences split on
`[.!?]` followed by whitespace and a capital, a backtick or `*`, which
over-splits on abbreviations, so the sentence count is a floor. (The
first version required a capital, backtick or `*` next, and merged sentences
that open with a link or a section sign; corrected the day it shipped.)

**The hole this does not close:** within a report that has a baseline, one long
paragraph can replace another at the same count. Nothing here says whether a
paragraph leads with its finding.

Usage: list_long_prose.py <project-dir>            report: totals and the ten longest
       list_long_prose.py --check <project-dir>    gate
       list_long_prose.py --lower <project-dir>    rewrite baseline, never upward
       list_long_prose.py --init <project-dir>     write baseline when none exists
       list_long_prose.py --self-test
"""
import json
import re
import sys
from pathlib import Path

PARAGRAPH_LIMIT = 150
SENTENCE_LIMIT = 60
BASELINE = Path(__file__).resolve().parent / "prose_baseline.json"

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
FENCE = re.compile(r"^```.*?^```[ \t]*$", re.S | re.M)
LIST_ITEM = re.compile(r"^(?:[-*+]|\d+\.)\s+")
SKIP = ("#", "|", ">", "<")
#: A sentence ends at [.!?], optionally closed by `**`, `*`, a quote or a
#: bracket, before whitespace and anything that does not start lowercase — so a
#: link, a section sign or a figure opening the next sentence still splits.
SENTENCE_END = re.compile(r"(?<=[.!?])(?:\*\*|\*|[\"”’)\]])?\s+(?=[^a-z\s])")


def units(text: str):
    """Every prose paragraph and list item in a report body, one string each."""
    body = FENCE.sub("", FRONTMATTER.sub("", text))
    for block in re.split(r"\n[ \t]*\n", body):
        lines = block.strip().split("\n")
        if not lines[0] or lines[0].lstrip().startswith(SKIP):
            continue
        item: list[str] = []
        for line in lines:
            stripped = line.strip()
            if LIST_ITEM.match(stripped):
                if item:
                    yield " ".join(item)
                item = [LIST_ITEM.sub("", stripped, count=1)]
            else:
                item.append(stripped)
        if item:
            yield " ".join(item)


def counts(text: str) -> tuple[int, int]:
    paragraphs = sentences = 0
    for unit in units(text):
        if len(unit.split()) > PARAGRAPH_LIMIT:
            paragraphs += 1
        sentences += sum(
            1 for s in SENTENCE_END.split(unit) if len(s.split()) > SENTENCE_LIMIT
        )
    return paragraphs, sentences


def measure(root: str) -> dict[str, tuple[int, int]]:
    systems = Path(root) / "content" / "systems"
    return {p.stem: counts(p.read_text(encoding="utf-8"))
            for p in sorted(systems.glob("*.md"))}


def load_baseline() -> dict[str, tuple[int, int]]:
    if not BASELINE.exists():
        return {}
    return {k: (v[0], v[1]) for k, v in json.loads(BASELINE.read_text()).items()}


def write_baseline(rows: dict[str, tuple[int, int]]) -> None:
    # One report per line, so a --lower shows up in a diff as the lines it moved.
    lines = [f"  {json.dumps(k)}: [{v[0]}, {v[1]}]"
             for k, v in sorted(rows.items()) if v != (0, 0)]
    BASELINE.write_text("{\n" + ",\n".join(lines) + "\n}\n")


def regressions(now, base) -> list[str]:
    out = []
    for slug, (p, s) in sorted(now.items()):
        bp, bs = base.get(slug, (0, 0))
        if p > bp:
            out.append(f"{slug}: {p} paragraphs over {PARAGRAPH_LIMIT} words, baseline {bp}")
        if s > bs:
            out.append(f"{slug}: {s} sentences over {SENTENCE_LIMIT} words, baseline {bs}")
    return out


def lowered(now, base) -> dict[str, tuple[int, int]]:
    return {slug: (min(now[slug][0], b[0]), min(now[slug][1], b[1]))
            for slug, b in base.items() if slug in now}


def self_test() -> int:
    words = lambda n: " ".join(["word"] * n)
    cases = [
        ("a 151-word paragraph counts", f"{words(151)}.\n", (1, 1)),
        ("a 151-word code block does not", f"```\n{words(151)}\n```\n", (0, 0)),
        ("a table row does not", f"| {words(151)} |\n", (0, 0)),
        ("two 80-word bullets are two units",
         f"- {words(80)}.\n- {words(80)}.\n", (0, 2)),
        ("a paragraph under History counts",
         f"## History\n\n**2026-09-25** {words(151)}.\n", (1, 1)),
        ("a sentence opening with a link still splits",
         f"{words(40)}. [A](x) {words(40)}. **B.** {words(40)}.\n", (0, 0)),
        ("three 55-word sentences are short",
         f"{words(55)}. A {words(54)}. A {words(54)}.\n", (1, 0)),
    ]
    for name, text, expected in cases:
        got = counts(text)
        if got != expected:
            print(f"self-test failed: {name}: got {got}, expected {expected}", file=sys.stderr)
            return 1
    if not regressions({"new": (1, 0)}, {}):
        print("self-test failed: a new report with a long paragraph passed", file=sys.stderr)
        return 1
    if regressions({"old": (3, 5)}, {"old": (3, 5)}):
        print("self-test failed: an unchanged report was flagged", file=sys.stderr)
        return 1
    if lowered({"old": (4, 1)}, {"old": (3, 5)}) != {"old": (3, 1)}:
        print("self-test failed: --lower raised an entry", file=sys.stderr)
        return 1
    print("self-test: 10 controls passed")
    return 0


def report(root: str) -> int:
    rows = []
    for path in sorted((Path(root) / "content" / "systems").glob("*.md")):
        for unit in units(path.read_text(encoding="utf-8")):
            rows.append((len(unit.split()), path.stem, unit[:70]))
    now = measure(root)
    print(f"{sum(p for p, _ in now.values())} paragraphs over {PARAGRAPH_LIMIT} words, "
          f"{sum(s for _, s in now.values())} sentences over {SENTENCE_LIMIT}, "
          f"in {sum(1 for v in now.values() if v != (0, 0))} reports\n")
    for n, slug, head in sorted(rows, reverse=True)[:10]:
        print(f"  {n:4}  {slug:32} {head}")
    return 0


def main(args: list[str]) -> int:
    root = next((a for a in args if not a.startswith("--")), ".")
    if "--self-test" in args:
        return self_test()
    now = measure(root)
    if "--init" in args:
        if BASELINE.exists():
            print(f"{BASELINE.name} exists; use --lower", file=sys.stderr)
            return 1
        write_baseline(now)
        return 0
    if "--lower" in args:
        write_baseline(lowered(now, load_baseline()))
        return 0
    if "--check" in args:
        problems = regressions(now, load_baseline())
        if problems:
            print("Long prose rose above its baseline. Split at a boundary the text "
                  "already has; do not edit the baseline upward.", file=sys.stderr)
            for p in problems:
                print(f"  {p}", file=sys.stderr)
            return 1
        print(f"long prose at or under baseline in {len(now)} reports")
        return 0
    return report(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

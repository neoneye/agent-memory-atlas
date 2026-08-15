#!/usr/bin/env python3
"""List corpus-scoped superlative claims, which nothing else in this build checks.

A superlative scoped to one repository — "the most valuable artifact in this
repository", "the only signal this system has" — is an ordinary judgement about
the thing under review, and the report's evidence supports it or does not.

A superlative scoped to the *corpus* is different in kind. "The only system in
this atlas that…", "the first report here to…", "nothing else in this corpus…"
are each an assertion about every report in the corpus at once. They are the sentences most
likely to be quoted, they are the ones a reader has no way to verify, and the
atlas has no mechanism that notices when one stops being true — a system added
next week can falsify a claim written today in a file nobody touches.

One was published on 2026-08-03 and retracted the same day: the memory-project
report called AGPL-3.0 "the most restrictive licence in this corpus" when five
other reports carry AGPL and six carry licences that are not open source at all.
It took one grep to disprove and had never had one.

**This is a reporting tool, not a gate.** It is deliberately not wired into
`npm test`, because a check that fails on several hundred pre-existing instances
teaches people to skip it. Run it when adding a report, or periodically, and treat the
output as a review list: for each hit, either the claim is checkable and should
be checked, or it is a judgement and should say so.

Usage: list_superlatives.py <project-dir> [--all]
       --all also lists repository-scoped superlatives, which are usually fine.
"""
import re
import sys
from pathlib import Path

SUPERLATIVE = (
    r"(the only|only system|the first|the most|the largest|the smallest|"
    r"the strongest|the weakest|the best|nothing else|no other|the sole|unique)"
)
CORPUS_SCOPE = (
    r"(in (this )?(atlas|corpus|set|batch)|in the atlas|here\b|of the \d+|"
    r"anywhere in this)"
)

CORPUS_CLAIM = re.compile(SUPERLATIVE + r"[^.\n]{0,90}?" + CORPUS_SCOPE, re.I)
ANY_CLAIM = re.compile(SUPERLATIVE, re.I)


def main(root: str, show_all: bool = False) -> int:
    content = Path(root) / "content"
    if not content.is_dir():
        print(f"Missing {content}", file=sys.stderr)
        return 1

    pattern = ANY_CLAIM if show_all else CORPUS_CLAIM
    rows = []
    for path in sorted(content.rglob("*.md")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            for match in pattern.finditer(line):
                rows.append((f"{path.relative_to(content)}:{lineno}", match.group(0)))

    scope = "superlatives of any scope" if show_all else "corpus-scoped superlatives"
    print(f"{len(rows)} {scope}\n")
    for location, text in rows:
        print(f"  {location:<38} {text[:100]}")

    if not show_all:
        print(
            f"\nEach of these asserts something about every report at once. None is "
            f"verified by anything in the build, and a report added later can "
            f"falsify one silently. Re-read them when the corpus grows."
        )
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    show_all = "--all" in args
    target = next((a for a in args if not a.startswith("--")), ".")
    sys.exit(main(target, show_all))

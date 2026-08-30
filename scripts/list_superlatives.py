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

**Listing is a reporting mode, not a gate**, because a check that fails on
several hundred pre-existing instances teaches people to skip it. `--check` is
the gate that was added on 2026-08-30, and it is a *ratchet* rather than a
threshold: the total may fall and may not rise. Nothing here can verify a
superlative — that needs a person or a grep per claim — so the gate stops the
pool growing while the pool is worked down by hand.

Two audits found what the absence of any gate cost. On 2026-08-03 the
memory-project report called AGPL-3.0 the most restrictive licence in the corpus,
with five other AGPL reports and six non-open-source ones sitting beside it. On
2026-08-30 the scope pattern page said MIRIX was the only system in the atlas
that tests a scope boundary, with around two dozen `negative_eval` records
describing exactly that test, and called its marks the rarest when it carries the
two most common. Both took one grep to disprove and neither had ever had one.

**The hole this gate does not close**, stated rather than hidden: a total ratchet
permits deleting one claim and adding another. It stops accumulation, which is
what actually happened — 537 of these accrued with nothing watching — and it does
not stop a single new claim from being wrong.

Usage: list_superlatives.py <project-dir> [--all]
       list_superlatives.py --check <project-dir>
       list_superlatives.py --self-test
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

#: Corpus-scoped superlatives standing when the ratchet was set. Lower it as
#: claims are checked and narrowed; --check fails if it rises. Never raise it to
#: admit a new claim — narrow the claim, or scope it to the system under review.
CORPUS_CLAIM_CEILING = 535


def count_corpus_claims(content: Path) -> list[tuple[str, str]]:
    rows = []
    for path in sorted(content.rglob("*.md")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            for match in CORPUS_CLAIM.finditer(line):
                rows.append((f"{path.relative_to(content)}:{lineno}", match.group(0)))
    return rows


def self_test() -> int:
    """The matcher must see a corpus claim and must not see a system-scoped one."""
    corpus = "It is the only system in this atlas that seals its own log."
    scoped = "It is the only writer that ever touches the table."
    if not CORPUS_CLAIM.search(corpus):
        print("self-test failed: a corpus-scoped superlative was not matched", file=sys.stderr)
        return 1
    if CORPUS_CLAIM.search(scoped):
        print("self-test failed: a system-scoped superlative was matched", file=sys.stderr)
        return 1
    print("self-test: 2 controls passed")
    return 0


def check(root: str) -> int:
    content = Path(root) / "content"
    rows = count_corpus_claims(content)
    if len(rows) > CORPUS_CLAIM_CEILING:
        print(
            f"corpus-scoped superlatives rose to {len(rows)} > {CORPUS_CLAIM_CEILING}.",
            file=sys.stderr,
        )
        print(
            "Each asserts something about every report at once and nothing in this "
            "build can verify one. Narrow the new claim, or scope it to the system "
            "under review; do not raise the ceiling to admit it.",
            file=sys.stderr,
        )
        return 1
    print(f"{len(rows)} corpus-scoped superlatives (ceiling {CORPUS_CLAIM_CEILING}).")
    return 0


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
    target = next((a for a in args if not a.startswith("--")), ".")
    if "--self-test" in args:
        sys.exit(self_test())
    if "--check" in args:
        sys.exit(check(target))
    sys.exit(main(target, "--all" in args))

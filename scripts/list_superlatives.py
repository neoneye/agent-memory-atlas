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
#: `here` needs a boundary on BOTH sides. Written as `here\b` it matched the tail
#: of "where", so "the only place where a mistake is permanent" — a quotation about
#: one repository's write path — was counted as a claim about every report at once.
CORPUS_SCOPE = (
    r"(in (this )?(atlas|corpus|set|batch)|in the atlas|\bhere\b|of the \d+|"
    r"anywhere in this)"
)

CORPUS_CLAIM = re.compile(SUPERLATIVE + r"[^.\n]{0,90}?" + CORPUS_SCOPE, re.I)
ANY_CLAIM = re.compile(SUPERLATIVE, re.I)

#: Corpus-scoped superlatives standing when the ratchet was set. Lower it as
#: claims are checked and narrowed; --check fails if it rises. Never raise it to
#: admit a new claim — narrow the claim, or scope it to the system under review.
#:
#: Set to 535 on 2026-08-30 and corrected to 459 the same day. The first figure
#: was the matcher's, not the corpus's: `here\b` matched the tail of "where", and
#: a superlative quoted from the repository under review was counted as the
#: atlas's own. Seventy-six of the 535 were one or the other. The ceiling is a
#: measurement of the prose and inherits every defect of the thing measuring it,
#: which is the argument for a self-test that carries the fixtures that were wrong.
CORPUS_CLAIM_CEILING = 459


#: A superlative the atlas *quotes* from the repository under review is that
#: project's claim about itself, not an assertion about every report at once —
#: which is the only thing this check exists to catch. Two verbatim quotations
#: pushed the total up by two on 2026-08-30, and the edit a ratchet invites for a
#: false positive is to alter the quotation, which is worse than the miscount.
#:
#: Matched over the whole file rather than per line, because the quotations that
#: caused it wrapped: the opening `*"` and the superlative sat on one line and the
#: closing quote on the next. Bounded at 800 characters so an unbalanced quote
#: swallows a paragraph rather than the rest of the file.
QUOTED = re.compile(r'"[^"]{0,800}?"|\u201c[^\u201d]{0,800}?\u201d', re.S)


def _quoted_spans(text: str) -> list[tuple[int, int]]:
    return [m.span() for m in QUOTED.finditer(text)]


def count_corpus_claims(content: Path) -> list[tuple[str, str]]:
    rows = []
    for path in sorted(content.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        spans = _quoted_spans(text)
        offset = 0
        for lineno, line in enumerate(text.split("\n"), 1):
            for match in CORPUS_CLAIM.finditer(line):
                start = offset + match.start()
                if any(lo <= start < hi for lo, hi in spans):
                    continue
                rows.append((f"{path.relative_to(content)}:{lineno}", match.group(0)))
            offset += len(line) + 1
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
    # "where" must not supply the corpus scope through its own tail.
    if CORPUS_CLAIM.search("the only place where a mistake is permanent"):
        print("self-test failed: 'where' was read as the scope word 'here'", file=sys.stderr)
        return 1
    # A quotation is the subject's claim about itself, not the atlas's about the corpus.
    quoted = 'The docstring says "it is the only thing here that has ever come back red".'
    spans = _quoted_spans(quoted)
    hit = CORPUS_CLAIM.search(quoted)
    if hit is None:
        print("self-test failed: the quoted fixture no longer matches at all", file=sys.stderr)
        return 1
    if not any(lo <= hit.start() < hi for lo, hi in spans):
        print("self-test failed: a superlative inside a quotation was counted", file=sys.stderr)
        return 1
    # And an unquoted one on a line that also carries a quotation must still count.
    mixed = 'It quotes "a thing" and is the only system in this atlas that does.'
    spans = _quoted_spans(mixed)
    hits = [m for m in CORPUS_CLAIM.finditer(mixed)
            if not any(lo <= m.start() < hi for lo, hi in spans)]
    if not hits:
        print("self-test failed: an unquoted claim beside a quotation was skipped", file=sys.stderr)
        return 1
    print("self-test: 5 controls passed")
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

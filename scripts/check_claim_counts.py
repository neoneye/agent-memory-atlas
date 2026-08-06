#!/usr/bin/env python3
"""Check hand-written mechanism counts against the frontmatter they describe.

`check_homepage.py` guards the *denominator* — the corpus total — because a file
count derives it. Nothing guarded the **numerator**, and the numerators are the
atlas's headline findings: "nine systems of one hundred and fifty-five carry a
tombstone" is the most-quoted sentence this project has.

On 2026-08-06 four of them were found stale in one page, the oldest by a whole
vintage: "148 reports across 147 repositories", "Seven systems in this entire
atlas can record that a value was rejected" (nine), "all 148 systems", "one
hundred and fifty-four systems". Each sat beside *generated* numbers that were
correct, which is what makes the class dangerous — a spelled count and a
generated one look identical to a reader, so stale prose inherits the
credibility of the machinery next to it.

What this checks: a number bound to one of the seven rubric mechanisms, against
the live count of reports carrying that capability flag. What it deliberately
does not check: numbers it cannot bind to a mechanism. Those are reported by
`--list` and never fail the build, because a checker that guesses at what a
sentence counts will eventually accuse a correct claim of being wrong — which
costs more than the drift it catches.

Usage:
    check_claim_counts.py [root] [--list]

`--list` prints every claim found, bound and unbound, with what it resolved to.
Read it after a prose rewrite: a claim that silently stops matching is exactly
the failure this script exists to prevent, one level up.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_homepage import _number_words  # noqa: E402
from generate_matrix import CAPABILITIES, read_capabilities  # noqa: E402

#: `_number_words` starts at ten, because below that a spelled number in this
#: atlas is usually a capability count that the homepage check has no business
#: guessing about. Here it is the opposite: the small numbers are the whole
#: point — the mechanisms worth counting are the rare ones.
WORDS = {
    **_number_words(10, 999),
    **{
        "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    },
}
#: First-match-wins alternation: "one hundred and five" must be offered before
#: "one hundred", or the long form is read as 100 and reported stale against a
#: live 105.
WORDS_BY_LENGTH = sorted(WORDS, key=len, reverse=True)
NUMBER = rf"(?:{'|'.join(WORDS_BY_LENGTH)}|\d{{1,3}})"
NOUNS = r"(?:memory\s+)?(?:systems?|repositories|repository|reports?)"

#: A claim is a number that either qualifies a countable atlas noun, or names a
#: denominator, or both. Requiring one of the two is what keeps ordinary prose
#: ("three steps", "two of the four engines") out of the results.
CLAIM = re.compile(
    rf"\b(?P<num>{NUMBER})\s+"
    rf"(?:(?P<noun1>{NOUNS})\s+)?"
    rf"(?:of\s+(?:the\s+)?(?P<denom>{NUMBER})\b)?"
    rf"(?:\s*(?P<noun2>{NOUNS})\b)?",
    re.I,
)

#: How a mechanism is named in prose, as opposed to how it is named in
#: frontmatter. Each phrase must be specific enough that its presence in the
#: sentence identifies the mechanism — "scope" alone is not, "scope key" is.
MECHANISM_PHRASES: dict[str, list[str]] = {
    "tombstone": [
        r"tombstones?",
        r"rejected[- ]value",
        r"value[- ]keyed refusals?",
        r"value was rejected",
        r"a value .{0,40}rejected",
    ],
    "trust_state": [
        r"discrete epistemic status",
        r"explicit trust states?",
        r"trust state",
        r"epistemic status as a field",
    ],
    "bitemporal": [r"bi[- ]?temporal"],
    "scope_enforced": [
        r"scope keys?",
        r"scope enforced",
        r"scope as a filter",
        r"scoped? .{0,20}on the read path",
    ],
    "audit_log": [
        r"append[- ]only .{0,30}audit",
        r"append[- ]only mutation",
        r"mutation audit",
        r"audit logs?",
    ],
    "human_review": [r"human review", r"review surface"],
    "negative_eval": [
        r"negative retrieval assertions?",
        r"negative evals?",
        r"negative[- ]eval",
        r"must not be retrieved",
        r"forbidden ?hits",
        r"asserting that particular material must",
    ],
}
#: Every literal space becomes `\s+` and `.` is allowed to cross a newline,
#: because these sentences are hard-wrapped at 80 columns and the wrap lands
#: wherever it lands. Written flat first, which silently missed "28 of 155
#: record a discrete\n   epistemic status" — the exact shape it exists to catch.
MECHANISM = {
    flag: re.compile("|".join(p.replace(" ", r"\s+") for p in phrases), re.I | re.S)
    for flag, phrases in MECHANISM_PHRASES.items()
}
LABELS = {flag: label for flag, label, _ in CAPABILITIES}

#: Windows are bounded by sentence, not by character count alone, so a mechanism
#: named in the *next* sentence cannot capture a number in this one. A table row
#: is its own boundary — `\n(?=\|)` — rather than every cell wall, because the
#: subject of a row is written in its first cell and the count in its last
#: ("Negative precision (forbidden hits) | … | Twenty-nine of one hundred and
#: fifty-five"). Splitting on every `|` left that one unchecked, and it was
#: stale.
BOUNDARY = re.compile(r"(?<=[.!?:])\s|\n\n|\n(?=\|)")
SENTENCE_AHEAD = BOUNDARY
SENTENCE_BEHIND = BOUNDARY
AHEAD_LIMIT = 220
BEHIND_LIMIT = 140

GENERATED = re.compile(
    r"<!-- BEGIN GENERATED.*?<!-- END GENERATED[^>]*-->", re.S
)
#: Whole files written by `generate_index.py`. Their numbers are derived, and
#: their per-system descriptions are not claims about the corpus — "RisuAI:
#: three memory systems, one repository" counts subsystems inside one report.
GENERATED_FILES = {"systems-index.md"}

#: A count scoped to something other than the corpus. "The closest near-miss of
#: the four systems in this batch" is a true sentence about a review round, and
#: reading it as a capability count is how a checker starts accusing correct
#: prose of being wrong.
LOCAL_SCOPE = re.compile(
    r"^\s*(?:in|of)?\s*(?:this|the)\s+(?:batch|round|family|section|report|repository|list|pair|group)",
    re.I,
)


def blank(text: str, span: tuple[int, int]) -> str:
    """Replace a span with spaces, preserving every offset after it."""
    start, end = span
    return text[:start] + re.sub(r"[^\n]", " ", text[start:end]) + text[end:]


def normalize(text: str) -> str:
    """Strip what markdown puts *inside* a sentence, keeping offsets aligned.

    Emphasis and code marks land in the middle of these claims — "a *value* was
    rejected", "`scope_enforced`" — and a phrase list that has to anticipate
    them is a phrase list that will miss one. Generated blocks are blanked
    entirely: checking derived numbers proves nothing, and counting them would
    inflate the coverage figure this script reports.
    """
    for match in GENERATED.finditer(text):
        text = blank(text, match.span())
    return re.sub(r"[*_`\[\]]", " ", text)


def live_counts(root: Path) -> tuple[dict[str, int], int, int]:
    paths = sorted((root / "content" / "systems").glob("*.md"))
    counts = {flag: 0 for flag, _, _ in CAPABILITIES}
    sources: set[str] = set()
    for path in paths:
        for flag in read_capabilities(path) or set():
            counts[flag] += 1
        found = re.search(r"^source_url:\s*(\S+)\s*$", path.read_text(encoding="utf-8"), re.M)
        if found:
            sources.add(found.group(1).rstrip("/"))
    return counts, len(paths), len(sources)


def window(text: str, start: int, end: int) -> tuple[str, str]:
    """The sentence fragments a claim may draw its subject from."""
    ahead = text[end : end + AHEAD_LIMIT]
    stop = SENTENCE_AHEAD.search(ahead)
    ahead = ahead[: stop.start()] if stop else ahead

    behind = text[max(0, start - BEHIND_LIMIT) : start]
    breaks = list(SENTENCE_BEHIND.finditer(behind))
    behind = behind[breaks[-1].end() :] if breaks else behind
    return ahead, behind


def bind(ahead: str, behind: str) -> str | None:
    """Which mechanism a claim is about, or None if the sentence does not say.

    Forward first. "Nine systems of one hundred and fifty-five carry a
    tombstone" names its subject after the number; the backward window exists
    for the inverted form ("the tombstone is carried by nine systems"), and a
    sentence naming two mechanisms is left unbound rather than guessed at.
    """
    for source in (ahead, behind):
        hits = {flag for flag, pattern in MECHANISM.items() if pattern.search(source)}
        if len(hits) == 1:
            return hits.pop()
        if len(hits) > 1:
            return None
    return None


def value(token: str) -> int:
    return int(token) if token.isdigit() else WORDS[token.lower()]


def check(root: Path, show_list: bool) -> int:
    counts, total_reports, total_repos = live_counts(root)
    problems: list[str] = []
    listed: list[str] = []
    bound = 0

    for source in sorted((root / "content").rglob("*.md")):
        if source.name in GENERATED_FILES:
            continue
        raw = source.read_text(encoding="utf-8")
        text = normalize(raw)
        where = source.relative_to(root)
        for match in CLAIM.finditer(text):
            noun = match.group("noun1") or match.group("noun2")
            denom = match.group("denom")
            # A number is a claim about the corpus if it counts atlas nouns or
            # names the corpus total. "One of two write paths" and "two of the
            # ten oldest pins" are neither, and every one of them was a false
            # positive on the first run of this check.
            if not noun and not (denom and value(denom) == total_reports):
                continue
            ahead, behind = window(text, match.start(), match.end())
            if LOCAL_SCOPE.match(ahead):
                continue
            flag = bind(ahead, behind)
            line = text[: match.start()].count("\n") + 1
            claim = " ".join(match.group(0).split())

            # Only the corpus total is ever this large, which keeps a paper's
            # own figures ("a benchmark of thirty tasks") out of the check.
            if denom is not None and value(denom) >= 40 and value(denom) != total_reports:
                problems.append(
                    f"{where}:{line}: '{claim}' — denominator {value(denom)}, "
                    f"live corpus is {total_reports} reports"
                )

            if flag is None:
                if show_list:
                    listed.append(f"{where}:{line}: '{claim}' — unbound, not checked")
                continue

            bound += 1
            said = value(match.group("num"))
            if show_list:
                listed.append(
                    f"{where}:{line}: '{claim}' — {LABELS[flag]}, said {said}, live {counts[flag]}"
                )
            if said != counts[flag]:
                problems.append(
                    f"{where}:{line}: '{claim}' — {LABELS[flag]} is carried by "
                    f"{counts[flag]} of {total_reports}, not {said}"
                )

    if show_list:
        print("\n".join(listed))
        print()

    print(
        f"{bound} mechanism count claims bound and checked "
        f"against {total_reports} reports over {total_repos} repositories."
    )

    # The failure this script is named after, one level up: if a prose rewrite
    # moves every claim out of reach of these phrases, the run goes green having
    # verified nothing — and a green check that checked nothing is worse than no
    # check, because it is quoted as evidence.
    if bound == 0:
        print(
            "NOTHING BOUND — no sentence in content/ was recognised as a mechanism "
            "count. This is not evidence that the counts are current; it is "
            "evidence that this checker has stopped reaching them.",
            file=sys.stderr,
        )
        return 1

    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


FIXTURE_REPORT = """---
title: Fixture {name}
capabilities: "{caps}"
source_url: https://example.invalid/{name}
---
"""


def self_test() -> int:
    """A positive control and a negative control, on a corpus of two.

    Everything else here reports what it found; nothing so far demonstrates
    that it can still *fail*. A checker whose regexes have rotted returns zero
    and looks identical to a clean tree — the tooling form of the lying
    operation this atlas names. So: build a two-report corpus where exactly one
    carries a tombstone, and assert that a page saying "One system carries a
    rejected-value tombstone" passes while "Two systems carry a rejected-value
    tombstone" fails.
    """
    import contextlib
    import io
    import tempfile

    cases = [
        ("One system carries a rejected-value tombstone.\n", 0, "correct count passes"),
        ("Two systems carry a rejected-value tombstone.\n", 1, "wrong count fails"),
        ("Memory is nice.\n", 1, "nothing bound is not a pass"),
    ]
    failures = []
    for prose, expected, label in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            systems = root / "content" / "systems"
            systems.mkdir(parents=True)
            (systems / "with.md").write_text(
                FIXTURE_REPORT.format(name="with", caps="tombstone"), encoding="utf-8"
            )
            (systems / "without.md").write_text(
                FIXTURE_REPORT.format(name="without", caps=""), encoding="utf-8"
            )
            (root / "content" / "page.md").write_text(prose, encoding="utf-8")
            # The controls are expected to fail loudly; their output would read
            # as real findings in a build log.
            noise = io.StringIO()
            with contextlib.redirect_stdout(noise), contextlib.redirect_stderr(noise):
                actual = check(root, show_list=False)
            if actual != expected:
                failures.append(
                    f"{label}: expected exit {expected}, got {actual}\n{noise.getvalue()}"
                )
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main() -> int:
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--self-test" in flags:
        return self_test()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else Path(__file__).resolve().parent.parent
    return check(root, "--list" in flags)


if __name__ == "__main__":
    raise SystemExit(main())

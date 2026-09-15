#!/usr/bin/env python3
"""Keep the homepage in step with the reports.

The rendered-report count is derived, but the homepage is hand-written: its
cards and its headline figure drift silently every time a system is added. This
asserts one card per report, headline figures written as placeholders, and no
corpus count written by hand anywhere in the prose.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CARD = re.compile(r'href="\./systems/([^/"]+)/"')
ARTICLE = re.compile(r'<article class="system-card[^"]*"[^>]*>.*?</article>', re.S)
CAPS_ATTR = re.compile(r'data-capabilities="([^"]*)"')
#: The headline stat is the report count and nothing else. It once carried the
#: distinct-repository count beside it, on the reasoning that a reader seeing one
#: number would read the other as an off-by-one — but the two differ by one, both
#: are true, and a strip of single figures is not the place to explain why. The
#: difference is stated where it can be argued: "Why the two counts differ" in
#: `content/overview.md`. Distinct `source_url` values are still counted here,
#: because that is the check that catches a report added under an existing
#: repository, and the number is reported rather than asserted against the page.
TRACED = re.compile(r"<strong>([^<]+)</strong><span>memory systems reviewed</span>")
PATTERNS = re.compile(r"<strong>([^<]+)</strong><span>reusable design patterns</span>")
SOURCE = re.compile(r"^source_url:\s*(\S+)\s*$", re.M)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from placeholders import TOKEN, counts as placeholder_counts  # noqa: E402

#: Corpus counts are written as `PLACEHOLDER_*` tokens and filled in by the build
#: (`placeholders.py`), so they cannot go stale. This used to be a stale-count
#: check that recognised every spelled-out number from sixteen to 999 — an
#: alternation of nearly two thousand phrases run over every page, which is what
#: kept a CPU busy for minutes. What is left to catch is a count written by hand.
#: Each rule anchors on a literal word — the noun, "of", "hundred" — and inspects
#: only the few characters before it. Scanning for a leading number instead tries
#: every position in every page.
NOUN = re.compile(r"\b(?:systems|reports|repositories)\b")
DIGIT_BEFORE_NOUN = re.compile(r"(?:^|[^\d,.#/-])(\d{2,3})\s+(?:memory\s+)?\Z")
SPELLED_BEFORE_NOUN = re.compile(
    r"\b(?:(?:one|two|three|four|five|six|seven|eight|nine)\s+hundred(?:\s+and\s+[a-z]+(?:-[a-z]+)?)?"
    r"|(?:forty|fifty|sixty|seventy|eighty|ninety)(?:-[a-z]+)?)\s+(?:memory\s+)?\Z",
    re.I,
)
#: "44 of 469", "237 of the 469" — a denominator this large is only ever the corpus.
DIGIT_DENOMINATOR = re.compile(r"\bof\s+(?:the\s+)?(\d{2,3})\b(?![,.]\d|%)")
NUMERATOR_BEFORE = re.compile(r"(?:^|[^\w,.])\d{1,3}\s+\Z")
#: "of four hundred and sixty-nine". Reports legitimately write "two hundred
#: lines", so a spelled hundred is only flagged as a denominator.
HUNDRED = re.compile(r"\bhundred\b", re.I)
SPELLED_DENOMINATOR_BEFORE = re.compile(
    r"\bof\s+(?:the\s+)?(?:one|two|three|four|five|six|seven|eight|nine)\s+\Z", re.I
)
GENERATED = re.compile(r"<!-- BEGIN GENERATED.*?<!-- END GENERATED[^>]*-->", re.S)
#: A paragraph that cites an external work states that work's numbers ("269 of 435").
EXTERNAL = re.compile(r"arxiv\.org|arXiv:|doi\.org", re.I)
#: A dated history entry records a past count on purpose.
DATED_ENTRY = re.compile(r"^[ \t\n*-]*\d{4}-\d{2}-\d{2}\b")
#: Pages written by a generator from live counts.
GENERATED_FILES = {"systems-index.md"}
#: Below this a count of systems is a finding about a handful ("12 systems"), not
#: a statement about the corpus.
CORPUS_FLOOR = 40


def exempt_spans(text: str) -> list[tuple[int, int]]:
    spans, cursor = [], 0
    for para in text.split("\n\n"):
        if EXTERNAL.search(para) or DATED_ENTRY.match(para):
            spans.append((cursor, cursor + len(para)))
        cursor += len(para) + 2
    return spans


def hand_written_counts(root: Path, values: dict[str, int]) -> list[str]:
    """Corpus counts written as numbers instead of placeholders, and unknown tokens."""
    found: list[str] = []
    sources = [root / "site" / "index.html", root / "AGENTS.md"]
    sources += [p for p in sorted((root / "content").rglob("*.md")) if p.name not in GENERATED_FILES]
    for source in sources:
        if not source.exists():
            continue
        raw = source.read_text(encoding="utf-8")
        text = GENERATED.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), raw)
        exempt = exempt_spans(text)
        where = source.relative_to(root)

        def report(match: re.Match[str], why: str) -> None:
            if any(start <= match.start() < end for start, end in exempt):
                return
            line = text[: match.start()].count("\n") + 1
            found.append(f"{where}:{line}: '{' '.join(match.group(0).split())}' — {why}")

        for match in TOKEN.finditer(text):
            if match.group(0) not in values:
                report(match, "unknown placeholder")
        for match in NOUN.finditer(text):
            before = text[max(0, match.start() - 60) : match.start()]
            digit = DIGIT_BEFORE_NOUN.search(before)
            if digit and int(digit.group(1)) >= CORPUS_FLOOR:
                report(match, f"{digit.group(1)} {match.group(0)} is a corpus count written by hand; use a PLACEHOLDER_* token")
            elif SPELLED_BEFORE_NOUN.search(before):
                report(match, "a spelled-out corpus count; use a PLACEHOLDER_* token")
        for match in DIGIT_DENOMINATOR.finditer(text):
            before = text[max(0, match.start() - 12) : match.start()]
            if int(match.group(1)) >= CORPUS_FLOOR and NUMERATOR_BEFORE.search(before):
                report(match, "a corpus denominator written by hand; use PLACEHOLDER_TOTAL_COUNT")
        for match in HUNDRED.finditer(text):
            if SPELLED_DENOMINATOR_BEFORE.search(text[max(0, match.start() - 30) : match.start()]):
                report(match, "a spelled-out denominator; use PLACEHOLDER_TOTAL_COUNT")
    return found


def self_test() -> int:
    """Positive and negative controls for `hand_written_counts` on a one-report corpus."""
    import tempfile

    cases = [
        ("469 systems were read.\n", True, "digits before an atlas noun"),
        ("44 of 469 carry it.\n", True, "digit denominator"),
        ("four hundred and sixty-nine systems.\n", True, "spelled count before a noun"),
        ("Forty-four systems carry it.\n", True, "spelled tens before a noun"),
        ("It is one of four hundred.\n", True, "spelled denominator"),
        ("PLACEHOLDER_TOTAL_COUNT systems and PLACEHOLDER_BOGUS_COUNT.\n", True, "unknown token"),
        ("PLACEHOLDER_PATTERN_TOMBSTONE_COUNT of PLACEHOLDER_TOTAL_COUNT systems.\n", False, "tokens pass"),
        ("It has two hundred lines and a macro F1 of 96%.\n", False, "ordinary numbers pass"),
        ("12 systems carry it.\n", False, "a small finding is not a corpus count"),
        ("2026-09-15 — the atlas held 469 reports.\n", False, "a dated history entry is exempt"),
        ("A survey at arXiv:2601.00001 coded 269 of 435 works.\n", False, "a cited corpus is exempt"),
    ]
    failures = []
    for text, flagged, label in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "content" / "systems").mkdir(parents=True)
            (root / "content" / "patterns").mkdir()
            (root / "content" / "systems" / "a.md").write_text(
                '---\ncapabilities: "tombstone"\nsource_url: https://example.invalid/a\n---\n',
                encoding="utf-8",
            )
            (root / "content" / "page.md").write_text(text, encoding="utf-8")
            found = hand_written_counts(root, placeholder_counts(root))
            if bool(found) != flagged:
                failures.append(f"{label}: expected {'a finding' if flagged else 'none'}, got {found}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return self_test()
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
        problems.append('homepage is missing the "N memory systems reviewed" figure')
    else:
        if traced.group(1) != "PLACEHOLDER_TOTAL_COUNT":
            problems.append(
                f'homepage states "{traced.group(1)} memory systems reviewed"; write '
                f"PLACEHOLDER_TOTAL_COUNT (content has {len(reports)} reports over "
                f"{len(sources)} distinct source_url values)"
            )

    # The capability filter reads data-capabilities off each card, so a card
    # whose attribute drifts from its report silently filters wrong.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_matrix import read_capabilities  # type: ignore[attr-defined]

    for card in ARTICLE.findall(homepage):
        slug_match = CARD.search(card)
        attr = CAPS_ATTR.search(card)
        if slug_match is None:
            continue
        slug = slug_match.group(1)
        declared = read_capabilities(root / "content" / "systems" / f"{slug}.md")
        if declared is None:
            continue
        stamped = set(attr.group(1).split()) if attr else set()
        if stamped != declared:
            problems.append(
                f"{slug}: card data-capabilities {sorted(stamped)} "
                f"does not match report {sorted(declared)}"
            )

    problems.extend(hand_written_counts(root, placeholder_counts(root)))
    stated = PATTERNS.search(homepage)
    if stated is None:
        problems.append('homepage is missing the "reusable design patterns" figure')
    elif stated.group(1) != "PLACEHOLDER_DESIGN_PATTERN_COUNT":
        problems.append(
            f'homepage states "{stated.group(1)} reusable design patterns"; '
            "write PLACEHOLDER_DESIGN_PATTERN_COUNT"
        )

    print("\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

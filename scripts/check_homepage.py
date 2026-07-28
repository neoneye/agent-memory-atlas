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
ARTICLE = re.compile(r'<article class="system-card[^"]*"[^>]*>.*?</article>', re.S)
CAPS_ATTR = re.compile(r'data-capabilities="([^"]*)"')
TRACED = re.compile(r"<strong>(\d+)</strong><span>repositories traced</span>")
PATTERNS = re.compile(r"<strong>(\d+)</strong><span>reusable design patterns</span>")
SOURCE = re.compile(r"^source_url:\s*(\S+)\s*$", re.M)


WORDS = {
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "forty-five": 45, "forty-six": 46, "forty-seven": 47, "forty-eight": 48,
    "forty-nine": 49, "fifty": 50, "fifty-one": 51, "fifty-two": 52,
    "fifty-three": 53, "fifty-four": 54, "fifty-five": 55, "fifty-six": 56,
    "fifty-seven": 57, "fifty-eight": 58, "fifty-nine": 59, "sixty": 60,
}


def stale_number_words(root: Path, live: set[int]) -> list[str]:
    """Spelled-out counts of atlas nouns that no longer match anything live.

    These have drifted three times, each caught by a reader rather than the
    build, and twice because a manual sweep was case-sensitive.

    Only number-words immediately qualifying a thing the atlas counts are
    checked. A first attempt flagged every number-word in prose and was useless:
    "twenty-plus lifecycle events" and "sixty iterations" are not counts of
    anything, and a bare \b also matched "fifty" inside "fifty-eight".
    """
    nouns = r"(?:memory )?(?:systems|reports|repositories|patterns|design patterns)"
    patterns = [
        # "fifty-eight systems" — the number qualifies the noun.
        re.compile(rf"\b({'|'.join(WORDS)})\b(?!-)(?:\s+\w+){{0,3}}?\s+{nouns}\b", re.I),
        # "two systems of fifty-eight" — the number is the DENOMINATOR, and sits
        # after the noun. The first version of this check only looked forward, so
        # it read straight past three of these and an outside reviewer quoted the
        # stale figure back at the atlas.
        re.compile(rf"\bof\s+({'|'.join(WORDS)})\b(?!-)", re.I),
    ]
    # "1 of 58" in digits. Bounded to denominators of forty or more because the
    # only atlas count that large is the system total, which keeps this away from
    # ordinary prose like "two of five backends".
    digits = re.compile(r"\b\d+\s+of\s+(\d{2,3})\b")

    found: list[str] = []
    for source in [root / "site" / "index.html"] + sorted((root / "content").rglob("*.md")):
        text = source.read_text(encoding="utf-8")
        for pattern in patterns:
            for match in pattern.finditer(text):
                value = WORDS[match.group(1).lower()]
                if value in live:
                    continue
                line = text[: match.start()].count("\n") + 1
                found.append(
                    f"{source.relative_to(root)}:{line}: '{match.group(0).strip()}' "
                    f"is a stale count (live: {sorted(live)})"
                )
        for match in digits.finditer(text):
            value = int(match.group(1))
            if value < 40 or value in live:
                continue
            line = text[: match.start()].count("\n") + 1
            found.append(
                f"{source.relative_to(root)}:{line}: '{match.group(0).strip()}' "
                f"is a stale count (live: {sorted(live)})"
            )
    return found


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

    expected_patterns = len(
        [p for p in (root / "content" / "patterns").glob("*.md") if p.stem != "index"]
    )

    problems.extend(
        stale_number_words(root, {len(reports), expected_patterns, len(sources)})
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

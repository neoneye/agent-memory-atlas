#!/usr/bin/env python3
"""Keep the homepage in step with the reports.

The rendered-report count is derived, but the homepage is hand-written: its
cards and its headline figure drift silently every time a system is added. This
asserts one card per report and a headline figure that matches the number of
reports.
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
TRACED = re.compile(r"<strong>(\d+)</strong><span>memory systems reviewed</span>")
PATTERNS = re.compile(r"<strong>(\d+)</strong><span>reusable design patterns</span>")
SOURCE = re.compile(r"^source_url:\s*(\S+)\s*$", re.M)


def _number_words(lo: int, hi: int) -> dict[str, int]:
    """Spelled-out numbers in the range this atlas counts things in.

    Hand-maintained until the list stopped at sixty while the corpus passed
    eighty, which is how "Four repositories of eighty" and "Seventy-three
    systems do not fall into eighty-five categories" both survived a green
    build. A generated range cannot fall behind the same way.

    Deliberately starts at sixteen. Below that, spelled-out numbers in this
    atlas are usually capability counts ("three systems carry a tombstone")
    that `live` does not know about, and flagging them produced nothing but
    noise the first time it was tried.
    """
    units = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    teens = {
        10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
        15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
    }
    tens = {
        2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty",
        7: "seventy", 8: "eighty", 9: "ninety",
    }
    words = {}
    for n in range(lo, hi + 1):
        if n in teens:
            words[teens[n]] = n
        elif n < 100:
            t, u = divmod(n, 10)
            words[tens[t] + ("-" + units[u] if u else "")] = n
        elif n == 100:
            words["one hundred"] = n
        else:
            # Past one hundred the same failure waits: a range that stops
            # where the corpus currently is stops checking the moment it is
            # passed. "one hundred and one" and "one hundred one" are both
            # written in practice, so accept both spellings.
            h, rem = divmod(n, 100)
            head = units[h] + " hundred"
            if rem == 0:
                words[head] = n
            else:
                if rem in teens:
                    tail = teens[rem]
                else:
                    t, u = divmod(rem, 10)
                    tail = units[u] if t == 0 else tens[t] + ("-" + units[u] if u else "")
                words[f"{head} and {tail}"] = n
                words[f"{head} {tail}"] = n
    return words


WORDS = _number_words(16, 999)

#: Alternation order matters: regex alternation is first-match-wins, so a short
#: form that prefixes a longer one wins and mis-reads it. Without this, "one
#: hundred and five" matches the "one hundred" branch and is reported stale
#: against a live 105 — the check accusing a correct count of being wrong.
WORDS_BY_LENGTH = sorted(WORDS, key=len, reverse=True)

#: Every literal space inside a spelled number matches a space *or* a newline.
#: Prose here is hard-wrapped, and *"of two hundred and\nninety"* against a
#: literal-space alternation matches only "of two hundred" — the same
#: first-match-wins truncation the length sort above prevents, arriving through
#: the line wrap instead. It reported a correct 290 as a stale 200.
#:
#: One character, not `\s+`. A quantifier here makes every one of the ~1,000
#: alternatives ambiguous about where it ends, and the following
#: `(?:\s+\w+){0,3}?\s+` re-splits the same whitespace — the two together took
#: this check from milliseconds to not finishing. A wrap produces exactly one
#: whitespace character where the space was, so one is all that is needed.
WORDS_WRAPPED = [w.replace(" ", "[ \n]") for w in WORDS_BY_LENGTH]

#: Matches the " of <number>" that turns a preceding count into the numerator of
#: a subset claim ("Sixteen repositories of one hundred and thirteen"). Allows a
#: line break, because these sentences wrap.
SUBSET_TAIL = re.compile(rf"\s+of\s+(?:{'|'.join(WORDS_WRAPPED)}|\d+)\b", re.I)


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
        re.compile(rf"\b({'|'.join(WORDS_WRAPPED)})\b(?!-)(?:\s+\w+){{0,3}}?\s+{nouns}\b", re.I),
        # "two systems of fifty-eight" — the number is the DENOMINATOR, and sits
        # after the noun. The first version of this check only looked forward, so
        # it read straight past three of these and an outside reviewer quoted the
        # stale figure back at the atlas.
        re.compile(rf"\bof\s+({'|'.join(WORDS_WRAPPED)})\b(?!-)", re.I),
    ]
    # "1 of 58" in digits. Bounded to denominators of forty or more because the
    # only atlas count that large is the system total, which keeps this away from
    # ordinary prose like "two of five backends".
    #
    # The optional "the" is load-bearing: the verdicts section opened with "64 of
    # the 97 reports" and drifted to 115 reports unnoticed, because the article
    # broke the match. Any determiner between the two numbers hides a count.
    digits = re.compile(r"\b\d+\s+of\s+(?:the\s+)?(\d{2,3})\b")

    # A paragraph citing an external work states that work's numbers. The floor
    # above ("only the system total is ever this large") stopped being true the
    # day this atlas started comparing itself to a survey that coded 435 works:
    # "retrieve appears in 269 of 435" clears every floor and is nobody's stale
    # count. Exempt only a denominator that is not one of our live totals, so a
    # real corpus count sitting beside a citation is still checked.
    external = re.compile(r"arxiv\.org|arXiv:|doi\.org", re.I)

    def cited_spans(text: str) -> list[tuple[int, int]]:
        spans, cursor = [], 0
        for para in text.split("\n\n"):
            if external.search(para):
                spans.append((cursor, cursor + len(para)))
            cursor += len(para) + 2
        return spans

    found: list[str] = []
    for source in [root / "site" / "index.html"] + sorted((root / "content").rglob("*.md")):
        text = source.read_text(encoding="utf-8")
        cited = cited_spans(text)
        for index, pattern in enumerate(patterns):
            for match in pattern.finditer(text):
                # Collapse a wrapped spelled number back to its `WORDS` key.
                value = WORDS[" ".join(match.group(1).split()).lower()]
                if value in live:
                    continue
                # The bare "of N" form is noun-blind, so it reads a research
                # paper's own figures as atlas counts — "a simulation of
                # twenty-five agents" is not a claim about this corpus. Apply
                # the same floor the digit rule below already uses: only the
                # system total is ever this large.
                if index == 1 and value < 40:
                    continue
                # "Sixteen repositories of one hundred and thirteen" — the
                # forward pattern reads the NUMERATOR of a subset claim, which is
                # a true count of a subset and never equals a live total. Only
                # the denominator is a claim about the corpus, and the second
                # pattern already checks it. Skip the numerator when an "of
                # <number>" follows, so a subset that grows past the dictionary
                # floor of sixteen does not start failing the build.
                #
                # Test from the end of the NUMBER, not the end of the whole
                # match: pattern 0 allows up to three words between the number
                # and the noun, so "Twenty of three hundred systems" matches to
                # the end of "systems" and the tail check looked past the
                # denominator it was meant to find. It only ever passed because
                # every denominator so far was long enough to overflow that
                # three-word window — "two hundred and ninety-nine" is five
                # words, "three hundred" is two, and the corpus reaching a round
                # hundred is what exposed it.
                # Two shapes put the denominator in different places —
                # "Twenty of three hundred systems" (tail after the number) and
                # "Twenty systems of 300" (tail after the noun) — so both
                # positions are tried.
                if index == 0 and (SUBSET_TAIL.match(text, match.end(1))
                                   or SUBSET_TAIL.match(text, match.end())):
                    continue
                if any(start <= match.start() < end for start, end in cited):
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
            if any(start <= match.start() < end for start, end in cited):
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
        problems.append('homepage is missing the "N memory systems reviewed" figure')
    else:
        said_reports = int(traced.group(1))
        if said_reports != len(reports):
            problems.append(
                f"homepage says {said_reports} memory systems reviewed; "
                f"content has {len(reports)} reports over {len(sources)} distinct source_url values"
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

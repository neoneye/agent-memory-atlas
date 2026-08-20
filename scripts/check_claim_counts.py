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
#: Spaces inside a spelled number match a space *or* a newline. Prose wraps, and
#: *"two hundred and\nninety"* with a literal-space alternation matches only
#: "two hundred" — the long form losing to a prefix, which is the exact failure
#: the length sort above exists to prevent, arriving through the line wrap
#: instead. It read a live 290 as a claimed 200 and reported a correct sentence
#: stale.
#:
#: One character, not `\s+`: a quantifier makes each of the ~1,000 alternatives
#: ambiguous about where it ends, and the `\s+` separators around it in `CLAIM`
#: re-split the same whitespace. A wrap leaves exactly one whitespace character.
NUMBER = rf"(?:{'|'.join(w.replace(' ', '[ \n]') for w in WORDS_BY_LENGTH)}|\d{{1,3}})"
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

#: A mechanism used as the countable noun itself: "three tombstones", "six
#: negative-eval suites". The first version of this check required an atlas noun
#: (systems, reports, repositories) or the corpus denominator, and so read
#: straight past *"the atlas's headline counts — three tombstones, six
#: negative-eval suites"* in the limitations, where both numbers were stale by
#: six and twenty-four. An outside reviewer found it the day this script
#: shipped, which is the second time the numerator has been caught by a reader.
#:
#: Only two mechanisms qualify, and the exclusions are the interesting part.
#: "Four scope keys" and "three trust states" count things *inside* one system —
#: EverOS has four scope keys, PowerMem three — so reading them as corpus counts
#: made this check accuse five correct sentences at once on its first run. A
#: mechanism noun is usable here only when its plural is never a within-system
#: quantity, which is true of a tombstone and of an eval suite and of nothing
#: else on the rubric.
#:
#: Even for those two the restriction is not enough on its own, because a report
#: may legitimately say a *store* holds two tombstones. So a mechanism-noun claim
#: must also carry a corpus marker in its sentence — the same discipline the
#: windowed matcher gets for free by requiring a mechanism to be named beside an
#: atlas noun. Without it this branch was the one part of the checker with no way
#: to tell "nine tombstones in the atlas" from "two tombstones in this table".
MECHANISM_NOUNS: dict[str, str] = {
    "tombstone": r"tombstones?",
    "negative_eval": r"negative[- ]eval(?:uation)? suites?|negative[- ]evals",
}
MECHANISM_NOUN_CLAIM = re.compile(
    rf"\b(?P<num>{NUMBER})\s+(?P<mech>"
    + "|".join(f"(?P<{flag}>{pattern})" for flag, pattern in MECHANISM_NOUNS.items())
    + r")\b",
    re.I,
)
#: What makes a sentence a statement about the corpus rather than about one
#: system. Deliberately short: every phrase here is one the atlas only writes
#: when it is counting across reports.
CORPUS_MARKER = re.compile(
    r"\batlas\b|\bcorpus\b|systems here|reports here|headline counts"
    r"|of\s+(?:the\s+)?(?:\d{2,3}|one hundred and [a-z-]+)",
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
        # The 2026-08-08 re-score found ten of the 37 keep material out of a
        # projection or a preamble rather than out of a query result, so the
        # headline verb changed from "retrieved" to "appear" — and the claim it
        # sits in silently fell out of this checker's reach for one commit.
        # A phrase list is only as good as the prose it was written against.
        r"must not appear",
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


#: A pattern page whose whole subject is one rubric mechanism. On these pages
#: the mechanism is usually a pronoun — *"Nineteen systems of two hundred and
#: ninety carry it"*, *"Nineteen systems in the atlas have this"* — because
#: naming it again in every sentence would be unreadable. Requiring the noun in
#: the window left both of the tombstone page's headline counts unbound, and
#: they were the two staleest numbers in the corpus: the page arguing the
#: atlas's central finding was the one page the numerator check could not read.
PAGE_SUBJECT = {
    "rejected-value-tombstone.md": "tombstone",
    "trust-state-machine.md": "trust_state",
    "bi-temporal-fact-validity.md": "bitemporal",
    "scope-as-a-first-class-key.md": "scope_enforced",
    "append-only-memory-audit.md": "audit_log",
}

#: The page subject alone is not enough to bind, and the first version of this
#: proved it by failing eleven correct sentences: a pattern page is *full* of
#: counts that are not censuses — "two systems arrived at it independently",
#: "one repository tests the rotation case". A census sentence on these pages
#: has both marks: it counts against the corpus denominator, and it says the
#: systems *carry* the thing. Requiring both is what separates
#: "Nineteen systems of two hundred and ninety carry it" from
#: "One of two hundred and ninety, plus one adoption, suggests an idea that is
#: not being reached at all" — two sentences, one paragraph apart, only one of
#: which is a count of the mark.
CARRIAGE = re.compile(
    r"\b(?:carry|carries|carrying|have\s+this|has\s+this|hold|holds|"
    r"implement|implements)\b",
    re.I,
)


def bind(ahead: str, behind: str, subject: str | None = None) -> str | None:
    """Which mechanism a claim is about, or None if the sentence does not say.

    Forward first. "Nine systems of one hundred and fifty-five carry a
    tombstone" names its subject after the number; the backward window exists
    for the inverted form ("the tombstone is carried by nine systems"), and a
    sentence naming two mechanisms is left unbound rather than guessed at.

    `subject` is the page's own mechanism, used only when the sentence names
    none. A sentence that names a *different* mechanism still wins over the
    page, and a sentence naming two is still left alone.
    """
    for source in (ahead, behind):
        hits = {flag for flag, pattern in MECHANISM.items() if pattern.search(source)}
        if len(hits) == 1:
            return hits.pop()
        if len(hits) > 1:
            return None
    return subject


def value(token: str) -> int:
    # A spelled number may have wrapped mid-phrase, so collapse whitespace
    # before the lookup — `NUMBER` matches across the newline and `WORDS` is
    # keyed on single spaces.
    token = " ".join(token.split())
    return int(token) if token.isdigit() else WORDS[token.lower()]


#: Below this, a count of atlas nouns is a finding rather than a denominator —
#: "nine systems", "eleven reports". Above it, nothing in this atlas counts that
#: many of anything except the corpus itself, which is what makes the check safe
#: without a corpus marker in the sentence. The marker was tried first and it
#: missed the case this branch was written for: *"It is a statement about 46
#: repositories, not about the whole field"* is a complete sentence with no
#: marker in it, sitting on a page whose other numbers are all machine-checked.
#: It had been stale since the corpus was 46 and the corpus had more than
#: tripled.
CORPUS_FLOOR = 40

#: A history entry opens with its date, and everything inside it is a statement
#: about a past state — *"the scope section claimed 140 reports across 135
#: repositories"*, *"the 62 repositories the atlas then held"*. Those are the
#: sentences that record drift, so a check that reads them as live claims
#: accuses the atlas of exactly the honesty it is trying to enforce. Four of
#: them were the entire first-run output of the corpus branch.
#:
#: One character class, not `\s*(?:[-*]\s+)?\s*`. `normalize` blanks generated
#: blocks to runs of spaces and turns every `*` into one, so a page can hold a
#: single "paragraph" thousands of whitespace characters long — and two adjacent
#: `\s*` groups backtrack quadratically over it. The first version of this line
#: hung the checker for minutes on `overview.md`.
DATED_ENTRY = re.compile(r"^[ \t\n*-]*\d{4}-\d{2}-\d{2}\b")


#: A paragraph that cites an external work states that work's numbers, not this
#: corpus's. "retrieve appears in 269 of 435" is a true sentence about somebody
#: else's coded corpus, and every phrase this checker binds on — "negative
#: retrieval assertion", "audit log", "scope" — appears in exactly the prose
#: that compares their findings to ours. The exemption is deliberately narrow:
#: it applies only to a denominator that is *not* one of this atlas's live
#: totals, so a corpus count that happens to sit beside a citation is still
#: checked. Reworded prose was tried first and is the wrong fix — it makes the
#: page harder to read to keep a checker quiet, and the next citation breaks it
#: again.
EXTERNAL_SOURCE = re.compile(r"arxiv\.org|arXiv:|doi\.org", re.I)


def external_spans(text: str) -> list[tuple[int, int]]:
    """Character ranges of *sentences* that cite an external work.

    This was paragraph-scoped once, and that is the widest hole this checker has
    had. The rejected-value tombstone page opens with a blockquote that states
    the atlas's own headline count and, six lines further down in the same
    paragraph, cites an arXiv paper for the vocabulary. Paragraph scope read the
    citation as owning the count, labelled *"Fourteen systems of two hundred and
    seventy-one"* an external corpus, and waved the atlas's most-quoted sentence
    through while it drifted five systems and nineteen reports out of date.

    A citation governs the number in its own sentence. Anything further away is
    this corpus until proven otherwise.
    """
    spans, cursor = [], 0
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if EXTERNAL_SOURCE.search(sentence):
            spans.append((cursor, cursor + len(sentence)))
        cursor += len(sentence) + 1
    return spans


def historical_spans(text: str) -> list[tuple[int, int]]:
    """Character ranges of dated history entries, which state past counts."""
    spans, cursor = [], 0
    for para in text.split("\n\n"):
        if DATED_ENTRY.match(para):
            spans.append((cursor, cursor + len(para)))
        cursor += len(para) + 2
    return spans


def corpus_total(noun: str | None, reports: int, repos: int) -> int | None:
    """Which live total a bare count of atlas nouns should be read against.

    Reports and repositories differ by one — `hermes-agent` carries two memory
    systems and is reviewed twice — so a check that conflated them would accuse
    one correct sentence every time it read the other.
    """
    if not noun:
        return None
    return repos if "repositor" in noun.lower() else reports


def check(root: Path, show_list: bool) -> int:
    counts, total_reports, total_repos = live_counts(root)
    problems: list[str] = []
    listed: list[str] = []
    bound = 0

    # `AGENTS.md` is scanned beside `content/` because it is the file an agent
    # reads first and the only prose outside the site that states corpus totals.
    # Its opening figure sat eighteen reports stale while every generated number
    # it points at was current.
    sources = sorted((root / "content").rglob("*.md"))
    agents_file = root / "AGENTS.md"
    if agents_file.exists():
        sources.append(agents_file)

    for source in sources:
        if source.name in GENERATED_FILES:
            continue
        raw = source.read_text(encoding="utf-8")
        text = normalize(raw)
        past = historical_spans(text)
        cited = external_spans(text)
        where = source.relative_to(root)
        subject = PAGE_SUBJECT.get(source.name) if source.parent.name == "patterns" else None

        # A number naming its mechanism directly needs no window: the subject is
        # the noun. Recorded first so the general pass can skip the same span.
        claimed_spans: list[tuple[int, int]] = []
        for match in MECHANISM_NOUN_CLAIM.finditer(text):
            flag = next(f for f in MECHANISM_NOUNS if match.group(f))
            ahead, behind = window(text, match.start(), match.end())
            line = text[: match.start()].count("\n") + 1
            claim = " ".join(match.group(0).split())
            # Same two guards the windowed matcher applies, which this branch
            # bypassed when it was first written: a count scoped to a batch or a
            # single system is not a claim about the corpus.
            if LOCAL_SCOPE.match(ahead) or not CORPUS_MARKER.search(f"{behind} {ahead}"):
                if show_list:
                    listed.append(
                        f"{where}:{line}: '{claim}' — no corpus marker in the sentence, not checked"
                    )
                continue
            claimed_spans.append(match.span())
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

        for match in CLAIM.finditer(text):
            if any(s <= match.start() < e for s, e in claimed_spans):
                continue
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
            # Somebody else's corpus, cited in the same sentence as the number.
            # A denominator matching one of our live totals is still ours — and
            # so is any denominator *below* one, because this corpus only ever
            # grows: a smaller own total is a stale own total, which is exactly
            # the drift this check exists to catch and the one case where
            # "external" is the most expensive possible misreading.
            if (
                denom is not None
                and value(denom) > max(total_reports, total_repos)
                and any(s0 <= match.start() < e0 for s0, e0 in cited)
            ):
                if show_list:
                    listed.append(
                        f"{where}:{text[: match.start()].count(chr(10)) + 1}: "
                        f"'{' '.join(match.group(0).split())}' — external corpus, not checked"
                    )
                continue
            page_subject = (
                subject
                if subject
                and denom is not None
                and value(denom) in (total_reports, total_repos)
                and (CARRIAGE.search(ahead) or CARRIAGE.search(behind))
                else None
            )
            flag = bind(ahead, behind, page_subject)
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
                total = corpus_total(noun, total_reports, total_repos)
                if (
                    total is not None
                    and value(match.group("num")) >= CORPUS_FLOOR
                    and not any(s <= match.start() < e for s, e in past)
                ):
                    bound += 1
                    said = value(match.group("num"))
                    if show_list:
                        listed.append(
                            f"{where}:{line}: '{claim}' — corpus total, said {said}, live {total}"
                        )
                    if said != total:
                        problems.append(
                            f"{where}:{line}: '{claim}' — the corpus is {total}, not {said}"
                        )
                    continue
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

    # Every matcher needs a control here. The mechanism-noun branch was added
    # after a reader found what the windowed one missed, shipped with no fixture
    # of its own, and a second review caught that before it caught a bug — which
    # is the same lesson as the rest of this file: an untested branch is a claim
    # nobody has checked.
    #: (prose, expected exit, label, page path, corpus size). The last two
    #: default to a plain page on a corpus of two; the branches added later need
    #: a real denominator and a real pattern page to exercise at all.
    cases = [
        ("One system carries a rejected-value tombstone.\n", 0, "windowed: correct count passes"),
        ("Two systems carry a rejected-value tombstone.\n", 1, "windowed: wrong count fails"),
        ("Memory is nice.\n", 1, "nothing bound is not a pass"),
        ("The atlas holds one tombstone.\n", 0, "mechanism noun: correct count passes"),
        ("The atlas holds two tombstones.\n", 1, "mechanism noun: wrong count fails"),
        (
            "One system carries a rejected-value tombstone.\n\n"
            "Its store holds two tombstones and a queue.\n",
            0,
            "mechanism noun: a within-system count is not a corpus claim",
        ),
        # A spelled denominator that wraps mid-phrase. Read as "two hundred"
        # this is a correct claim reported stale; the whole number has to match
        # across the newline.
        (
            "One system of two hundred and\nninety carries a rejected-value tombstone.\n",
            0,
            "wrapped denominator: the long form survives a line break",
            "page.md",
            290,
        ),
        # The external-corpus escape, which was paragraph-scoped and swallowed
        # this atlas's own headline count six lines above an arXiv link.
        (
            "Two systems of one hundred carry a rejected-value tombstone.\n"
            "The vocabulary is borrowed from arXiv:2605.26252.\n",
            1,
            "external escape: a citation in a later sentence does not excuse the count",
        ),
        (
            "A survey at arXiv:2605.26252 found two systems of four hundred "
            "carrying a rejected-value tombstone.\n\n"
            # A bound, correct claim beside it: an excused claim on its own
            # leaves nothing bound, which is its own failure by design.
            "One system carries a rejected-value tombstone.\n",
            0,
            "external escape: a citation in the same sentence, over our total, still excuses",
        ),
        # A pattern page names its mechanism with a pronoun. Both of the
        # tombstone page's headline counts were unbound for this reason.
        (
            "One system of two hundred and ninety carries it.\n",
            0,
            "page subject: correct pronoun census passes",
            "patterns/rejected-value-tombstone.md",
            290,
        ),
        (
            "Two systems of two hundred and ninety carry it.\n",
            1,
            "page subject: wrong pronoun census fails",
            "patterns/rejected-value-tombstone.md",
            290,
        ),
        (
            "Two systems of two hundred and ninety arrived at it independently.\n\n"
            "One system of two hundred and ninety carries it.\n",
            0,
            "page subject: a non-carriage sentence on the page is not a census",
            "patterns/rejected-value-tombstone.md",
            290,
        ),
    ]
    failures = []
    for case in cases:
        prose, expected, label = case[0], case[1], case[2]
        rel = case[3] if len(case) > 3 else "page.md"
        size = case[4] if len(case) > 4 else 2
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            systems = root / "content" / "systems"
            systems.mkdir(parents=True)
            (systems / "with.md").write_text(
                FIXTURE_REPORT.format(name="with", caps="tombstone"), encoding="utf-8"
            )
            for i in range(size - 1):
                (systems / f"without{i}.md").write_text(
                    FIXTURE_REPORT.format(name=f"without{i}", caps=""), encoding="utf-8"
                )
            page = root / "content" / rel
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(prose, encoding="utf-8")
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

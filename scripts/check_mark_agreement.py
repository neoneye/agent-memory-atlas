#!/usr/bin/env python3
"""Assert a report's body does not contradict its own frontmatter about a mark.

Every count on this site derives from `capabilities:` in report frontmatter. The
matrix, the capability index, the homepage filters and the bound claim counts all
read that one line, and `check_verdict_marks.py` makes `content/verdicts.md`
agree with it too. Nothing compared it to the **prose of the report it sits on**.

That gap has a shape, and it is produced by the atlas's own process. A re-score
awards a mark, updates `capabilities:` and writes the `## History` entry — and
leaves the body arguing the other way, because the sentence withholding the mark
is three sections down and reads as settled. The published result is one page
making two claims: aimee's frontmatter carried `tombstone` with an evidence
record while its section 12 still said *"this is why the `tombstone` mark is not
awarded"*, its summary still opened "Five marks", and its matrix `risks` field —
rendered verbatim on the compare page — still said nothing consulted the
invalidated set. Three surfaces, two answers.

When this check was written it found four reports in that state: aimee,
[nexusmem], [remem-mcp] and [tokenmizer]. Each is a defect whichever way it
resolves — either the mark is wrong or the paragraph is, and the build cannot
tell which. That is the point: this check does not decide, it refuses to let a
report ship while it disagrees with itself.

One thing is checked, against the body only: **a mark the prose withholds and the
frontmatter awards** — "`scope_enforced` is withheld", "the `tombstone` mark is
not awarded", "withholds the `trust_state` mark".

A *stated total* — "Five marks." — was tried and removed, and the reason is
worth keeping. "N marks" in this corpus means four different things: the marks
carried ("Five marks. The project states three"), the marks **withheld** ("Two
marks are withheld and they are the interesting ones"), the rubric's full set
("none of the seven capability marks"), and the marks on one *component* rather
than the report ("they are twenty lines and they carry two capability marks").
One run flagged twenty-five reports and every one of them was written correctly;
it also matched `= 2 marks current` inside a quoted code comment. A checker that
has to guess which of four things a sentence counts will accuse correct prose,
which costs more than the drift it catches — the same judgement
`check_claim_counts.py` records in its own docstring. The denial branch needs no
guess: it names a flag and refuses it, and the frontmatter either awards that
flag or does not.

What is deliberately excluded:

- **The frontmatter itself**, including `capability_evidence:` records. One of
  those says a *malformed tombstone entry* "is refused" by a validator, which is
  a sentence about the system and not about the mark.
- **`## History`.** Its entries record past states on purpose — "Marks moved
  from five of seven to six" — so reading them as live claims accuses the log of
  being a log.
- **Withholding language naming a mark the report does not carry**, which is the
  overwhelmingly common case and is correct writing: a report explains its
  dashes, and 252 sentences in this corpus do exactly that.

Usage: check_mark_agreement.py <project-dir>
       check_mark_agreement.py --self-test
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

FLAGS = [
    "tombstone",
    "trust_state",
    "bitemporal",
    "scope_enforced",
    "audit_log",
    "human_review",
    "negative_eval",
]
FLAG_ALT = "|".join(FLAGS)

#: Withholding stated *about a mark*. Every branch requires either the noun
#: "mark" or an unambiguous verb of refusal applied to the flag name itself.
#:
#: The bare verb "refused" was tried without the "mark" requirement and matched
#: "a malformed tombstone is refused" inside an evidence record — a true
#: sentence about the validator, read as a claim about the rubric. Weak verbs
#: now need the noun; only "withheld" stands alone, because nothing in this
#: corpus withholds anything but a mark.
DENIAL = re.compile(
    rf"`?(?P<f1>{FLAG_ALT})`?\s+(?:mark\s+)?(?:is|was)\s+withheld"
    rf"|`?(?P<f2>{FLAG_ALT})`?\s+mark\s+(?:is|was)\s+(?:refused|not\s+awarded|withheld)"
    rf"|withholds?\s+the\s+`?(?P<f3>{FLAG_ALT})`?\s+mark"
    rf"|the\s+`?(?P<f4>{FLAG_ALT})`?\s+mark\s+is\s+not\s+awarded"
    rf"|earns?\s+no\s+`?(?P<f5>{FLAG_ALT})`?\s+mark",
    re.I | re.S,
)

#: Asterisks and code ticks sit inside these phrases — "**`negative_eval` is
#: withheld**" — and are stripped before matching. Underscores are *not*, because
#: four of the seven flag names contain one and stripping it turns `trust_state`
#: into a word this checker no longer recognises.
MARKUP = re.compile(r"[*`]+")


def body_of(text: str) -> str:
    """The prose a reader judges, with the frontmatter and the log removed."""
    block = re.match(r"---\n.*?\n---\n", text, re.S)
    body = text[block.end():] if block else text
    return body.split("\n## History")[0]


def declared(text: str) -> set[str] | None:
    match = re.search(r'^capabilities: "(.*)"$', text, re.M)
    if match is None:
        return None
    return {c.strip() for c in match.group(1).split(",") if c.strip()}


def problems_in(slug: str, text: str) -> list[str]:
    marks = declared(text)
    if marks is None:
        return []
    body = body_of(text)
    found = []

    for match in DENIAL.finditer(MARKUP.sub("", body)):
        flag = next(g for g in match.groups() if g)
        if flag.lower() in marks:
            phrase = " ".join(match.group(0).split())
            found.append(
                f"{slug}: the body says {phrase!r}, but the frontmatter awards {flag.lower()}"
            )
    return found


def self_test() -> int:
    def report(caps: str, body: str) -> str:
        return f'---\ncapabilities: "{caps}"\n---\n{body}\n## History\n\n**2026-01-01** — Marks moved from two marks to three.\n'

    cases = [
        # Denial of a mark the frontmatter awards — the aimee class.
        ("bad-denial", report("tombstone, audit_log", "So the `tombstone` mark is not awarded here."), 1),
        # The same sentence about a mark the report does NOT carry: correct writing,
        # and the overwhelmingly common case. Firing here would make the check noise.
        ("ok-denial", report("audit_log", "So the `tombstone` mark is not awarded here."), 0),
        # The three live phrasings, each with emphasis inside the phrase.
        ("bad-withheld", report("scope_enforced", "The **`scope_enforced` mark is withheld** on that reasoning."), 1),
        ("bad-bare", report("human_review", "Viewing is not reviewing, so `human_review` is withheld."), 1),
        ("bad-withholds", report("trust_state", "This report withholds the `trust_state` mark."), 1),
        # An underscore flag must survive markup stripping — `trust_state` became
        # "truststate" when underscores were stripped with the asterisks.
        ("ok-underscore-flag", report("audit_log", "The `trust_state` mark is withheld: a float is not a state."), 0),
        # Per-mechanism "no mark", about one subsystem rather than the rubric flag.
        ("ok-mechanism", report("audit_log", "An event cannot be false, so it earns no mark here."), 0),
        # `## History` records past states on purpose.
        ("ok-history", report("tombstone", "Prose.\n## History\n\n**2026-01-01** — the `tombstone` mark is withheld."), 0),
        # Frontmatter evidence records are not body prose: this one is a sentence
        # about a validator refusing a malformed entry, not about the rubric.
        (
            "ok-frontmatter",
            '---\ncapabilities: "tombstone"\ncapability_evidence:\n'
            '  tombstone: "a malformed tombstone is refused | v.js | x | tests/"\n---\nProse.\n',
            0,
        ),
    ]
    failures = 0
    for name, text, expected in cases:
        got = len(problems_in(name, text))
        if got != expected:
            print(f"self-test failed: {name} expected {expected} problem(s), got {got}", file=sys.stderr)
            failures += 1
    if failures:
        return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main(root: str) -> int:
    systems = Path(root) / "content" / "systems"
    if not systems.is_dir():
        print(f"Missing {systems}", file=sys.stderr)
        return 1

    problems: list[str] = []
    checked = 0
    for path in sorted(systems.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if declared(text) is None:
            continue
        checked += 1
        problems.extend(problems_in(path.stem, text))

    if problems:
        print("A report contradicts its own frontmatter about a mark:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            "A re-score updates `capabilities:`; the sentence that argued the other "
            "way has to move with it. Fix whichever side is wrong.",
            file=sys.stderr,
        )
        return 1

    print(f"{checked} reports agree with their own frontmatter about their marks.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

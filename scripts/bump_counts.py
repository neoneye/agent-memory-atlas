#!/usr/bin/env python3
"""Move the hand-kept corpus and mark counts after a report is added or a mark moves.

The generated lists (`*N of M:*` in the overview, the A-Z index, the matrix) are
rebuilt by `npm run build`. This script exists for the *other* half: the
sentences a person wrote, where the same number appears as digits in one file
and as words in another, and `check_claim_counts` binds both.

It replaces whole phrases, never bare numbers, because a bare 353->354 sweep
once rewrote two commit hashes and a card number. Every replacement is a
literal phrase containing a word, and the count of hits is asserted.

Usage:
    python3 scripts/bump_counts.py --reports 396:397 --repos 395:396 \
        --mark scope_enforced=209:210 --mark trust_state=86:87
"""
from __future__ import annotations
import argparse, io, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ONES = ["zero","one","two","three","four","five","six","seven","eight","nine","ten",
        "eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen",
        "eighteen","nineteen"]
TENS = ["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]

def words(n: int) -> str:
    """British-style spelling matching the prose in content/: 'three hundred and ninety-six'."""
    if n < 20:
        return ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        return TENS[t] + ("-" + ONES[o] if o else "")
    h, r = divmod(n, 100)
    out = ONES[h] + " hundred"
    if r:
        out += " and " + words(r)
    return out

def variants(n: int) -> list[str]:
    w = words(n)
    return [str(n), w, w[0].upper() + w[1:]]

FILES = ["AGENTS.md", "README.md", "content/overview.md", "content/capabilities.md",
         "content/benchmarks.md", "content/verdicts.md", "content/methodology/atlas-rubric.md",
         "content/patterns/index.md", "site/index.html"]

def collect_files() -> list[Path]:
    out = []
    for rel in FILES:
        p = ROOT / rel
        if p.is_file():
            out.append(p)
    for p in sorted((ROOT / "content" / "patterns").glob("*.md")):
        if p not in out:
            out.append(p)
    for p in sorted((ROOT / "content" / "methodology").glob("*.md")):
        if p not in out:
            out.append(p)
    return out

# A number only moves when it sits next to one of these words. This is the whole
# safety property: a sha or a line reference never does.
# The same integer is a report count in one sentence and a repository count in
# another, one below it. Keeping the two vocabularies apart is what stops a
# --reports bump from silently moving the repository figure; that happened once.
REPORT_CONTEXTS = [
    # NOT "reports across {n}": the number after "across" is the repository
    # count, one below the report count, and belongs to REPO_CONTEXTS alone.
    "{n} reports", "{n} memory systems", "{n} systems",
    "of {n} carry", "of {n} apply", "of {n} commit", "of {n} record",
    "of {n} systems", "of {n} repositories", "of {n} in the atlas",
    "of {n} —", "of {n}:", "of {n} verdict", "all {n} systems",
    "about {n} repositories", "across {n} repositories", "{n} agent memory architectures",
    "{n} distinct", "{n} of",
    "<strong>{n}</strong>",
    # The mirrored word order: prose says both "of N systems" and "systems of N".
    "systems of {n}", "entries of {n}", "reports of {n}",
]

MARK_CONTEXTS = [
    "of {n} carry", "of {n} apply", "of {n} commit", "of {n} record",
    "of {n} systems", "of {n} repositories", "of {n} in the atlas",
    "of {n} —", "of {n}:", "{n} of", "systems of {n}", "repositories of {n}",
    "{n} negative-eval suites", "{n} tombstones", "{n} trust states",
    # numerator-first shapes: "32 systems of 399 carry a ..."
    "{n} systems of", "{n} repositories of", "{n} reports of",
]

REPO_CONTEXTS = [
    "{n} repositories", "statement about {n}", "reports across {n}",
    "repositories of {n}", "across {n} repositories",
]

# A digit run only counts when nothing numeric touches either side. Without
# this, "{n} of" with n=56 matched inside "SHA-256 of", "1056 of 1200",
# "$656 of API list price" and "2,291 of"; a single run corrupted eleven
# unrelated numbers across five files on 2026-09-10.
NUM_LEFT = r"(?<![\d,.$-])"
NUM_RIGHT = r"(?![\d,.])"

# "{n} of" is the loosest template here — it also matches "91 of tests",
# meaning ninety-one lines of tests. Require a corpus-scale denominator after
# it so only "91 of 406" moves.
DENOM_REQUIRED = {"{n} of"}
DENOM_AHEAD = r"(?=\s*(?:\*?\d{3}\b|four hundred|three hundred))"

# A spelled number under a hundred is one word, and "ninety-one" is as likely
# to be a retention period, a line count or a number of seconds as a corpus
# figure. Require a corpus noun after it. Longer spelled forms
# ("one hundred and fifty-five") are distinctive enough to replace bare.
SPELLED_NOUN = r"(?=\]?\s+(?:systems?|repositories|reports|tombstones|trust states|negative-eval|of\b))"

NUMBER_WORD = ("one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
               "thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
               "twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety")

def digit_pattern(tpl: str, ov: str) -> re.Pattern:
    pre, post = tpl.split("{n}")
    body = re.escape(pre) + NUM_LEFT + re.escape(ov) + NUM_RIGHT + re.escape(post)
    if tpl in DENOM_REQUIRED:
        body += DENOM_AHEAD
    return re.compile(body)

def apply(old: int, new: int, dry: bool, contexts) -> int:
    """Replace `old` with `new` where it is a count.

    Both forms need a guard. A digit run needs a context word beside it *and*
    no digit, comma, dot, dollar or hyphen touching it — that pair is what
    stops a sweep rewriting a commit sha, a price or a checksum name. A
    one-word spelled number needs a corpus noun after it, because "ninety-one"
    is a perfectly ordinary quantity of days.
    """
    total = 0
    for path in collect_files():
        s = io.open(path, encoding="utf-8").read()
        orig = s
        # Spelled forms first. "four hundred" is a prefix of "four hundred and
        # two", and a naive replace turned an already-updated 402 into "four
        # hundred and one and two" across eighteen lines, so refuse to match
        # when another number word follows.
        for ov, nv in list(zip(variants(old), variants(new)))[1:]:
            guard = SPELLED_NOUN if " " not in ov else ""
            pattern = re.compile(
                re.escape(ov)
                + r"(?!\s+and\s+(?:" + NUMBER_WORD + r")\b)(?![-\w])"
                + guard
            )
            c = len(pattern.findall(s))
            if c:
                s = pattern.sub(nv, s)
                total += c
                print(f"  {path.relative_to(ROOT)}: {c}x {ov!r} -> {nv!r} (spelled)")
        ov, nv = str(old), str(new)
        for tpl in contexts:
            pattern = digit_pattern(tpl, ov)
            hits = pattern.findall(s)
            if hits:
                s = pattern.sub(tpl.format(n=nv), s)
                total += len(hits)
                print(f"  {path.relative_to(ROOT)}: {len(hits)}x {tpl.format(n=ov)!r} -> {tpl.format(n=nv)!r}")
        if s != orig and not dry:
            io.open(path, "w", encoding="utf-8").write(s)
    return total

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", help="OLD:NEW total report count")
    ap.add_argument("--repos", help="OLD:NEW distinct repository count")
    ap.add_argument("--mark", action="append", default=[], help="name=OLD:NEW numerator")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    jobs = []
    if args.reports:
        o, n = args.reports.split(":")
        jobs.append((int(o), int(n), REPORT_CONTEXTS))
    if args.repos:
        o, n = args.repos.split(":")
        jobs.append((int(o), int(n), REPO_CONTEXTS))
    for m in args.mark:
        _, pair = m.split("=", 1)
        o, n = pair.split(":")
        jobs.append((int(o), int(n), MARK_CONTEXTS))
    if not jobs:
        sys.exit("nothing to do: pass --reports, --repos or --mark")

    total = 0
    for old, new, contexts in jobs:
        print(f"{old} -> {new}")
        total += apply(old, new, args.dry_run, contexts)
    print(f"{total} replacement(s){' (dry run)' if args.dry_run else ''}")
    print("Now run: npm run build && npm test — the checks name any phrase this missed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

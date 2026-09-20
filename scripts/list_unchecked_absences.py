#!/usr/bin/env python3
"""List whole-repository absence claims about files that carry no recorded command.

Negative existence claims are this atlas's dominant error class — that was the
finding of the 2026-08-31 audit and it has held since. What two sweeps in
September 2026 added is *which* negative claims go wrong, and the split is sharp
enough to gate on.

**Claims about a symbol hold. Claims about a file do not.** Across 55 published
absence claims checked against the GitHub trees API at each report's own pin,
every claim of the form "X has no writer anywhere", "Y appears in no WHERE
clause", "no tombstone concept exists" was correct or off by a nuance. Seven
claims of the form "there are no tests", "no LICENSE exists", "there is no CI
configuration" were false:

    munder-difflin   "the repository contains no tests at all"  — 110 files under test/
    pro-long         "no assertion anywhere in the tree"        — tests/lifecycle.test.ts
    pro-long         "no LICENSE exists in the tree"            — a top-level MIT LICENSE
    hivemind         "there is no CI configuration in the tree" — a four-platform matrix
    marsnme          "no test directory found"                  — scripts/tests/ + a Vitest suite
    syke             "no test file named for the safety layer"  — 871 lines over 21 cases
    engram-format    "no CI in the repository"                  — a publish workflow with a gate
    auto-company     "still contains no licence file"           — a root MIT LICENSE

The reason the two classes differ is the reading. A symbol claim is written
*while reading the code that would contain the symbol* — the author already
grepped, because that is how they got there. A file claim feels self-evident from
a directory listing, and in all seven cases above the claim's scope was a
directory the reader never opened while being careful somewhere else: engram-format
catalogued dozens of Rust tests in `src/` and then asserted over `.github/`;
marsnme read the memory tools and asserted over two deployment subtrees.

The worst shape is a false absence used as the *reason* for a conclusion. syke's
said nothing asserts what the deletion gate does and concluded the behaviour was
"unspecified rather than chosen"; the behaviour was chosen, committed and
asserted by name in a file the reading did not open.

**Listing is the reporting mode and `--check` is a ratchet**, following
`list_superlatives.py` for the same reason: a gate that fails on several hundred
pre-existing instances teaches people to skip it. Nothing here can verify an
absence — that needs one network call per claim — so the gate stops the pool
growing while the pool is worked down by hand.

**The hole this gate does not close**, stated rather than hidden: a recorded
command is evidence only if it was *re-executed*. auto-company carried
`ls LICENSE* COPYING*` annotated "still absent, against an MIT badge" inside a
block headed "Re-run at this pin", and that line had been copied across two
re-pins while the five lines above it were genuinely re-run. It would pass this
check. Grounding predicts correctness at a first reading and not across a
re-pin, where the word to grep for is `still`.

Usage: list_unchecked_absences.py <project-dir>
       list_unchecked_absences.py --check <project-dir>
       list_unchecked_absences.py --self-test
"""
import re
import sys
from pathlib import Path

#: The artifacts a reader is expected to notice without looking. Deliberately
#: not "any noun": a claim about a *symbol* belongs to the class that holds, and
#: sweeping it in here would bury the signal under several thousand rows.
ARTIFACT = (
    r"(licen[cs]e file|`?LICEN[CS]E`?|`?COPYING`?|"
    r"tests?\b|test (?:file|files|directory|suite|harness|tree)|`?tests?/`?|"
    r"CI(?: configuration| pipeline| workflow)?\b|continuous integration|"
    r"(?:GitHub )?Actions? workflow|`?\.github`?|workflows?\b|"
    r"benchmark(?: file| suite| directory)?|fixture(?: vault| directory)?|"
    r"`?CHANGELOG`?|`?CONTRIBUTING`?|`?Dockerfile`?|`?Makefile`?)"
)

NEGATION = r"(there (?:are|is) no|there (?:are|is)n't (?:any|a)|has no|have no|carries no|contains no|ships no|with no|without (?:a|any)|\bno\b|none of)"

#: A claim is only interesting when it is scoped to the *whole repository*. "No
#: test covers the dedup path" is a scoped claim the surrounding paragraph
#: supports; "there are no tests in the repository" is the one that goes wrong.
WHOLE_REPO = (
    r"(in the (?:tree|repo|repository|codebase|project)|anywhere(?: in| at all)?|"
    r"at all\b|of any kind|in this (?:tree|repo|repository)|exists? anywhere)"
)

CLAIM = re.compile(
    NEGATION + r"[^.\n]{0,60}?" + ARTIFACT + r"[^.\n]{0,60}?" + WHOLE_REPO,
    re.I,
)

#: A quotation is the subject's claim about itself, not the atlas's about the
#: tree. Same rule and same bound as `list_superlatives.py`, for the same reason:
#: the edit a ratchet invites for a false positive is to alter the quotation.
QUOTED = re.compile(r'"[^"]{0,800}?"|“[^”]{0,800}?”', re.S)

#: A claim is *grounded* when the report shows the reader how it was established:
#: a shell command naming the artifact, inside a fence or inline. This is the
#: structural predictor the sweeps found — of the seven false claims, six sat in
#: reports with no recorded search at all.
COMMAND = re.compile(
    r"(?:^|[\s`])(?:ls|find|grep|rg|rgrep|git ls-files|cat|head|test -[fed]|stat|fd)\s[^\n`]{0,160}",
    re.M,
)

#: A claim can also be established without a clone, by listing the repository
#: tree at the pinned revision over the API. That is a recorded check like any
#: other and the honest way to write down what was actually run, so it grounds a
#: claim too — the 2026-09-20 sweep established most of its results that way.
#: Backticks are permitted inside the match, unlike the shell form, because this
#: one is prose naming the filter rather than a line to paste into a terminal.
API_CHECK = re.compile(
    r"GET /repos/[^\n]{0,200}?/git/trees/[^\n]{0,200}", re.M
)


def _spans(text: str) -> list[tuple[int, int]]:
    return [m.span() for m in QUOTED.finditer(text)]


def _grounding_tokens(text: str) -> str:
    """The lowercased text of every shell command in the report, joined."""
    return " ".join(
        m.group(0).lower()
        for pattern in (COMMAND, API_CHECK)
        for m in pattern.finditer(text)
    )


def _artifact_word(claim: str) -> str:
    """The artifact a claim is about, reduced to a token a command would name."""
    low = claim.lower()
    if "licen" in low or "copying" in low:
        return "licen"
    if "test" in low:
        return "test"
    if "ci" in low or "workflow" in low or "action" in low or ".github" in low:
        return "github"
    if "benchmark" in low:
        return "benchmark"
    if "fixture" in low:
        return "fixture"
    return low.strip()[:12]


def collect(content: Path) -> list[tuple[str, str, bool]]:
    rows: list[tuple[str, str, bool]] = []
    for path in sorted((content / "systems").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        spans = _spans(text)
        commands = _grounding_tokens(text)
        offset = 0
        for lineno, line in enumerate(text.split("\n"), 1):
            # Table rows are appendix entries; they carry their command in the
            # next cell and are the shape this check is asking reports to adopt.
            if line.lstrip().startswith("|"):
                offset += len(line) + 1
                continue
            for match in CLAIM.finditer(line):
                if any(lo <= offset + match.start() < hi for lo, hi in spans):
                    continue
                word = _artifact_word(match.group(0))
                grounded = word in commands
                rows.append((f"{path.name}:{lineno}", match.group(0).strip(), grounded))
            offset += len(line) + 1
    return rows


#: Ungrounded file-shaped absence claims standing when the ratchet was set
#: (2026-09-20), out of 108 such claims in total. It was 53 when the ratchet was
#: written and fell to 46 the same day, as twelve reports whose licence and test
#: claims had just been checked against their trees gained an appendix recording
#: that check. Lower it as claims are checked;
#: `--check` fails if it rises. Never raise it to admit a new claim — check the
#: claim and record the command beside it, or narrow the claim to the subtree
#: that was actually read.
#:
#: Grounding is measured per *artifact class*, not per claim: a report that
#: records `find . -name '*test*'` anywhere grounds every test claim it makes.
#: That is deliberate — the question the predictor answers is whether the author
#: went looking, not whether each sentence has its own footnote — and it is the
#: reason this is a ratchet and not a verifier.
UNGROUNDED_CEILING = 46


def check(root: str) -> int:
    rows = collect(Path(root) / "content")
    ungrounded = [r for r in rows if not r[2]]
    if len(ungrounded) > UNGROUNDED_CEILING:
        print(
            f"ungrounded whole-repository absence claims rose to "
            f"{len(ungrounded)} > {UNGROUNDED_CEILING}."
        )
        print(
            "Each asserts that a file or directory is absent from a whole repository, "
            "and no command in its report shows how that was established. This is the "
            "atlas's dominant error class: seven such claims were false when checked "
            "against the tree at their own pins. Run the search, record it beside the "
            "claim, or narrow the claim to the subtree you read. Do not raise the ceiling."
        )
        for where, claim, _ in ungrounded[: UNGROUNDED_CEILING + 12]:
            print(f"  {where}: {claim}")
        return 1
    print(
        f"{len(rows)} whole-repository absence claims about files; "
        f"{len(ungrounded)} carry no recorded command (ceiling {UNGROUNDED_CEILING})."
    )
    return 0


def self_test() -> int:
    """The matcher must see a whole-repository file claim and nothing else."""
    whole = "There are no tests in the repository."
    if not CLAIM.search(whole):
        print("self-test failed: a whole-repository file claim was not matched", file=sys.stderr)
        return 1
    # A claim scoped to one path is the class that holds; it must not be swept in.
    scoped = "No test covers the dedup fallback in store.rs."
    if CLAIM.search(scoped):
        print("self-test failed: a path-scoped claim was matched", file=sys.stderr)
        return 1
    # A symbol claim is the class that holds, even when phrased over the tree.
    symbol = "`memory_state` has no writer anywhere in the tree."
    if CLAIM.search(symbol):
        print("self-test failed: a symbol claim was matched", file=sys.stderr)
        return 1
    # A quotation is the subject's claim about itself.
    quoted = 'The README says "there is no CI configuration in the tree yet".'
    hit = CLAIM.search(quoted)
    if hit is None:
        print("self-test failed: the quoted fixture no longer matches at all", file=sys.stderr)
        return 1
    if not any(lo <= hit.start() < hi for lo, hi in _spans(quoted)):
        print("self-test failed: a claim inside a quotation was counted", file=sys.stderr)
        return 1
    # Grounding: the artifact token must be found in the report's own commands.
    grounded = "There is no LICENSE file in the tree.\n\n```sh\nls LICENSE* COPYING*\n```"
    if "licen" not in _grounding_tokens(grounded):
        print("self-test failed: a recorded `ls` did not count as grounding", file=sys.stderr)
        return 1
    # And prose mentioning the word must not be mistaken for a command.
    if "licen" in _grounding_tokens("The licence is MIT and the badge resolves."):
        print("self-test failed: prose was read as a recorded command", file=sys.stderr)
        return 1
    # A tree listing at the pinned revision is a recorded check without a clone.
    api = ("| No licence file exists anywhere in the tree | `GET /repos/o/r/git/trees/"
           "abc?recursive=1`, filtered for a path matching `licen[cs]e` | Nothing. |")
    if "licen" not in _grounding_tokens(api):
        print("self-test failed: a recorded tree listing did not count as grounding",
              file=sys.stderr)
        return 1
    print("self-test: 7 controls passed")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    if "--check" in argv:
        rest = [a for a in argv if a != "--check"]
        return check(rest[0] if rest else ".")
    root = argv[0] if argv else "."
    rows = collect(Path(root) / "content")
    for where, claim, grounded in rows:
        mark = "    " if grounded else "  ! "
        print(f"{mark}{where}: {claim}")
    print(
        f"\n{len(rows)} whole-repository absence claims about files, "
        f"{sum(1 for r in rows if not r[2])} with no recorded command."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

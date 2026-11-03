#!/usr/bin/env python3
r"""List recorded shell commands that cannot match what they claim to search for.

An appendix command is this atlas's mechanism for making an absence claim
re-runnable. `add-memory-system` puts it plainly: *"A negative claim you were
not willing to run a command for is one to delete rather than publish."* The
command is the evidence, and nothing until now checked that the evidence works.

**The defect is one character.** `grep` without `-E` is a *basic* regular
expression, in which `|` is an ordinary character and not alternation. So

    grep -rn -i "arxiv|bibtex|@article|citation|doi" README.md

searches for the literal string `arxiv|bibtex|@article|citation|doi`, matches
nothing in any repository ever written, and reports the empty result that the
author then records as proof. It is a check that cannot fail — the same defect
this corpus documents in other people's test suites, sitting in its own
appendix. The correct forms are `-E` with bare pipes, or BRE with `\|` escaped.

**It was found by its consequences, once.** MenteDB's report said
`benchmarks/longmemeval/` was *"a harness rather than a committed result"*,
while `benchmarks/longmemeval/results/` held the official judge's 500 per-question
labels, from which the README's 92.0% recomputes as 460/500 exactly. The
adjacent recorded command was the inert grep above. Six commands across five
further reports shared the defect:

    hivemind-activeloop  arxiv / bibtex / @article / @misc / citation / doi
    signetai             arxiv / bibtex / @article / @misc / CITATION / doi.org
    ultracontext         status / confidence / verified / superseded / stale
    ultracontext         arxiv / bibtex / CITATION
    xerj                 trust_state / "verified" / "approved" / review_status
    beevibe              a `grep -v` exclusion filter that excluded nothing

**A broken command does not make the claim wrong, and that is the point.** Five
of the six carried annotations describing specific hits — *"the LoCoMo dataset
paper only"*, *"HTTP status codes and key verification only"* — which a
non-matching command could never have produced, so a working one was run and
only the written form is wrong. MenteDB's was the one whose annotation was also
false. The gate therefore measures re-runnability, not correctness: it says a
reader cannot reproduce the search, which is the property the appendix exists
to provide.

**Two signals that this is a slip rather than a convention.** In MenteDB's block
the line above used `-iE` correctly; in xerj's, the two lines below used `\|`
correctly. Authors who knew the right form wrote the wrong one once.

**Listing is the reporting mode and `--check` is a ratchet**, following
`list_superlatives.py` and `list_unchecked_absences.py`. The ceiling may fall
and may not rise. Lowering it means fixing a command or justifying it here —
not loosening the matcher.

**What this does not close.** Four holes, stated so the number is not mistaken
for more than it is:

- **It reads `grep` only.** `sed`, `awk`, `find -regex` and `rg` have their own
  syntaxes, and `rg` is ERE by default so the same text is correct there.
- **It cannot tell a literal pipe from a broken one.** `grep -c "|| true"`
  wants the literal string and is correct; it is carried as a named exemption
  rather than matched around.
- **It checks the form, never the result.** A command that runs perfectly and
  whose recorded output is fiction passes this gate. Only re-running finds that,
  which is what caught MenteDB.
- **A command absent from the appendix is invisible here.** That is
  `list_unchecked_absences.py`'s job, and the two gates are complements: one
  asks whether a search was recorded, this one whether the recorded search runs.

**The second defect is an escape under `-E`.** Git uses the platform's POSIX
regex library unless it was built with PCRE, and on macOS that library's
*extended* mode reads `\b`, `\s`, `\w`, `\d`, `\<` and `\>` as nothing it can
match, and `\|` as a literal pipe. Basic mode accepts them, and BSD `grep -E`
accepts every one of them except `\|`. So

    git grep -n -E '\.disputed\b' -- src

returns nothing on the machine these reports are written on, whether or not
the field is assigned. On 2026-11-03, 66 such commands in 41 pages were re-run
in a form that can match. Nine annotations stated an absence the tree
contradicts, two of them in kannaka-memory (`disputed` has two writers), and
six more omitted hits that were really there. The same commands match on glibc, so this check is about
who can reproduce a search, not about any one machine. The portable spellings
are `-w` for a pattern wrapped whole in `\b…\b`, `(^|[^[:alnum:]_])` and
`([^[:alnum:]_]|$)` for a single boundary, and `[[:space:]]` for `\s`.

This rule reads inline code spans as well as fenced lines, since most recorded
searches are inline list items, and it reads a table cell's `\|` as the `|` it
renders as. `ESCAPE_CEILING` is its own ratchet, at zero.

Usage:
       list_inert_recorded_commands.py <project-dir>
       list_inert_recorded_commands.py --check <project-dir>
       list_inert_recorded_commands.py --self-test
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

#: Inline code spans. Prose *quoting* a broken command — a known-limitations
#: bullet, say — is a quotation and not a recorded search, so these are removed
#: before matching. Fenced ```sh blocks are untouched: their command lines carry
#: no backticks of their own.
INLINE_CODE = re.compile(r"`[^`]*`")

#: A quoted grep pattern on one line.
GREP = re.compile(r'\bgrep\b([^\n`]*?)(["\'])(.*?)\2')

#: `-E`, `-P`, or the `egrep` spelling all make `|` alternation.
EXTENDED = re.compile(r"-[a-zA-Z]*[EP]\b|\begrep\b")

#: Commands whose pipe is deliberately literal. Keyed by the pattern text so a
#: file may move without silently re-admitting a different command.
LITERAL_PIPE_EXEMPTIONS = {
    "|| true",
    "| head",
    "| tail",
}

#: Inert commands at the last time this was lowered. `--check` fails if it
#: rises. Never raise it to admit a new one — fix the command instead.
#:
#: The one standing entry, read and justified:
#:   beevibe.md:344  `grep -v '\.test\.|ports/|adapters/'` — the filter excluded
#:   nothing, so its recorded "2 call sites" is an upper bound that a working
#:   filter may reduce. Fixing the command without re-running it would publish a
#:   working search beside a count it may no longer produce, so it waits for a
#:   re-read rather than a cosmetic patch.
#:
#: Two further cases are handled by construction rather than by the ceiling:
#: kipi-system's `grep -c "|| true"` is in LITERAL_PIPE_EXEMPTIONS, and the
#: known-limitations bullet quoting the defect is inside an inline code span.
INERT_CEILING = 1

#: Escapes macOS's extended-mode regcomp cannot match. Read for `git grep`
#: only: BSD `grep -E` accepts all of them.
CLASS_ESCAPE = re.compile(r"\\[bBsSwWdD<>]")

#: Extended-mode patterns whose `\|` is deliberately a literal pipe.
LITERAL_ESCAPED_PIPE_EXEMPTIONS = {
    r"slug_pattern \|\| '%'",   # llm-memory-api: SQL string concatenation
}

#: Commands with an extended-mode escape at the last time this was lowered.
ESCAPE_CEILING = 0


def scan_escapes(text: str) -> list[tuple[int, str]]:
    """Return (line number, command) for each -E grep with an escape it cannot match."""
    found = []
    fenced = False
    for lineno, raw in enumerate(text.splitlines(), 1):
        if raw.lstrip().startswith("```"):
            fenced = not fenced
            continue
        spans = [raw] if fenced else re.findall(r"`([^`]*)`", raw)
        if not fenced and raw.lstrip().startswith("|"):
            spans = [s.replace(r"\|", "|") for s in spans]
        for span in spans:
            for match in GREP.finditer(span):
                flags, pattern = match.group(1), match.group(3)
                is_git = span[: match.start()].endswith("git ")
                if not re.search(r"(^|\s)-[a-zA-Z]*E", flags) or re.search(r"(^|\s)-[a-zA-Z]*P", flags):
                    continue
                if is_git and CLASS_ESCAPE.search(pattern):
                    found.append((lineno, match.group(0).strip()))
                elif r"\|" in pattern and pattern not in LITERAL_ESCAPED_PIPE_EXEMPTIONS:
                    found.append((lineno, match.group(0).strip()))
    return found


def scan_text(text: str) -> list[tuple[int, str]]:
    """Return (line number, command) for each grep that cannot alternate."""
    found = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = INLINE_CODE.sub(" ", raw)
        for match in GREP.finditer(line):
            flags, pattern = match.group(1), match.group(3)
            if "|" not in pattern:
                continue
            if pattern in LITERAL_PIPE_EXEMPTIONS:
                continue
            if r"\|" in pattern:            # escaped: valid BRE alternation
                continue
            if EXTENDED.search(flags):      # -E / -P / egrep
                continue
            found.append((lineno, match.group(0).strip()))
    return found


def collect(project_dir: Path, scan=None) -> list[tuple[str, int, str]]:
    scan = scan or scan_text
    out = []
    targets = sorted((project_dir / "content" / "systems").glob("*.md"))
    for extra in ("overview.md", "families.md", "appendix.md", "benchmarks.md", "verdicts.md"):
        candidate = project_dir / "content" / extra
        if candidate.is_file():
            targets.append(candidate)
    for path in targets:
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, command in scan(text):
            out.append((path.name, lineno, command))
    return out


SELF_TEST = [
    # (text, expected hit count, why it is here)
    ('grep -rn -i "arxiv|bibtex|doi" README.md', 1, "the MenteDB defect"),
    ("grep -rni 'trust_state|\"verified\"|review_status' .", 1, "the xerj defect"),
    ("grep -v '\\.test\\.|ports/|adapters/'", 1, "the beevibe exclusion filter"),
    ('grep -rniE "arxiv|bibtex|doi" .', 0, "-E makes it alternation"),
    ('grep -rn -iE "a|b" .', 0, "-iE, flags combined"),
    ("grep -rni 'approve\\|adjudicat\\|curat' .", 0, "escaped BRE alternation"),
    ('egrep "a|b" .', 0, "egrep is extended"),
    ('grep -rnP "a|b" .', 0, "-P is Perl"),
    ('grep -c "|| true" file', 0, "literal pipe, exempt by intent"),
    ('grep -rn "searchByVector" packages', 0, "no pipe at all"),
    ("a sentence about `grep -i 'a|b'` inside backticks", 0, "prose, not a command"),
    ('grep -rn "single" .', 0, "plain single-term grep"),
    ('rg "a|b" .', 0, "rg is not grep and is ERE by default"),
]

ESCAPE_SELF_TEST = [
    ("- `git grep -nE '\\.disputed\\b' -- src` — no match.", 1, "the kannaka defect, inline"),
    ("```sh\ngit grep -n -E 'Model\\s*[:=]' -- internal\n```", 1, "\\s under -E, fenced"),
    ("- `git grep -n -i -E 'a\\|b' -- src`", 1, "escaped pipe under -E is a literal"),
    ("| claim | `git grep -n -E '\\bDELETE\\b\\|unlink' -- .` | Nothing. |", 1, "table cell, \\b still inert"),
    ("| claim | `git grep -n -E 'DELETE\\|unlink' -- .` | Nothing. |", 0, "table cell's \\| renders as |"),
    ("- `git grep -n -w -E 'disputed' -- src`", 0, "-w is the portable boundary"),
    ("- `git grep -n -E '\\.disputed([^[:alnum:]_]|$)' -- src`", 0, "POSIX class boundary"),
    ("- `git grep -n 'facade\\.record\\b'`", 0, "basic mode accepts \\b"),
    ("- `/usr/bin/grep -rn -E '\\bfoo\\b' src`", 0, "BSD grep -E accepts \\b"),
    ("- `/usr/bin/grep -rn -E 'a\\|b' src`", 1, "BSD grep -E reads \\| as a literal too"),
    ("- `git grep -n -P '\\bfoo\\b'`", 0, "-P is Perl"),
    ("- `git grep -nE \"slug_pattern \\|\\| '%'\" -- node`", 0, "literal ||, exempt by intent"),
]


def self_test() -> int:
    failures = 0
    cases = [(scan_text, *c) for c in SELF_TEST] + [(scan_escapes, *c) for c in ESCAPE_SELF_TEST]
    for scan, text, expected, why in cases:
        got = len(scan(text))
        if got != expected:
            print(f"  FAIL ({why}): expected {expected}, got {got} — {text}", file=sys.stderr)
            failures += 1
    if failures:
        print(f"self-test: {failures} of {len(cases)} controls failed", file=sys.stderr)
        return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    check = "--check" in argv
    args = [a for a in argv if not a.startswith("--")]
    project_dir = Path(args[0]) if args else Path(__file__).resolve().parent.parent
    inert = collect(project_dir)
    escapes = collect(project_dir, scan_escapes)
    if check:
        failed = False
        if len(inert) > INERT_CEILING:
            for name, lineno, command in inert:
                print(f"  {name}:{lineno}  {command}", file=sys.stderr)
            print(
                f"recorded commands that cannot match rose to {len(inert)} > {INERT_CEILING}. "
                "A grep without -E treats | as a literal, so the search proves nothing. "
                "Use -E, or escape the pipes as \\|.",
                file=sys.stderr,
            )
            failed = True
        if len(escapes) > ESCAPE_CEILING:
            for name, lineno, command in escapes:
                print(f"  {name}:{lineno}  {command}", file=sys.stderr)
            print(
                f"extended-mode escapes that cannot match rose to {len(escapes)} > {ESCAPE_CEILING}. "
                "Under -E, macOS git matches nothing for \\b, \\s, \\w, \\d, \\< or \\>, and grep "
                "and git grep read \\| as a literal. Use -w, (^|[^[:alnum:]_]), [[:space:]] or a bare |.",
                file=sys.stderr,
            )
            failed = True
        if failed:
            return 1
        print(
            f"{len(inert)} recorded command(s) cannot match as written (ceiling {INERT_CEILING}); "
            f"{len(escapes)} carry an extended-mode escape (ceiling {ESCAPE_CEILING})."
        )
        return 0
    for name, lineno, command in inert + escapes:
        print(f"{name}:{lineno}  {command}")
    print(f"\n{len(inert)} inert recorded command(s), {len(escapes)} with an extended-mode escape.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

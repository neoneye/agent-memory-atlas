#!/usr/bin/env python3
"""Assert every report's `archive_name` matches the fork its `source_url` implies.

`archive_name` is the report's pointer into the archive organisation — the path
under https://github.com/agent-memory-atlas-archive/ where a fork of the source
lives. It exists so a reader can compare a report against a copy the atlas
controls, and so a report whose upstream disappears still has somewhere to point.

It is also a hand-kept restatement of something already in the file, which is the
shape this repository has been bitten by before: three entries in the
repositories-inspected list drifted precisely because they restated a `revision`
that lived somewhere else, and `check_inspected_pins.py` exists because of it. So
the same discipline applies here — the value is derived from `source_url` by one
rule, and this check re-derives it and fails on a disagreement.

The rule: `https://github.com/<owner>/<repo>` becomes `<owner>--<repo>`, keeping
the casing the report itself uses, because that is the name the fork was created
with. A flat organisation namespace makes `<repo>` alone ambiguous — the corpus
holds three separate `engram`s and two unrelated `sage`s.

An empty `archive_name` is legal and means *deliberately not archived*. There is
one: `sovereign`, whose upstream was deleted before the archive existed, so no
fork could be taken. An empty value must be paired with a report that says why,
which is a judgement this script cannot make and a reader can.

Offline by construction. It re-derives a string; it does not ask GitHub whether
the fork is there. Whether the archive actually holds what the reports claim is
`archive_sync.py`'s job, and it needs a network and a token.

Usage: check_archive_names.py <project-dir> [--self-test]
"""

import re
import sys
from pathlib import Path

REPO_RE = re.compile(
    r"github\.com/([A-Za-z0-9][\w.-]*)/([\w.-]+?)(?:\.git)?(?:/(?:tree|blob)/[^\s]*)?/?$"
)
SOURCE_URL = re.compile(r"^source_url:\s*(\S+)\s*$", re.M)
ARCHIVE_NAME = re.compile(r'^archive_name:\s*"([^"]*)"\s*$', re.M)


def expected(source_url: str) -> str | None:
    hit = REPO_RE.search(source_url.strip().strip('"'))
    return f"{hit.group(1)}--{hit.group(2)}" if hit else None


def check(root: Path) -> list[str]:
    problems = []
    for report in sorted((root / "content" / "systems").glob("*.md")):
        text = report.read_text(encoding="utf-8")
        src = SOURCE_URL.search(text)
        got = ARCHIVE_NAME.search(text)
        if not src:
            continue                      # shape of the frontmatter is another check's job
        if not got:
            problems.append(
                f"{report.name}: no `archive_name`. Add the fork's path under the archive "
                f"organisation, or an empty string with the reason in the report."
            )
            continue
        want = expected(src.group(1))
        if want is None:
            continue                      # not a GitHub URL; nothing to derive
        if got.group(1) == "":
            continue                      # deliberately not archived; the report explains
        if got.group(1) != want:
            problems.append(
                f"{report.name}: archive_name is `{got.group(1)}` but source_url implies "
                f"`{want}`. One of the two moved without the other."
            )
    return problems


def self_test() -> int:
    """Prove the check can still fail, on a tree built to fail it."""
    import tempfile

    controls = [
        ("mismatch", 'source_url: https://github.com/a/b\narchive_name: "a--WRONG"\n', True),
        ("missing", "source_url: https://github.com/a/b\n", True),
        ("agrees", 'source_url: https://github.com/a/b\narchive_name: "a--b"\n', False),
        ("empty is allowed", 'source_url: https://github.com/a/b\narchive_name: ""\n', False),
    ]
    failures = 0
    for label, body, should_fail in controls:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "content" / "systems"
            d.mkdir(parents=True)
            (d / "x.md").write_text(f"---\n{body}---\n", encoding="utf-8")
            got = bool(check(Path(tmp)))
            if got != should_fail:
                print(f"self-test FAILED: {label} expected fail={should_fail}, got {got}")
                failures += 1
    print(f"self-test: {len(controls) - failures} of {len(controls)} controls passed")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    problems = check(root)
    if problems:
        print("archive_name disagrees with source_url:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    total = len(list((root / "content" / "systems").glob("*.md")))
    empty = sum(
        1 for r in (root / "content" / "systems").glob("*.md")
        if (m := ARCHIVE_NAME.search(r.read_text(encoding="utf-8"))) and m.group(1) == ""
    )
    print(f"{total - empty} reports point at a fork in the archive; {empty} deliberately do not.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

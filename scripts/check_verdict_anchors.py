#!/usr/bin/env python3
"""Assert every system slug resolves as an anchor on the verdicts page.

The 140 per-system verdict anchors lived on `/compare/` until 4 August 2026,
when section 9 moved to `/verdicts/`. The section heading was left behind as a
stub so `#9-repo-by-repo-verdicts` still resolves — but every *per-system*
anchor moved with the content, and a fragment never reaches the server, so an
external deep link to `/compare/#mem0` cannot be redirected by the host.

`assets/main.js` catches those client-side: on `/compare/`, a hash matching
nothing on the page is sent to `/verdicts/`. That fallback is only correct while
the target actually exists there, which is what this checks — every slug in
`content/systems/` must be an `id` on the rendered verdicts page.

It also asserts the compare-page stub anchor survives, because the whole reason
the split was safe is that `#9-repo-by-repo-verdicts` never moved.

The claim this exists to stop being made again: the split was reported as
carrying "none of that exposure" on the strength of checking seventeen inbound
links from `content/`. Those are internal references. The links the conservative
strategy was meant to protect are external deep links, which no search of this
repository can see, and none of them was checked.

Usage: check_verdict_anchors.py <project-dir>
"""
import re
import sys
from pathlib import Path


def main(root: str) -> int:
    project = Path(root)
    verdicts = project / "docs" / "verdicts" / "index.html"
    compare = project / "docs" / "compare" / "index.html"
    systems = project / "content" / "systems"

    for path in (verdicts, compare):
        if not path.is_file():
            print(f"Missing {path} — run the build first", file=sys.stderr)
            return 1

    ids = set(re.findall(r'id="([^"]+)"', verdicts.read_text(encoding="utf-8")))
    slugs = sorted(p.stem for p in systems.glob("*.md"))
    missing = [s for s in slugs if s not in ids]

    problems = []
    if missing:
        problems.append(
            f"{len(missing)} system slugs do not resolve on /verdicts/: "
            f"{', '.join(missing[:8])}{' …' if len(missing) > 8 else ''}"
        )
    if 'id="9-repo-by-repo-verdicts"' not in compare.read_text(encoding="utf-8"):
        problems.append(
            "/compare/ no longer carries #9-repo-by-repo-verdicts — the stub "
            "heading is what keeps the section-level deep link alive"
        )

    if problems:
        print("Verdict anchors are broken:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            "Legacy /compare/#<slug> links are redirected client-side by "
            "assets/main.js; that only works while the slug exists on /verdicts/.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

#!/usr/bin/env python3
"""Assert every anchor that left /compare/ still resolves where it went.

Until 25 September 2026 `/compare/` was the whole comparative report: the
argument, the system families, the generated matrix and the appendix, 428,000
words with the build order a builder is sent to behind 340,000 of them. It now
carries the matrix alone. A fragment never reaches the server, so an external
deep link to `/compare/#the-layer-below-delete-…` cannot be redirected by the
host; `assets/main.js` carries a map of every id that left and sends the reader
to its new page.

That map is only correct while each target exists, which is what this checks:
every entry names a built page, and the fragment it names is an `id` on that
page. It also fails when a mapped id reappears on `/compare/`, because the
redirect only fires for an id the page lacks and the entry would be dead.

The hole this does not close: a link from outside the repository to an id that
never existed is not in the map and falls through to the verdict redirect, as
it did before the split.

Usage: check_moved_anchors.py <project-dir>
       check_moved_anchors.py --self-test
"""
import json
import re
import sys
import tempfile
from pathlib import Path

MAP = re.compile(r"/\* BEGIN MOVED ANCHORS \*/\s*(\{.*?\})\s*/\* END MOVED ANCHORS \*/", re.S)


def load_map(js: str) -> dict[str, str]:
    m = MAP.search(js)
    if not m:
        raise ValueError("assets/main.js has no MOVED ANCHORS block")
    return json.loads(m.group(1))


def problems(site: Path, moved: dict[str, str]) -> list[str]:
    out = []
    compare = site / "compare" / "index.html"
    compare_ids = set(re.findall(r'\bid="([^"]+)"', compare.read_text(encoding="utf-8"))) if compare.is_file() else set()
    pages: dict[str, set[str]] = {}
    for anchor, target in sorted(moved.items()):
        page, _, frag = target.partition("#")
        html = site / page / "index.html"
        if not html.is_file():
            out.append(f"#{anchor} → {target}: no page at {page}")
            continue
        ids = pages.setdefault(page, set(re.findall(r'\bid="([^"]+)"', html.read_text(encoding="utf-8"))))
        if frag and frag not in ids:
            out.append(f"#{anchor} → {target}: no id '{frag}' on {page}")
        if anchor in compare_ids:
            out.append(f"#{anchor} is on /compare/ again, so its redirect can never fire")
    return out


def self_test() -> int:
    with tempfile.TemporaryDirectory() as d:
        site = Path(d)
        for page, body in {"compare": '<h2 id="matrix">', "overview": '<h2 id="in-short">'}.items():
            (site / page).mkdir()
            (site / page / "index.html").write_text(body)
        cases = [
            ("a resolving entry passes", {"in-short": "overview/#in-short"}, 0),
            ("a page-level entry passes", {"1-high-level-taxonomy": "overview/"}, 0),
            ("a missing id fails", {"gone": "overview/#gone"}, 1),
            ("a missing page fails", {"x": "families/#x"}, 1),
            ("an id back on /compare/ fails", {"matrix": "overview/#in-short"}, 1),
        ]
        for name, moved, expected in cases:
            got = len(problems(site, moved))
            if got != expected:
                print(f"self-test failed: {name}: got {got}, expected {expected}", file=sys.stderr)
                return 1
    js = 'const M = /* BEGIN MOVED ANCHORS */ {\n "a": "overview/#a"\n } /* END MOVED ANCHORS */;'
    if load_map(js) != {"a": "overview/#a"}:
        print("self-test failed: the map block no longer parses", file=sys.stderr)
        return 1
    print("self-test: 6 controls passed")
    return 0


def main(root: str) -> int:
    project = Path(root)
    moved = load_map((project / "assets" / "main.js").read_text(encoding="utf-8"))
    found = problems(project / "docs", moved)
    if found:
        print("Anchors that left /compare/ no longer resolve:", file=sys.stderr)
        for p in found:
            print(f"  {p}", file=sys.stderr)
        return 1
    print(f"{len(moved)} anchors that left /compare/ resolve where they went.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--self-test" in args:
        sys.exit(self_test())
    sys.exit(main(next((a for a in args if not a.startswith("--")), ".")))

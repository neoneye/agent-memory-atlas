#!/usr/bin/env python3
"""Verify every internal fragment link lands on an id that exists.

Pandoc derives heading ids from heading text, so `## 7. The Contradiction Test`
becomes `#7-the-contradiction-test` and silently changes the moment sections are
renumbered. The ordinary link check does not notice, because the page still
exists — only the fragment is wrong. Run via `npm test`.
"""

from __future__ import annotations

import glob
import os
import re
import sys

ID = re.compile(r'id="([^"]+)"')
LINK = re.compile(r'href="([^"#]*)#([^"]+)"')


def main() -> int:
    site = sys.argv[1]
    pages = glob.glob(os.path.join(site, "**", "index.html"), recursive=True)
    ids = {os.path.realpath(p): set(ID.findall(open(p, encoding="utf-8").read())) for p in pages}

    broken: list[str] = []
    for page in pages:
        real = os.path.realpath(page)
        directory = os.path.dirname(real)
        for target, fragment in LINK.findall(open(page, encoding="utf-8").read()):
            if target.startswith(("http", "mailto")):
                continue
            if target:
                resolved = os.path.realpath(os.path.join(directory, target))
                if os.path.isdir(resolved):
                    resolved = os.path.join(resolved, "index.html")
            else:
                resolved = real
            known = ids.get(resolved)
            if known is None or fragment not in known:
                broken.append(f"{os.path.relpath(page, site)} -> {target}#{fragment}")

    print("\n".join(sorted(set(broken))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

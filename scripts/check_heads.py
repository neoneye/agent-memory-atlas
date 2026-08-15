#!/usr/bin/env python3
"""Assert no <head> contacts Google before the reader has chosen.

There is no shared header partial: `site/index.html` carries its own head and
every generated page gets `templates/document.html`. Both used to load
`gtag.js` with Consent Mode v2 defaulting every signal to denied, and this
script compared the two blocks so they could not drift apart.

That invariant was the wrong one, because both heads could agree and both still
be wrong — and they were. Loading the tag contacts Google on the first paint,
and Google documents that a denied `analytics_storage` still sends cookieless
pings, so the banner's "Nothing is collected until you choose" was false for
every reader who never chose. Agreement between two heads that both measure you
is not a privacy property.

So the assertion is now absolute rather than comparative: **no head may
reference the Google tag at all.** `assets/main.js` injects it after a click on
Allow and nowhere else, which is the only arrangement that makes the banner's
sentence true. One place, one code path, and a grep that fails the build if a
second one appears.

Usage: check_heads.py <project-dir>
"""
import re
import sys
from pathlib import Path

HEADS = ("site/index.html", "templates/document.html")
#: The one file allowed to name the tag, because it only runs on consent.
LOADER = "assets/main.js"
TAG = re.compile(r"googletagmanager\.com|gtag\s*\(", re.I)
MEASUREMENT_ID = re.compile(r"\bG-[A-Z0-9]{8,}\b")


def main(root: str) -> int:
    root_path = Path(root)
    problems = []

    for rel in HEADS:
        path = root_path / rel
        if not path.is_file():
            print(f"Missing head file: {rel}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        # Comments explain why the tag is absent; they are not the tag. Strip
        # them before looking, or the explanation trips the check it documents.
        code = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        if TAG.search(code) or MEASUREMENT_ID.search(code):
            problems.append(
                f"{rel}: loads or configures the Google tag in the <head>. That "
                "runs before the reader has chosen, which makes the consent "
                f"banner's promise false. Inject it from {LOADER} on Allow."
            )

    loader = root_path / LOADER
    if not loader.is_file():
        problems.append(f"Missing {LOADER}, which is where the tag is supposed to live.")
    elif not MEASUREMENT_ID.search(loader.read_text(encoding="utf-8")):
        problems.append(
            f"{LOADER} no longer names a measurement id. If analytics was removed "
            "entirely, remove the consent banner with it and drop this check."
        )

    # Anywhere else in the hand-written sources is a second code path, and a
    # second code path is how the pre-consent load comes back.
    for path in sorted(root_path.glob("templates/*.html")) + sorted(
        root_path.glob("assets/*.js")
    ):
        if path.name == Path(LOADER).name:
            continue
        code = re.sub(r"<!--.*?-->|//.*", "", path.read_text(encoding="utf-8"))
        if MEASUREMENT_ID.search(code):
            problems.append(
                f"{path.relative_to(root_path)}: names a measurement id. Keep the "
                f"tag in {LOADER} only."
            )

    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print("no <head> contacts Google; the tag loads from assets/main.js on consent.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

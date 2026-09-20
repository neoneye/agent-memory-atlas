#!/usr/bin/env python3
"""Check every report's stated licence against the licence in its pinned tree.

A wrong licence is the atlas's most consequential kind of error. Every other
mistake here costs a reader accuracy; this one costs them a decision they cannot
take back — whether they may build on the code at all. And it is the claim least
likely to be re-checked, because nothing forces it: an evidence record forces a
re-pin to re-derive the capability marks, and there is no equivalent for the
sentence in section 1 that says what the licence is.

**Two were wrong when this was first run on 2026-09-20, and both had the same
shape: the project relicensed between pins and the re-pin inherited the prose.**

    silica                   AGPL-3.0 at 300fab2e -> MIT at 3fd11a00
    omninode-knowledge-base  Apache-2.0 at 37f76b13 -> MIT at cb724907

Silica's was on the first line of the report — "an AGPL-3.0 harness" — which is
where a reader deciding whether they may adopt it stops. So the check that
matters most is not "is the label right today" but **"did it change since the
last pin"**, and the cheapest form of that is two fetches:

    curl -s https://raw.githubusercontent.com/<owner>/<repo>/<OLD-pin>/LICENSE | head -1
    curl -s https://raw.githubusercontent.com/<owner>/<repo>/<NEW-pin>/LICENSE | head -1

This is not a build check and cannot be one: the build is offline by design, and
every answer here needs the network. It belongs beside `drift_report.py` as
something run when pins move.

**Three traps, all of which produced long lists of corpus errors that were
entirely the instrument's.** They are encoded below and are the reason this file
exists rather than a one-line grep:

1. **Classify from the title, never by scanning the body.** MPL-2.0 defines
   "Secondary License" in section 1.12 as the GNU GPL, LGPL and *Affero* GPL, so
   a GNU-before-Mozilla body scan reports every MPL file as AGPL.
2. **BUSL, PolyForm and Elastic must be matched before Apache.** Each declares a
   *Change License* in its own header, and that change licence is very often
   "Apache 2.0".
3. **`MIT` needs word boundaries.** Unbounded it matches inside `LIMIT` and
   `LIMITATIONS`, which is where sixteen false MIT claims came from on the first
   run of this sweep.

A mismatch here is a question, not a finding. Dual-licensed and per-component
repositories are common and legitimate — serena is MIT for SolidLSP and
GPL-3.0-or-later for the combined distribution, halofy is AGPL with one
interface under Apache — and a report describing that correctly will look like a
mismatch to a checker that expects one answer. Read the report before changing
it. Of 512 stated licences on the first run, 510 were right.

Usage: licence_drift.py [--limit N] [--slug SLUG ...]
       Writes one JSONL row per report to stdout; summary to stderr.
"""
from __future__ import annotations

import sys

# `scripts/queue.py` shadows the standard library's `queue` module for anything
# run from this directory, and `ThreadPoolExecutor` imports `queue` — so the
# pool raises `AttributeError: module 'queue' has no attribute 'SimpleQueue'`
# before this script does any work. Dropping the script's own directory from
# `sys.path[0]` is the fix that does not require renaming a file other scripts
# import. Must happen before `concurrent.futures` is imported.
if sys.path and sys.path[0].rstrip("/").endswith("scripts"):
    sys.path.pop(0)

import argparse
import concurrent.futures as cf
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Checked in order, and the order is load-bearing — see trap 2 in the docstring.
TITLES: tuple[tuple[str, str], ...] = (
    ("mozilla public license", "MPL-2.0"),
    ("business source license", "BUSL-1.1"),
    ("polyform", "PolyForm"),
    ("elastic license", "Elastic-2.0"),
    ("server side public license", "SSPL"),
    ("gnu affero general public license", "AGPL-3.0"),
    ("gnu lesser general public license", "LGPL-3.0"),
    ("gnu general public license", "GPL-3.0"),
    ("apache license", "Apache-2.0"),
    ("mulan", "MulanPSL-2.0"),
    ("creative commons", "CC"),
    ("mit license", "MIT"),
    ("isc license", "ISC"),
)

NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "LICENCE.md",
         "COPYING", "LICENSE.rst", "License/LICENSE", "LICENSE-MIT",
         "LICENSE-APACHE", "license")

#: `\b` on every alternative. See trap 3.
SPDX = re.compile(
    r"\b(AGPL-3\.0|GPL-3\.0|GPL-2\.0|LGPL-3\.0|Apache-2\.0|Apache 2\.0|MIT|"
    r"BSD-3-Clause|BSD-2-Clause|MPL-2\.0|Elastic License 2\.0|"
    r"Business Source License|BUSL-1\.1|PolyForm[A-Za-z ]*|Commons Clause|SSPL|"
    r"MulanPSL-2\.0|Unlicense|CC0|WTFPL|ISC|Zlib)\b")
CONTEXT = re.compile(r"licen[cs]e|licensed|released under|ships under", re.I)

ALIASES = {"Apache 2.0": "Apache-2.0", "Elastic License 2.0": "Elastic-2.0",
           "Business Source License": "BUSL-1.1"}


def classify(text: str) -> str:
    head = " ".join(text[:400].split()).lower()
    for needle, name in TITLES:
        if needle in head:
            if name == "GPL-3.0" and "version 2" in head:
                return "GPL-2.0"
            return name
    body = " ".join(text[:4000].split()).lower()
    if "permission is hereby granted, free of charge" in body:
        return "MIT"
    if "redistribution and use in source and binary" in body:
        return "BSD-3-Clause" if "neither the name" in body else "BSD-2-Clause"
    if "this is free and unencumbered software" in body:
        return "Unlicense"
    return "UNKNOWN"


def fetch(url: str) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "atlas-licence-drift"})
        with urllib.request.urlopen(req, timeout=25) as fh:
            return fh.read().decode("utf-8", "replace")
    except Exception:
        return None


#: A corrected report keeps its old claim on the page, struck through, in a
#: Recorded Searches row: "~~The repository is Apache-2.0~~ — withdrawn". Read
#: naively that is the report still claiming Apache, and this checker would
#: re-raise every correction it had already caused. Table rows and struck-through
#: spans are therefore not claims.
STRUCK = re.compile(r"~~.*?~~", re.S)


def stated(body: str) -> str | None:
    """The licence the report names, preferring one in a licence sentence."""
    body = STRUCK.sub(" ", body)
    for line in body.split("\n"):
        if line.lstrip().startswith("|"):
            continue
        for m in SPDX.finditer(line):
            near = line[max(0, m.start() - 90):m.end() + 60]
            if CONTEXT.search(near):
                return ALIASES.get(m.group(0), m.group(0))
    m = SPDX.search(body)
    return ALIASES.get(m.group(0), m.group(0)) if m else None


def reports(slugs: list[str] | None):
    for path in sorted((ROOT / "content" / "systems").glob("*.md")):
        if slugs and path.stem not in slugs:
            continue
        text = path.read_text(encoding="utf-8")
        url = re.search(r"^source_url: (\S+)", text, re.M)
        rev = re.search(r"^revision: (\S+)", text, re.M)
        if not url or not rev or "/tree/" in url.group(1):
            continue
        body = text.split("---", 2)[2] if text.startswith("---") else text
        claim = stated(body)
        if not claim:
            continue
        repo = url.group(1).replace("https://github.com/", "").rstrip("/")
        yield path.stem, repo, rev.group(1), claim


def one(row):
    slug, repo, rev, claim = row
    for name in NAMES:
        text = fetch(f"https://raw.githubusercontent.com/{repo}/{rev}/{name}")
        if text:
            return {"slug": slug, "repo": repo, "revision": rev,
                    "stated": claim, "actual": classify(text), "file": name}
    return {"slug": slug, "repo": repo, "revision": rev,
            "stated": claim, "actual": "NO-FILE", "file": None}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--slug", action="append")
    args = ap.parse_args(argv)

    rows = list(reports(args.slug))
    if args.limit:
        rows = rows[:args.limit]

    agree = differ = nofile = 0
    with cf.ThreadPoolExecutor(max_workers=10) as pool:
        for r in pool.map(one, rows):
            if r["actual"] == "NO-FILE":
                nofile += 1
            elif r["actual"] == r["stated"]:
                agree += 1
            else:
                differ += 1
                print(f"  {r['slug']:28} states {r['stated']:<18} "
                      f"tree says {r['actual']} ({r['file']})", file=sys.stderr)
            print(json.dumps(r, ensure_ascii=False), flush=True)

    print(f"\n{len(rows)} stated licences: {agree} agree, {differ} differ, "
          f"{nofile} with no licence file found.", file=sys.stderr)
    print("A difference is a question, not a finding — dual-licensed and "
          "per-component repositories look like this. Read the report.",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

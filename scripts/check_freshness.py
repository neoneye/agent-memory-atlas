#!/usr/bin/env python3
"""Report how far each pinned revision has drifted from its upstream default branch.

Commit pinning is what makes every claim in this atlas auditable, and it is also
what makes the atlas go quietly stale: a report pinned to a commit stays true
about that commit forever while becoming less true about the project. Nothing
here can fix that automatically — re-reading a system is the expensive part —
but knowing *which* reports have drifted, and by how much, turns an unbounded
maintenance worry into a work list.

Reads `source_url` and `revision` from each report, asks GitHub for the current
default-branch head, and reports the comparison. Never fails the build: a stale
pin is information, not an error.

Usage:
    python3 scripts/check_freshness.py [--json] [--limit N]

Set GITHUB_TOKEN to raise the anonymous rate limit (60/hour).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEMS = ROOT / "content" / "systems"
REPO_API = "https://api.github.com/repos/{owner}/{repo}"
COMPARE_API = "https://api.github.com/repos/{owner}/{repo}/compare/{base}...{head}"
REPO_RE = re.compile(r"github\.com/([^/]+)/([^/\s]+?)(?:\.git)?/?$")


def field(text: str, name: str) -> str | None:
    match = re.search(rf"^{name}:\s*(\S+)\s*$", text, re.M)
    return match.group(1).strip('"') if match else None


def request(url: str) -> dict | None:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "agent-memory-atlas"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as exc:
        return {"_error": f"HTTP {exc.code}"}
    except Exception as exc:  # noqa: BLE001 - a network failure is a result, not a crash
        return {"_error": type(exc).__name__}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--limit", type=int, default=0, help="check at most N reports")
    args = parser.parse_args()

    rows = []
    paths = sorted(SYSTEMS.glob("*.md"))
    if args.limit:
        paths = paths[: args.limit]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        url, revision = field(text, "source_url"), field(text, "revision")
        analyzed = field(text, "analyzed_at")
        if not url or not revision:
            continue
        match = REPO_RE.search(url)
        if not match:
            rows.append({"slug": path.stem, "status": "not-github", "url": url})
            continue
        owner, repo = match.groups()
        # The compare endpoint resolves a literal `HEAD` against the base ref, not
        # against the repository, so it reports every pin as identical to itself.
        # The default branch has to be looked up and named explicitly.
        meta = request(REPO_API.format(owner=owner, repo=repo))
        if meta is None or "_error" in meta:
            rows.append({"slug": path.stem, "status": (meta or {}).get("_error", "error")})
            continue
        branch = meta.get("default_branch", "main")
        data = request(
            COMPARE_API.format(owner=owner, repo=repo, base=revision, head=branch)
        )
        if data is None or "_error" in data:
            rows.append({"slug": path.stem, "status": (data or {}).get("_error", "error")})
            continue
        behind = data.get("behind_by", 0)
        ahead = data.get("ahead_by", 0)
        rows.append(
            {
                "slug": path.stem,
                "status": "current" if ahead == 0 else "stale",
                "commits_since": ahead,
                "diverged_by": behind,
                "analyzed_at": analyzed,
                "repo": f"{owner}/{repo}",
            }
        )

    if args.json:
        print(json.dumps(rows, indent=1))
        return 0

    stale = [r for r in rows if r.get("status") == "stale"]
    current = [r for r in rows if r.get("status") == "current"]
    errors = [r for r in rows if r.get("status") not in {"stale", "current"}]

    for row in sorted(stale, key=lambda r: -r.get("commits_since", 0)):
        print(f"{row['commits_since']:>6} commits since pin  {row['slug']:<28} {row['repo']}")
    for row in current:
        print(f"{'current':>6}                     {row['slug']:<28} {row['repo']}")
    for row in errors:
        print(f"{row['status']:>6}                      {row['slug']}")

    print(
        f"\n{len(current)} current, {len(stale)} stale, {len(errors)} unresolved "
        f"of {len(rows)} pinned reports."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

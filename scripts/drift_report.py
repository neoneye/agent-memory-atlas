#!/usr/bin/env python3
"""Emit one JSONL row per report: how far its pin has drifted, and how often it
has been re-read.

`check_freshness.py` answers "is this pin stale?" for a human reading the
terminal. This answers a different question: **which reports should be re-read
next, and in what order?** A report pinned to a commit stays true about that
commit forever while becoming less true about the project, and nothing in the
build notices. TencentDB Agent Memory is the case that prompted this: the report
is pinned at `45e6e80a` and describes v0.3.6, while the project has since
shipped a v2. Nothing was wrong; nobody was told.

Drift alone is the wrong signal to sort on. A repo that lands forty commits a
week is not more urgent than one that landed a rewrite in three, and a report
already re-read last Tuesday is not a candidate no matter how the upstream
moves. So each row carries the three numbers a triage decision actually needs:
how far the pin has moved, how much attention the report has already had, and
how recent that attention was. Ranking is left to whoever reads the file — this
script does not decide what "urgent" means.

One object per line, so the output appends, diffs and greps. Written to stdout
by default; the summary goes to stderr, so a pipe stays clean.

Stars are collected because the ordering question — which report to spend a
re-read on — is not the evidence question, and they are a legitimate input to
the first. They are not an input to the second. `notes/2026-08-04-automating-
re-analysis.md` draws that line and names the failure it guards against: a
scheduling field lands in report frontmatter "for convenience", and six months
later a sentence says "a widely adopted system". So this register is scheduling
state and belongs in `scripts/state/`, which is gitignored. Nothing here writes
to a report, and no report reads from here.

Usage:
    python3 scripts/drift_report.py [--out FILE] [--limit N] [--only SLUG]...
                                    [--window DAYS] [--as-of YYYY-MM-DD]

    python3 scripts/drift_report.py --out scripts/state/drift.jsonl

Exits 1 on an unreachable pin or a run that mostly failed, and 0 otherwise —
drift itself is information, not an error.

Set GITHUB_TOKEN. Up to three API calls per report and ~390 reports means the
anonymous limit (60/hour) cannot finish a run; the script stops rather than
emit a file that looks complete and is not.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEMS = ROOT / "content" / "systems"

REPO_API = "https://api.github.com/repos/{owner}/{repo}"
HEAD_API = "https://api.github.com/repos/{owner}/{repo}/commits?sha={branch}&per_page=1"
COMPARE_API = "https://api.github.com/repos/{owner}/{repo}/compare/{base}...{head}"

REPO_RE = re.compile(r"github\.com/([^/]+)/([^/\s]+?)(?:\.git)?/?$")
HISTORY_RE = re.compile(r"^## History\s*$", re.M)
ENTRY_RE = re.compile(r"^\*\*(\d{4}-\d{2}-\d{2})\*\*", re.M)

# Statuses that mean the report's own claims have stopped being verifiable by
# anyone, as opposed to merely describing an older commit. These are what the
# scheduled run fails on; drift is not.
UNCHECKABLE = {"unreachable", "orphaned", "gone"}


class RateLimited(Exception):
    """The token ran out mid-run. A partial file is worse than no file."""


def field(text: str, name: str) -> str | None:
    match = re.search(rf"^{name}:\s*(\S+)\s*$", text, re.M)
    return match.group(1).strip('"') if match else None


def request(url: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "agent-memory-atlas"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 429) and exc.headers.get("x-ratelimit-remaining") == "0":
            reset = exc.headers.get("x-ratelimit-reset", "")
            raise RateLimited(reset) from exc
        return {"_error": f"http-{exc.code}"}
    except Exception as exc:  # noqa: BLE001 - a network failure is a result, not a crash
        return {"_error": type(exc).__name__}


def readings(text: str) -> list[str]:
    """Dates of the readings recorded in `## History`, newest first.

    Counted from the History section rather than from git: a re-read that
    changed nothing about the pin is still a reading, and the atlas records
    those (Mem0's `audit_log` mark was recovered at an unchanged commit). Git
    would also count copy-edits and count sweeps as attention the report never
    got.
    """
    heading = HISTORY_RE.search(text)
    if not heading:
        return []
    return ENTRY_RE.findall(text[heading.end():])


def rows_for(path: Path, as_of: dt.date, window: int) -> dict:
    text = path.read_text(encoding="utf-8")
    dates = readings(text)
    analyzed = field(text, "analyzed_at")
    cutoff = as_of - dt.timedelta(days=window)

    # The first reading is not a reanalysis, so it is excluded from both counts.
    # Otherwise every report added this week would rank as freshly attended-to
    # on the strength of the reading that created it.
    parsed = sorted(dt.date.fromisoformat(d) for d in dates)
    reanalyses = parsed[1:]

    row = {
        "slug": path.stem,
        "source_url": field(text, "source_url"),
        "repo": None,
        "default_branch": None,
        "status": None,
        "revision": field(text, "revision"),
        "head": None,
        "commits_drift": None,
        "pin_ahead_of_head_by": None,
        "stars": None,
        "analyzed_at": analyzed,
        "days_since_analysis": (as_of - dt.date.fromisoformat(analyzed)).days if analyzed else None,
        "first_reading": parsed[0].isoformat() if parsed else None,
        "last_reading": parsed[-1].isoformat() if parsed else None,
        "readings_total": len(parsed),
        "reanalyses_total": len(reanalyses),
        "reanalyses_recent": sum(1 for d in reanalyses if d > cutoff),
        "recent_window_days": window,
        "checked_at": as_of.isoformat(),
    }
    return row


def measure(row: dict) -> dict:
    """Fill in the upstream half of a row. Mutates and returns it.

    Two API calls per report, not three. The compare response already carries
    the branch head as the last commit it lists, so the head is only asked for
    separately when that list is truncated past 250 commits or the pin sits
    ahead of the branch. Worth the branching: the corpus is ~390 reports and
    grows, and the hourly ceiling is what decides whether a scheduled run
    finishes or stops halfway with a file that looks complete.
    """
    url, revision = row["source_url"], row["revision"]
    if not url or not revision:
        row["status"] = "unpinned"
        return row
    match = REPO_RE.search(url)
    if not match:
        row["status"] = "not-github"
        return row
    owner, repo = match.groups()
    row["repo"] = f"{owner}/{repo}"

    meta = request(REPO_API.format(owner=owner, repo=repo))
    if "_error" in meta:
        # A 404 here is not a failed request. The repository has been deleted,
        # renamed without a redirect, or taken private, and the report's source
        # link is dead — a finding, and one no drift number would ever show.
        row["status"] = "gone" if meta["_error"] == "http-404" else "error-" + meta["_error"]
        return row
    # A rename redirects and still resolves, so the row records where the repo
    # is *now* — a moved project is a re-read trigger of its own.
    row["repo"] = meta.get("full_name", row["repo"])
    row["stars"] = meta.get("stargazers_count")
    branch = meta.get("default_branch") or "main"
    row["default_branch"] = branch

    data = request(COMPARE_API.format(owner=owner, repo=repo, base=revision, head=branch))
    if "_error" in data:
        # A pin can be *unreachable* rather than merely old: force-pushes,
        # rebases and a swapped default branch leave commits GitHub still serves
        # by SHA but can no longer compare, so this is the only call that fails.
        # That is worse than staleness — the report cites a state that is not in
        # the branch's history at all, so every line number in it is unanchored.
        # TencentDB Agent Memory is the live case: its default branch is now
        # `feat/server_team`, which shares no ancestor with the pinned commit.
        # A transport failure is not the same finding and keeps its own status.
        row["status"] = (
            "unreachable"
            if data["_error"] in {"http-404", "http-422"}
            else "error-" + data["_error"]
        )
        return row

    ahead = data.get("ahead_by", 0)
    behind = data.get("behind_by", 0)
    row["commits_drift"] = ahead
    row["pin_ahead_of_head_by"] = behind

    commits = data.get("commits") or []
    if ahead == 0 and behind == 0:
        row["head"] = revision
    elif len(commits) == ahead:
        row["head"] = commits[-1]["sha"]
    else:
        # More than 250 commits of drift, so the compare truncated its list and
        # the last entry is not the head.
        head = request(HEAD_API.format(owner=owner, repo=repo, branch=branch))
        if isinstance(head, list) and head:
            row["head"] = head[0]["sha"]

    if data.get("status") == "diverged":
        row["status"] = "orphaned"
    elif ahead == 0:
        row["status"] = "current"
    else:
        row["status"] = "stale"
    return row


def order(row: dict) -> tuple:
    """Uncheckable pins first, then most-drifted, then everything measurable."""
    rank = 0 if row["status"] in UNCHECKABLE else 1
    return (rank, -(row["commits_drift"] or 0), row["slug"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, help="write JSONL here instead of stdout")
    parser.add_argument("--limit", type=int, default=0, help="check at most N reports")
    parser.add_argument("--only", action="append", default=[], help="slug to check (repeatable)")
    parser.add_argument("--window", type=int, default=14, help="days counted as recent (default 14)")
    parser.add_argument("--as-of", default=dt.date.today().isoformat(), help="date to measure against")
    args = parser.parse_args()

    as_of = dt.date.fromisoformat(args.as_of)
    paths = sorted(SYSTEMS.glob("*.md"))
    if args.only:
        wanted = set(args.only)
        paths = [p for p in paths if p.stem in wanted]
        missing = wanted - {p.stem for p in paths}
        if missing:
            print(f"No such report(s): {', '.join(sorted(missing))}", file=sys.stderr)
            return 2
    if args.limit:
        paths = paths[: args.limit]

    rows = []
    try:
        for path in paths:
            rows.append(measure(rows_for(path, as_of, args.window)))
    except RateLimited as exc:
        when = ""
        if str(exc).isdigit():
            when = dt.datetime.fromtimestamp(int(str(exc))).strftime(" (resets %H:%M local)")
        print(
            f"STOPPED: GitHub rate limit exhausted after {len(rows)} of {len(paths)} "
            f"reports{when}. Set GITHUB_TOKEN, or pass --limit and resume. Nothing "
            "written: a truncated register reads exactly like a clean one.",
            file=sys.stderr,
        )
        return 1

    rows.sort(key=order)
    text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)

    tally: dict[str, int] = {}
    for row in rows:
        tally[row["status"]] = tally.get(row["status"], 0) + 1
    drifted = [r for r in rows if r["status"] == "stale"]
    print(
        f"{len(rows)} reports: " + ", ".join(f"{n} {s}" for s, n in sorted(tally.items())),
        file=sys.stderr,
    )
    for row in drifted[:5]:
        print(
            f"  {row['commits_drift']:>6} commits since pin  {row['slug']:<32} "
            f"{row['repo']}  ({row['reanalyses_total']} reanalyses, "
            f"{row['reanalyses_recent']} in the last {args.window}d)",
            file=sys.stderr,
        )

    # Drift is not a failure. A pin is a deliberate claim about what was read, so
    # commits landing upstream is the normal state of every report here and a job
    # that goes red weekly for it is a job nobody reads. The two conditions that
    # do fail are the ones from `check_freshness.py`, and for the same reasons:
    # a pin no longer reachable in its branch's history means every quotation and
    # line number in that report has stopped being checkable, and a run where most
    # requests failed measured nothing while looking exactly like a clean result.
    broken = [r for r in rows if r["status"] in UNCHECKABLE]
    unresolved = [r for r in rows if str(r["status"]).startswith("error-")]
    if broken:
        print(
            f"\nFAIL: {len(broken)} report(s) can no longer be checked against the "
            "code they describe — " +
            ", ".join(f"{r['slug']} ({r['status']})" for r in broken[:10]) +
            ". Re-pin, re-review, or record that the source is gone.",
            file=sys.stderr,
        )
        return 1
    if rows and len(unresolved) > len(rows) // 4:
        print(
            f"\nFAIL: {len(unresolved)} of {len(rows)} reports did not resolve. This "
            "run did not measure drift — do not read it as evidence that the pins "
            "are current.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

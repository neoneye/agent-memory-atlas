#!/usr/bin/env python3
"""Render a drift register as a work list. Reads JSONL, writes text; no network.

Split from `drift_report.py` because measuring and ranking are different jobs
with different failure modes. Measuring costs an API budget and can only be
done online; ranking is a judgement that will be argued with and rewritten, and
should be re-runnable against a register captured weeks ago without asking
GitHub anything.

The ordering is deliberately dumb: reports that can no longer be checked at all,
then reports by how far their pin has moved. It does not weigh drift against
neglect or invent a staleness score.

**This is a register, not a re-read queue, and the difference matters.**
`notes/2026-08-04-automating-re-analysis.md` argues that sorting by
commits-since-pin is the worst available scheduling rule, because the projects it
puts at the top are the ones whose re-reads go stale fastest — churn belongs in
the denominator, with stars as a mild damping prior and a per-repo cadence cap
over the top. None of that is implemented here, on purpose: a score would bury
the judgement in a weight nobody revisits. What this prints is what moved and by
how much, beside how much attention each report has already had, so the person
deciding can see both numbers at once.

Usage:
    python3 scripts/drift_table.py [FILE] [--top N] [--markdown]

Reads stdin when no file is given, so it pipes straight off drift_report.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

UNCHECKABLE = {"pin-not-in-branch", "pin-unresolvable", "repo-gone"}

# Phrased so a reader cannot mistake a statement about the pin for a statement
# about the repository. The first version said "unreachable" of a live repo whose
# pin had been rewritten out of its branch, and it was read the obvious way.
REASON = {
    "pin-not-in-branch": "repo is live and the commit still resolves, but it is "
                         "no longer in the default branch's history",
    "pin-unresolvable": "GitHub no longer serves the pinned commit at all",
    "repo-gone": "repository deleted, renamed away, or private",
}

# The workflow keeps registers for 90 days so one week can be diffed against
# another, which means this has to keep reading files written before the rename.
# Without these an old artifact's uncheckable rows would fall through to "other"
# and silently stop being counted.
LEGACY = {"unreachable": "pin-not-in-branch", "orphaned": "pin-not-in-branch", "gone": "repo-gone"}


def load(path: str | None) -> list[dict]:
    text = sys.stdin.read() if path in (None, "-") else Path(path).read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", help="drift JSONL (default: stdin)")
    parser.add_argument("--top", type=int, default=25, help="drifted reports to list (default 25)")
    parser.add_argument("--markdown", action="store_true", help="emit a Markdown table")
    args = parser.parse_args()

    rows = load(args.file)
    if not rows:
        print("empty register", file=sys.stderr)
        return 1
    for row in rows:
        row["status"] = LEGACY.get(row["status"], row["status"])

    broken = [r for r in rows if r["status"] in UNCHECKABLE]
    stale = sorted(
        (r for r in rows if r["status"] == "stale"),
        key=lambda r: -(r["commits_drift"] or 0),
    )
    current = [r for r in rows if r["status"] == "current"]
    other = [r for r in rows if r["status"] not in UNCHECKABLE | {"stale", "current"}]

    out = []
    if broken:
        out.append("### Pins that no longer anchor — re-pin or re-review")
        out.append("")
        for r in sorted(broken, key=lambda r: r["slug"]):
            out.append(f"- `{r['slug']}` — {r['repo']} — **{r['status']}**: "
                       f"{REASON.get(r['status'], r['status'])}")
        out.append("")

    if not stale:
        out.append(f"No drifted reports in this register ({len(rows)} rows).")
        out.append("")
        print("\n".join(out + [
            f"{len(rows)} reports: {len(current)} at head, 0 drifted, "
            f"{len(broken)} uncheckable, {len(other)} other."
        ]))
        return 0

    out.append(f"### Most drifted ({min(args.top, len(stale))} of {len(stale)} stale)")
    out.append("")
    header = ("report", "repo", "drift", "stars", "re-reads", f"last {rows[0]['recent_window_days']}d", "pinned")
    if args.markdown:
        out.append("| " + " | ".join(header) + " |")
        out.append("|" + "|".join(["---"] * len(header)) + "|")
    else:
        out.append(
            f"{header[2]:>6}  {header[0]:<34} {header[1]:<40} "
            f"{header[3]:>7}  {header[4]}/{header[5]}  {header[6]}"
        )
    for r in stale[: args.top]:
        cells = (
            f"`{r['slug']}`" if args.markdown else r["slug"],
            r["repo"] or "",
            str(r["commits_drift"]),
            str(r["stars"] if r["stars"] is not None else ""),
            str(r["reanalyses_total"]),
            str(r["reanalyses_recent"]),
            f"{r['analyzed_at']} ({r['days_since_analysis']}d)",
        )
        if args.markdown:
            out.append("| " + " | ".join(cells) + " |")
        else:
            out.append(
                f"{cells[2]:>6}  {cells[0]:<34} {cells[1]:<40} "
                f"{cells[3]:>7}  {cells[4]}/{cells[5]}  {cells[6]}"
            )
    out.append("")
    out.append(
        f"{len(rows)} reports: {len(current)} at head, {len(stale)} drifted, "
        f"{len(broken)} uncheckable, {len(other)} other."
    )
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

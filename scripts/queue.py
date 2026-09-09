#!/usr/bin/env python3
"""Keep a short work queue of repositories to read next, ranked from the drift register.

`drift_report.py` measures; `drift_table.py` displays; this one *decides*, which
is the part `notes/2026-08-04-automating-re-analysis.md` argued should exist and
deliberately left unbuilt. That note is the source of the ranking here, and its
central claim is the one worth restating: **the queue is a selection against a
budget, not a work list that grows with staleness.** If sixty reports are stale
and the queue holds five, the answer is five. A backlog allowed to grow is a
backlog that gets abandoned, which is what happened to the freshness output that
preceded all of this.

Ranking
-------

    priority = signal / (star_term × churn_term × recency_term)

**signal** — `1 + log10(1 + commits_drift)`, so drift counts sub-linearly: a
4,000-commit gap is worth roughly twice a 60-commit one, not sixty times. A pin
that no longer anchors in its branch takes a fixed high signal instead, because
that is not staleness — the report cites a commit a reader cannot navigate to
from the default branch, and no drift number expresses it.

**star_term** — `log10(stars + 10)`, exactly as the note prescribes. Small
projects rank first. The reasoning there is worth keeping in view: a maintainer
with 40 stars reads an outside review closely because outside reviews are rare;
a maintainer with 40,000 has a triage queue. Logarithmic so it is a nudge across
two orders of magnitude rather than a cliff — a 40-star and a 400-star project
differ a little, a 400-star and a 40,000-star project differ noticeably, and
nothing is unreachable for being popular.

**churn_term** — velocity is a *cost*, not a signal. The obvious scheduler sorts
by commits-since-pin and puts the fastest-moving projects on top, which is the
worst available rule: a re-read of a repository landing 300 commits a day
describes a commit nobody is running by the end of the week. So commits per day
goes in the denominator, where it damps the treadmill instead of feeding it.

**recency_term** — a report re-read last Tuesday is not a candidate however far
its upstream has moved. Days since the last reading damp directly, and each
reading inside the register's own recent window damps again.

Then a hard cadence cap, which the note calls the crudest control here and
probably the most effective: nothing analyzed within `--cadence-days` is
eligible at all, unless its pin has stopped anchoring.

Every queued line carries the numbers that put it there. That is not decoration:
a scheduler whose weights are tuned once and never revisited quietly encodes
last quarter's beliefs, and the only defence is that each pick can be argued
with afterwards.

What this does not rank
-----------------------

Repositories with no report yet. The register is generated *from* the reports,
so a system the atlas has never read cannot appear in it. Those enter with
`add`, which is also how anything jumps the queue.

`repo-gone` rows are excluded: there is nothing left to read, and what those
reports need is an editorial decision about a dead source rather than a reading.
They are listed on `rank` so they are not silently dropped.

Usage
-----
    python3 scripts/queue.py fill              # top up to --max from the register
    python3 scripts/queue.py add <url>         # jump the queue; trims the tail
    python3 scripts/queue.py peek              # bare URL of the top item
    python3 scripts/queue.py list              # the queue, with reasons
    python3 scripts/queue.py done <url>        # remove one, wherever it sits
    python3 scripts/queue.py rank --top 20     # scoring, without touching the queue

The queue lives in gitignored `scripts/state/` and is never committed: it is
scheduling state, and the firewall the note asks for keeps it out of the
repository so a number that decides *where to look* can never be read back as
evidence about what is true.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "scripts" / "state"
REGISTER = STATE / "drift.jsonl"
QUEUE = STATE / "queue.txt"

# The queue holds five. This is a ceiling, not a default: a longer queue is a
# backlog, and a backlog has no point at which the work is finished. The first
# version made this a plain `--max` default, and within a day it was raised to
# ten to satisfy a request for "five more" on a queue that already held five —
# quoting the budget argument while breaking it. The correct answer to that
# request is to process the five first, so `--max` can lower the ceiling and
# cannot raise it.
QUEUE_CEILING = 5
DEFAULT_MAX = QUEUE_CEILING
DEFAULT_CADENCE_DAYS = 21

# A pin that no longer anchors is not far along a scale that starts at "current";
# it is a different failure. This is where it sits on the drift scale, roughly
# equivalent to a 10,000-commit gap, so it outranks ordinary drift without
# swamping the star and recency terms that decide between two broken pins.
BROKEN_SIGNAL = 5.0
BROKEN = {"pin-not-in-branch", "pin-unresolvable"}
LEGACY = {"unreachable": "pin-not-in-branch", "orphaned": "pin-not-in-branch", "gone": "repo-gone"}

URL_RE = re.compile(r"^(https?://\S+)")
# A published report page, which is the link a person actually has in front of
# them when they decide something needs re-reading. Queueing it verbatim would
# put a URL in the file that `work-the-queue` cannot clone, so `add` resolves it
# to the repository the report is about.
ATLAS_PAGE_RE = re.compile(r"/agent-memory-atlas/systems/([a-z0-9][a-z0-9-]*)/?$")
SYSTEMS = ROOT / "content" / "systems"
SOURCE_URL_RE = re.compile(r"^source_url:\s*(\S+)\s*$", re.M)


def normalize(url: str) -> str:
    return url.strip().rstrip("/").removesuffix(".git").lower()


def load_register(path: Path) -> list[dict]:
    if not path.is_file():
        sys.exit(
            f"No register at {path}. Build one first:\n"
            f"    GITHUB_TOKEN=... python3 scripts/drift_report.py --out {path}"
        )
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for row in rows:
        row["status"] = LEGACY.get(row["status"], row["status"])
    # A register is a measurement with a date on it, and ranking against an old
    # one silently queues work that may already be done. Warn rather than refuse:
    # an offline rank against last week's numbers is still a reasonable thing to
    # want, as long as nobody mistakes it for this week's.
    # Reconcile against the reports on disk before ranking. A register is a
    # measurement taken at a moment; the reports move on without it, and a row
    # whose `analyzed_at` predates the report's would re-queue work already done.
    # Eleven reports were re-read in one pass on 2026-09-09 against a register
    # measured that morning, and every one of them stayed eligible in it.
    # Cheap to fix and entirely offline: the report is the authority on when it
    # was last read.
    restated = 0
    for row in rows:
        report = SYSTEMS / f"{row['slug']}.md"
        if not report.is_file():
            continue
        text = report.read_text(encoding="utf-8")
        seen = re.search(r"^analyzed_at:\s*(\d{4}-\d{2}-\d{2})\s*$", text, re.M)
        pinned = re.search(r"^revision:\s*(\S+)\s*$", text, re.M)
        if seen and seen.group(1) != row.get("analyzed_at"):
            row["analyzed_at"] = seen.group(1)
            row["days_since_analysis"] = (dt.date.today() - dt.date.fromisoformat(seen.group(1))).days
            restated += 1
        # A report re-pinned since the measurement has no drift the register can
        # still vouch for, so it is not a candidate until the next run measures it.
        if pinned and row.get("revision") and pinned.group(1).strip('"') != row["revision"]:
            row["status"] = "repinned-since-measurement"
    if restated:
        print(
            f"note: {restated} row(s) restated from the reports on disk, which have been "
            f"read since this register was measured.",
            file=sys.stderr,
        )

    stamps = sorted({r.get("checked_at") for r in rows if r.get("checked_at")})
    if stamps:
        age = (dt.date.today() - dt.date.fromisoformat(stamps[0])).days
        if age > 7:
            print(
                f"warning: this register was measured {age} days ago ({stamps[0]}). "
                f"Re-run drift_report.py before trusting the ranking.",
                file=sys.stderr,
            )
    return rows


def score(row: dict) -> tuple[float, str]:
    """Priority and the one-line reason that justifies it."""
    drift = row.get("commits_drift") or 0
    stars = row.get("stars") or 0
    days = max(row.get("days_since_analysis") or 0, 1)
    recent = row.get("reanalyses_recent") or 0
    broken = row["status"] in BROKEN

    signal = BROKEN_SIGNAL if broken else 1 + math.log10(1 + drift)
    star_term = math.log10(stars + 10)
    churn_term = 1 + (drift / days) / 50          # 50 commits/day doubles the cost
    recency_term = max(1.0, 30 / days) * (1 + 2 * recent)

    priority = signal / (star_term * churn_term * recency_term)
    why = (
        f"{row['status']} drift={drift} stars={stars} "
        f"last={row.get('analyzed_at')} ({days}d) rereads={row.get('reanalyses_total', 0)}"
        f"/{recent}in{row.get('recent_window_days', 14)}d score={priority:.3f}"
    )
    return priority, why


def candidates(rows: list[dict], cadence_days: int) -> list[tuple[float, dict, str]]:
    out = []
    for row in rows:
        if row["status"] in ("repo-gone", "repinned-since-measurement") or not row.get("source_url"):
            continue
        if row["status"] not in BROKEN:
            if row["status"] != "stale":
                continue                                   # current, unpinned, not-github, errors
            if (row.get("days_since_analysis") or 0) < cadence_days:
                continue                                   # cadence cap
        priority, why = score(row)
        out.append((priority, row, why))
    out.sort(key=lambda t: (-t[0], t[1]["slug"]))
    return out


def read_queue() -> list[str]:
    if not QUEUE.is_file():
        return []
    return [ln for ln in QUEUE.read_text(encoding="utf-8").splitlines() if URL_RE.match(ln.strip())]


def write_queue(lines: list[str]) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text("".join(ln.rstrip() + "\n" for ln in lines), encoding="utf-8")


def url_of(line: str) -> str:
    return normalize(URL_RE.match(line.strip()).group(1))


def cmd_fill(args) -> int:
    lines = read_queue()
    if len(lines) >= args.max:
        print(f"queue already holds {len(lines)} (max {args.max}); nothing added", file=sys.stderr)
        return 0
    held = {url_of(ln) for ln in lines}
    rows = load_register(args.register)
    added = 0
    for priority, row, why in candidates(rows, args.cadence_days):
        if len(lines) >= args.max:
            break
        if normalize(row["source_url"]) in held:
            continue
        lines.append(f"{row['source_url']}  # {row['slug']} — {why}")
        held.add(normalize(row["source_url"]))
        added += 1
    write_queue(lines)
    print(f"appended {added}; queue holds {len(lines)} of {args.max} — {QUEUE}", file=sys.stderr)
    for ln in lines:
        print(ln)
    return 0


def resolve(url: str) -> tuple[str, str]:
    """Return the repository URL to queue, and a note about how it was reached."""
    url = url.strip()
    page = ATLAS_PAGE_RE.search(url)
    if not page:
        return url, ""
    report = SYSTEMS / f"{page.group(1)}.md"
    if not report.is_file():
        sys.exit(f"{url} names `{page.group(1)}`, which is not a report in content/systems/")
    found = SOURCE_URL_RE.search(report.read_text(encoding="utf-8"))
    if not found:
        sys.exit(f"{report.name} has no source_url to queue")
    return found.group(1).strip('"'), f" (from the {page.group(1)} report page)"


def cmd_add(args) -> int:
    if not URL_RE.match(args.url.strip()):
        sys.exit(f"not a URL: {args.url}")
    url, via = resolve(args.url)
    # If the register already knows this repository, carry its reason rather than
    # "inserted by hand": a queue line is supposed to justify itself, and a hand
    # pick is exactly the one a reader will want the numbers for later.
    why = f"inserted by hand{via}"
    if args.register.is_file():
        match = next(
            (r for r in load_register(args.register) if normalize(r.get("source_url") or "") == normalize(url)),
            None,
        )
        if match:
            why = f"inserted by hand{via} — {match['slug']} — {score(match)[1]}"
    lines = [ln for ln in read_queue() if url_of(ln) != normalize(url)]
    lines.insert(0, f"{url}  # {why}")
    dropped = lines[args.max:]
    write_queue(lines[: args.max])
    print(f"queued at the front; {len(lines[:args.max])} of {args.max}", file=sys.stderr)
    for ln in dropped:
        print(f"dropped from the tail: {ln}", file=sys.stderr)
    for ln in lines[: args.max]:
        print(ln)
    return 0


def cmd_peek(args) -> int:
    lines = read_queue()
    if not lines:
        print("queue is empty; run `python3 scripts/queue.py fill`", file=sys.stderr)
        return 1
    print(URL_RE.match(lines[0].strip()).group(1))
    return 0


def cmd_list(args) -> int:
    lines = read_queue()
    if not lines:
        print("queue is empty", file=sys.stderr)
        return 1
    for i, ln in enumerate(lines, 1):
        print(f"{i}. {ln}")
    return 0


def cmd_done(args) -> int:
    lines = read_queue()
    kept = [ln for ln in lines if url_of(ln) != normalize(args.url)]
    if len(kept) == len(lines):
        print(f"not in the queue: {args.url}", file=sys.stderr)
        return 1
    write_queue(kept)
    print(f"removed; queue holds {len(kept)}", file=sys.stderr)
    return 0


def cmd_rank(args) -> int:
    rows = load_register(args.register)
    ranked = candidates(rows, args.cadence_days)
    for priority, row, why in ranked[: args.top]:
        print(f"{priority:7.3f}  {row['slug']:<32} {row['repo'] or '':<40} {why}")
    gone = [r for r in rows if r["status"] == "repo-gone"]
    held = sum(
        1
        for r in rows
        if r["status"] == "stale" and (r.get("days_since_analysis") or 0) < args.cadence_days
    )
    print(
        f"\n{len(ranked)} eligible of {len(rows)} rows; {held} held by the "
        f"{args.cadence_days}-day cadence cap; {len(gone)} excluded as repo-gone"
        + (": " + ", ".join(r["slug"] for r in gone) if gone else ""),
        file=sys.stderr,
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--register", type=Path, default=REGISTER)
    ap.add_argument("--max", type=int, default=DEFAULT_MAX,
                    help=f"lower the queue ceiling below {QUEUE_CEILING}; it cannot be raised")
    ap.add_argument("--cadence-days", type=int, default=DEFAULT_CADENCE_DAYS)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("fill").set_defaults(fn=cmd_fill)
    p = sub.add_parser("add"); p.add_argument("url"); p.set_defaults(fn=cmd_add)
    sub.add_parser("peek").set_defaults(fn=cmd_peek)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    p = sub.add_parser("done"); p.add_argument("url"); p.set_defaults(fn=cmd_done)
    p = sub.add_parser("rank"); p.add_argument("--top", type=int, default=20); p.set_defaults(fn=cmd_rank)
    args = ap.parse_args()
    if args.max > QUEUE_CEILING:
        sys.exit(
            f"--max {args.max} exceeds the queue ceiling of {QUEUE_CEILING}. The cap is the "
            f"point of the queue: it is a selection against a budget, not a backlog that grows "
            f"with staleness.\n"
            f"If the queue is full and more work needs queueing, process what is in it first, "
            f"or use `add` to put one item at the front and let the tail fall off."
        )
    if not getattr(args, "fn", None):
        args.fn = cmd_list
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())

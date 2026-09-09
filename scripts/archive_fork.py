#!/usr/bin/env python3
"""Fork every repository the atlas cites into the archive organisation.

Every claim in this atlas is pinned to a commit in somebody else's repository,
which means every claim depends on that repository continuing to exist. It does
not always. The 2026-09-09 drift run found `Renkasha/Sovereign` returning 404 on
both the repository and the pinned sha — a report whose evidence is gone for
everyone, permanently — and seven more pins that no longer anchor in their
branch. A fork is the cheapest insurance against the first failure and a useful
record against the second.

Naming: every fork is `<owner>--<repo>`, not `<repo>`.

    techtheist/engram          ->  techtheist--engram
    Harshitk-cp/engram         ->  Harshitk-cp--engram
    Gentleman-Programming/engram -> Gentleman-Programming--engram

The organisation namespace is flat and the corpus already contains six colliding
names across thirteen repositories — three separate `engram`s, two `agentmemory`s,
two `memos`, and the two unrelated `sage`s. A scheme that only disambiguates on
collision has to be re-decided every time the corpus grows; this one never does,
and the fork name is the upstream identity rather than a guess about it.

`default_branch_only` is false on purpose. A pin is not always on the default
branch — the atlas's Kage report was pinned to a branch the project later named
`archive/remote-final` — so an archive that took only `main` would miss exactly
the commits most in need of archiving.

Usage:
    python3 scripts/archive_fork.py --dry-run          # what would be forked
    python3 scripts/archive_fork.py                    # do it, resumable
    python3 scripts/archive_fork.py --suggest-helpers  # repos the reports cite

Set GITHUB_TOKEN with `repo` scope and admin on the target organisation.
Idempotent: a fork that already exists is skipped, so a failed run resumes by
being re-run.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEMS = ROOT / "content" / "systems"
STATE = ROOT / "scripts" / "state"
LEDGER = STATE / "archive-forks.jsonl"
EXTRA = ROOT / "scripts" / "archive-extra-repos.txt"

ORG = "agent-memory-atlas-archive"
API = "https://api.github.com"

# Matches a repository URL, including one pointing at a subdirectory: the atlas
# cites one system as a path inside GoogleCloudPlatform/generative-ai, and the
# thing to archive is the repository that contains it.
REPO_RE = re.compile(
    r"github\.com/([A-Za-z0-9][\w.-]*)/([\w.-]+?)(?:\.git)?(?:/(?:tree|blob|pull|issues)/[^\s)]*)?/?$"
)
SOURCE_URL = re.compile(r"^source_url:\s*(\S+)\s*$", re.M)

# GitHub's secondary limit on content-creating requests is 80/minute and
# 500/hour. ~400 forks fits inside the hourly budget only just, so the default
# pace is deliberately under it rather than racing to the ceiling and being
# throttled into a partial run that looks finished.
SLEEP_SECONDS = 8.0


def token() -> str:
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if not tok:
        sys.exit("Set GITHUB_TOKEN (repo scope, admin on the target organisation).")
    return tok


def request(method: str, url: str, body: dict | None = None) -> tuple[int, dict | list | None, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "agent-memory-atlas-archive")
    req.add_header("Authorization", f"Bearer {token()}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None), dict(r.headers)
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw) if raw else None
        except Exception:  # noqa: BLE001
            payload = {"message": raw[:200].decode("utf-8", "replace")}
        return exc.code, payload, dict(exc.headers)
    except Exception as exc:  # noqa: BLE001 - a network failure is a result
        return 0, {"message": type(exc).__name__}, {}


def fork_name(owner: str, repo: str) -> str:
    return f"{owner}--{repo}"


def corpus_repos() -> dict[str, tuple[str, str, list[str]]]:
    """{lowercased owner/repo: (owner, repo, [slugs that cite it])}."""
    found: dict[str, tuple[str, str, list[str]]] = {}
    for path in sorted(SYSTEMS.glob("*.md")):
        match = SOURCE_URL.search(path.read_text(encoding="utf-8"))
        if not match:
            continue
        hit = REPO_RE.search(match.group(1).strip('"'))
        if not hit:
            continue
        owner, repo = hit.group(1), hit.group(2)
        key = f"{owner}/{repo}".lower()
        if key in found:
            found[key][2].append(path.stem)
        else:
            found[key] = (owner, repo, [path.stem])
    return found


def extra_repos() -> dict[str, tuple[str, str, list[str]]]:
    """Hand-maintained additions — helper repositories a project depends on.

    Auto-detecting "the helper repos a project uses" is not something this script
    can do honestly: a dependency manifest names packages, not the repositories
    behind them, and a repository referenced in a README may be an inspiration
    rather than a dependency. `--suggest-helpers` proposes candidates from the
    reports' own prose; a person decides, and the decision lands here.
    """
    out: dict[str, tuple[str, str, list[str]]] = {}
    if not EXTRA.is_file():
        return out
    for line in EXTRA.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        if "/" not in line:
            sys.exit(f"{EXTRA.name}: not an owner/repo line: {line!r}")
        owner, repo = line.split("/", 1)
        out[f"{owner}/{repo}".lower()] = (owner, repo, ["(extra)"])
    return out


def suggest_helpers() -> int:
    """Print GitHub repositories the reports mention that the atlas does not cover."""
    known = set(corpus_repos()) | set(extra_repos())
    link = re.compile(r"github\.com/([A-Za-z0-9][\w.-]*)/([\w.-]+?)(?:\.git)?(?=[)\s/\"'>]|$)")
    seen: dict[str, set[str]] = {}
    for path in sorted(SYSTEMS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        own = SOURCE_URL.search(text)
        own_key = ""
        if own:
            hit = REPO_RE.search(own.group(1).strip('"'))
            if hit:
                own_key = f"{hit.group(1)}/{hit.group(2)}".lower()
        for owner, repo in link.findall(text):
            key = f"{owner}/{repo}".lower()
            if key in known or key == own_key:
                continue
            seen.setdefault(key, set()).add(path.stem)
    for key in sorted(seen, key=lambda k: (-len(seen[k]), k)):
        slugs = sorted(seen[key])
        print(f"{key:<52} cited by {len(slugs):>2}: {', '.join(slugs[:4])}"
              + (" …" if len(slugs) > 4 else ""))
    print(
        f"\n{len(seen)} repositories are referenced by a report and not covered by the atlas. "
        f"These are candidates, not a work list: many are prior art or a comparison rather than a "
        f"helper this project needs to run. Put the ones worth archiving in {EXTRA.name}, one "
        f"`owner/repo` per line, with the reason in a trailing comment.",
        file=sys.stderr,
    )
    return 0


def record(entry: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="list what would be forked")
    ap.add_argument("--suggest-helpers", action="store_true",
                    help="print repositories the reports cite that the atlas does not cover")
    ap.add_argument("--limit", type=int, default=0, help="fork at most N this run")
    ap.add_argument("--only", action="append", default=[], metavar="OWNER/REPO")
    ap.add_argument("--sleep", type=float, default=SLEEP_SECONDS,
                    help=f"seconds between fork requests (default {SLEEP_SECONDS})")
    args = ap.parse_args()

    if args.suggest_helpers:
        return suggest_helpers()

    repos = {**corpus_repos(), **extra_repos()}
    if args.only:
        wanted = {o.lower() for o in args.only}
        repos = {k: v for k, v in repos.items() if k in wanted}
        missing = wanted - set(repos)
        if missing:
            sys.exit(f"not in the corpus: {', '.join(sorted(missing))}")

    todo = []
    for key, (owner, repo, slugs) in sorted(repos.items()):
        name = fork_name(owner, repo)
        status, _, _ = request("GET", f"{API}/repos/{ORG}/{name}")
        if status == 200:
            continue                      # already archived; resumable by construction
        todo.append((key, owner, repo, name, slugs))

    print(f"{len(repos)} repositories cited, {len(repos) - len(todo)} already forked, "
          f"{len(todo)} to fork.", file=sys.stderr)
    if args.limit:
        todo = todo[: args.limit]
    if args.dry_run:
        for key, owner, repo, name, slugs in todo:
            print(f"{key:<52} -> {ORG}/{name:<56} ({', '.join(slugs)})")
        return 0

    created = failed = 0
    for i, (key, owner, repo, name, slugs) in enumerate(todo, 1):
        status, payload, headers = request(
            "POST", f"{API}/repos/{owner}/{repo}/forks",
            {"organization": ORG, "name": name, "default_branch_only": False},
        )
        if status in (200, 202):
            created += 1
            print(f"[{i}/{len(todo)}] forked  {key} -> {ORG}/{name}")
            record({"upstream": key, "fork": f"{ORG}/{name}", "status": "forked", "slugs": slugs})
        elif status == 403 and "rate" in str(payload.get("message", "")).lower():
            wait = int(headers.get("Retry-After", 60))
            print(f"[{i}/{len(todo)}] rate limited, sleeping {wait}s then retrying {key}",
                  file=sys.stderr)
            time.sleep(wait + 1)
            status, payload, _ = request(
                "POST", f"{API}/repos/{owner}/{repo}/forks",
                {"organization": ORG, "name": name, "default_branch_only": False},
            )
            if status in (200, 202):
                created += 1
                record({"upstream": key, "fork": f"{ORG}/{name}", "status": "forked", "slugs": slugs})
            else:
                failed += 1
                record({"upstream": key, "status": f"http-{status}",
                        "detail": str(payload.get("message"))[:200], "slugs": slugs})
        else:
            failed += 1
            msg = str((payload or {}).get("message"))[:120]
            print(f"[{i}/{len(todo)}] FAILED  {key}: http-{status} {msg}", file=sys.stderr)
            record({"upstream": key, "status": f"http-{status}", "detail": msg, "slugs": slugs})
        time.sleep(args.sleep)

    print(f"\n{created} forked, {failed} failed. Ledger: {LEDGER}", file=sys.stderr)
    # A repository that cannot be forked is the case this whole script exists for:
    # it is already gone, or private, or blocked. That is a finding for the report
    # that cites it, not a crash here.
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

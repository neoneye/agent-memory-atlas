#!/usr/bin/env python3
"""Keep the archive forks current, preserving whatever a force-push would destroy.

`archive_fork.py` takes the snapshot; this keeps it. The invariant it maintains:

  * the fork's default branch always equals the upstream's default branch head
  * no commit the archive has ever held is lost to a force-push upstream

Those two pull against each other, which is the whole problem. Upstream rebases,
squash-merges and branch resets are common — the atlas's own drift register found
seven pins that no longer anchor in their branch — and a plain mirror would
silently adopt the rewritten history and drop the commits a report was pinned to.

So a divergence is not an error to resolve, it is a thing to keep. When the
fork's current head is no longer an ancestor of upstream's, the head is saved
first, under a timestamped branch:

    agent-memory-atlas-archive/2026-09-09-21-14-07

and only then is the default branch moved to the upstream head. `main` is the
current snapshot; the dated branches are every snapshot it used to be.

This works without cloning anything. A fork shares an object network with its
parent, so a ref in the fork can be pointed at a sha that arrived through the
parent, and the whole sync is ref arithmetic over the API — which is what makes
running it over ~400 repositories cheap enough to schedule.

Upstream disappearing is the case the archive exists for and is not a failure
here: the fork is left exactly as it is, recorded as `upstream-gone`, and it
becomes the only surviving copy.

A deleted upstream has a second form that does not look like one. GitHub does
not leave an orphaned fork network parentless — it reparents the network onto a
surviving sibling — so `parent` keeps naming *a* repository, just not the one
the archive forked. Following it silently is how a snapshot gets overwritten
with a stranger's history. Every fork's `parent` is therefore checked against
its own `<owner>--<repo>` name before anything is read from it, and a
disagreement is classified rather than followed: a rename (the old name
redirects to the parent) is the same repository and is synced, reported as
`current-upstream-renamed` so a person can rename the fork; anything else is
`upstream-reparented` and nothing is touched.

Scope: the default branch is tracked. Every other branch is captured once, at
fork time, and divergence in them is reported rather than followed — mirroring
every branch of every repository is a different and much more expensive job.

Usage:
    python3 scripts/archive_sync.py --dry-run
    python3 scripts/archive_sync.py
    python3 scripts/archive_sync.py --only owner/repo

Set GITHUB_TOKEN with `repo` scope and write access to the organisation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "scripts" / "state"
LEDGER = STATE / "archive-sync.jsonl"

ORG = "agent-memory-atlas-archive"
API = "https://api.github.com"
BRANCH_PREFIX = ORG          # agent-memory-atlas-archive/<timestamp>


def token() -> str:
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if not tok:
        sys.exit("Set GITHUB_TOKEN (repo scope, write access to the organisation).")
    return tok


def request(method: str, url: str, body: dict | None = None):
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
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw) if raw else None
        except Exception:  # noqa: BLE001
            payload = {"message": raw[:200].decode("utf-8", "replace")}
        return exc.code, payload
    except Exception as exc:  # noqa: BLE001
        return 0, {"message": type(exc).__name__}


def paged(url: str):
    page, out = 1, []
    while True:
        status, payload = request("GET", f"{url}{'&' if '?' in url else '?'}per_page=100&page={page}")
        if status != 200 or not payload:
            break
        out.extend(payload)
        if len(payload) < 100:
            break
        page += 1
    return out


def stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")


def record(entry: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    entry["at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


def head_sha(full_name: str, branch: str) -> str | None:
    status, payload = request("GET", f"{API}/repos/{full_name}/commits/{branch}?per_page=1")
    return payload.get("sha") if status == 200 and isinstance(payload, dict) else None


def candidate_upstreams(fork_name: str) -> list[str]:
    """Every `owner/repo` a `<owner>--<repo>` fork name could have come from.

    Usually one. More when a name contains a second `--`, which happens because
    GitHub allows it in an account name: `johan--/mneme` forks as
    `johan----mneme`, and splitting on the first separator would read that as
    `johan/--mneme`. Every split point is offered instead, so a real upstream is
    always among the candidates and a match is never missed.
    """
    out, idx = [], fork_name.find("--")
    while idx != -1:
        owner, repo = fork_name[:idx], fork_name[idx + 2:]
        if owner and repo:
            out.append(f"{owner}/{repo}")
        idx = fork_name.find("--", idx + 1)
    return out


def classify_parent(fork_name: str, parent: str) -> tuple[str, str | None]:
    """Does `parent` still name the repository this fork was taken from?

    GitHub's `parent` is not stable. When the root of a fork network is deleted
    the network is reparented onto a surviving sibling, and the field then names
    a repository the archive never forked. Following it is not a no-op: the
    sibling's history is unrelated, so every sync sees a divergence and resets
    the archived default branch onto a stranger's commits. That happened to
    `Perseus-Computing-LLC--perseus-vault` on 2026-09-13 — deleted upstream,
    reparented to `johan--/mneme`, and one sync moved `main` from a 6 September
    head to an unrelated 29 June one. Nothing was lost, because the preserve
    step ran first, but the archive's default branch showed the wrong project.

    A rename produces the same disagreement and is harmless: the repository is
    the same one under a new name. The two are told apart by asking what the
    original name does now — GitHub redirects a rename and 404s a deletion — so
    the check costs one request, and only on a fork whose name already
    disagrees.

    Returns `(verdict, matched_name)` where verdict is `ok`, `renamed` or
    `reparented`.
    """
    candidates = candidate_upstreams(fork_name)
    if not candidates:
        return "ok", None                      # not a `--` name; nothing to check
    if parent.lower() in {c.lower() for c in candidates}:
        return "ok", parent
    for candidate in candidates:
        # urllib follows the redirect a rename leaves behind, so a 200 whose
        # `full_name` is the parent means the repository moved rather than died.
        status, moved = request("GET", f"{API}/repos/{candidate}")
        if status == 200 and isinstance(moved, dict) \
                and (moved.get("full_name") or "").lower() == parent.lower():
            return "renamed", candidate
    return "reparented", None


def sync_one(fork: dict, dry_run: bool) -> dict:
    name = fork["name"]
    fork_full = f"{ORG}/{name}"
    parent = (fork.get("parent") or {}).get("full_name")
    if not parent:
        return {"fork": fork_full, "status": "no-parent"}

    verdict, matched = classify_parent(name, parent)
    if verdict == "reparented":
        # Touch nothing. The fork is the archived copy of a repository that no
        # longer exists, and the only thing `parent` still offers is somebody
        # else's history.
        return {"fork": fork_full, "upstream": parent, "status": "upstream-reparented"}

    status, upstream = request("GET", f"{API}/repos/{parent}")
    if status == 404:
        # The reason this archive exists. Leave the fork untouched: it is now the copy.
        return {"fork": fork_full, "upstream": parent, "status": "upstream-gone"}
    if status != 200 or not isinstance(upstream, dict):
        return {"fork": fork_full, "upstream": parent, "status": f"upstream-error-{status}"}

    up_branch = upstream.get("default_branch") or "main"
    fork_branch = fork.get("default_branch") or up_branch
    up_sha = head_sha(parent, up_branch)
    our_sha = head_sha(fork_full, fork_branch)
    if not up_sha:
        return {"fork": fork_full, "upstream": parent, "status": "upstream-head-unreadable"}
    if not our_sha:
        return {"fork": fork_full, "upstream": parent, "status": "fork-head-unreadable"}
    if up_sha == our_sha:
        # A renamed upstream is still the right upstream, so the sync is correct
        # and complete — but the fork's own name is now stale and only a person
        # can rename it, so say so instead of reporting `current` and moving on.
        status_name = "current-upstream-renamed" if verdict == "renamed" else "current"
        return {"fork": fork_full, "upstream": parent, "status": status_name, "sha": up_sha}

    # Is our head still in upstream's history? Compare inside the fork, which can
    # see both sides of the object network.
    status, cmp = request("GET", f"{API}/repos/{fork_full}/compare/{our_sha}...{up_sha}")
    diverged = True
    if status == 200 and isinstance(cmp, dict):
        diverged = cmp.get("status") == "diverged" or (cmp.get("behind_by") or 0) > 0
    ahead_by = (cmp or {}).get("ahead_by") if isinstance(cmp, dict) else None

    result = {
        "fork": fork_full, "upstream": parent, "branch": fork_branch,
        "from": our_sha, "to": up_sha, "ahead_by": ahead_by,
    }

    if dry_run:
        result["status"] = "would-preserve-and-reset" if diverged else "would-fast-forward"
        return result

    if diverged:
        # Save what a reset would destroy, before destroying it. If this fails the
        # reset does not happen — losing the old head is the one outcome that makes
        # the archive worthless.
        branch = f"{BRANCH_PREFIX}/{stamp()}"
        status, payload = request(
            "POST", f"{API}/repos/{fork_full}/git/refs",
            {"ref": f"refs/heads/{branch}", "sha": our_sha},
        )
        if status not in (200, 201):
            result["status"] = f"preserve-failed-{status}"
            result["detail"] = str((payload or {}).get("message"))[:160]
            return result
        result["preserved_as"] = branch

    status, payload = request(
        "PATCH", f"{API}/repos/{fork_full}/git/refs/heads/{fork_branch}",
        {"sha": up_sha, "force": True},
    )
    if status != 200:
        result["status"] = f"update-failed-{status}"
        result["detail"] = str((payload or {}).get("message"))[:160]
        return result

    result["status"] = "preserved-and-reset" if diverged else "fast-forwarded"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", action="append", default=[], metavar="FORK_NAME_OR_UPSTREAM")
    ap.add_argument("--sleep", type=float, default=0.3)
    args = ap.parse_args()

    forks = paged(f"{API}/orgs/{ORG}/repos?type=all")
    if not forks:
        sys.exit(f"No repositories found in {ORG} (or the token cannot see them).")
    if args.only:
        # The org listing omits `parent`, so an upstream `owner/repo` argument is
        # matched by the name the fork would carry rather than by re-fetching all
        # of them to read a field the filter is about to discard.
        wanted = set()
        for arg in args.only:
            wanted.add(arg.lower())
            if "/" in arg:
                wanted.add(arg.replace("/", "--", 1).lower())
        forks = [f for f in forks if f["name"].lower() in wanted]
        if not forks:
            sys.exit(f"no fork in {ORG} matches {', '.join(args.only)}")

    tally: dict[str, int] = {}
    for i, fork in enumerate(forks, 1):
        # The org listing omits `parent`; the per-repo read carries it.
        status, full = request("GET", f"{API}/repos/{ORG}/{fork['name']}")
        outcome = sync_one(full if status == 200 and isinstance(full, dict) else fork, args.dry_run)
        tally[outcome["status"]] = tally.get(outcome["status"], 0) + 1
        if outcome["status"] not in ("current",):
            print(f"[{i}/{len(forks)}] {outcome['status']:<26} {outcome['fork']}"
                  + (f"  preserved as {outcome['preserved_as']}" if outcome.get("preserved_as") else ""))
        if not args.dry_run and outcome["status"] != "current":
            record(outcome)
        time.sleep(args.sleep)

    print("\n" + ", ".join(f"{n} {s}" for s, n in sorted(tally.items())), file=sys.stderr)
    # A fork that could not be updated is worth a non-zero exit: the archive is
    # then not what it claims to be. An upstream that is gone is not — that is the
    # archive doing its job.
    bad = sum(n for s, n in tally.items() if "failed" in s or "error" in s or "unreadable" in s)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

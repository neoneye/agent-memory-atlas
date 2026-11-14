#!/usr/bin/env python3
"""Replace one archive fork with a standalone copy, keeping every pin it cites.

A fork in the archive cannot be brought up to date without writing upstream:
moving its branch makes each commit message that names `#N` add "neoneye added
a commit ... that referenced this issue" to the parent's issue or pull request
(notes/2026-11-01-archive-copies-not-forks.md). A copy outside the fork network
has no such link, so a re-read converts the fork it touches instead of syncing
it. The name stays `<owner>--<repo>`, so `archive_name` and
`check_archive_names.py` are unchanged.

What it does, per repository, in an order that loses nothing if it stops:

  1. Confirms `agent-memory-atlas-archive/<owner>--<repo>` is a fork whose
     parent or source is the upstream, and that the upstream's licence and size
     allow a copy (the same refusals as `archive_mirror.py`). A refused
     repository stays a frozen fork, and the script says so.
  2. Collects every pin the atlas cites for the upstream: each report's
     `revision` and every `<source_url>/commit/<sha>` link in it, History
     entries included.
  3. Bare-clones the upstream and fetches each pin by sha, from the upstream or
     else from the fork, which still holds commits the upstream rewrote away.
     **If any pin is missing locally, it stops here and deletes nothing.**
  4. Deletes the fork and waits for the name to free.
  5. Creates the copy, switches Actions off and reads that back, pushes every
     branch and tag plus `refs/tags/atlas-pin-<sha>` for every pin, sets the
     default branch, and reads each pin back through the API.

If step 5 fails, the local bare clone is kept and its path printed: it holds
every pin, and `git push` from it to a recreated copy finishes the job.

Usage:
    python3 scripts/archive_convert.py --dry-run --only owner/repo   # steps 1-3, nothing deleted
    python3 scripts/archive_convert.py --only owner/repo

Exit codes: 0 converted (or, with --dry-run, convertible); 1 refused or failed.

Set GITHUB_TOKEN with `repo` and `delete_repo` scopes and admin on the
organisation; `gh auth token` works.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive_fork as af  # noqa: E402
import archive_mirror as am  # noqa: E402

sys.stdout.reconfigure(line_buffering=True)

ORG = af.ORG
API = af.API


def cited_pins(owner: str, repo: str) -> tuple[set[str], list[str]]:
    """Every sha the reports cite for owner/repo, and the slugs that cite it."""
    key = f"{owner}/{repo}".lower()
    link = re.compile(rf"https://github\.com/{re.escape(owner)}/{re.escape(repo)}/commit/([0-9a-f]{{40}})", re.I)
    pins: set[str] = set()
    slugs: list[str] = []
    for path in sorted(af.SYSTEMS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        src = af.SOURCE_URL.search(text)
        hit = af.REPO_RE.search(src.group(1).strip('"')) if src else None
        if not hit or f"{hit.group(1)}/{hit.group(2)}".lower() != key:
            continue
        slugs.append(path.stem)
        rev = am.REVISION.search(text)
        if rev:
            pins.add(rev.group(1))
        pins.update(m.lower() for m in link.findall(text))
    return pins, slugs


def check_fork(name: str, key: str) -> str | None:
    """None when the archive repo is a fork of the upstream; else why not."""
    status, payload, _ = af.request("GET", f"{API}/repos/{ORG}/{name}")
    if status == 404:
        return "no archive repository: use `archive_mirror.py --only` instead"
    if status != 200 or not isinstance(payload, dict):
        return f"http-{status} reading {ORG}/{name}"
    if not payload.get("fork"):
        return "already a copy: `archive_mirror.py --only` adds the new pin"
    parents = {((payload.get(k) or {}).get("full_name") or "").lower() for k in ("parent", "source")}
    if key not in parents:
        return f"fork of {', '.join(sorted(p for p in parents if p))}, not {key}: left alone"
    return None


def gather(owner: str, repo: str, name: str, pins: set[str], bare: Path) -> str | None:
    """Clone upstream into `bare` and make every pin present. None on success."""
    r = am.git("clone", "--bare", "--quiet", f"https://github.com/{owner}/{repo}.git", str(bare))
    if r.returncode != 0:
        return f"clone failed: {r.stderr.strip()[-160:]}"
    am.git("remote", "add", "fork", f"https://github.com/{ORG}/{name}.git", cwd=bare)
    missing = []
    for sha in sorted(pins):
        for remote in ("origin", "fork"):
            if am.git("cat-file", "-e", f"{sha}^{{commit}}", cwd=bare).returncode == 0:
                break
            am.git("fetch", "--quiet", remote, sha, cwd=bare, auth=True)
        if am.git("cat-file", "-e", f"{sha}^{{commit}}", cwd=bare).returncode != 0:
            missing.append(sha)
    if missing:
        return f"pin(s) held by neither upstream nor fork: {', '.join(missing)}"
    return None


def delete_fork(name: str) -> str | None:
    status, payload, _ = af.request("DELETE", f"{API}/repos/{ORG}/{name}")
    if status != 204:
        return f"delete http-{status} {str((payload or {}).get('message', ''))[:100]}"
    for _ in range(30):
        status, _, _ = af.request("GET", f"{API}/repos/{ORG}/{name}")
        if status == 404:
            return None
        time.sleep(2)
    return "fork still visible a minute after deletion"


PUSH_BATCH = 150


def push(bare: Path, name: str, pins: set[str]) -> str | None:
    """Push every branch, tag and pin, a batch of refs at a time.

    One push of all refs returned HTTP 500 from GitHub on RakuenSoftware/aimee
    (1,355 branches, 209 tags, 660 MB) after the fork was already deleted, which
    left the archive empty until the refs were pushed by hand in batches.
    """
    listed = am.git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/tags", cwd=bare)
    if listed.returncode != 0:
        return f"could not list refs: {listed.stderr.strip()[-200:]}"
    refspecs = [f"{ref}:{ref}" for ref in listed.stdout.split()]
    refspecs += [f"{sha}:refs/tags/atlas-pin-{sha}" for sha in sorted(pins)]
    url = f"https://github.com/{ORG}/{name}.git"
    for start in range(0, len(refspecs), PUSH_BATCH):
        r = am.git("push", "--quiet", url, *refspecs[start:start + PUSH_BATCH], cwd=bare, auth=True)
        if r.returncode != 0:
            return f"push failed at ref {start} of {len(refspecs)}: {r.stderr.strip()[-200:]}"
    return None


def convert(owner: str, repo: str, dry_run: bool) -> str:
    key = f"{owner}/{repo}".lower()
    name = af.fork_name(owner, repo)
    why = check_fork(name, key)
    if why:
        return f"skipped: {why}"
    spdx, upstream = am.licence_of(owner, repo)
    if upstream is None:
        return f"upstream-unreadable ({spdx}): the fork stays"
    if spdx not in am.REDISTRIBUTABLE:
        return f"refused-licence ({spdx}): stays a frozen fork"
    if int(upstream.get("size") or 0) > am.MAX_HISTORY_KB:
        return "refused-size (over GitHub's 2 GB push limit): stays a frozen fork"
    pins, slugs = cited_pins(owner, repo)
    if not pins:
        return "failed: no cited pin found in the reports"

    tmp = Path(tempfile.mkdtemp(prefix="atlas-convert-"))
    bare = tmp / f"{name}.git"
    problem = gather(owner, repo, name, pins, bare)
    if problem:
        shutil.rmtree(tmp, ignore_errors=True)
        return f"failed before deleting anything: {problem}"
    if dry_run:
        shutil.rmtree(tmp, ignore_errors=True)
        return f"convertible ({spdx}, {len(pins)} pin(s) all held locally); nothing deleted"

    problem = delete_fork(name)
    if problem:
        shutil.rmtree(tmp, ignore_errors=True)
        return f"failed: {problem}"
    ok, detail = am.ensure_repo(name, owner, repo, upstream)
    if not ok:
        return f"failed after deleting the fork: {detail}; every pin is in {bare}"
    if not am.actions_off(name):
        return f"failed: could not confirm Actions disabled, nothing pushed; every pin is in {bare}"
    problem = push(bare, name, pins)
    if problem:
        return f"failed: {problem}; every pin is in {bare}"
    am.set_default_branch(name, upstream.get("default_branch"))
    missing = am.verify_pins(name, pins)
    if missing:
        return f"failed: pin(s) not readable from the copy: {', '.join(missing)}; every pin is in {bare}"
    shutil.rmtree(tmp, ignore_errors=True)
    af.record({"upstream": key, "fork": f"{ORG}/{name}", "kind": "mirror", "status": "converted",
               "licence": spdx, "pins": sorted(pins), "slugs": slugs,
               "detail": "fork deleted, copy pushed"})
    return f"converted ({spdx}, {len(pins)} pin(s) tagged)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="check and gather, delete nothing")
    ap.add_argument("--only", action="append", required=True, metavar="OWNER/REPO")
    args = ap.parse_args()
    if not shutil.which(am.GIT):
        sys.exit(f"{am.GIT} not found")
    repos = af.corpus_repos()
    failed = 0
    for want in args.only:
        val = repos.get(want.lower())
        if not val:
            print(f"{want:<48} failed: not in the corpus")
            failed += 1
            continue
        outcome = convert(val[0], val[1], args.dry_run)
        print(f"{want:<48} {outcome}")
        if not outcome.startswith(("converted", "convertible", "skipped: already a copy")):
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

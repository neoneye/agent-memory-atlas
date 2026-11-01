#!/usr/bin/env python3
"""Archive a cited repository as a standalone copy, not a fork.

This replaces `archive_fork.py` for every repository added to the archive from
2026-11-01 on. The reason is what a fork does upstream. A fork shares its
parent's network, and GitHub resolves a short reference such as `#969` in a
fork's commit messages to the *parent's* issue 969. Every time
`archive_sync.py` moved a fork's branch forward, each commit message that named
an issue or a squash-merged pull request — `Closes #969`, `(#993)` — put a line
into that upstream issue or pull request's timeline: "neoneye added a commit to
agent-memory-atlas-archive/... that referenced this issue". The Wenlan
maintainer asked what it was on wenlan-app/wenlan#969 after the 2026-10-28 run,
which moved 499 forks. Nothing upstream changed — no CI ran and nothing closed —
but it was noise in other people's trackers, attributed to the atlas.

A repository outside the fork network does not have that link. A short `#969` in
it resolves to its own issue 969, and this script creates the copy with issues
switched off. What it does not neutralise: a commit message that writes a full
reference (`owner/repo#969`) or an issue URL still cross-references from any
repository on GitHub. That is rarer than a short reference and has not been
measured here.

What it does, per repository:

  1. Reads the upstream's licence. A copy outside GitHub's fork mechanism is a
     redistribution, so it needs a licence that grants one. A repository with no
     licence, or one this script does not recognise, is refused and named; the
     fallback is `archive_fork.py --only owner/repo`, a fork taken once and never
     synced (creating a fork writes nothing upstream; moving its branch does).
  2. Creates `agent-memory-atlas-archive/<owner>--<repo>` — the same naming rule
     as the forks, so `archive_name` and `check_archive_names.py` are unchanged —
     with issues, projects and wiki off and the topic `atlas-mirror`.
  3. Switches GitHub Actions off, and reads it back, **before** anything is
     pushed. A pushed `.github/workflows/` with an `on: push` trigger would
     otherwise run the upstream's CI in the archive organisation.
  4. Bare-clones the upstream (no checkout, so nothing in the tree runs) and
     pushes every branch and tag, plus `refs/tags/atlas-pin-<sha>` at each pin a
     report cites. The tag is what keeps a pin that lives only on a pull-request
     ref, or on a branch the upstream later deletes.
  5. Reads each pin back from the copy through the API and fails if one is
     missing.

Re-running on an existing copy adds the pins it lacks and pushes branches
without force: a rejected branch means upstream rewrote history, and the copy
keeps the old commits rather than following. An existing *fork* of the same name
is left alone — it already holds the pins it was forked at — and reported as
such.

Usage:
    python3 scripts/archive_mirror.py --dry-run               # what would be copied
    python3 scripts/archive_mirror.py --only owner/repo       # one repository
    python3 scripts/archive_mirror.py                         # every cited repo with no archive

Exit codes: 0 everything asked for is archived; 1 a repository was refused or
failed for its own reasons (licence, push rejected, pin missing).

Set GITHUB_TOKEN with `repo` scope and admin on the organisation; `gh auth token`
works. The token reaches git through an `http.extraheader`, never through the
remote URL, so it does not land in the copy's config or in a process listing.
"""
from __future__ import annotations

import argparse
import base64
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import archive_fork as af  # noqa: E402  - shared corpus walk, API client, naming

sys.stdout.reconfigure(line_buffering=True)

ORG = af.ORG
API = af.API
GIT = "/usr/bin/git"
TOPIC = "atlas-mirror"
REVISION = re.compile(r"^revision:\s*\"?([0-9a-f]{40})\"?\s*$", re.M)

# GitHub refuses a single push over 2 GB, and the first push of a copy carries
# the whole history. `size` from the repository API is in KB and approximates the
# packed history; above this the push would fail after a long clone, so the copy
# is refused up front. CIRISAI/CIRISAgent (9.2 GB) was the first to hit it.
MAX_HISTORY_KB = 1_800_000

# SPDX ids GitHub reports for licences that grant redistribution. A copyleft
# licence is on the list: the copy carries the LICENSE file and the source, which
# is what those licences ask of a verbatim redistribution.
REDISTRIBUTABLE = {
    "MIT", "MIT-0", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "BSD-3-Clause-Clear",
    "0BSD", "ISC", "Zlib", "BSL-1.0", "Unlicense", "CC0-1.0", "CC-BY-4.0",
    "MPL-2.0", "EPL-1.0", "EPL-2.0", "Artistic-2.0", "UPL-1.0", "PostgreSQL",
    "GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0", "AGPL-3.0", "EUPL-1.2", "OSL-3.0",
    "WTFPL",
}


def pins_by_repo() -> dict[str, set[str]]:
    """{lowercased owner/repo: {pinned shas}} from report frontmatter."""
    out: dict[str, set[str]] = {}
    for path in sorted(af.SYSTEMS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        src = af.SOURCE_URL.search(text)
        rev = REVISION.search(text)
        if not (src and rev):
            continue
        hit = af.REPO_RE.search(src.group(1).strip('"'))
        if hit:
            out.setdefault(f"{hit.group(1)}/{hit.group(2)}".lower(), set()).add(rev.group(1))
    return out


def licence_of(owner: str, repo: str) -> tuple[str, dict | None]:
    status, payload, _ = af.request("GET", f"{API}/repos/{owner}/{repo}")
    if status != 200 or not isinstance(payload, dict):
        return f"http-{status}", None
    spdx = ((payload.get("license") or {}).get("spdx_id") or "NONE")
    return spdx, payload


def git_auth_args() -> list[str]:
    basic = base64.b64encode(f"x-access-token:{af.token()}".encode()).decode()
    return ["-c", "credential.helper=",
            "-c", f"http.https://github.com/.extraheader=AUTHORIZATION: basic {basic}"]


def git(*args: str, cwd: Path | None = None, auth: bool = False) -> subprocess.CompletedProcess:
    cmd = [GIT, *(git_auth_args() if auth else []), *args]
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def ensure_repo(name: str, owner: str, repo: str, upstream: dict) -> tuple[bool, str]:
    """Create the copy, or confirm an existing non-fork one. Returns (ok, detail)."""
    status, existing, _ = af.request("GET", f"{API}/repos/{ORG}/{name}")
    if status == 200 and isinstance(existing, dict):
        if existing.get("fork"):
            return False, "fork-exists"
        return True, "exists"
    if status != 404:
        return False, f"http-{status} reading {ORG}/{name}"
    body = {
        "name": name,
        "description": f"Archive of github.com/{owner}/{repo} for the Agent Memory Atlas "
                       f"(a copy, not a fork, so commit references stay here).",
        "homepage": upstream.get("html_url") or f"https://github.com/{owner}/{repo}",
        "private": False,
        "has_issues": False,
        "has_projects": False,
        "has_wiki": False,
        "has_discussions": False,
    }
    status, payload, _ = af.request("POST", f"{API}/orgs/{ORG}/repos", body)
    if status != 201:
        return False, f"create http-{status} {str((payload or {}).get('message', ''))[:100]}"
    af.request("PUT", f"{API}/repos/{ORG}/{name}/topics", {"names": [TOPIC]})
    return True, "created"


def actions_off(name: str) -> bool:
    af.request("PUT", f"{API}/repos/{ORG}/{name}/actions/permissions", {"enabled": False})
    status, payload, _ = af.request("GET", f"{API}/repos/{ORG}/{name}/actions/permissions")
    return status == 200 and isinstance(payload, dict) and payload.get("enabled") is False


def push_copy(owner: str, repo: str, name: str, pins: set[str], workdir: Path) -> tuple[bool, str]:
    bare = workdir / f"{name}.git"
    r = git("clone", "--bare", "--quiet", f"https://github.com/{owner}/{repo}.git", str(bare))
    if r.returncode != 0:
        return False, f"clone failed: {r.stderr.strip()[-160:]}"
    refspecs = ["refs/heads/*:refs/heads/*", "refs/tags/*:refs/tags/*"]
    for sha in sorted(pins):
        if git("cat-file", "-e", f"{sha}^{{commit}}", cwd=bare).returncode != 0:
            # A pin reachable only from a pull-request ref is not in a bare clone's
            # heads; GitHub serves it by sha.
            git("fetch", "--quiet", "origin", sha, cwd=bare)
        if git("cat-file", "-e", f"{sha}^{{commit}}", cwd=bare).returncode != 0:
            return False, f"pin {sha} not fetchable from upstream"
        refspecs.append(f"{sha}:refs/tags/atlas-pin-{sha}")
    target = f"https://github.com/{ORG}/{name}.git"
    r = git("push", "--quiet", target, *refspecs, cwd=bare, auth=True)
    if r.returncode != 0:
        # Non-fast-forward rejections on an existing copy are the archive keeping
        # history upstream rewrote; push the pin tags alone so they still land.
        if "non-fast-forward" in r.stderr or "rejected" in r.stderr:
            tags = [s for s in refspecs if "atlas-pin-" in s]
            r2 = git("push", "--quiet", target, *tags, cwd=bare, auth=True) if tags else r
            if tags and r2.returncode == 0:
                return True, "pushed pins; some branches kept their archived history"
        return False, f"push failed: {r.stderr.strip()[-200:]}"
    return True, "pushed"


def set_default_branch(name: str, branch: str | None) -> None:
    if branch:
        af.request("PATCH", f"{API}/repos/{ORG}/{name}", {"default_branch": branch})


def verify_pins(name: str, pins: set[str]) -> list[str]:
    missing = []
    for sha in sorted(pins):
        status, _, _ = af.request("GET", f"{API}/repos/{ORG}/{name}/commits/{sha}")
        if status != 200:
            missing.append(sha)
    return missing


def archive_one(key: str, owner: str, repo: str, slugs: list[str], pins: set[str],
                dry_run: bool) -> str:
    name = af.fork_name(owner, repo)
    spdx, upstream = licence_of(owner, repo)
    if upstream is None:
        return f"upstream-unreadable ({spdx})"
    if spdx not in REDISTRIBUTABLE:
        return (f"refused-licence ({spdx}): fall back to `archive_fork.py --only {owner}/{repo}`, "
                f"forked once and never synced")
    size_kb = int(upstream.get("size") or 0)
    if size_kb > MAX_HISTORY_KB:
        return (f"refused-size ({size_kb // 1024} MB of history, over GitHub's 2 GB push limit): "
                f"fall back to `archive_fork.py --only {owner}/{repo}`, forked once and never synced")
    if dry_run:
        status, existing, _ = af.request("GET", f"{API}/repos/{ORG}/{name}")
        if status == 200 and isinstance(existing, dict):
            kind = "fork" if existing.get("fork") else "copy"
            return f"exists as a {kind}; would add missing pins" if kind == "copy" \
                else "fork-exists: would leave alone"
        return f"would-copy ({spdx}, {len(pins)} pin(s))"
    ok, detail = ensure_repo(name, owner, repo, upstream)
    if not ok:
        return "fork-exists: left alone, it holds its fork-time pins" if detail == "fork-exists" \
            else f"failed: {detail}"
    if not actions_off(name):
        return "failed: could not confirm Actions disabled; nothing pushed"
    with tempfile.TemporaryDirectory(prefix="atlas-mirror-") as tmp:
        ok, pushed = push_copy(owner, repo, name, pins, Path(tmp))
    if not ok:
        return f"failed: {pushed}"
    if detail == "created":
        set_default_branch(name, upstream.get("default_branch"))
    missing = verify_pins(name, pins)
    if missing:
        return f"failed: pin(s) not readable from the copy: {', '.join(missing)}"
    af.record({"upstream": key, "fork": f"{ORG}/{name}", "kind": "mirror", "status": "mirrored",
               "licence": spdx, "pins": sorted(pins), "slugs": slugs, "detail": pushed})
    return f"mirrored ({detail}, {pushed})"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="list what would be copied")
    ap.add_argument("--only", action="append", default=[], metavar="OWNER/REPO")
    ap.add_argument("--sleep", type=float, default=5.0)
    args = ap.parse_args()
    if args.dry_run:
        af.READ_ONLY = True
    if not shutil.which(GIT):
        sys.exit(f"{GIT} not found")

    repos = {**af.corpus_repos(), **af.extra_repos()}
    pins = pins_by_repo()
    if args.only:
        wanted = {o.lower() for o in args.only}
        missing = wanted - set(repos)
        if missing:
            sys.exit(f"not in the corpus: {', '.join(sorted(missing))}")
        todo = {k: v for k, v in repos.items() if k in wanted}
    else:
        todo = {}
        for key, val in sorted(repos.items()):
            status, _, _ = af.request("GET", f"{API}/repos/{ORG}/{af.fork_name(val[0], val[1])}")
            if status == 404:
                todo[key] = val
            elif status != 200:
                print(f"could not check {key} (HTTP {status}); skipped", file=sys.stderr)

    failed = 0
    for i, (key, (owner, repo, slugs)) in enumerate(sorted(todo.items()), 1):
        outcome = archive_one(key, owner, repo, slugs, pins.get(key, set()), args.dry_run)
        print(f"[{i}/{len(todo)}] {key:<48} {outcome}")
        if outcome.startswith(("failed", "refused", "upstream-unreadable")):
            failed += 1
        if not args.dry_run:
            time.sleep(args.sleep)
    if not todo:
        print("nothing to archive", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

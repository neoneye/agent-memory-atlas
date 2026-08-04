#!/usr/bin/env python3
"""Drive `screen_repo.py` over the whole corpus, one bounded batch at a time.

Every report in this atlas was produced by cloning a repository onto a personal
machine and often running its build or its tests — all of it before any screen
existed. This walks back over that history and asks, per repository, what the
execution surface actually was at the commit the atlas pinned.

Design constraints, all of them about not occupying the machine:

- **Blobless partial clone, no checkout.** `--filter=blob:none` fetches history
  without file contents, so `git log -- <path>` still bounds lockfile age while
  the download stays small. Blobs arrive only for files the screen reads.
- **One repository on disk at a time.** Each clone is deleted before the next
  begins, so peak disk is one repository rather than 146.
- **Resumable.** Results accumulate in a JSON file; a repository already recorded
  is skipped, so the run can be stopped and restarted at any point.
- **The pinned revision, not HEAD.** The question is what the atlas actually
  cloned and ran, which is the pin. Where the pin is unreachable — force-pushed
  or rebased away — that is itself recorded rather than silently screened at
  something else.

This driver executes nothing from any target. It runs `git` and the screen, both
of which only read.

Usage:
    python3 scripts/screen_corpus.py --batch 5
    python3 scripts/screen_corpus.py --batch 5 --reuse /path/to/existing/clones
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEMS = ROOT / "content" / "systems"
STATE = ROOT / "notes" / "screening" / "screening.json"
SCREEN = ROOT / "scripts" / "screen_repo.py"


def field(text: str, name: str) -> str | None:
    m = re.search(rf"^{name}:\s*(.+)$", text, re.M)
    return m.group(1).strip().strip('"') if m else None


def corpus() -> list[dict]:
    rows = []
    for path in sorted(SYSTEMS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        url, rev = field(text, "source_url"), field(text, "revision")
        if not url or not rev:
            continue
        rows.append({"slug": path.stem, "url": url, "revision": rev})
    return rows


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"screened": {}}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def run(cmd: list[str], timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)


def screen_one(slug: str, url: str, revision: str, reuse: Path | None) -> dict:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    base = {"slug": slug, "url": url, "revision": revision, "screened_at": stamp}

    workdir = None
    checkout: Path
    if reuse and (reuse / slug).is_dir():
        checkout = reuse / slug
        base["source"] = "reused-clone"
    else:
        workdir = Path(tempfile.mkdtemp(prefix=f"screen-{slug}-"))
        checkout = workdir / "repo"
        clone = run(["git", "clone", "--filter=blob:none", "--no-checkout",
                     "--quiet", url, str(checkout)], timeout=900)
        if clone.returncode != 0:
            shutil.rmtree(workdir, ignore_errors=True)
            err = (clone.stderr or "").strip().splitlines()
            return {**base, "status": "clone-failed", "detail": err[-1][:200] if err else "unknown"}
        co = run(["git", "-C", str(checkout), "checkout", "--quiet", revision], timeout=900)
        if co.returncode != 0:
            base["status_note"] = "pinned revision unreachable; screened at default HEAD"
            run(["git", "-C", str(checkout), "checkout", "--quiet", "HEAD"], timeout=900)
        base["source"] = "fresh-clone"

    try:
        proc = run([sys.executable, str(SCREEN), str(checkout), "--json"], timeout=600)
        if proc.returncode == 1 or not proc.stdout.strip():
            return {**base, "status": "screen-failed",
                    "detail": (proc.stderr or "no output").strip()[:200]}
        data = json.loads(proc.stdout)
        findings = data.get("findings", [])
        counts: dict[str, int] = {}
        for f in findings:
            counts[f["kind"]] = counts.get(f["kind"], 0) + 1
        return {
            **base,
            "status": "screened",
            "files_scanned": data.get("files_scanned", 0),
            "counts": counts,
            "findings": [f for f in findings if f["kind"] in ("RUNS", "FRESH", "EXEC")],
        }
    except (json.JSONDecodeError, subprocess.SubprocessError) as exc:
        return {**base, "status": "screen-failed", "detail": str(exc)[:200]}
    finally:
        if workdir is not None:
            shutil.rmtree(workdir, ignore_errors=True)


SUMMARY = ROOT / "notes" / "screening" / "README.md"


def write_summary(state: dict, total: int) -> None:
    rows = state["screened"]
    done = len(rows)
    runs = {k: v for k, v in rows.items() if v.get("counts", {}).get("RUNS")}
    fresh = {k: v for k, v in rows.items() if v.get("counts", {}).get("FRESH")}
    execs = {k: v for k, v in rows.items() if v.get("counts", {}).get("EXEC")}
    failed = {k: v for k, v in rows.items() if v.get("status") != "screened"}
    nothing = {k: v for k, v in rows.items() if v.get("status") == "screened" and not v.get("files_scanned")}

    out = [
        "# Screening the corpus",
        "",
        "Generated by `scripts/screen_corpus.py`; do not hand-edit. Each repository is",
        "screened at **the commit the atlas pins**, which is what was actually cloned and",
        "run, using `scripts/screen_repo.py`.",
        "",
        "A finding is a place execution can happen, not an accusation. Most are ordinary.",
        "The point is that the surface is now written down instead of discovered by",
        "typing `npm install`.",
        "",
        f"**Progress: {done} of {total} screened.**",
        "",
        "| Result | Count |",
        "| --- | ---: |",
        f"| Repositories with an auto-run surface (`RUNS`) | {len(runs)} |",
        f"| Repositories with a dependency surface inside the cooldown (`FRESH`) | {len(fresh)} |",
        f"| Repositories with build-time execution (`EXEC`) | {len(execs)} |",
        f"| Repositories where the screen saw nothing (`NOTHING SCANNED`) | {len(nothing)} |",
        f"| Repositories that could not be screened | {len(failed)} |",
        "",
    ]

    if runs:
        out += ["## Auto-run surfaces", "",
                "These execute without a command being typed. Read before opening the tree.",
                "", "| System | Surfaces |", "| --- | --- |"]
        for slug in sorted(runs):
            paths = [f["path"] for f in runs[slug].get("findings", []) if f["kind"] == "RUNS"]
            out.append(f"| [`{slug}`](../../content/systems/{slug}.md) | {', '.join(f'`{p}`' for p in paths[:8])} |")
        out.append("")

    if failed:
        out += ["## Not screened", "", "| System | Status | Detail |", "| --- | --- | --- |"]
        for slug in sorted(failed):
            r = failed[slug]
            out.append(f"| `{slug}` | {r.get('status')} | {str(r.get('detail', ''))[:120]} |")
        out.append("")

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=5, help="repositories to screen this run")
    ap.add_argument("--reuse", type=Path, default=None,
                    help="directory of existing clones, matched by report slug")
    args = ap.parse_args()

    state = load_state()
    done = state["screened"]
    todo = [r for r in corpus() if r["slug"] not in done]

    if not todo:
        write_summary(state, len(corpus()))
        print(f"screen_corpus: all {len(done)} repositories screened; nothing to do")
        return 0

    batch = todo[: args.batch]
    print(f"screen_corpus: {len(done)} done, {len(todo)} remaining; screening {len(batch)}")
    for row in batch:
        result = screen_one(row["slug"], row["url"], row["revision"], args.reuse)
        done[row["slug"]] = result
        counts = result.get("counts", {})
        summary = " ".join(f"{k}={v}" for k, v in sorted(counts.items())) or result["status"]
        print(f"  {row['slug']:34} {result['status']:14} {summary}")
        save_state(state)

    all_rows = corpus()
    write_summary(state, len(all_rows))
    remaining = len([r for r in all_rows if r["slug"] not in done])
    print(f"screen_corpus: {len(done)} screened, {remaining} remaining")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

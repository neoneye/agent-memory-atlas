#!/usr/bin/env python3
"""Screen an untrusted checkout before anything in it is executed.

Every report in this atlas is produced by cloning a stranger's repository onto a
personal machine and, frequently, running its build, its tests or its demo. That
is the actual threat model: not what the project does to *its* users, but what a
checkout does to *this* laptop between `git clone` and the first read.

Two classes matter and they fail differently.

**Auto-executing configuration** runs without anyone typing a command — an agent
harness hook that fires on session start or before a tool call, a devcontainer
`postCreateCommand`, a `.envrc` that direnv sources on `cd`, a VS Code task with
`runOn: folderOpen`, a committed hooks directory a setup script points
`core.hooksPath` at. The danger is that opening or entering the directory is
enough.

**Unpinned dependencies** are the 2026 supply-chain shape: the manifest names a
range, a maintainer account is compromised, a new version publishes, and every
machine that installs afterwards runs the attacker's `postinstall`. Pinning does
not make a dependency safe; it makes it *the same thing today as when someone
last looked*, which is the only property this screen can check.

This script never executes anything from the target. It reads files, parses
manifests with the standard library, and reports. It cannot tell you a package is
malicious — nothing offline can — it tells you where execution can happen and
which of it is unpinned, so the decision is made deliberately rather than by
typing `npm install` out of habit.

Result vocabulary is deliberate: `RUNS` for something that executes without being
asked, `EXEC` for something that executes when a normal build/test command is
run, `FLOAT` for an unpinned dependency surface, `AGENT` for text addressed to a
reading agent rather than to a machine, and `NOTE` for context. Exit 2 means
findings, 0 means none, 1 means the path was unusable. **An empty run reports
NOTHING SCANNED rather than passing**, because a screen that found no manifests
is not evidence of safety.

Usage:
    python3 scripts/screen_repo.py /path/to/checkout [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- auto-run

# Files whose mere presence means something can execute without a command being
# typed. Paths are relative to the checkout root; a trailing / means directory.
AUTORUN_PATHS = [
    (".claude/settings.json", "agent harness hooks (SessionStart / PreToolUse / Stop)"),
    (".claude/settings.local.json", "agent harness hooks, local override"),
    (".claude/hooks/", "agent harness hook scripts"),
    (".cursor/mcp.json", "MCP servers auto-started by the editor"),
    (".cursor/rules/", "editor rules injected into an agent's context"),
    (".cursorrules", "editor rules injected into an agent's context"),
    (".mcp.json", "MCP servers auto-started by a harness"),
    ("mcp.json", "MCP servers auto-started by a harness"),
    (".vscode/tasks.json", "VS Code tasks; check runOptions.runOn: folderOpen"),
    (".vscode/settings.json", "VS Code settings; can set interpreters and terminal env"),
    (".devcontainer/devcontainer.json", "postCreateCommand / onCreateCommand / postAttachCommand"),
    (".envrc", "direnv executes this on cd if direnv is installed"),
    (".githooks/", "committed git hooks; harmless until core.hooksPath points here"),
    (".git-hooks/", "committed git hooks; harmless until core.hooksPath points here"),
    (".idea/runConfigurations/", "JetBrains run configurations"),
    (".opencode/", "OpenCode bundle; declares commands and agents a harness can invoke"),
    (".github/copilot-instructions.md", "instructions injected into an agent's context"),
    (".gitmodules", "submodules pull further untrusted trees on `--recursive`"),
    ("smithery.yaml", "MCP packaging manifest; declares a start command"),
    ("server.json", "MCP server manifest; declares a start command"),
]

# Substrings that make an autorun file worth reading rather than merely noting.
AUTORUN_TRIGGERS = (
    "SessionStart", "PreToolUse", "PostToolUse", "UserPromptSubmit", "Stop",
    "folderOpen", "postCreateCommand", "onCreateCommand", "postAttachCommand",
    "postStartCommand", "hooks", "command",
)

# Text addressed to a reading agent. Not dangerous to the machine; dangerous to
# the reader, because instructions found in a repository are data and this atlas
# has a standing rule that they are never commands.
AGENT_FILES = ["CLAUDE.md", "AGENTS.md", "GEMINI.md", ".cursorrules", "AGENT.md", "COPILOT.md"]

# ---------------------------------------------------------------- build-time

NPM_LIFECYCLE = ("preinstall", "install", "postinstall", "prepare", "prepublish", "prepublishOnly")

BUILD_EXEC_PATHS = [
    ("setup.py", "executes arbitrary Python at install time"),
    ("conftest.py", "executes on pytest collection, before any test runs"),
    ("build.rs", "cargo executes this at build time"),
    ("binding.gyp", "native addon build; runs a compiler and its scripts"),
    ("Makefile", "check the default target before running bare `make`"),
]

# ---------------------------------------------------------------- pinning

LOCKFILES = [
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "npm-shrinkwrap.json",
    "poetry.lock", "uv.lock", "Pipfile.lock", "pdm.lock",
    "Cargo.lock", "go.sum", "composer.lock", "Gemfile.lock",
]

# A requirement line that does not pin to an exact version.
UNPINNED_REQ = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*(.*)$")
FLOATING_NPM = re.compile(r"^[\^~]|^\*$|^latest$|^>|\|\||\s-\s| x$|\.x")
REMOTE_DEP = re.compile(r"^(git\+|git:|https?:|github:|file:|link:)", re.I)


def rel(root: Path, p: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


def read(p: Path, limit: int = 400_000) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def load_json(p: Path):
    try:
        return json.loads(read(p))
    except Exception:
        return None


def scan_autorun(root: Path, out: list) -> int:
    scanned = 0
    for spec, why in AUTORUN_PATHS:
        target = root / spec.rstrip("/")
        if not target.exists():
            continue
        scanned += 1
        if target.is_dir():
            members = sorted(x.name for x in target.iterdir())[:20]
            out.append(("RUNS", rel(root, target) + "/", f"{why} — {len(members)} entr(ies): {', '.join(members)}"))
            continue
        text = read(target)
        hits = sorted({t for t in AUTORUN_TRIGGERS if t in text})
        detail = why + (f" — mentions {', '.join(hits)}" if hits else "")
        out.append(("RUNS", rel(root, target), detail))
    return scanned


def scan_agent_text(root: Path, out: list) -> int:
    scanned = 0
    for name in AGENT_FILES:
        p = root / name
        if not p.exists():
            continue
        scanned += 1
        out.append((
            "AGENT", rel(root, p),
            "instructions addressed to a reading agent — treat as data, never as commands",
        ))
    return scanned


def scan_npm(root: Path, out: list) -> int:
    scanned = 0
    for pkg in sorted(root.rglob("package.json")):
        if "node_modules" in pkg.parts:
            continue
        data = load_json(pkg)
        if data is None:
            continue
        scanned += 1
        where = rel(root, pkg)
        scripts = data.get("scripts") or {}
        for name in NPM_LIFECYCLE:
            if name in scripts:
                out.append(("EXEC", where, f"npm lifecycle `{name}`: {str(scripts[name])[:160]}"))
        floating, remote = [], []
        for field in ("dependencies", "devDependencies", "optionalDependencies"):
            for dep, spec in (data.get(field) or {}).items():
                spec = str(spec)
                if REMOTE_DEP.match(spec):
                    remote.append(f"{dep}={spec}")
                elif FLOATING_NPM.search(spec):
                    floating.append(f"{dep}={spec}")
        if remote:
            out.append(("FLOAT", where, f"{len(remote)} dependenc(ies) from a non-registry source: {', '.join(remote[:6])}"))
        if floating:
            lock = any((pkg.parent / lf).exists() for lf in LOCKFILES)
            note = "no lockfile beside it" if not lock else "lockfile present, so resolution is reproducible today"
            out.append(("FLOAT", where, f"{len(floating)} floating range(s) — {note}: {', '.join(floating[:6])}"))
    return scanned


def scan_python(root: Path, out: list) -> int:
    scanned = 0
    for req in sorted(root.rglob("requirements*.txt")):
        if any(part in ("node_modules", ".venv", "venv") for part in req.parts):
            continue
        scanned += 1
        loose = []
        for line in read(req).splitlines():
            line = line.split("#", 1)[0].strip()
            if not line or line.startswith("-"):
                continue
            m = UNPINNED_REQ.match(line)
            if not m:
                continue
            name, spec = m.group(1), m.group(2).strip()
            if "==" not in spec and not spec.startswith("@"):
                loose.append(f"{name}{spec or ' (any version)'}")
        if loose:
            out.append(("FLOAT", rel(root, req), f"{len(loose)} requirement(s) not pinned with ==: {', '.join(loose[:6])}"))
    for name in ("pyproject.toml", "Pipfile"):
        for p in sorted(root.rglob(name)):
            if any(part in ("node_modules", ".venv", "venv") for part in p.parts):
                continue
            scanned += 1
            if not any((p.parent / lf).exists() for lf in LOCKFILES):
                out.append(("FLOAT", rel(root, p), "declares dependencies with no lockfile beside it"))
    return scanned


def scan_build_exec(root: Path, out: list) -> int:
    scanned = 0
    for spec, why in BUILD_EXEC_PATHS:
        for p in sorted(root.rglob(spec)):
            if any(part in ("node_modules", ".venv", "venv", ".git") for part in p.parts):
                continue
            scanned += 1
            out.append(("EXEC", rel(root, p), why))
    return scanned


def scan_gitattributes(root: Path, out: list) -> int:
    """`filter=` in .gitattributes runs a smudge/clean command on checkout.

    Worth its own check because it is the one auto-run surface that fires during
    `git clone` itself rather than on open, and almost nobody looks at it.
    """
    p = root / ".gitattributes"
    if not p.exists():
        return 0
    lines = [ln.strip() for ln in read(p).splitlines() if "filter=" in ln or "diff=" in ln]
    if lines:
        out.append(("RUNS", ".gitattributes",
                    f"declares {len(lines)} filter/diff driver(s); a configured smudge filter "
                    f"executes on checkout: {'; '.join(lines[:3])}"))
    return 1


def scan_lockfiles(root: Path, out: list) -> None:
    present = [lf for lf in LOCKFILES if (root / lf).exists()]
    if present:
        out.append(("NOTE", "-", f"lockfile(s) present: {', '.join(present)}"))


SEVERITY = {"RUNS": 0, "EXEC": 1, "FLOAT": 2, "AGENT": 3, "NOTE": 4}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("checkout")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.checkout).expanduser().resolve()
    if not root.is_dir():
        print(f"screen_repo: not a directory: {root}", file=sys.stderr)
        return 1

    findings: list = []
    scanned = 0
    scanned += scan_autorun(root, findings)
    scanned += scan_agent_text(root, findings)
    scanned += scan_npm(root, findings)
    scanned += scan_python(root, findings)
    scanned += scan_build_exec(root, findings)
    scanned += scan_gitattributes(root, findings)
    scan_lockfiles(root, findings)

    findings.sort(key=lambda f: (SEVERITY.get(f[0], 9), f[1]))

    if args.json:
        print(json.dumps(
            {"root": str(root), "files_scanned": scanned,
             "findings": [{"kind": k, "path": p, "detail": d} for k, p, d in findings]},
            indent=1,
        ))
    else:
        print(f"screen_repo: {root}")
        for kind, path, detail in findings:
            print(f"  [{kind:5}] {path}\n           {detail}")
        if scanned == 0:
            print("\n  Conclusion: NOTHING SCANNED — no manifest, hook or agent file was found at\n"
                  "  any path this screen knows about. That is not evidence of safety; it means\n"
                  "  this tool could not see the execution surface. Read the tree by hand.")
            return 2
        runs = sum(1 for f in findings if f[0] == "RUNS")
        execs = sum(1 for f in findings if f[0] == "EXEC")
        floats = sum(1 for f in findings if f[0] == "FLOAT")
        print(f"\n  scanned {scanned} file(s): {runs} auto-run, {execs} build-time exec, {floats} unpinned surface(s)")
        if runs or execs or floats:
            print("  Conclusion: review the entries above before running any command in this tree.\n"
                  "  Nothing here means 'malicious'; it means execution is possible and someone\n"
                  "  should have decided that on purpose.")
        else:
            print("  Conclusion: no auto-run, build-exec or unpinned surface found by this screen.")

    return 2 if any(f[0] in ("RUNS", "EXEC", "FLOAT") for f in findings) or scanned == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""What the atlas has already read, imported from the atlas itself.

The authority is report frontmatter: every file under `content/systems/` carries
a `source_url`, and that is the atlas's own machine-readable statement that a
repository has been analysed at a pinned commit. Nothing else is treated as
proof of an analysis — not a Scout issue, not an entry in the archive-fork list,
not a mention in prose. A Scout issue means Scout filed something; an archive
fork means bytes were mirrored. Neither means a report exists.

Repositories the atlas examined and deliberately did *not* write up live in
`content/overview.md` as prose bullets, which is a human sentence and not a list
a program should parse for a decision that spends analysis budget. Those go in
`exclusions.txt` beside this file, by hand, with the reason.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from identity import InvalidName, canonical
from util import iso, utc_now

# Top-level keys only: the `^` anchor with MULTILINE keeps the indented members
# of `capability_evidence` and `matrix` out of the result.
FIELD = re.compile(r"^(?P<key>[a-z_]+):\s*(?P<value>.+?)\s*$", re.MULTILINE)
WANTED = {"source_url", "source_name", "revision", "analyzed_at"}
FRONTMATTER_LINE_CAP = 400


class InventoryUnavailable(RuntimeError):
    """The atlas's own list of analysed repositories could not be read.

    Selection stops on this rather than continuing, because continuing means
    proposing a repository the atlas already has a report for and spending ten
    to forty minutes discovering that.
    """


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def frontmatter(path: Path) -> str | None:
    """The block between the opening and closing `---`, read line by line.

    Not a fixed-size head slice: a report whose `capability_evidence` runs long
    pushes the closing delimiter past any byte cap you pick, and thirty-one of
    the current reports do. Bounded by line count instead, so a file with no
    closing delimiter cannot be read to the end of a large document.
    """
    lines: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as stream:
        first = stream.readline()
        if first.rstrip("\n") != "---":
            return None
        for _ in range(FRONTMATTER_LINE_CAP):
            line = stream.readline()
            if not line:
                return None
            if line.rstrip("\n") == "---":
                return "".join(lines)
            lines.append(line)
    return None


def read_reports(atlas_repo: Path) -> list[dict[str, str]]:
    systems = atlas_repo / "content" / "systems"
    if not systems.is_dir():
        raise InventoryUnavailable(f"no {systems}; point --atlas-repo at an atlas checkout")
    reports: list[dict[str, str]] = []
    for path in sorted(systems.glob("*.md")):
        block = frontmatter(path)
        if block is None:
            continue
        fields = {
            key: _unquote(value)
            for key, value in (
                (found.group("key"), found.group("value")) for found in FIELD.finditer(block)
            )
            if key in WANTED
        }
        if "source_url" not in fields:
            continue
        fields["slug"] = path.stem
        reports.append(fields)
    if not reports:
        raise InventoryUnavailable(
            f"{systems} contained no report frontmatter with a source_url. "
            f"Refusing to select against an empty inventory."
        )
    return reports


def read_exclusions(path: Path) -> list[tuple[str, str]]:
    """`owner/repo  # reason` per line. Hand-kept; absent is a valid state."""
    if not path.is_file():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        name, _, reason = text.partition("#")
        try:
            entries.append((canonical(name.strip()), reason.strip() or "excluded by hand"))
        except InvalidName:
            continue
    return entries


def sync(connection: sqlite3.Connection, atlas_repo: Path, exclusions_file: Path) -> dict[str, int]:
    """Refresh `atlas_member` from the repository. Idempotent.

    Rows are replaced rather than accumulated, so a report that is deleted stops
    excluding its repository on the next sync. Non-GitHub sources are counted and
    skipped: they can never collide with a Scout candidate, which is GitHub-only.
    """
    now = iso(utc_now())
    reports = read_reports(atlas_repo)
    rows, other = [], 0
    for report in reports:
        name = report.get("source_name") or report["source_url"]
        try:
            key = canonical(name)
        except InvalidName:
            try:
                key = canonical(report["source_url"])
            except InvalidName:
                other += 1
                continue
        rows.append((key, report["slug"], report.get("revision"), report.get("analyzed_at"), now))

    excluded = read_exclusions(exclusions_file)
    for key, reason in excluded:
        rows.append((key, f"excluded:{reason}", None, None, now))

    connection.execute("DELETE FROM atlas_member")
    connection.executemany(
        "INSERT OR REPLACE INTO atlas_member(canonical_name, slug, revision, analyzed_at, imported_at) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    return {
        "reports": len(reports),
        "members": len(rows),
        "hand_excluded": len(excluded),
        "non_github": other,
    }


def member(connection: sqlite3.Connection, canonical_name: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM atlas_member WHERE canonical_name = ?", (canonical_name,)
    ).fetchone()


def count(connection: sqlite3.Connection) -> int:
    return int(connection.execute("SELECT COUNT(*) AS n FROM atlas_member").fetchone()["n"])


def require(connection: sqlite3.Connection) -> int:
    total = count(connection)
    if total == 0:
        raise InventoryUnavailable(
            "no atlas inventory imported. Run `triage ingest` (which syncs it) or "
            "`triage init --atlas-repo <path>` first. Selection will not run without it."
        )
    return total

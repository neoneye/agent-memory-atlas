#!/usr/bin/env python3
"""Check that every screening record still describes the commit its report pins.

`notes/screening/screening.json` records what `screen_repo.py` found in a
repository. The record is only meaningful against one revision: a tree screened
at `abc123` says nothing about `def456`, and a report re-pinned after its
screening carries a record for code nobody looked at.

Three states, and only one of them is a defect:

- **At pin** — the record's revision is the report's current pin. Screened.
- **Absent** — no record. Honest; it is a backlog item, and 143 reports were in
  this state when this check was written. Never fails.
- **Off pin** — a record marked `screened` whose revision is *not* the report's
  pin. This is the one that lies, because the summary counted it as progress and
  the reader has no way to see the difference.

Off-pin records fail only above a ceiling that can only move down. Twenty-one
existed when this shipped, all of them from re-pins that predate keying the
skip-list on the revision; failing the build on a pre-existing backlog is how a
check gets skipped rather than fixed. Screening any of them lowers the ceiling.

Usage: check_screening_ledger.py [root]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

#: Records marked `screened` at a revision the report has since moved off, as of
#: the last time this was lowered. Edited by hand in the same commit that earns
#: it, like `COVERAGE_FLOOR` in `check_capability_evidence.py`, so a reduction is
#: a deliberate act with a diff. It may never rise.
OFF_PIN_CEILING = 19


def pins(root: Path) -> dict[str, str]:
    found = {}
    for path in sorted((root / "content" / "systems").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        block = re.match(r"---\n(.*?)\n---", text, re.S)
        if not block:
            continue
        rev = re.search(r"^revision:\s*[\"']?([0-9a-f]{7,40})", block.group(1), re.M)
        if rev:
            found[path.stem] = rev.group(1)
    return found


def audit(root: Path) -> tuple[list[str], dict[str, list[str]]]:
    ledger_path = root / "notes" / "screening" / "screening.json"
    if not ledger_path.exists():
        return ["no screening ledger at notes/screening/screening.json"], {}
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")).get("screened", {})
    pinned = pins(root)

    at_pin, off_pin, absent = [], [], []
    for slug, rev in sorted(pinned.items()):
        record = ledger.get(slug)
        if not record or record.get("status") != "screened":
            absent.append(slug)
        elif record.get("revision") == rev:
            at_pin.append(slug)
        else:
            off_pin.append(slug)

    # A record for a slug with no report is a leftover, not a certification, but
    # it is also the shape a rename takes. Reported, never fatal.
    orphaned = sorted(set(ledger) - set(pinned))

    problems = []
    if len(off_pin) > OFF_PIN_CEILING:
        problems.append(
            f"{len(off_pin)} screening records describe a revision their report no "
            f"longer pins, above the ceiling of {OFF_PIN_CEILING}. A record is a "
            "claim about one tree; re-screen these or drop them:\n  "
            + "\n  ".join(off_pin[:20])
        )
    return problems, {
        "at_pin": at_pin, "off_pin": off_pin, "absent": absent, "orphaned": orphaned,
    }


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else Path(__file__).resolve().parent.parent
    problems, groups = audit(root)

    total = len(groups.get("at_pin", [])) + len(groups.get("off_pin", [])) + len(groups.get("absent", []))
    print(
        f"{len(groups.get('at_pin', []))} of {total} reports screened at their current pin "
        f"({len(groups.get('off_pin', []))} off pin, ceiling {OFF_PIN_CEILING}; "
        f"{len(groups.get('absent', []))} never screened)."
    )
    if groups.get("orphaned"):
        print(f"  {len(groups['orphaned'])} ledger record(s) have no report: "
              + ", ".join(groups["orphaned"][:10]))
    if "--list" in sys.argv[1:]:
        for slug in groups.get("off_pin", []):
            print(f"  off pin: {slug}")

    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

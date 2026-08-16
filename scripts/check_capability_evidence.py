#!/usr/bin/env python3
"""Validate per-mark evidence records, and report where a system's marks split.

`capabilities:` is a flat list of flags. It says a mechanism was found somewhere
in the repository; it does not say *which memory path* the mechanism protects,
and for a system with more than one durable store those are different claims.
An outside review made the case with DeepCode: its scope filter and its audit
log both guard the conversation store, its negative test guards instruction-file
assembly, and none of the three reaches the Markdown notes the report is largely
about. All three marks are correct. The profile they add up to is not a thing
that exists, and a reader filtering the capability index for two marks at once
can be handed a union no single path in that system has.

`capability_evidence:` is the fix — subsystem, file, symbol, covering test, one
record per mark. This script does three jobs:

  1. **Shape.** Every record names a known flag the report actually carries, and
     fills all four fields. A half-written record is worse than none, because it
     looks migrated.
  2. **Ratchet.** Coverage may not fall. The block arrived after 164 reports
     existed and every record has to come from a real re-read, so this migrates
     report by report instead of by flag day — and a ratchet is what stops
     "incremental" from meaning "abandoned".
  3. **Split subsystems.** Where a report's marks do not all name the same
     subsystem, say so. That is not an error. It is the finding the block was
     added to make visible, and it belongs in the open where the grid is.

**Read the split count carefully: it compares strings, not stores.** A system
whose marks sit on different *layers* of one store — a write gate, a recall
path, a journal, an approval queue, all over the same SQLite file — reports as
split in exactly the same way as DeepCode, whose marks genuinely never reach the
notes the report is about. Perseus Vault made this concrete: seven marks, six
distinct names, one memory path. Naming a layer after the store it belongs to
("entity store — recall and journal listing") is what keeps the signal
meaningful, and the checker cannot enforce it. The number says *look here*, not
*this is wrong*.

Usage:
    check_capability_evidence.py [root] [--list] [--self-test]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_matrix import (  # noqa: E402
    CAPABILITIES,
    EVIDENCE_FIELDS,
    read_capabilities,
    read_capability_evidence,
)

FLAGS = {flag for flag, _, _ in CAPABILITIES}

#: Marks carrying an evidence record, as of the last time this was raised. The
#: number is the whole mechanism: it can only go up, and it is edited by hand in
#: the same commit that earns it, so raising it is a deliberate act with a diff
#: rather than a side effect of a build.
COVERAGE_FLOOR = 60

#: Reports analyzed on or after this date must carry an evidence record for
#: *every* mark they declare. The floor above only stops coverage falling; it
#: says nothing about new marks, so an unbounded number of unsupported ticks
#: could be added forever without the build noticing — 43 of 502 marks carried a
#: record when this was added, and nothing prevented the next 500.
#:
#: A date rather than a flag day. The 459 legacy marks are a real backlog that
#: has to be worked report by report at the pin, and failing the build on them
#: teaches people to skip the check rather than to fill it in. New work has no
#: such excuse: the report is being written at the pin *now*, with the code
#: open, which is the only moment the four fields are cheap to fill.
EVIDENCE_REQUIRED_FROM = "2026-08-16"

#: A test field says what pins the mechanism. These two are the honest answers
#: when nothing does, and they are common — writing one is the point, because
#: "the mechanism is real and no test holds it in place" is a finding this atlas
#: makes constantly in prose and has never been able to count.
NO_TEST = {"none", "unknown"}


def audit(root: Path) -> tuple[list[str], list[str], int, int]:
    """Problems, notes, marks covered, marks total."""
    problems: list[str] = []
    notes: list[str] = []
    covered = total = 0

    for path in sorted((root / "content" / "systems").glob("*.md")):
        where = f"content/systems/{path.name}"
        marks = read_capabilities(path) or set()
        records = read_capability_evidence(path)
        total += len(marks)
        covered += len(marks & set(records))

        analyzed = re.search(
            r"^analyzed_at:\s*[\"']?(\d{4}-\d{2}-\d{2})",
            path.read_text(encoding="utf-8"),
            re.M,
        )
        if analyzed and analyzed.group(1) >= EVIDENCE_REQUIRED_FROM:
            bare = sorted(marks - set(records))
            if bare:
                problems.append(
                    f"{where}: analyzed {analyzed.group(1)}, so every mark needs an "
                    f"evidence record. Missing: {', '.join(bare)}. Write "
                    '"subsystem | file | symbol | test" for each, at the pin — '
                    '"none" or "unknown" is a valid test field and is often the '
                    "finding."
                )

        for flag, record in sorted(records.items()):
            if flag not in FLAGS:
                problems.append(f"{where}: '{flag}' is not one of the seven capabilities")
                continue
            if flag not in marks:
                problems.append(
                    f"{where}: evidence for '{flag}' but the report does not carry that mark"
                )
            missing = [f for f in EVIDENCE_FIELDS if not record.get(f)]
            if missing:
                problems.append(
                    f"{where}: '{flag}' record is missing {', '.join(missing)} — "
                    f"expected \"subsystem | file | symbol | test\""
                )

        subsystems = {
            record["subsystem"] for flag, record in records.items() if record.get("subsystem")
        }
        if len(subsystems) > 1:
            notes.append(
                f"{where}: marks split across {len(subsystems)} subsystems — "
                + "; ".join(sorted(subsystems))
            )
        untested = sorted(
            flag for flag, record in records.items() if record.get("test", "").lower() in NO_TEST
        )
        if untested:
            notes.append(f"{where}: no test recorded for {', '.join(untested)}")

    return problems, notes, covered, total


def check(root: Path, show_list: bool) -> int:
    problems, notes, covered, total = audit(root)

    if show_list:
        print("\n".join(notes) or "no split subsystems and no untested marks recorded")
        print()

    if covered < COVERAGE_FLOOR:
        problems.append(
            f"capability evidence covers {covered} marks; the floor is {COVERAGE_FLOOR}. "
            "Coverage may not fall — restore the records or lower the floor deliberately."
        )

    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1

    split = sum(1 for note in notes if "split across" in note)
    print(
        f"{covered} of {total} capability marks carry an evidence record "
        f"(floor {COVERAGE_FLOOR}); {split} reports have marks that guard different subsystems."
    )
    if covered > COVERAGE_FLOOR:
        print(f"COVERAGE_FLOOR can be raised to {covered}.")
    return 0


FIXTURE = """---
title: "Fixture"
analyzed_at: {analyzed}
capabilities: "{caps}"
capability_evidence:
{records}---

Body.
"""


def self_test() -> int:
    """Controls, because a validator that cannot fail is not a validator.

    The ratchet is deliberately not exercised here — it reads a module constant
    against the real corpus — but every shape rule is, including the one that
    matters most: an evidence record for a mark the report does not carry, which
    is how a migration quietly invents a capability.
    """
    import tempfile

    # An analysis date before the cutoff, so the shape cases exercise only the
    # shape rules. The date rule gets its own three at the end.
    legacy = "2020-01-01"
    cases = [
        ('scope_enforced', '  scope_enforced: "store | a/b.py | q | none"\n', 0,
         "complete record passes", legacy),
        ('scope_enforced', '  scope_enforced: "store | a/b.py | q"\n', 1,
         "missing test field fails", legacy),
        ('scope_enforced', '  audit_log: "store | a/b.py | q | none"\n', 1,
         "evidence for an uncarried mark fails", legacy),
        ('scope_enforced', '  invented: "store | a/b.py | q | none"\n', 1,
         "unknown flag fails", legacy),
        ('scope_enforced', '  scope_enforced: " | a/b.py | q | none"\n', 1,
         "empty subsystem fails", legacy),
        # The date rule. A legacy report may carry a bare mark forever; a report
        # analyzed on or after the cutoff may not.
        ('scope_enforced, audit_log', '  scope_enforced: "store | a/b.py | q | none"\n',
         0, "legacy report may leave a mark bare", legacy),
        ('scope_enforced, audit_log', '  scope_enforced: "store | a/b.py | q | none"\n',
         1, "new report may not leave a mark bare", EVIDENCE_REQUIRED_FROM),
        ('scope_enforced, audit_log',
         '  scope_enforced: "store | a/b.py | q | none"\n'
         '  audit_log: "store | a/c.py | w | none"\n',
         0, "new report with every mark covered passes", EVIDENCE_REQUIRED_FROM),
    ]

    failures = []
    for caps, records, expected, label, analyzed in cases:
        with tempfile.TemporaryDirectory() as tmp:
            systems = Path(tmp) / "content" / "systems"
            systems.mkdir(parents=True)
            (systems / "fixture.md").write_text(
                FIXTURE.format(caps=caps, records=records, analyzed=analyzed),
                encoding="utf-8",
            )
            problems, _, _, _ = audit(Path(tmp))
            if bool(problems) != bool(expected):
                failures.append(f"{label}: expected {expected}, got {problems}")

    for failure in failures:
        print(failure, file=sys.stderr)
    if failures:
        return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main() -> int:
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--self-test" in flags:
        return self_test()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else Path(__file__).resolve().parent.parent
    return check(root, "--list" in flags)


if __name__ == "__main__":
    raise SystemExit(main())

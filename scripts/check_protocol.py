#!/usr/bin/env python3
"""Validate the agent protocol against the pages it cites.

`.agents/protocol/tests.yaml` claims that each test "carries the page it came
from, so a test whose source argument changes goes stale visibly rather than
quietly". That was false when written: nothing parsed the file, nothing checked
that a cited page or section existed, and nothing checked that the ids used in
the templates were real. The claim described a property of a checker that did not
exist — which is the same failure this repository has now recorded three times in
its own prose.

What this validates:

- the catalogue parses, and every entry has the required fields;
- ids are unique, and every id referenced in a template resolves;
- each `source:` names a file that exists and a section that appears in it;
- each `pattern:` is a real pattern slug, or the literal `multiple`;
- no literal commit hash is left in the templates, because a copied hash is a
  false provenance record in someone else's repository.

Deliberately hand-rolled rather than using a YAML library: this repository's
checks run on a stock Python with no site-packages, and `import yaml` fails.
The parser accepts the subset this file is written in and rejects anything else,
which is the right trade for a file that only ever has one author.

Usage:
    check_protocol.py [root] [--self-test]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CATALOGUE = ".agents/protocol/tests.yaml"
TEMPLATES = [".agents/protocol/build-brief.md", ".agents/skills/use-the-atlas/SKILL.md"]
REQUIRED = ("pattern", "source", "proves", "spec", "not_proven")
SPEC_KEYS = ("given", "when", "then")
#: A bare hex run long enough to be a commit. Templates must use a placeholder:
#: an agent that copies `atlas_commit: 4a328bb` into its own repository has
#: written down a provenance claim that was never true.
COMMITISH = re.compile(r"(?<![\w/])[0-9a-f]{7,40}(?![\w/])")


def parse_tests(text: str) -> list[dict]:
    """Entries from the `tests:` list, as {field: raw string} plus `spec`.

    Understands exactly one shape: two-space-indented `- id:` entries, scalar
    fields at four spaces, and a nested `spec:` mapping at six. Block scalars
    (`>`) are recognised by the marker; their bodies are not needed here, only
    their presence, so they collapse to a non-empty placeholder.
    """
    entries: list[dict] = []
    current: dict | None = None
    in_spec = False
    for raw in text.splitlines():
        if raw.strip().startswith("#") or not raw.strip():
            continue
        entry = re.match(r"^  - id:\s*(\S+)\s*$", raw)
        if entry:
            current = {"id": entry.group(1), "spec": {}}
            entries.append(current)
            in_spec = False
            continue
        if current is None:
            continue
        field = re.match(r"^    (\w+):\s*(.*)$", raw)
        if field:
            key, value = field.group(1), field.group(2).strip()
            in_spec = key == "spec"
            if not in_spec:
                current[key] = "block" if value in {">", "|", ">-", "|-"} else value
            else:
                current.setdefault("spec", {})
            continue
        sub = re.match(r"^      (\w+):\s*(.*)$", raw)
        if sub and in_spec:
            value = sub.group(2).strip()
            current["spec"][sub.group(1)] = "block" if value in {">", "|", ">-", "|-"} else value
    return entries


def validate(entries: list[dict], root: Path, referenced: dict[str, list[str]]) -> list[str]:
    problems: list[str] = []
    if not entries:
        problems.append(f"{CATALOGUE}: no test entries parsed")
        return problems

    seen: set[str] = set()
    patterns = {p.stem for p in (root / "content" / "patterns").glob("*.md")}

    for entry in entries:
        tid = entry["id"]
        if tid in seen:
            problems.append(f"{CATALOGUE}: duplicate id {tid}")
        seen.add(tid)

        for field in REQUIRED:
            if not entry.get(field):
                problems.append(f"{CATALOGUE}: {tid} is missing {field}")
        for key in SPEC_KEYS:
            if not entry.get("spec", {}).get(key):
                problems.append(f"{CATALOGUE}: {tid} spec is missing {key}")

        slug = entry.get("pattern", "")
        if slug and slug != "multiple" and slug not in patterns:
            problems.append(f"{CATALOGUE}: {tid} names pattern '{slug}', which has no page")

        source = (entry.get("source") or "").strip('"')
        if source and source != "block":
            problems.extend(check_source(tid, source, root))

    for where, ids in referenced.items():
        for tid in ids:
            if tid not in seen:
                problems.append(f"{where}: references test id '{tid}', which is not in the catalogue")

    return problems


def check_source(tid: str, source: str, root: Path) -> list[str]:
    """The cited file must exist and the cited section must appear in it."""
    path_part, _, section = source.partition("§")
    path = root / path_part.strip()
    if not path.exists():
        return [f"{CATALOGUE}: {tid} cites {path_part.strip()}, which does not exist"]
    if not section.strip():
        return []

    # "§ 6 (ten-step deletion sequence)" — the parenthetical is a hint for a
    # human, not part of the heading.
    wanted = re.sub(r"\(.*?\)", "", section).strip()
    headings = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("#")]
    if re.fullmatch(r"\d+", wanted):
        found = any(re.match(rf"^#+\s*{wanted}[.)]?\s", line) for line in headings)
    else:
        found = any(wanted.lower() in line.lower() for line in headings)
    if not found:
        return [f"{CATALOGUE}: {tid} cites section '{wanted}' of {path_part.strip()}, which has no such heading"]
    return []


def referenced_ids(root: Path) -> dict[str, list[str]]:
    """Test ids used in the templates, which must resolve to real entries."""
    found: dict[str, list[str]] = {}
    known = re.compile(r"\b((?:scope|evidence|gateway|tombstone|deletion|correction|retrieval|prompt)\.[a-z0-9_]+)\b")
    for name in TEMPLATES:
        path = root / name
        if path.exists():
            found[name] = sorted(set(known.findall(path.read_text(encoding="utf-8"))))
    return found


def check_templates(root: Path) -> list[str]:
    problems = []
    for name in TEMPLATES:
        path = root / name
        if not path.exists():
            problems.append(f"{name}: missing")
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "commit" not in line.lower():
                continue
            for match in COMMITISH.finditer(line):
                problems.append(
                    f"{name}:{number}: literal commit '{match.group(0)}' in a template — "
                    "use a placeholder, or an agent copies a provenance claim that was never true"
                )
    return problems


BAD_FIXTURE = """
tests:

  - id: scope.cross_tenant_absent
    pattern: no-such-pattern
    source: "content/patterns/nope.md § Tests to require"
    proves: Something.
    spec:
      given: A thing.
      when: Another thing.
    not_proven: Everything else.

  - id: scope.cross_tenant_absent
    pattern: multiple
    source: "content/overview.md § A heading that does not exist"
    proves: Something.
    spec:
      given: A thing.
      when: Another thing.
      then: A third thing.
    not_proven: Everything else.
"""


def self_test(root: Path) -> int:
    """Controls: the validator must catch each class it claims to catch.

    Written at the same time as the validator, because the last checker added to
    this repository shipped a branch with no fixture and an outside review found
    it before a bug did.
    """
    entries = parse_tests(BAD_FIXTURE)
    problems = " | ".join(validate(entries, root, {"fixture": ["not.a_real_id"]}))
    expected = {
        "duplicate id": "duplicate id",
        "missing spec key": "spec is missing then",
        "unknown pattern slug": "which has no page",
        "missing source file": "does not exist",
        "missing section": "no such heading",
        "unresolved reference": "not in the catalogue",
    }
    failures = [label for label, needle in expected.items() if needle not in problems]
    if len(entries) != 2:
        failures.append(f"parser read {len(entries)} entries, expected 2")
    if failures:
        print("self-test failures: " + ", ".join(failures), file=sys.stderr)
        print(problems, file=sys.stderr)
        return 1
    print(f"self-test: {len(expected)} controls passed")
    return 0


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else Path(__file__).resolve().parent.parent
    if "--self-test" in sys.argv[1:]:
        return self_test(root)

    catalogue = root / CATALOGUE
    if not catalogue.exists():
        print(f"{CATALOGUE}: missing", file=sys.stderr)
        return 1

    entries = parse_tests(catalogue.read_text(encoding="utf-8"))
    problems = validate(entries, root, referenced_ids(root)) + check_templates(root)

    print(f"{len(entries)} protocol tests validated against the pages they cite.")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

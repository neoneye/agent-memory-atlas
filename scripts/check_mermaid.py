#!/usr/bin/env python3
"""Catch mermaid node labels that break the renderer, and pin the renderer.

**This is not diagram validation.** Nothing here parses mermaid. What follows is
a short list of syntax errors that have shipped to the published site at least
once, written as regexes so the same mistake cannot ship twice. A diagram that
fails for any reason not on the list passes this check and renders as a red box
in the reader's browser. Read the count it prints as "no *known* breakage",
never as "the diagrams are valid".

The renderer itself runs in the reader's browser from a CDN, so the version is
part of the contract: `check_pin` asserts the template imports an exact mermaid
version rather than a floating range. It was `mermaid@11` — a range that could
have broken every diagram in the atlas hours after a green build here, with no
commit to point at, and this file's regexes would have reported success while it
happened.

Mermaid parses a node's shape from its delimiters, so a `[` or `]` inside an
unquoted label ends the shape early and the whole diagram fails with
"Syntax error in text" — which only shows on the rendered page, never at build
time. That is how `S[(Summary[]<br/>...)]` shipped to the published RisuAI
report: the markdown was fine, the HTML was fine, and the diagram was a red box.

The fix in every case is to quote the label: `S[("Summary[]")]`. This check
looks for the unquoted form only.

Usage: check_mermaid.py <content-dir>
"""
import re
import sys
from pathlib import Path

# id[...] id[(...)] id{...} id((...)) and subgraph X[...] — capturing an
# unquoted body, then flagging shape delimiters inside it.
LABEL = re.compile(
    r'(?:subgraph\s+)?\w+'
    r'(?:\[\(|\[|\{\{|\{|\(\(|\()'
    r'(?!")([^"\n]*?)'
    r'(?:\)\]|\]|\}\}|\}|\)\)|\))'
)
BREAKERS = "[]{}"


# In a stateDiagram, `A --> B: label` delimits the label with a colon, so a second
# colon inside it ends the parse. `FrameWalOp::Tombstone` shipped this way once and
# only the renderer knew. Node labels are unaffected — this is transitions only.
STATE_EDGE = re.compile(r"^\s*[\w\[\]*]+\s*-->\s*[\w\[\]*]+\s*:(?P<label>.*)$")


#: `mermaid@11.16.1` — exact. Rejects `mermaid@11`, `mermaid@^11.2`,
#: `mermaid@latest` and a bare `mermaid`.
MERMAID_IMPORT = re.compile(r"cdn\.jsdelivr\.net/npm/mermaid@([^/\"']+)/")
EXACT_VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def check_pin(root: Path) -> list[str]:
    """Every mermaid import in a template names an exact version."""
    problems = []
    for path in sorted(root.rglob("*.html")):
        if "docs" in path.parts or "node_modules" in path.parts:
            continue
        for spec in MERMAID_IMPORT.findall(path.read_text(encoding="utf-8")):
            if not EXACT_VERSION.match(spec):
                problems.append(
                    f"{path}: mermaid is imported as '{spec}', which floats. Pin an "
                    "exact version — a CDN release must arrive as a diff, not as "
                    "hundreds of broken diagrams on a build nobody changed."
                )
    return problems


def main(content_dir: str) -> int:
    problems = check_pin(Path(content_dir).resolve().parent)
    for path in sorted(Path(content_dir).rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for block in re.findall(r"```mermaid\n(.*?)```", text, re.S):
            is_state = block.lstrip().startswith("stateDiagram")
            for line in block.split("\n"):
                if is_state:
                    edge = STATE_EDGE.match(line)
                    if edge and ":" in edge.group("label"):
                        problems.append(
                            f"{path}: a second ':' inside a stateDiagram "
                            f"transition label ends the parse\n    {line.strip()}"
                        )
                for body in LABEL.findall(line):
                    bad = sorted({c for c in BREAKERS if c in body})
                    if bad:
                        problems.append(
                            f"{path}: unquoted {''.join(bad)} in a node label\n"
                            f"    {line.strip()}"
                        )
    # Every system report carries a diagram. This started as a convention and
    # drifted: twenty-five reports shipped without one, and nobody noticed until
    # a reader walked the published pages in order and found where the pictures
    # stopped. A convention a build does not check is a convention that decays
    # from the newest end, which is the end a reader arrives at first.
    missing = sorted(
        path.stem
        for path in sorted((Path(content_dir) / "systems").glob("*.md"))
        if "```mermaid" not in path.read_text(encoding="utf-8")
    )
    if missing:
        print(
            f"System reports with no mermaid diagram ({len(missing)}):",
            file=sys.stderr,
        )
        for slug in missing:
            print(f"    {slug}", file=sys.stderr)
        print(
            "Every report gets one. Put it at the end of section 2 (Mental "
            "Model), before '## 3. Architecture', and draw the mechanism the "
            "report is actually about — not a generic box diagram.",
            file=sys.stderr,
        )
        return 1

    if problems:
        print("Mermaid labels that will fail to render:", file=sys.stderr)
        for p in dict.fromkeys(problems):
            print(p, file=sys.stderr)
        print(
            'For a node label, wrap it in quotes: id["a[b]c"] not id[a[b]c].\n'
            "For a stateDiagram transition, remove the second colon — reword, or "
            "move the detail into a note.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "content"))

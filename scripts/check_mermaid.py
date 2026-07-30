#!/usr/bin/env python3
"""Catch mermaid node labels that break the renderer.

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


def main(content_dir: str) -> int:
    problems = []
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

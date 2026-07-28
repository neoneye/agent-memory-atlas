#!/usr/bin/env python3
"""Render a system's capability checklist as HTML for the report hero.

The `capabilities:` frontmatter already drives the generated index in the
comparative report, but that only tells a reader what a system *has*. Arriving
on a single report, the more useful question is what it has **and lacks**
against the same seven definitions — the rubric this atlas judges by. That
belonged at the top rather than halfway down section 5, so the build renders it
under the deck.

Absence of a flag means the mechanism was not found at the pinned commit. The
definitions live in scripts/generate_matrix.py and are imported here so the two
surfaces cannot disagree.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Imported for its side-effect-free definitions; the sys.path line above is what
# makes this resolvable when the script is run by path from the build.
from generate_matrix import (  # type: ignore[attr-defined]  # noqa: E402
    CAPABILITIES,
    read_capabilities,
)

# Short labels; the full definition rides along as a tooltip.
SHORT = {
    "tombstone": "Tombstone",
    "trust_state": "Trust state",
    "bitemporal": "Bi-temporal",
    "scope_enforced": "Scope enforced",
    "audit_log": "Mutation audit",
    "human_review": "Human review",
    "negative_eval": "Negative evals",
}


def render(path: Path) -> str:
    carried = read_capabilities(path)
    if carried is None:
        return ""

    chips = []
    for flag, label, definition in CAPABILITIES:
        present = flag in carried
        chips.append(
            '<li class="cap-chip{cls}" title="{title}">'
            '<span class="cap-mark" aria-hidden="true">{mark}</span>'
            '<span class="cap-name">{name}</span>'
            "</li>".format(
                cls=" is-present" if present else "",
                title=html.escape(f"{label} — {definition}", quote=True),
                mark="✓" if present else "—",
                name=html.escape(SHORT.get(flag) or label),
            )
        )

    count = len(carried)
    total = len(CAPABILITIES)
    return (
        '<div class="capability-strip">'
        '<p class="cap-legend">Atlas rubric '
        f"<b>{count} of {total}</b> "
        "<span>— a dash means the mechanism was not found at this commit</span></p>"
        '<ul class="cap-chips">' + "".join(chips) + "</ul>"
        "</div>"
    )


def main() -> int:
    print(render(Path(sys.argv[1])), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

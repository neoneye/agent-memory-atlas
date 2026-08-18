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

The legend carries the provenance of a mark as well as its meaning, and that is
deliberate. This strip is the most portable thing on the page — seven names and
a tick, quotable without the report around it — so it is the surface most likely
to be read by someone who never reaches the rubric. It said what a *dash* meant
and nothing about what a *tick* rested on; a reader had no way to learn from
here that a mark is one language model's reading of code it did not run, and
that there is no second reader. Both facts live in the rubric's known limits,
and the legend now points at them from beside the marks they qualify.

The legend deliberately does **not** read as a score. These seven are rare by
construction — most systems carry none or one — so a bare "1 of 7" invites a
reader to see a failing grade where the honest reading is "typical, and five of
these columns are outside what this system set out to do". The strip therefore
states the distribution alongside the count, computed from the corpus at build
time so it cannot drift.
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


def _typical_share(systems_dir: Path) -> int | None:
    """Percentage of reports carrying at most one rubric mechanism.

    Computed from the corpus rather than hardcoded, so the legend cannot drift
    away from the thing it claims. Returns None if the directory is unreadable,
    in which case the legend simply omits the clause.
    """
    counts = []
    try:
        for report in sorted(systems_dir.glob("*.md")):
            carried = read_capabilities(report)
            if carried is not None:
                counts.append(len(carried))
    except OSError:
        return None
    if not counts:
        return None
    return round(100 * sum(1 for n in counts if n <= 1) / len(counts))


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
    share = _typical_share(path.parent)
    context = (
        f" Most systems here carry none or one ({share}%),"
        if share is not None
        else " These are rare by construction,"
    )
    return (
        '<div class="capability-strip">'
        '<p class="cap-legend">Carries '
        f"<b>{count}</b> of {total} rubric mechanisms."
        f"<span>{context} and a dash means the mechanism was not found at this "
        "commit — not that the system needed it. Each mark is one LLM "
        "reviewer's reading of the code at this commit rather than a run of it "
        '— <a href="../../methodology/atlas-rubric/#known-limits">known '
        "limits</a>.</span></p>"
        '<ul class="cap-chips">' + "".join(chips) + "</ul>"
        "</div>"
    )


def main() -> int:
    print(render(Path(sys.argv[1])), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

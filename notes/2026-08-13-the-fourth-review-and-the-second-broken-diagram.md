# The fourth review, the second broken diagram, and a triage rule that now has evidence

**Status:** finding, with one rule proposed.
**Origin:** an outside review (Qwen, 2026-08-13) of the
[PRO-LONG](../content/systems/pro-long.md),
[arc-code](../content/systems/arc-code.md) and
[Prime Agent](../content/systems/prime-agent.md) reports.

## The claim, and what it actually was

> **Formatting Failure:** The "Mental Model" section (Section 2) features a table
> that has completely lost its markdown rendering. It looks like a wall of
> disconnected text (`board after each action`, `[PLAN] block`, `None: copy bytes
> from...`). It is entirely unreadable as a data-flow diagram.

All three quoted fragments are edge labels in the Mermaid flowchart at
[`pro-long.md:124-127`](../content/systems/pro-long.md):

```text
ENV[...] -->|"board after each action"| MASTER[...]
AGENT[...] -->|"[PLAN] block"| MASTER
W -->|"None: copy bytes from<br/>offset = size of the copy"| SB[...]
```

There is no table in that section. The same finding was reported against
`build.md` by the previous review and diagnosed in
[the atlas read without JavaScript](2026-08-12-the-atlas-read-without-javascript.md).

Two further items in this review — *"create a dedicated Methodology page and link
it"* and *"create a cross-referenced Patterns section"* — describe pages that
exist and are in the site navigation of every page rendered
(`templates/document.html:57` and `:62`, beside Capabilities, Compare, Verdicts,
Benchmarks and A–Z). Same root cause: anchors stripped along with the script.

## Why this one counts differently

One reviewer reporting a broken visual is a reader with an unusual pipeline. Two
independent reviews, weeks apart, on different pages, both opening with
confident structural criticism that resolves to *the diagram did not render* is a
property of the artifact.

The exposure is the whole corpus: `scripts/check_mermaid.py` requires a diagram
in every system report, so **all 264 report pages** degrade to raw `flowchart TD`
source for a reader who executes no JavaScript. The rule that improved the
reports is the rule that produces the worst experience for a growing share of
the people reading them.

That moves
[the atlas read without JavaScript](2026-08-12-the-atlas-read-without-javascript.md)
from a proposal worth considering to a decision worth making. Its two options
stand: pre-render the SVG at build time with the source kept in a `<details>`,
and give every diagram a one-line text alternative. The second is a content
change, costs no dependency, and would have prevented both reviews from reaching
the wrong conclusion.

## The triage rule

Across four outside reviews, the errors are not randomly distributed. They
cluster in two places, and both are now predictable:

| Where the error lands | Instances |
| --- | --- |
| **The final claim, at the point of maximum asserted evidence** | the invented Gang-of-Four quotation and the five phantom maintainers, recorded in [a third review and the second invented quotation](2026-08-04-a-third-review-and-the-second-invented-quotation.md) |
| **The most confident structural criticism, when it concerns anything rendered** | the `build.md` "floating text artifacts", and this review's "broken table" |

**Proposed rule for handling the next one: check the rendered artifact before
answering any criticism of presentation, and check the corpus before answering
any criticism of coverage.** In this review, four of the seven atlas-wide
proposals were answered by opening one HTML file and one template. That is a
cheaper first move than reasoning about whether the criticism is fair, and it
changes the answer.

The rule cuts the other way too, and this review is the case for it: once the
artifacts were checked, three of the remaining items turned out to be real and
worth acting on — see
[the marks are invisible on the page that earns them](2026-08-13-the-marks-are-invisible-on-the-page-that-earns-them.md),
[actuator as logger](2026-08-13-actuator-as-logger.md), and
[what a friction column could actually say](2026-08-13-what-a-friction-column-could-actually-say.md).
A review whose loudest claims are artifacts is not a review with nothing in it.

## One claim that was simply wrong

> If a harness has no tests, its memory guarantees are theoretical. That should
> be a giant red banner at the top of the page, not a footnote.

PRO-LONG's absent test suite is in section 1, at
[`pro-long.md:74`](../content/systems/pro-long.md) — *"No tests exist in the
tree."* It is not in section 10 and it is not a footnote.

The sub-point survives the correction, though, and is worth taking: it is the
**last** line of the executive summary, sharing a paragraph with a licence note.
For a system whose entire claim is a measurement, "no tests" competes badly for
attention there. Reordering the summary so the evidence posture lands before the
licensing caveat costs one paragraph move per report and no new rule.

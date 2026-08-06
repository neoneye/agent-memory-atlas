# Working in this repository

A code-grounded field guide to agent memory systems: 155 reports, each read at a
pinned commit, plus 21 design patterns extracted from them.

There are two jobs here, and they use different parts of the repo.

---

## Job 1 — You are designing or building memory for some other product

**Do not read the reports.** There are 155 of them and reading widely is how an
agent ends up recommending the most interesting mechanism instead of the smallest
sufficient one. Read five things, in this order.

1. **[`content/patterns/index.md`](content/patterns/index.md), the section
   *How to use the library*.** It is a list of failure modes, each pointing at
   the pattern that closes it. **Start from the failure the product cannot
   tolerate**, not from the mechanism that sounds most rigorous.

2. **The *Stacks, by what you are building* table on the same page.** Five rows —
   single-user tool, multi-tenant, companion/roleplay, autonomous actor, and
   memory that must be correctable and defensible — each naming the failure that
   actually hurts for that shape. Pick the row, then read the *What you can
   defer* paragraph under it, which is the part that keeps the build small.

3. **The pattern pages you selected.** Each carries `Cost to adopt`,
   `Tradeoffs`, `Implementation checklist`, `Tests to require`, and
   `Seen in the atlas`. The last one names the systems worth reading — that is
   your entry point into the corpus, and the only one you need.

4. **[`content/overview.md`](content/overview.md) §8 *What I Would Build* and §10
   *Practical Checklist*.** §8 gives a build order in which each stage works on
   its own; vector search and model-based extraction come last, deliberately.

5. **[`content/benchmarks.md`](content/benchmarks.md) §6 and §7** when you need
   tests: a ten-step deletion sequence with a six-method adapter, and a
   contradiction test with five case shapes. Both are specified in enough detail
   to implement and neither has been run by this project.

Read a system report only when a pattern page cites it for the exact mechanism
you are borrowing.

### Rules for using what you find here

- **The correctable stack is not the default.** Scope → evidence → governed
  gateway → tombstone is the answer for memory that must be correctable and
  defensible. A single-user CRUD memory genuinely does not need a tombstone, and
  the pattern index says so in its own words. Applying the whole stack to
  everything is the failure mode this file exists to prevent.
- **Patterns are not a checklist.** Adopt the smallest set that closes a
  demonstrated failure. Record what you deferred and why — that record is worth
  more later than the code you wrote instead.
- **Every claim here is pinned.** A report describes one commit. "Not found"
  means *not found in the inspected code at that commit* — never "does not
  exist". Do not upgrade an absence into a fact about a project or the field.
- **Never cite stars, downloads or adoption** as evidence about a mechanism.
  This project has a standing rule against it and a note explaining what it cost
  to learn.
- **Counts are generated.** Anything of the form "9 of 155" comes from report
  frontmatter. Do not hand-copy a count into new prose; link to the
  [capability index](content/capabilities.md) instead. If you copy one anyway,
  `scripts/check_claim_counts.py` will catch it when it goes stale.

---

## Job 2 — You are extending the atlas itself

Three skills under `.agents/skills/`, in the order they are normally used:

- **`screen-repository`** — run `python3 scripts/screen_repo.py <path>` before
  reading or running anything from a checkout. Reports auto-executing hooks,
  build-time execution and unpinned dependency surfaces without executing the
  tree.
- **`add-memory-system`** — pins the commit, scaffolds the report, guides the
  review against the seven-mechanism rubric, updates the affected patterns, and
  validates the site.
- **`reanalyze-memory-system`** — re-reads a system at a newer commit and records
  what moved, including claims the atlas published that stopped being true.

Read [`content/methodology/atlas-rubric.md`](content/methodology/atlas-rubric.md)
first: it defines each of the seven marks strictly, and a mark awarded on a
loose reading is worse than no mark.

### House rules that have all been learned the hard way

- **Before writing "nothing does X", grep the whole tree for X** — not the
  directory that ought to contain it. Positive claims fail loudly when wrong;
  negative ones fail silently, and two published ones failed on the same day.
- **A report that does not claim a test run did not do one.** Say in the first
  person what you ran and what passed.
- **Every system report carries a Mermaid diagram of the real mechanism**, and
  the build enforces it.
- **Verify before you claim.** `npm run build && bash scripts/test_site.sh` runs
  the anchor, pin, history, diagram, homepage and count checks. Green is the
  minimum, not the evidence.

---

## Not built yet

Turning the above into a deterministic protocol — a product profile, a reviewable
build brief, pattern-derived acceptance tests and a conformance report — is
proposed and triaged in
[`notes/2026-08-07-the-atlas-as-an-agent-protocol.md`](notes/2026-08-07-the-atlas-as-an-agent-protocol.md),
which also says which parts of it this project has already declined to invent and
why. Read that before proposing it again.

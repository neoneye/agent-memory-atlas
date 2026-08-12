# What a friction column could actually say — measured against the 264 reports

**Status:** proposed, with the compliance gap measured.
**Origin:** an outside review (Qwen, 2026-08-13): *"Every entry needs a
standardized, brutal reality-check table near the top. Memory isn't free."* Four
columns were named — token overhead, latency penalty, setup friction, adoption
portability.

The instinct is right and the atlas has an unusual constraint on acting: it does
not run these systems, so a column it cannot fill honestly becomes 264 cells of
"unknown", which reads as an answer and is not one. This note asks the only
useful question first — **which of the four could be filled from what the reports
already contain?**

## The measurement

Two of the four are already *required* by
[the report format](../content/methodology/per-repo-report-format.md), at lines
170–172:

> Is the write path **synchronous** — does the agent block on an LLM extraction …
> If deferred, what is the lag before a new memory is retrievable? State it even
> [when unmeasured].

Compliance across the corpus, counted at this commit:

| Fact | Reports that say something | Share |
| --- | --- | --- |
| writes blocking / synchronous / asynchronous | 124 of 264 | 47% |
| lag or retrievability after a write | 186 of 264 | 70% |
| a `### Deployment and ergonomics` section | 98 of 264 | 37% |

So the atlas asks for the two facts the reviewer wants a column for, and **under
half the reports state the first one**. That is not a taxonomy problem or a UI
problem. It is a rule that is enforced by nothing: `npm test` fails a report
missing a `capabilities:` key and passes one that never says whether the agent
waits.

## Column by column

**Blocking write — buildable, and the cheapest of the four.** It is a code-level
fact, decidable by reading the write path, with a small closed vocabulary:
`blocking`, `deferred`, `queued`, `none`. 124 reports already contain the
sentence; the rest need a targeted pass, not a re-read.

**Write-to-readable lag — buildable only as a shape, not a number.** Whether the
path is synchronous, batched, cron-driven or human-gated is readable in code.
*How long* is not, and
[the cheapest of the ten metrics](2026-08-12-the-cheapest-of-the-ten-metrics.md)
is the proposal for measuring it on one machine at a time. The column should hold
the shape and link the metric, never a duration the atlas did not observe.

**Setup friction — buildable, with a judgement.** 98 reports carry a deployment
subsection and the material is present in most others, but "friction" is a
comparison, so it needs a vocabulary rather than prose: `library only`,
`local service`, `managed dependency`, `cloud account`. MindCache is `library
only`, [PRO-LONG](../content/systems/pro-long.md) is `local service` — four
Docker images and two API keys — and [arc-code](../content/systems/arc-code.md)
is `cloud account`, because it needs a managed Postgres and a sandbox host.

**Token overhead — not buildable, and it should not be faked.** A handful of
systems state a budget in code and those are quotable — Hermes Agent's 2,200
characters, GenericAgent's thirty-line index, CowAgent's ~30 entries — but a
per-turn cost depends on the corpus, the query and the injection policy, and no
reading produces it. This is the column the reviewer most wants and the one the
atlas has no honest way to fill for more than a dozen systems.

**Portability — the interesting one, and it is already half-recorded.** "How hard
is it to rip this out and use it elsewhere" has a code-level proxy the corpus
already discusses: whether the *output* survives the system's removal. Acontext's
skills are Markdown a ZIP export preserves; a vector store's contents are not.
That is a better question than "does it have a LangChain adapter", and it is the
one this atlas is positioned to answer.

## How to add one without a 264-file rewrite

The precedent exists and worked. `stack_storage`, `stack_retrieval` and
`stack_source` were added as flat frontmatter keys, back-filled by
`scripts/extract_stack.py --seed` from each report's own summary lines, and
labelled: 235 rows are `seeded` — a guess with a label on it — and 29 are
`reviewed`. The seeded count is only allowed to fall, and the build enforces the
vocabulary.

The same mechanism carries a friction column:

```yaml
write_mode: "queued"        # blocking | deferred | queued | none
setup: "local service"      # library | local service | managed dependency | cloud account
friction_source: "seeded"   # seeded | reviewed
```

seeded from the 124 and 98 reports that already say it, `reviewed` when a reader
checked the code, and the matrix generated from the same key the reports carry.
No new page, no re-read of the corpus, and the honesty label travels with the
cell.

## The order I would do it in

1. **Enforce the existing rule before adding a new one.** A check that fails a
   report whose write section never says whether the agent waits would close a
   47% gap with no new vocabulary and no schema change. It is also the change
   most likely to improve the *reports*, which is where the atlas's value is.
2. Then `write_mode` and `setup`, seeded and labelled.
3. Portability as a fourth column only after deciding whether it means "has an
   adapter" or "the memory survives removal" — they are different claims and the
   second is the one worth having.
4. Token overhead: not as a column. As a
   [benchmarks page](../content/benchmarks.md) section listing the systems that
   state a budget in code, which is a real finding about how few do.

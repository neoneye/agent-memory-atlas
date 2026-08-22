# The benchmark everyone cites, and the hint with no verb

**Status:** one re-pin published, one benchmark read at a commit and folded into
the benchmarks page with no report. Both read on 2026-08-22.
**Origin:** two links submitted together — one repository, one benchmark.

---

## LongMemEval — read, and deliberately not given a report

[xiaowu0162/longmemeval](https://github.com/xiaowu0162/longmemeval) at
`9e0b455f4ef0e2ab8f2e582289761153549043fc`, MIT, Di Wu and five co-authors,
ICLR 2025. The atlas cites it eighteen times on the benchmarks page and sixteen
in the comparative report and had never opened it.

**Scope decision: no report.** It is a dataset and an evaluation harness. It
stores nothing across sessions on an agent's behalf, has no read path an agent
calls, and nothing in it could later turn out to have been false about a row it
holds — the boundary the compare page draws. The atlas's own precedent is the
five vector engines: read at a pin, characterised in prose on the page where the
claim lives, no system report. The findings therefore went into
[benchmarks.md](../content/benchmarks.md) under *Read directly, at a pinned
commit*, which went from four benchmarks to five.

What the reading changed, briefly:

- The paper's five abilities are six question types in `evaluate_qa.py`, and
  abstention is not one of them — it is `'_abs' in entry['question_id']`, so an
  abstention item is counted inside its own type *and* in the abstention figure.
- Three headline accuracies exist. `evaluate_qa.py` prints micro;
  `print_qa_metrics.py` prints task-averaged macro, micro, and abstention
  separately. Every "X% on LongMemEval" in the literature picks one silently.
- The grade is `'yes' in eval_response.lower()` over one `gpt-4o-2024-08-06`
  call at `max_tokens: 10`, with no parse-failure path — a refusal scores as a
  wrong answer.
- `print_retrieval_metrics.py` drops every `_abs` item before computing
  anything. The questions where finding nothing is correct are exactly the ones
  the retrieval metrics never see.
- The dataset is not in the repository and nothing records which file was read.
  The September 2025 "cleaned" release changed the haystacks. Pre- and
  post-cleaning scores are not the same benchmark and no artifact says which it
  is.

The last one is the one with teeth for this atlas, because it applies to every
LongMemEval figure the corpus repeats from a README.

## Heimdall — the write path was replaced, and the argument is in the comments

[ArihantDeva/heimdall](https://github.com/ArihantDeva/heimdall) re-pinned from
`f9bc25abd273` to `70ad71d06328`, fifteen commits. The first reading's stated
weakness was that graph freshness depended on a regex parser for the agent's
shell commands. That mechanism is gone; `kb-autosync.ts` now appends a path and
a reconciler reads the file itself.

Worth keeping for the patterns pages: the queue row carries **no verb**. Almost
every sync-a-store-to-the-world design in this corpus ships an event with a type,
and inherits the three failures the repository's own post-mortem lists —
unrecognised writes are invisible, concurrent hooks race, a misparse writes wrong
data confidently. Removing the payload makes all three unrepresentable rather
than handled. Added to
[recoverable background work](../content/patterns/recoverable-background-work.md).

The finding that did not fit anywhere else: **two subsystems in one repository
now delete from the same store and neither reads the other's record.** The
reconciler retracts nodes it owns and journals the outcome; `handle_stale` at
read time deletes nodes it inferred from a note's prose. `audit()` compares the
journal to the filesystem and never to the projection, so a node the read path
removed leaves a `sink_id` in the journal that nothing will ever question. It is
the same shape as the atlas's recurring finding about stores that record what
they admitted and nothing about what they refused, moved one level up: a system
can be rigorous about the half of its state it decided to model.

No capability mark changed. The journal's `absent` row is keyed on a path rather
than a rejected value, it is updated in place rather than appended to, and the
verdicts are still computed per hit and discarded.

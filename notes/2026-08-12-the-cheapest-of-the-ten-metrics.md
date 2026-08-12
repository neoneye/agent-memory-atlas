# The cheapest of the ten metrics — write-to-readable lag, in about forty lines

**Status:** proposed.
**Origin:** an outside review (Qwen, 2026-08-12) of the benchmarks page:
*"Provide a simple Python script or a template on how a developer can actually
measure these."* The scorecard in
[§8](../content/benchmarks.md#8-a-scorecard-worth-publishing) names ten axes and
the page asserts that several are measured nowhere. One of them is measurable in
an afternoon, and the asymmetry between how easy it is and how completely absent
it is makes it the right one to start with.

## Why this axis and not the others

Of the ten, most need a corpus, a judge, or a store big enough for the number to
mean something. Three do not:

| Axis | What it needs | Verdict |
| --- | --- | --- |
| Freshness — write-to-readable lag | a clock and two calls | **start here** |
| Storage — index bytes as a multiple of source bytes | `du` before and after | trivial, but needs a corpus to be interesting |
| Cost (read) — injected memory tokens per turn | a tokenizer and the prompt | easy, but the prompt is often not exposed |

Write-to-readable lag also has the strongest claim to being *absent* rather than
merely unreported. The page has said since it was written that the interval
between a memory being written and being retrievable is measured nowhere, and the
last fortnight kept producing systems where the interval is real and unbounded:
[PLUR1BUS](../content/systems/plur1bus.md) queues embeddings through a JSONL file
drained by a cron, so a memory is lexically retrievable before it is
vector-retrievable and nothing bounds the gap;
[OmniIntelligence](../content/systems/omniintelligence.md)'s path from a session
event to an injectable pattern runs through clustering, a promotion check and an
attribution binder, none of it timed;
[NeuraKeep](../content/systems/neurakeep.md)'s answer is a person, which is the
honest extreme.

## Proposal

A single file, `tools/lag/measure_lag.py`, standard library only, that takes the
same adapter shape the [deletion sequence](../content/benchmarks.md) already
defines — reusing `write`, `prompt_prefix` and `settle` — and reports a
distribution rather than a number.

```python
def measure_lag(memory, *, scope: str, trials: int = 20,
                timeout_s: float = 300, poll_s: float = 0.25) -> dict:
    """Write a unique token, poll until it reaches the prompt, record the delay."""
    samples: list[float] = []
    timeouts = 0
    for i in range(trials):
        token = f"lag-probe-{uuid4().hex}"          # unique: no cache can pre-answer it
        started = perf_counter()
        memory.write(f"The lag probe value is {token}.", scope=scope)
        while True:
            if token in memory.prompt_prefix("what is the lag probe value?", scope=scope):
                samples.append(perf_counter() - started)
                break
            if perf_counter() - started > timeout_s:
                timeouts += 1
                break
            sleep(poll_s)
    return summarize(samples, timeouts=timeouts, trials=trials)
```

**Four design points that are the whole value:**

1. **A unique token per trial.** A fixed probe measures the cache, not the store.
2. **Poll `prompt_prefix`, not the store's own read API.** The question is when
   the memory reaches the model, not when a row lands. A system whose row is
   instantly queryable and whose prompt assembly runs on a schedule has a lag,
   and only this framing catches it.
3. **Report p50, p95, max and a timeout count — never a mean.** These
   distributions are bimodal by construction: a synchronous path returns in
   milliseconds and a batched one returns at the next boundary. A mean over both
   describes neither.
4. **A timeout is a result, not an error.** *"Three of twenty probes never became
   readable within five minutes"* is the most interesting output this can
   produce, and a harness that raises on timeout throws it away.

## What a number from this would and would not prove

It would establish, for one store on one machine, the interval between writing
and being able to use it — the thing every asynchronous-extraction architecture
has and none reports.

It would not establish that the memory is *correct* when it arrives, that it
survives the next background pass, or that a slower system is worse: a store that
takes ninety seconds because it is doing model-based extraction and one that
takes ninety seconds because a cron fires every two minutes have the same number
and different problems. The report has to say which.

And it measures one machine's configuration, not a system. Publishing a
cross-system table from it would repeat the vendor-comparison failure this page
spends [§3](../content/benchmarks.md#3-does-a-bad-score-matter) documenting. The
output is a self-check a builder runs on their own stack, and the atlas's
contribution is the script and the four design points, not a league table.

## Sequencing

Independent of
[the deletion harness](2026-08-12-the-harness-this-page-does-not-ship.md), and
smaller. If the adapter contract is going to exist for the deletion sequence,
this reuses three of its methods and is the cheaper way to find out whether that
contract is workable before the thirteen steps are built on top of it.

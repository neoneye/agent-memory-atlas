# A tested contract for losing the write

**Status:** triage. One repository read on 2026-08-23, no report. Screened
before reading; nothing installed, no container started, no test run.
**Origin:** one link submitted alone.

---

## llmaker — a platform, and a chat buffer called memory

[raiyanyahya/llmaker](https://github.com/raiyanyahya/llmaker) at
`683f7a283bfd2465f97106be769cf5ebd256a663`, Apache-2.0, ~11,000 lines of Go and
5,000 of Python, 46 commits since 24 June 2026. One command provisions Ollama,
Qdrant and Redis as a networked stack; a FastAPI facade and a LangGraph agent
sit on top. The scope call is quick and the reason to write it down is what sits
underneath it.

**Out of scope.** `agent/app/memory.py` is 72 lines: a session's messages as one
JSON list in Redis, capped at 20 turns, expiring after 7 days. No extraction, no
identity, nothing a later reading could contradict — the eviction of turn three
is not a correction, it is a queue. The Qdrant side is loaded by an explicit
`/ingest` from uploaded documents and by `/items` from a catalogue; no chat path
upserts, so nothing learned in a conversation becomes durable. `extract.py`
pulls typed JSON out of one piece of text and stores none of it.

## The part worth keeping

Every Redis call in that module is wrapped in a bare `except Exception` that
returns `[]` or passes. The docstring frames it as availability:

> Every Redis call is best-effort — if Redis is unreachable the agent still
> answers (with whatever the client sent), mirroring how the vector store
> degrades.

Reasonable for a chat buffer. What makes it worth recording is
`tests/test_memory.py::test_memory_degrades_when_redis_errors`, which builds a
client that raises on `get`, `set` and `delete`, and asserts that `load`,
`append` and `clear` all return normally. **The silent loss is a committed
contract**, not an oversight — and two consequences follow that generalise well
past this repository.

A caller cannot distinguish a session whose history was written from one that
was silently dropped. Both return `None`. The only observable is a later answer
that has forgotten something, at which point the cause is unrecoverable.

And the test now protects the behaviour. Anyone who later decides the write
should report its failure has to delete an assertion to do it, which is exactly
the friction that keeps a known-bad default in place.

**The same shape, one report over.** GENOME's `_maybe_auto_detect_facts`
catches every exception from its model call and logs at DEBUG, then catches
every exception from `record_fact` and logs at DEBUG again — so an empty
temporal layer and a working one are indistinguishable from outside. Two
unrelated projects, one written in a week and one with two papers, reached the
same failure surface from opposite directions: swallow, continue, say nothing.

The repair is the same in both and it is small: return what happened. A
`bool` from `append`, a count of what was skipped, a status on the result
object. Degrading is the right call; degrading *silently* is a separate
decision, and it is usually made by accident.

## One idea from the RAG side

`agent/app/eval.py` grades four metrics per case and separates them by how they
are produced: `groundedness`, `relevance` and `correctness` are LLM-as-judge,
while **`context_recall` is deterministic** — the fraction of a case's declared
`expected_sources` that retrieval actually surfaced, computed with no model.
Labelling which numbers a judge produced and which arithmetic did, inside one
result row, is the discipline the
[benchmarks page](../content/benchmarks.md) keeps asking for. The cases are also
traced with their scores attached, so the harness *"doubles as an evaluation
dataset in the same place the live traces land"* — the eval set and the
production telemetry in one store, which is a cheaper version of what several
larger projects build twice.

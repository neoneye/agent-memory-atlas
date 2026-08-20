# A run record and the cost completion hides

**Status:** triage. Two items read on 2026-08-20 — a reproducibility CLI and a
measurement paper — neither of them an agent memory system, one of them
carrying a number this atlas has wanted for a year.
Recorded alongside [Hestia](../content/systems/hestia.md), which was the memory
system in the same batch.
**Origin:** three links submitted together.

---

## RunTrace — `Corvus-226/RunTrace` at [`1c019f0032061213aa4f868d803fc6a1ac5854c0`](https://github.com/Corvus-226/RunTrace/commit/1c019f0032061213aa4f868d803fc6a1ac5854c0)

**Excluded, and it is not a close call.** MIT, ~1,900 lines of Python across
thirteen modules, ~2,600 lines of tests. It is a local-first CLI that writes one
YAML snapshot per machine-learning run into `.runtrace/runs/` at the git root:
commit, branch, detached, dirty, Python version and implementation, platform
tuple, the full installed package map with VCS/archive/directory source
metadata, GPU devices and driver versions, and the command plus a config file
recorded by path, sha256 and parsed values. Six commands — `init`, `run`, `exec`,
`list`, `show`, `diff`.

Nothing in it faces a model. A grep for `mcp`, `llm`, `openai`, `anthropic`,
`embedding` or `agent` across `src/` returns two hits, both of them the regex
name `_FULL_RUN_ID`. There is no tool registry, no retrieval-into-context, no
query surface an agent could call. The record survives the session and has an
identity, and the second half of this atlas's scope test fails outright: it
cannot be corrected. There is no edit path and no delete command — `save()`
raises `SnapshotConflictError` rather than replacing, by design. `AGENTS.md`
states the boundary itself: no server, no database service, no model host, and
*"do not capture environment variables, tokens, credentials, SSH material, or
source-code contents."* Screened clean: four dependency-surface files, no
auto-run, no build-time execution, no unpinned surface; `pyproject.toml` and
`uv.lock` had both changed the same day, so nothing was installed and no command
was run.

It is in this directory because of how the store is written, which is better
than most memory stores in the corpus.

**1. Every refusal test asserts the absence, not just the exception.** This is
the shape the atlas awards `negative_eval` for, applied to something that is not
memory. `test_duplicate_run_id_never_overwrites_existing_snapshot` raises on the
second save *and then* re-loads the record to check the original survived *and*
counts occurrences of the original's name in the file on disk.
`test_failed_atomic_replace_leaves_no_partial_snapshot` monkeypatches
`os.replace` to raise and asserts `list(runs.iterdir()) == []` — the failure
leaves no temp file behind. `test_existing_save_lock_reports_a_conflict` asserts
both that the pre-existing lock still exists and that the snapshot does not.
`test_uninitialized_project_is_rejected_without_creating_files` asserts
`list(project.iterdir()) == []` afterwards. Four refusals, four absence
assertions. The corpus's ninety-three negative-eval suites are mostly about
content that must not be retrieved; this is the same discipline pointed at
partial writes, and it is rarer than it should be in systems that call
themselves durable.

**2. A filename that disagrees with the record it holds is an error, not a
tiebreak.** `_load_path` compares `snapshot.run_id` against the file's stem and
raises *"declares run ID … rename or repair the file"*, with
`test_filename_and_declared_run_id_must_match` renaming a saved file to prove
it. A large number of file-backed memory stores in this atlas key a record by
its path and never check that the body agrees — so a moved, copied or restored
file silently acquires a new identity. This is four lines and it closes that.

**3. The store treats its own directory as untrusted.** `_ensure_within_project`
and a `relative_to` check on every resolved path mean a `.runtrace` symlinked
outside the project raises *"escapes the project root"*, tested; the run-ID regex
`^[0-9a-f]{1,12}$` refuses `../../outside` at the model layer, tested. The write
is `O_CREAT|O_EXCL` lock, `mkstemp` in the destination directory, `fsync`, then
`os.replace`. Compare with [scope as a first-class key](../content/patterns/scope-as-a-first-class-key.md),
whose recurring failure is a scope that is checked at the API and not at the
path.

**4. A schema mismatch on read refuses and says what to do.** `schema_version`
is `Literal[1]`; a record that does not validate raises with the error count and
*"repair or remove it"* rather than being coerced or skipped. Memory stores that
silently drop unparseable records lose data without ever reporting it.

What it does not have is the half this atlas cares about most: no supersession,
no tombstone, no annotation, nothing that can mark a recorded run as wrong. That
is defensible for a reproducibility record — a snapshot of what happened is not
a claim that can become false — and it is exactly why it is not memory.

## What Does Context Compression Cost an Agent? — [arXiv:2608.16370](https://arxiv.org/abs/2608.16370)

**Excluded as a system; integrated into the [benchmarks page](../content/benchmarks.md).**
Shuyu Liu, submitted 17 August 2026, cs.AI. No repository, dataset or harness
URL is named on the abstract page, so none of it is inspectable at a pin and it
gets no report.

Its first sentence is the argument this atlas's §3 makes qualitatively, made
quantitatively: *"Task completion is the standard metric for evaluating context
compression, yet it is incomplete: compression can increase an agent's
interaction cost by forcing it to reacquire dropped state while leaving
completion statistically unchanged."* Retrieval calls rose in all six
model-regime comparisons, five significant. The clean case is GPT-5.5 —
completion 80% → 85% at p = 1.0, retrieval calls 21.0 → 63.9 at p = .002.

Why it is worth the page space: **the counter-example does not depend on judge
variance.** Every other argument on the benchmarks page for distrusting a score
attacks the measurement — weak baseline, easy benchmark, LLM judge disagreeing
with itself. This one leaves the score alone and adds a second number that the
first one hid, and that second number is a hard integer the agent produced
itself. A release note quoting the five-point completion gain would be telling
the truth and describing a system that got three times more expensive.

It has been added to §5 as a metrics-table row and a subsection, on the reading
that compression does not remove the need for state — it converts a prompt-token
cost into a tool-call cost, serial and latency-bearing, which is the same
argument [On LLM usage](../content/benchmarks.md) already makes one level down.

---

## For next time

**"Not memory" and "nothing to learn" keep coming apart in this direction.** The
second time in two days that a batch's most instructive artefact was the one
that got excluded. RunTrace has a better-tested write path than most of the
memory systems in the corpus, and the reason is legible: it has one record type,
one writer, and no correction semantics to get wrong. The systems that fail
these tests are failing them because they are trying to do more, which is worth
remembering before quoting a small project's rigour at a large one.

**The absence assertion travels.** Four refusal tests, four checks that nothing
was written. That is a habit, not a feature, and it costs one line per test. It
is the cheapest thing on this page to copy and the one most consistently missing
from the corpus.

---
title: "vir"
eyebrow: "Most of your session history is your tooling talking to itself"
description: "Three independent detectors decide which transcripts on your disk were sessions you actually drove — of 243 on the author's machine, about 20 were."
root: ../..
page_kind: system
source_name: "djolex999/vir"
source_url: https://github.com/djolex999/vir
revision: 49451ee8edf3747f81df6548411f0439c4378c6c
revision_url: https://github.com/djolex999/vir/commit/49451ee8edf3747f81df6548411f0439c4378c6c
analyzed_at: 2026-08-09
capabilities: "human_review"
stack_storage: "files"
stack_retrieval: "vector"
stack_source: "seeded"
matrix:
  memory_unit: "A typed markdown note — pattern, gotcha, decision or tool — in an Obsidian vault"
  storage: "Plain markdown on disk plus a state database; embeddings in Ollama or a TF-IDF fallback"
  retrieval: "Vector search over one space spanning sessions, clipped articles and PDFs"
  write: "Transcripts filtered, classified with Haiku, distilled with Sonnet, written as notes"
  update_delete: "Dedupe detection and merging; notes are files the user can edit or delete"
  scoping: "One vault; transcripts are categorised by on-disk layout rather than scoped by key"
  integration: "A CLI, a scheduled daemon, an MCP server, and a CLAUDE.md writer with markers"
  background: "A scheduled pass over new transcripts; an embedding sweep"
  trust: "A confidence float per distilled entry, used to pick the top five per category"
  strengths: "Three independent detectors for agent-internal transcripts, with a named trap"
  risks: "Distillation is two LLM passes with no committed evaluation of what survives them"
---

## 1. Executive Summary

vir reads Claude Code transcripts, filters them, and writes typed markdown notes
— patterns, gotchas, decisions, tools — into an Obsidian vault beside your own
notes. "There is no server, no account, no export step. Uninstall vir tomorrow
and the vault stays yours."

**The observation worth the report is in the README's second section:**

> "**243 transcripts, about 20 mine.** Of the 243 transcripts on my machine,
> about 20 were sessions I actually drove. The rest were subagent runs, workflow
> phases, and headless SDK agents. Vir detects all three kinds and skips them by
> default. The vault holds your work, not your tooling's."

Roughly 8%. Every system in this atlas that mines an agent's own transcripts is
ingesting the other 92% unless it does something about it — and the memory that
results is largely the tooling describing its own scaffolding back to itself.

**And the detection is three independent mechanisms, each with its reasoning
written down.**

**Layout.** `classifyTranscript` reads the on-disk shape — a bare
`<session-id>.jsonl` is a session, `<sid>/subagents/agent-*.jsonl` is a
sidechain, `<sid>/subagents/workflows/wf_*/agent-*.jsonl` is a workflow — with
two guards:

> "The `subagents` marker must sit BELOW the encoded project dir — a project
> literally named 'subagents' stays a session. Anything not under projectsDir is
> a session: **never guess**."

**Entrypoint**, with a named trap and two rejected alternatives:

> "The first `type:"user"` line's `entrypoint` starting with 'sdk' marks an
> agent-internal transcript… Keyed on entrypoint ONLY — `promptSource` reads
> 'sdk' even on desktop-launched human sessions (**the C23 serbeval trap**), and
> turn count would kill single-prompt autonomous runs."

**Content**, as an explicit backstop — lines carrying `isSidechain: true` — with
a test file whose describe block names it "sidechain detection (backstop for the
transcript filter)".

Three detectors, a false-positive guard on each, a documented incident, two
alternative signals rejected with the reason, and a fail-safe default that
classifies as *session* when uncertain — because the cost of wrongly skipping
your own work is higher than the cost of ingesting one extra agent run.

**The second contribution is a reason to do any of this at all:**

> "**354 sessions.** Claude Code prunes transcripts after about 30 days. 354 of
> my sessions now exist nowhere except this vault."

## 2. Mental Model

Transcripts on disk are filtered for provenance, scrubbed for secrets, classified
cheaply, distilled expensively, deduplicated, and written as typed notes into a
vault the user owns. A separate command offers the best of them back to
`CLAUDE.md`.

```mermaid
flowchart TD
    T["~/.claude/projects transcripts"] --> CL{"classifyTranscript by layout"}
    CL -->|"<sid>/subagents/…"| SC["sidechain — skipped"]
    CL -->|"…/workflows/wf_*/…"| WF["workflow — skipped"]
    CL -->|"not under projectsDir, or no marker"| SESS["session — never guess"]
    SESS --> EP{"first user line: entrypoint starts with 'sdk'?"}
    EP -->|yes| SKIP2["agent-internal — skipped"]
    EP -->|no| BK{"backstop: any line isSidechain: true?"}
    BK -->|yes| SKIP3["skipped"]
    BK -->|no| SCRUB["scrubber: sk-ant-…, sk-…<br/>negative lookbehind so<br/>'risk-ant-…' survives"]
    SCRUB --> CLS["classify — Haiku"]
    CLS --> DIST["distil — Sonnet"]
    DIST --> DD["dedupe: detector + merger"]
    DD --> W["typed notes: pattern | gotcha | decision | tool"]
    A["web articles, PDFs"] --> DIST
    W --> EMB["one vector space — Ollama, TF-IDF fallback"]
    EMB --> Q["vir query — search and synthesise"]
    EMB --> MCP["MCP server — the agent consults mid-session"]
    W --> SY["vir sync-claude"]
    SY --> DF["diff: added / removed, top 5 per category"]
    DF --> CONF{"user confirms"}
    CONF -->|yes| CM["written between VIR:START and VIR:END<br/>in CLAUDE.md — the rest of the file untouched"]
```

## 3. Architecture

`src/pipeline/` is the engine and it is unusually well factored — `scanner`,
`projects`, `parser`, `filter`, `toolCallFilter`, `scrubber`, `summarizer`,
`distiller`, `articleReader`, `articleDistiller`, `pdfReader`, `pdfDistiller`,
`composer`, `writer`, `relatedLinks`, `periodSummary`, `embeddingSweep`, `lock`,
`slug`, `run`. Nearly every module has a sibling `.test.ts`.

Beside it: `src/dedupe/` (detector and merger), `src/search/`, `src/state/`,
`src/mcp/`, `src/daemon/`, `src/cost/`, `src/lint/`, `src/diagnostics/`,
`src/claude/updater.ts`, `src/ui/`.

A `cost/` module for a two-model pipeline (Haiku to classify, Sonnet to distil)
is the right instinct: the cheap model triages, the expensive one only sees what
survived, and the bill is tracked.

46 test files, including four named for specific `run` behaviours —
`run.preflightProbe`, `run.projectFilter`, `run.retryBound`,
`run.rewriteDryRun`, `run.transcriptFilter`.

## 4. Essential Implementation Paths

**Categorise** — `src/pipeline/projects.ts` (the layout comment `:78-86`,
`classifyTranscript` `:88-103`, the SDK-entrypoint rule and the C23 trap
`:105-`).

**Backstop** — `src/pipeline/parser.ts`, `src/pipeline/parser.test.ts`
(`:123-150`).

**Scrub** — `src/pipeline/scrubber.ts` (the lookbehind rationale `:6-17`).

**Distil** — `src/pipeline/summarizer.ts`, `distiller.ts`, `composer.ts`,
`writer.ts`.

**Offer back** — `src/claude/updater.ts` (`VIR_START` / `VIR_END` `:8-9`,
`TOP_N_PER_CATEGORY` `:10`, `DiffResult` `:20-`).

## 5. Memory Data Model

A note is a markdown file with a category (`pattern`, `gotcha`, `decision`,
`tool`), a topic, a slug, a `confidence` float and a `startedAt`. The vault is
the store; a state database tracks what has been processed.

There is no status field, no supersession pointer and no tombstone. Correction is
editing or deleting a file, and the dedupe module merges rather than supersedes.
`confidence` is used for selection — the top five per category are what
`sync-claude` offers — not for withholding.

## 6. Retrieval Mechanics

One vector space over sessions, clipped web articles and PDFs, with Ollama
embeddings and a TF-IDF fallback so the system works with no model server. `vir
query` searches and synthesises; an MCP server exposes the same vault to Claude
Code mid-session "so the agent consults past decisions instead of rediscovering
them".

Scope is the vault. Transcript *categorisation* is not scoping — it decides what
enters the store, not who may read it — so `scope_enforced` is not earned.

## 7. Write Mechanics

Filter, scrub, classify, distil, dedupe, write.

**The scrubber is designed against its own false positives**, with the
counterexamples in the comments: the Anthropic-key pattern carries a negative
lookbehind because "a real key is preceded by whitespace/quote/=/start, never by
`[A-Za-z0-9-]`" so `"risk-ant-…"` is not redacted, and the OpenAI pattern has the
same guard so `"risk-management-strategy-2026-plan"` survives. A redaction rule
that names the innocent string it must not eat is a rule someone tested against
real notes.

**`sync-claude` writes into a file it does not own, correctly.** vir's content
goes between `<!-- VIR:START -->` and `<!-- VIR:END -->`, only the top five per
category, and only after showing a diff of what would be added and removed and
getting confirmation. Everything outside the markers is untouched.

## 8. Agent Integration

`npm install -g @djolex999/vir-cli`, `vir init` (a wizard for provider, models
and vault path), `vir run` for one pass, `vir schedule install` for a daemon.
Plus `vir query`, `vir sync-claude`, an MCP server, and lint and diagnostics
subcommands.

The retroactive framing is the selling point and it is honest about its window:
existing history becomes notes in one run, and the transcripts it reads are the
ones not yet pruned.

## 9. Reliability, Safety, and Trust

**One mark: human review.** `sync-claude` is a genuine adjudication surface — the
distilled notes do not enter the agent's standing instructions until a person
sees a diff of the additions and removals and confirms. Combined with the marker
delimiters, it is the most careful implementation in this atlas of writing into a
file the user owns.

**Trust state, tombstone, bitemporal, audit log, scope, negative eval — no.**
`confidence` selects rather than withholds.

**The transcript filter is the safety mechanism**, and its default direction is
right: anything not clearly agent-internal is treated as a session, because a
missed sidechain costs one noisy note and a wrongly-skipped session costs work
that may exist nowhere else.

**The unaddressed risk is what distillation does.** Two LLM passes stand between
a transcript and a note, and nothing committed measures whether the note is
faithful to the session. A gotcha the model paraphrases into a general rule, or a
decision it records without its rationale, becomes a permanent vault entry that
outlives the transcript it came from — which is precisely the situation the
project exists to create.

## 10. Tests, Evals, and Benchmarks

**No paper, no benchmark, no committed results.** 46 test files, nearly one per
pipeline module, and the ones named for `run` behaviours are the interesting set:
`run.preflightProbe`, `run.projectFilter`, `run.retryBound`,
`run.rewriteDryRun`, `run.transcriptFilter`.

`run.rewriteDryRun` and `run.retryBound` are the two most systems lack — a dry
run for a destructive rewrite, and a bounded retry, each with a test named after
it.

The parser test describes itself as a "backstop for the transcript filter",
which is the right way to label a defence-in-depth check: it says what the test
is *for* relative to the other mechanism, so a reader knows removing one leaves
the other.

Nothing evaluates distillation quality, which is the pipeline's central
transformation.

**I ran nothing.**

## 11. For Your Own Build

### Steal

- **Work out how much of your transcript history is actually the user's.** If
  you mine an agent's own logs, subagent runs, workflow phases and headless SDK
  sessions are in there, and on one real machine they were 92% of the files.
  Ingesting them fills memory with your tooling describing itself.
- **Detect provenance three ways and let them back each other up.** Directory
  layout, a launch-signature field, and a per-line flag as a backstop — with the
  test that covers the backstop saying so in its name.
- **Guard each detector against its obvious false positive.** "A project
  literally named `subagents` stays a session." "Anything not under projectsDir
  is a session: never guess."
- **Write down the signals you rejected and why.** `promptSource` reads "sdk"
  even for desktop-launched human sessions; turn count would kill single-prompt
  autonomous runs. Both are the signals a reader would reach for first.
- **Default to keeping when uncertain**, when the asymmetry runs that way: a
  missed skip costs a noisy note, a missed session costs work that exists
  nowhere else.
- **Put the innocent string in the redaction comment.** `"risk-ant-…"` must not
  redact, `"risk-management-strategy-2026-plan"` must survive — a negative
  lookbehind with its counterexample named.
- **Delimit your content in a file you do not own.** `VIR:START` / `VIR:END`, a
  diff of additions *and* removals, and confirmation before writing.
- **Triage with the cheap model and distil with the expensive one**, and track
  the cost of both.
- **Name a test after the behaviour it protects.** `run.rewriteDryRun`,
  `run.retryBound`, `run.transcriptFilter`.
- **Ship a fallback embedder.** TF-IDF when Ollama is absent means the tool works
  before the user has set anything up.

### Avoid

- **Do not leave the distillation unmeasured.** Two LLM passes produce every note
  in the vault, and the vault outlives the transcripts, so an unfaithful
  distillation is permanent and unfalsifiable once the source is pruned.
- **Do not let `confidence` only select.** It picks the top five for
  `sync-claude` and does nothing at query time, so a low-confidence note is
  retrieved like any other.

### Fit

The right choice if you use Claude Code daily, keep an Obsidian vault, and want
the last month of sessions to survive their pruning window as searchable notes.
The retroactive first run is the moment of value and the daemon keeps it current.

Read `src/pipeline/projects.ts` even if you build something else. Deciding which
of your own logs are actually yours is a problem every transcript-mining memory
system has, and this is the only careful treatment of it in the atlas.

## 12. Open Questions

- **How faithful are the distilled notes?** No evaluation is committed.
- **What was the C23 serbeval trap?** Named in a comment as the reason for
  keying on `entrypoint` alone; the incident is not written up.
- **Does `confidence` reach the query path?** It selects for `sync-claude`; no
  retrieval use was found.
- **What happens to a note whose source transcript is later pruned?** The note
  outlives it by design; nothing records that the source is gone.

## Appendix: File Index

**Provenance** — `src/pipeline/projects.ts` (the on-disk shapes and the
never-guess rule `:78-86`, `classifyTranscript` `:88-103`, the SDK-entrypoint
signature and the C23 trap `:105-`), `src/pipeline/parser.ts`,
`src/pipeline/parser.test.ts` (the backstop describe block `:123-150`),
`src/pipeline/filter.ts`, `src/pipeline/toolCallFilter.ts`

**Redaction** — `src/pipeline/scrubber.ts` (the Anthropic-key lookbehind and its
counterexample `:6-13`, the OpenAI pattern `:14-17`), `scrubber.test.ts`

**Distillation** — `src/pipeline/summarizer.ts`, `distiller.ts`,
`articleDistiller.ts`, `pdfDistiller.ts`, `composer.ts`, `writer.ts`,
`relatedLinks.ts`, `periodSummary.ts`, `src/dedupe/{detector,merger}.ts`

**Instruction sync** — `src/claude/updater.ts` (`VIR_START`/`VIR_END` `:8-9`,
`TOP_N_PER_CATEGORY` `:10`, `Entry` `:12-18`, `DiffResult` `:20-`)

**Run behaviours** — `src/pipeline/run.ts`, `run.preflightProbe.test.ts`,
`run.projectFilter.test.ts`, `run.retryBound.test.ts`,
`run.rewriteDryRun.test.ts`, `run.transcriptFilter.test.ts`,
`src/pipeline/lock.ts`

**Surfaces** — `src/cli.ts`, `src/mcp/`, `src/daemon/`, `src/cost/`,
`src/search/`, `src/state/`, `src/lint/`, `src/diagnostics/`

## History

**2026-08-09** — [`49451ee8edf3747f81df6548411f0439c4378c6c`](https://github.com/djolex999/vir/commit/49451ee8edf3747f81df6548411f0439c4378c6c) — first reading. Screened before reading; the tree was read, never installed, and no pass was run. The 243-and-20 figures are the author's, reported from one machine.

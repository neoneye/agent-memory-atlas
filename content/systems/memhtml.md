---
title: "memhtml"
eyebrow: "An empty result tells you whether the address never existed or was archived"
description: "A git repository of semantic HTML files, one fact each, with a rebuildable SQLite index, four ranking arms sharing one scope filter, and a seventeen-phase curation pass that commits to a branch only a person may merge."
root: ../..
page_kind: system
source_name: "memhtml/memhtml"
source_url: https://github.com/memhtml/memhtml
archive_name: "memhtml--memhtml"
revision: 4778735a5016ecaabd725df594729848334e9968
revision_url: https://github.com/memhtml/memhtml/commit/4778735a5016ecaabd725df594729848334e9968
analyzed_at: 2026-09-16
capabilities: "trust_state, bitemporal, human_review, negative_eval"
capability_evidence:
  human_review: "three actors, and only one of them may settle a contradiction | README.md:122, :126, :178, :268, :272 | the division of labour is stated as a rule rather than a habit: \"Three actors share one tree. The agent writes facts, and it resolves only the conflicts it found itself. Sleep curates on a branch when a caller fires it, and it detects conflicts without resolving them. The human owns the gate and every one-way door.\" A curation run is a branch — `memhtml sleep run` puts its commits on `sleep/<date>` and leaves `main` untouched — and each phase \"commits each one's work on its own, so a human reads the curation one phase-shaped diff at a time\". `trace-consolidation` \"lands each distilled memory as its own commit, one per memory, so a reviewer reads one claim at a time\". The phases that decline to decide open tasks instead, each citing its evidence verbatim and capped at ten a night, because \"[a] detection is a proposal for a human, never a fact the corpus asserts\". `memhtml sleep merge` then \"fast-forwards `main` only after a quality gate that can refuse\" | the merge gate re-runs the retrieval evaluation, \"so a sleep run that degrades retrieval cannot land\", and reports `skipped: true` when it cannot reach the model \"so a skipped gate reads as skipped rather than as green\""
  negative_eval: "the merge veto read backwards into adversarial controls, gating retrieval on ranking a claim above its own plausible impostor | packages/eval/src/controls.ts:1-20, packages/eval/src/discriminate.ts:8-12 | \"[t]he discrimination gate asks one question: can the retrieval stack rank a memory above its own high-similarity WRONG twin?\" The controls are generated from the three divergence predicates that already forbid folding two memories together — negation, numeric token, variant qualifier — \"as pure text transforms that turn a true claim into a high-similarity WRONG one\", on the reasoning that \"[t]he three predicates that forbid folding two memories together are the three ways to build a plausible impostor, and a control the veto cannot see does not test anything.\" Each control is checked against its own family's predicate rather than the disjunction, so a control that only trips a different rule is not counted. The gate runs in `pnpm check`, in CI, and again inside `memhtml sleep merge` | a fake-embedder mode makes the suite deterministic and credential-free, so the gate is runnable by anyone who clones the repository"
  trust_state: "archived as a stored state the default scope excludes, with the replacement reachable from the row it replaced | packages/index/src/retrieval.ts:88-99, :140-160, packages/store/src/store.ts:253, :266, :1110 | a correction writes `memhtml-superseded-by` on the loser pointing at its winner and a `supersedes` edge on the winner, in one commit, and eviction or compression is \"a `git mv` into `archive/`\". \"[T]he default scope excludes archived rows\", so a superseded memory leaves the live view without leaving the corpus, and reaches a result set again only through `includeArchived` or the point-in-time lens. `supersededBy` is then present-and-nullable on every hit, derived from the `edges` table rather than the head meta \"so a caller can tell 'not superseded' from 'this build does not report supersession'\". The honesty extends to the empty result: when a scope matches nothing, `archivedMatches` counts how many archived rows the same scope matches, so an agent \"can tell 'never existed' from 'archived'\" and can follow `archived[].supersededBy` to what replaced it | the flag is computed only when the scope came back empty, and is zero under `asOf`, \"whose lens already admits archived rows, so the flag is not what emptied that search\""
  bitemporal: "a validity interval read separately from creation time, with the fallback chain written into the SQL | packages/index/src/scope.ts:195-200, :255, packages/index/src/retrieval.ts:88-93 | the point-in-time predicate is `coalesce(valid_from, event_at, created_at) <= asOf AND (valid_until IS NULL OR valid_until > asOf)`: `valid_from` and `valid_until` are the memory's own statement about when its claim held, `created_at` is when the file was written, and the coalesce chain is what a store does when a fact declares no validity of its own. Under the lens an archived hit comes back carrying the path of what replaced it, \"so a point-in-time answer reads as history. The hit was believed then, and THIS is what replaced it.\" The limit is in the coalesce: a memory that declares neither `valid_from` nor `event_at` is treated as valid from the moment it was written, so for undeclared facts the two axes coincide — a conservative default, and one a reader should know before trusting a historical answer | the same lens is applied through the single scope filter every retrieval arm receives, so the temporal predicate cannot hold on three arms and miss the fourth"
stack_storage: "files, sqlite"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "One semantic HTML5 file per fact in a git repository, carrying a title, type, claim, entities, validity, confidence and supersession meta, addressed by its path"
  storage: "A git repository of HTML under `MEMHTML_ROOT` in PARA directories, with a rebuildable SQLite index and a merge driver installed at init"
  retrieval: "Four arms — FTS, vector, recency, salience — fused with reciprocal rank, all receiving one scope filter string built once"
  write: "A CLI `write`, an MCP server with fifteen tools, and hooks that recall and index but never write, because distilling a transcript into a durable fact belongs to the sleep run"
  update_delete: "A correction writes `memhtml-superseded-by` on the loser and a `supersedes` edge on the winner in one commit; eviction and compression are a `git mv` into `archive/`"
  scoping: "Facet, type, path and date axes assembled into one filter every arm receives, with archived rows excluded by default"
  integration: "Two binaries, an MCP server over stdio, and installers for Claude Code, Codex, Cursor and OpenCode that record a SHA-256 receipt of every file and fragment they own"
  background: "A seventeen-phase sleep run — dedup, entity resolution, edge typing, confidence decay, arc synthesis, retention triage, compression, task detection, integrity — each committing phase making its own isolated commit with a machine-readable trailer"
  trust: "Supersession links both ways, an archived state excluded by default, tasks that propose rather than assert, and a merge gate that re-runs the retrieval evaluation"
  strengths: "The division of labour is the design, and it is written as a rule: \"The agent writes facts, and it resolves only the conflicts it found itself. Sleep curates on a branch when a caller fires it, and it detects conflicts without resolving them. The human owns the gate and every one-way door.\" Everything follows from that — curation arrives as phase-shaped diffs on a branch, distilled memories land one commit per claim \"so a reviewer reads one claim at a time\", the phases that decline to decide open a task quoting its evidence instead, and the merge fast-forwards only after a gate that re-runs the retrieval evaluation. Two smaller pieces are worth stealing on their own. The scope filter \"is built ONCE and every arm receives the same string\", because \"[p]er-arm filters would let a scope apply to three arms and not the fourth, which surfaces as a scoped query returning a result from outside the scope. No type catches that leak\" — with an explicit rule that anything narrowing one arm's candidates belongs in that arm and \"must never enter this filter\". And `archivedMatches` turns an empty result into an answer: when a scope matches nothing, the count of archived rows the same scope matches lets an agent \"tell 'never existed' from 'archived'\" and follow the supersession link to the replacement"
  risks: "The mutation record is git, which this atlas does not count as an audit of memory mutations: the phase trailers, the one-commit-per-claim discipline and the receipts are real and they live in a history a force-push rewrites, with no separate append-only table in the store. Scope is a caller-supplied facet set rather than a stored key applied on the caller's behalf — the single-filter design closes the arm-drift leak thoroughly, and it still narrows only what the caller asked to narrow, so nothing separates one project's memories from another's unless the query says so. The bitemporal fallback deserves a reader's attention: `coalesce(valid_from, event_at, created_at)` means a memory that declares no validity is treated as valid from the moment it was written, so a historical query over a corpus where nobody filled those fields answers from write time while looking like it answered from world time. And the operational surface is large for a personal memory — 132,835 lines of TypeScript over 393 files, a seventeen-phase nightly pass, Bedrock for embeddings and model calls unless both are switched off, and installers that write into four hosts' configuration files"
---

## 1. Executive Summary

memhtml "stores an agent's long-term memory as a git repository of semantic
HTML5 files, one fact per file. A rebuildable SQLite index sits over that tree,
retrieval fuses four ranking arms, and a seventeen-phase curation pipeline
commits its work to a branch a human reviews before it lands." Apache-2.0,
TypeScript, 132,835 lines across 393 files, two binaries and an MCP server.

**The design is a division of labour, stated as a rule.**

> "Three actors share one tree. The agent writes facts, and it resolves only the
> conflicts it found itself. Sleep curates on a branch when a caller fires it,
> and it detects conflicts without resolving them. The human owns the gate and
> every one-way door."

Everything else follows. The nightly pass puts its commits on `sleep/<date>` and
leaves `main` untouched. Each phase commits separately "so a human reads the
curation one phase-shaped diff at a time", and `trace-consolidation` lands "each
distilled memory as its own commit, one per memory, so a reviewer reads one
claim at a time." The phases that could decide and choose not to open a task
instead, quoting the sentence they found, because "[a] detection is a proposal
for a human, never a fact the corpus asserts." `memhtml sleep merge`
fast-forwards `main` "only after a quality gate that can refuse", and that gate
re-runs the retrieval evaluation "so a sleep run that degrades retrieval cannot
land."

**The evaluation behind that gate is the second thing to take.** Its controls
are the system's own merge veto read backwards:

> "The three predicates that forbid folding two memories together are the three
> ways to build a plausible impostor, and a control the veto cannot see does not
> test anything."

Negation, numeric token and variant qualifier become text transforms "that turn
a true claim into a high-similarity WRONG one", and the discrimination gate asks
"can the retrieval stack rank a memory above its own high-similarity WRONG
twin?" Each control is validated against its own family's predicate rather than
the disjunction, so one that trips a different rule does not count.

**A third piece answers a question most stores leave hanging: what an empty
result means.** When a scope matches nothing, `archivedMatches` reports how many
archived rows the same scope matches, so an agent can "tell 'never existed' from
'archived'" and follow `archived[].supersededBy` to the replacement. A corrected
memory leaves the default view — "the default scope excludes archived rows" —
without leaving the corpus.

**And the scope filter is built once for all four arms**, with the reason given:
"[p]er-arm filters would let a scope apply to three arms and not the fourth,
which surfaces as a scoped query returning a result from outside the scope. No
type catches that leak."

The gap is that the mutation record is git. The phase trailers and the
one-commit-per-claim discipline are real, and they live in a history a rewrite
can change, with no append-only table in the store beside them.

## 2. Mental Model

A **memory** is one HTML file in a git tree, and the index is rebuildable.

A **correction** archives the loser and links it to its winner, both ways.

A **curation run** is a branch of phase-shaped diffs.

A **task** is what the machine opens when it declines to decide.

An **empty result** says whether the address never existed or was archived.

```mermaid
%% caption: the agent writes to main, the sleep run curates on a branch it may not merge, a person owns the gate, and the merge is refused by an evaluation whose adversarial controls are generated from the system's own anti-merge predicates
flowchart TB
    AGENT["the agent — writes facts to main at any hour,<br/>one fact per file, and resolves only<br/>the conflicts it found itself"] --> MAIN[("main: a git tree of semantic HTML5,<br/>one fact per file, PARA directories")]
    HOOK["session hooks: recall and trace indexing<br/>under a hard time bound"] -.->|"NO hook writes a memory —<br/>any failure prints nothing and exits 0,<br/>so a hook can never block a turn"| MAIN
    MAIN --> IDX[("rebuildable SQLite index:<br/>files · chunks · edges · vectors")]
    IDX --> ARMS["four arms: FTS · vector · recency · salience,<br/>fused with reciprocal rank"]
    SCOPE["one scope filter string, built ONCE"] --> ARMS
    SCOPE -.->|"'per-arm filters would let a scope apply to three arms<br/>and not the fourth, which surfaces as a scoped query<br/>returning a result from outside the scope.<br/>No type catches that leak.'"| SAFE["the leak a type cannot catch"]
    ARMS --> RES{"any hits?"}
    RES -->|"yes"| HITS["each hit carries supersededBy,<br/>present-and-nullable"]
    RES -->|"no"| EMPTY["archivedMatches: how many archived rows<br/>this same scope matches"]
    EMPTY -.->|"so an agent can tell 'never existed'<br/>from 'archived', and follow the link<br/>to what replaced it"| ANSWER["an empty result that answers"]
    MAIN --> SLEEP["memhtml sleep run — seventeen phases<br/>on a sleep/date branch, main untouched"]
    SLEEP --> COMMITS["each phase commits separately;<br/>trace-consolidation lands ONE commit per claim"]
    SLEEP -.->|"phases detect contradictions<br/>WITHOUT choosing a winner"| TASKS["a task, quoting its evidence verbatim,<br/>capped at ten a night — 'a proposal for a<br/>human, never a fact the corpus asserts'"]
    COMMITS --> HUMAN["the human reads phase-shaped diffs"]
    HUMAN --> MERGE{"memhtml sleep merge"}
    GATE["the discrimination gate: can retrieval rank a memory<br/>above its own high-similarity WRONG twin?"] --> MERGE
    CTRL["controls generated by reading the merge veto backwards —<br/>negation, numeric token, variant qualifier;<br/>each validated against its OWN family's predicate"] --> GATE
    MERGE -->|"gate refuses"| NOLAND["a run that degrades retrieval cannot land"]
    MERGE -->|"gate passes"| MAIN
    CORR["a correction"] --> ARCH["git mv into archive/ +<br/>memhtml-superseded-by on the loser,<br/>a supersedes edge on the winner, ONE commit"]
    ARCH -.->|"the default scope excludes archived rows;<br/>includeArchived or the asOf lens brings them back"| IDX
    ASOF["asOf lens"] -.->|"coalesce(valid_from, event_at, created_at) bounds the start —<br/>so a memory that declares no validity is valid from<br/>the moment it was written"| IDX
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `packages/store` | The git tree, supersession meta, archive moves, the merge driver |
| `packages/index` | The rebuildable SQLite index, the four arms, and the one scope filter |
| `packages/sleep` | Seventeen curation phases, each its own commit |
| `packages/eval` | Adversarial controls and the discrimination gate the merge runs |
| `packages/domain` | Divergence predicates, retention scoring, confidence decay |
| `packages/integrations` | Four host installers, and the receipts that make uninstall exact |

## 4. Essential Implementation Paths

`packages/index/src/scope.ts:6-20` — one filter for four arms, and the leak no
type catches.

`packages/index/src/scope.ts:195-200` — the point-in-time predicate and its
coalesce fallback.

`packages/index/src/retrieval.ts:140-160` — the count that makes an empty result
informative.

`packages/eval/src/controls.ts:1-20` — the merge veto read backwards into
impostors.

`packages/eval/src/discriminate.ts:8-12` — the one question the gate asks.

`packages/store/src/store.ts:253`, `:266` — a correction as one commit touching
both sides.

## 5. Memory Data Model

One semantic HTML5 file per fact, carrying the claim, type, entities, validity
bounds, confidence and supersession meta, addressed by path inside PARA
directories. The SQLite index holds files, chunks, edges and vectors and is
rebuildable from the tree, which is what makes the tree the system of record.

## 6. Retrieval Mechanics

FTS, vector, recency and salience arms fused with reciprocal rank, each
receiving the same scope filter. Archived rows are excluded by default and
admitted by `includeArchived` or by the point-in-time lens. Every hit reports
whether something superseded it and what.

## 7. Write Mechanics

The agent writes through the CLI or MCP; hooks never write. Corrections are one
commit touching the loser's meta and the winner's edge together. Eviction and
compression are `git mv` into `archive/`, so nothing is destroyed by curation.

## 8. Agent Integration

Fifteen MCP tools and three resources over stdio, plus installers for Claude
Code, Codex, Cursor and OpenCode that write MCP entries, hooks, an instruction
block and a skill — each recorded in a receipt with the SHA-256 of every owned
file or fragment, "so uninstall removes exactly what install wrote and nothing
you added beside it."

## 9. Reliability, Safety, and Trust

The strong parts are the actor separation, the refusable merge gate, the
single-filter scope, and an empty result that explains itself. The gaps are an
audit that is git rather than a table, scope that narrows only what the caller
asked, and a validity fallback that silently equates world time with write time
for memories that declare neither.

## 10. Tests, Evals, and Benchmarks

The discrimination gate runs in `pnpm check`, in CI, and again at merge, with a
deterministic fake-embedder mode so it needs no credentials, and a `live` mode
that reports `skipped: true` rather than passing when it cannot reach a model.
Write-path acceptance corpora sit beside it.

## 11. For Your Own Build

Build your scope filter once and hand the same string to every arm. A scope that
holds on three of four retrieval paths is a leak no type system will catch.

Generate your adversarial controls from the rules you already wrote. If you have
predicates that forbid merging two records, those predicates describe exactly
the impostors your retrieval has to survive.

Make an empty result say why. "Never existed" and "archived last night" are
different answers, and only one of them means the agent should stop looking.

Let the machine open a task where it declines to decide, and make the task quote
its evidence. A proposal with the sentence attached is reviewable; a flag is
not.

## 12. Open Questions

Whether an append-only record belongs beside the git history. Everything about
the curation is designed to be reviewable, and the review record itself lives
somewhere a rewrite can edit.

Whether the validity coalesce should be visible in the answer. A historical
query whose result rests on `created_at` because no memory declared a validity
is a different claim from one resting on `valid_from`, and the result does not
currently distinguish them.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `packages/index/src/scope.ts:6-20` | One filter for every arm, and the reason |
| `packages/index/src/retrieval.ts:140-160` | An empty result that tells you which kind of empty |
| `packages/eval/src/controls.ts:1-20` | Adversarial controls derived from your own veto |
| `packages/eval/src/discriminate.ts:8-12` | The single question a retrieval gate should ask |
| `README.md:126` | Three actors, and which one owns the one-way doors |

## History

**2026-09-16** — [`4778735a5016ecaabd725df594729848334e9968`](https://github.com/memhtml/memhtml/commit/4778735a5016ecaabd725df594729848334e9968) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: no auto-run surfaces, no build-time execution points, one unpinned dependency surface and eighteen dependency files inside the seven-day cooldown, with `pnpm-lock.yaml` present. `AGENTS.md` and `CLAUDE.md` are addressed to a reading agent and were recorded as data. Nothing was installed, built or run, no integration installer was executed, and no AWS credential was present, so the sleep pipeline and the evaluation gate are described from source rather than observed.

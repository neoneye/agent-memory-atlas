---
title: "Rekal"
eyebrow: "The gate that never stays quiet"
description: "A Go CLI that captures coding sessions at every git commit and ships them to teammates through git itself — with a committed benchmark showing its recall gate injected on all 1,888 questions and abstained on none of the 446 that had no answer."
root: ../..
page_kind: system
source_name: "rekal-dev/rekal-cli"
source_url: https://github.com/rekal-dev/rekal-cli
archive_name: "rekal-dev--rekal-cli"
revision: 4550e602eaa347d7afe28cf7f38f25f8c43f9afc
revision_url: https://github.com/rekal-dev/rekal-cli/commit/4550e602eaa347d7afe28cf7f38f25f8c43f9afc
analyzed_at: 2026-09-13
capabilities: "negative_eval"
capability_evidence:
  negative_eval: "the LoCoMo route benchmark — 446 committed adversarial cases whose gold answer is silence, scored against the shipped gate | scripts/industry-bench/runs/locomo-route-lowfloor/route.jsonl, summary.json, scripts/industry-bench/eval_locomo_route.py:9, :307 | each of the 1,888 committed rows carries `question`, `evidence`, `answerable`, `gold_silence` and `want_gate`; 446 have `gold_silence: true` and `want_gate: SILENCE`, and the harness states the rule as gold silence (adversarial / abstention) must SILENCE. The committed summary reports `want_silence: 446, want_silence_pass: 0, want_silence_pass_rate: 0.0` with `gates: {INJECT: 1888}`. The vacuity guard is in the same file: 1,442 rows want INJECT, all 1,442 pass, and `evidence@20_rate` is 0.9854, so the corpus is demonstrably populated and retrievable rather than empty. The run's own `eval.log` records `CONF_MIN=0.25 CONF_SOFT=0.2 GAP_MIN=0.02`, the same floors `digestConfMin`/`digestConfSoft`/`digestGapMin` ship | `go test ./...`; not run — two auto-run surfaces and a dependency manifest inside the 7-day cooldown"
stack_storage: "duckdb, files"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A whole captured coding session — its turns, tool calls and metadata — linked to the git commit it produced, kept raw rather than distilled"
  storage: "A `.rekal/` directory inside the repo: DuckDB for data and a derived index, a compressed frame format for the wire, and the git object store as the transport"
  retrieval: "BM25, LSA and vector similarity from an embedding model compiled into the binary, fused by weight, then nudged by recency and by how often an agent opened the session"
  write: "Captured at every commit by a git hook, scrubbed for secrets and home paths, indexed and embedded in a background pass"
  update_delete: "Sessions are immutable once captured. A duplicate re-capture is folded to a survivor; nothing records that a claim inside a session was wrong"
  scoping: "A merge gate on the export path decides what leaves the machine — unmerged work never ships. Recall itself applies no scope predicate"
  integration: "A CLI, a Claude Code plugin and skill, and a CLAUDE.md line; adapters read Claude, Cursor, Copilot, Codex, Gemini, Kiro and OpenCode transcripts"
  background: "A local embedding daemon and an incremental knowledge re-chunk keyed to the commit the index was last built at"
  trust: "None as a status. A per-result confidence number drives the gate, and no field records whether anything in a session was later found false"
  strengths: "A citation graph that ranks on the drill edge rather than the recall edge, because the recall edge is the ranker's own output fed back to itself"
  risks: "The gate's abstention path is scored at zero on 446 committed adversarial cases at shipped floors; `captured_at` means the session's start time for three adapters and the ingest clock for two"
---

## 1. Executive Summary

Rekal is a Go CLI — Apache-2.0, about 41,900 lines across 184 files — that
captures an AI coding session at every git commit, stores it raw in a `.rekal/`
directory inside the repository, and moves it to teammates over the `git push`
they already run. There is no server, no account and no memory service: the
embedding model, the inference engine, the database and the full-text extension
are compiled into a single ~170 MB binary, so recall works offline.

The design argument is good and the engineering is careful in places this corpus
rarely sees. The best of it is in the recall citation graph. Rekal records every
session an agent reached and every session an agent actually opened, keeps the
two counts in separate columns, and ranks on only the second. The reasoning is
written where it is implemented: a recall edge "only says the engine ranked this
session into some window — its own past output, which is why feeding it back
into ranking is a loop." It is not a hypothetical. The comment carries the
measurement that produced it: 741 recall edges against 6 drills, 36 of 37
sessions "reached", and the top slot held by a three-turn session.

The finding is what the project committed beside its own benchmark. Rekal's
recall emits a verdict — `INJECT`, `KNOWLEDGE` or `SILENCE` — and `SILENCE` is
the answer for a question the store cannot support. `scripts/industry-bench/runs/`
holds two scored LoCoMo runs of 1,888 questions each. Both report
`gates: {"INJECT": 1888}`. Of those questions 446 are adversarial, with no
answer in the corpus and a gold verdict of silence. Both runs record
`want_silence_pass: 0` and `want_silence_pass_rate: 0.0`. The 0.7638 pass rate
is carried entirely by the 1,442 answerable questions, every one of which
passed.

Two things stop that from being a stale artifact. The run's own `eval.log`
records the floors it used — `CONF_MIN=0.25 CONF_SOFT=0.2 GAP_MIN=0.02` — and
those are the values `digestConfMin`, `digestConfSoft` and `digestGapMin` return
by default at this commit. And `digest.go`'s header says it is "the in-binary
port of the skill's `route.py` … byte-identical to `route.py`", which is the
script the benchmark drove. The measured configuration is the shipped one.

One mark, `negative_eval`, and it is earned on exactly those 446 cases. The
other six are withheld, each for a reason in section 9. The most instructive is
`tombstone`: the README promises that "dead-ends already ruled out stay ruled
out; nobody re-proposes them", and the only thing in the tree named for it is a
wire constant with no producer.

## 2. Mental Model

A memory is a whole conversation, kept whole. Rekal does not extract facts,
summarise sessions into claims, or distil anything up front — the README makes
the refusal explicit against hosted memory layers, whose memories are
"distilled lossily up front". What is stored is the transcript: turns, roles,
tool calls, the files touched, and the commit it ended at.

That choice moves all of the judgement to read time, and it is where the design
lives or dies. Nothing in the store says a claim inside a session was wrong,
because the store holds conversations rather than claims. What makes a rejected
approach "stay rejected" is that recall surfaces the conversation where it was
rejected. There is no rejected-value record, and there is nothing to consult
before proposing something again — the guarantee is entirely a retrieval
guarantee.

Which is why the gate matters more here than in a system with an epistemic
layer. Recall returns a window of seeds with a per-seed confidence and one of
three verdicts. `INJECT` says sessions worth reading were found. `KNOWLEDGE`
says the answer is in tracked files rather than in a conversation. `SILENCE`
says nothing cleared the floor, and it exits 1. The chain from the README's
promise to the code runs through that verdict: a dead-end stays ruled out only
if a later query retrieves the session containing it, and the system is honest
about an empty answer only if `SILENCE` can fire.

```mermaid
%% caption: every guarantee Rekal makes about ruled-out approaches is a retrieval guarantee, because nothing in the store records that a claim was rejected — and the one verdict that can say "no answer here" scored zero on the 446 committed cases that required it
flowchart TD
    S["session captured at a commit<br/>turns kept raw, nothing distilled"] --> ST["stored in .rekal/ DuckDB<br/>immutable; no claim-level record"]
    ST --> Q["later query"]
    Q --> R["BM25 + LSA + vector<br/>fused, then recency and drill boosts"]
    R --> V{"episodeVerdict<br/>on absolute confidence"}
    V -->|"top >= 0.25, or<br/>top >= 0.20 and gap >= 0.02"| I["INJECT<br/>seeds handed to the agent"]
    V -->|"nothing clears the floor"| SI["SILENCE reason=below_gate<br/>exit 1"]
    I --> A["agent reads the rejection<br/>in the transcript"]
    SI --> H["agent told the store has nothing"]
    A --> G["a dead-end stays ruled out"]
    V -.->|"446 committed cases needed this edge;<br/>0 of them took it"| SI
```

## 3. Architecture

One binary and a directory. `rekal init` installs a git hook and writes one
marked line into `CLAUDE.md`; from then on every commit captures whatever
sessions produced it. The store is `.rekal/` inside the repository, and it is
the repository that moves it: sessions are encoded into a compressed frame
format and travel as git objects on the same push and fetch a developer already
runs.

Inside `.rekal/` the split is deliberate and load-bearing. `data.db` is the
permanent DuckDB store of sessions, turns, tool calls, checkpoints and the
recall citation graph. `index.db` is derived and rebuildable — facets,
full-text, embeddings, and the aggregated reach counts. The compatibility
document freezes the store format, wire format, command surface and exit codes
under the version number while deliberately leaving ranking and `index.db`
unfrozen, so retrieval can keep changing without a major version.

What an operator stands up is nothing. There is no service, no model download on
first run, and no API key: the embedding model ships inside the binary as a
compressed `nomic-embed-text-v1.5` in Q8_0, with a small local daemon around it,
and DuckDB and the full-text extension are linked in. The cost is the binary —
~170 MB to download, ~200 MB on disk — and the project states that trade in the
quick-start rather than burying it.

Three tables are local-only by design and never cross the wire: `recall_edges`,
`checkpoint_state`, and `merge_gate_cache`. Each carries a comment saying why.
The merge-gate cache is the clearest: it "is a record of what this machine's git
could see, which says nothing useful to anyone else."

## 4. Essential Implementation Paths

- **Capture** — the commit hook collects sessions from whichever agent wrote
  them (`session/claude.go`, `codex.go`, `copilot.go`, `cursor.go`,
  `gemini.go`, `kiro.go`, `opencode.go`), each adapter normalising into the
  same `Turn`/`ToolCall` shape in `session/parse.go`.
- **Scrub** — `scrub/secrets.go` and `scrub/paths.go` run before storage:
  pattern and entropy secret detection, and home-path anonymisation that
  replaces the current username with `user_<8hex>` derived from a SHA-256.
- **Recall** — `search/search.go` (1,873 lines) fuses BM25, LSA and vector
  similarity by configured weight, then adds a max-normalised recency term and
  a max-normalised drill term before a subagent discount.
- **Gate** — `digest.go:44` `episodeVerdict` sorts candidate confidences and
  returns `pass` when the top clears `CONF_MIN` (0.25) or clears `CONF_SOFT`
  (0.20) with a gap of at least `GAP_MIN` (0.02); otherwise `silence`.
- **Citation graph** — `graph/graph.go` appends one NDJSON edge per reached
  session to a lock-free spool so the hot recall path never takes DuckDB's
  single writer; the spool drains into `data.db.recall_edges` at the next
  checkpoint, which already holds that writer.
- **Export** — `transport/export.go:146` `filterMerged` drops checkpoints whose
  commits are not reachable from the mainline tip, so unmerged work never
  leaves the machine.

## 5. Memory Data Model

`sessions` carries `id`, `parent_session_id`, `session_hash`, `captured_at`,
`actor_type`, `agent_id`, `user_email`, `branch`, `source`, `team_name`,
`workflow_name`, `agent_type`, `description` and `spawn_depth`. `turns` carries
role, content, order and a timestamp. `checkpoints` carries the commit sha,
branch, author, timestamp and an `exported` flag.

There is exactly one time axis the system reads. `captured_at` is the session's
clock, and its meaning depends on which agent wrote the transcript. Copilot sets
it to the earliest event time, with the comment "captured_at is the session's
real start, the earliest event time — not the ingestion wall clock (that is only
the final fallback below)". Gemini uses the transcript's `StartTime`, Kiro the
sibling metadata's `created_at`, both falling back to now. Claude and Codex set
`payload.CapturedAt = time.Now().UTC()` unconditionally. So the column holds
when the conversation happened for three sources and when Rekal ingested it for
two — and the ranking's recency prior reads that column. Two sessions from the
same afternoon can order by when they were imported rather than when they
occurred, depending on which tool produced them.

The real event time is not lost: `turns.ts` holds it, and `rekal query` exposes
SQL over it with a documented example filtering a date range. It is simply never
joined against a record-time axis, and no as-of read exists anywhere in the tree.

`session_supersedes` maps `old_session_id` to `survivor_session_id`. Its comment
places it precisely: it exists so that when duplicate copies of one conversation
collapse, the reach counts keyed to whichever copy was surfaced at the time fold
onto the survivor, rather than "a heavily used conversation read[ing] as never
used the moment its copies collapse". It is duplicate reconciliation, not a
judgement that anything was wrong.

## 6. Retrieval Mechanics

Three arms are fused by weight — BM25 at 0.3, LSA at 0.2, semantic at 0.5 in
the shipped calibration — over a window of 20 seeds. Two additive layers then
reorder within the retrieved set, and both are documented with the same
discipline: each is max- or min-max-normalised, each ships small, each is
inert on a cold store, and each carries the sentence "Never feeds absolute
confidence."

`RecencyBoost` ships 0.15 and is "inert whenever the candidate set shares a
timestamp (span 0)". `ReachBoost` ships 0.2 and is the interesting one. It reads
`session_reach.drill_count` — the edges where an agent chose to open a session —
and not `reach_count`, which counts every edge including the ones this engine
produced itself. The rationale is given twice, in the schema and at the loader,
and the second copy carries the numbers: a recall returns 20 seeds, so "on any
store smaller than a few hundred sessions one query marks most of the corpus
(measured: 36 of 37 sessions reached, top slot a three-turn session, an empty
session at 36)."

That is a real and reusable correction. A usage signal derived from the ranker's
own output is a feedback loop, and the separation here is between evidence the
ranker manufactured and evidence it did not. Both counts stay in the table; only
the one from outside the ranker reaches ranking. One cosmetic leftover: the
function that loads the drill count is still called `loadReachCounts`, and its
doc comment opens by having to say it reads the other column.

The gate runs on absolute confidence, never on the normalised score, which is
the right choice — a max-normalised top score is 1.0 whether the match is good
or the best of a bad set. Both boosts are excluded from it; `config.go` states
that "RecencyBoost/ReachBoost never feed the silence gate".

## 7. Write Mechanics

Capture is synchronous with the commit and cheap by construction: the recall
spool is a file append precisely so the hot path never contends for DuckDB's
single writer, and the drain happens at checkpoint time when that writer is
already held. Indexing and embedding run in a background pass; the knowledge
layer keys its watermark to the commit sha it was last built at, so a recall
whose HEAD matches skips the refresh after one `rev-parse` and a mismatch
re-chunks only files whose blobs changed.

Sessions are immutable once captured. There is no update path, no consolidation
pass that rewrites stored memories, and no summarisation step — the transcript
that was captured is the transcript that is retrieved, which is the point.

Scrubbing happens before storage rather than before transmission, so a secret
never reaches the database, let alone the wire. The path anonymiser hashes the
current username into `user_<8hex>` and rewrites both macOS and Linux home
layouts plus their hyphenated variants.

The export gate is the other write-shaped decision. `filterMerged` runs on the
push path and keeps a checkpoint only when its commit is reachable from the
mainline tip, and the verdicts are cached on `(git_sha, target_tip,
gate_version)`. The key includes the tip "because the answer genuinely changes
when the mainline moves: work that was unmerged at one tip may have landed by
the next", and the version because "a cache that outlives the reasoning behind
it is worse than no cache".

## 8. Agent Integration

`rekal init` writes one marked line into `CLAUDE.md` telling the agent to recall
before non-trivial work — and that line is where the product promise actually
lives. It says recall "returns the why, the decisions, and the dead-ends already
ruled out". Nothing extracts decisions or dead-ends; the sentence is a
description of what a retrieved transcript contains.

The shipped skill is prose rather than code. `SKILL.md` and
`references/ledger.md` tell the agent how to read the verdict, and they are
candid that it is advisory: "`INJECT`/`SILENCE` are **recommendations**, biased
toward more data than" the alternative. The guidance around abstention is
careful — "a weak seed is not absence — before concluding SILENCE, re-search
once", and "Only conclude SILENCE after a genuinely different re-search also
comes back" empty. Read against the benchmark, that instruction is carrying more
weight than it looks: the model is being asked to supply the abstention the gate
does not.

Adapters cover Claude Code, Cursor, Copilot, Codex, Gemini, Kiro and OpenCode,
which is unusually broad, and the OpenCode adapter is the only place SQLite
appears — it reads that tool's store, rather than being one of Rekal's own.

## 9. Reliability, Safety, and Trust

**Negative eval — earned.** The 446 committed adversarial cases, the scored
result, and the positive control are in section 10.

**Tombstone — withheld, and the near-miss is exact.** The README's second bullet
is "Stop re-deciding — dead-ends already ruled out stay ruled out; nobody
re-proposes them." The mark asks for a durable record of a rejected value, keyed
on the value. There is none: the store holds conversations, not claims, and
nothing is consulted before an approach is proposed again. The one identifier in
the tree named for the mechanism is `FrameTombstone FrameType = 0xFF` in
`codec/body.go:44`, and it occurs exactly once in the repository — its own
declaration. No encoder emits it, no decoder branches on it, and no test
exercises it. It is a reserved wire slot for a deletion that was not built.

**Scope enforced — withheld, and the boundary is real anyway.** Rekal's privacy
claim is that "an unmerged spike never leaves your machine", and that is true and
enforced. But it is enforced on egress: `filterMerged` is called only from
`transport/export.go`, on the two push paths. Recall applies no scope predicate
at all — `branch` is stored on the session facet and read only to display it,
and a search for a branch comparison in a query returns nothing. This is a gate
on what leaves, not a filter on what returns, and the mark asks for the second.
Worth saying plainly because the egress gate is the stronger guarantee for the
threat the project actually names.

**Audit log — withheld, and the reason is a category the rubric draws.**
`recall_edges` is genuinely append-only, permanent, and carefully kept out of
the wire. But it records reads — which sessions an agent reached or opened —
not mutations of the store. A record of which sessions were retrieved cannot
turn out to be false; it happened. The mutation history of this store is git's,
which is a different mechanism.

**Trust state — withheld.** Nothing carries an epistemic status. `actor_type`
distinguishes human from agent and `source` names the tool; neither says whether
anything is true. Confidence is a float that drives the gate and is explicitly
never allowed to be fed by the ranking boosts.

**Human review — withheld.** There is no approval surface; a search for
`approve`, `review_status`, `adjudicat` and `curate` across the Go sources
returns nothing.

## 10. Tests, Evals, and Benchmarks

The paper is [arXiv:2607.14390](https://arxiv.org/abs/2607.14390), "Why Git Is
the Memory Solution for the Agentic Development Lifecycle", Frank Guo, submitted
15 July 2026. It reports ~0.31 pooled MRR across an eight-corpus retrieval study
against a raw-transcript grep floor and a parsed-turn floor, 0.83 answer
sufficiency on a ~50k-LOC production system, and 382–980 tokens per question. It
also reports that single-shot retrieval scored 0.07–0.20 on real developer
questions, which is the honest number behind the router design.

The benchmark harness is committed, which is rarer than it should be, and the
artifacts are what make this report worth reading. `scripts/industry-bench/`
carries LoCoMo and LongMemEval normalisers, a scoring shim, a calibration file,
and `runs/` with per-question output. The datasets themselves are fetched by
script, but the evaluated rows are committed: `route.jsonl` holds all 1,888
questions with `question`, `evidence`, `answerable`, `gold_silence`,
`want_gate`, the verdict, `top_conf` and `pass`.

`eval_locomo_route.py` states the rule in its header: "Gold silence
(adversarial / abstention) → must SILENCE", and at line 307, "INJECT when an
answer is expected; SILENCE when gold is abstention." Both directions in one
harness is the right shape, and it is why the negative result here is not
vacuous — the same file proves the corpus is retrievable before asking whether
the excluded material stayed out.

The two committed runs agree exactly:

| | lowfloor | knfloor |
|---|---|---|
| questions | 1,888 | 1,888 |
| gates issued | `INJECT: 1888` | `INJECT: 1888` |
| want INJECT / passed | 1,442 / 1,442 | 1,442 / 1,442 |
| want SILENCE / passed | 446 / **0** | 446 / **0** |
| evidence@20 rate | 0.9854 | 0.9868 |
| token saving | 82.85% | 82.87% |

A representative failing row: `conv-26:q153`, category `adversarial`, question
"What did Caroline realize after her charity race?", `evidence: []`,
`answerable: false`, `gold_silence: true`, `want_gate: SILENCE`, `gate: INJECT`,
`n_results: 19`, `top_conf: 0.71`. Nineteen seeds at 0.71 confidence for a
question with no answer in the corpus.

Two qualifications, both in the project's favour and neither changing the
result. The run notes are dated 17 July 2026 against a pin from 10 September,
and `route.py` itself is no longer in the shipped skill — the logic moved into
the binary. But `digest.go` says it is a byte-identical port of that script, and
the floors the runs recorded are the floors the binary ships. The second is that
the `notes/` directory shows the team reasoning about exactly this and declining
the cheap fix: the failed-case autopsy concludes that one case "needs better
retrieval or why-mode assembly, not a lower SILENCE bar."

The Go suite is substantial — integration tests for checkpoint round-trips,
recall, sync, schema migration and the codec, including a 991-line frame test.
It was not run here: the screen found a `.claude-plugin/` marketplace manifest,
a configured LFS smudge filter, and `go.mod`/`go.sum` inside the seven-day
cooldown.

## 11. Patterns Worth Stealing

### Steal

- **Split the usage signal by who produced it.** The recall edge is the ranker's
  own output; the drill edge is an agent's decision. Ranking on the first is a
  loop that amplifies whatever surfaced once. Any system boosting on "memories
  you keep returning to" needs this distinction, and most do not have it.
- **Put the measurement in the comment.** "36 of 37 sessions reached, top slot a
  three-turn session, an empty session at 36" is what makes the design decision
  reviewable years later, and it costs one line.
- **Version the cache key with the rule.** `merge_gate_cache` keys on
  `(git_sha, target_tip, gate_version)` because the answer changes when the
  mainline moves and when the rule does — "a cache that outlives the reasoning
  behind it is worse than no cache".
- **Gate on absolute confidence, never the normalised score.** A max-normalised
  top score is 1.0 for the best of a bad set.
- **Scrub before storage, not before transmission.** A secret that never enters
  the database cannot leak from it.
- **Keep the transport out of the derived tables.** Three tables carry an
  explicit comment saying they must never cross the wire, each with its reason.

### Avoid

- **A verdict whose negative branch is never taken.** `SILENCE` exists, is
  implemented, exits 1, and is documented for the agent — and on the one
  committed measurement that requires it, it fired zero times out of 446.
- **One timestamp column meaning two things.** `captured_at` is the session
  start for three adapters and the ingest clock for two, and the recency prior
  ranks on it either way.
- **A product promise with no mechanism under it.** "Dead-ends already ruled out
  stay ruled out" is a claim about retrieval recall stated as a claim about
  memory, and the identifier named for the mechanism is unwired.
- **Naming a loader for the column it deliberately does not read.**
  `loadReachCounts` reads `drill_count` and has to spend its first line saying so.

### Fit

Take Rekal if your team already lives in git, works in one repository, and wants
the reasoning behind commits available to everyone's agent without operating
anything. The transport story is the strongest part of the design: memory that
arrives with `git fetch` needs no sync job, no access-control layer of its own,
and no second source of truth about who may see what — the repository already
answered all three.

It fits badly where memory must contain judgements rather than conversations. If
you need to record that a claim was wrong, that a fact was superseded, or that
an approach is forbidden, none of that exists here and the raw-transcript design
is against it in principle rather than by omission. It also fits badly where an
agent must be told reliably that nothing is known, which on this evidence it
will not be.

Be deliberate about the binary. ~200 MB on disk per developer is the price of no
service and offline recall, and that is a reasonable trade, but it is a per-seat
trade and the project is right to state it early.

## 12. Antipatterns / Risks

- **The abstention path is unmeasured in the shipped direction.** Every
  committed evidence about `SILENCE` firing on questions that need it says it
  does not. An agent that trusts `INJECT` as a signal that relevant material
  exists is trusting a verdict that was issued 1,888 times out of 1,888.
- **The skill instruction is carrying the gate's job.** `ledger.md` asks the
  agent to re-search before concluding silence, which is sound advice and also
  the only abstention in the system that has been observed to work.
- **Recency ranks on an inconsistent clock.** Reindexing or re-importing a
  Claude or Codex session moves it to the front of the recency prior.
- **Nothing records a correction.** A session where the team decided X and a
  later session where they reversed it are both retrievable, both unmarked, and
  ordered by relevance and recency rather than by which one is current.
- **`session_supersedes` exists for a bug, not a concept.** Its comment names
  "the duplicate bug" as the reason. It is not a supersession model and should
  not be read as one.
- **The store grows with the repository and never compacts.** Sessions are
  immutable and kept raw; there is no retention policy, and the wire format's
  reserved deletion frame is unimplemented.

## 13. Build-vs-Borrow Takeaways

Borrow the transport idea outright, even if you never run Rekal. Putting team
memory in the repository and letting `git push` move it removes an entire class
of problem — the sync service, its availability, and its permission model — and
the merge gate is a clean answer to the obvious objection about unfinished work.

Borrow the two-count citation graph. It is small, it is self-activating on a
cold store, it fails soft on an index without the column, and the reasoning
behind it generalises to any ranker that learns from its own results.

Do not borrow the gate without measuring its negative branch first. The lesson
is not that Rekal's floors are wrong; it is that a verdict with three outcomes
needs a scored count per outcome, because a pass rate aggregated over a set
where 76% of cases only require the easy branch will look healthy while one
branch is dead.

Build your own if the memory has to hold claims. Rekal's raw-session model is a
deliberate, well-argued position, and retrofitting claim-level state onto it
would fight the design rather than extend it.

## 14. Open Questions

- Is the 0/446 known? The `notes/` directory shows the abstention cases being
  discussed and a lower SILENCE bar being explicitly rejected as the wrong fix,
  so the behaviour appears understood; whether the pass-rate-by-branch split is
  tracked anywhere outside these committed artifacts is not visible in the tree.
- Does the in-binary `digest` remain byte-identical to the `route.py` the
  benchmark drove, now that the script is no longer in the tree to compare
  against?
- Should `captured_at` be split into event time and ingest time, given that
  three adapters already have the former?
- What is `FrameTombstone` reserved for, and does the store format's version
  guarantee cover a frame type nothing writes?

## 15. Appendix: File Index

**Capture and scrub**

- `cmd/rekal/cli/session/` — `parse.go` (the shared shape), `claude.go`,
  `codex.go`, `copilot.go`, `cursor.go`, `gemini.go`, `kiro.go`, `opencode.go`
- `cmd/rekal/cli/scrub/secrets.go`, `paths.go`
- `cmd/rekal/cli/checkpoint.go`

**Store**

- `cmd/rekal/cli/db/schema.go` (`:270` schema meta, `:291` recall edges,
  `:334` sessions), `db.go`, `indexer.go`
- `cmd/rekal/cli/db/reach.go` (`:12-35` the two-count rationale, `:64`
  supersedes), `mergegate.go`, `knowledge.go`
- `cmd/rekal/cli/graph/graph.go` — the recall spool

**Retrieval and the gate**

- `cmd/rekal/cli/search/search.go` (`:1443` the drill-count loader),
  `weights.go` (`:45` recency, `:59` reach)
- `cmd/rekal/cli/digest.go` (`:38` `episodeVerdict`, `:207` the INJECT line,
  `:223` the SILENCE line), `recall.go:422`, `query.go`

**Transport**

- `cmd/rekal/cli/transport/export.go:146` — `filterMerged`
- `cmd/rekal/cli/codec/frame.go`, `body.go:44`, `dict.go`

**Benchmark**

- `scripts/industry-bench/eval_locomo_route.py` (`:9`, `:307`),
  `calibration/skill-default.json`, `datasets/normalize_locomo.py`,
  `normalize_longmemeval.py`
- `scripts/industry-bench/runs/locomo-route-lowfloor/` and
  `locomo-route-knfloor/` — `summary.json`, `route.jsonl`, `eval.log`
- `scripts/industry-bench/runs/notes/2026-07-17-failed-cases-skill-route.md`

**Agent surface**

- `cmd/rekal/cli/init.go:41` — the CLAUDE.md line
- `cmd/rekal/cli/skill/skills/rekal/SKILL.md`, `references/ledger.md`,
  `references/reference.md`

### Commands behind the absence claims

```sh
grep -rn 'FrameTombstone\|0xFF' --include='*.go' .
grep -rni 'tombstone\|rejected_\|blocklist\|denylist\|do not resurface' \
  --include='*.go' cmd/ | grep -v '_test'
grep -rn 'git_branch *=\|branch *= *?\|WHERE.*branch' --include='*.go' cmd/ | grep -v '_test'
grep -rn 'filterMerged(' --include='*.go' cmd/ | grep -v '_test'
grep -rni 'as_of\|asOf\|point.in.time\|valid_from\|valid_at\|known_at\|recorded_at' \
  --include='*.go' cmd/ | grep -v '_test'
grep -rni '"verified"\|"pending"\|"candidate"\|trust_state\|status *VARCHAR' \
  --include='*.go' cmd/ | grep -v '_test'
grep -rni 'approve\|review_status\|adjudicat\|curate' --include='*.go' cmd/ | grep -v '_test'
grep -rni 'decision\|rejected approach\|dead.end\|ruled out' --include='*.go' cmd/ | grep -v '_test'
find . -name 'route.py' -o -name 'recall-route.py' -o -name 'hunt-gate.py' | grep -v '.git/'
```

## History

**2026-09-13** — [`4550e602eaa347d7afe28cf7f38f25f8c43f9afc`](https://github.com/rekal-dev/rekal-cli/commit/4550e602eaa347d7afe28cf7f38f25f8c43f9afc) — first reading. Screened first: two auto-run surfaces — a `.claude-plugin/` marketplace manifest and a configured LFS smudge filter over the packed embedding model — plus `go.mod` and `go.sum` inside the 7-day cooldown and an uninstalled `scripts/pre-push` hook. Nothing was installed and no suite was run; the clone is shallow, so the LFS-tracked model is a pointer. One mark. `negative_eval` is earned on 446 committed adversarial rows whose gold verdict is silence, scored in two committed runs at the floors the binary ships, with 1,442 answerable rows passing in the same file as the positive control. Both runs report `want_silence_pass_rate: 0.0` against `gates: {INJECT: 1888}`. `tombstone` is withheld: the README promises that ruled-out dead-ends stay ruled out, and `FrameTombstone` occurs once in the repository, in its own declaration, with no encoder, decoder or test. `scope_enforced` is withheld because the merge gate filters the export path rather than the read path and `branch` never appears in a query predicate. `audit_log` is withheld because `recall_edges` is an append-only record of reads rather than of mutations. `bitemporal` is withheld: `captured_at` is the only axis the system reads, it means the session start for three adapters and the ingest clock for two, and no as-of read exists. `trust_state` and `human_review` are withheld on searches recorded in the appendix.

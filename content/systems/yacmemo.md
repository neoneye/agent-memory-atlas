---
title: "yacmemo"
eyebrow: "The duplicate guard strips the suffix you would rename around"
description: "A Markdown memory server that refuses a near-duplicate title after normalising away the dates and -2 suffixes an evasion would use, rate-limits its own override, hides nothing from search, and lets a person dismiss a collision warning so it stops appearing on every later hit."
root: ../..
page_kind: system
source_name: "yachen4ever/yacmemo"
source_url: https://github.com/yachen4ever/yacmemo
archive_name: "yachen4ever--yacmemo"
revision: 2440aa563e1474d5a07b16d052373c28ed8a4a7c
revision_url: https://github.com/yachen4ever/yacmemo/commit/2440aa563e1474d5a07b16d052373c28ed8a4a7c
analyzed_at: 2026-09-16
capabilities: "human_review"
capability_evidence:
  human_review: "a person marks a detected collision resolved or dismissed in the web console, and every later search of that note stops carrying its warning | yacmemo/index_db.py:255-261, yacmemo/webui/app.py:254-265, :423, yacmemo/search.py:107-119 | `resolve_collision(collision_id, status)` validates against `(\"open\", \"resolved\", \"dismissed\")` and is documented as a \"human decision via WebUI/audit\". Its only caller in the repository is the `POST /api/{user}/collision` route — no scheduler, detector or agent path reaches it. `Search._warnings_for` calls `self.db.collisions_for(path)`, whose `status` parameter defaults to `\"open\"`, so the ⚠ line naming the colliding note disappears from every subsequent hit once a person has judged it. The detector proposes; the person disposes; the retrieval path reads the person's verdict | tests/test_index_db.py:84"
stack_storage: "files, sqlite, lancedb"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A Markdown note under a git-tracked memory root, its title the identity and its directory only filing, with Basic-Memory-style `- [category] text` observation lines parsed out of the body"
  storage: "Markdown files as the sole truth; SQLite (metadata, FTS5 trigram, collisions, guard events) and LanceDB vectors are derived indexes under `.index/`, rebuildable and untracked"
  retrieval: "FTS5 trigram and vector search fused by RRF, with a ⚠ warning attached to any hit that has an open collision"
  write: "`memory_write(title, content, force, force_confirm)` — refused outright when a near-duplicate title exists, unless forced, and the force is itself rate-limited"
  update_delete: "`memory_edit` on a unique anchor, `memory_edit_section` by heading, move, and an explicit delete. Every one commits to git, so the memory repository is always clean and any deletion is recoverable"
  scoping: "A separate `Store(root=...)` and MCP mount per user — separate directories rather than a predicate"
  integration: "One streamable-HTTP server that any MCP client joins by URL with nothing installed locally, plus a bundled Vue web console at `/ui/`"
  background: "A weekly curator on a systemd timer that reviews quality and writes a proposal report, and an incremental observation-collision detector on the write path"
  trust: "A deterministic duplicate guard with a counted override, collision warnings a person can dismiss, per-call usage logging, and git history over every mutation"
  strengths: "The duplicate guard is the best version of this idea in the corpus, because it anticipates the evasion. `normalize_title` strips trailing dates, `-2`-style counters, `v1`, `更新` and `（新）` before comparing, so the rename that would slip a second copy past a naive check is exactly what it collapses — and the refusal message names the near-matches with their scores and tells the caller to edit instead. The override ladder is better still: `force=true` is allowed, counted in `guard_events`, and once forced writes in the last 24 hours cross a configured threshold a second flag becomes mandatory, so bypassing is possible, visible and self-limiting rather than free. The design also refuses to hide: there is no status, tier or score anywhere in the search path that withholds a note, and a contradiction is surfaced beside its counterpart with a ⚠ rather than silently resolved. And there is no generative model in the memory subsystem at all — one 0.6B embedding call — so the store's behaviour is string math a reader can follow"
  risks: "No record covers every mutation. Git commits do — and git history is not an audit record this atlas credits, because it lives outside the store and anyone with the directory can rewrite it. Of the two SQLite records, `guard_events` holds only refusals and forced bypasses, and `call_log` is written by the MCP tool wrapper, so a note saved or deleted through the web console leaves no row in it at all; it also carries an argument summary rather than a before-image, and self-trims to 20,000 rows. The curator is proposal-only by design — \"it has no write power over memories\" — but nothing in the system approves or applies a proposal either: the WebUI lists the report files and a person carries out the work by hand, so the loop is closed outside the software. The duplicate guard is keyed on title similarity only, so the same fact under two genuinely different titles is two memories and the guard says nothing. Scope is one directory per user rather than a predicate, and MIT is declared in `pyproject.toml` with no licence file in the tree"
---

## 1. Executive Summary

yacmemo describes itself as a personal memory layer with API-level consistency
guards — "markdown 为本、全本地、agent 无关" (Markdown-native, fully local,
agent-agnostic). Version 0.2.0, MIT by metadata, 11,833 lines of which 4,764 are
Python, with 95 test functions. Documentation and interface are in Chinese; the
code comments are in English.

The shape is one server process on the machine that holds the data, speaking
streamable HTTP, with a separate MCP mount and store root per user. Any client —
Claude Code, Codex, Cursor — joins by adding a URL, with nothing installed
locally. Markdown files in a git repository are the only truth; SQLite and
LanceDB are derived indexes under `.index/` that can be deleted and rebuilt.

Three things make it worth reading.

**The duplicate guard anticipates its own evasion.** `memory_write` refuses a
title that is a near-duplicate of an existing note — and the comparison runs on
`normalize_title`, which first strips trailing dates, `-2`-style counters, `v1`,
`更新` ("updated") and `（新）` ("new"). The rename an agent would reach for to
get a second copy in is precisely the transformation the normalizer collapses.
The refusal names the near-matches with their similarity scores and says what to
do instead: edit the existing note.

The override is the better half. `force=true` writes anyway and records a
`forced` event; but when forced writes in the last 24 hours reach a configured
threshold, a second flag `force_confirm=true` becomes mandatory, with the comment
naming the intent — "human-confirm semantics, deterministic and fully counted in
guard_events". A bypass that is possible, counted and self-limiting is a
materially different thing from a bypass that is free.

**Nothing is hidden.** There is no status, tier, score or expiry anywhere in the
search path that withholds a note. When two notes collide, both are returned and
the hit carries a warning naming the other:

> "⚠ 与 [[other]] 疑似重复（score …）— 建议读两篇后用 memory_edit 合并"
> *(suspected duplicate of [[other]] — read both, then merge with memory_edit)*

Most systems in this corpus resolve a contradiction by deciding which side wins
and dropping the other. This one presents both and hands the judgement to the
model reading the results — which is consistent with the other stated rule, that
the memory subsystem contains no generative LLM: one 0.6B embedding call, and
everything else deterministic string math.

**A person's dismissal changes what later reads say.** A collision carries a
status of `open`, `resolved` or `dismissed`, validated against that whitelist and
documented as a "human decision via WebUI/audit". Its only caller in the
repository is the web console's `POST /api/{user}/collision`; no detector,
scheduler or agent path sets it. And `Search._warnings_for` reads
`collisions_for(path)` with the default `status="open"`, so once a person has
judged a pair, the ⚠ stops appearing on every future hit for that note. That is
the mark: a human verdict, stored, consulted by the retrieval path.

Where it is thinner is the record. Every write, edit, move and delete makes a git
commit, so the memory repository is always clean and a mistaken deletion is
recoverable — good practice, but git history is not an audit record this atlas
credits, since it sits outside the store and can be rewritten by anyone holding
the directory. The two SQLite records each cover a slice: `guard_events` holds
refusals and forced bypasses only, and `call_log` is written by the MCP tool
wrapper, so a note saved or deleted in the web console produces no row in it. It
stores a summary of arguments rather than a before-image, and trims itself to
20,000 rows.

The curator is honest about its own limits in the first line of its module —
"periodic review -> proposal report. Never auto-applies" — and the system keeps
that promise completely: proposals are Markdown files in `curator/`, the WebUI
lists them, and a person does the work by hand. That is the right default, and it
also means the approval half of the loop lives outside the software.

## 2. Mental Model

A **note** is a Markdown file. Its **title** is its identity; its directory is
only filing.

A **guard** is a refusal at the API, not a warning in a report.

A **collision** is a question the system asks and a person answers.

**Git** is the undo.

```mermaid
%% caption: the write guard normalises away the suffixes an evasion would add, refuses, and counts the override; a person's verdict on a collision is what the search path reads
flowchart TB
    W["memory_write(title, content,<br/>force, force_confirm)"] --> NORM["normalize_title: strip trailing dates,<br/>'-2' counters, 'v1', '更新', '（新）',<br/>punctuation and case"]
    NORM --> SIM{"title_similarity >= threshold<br/>against every existing title?"}
    SIM -->|"no"| OK["write the file"]
    SIM -->|"yes, force not set"| REF["REFUSED — name the near-matches<br/>with scores, say to use memory_edit<br/>guard_events: kind='refused'"]
    SIM -->|"yes, force=true"| LADDER{"forced writes in the last 24h<br/>>= force_confirm_threshold?"}
    LADDER -->|"no"| FORCED["write · guard_events: kind='forced'"]
    LADDER -->|"yes, force_confirm not set"| STOP["REFUSED — 'force 近 24 小时已被使用 N 次…<br/>需要人工确认' (needs human confirmation)"]
    LADDER -->|"yes, force_confirm=true"| FORCED
    OK & FORCED --> IDX["index: SQLite FTS5 + LanceDB vectors"]
    OK & FORCED --> GIT[("git commit 'write: path'<br/>— the only record covering<br/>every mutation, and it lives<br/>outside the store")]
    IDX --> D2["D2: incremental observation<br/>collision detection (vector)"]
    D2 --> COLL[("collisions table:<br/>status open | resolved | dismissed")]
    UI["a person, in the web console:<br/>POST /api/{user}/collision"] -->|"the only caller of<br/>resolve_collision"| COLL
    COLL --> SR{"Search._warnings_for:<br/>collisions_for(path) — status defaults to 'open'"}
    SR -->|"still open"| WARN["hit carries ⚠ naming the other note<br/>— both notes are returned, always"]
    SR -->|"resolved or dismissed"| CLEAN["hit carries no warning"]
    CUR["curator, weekly: review quality,<br/>write a proposal report"] -.->|"'no write power over memories' —<br/>a person executes it by hand"| GIT
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `store.py` | CRUD, the write guards, the topic registry, git snapshots |
| `detectors.py` | Title normalisation, D1 duplicate scan, D3 dangling links — no LLM |
| `index_db.py` | SQLite: notes, FTS, collisions, guard events, embedding cache |
| `search.py` | FTS5 trigram and vector, fused by RRF, warnings attached |
| `vector.py`, `embedding.py` | LanceDB and the single 0.6B embedding call |
| `curator.py` | The weekly quality review that only proposes |
| `webui/app.py` | The console: notes, search, audit, usage, health, config |
| `usage.py` | Per-call log for the MCP transports |

## 4. Essential Implementation Paths

`detectors.py:14-43` — the suffix patterns and the similarity function. Read the
patterns first; they are the design.

`store.py:151-198` — refusal, the confirmation ladder, and what gets counted.

`search.py:107-119` and `index_db.py:231-261` — the warning, and the human
verdict that silences it.

## 5. Memory Data Model

A note is Markdown. The registry (`TOPICS.md`) names which topics are long-term,
with active and archived sections; `PROFILE.md` carries preferences injected
ahead of context. `journal/`, `archive/` and `curator/` are registration-free
areas, and journal notes are exempt from the title guard — a deliberate carve-out,
since a daily log is supposed to repeat its own titles.

Observations are parsed from `- [category] text` lines, with GFM task items
(`- [x]`) excluded so a checklist-heavy note does not manufacture collision
noise. That exclusion is a small thing, and it is the kind of small thing that
decides whether a detector is usable.

## 6. Retrieval Mechanics

FTS5 trigram — which matters for Chinese, where word boundaries are not spaces —
and vector search, fused by reciprocal rank. Then warnings are attached per hit.

The absence is the point: no filter, no tier, no decay, no status that withholds.
The README states it as a rule — the system never silently deletes or hides any
memory — and the search path matches the claim.

## 7. Write Mechanics

Covered above. `memory_edit` requires its anchor string to be unique in the file
and raises otherwise, so an edit cannot silently hit the wrong occurrence;
`memory_edit_section` addresses a heading instead. Move refuses an existing
target and re-indexes from the embedding cache rather than re-embedding.

## 8. Agent Integration

One URL per user, streamable HTTP, stateless sessions, nothing installed on the
client. For a person running several agents across several machines against one
memory, this is the least-friction shape available, and it is why the guards have
to live at the API: there is no client-side library to put them in.

The web console covers browsing and editing notes, search, a two-mode audit
(deterministic rules, and the curator's LLM review), the call log, health, and
editing `config.toml` in the browser.

## 9. Reliability, Safety, and Trust

Path traversal is refused on title-to-path conversion and on move. The store
takes an instance lock on every public method because the HTTP server runs sync
MCP tools in a threadpool. Git commits every mutation and the repository is
expected to stay clean, which is both the undo and a way to see what an agent did
without giving the agent filesystem access.

The gap to be aware of is the one named above: the complete record is git, and
the in-store records each cover a slice.

The README carries an AIGC labelling block in its front matter — a content
producer and propagation id, as Chinese regulation asks for on AI-generated
material.

## 10. Tests, Evals, and Benchmarks

95 test functions across thirteen files covering the store, guards, git
snapshots, detectors, topics, profile, search, the index, the curator, the server
and the WebUI, with a v1 suite kept under `legacy/`. `docs/06-evaluation.md`
exists; the evaluation it describes was not run here, and nothing is installed or
executed by this reading.

## 11. For Your Own Build

Normalise before you compare. A duplicate check that a trailing `-2` or a date
defeats is a check against typos, not against duplication — and the suffix list
in `detectors.py` is twenty lines that turn one into the other.

Make the bypass count itself. `force` with a 24-hour counter and a second flag
above a threshold gives you an escape hatch that stays an escape hatch. An
uncounted override becomes the default path within a week.

Consider not hiding. Presenting both sides of a contradiction with a marker, and
letting the reading model judge, is a real alternative to picking a winner at
write time — and it is only affordable because nothing here is lossy.

Let a person's dismissal stick. A warning that reappears after it has been judged
trains the reader to ignore warnings.

And if you are relying on git as your audit trail, say so plainly and keep the
in-store record honest about its scope. A table named for guards that holds only
guard events is fine; a call log that misses the console's own writes is a gap
worth closing.

## 12. Open Questions

Whether a proposal can ever be applied from inside the system. The curator will
not, by design, and no route or command was found that executes one.

What happens to a collision when the notes are merged. `remove_collisions_involving`
clears rows on delete and move, and `prune_stale_collisions` drops rows whose
notes are gone; whether an edit that resolves the overlap re-opens or clears the
row was not traced.

Whether the same fact under two unrelated titles is detected. The write guard is
title-keyed; D2 works on observation lines, and how much of a note's body it
covers was not established.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `yacmemo/detectors.py:14-43` | The suffix list, which is the whole idea |
| `yacmemo/store.py:151-198` | Refusal, the confirmation ladder, and what is counted |
| `yacmemo/search.py:107-119` | Both notes returned, one of them marked |
| `yacmemo/index_db.py:231-261` | The human verdict the search path reads |
| `yacmemo/curator.py:1-46` | A reviewer with no write power, and its review dimensions |
| `yacmemo/usage.py:1-34` | What the call log does and does not cover |

## History

**2026-09-16** — [`2440aa563e1474d5a07b16d052373c28ed8a4a7c`](https://github.com/yachen4ever/yacmemo/commit/2440aa563e1474d5a07b16d052373c28ed8a4a7c) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: ten files scanned, no auto-run surfaces, two build-time execution points, two unpinned surfaces and five dependency files inside the seven-day cooldown. Nothing was installed, built or run.

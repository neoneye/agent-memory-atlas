---
title: "Huiran-cerebro"
eyebrow: "The duplicate is retired, the first writer is kept"
description: "A single-file personal memory hub whose deduplication marks the later of two near-identical fragments merged rather than deleting it, keeps the earlier one as the source, and offers a dry run that returns the pairs before anything changes."
root: ../..
page_kind: system
source_name: "qilunuojiang9-hue/Huiran-cerebro"
source_url: https://github.com/qilunuojiang9-hue/Huiran-cerebro
archive_name: "qilunuojiang9-hue--Huiran-cerebro"
revision: 08644a7edd1bff64ba46177d069287cb1daaad7a
revision_url: https://github.com/qilunuojiang9-hue/Huiran-cerebro/commit/08644a7edd1bff64ba46177d069287cb1daaad7a
analyzed_at: 2026-09-19
capabilities: "trust_state"
capability_evidence:
  trust_state: "a stored fragment status that the recall, listing, summary and relation paths filter on, set to `merged` by the dedup pass so the row survives while leaving retrieval — and absent from the three reads that build the start-of-day context | cyber_brain.py:189-206 (the column and its index), :640-641 (`list_fragments`), :708, :779, :807, :838, :1173 (the filtered reads), :832-859 (`dedupe_fragments`), :1264-1339 (`daily_context`, the exception) | `memory_fragments.status` defaults to `active` with its own index, and six reads select `WHERE status=active`. `dedupe_fragments` marks the later writer merged and keeps the text — 重复碎片合并：内容 Jaccard >= threshold 的碎片，标记后写者 status=merged（不删原文）— with the rule for which side survives stated beside it: keep the first creator as the information source. `list_fragments` defaults to active and a caller may name another status. The exception is `daily_context`, which assembles the block a session opens with: its three fragment reads — iron rules by `source_ref`, the five most recent decisions, five high-importance fragments — carry no status predicate, so a fragment marked merged is emitted into that block under 铁律, 最近决策 and 高价值知识 | cyber_brain.py:640"
stack_storage: "sqlite"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A memory fragment — type, subject, content, entities, tags, status, source reference, embedding state, importance and namespace — beside content items, knowledge-base chunks and a typed entity graph"
  storage: "One SQLite file with FTS5 trigram tokenisation for Chinese, a reserved embedding table, and no service dependency"
  retrieval: "FTS5 trigram plus `bge-small-zh-v1.5` embeddings fused by reciprocal rank, over fragments, rolling summaries and knowledge-base chunks"
  write: "CLI subcommands, a web console, or MCP tools; content items carry a source type, a source tag and an authorization reference"
  update_delete: "A Jaccard dedup pass marks the later of two near-identical fragments `merged` and keeps its text; content items carry a version and a parent id"
  scoping: "A `namespace` column with a `default` value, passed as an optional argument — omitted, no predicate is emitted"
  integration: "An MCP server with a written guide for Doubao, a Flask-shaped web console, and Windows batch launchers"
  background: "Rolling summaries, a daily brief over unfinished work items, and the dedup pass when invoked"
  trust: "A fragment status that withholds merged duplicates from the search paths but not from the start-of-day context block, a retrieval-audit table recording what was asked, and an authorization reference on content items"
  strengths: "The dedup decision is the right one twice over. It marks rather than deletes — the docstring says 不删原文, do not delete the text — so a merge is reversible and the merged row stays inspectable, while every recall path's `status='active'` predicate keeps it out of results. And it keeps the *earlier* fragment as the surviving one, on the stated ground that the first writer is the information source, which is the opposite of the last-write-wins default and the right call when the later copy is a restatement. A `dry_run` flag returns the candidate pairs with their similarity scores and changes nothing, so the threshold can be tuned against real data before it is applied. Around that, the engineering is proportionate to its scale: one 1,734-line module holding the schema and the operations, FTS5 with trigram tokenisation because Chinese has no spaces to tokenise on, a version number with a single source of truth and a script that syncs the README badge to it, and a `doctor` command"
  risks: "There are no tests anywhere in the repository — no test directory, no test file, and the two `tools/_*_smoke.py` scripts are smoke checks rather than assertions — for a store whose dedup pass rewrites rows in place. The dedup itself is a full pairwise scan of every active fragment with a Python Jaccard per pair, so its cost grows with the square of the store; and because the scan reads only `status='active'`, a merged fragment is never compared against again, so re-adding the same text creates a fresh active row that the next pass must merge once more — the mark records a decision, and nothing consults it at write time to refuse the repeat. `daily_context` reads fragments three times with no `status` predicate, so a merged duplicate is rendered into the start-of-day block under iron rules, recent decisions and high-value knowledge — the six search paths filter and the summary does not. `namespace` is an optional argument that emits no predicate when omitted, so it separates nothing by default. The delete helper is Windows-only, calling `SHFileOperationW` with `FOF_ALLOWUNDO` to move a directory to the recycle bin, which is a thoughtful default and unavailable everywhere else. And the README carries a section addressed to LLM readers alongside an `llms.txt`, which is worth knowing about when an agent summarises this project from its own documentation"
---

## 1. Executive Summary

Huiran-cerebro (赛博大脑, "cyber brain") is a personal and team memory hub and
knowledge-base engine — MIT, Python 3.10+, version 1.5.0, 4,582 lines across a
handful of modules, one SQLite file with no service dependency. Its stated goal
is to settle an AI's memory and knowledge into a local, searchable, conversable
private knowledge base, and it ships an MCP server with a written integration
guide for Doubao, a web console, and Windows batch launchers.

The engine is four layers in one file: a knowledge base of documents and chunks,
memory fragments, a typed entity graph, and an AI conversation log, retrieved by
FTS5 with trigram tokenisation — the right choice for Chinese, which has no
spaces to tokenise on — fused with `bge-small-zh-v1.5` embeddings by reciprocal
rank.

The mechanism worth the visit is the deduplication, and it makes two good
decisions in one docstring:

> "重复碎片合并：内容 Jaccard >= threshold 的碎片，标记后写者 status='merged'（不删原文）。
> 保留先创建者（信息源），后写者合并到它。"
>
> *Merge duplicate fragments: for fragments whose content Jaccard is at or above
> the threshold, mark the later writer `status='merged'` (do not delete the
> text). Keep the first creator as the information source; the later writer is
> merged into it.*

**It marks rather than deletes**, so the duplicate stays inspectable and the
merge is reversible — and because the recall, listing, summary and relation
paths each select `WHERE status='active'` (`:708`, `:779`, `:807`, `:838`,
`:1173`, and `list_fragments` through its default at `:640`), the marked row
leaves retrieval without leaving the store. That is the trust-state mark: a
stored discrete status, set by a real mechanism, read by the paths that matter.

There is one read where it is not applied, and it is the one a session opens
with. `daily_context` (`:1264-1339`) assembles the start-of-day block, and its
three fragment queries carry no status predicate: the iron rules selected by
`source_ref LIKE 'iron_rules%'` (`:1270`), the five most recent `decision`
fragments (`:1326`), and five `importance='high'` fragments (`:1334`). Each is
rendered straight into the block — `[铁律]`, `[提醒·最近决策]`, `[提醒·高价值知识]` —
so a fragment the dedup pass marked `merged` comes back in all three, which is
the one thing marking it was meant to prevent. The six filtered reads are the
searches; the three unfiltered ones are the summary a person reads first. That
asymmetry recurs across this corpus and is worth stating plainly: the search
path is the one with a predicate because it is the one anyone thinks of as
retrieval, and the context builder returns prose rather than rows, so nothing
about it looks like a query.

**And it keeps the earlier fragment**, on the stated ground that the first writer
is the information source. Last-write-wins is the default almost everywhere, and
it is the wrong default when the later copy is a restatement of the earlier one
rather than a correction of it.

A `dry_run` flag returns the candidate pairs with their similarity scores and
changes nothing, so the threshold can be tuned against real data before it is
applied to it. Small, and more than many larger systems here offer.

What to weigh against that. **There are no tests** — no test directory, no test
file, and the two `tools/_*_smoke.py` scripts are smoke checks rather than
assertions — under a pass that rewrites rows in place. The dedup is a full
pairwise scan of every active fragment with a Python Jaccard per pair, so its
cost grows with the square of the store. And because the scan reads only active
rows, a merged fragment is never compared against again: re-adding the same text
creates a fresh active row that the next pass must merge all over again. The mark
records a decision; nothing consults it when the next write arrives, so it is a
retirement rather than a refusal.

`namespace` exists on fragments and entities with a `default` value, and is
passed as an optional argument that emits no predicate when omitted — so it
separates nothing unless a caller asks it to.

Two details for a reader coming from elsewhere. The delete helper is Windows-only,
calling `SHFileOperationW` with `FOF_ALLOWUNDO` so a removed directory lands in
the recycle bin rather than vanishing — a thoughtful default that does not exist
on other platforms. And the README carries a section explicitly addressed to LLM
readers, alongside an `llms.txt`, which is worth knowing when an agent summarises
this project from its own documentation rather than from its code.

## 2. Mental Model

A **fragment** is a small remembered thing, and it is either active or it has
been merged into an earlier one.

**Merged** means retired from recall, not gone.

The **first writer wins**, because the first writer is the source.

```mermaid
%% caption: the dedup pass marks the later of two near-identical fragments merged and keeps its text, and every recall path's status='active' predicate is what removes it from results
flowchart TB
    W["add a fragment — CLI, web console, or MCP"] --> ROW[("memory_fragments:<br/>type · subject · content · entities ·<br/>tags · status='active' · source_ref ·<br/>importance · namespace")]
    DED["dedupe_fragments(threshold, dry_run)"] --> SCAN["read every row WHERE status='active'<br/>AND length(content) >= 8, oldest id first"]
    SCAN --> PAIR{"pairwise: identical content,<br/>or Jaccard >= threshold?"}
    PAIR -->|"no"| KEEP["both stay active"]
    PAIR -->|"yes, dry_run"| CAND["return the pair with its score;<br/>change nothing"]
    PAIR -->|"yes"| MARK["UPDATE the LATER row:<br/>status='merged'<br/>— '不删原文', the text is not deleted;<br/>the first creator is kept as the source"]
    MARK --> ROW
    ROW --> R{"recall · list · summary · relations"}
    R -->|"every path"| F["WHERE status='active'"]
    F --> OUT["results: FTS5 trigram +<br/>bge-small-zh embeddings, fused by RRF"]
    MARK -.->|"merged rows are excluded from the<br/>next scan, so re-adding the same text<br/>makes a new active row the next pass<br/>must merge again"| SCAN
    NS["namespace — default 'default',<br/>an optional argument"] -.->|"omitted ⇒ no predicate emitted"| R
```

## 3. Architecture

| File | Role |
| --- | --- |
| `cyber_brain.py` | The schema, the store, search, recall, dedup, summaries |
| `web_ui.py` | The browser console |
| `mcp_server.py` | The MCP surface |
| `session_log.py`, `summarize.py`, `daily_brief.py` | Session capture, rolling summaries, a daily brief |
| `doctor.py`, `tools/check_version.py` | Diagnostics, and a version badge kept in sync |

## 4. Essential Implementation Paths

`cyber_brain.py:832-859` — the dedup, its docstring, and its dry run.

`cyber_brain.py:189-206` — the fragment schema and the status index.

`cyber_brain.py:708`, `:779`, `:807`, `:1173` — the four places the predicate is
repeated.

## 5. Memory Data Model

Fragments carry a type, a subject, entities, tags, a status, a source reference,
an embedding state, an importance and a namespace. Content items carry more:
a status of draft or done, a version and a parent id forming a revision chain, a
source type, a source tag and an `authorization_ref` defaulting to `manual` —
provenance fields that are recorded and, as far as this reading found, not yet
consulted by a read.

Rolling summaries carry a scope key and a checkpoint version, which is how the
system keeps a compacted account of a long stretch without losing the fragments
underneath it.

## 6. Retrieval Mechanics

FTS5 trigram and embeddings fused by reciprocal rank, with the active-status
predicate repeated at each site rather than centralised — four copies of one
rule, which is the shape that drifts. A retrieval-audit table records what was
asked and in what mode.

## 7. Write Mechanics

Direct inserts; dedup is an explicit pass rather than a write-time check. That
ordering is the trade-off: writes stay cheap and unconditional, and duplicates
accumulate until someone runs the pass.

## 8. Agent Integration

An MCP server with a document walking through connecting Doubao, plus a web
console and CLI. `add_content` takes a status defaulting to `draft`, so an agent's
write lands as a draft unless it says otherwise — a small default in the right
direction.

## 9. Reliability, Safety, and Trust

The merge-not-delete rule is the substance. Beyond it: a `doctor` command, a
version constant with a script that syncs the README badge to it, and a
recycle-bin delete on Windows.

The absence to weigh is testing. A pass that rewrites status in place, over a
store whose whole value is that nothing was lost, is the code most in need of a
test that a merged fragment is absent from recall and its content still in the
table.

## 10. Tests, Evals, and Benchmarks

None found. Two smoke scripts under `tools/` exercise the frontend and the graph
without asserting outcomes. Nothing was installed or run for this reading.

## 11. For Your Own Build

Mark, do not delete, and say so in the docstring. A duplicate marked `merged`
with its text intact can be reviewed, reversed and counted; a deleted one cannot.

Decide which side of a duplicate survives, and write down why. "Keep the first
creator, it is the information source" is a rule a reader can argue with, which
is more than a silent last-write-wins offers.

Ship the dry run with the destructive pass, not after it. Returning the candidate
pairs and their scores is what makes a threshold tunable.

And put the status predicate in one place. Four copies of `status='active'` is
four chances for the next read path to forget it.

## 12. Open Questions

Whether `authorization_ref` and `source_tag` are consulted anywhere. Both are
written with defaults and no reader was found.

What `embedding_state` gates. It defaults to `disabled` on every fragment, and
how the embedding path treats that was not traced.

Whether a merged fragment can be restored. The row and its text survive; no
command to set the status back was found.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `cyber_brain.py:832-859` | Mark rather than delete, keep the first writer, and a dry run |
| `cyber_brain.py:189-206` | The fragment, and the index the predicate needs |
| `cyber_brain.py:78-101` | Provenance fields on a content item, awaiting a reader |
| `tools/recycle_delete.py` | A delete that lands in the recycle bin, on one platform |

## History

**2026-09-19** — [`08644a7edd1bff64ba46177d069287cb1daaad7a`](https://github.com/qilunuojiang9-hue/Huiran-cerebro/commit/08644a7edd1bff64ba46177d069287cb1daaad7a) — `trust_state` re-tested at an unchanged pin, and the record's universal claim did not survive it. Every anchor held: the column and its index, `dedupe_fragments` marking the later writer merged without deleting the text, and the filtered reads at `:708`, `:779`, `:807`, `:838` and `:1173`, with `list_fragments` defaulting to active at `:640`. Six reads filter. The seventh is `daily_context` (`:1264-1339`), which assembles the block a session opens with, and its three fragment queries carry no status predicate — iron rules by `source_ref` (`:1270`), the five most recent decisions (`:1326`) and five high-importance fragments (`:1334`), each rendered straight into the block. So a fragment marked merged is withheld from every search and returned in the summary a person reads first, which is the one thing marking it was meant to prevent. The mark stands on the six; the record now names the seventh beside it. This is the third system in one sweep where the missing predicate was in the session-start context builder rather than in a search path, which is worth saying out loud: the context builder returns prose rather than rows, so nothing about it looks like a query. Re-read from a fresh clone; nothing was installed and no suite was run.

**2026-09-16** — [`08644a7edd1bff64ba46177d069287cb1daaad7a`](https://github.com/qilunuojiang9-hue/Huiran-cerebro/commit/08644a7edd1bff64ba46177d069287cb1daaad7a) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: two files scanned, no auto-run surfaces, no build-time execution points, one unpinned surface and one dependency file inside the seven-day cooldown. Nothing was installed, built or run.

---
title: "Memobase"
eyebrow: "Structured user profiles"
description: "A Postgres profile service that compiles chat into a small topic-indexed memo per user, where scope is part of the primary key and the raw transcript is deleted by default."
root: ../..
page_kind: system
source_name: "memodb-io/memobase"
source_url: https://github.com/memodb-io/memobase
revision: 358c16bbc6d687937d79bc2f984a11c3be8da901
revision_url: https://github.com/memodb-io/memobase/commit/358c16bbc6d687937d79bc2f984a11c3be8da901
analyzed_at: 2026-07-29
capabilities: "scope_enforced"
stack_storage: "postgres"
stack_retrieval: "vector"
stack_source: "seeded"
matrix:
  memory_unit: "A free-text memo of at most five sentences, keyed by topic and subtopic, plus tagged events and their embedded gists"
  storage: "Postgres with pgvector; composite (id, project_id) primary keys on all seven memory tables"
  retrieval: "Profiles selected by topic preference and token budget; events by tag filter and gist embedding similarity"
  write: "Buffered — blobs queue in buffer_zones until a token threshold or a one-hour flush, then one LLM extract-and-merge pass"
  update_delete: "An LLM rewrites the memo in place (APPEND / UPDATE / ABORT); no prior value is retained"
  scoping: "project_id and user_id in every memory table's primary key, foreign key, index, read-path filter and Redis cache key"
  integration: "REST API with Python, TypeScript and Go clients, an MCP server, and an OpenAI-compatible wrapper"
  background: "Buffer flush, plus organize_profile when a topic exceeds max_profile_subtopics"
  trust: "None represented; a memo is a string, and a rewrite leaves no record of what it replaced"
  risks: "persistent_chat_blobs defaults to false, so the source transcript is hard-deleted after extraction"
  strengths: "Scope is structurally impossible to omit; context assembly has a real token budget and a profile/event split"
---

## 1. Executive Summary

Memobase is a user-profile service. You post chat transcripts to it, and it
maintains a compact, topic-indexed set of memos about each user — "basic_info /
name", "interest / books", "psychological / goal" — plus a stream of tagged
events. On retrieval you ask for a *context block* sized to a token budget, and it
returns a rendered profile and a selection of events to paste into a system
prompt.

The design commitment is bluntly stated in the code: a memo is capped at five
sentences by prompt instruction, a topic is capped at
`max_profile_subtopics = 15` before a reorganize pass merges it down, and
`max_pre_profile_token_size = 128`. Memobase is not trying to remember what
happened. It is trying to maintain the smallest description of a user that is
still useful, and to make that description cheap enough to inject on every turn.

**What is genuinely good is the scoping.** All seven memory tables —
`users`, `general_blobs`, `buffer_zones`, `user_profiles`, `user_events`,
`user_event_gists`, `user_statuses` — declare
`PrimaryKeyConstraint("id", "project_id")`, every foreign key between them is
the composite `(user_id, project_id)`, and every index leads with those
columns. The two exceptions are the account tables and prove the rule:
`Project`'s primary key is `project_id` alone and `Billing`'s is `id`, because
neither sits inside a tenant. Scope is not a field someone remembered to filter
on — it is the memory row's identity, so writing a query that crosses a tenant
boundary takes effort. Of the systems in this atlas that enforce scope, this is the
most structural implementation.

**What is weakest is that nothing survives a bad extraction.**
`persistent_chat_blobs` defaults to `False`, and on buffer flush the source chat
blobs are hard-deleted from Postgres
(`src/server/api/memobase_server/controllers/buffer.py:211`). The profile is a
string that an LLM rewrites in place. There is no prior value, no supersession
record, no confidence, and no evidence to re-derive from. If the extractor gets a
user's job wrong, the wrong answer is the only answer the system has ever had.

## 2. Mental Model

A memory in Memobase is a **memo**: a short piece of free text filed under a
`(topic, subtopic)` pair, with the whole set constituting the user's profile.

```text
UserProfile
  content     TEXT     -- the memo, ≤ 5 sentences by prompt instruction
  attributes  JSONB    -- {topic, sub_topic, ...}

UserEvent       event_data JSONB, with event_tags
UserEventGist   gist_data JSONB + embedding — the searchable unit
UserStatus      typed attributes
GeneralBlob     the raw material — deleted after processing by default
BufferZone      blobs awaiting processing
```

The life of a memo is a three-way decision made by one LLM call, and the
vocabulary comes straight from
`src/server/api/memobase_server/prompts/merge_profile.py`:

```mermaid
%% caption: three merge verdicts, one of which rewrites the memo so the previous text ceases to exist
flowchart TB
    N["new information about<br/>(topic, subtopic)"] --> M{"merge_profile"}
    M -->|APPEND| A["the memo did not exist,<br/>or this is additive"]
    M -->|UPDATE| U["rewrite the memo —<br/><b>old text ceases to exist</b>"]
    M -->|ABORT| AB["discard the new information"]

    style U fill:#f4e2bd,stroke:#b8860b
```

Three verdicts from one model call. `UPDATE` is the lossy one: the memo is
rewritten and the previous wording is gone, so a wrong merge cannot be walked
back.

That is the entire epistemic model, and both of its ends are worth naming. `ABORT`
discards *incoming* information with no record that it was seen — so a fact the
extractor judged valueless cannot be recovered or reconsidered. `UPDATE` discards
*existing* information by overwriting the string, and the prompt actively
encourages it: "also think about whether there are other parts of the current memo
that can be simplified or removed."

Memory is **background-managed and application-triggered**. The application posts
blobs; everything else happens on the server's schedule. A developer can write
profiles directly through the API, but nothing in the system distinguishes a memo
a human wrote from one the extractor produced.

There is one place the system knows time matters and declines to model it. The
merge prompt instructs: "Preserve time annotations from both old and new memos
(e.g.: XXX[mentioned on 2025/05/05, occurred in 2022])." That is *exactly* the
distinction [bi-temporal fact validity](../../patterns/bi-temporal-fact-validity/)
is about — when it was said versus when it was true — and it lives inside a text
string, maintained by asking a language model nicely, queryable by nothing.

## 3. Architecture

```mermaid
%% caption: blobs buffer until a token threshold flushes them through extract-merge-organize, and the source blob is deleted afterwards unless chat persistence is on
flowchart LR
    APP["app / SDK / MCP"] -->|insert blob| API["FastAPI<br/>memobase_server"]
    API --> BLOB[("general_blobs")]
    API --> BUF[("buffer_zones")]
    BUF -->|token threshold<br/>or flush| EX["extract → merge → organize"]
    EX --> PROF[("user_profiles")]
    EX --> EV[("user_events<br/>user_event_gists")]
    EX -.->|delete unless<br/>persistent_chat_blobs| BLOB
    API -->|get_user_context| CTX["context assembly<br/>profile + events,<br/>token-budgeted"]
    PROF --> CTX
    EV --> CTX
```

- **Runtime** is a single FastAPI service plus Postgres with `pgvector`. Redis
  appears for buffer coordination. There is no queue broker and no separate worker
  image — background work runs in-process off the API
  (`controllers/buffer_background.py`).
- **Clients** are first-class and plural: Python, TypeScript (npm and JSR), Go, an
  MCP server under `src/mcp/`, and an OpenAI-compatible wrapper
  (`assets/openai_memory.py`) that transparently adds memory to chat completions.
- **Configuration** is a single `config.yaml`, with worked examples committed under
  `src/server/api/example_config/` for education, companion and assistant profile
  schemas — a better onboarding story than most of this atlas.

### Deployment and ergonomics

One service and one database. That is a genuinely modest ask, and materially
cheaper than [MIRIX](../mirix/)'s four containers for a comparable job.

An LLM key is required to store anything durable — blobs land without one, but
nothing becomes a profile until the extractor runs, so an outage means the buffer
grows and recall returns the last flushed state. There is no
[zero-LLM capture](../../patterns/zero-llm-capture/) path.

The store is human-readable and repairable by hand: profiles are rows of text in
Postgres, and the profile API supports direct add, update and delete. That is a real
operational advantage over graph-shaped systems. What you cannot repair by hand is a
bad extraction whose source blob has already been deleted.

## 4. Essential Implementation Paths

**Capture** — `api_layer/blob.py` → `controllers/blob.py`. A blob is written to
`general_blobs` and an entry to `buffer_zones` with its `token_size`. The write
returns immediately; nothing has been extracted yet.

**Flush** — `controllers/buffer.py`. The buffer is processed when accumulated
tokens exceed `max_chat_blob_buffer_token_size` (default 1024) or when
`buffer_flush_interval` (default `60 * 60` — one hour) elapses;
`max_chat_blob_buffer_process_token_size` (16384) caps a single processing batch.
On success the buffer rows are marked `BufferStatus.done` and, unless
`CONFIG.persistent_chat_blobs` is set, the source blobs are deleted (line 211).

**Extraction and merge** — `controllers/modal/chat/`: `extract.py` →
`merge_yolo.py` → `organize.py` → `event_summary.py`. Two merge
implementations are committed and only one is wired: `chat/__init__.py:14`
carries `# from .merge import merge_or_valid_new_memos` commented out above
`from .merge_yolo import merge_or_valid_new_memos` on line 15, so `merge.py`
is unreachable and the batched path is the merge path. The prompts are
separate and readable: `prompts/extract_profile.py`, `prompts/merge_profile.py`,
`prompts/merge_profile_yolo.py`, `prompts/organize_profile.py`,
`prompts/event_tagging.py`, each with a Chinese counterpart (`zh_*`).

**Retrieval and context assembly** — `controllers/context.py:115`,
`get_user_context()`. It splits the caller's `max_token_size` by
`profile_event_ratio`, then runs `get_user_profiles_data()` and
`get_user_event_gists_data()` **in parallel** via `asyncio.gather`, and renders
both through a language-specific prompt pack.

**Update/delete** — `api_layer/profile.py` exposes `get_user_profile`,
`add_user_profile`, `update_user_profile`, `delete_user_profile` and
`import_user_context`. Profile reads filter on both scope columns —
`get_user_profiles()` at `controllers/profile.py:75` does
`.filter_by(user_id=user_id, project_id=project_id)` at line 95 — and the
bulk delete at `controllers/profile.py:206` carries the same pair alongside
the id list.

**Schema** — `models/database.py`: `Project`, `User`, `GeneralBlob`, `BufferZone`,
`UserProfile`, `UserEvent`, `UserEventGist`, `UserStatus`.

## 5. Memory Data Model

The scoping model is the thing to study. `UserProfile.__table_args__` is
representative:

```python
PrimaryKeyConstraint("id", "project_id"),
Index("idx_user_profiles_user_id_project_id", "user_id", "project_id"),
ForeignKeyConstraint(
    ["user_id", "project_id"], ["users.id", "users.project_id"],
    ondelete="CASCADE", onupdate="CASCADE",
),
```

`project_id` is in the primary key, in every index and in every foreign key. Every
other memory table follows the same shape. The consequence is that
[scope as a first-class key](../../patterns/scope-as-a-first-class-key/) is not a
discipline the developers have to maintain — the schema will not let them forget
it, and a cascade delete of a project actually removes its memory rather than
orphaning it.

The scope also reaches past the schema into the cache, which is the part this
atlas's [rubric](../../methodology/atlas-rubric/) names as the usual blind spot
behind a `scope_enforced` mark. `get_user_profiles()` keys Redis on
`user_profiles::{project_id}::{user_id}` (`controllers/profile.py:78`), and
`refresh_user_profile_cache()` at line 220 deletes that same composite key
after every add, update and delete. There is no cache entry keyed on
`user_id` alone for a second tenant to collide with.

What the model does *not* have is anything above the string. `UserProfile` is
`content TEXT` plus an `attributes` JSONB carrying topic and subtopic. There is no
validity-versus-record time distinction, no version, no `superseded_by`, no source
pointer back to the blob it came from, no confidence, and no status. A search
across `models/` and `controllers/` for `tombstone`, `rejected`, `trust`,
`confidence`, `valid_from`, `audit`, `approve` or `review` returns nothing.

Events are better provenanced than profiles: `UserEventGist` carries an `event_id`
foreign key back to the `UserEvent` it summarizes, plus its own `embedding`. So the
gist — the retrievable unit — can always be traced to the full event. Profiles get
no equivalent link, which is backwards: the profile is the thing most likely to be
wrong.

## 6. Retrieval Mechanics

Two retrieval paths, deliberately different, assembled together.

**Profiles are not searched, they are selected.** `get_user_profiles_data()` takes
`prefer_topics`, `only_topics`, `topic_limits` and `max_subtopic_size`, and fills a
token budget. This is the right call for a profile: you want the same stable
description every turn, not a similarity-ranked sample of it that changes depending
on what the user just said.

**Events are searched**, by tag filter (`has_event_tag`, `event_tag_equal`) and by
gist embedding against `event_similarity_threshold`, restricted to
`time_range_in_days`.

The split is governed by `profile_event_ratio`, asserted at the top of
`get_user_context()` to lie in `(0, 1]`, and the two halves are fetched
concurrently. `fill_window_with_events` lets the event half absorb whatever the
profile half did not use.

This is one of the better context assemblies in the atlas, for a specific reason:
the token budget is a parameter of the retrieval call rather than a truncation
applied afterwards. Most systems here return *k* rows and let the caller discover
the size.

The failure modes are the ones the design accepts. A capped profile cannot
represent a user with many stable traits; `only_topics` will silently starve a
question whose answer sits in an excluded topic; and because profiles are selected
rather than searched, a memo that is present but filed under an unexpected subtopic
is unreachable by relevance.

## 7. Write Mechanics

The write path is **buffered, batched and rewriting**.

Buffered: `POST` a blob and it lands in `general_blobs` and `buffer_zones`
immediately. Nothing is retrievable from it yet.

Batched: the buffer flushes at 1024 accumulated tokens or after one hour. For a
low-traffic user this is the operative number — **a fact stated now may not be
recallable for an hour.** The atlas's [benchmarks page](../../benchmarks/) notes
that the lag between writing and being able to recall is measured nowhere; Memobase
is the clearest instance in the corpus, because the lag is not an emergent property
but a documented default with a name.

Rewriting: `merge_profile` returns `APPEND`, `UPDATE\t[UPDATED_MEMO]`, or `ABORT`,
parsed on an `llm_tab_separator` (`::`). `UPDATE` carries the complete new memo, and
the controller writes it over the old `content`. The wired variant,
`merge_profile_yolo`, uses the identical three-verdict vocabulary and the same
five-sentence cap; what it changes is the batching — every extracted memo in a
flush is numbered into one prompt and the model answers `N. VERDICT{tab}…` per
line, so a flush costs one merge call rather than one per memo. Nothing checks that the rewrite
retained the facts the old memo held, which is the check the atlas's
[structural-loss guard on generated
rewrites](../../compare/#structural-loss-guard-on-generated-rewrites) exists for.

A second rewriting pass, `organize_profile`, fires when a topic exceeds
`max_profile_subtopics` (15) and merges subtopics into fewer, broader ones. Its
committed few-shot example (`prompts/organize_profile.py:9-29`) shows eleven
subtopics collapsing into three — `上岛冒险`, `休息`, `逃离` — and two of the
eleven, `下雨` and `到达新地方`, appear nowhere in the output at all. That is
deliberate: the prompt's first bullet is "You can discard some memos if they're
not relevant to the topic." So the pass is not only a merge, it is a merge with
an unlogged drop, and the compression is aggressive by design.

Two config flags gate how much LLM judgement a write gets, and they are
different knobs. `profile_strict_mode` constrains extraction to the configured
topic list, so with it on the extractor cannot invent a schema.
`profile_validate_mode` (`env.py:118`, default `True`) decides whether a memo
at a *new* `(topic, subtopic)` key goes through the merge model at all: at
`merge_yolo.py:35-37` it is read as a per-project override falling back to
`CONFIG`, and when it is false, the subtopic definition carries no
`validate_value` and no profile exists at that key, the memo is appended
straight to the `add` list with a `Skip validation` trace and no model call
(`merge_yolo.py:56-72`; the unwired `merge.py:82-98` holds the identical
branch). Turning it off is a real cost saving and it removes the only gate that
can `ABORT` a first-time claim.

### Operational cost

- **Synchronous?** No. Blob insert returns before extraction.
- **Lag?** Bounded by `buffer_flush_interval`, default **one hour**, or by 1024
  accumulated tokens, whichever comes first. This is the atlas's clearest committed
  answer to a question it says nobody answers.
- **Whole-store passes?** No global pass. `organize_profile` rewrites one topic at a
  time when it crosses the subtopic cap, so cost scales with churn rather than with
  corpus size — a better shape than the nightly-everything designs elsewhere in this
  atlas.
- **Read path?** Explicitly budgeted by `max_token_size` and split by
  `profile_event_ratio`. Because the profile block is stable across turns and
  injected at the front, it is friendlier to prompt-prefix caching than a
  similarity-ranked block would be.

## 8. Agent Integration

Integration is the strongest non-memory part of this project. Four clients (Python,
TypeScript, Go, MCP), an OpenAI-compatible drop-in wrapper, and committed example
configs for three product shapes. The MCP server under `src/mcp/` is what you would
wire into an agent host.

Model agency over memory is **low**, and this is a design choice rather than an
omission. The agent does not call `remember` or `forget`. The application posts
transcripts and asks for a context block; what is worth keeping is decided by
server-side prompts under a configured topic schema. For a product team that wants
consistent user modelling across many conversations, that is the right allocation.
For an agent that should be able to act on "forget that", it is the wrong one —
there is no tool for the model to reach.

## 9. Reliability, Safety, and Trust

Uncertainty cannot be represented. A memo is a string; the merge prompt says "Never
make up content not mentioned in the input" and that is the whole defence.

Prompt injection has a direct route to persistence: text in an ingested transcript
is what the extractor reads, and a message crafted to look like a stated user
preference will be filed as one. With `profile_strict_mode` off it can also create
new subtopics. Nothing downstream marks a memo as model-derived.

Multi-tenancy is strong, for the structural reason in section 5. Deletion of a
project or user cascades properly through every memory table.

Privacy semantics have an unusual shape worth stating plainly, because it cuts both
ways. `persistent_chat_blobs = False` means raw transcripts do not accumulate —
which is a *good* default for a service holding other people's conversations, and
several systems in this atlas would be better off with it. It is simultaneously the
reason the system cannot repair itself: the profile is a lossy derivation and the
source is gone, so the atlas's [evidence before
belief](../../patterns/evidence-before-belief/) pattern is not merely unimplemented
here but deliberately inverted. Both readings are correct; which one matters depends
on whether you fear leaking transcripts more than you fear an unfixable profile.

The remaining data-loss risk is the buffer. Blobs sit in `buffer_zones` awaiting a
flush, and extraction runs in-process off the API service. A failure mid-flush is
handled by the session rollback, but what happens to a half-processed batch across a
restart was not traced.

## 10. Tests, Evals, and Benchmarks

Server tests are `src/server/api/tests/`: `test_api.py`, `test_controller.py`,
`test_db.py`, `test_chat_modal.py`, `test_summary_modal.py`. Client suites exist for
Python, TypeScript and Go. Coverage is real but shallow on the parts that matter —
the tests exercise API shape, filter correctness and event tagging, not extraction
quality or merge behaviour under contradiction.

`test_controller.py` contains assertions that *look* like negative retrieval
assertions and are not, and the distinction is worth recording because it is where
the atlas's rubric earns its strictness. Lines 347–361 assert that filtering by a
non-existent tag, or by `emotion=angry` when no event carries it, returns zero
events. No particular material is being excluded — the filter simply has no matches.
Compare [MIRIX](../mirix/), which creates a specific memory under one scope, queries
under another, and asserts *that memory's id* is absent from the result. The first
tests that a filter does not over-return; only the second asserts that named
material must not be retrieved. **`negative_eval` is withheld.**

`docs/experiments/900-chats/` holds a ShareGPT-derived transcript set, and
`docs/experiments/locomo-benchmark/` holds the LoCoMo number and the artifacts
behind it. That is unusually complete for this atlas and it is worth judging on
what it does and does not establish.

**What is committed.** A full harness — `run_experiments.py` dispatching over
six techniques, `evals.py` scoring BLEU, F1 and an LLM judge, `generate_scores.py`
aggregating by category, `metrics/llm_judge.py`, `prompts.py`, and
`src/{memobase_client,memzero,zep,openai,rag,langmem}` adapters — forked, per
its README's first line, from
[mem0's evaluation directory](https://github.com/mem0ai/mem0/tree/main/evaluation)
at commit `393a4fd5a6cfeb754857a2229726f567a9fadf36`. Under `fixture/memobase/`
are four result files, two per version: `results_0503_3000.json` and
`memobase_eval_0503_3000.json` for v0.0.32, `results_0710_3000.json` and
`memobase_eval_0710_3000.json` for v0.0.37. The eval files carry 1,540 graded
questions across the ten LoCoMo conversations (category 5, the adversarial set,
is skipped by `evals.py`), and re-aggregating
`memobase_eval_0710_3000.json` by hand reproduces the README's table exactly:
single-hop 0.7092 over 282 questions, temporal 0.8505 over 321, multi-hop
0.4688 over 96, open-domain 0.7717 over 841, **overall LLM-judge 0.7578**. The
number is an artifact, and it is one a reader can recompute offline from the
committed file with no API key.

**The `results_*.json` files are the better artifact and are 35 MB each,**
because each of the 1,540 records carries not just question, gold answer and
response but `speaker_1_memories` and `speaker_2_memories` — the exact rendered
profile block that was in front of the answering model — plus
`speaker_1_memory_time`, `speaker_2_memory_time` and `response_time`. Almost
nothing else in this atlas commits the retrieved context per question. It makes
a wrong answer attributable: you can read the memo the model was given and see
whether the failure was retrieval or reading. Median `response_time` in the
v0.0.37 file is 1.383 s and median `speaker_1_memory_time` 0.972 s.

**What it does not establish, and the caveats are load-bearing.** The
comparison rows are not run here — the README states plainly that the other
methods' figures are pasted from the Mem0 paper
([arXiv:2504.19413](https://arxiv.org/abs/2504.19413)), so this is a vendor
running its own system on a fork of a competitor's harness and transcribing the
competitor's published baselines beside it. A later note in the same README
records that the Zep row was superseded by figures the Zep team supplied, which
move Zep from 65.99 to 75.14 overall — 0.64 points behind the bolded Memobase
v0.0.37 figure rather than 9.79, and ahead of it on single-hop (74.11 to 70.92)
and by 19 points on multi-hop. The run is single — no repeats, no variance, against
[Zep](../zep/)'s ten runs per configuration on the same dataset. And the
configuration is bespoke: `src/memobase_client/config.yaml` sets
`overwrite_user_profiles` to five hand-written topics and twenty subtopics
fitted to LoCoMo's conversations (`personal_narrative / identity_journey`,
`personal_narrative / self_acceptance`), replacing the eight shipped defaults in
`prompts/user_profile_topics.py` outright, and `memobase_search.py` reads a
3,000-token context. `memobase_add.py` calls `insert(..., sync=True)` and
`flush(sync=True)`, so the benchmark never experiences the buffer lag that
section 7 identifies as the operative cost for a real user. The judge is
`gpt-4o-mini` at `metrics/llm_judge.py:43`, not the `gpt-4o` the README's
explanatory aside names.

None of that is misconduct — the artifacts are there precisely so it can be
checked, which is more than most published memory benchmarks allow. It does
mean the headline 75.78 is a number about Memobase under a schema written for
this dataset, graded once, beside baselines nobody re-ran.

The test I would want: post a fact, flush, post a contradicting fact, flush, and
assert what the profile says and whether anything records that the first value was
ever held. Nothing of that shape exists, and the honest answer from reading the code
is "the second value, and no".

## 11. For Your Own Build

### Steal

- **Put the tenant key in the primary key.** `PrimaryKeyConstraint("id",
  "project_id")` with composite foreign keys throughout is the cheapest way to make
  a scope leak a schema error rather than a code-review responsibility. It costs
  nothing at design time and cannot be retrofitted cheaply.
- **Make the token budget a parameter of retrieval, not a truncation after it.**
  `get_user_context(max_token_size, profile_event_ratio)` lets the caller say what it
  can afford and lets the assembler decide what fits. Returning *k* rows and hoping
  is the common alternative, and it is worse.
- **Select profiles; search events.** Stable user description and episodic recall
  want different retrieval, and running them concurrently against one budget is a
  clean way to express that.
- **Ship worked config examples.** Three committed profile schemas for three product
  shapes do more for adoption than a page of documentation, and they make the
  topic-schema idea legible.

### Avoid

- **Do not let an LLM rewrite the only copy.** `UPDATE\t[UPDATED_MEMO]` overwrites
  the memo with a regenerated string and nothing checks what was lost. If you must
  regenerate, keep the previous version, or assert that the new one still contains
  the facts you can enumerate.
- **Do not delete the evidence and keep only the derivation.** Whichever way you
  resolve the privacy tension in section 9, resolve it *knowingly* — a default that
  discards source material is a decision that the profile can never be repaired, and
  it does not look like one in a config file.
- **Do not put a temporal distinction inside a text field.** "[mentioned on
  2025/05/05, occurred in 2022]" is two columns wearing a disguise. It cannot be
  filtered, sorted or corrected, and it survives only as long as the next rewrite
  chooses to copy it.
- **Do not let `ABORT` be silent.** Discarding incoming information is a decision;
  if nothing records that it happened, nobody can audit what the extractor refused.

### Fit

Memobase suits a product team building a *personalized consumer application* —
companion, tutor, assistant — that wants a stable user description injected on every
turn at a predictable token cost, with one service and one database to run. Within
that brief it is well-judged: the caps are deliberate, the config surface is small,
the client story is unusually complete, and the scoping is the best in this atlas.

It is the wrong choice wherever the memory needs to be *accountable*. Anything that
must answer "why do you believe that?", "where did that come from?" or "forget that
permanently" has nowhere to stand here — the evidence is deleted, the provenance is
absent, and correction is a rewrite. That is not an oversight to be patched; it
follows from the decision to keep the profile small and cheap, and reversing it
means a different data model.

Walk away if your users can dispute what the system believes about them and expect
the dispute to stick.

## 12. Open Questions

- **What happens to a half-processed buffer across a restart?** `BufferStatus` has
  the states; the recovery path was not traced.
- **Why is `merge.py` kept in the tree with its import commented out?** The
  per-memo merge path is complete and unreachable, and whether it is a rollback
  lever, an A/B remnant or a path the hosted service still runs is not
  answerable from this repository.
- **Is there a retention or decay policy for events?** `time_range_in_days` bounds
  *retrieval*; no pruning of `user_events` was found.
- **Do the hosted playground and the OSS server behave identically on profile
  updates?** The atlas can only speak to the committed code.

## Appendix: File Index

**Storage/schema** — `src/server/api/memobase_server/models/database.py`,
`build_init_sql.py`, `alembic.ini`

**Write path** — `controllers/blob.py`, `controllers/buffer.py`,
`controllers/buffer_background.py`,
`controllers/modal/chat/{extract,merge,merge_yolo,organize,event_summary}.py`

**Prompts** — `prompts/extract_profile.py`, `prompts/merge_profile.py`,
`prompts/organize_profile.py`, `prompts/event_tagging.py`,
`prompts/user_profile_topics.py`

**Retrieval / context assembly** — `controllers/context.py`,
`controllers/profile.py`, `controllers/event.py`, `controllers/event_gist.py`,
`prompts/chat_context_pack.py`

**API/SDK** — `api_layer/{blob,profile,event,user,project,context}.py`, `src/mcp/`,
`src/client/`, `assets/openai_memory.py`

**Config** — `memobase_server/env.py`, `example_config/`

**Tests** —
`src/server/api/tests/{test_api,test_controller,test_db,test_chat_modal}.py`,
`src/client/tests/`

**Evals** — `docs/experiments/locomo-benchmark/{run_experiments,evals,generate_scores}.py`,
`metrics/llm_judge.py`, `src/memobase_client/{memobase_add,memobase_search}.py`,
`src/memobase_client/config.yaml`, `fixture/memobase/*.json`;
`docs/experiments/900-chats/`

## History

**2026-08-31** — [`358c16bbc6d687937d79bc2f984a11c3be8da901`](https://github.com/memodb-io/memobase/commit/358c16bbc6d687937d79bc2f984a11c3be8da901) — same pin, five corrections, the first of them load-bearing and wrong in the direction of asserting an absence. Section 10 said no LoCoMo harness or result was committed and used that to discount the published number as a claim rather than an artifact. `docs/experiments/locomo-benchmark/` is a full harness forked from mem0's evaluation directory, with four committed result files under `fixture/memobase/`; re-aggregating `memobase_eval_0710_3000.json` reproduces the README's 75.78 overall across 1,540 graded questions, and the 35 MB `results_*.json` files carry the rendered memory block and per-question latency that produced each answer. Section 10 judges it on its merits instead — a single vendor-run pass under a topic schema written for the dataset, with the baseline rows transcribed from the Mem0 paper rather than re-run. `profile_validate_mode` was called possibly-dead configuration; it is consumed at `merge_yolo.py:35-37` and `merge.py:82-98` and gates whether a first-time memo reaches the merge model at all, so the open question is dropped and section 7 states the mechanism. The `organize_profile` few-shot collapses eleven subtopics into three and discards two of them, not into two. Section 1 said every table's primary key is `(id, project_id)`; that holds for the seven memory tables and not for `Project` or `Billing`. The profile-read citation moves from `controllers/profile.py:212`, which sits in a delete, to `get_user_profiles()` at line 75 and its filter at line 95. Also established: `merge.py` is unwired at `chat/__init__.py:14` and `merge_yolo` is the live merge path, which answers the open question about which one runs. No capability mark moved; `scope_enforced` was re-checked in both directions and gained evidence, the Redis profile cache being keyed on `user_profiles::{project_id}::{user_id}`.

**2026-07-29** — [`358c16bbc6d687937d79bc2f984a11c3be8da901`](https://github.com/memodb-io/memobase/commit/358c16bbc6d687937d79bc2f984a11c3be8da901) — first reading.

---
title: "Project N.E.K.O."
eyebrow: "Memory that must not reopen a wound"
description: "A companion app whose memory subsystem tracks reinforcement and disputation on separate decay clocks, and tests that a user-disputed entry never feeds back."
root: ../..
page_kind: system
source_name: "Project-N-E-K-O/N.E.K.O"
source_url: https://github.com/Project-N-E-K-O/N.E.K.O
archive_name: "Project-N-E-K-O--N.E.K.O"
revision: b51d4532c59c03b6221bb74560b12e797af9307c
revision_url: https://github.com/Project-N-E-K-O/N.E.K.O/commit/b51d4532c59c03b6221bb74560b12e797af9307c
analyzed_at: 2026-09-13
capabilities: "scope_enforced, audit_log, negative_eval"
capability_evidence:
  scope_enforced: "recall — `MemorySubject` filtering applied before any ranking, on both the internal path and the model-facing tool | memory/scopes.py:30 (LEGACY_PRIVATE_SCOPE), :98-99, :263-285, :311-321, memory/hybrid_recall.py:1165-1169, plugin/plugins/qq_auto_reply/memory_tool_service.py:25-67 | the stored key is the entry's `subject_kind` / `subject_id` / `scope` triple, and `filter_entries_for_subjects` is called before BM25, cosine and RRF — the source comment at hybrid_recall.py:1165 names it a security boundary and states the reason, that a pre-ranking filter cannot be undone by a post-ranking one. It fails closed: an entry with no scope reads as `legacy_private` rather than as a wildcard, `scopes.py:19` says so in the module note, and a new subject is refused that scope outright. On the tool path `resolve_group_recall_subjects` is the single builder shared by the tool handler and the bootstrap context so both authorize identically, member subjects are gated on a non-empty sender and on a switch re-read at recall time, and a second group-shaped slot is deliberately left empty rather than filled with another group's memory | tests/unit/test_group_memory_recall_tool.py:204 (`test_model_supplied_subjects_cannot_influence_scope` — the model supplies a subjects list naming the legacy-private corpus plus include_legacy_private, and the outgoing call carries only the two host-derived subjects, with a positive control that the real answer still returns), :231 (a blank group id fails closed and the bridge is never awaited), tests/unit/test_group_memory_scopes.py:99, :121, :455, :554 (267 cases in that file)"
  audit_log: "the memory views — a per-character append-only event journal under every mutation | memory/event_log.py:194 (class EventLog), :246 (`_append_unlocked`), :274 (public `append`), :617 (`record_and_save`) | every view mutation runs the ordered sequence load view, append event, mutate view, save view, advance sentinel, and the module comment states why the append precedes the mutation: the loaded view is often a shared cached object, so mutating first and failing to append would leave the journal disagreeing with memory that had already changed. The sentinel records the last event reconciled, so a crash between the append and the save is detectable and replayable rather than silent; `SentinelAdvanceError` and `SentinelConflictError` are raised rather than swallowed. Records are JSON lines and no path in the module rewrites or truncates one | tests/unit/test_memory_liveness_dead_letter.py, tests/unit/test_memory_maint_state_lock.py — not run here: the screen reports EXEC on four conftest.py files and FRESH on three dependency manifests, so nothing was installed and the suite was not executed at this pin"
  negative_eval: "recall — the hard filter between fusion and the LLM rerank, and the provenance channel that feeds arbitration | tests/unit/test_memory_recall.py:120, :136, tests/unit/test_group_memory_scopes.py:3165, :3260, :3323, tests/unit/test_group_memory_recall_tool.py:204, :231 | `test_hard_filter_drops_negative_score` and `test_hard_filter_drops_suppressed` assert that an entry the user disputed into a negative evidence score, and one flagged suppressed, are absent from what reaches the reranker — a must-not-retrieve case about a corrected value rather than an access boundary. The scope suite adds the boundary form: a group bootstrap must not read legacy-private memory, an empty subject list must not fall back to the private corpus, and a model-supplied subject list must not reach the query. The forgery trio asserts that an extractor element carrying `speaker_trust: 999` and a spoofed label does not overwrite the request segment's real values, and that neither a message body nor a speaker label can forge a segment boundary — the inputs to the arbitration in section 1. Each carries a positive control: the real answer still returns, the genuine provenance is asserted present | the cases are the evidence, read at the pin; the suite was not executed here because the screen reports EXEC on four conftest.py files and FRESH on three dependency manifests"
stack_storage: "files"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A fact or observation carrying independent reinforcement and disputation counters with separate decay clocks, plus a scope and a source"
  storage: "Per-character JSON views — facts, reflections, persona, directives — behind an append-only event log, with embeddings and archive shards"
  retrieval: "Hybrid BM25 and cosine fused by RRF, then an LLM rerank, with scope filtering applied before ranking and a hard filter dropping disputed entries"
  write: "Extraction into an outbox, deduplicated, with reflection and refinement passes running as background workers"
  update_delete: "Disputation drives an entry's score negative and out of recall; archival needs sustained negative days; no rejected-value record survives archival"
  scoping: "`MemorySubject` with group and participant scopes, missing fields failing closed to `legacy_private`, filtered before any ranking"
  integration: "A companion runtime — voice, vision, avatar — with memory as an internal subsystem, plus a `recall_memory` tool exposed to the model inside the QQ plugin whose scope list is host-derived and ignores any subject the model supplies"
  background: "Embedding worker, reflection, refinement, dedup, archive sharding, and an outbox so mid-flight tasks can be re-run"
  trust: "Two unrelated axes. On the memory: reinforcement and disputation with independent decay, deriving pending, confirmed, promoted or archive-candidate at read time. On the speaker: a server-authoritative trust pool keyed by account, stamped onto a fact's provenance at extraction and used to arbitrate contradictions, with `None` as an explicit abstention distinct from a low score"
  strengths: "A dispute signal structurally separate from reinforcement; a tested hard filter on disputed entries; a do-not-mention list whose life extends with repetition; and committed tests that a model cannot forge the speaker provenance its arbitration depends on, nor widen its own recall scope"
  risks: "The status is derived from a score rather than stored; ban-topic directives expire 3 to 30 days after the last time they were said, scaled by repetition, and the project's own constant comment records that there is no user-facing way to delete one"
---

## 1. Executive Summary

Project N.E.K.O. is a proactive companion application — voice, vision, avatar,
Apache-2.0 — and its memory subsystem is roughly 24,000 lines across thirty
modules. That is larger than most of the purpose-built memory systems in this
atlas, and better reasoned than many, with design RFCs
(`docs/design/memory-evidence-rfc.md`, `memory-event-log-rfc.md`) that the code
cites by section number.

It is here because a companion application has a product incentive the research
systems lack. If a memory layer forgets, a user notices immediately; if it
*re-raises something the user asked it to drop*, the user is not mildly
inconvenienced but hurt. That pressure has produced two mechanisms this atlas has
been looking for and finding almost nowhere.

**Reinforcement and disputation are separate quantities with separate decay
clocks.** `evidence_score(entry, now)` is
`effective_reinforcement − effective_disputation`, and `rein_last_signal_at` and
`disp_last_signal_at` advance independently, so a signal on one side does not
reset the other's decay. Almost every system in this atlas collapses "how sure am
I" into a single number that agreement and disagreement both move. Here, "long
confirmed but recently disputed" is representable, and it decays like two things
because it is two things.

**And a disputed entry is tested not to come back.**
`test_hard_filter_drops_negative_score` asserts that an observation with
`evidence_score < 0` is excluded from the pool, with the reasoning in its
docstring: *"Stage-2 would either reinforce the dispute or, worse, cancel it."*
That is the re-assertion failure this atlas is organised around — named,
understood, and defended with a committed test. It is the **first negative
retrieval assertion in the atlas that is about a corrected value rather than an
access boundary**.

**Trust runs on a second axis that has nothing to do with the memory.**
`memory/trust_store.py` holds a server-authoritative pool keyed by a
platform-neutral account id, and `resolve_trust` returns a float — or `None`,
which is an explicit abstention the module goes to some length to keep distinct
from a low score: *"``None`` means the handler must not write the
``speaker_trust`` key at all… Falling back to 0.5 would stamp a finite value onto
rows that today deliberately carry none, turning abstention into an active
arbitration vote."* That value is stamped onto a fact's provenance when it is
extracted, and `preferred_by_trust` uses it to decide which of two contradictory
facts survives de-duplication. A memory's credibility is, in part, a property of
who said it.

Which makes the attribution channel a privilege boundary, and it is defended as
one. `test_llm_output_cannot_spoof_speaker_provenance` has the extractor return
an element carrying `speaker_trust: 999` and `speaker_label: "admin 本人"`, and
asserts the stored fact keeps the request segment's `0.3` and `Alice(1001)`.
Two further cases assert that neither a message body nor a speaker label can
forge a segment boundary. Without those, a user could talk their way into a
higher arbitration weight.

The weaknesses are narrower than usual. The status tiers are *derived* from the
score at read time rather than stored, so there is no field a query can filter on
and no record that a specific value was rejected. And the do-not-mention
directives — the closest thing here to a tombstone — are prompt-only and expire,
though how fast depends on how often they were said.

## 2. Mental Model

A memory is an entry whose standing is computed, not stored. Reading one calls
`evidence_score(entry, now)`, and `derive_status` maps that to one of four tiers:

| Condition on `evidence_score(entry, now)` | Derived status |
| --- | --- |
| `score >= EVIDENCE_PROMOTED_THRESHOLD` | `promoted` |
| `score >= EVIDENCE_CONFIRMED_THRESHOLD` | `confirmed` |
| `score <= EVIDENCE_ARCHIVE_THRESHOLD` | `archive_candidate` |
| otherwise | `pending` |

The docstring is careful that this is *"a DERIVED semantic label, not a storage
field"*, and that archival additionally requires
`sub_zero_days >= EVIDENCE_ARCHIVE_DAYS` — an entry must stay negative for a
sustained period, not merely dip.

The lifecycle, with the two unusual things marked:

```mermaid
%% caption: reinforcement and disputation are separate counters on separate decay clocks, every mutation appends to the event log, and a ban-topic directive expires after three days
flowchart TB
    U["utterance"] --> EX["extraction"]
    EX --> OB["outbox"] --> DD["dedup"] --> ST[("facts / reflections / persona")]
    ST -->|"every mutation"| EL[("event_log<br/>append-only")]

    U --> RS["reinforcement signal"] --> RC["rein counter<br/><i>own decay clock</i>"]
    U --> DS["disputation signal"] --> DC["disp counter<br/><i>own decay clock</i>"]

    U --> BT["ban-topic directive<br/>stop mentioning X"]
    BT --> UD[("user_directives.json<br/>keyed on kind + term.casefold()<br/>TTL 3d × hit_count, capped at 30d")]
    UD -->|"spliced in at cold start"| SP["system prompt"]

    style DC fill:#f4e2bd,stroke:#b8860b
```

The two decay clocks are the point: reinforcement and disputation are separate
counters, so "long confirmed, recently disputed" is a state this system can hold
and a single confidence float cannot.

Recall runs in one direction with two gates that both matter:

```mermaid
%% caption: the scope filter runs before ranking and a hard filter drops suppressed entries before the LLM reranker ever sees them
flowchart LR
    Q["query"] --> SF["scope filter"]
    SF --> BM["BM25 + cosine"] --> RRF["RRF fusion"] --> HF["hard filter"] --> RR["LLM rerank"]
    SF -.- N1["before ranking,<br/>never after"]
    HF -.- N2["drops score < 0<br/>and suppressed entries"]

    style HF fill:#f4e2bd,stroke:#b8860b
    style N1 fill:#f7f4ec,stroke:#cfcfcf
    style N2 fill:#f7f4ec,stroke:#cfcfcf
```

Scope filters **before** ranking, so excluded material is never ranked rather than
ranked and hidden. The hard filter sits **before** the LLM rerank, so disputed
material the model never sees cannot be talked back into relevance — and
`test_hard_filter_drops_negative_score` asserts it.

`protected=True` entries — those from the character card — return `float('inf')`
from `evidence_score` and are *"never evicted / archived / squeezed out by
budget"*. So the character's own identity cannot be disputed away by
conversation, which is correct for this product and a pinning rule the atlas
rarely sees stated so plainly.

## 3. Architecture

Python, Apache-2.0, with `memory/` holding thirty modules and about 24,000 lines:

| Concern | Modules |
| --- | --- |
| Belief | `facts.py` (2,474), `fact_dedup.py` (839), `evidence.py`, `evidence_analytics.py`, `evidence_handlers.py` |
| Recall | `hybrid_recall.py` (803), `recall.py`, `recent.py`, `timeindex.py` |
| Correction | `user_directives.py` (465), `anti_repeat.py` (617), `refine.py` |
| Durability | `event_log.py` (601), `outbox.py`, `cursors.py`, `archive_shards.py` |
| Structure | `scopes.py`, `temporal.py`, `persona/`, `reflection/`, `store/` |
| Embedding | `embeddings.py`, `embedding_worker.py`, `embeddings_fallback.py`, `_embeddings/` |

```mermaid
%% caption: the write and read halves together, with the scope filter failing closed to the private namespace
flowchart TB
    U[Utterance] --> EX[extraction]
    U --> UD[user_directives<br/>ban-topic, TTL 3d × hits, cap 30d]
    EX --> OB[outbox] --> DD[fact_dedup] --> V[(facts / reflections / persona JSON)]
    V --> EL[(event_log — append-only)]
    Q[Query] --> SF[scope filter<br/>fail-closed to legacy_private]
    SF --> H[BM25 + cosine → RRF]
    H --> HF[hard filter<br/>score < 0, suppressed]
    HF --> RR[LLM rerank] --> OUT[recall]
    UD --> PR[system prompt at cold start]
    AR[anti_repeat BM25<br/>over recent AI output] --> GEN[generation]
```

### Deployment and ergonomics

- **What has to run:** the companion app. Storage is per-character JSON plus
  embeddings; there is no database server.
- **Local and offline:** embeddings have a fallback path
  (`embeddings_fallback.py`), and BM25 needs no model — so recall degrades rather
  than breaking without an embedding service.
- **Hand-repairable:** the views are JSON per character, and the event log gives
  a bad state a history to reconstruct from.

## 4. Essential Implementation Paths

**Evidence.** `memory/evidence.py` — `evidence_score` (152) as reinforcement
minus disputation, both decayed at read time; `derive_status` (163);
`compute_evidence_snapshot` producing the payload for the outgoing event.

**The audit log.** `memory/event_log.py` — *"per-character append-only audit +
replay log"*. Its motivation is stated precisely: the views
(`facts.json` / `reflections.json` / `persona.json`) *"are the only record of
state transitions, so there is no ordered history"*, which makes "crashed halfway
through a view write" invisible and cross-file invariants uncheckable.

**Scope, enforced before ranking.** `memory/hybrid_recall.py:566` carries the
comment *"Security boundary: scope filtering happens before any
BM25/cosine/RRF"* — because filtering afterwards hides results rather than
excluding them. `memory/scopes.py` states the fail-closed rule: *"Missing fields
deliberately mean `legacy_private`; they never mean wildcard/global access."*

**The hard filter.** `MemoryRecallReranker._hard_filter` drops entries with
`evidence_score < 0` and entries flagged `suppress`, before the LLM rerank.

**Ban-topic directives.** `memory/user_directives.py` — extraction across locales
in parallel, dedup key `(kind, term.casefold())`, storage in
`memory/{name}/user_directives.json`, and `render_prompt_block` splicing the block
into the system prompt tail at startup. The TTL is a function of how often the
directive has been said: `_effective_ttl(hit_count)` (`:134-149`) returns
`min(USER_DIRECTIVE_TTL_SECONDS * hit_count, USER_DIRECTIVE_TTL_MAX_SECONDS)`,
which is three days for one mention, six for two, and a thirty-day cap from ten
onwards. Only a fresh hit renews `expire_at`; silence does not. Reads filter on
`expire_at`, `purge_expired` collects, and `_rotate` caps the file at
`USER_DIRECTIVE_MAX_STORED = 60` while `get_active` truncates the injected block
to `USER_DIRECTIVE_MAX_ACTIVE = 20`.

**Anti-repetition.** `memory/anti_repeat.py` — a per-character rolling BM25
corpus over recent *AI* output, because *"the LLM tends to circle back to the
same topic … Simple SequenceMatcher similarity only catches exact repeats and is
useless against rephrased but still on the same topic."* The background corpus is
count-capped and *"never time-filtered, so IDF context survives idle periods
intact"*.

**Tests.** ~7,936 across the repository, including
`tests/unit/test_memory_recall.py`, `test_group_memory_scopes.py`, and several
`*_memory_policy_contract.py` suites.

## 5. Memory Data Model

The evidence fields are the model: reinforcement and disputation counters with
`rein_last_signal_at` and `disp_last_signal_at`, a `protected` flag, a scope, a
source, and a `suppress` flag.

**Scope** is a `MemorySubject` supporting group and participant memory, with a
`SCOPED_PERSONA_PREFIX` of `@subject/` and a documented legacy path. The
fail-closed default — absent scope means `legacy_private`, never global — is the
same discipline [OpenHuman](../openhuman/) applies to its taint column, and the
right default for a system that gained group chat after the fact.

**No stored status field**, which is why `trust_state` is withheld. The four tiers
are computed per read, so nothing can query "all pending facts" without
recomputing, and no history of status transitions exists outside the event log.

**No rejected-value record that survives archival.** Disputation pushes an entry
out of recall and eventually into an archive shard, but nothing keyed on the
*value* prevents the same claim being extracted from a later conversation and
starting fresh at zero.

## 6. Retrieval Mechanics

The most complete retrieval stack in the companion category and competitive with
the best here: **scope filter → BM25 + cosine → RRF → hard filter → LLM rerank**,
with a budget and an embedding fallback.

Two details are worth stealing regardless of domain. **Scope before ranking** is a
security property rather than a performance one, and the comment says so. **The
hard filter sits between fusion and the LLM rerank**, so disputed material never
reaches the model that would otherwise weigh it — the difference between "the
model decided not to use it" and "the model never saw it".

`anti_repeat` is a second, unusual mechanism: a negative filter over the
assistant's *own recent output*, to stop a proactive companion raising the same
subject repeatedly. Nothing else in this atlas models self-repetition as a memory
problem.

## 7. Write Mechanics

Extraction runs into an **outbox** so a background task killed mid-flight can be
re-run, then through `fact_dedup` before landing in the per-character views.
Reflection and refinement are separate background passes.

The directive path is the interesting write. `dispatch_user_utterance` fans out to
a registered sink; extraction runs *all locales in parallel* because mixed
Chinese and English speech is common; a hit is trimmed and stored under
`(kind, term.casefold())`, with repeated hits refreshing the expiry and
incrementing `hit_count`.

Its **false-positive policy is stated explicitly**, which is rare enough to quote:

> *"The regex templates are lenient. Cost of a false kill = the user says an
> equivalent sentence once more; cost of a miss = the user gets offended again —
> so we lean toward over-killing."*

That is an asymmetric error-cost analysis written into the module implementing the
suppression. No other system in this atlas states the trade it is making on a
suppression mechanism.

The scope discipline is equally careful. The module documents what it deliberately
does *not* extract: object-less "shut up" or "change the subject" (no concrete
topic to carry forward, and pushing the intent into the next round would
backfire), and plain preferences like "I don't like watermelon" (that belongs to
the fact pipeline, not the ban list).

### Operational cost

- **The hot path is not blocked**: extraction goes to an outbox and workers drain
  it.
- **Decay is computed at read time rather than as a state transition**, so no
  sweep rewrites scores — a good trade that removes a whole class of background
  job.
- **Embeddings have a worker and a fallback**, so a slow embedding service
  degrades recall rather than stalling writes.
- **On the read path**, the LLM rerank has a budget and the directive prompt block
  is bounded by `USER_DIRECTIVE_MAX_ACTIVE`.

## 8. Agent Integration

Memory is mostly an internal subsystem rather than an exposed API. There is no
MCP surface; recall is assembled and injected, and directives are spliced into
the system prompt at cold start. That is right for a product where the user never
thinks about memory, and it means the mechanisms here are not reusable as a
library — they are reusable as *designs*.

### The one place the model may ask

`plugin/plugins/qq_auto_reply/memory_tool_service.py` defines a `recall_memory`
tool (`RECALL_TOOL_NAME`, `:20`) with a five-second HTTP budget, handed to the
model during a group turn. What makes it worth reading is not the tool but how
its scope is decided.

`resolve_group_recall_subjects` (`:25`) is the single place the group read path's
subject list is built, and its docstring says why it is single: it is *"shared by
the recall_memory tool handler AND the scoped bootstrap context: both paths must
authorize exactly the same scopes, or what a group turn may read would depend on
which one ran."* The list is the group subject, then the current speaker, then up
to `GROUP_RECALL_MAX_MEMBER_SUBJECTS - 1` recent speakers — and the member slots
are gated twice, on a non-empty sender id and on a `group_member_memory_enabled`
switch re-read at the moment of recall so that turning member memory off stops
participant-scope reads immediately rather than at the next restart.

The ordering is load-bearing rather than cosmetic: the subject order *is* the
render budget's allocation order under `SCOPED_RENDER_TOTAL_MAX_TOKENS`, so the
group always outranks any individual, and the comment names that as the caller's
only priority knob.

**And there is a slot deliberately left empty.** A second group-shaped position
exists in the shape and is not filled, because the only thing that could fill it
is another group's memory — and the comment declines to open that here: the
existing cross-group path reads live session memory and *"从不碰记忆库"*, never
touches the memory store, so whether to allow cross-group disclosure is a
separate decision rather than one made in passing while wiring a tool. A refusal
to widen a scope, recorded at the place where widening would have been one line,
is worth more than most of the scope documentation in this corpus.

The model's own arguments do not reach any of this: see section 10.

## 9. Reliability, Safety, and Trust

**The dispute channel is the contribution.** Separating reinforcement from
disputation, giving each its own decay clock, then hard-filtering negative entries
before the rerank is a more careful treatment of disagreement than any dedicated
memory system in this atlas manages. Most systems here have one confidence number
that agreement and disagreement both push on, which cannot express "recently
disputed but long confirmed" — the exact state a companion must handle gently.

**`trust_state` is withheld** because the four tiers are derived per read rather
than stored, and the definition asks for a field. The near-miss is substantial and
arguably the definition's problem rather than the system's: a label computed
deterministically from two independently-decaying counters carries more
information than a stored enum and cannot go stale. What it cannot do is be
queried or filtered without recomputation, and no transition history exists
outside the event log.

**`audit_log` is earned** on `event_log.py` — append-only, per character,
motivated by exactly the failure the atlas cares about, and backed by a design
RFC.

**`negative_eval` is earned, and for the reason the atlas has been waiting for.**
The prior holders that came from access-control work — MIRIX, Aukora, EverOS —
all assert a *boundary*. `test_hard_filter_drops_negative_score` asserts that **a
value the user disputed does not feed back into the pipeline**. That is
correction, not scope, and it is the first of its kind in this corpus.

**The ban-topic list is the closest thing here to a tombstone and does not earn
the mark.** It is durable, keyed on the term rather than on a row, and survives
the restart that would otherwise wipe the context — more than most manage. But it
works by *asking the model* not to raise the topic, so a sufficiently distracted
model still can, and it expires: three days from one mention, extending linearly
with repetition to a thirty-day ceiling, measured from the last time the user
said it rather than from a cumulative lifetime.

The scaling is the right shape for the signal — `config/session_settings.py:46`
argues it directly, that saying something once may be a mood and saying it
repeatedly is a stable preference, and that the two should not share an expiry —
and the same comment records the gap the atlas would otherwise have to infer:
the ban list is a pure prompt constraint and *"用户今天还没有界面能删（管理面另行补）"*
— the user has no interface today for deleting one, with an admin surface
deferred. A suppression a user cannot inspect or revoke, that lapses on its own
after a month of silence, is a strong hint and not a durable rejection. The mark
stays withheld.

**Privacy**: memories are per-character JSON on the user's machine, and the
`protected` flag prevents character-card identity being disputed away. No secret
filtering on the write path was found.

## 10. Tests, Evals, and Benchmarks

About **16,344 test functions** under `tests/` and `plugin/tests/` — the largest
suite of any system in this atlas — with memory covered by `test_memory_recall.py` (phase by phase
over the recall pipeline), `test_group_memory_scopes.py`, a runtime memory soak
test, and several `*_memory_policy_contract.py` files asserting that a feature's
memory behaviour matches a written policy.

The recall tests are structured the way this atlas keeps asking for: each phase in
isolation, with negative assertions at the phase boundary rather than end to end.
`test_hard_filter_drops_negative_score` and `test_hard_filter_drops_suppressed`
are both single-phase and both assert absence.

No public benchmark is run, and none would be meaningful — this product's
evaluation is whether users keep talking to it.

### What the scope and tool suites assert

The scope suite runs to 267 test functions and the recall-tool suite to 50, and
between them they cover the two surfaces a scope mark usually cannot reach.

`test_model_supplied_subjects_cannot_influence_scope` calls the recall tool with
a hallucinated `subjects` list naming the legacy-private corpus plus
`include_legacy_private: True`, and asserts the outgoing call carries exactly the
two host-derived subjects for the turn — with a positive control that the real
answer still comes back. Its docstring names it *"behavioural twin of the schema
assert"*, so the schema and the behaviour are checked separately. The atlas's own
definition of `scope_enforced` says explicitly that the mark does **not** certify
that a caller cannot widen the boundary by passing a different argument; this is
a committed test that it cannot.

`test_execute_recall_missing_group_id_fails_closed` covers the direction that
matters more: a group turn with a blank group id must not call recall at all,
because `subjects=None` means the legacy-private corpus server-side, so falling
through would read the operator's private memories into a group chat. The test
asserts the bridge was never awaited.

And the provenance-forgery trio — `test_llm_output_cannot_spoof_speaker_provenance`,
`test_message_body_cannot_forge_a_segment_boundary`,
`test_speaker_label_cannot_forge_a_segment_boundary` — defend the input to the
trust arbitration described in section 1.

**What I would still want:** a test that a ban-topic directive still suppresses
after the TTL boundary, or an explicit decision that it should not; a test that
re-stating a directive extends rather than resets its life; and a test that a
disputed fact re-extracted from a later conversation does not silently reset to
zero.

## 11. For Your Own Build

### Steal

- **Track agreement and disagreement as separate quantities with separate decay
  clocks.** One confidence float cannot represent "long confirmed, recently
  disputed", which is the state that most needs careful handling. Two counters and
  two timestamps can, and `score = rein − disp` collapses them only when you need
  a number.
- **Compute status at read time instead of storing it.** No sweep, no stale
  labels, no migration when a threshold changes.
- **Filter scope before ranking, and write the reason in the code.** Filtering
  after ranking hides results instead of excluding them, and the comment is what
  stops someone reordering it for performance.
- **Put the hard filter before the LLM rerank.** Disputed material the model never
  sees cannot be talked back into relevance.
- **Keep a durable do-not-mention list keyed on the term.** The insight is in the
  motivation: the current turn is fine because the model can see the user's
  words — the failure is the *next cold start*, after compression has wiped them.
- **State your false-positive policy where the suppression lives.** One sentence
  tells every future maintainer which way to tune.
- **Model self-repetition as a memory problem.** A BM25 corpus over your own
  recent output catches "rephrased but still the same topic", which string
  similarity never will.
- **Take the disputation mechanism into serious systems, not just companions.**
  This is the transfer worth stating plainly, because the packaging invites
  dismissal. A companion app builds this because raising something the user asked
  it to drop is an emotional injury and the user leaves. The identical
  architecture is what stops a customer-service agent volunteering a declined
  mortgage application, a health assistant re-raising a terminated pregnancy, or a
  CRM summary reminding a rep to ask after a client's late spouse. Every one of
  those is a *retrieval* failure over a technically accurate memory, which a
  confidence score cannot express and a relevance ranker will happily surface
  forever. The distinction the atlas has been asking for — a durable record that
  a specific value was *rejected*, separate from how confident anyone is in it —
  gets built first where the cost of getting it wrong is felt immediately rather
  than measured quarterly.

### Avoid

- **A three-day TTL on a suppression the user asked for.** Reinforcement decay
  makes sense for facts; "never mention this again" is not a fact and does not
  weaken with time. If the list must be bounded, bound it by size and let the user
  see it.
- **Deriving status without keeping transitions.** Read-time computation is the
  right call, and it means you cannot answer "when did this become disputed?"
  unless the event log carries it — so make sure it does.

### Fit

Read this if you are building anything where a memory mistake is *felt* rather
than merely wrong — a companion, a therapy-adjacent tool, a long-running personal
assistant. The evidence model and the directive list come from that pressure and
are the two best answers to it in this atlas.

It is not a library. Memory is wired into a companion runtime with voice, vision
and an avatar, and there is no API boundary to lift it out through. Take the
designs, not the code.

And the broader point for anyone surveying this field: this subsystem is larger
and more carefully reasoned than most of the purpose-built memory frameworks
here, and it was found in a companion app. Product pressure from users who notice
produced a dispute channel, an append-only audit log and a tested correction
filter — three things the research systems mostly discuss.

## 12. Open Questions

- **Will the deferred admin surface for the ban list arrive?** The constant's own
  comment defers it, and until it does a user cannot see or delete a suppression
  the system is applying on their behalf.
- **Does a re-stated directive that has already expired start again at three days
  or resume at its old `hit_count`?** The row is dropped on read once
  `expire_at` passes, and whether `record` then sees a fresh term or a surviving
  one decides how much a user pays for a lapse.
- **Should `speaker_trust` reach the recall path as well as the write path?** It
  arbitrates de-duplication and correction today; nothing consults it when
  ranking what to recall, so a low-trust fact that survived arbitration is
  retrieved on the same footing as any other.
- **What happens when a disputed fact is re-extracted?** Whether `fact_dedup`
  matches it back to the archived entry and restores its disputation, or creates a
  fresh entry at zero, was not traced — and it decides whether correction
  survives.
- **Does the event log let status transitions be reconstructed?** It records
  mutations; whether an evidence snapshot rides on every one determines if "when
  did this become disputed" is answerable.
- **How is a disputation signal produced?** The scoring is clear; the classifier
  deciding that a user utterance disputes a specific entry was not read.
- **Do the `*_memory_policy_contract` tests assert policies from the design
  RFCs**, and is anything keeping the two in sync?

## Appendix: File Index

**Evidence and belief**

- `memory/evidence.py` — `evidence_score` (152), `derive_status` (163),
  `compute_evidence_snapshot`
- `memory/facts.py`, `memory/fact_dedup.py`, `memory/evidence_handlers.py`,
  `memory/evidence_analytics.py`

**Correction**

- `memory/user_directives.py` — `UserDirectivesManager`, TTL, prompt block
- `memory/anti_repeat.py` — BM25 over recent AI output
- `memory/refine.py`, `memory/reflection/`

**Speaker trust**

- `memory/trust_store.py` — the pool, its four stated rules and its kill list of
  identity heuristics (17–60), `TrustSnapshot.trust_inputs` (744),
  `resolve_trust` and its three abstention conditions (778)
- `memory/speaker_trust.py` — `preferred_by_trust` (156), `trust_band`
- Consumers: `memory/fact_dedup.py` (1319, 1357),
  `memory/persona/corrections.py` (757, 792), `memory/scoped_refine.py` (220–228)
- `config/session_settings.py` — `USER_DIRECTIVE_TTL_SECONDS` (35),
  `USER_DIRECTIVE_TTL_MAX_SECONDS` (46), `USER_DIRECTIVE_MAX_STORED` (66)

**Recall**

- `memory/hybrid_recall.py` — scope boundary comment (1165), RRF fusion
- `memory/recall.py`, `memory/recent.py`, `memory/timeindex.py`,
  `memory/recall_render.py`
- `plugin/plugins/qq_auto_reply/memory_tool_service.py` — `RECALL_TOOL_NAME` (20),
  `resolve_group_recall_subjects` and the empty second group slot (25),
  `resolve_participant_recall_subjects` (68)
- `config/memory_settings.py` — `SCOPED_RENDER_TOTAL_MAX_TOKENS` (136),
  `GROUP_RECALL_MAX_MEMBER_SUBJECTS` (234)

**Durability and scope**

- `memory/event_log.py` — append-only audit and replay
- `memory/outbox.py`, `memory/cursors.py`, `memory/archive_shards.py`
- `memory/scopes.py` — `MemorySubject`, `LEGACY_PRIVATE_SCOPE`

**Design documents**

- `docs/design/memory-evidence-rfc.md`, `docs/design/memory-event-log-rfc.md`

**Tests**

- `tests/unit/test_memory_recall.py` — `test_hard_filter_drops_negative_score`
  (120), `test_hard_filter_drops_suppressed` (136)
- `tests/unit/test_group_memory_scopes.py` — 267 cases, including
  `test_llm_output_cannot_spoof_speaker_provenance` (3165),
  `test_message_body_cannot_forge_a_segment_boundary` (3260),
  `test_speaker_label_cannot_forge_a_segment_boundary` (3323),
  `test_qq_group_bootstrap_never_reads_legacy_private_memory` (455)
- `tests/unit/test_group_memory_recall_tool.py` — 50 cases, including
  `test_model_supplied_subjects_cannot_influence_scope` (204) and
  `test_execute_recall_missing_group_id_fails_closed` (231)
- `tests/unit/test_speaker_trust.py`, `tests/unit/test_trust_store.py`,
  `tests/unit/test_runtime_memory_soak.py`

## History

**2026-09-13** — [`b51d4532c59c03b6221bb74560b12e797af9307c`](https://github.com/Project-N-E-K-O/N.E.K.O/commit/b51d4532c59c03b6221bb74560b12e797af9307c) — 403 commits past the previous pin, with roughly 19,000 lines added under `memory/` and ten new modules there. A published criticism is corrected: the ban-topic TTL is not a flat three days but `min(3 days × hit_count, 30 days)` measured from the last mention, and `config/session_settings.py:46` argues the scaling and records that no user-facing delete exists yet — which narrows the criticism rather than removing it, and answers the open question that asked for the rationale. The largest new material is `memory/trust_store.py` and `memory/speaker_trust.py`: a server-authoritative trust pool keyed by account, stamped into a fact's provenance and used by `preferred_by_trust` to arbitrate contradictions during de-duplication and correction, with `None` held as an explicit abstention. It is a float banded at read time and it describes the speaker rather than the memory, so `trust_state` is re-checked and withheld. The scope test file grew to 267 cases and a recall-tool file of 50 was added; both are folded into the `scope_enforced` record, which now rests on a committed test that a model cannot widen its own scope by passing subject arguments. `audit_log` and `negative_eval` re-verified at the new pin and unchanged. The screen reports `FRESH` on `pyproject.toml`, `requirements.txt` and `uv.lock` and `EXEC` on four `conftest.py` files, so nothing was installed and no test was run here; every claim about a test is a claim about its committed source.

**2026-07-29** — [`6a3d4beb7425261d01eb08034139d87bec03b8b5`](https://github.com/Project-N-E-K-O/N.E.K.O/commit/6a3d4beb7425261d01eb08034139d87bec03b8b5) — first reading.

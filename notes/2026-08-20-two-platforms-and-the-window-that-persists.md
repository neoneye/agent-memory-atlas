# Two platforms, and the window that persists

**Status:** triage. Two repositories read on 2026-08-20, both excluded, both
worth recording — one for a boundary case the corpus keeps meeting, one for a
sixth vocabulary poison. Screened before reading; nothing installed, nothing run.
**Origin:** `hybroai/hybro` and `future-agi/future-agi` submitted together,
alongside the [Perseus Vault re-read](2026-08-20-someone-built-the-contract.md).

---

## Hybro — `hybroai/hybro` at [`bf48e3036c5db2a26fb4cbad13ae2d6f47fed9a8`](https://github.com/hybroai/hybro/commit/bf48e3036c5db2a26fb4cbad13ae2d6f47fed9a8)

**Excluded on the compaction boundary, and it is the closest call in a while.**
Apache-2.0, ~282,000 lines, an async FastAPI backend and a Next.js dashboard for
an agent-interoperability platform: local and remote agents in execution rooms,
routed over the Agent2Agent protocol. Screened: no auto-run surface, one
build-time execution point, four manifests inside the cooldown.

**The vocabulary probe was clean and would have been wrong.** `remember`,
`recall`, `forget`, `tombstone` and `supersede` appear nowhere in the backend,
and every `embedding` hit is the LLM gateway offering `embed()` as a provider
capability. The memory is in a package the probe cannot see by name:
`backend/context_memory/`, with `assembly.py`, `compaction.py`,
`content_storage.py`, `projection.py`, `search.py`, `summary.py` and a MongoDB
repository. Fifth instance for
[the probe note](2026-08-19-the-vocabulary-probe-lies.md), and the first where
the miss was a *directory name* rather than a sense collision.

What it holds is a conversation, durably:

- `ConversationTurnData` — `turn_id`, `role`, `agent_id`, `user_id`, a
  `representation` of `full` or compact, `estimated_tokens_full` and
  `estimated_tokens_compact` as separate fields, a `brief_summary`, `turn_notes`,
  and `was_successful`.
- `ContentReferenceData` — the body lives in MongoDB under a `document_id` with a
  `content_hash`, so a turn carries a pointer and a digest rather than the text.
- `RoomSummaryData` — `current_goal`, `key_decisions`, `open_questions`,
  `recent_agent_contributions`, maintained by `update_room_summary`.

**The call turns on who searches and what the unit is.**
`ContextMemoryFacade.search_memory(room_id, query, limit)` is scoped to one room,
and its only non-test caller is
`execution/orchestration/room_message_center.py:629`, inside
`_refresh_supervisor_conversation_context`, which folds the results into an
assembled supervisor context at `max_turns=5`. **The orchestrator searches; the
model cannot.** No agent tool exposes it — agents are A2A endpoints whose cards
declare skills, and none of those skills is a memory operation. That is the
[tool-registry test](2026-08-14-a-coding-agent-whose-search-is-the-users-not-the-models.md)
failing in the same way Kimi Code failed it, with the searcher being an
orchestrator rather than a human.

And the unit never leaves the room. `delete_room_memory(room_id)` is the only
delete and its granularity is the whole room; nothing is scoped above a room,
nothing is retrieved across rooms, and the summary's `key_decisions` — the one
field here that is a claim capable of being wrong — is regenerated for the room
rather than corrected as a belief. This is
[conversation-window management](../content/overview.md)
with a durable backing store and a real ranker, which is the atlas's stated
boundary, and it is better plumbing than most systems that cross it.

**Three mechanisms worth taking anyway.**

1. **A turn carries a token estimate per representation.**
   `estimated_tokens_full` and `estimated_tokens_compact` side by side mean the
   assembler can decide what to include without re-estimating, and can tell how
   much a compaction actually bought.
2. **The body is stored by reference with a hash and an expiry.** A turn is a
   pointer plus `content_hash`, and `is_content_expired` governs whether the body
   is still there — so the metadata layer stays small and the store can be honest
   about a body it no longer has.
3. **`was_successful` on the turn.** A boolean outcome recorded beside the
   content is the cheapest version of the thing several systems in this corpus
   build elaborately: knowing which past turns worked before deciding which to
   replay.

## Future AGI — `future-agi/future-agi` at [`20e5a0f90075ed83cdb358c0d54e2a01ca8274cc`](https://github.com/future-agi/future-agi/commit/20e5a0f90075ed83cdb358c0d54e2a01ca8274cc)

**Excluded: it observes agents, it does not remember for them.** ~1.28 million
lines across a Django backend, a collector, a Go gateway and a frontend, plus a
separate enterprise licence file beside the open one. Simulation, evaluation,
observability, guardrails, and — the part worth checking — a prompt optimiser.
Screened: no auto-run surface, thirty-one build-time execution points, two
manifests inside the cooldown.

What it stores durably is traces, spans, annotations, eval scores and prompt
trials. A span records what happened; an eval score measures it. Neither is a
claim the agent later acts on as true, which is the same boundary that excluded
`os-factory/har`, `pingdotgg/t3code` and `MeisnerDan/mission-control`.

**The one thing that deserved a second look** is
`tfc/temporal/agent_prompt_optimiser/`, which runs `PromptTrial` records through
Temporal workflows with eval activities and promotes on measured results. That
is the [MetaClaw](../content/systems/metaclaw.md) shape — a candidate promoted only
when it does not regress — and MetaClaw *is* in the corpus. The difference is
what is being promoted and what sits underneath. MetaClaw promotes a *retrieval
policy*, which governs a memory store it also owns; Future AGI promotes a
*prompt*, and there is no store of facts anywhere in the tree for the promotion
to govern. A prompt is an instruction, and an instruction cannot be false — the
same reason a schedule and a phase were refused in earlier readings.

**A sixth vocabulary poison, and the most on-the-nose one yet.** Grep this tree
for `tombstone` — the rarest mechanism in this atlas, the one twenty-one of
three hundred and fourteen systems carry — and every hit is a **ClickHouse/PeerDB
CDC deletion marker**: *"span's tombstone wins over its live version before
`is_deleted = 0`"*, *"seed a CH row with `_peerdb_is_deleted = 1` (CDC
tombstone)"*. `supersede` is `ReplacingMergeTree` version collapse. The
atlas's headline mechanism name, used throughout a data-warehouse pipeline, in a
repository with no agent memory in it at all.

---

## For next time

**A memory subsystem can hide behind a directory name the probe does not
carry.** The five words in the standard probe are the *operations*; Hybro names
its package for the *thing* — `context_memory` — and implements it with
`project_message`, `assemble_context`, `run_compaction` and `search_memory`.
Worth adding a second pass over directory and module names —
`memory`, `context`, `recall`, `history`, `store` — before concluding a tree has
none, because a clean operation probe over a repository that has a
`context_memory/` package is exactly the shape
[the probe note](2026-08-19-the-vocabulary-probe-lies.md) warns is most
dangerous: it reads as a settled negative.

**And the compaction boundary now has a second question attached.** The stated
test is whether something survives the session with an identity that could later
be corrected. Hybro's turns survive, carry ids, and are searchable — and the
searcher is the orchestrator, not the model, and the scope never exceeds the
room. Both halves were needed to settle it. When a system stores a conversation
durably and ranks it, ask *who issues the query* and *what the widest scope is*;
either answer alone leaves the call open.

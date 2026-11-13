---
title: "MGI-Mind"
eyebrow: "Local MCP memory with a duel rule over facts"
description: "A local Rust MCP memory server over Qdrant whose facts resolve contradictions by a duel rule, while memories pass a relevance gate into quarantine."
root: ../..
page_kind: system
source_name: "madgodinc/mgi-mind"
source_url: https://github.com/madgodinc/mgi-mind
archive_name: "madgodinc--mgi-mind"
revision: 8069652a5dd69c68ebd32d8dbdc3eb3327681d88
revision_url: https://github.com/madgodinc/mgi-mind/commit/8069652a5dd69c68ebd32d8dbdc3eb3327681d88
analyzed_at: 2026-11-13
licence: "Apache-2.0"
size: "28,617 lines of Rust in src/ before the inline test modules, 36,805 with them; a 536-line Python client"
activity: "322 commits on main by 1 contributor, 28 May 2026 – 13 November 2026"
tests: "471 inline Rust unit tests, 48 integration tests in tests/, 8 Python client tests"
capabilities: "tombstone, trust_state, bitemporal, audit_log, human_review, negative_eval"
capability_evidence:
  tombstone: "fact store — an explicitly invalidated triple, refused on every fact write path until an explicit restore, whether re-sent exactly or differing only in case or whitespace | src/knowledge.rs:303-308; src/knowledge.rs:336-382; src/knowledge.rs:594-628; src/knowledge.rs:1337-1424; src/knowledge.rs:1436-1503; src/mcp.rs:1152-1176 | the fact id is a UUIDv5 of subject, predicate and object, so a re-assertion addresses the invalidated row; add_fact_core reads that row's valid field under both locks and, when it is false, returns verdict invalidated without writing. It then scrolls every valid = false row and refuses a triple equal to one under tombstone_key — whitespace runs collapsed, ends trimmed, lowercased — returning that row's id. invalidate_fact_authored is the only writer of valid = false and restore_fact_authored the only path back; every fact writer reaches add_fact_core, and nothing deletes a fact point | explicit_invalidate_is_final_until_restored (tests/cli_integration.rs:3447-3505) asserts the refused re-add, the absence after it and the return after restore; invalidated_triple_refuses_case_and_whitespace_variants (:3849-3899) asserts an upper-cased, padded variant refused with the invalidated id beside a different object accepted. The loose key applies to the refusal only: the id and the duel compare exact strings, no Unicode normalisation runs, and a variant row written before the invalidate stays visible; the agent holds restore on the same tool; a duel loser is not covered; memories have no equivalent; mind_ingest counts a refused fact as stored"
  trust_state: "a fact carries a lifecycle status, and the duel rule writes stale, superseded or quarantine_candidate to keep a value from being read as current | src/knowledge.rs:87-113; src/knowledge.rs:165-210; src/knowledge.rs:943-995; src/knowledge.rs:1849-1898; src/cli.rs:3240-3252; src/duel.rs:397-450 | EntryStatus holds active, contested, stale, quarantine_candidate and superseded. add_fact_core writes the duel's verdict into status (knowledge.rs:775) and retire_loser sets the displaced value stale or superseded. hidden_status_must_not derives the excluded set from is_default_visible, and query_facts, find_facts_by_subject_predicate and the session briefing all apply it, so a hidden value is neither returned, briefed nor duelled against | build_context_hides_a_dampened_fact_but_shows_the_live_one (tests/cli_integration.rs:2731-2794) asserts the stale loser absent from the briefing beside the winner. contested withholds nothing: a loser re-asserted inside the flip-back window returns to the fact query and the briefing beside the winner, labelled disputed, and leaves the as-of timeline, and the axis takes no further duel until a person answers; a loser first re-added after the window duels afresh and can flip back; quarantine_candidate needs a rival with a migration-written dependants count or some forty assertions; memories carry a separate quarantined boolean outside this state"
  bitemporal: "fact store — a caller-supplied valid_from beside the record-time created_at, and a world_until that a dated successor writes on the value it displaces, both read by the world-time as-of query | src/knowledge.rs:649-652; src/knowledge.rs:784-786; src/knowledge.rs:855-862; src/knowledge.rs:1147-1168; src/knowledge.rs:1241-1324; src/mcp.rs:1161-1164; src/http_api.rs:1043-1051; src/cli.rs:3595-3623 | valid_from is written only when a caller passes it — the valid_from argument of mind_fact add, the body field of HTTP /fact/add, or mgimind fact add --valid-from — and a re-add without one keeps the stored value; nothing defaults it to the write clock. On a flip, add_fact_core sets the loser's world_until to the winner's valid_from. query_fact_as_of with world_time tests valid_from falling back to created_at as the start and world_until falling back to valid_until as the end, where the default tests created_at and valid_until | world_time_as_of_differs_from_record_time_as_of (tests/cli_integration.rs:3701-3770) asserts at 2020-06-01 the record-time slice empty and the world-time slice holding the 2020 value and not the 2023 one, and at 2024-06-01 the 2023 value without the 2020 one. world_until is written only by an add_fact_core flip whose winner is dated, so an undated successor and migrate-v14 redo-duels close on record time; it is read only by the world-time as-of; dates are unvalidated strings compared lexicographically, and nothing orders world_until after the loser's own valid_from; ingest and the extractor never set either"
  audit_log: "an append-only, hash-chained NDJSON file records memory, fact, procedure, skill, pinned-block, backup-restore and review mutations | src/audit.rs:36-122; src/audit.rs:282-326; src/knowledge.rs:878-901; src/storage.rs:2542-2571; src/consolidate.rs:294-315; src/procedure.rs:124-130; src/skill.rs:188-213; src/storage.rs:649-690; src/storage.rs:4993-5017; src/review.rs:208-213; src/review.rs:274-300; src/viewer.rs:534-538 | record() appends under an in-process mutex and a cross-process file lock, reading the tail afresh to chain each line to the BLAKE3 of the previous one, and audit verify reports the first break. Every declared AuditOp has a producer: memory add, update, delete, quarantine, archive and restore, fact add with its verdict and retired loser, fact invalidate and restore, procedure and skill writes, outcomes and removal, pinned-block set with the prior content and remove with the removed content, a consolidate summary beside a Delete row per removed memory, a backup_restore row naming the archive and the side copy of the replaced log, a review_ask row for an agent's question, and a review_answer row naming the human surface for each accepted or rejected fact and each refused PIN | fact_add_audits_the_verdict_and_the_retired_loser, procedure_and_skill_writes_land_in_the_audit_log, consolidate_apply_audits_the_bulk_delete_and_its_own_summary and quarantine_promote_attributes_the_real_actor_not_relevance_gate (tests/cli_integration.rs:2986-3344), pinned_block_writes_land_in_the_audit_log (:3904-3943), and the restore assertions in backup_and_restore_round_trip_facts_through_qdrant_snapshots (:2095-2209). No rotation or prune exists; recording is best-effort, a warning on failure; a restore that fails after unpacking audit.log, as a Qdrant snapshot upload can, leaves the side copy and no backup_restore row; a contested write enters the review queue on its fact_add row alone, with no review_ask"
  human_review: "fact store — a fact that lands contested, or that an agent asks about, carries review = pending until a person accepts or rejects it at a terminal or with a PIN the agent's tools cannot supply | src/review.rs:44-46; src/review.rs:173-215; src/review.rs:226-302; src/review.rs:319-367; src/knowledge.rs:563-574; src/knowledge.rs:678-690; src/knowledge.rs:798-809; src/knowledge.rs:1367-1373; src/cli.rs:1400-1430; src/mcp.rs:1068-1094; src/viewer.rs:491-546 | add_fact_core stamps review = pending on every contested write, and review::ask on any live fact an agent names; while a fact is pending or accepted no duel runs against it and invalidate refuses it. accepted and rejected have one writer, review::answer, with two callers: mgimind review accept or reject, which refuses unless stdin and stdout are terminals and then wants the fact's short id typed back, and the viewer's POST /api/review/:id, which checks an Argon2id PIN hash beside the bearer token. mind_review's action enum is list and ask, and the HTTP API has no review route. The answer is read: an accepted value is written active and its single-valued rivals retired as rejected, and re-adding a rejected triple is refused with verdict rejected | contested_fact_waits_on_a_person (tests/cli_integration.rs:4121-4301) asserts the queue entry and its label, invalidate refused, accept and pin refused off a terminal, 403 on a wrong PIN and 200 on the right one, the rival retired and its re-add refused; the test plants the PIN hash file itself. A pending value is returned, labelled disputed; an agent with a general shell can satisfy the terminal check with a pseudo-terminal, replace the PIN hash under MGIMIND_HOME, or set the payload through the loopback Qdrant, which takes no API key by default; mind_review ask returns an accepted fact to pending; the rejected refusal matches the exact triple, not a case or whitespace variant; re-registering the predicate multi lets a contradiction of an accepted value land active; memories have no review state"
  negative_eval: "a value that lost a duel, a hidden record, an invalidated triple's variant, a superseded value on the world axis, a rival a person rejected and another library's material must not be returned, each beside a positive control in the same run | tests/cli_integration.rs:905-963; tests/cli_integration.rs:972-1044; tests/cli_integration.rs:2731-2971; tests/cli_integration.rs:3701-3899; tests/cli_integration.rs:4121-4301; tests/http_integration.rs:581-1010; .github/workflows/ci.yml:85-102 | duel_rule_dampens_loser_on_single_cardinality asserts the query holds the new value and not the old; temporal_single_supersedes_prior_value asserts Munich present and Berlin absent by default and the reverse in history; the visibility tests assert a stale fact, an archived memory and a skill absent from the briefing, history and by-author beside a live record; the variant test refuses an invalidated triple's variant and accepts a different object; the world-time test excludes the 2020 value at 2024 beside the 2023 one; the review test asserts the rejected rival absent beside the accepted value; http_v2_acl_flood_verdict_contract asserts a scoped token gets no canary memory, an empty facts array and empty procedures_text from JSON recall after an unscoped token finds all three | CI runs both cli_integration and http_integration with Qdrant, models and ONNX Runtime set, on Linux and Windows. No case plants a quarantine_candidate fact, and none reaches the duel with the challenger's own row among the visible rows"
stack_storage: "qdrant, files"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "Three kinds in one Qdrant instance: a memory chunk of up to 500 characters keyed by a UUIDv5 of library and content; a vectorless fact triple keyed by a UUIDv5 of subject, predicate and object with a lifecycle status, a review state, a confirmation count, and an optional world-time valid_from and world_until; and procedures and skills stored as typed points in the memories collection"
  storage: "A local Qdrant the binary downloads and starts on loopback: a memories collection with dense and sparse vectors, a _kg_facts collection, a predicate registry and a procedure-stats side collection. Files under MGIMIND_HOME hold the audit log, session logs, pinned blocks, an access journal and an encrypted vault"
  retrieval: "Memories: dense multilingual-e5-base and a sparse term-frequency arm fused by RRF in one Qdrant query, then a bge-reranker-base cross-encoder over the top 20, filtered by optional library, author, source and date. Facts: full-text match on subject, predicate or object with the hidden statuses excluded, and an as-of slice on record time or world time. Procedures and skills: dense plus sparse over their own type"
  write: "Explicit tools: mind_add writes directly; mind_ingest runs a secret scan, a cheap relevance gate, a token-novelty check and a near-duplicate check, routing rejects to quarantine; mind_fact add refuses an invalidated triple or its case and whitespace variant, then runs the duel rule under a per-axis and a cross-process lock, and a contested result is queued for a person. An optional local Qwen extractor is behind a cargo feature that is off by default"
  update_delete: "Memories: content-addressed upsert, delete by id, soft archive and restore, quarantine promote and expire. Facts: the duel marks a loser stale or superseded with valid_until, and world_until when the winner is dated; a loser re-added within 24 hours lands contested beside the winner and waits on a person, whose accept retires the rivals and whose reject is refused on re-add; invalidate sets valid false and valid_until, and the triple and its case and whitespace variants are refused until an explicit restore"
  scoping: "A library key on every memory, applied as an optional caller filter on MCP and for unscoped HTTP tokens, and enforced for library-scoped HTTP tokens, which reach only confined memory routes and get no facts or procedures from JSON recall. Facts, procedures, skills and sessions are global"
  integration: "MCP over stdio, which the README counts at 30 live tools plus 15 deprecated aliases hidden from tools/list and dispatched by name; a loopback HTTP API with per-agent tokens and a library allowlist; a CLI; a loopback viewer with delete, edit, promote and a PIN-gated review tab; a Python client; an npm wrapper that downloads the release binary. No host hook; AI_INSTRUCTIONS.md asks the model to call mind_session and mind_context at session start"
  background: "Inside the warm MCP process an hourly, load-aware re-test loop recomputes confidence_score on up to 50 entrenched facts per tick and moves the doubt counter; access counts flush to a journal; consolidate, archive and prune are CLI-only"
  trust: "Fact status filters stale, superseded and quarantine_candidate from the fact query, the session briefing and the duel's rival set; contested stays visible, labelled disputed, and pending a person's answer; an invalidated triple and its case and whitespace variants are refused on re-add; memory quarantine is excluded from search and history; the doubt window ships in shadow mode and only reorders"
  strengths: "One status-visibility function drives the Rust gate and every fact reader's Qdrant filter; an explicit invalidate refused on every fact write path, case and whitespace variants included; a world-time end written from the successor's valid_from; a fact review answered only at a terminal or with a PIN, with no answer verb on MCP; per-axis plus cross-process locking around the fact duel; a library-scope canary with positive controls that runs in CI; audit lines chained by BLAKE3 under a cross-process lock, with skill, pinned-block and restore rows; benchmark figures that recompute exactly from committed per-question files"
  risks: "On the default path a once-asserted fact younger than about four months flips to any contradiction; a contested value is returned beside the winner while it waits on a person, and one open question stops every duel on its axis; an agent's ask reopens an accepted fact, and the review gate assumes an agent without a shell; library scope is optional on MCP"
---

## 1. Executive Summary

MGI-Mind is a single Rust binary that gives an assistant long-term memory over
MCP, backed by a local Qdrant it downloads and runs on loopback. It stores three
things: text memories with hybrid dense and sparse retrieval and a
cross-encoder rerank; fact triples governed by a *duel rule* that resolves a
contradiction on a single-valued predicate; and error-to-fix procedures and
skills. A relevance gate sends low-signal ingest candidates to a quarantine
instead of dropping them.

What is notable is the discipline around the fact state. One function decides
which statuses are hidden, and every fact reader's Qdrant filter is derived from
it: the query, the duel's rival set and the session briefing. A fact's id is its
value, and an explicit invalidate is final: every fact write path refuses the
invalidated triple, and any triple equal to it up to case and whitespace, until
a restore. Facts take an optional world-time `valid_from`
beside the record clock, a dated successor writes the end of its predecessor's
world interval, and an as-of query reads either axis.

What is weak is the duel. On the default path a fact asserted once flips to any
contradiction while younger than about four months. A loser re-asserted inside
the default 24-hour window lands `contested`, which hides nothing: both values
return, the contested one labelled disputed. On MCP the library is a caller's
option; only a library-scoped HTTP token is held to it.

A contested fact waits on a person. Every contested write carries
`review = pending`, and the agent's `mind_review` tool can list the queue and
ask a question but not answer one. An answer comes from
`mgimind review accept|reject` at a terminal, or from the viewer with a PIN set
at a terminal. The gate holds against the MCP tool surface; an agent that also
holds a shell can reach past it.

Six marks: `tombstone`, `trust_state`, `bitemporal`, `audit_log`,
`human_review` and `negative_eval`. Section 9 names the one withheld.

## 2. Mental Model

There are two belief stores with different admission rules, and they do not
share a state machine.

**A memory becomes a belief when it is written, and stays one until deleted or
archived.** `mind_add` writes directly. `mind_ingest` runs a secret scan, a
cheap relevance gate on length, blacklists and decision markers, and a token
novelty check against three neighbours (`src/ingest.rs:293-386`). A candidate
that fails is stored with `quarantined = true` and a reason, and ordinary search
and history exclude it (`src/storage.rs:385-405`). The same content arriving
again promotes it, so repetition is the admission test. Nothing judges whether a
memory is true.

**A fact becomes current by winning a duel.** A triple is keyed on its own
value, a UUIDv5 of subject, predicate and object (`src/knowledge.rs:379-382`).
For a predicate registered `Single` or `TemporalSingle`, a new object that
differs from a visible valid one triggers `resolve_against_existing`. The duel
compares the newcomer's weight with the entrenchment of the strongest visible
row on the axis and returns flip, contested or quarantine
(`src/duel.rs:277-285`, `:303-345`). A flip writes the newcomer `active` and
retires the loser: `stale` for `Single`, `superseded` for `TemporalSingle`,
each with `valid_until = now` (`src/duel.rs:397-450`). When the winner carries
a `valid_from`, the loser also gets `world_until` set to it
(`src/knowledge.rs:855-862`).

**On the default path the duel leans on recency.** A newcomer weighs
`0.1 · log2(1 + c)` in the default `ChatOnly` mode, where `c` is its own
confirmation count, 1 on a first write (`src/knowledge.rs:648`, `:706-715`;
`src/duel.rs:210-231`; `src/install_mode.rs:57-61`). Every write of a triple
raises its `confirmations_count` by one, whoever sends it. Entrenchment sums log
terms for dependants, confirmations and age and divides by 50
(`src/duel.rs:121-129`); `dependants_count` is written only by `mgimind
migrate-v14 dependants --apply` (`src/migrate_v14.rs:404`).

A flip needs entrenchment below the newcomer's weight divided by 1.5. A rival
asserted once loses to a first-time contradiction while younger than about four
months. Each re-assertion of the rival shortens that window, and from about ten
it never flips to a first mention; it lands `contested`, where both values stay
visible. `quarantine_candidate` needs entrenchment at least twice the newcomer's
weight, which without dependants takes some forty assertions of a two-year-old
rival. These thresholds were computed from the code, not run.

**How a fact stops being one.** A duel loser is hidden, not deleted. Re-adding
it rewrites the whole payload with its original `created_at` and its own count
plus one, which drops its `valid_until` and `world_until`
(`src/knowledge.rs:637-652`, `:767-827`). If it lost within
`flip_back_window_hours` of the re-add, 24 by default and 0 to disable, a
winning duel writes it `contested` and leaves the winner in place; after the
window it flips the winner back (`src/knowledge.rs:310-334`, `:629-634`,
`:736-741`; `src/config.rs:103-112`).

**A contested write waits on a person.** `add_fact_core` stamps every
`contested` write `review = pending` with a stock question, and
`mind_review action=ask` does the same to any live fact the agent names
(`src/knowledge.rs:798-809`; `src/review.rs:173-215`). While one row on an axis
is pending or accepted, a contradicting write skips the duel and lands
`contested` too, so the axis takes no flip until a person answers
(`src/knowledge.rs:678-690`).

Accept writes the fact `active` and, on a single-valued predicate, retires
every visible rival as `rejected`. Reject retires the fact itself
(`src/review.rs:226-302`). A re-add of a rejected triple is refused with verdict
`rejected`, ahead of the invalidation check (`src/knowledge.rs:563-574`).

An invalidate is different. It sets `valid = false` and `valid_until`
(`src/knowledge.rs:1337-1424`). Before any duel, `add_fact_core` reads that
field on the row the triple's id addresses, then scans every `valid = false`
row for one equal under `tombstone_key`: whitespace runs collapsed, ends
trimmed, lowercased. Either match refuses with verdict `invalidated` and the
invalidated row's id, writing nothing but an audit row
(`src/knowledge.rs:303-308`, `:336-377`, `:594-628`). `restore` is the only way
back (`:1436-1503`).

```mermaid
%% caption: how a memory and a fact each become current in MGI-Mind, where an invalidated triple or its variant is refused, the two paths that bring a duel loser back, and where a contested fact waits on a person
flowchart TD
    I["mind_ingest candidate"] --> G{"secret scan, relevance<br/>gate, novelty,<br/>near-duplicate"}
    G -- "passes" --> M["live memory, returned<br/>by search and history"]
    G -- "fails" --> Q["quarantined = true,<br/>hidden from search<br/>and history"]
    Q -- "re-ingested<br/>or promoted" --> M
    A["mind_add,<br/>no gate"] --> M
    M ~~~ F
    F["mind_fact add s,p,o<br/>from MCP, HTTP,<br/>CLI or ingest"] --> T{"own row has<br/>valid = false, or an<br/>invalidated row equal<br/>up to case and<br/>whitespace?"}
    T -- "yes" --> R["refused with that<br/>row's id,<br/>nothing written"]
    T -- "no" --> C{"single-valued<br/>predicate with a<br/>visible rival object?"}
    C -- "no" --> ACT["status active,<br/>confirmations + 1"]
    C -- "yes" --> D{"duel: own<br/>confirmations against<br/>the most entrenched<br/>visible row"}
    D -- "young rival,<br/>asserted once" --> FLIP["newcomer active,<br/>rival stale or<br/>superseded,<br/>valid_until = now,<br/>world_until = winner's<br/>valid_from if dated"]
    D -- "older or<br/>re-confirmed" --> CON["newcomer contested,<br/>review = pending,<br/>both visible,<br/>labelled disputed"]
    D -- "about forty<br/>confirmations<br/>or dependants" --> QC["quarantine_<br/>candidate,<br/>hidden"]
    FLIP --> RE{"rival's value<br/>re-added: lost<br/>within 24 hours?"}
    RE -- "yes, and it<br/>would win" --> CON
    RE -- "no" --> D
    CON --> RV{"a person answers:<br/>terminal command, or<br/>viewer with the PIN"}
    RV -- "accept" --> ACC["active, confirmed;<br/>single-valued rivals<br/>retired as rejected"]
    RV -- "reject" --> REJ["retired; a re-add<br/>is refused<br/>as rejected"]
    RE ~~~ INV
    INV["mind_fact invalidate"] --> X["valid = false, hidden"]
    X -- "mind_fact restore" --> RS["valid = true,<br/>prior status back"]
```

## 3. Architecture

`mgimind` is a CLI whose `mcp` subcommand is the MCP server over stdio and whose
`serve-http` subcommand is a loopback HTTP surface over the same dispatcher
(`src/mcp.rs:37`; `src/http_api.rs:1-18`). Embedding runs in process through
ONNX Runtime: `multilingual-e5-base` by default, with a `bge-reranker-base`
cross-encoder on by default (`src/config.rs:118-135`). The models stay warm for
the life of the MCP process.

Qdrant holds four collections: `memories`, with named dense and sparse vectors
and payload indexes on library, author, source, type and `created_at`;
`_kg_facts`, vectorless; `_kg_predicates`, the cardinality registry; and
`_mod_procstats`, derived procedure statistics (`src/storage.rs:26-35`).
Procedures and skills live in `memories` as typed points in the `_procedures`
and `_skills` libraries (`src/storage.rs:2628`, `:3451-3452`).

Files under `$MGIMIND_HOME` hold the rest: `audit.log`, per-agent session logs,
pinned blocks rendered at the top of every briefing, the access journal used by
decay, and the AES-GCM vault, which is terminal-only.

Inside the MCP process a background loop re-tests entrenched facts hourly by
default, yields while a tool call is in flight, and caps each tick at 50 facts
(`src/doubt.rs:62-71`; `src/mcp.rs:70-79`). An optional local extractor, a
Qwen GGUF behind `llama-server`, exists only with `--features extractor`, which
the default build leaves off (`Cargo.toml`).

### Deployment and ergonomics

One binary plus what `doctor --fix` downloads: Qdrant, ONNX Runtime, and two
quantized models the README puts at about 270 and 280 MB, checked against
pinned SHA-256 where pinned. A Docker image bundles everything. An npm package
under `packaging/npm/` downloads the release binary for the platform in a
`postinstall` script, checks it against the `.sha256` file published beside it
in the same release, and unpacks it; `server.json` registers that package as an
MCP server. No API key is needed and nothing leaves the machine. Qdrant's store
is not readable by hand; `export --format md` and `backup` are the repair route,
and the audit log is grep-able NDJSON.

## 4. Essential Implementation Paths

**Memory write.** `mind_add` → `storage::add_memory_authored`
(`src/storage.rs:1423-1539`): refuse an unregistered library, refuse a secret,
chunk at 500 characters with overlap, embed, keep the original `created_at` for
an existing id, upsert, and append an `Add` audit row.

**Ingest.** `mind_ingest` → `ingest::run_ingest_authored`
(`src/ingest.rs:232-522`). For a memory candidate: secret scan, `check_cheap`,
then `top_k_neighbor_content` and `novelty_ratio` against `min_novelty`. A
quarantine verdict first tries `promote_from_quarantine` on the same id, then
checks for a live duplicate, then calls `add_quarantined`. A pass with
`nearest_score ≥ 0.95` is skipped as a near-duplicate and parked in quarantine
with reason `near_dup_drop` (`:383-436`). Fact and procedure candidates go to
their own stores, unless a library-scoped HTTP token set `_confine_extraction`.

**Memory search.** `mind_search` → `storage::search_filtered`
(`src/storage.rs:2248-2380`): embed the query, record it in the activity buffer
for the doubt window, build the filter with `memory_query_filter_ex`, run dense
and sparse prefetches fused by RRF, rerank, truncate to the tier, and record
access counts in process.

**Fact write.** `mind_fact add` → `knowledge::add_fact_core`
(`src/knowledge.rs:497-901`): take the per-axis mutex and a cross-process file
lock, read this triple's own `created_at`, `valid`, `confirmations_count`,
`valid_from`, `status`, `valid_until` and review fields, and refuse it if a
person rejected it, or if it or a case and whitespace variant is invalidated. Then look up the cardinality, fetch visible
rivals, run the duel unless a person holds the axis, upsert, `retire_loser`, set the loser's `world_until`
when the winner is dated, and append a `FactAdd` row with the verdict and any
retired loser. Both MCP and HTTP return the verdict
(`recorded`, `won`, `contested`, `quarantined`, `invalidated`, `rejected`).

**Fact read.** `mind_fact query` → `query_facts`, `query_fact_history` or
`query_fact_as_of` (`src/mcp.rs:1178-1195`). `query_facts` filters `valid =
true`, excludes the hidden statuses, matches the term as full text on any of
the three fields, and runs the doubt-window drift check
(`src/knowledge.rs:943-995`). `query_fact_as_of` reads `active`, `superseded`
and `stale` rows only, and `world_time` chooses both bounds (`:1241-1324`).
All three render through `render_facts`, which prints the record-time interval
and a review label: disputed for a `contested` or pending fact, confirmed for
an accepted one (`src/cli.rs:3626-3657`; `src/review.rs:306-313`).

**Unified recall.** `mind_recall_all` fuses facts, a `search` with no library,
and procedures (`src/mcp.rs:393-447`).

**Session start.** `mind_context` → `cli::build_context`
(`src/cli.rs:3217-3426`): an operating rule, pinned blocks, the skill catalogue,
the last session, the 20 newest visible facts, the library list, a quarantine
digest and a count of the facts waiting on a person.

**Forget.** `mind_delete` → `delete_memory`, with the content snapshotted into
the audit row (`src/storage.rs:3382-3418`). `consolidate --apply` merges
near-duplicates, then archives or prunes cold memories, logging a `Delete` row
per removed memory and one `Consolidate` summary (`src/consolidate.rs:276-315`).
`mind_fact invalidate` hides a fact; nothing deletes one.

## 5. Memory Data Model

| Store | Key | Fields that matter |
| --- | --- | --- |
| memory point | UUIDv5 of `library` and trimmed content | `content`, `hash`, `library`, `type`, `source`, `author`, `created_at`, `updated_at`, `quarantined`, `quarantine_reason`, `archived`, `embed_model`, chunk position |
| fact point | UUIDv5 of subject, predicate, object | `valid` as a string, `status`, `created_at`, `updated_at`, `valid_from`, `valid_until`, `world_until`, `review`, `review_question`, `reviewed_by`, `reviewed_at`, `confirmations_count`, `author`, `origin_context_id`, later `dependants_count`, `confidence_score`, doubt count |
| predicate | UUIDv5 of the predicate | cardinality: `Single`, `TemporalSingle` or `Multi`, default `Multi` |
| procedure | UUIDv5 of normalised error and fix | trigger error, context, fix, provenance; counts in `_mod_procstats` |

**Scope is a library on memories and nothing on facts.** A memory carries
`library`, and a query may filter on one or several. Facts, procedures, skills,
sessions and pinned blocks are global (`src/http_api.rs:690-702`).

**Time.** A fact carries two start bounds and two ends. `created_at` is the
record time of its first write and survives re-adds (`src/knowledge.rs:637`).
`valid_from`, when a caller supplies one, is when it became true in the world,
and a later re-add without one keeps it (`:649-652`, `:784-786`). `valid_until`
is the system clock at retirement or invalidation. `world_until` is the
winner's `valid_from`, written on the loser of a flip whose winner is dated
(`:855-862`).

The record-time slice tests `[created_at, valid_until)`; the world-time slice
tests `[valid_from or created_at, world_until or valid_until)`
(`:1141-1168`). Nothing else reads `world_until`: history and the current-value
query read status, and `render_facts` prints `created_at .. valid_until` on
either axis. An undated successor, and the operator's `migrate-v14 redo-duels
--apply` retire pass, leave the loser's world end at record time
(`src/cli.rs:2506-2526`). Dates are stored as given and compared as strings,
and nothing checks that `world_until` falls after the loser's own `valid_from`.

**Content addressing has consequences.** Editing a memory writes a new point
and deletes the old one (`src/storage.rs:1311-1335`). Re-adding identical text
upserts the same point and clears any `quarantined` or `archived` flag, because
the payload is rebuilt. For a fact the same identity is what makes the
invalidation durable.

## 6. Retrieval Mechanics

Memory retrieval is hybrid by default: a dense arm over e5 vectors and a sparse
arm over a hashed term-frequency vector, each limited to `rerank_top_k` (20)
and fused with RRF inside one Qdrant Query API call. The cross-encoder then
re-scores and sorts, and the score is mapped through a sigmoid
(`src/storage.rs:2289-2356`). Tiers truncate the text to about 100 or 500
characters, or return it whole.

**One base filter excludes procedures, skills, quarantined points and archived
points** (`src/storage.rs:385-405`), and every memory listing builds on it:
search, browse, history and by-author (`:2299`, `:4127`, `:4300`, `:4363`).
Archived points can be asked for explicitly through the filter's archived scope.

Fact retrieval is a full-text payload match, not semantic. The doubt window
measures, per surfaced fact, how far the current query centroid has drifted
from the context the fact was written in, using corpus-mean-centred cosine. In
`enforce` mode with a calibrated threshold it sorts doubted facts last. The
default mode is `shadow`, which only records (`src/config.rs:15-17`;
`src/doubt.rs:211-265`). Nothing is hidden by doubt in either mode.

Retrieval is tool-mediated. `mind_should_search` classifies a query and returns
advice; it cannot force a search.

## 7. Write Mechanics

Every write is an explicit tool or CLI call; the default build calls no model.
Memory writes block on embedding, one batched pass per add, and are searchable
as soon as the upsert returns, since writes use `wait(true)`.

**Deduplication is by identity and by neighbourhood.** Identical text in the
same library lands on the same id. Ingest also skips a candidate whose nearest
neighbour scores at least 0.95, and parks it in quarantine so a later
re-assertion can restore it. `mind_add` and HTTP `/memory/add` skip the
relevance gate entirely, which is why HTTP adds a per-author write quota
(`src/http_api.rs:509-550`).

**Agent-generated content is treated like the user's.** The relevance gate
checks form, not truth. `mind_web` fetches a page and can save it to a library.
The secret scanner refuses a key-like string and points at the vault, on every
write path including quarantine (`src/storage.rs:1437-1448`, `:1563-1569`).

**A re-assertion is a confirmation, whoever makes it.** `confirmations_count`
rises by one on every write of the same triple, from any agent or the same one
(`src/knowledge.rs:648`, `:777-780`). It feeds the triple's own weight as a
challenger and its entrenchment as a rival, so repeating a value is how it
resists the next contradiction.

**The inheritance discount is narrow.** `build_context` marks every fact it
briefs as inherited in a process-local set (`src/cli.rs:3280-3290`;
`src/doubt.rs:906-929`), and `add_fact_core` halves a challenger's weight when
that challenger's own triple is in the set (`src/knowledge.rs:697-715`). A
briefed fact was visible, so on a single-valued predicate the discount reaches
one side of a contested pair, or a value that lost after the briefing.
Re-asserting a briefed winner that stands alone raises no duel. The set lives in one process,
so `mgimind context` from a terminal marks nothing in the MCP server.

### Operational cost

- Write: synchronous embed and upsert; facts are vectorless and pay two locks
  and a few payload reads. No LLM on the default path.
- Background: one re-test pass per hour by default, at most 50 facts per tick,
  each a payload read and a `confidence_score` write. No whole-store rewrite
  runs unattended; `consolidate` is an operator command.
- Read: one embed, one fused query, and a cross-encoder pass over 20 candidates,
  which the README puts at one to two seconds on CPU. Injection is whatever the
  agent asks for, at the tier it picks; `mind_context` is bounded by its fixed
  sections.

## 8. Agent Integration

The README counts 30 live MCP tools plus 15 deprecated aliases. `tools/list`
hides the aliases unless `MGIMIND_LIST_DEPRECATED=1`, and the dispatcher
serves them (`src/mcp.rs:1324-1345`). Each listed tool carries read-only,
destructive and idempotent hints (`:1975`). The model holds every verb but one: add,
ingest, search, fact add, invalidate and restore, predicate registration,
quarantine list, promote and expire, restore, delete, export and import,
sessions and pinned blocks. `mind_review` carries `list` and `ask` and no
answer (`src/mcp.rs:1068-1094`). Vault tools return terminal instructions, never
a secret.

No host hook is installed. `AI_INSTRUCTIONS.md` asks the assistant to call
`mind_session(action="last")`, `mind_session(action="start")` and `mind_context`
at the start of every session, search before answering, and close the session
with a summary. Continuity therefore depends on the model following the
instruction file. A separate CLI command ingests a finished Claude Code
transcript through the same gate (`src/session_ingest.rs:1-15`).

The HTTP surface is the multi-agent door. A token can be anonymous, named, or
named and confined to libraries. A named token's identity overrides any
`X-Agent` header for authorship (`src/http_api.rs:490-508`).

## 9. Reliability, Safety, and Trust

**The status filter has one source of truth, and every fact reader uses it.**
`hidden_wire_strings` derives the hidden set from `is_default_visible`, and
`hidden_status_must_not` turns it into the Qdrant `must_not` used by
`query_facts`, the duel's rival set, `list_all_facts` and the session briefing
(`src/knowledge.rs:165-210`, `:962`, `:1874`; `src/cli.rs:3240-3252`). The
comments record the drift that leaked `stale` and then `quarantine_candidate`
before the derivation existed, the second through the briefing.

**`contested` hides nothing.** It is default-visible, so a damped flip-back
puts the re-asserted loser back into the fact query and the briefing beside the
winner (`src/knowledge.rs:165-170`). `review::label` tags it in the briefing,
`render_facts`, the profile and unified recall: disputed for a contested or
pending fact, confirmed for an accepted one (`src/review.rs:306-313`;
`src/cli.rs:3271-3281`, `:3633-3640`; `src/mcp.rs:411-417`). The briefing also
counts the open questions and tells the model not to treat them as settled
(`src/cli.rs:3403-3416`). The as-of slices whitelist `active`, `superseded` and
`stale`, so while a value sits `contested` it drops out of both time axes
(`src/knowledge.rs:1264-1269`).

**The duel excludes the challenger's own row.** `add_fact_core` filters the row
at the challenger's id out of the visible rows before
`resolve_against_existing` picks a loser, so a re-assertion cannot retire
itself (`src/knowledge.rs:716-723`). On rows written at this pin the filter is
seldom the line that decides: a contested row is pending, and a pending triple
re-asserted against a rival takes the review branch and never duels
(`:681-690`). The filter decides for a `contested` row written before the
review field existed, and for an axis whose predicate was registered
single-valued after several values were stored. This was traced through the
code, not run.

**Only a person's surface writes an answer.** `review::answer` is the one
writer of `accepted` and `rejected`, and it has two callers.
`cmd_review_answer` refuses unless stdin and stdout are terminals, then reads
the fact's six-character short id back (`src/cli.rs:1400-1430`;
`src/review.rs:319-327`). The viewer's `POST /api/review/:id` checks the bearer
token and then a PIN against an Argon2id hash in `$MGIMIND_HOME/review_pin`,
which `mgimind review pin` writes only at a terminal. Five wrong PINs lock
answers for fifteen minutes (`src/viewer.rs:483-546`; `src/review.rs:331-367`;
`src/cli.rs:1432-1445`).

`mind_review` dispatches `list` and `ask` and rejects any other action, and no
HTTP API route names review (`src/mcp.rs:1068-1094`). A pending or accepted fact
is refused by `invalidate`, and `migrate-v14 redo-duels` skips its axis
(`src/knowledge.rs:1367-1373`; `src/cli.rs:2514-2522`).

**The gate is on the tool surface, not the machine.** `at_terminal` tests
`is_terminal` on two descriptors, which a pseudo-terminal satisfies, and the
short id is printed in the queue. The PIN hash is a file, and the README says
an agent that can write `$MGIMIND_HOME` could replace it. Qdrant listens on
loopback with no API key unless `qdrant_api_key` is set, so a local process can
set the `review` payload directly (`src/cli.rs:4494-4513`). The PIN lockout is
counted in the viewer process and starts at zero in each one. None of these is
a verb the MCP server declares.

**Three tool calls soften an answer.** `ask` refuses a rejected fact and not an
accepted one, so an agent's question returns a confirmed fact to pending; it
stays protected and loses its confirmed label (`src/review.rs:183-207`). The
rejected refusal reads the row at the triple's exact id, so `berlin` after a
rejected `Berlin` is a new fact (`src/knowledge.rs:563-574`). And
`mind_predicate register` overwrites a cardinality unchecked, so re-registering
a predicate `multi` lets a contradiction of an accepted value land `active`
beside it (`src/knowledge.rs:1520-1552`; `src/mcp.rs:1258-1279`).

**Locking around the duel is careful.** A per-(subject, predicate) async mutex
serialises agents in one process, and `lock_facts_cross_process` extends it to
separate `mgimind` processes; invalidate and restore take the same file lock
(`src/knowledge.rs:417-471`, `:1346`, `:1443`).

**The invalidation is consulted on every write path, and matched loosely.** The
refusal sits at the top of the one function every fact writer reaches: MCP
`mind_fact` and its legacy alias, HTTP `/fact/add`, `mgimind fact add`,
`mind_ingest` and the feature-gated extractor (`src/mcp.rs:768`, `:1162`;
`src/http_api.rs:1044`; `src/cli.rs:3604`; `src/ingest.rs:487`). Nothing
deletes a fact point; the one collection drop, a vectorless migration,
re-inserts every payload (`src/storage.rs:922-950`). `mind_ingest` counts a
refused fact in `stored_facts` (`src/ingest.rs:487-489`).

The loose key is local to the refusal. The id, the duel's conflict test and
the rival lookup compare exact strings, so `Berlin` and `berlin` on a `Single`
predicate duel each other (`src/knowledge.rs:226-231`, `:1863-1868`).
`tombstone_key` lowercases and collapses Unicode whitespace but applies no
Unicode normalisation, so a precomposed and a decomposed `ü` differ. A variant
row written before the invalidate stays visible, and re-asserting it is
refused. The variant check scrolls every `valid = false` row on each fact
write, under both locks (`src/knowledge.rs:336-377`).

**Library scope holds for a scoped token and is optional elsewhere.** The route
gate admits a library-scoped HTTP token only to memory routes that apply its
allowlist (`src/http_api.rs:703-744`). Its JSON `/memory/recall` returns no
facts and no procedures, and the text form is refused
(`src/http_api.rs:432-487`, `:833-847`). On MCP, and for unscoped or anonymous
HTTP tokens, the library is a caller's filter, and `mind_recall_all`,
`mind_history` and `mind_context` take none.

**Audit coverage and its edges.** Every declared `AuditOp` has a producer.
Promote and expire record the calling agent, and `relevance-gate` remains only
on the automatic ingest path (`src/storage.rs:1676-1696`; `src/ingest.rs:339`).
`skill::remove` writes `skill_remove` with the removed text, and the pinned-block
writers write `block_set` with the prior content and `block_remove` with the
removed content, inside the functions every CLI, MCP and HTTP caller reaches
(`src/skill.rs:188-213`; `src/storage.rs:649-690`). `review::ask` writes `review_ask`, and
`review::answer` writes `review_answer` with actor `human:terminal` or
`human:viewer-pin`, one row per retired rival; the viewer adds one per refused
PIN (`src/review.rs:208-213`, `:274-300`; `src/viewer.rs:534-538`). A contested
write enters the queue on its `fact_add` row alone. Nothing rotates or prunes
`audit.log`, and `record` logs a warning when an append fails
(`src/audit.rs:310-326`).

**A restore keeps the log it replaces.** Before a backup's `audit.log` is
unpacked, `restore_archive_inner` copies the live log to
`audit.log.pre-restore-<UTC stamp>`, and after a successful restore a
`backup_restore` row naming the archive and that copy is chained onto the
restored log (`src/storage.rs:4993-5017`, `:5055-5066`). Rows written after the
backup survive only in the copy, which no `audit verify` reads. Snapshots
upload to Qdrant after every file is unpacked, so a restore failing there
leaves the replaced log and the copy with no `backup_restore` row
(`:5074-5104`).

**Privacy.** Delete removes the point and keeps the truncated content in
`audit.log`. Backups can be encrypted with a passphrase.

Capability marks:

- `tombstone` — awarded on the fact store. The rejected value is the key of its
  row, and the writer reads that row, and every invalidated row equal to it up
  to case and whitespace, and refuses the value until a restore. A duel loser is
  not covered, and memories have no equivalent: a quarantined memory is
  promoted by re-assertion, the opposite of a tombstone.
- `trust_state` — awarded. The fact `status` enum carries states that withhold a
  value, and every fact reader filters on them. `contested` is not one of them.
- `bitemporal` — awarded on the fact store. `valid_from` is a world time a
  caller supplies, kept apart from `created_at`, and a flip to a dated winner
  writes the loser's `world_until`. The world-time as-of reads both. An undated
  successor closes the world interval at record time.
- `audit_log` — awarded; the edges are above.
- `human_review` — awarded on the fact store. A contested or asked-about fact
  holds `review = pending`, and the answer has one writer, reached from a
  terminal-gated command and a PIN-gated viewer route. The agent's
  `mind_review` declares neither. The gate assumes an agent without a shell,
  and `ask` reopens an accepted fact. Memories are outside it: the agent holds
  `mind_quarantine(action="promote"|"expire")` for them.
- `negative_eval` — awarded; section 10.
- `scope_enforced` — withheld. The boundary is real for a library-scoped HTTP
  token on every route it reaches. On MCP and for unscoped tokens the library is
  an optional caller filter, and three read tools take none.

## 10. Tests, Evals, and Benchmarks

Nothing was built or run for this report. Everything below is from reading the
tests and the committed result files at the pin, apart from the recall figures,
which I recomputed with a standalone script over the committed JSON.

**The negative cases.** `duel_rule_dampens_loser_on_single_cardinality`
registers a `Single` predicate, adds `old_winner` and then
`new_value_should_flip` over MCP, and asserts the query contains the new value
and not the old (`tests/cli_integration.rs:905-963`).
`temporal_single_supersedes_prior_value` asserts `Munich` present and `Berlin`
absent in the default query, and the reverse in the history query
(`:972-1044`). Three visibility tests plant a hidden record beside a live one
and assert the stale fact absent from the briefing, and an archived memory and a
skill absent from history and by-author (`:2731-2971`).

**The scope canary runs in CI.** `http_v2_acl_flood_verdict_contract` plants a
canary memory in a library a scoped token cannot see, and a fact and a procedure
in the global stores. An unscoped token finds all three; the scoped token gets
none of them from search, by-agent, browse or JSON recall, where `facts` is
`[]` and `procedures_text` is empty (`tests/http_integration.rs:581-1010`). CI
runs `cli_integration` and `http_integration` with Qdrant, the models and ONNX
Runtime configured, on Linux and Windows (`.github/workflows/ci.yml:85-102`,
`:143-150`).

**The fact rules have their own cases.**
`explicit_invalidate_is_final_until_restored` asserts the refused re-add, the
absence after it and the return after `restore`
(`tests/cli_integration.rs:3447-3505`).
`invalidated_triple_refuses_case_and_whitespace_variants` re-adds an
upper-cased, padded subject with `berlin  ` and asserts the refusal names the
invalidated id. Its control, `Berlin-Mitte`, is accepted (`:3849-3899`).

`world_time_as_of_differs_from_record_time_as_of` asserts that at 2020-06-01
the record-time slice is empty and the world-time slice holds the 2020 value
and not the 2023 one. At 2024-06-01, between the successor's `valid_from` and
its record time, it holds the 2023 value and not the 2020 one (`:3701-3770`).
`flip_back_within_window_lands_contested` asserts a first contradiction
`won`, the loser's re-add `contested`, both values in the query, and the
loser's value still returned after a fourth write of it (`:3777-3843`). Two older duel tests set the window to 0, and they assert the
flip-back it would damp (`:3512-3612`, `:3626-3694`).

**The review has one end-to-end case.** `contested_fact_waits_on_a_person`
drives A, B, A over MCP and asserts the queue lists A beside its rival and the
query labels it. It then asserts `invalidate` refused, and `review accept` and
`review pin` refused with stdio piped. Against a spawned viewer it asserts 403
for a wrong PIN and 200 for the right one, after which A is confirmed, B is
absent from the query, a re-add of B returns `rejected`, and the audit log
names `human:viewer-pin` (`:4121-4301`).

**The audit tests read the log back after each write** (`:2986-3344`,
`:3904-3943`), each ending in a passing `audit verify`. The restore round trip
asserts the last row is `backup_restore` naming the saved copy, and that the
copy exists (`:2095-2209`).

**Computed and frozen.** `calibration.rs` runs a fixed corpus of conflict
scenarios through the duel formulas with a match-rate floor and a frozen set of
divergences. It exercises the formulas with synthetic entrenchment inputs, not
the counts a live write produces.

**Benchmarks recompute.** R@1, R@5 and R@10, recomputed from three committed
per-question files, each match their log: 85.2, 98.2 and 99.4% for MiniLM
without rerank
(`benchmark/results/2026-06-02-cpu-overnight/run01_minilm_rerank_off/raw.json`),
then 91.6, 98.2 and 99.8% with rerank and 85.6, 97.6 and 99.4% without, on the
v0.12.1 regression pods. The metric is session-level retrieval recall on
LongMemEval-S, and `BENCHMARKS.md` says it is not QA accuracy. The headline row
names `all-MiniLM-L6-v2` as the zero-config default, while
`MindConfig::default` selects `multilingual-e5-base`. The committed e5 runs are
FP16 on a GPU.

**Not covered.** No test plants a `quarantine_candidate` fact. The flip-back
test's fourth write takes the review branch, so no case runs the duel with the
challenger's own row among the visible rows. The review test plants the PIN
hash file itself and sends a wrong PIN where its message names the token alone;
it has no case for the lockout, a terminal accept, a reject answer or `ask`.
The restore test writes nothing between backup and restore, so it cannot show
that the saved copy holds rows the restored log lacks. No paper belongs to the project; the arXiv identifiers in
`docs/design/`, `src/bench_stale.rs` and `src/cli.rs` cite other work.

## 11. For Your Own Build

### Steal

- **Derive the read filter from the visibility rule.** One function says which
  statuses are hidden, and the database predicate is generated from it, so a new
  status cannot be written and left visible by a filter nobody updated.
- **Make the value the key, then read the key before writing.** A
  content-addressed fact id turns "has this value been rejected" into one
  payload read on the row the write would land on, with no separate table.
- **Lock the contradiction check across processes, not just tasks.** A
  per-axis mutex plus a file lock around read, decide, write and retire is the
  smallest thing that makes "one current value" true.
- **Quarantine instead of drop, and log why.** A rejected candidate kept with a
  reason is recoverable and countable; a briefing that summarises the pile by
  reason makes the gate auditable.
- **Give the agent the question and not the answer.** A review tool whose
  action enum stops at `list` and `ask`, with the answer behind a terminal
  check or a secret set at one, cannot clear the queue it fills.
- **Write the negative test with its positive control in the same response.**
  Every visibility and scope case here asserts the live record present and the
  hidden one absent from one result, so an empty result fails.

### Avoid

- **A contradiction rule whose strongest term has no live producer.** When
  entrenchment can earn only age and repetition, the duel rewards whoever
  repeated a value last, and the old value wins the rematch.
- **A review secret kept beside the data.** A PIN hash in the store's own
  directory and a database with no key on loopback hold against a tool surface,
  not against an agent that also has a shell.
- **A parked value that drops off the timeline.** Parking a flip-back as
  `contested` keeps the winner in place, but the as-of slices whitelist three
  other statuses, so the parked value is absent from both time axes while it
  waits.
- **A route gate and a composite route decided separately.** Refusing
  `/fact/query` to a scoped token means nothing if `/memory/recall` serves facts;
  the confinement has to sit in the composite route as well
  (`src/http_api.rs:439-441`).

### Fit

This suits one person running one or a few assistants on one machine who wants
good local retrieval, explicit facts that stay retracted, and a store that keeps
its own audit trail, and who can tolerate a Qdrant process and about 550 MB of
models. It is a poor fit where facts must survive contradiction by a newer but
wrong assertion, because the default duel favours recent repetition. Its fact review is a gate for an assistant confined to the MCP
tools and a convention for one that also holds a shell. As a multi-tenant
boundary it holds only behind library-scoped HTTP tokens, not over MCP.

## 12. Open Questions

- Does any deployment run `migrate-v14 dependants --apply` routinely, and how
  does the duel behave once dependants counts exist?
- Should `mind_review ask` refuse an accepted fact as it refuses a rejected
  one, and should the rejected refusal use the loose key the invalidation uses?
- Should `valid_from` and `world_until` be parsed and normalised before they are
  stored, given that the comparison is lexicographic?
- What does `enforce` mode do to fact ranking on a real store once
  `calibrate` proposes a threshold?

## Appendix: File Index

- **Storage/schema:** `src/storage.rs` (collections, filters, memory and
  quarantine writes, history, procedures, skills, backup), `src/knowledge.rs`
  (facts, `EntryStatus`, cardinality, invalidate and restore, history and
  as-of), `src/review.rs` (review state, the terminal check, the PIN),
  `src/config.rs`.
- **Write path:** `src/ingest.rs`, `src/relevance.rs`, `src/secrets.rs`,
  `src/duel.rs`, `src/install_mode.rs`, `src/provenance.rs`, `src/procedure.rs`,
  `src/skill.rs`.
- **Retrieval path:** `src/storage.rs:2248-2380`, `src/reranker.rs`,
  `src/embedder.rs`, `src/doubt.rs`, `src/activity.rs`.
- **Context assembly:** `src/cli.rs:3217-3426`, `src/session.rs`.
- **Background workers:** `src/doubt.rs:785-900`, `src/confidence.rs`,
  `src/access.rs`, `src/consolidate.rs`, `src/migrate_v14.rs`.
- **MCP/API/SDK:** `src/mcp.rs`, `src/http_api.rs`, `src/viewer.rs`,
  `clients/python/mgimind/_client.py`, `packaging/npm/`, `server.json`.
- **Audit:** `src/audit.rs`.
- **Tests/evals:** `tests/cli_integration.rs`, `tests/http_integration.rs`,
  `src/calibration.rs`, `.github/workflows/ci.yml`, `BENCHMARKS.md`,
  `benchmark/results/`.

### Recorded searches

Checked against the checkout at the pinned revision.

- `grep -rn 'AuditOp::' src | grep -v '^src/audit.rs'` — producers for every declared op, including `FactAdd` (`knowledge.rs`), `ProcedureAdd` and `ProcedureOutcome` (`procedure.rs`, `skill.rs`), `Consolidate` (`consolidate.rs`), `SkillRemove` (`skill.rs`), `BlockSet`, `BlockRemove` and `BackupRestore` (`storage.rs`), `ReviewAsk` (`review.rs`) and `ReviewAnswer` (`review.rs`, `viewer.rs`); `Reanchor` is produced inside `audit.rs`.
- `git grep -n -E 'remove_skill|set_block\(|remove_block\(|save_blocks\(' -- src` — `remove_skill` is called only by `skill::remove`, and `save_blocks` only by `set_block` and `remove_block`, whose callers are `cli.rs` and `mcp.rs`.
- `grep -n -i -E 'rotate|retention|prune|truncate|remove_file' src/audit.rs` — doc comments and `truncate(false)` on the lock file only; the log file is opened with `append(true)` alone.
- `grep -n 'unpack_in' src/storage.rs` — one call, in `restore_archive_inner` (`storage.rs:5068`), after the live-log copy at `:5055-5066`.
- `grep -rn -E 'DeletePointsBuilder::new\(' src` — memories and procstats only; no point deletion targets `FACTS_COLLECTION`.
- `git grep -n -E 'add_fact(_authored|_authored_verdict)?\(' -- src` — callers in `mcp.rs`, `http_api.rs`, `cli.rs`, `ingest.rs` and `extractor.rs`, all through `add_fact_core`.
- `grep -rn '"valid"' src | grep false` — `"false"` is written only by `invalidate_fact_authored` (`knowledge.rs:1387`); `knowledge.rs:350` is the variant scan's filter and the third hit a test comment.
- `git grep -n -w tombstone_key -- src` — `knowledge.rs:303-366` and its unit test only; the id, `detect_conflict` and the rival lookup do not use it.
- `git grep -n -i -E 'unicode_normalization|nfc|nfkc' -- src Cargo.toml` — no match; no Unicode normalisation runs on fact strings.
- `git grep -n -E 'valid_from' -- src ':!src/knowledge.rs'` — hits only in `mcp.rs`, `http_api.rs` and `cli.rs` argument handling; none in `ingest.rs` or `extractor.rs`.
- `grep -n -E 'parse|DateTime' src/knowledge.rs | grep -i -E 'valid_from|world_until'` — no match; both are stored as given.
- `git grep -n -w world_until -- src` — one writer, `knowledge.rs:861` in `add_fact_core`; read by `fact_from_point` (`:1124`) and used only by `fact_valid_at_world_time` (`:1165`) from `query_fact_as_of` (`:1300`).
- `grep -rn -E 'mark_inherited|from_live_session: false' src tests` — one production caller, `cli.rs:3289`; `from_live_session: false` only in a `duel.rs` test.
- `grep -rn -E '"(confirmations_count|dependants_count)"' src | grep -v '^src/duel.rs'` — `dependants_count` is written only by `migrate_v14.rs:404`; `confirmations_count` by `add_fact_core` (`knowledge.rs:779`) and the procedure migration.
- `grep -n 'memory_query_filter' src/storage.rs` — applied by `search_filtered`, `top_k_neighbor_content`, `list_filtered`, `list_memories`, `history` and `by_author`.
- `grep -n 'scoped_route_allowed' -A14 src/http_api.rs` and `sed -n 432,487p src/http_api.rs` — `/memory/recall` allowed; its JSON body skips `query_facts` and `procedure::recall` for a scoped token.
- `grep -n -E 'cargo test --all|cargo test --test (cli|http)_integration' .github/workflows/ci.yml` — both integration targets run on Linux and Windows.
- `git grep -n -E 'quarantine_candidate|QuarantineCandidate' -- tests` — one comment; no case plants the state.
- `git grep -n -E 'world_time' -- tests` — one case, querying 2020-06-01 and 2024-06-01.
- `sed -n 3777,3843p tests/cli_integration.rs | grep -c '"object":"value_A"'` — 3: the first write, the re-add and a fourth write, which follows the pending stamp at `knowledge.rs:798`.
- `git grep -n -E 'review::answer|decided\(' -- src` — `review::answer` is called from `cli.rs:1420` and `viewer.rs:542` only; `decided`, the one builder of `accepted` and `rejected`, is used three times inside it.
- `git grep -n -E 'route\("[^"]*review' -- src` — `viewer.rs:116-117` only; no route in `http_api.rs`.
- `git grep -n -E '"enum": \["list", "ask"\]|answers are human-only' -- src/mcp.rs` — the tool schema at `:1782` and the dispatcher's refusal of any other action at `:1091`.
- `git grep -n 'retire_loser' -- src` — callers are `add_fact_core` (`knowledge.rs:856`), `review::answer` (`review.rs:272`, `:288`) and `redo-duels` (`cli.rs:2525`), the last behind the `holds` skip at `:2516-2522`.
- `git grep -n -E 'tombstone_key|find_invalidated_variant' -- src/review.rs` — no match; the rejected refusal has no loose key.
- `git grep -n -E '"action":"ask"|"review", "(accept|reject)"' -- tests` — one hit, the refused `review accept` at `cli_integration.rs:4190`; no test calls `ask`, a terminal answer or a reject.
- `git grep -n -E 'qdrant_api_key' -- src/config.rs src/cli.rs` — an `Option` defaulting to `None` (`config.rs:139`), passed to Qdrant only when set (`cli.rs:4511-4513`).
- `sed -n 2095,2209p tests/cli_integration.rs | grep -n -E 'run\(&\['` — fact add, backup, restore, fact query and audit verify; no write between backup and restore.
- `grep -rliE 'arxiv|bibtex|@article|@misc|doi\.org' . --exclude-dir=.git` — design notes, `bench_stale.rs` and `cli.rs` citing other papers; no `CITATION.cff`.
- `grep -rn -E 'SessionStart|UserPromptSubmit|PreCompact|PostToolUse|"hooks"' . --exclude-dir=.git` — no match; no host hook is installed.

## History

**2026-11-13** — [`8069652a5dd69c68ebd32d8dbdc3eb3327681d88`](https://github.com/madgodinc/mgi-mind/commit/8069652a5dd69c68ebd32d8dbdc3eb3327681d88) — v2.10.0, three commits past the previous pin. `human_review` earned on the fact store: a contested or asked-about fact holds `review = pending`, and the answer is written only from a terminal-gated command or a PIN-gated viewer route, neither declared on MCP ([section 9](#9-reliability-safety-and-trust)). The gate assumes an agent without a shell, and `ask` reopens an accepted fact. `add_fact_core` excludes the challenger's own row from the duel, under a comment citing the atlas's reading at v2.9.0; the extended flip-back test reaches the review branch, not that filter. Fact readers label contested and pending values, which the previous pin returned unlabelled. Screened: three `FRESH` files, each a version bump. Nothing was run.

**2026-11-06** — [`a8defc36f7d0bcd5108714763a12625a0eda0868`](https://github.com/madgodinc/mgi-mind/commit/a8defc36f7d0bcd5108714763a12625a0eda0868) — v2.9.0, two commits past the previous pin; its changelog says it answers the limits this report named at v2.8.2. The invalidate refusal extends to case and whitespace variants, a dated winner writes the loser's `world_until`, and skill removal, pinned blocks and `mgimind restore` are audited, the last keeping the replaced log beside it. A loser re-added within 24 hours lands `contested`, which hides nothing. Marks unchanged. The duel's rival set includes the challenger's own row, at the previous pin too, so a re-assertion on a contested axis can retire itself and report `won`; parking flip-backs as `contested` makes that path routine ([section 9](#9-reliability-safety-and-trust)). Screened: three `FRESH` files, each a version bump. Nothing was run.

**2026-11-05** — [`9fae7803ff7514d02504cd01a8f14f7e146fa8ba`](https://github.com/madgodinc/mgi-mind/commit/9fae7803ff7514d02504cd01a8f14f7e146fa8ba) — v2.8.2, 20 commits past the previous pin. `tombstone` and `bitemporal` earned: an invalidated triple is refused on every fact write path until `restore`, and a caller-supplied `valid_from` is read by a world-time as-of whose end bound is record time ([section 9](#9-reliability-safety-and-trust)). The scoped-token recall leak, the briefing's `quarantine_candidate` leak, the unfiltered history and by-author listings and the four producer-less audit ops are fixed; confirmations feed entrenchment, shrinking the default flip window to about four months for a once-asserted fact. The 2.8.1 and 2.8.2 releases changed only MCP tool descriptions, listing and annotations. Screened: `server.json` registers an MCP server and `packaging/npm` adds a `postinstall` that downloads the release binary. Nothing was run; recall was recomputed from committed files.

**2026-10-03** — [`190d1db71331da42bf3ecee3400b67732c9e1de8`](https://github.com/madgodinc/mgi-mind/commit/190d1db71331da42bf3ecee3400b67732c9e1de8) — first reading, at the head of `main`, a commit dated 13 September 2026. Three marks: `trust_state`, `audit_log`, `negative_eval`. Screened before reading: 0 auto-run surfaces, 0 build-time execution points, 0 dependency files inside the cooldown, 1 unpinned surface (`clients/python/pyproject.toml` with no lockfile), and `AGENTS.md` recorded as data; the clone was depth 1, so file dates are the tip's. Nothing was installed, built or run. Benchmark recall was recomputed from the committed per-question files with a standalone script.

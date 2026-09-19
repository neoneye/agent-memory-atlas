---
title: "MIRA"
eyebrow: "Continuous personal assistant"
description: "One conversation thread that never ends, whose older turns collapse into first-person memories scored by a thirteen-step SQL formula counting the user's active days rather than the calendar, with row-level security on eleven tables and a boot probe that plants a canary row and refuses to start if another user can read it."
root: ../..
page_kind: system
source_name: "taylorsatula/mira"
source_url: https://github.com/taylorsatula/mira
archive_name: "taylorsatula--mira"
revision: e401d59bde9b6d9811d05b7abee1438907f99394
revision_url: https://github.com/taylorsatula/mira/commit/e401d59bde9b6d9811d05b7abee1438907f99394
analyzed_at: 2026-09-19
capabilities: "scope_enforced, tombstone, negative_eval"
stack_storage: "postgres"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
capability_evidence:
  scope_enforced: "Postgres row-level security on eleven tables, with the boundary re-verified against the live catalogue before the server binds a socket | deploy/mira_service_schema.sql:530, :831-870, lt_memory/db_access.py:113, :148, :215, :249, :279, :311, :471-517, utils/power_on_self_test.py:481-560, :603-622 | the isolation is in the database rather than in a WHERE clause a caller assembles: `ALTER TABLE memories ENABLE ROW LEVEL SECURITY` with `memories_user_policy` beside it, one of fourteen policies in the schema, and a B-tree index on `memories.user_id` whose comment calls it *essential for multi-user performance* under RLS. Every `db_access` method resolves a user id before it touches the pool, and material that is deliberately shared lives in a separate `global_memories` table outside RLS, UNIONed into results and tagged `source='global'` so a caller can tell the two apart. What lifts this above a schema claim is the startup probe: `_check_postgres_rls` confirms the service pool has not inherited `app.current_user_id`, confirms the admin role is the deliberate `BYPASSRLS` exception, and queries `pg_class` and `pg_policy` for eleven named tables, failing if any has RLS disabled or zero policies | the probe runs pre-server in a subprocess with a hard deadline, so a deployment whose policies were dropped cannot quietly serve"
  tombstone: "an archival flag written by a curating agent that is forbidden from creating memories, filtered at fifteen read sites, with no path back | lt_memory/models.py:178-179, :181-184, lt_memory/db_access.py:360-362, :435, :501, :517, :564, :597, :809, :827-831, :876, lt_memory/hybrid_search.py:155, :171, agents/implementations/memory_curator_agent.py:1-20 | `Memory.is_archived` and `archived_at` are stored on the row, set by `UPDATE ... SET is_archived = TRUE`, and tested as `is_archived = FALSE` in thirteen queries in `db_access.py` and twice more in `hybrid_search.py` — once for the personal leg and once for the global one — so an archived memory leaves every read rather than being ranked down. The writer is the `MemoryCuratorAgent` in its floor mode, which samples memories not tended in a while and triages each as archive or salvage, and the agent's own docstring records the restriction that makes the mechanism safe: it *can NEVER create memories (create_memory is excluded from its tool schema) — preventing manufactured silt*. So the process that retires memories cannot mint replacements. `last_tended_at` records when the curator last touched a row and is the field the floor trigger samples on | archival is one-way at this pin: grepping the tree for a writer setting `is_archived` back to false returns nothing, and *salvage* in this codebase means declining to archive rather than restoring something archived"
  negative_eval: "a two-way isolation control that runs at every boot rather than in CI | utils/power_on_self_test.py:603-622, :94-110 | the RLS probe plants a canary: it inserts a `continuums` row owned by one user id, opens two RLS-scoped connections as the owner and as a different user, and asserts both directions on the same row — the owner's query must see it, failing with *Owner-scoped RLS query could not see its continuum canary*, and the other user's must not, failing with *Other-user RLS query could see owner continuum canary*. The positive control and the negative assertion are the same fixture, so a connection that returned nothing at all would fail the first before reaching the second, which is the vacuity this mark exists to exclude. The placement is the unusual part: it is in the pre-server startup gate, run in a subprocess with a hard deadline before Hypercorn can bind, so it is executed on every deployment rather than on every push | the companion fact belongs on the record: a `find` for test files across the tree returns four paths, two of them test files, both under `tests/utils/` and both about HTTP and URL safety — no committed test exercises any memory behaviour"
matrix:
  memory_unit: "A first-person memory row — text, a 768-dimension embedding, an importance score in [0,1], created and updated stamps, an optional `expires_at` and `happens_at`, access and mention counts, inbound, outbound and entity links, an `is_archived` flag with its timestamp, a `last_tended_at`, activity-day snapshots taken at creation and last access, free annotations, and the conversation segment it was extracted from"
  storage: "Postgres with pgvector, row-level security on eleven tables and a separate `global_memories` table outside it; Valkey beside it, and a vault for secrets"
  retrieval: "Hybrid vector and lexical search over the personal and global legs UNIONed, ranked by a thirteen-step importance formula kept in `scoring_formula.sql` as a single source of truth"
  write: "Conversation turns stay live while relevant; a segment collapses on an inactivity threshold and is distilled into first-person memories, with entity extraction, hub discovery and link typing following behind"
  update_delete: "Archival rather than deletion — the curator agent triages sampled low-value memories as archive or salvage, and every read filters archived rows out; entity merging consolidates duplicates"
  scoping: "Postgres RLS keyed on `app.current_user_id`, with shared material held in a separate table outside RLS and tagged `source='global'` in results"
  integration: "A FastAPI and Hypercorn service with its own clients and agents rather than an MCP surface; one conversation thread per user, with no way to start a new chat"
  background: "A dispatcher running the curator on a use-day cadence, a memory floor trigger sampling untended memories, batch extraction, entity garbage collection and proactive recall"
  trust: "An importance score computed by SQL from access rate, hub position, entity links, explicit mentions and a newness grace period, passed through a sigmoid; decay counts the user's activity days so a fortnight away does not degrade the store, while `happens_at` and `expires_at` count calendar days because deadlines do not pause"
  strengths: "Two clocks chosen per purpose — activity days for decay, calendar days for real-world deadlines — with the reasoning in the formula's header; a curating agent whose tool schema excludes memory creation so it cannot manufacture what it is meant to prune; and an isolation contract re-checked against the live catalogue on every boot instead of being asserted once in a test"
  risks: "No committed test exercises any memory behaviour — a `find` for test files returns two, both about HTTP and URL safety — so a thirteen-step scoring formula, a graph curator and a collapse pipeline rest on a startup probe and manual use; there is no audit or event table in the twenty-two-table schema, so nothing records what happened to a memory; and archival is one-way, with no writer anywhere returning an archived memory to circulation"
---

## 1. Executive Summary

MIRA is one person's attempt at a continuous digital entity, and it says so:
*"This is my TempleOS."* The design constraint that produces everything else is
that there is one conversation thread forever and no way to start a new chat.
Older material has to go somewhere, so it collapses — a segment reaching an
inactivity threshold is distilled into first-person memories, and the
conversation carries a rolling continuation brief when it grows too large
before that happens.

Three mechanisms make it worth reading. The **scoring formula** is a
thirteen-step calculation kept in `lt_memory/scoring_formula.sql` and described
there as the single source of truth, with every constant named and explained.
Its best idea is two clocks: decay counts the user's *activity days*, so a
fortnight offline does not degrade the store, while `happens_at` and
`expires_at` count calendar days *"since real-world deadlines don't pause"*.

The **curator** is an agent that links, merges, archives and salvages — and
cannot create. Its docstring says why the tool schema excludes `create_memory`:
*preventing manufactured silt*. A process that prunes must not be able to mint.

The **isolation** is Postgres row-level security on eleven tables, and it is
not left as a schema claim. A pre-server probe plants a canary row, opens two
RLS-scoped connections, and asserts that the owner can see it and another user
cannot — before Hypercorn binds a socket.

The report awards `scope_enforced`, `tombstone` and `negative_eval`. It
withholds `bitemporal`, `audit_log`, `trust_state` and `human_review`, and
section 9 gives the reason for each. The counterweight to all of the above is
in section 10: a `find` for test files across the whole tree returns two, both
about HTTP and URL safety. Nothing committed exercises the memory system.

## 2. Mental Model

A single thread, three states for the material in it.

**Live** is the active conversation, kept while it is relevant. **Collapsed** is
what happens when a segment goes quiet: `status` on a message moves from
`active` to `collapsed`, and the segment is distilled into memories written in
the first person. **Archived** is what happens to a memory the curator decides
is not earning its place — the row stays, and every read stops returning it.

The scoring formula is the pressure that drives the third transition. New
memories start around 0.5 and, in the formula's own phrase, have to "earn their
keep": importance rises with access rate, inbound links, entity links and
explicit LLM mentions, and decays without reinforcement, all passed through a
sigmoid centred so that an average memory lands near 0.5.

## 3. Architecture

```mermaid
%% caption: one conversation thread whose quiet segments collapse into first-person memories; entity extraction, hub discovery and a curating agent that may link, merge, archive or salvage but never create then tend the graph; retrieval unions a row-level-security-scoped personal leg with a global table outside it and ranks by a thirteen-step SQL importance formula whose decay counts the user's activity days while its deadline terms count calendar days; and a pre-server probe re-verifies the isolation contract against the live catalogue on every boot
flowchart TD
    subgraph Thread["One thread, forever"]
        LIVE["active messages"]
        BRIEF["rolling continuation brief<br/>when the window grows"]
        COLL["segment collapse<br/>on inactivity"]
    end

    subgraph Distil["Extraction"]
        MEM["first-person memories"]
        ENT["entity extraction"]
        LINK["deterministic link discovery<br/>typeless hints"]
    end

    subgraph Curate["MemoryCuratorAgent"]
        INT["integration mode<br/>link / merge / stand-alone"]
        FLOOR["floor mode<br/>archive / salvage"]
        NOCREATE["create_memory excluded<br/>from the tool schema"]
    end

    subgraph Store["Postgres + pgvector"]
        PM["memories<br/>RLS: memories_user_policy"]
        GM["global_memories<br/>outside RLS"]
        ENTT["entities"]
        SCORE["scoring_formula.sql<br/>13 steps, activity days"]
    end

    subgraph Read["Retrieval"]
        HS["hybrid search<br/>vector + lexical"]
        UNION["UNION, tagged<br/>source=personal | global"]
        ARCH["is_archived = FALSE<br/>15 sites"]
    end

    POST["power-on self test<br/>RLS canary, both directions"]

    LIVE --> BRIEF
    LIVE --> COLL --> MEM
    MEM --> ENT --> ENTT
    MEM --> LINK --> INT
    INT --> PM
    FLOOR --> PM
    NOCREATE -.-> INT
    NOCREATE -.-> FLOOR
    PM --> HS
    GM --> HS
    HS --> ARCH --> UNION
    SCORE --> HS
    POST -.->|verifies before bind| PM
```

## 4. Essential Implementation Paths

- **Domain types:** `lt_memory/models.py` — the `Memory` row and its link
  entries.
- **Data access and the archived predicate:** `lt_memory/db_access.py`.
- **Retrieval:** `lt_memory/hybrid_search.py`, `lt_memory/vector_ops.py`.
- **Ranking:** `lt_memory/scoring_formula.sql`.
- **Graph tending:** `agents/implementations/memory_curator_agent.py`,
  `lt_memory/linking.py`, `lt_memory/entity_merge.py`,
  `lt_memory/hub_discovery.py`.
- **Collapse:** `cns/core/message.py`, `cns/core/events.py`.
- **Isolation contract:** `deploy/mira_service_schema.sql`,
  `utils/power_on_self_test.py`.

## 5. Memory Data Model

The row carries more instrumentation than most, and the unusual fields are the
interesting ones:

- **`mention_count`** — explicit LLM references, annotated in the model as the
  strongest importance signal, and scored separately from `access_count`.
- **`activity_days_at_creation` / `activity_days_at_last_access`** — snapshots
  of the user's activity-day counter, so decay can be computed against
  engagement rather than wall-clock time.
- **`last_tended_at`** — when the curator last linked, merged, archived or
  salvaged this memory, `NULL` meaning never tended; the floor trigger samples
  on it.
- **`happens_at`** — when the thing the memory is about occurs, distinct from
  when the memory was created.
- **`inbound_links`, `outbound_links`, `entity_links`** — the graph the hub
  terms of the scoring formula are computed over.
- **`annotations`** — contextual notes with a source, kept beside the text
  rather than edited into it.

## 6. Retrieval Mechanics

Hybrid search runs a vector leg and a lexical leg and UNIONs a personal query
against a global one, tagging each row `source='personal'` or `source='global'`
so the caller can tell shared material from the user's own. Both legs carry
`is_archived = FALSE`.

Ranking is the SQL formula, and it repays reading in full because it states its
own constants and the reasoning behind them. Value comes from an access *rate*
rather than a raw count, with a seven-day floor on the denominator to stop new
memories spiking. Hub position contributes with diminishing returns after ten
inbound links, and entity links are weighted by entity type — a person counts
for more than a product. Explicit mentions score separately and are called the
strongest signal. A newness boost of 2.0 decays to zero over fifteen activity
days, a grace period rather than a permanent advantage. The raw total is
multiplied by a recency factor and a `happens_at` proximity multiplier, then
squashed by a sigmoid centred at 2.0 so an average memory maps to about 0.5.

The choice worth copying is which clock each term uses. Decay is in activity
days, because a user who goes on holiday has not decided their memories matter
less. Deadlines are in calendar days, because a date does not wait for someone
to come back.

## 7. Write Mechanics

A segment collapses when an inactivity threshold fires, and the collapse hook
spawns the curator in integration mode to tend each new memory — link it, merge
it, or leave it standing — before the user's next conversation. That ordering
matters: the graph is tended between sessions rather than during one.

Floor mode is the opposite direction. A trigger samples memories not tended in
a while and hands the curator a batch to triage as archive or salvage. The
separation between the two modes is a single `mode` key on the work item, and
the same agent serves both.

The division of labour with the deterministic code is stated plainly: discovery
emits typeless candidate hints, and the agent is the sole link typer — every
typed relationship in the graph was written by it. And it cannot create
memories at all.

## 8. Agent Integration

There is no MCP server. MIRA is a service — FastAPI and Hypercorn, its own
clients, its own agent framework, a web and mobile-facing API — built around
the premise that the user talks to one assistant in one thread. Memory is
internal plumbing rather than a surface other agents call.

## 9. Reliability, Safety, and Trust

**Scope enforcement — awarded, in the database.** RLS on eleven tables, a
policy per table, an index the schema comments as essential for it, and a
startup probe that checks the catalogue rather than trusting the migration.
Shared material is a separate table outside RLS rather than a nullable column
inside it, which means "global" cannot be reached by forgetting a predicate.

**Tombstone — awarded.** Archived rows stay, fifteen reads exclude them, and
the writer is an agent structurally prevented from creating the replacements it
might otherwise be tempted to write.

**Negative eval — awarded, in an unusual place.** The canary probe asserts both
directions on the same row. It is in the boot path rather than a test file,
which means it runs on every deployment and never in CI.

**Bitemporal — withheld.** The row carries `happens_at` alongside `created_at`,
which is the second axis the mark looks for, and no read uses it as one:
`happens_at` appears in the scoring formula as a proximity multiplier and in the
select lists, and nothing answers "what was true at time T". The axis exists and
feeds ranking.

**Audit log — withheld.** The schema declares twenty-two tables and none of them
records what happened to a memory; `billing_transactions` and
`stripe_webhook_events` are financial records, and `users_trash` is a
soft-delete for accounts. Archival stamps `archived_at` on the row itself, which
tells you a memory was archived but not by which pass or why.

**Trust state — withheld.** The epistemic axis here is `importance_score`, a
number the SQL formula computes and the ranking consumes. The discrete state
that withholds a memory is `is_archived`, and that is already carrying
`tombstone`.

**Human review — withheld.** No approval state gates what a memory may be used
for. The curator is an LLM agent, and its restraint is a tool-schema exclusion
rather than a human in the loop.

## 10. Tests, Evals, and Benchmarks

**No paper.** Searched the README and `docs/` for `arxiv`, `@article`, `@misc`,
`doi.org` and a `CITATION.cff`: none.

**No test of any memory behaviour.** `find . -name "*test*"` across the tree
returns four paths: the `tests/` directory itself, `utils/power_on_self_test.py`,
and two test files — `tests/utils/test_pinned_http.py` and
`tests/utils/test_url_safety.py`, both about outbound HTTP rather than memory.
There is no pytest configuration in `pyproject.toml`. So the thirteen-step
scoring formula, the collapse pipeline, the entity merge, the link typing and
the archival triage have no committed case establishing that any of them does
what it says.

That is the honest counterweight to everything in sections 6 and 7, and it is
worth stating precisely rather than as a complaint. The formula is a long SQL
expression with eight constants and a sigmoid; a change to any term is
unverifiable except by running the system and watching what surfaces. The one
property that *is* checked mechanically — user isolation — is checked in the
strongest available way, at every boot, against the live catalogue and with a
live canary. A reader should take that contrast as the shape of the project: the
author verified the thing that would be catastrophic to get wrong, and left the
rest to use.

## 11. For Your Own Build

- **Pick a clock per term, not per system.** Decay in activity days so a
  holiday does not degrade the store; deadlines in calendar days because they
  do not pause. Both live in the same formula here, each with the reason
  written beside it.
- **Forbid the pruner from creating.** Excluding `create_memory` from the
  curator's tool schema is one line of configuration that removes a whole class
  of failure — the agent that decides what to discard cannot replace it with
  something it wrote.
- **Check the isolation contract at boot, not in CI.** A probe that plants a
  canary and asserts both directions catches a dropped policy in the
  environment that actually matters, and it caught the subtler thing too: that
  the service pool has not inherited a session user id.
- **Separate shared material into its own table.** `global_memories` outside RLS
  cannot be reached by forgetting a predicate, which a nullable `user_id`
  inside the RLS table could be.
- **Rate, not count.** Value is access rate over a denominator floored at seven
  days, so a memory read twice on its first afternoon does not outrank one read
  steadily for a year.

## 12. Open Questions

- Archival is one-way at this pin — no writer sets `is_archived` back to false.
  Is a restore intended, or is re-extraction the recovery path?
- The formula's header calls itself the single source of truth. Is it
  interpolated into more than one query, and what keeps a caller from computing
  importance a second way?
- With no test around the scoring formula, how is a constant change validated
  before it reaches a live store?

## Appendix: File Index

- Domain types: `lt_memory/models.py`
- Data access: `lt_memory/db_access.py`
- Hybrid search: `lt_memory/hybrid_search.py`, `lt_memory/vector_ops.py`
- Ranking: `lt_memory/scoring_formula.sql`
- Graph: `lt_memory/linking.py`, `lt_memory/entity_merge.py`,
  `lt_memory/hub_discovery.py`, `lt_memory/entity_extraction.py`
- Curator: `agents/implementations/memory_curator_agent.py`,
  `agents/triggers/memory_floor_trigger.py`
- Conversation: `cns/core/message.py`, `cns/core/events.py`
- Schema and isolation: `deploy/mira_service_schema.sql`,
  `utils/power_on_self_test.py`

## History

**2026-09-19** — [`e401d59bde9b6d9811d05b7abee1438907f99394`](https://github.com/taylorsatula/mira/commit/e401d59bde9b6d9811d05b7abee1438907f99394) — first reading, at the head of `main`. Screened with `scripts/screen_repo.py` before anything was read: no auto-run surface, no build-time execution, nothing inside the seven-day cooldown, one unpinned dependency surface with thirty-six requirements not pinned with `==`, and an `AGENTS.md` addressed to a reading agent which was read as data. Nothing was installed, built or run. Three marks. The reading covered the memory row and its instrumentation, the data-access layer and its archived predicate, hybrid search across the personal and global legs, the scoring formula in full, the curator agent and its two modes, the collapse path, and the schema's row-level security together with the startup probe that verifies it; the tool framework, the billing tables and the web surface were read as context rather than as subject. AGPL-3.0, licence text in the tree. Four marks are withheld with reasons in section 9, and the one worth repeating here is `audit_log`: twenty-two tables in the schema and none of them records what happened to a memory. The finding that most shapes how to read the rest is that a `find` for test files across the tree returns two, both about HTTP and URL safety — the memory system has no committed test, while the isolation contract is re-verified against the live catalogue on every boot.

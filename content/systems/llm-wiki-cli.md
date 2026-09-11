---
title: "LWC"
eyebrow: "Recall hands back the replacement, not the superseded memory"
description: "A Rust CLI holding two stores at once — a source-grounded wiki whose pages carry an ordered provenance from source-grounded down to hypothesis, and a temporal memory of fingerprinted events with typed fragments, an FTS5 recall bounded by event time, and a supersession chain the read path walks so a replaced memory returns its successor unless the caller asks for the history."
root: ../..
page_kind: system
source_name: "JanYork/llm-wiki-cli"
source_url: https://github.com/JanYork/llm-wiki-cli
archive_name: "JanYork--llm-wiki-cli"
revision: 09e922b4c800d52053cac9ef702c15b6982152e0
revision_url: https://github.com/JanYork/llm-wiki-cli/commit/09e922b4c800d52053cac9ef702c15b6982152e0
analyzed_at: 2026-09-10
capabilities: "trust_state, bitemporal, audit_log, negative_eval"
capability_evidence:
  trust_state: "every recall result carries a `current` or `superseded` state, and a superseded event is dropped from the result in favour of its replacement unless the caller passes an explicit flag | src/store/temporal_memory.rs:1029-1060, :856-880, :894-899 | `current_visible_memory_id` walks the `supersedes` edges in `memory_relations` from a lexical hit to the newest event that replaced it, under the same event-time window as the search itself. The recall loop then keeps the original hit only when the caller asked to include superseded events or when the walk found no replacement, and always keeps the successor, tagging it `matched_via: \"superseded_event\"`. Each result reports `state` as `current` or `superseded`. The state is derived per call but not derived-only: the `supersedes` rows are durable and carry an index on `(target_event_id, relation_type, event_id)`, so replaced events are directly queryable rather than replayable, which is what separates this from the read-time ladders the corpus withholds the mark from | tests/temporal_memory.rs:814-901 asserts a one-result recall returning the replacement instead of the superseded hit, then the same query with the override returning three with the old event marked `superseded`"
  bitemporal: "event time and record time are separate non-null columns on every memory event, and event time is the axis the recall, retention and eviction paths filter on | src/store/temporal_memory.rs:6-21, :824-837, :1043-1048, :1162-1164 | `memory_events` stores `occurred_at TEXT NOT NULL` beside `recorded_at TEXT NOT NULL DEFAULT (…)`, with a retention index on `(occurred_at, id)` and a recall index on `(event_type, context, occurred_at DESC, id)`. A caller supplies `since` and `until`, normalised through SQLite and rejected if inverted, and every read applies `JULIANDAY(e.occurred_at) >= JULIANDAY(?3)` and `<= JULIANDAY(?4)` on top of a configured age window. Two limits belong with the mark: `recorded_at` is never a predicate, only an ordering tiebreak, so there is no as-of-record-time query; and the explicit `valid_from`/`valid_until` interval is written, cross-validated so the start is not later than the end, and returned by `memory_show`, yet appears in no `WHERE` anywhere in the tree | tests/temporal_memory.rs:758 recall is time-filterable, :1147 age retention evicts only expired unprotected events, :1272 recall hides an expired event that is still physically present"
  audit_log: "an operations table written from fifty-four call sites through one helper, plus a per-event change record keeping the prior and new value of each mutated subject | src/store/schema.rs:105-111, src/store/search_state.rs:563-590, src/store/temporal_memory.rs:34-42, :990, src/store/checkpoints.rs:204, src/sync.rs:3955 | `operations(id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, target TEXT NOT NULL, detail_json TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (…))` is written only by `record_operation(tx, action, target, detail)`, which fifty-four sites call inside the same transaction as the mutation they describe, and the checkpoint and sync paths read it back. Beside it `memory_changes(event_id, ordinal, subject, before_value, after_value, reason)` records what a memory event changed and why. Two limits belong with the mark. Four statements amend `detail_json` after insertion, two against `last_insert_rowid()` completing the row just written and two in `sync_publish` by explicit id, so a row's payload is not immutable. And no ordinary write path removes a row, but `replace_main_from_attached` clears `operations` along with every other table when a changeset is applied and repopulates it from the attached draft, so applying a changeset replaces the log rather than merging into it | src/changeset_hook_summary_tests.rs:19 counts `operations` rows after a hook run; tests/temporal_memory.rs:946 asserts feedback is append-only"
  negative_eval: "a committed case asserting that a superseded memory must not come back from a populated recall, with the replacement, the override direction and an unrelated cluster as controls in the same test | tests/temporal_memory.rs:814-901 | Three events are stored: a payment policy, a replacement carrying a `supersedes` relation to it, and an unrelated inventory policy. Recalling a term that matches the *old* event asserts `results.len() == 1` and that the single result is the replacement, with `state == \"current\"` and `matched_via == \"superseded_event\"` — so the superseded event is excluded from a result that is not empty and whose one member is a different, named event. The same query with `--include-superseded` then asserts exactly three results with the old event present and marked `superseded`, and a fourth assertion recalls the inventory term and gets exactly one, proving the exclusion is not a retriever that returned nothing | tests/temporal_memory.rs:1147, :1272 add the retention pair: an expired event is absent from recall while a `SELECT EXISTS` on the same id proves it is still in the store"
stack_storage: "sqlite"
stack_retrieval: "lexical, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "Two shapes in one database. A wiki `Page` — slug, title, an optional kind and summary, a Markdown body whose `[[slug]]` links become edges, the paths of the sources supporting it, an ordered `provenance` list, created and updated. And a `memory_event` — a 64-character fingerprint, an event type, a context, `occurred_at`, `recorded_at`, an optional validity interval, a `pinned` flag and a logical byte count — with `memory_fragments` typed `observed`, `decision`, `constraint`, `learned`, `unresolved` or `outcome`, `memory_changes` holding a subject with its before and after values and a reason, `memory_evidence` holding a reference and an excerpt, and `memory_relations` typed `supersedes`, `contradicts`, `resolves`, `supports` or `related`"
  storage: "SQLite with a versioned migration chain, one database per scope: `.lwc/wiki.db` under the project root and a separate store under the home directory. There is no scope column — `Scope::Project` and `Scope::Global` resolve to different files and `Scope::All` opens both read-only. An FTS5 contentless index sits over the memory events, and changesets and checkpoints sit over the wiki"
  retrieval: "Two arms. The wiki search is weighted lexical with graph awareness — title thirty-two, path sixteen, generic eight, a graph-match and a graph-hub term — and decorates each result with the page's provenance. Memory recall is FTS5 `bm25` with column weights, bounded by a configured age window and optional `since`/`until` on event time, with every candidate resolved forward through the `supersedes` chain and re-ranked by a feedback score clamped to plus or minus three"
  write: "An agent drives it as a CLI or over MCP. A page cites its sources with a repeated `--source` and declares `--provenance` otherwise; a citation adds `source-grounded` automatically. A memory event is a capsule of JSON — `remember` — deduplicated by a 64-character fingerprint and idempotent under a `request_id`, where a replayed request with a changed payload conflicts instead of mutating. A semantic wiki relation is refused unless its type is one of six, its provenance one of four, its reason non-empty and its confidence a finite number in zero-to-one"
  update_delete: "Supersession rather than deletion at the memory layer: a new event points a `supersedes` edge at the old one, recall returns the successor, and the old event stays reachable behind an explicit flag. Retention does delete — an age pass evicts events past the configured window and a byte-budget pass evicts the oldest, both skipping anything pinned or carrying an unresolved fragment, with the counts kept in a `memory_state` row. The wiki layer has changesets with restore and rollback"
  scoping: "Physical rather than keyed. A project store and a global store are separate SQLite files chosen by a `Scope` enum, and `Scope::All` reads both and labels each result with the store it came from. No record carries a scope key and no query filters on one, so this partitions the way a per-project configuration directory does rather than the way a tenant column does"
  integration: "A CLI on npm as `@i-xor/lwc` and on crates.io as `lwc`, an MCP server, and a published skill; documented for Claude Code, Codex, Cursor, OpenCode, Gemini CLI, Kiro, Hermes, Antigravity, Copilot in VS Code, Copilot CLI, Copilot for JetBrains and pi. READMEs in seven languages"
  background: "A hint engine runs inside every `remember`: it returns up to three prompts to the agent — a `contradicts` or `supersedes` edge needing review, five or more events sharing an exact type and context, an unresolved fragment older than fourteen days, and storage past eighty per cent of the byte budget — each suppressed by a seven-day cooldown row that a prune pass clears when it expires. Beside it, age and capacity eviction, ingest jobs with a status ladder, checkpoints, and a git-backed sync"
  trust: "Three separate vocabularies. The wiki has a four-value ordered provenance — `source-grounded`, `user-provided`, `agent-observed`, `hypothesis` — rejected at the boundary if unrecognised, decorated onto every search result, and filtered on nowhere. Memory events have `current` versus `superseded`, resolved from the relation graph on every recall and used to drop the replaced event. And `memory_feedback` records a `useful` or `not-useful` signal with a mandatory reason, aggregated into an integer clamped to plus or minus three that adjusts rank by five per cent and never excludes anything"
  strengths: "A recall that walks the supersession chain and hands back the replacement, with the history one flag away and each result labelled; a provenance vocabulary that names a hypothesis as a hypothesis and refuses an unrecognised value; retention that protects pinned events and anything still marked unresolved, so the open questions are the last thing forgotten; benchmark adapters that pin the upstream by commit and the dataset by content hash and stamp a limited run `partial=true`; an operations log written through one helper from fifty-four sites; a mandatory reason on a wiki relation and on a feedback signal alike"
  risks: "The wiki's provenance ladder is stored, ordered, validated and attached to every result, and no read path acts on it, so a hypothesis ranks like a cited fact; `valid_from` and `valid_until` are written, cross-validated and returned but appear in no `WHERE`, so the explicit validity interval is a column rather than a mechanism; `recorded_at` is never a predicate, so there is no as-of-record-time query; scope is a choice of database file rather than a key, so nothing partitions two callers sharing a store; the memory layer is off unless a scope enables it; and 123,311 lines of Rust from two authors in about six weeks is a lot of surface per commit-month"
---

## 1. Executive Summary

LWC is two stores wearing one CLI. The visible one is a source-grounded wiki an
agent curates — pages with cited sources, `[[slug]]` links, and a typed relation
graph. The one that earns the marks is underneath it: a temporal memory of
fingerprinted event capsules with typed fragments, an FTS5 recall bounded by
event time, supersession resolved at read time, retention with protection, and a
hint engine that tells the agent what needs reviewing.

Apache-2.0; 294 commits between 29 July and 5 September 2026 from two authors —
about six weeks — for 123,311 lines of Rust across 139 files, with 868 test
attributes. Published on npm and crates.io with READMEs in seven languages. The
screen found no auto-run surface, three manifests inside the seven-day cooldown,
one build-time execution path and one unpinned dependency surface; nothing was
installed, built or run.

**Recall hands back the replacement.** A lexical hit on a memory event is not
returned directly. `current_visible_memory_id` walks the `supersedes` edges
forward from the hit to the newest event that replaced it, and the recall loop
keeps the original only if the caller passed `--include-superseded`. Every result
is stamped `current` or `superseded`, and a hit reached through the chain is
labelled `matched_via: "superseded_event"` so a reader can see the redirect
happened. That is a discrete status deciding what may be treated as true, and it
earns `trust_state` — the status is derived per call, but the `supersedes` rows
are durable and indexed on their target, so replaced events are queryable rather
than replayable, which is the line the corpus draws.

**Event time is the axis, and record time is only a tiebreak.** `occurred_at`
and `recorded_at` are separate non-null columns, and every read — recall,
supersession resolution, retention, eviction — filters on `occurred_at` with a
configured age window and optional `since` and `until` bounds that are normalised
through SQLite and rejected if inverted. `bitemporal` is earned on that, with two
limits stated: `recorded_at` never appears in a predicate, so there is no
as-of-record-time question; and `valid_from`/`valid_until` — the explicit
validity interval — are written, cross-validated so the start is not later than
the end, and returned by `memory_show`, and appear in no `WHERE` in the tree.
The interval is a column; the mark rests on the pair that is queried.

**Forgetting protects the unfinished.** Age and capacity eviction both skip an
event that is pinned *or* that carries a fragment of kind `unresolved`. Marking
something as an open question is therefore also a retention decision, which is a
better default than most decay schemes manage: the things you have not settled
are the last things dropped.

**Supersession is tested from both directions.** A committed case stores three
events, recalls a term matching the superseded one, and asserts exactly one
result which is the replacement; then re-runs with the override and asserts
exactly three with the old one marked `superseded`; then recalls an unrelated
term and asserts exactly one. The exclusion is proved against a populated
result with the positive controls beside it, which earns `negative_eval`.

**The wiki's provenance ladder is the good idea that stayed inert.**
`PROVENANCE_ORDER` runs `source-grounded`, `user-provided`, `agent-observed`,
`hypothesis`; an unrecognised value is rejected rather than defaulted; and the
value is attached to every search result. No read path filters on it. A page
whose only provenance is `hypothesis` ranks beside a cited one, and the
distinction reaches a reader only if the reader acts on the label.

## 2. Mental Model

Think of it as a notebook and a logbook sharing a drawer.

The **notebook** is the wiki. A page is a claim with citations: the agent writes
it, attaches the immutable sources supporting it, and where there is no source
declares what kind of claim it is instead. Pages link to each other twice —
untyped `[[slug]]` wikilinks, and typed semantic edges that cannot exist without
a reason and a bounded confidence. A lint flags any page with neither a cited
source nor an explicit provenance as `uncited_page`.

The **logbook** is the temporal memory. The agent hands over a capsule: a type, a
context, when it happened, and fragments sorted into what was observed, what was
decided, what constrains, what was learned, what stays unresolved, and what came
out. It can carry evidence with excerpts, changes with before and after values,
and relations to earlier events. The capsule is fingerprinted, so replaying it is
idempotent; a replay under the same `request_id` with a *different* payload
conflicts instead of overwriting.

Correction in the logbook is not editing. A new event points `supersedes` at the
old one, and from then on recall answers with the new one. The old event is still
there, still searchable behind a flag, still marked for what it is. Deletion
happens only through retention, and retention refuses to touch what is pinned or
still unresolved.

The gap runs between the two halves. The notebook has the richer vocabulary for
doubt — four provenance values, confidence on every edge, a lint for ungrounded
pages — and does nothing with it at read time. The logbook has the thinner
vocabulary and enforces it.

```mermaid
%% caption: a memory capsule is fingerprinted and stored with typed fragments and relations, and the hint engine reports what needs review; recall matches by FTS5 inside an event-time window, resolves every hit forward through the supersedes chain so the replacement is returned in place of the superseded event, re-ranks by a clamped feedback score, and labels each result current or superseded
flowchart TB
    AG["an agent calls remember<br/>with a JSON capsule"]
    FP{"fingerprint<br/>64 chars"}
    IDEM["same request_id, same payload<br/>→ idempotent replay"]
    CONF["same request_id, changed payload<br/>→ conflict, no mutation"]
    EV[("memory_events<br/>occurred_at · recorded_at<br/>valid_from · valid_until<br/>pinned · logical_bytes")]
    FR[("fragments: observed · decision<br/>constraint · learned<br/>unresolved · outcome")]
    REL[("relations: supersedes · contradicts<br/>resolves · supports · related")]
    HINT["hint engine returns up to three:<br/>relation-review · exact-context-cluster<br/>aged-unresolved · storage-pressure<br/>each on a seven-day cooldown"]
    Q["memory recall query"]
    FTS["FTS5 bm25 over memory_fts<br/>AND occurred_at within max_age_days<br/>AND optional since / until"]
    PROT["kept past the window if<br/>pinned or holding an<br/>unresolved fragment"]
    WALK["walk supersedes forward:<br/>current_visible_memory_id"]
    DROP["superseded hit dropped<br/>unless --include-superseded"]
    RANK["rank adjusted by feedback<br/>clamped to ±3, five per cent"]
    OUT["results, each labelled<br/>current or superseded"]
    OPS[("operations: action, target,<br/>detail_json — 54 call sites")]

    AG --> FP
    FP --> IDEM
    FP --> CONF
    FP --> EV
    EV --> FR
    EV --> REL
    AG --> HINT
    AG -.-> OPS
    Q --> FTS
    FTS --> PROT
    PROT --> WALK
    REL --> WALK
    WALK --> DROP
    DROP --> RANK
    RANK --> OUT
```

## 3. Architecture

One Rust crate, 123,311 lines across 139 files: `agent/`, `artifacts/` (the page
and source types and their normalisation), `store/` (schema and migrations,
content search, graph ingest and search, checkpoints, changeset restore, sync
publish, temporal memory), `codegraph/`, `learning/`, `view/`, `work/`, plus
`mcp.rs`, `scope.rs`, `secret_scan.rs`, `source_diff.rs`, `sync_git.rs` and
`office.rs`.

Storage is SQLite behind a versioned migration chain — the temporal memory
arrives as its own schema version, migrating transactionally from the tags
version and refusing any other. The scope decision happens before the
connection: `Scope::Project` resolves to `<project>/.lwc/wiki.db`,
`Scope::Global` to a home-directory path, `Scope::All` to both, read-only.

The memory layer is off by default in the sense that it is `Inherit` until a
scope sets `enabled`, with a maximum age of 365 days and a byte budget of 256
mebibytes; `memory feedback` on a disabled scope returns `memory_disabled`
rather than silently succeeding.

`secret_scan.rs` is wired into two paths — `config.rs` when a translation
argument is handled, and `cli/helpers.rs` when file content is read — through
`detect_possible_secret_reasons(path, content)`, which returns reasons rather
than a boolean. A knowledge base an agent fills from a codebase will eventually
ingest a key, and somebody thought about that.

## 4. Essential Implementation Paths

- **Record a memory.** `remember` → a capsule validated against
  `MemoryEventInput` with `deny_unknown_fields` → fingerprint → `INSERT INTO
  memory_events` with `occurred_at` defaulting to `recorded_at` when the caller
  gives none → fragments, changes, evidence and relations inserted → the hint
  engine runs → `record_operation`.
- **Recall.** `store/temporal_memory.rs:790-912` → tokenize, normalise `since`
  and `until` through SQLite and reject an inverted pair → FTS5 `MATCH` with
  `bm25(memory_fts, 0.0, 2.0, 4.0, 1.0)` inside the age window and the bounds →
  each hit resolved forward by `current_visible_memory_id` → the superseded hit
  dropped unless overridden, the successor always kept → feedback score applied
  as a rank adjustment → sorted and truncated.
- **Resolve supersession.** `:1029-1060` → a loop over `SELECT relation.event_id
  FROM memory_relations relation JOIN memory_events e … WHERE
  relation.relation_type = 'supersedes' AND relation.target_event_id = ?1` under
  the same time window, taking the newest by `occurred_at DESC, recorded_at
  DESC, id`, until no further replacement exists.
- **Protect and evict.** `MEMORY_EVENT_PROTECTED_SQL` is `e.pinned = 1 OR
  EXISTS(SELECT 1 FROM memory_fragments unresolved WHERE unresolved.event_id =
  e.id AND unresolved.kind = 'unresolved')`, spliced into the recall filter as a
  disjunct and into the retention query negated.
- **Hint.** `:1341-1476` → four candidate rules → for each, skip if a cooldown
  row exists, else insert one with a seven-day `next_eligible_at` and emit →
  at most three per call. `prune_memory_hint_state` clears rows whose
  `next_eligible_at` has passed before the loop runs, so the cooldown expires.
- **Create a wiki relation.** `store/graph_search.rs:105-135` → four validations
  in order, each with its own error code: `invalid_semantic_relation` for the
  type, `invalid_provenance` for the provenance, `invalid_input` for an empty
  reason, `invalid_confidence` for a value outside a finite zero-to-one.
- **Record an operation.** `store/search_state.rs:563-590` → `INSERT INTO
  operations(action, target, detail_json)` in the caller's transaction.

## 5. Memory Data Model

**The event.** `id`, an optional `request_id` under a unique partial index, a
`fingerprint` constrained to exactly 64 characters, an `event_type` and a
`context` both non-blank, then `occurred_at`, `recorded_at`, `valid_from`,
`valid_until`, a `pinned` flag checked to zero or one, and `logical_bytes`
checked non-negative. Three indexes: by request id, by `(event_type, context,
occurred_at DESC, id)` for recall, and by `(occurred_at, id)` for retention.

Almost every column carries a `CHECK`. That is unusual and it matters here,
because the writer is a language model: a blank context or a truncated
fingerprint fails at the database rather than becoming a row nobody can use.

**The fragments.** `kind` is constrained to `observed`, `decision`,
`constraint`, `learned`, `unresolved` and `outcome`, with an ordinal and a
non-blank value. Six genres, and `unresolved` is the one worth naming: a memory
system that can record *this is still open* has somewhere to put the thing that
usually gets lost, and here that record also buys the event protection from
eviction.

**The satellites.** `memory_changes(subject, before_value, after_value, reason)`
— what changed, from what, to what, and why. `memory_evidence(reference,
excerpt)` — a citation with the passage. `memory_relations(relation_type IN
('supersedes','contradicts','resolves','supports','related'), target_event_id,
basis)` — with an index on `(target_event_id, relation_type, event_id)` so the
inbound direction is the fast one, which is exactly what supersession resolution
needs.

**The counters.** `memory_state` is a single row holding `record_attempts`,
`inserted_events`, `idempotent_replays`, `feedback_useful`,
`feedback_not_useful`, `age_evictions`, `capacity_evictions`, `event_count` and
`logical_bytes`. A store that counts its own replays and evictions can answer
whether the memory is working without instrumenting the caller.

**The page.** `slug`, `title`, an optional `kind` and `summary`, a Markdown
`body`, `source_artifact_paths`, a `provenance: Vec<String>`, created and
updated. Provenance is a list, so a page assembled from a citation plus an
inference is honestly both.

## 6. Retrieval Mechanics

**Memory recall** is FTS5 with `bm25(memory_fts, 0.0, 2.0, 4.0, 1.0)` — the
event id unweighted, the event type at two, the context terms at four, the
content terms at one — so what a memory is *about* outweighs its wording. The
candidate limit is the requested limit times eight, clamped to a thousand, which
leaves room for the supersession walk to collapse several hits onto one
successor without starving the result.

The time filter is three clauses: the event must be inside `max_age_days` of now
*or* protected, and inside the caller's `since` and `until` if given. Both
bounds are normalised by asking SQLite to format them and rejected as
`invalid_input` if they are not timestamps, and an inverted pair fails before any
query runs.

Then the walk. Every hit goes through `current_visible_memory_id` — and so does
every candidate a second time, when the results are assembled — so a chain of
three replacements resolves to the third. Note that the walk applies the same
time window, so a replacement that has itself aged out does not hide the older
event behind a result the reader cannot see.

Feedback re-ranks and never filters: the score is the count of `useful` minus
`not-useful` for that event, clamped to plus or minus three, and the adjustment
is five per cent of the absolute lexical rank times that number. The
`explanation` block on each result reports the raw `lexical_rank`, the
`feedback` integer and `matched_via`, so the ordering is inspectable.

**Wiki search** is the weighted lexical scorer — title thirty-two, path sixteen,
generic eight, graph match a quarter, graph hub four, manual boost two — and it
decorates each result with the page's provenance, computed from whether the page
has cited sources and what explicit values it carries. Decorated, not filtered:
the searches for a provenance predicate return an insert, two delete-and-restore
statements, a display query, a graph-ingest identity match, and the lint that
flags a page with neither sources nor provenance. Nothing narrows a result set.

## 7. Write Mechanics

`remember` takes a JSON capsule with `deny_unknown_fields`, so a hallucinated
key fails rather than being dropped. The fingerprint gives content dedup; the
optional `request_id` gives idempotency across processes, and the interesting
case is the third one — a replay under the same `request_id` with a changed
payload is a conflict, and the test name says what that is worth:
`changed_request_replay_conflicts_without_mutation`.

`occurred_at` defaults to `recorded_at` when the caller omits it, which is the
right default and the reason the two columns do not collapse: a capsule about
something that happened last month carries that fact, and one about right now
carries the same value twice.

The wiki's write path validates harder because its writer is less constrained. A
provenance outside the four is rejected. A semantic relation is refused unless
its type is one of six, its provenance one of four, its reason non-empty and its
confidence a finite number in zero-to-one — four checks, four distinct error
codes, so the agent that got it wrong can fix the right thing. An edge that
cannot exist without a justification makes the graph self-documenting.

Correction differs by layer. In the memory, a new event supersedes an old one and
nothing is edited. In the wiki, a changeset can be restored — and
`changeset_restore` deletes a page's provenance rows and re-inserts them from the
candidate database rather than merging, which is the correct choice for making a
rollback exact.

Retention is the only deletion. The age pass evicts events past the window and
the capacity pass evicts the oldest until the byte budget is met, both skipping
anything protected, both rolling back if the budget cannot be met without
touching protected rows, and both incrementing the counters in `memory_state`.

## 8. Agent Integration

An MCP server and a CLI, on npm as `@i-xor/lwc` and crates.io as `lwc`, with a
published skill and a dozen named harnesses in the README, in seven languages.

The hint engine is the part designed specifically for an agent. Every `remember`
returns up to three prompts: a `contradicts` or `supersedes` edge that needs
review, five or more events sharing an exact type and context — a redundancy
signal — an `unresolved` fragment more than fourteen days old, and storage past
eighty per cent of budget. Each is keyed and suppressed for seven days, and the
suppression rows are pruned when they expire, so the same nag does not arrive on
every write. That is a memory store telling its writer what to clean up, which is
a more useful form of proactivity than surfacing memories unprompted.

## 9. Reliability, Safety, and Trust

**Trust state — awarded.** `current` versus `superseded`, resolved on every
recall and used to drop the replaced event rather than to rank it, with an
explicit `--include-superseded` override for the history and a label on every
result. The corpus withholds this mark from statuses computed per call and stored
nowhere, and that objection does not apply here: the `supersedes` rows are
durable and indexed on `(target_event_id, relation_type, event_id)`, so a caller
can ask which events have been replaced with one indexed query rather than
replaying the corpus. What is derived is the resolution, not the fact.

**Bitemporal — awarded, with the interval named as unused.** `occurred_at` and
`recorded_at` are separate non-null columns on every event, and event time is
what recall, supersession resolution, retention and eviction all filter on, with
caller-supplied bounds validated before use. Two limits: `recorded_at` appears
only in `ORDER BY`, so there is no as-of-record-time query; and `valid_from` and
`valid_until` are written, cross-validated so the start is not later than the
end, carried through sync, and returned by `memory_show`, yet appear in no
`WHERE` anywhere. The explicit interval is a column awaiting a consumer.

**Audit log — awarded, with two limits.** `operations` records an action, a
target and a JSON detail, written through one helper from fifty-four call sites
inside the mutating transaction and read back by the checkpoint and sync paths.
`memory_changes` adds the prior and new value of each mutated subject with a
reason. Against that: four statements amend `detail_json` after insertion — two
completing the row just written, two in `sync_publish` by explicit id — so a
row's payload is not immutable. And while no ordinary write path deletes a row,
`replace_main_from_attached` wipes `operations` along with every other table when
a changeset is applied and repopulates it from the draft, whose autoincrement
`changeset_begin_sparse` seeded at the base store's last operation id. So ids
stay continuous across an applied changeset and the log is replaced rather than
merged — anything recorded on the live store while the draft was open does not
survive the apply.

**Negative evaluation — awarded.** The supersession case asserts a one-member
result containing the replacement rather than the matched-and-superseded event,
with the override direction and an unrelated-cluster control in the same test;
the retention pair asserts an expired event is absent from recall while a `SELECT
EXISTS` proves the row is still in the store. Neither can pass on a retriever
that returns nothing.

**Tombstone — withheld, and the near-miss is real.** `memory_hint_state` is a
durable row keyed on a candidate and consulted before a later emission, which is
the *shape* the mark asks for — but what it suppresses is a repeated nag, not a
rejected value, and the suppression expires by design. Supersession is explicitly
not this either: the superseded event stays retrievable and nothing prevents an
equivalent claim being recorded again.

**Scope — withheld.** A `Scope` enum selects a database file, and `Scope::All`
opens both and labels each result with its store. There is no scope key on a
record and no predicate on a read, so this partitions the way a per-project
configuration directory does. It is the right shape for a local tool and it does
not separate two callers sharing a store.

**Human review — withheld, and this is the second-closest miss.**
`memory feedback` is a person or agent adjudicating a memory with a mandatory
non-empty reason, and the `relation-review` hint exists to route a contradiction
to somebody. But feedback moves a rank by five per cent and gates nothing, and
the hint is a suggestion with no approval step: no surface holds memory content
back until a person passes it.

**One property worth naming, and one worth watching.** The protection predicate
— pinned *or* unresolved — makes marking a question open into a retention
decision, which is a genuinely good coupling. Against it: the wiki's provenance
ladder and the memory's validity interval are both carefully built, both written,
both surfaced, and neither reaches a `WHERE`. Two well-designed vocabularies in
one repository stopping one clause short of being mechanisms is a pattern, not an
oversight.

## 10. Tests, Evals, and Benchmarks

868 test attributes across 139 Rust files, with `tests/temporal_memory.rs`
carrying twenty-five integration cases that drive the real binary in a temporary
project and home directory and assert against both the JSON output and the
SQLite file. The fixtures are written in Chinese, which is a useful side-effect:
`recall_is_bounded_cjk_searchable_and_time_filterable` proves the tokenizer works
on CJK text rather than assuming whitespace.

The names carry the contracts:
`age_retention_evicts_only_expired_unprotected_events`,
`recall_filters_expired_events_before_physical_maintenance`,
`byte_budget_evicts_oldest_unprotected_and_rolls_back_when_blocked`,
`changed_request_replay_conflicts_without_mutation`,
`feedback_is_append_only_and_reranks_only_matching_memories`,
`version_13_store_migrates_temporal_tables_transactionally`. Each of those is an
assertion about a boundary rather than a happy path.

**Benchmarks are committed, and the discipline is the notable part.**
`benchmarks/agent_memory/` holds adapters for LongMemEval-S, LongMemEval-V2 and
the Agent Memory Leaderboard Add/Search contract, each pinned to an upstream
commit, with the LongMemEval-S dataset pinned by a SHA-256 the README prints and
a Hugging Face revision. A limited run writes `partial=true` into its report, and
the README states that a run is `scored` only with the benchmark's official
answers — the distinction that lets a reader tell a smoke from a result. Reports
are written to a gitignored directory, so the repository claims no numbers. There
are also local latency benchmarks for search, graph, tags and word graph, opt-in
behind an environment variable and ignored in normal runs.

No paper: a search of the READMEs, `docs/` and `benchmarks/` for `arxiv`,
`bibtex`, `@article`, `@misc` and `CITATION` returns nothing.

The maturity signal to hold against all of it is the ratio: 123,311 lines from
two authors in about six weeks. The temporal memory is the best-tested part of
this system and the wiki around it is much larger; a surface that accumulated
that fast will have more of itself untested than the headline count suggests.

## 11. For Your Own Build

### Steal

- **Resolve supersession on the read path, not the write path.** Leave the old
  event in place, point an edge at it, and let recall walk forward. You keep the
  history, you answer with the current fact, and one flag gives a reader the
  chain. Index the edge on its target so the walk is cheap.
- **Label the result with the state you filtered on.** `state: "current"` plus
  `matched_via: "superseded_event"` tells a reader that a redirect happened. A
  filter that leaves no trace is indistinguishable from a retrieval miss.
- **Let "unresolved" buy protection from eviction.** Coupling the open-question
  genre to the retention predicate means decay drops what you have settled and
  keeps what you have not, which is the opposite of what recency alone does.
- **Make a replay with a changed payload a conflict.** Idempotency that silently
  overwrites hides the bug; `changed_request_replay_conflicts_without_mutation`
  surfaces it.
- **Put `CHECK` constraints on everything a model writes.** Non-blank contexts,
  a fixed-length fingerprint, an enumerated fragment kind — the database is the
  last place to catch a capsule that a prompt got wrong.
- **Stamp a partial benchmark run `partial=true`.** Pinning the upstream by
  commit and the dataset by content hash, and refusing to call an unscored run a
  score, is how a benchmark harness stays honest between releases.

### Avoid

- **Recording a signal nothing reads.** The provenance ladder and the validity
  interval are both designed, written and surfaced, and neither is consulted. A
  field that only renders is a field a reader must remember to act on, and the
  distance to a mechanism is one clause.
- **Two vocabularies where one would do.** Wiki provenance, memory supersession
  state and feedback signal are three trust notions in one product, and only the
  middle one affects what comes back.
- **Calling a file-per-scope arrangement a boundary.** It is right for a local
  tool and it does not survive two callers sharing a store.

### Fit

LWC suits a developer who wants an agent to keep a durable record of decisions
across sessions in a local SQLite file, with supersession handled properly and
retention that protects the unfinished. The recall path is the reason to look:
the supersession walk, the protection predicate and the labelled results are
worth reading whatever you build. The wiki layer around it is larger, younger,
and less connected — its provenance vocabulary is the best-designed inert thing
in this system. Expect to add the provenance predicate and, if you need it, the
validity predicate, and note that you will be adding them to a schema that
already holds the data.

## 12. Open Questions

- What was `valid_from`/`valid_until` for? The columns, the cross-validation and
  the sync carriage all exist; only the predicate is missing.
- Is an as-of-record-time query intended? `recorded_at` is stored on every event
  and never constrains one.
- Should the wiki search filter on provenance, or should the memory layer's
  supersession model absorb the wiki entirely? The two halves solve overlapping
  problems with different rigour.
- How does the feedback score behave over a long-lived store? Clamped to plus or
  minus three and applied as five per cent of the lexical rank, it can reorder
  near-ties and cannot promote a weak match — is that the intended ceiling?

## Appendix: File Index

| Path | What it holds |
| --- | --- |
| `src/store/temporal_memory.rs` | The whole memory layer: the schema (1-107), `MemoryEventInput` (145-160), the validity cross-check (449-453), the protection predicate (749-755), recall (790-912), feedback (928-1010), supersession resolution (1029-1060), retention and eviction (1150-1300), the hint engine (1341-1476), cooldown pruning (1504-1540) |
| `tests/temporal_memory.rs` | Twenty-five integration cases driving the real binary: supersession (814), scope-all recall (906), feedback (946), age retention (1147), expired-recall (1272), byte budget (1332) |
| `src/store/schema.rs` | The `operations` table (105-111), the column contracts asserted at open (433-439) |
| `src/store/search_state.rs` | `record_operation` (563-590), the memory table registry (49-57) |
| `src/artifacts/types.rs` | `PROVENANCE_ORDER` (35-40), `Source` (52-57), `Page` (60-70), `Operation` (72-77) |
| `src/artifacts/normalize.rs` | Provenance validation (121) and ordered emission (125) |
| `src/store/graph_search.rs` | The four semantic-relation validations (105-135), provenance decoration of results (665-690) |
| `src/store/types.rs` | `EXPLICIT_PROVENANCE` (48), the search weights (51-56), the `uncited_page` lint (148-156) |
| `src/store/changeset_restore.rs` | Provenance delete-and-restore (380-385, 752), the `detail_json` amendments (660, 1043) |
| `src/scope.rs` | The `Scope` enum and per-scope store resolution |
| `src/config.rs` | `MemorySetting` (44-50), the 365-day and 256-mebibyte defaults (16-17), the secret-scan call site (905) |
| `src/secret_scan.rs` | `detect_possible_secret_reasons`, returning reasons rather than a boolean |
| `benchmarks/agent_memory/` | LongMemEval-S, LongMemEval-V2 and Agent Memory Leaderboard adapters, upstreams pinned by commit and the dataset by SHA-256 |

Searches behind the absence claims above, run from the repository root:

```sh
rg -n 'valid_until' src --glob '*.rs' | rg 'WHERE|<=|>='                # none: written, cross-validated, returned, never a predicate
rg -n 'recorded_at' src --glob '*.rs' | rg 'WHERE|JULIANDAY|<=|>='      # none: ordering only, never a filter
rg -n 'provenance' src/store src/view | rg 'filter|WHERE|exclude'       # an insert, two restore deletes, a display query, a graph-ingest identity match, the uncited_page lint — no read filter
rg -n 'DELETE FROM operations|UPDATE operations' src                    # four detail_json amendments; two wholesale clears, both in the changeset lifecycle
rg -n -i 'arxiv|bibtex|@article|@misc|CITATION\.cff|doi\.org' README*.md docs benchmarks   # none: no paper
```

## History

**2026-09-10** — [`09e922b4c800d52053cac9ef702c15b6982152e0`](https://github.com/JanYork/llm-wiki-cli/commit/09e922b4c800d52053cac9ef702c15b6982152e0) — first reading, at the head of `main`, the last commit of 5 September 2026. Screened before reading: no auto-run surface, three manifests inside the seven-day cooldown, one build-time execution path, one unpinned dependency surface, and agent instruction files treated as data; nothing was installed, built or run, and the read was made from a full clone. Four marks. The reading covered the temporal memory schema and its recall, supersession, retention and hint paths, the wiki page and provenance model, the semantic relation constraints, the operations log, the changeset restore path and the benchmark adapters; the code graph, the learning subsystem, the office and translation surfaces and the git sync were read as context rather than as subject.

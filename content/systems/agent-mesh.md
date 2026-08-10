---
title: "Agent Mesh"
eyebrow: "The schema for a verified decision, and no way to write one"
description: "A hash-chained event log whose decisions carry tiers, quorum, supersession and executable verification commands — with both shipped write paths hardcoding the verification list empty, and a grounding packet that never reads the decision store at all."
root: ../..
page_kind: system
source_name: "cbalgeman/agent-mesh"
source_url: https://github.com/cbalgeman/agent-mesh
revision: 258a1eed288513e24953a633c44b397e91ea9886
revision_url: https://github.com/cbalgeman/agent-mesh/commit/258a1eed288513e24953a633c44b397e91ea9886
analyzed_at: 2026-08-10
capabilities: "trust_state, audit_log, human_review"
stack_storage: "files, sqlite"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "A decision — a titled record with a tier, an externalized Markdown body addressed by SHA, and a status; messages and backlog items share the log but are coordination state, not claims"
  storage: "`.agent-mesh/events.jsonl`, an append-only SHA-256 hash chain, with SQLite as an explicitly derived and rebuildable index across roughly thirty tables"
  retrieval: "Explicit CLI query only — a full-table substring scan for `decisions search`, `fnmatch` over affected-code globs for `decisions at`, and a Workbench tab"
  write: "Deterministic and local; no LLM anywhere. An agent or human appends a `decision_proposed` event through the CLI or the Workbench"
  update_delete: "Supersession with cycle detection and a target-status gate, plus rejected and retired states — and no delete, no redaction and no TTL of any kind"
  scoping: "One `.agent-mesh/` per repository; the multi-repo Workbench resolves an opaque repo ID to a store, but no scope key is stored on a record or applied as a filter"
  integration: "Two CLIs (`agent-mesh`, `agent-q`), a loopback Workbench UI with a supervised background service, and a versioned contract block installed into `AGENTS.md` and `CLAUDE.md`"
  background: "None over memory. A user-level service (launchd, systemd, Task Scheduler) supervises the Workbench server; nothing re-reads or rewrites the store on a schedule"
  trust: "A six-value `status` column — proposed, accepted, in_force, rejected, superseded, retired — with tier-driven promotion, optional reviewer quorum, and re-approval forced by editing an accepted record"
  strengths: "Editing an accepted decision emits `decision_revisited`, clears `accepted_utc` and returns the record to proposed, so a revision cannot silently inherit its predecessor's approval"
  risks: "`decision_verifications` is populated by no shipped write path and executed with `shell=True` by `agent-q decisions verify`; a single stop-line-violating event is durably appended and then aborts every subsequent read"
---

## 1. Executive Summary

Agent Mesh is a project-local coordination substrate for human-plus-agent teams:
19,170 lines of Python across `src/agent_mesh/`, MIT, version 0.2.0, five
commits between 14 and 16 July 2026 on a repository whose first commit is
`chore: publish clean agent-mesh surface` — a curated publish of work developed
elsewhere, which is why the history says nothing about how the design arrived.
It has **no third-party dependencies**: `pyproject.toml` declares an empty
`dependencies` list under the comment *"Stdlib-only by design for core."* That
is rare enough in this corpus to state first, and it means the supply-chain
surface of adopting it is the Python standard library and nothing else.

The substrate is a hash-chained append-only `events.jsonl` with SQLite as a
declared projection of it. Most of what flows through it — requests, responses,
backlog items, dispatch runs and leases — is coordination state rather than
memory: a request is an act, not a claim that can turn out false. **The memory is
the decision log**, and it is a serious one. A decision carries a human ID with
aliases, a tier, an externalized Markdown body addressed by SHA, an owner, a
status, an enforcement mode, affected-code globs, exemptions, required checks,
assumptions, evidence references, tags, and a list of verification commands with
expected signals. Supersession detects cycles and refuses a target that was never
accepted. Acceptance can require a reviewer quorum. Three tiers skip `accepted`
and go straight to `in_force`.

**The best thing here is the revision rule, and it is a mechanism rather than a
convention.** Editing a decision that is `accepted` or `in_force` through the
Workbench requires a reason, emits a `decision_revisited` event, and sets
`fields_changed["status"] = [status, "proposed"]` — the projection then clears
`accepted_utc` and the record has to be accepted again. A revised decision cannot
inherit the approval of the thing it replaced. Very little in this atlas closes
that loop.

**The worst thing is that the verification apparatus cannot be filled.** Both
shipped write paths — `cmd_decision_propose` in `cli/mail.py` and
`create_decision` in `workbench.py` — construct the `decision_proposed` payload
with `"verification": []`, `"assumptions": []`, `"required_checks": []` and
`"evidence": {}` hardcoded, and the Workbench also hardcodes
`"affected_code_globs": []`. The only later mutation event,
`decision_metadata_updated`, handles title, owner, tier, body, human ID, status
and seven meta fields, and touches none of those five. So
`decision_verifications`, `decision_assumptions`, `decision_checks` and
`decision_evidence` have tables, projections, a rebuild path and consumers —
and no producer. `agent-q decisions verify` reads a table that the package
cannot write.

Two further findings follow from reading the read path rather than the schema.
The dispatch grounding packet that an agent actually receives has a section
called `prior-decisions`, and it is not the decision store: `prior_decisions_text`
regex-matches `APPROVE|REJECT|GO|NO-GO` and friends against the bodies of
`res_posted` messages in the same thread. **No decision record reaches an agent's
context through any automatic path**; the contract installed into `AGENTS.md`
tells the model to go and look. And every `agent-q` read calls
`rebuild_all`, which does `reset_schema` and replays the entire log —
`projection_is_current` exists and is called from exactly one place, the
Workbench refresh.

There are **zero tests** in the published tree.

## 2. Mental Model

A memory here is a **decision**: a durable, human-identified record (`D001`,
`D038-S1`, `D076-E`) of something the project settled, with the argument in an
externalized Markdown body addressed by `body_sha` and the structure in the event
payload. Everything else the log carries is a different kind of thing. A request
is a speech act; a backlog item is workflow state; a dispatch lease is a
concurrency primitive. None of them can be wrong in the way a decision can, and
the design is right not to treat them alike.

Nothing extracts a decision. There is no model anywhere in the package — an agent
or a human names the decision, and the substrate's job is to make the naming
durable, ordered and hash-linked. Capture is therefore a deliberate act with a
form, which puts Agent Mesh at the far explicit end of
[zero-LLM capture](../../patterns/zero-llm-capture/).

The state machine is a `status` column and it is real. `decision_proposed`
inserts at `proposed`. `decision_accepted` first checks a reviewer quorum
(`_decision_quorum_reached`, which reads `review_policy.required_reviewers` and
`approval_quorum` and returns `True` when none are configured), then promotes to
`in_force` if the tier is `architecture_contract`, `production_invariant` or
`compliance_security`, and to `accepted` otherwise. `decision_rejected` and
`decision_retired` are terminal marks; `decision_superseded` points the old
record at a successor and the successor back at the old one, after
`_ensure_supersede_target_valid` refuses a target that is not `accepted` or
`in_force` and `_ensure_no_supersede_cycle` walks the chain.

**The transition worth studying is the reverse one.** Editing an accepted or
in-force decision in the Workbench is refused without a `revision_reason`, then
emits `decision_revisited` and folds `status: [old, "proposed"]` into the
metadata update. `_project_decision_metadata_updated` reads that and sets
`accepted_utc = NULL`. Approval is attached to a version of the content, not to
the record, and the code enforces the difference.

Two states in the vocabulary have no producer. `decision_assumption_violated`
would flip a `decision_assumptions` row to `violated` and stamp the invalidating
event; `decision_check_failed` would append to the decision's log. Both appear in
the accepted-kinds set and in the projection's `elif` chain, and neither is
emitted by any code path in the package. `decision_drift_detected` is emitted, by
one command.

Nothing forgets. There is no delete, no redaction, no expiry and no retention
policy over decisions or messages — the only `DELETE` statements in the tree
clear derived SQLite rows before reprojection. `body_fidelity` admits the value
`redacted`, and it is a label a caller may pass to `agent-mesh request
--body-fidelity`; no code path produces it, and nothing removes the bytes it
would describe.

```mermaid
stateDiagram-v2
    [*] --> Proposed: "decision_proposed — verification, assumptions, checks and evidence all arrive empty"
    Proposed --> Accepted: "decision_accepted, quorum met, ordinary tier"
    Proposed --> InForce: "decision_accepted — architecture_contract, production_invariant or compliance_security"
    Proposed --> Rejected: "decision_rejected"
    Accepted --> InForce: "status set through decision_metadata_updated"
    Accepted --> Proposed: "Workbench edit — reason required, emits decision_revisited, clears accepted_utc"
    InForce --> Proposed: "same rule — approval belongs to the content, not the record"
    Accepted --> Superseded: "decision_superseded — target must be accepted or in_force, cycles refused"
    InForce --> Superseded
    Accepted --> Retired: "decision_retired"
    InForce --> Retired

    note right of Rejected
        Keyed on the record, not the value.
        Nothing stops the same content
        being proposed again as D-next.
    end note

    note right of InForce
        enforcement_mode is computed from
        the tier, stored, and printed in a
        rendered Markdown view. No read path
        consults it.
    end note
```

## 3. Architecture

Nothing has to be running to store or read anything. A project is a
`.agent-mesh/` directory holding `config.toml`, `events.jsonl`, externalized
bodies, a SQLite file, generated Markdown views and a lock.

**The log is the store.** `core/events.py` defines a frozen `Event` envelope —
`event_id`, `schema_version`, `occurred_utc`, `event_seq`, `actor`, `kind`,
`entity_id`, `thread_id`, `prev_event_hash`, `payload` — serialized through
`canonical_json` with sorted keys and no whitespace, hashed with SHA-256 over the
exact newline-terminated bytes. `core/chain.py` verifies the chain in two modes
and its docstring states the limit of the cheap one precisely: an anchored walk
*"does NOT prove that an arbitrary earlier prefix line was not rewritten in place
at the same byte length; that requires the full walk"*. The chain is unkeyed, so
it is tamper-evident against accident and against an editor who does not
recompute, and not against anyone who does.

**SQLite is a projection and says so.** `store/sqlite.py` creates roughly thirty
tables; `store/rebuild.py` replays the log into them. `reset_schema` wipes,
`apply_record` refuses a gap in `event_seq`, and `table_hashes_for` canonically
dumps and hashes every table so two machines can compare projections. This is the
cleanest instance in the corpus of the log-and-projection split the atlas records
in [its own notes](https://github.com/neoneye/agent-memory-atlas/blob/main/notes/2026-08-03-the-log-and-the-projection.md):
the derived store is disposable by construction, and the code treats it that way.

**Concurrency** is an owner-aware file lock (`core/lock.py`) carrying a PID, a
boot ID and a hostname, with `OwnerStatus` distinguishing `live`,
`stale_pid_dead`, `stale_age_exceeded` and `cannot_verify`, and a 600-second
staleness bound. Interrupted writes are recovered idempotently
(`core/recovery.py`), and `dispatch/atomic.py` journals a set of replace and
delete operations so a crash rolls forward rather than leaving a half-applied
unit.

**The Workbench** (`workbench.py`, 4,411 lines) is a loopback HTTP server plus a
single-file HTML page, with a per-server access token carried in a URL fragment,
restricted browser origins, a `0600` machine-local bookmark stored outside any
repository, and retry-safe receipts so an uncertain feedback retry returns the
original request instead of creating a second one.
`workbench_service.py` installs it as a user-level service under launchd,
`systemd --user` or Task Scheduler, serving every repository in a machine-local
registry from one process.

### Deployment and ergonomics

`pip install agent-mesh`, then `agent-mesh init` in a repository. No database
server, no key, no network, no model. Python 3.11+ and the standard library.

The store is repairable by hand in the ordinary sense — `events.jsonl` is one
canonical JSON object per line and the bodies are Markdown files — but with a
sharp caveat the design creates: editing a line invalidates every
`prev_event_hash` after it, so hand-repair means rewriting the chain, and there
is no tool for that. The delete-free, redaction-free design means the recovery
story for a mistaken write is *append a corrective event*, and for a decision
that is `decision_revisited` or `decision_superseded`. For anything the schema
cannot express, there is no story.

Privacy is the part of the operator experience that has had the most thought.
New projects default to `local-only`, whose generated `.agent-mesh/.gitignore` is
deny-all and ignores itself, so a plain `git add -A` selects nothing.
`git-shared` is an explicit opt-in allowlisting exactly the config, the event log
and externalized bodies — and `docs/privacy.md` refuses to oversell it: *"This is
an allowlist of canonical state, not a promise that the allowed files are
public."* It also states that configs predating the setting are read as
`git-shared` rather than silently made private, and that changing `.gitignore`
*"does not erase prior commits, forks, caches, or clones."*

## 4. Essential Implementation Paths

- **Append.** `core/events.py:append_event` — assigns `event_seq` and
  `prev_event_hash` from the tail, validates provenance
  (`core/provenance.py:validate_event_provenance`) and dispatch payloads
  (`core/dispatch_schema.py`), writes the canonical line. **Decision stop lines
  are not checked here.**
- **Project.** `store/rebuild.py:rebuild_all` → `reset_schema` → `apply_record`
  per event → `_project_record`. Decision handling is `_project_decision_event`
  around `:1099` and `_project_decision_proposed` at `:1179`.
- **Decision write surfaces.** `cli/mail.py:cmd_decision_propose` (`:838`),
  `cmd_decision_accept`, `cmd_decision_revisit`, `supersede`, `retire`; and
  `workbench.py:create_decision` (`:500`) and the edit path (`:680`).
- **Decision read surfaces.** `cli/q.py:cmd_decisions_list/show/log/search/at/verify`
  (`:733`–`:914`) and the Workbench Decisions tab.
- **Verification runner.** `cli/q.py:cmd_decisions_verify` (`:866`) —
  `subprocess.run(row["command"], cwd=config.project_root, shell=True)`, emitting
  `decision_drift_detected` on non-zero exit.
- **Grounding.** `dispatch/grounding.py` — sections for referenced rows, git
  state, `prior-decisions` (`prior_decisions_text`, `:57`) and the full thread,
  each tagged `stable` or `volatile` and hashed.
- **Packet.** `cli/q.py:cmd_packet` → `message_packet.py:build_message_packet`;
  the word *decision* does not occur in that module.
- **Chain integrity.** `core/chain.py`, exposed as `agent-q verify-chain`.
- **Locking and recovery.** `core/lock.py`, `core/recovery.py`,
  `dispatch/atomic.py`.
- **Agent contract.** `skill/render.py:CANONICAL_SKILL_BODY`, installed by
  `adoption.py` into `AGENTS.md` and, when the repository shows signs of it,
  `CLAUDE.md`.
- **Tests.** None.

## 5. Memory Data Model

`decisions` is the table that matters: `dec_ulid` primary key, `human_id`,
`parent_human_id`, `title`, `tier`, `status`, `enforcement_mode`, `owner`,
`body_sha`, `body_path`, `body_bytes`, `body_media_type`, `superseded_by`,
`supersedes`, `proposed_utc`, `accepted_utc`, `in_force_utc`, `retired_utc`,
`last_verified_utc`, `drift_risk`, `event_seq`, `meta_json`. Around it sit
`decision_aliases` (a renamed decision keeps its old ID resolvable, with one
primary), `decision_globs` (kinds `affected`, `exempt`, `generated`),
`decision_checks`, `decision_verifications`, `decision_assumptions`,
`decision_evidence`, `decision_references_in_code` and `decision_tags`.

Separating the body from the record by SHA is the right call and it pays off
twice: `body_sha` is a field `decision_metadata_updated` can change, so a
revision is a content-hash change with an event behind it, and the alias table
means the identifier a human uses is decoupled from the identity the projection
keys on.

**Temporal fields are all record time.** `occurred_utc` on the event,
`event_seq` for order, and four transition stamps on the decision. There is
nothing recording when a decision was true *of the world* as distinct from when
the project wrote it down, and no as-of query — `agent-q decisions at` takes a
file path, not a date. Single axis, so not
[bi-temporal](../../patterns/bi-temporal-fact-validity/), though the log makes
the history reconstructible by replay in a way most single-axis stores cannot
manage.

**There is no scope key.** The boundary is `.agent-mesh/` in a directory, the
same filesystem-boundary answer as [Graphify](../graphify/) and
[Klypix MCP](../klypix-mcp/). The near-miss is worth naming because it looks like
more: the multi-repo Workbench server *"resolves its opaque repo ID before
feedback, request-status, backlog, attachment, or decision operations"*, which is
a real access-control indirection over a machine-local registry. But it selects
which store to open rather than filtering rows inside one, and no record carries
a tenant, user or workspace key. `config.participants` is the closest thing to an
identity list, and it gates who may act, not what may be read.

Provenance is the model's other strength, and it is on the message side rather
than the decision side. `core/provenance.py` defines closed vocabularies for
`body_authority` (`human_chat`, `agent_mail`, `tool_payload`, `agent_summary`,
`recovery_artifact`, `unknown`), `body_fidelity` (`full`, `metadata_only`,
`reconstructed`, `inferred`, `redacted`, `missing`), source-selection modes and
eight causal-edge relations. **Distinguishing what a human said from what an
agent summarised, as a validated enum on the record, is a thing this atlas asks
about constantly and finds rarely** — and the grounding path uses it, refusing to
call a packet complete when a thread event's fidelity is not `full`.

## 6. Retrieval Mechanics

Retrieval is deliberate and thin. `agent-q decisions search` selects every row
from `decisions`, builds a haystack from `human_id`, `title`, and the `context`
and `decision` strings inside `meta_json`, and prints rows whose lowercased
haystack contains the lowercased query. No index, no ranking, no scoring, no
limit, and the body — the file where the actual argument lives — is not searched
at all. `agent-q decisions at <path>` is the more interesting query: it joins
`decision_globs` where `kind='affected'` and `fnmatch`es the relative path, which
answers *which decisions govern this file*. That is the right question, and the
Workbench cannot create the globs it needs.

Neither query filters on status. A retired, rejected or superseded decision
prints alongside a live one with its status in the second column, which is the
recall-first-and-label choice and is defensible on a surface a human reads.

**The automatic path does not retrieve decisions at all.**
`dispatch/grounding.py` assembles a packet with a stable prefix and volatile
suffix — a cache-shaped design, and it hashes every section so a caller can see
what changed — but its `prior-decisions` section comes from
`prior_decisions_text`, which scans `res_posted` events in the current thread for
the regex `\b(APPROVE_WITH_CHANGES|APPROVE|REQUEST_CHANGES|REJECT|NO-GO|GO)\b` in
the summary and the first 200 characters of the body. Those are review verdicts
inside messages, not records in the decision store. `build_message_packet`, which
backs `agent-q packet`, contains no reference to decisions either.

So the substrate's durable, tiered, supersession-aware memory is reachable by an
agent only if the agent runs a query, and the thing that tells it to is prose:
the contract installed in `AGENTS.md` says *"Run `agent-q status` and targeted
`agent-q list/locate/body` before responding."* This is the shape the atlas
records as [the guidance was already in
context](https://github.com/neoneye/agent-memory-atlas/blob/main/notes/2026-08-08-the-guidance-was-already-in-context.md)
— an instruction to consult standing in for a mechanism that consults.

The other retrieval cost is structural. Twenty-one `agent-q` commands begin with
`_rebuild_all_locked`, which calls `rebuild_all` unconditionally: wipe the
schema, read the whole log, replay every event. `projection_is_current` compares
the log's SHA-256 against the value stamped in the projection's `meta` table and
would let a reader skip all of that; it is called from one line in
`workbench.py`. The optimisation exists, is correct, and was applied to one of
the two readers — the interactive one, in the commit titled `perf: reduce
Workbench refresh work`. Every command-line read still pays for the full history.

## 7. Write Mechanics

Writes are synchronous, deterministic, and cheap in model terms because no model
is involved. The path is: acquire the project lock, read the tail line for
`event_seq` and `prev_event_hash`, validate, append the canonical line, project.
A new decision is retrievable immediately — the next reader replays the log and
sees it.

Idempotence and crash safety got real attention. `AGENT_MESH_FAULT_AFTER` is a
fault-injection hook in the append protocol, `core/recovery.py` handles
interrupted writes, `dispatch/atomic.py` journals its file operations for
roll-forward, and the Workbench's feedback receipts make an uncertain retry
return the original request ID.

**The write path does not validate decision invariants.** `append_event` calls
`validate_event_provenance` and `validate_dispatch_payload`; there is no
equivalent for decisions. The decision invariants — a superseded target must be
accepted or in force, no supersession cycles, no human-ID collision, no alias
fork, no missing parent — are all enforced at *projection* time, by raising
`DecisionStopLine`, and nothing catches that inside `rebuild_all`. The
consequence is a poison event: an event violating a stop line is durably
appended, hash-chained into the log, and then aborts the replay. Because
`rebuild_all` runs at the top of essentially every read, **one bad decision event
makes the whole store unreadable from the CLI** — and the log has no delete, no
skip and no quarantine, so the repair is to rewrite an append-only hash chain by
hand. Validating at the write boundary as well as the replay boundary is the
standard defence and it is one function call away from where it already lives.

The other write-side finding is the one in this report's title. Both propose
paths hardcode the interesting lists empty:

```python
"assumptions": [],
"evidence": {},
"required_checks": [],
"verification": [],
```

and `create_decision` in the Workbench adds `"affected_code_globs": []` to that
set, so the only way to attach a glob is the CLI's `--affects`. The one later
mutation event covers title, owner, tier, body, human ID, status and the seven
`meta_fields`; it cannot reach any of the four. The tables, the projection code,
the drift event and the runner all exist for data no shipped command can create.
The honest framing is that the substrate is a library — the README says
*"Project-specific importers should live in the consumer repository"* — so a
consumer can import `append_event` and construct a fuller payload. But a reader
who installs the package and follows the documented flow gets a decision with an
empty verification list and a verify command that prints `no verification
commands`.

Nothing filters malicious input, and one path makes that sharper than usual.
`agent-q decisions verify` runs each stored verification command through
`subprocess.run(..., shell=True)` in the project root. The command string is
memory: it arrives in an event payload, written by whichever participant appended
it, and the participant set includes agents. A memory store whose records can
contain a shell command that a maintenance command later executes is a
prompt-injection path with an unusually short distance to code execution. That
the field is currently unfillable through the shipped surfaces is what keeps it
theoretical, which is an uncomfortable pair of facts to hold together: the same
gap that makes the feature useless is the thing making it safe.

## 8. Agent Integration

There is no MCP server and no SDK. The integration is two CLIs and a contract.

`agent-mesh` writes: `init`, `request`, `reply`, `respond`, `resolve`, `reopen`,
`decision propose|accept|revisit|supersede|retire`, `backlog upsert|link`,
`skill render|install`, `adopt`, `workbench`. `agent-q` reads: `list`, `locate`,
`body`, `packet`, `thread`, `trace`, `render`, `rebuild`, `recover`,
`verify-chain`, `status`, `events`, `backlog`, `decisions
list|show|log|search|at|verify`, `dispatches`.

`adoption.py` installs a versioned managed block into `AGENTS.md`, and into
`CLAUDE.md` when the repository already has one or a `.claude/` directory.
`agent-mesh adopt --check` detects a stale contract *and conflicting legacy
decision-write guidance*, and the contract text tells the agent that finding one
*"is an adoption defect; report it instead of silently choosing a second source
of truth."* Treating a second writable surface for the same facts as a defect the
tool detects, rather than a documentation problem, is the right instinct.

The contract itself is the best-written agent-facing prose in this part of the
corpus, and one passage is worth copying outright. Under *Quality Discipline* it
names event kinds that do not exist yet and instructs against inventing them:

> Until quality/investigation events exist, treat this as advisory procedure.
> Future event names (do not invent today): `quality_bar_declared`,
> `quality_bar_updated`, `quality_gate_evaluated`, `investigation_opened`, …

A model asked to record something for which no verb exists will invent one. Naming
the reserved vocabulary in advance is a cheap defence against a schema being
polluted by plausible guesses, and nothing else in this atlas does it.

Against that, the contract also carries the system's weakest guarantee: *"Run
`agent-mesh decision accept` only after explicit human approval and name the
approving human with `--by`."* `cmd_decision_accept` takes `--by` as a free
string and appends the event. The Workbench is stricter — `_decision_actor`
rejects an actor outside `config.participants` — but participants routinely
include the agents. Human acceptance is a mechanism in the UI and an honour
system at the command line, and the same event kind serves both.

## 9. Reliability, Safety, and Trust

**Integrity.** The hash chain is the strongest property and its own docstrings
scope it correctly: full walks catch a same-length rewrite of an earlier line,
anchored walks do not, and the anchored mode is offered as an incremental gate
rather than as the audit. `table_hashes_for` extends the idea to the projection
so two replicas can compare derived state. What none of it provides is
authenticity: SHA-256 with no key means the chain proves the log has not been
*carelessly* edited, and anyone who can write the file can produce a consistent
forgery. For a project-local file that is a reasonable place to stop, but
"tamper-evident" in the README is doing work that a signature would do properly.

**Trust states** are genuine and applied. `status` gates supersession
(`_ensure_supersede_target_valid`), drives the tier promotion, and is reset by the
revision path. What is absent is any gate on *reading*: an agent that queries
`decisions search` gets proposed records beside in-force ones, and
`enforcement_mode` — computed per tier, stored on every row, and non-null by
schema — is consulted by no code path in the package. It is printed in a rendered
Markdown view. A field named for enforcement that enforces nothing is worth
saying plainly, and it is the same class of finding as the four unwritable tables.

**Audit** is the capability this system has most completely. The event log is not
a sidecar record of mutations; it *is* the store, append-only, ordered,
hash-linked and schema-versioned, with the queryable form defined as derived from
it. `_append_decision_log` additionally keeps a per-decision event trail, and
`agent-q decisions log` prints it. Nothing in this corpus makes the mutation
record more load-bearing.

**Human review** exists as a place: the Workbench Decisions tab creates proposals,
appends revisions with a required reason, and records acceptance, with the
re-approval rule enforced in code. The caveats above are real — an agent in the
participant list can accept, and the CLI does not check even that — but a person
inspecting and adjudicating memory content has somewhere to do it.

**The reference scanner checks the inverse of what the schema suggests.**
`agent-mesh decision refs` walks the tree for `D001`-shaped tokens and reports
the ones that resolve to nothing — a *dangling* reference, a citation of a
decision that does not exist — recording the list in a
`decision_scanner_run_completed` payload with `--record-scan`. It never writes
`decision_references_in_code`; that table is filled by
`decision_reference_resolved` events, which no code path emits, so the join
between a decision and the lines of code that cite it stays empty. The check
that ships is the cheap and useful half, and no other system here checks that a
memory's *identifier* is citable at all — but it runs the opposite direction to
[verify memory against its subject](../../compare/#verify-memory-against-its-subject),
which asks whether the cited code moved rather than whether the citation
resolves. Both would be worth having; one is here.

**Failure modes worth naming.** The poison event of section 7 is the sharpest:
one stop-line violation makes every CLI read fail, permanently, in a store with
no delete. The full-replay-per-read is the second: correctness is excellent —
the projection cannot drift, because it is rebuilt — and the cost is linear in
total history on every query. And a projection whose invariants are enforced only
during replay means the log can hold a state the code will never accept, which
is precisely the situation the write-time validator exists to prevent.

**Privacy and deletion.** Local-only by default, deny-all `.gitignore` including
itself, an explicit allowlist for the shared mode, and a publish checklist that
tells the reader to inspect commit authors, screenshots and package artifacts.
Against that: there is no delete and no redaction. If a request body captured a
secret or a personal detail, the substrate's answer is the same one
`docs/privacy.md` gives for Git — rotate it, because the record is not coming
out. For a design that stores human chat verbatim under a `human_chat` authority
label, an intentional redaction path is the obvious next mechanism, and the
`redacted` fidelity value is already sitting in the enum waiting for it.

## 10. Tests, Evals, and Benchmarks

There are no tests. Not a `tests/` directory, not a `test_*.py`, not a
`conftest.py`, nothing under `examples/` that asserts. The `.gitignore` excludes
`.pytest_cache/`, `.coverage`, `htmlcov/`, `.tox/` and `.mypy_cache/` — artifacts
of a suite that is not in this tree, which is consistent with the repository
being a curated publish of a larger internal one rather than with there being no
suite at all. Either way, what a reader can check is nothing.

That matters more here than in most reports, because the design's claims are
exactly the kind that only a test can support. Idempotent crash recovery, a
fault-injection hook (`AGENT_MESH_FAULT_AFTER`) that exists specifically to be
driven by a test, roll-forward of a journaled atomic apply, owner-aware lock
staleness across a reboot, a projection that must exactly reproduce the log, and
stop lines that must fire — every one of these is asserted by a docstring and by
no executable. The fault-injection environment variable is the clearest signal:
somebody wrote a seam for a test harness, and the harness is not here.

What ships instead is two runnable examples, `examples/solo-project/run.sh` and a
parameterized `N=3 examples/n-agent/run.sh`, which exercise the flow and check
nothing. `agent-q verify-chain`, `agent-q audit-recovered-sources` and
`agent-mesh adopt --check` are operator-facing verification commands and a
reasonable substitute for *runtime* assurance, but they verify a live store, not
the code's behaviour.

There is no paper, no benchmark, and no performance claim — grepping the README,
`docs/` and the source for `arxiv`, `bibtex`, `@article`, `@misc`, `Citation` and
`doi` returns nothing, and there is no `CITATION.cff`. The README makes no
quantitative claim at all, which given the absence of tests is the correct
restraint: nothing here is asserted that a reader is invited to trust on
numbers.

Before relying on this I would want, in order: a test that a stop-line violation
does not brick every subsequent read; a test that the projection of a fixed log
hashes to a fixed value; a test driving `AGENT_MESH_FAULT_AFTER` through the
recovery path; and one asserting that a revised decision loses its
`accepted_utc`, because that is the mechanism the design is best at and nothing
currently protects it from a refactor.

## 11. For Your Own Build

### Steal

- **Make approval belong to the content, not the record.** Requiring a reason to
  edit an approved record, emitting a distinct revision event, and clearing the
  approval stamp so it must be granted again is a handful of lines and closes the
  hole where a memory keeps its blessing through a rewrite.
- **Name your reserved vocabulary to the model before you implement it.** A
  contract that lists the event names a future version will use, under *do not
  invent today*, costs one paragraph and prevents a schema being polluted by
  plausible invented verbs.
- **Treat a second writable surface for the same facts as a detectable defect.**
  `adopt --check` looks for conflicting legacy decision-write guidance and reports
  it. Most projects document the migration and hope; a check that fails is better.
- **Put provenance in a closed enum and validate it on append.** Separating *who
  authored this* from *how faithful is this copy* — `human_chat` versus
  `agent_summary`, `full` versus `reconstructed` — and rejecting values outside
  the set makes the difference queryable instead of conventional.
- **Hash the projection, not just the log.** A canonical per-table dump hashed
  after replay turns "did these two machines derive the same state" into a
  comparison rather than an argument.
- **State the limit of the cheap integrity check in the code.** The anchored-walk
  docstring explains exactly what it does not prove and keeps the full walk as
  the audit. Every incremental verifier should carry that paragraph.

### Avoid

- **Do not enforce invariants only at replay.** If a record can be durably
  accepted at write time and rejected at read time, you have built a store that
  can hold a state your reader will never accept — and in an append-only log with
  no delete, that state is permanent. Validate at both boundaries, or make the
  replay skip and quarantine rather than abort.
- **Do not ship a table with a consumer and no producer.** Four decision
  side-tables here have projections, a rebuild path and a runner, and no write
  surface. A reader inspecting the schema concludes the system verifies its
  decisions; a reader tracing the write path finds it cannot.
- **Do not execute memory.** A stored field that a maintenance command feeds to a
  shell is a memory store with a code-execution path, and the writer of that
  field is whoever can append an event. If verification commands must be stored,
  bound them to a declared allowlist and never interpolate them into a shell.
- **Do not let the derived index be rebuilt from scratch on every read.** The
  correctness argument for full replay is good and the cost is unbounded in
  history. The skip check here is written and correct; it is simply not called
  from the reader that runs most often.
- **Do not write an enforcement field nothing reads.** `enforcement_mode` is
  computed, stored, non-null and printed. Either a read path consults it or the
  column is documentation with a schema constraint.

### Fit

This suits a small team that wants coordination between humans and several coding
agents to leave a record it can audit, in a repository it controls, with no
service and no vendor. The install cost is genuinely near zero — standard library
only, one directory, and a privacy default that errs toward not committing
anything — and the log-and-projection architecture means the parts most likely to
be wrong are the disposable ones. If what you want is an inspectable history of
who asked for what and what the project decided, this is a more careful
foundation than most.

It is not a memory layer for an agent's working knowledge, and reading it as one
will disappoint. Nothing is retrieved automatically, nothing is ranked, nothing
is summarised, and the only thing standing between a decision and the model that
should honour it is an instruction to go and query. Walk away entirely if you
need multi-user or multi-tenant boundaries, if you need to delete or redact
anything you have stored, or if you cannot accept a substrate whose durability
guarantees are asserted by docstrings and checked by nothing. At 0.2.0, with a
five-commit published history and no test suite, the right posture is to read the
design for its ideas — several of which are better than what surrounds them —
rather than to adopt it for the guarantees.

## 12. Open Questions

- Does the upstream development repository have the test suite the `.gitignore`
  and `AGENT_MESH_FAULT_AFTER` imply? The published history is five commits
  beginning with a curated publish, so this cannot be settled from the tree.
- What was the intended producer for `decision_verifications` and the three
  sibling tables — a richer Workbench form, a consumer-side importer, or a
  command that was not part of the published surface?
- What actually happens to a live project after a stop-line-violating event is
  appended? The code path says every read fails; whether an operator has a
  recovery route in practice needs the tool run against a constructed log, which
  this reading did not do.
- Does the Workbench expose `review_policy`, and therefore the reviewer quorum,
  anywhere in its forms? The propose payload hardcodes it empty and
  `decision_metadata_updated` can carry it, so the capability may exist through a
  path this reading did not find.

## Appendix: File Index

- **Log and integrity** — `core/events.py`, `core/hashing.py`, `core/chain.py`,
  `core/ids.py`, `core/lock.py`, `core/recovery.py`,
  `core/source_recovery*.py`, `core/external_recovery_plan.py`.
- **Schema and projection** — `store/sqlite.py`, `store/rebuild.py`.
- **Decision model** — `_project_decision_proposed` and
  `_project_decision_metadata_updated` in `store/rebuild.py`;
  `enforcement_for_tier`, `_decision_quorum_reached`,
  `_ensure_supersede_target_valid`, `_ensure_no_supersede_cycle`.
- **Provenance** — `core/provenance.py`.
- **Write surface** — `cli/mail.py`, `workbench.py`.
- **Read surface** — `cli/q.py`, `message_packet.py`, `views/rendering.py`,
  `views/inbox.py`, `views/outbox.py`, `views/archive.py`, `views/log.py`.
- **Grounding and dispatch** — `dispatch/grounding.py`, `dispatch/dispatch.py`,
  `dispatch/atomic.py`, `dispatch/guard.py`, `dispatch/runtime.py`,
  `core/dispatch_schema.py`.
- **Agent integration** — `skill/render.py`, `adoption.py`,
  `project_registry.py`, `workbench_service.py`.
- **Docs** — `README.md`, `docs/adoption.md`, `docs/configuration.md`,
  `docs/migration.md`, `docs/privacy.md`.

## History

**2026-08-10** — [`258a1eed288513e24953a633c44b397e91ea9886`](https://github.com/cbalgeman/agent-mesh/commit/258a1eed288513e24953a633c44b397e91ea9886) —
first reading, at 5 commits. Screened before reading: 0 auto-run surfaces, 0
dependency surfaces inside the seven-day cooldown, 1 unpinned manifest with no
lockfile — which is a declared-but-empty `dependencies` list, so there is no
third-party surface to pin. Nothing was installed and nothing was executed; the
two shipped examples were read rather than run.

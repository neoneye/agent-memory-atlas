---
title: "MemoryIndustry"
eyebrow: "It published the benchmark that was lying"
description: "A Rust MCP memory server over PostgreSQL whose quarantine tier is enforced by an allow-list on the search path and pinned by tests that pair each must-not with its control, and whose README retracts its own headline retrieval number and the two conclusions drawn from it."
root: ../..
page_kind: system
source_name: "LeandroPG19/Memorys"
source_url: https://github.com/LeandroPG19/Memorys
archive_name: "LeandroPG19--Memorys"
revision: 2f45dcb729426b4b5bfca45981d52a39d3f09d0b
revision_url: https://github.com/LeandroPG19/Memorys/commit/2f45dcb729426b4b5bfca45981d52a39d3f09d0b
analyzed_at: 2026-09-20
capabilities: "trust_state, scope_enforced, negative_eval"
capability_evidence:
  trust_state: "the quarantine tier on every content table | rust/src/core/trust.rs:1-21, rust/src/search/bm25.rs:23, rust/src/search/calibrate.rs:64, :91, rust/src/constants.rs:375 | `trust` is one of two discrete strings rather than a score, kept apart from the ranking signals, and `quarantined` withholds a row from every search branch. The read predicate is an allow-list — `AND o.trust = 'trusted'` — so a tier added later would be hidden rather than exposed. The tool schema documents the door: text the caller marks untrusted lands quarantined, 'stored and inspectable via cuba_eco action=pending, but withheld from cuba_faro until promoted' | rust/tests/v016_quarantine.rs:67 and :151, rust/tests/v021_import_quarantine_all_kinds.rs:174. Two limits belong on the record: the automatic path is off by default, since `resolve` quarantines an inference source only when CUBA_QUARANTINE_INFERENCE is set, and an explicit tier supplied by the caller wins over both, so out of the box everything is trusted unless a caller says otherwise"
  scope_enforced: "project predicate in both search branches over forced row-level security | rust/src/search/bm25.rs:24, :59, rust/migrations/0017_rls_policies.up.sql:23-31, rust/migrations/0055_content_tables_get_rls.up.sql | both the BM25 and the vector branch compose the project predicate beside the trust predicate, and migration 0017 both ENABLEs and FORCEs row-level security on the listed tables under a `tenant_isolation` policy, FORCE being the clause that makes it apply to the table owner too; 0055 extends it to the content tables | the predicate reads `project_id = $3 OR project_id IS NULL`, so a globally-scoped row reaches every project by design — the isolation is between projects, not from the global set. The project's own doctor records the other limit in words: a superuser ignores RLS and can alter the audit log, so both isolation and traceability rest on nobody connecting as one"
  negative_eval: "quarantine must-not cases, each paired with its control | rust/tests/v016_quarantine.rs:67, :151, rust/tests/v021_import_quarantine_all_kinds.rs:174, rust/tests/v033_untrusted_extraction_does_not_touch_the_graph.rs:157 | committed cases assert material must not be retrieved and say so in the message — 'a quarantined memory must not surface in search' and 'a quarantined episode must not come back from cuba_faro, or the quarantine is a column'. The control sits in the same file: 'an ordinary agent write must stay retrievable — the gate must not change default behaviour', which is the half a filter excluding everything would fail. A further case pins that untrusted extraction never creates graph nodes | subsystem: these are negative retrieval assertions on the read path, the strict reading. The NLI entailment cases are `#[ignore]` because they need a downloaded model, so they do not run in an ordinary CI pass, though the helper forbids the usual escape — 'Soft-skip is forbidden'"
stack_storage: "postgres"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A row in one of three content tables — observations, episodes, errors — each carrying a `trust` tier and a `project_id`; facts live apart in `brain_facts` as subject/predicate/object with a validity window and a confidence"
  storage: "PostgreSQL 18 with pgvector, row-level security enabled and forced on the content tables under a `tenant_isolation` policy"
  retrieval: "Hybrid BM25 and vector, fused, with an optional cross-encoder reranker; both branches compose the same trust and project predicates"
  write: "An MCP tool call resolves the trust tier before the insert, from the source, an optional caller-supplied tier and a policy that quarantines LLM inference only when an environment variable enables it"
  update_delete: "Superseding a fact sets `is_current = FALSE` and `valid_to` together, which a CHECK constraint requires; feedback records an outcome per memory. Nothing keys a rejection on the value, so the same claim arriving again is a new row"
  scoping: "A project predicate in both search branches that also admits globally-scoped rows, over forced row-level security at the database"
  integration: "An MCP server with 31 tools under `cuba_*` plus 23 CLI commands, published to PyPI, npm and the MCP registry"
  background: "Embedding backfill, calibration over recorded outcomes, deduplication, and a code-graph indexer"
  trust: "Two discrete tiers, trusted and quarantined. A quarantined row is stored and listable and admitted by no search path until promoted; the promoting action sits on the same tool the writing agent already holds"
  strengths: "The trust predicate is written as an allow-list so a new tier fails closed; each must-not test is paired with the control that would catch a filter excluding everything; database CHECK constraints were added with a comment naming the illegal states the schema had permitted; and the README retracts its own published retrieval score and the two conclusions drawn from it"
  risks: "The hash-chained append-only audit log has no writer on any memory path — its only insert is a tool action whose action string and payload come from the caller; both time axes on a fact are stamped from record time and no query reads the validity window, whose only accessor has no caller; and promotion out of quarantine is one value of an action enum on the writing agent's own tool"
---
## 1. Executive Summary

MemoryIndustry is an MCP server in Rust over PostgreSQL and pgvector, giving a
coding agent a searchable knowledge graph across sessions. Thirty-one MCP tools,
twenty-three CLI commands, Apache 2.0. It was called cuba-memorys until
recently, and the `cuba_*` tool names are unchanged.

**Three marks:** `trust_state`, `scope_enforced`, `negative_eval`. The
quarantine tier is the spine of all three. Text the agent did not vouch for is
stored with `trust = 'quarantined'`, every search path admits rows with
`AND trust = 'trusted'` — an allow-list, not an exclusion — and the tests pin
both directions: a quarantined memory must not surface, *and* an ordinary write
must stay retrievable, so a filter that excluded everything could not pass.

Two mechanisms that look like marks are withheld, and the reasons are the
interesting part of this page. The `brain_audit_log` is a hash-chained,
trigger-enforced append-only table maintained under `SERIALIZABLE` with an
advisory lock to keep the chain linear — and **no memory mutation writes to
it.** Its only writer is the `append` action of a tool, which takes the action
string and the payload from its caller. Separately, `brain_facts` carries
`valid_from`, `valid_to` and `observed_at` behind database CHECK constraints,
and every write sets validity from record time while no query asks a validity
question.

What distinguishes the project is section 10. Its README carries a heading
reading *"Measured — and the benchmark that was lying"*, retracts its own
published retrieval score, and withdraws the two conclusions that rested on it.

## 2. Mental Model

Everything written is trusted unless something says otherwise, and "otherwise"
has two sources: a caller that marks the text untrusted, and a policy that
quarantines LLM inference. A quarantined row is stored, listable and invisible
to search until a promotion moves it. Retrieval is hybrid — BM25 and vectors —
and both branches carry the same two predicates: the trust tier and the project.

## 3. Architecture

```mermaid
%% caption: text arrives from a tool call carrying an untrusted flag, and the trust tier is resolved from the source, the caller's explicit value and a policy that quarantines LLM inference only when an environment variable turns it on; both search branches admit rows with an allow-list trust predicate and a project predicate that also matches globally-scoped rows, and PostgreSQL row-level security is forced underneath; the audit chain is hash-linked and append-only by trigger but has no writer on any memory path, and the fact table carries a validity window whose ends are both stamped from record time and which no query reads
flowchart TD
    W["cuba_cronica write<br/>untrusted flag optional"] --> RES["core::trust::resolve<br/>explicit value wins if valid<br/>else source == inference<br/>AND policy on → quarantined<br/>else trusted"]
    RES --> ROW[("brain_observations · brain_episodes · brain_errors<br/>trust · project_id")]

    ROW --> S1["BM25 branch"]
    ROW --> S2["vector branch"]
    S1 --> P["AND trust = 'trusted'<br/>AND (project = $3 OR project IS NULL)"]
    S2 --> P
    P --> OUT["cuba_faro results"]

    ROW -.->|withheld| Q["cuba_eco action=pending<br/>lists what is quarantined"]
    Q --> PROM["action=promote<br/>an enum value on the<br/>agent's own tool"]
    PROM --> ROW

    RLS{{"RLS: FORCE ROW LEVEL SECURITY<br/>policy tenant_isolation"}} -.->|underneath| ROW

    F[("brain_facts<br/>valid_from · valid_to · observed_at<br/>CHECK valid_from <= valid_to<br/>CHECK NOT is_current OR valid_to IS NULL")]
    F --> SUP["supersede:<br/>is_current = FALSE<br/>valid_to = observed_at of the newer fact"]
    F -.->|"no query filters on the window"| NOREAD["was_valid_at: no caller<br/>outside its own tests"]

    A[("brain_audit_log<br/>sha256 chain · BEFORE UPDATE/DELETE trigger<br/>SERIALIZABLE + advisory lock")]
    TOOL["cuba_archivo action=append<br/>caller supplies action and payload"] --> A
    ROW -.->|"no path writes here"| A
```

## 4. Essential Implementation Paths

**The tier** — `rust/src/core/trust.rs:11-21`. `resolve(source, explicit,
policy_quarantines_inference)` returns the caller's `explicit` value when it is
one of the two legal strings, else `QUARANTINED` when the source is `inference`
*and* the policy is on, else `TRUSTED`. The policy is
`CUBA_QUARANTINE_INFERENCE`, unset by default, so out of the box nothing is
quarantined automatically.

**The read predicate** — `rust/src/search/bm25.rs:23-24`, repeated at `:59`, and
`rust/src/search/calibrate.rs:64, :91`. `AND o.trust = 'trusted'` beside
`AND ($3::uuid IS NULL OR o.project_id = $3 OR o.project_id IS NULL)`. The trust
clause names the state it admits; adding a third tier later would hide those
rows rather than expose them.

**The untrusted door** — `rust/src/constants.rs:375`, the tool schema. *"Set
when the text came from somewhere you do not control (a fetched page, a pasted
document, a third party). Everything extracted lands quarantined — stored and
inspectable via `cuba_eco action=pending`, but withheld from `cuba_faro` until
promoted."*

**The chain** — `rust/src/handlers/archivo.rs:145-173`. Each append opens a
transaction at `SERIALIZABLE` *"to keep the hash chain linear"*, takes
`pg_advisory_xact_lock` on a fixed key, reads the newest `current_hash`, and
inserts `sha256(prev_hash || action || payload || created_at_iso)`, retrying up
to five times. Migration `0016_audit_log.up.sql` puts `BEFORE UPDATE` and
`BEFORE DELETE` triggers on the table that raise unless the role is
`cuba_admin`, kept *"for legal data deletion under GDPR"*.

## 5. Memory Data Model

Three content tables — observations, episodes, errors — each with `trust` and
`project_id`. Facts live apart in `brain_facts` as
subject/predicate/object with `valid_from`, `valid_to`, `observed_at`,
`confidence` and `is_current`.

Migration `0029_bitemporal_check.up.sql` is worth reading for its candour. It
adds two CHECK constraints and explains that the original schema *"allowed
states that contradict its own model: `valid_from > valid_to` (a fact valid in
negative time); `is_current = TRUE` together with a `valid_to` already in the
past. Nothing prevented them."* It records that it checked the
existing rows and found none violating either constraint, and says a future
violation should make *"the migration fail loudly instead of corrupting silently
— which is the point."*

## 6. Retrieval Mechanics

Hybrid: a BM25 branch and a pgvector branch, fused, with an optional
cross-encoder reranker. Both branches carry the trust and project predicates.
Row-level security sits underneath — `0017_rls_policies.up.sql` enables *and*
`FORCE`s RLS on the listed tables and creates a `tenant_isolation` policy, and
`0055` extends it to the content tables. `FORCE` is the part that matters: it
applies to the table owner too.

The project's own `doctor` names the limit rather than leaving it implied — a
superuser ignores RLS and can alter the audit log, so project isolation and
traceability both rest on nobody connecting as one.

## 7. Write Mechanics

A write resolves its tier before the insert. Superseding a fact sets
`is_current = FALSE` and `valid_to` together, which is exactly what the second
CHECK constraint requires, so the invariant and the write path agree.

## 8. Agent Integration

Thirty-one MCP tools under `cuba_*`. Promotion out of quarantine is
`cuba_eco action=promote`, one value of an action enum that also carries
`positive`, `negative`, `correct`, `quarantine` and `pending`.

## 9. Reliability, Safety, and Trust

**`trust_state`.** Two discrete states, and `quarantined` withholds a row from
every search path. The tier is a field rather than a score, and the ranking
signals — confidence, decay — are separate from it.

**`scope_enforced`.** Two layers: the `project_id` predicate in both search
branches, and forced row-level security with a `tenant_isolation` policy
beneath. The predicate admits `project_id IS NULL` as well, which is how a
globally-scoped memory reaches every project, so the isolation the mark
describes is between projects and not from the global set.

**`negative_eval`.** Read-path must-not assertions with their controls beside
them — section 10.

**`audit_log` is withheld.** The table is a well-built tamper-evident ledger and
nothing on a memory path writes to it. Its sole `INSERT` is inside the `append`
branch of `cuba_archivo`, which takes the action string and the payload from its
caller, so a row exists only because an agent chose to write one and says
whatever that agent chose. A mutation audit has to be written by the mutation.

**`bitemporal` is withheld.** Both axes exist as columns and both are stamped
from record time: `valid_from` is `Utc::now()` at construction in both builders,
and supersession sets `valid_to = u.observed_at` of the superseding fact.
`was_valid_at` is the only function that would ask a validity question and has
no caller outside its own tests. The single query that touches the window is an
integrity check in `doctor` looking for `valid_to <= valid_from`.

**`human_review` is withheld.** Quarantine holds a memory in a state until
something resolves it, but `promote` is one value of the `action` enum on
`cuba_eco`, a tool the writing agent already holds. The producer can clear its
own queue.

**`tombstone` is withheld.** Supersession flips `is_current` on a row and
feedback records an outcome per memory; nothing keys a rejection on the value,
so the same claim arriving again is a new row.

## 10. Tests, Evals, and Benchmarks

Test files are named for the version and the invariant they defend —
`v016_quarantine.rs`, `v021_import_quarantine_all_kinds.rs`,
`v033_untrusted_extraction_does_not_touch_the_graph.rs` — and the assertion
messages carry the claim:

- *"a quarantined memory must not surface in search"* (`v016_quarantine.rs:67`),
  paired at `:151` with *"an ordinary agent write must stay retrievable — the
  gate must not change default behaviour."* The control is the harder half: a
  predicate that excluded everything would satisfy the first assertion alone.
- *"a quarantined episode must not come back from `cuba_faro`, or the quarantine
  is a column"* (`v021:174`) — the test states its own purpose, which is to
  prove the column is enforced rather than decorative.

The NLI cases in `rust/tests/nli_entailment.rs` are `#[ignore]` because they
need a downloaded model, and the helper refuses the usual escape:
*"Soft-skip is forbidden."* They do not run in an ordinary CI pass.

**The benchmark.** The README's own section, *"Measured — and the benchmark that
was lying"*, records that until v0.12 the file claimed every number was measured
and every number was wrong, in three ways: ten queries, so *"the smallest effect
it could detect was ~0.25 nDCG"*; relevance judged by substring match, which
*"measures keyword presence, not retrieval, and it tilts the whole benchmark
toward the lexical branch"*; and nDCG normalised against what was retrieved
rather than what exists, so a system that missed 60% of the answer scored 1.0.
An `R@10 = 3.125` had shipped — *"Recall is a proportion."*

The corrected figure is nDCG@10 = 0.50, 95% CI 0.44–0.56, over 221 id-scored
queries, against a published 0.894. The sentence that follows is the one worth
quoting: *"The system did not get worse. It was never 0.894."*

Two conclusions were withdrawn with it. One held that the cross-encoder reranker
earned nothing; it had never run — three bugs in series, an error dropped by
`if let Ok(..)`, `token_type_ids` fed to a model that is XLM-RoBERTa and has
none, and `f16` logits read as `f32`. The other held that associative retrieval
degrades results, which a paired bootstrap on the new dataset confirms at
[−0.051, −0.018] — *"The decision was right; the reasoning was not."*

## 11. For Your Own Build

### Steal

- **Write the trust predicate as an allow-list.** `trust = 'trusted'` fails
  closed when a tier is added; `trust != 'quarantined'` fails open.
- **Pair every must-not with its control.** `v016_quarantine.rs` asserts the
  quarantined row is absent and the ordinary row is present, in the same file.
- **Put the invariant in the database and say what it was protecting against.**
  Migration 0029's comment names the two illegal states the schema had permitted
  and reports how many rows violated them.
- **Take a lock to keep a hash chain linear.** `SERIALIZABLE` plus an advisory
  lock plus bounded retries is the honest way to append to a chain concurrently.
- **Retract your own number in the file that published it.** The heading is
  *"the benchmark that was lying"*, not a changelog line.

### Avoid

- **A ledger with no producer.** Hash chain, triggers, serializable appends —
  and a memory can be written, promoted or superseded without a row appearing.
- **Two time axes both stamped from the clock.** A validity window whose ends
  come from record time answers the same question the record time does.
- **Promotion as a value on the writer's own tool.** If the same agent can
  quarantine and promote, the tier records provenance rather than review.

### Fit

Take this if you want a Postgres-backed agent memory with a real quarantine tier
and are willing to run the promotion step yourself. Read section 10 before
taking any retrieval number from any project, including this one.

## 12. Open Questions

- `CUBA_QUARANTINE_INFERENCE` is off by default, so nothing is quarantined
  automatically unless a caller sets `untrusted`. Is the default meant to change?
- `brain_audit_log` has no writer on a memory path. Was it meant to be called
  from the write handlers, or is it a ledger for the agent's own use?
- `was_valid_at` has no caller. Is a validity-filtered read planned, and would
  `valid_from` then become caller-supplied?
- `promote` sits on `cuba_eco` beside the write actions. Is there a deployment
  where the promoting principal is not the writing one?

## Appendix: File Index

| Path | What it holds |
| --- | --- |
| `rust/src/core/trust.rs` | the two tiers and the resolution rule, with its own unit tests |
| `rust/src/search/bm25.rs` | the allow-list trust predicate and the project predicate, twice |
| `rust/src/constants.rs` | the tool schemas, including the `untrusted` flag and the `cuba_eco` action enum |
| `rust/src/handlers/archivo.rs` | the hash chain, the advisory lock, and the only audit insert |
| `rust/src/core/bitemporal.rs` | the `Fact` builder, the supersede write, and the uncalled `was_valid_at` |
| `rust/migrations/0016_audit_log.up.sql` | the chain definition and the append-only triggers |
| `rust/migrations/0017_rls_policies.up.sql` | `ENABLE` plus `FORCE ROW LEVEL SECURITY` and `tenant_isolation` |
| `rust/migrations/0029_bitemporal_check.up.sql` | the two CHECK constraints and what they were added against |
| `rust/tests/v016_quarantine.rs` | the must-not and its control |
| `README.md` | the retraction, the corrected figure and the two withdrawn conclusions |

## Appendix: Recorded Searches

Run from the root of the checkout at the pinned commit.

| Claim | Command | Result at this pin |
| --- | --- | --- |
| Nothing on a memory path writes the audit log | `grep -rn "brain_audit_log" --include='*.rs' rust/src \| grep -i insert` | One hit, `handlers/archivo.rs:173`, inside the `append` action of `cuba_archivo` |
| `was_valid_at` has no caller | `grep -rn "was_valid_at" --include='*.rs' rust/src` | Its definition and two assertions in its own test module |
| No query filters on the validity window | `grep -rn "valid_from\|valid_to" --include='*.rs' rust/src \| grep -iE "select\|where"` | `doctor.rs:705` only, an integrity check for `valid_to <= valid_from` |
| `valid_from` is never caller-supplied | `grep -rn "valid_from" --include='*.rs' rust/src \| grep -i "set \|valid_from:"` | `Utc::now()` in both builders, `core/bitemporal.rs:50` and `sync/chunk.rs:286` |
| The trust predicate is an allow-list on every search branch | `grep -rn "trust = 'trusted'" --include='*.rs' rust/src` | `search/bm25.rs:23`, `search/calibrate.rs:64` and `:91` |
| Promotion is on the agent's own tool | read `rust/src/constants.rs:161` | `promote` and `quarantine` are values of the `action` enum on `cuba_eco` |
| The licence carries no rider | `grep -n -i 'anthropic\|may not' LICENSE` | Stock Apache 2.0; the only match is the standard compliance clause |

## History

**2026-09-20** — [`2f45dcb729426b4b5bfca45981d52a39d3f09d0b`](https://github.com/LeandroPG19/Memorys/commit/2f45dcb729426b4b5bfca45981d52a39d3f09d0b) — first reading, at 402 files. Screened before reading: one auto-run surface, one build-time execution point, one unpinned surface and nothing inside the seven-day cooldown; the screen also flagged an `AGENTS.md` carrying instructions addressed to a reading agent, which was treated as data. Nothing was installed and nothing was run, so the benchmark figures in section 10 are the project's own account of its own correction rather than a re-measurement. Apache 2.0. Three marks: `trust_state`, `scope_enforced`, `negative_eval`. `audit_log` and `bitemporal` are both withheld over well-built machinery with no live path into it, and each withholding rests on a search recorded in the appendix. The project was called cuba-memorys and the `cuba_*` tool names still carry that; the atlas had no report under either name before this one.

---
title: "anatid"
eyebrow: "A test parses every module and fails when a tenant or time predicate is written by hand"
description: "A DuckDB memory whose tenant and bitemporal predicates are compiled in one module, whose accelerators may only narrow a candidate set, and whose erasure chases the copies of a memory that live outside the memory graph."
root: ../..
page_kind: system
source_name: "thedatasense/anatid"
source_url: https://github.com/thedatasense/anatid
archive_name: "thedatasense--anatid"
revision: aa7edcdfb5fe220f855c6c74943f7090b561854b
revision_url: https://github.com/thedatasense/anatid/commit/aa7edcdfb5fe220f855c6c74943f7090b561854b
analyzed_at: 2026-09-16
capabilities: "bitemporal, scope_enforced, audit_log, negative_eval"
capability_evidence:
  scope_enforced: "the tenant predicate is compiled in one module, and a test refuses to let any other module write one | src/anatid/visibility.py:1-9, tests/test_visibility.py:37-53, :122-140 | the module states its own reason for existing: DuckDB \"has no `AS OF SYSTEM TIME` and no row-level access control\", so tenant scoping is \"predicates anatid compiles into every read, and a read that forgets one of them returns another tenant's rows\". Every read in `recall`, `csr`, `verbs` and `database` obtains the predicate from `Visibility` rather than writing it, and the enforcement is mechanical rather than cultural: `test_no_module_writes_the_visibility_predicate_by_hand` walks each module's AST, extracts its string literals with docstrings excluded and f-strings and implicit concatenation handled, and fails when a literal that begins like a SQL statement also contains `tenant_id = ?`. It is parameterised one test per module \"so a failure names the file\". That converts the scope-predicate drift this atlas keeps finding from a review problem into a build failure | tests/test_core.py:411 asserts a second tenant's two-hop recall returns the empty list against a populated graph in the same file, and tests/test_core.py:866 pins that scoped tenants share one file and are separated only by the filter"
  bitemporal: "two axes, half-open intervals, immutable versions, and a rule about what an index is allowed to answer | src/anatid/visibility.py:11-50 | a row is visible to `Visibility(tenant_id, valid_at, tx_at)` when the tenant matches, when valid time holds — `valid_at` is `None` and `valid_to IS NULL`, or `valid_from <= valid_at < valid_to` — and when transaction time holds, `tx_at` is `None` and `tx_to IS NULL`, or `tx_from <= tx_at < tx_to`. Intervals are half-open, stated explicitly: \"a row closed exactly at T is already invisible at T, and a row opened exactly at T is already visible.\" Corrections never rewrite: a supersede, soft forget, unrelate or confidence-changing reinforce closes the current version's `tx_to` and inserts the next version in the same transaction, so at most one version of a logical id is selected for any pair of instants. The module works the question through — \"[a]sking what the database believed on Jan 2 about Jan 4, after a forget on Jan 3, returns the open-ended version 1; asking on Jan 4 returns nothing\" — and names what is *not* bitemporal: `access_count` and `last_access_at` are bumped in place on the live version | the derived-index rule is the part worth copying: \"[a]n index built over current state cannot answer what was visible at an earlier instant, so an accelerator only ever narrows the candidate set\", after which candidates are refiltered with the same predicate or with `Visibility.admits`"
  audit_log: "an audit table written in the mutation's transaction, with the counterpart id in a column precisely so erasure can find it | src/anatid/schema.py:1170-1179, src/anatid/verbs.py:1645-1653, :1833-1837, src/anatid/visibility.py:28-34 | `anatid_audit` carries tenant, memory id, a related memory id, an action, a reason, a writer and a timestamp, and the supersede and soft-forget paths insert into it inside the same statement sequence as the mutation. Beside it the version chain is itself the append-only record: every correction inserts a new immutable version carrying its own `tx_from` and `writer` rather than overwriting the row it corrects, so who changed what and when is reconstructable from the table the memory lives in. The detail to take is a comment on the supersede insert: \"[t]he counterpart id goes in a COLUMN, never into `reason`: forget(hard=True) has to be able to find and delete every audit row that names an erased memory, and it cannot search free text for it\" — an audit schema shaped by the erasure it has to survive | src/anatid/erasure.py:1-22 extends that concern outside the memory graph, to transcripts and serialised run states that hold copies of the same text"
  negative_eval: "hop-boundary and tenant-boundary assertions in one test, each kept honest by the other | tests/test_core.py:397-412, :866 | `test_recall_2hop_walks_two_hops_and_respects_the_tenant` builds a chain of relations three hops deep, then asserts that the two-hop recall contains the near memory and does **not** contain the far one, then asserts that asking for three hops does return the far memory. The third assertion is what makes the second non-vacuous: the far memory is reachable and was excluded by the hop limit rather than being absent from the graph. The same test closes with the scope case — a different tenant's two-hop recall over the same populated file returns the empty list. That is a must-not-retrieve assertion on a store, with its positive control in the same function | tests/test_conflicts.py:333 and :490 add the update and current-ids cases, asserting that an id belonging to another tenant is not found rather than silently acted on"
stack_storage: "duckdb"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "An immutable memory version — content, kind, confidence, embedding, writer — addressed by a logical id, with entity and relation edges and an episode beside it"
  storage: "One DuckDB file holding memories, edges, episodes, audit rows, a BM25 index and the bundled integration tables, queryable with SQL by anyone who opens it"
  retrieval: "Reference walks over the entity graph, BM25 text ranking and optional vector search, each narrowing a candidate set that is then filtered by the visibility predicate"
  write: "Verbs — remember, relate, supersede, reinforce, forget, unrelate — each inserting a new version rather than editing the row it corrects"
  update_delete: "A correction closes the current version's transaction interval and inserts the next in the same transaction; `forget(hard=True)` is a right-to-erasure purge that also runs registered hooks over tables anatid does not own"
  scoping: "`tenant_id` compiled into every read from one module, with a test that fails the build when any other module writes the predicate by hand"
  integration: "A Python library, an MCP server, and bundled agent integrations whose tables are covered by the erasure hooks"
  background: "Index generations and a journal, with derived accelerators constrained to narrowing rather than answering"
  trust: "Provenance through a writer on every version, an audit table with typed counterparts, and erasure that reaches transcripts and serialised state"
  strengths: "The enforcement mechanism is the thing to take. Most systems in this corpus hold their scope predicate by convention, and the atlas keeps finding the read path that forgot it. anatid puts the predicate in one module and then writes `test_no_module_writes_the_visibility_predicate_by_hand`, which parses every module's AST, pulls its string literals with docstrings excluded and f-strings handled, and fails when a literal that starts like SQL also matches `tenant_id\\s*=\\s*(\\?|\\{)` — one parameterised test per module \"so a failure names the file\". The same discipline shows in two smaller rules. An accelerator \"only ever narrows the candidate set\", because \"[a]n index built over current state cannot answer what was visible at an earlier instant\", so a stale index can cost recall and can never leak a row past the guard. And the audit schema is shaped by erasure: the counterpart memory id \"goes in a COLUMN, never into `reason`\", because a hard forget \"has to be able to find and delete every audit row that names an erased memory, and it cannot search free text for it\". `erasure.py` then chases the copies that live outside the memory graph entirely — transcripts, serialised run states — and covers integration tables that are \"counters today\" so that \"a column added later cannot quietly reopen the hole\""
  risks: "There is no epistemic status: a memory is current or superseded, and the axis that decides is time rather than a judgement, so a claim nobody has verified and one a reviewer confirmed are indistinguishable at read time beyond a confidence number. Nothing is keyed on a rejected value — a hard forget removes every copy it can reach, and re-asserting the same content afterwards produces an ordinary new memory with nothing recording that the store was once asked to erase it. The erasure hooks are the honest version of a hard problem and they are still hooks: coverage of a table anatid has never heard of depends on whoever created it registering one, and the module says so. The usage counters are excluded from the bitemporal rule by design and are mutated in place, so an older version keeps the counts it had when it closed rather than the ones the memory has now. And DuckDB is a single-writer analytical file, which is what makes the SQL-queryable promise real and also what bounds the concurrency this can serve"
---

## 1. Executive Summary

anatid is "[l]ocal memory for artificial intelligence (AI) agents. Keep the
source behind a claim and the history of each correction in one DuckDB file." —
MIT, Python, version 0.4.3, 36,813 lines across 44 files.

Its framing example is a medical-device lot whose final test passes, is then
withdrawn because the fixture loaded the wrong firmware, and is scheduled for a
replacement test. The question the store exists to answer is the one that
example makes unavoidable: not just what is true now, but "what the reviewer
knew at the time".

**The mechanism to take away is how it stops a read path from forgetting the
predicate.** DuckDB "has no `AS OF SYSTEM TIME` and no row-level access
control", so both tenant scoping and time travel are predicates the library
compiles into every read — and a read that omits one "returns another tenant's
rows or a row that was not visible at the requested instant." Every system in
this corpus with that arrangement relies on reviewers to catch the query that
skipped it. anatid relies on a test:

> "`tests/test_visibility.py` scans the source tree for the literal fragments
> and fails when one appears anywhere outside this file."

`test_no_module_writes_the_visibility_predicate_by_hand` parses each module's
AST, extracts its string literals with docstrings excluded and f-strings and
implicit concatenation handled, and fails when a literal that begins like a SQL
statement also contains a hand-written tenant predicate — parameterised one test
per module "so a failure names the file." The atlas has a recurring finding
about scope predicates drifting out of one read path; this is the first system
read here that turns that into a build failure.

**The bitemporal rule is stated once and worked through.** A row is visible to
`Visibility(tenant_id, valid_at, tx_at)` when the tenant matches and both
intervals contain their instant, half-open so that "a row closed exactly at T is
already invisible at T". Corrections never rewrite: they close the current
version's `tx_to` and insert the next version in the same transaction. The
docstring then answers the question the design is for — "[a]sking what the
database believed on Jan 2 about Jan 4, after a forget on Jan 3, returns the
open-ended version 1; asking on Jan 4 returns nothing" — and immediately names
what the rule does not cover: the usage counters are bumped in place and are not
bitemporal.

**A third rule protects the whole arrangement from its own accelerators.**

> "An index built over current state cannot answer what was visible at an
> earlier instant, so an accelerator only ever narrows the candidate set."

Candidates are then refiltered with the same predicate. A stale index can cost
recall; it cannot leak a row past the guard.

**And the audit schema is shaped by the erasure it has to survive.** On the
supersede path, the counterpart memory id "goes in a COLUMN, never into
`reason`", because a hard forget "has to be able to find and delete every audit
row that names an erased memory, and it cannot search free text for it."
[Verimem](../verimem/), read just before this, reaches the same concern from the
other direction — it keeps content *out* of its immutable chain so erasure stays
possible. Both are designing the audit around the deletion rather than
discovering the conflict later.

## 2. Mental Model

A **memory** is a logical id with immutable versions behind it.

A **correction** closes one version's transaction interval and opens the next.

A **predicate** lives in one module, and a test says so.

An **index** narrows; it never decides.

An **erasure** has to reach the transcript too.

```mermaid
%% caption: one module compiles the tenant and bitemporal predicates into every read, a test fails the build if any other module writes one by hand, accelerators may only narrow a candidate set, and erasure reaches copies outside the memory graph
flowchart TB
    V["Visibility(tenant_id, valid_at, tx_at)"] --> RULE["tenant_id matches<br/>valid_from at-or-before valid_at, before valid_to<br/>tx_from at-or-before tx_at, before tx_to<br/>intervals half-open"]
    RULE --> READS["every read in recall, csr, verbs, database<br/>obtains the predicate from here"]
    TEST["test_no_module_writes_the_visibility_predicate_by_hand"] -.->|"parses each module's AST, pulls its string literals<br/>(docstrings excluded, f-strings handled), and fails when<br/>a SQL-shaped literal contains a hand-written predicate —<br/>one test per module so a failure names the file"| READS
    W["remember · relate · supersede ·<br/>reinforce · forget · unrelate"] --> VER["a correction never rewrites:<br/>close this version's tx_to, insert the next,<br/>same transaction"]
    VER --> T[("memories · edges_about · edges_relates —<br/>immutable versions of one logical id")]
    VER --> AUD[("anatid_audit: tenant · memory_id ·<br/>related_memory_id · action · reason ·<br/>writer · happened_at")]
    AUD -.->|"'the counterpart id goes in a COLUMN, never into reason:<br/>forget(hard=True) has to be able to find and delete every<br/>audit row that names an erased memory, and it cannot<br/>search free text for it'"| SHAPE["the audit schema is shaped by the erasure"]
    T --> IDX["BM25 · vector · graph accelerators"]
    IDX -.->|"'an index built over current state cannot answer<br/>what was visible at an earlier instant, so an<br/>accelerator only ever narrows the candidate set'"| NARROW["candidates are refiltered by the predicate"]
    NARROW --> READS
    READS --> OUT["at most one version per logical id<br/>for any (valid_at, tx_at)"]
    OUT -.->|"'asking what the database believed on Jan 2 about Jan 4,<br/>after a forget on Jan 3, returns the open-ended version 1;<br/>asking on Jan 4 returns nothing'"| WORKED["the question the design exists for"]
    COUNT["access_count · last_access_at"] -.->|"bumped in place on the live version —<br/>declared NOT bitemporal"| OUT
    HARD["forget(memory_id, hard=True)"] --> GRAPH["the memory graph anatid owns"]
    HARD --> HOOKS["registered TableErasureHooks"]
    HOOKS -.->|"agent_messages, agent_run_states and the rest hold<br/>copies of the text; counters today are covered too so<br/>'a column added later cannot quietly reopen the hole'"| RESIDUE["the copies outside the graph"]
    HOOKS -.->|"a table anatid has never heard of is covered<br/>only if whoever created it registered a hook"| LIMIT["the honest limit of the mechanism"]
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `src/anatid/visibility.py` | The tenant and bitemporal predicates, and the rule stated once |
| `tests/test_visibility.py` | The AST scan that keeps them there |
| `src/anatid/verbs.py` | The write verbs, versioning, and the audit inserts |
| `src/anatid/schema.py` | Tables, generated columns, and the indexes that enforce uniqueness |
| `src/anatid/erasure.py` | Hooks, and the copies of a memory outside the memory graph |
| `src/anatid/csr.py`, `fts.py`, `vector.py` | Accelerators that narrow rather than answer |

## 4. Essential Implementation Paths

`src/anatid/visibility.py:1-9` — why the predicates exist and where they are
allowed to live.

`tests/test_visibility.py:122-140` — the test that turns a convention into a
build failure.

`src/anatid/visibility.py:28-34` — versioning, and the worked bitemporal
question.

`src/anatid/visibility.py:45-50` — what an accelerator is allowed to do.

`src/anatid/verbs.py:1645-1653` — a comment that explains a column by naming the
delete it has to survive.

`src/anatid/erasure.py:1-22` — the residue problem, stated as a table.

## 5. Memory Data Model

Memories, `edges_about` and `edges_relates` are immutable versions of logical
ids, each carrying tenant, both time intervals, a writer, a confidence and
optionally an embedding. Entities carry a generated `entity_key` whose
uniqueness is enforced by an index rather than by a select-then-insert in the
verbs. `anatid_audit` records actions with typed counterparts. Everything sits
in one DuckDB file that SQL can read directly.

## 6. Retrieval Mechanics

Reference walks over the entity graph, BM25 ranking over text, and vector search
when an embedding model is configured. Each is a candidate generator; the
visibility predicate decides.

## 7. Write Mechanics

Six verbs, each producing a new version rather than an edit, with the audit row
and the version insert in the same transaction. `forget` is soft by default and
purges with `hard=True`, running registered erasure hooks over tables outside
anatid's own schema.

## 8. Agent Integration

A Python library, an MCP server, and bundled agent integrations — messages, run
states, sessions, turn usage — whose tables are explicitly enumerated in the
erasure module rather than left to be discovered.

## 9. Reliability, Safety, and Trust

The strong parts are the single predicate with mechanical enforcement, the
narrowing rule for accelerators, the typed audit counterpart, and an erasure
design that starts from where copies actually end up. The gaps are the absence
of any epistemic status beyond time, nothing keyed on an erased value, and hooks
that cover unknown tables only when somebody registers them.

## 10. Tests, Evals, and Benchmarks

A test suite that includes the source-scanning visibility test, tenant-boundary
and hop-boundary assertions with their controls in the same function, pool
isolation, backup quiescing, and conflict cases asserting that an id belonging
to another tenant is not found rather than silently acted on.

## 11. For Your Own Build

Put your scope and time predicates in one module, then write the test that fails
the build when a literal elsewhere contains one. The review that catches it by
eye works until the day it does not.

Let your indexes narrow and never decide. It is the difference between a stale
index costing recall and a stale index disclosing a row.

Shape the audit schema around the delete. If a hard erasure has to find every
row naming a memory, the id belongs in a column, not in a sentence.

Enumerate where copies of your memory end up. The transcript and the serialised
run state are memory too, and a purge that only clears the store leaves both.

## 12. Open Questions

Whether a status axis is wanted beside the time axes. Superseded and current are
temporal facts; unverified and confirmed are not, and a manufacturing record is
exactly the domain where the difference matters.

Whether the hook mechanism should fail closed for unregistered tables. The
module is clear that hooks are the only route for tables it has never heard of,
which means an erasure can succeed while a copy survives in a table nobody
wired up.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `src/anatid/visibility.py:1-50` | One predicate, one module, and the whole rule stated once |
| `tests/test_visibility.py:122-140` | An AST scan that makes the convention mechanical |
| `src/anatid/verbs.py:1645-1653` | An audit column explained by the delete it must survive |
| `src/anatid/erasure.py:1-22` | Where copies of an erased memory actually live |
| `tests/test_core.py:397-412` | A negative assertion with its control in the same test |

## History

**2026-09-16** — [`aa7edcdfb5fe220f855c6c74943f7090b561854b`](https://github.com/thedatasense/anatid/commit/aa7edcdfb5fe220f855c6c74943f7090b561854b) — first reading, at a commit dated 10 September 2026. Screened before opening, from a shallow clone: no auto-run surfaces, two build-time execution points, two unpinned dependency surfaces and two dependency files inside the seven-day cooldown. Nothing was installed, built or run, and no DuckDB file was opened, so every claim here is read from source.

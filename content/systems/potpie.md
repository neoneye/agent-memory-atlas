---
title: "Potpie"
eyebrow: "Invalidation with a reason, and no key on the value"
description: "A context graph over a codebase and its development lifecycle, where every mutation carries provenance and an invalidation stamps valid_to rather than deleting — and the rejected value itself is not what the refusal is keyed on."
root: ../..
page_kind: system
source_name: "potpie-ai/potpie"
source_url: https://github.com/potpie-ai/potpie
archive_name: "potpie-ai--potpie"
revision: 7726221dc95c3549a26d83dad9a4b9a0b6aa5ccb
revision_url: https://github.com/potpie-ai/potpie/commit/7726221dc95c3549a26d83dad9a4b9a0b6aa5ccb
analyzed_at: 2026-09-19
capabilities: "trust_state, bitemporal, scope_enforced, audit_log, negative_eval"
stack_storage: "graph"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
capability_evidence:
  trust_state: "the claim graph — a discrete invalidation state that withholds, beside a verification field on the record | potpie/context-engine/src/potpie_context_engine/core/graph_mutations.py | `InvalidationOp` requires a `reason`, stamps `valid_to` and optionally writes a SUPERSEDES edge; `FixRecord.verification_status` defaults to `unverified` and is carried into the semantic layer, where a refuted fix becomes `failed` (record_to_semantic.py:171-229), and `VERIFICATION_OUTCOMES` is worked / didnt_work / partial | potpie/context-engine/tests/conformance/test_public_graph_runtime.py"
  bitemporal: "the claim graph — validity bounds separate from record time, queryable as of an instant | potpie/context-engine/src/potpie_context_engine/core/ports/claim_query.py | `ClaimQuery` carries an optional `as_of` datetime beside `include_invalidated`, and the mutation layer stamps `valid_from` / `valid_to` rather than deleting, with `observed_at` and `deployed_at` in the same temporal vocabulary (reconciliation_validation.py:55) | potpie/context-engine/tests/conformance/test_public_graph_runtime.py"
  scope_enforced: "every graph read — a required pot key, not an optional filter | potpie/context-engine/src/potpie_context_engine/core/graph_query.py | `pot_id: str` is a required positional on the query functions (:64, :114, :151) and on `ClaimQuery` itself, so a caller cannot omit the scope rather than merely being expected to pass it | potpie/context-engine/tests/conformance/test_public_graph_runtime.py"
  audit_log: "the mutation layer — provenance on every fact, and an append-only event verb in the vocabulary | potpie/context-engine/src/potpie_context_engine/core/graph_mutations.py | `ProvenanceRef` stamps pot, source event, mutation id, source system and kind on every entity, edge and invalidation; `SemanticMutationOp.append_event` is a first-class verb the validator refuses without a verb class (semantic_mutation_validator.py:425) | potpie/context-engine/tests/core/test_semantic_mutations.py"
  negative_eval: "recall after invalidation, as a committed conformance case | potpie/context-engine/tests/conformance/test_internal_graph_runtime.py | after a retraction the default `find_claims` returns `== []` (:328), and only `include_invalidated=True` surfaces the row, which then carries a non-null `invalid_at` (:330-334) — a must-not-appear assertion rather than a recall check | potpie/context-engine/tests/conformance/test_internal_graph_runtime.py:319"
matrix:
  memory_unit: "A typed context record — fix, bug pattern, preference, policy, decision, verification, or free-form — lowered into claims and edges in a per-pot context graph"
  storage: "A graph behind a port: FalkorDB by default with an embedded `falkordblite` option, Neo4j as an extra, and NetworkX in-process; claims, edges and invalidations all carry provenance columns"
  retrieval: "Claim queries filtered by pot, predicate, source system and time, with an optional native vector arm; invalidated claims excluded unless asked for"
  write: "An ingestion submission validated against a discriminated-union schema per record type, then lowered to semantic mutations and applied as typed graph operations"
  update_delete: "`InvalidationOp` with a required `reason` stamps `valid_to` and writes a SUPERSEDES edge from the replacement, preserving the row rather than deleting it; there is no delete verb for a claim"
  scoping: "`pot_id` is a required argument on every graph query and on the claim filter, so the scope reaches the query rather than being available to it"
  integration: "A CLI, a daemon, an MCP surface and agent bundles shipped as skills for Claude Code and other harnesses"
  background: "Reconciliation over ingested events, an LLM-planned mutation path validated before it is applied, and quality-issue creation as a typed mutation"
  trust: "A `verification_status` on a fix that starts `unverified` and can become `failed`, a separate verification record carrying worked / didnt_work / partial against an existing fix, a confidence on the provenance, and an invalidation state that withholds on read"
  strengths: "Every mutation carries provenance answering where a fact came from, when it was observed, when it was written and who produced it; an invalidation cannot be recorded without a reason; and a conformance test asserts the invalidated claim is absent by default"
  risks: "Invalidation is keyed on the entity or edge, not on the value, so re-extraction of the same claim under a new key is not refused; the approval gate guards the workbench commit path only, the reconciliation agent's plans apply through apply_mutation_batch without it, and approved_by is a caller-supplied string nothing verifies"
---

## 1. Executive Summary

Potpie is Apache-2.0, 678 Python files across twelve packages under `potpie/`,
774 commits since 12 August 2024, and it describes itself as turning a codebase and its
development lifecycle into a *living context graph* — indexing code, structure,
decisions, source history and team knowledge so an agent can answer with
project-specific context.

Most of that is a corpus index of the user's own source, which this atlas keeps
outside its boundary. What puts Potpie inside it is the other half: a typed
record layer where an agent writes claims that could later turn out to be wrong,
and a mutation layer built to take them back.

**The mechanism worth the report is that an invalidation cannot be recorded
without a reason, and does not delete anything.** `InvalidationOp`
(`graph_mutations.py:160`) takes a target entity key or edge, a **required**
`reason`, and an optional `superseded_by_key`. Its own docstring states the
contract: *"the invalidated node/edge gets valid_to stamped rather than being
deleted, preserving the audit trail"*, and when a replacement is named a
`SUPERSEDES` edge is written from the new entity to the old one. Deletion of a
claim is not in the verb set.

**Provenance is a first-class contract rather than a convention.**
`ProvenanceRef` (`:11`) is stamped on every entity, edge *and invalidation*, and
its docstring names the question it exists to answer: *"where did this come
from, when was it observed, when was it last written, how confident is it, and
who produced it"*. The confidence lives on the provenance, beside the fact,
rather than inside it.

**The read path defaults to hiding what was withdrawn.** `ClaimQuery`
(`ports/claim_query.py`) carries `include_invalidated: bool = False` and an
optional `as_of` datetime. A caller who asks for nothing in particular gets the
claims that still stand; the history is reachable and requires saying so. A
committed conformance case asserts exactly that, and it is what the negative-eval
mark rests on.

**The gap is what the refusal is keyed on.** Invalidation targets an entity key
or an edge triple. Nothing is keyed on the *value*, so a claim withdrawn once and
re-derived later under a different key is a new entity rather than a refused
write — the distinction this atlas draws between supersession and a
rejected-value tombstone. The tombstone mark is withheld on that, and the
machinery to close it is already present: the reason, the provenance and the
SUPERSEDES edge are all there, and only the key is row-shaped.

## 2. Mental Model

Two layers, and the epistemic content is in the upper one.

**The lower layer is a code graph** — files, symbols, call structure, source
history — regenerated from the repository. Nothing there is a claim; it is a
projection of something that can be recomputed, and on its own it would place
Potpie outside this atlas beside the other corpus indexes.

**The upper layer is a claim graph**, written by an agent through typed records.
`context_records.py` defines a discriminated union with six shapes and a
fallback, and the shapes are unusually specific about epistemic status:

```text
fix           symptom_signature, fix_steps, root_cause,
              verification_status = "unverified",
              attempted_failed_fixes   <- what did NOT work
bug_pattern   the symptom side of a fix
preference    prescription + code_scope + strength (hard|strong|soft)
                                        + audience (team|service|project|global)
decision      ADR-shaped: rationale + alternatives_rejected
verification  a confirm/refute against an existing fix:
                            worked | didnt_work | partial
```

Two of those fields are the interesting ones. `attempted_failed_fixes` and
`alternatives_rejected` record the road not taken — the negative half that most
stores in this corpus discard — and they are ordinary tuples on the record
rather than anything the write path consults. They are documentation of a
rejection, not a refusal of one.

`verification` is the sharper idea: a *separate record type* whose whole job is
to confirm or refute a fix that already exists. Corroboration is a write rather
than a score adjustment, and `didnt_work` is a first-class outcome.

```mermaid
%% caption: A typed record is validated, lowered to semantic mutations and applied with provenance stamped on every operation; an invalidation stamps valid_to and writes a SUPERSEDES edge instead of deleting, and the default claim query returns only what still stands.
flowchart TD
    A["agent writes a typed record"] --> V{"validate_record_payload<br/>discriminated union"}
    V -->|"unknown type"| FF["FreeFormRecord<br/>accepted, unstructured"]
    V -->|"typed"| L["lower to semantic mutations"]
    L --> M{"semantic_mutation_validator"}
    M -->|"refused"| X["error with a precise message"]
    M -->|"valid"| P["apply typed graph ops<br/>ProvenanceRef stamped on each"]
    P --> G[("claim graph<br/>per pot_id")]
    I["InvalidationOp<br/>reason REQUIRED"] --> S["stamp valid_to<br/>+ SUPERSEDES edge"]
    S --> G
    G --> Q["ClaimQuery<br/>pot_id required<br/>include_invalidated = False"]
    Q --> R["claims that still stand"]
    G -. "include_invalidated = True" .-> H["the withdrawn history"]
```

## 3. Architecture

Twelve packages under `potpie/`. `context-engine` holds the domain in its
`core` subpackage — records, ontology, mutations, queries, plans, the workbench
and the validators — beside the adapters, reconciliation and the LLM planning
path; the domain was a separate `context-core` package until #1057 (28 August
2026) absorbed it. `tests/core/test_library_isolation.py` asserts, in a
subprocess, that importing `potpie_context_engine.core` loads nothing beyond the
engine package, the standard library and pydantic, which is how the domain stays
portable across backends. `auth`, `cli`, `config`, `daemon`, `integrations`,
`parsing`, `pots`, `runtime`, `sandbox`, `setup` and `skills` sit around it.
Paths below are relative to `potpie/context-engine/src/potpie_context_engine/`
unless given in full.

The graph is behind a port. `falkordb` is the default with an embedded
`falkordblite` for a hostless run, `neo4j` is an extra, and `networkx` is
available in process — so the same claim semantics run against three very
different stores, and the domain does not know which.

## 4. Essential Implementation Paths

**The write.** A record arrives, `validate_record_payload` dispatches on
`record_type` and raises `ContextRecordValidationError` with a precise message
on bad input; the returned dataclass is attached to the submission so
downstream consumers read structured fields *"without re-parsing free text"*.
An unknown record type is not an error — it falls back to `FreeFormRecord`,
which is the pre-typing `{summary, details}` shape kept deliberately so the
agent's writes are not rejected for being ahead of the schema.

**The lowering.** `record_to_semantic.py` turns a record into semantic
mutations, carrying `verification_status` through and marking a refuted fix
`failed` (`:229`). `semantic_mutation_validator.py` then refuses malformed
operations by name — `append_event` without a verb class is rejected at `:425`.

**The invalidation.** `InvalidationOp` has four production call sites, in
`core/graph_plans.py:496` and `core/semantic_mutation_lowering.py` at `:338`,
`:347` and `:400`, plus an LLM-facing schema `LlmInvalidationOp` so a planned mutation can
propose one. It is wired, not declared.

**The read.** `graph_query.py` takes `pot_id` as a required positional at `:64`,
`:114` and `:151`. `ClaimQuery` adds predicate, source-system and time filters,
an optional native vector arm, and `include_invalidated` defaulting to `False`.

## 5. Memory Data Model

A claim carries its provenance rather than pointing at it. `ProvenanceRef`
holds `pot_id`, `source_event_id`, a generated `mutation_id`, `source_system`
and `source_kind`, with a confidence alongside. The temporal vocabulary the
reconciliation validator recognises is `valid_at`, `valid_from`, `valid_to`,
`observed_at`, `deployed_at` (`reconciliation_validation.py:55`) — five distinct
times, of which two are about the world and three about the system.

Scope is expressed twice and differently. `pot_id` is the hard boundary, applied
in the query. `PreferenceRecord.code_scope` is a soft one — a mapping of
language, framework, repo and service that *"readers intersect against task
scope at query time"* — beside a `SCOPE_KINDS` vocabulary of service,
component, feature, module, language, framework and global. The first is
enforcement; the second is relevance.

## 6. Retrieval Mechanics

Claims are filtered rather than ranked into oblivion: pot, predicate, source
system, time window, and an optional vector arm when the port supports a native
query. The default excludes invalidated claims. `as_of` makes the graph
answerable at a past instant, which is the half of bi-temporality that is
often declared and not queried.

## 7. Write Mechanics

Every write is validated twice — once against the record schema, once against
the semantic mutation contract — before anything reaches the graph. The LLM sits
on the *planning* side: `reconciliation/llm_plan_schema.py` defines what a model
may propose, including `LlmInvalidationOp`, and the validator is what decides
whether the proposal is applied. A model can propose a withdrawal; it cannot
perform one without passing the same gate as any other mutation.

**A named approver gates the riskier plans on the workbench path.** A harness
working the graph directly proposes a plan (`potpie --json graph propose --file`),
and
`validate_semantic_plan` grades every operation: appends, entity upserts and
ordinary claims are low risk; retractions, entity patches, state transitions and
claims marked `user_decision` are medium; supersessions and merges are high (`core/semantic_mutation_validator.py:743`).
`commit` (`core/workbench_service.py:291`) runs `_approval_error` (`:3358`): a
plan carrying operations from `REVIEW_REQUIRED_OPS` would be refused outright —
*"the local commit path does not apply [them] yet"* — though that set is empty at
this pin; and with
`require_approval_for_review` on — the default in `core/mutation_policy.py` — a
medium- or high-risk plan refuses until `--approved-by <user-ref>` is passed,
whereupon a `GraphMutationApproval` with the approver and time is written to the
plan record. `test_medium_risk_plan_requires_approval_before_commit` asserts
the refusal, the commit with `user:alice`, and the recorded approval. Two
limits, and together they are why this report does not carry `human_review`.
`approved_by` is whatever string the caller supplies — the parameter is
`approved_by: str | None` at `core/workbench_service.py:296` and nothing verifies
it — so an agent can name itself. And the reconciliation agent does not use this
path at all: its plans go through `apply_mutation_batch`
(`adapters/outbound/graph/apply_plan.py:103`), whose signature takes a writer, a
plan, a pot id, a provenance context, a definition and a reconciliation config,
and no approver or policy of any kind. A gate one producer can satisfy by
writing its own name, and another can walk around, is a shape check rather than
an actor check. What remains is still worth copying — the risk grading is
per-operation and checkable, and the refusal is tested — but it grades the
*change*, not the *changer*.

## 8. Agent Integration

A CLI, a daemon, an MCP surface, and agent bundles shipped as skills —
`potpie/cli/templates/agent_bundle/.agents/skills/` and a Claude Code plugin
directory beside it. The integration ships the *instructions* for using the
graph, not only the graph.

## 9. Reliability, Safety, and Trust

**What is strong.** An invalidation cannot be recorded without a reason. A
withdrawal preserves the row. Provenance is stamped on the invalidation itself,
so the record of a retraction says who retracted it and from what event. The
scope key is required rather than defaulted, which is the difference between a
boundary a caller must pass and one they must remember.

**What is missing.** Nothing is keyed on the value, so the refusal of a rejected
claim depends on the next writer using the same entity key. A system this careful
about *recording* a withdrawal has not yet made the withdrawal *bind*. The
approval gate in section 7 is the review surface, and it covers half the write
paths: a harness committing a workbench plan must name an approver for a
retraction or a supersession, while the reconciliation agent's LLM-planned
mutations apply once they pass the shape validator, with no person between the
plan and the graph.

## 10. Tests, Evals, and Benchmarks

147 test files under `potpie/`, split across core, unit, conformance and
integration. The conformance suite is the one that matters here:
`test_internal_graph_runtime.py` drives the runtime against a backend and
asserts, after a retraction, that the default claim query returns `== []` and
that `include_invalidated=True` returns exactly one row carrying a non-null
`invalid_at` (`test_public_runtime_retracts_extension_predicate`, `:319-334`). That is a
must-not-appear assertion against the real read path rather than a helper, and
it is what the negative-eval mark rests on. `test_graph_workbench_plans.py`
carries the approval cases: a medium-risk plan blocked, then committed with a
named approver, and an entity patch that requires approval before it updates
metadata.

`benchmarks/retrieval_eval.py` exists in the engine package. No committed
results were found for it, and none is claimed. I did not run the suite.

## 11. Patterns Worth Stealing

- **Require the reason on the withdrawal, not on the write.** `InvalidationOp`
  cannot be constructed without one. A reason left optional is a retraction
  nobody can explain later.
- **Stamp provenance on the invalidation too.** A retraction is a claim about a
  claim, and it has a source and an author like any other.
- **Make the scope key a required positional.** `pot_id` cannot be omitted; a
  defaulted scope is a widening hazard one refactor away.
- **Model corroboration as a record, not a score.** A `verification` write
  carrying `worked | didnt_work | partial` against an existing fix is auditable
  in a way that a confidence increment is not.
- **Grade each operation's risk and gate the commit on it.** Appends go through;
  retractions, supersessions and merges wait for a named approver, and the
  approval is written onto the plan. Put the approver behind authentication and
  put every write path through the same gate, which Potpie has not yet done.
- **Keep a free-form fallback so the schema does not reject the future.**
  `FreeFormRecord` accepts what the typed union does not yet model, which is how
  a discriminated union stays adoptable.

## 12. Open Questions

- **Would a value-keyed refusal fit?** The reason, the provenance and the
  SUPERSEDES edge already exist. What is missing is a digest of the normalised
  claim and a check on the write path.
- **Should the reconciliation agent's plans pass the workbench approval gate?**
  The validator grades their risk and checks their shape; nothing holds a
  high-risk reconciliation plan for a person.
- **Does `attempted_failed_fixes` reach retrieval?** It is stored on the record;
  no consumer was traced.
- **What do the retrieval benchmarks score?** The harness is present and no
  result is committed.

## Appendix: File Index

| Path | What it holds |
| --- | --- |
| `potpie/context-engine/src/potpie_context_engine/core/context_records.py` | The six typed record shapes, their vocabularies, and the validator |
| `potpie/context-engine/src/potpie_context_engine/core/graph_mutations.py` | `ProvenanceRef`, `InvalidationOp`, and the typed graph operations |
| `potpie/context-engine/src/potpie_context_engine/core/graph_query.py` | Query functions with `pot_id` required |
| `potpie/context-engine/src/potpie_context_engine/core/ports/claim_query.py` | `ClaimQuery` — `include_invalidated`, `as_of`, vector arm |
| `potpie/context-engine/src/potpie_context_engine/core/record_to_semantic.py` | Record to semantic mutation, carrying `verification_status` |
| `potpie/context-engine/src/potpie_context_engine/core/semantic_mutation_validator.py` | The refusals by name, and `_op_risk` |
| `potpie/context-engine/src/potpie_context_engine/core/workbench_service.py` | `propose`, `commit` and `_approval_error` |
| `potpie/context-engine/src/potpie_context_engine/core/mutation_policy.py` | `require_approval_for_review`, on by default |
| `potpie/context-engine/.../reconciliation/llm_plan_schema.py` | What a model may propose, including an invalidation |
| `potpie/context-engine/tests/conformance/test_internal_graph_runtime.py` | The invalidated-claim-is-absent assertion |
| `potpie/context-engine/tests/unit/test_graph_workbench_plans.py` | The approval-before-commit cases |
| `potpie/context-engine/tests/core/test_library_isolation.py` | The core imports only the engine package, stdlib and pydantic |

## History

**2026-09-19** — re-pinned to [`7726221dc95c3549a26d83dad9a4b9a0b6aa5ccb`](https://github.com/potpie-ai/potpie/commit/7726221dc95c3549a26d83dad9a4b9a0b6aa5ccb), 2 commits on and none of the eighteen changed files under `potpie/context-engine/`, so the five remaining marks keep their anchors untouched. `human_review` is **withdrawn**, on the two limits the previous record already stated beside it rather than on anything new: `approved_by` is declared `str | None` and nothing verifies it, so the producer can name itself; and `apply_mutation_batch`, the path the reconciliation agent's plans take, has no approver or policy parameter at all. A gate one producer satisfies by writing its own name and another walks around grades the change rather than the changer. The per-operation risk grading and its tested refusal keep their credit in section 7. Screened again first; nothing was installed and no suite was run.

**2026-09-15** — [`0b18cea8dcd984bd70d9d7d85cd340ceab87dd94`](https://github.com/potpie-ai/potpie/commit/0b18cea8dcd984bd70d9d7d85cd340ceab87dd94) — ten commits on, 2026-09-15. Screened before reading: no auto-run surface, six build-time execution points (a `Makefile` and five `conftest.py` files that run on test collection), three unpinned surfaces and six dependency surfaces inside the cooldown. Nothing was installed and no test was run. #1057 (28 August) absorbed `context-core` into `context-engine` as its `core` subpackage and renamed the public-runtime conformance file; the invalidation, provenance, claim query, required `pot_id` and verification mechanics are unchanged in substance, and the evidence records point at the new paths. `results.md` is no longer at the root. `human_review` added: the workbench commit path, present at the first reading, refuses medium- and high-risk plans until a named approver is given and records the approval, with a committed test; the approver is unauthenticated and the reconciliation agent's plans bypass the gate, which the report now says in section 7. Six marks.

**2026-08-19** — [`a341978880b9d4c1b403831931279ccedf6184ae`](https://github.com/potpie-ai/potpie/commit/a341978880b9d4c1b403831931279ccedf6184ae) — first reading. The screen reported no auto-run file, six manifests inside the seven-day cooldown, a `Makefile` and three `conftest.py` executing on collection; nothing was installed and no test was run, so the conformance assertions were read rather than executed. `InvalidationOp`'s four production call sites and the `include_invalidated` default were traced by hand rather than taken from the docstrings, and the tombstone mark was withheld after checking that the invalidation target is an entity key or edge triple and never the claim value.

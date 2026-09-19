---
title: "RE-call"
eyebrow: "The off-topic pool had to be moved out of Python, because the code corpus was ingesting it"
description: "Agent memory on PostgreSQL with pgvector where every hit carries one of eleven verdicts, strict mode refuses instead of answering, erasure writes a permanent tombstone the builder re-checks, and 162 dated preregistrations record what was going to be measured before it was."
root: ../..
page_kind: system
source_name: "GiulioDER/RE-call"
source_url: https://github.com/GiulioDER/RE-call
archive_name: "GiulioDER--RE-call"
revision: 1157360f1e0704a06548d93a4f4797c415c722f9
revision_url: https://github.com/GiulioDER/RE-call/commit/1157360f1e0704a06548d93a4f4797c415c722f9
analyzed_at: 2026-09-19
capabilities: "tombstone, trust_state, bitemporal, scope_enforced, audit_log, human_review, negative_eval"
capability_evidence:
  tombstone: "a permanent per-source tombstone the builder re-checks inside the ingest it already holds | recall/migrations/sql/0008_generation_foundation.sql:104-112, recall/generations.py:566-570, :810, :976, :1005, recall/generation_store.py:52-58 | `recall_source_tombstones` is keyed `(tenant_id, source_uri)` — on the identity of the erased content, not on a row id — and it references the `source_forgotten` audit event that created it by foreign key, so an erasure cannot exist without its record. `_is_tombstoned` is consulted at three separate points in the build, not once at the top, and the module comment says why: a tombstone \"is permanent and bars that URI from every future build\", and an erasure arriving mid-ingest would otherwise land after the check that would have caught it, so \"the build then indexed the content the user asked to erase\". The re-check closes that window. A URI that no successful build ever named is still refused as a typo, because forgetting it writes a permanent tombstone | tests/ carries the generation-lifecycle suite, and the effective corpus fingerprint is computed from the manifest minus the tombstoned set, so a build whose only change is an erasure is still a distinct generation"
  trust_state: "eleven discrete verdicts, only one of which becomes evidence, and strict mode raises rather than answering | recall/types.py:55-81, recall/evidence.py:346, recall/trust.py:873, :975 | `Verdict` is a closed vocabulary — `ok`, `superseded`, `expired`, `not_yet_valid`, `not_yet_known`, `low_confidence`, `invalid_metadata`, `ambiguous_supersession`, `not_entailed`, `unverified`, `dependency_invalidated` — and each non-`ok` value is documented with why it is not its neighbour. `unverified` \"is not a weaker `ok`: it says the trust gate never ran\", kept apart from `low_confidence` so that \"we measured this and it scored badly\" stays distinguishable from \"nobody measured anything\". `ambiguous_supersession` \"fails closed rather than being served with a guessed successor\". The verdict is what withholds: every evidence path filters to `hit.verdict == \"ok\"`, so a superseded claim stays readable and never becomes the answer, and under a strict policy a failed gate raises `TrustRefusal` — including through a deliberate broad catch annotated `# BROAD-CATCH: fail-closed` that turns any dependency failure into a refusal | recall/eval/locomo_abstention.py scores the abstention axis, and docs/preregistrations/2026-08-22-atm-abstention-relative-criterion.md and 2026-08-23-benchd-abstention-threshold.md record the criteria before the runs"
  bitemporal: "two axes that compose, with supersession rewound on the transaction axis too | recall/trust.py:520-544, recall/types.py:60-63 | the function's own docstring states the split: `now` is valid time and drives `expired` and `not_yet_valid` from the memory's declared `valid_from`/`valid_until`; `known_as_of` is transaction time and drives `not_yet_known` from the store's index time, answering \"what did we know at that moment, rather than what was true\". They compose — `evaluate(..., now=june, known_as_of=tuesday)` asks what was believed on Tuesday about the world in June. Two details raise it above a schema with four columns. Supersession edges are rewound as well, since \"[a]n edge becomes assertable when the superseding document is written, so its `indexed_at` dates the edge\", making a replay honest about which memories were current and not only which existed. And the axis reads `first_indexed_at` rather than `indexed_at`, because using the last write \"claimed a memo edited today had never existed before the edit, so every replay of an earlier instant reported an empty store\" — a bug found, fixed, and left written down | docs/preregistrations/2026-09-10-temporal-supersession-traversal.md, and `evaluate` is pure with no DB access or clock reads, so the axes are testable without a database"
  scope_enforced: "tenant isolation as a forced Postgres row-level-security policy on the chunk table itself | recall/migrations/sql/0008_generation_foundation.sql:114-144, recall/fact_ledger.py:1-6 | `recall_chunks_v1` — the memory rows — carries `ENABLE ROW LEVEL SECURITY` followed by `FORCE ROW LEVEL SECURITY`, with a policy of `tenant_id = current_setting(<tenant GUC>)` in both `USING` and `WITH CHECK`. The key is stored on the row and applied by the database rather than by a predicate the application remembers to add, `FORCE` means the table owner is subject to it too, and the same treatment covers generations, tenant state, ingest jobs and the audit events. A caller cannot omit it, because there is no query path that reaches the rows without the session GUC set. The fact ledger reuses the same GUC and policies rather than inventing a second scheme | the folder and facet `Scope` is a separate, caller-supplied retrieval dimension and is not this mark; it is documented as refusing a facet filter against a corpus with no facet rows rather than returning an empty result \"that reads like no match\""
  audit_log: "generation-lifecycle events written inside the build transaction, not beside it | recall/generations.py:361-380, :492, :1083, :1122, :1151, :1268, :1345, :1399, :1441, :1544, :1706, recall/store.py:1486-1530 | `_audit` appends to `recall_audit_events` on the same connection as the build, so the record commits or rolls back with the mutation it describes. The vocabulary covers the memory lifecycle rather than a corner of it: `generation_created`, `generation_built`, `generation_failed`, `generation_abandoned`, `generation_validated`, `generation_graph_rebuilt`, `generation_promoted_unsafe_development`, `generation_rolled_back`, `generation_gc`, `source_forgotten` and `calibration_invalidated`. Each row carries tenant, actor, generation, source URI and a JSON payload, the table is RLS-isolated, and the tombstone table holds a foreign key into it. The separate `DecisionLedger` is explicitly *not* this: it records retrieval decisions, is off by default, and is best-effort by design — \"[t]he one thing a witness must not do is become load-bearing\" | recall/decision_ledger.py:1-32 draws the line between the two in its own module docstring"
  human_review: "a review gate the type system enforces, refusing without a reviewer, a timestamp and a note — and deliberately absent from the surface the model holds | recall/promotion.py:99-111, :200-210, recall/cli_commands/extract_rewrite.py:398-400, recall/rewrite.py:26, recall_mcp/server.py:1942-1949, :1578-1582 | an extracted proposal moves through `proposed → reviewed → accepted → promoted`, and `review_proposal` calls `_require_review_fields`, which raises unless a non-blank reviewer identity, a review timestamp and a non-blank audit note are all present. The gate is structural rather than conventional: downstream functions cannot accept an unreviewed proposal because they take a `PromotedFact`, and \"only `promote_accepted_proposal` produces one\". What settles the producer test is the MCP server, which registers `recall_rewrite_plan` and no apply twin, with the reason in its own docstring — *\"There is deliberately no `recall_rewrite_apply`. The MCP client is the model, so letting it supply a reviewer id and an audit note would make the named human gate a formality it satisfies by typing a string: the gate becomes a field, not a person.\"* The one fact-writing tool, `recall_apply_fact`, states the same rule as a property of its inputs: trust verdicts, timestamps, approval fields and writer identity are *\"server-owned and cannot be supplied here\"*. The limit worth stating is that `reviewer_id` remains a supplied string on the CLI path: it records who claims to have reviewed, not who authenticated | the promotion suite, and the MCP tool list itself, where the apply verb is absent by construction"
  negative_eval: "a committed distractor set and an off-topic pool, with the pool guarded against the repository ingesting it | recall/eval/near_miss.json, recall/eval/offtopic_subjects.json, recall/eval/synthetic.py:75-100, tests/test_wizard_queryset.py:244-256 | `near_miss.json` pairs each query with explicit `distractor_ids` — the documents that must not be the answer — and `offtopic_subjects.json` holds a pool of subjects that must produce abstention. The hygiene around the pool is the part to read. The subjects live in JSON rather than as Python literals because as literals they were also corpus: a code corpus rooted at this repository ingested the list and then disqualified every subject in it, measured on 18 August 2026 as none of twenty-five surviving, against eleven of twenty-five for an unaffected third-party corpus of the same size, so \"the failure was recall dogfooding itself, not the pool being too small\". The distinctive words are deliberately never named in prose, because naming one \"puts it back into every code corpus rooted at this repository and silently disqualifies its subject\" — which the author reports doing twice while writing the fix, once caught only because a survivor count moved the wrong way. Three committed guards hold it, and a corpus that collides with the pool is refused rather than silently narrowed, since \"duplicate gap queries understate the variance of any rate measured on them\" | tests/test_eval_synthetic.py holds the three guards, and tests/test_wizard_queryset.py:244 asserts the refusal"
stack_storage: "postgres"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A source document chunked and indexed, carrying declared validity, lineage and supersession; beside it an `AtomicFact` — namespace, subject, predicate, object, context, `valid_from`, `valid_until` — promoted through a review gate into an append-only fact ledger"
  storage: "The caller's own PostgreSQL with pgvector, every memory table under forced row-level security keyed on a tenant GUC; generations, audit events, tombstones, calibrations and the fact ledger share the scheme"
  retrieval: "Dense, sparse and graph legs fused, reranked, then judged: each hit returns a verdict, a score and provenance, and only `ok` hits become evidence"
  write: "Generation builds from a manifest, an MCP write path, harness hooks, and a promotion pipeline that turns extracted proposals into facts only after a named review"
  update_delete: "Declared supersession makes the current memory outrank a stale but similar one; `forget()` writes a permanent per-source tombstone that every future build re-checks"
  scoping: "Tenant isolation is forced row-level security in Postgres, not an application predicate; folder and facet scope is a separate caller-supplied retrieval dimension over the same rows"
  integration: "A CLI, an MCP server, a Codex plugin, Claude Code hooks, a desktop packaging path and Docker compose files"
  background: "Generation builds, graph rebuilds, calibration fitting and invalidation, dependency invalidation, and a garbage collector over superseded generations"
  trust: "A closed eleven-value verdict vocabulary, calibrated thresholds with a certification status, strict mode that refuses rather than answers, a degraded mode with a verdict of its own so it cannot be mistaken for a judged result"
  strengths: "The evaluation discipline is what makes this repository unusual. `docs/preregistrations/` holds 162 dated markdown documents running from mid-August to mid-September 2026, beside the query-set JSON files several of them cite, each stating what was going to be measured before it was, with amendments filed as separate dated files and results as separate `-result.md` documents, so a hypothesis and its outcome cannot be quietly reconciled after the fact. The negative-set story is the one to read in full: the off-topic pool lives in JSON rather than Python because as literals the subjects were also corpus, the contamination was measured rather than assumed (none of twenty-five subjects surviving against eleven for an uncontaminated corpus of the same size), the distinctive words are never named in prose because naming one re-contaminates the pool, and three committed guards hold all of it — a project that has understood that its own tree is part of the test environment. Beside that, the verdict vocabulary is argued rather than listed: `unverified` exists so that a degraded hit cannot pass as a judged one, since reusing `low_confidence` \"would have made 'we measured this and it scored badly' indistinguishable from 'nobody measured anything'\""
  risks: "Licence first, because it changed at 0.14.0: PolyForm Noncommercial 1.0.0 for this release and later, Apache-2.0 for 0.13.x and earlier, with commercial production, a hosted service and redistribution all needing a separate written licence. Then size and operational weight: 103,088 lines of Python over 254 modules with 518 test files, a required PostgreSQL with pgvector, and at this pin three auto-run surfaces and three build-time execution points, among them a `setup.py` that executes at install time and a `conftest.py` that runs on pytest collection. Nothing here was installed or run, so every claim is read from source. The degraded path is the substantive one: development mode retrieves without a certified threshold and stamps `unverified`, and `generation_promoted_unsafe_development` is a real audit event, so a deployment can serve unjudged results and a generation can reach production without the validation that normally precedes it — both are named honestly in the code, which is why they are visible here at all, but they are escape hatches that ship. The reviewer identity is a supplied string rather than an authenticated principal. And the decision ledger, the only record of *why* a particular search abstained, is off by default and best-effort by design: a ledger write failure is counted and logged, never raised, so the audit of retrieval decisions is exactly as complete as the operator's configuration makes it"
---

## 1. Executive Summary

RE-call is "[m]emory that abstains instead of guessing" — version 0.14.0,
103,088 lines of Python across 254 modules with 518 test files, running on the
caller's own PostgreSQL with pgvector. **The licence changed between the
previous pin and this one**: releases up to and including 0.13.x stay Apache-2.0,
and this release and later ones are under the PolyForm Noncommercial License
1.0.0, which permits personal, educational and noncommercial research use and
requires a separate written licence for commercial production, a hosted service
or redistribution. A `COMMERCIAL_LICENSE.md` sits beside it in the tree. It stores source documents, indexes
them, "and keeps validity and lineage attached to every hit."

The pitch is a distinction rather than a feature:

> "Plain vector search returns nearby text. RE-call also asks whether that text
> is current, supported, and trustworthy enough for the query. A superseded
> claim comes back marked `superseded`; a result that does not clear the
> calibrated trust gate becomes `ABSTAIN` with a reason."

That is implemented as a closed vocabulary of eleven verdicts, of which exactly
one — `ok` — becomes evidence. The rest stay readable and never become the
answer. Under a strict policy the gate does not degrade quietly; it raises.

**What makes this repository worth a careful read is not the retrieval stack but
what surrounds it.** `docs/preregistrations/` holds 162 dated markdown documents,
running from 15 August to 15 September 2026, each stating what was about to be
measured before the measurement happened. Amendments are separate dated files
(`...-amendment-2.md` through `-amendment-5.md` on one canary), and results are
separate documents again (`2026-08-27-checker-ground-truth.md` beside
`2026-08-27-checker-ground-truth-result.md`). A hypothesis and its outcome
cannot be reconciled after the fact when both are committed under their own
dates.

**The single best passage in the tree is about the project's own test data.** The
off-topic query pool — subjects a search must abstain on — was written as Python
literals, and RE-call is a system people point at code corpora, including its
own:

> "These subjects are DATA, and as Python literals they were also CORPUS.
> `offtopic_subjects_absent_from` keeps a subject only when none of its content
> words appear anywhere in the corpus under test, so a code corpus that includes
> recall's own tree ingested this very list and then disqualified every one of
> its 25 subjects."

It was measured, not assumed: none of twenty-five survived against a
repository-rooted corpus, eleven of twenty-five against a third-party corpus of
the same size, "so the failure was recall dogfooding itself, not the pool being
too small." The pool moved to JSON, which the wizard's `**/*.py` and `**/*.md`
globs do not match. And the distinctive words are deliberately never written in
prose, because naming one re-contaminates the pool — a rule the author reports
breaking twice while fixing it, "once in a comment in
`recall/wizard/queryset.py`, caught only because the measured survivor count
moved the wrong way, and once in THIS paragraph, caught in seconds by the guard
below."

Every one of the atlas's seven capabilities is present, and the reason is
visible in the code rather than in the README: each was built as an argument
about what a neighbouring design would have got wrong.

## 2. Mental Model

A **hit** carries a verdict, and only `ok` becomes evidence.

A **verdict** is a member of a closed set, each one defined against the one it
is most likely to be confused with.

A **tombstone** is permanent, keyed on the source URI, and re-checked mid-build.

A **tenant** is a Postgres row-level-security policy, not a `WHERE` clause.

A **preregistration** is what you wrote down before you measured.

```mermaid
%% caption: retrieval is judged against two independent time axes and a calibrated threshold, only ok hits become evidence, strict mode refuses rather than degrading, and erasure writes a permanent tombstone the builder re-checks inside the ingest
flowchart TB
    Q["a query"] --> LEGS["dense · sparse · graph legs, fused and reranked"]
    RLS[("recall_chunks_v1 —<br/>FORCE ROW LEVEL SECURITY<br/>tenant_id = current_setting(GUC)")] --> LEGS
    LEGS --> EV["trust.evaluate — pure: no DB access, no clock reads"]
    VT["now = VALID time:<br/>drives expired, not_yet_valid<br/>from declared valid_from/valid_until"] --> EV
    TT["known_as_of = TRANSACTION time:<br/>drives not_yet_known from<br/>first_indexed_at, not indexed_at"] --> EV
    TT -.->|"using the LAST write 'claimed a memo edited today<br/>had never existed before the edit, so every replay<br/>of an earlier instant reported an empty store'"| FIXED["a bug found, fixed, written down"]
    SUPE["supersession edges are rewound too:<br/>an edge dates from when its<br/>superseding document was written"] --> EV
    EV --> V{"one of eleven verdicts"}
    V -->|"ok"| USE["evidence: trusted = [h for h in hits if h.verdict == 'ok']"]
    V -->|"superseded · expired · not_yet_valid ·<br/>not_yet_known · low_confidence ·<br/>invalid_metadata · not_entailed ·<br/>dependency_invalidated"| SEEN["returned and readable —<br/>never the answer"]
    V -->|"ambiguous_supersession"| CLOSED["fails closed rather than<br/>guessing a successor"]
    V -->|"unverified"| DEG["the DEGRADED-mode verdict:<br/>'not a weaker ok — the trust gate never ran'"]
    GATE{"strict policy?"} --> EV
    GATE -->|"strict"| REFUSE["raise TrustRefusal —<br/>including a deliberate<br/>BROAD-CATCH: fail-closed"]
    GATE -->|"degraded"| DEG
    FORGET["forget(source_uri)"] --> TS[("recall_source_tombstones<br/>PK (tenant_id, source_uri)<br/>FK → the source_forgotten audit event")]
    TS --> BUILD["every future build calls _is_tombstoned"]
    BUILD -.->|"re-checked INSIDE the ingest, because an erasure<br/>arriving mid-build would otherwise land after<br/>the check that would have caught it"| PERM["permanent: the URI is barred from every future build"]
    AUD[("recall_audit_events — appended on the<br/>build's OWN connection: generation_created,<br/>built, failed, abandoned, validated,<br/>rolled_back, gc, source_forgotten")] --- BUILD
    PROP["a model-extracted proposal"] --> REV{"review_proposal: _require_review_fields"}
    REV -.->|"raises without reviewer identity,<br/>timestamp AND a non-blank audit note"| REFUSED["no promotion"]
    REV --> PF["PromotedFact — the only type<br/>downstream writers accept"]
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `recall/trust.py` | The gate: two time axes, the verdicts, and where it refuses |
| `recall/types.py` | The verdict vocabulary, each value argued against its neighbour |
| `recall/generations.py` | Builds, the audit events, and the tombstone re-checks |
| `recall/migrations/sql/0008_generation_foundation.sql` | Forced RLS, the audit table, the tombstone table |
| `recall/promotion.py` | The review gate a proposal cannot go around |
| `recall/decision_ledger.py` | A witness of retrieval decisions, deliberately not an enforcer |
| `recall/eval/`, `docs/preregistrations/` | The negative sets, and what was written down first |

## 4. Essential Implementation Paths

`recall/trust.py:520-544` — the two axes, how they compose, and the
`first_indexed_at` bug that made every point-in-time replay return an empty
store.

`recall/types.py:55-81` — eleven verdicts, and the argument for why `unverified`
is not `low_confidence`.

`recall/generations.py:566-570` with `:810`, `:976`, `:1005` — one tombstone
check, called three times, for a reason stated in `generation_store.py:52-58`.

`recall/migrations/sql/0008_generation_foundation.sql:128-133` — `FORCE ROW
LEVEL SECURITY` on the chunk table itself.

`recall/promotion.py:200-210` — a gate that refuses three ways.

`recall/eval/synthetic.py:75-100` — the negative pool that was contaminating
itself, measured.

## 5. Memory Data Model

Source documents are chunked into `recall_chunks_v1` with declared validity,
lineage and supersession attached, all under a tenant policy. Beside them,
`AtomicFact` is a structured claim — namespace, subject, predicate, object,
context, `valid_from`, `valid_until` — validated on construction and promoted
into an append-only fact ledger with a current-state projection. Generations
version the corpus: a build produces a new generation, promotion makes it
active, and a garbage collector removes superseded ones.

## 6. Retrieval Mechanics

Dense, sparse and graph legs are fused and reranked, then every surviving hit is
judged by `trust.evaluate` — a pure function with no database access and no
clock reads, which is what makes the two time axes testable without a database.
Calibration supplies the threshold, and carries its own certification status, so
the system can tell a threshold it fitted from one it never had.

## 7. Write Mechanics

A build reads a manifest, skips tombstoned URIs, writes chunks, and appends its
lifecycle events on the same connection. The corpus fingerprint is computed from
the manifest minus the tombstoned set, so a build whose only change is an
erasure is still a distinct generation rather than a no-op. Extracted proposals
take the other path, through review.

## 8. Agent Integration

A CLI, an MCP server registered as `io.github.GiulioDER/re-call`, a Codex
plugin, Claude Code hooks, desktop packaging and Docker compose files. Several
preregistrations measure the integration itself — hook ordering, in-process
against MCP transport, tool-definition context cost, and Claude Code with and
without RE-call, calibrated and not.

## 9. Reliability, Safety, and Trust

**The review gate is kept off the model's own surface, and the project says
why.** The MCP server registers `recall_rewrite_plan` and no apply twin, and the
docstring is the clearest statement of this rule anywhere in the corpus:
*"There is deliberately no `recall_rewrite_apply`. The MCP client is the model,
so letting it supply a reviewer id and an audit note would make the named human
gate a formality it satisfies by typing a string: the gate becomes a field, not
a person. This surface proposes; a human applies at `recall rewrite apply`."*
The plan tool hands back the exact CLI line a person would run
(`recall_mcp/reasoning_admin.py:14-20`), so the handoff is spelled out rather
than implied. The one fact-writing tool states the same rule as a property of
its inputs: on `recall_apply_fact`, trust verdicts, timestamps, approval fields
and writer identity are *"server-owned and cannot be supplied here"*. That is
what `human_review` is for, and this is the version to copy.

Fail-closed is the default posture and is written as such, including a broad
exception catch annotated with its intent. The gaps are the configured ones: a
development mode that serves `unverified` results, a
`generation_promoted_unsafe_development` path that exists, and a decision ledger
that is off unless enabled and best-effort when it is. The mutation audit is the
part that is not optional — it commits with the build.

## 10. Tests, Evals, and Benchmarks

494 test files, evaluation suites over LoCoMo, LongMemEval, BEIR and synthetic
corpora, a labelled gap study, and abstention scored as its own axis. The
preregistration directory is the artifact that distinguishes it: hypotheses,
amendments and results filed separately and dated, including negative results
and a holdout-validation document.

## 11. For Your Own Build

Write down what you are about to measure, in a dated file, before you measure
it. Everything else here follows from that habit.

Check whether your evaluation data is inside your corpus. If your system indexes
code and your negative examples are Python literals, they are corpus, and the
failure is silent.

Re-check your tombstones inside the ingest, not only at the start of it.

Define each status against the one it will be confused with, and say so in the
type. `unverified` and `low_confidence` look interchangeable until somebody has
to explain a result.

## 12. Open Questions

Whether the degraded path should be reachable in a packaged install at all. Both
escape hatches are honestly named and audited, which is the right second-best;
the first-best would be that a deployment cannot serve an unjudged result.

Whether `reviewer_id` should be bound to an authenticated identity. The gate is
structural and the field is a string, so the mechanism is stronger than the
attribution it records.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `recall/types.py:55-81` | A status vocabulary where each value argues against its neighbour |
| `recall/trust.py:520-544` | Two time axes that compose, and the replay bug that shaped them |
| `recall/eval/synthetic.py:75-100` | Your own repository contaminating your own negative set |
| `recall/generations.py:566-570` | A tombstone check placed where the race actually is |
| `recall/promotion.py:200-210` | A review gate that refuses without a reviewer, a time and a note |
| `docs/preregistrations/` | 162 dated statements of what was going to be measured |

## History

**2026-09-19** — re-pinned to [`1157360f1e0704a06548d93a4f4797c415c722f9`](https://github.com/GiulioDER/RE-call/commit/1157360f1e0704a06548d93a4f4797c415c722f9), 29 commits and 184 files on. **All seven marks re-tested and held**, and `human_review` is re-grounded on the thing that actually settles the producer test. The structural gate is unchanged — `_require_review_fields` (`recall/promotion.py:200-210`) still raises without a reviewer identity, a review timestamp and a non-blank audit note, and `recall/rewrite.py:26` still records that a downstream function cannot take an unreviewed proposal because only `promote_accepted_proposal` produces a `PromotedFact`. What the record now cites beside it is the absence: the MCP server registers `recall_rewrite_plan` and no apply twin, and its docstring states the rule this atlas's rubric arrived at independently — *"letting it supply a reviewer id and an audit note would make the named human gate a formality it satisfies by typing a string: the gate becomes a field, not a person."* `recall_apply_fact` repeats it as an input property, with approval fields and writer identity server-owned. Quoted in section 9, and re-call is added to the rubric's list of what passing looks like. The stated limit is unchanged: on the CLI path `reviewer_id` is a supplied string, so the mechanism is stronger than the attribution it records, and section 12 still asks whether it should be bound to an authenticated principal. Screened again first; nothing installed or run.

**2026-09-16** — [`1994fd256820df7970eac1f1d588a1961da16edf`](https://github.com/GiulioDER/RE-call/commit/1994fd256820df7970eac1f1d588a1961da16edf) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: fifteen files scanned, three auto-run surfaces, three build-time execution points (`recall/setup.py`, which executes at install time, `tests/conftest.py`, which runs on pytest collection, and the `Makefile` default target), one unpinned dependency surface and three dependency files inside the seven-day cooldown. `uv.lock` is present. A `hooks/pre-commit` payload sits in the tree uninstalled and inert. `AGENTS.md` and `CLAUDE.md` are addressed to a reading agent and were recorded as data. Nothing was installed, built or run, so every claim here is read from source rather than observed.

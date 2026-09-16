---
title: "Verimem"
eyebrow: "The mutation chain records that a row was deleted and never what it said"
description: "An AGPL Python memory whose writes pass an admission gate, whose recall SQL drops three stored statuses, and whose hash-chained mutation log is deliberately action-only so that erasure and immutability are not in contradiction."
root: ../..
page_kind: system
source_name: "aureliocpr-ctrl/verimem"
source_url: https://github.com/aureliocpr-ctrl/verimem
archive_name: "aureliocpr-ctrl--verimem"
revision: ef7de72459c9d12a1f4a22af4362a1b4a47c8fa8
revision_url: https://github.com/aureliocpr-ctrl/verimem/commit/ef7de72459c9d12a1f4a22af4362a1b4a47c8fa8
analyzed_at: 2026-09-16
capabilities: "trust_state, audit_log, human_review"
capability_evidence:
  trust_state: "a stored status vocabulary that the ranking SQL drops, with every exception opt-in | verimem/admission_gate.py:85, :276-280, verimem/bm25_rank.py:26, :42, verimem/semantic.py:4016-4026 | the gate classifies a write into a closed set of statuses including `user_belief`, `quarantined`, `orphaned`, `legacy_unverified`, `provisional` and `model_claim`, and the retrieval SQL withholds three of them outright: the BM25 rank clause is `status NOT IN ('orphaned', 'quarantined', 'user_belief')`, present both as an appended predicate and as a standalone filter string. `recall` then makes every widening an opt-in keyword — `include_superseded`, `include_orphaned`, `include_beliefs`, `include_conversational`, `min_status` — all defaulting to the withholding behaviour, so a caller sees the guarded view unless it asks otherwise. That is the direction the mark is about: a stored discrete state that keeps a fact out of what an agent is handed, rather than a score that ranks it lower | 284 of the committed test files exercise the quarantine path, and `verimem/semantic.py:5695-5701` documents the reverse as deliberately narrow — only quarantined rows are restorable, so a restore \"never silently un-orphans/un-supersedes\""
  audit_log: "a hash-chained mutation table written in the mutation's own transaction, and deliberately holding no content | verimem/mutation_audit.py:1-25 | \"[e]very destructive operation on the facts store (delete / purge / forget / supersede / reset) appends one row to `audit_mutations` INSIDE THE SAME TRANSACTION as the mutation itself\", recording principal, action, resource id, timestamp and outcome, chained so that \"any edit, interior deletion or reorder of past rows is detectable by `verify()`\". Two design decisions are argued rather than assumed. It is action-only, never content, because \"storing WHAT was deleted — even as a hash, brute-forceable on short text — inside an immutable chain makes GDPR Art.17 erasure a logical contradiction\"; the chain proves \"THAT/WHO/WHEN/WHICH-RECORD, not what the record said\", and free text \"must never reach this table\". And it is fail-closed: `record_mutation` \"never swallows\", running after the mutation's SQL on the same connection so a failure propagates rather than leaving an unrecorded deletion | the module states both decisions were \"forged against two independent adversarial reviews (GLM-5.2 + deepseek, convergent findings)\", naming the failure ids each one answers"
  human_review: "an operator command that re-admits quarantined facts, dry-run by default, and a restore that refuses to widen | verimem/cli.py:4921-4947, verimem/semantic.py:5695-5701, verimem/review_queue.py:1-16 | `verimem facts requalify-quarantined` is run by a person and applies nothing unless `--apply` is passed, so the default is a report of what would be re-admitted. Underneath, `restore_fact` flips a quarantined fact back to a named status with a reason and returns whether a quarantined row actually existed, making \"the Tier-2 triage genuinely REVERSIBLE (a wrongly-declassed fact, or one corroborated by later evidence, returns to the live view)\" while refusing to touch orphaned or superseded rows. The queue that feeds it is measured on purpose: \"A queue nobody measures is a queue nobody drains, and 'held for review' quietly turns into 'silently dropped' — the fact was neither admitted nor honestly refused, which is the one outcome a memory sold on honest abstention cannot afford\" | the same module publishes its own gap under a DECLARED LIMIT heading: with no persisted per-fact quarantine reason, the reported depth \"counts the WHOLE quarantined backlog rather than the L4-review class alone\""
stack_storage: "sqlite"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A fact with a proposition, a status from a closed vocabulary, a writer role, grounding evidence and a trust score, beside episodes carrying task traces and outcomes"
  storage: "SQLite, with a local judge model fetched once for the admission gate and an audit table chained by tamper-evidence primitives"
  retrieval: "BM25 and semantic recall whose SQL drops orphaned, quarantined and user-belief rows, with each exception a named opt-in keyword"
  write: "Every write passes an admission gate with three tiers — `off`, `fast` substring detectors, and `full` with claim validation against semantic memory — before a fact is persisted"
  update_delete: "Supersede, quarantine, forget, purge and reset, each appending an action-only row to the hash-chained mutation table in the same transaction"
  scoping: "A zero-schema topic-prefix convention, `user:<u>/agent:<a>/run:<r>/<base>`, assembled and filtered by the CLI rather than enforced in the store"
  integration: "A CLI, an MCP server registered as `io.github.aureliocpr-ctrl/verimem`, an SDK client, a gateway and Docker compose files"
  background: "Admission cleanup and requalification passes, trust calibration, anomaly detection, and a sleep-consolidation family"
  trust: "An admission gate with a local judge, grounding scores on the write receipt, a status vocabulary that withholds, and a tamper-evident mutation chain"
  strengths: "Two habits, visible everywhere. The first is that the reasoning is written beside the code and names what it is defending against: the mutation audit is action-only because \"storing WHAT was deleted — even as a hash, brute-forceable on short text — inside an immutable chain makes GDPR Art.17 erasure a logical contradiction\", and both that decision and the fail-closed one are attributed to two independent adversarial reviews with the finding ids they answer. The second is that the project corrects its own documentation in place and shows the receipt. The README's opening box previously said the admission gate was off until a warmup command was run; it now says that was true of 0.7.1, names the function that was reachable only from `warmup`, cites \"`tests/test_ws5_giudice_si_procura_da_solo.py` records the measurement and the fix\", and adds the sentence that matters — \"[t]he fix shipped; the text did not follow it. Corrected here.\" The review queue does the same for its own shortfall, publishing a DECLARED LIMIT that the depth it reports counts the whole quarantined backlog rather than the review class alone, on the ground that \"[m]easuring the real thing coarsely beats measuring a precise thing that does not\""
  risks: "Scope is the substantive gap. Multi-tenancy is \"a ZERO-SCHEMA topic prefix\" — `user:<u>/agent:<a>/run:<r>/<base-topic>` — with the scope living in the topic string and filtered at recall, and the functions that build the `topic LIKE '<prefix>%'` narrow are imported by `verimem/cli.py` rather than applied inside the store, so the isolation holds on the command-line path and depends on the caller everywhere else. The module names its own ambiguity too: \"a legitimate topic that literally starts with `user:` / `agent:` / `run:` would be parsed as scoped\". There is no bitemporal pair — `search_facts` takes a single `as_of` over record time, so the store can answer when it learned something and not when that thing was true. Nothing is keyed on a rejected value, so a purged claim can be written again as a new fact. And the surface is very large for the guarantee it sells: 130,388 lines in the core package across several hundred modules, 1,694 test files, a 711 MB judge model fetched on first gated write, and at this pin five auto-run surfaces, two build-time execution points and two dependency files inside the cooldown"
---

## 1. Executive Summary

Verimem is "**[v]erified memory for AI agents**" — AGPL-3.0 with a commercial
option, Python, version 0.7.7, 130,388 lines in the core package with 1,694 test
files, on SQLite. Its promise is a conjunction:

> "Every write passes an admission gate, every read carries provenance, and a
> claim the source **openly contradicts** does not come back as truth."

**The mechanism worth carrying away is what the audit log refuses to store.**
Most projects that reach for a tamper-evident chain put the content in it, and
then discover that an immutable record of what was deleted is itself a copy of
what was deleted. `mutation_audit.py` argues the other way:

> "ACTION-ONLY, never content (F1/F8): storing WHAT was deleted — even as a
> hash, brute-forceable on short text — inside an immutable chain makes GDPR
> Art.17 erasure a logical contradiction. The chain proves THAT/WHO/WHEN/
> WHICH-RECORD, not what the record said."

Every destructive operation — delete, purge, forget, supersede, reset — appends
one row "INSIDE THE SAME TRANSACTION as the mutation itself", and
`record_mutation` "never swallows", so a failure to record propagates instead of
leaving an unrecorded deletion. Both decisions are attributed to "two
independent adversarial reviews (GLM-5.2 + deepseek, convergent findings)", with
the finding ids each one answers.

**The status vocabulary withholds rather than ranks.** The gate classifies a
write into a closed set — `user_belief`, `quarantined`, `orphaned`,
`legacy_unverified`, `provisional`, `model_claim` — and the ranking SQL carries
`status NOT IN ('orphaned', 'quarantined', 'user_belief')`. Every route back to
the withheld material is an explicitly named opt-in on `recall`:
`include_superseded`, `include_orphaned`, `include_beliefs`, `min_status`. The
atlas has read two systems this week whose epistemic vocabulary only sorted the
results; this one drops them.

**The project corrects its own documentation in public.** The README's first
box used to say the gate was off until a warmup command was run. It now carries
the correction, the version the old claim was true of, the function that was
reachable only from `warmup`, the test that "records the measurement and the
fix", and the admission that matters: "*The fix shipped; the text did not follow
it. Corrected here.*"

**The gap is scope.** Multi-tenancy is "a ZERO-SCHEMA topic prefix" —
`user:<u>/agent:<a>/run:<r>/<base-topic>` — and the functions that turn it into
a `topic LIKE '<prefix>%'` narrow are imported by `verimem/cli.py`, not applied
inside the store. The isolation is real on the command-line path and is the
caller's responsibility elsewhere, which is why the mark is withheld.

## 2. Mental Model

A **status** is a stored verdict, and three of them keep a fact out of recall.

A **widening** is a named keyword you had to type.

An **audit row** proves that a deletion happened and cannot tell you what was deleted.

A **quarantine** is reversible, and only quarantine is.

A **declared limit** is a gap the module publishes about itself.

```mermaid
%% caption: writes pass an admission gate that assigns a status from a closed vocabulary, the ranking SQL drops three of those statuses unless a named keyword opts them back in, and every destructive operation appends an action-only row to a hash-chained table in the same transaction
flowchart TB
    W["remember --source"] --> GATE{"anti_confab_gate:<br/>off, fast or full"}
    GATE -->|"fast: L1 substring detectors"| J["local judge model,<br/>711 MB, fetched once, then ~0.2 s offline"]
    GATE -->|"full: + validate_claim over semantic memory"| J
    J --> ST["status assigned from a closed vocabulary:<br/>model_claim · user_belief · quarantined ·<br/>orphaned · legacy_unverified · provisional"]
    ST --> DB[("SQLite facts store")]
    DB --> RANK["BM25 / semantic recall"]
    RANK --> FILTER["status NOT IN ('orphaned', 'quarantined', 'user_belief')"]
    FILTER --> OUT["what the agent is handed"]
    FILTER -.->|"every way back in is a named keyword:<br/>include_superseded · include_orphaned ·<br/>include_beliefs · min_status"| OPT["widening is opt-in, never the default"]
    QUEUE["borderline writes held for review"] --> DEPTH["depth reported on the write that ADDS to the queue"]
    DEPTH -.->|"'a queue nobody measures is a queue nobody drains,<br/>and held-for-review quietly turns into silently dropped'"| HONEST["neither admitted nor honestly refused<br/>is the one outcome it cannot afford"]
    OPER["an operator runs<br/>verimem facts requalify-quarantined"] --> DRY{"--apply passed?"}
    DRY -->|"no, the default"| REPORT["a report of what would be re-admitted"]
    DRY -->|"yes"| RESTORE["restore_fact: quarantined → named status, with a reason"]
    RESTORE -.->|"only quarantined rows are restorable —<br/>never silently un-orphans or un-supersedes"| NARROW["the reverse is deliberately narrow"]
    DEL["delete · purge · forget · supersede · reset"] --> AUD[("audit_mutations — principal, action,<br/>resource_id, ts, outcome; hash-chained")]
    DEL -.->|"appended INSIDE THE SAME TRANSACTION,<br/>and record_mutation never swallows"| FC["fail-closed: no unrecorded deletion"]
    AUD -.->|"ACTION-ONLY, never content: storing what was deleted<br/>even as a hash 'makes GDPR Art.17 erasure<br/>a logical contradiction'"| WHY["the chain proves THAT / WHO / WHEN /<br/>WHICH-RECORD, not what the record said"]
    SCOPE["user:alice/agent:pentester/run:7/topic"] -.->|"zero-schema: the scope lives in the topic string,<br/>and the LIKE-prefix narrow is assembled in cli.py<br/>rather than inside the store"| NOSCOPE["no scope-enforced mark"]
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `verimem/admission_gate.py` | The status vocabulary and what earns each one |
| `verimem/anti_confab_gate.py` | Three validation tiers, run before a fact is persisted |
| `verimem/bm25_rank.py` | The clause that keeps three statuses out of ranked recall |
| `verimem/semantic.py` | Recall, its opt-in widenings, and the reversible restore |
| `verimem/mutation_audit.py` | A hash-chained, action-only, fail-closed mutation record |
| `verimem/review_queue.py` | Queue depth, and a declared limit about measuring it |
| `verimem/scope.py`, `agent_scope.py` | Topic-prefix multi-tenancy, and its accepted caveat |

## 4. Essential Implementation Paths

`verimem/mutation_audit.py:1-25` — the whole argument for what an audit chain
must not contain.

`verimem/bm25_rank.py:26`, `:42` — five words of SQL doing the withholding.

`verimem/semantic.py:4016-4026` — a recall signature where every widening is
named.

`verimem/semantic.py:5695-5701` — an un-quarantine that refuses to un-orphan.

`verimem/review_queue.py:1-16` — why an unmeasured queue is a dishonest
abstention.

`verimem/scope.py:1-14` — the scope convention, and the collision it accepts.

## 5. Memory Data Model

A fact carries a proposition, a status from the gate's vocabulary, a writer
role, grounding evidence and trust signals; episodes carry task traces, skills
and outcomes beside them. Statuses are the load-bearing field: they decide
whether the fact is in the live view, and the transitions between them are what
the mutation chain records.

## 6. Retrieval Mechanics

BM25 and semantic recall over the guarded view, with the status filter compiled
into both the appended predicate and a standalone filter string so the two
cannot drift. `search_facts` accepts a single `as_of` over record time and
counts how many rows that constraint excluded, which is a real point-in-time
read over one axis rather than two.

## 7. Write Mechanics

`validate="fast"` is the default tier: pure substring detectors, "cold execution
<< 1 ms". `full` adds claim validation against the agent's semantic memory at a
measured mean of about 13 ms. `off` exists and is labelled what it is — "[p]ure
escape hatch for migrations, replays, deliberate writes." The first gated write
on a fresh install fetches the judge model itself, which the README measures at
85.7 seconds and explains how to move rather than avoid.

## 8. Agent Integration

A CLI, an MCP server registered as `io.github.aureliocpr-ctrl/verimem`, an SDK
client exposing `search(query, as_of="auto")`, a gateway, Docker compose files
and hook and slash-command bundles.

## 9. Reliability, Safety, and Trust

The strong parts are the fail-closed audit, the withholding statuses, the
reversible-but-narrow restore, and a documentation habit that publishes
corrections and limits rather than quietly fixing them. The weak parts are scope
living in a string and assembled outside the store, a single time axis, and no
value-keyed record of a rejected claim.

## 10. Tests, Evals, and Benchmarks

1,694 test files, of which 284 touch the quarantine path, plus benchmark
directories and a `docs/stato-reale/banchi/` tree the README cites figure by
figure. The negative-bundle suites are about skill pairs that predict failure
rather than about material that must not be retrieved, so the committed
must-not-retrieve case this design would support does not appear to exist yet.

## 11. For Your Own Build

Decide what your audit chain is allowed to contain before you build it. An
immutable record of content is a second copy you cannot delete, and the argument
in `mutation_audit.py` is the clearest statement of that trade in this corpus.

Write the audit row inside the mutation's transaction and let a failure
propagate. An audit that can fail silently is an audit that is wrong exactly
when it matters.

Name every widening. A recall signature where `include_orphaned` has to be typed
is one where the default is defensible and the exception is visible in the
caller's code.

Publish the limit. `DECLARED LIMIT` as a heading, with the reason the coarse
measure was chosen, is better than a precise number nobody computes.

## 12. Open Questions

Whether scope should move into the store. Everything else here is enforced where
it cannot be forgotten; the topic prefix is assembled by the CLI, and a library
consumer that skips it gets every tenant's facts.

Whether the gate's status vocabulary wants a second time axis behind it. A fact
that was true and stopped being true is currently handled by supersession over
record time, which cannot answer what was true last quarter.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `verimem/mutation_audit.py:1-25` | What an immutable chain must not be allowed to remember |
| `verimem/bm25_rank.py:26`, `:42` | A status filter written twice so it cannot drift |
| `verimem/semantic.py:4016-4026` | Widening as a named keyword rather than a default |
| `verimem/review_queue.py:1-16` | Why "held for review" becomes "silently dropped" |
| `verimem/scope.py:1-14` | Multi-tenancy as a string convention, with its collision declared |

## History

**2026-09-16** — [`ef7de72459c9d12a1f4a22af4362a1b4a47c8fa8`](https://github.com/aureliocpr-ctrl/verimem/commit/ef7de72459c9d12a1f4a22af4362a1b4a47c8fa8) — first reading, at a commit dated 13 September 2026. Screened before opening, from a shallow clone: five auto-run surfaces, two build-time execution points, two unpinned dependency surfaces and two dependency files inside the seven-day cooldown. `CLAUDE.md` is addressed to a reading agent and was recorded as data. Dual-licensed AGPL-3.0 with a paid commercial option; the licensing file carries no rider restricting who may read or analyse the code. Nothing was installed, built or run, no judge model was fetched, and none of the benchmark figures quoted here were reproduced — they are the project's own measurements, read from its documentation.

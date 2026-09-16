---
title: "Temvera"
eyebrow: "It publishes the bypass that works, and a test asserts that it is the only one"
description: "A PVLDB artifact whose reference substrate is a bitemporal belief ledger with signed evidence, tenant-scoped authorization and crypto-shredded payloads, shipped beside a harness that can recheck every printed figure without an API key."
root: ../..
page_kind: system
source_name: "suanlab/temvera"
source_url: https://github.com/suanlab/temvera
archive_name: "suanlab--temvera"
revision: 75243a3dbc3dfeda3613fb69e940c774f5ff4e5b
revision_url: https://github.com/suanlab/temvera/commit/75243a3dbc3dfeda3613fb69e940c774f5ff4e5b
analyzed_at: 2026-09-16
capabilities: "trust_state, bitemporal, scope_enforced, audit_log, negative_eval"
capability_evidence:
  trust_state: "a five-level authority enum that refuses an action rather than discounting it | src/temvera/model.py:19-24, :84-97, src/temvera/security.py:9-41, src/temvera/governance.py:86-90 | `Authority` is stored on every belief as one of `SYSTEM`, `VERIFIED_TOOL`, `USER`, `EXTERNAL`, `INFERRED`, ranked 4 down to 0 in `AUTHORITY_RANK`. `ProvenanceGate.evaluate` returns `ActionDecision(False, \"insufficient authority\")` when any piece of evidence ranks below the configured minimum, which defaults to `VERIFIED_TOOL`, and the governed policy repeats the check on signed envelopes. So a belief whose authority is `INFERRED` or `EXTERNAL` cannot authorize an action at all — it is withheld rather than scored down. The gate also refuses evidence with no `sources` (\"missing source provenance\") and evidence whose derivation lineage launders a low-authority claim through a high-authority one | src/temvera/bypass.py:22-56 exercises the authority and lineage refusals as probes, and tests/test_bypass.py asserts the outcome of each"
  bitemporal: "a query protocol that requires both instants, and baselines defined by which one they throw away | src/temvera/evaluation.py:14-51, :71-75, src/temvera/model.py:89-100, src/temvera/store.py:55-57 | the `QuerySystem` protocol makes both axes mandatory in the signature — `query(subject, attribute, *, valid_at, transaction_at)` — and `Belief` carries `valid_from`/`valid_to` for world time beside `recorded_at` and `last_confirmed_at`, with `valid_at()` implementing the half-open interval. What makes this more than a schema is the ablation built on it: `AppendOnlyBaseline` is constructed by filtering the event stream to `INGEST` only, so it \"[i]gnore[s] revision, expiry, and purge operations\", and the weaker baselines take `valid_at` and then execute `del valid_at` before answering from transaction time alone. Every comparator receives the same two instants, and the design isolates exactly what discarding an axis costs | experiments/ holds sealed runs, and `temvera benchmark` compares the bitemporal oracle against append-only, full-context, recent-context, BM25@1 and last-write-wins under identical histories"
  scope_enforced: "tenant as a required keyword on the authorization call, matched against the evidence envelope | src/temvera/governance.py:69-83, src/temvera/bypass.py:36-40 | `authorize_action` takes `tenant: str` as a keyword-only argument with no default, so a caller cannot omit it, and the first substantive check refuses when `any(item.tenant != tenant for item in envelopes)` with the reason \"cross-tenant evidence\". The key is stored on the signed envelope rather than passed alongside it, which means re-labelling evidence for another tenant also invalidates its signature. The limit worth stating is that this governs authorization rather than retrieval: it decides whether evidence may act, not what a search returns | src/temvera/bypass.py:36-40 builds the `cross_tenant_replay` probe by taking a validly signed envelope and replacing only its tenant, and tests/test_bypass.py asserts it does not activate"
  audit_log: "an append-only event ledger the projection is rebuilt from, with redaction that leaves the record intact | src/temvera/store.py:24-36, :55-94, :109-175, src/temvera/protected_store.py:14-40 | the store is the event log: `append` refuses a duplicate `event_id`, `rebuild(transaction_at)` projects state from the events, and `verify_rebuild` re-derives the projection to check it. Erasure is the part worth reading, because an append-only ledger in Git is usually where deletion goes to die: `ProtectedEventStore` keeps \"[m]etadata, validity, lineage identifiers, and ciphertext … auditable\" while encrypting subject, attribute, value and sources under a per-belief key, and erases by destroying the key, writing a `destroyed_key_sha256` receipt. The redaction is two-phase with a journal and a `recover_redactions` path, so an interrupted purge is finished rather than left half-done, and `residual_occurrences` exists to check that erased text is really gone | tests/ cover rebuild verification and the redaction recovery path; the key directory carries its own deny-all `.gitignore`"
  negative_eval: "adversarial probes committed with the one that works, and a test pinning it as the only one | src/temvera/bypass.py:1, :51-56, tests/test_bypass.py:8-11, src/temvera/forgeteval.py:1-14 | `run_bypass_probes` returns four results, each a `BypassResult(probe, activated, expected_limitation)`. Three must not activate — `cross_tenant_replay`, `signed_claim_tamper`, `expired_signature_replay` — and the fourth, `compromised_trusted_signer`, is declared `expected_limitation=True` because a policy anchored on a signer's key cannot survive that key being stolen. The test asserts that exactly one probe activated and that it is the one declared as a known limitation, so a newly-working bypass fails the suite and the honest one cannot be quietly removed. Publishing the attack that succeeds, in the same tuple as the ones that fail, is the shape this atlas looks for and rarely finds | src/temvera/forgeteval.py adapts the public ForgetEval operation contract, where a deactivated memory must stop being returned, and tests/ run both"
stack_storage: "files"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A belief — subject, attribute, value, a valid interval, a recorded and a last-confirmed time, an authority level, sources, derivation lineage, a status and a supersession link — written as an immutable event"
  storage: "Append-only JSONL event ledgers in a Git repository, with a protected variant that encrypts each belief's payload under its own key and keeps only metadata and ciphertext in history"
  retrieval: "Exact, lexical and vector retrieval over a projection rebuilt from the events, with calibrated fusion and reranking; every query takes a valid instant and a transaction instant"
  write: "Events appended through a store that refuses duplicate ids, with ingest gated by a provenance and signature policy before a claim may act"
  update_delete: "Revision and expiry are events rather than edits; erasure destroys a per-belief key and appends a receipt, and redaction runs in two phases with a recovery path"
  scoping: "Tenant is carried on the signed evidence envelope and is a required argument to authorization, which refuses cross-tenant evidence; it governs acting rather than searching"
  integration: "A `temvera` CLI over the substrate and the experiment harness, plus adapters for the external systems the paper measures"
  background: "Consolidation and decay studies, a literature-freeze tool for the paper's prior-art review, and artifact verification over sealed runs"
  trust: "Five ranked authority levels that refuse rather than discount, Ed25519-signed evidence envelopes, derivation-laundering detection, and adversarial probes whose one success is published"
  strengths: "Two things, and they are the same habit applied twice. The first is `bypass.py`, which publishes the attack that works: `compromised_trusted_signer` activates, is declared `expected_limitation=True`, and `tests/test_bypass.py` asserts that it is the only probe that activates — so a newly-working bypass breaks the build and the honest admission cannot be deleted without the test noticing. The second is the artifact discipline. \"Every number the paper reports is an aggregation over sealed per-case transcripts, so the whole paper can be checked without an API key, a database server, or a dataset download\", with `verify_paper_claims.py` pairing \"each figure as printed in the paper with a recomputation from a sealed run\" and failing \"if either half moves\" — the check catches a corrected number as readily as a corrupted one. Regeneration is deliberately decoupled from verification, \"so you can confirm what we computed before deciding whether to re-run generation\". The status section is written the same way, listing what remains incomplete and stating that \"[c]laims outside the frozen synthetic fixtures remain hypotheses\""
  risks: "This is a research reference implementation and says so: version 0.0.1, \"[n]o production readiness is claimed\", and a provisional API. The substrate is 7,683 lines of Python with no server, so treat the mechanisms as demonstrations rather than as something to deploy. The deletion story is the one to read carefully against the project's own subject matter: crypto-shredding makes an erased payload unrecoverable and leaves a receipt, but nothing on the ingest path consults those receipts, so re-asserting an erased value produces a new belief with no sign that the store once destroyed it — a deletion record rather than a tombstone. Tenant scoping governs authorization rather than retrieval, so it answers whether evidence may act and not what a search returns. There is no human-review surface: the review tooling in the tree belongs to the paper's prior-art process, not to the memory. And the paper's external comparisons need an OpenAI key, a Neo4j server and a second interpreter, which is a real barrier to the half of the work that measures other people's systems"
---

## 1. Executive Summary

Temvera is "[t]emporal, provenance-aware memory infrastructure for AI agents" —
Apache-2.0, Python, version 0.0.1, 11,702 lines across 93 files, and the artifact
behind a PVLDB Experiment, Analysis & Benchmark paper whose title is a thesis
this atlas has been testing one repository at a time:

> *Temporal Fields Are Not Temporal Correctness: Measuring Bitemporal and
> Deletion Semantics in Deployed Agent Memory.*

The repository is two things at once. It is a measurement harness for deployed
systems — with adapters for the graph and vector memories the paper compares —
and it is a reference substrate implementing what the paper argues for: an
append-only belief ledger with valid and transaction time, signed evidence,
ranked authority, tenant-scoped authorization, and erasure by key destruction.

**The single most unusual thing in the tree is that it publishes the bypass that
works.** `run_bypass_probes` returns four adversarial results, each carrying
whether it activated and whether that activation was expected:

```python
BypassResult("compromised_trusted_signer", compromised_allowed, True),
BypassResult("cross_tenant_replay", cross_allowed, False),
BypassResult("signed_claim_tamper", tampered_allowed, False),
BypassResult("expired_signature_replay", expired_allowed, False),
```

Three must not activate. The fourth does, because a policy anchored on a
signer's public key cannot survive that key being stolen, and the module's own
docstring calls it "expected trust-root failure". `tests/test_bypass.py` then
asserts that exactly one probe activated and that it is the one declared as a
limitation — so a newly-working bypass fails the suite, and the admission cannot
be quietly removed without the test noticing either.

**The artifact discipline is the second thing.** "Every number the paper reports
is an aggregation over sealed per-case transcripts, so **the whole paper can be
checked without an API key, a database server, or a dataset download**."
`verify_paper_claims.py` pairs "each figure as printed in the paper with a
recomputation from a sealed run, and fails if either half moves" — which catches
a silently corrected number as readily as a corrupted run. Verification and
regeneration are deliberately decoupled, "so you can confirm what we computed
before deciding whether to re-run generation."

**The bitemporal design is expressed as an interface rather than a schema.** The
`QuerySystem` protocol makes both instants mandatory — `query(subject,
attribute, *, valid_at, transaction_at)` — and the baselines are then defined by
which one they discard. `AppendOnlyBaseline` is built by filtering the event
stream to `INGEST` only, so it "[i]gnore[s] revision, expiry, and purge
operations"; the weaker comparators accept `valid_at` and execute `del valid_at`
before answering. Every system in the comparison is handed the same two
instants, and the ablation is what each one refuses to use.

## 2. Mental Model

A **belief** is an event, not a row, and it carries who asserted it.

An **authority** is a rank, and below the minimum the evidence cannot act at all.

A **baseline** is the oracle with one axis deleted, literally.

A **purge** destroys a key and leaves a receipt; the ciphertext stays in history.

A **probe** that works is published beside the ones that fail.

```mermaid
%% caption: beliefs are appended as events carrying an authority rank and a signed tenant envelope, the projection is rebuilt at a pair of instants, erasure destroys a per-belief key rather than rewriting history, and the adversarial probes include the one that succeeds
flowchart TB
    IN["a claim arrives"] --> ENV["EvidenceEnvelope: belief + tenant +<br/>Ed25519 signature over it"]
    ENV --> GATE{"authorize_action(envelopes, *, tenant, at)<br/>tenant is keyword-only, no default"}
    GATE -->|"any envelope's tenant differs"| R1["refused: cross-tenant evidence"]
    GATE -->|"belief not valid_at(action time)"| R2["refused: evidence not valid at action time"]
    GATE -->|"no sources"| R3["refused: missing source provenance"]
    GATE -->|"AUTHORITY_RANK below VERIFIED_TOOL"| R4["refused: insufficient authority<br/>INFERRED=0 EXTERNAL=1 USER=2<br/>VERIFIED_TOOL=3 SYSTEM=4"]
    GATE -->|"signature fails"| R5["refused: invalid signature"]
    GATE -->|"low authority laundered through<br/>a high-authority derivation"| R6["refused: untrusted derivation lineage"]
    GATE -->|"all checks pass"| OK["allowed"]
    OK --> LEDGER[("append-only event ledger —<br/>append refuses a duplicate event_id")]
    LEDGER --> REBUILD["rebuild(transaction_at) → projection<br/>verify_rebuild re-derives it to check"]
    REBUILD --> Q["QuerySystem.query(subject, attribute,<br/>*, valid_at, transaction_at)"]
    Q --> ORACLE["the bitemporal oracle uses both"]
    Q --> BASE["baselines: AppendOnly filters events to INGEST only;<br/>the weaker ones run 'del valid_at' and answer<br/>from transaction time alone"]
    BASE -.->|"every comparator gets the same two instants,<br/>so the ablation is what each refuses to use"| ORACLE
    PURGE["erasure"] --> PS["ProtectedEventStore: payload encrypted<br/>under a per-belief key"]
    PS --> KILL["destroy the key, append<br/>destroyed_key_sha256 receipt"]
    KILL -.->|"metadata, validity, lineage and ciphertext<br/>stay auditable; two-phase with a journal and<br/>recover_redactions for an interrupted purge"| KEPT["history is not rewritten"]
    KILL -.->|"nothing on the ingest path reads the receipts,<br/>so re-asserting an erased value is a new belief"| NOTOMB["a deletion record, not a tombstone"]
    PROBES["run_bypass_probes()"] --> P1["cross_tenant_replay — must not activate"]
    PROBES --> P2["signed_claim_tamper — must not activate"]
    PROBES --> P3["expired_signature_replay — must not activate"]
    PROBES --> P4["compromised_trusted_signer —<br/>ACTIVATES, expected_limitation=True"]
    P4 -.->|"the test asserts exactly one probe activated<br/>and that it is the declared one, so a new bypass<br/>fails the build and the admission cannot be deleted"| HONEST["the attack that works is published"]
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `src/temvera/model.py` | The belief, its two time axes, and the authority enum |
| `src/temvera/store.py` | The append-only ledger, rebuild, verify, and redaction |
| `src/temvera/protected_store.py` | Per-belief encryption and erasure by key destruction |
| `src/temvera/governance.py`, `security.py` | Signed envelopes, authority ranking, lineage laundering |
| `src/temvera/bypass.py` | Four adversarial probes, one of which is meant to succeed |
| `src/temvera/evaluation.py` | The oracle and the baselines defined against it |
| `experiments/`, `scripts/` | Sealed runs, and the scripts that recheck the paper from them |

## 4. Essential Implementation Paths

`src/temvera/bypass.py:51-56` with `tests/test_bypass.py:8-11` — the published
limitation, and the assertion that keeps it the only one.

`src/temvera/evaluation.py:14-24` — both instants made mandatory in the
protocol, which is what makes the ablations comparable.

`src/temvera/evaluation.py:45-51` — `del valid_at`, an ablation written as one
statement.

`src/temvera/governance.py:69-97` — six refusals in order, each with the reason
it returns.

`src/temvera/protected_store.py:14-21` — keeping secrets out of Git history
while leaving the ledger auditable.

`src/temvera/store.py:109-175` — a two-phase redaction with a recovery path.

## 5. Memory Data Model

A `Belief` carries subject, attribute and value; `valid_from` and `valid_to` for
world time; `recorded_at` and `last_confirmed_at` for the store's own time; an
`Authority`; `sources`; `derived_from` lineage; a status; and a supersession
link. `MemoryEvent` wraps it with an operation — ingest, revision, expiry, purge
— and the ledger of events is the store, with the queryable projection rebuilt
from it at a chosen transaction instant.

## 6. Retrieval Mechanics

Exact, lexical and vector retrieval over the rebuilt projection, with calibrated
fusion and reranking described in the research program. Every query takes both
instants, so point-in-time retrieval is the default interface rather than an
extra method.

## 7. Write Mechanics

Ingest is gated before it lands: signature, tenant, validity at action time,
source presence, authority rank, and derivation lineage, each returning its own
reason string. The ledger refuses a duplicate `event_id`. Revision and expiry
are new events rather than edits, so the projection changes and the history does
not.

## 8. Agent Integration

A `temvera` CLI over both halves — `generate` and `benchmark` for the local
deterministic substrate, `verify-artifacts` for the sealed runs — plus adapters
for the external systems the paper measures. There is no server and no MCP
surface; this is a research package.

## 9. Reliability, Safety, and Trust

The strong parts are the refusal-with-reason gate, the signed envelopes, the
published bypass, and an erasure design that answers the usual objection to
append-only storage in Git. The honest weak parts are stated by the project
itself: no production readiness, a provisional API, and claims outside the
frozen fixtures held as hypotheses.

## 10. Tests, Evals, and Benchmarks

Thirty sealed runs, 87 printed figures each paired with a recomputation, a
deterministic test suite, and a lifecycle benchmark that the README is careful
to call "a harness identifiability check, not a performance or novelty result."
The forgetting evaluation adapts a public operation contract rather than
inventing a private one.

## 11. For Your Own Build

Publish the probe that works. A suite of attacks that all fail is a suite that
has not been pushed hard enough, and an expected-limitation flag with a test
behind it is how you keep the admission from decaying.

Make both instants mandatory in the query signature. If `as_of` is optional,
most callers will omit it and the path will rot; if it is required, a system
that ignores it has to say so with a statement you can point at.

Separate verifying what was computed from re-running the computation. The first
should need nothing but the repository.

## 12. Open Questions

Whether the deletion receipts should be consulted on ingest. The paper is about
deletion semantics, and the substrate's own erasure leaves a record that nothing
reads back, so a value destroyed on Monday can be re-asserted on Tuesday without
contradiction.

Whether tenant scoping is meant to reach retrieval. It is enforced where
evidence acts, which is the higher-stakes path, but a search that returns
another tenant's belief without authorizing it has still disclosed it.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `src/temvera/bypass.py:51-56` | Four probes, and the one that is supposed to succeed |
| `tests/test_bypass.py:8-11` | The assertion that keeps the admission honest |
| `src/temvera/evaluation.py:14-51` | Two mandatory instants, and baselines that discard one |
| `src/temvera/governance.py:69-97` | Six refusals, each with its reason |
| `src/temvera/protected_store.py:14-21` | Erasure that survives an append-only history |

## History

**2026-09-16** — [`75243a3dbc3dfeda3613fb69e940c774f5ff4e5b`](https://github.com/suanlab/temvera/commit/75243a3dbc3dfeda3613fb69e940c774f5ff4e5b) — first reading, at a commit dated 13 September 2026. Screened before opening, from a shallow clone: four files scanned, no auto-run surfaces, no build-time execution points, one unpinned dependency surface and one dependency file inside the seven-day cooldown. `AGENTS.md` and `CLAUDE.md` are addressed to a reading agent and were recorded as data. Nothing was installed, built or run, and none of the paper's verification scripts were executed, so the artifact claims described here are read from the repository rather than reproduced.

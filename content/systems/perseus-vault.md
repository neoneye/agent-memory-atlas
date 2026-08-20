---
title: "Perseus Vault"
eyebrow: "Claims audited against artifacts"
description: "A local-first vault whose published benchmark means recompute exactly from committed per-run reports, whose self-audit retires the claims it cannot back, and whose rejected-value tombstone stores a digest rather than the value it refuses."
root: ../..
page_kind: system
source_name: "Perseus-Computing-LLC/perseus-vault"
source_url: https://github.com/Perseus-Computing-LLC/perseus-vault
revision: 1bf7041e428a7302281c67f5d597a06f33d38cce
revision_url: https://github.com/Perseus-Computing-LLC/perseus-vault/commit/1bf7041e428a7302281c67f5d597a06f33d38cce
analyzed_at: 2026-08-20
capabilities: "tombstone, trust_state, bitemporal, scope_enforced, audit_log, human_review, negative_eval"
stack_storage: "sqlite"
stack_retrieval: "lexical, vector"
stack_source: "seeded"
capability_evidence:
  tombstone: "entity store — remember-path write gate | src/db.rs | normalize_rejected_value + rejected_value_digest against rejected_value_tombstones | src/db.rs::rejected_value_tombstone_blocks_same_value_under_any_key_in_scope"
  trust_state: "entity store | src/models.rs | epistemic_state, schema v27 vocabulary candidate/verified/corroborated/rejected/defensively_recalled | src/db.rs::recall_filters_by_epistemic_state_on_all_paths"
  bitemporal: "entity store | src/schema.rs | valid_from_unix_ms and valid_to_unix_ms beside recorded_at_unix_ms | CI Bi-temporal gate"
  scope_enforced: "entity store — recall and journal listing | src/db.rs | workspace_hash predicate on recall; get_recent_journal(workspace_hash, limit) since #877 | src/db.rs::rejected_value_tombstone_scopes_isolate_workspaces"
  audit_log: "entity store — hash-chained journal | src/db.rs | journal() chaining prev_hash from genesis | src/db.rs::purge_erases_history_and_redacts_journal_for_purged_entities"
  human_review: "admission — an operator decision recorded on the entity it admits | src/tools.rs | `admission_decide` refuses any decision that is not `approve` or `reject` (:1854) and routes an approval through `.approve(reason)` (:1977), with `reviewable_write_result` (:29) marking a write reviewable rather than settled | none — no committed test names the approval path"
  negative_eval: "entity store — purge and journal redaction | src/db.rs | purge_erases_history_and_redacts_journal_for_purged_entities, paired with purge_does_not_redact_other_workspace_live_journal_rows | both are the tests"
matrix:
  memory_unit: "An entity — category, key, JSON body — carrying status, type, layer, certainty, verified flag, decay score, and bi-temporal bounds"
  storage: "One SQLite file with FTS5, AES-256-GCM bodies encrypted by default on a fresh install, an entity history table, a hash-chained journal, sign-bit embedding signatures, and a rejected-value tombstone table holding digests"
  retrieval: "Hybrid BM25 (FTS5) plus dense vectors fused by RRF, with a Hamming prefilter on embedding sign bits and workspace filters applied in the query; every recall carries a `RecallOutcome` naming why it is empty or degraded"
  write: "MCP tool calls into a Rust binary; supersession writes history rows and sets `superseded_by`, with a trust-admission path in front"
  update_delete: "Supersede, correct, demote, archive with a reason, forget, and purge — purge erases history and redacts the journal; a rejected value is refused on every remember-path write by a digest-keyed tombstone, with an audited trusted override"
  scoping: "`workspace_hash` on entities and journal rows, a `(category, key, workspace_hash)` identity index, and a `visibility` column; applied in entity read queries, and — as of this pin, not the previous one — in the journal listing too"
  integration: "An MCP stdio server with ninety canonical tools, plus LangGraph, CrewAI, AutoGen, PydanticAI and Praison adapters; one binary, no services"
  background: "Decay ticks, cohere and dream passes, consolidation, hygiene scans, community detection"
  trust: "A discrete `status`, a separate `epistemic_state` (`candidate`/`verified`/`corroborated`/`rejected`/`defensively_recalled`), a `verified` flag, a `certainty` float and a `source` field — four distinct axes rather than one score"
  strengths: "Three full benchmark runs per prompt variant with a config stamp, published means that recompute exactly, a claims audit that retires what it cannot back, and a blocking memory-quality gate whose required categories read like an acceptance suite"
  risks: "A database created before the default flipped stays plaintext until an explicit `init --rekey`, the encryption key sits beside the database it protects, and the new capability split is documented fail-open when no authority manifest exists"
---

## 1. Executive Summary

Perseus Vault is roughly 63,000 lines of Rust over 666 commits, MIT-licensed,
shipping one binary and one SQLite file with no services. It exposes memory
through an MCP stdio server plus LangGraph, CrewAI and AutoGen adapters, stores
entities with bi-temporal bounds, retrieves with BM25 and dense vectors fused by
RRF, and encrypts bodies with AES-256-GCM by default on a fresh install. It
carries all seven of this atlas's capability marks.

That would make it a substantial report on mechanism alone. It is a more
interesting one because of how it handles its own claims.

**It ships a `CLAIMS-AUDIT.md` that retires claims it cannot back.** The file
audits the README against code and committed artifacts, and its 2026-07-16 entry
records what that cost:

- *"Retired the 'sub-millisecond recall' entry"* — with the reason stated plainly:
  no committed artifact supported it, and the old justification, bundled offline
  embeddings, *"said nothing about latency."* The replacement is measured and
  cited: FTS5 recall p50 3.14 ms at 10K entities, dense p50 194.5 ms at 1M.
- *"Removed the unbacked 100K-entity insert-rate figure from the README (no
  artifact anywhere in the repo backed it)."*
- Reworded "signed results" to **"content-hashed (sha256)"**, because
  `signature_sha256` is a self-computed content hash *"not a cryptographic
  signature."* Downgrading your own security-adjacent wording is not a common
  edit.
- Clarified that `federate` is a local export and re-import, *"file based, no
  network peers."*

This atlas's [benchmarks page](../../benchmarks/) has spent most of its length on
figures with no traceable artifact. Here is a project that went looking for its
own and deleted the ones that failed.

**Its benchmark discipline is the strongest in the corpus.** The README leads
with 73.8% on LongMemEval against Zep's published 63.8% and Mem0's 49.0%. That
number is the mean of **three independent full 500-question runs**, each with its
own committed report carrying dataset, split, `n_instances`, `mock_llm: false`,
the pinned answerer and judge model snapshots, temperature, retrieval mode and
`k`, commit, binary version, platform, hardware, elapsed time and a run
signature. Recomputed from those three artifacts at this commit:

```text
qa_report.json        0.736
qa_report_seed2.json  0.750
qa_report_seed3.json  0.728
mean                  0.738   ← the published figure, exactly
```

**And the headline is the lower of its two numbers.** The same directory holds
three `official-cot` runs meaning **79.0%** (0.800 / 0.786 / 0.784, also
recomputed exactly), and the README quotes the plain-prompt 73.8% instead. The
comparison document explains why in a section headed *"Caveats (read before
quoting the number)"*: the two prompts are different official conditions,
*"every quote must carry its `answer_prompt` label"*, and — on the competitors —
*"Zep's publication does not state their variant; flag that when comparing, never
blend."* Zep's and Mem0's figures are labelled as their publishers' claims and
cited to an issue rather than reproduced as head-to-heads, which is the reporting
policy this atlas credits [Daimon](../daimon/) for writing down, implemented.

**And the count claim is derived rather than asserted.** The audit's check is
`scripts/registry_metadata_check.py`, which extracts the embedded registry
literal from `src/mcp.rs` and parses it exactly as the Rust implementation does,
rather than grepping for a name pattern. From that one derivation it asserts the
same number appears in `README.md`, `CLAIMS-AUDIT.md`, `glama.json`,
`manifest.json` and `server.json`, and it fails on a duplicate name or a
non-canonical one. Run at this commit it exits zero and prints
`{"canonical_tools_list_count": 90, "compatibility_manifest_count": 270,
"registry_count": 90}`.

What makes it a check rather than a documented command is
`.github/workflows/mcp-registry.yml`, whose `verify-registry` job runs on every
`push` and `pull_request` and executes both the parser and the Rust uniqueness
test. The audit describes it in those terms: *"this parser is
formatting-insensitive and runs in CI"*.

That is the difference between a count that agrees today and a count that cannot
silently drift, and the second is the property worth having. The canonical/legacy
split does not live in the literal — `tool_registry_base` calls the `mimir_*`
names *"an implementation migration detail"* and `legacy_alias_tool` synthesizes
aliases by prefix rewriting at advertise time — so the parser rewrites a `mimir_`
prefix to `perseus_vault_` before counting, and rejects the result if any name
survives that is not canonical. The advertised surface remains a runtime decision,
and `compatibility_manifest_count` is the parser's own name for it: 270, three
aliases per canonical tool.

**A fresh install encrypts, and a test says what that means.** The first default
startup creates an owner-only key and an encrypted canary row.
`tests/encryption_bootstrap.rs` pins the behaviour rather than the intent: the key
file must be mode `0600` and hold exactly 32 bytes, the canary must be
established, and the stored body must **not** equal the plaintext JSON that was
written — `assert_ne!(stored, r#"{"note":"bootstrap encrypted body"}"#)`. A second
case covers the opt-out, asserting that an explicit plaintext choice suppresses
key creation and stores the body verbatim.

**Two things the default does not cover, and both are stated upstream.** A
database created before the default flipped stays plaintext until an explicit
`init --rekey`, so "encrypted by default" is a claim about fresh installs and the
claims audit says exactly that. And the key sits beside the database it protects,
at owner-only permissions — which defends the file carried off a disk, not an
attacker who already reads the filesystem as that user. The threat model is
narrower than the banner, disclosed, and the narrower claim is the one to quote.

## 2. Mental Model

An entity's standing is three separate things — a discrete `status`, a boolean
`verified`, and a `certainty` float — over a bi-temporal record that keeps its
own history.

```mermaid
stateDiagram-v2
    [*] --> candidate: trust admission
    candidate --> active: accepted
    active: status active<br/>verified 0 or 1, certainty float
    active --> active: correct, score, promote, demote
    active --> superseded: supersede writes a history row<br/>and sets superseded_by
    superseded: valid_to and invalidated_at closed<br/>prior version readable via as_of
    active --> deprecated: demote
    active --> archived: archive with archive_reason
    archived --> active: restore
    superseded --> [*]: purge erases history<br/>and redacts the journal
    archived --> [*]: forget

    note right of superseded
        valid_from / valid_to is world time.
        recorded_at / invalidated_at is
        transaction time. Both are columns,
        on entities and on entity_history.
    end note
```

The schema comments say it directly — `valid_from_unix_ms` is *"when the fact
became true in the world"* and `recorded_at_unix_ms` is *"transaction time: when
Mneme first knew it"* — which is the distinction the
[bi-temporal fact validity](../../patterns/bi-temporal-fact-validity/) pattern
exists for, present on both the live table and its history.

What the diagram has no state for is a value that was judged wrong. `purge` and
`forget` remove records; nothing records the *content* so a later ingest cannot
re-assert it. That is the one mark missing and the one gap the rest of the design
makes conspicuous.

## 3. Architecture

One Rust binary over one SQLite file. Tables: `entities` and `entity_history`,
`journal` with `audit_chain_state`, `communities`, `keystones`, `artifacts` and
`artifact_bindings`, `agents`, `authority_manifests` with
`authorized_actions` and `authorized_action_leases`, `dedup_signatures`,
`encryption_canary`, and a `state` key-value table.

Entity columns carry the whole model: `category`, `key`, `body_json`, `status`,
`type`, `tags`, `decay_score`, `retrieval_count`, `layer`, `topic_path`,
`archived` with `archive_reason`, `links`, `verified`, `source`, `certainty`,
`always_on`, `workspace_hash`, `visibility`, the four temporal columns, an
`embedding` blob and an `emb_sig` sign-bit signature.

### Deployment and ergonomics

`curl | sh` to `~/.local/bin`, then `serve --db`. No Docker, no Postgres, no
network dependency in `Cargo.toml`. Encryption requires an explicit `init` that
creates the key and the canary row; `serve` warns when an encrypted vault is
opened without a key.

The cost of the single-file model is the usual one and the project does not hide
it: `federate` is export and re-import rather than peer sync, so multi-machine
use is a file operation.

## 4. Essential Implementation Paths

### Three runs, one signature, and a caveat section

`benchmark/longmemeval/` holds `run.py`, the per-run reports, `COMPARISON.md` and
a retrieval diagnostic. Each report is a full config stamp rather than a score,
and the comparison document records the provenance per run — *"plain run 2
signature `929623670d8bcc67…`; CoT runs `20327b31b5940f58…` / `7c8ce1b406c0cc4b…`
/ `eb848e786677a8d1…` — each over the per-question verdict set."*

The design decision worth stealing is that the answer prompt is *"folded into the
run signature (a CoT number can never be silently blended with a plain-prompt
one)"*. Blending incomparable conditions is the most common way a benchmark table
misleads without anybody lying, and making the condition part of the hash removes
the possibility rather than warning against it.

Publishing per-question-type results is the second. The committed report shows
`single-session-user` at 0.957 and `single-session-preference` at **0.300** on
30 questions. A weak category is visible because they published the breakdown;
in most of this corpus it would be inside the headline average.

### The count, derived from source and asserted in CI

Three surfaces say 65. The audit's designated command returns 76, and the tool
names it lists are unmistakably real — `recall`, `supersede`, `correct`,
`forget`, `purge`, `bitemporal`, `valid_at`, `operator_review`, `journal`,
`beliefs`, `conflicts`, `promote`, `demote`, `keystone_get`, and so on.

**The instructive part is where the fix landed.** This is a project that retired
a latency claim for lack of an artifact and downgraded "signed" to
"content-hashed" on its own initiative. The claim that had gone stale was the one
with a check attached — because a command written down in a Markdown file
runs only when somebody remembers, and the discipline that catches unbacked
claims is a different discipline from the one that keeps backed claims current.
It is the same failure this atlas has recorded in its own count sweeps: the
guard exists, and nothing runs it.

### Trust as three axes, not one float

`status` carries `active`, `candidate`, `superseded`, `deprecated`, `compacted`,
`dead` and `useful`; `verified` is a separate boolean; `certainty` is a separate
float; `source` records where it came from. `src/trust_admission.rs` gates what
enters.

Keeping "we checked this" apart from "how confident are we" apart from "what
state is this record in" is a distinction most systems here collapse, and it is
what makes the `trust_state` mark straightforward: `candidate` and `superseded`
are states that withhold a memory from being treated as current, expressed as a
column rather than inferred from a number.

### A tombstone that stores the digest, not the value

`rejected_value_tombstones` is keyed on `(workspace_hash, subject, predicate,
value_sha256)` and carries `reason`, `evidence_ref`, `author_agent_id`, a
creation timestamp and an optional expiry. The value itself is never written —
only `value_sha256`, over a normalized form:

```rust
fn normalize_rejected_value(value: &str) -> String {
    let canonical = match serde_json::from_str::<serde_json::Value>(value) {
        Ok(v) => v.to_string(),
        Err(_) => value.to_string(),
    };
    canonical.split_whitespace().collect::<Vec<_>>().join(" ").to_lowercase()
}
```

JSON is canonicalised when it parses, whitespace is collapsed, and the result is
lower-cased — so a re-indented body, a re-ordered object and a case variant all
hash to the same tombstone. That is the normalization the
[rejected-value tombstone](../../patterns/rejected-value-tombstone/) pattern
calls the part where the real work is, done in nine lines.

Storing only the digest is the part worth taking. The pattern page lists as a
tradeoff that *"the tombstone itself can contain sensitive data and must follow
deletion policy"* — a rejection record for a leaked credential is a copy of the
credential. A digest refuses the value without retaining it, and the doc says so
in the same terms: the raw value is never stored, so *"rejection records cannot
leak the content they suppress."*

`is_value_rejected` runs the lookup as `workspace_hash IN ('', ?1)`, so a
tombstone written with an empty workspace is global and a named one binds to its
workspace, and one workspace's rejection cannot censor another. Expired rows are
deleted on the way past.

The enforcement point is `remember_impl`, with the reach stated in a comment:

> scoped rejected-value tombstones are enforced on every remember-path write
> (agent remember, capture, ingest, connectors, derived writers) so a
> corrected/deleted value cannot be laundered back in under a new key. A
> deliberate trusted override passes `allow_rejected=true` and is journaled
> below for audit.

Two details separate this from the other holders. The lookup keys on the
**predicate and the digest and not the subject**, so a rejected value is refused
under any key in scope — broader than the identity index it is written under, and
named in a test as `rejected_value_tombstone_blocks_same_value_under_any_key_in_scope`.
And the override is not a bypass flag but an audited act, journaled in the same
hash-chained ledger as everything else, which is the shape the pattern page asks
for when a trusted human correction must win.

Four tests cover it: blocking under any key in scope, workspace isolation,
normalization and expiry, and — at the MCP layer —
`rejected_value_tombstones_block_laundering_and_support_audited_override`, whose
name is the whole mechanism.

### Deletion that is tested to have happened

`purge_erases_history_and_redacts_journal_for_purged_entities` seeds an entity
with fake PII, supersedes it several times so `entity_history` accumulates, then
purges and asserts the history rows are gone, the journal rows are marked
`redacted`, and `category`, `key` and `entity_id` are scrubbed to empty strings.
A companion test,
`purge_does_not_redact_other_workspace_live_journal_rows`, asserts the blast
radius stops at the workspace boundary.

An audit log that reproduces the content a user asked to delete is a real hazard
and one this atlas has flagged elsewhere. Testing both that the secret is gone
and that the erasure did not over-reach is the pair of assertions the problem
needs, and it is why the `negative_eval` mark applies.

## 5. Memory Data Model

The unit is an entity keyed by `(category, key, workspace_hash)` — an identity
index the schema comments date to issue #339 and credit with *"~66x on
workspace-scoped browse at 30k rows."*

`entity_history` mirrors the entity columns and adds the transaction interval,
with a comment describing it as `[recorded_at_unix_ms, invalidated_at_unix_ms)`
and `superseded_by` pointing at the replacement. So a superseded value is
readable as of a past instant rather than lost, and `mimir_as_of`,
`mimir_valid_at`, `mimir_recall_when`, `mimir_timeline` and `mimir_history` are
the tools over it.

The `journal` is hash-chained — SHA-256 plus a keyed MAC, with `audit_chain_state`
holding the chain head — and rows are stamped with `workspace_hash` at write time
*"so purge can scope journal redaction per-workspace."* That is an append-only
mutation record in the system's own store with a tamper-evident chain, which is
the `audit_log` mark and a strong instance of it.

What is absent is the tombstone. `forget` and `purge` are removals; supersession
records a replacement. Nothing is keyed on the rejected *value*, so a later
ingest of the same wrong content creates a new entity, and the
[rejected-value tombstone](../../patterns/rejected-value-tombstone/) page's
argument applies unchanged.

## 6. Retrieval Mechanics

FTS5 for lexical, dense vectors for semantic, fused by reciprocal rank. The
performance detail worth noting is `emb_sig`: a sign-bit signature of each
embedding, one bit per dimension, so `dense_search` Hamming-prefilters candidates
*"instead of reading every full embedding blob once the vault is large enough."*
Written on store and backfilled by a migration.

Scope reaches the query: `workspace_hash` appears in read predicates across
`tools.rs`, `communities.rs` and the trust-admission path, alongside a
`visibility` column. The usual caveat applies — the caller supplies the workspace
— so the mark certifies the key reaches the query, not that a caller cannot pass
a different one.

Measured latencies, from the artifacts the claims audit points at rather than
from prose: FTS5 recall p50 3.14 ms at 10K entities; dense recall p50 194.5 ms at
1M entities on the uniform arm.

## 7. Write Mechanics

Writes arrive as MCP tool calls and are synchronous against SQLite. Supersession
writes a history row, closes the prior interval and sets `superseded_by`;
`correct`, `promote`, `demote` and `score` move the trust axes; `archive` sets a
flag and a reason; `forget` and `purge` remove.

Background work is extensive — decay ticks, `cohere`, `dream`, `consolidate`,
`hygiene`, community detection — and `score` sets a persistent importance floor
that decay and cohere respect, with the reasoning in the schema comment: *"an
explicit score survives the recency-based recompute instead of being erased by
the next tick (fidelity > recency)."* An explicit human judgement outranking an
automatic recompute is the right default and is written down where the column is
declared.

### Operational cost

No model in the read path; embeddings are bundled ONNX and run locally. The
background passes are the variable cost and several are LLM-assisted. Storage
grows with history, which is the price of the bi-temporal model, and `purge` is
the release valve.

## 8. Agent Integration

An MCP stdio server implementing `initialize`, `tools/list` and `tools/call`,
with adapters committed for LangGraph, CrewAI and AutoGen. Legacy `mimir_*` and
`mneme_*` aliases remain callable and are counted separately from the canonical
set — and `mimir_alias_usage` exposes counters for canonical versus alias calls,
so a maintainer can see whether the old names can be retired. Instrumenting a
deprecation rather than announcing one is a small, unusually practical touch.

## 9. Reliability, Safety, and Trust

Strengths:

- **A claims audit that retires unbacked claims**, naming the retired figure, the
  reason, and the artifact that replaced it.
- **Three full runs per benchmark condition**, each with a complete config stamp,
  and published means that recompute exactly from the committed reports.
- **The answer prompt folded into the run signature**, so incomparable conditions
  cannot be blended.
- **Competitor figures labelled as published claims** and cited, not reproduced
  as head-to-heads.
- **Per-question-type results published**, including the weak category.
- **Bi-temporal columns on the live table and its history**, with `superseded_by`.
- **A hash-chained journal** with a keyed MAC and per-workspace stamping.
- **Purge tested both ways** — the content is gone, and the erasure did not cross
  the workspace boundary.
- **Trust split into status, verified and certainty**, three axes rather than one.
- **An explicit score that outranks the decay recompute**, with the rule stated at
  the column.
- **Encryption on by default for a fresh install**, with a committed test
  asserting the stored body is not the plaintext.
- **A rejected-value tombstone storing a digest rather than the value**, refused
  on every remember-path write, with a trusted override that is journaled.

Gaps:

- **The tombstone is enforced on the predicate and the value, not the subject.**
  A rejected value is blocked under any subject in scope, which is deliberate and
  named in a test — and it is the pattern page's first tradeoff, a normalization
  that can refuse a legitimately different fact, taken further than any other
  holder here takes it.
- **A tombstone can expire.** `expires_at_unix_ms` is honoured and reaped on
  lookup, which the pattern page's round-8 lesson calls the way a tombstone stops
  being one. Nothing in the default path sets it, so this is a facility rather
  than a live gap.

  The sequence nothing yet covers end to end is the one the project's author
  named: reject value A, replace it with B, re-ingest A through a different write
  path, run the background consolidation passes, and check that A remains
  rejected. The committed tests cover the write paths and the override; the
  background passes are the untested leg.
- **A pre-existing database stays plaintext** until an explicit `init --rekey`,
  so the default covers fresh installs rather than upgrades; and the key lives
  beside the database at owner-only permissions.
- **Federation is file-based**, so the multi-machine story is manual.

## 10. Tests, Evals, and Benchmarks

592 `#[test]` functions inline across `src/`, plus three integration files under
`tests/`. Nothing was run for this review — the suite is Rust and the benchmark
harness calls `gpt-4o-2024-08-06` for both answering and judging, so reproducing
the LongMemEval figure means paying for 500 questions × 3 runs × 2 model calls.

**What was verified is the arithmetic, and it holds.** The published 73.8% and
79.0% are the exact means of the three committed reports in each condition. That
is a weaker claim than a re-run and a much stronger one than the corpus norm: it
establishes that the headline figure is a function of artifacts in the repository
rather than a number in a README, and that the runs behind it were three rather
than one.

`benchmark/` also carries scale, contention, temporal, recall, quality, beam,
context-selection and embedding-quantization suites with committed JSON, and
`GAUNTLET.md` over the top. `PERF.md` and the claims audit both point at
artifacts rather than restating figures.

The untested surface is the one the tool-count finding exposes: nothing in CI
runs the audit's verification command, so a claim with a documented check went
stale anyway.

## 10a. Three mechanisms added since the previous reading

125 commits and roughly 109,000 added lines in `src/` alone sit between the two
pins. Most of it extends machinery this report already describes; three pieces
are new in kind and belong here.

**A zero-token write gate.** `src/write_gate.rs` is a deterministic precheck the
provider flow calls *before* LLM enrichment: content-hash dedup, key
supersession, and a stored-signature near-duplicate scan return `Store`,
`Duplicate`, `Supersede`, `Forget` or `Adjudicate`, and only the last escalates
to a model or an operator. Two properties are stated as contract rather than
left to reading: the gate is **read-only by construction** — it never mutates —
and `Forget` is *"deliberately conservative (only vague/empty notes) so the gate
can never drop a substantive fact"*. Putting the cheap deterministic layer in
front of the expensive one is the [zero-LLM capture](../../patterns/zero-llm-capture/)
pattern, applied to the *decision* rather than to the capture.

**A self-audit that distinguishes "could not check" from "passed."**
`src/verify.rs` re-asserts the store's invariants against a live database over
a `SQLITE_OPEN_READ_ONLY` connection, across eight checks, and its status enum
is three-valued: `Pass`, `Unverified`, `Fail`. The exit contract makes the
middle state load-bearing — **0 all pass, 2 a check could not run (UNVERIFIED,
never PASS), 3 an invariant is violated** — so a verifier that cannot reach a
check reports that rather than reporting success. Findings print `path:key`
only, never values, so running it against a real store does not spill one. This
is the same discipline the benchmarks page credits `a40-labs/memory` for, and
the two are the only instances in the corpus.

**A memory red-team harness, honest about being a skeleton.**
`benchmark/redteam/` aims three published attack families — MAFIA,
MemCollusion and Chronos — at the recall and admission surfaces, with a
`manifest.json` fixing budgets (300 probes, 90 poison writes) and an outcome
taxonomy, worked probe and scenario datasets, and `harness.py` carrying
deterministic validators for the four MemCollusion construction constraints
plus sha256 pinning of harness and datasets. Its README opens by calling itself
a **skeleton**, and lists what exists rather than what it found: no results are
committed and no run is claimed. An adversarial suite for a memory store is
something this atlas has asked for and not found; this is the first, and it has
not been run.

## 11. For Your Own Build

### Steal

- **Keep a claims audit file and let it delete things.** Naming a retired claim,
  why it failed, and what replaced it is worth more than any number the README
  could have kept.
- **Run your benchmark three times and commit all three.** A single run is a
  sample; a mean with its members committed is a result, and it lets a reader
  recompute your headline without rerunning anything.
- **Fold the condition into the run signature.** If the prompt variant is part of
  the hash, a chain-of-thought number cannot be quoted beside a plain one by
  accident.
- **Publish the per-category breakdown**, including the category you do badly on.
  It costs a table and it is the difference between a score and a result.
- **Cite competitors as their publishers' claims.** Reproducing someone else's
  number as a head-to-head asserts a comparability you did not establish.
- **Split trust into status, verified and confidence.** One float cannot express
  "checked and wrong".
- **Let an explicit human score outrank the automatic recompute**, and write the
  rule where the column is declared.
- **Test a deletion in both directions** — the content is gone, and the erasure
  stopped at the boundary.
- **Instrument your deprecation.** A counter for canonical versus alias calls
  tells you when the alias can go.

### Avoid

- **Documenting a verification command and not running it.** A check that lives
  in Markdown runs when somebody remembers; the count it guards went stale by
  eleven while the audit around it stayed sharp. Put it in CI or accept that it
  is a comment.
- **Treating supersession and purge as protection against re-assertion.** Both
  are keyed on the record. The next ingest of the same wrong value creates a new
  one.
- **Leaving a count's only check in a Markdown file.** The fix here was to derive
  the number from source and run the derivation in CI; until that happened the
  audit around it stayed sharp while the count drifted.

### Fit

Right if you want a single-binary local memory with real correction semantics —
bi-temporal history, supersession with a readable past, a tamper-evident journal,
tested purge — and you would rather read a project's own audit of its claims than
take its README on faith. All seven marks is a position three other systems here
hold.

Wrong if you need multi-machine memory without manual file movement, or
encryption on a database that predates the default. The rejection guarantee is
the most privacy-careful instance of one in the atlas — a digest rather than the
value — and the open question about it is reach rather than existence: the
background consolidation passes are the leg no committed test walks.

## 12. Open Questions

- Do the consolidation, cohere and dream passes write through `remember_impl`,
  and therefore through the tombstone check? That is the one reach the comment
  claims and no committed test walks.
- The tombstone matches on predicate and digest without the subject. What is the
  false-positive surface — the same value legitimately true of two subjects under
  one predicate?
- Nothing sets `expires_at_unix_ms` on the default path. Is a lapsing rejection
  intended, or is the column there for a caller that does not exist yet?
- `single-session-preference` scores 0.300 in the committed report. Is that a
  retrieval failure, a prompt failure, or a category the design does not target?
- Does `emb_sig` Hamming prefiltering change recall, and is there an artifact
  measuring the loss rather than the speedup?
- What would it take to make `federate` a sync rather than an export?

## Appendix: File Index

- Schema and temporal model: `src/schema.rs` (`entities`, `entity_history`,
  `journal`, `audit_chain_state`, `encryption_canary`, the `valid_*` and
  `recorded_at`/`invalidated_at` columns).
- Tools and review surface: `src/mcp.rs` (registry),
  `src/tools.rs` (`handle_operator_review`, recall, supersede, correct, purge).
- Trust admission: `src/trust_admission.rs`.
- Storage and deletion tests: `src/db.rs`
  (`purge_erases_history_and_redacts_journal_for_purged_entities`,
  `purge_does_not_redact_other_workspace_live_journal_rows`).
- Benchmarks: `benchmark/longmemeval/` (`qa_report.json`, `qa_report_seed2.json`,
  `qa_report_seed3.json`, the three `qa_report_cot*.json`, `COMPARISON.md`,
  `run.py`), `benchmark/scale/report.json`, `benchmark/lambda/results/`,
  `benchmark/GAUNTLET.md`, `PERF.md`.
- Claims: `CLAIMS-AUDIT.md`; encryption behaviour: `docs/ENCRYPTION.md`.
- Integrations: `integrations/langgraph/`, `integrations/crewai/`,
  `integrations/autogen/`.

## History

**2026-08-20** — [`1bf7041e428a7302281c67f5d597a06f33d38cce`](https://github.com/Perseus-Computing-LLC/perseus-vault/commit/1bf7041e428a7302281c67f5d597a06f33d38cce) — re-pinned nine commits on, 46 files and +6,561 lines, most of it under `benchmark/`. Screened again: two auto-run surfaces, one build-time execution point, one manifest inside the cooldown across eight unpinned surfaces; nothing was installed and no benchmark was run. Marks unchanged at seven of seven. **The addition is the artifact this atlas specified and has not built.**

`benchmark/scoped_memory/` is a *portable scoped-memory capability contract*, versioned `perseus-vault-scoped-memory-contract/v1` and described in its own README as *"a capability boundary, not a second memory API"*. Four properties make it worth reading whatever you think of the rest of the system.

- **Scope is bound out of band and the model cannot reach it.** The contract binds `user_id`, `workspace_hash`, `agent_id` and `session_id` supplied by the host, and states that *"model-authored arguments cannot supply or override any of those fields"*; `contract.py:190` returns `_result("deny", "caller_scope_injection")` when they try. *"Scope and policy filtering happens before a ranker receives candidate IDs"*, and `RecordingRanker` exists so a test can prove what the ranker was handed.
- **The outcome vocabulary refuses to collapse an absence into a pass.** `OUTCOMES` is `allow`, `deny`, `scope_mismatch`, `stale_conflict`, `abstain`, `unavailable`, and the README states the rule directly: *"A missing semantic provider or surface is represented as `unavailable`; it is never converted to a fabricated zero or pass."* `test_publication.py::test_failed_surface_is_explicitly_partial_not_zero` pins it.
- **It runs against two surfaces.** `InProcessSurface` is a deterministic reference, and `McpSurface` is an adapter over the shipped `VaultClient` and the canonical MCP tools `recall`, `context`, `get_entity`, `remember`, `correct` and `supersede` — so the same contract exercises a reference implementation and the real system, which is what makes a passing run mean anything.
- **The published artifact is hash-only and stable.** `test_report_is_hash_only_and_repeated_signature_is_stable` asserts the report carries hashes rather than content and that a repeated run signs identically.

Writes require a trusted authority whose capability set includes the operation, a stale expected version fails closed, and corrections and supersessions retain the prior record with a deterministic successor relationship — the same semantics the report describes in the store, restated as an executable contract.

Also at this pin: `benchmark/recall/test_fusion_regression.py` adds conflict-magnet fusion regressions, `test_replay.py` a shared retrieval replay envelope, evidence-sufficiency curves and protocol-comparability lanes under `longmemeval`, corpus inputs certified and redacted before use, proposal-admission writes isolated, and `src/db.rs` and `src/tools.rs` grown by 237 and 157 lines.

**2026-08-19** — [`443239f45d39106169a2f37d193897c609850bd9`](https://github.com/Perseus-Computing-LLC/perseus-vault/commit/443239f45d39106169a2f37d193897c609850bd9) — re-read 125 commits on, roughly 109,000 added lines in `src/` across 69 files. Every one of the seven marks was re-verified at this pin and every one holds, but one evidence record had gone stale under it: `human_review` named `mimir_action_approve` in `src/mcp.rs`, which existed at the previous pin and does not exist at this one. The approval surface is `admission_decide` in `src/tools.rs`, refusing any decision that is not `approve` or `reject`, and the record is re-anchored to it with `none` for its test, because no committed test names the path. Nothing in the previous reading was found stale, so this is an extension rather than a correction: section 10a adds the three mechanisms that are new in kind — `write_gate.rs`, a deterministic read-only precheck that decides Store/Duplicate/Supersede/Forget before any model call and refuses to let `Forget` drop a substantive fact; `verify.rs`, a runtime self-audit whose three-valued status makes `Unverified` a distinct exit code from `Pass`; and `benchmark/redteam/`, an adversarial harness against MAFIA, MemCollusion and Chronos whose README calls itself a skeleton and commits datasets and validators without results.

The remaining growth was read at the level of what it changes about this report's claims rather than line by line, and it changed none of them. The screen reported two auto-run publication manifests — `server.json` and `smithery.yaml`, both registry metadata — plus a `build.rs` and a `Cargo.lock` inside its cooldown; nothing was installed and no test was run. One skew worth recording: `server.json` declares version 2.23.0 while the OCI package it lists pins 2.20.2.

**2026-08-08** — [`60d7ac4fc41bff182a6a53826f0b230bc6b9b785`](https://github.com/Perseus-Computing-LLC/perseus-vault/commit/60d7ac4fc41bff182a6a53826f0b230bc6b9b785) — re-pinned three commits after the previous reading, which was one day old. Nothing was run; the delta is +5,093/-420 lines over 17 files, read against the previous pin.

**A claim in this report was wrong at the pin it was made on, and is retracted.** The scoping row said `workspace_hash` was applied in read queries on entities *and journal rows*. At `4008228` it was not: `get_recent_journal(limit)` selected `FROM journal ORDER BY created_at_unix_ms DESC LIMIT ?1` with no workspace predicate and blanked the field on the way out, under a comment reading *"Not selected by this listing query; purge-scoping metadata only."* A caller in one workspace listing recent journal events received every workspace's. `8e26619` (#877) fixed it upstream: the reader now takes a `workspace_hash`, and the unscoped variant is `get_recent_journal_admin`, gated on an in-process `JournalAdminAuthorization` whose own comment says no public transport mints one. The `scope_enforced` mark stands — entity recall was scoped throughout, and the rubric's mark measures the memory read path — but the matrix sentence overstated it and now says which pin changed it.

**Three mechanisms arrived that the previous reading could not have seen.** `#880` adds an `epistemic_state` column at schema v27 — `candidate`, `verified`, `corroborated`, `rejected`, `defensively_recalled` — explicitly orthogonal to the lifecycle `status`, with `recall_filters_by_epistemic_state_on_all_paths` committed beside it. `defensively_recalled` is the one this atlas has no other instance of: every trust state in the corpus withholds a memory, and this one serves it while framing it as untrusted. `#864` adds a `RecallOutcome` carrying `abstained`, a machine-readable `reason` (`no_match`, `db_unhealthy`, `embedding_unavailable`, `deadline_elapsed`, `partial_arms`), a deadline flag and embedding-backend health — so an empty recall now distinguishes *nothing matched* from *the backend was down*, which the [benchmarks page](../../benchmarks/) records as measured nowhere. And `#865` splits `memory.read`/`propose`/`commit`, types retrieved memory as untrusted below `verified`, and adds versioned per-agent authority manifests; the split is documented **fail-open when no manifest exists**, which is why it is in the risks row rather than the strengths one. The admission evaluator also gained a `proposed` outcome, keeping an unvalidated authoritative claim a reviewable proposal rather than a fact.

**`#878` is the one worth copying.** A memory-quality scorecard, blocking on any pull request touching vault behaviour, whose `release_ready` demands accuracy of exactly 1.0 over a committed 24-case manifest and requires every category to be present: long-horizon recall, contradiction and supersession, shared-memory visibility, adversarial contamination, temporal validity, scope validity, and provenance. That list is close to the acceptance suite this atlas publishes and has never run against anything.

**Said plainly, because the atlas would otherwise be marking its own homework.** These commits use this atlas's vocabulary — admission contract, epistemic trust axis, recall outcome, untrusted recall — and the [rubric](../../methodology/atlas-rubric/) already warns that a mark count partly measures who has read it. Two things bound that here. This report carried all seven marks *before* these commits, so no mark was added by them and none could be. And the commits carry the project's own issue numbers, which is evidence of an internal plan rather than of a checklist. What changed is the prose, and the prose now says when.

**2026-08-07** — [`4008228ee4fb1846bef562d91037b4be11356de4`](https://github.com/Perseus-Computing-LLC/perseus-vault/commit/4008228ee4fb1846bef562d91037b4be11356de4) — one commit past the previous pin, and it adds a file rather than changing one: a 251-line research memo under `docs/research/`. No source, schema, test or manifest moved, so every published claim and all seven marks stand unexamined by this reading rather than re-confirmed by it. Screened first: 2 auto-run surfaces (`server.json`, `smithery.yaml`), 1 build-time exec (`build.rs`), 8 unpinned surfaces and 2 files inside the seven-day cooldown — the same shape as the previous screen, with the auto-run pair still the MCP publication manifests. Nothing was built or run. The memo is worth one sentence because of what it argues rather than what it changes: it reviews five 2026 memory papers and concludes that *"memory is a state machine, not just a search index"*, listing revision, forgetting, temporal validity and provenance as the properties that matter — which is a description of the mechanisms this system already carries marks for, arrived at from the literature rather than from the code. It also repeats the [MemoryAgentBench mislabel](https://arxiv.org/abs/2507.05257) this atlas has traced twice before, citing the benchmark as evaluating *"selective forgetting"* where the repository itself calls that competency conflict resolution.

**2026-08-05** — [`5d6cecf9a5c2a95d90b9e96faadc45fa8ebec601`](https://github.com/Perseus-Computing-LLC/perseus-vault/commit/5d6cecf9a5c2a95d90b9e96faadc45fa8ebec601) — second reading, two commits on. Screened before reading: 2 auto-run surfaces (`server.json`, `smithery.yaml`), 1 build-time exec (`build.rs`), 8 unpinned surfaces, and `Cargo.toml` and `Cargo.lock` both changed the day of the pin. Both auto-run findings predate the previous pin and are MCP publication manifests declaring how a client starts the published image; neither reads outside the tree nor reaches the network with anything it reads. Nothing was built or executed from the checkout — the only thing run was `scripts/registry_metadata_check.py`, which is stdlib Python that reads files in the tree and prints JSON. `6d6c6c8` is titled *"implement Atlas review follow-ups"* and closes three upstream issues; each was verified here against code rather than against the commit message. The tool count is derived rather than asserted: the parser extracts the embedded registry literal from `src/mcp.rs` and parses it as the implementation does, then asserts the same figure in five published surfaces, and `.github/workflows/mcp-registry.yml` runs it on every push and pull request alongside a Rust uniqueness test. Run at this commit it exits zero and reports `registry_count: 90`, `canonical_tools_list_count: 90`, `compatibility_manifest_count: 270`. `CLAIMS-AUDIT.md` replaced its `grep -o '"name": "mimir_[a-z_]*"'` instruction with that command, described as formatting-insensitive and CI-run. Encryption is on by default for a fresh install, with `tests/encryption_bootstrap.rs` asserting a 32-byte key at mode `0600`, an established canary, and a stored body that is not the plaintext that was written, plus a second case for the explicit opt-out; a database created before the flip stays plaintext until `init --rekey`, which the audit states. `tombstone` moves to present and the report carries all seven marks: `rejected_value_tombstones` is keyed on `(workspace_hash, subject, predicate, value_sha256)` over a value normalized by JSON canonicalisation, whitespace collapse and lower-casing, stores only the digest so a rejection record cannot leak what it suppresses, is enforced in `remember_impl` across the remember paths, honours a global-or-workspace scope through `workspace_hash IN ('', ?1)`, and admits a trusted override that is journaled — with four committed tests including one for laundering and the override. `5d6cecf` adds Ed25519-signed policy/authority profiles verified before a manifest takes effect, failing closed, which is new context rather than a change to any published claim.

**2026-08-04** — same pin, corrected after the project's author reviewed the
report. The tool-count finding was stated as "stale by eleven", which asserts
that 76 is the true canonical figure; nothing established that. Parsing the
embedded registry literal rather than grepping it returns **88** top-level
entries — 87 `mimir_`-named, one `perseus_vault_`-named — so the claim (65), its
designated command (76) and the registry (88) disagree three ways. The
canonical/legacy split is not present in the literal: `tool_registry_base` calls
the `mimir_*` names "an implementation migration detail" and `legacy_alias_tool`
synthesizes aliases by prefix rewriting at advertise time, so what is advertised
is a runtime decision no static count can see. The finding is drift between a
count definition and its verification command, not a corrected number. The
tombstone gap is additionally qualified against the pattern page's own "not an
established best practice" header, and the falsifying test the author proposes —
reject A, replace with B, re-ingest A by another path, run consolidation, check
whether A stays rejected — is recorded in section 9.

**2026-08-04** — [`838c63dabbcfc4aaee0867ba7ff0bab7829e442b`](https://github.com/Perseus-Computing-LLC/perseus-vault/commit/838c63dabbcfc4aaee0867ba7ff0bab7829e442b) — first reading. The published LongMemEval means were recomputed from the six committed per-run reports and match exactly (73.8% plain, 79.0% CoT); the benchmark itself was not re-run, as it requires paid model calls. The claims audit's own tool-count command was executed and returns 76 against a claim of 65.

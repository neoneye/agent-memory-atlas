---
title: "Perseus Vault"
eyebrow: "Claims audited against artifacts"
description: "A local-first vault whose published benchmark means recompute exactly from committed per-run reports, whose self-audit retires the claims it cannot back, and whose rejected-value tombstone stores a digest rather than the value it refuses."
root: ../..
page_kind: system
source_name: "Perseus-Computing-LLC/perseus-vault"
source_url: https://github.com/Perseus-Computing-LLC/perseus-vault
revision: 5d6cecf9a5c2a95d90b9e96faadc45fa8ebec601
revision_url: https://github.com/Perseus-Computing-LLC/perseus-vault/commit/5d6cecf9a5c2a95d90b9e96faadc45fa8ebec601
analyzed_at: 2026-08-05
capabilities: "tombstone, trust_state, bitemporal, scope_enforced, audit_log, human_review, negative_eval"
matrix:
  memory_unit: "An entity — category, key, JSON body — carrying status, type, layer, certainty, verified flag, decay score, and bi-temporal bounds"
  storage: "One SQLite file with FTS5, AES-256-GCM bodies encrypted by default on a fresh install, an entity history table, a hash-chained journal, sign-bit embedding signatures, and a rejected-value tombstone table holding digests"
  retrieval: "Hybrid BM25 (FTS5) plus dense vectors fused by RRF, with a Hamming prefilter on embedding sign bits and workspace filters applied in the query"
  write: "MCP tool calls into a Rust binary; supersession writes history rows and sets `superseded_by`, with a trust-admission path in front"
  update_delete: "Supersede, correct, demote, archive with a reason, forget, and purge — purge erases history and redacts the journal; a rejected value is refused on every remember-path write by a digest-keyed tombstone, with an audited trusted override"
  scoping: "`workspace_hash` on entities and journal rows, a `(category, key, workspace_hash)` identity index, and a `visibility` column; applied in read queries"
  integration: "An MCP stdio server with ninety canonical tools, plus LangGraph, CrewAI, AutoGen, PydanticAI and Praison adapters; one binary, no services"
  background: "Decay ticks, cohere and dream passes, consolidation, hygiene scans, community detection"
  trust: "A discrete `status`, a separate `verified` flag, a `certainty` float and a `source` field — three distinct axes rather than one score"
  strengths: "Three full benchmark runs per prompt variant with a config stamp, published means that recompute exactly, a claims audit that retires what it cannot back, and a count check derived from source and run in CI"
  risks: "A database created before the default flipped stays plaintext until an explicit `init --rekey`, and the encryption key sits beside the database it protects"
---

## 1. Executive Summary

Perseus Vault is roughly 59,000 lines of Rust over 660 commits, MIT-licensed,
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

536 `#[test]` functions inline across `src/`, plus three integration files under
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

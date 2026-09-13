---
title: "Compartment"
eyebrow: "The prompt was measured and replaced with a door"
description: "An encrypted offline vault whose audit chain anchors its own length against truncation, and whose memory-shape rule moved from the MCP handshake into a refusal after the handshake version was measured at a 1,938-character median."
root: ../..
page_kind: system
source_name: "MaxFreedomPollard/Compartment"
source_url: https://github.com/MaxFreedomPollard/Compartment
archive_name: "MaxFreedomPollard--Compartment"
revision: 2686197034ed103a2d4283f1e679a7c8a2d929b6
revision_url: https://github.com/MaxFreedomPollard/Compartment/commit/2686197034ed103a2d4283f1e679a7c8a2d929b6
analyzed_at: 2026-09-13
capabilities: "bitemporal, scope_enforced, audit_log, negative_eval"
capability_evidence:
  audit_log: "the sealed payload — a hash-chained log whose length is anchored outside itself | src/compartment/audit.py:1-12 | each entry hashes over its predecessor, so an edit or a reordering in the middle breaks the chain at a detectable point. The part most chains in this corpus miss is handled explicitly: a forward-only chain cannot detect truncation of its own tail, so the head and the length are anchored in the meta table on every save and `verify()` requires the chain to EXTEND that anchor — fewer entries than were anchored, or a different hash at the anchored position, is reported as removal rather than passing as a clean shorter log. The log lives inside the sealed payload rather than beside it | tests/test_acl_audit_packs.py"
  scope_enforced: "search — a per-caller ACL resolved to a namespace set before the query runs | src/compartment/acl.py:1-6, :99-106, src/compartment/vault.py:1096-1141 | ACLs live in `<vault>.config.json` beside the sealed vault, granting each caller read or write on namespace patterns with the most specific grant winning rather than dict order. `Vault.search(self, query, caller, namespace=None, ...)` takes the caller as a required positional argument and resolves `allowed = set(self._readable_namespaces(caller))` before filtering, and `packs/*` namespaces are read-only for every caller including the `*` default. A caller cannot widen the set by omitting an argument, because the argument is not optional | tests/test_acl_audit_packs.py"
  bitemporal: "the relation table — when a fact was true, apart from when it was written | src/compartment/store.py:90-91, :652-676, src/compartment/cli.py:945, :954 | `relations` carries `valid_from` and `valid_to` commented as when the fact became and stopped being true, beside a `created` write timestamp, and the CLI lets a caller set the window explicitly so a fact learned today can be recorded as true from a past date. `find_relations(..., as_of=...)` keeps relations whose window covers the instant, with open-ended windows always matching. The limit is worth stating: `created` is stored and not filterable, so the vault can answer what was true in March and not what it believed in March | tests/test_atomic_and_retag.py:404"
  negative_eval: "the recent feed and search — seeded starter memories must not surface, over a store that holds 6,665 of them | tests/test_starter_visibility.py:92-97, :150, tests/test_atomic_and_retag.py:404, tests/test_long_memory_recall.py:109 | `test_the_recent_feed_hides_seeded_memories` asserts `not any(r[\"seeded\"] for r in out[\"results\"])` and then asserts `out[\"counts\"][\"seeded\"] == 6665` in the next line, so the absence is measured against a store demonstrably full of the excluded material — the vacuity guard is the count itself. Its docstring says why the case exists: stated so a later fix cannot be read as a licence to bury real memories under thousands of starting ones | `pytest`; not run, the screen reports three auto-run surfaces and a conftest that executes on collection"
stack_storage: "sqlite, files"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "An encrypted record in a namespace, with a kind, tags and optional validity bounds, beside a relation table of subject-predicate-object triples"
  storage: "One sealed `.vault` file — SQLite and ciphertext inside an encrypted payload, journaled and fsynced per write, with a hash-chained audit log inside the seal and ACLs in a plaintext config beside it"
  retrieval: "Keyword search over FTS, vectors rebuilt into RAM on unlock, and a deterministic relation filter with an `as_of` instant"
  write: "Every write is journaled and fsynced; a store gate refuses a memory whose shape would embed badly, rather than asking the model not to send one"
  update_delete: "Supersession by record id — the row, ciphertext and vectors stay so history and export keep it, while the FTS row goes so the keyword channel can never surface it again"
  scoping: "Per-caller ACLs over namespace patterns, resolved to a readable set before every search, with `packs/*` read-only for everyone"
  integration: "An MCP server, a Claude Code plugin, a Gemini extension, a menu-bar and systray app, and a CLI"
  background: "An embedding daemon; the vector index is rebuilt in RAM on unlock rather than persisted"
  trust: "None as a status. A record carries a kind and tags, and no epistemic state"
  strengths: "An audit chain that anchors its own length so a tail truncation is reported as removal; a store gate whose justification is a measurement of the prompt it replaced"
  risks: "Supersession is keyed on the record id, so nothing prevents the same claim being stored again; the record-time axis is stored and not queryable"
---

## 1. Executive Summary

Compartment is an encrypted, fully offline memory vault — Apache-2.0, about
30,700 lines of Python, one sealed `.vault` file, with an MCP server, a Claude
Code plugin, a Gemini extension, a menu-bar app and a CLI over it. A passphrase
the user sets is the only credential, and the project never generates one.

Four marks, and the two things worth reading are both cases of a design decision
being *argued* in the file that implements it.

**The audit chain knows what a hash chain cannot catch.** `audit.py` states the
problem and its answer in eleven lines:

> A forward-only chain cannot catch a truncation of its own tail: lop the last
> three entries off and what remains still verifies, just shorter. So the head
> and the length are anchored outside the chain, in the meta table, every time
> the vault is saved. `verify()` then requires the chain to EXTEND that anchor:
> fewer entries than were anchored, or a different hash at the anchored
> position, is reported as removal rather than passing as a clean shorter log.

Hash-chained audit logs are not rare in this corpus. One that notices its own
blind spot and closes it is.

**The store gate replaced a prompt after measuring the prompt.** The header of
`gate.py` records what happened:

> An instruction asking for one-or-two-sentence memories shipped in the MCP
> handshake and was measured not to work: against a real vault the median
> organic memory was 1,938 characters — session logs, headed lists, narrated
> paragraphs — because prose advice competes with everything else in a busy
> context and loses. A structured refusal arrives at the exact moment of the
> mistake, names what to do instead, and is obeyed.

This atlas records a great many memory policies that live in prompt text. Here is
one that was tried, measured against a real vault, found not to work, and moved
into code — with the number kept.

The gate is also careful about where it applies. It is *"enforced only where an
author can rephrase: agent- and operator-authored stores"*, and the restore and
capture paths — imports, journal replay, pack installs, the Claude Code hook, the
Hermes auto-capture writer — *"pass verbatim text they have no license to
rewrite, and bypass with `_gate=False`."* A shape rule that rewrote an import
would be corrupting a record rather than improving one.

**The reason it is protecting.** The same header states why one claim per record
matters, and it is a retrieval argument rather than a tidiness one: *"A blob
embeds as the centroid of its topics, so it matches many queries weakly; when it
does match, one relevant sentence drags kilobytes into the reader's context."*

## 2. Mental Model

A memory is a record in a namespace inside a sealed file, and the caller's ACL
decides which namespaces exist as far as they are concerned.

```mermaid
%% caption: the gate refuses a badly shaped memory at the door on authored paths only, while restore paths bypass it verbatim, and every write lands in a journal and a hash chain anchored against truncation
flowchart TB
    UNLOCK["Vault.unlock(path, passphrase)"] --> RAM["decrypt payload,<br/>replay journal,<br/>rebuild vector index in RAM"]
    A["agent or operator store"] --> G{"store gate:<br/>one claim, shape checked"}
    G -->|refused| MSG["structured refusal naming<br/>what to do instead"]
    G -->|accepted| W["write"]
    IMP["import, journal replay,<br/>pack install, capture hook"] -->|"_gate=False, verbatim"| W
    W --> J[("journal + fsync")]
    W --> AU[("hash-chained audit log,<br/>head and length anchored in meta")]
    W --> DB[("records + relations,<br/>inside the seal")]
    Q["search(query, caller)"] --> ACL{"ACL: readable namespaces<br/>for this caller"}
    ACL --> DB
    DB --> R["results"]
    TS["tombstone(record_id, by)"] --> KEEP["row, ciphertext and vectors stay —<br/>history and export keep it"]
    TS --> FTS["FTS row removed —<br/>the keyword channel cannot surface it"]
```

## 3. Architecture

One file. `Vault.create` writes a sealed `.vault`; `Vault.unlock` decrypts the
payload into RAM, replays the journal and rebuilds the vector index in memory;
writes are journaled and fsynced; `save()` compacts and reseals and `lock()` drops
key material from the process.

**The vector index is never persisted** — it is rebuilt on unlock. That costs
startup time and means an attacker with the file gets ciphertext rather than
embeddings, which for a vault whose premise is offline encryption is the right
trade.

The ACL config lives *next to* the vault as plaintext `<vault>.config.json`, and
the file says why that is safe: it *"contains no secrets — only ACLs and
preferences."*

## 4. Essential Implementation Paths

- **Vault lifecycle** — `src/compartment/vault.py:1-12` (the docstring states it),
  `_readable_namespaces` (1096), `search` (1125-1141), tombstone dispatch (923),
  journal ops including `forget` (725-732).
- **Audit** — `src/compartment/audit.py:1-12`.
- **ACL** — `src/compartment/acl.py:1-6`, defaults (23), `default_namespace` (99),
  `_match` specificity (103-106).
- **Store gate** — `src/compartment/gate.py:1-30`.
- **Store layer** — `src/compartment/store.py`: `relations` validity columns
  (90-91), `tombstone` (274-282), `find_relations` with `as_of` (652-676).
- **Curation** — `src/compartment/curate.py:1-12`, `apply_plan` (105).
- **Crypto** — `src/compartment/crypto.py`; embedding daemon in `embed_daemon.py`.

## 5. Memory Data Model

A record carries ciphertext, a namespace, a `kind` and tags. Relations are a
separate subject-predicate-object table with `valid_from`, `valid_to` and a
`created` timestamp.

There is no epistemic status on a record — no candidate, verified or rejected —
so **`trust_state` is withheld**. `kind` is a genre and tags are labels.

**`tombstone` is withheld**, and the near-miss is interesting.
`store.tombstone(record_id, by)` sets `superseded_by` and the docstring describes
a deliberate asymmetry: *"The row, its ciphertext and its vectors stay — history
is kept, and export still carries it — but its FTS row goes, so the keyword
channel can never surface it."* That is supersession keyed on a record id, which
the rubric names as not the mark, and the partial removal is a thoughtful design:
the record survives for audit and export while one retrieval arm loses it
permanently. Nothing is keyed on the *content*, so the same claim stored again is
a new live record.

## 6. Retrieval Mechanics

Three channels: FTS keyword search, vectors held in RAM, and a deterministic
relation filter. The ACL is applied first — `search` resolves the caller's
readable namespaces before anything is scored — and `as_of` on the relation
filter keeps windows covering an instant, with open-ended windows always
matching.

Namespace scoping is the boundary and it is not optional: the caller is a
required argument, so there is no call shape that skips it.

## 7. Write Mechanics

Every write is journaled and fsynced before the vault is resealed, so a crash
loses at most the compaction rather than the write. The journal is replayed on
unlock, and the `forget` operation is explicitly built to be replayable.

The gate sits in front of authored writes only. Its bypass is not a loophole but
the correct behaviour for a path that is restoring somebody else's text, and the
distinction is stated where the flag is defined.

## 8. Agent Integration

An MCP server (`mcp.json`, `server.json`), a Claude Code plugin with hooks, a
Gemini extension, a desktop menu bar and systray, and a CLI. The screen flags
three auto-run surfaces, which is what a tool designed to be installed into
several harnesses looks like.

`curate.py` is the interesting integration: it splits blob memories into atomic
ones, and it *"never invents the split. Compartment never calls an LLM and never
touches the network, so the intelligence that turns one 2,000-character blob into
five one-claim memories comes from outside — the user's own agent, reading the
listing this module produces and writing the plan this module applies."* The
module owns the bookkeeping and delegates the judgement. **`human_review` is
withheld** because the plan is authored by an agent rather than approved by a
person, and no command prompts for an approval — but the split of mechanics from
judgement is worth copying regardless.

## 9. Reliability, Safety, and Trust

The threat model is a stolen file and a tampered log, and both are addressed. The
payload is sealed with a user-set passphrase, the vector index never touches disk,
`lock()` drops key material from the process, and the audit chain detects
insertion, reordering and truncation.

`packs/*` namespaces being read-only for every caller including the `*` default is
the ACL detail worth noting: shipped content cannot be edited by a caller who was
granted everything.

What is absent is epistemics. Nothing records that a memory was judged wrong, and
supersession is by id, so the vault's defence is against tampering rather than
against being mistaken.

## 10. Tests, Evals, and Benchmarks

A substantial suite, and `tests/test_starter_visibility.py` is the one that earns
the mark. `test_the_recent_feed_hides_seeded_memories` asserts no seeded memory
appears in the feed, and on the very next line asserts
`out["counts"]["seeded"] == 6665` — so the absence is measured against a store
containing six and a half thousand of exactly the material being excluded. The
count *is* the vacuity guard, and it is the cleanest instance of that pairing this
atlas has read.

Its docstring explains why the test exists, which is rarer still: *"Unchanged
behaviour, stated so the fix below cannot be read as a licence to bury real
memories under thousands of starting ones."*

`longmemeval.py` and `bench.py` are in the tree; no committed result was found for
either. No paper and no `CITATION.cff`.

Nothing was run. The screen reports three auto-run surfaces — a `.claude-plugin/`
marketplace manifest, `mcp.json` and `server.json` — and a `tests/conftest.py`
that executes on collection.

## 11. For Your Own Build

### Steal

**Anchor your audit chain's length outside the chain.** A hash chain proves
nothing about its own tail. Writing the head and the count into a separate table
on every save, and requiring a later verification to *extend* that anchor, turns
a silent truncation into a reported removal. Eleven lines of comment and a
meta-table row.

**Measure the prompt before you trust it, and keep the number.** *"The median
organic memory was 1,938 characters"* is the sentence that justifies moving a
rule from the handshake into a refusal. Most projects in this corpus have the
rule in the prompt and no measurement either way.

**Refuse at the door, and say what to do instead.** A structured refusal *"arrives
at the exact moment of the mistake, names what to do instead, and is obeyed"* —
which is what prose advice in a system prompt cannot do.

**Exempt the paths that are restoring, not authoring.** The gate bypasses imports,
journal replay and capture hooks *"verbatim text they have no license to
rewrite"*. A shape rule applied to a restore is data corruption.

**Take the caller as a required argument on your read path.** `search(query,
caller, ...)` has no call shape that omits the scope.

**Keep the record and drop it from one channel.** Tombstoning here retains the
row, the ciphertext and the vectors for history and export while removing the FTS
row permanently. Two different questions — can it be audited, can it be found —
answered separately.

### Avoid

**Superseding by id when the risk is re-assertion.** The record is removed from
the keyword channel and nothing is keyed on its content, so the same claim
arriving again is simply a new record.

**Storing a record time you cannot query.** `created` sits beside `valid_from` and
`valid_to` and no filter reads it, so the vault can say what was true in March and
not what it believed in March.

### Fit

This suits someone who wants agent memory that is genuinely private — encrypted at
rest, no network, no model calls from the library itself — and who will keep a
passphrase. The audit design makes it a reasonable choice where the question
"has this been tampered with" has to have an answer.

It is the wrong fit where memory must be shared across people or machines, where
correction has to bind against re-assertion, or where you want the system itself
to summarize and split memories — it deliberately delegates that to your agent
and applies the plan.

## 12. Open Questions

- **Would keying supersession on content fit the sealed design?** The ciphertext
  is there; a digest of the plaintext at write time would be enough.
- **Should `created` be filterable?** The column exists and the as-of machinery is
  already written for the other axis.
- **What does `apply_plan` do with a plan that contradicts the audit chain?** The
  curation path applies an externally authored plan, and the chain records the
  result rather than gating it.
- **Was the 1,938-character median re-measured after the gate shipped?** The
  number that justified the change is the number that would show it worked.

## Appendix: File Index

**Vault and storage**

- `src/compartment/vault.py` — lifecycle docstring (1-12), `_readable_namespaces`
  (1096), `search` (1125-1141), tombstone dispatch (923), journal `forget`
  (725-732)
- `src/compartment/store.py` — relation validity (90-91), `tombstone` (274-282),
  `find_relations` with `as_of` (652-676)
- `src/compartment/crypto.py`, `embed.py`, `embed_daemon.py`

**Governance**

- `src/compartment/audit.py` — the chain and its anchor (1-12)
- `src/compartment/acl.py` — namespace grants (1-6, 23, 99-106)
- `src/compartment/gate.py` — the measurement and the bypass (1-30)
- `src/compartment/curate.py` — mechanics-versus-judgement (1-12), `apply_plan` (105)

**Surfaces**

- `mcp.json`, `server.json`, `.claude-plugin/`, `gemini-extension.json`,
  `src/compartment/menubar.py`, `systray.py`, `cli.py`, `claude_hooks.py`

**Tests**

- `tests/test_starter_visibility.py` (92-97, 150), `tests/test_acl_audit_packs.py`,
  `tests/test_atomic_and_retag.py` (404), `tests/test_long_memory_recall.py` (109)

### Commands behind the absence claims

```sh
grep -rn -i "tombstone" src/compartment/store.py
grep -n "created" src/compartment/store.py | grep -iE "WHERE|<=|>="
grep -n "confirm\|apply\|--yes\|dry" src/compartment/curate.py
grep -rn -i "arxiv\|bibtex\|@article\|citation\|doi" README.md docs/
```

## History

**2026-09-13** — [`2686197034ed103a2d4283f1e679a7c8a2d929b6`](https://github.com/MaxFreedomPollard/Compartment/commit/2686197034ed103a2d4283f1e679a7c8a2d929b6) — first reading. Screened first: three auto-run surfaces — a `.claude-plugin/` marketplace manifest, `mcp.json` and `server.json` — and a `tests/conftest.py` that executes on collection. Nothing was installed, no harness was wired and the suite was not run. Four marks. `audit_log` is earned on a hash chain that anchors its own head and length in the meta table so a tail truncation is reported as removal rather than verifying as a shorter log. `bitemporal` is earned with a stated limit: the validity window is independently settable and queryable through `as_of`, while the `created` record timestamp is stored and not filterable. `tombstone` is withheld — supersession is keyed on a record id, and the interesting half is that the row, ciphertext and vectors are kept for history and export while the FTS row is removed permanently. `human_review` is withheld because curation applies a plan an agent wrote rather than one a person approved.

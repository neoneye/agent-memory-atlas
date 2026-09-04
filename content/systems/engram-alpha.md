---
title: "Engram Alpha"
eyebrow: "Time doesn't validate, exposure doesn't validate"
description: "A Rust graph memory for coding assistants whose trust decays only when judged contradicting evidence lands, never from age alone and never from being retrieved — with the ablation row it ships labelled in its own committed benchmark data, and a fitted-as-data ontology carrying it onto a corpus it did not write."
root: ../..
page_kind: system
source_name: "techtheist/engram"
source_url: https://github.com/techtheist/engram
revision: f13d45a90391aa0d7a8986cfd79f8246ac607f9c
revision_url: https://github.com/techtheist/engram/commit/f13d45a90391aa0d7a8986cfd79f8246ac607f9c
analyzed_at: 2026-09-04
capabilities: "trust_state, bitemporal, audit_log, human_review, negative_eval"
capability_evidence:
  trust_state: "the node record and the suspects queue | crates/engram-core/src/schema.rs, engine.rs | three durable anchors on `nodes` — `confirmed_at` (*\"last deliberate act; the unapproved trust anchor\"*), `approved_at` (*\"last explicit approval; trust anchors here\"*) and `demoted_at` (*\"when contradicting evidence landed\"*) — plus `trust_override`, a pin that holds trust constant and turns decay off, and a `suspects.status` of suspected/confirmed/dismissed carrying an `nli_label` hint of contradiction/entailment/neutral beside it. Trust is computed at read time from the anchors rather than stored as a score | crates/engram-core/src/tests.rs `user_nodes_are_approved_on_creation_and_approve_restores_trust`, `claude_replaces_verdict_cannot_archive_a_pinned_node`, `decay_archives_only_stale_unapproved_claude_episodic_nodes`"
  bitemporal: "the node and edge records, and a graph-declared event clock on search | crates/engram-core/src/schema.rs, engine.rs:1850-1853,:1754-1790, timespec.rs:84-98, store.rs:562-567 | `valid_from` and `valid_until` on both tables, distinct from `created_at`: the record axis says when the store learned it, the validity axis when it held as canon. Setting `valid_until` is the supersede flow and nothing else — the comment says so at the call — and the audit action becomes `archived`; retrieval retains only rows whose `valid_until` is none. A second validity axis is the owner's: `search` reads its `after`/`before` window against `created_at` by default, and a `date_field` selector re-aims the same window at a date-kind custom field, or at a `from..to` pair with interval-overlap semantics, so a note captured today about something that held in 2019 answers a 2019 question. `check_clock` refuses an undeclared field or a clock with no window as an error rather than a dropped filter | crates/engram-core/src/tests.rs `resolve_replaces_archives_the_older_node`, `audit_logs_supersede_and_decay_as_archived`, `date_field_clock_filters_on_the_event_clock`, `date_field_clock_is_validated_loudly`, `sealed_indexed_fields_and_event_clock_still_work`"
  audit_log: "the store | crates/engram-core/src/schema.rs:66-81 | an insert-only `audit` table — *\"Rows are only ever inserted; `seq` is the pagination cursor\"* — one row per node or edge mutation over an eleven-value action vocabulary (created, updated, approved, unapproved, pinned, unpinned, demoted, undemoted, archived, deleted, imported), with full `before_json` and `after_json` snapshots, a `title` label that survives deletion, and the writing process stamped on the row: `origin` of pane/mcp/daemon/cli/library, `session_id`, `cwd`, `pid`, `version` | crates/engram-core/src/tests.rs `audit_journals_node_lifecycle_with_context`, `audit_journals_edges_with_sentence_labels`, `audit_logs_supersede_and_decay_as_archived`, `audit_page_keyset_pagination`, `audit_origin_stamp_and_session_fallback`, `audit_import_writes_one_summary_row`"
  human_review: "the suspects queue, the pane and the pin | crates/engram-core/src/engine.rs (`resolve_suspect`, `approve`, `set_trust_override`, `nli_agreement`) | a write returns the look-alike pairs it queued so the assistant judges them in the same turn, and `resolve_suspect` records the verdict as conflict, replaces or dismiss. Pinning is a human act by construction — no MCP tool writes `trust_override` — and a pinned node ignores contradicting evidence until a person unpins it; approval is not: `approve_node` (crates/engram-mcp/src/lib.rs:1073-1080) restarts trust at 100% from the assistant's side, and its only restriction is the sentence in its description. The pane is the surface: stale nodes queue for a decision, conflicts are judged there, and the browser demo exercises all of it. `nli_agreement` scores the model hint against the human verdict and is deliberately excluded from the auto-tune inputs | crates/engram-core/src/tests.rs `user_nodes_are_approved_on_creation_and_approve_restores_trust`, `claude_replaces_verdict_cannot_archive_a_pinned_node`, `audit_answered_nominates_but_never_resolves`"
  negative_eval: "the offline evaluation harness | eval/src/generate.rs, eval/src/arms.rs, eval/results/floor-100.json, floor-500.json, floor-1500.json | the generated corpus carries a control arm of *\"questions about subjects that were never written\"* — one control subject per four tested facts, with chains generated before the controls so a phantom subject can never collide with a real one — and `controls_declined` is reported at every threshold in the committed floor sweeps, so a precision gain is never published without the recall it cost | the harness is the mechanism, and the three committed floor sweeps are its runs"
stack_storage: "tepindb, sqlite"
stack_retrieval: "lexical, vector, graph"
stack_source: "reviewed"
matrix:
  memory_unit: "A typed node joined by typed edges, carrying a `fields` map of graph-declared custom values beside its tags — but the type set is per-graph config, not a Rust enum: engine logic keys on the roles a type or verb carries (`supersession`, `contradiction`, `worklist`, `tombstone`), so a renamed or replaced ontology keeps every behaviour"
  storage: "TepinDB — one self-describing `graph.tepin` file holding documents, keyword index and vectors, the birth format of every new graph since v0.6.2 — with the SQLite driver kept behind the same trait as a migration source; nodes and edges plus a suspects table, an append-only audit journal and a meta row that records the store's own encryption state"
  retrieval: "Vectors with a reranker that votes rather than decides, a keyword weight of 0.15 over a blind BM25 index that ranks identically sealed or plain, calibrated delivery — a score floor and a knee cut whose whole tradeoff curve is committed, with the abstention line fitted per graph from unanswerable probes built out of the graph's own vocabulary — a rank demotion at the cut for a second hit from a session already delivered, and one-hop neighbours attached to every hit"
  write: "A write returns the look-alike pairs it just queued, so the assistant judges them in the same turn — detection is local, judgment is the assistant's"
  update_delete: "`replaces` and `conflicts-with` edges, `valid_until` for archival, an atomic `merge_nodes` that rehomes edges and archives victims behind a supersession, a suspects table resolved as conflict, replaces or dismiss, a human pin that disables decay, and a hard delete that mints a `Tombstone` note naming what was removed and why"
  scoping: "None inside a graph. Separation is one store per project, and a single machine-wide core process holds them all — so which project a session reads is a five-rung binding decision, not a predicate"
  integration: "An MCP server that is always a bridge to the machine core, a JetBrains plugin and a VS Code extension published to three marketplaces, plus a standalone pane with a live browser demo; `brief` called with a `project` rebinds a session whose client will not say where it is, and `setup` writes session-start brief hooks for Claude Code, Codex, Devin CLI and Bob"
  background: "Trust is computed at read time, so no pass has to have run for a read to be correct; a session-boundary `validate_graph` archives, retires, re-fits the two auto-tune dials and rescans, and drift scans surface for review while deliberately never demoting"
  trust: "Three distinct durable anchors — `confirmed_at`, `approved_at`, `demoted_at` — plus a `trust_override` pin, and a suspects status of suspected, confirmed or dismissed"
  strengths: "Retrieval stamps `last_seen` for observability only, because exposure would otherwise let a broad recurring query certify its own outputs"
  risks: "No scope key of any kind, and a session whose workspace cannot be determined binds the home graph rather than failing; approval is an MCP call whose only guard is its own description; the retrieval half of LongMemEval is graded at session level, and the one number the external run does not price is how often an answerable question gets warned"
---

## 1. Executive Summary

Engram Alpha is graph memory for AI coding assistants: ~31,000 lines of Rust
across four crates (~45,000 counting their test modules) plus a 12,300-line
evaluation crate, MIT, release v0.9.1, 142 commits since 3 July 2026, shipping
as a JetBrains plugin and a VS Code extension on three marketplaces with a
browser demo of the real pane. **Not to be confused with
[Engram](../engram/) — a different project of the same name, already in this
atlas.**

*Alpha* is part of the product's name, not a maturity label: the marketplace
identifier is `techtheist.engram-alpha`, the installed binary is
`engram-alpha`, and nothing in the README applies the word to the software's
state. The stability claim the repository does make is its own status line —
*"early development, heavily dogfooded, benchmark-driven — retrieval changes
cite a measured run or they don't ship"* — and the second half of that sentence
is the one this report can check.

A memory is a typed node joined by typed edges — but the vocabulary is
**per-graph configuration, not a closed enum**. `GraphConfig` (`config.rs`)
stores the ontology, the policy numbers and the brief shape as one document
inside the graph itself, travelling with `migrate` and riding along in exports.
The shipped preset is nine types — `Principle`, `Decision`, `Caution`,
`Problem`, `Resolution`, `Insight`, `Intent`, `Anchor`, `Tombstone` — over
seven verbs: `about`, `because`, `answers`, `builds-on`, `replaces`,
`conflicts-with`, `needs`. Three other presets ship beside it (`research`,
`minimal`, `general`) and a graph may define its own type set, its own verbs,
and its own custom fields.

The rule that makes that safe is stated at the top of the module and enforced
throughout: **roles, never names.** Engine logic keys on the role flags a type
or verb carries — `worklist`, `supersession`, `contradiction` — never on the
strings, so a renamed or wholly replaced ontology keeps every behaviour.
`hub.rs:104` is the shape of it: the contradiction gate tests
`edge.edge_type.as_str() == contradiction_verb`, where the verb comes from the
graph's config, not from a literal. Two hard invariants hold across any
configuration — edges stay sentence-shaped, and exactly one supersession verb
plus one contradiction verb must exist, *"they are what make the graph active"*
— with `graph_config_validation_guards_hard_invariants` and
`shipped_presets_are_valid_and_complete` asserting both. There is deliberately
**no MCP write surface** for the ontology: reshaping it is a pane gesture,
*"like pin and delete"*.

**Its trust model states two principles the rest of this corpus mostly violates**,
and `crates/engram-core/src/policy.rs` names both:

> **Time doesn't validate.** `stable` knowledge holds its trust flat until a live
> `conflicts-with` edge (the judged-evidence event) stamps `demoted_at`; only
> then does it ramp down, and withdrawing the evidence withdraws the demotion.

> **Exposure doesn't validate.** Retrieval stamps `last_seen` for observability
> only — it proves a note was *findable*, not that it is true. Trust anchors on
> `confirmed_at`, which only deliberate acts refresh. Otherwise a broad recurring
> query would keep an attractive but wrong note alive forever — **retrieval
> certifying its own outputs.**

That second sentence is the exact failure this atlas records in
[Core Memory](../core-memory/) ("recall raises the class… still a use signal
feeding a trust field"), in [NOOA](../nooa-memory/)'s myelination, and in the
decay curves of [Mnemopi](../mnemopi/) and [PowerMem](../powermem/). Engram names
it and refuses it. The header adds that both principles were *"learned from
external feedback on v0.4.1"* — a trust model changed by review rather than
defended.

Drift is treated the same way: surfaced for review, never demoting, because it is
*"environment-dependent (wrong cwd, feature branches) and a sticky stamp from a
bad scan would mass-bury the graph."* A system that knows which of its own
signals are too noisy to act on is rare.

**The write path resolves instead of queueing.** `WriteOutcome::Created` returns
the look-alike pairs the write just queued, with the reason in the type:
*"returned so the writer judges them in the same turn instead of leaving them for
the next session's brief (PLAN §7: detection is local, judgment is the
assistant's)."* Deterministic local detection, model judgment, in one turn — the
shape [resolve, don't just detect](../../patterns/resolve-not-just-detect/) asks
for.

**Deletion leaves a tombstone, and the tombstone is a note, not a gate.** A hard delete from the pane or
the HTTP surface mints a `Tombstone`-role note — *"Removed: `<title>`"*, with
the victim's type, id and the person's reason in the body — so the removal is
on the record. What it does not do is stop the record being contradicted: the
write boundary consults no tombstone, and the sweep that nominates look-alike
pairs skips tombstones by design. Section 9 prices that.

**And the benchmark data is the most self-incriminating in the corpus.**
`eval/results/bench-100.json` is a thirteen-row ablation with a full config stamp
(`"embeddings_are_fake": false`, seed, embedder, reranker), a corpus profile, and
a phrasing mix. The shipped configuration is labelled *in the data*:
`"kw 0.15 · reranker VOTES   <- ships today"`. And it does not win:

```text
rag (pure vectors)   weighted_recall 0.992   oblique 0.92   tokens_mean 2268.8
engram (shipped)     weighted_recall 0.989   oblique 0.89   tokens_mean  373.1
```

They publish the row where plain RAG beats them on recall, and let the six-fold
token reduction make the argument. `contradictions-500.json` separates the two
ways contradiction detection fails — *"missed_by_retrieval": 0,
"missed_by_judgment": 3* out of 100 — which is a diagnostic decomposition almost
nobody reports, and `floor-500.json` sweeps twenty-one score floors with
unanswerable **controls** at each point, so the precision gained is priced
against the answerable questions declined.

**And it runs on a corpus it did not write.** `eval/LONGMEMEVAL.md` reports the
full 500 questions of [LongMemEval](https://github.com/xiaowu0162/LongMemEval)-S
— real multi-session chat, ~115k tokens of haystack per question, evidence
sessions labelled, 30 questions deliberately unanswerable — ingested *as-is*,
one verbatim note per chat turn, with no extraction and no model anywhere in the
ingestion or grading path. Five arms over identical haystacks; the receipt is
`eval/results/longmemeval-s-full.json`:

```text
arm            R@1    R@5    MRR    tok/query
engram         0.909  0.953  0.929      207.5
rag            0.909  0.974  0.937    2,654.4
grep           0.706  0.864  0.775    4,761.0
curated-file   0.919  0.919  0.919    2,999.0
whole-file     1.000  1.000  1.000  122,515.5
```

No row is an outright win, and that is the point of publishing all five. Engram
matches pure vectors at R@1, gives up 0.02 at R@5, loses R@1 to a blind
3,000-token file dump — and delivers an eighth of rag's tokens doing it, with
both of its recall figures computed over the set calibrated delivery left rather
than over a fixed ten. The 30 unanswerable questions draw **2 empty deliveries,
28 warned, 0 unwarned**, with the weak line auto-fitted per store on 27 of 30
graphs.

The limits are real and the project states most of them itself: there is no
scope key of any kind, the external run grades retrieval at *session* level
(any turn from the right session counts, which flatters dumps), and the
harness never asks what the same warning line costs on the 470 answerable
questions — the offline suite, which does ask, answers 47% at both 100 and
1,500 notes.


## 2. Mental Model

A node is a claim of a kind the graph's ontology declares, and the kind carries
the epistemics: under the shipped preset a `Decision` is not a `Caution` is not
an `Insight`, and the roles each kind carries are what the engine reads.
Durability is separate —
`stable`, `episodic`, `volatile` — and decides whether time is allowed to erode
it at all.

Trust is **computed at read time** from durable anchors, so nothing depends on a
background pass having run. The anchor picks the starting value: `created_at`
alone starts at `TRUST_UNSEEN_START`; `confirmed_at` (a deliberate update, or
"Confirm still true") restarts the clock at `TRUST_CONFIRMED_START`;
`approved_at` starts higher and ramps to a floor. `trust_override` — the pane's
pin — short-circuits all of it: pinned nodes never decay, never auto-archive, and
evidence events skip them, because *"a human said 'forever', so only a human
unsays it"* — while contradictions still surface for review.

A node whose computed trust falls below `STALE_TRUST` is **stale**: still
searchable, buried by the multiplier, flagged to the assistant, and put in the
pane's review queue for a human decision. Nothing disappears silently.

The other half of the state machine is the `suspects` table: look-alike pairs
with a similarity, an optional local-NLI hint (`contradiction | entailment |
neutral`) and a score whose column comment reads *"models don't validate"*. A
suspect is `suspected`, then `confirmed` or `dismissed`, and the verdict
vocabulary is `conflict`, `replaces`, `dismiss`.

The constants in that machine are per-graph, and two of them are fitted rather
than chosen. `Engine::auto_tune` runs at every session boundary: dial one
refits the conflict-suspect floor from the graph's own judged suspects by
maximising balanced accuracy over midpoint candidates, and dial two refits the
"likely not in memory" line. Each move is damped to half the distance to the fit
(`AUTO_TUNE_DAMPING = 0.5`), clamped into a stated range, suppressed below
`AUTO_TUNE_MIN_DELTA`, gated behind minimum volumes — 200 notes and 20
judgments with at least 3 on each side for dial one — and journalled as an
`auto_tuned` row. `policy.auto_tune = false` opts a graph out entirely. The
field lesson behind it is written down in the project's own chronicle:
*"register-dependent score scales — absolute thresholds don't transfer between
graphs, relative mechanisms do."*

```mermaid
%% caption: trust moves on evidence and on people — a live conflicts-with edge demotes and its withdrawal lifts the demotion, a human pin turns decay off, and retrieval stamps last_seen without moving anything
stateDiagram-v2
    [*] --> Unseen: created_at only, trust starts low
    Unseen --> Confirmed: a deliberate update or Confirm still true
    Unseen --> Approved: explicit approval, higher start, ramps to a floor
    Confirmed --> Demoted: a live conflicts-with edge stamps demoted_at
    Approved --> Demoted: a live conflicts-with edge stamps demoted_at
    Demoted --> Confirmed: the evidence is withdrawn, the demotion lifts
    Approved --> Pinned: trust_override, decay off
    Pinned --> Approved: only a human unpins
    Confirmed --> Stale: trust falls below the floor, buried not deleted
    Stale --> Confirmed: reviewed and confirmed in the pane
    Confirmed --> Archived: valid_until set
    Unseen --> Unseen: retrieval stamps last_seen and moves nothing
```

The self-loop at the bottom is the design. Retrieval touches the graph and
changes no trust, so a note cannot certify itself by being popular.


## 3. Architecture

**Runtime.** One binary, and at runtime one heavy process per machine with any
number of deliberately light ones around it. The **machine core** holds every
open store and its locks, the three local models, the pane's web server and every
MCP session; it binds `127.0.0.1:8787`, runs as a hidden `core` subcommand, is
spawned detached by whichever command first needs it, and ends only on
`engram-alpha stop`. `serve` is a launcher that registers the repository and
exits. `engram-alpha mcp` is *always a bridge* — it never opens a store on any
backend, proxying the client's stdio session to the core over streamable HTTP,
and failing with an error in `.engram/mcp.log` rather than *"silently opening the
store in-process"*. `status`, `doctor`, `stop` and the hooks are one-shot REST
clients. Discovery is two JSON advertisements plus a `GET /health` check, so a
stale file is harmless, and `~/.engram/registry.json` lists which repositories
have graphs.

That consolidation is the change a reader of the previous release has to notice,
because it moves a guarantee. When each project directory ran its own process
over its own file, reading the wrong project's graph was not expressible. One
core holding every store makes it a routing decision — see the binding ladder in
section 8.

`engram-core` carries the engine, `engram-mcp` the tool surface, `engram-http`
the REST and SSE API, `engram-cli` the process model and the per-client setup
writers, with a Vue frontend for the pane and editor integrations for JetBrains
and VS Code published to the JetBrains Marketplace, the VS Marketplace and Open
VSX. There is a standalone browser demo running the real pane over an invented
project, and the feature screenshots in the documentation are generated from
that demo by a headless-browser manifest (`frontend/scripts/shots/`), so every
image is one a reader can reproduce.

**Persistence.** TepinDB (`store_tepin.rs`) — a single self-describing
`graph.tepin` file holding documents, keyword index and vectors, from the
`tepindb` crate the same author publishes, inspectable with `npx tepindb` —
is where every new graph has been born since v0.6.2; SQLite (`store_sqlite.rs`)
sits behind the same `store.rs` trait and `docs/storage.md` calls it *"only a
migration source"*, with a `graph.db` migrating itself at the daemon's next
open. Four tables: `nodes`, `edges`, `suspects`, `audit`, plus a `meta` table
holding the embedding model identity and vector width so a store cannot be
silently read with the wrong embedder, and — since v0.9.0 — the store's own
`encryption_state`.

**At rest, two switches.** `~/.engram/settings.json` carries `encrypt_graph`
(off by default, because a sealed graph costs the `npx tepindb` inspection)
and `encrypt_history` (on by default, formalising what the harvester had done
since v0.8.4). Sealing is field-level in `seal.rs` — zstd then
XChaCha20-Poly1305 over titles, bodies, tags, code refs, custom-field values,
edge notes and the audit journal's before/after images, under a machine key in
the OS keystore — and the state lives in the store's own meta as `plaintext |
sealing | sealed | unsealing`, so a migration killed halfway resumes at the next
open and the settings file only ever carries intent. Structure, timestamps, ids
and embedding vectors stay open, and the module says why for the vectors:
*"documented inversion risk — vectors recover gist, not text."* The keyword
index is a blind index: one synthetic `_kw` token stream per node, identity
tokens on a plaintext store and keyed HMAC-SHA256 digests on a sealed one
(`seal.rs:216-224`), so term frequencies and document lengths are preserved and
a golden test asserts bit-identical BM25 rankings across the two states.

**Modules worth naming.** `config.rs` holds `GraphConfig` — the ontology, the
custom-field definitions, the policy numbers and the brief composition as one
stored document, with the four shipped presets and the validator for the hard
invariants; `seal.rs` the at-rest codec and the blind keyword tokens; `nli.rs` runs a local
natural-language-inference model for contradiction hints; `policy.rs` holds the
trust constants, the auto-tune bounds and their rationale; `onnx.rs` centralises
inference-session policy (arena, thread and batch-width knobs, read from
`ENGRAM_ONNX_*`); `redact.rs` exists at all; `cortex.rs`, `digest.rs`, `rag.rs`,
`hub.rs` carry retrieval and briefing; `migrate.rs` handles schema movement.

**Background work.** Deliberately little, and none of it load-bearing for a
read. Trust is a read-time computation. The suspects queue is filled
synchronously by the write that created the look-alike. What does run is
`Engine::validate_graph`, one session-boundary pass — archive what decayed,
retire what a supersession superseded, refit the two auto-tune dials, rescan for
conflicts, count drifted `code_refs` — journalled as a `graph_validated` row
with its own summary note, and backed by a six-hourly sweep. Drift scans surface
for review without demoting.

Since v0.8.4 a second detached daemon runs alongside that sweep: the **history
harvester**, a 60-second loop (fs-notify-accelerated in v0.8.7) that tails
coding-assistant transcripts into a separate episodic store — so "deliberately
little background" understates a continuous transcript-tailing loop, even
though it feeds a sibling store and not the curated read.

### Deployment and ergonomics

One binary, one store file per project, one core process per machine, plus
optional local models. `install.sh` and `install.ps1` fetch the binary and stop;
wiring a repository is the explicit `engram-alpha setup --cli …`, and `serve`
names what it found and did not wire — *"found codex, gemini — installed but not
connected to Engram in this repo"* — rather than touching a config it did not
write. The models are an
embedder (`bge-small-en-v1.5`), a reranker (`jina-reranker-v1-turbo-en`) and an
NLI model (`deberta-v3-small-tasksource-nli`, a 172 MB quantised ONNX export the
project made itself) — all small enough to run on a developer machine, which is
the point. No service to stand up and no API key required to store anything.

The NLI slot has been swapped twice on measurement, and the module says what
each swap bought: MNLI-only models *"presuppose co-reference"* and call
unrelated same-register notes confident contradictions — *"Engram uses Rust"*
against *"TepinDB is on crates.io"* scored 0.99 — where the multi-task model
judges them neutral, halving false alarms at the shipped gate. Predecessors stay
selectable, and the swap contract is a directory holding `model.onnx`,
`tokenizer.json` and a `config.json` whose `id2label` covers the three classes.

The pane is the operating surface and it is unusually complete: a live graph, a
review queue, conflict judgement, retirement, pinning, an ontology editor, a
feed timeline and a theme menu. The browser demo means a reader can exercise the
correction flow without installing anything, which is the best documentation
decision in the repository.

The daemon's memory footprint is measured with a committed before/after pair.
`eval/results/mem-daemon-before.json` and `-after.json` walk the same six stages
— startup with three models, one search, ten searches, an NLI claim check, a
conflict scan, thirty seconds idle — under stock onnxruntime defaults and under
the shipped ones: 669,696 → 896,000 KB against 667,648 → 696,320 KB. The
difference is an inference batch width capped at 2 instead of fastembed's 256;
`scripts/mem-probe.sh` is the harness, and three other suspects (the ORT arena,
per-session thread pools, malloc free-list retention) are recorded as measured
and refuted.


## 4. Essential Implementation Paths

- **Schema:** `crates/engram-core/src/schema.rs` — `nodes` (`:6`), `edges`
  (`:29`), `suspects` (`:52`), the append-only `audit` journal (`:67`), `meta`
  (`:88`).
- **Types and vocabularies:** `crates/engram-core/src/types.rs` — open
  string-backed name types, durability, statuses, `WriteOutcome::Created`
  returning `suspects`, `MergeOutcome`.
- **Ontology and per-graph config:** `crates/engram-core/src/config.rs` —
  `GraphConfig`, `OntologyConfig`, `TypeRoles` / `VerbRoles` (the `tombstone`
  role at `:298-302`), `FieldDef` / `FieldKind` (`:51-96`), the `engram`,
  `research`, `minimal` and `general` presets, `describe_ontology`.
- **Trust:** `crates/engram-core/src/policy.rs` — the two principles, the
  anchors, `STALE_TRUST`, `trust_override`, the `AUTO_TUNE_*` bounds.
- **Auto-tune:** `engine.rs` — `auto_tune` (`:1235`), `fit_conflict_floor`
  (`:1268`), `fit_weak_line` (`:1341`), called from `validate_graph` (`:1173`).
- **Contradiction:** `crates/engram-core/src/nli.rs`;
  `hub.rs:104` gates on a live edge carrying the graph's contradiction role
  with `valid_until` unset.
- **Consolidation:** `engine.rs` — `merge_nodes` (`:3040`).
- **Deletion:** `engine.rs` — `delete_node` (`:1915`) and
  `delete_node_with_tombstone` (`:1936`).
- **Stores:** `store.rs`, `store_sqlite.rs`, `store_tepin.rs`, `migrate.rs`;
  `seal.rs` for the at-rest codec.
- **Retrieval and delivery:** `rag.rs`, `cortex.rs`, `digest.rs`;
  `Engine::search` (`engine.rs:2535`) applies the delivery floor, the knee cut
  and the session-diverse selection, then attaches one-hop neighbours
  (`:2616`); `search_confidence` (`:2751`) returns `none | weak | strong`;
  `time_filter_clocked` (`:2692`) and `check_clock` (`:1754`) are the temporal
  grammar's boundary.
- **Redaction:** `redact.rs` — `scrub` and, for custom fields, `scrub_fields`.
- **Surfaces:** `crates/engram-mcp/`, `crates/engram-http/`, `frontend/`,
  `engram-vscode/`, the JetBrains plugin.
- **Evaluation:** `eval/src/` and `eval/results/` — 108 committed result
  files, 66 of them JSON — plus `eval/src/longmem.rs` (the LongMemEval
  adapter), `eval/src/chains.rs` (the supersession-chain bench) and
  `eval/src/sessions.rs` (the multi-session coverage bench).


## 5. Memory Data Model

`nodes` carries `id`, `type`, `title`, `body`, `durability`, `source`,
`session_id`, `created_at`, **`valid_from`, `valid_until`**, `status`,
`code_refs`, `tags`, `last_seen`, `confirmed_at`, `approved_at`, `demoted_at`,
`trust_override`, and `fields` — a JSON object of custom-field values. `edges`
carries the same temporal pair plus `confidence`, `strength`, `note` and a
`status`.

**Bi-temporality is real and used, on two axes.** `valid_from` / `valid_until`
are validity time and `created_at` is record time; `hub.rs:104` treats an edge
as live only when `valid_until.is_none()`, and `types.rs:404` documents a
neighbour as *"superseded/archived (`valid_until` set)"*. Archival is closing an
interval rather than deleting a row. The engine's axis says when a claim held
*as canon*; the second axis is the graph owner's and says when the thing
happened: a date-kind custom field, or a `from..to` pair of them, becomes the
*event clock* a search window can be aimed at (section 6), which is what a
historic import needs when everything is captured today and happened over
years.

**Custom fields are declared in the graph and validated at the write boundary.**
`FieldDef` (`config.rs:51-96`) names a field, a kind — `text`, `number`,
`bool`, `date`, `enum`, `url` — whether it is required, which types it applies
to, whether it is `indexed` (joins the note's embedding and the keyword channel,
with the indexed set fingerprinted so a change re-embeds exactly once) and
whether it is shown on brief lines. `check_fields_ext` (`engine.rs:1654`) is the
one gate every surface passes: unknown names fail, kinds must match, required
fields must be present, and reserved built-in names cannot be shadowed; a
refusal is a *teaching error* that names the whole roster and the exact call
shape, so an agent that has never seen this graph corrects itself in one step.
`update_node` merges the map and a `null` deletes a key; renaming a field moves
every stored value with the definition, as renaming a type does. The one
exception is engine-authored: the tombstone a delete mints skips required-field
enforcement, because *"field config must never veto a user's delete."*

**The trust anchors are three separate durable facts**, not one score:
`confirmed_at` (a deliberate act), `approved_at` (explicit approval), and
`demoted_at` (contradicting evidence landed). Keeping them apart is what lets the
policy say *withdrawing the evidence withdraws the demotion* — with one blended
number that operation is impossible.

**`code_refs` ties memory to the artifact it describes**, which is the property
[Magic Context](../magic-context/) is credited for here.

**There is no scope key.** No user, project or workspace column; isolation is one
graph per project directory. Coherent for an editor plugin, and it means the
schema cannot host two projects without a migration.

### What a user may reshape, and the guard on each

The pane's ontology editor writes `GraphConfig` — types, verbs, the trust and
threshold constants, and the brief composition — and three of its rules are
worth naming because each closes a way the reshape could strand data.

- **A rename is the migration gesture, not a relabel.** `rename_type` and
  `rename_verb` (`engine.rs:2427`) move the stored rows along with the name, and
  the editor's card shows how many nodes will follow.
- **A save cannot drop a vocabulary that still holds data.** Removing a type
  that has nodes fails with *"type … still has N node(s) — rename it (bulk
  retype) or retype them first"* (`engine.rs:2299`), and the same for verbs on
  edges. There is no path where an edit orphans knowledge.
- **The hard invariants survive every configuration.** Exactly one supersession
  verb and one contradiction verb must exist, or validation refuses the
  document — the graph cannot be configured into inertness. A type carrying the
  `tombstone` role may not also carry `worklist` or `anchor`
  (`config.rs:1461-1466`), because *"a tombstone is a closed record of a
  removal — it can't be open."*

Two smaller per-graph features sit in the same document. **Version tracking**
(off by default) stamps every new node of a `versioned` type with the graph's
current working version, set by the `set_version` MCP tool, so a note records
which release it was captured under; `Principle` and `Anchor` carry the
`versioned: false` role in the shipped preset, because *"a value or a code
subject transcends any single release"*, and the stamp is provenance only —
nothing in trust or ranking reads it. And a reserved `handoff` tag
(`config.rs:568`) gives an open worklist note guaranteed top placement in the
next session brief, which is reactive session-to-session memory without a new
node type.


## 6. Retrieval Mechanics

Vectors from `bge-small-en-v1.5`, a keyword weight of 0.15, and a reranker
(`jina-reranker-v1-turbo-en`) that **votes rather than decides** — a distinction
the ablation measures rather than asserts. Across every keyword weight in
`bench-100.json`, `reranker VOTES` beats `reranker DECIDES` on weighted recall
(0.991 vs 0.980 at the shipped 0.15) and on oblique questions (0.91 vs 0.80). A
reranker allowed to overrule the retriever loses obliquely-phrased hits; one that
contributes a vote does not.

The score floor is a published tradeoff curve rather than a constant.
`floor-500.json` walks twenty-one floors and reports, at each, recall@5, oblique
recall, mean results returned, mean tokens, and two decline rates — for
answerable questions and for **unanswerable controls**. At floor 0 the system
returns 9.95 results and 512 tokens and declines nothing including the controls;
by floor ~0.62 it returns 1.03 results and 55 tokens, declines 62% of controls
and 38% of answerable questions. Every operating point is priced.

Trust multiplies the score, so a stale node is buried rather than filtered — it
stays findable, which is what makes the review queue meaningful.

**Delivery is a second stage with two cuts, both reranker-gated.** `search`
(`engine.rs:2535`) fetches wide, reranks, drops everything under
`policy.delivery_floor`, truncates to the limit, then applies a *knee* cut: sort
the delivered score curve, find the largest relative drop over
`policy.knee_cliff`, and discard the tail below it. The reasoning for gating
both on the reranker is stated at the call site — the fused hybrid score is a
different scale, so a floor read against it would be read on the wrong ruler.
The consequence for every number in this report: engram's recall is measured
over a set the system has already trimmed, while the RAG arm it is compared
against keeps its full ten.

**A third cut is about provenance, not score.** When more candidates survive
the floor than fit the list, each additional hit from a session already holding
a slot is demoted `policy.session_diversity_demote` rank positions before the
final cut — two by default (`policy.rs:157`), a rank rather than a score on
purpose, because *"absolute score thresholds don't transfer between graphs
while relative mechanisms do."* It changes selection and order only; scores, the
floor, the knee and the verdict still read the cross-encoder's scale, and a
graph whose notes share one session is byte-identical to the cut without it.
Every hit carries its `session_id`, so the provenance the demotion acts on is
visible where it acts. The number was chosen from a committed sweep and its
cost is measured in section 10.

**The abstention line is fitted from probes the graph writes about itself.**
`fit_weak_line` (`engine.rs:1341`) synthesises questions that have no answer —
half question-shaped templates over vocabulary borrowed from the graph's own
node titles, half *ICT transplants*: real sentences from the store with their
subjects coined out — then measures how high the reranker's top score climbs
against each, and takes the **larger** of the two families' q90 as the fit — the
line must clear whichever register this graph's noise speaks loudest in. The fit
is then damped halfway and clamped, with the lower clamp *relative to the
delivery floor* rather than absolute, so a line that could never fire is
impossible and one noisy probe register cannot teleport it. Borrowed vocabulary
is the load-bearing part and the comment says why: generic probes under-read how
high *this* graph's scores can go, and the first live fit found in-register
questions reaching 0.32 against a 0.25 line fitted from generic wording. What
clears the line is answered; what falls below is delivered warned, never cut. **No other report in this corpus describes a
system calibrating its own "I don't know" threshold from synthesised
unanswerable queries** — [MetaClaw](../metaclaw/) is the nearest, and it replays
*real* past turns against candidate policies rather than manufacturing negatives.

**Search is time-scoped, and the window has two clocks.** A single temporal
grammar (`timespec.rs`) adds `after`, `before`, `during_version` and `order` to
the MCP `search`, applied *before* the reranker and every cut so "a scoped
verdict describes the scoped set," with ordering applied last so a time-ordered
read has the same membership as its relevance twin. `during_version` resolves a
window from the audit journal's `version_switched` rows with no new storage, and
`order: "recent"` folds a history restatement under its newest form. By default
the window reads `created_at` — *when the knowledge was captured*, and the
comment at `store.rs:562-567` explains why not `confirmed_at`: *"a node
reconfirmed last week is still July's decision."* A `date_field` selector
re-aims the same window at the **event clock** the graph's owner declared: one
date-kind custom field matches when its value falls inside the window, and a
`from..to` pair matches when the node's own validity span overlaps it, an absent
`from` reading *since forever* and an absent `to` *still valid*
(`timespec.rs:84-98`). Nodes without the field drop out, because they cannot
answer an event-time question. `check_clock` (`engine.rs:1754-1790`) refuses an
undeclared or non-date field, and a clock without a window, as loud errors —
*"an unaimed clock filters nothing and would silently return the default result
while looking like an event-time answer."* The history layer has no custom
fields, so `date_field` on `scope: "history"` is refused too.

Beneath the curated graph sits a second, sealed **episodic history store**
(`history.tepin`, one per project): the harvester tails chat transcripts from
seven assistants — Claude Code, Codex, Gemini CLI, opencode, Kilo, Antigravity,
IBM Bob — as Session/Message nodes cross-linked to curated memory by a `born-in`
provenance edge. Its isolation is physical, not a filter: curated search, brief,
drift and decay never see it (`history.rs:7-11`). Harvesting is opt-in
(`HistoryConfig.enabled` defaults to false) and the store is **sealed at rest**
by the `encrypt_history` switch, on by default — the sharper half of a
deliberate two-store split in which the curated graph is redacted and sealed
only if its owner turns the second switch. The blind keyword index gives the
history layer a BM25 channel of its own, fused with vector candidates under the
curated layer's weights. The MCP tools `expand_history` and `list_sessions`
read it on request.

## 7. Write Mechanics

A write is synchronous and returns more than an id. `WriteOutcome::Created`
carries the node, any `warnings`, and the `suspects` — look-alike pairs the write
just created — *"so the writer judges them in the same turn instead of leaving
them for the next session's brief."*

The division of labour is stated: **detection is local, judgment is the
assistant's.** Similarity and the NLI hint are computed by small local models;
the verdict — `conflict`, `replaces`, `dismiss` — is the assistant's, and the
column comment beside the NLI score says why: *"models don't validate."* A
probability is a hint, not a ruling.

Correction is a family of moves rather than a delete: a `replaces` edge, a
`conflicts-with` edge that stamps `demoted_at`, closing `valid_until` to archive,
approving, pinning, or dismissing a suspect. Every one of them appends to the
audit journal.

**Deletion leaves a trace.** `delete_node_with_tombstone`
(`engine.rs:1936-1983`) is the pane's default delete and the HTTP surface's
`DELETE /nodes/{id}?tombstone=true&reason=…`: it mints a note of the first type
carrying the `tombstone` role — title *"Removed: `<victim title>`"*, body
*"Deleted `<type>` "`<title>`" (id …)"* with the reason under **Why** — and then
cascades the victim. The tombstone is `Source::User`, stable durability so it
never decays, carries no edge to the victim — *"the victim is gone and edges never
dangle"* — and skips required-field enforcement. When the ontology declares no tombstone type
the call degrades to a plain delete — *"the config decides, never the
caller"* — and there is no MCP path to either delete. The role's own definition
says what it is for: *"records that knowledge was deliberately removed so it
isn't re-learned."* Whether anything enforces that is section 9's question.

**`merge_nodes` is the consolidation move**, and its edge cases are where the
design shows. Several notes stating one truth collapse into one survivor: tags
and `code_refs` union, live edges rehome onto the survivor, victims are archived
behind a supersession edge rather than deleted, and `MergeOutcome` reports per
victim how many edges moved and how many were deliberately left — already
present on the survivor, internal to the merged set, or an *incoming*
supersession, which is part of the victim's own story and does not travel. An
archived survivor is refused outright. And the assistant cannot merge away a
pinned node: with `source == Source::Claude` a pinned victim raises
`Error::Pinned` carrying the instruction to *"tell the user and let them merge
this pair in the pane"* — the same human-only boundary the pin draws everywhere
else. Four committed tests cover the union, the pin refusal, the
outgoing-but-not-incoming supersession rule, and a live conflict rehoming onto
the survivor.

The audit journal also carries events that are not node or edge mutations:
`audit_activity` writes rows against the entity type `session`, which is where
`graph_validated` and `auto_tuned` land — so a threshold the system moved on
itself is on the same tape as a human's approval.

**The audit journal is the richest in this corpus.** One row per node or edge
mutation, insert-only, carrying `before_json` and `after_json` in full, the
`action` from an eleven-value vocabulary (`created | updated | approved |
unapproved | pinned | unpinned | demoted | undemoted | archived | deleted |
imported`), the `origin` surface (`pane | mcp | daemon | cli | library`), and the
writing process's `session_id`, `cwd`, `pid` and `version`. `title` is snapshotted
so it *"survives deletion"*.

Knowing which surface made a change — a human in the pane, an assistant over MCP,
a daemon — is the distinction most audit logs here collapse, and it is exactly
what you need when a memory is wrong and you are deciding whether to distrust the
model or the person.


## 8. Agent Integration

An MCP server for the assistant, an HTTP surface, a JetBrains plugin, a VS Code
extension, and a standalone pane. The screenshots show the intended loop: the
graph fills in live while Claude Code works in the terminal below.

**Which project a session serves is a five-rung ladder, and the last rung is the
one to read carefully.** An explicit `--db` pins it; otherwise the bridge asks
the client for `roots/list` and binds the first `file://` root, re-resolving on
`roots/list_changed` so one db-less config entry follows a client across
workspaces; otherwise the bridge's working directory; otherwise a machine-level
**default agent project** setting; and otherwise **the home graph** — *"the
session binds the core's `/mcp` endpoint rather than dying."* Every rung is
logged, so `mcp.log` always names the one that bound.

Rung five is a deliberate trade and the report's sharpest reservation about the
process model. A session that cannot establish its workspace does not fail; it
reads and writes somebody else's graph — specifically the home one. The
mitigation is `brief` called with a `project`: a name, an id or any absolute
path inside a registered root rebinds the running session and returns that
project's brief in one call (`crates/engram-mcp/src/lib.rs:844-870`), refusing
an unregistered selector *with the known roster* and leaving the binding
untouched when it refuses, so a hallucinated path can never birth a graph.
Sessions stranded on rungs four or five get a one-line hint above their brief
pointing at it. Folding the rebind into `brief` is the field lesson from the
project's issue #4, where an injected *"call `brief` first"* overruled a
workspace rule that said `set_project` first; one tool means there is no wrong
first call left to make. The clients that need it are named in the docs —
Windsurf and Devin CLI advertise roots and never answer them — and `setup`
writes each client what it can consume: a `SessionStart` brief hook for Claude
Code, Codex, Devin CLI and Bob (Devin and Codex only accept injected context
inside a `hookSpecificOutput` JSON envelope, so the two share one wrapper), an
`always_on` rule for Windsurf, and an `AGENTS.md` block for the rest.

The pane's Processes census shows each live session's current binding. Bridges
hold a 15-second-heartbeat lease that expires after 45 seconds, so a crashed
client leaves the list within three missed beats, and a failed registration never
blocks bridging: the census is observability, not control.

The assistant's authority is broad on judgment and bounded on trust in one
place by construction and in another by instruction. It writes nodes and edges,
and it judges the suspects the write hands back. Pinning is human-only in the
code: no MCP tool writes `trust_override`, retrieval moves nothing, and a pinned
node ignores the assistant's evidence entirely until a human unpins it.
Approval is not: `approve_node` is an MCP tool (`lib.rs:1073-1080`) that
restarts trust at 100%, `Engine::approve` (`engine.rs:1873`) takes no source and
gates on nothing, and the whole restraint is the tool description — *"ONLY on
explicit user demand or after word-by-word verification against current
reality."* The audit row records `origin: mcp`, so an assistant's approval is
distinguishable after the fact; it is not preventable before it.

The pane is a genuine review surface: stale nodes queue for a decision, conflicts
are judged there, decisions are retired there, and the browser demo lets a reader
do all three without installing anything.


## 9. Reliability, Safety, and Trust

**`audit_log` — earned, and it sets the bar.** Insert-only, one row per
mutation, full before and after JSON, an eleven-value action vocabulary, the
originating surface, and process context. Deletion-surviving titles.

**`bitemporal` — earned.** `valid_from` / `valid_until` on nodes and edges
against `created_at`, used on the read path to decide what is live; and a
second, owner-declared validity axis — a date-kind custom field or a `from..to`
pair — that a search window can be aimed at instead of the capture clock, with
the boundary refusing an unaimed or undeclared clock rather than dropping it.

**`trust_state` — earned.** `suspects.status` is a persisted
`suspected | confirmed | dismissed`; nodes carry a `status` and three distinct
durable epistemic stamps, `confirmed_at`, `approved_at` and `demoted_at`, which
the policy reads separately and which the audit journal names as actions.

**`human_review` — earned.** A review queue for stale nodes, conflict judgement,
retirement, deletion and pinning, with pinning reserved to humans by the absence
of any tool that sets it. Two further gestures are human-only by construction
rather than by convention: reshaping the ontology — types, verbs, custom fields
— has no MCP write surface at all, and `merge_nodes` refuses a pinned victim
when the caller is the assistant. Approval is the gesture that is *not*: the
`approve_node` tool exists and the engine does not ask who called it, so the
line the documentation draws — *"the drawer is where you approve what you vouch
for"* — is a line the assistant is asked to respect rather than one it cannot
cross.

**`negative_eval` — earned.** The floor sweep carries unanswerable **controls**
at every operating point and reports `controls_declined`, so the evaluation
asserts that material which should not be returned is not returned — and prices
the answerable questions lost at each threshold. The LongMemEval run extends the
same discipline onto a corpus the project did not write: 30 labelled
never-answerable questions, scored on whether an answer went out unwarned.

**`tombstone` — withheld, and this is the near-miss worth reading.** The
`Tombstone` type is a durable, user-minted record of a removal, keyed on the
victim's title in its own title, stable so it never decays, and its role
definition states the purpose this mark exists for: *"so it isn't re-learned."*
What withholds the mark is that nothing on the write path reads it. The
near-duplicate short-circuit in `add_node_checked` (`engine.rs:2843-2888`)
matches only a live node *of the same type*, so a re-authored `Decision` never
lands on its `Tombstone`; `write_warnings` (`:3247`) warns only about superseded
or in-conflict neighbours, which a tombstone is neither; the conflict sweep
iterates `scannable_nodes` (`store.rs:406-418`), which excludes tombstones by
design — *"a tombstone contradicts its victim by DESIGN — that's its job, not a
conflict to surface"* — and `tombstones_sit_out_the_conflict_scan` asserts
exactly that. The one accidental path is the write-time nomination:
`suspects_near` (`engine.rs:4118`) filters anchors, archived rows, linked and
already-queued pairs and not the tombstone role, so a re-assertion whose
embedding clears `conflict_suspect_similarity` against *"Removed: …"* plus a
body beginning *"Deleted Decision"* is handed back to the assistant as a
look-alike pair to judge. That is a nomination that depends on cosine distance,
not a refusal keyed on the value; and the brief never shows tombstones
(`hidden_brief()` on the type), so the only other channel is a search hit and
the assistant's obedience to *"don't resurrect it"*. A dismissed suspect and a
`replaces` edge remain keyed on ids. The design has the record and not the gate.

**`scope_enforced` — not found.** No scope key on either table.

Other observations:

- **`redact.rs` drives the write path.** `redact::scrub` runs on title and body
  in the node write paths (`engine.rs:290-291`, `:2844-2845`) and `scrub_fields`
  on every string-valued custom field: named patterns
  (PEM/AWS/JWT/GitHub/Slack/OpenAI/`key=value`) plus a high-entropy backstop
  judged per separator-delimited segment (segments under twelve chars abstain) so
  a compound identifier is not masked. Redaction runs before anything reaches
  either store; sealing is the separate, switchable layer described in section 3,
  and the curated graph ships with it off.
- **`meta` pins the embedding model identity and vector width**, so a store read
  with the wrong embedder is detectable rather than silently wrong, and records
  the store's own `encryption_state`, so a store read without its key renders
  *"[sealed — encryption key unavailable]"* in place of a value — a placeholder,
  *"never garbage, never an error"* — rather than failing or leaking.
- **The external dataset is SHA-256 pinned and re-verified on every open**, not
  only on download, and the reason is written at the function: *"a truncated
  download must never quietly grade as a small corpus."* Both digests live in
  `longmem.rs` with a committed test asserting they are well-formed. The data
  itself is never checked in — the repository carries the loader, the digests
  and the provenance note.
- **The system moves its own thresholds.** Two auto-tune dials rewrite
  `GraphConfig` at session boundaries. Every move is damped, clamped, gated on
  volume and journalled, and a graph can opt out — but a reader comparing two
  installations should expect their delivery and conflict thresholds to differ,
  because each was fitted to its own graph.
- **The loop is scored against the people in it.** `Engine::nli_agreement`
  joins each judged suspect's stored `nli_label` with the verdict a person
  reached and reports the confusion matrix: hits, false alarms, misses, passes,
  and an agreement rate that is absent until a hinted pair has been judged.
  Surfaced as `GET /conflicts/agreement` and a Checkup panel block. Two
  properties make it worth naming. It counts **misses** — the judge confirmed a
  pair the model called entailment or neutral — so the measure is not only about
  the alarms the model raised. And it is **read-only, never a calibration
  input**: the auto-tune dials do not consume it, so the model cannot chase its
  own agreement score. The type's own comment scopes the claim to what the row
  can carry: conflict and replaces both land as confirmed, so agreement reads
  *"the hint said contradiction and the judge kept the pair"* and no finer.
  Almost nothing in this corpus measures whether its automatic nomination agreed
  with the human who adjudicated it, and the systems that do usually feed the
  answer straight back into a threshold.
- **Most numbers are self-generated.** The offline suite's graphs,
  questions and controls are the project's own synthetic corpora. LongMemEval is
  the exception and it is one corpus, graded on the retrieval half only.


## 10. Tests, Evals, and Benchmarks

`eval/` is a first-class crate with 108 committed result files, 66 of them JSON
— `bench-100.json`, `contradictions-500.json`, `floor-100/500/1500.json`,
`floor-dial3-*.json`, `longmemeval-s-*.json`, `chains-200x20.json`,
`budget-*.json`, `sessions-*.json`, `posttune-*.json` and their `.log`
companions — and this is the part of the project most worth copying.

**The ablation labels its own shipped row.** `bench-100.json` holds thirteen
configurations with a runtime stamp (`"embeddings_are_fake": false`, seed,
embedder, reranker), a corpus profile down to the verb mix and code-ref
distribution, and a phrasing mix of 45% lexical, 45% paraphrase, 10% oblique. One
row reads `"kw 0.15 · reranker VOTES   <- ships today"`, and pure RAG beats it on
recall. Publishing the row you lose, beside the row you ship, in the machine-
readable artifact, is the strongest form of the discipline this atlas credits
[Perseus Vault](../perseus-vault/) and [memsem](../memsem/) for.

**Contradiction detection is decomposed, not scored.**
`contradictions-500.json`: 100 contradictions, 97 caught, `"missed_by_retrieval":
0`, `"missed_by_judgment": 3`; 100 entailments with 78 supported. Separating a
detector's retrieval failures from its judgment failures tells a maintainer which
half to fix, and almost nothing in this corpus reports it.

**The floor sweep has controls.** Unanswerable questions at every threshold, with
`controls_declined` rising as the floor rises — so precision is never claimed
without the recall it cost.

**The process model has its own test suites**, which is the shape the rest of
the repository has.
`crates/engram-cli/tests/` carries `process_model.rs`, `roots_binding.rs`,
`session_brief_hook.rs`, `setup_windsurf.rs` and `setup_devin.rs` — the binding
ladder, the convergence of concurrent launchers on exactly one core, and the
per-client setup writers, tested as integration rather than asserted in a doc.
One of them pins a case that is easy to get wrong under lazy opening: a resolved
store survives its project being unregistered. Beside them sit three end-to-end
journeys over the real binary — `e2e.rs` (*"every test is a story a user
actually lived"*, including a version update reproduced by running one binary
as two versions), `e2e_wiring.rs`, and `e2e_encryption.rs`, which encrypts,
proves the bytes went dark, searches and reads prose throughout, restarts,
decrypts and proves the bytes are back, with the sealing key in a file fallback
so nothing touches a real keychain. The store trait has a conformance battery
of its own: `store_battery` in `crates/engram-core/src/tests.rs` runs one
sequence — nodes, edges, tags, redaction, suspects, audit — against both
backends, on the stated contract that *"whatever passed on SQLite must pass
unchanged on TepinDB."*

### The external corpus

`eval/LONGMEMEVAL.md` and `eval/src/longmem.rs` run
[LongMemEval](https://github.com/xiaowu0162/LongMemEval)-S (Wu et al., ICLR
2025, MIT): 500 questions, each over its own multi-session chat haystack of
~115k tokens, evidence sessions labelled, 30 questions deliberately
unanswerable. The receipt is `longmemeval-s-full.json` — the whole population
run, `questions_run` equal to `questions_total`, mean 493 turn-notes per store,
and the table reproduced in §1 above.

**What the design gets right, and it is most of it.**

- **The population is not sampled.** Every question, with `questions_run` and
  `capped` in the receipt so a partial run cannot be mistaken for a full one.
- **No model in the ingestion or grading path.** One note per chat turn,
  verbatim, filler included; a question counts as answered when a note from a
  labelled evidence session lands in the delivered set. Deterministic and
  judge-free, which is the same standard the offline suite meets.
- **The unflattering register is chosen deliberately and labelled.** Engram
  ships no extractor — the deployed shape is typed notes an agent wrote — so
  as-is ingestion measures the *floor* for the product, not its intended
  operating point, and the page says exactly that.
- **One embedder, five arms, identical haystacks**, so what separates the rows
  is the retrieval stack.
- **The runtime swap is verified rather than asserted.** The full run used
  bge-small served by Ollama on GPU instead of onnxruntime on CPU, to bring
  ~16 h down to ~2 h. Both smoke receipts are committed —
  `longmemeval-s-smoke20.json` and `-gpu.json` — and every arm's R@1, R@5, MRR
  and token mean agrees to four decimal places. The claim of grade-identity is
  checkable from the repository, and it holds.
- **The rows that do not flatter are published.** `whole-file` scores a perfect
  1.00 and its column of interest is the 122,515 tokens per question it costs;
  the blind 3k `curated-file` beats engram on R@1 (0.919 vs 0.909); pure vectors
  beat it on R@5.

**Three things a reader has to hold while reading the table.**

1. **The token column compares two different delivery formats.** The engram arm
   is billed for a title plus a matched snippet per hit; the RAG arm is billed
   for a title plus the *whole* turn, for a fixed ten hits. Part of the 13× is
   calibrated delivery returning fewer notes — which is a real product
   behaviour, and it makes engram's recall harder-won, since its R@5 is computed
   over a set already trimmed — and part is snippet-versus-whole-note framing.
   A vector stack that also delivered snippets would close some of that gap.
2. **Session-level grading is generous to dumps**, which the page states
   plainly: any turn from the right session counts, so a blind selection that
   happens to keep one filler line from the evidence session scores as a hit.
   The token column is the only thing separating *present* from *readable* here;
   the focus/noise metrics that do that job in the offline suite are not run.
3. **This is the retrieval half.** The published benchmark grades a generated
   answer; these numbers grade a delivery, so they are not comparable with
   published LongMemEval scores and the page says so in its second paragraph.
   The reserved online half is named as the plan of record.

**The chat ontology is the interesting part of the adapter.** Rather than
forcing the software ontology onto chat — where every turn lands as `Insight`
and the type layer contributes nothing — the run defines a two-type ontology
*entirely as per-graph data*: `statement` (a user turn, `rank_prior` 0.05, so a
first-party source outranks a restatement at equal relevance) over `reply` (an
assistant turn, no prior, muted). Role is the one distinction an as-is ingester
can make without a classifier. `the_chat_ontology_validates_and_the_engine_accepts_its_types`
asserts the engine's write boundary accepts the fitted types and refuses the
stock one they replaced. Zero engine changes — which is the per-graph
`GraphConfig` machinery demonstrating itself on a register it was never written
for, and the strongest available evidence that the "roles, never names" rule is
real rather than aspirational.

**The gap in the external run is the warn rate on answerable questions.** The
abstention result is strong — 30 `_abs` questions, 2 empty deliveries, 28
warned, 0 unwarned, weak line auto-fitted on 27 of 30 stores. But
`weak_evidence_top` is read only in the abstention branch of `run_question`; the
answerable path computes rank and cost and never asks for a verdict. So the run
prices the false-positive side of the calibrated line and not its cost, and a
line that warns on everything would also score 0.00 here. The offline suite does
measure that cost and does not hide it: `posttune-0.9.0-100-1500.json` pairs
`controls_unwarned` 0.000 with `answerable_warned` **0.473** at 100 notes, and
0.016 with 0.472 over 375 controls at 1,500. So the warning line is well-behaved
at both graph sizes the project sweeps, and the price of it is that nearly half
of answerable questions come back carrying a "likely not in memory" flag. The
1,500-note figure reads 0.011 in `posttune-0810-100-1500.json` because the blind
keyword index normalises BM25 slightly differently than per-field scoring and
the weak line re-fitted from 0.898 to 0.878; the changelog counts it as
*"4 → 7"* unwarned controls, and the receipt's 0.016 over 375 is six. Running those same two counters over LongMemEval's
470 answerable questions is a small change to `run_question`, and it would turn
the abstention paragraph from a one-sided result into a priced one — on the
corpus where it would matter most, because it is the one nobody here wrote.

### Sessions, measured against the recall they might cost

`sessions-100-500.json` plants multi-session *clusters* on top of the regular
crowd — one invented subject, one complementary aspect per session, four
entailed recaps beside each aspect in the same session — and asks one
aggregation question per subject, scoring **coverage**: how many of the
subject's sessions reach the delivered list. The regular single-gold questions
are re-asked under the same knob as the price. At 420 and 1,875 notes:

```text
demote   cov@5 (420)   cov@5 (1875)   full coverage   R@5 regular (1875)   oblique (1875)
0            0.625          0.707           0.625/0.76             0.772            0.325
2            0.792          0.827           1.000                  0.772            0.325
5            0.958          0.960           1.000                  0.770            0.322
8            1.000          0.987           1.000                  0.776            0.339
```

The single-gold columns are identical to three decimals at demote 0, 1 and 2,
and the recall cost appears only from 5 upward on the 420-note seed; the shipped
constant is *"the top of the measured free zone."* The real-data check found the
knob **inert** on the chat register: `longmemeval-s-turns50-demote0.json` and
`-demote2.json` are identical to the digit at 100 questions, because engram's
delivered list there is already trimmed to two or three hits, the pool never
exceeds the limit, and the selection never engages. The eval README says so and
says what owns the remaining gap — the delivery trims, not the cut.

### Two attacks on the delivery floor, both priced, neither shipped

The fixed `delivery_floor` of 0.22 was measured on the note register, and on
registers whose whole score scale sits lower it behaves like the hard abstention
gate the project had already refused three times. `floor-dial3-snippet.json` and
`floor-dial3-rerankfull.json` price two fixes on one sweep. *Dial three* fits the
floor per graph as a quantile of the phantom questions' score body; it is
recall-free at 100 and 500 notes and costs 0.01 R@5 and 0.02 oblique at 1,500.
*Full-note reranker input* lets the cross-encoder judge title plus whole body
and wins on the note register uncut — oblique 0.34 to 0.41 at 1,500 — and
collapses on chat: `longmemeval-s-turns50-rerankfull.json` reads R@5 0.957 to
0.777 against the same 100 questions, multi-session coverage 0.557 to 0.246,
delivery over-trimmed from 111 to 67 tokens per query. The two are antagonistic
— full-note input raises phantom scores with answer scores, so the dial-three
fit misfires on it — and the README's verdict is that neither ships as a
default: full-note input stays a per-graph knob *"refuted as a default by the
chat receipt"*, and the auto-tune dial is not written until the fit is validated
on the register it exists for, which needs a chat-register floor sweep that does
not exist yet. The 0.22 stands, with both alternatives *"priced instead of
promised."*

The `--lme-turns 50` receipts that carry those numbers are labelled: `capped:
true`, `turns_cap: 50`, `questions_run: 100` of 500, and the README says they
are *"not comparable to full-haystack numbers"*. They are a tuning loop — about
seven minutes on the GPU embedder instead of hours — and the labelled answer
sessions are always kept so a cap can never grade retrieval on an unanswerable
world.

### Supersession, measured against an ablation

`chains-200x20.json` builds ADR-shaped history — 20 chains of 3 generations,
each `replaces`-ing the last, 40 supersessions over a 660-node graph — and runs
the identical store with and without them:

```text
                 R@1    R@5   pollution  head_first  tokens
superseded      0.75   0.85       0.00        1.00     219.6
flat            0.50   0.83       0.88        0.59     292.8
rag             0.30   0.97       0.97        0.41   2,144.2
grep            0.00   0.67       0.70        0.02   2,656.8
curated-file    0.00   0.00       0.00        0.00   3,000.0
whole-file      1.00   1.00       1.00        0.00 165,115.0
```

`pollution` is the share of questions where a retired generation was delivered,
`head_first` the share where the current one won the ranking. Pure vectors have
the best R@5 on the board and deliver a retired answer 97% of the time — which
is the clearest statement in this repository of what the graph is *for*. The
receipt also records `retired_searchable: 0.0`, `retired_fetchable: 1.0`,
`history_reachable: 1.0`: retired generations leave the search path and stay one
link away.

### Levers that were tried and refuted

`budget-500.json` is six configurations × four retrieval limits over a
1,500-node graph and 858 questions, and it refutes the obvious lever. Raising
the limit from 10 to 30 moves the RAG arm's weighted recall not at all —
0.9231 at every limit — while `tokens_mean` goes 2,673 → 4,069 → 5,428 → 8,070
and `noise` climbs 0.907 → 0.968. The shipped stack behaves the same way,
0.9330 → 0.9343 across a 2.7× token increase. **Spending more delivered tokens
buys nothing measurable, in either stack.**

The same file prices the two delivery trims directly. `engram open+no-trims`
reaches 0.9257 weighted recall with `noise` 0.919 and 536 tokens; the shipped
configuration reaches 0.9330 with `noise` 0.546 and 293 tokens. Removing the
floor and knee roughly doubles both the tokens and the noise without buying
recall — which is the ablation that turns "calibrated delivery" from a claim
into a measurement. And a row that does not flatter sits beside it: `engram kw0`,
the keyword channel switched off entirely, edges the shipped keyword weight of
0.15 on weighted recall at limits 20 and 30 (0.9355 vs 0.9346).

The README keeps a standing list of mechanisms that did not survive measurement
— graph spreading activation, a deciding cross-encoder, deeper reranking, and
**hard abstention**, which was measured, priced and rejected because refusing to
return candidates costs real answers. That last decision is why the budget rows
all read `false_positive_rate: 1.0`: that field counts unanswerable questions
that returned *anything at all*, and this system deliberately always returns
something and warns instead. The metric that judges the warning is the pair
`controls_unwarned` / `answerable_warned`, and it holds its shape with scale —
0.000 / 0.473 on a 100-node graph, 0.016 / 0.472 on a 1,500-node one with 375
controls. Between one and two controls in a hundred slip through unwarned, and
nearly half of answerable questions carry a warning they did not need.

**The encryption change ships with a regression receipt.**
`0.9.0-ladder-run.log` re-measures the full ladder, 10 to 1,500 notes with real
embeddings, on the blind `_kw` keyword path, and the changelog's claim is that
it reproduces the previous note-register baselines *"to the digit"* at every
rung — R@5 0.94 and 198 tokens at 100, 0.78 and 297 at 1,500 — with sealed-state
parity asserted separately by the bit-identical-BM25 golden test. The post-tune
receipt beside it is the one that moved, by the 0.005 in the weak-line fit
described above.

Every number in this section is read from committed receipts; the two
LongMemEval smoke receipts agree field by field.

What the evaluation does not establish: what a model *does* with any of
these deliveries. Both halves of the corpus — synthetic and external — are
graded on retrieval, so the numbers price what reaches the context window and
say nothing about what an answerer makes of it. The project names that gap
itself and reserves a section for closing it.


## 11. For Your Own Build

### Steal

- **"Exposure doesn't validate."** Stamp retrieval for observability and let it
  move nothing. A trust signal fed by recall is retrieval certifying its own
  outputs, and it keeps attractive wrong notes alive forever.
- **"Time doesn't validate" — for stable knowledge.** Decay episodic and volatile
  material; hold stable knowledge flat until judged evidence lands. Age is not
  disagreement.
- **Make demotion reversible.** `demoted_at` is set by a live `conflicts-with`
  edge and lifted when that edge is resolved, dismissed or deleted. A correction
  that cannot be withdrawn makes reviewers reluctant to correct.
- **Decide which of your own signals may not act.** Drift is surfaced and
  deliberately never demotes, because a bad scan would mass-bury the graph.
  Knowing a signal is too noisy to be trusted with a write is a design decision
  worth writing down.
- **Return the conflicts from the write that created them.** Detection local,
  judgment the model's, both in one turn — instead of a queue somebody reads
  next session.
- **Log the origin surface.** `pane | mcp | daemon | cli | library` on every
  audit row answers "was this the human or the assistant", which is the first
  question when a memory turns out wrong.
- **Label the shipped row in the benchmark file.** Not the README — the data.
- **Key your engine on roles, not on type names.** `worklist`, `supersession`,
  `contradiction` as flags a configured type or verb carries is what lets a user
  rename or replace the whole vocabulary without breaking a single behaviour —
  and it is what let the same engine run a two-type chat ontology on an external
  corpus with no code change. Declare the invariants that must survive any
  configuration (here: exactly one supersession verb, exactly one contradiction
  verb) and test them against every shipped preset.
- **Fit the "I don't know" line from probes your own store generates.** Coin a
  subject that cannot exist, phrase the question in vocabulary borrowed from
  your own titles, and see how high the ranker climbs with no answer present.
  That ceiling is your abstention threshold, it needs no labels, and it moves
  with the graph — a constant fitted on someone else's corpus will not transfer.
- **Damp, clamp and journal every self-tuning move.** Half the distance to the
  fit, a stated range, a minimum delta below which nothing moves, a volume gate,
  an audit row, and a per-graph off switch. Self-tuning without those five is a
  system that silently drifts away from the behaviour you tested.
- **Publish the before/after when you fix a resource bug.** Six named stages,
  two committed JSON files, and the refuted hypotheses beside the confirmed one.
- **Make a delete leave a record, and say what the record is not.** A
  tombstone note with the victim's type, title, id and the reason is more than
  most systems here keep. Then decide whether the write path reads it; here it
  does not, and a design that says so is easier to finish than one that assumes
  the model will.
- **Ship a knob at the top of its measured free zone.** The session-diversity
  demotion was swept from 0 to 8 with the recall columns beside the gain, the
  default sits at the last value where recall did not move, and the real-data
  check that found it inert is committed next to the synthetic one that found it
  useful.

### Avoid

- **Letting a reranker decide.** Measured here across every keyword weight:
  DECIDES loses oblique recall against VOTES. If you rerank, fuse.
- **A single blended trust number.** Three separate anchors are what make
  "withdraw the evidence, withdraw the demotion" expressible at all.
- **Treating an NLI score as a verdict.** The column comment is *"models don't
  validate"*; the score is a hint and the judgment is elsewhere.
- **Reading a retrieval-graded benchmark as a benchmark score.** The offline
  suite's corpus is the project's own, and the LongMemEval run grades deliveries
  rather than answers. Both are labelled as such in the repository; a reader
  quoting the numbers elsewhere is the one who drops the label.
- **Pricing an abstention mechanism on the abstention questions alone.** A line
  that warns on everything scores a perfect false-positive rate. The warn rate
  on *answerable* questions is the other half, and where this project does
  measure it, it is 47% at both 100 and 1,500 notes.
- **Drawing a human-only line in a tool description.** Pinning here is
  human-only because no tool sets it; approval is "human-only" because a
  sentence asks the model not to. Only the first survives a model that does not
  read the sentence.
- **Comparing delivered-token counts across different delivery formats.** A
  snippet-per-hit stack against a whole-document stack is measuring two things
  at once. Say which part of the gap is fewer results and which is shorter ones.

### Fit

This suits a developer who wants project memory inside the editor, with a graph
they can see and correct, and small local models rather than an API key. The
editor integrations and the browser demo make it unusually easy to evaluate
before adopting. The configurable ontology widens that fit: the shipped preset
is software-decision shaped, but `research` and `minimal` ship beside it and a
graph can define its own type and verb set, which is the mechanism the external
run exercises.

It is single-project and has no scope key, so it is not a fit for a team store
or anything multi-tenant, and the README's own status line is *"early
development"*.

Take the policy module even if you take nothing else. It is a few hundred lines
of constants and rationale, and it is the clearest statement in this corpus of
which signals are allowed to change what an agent believes.


## 12. Open Questions

- **What does the calibrated warning cost on LongMemEval's answerable half?**
  The harness computes the verdict only for the 30 `_abs` questions. Two
  counters over the other 470 would price it.
- **What does a model do with these deliveries?** Every arm is graded on
  retrieval, so the comparison between a 208-token focused delivery and a
  2,654-token whole-turn one is a comparison of inputs, not of answers. The
  online half is planned and reserved.
- **How much of the LongMemEval result is the fitted chat ontology?**
  `--lme-ontology default` runs the stock types beside it and the page lists
  that pair as reserved, so the type layer's contribution on this corpus is
  named but not yet a number.
- **How much does the encrypted history store get used in practice?** The
  transcript-harvest layer is opt-in and physically isolated from curated recall;
  whether teams enable it, and how much it grows, is not observable from the tree.
- **What does the agreement rate read on a real graph?** The scoreboard is
  computed and rendered; no committed result file carries a value from a graph
  anyone actually judged, so the measure exists and its answer does not.
- **How often does a session land on the home graph?** Rung five is logged per
  session in `mcp.log` and the pane census shows the current binding, but nothing
  counts the fallback, so the frequency of the failure mode the ladder was built
  around is not observable from the tree.
- **What does the dial-three floor fit read on the chat register?** The project
  names the missing artifact itself — a LongMemEval floor sweep with raw score
  curves — and has said the auto-tune dial waits for it.
- **How often is a tombstoned claim re-learned?** The role's purpose is that it
  is not, nothing on the write path enforces it, and no committed test or
  receipt writes a claim, tombstones it and re-asserts it.
- **What happens to a pinned node that is genuinely wrong?** Evidence events skip
  it by design; contradictions surface for review, and nothing forces the review.


## Appendix: File Index

**Schema and types**
- `crates/engram-core/src/schema.rs`, `types.rs`, `id.rs`

**Ontology and per-graph configuration**
- `config.rs` — `GraphConfig`, `OntologyConfig`, `TypeRoles` (including the
  `tombstone` role), `VerbRoles`, `FieldDef`, `FieldKind`, `presets()`,
  `describe_ontology`

**Trust, judgment and calibration**
- `crates/engram-core/src/policy.rs`, `nli.rs`, `hub.rs`; `engine.rs` —
  `auto_tune`, `fit_conflict_floor`, `fit_weak_line`, `validate_graph`

**Stores**
- `store.rs`, `store_sqlite.rs`, `store_tepin.rs`, `migrate.rs`, `registry.rs`
- `seal.rs` — the at-rest codec, the machine key, `EncryptionState`, the blind
  keyword tokens
- `timespec.rs` — the temporal grammar and `TimeClock`

**Retrieval and briefing**
- `rag.rs`, `cortex.rs`, `digest.rs`, `engine.rs`, `harness.rs`

**Inference runtime**
- `onnx.rs` — session policy, batch width, thread and arena knobs

**Safety**
- `redact.rs`, `error.rs`

**Surfaces**
- `crates/engram-mcp/`, `crates/engram-http/`, `frontend/`, `engram-vscode/`

**Runtime and process model**
- `crates/engram-cli/src/lazy.rs`, `main.rs`, `setup.rs`, `doctor.rs` — the core
  spawn, the bridge, the one-shot REST clients and the per-client setup writers
- `crates/engram-core/src/settings.rs` — the machine-level default agent project
- `crates/engram-core/src/store.rs` — `resolve_db_path`, the `graph.db`/`.tepin`
  resolution every registry consumer has to go through
- `docs/runtime.md`, `docs/multi-project.md` — the process map and the binding
  ladder
- `crates/engram-cli/tests/` — `process_model.rs`, `roots_binding.rs`,
  `session_brief_hook.rs`, `setup_windsurf.rs`, `setup_devin.rs`, `e2e.rs`,
  `e2e_wiring.rs`, `e2e_encryption.rs`
- `install.sh`, `install.ps1`, `hooks/` — the fetch-and-stop installers and
  the portable brief hook scripts

**Evaluation**
- `eval/src/` — `longmem.rs` (LongMemEval adapter), `chains.rs` (supersession
  chains), `sessions.rs` (multi-session coverage), `generate.rs`, `arms.rs`,
  `run.rs`, `ollama.rs`
- `eval/LONGMEMEVAL.md`, `eval/README.md`
- `eval/results/` — `bench-100.json`, `contradictions-500.json`,
  `floor-100/500/1500.json`, `longmemeval-s-full.json`,
  `longmemeval-s-smoke20.json` and `-gpu.json`, `chains-200x20.json`,
  `budget-50/100/500.json`, `posttune-0.9.0-100-1500.json`,
  `posttune-0810-100-1500.json`, `sessions-100-500.json`,
  `sessions-100-seed2/3.json`, `floor-dial3-snippet/rerankfull.json`,
  `longmemeval-s-turns50-demote0/demote2/rerankfull.json`,
  `0.9.0-ladder-run.log`, `ladder-100/1500-enriched.json`,
  `mem-daemon-before/after.json` and logs
- `scripts/mem-probe.sh`, `scripts/screenshots.sh`

**Searches that ground the absence claims above** (run at the pinned commit):
- `rg -n 'roles.tombstone' crates/engram-core/src/` — hits in `config.rs`,
  `store.rs:415`, `store_sqlite.rs:1142` and `engine.rs:3874` (answer
  candidacy) only; none in `add_node_checked`, `write_warnings` or
  `suspects_near`.
- `rg -n 'trust_override|set_trust_override' crates/engram-mcp/src/lib.rs` —
  one hit, the read-only `pinned` filter in `list_nodes`; no tool sets it.
- `rg -n 'async fn approve_node' crates/engram-mcp/src/lib.rs` — one hit.
- `rg -n 'set_graph_config|rename_field|rename_type|PUT /config'
  crates/engram-mcp/src/lib.rs` — test-module hits only; no ontology or
  field-definition write tool.
- `rg -l agreement eval/results/` — empty; no committed value for
  `nli_agreement`.
- `rg -n -i 'arxiv|bibtex|@article|doi\.org' README.md docs/ eval/` — the
  TAA-k citation in the eval README and LongMemEval; no paper for engram
  itself, and no `CITATION.cff`.
- `rg -n 'tombstone' crates/engram-core/src/tests.rs` — four cases, none of
  which writes a claim after its tombstone and asserts on the outcome.

## History

**2026-09-04** — [`f13d45a90391aa0d7a8986cfd79f8246ac607f9c`](https://github.com/techtheist/engram/commit/f13d45a90391aa0d7a8986cfd79f8246ac607f9c) — re-pinned at release v0.9.1 (142 commits, ~31,000 lines of Rust across four crates, ~45,000 with their test modules). Screened again first: three auto-run surfaces (`.claude-plugin/`, `.claude/settings.json`, `hooks/`), four files inside the seven-day cooldown, two unpinned surfaces, a `CLAUDE.md` addressed to a reading agent; nothing was installed, built or run. No capability mark moves. What moved upstream: a `tombstone` type role and a delete that mints one, custom fields with a graph-declared event clock on search (`date_field`), at-rest encryption as two machine switches with a blind keyword index that keeps BM25 identical, session-diverse delivery at the cut, `brief` absorbing `set_project`, installers that stop after fetching the binary, setup writers for Devin CLI, Codex, Windsurf and Bob, three end-to-end suites over the real binary, and the sessions bench, the delivery-floor bake-off and the 0.9.0 regression receipts under `eval/results/`. The `bitemporal` evidence gains the second axis; `tombstone` is withheld with the near-miss named — the record exists and the write path does not read it. Three published claims were wrong at every earlier pin and are corrected in the body: approval was described as an act the assistant cannot perform, and `approve_node` has been an MCP tool since the first reading with no source gate behind it; storage was described as SQLite with a TepinDB backend beside it, and every new graph has been born on TepinDB since v0.6.2 (21 July 2026), with the SQLite driver a migration source — the project's own docs said `graph.db` until the v0.9.1 sweep, which is where the reading took it from; and the open question *"does the TepinDB backend match the SQLite one … no parity comparison found"* named a `store_battery` conformance test that has run both backends since v0.6.0. The stack row is promoted from seeded to reviewed with a graph arm for the one-hop neighbours every hit carries.

**2026-08-22** — [`2605d84246c44c258b0d0f12a555980eb6a7456f`](https://github.com/techtheist/engram/commit/2605d84246c44c258b0d0f12a555980eb6a7456f) — re-pinned at release v0.8.9 (112 commits, ~27,800 lines of Rust across the crates, 38,700 with their test modules). Screened again first: three auto-run surfaces, two files inside the seven-day cooldown, two unpinned surfaces, and a `CLAUDE.md` addressed to a reading agent; nothing was installed and no test was run. The trust engine did not move — `policy.rs`, `nli.rs`, `rag.rs`, `cortex.rs` and `digest.rs` are unchanged — and no capability mark changes. The release is a process model: one machine core holding every store, an MCP server that is always a bridge, a five-rung project-binding ladder whose last rung is the home graph, a `set_project` tool for clients that advertise roots and never answer them, and four new integration test files under `engram-cli`. `Engine::nli_agreement` adds a read-only confusion matrix of the model's hint against the human's verdict, deliberately excluded from the auto-tune inputs. `resolve_db_path` now mediates every registry read, after stale `graph.db` entries made live TepinDB stores report as missing. Section 3 gains the runtime topology and section 8 the binding ladder, which is where the consolidation costs something: separation between projects was a property of the process layout and is now a property of routing.

**2026-08-15** — [`15fbe809ddfd744c161cb49a4b0014d96693cceb`](https://github.com/techtheist/engram/commit/15fbe809ddfd744c161cb49a4b0014d96693cceb) — re-pinned at release v0.8.7 (98 commits, ~30,200 lines across the three core crates / 33,500 with `engram-cli`; `engram-mcp` 3,046→3,778). Screened again; the `.claude/settings.json` auto-run surface is still present, nothing installed or run. No capability mark changed: all five hold, and time-scoped search — the headline addition ([`719f7b56d03940b959a843131e6455a6ee9894fc`](https://github.com/techtheist/engram/commit/719f7b56d03940b959a843131e6455a6ee9894fc)) — filters the record-time (`created_at`) axis with recency ordering, not a new validity axis, so `bitemporal` is not upgraded. Two additions are new context: a sealed, opt-in, XChaCha20-encrypted **episodic history store** that harvests seven assistants' transcripts ([`40b919bfc20373951337273aff7a2452391c4324`](https://github.com/techtheist/engram/commit/40b919bfc20373951337273aff7a2452391c4324) accelerates its sweep with fs-notify), physically isolated from curated recall; and a **time-scoped search grammar** over both layers. Two prior claims are corrected: `redact.rs` is now traced to the node write paths (with a per-segment-entropy fix), and "deliberately little background" is qualified by the new harvester daemon. The `engram-cli` crate was added. No paper for engram itself; the only external citation remains LongMemEval.

**2026-08-09** — [`cbc6f0b867d8858ba6795b516bf9baf7f852426d`](https://github.com/techtheist/engram/commit/cbc6f0b867d8858ba6795b516bf9baf7f852426d) — ten commits past the previous pin, covering releases 0.8.2 and a drafted 0.8.3. Two published claims were wrong in the same direction and are corrected here. **The ontology was described as a fixed set of eight node kinds; it is per-graph configuration** — `config.rs`, unchanged since the previous pin, stores types and verbs as a document inside the graph, engine logic keys on roles rather than names, three presets ship, and the hard invariants are asserted by test. The same document carries version stamping and the reserved `handoff` tag, a rename bulk-retypes the rows it renames, and `docs/customization.md` described all of it at the previous pin. **Auto-tune was not described at all**, though both dials predate the previous pin: dial one fits the conflict floor from judged suspects, dial two fits the abstention line from synthesised unanswerable probes, and both run at session boundaries under damping, clamps, volume gates and an audit row. The report also read *Alpha* as a maturity label; it is part of the product's name — the marketplace id is `techtheist.engram-alpha` and the binary is `engram-alpha` — and the stability statement the repository actually makes is its README status line. What moved upstream: LongMemEval-S at full population, the first external corpus, under a chat ontology defined purely as per-graph data; `merge_nodes` with four committed tests; a supersession-chain bench with a no-supersession ablation; budget sweeps that refute the spend-more-tokens lever; and an inference batch-width cap with a before/after daemon-memory receipt. The open question "how does any of it perform on a corpus the project did not generate" is answered and removed; the criticism replacing it is narrower — the external run prices the false-positive side of the calibrated warning line and not its cost on the 470 answerable questions. Screened before reading: 1 auto-run surface (`.claude/settings.json` hooks), 0 build-time exec paths, 2 unpinned dependency surfaces and 4 inside the seven-day cooldown. Nothing was installed, built or run; the committed receipts were read, and the CPU and GPU smoke runs compared field by field.

**2026-08-06** — [`5721848af9fe4adc28ff08dce5bda6cfc3f24a37`](https://github.com/techtheist/engram/commit/5721848af9fe4adc28ff08dce5bda6cfc3f24a37) — first reading. The slug is `engram-alpha` because `engram` is taken by [a different project of the same name](../engram/); the two are unrelated. Screened before reading: 1 auto-run surface, 0 build-time exec paths, 2 unpinned dependency surfaces and three inside the seven-day cooldown. Nothing was installed, built or run; the committed evaluation artifacts were read, not regenerated.

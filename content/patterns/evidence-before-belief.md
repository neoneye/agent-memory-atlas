---
title: Evidence Before Belief
eyebrow: Pattern · Provenance
description: Persist raw events and source text before deriving the compact memories that influence an agent.
root: ../..
page_kind: pattern
stance: reporting
---

## Intent

Keep the material from which a memory was derived. Treat compact facts, profiles, summaries, and graph relations as interpretations that can be inspected and recomputed.

## The problem

Extraction is lossy. A short claim can omit qualifiers, invert who said what, flatten uncertainty, or preserve a model hallucination. If the source event is discarded, correction becomes guesswork and a new extractor cannot repair old state.

## The pattern

Write evidence first, then derive memory:

```mermaid
%% caption: raw evidence is durable and indexed first; candidate facts, profiles and summaries are derived from it, so recall can be traced back to a source span
flowchart TD
    A["Message, file, tool result"] --> B["Durable event"]
    B --> C["Evidence chunks + source spans"]
    C --> D["Candidate facts, profile, summary"]
    C --> E["Lexical and vector indexes"]
    D --> F["Trust and conflict policy"]
    E --> G["Recall"]
    F --> G
    G --> H["Source-linked context"]
```

Evidence needs stable identity, scope, actor, timestamp, source location, and content hash. Derived records reference evidence IDs rather than copying an unattributed excerpt into a mutable field.

Retrieval should retain a direct path to evidence. Derived structures may boost or organize evidence, but should not make the original unreachable.

## Why it works

- Wrong memories can be explained and corrected.
- Extractors and embedding models can be upgraded without losing the corpus.
- Multiple interpretations can coexist over one source event.
- Users can distinguish “the source said this” from “the system inferred this.”
- Deletion can enumerate raw and derived artifacts explicitly.

## Tradeoffs

Raw evidence increases storage, privacy exposure, and retrieval noise. Evidence retention needs access control, retention windows, source-aware deletion, and bounded context assembly. Keeping a source is not the same as proving it is true; provenance answers “where did this come from?”, not “should I believe it?”

## Cost to adopt

**Build:** an append-only evidence store, stable references from derived records
back to it, and a rebuild path that can regenerate derivations from evidence.

**Forces elsewhere:** storage grows with raw volume rather than with distilled
volume, and the evidence store inherits the strictest retention and privacy
requirements in the system — deleting a user now means deleting from evidence
*and* everything derived from it.

**Ongoing:** the rebuild path decays unless exercised, so it needs to be run
regularly rather than kept for emergencies.

**Skip it if** the raw material is already durable somewhere you control (a
transcript store, a git history) and you can reference it rather than copying
it.

## Seen in the atlas

### Read these first

- [sift-kg](../../systems/sift-kg/) — a retained extraction layer the graph is rebuilt from, and the rebuild that undoes every correction applied to the artifact instead of its input.
- [MemMachine](../../systems/memmachine/) — one citations array on every derived feature, pointing at retained episodes: the cheapest backward link, and how merging turns it into a bibliography.
- [elizaOS](../../systems/elizaos/) — the source revision each fact was read from, so an edited source withholds the fact from every reader and queues it for re-extraction.
- [Daimon](../../systems/daimon/) — evidence referenced rather than copied, with the quote checked against the cited message at write time.
- [Memobase](../../systems/memobase/) — the counterexample: the transcript is hard-deleted once the profile is written, so the lossy derivation is the only copy.

### Every instance

[sift-kg](../../systems/sift-kg/) is the pattern implemented without being
named, and the case that shows what it does not cover. Extraction output is kept
per document under `extractions/`, every entity node carries `source_documents`,
every relation carries an `evidence` quote, and `sift build` reconstructs the
graph from that layer rather than mutating it — so a bad extraction is
traceable and the derived store is honestly disposable. The gap is that the
*corrections* are not part of the retained layer: merges and rejected relations
are applied to the rebuilt artifact, and the rebuild reads only the extractions,
so every human judgement is undone by the command that grows the corpus.
[Corbell](../../systems/corbell/) has the same shape one level up — a `Decision`
lifted from a team's ADRs keeps its `source_file`, and the flag recording which
documents a person approved is overwritten by the next scan.

**The rule both of them establish: retaining evidence makes a projection safe to
rebuild, and it makes nothing else safe.** A decision about the projection has to
live in the rebuild's input or it is a scheduled undo — which is a test worth
requiring: apply a correction, run the regeneration, assert the correction held.

[nanobot](../../systems/nanobot/) states the principle more plainly than this
page does. Its documentation says of the append-only summary archive:
*"It is not the final memory. It is the material from which final memory is
shaped."* The layout enforces it — `memory/history.jsonl` holds evidence,
`SOUL.md`/`USER.md`/`memory/MEMORY.md` hold belief, and only the Dream pass moves
material from one to the other.

[CowAgent](../../systems/cowagent/) gets the same separation from the calendar:
conversations become dated `memory/YYYY-MM-DD.md` files, and only distillation
turns those into `MEMORY.md`. The daily files remain. Bucketing by day is cruder
than a cursor and considerably easier for a human to inspect — "what did it learn
on the 14th?" is answerable by opening a file.

[GenericAgent](../../systems/genericagent/) keeps raw sessions beneath three
distilled layers in `L4_raw_sessions/`, archived on a 12-hour cron. Beside the
retention it states an admission rule as an axiom: *"No Execution, No Memory"* —
nothing enters durable memory unless it came from a successful tool call, with
model guesses, unexecuted plans, and unverified assumptions explicitly forbidden.

[AIMAOS](../../systems/aimaos/) makes the same separation structural in the
cheapest way available: raw conversation chunks are their own storage category,
and that category is listed in `DECAY_EXEMPT_CATEGORIES` so every pruning and
confidence rule skips it by construction. The comment states the invariant —
raw chunks are *"the raw source material that nightly review forms beliefs FROM —
pruning one silently deletes history no later pass can recover"*. **A decay pass
cannot forget to exempt a category it was never given**, which is a stronger
guarantee than a `is_evidence` flag every future query has to remember to check.

[Helix AGI](../../systems/helix-agi/) has the separation and shows what it costs
when only half of it is wired. Memories live in an append-only journal and
beliefs are derived from them nightly, with `memory_refs` on every belief and a
`get_justification_chain` that walks back to the material — real provenance, of
the kind this page asks for. But **the evidence layer never learns about a
deletion**: removing a belief rewrites its category file and clears the runtime
indexes while the journal keeps the content, and `preconscious._resolve_memory_content`
falls back to the journal when the belief store misses. Keeping the evidence is
what makes a wrong belief repairable; it is also what makes a *deleted* belief
recoverable, and those are the same property viewed from two sides. **A system
that retains evidence owes a deletion path that reaches it** — otherwise the
pattern's benefit and its worst failure are the same mechanism.

[MemPalace](../../systems/mempalace/) is a verbatim-first design
— extracted structures are navigation aids, drawers are authoritative.
[Cognee](../../systems/cognee/) retains source data below its projections and can
rebuild them; [Graphiti](../../systems/graphiti/) keeps episodes behind edges;
[Hindsight](../../systems/hindsight/) links observations to source facts;
[Honcho](../../systems/honcho/) derives representations from a retained message
stream; [Basic Memory](../../systems/basic-memory/) keeps human-authored Markdown
canonical.

The recurring failure is not losing evidence but **failing to link back to it**.
nanobot's durable claims do not cite the `history.jsonl` cursors that produced
them; CowAgent's `MEMORY.md` entries do not name their daily file;
GenericAgent's action-verified axiom leaves no record of the tool call that
justified a write. Evidence retained but unlinked supports recomputation and not
explanation.

[MemMachine](../../systems/memmachine/) is the plainest demonstration that the
link is cheap. Every derived `SemanticFeature` carries
`metadata.citations: Sequence[EpisodeIdT]`, written by `_apply_commands` on each
ADD, and the episodes are retained, so the citation resolves to text rather than
to a dangling id. One array column converts a store that can recompute into one
that can explain. Two cautions come with it, both visible in the code. Retrieval
takes a `load_citations` flag that defaults off, so provenance is available and
not automatic — a caller who never sets it gets the same unlinked experience as
the systems above. And every consolidation pass unions the citations of the
features it merges, so a long-lived feature ends up citing dozens of episodes:
the link never breaks, it just stops being a pointer and becomes a bibliography.
If you adopt this, keep the pre-merge rows or record which input contributed
which clause.

[Daimon](../../systems/daimon/) is a counter-example to that failure,
and it gets there without storing the evidence at all. It keeps no copy of the
transcript: a checkpoint carries a hash of the source bytes, and each verbatim
item carries the quote plus the id of the host message it came from. The link is
the whole mechanism, and it is **checked rather than recorded** — at write time
the quote is matched against the cited message, a resolvable-but-mismatched
binding is *dropped* rather than stored as false provenance, and a quote found
nowhere in the transcript costs the item its trust class.

That is a different bargain from the one this page describes, and worth naming
as its own option. Referencing evidence instead of copying it keeps the store
small, keeps the strictest privacy obligations with whoever already holds the
transcript, and makes the link falsifiable at the moment it is created. What it
gives up is exactly what this page's "Skip it if" clause anticipates: when the
host rotates its transcripts, the derivation can no longer be rebuilt or
re-checked, and the verification stamp on the item becomes the only surviving
evidence that a check ever happened. Reference evidence you control; copy
evidence you do not.

[MIRIX](../../systems/mirix/) is a cheap instance to copy: one `raw_memory`
table holding the unprocessed context string, embedded and searchable in its own
right, beside six typed derived tables. No lineage graph — just the
source kept where a bad extraction cannot destroy it. What it does not do is link
the derived rows back to it, so the evidence is searchable but not attributable.

[Memobase](../../systems/memobase/) is the deliberate inversion, and it is the
useful counterexample because the reasoning is sound. `persistent_chat_blobs`
defaults to `False`, so the source transcript is hard-deleted from Postgres once
the profile is written. For a service holding other people's conversations that is
a defensible privacy posture — and it means the profile, which is a lossy LLM
derivation rewritten in place, is the only copy there has ever been. This pattern
and data minimization are in genuine tension; Memobase is where the price of
choosing the other side is clearest.

[CSM](../../systems/csm/) has the provenance half that Helm, below, lacks, and adds
a gate the rest of this section does not: **evidence diversity, not just evidence count.** A
promotion candidate carries `source_packet_ids` pointing back to rows in
`experience_packets`, and `BeliefPromotionEngine` joins those ids to
`experience_packets.session_id` and counts *distinct sessions* before promoting.
That separates a pattern from a loop — one runaway session can reinforce the
same candidate fifty times and still be a single observation, which a threshold
on raw occurrences reads as overwhelming evidence.
Each decision also carries a `thresholdChecks` object recording
actual-versus-required for all five gates, so a promotion report explains its own
refusals; and a candidate with any contradiction returns `needs_review` rather
than a silent skip.

Two things blunt it at the pinned commit. The engine ships **disabled and
dry-run by default**, and `minSessions` defaults to `1`, which makes the gate
that distinguishes this implementation a no-op until an operator raises it. A
threshold whose default value disables it is a design that has been thought
through and then not committed to — and the number to ship is the one that makes
the mechanism do something.

Worse, and more general: the parallel belief store, which the engine never writes,
declares `candidate | promoted | rejected | stale`, the injected beliefs layer
admits only `promoted`, and **no code path writes `promoted`** — so the store
is built, maintained, decayed and contradicted, and terminates in a state
nothing can enter. Evidence-before-belief has a last mile that is easy to leave
unbuilt precisely because the interesting work is upstream of it: if you build
the ladder, commit a test that something can climb it.

**[Claude Self-Reflect](../../systems/claude-self-reflect/) keeps the evidence in a form a later pass can re-check rather than re-derive.** Its `witness_ledger` is insert-and-query only by module contract — *"a witness that no longer holds is superseded by inserting a NEW row … never by mutating the old one"* — and each row is a BLAKE3 stamp of a symbol span anchored to a commit oid. The belief layered on top, a `witness_verdicts` event saying an anchor is obsolete, superseded or reinstated, is a pure function of those stamps and git commit-graph ancestry, so any reader can recompute it, and the verdict carries the commit that proves it into the search-facing annotation. The raw material is never consumed either: the transcripts stay where the harness wrote them and a lost database is rebuilt by re-import. What it does not keep is the other direction — a `<private>` tag applied after the fact cannot reach a chunk already stored, because no user-reachable path deletes one.

[Signet AI](../../systems/signetai/) enforces the separation in the schema and then again at the write gate. A `memory_kind` column splits rows into episodic evidence — anything not produced by the daemon's own derived source types — and derived state, and the MCP store tool's description tells the model that a save is *"immutable episodic evidence"* and that a structured payload is *"retained alongside the content as evidence but is not applied to the graph from this tool"*. The gate is in code, not the prompt: `citeEvidence` resolves each claim operation's quote and source ref against the episodic store, scoped by agent, and requires the credential-redacted text the model was shown to contain the quote; `validateRequestBeforeWrites` refuses the whole batch on the first citation that does not resolve. What distinguishes it from the other instances here is the refusal ledger — the exclusion row records the failure with a class of `quote_mismatch`, `scope_mismatch`, `source_projection` or `incomplete_transcript`, a retry count and a requeue timestamp, so an ungrounded belief is a work item rather than a silence. When a cited source is edited, its claims stay and each one whose quote no longer appears is queued for the next pass to re-check.

[elizaOS](../../systems/elizaos/) carries the backward
link this page asks for, and closes the loop the others leave open. Every
extracted fact stores `extractionEvidenceIds` — which messages produced it — and
`extractionSourceRevisions`, a map from source message id to **the revision that
was read**. That second field is what turns provenance into a mechanism rather
than a record: `reviewChangedExtractionSources` compares each unconfirmed, non-`MEMORY` fact's stored
revisions against the current ones and marks any whose sources were edited
or removed `extractionReviewRequired: true`, then a reconciliation pass sets
`extractionStatus: "source_invalidated"`, stamps the reconciliation id and the
changed source ids, and adds those sources to a reprocess queue. A read-side
predicate, `isActiveMemoryEvidence`, then withholds the fact from the FACTS
provider, from the long-term memory service and from the write-time dedupe pool.
So a belief whose evidence stopped saying what it said is out of the prompt
without anybody noticing it was wrong, and the source is queued to be read
again.

Two details are worth copying beside the shape. The retirement write throws a
typed error rather than continuing — *"Derived fact could not be retired"* — so a
failed invalidation is loud instead of leaving a stale belief live. And a
historical backfill marked `extractionBackfill` attaches provenance to a
rediscovered row **without** treating old evidence as reconfirmation, which is
the distinction between learning where a belief came from and deciding it is
still true.

Where it stops is the value. Retirement is keyed on the row, and the write-time
dedupe opens its loop with `if (!isActiveMemoryEvidence(candidate)) continue;`,
so a retired claim does not block the identical text being written again as a
new fact — see [rejected-value tombstone](../rejected-value-tombstone/).

[Emulo](../../systems/emulo/) retains evidence strictly, and shows the same gap. Every rule reaches verbatim quotes bound to the dated message they came from, and the profile is rebuilt from cached, content-addressed worker reports. There is no correction in the retained layer: a hand edit to the active profile fails its hash, and re-mining over unchanged reports reactivates the same version. The rebuild also consumes the host's log retention, so evidence that rolls off disk takes its rules with it at the next update — deletion upstream acts as a forgetting policy nobody chose.

[Memseek](../../systems/memseek/) enforces the pattern at the write boundary. `compile_candidate_set` rejects any citation outside the rows a derivation was shown, and the commit refuses the write if a shown source has gone. Every derived row carries `derived_from = (run_id, *citations)`, the graph erasure walks. The limit: its agent-memory catalog records supersession only as an id array on the newer row, so the stale belief stays in recall.

[Mnemosyne (28naem-del)](../../systems/mnemosyne-28naem-del/) makes the evidence graph the eligibility rule. A record declares its dependencies, `correct()` marks every record reachable over them `invalidated` in the same transaction, and the context compiler walks each candidate's provenance before top-k, withholding it when any ancestor is untrusted, inactive, has a failed outcome or holds a disagreeing fact key (`src/local/index.ts:2797-2834`, `:1151-1190`, `:3144-3165`). The limit is the edge nobody declared. Co-use inference proposes it and writes nothing until `mnemosy dependencies --review` accepts it under a typed reviewer name, and the premise guard that would hold a procedure in between is called only by the evaluation runner.

[Noosphere Lite MCP](../../systems/noosphere-lite-mcp/) re-derives the evidence at every read instead of trusting the stored copy. A claim keeps a JSON pointer, the value it found and the source's SHA-256, and the evidence query re-hashes the source, re-reads the pointer, checks every `derived_from` ancestor's status and runs a live Git check on each anchor before returning it, with a discard count per reason (`noosphere_lite/evidence.py:140-256`). Two values for one key are both withheld. The limit is that the claim lane is opt-in: ordinary notes reach search and context labelled unreviewed, and the same value written as a note passes no gate.

[LCM-X](../../systems/lcm-x/) moves the check into the database. An assertion insert aborts unless its quoted span equals the source message's substring at the stated offsets, and an update or deletion of the message marks every receipt derived from it `source_updated` or `source_deleted` by trigger, so default reads drop the claim whichever code path changed the source (`db_bootstrap.py:2208-2292`). The retained evidence is the raw row, and a model-proposed `supersedes` must quote an explicit update word from it. The gap is the other direction: invalidation hides the derived row and keeps its verbatim quote, so deleting the evidence does not delete what was derived from it.

[Agentic GraphRAG](../../systems/agentic-graphrag/) holds an agent's decisions to the version of each document they read. A decision is refused unless every document support was fetched in the same run with status `ok`, and the support stores the content hash and activation sequence it saw (`agrag/decisions.py:924-976`). The cutover that activates a new version flags every active decision citing that document in the same transaction (`agrag/cypher/documents.py:139-170`), and clearing the flag requires a fresh fetch at the current hash. The built-in agent holds the reaffirm tool, so the check proves the text was read, not that a person judged it.

**[Praxi-Bot](../../systems/praxi-bot/) checks the quote in code, twice, against two different texts.** Each extracted candidate must carry a quote that is a whitespace-normalised span of the excerpt the model was shown, or it is dropped with a reason (`crates/memory-store/src/pipeline.rs:236-257`). The model's own `memory_save` tool is held to a narrower text: the quote must appear in a user message of the current run that is not marked untrusted, never in a tool output or an assistant message (`crates/memory-store/src/tools.rs:566-585`). The background path's excerpt includes the assistant's final answer, so a quote from the model's own reply passes there and would not pass the tool. The quote and source chat are stored on the row.

[Mem-Forever](../../systems/mem-forever/) checks an owner quote against the transcript by hash. `evidence add --transcript` stores a quote as `owner_verbatim` only when the first eight hex characters of its SHA-256 match a `type: user` turn of a Claude Code JSONL, or one of its paragraphs; without a match it is `owner_claimed`, and `provenance repair` downgrades any `by:owner_verbatim` block whose `q:` is unbacked (`tools/brain.py:3528-3603`, `:3621-3642`, `:3702-3705`). The check covers one source value of three: `by:owner_confirmed` needs no quote at all, and `evidence confirm`, the owner's backing, is a command the agent can run (`:3643-3678`).

[STUAIM](../../systems/stuaim/) checks the source at read time, twice. `validated_memory_query` answers a MemPalace hit only through a reviewed registry row keyed on the source path and the hash of the claim's normalized text, re-hashes a local source against the row's `source_sha256`, and returns the row's `safe_text` rather than the retrieved chunk (`adapters/pi/memory/validated_memory_query.py:131-182`); the preparation packet re-hashes every cited local file when it reaches the model (`adapters/pi/project-workflow/pi-kanban.ts:426-433`, `:457-466`). A closeout carries the hash of the supervisor receipt it was written against. The evidence end is missing: the registry is created as an empty file with its hash pinned, no code adds a row, and every validated query abstains in an install.

### Related: admission gates rather than evidence

These decide what may become a belief — a shared derivation, a confirmation turn,
a confidence cap, a provenance class — rather than keeping the material a belief
came from. They sit beside the pattern, not inside it.

[Atomic Agent](../../systems/atomic-agent/) links two derivations to each other
rather than a derivation to its source: a lesson and its procedure are derived
from the **same consolidator cluster** in one LLM call, so the how-to and the why cannot drift apart.

[Nova AI](../../systems/nova-ai/) separates a parse from a belief with no model
on any running path, which makes the boundary unusually easy to see. A
sentence parsed into a candidate relation is held in a single `pending_relation`
and is **not stored**; it becomes a belief only when the user types "ja" to a
question asked in plain language — *"Mag ik onthouden dat 'X' is een soort van
'Y'?"* — with the sense disambiguated first, by number, if the word has more than
one. An unparseable answer re-asks rather than defaulting. The boundary covers
the user's own sentences only: `_auto_extract_is_a` and the Wikipedia teacher
append `unverified` edges from definitions without asking. A person promotes
one later from the uncertainty list, which numbers unverified relations and
confirms or rejects one per typed answer, and relations proposed from Wikipedia
or by embedding similarity are stored only when the user picks them. With no model to distrust, the pattern here is the
recognition that a parse and a belief are different objects, and it costs one
conversational turn taken at the moment the user still has the context to
answer.

[Helm](../../systems/helm/) has the belief half of this page and not the evidence
half, and the split is worth studying. The belief side is right: a write
tagged `--source observed` is capped at 0.7 confidence regardless of what the
caller asked for, unless it passes `force`, and rises 0.05 each time the same
value is written again, so a single sighting cannot be recorded as certain.
Nothing checks that a repeat is independent: any write of the same kind, key and
value increments `evidence_count`. That is the whole gate, in about
fifteen lines of arithmetic on a SQLite row.

The evidence side is missing, and the consequence is precise. Episodes are
retained, but no fact links to the episodes that produced it — the `links` table
that could express it is created and never written. So a distilled row reading
`mentioned in 5 episodes` is a claim about evidence that cannot name any of it,
and a fact whose confidence has ratcheted to 0.9 across five corroborations
cannot be audited back to a single one of them. Corroboration is the affordable
half of this pattern and provenance is the load-bearing half: without it,
repeated exposure to the same wrong value is indistinguishable from evidence,
and a bad belief can be raised but not traced.

[Ouroboros](../../systems/ouroboros-agent-os/) supplies the rule this pattern
usually leaves implicit: **not all evidence is allowed to become a belief.** Its
interview answers arrive with an advertised prefix, and
`classify_answer_provenance` settles at the point of entry whether an answer is a
decision the caller *made* or a fact the caller *adopted* — `[from-code]`,
`[from-repo]`, `[from-research]`, `[from-data]`. An adopted fact is evidence in
the fullest sense of this page and is deliberately **withheld from the slot
requirements are extracted from**, while staying intact in the question slot,
because sharpening the next question is what collecting it was for. The rule is
scoped per role rather than per string, so the same text plays both parts
without the redaction destroying the second one.

Two details make it transferable. The classification is **decided once and
carried as a typed field** rather than re-derived per consumer, and the module
names the drift that motivated it — a second classifier in the same repository
reads `[from-research]` as human. And the withholding is enforced structurally
rather than in a prompt: one requirement path emits a specification with no LLM
in it at all, so a redaction living in a prompt template would never have reached
it. A single parametrized test asserts across all four requirement-consuming
render surfaces that the adopted fact's content is absent, with a companion test
pinning the intentional *non*-redaction of the question line as *"intended
behavior, not a conceded leak"* — which is the sentence that stops a later
contributor from finishing the job.

[Zeroshot](../../systems/zeroshot/) checks a model's citations against records the model did not write. A postmortem specialist proposing a lesson must name the agent node it concerns and cite a reference the host's run ledger holds for that node — a completion cursor or a numbered tool receipt recorded by the hook broker — and a repository lesson must also cite a file that opens in the workspace and carries one of the lesson's file, folder or identifier associations. One failing proposal rejects the specialist's whole output, and the rejection logs the stage without the text. The host then adds the one reference the model may not write, the clean checkout's commit. What the gate establishes is that the cited things exist and belong to the node; whether the lesson follows from them is left to the specialist, and the lesson is believed at once.

[TypeGraph](../../systems/typegraph/) makes belief a function of retained support rather than a stored verdict. Its provenance subpath keeps each derivation as a justification node with `premiseOf` edges from sources or facts, and a fact is believed only while some justification has every premise supported, computed as a least fixpoint (`packages/typegraph/src/provenance/support.ts:189-273`). Withdrawing evidence is then `retract(source)`, which closes exactly the reachable facts that lose every firing justification, keeps their edges so the inverse is exact, and returns `died` and `survivedVia` from the set the close pass wrote (`src/provenance/transition.ts:110-120`, `:231-297`). The gap is on the way in: support is checked at commit only by `assertHolds`, so a write that derives a fact from an already-retracted source commits live and is withheld only from `holding()` — a test worth requiring of any instance: derive from a withdrawn source, assert the fact is refused or unbelieved on every read.

[Persistent Mind Model](../../systems/persistent-mind-model/) orders the layers inside one turn. The model's reply is stored as the turn's single terminal outcome before any parser reads it; only a `complete` generation reaches the parsers, a failed structured line appends a `validation_failure` citing the reply, and a claim's `evidence_events` must both exist and have been selected by retrieval that turn (`pmm/core/validators.py:144-170`). The gap is the default: claim types without a validator are accepted as `ACCEPTED_UNKNOWN_TYPE`, and one of them, `name_change`, is what the prompt's `Identity:` line is built from (`pmm/runtime/context_utils.py:19-45`).

[LokalBot](../../systems/lokalbot/) ties each learned claim about its user to the meeting it came from and lets the person cut the tie. A claim learned overnight carries the meeting id, the store revision captured before the lines were read, and the person's quoted line (`LokalBot/Services/PersonalModel/PersonalLearning.swift:532-545`). Deleting or correcting a meeting advances the revision; on every read, a changed claim survives only if its source still holds the quote, and while a revocation is unfinished every learned claim is withheld (`LokalBot/Services/PersonalModel/PersonalModelController.swift:65-73`, `:91-111`). The person can move a claim out of the evidence layer: *Keep as statement* drops its evidence, and it then outlives the meeting. The work memory beside it inherits, for any reworded entry, every source the synthesis could read, because a model citation cannot prove what did not influence it (`LokalBot/Services/Dreaming/DreamModels.swift:432-450`).

[dsh-engram](../../systems/dsh-engram/) keeps the raw memories beneath its derived layer and makes the derived layer answer to them. An auxiliary LLM consolidates active memories into one-sentence beliefs whose `sources_json` lists the rows they came from, and the raw rows stay active beside them. When any source row is forgotten, archived, superseded, distilled or decayed, `detachArchivedEvidence` removes its id from every belief citing it in the same call: the belief turns stale while sources remain and refuted when none do, and only active beliefs are injected. A restore deliberately does not put the source back. The gap is the other derived layer: entity facts point at a `source_node_id`, and nothing invalidates a fact when that memory is forgotten.

[ResiMind](../../systems/resimind/) puts the whole gate in the verifier and runs it twice. A `KnowledgeCandidate` carries a statement, its assumptions, the derivation steps, a source task id and evidence references, and admission treats every one of them as an untrusted claim: the verifier registered for the candidate's domain decides, a candidate without a source task or with no verifier is `unknown`, and a verifier that mutates its input voids the verdict (`src/resimind/knowledge.py:222-252`). Loading a saved library validates and then discards each stored verdict and admits the candidate again under the current verifiers, so a forged `verified` in the file loads as `rejected` (`knowledge.py:409-422`, `tests/test_knowledge.py:212-223`). What it does not keep is the evidence itself: the references are strings, and the guarantee is exactly as strong as the verifier, which the module says in its first lines.

[Walrus Memory](../../systems/walrus-memory/) is the rebuild rule at the scale of a whole service. Its documentation calls the pgvector index a cache and Walrus the source of truth, and `restore` regenerates the index from the owner's Blob objects on Sui, so the derived store is honestly disposable. Forget is a decision about that projection only: `delete_by_namespace` deletes the rows and writes `memory_tombstones` keyed on the memory id, while restore matches on blob id, mints a new uuid and never reads the tombstone table. The API reference documents the re-index as intended, and the MCP plugin's session-start guidance tells the agent to run `memwal_restore` whenever recall for a used namespace comes back empty, which is exactly the state a forget leaves. The test this page asks for, apply a correction and then run the regeneration, fails here by design.

[Agents Remember](../../systems/agents-remember/) binds evidence to the bytes rather than to a document id. Every citation, realization and proof in a card's sidecar records a path, a locator, the file's Git blob and a content hash of the cited range, and a read recomputes each rule's state against the caller's code tree: current when the range still has the recorded content, stale when it differs, the symbol no longer binds once, or the file is gone. It shows the limit of the move as plainly as the move. The check proves the cited code has not changed since the card was written, not that the card describes it, and the gate that enforces it reads only entries at paths the task's own diff changed, so drift arriving from any other commit is labelled on every read and blocks nothing.

## Implementation checklist

- Store the event before starting asynchronous extraction.
- Give chunks deterministic IDs and precise source spans.
- Link every derived memory to one or more evidence IDs.
- Record extractor, prompt/schema version, and embedder identity.
- Return source references with recalled claims.
- Cascade delete through chunks, embeddings, summaries, and graph edges.
- Define when evidence expires and whether derived memory may outlive it.

## Tests to require

- Rebuild derived memory from retained evidence.
- Trace every injected claim back to a source.
- Delete a source and prove no derived artifact survives unintentionally.
- Retry a failed extraction without duplicating evidence.
- Verify access rules on both evidence and derived records.

## Related patterns

- [Trust-state machine](../trust-state-machine/)
- [Recoverable background work](../recoverable-background-work/)
- [Append-only memory audit](../append-only-memory-audit/)
- [Zero-LLM capture](../zero-llm-capture/)

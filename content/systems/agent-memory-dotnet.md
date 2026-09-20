---
title: "AgentMemory for .NET"
eyebrow: "Neo4j memory library"
description: "A .NET agent-memory library over Neo4j whose point-in-time recall carries two independent clocks in one query, whose facts merge on a canonical triple key computed in C# because the database's own lowercase function disagrees with it, and which clears an invalidation when the world asserts the same fact again."
root: ../..
page_kind: system
source_name: "joslat/agent-memory-dotnet"
source_url: https://github.com/joslat/agent-memory-dotnet
archive_name: "joslat--agent-memory-dotnet"
revision: 1fe5105ce9347ccc629d72a1f8560538a250fceb
revision_url: https://github.com/joslat/agent-memory-dotnet/commit/1fe5105ce9347ccc629d72a1f8560538a250fceb
analyzed_at: 2026-09-19
capabilities: "trust_state, bitemporal, scope_enforced, negative_eval"
stack_storage: "graph"
stack_retrieval: "vector, graph, lexical"
stack_source: "reviewed"
capability_evidence:
  trust_state: "a stored invalidation stamp surfaced as a two-value status, with the history read taking a flag that decides whether invalidated rows come back | src/AgentMemory.Abstractions/Domain/History/MemoryHistory.cs:18-53, src/AgentMemory.Neo4j/Queries/ConsolidationQueries.cs:56, src/AgentMemory.Neo4j/Queries/PreferenceQueries.cs:138, :167, src/AgentMemory.Abstractions/Domain/LongTerm/SupersededFact.cs:1-32, tests/AgentMemory.Tests.Integration/ShakedownEndToEndTests.cs:225-250 | `invalidated_at` is a property on entity, fact and preference nodes, written when a duplicate loses consolidation, when a preference is superseded, and by an explicit invalidate on each repository. It is exposed as a coarse lifecycle status of live or invalidated, described as soft-invalidated and retained for history and as-of recall, and the history query carries an include-invalidated flag that decides whether those rows are returned at all — so the state filters rather than annotates. A superseded fact is not merely hidden: the predecessor is read back as its own small record carrying what it used to assert and both closing clocks, so recall can render a current value with its previous one beside it | the states are two, not a vocabulary — nothing distinguishes a fact that lost a dedup from one a person retracted. And the write path clears the stamp: see the tombstone paragraph in section 9"
  bitemporal: "two independent clocks bound as separate parameters in one point-in-time query, and a predecessor record that keeps both | src/AgentMemory.Neo4j/Queries/TemporalQueries.cs:1-60, src/AgentMemory.Abstractions/Domain/LongTerm/SupersededFact.cs:10-31, src/AgentMemory.Abstractions/Options/ValidTimeMode.cs:1-41 | the as-of fact search takes a system clock that binds created-at and invalidated-at — what the store believed at that moment — and a valid-time clock that binds the fact's own valid-from and valid-until window — what held in the world — and applies both in the same Cypher, with the owner clause spliced in beside them. Entities take only the transaction clock because they carry no validity window, and the docstring says so rather than leaving the asymmetry to be discovered. A single-clock caller passes the two equal. The separation reaches the product surface too: the superseded-fact record carries the transaction close and the valid-time close as distinct fields and prefers the valid-time date when rendering, because a reader asking since when means the world rather than the database | ordinary live recall does not honour valid time by default: it filters on similarity, invalidation and owner. The repository documents that as a defect with its own configuration flag, and names the release in which a writer for those columns made it reachable"
  scope_enforced: "an owner key that is part of the merge-key index, spliced into every read, with a strict mode that throws when a tenant-facing call arrives without one | src/AgentMemory.Neo4j/Queries/TemporalQueries.cs:12-17, src/AgentMemory.Neo4j/Queries/FactQueries.cs:755-769, src/AgentMemory.Abstractions/Options/MemoryScope.cs:1-47, src/AgentMemory.Abstractions/Exceptions/MemoryOwnerScopeRequiredException.cs:1-24, tests/AgentMemory.Tests.Integration/ShakedownEndToEndTests.cs:123-131 | scope is a record carrying an owner id and an include-shared flag, and each query builder emits its own AND clause from it — owner matches, or owner matches or the row has no owner when shared rows are wanted. The fact lookup filters the canonical owner key rather than the display owner id, because only every column of the merge-key index produces a seek. The isolation policy adds a strict multi-tenant mode whose failure is a dedicated exception naming the operation, so an application can catch a missing-owner-context bug at the point it happens rather than after a global read has already occurred | the default is no filter, which the type documents as the backward-compatible global read, and the two null conventions are opposite by design: a null scope on a read means every owner, while a null owner id on a write means the shared bucket. Strict mode is opt-in"
  negative_eval: "isolation and invalidation absences asserted beside their positive controls, against a real database rather than a stub | tests/AgentMemory.Tests.Integration/ShakedownEndToEndTests.cs:123-131, :225-250, tests/AgentMemory.Tests.Integration/Compatibility/TckMirroredBehaviorTests.cs:138-142, :311, tests/AgentMemory.Tests.Integration/GraphRag/GraphRagAdapterIntegrationTests.cs:70, :109 | the end-to-end case seeds three entities — one owned by each of two users and one shared — then asserts all four outcomes in consecutive lines: each owner finds their own, finds the shared one, and finds nothing for the other's. The invalidation pair is built the same way: a history read including invalidated rows asserts the dedup loser is present, carries the invalidated status, has a valid-until stamp, names its successor and keeps its source message ids, and that the winner is present and live; the same read with invalidated excluded then asserts the loser is gone and the winner remains. The mirrored-behaviour suite repeats the isolation assertions with reasons attached, including one that include-shared set false excludes shared memory, and the GraphRAG adapter asserts another user's context never appears in assembled text | these run against a Neo4j fixture, so they exercise the emitted Cypher rather than a substitute; the unit suite's query tests assert the text of the Cypher instead and are the weaker half"
matrix:
  memory_unit: "An entity, a subject-predicate-object fact, or a preference, each a Neo4j node with an embedding, a confidence, an owner, created and updated stamps, an optional validity window and an optional invalidation stamp; facts also carry canonical keys and a mention count"
  storage: "Neo4j, with vector indexes per node family and a composite merge-key index on facts"
  retrieval: "Vector similarity per family with an owner clause spliced in, graph expansion and GraphRAG context assembly, plus a point-in-time path carrying a transaction clock and a valid-time clock"
  write: "Extraction from conversation into entities, facts and preferences, merged on canonical keys so a re-extracted triple collapses onto the existing node and increments its mention count"
  update_delete: "Soft invalidation rather than deletion — set by consolidation, by preference supersession, by an explicit invalidate, and by decay in its destructive mode; invalidated rows remain readable through history and as-of recall"
  scoping: "An owner id on every node plus a shared bucket for rows with none, applied as a query clause; a strict multi-tenant mode turns a missing owner scope into a named exception"
  integration: "An MCP server with tools, resources and prompts, plus Semantic Kernel and Agent Framework adapters, a CLI, connectors and a NuGet meta-package"
  background: "Consolidation that collapses duplicates onto a winner, a decay service with a non-destructive default, and enrichment and analytics passes over the graph"
  trust: "A confidence number per node that a re-assertion increases rather than replaces, and a two-value lifecycle status of live or invalidated; no vocabulary distinguishes why something was invalidated"
  strengths: "Two clocks bound as separate parameters in one query; canonical merge keys computed in C# because the database's own lowercase function disagrees with the canonicaliser on a specific code point; and a salience counter that deliberately counts assertions rather than retrievals"
  risks: "Re-asserting an invalidated fact clears the invalidation by design, so a retraction does not survive the same claim arriving again; the audit trail records reads rather than writes; and live recall ignores valid time unless a flag is set, which the repository documents as a defect"
---

## 1. Executive Summary

This is a .NET library — sixteen projects, a NuGet meta-package, an MCP server,
Semantic Kernel and Agent Framework adapters — storing agent memory as a Neo4j
graph of entities, subject-predicate-object facts and preferences.

Four marks, and the through-line is that the interesting decisions are all
written down at the point they were made.

**Two clocks, in one query.** The point-in-time fact search binds a system
clock against `created_at`/`invalidated_at` and a valid-time clock against
`valid_from`/`valid_until`, applies both, and splices the owner clause in
beside them. Entities take only the transaction clock because they have no
validity window, and the docstring says so. The separation reaches the rendered
answer: a superseded fact comes back as its own small record carrying both
closing clocks, and rendering prefers the valid-time date, because *"a reader
asking 'since when?' means the world, not the database."*

**Facts merge on a canonical key computed outside the database.** Subject,
predicate, object and owner are each canonicalised in C# — lowercased *and*
whitespace-collapsed — and the write path merges on those four columns. The
lookup used to ask a different question, matching `toLower(f.subject)`, and the
comment explains why that was a correctness bug rather than a performance one:
the two disagree outright on U+0130, so the lookup *"could find a different
fact than a MERGE would collapse onto."*

**Salience counts assertions, not retrievals.** `mention_count` increments once
per ingestion that re-states a triple, and the comment names what it refuses to
be: ranking on the system's own retrievals *"is a rich-get-richer loop that
reinforces whatever already ranks highly and calls it learning."*

**The isolation tests assert all four outcomes in a row.** Two owners and a
shared row; each owner finds their own and the shared one, and nothing of the
other's.

What is not here is a rejection that survives. Re-asserting an invalidated fact
sets `invalidated_at` back to null, deliberately — *"a present-time positive
assertion restores live recall."*

## 2. Mental Model

Memory is a graph of three node families, and almost every mechanism is a
property on those nodes rather than a separate table.

A fact's identity is its canonical triple plus its owner. Everything else
follows from that: re-extraction collapses rather than duplicating, confidence
is earned by corroboration rather than overwritten by whichever extraction ran
last, and the mention count is a record of how often the world said the thing.

Time is two properties and two more: when the row was created and when the
system stopped believing it, alongside when the fact started and stopped
holding. A read either asks the live question — similarity, invalidation,
owner — or the as-of question, which is where both clocks come in.

Deletion is not part of the model. Consolidation, supersession and the
destructive decay mode all stamp `invalidated_at`; history reads can ask for
those rows back.

## 3. Architecture

```mermaid
%% caption: extraction canonicalises each triple in C# and merges facts on subject, predicate, object and owner keys, so a re-extracted triple collapses onto the existing node, increments a mention count that counts assertions rather than retrievals, earns confidence by corroboration, and clears any invalidation stamp; live recall filters on similarity, invalidation and owner while the point-in-time path binds a transaction clock and a valid-time clock as separate parameters in the same query; consolidation, preference supersession and destructive decay stamp an invalidation rather than deleting, and a history read decides with a flag whether those rows come back
flowchart TD
    CONV["conversation"] --> EXT["extraction<br/>LLM or Azure Language"]
    EXT --> CANON["MemoryTripleCanonicalizer<br/>lowercase + collapse whitespace<br/>in C#, never in Cypher"]
    CANON --> MERGE{"MERGE on<br/>subject_key · predicate_key<br/>object_key · owner_key"}
    MERGE -->|ON CREATE| NEW["mention_count = 1"]
    MERGE -->|ON MATCH| UPD["confidence earns by corroboration<br/>mention_count + 1<br/>invalidated_at = null"]

    G[("Neo4j<br/>Entity · Fact · Preference<br/>owner_id · valid_from/valid_until<br/>created_at · invalidated_at")]
    NEW --> G
    UPD --> G

    subgraph Reads
        LIVE["live recall<br/>similarity + invalidated_at IS NULL<br/>+ owner clause"]
        ASOF["point-in-time recall<br/>$systemAsOf binds created/invalidated<br/>$validAsOf binds valid_from/valid_until"]
        HIST["history read<br/>IncludeInvalidated decides"]
    end
    G --> LIVE
    G --> ASOF
    G --> HIST
    LIVE --> PREV["SupersededFact<br/>both clocks, renders the valid-time date"]

    subgraph Background
        CONS["consolidation<br/>duplicate loser invalidated"]
        DEC["decay<br/>non-destructive by default"]
        SUP["preference supersession<br/>loser invalidated"]
    end
    CONS --> G
    DEC --> G
    SUP --> G

    ISO{"IMemoryIsolationPolicy<br/>StrictMultiTenant"} -->|no owner scope| THROW["MemoryOwnerScopeRequiredException<br/>named operation"]
    ISO --> LIVE
    ISO --> ASOF
```

## 4. Essential Implementation Paths

- **Scope and isolation:** `src/AgentMemory.Abstractions/Options/MemoryScope.cs`,
  `Options/MemoryIsolationMode.cs`,
  `Exceptions/MemoryOwnerScopeRequiredException.cs`.
- **Time:** `src/AgentMemory.Neo4j/Queries/TemporalQueries.cs`,
  `Abstractions/Options/ValidTimeMode.cs`,
  `Abstractions/Options/TemporalValidityMode.cs`.
- **Fact identity and upsert:** `src/AgentMemory.Neo4j/Queries/FactQueries.cs`.
- **Lifecycle:** `src/AgentMemory.Abstractions/Domain/History/MemoryHistory.cs`,
  `Domain/LongTerm/SupersededFact.cs`,
  `Neo4j/Queries/ConsolidationQueries.cs`, `Queries/DecayQueries.cs`.
- **Surfaces:** `src/AgentMemory.McpServer/`, `src/AgentMemory.SemanticKernel/`,
  `src/AgentMemory.AgentFramework/`.

## 5. Memory Data Model

Three node families share a shape: an embedding, a confidence, an owner id, a
created stamp, an updated stamp and a nullable invalidation stamp. Facts add
the canonical keys, a validity window, source message ids and the mention
count.

The canonical keys are the part worth copying. They exist because the
canonicaliser and Cypher's `toLower` are different functions, and the
difference is not theoretical — the comment names U+0130 and notes that the C#
form also collapses whitespace runs. Keeping the computation on one side of the
wire means the read and the write cannot drift apart, and the unit test asserts
exactly that: the lookup must filter the same four columns the merge uses, and
`toLower` must not appear in either shape.

The composite index wants every column, not a prefix, which is why the owner
clause in that one query filters `owner_key` rather than `owner_id` — and why
an unscoped lookup is documented as still planning a scan, *"deliberately so:
with no owner there is no fourth column to filter."*

## 6. Retrieval Mechanics

Live recall is vector similarity per family with an owner clause and an
invalidation clause. Point-in-time recall adds the second clock. GraphRAG
context assembly walks the graph and is covered by its own isolation test.

The honest gap is documented in the enum that exists to close it: live recall
does *not* filter on valid time by default, so a fact valid from six months
hence is returned today and a fact whose `valid_until` has passed is returned
*"forever"*. The remarks explain why that was inert until recently — no
extractor wrote validity bounds, so the clauses would have matched nothing —
and why shipping the writer made the defect reachable from configuration. Both
new modes default to off, and the reason given is that prompt bytes are a
measured variable fingerprinted into evaluation runs, so a default that shifted
them *"would invalidate sealed bases silently."*

That reasoning also produces the sharpest risk statement in the tree: because
live recall filters on these columns, a fabricated `valid_until` does not add
noise, it *"silently removes a memory from every future answer"* — which is why
the extraction instruction tells the model to omit validity rather than guess
it.

## 7. Write Mechanics

Extraction canonicalises, then merges. On create the mention count starts at
one; on match, confidence is increased by a configurable corroboration alpha
rather than replaced, validity bounds are coalesced so re-extraction never
clears a supersession window, the mention count increments, and
`invalidated_at` is reset.

The batch path merges on the same four keys as the single path, and the
docstring records why: it used to merge on `id`, *"which let a re-extracted
triple with a fresh id create a second node."*

## 8. Agent Integration

An MCP server exposing tools, resources and prompts; adapters for Semantic
Kernel and the Microsoft Agent Framework; a CLI; connectors; sample projects
and a package-consumer test matrix. MIT, version 1.5.0.

## 9. Reliability, Safety, and Trust

**Trust state — awarded**, on a narrow but real mechanism: a stored
invalidation stamp, surfaced as a two-value status, with a history read whose
flag decides whether invalidated rows are returned. The limit is vocabulary —
two states, and nothing distinguishing a dedup loser from a retraction.

**Bi-temporal — awarded.** Two clocks as separate parameters in one query, and
a predecessor type that keeps both and knows which one to render.

**Scope enforced — awarded**, with the opt-in caveat in the evidence. The
strict mode is the part worth naming: a missing owner scope becomes a dedicated
exception carrying the operation name, so the failure is visible at the call
rather than as a quietly broader result set.

**Negative eval — awarded**, on integration cases against a real Neo4j with
their positive controls in the same block.

**Tombstone — withheld, and the code makes the call for me.** Fact identity
*is* value-keyed — the canonical triple plus owner — and the lookup carries no
liveness filter, so a re-extracted triple does find the invalidated node rather
than creating a new one. Everything a tombstone needs is in place except the
refusal: `ON MATCH SET` includes `f.invalidated_at = null`, and the batch
path's docstring states the intent plainly — *"invalidated_at is reset on
re-assert (a present-time positive assertion restores live recall)."* So a
retraction lasts exactly until the next extraction that says the same thing.
That is a defensible product decision for a store whose invalidations mostly
come from deduplication, and it is the opposite of what this mark asks for.

**Audit log — withheld**, and the rubric's exclusion is the one that applies:
logs of retrieval do not count. The trail here is `:MemoryReadAudit`, one row
per surfacing, and the codebase is explicit that it is deliberately *not* the
salience signal. No append-only record of mutations exists; history is derived
from the nodes' own stamps and supersession edges.

**Human review — withheld.** There is a `memory-review` MCP prompt, and its
text is a numbered procedure addressed to the agent: call search, call
list-sessions, compile a summary, flag contradictions. No person adjudicates
anything, and nothing gates a write on approval.

## 10. Tests, Evals, and Benchmarks

**No paper** and no `CITATION.cff`.

Five test projects. The unit suite is large and much of it asserts the *text*
of emitted Cypher — that a clause is present, that `toLower` is absent, that
all four index columns are filtered. That is a reasonable way to pin a query
builder and a weak way to pin behaviour, which is why the marks rest on the
integration suite instead.

The evaluation apparatus is the unusual part. A dedicated LongMemEval harness
sits under `tools/`, with its own unit project of over a hundred files covering
ablations, answer-presence gates, prompt byte-identity, seed wiring, voting and
quote forcing, and abstention accuracy. That last one carries the most careful
distinction in the repository: the sufficiency metric's absent-count is a
ground-truth *input*, identical across arms by construction, while abstention
accuracy is an *outcome*, and reporting only the first *"invites reading a class
balance as a result."* It also records that across fifty-two runs before typed
sampling shipped, no abstention question had ever been drawn.

No benchmark result is committed, and the architecture document marks several
tiers **BUILT and WIRED but not MEASURED**, naming working memory as having had
no LongMemEval run at all. A repository that labels its own unmeasured surfaces
is doing something most do not.

## 11. For Your Own Build

- **Make the read ask the question the write answers.** Canonicalise on one
  side of the wire and filter the canonical columns; a lookup that lowercases
  in the database and a merge that canonicalises in the application are two
  different notions of the same key.
- **Count assertions, not retrievals.** A salience signal fed by your own
  recall reinforces whatever already ranks, which is a loop rather than
  learning.
- **Let corroboration increase confidence rather than replace it**, so the
  latest extraction's number is not automatically the stored one.
- **Turn a missing scope into a named exception.** Catching
  `OwnerScopeRequired` at the call is worth more than noticing a broad read
  later.
- **Say which clock you render.** A user asking "since when?" wants valid time;
  the transaction clock is the fallback, not the answer.
- **Decide explicitly whether a retraction survives re-assertion**, and put the
  decision in the query rather than leaving it to whichever branch the merge
  happens to take.

## 12. Open Questions

- Clearing `invalidated_at` on re-assert is right for a dedup loser and
  questionable for a user retraction, and both share the field. Would a reason
  on the invalidation — retracted versus deduplicated — let the merge treat
  them differently?
- Live recall ignores valid time unless the flag is set, and the writer for
  those columns now exists. What is the migration story for a store that
  enabled extraction before enabling the read gate?
- The architecture document marks several tiers as unmeasured. Which of them
  does the next LongMemEval run cover, and does the abstention sampling change
  the baseline enough that earlier numbers are not comparable?

## Appendix: File Index

- Scope, isolation and exceptions:
  `src/AgentMemory.Abstractions/Options/MemoryScope.cs`,
  `Options/MemoryIsolationMode.cs`, `Options/MemoryIsolationOptions.cs`,
  `Exceptions/MemoryOwnerScopeRequiredException.cs`
- Time: `src/AgentMemory.Neo4j/Queries/TemporalQueries.cs`,
  `src/AgentMemory.Abstractions/Options/ValidTimeMode.cs`,
  `Options/TemporalValidityMode.cs`, `Options/TemporalQueryClocks.cs`
- Fact identity and upsert: `src/AgentMemory.Neo4j/Queries/FactQueries.cs`
- Lifecycle and history:
  `src/AgentMemory.Abstractions/Domain/History/MemoryHistory.cs`,
  `Domain/LongTerm/SupersededFact.cs`,
  `src/AgentMemory.Neo4j/Queries/ConsolidationQueries.cs`,
  `Queries/DecayQueries.cs`, `Queries/PreferenceQueries.cs`,
  `Queries/HistoryQueries.cs`
- Surfaces: `src/AgentMemory.McpServer/`, `src/AgentMemory.SemanticKernel/`,
  `src/AgentMemory.AgentFramework/`
- Tests: `tests/AgentMemory.Tests.Integration/ShakedownEndToEndTests.cs`,
  `Integration/Compatibility/TckMirroredBehaviorTests.cs`,
  `Integration/GraphRag/GraphRagAdapterIntegrationTests.cs`,
  `tests/AgentMemory.Tests.Unit/Queries/FindByTripleMergeKeyTests.cs`,
  `tests/AgentMemory.Tests.Unit.LongMemEval/`

## History

**2026-09-19** — [`1fe5105ce9347ccc629d72a1f8560538a250fceb`](https://github.com/joslat/agent-memory-dotnet/commit/1fe5105ce9347ccc629d72a1f8560538a250fceb) — first reading, at the head of `main`, version 1.5.0. Screened with `scripts/screen_repo.py` before anything was read: three auto-run surfaces (a Copilot instructions file and two VS Code settings files), four unpinned MSBuild reference surfaces in the package-consumer projects, no build-time execution path, and an `AGENTS.md` addressed to a reading agent — read as data throughout. Nothing was installed, built or run. MIT. Four marks. The reading covered the node model and its canonical keys, the upsert's create and match branches, the point-in-time queries and both clocks, the scope record and the isolation policy, the history surface and its invalidation flag, the consolidation, decay and preference supersession writers, and the integration tests the marks rest on; the connectors, analytics, enrichment and NAMS trees were read as context rather than as subject. Three marks are withheld with reasons in section 9, and the one to read is `tombstone`: fact identity is genuinely value-keyed and the lookup carries no liveness filter, so everything the mark asks for is present except the refusal — the merge's match branch sets the invalidation stamp back to null, with the intent stated in the batch path's own docstring. Two reports in this corpus already carry the name `agentmemory`; both are different projects by different authors and neither is this one.

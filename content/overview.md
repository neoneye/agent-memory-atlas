---
title: Agent Memory Systems Comparative Report
eyebrow: Cross-system synthesis
description: A code-grounded comparison of one hundred and eleven agent memory architectures, their retrieval mechanics, trust models, and operational tradeoffs.
root: ..
page_kind: comparison
---

## Reading This Report

**What is in the atlas.** A system qualifies if something it stores **survives
the session with an identity that can later be corrected**. That single test
does the work: it admits a 300-line Markdown file with stable entry IDs and
excludes a sophisticated chat-buffer compactor, however good the compaction is.
Systems reviewed and excluded on this basis, or on licence grounds, are named in
the limitations at the end rather than quietly dropped — the exclusions are part
of the evidence.

**How systems were selected.** Opportunistically: repositories encountered,
suggested, or found while looking for the ones already here. This is not a
sample of a population and no sampling frame is claimed. It skews toward
actively developed open-source projects, toward things adjacent to coding
agents, and toward whatever was visible in mid-2026. Absence from this atlas is
not evidence of anything.

**What an absence claim means.** "There is no trust state", "no tombstone was
found", "no benchmark exists" all mean the same thing: *not found in the
inspected code at the pinned commit*. Every claim here is static review — code
read, not run — and the reports are opinionated by design. Where the code is
partly closed, or a capability is documented but managed-platform-only, the
reports say so at that point rather than hedging every sentence.

**What this method structurally cannot reach, and what that costs.** Every claim
here rests on reading code at a commit, so a system with no inspectable code is
not merely absent from this atlas — it is *unreachable by it*. That excludes the
memory features most users have actually met: OpenAI's memory, Claude's memory and
project knowledge, Zep's hosted service, Google's Vertex Memory Bank as a service,
and every enterprise offering whose multi-tenancy, retention and audit behaviour
lives on someone else's servers.

This is a real limitation and not a small one, because those are the systems
operating under compliance, scale and tenancy constraints that the local-first
projects here never face. Where a hosted product has an open component, the open
component is what gets reviewed and the report says so: Zep is here as
[Graphiti](../systems/graphiti/), and Vertex Memory Bank appears inside
[adk-python](../systems/adk-python/) as a client whose contract has no delete.
That is genuinely less than reviewing the service, and the difference should be
read as a gap in the atlas rather than a finding about the products.

Two consequences worth stating plainly. The atlas's headline counts — three
tombstones, six negative-eval suites — are counts *over inspectable code*, and a
closed system could hold any of these mechanisms without this method ever
knowing. And a mechanism's absence here is weaker evidence about the field than
its presence: finding a tombstone proves someone built one, while not finding one
proves only that nobody built one *in public*.

**The divergences that actually separate these systems.** If you read nothing
else:

1. **Whether correction is possible at all.** Almost everything can overwrite
   or supersede. Three systems in this entire atlas can record that a *value*
   was rejected so extraction cannot bring it back — see the
   [capability index](../capabilities/) for the live count. This is the single widest gap in
   the field, and it is invisible on every benchmark.
2. **Whether evidence outlives its derivations.** Systems that keep the raw
   event and treat summaries, profiles, and graphs as rebuildable projections
   can repair a bad extraction. Systems that discard the source cannot.
3. **Whether scope is identity or decoration.** Three levels, and the atlas's
   `scope_enforced` mark only certifies the middle one. A scope *tag* stored
   beside the memory is a hope. A scope *key applied as a filter on the read
   path* is what 61 of 111 systems here have, and is what the mark means. A scope
   *boundary* — authenticated identity, grants, and a filter that a caller cannot
   widen by passing a different argument — is rarer than the count suggests, and
   in a single-user desktop deployment is not even the right goal. Read the
   column as "the key reaches the query", not as "this is multi-tenant safe".
4. **Whether retrieval can decline.** Most systems always return their top *k*.
   Very few can decide that this turn needs no memory, and irrelevant memory in
   a prompt is not inert — it bends the answer.
5. **Who decides.** Fully automatic memory, memory a person can review before it
   takes effect, and memory a person authors are three different products with
   three different failure modes.

Everything below is evidence for those five, in more detail than most readers
need. The [capability index](../capabilities/) — every system against all seven
marks, filterable — is the fastest way in.

## 1. High-Level Taxonomy

One hundred and eleven systems do not fall into one hundred and eleven categories. They cluster around
eight architectural commitments, and most systems belong to more than one —
a coding-agent memory can also be verification-first, and a host runtime's
plugin can also be a hosted service. The families below are lenses, not bins.

Where a system is the clearest instance of an idea, it is named in bold and
characterized in place rather than given a category of its own.

### Embeddable memory libraries

`mem0`, `langmem`, `llamaindex`, `cognee`, `a-mem`, `memori`, `goodai-ltm`,
`pydantic-ai-harness`, `camel`, `crewai`, `agent-memory-supabase`, `cosmonapse`,
`mem0sharp`

Called from an application that owns the agent loop. Easy to adopt; weak
authority over when memory is written or how recall is used.

**GoodAI LTM is the family's cautionary comparison, and it points at the two
framework contracts above.** Dormant since February 2024 and carrying no scope
key at all, it nonetheless declares on its base interface what neither ADK nor
AutoGen can express: `add_text` returns a `text_key`, and `replace_text`,
`delete_text` and `get_text` all take that key back. Insert returns an address;
update and delete use it. A small research lab shipped the addressed lifecycle in
2024 and the 2026 framework abstractions from Google and Microsoft did not — one
declining to declare a removal method, the other unable to, since `MemoryContent`
has no identifier to remove by. Its deletion is still removal rather than
rejection, which is the distinction the correction section draws: being able to
delete a memory is not being able to reject a value. **Cognee** is the
outlier in surface area — a knowledge pipeline platform with ontologies,
dataset permissions, and provenance rollback behind a small remember/recall
API. **LlamaIndex** composes memory from pluggable blocks that each truncate
themselves to budget. **A-MEM** is a compact Zettelkasten research sketch whose
linked-note evolution idea outruns its implementation. **Memori** ships a Rust
core with Python and TypeScript bindings over seven backends, and is the atlas's
sharpest illustration of the family's tradeoff taken one step further: the schema,
the drivers and the migrations are all open, and the extraction that decides what
a fact *is* runs in the vendor's hosted service.

**The Pydantic AI Harness is the family's answer to the tradeoff below, and it
answers it by narrowing the claim.** Its memory is a Markdown notebook behind
four tools, with no unit below the file, no status, no confidence and no
provenance — and the engineering all sits where a library actually can act: what
reaches the prompt, and who is allowed to ask. The namespace is resolved from
run context and documented as never exposed as a tool argument, so a model has
no argument in which to name another tenant; then `list_subfiles` re-checks
every returned path against the requested prefix and raises if a store hands
back anything outside it. **That check is unique in this atlas.** Every other
system with a pluggable store trusts the store to have filtered; this one treats
its own backend as untrusted and verifies the boundary on the way back, which is
the difference between enforcing a scope and asserting that it was enforced.
Writes carry an idempotency id derived from the run and the tool call, so a
retried write is a replay rather than a second append — the failure mode an
agent framework hits constantly and which almost nothing here models.

**CrewAI models scope as a filesystem, and is the only system here that does.**
A `MemoryRecord` carries a hierarchical `scope` path — `/company/team/user` —
and `MemoryScope` is a *view* of the store rooted at a subtree, with
`subscope()` to descend and a `read_only` flag, while `MemorySlice` spans
several. Multi-tenancy becomes an object a caller holds rather than a parameter
they must remember to pass, and the prefix gives hierarchy for free. A second
axis sits on top: every record has a `source` and a `private` flag, and recall
filters `if not r.private or r.source == self.state.source`. Both boundaries are
applied on the read path and one of them is proved by a committed test.

**Then it hands a language model a delete.** `analyze_for_consolidation` returns
a `ConsolidationPlan` whose actions on existing records are keep, update or
**delete**, executed inline on every write, so a model comparing new content
against what is stored decides what to destroy. No tombstone, no append-only
record, no trust state that would let a doubtful record be withheld instead, and
no review surface — the CLI's memory TUI is a browser whose every `update()` is a
panel repaint. The most carefully scoped store in the atlas is also the one that
most readily authorises an LLM to remove what it already believed, and nothing
measures how often that judgement is right. Two smaller things worth keeping:
`MemoryMatch.evidence_gaps` reports *"information the system looked for but
could not find"*, which almost nothing else here does, and `match_reasons` names
why a record ranked — with a test asserting `"recency"` is **absent** when the
decay term does not clear its threshold.

**CAMEL is the family's floor and its clearest warning about stored scope.** Its
memory unit is the message rather than the fact — `MemoryRecord` is a chat
message, a backend role, a UUID and a timestamp, with nothing extracted or
derived — so it sits at the boundary between memory and window management, on
the memory side only because `VectorDBMemory` embeds messages into a durable
store and recalls them by similarity across sessions. Every record carries an
`agent_id` that is set on write, serialised both ways, and **applied on no read
path**; isolation comes from handing each agent its own storage object, which is
a convention rather than a mechanism. Two smaller things are worth recording
because they are the shape of drift rather than of design: the recall query is
`_current_topic`, set to whatever the last user message said and initialised to
the empty string, so the first retrieval in a fresh process is arbitrary; and
`ScoreBasedContextCreator` neither scores nor filters, its `token_limit`
documented as *"Retained for API compatibility. No longer used to filter
records."* A name and a parameter outlived the mechanism they described.

Tradeoff: a library can store and retrieve, but it cannot guarantee the model
calls the right tool, verifies a fact, or uses recall safely.

### Hosted and service memory

`honcho`, `supermemory`, `hindsight`, `redis-agent-memory-server`, `openviking`,
`memanto`, `memory-engine`, `memu`, `elastic-atlas`, `mirix`, `memobase`,
`powermem`, `memmachine`, `gobii`, `cortex`

Multi-user, API-first, with background derivation. **Honcho** models workspaces,
peers, sessions, and derived representations rather than flat facts.
**Hindsight** runs four independent recall arms with task-specific fusion.
**Redis Agent Memory Server** splits TTL-scoped working memory from promoted
long-term memory and carries the atlas's most developed retention policy.
**OpenViking** unifies memory, resources, and skills in one filesystem
hierarchy with three retrievable granularities per record. **Memanto** is the
only system here whose contradiction pipeline ends in a decision: a nightly pass
writes a dated conflict report, and a human resolves each entry as `keep_old`,
`keep_new`, `keep_both`, `remove_both`, or `manual` with content they write
themselves. **Memory Engine** makes the agent a first-class access-control
principal and clamps a delegated agent grant to `least(agent, owner)` at every
path, so over-granting your own agent is harmless by construction. **memU** ranks
segments and returns the files they belong to, scoring each file by the max of
its segments — the search unit and the return unit are deliberately different
sizes. **MIRIX** gives each of six memory types its own table, manager, writer
agent and prompt, and carries the most thoroughly *enforced* scope model here —
four levels, applied in the SQL and in the Redis index queries alike.
**Memobase** goes further on the same axis by making scope structural: every
primary key is `(id, project_id)` and every foreign key is composite, so a
cross-tenant query is a schema error rather than a review failure.

Three members mark the family's boundaries on the same axis: what happens to the
evidence. Memobase caps a user profile at five sentences per subtopic and fifteen
subtopics per topic, and **deletes the source transcript after extraction by
default**; MIRIX ingests screen captures continuously and runs a periodic pass
that can rewrite the whole store. One is the smallest useful description of a
user, the other is the largest, and neither can say that a value was rejected.
**PowerMem** answers the same question a third way, with an Ebbinghaus retention
curve that decides reachability — the atlas's most complete forgetting model, and
a reminder that a well-tuned curve is still not a trust state.

**MemMachine takes the opposite side of Memobase's bet and is the better system
for it.** Every raw episode is kept, and each derived `SemanticFeature` carries
`metadata.citations` — the episode IDs it came from. Because the episodes are
still there, those citations *resolve*: "why do you believe that?" returns text a
support engineer can read. That is the rarest property in this family and it
costs one array column. The same retention is what makes its correction story
thin: a deleted feature leaves no rejected-value record, and only a one-way
`is_ingested` watermark stops the still-present evidence from producing the
feature again — protection from bookkeeping rather than from knowing the claim
was wrong. It also states its own write lag in configuration
(`feature_update_interval_sec = 2.0`), which almost nothing else here does.

Tradeoff: the API surface is usually easier to study than the decision
machinery. In `supermemory` the hosted core is not visible at all; in `mem0`
several documented capabilities are managed-platform-only.

### Agent-runtime memory

`letta`, `rainbox`, `memos`, `mastra-observational-memory`, `claude-mem`, `npcpy`, `juggler`, `gitlord`, `tokenmizer`, `zerostack`,
`agentmemory`, `tencentdb-agent-memory`, `nanobot`, `cowagent`, `genericagent`,
`mercury-agent`, `atomic-agent`, `mateclaw`, `waku-agent`, `loongflow`, `buzz`,
`openhuman`, `aukora-kernel`, `helm`, `neko`, `sillytavern`, `risuai`, `soul-of-waifu`, `z-waif`, `virtualwife`

Memory is part of the runtime: compiled into context, mutated through
first-class actions, tied to agent state. **Letta** separates core, archival,
and recall memory inside the loop. **RainBox** routes every belief through one
governed write path with a five-actor trust model. **MemOS** mounts textual,
preference, skill, KV-cache, and parametric memory as one cube. **Mastra**
compresses older messages into dated observations and activates them without
blocking. **TencentDB** layers L0 conversation evidence through L3 persona with
symbolic tool-output offload. **Mercury** grades every record on confidence,
importance, and durability separately, and keeps a subconscious tier below
active recall. **Atomic Agent** cites numbered invariants from its schema into a
design document, records votes as append-only events with derived scores, and
ships new memory features off by default until an evaluation campaign reports. **GenericAgent** governs four file layers with written axioms
instead of code. **Waku** organizes everything around refusing expensive work:
a small model decides whether to retrieve at all, consolidation batches, and
skill bodies load only on match. **LoongFlow** carries two unrelated memories in
one package — a conventional short/medium/long tier stack, and a population of
scored solutions recalled by Boltzmann sampling whose temperature is driven by
the population's measured diversity.

**npcpy is the corpus's most literal answer to "who decides".** Extracted
memories are written with `status = "pending_approval"` and a terminal loop walks
them one at a time — approve, reject, **edit**, skip, defer, approve-all — with
each decision stamped `human-approved` or `human-rejected`. The gate is not
advisory: `build_context` calls `get_memories(status="human-approved")`, so a
candidate nobody has said yes to reaches no prompt, and the row keeps the initial
text beside the human-edited final one, which almost nothing else here does.
Its failure is the exact inverse of its strength — `human-rejected` is a status
on a row that the extraction path never consults, so the same sentence extracted
again arrives as a fresh candidate and the user is asked the same question. A
system that goes to the trouble of asking a human throws the answer away when the
answer is no.

**Juggler makes the opposite storage choice from every other notebook here.**
Its memory is `<project>/.juggler/MEMORY.md` and `.juggler/` is **git-ignored on
purpose** — private to the checkout, never committed, per-machine — where
[Basic Memory](../systems/basic-memory/), [claude-mem](../systems/claude-mem/)
and [TigrimOSR](../systems/tigrimosr/) all keep the file somewhere a team could
share it and several treat git history as the audit trail. It forgoes that
provenance so an assistant's notes about a codebase never reach a colleague's
review. Its documentation also states the distinction this atlas's fifth
divergence is about: the instructions file is what *you* write for the
assistant, memory is the notes the *assistant* keeps for itself. The sharp edge
is `forget`, which removes every entry matching a case-insensitive substring and
returns no list of what it took.

**GitLord is the strongest instance of the mechanism the rubric deliberately
excludes.** Every turn is a git commit, every session a branch, and
`DedupIndex.rebuild_from_log` regenerates the retrieval index by walking the
log — the log is the authority and the index is a projection, which is
[Core Memory](../systems/core-memory/)'s arrangement obtained for free by making
the authority a repository. It carries no capability marks and the reason is a
category difference rather than a deficiency: it durably records *what happened*
and has no representation of *what is believed*, so a user's correction and the
mistake it corrects are both in the log, in order, with nothing preferring
either. Git history is not this atlas's append-only audit column — the rubric
says so — and this is the clearest case of why that is a different mechanism
rather than a weaker one.

**TokenMizer has a status for not knowing, and it is the best answer in the
corpus to the problem supersession usually creates.** Every other system here
resolves a contradiction by picking: the newer decision supersedes, the old row
drops out of retrieval, and nothing tells the model there was a disagreement.
TokenMizer's contradiction check asks whether the evidence supports that call,
and when two decisions share a topic bucket without sharing enough context to
call one a replacement — its own example is *"Use PostgreSQL for primary user
data"* against *"Use SQLite for the local offline cache"* — it marks **both**
`CONTESTED` rather than *"silently guessing and marking one SUPERSEDED —
destroying it from resume context on possibly-wrong evidence"*. The pair is
joined by a symmetric `CONFLICTS_WITH` edge, and `CONTESTED` is the one status
that **stays visible** in `query()` and `to_context_block()` where `SUPERSEDED`,
`ARCHIVED` and `INVALIDATED` are hidden — because the point is to put the
unresolved pair in front of whoever can settle it.

Its correction record is the richest here too: a `DecisionTransition` stores
*"what triggered the change, why the old decision was wrong, what evidence caused
the switch, and how confident we are now"*, in a table deliberately outside the
node and edge JSON *"so it survives graph pruning"*. Most systems record that a
value was replaced; this records the argument.

And it measures its own extraction, which almost nothing here does.
`tests/memory_accuracy/test_retention.py` runs a synthetic thirty-turn coding
session past the extractor against a hand-written ground truth and asserts recall
thresholds — 0.4 for tasks, 0.33 for decisions and files. Read those numbers as a
disclosure rather than a weakness: this is a project that knows roughly two-thirds
of a session's decisions never reach its graph, has written that down where CI
enforces it, and has not dressed it up.

**agent-afk answers the criticism this atlas ends the Helm report on.** Helm
computes a provisional-confidence cap, earns increases through corroboration,
and then formats the surviving facts as `- (kind) key: value` under *"use these,
never contradict them"* — the number stripped off before the model sees it.
agent-afk does the cheap version and does not drop it: a `convention` fact
written without a provenance citation is recalled with an **`[unverified]`
marker in the text the model reads**, and the write warns. The gate is
category-aware — preferences never require file evidence, a `learning` is not
treated as factual codebase knowledge — and supersession has four tested
outcomes, including carrying a prior citation forward *with a staleness
warning* when no fresh evidence is supplied. A system that computes trust and
ships it as a string has closed the boundary this atlas keeps finding open. It
is all behind `AFK_MEMORY_EVIDENCE_GATE=1`, so the default build carries the
migrated column and none of the behaviour.

**Helm is the family's floor, and it shows how little a working epistemic model
costs.** One SQLite file opened through Node's built-in `node:sqlite`, no
service, no key required to store anything, 401 lines — and inside them a
provisional-confidence cap on any fact the agent thinks it noticed, an evidence
counter that is the only thing able to raise belief, decay that retrieval slows
rather than resets, and supersession that keeps the row it replaced. It is the
cheapest instance in this atlas of [evidence before
belief](../patterns/evidence-before-belief/) and worth reading beside systems a
hundred times its size. Its failure is at the boundary rather than in the model:
`recallMemories` formats the surviving facts as `- (kind) key: value` under the
instruction *"use these, never contradict them"*, so the confidence the store
worked to earn never reaches the model that consumes it. A system can compute
trust carefully and still ship it as an assertion.

**Buzz is the family's outlier and the only system here that treats memory as a
wire protocol.** An engram is a signed, NIP-44-encrypted Nostr event, and the
`d` tag the relay indexes by is `HMAC(conversation_key, slug)` — so the operator
holding the data can read neither its content nor which memory it is, and cannot
tell two related slugs apart. Every other private-by-design system in this atlas
protects the payload; this is the only one that blinds the *index*. The price is
paid in the same place: engrams are parameterized-replaceable events, so the
relay keeps one head per tag and discards what it overwrites. There is no
history, no retrieval beyond following `[[slug]]` references from a `core`
engram, and no model in the loop at all.

**Gobii inverts what a memory system decides.** Its durable store is a SQLite
file the *agent* designs: no `MemoryRecord`, no extraction pass, no embeddings —
one database per agent, a generated schema prompt capped at 30,000 bytes and 25
tables, and a SQL tool with roughly 12,000 lines of guardrails, autocorrect,
recovery and digest around it. The platform mounts its own state as eight
double-underscore tables — `__messages`, `__files`, `__contacts`,
`__agent_config`, `__agent_schedules`, `__agent_skills`, `__tool_results`,
`__kanban_cards` — so the agent can join its own data against the platform's,
and **every one of them is dropped before the file is persisted**. What survives
is only what the agent created.

The mechanism worth copying is one string per table. `BUILTIN_TABLE_NOTES`
writes each built-in table's mortality into the schema prompt — *"built-in,
ephemeral (dropped before persistence)"*, *"reset every LLM call"* — so the model
is told what survives before it chooses where to put something. Every other
system here decides the persistence boundary and leaves the model to infer it.
Its scope enforcement is also unlike anything else in the corpus: a `sqlite3`
authorizer denies `ATTACH` and `DETACH` so no query can mount another agent's
file, alongside `load_extension`, `readfile`, `writefile` and five pragmas — the
boundary held by an engine callback rather than a query predicate.

The cost is on the other side of the same decision. A model-authored schema
means there is no shape an operator can write against: no tombstone is possible,
no trust column exists unless a model invented one, and an erasure request
cannot be satisfied generically because the tables differ per agent and were
named by an LLM. It is the clearest case in the atlas of deletion being not
unimplemented but *inexpressible at the platform level*.

**Cortex asks a question nothing else here asks: may the agent be *told* this?**
Every memory carries a sensitivity from `public` through `secret`, and
`memory_search` classifies what it is about to return: a supervisor-requiring
result runs `requestSupervisorDecision` and a refusal returns
`Access denied: <reason>`, while a `secret` result goes to
`context.approvalGate` or `requestHumanApproval` and a no returns
`Access denied by human approval`. Fifteen other systems in this atlas hold the
human-review mark and every one of them reviews a **write** — approving a memory
before storage or editing it after. This one reviews a **read**, fails closed on
refusal, and lets a headless deployment inject its own gate function. It is the
closest thing in the corpus to memory access control with a person in the loop,
and it is a different axis from the seven columns rather than a stronger score on
them: Cortex has machinery for *disclosure* risk and none at all for *epistemic*
risk — no supersession, no trust state, no tombstone, and consolidation that
rewrites.

Beside it sits the sharpest instance of declared-and-unwired in the atlas.
`src/memory/privacy.ts` defines a `MemoryPrivacyPolicy` with `allowedTiers`,
`piiRedaction` and a `maxRetentionDays` defaulting to 90, with setter, getter,
redactor and a sensible default, all exported from `mod.ts` — and **nothing
calls `getPrivacyPolicy`**. No read consults the allowed tiers, nothing expires
at ninety days, and the `redactPII` the pipeline actually runs is a separate
duplicate defined in `pipeline/builtin.ts`. The policies live in a process-local
`Map`, so even wired they would reset to permissive on restart. An auditor
reading that file for retention behaviour would draw a guarantee out of it that
does not exist. Its tier vocabulary is also the one place tiers are load-bearing,
and the tier filter in `memory_search` carries a `NOTE` admitting that asking for
`reflection` or `graph` returns semantic results instead.

**OpenHuman is the largest memory subsystem in the atlas — twelve modules, some
76,000 lines, about 1,278 memory tests — and it earns its place on one field.**
`MemoryTaint` labels every entry `Internal` or `ExternalSync`, fails closed to
the restrictive value for unknown or corrupt columns, and gates which memories
may drive external-effect tools. Every other trust mechanism here answers *is
this memory true?*; this one answers *what may this memory be allowed to cause?*,
which is the question that matters once the store is an injection surface. It is
not a trust state — provenance is assigned at ingest, never narrowed by
corroboration, and a user's mistaken belief is `Internal` like any other — so
the mark is withheld and the near-miss recorded instead, because the axis it
opens is one this atlas does not currently count. Its companion decision is as
good: the secret and PII scrubbers deliberately leave the taint untouched, since
redaction must not launder provenance.

Tradeoff: deeper integration buys behavioural control at the cost of coupling
memory to the framework, prompt assembly, and tool loop.

### Host runtimes with pluggable memory

Hosts: `hermes-agent`, `openclaw`, `pi`, `mateclaw`, `opencode`, `nemoclaw`,
`tigrimosr`, `adk-python`, `autogen`, `agno`, `agent-framework`
Plugins mounted on them: `holographic`, `magic-context`, `metaclaw`,
`byterover`, `tencentdb-agent-memory`, plus hosted providers

The runtime ships an interface, not a memory model. **Hermes** bounds its own
curated Markdown hard and freezes it into the prompt at session start while
mounting one external provider. **TigrimOSR** is the exception that proves the
family's rule: its own memory is one `memory.md` per project, and the mechanism
worth copying is beside it — a skill synthesizer that stages a proposed skill as
`SKILL.md.proposed` next to the live file, keeps the rationale and the sessions it
came from, waits for a person, and promotes by rename. It also forces review when
the target skill was authored by a human rather than by the automation, which
nothing else here does. **OpenClaw** ships memory entirely as
extensions over a plugin contract. **Pi** is the limit case: twenty-plus
lifecycle events and no memory concept at all, so plugins rebuild indexing,
scope, and retrieval from scratch. **OpenCode** is the commoner case and
the more instructive one: it ships the two hooks a memory plugin needs — a
system-prompt transform and a compaction hook — marks both experimental, and
offers no memory contract, so the plugin this atlas reviews from the other side
reads its SQLite session tables directly. A host that offers seams without a
contract does not avoid the design work; it relocates it into every plugin, in
incompatible forms. **NemoClaw** sits a layer lower again: it sandboxes
Hermes and OpenClaw and declares, per agent, which state directories exist and how
each is snapshotted, restored and destroyed. Credentials are sanitized field by
field on backup; memory is a directory, copied whole — so the most careful
deletion above is undone by an ordinary restore below.

Tradeoff: users choose a backend that fits their privacy and scale needs, but
trust state, scope, and above all deletion must cross the host/provider
boundary. **MateClaw** is the partial counterexample: its provider SPI carries an
owner key on `prefetch` and `syncTurn`, and wraps every provider in retry and
metrics decorators — but like the other three, it has no deletion hook.

**Google's ADK is the largest instance of the same finding, and it inverts the
first half.** `BaseMemoryService` makes `app_name` and `user_id` *required
keyword arguments* on every write and on `search_memory`, so a provider in that
framework cannot forget which user it serves without discarding arguments it was
handed — the strongest scope enforcement in the atlas, and enforced by a
signature rather than a query. Then it declares `add_session_to_memory`,
`add_events_to_memory`, `add_memory` and `search_memory`, and **no removal method
of any kind**, while the sibling `BaseSessionService` does declare
`delete_session`. Content promoted out of a deletable session into memory becomes
unremovable through the framework. **Microsoft's AutoGen is the same finding one level deeper.** Its `Memory`
protocol is five methods, and `MemoryContent` carries content, a MIME type and
metadata — **no identifier**. So the absent delete is not an omission but a
consequence: with nothing to address a memory by, a targeted removal cannot be
written, and `clear()` — wipe everything — is the only removal verb in the
protocol or in any of its ChromaDB, Redis, Mem0 and canvas adapters, both of the
first two backends supporting targeted deletion natively. Scope is missing from
the contract too, present only on the Mem0 adapter, optional, and defaulting to
`user_id or str(uuid.uuid4())` — so a forgotten principal is a silently orphaned
store rather than an error.

**That finding has now been refuted once, and by whose contract matters.** For
six framework contracts the count held — two carried scope, none carried
deletion, and AutoGen's could not express one. Of the nine now read, the
[Pydantic AI Harness](../systems/pydantic-ai-harness/)'s `MemoryStore` Protocol
declares `read`, `get_operation`, `write`, **`delete`** and `list_paths`, with
search split into an optional `SearchableMemoryStore` extension. It is a
targeted, addressed removal in the contract itself, and it is the only one. The
three contracts added since — Agno's `LearningStore`, Microsoft's
`ContextProvider`, and CAMEL's `AgentMemory`, whose only removal verb is `clear`
— leave the shape unchanged. So the honest statement is no longer "nobody
declares deletion" but **one of nine does**, which is the stronger claim: it
proves the thing is expressible in a small protocol, and names who bothered. See
[pluggable memory provider](../patterns/pluggable-memory-provider/).

**Microsoft's next contract is the third from these two vendors and keeps the
gap.** [Agent Framework](../systems/agent-framework/) succeeds both AutoGen and
Semantic Kernel, and its `ContextProvider` is `before_run`, `after_run` and a
`source_id` — a context-engineering seam rather than a memory interface, with no
add, no query, no delete and no scope. That is a more honest position than
AutoGen's, which promised a `Memory` protocol and could not express a targeted
removal; it also means deletion and tenancy are reinvented per provider. The
in-tree harness memory then supplies what the contract declines, and its scoping
is among the best in the atlas: the owner id is read from session state and
**raises when missing**, `..` and absolute segments raise, and after resolving
the per-owner root the store asserts it is still inside the base path and raises
*"Memory storage path escaped base_path"* if not. Three checks for one boundary,
in a framework whose contract asks for none — and its correction path is an LLM
rewriting the durable topic file into "a tighter durable form", with no diff and
no previous version kept.

**Agno is the third framework contract and the one that answers the question
instead of deferring it.** Its `LearningStore` Protocol is six methods —
`recall`, `process`, `build_context`, `instructions`, `get_tools`, and a
`learning_type` key — and unlike ADK and AutoGen it ships six implementations
behind it rather than an in-process dict. That changes what the contract can be
judged on. `recall(user_id)` returns `None` when the scope key is missing, so
the fail-closed behaviour ADK gets from a signature, Agno gets from the body.
Deletion is present and per-store: `retire_fact` keeps the superseded row with
`superseded_by` naming its replacement, `forget` archives an entity, and both
are exercised by tests. It also shows what a contract does *not* fix. The
protocol has no notion of approval, so `LearningMode.PROPOSE` — advertised as
agent-proposes-human-confirms — is implemented as a different return value from
`instructions()`, a prompt telling the model to ask before calling
`save_learning`, while `save_learning` itself writes unconditionally. A gate
that exists only in the string handed to the model is not a gate, and it is the
clearest instance in this atlas of the difference between instructing a
behaviour and enforcing one.

### Local coding-agent memory

`engram`, `mempalace`, `llm-wiki-memory`, `basic-memory`, `moltis`,
`open-cowork`, `byterover`, `magic-context`, `swafra`, `memora`, `ai-memory`,
`ctx`, `optmem`, `openworker`, `qwen-code`, `daimon`, `reme`, `acontext`,
`logseq`, `everos`, `ecc`, `skales`

Durable local state for a developer workflow: hooks, MCP, project scopes, exact
search. **Engram** is the small no-extraction baseline over SQLite and FTS.
**MemPalace** keeps verbatim drawers authoritative and treats extracted layers
as navigation aids. **Basic Memory** makes human-editable Markdown canonical
and every index a rebuildable projection. **Moltis** indexes a Markdown corpus that sanitized
session transcripts are exported into, so conversations become searchable notes
in the same substrate as curated ones. **open-cowork** separates core from experience memory and
ships the atlas's most complete memory benchmark. **ReMe** is the one that
publishes its *results* rather than its harness — per-category LongMemEval and
BEAM tables committed to the repository, its worst score among them — and carries
the atlas's only validated correction vocabulary outside Memanto:
`CREATE | CORROBORATE | REFINE | CORRECT`, with an additive-only update rule that
nothing checks. **Acontext** is the one that finally implements the gate this
atlas has been asking for: a task's `status` is constrained to
`success | failed | running | pending` by a database CHECK, only the two terminal
values enqueue learning, and three committed tests assert that the other cases
write nothing. **Swafra** shows how little
code a local graph-RAG sidecar needs, and — since its v0.3 line — how narrowly a
correction mechanism can miss. It now retains superseded facts with a validity
end instead of deleting them, and demotes the chunks behind them at search time;
but the fact id hashes `source_id` alongside the value, so the same value
restated in a *different session* is stored fresh as current, and the whole
lifecycle is absent from the six MCP tools, leaving a ranking multiplier as its
only consumer. Its SQLite tier also declares a normalised `facts` table with
`valid_from` and `valid_to` that nothing writes — the shape
[PowerMem](../systems/powermem/) showed first.
**Qwen Code** has three memory tiers and commits the third to the
repository, so shared memory is distributed by `git pull` — and a write to that
tier containing a detected secret is refused *unconditionally*, even when the
tier is switched off, because the directory is source-controlled regardless.
**OpenWorker** carries a 260-line memory whose real artifact is the
paragraph governing it, and a comment recording why it exists: without
when-to-remember rules, "models either never call `remember` or save noise the
repo already records". **OptMem** is the limit case in the
other direction: 860 lines, an append-only log the code never edits, a binary
merge tree whose resolution decays with age by geometry rather than policy, and
**no background work at all** — every compression is printed in the output of
`note` for the agent to answer in its own turn. **ctx** is the only system here
that bounds where its background consolidation may write — a path guard with one
disposition-gated exception — and the only one whose tests include a corruption
corpus drawn from published research. **ai-memory** models the thing an
interrupted task leaves
behind: a `Handoff` addressed from one harness to another, carrying open
questions and next steps, which expires if nobody accepts it. **Memora** is the
only system here whose automated correction pass defaults to a dry run: the sweep that would hide superseded memories reports its findings
unless mutation is explicitly requested. **Daimon** narrows the unit of memory
to the session boundary — one checkpoint written when a session ends, one
skimmable briefing injected when the next begins — and spends its complexity
budget on checking the extraction rather than on retrieving from it.

**ECC makes the honest declaration the rest of this family avoids.** Its vault
schema gives `trust` an enum of exactly one value — `unreviewed` — and documents
why: verified knowledge is promoted into a governed artifact elsewhere rather
than upgraded in place, so the store never claims authority it cannot support.
Set beside the systems here carrying a `confidence` float nothing revises, a
field that can only say "not checked" is the more truthful design. Its `status`
enum is the counterweight: `active | rejected | superseded` is validated and
filtered on both read paths, and every write sets `active`, so two thirds of the
state machine is honoured on read and reachable only by hand-editing a
Markdown file.

**Skales is the atlas's clearest case of a deletion affordance that does not
delete.** Its memory page renders a bin icon beside every known fact; clicking it
confirms *"Delete fact «key»?"*, computes the object with the key removed,
discards it, and shows a modal reading *"Deletion not yet supported in UI. Ask
Skales to 'forget the fact {key}' in chat."* No forget verb exists in the
application. The only two occurrences of the word outside the locale files point
the other way — `forget` is a keyword that **boosts** `action_item` retrieval,
and `don't forget …` is a capture pattern that **stores a new memory**. The
product is otherwise a competent zero-LLM design: regex capture on a 90-minute
watermarked scan, and retrieval scored `0.70 / 0.20 / 0.10` under a stated
sub-100ms budget with no model in either path.

**Logseq is the odd member and the only one here that is not developer-shaped**
— a twelve-year-old outliner that grew an MCP server, filed beside Basic Memory
and llm-wiki-memory because it is the same bargain: a store a human authors,
which an agent may now write into. It contributes the one thing no other system
here has, which is a **user-defined schema**: properties carry a declared type
and a cardinality, tags are classes that extend other tags and declare the
properties their instances hold, and `listTags`/`listProperties` let a model
discover that ontology before writing inside it. Everywhere else the memory
model is the vendor's; here it is the user's. Its retrieval is also the most
carefully gated in the atlas — exact title, FTS5 over a trigram tokenizer, a
`LIKE` arm for two-character queries, fuzzy, and a local 384-dimension vector arm
fused by reciprocal rank, with the expensive arms skipped when the cheap ones
already filled the limit. And it is fully offline, embeddings included. The
failure is at the seam: agent writes land live and **unmarked** — the schema
defines a `created-by-ref` property that the MCP write path never sets — so the
store cannot answer "what did the agent change?", and the agent has no delete
verb with which to correct itself.

Tradeoff: operationally simple and inspectable; no answer to hosted ranking,
multi-tenancy, or rich user modelling.

### Graph, temporal, and symbolic memory

`graphiti`, `cognee`, `hipporag`, `holographic`, `gini-agent`, `memvid`,
`neo4j-agent-memory`, `memary`

Structure is the retrieval mechanism. **Graphiti** tracks transaction time and
real-world validity separately, invalidating facts by closing an interval
rather than erasing history. **HippoRAG** seeds a personalization vector and
lets Personalized PageRank diffuse relevance instead of planning hops, and
links similar entities rather than merging them. **Holographic** encodes facts
as SHA-256-derived phase vectors so entities can be bound and unbound
algebraically, with no embedding model to version. **Gini** reimplements the
Hindsight model locally with bi-temporal columns and four RRF-fused channels. **Neo4j Agent Memory** adds a third tier beside short and long term —
reasoning memory, recording traces and tool calls through a context manager, so a
raised exception becomes the outcome and **failures are stored by default** where
almost everything else here records only successes. **Memary** is the family's minimum viable
member and the clearest one to read: a LlamaIndex graph, plus forty lines that
count how often each entity has been mentioned — the smallest complete instance of
reinforcement by frequency in the atlas, and the one where that mechanism is
demonstrably inverted at its only point of use. **Memvid** gets time travel
from its storage format rather than its
schema: an append-only file of immutable frames, so a memory card keyed
`entity:slot` can be read as of any past instant and a whole session can be
replayed.

Tradeoff: structure answers questions flat stores cannot, but extraction and
resolution mistakes have a blast radius proportional to how connected the graph
is.

### Verification and trust-first memory

`verel`, `rainbox`, `magic-context`, `metaclaw`, `gini-agent`, `core-memory`,
`daimon`

These treat memory as a trust problem before a retrieval problem. **Verel**
separates confidence, retrieval strength, and verification state, carries
rejected values forward, and fences recall as untrusted data. **RainBox** adds
governed atomic correction, lattice-aware conflict detection, and rejected-value
tombstones that block model re-assertion. **Magic Context** maps each memory to
the files it describes and re-verifies when git reports those files changed,
keeping lifecycle and verification on separate axes. **MetaClaw** applies the
idea one level up, promoting a candidate *retrieval policy* only when it does
not regress across eight measured deltas. **Core Memory** goes furthest on the
axis: a record's epistemic grounding sets a *ceiling* on how trusted it can ever
become, so a speculative memory cannot be promoted into canon by being recalled
often — the guarantee is structural rather than procedural. **Daimon** attacks
the problem one step earlier than any of them: the model is asked to label each
item verbatim or inferred *and to cite the span*, and then code greps the quote
against the transcript and downgrades the item when it is not there. Everywhere
else in this family, trust is assigned by policy over a claim; here the claim's
own evidence is mechanically falsifiable, which is why it is the only system in
the atlas whose trust classes can be wrong in a way the system itself detects.

Tradeoff: more machinery than an MVP needs, and it directly addresses the
failures simpler systems discover in production.

### Research lineage

`generative-agents`, `voyager`, `hipporag`, `a-mem`, `memoryos`, `nooa-memory`,
`second-me`, `simplemem`, `livingfeed`, `mnemopi`

Artifacts the practical systems are largely responses to. **Generative Agents**
established the observation/reflection/planning stream and the
importance-recency-relevance score — whose weights, read at the source, are
hand-tuned constants with two abandoned settings left in comments. **Voyager**
established procedural skill memory with an execution-verified write gate.
**HippoRAG** established diffusion-based associative retrieval. **Second Me** is
the only system here whose memory ends up in *weights*: documents become a
versioned biography, the biography becomes synthesized training data, and LoRA
fine-tuning plus DPO produce a local model that answers without retrieving
anything. It is the atlas's single instance of parametric memory — see the limitations for
what one instance is and is not evidence of. **NOOA Memory** implements the cognitive models the others
approximate — ACT-R base-level activation with spreading activation for
retrieval, the Ebbinghaus curve for forgetting — and stores the score
components of every retrieval on the memory that was retrieved. **MemoryOS** is
the tiered short/mid/long architecture in its most legible form, with the
promotion rule written down as `alpha * N_visit + beta * L_interaction + gamma *
R_recency` — and the coefficients left at 1, 1 and 1 with no ablation, so
verbosity scores like importance.

**LivingFeed answers the criticism this atlas makes of the family's founder.**
[Generative Agents](../systems/generative-agents/) ships `gw = [0.5, 3, 2]` as
hand-tuned constants with no committed ablation, and [MemoryOS](../systems/memoryos/)
leaves its promotion coefficients at 1, 1 and 1 with nothing measuring them.
LivingFeed composes importance as `0.35·emotion + 0.30·relationship +
0.20·goal + 0.15·rarity` and then stores **all four components on the memory**,
in a required `factors` object its schema describes as the material for
coefficient tuning by offline replay. Storing a composite score's parts rather
than only its total is the cheapest answer in the corpus to the hand-tuned-weights
problem, and it costs four floats.

Its second rule is the second divergence stated as schema policy: *"forgetting
happens only in Semantic; the original is not erased"*. Semantic points carry a
`decay_at` computed from importance — one day at zero, thirty at one — and recall
filters on it, so expiry needs no sweeper and the episodic event that produced
the memory is permanent. Provenance is mandatory in the same direction:
`source_event_ids` is `minItems: 1`, with the rule cited inline as *"any memory
is audit-traceable"*. The documentation and comments are in Korean, so the terms
here are translations, as with [GenericAgent](../systems/genericagent/). The
failure worth naming is at the boundary: recall catches every exception, logs
*"recall failed (bypassing with empty recall)"*, and returns an empty list — so
an unreachable index produces an amnesiac actor and a quiet world looks
identical to a broken one.

**SimpleMem is the family's most useful single idea and its sharpest warning.**
Its `MemoryEntry` carries a `lossless_restatement` built by two declared
transforms — `Φ_coref`, resolving every pronoun, and `Φ_time`, absolutising
every timestamp — so a stored unit is legible with no surrounding turn. That is
context-independence bought once at write instead of reconstructed at every
read, it is a prompt and a schema rather than an architecture, and it is
portable into any extractor in this atlas. The warning is what surrounds it. The
store holding those units offers `add_entries`, three searches and `clear()`:
no delete, no update, and no scope key to delete by, so the pillar the papers
and the packaged Claude skill are about cannot remove one memory. Its
governance apparatus — `scope_id` on every read, an append-only `memory_events`
log recording seven mutation kinds, a `scope_access` principal table — lives in
EvolveMem, the newest and least tested of the repository's three pillars, and
does not touch the benchmarked one. It also states its own inversion of the
corpus: `MemoryEntry.timestamp` is when the described event happened, and
nothing records when the system learned it, so SimpleMem has the validity clock
almost everything here lacks and lacks the record clock almost everything here
has.

Tradeoff: the ideas are unusually legible because no production concern
obscures them, and none of these has scope, correction, deletion, or a trust
model. Voyager and Generative Agents have been frozen since 2023; read them for
design, not adoption.

### The category almost nothing models: prospective memory

[NOOA Memory](../systems/nooa-memory/) carries two memory types almost no other
system in this atlas has: `intent` — "prospective: trigger-based reminder (when
X…)" — and `todo`, "prospective: durable commitment with an open/done" lifecycle.
Nearly everything else here remembers what *was*; these remember what the agent
has undertaken to do.

**The second occupant differs in the way that matters.**
[MineContext](../systems/minecontext/) has a `todo` table — `content`,
`start_time`, `end_time` as a deadline, `urgency`, `assignee`, `reason`, and a
`status` integer with exactly two values, stamped with an `end_time` on
completion by `update_todo_status`. It also has an `INTENT_CONTEXT` type for
"future plans, goal setting, and action intentions", and its `ContextProperties`
model documents `event_time` as "event occurrence time, **can be future**" —
which is the cheapest route to prospective memory anyone here has found, since a
system that already separates event time from record time is most of the way
there.

But NOOA's commitments are *declared* and MineContext's are *inferred*. Its
`SmartTodoManager` reads recent activity, pulls the relevant contexts, checks
which historical todos were completed, and asks a model to extract tasks with due
dates and priorities from what it watched the user do. It remembers commitments
the user never made — and, per its report, offers no surface on which to reject
one.

[Gobii](../systems/gobii/) is a third occupant and it satisfies a different two
of the three requirements below. Its `PersistentAgentKanbanCard` is a durable
commitment with an enforced `todo`/`doing`/`done` lifecycle and a `completed_at`
— the strict lifecycle NOOA has and MineContext approximates with a two-valued
integer — but its triggers are cron (`PersistentAgentCronTrigger`,
`PersistentAgentSchedule`) rather than semantic, and nothing can reject a
commitment such that it cannot be recreated. Its SQLite mirror of the board,
`__kanban_cards`, is one of the eight tables dropped before persistence, so the
durable copy lives in Postgres and the agent sees a per-cycle projection of it.

[Mnemopi](../systems/mnemopi/) is a fourth arrangement and satisfies none of the
three. It has the *vocabulary* — `COMMITMENT` and `GOAL` are two of its fourteen
first-class memory types — and gives them a decay curve instead of a lifecycle:
`commitment: { k: 1.0, eta: 240.0 }`, and a Weibull with k=1 is exactly an
exponential, so a commitment's survival is memoryless and it is gone in about ten
days whether or not it was ever discharged. An obligation is the one memory type
where the correct behaviour is to persist undiminished until it is met and then
stop, which is a state machine and not a half-life.

Four occupants bracket the design question rather than settling it. A declared
commitment is a memory; an inferred commitment is a claim about someone's
intentions, which is a stronger claim than any preference in this atlas and the
one most costly to get wrong.

**Why the category is nearly empty is a boundary dispute, not an oversight.**
Ordinary software already has somewhere for future commitments to live — a
scheduler, a job queue, a state machine — and on that division memory is the
passive store and the queue is what acts. The reason that division does not
survive contact with an agent is the *trigger*. "At 09:00 tomorrow" belongs in
cron. "The next time we discuss project scope" does not, and cannot: matching it
requires the incoming turn, the stored commitment, and something able to judge
that the two are about the same thing. That is a retrieval operation, so the
commitment has to sit where retrieval can reach it. What the field has built
instead is retrieval tuned entirely for *what was*, which is why the two systems
that got here arrived by extending a memory schema rather than by adding a
scheduler.

The gap is also visible from the other side, in systems that hold a future
without committing to it. [ai-memory](../systems/ai-memory/)'s handoff is a typed
record of unfinished work addressed from one harness to another, carrying open
questions rather than conclusions — genuinely forward-looking, and a snapshot of
an interruption rather than a durable obligation with a trigger and a lifecycle.
The distance between those two things is the whole category.

Three requirements follow from the two implementations, and no system here has
all three: a **semantic trigger** that retrieval can evaluate rather than a
timestamp a scheduler can fire; an enforced **lifecycle** on the commitment, so
open, done and abandoned are distinguishable states rather than a derived
guess; and — for anything that *infers* commitments — a way to
[reject](../patterns/rejected-value-tombstone/) one, keyed on the commitment, so
a hallucinated obligation the user disowns cannot be re-extracted from the same
transcript on the next pass. MineContext infers and has no rejection surface,
which is the combination this atlas would flag anywhere else in memory and which
matters more here: a wrong preference bends an answer, and a wrong obligation
makes the agent act.

The nearest other neighbour is [ai-memory](../systems/ai-memory/)'s handoff with
its `next_steps` list, and that is a record of an interrupted task rather than a
trigger. Whether prospective memory belongs in a memory layer or in a scheduler
is a real question — but it is being answered by omission nearly everywhere, and
an agent that cannot remember its own commitments will keep rediscovering them.

### The category that competes on control, not accuracy

Six systems here — [SillyTavern](../systems/sillytavern/),
[RisuAI](../systems/risuai/), [Project N.E.K.O.](../systems/neko/),
[Soul of Waifu](../systems/soul-of-waifu/), [Z-Waif](../systems/z-waif/),
[VirtualWife](../systems/virtualwife/) — are roleplay and companion clients, and
reading them together produces a finding the seven-column rubric cannot express.

Between them they hold four marks out of a possible 42. On the epistemic
questions this atlas usually asks — is there a tombstone, a trust state, a
validity time — the answer is mostly no. And these are, by hours of use, among
the most-exercised memory implementations in existence, running against users who
would notice immediately if memory failed them.

The resolution is not that the users are undemanding. It is that **the axis they
demand on is different.** What a companion user means by good memory is not
autonomous factual accuracy; it is *authorial control* — being able to see what
the model will read, and change it. Judged on that axis these systems are not
primitive but mature, and the mechanisms are specific:

- **Editability as the primary write path.** SillyTavern has no extraction at all;
  a person writes every entry. RisuAI's HypaV3 modal lets a user edit, delete,
  merge, pin and re-roll any summary the model wrote, with the re-roll previewed
  before it lands. This is the [memory as an editing
  surface](../patterns/memory-as-an-editing-surface/) pattern, and its clearest
  instances are all in this group.
- **Suppression as a first-class state.** `@@dont_activate` disables an entry
  without deleting it; N.E.K.O.'s ban-topic directive is keyed on the term and
  withholds it from recall; RisuAI's pin exempts a summary from budget pressure.
- **Hysteresis on activation.** Sticky, cooldown and delay give a unit state about
  its own recent firing, so it neither repeats every turn nor drops mid-thread —
  see [retrieval hysteresis](../patterns/retrieval-hysteresis/). Nothing outside
  this group has it.
- **Guarding against the agent's own voice.** Z-Waif caps the character's previous
  reply at two of six query terms; N.E.K.O. runs a BM25 corpus over its own
  output to catch rephrased repetition.

Read the four marks accordingly. A dash in the tombstone column means the
mechanism was not found, and for a store whose only writer is the user it is a
different absence than it would be in an extraction pipeline — there is no
extractor to re-assert what was removed. The columns still measure what they
measure; what they do not do is score these systems on the thing they were built
to be good at.

Two transfers run the other way, out of this group and into serious systems.
N.E.K.O.'s separation of disputation from reinforcement is built because raising
something a user asked you to drop is an emotional injury — and it is the same
architecture that stops a customer-service agent volunteering a declined mortgage
or a CRM summary asking after a late spouse. And the editing surface is the
cheapest correction mechanism in this atlas: one click, no model, no trust-state
machine, fixing a fact the user knows and the extractor guessed.

### Not in scope: conversation-window management

Most agent frameworks ship something called "memory" that is a **chat buffer**,
and the naming collision misleads people evaluating options.

IBM's [BeeAI framework](https://github.com/i-am-bee/beeai-framework) is the
cleanest example. At commit
[`21284d7f53d5a50e546350f371c69747bd6a176b`](https://github.com/i-am-bee/beeai-framework/commit/21284d7f53d5a50e546350f371c69747bd6a176b)
its entire memory subsystem is about 1,300 lines across both the Python and
TypeScript implementations, and consists of four strategies for deciding which
messages stay in context: `UnconstrainedMemory`, `SlidingMemory`, `TokenMemory`,
and `SummarizeMemory`, plus a `ReadOnlyMemory` wrapper. Its documentation states
that "Messages are the fundamental units stored in memory". The memory modules
reference no embeddings, vectors, or persistent store; BeeAI keeps document
retrieval in a separate `rag` module, so the framework's own architecture agrees
these are different concerns. LlamaIndex's older `ChatMemoryBuffer` family and
LangChain's original `ConversationBufferMemory` are the same category — which is
why this atlas reviews `langmem` and LlamaIndex's newer block-based `Memory`
instead.

Deciding what stays in the context window is a real problem. It is a different
problem: nothing survives the session, nothing is retrieved, nothing is scoped,
corrected, verified, or forgotten on request. A system whose memory is a window
has no answer to "why do you believe that?" or "forget what I told you last
week", because it never claimed to remember.

The most sophisticated instance of the category is worth naming, because it
shows the boundary is about *architecture* rather than about effort. ByteDance
and Tsinghua's [MemAgent](https://github.com/BytedTsinghua-SIA/MemAgent)
(Apache 2.0, at
[`ef4219b23499a069cb00e5daff4c426d4c600851`](https://github.com/BytedTsinghua-SIA/MemAgent/commit/ef4219b23499a069cb00e5daff4c426d4c600851))
processes arbitrarily long input in fixed context by walking it chunk by chunk,
and at each step the model is handed the problem, the previous memory, and the
next chunk, and asked to emit an **updated memory** that overwrites the old one.
What it keeps is not decided by a heuristic or a prompt-engineered summarizer:
the whole loop is trained end-to-end with multi-conversation RL against the
final answer's reward, so the retention policy is *learned* — dropping the wrong
detail costs reward several chunks later. The published claims are strong (a
model trained at 8K extrapolating to 3.5M-token tasks with under 5% loss, 95%+
on 512K RULER), and the mechanism is genuinely novel: nothing else this atlas
has read learns what to remember rather than being told.

It is still out of scope, and the code says so plainly. `self.memory` is a
NumPy object array allocated in `start()` per batch, carried across chunks of
one input, and discarded; there is no persistence path, no retrieval, no scope,
and no identity a later correction could name. It is a compressor with a learned
policy rather than a memory with a lifecycle — the same category as BeeAI's
`SummarizeMemory`, several orders of sophistication up. That the best learned
context compression in the field lands outside this atlas is the clearest
argument that the boundary is drawn in the right place.

A second boundary is worth naming because it is where this atlas most often
declines something interesting: **a durable store an agent operates is not
memory.** [beads](https://github.com/gastownhall/beads) (MIT, at
[`dbbf3a9618aacaab20427f7bc1f7b35b6edab3ba`](https://github.com/gastownhall/beads/commit/dbbf3a9618aacaab20427f7bc1f7b35b6edab3ba)) is a
distributed graph issue tracker for AI agents, Dolt-backed, and it passes the
literal test — issues persist across sessions, carry identity, and can be
corrected. So would Jira. The distinction that keeps the atlas from swallowing
every agent-adjacent database is whether the store exists to hold what the agent
*believes* or what the agent *operates on*: a task database is the second. It is
noted here rather than dropped because [Core Memory](../systems/core-memory/)
borrows the "bead" vocabulary, and a reader meeting both could reasonably assume
a relationship.

The nearby case is a corpus index. `VectorSpaceLab/general-agentic-memory` (GAM)
builds an LLM-generated directory tree over long documents, video, or agent
trajectories, with a Memory and TLDR summary per chunk and an agent that
navigates the taxonomy to answer questions. That is a hierarchical index with
exploratory QA over it — the shape [OpenViking](../systems/openviking/) already
covers with its L0/L1/L2 granularities, and one this atlas would need a reason
to add again. It also carries **no licence file**. The OptMem exception was
granted for mechanisms found nowhere else; an auto-generated taxonomy over a
document tree is not that, so GAM gets a note rather than a report.

A third shape declines for a reason worth separating from the other two: **an
algorithm workbench is not a memory system.** `nuster1128/MemEngine` appears in the
open-source framework table of the field's own 107-page survey as a representative
memory framework with a "modular space" structure, and it implements ten named
memory methods — `FUMemory`, `GAMemory`, `LTMemory`, `MBMemory`, `MGMemory`,
`MTMemory`, `RFMemory`, `SCMemory`, `STMemory` — behind one `BaseMemory` interface
with `store`, `recall`, `manage` and `optimize`. It is a genuinely useful thing:
a common harness for comparing published memory algorithms against each other.

It stores nothing. `LinearStorage` in `memengine/utils/Storage.py` is a Python
list; `reset()` empties it; `BaseMemory` declares no save or load; and
`server_start.py` keeps sessions in `service_database = {}`, an in-process dict
addressed by a UUID that does not survive a restart. Nothing in the package writes
to disk except a `Display` utility and the config reader. So MemEngine cannot fail
this atlas's test in an interesting way — nothing survives the session to have an
identity, let alone a correction. It also carries **no licence file**, which would
have excluded it independently.

That a peer-surveyed "open-source memory framework" turns out to have no
persistence layer is not a criticism of the project, which is honest about being a
research library. It is a reason to be careful with framework lists: the word
covers both a store you would run in production and a benchmark rig for comparing
algorithms, and only one of them can answer "forget what I told you last week".

A fourth shape is the most frustrating one to decline, because it is closer to
this atlas's concerns than most of what it does review: **a guard is not a
store.** [OWASP Agent Memory Guard](https://github.com/OWASP/www-project-agent-memory-guard)
(Apache 2.0, at
[`78b9227f5d832cfe83b1d3f01dbcb6f51235dc39`](https://github.com/OWASP/www-project-agent-memory-guard/commit/78b9227f5d832cfe83b1d3f01dbcb6f51235dc39))
is the reference implementation cited by the security survey above, and it is
the closest public code to that survey's Verifiable Memory Governance. Its
`MemoryGuard` screens every read and write through a detector suite, and it
carries mechanisms the atlas counts and rarely finds:

- A **classification graph** with typed transitions —
  `ephemeral → user_preference_candidate → verified_preference`, where that last
  edge sets `requires_verification=True` and `promote()` refuses without an
  explicit `verified=True`. That is a trust state machine with a human opt-in on
  the promoting edge, and it is enforced rather than advisory: writing with a
  different class raises rather than silently reclassifying.
- **Snapshots and rollback**, including a pre-snapshot before every blocked
  write and before every `retire_if` sweep — Rollbackability, which the survey
  calls "largely absent".
- A **self-reinforcement detector** aimed squarely at the failure this atlas
  keeps naming: an agent reading its own prior claim, elaborating it, and
  writing it back until a hallucination hardens into a fact. It fires only on
  `AGENT_AUTHORED` writes and resets when independent evidence arrives.

It gets no report because **nothing survives the process.** The only shipped
`MemoryStore` implementation is `InMemoryStore`, a dict; `SnapshotStore` is a
50-entry `OrderedDict` ring buffer; the event log is a Python list; and the HTTP
and MCP servers both construct `MemoryGuard(policy=...)` with no store. The
`MemoryStore` Protocol is the extension point, and the durable half is the
reader's to supply. So the same rule that excluded MemEngine applies, for a
different reason: MemEngine had no store because it is a workbench, and this has
no store because it is a layer.

Two observations survive the exclusion, and they are why it is recorded at
length rather than dropped. First, the self-reinforcement detector guards a
60-second window over a similarity ratio, keyed by memory key and held in a
deque of eight — it catches a tight write-read-elaborate loop, which is a real
attack, and not the atlas's actual failure mode, where a *nightly* extraction
pass re-asserts what a user corrected last week. Second, its quarantine is the
clearest near-miss on a tombstone in this atlas: a blocked write's value is
stored in `self._quarantine[key]`, exposed as a read-only property, exported to
metrics — and consulted by nothing. Write the same rejected value again and, if
no detector independently matches it a second time, it commits. The one project
in the field built specifically to secure agent memory implements four of the
survey's five primitives, and the one it does not implement is Verified
Forgetting.

**Checkpointing is the boundary case most often argued about, and it belongs
here rather than in the corpus.** LangGraph's native thread-level persistence is
the de-facto standard for stateful agents, it survives the process, and it
supports time-travel — you can rewind a thread to an earlier checkpoint and
resume. Those are real properties and none of them is memory by this atlas's
test. A checkpoint is the *whole state of a run at a point in time*, addressed
by thread and step; it has no unit a correction could name, no scope key beyond
the thread, and nothing that could be individually superseded, rejected or
forgotten. Rewinding a thread discards everything after a point rather than
retracting a belief. It is the same category as [MemAgent](#not-in-scope-conversation-window-management)
above — durable, sophisticated, and about *runs* rather than about what an agent
holds true — which is why this atlas reviews [LangMem](../systems/langmem/), the
layer LangChain built for the other question, and not the checkpointer beneath
it. Read them together and the split is the point: LangMem stores items in a
`BaseStore` namespace precisely because checkpoints cannot hold that shape.

A fifth boundary needs stating only because every list of recent memory papers
puts it beside the systems here: **an architecture is not a memory system.**
*Titans: Learning to Memorize at Test Time*
([arXiv:2501.00663](https://arxiv.org/abs/2501.00663), Google Research) adds a
neural long-term memory module that learns what to store during inference,
alongside short-term attention and persistent memory tokens. It is a genuine
advance and it is a different object: what it memorizes lives in module weights
updated per sequence, with no key, no scope, no provenance and nothing a later
correction could name. It also has **no official implementation** — the
repositories carrying the name are third-party reimplementations, so there is no
canonical artifact to pin even if the boundary were drawn elsewhere. The same
applies to the model-editing line (ROME and successors) that the field's surveys
file under parametric memory. [Second Me](../systems/second-me/) is in this
atlas because it is a *system* that fine-tunes on a user's documents and then
has to answer "delete my data" — the deletion request is what pulls weights into
scope, not the fact of learning.

Eight more candidates were read on 2026-07-29 and declined. They are recorded
because each looks like a memory system from its description, and because two
recurring shapes account for most of them — resource accounting that uses the
word *memory*, and durable state an agent operates rather than believes:

| Candidate | Why not |
| --- | --- |
| [kvcache-ai/AgentENV](https://github.com/kvcache-ai/AgentENV) | An orchestrator for Firecracker microVM sandboxes. Every one of its 176 files matching "memory" means guest RAM, memory ballooning or a memory snapshot; `InMemoryMetadataStore` holds sandbox metadata. Adjacent by name only |
| [deftai/subspace](https://github.com/deftai/subspace) | ACP, A2A and MCP transport plumbing — framer, codec, wire. Its single "memory" match is a test fixture named `memory-message-a` |
| [code-yeongyu/oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) | An agent harness whose durable state is `.omo/boulder.json`, a work ledger the prompt calls "the source of truth", plus a team mailbox with leases and an ack ledger. Its rules engine loads *human-authored* files into context and writes nothing back. This is the `beads` exclusion — a task database and a queue, not a belief store |
| [endomorphosis/ipfs_accelerate_py](https://github.com/endomorphosis/ipfs_accelerate_py) | A model-inference and hardware-routing framework. Its ~4,500 "memory" matches are `memory_mb`, `memory_bytes`, `memory_gb`, WebGPU memory optimisation and resource schedulers — the AgentENV shape again, RAM rather than recall |
| [endomorphosis/swissknife](https://github.com/endomorphosis/swissknife) | A browser-based collaborative virtual desktop that vendors the previous entry's JS port; same `memory` vocabulary, same exclusion. It also ships **no licence file** |
| [endomorphosis/lift_coding](https://github.com/endomorphosis/lift_coding) | A voice-first GitHub workflow assistant. No memory subsystem — the matches are in audio fetching, auth, metrics and a GitHub provider |
| [JesseBrown1980/asolaria-behcs-256](https://github.com/JesseBrown1980/asolaria-behcs-256) | Its `behcs-memory-bridge.js` indexes markdown memory files into addressable "cubes", which sounds in scope until the constant: `const MEMORY_DIR = 'C:/Users/acer/.claude/projects/E--/memory'`. It is a personal index over *another tool's* memory store, at a path that exists on one machine. The 927-line `memoryStore.js` beside it sits under `packages-legacy-import/` and is vendored, so it is not the project's own design either |
| [xD4O/memento](https://github.com/xD4O/memento) | **The reluctant one.** A voice and video journal that is genuinely memory-shaped: `profile_facts`, `threads` and `pins` tables all soft-deleted through partial indexes, and a `deliver_on` column implementing *time capsules* — an entry sealed at record time whose `unseal_due_capsules` worker moves it to `uploaded` on its delivery date, so it enters indexing and retrieval only then. Memory deliberately unreachable until a future moment is a variant of prospective memory nothing else here has. It carries **no licence file**, which excluded GAM and MemEngine before it, and the OptMem exception was granted for mechanisms found nowhere else — a `deliver_on` date gating a status transition is a nice detail, not an architecture. Recorded so the decision can be revisited if a licence appears |

Compaction appears in this atlas only as a component of systems that also
persist — `mastra-observational-memory` with exact covered ranges and buffered
activation, `hermes-agent` with a hard budget forcing in-turn consolidation,
`pi` with deterministic file manifests on compaction entries. The test for
inclusion is not whether a system compacts, but whether anything survives the
session with an identity you could later correct.

## 2. Comparative Matrix

<!-- BEGIN GENERATED MATRIX -->
| Repo | Memory unit | Storage backend | Retrieval strategy | Write strategy | Update/delete model | Scoping model | Agent integration | Background processing | Trust/provenance model | Notable strengths | Main risks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `a-mem` | `MemoryNote` with content, tags, context, links, and evolution history | In-process dictionary plus ephemeral Chroma; separate persistent retriever utility | Vector similarity with optional linked-neighbor append | LLM decides links and neighbor metadata mutation before insert | Delete/re-add update; exact delete without incoming-link cleanup | None in core | Direct Python library | Periodic reindex called consolidation | No source provenance or trust state | Small, legible linked-note evolution concept | Neighbor position/identity bug can mutate wrong notes; destructive initialization; no durability |
| `acontext` | An agent skill — a directory of Markdown files with a SKILL.md the user defines the schema for | Postgres for skills, tasks, sessions and messages; a disk abstraction for the files themselves | None automatic — the agent calls list_skills, get_skill and get_skill_file and decides | A task reaching success or failed triggers distillation, then a skill agent routes and writes | The skill agent rewrites files; the dashboard can delete a whole skill; no rejected-value record | project_id on the skill read path, with disk, user and project foreign keys cascading | Python, TypeScript and CLI clients, plus Claude Code and OpenClaw packages and a sandbox | A message queue driving distillation and the skill agent, with session status through the pipeline | Task outcome is the only signal, and it gates the write rather than labelling the memory | The outcome gate the skills pattern asks for, tested; no embeddings, so memory is greppable and portable | Retrieval depends entirely on the agent choosing to look; a wrong skill file has no tombstone |
| `adk-python` | `MemoryEntry` — a `types.Content` plus optional id, author, timestamp and custom metadata; the unit written is usually a whole session's events | Interface only. Ships an in-process dict, a Vertex AI Memory Bank client and a Vertex AI RAG client; sessions additionally have SQLite and database backends | `search_memory(app_name, user_id, query)` — keyword set-intersection in the default implementation, hosted similarity search in Memory Bank | `add_session_to_memory`, `add_events_to_memory`, `add_memory`; Memory Bank generates memories from events server-side | None. The contract has no delete, no update and no expiry, and no implementation adds one | `app_name` and `user_id` are required keyword arguments on every write and on search, and travel to Memory Bank as a `scope` dict | `LoadMemoryTool` for the agent, `Runner` wiring, and a plugin surface; the memory service is chosen by the app author | Memory Bank does generation and ingestion server-side; the local implementations do none | Author and timestamp on an entry; no provenance chain, trust state or confidence anywhere | Scope keys mandatory in the signature; session and memory cleanly separated; 61 memory tests | Deletion exists on the session service and not on the memory service, so the durable half of a user's data has no removal path |
| `agent-afk` | A fact — content, one of four CHECK-constrained categories, a source surface, a confidence float, an access count, a supersedes pointer and a nullable `evidence` citation | SQLite with an FTS5 external-content index and porter tokenizer, plus a `HOT.md` working file under a token cap | `facts_fts MATCH` ranked by FTS rank, with optional category and since filters, and `superseded_by IS NULL` always appended | Three agent tools — `memory_search`, `memory_update`, `procedure_write` — writing either hot memory or the durable fact archive | `supersedeFact` sets `superseded_by` under a `WHERE superseded_by IS NULL` guard, so a double supersede is a no-op | None on the read path by design — the fact archive is deliberately cross-session | A CLI agent with a hot working file and a durable archive behind three tools | None; truncation of the hot file happens on write | A `confidence` float, and a derived `[unverified]` marker applied at render time when a codebase fact has no citation | An evidence gate that reaches the prompt text rather than being dropped before it, with a stale-citation warning on supersession and twelve committed cases | The gate is behind `AFK_MEMORY_EVIDENCE_GATE=1`, so the default build stores codebase facts with no citation and marks nothing |
| `agent-framework` | A `MemoryTopicRecord` — topic, slug, summary, a list of memory bullets, `updated_at`, and the `session_ids` that contributed to it — serialised as one Markdown file per topic | A `MemoryStore` ABC with a file-backed implementation: per-owner, per-source directory trees holding topic files, an index, state, and a transcript archive. Separate packages back Azure Cosmos DB and the hosted Foundry service | An index of one-line topic pointers injected per turn, with keyword extraction from the current messages selecting which topic files to expand | Model tools plus a consolidation pass tracked by `last_consolidated_at` and `sessions_since_consolidation` | `write_topic` and `delete_topic` on the store; consolidation rewrites a topic file into a tighter form. No record of a deleted or rejected value | The owner id is read from session state and **required** — a missing one raises, `..` and absolute paths raise, and the resolved root is asserted to be inside the base path | A `ContextProvider` contract of `before_run`/`after_run` plus a `source_id`, consumed by the Agent runtime; .NET and Python; DevUI; a hosted Foundry provider | Consolidation of a topic file via an LLM prompt, scheduled by sessions-since-last-run | None. A topic memory is a bullet list; there is no status, confidence or verification anywhere on it | Fail-closed owner scoping with a post-resolve containment assertion; `session_ids` provenance on every topic; ~1,357 lines of tests on the harness memory alone | The provider contract still declares neither deletion nor scope, so a third-party provider inherits AutoGen's gap; nothing records that a value was removed |
| `agent-memory-supabase` | One `memories` row — content, a nine-value `memory_type`, project, tags, importance 1–10, extracted entities as JSONB, a validity window, an expiry and a supersedes pointer | A single Postgres table on Supabase with pgvector HNSW, a generated `tsvector`, pg_trgm and six further indexes | Three lanes — vector, full-text and entity-grounded — fused by RRF with k=60, then blended by recency, importance and usage, with the blend switchable off for evals | Client-side embedding and entity extraction, then two dedup probes: cosine at 0.95 within the same type, and pg_trgm at 0.65 for same-template snapshots | `superseded_by` pointing at the replacement, `valid_until` closing the window, `active` for soft delete and `expires_at` as a hard TTL | A nullable `project` column applied as a filter in every function — and defaulting to NULL, which means all projects | A 257-line JavaScript `MemoryStore` class over the Supabase client; no framework binding, no MCP, no agent tools | None. Everything happens in the query | An `importance` smallint that feeds ranking, and `correction` as one of nine memory types. No status field | Real validity-versus-record time; an `updated_at` trigger that will not fire on access-stat touches; a similarity floor on the text lane with the RRF failure it prevents written into the comment | The per-user RLS policies are commented out, so the only enforced posture is server-sees-everything; 898 lines and no tests at all |
| `agentmemory` | Raw/compressed observation, versioned memory, summary, lesson, graph/semantic/procedural records | iii StateModule backed by local SQLite plus persisted search projections | BM25 + optional vector + graph arms, weighted RRF, query expansion, rerank, source diversity | Hooks call `mem::observe`; explicit `mem::remember`; optional compression and consolidation | Delete/TTL; similarity-based version supersession; rebuildable indexes | Project, session, working directory; shared or isolated agent mode | Hooks, MCP, HTTP, CLI, iii functions | Optional compression, graph extraction, consolidation, decay, repair | Source observation IDs, versions, audit; no candidate/verified/rejected state | Cheap synchronous capture and compact-first hybrid search | Very broad surface; shared scope default; fuzzy supersession can hide conflicts |
| `agno` | Six of them — a profile field, a free-text memory, a session summary, a titled learning, an entity carrying facts and events, and a decision with an outcome | One `BaseDb` behind twenty backends (Postgres, SQLite, Mongo, Redis, DynamoDB, Firestore, ClickHouse, SurrealDB, JSON, GCS); learnings in one table keyed by learning type | No embeddings anywhere on the memory path — `last_n`, `first_n`, or an `agentic` mode that sends the memory list to a model and takes back ids; entity recall matches names on word boundaries | `ALWAYS` extraction fired from a post-run hook, or `AGENTIC` tools the model calls; a `background_executor` if the app supplies one, otherwise inline on the response path | `retire_fact` stamps `superseded_at`/`superseded_by` and keeps the row; `forget` archives an entity; the curator prunes by age and count; `optimize_memories` clears the table | `user_id` required on every recall and returns `None` when absent; entity namespaces of `user`, `global`, or a custom group | Agent and Team runtime, ~20 model providers, an AgentOS FastAPI control plane with nine memory routes, MCP, and a `MemoryTools` toolkit | A post-run capture hook, a `Curator` that prunes and deduplicates the user profile only, and an LLM supersession judge on the entity write path | A `confidence` float on decision-log entries and nothing else; facts are live until something supersedes them | Supersession that is judged, thresholded, reversible and tested; scope that fails closed on read; comments that document the corruptions that produced the code | `optimize_memories` defaults to `apply=True` and replaces every memory with one model-written paragraph; PROPOSE-mode approval exists only in a prompt string |
| `ai-memory` | Markdown page in git, plus observation, handoff, and workstream records | Markdown in git as the human source of truth; SQLite as derived index and state | Authority- and tier-ranked search over pages, with a retention score | Harness lifecycle hooks capture observations; opt-in LLM consolidation into pages | Versioned supersession; generation-based supersession of pending work | Workspace and project ids with per-project UUID isolation; capability-gated actors | MCP plus lifecycle hooks for Claude Code, Codex, Cursor, Gemini, opencode, Devin, Grok, Kimi | Consolidation workers, retention/decay scoring, wiki migrations | Actor capabilities and auth levels; no candidate/verified state on a memory | A handoff with a lifecycle, carrying open questions and next steps across harnesses | No trust state or tombstone; supersession is page-keyed and re-capture is unguarded |
| `atomic-agent` | Memory, lesson, profile fact, and procedure, linked by typed edges | SQLite with versioned migrations; bi-temporal profile facts | Heuristic-gated query rewriting, links, and vote-aware ranking | Consolidator clusters; lessons and procedures from one LLM call per cluster | `supersedes`/`superseded_by` chains; deprecation retains the row | Not traced | Agent runtime with a separate reflection slot | Consolidator, reflection, neighbour evolution, vote runner | Append-only `vote_events` with derived `vote_score`; surfaced-id allowlist | Numbered invariants cited from code, and features default-off until evaluated | Large opt-in surface; evaluation campaign results not committed |
| `aukora-kernel` | A hash-chained entry — payload (actor, chainKey, seq, operation, tier, contentHash) plus plaintext that a forget erases | Two paths: a local JSONL store with an independent JSONL receipts log, and a Convex `aukora_memory` table behind a delegation-manifest pipeline | `recall` returns active entries for a chainKey in seq order, banner-marked advisory; the Convex path requires a reader proof-of-possession | Authority-gated through the same gate as every tool — locked session pauses, an apparent secret denies — then chained, receipted, fsynced | `forget` erases the plaintext, tombstones the row, keeps the hash link and appends a forget receipt; nothing blocks re-asserting the same content | `chainKey` filters every read; the Convex path binds owner, subject and resource scope and severs a revoked subject | A CLI, an IDE agent (Auma), and the Convex kernel pipeline of grant, intent, decision token and receipt | None on the memory path | Receipts, hash chain and per-entry actor; recall is advisory and can never authorize an effect | Receipt-coupled fail-closed writes; RTBF that erases plaintext without breaking the chain; limits documented inline | Forget records a rejection it never consults, so the same content can be written again; tiers are declared and never applied |
| `autogen` | `MemoryContent` — content, a MIME type and optional metadata. There is no identifier field | Interface only. Ships an in-process list plus ChromaDB, Redis, Mem0 and a text-canvas adapter | `query(query)` returning `MemoryQueryResult`; the default returns everything in chronological order | `add(MemoryContent)`, called by the application or by a task-centric memory sample; no extraction in the core | `clear()` wipes the store. There is no targeted delete in the protocol or in any shipped adapter | Absent from the protocol. Only the Mem0 adapter carries `user_id`, and it defaults to a fresh UUID | `update_context` lets memory inject itself into the model context; components are declaratively configured | None in the core; the task-centric memory samples add their own learning loops | MIME type and free-form metadata; no provenance, confidence or state | `update_context` as a first-class injection point; a small protocol that is genuinely easy to implement | No identity on a memory, so targeted deletion is not expressible; scope is an adapter's option, not the contract's |
| `basic-memory` | Canonical Markdown note; indexed entity, observation, relation | Filesystem source + SQLite/PostgreSQL projection | FTS5/tsvector, optional semantic chunks, hybrid score fusion, graph context | MCP/API writes accepted Markdown; file watcher reconciles human edits | Distinct create/replace/edit/move/delete with stable ID and reindex | Project, workspace, tenant, local/cloud route | MCP tools, typed clients, API, CLI | Watcher, startup reconciliation, indexing workflows | Human-visible source/checksums; no candidate/verified state | Inspectable portable memory with rebuildable indexes | Bidirectional sync complexity; agent can write unsupported claims |
| `buzz` | An engram — a `kind:30174` Nostr event whose NIP-44 ciphertext decodes to `{slug, value}`, or `{slug: core, profile}` for the identity surface | A Nostr relay the operator runs; engrams are parameterized-replaceable events keyed by (pubkey, kind, d_tag), so the relay holds only the head | No search. `core` is fetched and injected; everything else is reached by following `[[slug]]` references or asking for a slug by name | Synchronous — build body, encrypt, sign, publish. `mem set` replaces; `mem patch` applies a unified diff under a sha256 compare-and-swap | Last-writer-wins head selection with monotonic `created_at` and event-id tiebreak; `mem rm` publishes a `value:null` tombstone, barred on `core` | The d-tag is `HMAC(conversation_key, slug)`, so addressing is per agent-owner pair; the relay filters by (pubkey, kind, d_tag) and can correlate neither | `buzz mem` CLI, ACP prompt injection of the core section, a read-only desktop viewer, and an MCP dev server | None for memory — no extraction, no consolidation, no embedding, no scheduled pass | Signatures and encryption, and nothing epistemic — no confidence, no candidate state, no provenance on a value | The relay cannot read content or correlate slugs; compare-and-swap on a memory value; a careful distinction between confirmed-absent and unknown | Replaceable events discard prior versions, so there is no history and a tombstone records only that something is gone, not what was rejected |
| `byterover` | Flat memory with source/pinned metadata; structured knowledge `ContextData` | Local Markdown under `.byterover/`, optional cloud sync | Metadata filter and pagination only in inspected modules | LLM dedup returning CREATE/MERGE/SKIP; `DECISIONS` always creates | Structural-loss guard repairs destructive curation; no tombstones | Storage directory only | `brv` CLI, MCP, Hermes provider | LLM dedup at bounded concurrency | `source` of agent/system/user recorded but not enforced | Deterministic structural-loss detection and repair on LLM rewrites | Elastic License 2.0, not open source; merge path itself is unguarded |
| `camel` | A `MemoryRecord` — a chat message plus its backend role, a UUID, a timestamp, an `extra_info` dict and an `agent_id`. Nothing is derived from the transcript | Key-value backends for chat history (in-memory, JSON file, Redis, Mem0 cloud) and a vector backend for recall (Qdrant by default) | Chat history returns the stored list, optionally windowed; the vector block embeds the last user message and takes the top `k` by similarity with no filter | `write_records` on every turn — no extraction, no summarisation, no consolidation. The transcript is the memory | `pop_records(count)` and `remove_records_by_indices(indices)` on chat history; both raise `NotImplementedError` on the vector store, where `clear()` is the only removal | `agent_id` is stored on every record and serialised both ways, and is applied on no read path. Isolation comes from giving each agent its own storage object | `AgentMemory` ABC consumed by `ChatAgent`; a `MemoryToolkit` for save/load; role-playing and workforce runtimes on top | None | None. A record is a message that was sent; there is no status, confidence, source or provenance beyond the backend role | A small, legible three-part contract — block, memory, context creator — that a custom store can satisfy in an afternoon | A stored-and-unused scope key, a vector store that cannot delete one record, and a retrieval query that is whatever the last user message happened to say |
| `claude-mem` | Hook event, pending message, observation, session summary, prompt | Canonical SQLite, optional Chroma projection and cloud sync | FTS/filter search or Chroma semantic search; file-only metadata/semantic intersection; recent timeline context | Lifecycle hooks queue work; observer generates structured XML; SQLite commit before acknowledgement | Exact row deletion with synchronized tombstones; project-wide server forget paths | Project/worktree, session, platform source; team/server scope emerging | Coding-agent hooks, HTTP, MCP, UI, multiple adapters | Durable queue, provider retries, vector/cloud projection, repair | Session/tool metadata and deterministic file evidence; generated claims have no trust state | Reliable non-blocking capture and bounded cross-session context | Ordinary search is not fused hybrid; generated observations activate automatically; dual schema transition |
| `cognee` | Source data, chunk, typed `DataPoint`, graph edge, summary, session entry | SQLite/PostgreSQL plus pluggable graph/vector stores | Chunk, lexical, vector, graph, triplet, summary, temporal, hybrid, and routed modes | `add` + `cognify`; unified `remember`; session-hot writes with background improvement | Exact data/dataset/all forget; memory-only reprocessing; provenance rollback | User permissions and dataset; optional per-user/dataset backend isolation | Python, REST, CLI, MCP, typed memory entries | Composable pipelines, session bridge, memify, rollback/recovery | Source records, content hashes, pipeline/task/user provenance; no factual trust state | Ontology-aware multimodal graph pipeline with serious rollback | Large configuration surface; cross-store consistency; extracted graph can harden errors |
| `core-memory` | Bead (typed record) plus Claim (subject/slot/value) with claim updates | Session JSONL as live authority, rebuildable index projection; Qdrant, Kuzu, Neo4j, SQLite backends | Typed pipeline over archive/graph/projection; lexical, semantic, entity, causal; myelinated edges | Turn capture into beads; claim extraction; connector ingest with per-source grounding | Supersession chains, `retracted`, tombstone_bead, reject; every governance action requires a reason | `scope` on every bead; session/project surfaces with a documented truth hierarchy | Python API, HTTP server, MCP, PydanticAI tools, OpenClaw bridge, CrewAI, Spring AI | Dreamer proposes candidates for human decision; association passes; promotion; compaction | `grounding` gates `confidence_class` C/B/A; `authority`; approval workflow with rejecter and reason | Grounding caps the trust ladder, so a speculative memory cannot be promoted by use | Very large surface; supersession is record-keyed, so re-derivation is not blocked |
| `cortex` | An episodic row (session, summary, topics, entities, importance, sensitivity) or a semantic row (content, summary, category, tags, importance, sensitivity) | libSQL/SQLite with FTS, embeddings stored as blobs, and an optional mirrored vector backend | Vector plus lexical over episodic and semantic, tier-filtered, with an optional `AND em.session_id = ?` predicate and a graph traversal beside it | Regex heuristics assign category and tags with no model call; a classifier assigns a sensitivity level; the vector store is mirrored best-effort | Consolidation and a delete path into both the row store and the vector records | `session_id` applied as a SQL predicate when supplied, on the episodic tier; `shared_context` is namespaced and versioned for deliberate cross-agent sharing | A Deno agent runtime with a memory_search tool, a supervisor decision path and a human approval gate | Consolidation, a preference learner, and a weekly benchmark workflow in CI | A four-level sensitivity classification — public, normal, sensitive, secret — computed at write and recomputed at read | A read gate that can refuse: a secret-classified hit needs a supervisor decision and then a human yes, and denial returns an error rather than a redaction | A complete `MemoryPrivacyPolicy` with allowed tiers, PII redaction and retention lives in a process-local Map and is consulted by nothing |
| `cosmonapse` | An entry, shape left to the backend; `Hit` and `RecallResult` on the way out, `ImprintReceipt` on the way in | An `Engram` ABC with three shipped backends — a dict, stdlib `sqlite3`, and asyncpg Postgres | `recall()` with a deadline, preceded by `can_serve(query)` — a hosting Dendrite skips responding when a backend says it cannot answer | `imprint(op, entry, merge_key=..., trace_id=...)` returning a receipt, with each write journaling its inverse against the trace | `compensate(trace_id)` replays journaled inverses LIFO; `commit(trace_id)` discards the journal. No delete on the contract itself | None in the contract. `namespace` appears only as advice about hosting more than one Engram | An event-driven A2A protocol — agents as functions on a bus — with Python and TypeScript SDKs, a CLI, and in-memory, TCP, NATS and Kafka transports | None on the memory path | None. No status, confidence or provenance on an entry | A contract that models refusal, overload, deadlines and rollback — the only memory interface here with a failure vocabulary | The saga journal is an in-process dict, so a worker that dies mid-workflow leaves provisional writes permanent and unmarked |
| `cowagent` | Markdown files, chunked into an indexed `chunks` table | SQLite with embeddings and self-healing FTS5 | Vector plus keyword over chunks; `MEMORY.md` injected in full | Summarize into dated daily files, then distil | Recency-wins conflict update; whole-file overwrite | `user_id` and `scope`, defaulting to `shared` | Agent memory tools | Deep Dream after the daily summary, 23:55 cron | Line-addressable chunks with hashes; dream diary | Dated intermediate layer and written distillation rules | Shared-by-default scope; chained lossy summarization |
| `crewai` | A `MemoryRecord` — content, a hierarchical `scope` path, categories, metadata, an `importance` float, `created_at`, `last_accessed`, a `source`, and a `private` flag | LanceDB by default, Qdrant Edge as an alternative, behind a `backend.py` contract; a separate SQLite store for kickoff task outputs | A recall Flow — sub-queries embedded in parallel, searched across candidate scopes concurrently, oversampled 2×, then composite-scored on semantic, recency and importance with `match_reasons` attached | An encoding Flow — batch embed, intra-batch cosine dedup, parallel find-similar, parallel LLM analysis producing a consolidation plan, then bulk execute | `forget()` deletes by scope, category, age, metadata filter or explicit ids; `update()` rewrites in place; the consolidation plan lets the model delete existing records on write | A path prefix — `/company/engineering/alice` — applied as `scope_prefix` on every search, plus a `private` flag filtered against the requesting `source` | `Memory`, `MemoryScope` and `MemorySlice` as views; agent tools; an event bus; a read-only Textual TUI in the CLI | None scheduled; consolidation happens inline on the write path | An `importance` float from 0.0 to 1.0 that feeds ranking. No status, no verification, no provenance beyond `source` | Scope as a hierarchical path with subscope views and a committed test that a rooted view cannot recall a sibling's records; recall that reports what it looked for and did not find | An LLM on the write path is authorised to delete existing records, with no tombstone, no audit and no human in the loop |
| `ctx` | Markdown entry staged, then digested into a themed region of a root document | Files in the project tree; a dream ledger and journal alongside | Progressive disclosure — roots, themes, regions read by any tool that can read files | Staged entries; `dream` proposes, a schema gate validates, apply writes within a guarded scope | Proposal dispositions including promote; region folding; no value-level tombstone | Write scope enforced by path — dreams/ and ideas/, with specs/ only on promote | CLI, MCP, VS Code extension, skills; any tool that can read files | `dream` scan, propose, validate, apply, with a ledger and resume | Provenance required on proposals; invalid proposals rejected rather than admitted | A write-scope guard on consolidation, and a corruption regression corpus from the literature | Correction is region folding; nothing records that a digested claim was wrong |
| `daimon` | Trust-classed checkpoint item: open question, decision, belief, uncertainty | Per-project JSON checkpoints plus a disposable SQLite FTS5 index | Automatic session-start injection; FTS5/BM25 for `recall`, ranked by importance x decay | Detached LLM extraction at session end, then deterministic quote and outcome gates | Append-only events; `forget` writes a content-hashed tombstone that deletes index rows | Per-project bucket applied on the read path; cross-project reads only by explicit slug | Host hooks (Claude Code plugin, Windsurf, Codex), CLI, read-only stdio MCP | Detached serialize child, retry ledger with self-heal, index rebuild | verbatim vs inferred as a stored field, verified by code against the transcript | The model's trust claims are checked by code, not believed | One live checkpoint per project; tombstone keyed on exact text |
| `ecc` | A Markdown file with validated frontmatter — id, title, kind, scope, trust, status, sourceHarness, targetHarnesses, tags, links, timestamps, body | One `${id}.md` per memory under a per-scope vault root, with a trusted-boundary assertion on every read | Index and lexical search over the vault, filtered to `status === 'active'`, with scope selecting the root | Create-only through the `ecc memory` CLI or the `memory_save` MCP tool; every write sets `trust: unreviewed` and `status: active` | Neither. Writes are create-only, and no code path sets `rejected` or `superseded` | `project \| team \| user`, each a separate vault root with a configured boundary policy asserted on read | A CLI, an MCP server, and harness skills for Claude Code, Codex, OpenCode and Cursor, plus session hooks | Session hooks that persist memory at lifecycle boundaries | `trust` is an enum of exactly one value, `unreviewed`, and the design says so — verified knowledge is promoted out of the vault, not within it | Says in the schema that its memory is never authoritative; harness routing on every record | The read path filters a status the write path cannot produce, so rejection is reachable only by hand-editing frontmatter |
| `elastic-atlas` | Document in one of three indices: episodic event, semantic fact, procedural playbook | Elasticsearch — `atlas_memory_episodic`, `atlas_memory_semantic`, `atlas_memory_procedural` | RRF retriever fusing BM25 with a semantic query over auto-embedded fields | Agent writes on every turn; auto-embedding via `semantic_text` inference, no client-side calls | Consolidation dedupes episodic into semantic and updates playbooks; no tombstone | `user_id` per persona, applied on recall | Backend service plus an MCP server for Claude Code, Claude Desktop, Cursor | Consolidation — one model pass distils episodic events into semantic facts and playbooks | Provenance by index and source event; no trust state on a fact | A committed recall eval computing Recall@k and MRR, plus a stress test | A research demo by its own description; consolidation is a single model pass with no gate |
| `engram` | Observation and prompt records | Local SQLite WAL, FTS5 | FTS5, topic-key lookup, context assembly | MCP `mem_save`, conflict candidate flow, dedupe/update rules | Topic-key updates, duplicate counts, soft delete/sync mutation | Project, scope, session, topic key | MCP tools for coding agents | Sync queue, local conflict workflows | Source/session/project metadata, explicit judgment path | Simple durable local design, inspectable code | Lexical retrieval limits; conflict UX depends on agent behavior |
| `everos` | Markdown on disk as the source, deriving episodes, atomic facts, agent cases and agent skills as typed rows | Markdown files as canonical, with SQLite and LanceDB indexes rebuilt from them | Keyword and dense search over LanceDB with a shared filter compile path for /search and /get, plus a case-to-skill bridge | A watcher-scanner-worker cascade over the Markdown root, with one handler per derived type | A `deprecated_by` column marks superseded episodes and atomic facts and is excluded on read; document deletion exists at the service layer | Four keys — owner_id, owner_type, app_id, project_id — pinned into the base filter of every read | A Python library, a service with /search and /get, and a `cascade sync` CLI | The cascade: a filesystem watcher, a scanner, a worker, a reconciler and a backfill | Confidence on some derived rows and a deprecation pointer; no epistemic state and no provenance chain | Four scope keys enforced on one shared compile path, tested end to end; Markdown canonical with rebuildable indexes | Supersession is excluded from reads but recorded on the row, not the value, so re-derivation is unguarded |
| `generative-agents` | `ConceptNode` typed event, thought, or chat with poignancy | Per-persona JSON plus in-memory embedding dict | Normalized recency + relevance + importance, hand-tuned `gw = [0.5, 3, 2]` | Perception, conversation, and reflection all write ungated | None; observations are never deleted or overwritten | One persona directory | Simulation only; tightly coupled to `Persona` | Reflection fired by accumulated poignancy | Reflections cite supporting nodes, but citations are never used | Consolidation triggered by significance rather than a timer | Derived thoughts share one pool with observations; positional not temporal decay |
| `genericagent` | Text and Markdown across four layers | `global_mem_insight.txt`, `global_mem.txt`, `memory/`, `L4_raw_sessions/` | Agent reads a ≤30-line index and opens files by pointer | Only successful tool-call results may be written (by policy) | Layer migration and patching; "better not to modify at all" | One global tree | Internal to the framework | 12-hour L4 archive cron | Verification is a stated precondition, but no record is kept | "No Execution, No Memory" plus an ROI test for permanent context | Every axiom is prose with no enforcement or audit |
| `gini-agent` | `memory_units` with network, status, confidence, bi-temporal occurrence | SQLite (`memory_banks`, `entities`, `entity_mentions`, `memory_links`) | Four channels — semantic, BM25, graph spreading activation, temporal — fused by RRF then reranked | `retain.ts`; `proposed` status as a candidate tier | `rejected` and `conflicted` states, `archived`, supersession | `agent_id` enforced across every channel and the HTTP API | CLI, HTTP, web UI | `reflect.ts` consolidation, `reinforce.ts` | Per-unit `embedding_model`, source task and session ids | Bi-temporal columns and a rejected/conflicted trust model, with decisions kept as ADRs | Conflict state has no visible resolution workflow; no value tombstone |
| `gitlord` | A turn — user, assistant or tool call — committed as JSON on a branch, addressed by commit sha and path | A git repository. Sessions are branches; the commit graph is the durable record | A `ContextAssembler` over the turn history with a dedup index and a per-branch context cache, plus a RAG module | `append_turn` and its typed variants commit; `_commit_turn` can rebuild a chain onto a new parent | Git's own semantics — a rewritten chain is a new set of commits, and the old objects remain until they are collected | A branch per session; nothing composes a scope key into a retrieval predicate | A CLI, an MCP server, and a LiteLLM-backed model layer with a tool-schema translator | None | None. A turn is what happened; there is no claim, status or confidence anywhere | A durable log that is inspectable, forkable and replayable by construction, with the derived index rebuildable from it | It stores what was said rather than what is believed, so nothing distinguishes a fact from a correction of it |
| `gobii` | A row in a table the agent invented. There is no framework-defined memory record — the schema is whatever the model wrote `CREATE TABLE` for | One zstd-compressed SQLite file per agent in Django's `default_storage`, restored per run through a validating subprocess; Postgres holds the platform's own 183 models | SQL. The agent is shown a generated schema prompt capped at 30,000 bytes and 25 tables, then writes queries against it | SQL, through a batch tool with autocorrect, query-quality checks and recovery; the file is validated and re-uploaded after the cycle | `UPDATE` and `DELETE FROM`, written by the model. No framework-level correction, no record of what was removed | One database file per agent UUID, with `ATTACH`/`DETACH` denied by a `sqlite3` authorizer so SQL cannot reach another agent's file; Django models are foreign-keyed to the agent | A Django platform — persistent agents with email, SMS, Discord and web endpoints, MCP servers, schedules, a browser-use agent, skills and a kanban plan | Celery. Comms and step snapshot chains summarise history incrementally, each linked to its predecessor with an inclusive cut-off | None. A row is true because the model inserted it; there is no status, confidence or provenance column unless the model invented one | An explicit persistence contract — eight built-in tables declared ephemeral and dropped before save, with each one's mortality stated in the prompt the model reads; a real SQL authorizer sandbox | The schema is model-authored, so nobody can write a query to correct or erase a subject without first discovering what tables exist |
| `goodai-ltm` | A chunk of text addressed by a `text_key` returned at insert, with optional metadata and a timestamp | In-process chunk queue over a simple vector database, serialised whole through `state_as_text` / `set_state` | Embedding retrieval with a pluggable reranker — embedding, cross-encoder or a probabilistic matching model — plus optional LLM query rewriting | `add_text` with optional LLM rewriting; chunking is queue-based with section separators bounding chunk expansion | `replace_text` and `delete_text` by key, both abstract on the base interface — the complete lifecycle, keyed | None. No user, session, project or tenant concept anywhere | A Python library plus example LTM agents; no MCP, no server, no framework binding | None | Metadata and timestamps; no provenance, confidence or state | Targeted update and delete on the interface itself; a trainable reranker; a companion benchmark suite | Dormant since February 2024; whole-state serialisation; no scope key of any kind |
| `graphiti` | Episode, entity, temporal relationship edge, community/saga | Neo4j, FalkorDB, Kuzu, Neptune | BM25 + cosine + BFS across edges/nodes/episodes/communities; RRF/MMR/cross-encoder | Episode ingestion, entity/edge extraction, resolution, temporal invalidation | Close `valid_at` intervals, expire edges, remove episodes | `group_id`, entity/edge types | Python library, MCP, server | Ingestion maintenance; saga summaries | Source episode UUIDs and bi-temporal history; no verified state | Preserves changing facts without erasing history | Entity merge/invalidation mistakes reshape the graph |
| `helm` | A `(kind, key)` fact carrying confidence, evidence_count, access_count and an expiry, plus a free-text episode | One local SQLite file via `node:sqlite`, vectors as JSON text in side tables; a separate Markdown vault the agent edits by prompt | BM25 fused with MiniLM cosine by RRF, scaled by confidence and a key-match boost, over the 500 most recently updated active facts | One CLI verb per fact, a regex on the hot path, and a 15-minute think tick plus a weekly LLM pass for the rest | A same-key rewrite expires the old row and inserts a new one; `forget` and the prune sweep hard-delete | None on the fact table — one owner, enforced at the gateway; `channel` is stored on episodes but never filtered on | Discord, iMessage and a terminal client into one Claude Code session; two registry tools; a generated index imported into the prompt | A launchd/systemd think tick, a weekly deep review, consolidation with decay and prune, and index regeneration | A confidence float with a 0.7 cap on a first observation that rises only on independent repeats | The evidence gate, decay slowed by access, and episode-noise gates anchored by tests that name the pollution that forced them | Confidence never reaches the model, three readers ignore the expiry predicate, and the 500-row recall window is ordered by recency |
| `hermes-agent` | Delimited text entry in `MEMORY.md` / `USER.md`; session message; skill | Markdown files plus SQLite `state.db` with FTS5 | Curated memory always in prompt; session history via FTS5; no cross-layer fusion | Explicit `memory` tool through a staged write-approval gate | Substring-addressed replace/remove; hard char cap forces in-turn consolidation | Profile-level only; no project or room boundary within a profile | Own tools plus one mounted `MemoryProvider`; MCP serve | None for curated memory; providers may run their own | Threat-scanned at write; no provenance on entries | Frozen prompt snapshot preserves cache; foreign-write detection with backup | Model writes are instantly authoritative; unlogged budget-driven eviction |
| `hindsight` | Source chunk, world/experience fact, observation, reflection | PostgreSQL/pgvector or Oracle | Semantic + BM25 + graph + temporal, RRF/interleave, cross-encoder rerank | Screen, chunk, extract, embed, link, consolidate | Replace/append source; observation create/update/history; exact bank/document operations | Memory bank, tags, schemas/tenants | REST, MCP, generated SDKs, framework integrations | Queued consolidation and maintenance with retries | Source IDs, proof counts, audit/LLM traces; no explicit truth state | Complete service pipeline; task-specific fusion; temporal recall | LLM facts/observations can harden errors; operational complexity |
| `hipporag` | Chunk plus derived entity and passage graph nodes | igraph graph with pluggable vector store (Qdrant/Chroma/Milvus) | Fact scores → LLM rerank → IDF-penalized graph seeding → Personalized PageRank diffusion | `index()`: chunk, OpenIE triples, fact/passage/synonymy edges | Chunk-scoped delete; shared entities survive by reference count | None — corpus is global | Python library only; no MCP, tools, or service | Cacheable OpenIE; incremental synonymy edges | Chunk identity only; no actor, time, or trust state | Diffusion replaces hop planning; synonymy as edges rather than merges | Assertion instead of fallback on unlinked queries; undirected diffusion discards predicate direction |
| `holographic` | Flat fact row plus HRR phase vector and linked entities | Local SQLite (WAL) with FTS5 and per-category bundled banks | FTS5 + Jaccard + HRR cosine, multiplied by trust; algebraic `probe`/`related`/`reason` | `fact_store` tool, mirrored host writes, optional end-of-session regex extraction | Exact update/remove; feedback shifts trust; no supersession | Category only; no user/project/session scope | Hermes `MemoryProvider` plugin; `fact_store` and `fact_feedback` tools | None; bank rebuild is synchronous on every write | None — no source, actor, or session on a fact | Deterministic hash-derived vectors; `contradict` as a query action | Three downvotes silently drop a fact below the retrieval floor; one score for truth and reachability |
| `honcho` | Message, document/observation, representation | Postgres/SQLAlchemy, pgvector or vector adapter | Working representation blends semantic, recent, most-derived; message search with windows | Message ingestion plus queued derivation | Soft delete, representation reconciliation | Workspace, peer, session, collection | Hosted API/service model | Deriver queues and workers | Source IDs, derived observations, peer/session provenance | Strong event-to-representation pipeline | Operational complexity; LLM-derived observations still need trust policy |
| `juggler` | One dated bullet — `- [YYYY-MM-DD] one fact` — in a flat list under a single heading, order preserved as written | `<project>/.juggler/MEMORY.md`, a plain Markdown file, git-ignored so it never leaves the checkout | The whole file is a context item on each conversation; there is no search, ranking or selection | One `memory` tool with two actions, `remember` and `forget`; the assistant is prompted to use it only for facts that outlive the session | `forget` removes every entry matching a case-insensitive substring; revision is forget-then-remember | One file per project checkout, per machine — partition rather than a filter | A context item in the Juggler UI, plus a seeded system prompt; every write appears in the conversation transcript | None | None. A bullet is a fact because the assistant wrote it or the user left it there | A canonical format the writer re-tidies, a per-fact delete control in the UI, and 43 committed test cases against 772 lines of implementation | `forget` matches by substring, so one careless match string removes more than it names, and nothing records what it removed |
| `langmem` | Store item, usually JSON memory | LangGraph `BaseStore` | `store.search/asearch` delegated to backend | Tools call create/update/delete/search; extraction via Trustcall | Tool-level CRUD | Namespace templates | LangChain/LangGraph tools | Reflection executor local/remote | Mostly application-defined | Clean primitives, schema-driven extraction | Too low-level to solve memory quality alone |
| `lethe` | A row with text and a `depth ∈ ℝ` — 1.0 just inscribed, (0,1) sinking, 0 submerged but present, above 1 pinned | SQLite with three synced tables — the row store, a `vec0` vector index, and a non-contentless FTS5 index so DELETE reaches it | Hybrid vector and BM25 fused by RRF, with `lexical=True` for identifier lookup and `at=T` reconstructing depth from the event log | `inscribe`, then control-plane verbs — `surrender`, supersede, edit, `pin`, `consolidate` | `release` sets depth to 0 — present but unreachable; `purge` deletes from all three indexes; `purge_with_receipt` signs the result | None. One store, no user, agent or tenant key anywhere | A CLI, an MCP server, and a six-adapter benchmark harness that runs the same control-plane contract against other systems | Gravity — depth decays over time — plus consolidation | No states. Every status collapses into one continuous `depth`, which is a float and not an epistemic field | Purge that reaches the lexical and vector substrates by construction, an Ed25519 receipt over a Merkle root of the event log, and a benchmark whose author's own system places third | A purged text can be inscribed again — the receipt records its hash for verification and no write path consults it |
| `letta` | Core memory block, archival passage, message | ORM database; passages with embeddings; optional git memory | Archival search, conversation search, compiled core prompt | Agent tools mutate core/archival memory | Append/replace/patch, passage insert, block update | Agent, block labels, files/sources | Deep runtime tool executor integration | Prompt rebuilds, manager services | Block tags/metadata, message timestamps; limited truth model | Clear core/archive/recall separation | Agent can rewrite important memory without strong verification |
| `livingfeed` | A consolidated episode — a summary under 500 characters, an importance float, the four factors that produced it, mandatory `source_event_ids`, and tags | Three layers — Redis lists for working memory, the event store as the permanent episodic original, Qdrant for the semantic index | Vector search per world collection, filtered on `actor_id`, an importance floor, and `decay_at > now` | Consolidation at tick end folds the tick's interventions, responses, emotions and actions into one episode; summaries are template-first with LLM reserved for high importance | Nothing is updated. Semantic points carry `decay_at` and fall out of recall; the episodic original is never deleted | A Qdrant collection per `world_id`, plus a `must` filter on `actor_id` inside every search | An actor engine with tick, director, emotion, goal and relationship services over a shared event store | The tick loop. Consolidation runs at tick end; reflection is a separate module | An importance float composed from emotion, relationship, goal and rarity — with the components stored, not just the total | Storing the importance factors so the coefficients can be tuned offline by replay; forgetting that expires the derived index and keeps the source; deterministic embeddings so CI does real similarity search | A recall failure is caught and returned as an empty list, so an actor with an unreachable index is simply amnesiac and nothing upstream is told |
| `llamaindex` | Block-owned content; no memory record | Application-chosen; vector store via the framework's abstractions | Per-block: vector retrieval, extracted facts, static text — composed, not fused | Short-term history overflow flushes `token_flush_size` into blocks | Condensation rewrites the fact list wholesale; no tombstone | None; application-owned | LlamaIndex agents and workflows; custom blocks via `BaseMemoryBlock` | None; extraction runs on flush | None — extracted facts record no source | Self-truncating blocks and one explicit budget split | No provenance, correction, or scope; capture depends on conversation length |
| `llm-wiki-memory` | Typed Markdown atom, plan/investigation, daily capture, or full document | Filesystem wiki, per-category embedding caches, private git history | Metadata prefilter, local embedding/chunk cosine, priority bands, federated locality boost; lexical vector fallback | MCP/CLI writes, transcript and plan hooks, daily compile, full-document absorb | Upsert/relocate, archive/re-enable, exact delete, supersedes, opt-in dedup/refresh consolidation | Private brain plus explicit repository wiki levels; workspace/area/task/subject facets | MCP, CLI, Claude Code lifecycle hooks, shared instructions | Detached flush, daily compile, opt-in consolidation, cron healing, git/cache maintenance | Body hash, capture audit, git history, user-gated lessons; no candidate/verified/rejected state | Recoverable capture, explicit targets, deterministic layout/topology, excellent operational tests | LLM atoms become active without verification; vector-only primary retrieval; linear scans; git is not erasure |
| `logseq` | An outliner block or page in a DataScript graph, typed by user-defined tags (classes) and properties with declared types and cardinality | DataScript over SQLite, local-first; FTS5 trigram index and a 384-dimension vector index alongside; optional multi-device sync | Four lexical arms — exact title, FTS5 match, LIKE, fuzzy — plus optional local vector search, fused by RRF with early exit when cheap arms suffice | Synchronous and literal. A human types, or an agent calls upsertNodes with add/edit operations; no extraction, no LLM in the write path | `:db/retractEntity` hard retraction with orphaned-page cleanup; agents cannot delete at all — no delete tool exists | A graph is a separate database; there is no principal, tenant or agent key inside one | MCP server over the desktop API with six tools, an HTTP API server, and the editor itself | Embedding upserts in batches of 1024 and index maintenance; nothing derives or consolidates memory | None. A `created-by-ref` property exists in the schema and the agent write path never sets it | A schema the user defines and the agent must obey; genuinely local hybrid retrieval; the best editing surface in the atlas | Agent writes land live, unmarked and indistinguishable from the user's own; hard retraction with no history |
| `loongflow` | Message in graded tiers; `Solution` with score and timestamp in the evolving population | In-memory or Redis for the population; pluggable storage for graded tiers | Graded tiers by recency; population by Boltzmann selection with adaptive temperature | Messages flow through stm to mtm to ltm via a compressor; solutions appended with a score | Compression across tiers; population turnover by selection pressure | Not traced | LoongFlow agent SDK | Auto-compression between tiers | Score on each solution; no trust state on messages | The only stochastic recall in the atlas, with temperature driven by measured diversity | Two unrelated memory models under one package; the graded stack is conventional |
| `magic-context` | Memory with separate lifecycle and verification state, plus compartments, facts, primers | SQLite (70 migrations) with FTS5, embeddings keyed by `(memory_id, model_id)`, git commits indexed | Hybrid semantic + BM25 with source boosts and `matchType`, over memories and raw history | Agent, user, historian, or dreamer writes; synchronous promotion, async embedding | Supersession and merge lineage; archived, not tombstoned | `project` / `ecosystem` / `universe` lattice plus a `shareable` flag | Pi `ExtensionAPI` and an OpenCode adapter sharing one store | Dreamer: verify, map, classify, promote, retrospective, at commit boundaries | Four-actor `sourceType`, mutation logs, per-memory `verified_at` | Memories re-verified against the files they describe when git says those files changed | Verdict is an LLM call; no rejected-value tombstone; very large surface |
| `mastra-observational-memory` | Raw message, dated observation group, reflected observation context | Mastra `MemoryStorage` adapters | Sequential active observations + recent raw tail; optional observation-vector retrieval | Processor observes at token thresholds; reflector compacts observations | Range replacement, buffered activation, clear/clone records | Thread or resource | Deep Mastra input/output processor integration | Early async observation/reflection buffers with activation | Exact covered ranges and markers; summary has no truth state | Non-blocking context compaction for long sessions | Distributed locking and progressive summary drift |
| `mateclaw` | Fact, recall record, workspace file, and dream report | Relational repositories with fact projections | Provider `prefetch`, fact projection, and search package | Turn lifecycle events drive `syncTurn` across registered providers | Contradiction detection over facts; archive package; no tombstone found | `MemoryScope` string column with TEAM and GLOBAL shared; `MemoryOwnerResolver` | `MemoryProvider` SPI with decorators; tool beans; Vue memory UI | Scheduler, dream reports, nudge service | Contradiction detector; owner key carried through the provider contract | A provider contract that carries scope, and retry/metrics as decorators | No deletion hook on the SPI; contradiction handling is detection only |
| `mem0` | Text fact in vector payload | Vector store plus SQLite history/messages | Semantic, optional keyword/BM25, entity boost, optional rerank | LLM additive extraction, hash dedupe, entity linking | Explicit update/delete APIs; V3 default append-oriented | `user_id`, `agent_id`, `run_id`, filters | Python SDK, tool/API style | Extraction and linking on write | Attribution metadata, history; weak epistemic trust | Practical SDK, pluggable stores, hybrid search | LLM facts can become durable claims without verification |
| `mem0sharp` | A row with text, `user_id`, `agent_id`, `run_id`, a `scope`, metadata, an embedding, timestamps, an expiry and a content hash | Postgres with pgvector as the real backend, plus an in-memory store; a separate relationship store for the graph | Cosine nearest-neighbour over the embedding with the scope predicate applied, ordered by distance and capped by top-k; an optional LLM reranker | LLM extraction into candidate memories, then an LLM conflict resolver deciding what happens to existing rows, with a hash column for dedup | Delete by id and delete by scope predicate; every mutation writes a history row carrying the old and the new text | `user_id text NOT NULL` plus optional `agent_id`, `run_id` and `scope`, composed into a `WHERE` clause on every read | A .NET library with an MCP server, a telemetry decorator, and clean Application/Infrastructure/Intelligence layering | None | None on the row. Conflict resolution is an LLM decision taken at write time and not recorded as a state | An append-only `_history` table storing old and new text per event, and a required user scope in the schema rather than in a convention | 2,333 lines reimplementing a design whose extraction and conflict-resolution quality are the whole product, with no evaluation of either |
| `memanto` | Typed memory with title, content, confidence, tags, and session linkage | Moorcheh vector service, hosted or on-prem; conflict reports as dated JSON on disk | Vector search with filters, confidence, and an `as_of_date` read | Direct store, batch write, and LLM extraction from conversation | Update and delete APIs; conflicts resolved by keep_old, keep_new, keep_both, remove_both, or manual | `agent_id` throughout the API surface; per-agent conflict reports | FastAPI service, CLI, web UI, MCP, plus LangGraph, CrewAI, Claude Code and Hermes integrations | Scheduled daily analysis producing an AI summary and a dated conflict report | Per-memory confidence; typed conflicts with old/new ids and a recommendation | A conflict workflow that ends in a resolution, including `keep_both` and human-authored `manual` | Detection is one unvalidated LLM pass; resolution does not tombstone what it removes |
| `memary` | An entity mention with a timestamp, and an entity with a cumulative mention count; graph triplets underneath | Neo4j or FalkorDB for the graph, plus two flat JSON files for the streams | LlamaIndex KnowledgeGraphRAGRetriever, with a count-ranked entity list injected alongside | Chat turns append entity mentions; graph triplets are extracted from the agent's own web-search output | Age-based truncation and index-based removal on the JSON lists; nothing deletes from the graph | None in the read path; FalkorDB deployments get a per-user database, Neo4j deployments get one shared graph | A Python `ChatAgent` class with a tool registry, plus a Streamlit app | None | Mention count stands in for confidence; external search results enter the graph unverified | The smallest legible instance of reinforcement-by-frequency, and an honest single-file store | `_select_top_entities` sorts ascending, so the least-mentioned entities are the ones injected; the graph has no delete path |
| `memmachine` | Raw `Episode` (a conversation message) plus derived `SemanticFeature` — category, tag, feature name, value — carrying citations back to episode IDs | Episodes in SQLAlchemy (SQLite or Postgres); semantic features in Neo4j or Postgres/pgvector; vectors in sqlite-vec, Qdrant, Milvus or in-process hnswlib | Parallel episodic and semantic search, optionally orchestrated by a retrieval agent that reranks and dedupes long-term hits | Raw episode committed synchronously; semantic extraction deferred to a background loop polling every 2s in batches of five per set | LLM emits add/delete commands; features hard-delete; episode deletion cascades to semantic history; no rejected-value record | org_id, project_id and session_key threaded through the read path, with org-level set types bypassing project_id | REST API v2, MCP over stdio and HTTP, Python and TypeScript clients, OpenClaw integration | Ingestion loop with backoff, consolidation above a 20-feature threshold, and a queued session-deletion worker | Citations from every feature to the episodes that produced it, resolvable because episodes are retained; no candidate/verified/rejected state | Provenance that actually resolves; a fast and stated write lag; reserved-key impersonation guard; ~1,978 test functions | Deletion is acknowledged before it happens; a duplicated method silently drops error handling on the delete path; consolidation dilutes citations |
| `memobase` | A free-text memo of at most five sentences, keyed by topic and subtopic, plus tagged events and their embedded gists | Postgres with pgvector; composite (id, project_id) primary keys throughout | Profiles selected by topic preference and token budget; events by tag filter and gist embedding similarity | Buffered — blobs queue in buffer_zones until a token threshold or a one-hour flush, then one LLM extract-and-merge pass | An LLM rewrites the memo in place (APPEND / UPDATE / ABORT); no prior value is retained | project_id and user_id in every primary key, foreign key, index and read-path filter | REST API with Python, TypeScript and Go clients, an MCP server, and an OpenAI-compatible wrapper | Buffer flush, plus organize_profile when a topic exceeds max_profile_subtopics | None represented; a memo is a string, and a rewrite leaves no record of what it replaced | Scope is structurally impossible to omit; context assembly has a real token budget and a profile/event split | persistent_chat_blobs defaults to false, so the source transcript is hard-deleted after extraction |
| `memora` | Memory row with content, tags, metadata, importance, and access count | SQLite with FTS5, embeddings, crossrefs, events, actions; D1 cloud backend | FTS5 plus embeddings, ranked with age-and-access importance decay | MCP tools; documents and images ingested alongside text | Pairwise relation classification into supersession edges; superseded rows hidden from retrieval | Not traced; tags form a dotted hierarchy | MCP server, CLI, graph server | Supersession sweeps, embedding backfill, cloud sync | `memories_events` and `memories_actions` logs; `contradicts` as a relation between memories | Correction that can be rehearsed — dry_run defaults to True | No tombstone; supersession hides rather than blocks re-entry |
| `memori` | An entity fact — content, embedding, num_times, and a normalized content hash — joined to every conversation that mentioned it | Six SQL dialects plus MongoDB, from one Rust core with Python and TypeScript bindings | Embedding search and lexical search over facts, ranked with a frequency index | Durable turn first, then best-effort augmentation; extraction runs in the vendor's hosted API | Upsert increments a counter and never rewrites content; deletion is per-entity only | entity_id and process_id foreign keys applied on every read, with ON DELETE CASCADE throughout | Python, TypeScript and Rust SDKs, plus plugins for Claude Code, Hermes and OpenClaw | A Rust worker drains a write queue; augmentation is asynchronous and best-effort | None represented; num_times is a frequency counter, and no fact carries a status | Fact-to-conversation provenance as a real join table, and a capture path that survives extraction failure | The dedupe key strips all non-ASCII, so facts in non-Latin scripts collide into one row; extraction is a closed hosted service |
| `memory-engine` | Row in one `memory` table: content, name, meta, tree path, temporal range, embedding | PostgreSQL 18 — ltree, pgvector/halfvec, BM25, JSONB, tstzrange; schema per space | Hybrid BM25 plus semantic via Reciprocal Rank Fusion, computed in SQL functions | JSON-RPC create/batchCreate requiring an explicit tree; importers for git, sessions, packs | Update, delete by id or path, `deleteTree` for a subtree; onConflict error/replace/ignore | `tree_access(space, principal, ltree path, level)` evaluated inside the search SQL; agents clamped to their owner | JSON-RPC over HTTP, MCP, CLI, web UI, harness adapters for Claude, opencode, Codex, Gemini | Worker pool; embedding generation; importers | Authorization by principal and path; `authenticatedAs` recorded for observability only | Agents are principals, and the agent grant clamps to its owner so over-granting cannot escalate | No trust state or correction semantics; memory is a well-governed store, not a belief model |
| `memoryos` | QA pair in short term; topic session segment in mid term; profile string and knowledge entry in long term | JSON files by default; a separate ChromaDB variant | Embedding similarity per tier, with mid-term segments ordered by a heat score | Dialogue pairs appended; LLM segmentation into topic sessions; profile and knowledge updates | LFU eviction at capacity; bounded knowledge deques; profile merged by rewrite | `user_id` and `assistant_id` on the store | PyPI package, MCP server, ChromaDB variant, playground | Segmentation, heat recomputation, profile and knowledge updates on threshold | None found — no source, actor, or status on a memory | A committed LoCoMo harness with its dataset, and an explicit promotion signal | Heat mixes three signals with hardcoded weights; a second LFU counter can disagree with it |
| `memos` | Textual item, graph tier, preference/skill, KV cache, LoRA | Configurable vector/graph stores, dumps, cache/model artifacts | Direct vector or graph + BM25 + rerank + reasoner; optional auxiliary memories | Reader extraction into a memory cube; scheduler transformations | Module-specific update/delete/soft-delete/dump semantics | User plus registered memory cube | MOS chat/runtime, APIs, CLI | Scheduler and activation-memory refresh | Source metadata varies by module; no uniform trust state | Treats memory as heterogeneous mountable resources | Umbrella API hides uneven guarantees and maturity |
| `mempalace` | Verbatim drawer chunks, closets, KG triples | Local Chroma default; sqlite_exact, Qdrant, pgvector; SQLite KG | Direct drawer vector search, BM25 rerank, closet boost, metadata filters, FTS fallback | Mine files/convos or MCP add drawer; deterministic IDs; chunk/upsert verbatim text | Delete/update drawers, delete by source, dedup, repair; limited epistemic correction | Palace, wing, room, source file, parent drawer, backend namespace | MCP, CLI, hooks, skills, wake-up stack | Mining, closet/hallway/tunnel computation, repair/sync/backup | Strong source provenance; weak candidate/verified/rejected trust state | Evidence-preserving raw baseline, hybrid retrieval, operational hardening | Raw stores get large/noisy; contradiction resolution mostly outside core recall |
| `memu` | `RecallFile` on a memory or skill track, sliced into `RecallFileSegment` search units | Pluggable repositories over SQLite, Postgres, or in-memory | Single-shot, LLM-free: segments ranked by embedding, rolled up to files by max score | `commit_results` writes recall files, resources and user state in one call | Segments dropped and recreated when a file is re-sliced; no supersession found | `where` filters over records; no tenant or project model traced | Host adapters for Claude Code, Codex, Cursor, OpenClaw, Hermes, Cola, WorkBuddy | Scheduling module; agentic backend for richer flows | Timestamps and track only; no source, actor, or status on a record | Ranking on segments and returning files, with local/remote ordering parity as an invariant | No trust state, provenance, correction path, or tombstone |
| `memvid` | Immutable frame; structured memory card keyed `entity:slot` with a cardinality | One `.mv2` file — payload, internal WAL, TOC, footer, lexical/vector/time indexes, no sidecars | Lexical, vector and graph search over frames; `get_current` and `get_at_time` per entity:slot | Append-only frames through a WAL; supersede links; enrichment recorded per engine and version | `Active \| Superseded \| Deleted`; supersedes/superseded_by chains; a `Tombstone` WAL op | ACL module over a single file; no multi-tenant model traced | Rust library and CLI over a portable file | Enrichment workers, maintenance, doctor | Checksums per frame, an audit module, enrichment provenance by engine and version | Immutable frames plus as-of reads and session replay — the memory can be rewound | Headline benchmark numbers with no committed result artifacts found; correction is frame-keyed |
| `mercury-agent` | `UserMemoryRecord` graded on confidence, importance, and durability | Second-brain DB, with people and relation records | Retrieval records `lastUsedAt` and `lastUsedQuery` | Candidates with narrowed `evidenceKind`; `evidenceCount` on corroboration | `dismissed` boolean and `supersededBy`; no tombstone | `durable`, `active`, `subconscious` tiers; single user | Internal, with a `brain/Memory.tsx` review page | Not traced | Four-way `evidenceKind`, corroboration counts, free-text provenance | Durability separated from importance; a subconscious tier; a learning-pause switch | Scores estimated once at write time; dismissal is not durable |
| `metaclaw` | `MemoryUnit` with type, status, importance, confidence, access count, reinforcement score | Store with embeddings, per-scope policies | Under a live `MemoryPolicyState`: mode, unit cap, token budget, weights | Conversation writes plus consolidation; no actor gate | `superseded_by` lineage, `expires_at`; no rejected state | `scope_id` throughout store, retriever, policy, metrics | OpenClaw plugin with a written spec and a sidecar manager | Self-upgrade worker: candidate → replay → gate → promote | Source session and turn range; reinforcement kept apart from confidence | Retrieval policy replayed offline and promoted only on non-regression across eight metrics | Optimizes overlap proxies; gate thresholds are themselves defaults |
| `minecontext` | A typed context with an event time, a confidence and an importance score, keeping its raw properties beneath it — plus todo rows with an open/done lifecycle | SQLite for structured rows, with ChromaDB or Qdrant for vectors | Vector search per context type, plus tool-shaped retrieval for todos, activity and entities | Passive capture from screenshots, folders, vault documents and web links, then LLM extraction and typed merge | Update and delete exist on the API; no UI is wired to them and no rejected-value record is kept | None on contexts or todos; user_id appears only on the chat conversations table | An Electron desktop app over a FastAPI server, with generated daily and weekly reports | Continuous capture, typed merging, and a SmartTodoManager that generates commitments from observed activity | Integer confidence and importance scores on extracted data; no status and no provenance chain to the screenshot | Event time separate from record time and allowed to be future; raw properties retained under every extracted context | No tests in the Python package; commitments are inferred from screen capture and nothing reviews them |
| `mirix` | Six typed rows — episodic event, semantic concept, procedural step, resource, knowledge-vault secret, core block — plus a raw_memory evidence table | Postgres with pgvector, or SQLite with FTS5; Redis Stack as a search-capable cache | Per-type search by embedding, BM25/full-text or string match, selected by the caller | Deferred — messages accumulate in a buffer, then a meta agent routes them to six specialist writer agents | Tool-driven replace, implemented as hard delete followed by insert; no supersession record | organization_id, user_id, client_id and a filter_tags scope, applied on every read path including the cache | REST API, Python client, outbound MCP client, read-only React dashboard | auto_dream — a periodic pass that loads up to 500 items per memory type and lets an agent merge and rewrite them | None represented; no status field, no confidence, no provenance beyond a free-text source string | Scope enforced across schema, queries, cache and tests; a raw evidence table; negative retrieval assertions in the test suite | auto_dream can hard-delete a correction; credentials stored as plaintext in knowledge_vault; last_modify is last-write-only |
| `mnemopi` | A typed memory — one of fourteen types, each carrying a `veracity` provenance class and a type-specific decay curve | Bun SQLite, one database per named bank under `~/.hermes/mnemopi/data/banks/`, with optional local ONNX embeddings | Polyphonic — four scored voices (vector, graph, fact, temporal) combined per memory, with MMR and an episodic graph beside them | Regex type patterns assign a type, a base confidence and one of nine priority classes with no model call; an LLM path is optional | `forget(memoryId)`, `update(...)`, and a `sleep(dryRun)` consolidation pass that can be run without applying anything | A bank is a separate database file selected by `setBank`; there is no scope predicate inside a bank | The memory engine behind the oh-my-pi coding agent, with retain, reflect, render and edit tools and a `memory://` protocol | `sleep` and `sleepAllSessions` consolidation, plus SHMR clustering with similarity and harmony thresholds | Veracity as a provenance class — stated, inferred, tool, imported, unknown — mapped to a fixed weight | Per-type Weibull decay with a shape as well as a scale, a dry-run consolidation pass, and a committed recall-precision regression suite | `unknown` provenance is weighted 0.8, above `tool` at 0.5 and `inferred` at 0.7, so a memory with no known origin outranks one whose origin is known |
| `moltis` | Chunk of a Markdown file | SQLite with vectors; pluggable local, OpenAI, batch, and fallback embeddings | Hybrid keyword plus vector, optional LLM rerank, citation modes | Corpus files plus sanitized session transcripts, one `sync()` chokepoint | Edit or delete the file and reindex | Indexed directory only | In-process library inside the host workspace | File watcher and scheduled memory work | Citations to path and chunk; content-hash addressing | `keyword_only()` makes a no-embeddings mode constructible and inspectable | Transcripts and curated notes rank identically; no trust state |
| `nanobot` | Markdown durable files plus JSONL summary lines | `SOUL.md`, `USER.md`, `memory/MEMORY.md`, `history.jsonl`, git | None; durable files are always in context | Consolidator appends evidence; Dream is the sole durable writer | Surgical edits under git; no tombstone | One workspace | Internal, with WebUI and cron | Dream on cron, gated on tool-error-free runs | Git history over an explicit durable-file allowlist | Dual cursors, and a cursor that refuses to advance after tool errors | No provenance from claim to evidence; single workspace scope |
| `neko` | A fact or observation carrying independent reinforcement and disputation counters with separate decay clocks, plus a scope and a source | Per-character JSON views — facts, reflections, persona, directives — behind an append-only event log, with embeddings and archive shards | Hybrid BM25 and cosine fused by RRF, then an LLM rerank, with scope filtering applied before ranking and a hard filter dropping disputed entries | Extraction into an outbox, deduplicated, with reflection and refinement passes running as background workers | Disputation drives an entry's score negative and out of recall; archival needs sustained negative days; no rejected-value record survives archival | `MemorySubject` with group and participant scopes, missing fields failing closed to `legacy_private`, filtered before any ranking | A companion runtime — voice, vision, avatar — with memory as an internal subsystem rather than an exposed API | Embedding worker, reflection, refinement, dedup, archive sharding, and an outbox so mid-flight tasks can be re-run | Reinforcement and disputation tracked separately with independent decay, deriving pending, confirmed, promoted or archive-candidate at read time | A dispute signal structurally separate from reinforcement; a tested hard filter on disputed entries; a durable do-not-mention list | The status is derived from a score rather than stored; ban-topic directives expire after three days |
| `nemoclaw` | None of its own — a declared state directory belonging to a wrapped agent | Durable volume per agent; snapshots taken by `nemoclaw backup-all` | None; the wrapped agent retrieves from its own store | None; NemoClaw governs the container, not the contents | `destroy` wipes declared state dirs; restore reinstates snapshotted ones verbatim | Per-agent state directories under one config dir, with locks and permission repair | Sandboxes Hermes, OpenClaw and LangChain Deep Agents in OpenShell | State-dir guard, config locks, permission repair, audit | Credential sanitization on backup; audit surface; nothing epistemic | The only explicit, inspectable backup-and-destroy contract over agent memory in the atlas | Memory is snapshotted and restored verbatim, so a restore can reinstate deleted memories |
| `neo4j-agent-memory` | Conversation turn, extracted entity, preference, and reasoning trace with tool calls | Neo4j — one graph shared across agents rather than per-agent silos | Graph queries over entities and relationships; embeddings; reasoning steps with parent context | Conversation capture, GLiNER extraction pipeline, traces recorded via a context manager | `supersede_preference`, idempotent, with `valid_from` / `valid_until` bounds | Multi-tenant mode that raises when a user identifier is missing | MCP server, CLI, AWS Strands tools, OpenAI Agents SDK examples | Consolidation; extraction pipeline | Trace outcomes with success, error kind and metrics; no trust state on a fact | A reasoning tier that captures failures automatically, and fail-closed multi-tenancy | No value-level tombstone; supersession covers preferences rather than every memory kind |
| `nooa-memory` | `Memory` typed info, skill, episode, intent, todo, reflection or scratch, with typed edges | SQLite with owner/status columns and pluggable vector backends | ACT-R activation — relevance, base-level recency, importance, plus graph spreading over k hops | Authoring via a memory skill; reflection distils episodes into gists | Retention decay archives below threshold; `archived` flag, record-keyed | `owner` column, indexed, applied on the retrieval path | Exposed as a memory skill inside the Object-Oriented Agents framework; tracing bridge | Reflection: dedup/merge, edge formation, re-scoring, prune — deterministic steps need no LLM | Separate importance, salience and confidence; per-access score components retained | Every retrieval leaves behind why it ranked where it did, on the record itself | Archival is record-keyed, and the access log is capped, so both history and correction are bounded |
| `npcpy` | A `MemoryItem` — content plus context, tied to a message, conversation, npc, team and directory, carrying an initial and a final text and a status | A JSON-backed knowledge store per directory, a knowledge graph with concepts and links, and a separate index | `build_context` takes only `human-approved` memories, capped; the knowledge graph and index are searched separately | A background processor extracts candidates from conversation, then a terminal review loop decides each one | `update_memory(mem_id, status, final_memory)` — approval, rejection and edit all move the same row | npc, team and directory are recorded on every item and none of them filters `build_context` | A CLI-first agent framework with NPCs, teams, jinxes and a set of knowledge skills | A threaded queue extracts memory candidates without blocking the conversation | `pending_approval`, `auto-extracted`, `human-approved`, `human-rejected` — a stored status, and only one of them is retrievable | A five-way review loop with edit and defer, and a retrieval path that reads approved memories only, so an unreviewed extraction cannot reach a prompt | A rejection is a status on a row; re-extraction of the same content produces a fresh candidate with nothing consulting the earlier no |
| `open-cowork` | Core memory and experience memory as separately extracted kinds | Per-kind stores plus SQLite FTS, with an ingestion queue | Retriever then navigator assembles the prompt prefix; tested FTS-absent path | Queue, then per-kind extractors with independently optimized prompts | No visible trust state or tombstone | Workspace field on eval queries; scope model not traced | Memory tools plus an extension entry point | Ingestion queue and prompt optimization | Not traced; no verification modules found | A committed eval harness with `forbiddenHits` — negative retrieval assertions | Harness present, results absent; substring scoring favours extractive memory |
| `openclaw` | Categorized entry (preference/fact/decision/entity/other) with embedding | LanceDB via `memory-lancedb` extension; swappable embedding adapters | Vector search with mandatory agent-scoped predicate; no lexical arm | Optional auto-capture after envelope sanitization; 500-char truncation | Exact scoped delete; no tombstones, and auto-capture can restore content | `agentId`, composed inseparably into every predicate | Plugin contract via `memory-core`; tools, CLI, doctor checks | Auto-capture cursor with fingerprint drift detection | `createdAt` and category only | Envelope sanitization before capture; scope that cannot be dropped | Vector-only reference backend; sanitization is a denylist tied to envelope formats |
| `opencode` | None — sessions, messages, parts and todos; instruction files are read, not stored | SQLite via Drizzle: session, message, part, todo, project, workspace tables | None for memory; instruction files resolved by nearest-ancestor lookup | None for memory; plugins may transform messages and the system prompt | None; no durable claim exists to correct | Project and workspace ids on sessions; nothing scopes memory because there is none | Plugin hooks, MCP, skills, LSP, tools | Compaction, with two hooks around it | None applicable | A compaction hook and a system-prompt transform — the two seams a memory plugin needs | Both are experimental, and there is no memory contract, so plugins reach past the API into SQLite |
| `openhuman` | `MemoryEntry` — id, key, content, namespace, category, timestamp, session, score and a `MemoryTaint` provenance label; plus chunks, tree summaries and extracted `event_log` rows | SQLite plus on-disk markdown across seven primitives — raw, chunks, entities, trees, vectors, kv, contacts — with FTS5 and a git repository used as a derived diff ledger | Hybrid vector and FTS5 search, an agentic tree walk, and cross-session episodic recall that is off by default and carries source session ids when on | Sanitize for secrets and PII, then ingest source to canonical markdown to chunks to scores; extraction is two-tier — regex always, local LLM on segment close | Snapshot diffing against a git ledger, tree bucket-seal and flush, operational tombstones for unembeddable rows; no rejected-value record | Namespace applied in SQL on the read path, plus session scoping and a cross-session flag defaulting to off | RPC namespace, agent tools per module, MCP sync pipelines, Composio and workspace connectors | Ingestion and extraction queues, re-embed backfill, tree summarisation, and a goals reflection agent fired on segment close | `MemoryTaint` — Internal or ExternalSync, failing closed to the restrictive value, gating which memories may drive external-effect tools | A taint lattice that governs consequence rather than belief; sanitization that deliberately cannot launder provenance; ~1,278 memory tests | Much of the core is re-exported from a separate unread crate; nothing records a rejected value; taint is binary and never re-evaluated |
| `openviking` | Typed memory file with L0 abstract, L1 overview, L2 content, links and backlinks | Pluggable vector/graph stores plus native Rust/C++ index | Directory-recursive dense + sparse, level filter, per-type quota, rerank, hotness blend | LLM extraction into typed files; write target resolved before persistence | Merge ops with `upsert`/`add_only`/`update_only`; no rejection state | Tenant and permission via `RequestContext`; user space plus `peers/<id>` | Server, SDKs, CLI, web studio; Hermes and OpenClaw provider | Extraction, streaming update, reindex, hotness maintenance | URIs, types, timestamps; no evidential spans or trust state | Three-granularity progressive disclosure; hotness kept apart from confidence | Headline benchmark numbers lack committed raw artifacts; AGPL-3.0 |
| `openworker` | Row with scope, optional key, content, workspace, session, created_at | SQLite (`coworker.db`) alongside sessions and workspaces | Listing filtered by scope and workspace; no ranking or search | Three agent tools — `remember`, `memory_update`, `memory_forget` | Update by id, hard delete by id; no supersession or tombstone | `Scope` of global, workspace, or session, applied on read | Tools wired into the agent loop with guidance injected only when a store exists | None for memory | Timestamps only; the prompt tells the model to re-verify what a memory names | The write policy is explicit, and it addresses a stated failure of models without one | No ranking, no correction record, and the whole discipline lives in a prompt |
| `optmem` | One line of at most 280 characters, fixed width, position-addressed | `LOG.txt` append-only, never edited; `TREE/` of compressed blocks, a rebuildable cache | `wake` prints a budgeted cover of the merge tree — verbatim recent, compressed ancient | `note` appends one line and may return a compression for the agent to answer | `forget <lo>-<hi>` drops a summary; the next nap rebuilds it. The log is never edited | One store per `$MEMORY_DIR`; none within it | A 426-token prompt block pasted into AGENTS.md or CLAUDE.md | None, by design — every compression is requested inline in the output of `note` | None; the log is append-only and everything derived is rebuildable from it | Detail decays by geometry, not policy, and no job can rewrite memory behind your back | No licence file; no scope, trust, or correction of the log itself |
| `pi` | None — session-tree entry, not a memory record | JSONL session tree (`id`/`parentId`), swappable in-memory backend | None; context is the tree walked to root plus discovered resource files | Append to session; compaction replaces a range | None; no durable claim exists | None | Own CLI/TUI/SDK; 20+ extension events, none memory-shaped | Compaction and branch summarization | Deterministic `readFiles`/`modifiedFiles` on compaction entries | Deterministic file manifest kept out of the model's output; branchable sessions | No memory contract at all, so scope and deletion have nowhere to live |
| `powermem` | An LLM-extracted memory row with retention metadata, plus distilled Experience and Skill records above it | SQLite, pgvector or OceanBase for memory; the skill and source stores are OceanBase only | Vector, FTS and graph fused by RRF, with recency and retention scores applied | LLM extraction with a simple and an intelligent path, plus background workers | Update and delete APIs; forgetting is a retention score falling below a threshold | user_id, agent_id and run_id built into effective filters and carried into the store | Python SDK, HTTP server, MCP, CLI, VS Code extension and a Claude Code plugin | Decay, promotion and archival evaluated during search, with some updates dispatched to a thread pool | None; retention and importance are scores, and no memory carries a status | The atlas's most complete forgetting-curve implementation, with promotion, archival and reinforcement as separate decisions | The history table has no callers anywhere in the repository; search writes to the store |
| `pydantic-ai-harness` | A Markdown file. `MEMORY.md` is the notebook; other files hold focused notes, each versioned with a generation counter and a fingerprint | A `MemoryStore` Protocol with three implementations — in-memory, a directory of files with a SQLite sidecar, and Postgres — plus an optional `SearchableMemoryStore` extension | A bounded excerpt of the notebook plus a file listing injected per request under a token budget; `read_memory` for a prefix and `search_memory` for bounded text search | Model tool calls only — no extraction pass. Optimistic concurrency on a version, with an idempotency id derived from the run and tool call | `write_memory` appends or replaces one unique fragment; `delete_memory` removes a file and the main notebook is protected. No record of what a delete removed | `{namespace}/{agent_name}` composed by application code, never exposed as a tool argument, and the toolset raises if the backend returns a path outside it | A Pydantic AI capability — `Agent(..., capabilities=[Memory(FileStore(...))])` — contributing four tools and a user-role context part | None. Writes are synchronous tool calls; crash recovery replays an incomplete operation from its receipt | None. A memory is a line in a Markdown file; there is no status, confidence, provenance or source on any of it | Scope the model cannot name and the toolset re-checks; idempotent writes under optimistic concurrency; 2,498 lines of tests to 2,452 of code, asserting what must not reach the prompt | Delete is content-free by design, so nothing records that a value was rejected; the operations table clears its own payload on success, so it audits nothing |
| `qwen-code` | Auto-memory entry typed `user \| feedback \| project \| reference`, with source refs | Markdown context files on disk; the team tier is committed to the repository | Indexed scan with a relevance selector; async recall on demand | Background extraction from sessions, cursor-tracked; `dream` consolidation; skills reviewed before use | `forget` by candidate selection, by match, or by entry; no value-level tombstone found | User, project and team tiers with separate paths; team writes guarded unconditionally | Built into the CLI; memory channels for intent and recall | Extraction with a resumable offset cursor, dream consolidation, skill review nudges | Source session and message ids; extraction and dream record `updated` or `noop` | A shared tier that is source-controlled, with secret writes refused even when the tier is off | Correction is entry-keyed, and re-extraction from retained sessions is unguarded |
| `rainbox` | Claim, evidence, embedding, retrieval event | Postgres/SQLAlchemy plus pgvector | Hard-filtered hybrid (vector + Postgres full-text + entity boost) for both chat and assistant; profile digest | User commands, assistant actions, review UI; single governed atomic path (`record_belief`); write-time conflict detection; active/candidate flows | Reject/supersede/reactivate/expiry/sensitivity; `MemoryRejectedValue` tombstones block model re-assertion of rejected values; governed atomic correction (`correct_belief`); UI stale-write guards | Global, agent, room, project; sensitivity | Full assistant app: chat prompt (via `build_chat_memory_block`→hybrid), action loop, review UI | Embedding sync/prune, telemetry, feedback/eval loop | Five-actor trust model (3 human/override + 2 model/candidate); rejected-value tombstones; write-time lattice-aware conflict detection; governed atomic correction; fenced prompt injection; claim/evidence provenance and retrieval audit | Operator governance, trust/correction machinery (tombstones + conflict detection + fenced recall + governed writes), telemetry, eval integration | Compact claims may lose source nuance; no automatic candidate extraction; `epistemic_confidence`/`retrieval_strength` columns exist but Tier-1 ranking still uses `confidence` (schema groundwork only); attribution is context-injection, not causal |
| `redis-agent-memory-server` | Working-memory message; long-term `MemoryRecord` typed episodic/semantic/message | Redis with TTL for working memory; pluggable vector DB for long-term | Vector search plus metadata filters, reranked by recency with dual half-lives | Debounced trailing extraction via swappable strategies, then layered dedupe | Exact delete; composite forgetting policy; no tombstones | Namespace, `user_id`, `session_id`, with auth | REST, MCP, CLI, SDKs; backs the OpenClaw Redis plugin | Debounced extraction, compaction, dedupe, forgetting sweeps | Session linkage and per-message extraction flags; no trust state | Best-specified retention policy in the atlas; cohesion-gated semantic merge | Deletion is not durable against re-extraction; access-driven reinforcement |
| `reme` | A Markdown note with YAML frontmatter and wikilinks, chunked for indexing | Files on disk as canonical, with FAISS and a keyword index as rebuildable projections | Vector plus BM25 fused by reciprocal rank, then wikilink traversal, with date filters | An agent writes and edits the notes through tools; auto-memory, auto-resource and auto-dream run as pipelines | A validated CREATE / CORROBORATE / REFINE / CORRECT verb per integration, with an additive-only update rule | One workspace directory per application instance; no scope key on the read path | Python service and CLI, plus Claude Code and Hermes plugins and a SKILL.md | Auto-dream extracts cross-file units, integrates them into digests, and checkpoints changed paths | A `status` frontmatter field is reserved by the prompts and read by nothing | Committed per-category benchmark results including its own worst numbers; a real correction vocabulary; additive updates | The correction vocabulary is enforced as a returned label, not as a constraint on the edit |
| `risuai` | A summary of a contiguous run of chat messages, carrying the set of message ids it was derived from, an importance pin, a category and tags | Per-chat-room JSON in the local database, with an embedding cache keyed by content and model | A token budget split into four bands — pinned, recent, embedding-similar, and random — with RRF from chunks up to parent summaries | An LLM summarizes a run of messages when the context overflows; re-summarization compresses summaries further | Summaries whose source messages no longer all exist are dropped; a person can edit, delete, merge, re-roll or pin any summary | Per chat room and character; no principal or tenant key | The chat UI itself; the selected summaries are injected as one `Past Events Summary` block | None — summarization happens inline on overflow, under a rate limiter | None epistemic. `isImportant` is a user pin, not a confidence or a verification state | Derived summaries carry their source message ids and are dropped when a source is deleted; a full review surface over machine-written memory | Three generations of summarizer ship side by side and none of them has a test |
| `second-me` | Three layers — a document with its raw content, a versioned biography and shades derived from it, and the model weights trained on both | SQLite for documents, chunks and the versioned L1 tables; ChromaDB for embeddings; GGUF files for the model | Embedding search over documents and chunks, plus whatever the fine-tuned model recalls without retrieval | Upload documents, generate L1 as a numbered version, then synthesize training data and run LoRA SFT and DPO | Document deletion cascades through chunks and both Chroma collections, and touches neither L1 nor the weights | None — the design is one person, one machine, one model | A local web app over a Flask kernel, with GGUF export and a decentralized network for connecting AI selves | Training pipelines run as scripted jobs rather than as a scheduler | Pipeline statuses only; no memory carries an epistemic state | L1 is a numbered generation over retained L0, so the derived layer is rebuildable and comparable across versions | Forgetting stops at the vector store; the trained model keeps what a deleted document taught it |
| `sillytavern` | A World Info entry: human-authored content plus primary and secondary keys, a logic mode, insertion position, order, depth and timed-effect settings | JSON lorebook files per world under the user's `worlds/` directory, plus a rolling summary in chat metadata | Keyword scan over a depth-bounded window, four logic modes, bounded recursive activation, token budget with a cap | A person types it. The optional summarize extension writes one rolling LLM summary into chat metadata | Edit or delete the entry in the editor; `@@dont_activate` suppresses an entry without removing it | Per-world lorebooks, character-bound or global, with an insertion strategy deciding precedence | The chat UI itself; entries are injected into the prompt at author-chosen positions and depths | None for lorebooks; the summarize extension runs on a message-count or token trigger | None. An entry is as true as whoever wrote it, and no field records who or when | Sticky, cooldown and delay as first-class activation state; negative key logic; a budget with a cap | Imported lorebooks carry no author field; recursion plus keyword triggers make activation hard to predict |
| `simplemem` | A `MemoryEntry` — a lossless restatement with pronouns resolved and times absolute, plus keywords, timestamp, location, persons, entities and topic | LanceDB behind a small vector-store wrapper for the text pillar; a separate SQLite schema with seven tables for EvolveMem | Query analysis, then parallel semantic, keyword and structured searches, merged and deduplicated, then an LLM adequacy check that can fire further query rounds | Windowed LLM extraction over dialogue batches, parallelised across workers; entries are added, never revised | The text store has `add_entries`, `get_all_entries` and `clear()` — no delete, no update. EvolveMem adds `update_content`, archive, and a `superseded` status | Absent from the text pillar entirely; `scope_id NOT NULL` on every EvolveMem read, with a `scope_access` principal/permission table beside it | A CLI, an MCP server, an HTTP server with per-user API keys, a Claude skill, and a benchmark runner per pillar | None on the text path. EvolveMem runs a closed-loop evaluate-diagnose-propose-guard cycle that rewrites retrieval configuration, not memories | An `importance` and a `confidence` float on EvolveMem units, moved by thumbs-up/down feedback; the text pillar has no trust representation at all | Memory units built to be context-independent — coreference resolved and time absolutised at write; an append-only event log recording seven mutation kinds | Six headline benchmark figures and no committed result artifact for any of them; the pillar the papers are about cannot delete or correct a single memory |
| `skales` | An `ExtractedMemory` — id, category, content, source conversation id, extraction time, relevance keywords — plus tiered memory files and a soul profile of known facts | JSON files under `.skales-data/`: one per extracted memory, plus short-term, long-term and episodic files and the soul object | Synchronous keyword scoring — overlap 0.70, recency 0.20, category boost 0.10 — top five, no LLM, behind a 30-second cache | Regex extraction over conversations since the last scan, run every 90 minutes; no model in the write path | Extracted memories and tiered files delete cleanly; known facts have no delete path in code at all | None. A single-user local application with no user, project or tenant key | An Electron desktop app with a Next.js web surface, chat, cron tasks and a dedicated memory page | A 90-minute scan driven by a cron job, watermarked by `lastScanTimestamp` | A source conversation id on every extracted memory; no confidence, no state, no verification | Zero-LLM capture and retrieval, both cheap and legible; a real memory management page; provenance on every extracted row | The documented deletion path for facts is a chat phrase nothing implements, and that phrase is bound to capture and retrieval instead |
| `soul-of-waifu` | Four kinds of Markdown file — a psychological state index, a user profile, per-subject topic files, and a dated append-only diary | Plain files under `.soul/<character>/chats/<chat>/memory/`, with a rolling five-deep backup directory | The index and profile are injected whole; topic files are ranked by MiniLM cosine similarity above a file-count threshold | A Router sub-agent returns JSON that the code renders into a fixed Markdown skeleton; an Archivist writes topic files; a Diary appends | The index and profile are overwritten wholesale, backed up first; topic files are overwritten; nothing is ever deleted | Per character and per chat, as a filesystem path; no principal or tenant key | The companion app's own prompt builder; no API and no tool interface | The pipeline runs every four messages, with the diary generated as a concurrent task | None. The `trust_level` field is the character's feeling about the user, not confidence in a memory | Short-output writes are rejected rather than stored; contradiction resolutions are logged; every index rewrite is backed up first | The backup, restore and inspection API has no caller anywhere in the application |
| `supermemory` | Document, chunk, memory entry, space | Hosted backend; visible schemas/client only | Hosted search/profile API; SDK uses hybrid settings | API/MCP add memory/document | Version chains, relations, forget API | Space, container tags, org/user/project | SDK, AI SDK tools, MCP | Hosted processing not visible | Rich schema fields and relations; implementation not visible | Product/API surface, document-memory graph | Backend black box; semantic forget needs care |
| `swafra` | Verbatim or synthetic chunk plus directed chunk edges, and a (subject, relation, value) fact carrying a validity end | Adaptive: three JSON files by default, auto-migrating to SQLite with WAL only past 5,000 chunks | BM25 + vector + entity/date/preference heuristics + char n-gram; graph walk; best chunk per title; optional LLM rerank | MCP add; Leiden or exchange/paragraph chunks; synchronous full-file rewrite; optional LLM dedup and entity extraction | Intra-source chunk supersession; transition-only fact supersession that a new session re-asserts; delete strands cross-session edges | Source ID/title only; no user/project/tenant scope | Python FastMCP, Node MCP over subprocess, Python and JS SDKs, a native CLI, a Claude Code skill | None | Fact confidence score and a validity end; no actor, span-quality provenance, trust state, or injection fence | Compact local hybrid graph-RAG; a real correction path reaching the ranker; optional dependencies; source diversity | Default JSON writes unlocked and non-atomic; dangling edges on both backends; benchmark invalid and its harness broken |
| `tencentdb-agent-memory` | L0 conversation, L1 memory record, L2 scene, L3 persona, offload reference/map | JSONL/Markdown plus SQLite FTS5/sqlite-vec or Tencent VectorDB | FTS + vector hybrid RRF; native cloud hybrid; layered scene/persona context | Successful-turn capture, LLM extraction, store/update/merge/skip judge, symbolic tool-output offload | Internal merge/delete/cleanup; no first-class correction/forget tool | Session fields and data directories; no general tenant boundary | OpenClaw hooks/tools/context engine; Hermes gateway | Deferred embeddings, scene/persona generation, retention reclamation | Source message IDs and raw evidence; no verification/rejection state | Layered progressive disclosure with raw drill-down | Non-atomic dual writes, fail-open dedup, thin core tests, unsupported benchmark claims |
| `tigrimosr` | A skill — a SKILL.md with a registry row carrying review status, rationale and the sessions it came from — plus one memory.md per project | JSON files on disk (skills.json, projects.json, chat history) and SKILL.md directories | No search; the project's assigned skills and its memory.md are assembled into the system prompt | A synthesizer reads finished sessions, user feedback and subagent traces, then proposes create or update | Proposals stage as SKILL.md.proposed and become live by rename on approval; rejection deletes the proposal and records nothing | Project id selects the memory.md and filters the installed-skills block on the read path | Native Rust desktop app, embedded web UI, MCP servers, plugins, Telegram and LINE bots | A scheduler runs the skill synthesizer; compaction hooks track file reads and invoked skills | review_status pending or approved, persisted, with pending coupled to enabled=false | A staged proposal a person can diff before it takes effect, carrying its rationale and source sessions | Proposal state is in-memory only, so a rejected skill can be re-proposed after a restart |
| `tokenmizer` | A graph node — one of fourteen types (task, decision, file, error, endpoint, schema, goal, test…) carrying a label, a summary and one of eight statuses | SQLite: nodes and edges plus a separate `decision_transitions` table that survives graph pruning | `query()` over the graph, excluding superseded, archived and invalidated nodes; `to_context_block()` renders a resume block | A hybrid extractor over session messages, with an ontology and a validator, then a contradiction check on every decision node | Supersession when the evidence is clear, `CONTESTED` on both sides when it is not, `INVALIDATED` for explicitly wrong, plus pruning | Per-project graph caches; no scope predicate inside a graph | A CLI and server for coding sessions — checkpointing, compression, a dashboard and a visualiser | Decay, pruning and compression passes, with idempotence and correctness suites of their own | Eight statuses — pending, in_progress, completed, failed, superseded, invalidated, archived, contested — with three excluded from retrieval and one deliberately not | A status for unresolved ambiguity that keeps both sides visible instead of guessing, and a committed ground-truth measurement of extraction recall | The redaction functions are unit-tested in isolation and nothing asserts a secret fails to reach the rendered context block |
| `verel` | `MemoryRecord` fact/rule/schema/failure/skill | SQLite local plus backend adapters | FTS5/BM25 default, cosine with embedder; rank adds strength, confidence, trust | Candidate extraction, attested/corroborated promotion | Correction chains, rejected tombstones, decay/prune | Scope lattice | Helpers, MCP, hosted/replicated adapters | Consolidation, promotion gate, replication | Explicit candidate/verified/rejected, provenance, confidence | Best correctness model in set | Complex; may be heavy for product MVP |
| `virtualwife` | Short term, a raw exchange as JSON in Django; long term, an LLM summary of an exchange with an LLM-assigned importance score 1–10 | Two stores behind one `BaseStorage` interface — a Django model for the short term, Milvus for the long term | Short term is the last N rows by timestamp; long term sums relevance, importance and an hourly exponential recency decay | Every exchange is saved raw; with long memory enabled it is also summarised and scored by an LLM before insertion | `clear(owner)` wipes everything for one owner; there is no per-memory delete anywhere in the interface | An `owner` (character) and `sender` (user) key on the long-term path only; short-term retrieval drops the owner filter | A Django backend behind a VRM avatar front-end; no agent API | None. Summarisation and importance scoring run inline on the write path | None. `importance_score` is salience assigned by a model, not confidence | A four-method storage contract with `owner` on every method, including a scoped clear | `normalize_scores` sums three quantities on different scales without normalising any of them |
| `voyager` | Executable JavaScript skill plus generated description | `skills.json` and flat files, Chroma index over descriptions | Vector similarity over descriptions, top-5, returns code | Written only when a critic verifies environment success | Same-name rewrite; old versions on disk but unreachable | Single agent checkpoint directory | Research rollout loop; prompt injection of retrieved code | None | Verified execution is the provenance | Environment-verified write gate — the strongest in the atlas | Unbounded skill concatenation into prompts; no failure memory; frozen since 2023 |
| `waku-agent` | Fact (semantic), episode (episodic), and SKILL.md (procedural) | SQLite by default; Supabase for facts, Notion for episodes | Gated — a small model decides whether to search at all, and supplies the query | Consolidation batched after N new chats, not per message | None found; no supersession or tombstone | Single user | CLI agent; skills in the Anthropic Agent Skills format | Batched consolidation into facts and episodes | Gate decisions carry a reason string; no trust state on memories | Refusing expensive work at three levels, and failing open when the gate errors | No correction, scope, or trust model; gate adds a model call per turn |
| `z-waif` | A message pair — one user turn and one character turn — reduced to a list of word ids with the common words pruned out | Three JSON files under `RAG_Database/`: a word table with counts and values, per-pair word ids and scores, and the raw text | Six highest-value query words scored against every stored pair by shared-word count, with a length penalty; the best pair and its two neighbours are injected | Every message pair is tokenised into the word table after it is sent; no model is involved at any point | An undo pops the word-id rows and documents that it does not uncount the words; a manual recalculate rebuilds everything | None. One global corpus per installation | The companion app's own prompt builder; the result is injected as a `[System M]` block | A thread recomputes word values every 120 seconds, plus a roughly one-in-three chance of recomputing on any given turn | None. Every stored pair is equally eligible and nothing records where it came from | Inverse document frequency, length normalisation and a cap on the character's own words steering retrieval — all derived from scratch | A three-message window score is computed and never used; the licence is not open source |
| `zerostack` | A Markdown file — the global `MEMORY.md`, a per-project `SCRATCHPAD.md`, project notes, and a daily log per date | Plain files on disk under a store root, with project-scoped subdirectories and `YYYY-MM-DD.md` daily logs | `memory_read` with a source selector and `memory_search` with a case-insensitive regex, both capped at 32 KB of injected context | `memory_write` and `memory_edit` as agent tools, each preceded by a permission check that can prompt the user | An edit without `old_str` deletes a whole note; every destructive mutation first copies the file to a sibling `.bak` — one version, not a history | A project slug scopes scratchpad, notes and daily logs; `MEMORY.md` is deliberately global and shared across projects | Four tools behind the agent's ordinary permission checker, plus a `/memory` slash command | None | None. A line is in a file or it is not | Atomic write-then-rename, a `.bak` whose extension keeps it out of the `.md` listing and search, and truncation-with-warning instead of rejection on oversized writes | The backup is one version deep and overwritten on the next destructive edit, so two bad edits in a row lose the original |
<!-- END GENERATED MATRIX -->

### Capability index

The matrix above says what each system does. This index answers the other
question — *which systems actually have X* — for the mechanisms that most often
decide whether a memory layer is usable. It is generated from the same
frontmatter as the matrix, so it cannot drift from the reports.

For the same data as a filterable table of every system against all seven marks,
see the [capability index](../capabilities/); this listing is the narrative
version, kept here because the counts are the argument.

Definitions are strict, and a flag is present only where the mechanism was found
in code. Near-misses do not count, and the near-misses are frequently the
interesting part:

- [`claude-mem`](../systems/claude-mem/) has "tombstones" that synchronize row
  deletion across stores, which is not a rejected-value tombstone.
- The three tombstones are not equal. [`verel`](../systems/verel/) and
  [`rainbox`](../systems/rainbox/) normalize the value and refuse the *write*;
  [`daimon`](../systems/daimon/) keys on a hash of the item's exact text and
  suppresses on every *read* path — briefing, carry and index deletion alike.
  For a byte-identical re-extraction the effect is the same, and a paraphrase
  defeats the third but not the first two. Its own test suite never exercises
  re-assertion after a forget, so the mechanism is read, not demonstrated.
- [`mercury-agent`](../systems/mercury-agent/) grades confidence three ways but
  has no discrete state.
- Of the four trust-state systems, only [`verel`](../systems/verel/),
  [`rainbox`](../systems/rainbox/) and [`gini-agent`](../systems/gini-agent/)
  carry an explicitly **rejected** state.
  [`magic-context`](../systems/magic-context/) qualifies on `stale` and
  `flagged` — states that withhold a memory from being trusted — and it is the
  one system here keeping lifecycle and epistemic state on genuinely separate
  axes, but it has no rejected state and its own report notes that `flagged` has
  no resolution workflow.
- The mutation-audit flag is deliberately narrow, and five systems that look
  like holders are not. [`rainbox`](../systems/rainbox/)'s `RetrievalEvent` and
  [`atomic-agent`](../systems/atomic-agent/)'s `vote_events` are append-only
  event tables recording *use and feedback* — the other half of the
  [append-only memory audit](../patterns/append-only-memory-audit/) pattern, and
  valuable, but not a record of what changed.
  [`llm-wiki-memory`](../systems/llm-wiki-memory/), [`nanobot`](../systems/nanobot/)
  and [`basic-memory`](../systems/basic-memory/) get an audit trail from git,
  which is a real mechanism and a different one. For
  [`hindsight`](../systems/hindsight/) and [`agentmemory`](../systems/agentmemory/)
  the word "audit" appears in this atlas's own summary of them without a named
  artifact behind it, so the flag is withheld until one is verified. Carrying none of these flags is not the same as
being bad: [`waku-agent`](../systems/waku-agent/)'s entire design is about doing
less on purpose, and [`moltis`](../systems/moltis/) is a corpus-and-index system
that never claims to model belief.

<!-- BEGIN GENERATED CAPABILITIES -->
**Rejected-value tombstone** — A durable record of a *rejected value*, keyed on the value, so later extraction cannot silently re-assert it.

*3 of 111:* [`daimon`](../systems/daimon/), [`rainbox`](../systems/rainbox/), [`verel`](../systems/verel/)

**Explicit trust state** — Discrete epistemic status as a field rather than a confidence score, including at least one state that withholds a memory from being treated as true.

*9 of 111:* [`core-memory`](../systems/core-memory/), [`daimon`](../systems/daimon/), [`gini-agent`](../systems/gini-agent/), [`magic-context`](../systems/magic-context/), [`npcpy`](../systems/npcpy/), [`rainbox`](../systems/rainbox/), [`tigrimosr`](../systems/tigrimosr/), [`tokenmizer`](../systems/tokenmizer/), [`verel`](../systems/verel/)

**Bi-temporal validity** — When a fact was true tracked separately from when the system recorded or expired it.

*9 of 111:* [`agent-memory-supabase`](../systems/agent-memory-supabase/), [`atomic-agent`](../systems/atomic-agent/), [`core-memory`](../systems/core-memory/), [`gini-agent`](../systems/gini-agent/), [`graphiti`](../systems/graphiti/), [`memory-engine`](../systems/memory-engine/), [`memvid`](../systems/memvid/), [`neo4j-agent-memory`](../systems/neo4j-agent-memory/), [`verel`](../systems/verel/)

**Scope enforced in retrieval** — A stored scope key (user, project, agent, tenant) applied as a filter on the read path, not merely available as a tag. This certifies that the key reaches the query — not that the boundary is authenticated, nor that a caller cannot widen it by passing a different argument.

*61 of 111:* [`acontext`](../systems/acontext/), [`adk-python`](../systems/adk-python/), [`agent-framework`](../systems/agent-framework/), [`agent-memory-supabase`](../systems/agent-memory-supabase/), [`agentmemory`](../systems/agentmemory/), [`agno`](../systems/agno/), [`ai-memory`](../systems/ai-memory/), [`aukora-kernel`](../systems/aukora-kernel/), [`basic-memory`](../systems/basic-memory/), [`buzz`](../systems/buzz/), [`claude-mem`](../systems/claude-mem/), [`cognee`](../systems/cognee/), [`core-memory`](../systems/core-memory/), [`cortex`](../systems/cortex/), [`cowagent`](../systems/cowagent/), [`crewai`](../systems/crewai/), [`ctx`](../systems/ctx/), [`daimon`](../systems/daimon/), [`ecc`](../systems/ecc/), [`elastic-atlas`](../systems/elastic-atlas/), [`engram`](../systems/engram/), [`everos`](../systems/everos/), [`gini-agent`](../systems/gini-agent/), [`gobii`](../systems/gobii/), [`graphiti`](../systems/graphiti/), [`hindsight`](../systems/hindsight/), [`honcho`](../systems/honcho/), [`langmem`](../systems/langmem/), [`letta`](../systems/letta/), [`livingfeed`](../systems/livingfeed/), [`llm-wiki-memory`](../systems/llm-wiki-memory/), [`magic-context`](../systems/magic-context/), [`mastra-observational-memory`](../systems/mastra-observational-memory/), [`mateclaw`](../systems/mateclaw/), [`mem0`](../systems/mem0/), [`mem0sharp`](../systems/mem0sharp/), [`memanto`](../systems/memanto/), [`memmachine`](../systems/memmachine/), [`memobase`](../systems/memobase/), [`memori`](../systems/memori/), [`memory-engine`](../systems/memory-engine/), [`memos`](../systems/memos/), [`mempalace`](../systems/mempalace/), [`metaclaw`](../systems/metaclaw/), [`mirix`](../systems/mirix/), [`neko`](../systems/neko/), [`neo4j-agent-memory`](../systems/neo4j-agent-memory/), [`nooa-memory`](../systems/nooa-memory/), [`openclaw`](../systems/openclaw/), [`openhuman`](../systems/openhuman/), [`openviking`](../systems/openviking/), [`openworker`](../systems/openworker/), [`powermem`](../systems/powermem/), [`pydantic-ai-harness`](../systems/pydantic-ai-harness/), [`qwen-code`](../systems/qwen-code/), [`rainbox`](../systems/rainbox/), [`redis-agent-memory-server`](../systems/redis-agent-memory-server/), [`simplemem`](../systems/simplemem/), [`supermemory`](../systems/supermemory/), [`tigrimosr`](../systems/tigrimosr/), [`verel`](../systems/verel/)

**Append-only mutation audit** — A named append-only event record of memory *mutations* in the system's own store. Logs of retrieval or feedback are the other half of the pattern and do not count here, nor does git history.

*15 of 111:* [`aukora-kernel`](../systems/aukora-kernel/), [`ctx`](../systems/ctx/), [`daimon`](../systems/daimon/), [`lethe`](../systems/lethe/), [`magic-context`](../systems/magic-context/), [`mem0`](../systems/mem0/), [`mem0sharp`](../systems/mem0sharp/), [`memora`](../systems/memora/), [`memvid`](../systems/memvid/), [`neko`](../systems/neko/), [`optmem`](../systems/optmem/), [`simplemem`](../systems/simplemem/), [`soul-of-waifu`](../systems/soul-of-waifu/), [`tokenmizer`](../systems/tokenmizer/), [`verel`](../systems/verel/)

**Human review surface** — A place where a person inspects, approves, or adjudicates memory content before or after it takes effect.

*19 of 111:* [`acontext`](../systems/acontext/), [`agno`](../systems/agno/), [`core-memory`](../systems/core-memory/), [`cortex`](../systems/cortex/), [`daimon`](../systems/daimon/), [`engram`](../systems/engram/), [`hermes-agent`](../systems/hermes-agent/), [`juggler`](../systems/juggler/), [`llm-wiki-memory`](../systems/llm-wiki-memory/), [`memanto`](../systems/memanto/), [`memora`](../systems/memora/), [`mercury-agent`](../systems/mercury-agent/), [`npcpy`](../systems/npcpy/), [`qwen-code`](../systems/qwen-code/), [`rainbox`](../systems/rainbox/), [`risuai`](../systems/risuai/), [`second-me`](../systems/second-me/), [`tigrimosr`](../systems/tigrimosr/), [`verel`](../systems/verel/)

**Negative retrieval assertion** — Committed evaluation cases asserting that particular material must *not* be retrieved.

*13 of 111:* [`agent-afk`](../systems/agent-afk/), [`agno`](../systems/agno/), [`aukora-kernel`](../systems/aukora-kernel/), [`crewai`](../systems/crewai/), [`everos`](../systems/everos/), [`helm`](../systems/helm/), [`lethe`](../systems/lethe/), [`mirix`](../systems/mirix/), [`mnemopi`](../systems/mnemopi/), [`neko`](../systems/neko/), [`open-cowork`](../systems/open-cowork/), [`pydantic-ai-harness`](../systems/pydantic-ai-harness/), [`verel`](../systems/verel/)
<!-- END GENERATED CAPABILITIES -->

Three observations follow from the counts, stated no more strongly than the
counts support.

**Read-path scoping is common; correction is not.** Over half the atlas applies
a scope key when retrieving, while three systems carry a value-level tombstone.
That is not the same as saying scope is solved — this flag measures the read
path only. It says nothing about write authorization, whether background
consolidation respects the same boundary, whether cache and embedding keys
include it, or whether deletion reaches every scoped copy. A summary that spans
two projects has crossed a boundary the retriever would have enforced, and
nothing here measures that.

**Trust is usually a number, not a state**, which collapses "how sure am I" into
"how findable is this" — see
[decay and reinforcement](../patterns/decay-and-reinforcement/).

**Negative evidence is almost never tested.** Thirteen repositories of one hundred and eleven
assert that particular material must *not* be retrieved — the assertion every
scope, deletion and correction claim in this document ultimately rests on. Read together
rather than one at a time, they split cleanly in two, and the split says more
than the count.

**Four assert a boundary:** that a principal cannot retrieve another
principal's material. [MIRIX](../systems/mirix/)'s `test_filter_tags_db.py`
creates a memory under one scope, searches under another, and asserts the id is
absent. [Aukora Kernel](../systems/aukora-kernel/) does it better — an unrelated
principal reads `ok: false`, a subject whose delegation manifest was revoked
reads `ok: false`, and the owner reads `"the secret"` in the same block, so the
denial is proved *targeted* rather than a blanket failure.
[EverOS](../systems/everos/) does it at the endpoint: two owners, the same query
string, `assert c_ids.isdisjoint(m_ids)` plus a positive control on each side,
repeated for two agent owners sharing a keyword. [CrewAI](../systems/crewai/)
does it over a path hierarchy: three records written under `/other/scope`,
`/crew/crew-a/inner` and `/crew/crew-b/inner`, a `Memory` opened with
`root_scope="/crew/crew-a"`, and an assertion that recall returns exactly one
result and it is the rooted one — a boundary test with its own positive control
in the same three lines.

All four of those systems also hold `scope_enforced`. Their negative suites are
therefore tests **of a capability the same system already claims** — which is
worth having, and is not evidence about deletion or correction.

**Eight assert about content:** that particular material must not surface to
anyone entitled to search, regardless of who is asking.
[open-cowork](../systems/open-cowork/)'s `forbiddenHits` is an eval-harness field
naming what a query must not return, scored as a penalty.
[Verel](../systems/verel/)'s `tests/test_memory_negative_eval.py` asserts a
REJECTED fact is invisible to every recall path — a suite built from the
red-team finding that produced its tombstone. [Project N.E.K.O.](../systems/neko/)'s
`test_hard_filter_drops_negative_score` asserts that an entry the user
*disputed* is dropped before the rerank, the docstring giving the reason:
*"Stage-2 would either reinforce the dispute or, worse, cancel it."*
[Helm](../systems/helm/)'s supersede case asserts a replaced value no longer
appears, [agent-afk](../systems/agent-afk/)'s
`it('excludes superseded facts from search')` asserts the same about its FTS
path, and [Agno](../systems/agno/)'s `test_entity_supersession.py` does it
against a judged verdict — a retired fact absent from `live_facts()` while
both rows remain in the record. The [Pydantic AI
Harness](../systems/pydantic-ai-harness/) asserts it about the *prompt*:
`test_delete_existing_is_content_free` requires the deleted body to be absent
from the tool result, one search test requires `all('secret' not in
repr(match))` under a character budget, and two injection tests require a
superseded line and a stale fact from an earlier history not to appear in the
captured model context. That is the assertion aimed at where the damage happens
rather than at where the row lives.

**Only these eight probe the question the atlas is actually asking.** A boundary
test proves the filter works; a content test proves a value that was rejected,
disputed or forbidden stays gone. Nine of one hundred and eleven is the real figure for the
second kind, and the two newest are the cheap version of it: a *superseded*
value is easy to assert about, because the row is still there to filter on. The
expensive assertion is that a value the system destroyed does not come back.

Two further things the joint reading shows. The **positive control** — asserting
that the denial is targeted rather than an empty result — appears in Aukora and
EverOS and is absent from the rest, and a negative test without one passes just
as well when retrieval is broken. And the assertion shape is **reachable from
ordinary engineering practice**: three of the six arrived from access-control
work rather than from memory research, and one, N.E.K.O., from a companion app
where re-raising something the user asked you to drop is a product failure
rather than a data-quality one.

[Daimon](../systems/daimon/) is the near-miss that shows how narrow the bar is:
1,974 tests, a committed LongMemEval harness, unit tests asserting that a
resolved item is withheld and that an id-bearing item is never fuzzy-matched
into suppression — and still no case that forgets a value, re-extracts it, and
asserts it stayed gone. The tombstone is the mechanism most in need of a
negative test and the one least likely to get one, because nothing fails
visibly when it silently stops working.

## 3. End-to-End Memory Lifecycle Comparison

### Capture

`mem0`, `letta`, `langmem`, and `supermemory` expose direct tool/SDK surfaces for adding memory. `cognee` supports both explicit permanent writes and a session-hot capture path through `remember`. `claude-mem` writes hook events to a durable queue before invoking its observer. `a-mem` accepts direct Python note writes but runs LLM evolution before the new note is durable. `hindsight` retains documents/chunks before extracting facts. `graphiti` stores episodes before deriving entities and temporal relationships. `mastra-observational-memory` persists messages before compressing covered ranges. `memos` routes items into configured memory cubes. `basic-memory` accepts Markdown writes from MCP/API or human file edits and reconciles indexes. `rainbox` captures through explicit memory commands, assistant memory actions, and review UI mutations. `engram` captures via MCP tools and can also store prompt/session metadata. `mempalace` captures by mining files/conversations and by MCP drawer writes, preserving verbatim text. `swafra` captures titled text via one MCP tool, then stores chunks in local JSON — or in SQLite once a corpus passes five thousand chunks. `llm-wiki-memory` combines explicit MCP/CLI writes with lifecycle hooks. `honcho` captures messages as the primary event stream, then derives observations. `verel` routes captured percepts through a trust gate. `agentmemory` combines cheap hook capture with explicit `mem::remember`; compression is optional. `tencentdb-agent-memory` records raw conversation evidence, then extracts higher layers from successful turns. `redis-agent-memory-server` writes messages into TTL-scoped working memory first and defers extraction behind a debounce. `hermes-agent` captures curated memory only through explicit tool calls, because a hard character budget makes automatic capture self-defeating. `openclaw` and `holographic` both capture without a model — OpenClaw after sanitizing its own message envelope, Holographic by regex over user turns when auto-extraction is enabled.

Two systems in the Hermes/OpenClaw ecosystem independently guard against the same subtle failure: **the harness's own scaffolding becoming memory.** OpenClaw devotes 567 lines to stripping media notes, context markers, reply headers, and sender prefixes before capture, with a `looksLikeEnvelopeSludge` gate rejecting what remains. Holographic had to exclude its host's compaction handoff summaries, which were being injected as `role="user"` messages, matched its decision-extraction patterns, and were stored as durable facts on every context rollover. Any system with automatic capture should test explicitly that its own generated text cannot re-enter as evidence.

`helm` is the third instance, and the only one where the scaffolding entering memory was the *memory layer's own audit trail*. Every supersession writes a `fact superseded: <kind>/<key>` row into the same episode table that its word-frequency distiller reads from, so the distiller began minting `learned` facts about supersession, ticks and smoke tests. The fix is visible in three places at once and worth reading together: a twenty-word extension to the distiller's stop list containing `supersed`, `episode`, `tick`, `think`, `memory` and `smoke`; two smoke tests asserting that a `__smoke`-keyed supersede emits zero episodes and that four rapid supersedes of one key collapse to one row; and a changelog entry naming the cleanup — 42 smoke episodes, 85 duplicate supersedes and 24 polluted `learned` rows deleted. The general rule: if you log mutations into the store you consolidate from, tag them at the source, because a stop list is how you find out you did not.

`daimon` captures nothing during a session and everything at the end of one: a `SessionEnd` hook spawns a **detached** child that serializes the whole transcript into a single checkpoint, so the agent never blocks on capture and there is no incremental write path at all. It is also the clearest instance of *referencing* evidence rather than storing it — the checkpoint carries a `transcript_hash` and per-item source message ids pointing into the host's own transcript file, which daimon never copies. That keeps the store tiny and the provenance real, at the cost of a provenance chain that breaks the moment the host rotates its transcripts.

The important split is whether the captured item is itself memory or evidence for memory. Cognee, Claude-Mem, Honcho, Verel, MemPalace, Graphiti, Hindsight, Basic Memory, Mastra, Swafra, RainBox, agentmemory, and TencentDB Agent Memory are evidence-aware in different ways: Cognee retains source data below graph/vector projections; Claude-Mem queues hook material before generated observations; Graphiti keeps episodes behind edges; Hindsight links observations to source facts; Basic Memory keeps canonical notes behind projections; Mastra records exact message ranges behind summaries; agentmemory links memories to observations; and TencentDB preserves L0 messages and offloaded raw tool output. `mirix` belongs on the evidence-aware side by an unusually cheap route: a `raw_memory` table holding the unprocessed context string, embedded and searchable in its own right, sitting beside six typed derived tables. One table is the whole mechanism, which makes it the easiest instance in the atlas to copy.

`memobase` is the deliberate counterexample, and it is worth stating without disapproval. Its `persistent_chat_blobs` config defaults to `False`, so the source transcript is hard-deleted from Postgres once the buffer flushes and the profile is written. For a service holding other people's conversations that is a *good* privacy default and several systems here would be better for it — but it also means the profile is a lossy derivation whose source no longer exists, so a bad extraction is permanent. Evidence retention and data minimization pull in opposite directions, and Memobase is the clearest place in the atlas to see the price of each.

These designs still differ sharply in trust: provenance supports correction, but only Verel and RainBox model rejection/promotion explicitly.

### Extraction

`mem0` has the clearest open implementation of LLM extraction: retrieve nearby existing memories, ask the model for additive facts, parse JSON, dedupe, embed, insert, and link entities.

`langmem` delegates extraction to Trustcall and schemas. This is elegant if the application already knows what shape memory should have.

`honcho` formats timestamped session messages and derives representations/observations asynchronously.

`verel` extracts candidate memories but restricts promotion. It is deliberately suspicious of raw extracted claims.

`supermemory` exposes document/chunk/memory schemas, but the extraction engine behind hosted endpoints is not present in this checkout.

`mempalace` mostly avoids extraction for primary memory. It may build closets, entities, halls, and KG triples, but the authoritative memory remains verbatim drawer text.

`swafra` also avoids LLM extraction. Regexes annotate entities, date strings, and preference phrases; conversations get a synthetic facts chunk that acts as a retrieval index while exchange text remains stored. Its Leiden partition uses embedding similarity plus positional weight, despite docs also claiming entity-weighted partitioning.

`rainbox` does not center on automatic extraction in the inspected paths. Explicit user commands and assistant actions create/update claims; evidence rows record whether a claim was user-confirmed, model-inferred, imported, or observed.

`llm-wiki-memory` automatically distills coding transcripts into schema-constrained atoms with chunked map/reduce, stores them in dated daily leaves, then compiles them into durable knowledge or lessons. Compile retrieves same-type/facet candidates and asks an LLM for create/update/skip, except same-error-pattern lessons are force-updated deterministically. This path is recoverable and well tested, but promoted atoms become active without a verification gate.

`hindsight` extracts world/experience facts, entities, temporal spans, and causal links from durable source material. `graphiti` extracts entities and typed relationships from an episode, then resolves them against existing graph identity. `memos` ranges from simple key/value/tag extraction to tree-memory readers. `basic-memory` usually avoids LLM extraction: observations and relations are explicit Markdown syntax. `mastra-observational-memory` extracts chronological summaries rather than atomic facts.

`agentmemory` defaults to synthetic compression on the hot path and makes LLM
compression/consolidation optional. `tencentdb-agent-memory` uses an LLM to
extract L1 records, then another judgment step chooses store, update, merge, or
skip; failures store all candidates rather than losing them.

`redis-agent-memory-server` is the clearest example of extraction policy as a
plugin point: `BaseMemoryStrategy` has discrete-fact, summary, user-preference,
and fully custom implementations, so what counts as a memory is configuration.
Because the custom strategy accepts an operator-supplied prompt, it also ships a
`PromptValidator` that screens those prompts for injection — an unusual threat
model in which the deployment's own configuration is the attack surface.
`openviking` extracts into typed memory files whose `stage` field separates
long-term user memory from execution-derived agent memory. `holographic` and
`openclaw` deliberately do not extract at all: both store lightly-processed user
text, which keeps capture model-independent but fills the store with prose
rather than normalized claims.

`cognee` runs typed task pipelines that chunk documents, extract graph
structures, embed several views, and optionally ground nodes in an ontology.
`claude-mem` asks an observer model for XML observations and summaries, but
replaces its modified-file list with paths deterministically derived from tool
calls. `a-mem` asks an LLM to organize a new note and rewrite nearby metadata;
its `analyze_content()` method has no call site, so ordinary note metadata is
not extracted as the public mental model suggests.

`magic-context` promotes eligible session facts synchronously and defers embedding to a best-effort async pass, so a memory is durable before it is enriched. `pi` captures nothing as memory — its JSONL session tree is conversation history, and every memory plugin builds its own index over it.

`genericagent` states the strictest capture rule in the atlas, as prose rather
than code: its *Action-Verified Only* axiom permits a durable write only when the
information came from a **successful tool call** — a shell command that
succeeded, a read that confirmed content, code that passed — and explicitly
forbids writing the model's inherent knowledge, guesses, unexecuted plans, or
unverified assumptions. Its slogan is "No Execution, No Memory". This is
`voyager`'s environment-verified gate generalized from procedures to facts; the
difference is that Voyager enforces it in the rollout loop while GenericAgent
asks the model to enforce it against itself, and keeps no record of the
justifying call.

`daimon` does the opposite of GenericAgent's self-enforcement: it lets the model
claim whatever it likes and then **checks the claim in code**. The extraction
prompt demands `trust: "verbatim"` plus a copy-pasted quote and the id of the
message it came from; afterwards `verify_quotes` greps the quote against the
rendered transcript and demotes any item that misses, `sanitize_source_ids`
deletes citations the transcript cannot vouch for, and `ground_outcomes`
demotes a verbatim claim that asserts an outcome — merged, deployed, tests green —
without citing a tool result that shows it. Three of the atlas's harder
extraction problems get deterministic answers here, and the module comments are
unusually clear about what is left: *"verbatim matching certifies TRANSCRIPTION,
not truth"*. A related backstop is worth stealing on its own. Because trust
assignment is model-chosen, a "never do X" that the model paraphrases into prose
leaves no quote to verify and can soften undetectably later — so
`pin_imperatives` scans user turns for hard imperatives (must, never, don't,
always, forbidden) with a regex and force-pins any the model skipped, through the
same verification gauntlet. Soft modals are deliberately left to the model. It is
the only place in this atlas where a system defends specifically against
*constraint inversion*.

The research lineage adds two capture disciplines the practical systems mostly lost. `voyager` writes memory **only** when a critic verifies the environment reached the intended state, so a failed attempt produces reasoning input and no durable record — the strongest write gate in the atlas, available because the memory is a procedure. `generative-agents` scores every incoming memory for importance at write time and uses that score to schedule consolidation, rather than capturing indiscriminately and compacting on a timer.

### Consolidation

`honcho`, `hindsight`, `mastra-observational-memory`, and `verel` have the strongest visible consolidation stories. Honcho derives working representations from event streams. Hindsight creates/updates observations with source IDs and proof counts. Mastra reflects growing observation logs and can prepare the result asynchronously before activation. Verel clusters failures, induces candidate design rules and schemas, then requires promotion gates for verification. `agentmemory` separately consolidates important observations into versioned memories and optional semantic/procedural layers. `tencentdb-agent-memory` compiles L1 records into scene files and changed scenes into a persona.

`mem0` V3 is intentionally more append-oriented; consolidation is mostly dedupe and entity linking in the OSS path. `mempalace` consolidates operationally through dedup, closets, halls, tunnels, graph layers, and repair paths rather than by rewriting memories into summaries. `swafra` has no real consolidation worker or correction policy: ingestion adds cross-source edges, and a `superseded_by` loop exists, but old same-source chunks are removed before that loop can see them. `llm-wiki-memory` has a substantial opt-in, brain-only pipeline: per-leaf similarity clusters, hash/lesson-key/cosine dedup, optional LLM merge, deterministic staleness flags, optional LLM refresh, orphan archive, archived-body compression, cache pruning, and index rebuild. `rainbox` consolidates through claim supersession, rejection, expiry, profile selection, and eval/feedback loops rather than through background summarization. `letta` separates core and archival memory but does not make consolidation the central visible mechanism in the inspected files. `langmem` provides reflection hooks rather than a fixed consolidation policy. `engram` keeps a pragmatic local model: update topic keys, count duplicates, surface conflicts. `helm` splits the job in two and only one half is real: a weekly LLM pass is *instructed* to turn themes appearing in two or more episodes into durable facts, with no schema and no validator, while a deterministic pass counts word stems and writes any stem seen in three episodes as a fact whose value is literally `mentioned in 3 episodes (last: "…")`. That is term frequency in the vocabulary of learning — no subject, no predicate, no claim — stored at up to 0.9 confidence and injectable like anything else. A distiller that cannot produce a proposition should not be writing into the store the model reads.

`generative-agents` is the origin of the reflection loop that several systems
here descend from, and its trigger is still the most elegant: a countdown seeded
with `importance_trigger_max` is decremented by each new memory's poignancy, so
reflection fires on accumulated significance rather than on elapsed time, token
count, or message count. Compare `mastra-observational-memory`, which triggers on
token thresholds, and `claude-mem`, which triggers on lifecycle hooks — both are
proxies for "enough has happened" that the original measured directly. Its
weakness is that the budget is denominated in one-shot LLM importance judgments,
and its reflections are stored in the same undifferentiated pool as observations,
so reflections of reflections can drift with no visible boundary.

`moltis` adds a fifth instance of a guard that is now unmistakably a general
requirement: it exports session transcripts into its corpus only after
**sanitizing** them, joining `openclaw`'s envelope stripping, `holographic`'s
compaction-summary exclusion, `nanobot`'s internal-session filter, and
`cowagent`'s distillation rules. Any system that both generates text and
captures text will eventually capture its own.

Four systems in the atlas now call consolidation **dreaming**, arrived at
independently: `magic-context`'s dreamer subagent, `nanobot`'s Dream pass,
`cowagent`'s Deep Dream, and — under a different name for the same idea —
`metaclaw`'s replay. The convergence is not only nominal. All four run offline
on a schedule, read accumulated raw material, and write back a smaller, more
coherent durable layer; three of the four also emit a written record of what the
pass decided (a dream diary, a replay report, a delta-grounded commit). The
metaphor appears to be tracking a real architectural category: consolidation as a
separate, slower, auditable process rather than a step in the write path.

`magic-context` adds a consolidation trigger no other system here uses: its
dreamer subagent fires at threshold pressure **or at git commit boundaries**, on
the reasoning that a commit is the moment a coding agent's work becomes durable
and therefore the right moment to reconcile memory against the repository. The
same run verifies, maps, classifies, promotes primers, and sweeps orphans, under
a lease so two runs cannot overlap.

`redis-agent-memory-server` has the most careful consolidation guard in the
atlas: hash, ID, and semantic dedupe are separate passes, and the semantic path
runs `_semantic_merge_group_is_cohesive` before an LLM is allowed to collapse a
cluster — an explicit test that "similar" really is "same" before merging.
`byterover` approaches the same risk from the document side, diffing existing
against proposed content and counting only what a rewrite would delete.
`hermes-agent` is the outlier: consolidation is neither background nor
automatic, but a synchronous obligation handed to the model when a write would
exceed the character budget.

`daimon` is the one system here that ran the experiment everybody else assumes
the answer to. Its cross-session carry — folding the previous checkpoint's
unresolved items into the new one — was tried as an LLM re-emission and as an
exact copy in code, and the logbook records that re-emission **lost whole items
even from lossless input** while exact copy held perfect fidelity. Carry is
therefore code: copy the item, keep its birth stamp, expire by weight, dedup by
salient-term overlap. The rule it derives from that is sharper than the
measurement: a verbatim item's frozen text and quote *overwrite* a reworded
twin, because a pinned quote that consolidation is allowed to rephrase was never
pinned. Any system whose background pass regenerates existing memories through a
model should run the same A/B before trusting it.

Cognee's `memify`/`improve` pipelines enrich an existing graph, while its
session path bridges hot entries into permanent memory asynchronously.
Claude-Mem compresses batches into observations and session summaries but does
not merge them into a verified long-term belief model. A-MEM's
`consolidate_memories()` is only a reindex pass, not semantic consolidation.

### Retrieval

The repeated successful pattern is hybrid retrieval:

- semantic/vector search where embeddings exist;
- lexical/BM25/FTS for exact terms and identifiers;
- metadata filters for scope;
- reranking or rank fusion when quality matters.

`mem0` combines semantic, keyword, entity boost, and optional rerank. `hindsight` runs semantic, BM25, graph, and temporal arms, then uses task-specific fusion and cross-encoder reranking. `graphiti` searches edges, nodes, episodes, and communities with BM25, cosine, and BFS plus configurable RRF/MMR/cross-encoder recipes. `cognee` exposes lexical chunks, vectors, graph, triplet, summary, temporal, and hybrid modes, but the result contracts differ enough that each route needs separate evaluation. `basic-memory` fuses FTS5/tsvector with optional semantic chunks. `memos` can run vector or graph/BM25/reranker/reasoner pipelines depending on the mounted cube. `honcho` blends semantic, recent, and most-derived observations. `engram` uses FTS5 and topic keys. `mempalace` combines direct drawer vector search, BM25, metadata, closet boosts, neighbor expansion, and fallback paths. `swafra` uses compact but uncalibrated hybrid/graph fusion. `llm-wiki-memory` combines frontmatter prefilters, embeddings or lexical hashes, priority, and locality. `rainbox` hard-filters then blends vector, full-text, and entity signals. `verel` adds trust and confidence into ranking. `agentmemory` fuses BM25, vector, and graph arms with weighted RRF and per-session diversity. `tencentdb-agent-memory` fuses FTS and vector results with RRF or uses native Tencent VectorDB hybrid search. `claude-mem` selects Chroma semantic search for ordinary text queries and reserves metadata/semantic intersection for file lookup. `metaclaw` is the only system that treats its own ranking parameters as
learnable: retrieval mode, injected-unit cap, token budget, and weights live in a
`MemoryPolicyState` that is replayed against past turns and replaced only on
non-regression. `genericagent` has no ranker at all — a ≤30-line index of
"existence pointers" lets the model recognize that knowledge exists and open the
file itself, which is the cheapest retrieval architecture here and fails silently
when a trigger word is missing. `nanobot` likewise has no retrieval: its durable
files are small enough to always inject. `cowagent` pairs vector and FTS5 search
over chunked files while injecting `MEMORY.md` wholesale.

`waku-agent` inverts the question everyone else asks. Rather than ranking
better, it decides per turn whether to retrieve at all, and its stated reason is
not cost but quality: irrelevant memory in the prompt bends the answer. Almost
nothing else in the atlas can abstain. `daimon`'s proactive path is the one
comparable case and it arrives from the opposite direction — not a judgment
about relevance but three cheap lexical gates, each defaulting to silence: an
unknown project, a prompt with fewer than two salient terms, or a candidate
session sharing fewer than two *distinct* terms all return nothing. The comment
explains why the shared-term count is per session rather than per item: a
multi-topic prompt splits its terms across items, and a per-item count silenced
exactly the sessions the feature existed to surface. Abstention by budgeted
noise gates is weaker than abstention by judgment, and it is far cheaper than
either ranking or asking a model.

`loongflow` breaks a different assumption: every other system here ranks
deterministically and takes the top *k*. Its evolutionary memory selects a
remembered solution by **Boltzmann sampling over scores**, at a temperature set
by `_adaptive_temperature_by_diversity` from a sampled measure of how varied the
stored population currently is — blending in 20% of the previous temperature so
the control signal does not oscillate. A converged population gets a higher
temperature and flatter selection, which readmits weaker solutions and restores
variety. This is only defensible because recall there feeds exploration rather
than belief; asked the same question twice it may answer differently, which is
the correct trade for a search loop and the wrong one for facts about a user.

`hipporag` is the one system here that does not rank at all in the usual sense: it seeds a personalization vector from query-linked entities plus a weak dense prior, then reads relevance off a Personalized PageRank diffusion across the whole graph. `generative-agents` established the multi-signal shape everything else refines — normalized recency, relevance, and importance combined in a weighted sum — though the specific weights (`gw = [0.5, 3, 2]`, with two earlier settings left commented out) are hand-tuned with no ablation in the repository, and its recency decays by chronological *position* rather than elapsed time. `voyager` retrieves top-5 by vector similarity over generated descriptions and returns executable code, with scores computed and then discarded so there is no relevance threshold. `openviking` runs directory-recursive dense plus sparse retrieval with level filters, per-type quotas, optional reranking, and a hotness blend. `redis-agent-memory-server` pairs vector search with a recency reranker using separate half-lives for last access and creation. `holographic` fuses FTS5, Jaccard, and HRR cosine, then multiplies by trust — and silently reweights to lexical-only when NumPy is absent while still reporting itself as available. `openclaw`'s reference backend is vector-only, which sits awkwardly with a category set dominated by preferences, entities, and decisions. `a-mem` is vector-only despite hybrid wording. `mastra-observational-memory` is the deliberate exception: its primary path is sequential observations plus a recent raw tail, with semantic observation retrieval optional. `daimon` is the deliberate exception in the other direction: **no embeddings exist anywhere in the codebase**, and its index is disposable by contract — any doubt about the SQLite file resolves to a full rebuild from the JSON, with no incremental upsert path, on the stated principle of "correctness over cleverness". The cost lands exactly where you would expect, and the project measures it rather than asserting it away — see [Evals/Tests](#evalstests).

### Context Injection

`letta` and `mastra-observational-memory` have the deepest runtime prompt integration. Mastra removes observed raw messages, injects active observations as system context, retains a recent tail, and adds a continuation reminder. `claude-mem` automatically renders a project-scoped chronological timeline, showing only a bounded subset of observations in full. `rainbox` injects an operator profile block and hybrid memory context and records what was injected. `verel` has the safest visible recall renderer: recalled memory is token-budgeted and fenced as untrusted data. `mempalace` has a four-layer stack. `basic-memory` builds graph context through MCP while leaving final prompt placement to the client. `agentmemory` assembles pinned items, profiles, lessons, summaries, and observations within a token budget; its smart search separately supports compact-first expansion. `tencentdb-agent-memory` separates dynamic L1 recall from stable scene/persona context and adds navigable short-term offload maps. `cognee`, `graphiti`, `hindsight`, and `memos` return structured recall/context to integrations. `swafra` exposes unbounded `get_context`; `llm-wiki-memory` injects session work context; `supermemory` emits profile text; `engram` has MCP context tools; `honcho` exposes working representations. A-MEM leaves injection entirely to its caller.

`hermes-agent` takes the most distinctive position in this set: curated memory is rendered into the system prompt **once, at session start, as a frozen snapshot**, and mid-session writes deliberately do not update it, so the provider's prefix cache survives the whole session. That choice is economic rather than epistemic, but it drives a real safety decision — because a poisoned entry would persist for the entire session and beyond, Hermes scans memory content against its broadest threat-pattern set at *write* time. This is the mirror image of Verel's and RainBox's read-time fencing, and the trade is instructive: write-time filtering is cheaper and cache-friendly but is a denylist, while read-time fencing costs tokens every turn and does not depend on pattern coverage. `holographic` does neither, injecting its top five stored facts into the prompt unfenced. `helm` is worse than unfenced: its eight recalled facts are prefixed *"MEMORY — use these, never contradict them"*, and the format is `- (kind) key: value` with the confidence, evidence count and source all dropped — so a preference the background loop guessed once from a transcript at 0.7 and a fact the owner stated outright arrive as the same kind of sentence, under an instruction not to argue with either. It also runs both injection channels at once: a generated `INDEX.md` imported through `CLAUDE.md` (stable between background ticks, and the only place a confidence figure survives) plus a per-turn recall block appended to the system prompt, which means the system-prompt prefix differs on every turn and the prefix cache is invalidated by construction. Hermes pays tokens to keep the prefix frozen; Helm gives the prefix up for free, and the cheaper arrangement — stable index in the prefix, query-specific hits in the user turn — is one line away.

`daimon` shares Hermes's session-start-snapshot shape but makes the artifact the
product: a "while you were away" briefing ordered by *what to verify first*,
each line tagged `✓ verbatim` or `~ inferred`, capped at 3,000 estimated tokens.
Two details generalize past the format. First, budget pressure is spent in the
right order — long *inferred* items are truncated in place before anything is
dropped, and verbatim text is never rewritten to fit, only dropped whole and
announced, because a guarantee that survives until the context gets tight is not
a guarantee. Second, the optional LLM re-render is **post-validated**: every
verbatim quote must survive the generated prose intact (whitespace-normalized),
and any loss falls back to the deterministic render. That is the
[structural-loss guard](#structural-loss-guard-on-generated-rewrites) applied to
context assembly rather than to consolidation, and it is the cheapest way to let
a model prettify memory without letting it edit it.

### Correction

This is where systems diverge sharply.

`verel` and `rainbox` have the strongest visible epistemic correction semantics in this set. `verel` has explicit trust states and rejected tombstones. `rainbox` has governed atomic correction, conflict detection, and tombstones that prevent model-write laundering. `engram` has conflict candidates and judgment tools. `mempalace`, `llm-wiki-memory`, `letta`, `mem0`, `honcho`, `supermemory`, and `langmem` expose increasingly operational forms of update/supersession without the same trust model.

`helm` has the shape of temporal correction and none of the temporality: a rewrite of an existing `(kind, key)` stamps `expired_at` on the old row, inserts the new one, and `history <key>` returns the chain — but `valid_from` is only ever written as the insert timestamp, so validity time is record time under a different name, and no caller can say "this became true in March". The instructive part is what the soft delete costs. Active rows are defined by the predicate `expired_at IS NULL`, enforced by a *partial* unique index that constrains writes and leaves every `SELECT` to remember the filter itself — and three readers do not. The agent's own autonomy setting is read back without it and therefore returns the stale pre-supersession value; the distiller's lookup can write onto a dead row; the dedupe pass can delete superseded history and sum retracted evidence onto the survivor. Any system that expresses correction as a nullable column needs a view or an accessor, because "remember the predicate" is not an invariant.

Graphiti closes a fact's validity interval and retains history, which is the strongest temporal correction model here, but it does not mark claims verified/rejected. Hindsight rewrites or merges observations while retaining source/history fields. Basic Memory makes correction a human-readable file edit followed by transactional reindexing. Mastra replaces only the observation range covered by a reflection. MemOS correction varies by module and therefore lacks one consistent semantic contract.

`agno` is the corpus's one *judged* supersession. Where `agentmemory` compares
strings and `helm` compares keys, Agno asks a model whether a new fact and an
existing one can both be true, and acts only on a verdict above a configurable
threshold — keeping both facts when the answer is weak, so the default failure
is a contradictory store rather than a destroyed value. `retire_fact` stamps
`superseded_at` and `superseded_by`, where the latter holds the replacement's
id, or the literal `"forgotten"`, or `"superseded"` when several new facts
jointly displaced one, and `live_facts()` filters retired rows out of everything
that renders. It is record-keyed like every supersession here, so re-extraction
walks past it, and it is undermined from an unexpected direction: the older of
Agno's two memory subsystems exposes `optimize_memories`, which summarises every
memory a user has into one paragraph and then calls `clear_user_memories`
before writing it back, with `apply=True` as the default. One subsystem takes
care to keep a replaced value; the other has an HTTP route that discards all of
them and reports the token saving.

`agentmemory` versions similar memories, but the Jaccard threshold can silently
supersede a conflict without an explicit judgment. `tencentdb-agent-memory`
offers internal merge/delete paths and editable generated files, but no
first-class agent/user correction or forget operation.

`magic-context` introduces a correction mechanism the atlas has not seen before:
memories are **re-verified against the artifacts they describe**. Each memory is
mapped to backing files and carries its own `verified_at`; when git reports a
committed change, an uncommitted edit, or a deletion touching a mapped file since
that memory's last verification, the memory re-enters verify scope. Lifecycle
state (`active|permanent|archived`) and verification state
(`unverified|verified|stale|flagged`) are separate columns, which is the split
Verel argues for and most systems collapse. The design is also explicit about its
own limits: file-independent memories are excluded from verification entirely and
handed to curation and age decay, because they "describe external behavior and
cannot be checked against local code". Its remaining gap is the familiar one —
supersession without a rejected-value tombstone, so an archived memory can be
re-derived from retained history.

`daimon` is the second implementation of that re-verification idea and extends
it in two directions. Downward, into code: `daimon anchor <file> <symbol>` pins
an item to a Python symbol, fingerprinted as a SHA-256 of `ast.dump` of the
definition node, so the anchor is stable under reformatting and comment edits
and moves only on a structural change — and drift is reported in the next
briefing. Outward, into the world: an opt-in `worldcheck` pass spot-checks a carried claim
against whatever it names — a ticket state, a source path, a branch, a pinned
dependency — under one sub-second aggregate budget and one probe cap, skipping
silently on any failure so a briefing can never block on a slow check. Only the
ticket class leaves the machine; the other three are answered from disk, which
is what lets the pass work in a project with no remote at all.

Two refusals define its edges, and both are the same rule: **when a probe might
answer about a different subject, skip rather than answer.** A reference that
could name another repository is not probed, and a path resolving outside the
project root is not probed, because in each case the reply would describe someone
else's checkout. A verification that can be wrong about *which thing it checked*
is worse than no verification, and this is the only system here that says so in
code.

Three of its correction decisions generalize. A machine-detected supersession is
written as `supersede-candidate:<new-id>` and is **live by construction** — a
guess may annotate a briefing with a confirm/reject command but may never
suppress anything, and the liveness rule enforces that rather than trusting
callers to remember it. Re-opening a resolved item requires *evidence*: either
the item's code anchor still checks out live, or an explicit `--evidence`
string, on the reasoning that re-stamping without one would mark an unchecked
claim verified. And staleness is measured honestly — a carried item restated by
a fresh checkpoint is not corroborated, because both statements descend from the
same original extraction, so effective age runs from the last time code or a
human actually checked it.

The six systems added from the Hermes/OpenClaw ecosystem are uniformly weak
here, and usefully so: none of `holographic`, `hermes-agent`, `openviking`,
`redis-agent-memory-server`, `byterover`, or `openclaw` has a rejected-value
tombstone, so in every one of them a corrected or deleted memory can be
re-derived from retained material with nothing to stop it. `byterover` is the
partial exception in an unexpected place — its `detectStructuralLoss` /
`resolveStructuralLoss` pair is the only mechanism in the atlas that guards a
*rewrite* rather than a claim, counting exactly what an LLM curation pass would
delete and merging the loss back in. `holographic` inverts the usual failure:
its `contradict` action surfaces contradictions as an ordinary query, but only
reports them, with no supersession or review workflow attached, and its docstring
claim that "no other memory system does this" is not accurate within this atlas.

A specification for measuring any of this — the shapes a contradiction can take, and the four things worth scoring separately — is in [the contradiction test](../benchmarks/#contradiction-test).

**Memanto closes the loop the rest of this section leaves open.** Every other
contradiction mechanism here detects and stops — Gini's `conflicted` status,
MateClaw's `ContradictionDetector`, Holographic's `contradict` query, all of them
produce a flag and no disposition. Memanto's scheduled pass writes a dated JSON
report typed as `contradiction | update | duplicate | conflict`, and a human
resolves each entry through the CLI or web UI with one of five actions. Two are
absent everywhere else: **`keep_both`**, which says the disagreement is not a
contradiction — the right answer whenever two memories differ because they cover
different times or scopes — and **`manual`**, where a person writes the
reconciling content, enforced by a validator that refuses the action without it.
The model's `recommendation` vocabulary is deliberately narrower than the
operator's action set, so the proposal does not bound the decision. What it still
lacks is the tombstone: `remove_both` deletes, and the next night's extraction is
free to bring the content back.

`memora` contributes the one procedural idea this section has been missing. Its
supersession pass runs in three phases — candidate pairs by embedding
similarity, LLM classification, then edge creation — and the mutating phase is
governed by `dry_run: bool = True`. **Reporting is the default; changing memory
is opt-in.** Every other correction mechanism here acts immediately, so an
operator learns the blast radius of a sweep only afterwards. Memora also
classifies each pair against a defined vocabulary — `a_supersedes_b`,
`b_supersedes_a`, `duplicate`, `related`, `contradicts`, `neither` — rather than
thresholding similarity, presents the pair neutrally as A and B so the model
chooses the direction rather than confirming an assumed one, and writes
`contradicts` as an **edge between two named memories** instead of a flag on one
row, which makes it queryable in a way Gini's `conflicted` status is not. The
gap is the usual one: supersession hides a memory from retrieval without
recording the rejected value, and this is a system that ingests documents and
images, so re-ingestion is a realistic path back.

`mirix` is the sharpest illustration of why a policy has to be a mechanism. Its
`auto_dream` agent runs against the whole store under a prompt that says: "Resolve
conflicts conservatively, preferring the more recent or more detailed item. If
uncertain, keep both and record the discrepancy." That is close to Memanto's
`keep_both` — the best correction rule in this atlas — except Memanto's is an enum
a validator enforces and MIRIX's is a sentence a model may skip. The tool the
sentence governs is `episodic_memory_replace`, which hard-deletes. So the atlas
now has the same idea implemented twice, once as a constraint and once as a
suggestion, and the difference is whether a user's correction survives the night.

`memobase` shows the failure without the good intention: an LLM is handed the
current memo and the new information and returns `APPEND`, `ABORT`, or
`UPDATE\t[UPDATED_MEMO]` — the last of which overwrites the string. Both ends
lose information silently. `ABORT` discards the incoming fact with no record it
was considered, and `UPDATE` discards the outgoing one, under a prompt that
explicitly invites the model to decide "whether there are other parts of the
current memo that can be simplified or removed".

Cognee can forget and rebuild derived projections from retained source, but its
ontology-valid, source-attributed graph facts still lack candidate/rejected
epistemic state. Claude-Mem offers exact deletion and feedback but no durable
rejection mechanism preventing an observation from being regenerated. A-MEM
mutates neighboring note metadata directly and has no correction chain.

The gap is visible from outside this atlas too. TeleAI's
[Awesome-Agent-Memory](https://github.com/TeleAI-UAGI/Awesome-Agent-Memory)
survey runs to about 1,500 lines across seventy sections and covers mem0, Letta,
Zep, Graphiti, Cognee, MemOS, and HippoRAG — every widely-cited system, and all
of them reviewed here. It does not list `verel`, `rainbox` or `daimon`, the only
three systems in this atlas that carry a rejected-value tombstone. That is not a
criticism of the survey; all three are small and obscure. It does mean
correction-focused memory is under-surveyed as well as under-built: a reader
working from the standard reading list would not encounter the mechanism at all.

The stronger version of that observation is not about which repositories get
listed. It is about vocabulary. *Memory in the Age of AI Agents*
([arXiv:2512.13564](https://arxiv.org/abs/2512.13564), v2, 13 January 2026) is
107 pages by 47 authors and is the most comprehensive description the field has
written of itself. Its §5.2.2 traces external memory update as a clear
progression — destructive replace and delete in MemGPT, D-SMART and Mem0ᵍ; then
Zep annotating conflicting facts with invalid timestamps instead of deleting
them; then dual-phase online/offline reconciliation; then reinforcement learning
over *whether* to update at all. Every step improves the decision. None of them
records the value that lost, and re-assertion by the next extraction pass is not
named in the section.

The term counts make the point without interpretation. Over a text extraction of
the full paper, `memory` appears 1,570 times, `forget*` 52, `conflict` 28,
`audit*` 5, `provenance` 3, `deletion` 2, `bi-temporal` 1. `tombstone`,
`rejected`, `tenant` and `negative` each appear **zero** times — the last of
those an ordinary English word that a 107-page technical survey manages never to
use, which is what an absent concept looks like from the outside. Meanwhile its
own trustworthy-memory frontier (§7.7) calls for "access control, verifiable
forgetting, and auditable updates", and for memory that is "version-controlled,
auditable, and jointly managed by agent and user": four of this atlas's seven
capability columns, stated as open research directions. The field is asking for
the property and has not yet named the mechanism.

Read that as corroboration rather than as a scoop. The comparison in full,
including where the survey covers ground the atlas does not — parametric and
latent memory, RL-learned memory management, multimodal — is in
[the working note](https://github.com/neoneye/agent-memory-atlas/blob/main/notes/2026-07-29-memory-survey-forms-functions-dynamics.md).

**The clearest external statement of the gap comes from security research rather
than from memory research.** *A Survey on Long-Term Memory Security in LLM
Agents* ([arXiv:2604.16548](https://arxiv.org/abs/2604.16548), v2, 11 June 2026,
by the MemOS group at MemTensor with SJTU) reaches this atlas's conclusions from
an entirely different starting point: what an attacker can do to a writable
store. Its §5 proposes **Verifiable Memory Governance**, five primitives it
argues a long-term-memory system must provide. Four of them are this atlas's
capability columns under other names:

| VMG primitive | The atlas's name for it |
| --- | --- |
| Write Authorization — every entry attributable to an authenticated source, passing an explicit check before consolidation | the [governed write gateway](../patterns/governed-write-gateway/) pattern |
| Provenance Visibility — every entry carrying queryable, lineage-complete provenance through summarization and merging | `audit_log`, and the provenance chain the [evidence-before-belief](../patterns/evidence-before-belief/) pattern needs |
| Principal-Scoped Retrieval — retrieval returns only entries whose scope includes the querying principal | `scope_enforced`, almost word for word |
| Rollbackability — versioned snapshots sufficient to restore a known-safe prior state | no column; the [append-only memory audit](../patterns/append-only-memory-audit/) pattern is the nearest |
| **Verified Forgetting** — after a deletion, the system can demonstrate by post-deletion membership tests that the content is unrecoverable "from any substrate — including raw logs, compressed summaries, vector indices, and propagated copies" | the question this atlas asks of every system. Its [benchmarks page](../benchmarks/) said nothing measured it until 30 July 2026, when [ForgetEval](../systems/lethe/) was read — 385 adversarial cases scoring `supersede`, `release` and `purge` across six systems. The survey marked Verified Forgetting "no existing literature"; Lethe implements it with signed receipts and ships the benchmark |

Verified Forgetting is given a formal definition — a bound ε on the probability
that any adversarial probing query re-exposes deleted content — and the paper's
own dependency diagram marks its deployment status as **"no existing
literature"**, the only one of the five so marked. Rollbackability is "largely
absent"; Principal-Scoped Retrieval "early-stage".

That is the sharpest form the atlas's central finding has taken. A survey
written by the authors of a system reviewed here, working from threat models
rather than from repositories, independently derives the capability the atlas
counts, defines it more precisely than this atlas does, and reports that nobody
has published it. Meanwhile three repositories here implement a value-level
tombstone — the mechanism Verified Forgetting requires — and none of the three
has a paper. The literature and the code have each found half of it.

The "propagated copies" clause has a partial answer too, from further outside the
literature than the tombstones are. [RisuAI](../systems/risuai/) stores on every
generated summary the set of chat-message ids it was derived from, and drops the
summary when any one of those messages no longer exists — deletion propagating
from a source into the artifacts computed from it, which is the substrate
Verified Forgetting names and the one summarization systems usually leave
standing. It arrived in that codebase on 2024-05-23, in the generation after a
summarizer that kept no link at all between a summary and its sources. It is not
Verified Forgetting: nothing records that the deletion happened, and the next
overflow will summarize the surviving messages again. But it is the mechanism the
definition asks for, implemented, in a roleplay client, with no test asserting it
holds.

And the vocabulary gap survives even here: over this survey's text, `provenance`
appears 25 times, `rollback` 24, `forget*` 25, `audit*` 13, `unlearn` 9 — and
`tombstone`, `rejected`, `negative` and `tenant` **zero** times each, exactly as
in the 107-page survey. The property is now named. The mechanism still is not.

**The security side has now built the mechanism twice and made it durable
neither time.** Both artifacts capture the rejected value and then fail to keep
it, in ways that only reading the callers reveals:

- **[A-MemGuard](https://github.com/TangciuYueng/AMemGuard)** (at
  [`dd92f7ff21b9a904a703141be3d5b80170e57228`](https://github.com/TangciuYueng/AMemGuard/commit/dd92f7ff21b9a904a703141be3d5b80170e57228),
  paper [arXiv:2510.02373](https://arxiv.org/abs/2510.02373)) names this atlas's
  failure mode more precisely than the memory literature does: a poisoned record
  triggers an error whose "corrupted outcome is stored as precedent", which
  "amplifies the initial error and progressively lowers the threshold for
  similar attacks". Its defence is exactly the right shape. Consensus validation
  splits retrieved memories into consistent and inconsistent; each inconsistent
  one gets its reasoning chain written back onto the memory entry as a `lesson`;
  and later retrievals inject those lessons under a header instructing the model
  to "AVOID the operations that previously led to failure". That is a
  rejected-value record consulted on the read path. It is **never written
  back**: `main.py` loads the memory pool read-only with `json.load`, the only
  `json.dump` is the results file, and the one call to `update_memory` is
  commented out. Every lesson lives in a Python dict for one run and dies with
  the process, so the next run meets the same poisoned record with no memory of
  having been fooled by it. The defence against a self-reinforcing error cycle
  does not itself survive the cycle.
- **OWASP Agent Memory Guard** quarantines each blocked value into a dict that
  nothing ever reads back — described in [§1](#not-in-scope-conversation-window-management).

Neither is a defect in its own terms: one is a research harness for scoring an
attack, the other a layer expecting you to bring the store. Together they make
the point that the missing piece is not the idea. Both projects independently
reached "keep a record of what was wrong and check it before acting", and in
both the record is in-process. The gap between that and a tombstone is
persistence, and persistence is the part nobody has treated as the interesting
half.

### Forgetting

Visible deletion varies from hard API deletion to lifecycle state:

- `mem0`: delete APIs and expiration metadata.
- `langmem`: delete tool operation.
- `honcho`: soft-delete style document handling.
- `engram`: deleted timestamps/sync mutation semantics.
- `mempalace`: delete drawer, delete by source, dedup, repair, backend delete; deletion must account for drawers, closets, KG, backups, sync, and remote backends.
- `swafra`: exact source deletion from chunks/sources and source-owned edges; global cross-session edges survive and become dangling records.
- `llm-wiki-memory`: exact archive/re-enable and hard working-tree delete; embedding/index cleanup follows, but private git history can retain deleted or truncated content.
- `rainbox`: reject claim (tombstones the value in `MemoryRejectedValue`), supersede claim (also tombstones), expire claim, prune embeddings; rejected/superseded evidence remains inspectable; tombstoned values block future model re-assertion (anti-laundering).
- `letta`: block/file/passage update paths, archival insert/search visible; deletion depends on manager APIs outside the key path.
- `supermemory`: forget API in MCP/client; semantic fallback delete is powerful but risky.
- `verel`: rejected tombstones, TTL/volatile/stale pruning, and protection for verified/rejected/pinned records.
- `helm`: two hard deletes and one soft. `forget <id>` removes the fact and its cached vector; the nightly consolidation prunes any active row below 0.05 confidence that was never corroborated; supersession is the only exit that keeps the row. Deletion is therefore genuinely irreversible — good for a private local store, and the reason nothing stops the same reflection loop re-deriving a pruned fact from the same episodes tomorrow. The exposure is specific: the hot-path regex that captures an explicit "remember that …" mints a fresh timestamped key each time, so those rows never corroborate, never supersede, and sit on the fastest path to a silent prune.
- `daimon`: `forget` deletes the item from the live checkpoint, appends a `forgotten:<content-hash>` event carrying a hash and never the text, re-mints the checkpoint's signed receipt, and — because item ids are a hash of the item's own text — deletes every row with that id from the search index across *all* historical checkpoints on the next rebuild. Weight-based expiry from carry is the softer path: an item below the floor simply stops being carried forward.
- `hindsight`: bank/document/memory operations plus cascading schema relations; derived observations must remain consistent with source changes.
- `graphiti`: episode removal and edge invalidation preserve temporal history and source support.
- `mastra-observational-memory`: clear/clone observational records and covered-range replacement.
- `memos`: module-specific hard/soft deletion across graph, vector, cache, dump, and model artifacts.
- `basic-memory`: canonical note deletion followed by entity, graph, full-text, semantic, and materialization cleanup.
- `agentmemory`: explicit forget, TTL/retention, and search-index cleanup.
- `tencentdb-agent-memory`: internal cleanup and record deletion, but no
  first-class user-facing forget tool.
- `cognee`: exact item, dataset, all-user, or memory-only deletion across source
  and projection stores.
- `claude-mem`: exact canonical-row deletion coupled to cloud tombstone
  enqueue; synchronized deletes fail closed when replication identity is
  unavailable.
- `a-mem`: exact local delete, but incoming links are not cleaned and the
  dictionary/Chroma mutation is not atomic.
- `holographic`: exact `remove`, but the practical forgetting mechanism is
  feedback — three unhelpful ratings drop a fact below the default `min_trust`
  floor of 0.3, making it permanently unreachable with no tombstone and no
  record that suppression occurred.
- `hermes-agent`: substring-addressed `remove` plus budget-driven eviction the
  model performs under pressure; nothing logs what was dropped.
- `second-me`: the most thorough deletion cascade here — the memory row, the
  document embedding, every chunk embedding, every chunk row, the document row and
  the file — and it stops there. The versioned biography derived from that document
  stays, and the model fine-tuned on data synthesized from it keeps what it
  learned. This is the atlas's one case where "delete" reaches the retrieval layer
  and cannot reach the belief.
- `mirix`: `episodic_memory_replace` is a loop of `hard_delete` followed by a
  loop of `insert`, so a correction destroys the row rather than superseding it —
  and the periodic `auto_dream` pass loads up to 500 items per memory type and
  can do the same thing unprompted. The base class has a soft-delete flag; the
  memory path does not use it.
- `memobase`: profile correction is an LLM rewriting the memo string in place
  (`UPDATE\t[UPDATED_MEMO]`), with no prior value kept and no check that the
  rewrite preserved what the old memo held.
- `openviking`: hotness decays reachability on a single seven-day half-life for
  every memory kind.
- `redis-agent-memory-server`: the most developed policy in the atlas —
  `select_ids_for_forgetting` combines TTL and inactivity so a recently-used
  memory survives its nominal age unless it passes a hard-age multiple, honours
  pinning and per-type allowlists, and prunes to a budget by a recency composite
  with separate half-lives for last access and creation.
- `byterover`: `maxMemories` cap with no eviction policy visible in the
  inspected modules.
- `openclaw`: exact agent-scoped delete, undermined by auto-capture, which can
  restore the same content from a later matching message.

- `magic-context`: archive plus `supersededByMemoryId` and `mergedFrom` lineage,
  with age decay owning memories that cannot be verified; no tombstone.
- `pi`: no memory to forget; deleting a session removes its JSONL file.
- `metaclaw`: `superseded_by` lineage plus `expires_at` TTL; `archived` status,
  no rejected state.
- `nanobot`: Dream edits durable files surgically under git; history is bounded
  at 1,000 entries, dropping oldest processed entries without discarding pending
  Dream input.
- `cowagent`: distillation prunes on a stated rule set, with recency winning
  conflicts and no tombstone.
- `genericagent`: forgetting is constrained by policy — verified configs,
  pitfall guides, and critical paths must never be dropped during garbage
  collection, only compressed or migrated to a deeper layer.

Semantic forgetting is an antipattern unless there is explicit user review or exact ID targeting.

Deletion is also where pluggable memory breaks down. Both host runtimes in the atlas — `hermes-agent` and `openclaw` — define a memory-provider contract with **no deletion hook and no scope parameter**, so a user's "forget that" has no defined path into whatever backend is mounted. `holographic` shows the resulting hazard concretely: it mirrors the host's built-in memory additions into its own store but implements only the `add` action, so removing an entry from `MEMORY.md` leaves the mirrored copy behind indefinitely.

### Cross-Session and Cross-Agent Persistence

`memory-engine` has the most developed access model in the atlas, and it is the only one where an **agent is a principal** rather than a process acting with someone else's authority. Grants are `(space, principal, ltree path, level)` over read/write/owner; `core.build_tree_access` materializes the caller's grants into a jsonb passed *into* the search SQL, so visibility and ranking are one query rather than a post-filter that would make `LIMIT` mean different things for different callers. Delegation is safe because `agent_tree_access` clamps an agent to `least(agent, owner)` at every path — a member may grant their own agents freely, and an over-grant clamps down instead of escalating. Row-level security was tried and rejected for performance, with the reason recorded beside the replacement and a benchmark query retained to keep watching it. `honcho` has the richest multi-actor model: workspace, peer, session, collections, and derived representations. Cognee authorizes datasets per user and can isolate supported backend stores per user/dataset. Claude-Mem scopes local reads by project/worktree, session, and platform source, while its newer server model adds teams and API keys. Hindsight isolates memory banks and database schemas. Graphiti uses `group_id`. Mastra scopes observations to a thread or resource. MemOS registers cubes to users. Basic Memory uses project/workspace/tenant boundaries with per-project local/cloud routing. `agentmemory` supports project/session keys and an opt-in isolated agent mode, but defaults to shared agent scope. TencentDB records session identity but does not turn it into a general tenant boundary; one persona per data directory is especially important operationally. `supermemory`, `mem0`, `rainbox`, `engram`, `mempalace`, `llm-wiki-memory`, `verel`, `letta`, and `langmem` each expose explicit boundaries. `openviking` carries tenant and permission filtering into every retrieval call and physically separates memory about the user from memory about a peer under `peers/<peer_id>`. `redis-agent-memory-server` scopes by namespace, user, and session behind auth. `openclaw` has a single `agentId` axis but defends it unusually well, composing scope and user filter into one predicate "so scope cannot be lost" and scoping deletes the same way. `hermes-agent` isolates by profile but has no project or room boundary within one. `magic-context` has a three-level lattice — `project`, `ecosystem`, `universe` — plus a `shareable` flag governing what may cross a boundary, with project identity resolved to the git root and a rekey map for when a repository moves. `pi` has no scope because it has no memory. `byterover` scopes only by storage directory, and `holographic` has no scope at all — it describes itself as a single-user store, with `category` serving as partitioning rather than access control. A-MEM, Swafra, and Holographic remain the outliers with effectively global local corpora. `daimon` scopes by a slug munged from the project's working directory, and the rule it derives is worth copying: callers that *display* what they read may fall back to another bucket, callers that *persist* what they read may not — carry always reads with `fallback=False`, so a cross-project pointer can never enter durable state. When the display fallback does fire, the foreign body is suppressed and only a header appears, on the stated reasoning that one warning line above a hundred foreign lines does not read as a warning. Its team mode is the atlas's cleanest answer to conflict-free sharing: only immutable per-author files sync through a private git sidecar, no mutable pointer ever lands there, teammates' items stay attributed and are never merged into yours, and a non-fast-forward is surfaced as a warning that repairs nothing.

## 4. Implementation Hotspots by Repo

### Memory Schema

- `mem0`: `mem0/mem0/configs/base.py`, payload construction in `mem0/mem0/memory/main.py`.
- `langmem`: store item shape is application-defined; see `langmem/src/langmem/knowledge/tools.py` and schema extraction in `langmem/src/langmem/knowledge/extraction.py`.
- `honcho`: `honcho/src/models.py`.
- `engram`: SQLite schema in `engram/internal/store/store.go`.
- `mempalace`: drawer metadata in `mempalace/mempalace/miner.py` and `mcp_server.py`; backend contract in `mempalace/mempalace/backends/base.py`; KG schema in `mempalace/mempalace/knowledge_graph.py`.
- `swafra`: implicit source/chunk/edge dictionaries and JSON files in `swafra/swafra/engine.py`.
- `llm-wiki-memory`: leaf and metadata types in `llm-wiki-memory/scripts/lib/types-metadata.mjs`; rendering in `wiki-render.mjs`; layout contracts in `examples/layouts/*/layout.yaml`.
- `rainbox`: `MemoryClaim`, `MemoryEvidence`, `MemoryEmbedding`, `RetrievalEvent` in `rainbox/source/db/models.py`.
- `letta`: `letta/letta/schemas/memory.py`, `letta/letta/orm/block.py`, `letta/letta/orm/passage.py`.
- `supermemory`: `supermemory/packages/validation/schemas.ts`, `supermemory/packages/validation/api.ts`.
- `verel`: `verel/src/verel/memory/view.py`.
- `hindsight`: `hindsight-api-slim/hindsight_api/engine/memory_engine.py` and Alembic `memory_units`/document/link migrations.
- `graphiti`: `graphiti_core/nodes.py` and `graphiti_core/edges.py`.
- `mastra-observational-memory`: core `ObservationalMemoryRecord` plus `packages/memory/src/processors/observational-memory/types.ts`.
- `memos`: `src/memos/memories/textual/item.py`, activation/parametric item modules, and `mem_cube/general.py`.
- `basic-memory`: `src/basic_memory/models/knowledge.py` and `markdown/schemas.py`.
- `agentmemory`: `src/types.ts` and state scopes in `src/state/schema.ts`.
- `tencentdb-agent-memory`: `src/core/record/l1-writer.ts`, `src/core/store/types.ts`, and `src/core/store/sqlite.ts`.
- `cognee`: `cognee/infrastructure/engine/models/DataPoint.py`, graph edge/triplet models, and relational dataset/data/session models.
- `claude-mem`: canonical tables and migrations in `src/services/sqlite/SessionStore.ts`; future server model in `src/storage/sqlite/schema.ts`.
- `a-mem`: `MemoryNote` in `agentic_memory/memory_system.py`.
- `hipporag`: graph and node construction in `src/hipporag/HippoRAG.py`; config defaults in `utils/config_utils.py`.
- `magic-context`: `packages/plugin/src/features/magic-context/memory/types.ts`; schema in `migrations.ts`.
- `metaclaw`: `metaclaw/memory/models.py` (`MemoryUnit`, `MemoryType`, `MemoryStatus`); policy in `policy_store.py`.
- `nanobot`: no schema; durable files plus `history.jsonl` lines in `nanobot/agent/memory.py`.
- `cowagent`: `chunks` table in `agent/memory/storage.py`.
- `genericagent`: no schema; layer contract in `memory/memory_management_sop.md`.
- `pi`: session entry types in `packages/agent/src/harness/types.ts`; no memory record exists.
- `voyager`: `skills[name] = {code, description}` in `voyager/agents/skill.py`.
- `generative-agents`: `ConceptNode` in `persona/memory_structures/associative_memory.py`; weights in `scratch.py`.
- `holographic`: `_SCHEMA` in `plugins/memory/holographic/store.py`; HRR encoding in `holographic.py`.
- `hermes-agent`: `MemoryStore` in `tools/memory_tool.py`; provider contract in `agent/memory_provider.py`.
- `openviking`: `MemoryData` / `MemoryTypeSchema` in `openviking/session/memory/dataclass.py`; level field in `openviking/storage/collection_schemas.py`.
- `redis-agent-memory-server`: `V0/agent_memory_server/models.py`.
- `byterover`: `src/agent/core/domain/memory/types.ts`; `ContextData` in `src/server/core/domain/knowledge/markdown-writer.ts`.
- `openclaw`: `MemoryEntry` in `extensions/memory-lancedb/lancedb-store.ts`; categories in `config.ts`.
- `daimon`: the item-field table in `plugin/daimon_briefing/schema.py`; checkpoint shape in the `SERIALIZE_SYS` prompt in `serializer.py`; on-disk layout and id stamping in `store.py`.
- `helm`: `facts`, `episodes` and an unused `links` table in `workspace/memory/memory.mjs:13-64`, where five later columns arrive as guarded `ALTER`s re-run on every process start and the active-row invariant is a partial unique index over `(kind, key) WHERE expired_at IS NULL`; vector side tables created lazily in `workspace/memory/embed.mjs`.

### Add/Write Path

- `mem0`: `Memory.add()` and `_add_to_vector_store()` in `mem0/mem0/memory/main.py`.
- `langmem`: `create_manage_memory_tool()` in `langmem/src/langmem/knowledge/tools.py`; extraction in `MemoryManager`.
- `honcho`: `honcho/src/crud/message.py`, `honcho/src/deriver/deriver.py`, `honcho/src/crud/representation.py`.
- `engram`: `AddObservation()` in `engram/internal/store/store.go`; MCP `handleSave()` in `engram/internal/mcp/mcp.go`.
- `mempalace`: `process_file()` and `mine()` in `mempalace/mempalace/miner.py`; `tool_add_drawer()` in `mempalace/mempalace/mcp_server.py`; collection access in `mempalace/mempalace/palace.py`.
- `swafra`: `add_knowledge()`, `leiden_chunk()`, and `chunk_conversation()` in `swafra/swafra/engine.py`.
- `llm-wiki-memory`: MCP dispatch in `llm-wiki-memory/mcp-server/mcp-write-dispatch.mjs`; `writeMemory()` / `saveDocument()` in `scripts/lib/wiki-mutate.mjs`; transcript capture in `scripts/hooks/flush-worker.mjs`; promotion in `scripts/compile-promote.mjs`.
- `rainbox`: explicit commands in `rainbox/source/memory/ops.py`; assistant actions in `rainbox/source/agents/assistant.py`; review UI actions in `rainbox/source/webapp/memory_api.py`; DB helpers in `rainbox/source/db/memory.py`.
- `letta`: `letta/letta/services/tool_executor/core_tool_executor.py`; `letta/letta/services/block_manager.py`; `letta/letta/services/passage_manager.py`.
- `supermemory`: `supermemory/packages/ai-sdk/src/tools.ts`, `supermemory/apps/mcp/src/server.ts`, `supermemory/apps/mcp/src/client.ts`.
- `verel`: `verel/src/verel/memory/local.py`, `verel/src/verel/memory/remember.py`.
- `hindsight`: `MemoryEngine.retain_async()` and `engine/retain/orchestrator.py`.
- `graphiti`: `Graphiti.add_episode()` and `utils/maintenance/node_operations.py` / `edge_operations.py`.
- `mastra-observational-memory`: `ObservationalMemoryProcessor` plus observation strategies and observer/reflector runners.
- `memos`: `MOSCore`, `GeneralMemCube`, `GeneralTextMemory.add()`, and `TreeTextMemory.add()`.
- `basic-memory`: MCP `write_note` through typed client/API to accepted-note services and indexing workflows.
- `agentmemory`: `src/functions/observe.ts` and `src/functions/remember.ts`.
- `tencentdb-agent-memory`: `src/core/hooks/auto-capture.ts`, `src/core/record/l1-extractor.ts`, `l1-dedup.ts`, and `l1-writer.ts`.
- `cognee`: `cognee/api/v1/remember/remember.py`, `add/add.py`, and `cognify/cognify.py`.
- `claude-mem`: hook adapters, `SessionMessageBuffer.ts`, and `worker/agents/ResponseProcessor.ts`.
- `a-mem`: `AgenticMemorySystem.add_note()` and `process_memory()` in `agentic_memory/memory_system.py`.
- `hipporag`: `index()`, `add_fact_edges()`, `add_passage_edges()`, `add_synonymy_edges()` in `src/hipporag/HippoRAG.py`.
- `magic-context`: `memory/promotion.ts` (`promoteSessionFactsDurable`, `embedPromotedFacts`).
- `metaclaw`: `metaclaw/memory/manager.py` and `consolidator.py`.
- `nanobot`: Consolidator append plus Dream's surgical edits in `nanobot/agent/memory.py`.
- `cowagent`: `agent/memory/summarizer.py` (daily summary and Deep Dream distillation).
- `genericagent`: policy-gated writes per `memory/memory_management_sop.md`.
- `pi`: append to the session tree; `harness/compaction/compaction.ts` for range replacement.
- `voyager`: `SkillManager.add_new_skill()` in `voyager/agents/skill.py`, gated by `if info["success"]` in `voyager/voyager.py`.
- `generative-agents`: `add_event()`, `add_thought()`, `add_chat()` in `associative_memory.py`.
- `holographic`: `add_fact()` and `_rebuild_bank()` in `plugins/memory/holographic/store.py`; `_auto_extract_facts()` in `__init__.py`.
- `hermes-agent`: `MemoryStore.add/replace/remove` and `_apply_write_gate()` in `tools/memory_tool.py`.
- `openviking`: `openviking/session/memory/extract_loop.py`, `memory_updater.py`, and `memory_isolation_handler.py`.
- `redis-agent-memory-server`: `promote_working_memory_to_long_term()` and the dedupe chain in `V0/agent_memory_server/long_term_memory.py`.
- `byterover`: `MemoryDeduplicator.deduplicate()` in `src/agent/infra/memory/memory-deduplicator.ts`; `resolveStructuralLoss()` in `knowledge/conflict-resolver.ts`.
- `openclaw`: `sanitizeForMemoryCapture()` in `extensions/memory-lancedb/memory-capture-sanitization.ts`; `store()` in `lancedb-store.ts`.
- `daimon`: `serialize_strict()` in `plugin/daimon_briefing/serializer.py` with its gate chain (`sanitize_source_ids`, `pin_imperatives`, `verify_quotes`, `ground_outcomes`); `merge()` in `carry.py`; `write_checkpoint()` in `store.py`.
- `helm`: the `remember` verb in `workspace/memory/memory.mjs:87-162` — provisional cap, evidence ratchet, supersession, gated supersede episode; hot-path capture in `index.js:572-583`; the tool wrapper `workspace/tools/impl/memory.remember.mjs`, which omits `--source` and so never trips the cap.

### Search/Retrieve Path

- `mem0`: `Memory.search()` and `_search_vector_store()`; scoring in `mem0/mem0/utils/scoring.py`.
- `langmem`: `create_search_memory_tool()` delegates to `BaseStore.search/asearch`.
- `honcho`: `honcho/src/crud/representation.py`, `honcho/src/crud/document.py`, `honcho/src/dialectic/`.
- `engram`: `Search()` and context helpers in `engram/internal/store/store.go`; MCP search/context handlers.
- `mempalace`: `search_memories()`, `_hybrid_rank()`, `_bm25_only_via_sqlite()` in `mempalace/mempalace/searcher.py`.
- `swafra`: `BM25Index`, `search_knowledge()`, and `graph_walk()` in `swafra/swafra/engine.py`.
- `llm-wiki-memory`: `searchOneTree()` in `llm-wiki-memory/scripts/lib/wiki-search.mjs`; federated merge in `wiki-search-fanout.mjs`; `searchMemory()` and `recallLessons()` in `recall-search.mjs` / `recall.mjs`.
- `rainbox`: `retrieve_memories_hybrid()`, `hard_filtered_claims()`, `build_chat_memory_block()` in `rainbox/source/memory/retrieval.py`; profile retrieval in `rainbox/source/user_profile/retrieval.py`.
- `letta`: `archival_memory_search()`, `conversation_search()`, `message_manager.search_messages_async`.
- `supermemory`: `client.search.execute`, `client.search.memories`, `/v4/profile` context helper.
- `verel`: `recall()` in `local.py`, `recall_budgeted()` in `recall.py`, rank logic in `view.py`.
- `hindsight`: `engine/search/retrieval.py`, `fusion.py`, `link_expansion_retrieval.py`, and `reranking.py`.
- `graphiti`: `graphiti_core/search/search.py` and `search_config_recipes.py`.
- `mastra-observational-memory`: `Memory.getContext()`, observation-context builders, and optional observation indexing in `packages/memory/src/index.ts`.
- `memos`: `TreeTextMemory.search()`, `memories/textual/searcher/`, and `get_relevant_subgraph()`.
- `basic-memory`: `services/search_service.py` and backend repositories inheriting `search_repository_base.py`.
- `agentmemory`: `src/functions/search.ts`, `src/state/hybrid-search.ts`, and `src/functions/smart-search.ts`.
- `tencentdb-agent-memory`: `src/core/tools/memory-search.ts`, `conversation-search.ts`, and store search methods.
- `cognee`: `cognee/api/v1/recall/recall.py`, `modules/search/methods/search.py`, and retrievers under `modules/retrieval/`.
- `claude-mem`: `worker/search/SearchOrchestrator.ts`, Chroma/SQLite strategies, and `services/sqlite/SessionSearch.ts`.
- `a-mem`: `search_agentic()` and Chroma wrappers in `agentic_memory/retrievers.py`.
- `hipporag`: `graph_search_with_fact_entities()` and `run_ppr()` in `src/hipporag/HippoRAG.py`.
- `magic-context`: `search.ts` with `matchType` semantic/fts/hybrid, plus `message-index.ts`.
- `metaclaw`: `metaclaw/memory/retriever.py` under the live `MemoryPolicyState`.
- `nanobot`: none; durable files are always in context.
- `cowagent`: vector and FTS5 search in `agent/memory/storage.py`.
- `genericagent`: L1 index lookup then file open; no ranker.
- `pi`: none; context is the session tree walked to root.
- `voyager`: `retrieve_skills()` in `voyager/agents/skill.py`.
- `generative-agents`: `new_retrieve()` and the extractors in `persona/cognitive_modules/retrieve.py`.
- `holographic`: `FactRetriever.search/probe/related/reason/contradict` in `plugins/memory/holographic/retrieval.py`.
- `hermes-agent`: FTS5 session search in `hermes_state.py`; curated memory needs no retrieval.
- `openviking`: `openviking/retrieve/hierarchical_retriever.py`, `type_quota_recall.py`, `memory_lifecycle.py`.
- `redis-agent-memory-server`: `search_long_term_memories()` and `rerank_with_recency` in `V0/agent_memory_server/long_term_memory.py`.
- `byterover`: `ListMemoriesOptions` filtering in `src/agent/infra/memory/memory-manager.ts`.
- `openclaw`: `scopedPredicate()` and `query()` in `extensions/memory-lancedb/lancedb-store.ts`; `normalizeRecallQuery()` in `memory-policy.ts`.
- `daimon`: `search()` and `suggest()` in `plugin/daimon_briefing/recall.py`; ranking in `scoring.py`.
- `helm`: one function, `workspace/memory/memory.mjs:164-326` — a 500-row recency-ordered candidate window, hand-written BM25, a semantic arm that is MiniLM if cached and TF-IDF cosine otherwise, RRF at k=60, a confidence weight and a key-match boost, and a separate episode scorer with a 30-day recency term.

### Context Assembly

- `mem0`: mostly application-owned after search.
- `langmem`: application-owned; tools return store/search results.
- `honcho`: working representation in `honcho/src/crud/representation.py`.
- `engram`: MCP context/session summary in `engram/internal/mcp/mcp.go`.
- `mempalace`: four-layer stack in `mempalace/mempalace/layers.py`; MCP search/status/list tools in `mempalace/mempalace/mcp_server.py`.
- `swafra`: `get_context()` source-diverse search/walk composition in `swafra/swafra/engine.py`.
- `llm-wiki-memory`: bounded MCP responses in `llm-wiki-memory/mcp-server/tools-search.mjs` and `scripts/lib/search-clamp.mjs`; automatic session context in `scripts/hooks/session-start.mjs` and `scripts/lib/work-context.mjs`.
- `rainbox`: `rainbox/source/agents/chat_context.py`, `rainbox/source/memory/retrieval.py`, `rainbox/source/user_profile/retrieval.py`.
- `letta`: `Memory.compile()` in `letta/letta/schemas/memory.py`.
- `supermemory`: `supermemory/packages/tools/src/shared/context.ts`.
- `verel`: `verel/src/verel/memory/recall.py`.
- `hindsight`: `MemoryEngine.recall_async()` and `reflect_async()` with `engine/search/think_utils.py`.
- `graphiti`: application-owned assembly from structured `SearchResults`.
- `mastra-observational-memory`: `Memory.getContext()` and `processor.ts` system-message injection.
- `memos`: `MOS.chat()` and context helpers in `mem_chat/`.
- `basic-memory`: `mcp/tools/build_context.py` and graph/context response schemas.
- `agentmemory`: token budgeting in `src/functions/context.ts`; compact expansion in `src/functions/smart-search.ts`.
- `tencentdb-agent-memory`: `src/core/hooks/auto-recall.ts` and symbolic offload assembly in `src/offload/index.ts`.
- `cognee`: structured output from `recall`; final prompt placement remains integration-owned.
- `claude-mem`: `src/services/context/ContextBuilder.ts` and `ObservationCompiler.ts`.
- `a-mem`: caller-owned; no bounded context assembler.
- `hipporag`: ranked passages returned to the caller; QA assembly in `rag_qa()`.
- `magic-context`: `<session-history>` and primer injection via the Pi context handler; `primer-clustering.ts`.
- `metaclaw`: injection bounded by policy `max_injected_units` and `max_injected_tokens`.
- `nanobot`: `SOUL.md`, `USER.md`, `memory/MEMORY.md` injected; Dream prompt capped at 8,000 chars per file.
- `cowagent`: `MEMORY.md` injected into every conversation.
- `genericagent`: L1 `global_mem_insight.txt`, hard-capped at 30 lines.
- `pi`: `buildSessionContext()` plus `core/resource-loader.ts` for AGENTS.md/SYSTEM.md.
- `voyager`: retrieved code plus the unbounded `programs` property injected into the action prompt.
- `generative-agents`: top-30 node descriptions, no token budget.
- `holographic`: `prefetch()` in `plugins/memory/holographic/__init__.py` — top-5, unfenced.
- `hermes-agent`: `format_for_system_prompt()` / `_render_block()` in `tools/memory_tool.py`, rendered once per session.
- `openviking`: `QueryResult` from the hierarchical retriever; final placement is integration-owned.
- `redis-agent-memory-server`: `V0/agent_memory_server/summary_views.py` and API response shaping.
- `byterover`: caller-owned after listing.
- `openclaw`: auto-recall assembly in `extensions/memory-lancedb/index.ts`.
- `daimon`: `build()`, `withhold()`, `stale_carried()` and `render_plain()` in `plugin/daimon_briefing/briefing.py`; terminal output in `render.py`.
- `helm`: `recallMemories()` in `index.js:490-510` for the per-turn block, prompt assembly at `index.js:595-607`, and the static channel — `workspace/memory/refresh-index.mjs` writing `INDEX.md`, imported by the `@memory/INDEX.md` line at `workspace/CLAUDE.md:15`.

### Background Workers

- `mem0`: no central open worker in the inspected OSS core; extraction happens in write path.
- `langmem`: `langmem/src/langmem/reflection.py`.
- `honcho`: `honcho/src/deriver/`, `honcho/src/reconciler/`, queue models.
- `engram`: sync queue in `engram/internal/sync/` and store mutation queue fields.
- `mempalace`: mining/convo/format miners, hallway/tunnel computation, daemon jobs, repair/sync/backups.
- `swafra`: none; chunking, embedding, graph construction, and JSON rewrites happen synchronously in `add_knowledge()`.
- `llm-wiki-memory`: detached capture in `llm-wiki-memory/scripts/hooks/flush-worker.mjs`; compile in `scripts/compile*.mjs`; consolidation in `scripts/consolidate*.mjs`; self-healing scheduler in `scripts/cron*.mjs`.
- `rainbox`: embedding sync/prune in `rainbox/source/memory/embeddings.py`; feedback/eval loop in `rainbox/source/db/feedback.py` and `rainbox/source/evals/`.
- `letta`: manager services and prompt rebuilds; not primarily worker-centric in inspected paths.
- `supermemory`: hosted processing not visible; graph UI and MCP/client visible.
- `verel`: consolidation, promotion, replication modules.
- `hindsight`: queued consolidation and maintenance workers with per-bank retries.
- `graphiti`: ingestion maintenance and optional saga summarization; no separate mandatory queue.
- `mastra-observational-memory`: early async observation/reflection buffers plus idle/provider-change activation.
- `memos`: `mem_scheduler/` and periodic activation-memory refresh.
- `basic-memory`: file watcher, startup reconciliation, and portable indexing workflows.
- `agentmemory`: consolidation, graph extraction, decay, and index maintenance.
- `tencentdb-agent-memory`: deferred embeddings, scene/persona generation, task draining, and `src/offload/reclaimer.ts`.
- `cognee`: pipeline executor, `memify`, session improvement, cognify rollback, and stale-run recovery.
- `claude-mem`: durable pending queue, observer providers, Chroma/cloud sync, and backfill/repair.
- `a-mem`: no worker; “consolidation” is synchronous reindexing.
- `hipporag`: none; OpenIE is cacheable and resumable but runs inline.
- `magic-context`: the dreamer — `task-scheduler.ts`, `cron.ts`, `lease.ts`, `verify.ts`, `map-memories.ts`.
- `metaclaw`: `self_upgrade.py`, `upgrade_worker.py`, `replay.py`, `policy_optimizer.py`.
- `nanobot`: Dream on cron, gated by `DreamRunProgress`.
- `cowagent`: 23:55 daily summary then Deep Dream distillation.
- `genericagent`: 12-hour L4 archive cron in `reflect/scheduler.py`.
- `pi`: compaction and branch summarization only.
- `voyager`: none; the rollout loop is synchronous.
- `generative-agents`: reflection fires inline when the poignancy countdown crosses zero.
- `holographic`: none; `_rebuild_bank()` runs synchronously on every write.
- `hermes-agent`: none for curated memory; a mounted provider may run its own.
- `openviking`: extraction loop, streaming updater, reindex executor, hotness maintenance.
- `redis-agent-memory-server`: debounced trailing extraction, compaction, dedupe, and forgetting sweeps via `docket_tasks.py`.
- `byterover`: bounded-concurrency LLM deduplication.
- `openclaw`: auto-capture cursor advancement; no separate worker.
- `daimon`: no worker — a detached `daimon serialize` child spawned by `hook/daimon-session-end.py`, tracked through `ledger.py` (`_session_ledger`, `_heal_plan`) and re-driven by `daimon heal`.
- `helm`: `workspace/think/think.mjs` under launchd/systemd — a ~15-minute reflection tick with a stale-PID lock, a quiet window, a tick and wall-clock guard that exits for the service manager to restart, and a weekly deep review whose completion mark is stamped only on a clean exit; then `workspace/memory/consolidate.mjs` (distil, decay, prune, dedupe) and an index rewrite after every tick.

### MCP/API/SDK Surfaces

- `mem0`: Python SDK and service/API paths.
- `langmem`: LangChain/LangGraph tools.
- `honcho`: service endpoints and SDK-facing models.
- `engram`: `engram/internal/mcp/mcp.go`.
- `mempalace`: `mempalace/mempalace/mcp_server.py`, CLI modules, hooks under `mempalace/hooks/`, skills/commands.
- `swafra`: Python FastMCP in `swafra/swafra/server.py`; Node MCP in `swafra/src/index.ts`; subprocess bridge in `swafra/src/engine.ts`.
- `llm-wiki-memory`: `llm-wiki-memory/mcp-server/index.mjs` and `tools-*.mjs`; `scripts/cli.mjs`; Claude Code hooks under `scripts/hooks/`; canonical agent policy in `templates/agents-memory-instructions.md`.
- `rainbox`: web API/UI in `rainbox/source/webapp/memory_api.py` and `memory_views.py`; assistant capabilities in `rainbox/source/agents/assistant.py`.
- `letta`: tool definitions in `letta/letta/functions/function_sets/base.py`, runtime in core tool executor.
- `supermemory`: `supermemory/apps/mcp/src/server.ts`, `supermemory/packages/ai-sdk/src/tools.ts`.
- `verel`: `verel/src/verel/mcp_server.py`, hosted/replicated adapters.
- `hindsight`: FastAPI REST, MCP, generated SDK clients, CLI, and framework integrations.
- `graphiti`: Python library, `mcp_server/`, and `server/`.
- `mastra-observational-memory`: Mastra `Memory`, agent processors, and direct context APIs.
- `memos`: MOS runtime/chat, API, and CLI layers.
- `basic-memory`: MCP tools, typed API clients, FastAPI, CLI, and per-project local/cloud routing.
- `agentmemory`: MCP, HTTP, CLI, lifecycle hooks, and the iii function registry.
- `tencentdb-agent-memory`: OpenClaw hooks and two search tools plus the Hermes gateway; no MCP surface was found.
- `cognee`: Python SDK, REST server, CLI, MCP server, and migration/export APIs.
- `claude-mem`: coding-agent hooks, worker HTTP API, local/server MCP, and UI.
- `a-mem`: direct Python API only.
- `hipporag`: Python library, `main.py`, and `examples/`; no MCP or service.
- `magic-context`: Pi `ExtensionAPI` adapter, an OpenCode adapter, a CLI, and a dashboard.
- `metaclaw`: OpenClaw plugin (`openclaw-metaclaw-memory/OPENCLAW_PLUGIN_SPEC.md`) with a sidecar manager.
- `nanobot`: internal, with WebUI and cron.
- `cowagent`: `agent/tools/memory/` plus `service.py`.
- `genericagent`: internal; `reflect/` drives autonomy.
- `pi`: CLI, TUI, SDK, server, and 20+ extension events — none memory-shaped.
- `voyager`: none; research rollout loop.
- `generative-agents`: none; simulation with a Django frontend.
- `holographic`: `fact_store` and `fact_feedback` tools through the Hermes `MemoryProvider` ABC.
- `hermes-agent`: the `memory` tool, `agent/memory_provider.py` for third-party backends, and `hermes mcp serve`.
- `openviking`: Python SDK, REST server, CLI, web studio, npm package, and Hermes/OpenClaw provider adapters.
- `redis-agent-memory-server`: REST (`api.py`), MCP (`mcp.py`), CLI, and generated SDK clients.
- `byterover`: `brv` CLI and MCP; Hermes provider adapter.
- `openclaw`: `extensions/memory-core/` plugin contract, memory tools, CLI, and doctor contracts.
- `daimon`: host hooks in `hook/` and `plugin/daimon_briefing/_hooks/`; read-only stdio MCP in `mcp_server.py` and `mcp_tools.py`; commands in `cli.py`.
- `helm`: no MCP or SDK for memory — a JSON-on-stdout CLI (`memory.mjs`), two shell-out entries in `workspace/tools/registry.json`, and Discord, iMessage and terminal front doors converging on one Claude Code session keyed `'owner'` in `workspace/sessions.mjs`.

### Evals/Tests

What these harnesses do and do not measure — and why a bad benchmark score is
often weak evidence — is covered separately in
[benchmarking agent memory](../benchmarks/).

- `mem0`: tests are present but the report focused on core implementation.
- `langmem`: tests/examples around tools and extraction should be consulted before reuse.
- `honcho`: rich tests under `honcho/tests`.
- `engram`: Go package tests and MCP flows should be inspected for command behavior.
- `mempalace`: broad tests under `mempalace/tests`; benchmarks under `mempalace/benchmarks`.
- `swafra`: no unit/integration tests; LongMemEval harness and artifacts under `swafra/bench` and `swafra/packages/mcp/bench`, with a result-count validity problem.
- `llm-wiki-memory`: broad unit tests under `llm-wiki-memory/test`; lifecycle and federation coverage under `test/e2e`; latency evidence in `PERFORMANCE.md`; no retrieval-relevance benchmark.
- `rainbox`: memory/retrieval/assistant/UI tests under `rainbox/source/memory`, `rainbox/source/db`, `rainbox/source/agents`, and `rainbox/source/webapp`.
- `letta`: `letta/tests/test_memory.py`, manager tests, passage/message/block tests.
- `supermemory`: visible integration/e2e wrappers and memory graph tests; backend tests not present.
- `verel`: strong memory-focused tests under `verel/tests/test_memory*.py`, plus consolidation, promotion, lattice, replicated, hosted, MCP tests.
- `hindsight`: broad retain/recall/reflect, temporal, consolidation, migration, defense, audit, and benchmark coverage.
- `graphiti`: graph-backend, extraction, dedupe, temporal invalidation, search recipe, saga, and removal tests.
- `mastra-observational-memory`: dense threshold, buffering, marker, retry, resource-scope, and storage integration tests.
- `memos`: unit/integration/benchmark coverage varies by configured cube and backend.
- `basic-memory`: SQLite/PostgreSQL unit/integration coverage plus a provenance-rich standalone benchmark harness.
- `agentmemory`: broad function/state/hook tests; documented retrieval-only LongMemEval-S and small synthetic coding-agent-life benchmarks.
- `tencentdb-agent-memory`: six visible TypeScript/Python test files, none covering the central L1/L2/L3 lifecycle; README benchmark claims lack committed harness/results here.
- `cognee`: broad unit/integration/backend/permission/recovery tests; committed preliminary BEAM report with a held-out 100K result and exploratory in-sample-routed 10M result.
- `claude-mem`: 237 TypeScript test files spanning hooks, queues, privacy, migrations, Chroma/cloud sync, and server paths; no committed memory-quality benchmark found.
- `a-mem`: small CRUD/retriever test suite; paper reproduction and benchmark artifacts live in a separate repository.
- `hipporag`: thin unit tests (`tests/test_bedrock_mantle.py`, `tests/integration/`) beside a well-developed `reproduce/` benchmark tree; no committed result artifacts.
- `magic-context`: 473 test files and roughly 131,000 lines of tests, including per-version migration suites and named CAS-race tests; no retrieval or verification-precision benchmark.
- `atomic-agent`: the most developed evaluation *process* in the atlas — a design plan with §14 acceptance criteria (`MEMORY_FABRIC_V2.md`), an implementation ledger recording which phases landed (`MEMORY_FABRIC_V2.5.md`), and a campaign whose stated purpose is "is memory actually useful" with numbered experiments E9–E12 behind `npm run eval:memory:v25`. All three v2.5 features ship `default: false` pending its verdict. No scored artifacts were found committed.
- `mateclaw`: tests under `src/test/java/vip/mate/memory/`; no memory benchmark. Its decorator chain already instruments every provider, so per-backend comparison would be straightforward and does not appear to have been done.
- `open-cowork`: `memory-eval-harness.ts` defines eval cases as a session plus queries carrying **both `expectedHits` and `forbiddenHits`**, scores the assembled prompt prefix rather than raw retrieval output, combines a deterministic containment score with an LLM judge, and writes reports with a run id and artifact directory. This is the most complete memory benchmark shape in the atlas; no scored results were found committed at this commit.
- `gini-agent`: per-module and integration tests, including an assertion that a follow-up task records recalled units; no memory-quality benchmark, despite a recall implementation that cites specific published equations.
- `moltis`: contract tests compiled under `#[cfg(test)]`; no memory benchmark.
- `mercury-agent`: `user-memory.test.ts`; no memory benchmark.
- `metaclaw`: committed `benchmark/data/metaclaw-bench*` harnesses with eval fixtures, plus dedicated `run_memory_ablation*.py` scripts — rare in this atlas; no numbers reproduced here.
- `nanobot`: no memory tests located, which is notable given the cursor and failure-gate logic carry most of the correctness.
- `cowagent`: no memory tests or benchmark located.
- `genericagent`: no memory tests or benchmark located; an arXiv report is cited but was not assessed.
- `pi`: an `evals` package and session-harness test utilities; no memory benchmark, because there is no memory.
- `voyager`: no tests for `SkillManager`; evaluation is the paper's Minecraft tech-tree benchmark, which measures task completion rather than memory quality.
- `generative-agents`: no memory tests; evaluation is human believability ratings, and the `gw` retrieval weights have no committed ablation.
- `holographic`: 599 lines across four plugin test files plus 1,662 lines exercising the provider ABC; no retrieval-quality benchmark, and the measured contribution of the HRR arm is unknown.
- `hermes-agent`: memory-tool, write-approval, provider, and backup suites, with several guards citing the issues that produced them; no committed memory-quality benchmark.
- `openviking`: 688 test files, plus committed LoCoMo, LongMemEval, tau2, SkillsBench, and vector-DB harnesses with runners for six systems and token accounting — but the published headline numbers live off-repo and no raw result artifacts are committed.
- `redis-agent-memory-server`: roughly 27,000 lines of tests, with dedicated forgetting, extraction, strategy, and contextual-grounding suites; benchmark scaffolding but no published numbers.
- `byterover`: no tests located for the memory or knowledge domain modules, including none for the structural-loss guard that is its best idea.
- `openclaw`: test lines far exceed implementation — 4,497 for the LanceDB extension and 2,530 for the memory-core doctor contract; no committed retrieval benchmark.
- `daimon`: 1,974 tests across roughly 29,700 lines against 15,600 lines of source, with dedicated quote-verification, carry, withhold, redaction-leak, receipt, and host-isolation suites. Its `benchmark/` runs LongMemEval-S through the real serializer and answers only from `daimon recall`, under a written reporting policy — publish only self-measured numbers with the full config stamp, label third-party figures as their publishers' claims, never report a figure without its backend, and report the trade rather than the win. Two result files are committed; the honest one is a 52-question interim baseline at **Recall@5 0.58 / Hit@5 0.67 / MRR 0.59** (my arithmetic over its per-question rows — the file ships no aggregate block). The other is a five-question run, which the config stamp makes obvious.
- `helm`: `workspace/tests/smoke.mjs`, 88 labelled cases against the live SQLite file, of which about nineteen touch memory. Two assert *ranking* rather than round-trips — confidence weighting placing a high-confidence fact above a low-confidence lexical match, and BM25 term-frequency ordering — which is rare at this scale. Others cover the provisional cap and its evidence ratchet, supersession end to end, the unique index rejecting a raw duplicate `INSERT`, the `access_count` bump on read, and two gates on the system's own episode noise. There is no eval harness, no retrieval benchmark, and no committed benchmark artefact; nothing tests the 500-row recall boundary that caps the whole design, and the second brain is covered by a case that explicitly asserts "no Claude run". Separately, `workspace/repo-scan-report.md` is a committed 25-issue self-audit — severity, `file:line`, "reproduced empirically", and a fix pointing at a correct pattern already in the repo — and every issue I checked is closed at the pinned commit, including the shared engine-resolution module the report itself recommended.

## 5. Design Patterns That Recur

These recurring moves are also documented as standalone implementation guides in the [memory design pattern library](../patterns/). The library covers correction, provenance, trust, retrieval, scope, write governance, federation, context assembly, recoverable background work, lifecycle decay, zero-LLM capture, audit history, pluggable memory providers, procedural skills, and gating expensive work.

### Explicit memory mutation surfaces

Repos: strongest in `mem0`, `langmem`, `engram`, `mempalace`, `llm-wiki-memory`, `rainbox`, `letta`, `supermemory`, `verel`, `hindsight`, `graphiti`, `basic-memory`, and `agentmemory`.

The agent, application, or operator explicitly calls a memory operation. This works because it gives the system a narrow interface for durable state changes. It fails when the model forgets to call the tool, calls it with low-quality facts, or treats tool descriptions as policy enforcement. It is not the only capture model in the atlas: Mastra observes automatically at context thresholds, Basic Memory also reconciles direct filesystem edits, and event-driven systems such as Honcho derive memory from ordinary message ingestion.

### Separate hot memory from archival memory

Repos: `letta`, `rainbox`, `honcho`, `supermemory`, `mempalace`, `llm-wiki-memory`, `hindsight`, `mastra-observational-memory`, `memos`, `tencentdb-agent-memory`, partly `mem0` and `agentmemory`.

Hot memory is small and prompt-ready. Archival/document memory is large and retrieved on demand. This works because prompt space is scarce and long-term stores are noisy. It fails when there is no promotion/demotion policy between the layers.

Promotion is the part most systems leave unstated; it is now a pattern in its
own right — see [promotion between tiers](../patterns/promotion-between-tiers/).

### Evidence first, derived memory second

Pattern guide: [Evidence before belief](../patterns/evidence-before-belief/).

Repos: strongest in `cognee`, `honcho`, `verel`, `mempalace`, `rainbox`, `graphiti`, `hindsight`, `basic-memory`, and `tencentdb-agent-memory`; partly in `claude-mem`, `engram`, `swafra`, `llm-wiki-memory`, `mastra-observational-memory`, and `agentmemory`.

Raw messages, observations, files, drawers, or evidence rows are retained, and derived facts/representations/indexes are computed from them. This works because wrong memories can be audited and recomputed. It fails if the derived layer does not preserve source IDs, if raw stores become too noisy, if evidence excerpts are too thin, or if background derivation makes read consistency surprising.

`helm` is the cheapest version of the idea in the atlas and shows how much of it
survives at that price. A write tagged as an agent observation is capped at 0.7
confidence no matter what the caller asked for, and rises by 0.05 only per
independent repeat of the *same value* — so a first sighting is structurally
incapable of being stored as certain, in about fifteen lines. What it does not
buy is auditability: the fact carries no link back to the episodes that produced
it, the table that could express one is created and never used, and a distilled
row reading "mentioned in 5 episodes" cannot name a single one. Corroboration
without provenance is the affordable half of the pattern, and it can raise
belief in a value it can no longer explain.

### Hybrid retrieval

Pattern guide: [Hybrid retrieval fusion](../patterns/hybrid-retrieval-fusion/).

Repos with visible fused lexical/semantic or multi-arm ranking: `mem0`, `honcho`, `mempalace`, `swafra`, `rainbox`, `verel`, `hindsight`, `graphiti`, `basic-memory`, `agentmemory`, `helm`, `tencentdb-agent-memory`, and configured `memos` pipelines. Supermemory exposes hybrid settings, but the hosted implementation is not visible. Engram's FTS/topic-key retrieval and Letta's separate archival/conversation searches are useful multi-mode retrieval surfaces, not evidence of fused hybrid ranking.

Vector search alone is not enough. Identifiers, names, exact phrases, dates, file paths, and project keys often need lexical search. Hybrid retrieval works because it handles both fuzzy semantic recall and exact lookup. MemPalace adds a useful variant: extracted/indexed "closets" boost drawer ranking but never gate direct evidence retrieval. Swafra is a useful compact example of BM25 + vector + cheap heuristic fusion, but also a warning: ad hoc component normalization and unbounded bonuses make scores hard to interpret. Hybrid retrieval fails when rank fusion is opaque or not evaluated.

Cognee has genuine multi-view hybrid retrievers but also many non-fused modes
with different result contracts. Claude-Mem and A-MEM are naming
counterexamples: ordinary Claude-Mem text search selects semantic rather than
fusing it with FTS, and A-MEM's “hybrid” path is vector-only.

`helm` answers the "opaque fusion" objection the cheap way and is worth copying
for it. Both arms are computed in JavaScript over the same candidate rows, and
they are combined by reciprocal rank at the conventional k=60 rather than by
normalizing two incomparable score scales — the right call precisely because the
project has no relevance data to calibrate against. The belief weight is applied
as a multiplier (`0.7 + 0.3·confidence`) rather than as a filter, so a
low-confidence row is penalized rather than excluded. The cost of arriving here
so cheaply shows up in two places: the semantic arm silently degrades through
three quality tiers — cached MiniLM, then TF-IDF cosine, then nothing — with one
output shape and no signal to the caller, and every arm runs over a hard
500-row window ordered by *recency*, so past a few hundred active facts the
oldest and best-corroborated memories stop being candidates at all. Fusion
quality is bounded by candidate generation, and this is the clearest place in the
atlas to see it.

### Scope as a first-class key

Pattern guide: [Scope as a first-class key](../patterns/scope-as-a-first-class-key/).

Repos: most systems; weakest or absent in `a-mem`, `swafra`, and
`tencentdb-agent-memory`, while `agentmemory` requires opt-in isolated agent
mode for its strictest boundary.

Good systems make memory boundaries explicit: user, agent, run, project, workspace, peer, session, space, palace, wing, room, source file, claim scope, sensitivity, scope lattice, namespace. This works because many memory bugs are scope bugs. Swafra's one global corpus shows why a source title is not a scope: two clients or projects can silently retrieve each other's memory. Scope fails when absent or when it is only metadata with no migration, inheritance, access, or conflict policy.

### MCP as a universal adapter

Repos: `engram`, `mempalace`, `swafra`, `llm-wiki-memory`, `supermemory`, `verel`, `hindsight`, `graphiti`, `cognee`, `claude-mem`, `basic-memory`, `agentmemory`, and conceptually similar tool surfaces elsewhere.

MCP is useful because it lets different coding agents and desktop tools use the same memory backend. It fails if the MCP tool descriptions become the only guardrail against bad writes.

### Local SQLite for inspectable memory

Repos: `engram`, `mempalace`, `verel`, `claude-mem`, `basic-memory`, `agentmemory`, `helm`, and the local backends of `cognee` and `tencentdb-agent-memory`; SQLite also supports history/messages in `mem0`.

SQLite works well for local agent memory: durable, fast, easy to inspect, transaction-friendly, and good enough with FTS5. MemPalace also shows the complementary local pattern: SQLite metadata/KG/FTS plus a local vector store. It fails if a product needs multi-tenant scale, remote sharing, or vector-heavy retrieval without extensions/adapters.

`helm` is the minimum viable instance: Node 22's built-in `node:sqlite`, so the
store has *no dependency at all*, and no FTS5 either — BM25 is computed in
JavaScript over the candidate rows. That buys a memory layer with nothing to
install and nothing to run, and it costs two things worth knowing before copying
it. Concurrency is a `busy_timeout` of five seconds against four unsynchronized
writer classes, each `remember` being a read-then-write across separate
statements with no transaction, where the partial unique index is what turns a
lost race into an error rather than a duplicate. And schema evolution is a stack
of `try { ALTER TABLE … } catch {}` re-executed by every entry point on every
start — idempotent, effective, and the reason the real schema is the union of
five files rather than a declaration in one.

### Flat JSON as a prototype store

Repo: `swafra`.

Three JSON files make the complete state inspectable and keep installation trivial. This is reasonable for a single-process prototype and terrible as implicit production durability: full-file rewrites, no transactions or locks, no indexed access, and cross-file consistency hazards. Treat flat JSON as a demo format or export, not a concurrent memory database.

### Filesystem wiki plus git history

Repo: `llm-wiki-memory`.

Markdown leaves plus generated folder indexes make local memory directly readable, diffable, and recoverable. Git commits can group one logical mutation into an auditable change, while repository-owned mounts provide a simple team-sharing path. This works for small coding-agent corpora where inspectability matters more than query throughput. It fails at large scale, under concurrent collaborative writes, or when deletion must erase prior content rather than leave it in history.

### Recoverable background capture

Repos: strongest in `claude-mem`, `llm-wiki-memory`, and `cognee`; related
checkpoint, deferred-work, and evidence-retention ideas appear in `honcho`,
`mempalace`, `agentmemory`, and `tencentdb-agent-memory`.

Decouple transcript capture from the interactive hook, chunk long inputs, retain failed chunks, write fenced raw fallbacks, and support redistillation. This turns provider failure into delayed processing instead of silent data loss. It fails if the recovery stores themselves leak secrets or if no operator ever reviews/retries accumulated stashes.

`daimon` adds the part this pattern usually lacks: a *classifier* over the
capture log, and a UI for it. Every spawn and every result line is appended to
`serialize.log`, and `ledger.py` folds them per session into outstanding
failures, hung children (a liveness heartbeat, not wall-clock, decides), and
retry-exhausted cases — which `daimon status` prints honestly and `daimon heal`
re-drives, one retry per session by default with `--force` as the operator
override. Its chunk cache is what makes the retry cheap: extractions are cached
by chunk content under an explicit version key, so a heal, a merge death, or a
grown transcript re-pays only for the chunks that changed. The cache key is
deliberately *separate* from the prompt version, so wording edits keep the cache
warm while semantic changes rotate it.

### Zero-LLM capture

Pattern guide: [Zero-LLM capture](../patterns/zero-llm-capture/).

Repos: strongest in `agentmemory`, `claude-mem`, `llm-wiki-memory`,
`tencentdb-agent-memory`, and message-first `honcho`; `engram` demonstrates the
small no-extraction baseline; `daimon` applies it *beside* an LLM path rather
than instead of one.

Persist a scoped event before any model call, make it searchable through exact
keys or lexical metadata, then enrich it asynchronously only when useful. This
keeps provider latency and outages out of the capture path. It fails when raw
capture has no privacy, size, retention, or retrieval policy.

`daimon` is the useful hybrid. Its main extraction is an LLM call, but every
mechanism guarding that call is stdlib code: quote verification, outcome
grounding, imperative pinning, carry, dedup, redaction, code anchors, the
world-check probes, and the scar harvester that drafts negative-knowledge
candidates from a session by regex and drops any hit with no file path in its
own span. The lesson is not "avoid the model" but "never let the model be the
only thing between a transcript and a durable claim".

`helm` is the smallest instance and a clean demonstration of the pattern's real
failure mode, which is not privacy but *keying*. One regex on the reply path —
`remember that`, `note that`, `for the record`, `fyi` — captures the following
span as a fact, with no model in the path and no latency on the turn. The key is
`'note-' + Date.now().toString(36)`. Because every capture mints a new key, the
uniqueness index never applies, supersession can never fire, and telling the
agent "remember that I prefer X" twice with different values leaves both facts
live and contradictory at equal confidence. Those rows also arrive
uncorroborated, so the one thing the owner said *explicitly* is the row most
exposed to the confidence-floor prune. A zero-LLM capture path still has to
decide what a memory is *about*, and a timestamp is not an answer.

### Decay and reinforcement

Pattern guide: [Decay and reinforcement](../patterns/decay-and-reinforcement/).

Repos: strongest in `verel`; supporting behavior in `agentmemory`, `honcho`,
`helm` and `daimon`; `swafra` is a counterexample for unconditional age decay.

Let retrieval strength fade or grow without changing epistemic confidence.
This keeps stale operational memory from dominating while protecting durable
truths and correction history. It fails when retrieval itself creates a
self-reinforcing popularity loop or one half-life is applied to every memory
kind.

`daimon` supplies the missing inversion. Its per-type decay rates are ordinary —
beliefs fade slowest, the active topic fastest — but open questions carry
`auto_escalation`, and past a fourteen-day expected lifespan their weight
*grows* by `age**1.5 / 100`, capped so a fresh item still outranks an escalated
one. For that one type, staleness means unresolved rather than irrelevant. The
same file also treats a stamp further in the future than clock skew explains as
neutral rather than maximally fresh, so a teammate's mis-stamped item cannot
outrank genuine local work — a small guard that only appears once memory is
shared across machines.

`helm` shows the pattern's failure mode being *narrowly avoided* and then
reintroduced two lines later. Retrieval does not raise belief — it slows loss:
`log1p(access_count)` is subtracted from the count of stale weeks, so a fact the
agent keeps reaching for holds its confidence without ever gaining any, which is
exactly the separation this pattern asks for. Only never-corroborated rows decay
at all, and rows sourced from the persona document are exempt entirely. Then the
same pass advances `last_seen` by the stale weeks it just consumed, purely so the
next nightly run does not re-apply the same step — an effective idempotence trick
that destroys the column's stated meaning for every other reader, including the
one that orders the weakly-evidenced list by it. If a batch job needs to remember
what it already did, give it its own column.

### Profiles and working representations

Repos: `honcho`, `supermemory`, `letta`, `hindsight`, `mastra-observational-memory`, `agentmemory`, and `tencentdb-agent-memory`.

A low-latency synthesized representation is often more useful than raw top-k memories. This works because agents need compact operating context. It fails when summaries drift, hide uncertainty, or cannot be traced back to evidence.

### Memory governance loop

Repos: strongest in `rainbox`; partly in `verel`.

Memory quality improves when memory use is observable and connected to review, feedback, and evals. RainBox's `RetrievalEvent`, `FeedbackEvent`, `/memory` review page, and eval loop show a practical product pattern. This fails if telemetry is mistaken for truth: a downvote is a review signal, not proof that a memory is false.

### Bi-temporal fact validity

Pattern guide: [Bi-temporal fact validity](../patterns/bi-temporal-fact-validity/).

Repos: strongest in `graphiti`; supporting temporal/event-time ideas in `hindsight`.

Record both when a fact was valid in the represented world and when the system learned or expired it. This preserves historical truth during correction and backfill. It fails when LLM-extracted dates or invalidation decisions are treated as certain.

`helm` is the instructive near-miss, and the reason the mark is withheld rather
than the columns counted. It has `valid_from` and `expired_at`, a `history` verb
that orders by `valid_from DESC`, and supersession that keeps the row it
replaced — the whole shape. But `valid_from` is only ever written as the insert
timestamp or backfilled to `created`, so validity time is record time under a
second name, and no writer can express that something became true before it was
recorded. Two columns and a history verb are not bi-temporality until some caller
can set them apart; the test to ask of any candidate is whether a backfill can
land a fact whose validity precedes its own row.

### Pluggable memory provider

Pattern guide: [Pluggable memory provider](../patterns/pluggable-memory-provider/).

Repos: `hermes-agent` and `openclaw` define the contracts; `holographic`,
`openviking`, `byterover`, `redis-agent-memory-server`, `tencentdb-agent-memory`,
`honcho`, `mem0`, `hindsight`, and `supermemory` are mounted through them.

A host runtime exposes one memory interface and lets users mount a backend by
configuration. This works because no single memory model suits a laptop and a
multi-tenant product at once, and because providers reach many hosts by
implementing one contract. It fails at the boundary: neither contract inspected
here carries a scope parameter or a deletion hook, so host-level erasure cannot
reach a mounted store, trust state cannot cross, and mirroring host writes into a
provider creates duplicates with independent lifecycles.

### Skills as procedural memory

Pattern guide: [Skills as procedural memory](../patterns/skills-as-procedural-memory/).

Repos: strongest in `voyager`; present without a verification gate in
`hermes-agent`, `openviking`, `memos`, and `agentmemory`; the failure-side
counterpart is `verel`.

Store the executable procedure rather than a description of it, index it by a
generated summary, and gate the write on verified execution. This works because
procedural truth is cheap to establish where actions have observable effects —
"did it run and produce the intended state?" is checkable in a way "is this fact
true?" is not, which is why Voyager's gate is stronger than any judgment-based
gate in the atlas. It fails when success in one context is generalized from a
single run, when retrieval has no score threshold (an irrelevant callable is
worse than an irrelevant fact), when the library has no utility signal to prune
by, and — outside a sandbox — because a skill library is agent-authored code
retrieved by similarity and then executed.

### Promotion gates for the policy, not just the memory

Repo: `metaclaw`; the memory-level analogue is `verel`.

Treat the retrieval configuration as a versioned object that must earn its place.
Generate a bounded set of candidate policies, replay them offline against real
past turns, and promote one only when it fails to regress on several independent
measures over a minimum sample. MetaClaw gates on eight deltas with at least ten
samples and an explicit cap on additional zero-retrieval cases — a guard on the
distribution rather than the mean.

This works because it is the only answer in the atlas to "are our fusion weights
right?", and because it resolves the telemetry-versus-truth tension by tuning
*reachability* and never touching confidence. It fails when the replay metrics
are proxies for usefulness rather than measures of it, and when the gate's own
thresholds are unmeasured constants — both of which are true here.

### Memory policy as a written artifact

Repo: `genericagent`; related operator surfaces in `nanobot` (`prompts/dream.md`)
and `cowagent` (documented distillation rules).

Write the memory rules down where a human can read and edit them, next to the
memory they govern. GenericAgent's axioms — action-verified writes, sanctity of
verified data, no volatile state, minimum sufficient pointer — plus its ROI test
for what earns permanent context, are more legible than most systems' code. It
also supplies the missing justification behind every hard budget in this atlas:
`ROI = (error probability x cost) / per-turn word cost`, with the sharp corollary
that an entry the model would act on unprompted is a permanent tax with zero
return.

It fails on enforcement. Prose rules bind only as far as the model follows them,
nothing audits compliance, and the action-verified axiom leaves no record of the
tool call that justified a write.

### Gate the expensive path

Pattern guide: [Gate the expensive path](../patterns/gate-the-expensive-path/).

Repos: strongest in `waku-agent`; also `atomic-agent`, `gini-agent`,
`hermes-agent`, `redis-agent-memory-server`, `metaclaw`, `genericagent`,
`daimon`.

Put a cheap decision in front of an expensive one. `waku-agent` asks a small
model, per turn, whether the store should be touched at all — because default-on
retrieval is not merely slow, it is worse: irrelevant memory in the prompt bends
the answer. The same call returns the search query, so gating costs one call and
buys two. `gini-agent` shows the cheapest version, letting its temporal channel
participate only when the query contains a temporal expression, and
`atomic-agent` heuristic-gates its query rewriter.

This works because it gives a memory layer the ability to return nothing, which
an unconditional pipeline does not have. It fails in one specific direction: a
wrongly skipped retrieval produces a confident answer missing context nobody
knows is missing, while a wrongly permitted one merely costs a search. Gates must
fail open — `waku-agent` states it in the code, "a stale memory beats a lost one"
— and they must be measured. Nothing in the atlas measures its gate.

`daimon` shows the zero-cost end of the same idea. Its proactive-recall gate is
three lexical tests and no model call at all, and its world-check gate is a hard
0.8-second aggregate budget with a five-probe cap where anything unfinished is
killed and skipped. Both fail toward silence rather than toward a stale answer,
which is the opposite of Waku's fail-open posture and correct for what they
guard: a missing *suggestion* costs a reminder, a missing *memory* costs the
answer.

One sub-lesson generalizes past memory: when several classes of work share one
budget, decide up front how the cap is divided rather than letting the first
caller consume it. Daimon allocates in item order, so an expensive class cannot
starve a cheap one — which is the difference between a shared budget and a race.

### Verify memory against its subject

Repos: `magic-context` and `daimon`; the procedural analogue is `voyager`;
contrast the judgment-based gates in `verel` and `rainbox`.

Where a memory describes something inspectable, do not adjudicate it — check it.
Map each memory to the artifacts it is about, record a per-memory verification
timestamp, and let a change in those artifacts put the memory back in scope.
Magic Context does this against files in a git repository; Voyager does the
procedural version by re-running a skill. This works because it replaces "do I
believe this claim?" with "does reality still agree?", which is enormously
cheaper. It fails for memories with no inspectable subject — Magic Context
excludes them explicitly rather than marking them verified — and it degrades if
the verdict itself is a model call, which it currently is.

The reusable sub-lesson is about watermarks: Magic Context's comments record that
an earlier version used a global commit watermark with all-or-nothing coverage,
and that it was reworked to per-memory timestamps so a timed-out run banks what
it checked. Global watermarks make partial progress worthless.

`daimon` is the second instance and answers the "degrades if the verdict is a
model call" objection directly: none of its verifications involve a model. A
quote is checked by string match against the transcript, a code anchor by a
SHA-256 of `ast.dump` of the symbol's definition node — stable under
reformatting, sensitive to structure — and a carried claim by probing whatever it
names, under a sub-second budget.

It also settles a question Magic Context leaves open: **what counts as an
inspectable subject.** Magic Context maps a memory to files. Daimon shows the set
is wider and mostly still local — a path, a branch, a pinned dependency version
are all referents you can read off disk, and only a ticket state has to leave the
machine. So the pattern's reach is not "memories about code"; it is *memories
that name something*, and the naming is what makes them checkable. The design
question that remains is latency and blast radius for the minority of referents
that are remote, rather than adjudication for any of them. Its own stated
measurement goal is the right one and still unanswered — how often a carried
repo-state claim is already false by the next read.

### Diffusion instead of traversal

Repo: `hipporag`; contrast with BFS traversal in `graphiti` and the graph arm in
`agentmemory`.

Rather than deciding how many hops to walk and in which direction, seed a
personalization vector with query-relevant graph nodes and run Personalized
PageRank over the whole graph. Multi-hop association becomes a property of the
diffusion rather than of a traversal policy, and a weak dense-retrieval prior can
be mixed into the same vector. HippoRAG adds two refinements worth copying: seed
weights divided by the entity's chunk count so hubs do not dominate, and low
damping (0.5) to keep relevance near the query's entities. It fails on cost —
PPR runs over the entire graph per query — and on attribution, since no single
signal explains a ranking.

### Non-destructive entity resolution

Repo: `hipporag`; contrast with `graphiti`.

Link similar entities with weighted edges instead of merging them. Graphiti's own
stated biggest risk is that entity-resolution mistakes reshape a large portion of
the graph; adding a synonymy edge instead means a wrong decision creates a weak
spurious path rather than destroying two identities irreversibly. It fails when
the graph becomes dense enough that diffusion blurs everything together, and it
does not give you a canonical entity to display or key on.

### Bounded prompt memory with in-turn consolidation

Repo: `hermes-agent`; contrast with the unbounded-plus-background-summarization
approach in most of the atlas.

Cap curated memory in characters, inject it as a frozen snapshot at session
start, and refuse any write that would exceed the cap — returning the current
entries and requiring the model to consolidate and retry in the same turn. This
works because prompt cost becomes a static, known quantity and the prefix cache
survives the session. It fails because the model chooses what to discard under
time pressure, with no review and no record of what was dropped.

### Structural-loss guard on generated rewrites

Repos: `byterover` and `daimon`; related range-tracking in
`mastra-observational-memory` and verbatim retention in `mempalace`.

Before an LLM rewrite replaces stored content, parse both versions and count
only what would be **deleted** — ignoring additions so enrichment does not
trigger false positives. Treat any loss as high impact and merge the lost
material back automatically. This is the cheapest countermeasure in the atlas to
summarization silently discarding evidence. It fails if the parse is lossy, or if
the same guard is not applied to every rewrite path — ByteRover itself protects
document curation but not its own LLM memory merge.

`daimon` applies the guard on the *read* side, which is cheaper still because it
needs no diff. Its optional LLM briefing render must reproduce every verbatim
quote intact — whitespace-normalized, since models re-wrap lines — and any loss
discards the whole render and falls back to the deterministic one. The check is
possible only because the system already knows which spans are load-bearing;
that is the real prerequisite, and it is why most systems cannot copy this.
The same reasoning governs its token budget: inferred items are truncated first
and verbatim ones are dropped whole rather than shortened, because a guarantee
that lapses under budget pressure was never a guarantee.

### Buffered observation-reflection

Repos: strongest in `mastra-observational-memory`; related consolidation in `hindsight` and `honcho`.

Prepare derived context before the hard prompt threshold, persist the exact source range it covers, and activate it atomically when needed. This removes LLM compression from the critical path. It fails without durable markers, range-aware replacement, recovery, and distributed coordination.

### Resolve, do not just detect

Repos: `memanto` and `daimon`; governance half in `core-memory`; the absence in
`gini-agent`, `mateclaw`, `magic-context`, `openviking`, `holographic`.

Every contradiction a system detects must end in a named disposition, chosen by
someone, recorded where the write path can consult it. Five systems here detect
and stop, which leaves a flagged memory both retrievable and ambiguous — the cost
of detection paid and none of the benefit collected. The disposition set must be
non-binary, because most detected contradictions are two true statements about
different times or scopes, and it must include a human-authored replacement.
Pending findings should stay retrievable, since a blocking queue degrades memory
whenever nobody is looking. It fails when the resolution leaves no trace the next
extraction pass can consult, which is exactly where Memanto's `remove_both`
stops.

`daimon` is the second implementation and the one that puts the disposition in
front of the user rather than in a review queue: a detected supersession renders
*inside the briefing* as a flagged item with the confirm and reject commands
inline, so the resolution happens at the moment the stale claim is read. Two
rules make that safe. A machine suggestion is live by construction — the
liveness fold refuses to let a `supersede-candidate` suppress anything, so a
wrong guess costs a line of noise and never a lost memory. And rejecting a
suggestion needs no evidence, while re-opening a genuinely resolved item does:
the system distinguishes "I am overruling your guess" from "I am vouching for
this claim", which is a distinction every other governance surface here
collapses.

### Rehearse the correction before committing it

Repos: `memora`; related staging in `hermes-agent`.

Any pass that can hide or delete memory in bulk should default to reporting what
it would do. Memora's supersession pipeline takes `dry_run: bool = True`, so a
sweep produces a reviewable list of proposed edges and changes nothing until
mutation is explicitly requested. This costs a keyword argument and turns an
operation with an unknowable blast radius into one an operator can read first.
It also makes the classifier measurable: the dry-run output is exactly the
artifact needed to count how often the pass would have been wrong. It fails if
the preview and the mutating path diverge, or if nobody actually reads the
report — a default that is always overridden is not a safeguard.

### Sample instead of rank, when recall feeds exploration

Repos: `loongflow`; adjacent in `voyager` and `verel`.

Deterministic top-*k* recall has a failure mode nobody else here names: if the
ranking function is slightly wrong, the same wrong memories surface every time
and the alternatives are never seen. LoongFlow's evolutionary memory samples a
remembered solution from a Boltzmann distribution over scores, with the
temperature driven by measured population diversity and bounded on both sides,
so a store that has collapsed toward sameness loosens selection until variety
returns. This is right only where remembered items inform *what to try next*
rather than *what is true* — the same mechanism applied to facts about a user
means the same question can get different answers. It also gives up
reproducibility, and nothing in LoongFlow provides a seed or replay path for
debugging a selection.

## 6. Antipatterns and Failure Modes

### Treating LLM-extracted facts as truth

Most systems extract with an LLM. Without trust state, provenance, and correction semantics, hallucinations become durable. `verel` addresses this directly; `honcho` preserves source events; `mem0`, `langmem`, `cognee`, `claude-mem`, `a-mem`, and `llm-wiki-memory` need stronger promotion guardrails.

`mempalace` is the clearest counterexample in this workspace: it makes verbatim evidence the primary store and treats derived structures as indexes. That does not solve truth, but it avoids losing the original context during extraction.

`daimon` is the sharpest counterexample, because it names the failure precisely
rather than routing around it. Verifying a quote proves the sentence was *said*;
it says nothing about whether the sentence was *right*, and the code comments
say so — the model concludes X, X is false, and the transcript faithfully
records the model saying X. The narrow fix it ships is the transferable part: for
claims that assert an *outcome*, demand a pointer to a tool result and downgrade
the claim when there is none. That covers exactly the class where a false memory
does the most damage — believing work is finished when it is not — and leaves
the general case openly unsolved rather than papered over with a confidence
score.

### Vector-only memory

Vector search misses exact constraints and can retrieve plausible but wrong memories. Every serious design should include lexical search or structured filters. `engram` demonstrates the value of boring FTS. `mempalace` demonstrates vector plus BM25 plus metadata plus fallback paths. `mem0` and `honcho` show hybrid approaches. `llm-wiki-memory` has strong metadata filters and deterministic topology lookup, but its lexical-hash mode is a fallback backend rather than a fused exact-search channel. Claude-Mem and A-MEM additionally show why having both lexical and vector code—or simply using Chroma—does not make an ordinary query path hybrid.

### Ranking positions used as identities

Retrieval order is ephemeral, not object identity. A-MEM shows the failure
directly: it returns vector rank positions and later applies them to insertion
order, so an LLM can rewrite a different neighbor than the one it saw. Carry
stable memory IDs through prompts, responses, validation, mutation, and audit.

### Recall@k without enforcing k

A retrieval benchmark is invalid at a stated cutoff if the system scores more than `k` returned items. Swafra's committed `k=10` artifact evaluated all returned sessions while returning 28–46 sessions per question (35.4 on average); it only truncated the displayed `retrieved_sessions` list. Benchmark harnesses should assert the result count, score exactly the first `k`, record token volume, and bind artifacts to a code/config/embedder manifest.

### Weak correction semantics

Pattern guide: [Rejected-value tombstone](../patterns/rejected-value-tombstone/).

Update/delete APIs are not enough. A system needs to model contradiction, supersession, source, timestamp, and rejected values. Otherwise a wrong fact can be reintroduced by later extraction. Verel's rejected tombstones are the clearest research-grade countermeasure; RainBox has adopted equivalent machinery in a product context: `MemoryRejectedValue` tombstones block future model re-assertion of rejected or superseded values, `correct_belief` is an atomic governed correction path, and write-time conflict detection is lattice-aware across the scope hierarchy. `llm-wiki-memory` shows the limit of operational supersession without epistemic state: it can archive a selected predecessor, but cannot prevent the rejected value from being distilled again.

### Semantic deletion

Deleting by "similar memory" is dangerous. It is useful as a discovery aid, but the actual forget operation should target exact IDs or require review. Supermemory's MCP client fallback semantic deletion is a risk pattern to treat carefully.

### Treating git deletion as privacy deletion

`llm-wiki-memory` removes exact leaves and embedding entries, but private wiki commits retain prior bodies. Git history is excellent for recovery and audit, but it is not an erasure guarantee. Any git-backed memory needs an explicit procedure for history rewriting, clones, backups, stashes, and derived caches.

### Core memory as a junk drawer

Editable prompt memory is powerful and dangerous. Letta's core memory tools are useful, but any system with long-lived core blocks needs provenance, review, and compaction policy. Otherwise it accumulates stale identity and preference claims.

### Tool descriptions as policy

Several systems rely on tool docs telling the agent when to save memory. This is necessary but insufficient. The backend still needs dedupe, conflict detection, trust gates, and review.

### Telemetry mistaken for truth

RainBox explicitly avoids this: retrieval events and downvotes are signals for inspection/evals, not automatic confidence changes or deletion. This matters because "memory was used in a bad answer" does not prove the memory was false.

`holographic` is the atlas's clearest counterexample, and it is worth studying precisely because the mechanism looks reasonable in isolation. A `fact_feedback` tool lets the model or user rate a fact helpful or unhelpful, adjusting a single `trust_score` by +0.05 or −0.10. That same score is multiplied directly into relevance during ranking *and* gates retrieval through a `min_trust` floor defaulting to 0.3. From the default trust of 0.5, three unhelpful ratings put a fact at 0.2 — below every default retrieval path, permanently, with no tombstone, no review queue, and no record that a suppression occurred. Feedback has quietly become deletion, and "unhelpful" has quietly become "false".

`atomic-agent` sits at the disciplined end of the same range. Votes are written
to an append-only `vote_events` table (`kind`, `target_id`, `direction`,
`session_id`, `turn_index`, `created_at`) and `vote_score` is a derived, indexed
column on memories, lessons, and profile facts. Because the raw events are
retained, a scoring rule can be recomputed, a suspicious pattern can be audited,
and no single vote is destructive — the atlas's own "keep retrieval events
append-only; derive counters from events" recommendation, implemented. Ranged
against Holographic's in-place mutation, RainBox's human gate, and MetaClaw's
replay-gated policy tuning, it is the option that preserves the most future
choices.

### The harness's own output captured as evidence

A system that generates text and also captures text will eventually capture its own output. `openclaw` strips media notes, context markers, reply headers, sender prefixes, and timestamps from every message before capture, then rejects whatever still `looksLikeEnvelopeSludge`. `holographic` had to exclude its host's compaction handoff summaries, which arrive as `role="user"` messages and reliably matched its own decision-extraction regexes, so the compactor's output was being stored as durable facts on every context rollover.

Both fixes arrived after the bug. Any system with automatic capture should have a test asserting that its own generated scaffolding — summaries, envelopes, tool wrappers, injected memory blocks — cannot re-enter as evidence.

### One score for truth and reachability

Separating epistemic confidence from retrieval strength is one of the atlas's recurring recommendations, and the new systems split cleanly on it. `openviking`'s `hotness_score` is explicitly a reachability signal blended into ranking and never touches correctness; `redis-agent-memory-server` keeps recency weights entirely inside ranking and retention. `holographic` collapses both into `trust_score`, so there is no way to ask for the most relevant memory independent of how it has been rated, and no way to record that a rarely-retrieved fact is nonetheless certainly true.

### Platform-only claims hidden behind OSS APIs

Mem0 and Supermemory both have product surfaces where advanced behavior may live outside the inspected source. For build decisions, separate what is visible in code from what is promised by hosted APIs.

`byterover` adds a licensing variant of the same problem: it is widely described as an open-source memory engine, but the repository inspected here carries the Elastic License 2.0, which prohibits offering the software as a hosted service. Check the `LICENSE` file rather than the positioning before planning to reuse anything.

### Published benchmark numbers without committed artifacts

The atlas has now found three variants of this. Swafra committed a `k=10` artifact that scored every returned session. TencentDB published gains with no harness in the repository at all. `openviking` is the most advanced case and the most nearly right: it commits a genuinely reproducible harness — ingest, QA, LLM judge, statistics, runners for six competing systems, and token accounting alongside accuracy, which is exactly what this atlas asks for — yet the headline figures in its README (LoCoMo accuracy of 82.08% versus 24.20% native for OpenClaw, and comparable deltas for Hermes and Claude Code) point to an off-repo blog post, and no raw result files are committed.

A reproducible harness and a reproducible result are different claims. See [benchmarking agent memory](../benchmarks/) for what the published numbers are and are not measuring. These are also vendor-run comparisons of "competitor's native memory" against "competitor plus our product", judged by an LLM, so the native baselines deserve independent scrutiny before the deltas are quoted.

### Throwing away raw evidence too early

Extraction-first systems can look elegant while deleting the only material needed to debug a wrong memory. MemPalace is the strongest evidence that raw text plus retrieval deserves to be the baseline before adding lossy summarization or fact extraction.

### Treating local JSON rewrites as durable storage

Swafra loads and rewrites chunks, edges, and sources as three independent JSON files. Without locks, atomic replace, transactions, repair, or cascading deletion, concurrent agents can lose writes and partial failure can split graph state. Human-readable export is valuable; it is not a substitute for transactional primary storage.

## 7. What Seems to Work

SQLite plus FTS works for local coding-agent memory. It gives inspectable state, transactional writes, simple backup/sync, and exact search. Engram, Verel, and Claude-Mem are good references. MemPalace shows how to combine local SQLite-style operational machinery with a vector backend and fallback BM25/FTS paths.

Hybrid retrieval is the default serious choice. Pair semantic search with lexical matching and metadata filters. Add reranking only after basic retrieval metrics exist. MemPalace's "closets boost but never gate drawers" rule is a particularly reusable retrieval principle.

Source diversity is useful when the context should cover sessions or documents rather than repeat adjacent chunks from one source. Swafra makes this explicit with best-chunk-per-source selection. The production version needs a hard result/token cap, stable source identity, and an escape hatch for questions requiring multiple chunks from one source.

Scope must be part of the primary design, not a later filter. User/agent/project/session/workspace boundaries determine whether recall is useful or harmful.

Make write destinations explicit in layered memory. `llm-wiki-memory` lets reads fan out across private and repository scopes while requiring every mutation to name a concrete target. This prevents a shared scope from silently becoming a shared write.

Keep raw evidence. Messages, source IDs, documents, drawers, and provenance make correction possible. Honcho, Verel, and MemPalace benefit from this; systems that only store extracted facts lose auditability.

Separate truth from usefulness. Retrieval strength should not mean the memory is true. Verel's split between `epistemic_confidence` and `retrieval_strength` is one of the strongest ideas in the workspace.

Render recalled memory defensively. Verel's untrusted-memory fence is a practical prompt-injection mitigation. Context should be quoted as data, not instructions.

Use small, explicit mutation APIs. Letta's append/replace/patch operations are easier to reason about than free-form "update my memory" text.

Record embedder identity. MemPalace's explicit model/dimension checks are a useful operational guardrail: a vector index searched with the wrong embedding model can silently degrade.

Make automatic capture recoverable. `llm-wiki-memory` preserves failed chunk inputs, raw fenced fallbacks, retry state, and provider provenance, which is a stronger failure posture than treating a failed summarization call as a lost session.

Keep capture model-independent. Agentmemory's synthetic observation path and
Claude-Mem's durable hook queue preserve the event before model compression.
Zero-LLM capture is the reliable floor; enrichment can be added later.

Treat semantic indexes as projections. Claude-Mem commits SQLite before
best-effort Chroma sync, and Cognee can retain sources while deleting and
rebuilding derived memory. The authoritative store and repair direction should
be obvious.

Make background derivation reversible by provenance. Cognee's pipeline-run
rollback is the strongest cross-store example in the atlas, even though it
cannot make every backend combination atomic.

Number your invariants and cite them from the code. `atomic-agent`'s schema
comments reference "cross-phase invariant 7 in `MEMORY_FABRIC_V2.md` §13.7",
invariant 20 on never auto-executing procedures, and invariant 21 bounding
distillation to one LLM call per cluster. It costs almost nothing and turns an
implicit constraint into a reviewable one — and across the atlas, nothing else
does it.

Ship new memory behaviour off by default until an evaluation says otherwise.
`atomic-agent`'s v2.5 features are all `default: false` while its campaign runs.

Put scope on the provider contract. `mateclaw`'s SPI carries an `ownerKey` on
`prefetch` and `syncTurn`, and its decorators give every backend retry and
metrics without per-plugin code — the two things the other host runtimes leave
to each plugin to solve, or not.

Test what memory must **not** surface. `open-cowork`'s eval cases carry
`forbiddenHits` alongside `expectedHits`, and a leak floors the case score
regardless of how much correct material was also retrieved. Every "tests to
require" list in the pattern library asks for scope-leakage, rejected-value, and
sensitivity assertions; this is what they look like as an executable fixture.

Score the prompt prefix, not the retriever. Between retrieval and the model sit
truncation, deduplication, ordering, and formatting — any of which can drop a
memory that retrieval correctly found. `open-cowork` scores what reached the
model.

Separate durability from importance. `mercury-agent` grades confidence,
importance, and durability independently, which is the schema-level answer to
this atlas's warning against applying one half-life to every memory kind.

Write your memory decisions down. `gini-agent` keeps ADRs recording the
decision, its context, and the failure that motivated it — its per-agent
isolation ADR states plainly that a coding agent's pinned memories were
polluting a research agent's recall. Across one hundred and eleven systems, almost none can
explain why they are shaped the way they are.

Make scope structurally inseparable from the query. OpenClaw composes agent scope and user filter into a single predicate so an unscoped read is not expressible, and scopes deletes the same way. This is stronger than applying a scope filter somewhere in the read path, and it is the kind of guarantee that survives refactoring.

Specify retention as a policy, not a TTL. Redis Agent Memory Server's `select_ids_for_forgetting` combines age and inactivity so recent use buys a memory time but not immunity, honours pinning and per-type allowlists, and prunes to a budget using separate half-lives for last access and creation. Most systems here either never forget or forget on one crude axis.

Guard generated rewrites against deletion. ByteRover's structural-loss detection parses before and after, counts only what would be removed, and merges it back. It is a few hundred lines, requires no model, and directly addresses the reason this atlas warns against premature summarization.

Sanitize your own scaffolding out of captured text, and test that it stays out. Two systems in the Hermes/OpenClaw ecosystem shipped fixes for their own generated text being stored as user memory.

Make memory use inspectable. RainBox's debug rows, retrieval events, and review UI are the best reference here. Users need to know which memories entered a prompt and need a way to correct or reject them.

Separate event time from ingestion time when facts change. Graphiti's bi-temporal edges preserve historical truth and backfilled events without destructive overwrite.

Decay reachability, not truth. Verel keeps retrieval strength separate from
confidence and protects important lifecycle states. Reinforcement should record
usefulness or corroboration, never silently upgrade factual authority.

Prepare compaction before the context cliff. Mastra Observational Memory's inactive buffers and exact coverage ranges make expensive observation/reflection recoverable and mostly non-blocking.

Keep human-owned source canonical when that is the product promise. Basic Memory's Markdown/projection boundary makes memory portable and repairable, provided every derived index has a reconciliation path.

Name the physical memory form. MemOS usefully expands memory beyond text, but KV cache, graph text, and LoRA memory need different compatibility, deletion, and evaluation guarantees.

## 8. What I Would Build

### Ship First

Build a local-first core even if a hosted version is planned later.

Data model:

- `event`: raw messages, tool calls, documents, user assertions, timestamps, actor IDs.
- `evidence_chunk`: verbatim text chunk with source path/session, line/span, authored/filed time, deterministic ID, embedding ID, and scope.
- `memory`: extracted or manually saved claim with `kind`, `subject`, `predicate`, `text`, `scope`, `status`, `confidence`, `retrieval_strength`, `source_event_ids`, `created_at`, `updated_at`.
- `memory_evidence`: append-only provenance rows, not a mutable field on `memory`.
- `memory_relation`: `supersedes`, `contradicts`, `supports`, `derived_from`, `same_as`.
- `rejected_value`: tombstone for values that should not be silently reintroduced.
- `embedding`: optional vector table or external vector ID.
- `retrieval_event`: append-only events for retrieved, used/injected, rejected, downvoted, considered.

Status should start simple:

- `candidate`
- `verified`
- `rejected`
- `stale`

Write path:

1. Store raw evidence first without requiring an LLM call.
2. Chunk deterministically and record embedder identity.
3. Index raw evidence with lexical and vector paths.
4. Extract candidate facts with schema-constrained LLM output only after evidence is durable.
5. Search for same subject/predicate and near duplicates.
6. If same key plus same value, corroborate.
7. If same key plus different value, create a conflict or supersession.
8. Do not auto-promote to verified unless the source is trusted or corroborated.
9. Preserve failed extraction inputs and make background work safely retryable.
10. Store enrichment state so raw memory remains searchable while derivation is pending.

Retrieval path:

1. Apply hard scope filters.
2. Run lexical search and vector search.
3. Retrieve raw evidence directly as the floor.
4. Let derived indexes/summaries/entities boost rank, not gate evidence.
5. Blend with recency, confidence, retrieval strength, and trust status.
6. Suppress rejected records from normal recall but use rejected tombstones during write conflict checks.
7. Return compact, source-linked results.

Context assembly:

- Token-budgeted.
- Verified first, then high-confidence candidates if needed.
- Group by subject or task.
- Fence as recalled data, not instructions.
- Include source or confidence markers when possible.
- Record which memories entered context.

Agent integration:

- MCP tools for `remember`, `recall`, `judge`, `forget`, and `context`.
- SDK methods with the same semantics.
- Tool calls should be small and boring; policy belongs in the backend.
- Review UI or API for activate/reject/correct/sensitivity/expiry.
- Confirm-tier write intents for high-impact assistant-proposed memory changes.
- Let reads span allowed scopes, but require an explicit destination for every write.

Testing:

- Extraction golden tests.
- Conflict/supersession tests.
- Retrieval recall/precision fixtures.
- Hard assertions that a benchmark labeled `@k` scores exactly the first `k` results and records token volume.
- Prompt-injection tests for recalled content.
- Deletion/privacy tests.
- Scope leakage tests.
- Telemetry and feedback-to-eval tests.
- Regression corpus of wrong memories that must not reappear.

### Add Later

- Background consolidation from failures into candidate rules.
- Promotion gates using held-out task suites.
- Entity graph linking with indexed, intentional edge direction and cascading deletion.
- Closet-style source indexes and neighbor expansion.
- Hosted multi-tenant API.
- Cross-device sync.
- UI for memory review and conflict resolution.
- Retrieval telemetry dashboards and feedback/eval promotion.
- Temporal reasoning and decay.

Do not add background summarization before raw-evidence retrieval and correction semantics exist. Summaries are compressed belief; if the system cannot explain and repair a belief, summarization hides the problem.

## 9. Repo-by-Repo Verdicts

**This section covers 64 of the 97 reports.** It was written when the
corpus was small enough to enumerate and has not kept pace with it, so a system
missing here has not been judged and found unremarkable — it has not been
written up in this format. The [capability index](../capabilities/) and the
comparative matrix above are generated from every report's frontmatter and are
complete by construction; this section is hand-written and is not. Stated rather
than left to be discovered, because the distinction between *assessed and
carries nothing* and *nobody wrote the paragraph* is the same one the
[rubric](../methodology/atlas-rubric/) enforces for capability marks, where the
build fails if a report omits the key. No equivalent guard exists here.

### `mem0`

- Best idea: pragmatic additive extraction plus hybrid retrieval/entity boost.
- Biggest risk: extracted facts are not strongly modeled as uncertain claims.
- Most reusable component: `Memory.add()` / `_add_to_vector_store()` pipeline.
- Maturity impression: practical SDK core, with some advanced features outside OSS.
- Study when: building a drop-in memory library.
- Do not copy when: you need rigorous trust/correction semantics.

### `langmem`

- Best idea: memory as LangGraph store tools with schema-driven extraction.
- Biggest risk: it is a primitive layer, not a full memory policy.
- Most reusable component: `create_manage_memory_tool()` and namespace templates.
- Maturity impression: clean and framework-native.
- Study when: already building on LangGraph.
- Do not copy when: you need a standalone memory service with built-in quality controls.

### `honcho`

- Best idea: event stream to derived working representation.
- Biggest risk: operational complexity and background consistency.
- Most reusable component: message ingestion plus deriver/representation flow.
- Maturity impression: serious service architecture with meaningful tests.
- Study when: modeling users/peers/sessions over time.
- Do not copy when: all you need is a local memory file.

### `engram`

- Best idea: local SQLite/FTS MCP memory with conflict-oriented writes.
- Biggest risk: lexical retrieval and agent-mediated judgment may hit limits.
- Most reusable component: `AddObservation()` and MCP `handleSave()`.
- Maturity impression: compact, inspectable, purpose-built for coding agents.
- Study when: building local developer-agent memory.
- Do not copy when: you need hosted multi-tenant vector retrieval.

### `mempalace`

- Best idea: verbatim drawers as the authoritative memory, with hybrid retrieval and extracted indexes as boosts.
- Biggest risk: raw stores get large/noisy and do not resolve contradictions by themselves.
- Most reusable component: `search_memories()` plus `_hybrid_rank()`, and the mining/write path around deterministic IDs.
- Maturity impression: operationally mature local system with broad tests, integrations, repair tooling, and benchmark artifacts.
- Study when: building local-first coding-agent memory or testing whether extraction is actually needed.
- Do not copy when: you need compact verified user facts as the primary memory surface.

### `swafra`

- Best idea: compact source-diverse hybrid retrieval with explicit graph exploration and no required cloud model.
- Biggest risk: non-atomic global JSON state plus a benchmark that scores far more than the advertised `k`.
- Most reusable component: the conceptual `search_knowledge()` -> `graph_walk()` -> best-per-source composition, not the persistence implementation.
- Maturity impression: promising alpha prototype with significant code/docs/artifact drift and no ordinary tests.
- Study when: learning how little code a local MCP graph-RAG memory can require.
- Do not copy when: you need concurrency, trustworthy evals, scope isolation, correction, bounded prompts, or durable storage.

### `llm-wiki-memory`

- Best idea: recoverable hook capture plus explicit federated write targets over inspectable Markdown/git memory.
- Biggest risk: LLM-distilled atoms become active guidance without candidate/verified/rejected state or contradiction protection.
- Most reusable component: `wiki-mutate.mjs` / `wiki-search*.mjs` with the flush, compile, scope, and commit orchestration around them.
- Maturity impression: operationally mature local coding-agent system with unusually broad failure-path and federation tests; retrieval quality is not benchmarked.
- Study when: building cross-agent local project memory, lifecycle capture, deterministic wiki placement, or self-healing maintenance.
- Do not copy when: you need high-stakes truth governance, large-corpus query performance, multi-tenant access control, or privacy-grade deletion.

### `rainbox`

Disclosure: RainBox is the atlas author's own project; this verdict is a self-assessment against the shared rubric.

- Best idea: claim/evidence memory tied to governed writes (single `record_belief` path, five-actor trust model, tombstones, conflict detection), review UI, retrieval telemetry, feedback, and eval gates.
- Biggest risk: active compact claims can steer behavior while losing nuance from original source context; no automatic candidate extraction means claims enter only through explicit writes.
- Most reusable component: `MemoryClaim`/`MemoryEvidence`/`MemoryRejectedValue`/`RetrievalEvent` model, `record_belief`/`correct_belief` governed write paths, `retrieve_memories_hybrid()`.
- Maturity impression: strong app-integrated memory subsystem with trust/correction machinery comparable to Verel's correctness properties, broad tests, and operator workflows.
- Study when: building an assistant product where memory must be inspectable, governable, and protected against model-write laundering.
- Do not copy when: you need a small embeddable library, raw transcript recall as the primary memory layer, or `epistemic_confidence`/`retrieval_strength` driving ranking (these columns are schema groundwork only; Tier-1 ranking still uses `confidence`).

### `letta`

- Best idea: core vs archival vs conversation memory inside the runtime.
- Biggest risk: agent-editable core memory without a strong truth model.
- Most reusable component: memory block compile/mutation and patch-style edits.
- Maturity impression: deep runtime integration with compatibility complexity.
- Study when: building an agent platform, not just a memory backend.
- Do not copy when: you want a small independent memory service.

### `supermemory`

- Best idea: product-grade API shape around documents, chunks, memory entries, spaces, profiles, SDKs, and MCP.
- Biggest risk: the hosted backend core is not visible here.
- Most reusable component: schemas and adapter surfaces.
- Maturity impression: polished integration surface; implementation evidence incomplete.
- Study when: designing public APIs and memory UX.
- Do not copy when: you need open implementation details for extraction/ranking.

### `verel`

- Best idea: explicit trust, confidence, retrieval strength, rejected tombstones, and defensive recall.
- Biggest risk: complexity.
- Most reusable component: `MemoryRecord`, `LocalMemory.write()`, and `recall_budgeted()`.
- Maturity impression: research-grade correctness focus with strong targeted tests.
- Study when: wrong memory is costly.
- Do not copy wholesale when: you need a fast MVP.

### `hindsight`

- Best idea: four independent recall arms plus task-specific fusion over evidence-backed facts and observations.
- Biggest risk: LLM-extracted and consolidated claims can become durable without an explicit truth state.
- Most reusable component: retain pipeline and `engine/search/` fusion/reranking stack.
- Maturity impression: service-grade implementation with unusually strong operational coverage.
- Study when: building a hosted retain/recall/reflect service.
- Do not copy when: a small local store can meet the evaluated retrieval need.

### `graphiti`

- Best idea: bi-temporal relationship edges that close validity intervals without erasing history.
- Biggest risk: entity-resolution or invalidation mistakes reshape a large portion of the graph.
- Most reusable component: episode/evidence model plus temporal edge maintenance.
- Maturity impression: substantial graph library with multiple drivers and deep search configuration.
- Study when: facts, relationships, and their validity change over time.
- Do not copy when: memory is mostly independent notes or stable preferences.

### `mastra-observational-memory`

- Best idea: compute observation/reflection buffers early, persist exact coverage, and activate without blocking.
- Biggest risk: progressive summary drift and in-process-only locking.
- Most reusable component: marker/range-aware buffered activation.
- Maturity impression: deeply integrated and heavily tested framework feature.
- Study when: long agent conversations exceed model context.
- Do not copy when: exact evidence retrieval is the primary requirement.

### `memos`

- Best idea: mount textual, preference, skill, KV-cache, and parametric memory as one cube.
- Biggest risk: one abstraction hides uneven backend guarantees and maturity.
- Most reusable component: memory-cube packaging and textual-to-activation scheduling.
- Maturity impression: ambitious research/engineering substrate with many configurations.
- Study when: exploring model-native memory or deployable heterogeneous memory bundles.
- Do not copy when: a single audited text store is sufficient.

### `basic-memory`

- Best idea: canonical human-editable Markdown with graph/search state treated as rebuildable projection.
- Biggest risk: bidirectional file/database synchronization and direct agent writes to canonical knowledge.
- Most reusable component: accepted-note transaction/reconciliation boundary and typed MCP client flow.
- Maturity impression: operationally serious local/cloud knowledge system with broad parity tests.
- Study when: people and agents must share portable project knowledge.
- Do not copy when: humans never edit memory and filesystem ownership adds no value.

### `agentmemory`

- Best idea: zero-LLM hook capture plus compact-first hybrid search and explicit expansion.
- Biggest risk: a large optional surface and similarity-based supersession without an epistemic review state.
- Most reusable component: `mem::observe`, `HybridSearch`, and `mem::smart-search`.
- Maturity impression: ambitious, heavily tested coding-agent runtime with many operational paths.
- Study when: hooks, local capture, hybrid recall, and later consolidation need to coexist.
- Do not copy when: a small auditable store is enough or shared-by-default agent memory is unsafe.

### `tencentdb-agent-memory`

- Best idea: progressive disclosure from raw evidence through records, scenes, persona, and navigable tool-output maps.
- Biggest risk: non-atomic JSONL/store updates and fail-open deduplication can create loss or contradictions.
- Most reusable component: L0/L1/L2/L3 context split and symbolic offload drill-down.
- Maturity impression: inventive OpenClaw/Hermes integration, but central lifecycle tests and reproducible benchmark evidence are thin.
- Study when: tool-heavy sessions exceed the context window and raw drill-down must remain possible.
- Do not copy when: authoritative cross-store consistency, multi-tenant boundaries, or verified memory are required.

### `cognee`

- Best idea: source-preserving, ontology-aware graph/vector pipelines with provenance rollback behind a small remember/recall API.
- Biggest risk: probabilistic extraction and a large adapter/configuration surface create cross-store consistency and policy burden.
- Most reusable component: permanent `remember()` as add-plus-cognify, dataset authorization, and pipeline-run rollback.
- Maturity impression: substantial platform with broad tests and transparent but preliminary BEAM artifacts.
- Study when: agents need multimodal ingestion, typed knowledge graphs, ontologies, dataset permissions, and backend choice.
- Do not copy when: a small local evidence store and lexical/vector retrieval satisfy the requirement.

### `claude-mem`

- Best idea: durable hook queue, canonical SQLite commit, then best-effort semantic/cloud projections and bounded timeline injection.
- Biggest risk: generated observations become active without epistemic review, and ordinary text search does not fuse its FTS and Chroma capabilities.
- Most reusable component: `pending_messages` lifecycle plus `ResponseProcessor` commit/acknowledgement ordering.
- Maturity impression: operationally mature coding-agent sidecar with broad failure-path tests; memory quality is not benchmarked.
- Study when: cross-session coding context must be captured automatically without blocking the agent.
- Do not copy when: explicit writes are sufficient, hooks are unavailable, or high-stakes facts require verification before use.

### `holographic`

- Best idea: deterministic SHA-256-derived phase vectors and algebraic multi-entity queries, with no embedding model to version.
- Biggest risk: three unhelpful ratings silently drop a fact below the retrieval floor forever.
- Most reusable component: `encode_atom`/`bind`/`unbind`, the FTS5 query sanitizer, and the refcounted shared-connection registry.
- Maturity impression: compact and fully readable, with real production scar tissue around concurrency, but no benchmark and an unmeasured HRR contribution.
- Study when: you want compositional structure without an embedding service, or a worked example of why truth and usefulness must be separate fields.
- Do not copy when: you need scope, provenance, correction, or any feedback mechanism that is not also a deletion mechanism.

### `hermes-agent`

- Best idea: bounded curated memory frozen into the prompt at session start, with overflow refused and consolidation demanded in-turn.
- Biggest risk: whatever the model writes is authoritative in every later session, and budget-driven eviction is unlogged.
- Most reusable component: the frozen-snapshot pattern, `_detect_external_drift`, and the staged write-approval gate.
- Maturity impression: heavily defended file layer whose guards cite the incidents that produced them; the provider contract is less complete than the store.
- Study when: prompt-cache cost is material, or you need memory that cannot grow without someone deciding what to drop.
- Do not copy when: you need verification, tombstones, substring-free identity, or a provider contract that can honour deletion.

### `openviking`

- Best idea: three retrievable granularities on one record, plus hotness kept strictly separate from confidence.
- Biggest risk: extraction becomes durable context with no verification tier, and published numbers are not backed by committed artifacts.
- Most reusable component: `hotness_score`, `type_quota_recall`, and the `user_space` / `peers/<id>` isolation convention.
- Maturity impression: a large, seriously engineered platform with real multi-tenancy and the most complete benchmark harness in the atlas.
- Study when: you need multimodal ingestion, tenant isolation, skills and resources unified with memory, or backend choice.
- Do not copy when: you need a small embeddable layer, verified memory, or a licence compatible with closed distribution — this is AGPL-3.0.

### `redis-agent-memory-server`

- Best idea: TTL-native working memory promoting into deduplicated long-term memory, with retention expressed as a real policy.
- Biggest risk: forgetting is deletion without tombstones, so anything forgotten can be re-extracted.
- Most reusable component: `select_ids_for_forgetting`, the three-layer dedupe chain, and `_semantic_merge_group_is_cohesive`.
- Maturity impression: vendor-neutral reference implementation with unusually well-targeted tests on the risky logic.
- Study when: you want the working/long-term split done carefully, or a retention policy you can defend to a user.
- Do not copy when: cognitive memory types would be mistaken for a trust model, or deletion must be durable.

### `byterover`

- Best idea: counting exactly what an LLM rewrite would delete, then merging the loss back automatically.
- Biggest risk: the Elastic License 2.0 forbids hosted redistribution, and the memory core itself has no trust, scope, or correction model.
- Most reusable component: `detectStructuralLoss` / `resolveStructuralLoss`, and the immutable `DECISIONS` category.
- Maturity impression: a thin memory primitive attached to a more thoughtful knowledge-curation layer, with no visible tests on its best idea.
- Study when: an LLM is allowed to rewrite stored knowledge and you need a cheap deterministic guard.
- Do not copy when: you need durable beliefs, ranked retrieval, or an OSI-compatible licence.

### `openclaw`

- Best idea: scope composed inseparably into every predicate, and 567 lines spent keeping the runtime's own envelope out of memory.
- Biggest risk: a vector-only reference backend for content full of names and identifiers, with auto-capture that can undo deletions.
- Most reusable component: `memory-capture-sanitization.ts`, `scopedPredicate`, and the doctor-contract idea.
- Maturity impression: test lines far exceed implementation lines; the plugin contract is mature, the memory model deliberately minimal.
- Study when: building a host runtime with swappable memory, or capturing from a channel that wraps messages in scaffolding.
- Do not copy when: you need hybrid retrieval, per-user scope inside an agent, or deletion that survives auto-capture.

### `atomic-agent`

- Best idea: numbered cross-phase invariants cited from the schema into a design document, and votes kept as append-only events with derived scores.
- Biggest risk: an elaborate opt-in surface whose evaluation campaign has no committed results.
- Most reusable component: the invariant-citation practice, the `vote_events` shape, and the surfaced-id allowlist in `neighbor-evolver.ts`.
- Maturity impression: the most specification-like memory system in the atlas — design plan, acceptance criteria, implementation ledger, and features default-off pending evidence.
- Study when: you want memory built as an engineering artifact rather than an accretion, or a feedback design that keeps every downstream option open.
- Do not copy when: you need a value tombstone or an established scope model; neither surfaced here.

### `mateclaw`

- Best idea: a provider SPI that carries an owner key, with retry and metrics as decorators over every backend.
- Biggest risk: the contract still has no deletion hook, and contradiction is detected without a resolution path.
- Most reusable component: the SPI shape with scoped overloads and default methods, and `spi/decorator/`.
- Maturity impression: built in the enterprise-framework tradition — layered, dependency-injected, event-driven, and conventional in the ways that tradition is good at.
- Study when: designing a memory contract third parties will implement, or wondering who owns provider resilience.
- Do not copy when: you need the deletion half of the governance story, which is absent.

### `llamaindex`

- Best idea: one token budget split between chat history and blocks, with each block truncating itself to fit.
- Biggest risk: no provenance, correction, or scope, and long-term capture is triggered by conversation length rather than importance.
- Most reusable component: the `BaseMemoryBlock` contract — `aget`, `aput`, `atruncate` — and the explicit budget split.
- Maturity impression: a widely deployed framework whose newer block API is a real memory layer, shipped alongside an older window-management API of the same name.
- Study when: you need a memory component contract, or a budget that several contributors must share.
- Do not copy when: facts must be traceable, correctable, or scoped — those are left to the application.

### `open-cowork`

- Best idea: a committed memory benchmark whose queries assert forbidden hits as well as expected ones, scored against the assembled prompt prefix.
- Biggest risk: the harness exists but no scored results are committed, and no trust state guards extraction.
- Most reusable component: `memory-eval-harness.ts` — the eval-case shape is largely independent of the rest of the system.
- Maturity impression: a well-factored memory subsystem whose evaluation thinking is ahead of most of the atlas.
- Study when: you need to turn "our memory works" into something a CI job can check.
- Do not copy when: you need verification or correction semantics; neither appears in the module set.

### `gini-agent`

- Best idea: bi-temporal units with `rejected` and `conflicted` states, four RRF-fused recall channels, and architecture decisions recorded as ADRs.
- Biggest risk: `conflicted` is modelled with no visible workflow to resolve it, and rejection has no value-level tombstone.
- Most reusable component: the `memory_units` schema, and the ADR practice itself.
- Maturity impression: a faithful local reimplementation of a published memory model, with unusually good written rationale.
- Study when: you want a trust-and-time-aware unit schema you can implement in plain SQLite.
- Do not copy when: you need the conflict workflow the schema implies but does not ship.

### `moltis`

- Best idea: a no-embeddings mode that is a constructor and a predicate rather than a degraded state, plus content-hash file addressing.
- Biggest risk: exported session transcripts share one index and one rank with curated notes, with nothing distinguishing them.
- Most reusable component: `MemoryManager::keyword_only()` / `has_embeddings()`, and the single `sync()` chokepoint.
- Maturity impression: carefully built, with feature-gated backends and committed plans naming its own gaps.
- Study when: memory and documents should be one substrate, or you need a genuinely offline path.
- Do not copy when: a chunk is not a good enough unit — there is no claim, status, or correction record.

### `mercury-agent`

- Best idea: three independent grades — confidence, importance, durability — plus a subconscious tier and a user-facing learning pause.
- Biggest risk: `dismissed` is a boolean, so dismissal is not durable against re-extraction.
- Most reusable component: the record model, especially the durability/importance split and the narrowed candidate type.
- Maturity impression: small but opinionated, with an operator review page and clear provenance kinds.
- Study when: building personal memory where different facts should live for different lengths of time.
- Do not copy when: automatic extraction can regenerate what a user dismissed.

### `waku-agent`

- Best idea: a small-model gate that decides whether to retrieve at all, returns the query when it says yes, and fails open when it errors.
- Biggest risk: the gate's own accuracy is unmeasured, and a false negative is invisible.
- Most reusable component: `should_retrieve()` — the fail-open branch and the recorded reason included.
- Maturity impression: small, opinionated, and unusually clear about why each expensive step is conditional; deterministic evals for memory behaviour.
- Study when: retrieval runs every turn and you suspect it is hurting as often as helping.
- Do not copy when: you need correction, scope, or trust — none of the three exists here.

### `metaclaw`

- Best idea: candidate retrieval policies replayed offline and promoted only on non-regression across eight metrics.
- Biggest risk: the loop optimizes lexical-overlap proxies, and its promotion thresholds are hand-chosen constants.
- Most reusable component: `promotion.py`'s `MemoryPromotionCriteria` and the replay-then-gate loop in `self_upgrade.py`.
- Maturity impression: substantial and unusually well evidenced, with committed benchmark fixtures and dedicated memory ablations.
- Study when: you cannot justify your retrieval weights and want a safe way to change them.
- Do not copy when: you need trust semantics — the memory model has no rejected state and no verification path.

### `nanobot`

- Best idea: two cursors over an append-only archive, with a Dream pass that refuses to advance after tool errors.
- Biggest risk: durable claims carry no provenance back to the evidence that produced them.
- Most reusable component: the dual-cursor split, the failure-aware advance gate, and the durable-file allowlist for audit commits.
- Maturity impression: compact and carefully reasoned, with unusually good design documentation and no visible memory tests.
- Study when: a fast producer feeds a slow consolidator, or you want git history that reads as a record of belief.
- Do not copy when: memory must grow past what fits in every prompt, or must be scoped per project.

### `cowagent`

- Best idea: a dated intermediate layer that gives consolidation a naturally bounded unit, plus written distillation rules and a dream diary.
- Biggest risk: two chained lossy summarizations with no loss detection, and recency-wins conflict resolution.
- Most reusable component: the daily-bucket pipeline, the distillation rule table, and the self-healing FTS5 state check.
- Maturity impression: practical and well documented, with real hybrid retrieval and no visible memory tests.
- Study when: you want consolidation you can inspect by opening a file for a given day.
- Do not copy when: scope matters — `scope` defaults to `shared` — or corrections must be reviewable.

### `genericagent`

- Best idea: "No Execution, No Memory", and an explicit ROI model for what earns a place in always-injected context.
- Biggest risk: every rule is prose, with no enforcement, no audit, and no record of the verification each write claims.
- Most reusable component: the four axioms and the cleanup SOP's ROI test and deletion categories.
- Maturity impression: a small framework whose memory thinking is considerably more developed than its memory machinery.
- Study when: designing the policy layer of a memory system, or deciding what belongs in permanent context.
- Do not copy when: wrong memory is costly and you need the rules enforced rather than requested.

### `magic-context`

- Best idea: memories mapped to backing files and re-verified when git reports those files changed, with lifecycle and verification on separate axes.
- Biggest risk: no rejected-value tombstone, so archived memories can be re-derived; and the verification verdict is still an LLM call.
- Most reusable component: `dreamer/verify-gate.ts`, the two-axis state model, and `(memory_id, model_id)` embedding keys.
- Maturity impression: the heaviest test posture in the atlas — 473 test files, seventy tested migrations, CAS-race suites, fail-closed registration.
- Study when: memory describes an inspectable artifact and you want trust to be observed rather than judged.
- Do not copy when: you need a small memory layer; most projects want the verify gate and the state model, not the whole platform.

### `pi`

- Best idea: deterministic `readFiles`/`modifiedFiles` manifests attached to compaction entries, derived from tool calls rather than from the summarizing model.
- Biggest risk: no memory contract at all, so scope and deletion have nowhere to live and every plugin reinvents indexing.
- Most reusable component: the typed session-entry model and the result-returning extension events.
- Maturity impression: actively developed, well-factored harness; memory is deliberately out of scope.
- Study when: designing a host runtime, or thinking about what branchable sessions mean for memory.
- Do not copy when: you expect third-party memory — define scope and deletion in the interface before plugins exist.

### `hipporag`

- Best idea: Personalized PageRank diffusion replaces hop planning, with IDF-penalized seeding and a weak dense prior.
- Biggest risk: no scope, trust, provenance, or temporal model, and a wrong extracted edge has graph-wide blast radius.
- Most reusable component: `graph_search_with_fact_entities()` plus `run_ppr()`, and synonymy-as-edges instead of entity merging.
- Maturity impression: actively maintained research framework with a strong reproduction tree and thin unit tests.
- Study when: recall must cross documents associatively, or entity-resolution merges have burned you.
- Do not copy when: you need agent memory rather than corpus QA — scope, correction, and time all have to be added.

### `voyager`

- Best idea: memory written only after the environment verifies the procedure worked.
- Biggest risk: a frozen 2023 artifact that generalizes from a single verified run and keeps no failure memory.
- Most reusable component: the verified write gate, and description-indexed / code-retrieved storage.
- Maturity impression: a 127-line memory subsystem inside a research agent; unmaintained since July 2023.
- Study when: your agent's actions have observable outcomes and competence is worth remembering, not just facts.
- Do not copy when: procedures will be executed outside a sandbox, or success is a matter of judgment rather than observation.

### `generative-agents`

- Best idea: consolidation triggered by accumulated significance rather than by a timer or token count.
- Biggest risk: its famous retrieval weights are hand-tuned constants, and reflections share one pool with observations.
- Most reusable component: the reflection trigger, and the three-signal retrieval structure — recalibrated, with time-based recency.
- Maturity impression: the field's reference architecture, frozen since August 2023 and never engineered for production.
- Study when: you want to understand where most of this atlas came from, or need a consolidation schedule that tracks salience.
- Do not copy when: you need any operational property at all — there is no scope, correction, deletion, or index.

### `a-mem`

- Best idea: small linked notes whose organization can be reconsidered when new memory arrives.
- Biggest risk: rank positions are used as note identities, allowing evolution to mutate the wrong neighbor.
- Most reusable component: the proposed Zettelkasten evolution protocol, after replacing direct mutation with validated change proposals.
- Maturity impression: research prototype; tests are shallow around the most consequential behavior and benchmarks live elsewhere.
- Study when: researching adaptive linked-note organization.
- Do not copy as a production core without stable IDs, canonical durability, scope, provenance, transactions, and trust state.

### `memora`

- Best idea: automated supersession that defaults to a dry run, so a correction sweep is previewed before it hides anything.
- Biggest risk: supersession without a tombstone, in a system that ingests documents and images and can therefore re-ingest what it hid.
- Most reusable component: the six-way relation vocabulary with neutral A/B presentation, and `dry_run: bool = True` as the default posture.
- Maturity impression: substantial for its age, with the sophistication concentrated in what happens to memories after they are written.
- Study when: you are about to run an automatic dedupe or supersession pass over a store you cannot afford to damage.
- Do not copy when: you need trust state, scope isolation, or a correction that survives re-ingestion.

### `loongflow`

- Best idea: recall by Boltzmann sampling at a temperature driven by the store's measured diversity — the only stochastic retrieval in the atlas.
- Biggest risk: selection quality is bounded entirely by a `score` nothing validates, and the same query can return different memories with no seed or replay path.
- Most reusable component: the diversity-to-temperature loop, including the 20% smoothing and the explicit min/max bounds.
- Maturity impression: two unrelated memory models in one package — a conventional tier stack and a genuinely novel selection mechanism — with the control constants undefended.
- Study when: memory feeds a search or generate-and-test loop and deterministic top-*k* keeps returning the same dead end.
- Do not copy when: recall must be reproducible, or the memories are facts rather than attempts.

### `core-memory`

- Best idea: epistemic grounding caps the confidence ladder, so a speculative record cannot reach canonical status by any amount of use.
- Biggest risk: correction is record-keyed, so supersession and rejection do not stop re-extraction from retained turns.
- Most reusable component: the grounding-to-ceiling table plus the monotonic class, which is a lookup and a `min()`.
- Maturity impression: the largest and most specification-like system in the atlas, with 300+ tests tracking the risky logic and committed benchmark harnesses.
- Study when: you need to explain why an incorrect memory never became permanent, and want the answer to be structural.
- Do not copy when: you cannot carry the surface — thirteen subpackages and forty store-ops modules is a real maintenance budget.

### `memanto`

- Best idea: a conflict workflow that terminates in a human decision, including `keep_both` and a human-authored `manual` resolution.
- Biggest risk: detection is one unmeasured LLM pass, and resolution deletes without a tombstone, so scheduled extraction can undo it.
- Most reusable component: the five-action resolver plus the bounded-scan instruction that keeps the nightly pass linear.
- Maturity impression: a real service with CLI, web UI, MCP and four framework integrations, and an unusually on-topic test tree.
- Study when: you have contradiction detection and no idea what to do with the flags it produces.
- Do not copy when: you need trust state or ranking you can inspect — storage is the vendor's own service.

### `memory-engine`

- Best idea: agents are access-control principals, and a delegated agent grant clamps to `least(agent, owner)` at every path, so over-granting cannot escalate.
- Biggest risk: no trust state, supersession, or tombstone — it governs who may read a memory and knows nothing about whether it is true.
- Most reusable component: the `tree_access` model with the agent clamp, and authorization evaluated inside the ranking query.
- Maturity impression: a serious database-native service with committed SQL benchmarks, access diagnostics, and unusually candid design notes including a negative result on RLS.
- Study when: agents write to shared memory and you cannot say from the schema which memories each may read.
- Do not copy when: you need correction semantics — `replace` overwrites in place and leaves no history.

### `ai-memory`

- Best idea: a `Handoff` with an open/accepted/expired lifecycle, typed sender and recipient, and an `open_questions` list — memory of what is *not* known.
- Biggest risk: hooks re-capture every session and supersession is page-keyed, so a deleted page returns through the path that first produced it.
- Most reusable component: `handoff.rs`, which is small and independent of the rest of the system.
- Maturity impression: broad and well packaged, with harness adapters for eight agents and committed prior-art analyses of four systems in this atlas.
- Study when: work is interrupted and resumed in a different harness, and re-explaining the state is the actual cost.
- Do not copy when: you need trust state — and do not assume its `do_not_answer_from` tag does anything; it appears only in a test fixture.

### `ctx`

- Best idea: a write-scope guard on the consolidation pass, with one crossing gated on the disposition rather than the caller, plus refusals that carry a registered reason.
- Biggest risk: correction is structural folding with no tombstone, so a dream can re-propose what a human folded away.
- Most reusable component: `WriteScope`, and the corrupted-artifact regression corpus, which any system with an LLM rewrite path could adopt in an afternoon.
- Maturity impression: dense tests in the packages that matter, an append-only ledger, and a 61,000-line CLI wrapped around them.
- Study when: a background model pass can write into the user's own repository and you have no answer for where it may write.
- Do not copy when: you need ranked retrieval — there is no ranker, only progressive disclosure over files.

### `optmem`

- Best idea: no background work at all — consolidation is requested inline in the output of `note`, so write-to-readable lag is zero and nothing rewrites memory unobserved.
- Biggest risk: no licence file, so nothing here is reusable; and a wrong memory is permanent, because the log is never edited.
- Most reusable component: the `cover` geometry — one parameter, closed form, and no compression at all while everything fits.
- Maturity impression: 860 lines with a 611-line test file, and the only committed footprint-and-latency figures in the atlas.
- Study when: you are about to build a consolidation queue and have not asked whether you need one.
- Do not copy when: you need to fix a mistake — OptMem can always tell you what was written and can never repair it.

### `memvid`

- Best idea: immutability as the correction mechanism — a supersession is a link, not an overwrite, so `get_at_time` and session replay come from the format rather than a bi-temporal schema.
- Biggest risk: the loudest quality claims in the atlas ("+35% SOTA on LoCoMo") with no committed raw artifacts found at this commit.
- Most reusable component: `entity:slot` cards with a declared cardinality, which turns contradiction detection into a lookup and tells you whether a second value is a conflict or an addition.
- Maturity impression: a serious file format with WAL, footer recovery, a 1,687-line doctor, and a deployment story of one binary and one file.
- Study when: you need to answer "what did the agent believe when it did that", which nothing else here can.
- Do not copy when: you need multi-tenant scope or epistemic status — the ACL is thin and there is no trust state.

### `memoryos`

- Best idea: the promotion rule is a written formula with named coefficients, and the LoCoMo harness ships with its dataset committed beside it.
- Biggest risk: heat sums frequency, interaction length and recency into one scalar with weights of 1/1/1, and a second LFU counter can disagree with it about the same segment.
- Most reusable component: the shape — tiers with an explicit, computable promotion signal — rather than the formula.
- Maturity impression: a legible research implementation with an MCP server, a vector variant and a playground around a 2,100-line core.
- Study when: you want the tiered architecture in a form small enough to read in an afternoon, or a base for experiments on promotion policy.
- Do not copy when: real users are involved — no provenance, no correction, no audit, and a merged profile string makes a deletion request unanswerable.

### `memu`

- Best idea: rank the slice, return the file — the embed/search unit and the context payload are different sizes, and a file scores as the max of its segments.
- Biggest risk: no epistemic model at all, and no scope key in a layer that serves seven different hosts from one store.
- Most reusable component: the three-method backend protocol, plus keyset pagination on immutable domain identity so a walk under concurrent writes neither skips nor repeats.
- Maturity impression: unusually disciplined for its size — schema comments cite the ADRs that produced them, and a denormalized column carries its safety argument.
- Study when: you want one memory across several coding agents and a read path that is cheap, predictable and model-free.
- Do not copy when: memory has to be trusted, corrected, or separated between users.

### `openworker`

- Best idea: an explicit when-to-remember policy, written because models without one fail bimodally — they either never save or save what the repository already records.
- Biggest risk: none of it is enforced or observable, so the first sign the model stopped following the policy is memory quality nobody can explain.
- Most reusable component: the guidance paragraph itself, especially "use absolute dates, never yesterday" and "don't save what the repo already records".
- Maturity impression: a large, carefully built agent with permissions, audit and unattended operation, and a memory subsystem of 260 lines that touches none of it.
- Study when: deciding whether to spend the next day on a pipeline or on the prompt that governs one.
- Do not copy when: you need ranking, a correction record, or any guarantee the policy was followed.

### `qwen-code`

- Best idea: a team tier committed to the repository, with secret-bearing writes to it refused unconditionally — the guard ignores the feature flag that governs the tier, because the directory is under version control either way.
- Biggest risk: three forget paths and no value-level tombstone, in a system whose extraction re-reads the sessions that produced the memory.
- Most reusable component: the extraction cursor with a processed offset, and recording `noop` as an outcome so "ran and changed nothing" is distinguishable from "did not run".
- Maturity impression: ~9,000 lines with a test beside nearly every module, and comments that read as scar tissue — per-operation kill signals for git, `execFile` with no shell.
- Study when: a team wants shared agent memory and does not want to stand up a service to get it.
- Do not copy when: corrections must survive a background pass.

### `opencode`

- Best idea: a compaction hook that lets a plugin append context as well as replace the prompt — the moment a memory system most needs, and one few hosts expose.
- Biggest risk: no memory contract at all, so plugins couple to the SQLite schema instead of the API, and a migration the host is entitled to make silently breaks them.
- Most reusable component: handing plugins the system prompt as `string[]` rather than a concatenated string, so two plugins compose instead of colliding.
- Maturity impression: a large, well-built coding agent with an extensive plugin surface, whose memory-relevant hooks are both marked experimental.
- Study when: you are building a host and deciding whether seams are enough without a domain contract.
- Do not copy when: you want the host to enforce scope or deletion — there is nothing here to enforce them with.

### `nooa-memory`

- Best idea: every access records the score components that produced it — `{rel, rec, imp, spread}`, the rank, the query and the reader — so "why was this retrieved" is a lookup rather than a reconstruction.
- Biggest risk: the access log is a capped ring on the record, so the formative accesses that explain how a memory became established are the first to be lost.
- Most reusable component: keeping rehearsal separate from belief — retrieval bumps a `strength` counter that slows forgetting and leaves `confidence` untouched.
- Maturity impression: 4,200 lines with 23 test modules, ACT-R and Ebbinghaus implemented literally rather than gesturally, inside an NVIDIA labs framework.
- Study when: you need memory whose ranking is explainable after the fact, or you want prospective memory — `intent` and `todo` are types nothing else here has.
- Do not copy when: you need correction — archival is a record flag, and a decayed memory can be re-authored with nothing to consult.

### `neo4j-agent-memory`

- Best idea: reasoning traces recorded via a context manager, so a raised exception becomes the outcome — failure memory proportional to coverage rather than to caller discipline, with an indexable error kind on top.
- Biggest risk: bi-temporality and supersession cover preferences only, and nothing is keyed on a rejected value.
- Most reusable component: the trace context manager plus `ReasoningStepWithContext`, which never returns a step without its parent's outcome.
- Maturity impression: a Neo4j Labs package with MCP, CLI, Strands and OpenAI Agents integrations, a benchmarks tree, and local NER extraction keeping the frequent write path off the token budget.
- Study when: several agents should share one view of the world, and operational history is the thing worth pooling.
- Do not copy when: corrections must survive re-extraction.

### `elastic-atlas`

- Best idea: a committed retrieval eval matched on document id rather than judged by a model, so Recall@k and MRR are arithmetic and reproducible — shipped beside a stress test.
- Biggest risk: a research demo by its own description, with synthetic personas and an ungated single-pass consolidation that writes both facts and playbooks.
- Most reusable component: the eval and stress-test scripts, which are more transferable than the memory layer.
- Maturity impression: a demo that measures itself more than most production systems in this atlas do.
- Study when: you want the clearest small example of the episodic/semantic/procedural split, or an eval design you can actually rerun.
- Do not copy when: you need correction, trust state, or an audit trail — none is present.

### `nemoclaw`

- Best idea: a per-agent state contract that says which directories are snapshotted, which are wiped, which are regenerated and which the user owns — written down rather than left to whoever wrote the backup script.
- Biggest risk: memory is snapshotted and restored verbatim, so a restore reinstates deleted memories and nothing above is told.
- Most reusable component: excluding state that is cheaper to regenerate than to restore, with the failure it prevents named — an argument that may apply to derived memory too.
- Maturity impression: infrastructure with guards that validate their own helpers, and issue numbers cited in the comments for the two decisions that would otherwise look arbitrary.
- Study when: you operate agents rather than build memory for them, and want to know what memory looks like from underneath.
- Do not copy when: you want a memory system — it has none, and its product page correctly credits memory to the agents it wraps.

### `daimon`

- Best idea: the model's trust label is a claim the code falsifies — a verbatim item's quote is grepped against the transcript and demoted on a miss, and an outcome claim with no tool result cited is demoted even when its quote verifies.
- Biggest risk: the live working set is one checkpoint per project, so anything carry drops is reachable only through a lexical index with no semantic arm, and the committed retrieval numbers are modest.
- Most reusable component: `verify_quotes` and `ground_outcomes` in `serializer.py` — about 200 lines that make an extraction's own provenance mechanically checkable.
- Maturity impression: 15,600 lines of source under 29,700 lines of tests, a research logbook, a scar file per landmine, and a benchmark reporting policy stricter than most vendors'.
- Study when: you want cross-session continuity for a coding agent, or you want to see what taking trust classes seriously actually costs in code.
- Do not copy when: you need memory within a session, semantic retrieval, or a shared service — none of the three is here or planned.

### `helm`

- Best idea: a first observation is capped at 0.7 confidence and can only rise 0.05 per independent repeat of the same value, so the store cannot record a single sighting as certain — the whole gate is about fifteen lines.
- Biggest risk: the confidence it computes never reaches the model. The per-turn block is `- (kind) key: value` under *"use these, never contradict them"*, which promotes every provisional guess to an assertion at the last step.
- Most reusable component: `workspace/memory/` — four scripts, a JSON-on-stdout CLI, no dependency beyond Node 22's built-in `node:sqlite`, and no coupling to the rest of Helm beyond a path.
- Maturity impression: uneven and legible. A committed 25-issue self-audit with `file:line` and reproduction steps, every issue I checked closed at this commit, and smoke tests that assert ranking and the system's own noise gates — beside a schema that exists as guarded `ALTER`s in five files and three readers that forgot the active-row predicate.
- Study when: you want the cheapest working epistemic model in this atlas, or you are building a single-owner local agent and want more than a JSON blob.
- Do not copy when: the store will pass a few hundred active facts (the recall window is 500 rows ordered by recency), more than one person or project shares it (there is no scope to add), or deletion has to survive re-derivation (`forget` and prune are hard deletes with no record).

## 10. Practical Checklist for Your Own System

Schema and scoping:

- Define the memory unit before choosing vector storage.
- Store raw evidence separately from derived memory.
- Give raw evidence stable IDs and source/span metadata.
- Make scope mandatory: user, agent, project/session, and sharing boundary.
- Include provenance/source IDs on every derived memory.
- Store provenance/evidence as append-only rows when a claim can have multiple origins.
- Represent status/trust explicitly.

Write path:

- Store evidence first.
- Record embedder identity and index version.
- Extract structured candidates.
- Dedupe by exact hash and semantic similarity.
- Detect same subject/predicate conflicts.
- Preserve correction chains.
- Keep rejected tombstones.
- Use stale-write guards for review UI mutations.

Retrieval:

- Use lexical plus vector retrieval.
- Filter by scope before ranking.
- Let summaries/entities/indexes boost raw evidence, not hide it.
- Rank with relevance, recency, confidence, trust, and retrieval strength.
- Enforce both result-count and token budgets; never let `k` silently become a lower bound.
- Evaluate retrieval on realistic tasks.

Context assembly:

- Budget tokens.
- Prefer verified memories.
- Mark uncertainty.
- Fence recalled memory as data.
- Include enough source metadata for debugging.

Trust/provenance:

- Do not let model extraction imply truth.
- Separate "often retrieved" from "known true".
- Require attestation or corroboration for important claims.
- Track who said what and when.
- Treat feedback/downvotes as review signals, not automatic truth updates.

Agent UX:

- Provide small MCP/SDK tools.
- Make `remember`, `recall`, `judge`, and `forget` distinct.
- Return conflicts for review instead of silently overwriting.
- Avoid broad semantic deletion without ID confirmation.
- Expose "which memories did you use?" as a first-class audit command.
- Require an explicit write target when private and shared scopes coexist.

Testing/evals:

- Golden extraction cases.
- Contradiction and supersession cases.
- Scope leakage cases.
- Prompt-injection recall cases.
- Delete/forget compliance cases.
- Long-running compaction/summarization regression cases.

Operations:

- Keep local state inspectable during early development.
- Use atomic transactional storage for primary state; reserve flat JSON for export or single-process prototypes.
- Add background workers only after synchronous semantics are clear.
- Log memory mutations as audit events.
- Version schemas.
- Provide repair/reindex paths for vector-store corruption or embedding-model swaps.
- Keep retrieval events append-only; derive counters from events.
- Preserve failed background-extraction inputs and provide a bounded retry/redistill path.
- Separate private auto-commit behavior from shared repository writes.

Privacy/deletion:

- Design deletion before shipping.
- Know whether delete means hide, tombstone, hard delete, or forget from embeddings.
- Propagate deletion to raw chunks, derived memories, summaries/indexes, graph facts, backups, sync, and remote backends.
- Test that cross-source graph edges cannot survive as dangling references after source deletion.

## 11. Appendix

### Individual Reports

- [`mem0`](../systems/mem0/)
- [`langmem`](../systems/langmem/)
- [`honcho`](../systems/honcho/)
- [`engram`](../systems/engram/)
- [`mempalace`](../systems/mempalace/)
- [`swafra`](../systems/swafra/)
- [`llm-wiki-memory`](../systems/llm-wiki-memory/)
- [`rainbox`](../systems/rainbox/)
- [`letta`](../systems/letta/)
- [`supermemory`](../systems/supermemory/)
- [`verel`](../systems/verel/)
- [`hindsight`](../systems/hindsight/)
- [`graphiti`](../systems/graphiti/)
- [`mastra-observational-memory`](../systems/mastra-observational-memory/)
- [`memos`](../systems/memos/)
- [`basic-memory`](../systems/basic-memory/)
- [`agentmemory`](../systems/agentmemory/)
- [`tencentdb-agent-memory`](../systems/tencentdb-agent-memory/)
- [`cognee`](../systems/cognee/)
- [`claude-mem`](../systems/claude-mem/)
- [`a-mem`](../systems/a-mem/)
- [`holographic`](../systems/holographic/)
- [`hermes-agent`](../systems/hermes-agent/)
- [`openviking`](../systems/openviking/)
- [`redis-agent-memory-server`](../systems/redis-agent-memory-server/)
- [`byterover`](../systems/byterover/)
- [`openclaw`](../systems/openclaw/)
- [`hipporag`](../systems/hipporag/)
- [`voyager`](../systems/voyager/)
- [`generative-agents`](../systems/generative-agents/)
- [`magic-context`](../systems/magic-context/)
- [`pi`](../systems/pi/)
- [`metaclaw`](../systems/metaclaw/)
- [`nanobot`](../systems/nanobot/)
- [`cowagent`](../systems/cowagent/)
- [`genericagent`](../systems/genericagent/)
- [`open-cowork`](../systems/open-cowork/)
- [`gini-agent`](../systems/gini-agent/)
- [`moltis`](../systems/moltis/)
- [`mercury-agent`](../systems/mercury-agent/)
- [`llamaindex`](../systems/llamaindex/)
- [`atomic-agent`](../systems/atomic-agent/)
- [`mateclaw`](../systems/mateclaw/)
- [`waku-agent`](../systems/waku-agent/)
- [`memora`](../systems/memora/)
- [`loongflow`](../systems/loongflow/)
- [`core-memory`](../systems/core-memory/)
- [`memanto`](../systems/memanto/)
- [`memory-engine`](../systems/memory-engine/)
- [`ai-memory`](../systems/ai-memory/)
- [`ctx`](../systems/ctx/)
- [`optmem`](../systems/optmem/)
- [`memvid`](../systems/memvid/)
- [`memoryos`](../systems/memoryos/)
- [`memu`](../systems/memu/)
- [`openworker`](../systems/openworker/)
- [`qwen-code`](../systems/qwen-code/)
- [`opencode`](../systems/opencode/)
- [`nooa-memory`](../systems/nooa-memory/)
- [`neo4j-agent-memory`](../systems/neo4j-agent-memory/)
- [`elastic-atlas`](../systems/elastic-atlas/)
- [`mirix`](../systems/mirix/)
- [`memobase`](../systems/memobase/)
- [`memary`](../systems/memary/)
- [`memori`](../systems/memori/)
- [`reme`](../systems/reme/)
- [`powermem`](../systems/powermem/)
- [`minecontext`](../systems/minecontext/)
- [`acontext`](../systems/acontext/)
- [`second-me`](../systems/second-me/)
- [`tigrimosr`](../systems/tigrimosr/)
- [`nemoclaw`](../systems/nemoclaw/)
- [`daimon`](../systems/daimon/)
- [`memmachine`](../systems/memmachine/)
- [`buzz`](../systems/buzz/)
- [`logseq`](../systems/logseq/)
- [`openhuman`](../systems/openhuman/)
- [`adk-python`](../systems/adk-python/)
- [`aukora-kernel`](../systems/aukora-kernel/)
- [`autogen`](../systems/autogen/)
- [`goodai-ltm`](../systems/goodai-ltm/)
- [`everos`](../systems/everos/)
- [`ecc`](../systems/ecc/)
- [`skales`](../systems/skales/)
- [`neko`](../systems/neko/)
- [`sillytavern`](../systems/sillytavern/)
- [`risuai`](../systems/risuai/)
- [`soul-of-waifu`](../systems/soul-of-waifu/)
- [`z-waif`](../systems/z-waif/)
- [`virtualwife`](../systems/virtualwife/)
- [`helm`](../systems/helm/)
- [`agno`](../systems/agno/)
- [`simplemem`](../systems/simplemem/)
- [`pydantic-ai-harness`](../systems/pydantic-ai-harness/)
- [`camel`](../systems/camel/)
- [`agent-framework`](../systems/agent-framework/)
- [`crewai`](../systems/crewai/)
- [`gobii`](../systems/gobii/)
- [`agent-memory-supabase`](../systems/agent-memory-supabase/)
- [`livingfeed`](../systems/livingfeed/)
- [`cosmonapse`](../systems/cosmonapse/)
- [`npcpy`](../systems/npcpy/)
- [`juggler`](../systems/juggler/)
- [`mem0sharp`](../systems/mem0sharp/)
- [`gitlord`](../systems/gitlord/)
- [`agent-afk`](../systems/agent-afk/)
- [`cortex`](../systems/cortex/)
- [`mnemopi`](../systems/mnemopi/)
- [`tokenmizer`](../systems/tokenmizer/)
- [`zerostack`](../systems/zerostack/)
- [`lethe`](../systems/lethe/)

### Repos Inspected

- [mem0ai/mem0](https://github.com/mem0ai/mem0) at [`31cec11a790868f88c9acafb8b70eb25071f2150`](https://github.com/mem0ai/mem0/commit/31cec11a790868f88c9acafb8b70eb25071f2150)
- [langchain-ai/langmem](https://github.com/langchain-ai/langmem) at [`c01e273b94aa4c06e41d0ed1ccce0db17de2bc11`](https://github.com/langchain-ai/langmem/commit/c01e273b94aa4c06e41d0ed1ccce0db17de2bc11)
- [plastic-labs/honcho](https://github.com/plastic-labs/honcho) at [`eb386c3ceb77774b29108f9ab114e71d52b7d420`](https://github.com/plastic-labs/honcho/commit/eb386c3ceb77774b29108f9ab114e71d52b7d420)
- [Gentleman-Programming/engram](https://github.com/Gentleman-Programming/engram) at [`44faeee1fb4fabdee4ba9619df55af485f3d06eb`](https://github.com/Gentleman-Programming/engram/commit/44faeee1fb4fabdee4ba9619df55af485f3d06eb)
- [MemPalace/mempalace](https://github.com/MemPalace/mempalace) at [`afd0428823b47f9a9d1d68c450d54bb0045a4988`](https://github.com/MemPalace/mempalace/commit/afd0428823b47f9a9d1d68c450d54bb0045a4988)
- [kunal12203/swafra](https://github.com/kunal12203/swafra) at [`24dba18a4194aef0cb0d6d6c68cf46e6fcbf2da7`](https://github.com/kunal12203/swafra/commit/24dba18a4194aef0cb0d6d6c68cf46e6fcbf2da7)
- [ctxr-dev/llm-wiki-memory](https://github.com/ctxr-dev/llm-wiki-memory) at [`b7cc76a493573baac133969b324a874990556146`](https://github.com/ctxr-dev/llm-wiki-memory/commit/b7cc76a493573baac133969b324a874990556146)
- [neoneye/RainBox](https://github.com/neoneye/RainBox) at [`9f565bf26175bc5e09288f70ec666a4616a2323c`](https://github.com/neoneye/RainBox/commit/9f565bf26175bc5e09288f70ec666a4616a2323c)
- [letta-ai/letta](https://github.com/letta-ai/letta) at [`6d8cb7fd48938b629aad5770faa051a8d42e1e9f`](https://github.com/letta-ai/letta/commit/6d8cb7fd48938b629aad5770faa051a8d42e1e9f)
- [supermemoryai/supermemory](https://github.com/supermemoryai/supermemory) at [`603d0512fd40e4575e2a075938c1851a898ceeb6`](https://github.com/supermemoryai/supermemory/commit/603d0512fd40e4575e2a075938c1851a898ceeb6)
- [amitpatole/verel](https://github.com/amitpatole/verel) at [`df80efe8207a99585a2ebce36fc6e32ba5077e2e`](https://github.com/amitpatole/verel/commit/df80efe8207a99585a2ebce36fc6e32ba5077e2e)
- [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight) at [`ed120a256d51d731085ec8aca724573a7f2f1e1c`](https://github.com/vectorize-io/hindsight/commit/ed120a256d51d731085ec8aca724573a7f2f1e1c)
- [getzep/graphiti](https://github.com/getzep/graphiti) at [`9140123a7282d44efc077a0af09179919f3defdf`](https://github.com/getzep/graphiti/commit/9140123a7282d44efc077a0af09179919f3defdf)
- [mastra-ai/mastra](https://github.com/mastra-ai/mastra) at [`40547102f655596178346ad2f883fbde735c3333`](https://github.com/mastra-ai/mastra/commit/40547102f655596178346ad2f883fbde735c3333)
- [MemTensor/MemOS](https://github.com/MemTensor/MemOS) at [`3fd109e7cbaba291af2253f107e0a595dbf62b00`](https://github.com/MemTensor/MemOS/commit/3fd109e7cbaba291af2253f107e0a595dbf62b00)
- [basicmachines-co/basic-memory](https://github.com/basicmachines-co/basic-memory) at [`232f2c2fc4e91564d88bcc312ed3d8bd1e8e051b`](https://github.com/basicmachines-co/basic-memory/commit/232f2c2fc4e91564d88bcc312ed3d8bd1e8e051b)
- [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) at [`d8b5267c367a5da07ad3619363520b7f1a506c6b`](https://github.com/rohitg00/agentmemory/commit/d8b5267c367a5da07ad3619363520b7f1a506c6b)
- [TencentCloud/tencentdb-agent-memory](https://github.com/TencentCloud/tencentdb-agent-memory) at [`45e6e80ae2e63b65fad0d89f5e13171229c8f295`](https://github.com/TencentCloud/tencentdb-agent-memory/commit/45e6e80ae2e63b65fad0d89f5e13171229c8f295)
- [topoteretes/cognee](https://github.com/topoteretes/cognee) at [`325acf356a81545b9892f19ab1ea7b61c51a776b`](https://github.com/topoteretes/cognee/commit/325acf356a81545b9892f19ab1ea7b61c51a776b)
- [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) at [`132b46343e60ecf4057c427736c57b08f7615dfe`](https://github.com/thedotmack/claude-mem/commit/132b46343e60ecf4057c427736c57b08f7615dfe)
- [agiresearch/A-mem](https://github.com/agiresearch/A-mem) at [`ceffb860f0712bbae97b184d440df62bc910ca8d`](https://github.com/agiresearch/A-mem/commit/ceffb860f0712bbae97b184d440df62bc910ca8d)
- [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) at [`0fa5e41c86f022bba147797849f0b44865721476`](https://github.com/NousResearch/hermes-agent/commit/0fa5e41c86f022bba147797849f0b44865721476) — analyzed twice, as the `holographic` plugin and as Hermes's own built-in memory
- [volcengine/OpenViking](https://github.com/volcengine/OpenViking) at [`c67222c3d46de4874eed65af8918fc55513812ef`](https://github.com/volcengine/OpenViking/commit/c67222c3d46de4874eed65af8918fc55513812ef)
- [redis/agent-memory-server](https://github.com/redis/agent-memory-server) at [`886437963dc02289e828872f0ae21fdaa734c337`](https://github.com/redis/agent-memory-server/commit/886437963dc02289e828872f0ae21fdaa734c337)
- [campfirein/cipher](https://github.com/campfirein/cipher) at [`1052ac1a5dd0fde4da8693d4712064f7876c269c`](https://github.com/campfirein/cipher/commit/1052ac1a5dd0fde4da8693d4712064f7876c269c)
- [openclaw/openclaw](https://github.com/openclaw/openclaw) at [`570eab59e7c7ce052f4550af7507e7dd77c73e11`](https://github.com/openclaw/openclaw/commit/570eab59e7c7ce052f4550af7507e7dd77c73e11)
- [OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG) at [`e37fba2af1a951ac340d837a7c02efb9d8c9544a`](https://github.com/OSU-NLP-Group/HippoRAG/commit/e37fba2af1a951ac340d837a7c02efb9d8c9544a)
- [MineDojo/Voyager](https://github.com/MineDojo/Voyager) at [`55e45a880755d0c8c66ca7fb5fe7962ac8974f89`](https://github.com/MineDojo/Voyager/commit/55e45a880755d0c8c66ca7fb5fe7962ac8974f89)
- [joonspk-research/generative_agents](https://github.com/joonspk-research/generative_agents) at [`fe05a71d3e4ed7d10bf68aa4eda6dd995ec070f4`](https://github.com/joonspk-research/generative_agents/commit/fe05a71d3e4ed7d10bf68aa4eda6dd995ec070f4)
- [cortexkit/magic-context](https://github.com/cortexkit/magic-context) at [`113f3e4824e0ea03a73f2c1e8a57a5ab0bbf7a09`](https://github.com/cortexkit/magic-context/commit/113f3e4824e0ea03a73f2c1e8a57a5ab0bbf7a09)
- [earendil-works/pi](https://github.com/earendil-works/pi) at [`a597371bda2af70372d1323d550483b5f4a0ae36`](https://github.com/earendil-works/pi/commit/a597371bda2af70372d1323d550483b5f4a0ae36)
- [aiming-lab/MetaClaw](https://github.com/aiming-lab/MetaClaw) at [`922caf3a1cd093fb316e95183a8acc8aa47b3b21`](https://github.com/aiming-lab/MetaClaw/commit/922caf3a1cd093fb316e95183a8acc8aa47b3b21)
- [HKUDS/nanobot](https://github.com/HKUDS/nanobot) at [`b99e0f937e828504e0f93dbe35dfd6b1540e20b2`](https://github.com/HKUDS/nanobot/commit/b99e0f937e828504e0f93dbe35dfd6b1540e20b2)
- [zhayujie/CowAgent](https://github.com/zhayujie/CowAgent) at [`fe88751ccb24e9b2991b6a35a2dcc538f7a38761`](https://github.com/zhayujie/CowAgent/commit/fe88751ccb24e9b2991b6a35a2dcc538f7a38761)
- [lsdefine/GenericAgent](https://github.com/lsdefine/GenericAgent) at [`7ffc95823b6e40ca4e10acf9fb285d923485cacc`](https://github.com/lsdefine/GenericAgent/commit/7ffc95823b6e40ca4e10acf9fb285d923485cacc)
- [OpenCoworkAI/open-cowork](https://github.com/OpenCoworkAI/open-cowork) at [`6f0c04741386b8600aa977f14ac0679d2203bd1b`](https://github.com/OpenCoworkAI/open-cowork/commit/6f0c04741386b8600aa977f14ac0679d2203bd1b)
- [Open-Curiosity/gini-agent](https://github.com/Open-Curiosity/gini-agent) at [`6c5d85ed0ecd7fe8567124bd4890b16c329970d8`](https://github.com/Open-Curiosity/gini-agent/commit/6c5d85ed0ecd7fe8567124bd4890b16c329970d8)
- [moltis-org/moltis](https://github.com/moltis-org/moltis) at [`1f53cd27b1a21c36b61ceda7a8ea65a35deb7872`](https://github.com/moltis-org/moltis/commit/1f53cd27b1a21c36b61ceda7a8ea65a35deb7872)
- [cosmicstack-labs/mercury-agent](https://github.com/cosmicstack-labs/mercury-agent) at [`6e174a4b5ea77bbc753bff5f89c76db9303439d1`](https://github.com/cosmicstack-labs/mercury-agent/commit/6e174a4b5ea77bbc753bff5f89c76db9303439d1)
- [run-llama/llama_index](https://github.com/run-llama/llama_index) at [`199e9b5b130bbde72639358a08935b913e7132c0`](https://github.com/run-llama/llama_index/commit/199e9b5b130bbde72639358a08935b913e7132c0)
- [AtomicBot-ai/atomic-agent](https://github.com/AtomicBot-ai/atomic-agent) at [`d69332c589733e38ae7393dd81fcbc5a375d02fb`](https://github.com/AtomicBot-ai/atomic-agent/commit/d69332c589733e38ae7393dd81fcbc5a375d02fb)
- [mateaix/mateclaw](https://github.com/mateaix/mateclaw) at [`3643aed7564390f57906954286a443d5913b97a7`](https://github.com/mateaix/mateclaw/commit/3643aed7564390f57906954286a443d5913b97a7)
- [ShenSeanChen/waku-agent](https://github.com/ShenSeanChen/waku-agent) at [`5f638cfb5de957c14f056027833d8a9df5bbe558`](https://github.com/ShenSeanChen/waku-agent/commit/5f638cfb5de957c14f056027833d8a9df5bbe558)
- [agentic-box/memora](https://github.com/agentic-box/memora) at [`bc64ff745a9b2c0e6245e0137654f041fba0c155`](https://github.com/agentic-box/memora/commit/bc64ff745a9b2c0e6245e0137654f041fba0c155)
- [baidu-baige/LoongFlow](https://github.com/baidu-baige/LoongFlow) at [`945c78bc1554f8281aac40320b3599bd68d528d7`](https://github.com/baidu-baige/LoongFlow/commit/945c78bc1554f8281aac40320b3599bd68d528d7)
- [JohnnyFiv3r/Core-Memory](https://github.com/JohnnyFiv3r/Core-Memory) at [`dfe306cda3505389904435132599153596417de2`](https://github.com/JohnnyFiv3r/Core-Memory/commit/dfe306cda3505389904435132599153596417de2)
- [moorcheh-ai/memanto](https://github.com/moorcheh-ai/memanto) at [`d1902419321352f0108c499bd8ed4ebd129fe138`](https://github.com/moorcheh-ai/memanto/commit/d1902419321352f0108c499bd8ed4ebd129fe138)
- [timescale/memory-engine](https://github.com/timescale/memory-engine) at [`54e4d7d201b5c7ba3aed618ea343d9f4d3f40927`](https://github.com/timescale/memory-engine/commit/54e4d7d201b5c7ba3aed618ea343d9f4d3f40927)
- [akitaonrails/ai-memory](https://github.com/akitaonrails/ai-memory) at [`5d3c08344cf40d23cbf06c47f6b6300bdb96d1e3`](https://github.com/akitaonrails/ai-memory/commit/5d3c08344cf40d23cbf06c47f6b6300bdb96d1e3)
- [ActiveMemory/ctx](https://github.com/ActiveMemory/ctx) at [`ce5a832885d66ba3608e02d2db85e5e90a455559`](https://github.com/ActiveMemory/ctx/commit/ce5a832885d66ba3608e02d2db85e5e90a455559)
- [VictorTaelin/OptMem](https://github.com/VictorTaelin/OptMem) at [`e36da55815951d50d103d7242d92cf9a71ceee96`](https://github.com/VictorTaelin/OptMem/commit/e36da55815951d50d103d7242d92cf9a71ceee96) — **no licence file**
- [memvid/memvid](https://github.com/memvid/memvid) at [`e6bd9f7b9c38cd8d5370fa0fc936ac1dcd751813`](https://github.com/memvid/memvid/commit/e6bd9f7b9c38cd8d5370fa0fc936ac1dcd751813)
- [BAI-LAB/MemoryOS](https://github.com/BAI-LAB/MemoryOS) at [`587ed7755c7aed179965792830ff1b5ad9a6fa92`](https://github.com/BAI-LAB/MemoryOS/commit/587ed7755c7aed179965792830ff1b5ad9a6fa92)
- [NevaMind-AI/memU](https://github.com/NevaMind-AI/memU) at [`3a5a05ea7fa4e3eafe609c189f2f2ff046c5e87e`](https://github.com/NevaMind-AI/memU/commit/3a5a05ea7fa4e3eafe609c189f2f2ff046c5e87e)
- [andrewyng/openworker](https://github.com/andrewyng/openworker) at [`d3863966c9de39140e7a28cffdc71ae96614774b`](https://github.com/andrewyng/openworker/commit/d3863966c9de39140e7a28cffdc71ae96614774b)
- [QwenLM/qwen-code](https://github.com/QwenLM/qwen-code) at [`6a432ad2ebce57b0b48cd3d6a8f4f7fab50c33fe`](https://github.com/QwenLM/qwen-code/commit/6a432ad2ebce57b0b48cd3d6a8f4f7fab50c33fe)
- [anomalyco/opencode](https://github.com/anomalyco/opencode) at [`3cc70160deb0eda7f67fbf5b0c0780000f5c342d`](https://github.com/anomalyco/opencode/commit/3cc70160deb0eda7f67fbf5b0c0780000f5c342d)
- [NVIDIA-NeMo/labs-OO-Agents](https://github.com/NVIDIA-NeMo/labs-OO-Agents) at [`f22805b52ea8a073dabc018cefe3db1ccf609a29`](https://github.com/NVIDIA-NeMo/labs-OO-Agents/commit/f22805b52ea8a073dabc018cefe3db1ccf609a29)
- [neo4j-labs/agent-memory](https://github.com/neo4j-labs/agent-memory) at [`b017db4449d592a982944986c2e3c18652bb36ad`](https://github.com/neo4j-labs/agent-memory/commit/b017db4449d592a982944986c2e3c18652bb36ad)
- [noamschwartz/atlas-memory-demo](https://github.com/noamschwartz/atlas-memory-demo) at [`0bd36a7b177a09aad97dc78efeb5fb43b9322f6d`](https://github.com/noamschwartz/atlas-memory-demo/commit/0bd36a7b177a09aad97dc78efeb5fb43b9322f6d)
- [NVIDIA/NemoClaw](https://github.com/NVIDIA/NemoClaw) at [`02b59e5dc1c995cd47574af5eafb23395959ea03`](https://github.com/NVIDIA/NemoClaw/commit/02b59e5dc1c995cd47574af5eafb23395959ea03)
- [Daily-Nerd/daimon](https://github.com/Daily-Nerd/daimon) at [`ecb7fafefa817f0726f46b221ddd4c7f4400a30a`](https://github.com/Daily-Nerd/daimon/commit/ecb7fafefa817f0726f46b221ddd4c7f4400a30a)
- [Mirix-AI/MIRIX](https://github.com/Mirix-AI/MIRIX) at [`51f3342d5366b0e215439581f92e0323227146af`](https://github.com/Mirix-AI/MIRIX/commit/51f3342d5366b0e215439581f92e0323227146af)
- [memodb-io/memobase](https://github.com/memodb-io/memobase) at [`358c16bbc6d687937d79bc2f984a11c3be8da901`](https://github.com/memodb-io/memobase/commit/358c16bbc6d687937d79bc2f984a11c3be8da901)
- [kingjulio8238/Memary](https://github.com/kingjulio8238/Memary) at [`b2331a2c0844d66f69acd607b9e4dbaba56552c1`](https://github.com/kingjulio8238/Memary/commit/b2331a2c0844d66f69acd607b9e4dbaba56552c1)
- [MemoriLabs/Memori](https://github.com/MemoriLabs/Memori) at [`538b61f245295aa1a43df8033879f8293627f74d`](https://github.com/MemoriLabs/Memori/commit/538b61f245295aa1a43df8033879f8293627f74d)
- [agentscope-ai/ReMe](https://github.com/agentscope-ai/ReMe) at [`550317c3bfb755d985a0401194827eaa9676a5bc`](https://github.com/agentscope-ai/ReMe/commit/550317c3bfb755d985a0401194827eaa9676a5bc)
- [oceanbase/powermem](https://github.com/oceanbase/powermem) at [`9d1b48449345b1ec7af1144aa1b81bb776478851`](https://github.com/oceanbase/powermem/commit/9d1b48449345b1ec7af1144aa1b81bb776478851)
- [volcengine/MineContext](https://github.com/volcengine/MineContext) at [`171c7a9ea8091e326ddcf0f10718aa1b58c83c65`](https://github.com/volcengine/MineContext/commit/171c7a9ea8091e326ddcf0f10718aa1b58c83c65)
- [memodb-io/Acontext](https://github.com/memodb-io/Acontext) at [`259d73bfdebeed35ec2d4211ddc060a2d4126bc6`](https://github.com/memodb-io/Acontext/commit/259d73bfdebeed35ec2d4211ddc060a2d4126bc6)
- [mindverse/Second-Me](https://github.com/mindverse/Second-Me) at [`d0e40251d9de61b3340b8d0d7d83150669f1885a`](https://github.com/mindverse/Second-Me/commit/d0e40251d9de61b3340b8d0d7d83150669f1885a)
- [Sompote/TigrimOSR](https://github.com/Sompote/TigrimOSR) at [`92e8867b63acfb8592d6ae3067ba3192ac49370d`](https://github.com/Sompote/TigrimOSR/commit/92e8867b63acfb8592d6ae3067ba3192ac49370d)
- [MemMachine/MemMachine](https://github.com/MemMachine/MemMachine) at [`a681abf9623299bba8ad931e5d9af02fb6ef0997`](https://github.com/MemMachine/MemMachine/commit/a681abf9623299bba8ad931e5d9af02fb6ef0997)
- [block/buzz](https://github.com/block/buzz) at [`24d90d1280a9325c6cbcf8eea30ac54db5afd2cb`](https://github.com/block/buzz/commit/24d90d1280a9325c6cbcf8eea30ac54db5afd2cb)
- [logseq/logseq](https://github.com/logseq/logseq) at [`9a11243d50b23afeb10bda5a2ca6cc77357eea38`](https://github.com/logseq/logseq/commit/9a11243d50b23afeb10bda5a2ca6cc77357eea38)
- [tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman) at [`e213bc5fc4000e9ad599c977a560113cc018c554`](https://github.com/tinyhumansai/openhuman/commit/e213bc5fc4000e9ad599c977a560113cc018c554)
- [google/adk-python](https://github.com/google/adk-python) at [`6bab08fc803d26853417c4d6e71704b1a72e035e`](https://github.com/google/adk-python/commit/6bab08fc803d26853417c4d6e71704b1a72e035e)
- [aumara-xyz/aukora-kernel](https://github.com/aumara-xyz/aukora-kernel) at [`b441edc4d17de778d30ae955f46408edae39bffe`](https://github.com/aumara-xyz/aukora-kernel/commit/b441edc4d17de778d30ae955f46408edae39bffe)
- [microsoft/autogen](https://github.com/microsoft/autogen) at [`027ecf0a379bcc1d09956d46d12d44a3ad9cee14`](https://github.com/microsoft/autogen/commit/027ecf0a379bcc1d09956d46d12d44a3ad9cee14)
- [GoodAI/goodai-ltm](https://github.com/GoodAI/goodai-ltm) at [`22ca10c21771d0192d550517cb06c3aab6e602aa`](https://github.com/GoodAI/goodai-ltm/commit/22ca10c21771d0192d550517cb06c3aab6e602aa)
- [GoodAI/goodai-ltm-benchmark](https://github.com/GoodAI/goodai-ltm-benchmark) at [`188e7618413775f1ce783763d5ee0b5ccd4c31c9`](https://github.com/GoodAI/goodai-ltm-benchmark/commit/188e7618413775f1ce783763d5ee0b5ccd4c31c9) — the companion benchmark, described on the benchmarks page
- [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) at [`4256419595f63fe307147dc19e379477cecdc44f`](https://github.com/EverMind-AI/EverOS/commit/4256419595f63fe307147dc19e379477cecdc44f)
- [affaan-m/ECC](https://github.com/affaan-m/ECC) at [`591ab5cbd3f2f65860ea91c226e410b1502c8e2e`](https://github.com/affaan-m/ECC/commit/591ab5cbd3f2f65860ea91c226e410b1502c8e2e)
- [skalesapp/skales](https://github.com/skalesapp/skales) at [`128103e732465a00a2d2ab4bf7d322e32c17ad4d`](https://github.com/skalesapp/skales/commit/128103e732465a00a2d2ab4bf7d322e32c17ad4d) — BSL 1.1, source-available
- [Project-N-E-K-O/N.E.K.O](https://github.com/Project-N-E-K-O/N.E.K.O) at [`6a3d4beb7425261d01eb08034139d87bec03b8b5`](https://github.com/Project-N-E-K-O/N.E.K.O/commit/6a3d4beb7425261d01eb08034139d87bec03b8b5)
- [netease-youdao/LobsterAI](https://github.com/netease-youdao/LobsterAI) at [`2921c1e5bddbd96a503da4acd7538cac45bcd0f2`](https://github.com/netease-youdao/LobsterAI/commit/2921c1e5bddbd96a503da4acd7538cac45bcd0f2) — not a report; cited in the OpenClaw analysis
- [SillyTavern/SillyTavern](https://github.com/SillyTavern/SillyTavern) at [`8172dcd0ee672d3cd9a5e5f7af134f91a45cd2b8`](https://github.com/SillyTavern/SillyTavern/commit/8172dcd0ee672d3cd9a5e5f7af134f91a45cd2b8)
- [kwaroran/RisuAI](https://github.com/kwaroran/RisuAI) at [`316e430bedbe68c80060ce74c5a1fff88f3bdf97`](https://github.com/kwaroran/RisuAI/commit/316e430bedbe68c80060ce74c5a1fff88f3bdf97)
- [jofizcd/Soul-of-Waifu](https://github.com/jofizcd/Soul-of-Waifu) at [`3d032badc07335012ae6917e29ea16b8203252f5`](https://github.com/jofizcd/Soul-of-Waifu/commit/3d032badc07335012ae6917e29ea16b8203252f5)
- [SugarcaneDefender/z-waif](https://github.com/SugarcaneDefender/z-waif) at [`aaf905c12efcbd2a709a3b2285f55e554d47484f`](https://github.com/SugarcaneDefender/z-waif/commit/aaf905c12efcbd2a709a3b2285f55e554d47484f)
- [yakami129/VirtualWife](https://github.com/yakami129/VirtualWife) at [`c8afd6d3ce6bb6f58988c649c50299d36b63e08f`](https://github.com/yakami129/VirtualWife/commit/c8afd6d3ce6bb6f58988c649c50299d36b63e08f)
- [GOODMAN-PRO/helm](https://github.com/GOODMAN-PRO/helm) at [`f453eaa9683ea0a66b45c76275cb6576bcf14f73`](https://github.com/GOODMAN-PRO/helm/commit/f453eaa9683ea0a66b45c76275cb6576bcf14f73)
- [agno-agi/agno](https://github.com/agno-agi/agno) at [`7c68873c1357321a5152397c8ab4fb8b3f587bba`](https://github.com/agno-agi/agno/commit/7c68873c1357321a5152397c8ab4fb8b3f587bba)
- [aiming-lab/SimpleMem](https://github.com/aiming-lab/SimpleMem) at [`db80b6a7c591e0ea730a058e9f5fc4eb06572299`](https://github.com/aiming-lab/SimpleMem/commit/db80b6a7c591e0ea730a058e9f5fc4eb06572299)
- [pydantic/pydantic-ai-harness](https://github.com/pydantic/pydantic-ai-harness) at [`39ee7e08101c54b1ddf9c1e3a7f603f09ae34555`](https://github.com/pydantic/pydantic-ai-harness/commit/39ee7e08101c54b1ddf9c1e3a7f603f09ae34555)
- [camel-ai/camel](https://github.com/camel-ai/camel) at [`ec48f997f3c2a700ae5a4cf0280792838fea81f8`](https://github.com/camel-ai/camel/commit/ec48f997f3c2a700ae5a4cf0280792838fea81f8)
- [microsoft/agent-framework](https://github.com/microsoft/agent-framework) at [`28389df805b97f846ca21d857e291602a7adc0a4`](https://github.com/microsoft/agent-framework/commit/28389df805b97f846ca21d857e291602a7adc0a4)
- [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) at [`ceed4a3ff71b5b4cb0ca316b4178ffcce74a53b2`](https://github.com/crewAIInc/crewAI/commit/ceed4a3ff71b5b4cb0ca316b4178ffcce74a53b2)
- [gobii-ai/gobii-platform](https://github.com/gobii-ai/gobii-platform) at [`26844673ac9f134e2ad3851a12dd26762d94c3a9`](https://github.com/gobii-ai/gobii-platform/commit/26844673ac9f134e2ad3851a12dd26762d94c3a9)
- [reescalder/agent-memory-supabase](https://github.com/reescalder/agent-memory-supabase) at [`b711e6d76009d0713c5d5c211c2ab5c83d01ca53`](https://github.com/reescalder/agent-memory-supabase/commit/b711e6d76009d0713c5d5c211c2ab5c83d01ca53)
- [showjihyun/livingfeed](https://github.com/showjihyun/livingfeed) at [`9bdd464d570a493ba9125636f4cf01b6cff78bae`](https://github.com/showjihyun/livingfeed/commit/9bdd464d570a493ba9125636f4cf01b6cff78bae)
- [Cosmonapse/cosmonapse-core](https://github.com/Cosmonapse/cosmonapse-core) at [`16997d577596750e139f3eb83fd5c4b1c3c740bf`](https://github.com/Cosmonapse/cosmonapse-core/commit/16997d577596750e139f3eb83fd5c4b1c3c740bf)
- [npc-worldwide/npcpy](https://github.com/npc-worldwide/npcpy) at [`a31ba52203062f7a586a901f6870176bf3961707`](https://github.com/npc-worldwide/npcpy/commit/a31ba52203062f7a586a901f6870176bf3961707)
- [juggler-ai/juggler](https://github.com/juggler-ai/juggler) at [`bf81e61087a6e6af24e5ffd225d66c74135a4faa`](https://github.com/juggler-ai/juggler/commit/bf81e61087a6e6af24e5ffd225d66c74135a4faa)
- [jihadkhawaja/mem0sharp](https://github.com/jihadkhawaja/mem0sharp) at [`ebf832c17f65815dfbfa65bcf376d4dc6683f057`](https://github.com/jihadkhawaja/mem0sharp/commit/ebf832c17f65815dfbfa65bcf376d4dc6683f057)
- [yashneil75/gitlord](https://github.com/yashneil75/gitlord) at [`42b0bab151777c1ee38ced7ab2805b0699e7a8a1`](https://github.com/yashneil75/gitlord/commit/42b0bab151777c1ee38ced7ab2805b0699e7a8a1)
- [griffinwork40/agent-afk](https://github.com/griffinwork40/agent-afk) at [`e3d15fe2389602c2761954baadd495d8ebe7a6a2`](https://github.com/griffinwork40/agent-afk/commit/e3d15fe2389602c2761954baadd495d8ebe7a6a2)
- [CortexPrism/cortex](https://github.com/CortexPrism/cortex) at [`0c446572ddaad588164af939f2e093441b06921f`](https://github.com/CortexPrism/cortex/commit/0c446572ddaad588164af939f2e093441b06921f)
- [can1357/oh-my-pi](https://github.com/can1357/oh-my-pi) at [`4df68d60438423b384b2b47fb3d6835641624757`](https://github.com/can1357/oh-my-pi/commit/4df68d60438423b384b2b47fb3d6835641624757)
- [Shweta-Mishra-ai/tokenmizer](https://github.com/Shweta-Mishra-ai/tokenmizer) at [`ed7860e626ccc5c67fdf28c5cd12532ba337aeee`](https://github.com/Shweta-Mishra-ai/tokenmizer/commit/ed7860e626ccc5c67fdf28c5cd12532ba337aeee)
- [gi-dellav/zerostack](https://github.com/gi-dellav/zerostack) at [`90986c5c55631e0a372694e77fa69880ba39b31b`](https://github.com/gi-dellav/zerostack/commit/90986c5c55631e0a372694e77fa69880ba39b31b)
- [deeplethe/lethe](https://github.com/deeplethe/lethe) at [`b6053b7bdacc78a91b9ea4bb25f32edad278c495`](https://github.com/deeplethe/lethe/commit/b6053b7bdacc78a91b9ea4bb25f32edad278c495)

### Commands Used

Representative local inspection commands:

- `find . -maxdepth ... -type d`
- `rg --files`
- `rg -n "memory|recall|remember|search|embedding|vector|MCP|Block|Passage|Representation|drawer|palace|wing|room|claim|evidence|retrieval_event"`
- `sed -n ...`
- `wc -l`
- `cmp`
- `jq`
- `git show -s --format=fuller HEAD`

No internet sources were used for this report. The analysis is based on the checked-out code in this workspace.

### Known Limitations

- Supermemory's hosted backend implementation was not visible in this checkout; its report emphasizes schemas, clients, SDKs, MCP, and graph UI.
- Some mem0 advanced capabilities appear to be managed-platform-only in the inspected OSS code.
- This is an implementation-oriented static review, not a runtime benchmark.
- **The licence check has not been applied uniformly.** The atlas declines
  repositories that ship no licence file — `general-agentic-memory` and
  `MemEngine` are both named above partly on that basis — but the check was
  performed at review time rather than as a build invariant, and at least one
  report was published against a commit that carried no licence. Swafra's
  original pin, `24dba18a`, had none; MIT landed later and the current pin
  carries it, so the entry is sound today, but the omission was the review's and
  the same gap may be waiting in other early reports. Nothing in
  `scripts/test_site.sh` enforces it.
- **Memory held in model weights is covered by exactly one system.**
  [Second Me](../systems/second-me/) is the atlas's only parametric-memory entry,
  and one system is a data point rather than coverage. Model editing, KV-cache
  reuse and weight-space personalization are a substantial branch of the
  literature and are essentially unrepresented here — which also means the seven
  rubric capabilities have only been exercised against token stores. Whether a
  tombstone, a scope key or an audit trail even has a referent in a fine-tuned
  model is an open question this corpus cannot answer.
- Four dimensions that matter operationally are not covered systematically here,
  and a reader choosing a system should investigate them directly. **Behaviour
  under embedding-model change or vector-store migration**: only a few systems
  visibly stamp records with the model that produced them, and a silent
  re-embedding is a silent corpus-wide quality change. **Whether scope survives
  background derivation**: the capability index records that a scope key is
  applied on the read path, not that consolidation, summarization, and profile
  building respect the same boundary — a summary spanning two projects has
  crossed a scope the retriever would have enforced. **Recall observability**
  beyond which memories were returned: why they outranked others, and what was
  dropped by budget truncation. **Cost and latency under realistic load**, which
  is treated separately in [benchmarking agent memory](../benchmarks/) — as an
  absence, because it is almost never measured.
- The capability flags in the index are the reviewer's judgements against
  strict definitions, applied to code read at the pinned commits. A flag's
  absence means the mechanism was not found, not that it is impossible to build
  on that system.
- Retrieval quality and extraction quality were not independently re-measured; committed benchmark artifacts were inspected for MemPalace but not rerun.
- Swafra was reviewed at commit `24dba18`; its full LongMemEval run was not rerun. Static inspection, committed artifact analysis, and a small hash-embedder smoke check exposed the `k` mismatch and same-title source behavior.
- `llm-wiki-memory` was reviewed at commit `b7cc76a493573baac133969b324a874990556146`; its broad test tree and committed latency report were inspected, but the suites and benchmarks were not rerun.
- RainBox was reviewed as an application-integrated memory subsystem; unrelated assistant/product features were not exhaustively analyzed.
- The reports prioritize memory-management code paths over unrelated framework/application code.
- Hindsight, Graphiti, Mastra, MemOS, and Basic Memory were reviewed statically at the pinned revisions above; their dependency-heavy integration suites and published benchmarks were not rerun.
- Mastra analysis is intentionally limited to `packages/memory` and the core contracts it directly uses.
- MemOS behavior varies materially by memory cube, backend, model, and search configuration; the report does not imply one universal MemOS pipeline.
- agentmemory's source tests and benchmarks were inspected but not rerun; its documented LongMemEval-S numbers are retrieval-only.
- TencentDB Agent Memory's published benchmark gains could not be traced to a committed harness or raw result artifacts in the inspected repository.
- Cognee's dependency-heavy suites and BEAM evaluation were not rerun. The committed 100K report uses a held-out conversation; its 10M routed result is explicitly exploratory and selected on the reported questions.
- Claude-Mem's Bun suite and optional service integrations were not run; no committed end-to-end recall-quality benchmark was found.
- A-MEM's tests were not run because they may download embedding models and call an external LLM. The paper reproduction code and results are outside the inspected package.
- `holographic` and `hermes-agent` are two reports over one repository at one commit: the first covers the in-tree HRR memory plugin, the second covers Hermes's own built-in memory and provider contract. Neither report's suites were run.
- Two open Hermes issues (#4781, #31263) report that the holographic plugin registers without its tools or context injection firing. Only the issue titles were read; they are not treated here as established defects in the inspected code.
- OpenViking's published LoCoMo and tau2-bench figures could not be reproduced or traced to committed raw artifacts at the inspected commit; the harness is committed, the results are not. Those figures are also vendor-run comparisons judged by an LLM, and the native-memory baselines for OpenClaw, Hermes, and Claude Code were not independently verified.
- The `openclaw` figures quoted from OpenViking's benchmark are third-party claims about OpenClaw's native memory, not measurements taken from the OpenClaw repository.
- ByteRover was reviewed at a commit where the repository is licensed under the Elastic License 2.0 and packaged as `byterover-cli`; descriptions of it as open source are inaccurate as of this commit. No tests were found for its memory or knowledge modules.
- Redis Agent Memory Server's `V0/` tree is the open reference implementation adjacent to a managed Redis offering; conclusions here apply only to the inspected code, and the managed product may differ.
- Retrieval quality was not measured for any of the six systems added in this round.
- Voyager and Generative Agents are frozen research artifacts, last committed in July and August 2023 respectively. Their reports are historical architectural reviews, not assessments of maintained software.
- HippoRAG's `reproduce/` tree provides benchmark scaffolding, but no raw result artifacts are committed and no published numbers were reproduced here.
- Voyager's and Generative Agents' published evaluations measure task completion and human believability, not retrieval quality; neither repository contains a memory-quality benchmark.
- Generative Agents' retrieval gain weights (`gw = [0.5, 3, 2]`) have no committed ablation; the atlas treats them as hand-tuned constants rather than a derived result.
- No suites were run for the three systems added in this round, and no retrieval quality was independently measured.
- Magic Context's verification precision — how often the verify task correctly marks a stale memory stale, and how often it wrongly confirms one — is not measured anywhere in that repository, and was not measured here. It is the central claim of the design.
- Magic Context reads OpenCode's native session database read-only for its retrospective scanner; that behaviour was read in code but not exercised, and the user-consent story around it was not assessed.
- Pi has no memory subsystem, so its report covers session persistence, compaction, and the extension surface only. Third-party Pi memory plugins other than Magic Context were not reviewed; the db0 integration has a closed backend and is not reviewable on this atlas's terms.
- MetaClaw's committed benchmark fixtures and memory ablation scripts were inspected but not run, and no published numbers were reproduced. Its replay metrics are lexical-overlap proxies; no evidence linking them to task outcomes was found in the repository.
- No memory tests or memory-quality benchmarks were located for nanobot, CowAgent, or GenericAgent. Nothing was run for any of the four systems added in this round.
- GenericAgent's memory documentation is written in Chinese; the axioms and rules quoted in its report are the reviewer's translations, with key terms given in the original. Its cited arXiv technical report was not retrieved or assessed.
- Waku Agent's evals were not run, and its retrieval gate's accuracy was not measured — the false-negative rate, which is the figure that matters, is unknown. No system in the atlas measures its gate.
- Nine repositories examined in the same round have no reports. `razzant/ouroboros` is cited in the append-only-memory-audit pattern for its "honest journal" fix rather than given a report. `truffle-ai/dexto` (Elastic License 2.0), `Arvincreator/project-golem` (a custom source-available licence), and `openyak/openyak` (**no licence file at all**, so all rights reserved by default) each carry a competent but conventional memory subsystem and no mechanism the atlas lacks, so none earns a licence exception. `OtterMind/youclaw` is small. `SixHq/Overture`'s only memory artifacts are `.claude/agent-memory/*/MEMORY.md` — Claude Code's own memory used while developing the repo, not a system it ships. `husu/loom` is an AI JSON Schema documentation generator, `AaronWong1999/hermesclaw` a launcher for running Hermes Agent, OpenClaw, and OpenCode on one WeChat account, and `KeyID-AI/agent-kit` gives MCP clients an email address; none is agent memory.
- Neither Atomic Agent's nor MateClaw's suites were run, and Atomic Agent's evaluation campaign was read but not executed; no scored results were found committed for it. MateClaw's scoping and retrieval ranking were not traced in full.
- Eight repositories examined in the same round have no reports. `beita6969/ScienceClaw` is an OpenClaw derivative whose memory extensions are OpenClaw's `memory-core` and `memory-lancedb`, already covered — its runtime skill authoring is cited in the skills pattern instead. `litanlitudan/skyagi` states that it "implements the idea of Generative Agents" and has been frozen since August 2023, so the original is the better subject. `xvirobotics/metabot` re-exports a memory client whose backend is not in the repository. `Gitlawb/zero` has context reporting and no memory module. `thClaws/thClaws` has a competent 1,644-line file-entry store that adds little beyond systems already covered, and `skalesapp/skales` (~1,542 lines) is Business Source License 1.1 with no distinctive mechanism found. `wanxingai/LightAgent`'s 196-line shared memory with swappable adapters is cited in the pluggable-provider pattern rather than given a report. `rush86999/atom` has roughly 976 lines of memory-named Python inside a 459 MB repository dominated by deployment scripts; no coherent memory design was established, and that is a weaker conclusion than the others here.
- LlamaIndex ships two APIs under the name "memory": the newer block-based `Memory` reviewed here, and an older `ChatMemoryBuffer` family that is conversation-window management and out of scope. Its tests were not run and no memory benchmark was found.
- No suites or benchmarks were run for open-cowork, Gini, Moltis, or Mercury. open-cowork's eval harness was read but not executed, and no scored results were found committed.
- Gini reimplements the Hindsight memory model locally rather than depending on Hindsight; its recall module cites the source paper's equation numbers, but no check was made that this implementation reproduces the published behaviour.
- Moltis's session sanitization was identified from its module documentation; exactly what it strips was not traced, which matters because transcripts can carry secrets, tool output, and previously injected memory blocks.
- Five further repositories examined in this round have no reports: `he-yufeng/CoreCoder` (1,166 lines whose `context.py` is conversation-window compaction with nothing persisted), `chrysb/alphaclaw` (an OpenClaw deployment harness whose only "memory" reference is host RAM), `Intelligent-Internet/ii-agent` (a SaaS agent platform with chat context and caches but no durable memory), `neomjs/neo` (39 AgentOS documents describing a "Memory Core" that does not appear in `src/` — documentation without a reviewable implementation), and `AgentsMesh/AgentsMesh` (a real pgvector-backed block memory with a `memory.retrieve` MCP tool, set aside for now because it is licensed under Business Source License 1.1 rather than an open-source licence).
- Three repositories examined in the same round were judged out of scope and have no reports: `KnockOutEZ/wigolo` (a web crawl, search, and extraction MCP server whose cache holds external content rather than agent belief), `siyuan-note/siyuan` (a note application whose agent kernel contains no memory concept — only conversation compaction — and whose MCP surface is note CRUD), and `netease-youdao/LobsterAI` (which operates OpenClaw's memory rather than having its own, and is covered inside the OpenClaw report).
- Nothing was run for memora or LoongFlow. Memora's pair classifier is the component that matters — its precision determines which memories get hidden — and no measurement of it was found; the dry-run mode makes exactly that measurable, and nothing indicates it has been done. LoongFlow's tests exist under `tests/agentsdk/memory` but were not run, and no comparison of adaptive against fixed temperature was found, though the code is parameterized for it.
- Six repositories examined in the same round have no reports. `TeleAI-UAGI/Awesome-Agent-Memory` is a survey, cited in the correction discussion rather than reviewed as a system. `webbrain-one/webbrain` (368 lines) and `AmeNetwork/aser` (29 lines) are too small to carry a mechanism. `AgentTeam-TaichuAI/ScienceClaw` is 78 lines with no licence file, and is a different repository from the OpenClaw-derived `beita6969/ScienceClaw` noted above. `ArtificialAnalysis/Stirrup` and `howl-anderson/agentsilex` have no memory subsystem.
- Nothing was run for the six systems added in this round. OptMem is reviewed **without a licence file** — all rights reserved by default — as a deliberate exception to the rule applied to `openyak` and others, because it carries mechanisms the atlas has not otherwise found; the exception covers reading it, not reusing it. MemAgent, HiAgent, Mi-Memory and langchain-ai/memory-agent were examined in the same round and have no reports: MemAgent and HiAgent are conversation-window management (MemAgent is discussed in the scope-boundary section), `Darwin-Agent/Mi-Memory` is a paper PDF and a landing page with no implementation, and `langchain-ai/memory-agent` is a 235-line LangGraph template whose substantive counterpart, LangMem, is already reviewed here.
- **The framework-native gap is now closed**, and closing it corrected the bullet that named it. [CrewAI](../systems/crewai/) — the most-cited omission on that side — is reviewed, as are [Agno](../systems/agno/), [CAMEL](../systems/camel/), the [Pydantic AI Harness](../systems/pydantic-ai-harness/) and [Microsoft Agent Framework](../systems/agent-framework/), which retires Semantic Kernel as a separate entry since it succeeds it. **Haystack was the error.** `deepset-ai/haystack` at `3cef34f2` has no agent memory to review: its `InMemoryDocumentStore` is a RAM-backed document store, `components/agents/state` is a typed run-scoped dict with a merge schema and no persistence layer, and the only things it calls memory stores are `Mem0MemoryStore` and `CogneeMemoryStore` — adapters that live in the separate `haystack-core-integrations` repository and are backed by [Mem0](../systems/mem0/) and [Cognee](../systems/cognee/), both already reviewed here. So this atlas spent several rounds naming as an unreviewed gap a thing that does not exist, and the correct statement is that Haystack is a RAG pipeline framework that mounts other people's memory. With the adjacent contracts — [adk-python](../systems/adk-python/), [AutoGen](../systems/autogen/) and [LangMem](../systems/langmem/) — already read, this atlas no longer has a named framework-native omission. That is a statement about this list, not about the field: the next one will arrive the way all of these did, from somebody naming it.
- **MemGPT is here under its current name.** The project renamed to Letta, so the OS-style tiered-memory reference implementation is the [Letta report](../systems/letta/), and a reader searching this atlas for "MemGPT" will otherwise find only a passing mention in the correction discussion. Recorded because the rename makes the lineage hard to find, not because anything is missing.
- `Cohexa-ai/agent-coherence` was examined and has no report. It is MESI cache-coherence for shared agent artifacts — single-writer ownership, commit-CAS, a read-generation fence, pinned snapshot sessions — and it stores no memory: `CCSStore._apply_put` serialises the value to an opaque JSON string and versions it, never parsing, ranking, scoping or correcting it. What it durably holds is coordination metadata. That is the guard-is-not-a-store shape and the operates-rather-than-believes shape at once, and naming `memory.json` as an example artifact does not change it. Recorded rather than dropped for two reasons. Its premise is a failure this atlas asks about in every report and finds answered in **three** of one hundred and eleven — [Mastra](../systems/mastra-observational-memory/) prevents lost updates with per-scope locks, [Logseq](../systems/logseq/) is last-write-wins, and the [Pydantic AI Harness](../systems/pydantic-ai-harness/) adds an idempotency receipt so a retried write is a replay rather than a second append — so a whole library existing for it says something about the corpus. And its central claim does not hold: the README says *"every spec carries a documented mutant that must fail — the invariants are load-bearing, not decorative"*, the mutants are written out in the specs' comments, and nothing executes them. `make tla-check` asserts six invariants hold; no job asserts a mutated spec fails, which is the standard defence against an invariant passing vacuously. A repository with 60,163 lines of tests documented its negative cases in prose — and the contrast is internal, because its *performance* claim is committed, checksummed and CI-regression-checked: `benchmarks/results/canonical/SUMMARY.md` reproduces its paper's Table 1 with all four figures against tolerances, which is the inverse of the traceability failure this atlas records for Memvid, MemoryOS and FiFA. The same discipline was applied to the speed claim and not to the safety claim. Its paper ([arXiv:2603.15183](https://arxiv.org/abs/2603.15183), 16 March 2026) is also worth noting for selling a different thing than the repository does — the paper leads with simulated token savings and the repository leads with preventing silent clobbers, which on this atlas's terms is the better framing of the same mechanism. See [the note](https://github.com/neoneye/agent-memory-atlas/blob/main/notes/2026-07-29-a-coherence-coordinator-not-a-memory-system.md) for what is unusually honest about it, and for the read-generation fence, which is the one mechanism there that memory systems with restartable background passes appear to need and none here has.
- Core Memory's grounding ceiling, Memanto's conflict-detection precision, Memory Engine's agent clamp, ai-memory's cross-harness continuity claim, ctx's disclosure reachability, and OptMem's cover loss are all directly testable and none was measured here.
- Nothing was run for the four systems added in this round. `gastownhall/beads` and `VectorSpaceLab/general-agentic-memory` were examined and have no reports, for the reasons given in the scope section; GAM additionally has no licence file. `langchain-ai/memory-agent` and `akitaonrails/ai-memory` were re-submitted in this round and were already handled — the first rejected as a 235-line template, the second reviewed.
- Memvid's headline figures ("+35% SOTA on LoCoMo", "+76% multi-hop", "+56% temporal") could not be traced to committed raw artifacts at the inspected commit and are recorded as claims. MemoryOS commits the LoCoMo dataset beside its harness but no scored results were found. Neither was run here.
- SimpleMem is the same finding at six figures rather than three. Its README claims a 26.4% average F1 gain and roughly 30× token reduction on LoCoMo, LoCoMo F1 = 0.613 and Mem-Gallery F1 = 0.810 for Omni-SimpleMem, and +25.7% on LoCoMo with +18.9% on MemBench for EvolveMem, and offers a benchmark runner per pillar. The repository contains **no `.json`, `.jsonl` or `.csv` file of any kind** at the inspected commit, so no scored result, prediction dump or metrics table backs any of the six. Nothing was run here either. Its 311 test functions were not executed, and the transforms carrying its contribution — coreference resolution and time absolutisation in the extraction prompt — have no test or metric anywhere in the repository, so how often they are correct is unknown and is the number the whole design rests on.
- OpenWorker's stated finding — that models without when-to-remember guidance "either never call `remember` or save noise" — is quoted from a source comment. Whether it was measured, and by how much guidance moves behaviour, is not established in the repository.
- `OpenHands/OpenHands` was examined and has no report. At the inspected commit that repository is **Agent Canvas**, an Electron desktop application: four Python files, and the only "memory" references are a `MemoryIcon`, a React `MemoryRouter`, and runtime RAM status. The OpenHands agent platform is a different repository and was not reviewed here.
- `aindilis/autonomous-ai-agent` and `aindilis/free-life-planner` were examined and have no reports. Both are components of FRDCSA, a long-running symbolic-AI project. The first is AgentSpeak(L) BDI agents over SWI-Prolog with **no licence file**, where the three occurrences of "memory" all refer to RAM and compute allocation. The second is a GPL-3.0 Prolog life-management and planning system — calendaring, fluent calculus, a software ontology — whose only belief-related identifier is `hasBeliefSystems/2` in a list of dynamic predicate declarations. Neither contains a memory subsystem: no capture, retrieval, consolidation, or lifecycle. Both are also **not self-contained**, carrying 50 and 352 distinct absolute paths respectively into a `/var/lib/myfrdcsa/` installation that is not in either repository, so neither can be evaluated as it stands.
- `elizaOS/agentmemory` is listed as a representative open-source memory framework in the open-source table of *Memory in the Age of AI Agents* ([arXiv:2512.13564](https://arxiv.org/abs/2512.13564)), and the URL **returns 404**; a search of the `elizaOS` organization finds no repository by that name. It could not be reviewed. Note also the name collision: this atlas's [agentmemory](../systems/agentmemory/) report is `rohitg00/agentmemory`, a different project, and anyone reconciling the two lists by name rather than by URL will merge them.
- `nuster1128/MemEngine` appears in the same table and earned no report: it has no persistence layer at all, as set out in the scope section above, and no licence file.
- Oracle's `oracleagentmemory` was suggested for review and has **no public source repository** — a GitHub search returns only third-party demos consuming the SDK. It cannot be reviewed on this atlas's terms, which require inspectable code at a pinned commit, and is recorded here rather than silently omitted.
- Verel was re-reviewed on 2026-07-28 at `5aa050fe` (v1.9.0) after its author reported the entry was out of date. The previous pin was not merely old but **unreachable from any branch** — GitHub served it by SHA while a full clone did not contain it — so that reading described a state absent from the project's history. The re-read moved Verel from three of the seven rubric capabilities to all seven, and changed four atlas-wide counts. `scripts/check_freshness.py` now distinguishes an orphaned pin from a stale one. Its first run, on 2026-07-28, found 30 stale pins out of the 62 repositories the atlas held that day — a dated measurement rather than a live figure, and one that moves between runs, so read it as magnitude. The same correction is likely waiting elsewhere.
- Agno was read, not run, and its 304 memory-related unit tests were not executed. Three things a live install would settle: whether the supersession judge's default threshold is calibrated against anything, since no calibration was found; how often a typical deployment sets `background_executor`, which decides whether extraction blocks the response path or not; and how often `PROPOSE` mode's prompt-level approval rule is actually followed, which is the number that decides whether the mode means anything and which nothing in the repository measures. Its two memory subsystems — `agno/memory/` and `agno/learn/` — overlap, and which one a given deployment is using was not established beyond noting that the AgentOS HTTP routes serve the older one.
- Six repositories submitted alongside TokenMizer and ZeroStack were examined and have no reports. `Bino5150/lumina`'s memory module opens with *"persistent memory across sessions via SQLite. **Write-through to MemPalace on save.** Flat table preserved for migration + fallback"* — so its durable store is [MemPalace](../systems/mempalace/), already reviewed here, behind a 291-line client with a flat-table fallback. It is the first system in the corpus whose primary memory is another atlas entry. `octelium/cordium` is a Kubernetes sandbox platform for identity-based secretless access to infrastructure; it has no memory concept. `faramesh/faramesh-core` and `9hannahnine-jpg/arc-gate` are both **guards rather than stores** — Faramesh is a policy daemon that permits, defers or denies each tool call against a declared `governance.fms`, and its `MemoryBackend` is an in-RAM `State` object for single-node deployments; Arc Gate is a runtime proxy whose purpose is preventing agents acting on hidden instructions. Neither durably holds anything an agent later retrieves as belief, which is the guard-is-not-a-store shape already recorded for `Cohexa-ai/agent-coherence`. `trumae/mei` is a 209-line stateless C99 orchestrator that uses Fossil SCM as its single source of truth — the same instinct as [GitLord](../systems/gitlord/), at a size too small to carry a mechanism. `jaylfc/taOS` is dual-licensed AGPL-3.0 and commercial, and its `user_memory.py` is 193 lines over a base store; the one idea worth citing is its settings block, which lets a user toggle `capture_conversations`, `capture_files`, `capture_searches` and `capture_notes` independently, so *what is eligible to be remembered* is a user preference rather than an extractor's judgement — a small instance of the who-decides divergence, at a scale that does not earn a report.
- Four repositories submitted alongside Cortex, Mnemopi and agent-afk were examined and have no reports. `proxysoul/soulforge` carries a 3,577-line memory package under **Business Source License 1.1**, which is not an open-source licence — the same call already applied to `skalesapp/skales` and `AgentsMesh/AgentsMesh`, and no mechanism was found that would earn the exception made for OptMem. `omnigent-ai/omnigent` mounts [Hindsight](../systems/hindsight/) as a built-in tool exposing its retain/recall/reflect operations, so its memory is a client for a system this atlas already reviews; the one detail worth keeping is that the memory bank is resolved per invocation from the agent spec, falling back to the run identity, so a single declaration isolates memory per agent. `opsyhq/wolli` (233 lines of session memory storage) and `fischerf/aar` (a 165-line session store) are both too small to carry a mechanism. `Fagoon-AI/upgrade` was read at `f027d614` and falls outside the inclusion test. Its `WorkflowMemory` is a message row — `workflow_id`, `conversation_id`, `role` from a five-value set, `content`, metadata, an estimated token count and a TTL — and its `MemoryNode` offers exactly six operations: add, get all, get, delete, prune and stats. **There is no embedding, no vector, no similarity and no search anywhere in either file**; the vector tables that migration creates belong to `knowledgedocument`, the RAG side, not to memory. So what survives a run is the transcript, listed by conversation rather than retrieved, and the `conversation_id` field defaults to the execution id — one run. That is the call already made for [Pi](../systems/pi/), for LlamaIndex's `ChatMemoryBuffer` family, and for OpenAI's `SQLiteSession`. The comparison worth recording is with [CAMEL](../systems/camel/), which *did* earn a report on a similar-looking message store: CAMEL's `VectorDBMemory` embeds messages and recalls them by similarity across sessions, which is retrieval; this lists them by key, which is storage. The line between the two is one index.
- Three repositories submitted in the same round were examined and have no reports. `ahmadvh/octochains` (4,406 lines, **no licence file**) is a framework for *parallel isolated* multi-agent reasoning whose stated premise is that shared chat history contaminates independent judgement — it has no memory concept because avoiding one is the design, which makes it the most pointed out-of-scope entry the atlas has recorded. `aleloro-dev/ago` is a 1,313-line zero-dependency Go agent library with **no licence file** and no persistence of any kind. `Gitlawb/zero` was re-examined at `d37de9214b` after growing to roughly 332,000 lines of Go since the earlier pass, and the earlier conclusion holds: `internal/background` and `internal/swarm` coordinate work, and there is still no memory module.
- **A mark that was wrong, and how it was found.** [Mem0Sharp](../systems/mem0sharp/) earned `audit_log` on 30 July for a history table written only by `INSERT`. The atlas's [Mem0](../systems/mem0/) report, of the system that C# port reimplements, carried only `scope_enforced` — a divergence recorded the same day as a limitation rather than resolved. Re-reading `mem0/mem0/memory/storage.py` at the pinned commit settled it: Mem0's `history` table is `id`, `memory_id`, `old_memory`, `new_memory`, `event`, `created_at`, `updated_at`, `is_deleted`, `actor_id`, `role`, written only by `add_history` and `batch_add_history`, with no `UPDATE` and no `DELETE` against it anywhere in the file. **Mem0 was under-marked and now carries `audit_log`.** Worth recording as a methodology note rather than a correction: the defect was invisible for two months and surfaced only because an independent reimplementation of the same design was reviewed and marked differently. A corpus wide enough to contain a system twice is a corpus that can check itself, and nothing in this atlas's process was doing that deliberately.
- `unibaseio/membase` was examined and has no report. Its memory is roughly 1,400 lines of conversation-keyed message buffers with LLM summarisation into a long-term memory and a profile, plus Chroma retrieval — well-covered ground here — beside a larger `chain/` package that is the project's actual subject. It carries **no licence file at this commit**, while its README states "MIT License. See [LICENSE](./LICENSE)" and links to a file that is not in the repository, so the licence is asserted and absent rather than merely missing. That is the same rule applied to `openyak` above, with an extra wrinkle, and the mechanisms did not clear the bar the [OptMem](../systems/optmem/) exception was made for. One thing in it is worth citing anyway: `membase/storage/hub.py` forces the `owner` field on every upload to the caller's recovered ETH signer address, warning loudly rather than silently accepting the legacy behaviour of passing an arbitrary owner string, because the hub now `401`s when `owner != signer`. Ownership proved by signature rather than asserted in a field is adjacent to [Aukora Kernel](../systems/aukora-kernel/)'s reader proof-of-possession and [Buzz](../systems/buzz/)'s blinded index, and is the only part of the repository this atlas does not already cover.
- `pi-chat` is a separate repository and was not reviewed; the claim that it injects two persistent memory files every turn comes from its documentation, not from its code.
- Helm was read, not run. Three claims in its report are inferences from code that a live database would settle: that `getAutonomyMode` returns the stale pre-supersession row (argued from SQLite's partial-index eligibility and rowid scan order, and consistent with the 82 duplicate supersessions of that one key recorded in the project's own changelog); that the 500-row recall window is reached in practice, which depends on a fact count that is gitignored; and which of the three retrieval quality tiers a typical install actually runs, since the MiniLM model is an explicit opt-in download and all three tiers produce the same output shape. Helm's third memory surface could not be reviewed at all: twelve `cortex.*` tools are registered and documented as a five-layer memory stack, and `workspace/cortex/` is gitignored and absent from the repository.

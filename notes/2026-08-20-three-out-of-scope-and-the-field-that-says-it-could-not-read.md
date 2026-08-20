# Three out of scope, and the field that says it could not read

**Status:** triage. Three of the eleven repositories submitted on 2026-08-20 are
not agent memory, and one of them carries a field this atlas has argued for
without ever finding a worked example.
Recorded alongside the four that were: [AIPass](../content/systems/aipass.md)
and [NexusMem](../content/systems/nexusmem.md) re-read,
[Muninn](../content/systems/muninn.md) and
[AgentDatabase](../content/systems/agentdatabase.md) added.
**Origin:** eleven links submitted together.

Four of the eleven were already pinned to their current `HEAD` with no commits
since — [memoir](../content/systems/memoir-cli.md),
[breadcrumbs](../content/systems/breadcrumbs.md),
[hippo-memory](../content/systems/hippo-memory.md) and
[MeMex-Zero-RAG](../content/systems/memex-zero-rag.md) — so nothing was re-read
and nothing was re-pinned. A report already at upstream `HEAD` is a finished
reading, and bumping `analyzed_at` without opening the tree would assert work
that did not happen.

---

## Semant — `adarshh347/Semant` at [`40cc63096592a562772c90c74bd7874c1f0ee21c`](https://github.com/adarshh347/Semant/commit/40cc63096592a562772c90c74bd7874c1f0ee21c)

**Excluded, and the most useful exclusion in this batch.** No licence file. An
"embodied perceptual runtime": a vision-and-curation system over MongoDB with
agents, atlases, corpora and a director that plans multi-step perceptual work.
Screened clean apart from one build-time execution point and six unpinned
surfaces; nothing was installed.

The file called `memory` is `backend/services/director/memory.py`, and its
header says what it is: *"working memory: the packet every step is handed"*, a
**pure module** with *"no database, no fetch, no clock it is not handed."* It
exists to stop an actuator firing blind — *"a step that does not know what has
already been found will re-find it, contradict it, or ask the curator something
they already answered."* That is intra-plan state, not memory that outlives a
session, so it fails the scope test at the first clause. `corpus_store.py` does
persist — *"a named, ordered walk that outlives the canvas built over it"* — but
a curated ordering of content is not a store of beliefs that can be corrected.

Six ideas in that one 191-line file are worth more than most in-scope reports
supply.

**1. Silence is a field, not an inference.** The packet carries
`unreadable: Tuple[str, ...]` — *"everything asked for and not obtained. NEVER
inferred from an empty list above: 'no marks' and 'could not read the marks' are
different facts."* This atlas has argued that absence assertions need positive
controls, that an audit log that renders only what it caught is misleading, and
that a store which returns nothing must say whether it looked. Here the
distinction is a field on the record, and it is the cleanest expression of it
found so far. Any memory system whose retrieval can partially fail should carry
the same thing: what was queried and did not answer, beside what was queried and
came back empty.

**2. Provenance of *how* a claim arrived, not just from whom.** `phrase_source`
distinguishes the curator's words typed into the workspace before anything ran
from the same words given mid-loop as the answer to a question the system asked.
The comment is the argument: *"Both are the curator's words and neither is
invented, but they are not the same event, and anything produced from the phrase
should be able to say which one it was rather than have a reader assume the
first."* Every extraction-based store in this corpus records the user as the
source and loses the difference between what a person volunteered and what a
model prompted out of them, which is exactly the difference that matters when
the memory is later disputed.

**3. Discipline carried as data so a prompt author cannot edit it.**
`constraints` is a dict on the packet *"carried as DATA and not prose, so it
cannot be quietly edited by whoever writes the eventual planner prompt."* The
corpus's recurring failure is a rule that lives only in a system prompt and
degrades silently; this is the one-line structural answer.

**4. A frozen packet with `evolve()` returning a new one**, because *"an executed
plan must be able to show what memory looked like at step 3, which is impossible
if step 5 has already overwritten it."* That is bi-temporal reasoning at the
scale of a single plan.

**5. Projections are marked so nothing mistakes them for records.** When the
planner reasons ahead, the ids it invents are `step_id#kind@n`, *"marked with
'#' precisely so nothing downstream"* treats a projection as a real record. The
atlas has repeatedly found stores where a derived or predicted item is
indistinguishable from an observed one.

**6. An empty value must not satisfy a requirement.** `available()` counts a
phrase as present only when it is non-empty, *"or… fabrication returns by the
back door with an empty query."* A dependency check that a blank satisfies is a
gate that is not there.

Nothing here is memory. All six would improve a memory system.

## OpenLawAI — `MSNetrom/OpenLawAI` at [`392d777212f2051573757622ddd347da9fdd5da0`](https://github.com/MSNetrom/OpenLawAI/commit/392d777212f2051573757622ddd347da9fdd5da0)

**Excluded: conversation-window management plus document retrieval.** AGPL-3.0,
Django and React, Weaviate as the vector store, an AI legal assistant over
Lovdata's free Norwegian public datasets. Screened clean; two unpinned surfaces,
nothing installed.

Its `chatdb` app declares exactly three models: `ChatConversation` (with a
`deleted_at` soft-delete, a `last_message` and a `message_count`),
`ChatMessage`, and `UserDocument` (an uploaded PDF or image with extracted text,
page, token and chunk counts). There is no memory model, no fact, no preference,
no profile and no cross-conversation state of any kind. What survives a session
is a transcript and the documents attached to it — the transcript is the
conversation window persisted, and the legal corpus is a static index that no
agent corrects.

That is the [not in scope](../content/overview.md) boundary the atlas draws
between a store of beliefs and a store of documents, and this falls on the
document side twice over. Recorded so a later reader does not re-check it. Worth
noting only that the soft delete is on the conversation and not on the uploaded
document rows, so a user deleting a conversation leaves the extracted text of
their uploads in the database — which is a real deletion-cascade question, in a
jurisdiction that has opinions about it.

## AI Agent Security — `jralmaraz/ai-agent-security` at [`de6e88ac42b7e10ee885d4dbe701a0eb1aadcb7c`](https://github.com/jralmaraz/ai-agent-security/commit/de6e88ac42b7e10ee885d4dbe701a0eb1aadcb7c)

**Excluded: identity and delegation, not memory.** MIT, Go, a stated research
proof of concept — *"not production software"* — implementing IETF WIMSE and
OAuth drafts for multi-hop agent calls. Screened clean; one auto-run surface
(`.githooks/`), one build-time execution point (`Makefile`).

Nothing is stored that outlives a request by design; the tokens are short-lived
and replay detection exists to make sure they are used once. It gets no report.

The reason to record it is that it answers a question the atlas keeps reaching
and has no vocabulary for: **when a memory arrives from another agent, what
exactly does the receiver know about where it has been?** The design's answer is
a chain rather than a claim. An `AgentToken` carries `role`, a `chain_depth`
that must be *"strictly sequential (0, 1, 2, …)"* with no gaps or resets across
the chain, and a `cnf.jwk` binding the token to a key the agent holds; a
per-request `AgentProofToken` is signed by that key and bound to the exact target
URI, so a token lifted from one hop cannot be replayed at another.

Set that beside [Portable Handoff](../content/systems/portable-handoff.md),
where trust is capped by provenance at parse time, and the pairing is the useful
part. Portable Handoff decides how much to *believe* an imported memory; this
decides whether the import is *from whom it says*. Both halves are needed and the
corpus has almost nothing on the second: cross-agent memory here is generally a
file, a webhook or a shared table, with the sender's identity asserted in a field
the sender wrote. A memory system that wanted to do better would not need this
implementation — it would need the idea that the delegation path is data the
receiver validates, rather than a header it reads.

---

## For next time

**Four of eleven needed nothing, and saying so is the result.** Half a batch of
"re-analyze these" resolved to "already at `HEAD`". The temptation is to re-read
anyway so the turn has output; the honest move is to check the pin, say nothing
moved, and spend the time on the two that did — one of which turned out to be
carrying two unfound capability marks.

**The out-of-scope pile keeps producing the best single ideas.** `unreadable[]`
is the third time in a week that a repository excluded on the scope test has
contributed a mechanism the in-scope corpus lacks. The pattern is not accidental:
a system built for a different problem has not inherited the field's habits, so
it solves the shared sub-problem — how do you record that you could not tell? —
without the standard wrong answer.

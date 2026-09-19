---
title: "ripwire"
eyebrow: "Heal the two sidecars, and every consumer is rename-aware"
description: "A C++ code-context engine whose memory is two committed sidecars — a ledger of deliberately accepted quality findings, each keyed to a symbol and pinned at the magnitude it was accepted at so it resurfaces the moment the finding worsens, with a content hash that re-files it across a rename and refuses to across a rewrite; and a field-notes file surfaced beside the symbol it names."
root: ../..
page_kind: system
source_name: "redhat-et/ripwire"
source_url: https://github.com/redhat-et/ripwire
archive_name: "redhat-et--ripwire"
revision: e54b688e63c0041049b49a8bf63997f8cd299844
revision_url: https://github.com/redhat-et/ripwire/commit/e54b688e63c0041049b49a8bf63997f8cd299844
analyzed_at: 2026-09-19
capabilities: "negative_eval"
capability_evidence:
  negative_eval: "a dangling note that must appear in the listing and nowhere else, and an ack that must not survive a real change, both asserted against populated retrievals with positive controls beside them | test/notescheck.sh:150-170, test/identitycheck.sh:21-24, :187-218 | The notes case writes a note against a target that does not exist, asserts the listing shows it as `dangling=\"1\"` and shows a live target as `dangling=\"0\"`, then asserts its text appears in neither a task-scoped retrieval nor the default map — a must-not against two populated emissions with the positive control in the same script. The identity gate is the stronger half, because it pins the *boundary* of a rescue rather than only its success: claim (C) states that identity following a rename *\"must not become identity that follows a rewrite — that would turn the ratchet into the blank check its own contract forbids\"*, held by two arms, a worsened finding that must re-report across a rename and a moved-and-rewritten body that must not be content-matched | the gate runs on a synthetic git repository *\"so it never depends on ripwire's own current debt or ack ledger\"*, which is the property that keeps the assertion from passing for the wrong reason"
stack_storage: "files"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "Two. An ack is one deliberately accepted finding — a kind token, a 16-hex key over the symbol's path, scope and name, the magnitude it was accepted at, an optional content hash of the scrubbed body, an optional scope that wrote it, and a free-text reason. A note is a target — a canonical `path::scope::name` or a path — with a date, a text, and optionally the HEAD sha and branch it was written on"
  storage: "Two plain files at the analyzed root, both committed: `.ripwire_quality_acks` (1,310 rows) and `.ripwire_notes` (three rows). Both are sorted for merge friendliness; the ack file publishes atomically under a cross-process lock, the notes file truncates and rewrites without one"
  retrieval: "Notes are surfaced by exact-string match on a canonical id or a root-relative path, riding along with the symbol or file in the task-scoped map, the default map, the expansion, the edit check and three MCP verbs. Acks are not retrieved; they are consulted as a filter when the quality delta is rendered"
  write: "`--quality-ack[=REASON]` merges every finding the current delta reports into the ledger at its present magnitude; `--note-add` resolves a selector through the same resolver the read verbs use and refuses an ambiguous one, warning loudly on a target that resolves to nothing. Both are command-line acts; no MCP verb writes either store"
  update_delete: "An ack is replaced in place by a later ack at a new magnitude, and its reason chain is capped at one hop so an older segment is dropped rather than accumulated. A rename or a move re-files an ack onto the current key through a healing pre-pass that rewrites the two sidecars before anything reads them — by the git-recorded rename map first, then by scrubbed-content-hash equality — and `--quality-ack` writes the healed rows back, so a rescued ack stops depending on the replay. A rewrite deliberately does not match. Nothing retires a stale row automatically — a past round retired 109 by hand"
  scoping: "None enforced. An ack row can record the scope that wrote it and the field is read only to build a disclosure row; the suppression test never consults it, so an ack filed under one scope suppresses findings anywhere. The runtime `--scope` glob filters what is analysed, which is an argument rather than a stored key"
  integration: "A single compiled binary with a large flag surface, an MCP server of thirty-one verbs, editor and agent hooks, and a set of agent skills that tell a model when to ack and when to look"
  background: "None. Every read and every write is a command"
  trust: "None on a stored memory. A stale ack is classified — its target is gone, its finding is gone, or it was filed from a foreign scope — and the classification is emitted as disclosure only; the suppression test consults presence and magnitude alone, so a stale ack keeps suppressing"
  strengths: "A ratchet rather than a suppression: an ack accepts a finding at its measured size and re-reports it the moment it worsens past that, with a zero-magnitude guard so a finding with no magnitude cannot become a blank check. The repair for a move is the part worth studying: rather than teaching nine call sites to try an alias — *\"each an independent chance to get the direction backwards\"* — the two sidecars are rekeyed forward into the identity the current tree uses, once, before anything reads them, so `computeDelta`, the ack ratchet, the stale-ack classifier and the ack writer become rename-aware with no edit at all, and it is self-healing because `--quality-ack` writes the rekeyed ledger back. The rescue route is kept per row rather than as a total, because surviving through a git-recorded rename and surviving through scrubbed-content equality are *\"different claims with different trust\"*. A ledger kept committed so what is suppressed is reviewable in a diff. And a survival measurement the project ran against its own history and published as the motivation for the repair"
  risks: "A stale ack is classified and never acted on: its target is gone, its finding is gone, or it was filed from a foreign scope, and the classification is emitted as disclosure while the suppression test consults presence and magnitude alone, so a stale ack keeps suppressing. The rescue that carries an ack across a move is the most load-bearing machinery in the tool and the least visible to the person relying on it — a row rescued by scrubbed-content equality is a weaker claim than one rescued by a git-recorded rename, which is why the route is disclosed per row, but nothing refuses the weaker route. The notes store has no rescue route at all and no lock on its writer. The project's own skill instructs an agent to write acks unattended, and no CI job reads either sidecar, so the review the committed ledger makes possible is a review somebody still has to perform. And the surface is very large for six weeks of work: 172,653 lines across 167 files, with two auto-run surfaces and four unpinned dependency surfaces at this pin"
---

## 1. Executive Summary

ripwire is a code-context engine for coding agents — Apache-2.0, 2,896 commits
between 31 July and 16 September 2026, 172,653 lines of C++23 across 167 files
under `src/`, with 618 gate scripts named by the loop in its own regression
runner and all 618 resolving to a file. Twenty commit identities appear, of which one
accounts for 1,903 of them. The screen found two auto-run surfaces — an MCP
manifest and a hooks directory — and four unpinned surfaces; nothing was
installed or run, and the read was made from a full clone.

**Most of the tool is out of this atlas's scope, and two files in it are
squarely in.** The call graph, the ranking and the lenses are a code index, and
a code index is a projection of source that cannot turn out to be false. What
this report is about is the pair of committed sidecars beside them:
`.ripwire_quality_acks`, 1,310 rows recording findings a person or an agent
deliberately accepted, and `.ripwire_notes`, a field-notes file whose entries are
surfaced beside the symbol they name. Both hold judgements that can be wrong,
both survive every session, and both can be corrected.

**The ack ledger is a ratchet, and that is the idea worth carrying.** A row is
`ack <kind> <16-hex key> <magnitude> [cid=…] [by=…] <reason>`, and the whole
mechanism is one comparison (`src/quality.h:5798-5802`):

```cpp
const auto it = acks.find( ackMapKey( ackKindToken( r ), r.key ) );
return ( it != acks.end() && r.now <= it->second.ackNow ) ? &it->second : nullptr;
```

An ack accepts a finding **at the size it was accepted at**. The moment the
finding worsens past that magnitude it reappears, which the source states as the
contract — *"an ack accepts a finding AT its acked size, never a blank check"*
(`src/quality.h:4838`). Suppression is disclosed rather than silent: the report
header carries an `acked` count. And the contract has been defended against its
own degenerate case: a finding whose magnitude is zero would make the test
`0 <= 0` and suppress forever, *"a permanent blank check, which the ack contract
explicitly promises never to be"* (`src/quality.h:4592-4594`), so the kind token
is qualified by origin to keep that from happening.

**Two marks.** `human_review` on a ledger the project keeps committed precisely
so that a change in what is suppressed shows up in a diff, beside a `--notes`
listing that flags a note whose target no longer resolves so a person can prune
it. `negative_eval` on a case that writes a note against a target that does not
exist and asserts its text appears in neither the task-scoped retrieval nor the
default map, with the positive control in the same script.

**Why `tombstone` is withheld, and it is the most interesting call in this
report.** Everything about the ack ledger looks like the mark: durable,
committed, consulted before the tool speaks again, with a magnitude floor that
stops it being a blanket. Three things decide against it. The key is a location
— `fnv1a64(relative path \0 scope \0 symbol name)` (`src/quality.h:733-740`) —
so it identifies *where* a finding was, not *what* was rejected. What the row
records is an **accepted** finding rather than a rejected value; it suppresses a
warning about code that stays. And it is consulted when a report is rendered
rather than when anything is written, so nothing prevents the same code being
written again. The near-miss is written up in section 9 because the one part of
the mechanism that *is* value-keyed — the `cid` content hash — is used with an
unusual precision the mark's own definition is about.

**The location key does not survive a move, and the repair is the thing to take
away.** The project measured the damage against its own history rather than
asserting it: on a commit where ten headers moved into `src/infra/` with not one
byte of code changed, not one of the fifty-nine canonical ids survived, nor any
of the fifty-nine path-qualified keys, nor any of the four clone groups — and in
the source's own words, *"[e]very ack recorded against those symbols died, along
with the reason someone wrote for accepting each one"*
(`src/quality.h:5300-5303`). The obvious fix — teach every baseline lookup and
the ratchet to try an alias — is rejected in the same comment, and the reason is
an argument about *where* a repair belongs:

> "means touching nine call sites inside computeDelta plus applyAckRatchet, each
> an independent chance to get the direction backwards. The repair actually
> taken is the opposite: leave every consumer alone and REKEY THE TWO SIDECARS
> FORWARD into the identity the current tree uses, once, before anything reads
> them."

`healIdentity` runs that pre-pass and `remapAckIdentity` rewrites the ledger
inside it, by the git-recorded rename map first and scrubbed-content-hash
equality second. Because the baseline snapshot and the ack ledger are the only
two things carrying a stale identity, healing them makes `computeDelta`, the
ratchet, the stale-ack classifier and the `--quality-ack` writer rename-aware
with no edit at all. It is wired on four paths — two in `src/verbs_quality.h`,
the history walk at `:907`, and the MCP delta at `src/mcpverbs.h:3401` — and it
is self-healing, because `--quality-ack` writes the rekeyed rows back, so a
rescued ack stops depending on the replay.

**The rescue discloses which route saved each row, and that is the honest part.**
`AckRescueRoute` is kept per ack rather than as a total, on a stated argument:

> "your ack survived because git recorded the rename" and "because the body is
> byte-for-byte the same after scrubbing" are different claims with different
> trust, and collapsing them would hide which one the tool actually relied on.

The boundary is pinned by a gate rather than by the comment. `identitycheck.sh`
holds three claims *"none of which may be traded for either of the others"*: an
ack survives a file rename, staged or committed; an ack survives a pure move git
records no rename for, via scrubbed-content equality including a re-indent —
with the measurement that motivates the scrub, 37.3% survival on raw body hashes
under a four-space re-indent against 100% on byte-identical moves; and an ack
does **not** survive a real change, because identity that follows a rename
*"must not become identity that follows a rewrite — that would turn the ratchet
into the blank check its own contract forbids."*

**Three findings sit against the design.** A stale ack is classified into three
reasons and never acted on. The notes store has none of the ack side's
protections — no rescue route, no write lock — and nothing in its format can say
a row has gone out of date. And the MCP verb advertised as *"most relevant memory notes / docs for a
task"* (`src/mcp.h:65`) does not read the notes store at all.

## 2. Mental Model

A memory here is **a judgement about a place in the code**, and there are two
kinds.

An **ack** says *this finding is acceptable, at this size, for this reason*. It
is written when a person or an agent has looked at a warning and decided to keep
the code. It is not an exemption: it is a floor, and crossing the floor brings
the warning back.

A **note** says *here is what someone learned about this thing*. It attaches to
a canonical id or a path, and it rides along whenever the tool next describes
that symbol or file to an agent, so the knowledge arrives at the moment it is
relevant rather than when someone thinks to look for it.

Neither has a status, a confidence or a validity window. Both are corrected by
being rewritten, and both are forgotten by being deleted from a file a person
edits.

The identity question is the whole design problem, and the project treats it as
one. A judgement about a symbol has to survive the symbol being renamed or moved,
and must *not* survive the symbol being rewritten — because the thing that was
judged is gone. The ack side has two rescue routes and a published measurement
of how well they work. The notes side has neither.

```mermaid
%% caption: the quality delta reports findings, and an ack accepts one at its current magnitude into a committed ledger keyed on the symbol's path, scope and name; a later run suppresses that finding only while it stays at or below the acked magnitude, re-reports it the moment it worsens, and before any of that re-files a row whose location key no longer resolves through a git rename or a unique content hash — never through a rewritten body
flowchart TB
    RUN["ripwire <dir> --quality-delta"]
    FIND["findings: complexity,<br/>verbosity, api-surface,<br/>duplication, churn, clones"]
    HEAL{"does this ack's location key<br/>still name a symbol?"}
    RESC{"a git rename, or a<br/>unique content hash?"}
    REKEY["re-file the row onto<br/>the new location key"]
    STALE["classified stale:<br/>target gone, finding gone,<br/>or foreign scope;<br/>disclosed, never acted on"]
    TEST{"is this finding acked,<br/>and is now &lt;= the<br/>acked magnitude?"}
    SUP["suppressed, and counted<br/>in the report header"]
    REP["reported: it worsened<br/>past what was accepted"]
    ACK["ripwire <dir> --quality-ack=REASON"]
    LEDGER[("committed ledger:<br/>kind, 16-hex key, magnitude,<br/>cid, scope, reason")]
    DIFF["a change in what is<br/>suppressed shows up<br/>in git diff"]

    RUN --> FIND
    LEDGER --> HEAL
    HEAL -- no --> RESC
    RESC -- yes --> REKEY
    RESC -- "no, or the body was rewritten" --> STALE
    HEAL -- yes --> TEST
    REKEY --> TEST
    FIND --> TEST
    TEST -- yes --> SUP
    TEST -- no --> REP
    REP --> ACK
    ACK --> LEDGER
    LEDGER --> DIFF
```

## 3. Architecture

A single compiled binary, header-heavy: 148 headers and six translation units.
The largest are `src/serialize.h` (7,479 lines), `src/quality.h` (6,078),
`src/graph.h` (5,787), `src/mcpverbs.h` (4,824), `src/cli.h` (4,548) and
`src/main.cpp` (4,062). Everything this report is about lives in
`src/quality.h` and `src/notes.h`, with the verbs in `src/verbs_quality.h` and
the surfacing in `src/serialize.h`.

Around them: `test/` holds 1,347 files including 610 shell gates and per-language
fixture corpora; `bench/` holds harnesses, locked datasets and committed results;
`third_party/` vendors the container and parser libraries; `docs/` holds a
12,678-line evaluation document and a lineage table; `skills/` holds the agent
skills that tell a model when to ack.

### Deployment and ergonomics

- **What has to run:** the binary. Runtime dependencies are none by design.
- **Fully local and offline:** yes, entirely.
- **Hand-repairable:** both stores are sorted text a person can edit, and both
  are committed, so a bad row is a revert away.
- **Install:** a script, a release binary, or a source build.

## 4. Essential Implementation Paths

- **Key a finding.** `pathQualifiedKey` (`src/quality.h:565-573`) hashes the
  root-relative path, the scope and the name with a null byte between each;
  `qualityKey` (`:654-658`) is the symbol-level caller. The two clone kinds key
  on a member-set hash instead.
- **Compute the content id.** `scrubbedBody` and `scrubbedBodyHash` (`src/quality.h:828-898`)
  hashes the body after collapsing whitespace, replacing the symbol's own name
  with a sentinel and dropping ack comment lines. Built corpus-wide with a
  count per id, so a body shared by two symbols refuses to resolve.
- **Heal an identity.** `remapAckIdentity` (`src/quality.h:4677-4755`) runs
  before the ratchet and re-files a row only when its own key resolves to
  nothing, it carries a content id, and that id is unique — preferring a
  git-recorded rename over a content match. The comment states the boundary:
  *"Identity that follows a rename must not become identity that follows a
  rewrite; that is the blank check the ack contract forbids"* (`:4673-4675`).
- **Apply the ratchet.** `findSuppressingAck` (`:5798-5802`) and
  `applyAckRatchet` (`:4907-4918`).
- **Write an ack.** `--quality-ack[=REASON]` (`src/cli.h:2667`, `:4506`) implies
  the delta, refuses reason-less spellings unless the delta is also requested,
  and is gated by `refuseForeignAckSelection` (`src/verbs_quality.h:401-441`)
  against an `--ack-only` that names rows outside the scope under review. The
  row is built at `:1141-1144` and published at `:1157` through an atomic write
  under a cross-process lock.
- **Add a note.** `resolveNoteAddTarget` (`src/main.cpp:606-670`) resolves the
  selector through the same resolver the read verbs use: unique stores the
  canonical id, ambiguous refuses and names every candidate, and a path that
  resolves to nothing stores with a loud dangling warning.
- **Surface a note.** `fileNoteTarget` and `symbolNoteTarget`
  (`src/serialize.h:503-511`) spell the two lookup keys once;
  `renderNoteChildren` (`:471-489`) attaches them, reached from the task map,
  the default map, the expansion, the edit check and three MCP verbs.
- **List notes for pruning.** `--notes` (`src/main.cpp:798-860`) recomputes the
  live target set and emits per-target rows with a dangling flag.

## 5. Memory Data Model

An **ack row**: a kind token, the 16-hex key, the accepted magnitude, an
optional `cid`, an optional `by` scope and a reason to end of line. Of the 1,310
committed rows, 925 carry a content id and 202 carry a scope. The kind
distribution is led by short-horizon churn (439), new-symbol api-surface (202),
api-surface (160) and duplication (139). Magnitudes run from 0 — 211 rows — to
1,731.

A **note**: a target, a date taken from git's committer clock, the text, and
optionally the HEAD sha and branch. One row is committed.

**Temporal:** one time on a note, none on an ack, and the absence is deliberate:
*"Deliberately NOT pinned to a HEAD sha: an acked finding … stays accepted
across commits"* (`src/quality.h:3941-3943`). `bitemporal` withheld.

**Trust:** none applied. `StaleAckWhy` (`src/quality.h:4936-4941`) is a real
three-value classification — the target is gone, the finding is gone, or the row
was filed from a foreign scope — and it is emitted as disclosure rows and never
read by the suppression test. `trust_state` withheld.

**Scoping:** the `by` field is written and read only to build a disclosure row.
`scope_enforced` withheld.

**Tombstone:** withheld — see section 9.

## 6. Retrieval Mechanics

Notes are retrieved by **exact string match** on a root-relative path or a
canonical `path::scope::name`, through a map built once per run. There is no
ranking, no fuzzy match and no fallback, which is the right choice for a store
whose whole value is arriving beside the right symbol — and it is also the reason
a rename silences a note without any error.

Acks are not retrieved at all in the ordinary sense. They are a filter applied
when the quality delta is rendered, and the number suppressed is disclosed.

**Failure modes.** A note whose target moves becomes inert: the lookup misses,
nothing surfaces, and only the `--notes` listing reveals it. An ack whose symbol
moves is rescued if a rename is recorded in git or its body is unchanged and
unique, and is otherwise classified stale and left in place. And because the
rescue routes were added after most of the ledger was written, the source is
explicit that they *"can never rescue the 443 rows already committed here, and
the report says so"* (`src/quality.h:5567`).

## 7. Write Mechanics

Both stores are written by command-line verbs only — no MCP verb writes either —
and both are sorted on every write so that two branches merge cleanly.

The ack writer is careful in ways worth naming. It publishes atomically under a
cross-process lock, added after a measured torn-write incident. It root-qualifies
the file name rather than trusting the working directory, after an observed case
where acking one root rewrote another root's committed ledger. And it refuses an
`--ack-only` selection that names rows outside the scope under review, which is
the rubber-stamp guard.

Two things it does not do. A reason is not required — a bare `--quality-ack`
alongside the delta is accepted and renders the literal string
`(no reason given)`, though no committed row carries it. And the reason chain is
capped at one hop, so a row acked three times keeps the newest reason and the one
before it, *"without turning the ledger into an append-only reason log"*
(`src/quality.h:3988`).

The note writer has none of this: a plain truncating stream with no lock, in a
file whose header cites the ack precedent for its sorted format.

### Operational cost

- Reading both sidecars is two file reads per run.
- The identity heal is a pre-pass over the ledger against the live symbol table.
- Nothing runs in the background and nothing calls a model.

## 8. Agent Integration

Thirty-one MCP verbs, all read-only with respect to these two stores. Notes ride
along with the symbol descriptions the agent already asked for, which is the
integration decision that matters: the agent does not have to know the memory
exists to receive it.

The agent skills close the loop on the ack side, telling a model to
*"record a trade-off instead of re-reading it forever"* with a worked command.
That is the mechanism working as designed, and it is also why the review
qualification in section 9 matters: the same verb a person uses deliberately is
one an agent is instructed to use unattended.

## 9. Reliability, Safety, and Trust

**Human review — withdrawn on the 2026-09-19 re-read, and the ledger is still
worth copying.** The adjudication is `--quality-ack`: a finding is looked at and
accepted at a magnitude with a reason, and the verdict is committed to a file the
project keeps in version control for exactly this reason — *"the ack file is
committed precisely so a change in what is suppressed is reviewable"*. The
inspection is `--notes`, which recomputes the live target set so a person can see
what has gone dangling, described in the source as *"listed here so the human can
prune it"*. Both are real, and the ratchet behind them — an ack accepts a finding
at its measured size and re-reports it the moment it worsens — is better
engineering than most review queues in this corpus.

The mark asks a narrower question: can the agent that produced the debt also
clear its review? Here the answer is not merely yes, it is documented. The
shipped skills spell the command out for the model to run —
`ripwire <dir> --quality-ack="why it's accepted"`
(`skills/ripwire-quality-bar/SKILL.md:178`), `--ack-only=contract-change
--quality-ack="arity change required by <fix>"` (`:188`), `--quality-ack="deliberate"`
(`:206`) — and two more skills tell an agent to *graduate* a recurring comment
into an ack reason (`skills/ripwire-handoff/SKILL.md:44`,
`skills/ripwire-orient/SKILL.md:183`). No MCP verb writes the ledger, and the
MCP `quality_delta` is declared read-only, so the ack is a command-line act; but
a command-line act the project instructs the agent to perform is the producer
clearing its own queue, not a person adjudicating it. The two qualifications the
previous record already carried point the same way: pruning and retirement are
manual file edits with no action in the tool — the source records what that
costs, *"A past round hand-retired 109 such dead rows out of this repo's own
committed acks file — a whole session of manual audit for a question the tool
could answer in one pass"* — and no CI job reads either sidecar. The review the
committed ledger makes possible is a review somebody still has to perform, and
nothing in the tool notices whether they did.

**Negative evaluation — awarded.** The notes case is the strongest shape this
mark takes: a note is written against a target that does not exist, the listing
is asserted to show it as dangling and to show a live target as not dangling, and
then its text is asserted absent from both a task-scoped retrieval and the
default map. Two populated emissions, one must-not, and the positive control in
the same script. The identity case adds the anti-blank-check assertion: a body
that was moved *and rewritten* must not be content-matched onto its old ack.

**Tombstone — withheld, and the near-miss is precise enough to be worth more
than the mark.** The ledger is durable, committed, consulted before the tool
reports again, and ratcheted so it cannot become a blanket exemption. Three
things decide against it. The lookup key is a location rather than the rejected
content. The row records a finding that was *accepted* — the code stays, the
warning goes — rather than a value that was refused. And the consultation happens
when a report is rendered, not when anything is written, so nothing stops the
same code being written again. What the mechanism does have is the distinction
the mark's definition is really about: `cid` is a hash of the symbol's body with whitespace collapsed and
its own name replaced, and it is used to re-file an ack across a rename and
deliberately refuses to match a rewritten body. The project states the rule in
one sentence — *"Identity that follows a rename must not become identity that
follows a rewrite"* — and defends it with a committed test. That is a considered answer to a
question about identity that this design had to face and most stores do not.

**Trust state — withheld.** The three stale reasons are computed and disclosed
and never consulted; a stale ack keeps suppressing. Notes carry no status field
at all, and the dangling flag is derived at listing time rather than stored,
filtering nothing — a dangling note is invisible because its key misses, not
because a state excludes it.

**Scope — withheld.** The `by` field is recorded and read in three places, all
of them building disclosure rows. The suppression test never consults it, so an
ack filed from one scope suppresses findings anywhere.

**Audit log — withheld.** Both stores are read-modify-rewrite rather than
append-only, and the reason chain is capped at one hop by an explicit decision
against a reason log. The record of what changed is git's, which the rubric
excludes by name.

**The measurement the project made against itself.** Rather than asserting that
its identity keys are durable, ripwire measured them across its own history and
published the result: across fifty-nine canonical ids, the same number of
path-qualified keys and four clone groups, not one survived a `git mv`. That
number is the argument for the content-hash rescue route, and it is in a comment
above the code that implements it. Reporting the survival rate of your own
identity scheme, in the negative, is the thing to copy here.

**One live memory that is wrong.** The notes store holds two rows. One, dated
23 August, says the README's single gate-count claim *"is NOT enforced"* by
`test/manifestcheck.sh` and names the fix: cover README.md in the
`gateCountClaims` arm. That fix landed — `gateCountSites` names
`docs/EVALS.md`, `README.md` and the deck, the count is generated by
`docs/gatecount_build.py` and gated twice over — so the note describes a gap
that is closed. Its target resolves, so `--notes` does not flag it dangling, and
no field in the format can mark it superseded. The store has no way to say that
one of its two memories has stopped being true, which is precisely the class of
failure the ack side built its stale classification to catch, and the contrast
is the sharper for sitting in the same repository.

**And the verb named for memory does not read it.** `src/mcp.h:62` advertises
`memory_recall` as returning *"most relevant memory notes / docs for a task, full
text"*. `src/recall.h` is a lexical search over markdown documents and contains
zero references to the notes store, its index or its namespace, against 179
occurrences of `doc`. An agent taking the tool list at face value would never
reach the field notes; they arrive only as riders on other verbs.

## 10. Tests, Evals, and Benchmarks

618 gate scripts are named by the loop in `test/regression.sh` and all 618
resolve to a file, alongside 206 C++ harnesses and per-language fixture corpora,
in a test tree of 1,599 files. The count is itself a build product:
`docs/gatecount_build.py` derives it from that loop and rewrites all eight
published sites, and `test/gatecountcheck.sh` gates the agreement — two
independent derivations of the same number, after a round where a deck published
a count its own instrument had never read.

`docs/EVALS.md` is 12,678 lines and opens with a provenance rule: every number
names the instrument that produced it, the corpus it ran on and the file that
pins it. The localization and retrieval benchmarks ship with locked datasets, an
instance file, label files and committed results, so those numbers are
re-derivable given a build; the head-to-head arms depend on external tools that
are not vendored, so those are attested by committed reports rather than
re-runnable here. Nothing was run for this review.

The section worth naming is the one listing what the project does *not* claim: a
benchmark evaluator that has never executed with every pilot record left null, a
design whose minimum detectable effect is stated so that *"a null result from
this design would not be evidence of no effect"*, a token-cost figure removed for
having no in-tree citation, and an improvement figure disavowed as belonging to a
rejected candidate's baseline. Publishing the claims you have withdrawn, with the
reasons, is the counterweight to a README this long.

**One README count is off by one against the project's own data.** The README
says seventeen of the folded papers are from 2026, and the gate that checks it
counts arXiv identifier stems beginning with 26. The repository's own dates file
warns against exactly that — the identifier stem does not track publication date,
and it records one paper whose stem is 2602 and whose date is December 2025. By
published date the figure is sixteen. The same gate uses dates, correctly, for
the two-month and thirty-day counts beside it.

## 11. For Your Own Build

### Steal

- **Ratchet an acceptance instead of suppressing it.** Recording the magnitude a
  finding was accepted at, and re-reporting it the moment it worsens, is the
  difference between a decision and an exemption — and it is one comparison.
- **Guard the degenerate case.** A finding with no magnitude makes the ratchet
  test trivially true and turns the whole record into a blank check; noticing
  that before shipping is the kind of thing that separates a mechanism from an
  intention.
- **Separate identity that follows a rename from identity that follows a
  rewrite.** A content hash that re-files a judgement when the code moved, and
  refuses when the code changed, is the exact distinction a durable judgement
  about code needs.
- **Measure your identity scheme's survival and publish the number.** A measured
  survival rate of none is a better argument for building a rescue route than any
  amount of reasoning about it.
- **Disclose what you suppressed.** A count in the report header means a reader
  can tell a clean run from a quiet one.
- **Root-qualify a sidecar's path.** A bare relative filename reads and writes
  the working directory's copy, and the observed failure was acking one
  repository and rewriting another's committed ledger.

### Avoid

- **Classifying staleness and never acting on it.** Three reasons are computed,
  emitted and ignored; the retirement they imply was done by hand, once, for 109
  rows.
- **Giving one store the protections and not the other.** The acks publish
  atomically under a lock and have two rescue routes; the notes truncate without
  a lock and have none, in a file whose header cites the ack precedent.
- **A memory that cannot be told it is wrong.** The single field note is stale
  and there is no status, no expiry and no supersession to record that.
- **Advertising a verb as memory recall when it reads a different store.**

### Fit

Right if you want a code-quality gate whose accepted debt is a reviewable
artifact rather than a suppression comment, and if the ratchet's discipline —
accept a number, not a warning — is what you want from it. The ack mechanism is
worth reading whatever you are building. Wrong as a general memory: retrieval is
exact-match on a path, there is no status, no validity and no scope, and the
notes half is two rows with none of the ack half's care.

## 12. Open Questions

- Will a stale ack ever be retired automatically? The classification exists, the
  reasons are named, and the source records what doing it by hand cost.
- Will the notes store get the ack side's identity healing? The same rename
  problem applies and the notes have no rescue at all.
- Should the ledger key on content rather than location? The content hash is
  computed already, and the argument against is that a rewritten body is a
  different finding — which is the same argument that makes the current key
  fragile under a move.
- Will `memory_recall` read `.ripwire_notes`? The name says it does.

## Appendix: File Index

| Path | Lines | What it holds |
| --- | --- | --- |
| `src/quality.h` | 7,142 | `pathQualifiedKey` (733), the scrubbed body and its hash (1379, 1446), the zero-magnitude guard (4592-4594), the ratchet contract (4838), the ack record and map key (4843-4862), the reader (5084-5092), the survival measurement and the repair argument (5300-5320), `AckRescueRoute` and `AckRemap` (5544-5556), `remapAckIdentity` (5576), `healIdentity` (5716-5754), `findSuppressingAck` and `applyAckRatchet` (5798-5810), `StaleAckWhy` (5859) |
| `src/verbs_quality.h` | 2,084 | Both ack reads (201, 262), the healing call sites (202, 263, 907), the ack write (860) |
| `src/notes.h` | 501 | The note record, the path, the reader and the writer; the dangling entry that *"stays dangling, which --notes already reports"* (365) |
| `src/serialize.h` | 8,192 | `renderNoteChildren` and the two lookup keys |
| `src/main.cpp` | 4,823 | The note write path and the `--notes` listing, with the prune rationale at 724 |
| `src/mcp.h`, `src/mcpverbs.h` | —, 5,126 | `kMcpVerbTable` with thirty-one verbs (mcp.h:58), the `memory_recall` description (mcp.h:65), and the healing call on the delta path (mcpverbs.h:3401) |
| `src/recall.h` | — | Lexical search over markdown documents; no reference to the notes store, its loader or its record type |
| `.ripwire_quality_acks` | 1,310 rows | The committed ledger; 925 rows carry a content id, 202 a scope |
| `.ripwire_notes` | 3 rows | The committed field notes |
| `test/identitycheck.sh` | 230 | The three claims that may not be traded for one another, on a synthetic git repository |
| `test/notescheck.sh` | 422 | The dangling-note exclusion with its positive control (150-170) |
| `docs/EVALS.md`, `docs/LINEAGE.md` | — | The evaluation record with its withdrawn-claims section, and the lineage table |
| `test/` | 1,599 files | 618 named gates, 206 C++ harnesses, fixture corpora |

**Searches recorded for the negative claims**

```sh
rg -niE 'valid_from|valid_to|validity time|transaction_time|as_of|bitemporal' src/   # 0; control: 17 hits for 'date' in notes.h
rg -niE 'append-only|audit_log|event log' src/                                       # 2, both prose declining the pattern
rg -nE 'confidence|trust|verified|status|revoked|retracted' src/notes.h              # 0; control: the five field declarations at 69-73
rg -n '\.by\b|->by\b|second\.by' src/                                                # 10, none in a suppression decision; control: 25 reads of ackNow
rg -c 'NoteIndex|ripwire_notes|notes::' src/recall.h                                 # 0; control: 179 hits for 'doc'
rg -niE 'cid|remap|alias|rename|heal' src/notes.h                                    # 7, none identity healing; the ack side has remapAckIdentity
rg -n 'acks.erase' src/quality.h                                                     # 2, both inside the re-key move, never a retirement
rg -n 'writeAckRecords|addNote\(' src/                                               # writes only from CLI paths; no MCP verb writes either store
```

## History

**2026-09-19** — re-pinned to [`e54b688e63c0041049b49a8bf63997f8cd299844`](https://github.com/redhat-et/ripwire/commit/e54b688e63c0041049b49a8bf63997f8cd299844), 449 commits and 300 files on from the previous pin. **`human_review` is withdrawn; `negative_eval` stands alone.** The ack ledger is unchanged in shape and is still described in sections 1, 5, 7 and 9, where it earns its space: a ratchet rather than a suppression, a rescue route kept per row, a file committed so a change in what is suppressed reads as a diff. What the mark needs is that the producer cannot clear its own queue, and here the project documents the opposite — `skills/ripwire-quality-bar/SKILL.md` spells the ack command out for the model three times (`:178`, `:188`, `:206`), and `ripwire-handoff` and `ripwire-orient` tell an agent to graduate a recurring comment into an ack reason. No MCP verb writes either sidecar and `quality_delta` is declared read-only, so this is a CLI act rather than a tool-surface verb; but a CLI act the shipped skill instructs the agent to perform is not a person's adjudication. The previous record's own two qualifications said as much. `negative_eval` re-verified: `test/notescheck.sh` still asserts a dangling note appears in the listing and in neither a task-scoped retrieval nor the default map, and `test/identitycheck.sh` still pins that an ack does not survive a rewrite. Screened again first: seventeen files, two auto-run surfaces, four unpinned surfaces, seven dependency files inside the cooldown. Nothing installed, built or run.

**2026-09-16** — [`f8e6087cc1dae2b438b3a69ccc8a4b53c19314cd`](https://github.com/redhat-et/ripwire/commit/f8e6087cc1dae2b438b3a69ccc8a4b53c19314cd) — re-read at a commit dated 16 September 2026, 979 commits past the previous pin, at version 0.6.1. The identity repair is the substantive change: rather than teaching nine call sites to try an alias, a `healIdentity` pre-pass rekeys the baseline snapshot and the ack ledger forward into the current tree's identity before anything reads them, through the git-recorded rename map and then scrubbed-content-hash equality, with the rescue route kept per row and `--quality-ack` writing the healed rows back. `identitycheck.sh` pins three claims that may not be traded for one another, including that an ack must not survive a rewrite. Both marks re-tested and held, with the negative-eval record re-grounded on that gate alongside the dangling-note case. The ledger has grown to 1,310 rows and the named gate list to 618. `memory_recall` still does not read the notes store: `src/recall.h` carries 96 case-insensitive matches for "note", every one of them prose or an unrelated identifier, and none naming the store, its loader or its record type. Screened before reading: two auto-run surfaces, four unpinned dependency surfaces, none inside the seven-day cooldown. Nothing was installed, built or run.

**2026-09-08** — [`8c20e10856d347206ccbd52fd1b83d90c5cbb5e3`](https://github.com/redhat-et/ripwire/commit/8c20e10856d347206ccbd52fd1b83d90c5cbb5e3) — first reading, at the head of `main`, on a commit from the same day. Screened before anything was read: two auto-run surfaces (an MCP manifest and a hooks directory), four unpinned surfaces, no build-time execution; nothing was installed or run, and the read was made from a full clone. The scope decision is recorded here because it shapes the report: the call graph and the lenses are a code index, which is a projection of source and cannot turn out to be false, so the subject is the two committed sidecars beside them — the ack ledger and the field notes — and the engine is context. Two marks. `human_review` rests on a ledger kept committed so that a change in what is suppressed appears in a diff, plus a listing built for pruning, with both qualifications stated: no action exists in the tool and no CI job reads either file. `negative_eval` rests on a dangling note asserted absent from two populated emissions with a control in the same script. `tombstone` was examined at length and withheld — the key is a location, the row records an accepted finding rather than a rejected value, and the consultation is on a read — with the near-miss written up because the content-hash rescue draws the rename-versus-rewrite distinction the mark's definition is about. `trust_state`, `scope_enforced`, `bitemporal` and `audit_log` were each examined and withheld on the read path rather than on the schema. Four claims were verified against the tree rather than repeated: the survival measurement, the off-by-one in the README's 2026 paper count against the project's own dates file, the staleness of the single committed note, and the MCP recall verb's failure to read the notes store.

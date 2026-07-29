# The field's own survey, read against the atlas

**Status:** comparison done, two systems reviewed and added, eight candidates open
**Origin:** *Memory in the Age of AI Agents: A Survey — Forms, Functions and
Dynamics*, [arXiv:2512.13564](https://arxiv.org/abs/2512.13564) (v2, 13 January
2026). 47 authors across twelve institutions, 107 pages, with a companion
reading list at
[Shichun-Liu/Agent-Memory-Paper-List](https://github.com/Shichun-Liu/Agent-Memory-Paper-List).

This is the most substantial artifact the field has produced about itself, and
it is the natural external check on the atlas's central claim. Read on
2026-07-29.

## Method, and its limits

Everything below comes from a text extraction of the PDF (pypdf, 107 pages,
~462 KB of text) plus reading the sections that bear on the atlas. **Word counts
are counts over that extraction, not over the typeset paper.** Figure labels do
survive extraction — Figure 9's branch names come through intact — but text set
inside vector graphics can be lost, so treat every zero below as "not found in
the extracted text" with the same force the atlas gives "not found in the
inspected code". The paper's own claims are reported as claims; nothing here was
run.

## What it is

A taxonomy paper, organised on three axes it argues are orthogonal:

| Axis | Question | Categories |
| --- | --- | --- |
| **Forms** (§3) | What carries memory? | token-level (flat 1D / planar 2D / hierarchical 3D), parametric (internal / external), latent |
| **Functions** (§4) | Why does an agent need it? | factual (user / environment), experiential (case / strategy / skill / hybrid), working (single-turn / multi-turn) |
| **Dynamics** (§5) | How does it operate and evolve? | formation, evolution (consolidate / update / forget), retrieval |

Plus §2.3, which spends nine pages separating agent memory from LLM memory, RAG,
and context engineering; §6, two consolidated tables of benchmarks and
frameworks; and §7, eight frontier essays.

**The §2.3 boundary and the atlas's boundary are close to the same line.** The
paper places pure context assembly outside agent memory because it lacks the
formation/evolution/retrieval lifecycle. The atlas excludes it because nothing
survives the session with a correctable identity. Different vocabulary, same cut
— and the atlas's [not in scope](../content/overview.md) section reaches it from
worked examples (BeeAI, MemAgent) rather than from a definition, which is the
more useful form for someone evaluating a framework whose README says "memory".

## The corpora barely overlap

Table 9 lists 25 rows, 24 distinct frameworks (ReMe appears twice). Matched
against the atlas's then-63 pinned repositories **by repository URL** (the count
is now 65 — see "The candidates, reviewed" below):

- **8 exact matches**: mem0, MemoryOS, MemOS, LangMem, Supermemory, Cognee,
  memU, Hindsight.
- **2 more by project identity**: `cpacker/MemGPT` is Letta under its former
  name; `getzep/zep` is the product whose engine the atlas reviews as Graphiti.
- **14 absent from the atlas**, of which three (Pinecone, Chroma, Weaviate) are
  vector databases the atlas's inclusion test excludes as infrastructure — and
  the paper says as much itself, noting that such entries "leave agent behavior
  and evaluation protocols to the application". Eleven are real candidates:
  Memobase, MIRIX, Memary, Second Me, MemEngine, Memori, ReMe, MineContext,
  Acontext, PowerMem, and `elizaOS/agentmemory`.
- **53 of the atlas's 63 systems appeared nowhere in the paper**, including all
  three tombstone holders.

**One trap worth recording.** The paper's `AgentMemory` is
`elizaOS/agentmemory`; the atlas's [agentmemory](../content/systems/agentmemory.md)
report is `rohitg00/agentmemory`. Different projects, identical name. Anyone
reconciling the two lists by name rather than by URL will merge them.

The shape of the divergence is not an accident. The paper selects on
*publication* — a framework earns a row largely by having a paper behind it,
though the Evaluation column is empty for sixteen of the twenty-four, so it is
not selecting on measured results either. The atlas selects on *inspectable
code*, opportunistically. Neither
is a sample of a population. What matters is that the two selection rules
disagree so completely that a reader using either alone would conclude the other
half of the field does not exist.

## What it confirms

**The forgetting-benchmark gap, against the field's own consolidated table.**
The [benchmarks page](../content/benchmarks.md) claimed no benchmark tests
whether a deleted memory stays deleted, scoped to what this atlas had read.
Table 8 is 40 benchmarks — 26 memory/lifelong/self-evolving, 14 related — and
the claim survives it. The nearest entries are MemoryBank ("user memory
updating"), LongMemEval, and HaluMem ("memory hallucinations"). Nothing tests
deletion durability. That upgrades the claim from "not in this atlas" to "not in
the field's own list either", which is the version worth publishing.

**Correction stops at soft deletion.** §5.2.2 traces external memory update as a
progression: destructive replace/delete (MemGPT, D-SMART, Mem0ᵍ) → Zep's
invalid-timestamp annotation instead of deletion → dual-phase online/offline
consolidation (MOOM, LightMem) → RL-learned update policies (Mem-α). Every step
makes the *decision* better. None of them records the rejected value, and the
failure the atlas keeps finding — the next extraction pass re-asserting what was
just corrected — is not named anywhere in the section. The counts:

| Term | Occurrences in 107 pages |
| --- | --- |
| `memory` | 1570 |
| `forget*` | 52 |
| `conflict` | 28 |
| `privacy` | 10 |
| `audit*` | 5 |
| `access control` | 4 |
| `contradiction` | 3 |
| `provenance` | 3 |
| `deletion` | 2 |
| `bi-temporal` | 1 |
| `tombstone` | **0** |
| `rejected` | **0** |
| `negative` | **0** |
| `tenant` | **0** |
| `unlearn*` | **0** |

`negative` at zero is the one to sit with. It is an ordinary English word, and a
107-page technical survey uses it never — which means no negative retrieval
assertion, no negative example, no negative result, under that name.

**§5.2.3 makes the atlas's point about forgetting explicitly.** The paper's three
forgetting mechanisms are time-based, frequency-based, and importance-driven —
all three are *capacity management*. Forgetting is defined there as removing
"outdated, redundant, or low-value information to free capacity". Deletion
because a person asked, or because a value was wrong, is not one of the
categories. The section's closing sentence is the tell: "when storage cost is not
a critical constraint, many memory systems avoid directly deleting certain
memories." Forgetting is treated throughout as an efficiency knob, which is
exactly the framing under which "does it stay deleted?" never becomes a question.

**§7.7 asks for the property without naming the mechanism.** The trustworthy-memory
frontier calls for "access control, verifiable forgetting, and auditable
updates", and for memory that is "version-controlled, auditable, and jointly
managed by agent and user". Those are, near enough, four of the atlas's seven
capability columns stated as open research directions. The paper wants the
property; the atlas has the count of who implements it.

That combination is the strongest form the atlas's central finding has taken so
far. It is no longer "a survey did not list three obscure systems" — it is that
the field's most comprehensive self-description does not contain the *concept*,
while its own frontiers section asks for what the concept provides.

## What it has that the atlas does not

Stated plainly, because the atlas has no coverage of any of it:

- **Parametric and latent memory (§3.2, §3.3).** Model editing (ROME, MEMORYLLM,
  M+), KV-state reuse, memory internalised into weights. The atlas's inclusion
  test — survives the session with a correctable identity — arguably admits
  these and the atlas has simply never gone looking. Weight-space memory has no
  row, no tombstone, and no scope key, which makes it either a hard case for the
  seven capabilities or evidence they are token-store-specific. Unresolved.
- **RL-learned memory management (§7.3).** Mem-α learns *whether* to update.
  MemEvolve evolves the memory architecture itself. The atlas's closest neighbour
  is the MemAgent exclusion, and its "promotion gates for the policy" pattern
  assumes the policy is written down.
- **Multimodal memory (§7.4)** and the multimodal column in both tables.
- **A literature backbone.** Several hundred citations against the atlas's
  pinned commits. The two are complementary in the obvious way, and the
  [symbolic prior art note](2026-07-28-symbolic-prior-art.md) is still the
  unpaid debt on this side — note that this survey does not pay it either:
  belief revision and truth maintenance appear nowhere in it.

## Changes made

1. **[overview.md](../content/overview.md), §Correction.** The "gap is visible
   from outside this atlas too" paragraph rested on TeleAI's Awesome-Agent-Memory
   list. Kept, and added this survey with the term counts and the §5.2.2
   progression. An awesome-list omitting three obscure repositories is weak
   evidence; a 47-author survey whose vocabulary lacks the concept is not.
2. **[benchmarks.md](../content/benchmarks.md), §2 and §6.** Added Table 8 to
   the named-outside-these-repositories list under the standard not-inspected
   caveat, and re-scoped the forgetting claim against 40 benchmarks instead of
   against this atlas alone.
3. **[patterns/index.md](../content/patterns/index.md), the establishment
   disclosure.** One sentence, because that paragraph is where a reader decides
   how much weight the advocacy patterns carry.

Those three were made from the survey alone, so nothing in them touched a
capability mark or a count — the atlas's marks come from code read at a pinned
commit, and a paper is not that. The counts *did* move afterwards, from the two
reviews below, which is the right order.

Two stale counts were also found and fixed while editing adjacent text:
`benchmarks.md` still said only Verel and RainBox carry a tombstone (commit
`1e65fd4` updated that from two to three everywhere else), and the
[rubric](../content/methodology/atlas-rubric.md) still said one repository makes a
negative retrieval assertion when the grid had said two since open-cowork was
added.

## The candidates, reviewed

Three of the eleven were checked out and read on 2026-07-29. Two became reports;
one did not, and the one that did not is the most interesting result.

### MemEngine — excluded, and it should not have been a candidate

`nuster1128/MemEngine` has **no persistence layer at all**. `LinearStorage` is a
Python list, `reset()` empties it, `BaseMemory` declares no save or load, and
`server_start.py` holds sessions in `service_database = {}` — an in-process dict
that dies with the process. Nothing writes to disk but a `Display` helper. It also
has no licence file, which would have excluded it independently.

It is a legitimate research library — a common harness for comparing ten published
memory algorithms — and it is honest about that. But it is in Table 9 as a
representative *open-source memory framework*, and a reader taking that table as a
shortlist would evaluate it alongside Mem0 and Zep. The atlas's inclusion test
catches this in one query, which is a small argument that the test is doing real
work. Recorded in the
[scope section](../content/overview.md) as a third exclusion shape: an algorithm
workbench is not a memory system.

### MIRIX — added, and it changed a count

[Report](../content/systems/mirix.md), pinned at `51f3342d`. Six typed memory
tables, each with a manager, a writer agent and a prompt; Postgres/pgvector or
SQLite, plus Redis Stack as a *searchable* cache. Letta's ORM lineage with a much
stronger tenancy model.

**It carries `negative_eval`, taking that column from 2 to 3.** This was not
expected and the judgement is worth recording, because the atlas has been caught
twice on semantic misclassification. `tests/test_filter_tags_db.py:300` creates a
memory under scope `test-ft`, searches under `scopes=["other-scope"]`, and asserts
`mem.id not in result_ids`; `test_search_all_users.py:405` asserts that user3
(different scope) and user4 (different org) are absent from a cross-user search.
Against the rubric — "committed evaluation cases assert that particular material
must **not** be retrieved", *not* "ordinary recall tests" — that is the shape, and
withholding it would have been strictness for its own sake.

The line was drawn against Memobase in the same session, which is what makes it
defensible: Memobase's `test_controller.py:347` asserts that filtering by a
non-existent tag returns nothing, and that is *not* the same claim — no material is
being excluded, the filter simply has no matches. One tests that a filter does not
over-return; the other tests that named material stays out. Both reports state the
distinction explicitly so a future reader can check the call.

The route matters more than the count. open-cowork got there through a relevance
harness and Verel through a red team; MIRIX got there through **multi-tenant
access-control testing**, a discipline with no connection to memory research. The
atlas's argument has been that this assertion shape is almost never reached; the
useful amendment is that it is reachable from ordinary engineering practice, and
that the systems reaching it that way assert it about *boundaries* rather than
about corrected values — which is still the hard case nobody tests.

MIRIX is also the atlas's best instance of the failure the benchmarks page names.
Its `auto_dream` pass loads up to 500 items per memory type with an explicit
`start_date=None, end_date=None`, and its prompt says "If uncertain, keep both and
record the discrepancy" — the same rule as Memanto's `keep_both`, except Memanto's
is an enum a validator enforces and MIRIX's is a sentence, and the tool it governs
hard-deletes.

### Memobase — added, one mark

[Report](../content/systems/memobase.md), pinned at `358c16bb`. A user-profile
service: a memo of at most five sentences per `(topic, subtopic)`, at most fifteen
subtopics per topic, assembled into a token-budgeted context block.

Two things are worth carrying into the pattern library, and both are now there.
First, **scope in the primary key** — `PrimaryKeyConstraint("id", "project_id")`
with composite foreign keys throughout, which makes a cross-tenant query a schema
error rather than a review failure, and is the strongest form of that pattern in
the atlas. Second, **evidence before belief, deliberately inverted**:
`persistent_chat_blobs` defaults to `False`, so the transcript is hard-deleted
after the profile is written. That is a defensible privacy posture *and* the reason
a bad extraction is permanent, and Memobase is the clearest place to see that the
two goals genuinely conflict.

Memobase also gives the atlas a committed number for something it says nobody
measures: `buffer_flush_interval` defaults to `60 * 60`. A fact stated now may not
be recallable for an hour.

## What the exercise settled

The blind-spot hypothesis was **partly confirmed, and not in the direction
expected**. The worry was that the atlas's opportunistic selection had missed a
cluster of published memory frameworks that would look different from the corpus.
Two of three landed exactly where the atlas predicts — scope enforced, nothing else
— which is the null result. But MIRIX carried a mark that three systems in
sixty-five carry, and the atlas would not have found it, because nothing about
MIRIX's documentation suggests it. It was found by reading the test directory.

That is the same lesson as the Verel tombstone, which the
[tombstone page](../content/patterns/rejected-value-tombstone.md) records: the
README did not mention the mechanism. Twice now the atlas's rarest findings have
come from reading code that no summary would have pointed at. It is the argument
for the whole method, and it has one uncomfortable corollary — the atlas's own
counts are lower bounds, and the eight unreviewed candidates below may hold more.

## Still open

**Eight candidates remain unreviewed**: Memary, Second Me, Memori, ReMe,
MineContext, Acontext, PowerMem, and `elizaOS/agentmemory`. The case for continuing
is now stronger than it was before this session, because the hit rate was not zero.
The case against is unchanged: 22 stale pins in the
[editorial backlog](2026-07-28-editorial-backlog.md) §3, and breadth added while
depth rots is the wrong trade. My read is that this can wait behind the
re-analysis work, with `elizaOS/agentmemory` first when it resumes — partly on
merit and partly because the name collision with the atlas's existing
`rohitg00/agentmemory` report will confuse somebody eventually.

**The freshness numbers could not be re-measured.** `check_freshness.py` against 65
pins exceeds GitHub's anonymous rate limit; the run during this session returned
46 unresolved. The "30 of 62" figure in the comparative report has been re-dated to
its 2026-07-28 run rather than silently updated, since inventing a current number
was the alternative.

**Parametric and latent memory remain absent from the atlas**, and this survey is
the strongest argument yet that the omission is a choice the atlas has never
actually made. Weight-space memory has no row, no scope key and no tombstone, so it
either breaks the seven capabilities or reveals them as token-store-specific. That
question is bigger than a report and is not resolved here.

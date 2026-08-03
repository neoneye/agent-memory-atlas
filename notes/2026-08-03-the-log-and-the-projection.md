# The log and the projection: a lineage the corpus already implements

**Status:** triaged — the gap is real but not the one that was claimed; one
correction to a note published earlier today
**Origin:** item A of the Gemini review triaged in
[the layer below delete](2026-08-03-the-layer-below-delete.md), which argued the
atlas should map its patterns onto distributed-systems theory — event sourcing,
CQRS, Cassandra tombstones.

That triage answered the tombstone third of the argument (the
[pattern page](../content/patterns/rejected-value-tombstone.md) already carries
the three-way table, and the key is what differs) and left event sourcing and
CQRS open with a claim attached: *"Neither term appears anywhere in
`content/`."*

**That claim is half wrong, and the half that is wrong is the interesting half.**

## The correction

`CQRS` appears zero times in `content/`. That much held.

`event sourcing` appears **twice**, in two system reports:

- [memledger](../content/systems/memledger.md) — "It is event-sourced: memories
  are a projection over an append-only ledger", with
  `src/memledger/projection.py` named and the background column reading
  "Projection is applied per event and can be rebuilt from the ledger".
- [simplemem](../content/systems/simplemem.md) — one passing use.

Both appear because the *project* uses the term about itself. The atlas has
never once reached for it as an analytical category, which is the actual finding
and is worse than the absence would have been.

## What the corpus is doing while the atlas declines to name it

Twenty reports describe an architecture in the atlas's own vocabulary —
*canonical store*, *source of truth*, *live authority*, *projection*,
*rebuildable* — and the architecture they describe is event sourcing with a read
model:

| Report | How the report puts it |
| --- | --- |
| [core-memory](../content/systems/core-memory.md) | "Session JSONL as live authority, rebuildable index projection" |
| [gitlord](../content/systems/gitlord.md) | "the retrieval index built as a projection the code can rebuild from the log" |
| [everos](../content/systems/everos.md) | "Markdown is the truth; everything else is a projection" |
| [claude-mem](../content/systems/claude-mem.md) | "Canonical SQLite, optional Chroma projection and cloud sync" |
| [daimon](../content/systems/daimon.md) | checkpoints are the truth; the FTS5 index is disposable and rebuilt |

Plus fifteen more carrying the same three words. Nobody coordinated this. The
systems converged on the shape because it is what you build when a model writes
into your store and you need to be able to throw away what it derived without
throwing away what it derived it *from* — which is also, in different words, the
atlas's own [evidence before belief](../content/patterns/evidence-before-belief.md).

So the honest position is not "the atlas is missing a lineage." It is: **the
atlas independently rediscovered event sourcing, described it accurately twenty
times, and only ever writes the name down when a README hands it over.**

## Why naming it is worth something, and where it stops

The case for the translation is not tidiness. It is that the established
literature has failure modes with names, and three of them are load-bearing here:

- **Deletion in an append-only log is a known hard problem with known answers.**
  You cannot delete from the log; you append a tombstone event that replay must
  honour, or you crypto-shred the payload and leave the envelope. That is exactly
  the atlas's central finding arriving from the other direction — and the atlas
  has already worked one of the two answers out from scratch, in
  [what survives encryption](2026-07-29-what-survives-encryption.md), without
  connecting it to the literature where it is standard.
- **Replay must be deterministic, and LLM-derived projections are not.** This is
  the sharpest thing the translation buys, because it is a property the corpus
  mostly does not have. If your projection is rebuilt by re-running extraction
  over the log, "rebuildable" is a much weaker promise than it sounds: you get *a*
  projection, not *the* projection. [Daimon](../content/systems/daimon.md)'s index
  is rebuildable in the strong sense — FTS5 over stored text, no model in the
  path. A system that re-extracts is rebuildable in the weak one. **The atlas
  does not currently distinguish these and uses one word for both.**
- **Schema evolution of old events.** A log outlives the code that reads it. No
  report in this corpus has been examined for what happens when a two-month-old
  event meets a changed extraction schema.

Where it stops: CQRS proper is about splitting the *command* model from the
*query* model for reasons of scale and contention, and nothing in this corpus has
that problem. Importing the term would be vocabulary borrowing rather than
translation, which is the failure mode the
[declined proposals](2026-07-28-declined-proposals.md) note calls inventing
columns to fill out a matrix.

## What follows

- **Corrected** in [the layer below delete](2026-08-03-the-layer-below-delete.md):
  the "neither term appears" claim, which was true only of CQRS.
- **One real distinction the atlas is not making**, and it is checkable across
  the twenty reports without re-reading any of them at the source: is the
  projection rebuilt *deterministically* from stored text, or re-derived by
  running a model over the log again? The two are one word apart in the reports
  and a different guarantee in practice. That is the work this note would
  become, and it is not done.
- **Not adopted:** CQRS as a category, for the reason above.
- **Not adopted:** an "event sourcing" pattern page. The shape is already
  covered from two directions —
  [evidence before belief](../content/patterns/evidence-before-belief.md) for
  keeping the raw event, and
  [append-only memory audit](../content/patterns/append-only-memory-audit.md) for
  the log — and a third page would be a second name for material that already has
  one, which is why the
  [antipatterns page](2026-07-28-declined-proposals.md) was declined.

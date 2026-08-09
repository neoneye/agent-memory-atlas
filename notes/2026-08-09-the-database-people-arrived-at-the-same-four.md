# The database people arrived at the same four

**Status:** one paper analysed and integrated; one repository queued for
screening.
**Subject:** *Is Agent Memory a Database? Rethinking Data Foundations for
Long-Term AI Agent Memory* — Abdelghny Orogat and Essam Mansour,
[arXiv:2605.26252](https://arxiv.org/abs/2605.26252), 25 May 2026, cs.AI.

## Why it matters here

This is a vision paper from a data-management group, and it derives this atlas's
central argument from the other side of the field. Its opening claim is that
current systems "treat memory as storage" and "localize correctness at records,
embeddings, or edges", and that the consequence is four recurring failure modes:

1. **unregulated growth** — append-only ingestion accumulating redundant entries
   that compete at retrieval;
2. **missing semantic revision** — updates that append instead of integrating,
   leaving contradictory values live;
3. **capacity-driven forgetting** — eviction by age or size rather than by
   importance;
4. **read-only retrieval** — access that cannot reinforce or protect what is
   used.

Those are the four this atlas keeps reporting, reached by people who did not read
these pages. Two independent derivations is better evidence than one.

## What it formalises

**Governed Evolving Memory (GEM).** Correctness is "a property of the state
trajectory, not of individual records". Four state-level operators replace
record-level CRUD — **ingestion** (integrate new input while retaining prior
values as evidence), **revision** (reconcile overlapping units, propagate along
typed edges, preserve superseded values with provenance), **forgetting** (graded
attenuation — compress, hide, archive — driven by relevance), and **retrieval**
(which *induces a state transition* updating salience).

Six correctness conditions govern the trajectory. Paraphrased: C1 responses
reflect the most recent non-archived values; **C2 no superseded value becomes
current**; C3 an update re-evaluates dependents along typed edges; **C4
forgetting and revision preserve provenance chains**; C5 the active state stays
within policy bounds while archived content stays recoverable; C6 every retrieval
updates salience and strictly reduces attenuation eligibility.

**C2 is the rejected-value tombstone stated as a property rather than as a
table**, and C4 is [evidence before belief](../content/patterns/evidence-before-belief.md)
and the [append-only memory audit](../content/patterns/append-only-memory-audit.md)
at once. C3 is the derived-copy problem the comparative report's lifecycle
section draws.

Three structural observations follow, and the first two are the useful ones:
pure-function retrieval cannot satisfy C6, because the state change has to be
inside the operator rather than bolted beside it; C5 and C6 are jointly
unenforceable above a CRUD engine; and **append-only storage cannot satisfy C2**,
with untyped propagation unable to satisfy C3. That last pair is an impossibility
argument for something this atlas has only ever shown empirically — that
supersession chains are structurally insufficient however carefully they are
kept, because the new write is a different record saying the same wrong thing.

## What it costs the atlas to admit

The tombstone page's disclaimer said there is "no consensus behind this page, no
library that provides the mechanism, and **no shared vocabulary for it**". The
third clause is now wrong. There is a vocabulary — C2, in a paper that proves the
append-only alternative cannot meet it. The disclaimer has been narrowed
accordingly, and the patterns index now carries the paper beside the 107-page
survey that contained none of these words eight months earlier.

What has *not* changed: a vision paper with a prototype is not a shipped library
and not adoption. The page remains advocacy and keeps its stance pill.

## MemState — a screening candidate, not yet read

The paper realises GEM in **MemState**, on the embedded property-graph engine
Kuzu, with self-contained topics carrying field histories, typed edges split into
extension versus association, declarative `⟨event, condition, action⟩` policies,
and atomic commits that check policy postconditions. Code is stated as released
at **https://github.com/CoDS-GCS/MemState** — note that the arXiv abstract page
does not mention it; the link is in the body.

That is a report candidate and an unusually interesting one, because it is the
only artifact in view built *from* the correctness conditions rather than
retrofitted to them. It has not been screened or read. The two questions to ask
of it are the ones this atlas asks of every system that publishes a design: does
the implementation carry all six conditions or a subset, and is there a committed
test asserting C2 — that a superseded value does not come back — as opposed to a
proof that it cannot.

The paper's own third research direction asks for "trajectory-level benchmarks
measuring C1–C6", which is the same hole the [benchmarks
page](../content/benchmarks.md) argues sits under every published memory score.

# Narrative representations, triaged for memory

**Status:** a gap, noticed rather than researched. One secondary survey read,
no primary paper.
**Origin:** "narrative graph" kept appearing as an AI-memory framing. Nothing
in the corpus uses the phrase, and the atlas neither borrows this vocabulary
nor says why not — the same omission [symbolic prior art](2026-07-28-symbolic-prior-art.md)
records for belief revision and truth maintenance.

This is a register rather than an essay: one entry per way of structuring
narrative or event data, each triaged for whether it suits agent memory. Add a
row when a new one turns up.

## How to read it

The entries are not siblings, and the two axes that separate them decide most
of the verdicts.

**Instance or type.** Does a node stand for *this* thing that happened, or for
a kind of thing that happens? Memory needs instances. A type-level graph is a
schema, and a schema is not a memory.

**Per-episode or per-corpus.** Is the structure built from one session, or
mined across thousands? A corpus-level structure needs a corpus. At one user
and one assistant, it will not have one for a long time — which rules out
several of these on volume alone, not on merit.

A third consideration, cutting across both: **extraction cost**. Every entry
here assumes something turns prose into structure. For a personal assistant
that cost is paid per session, by a model, forever.

## The register

### Narrative graph (umbrella)

The family term, not a member. Entities, events, relations, tropes and
structural features encoded as a graph. Everything below is one of these.

The unifying commitment, and the useful thing to take away: **the story lives
in the edges**. A coherence weight, a causal link, an attitude node. Not text
attached to a node — which is what nearly every memory system in this corpus
means when it writes `narrative` into a field.

*Superset of everything below.*
**Verdict: n/a** — too general to adopt or reject.

### Event evolutionary graph (script / eventuality graph)

Nodes are events reduced to predicate–role tuples; edges are temporal and
causal transitions *observed across a large corpus*, weighted by frequency.
Built for script event prediction: what usually happens next.

*Instance-level nodes, corpus-level edges. Subset of the umbrella; narrative
maps are a near relative with different edge semantics.*

**Verdict: wrong for a personal assistant, right for an organizational one.**
The edges are a statistic. One developer does not generate enough episodes for
"what usually follows what" to mean anything, and the failure mode is
confident nonsense learned from five samples. A team memory over thousands of
sessions is a different calculation.

### Actor–event–perspectivization graph

Actor nodes, event nodes, and — the distinctive part — **perspectivization
nodes**: events representing attitudes. Wants, hopes, needs. Edges run from
events to actors by semantic role, and between events by attitude dependency.
Built for political discourse analysis, extracted via AMR parsing.

*Superset of a plain event graph: adds actors and attitudes on top.*

**Verdict: the idea yes, the machinery no.** Modelling stance as first-class
is exactly what a personal assistant is missing — "prefers", "rejected",
"is wary of" are not facts about the world, they are facts about the user, and
storing them as ordinary facts loses that distinction. But AMR parsing plus
coreference to build it is heavy. Take the attitude node as a typed memory
kind; skip the pipeline.

### Coherence graph (retrospective questions)

Edges between text snippets, weighted by how many retrospective "why did that
happen" questions are answerable across them. An LLM generates the questions;
answerability is the filter; the count is the weight.

*Instance-level, per-document. Orthogonal to the event graphs — it weights
links between chunks without committing to a relation type.*

**Verdict: elegant, and too expensive here.** Getting a coherence signal
without naming the relation is a genuinely clever dodge. But the cost is
model calls over snippet *pairs*, which is quadratic in the thing you least
want to be quadratic in. Revisit if a cheap local model makes per-pair
scoring free.

### STAC (situation, task, action, consequence)

Not a graph so much as a **typed clause schema**. Each vertex is an
agent-centred clause labelled one of four ways; edges are causal, built by an
iterative propose-prune-validate pass.

*Instance-level, per-episode. The narrowest thing here, and the only one whose
shape matches what an agent actually does.*

**Verdict: right, and the one to steal.** Four fields on an episode. It costs
one classification per clause and it answers the question the corpus shows
agent memory failing at — not "what is true now" but "what did we try, and
what happened". [funes](../content/systems/funes.md) argues for exactly this
without the vocabulary, quoting its own rationale document: *"A log also keeps
what a knowledge base throws away — the superseded passage is often the answer
itself: what did we try before, and why did we move off it?"*

### Narrative map

A weighted DAG over events where edge weight encodes coherence from lexical
and topic similarity. Built for *visualizing* how a story develops through a
document set.

*Close to an event evolutionary graph, but per-document and acyclic by
construction.*

**Verdict: wrong for storage, right for review.** This is a reading surface.
Worth remembering if the assistant ever needs to show a person how a decision
was reached, which is a different feature from remembering it.

### Trope graph

Nodes are tropes — hero, villain, conflict, plot device. Edges are causal,
derivative, conflict, entailment. Grown by graph grammars and evolutionary
search for game narrative generation.

*Type-level. The only entry here whose nodes are not instances.*

**Verdict: wrong, and instructive about why.** A trope graph holds no
episodes; it constrains what *may* be generated. That is a schema with
fitness functions, and it fails the atlas's bar at the first clause — nothing
survives a session because nothing about a session was ever in it.

### Multimodal hierarchical graph

Three levels — macro (arcs), mid (segments), panel (objects, captions,
dialogue) — with cross-level edges. Built for comics and visual narrative.

*Orthogonal to everything above: a layering that could wrap any of them.*

**Verdict: the layering transfers, the multimodality does not.** Macro / mid /
detail with explicit cross-level links is a summarization hierarchy where the
summary still points at what it summarizes — which is the thing several
systems in this corpus get wrong by letting a summary outlive its evidence.

## Adding an entry

Name it, say what the nodes and edges are, place it on the two axes, then give
a verdict with a reason that is not a restatement of the axes. If the verdict
is "wrong for memory", say which clause of the scope bar it fails — survives
the session, retrievable later, scopeable, correctable, forgettable — because
"wrong" without that is an opinion.

## What has not been done

No primary paper read; this rests on one secondary survey page, and the class
names and their groupings come from it rather than from the literature. The
claim that this corpus keeps `narrative` as node text and not as edge
structure is a grep, not a measurement. Neither is load-bearing for the STAC
recommendation, which stands on funes's argument and on the shape of the
corpus's correction machinery.

# Narrative graphs, triaged for memory

**Status:** a gap, noticed and then checked. The class list comes from one
auto-generated survey page; each class was then checked against its primary
paper on 2026-09-21, to the depth of the paper's definitions section, not a
full read. Three of the survey's descriptions did not match the paper they
cite, and the first draft of this note carried two more errors of its own.
Each correction is marked in its row.
**Origin:** "narrative graph" kept appearing as an AI-memory framing. Nothing
in `content/` uses the phrase, and the atlas neither borrows this vocabulary
nor says why not — the same omission [symbolic prior art](2026-07-28-symbolic-prior-art.md)
records for belief revision and truth maintenance.

This is a register rather than an essay: one entry per way of structuring
narrative or event data as a graph, each triaged for whether it suits agent
memory. Add a row when a new one turns up.

**Where the list comes from.** The grouping is [Emergent Mind's topic page on
narrative graphs](https://www.emergentmind.com/topics/narrative-graphs), which
carries no author and reads as machine-written. It is a finding aid, not a
source: its edge types for the trope graph, its levels for the comics graph,
and its "attitude" gloss on perspectivization are all paraphrases the papers
do not support. Every row below cites the paper and states what the paper
says its nodes and edges are.

## How to read it

The entries are not siblings, and the two axes that separate them decide most
of the verdicts.

**Instance or type.** Does a node stand for *this* thing that happened, or for
a kind of thing that happens? Memory needs instances. A type-level graph is a
schema, and a schema is not a memory. Two entries here are type-level — the
event evolutionary graph and the trope graph — and both fail the scope bar at
the same clause for the same reason.

**Per-episode or per-corpus.** Is the structure built from one session, or
mined across thousands of documents? A corpus-level structure needs a corpus.
At one user and one assistant, it will not have one for a long time — which
rules out several of these on volume alone, not on merit.

A third consideration, cutting across both: **extraction cost**. Every entry
here assumes something turns prose into structure, and the papers pay that
cost very differently — one by hand, one with a fine-tuned classifier, several
with a frontier model per pair of passages. For a personal assistant the cost
is paid per session, by a model, forever.

## The register

### Narrative graph (umbrella)

The family term, not a member. The survey page's definition: *"a family of
computational representations that encode entities, events, relationships,
tropes, and structural features of stories in graph form."* No paper owns the
phrase; the trope paper and the political-discourse paper below each call
their own structure a "narrative graph" and mean different things by it.

The unifying commitment, and the useful thing to take away: **the story lives
in the edges**. A coherence weight, a causal link, a want with an actor. Not
text attached to a node.

That distinction is checkable against the corpus. 39 of the reports use the
word `narrative`; in every one read for this note it names a text field on a
node — [moltbrain](../content/systems/moltbrain.md)'s `narrative` column
beside `facts[]`, [byterover](../content/systems/byterover.md)'s five
narrative fields, [agent-working-memory](../content/systems/agent-working-memory.md)'s
`narratives` kept outside the injected context,
[claude-self-reflect](../content/systems/claude-self-reflect.md)'s
model-written narrative layers. The edge form does exist in the corpus without
the vocabulary: [hindsight](../content/systems/hindsight.md) and
[memomind](../content/systems/memomind.md) both keep causal links between
memories in a link graph, and MemoMind boosts them at recall. So the corpus
holds some of this already; what it lacks is the name and the comparison.

*Superset of everything below.*
**Verdict: n/a** — too general to adopt or reject.

### Event evolutionary graph (script graph; eventuality graph)

**Source:** Li, Ding and Liu, *Constructing Narrative Event Evolutionary
Graph for Script Event Prediction*, IJCAI 2018,
[arXiv:1805.05081](https://arxiv.org/abs/1805.05081). Near relative:
ASER, Zhang et al., WWW 2020, [arXiv:1905.00270](https://arxiv.org/abs/1905.00270),
whose nodes are eventualities and whose edges are Penn Discourse Treebank
relations (*Precedence*, *Reason*, *Result*), 194 million eventualities and
64 million edges from 11 billion tokens.

**What the paper says.** A node is an abstract event: a predicate verb and
its grammatical relation to the chain's protagonist, `(eats, subj)`. One node
per event *type*, not per mention — 104,940 nodes over the New York Times
portion of Gigaword. An edge is a predicate–GR bigram seen in the extracted
chains, directed, weighted by conditional probability
`count(vi, vj) / Σk count(vi, vk)`; 6,187,046 of them. Built as a knowledge
base of "event evolutionary principles" for predicting the next event in a
chain.

*Correction to the first draft, which placed this as instance-level nodes over
corpus-level edges. It is type-level on both counts.*

*Type-level, per-corpus. Subset of the umbrella; narrative maps are a near
relative with instance nodes and different edge semantics.*

**Verdict: wrong for storage anywhere; possibly right as a prior for an
organizational assistant.** A node like `(eats, subj)` has no episode in it,
so the graph fails the scope bar at the first clause — nothing about a
session survives, only a statistic learned from sessions. As a prior over
"what usually follows what" it needs volume: one developer does not generate
enough episodes, and the failure mode is confident nonsense learned from five
samples. A team memory over thousands of sessions is a different calculation,
and even there it sits beside the memory, not in it.

### Actor–event–perspectivization graph

**Source:** Pournaki and Willaert, *Extracting narrative signals from public
discourse: a network-based approach*,
[arXiv:2411.00702](https://arxiv.org/abs/2411.00702); *Humanities and Social
Sciences Communications*, 2025.

**What the paper says.** Each sentence is parsed to Abstract Meaning
Representation with IBM's transition-based parser. Predicates become event
nodes; their argument fillers become actor nodes; edges from event to actor
carry PropBank roles (ARG0 agent, ARG1 patient, ...), and an event that is
itself an argument of another event gets a hierarchical edge to it.
"Perspectivization" is narrower than the word suggests: it is the
operationalization of *goal expressions* — events under two VerbAtlas frames,
`require_need_want_hope` and `oblige_force` ("we need to", "we must"), with an
actor in ARG0 — and the events those goal-events embed. The output is a
narrative trace table from which actor networks are drawn. Corpus: the State
of the European Union addresses, 2010–2023.

*Correction to the survey page, which glosses the perspectivization nodes as
attitudes generally. The paper detects wants, needs, hopes and obligations,
and nothing else.*

*Instance-level, per-document. Superset of a plain event graph: adds actors
and goal-holding on top.*

**Verdict: the idea yes, the machinery no.** The paper's move is that a want
or a must is an *event with an actor*, not a property of the world. That is
exactly the distinction a personal assistant loses when it stores "prefers
X" or "rejected Y" as ordinary facts: those are facts about the user, with the
user as ARG0, and a store that cannot say who holds them cannot scope or
correct them properly. The corpus's [rejected-value tombstone](../content/patterns/rejected-value-tombstone.md)
is a special case — a rejected value is a stance with a holder. Take the typed
node with an explicit holder; skip the AMR pipeline, which is built for
speeches and heavy for a session log.

### Coherence graph (retrospective questions)

**Source:** Xu, Li, Yu and Zhou (Tencent AI Lab), *Fine-Grained Modeling of
Narrative Context: A Coherence Perspective via Retrospective Questions*, ACL
2024, [arXiv:2402.13551](https://arxiv.org/abs/2402.13551). The graph is
called NarCo.

**What the paper says.** Nodes are chunks of at most about 240 words, split
on paragraph and sentence boundaries, in reading order. Edges run backward,
from a later chunk to an earlier one, and carry up to four free-form questions
the later chunk raises that the earlier one answers — "why did that happen",
"who is this". GPT-4 generates them per node pair in two turns; a second pass
discards questions answerable from the later chunk alone, or hallucinated. The
number of surviving questions per edge is the signal in the recap task; in
plot retrieval the questions themselves are matched against the query.

*Correction to the first draft, which called the construction quadratic. The
definition ranges over every earlier node, but the paper's own realization
uses a window of four preceding nodes "such that the graph realization is
proportional to the input instead of being quadratic": about 6T thousand
tokens for a T-thousand-token context, or roughly six times the text, at
$0.03 per thousand input tokens with GPT-4 in 2024.*

*Instance-level, per-document. Orthogonal to the event graphs — it links
chunks without committing to a relation type.*

**Verdict: cheaper than first thought, and the transferable part is the edge,
not the graph.** A question the later moment asks of the earlier one is a
retrieval key written at write time: it says what a future reader would need
this passage for, in the reader's words rather than the passage's. That is
the write-time hook worth trying, at six times the text per session. The
window is what makes it affordable; across sessions the store is the whole
history, the window is gone, and the quadratic cost returns. Revisit as a
per-session key generator, not as a cross-session graph.

### STAC-typed causal graph (situation, task, action, consequence)

**Source:** Li, Pan and Pi (UC San Diego), *Beyond LLMs: A Linguistic
Approach to Causal Graph Generation from Narrative Texts*, Workshop on
Narrative Understanding 2025,
[arXiv:2504.07459](https://arxiv.org/abs/2504.07459).

**What the paper says.** It is a causal graph; STAC is the vertex typing, and
the typing constrains the edges. Vertices: GPT-4o rewrites the narrative into
sentences of at most two clauses, one explicit subject, active voice. Each
vertex gets one of four labels — situation (background), task (an explicit
requirement), action (an activity performed), consequence (an outcome that
changes state) — adapted from Minto's structured-thinking scheme from
business writing. The classifier is RoBERTa embeddings concatenated with seven
hand-defined linguistic features (genericity, eventivity, boundedness,
initiativity, time start, time end, impact) into XGBoost, trained on 1,000
annotated sentences. Edges come from a five-step loop: learn which label
transitions are valid ("bonds"), propose causal pairs, prune with a
counterfactual test — *if A had not occurred, would B still happen?* —
reconnect isolated vertices, compile. Evaluated on 100 chapters and short
stories published 1800–1950, against GPT-4o and Claude 3.5 building the same
graphs directly.

*Correction to the first draft, which called this "not a graph so much as a
typed clause schema" and costed it at one classification per clause. The
labels are one classification per clause; the edges are a model loop on top.*

*Instance-level, per-episode. The narrowest thing here, and the only one whose
shape matches what an agent actually does.*

**Verdict: right, and the one to steal — the labels and the bond, not the
pipeline.** Four fields on an episode, and a rule that a consequence follows
an action and an action follows a task. It answers the question this corpus
mostly does not ask — not "what is true now" but "what did we try, and what
happened". [funes](../content/systems/funes.md) argues for exactly this
without the vocabulary, quoting its own rationale document: *"A log also keeps
what a knowledge base throws away — the superseded passage is often the
answer itself: what did we try before, and why did we move off it?"* The
nearest pattern here, the [rejected-value tombstone](../content/patterns/rejected-value-tombstone.md),
keeps the consequence — this value was rejected — without the action that
produced it. And the expensive half of the paper's pipeline is mostly given
away in the agent setting: episodes arrive already segmented, a tool call is
an action and its result is a consequence, so the vertex rewriting the paper
needs a frontier model for is close to free. That is this note's inference,
not the paper's.

### Narrative map

**Source:** Keith Norambuena and Mitra, *Narrative Maps: An Algorithmic
Approach to Represent and Extract Information Narratives*, CSCW 2020,
[arXiv:2009.04508](https://arxiv.org/abs/2009.04508).

**What the paper says.** Definition 1: a weighted directed acyclic graph with
a single source (the starting event) and a single sink (the ending event).
Nodes are events, in practice news articles about one issue — hundreds of
articles on the coronavirus outbreak in the worked example. Edge weight is
coherence, a combination of event similarity over document embeddings and
topic similarity from shared clusters (UMAP over the embeddings, then
HDBSCAN). Extraction is a linear program that maximizes coherence subject to
coverage constraints over the topic clusters. Built for intelligence analysts,
computational journalists and misinformation researchers: the map is the
reading surface.

*Correction to the first draft, which said lexical similarity and
per-document. It is embedding similarity, and the unit is a document
collection about one issue.*

*Instance-level, per-collection. Close to an event evolutionary graph in
shape, but with instance nodes and acyclic by construction.*

**Verdict: wrong for storage, right for review.** The input is "everything
about one issue", which in memory terms is a query result, not a store. Worth
remembering if the assistant ever needs to show a person how a decision was
reached across many sessions — a different feature from remembering it, and
one that could be built over any of the instance-level stores above.

### Trope graph

**Source:** Alvarez and Font, *TropeTwist: Trope-based Narrative Structure
Generation*, Foundations of Digital Games 2022, procedural content generation
workshop, [arXiv:2204.09672](https://arxiv.org/abs/2204.09672).

**What the paper says.** Nodes are thirteen tropes taken from TvTropes, in
three base types — heroes, conflicts, enemies — plus plot devices: Hero,
Five-man band, The chosen one, Superhero, Conflict, Enemy, Empire, Big bad,
Dragon, Plot device, Chekhov's gun, MacGuffin, May help in quest. Three edge
types: a directed relation `A → B`, a reflexive one `A ↔ B` (a hero in
conflict with themselves), and entailment `A ♦— B` ("A entails B": an empire
entails a dragon, which entails a chosen one). Subgraphs such as conflict
patterns and plot-device patterns are the units the quality metrics count.
Graph grammars are the encoding; MAP-Elites is the search; the targets are
hand-made structures for three games; the fitness terms are coherence,
cohesion and interestingness.

*Correction to the survey page, which lists the edge types as "causal,
derivative, conflict, entailment". The paper has the three above; conflict is
a node type and a pattern, and derivatives are what one of the quality
metrics counts.*

*Type-level, per-corpus (a corpus of games). One of two entries here whose
nodes are not instances.*

**Verdict: wrong, and instructive about why.** A trope graph holds no
episodes; it constrains what *may* be generated. That is a schema with
fitness functions, and it fails the atlas's bar at the first clause — nothing
survives a session because nothing about a session was ever in it.

### Hierarchical multimodal graph

**Source:** Chen (Yale), *Hierarchical Knowledge Graphs for Story
Understanding in Visual Narratives*,
[arXiv:2506.10008](https://arxiv.org/abs/2506.10008); the first version was
titled *Structured Graph Representations for Visual Narrative Reasoning: A
Hierarchical Framework for Comics*.

**What the paper says.** Three levels, named panel, sequence and event. The
panel level is a multimodal knowledge graph — characters, objects, actions,
dialogue, captions, with semantic-role, spatial and action–agent edges. The
sequence level is a temporal graph over panels and event segments
(*precedes*), which is where flashbacks and ellipses are handled. The event
level is a semantic graph with macro-events, events and sub-events nested
(*subevent-of*, *precedes*, *co-occurs*). Cross-level edges are
*instantiates* and *refers-to*, so an entity keeps one identity from panel to
arc. Built by hand: the author annotated two Manga109 story arcs — 111 panels,
102 event segments, 39 events, 12 macro-events — and ran four symbolic
reasoning tasks over them in NetworkX.

*Correction to the survey page and the first draft, which gave the levels as
macro, mid and panel. Those are the nesting inside the event level, not the
three levels.*

*Instance-level, per-document. Orthogonal to everything above: a layering
that could wrap any of the instance-level entries.*

**Verdict: the layering transfers, the multimodality does not, and the
extraction is nobody's yet.** Macro / event / segment with explicit
*instantiates* edges is a summarization hierarchy where the summary still
points at what it summarizes — which is the thing several systems in this
corpus get wrong by letting a summary outlive its evidence. But the paper pays
its extraction cost by hand, at 111 panels; a memory system would pay it per
session, by model, and the paper says nothing about how well a model does it.

## Adding an entry

Cite the paper, not a survey of it, and state what the paper calls its nodes
and edges in the paper's own words. Place it on the two axes, then give a
verdict with a reason that is not a restatement of the axes. If the verdict
is "wrong for memory", say which clause of the scope bar it fails — survives
the session, retrievable later, scopeable, correctable, forgettable — because
"wrong" without that is an opinion.

## What has not been done

- Each paper was read to the depth of its definitions section and its
  construction method; none was read end to end, and no evaluation claim
  above has been checked beyond what the paper states.
- The survey page lists entries this register has not triaged: event-centric
  knowledge graphs ([arXiv:2205.03876](https://arxiv.org/abs/2205.03876)),
  EventGround ([arXiv:2404.00209](https://arxiv.org/abs/2404.00209)), and a
  second visual-narrative paper ([arXiv:2507.21893](https://arxiv.org/abs/2507.21893)).
- The claim that this corpus keeps `narrative` as node text rests on a grep
  (39 reports) and four of them read. The counter-examples, Hindsight and
  MemoMind, came from a second grep for causal links whose other hits were not
  checked, so no count of edge-carrying systems is claimed.
- Nothing load-bearing for the STAC recommendation rests on any of these
  gaps. It stands on funes's argument and on the shape of the corpus's
  correction machinery.

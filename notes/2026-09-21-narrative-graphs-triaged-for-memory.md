# Narrative graphs, triaged for memory

Eight ways of putting narrative or event data into a graph, each with what an
agent memory can take from it and what it must not. The register is the body;
the design patterns and anti-patterns it yields come first.

## What transfers

Four patterns, each carried by one entry below.

- **Type the episode, and constrain the transitions.** Label every clause of
  what happened as *situation*, *task*, *action* or *consequence*, and require
  that a consequence follows an action and an action follows a task. That is
  the shape of an agent's work, and it answers the question a fact store
  cannot: not *what is true now* but *what did we try, and what happened*.
  From the [STAC-typed causal graph](#stac-typed-causal-graph-situation-task-action-consequence).
- **A stance is an event with a holder.** "Prefers X", "rejected Y", "must
  do Z" are not facts about the world; they are facts about who holds them.
  Store them as a typed node with an explicit actor, or they cannot be scoped
  or corrected as the user's. From the
  [actor–event–perspectivization graph](#actorevent-perspectivization-graph).
- **Write the retrieval key as the question a later moment would ask.** At
  write time, generate the questions a future reader would need this passage
  to answer, in the reader's words, and index those. It costs about six
  times the text. From the [coherence graph](#coherence-graph-retrospective-questions).
- **A summary keeps an edge to what it summarizes.** Layer segment, event and
  arc, with an explicit *instantiates* edge from each level to the one
  below, so a summary cannot outlive its evidence. From the
  [hierarchical multimodal graph](#hierarchical-multimodal-graph).

## What does not

Three anti-patterns, and the clause of the scope bar each one fails.

- **A schema mistaken for a memory.** A graph whose nodes are *kinds* of
  event — `(eats, subj)`, `Hero`, `Big bad` — holds no episode. Nothing about
  a session survives in it, so it fails the bar at the first clause. Two
  entries below are this: the [event evolutionary graph](#event-evolutionary-graph-script-graph-eventuality-graph)
  and the [trope graph](#trope-graph).
- **Corpus statistics at one-user volume.** Edge weights that mean "what
  usually follows what" need thousands of episodes. One developer and one
  assistant produce a handful, and a prior learned from five samples is
  confident nonsense. Same two entries, second reason.
- **Narrative as a text blob on a node.** The story is in the edges: a
  causal link, a coherence weight, a stance with a holder. A `narrative`
  column beside `facts[]` keeps the prose and throws the structure away. 39
  reports in this corpus use the word, and in every one read for this note it
  names a text field. The edge form exists here too, without the vocabulary:
  [hindsight](../content/systems/hindsight.md) and
  [memomind](../content/systems/memomind.md) keep causal links between
  memories, and MemoMind boosts them at recall.

## How to read the register

Two axes decide most verdicts.

**Instance or type.** Does a node stand for *this* thing that happened, or for
a kind of thing that happens? Memory needs instances. A type-level graph is a
schema, and a schema is not a memory.

**Per-episode or per-corpus.** Is the structure built from one session, or
mined across thousands of documents? A corpus-level structure needs a corpus,
which one user and one assistant will not have for a long time. That rules
out several entries on volume alone, not on merit.

A third consideration cuts across both: **extraction cost**. Every entry
assumes something turns prose into structure, and the papers pay that cost
very differently — one by hand, one with a fine-tuned classifier, several
with a frontier model per pair of passages. A personal assistant pays it per
session, by model, forever.

## The register

### Narrative graph (umbrella)

The family term, not a member: entities, events, relations, tropes and
structural features of a story, encoded as a graph. No paper owns the phrase;
the trope paper and the political-discourse paper below each call their own
structure a "narrative graph" and mean different things by it.

The one commitment the members share is that **the story lives in the
edges** — a coherence weight, a causal link, a want with an actor — and not
in text attached to a node.

*Superset of everything below.*
**Verdict: n/a** — too general to adopt or reject.

### Event evolutionary graph (script graph; eventuality graph)

**Source:** Li, Ding and Liu, *Constructing Narrative Event Evolutionary
Graph for Script Event Prediction*, IJCAI 2018,
[arXiv:1805.05081](https://arxiv.org/abs/1805.05081). Near relative:
ASER, Zhang et al., WWW 2020, [arXiv:1905.00270](https://arxiv.org/abs/1905.00270),
whose nodes are eventualities and whose edges are Penn Discourse Treebank
relations (*Precedence*, *Reason*, *Result*): 194 million eventualities and
64 million edges from 11 billion tokens.

**What it is.** A node is an abstract event: a predicate verb and its
grammatical relation to the chain's protagonist, `(eats, subj)`. One node per
event *type*, not per mention — 104,940 nodes over the New York Times portion
of Gigaword. An edge is a predicate–GR bigram seen in the extracted chains,
directed, weighted by conditional probability
`count(vi, vj) / Σk count(vi, vk)`; 6,187,046 of them. Built as a knowledge
base of "event evolutionary principles" for predicting the next event in a
chain.

*Type-level, per-corpus. Narrative maps are a near relative with instance
nodes and different edge semantics.*

**Verdict: wrong for storage anywhere; possibly right as a prior beside an
organizational memory.** A node like `(eats, subj)` has no episode in it, so
nothing about a session survives — only a statistic learned from sessions.
As a prior over "what usually follows what" it needs volume a single
developer does not produce. A team memory over thousands of sessions is a
different calculation, and even there the graph sits beside the memory, not
in it.

### Actor–event–perspectivization graph

**Source:** Pournaki and Willaert, *Extracting narrative signals from public
discourse: a network-based approach*,
[arXiv:2411.00702](https://arxiv.org/abs/2411.00702); *Humanities and Social
Sciences Communications*, 2025.

**What it is.** Each sentence is parsed to Abstract Meaning Representation
with IBM's transition-based parser. Predicates become event nodes; their
argument fillers become actor nodes; edges from event to actor carry PropBank
roles (ARG0 agent, ARG1 patient, ...), and an event that is itself an
argument of another event gets a hierarchical edge to it. "Perspectivization"
is narrower than the word suggests: it is the operationalization of *goal
expressions* — events under two VerbAtlas frames, `require_need_want_hope`
and `oblige_force` ("we need to", "we must"), with an actor in ARG0 — and the
events those goal-events embed. The output is a narrative trace table from
which actor networks are drawn. Corpus: the State of the European Union
addresses, 2010–2023.

*Instance-level, per-document. A plain event graph with actors and
goal-holding on top.*

**Verdict: the idea yes, the machinery no.** The move worth keeping is that
a want or a must is an *event with an actor*, not a property of the world.
That is exactly the distinction a personal assistant loses when it stores
"prefers X" or "rejected Y" as ordinary facts: those are facts about the
user, with the user as ARG0, and a store that cannot say who holds them
cannot scope or correct them as the user's. The corpus's
[rejected-value tombstone](../content/patterns/rejected-value-tombstone.md)
is a special case — a rejected value is a stance with a holder. Take the
typed node with an explicit holder; skip the AMR pipeline, which is built
for speeches and heavy for a session log.

### Coherence graph (retrospective questions)

**Source:** Xu, Li, Yu and Zhou (Tencent AI Lab), *Fine-Grained Modeling of
Narrative Context: A Coherence Perspective via Retrospective Questions*, ACL
2024, [arXiv:2402.13551](https://arxiv.org/abs/2402.13551). The graph is
called NarCo.

**What it is.** Nodes are chunks of at most about 240 words, split on
paragraph and sentence boundaries, in reading order. Edges run backward, from
a later chunk to an earlier one, and carry up to four free-form questions the
later chunk raises that the earlier one answers — "why did that happen", "who
is this". GPT-4 generates them per node pair in two turns; a second pass
discards questions answerable from the later chunk alone, or hallucinated.
The number of surviving questions per edge is the signal in the recap task;
in plot retrieval the questions themselves are matched against the query.
The definition ranges over every earlier node, but the realization uses a
window of four preceding nodes "such that the graph realization is
proportional to the input instead of being quadratic": about six times the
text in tokens, at $0.03 per thousand input tokens with GPT-4 in 2024.

*Instance-level, per-document. Orthogonal to the event graphs — it links
chunks without committing to a relation type.*

**Verdict: the edge transfers, the graph does not.** A question the later
moment asks of the earlier one is a retrieval key written at write time: it
says what a future reader would need this passage for, in the reader's words
rather than the passage's. At six times the text per session that is
affordable. The window is what makes it so; across sessions the store is the
whole history, the window is gone, and the quadratic cost returns. Use it as
a per-session key generator, not as a cross-session graph.

### STAC-typed causal graph (situation, task, action, consequence)

**Source:** Li, Pan and Pi (UC San Diego), *Beyond LLMs: A Linguistic
Approach to Causal Graph Generation from Narrative Texts*, Workshop on
Narrative Understanding 2025,
[arXiv:2504.07459](https://arxiv.org/abs/2504.07459).

**What it is.** A causal graph whose vertices are typed, with the typing
constraining the edges. Vertices: GPT-4o rewrites the narrative into
sentences of at most two clauses, one explicit subject, active voice. Each
vertex gets one of four labels — situation (background), task (an explicit
requirement), action (an activity performed), consequence (an outcome that
changes state) — adapted from Minto's structured-thinking scheme from
business writing. The classifier is RoBERTa embeddings concatenated with
seven hand-defined linguistic features (genericity, eventivity, boundedness,
initiativity, time start, time end, impact) into XGBoost, trained on 1,000
annotated sentences. Edges come from a five-step loop: learn which label
transitions are valid ("bonds"), propose causal pairs, prune with a
counterfactual test — *if A had not occurred, would B still happen?* —
reconnect isolated vertices, compile. Evaluated on 100 chapters and short
stories published 1800–1950, against GPT-4o and Claude 3.5 building the same
graphs directly.

*Instance-level, per-episode. The narrowest thing here, and the only one whose
shape matches what an agent actually does.*

**Verdict: right, and the one to steal — the labels and the bond, not the
pipeline.** Four fields on an episode, and a rule that a consequence follows
an action and an action follows a task. [funes](../content/systems/funes.md)
argues for exactly this without the vocabulary, quoting its own rationale
document: *"A log also keeps what a knowledge base throws away — the
superseded passage is often the answer itself: what did we try before, and
why did we move off it?"* The nearest pattern in this corpus, the
[rejected-value tombstone](../content/patterns/rejected-value-tombstone.md),
keeps the consequence — this value was rejected — without the action that
produced it. The expensive half of the paper's pipeline is mostly given away
in the agent setting: episodes arrive already segmented, a tool call is an
action and its result is a consequence, so the vertex rewriting the paper
needs a frontier model for is close to free. That inference is this note's,
not the paper's.

### Narrative map

**Source:** Keith Norambuena and Mitra, *Narrative Maps: An Algorithmic
Approach to Represent and Extract Information Narratives*, CSCW 2020,
[arXiv:2009.04508](https://arxiv.org/abs/2009.04508).

**What it is.** A weighted directed acyclic graph with a single source (the
starting event) and a single sink (the ending event). Nodes are events, in
practice news articles about one issue — hundreds of articles on the
coronavirus outbreak in the worked example. Edge weight is coherence, a
combination of event similarity over document embeddings and topic
similarity from shared clusters (UMAP over the embeddings, then HDBSCAN).
Extraction is a linear program that maximizes coherence subject to coverage
constraints over the topic clusters. Built for intelligence analysts,
computational journalists and misinformation researchers: the map is the
reading surface.

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

**What it is.** Nodes are thirteen tropes taken from TvTropes, in three base
types — heroes, conflicts, enemies — plus plot devices: Hero, Five-man band,
The chosen one, Superhero, Conflict, Enemy, Empire, Big bad, Dragon, Plot
device, Chekhov's gun, MacGuffin, May help in quest. Three edge types: a
directed relation `A → B`, a reflexive one `A ↔ B` (a hero in conflict with
themselves), and entailment `A ♦— B` ("A entails B": an empire entails a
dragon, which entails a chosen one). Subgraphs such as conflict patterns and
plot-device patterns are the units the quality metrics count. Graph grammars
are the encoding; MAP-Elites is the search; the targets are hand-made
structures for three games; the fitness terms are coherence, cohesion and
interestingness.

*Type-level, per-corpus (a corpus of games).*

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

**What it is.** Three levels, named panel, sequence and event. The panel
level is a multimodal knowledge graph — characters, objects, actions,
dialogue, captions, with semantic-role, spatial and action–agent edges. The
sequence level is a temporal graph over panels and event segments
(*precedes*), which is where flashbacks and ellipses are handled. The event
level is a semantic graph with macro-events, events and sub-events nested
(*subevent-of*, *precedes*, *co-occurs*). Cross-level edges are
*instantiates* and *refers-to*, so an entity keeps one identity from panel to
arc. Built by hand: the author annotated two Manga109 story arcs — 111
panels, 102 event segments, 39 events, 12 macro-events — and ran four
symbolic reasoning tasks over them in NetworkX.

*Instance-level, per-document. Orthogonal to everything above: a layering
that could wrap any of the instance-level entries.*

**Verdict: the layering transfers, the multimodality does not, and the
extraction is nobody's yet.** Segment / event / arc with explicit
*instantiates* edges is a summarization hierarchy where the summary still
points at what it summarizes — which is the thing several systems in this
corpus get wrong by letting a summary outlive its evidence. The paper pays
its extraction by hand, at 111 panels; a memory system would pay it per
session, by model, and the paper says nothing about how well a model does it.

## Adding an entry

Cite the paper and state what the paper calls its nodes and edges in the
paper's own words. Place it on the two axes, then give a verdict with a
reason that is not a restatement of the axes. If the verdict is "wrong for
memory", say which clause of the scope bar it fails — survives the session,
retrievable later, scopeable, correctable, forgettable — because "wrong"
without that is an opinion. If something transfers, add it to the pattern
list at the top with the one entry it comes from.

## Sources and limits

- The class list was taken from an unsigned, machine-written topic page and
  then checked against each paper on 2026-09-21. Every description above is
  the paper's; the page's paraphrases are not used.
- Each paper was read to the depth of its definitions and construction
  sections, not end to end. No evaluation claim above has been checked beyond
  what the paper states.
- Not yet triaged: event-centric knowledge graphs
  ([arXiv:2205.03876](https://arxiv.org/abs/2205.03876)), EventGround
  ([arXiv:2404.00209](https://arxiv.org/abs/2404.00209)), and a second
  visual-narrative paper ([arXiv:2507.21893](https://arxiv.org/abs/2507.21893)).
- The claim that this corpus keeps `narrative` as node text rests on a grep
  (39 reports) and four of them read: [moltbrain](../content/systems/moltbrain.md),
  [byterover](../content/systems/byterover.md),
  [agent-working-memory](../content/systems/agent-working-memory.md) and
  [claude-self-reflect](../content/systems/claude-self-reflect.md). Hindsight
  and MemoMind came from a second grep for causal links whose other hits were
  not checked, so no count of edge-carrying systems is claimed.
- The atlas does not otherwise use this vocabulary, or say why not — the same
  omission [symbolic prior art](2026-07-28-symbolic-prior-art.md) records for
  belief revision and truth maintenance.

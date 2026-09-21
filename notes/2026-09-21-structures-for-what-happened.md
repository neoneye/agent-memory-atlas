# Structures for what happened, triaged for memory

Seven graph-based approaches, plus the umbrella term *narrative graph*,
triaged for remembering what an agent and a user did. They serve different
jobs: recording an episode, supplying a prior, generating a story, or showing
a history. This is a register of representations, not a comparison of complete
memory systems, and it remains open to non-graph structures.

The useful transfers are episode roles, attributed stances, question-based
retrieval keys and evidence-linked summaries. Their value is a hypothesis for
agent memory; the papers below do not establish that they improve long-term
assistant recall, correction or forgetting.

## What transfers

Four patterns to try, with the source and the adaptation kept distinct.

- **Keep the attempt and its outcome together.** Use *situation*, *task*,
  *action* and *consequence* as episode roles, allowing repeated actions,
  missing roles and unresolved outcomes. Distinguish sequence from causation.
  This makes “what did we try, and what happened?” a direct retrieval target.
  From the [STAC-typed causal graph](#stac-typed-causal-graph-situation-task-action-consequence).
- **Attribute a stance to its holder and its source.** “Prefers X”, “rejected
  Y” and “must do Z” need an actor, a scope, a time and evidence. A stated
  preference, an imposed obligation and an assistant's inference are different
  claims. Extending goal-event attribution to these other stances is this
  note's proposal. From the
  [actor–event–perspectivization graph](#actoreventperspectivization-graph).
- **Index an episode by questions it can answer.** Generate a few retrieval
  questions grounded in retained evidence. The source paper connects two
  already-seen passages; anticipating a future session's questions is an
  adaptation, with its own quality and cost to measure. From the
  [coherence graph](#coherence-graph-retrospective-questions).
- **A summary keeps links to what supports it.** Link summaries to versioned
  evidence so correction or deletion can find their dependents. Those links
  enable invalidation; a read filter and an update policy must enforce it.
  From the [hierarchical multimodal graph](#hierarchical-multimodal-graph).

## What does not

Three ways to mistake a useful representation for a sufficient memory.

- **A generalization substituted for its instances.** The
  [event evolutionary graph](#event-evolutionary-graph-script-graph-eventuality-graph)
  collapses occurrences into event types and transition counts. A
  [trope graph](#trope-graph) abstracts a story into roles and conflicts.
  Both can be useful stored knowledge; neither, as described, retains the
  evidence needed to recover and correct a particular agent episode.
- **A frequency treated as a reliable personal prior.** A transition seen a
  few times is weak evidence for “what usually follows what”. Reliability
  depends on counts per transition, task diversity and uncertainty, not a
  universal minimum number of sessions. A pretrained corpus prior avoids
  learning everything locally, but its applicability still needs testing.
  This applies to the event evolutionary graph; TropeTwist is not a
  corpus-frequency estimator.
- **Prose expected to do the work of explicit relations.** A `narrative`
  field can preserve an excellent account. It does not by itself provide
  queryable links for “which attempt produced this observation?” or “which
  summaries depend on this source?”. Conversely, an edge is not proof of
  causation. The atlas already contains several shapes:
  [moltbrain](../content/systems/moltbrain.md) has a narrative field;
  [agent-working-memory](../content/systems/agent-working-memory.md) uses
  narrative cohesion in graph-based retraction propagation;
  [hindsight](../content/systems/hindsight.md) and
  [memomind](../content/systems/memomind.md) retain causal links, which
  MemoMind boosts at recall. These examples support a distinction between
  mechanisms, not a claim that the corpus uses the word only for text.

## How to read the register

The [atlas scope bar](../content/contributing.md#proposing-a-memory-system)
asks whether something is stored beyond a session, retrieved later, and could
in principle be scoped, corrected or forgotten. It does not require episodic
memory: a durable generalization can qualify. The narrower question here is
whether a representation preserves **what happened in a particular episode**.

Two axes help place each proposal.

**Instance or type.** Does a node stand for *this* thing that happened, or for
a kind of thing that happens? Episodic recall needs identifiable occurrences.
Type-level knowledge can sit beside them, but cannot replace their evidence.

**Construction unit.** Is it built from a document or episode, extracted
from a collection, mined across a corpus, or authored and generated? Those
have different costs. A corpus prior can be imported; a graph over many
episodes can still use bounded candidate selection.

| Structure | What its nodes identify | Construction | Candidate role in memory |
| --- | --- | --- | --- |
| Event evolutionary graph | Event types | Mined corpus | Prior beside episode records |
| Actor–event–perspectivization graph | Event mentions and participants | Document parsing | Attribution of goals and stances |
| Coherence graph | Text chunks | Selected passage pairs | Retrieval keys and context links |
| STAC-typed causal graph | Rewritten narrative clauses | Episode/document extraction | Attempt–outcome organization |
| Narrative map | Articles representing events | A selected collection | Review surface |
| Trope graph | Abstract roles and narrative elements | Authored examples and generation | Story schema |
| Hierarchical multimodal graph | Panels, entities and event units | Manual annotation | Evidence-linked hierarchy |

A third consideration is **construction and maintenance cost**: parsing,
annotation, model calls, indexing, and repair after a correction. The papers
pay for construction differently. An agent can capture tool-call identifiers
and returned observations directly; interpreting their significance still
requires work. None of these representations alone supplies scope enforcement,
trust state or deletion propagation.

## The register

### Narrative graph (umbrella)

The family term, not a member: entities, events, relations, tropes and
structural features of a story, encoded as a graph. No paper owns the phrase;
the trope paper and the political-discourse paper below each call their own
structure a "narrative graph" and mean different things by it.

The common move is to make some relations explicit — temporal, causal,
semantic or structural — alongside whatever text the nodes preserve. The
edge semantics differ enough that “uses a narrative graph” explains little
without naming them.

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

*Type-level, per-corpus. An aggregate over occurrences, not a record of them.*

**Verdict: a possible prior, insufficient as the episode record.** A node
like `(eats, subj)` cannot identify which occurrence a user is correcting.
The aggregate may persist and be retrieved, so it does not inherently fail
the atlas's scope bar. It loses the episode-specific identity and evidence
this note needs. An imported graph could inform predictions even for one
user; a locally learned one needs enough support per transition. Either
belongs beside identifiable episode records.

### Actor–event–perspectivization graph

**Source:** Pournaki and Willaert, *Extracting narrative signals from public
discourse: a network-based approach*,
[arXiv:2411.00702](https://arxiv.org/abs/2411.00702); *Humanities and Social
Sciences Communications*, 2025.

**What it is.** Each sentence is parsed to Abstract Meaning Representation
with IBM's transition-based parser. Predicates become event nodes; their
argument fillers become actor nodes; edges from event to actor carry PropBank
roles (often ARG0 agent, ARG1 patient; the roles are predicate-specific).
An event that is itself an argument of another event gets a hierarchical
edge to it. "Perspectivization" is narrower than the word suggests: it is the
operationalization of *goal expressions* — events under two VerbAtlas frames,
`require_need_want_hope`
and `oblige_force` ("we need to", "we must"), with an actor in ARG0 — and the
events those goal-events embed. The output is a narrative trace table from
which actor networks are drawn. Corpus: the State of the European Union
addresses, 2010–2023.

*Instance-level, per-document. A plain event graph with actors and
goal-holding on top.*

**Verdict: borrow attribution; justify the parser separately.** The paper
makes goal expressions attributable to actors. For memory, extend that idea
to preferences, decisions and rejections, recording both who holds the stance
and who reported it. “The assistant inferred that the user prefers X” must
remain distinct from the user's statement. An explicit subject in a fact
record can do this too; a graph node is not required.

The [rejected-value tombstone](../content/patterns/rejected-value-tombstone.md)
adds an operational requirement beyond attribution: a durable value-level
record is consulted to prevent reassertion. A rejection event alone does not
provide that gate. AMR is an extraction option for unstructured text; a session
with known speakers and tool actors may not need it.

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
For plot retrieval and long-document QA, construction is limited to four
preceding nodes. Appendix A.1 reports roughly `6T` thousand processing tokens
and a total cost of `$0.03T` for a source of `T` thousand tokens. That is the
paper's construction estimate at its historical pricing, not a sixfold
storage multiplier or a current API token rate.

*Instance-level, per-document. Orthogonal to the event graphs — it links
chunks without committing to a relation type.*

**Verdict: try bounded question-based indexing.** NarCo derives a question
from two passages already available. Generating questions from one episode
for a future reader is a related proposal, not the method the paper tested.
Keep the answer's evidence reference with each key, and check that the
question neither invents an outcome nor assumes an unsupported cause.

Cross-session linking becomes quadratic only if every pair is considered.
A recency window or a fixed number of retrieved candidates can bound pair
generation to `O(Nk)` for `N` chunks and `k` candidates per chunk, excluding
candidate-search cost. That trades coverage for cost. Compare retrieval
against the original episode text before paying for the extra index; the
paper's budget alone does not establish affordability for an assistant.

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
annotated sentences. Edges come from a five-step loop: prompt the model with
the valid label relationships ("bonds"), propose causal pairs, prune with a
counterfactual test — *if A had not occurred, would B still happen?* —
reconnect isolated vertices, compile. Evaluated on 100 chapters and short
stories published 1800–1950, against GPT-4o and Claude 3.5 building the same
graphs directly. Section 3.4 permits 11 of the 16 label-pair types, including
action → action and situation → situation; STAC is not a mandatory four-step
chain. The counterfactual prompt assesses textual plausibility, not causality
established by intervention.

*Instance-level, per-document. Its roles are a useful candidate vocabulary
for episodes of agent work.*

**Verdict: the strongest candidate here for organizing attempts and
outcomes.** Use the roles as optional, repeatable parts of an episode. An
action can produce no observation, several observations or a delayed result;
an observed change can have causes outside the agent's actions. Preserve
`precedes`, `result_of_call` and an inferred `causes` as different relations.

[funes](../content/systems/funes.md) argues for keeping superseded attempts
and the reasons for moving away from them. That supports preserving history,
not specifically STAC typing. A rejected-value tombstone prevents a value
from returning; linking it to an episode can additionally explain the attempt
and decision behind it.

Tool logs supply action boundaries and call–response links cheaply. A tool
response is an observation, not necessarily proof that the intended change
happened: a timeout can leave the outcome unknown. Task boundaries, user
intent, delayed effects and causal attribution still need extraction or
verification. This adaptation is the note's, not the paper's result.

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

*Instance-level, per-collection. Its coherence weights organize a reading
path; they are not transition counts or causal claims.*

**Verdict: useful as a derived review surface.** A map could help a person
trace a decision across sessions. Its coherence objective and coverage
constraints select a readable account; they do not guarantee preservation of
every failed attempt or dissenting observation. Keep the underlying records
and make omissions inspectable. Coherence is not a causal explanation, and
the single-start/single-end constraint should be relaxed for ongoing work.
The map can itself be stored, but should not be the sole episode record.

### Trope graph

**Source:** Alvarez and Font, *TropeTwist: Trope-based Narrative Structure
Generation*, Foundations of Digital Games 2022, procedural content generation
workshop, [arXiv:2204.09672](https://arxiv.org/abs/2204.09672).

**What it is.** Nodes use thirteen tropes taken from TvTropes, grouped as
heroes, conflicts, enemies and plot devices: Hero, Five-man band,
The chosen one, Superhero, Conflict, Enemy, Empire, Big bad, Dragon, Plot
device, Chekhov's gun, MacGuffin, May help in quest. Three edge types: a
directed relation `A → B`, a bidirectional relation `A ↔ B` (called
“reflexive” in the paper), and entailment `A ♦— B` ("A entails B": an empire
entails a dragon, which entails a chosen one). Subgraphs such as conflict
patterns and plot-device patterns are the units the quality metrics count. Graph grammars
are the encoding; MAP-Elites is the search; the targets are hand-made
structures for three games; the fitness terms are coherence, cohesion and
interestingness.

*Schema-level abstractions of individual stories; authored and generated,
not mined transition statistics over a corpus.*

**Verdict: a story-design representation, not an episode record.** It can
describe an existing game as well as constrain generated variants, so it is
not merely a list of event types. But its roles and conflict patterns omit
the source-linked occurrences needed to recover an agent's actual attempts.
Its mismatch is the level of abstraction and purpose, not insufficient
corpus size. A stored trope graph could meet the atlas's general scope bar
without answering this note's episodic question.

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
(*subevent-of*, *precedes*, *co-occurs*). Panels link to event segments via
*instantiates*; segments, events and macro-events are grouped through
*subevent-of*. Identity-preserving *refers-to* edges connect entities across
levels. Built by hand: the author annotated two Manga109 story arcs — 111
panels, 102 event segments, 39 events, 12 macro-events — and ran four
symbolic reasoning tasks over them in NetworkX.

*Instance-level, per-document. Orthogonal to everything above: a layering
that could wrap any of the instance-level entries.*

**Verdict: borrow the traceable hierarchy; add a maintenance policy.** A
memory adaptation could link summaries to episode records and records to
source spans. Use relations such as `summarizes` and `supported_by` for those
jobs; the paper does not call every cross-level link *instantiates*.

A pointer makes dependencies discoverable. To prevent unsupported recall,
source correction must invalidate affected derivatives, and reads must
withhold them until they are recomputed or revalidated. Forgetting also needs
to reach derivative text and indexes. A retained historical summary may
remain useful if clearly marked; it must not masquerade as current evidence.
These lifecycle rules are this note's extension, not a result of the paper.
Multimodal linking is relevant when an agent uses screenshots or documents;
the unproven part is reliable automated extraction at memory-system scale.

## A small episode, and what would justify keeping the structure

An illustrative session: a user asks the assistant to enable a project
setting. The update call times out. A later read confirms that the setting
was enabled. The user then says to keep that setting off for this project,
and a second update plus a read confirms it is off.

| Record or relation | What to preserve |
| --- | --- |
| Task and scope | The original request, user, project and source message |
| First action | The attempted update, arguments, timestamp and call ID |
| First observation | Timeout linked to the call; outcome still unknown |
| Later observation | Read reports “on”; this confirms state, not by itself which action caused it |
| User stance | “Keep it off”, its holder, project scope, time and source; distinct from the earlier request |
| Second attempt and observation | Update to “off”, followed by a read confirming “off” |
| Retrieval key | “Why is this setting off in this project?” linked to the user decision and episode |
| Summary | The account above, linked to the exact evidence revisions it summarizes |

The current setting, the user's standing instruction and the history of
attempts are three different things to retrieve. The instruction supersedes
the earlier request for future action; it does not make the earlier request
or the observed “on” state historically false. No causal edge should be
invented just to complete the four STAC roles. These records and links can
live in ordinary tables; none requires a graph database.

Before adopting the extra structure, compare it with a simpler baseline:
the same scoped, source-linked episode text retrieved directly. Use later
questions held out from key generation, and check:

- Does it recover the failed or uncertain attempt as well as the final state?
- Does it distinguish what the user said from what the assistant inferred?
- Does a project-specific instruction stay within its project, including
  when recall follows an edge to another record?
- After a source correction or deletion, can an old summary or generated
  question still expose the removed claim?
- Does any retrieval gain justify extraction tokens, latency, index size and
  the cost of repairing derivatives?

These are proposed checks, not experiments run for this note. If simple
episode records answer them adequately, the graph adds no demonstrated value.

## Adding an entry

Cite the paper, preferably the version and section, and use its terminology
for nodes and edges. Identify the construction unit and intended job. Keep
the paper's mechanism separate from the proposed memory adaptation, its cost
and the evidence that would justify it. Distinguish failing the atlas's scope
bar from being insufficient for episodic recall. If something transfers, add
it to the pattern list with its source and the conditions on the transfer.

## Sources and limits

- The initial class list came from an unsigned, machine-written topic page.
  It is a starting list, not a systematic survey or an exhaustive taxonomy.
  Definitions and construction details were checked against the papers on
  2026-09-21; the verdicts and memory adaptations are this note's judgements.
- The key qualifications can be checked in STAC
  [v1 §3.4](https://arxiv.org/html/2504.07459v1#S3.SS4), NarCo
  [v2 §3 and Appendix A.1](https://arxiv.org/html/2402.13551v2),
  the discourse paper [v2 §2](https://arxiv.org/html/2411.00702v2),
  TropeTwist [v2 §§3–4](https://arxiv.org/html/2204.09672v2), and the
  hierarchical graph paper [v2 §3](https://arxiv.org/html/2506.10008v2).
  Papers were read for definitions and construction, not reproduced; reported
  evaluations are not independent evidence of performance in agent memory.

- Not yet triaged: event-centric knowledge graphs
  ([arXiv:2205.03876](https://arxiv.org/abs/2205.03876)), EventGround
  ([arXiv:2404.00209](https://arxiv.org/abs/2404.00209)), and a second
  visual-narrative paper ([arXiv:2507.21893](https://arxiv.org/abs/2507.21893)).
- Corpus comparisons rely on the linked atlas reports at their recorded pins,
  not new inspections of those systems' source code. Word searches are a way
  to find examples, not a census of mechanisms. No prevalence claim is made
  about prose narratives or graph-based memory.
- [Symbolic prior art](2026-07-28-symbolic-prior-art.md) raises a related
  question for belief revision and truth maintenance: what can memory design
  borrow from established representations without inheriting their full
  machinery?

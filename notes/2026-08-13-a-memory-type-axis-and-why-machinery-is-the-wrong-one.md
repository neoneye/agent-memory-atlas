# A memory-type axis, and why sorting by machinery is the wrong version of it

**Status:** half accepted, half declined, with the declined half argued.
**Origin:** an outside review (Qwen, 2026-08-13):

> **Draw a Hard Line: "Memory" vs "Telemetry/Logging."** Appending a board state
> to `logs.txt` and using `grep` is **Episodic Telemetry**. Vector databases with
> decay curves are **Semantic Memory**. … Stop treating flat-file append-only
> logs as direct competitors to complex memory graphs. Compare apples to apples.

## The half that is right

The atlas has no axis for *what kind of memory this is*. Its eight families —
embeddable library, hosted service, agent-runtime, host runtime with pluggable
memory, local coding-agent, graph and temporal, verification-first, research
lineage — sort by **how you would adopt it**, not by what it holds. That is a
useful axis for someone choosing a dependency and a useless one for someone
asking "who else stores procedures rather than facts".

A reader currently answers that question by reading the comparative matrix's
`memory_unit` column, which is 264 sentences. The frontmatter's `stack_storage`
and `stack_retrieval` come closer and describe the plumbing rather than the
content. So a memory-type tag is a real gap, and a closed vocabulary over
something like *episodic trace*, *semantic fact*, *procedural skill*, *working
state*, *decision record* would be filterable, seedable from `memory_unit`, and
orthogonal to the families rather than a ninth one — which matters, because
adding families is what
[turned the taxonomy into a list once already](../content/patterns/index.md).

## The half that is wrong, and the corpus says so

The proposal's stated reason is that a flat log with `grep` is a lesser thing
than a vector database with decay curves, and that comparing them flatters the
former. The atlas's own strongest finding on that question points the other way:

> The system with the least retrieval machinery has the strongest deletion
> guarantee, and the trade is explicit: it also has no semantic retrieval at all.
> — [the comparative report](../content/overview.md), on [daimon](../content/systems/daimon.md)

daimon carries the most complete deletion test in the corpus — eleven steps, each
paired with a never-forgotten twin — and step 8 can assert absence from *the whole
index* precisely because the index is a disposable SQLite FTS5 database rebuilt
from checkpoints, with no embedding anywhere in the source. It has nothing to
prove about compaction because it has no graph to compact.

Sorting by machinery would file that system below the ones it beats on the axis
this atlas cares most about. The same inversion runs through the corpus: on three
of four vector engines a deleted memory's embedding survives until a vacuum the
memory layer does not schedule, and nobody discloses it. Machinery buys recall
and costs forgettability, and a taxonomy that ranks by machinery hides the trade
instead of showing it.

## What the scope bar actually says, and how the two harnesses pass it

The bar is: something is **stored**, **retrieved later**, and can be **scoped,
corrected, or forgotten** — with a "not in scope" section for chat buffers, KV
caches and response caches, because a naming collision misleads people evaluating
options.

[PRO-LONG](../content/systems/pro-long.md) and
[arc-code](../content/systems/arc-code.md) pass the first two and fail the third
in a specific, published way. Each agent call is a fresh session; the durable
artifact survives it; the agent recovers state by reading that artifact rather
than from its context, and in arc-code the schema counts how often the context
compacted underneath it. That is memory outliving a session, which is the bar.

Neither can correct anything, and both reports say so — `capabilities: ""` on
each, with the reason in prose. **That is the taxonomy working, not failing.** A
reader comparing the two against MindCache sees two empty mark rows and one
carrying `trust_state`, which is the apples-to-apples comparison the review asks
for, expressed in the mechanism vocabulary rather than in a genre label.

Where the review has a point about *those two* specifically: both sit in
`research lineage` beside Generative Agents and HippoRAG, and they are benchmark
harnesses rather than research artifacts. A memory-type tag would separate them
without needing a new family, which is another argument for the axis and against
the reason given for it.

## Proposal

1. **Add `memory_type` as a flat frontmatter key** with a closed vocabulary,
   seeded from `memory_unit` and labelled `seeded`/`reviewed` exactly as
   `stack_*` was — see
   [what a friction column could actually say](2026-08-13-what-a-friction-column-could-actually-say.md)
   for the mechanism, which already exists and is enforced by `npm test`.
2. **Let a system carry more than one.** MindCache holds decisions *and*
   episodes *and* user facts in separate tables; a single tag would be a lie
   about half the corpus.
3. **Do not rank the values, and do not use the tag to decide scope.** Scope is
   the existing bar and it is a behavioural test, not a genre judgement. The tag
   answers "what does this hold"; `capabilities:` already answers "what can it do
   about it".

## Not proposed

A "telemetry" bucket for systems the atlas judges lightweight. Every candidate
for it — the two harnesses, the Markdown notebooks, the file-native stores —
either passes the scope bar or is already in the "not in scope" section, and a
third category between them would be a place to put systems nobody wanted to
argue about.

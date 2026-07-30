# Twenty suggested systems, triaged

**Status:** done — five of the six became reports the same day; see the outcomes table
**Origin:** a 20-item list of "agent memory systems missing from the atlas",
produced by Grok and submitted on 2026-07-30. Checked against the 91 reports in
`content/systems/` and against the two rules the atlas already publishes:
inspectable code at a pinned commit, and *survives the session with a
correctable identity*.

Recorded because half the list is the closed-source proposal arriving for at
least the third time, and re-deriving the refusal each time is the cost this
notes directory exists to avoid.

## The ledger

| # | Item | Outcome |
| --- | --- | --- |
| 1 | Zep (hosted) | Reviewed as [Graphiti](../content/systems/graphiti.md); the service is already named unreachable in the scope section |
| 2 | Memvid | [Reviewed](../content/systems/memvid.md) |
| 3 | Membase | **New**, and the one that did not survive contact: no licence file at the pinned commit, and the axis is on-chain verifiability rather than memory mechanism |
| 4 | Memory Store (memory.store) | Hosted, closed. Unreachable |
| 5 | Graphlit | Hosted, closed. Unreachable |
| 6 | CrewAI Memory | Already named as a known gap, [overview.md:3646](../content/overview.md) |
| 7 | Agno | **New, and the strongest item on the list.** Named nowhere in the corpus |
| 8 | Microsoft Agent Framework | **New.** Open source, GA 1.0; the reviewable part is the contract. Foundry Agent Service itself is closed |
| 9 | OpenAI Agents SDK | Out of scope. `SQLiteSession` is a conversation log |
| 10 | Claude memory stores | Closed. Unreachable |
| 11 | Vertex AI Memory Bank | The client is inside [adk-python](../content/systems/adk-python.md); the service is closed |
| 12 | Haystack | Already named as a known gap, same bullet as CrewAI |
| 13 | DSPy | Out of scope. Retrieval and optimizers, no memory subsystem |
| 14 | Pydantic AI | **New**, but not the framework — the *harness* |
| 15 | LangGraph / LangChain | [LangMem](../content/systems/langmem.md) reviewed; `langchain-ai/memory-agent` examined twice and rejected as a 235-line template |
| 16 | AutoGen / AG2 | [Reviewed](../content/systems/autogen.md) |
| 17 | CAMEL-AI | **New.** `camel-ai/camel`, a pluggable memory contract |
| 18 | "SimpleMem / Membox-style research systems" | **New**, once un-hedged — see below |
| 19 | MemTrust | A paper, not a system. Probably the OWASP-guard treatment |
| 20 | Oracle / AgentCore-style DB-native memory | Already refused by name: `oracleagentmemory` has no public source repository |

Five already reviewed, five unreachable, two out of scope, two already named as
gaps, six new.

## The closed-source half, for the third time

Items 1 (hosted), 4, 5, 10, 11 (service) and 20 are the same proposal:
review the memory products most users have actually met.

[overview.md](../content/overview.md) already concedes this in the scope
section, at more length than a reviewer proposing it would expect — it names
OpenAI's memory, Claude's memory and project knowledge, Zep's service and Vertex
Memory Bank; states that these are the systems operating under the compliance,
tenancy and retention constraints the local-first corpus never faces; and draws
the consequence for the headline counts, that a closed system could hold any of
these mechanisms without this method ever knowing.

So the gap is admitted, sized, and load-bearing. What is being proposed is not
*naming* it but *filling* it, and the only way to fill it is to write reports
from documentation. That trades the one property that makes a mark mean
something — found in code at a pinned commit — for coverage of products that
publish their own feature lists anyway.

**Would change if** a hosted product ships an inspectable component. That rule
is already applied twice: Zep is here as Graphiti, Memory Bank as a client
contract inside adk-python. Both reports say plainly that this is less than
reviewing the service.

## Out of scope, and why these two are not close calls

**OpenAI Agents SDK.** `SQLiteSession` has `add_items`, `get_items`,
`pop_item`, `clear_session`, and defaults to an in-memory database. That is
conversation history with an optional file path. The same call has already been
made for [Pi](../content/systems/pi.md) — reviewed for session persistence and
the extension surface, with the report saying it has no memory subsystem — and
for LlamaIndex's `ChatMemoryBuffer` family, excluded inside a report that
reviews the newer block-based `Memory` instead.

**DSPy.** Retrieval modules and optimizers. Nothing durable carries an identity
that can later be corrected.

## The six worth doing, in order

1. **Agno** (`agno-agi/agno`) — a full agent platform with a built-in memory
   layer: session storage, user memories recalled across sessions, your own
   database. The string does not appear anywhere in `content/` or `notes/`.
   That is the largest framework-native omission the atlas has not already
   admitted to, and it should join CrewAI and Haystack in that bullet whether or
   not it gets a report soon.

2. **SimpleMem** (`aiming-lab/SimpleMem`,
   [arXiv:2601.02553](https://arxiv.org/abs/2601.02553)) — same lab as
   [MetaClaw](../content/systems/metaclaw.md), which is already pinned, so the
   authors' committing habits are partly known. It claims +26.4% F1 over Mem0 and
   a 30× token reduction, with an Omni- v2 in April 2026 claiming LoCoMo F1 0.613.
   Those are exactly the figures the
   [reading-list note](2026-07-29-a-reading-list-triaged.md) says to check
   against committed artifacts rather than read, and the atlas already records
   three systems — Memvid, MemoryOS, FiFA — whose headline numbers had no raw
   results behind them.

3. **Pydantic AI harness memory** — the framework itself is stateless per
   `agent.run()` and would be a wasted read. The harness is not: memory as a
   `MEMORY.md` notebook plus sibling files, with a bounded excerpt injected as
   delimited user-role context. That is the
   [basic-memory](../content/systems/basic-memory.md) /
   [claude-mem](../content/systems/claude-mem.md) markdown shape shipped by a
   typed-framework vendor, and the delimiting is a provenance decision worth
   reading against [openhuman](../content/systems/openhuman.md)'s taint labels.

4. **CAMEL-AI** (`camel-ai/camel`) — `AgentMemory` over `ChatHistoryBlock` and
   `VectorDBBlock`, with key-value and vector storage abstractions underneath.
   A third pluggable-provider contract to sit beside
   [adk-python](../content/systems/adk-python.md) and
   [AutoGen](../content/systems/autogen.md), and the interesting question is the
   one those two answered differently: what the contract makes impossible.

5. **Microsoft Agent Framework** — open source, GA 1.0 in April 2026, and the
   successor to both AutoGen and Semantic Kernel. Reviewing it would retire the
   Semantic Kernel line in the gap bullet rather than add to it. Its memory is a
   pluggable contract over Foundry, Mem0, Redis and Neo4j; the contract is
   reviewable and Foundry is not, which is the adk-python situation exactly.

6. **Membase** (`unibaseio/membase`) — real, open, and pointed at a different
   problem: decentralized storage with verifiable multi-session memory, a hub
   with auto-upload, an MCP gateway. Worth a look because the corpus has nothing
   whose durability argument is cryptographic rather than operational. Ranked
   last because on the seven columns it will most likely read as a buffered
   conversation store with a blockchain behind it, and because "verifiable"
   there means the record was not tampered with, not that the belief was ever
   true.

Licences unchecked for all six at the time of triage; that is the first step of
the `add-memory-system` skill and not a triage question. It decided one of the
six — see below.

## Two properties of the list itself

**The two vaguest entries were the two most checkable.** Item 18 is written as
"SimpleMem / Membox-style research systems" — a hedge naming a category — and
behind it are a paper with a repository and a second real paper (*Membox:
Weaving Topic Continuity into Long-Range Memory for LLM Agents*, January 2026).
Item 19, MemTrust, reads like a coinage and is
[arXiv:2601.07004](https://arxiv.org/abs/2601.07004), a five-layer TEE
architecture over Storage, Extraction, Learning, Retrieval and Governance. The
list hedged hardest exactly where it had the most to point at.

MemTrust is not a system report either way. If it ships no code it belongs where
the security survey went in
[the OWASP note](2026-07-29-security-research-names-the-column.md): a threat
model that derives columns, cited in prose. Its five layers are worth reading
against that survey's six lifecycle phases, since both partition the same object
and neither cites the other.

**The ordering is inverted relative to what the method can use.** Four hosted
products lead; Agno, the one genuinely new open framework with real memory, is
seventh. A list ranked by how much a system is discussed will always look like
this, and the atlas's ranking — how much inspectable mechanism is there — is not
recoverable from discussion volume. That is the same
[judge-code-not-popularity](2026-07-28-declined-proposals.md) instinct the
declined-proposals note applies to leaderboards, arriving from the intake side.

## What the six turned into

All six were read on 2026-07-30, the same day this note was written. Five became
reports and one did not; the corpus went from 91 to 96.

| Candidate | Outcome |
| --- | --- |
| Agno | [Reviewed](../content/systems/agno.md). `LearningMode.PROPOSE` advertises human confirmation and is implemented as a different return value from `instructions()`; `save_learning` writes unconditionally. `optimize_memories` collapses every memory into one paragraph with `apply=True` by default |
| SimpleMem | [Reviewed](../content/systems/simplemem.md). Six headline figures, a reproduce section, and no `.json`/`.jsonl`/`.csv` file in the repository. The store's only removal verb is `clear()` |
| Pydantic AI Harness | [Reviewed](../content/systems/pydantic-ai-harness.md). The namespace is never a tool argument and the toolset raises if the backend returns a path outside the requested scope — the only scope *verification* in the atlas |
| CAMEL | [Reviewed](../content/systems/camel.md). `agent_id` on every record, applied on no read path; isolation comes from remembering to give each agent its own storage object |
| Microsoft Agent Framework | [Reviewed](../content/systems/agent-framework.md). `ContextProvider` declares no delete and no scope, a third contract from the same two vendors; the harness memory checks its owner boundary three ways |
| Membase | **No report.** No licence file at the pinned commit while the README states MIT and links to it. Its memory is covered ground; its signer-derived ownership is cited in the overview instead |

**The ranking held, and the reason it held is worth keeping.** Agno was ranked
first and produced the sharpest finding; Membase was ranked last with "low
expected yield" and produced no report. The ranking signal was not novelty or
popularity but *how much inspectable mechanism the description implied* — and
Membase's description implied a property of its backend rather than of its
memory, which is what "verifiable" turned out to mean.

**Five of the six ship two memory subsystems or none.** Agno has `memory/` and
`learn/`; SimpleMem has the text pillar and EvolveMem; Microsoft has the
contract and the harness memory. In each case the governance apparatus — the
scope key, the status field, the audit trail — is in the subsystem that is *not*
the one being benchmarked, packaged or documented. That pattern was not visible
from any single report and is the round's most useful observation.

## Still not done

- ~~**CrewAI** and **Haystack** remain the two named framework-native gaps~~ —
  **both closed on 2026-07-30.** CrewAI is [reviewed](../content/systems/crewai.md).
  Haystack turned out not to exist as a subject: `deepset-ai/haystack` has no
  agent memory, and the two things it calls memory stores are Mem0 and Cognee
  adapters living in a separate repository, both already in the atlas. The gap
  bullet had been naming an unreviewed thing that was not there.
- Nothing was run for any of the five. No suite was executed and no benchmark
  reproduced, including SimpleMem's, where the harness is committed and checking
  one figure is a bounded job.

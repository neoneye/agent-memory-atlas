# Twenty suggested systems, triaged

**Status:** triage recorded; no atlas content changed
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
| 3 | Membase | **New.** `unibaseio/membase` is real and open; axis is on-chain verifiability, not memory mechanism. Low expected yield |
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

Licences unchecked for all six; that is the first step of the
`add-memory-system` skill and not a triage question.

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

## Not done here

- The gap bullet at [overview.md:3646](../content/overview.md) still names only
  CrewAI, Semantic Kernel and Haystack. Adding Agno, and replacing Semantic
  Kernel with Microsoft Agent Framework, is a small published-content edit that
  has not been made.
- No repository in the six was cloned, pinned or read. This note is a triage of
  a list, not a review of anything.

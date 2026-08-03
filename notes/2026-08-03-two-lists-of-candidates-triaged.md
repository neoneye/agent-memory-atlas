# Two lists of candidates, triaged — and the recommendation points the wrong way

**Status:** triaged to a shortlist; no report written yet
**Origin:** two inputs submitted together on 2026-08-03 — a Grok assessment
naming three systems as "newer / not covered", and a raw GitHub search dump of
30 repositories created after 2026-02-03 matching *agent memory*. Checked
against the 133 reports in `content/systems/`.

Recorded because the two inputs disagree with each other about where the
interesting work is, and **the checkable evidence sides with the one that was
presented as noise.**

## The GitHub dump: 6 already reviewed, all 30 real

Matching on `source_url` against the corpus:

| Listed | Already in the atlas as |
| --- | --- |
| `TencentCloud/TencentDB-Agent-Memory` | [tencentdb-agent-memory](../content/systems/tencentdb-agent-memory.md) |
| `rohitg00/agentmemory` | [agentmemory](../content/systems/agentmemory.md) |
| `moorcheh-ai/memanto` | [memanto](../content/systems/memanto.md) |
| `akitaonrails/ai-memory` | [ai-memory](../content/systems/ai-memory.md) |
| `Gentleman-Programming/engram` | [engram](../content/systems/engram.md) |
| `Goldentrii/AgentRecall-X` | [agentrecall-x](../content/systems/agentrecall-x.md) |

**All 30 repositories exist**, verified by `ls-remote`. That is worth recording
against [the July Grok list](2026-07-30-twenty-suggestions-triaged.md), where
five of twenty were unreachable and had been for the third time. A search dump
is a different *kind* of input from a model's recollection: it cannot name a
repository that is not there. It also cannot tell you which ones matter, which
is the other half of this note.

Out of scope by kind, before any code was read — six of them are not memory
systems at all: `NirDiamant/Agent_Memory_Techniques` (tutorial notebooks),
`0xNyk/awesome-hermes-agent` (a directory), `VoltAgent/awesome-ai-agent-papers`
(a paper list), `memovai/mimiclaw` (an OS for microcontrollers),
`StarTrail-org/PixelRAG` (retrieval, nothing durable).
`OpenDataBox/MemoryData` is a **benchmark suite**, so if it earns anything it is
a row on the [benchmarks page](../content/benchmarks.md), not a report.

## The probe, and what it is not

Ten candidates were shallow-cloned and run through one uniform, cheap probe:
licence file, source lines excluding vendored trees, and how many source files
match three vocabularies — correction (`tombstone|supersede|retract`), scope
(`user_id|project_id|namespace|tenant|scope`), and committed test files.

**This is a triage instrument and not a reading.** A file matching `supersede`
may carry the word in a comment and nothing in the code; a system with no match
may implement correction under a name this probe does not know. Every number
below is a reason to look, never a finding. Two probes in this session returned
confidently wrong output before being control-tested — `timeout` does not exist
on this machine, so an existence check reported *every* repository missing
including `torvalds/linux`, and a zsh glob failure reported every candidate as
unlicensed. Both were caught by running a case whose answer was known. The
numbers below survived that treatment; they have not survived a code review,
because none has had one.

| Repository | Licence | Source | Correction | Scope | Test files |
| --- | --- | --- | --- | --- | --- |
| `fuyuxiang/echo-agent` | MIT | ~171k | **54** | 202 | **460** |
| `kitfunso/hippo-memory` | MIT | ~125k | **102** | 323 | **376** |
| `ZhangHanDong/mempal` | MIT | ~62k | 3 | 35 | 0 |
| `Agentscreator/engram-memory` | Apache-2.0 | ~52k | 16 | 60 | 47 |
| `LycheeMem/LycheeMem` | Apache-2.0 | ~28k | **0** | 9 | **1** |
| `sachinsharma9780/memweave` | MIT | ~18k | **0** | 4 | 49 |
| `ClaudioDrews/memory-os` | present | ~10k | 1 | 5 | 1 |
| `mcncarl/agent-memory-vault` | present | ~9k | 1 | 23 | 14 |
| `OPPO-PersonalAI/O-Mem` | present | ~4k | **0** | 5 | **0** |
| `Rotoslider/long-term-memory-mcp` | present | ~2k | **0** | **0** | **0** |

## The finding: the recommendation is inverted

Grok named three systems to "try" — LycheeMem, memweave, and
`long-term-memory-mcp` — and dismissed the search dump as "most high-star new
things are already in the Atlas".

Those three are **the bottom of this table on the axes this atlas judges by.**
Between them: zero files matching any correction vocabulary, and
`long-term-memory-mcp` matches nothing on scope either and ships no tests.
LycheeMem, the headline recommendation, has one test file against 28,000 lines.
They may still be good systems — memweave's *Markdown as the source of truth
with SQLite as a rebuildable index* is a shape this corpus has twenty instances
of and is a legitimate design — but they are recommended on ergonomics, and
ergonomics is not what this atlas measures.

Meanwhile the two strongest candidates by every signal here were **in the list
that was waved past**. `hippo-memory`'s own tagline is *"The secret to good
memory isn't remembering more. It's knowing what to forget"* — which is this
atlas's thesis, arrived at independently — with 102 source files touching
correction vocabulary and 376 test files. `echo-agent` describes four-layer
memory with forgetting and contradiction detection, and carries 460.

**And the recommendation cites stars.** LycheeMem is offered with "~1.2k stars"
attached. This atlas has a standing rule against adoption as evidence, and this
is now the third external instance of the inference the rule exists to prevent —
after [the Reddit star-velocity argument](2026-07-30-a-reddit-thread-triaged.md)
and the survey citations. It is the sharpest of the three, because here the
starred system is *demonstrably* the weaker candidate on mechanism, in the same
message, checkable in ten minutes.

## What to do, in order

1. **`kitfunso/hippo-memory`** — highest correction signal in the batch, MIT,
   heavily tested, and its stated thesis is deletion. If the mechanism matches
   the tagline this is a report; if it does not, that gap is itself the finding.
2. **`fuyuxiang/echo-agent`** — "forgetting and contradiction detection" is a
   claim about two of the atlas's seven columns. Largest codebase here.
3. **`sachinsharma9780/memweave`** — not for correction, but because
   Markdown-as-truth over a rebuildable SQLite index is the exact shape the
   [log-and-projection note](2026-08-03-the-log-and-the-projection.md) says the
   corpus blurs. A deterministic rebuild with no model in the replay path would
   be a clean second instance beside Daimon.
4. **`Agentscreator/engram-memory`** — note the name collision with
   [engram](../content/systems/engram.md) (`Gentleman-Programming/engram`),
   already reviewed and a different project. Anyone reconciling these lists by
   name rather than URL will merge them, which is the failure the
   [agentmemory collision](2026-07-29-memorypapers-against-the-atlas.md) already
   caused once.
5. **`LycheeMem/LycheeMem`** — worth a report despite the ranking, because
   *novelty is not a criterion* and a competent instance of a common design is
   evidence about the design. It should not be first.
6. **`ZhangHanDong/mempal`** — 62k lines of Rust with zero test files, which is
   either a wrong probe or the finding.

Not pursued here: `O-Mem` (research code, 4k lines, no tests — probably the
paper treatment rather than a report), `long-term-memory-mcp` (2.4k lines, no
scope, no tests), `memory-os` and `agent-memory-vault` (plausible, unremarkable
on every signal), and the eight remaining runtime-integration repos from the
dump, which look like harnesses rather than memory systems and were not cloned.

## What came of it

- **No report added.** This is a shortlist, not a review.
- **Six of thirty already covered**, and every one of the thirty reachable —
  the first candidate list submitted to this project with no dead entries.
- **One editorial rule corroborated for the third time**, and for the first time
  by a case where following the star count would have picked the weakest system
  in the batch on the atlas's own axes.
- **One name collision flagged** before it can merge two different projects.

# Nine repositories, triaged — and five of them carry no licence

**Status:** triaged; four candidates for review, five refused with reasons, no
report written
**Origin:** nine GitHub URLs submitted 2026-08-04. Checked against the 136
reports in `content/systems/`, then cloned and probed.

None is in the corpus. All nine exist, verified by `ls-remote` against a
`torvalds/linux` control — the second consecutive submission with no dead
entries.

## The ledger

| Repository | Lines | Licence | Outcome |
| --- | --- | --- | --- |
| `Prateek816/7layermem` | 7,016 | **none** | **Candidate** — "7-layer memory framework… persistent, structured long-term memory across conversations" |
| `RBKunnela/ALMA-memory` | 106,594 | **none** | **Candidate** — Agent Learning Memory Architecture, published to PyPI |
| `cognicore-dev/cognicore-my-openenv` | 79,439 | present | **Candidate** — "persistent, searchable memory"; the only in-scope one that is licensed |
| `deepractice/promptx` | 63,237 | present | **Needs one more look** — an "AI Agent Context Platform", but it ships a memory surface in the desktop app |
| `FalkorDB/falkordb` | — | — | Out of scope: a graph database, and already in the atlas as a *backend* to [Graphiti](../content/systems/graphiti.md) and [memary](../content/systems/memary.md) |
| `hshadab/kinic-api` | 310,328 | **none** | Out of scope: a client to a hosted service |
| `OmniNode-ai/onex_change_control` | 86,383 | present | Out of scope: governance, drift detection and enforcement — nothing durable carries a correctable identity |
| `Tufalabs/duck-harness` | 19,860 | **none** | Out of scope: an ARC-AGI-3 solver harness plus one committed benchmark run |
| `david-courtis/opine-world` | 15,502 | **none** | Out of scope on the evidence found: a world-model learner whose persistence hits are all in `docs/` site tooling |

## The two refusals worth stating

**`kinic-api` is the closed-service pattern again.** It presents as "The AI
Memory Layer for Multi-Agent Systems" with "persistent semantic memory", and the
repository contains **no local store at all** — no SQLite, no Chroma, no
`CREATE TABLE` in any Python file — while pointing at `kinic.io` and a hosted
front end. 310,000 lines of client and surface around a mechanism that is
somewhere else. This is the same refusal made for
[graperoot](2026-08-03-two-lists-of-candidates-triaged.md) and, before that, for
every hosted product: the atlas needs inspectable code at a pinned commit, and a
client is not the thing being reviewed.

**`FalkorDB` is infrastructure, not a memory system**, and the atlas has already
decided how to treat that layer. It is a graph database that two reviewed systems
mount as a backend, which puts it with pgvector, Chroma, Qdrant and LanceDB —
read for
[the layer below delete](../content/overview.md) as a shared dependency, not
given a report. Reviewing a database as a memory system would make the same
category error the corpus already avoids for vector stores.

## The finding: five of eight clones have no licence file

`7layermem`, `ALMA-memory`, `kinic-api`, `duck-harness` and `opine-world` carry
no `LICENSE` at the pinned commit. That is not a source-available licence being
restrictive; it is **no grant at all**, which defaults to all rights reserved.

The atlas's rule, stated in the `add-memory-system` skill, is that a restrictive
or source-available licence is a **caveat, not an exclusion** — BSL, ELv2,
PolyForm and "all rights reserved" are named in section 1 and the mechanisms are
still analysed. So the absence does not disqualify any of these, and two of the
three strongest candidates here are among them.

What it does mean is that section 1 of each report has to say so plainly, the way
[membase](../content/systems/membase.md)'s does — a README asserting MIT beside a
`LICENSE` file that is not in the tree is a fact a reader needs before they copy
anything. Worth recording as a rate: **five of eight** is high enough that the
report format's licence sentence is doing more work on new submissions than on
the established corpus.

## What to do, in order

1. **`cognicore-my-openenv`** — the only licensed in-scope candidate, and
   "persistent, searchable memory" is a direct claim on this atlas's axes.
2. **`7layermem`** — 7,016 lines is tractable in one pass, and a seven-layer
   scheme invites the question the atlas keeps asking of tiered designs: what
   promotes between them. Licence absence stated in section 1.
3. **`ALMA-memory`** — 106,594 lines and a PyPI release; the size means a
   capability pass before committing to a report.
4. **`promptx`** — resolve the scope question first. A context platform is out of
   scope; a context platform with a durable, correctable memory surface is not,
   and the desktop app contains a `memory` directory that decides it.

## What came of it

- **Four candidates**, one of them conditional on a scope question.
- **Five refused**, two on grounds the atlas has already written down (hosted
  service, storage engine) and three on the session-survival test.
- **All nine reachable**, the second such submission in two days.
- **One rate worth watching**: five of eight cloned repositories had no licence
  file, which is a caveat to state rather than a reason to skip.

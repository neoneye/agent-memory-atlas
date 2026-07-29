# The forgetting benchmark, found in a bibliography

**Status:** done; benchmarks.md §1, §6 and §7 updated
**Origin:** *From Storage to Experience: A Survey on the Evolution of LLM Agent
Memory Mechanisms*, [arXiv:2605.06716](https://arxiv.org/abs/2605.06716)
(v1, 7 May 2026, ACL 2026 Findings), and the paper its bibliography led to.
Read on 2026-07-29 as the third of the recent surveys checked against the atlas.

## The survey itself

Nine authors, 31 pages, with a maintained companion list at
[FeishuLuo/Evolving-LLM-Agent-Memory-Survey](https://github.com/FeishuLuo/Evolving-LLM-Agent-Memory-Survey)
(`92b5a4b1b25a02e3a053ed0309704e0ad31d3093`, 13 April 2026) — 140+ papers and
45 benchmarks. Its frame is developmental rather than taxonomic: **Storage**
(trajectory preservation) → **Reflection** (trajectory refinement) →
**Experience** (trajectory abstraction), with each stage motivated by what
defeats the previous one.

**It links no repositories.** The companion list is 466 lines of README and
three figures, and every entry points at arXiv, ACL or OpenReview. So the
instruction "check out the repos it links to" again has a short answer, and the
work was in the bibliography.

### The vocabulary result, for a third time

Counts over the extracted PDF, and over the companion README, on the atlas's
standard terms:

| Term | Paper (31pp) | Reading list |
| --- | --- | --- |
| `memory` | 346 | — |
| `forget*` | 7 | 1 |
| `audit*` | 3 | 0 |
| `contradict*` | 2 | 0 |
| `privacy` | 1 | 0 |
| `deletion` | 1 | 0 |
| `conflict` | 0 | 1 |
| `delete` / `tombstone` / `rejected` / `negative` / `unlearn*` / `provenance` / `governance` | 0 | 0 |

The single `forget` in the reading list is *forgetting risk* as a drawback of
parametric memory — catastrophic forgetting, not deletion. Its three `audit`
hits in the paper are all inside a cited title. This is the third independent
consolidated list, after Table 8 of
[arXiv:2512.13564](https://arxiv.org/abs/2512.13564) and the benchmark section
of [arXiv:2603.07670](https://arxiv.org/abs/2603.07670), whose vocabulary does
not contain the atlas's central mechanism. Three lists, ~90 distinct
benchmarks between them, and the union still contains no deletion-durability
test.

Which makes what turned up in the citations more interesting, not less.

## FiFA

One line of §7 on multimodal memory cites Alqithami 2025 on the difficulty of
adapting decay functions. The cited work is *Forgetful but Faithful: A Cognitive
Memory Architecture and Benchmark for Privacy-Aware Generative Agents*
([arXiv:2512.12856](https://arxiv.org/abs/2512.12856), 14 December 2025, single
author, Al-Baha University, 45 pages). It appears in **no** benchmark table in
any of the three surveys, including the one citing it.

Its privacy-preservation metric counts, as violations, "disclosing sensitive
tokens, retaining data beyond declared horizons, or **failing to honor deletion
preferences**", against opportunities that include "outputs **after TTL
expiry**". That is the question this atlas has said for eleven system reports
that nobody asks.

Its term profile is unlike anything else read here: privacy 211, forget 68,
audit 61, leak 34, delete\* 20, erasure 7, right-to-be-forgotten 7, GDPR 3,
unlearn 6. The 107-page field survey's corresponding numbers are 10, 52, 5, —,
2, 0, 0, 0, 0.

### Why it does not close the gap

Set out in [benchmarks.md §6](../content/benchmarks.md); the short form, in
increasing order of severity:

1. Three violation classes share one denominator, so no published number
   isolates deletion durability.
2. The subject is six eviction policies inside one architecture, in simulation —
   not memory systems. Deletion compliance rides along inside a capacity-management
   study.
3. PP did not discriminate: 0.722–0.780 across all five reported policies,
   `p = 0.485`, η² = 0.047. The paper explains why, candidly.
4. **No artifact, and an abstract that contradicts the results table.** The
   abstract reports Hybrid best at ≈0.911. Table 2, §6.5.1, §7.2 and §7.6 report
   Hybrid **last** of five at 0.589±0.009, behind Random-Drop at 0.635±0.024;
   §7.2 says "Hybrid does not win the aggregate". A footnote marks the sixth
   policy's row as pending. Goal completion is 0.058–0.078 across every policy.
   Forty-five pages describe version-locked code and archived artifacts; no
   repository is linked anywhere, and the public leaderboard is future work.

Point 4 is worth stating plainly because it is the atlas's own named
antipattern — published benchmark numbers without committed artifacts — showing
up in the evaluation literature rather than in a product README, and caught the
same way.

## What changed, and what did not

The claim in [benchmarks.md](../content/benchmarks.md) §1 and §6 was **"no
benchmark tests whether a deleted memory stays deleted."** It now names FiFA,
credits it with asking the question, and says why the answer is not yet
available. The conclusion is unchanged; the evidence behind it is much better,
because "nobody proposed it" and "one person proposed it and the number did not
work" are different states of a field and the second is the true one.

§7's contradiction-test specification now points a reader at FiFA's violation
taxonomy as a starting point rather than implying they must invent one.

No capability mark moved. FiFA describes an architecture (MaRS) with provenance
edges, sensitivity attributes, signed audit entries per mutation and an
`explain()` endpoint — on paper, four of the atlas's seven columns. With no
repository there is nothing to read, so it earns no report and no marks, and
the [scope rule](../content/overview.md) that produces that outcome is the same
one that excluded MemEngine.

## Two leads not followed

- **arXiv:2606.15903**, *Control-Plane Placement Shapes Forgetting: An
  Architectural Study of Agent Memory Across Thirteen System Configurations*.
  The title describes an experiment the atlas has effectively been running by
  hand across 73 reports. Surfaced while chasing FiFA; not read.
- **Minerva** ([arXiv:2502.03358](https://arxiv.org/abs/2502.03358)), listed in
  the companion list as "programmable memory read-write tests" — the only entry
  across ~90 benchmarks whose one-line description mentions write operations
  rather than question answering. Worth ten minutes before the next round of
  benchmark claims.

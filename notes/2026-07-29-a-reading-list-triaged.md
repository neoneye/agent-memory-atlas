# A recent-papers list, triaged end to end

**Status:** done
**Origin:** a nine-item list of "recent papers on agent memory systems"
(four surveys, four systems, one web resource), worked through on 2026-07-29 on
the instruction to check out the repositories each one links to. This note is
the ledger; the three substantive findings have their own notes.

## The ledger

| # | Item | Repos it links | Outcome |
| --- | --- | --- | --- |
| 1 | [arXiv:2512.13564](https://arxiv.org/abs/2512.13564) *Memory in the Age of AI Agents* | [Agent-Memory-Paper-List](https://github.com/Shichun-Liu/Agent-Memory-Paper-List) | Already processed 2026-07-29; re-checked, nothing new |
| 2 | [arXiv:2603.07670](https://arxiv.org/abs/2603.07670) *Memory for Autonomous LLM Agents* | none | Two benchmarks read; [benchmarks.md](../content/benchmarks.md) §2 and §6 changed — [note](2026-07-29-selective-forgetting-that-is-not.md) |
| 3 | [arXiv:2605.06716](https://arxiv.org/abs/2605.06716) *From Storage to Experience* | [Evolving-LLM-Agent-Memory-Survey](https://github.com/FeishuLuo/Evolving-LLM-Agent-Memory-Survey) (no code) | FiFA found in its bibliography; the forgetting claim was corrected — [note](2026-07-29-the-forgetting-benchmark-in-a-bibliography.md) |
| 4 | [arXiv:2604.16548](https://arxiv.org/abs/2604.16548) *Long-Term Memory Security* | [OWASP Agent Memory Guard](https://github.com/OWASP/www-project-agent-memory-guard) | Read and excluded with reasons; [overview.md](../content/overview.md) correction and scope sections changed — [note](2026-07-29-security-research-names-the-column.md) |
| 5 | [arXiv:2504.19413](https://arxiv.org/abs/2504.19413) Mem0 | `mem0ai/mem0` | Pinned, [reviewed](../content/systems/mem0.md) 2026-07-26 |
| 6 | [arXiv:2502.12110](https://arxiv.org/abs/2502.12110) A-MEM | `agiresearch/A-mem` | Pinned, [reviewed](../content/systems/a-mem.md) 2026-07-27 |
| 7 | [arXiv:2507.03724](https://arxiv.org/abs/2507.03724) MemOS | `MemTensor/MemOS` | Pinned, [reviewed](../content/systems/memos.md) 2026-07-26 |
| 8 | [arXiv:2501.00663](https://arxiv.org/abs/2501.00663) Titans | none official | Out of scope; now named in the scope section |
| 9 | [memorypapers.org](https://memorypapers.org) | HippoRAG, Mem0, MemOS | **This row was wrong** — it rested on one landing-page fetch. Re-read properly: 200 papers, a security category, one published finding and one outstanding report — [note](2026-07-29-memorypapers-against-the-atlas.md) |

All nine items verified to exist. The three surveys dated after this atlas's
previous survey pass are real papers, not artifacts of the list.

## The headline result: four surveys, one repository between them

Items 1–4 are 200-odd pages of survey with maintained companion lists, and they
link **one** repository that is not a reading list: the OWASP guard, from the
security paper. Items 5–7 are system papers whose repositories were already
pinned and read this week.

**So the exercise added no system report, and that is the finding.** The
[previous survey pass](2026-07-29-memory-survey-forms-functions-dynamics.md)
mined a framework *table* and got nine reports out of it. These four surveys
have no framework table between them — they cite papers. A reading list
assembled from recent arXiv activity and a reading list assembled from
inspectable code have almost no intersection, and the [editorial
backlog](2026-07-28-editorial-backlog.md) §3 argument against adding breadth
was, this time, answered by the material itself rather than by restraint.

What the four surveys did produce is three corrections to published atlas
claims, which is a better return per hour than nine reports were.

## What each one cost, and returned

Recorded because the [previous pass](2026-07-29-memory-survey-forms-functions-dynamics.md)
recorded the same and the comparison is the useful part.

- **Item 2** — no repos, so the checkable thing was a benchmark claim. Two
  clones, one HuggingFace query, ~1 hour. Returned: the benchmark two surveys
  call *selective forgetting* is named conflict resolution in its own repository
  and keeps both values in the store.
- **Item 3** — no repos. The return came from a bibliography line, not from the
  survey. ~1.5 hours. Returned: a paper that does score deletion compliance, an
  abstract that contradicts its own results table, and a claim on this atlas's
  benchmarks page that needed correcting rather than defending.
- **Item 4** — one repo, read in full. ~1.5 hours. Returned: four capability
  columns independently derived from threat models, a formal definition of
  deletion durability better than the atlas's own, and a project that implements
  four of five governance primitives while quarantining rejected values into a
  dict nothing reads.

Items 1 and 5–9 cost about twenty minutes in total and returned confirmation
that no work was outstanding.

## The pattern worth keeping

Each of the three findings came from the same move: **take the strongest claim
in the paper that could be checked against an artifact, and check it.**

- "Only MemoryAgentBench tests selective forgetting explicitly" → read the
  config directory.
- "The Hybrid policy delivers the best composite performance (≈0.911)" → read
  Table 2.
- "Verified Forgetting: no existing literature" → read the repository the paper
  links, and find the quarantine.

None of the three required reading the paper closely. All three required
reading something the paper points at. That is the same discipline the atlas
applies to a README's feature list, moved up a level, and it worked three times
out of four.

## Open, and now recorded

- ~~**MemMachine is unreviewed and in scope**~~ — **done**, same day, at
  `a681abf9623299bba8ad931e5d9af02fb6ef0997`. Found on the re-read of item 9,
  which this note originally dismissed in one line, and the only system report
  this round generated. See
  [the memorypapers note](2026-07-29-memorypapers-against-the-atlas.md).
- ~~**Substrate coverage in the deletion test.**~~ **Made on 2026-07-30.** The
  test now runs to thirteen steps: share, export or sync the memory to a second
  scope *before* deleting it, delete the original, and assert it is not
  retrievable from the second scope either. The section explains why this is a
  different surface from step 9 rather than more of it — a derived artifact is
  downstream of the original and can be invalidated by tracking what it came
  from, while a propagated copy is a *peer* with its own identity and usually no
  back-reference, so a deletion has nothing to follow. Three grounded instances
  cover the range: SimpleMem's `share` mints a fresh uuid and copies the content
  with no link to the source memory (the link exists only as a detail string in
  an event log its own write path never consults), Cortex's `shared_context` is a
  publication nobody owns, and NemoClaw's snapshot makes propagation
  bidirectional — the deleted value comes back. On the atlas's current reading
  nothing would pass steps 11–13.
- ~~**[arXiv:2606.15903](https://arxiv.org/abs/2606.15903)**~~ — **read
  2026-07-30, and it was the highest-yield item on any list this project has
  triaged.** It releases code under MIT, which none of the nine items in this
  note's ledger did. The artifact is two things at once: a memory system,
  [Lethe](../content/systems/lethe.md), built around the control plane instead
  of the recall plane and able to issue an Ed25519 receipt over a Merkle root of
  its event log — Verified Forgetting implemented, which the security survey had
  marked *"no existing literature"* — and **ForgetEval**, 385 adversarial cases
  scoring `supersede`, `release` and `purge` across six systems, five of them
  already in the atlas. The benchmarks page had said for five months that nothing
  measures whether a deleted memory stays deleted; that claim is now dated and
  narrowed. Checking it also found one wrong row: ForgetEval scores MemPalace
  0/385 on a docstring asserting it "does NOT support delete", and MemPalace's
  MCP server exposes `delete_drawer`, `delete_by_source` and `delete_hallway` at
  its pinned commit.

  The lesson for this ledger is worth keeping. The rule the note derived — that
  surveys and reading lists have almost no intersection with inspectable code —
  held for nine of nine items and then failed on the tenth, which was a *systems*
  paper filed among them. The discriminator was never "paper versus repository";
  it was whether the artifact section names a licence.
- ~~**Minerva** ([arXiv:2502.03358](https://arxiv.org/abs/2502.03358))~~ —
  **read 2026-07-30, and out of scope.** *Minerva: A Programmable Memory Test
  Benchmark for Language Models* (Xia, Ruehle, Rajmohan, Shokri; Microsoft and
  NUS, Feb 2025) automatically generates tests for how well a **model** uses its
  context: searching, recalling, editing, matching, comparing, operating on
  structured blocks, and maintaining state. The "write operations" that put it on
  this list are edits *within a prompt*, not mutations of a durable store — there
  is no memory system under test, no retrieval layer and nothing that survives a
  session. It is a context-manipulation benchmark for LLMs, which is a real and
  useful thing and not what this atlas's benchmarks page is about. No repository
  URL was found on the abstract page. The catalogue entry that flagged it
  described it accurately; the word *editing* was doing the misleading.
- **Parametric memory** remains one report deep, and Titans is now named in the
  scope section as the architecture-level case rather than left implicit.

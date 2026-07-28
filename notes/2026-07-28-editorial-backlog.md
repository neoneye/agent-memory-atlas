# Editorial backlog — work on existing content

**Status:** open
**Origin:** accumulated from reviews on 2026-07-28 plus the first freshness run.

## 1. Prose de-duplication across the 46 older reports

Sections 11, 12 and 13 were merged into one — `## 11. For Your Own Build` with
`### Steal`, `### Avoid`, `### Fit` — across all reports on 2026-07-28. The
**structure** is uniform. The **prose** is not: the older reports still restate
themselves under the new subheads, because the merge preserved content verbatim.

The specific symptom: `### Fit` frequently opens with "Borrow:" followed by a
list that repeats `### Steal`. The format spec now says outright — "if Fit reads
as a summary of Steal and Avoid, delete it and write the judgement instead" —
and roughly 46 reports predate that instruction.

**Why it was not done at the time:** 46 judgement calls, and doing six well while
leaving forty in a different voice trades a structural inconsistency for an
editorial one. It needs to be one pass or none.

**Measure of done:** no `### Fit` section contains a bulleted list of mechanisms.
Fit is a judgement about maintenance budget, scale, deployment, and who should
walk away.

## 2. A Measured / Claimed / Not-measured axis

Proposed as a column on the capability index. The distinction is real and the
atlas already makes it in prose — "published benchmark numbers without committed
artifacts" is a named antipattern with several instances, and Memvid is the
loudest current case.

**Not done because** it is 56 fresh judgements on a dimension never assessed
uniformly, and retrofitted classification is exactly where this atlas has been
caught twice. If it ships, it ships like the other seven: one strict definition,
applied deliberately per system, drift-checked by the build. Not filled in from
memory.

## 3. Re-analysis priority, from the first freshness run

`scripts/check_freshness.py`, first run 2026-07-28: **34 current, 22 stale**.

These are a snapshot and they move. Two runs an hour apart on the same day
differed by six commits on `openclaw` and seventeen on `hermes-agent`, which is
the point of the tool rather than a defect in it — the ordering below is stable
even though the counts are not, so treat the numbers as magnitude and the rank
as the work list.

Priority is not simply "most commits behind" — it is **how load-bearing the
report is** multiplied by drift:

| System | Commits since pin | Why it matters |
| --- | --- | --- |
| ~~`verel`~~ | — | **Done 2026-07-28**, after its author pointed out the report was out of date. The pin turned out to be *orphaned*, not merely old, and the re-read moved Verel from three of seven capabilities to all seven — the first system in the atlas to carry them all. Two atlas-wide counts changed as a result. |
| `rainbox` | ~163 | The author's own system, and the other tombstone holder. Same load-bearing problem, plus the self-assessment framing makes staleness worse. |
| `openclaw` | ~409 | Largest drift in the atlas; a host runtime several other reports reference. |
| `hermes-agent` / `holographic` | ~234 each | Two reports over one repository, so one re-read updates both. |
| `mem0` | ~108 | Most widely adopted system here; the report is the one most likely to be read. |
| `mempalace` | ~99 | Cited repeatedly for evidence-before-belief. |

The rest — supermemory (66), mastra (39), engram (38), honcho (36),
basic-memory (27), hindsight (16), graphiti (14), openviking (9), langmem (8),
memory-engine (7), memos (4), nanobot (2), pi (2), letta (1), waku-agent (1) —
are ordinary drift and can wait.

**A pin can be worse than stale.** Verel's was unreachable from any branch —
GitHub still served it by SHA, so the freshness tool reported it as 324 commits
behind rather than as describing a state absent from the project's history.
`check_freshness.py` now distinguishes the two, because only one of them means
"the report may be describing something that never shipped".

**Note the asymmetry:** a drifted pin does not make a report wrong. The report was
true of that commit and still is. It makes the report less useful as a
description of the project today, and the two tombstone reports are the ones
where "less useful today" is most costly.

## 4. Small things

- The `key` column in OpenWorker's schema is unused — noted in its report as an
  open question, worth confirming if the repository moves.
- `beads` and `GAM` are named in the scope section rather than given reports. If
  either changes character — beads growing a belief model, GAM gaining a licence
  and a mechanism — the decision should be revisited rather than inherited.

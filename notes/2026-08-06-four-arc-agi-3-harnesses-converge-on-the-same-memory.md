# Four ARC-AGI-3 harnesses, independently, put the log in charge and the notes on probation

**Status:** done — examined 2026-08-06, no reports, recorded in the overview's
scope section
**Origin:** three repositories linked from the
[VISTA page](2026-08-06-a-harness-whose-traces-are-published-and-whose-code-is-not.md),
submitted 2026-08-06

| Project | Pin | Lines | Licence | Headline claim | Verifiable how |
| --- | --- | --- | --- | --- | --- |
| **Tycho** (NIMI-research) | `f68912a764372ead0a610db2e1c011d41ce5197e`, 29 July 2026 | 24,829 Py | Apache-2.0 | RHAE 100.00 on all 25 public games | **Six official ARC Prize scorecard links**, plus manifests in `artifacts/` |
| **Retrodict** (ryanbbrown) | `633376beb3ee5ca838a7c20bfd163396bc7891b3`, 20 July 2026 | 3,888 Py | **none** | 99.86% mean RHAE, all 25 solved, $654 | **Official competition-mode scorecard**, plus `docs/official-scorecard-8d734689.json` and per-game cost tables |
| **Schema** (Impossible Research · Berkeley · CMU) | project page only | — | **none** | *"~99% on ARC-AGI-3 Public"* | Embedded traces in a 6.3 MB page; **no official scorecard link** |
| **VISTA** (MIT) | page + replays, 6 Aug 2026 | — | — | 25/25, RHAE 100 | 320 MB of committed per-game run traces |

## The call: no reports, all four

None of them stores memory that outlives the session, where the session is one
game run. Checked individually rather than assumed by family resemblance:

- **Tycho** — `tycho/workspace/workspace.py` opens with *"Tycho's per-game
  on-disk working memory."* `__init__` takes `root` and does
  `base = Path(root) if root else Path(tempfile.mkdtemp(prefix="arcws_"))`,
  then `if root and not resume and self.dir.exists(): shutil.rmtree(self.dir)`.
  A default run gets a temp directory; a named root is wiped at startup. The one
  survival path is `resume=True`, which *"restores the complete committed
  directory"* byte-exact — continuation of the same run after interruption, not
  memory carried into a new one.
- **Retrodict** — `src/arc3/runner.py:693` does
  `shutil.copytree(WORKSPACE_TEMPLATE, workspace, dirs_exist_ok=True)` into
  `run_dir / "workspace"`. Every run starts from the same empty template.
- **Schema** — no source at any commit; the only repository in either
  organisation is the project page, which is three files.
- **VISTA** — no source; and across all 25 published traces, zero first
  `GUIDE.md` writes reference another game.

Tycho is the closest to the line and deserves the caveat stated plainly: it has
**more memory machinery than several systems that do have reports here** — an
on-disk store, agent-owned belief files (`notes/actor_beliefs.md`,
`world_model.md`, `level_L_insights.md`), an `attempts/level_N_attempt_M/`
archive described as an *"immutable prior-attempt observation root"*, and
`WorkspaceVersionStore`, which takes *"exact, content-addressed snapshots of
agent-controlled workspace state."* Content-addressed snapshots of the agent's
own beliefs is a mechanism this atlas would mark if it survived the run. It does
not, and that is the only reason there is no report.

## The finding: convergent memory architecture

Four teams — MIT, an ARC-focused lab, an independent author, and an
Impossible/Berkeley/CMU group — built harnesses for the same benchmark and
arrived at the same two-part memory, apparently without copying each other:

| | Ground truth (append-only, not model-authored) | Belief cache (model-authored, rewritten) |
| --- | --- | --- |
| VISTA | Every returned frame at full resolution, indexed by turn | `GUIDE.md` (rules) + `WORKING.md` (scratch) |
| Tycho | Per-turn grid text, PNG, JSON, exact cell diffs, death evidence | `notes/actor_beliefs.md`, `world_model.md`, per-level insights |
| Retrodict | `log.txt` — every frame, with a derived `[DIFF]` line per step | `playbook.md` — working model + working memory |
| Schema | An append-only `Timeline` / `events.jsonl` | `world_model.py` + `notes.md` |

**The shared invariant is that the model's own summary is explicitly
subordinate to the record.** Each project says so in its own words. Retrodict's
prompt tells the agent to mark each point *"checked against the log vs. still
assumed"*, not to build multi-step plans on merely-assumed points, and that
*"the log stays ground truth"*. Tycho's README: *"checks the hypothesis against
experience."* Schema: *"`run_backtest` checks each candidate rule against the
entire record rather than relying on recollection"*, and — the sentence that
names the mechanism — *"because the record survives both bounded working memory
and the auto-compacted context window, the certified model can be trusted in
place of further real-environment testing."* VISTA's table gives the same
property as a column: written notes lose *"everything not written down; the
model chooses what to drop"*, where the frame store loses *"nothing"*.

**This inverts what most of the atlas does.** The dominant pattern in
`content/systems/` is to extract beliefs from the transcript and then discard or
demote the transcript: the extracted fact is the memory, and the raw material is
storage overhead. These four do the opposite — the raw record *is* the memory,
retrieval is the model deciding which part of it to bring back, and the
distilled beliefs are a cache that may be wrong and is expected to be
re-derivable. [MemPalace](../content/systems/mempalace.md) is the atlas's
closest existing instance of the same instinct, making verbatim evidence primary
and derived structures indexes.

Why the pressure produced it here is not mysterious, and it is the transferable
part: in ARC-AGI-3 the environment is cheap to record, exactly reproducible, and
the *only* source of truth, while every belief the agent holds was invented by a
model that has been wrong before. Under those conditions, keeping the record and
distrusting the summary is simply correct. The question the atlas should carry
forward is which of those conditions hold for ordinary agent memory — the
transcript is cheap to record there too, and the extracted fact is no more
trustworthy.

**And the correction semantics come free from the same choice.** A falsified
rule in Retrodict is deleted from `playbook.md` and the log is unaffected; the
next session re-derives from the log rather than inheriting the error. No
tombstone is needed because the belief layer is disposable and the ground truth
is immutable. That is a real answer to the atlas's central complaint, available
only to systems whose ground truth is replayable — which is exactly what an
interaction log with a deterministic environment is, and exactly what a
conversation with a person is not.

## Verifiability: the same four, ranked

The spread here is wider than the mechanism spread and is worth recording
because ARC-AGI-3 offers something most benchmarks do not — a **third-party
scorecard**, issued by the ARC Prize server in competition mode, that the author
does not control.

- **Tycho** publishes six of them, one per policy/model configuration, including
  its two 100.00 runs, plus the ablation ladder that produced them (79.07 with
  no world model, 85.36 single actor model, 88.49 actor-controlled builder).
  Publishing the configurations that scored *worse* is the ablation discipline
  the atlas credits [memsem](../content/systems/memsem.md) for.
- **Retrodict** publishes one official scorecard and commits the JSON, plus
  per-game cost tables and a comparison against the previous best that links
  *that* system's scorecard too. It also reports what it lost on: 23 of 25 games
  perfect, sk48 at 98.64%, sp80 at 97.77%. Naming your two worst games is not
  common.
- **VISTA** publishes no scorecard and 320 MB of run traces instead — from which
  the claim recomputes exactly (25/25 `WIN`, every `score: 100`).
- **Schema** publishes neither. Its page carries embedded interactive traces and
  cites the ARC Prize launch blog, the technical report and a GPT-5.6 results
  page — but **no scorecard for its own runs**, and no source. Of the four it is
  the only one whose headline number rests on its own account of itself.

That Schema is also the only one of the four with named institutional
affiliations across three universities and a company is worth noting without
drawing a moral from it. Provenance of authorship is not evidence; a scorecard
id is.

## Smaller observations

- **Retrodict has no licence file** — all rights reserved by default — despite
  being the most thoroughly documented of the three repositories. Recorded the
  same way as OptMem and Nova AI: a caveat for a reader, not a reason to skip
  the reading.
- **Tycho is one squashed commit** (152 files, 29 July 2026), so its development
  history is not inspectable. The artifacts directory compensates.
- **Retrodict's containment check is a mechanism worth stealing outright.** The
  agent's Python runs in a venv with no game-engine packages, and *"every run
  writes a `containment.json` proving the engine imports fail, and aborts if
  they don't."* An agent that could import the game could read the answer; this
  turns "we didn't cheat" from an assurance into a per-run artifact. The atlas
  has no other instance of a self-proving negative capability check.
- **Retrodict ships `AGENTS.md` and `CLAUDE.md`**, both flagged by the screen as
  instructions addressed to a reading agent. Read as data, not followed.
- **Tycho's grid format carries a measurement.** A comment records token cost
  per format against a real 64×64 frame — dense 0.51×, spaced 1.0×,
  spaced_rownum 1.04×, spaced_grid8 1.09×, json 1.51× — and picks
  `spaced_grid8` for +9% tokens because row numbers and a `|` every 8 columns
  *"directly mitigates the grid-disorientation we observed."* A serialization
  choice with a measured cost and a named failure it prevents.

## What this taught the method

**A benchmark that issues third-party scorecards makes a whole family of claims
checkable at zero cost to the reader**, and the atlas should look for that
before reaching for its usual "no committed artifact" finding. Three of these
four could be verified in minutes without cloning anything, because the ARC
Prize server holds the result and the author cannot edit it. Most of the
memory-benchmark claims this atlas has had to record as unverifiable — LoCoMo,
LongMemEval, MemoryBench figures — are self-reported against datasets anyone can
score themselves, with no neutral party holding the outcome. The difference is
not the rigour of the projects; it is the existence of a scorekeeper.

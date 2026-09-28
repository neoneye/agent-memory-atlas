# Unreleased code watchlist

Items this atlas examined while their code, the part of the code that holds
the memory, or the paper was not public. Most come from the *Known
Limitations* section of `content/appendix.md`; a few are system reports that
name a missing component. Compiled 2026-09-28. Every link below returned 200
on that date unless the entry says otherwise, and every status line records
what was checked on that date. Re-run the commands under
[How to check](#how-to-check) to refresh it. An item whose code appears
moves to *Code now available*, which is a queue for re-examination, not a
verdict: a released tree still goes through `screen-repository` and the
rubric.

Each entry says whether a release would reopen the call. Where the bullet
excluded the item on a second, independent ground (the memory lives inside
one run, or is a training-time artifact), a release would not change it, and
the entry says so.

## Code now available

**VISTA** — a visual harness for ARC-AGI-3 from MIT with a lossless frame
store and two model-authored notes files.
- Examined 2026-08-06; `content/appendix.md`, bullet opening
  "`vista-research.github.io` was examined and has no report".
- Missing then: all harness source; only the project page and run traces
  were public.
- Now: [joshhhhhan/VISTA](https://github.com/joshhhhhan/VISTA), MIT, one
  commit "Initial release" on 2026-09-05, linked from
  [the project page](https://vista-research.github.io/). It holds
  `src/vista_arc3/` with Claude and Codex controllers, harnesses, runners,
  tools and an MCP bridge, a compact hook, and `tests/` (54 blobs in all).
- The bullet's second ground — the memory does not outlive the run — was
  established from the traces, so the code is a check on that finding rather
  than an automatic report.

**THREADS reasoning engine** — an engine described as versioned events with
positive and negative evidence kept apart, provenance and contradiction.
- Examined 2026-09-07; bullet opening "One repository examined in the same
  round has no report. `rickey1990/THREADS-reasoning-engine`".
- Missing then: the `source/` and `benchmarks/` directories the test runner
  calls, absent from all five commits.
- Now: [rickey1990/THREADS-reasoning-engine](https://github.com/rickey1990/THREADS-reasoning-engine)
  has nine commits, the last on 2026-09-12. `source/srmh/` holds `engine.py`,
  `evidence.py`, `ledger.py`, `search.py`, `algebra.py`, `compiler.py`,
  `language.py` and `numeric.py` (about 40 KB of Python), with
  `source/tests/` and four scripts under `benchmarks/`. GitHub reports the
  licence as `NOASSERTION`; the tree carries `LICENSE-CODE.txt`,
  `LICENSE-DOCUMENTATION.txt` and `LICENSING.md`, and the bullet recorded
  PolyForm Noncommercial and CC BY-NC.

**Harness-of-Harness (HoH-lite)** — an outer planner, developer and QA loop
around an existing coding-agent harness
([arXiv:2609.01481](https://arxiv.org/abs/2609.01481), v1).
- Examined 2026-09-05; bullet opening "[`arXiv:2609.01481`](https://arxiv.org/abs/2609.01481) was examined and
  has no report: the repository it links holds a README and assets".
- Missing then: HoH-lite, which the README promised.
- Now: [Flesymeb/HarnessOfHarness](https://github.com/Flesymeb/HarnessOfHarness)
  (MIT) added `hoh-lite/` in commit "Add HoH-lite release source and
  documentation" on 2026-09-23: 60 Python files including
  `src/gameloop/core/evidence.py`, `loop_engine.py`, `roles.py`,
  `mcp_evidence.py`, harness adapters for Codex, OpenCode, Pi and DeepSeek,
  and a GameCraft-Bench adapter. The bullet named the evidence bundle as the
  first thing to read.
- The bullet's own finding is that continuity is the project's files and
  history, not a memory module, so this may confirm the exclusion.

**eMEM** — a hybrid spatio-temporal memory for embodied agents
([arXiv:2606.03374](https://arxiv.org/abs/2606.03374), v2).
- Examined 2026-09-05; bullet opening "Nine spatial-memory repositories for
  robots were examined in one round".
- Missing then: the paper names `automatikarobotics/emem`, which returned
  404 and still does.
- Now: [automatika-robotics/emem](https://github.com/automatika-robotics/emem)
  (MIT, created 2026-03-07, last push 2026-05-22) describes itself as a
  graph-based spatio-temporal memory for embodied agents and holds
  `emem/store.py`, `memory.py`, `consolidation.py`, `working_memory.py`,
  `spatial.py` and `tools.py`, a `harness/`, and eMEM-Bench paradigms. The
  organisation name in the paper lacks the hyphen; the code was public
  before the examination under the correct name.

**EmbodiedLGR** — lightweight graph representation and retrieval for
semantic-spatial memory on ROS2 robots
([arXiv:2604.18271](https://arxiv.org/abs/2604.18271), v2).
- Examined 2026-09-05; bullet opening "Seven spatial-memory papers from the
  same search have no repository to pin".
- Missing then: no URL in the paper.
- Now: [paolorv/lgr-agent](https://github.com/paolorv/lgr-agent)
  (Apache-2.0; created 2025-11-19, last push 2026-04-10), whose README title
  is the paper's title; Paolo Riva is the paper's first author. It holds a
  captioner server, a `remembr/` agent tree and evaluation scripts
  (214 code files). Public before the examination.

**FARM** — relational spatial memory for finding objects
([arXiv:2606.15476](https://arxiv.org/abs/2606.15476), v3).
- Examined 2026-09-05; same bullet as EmbodiedLGR.
- Missing then: the paper links a project page and no code.
- Now: [the project page](https://goldengait.github.io/farm/) links
  [GoldenGait/FARM-Project](https://github.com/GoldenGait/FARM-Project)
  (AGPL-3.0, one commit "FARM: initial public release" on 2026-07-28): a ROS
  mapping package with `lib/persistence.py`, `lib/scene_graph_io.py`, a
  `streaming_mapper` node and evaluation scripts. Public before the
  examination, one hop from the paper.

**Agent Memory Distillation** — teacher trajectories distilled into
workflow, subtask and function memory for small student agents
([arXiv:2608.07169](https://arxiv.org/abs/2608.07169), v1).
- Examined 2026-08-15; bullet opening "[`arXiv:2608.07169`](https://arxiv.org/abs/2608.07169) was examined and
  has no report: it is a memory *method* with no released implementation".
- Missing then: no code URL in the paper, which is still true of v1.
- Now: [the project page](https://agent-memory-distillation.github.io/)
  links [taeilkim2465/agentic_memory_distillation](https://github.com/taeilkim2465/agentic_memory_distillation)
  (created 2026-06-18, last push 2026-08-10, **no licence file**). It holds
  AppWorld, BFCL and ToolSandbox trees with memory builders and stores, and
  BFCL scripts named `exp_2_workflow.sh`, `exp_3_workflow_func.sh` and
  `exp_4_workflow_func_subtask.sh` — the paper's three tiers. Its README
  frames the methods as ReasoningBank, MEMP and SASM. Public before the
  examination.

**OmniIntelligence's framework dependencies** — the `omnibase` framework
beneath a reported system.
- Recorded in `content/systems/omniintelligence.md` (analysed 2026-09-19),
  which calls the framework "three private repositories".
- Now: [OmniNode-ai/omnibase_core](https://github.com/OmniNode-ai/omnibase_core),
  `omnibase_infra`, `omnibase_spi`, `omnimarket` and
  [onex_change_control](https://github.com/OmniNode-ai/onex_change_control)
  all report `public`, and `omnibase_core` answers 200 unauthenticated.
  At the report's pin, `pyproject.toml` depends on `omnibase-core` by
  version range, and its comments say the git-rev overrides for
  `omnibase-core` and `omnibase-infra` were removed on 2026-08-20 and
  2026-08-21, before the pin. The report's claim needs re-checking at the
  pin; when the repositories became public was not established.

**CSM's living-mind service (candidate)** — the "cortex" that CSM's
`CSM_LIVING_MIND_URL` hook consumes.
- Recorded in `content/systems/csm.md` (analysed 2026-09-18): "the service
  is not in this repository".
- Now: the same author publishes
  [NovasPlace/living-mind-cortex](https://github.com/NovasPlace/living-mind-cortex)
  (created 2026-04-06, last push 2026-08-06, no licence file), a local
  memory backend with a hormone bus and `state/circadian.py` — the
  vocabulary of the contract the report describes — and 105 code files.
  That it is the service the hook points at is inferred from the vocabulary
  and the author, not from CSM's code.

## Still unreleased

### Research code and papers, by examined date

**neo Memory Core** — the "Memory Core" documented in `neomjs/neo`'s AgentOS
material.
- Examined 2026-07-27; bullet opening "Five further repositories examined in
  this round have no reports: `he-yufeng/CoreCoder`".
- Missing: any implementation; the documents describe it.
- Monitor: [neomjs/neo](https://github.com/neomjs/neo).
- Status 2026-09-28: default branch `dev`, pushed today; the untruncated
  tree (27,974 paths) still has exactly three paths matching `memory`:
  `learn/agentos/SeatMemoryLayer.md`, `resources/content/concepts/memory-core.md`
  and a Playwright memory-leak spec. Nothing under `src/`.

**Mi-Memory** — a lifecycle memory framework for personal AI
([arXiv:2607.18975](https://arxiv.org/abs/2607.18975), v1).
- Examined 2026-07-28; bullet opening "Nothing was run for the six systems
  added in this round. OptMem is reviewed".
- Missing: implementation; the repository is a paper PDF and a landing page.
- Monitor: [Darwin-Agent/Mi-Memory](https://github.com/Darwin-Agent/Mi-Memory),
  [project page](https://darwin-agent.github.io/Mi-Memory/),
  [Darwin-Agent](https://github.com/Darwin-Agent).
- Status 2026-09-28: six commits, last 2026-08-19 ("move pdf to root");
  14 blobs, none of them code — `paper.pdf`, a `MemFuse/` PDF with a
  benchmark JSON, figures, `index.html`. The arXiv v1 comment links only the
  project page. If released: in scope as described.

**elizaOS/agentmemory** — listed as an open-source memory framework in the
table of *Memory in the Age of AI Agents*
([arXiv:2512.13564](https://arxiv.org/abs/2512.13564)).
- Examined 2026-07-29; bullet opening "`elizaOS/agentmemory` is listed as a
  representative open-source memory framework".
- Missing: the repository; the URL returns 404.
- Monitor: [elizaOS](https://github.com/elizaOS).
- Status 2026-09-28: `repos/elizaOS/agentmemory` still 404.

**Schema harness** — an ARC-AGI-3 harness from Impossible Research,
Berkeley and CMU.
- Examined 2026-08-06; bullet opening "Three further ARC-AGI-3 harnesses were
  examined alongside VISTA".
- Missing: source at any commit.
- Monitor: [schema-harness.github.io](https://schema-harness.github.io/),
  [traces dataset](https://huggingface.co/datasets/schema-harness/arc-agi-3-schema-traces).
- Status 2026-09-28: the `schema-harness` GitHub account has one repository,
  the project page; the page links only the Hugging Face dataset. A search
  finds `Erikiss/Rebuild-schema-harness-by-impossible-research`, a third
  party's rebuild. If released: would not change the call (the bullet
  judged the memory per run, like the other three).

**Memory Reward Inflation in Self-Improving LLM Agents** — the Echo Gap
measurement and the LUCID de-inflation detector
([arXiv:2608.00017](https://arxiv.org/abs/2608.00017), v1).
- Examined 2026-08-10; bullet opening "[`arXiv:2608.00017`](https://arxiv.org/abs/2608.00017) was examined and
  has no report, and the reason is that its own advertised repository does
  not exist".
- Missing: code, data and per-episode memory traces the paper says are
  released.
- Monitor: [the author's account](https://github.com/MohammadAsadolahi).
- Status 2026-09-28: still v1; the paper's URL,
  `github.com/MohammadAsadolahi/Reliable-Memory-Agents-in-the-Wild`, returns
  404; the account has 49 public repositories, the newest created
  2026-09-16 and unrelated. If released: a report, per the bullet.

**Weighted Memory Tree** — a retention-scored memory tree with a four-value
lifecycle state for long-horizon agents
([arXiv:2608.20631](https://arxiv.org/abs/2608.20631), v1).
- Examined 2026-08-26; bullet opening "`Weighted Memory Tree` was examined
  and has no report: no repository".
- Missing: code and dataset.
- Monitor: the arXiv page.
- Status 2026-09-28: v1; the HTML's only GitHub link is LaTeXML's. Title
  searches find `StarDust-zz/utility-is-the-compile`, a ten-kilobyte third
  party repository. If released: would be read for `trust_state` and
  `negative_eval`.

**SKILL.state** — an explicit, mutable execution state replacing
append-only history inside a run
([arXiv:2608.26263](https://arxiv.org/abs/2608.26263), v3).
- Examined 2026-08-29; bullet opening "`SKILL.state` was examined and has no
  report".
- Missing: code.
- Monitor: the arXiv page.
- Status 2026-09-28: v3 (2 September), no code link.
  `WUWeifeng710/skill-state-runtime` (created 2026-09-14) describes itself
  as a runtime for the paper; its owner is not an author. If released:
  would not change the call (state is within one run).

**WikiSkill** — raw experience consolidated into a persistent wiki that
later skill updates build on
([arXiv:2608.27454](https://arxiv.org/abs/2608.27454), v1).
- Examined 2026-08-29; bullet opening "`WikiSkill` was examined and has no
  report, and its ablation is the finding".
- Missing: code.
- Monitor: the arXiv page.
- Status 2026-09-28: v1, no code link. At least three third-party
  implementations exist (`ashutoshsinghpr7/wikiskill`,
  `ranjithrajv/wikiskill`, `Stahl-G/wikiskill`); none is from the authors'
  accounts as far as the names show. If released: in scope.

**Self-GC** — a side-channel planner that folds, masks and prunes a run's
active context
([arXiv:2607.00692](https://arxiv.org/abs/2607.00692), v1).
- Examined 2026-08-29; bullet opening "`Self-GC` was examined and has no
  report".
- Missing: code.
- Monitor: the arXiv page.
- Status 2026-09-28: v1, no code link; a title search returns nothing
  relevant. If released: would not change the call (context-window
  management).

**JIT-Agent harness bank** — the cross-task archive of generated harnesses
behind *JIT-Agent*
([arXiv:2608.25593](https://arxiv.org/abs/2608.25593), v2).
- Examined 2026-09-03; bullet opening "[`arXiv:2608.25593`](https://arxiv.org/abs/2608.25593) and
  `bingreeky/JIT` were examined together".
- Missing: the harness bank, frontier and streaming mode, two of thirteen
  seed harnesses, and the training pipeline; the generator and eleven seeds
  are public.
- Monitor: [bingreeky/JIT](https://github.com/bingreeky/JIT).
- Status 2026-09-28: still three commits, last 2026-08-27, the examined
  commit. If released: the bank is the in-scope part.

**HarnessEvolve** — harness optimisation from reference trajectories with a
quality gate and a performance gate
([arXiv:2609.00829](https://arxiv.org/abs/2609.00829), v1).
- Examined 2026-09-04; bullet opening "[`arXiv:2609.00829`](https://arxiv.org/abs/2609.00829) was examined and
  has no report: it releases no code".
- Missing: code and the in-house data.
- Monitor: the arXiv page.
- Status 2026-09-28: v1; the HTML's only GitHub link is LaTeXML's; searches
  return only reading lists. If released: screened as a skill-evolution
  repository.

**MAAFL-6G** — a PPO multi-agent hierarchy for federated learning at the 6G
edge (*IEEE Network*, early access; doi:10.1109/MNET.2026.3694694).
- Examined 2026-09-04; bullet opening "IEEE Xplore document 11554177 was
  examined and has no report".
- Missing: code and data.
- Monitor: [IEEE Xplore 11554177](https://ieeexplore.ieee.org/document/11554177)
  (returns 202 to scripted requests;
  [the DOI](https://doi.org/10.1109/MNET.2026.3694694) redirects).
- Status 2026-09-28: a repository search for the system name returns zero.
  If released: would not change the call, as the bullet says.

**HoloAgent-0** — an embodied agent framework with 3D spatial memory
([arXiv:2606.23565](https://arxiv.org/abs/2606.23565), v1).
- Examined 2026-09-05; bullet opening "Nine spatial-memory repositories for
  robots were examined in one round".
- Missing: HoloAgent-0 code; the tree holds the earlier FSR-VLN stack.
- Monitor: [HorizonRobotics/HoloAgent](https://github.com/HorizonRobotics/HoloAgent).
- Status 2026-09-28: no commit since 2026-07-17; README line 15 still reads
  "Code is under preparation and will be released soon". If released:
  screened.

**EvoMemNav** — self-evolving fine-grained memory for zero-shot navigation
([arXiv:2606.03509](https://arxiv.org/abs/2606.03509), v1).
- Examined 2026-09-05; same bullet.
- Missing: code.
- Monitor: [caicaiya123/EvoMemNav](https://github.com/caicaiya123/EvoMemNav).
- Status 2026-09-28: one commit, "Initial placeholder", 2026-06-01; the
  README is "Code coming soon."

**When Memory Lies** — an empirical study of spatial memory staleness in VLM
agents ([arXiv:2608.04574](https://arxiv.org/abs/2608.04574), v1).
- Examined 2026-09-05; bullet opening "Seven spatial-memory papers from the
  same search have no repository to pin".
- Missing: the code, seed map sets and traces the paper says it releases,
  with no URL.
- Monitor: the arXiv page.
- Status 2026-09-28: v1; the HTML's only repository link is gym-minigrid;
  title searches find only reading lists.

**EchoVLA** — a vision-language-action model with declarative memory
([arXiv:2511.18112](https://arxiv.org/abs/2511.18112), v3).
- Examined 2026-09-05; same bullet.
- Missing: code; the paper carries no URL.
- Monitor: [EchoVLA-project/EchoVLA_web](https://github.com/EchoVLA-project/EchoVLA_web).
- Status 2026-09-28: that repository's description claims the official
  implementation, and its 21 files are a Bulma project-page template
  (`index.html`, `static/`, a sample PDF); two commits on 2025-11-22.

**Spatial Memory for Out-of-Vision Manipulation** — spatial memory for a
VLA policy ([arXiv:2605.22283](https://arxiv.org/abs/2605.22283), v1).
- Examined 2026-09-05; same bullet.
- Missing: code; the paper carries no URL.
- Monitor: [Hoantrbl/SOMA](https://github.com/Hoantrbl/SOMA).
- Status 2026-09-28: that repository calls itself the official code and
  holds two files; its README says "Code will be released soon." Last
  commit 2026-05-21.

**Vision-Language Memory for Spatial Reasoning** — a model-internal memory
for spatial reasoning ([arXiv:2511.20644](https://arxiv.org/abs/2511.20644), v2).
- Examined 2026-09-05; same bullet.
- Missing: code.
- Monitor: the arXiv page.
- Status 2026-09-28: v2, no code link found. If released: would not change
  the call (the memory is a model's internal state).

**Survey of spatial memory representations for robot navigation**
([arXiv:2604.16482](https://arxiv.org/abs/2604.16482), v1).
- Examined 2026-09-05; same bullet.
- Missing: nothing a survey would release; recorded because the bullet
  lists it.
- Monitor: [spatial-memory.github.io](https://spatial-memory.github.io/).
- Status 2026-09-28: the project page resolves; no code expected.

**Act More, Decide Less** — a skill library that supplies action-chunk
boundaries during training
([arXiv:2609.02042](https://arxiv.org/abs/2609.02042), v1).
- Examined 2026-09-05; bullet opening "[`arXiv:2609.02042`](https://arxiv.org/abs/2609.02042) was examined and
  has no report: it releases no code".
- Missing: code.
- Monitor: the arXiv page.
- Status 2026-09-28: v1 (EMNLP 2026 camera-ready), no code link; title
  searches find one reading list. If released: would not change the call
  (training-time scaffold); the pruning rule is what the bullet would read.

**Prove2Me server** — the shared theorem library behind the Fermat's Last
Theorem formalization
([arXiv:2608.28433](https://arxiv.org/abs/2608.28433), v2).
- Examined 2026-09-06; bullet opening "Prove2Me, the shared theorem library
  behind the Fermat's Last Theorem formalization".
- Missing: the server; the client contract and an older prototype are
  public.
- Monitor: [prove2me/prove2me_workspace](https://github.com/prove2me/prove2me_workspace),
  [prove2.me](https://prove2.me/).
- Status 2026-09-28: the `prove2me` account still has one repository, now
  at version 0.11.4 (last push 2026-09-27) and still client-side:
  `SKILL.md`, `references/`, two Lean extraction scripts and examples.
  Other `prove2me` repositories found by search are empty or hold Lean
  solutions. If released: screened as a shared machine-checked memory.

**CompBio and MIRaS** — a multi-omic platform on a memory-based reasoning
engine (*Nucleic Acids Research* 54(16), doi:10.1093/nar/gkag833).
- Examined 2026-09-08; bullet opening "CompBio and MIRaS were examined and
  have no report".
- Missing: code; the Zenodo deposit is embargoed behind a request form.
- Monitor: [the running system](https://gtac-compbio-ex.wustl.edu/),
  [the Zenodo DOI](https://doi.org/10.5281/zenodo.18602034) (redirects;
  Zenodo answered 403 to scripted requests on 2026-09-28, so the embargo
  state was not re-checked).
- If released: would not change the call (the memory is the literature,
  not the user).

**MAP-Graph** — provenance-aware shared memory with scope intersection and
recursive revocation ([arXiv:2608.10509](https://arxiv.org/abs/2608.10509), v1).
- Examined 2026-09-08; bullet opening "[`arXiv:2608.10509`](https://arxiv.org/abs/2608.10509) was examined and
  has no report: it releases no code".
- Missing: code, dataset and artifacts.
- Monitor: the arXiv page.
- Status 2026-09-28: v1, no code link; the name is too common for a
  repository search to settle it. If released: read the scope-intersection
  rule and the revoked-ancestor check first.

**xiaoO RAM-A server** — the long-term memory server openEuler's AgentOS
runtime calls over MCP.
- Examined 2026-09-11; bullet opening "`FreshHillyer/xiaoO` was examined and
  has no report".
- Missing: RAM-A, configured only as a local URL; also, the in-tree memory
  crate has no caller.
- Monitor: [FreshHillyer/xiaoO](https://github.com/FreshHillyer/xiaoO),
  [gitcode.com/openeuler/xiaoO](https://gitcode.com/openeuler/xiaoO).
- Status 2026-09-28: the GitHub mirror's head is still the examined commit
  (2026-09-10); a repository search for `RAM-A` returns nothing related.
  The upstream on GitCode was not walked.

**Dream-RSI** — recursive self-improvement that replays recorded discovery
trees as a simulator.
- Examined 2026-09-16; bullet opening "`zhengkid/Dream-RSI` was examined and
  has no report: no code is released yet".
- Missing: code.
- Monitor: [zhengkid/Dream-RSI](https://github.com/zhengkid/Dream-RSI).
- Status 2026-09-28: head is still the examined commit; the README's release
  table still lists the full codebase as "⏳ Being prepared". Search finds
  `Sebastianrodaaa/Dream-RSI`, a copy with the same commits and no code, and
  third-party reimplementations. If released: would not change the call.

**Grounding Agent Memory** — a post-task curator that probes the environment
before committing a memory
([arXiv:2609.11060](https://arxiv.org/abs/2609.11060), v1).
- Examined 2026-09-16; bullet opening "[arXiv:2609.11060](https://arxiv.org/abs/2609.11060) was analysed and
  has no report".
- Missing: code and the adapted APEX split.
- Monitor: the arXiv page;
  [hermes-agent issue 107914](https://github.com/NousResearch/hermes-agent/issues/107914)
  proposes the same loop downstream.
- Status 2026-09-28: v1; the HTML's only repository link is
  `github/copilot-sdk`. If released: read the probe-tool binding first.

**arc-code post-broker record** — the per-session evidence behind arc-code's
headline ARC score.
- Recorded in `content/systems/arc-code.md` (analysed 2026-09-18).
- Missing: the full post-broker record; six workspaces of 191 are public.
- Monitor: [jerber/arc-code](https://github.com/jerber/arc-code).
- Status 2026-09-28: the README still says the record "will be released
  shortly".

**Qwen-Planner-Agent** — a mobile planner agent whose technical report
describes a persistent memory manager with provenance tiers, supersession
and prospective memory
([arXiv:2609.29892](https://arxiv.org/abs/2609.29892), v1).
- Examined 2026-09-24; bullet opening "`Tongyi-MAI/Qwen-Planner-Agent` was
  examined and has no report".
- Missing: the agent implementation, training code and weights.
- Monitor: [Tongyi-MAI/Qwen-Planner-Agent](https://github.com/Tongyi-MAI/Qwen-Planner-Agent),
  [project page](https://tongyi-mai.github.io/Qwen-Planner-Agent/).
- Status 2026-09-28: the paper is now on arXiv (the bullet found no entry);
  commit "Update paper and arXiv citation" on 2026-09-26; still 17 blobs and
  no source file; the README still says it is not the release repository;
  the organisation's Hugging Face account still lists four models, none this
  one. If released: squarely in scope.

**Infinite-Parameter LLMs** — a hypernetwork that adapts weights online
from live data ([arXiv:2609.18842](https://arxiv.org/abs/2609.18842), v2).
- Examined 2026-09-25; bullet opening "[`arXiv:2609.18842`](https://arxiv.org/abs/2609.18842) was examined and
  has no report: it releases no code".
- Missing: code.
- Monitor: the arXiv page.
- Status 2026-09-28: v2, no code link. If released: would not change the
  call (no handle on an absorbed fact).

**HyperAgents evolved memory** — the `MemoryTool` over `memory.json` that
evolved DGM-H agents wrote, per the paper
([arXiv:2603.19461](https://arxiv.org/abs/2603.19461), v1).
- Examined 2026-09-27; bullet opening "`facebookresearch/HyperAgents` was
  examined and has no report".
- Missing: the evolved agents' code; the committed program holds only the
  outer loop, and evolved agents are published as experiment logs on Google
  Drive, which were not read.
- Monitor: [facebookresearch/HyperAgents](https://github.com/facebookresearch/HyperAgents).
- Status 2026-09-28: head is still the examined commit (2026-04-14). If the
  evolved agents are committed: the case the Gödel-machine note said would
  enter the atlas.

**HomeBody** — a humanoid that explores, stores ego observations in a shared
frame and recalls them for skill selection.
- Examined 2026-09-28; bullet opening "`Stanford-TML/homebody` was examined
  and has no report".
- Missing: code and paper.
- Monitor: [Stanford-TML/homebody](https://github.com/Stanford-TML/homebody),
  [project page](https://tml.stanford.edu/homebody/).
- Status 2026-09-28: still six commits; the 22 code files are the page's
  scripts; the README still says "Code coming soon."; a title search finds
  only this repository.

### Closed or hosted memory components

These were excluded, or reported with a gap, because the memory is behind a
service or in a private repository. None has announced a release; they are
listed so a change of licence or an open engine is noticed. Status is from
the organisation's repository listing on 2026-09-28.

| Item | Examined | Where recorded | Closed part | Monitor | Status 2026-09-28 |
|---|---|---|---|---|---|
| Supermemory | 2026-07-26 | appendix, "Supermemory's hosted backend implementation was not visible" | hosted backend | [supermemoryai/supermemory](https://github.com/supermemoryai/supermemory) | no backend repository among the organisation's recent ones |
| Mem0 platform | 2026-07-26 | appendix, "Some mem0 advanced capabilities appear to be managed-platform-only" | managed-platform features | [mem0ai/mem0](https://github.com/mem0ai/mem0) | not re-checked beyond the repository resolving |
| MetaBot | 2026-07-27 | appendix, "Eight repositories examined in the same round have no reports" | memory backend | [xvirobotics/metabot](https://github.com/xvirobotics/metabot) | no backend repository in the listing |
| Oracle Agent Memory ([arXiv:2607.13157](https://arxiv.org/abs/2607.13157), v1) | 2026-07-28 | appendix, "Oracle's `oracleagentmemory` was suggested for review" | the substrate; the paper ships no code | the arXiv page | a search of the Oracle organisations for agent memory returns zero; search hits are third-party demos |
| graperoot | 2026-07-31 | appendix, "Five repositories named in a Reddit thread were examined" | proprietary graph engine package | [kunal12203/graperoot](https://github.com/kunal12203/graperoot) | no engine repository in the listing |
| bhived | 2026-07-31 | same bullet | hosted memory API | [ArtKeyAi/bhived-mcp](https://github.com/ArtKeyAi/bhived-mcp) | the account has one repository |
| Empryo `packages/memory` | 2026-08-05 | appendix, "Empryo's maintainer reports substantial changes" | private memory workspace | [proxysoul/Empryo](https://github.com/proxysoul/Empryo) | public head moved to `669ff9198da5` (2026-09-27, docs commits); still `src/core/memory/`, no `packages/memory/` |
| Maximem Synap | 2026-08-15 | appendix, "`maximem-ai/maximem_synap_sdk` was examined" | hosted engine | [maximem-ai/maximem_synap_sdk](https://github.com/maximem-ai/maximem_synap_sdk) | no engine repository in the listing |
| Custodian Labs | 2026-08-17 | appendix, "`Custodian-Labs/custodian-labs-python` was examined" | hosted SDK | [Custodian-Labs/custodian-labs-python-examples](https://github.com/Custodian-Labs/custodian-labs-python-examples) | the repository was renamed to `custodian-labs-python-examples`; no SDK source in the listing |
| Warp memory stores | 2026-08-18 | appendix, "`warpdotdev/warp` was examined" | server-side memory stores | [warpdotdev/warp](https://github.com/warpdotdev/warp) | not re-checked beyond the repository resolving |
| Memstate | 2026-08-27 | appendix, "`memstate-ai/memstate-mcp` was examined" | hosted MCP server | [memstate-ai/memstate-mcp](https://github.com/memstate-ai/memstate-mcp) | no server repository in the listing |
| Benzi | 2026-09-01 | appendix, "`oooscoos/Benzi` was examined" | VS Code extension and per-repo store | [oooscoos/Benzi](https://github.com/oooscoos/Benzi) | the account has two repositories, `Benzi` and `experiments` |
| Zep Cloud | 2026-09-15 | `content/systems/zep.md` | the temporal graph service | [getzep/zep](https://github.com/getzep/zep) | not re-checked beyond the listing |
| SageOx | 2026-09-16 | appendix, "`sageox/ox` was examined" | session-to-memory processing behind the API | [sageox/ox](https://github.com/sageox/ox) | no server repository in the listing |
| Mnemoverse | 2026-09-16 | appendix, "`mnemoverse/mcp-memory-server` was examined" | hosted engine | [mnemoverse/mcp-memory-server](https://github.com/mnemoverse/mcp-memory-server) | newest repositories are plugins, an SDK and paper repositories; no engine |
| ContextStream | 2026-09-17 | `content/systems/contextstream-mcp.md` | proprietary backend | [contextstream/mcp-server](https://github.com/contextstream/mcp-server) | no backend repository in the listing |
| SmythOS SRE | 2026-09-18 | `content/systems/smythos-sre.md` | proprietary modules named in `NOTICE.md` | [SmythOS/sre](https://github.com/SmythOS/sre) | not re-checked beyond the listing |
| Montycat | 2026-09-19 | appendix, "A second repository was examined and is a client, not a store" | proprietary engine | [MontyGovernance/montycat-mcp](https://github.com/MontyGovernance/montycat-mcp) | the listing shows `montycat_rust`, `_node`, `_dart`, `_python` and `_serialization_derive`, all older than the examination; none was opened |
| Dakera | 2026-09-19 | appendix, "A repository was examined and carries no memory implementation" | closed engine image | [Dakera-AI/dakera-deploy](https://github.com/Dakera-AI/dakera-deploy) | integrations, SDK and package repositories; no engine |
| breadcrumbs fleet | 2026-09-19 | `content/systems/breadcrumbs.md` | the fleet machinery the essays describe | [The-825/breadcrumbs](https://github.com/The-825/breadcrumbs) | the account has two repositories |
| Engram product | 2026-09-20 | `content/systems/engram-format.md` | the daemon, vault, relay and observer | [El-AI-Intelligence/engram-format](https://github.com/El-AI-Intelligence/engram-format) | the listing adds `amparo` (created 2026-08-27, "an open agent that acts under policy"); no daemon repository |
| OGAD pro | 2026-09-26 | `content/systems/ogad.md` | the paid `pro/` submodule | [off-grid-ai/OGAD](https://github.com/off-grid-ai/OGAD) | `.gitmodules` points at `off-grid-ai/desktop-pro`, which returns 404 |

## How to check

Repository placeholders: last push, commit count and code files.

```sh
for r in Darwin-Agent/Mi-Memory elizaOS/agentmemory bingreeky/JIT \
         HorizonRobotics/HoloAgent caicaiya123/EvoMemNav Hoantrbl/SOMA \
         EchoVLA-project/EchoVLA_web prove2me/prove2me_workspace \
         FreshHillyer/xiaoO zhengkid/Dream-RSI jerber/arc-code \
         Tongyi-MAI/Qwen-Planner-Agent facebookresearch/HyperAgents \
         Stanford-TML/homebody neomjs/neo; do
  gh api "repos/$r" --jq '[.full_name, .pushed_at] | @tsv' 2>/dev/null || { echo "$r 404"; continue; }
  gh api "repos/$r/commits?per_page=1" -i | grep -i '^link:' | grep -o 'page=[0-9]*>; rel="last"'
  gh api "repos/$r/git/trees/HEAD?recursive=1" \
    --jq '"truncated=\(.truncated) code=\([.tree[] | select(.type=="blob") | .path | select(test("\\.(py|rs|ts|js|go|ipynb|cpp|sh|lean)$"))] | length)"'
done
```

A code count above zero is a prompt to open the tree, not a result: HomeBody's
22 are its project page's scripts.

arXiv: current version, and any repository link in the newest HTML.

```sh
note=notes/2026-09-28-unreleased-code-watchlist.md
for id in $(grep -o 'arxiv.org/abs/[0-9.]*' "$note" | cut -d/ -f3 | sort -u); do
  v=$(curl -s "https://export.arxiv.org/api/query?id_list=$id" | grep -o '<id>http://arxiv.org/abs/[^<]*' | sed 's|.*/abs/||')
  links=$(curl -sL "https://arxiv.org/html/$id" | grep -o -E '(github\.com|huggingface\.co)/[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)?' \
          | grep -v -E 'brucemiller/LaTeXML|arXiv/html_feedback' | sort -u | tr '\n' ' ')
  echo "$v | $links"
  sleep 3
done
```

Project pages, which link code before papers do (FARM, VISTA and Agent
Memory Distillation all did):

```sh
for u in https://darwin-agent.github.io/Mi-Memory/ https://schema-harness.github.io/ \
         https://tongyi-mai.github.io/Qwen-Planner-Agent/ https://tml.stanford.edu/homebody/ \
         https://prove2.me/; do
  echo "$u $(curl -sL "$u" | grep -o -E '(github\.com|huggingface\.co)/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+' | sort -u | tr '\n' ' ')"
done
```

Papers with no known repository: one exact-title search and one broader
search each, spaced for the 30-per-minute search limit. A hit is only a lead
until the owner is matched against the author list; SKILL.state, WikiSkill
and Dream-RSI all have third-party implementations.

```sh
gh search repos "<exact paper title>" --limit 5
gh api search/repositories -X GET -f q='<short title> in:name,description,readme' \
  --jq '.total_count, (.items[] | .full_name + " " + .created_at[0:10])'
```

Closed components: list the organisation's repositories newest first and
look for a name that could be the engine.

```sh
gh api "users/<org>/repos?per_page=100&sort=created" --jq '.[] | .created_at[0:10] + " " + .name'
```

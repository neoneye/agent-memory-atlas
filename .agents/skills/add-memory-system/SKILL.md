---
name: add-memory-system
description: Research and integrate a new agent-memory repository into Agent Memory Atlas. Use when asked to add, analyze, catalog, or compare a memory system in this repository, including its commit-pinned system report, comparative overview coverage, homepage card, generated site, and validation.
---

# Add Memory System

Add one memory system to the atlas as a code-grounded, commit-pinned analysis. Treat the individual report, comparative synthesis, homepage, and generated site as one change.

**Screen the checkout first — this is a precondition, not a suggestion.** Run the
`screen-repository` skill before reading a single file of a newly cloned tree:

```sh
python3 scripts/screen_repo.py /absolute/path/to/source-repository
```

Analysis means cloning a stranger's repository onto a personal machine and often
running its build or its tests. Auto-executing hooks fire without a command being
typed, and an unpinned dependency is a supply-chain compromise waiting on somebody
else's account. Read every `RUNS` finding before doing anything else, keep the
default posture read-only, and prefer `npm ci --ignore-scripts` and a throwaway
venv over the documented install when execution is genuinely needed. `NOTHING
SCANNED` is a finding, not a pass, and so is `FRESH` — **never install a
third-party dependency published in the last seven days**, because that window is
where an undetected registry compromise lives. `npm ci` does not protect you
there: it reproduces the lockfile faithfully however new the pin is. Record the
outcome in the report's History entry.

If the atlas already has a report for this repository, this is the wrong skill — use `reanalyze-memory-system`, which covers re-pinning, deciding whether a published claim went stale, and the rename-and-redirect convention. Check first:

```sh
rg -l '^source_url:.*<owner>/<repo>' content/systems/
```

A renamed upstream will not match on name; search the pinned `revision` as well before concluding it is new.

## Establish the inputs

Resolve these before writing:

- The Agent Memory Atlas repository root.
- A local checkout of the memory-system repository.
- A unique lowercase filename slug.
- The canonical source repository URL.
- The exact full commit ID being analyzed.

Prefer a local checkout because the report must trace implementation paths. Do not change the source repository. If only a URL is available, clone it to a temporary directory when network access and user authorization allow it.

Confirm the system is in scope before writing. The atlas compares memory that outlives a session: something is stored, retrieved later, and can be scoped, corrected, or forgotten. A framework whose "memory" only decides which messages stay in the current context window is conversation-window management, not agent memory — see the "Not in scope" entry in `content/overview.md`. Such a system belongs in that section as a short example, not as a report with empty matrix columns. Compaction counts only when something survives the session with an identity that could later be corrected. Say so early if a candidate fails this bar, rather than padding a report.

**Two things are not part of that bar, and both have been mistaken for it.** *Novelty is not a criterion* — a system whose memory is a well-covered shape still gets a report, because the atlas compares implementations and a competent instance of a common design is evidence about the design. Excluding something for being unoriginal is the error that cost this repository six reports before it was reversed. And a *source-available or restrictive licence is a caveat, not an exclusion* — BSL, ELv2, PolyForm and "all rights reserved" are stated in section 1 so a reader knows what they may do with what they read, and the mechanisms are still analysed. A licence asserted in a README whose file is absent from the tree is worth stating plainly for the same reason. The genuine exclusions are: nothing survives the session, the mechanism is closed-source behind an open wrapper, or there is no inspectable code at a pinned commit at all.

Inspect repository-level instructions in both repositories before proceeding. Check the atlas worktree and preserve unrelated changes.

## Scaffold the report

After an initial orientation pass, choose a concise title, eyebrow, and one-sentence description. Run:

```sh
python3 .agents/skills/add-memory-system/scripts/scaffold_report.py \
  /absolute/path/to/source-repository \
  --slug example-system \
  --title "Example System" \
  --eyebrow "Local hybrid memory" \
  --description "A concise architectural description grounded in the implementation."
```

The script reads the checkout's `origin` and `HEAD`, normalizes GitHub links, stamps `analyzed_at` with today's date, and creates `content/systems/<slug>.md`. It refuses to overwrite an existing report. Use `--stdout` to inspect the generated document without writing it.

For a non-GitHub or unusual remote, pass `--source-url` with the public repository URL. Verify that `source_url`, `revision`, and `revision_url` resolve to the repository and exact analyzed commit.

## Investigate the source repository

Start broad, then trace concrete state transitions:

1. Read the README, package manifests, architecture documents, and deployment files.
2. Locate memory schemas, storage adapters, prompts, APIs, MCP tools, workers, tests, evals, and benchmark artifacts.
3. Trace capture/write, extraction/consolidation, retrieval/ranking, context injection, correction/deletion/forgetting, and background processing end to end.
4. **Find the producer of every mechanism before crediting it.** A mechanism can be fully declared — a schema column, an enum value, a function, a spec section, its own passing tests — and have nothing in the repository that ever puts a value into it. This is the most common defect in the corpus; 51 reports carry a version of it. An audit log with a closed action vocabulary where `data.written` and `data.deleted` have no producer. A tombstone whose only writer is a script whose own header says it is "NOT wired into any CLI command", and which the package manifest excludes from what ships. A reviewer quorum that always passes because the policy it consults is hardcoded `{}` at both write paths.

   **The test is not whether the symbol has callers.** All three of those have callers, and a grep for call sites reports them live. The question is whether any path a user or an agent can reach *produces* the state the mechanism acts on, which is a question about data flow rather than the call graph. Work backwards from the field to every assignment, and forwards from each entry point the system actually exposes — MCP tool, HTTP endpoint, CLI command, scheduled worker — to see whether any assignment sits on one. The shapes this keeps taking: a parameter every caller omits, a config key with no setter, a branch on a flag nothing sets, a default no caller overrides, and a writer that exists only in tests or in a file excluded from the published package.

   Then say which it is. **Do not credit a capability mark to a mechanism with no producer** — `capabilities: ""` is a real answer, and an unreachable mechanism is the case it exists for. Declared-and-unwired is not a caveat to bury in a risk bullet; it is often the most informative thing in the repository, because it means the design was understood and the wiring was not finished, which is a sharper finding than an absence.

   Every report in the corpus that finds an unwired mechanism already withholds the mark that mechanism would have earned, so this codifies the bar rather than raising it. Five say so in as many words, and they are the models to copy: kage — *"Audit log — withheld, and the reason is a second unwired mechanism"*; memoir — *"it is why the `trust_state` mark is withheld… the field exists, the reader respects it, and no writer sets it"*; NOOA Memory — *"the mark is withheld not because the design lacks the idea but because the idea is a schema comment"*; PowerMem — *"the capability is withheld twice over"*; yantrikdb — *"Bitemporal, human review, negative eval — no"*, because the review surface *"belongs to an unwired path"*. Naming the withheld mark and the reason is worth more than silence, because a reader comparing two systems can otherwise not tell a mark that was considered and refused from one nobody looked for.

   One distinction the test does not make, and you should. A mechanism whose *producer* is missing has not been built; a mechanism whose *consumer* is stale has been built and does not take effect. OmniIntelligence is the corpus's example of the second — its manual kill switch appends to `pattern_disable_events` with `reason` and `actor` both `NOT NULL`, so the producer is real, and the gate reads a materialized view nothing refreshes outside tests. That still earns the mark, and the report is required to say the override never reaches the read path.

5. **Inspect tests beside each important behavior, and check that each one can fail.** Distinguish tested behaviour from documentation claims — and then apply a second test to the test, because a suite that cannot fail reports PASS regardless of the code and reads, in a report, as coverage.

   Silica states the class exactly and is the only project in the corpus that guards against it: *"A metric that cannot fail reports PASS regardless of the arm, and the gate reads as a result."* Its `evals/negative_controls.py` pins every deterministic gate metric against fixtures of which **at least two must disagree**, and refuses to run a gate whose metric it does not recognise. Read it before writing section 10 of anything.

   Four shapes recur, and all four were found in one week across unrelated repositories:

   - **The vacuous predicate.** `results.every(m => m.status !== ARCHIVED)` over a database a `beforeEach` seeded with one archived row and nothing else. `Array.every` on an empty array is `true`, so the case passes against a retriever that returned nothing — Arcon, `memory-retriever.test.ts`, repaired at the next pin by adding `results.some(...)` for a control memory in the same test. Rust and Python spell it `is_empty()`, `all(...)`, `assert_eq!(len, 0)`.
   - **The computed-and-unasserted number.** Hillock's `verify_hillock.py` builds the score distribution the whole gate turns on, computes `passes` and `leaks` against the threshold, and asserts `len(rows) == 30` — that the distribution *ran*, not what it said. Both identifiers appear once and never again.
   - **The comment that stands in for the assertion.** Weave's `verifier_falls_back_without_llm_v4` ingests a second note under *"Unsupported claim is still quarantined deterministically"* and deletes both fixtures without checking it.
   - **The suite that skips itself.** The same file opens each case with `let Some(pool) = pool().await else { eprintln!("skipping: no reachable database"); return; }`, so a run without Postgres is green having asserted nothing. A skip is not a pass, and a report must not treat a badge as evidence the behaviour holds.

   A fifth belongs beside them because it is the same defect outside a test: **the declared threshold nothing reads**. `retrieveMemory(agent, query, topK = 5, minScore = 0.45)` in ai-agent-automation scores, sorts and slices, and `minScore` appears on exactly one line of the backend — the signature — while a caller passes `0.45` explicitly. The intent is documented at the call site and defeated in the callee.

   Cheap checks, in order of yield: for every negative assertion, ask what the fixture guarantees is *present*; grep the file for the identifiers a computed metric was bound to; read the skip path of an integration suite before quoting its pass count; and treat a stated behaviour in a comment as a claim to verify rather than a finding.

   Then say which it is. **A negative assertion that can pass on an empty result does not earn `negative_eval`** — the mark asks for a committed case establishing that particular material stayed out of a populated result set, and vacuity is the failure it exists to exclude. Arcon's first reading withheld the mark on exactly this and named the one-line repair; its second reading awarded it because the repair had landed.
6. Identify deployment assumptions, concurrency boundaries, trust decisions, provenance, privacy, and failure recovery.
7. **Look for a paper before writing section 10.** Grep the README and docs for `arxiv`, `bibtex`, `@article`, `@misc`, `Citation`, `CITATION.cff` and `doi`. A citation block at the bottom of a README is easy to scroll past, and missing it produces the specific error this step exists to prevent: a report that says "no ablation" or "no evaluation" when the ablation is in the paper. If a paper exists, read at least its abstract and any ablation table, cite it as `[arXiv:ID](https://arxiv.org/abs/ID)` with the submission date, and keep its claims separate from code claims exactly as README claims are kept separate. Two findings are worth looking for specifically: whether the paper's description of the mechanism matches the code, and whether anything the paper starts from — a seed corpus, a checkpoint, a dataset — is absent from the tree. If no paper exists, the report says so rather than staying silent, because a reader cannot tell an absent paper from an unread one.

**Follow every link to a hosted result, too, and read the artifact under it rather than the row.** A leaderboard entry, a scorecard, a hosted eval run — if the README or the project links one, open it before writing section 10. Three reports written in one sitting all cited an external ARC-AGI-3 leaderboard second-hand; the scorecards behind it carry per-environment tables from which each published mean recomputes exactly, one project's `artifacts/` held a six-arm ablation pricing its own mechanism, and one report had described a 19.80% result as "a benchmark claim" without the number. Two questions pay for the click every time: **does the headline recompute from the artifact**, and **is the metric what the ranking implies** — two entries 0.14 points apart there had solved identical task sets, the gap being action efficiency at 4.6x the cost. Record what the venue says about its own verification: a listing is often publication, not checking, and the good ones say so.

A paper is a third category beside product claims and code claims, and it is the one most likely to be missing rather than wrong: scoping an absence claim to the artifact ("no result is committed to this repository") is correct where an unscoped one ("no ablation exists") is a claim about work that was probably done elsewhere.

Prefer code, schemas, tests, and committed artifacts over marketing language. Cite repository-relative file paths and key functions, classes, types, or endpoints. Label inferences and unknowns. Do not imply that a benchmark was rerun when only its code or committed output was inspected.

Use focused searches rather than reading every file. Useful search concepts include:

```text
memory recall remember search embedding vector rank rerank
extract consolidate summarize profile graph entity
delete forget expire ttl supersede conflict provenance trust
mcp tool api route worker queue migration schema benchmark eval
```

Run proportional smoke tests when they materially verify the architecture and are safe in the source checkout. Avoid broad installation or expensive benchmarks unless the user requested them.

## Write the individual report

Read `content/methodology/per-repo-report-format.md` completely and fill every scaffolded section:

1. Executive Summary
2. Mental Model
3. Architecture
4. Essential Implementation Paths
5. Memory Data Model
6. Retrieval Mechanics
7. Write Mechanics
8. Agent Integration
9. Reliability, Safety, and Trust
10. Tests, Evals, and Benchmarks
11. Patterns Worth Stealing
12. Antipatterns / Risks
13. Build-vs-Borrow Takeaways
14. Open Questions
15. Appendix: File Index

Make the report opinionated but fair. Explain what makes the design good, what makes it weak, and for which use cases those tradeoffs matter.

**Write about the system, not about the writing of the report.** The reader wants the state of the code at the pinned commit. Sentences about what the atlas noticed, corrected, previously believed, or was right about are process narration and do not belong in a report body — they have been removed from this repository more than once. A fact about the *subject's* own history is different and often the point: "until 31 July 2026 neither variable was assigned anywhere in the repository" describes the system. The test: if a sentence would have to change when the atlas changes rather than when the system changes, cut it. Corrections to previously published claims are logged in the known-limitations list at the end of `content/overview.md`, not narrated in place.

**Every report carries a Mermaid diagram.** Put it at the end of section 2, before `## 3. Architecture`, and draw the mechanism the report is actually about — the epistemic state machine where there is one, the write-to-recall path where there is not, and the place the design fails where that is the finding. A generic boxes-and-arrows of components is worse than none: it takes a reader's attention and returns nothing the prose did not already say. `scripts/check_mermaid.py` fails the build on a report without one, and separately on labels that break the renderer, so quote any label containing `[](){}"` and avoid a second `:` in a stateDiagram transition.

Before integration, verify:

- No placeholder text remains.
- The frontmatter matches nearby reports.
- Sections 2 and 3 do not tell the same story twice: section 2 is the epistemic
  state machine (how a thing becomes a belief and how it stops being one),
  section 3 is infrastructure (what has to be running, and what it costs an
  operator to stand up).
- Section 11 is one section with `### Steal`, `### Avoid`, `### Fit`. `Fit` is a
  judgement about whether the whole design suits a reader — maintenance budget,
  scale, deployment, who should walk away. If it reads as a summary of Steal and
  Avoid, it has failed and should be rewritten, not padded.
- The write section states whether writes block the agent, what the lag is
  before a memory is retrievable, and whether any background pass rewrites the
  whole store.
- The full commit ID appears in `revision`.
- The commit URL appears in `revision_url`.
- `analyzed_at` reflects the date the analysis was actually performed.
- Important architectural claims point to concrete implementation locations.
- Strengths and risks are supported by evidence.
- Every mechanism carrying a capability mark has a producer on a path a user or
  an agent can reach, and any mechanism without one is reported as declared and
  unwired rather than as present.

## Integrate the comparative overview

Read `content/methodology/overview-report-format.md` and the complete `content/overview.md`. Integrate the new system throughout the comparison instead of appending an isolated summary.

Review and update every applicable area:

- Title metadata and prose that states the system count.
- Taxonomy and category membership. The taxonomy has eight families plus a
  scope boundary; fit the system into an existing family and characterize it in
  place. Do not add a family for a single system — that is what turned the
  taxonomy into a list once already.
- Comparative matrix — **do not edit the table**. It is generated by
  `scripts/generate_matrix.py` from a `matrix:` block in each report's
  frontmatter. The scaffolder emits the block with all eleven keys
  (`memory_unit`, `storage`, `retrieval`, `write`, `update_delete`, `scoping`,
  `integration`, `background`, `trust`, `strengths`, `risks`); fill every one,
  then run `npm run build`. `npm test` fails if the table is out of sync.
- Storage census — three flat keys beside `capabilities:`, and the build fails
  if they are missing:

  ```yaml
  stack_storage: "sqlite, files"
  stack_retrieval: "lexical, vector"
  stack_source: "reviewed"
  ```

  Vocabularies are fixed and listed in `scripts/extract_stack.py`; an unknown
  value fails `npm test`. Name every store the system *itself* runs — a vector
  sidecar counts, an adapter the adopter binds is `delegated`, and a system with
  no store of its own gets `""`. Arms are `lexical`, `vector`, `graph`, and only
  those the read path actually runs: a `pgvector` column is storage, not a
  vector arm, unless retrieval queries it.

  **Set `stack_source: "reviewed"` — you read the tree.** `"seeded"` marks the
  238 rows back-filled from each report's own summary lines by
  `extract_stack.py --seed` before this key existed; those are a guess with a
  label on it, and the seeded count is only allowed to fall. If you re-analyse a
  report carrying `"seeded"`, check the two lists against the code and promote
  it while you are there.
- Capability index — **do not edit that list either**. It is generated from the
  `capabilities:` key in the same frontmatter, and the build fails if the key is
  missing. Declare only what was found in code, against the definitions below.
  `capabilities: ""` is a real answer and the common one; it says the report was
  assessed and the system carries none of these mechanisms, which is different
  from nobody having looked.

  | Flag | Present only when |
  | --- | --- |
  | `tombstone` | A durable record of a *rejected value*, keyed on the value, so later extraction cannot re-assert it. Supersession, archival, and delete-sync markers are **not** this. |
  | `trust_state` | Discrete epistemic status — at least candidate vs verified vs rejected — as a field. A confidence *score* is not a state. |
  | `bitemporal` | Validity time tracked separately from record time. |
  | `scope_enforced` | A stored scope key applied as a filter on the read path. A scope stored as a tag but not applied is not this. |
  | `audit_log` | An explicit append-only event or audit record of mutations in the system's own store. Git history alone is a different mechanism — note it in prose instead. |
  | `human_review` | A surface where a person inspects, approves, or adjudicates memory content. A memory UI that only displays is not this. |
  | `negative_eval` | Committed evaluation cases asserting that particular material must *not* be retrieved. |

  Be strict, and put the near-miss in the prose. "Almost has a tombstone" is the
  most useful sentence in several of these reports, and it is only legible
  because the flag is withheld.
- Lifecycle, retrieval, write, correction, trust, integration, and operations comparisons.
- Implementation hotspots and patterns worth stealing.
- Risks, recommendations, and build-vs-borrow conclusions.
- Individual report links.
- Repositories inspected, with source and exact commit links.
- Known limitations and test/benchmark qualification.

Preserve nuance. A system can belong to multiple categories, and absence of a feature is not automatically a defect if it is outside the design's intended scope.

## Review the pattern library

Read `content/patterns/index.md` and every pattern page that overlaps the new system. Update the "Seen in the atlas" evidence when the repository provides a strong example, counterexample, or failure mode.

Add a dedicated pattern page only when the implementation reveals a reusable architectural move that is not already covered. A good pattern page must explain:

- Intent and the recurring problem.
- Architectural shape and important invariants.
- Why the pattern works.
- Tradeoffs and failure modes.
- Concrete systems in the atlas.
- Tests required before relying on it.
- Related patterns.

When adding a pattern, register it in the pattern index, consider featuring it on the homepage, update the homepage pattern count, and keep `scripts/test_site.sh` aligned. Do not create a new pattern name for a minor product feature or a one-off implementation detail.

## Register the system on the homepage

Add one card to `site/index.html` that matches the existing card structure:

- Pick the closest category and existing accent style.
- Use a unique sequential card number.
- Summarize the architecture, best idea, and main risk.
- Link to `./systems/<slug>/`.
- Include useful search terms in `data-search`.

Update nearby statistics, spelled-out counts, comparison copy, and the conceptual memory map when the new system materially changes a family. Search the repository for old counts rather than assuming they occur in one place:

```sh
current_count="$(find content/systems -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"
rg -n "\\b${current_count}\\b|repositories traced|across all|Expected [0-9]+|Validated [0-9]+|system_count" \
  README.md content site scripts templates
```

The `rg` line above finds digits. It does not find the two forms that actually go stale, so sweep for both:

```sh
rg -n -i 'one hundred and [a-z-]+|of (the )?[0-9]{2,3}\b' README.md content site
```

Spelled-out counts ("one hundred and twenty-three") appear in prose across the homepage, the overview, the
capability pages and several pattern pages, and they are case-sensitive — `One hundred` and `one hundred` are
separate replacements. The `N of M` form ("69 of 123") is worse, because the numerator changes only when a
mark moves and the denominator changes on every addition, so the two drift apart silently.

**Never put a corpus count in a report body.** A sentence like "eighteen systems here carry `audit_log`" is
stale the next time anything is added, and it makes an unrelated report a required edit forever. Write the
comparison without the number — "in every other system here that carries `audit_log`…" — and let
`content/patterns/index.md` hold the counts, where they are generated.

Review every match. Do not mechanically change unrelated section numbers or commit IDs.

`scripts/test_site.sh` derives its expected report and pattern counts from `content/`, so it needs no count edits; only touch it when adding a new required file or invariant.

## Build and validate

From the atlas root, run:

```sh
npm run build
npm test
```

Then verify:

- `docs/systems/<slug>/index.html` exists and is non-empty.
- The homepage links to the rendered report.
- The report shows source and analyzed-revision links.
- Generated `docs/` contains the updated overview and homepage.
- Relevant pattern pages include the new implementation evidence.
- No root-relative links were introduced.
- Search/filter metadata makes the new card discoverable.

Inspect the rendered page when the report contains wide tables, diagrams, or unusual markup.

Finally review `git diff --check`, the scoped diff, and repository status. Do not commit or push unless the user asks.

## Completion summary

Report:

- The new system and analyzed commit.
- The report, overview, homepage, and generated site files changed.
- Tests or smoke checks run.
- Any unresolved architectural unknowns.

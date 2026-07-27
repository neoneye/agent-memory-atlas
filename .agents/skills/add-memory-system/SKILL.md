---
name: add-memory-system
description: Research and integrate a new agent-memory repository into Agent Memory Atlas. Use when asked to add, analyze, catalog, or compare a memory system in this repository, including its commit-pinned system report, comparative overview coverage, homepage card, generated site, and validation.
---

# Add Memory System

Add one memory system to the atlas as a code-grounded, commit-pinned analysis. Treat the individual report, comparative synthesis, homepage, and generated site as one change.

## Establish the inputs

Resolve these before writing:

- The Agent Memory Atlas repository root.
- A local checkout of the memory-system repository.
- A unique lowercase filename slug.
- The canonical source repository URL.
- The exact full commit ID being analyzed.

Prefer a local checkout because the report must trace implementation paths. Do not change the source repository. If only a URL is available, clone it to a temporary directory when network access and user authorization allow it.

Confirm the system is in scope before writing. The atlas compares memory that outlives a session: something is stored, retrieved later, and can be scoped, corrected, or forgotten. A framework whose "memory" only decides which messages stay in the current context window is conversation-window management, not agent memory — see the "Not in scope" entry in `content/overview.md`. Such a system belongs in that section as a short example, not as a report with empty matrix columns. Compaction counts only when something survives the session with an identity that could later be corrected. Say so early if a candidate fails this bar, rather than padding a report.

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
4. Inspect tests beside each important behavior; distinguish tested behavior from documentation claims.
5. Identify deployment assumptions, concurrency boundaries, trust decisions, provenance, privacy, and failure recovery.

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

Make the report opinionated but fair. Explain what makes the design good, what makes it weak, and for which use cases those tradeoffs matter. Include a Mermaid diagram only when it clarifies components or lifecycle.

Before integration, verify:

- No placeholder text remains.
- The frontmatter matches nearby reports.
- The full commit ID appears in `revision`.
- The commit URL appears in `revision_url`.
- `analyzed_at` reflects the date the analysis was actually performed.
- Important architectural claims point to concrete implementation locations.
- Strengths and risks are supported by evidence.

## Integrate the comparative overview

Read `content/methodology/overview-report-format.md` and the complete `content/overview.md`. Integrate the new system throughout the comparison instead of appending an isolated summary.

Review and update every applicable area:

- Title metadata and prose that states the system count.
- Taxonomy and category membership.
- Comparative matrix.
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

Review every match and search for a spelled-out version of the current count. Do not mechanically change unrelated section numbers or commit IDs.

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

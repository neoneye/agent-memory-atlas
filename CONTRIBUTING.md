# Contributing

The reader-facing version of this page, with the reasoning behind each rule, is
[neoneye.github.io/agent-memory-atlas/contributing/](https://neoneye.github.io/agent-memory-atlas/contributing/)
— source in [`content/contributing.md`](content/contributing.md). This file is
the mechanical half: what to run, and what the build will refuse.

Open an issue or pull request here, or talk first on
[Discord](https://neoneye.github.io/agent-memory-atlas/discord.html).

## Correct a report

The most useful contribution, and the cheapest. Every report header pins the
exact commit it was read at, so a correction is decidable: name the claim, name
what the code at that pin does, give a path.

- Wrong at its own pin → fixed, and the report's `## History` section records
  what was wrong.
- Right at its pin, but the system moved → a re-analysis. Use the
  `reanalyze-memory-system` skill, which covers re-pinning and the
  rename-and-redirect convention.

Disputing a capability mark has its own procedure in
[`content/methodology/atlas-rubric.md`](content/methodology/atlas-rubric.md).

## Add a memory system

**Screen the checkout before reading a file of it.** Not optional:

```sh
python3 scripts/screen_repo.py /absolute/path/to/source-repository
```

Read every `RUNS` finding first. `NOTHING SCANNED` is a finding, not a pass, and
so is `FRESH` — never install a third-party dependency published in the last
seven days. Record the outcome in the report's History entry.

Then follow [`.agents/skills/add-memory-system/`](.agents/skills/add-memory-system/SKILL.md),
which scaffolds the report, pins the commit, and walks the code review:

```sh
python3 .agents/skills/add-memory-system/scripts/scaffold_report.py \
  /absolute/path/to/source-repository \
  --slug example-system --title "Example System" \
  --eyebrow "Local hybrid memory" \
  --description "A concise architectural description grounded in the implementation."
```

Scope bar: memory that outlives a session. Novelty is not required, and a
restrictive licence is a caveat rather than an exclusion.

## Before you open the PR

```sh
npm run build && npm run test
```

The suite is the review. It checks pins against the analyzed revision, every
relative link and anchor, spelled mechanism counts against the live corpus,
capability marks against their evidence records, History ordering, Mermaid
syntax that only fails at render time, pattern stance against the patterns
index, and that every report carries a diagram.

Several checks ship a `--self-test` that injects a fault into a scratch copy and
requires the check to fail. Add one to any check you write: a checker nobody has
seen fail is a checker nobody knows is running.

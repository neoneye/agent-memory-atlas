# Agent Memory Atlas

A code-grounded field guide to memory systems for AI agents.

The atlas compares memory units, storage models, write paths, retrieval mechanics, correction semantics, trust models, agent integrations, and operational risks across systems whose source is publicly readable — most open source, fifteen of them not, which the atlas names rather than averages over. Every report links to the exact Git commit that was analyzed.

## Read the atlas

Visit [neoneye.github.io/agent-memory-atlas](https://neoneye.github.io/agent-memory-atlas/).

## Discuss

Questions, corrections, and systems worth adding are welcome on Discord: [neoneye.github.io/agent-memory-atlas/discord.html](https://neoneye.github.io/agent-memory-atlas/discord.html). That page redirects to the invite, so the invite code stays in one file and can be rotated without editing every place it has been shared.

## Repository structure

- `content/systems/` — individual repository reports.
- `content/patterns/` — reusable memory architecture pattern guides.
- `content/overview.md` — cross-system comparative analysis.
- `content/methodology/` — the review and synthesis formats.
- `site/` — the designed homepage and the `/discord.html` invite redirect.
- `templates/` — the shared document-page template.
- `assets/` — styles, behavior, and social-preview media.
- `docs/` — generated static site published by GitHub Pages.
- `AGENTS.md` — the entry point for an AI agent: what to read to build memory for a product, in what order, and what not to read.
- `.agents/protocol/` — the machine-readable half: portable acceptance tests with stable ids, and the build-brief, closure-report and lock-file formats.
- `.agents/skills/use-the-atlas/` — designing memory for another product from the atlas: profile, brief, approval, then code.
- `.agents/skills/screen-repository/` — the security screen every checkout passes before it is read or run.
- `.agents/skills/add-memory-system/` — the repeatable workflow for researching and integrating another memory system.

## Add a memory system

Screen the checkout first — `python3 scripts/screen_repo.py <path>` reports auto-executing hooks, build-time execution and unpinned dependency surfaces without running anything from the tree. Then invoke the repository-local `$add-memory-system` skill with the path to a source checkout. It pins the analyzed commit, scaffolds the report, guides the code review, updates applicable design patterns, integrates the comparison and homepage, and validates the generated site.

## Build locally

The build requires [Pandoc](https://pandoc.org/).

```sh
npm run build
npm run serve
```

Then open `http://localhost:4173`.

## License

MIT

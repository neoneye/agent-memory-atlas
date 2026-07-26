# Agent Memory Atlas

A code-grounded field guide to memory systems for AI agents.

The atlas compares memory units, storage models, write paths, retrieval mechanics, correction semantics, trust models, agent integrations, and operational risks across open-source systems. Every report links to the exact Git commit that was analyzed.

## Read the atlas

Visit [neoneye.github.io/agent-memory-atlas](https://neoneye.github.io/agent-memory-atlas/).

## Repository structure

- `content/systems/` — individual repository reports.
- `content/overview.md` — cross-system comparative analysis.
- `content/methodology/` — the review and synthesis formats.
- `site/` — the designed homepage.
- `templates/` — the shared document-page template.
- `assets/` — styles, behavior, and social-preview media.
- `docs/` — generated static site published by GitHub Pages.

## Build locally

The build requires [Pandoc](https://pandoc.org/).

```sh
npm run build
npm run serve
```

Then open `http://localhost:4173`.

## License

MIT

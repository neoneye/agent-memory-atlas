# The framework that explains the DeepSeek correction

**Status:** examined, excluded, no report. Recorded because the exclusion is
trivial and the reason it was worth looking is not: this is the runtime whose
design produced [the DeepSeek Harness correction](../content/overview.md#known-limitations)
made the same day, and it generalises into a reading rule.
**Subject:** [cordiverse/cordis](https://github.com/cordiverse/cordis), read on
2026-08-14 at
[`8cc9e33fab69e2d0476d126baaf2acb24e6a6ab4`](https://github.com/cordiverse/cordis/commit/8cc9e33fab69e2d0476d126baaf2acb24e6a6ab4),
a commit dated 13 August 2026.

## The exclusion takes one grep

Cordis is *"a Meta-Framework of Spatiotemporal Composability"* — a dependency-injection
and plugin-lifecycle runtime, MIT, 8,355 lines of TypeScript across 57 files in
nine packages (`core`, `loader`, `group`, `include`, `hmr`, `timer`,
`logger-console`, `create`, `utils`). It is the substrate
[DeepSeek Harness](../content/systems/deepseek-harness/) is built on, and its
documentation is hosted on the harness's own site.

Case-insensitive whole-word counts across every `.ts` file outside
`node_modules`:

| Term | Hits |
| --- | ---: |
| `recall`, `remember`, `persist`, `storage`, `durable`, `embedding`, `vector`, `sqlite`, `database`, `forget`, `retrieve` | **0 each** |
| `memory` | 1 |
| `store` | 35 |
| `session` | 39 |

The single `memory` is a comment in `packages/loader/src/index.ts:130` —
*"Loader's root tree is in-memory; writes are no-ops"* — sitting directly above
a `write()` whose body is that comment and nothing else. The 35 `store` hits are
two in-process dictionaries: `Dict<Entry>` in `config/tree.ts`, the plugin
config tree, and `Dict<symbol>` in `config/isolate.ts`, which maps a service
name to a unique symbol per realm. The 39 `session` hits are a test fixture in
`packages/core/tests/` exercising event filtering.

`rg 'writeFile|readFile|fs\.'` across `packages/loader/src` returns nothing. The
framework does not write to disk at all.

So: nothing survives a session, nothing is retrieved, nothing is a claim. Not
close, and not interesting on its own.

## Why it was worth reading anyway

The atlas corrected the DeepSeek Harness report on 14 August because that report
described cross-session full-text search and five model-facing history tools as
what the harness does, when both are absent from every shipped composition. The
correction's one-line diagnosis was *reading the mechanism and not the
composition that mounts it*. Cordis is why that gap is as wide as it is.

Its thesis, which DSH restates as **everything is a plugin**, is that a system
is a *composition* rather than a program: capabilities are packages, a
deployment is a list of `- id: … name: …` rows in a patch file, and
`config/isolate.ts` gives each subtree its own service symbols so two plugin
groups can each hold a different `ctx.foo` without seeing each other. That is a
good design and it has a consequence for anyone reading such a tree:

> **In a DI-composed system, "the capability is implemented" and "the capability
> is present" are independent facts, and only the second is a property of the
> product.**

In a monolith those two collapse — if the code is in the binary and reachable,
it runs. Cordis deliberately pulls them apart, and it provides no signal at the
implementation site that the implementation is unmounted. `tool-session-query`
looks exactly the same in the tree whether every bundle mounts it or none does;
the only place the answer lives is `packages/bundle/*/cordis.patch.yml`. In that
particular case the package README did say so — *"shipped host compositions do
not mount it by default"* — but a README sentence is a courtesy, not a
structural guarantee, and the next such package need not have one.

## The reading rule this produces

For any system built on a plugin or DI runtime — Cordis here, but the same
applies to a Cargo feature matrix, a Spring profile set, a Nix module list, or
anything with a composition file — **the composition is a required artifact, not
an appendix.** Concretely, before writing about what a system does:

1. Find the shipped composition(s), not the example ones. In this family they
   were `packages/bundle/{base,headless,web-app}/cordis.patch.yml`; the
   compositions under `examples/` and `tests/` mount things the product does not.
2. Grep the composition for the package that implements the mechanism you are
   about to describe. Absence is the finding.
3. Check the *config* the composition passes, not only the component's schema
   default. DSH's `session-query-sqlite` schema-defaults `openAt` to `startup`
   and every bundle overrides it to `never` — reading the default would have
   given the wrong answer even after finding the mount.

Step 3 is the one that would have caught it fastest and the one most likely to
be skipped, because a schema default reads like an authoritative statement about
behaviour and is only a statement about the component in isolation.

None of this is new as a principle. What is new is that the atlas has now been
wrong about it once, in a report it was otherwise happy with, and the
[per-repo report format](../content/methodology/per-repo-report-format.md)
currently asks section 3 what has to be running and section 8 how the agent
integrates, without asking anywhere *what the shipped composition actually
mounts*. Worth adding as an explicit prompt, in the same spirit as the
monotonicity check proposed in
[the teaching-corpus note](2026-08-14-a-teaching-corpus-and-the-prior-art-it-was-citing.md):
a one-line question that costs nothing when the answer is boring.

## One mechanism, noted without a claim

`config/isolate.ts` implements per-subtree service isolation by symbol: `Realm`
holds `Dict<string, symbol>`, and `access(key, create)` returns a stable
`Symbol(key + suffix)` so a service name resolves to different implementations
in different realms. It is not memory scoping — nothing is stored — but it is
the same shape as the scope-by-containment argument this atlas keeps making
about per-workspace stores ([Grok Build](../content/systems/grok-build/)'s
per-workspace `index.sqlite`, [Reflexion](../content/systems/reflexion/)'s
per-environment memory list): isolation achieved by making the wrong thing
*unnameable* rather than by filtering it out after the fact.

Recorded as an observation about the shape, not as evidence about a memory
system, because there is no memory here to be evidence about.

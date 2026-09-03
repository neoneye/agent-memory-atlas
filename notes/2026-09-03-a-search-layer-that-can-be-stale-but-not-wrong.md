# A search layer that can be stale but not wrong

**Status:** a reading, 3 September 2026, of `zvec-ai/zvec-grep` at
[`81a80f478f2d3ec76556cd3c993d0d064cc9580a`](https://github.com/zvec-ai/zvec-grep/commit/81a80f478f2d3ec76556cd3c993d0d064cc9580a).
Filed in the overview's examined-without-report list and on the benchmarks page
under vendor-run comparisons. No report. Screened before reading: no auto-run
surface, `package.json` and its lockfile changed inside the seven-day cooldown,
fifteen floating ranges under a lockfile, two `uv.lock` files 20 and 23 days
old. Nothing installed, built or run.

---

## What it is

`zg` — the CLI name — is a local-first search layer over a workspace: managed
ripgrep for exact text, BM25 over a jieba-tokenised text field, HNSW vectors
from a local or hosted embedding model, reciprocal-rank fusion across whatever
routes a query names, and one loopback MCP endpoint whose default toolset is a
single `zvec_grep_search`. Apache-2.0, 38,327 lines of TypeScript under `src/`,
19,890 lines of tests, 229 commits since 10 July 2026 from eight authors,
`v0.2.1` tagged 1 September 2026. The storage engine is Alibaba's `@zvec/zvec`,
an embedded vector database, holding two collections under `<root>/.zvec-grep/`:
file metadata with a content hash, mtime and indexed time per file, and
fragments with text, symbol fields and a vector.

It was submitted to a memory atlas because it is built to be handed to a coding
agent and its README calls it *"the local-first search layer for humans and
agents"*. It never calls itself memory, and the code agrees: a grep of `src/`
for `remember`, `forget` and `memorize` finds nothing, and every `recall` is a
retrieval-trace field.

## Why no report

The inclusion test is whether the store holds anything that could turn out to
be false. Here the store holds a derived representation of files that are still
on disk, and the only thing that can go wrong with an entry is that the file
moved on. The system knows this and has exactly one epistemic state for it:
`fresh` / `possibly_stale`, computed per hit by comparing `indexed_time` with
the file's mtime and then its SHA-256 with the stored `content_hash`, and per
search from whether the watcher has pending events or a change job is queued.
The repair is the same read that built the entry — a watcher with a 750 ms
debounce and a 5 s ceiling, a full reconcile hourly and after a 90 s gap in the
clock, a size-then-mtime-then-hash diff that promotes a file to modified only
when all three disagree.

That is a cache with a coherence protocol, and the KV-cache entry on the compare
page already draws the line: a loss that costs latency, not correctness. The
committed BrowseComp-Plus report prices the latency at 9,721 seconds and 7.9 GB
for 100,195 documents. The shepherd entry put the same distinction in four
words — *a checkpoint cannot be wrong, only stale* — and this is the second
instance, and the first with the staleness computed on the read path and
labelled in the response.

Nothing an agent says enters the store. The `full` MCP toolset has six tools;
none takes content to keep, and `zvec_grep_index` takes a root and re-reads the
files. So there is no write arm whose output could later be corrected, which
is the thing a memory system has and a search index does not.

The exclusion is the boundary note's first kind and will not reverse on a
release. The roadmap's four directions — more formats, graph retrieval, a GUI,
mobile — add retrieval and never a store of anything but the files.

## Two things worth taking

**The remote-embedding consent surface.** A search or index that would send
text to a hosted `qwen` provider is first planned into a disclosure —
`queryText` true or false, `workspaceContent` of `none`, `changed` or `full`.
Absent a standing grant, the MCP server answers with `inputRequired` carrying a
signed, single-use `requestState` and a form: *allow once*, *allow for this
workspace*, *use FTS only*, *cancel*, defaulting to cancel. A workspace grant is
HMAC-SHA256-signed with a key under `~/.zvec-grep/`, fingerprinted on the
canonical roots, provider, model and endpoint, and stored in the workspace's
own `.zvec-grep/authorization.json`, so a grant for one root under one model at
one endpoint says nothing about any other. A memory system that ships its
embeddings to a hosted provider faces the same question about the memories
themselves. The shape — name what leaves, default to refusal, bind the grant to
a fingerprint and sign it — is the answer, and it is more carefully built than
the memory half of most systems in the corpus.

**The per-miss retrieval diagnosis.** `trackEntityId` forces a named entity
into the candidate set and records, per route, why it did not come back —
*"Target entity did not match the FTS query"*, *"Target entity file was
excluded by the path filters"*, *"Target entity could not be scored by vector
search"* — beside the rank it would have had. The benchmarks page keeps noting
that memory systems score retrieval as a black box; this is the explainer
those systems could ship.

## The benchmarks, read per artifact

`benchmarks/README.md` is the most explicit statement of the "them plus us"
protocol's terms I have read: only tool access differs between arms, index
preparation timed separately, the judge blind to the arm, references held
outside the indexed corpus, and a warning that *"rules that force or forbid
either tool bias the evaluation toward particular scenarios"*.

The two halves then diverge on what is committed. BrowseComp-Plus ships its run
report: 100 cases, three trials per arm, accuracy 98.67% against 99.00% — the
claim is cost, not quality — with tokens −37.56%, tool calls −43.52%, agent time
−38.58%, a both-correct subset, a per-case improved/regressed split, and a
leakage check showing zero baseline invocations of the tool. SWE-QA ships the
harness, the pinned selection and the isolated references, and no result: its
headline exists only as string literals in an SVG generator under `.github/`.
The same generator captions the BrowseComp-Plus panel *"80 cases · 2
trials/profile"* over numbers that recompute from the 100-case, three-trial
report, and the root README says the Codex arm ran at medium reasoning effort
where `benchmark.toml` and the report say `high`. Small, checkable, and the
reason the rule on that page is per number rather than per project.

## What this changes for the method

Nothing new, one confirmation. The reviewer's trap from the boundary note held:
the best-engineered part of this tree is the consent surface, and it is not
memory. Reading for engineering quality pulls toward it; the scope test has to
be asked of the store, not of the code around it.

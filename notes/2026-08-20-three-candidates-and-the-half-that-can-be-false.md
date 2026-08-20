# Three candidates, and the half that can be false

**Status:** triage. Three repositories read at a pinned commit on 2026-08-20 —
one excluded, two in scope with no report written yet. Each was screened before
a file was read; nothing was installed and nothing was run.
**Origin:** three URLs submitted in sequence. They have nothing to do with each
other, and the same shape turned up in all three.

---

## The shape

In each of these three, the durable state splits into a half that cannot be
wrong and a half that can — and the half that can be wrong is the half nothing
is defending.

- **OpenWolf** writes its mechanical half from hooks on every turn and leaves
  its belief half to a weekly cron that replaces the whole file with a model's
  stdout.
- **piodide** keeps nothing that can be wrong at all, which is why it is
  excluded — and says so to the model in its own system prompt.
- **sift-kg** rebuilds its graph from retained extractions, which is the
  virtue the atlas asks for, and the rebuild is exactly what discards every
  human rejection.

The falsifiability test the atlas uses at the boundary — *could the surviving
thing be false?* — turns out to sort the internals of a single system as
usefully as it sorts systems from non-systems.

---

## OpenWolf — `cytostack/openwolf` at [`7defd81b`](https://github.com/cytostack/openwolf/commit/7defd81b9faacea0134965e539118efb2a890cba)

Middleware for coding agents (Claude Code, Codex, OpenCode, Cursor,
Antigravity), v2.1.0, AGPL-3.0-only, ~12.9k lines of TypeScript.
Screened: 0 auto-run hooks, 1 build-time `prepublishOnly`, two dependency
surfaces changed the same day — inside the seven-day cooldown, so read-only.

**In scope.** `.wolf/cerebrum.md` holds User Preferences, Key Learnings,
Do-Not-Repeat and a Decision Log. Those survive the session, carry an identity,
and can be false.

**The finding: the only code path that writes a belief replaces the whole file
with model stdout, routed by substring.** `src/daemon/cron-engine.ts:403-413`.
A weekly cron pipes cerebrum to `claude -p` with a prompt that says to remove
Do-Not-Repeat entries older than 90 days *"if no longer relevant"*, strips code
fences from the reply, and then:

```
try   JSON.parse(result)  → suggestions.json
catch if result includes "## User Preferences" | "## Key Learnings" | "# Cerebrum"
      → writeText(cerebrum.md, result)
```

No merge, no diff, no backup, no record of what was dropped. The output sink is
chosen by string sniffing, so the sibling `project-suggestions` task — same
schedule, same context files — lands in the same branch whenever its JSON parse
fails and its prose happens to carry one of those headings. A user's correction
is deletable by a model's judgement of relevance, and nothing records that it
happened. [ByteRover](../content/systems/byterover.md) is praised in the
comparative report for the inverse of this: parse before and after, count only
what would be removed, merge it back.

**And the system ships a detector for the failure it cannot fix.**
`src/tracker/waste-detector.ts:83` fires `cerebrum_stale` after fourteen days
with the suggestion *"Learning may not be active. Check if cerebrum is being
updated by hooks."* No hook updates cerebrum. Outside that one cron job it grows
only when the model obeys a markdown instruction in the generated
`OPENWOLF.md` — the [Cline Memory Bank](2026-08-07-three-coding-agents-and-where-their-memory-isnt.md)
shape, in a project whose other memory is fully wired.

`memory.md` consolidation is destructive by default: the daily job collapses
sessions older than seven days to `> Consolidated session (N actions)` and drops
the rows, with an idempotency guard that keeps a re-run from rewriting the count
to zero. Care spent on the counter, not on the evidence.

**What is worth taking.** `src/cli/memory-migrate.ts` mirrors cerebrum sections
into Claude Code's own auto-memory directory with a content hash in the
frontmatter, a byte cap that drops oldest-first, an idempotent write — and, when
a section empties, an `unlink` of the mirrored file so *"stale advice does not
outlive its cerebrum source."* `src/hooks/session-start.ts` then detects the
sync marker and suppresses its own Do-Not-Repeat injection, so the list is not
paid for twice. That is enumerated-derived-copy deletion plus double-injection
avoidance, across two memory systems, in middleware. `tests/anatomy-store.test.ts:267`
also commits *"empty/corrupt anatomy.md never wipes preserved content"* — a
guard against [the empty-read defect class](2026-08-20-a-failure-that-reads-as-empty.md)
found in fx the same week.

**Provisional marks: 1 of 7.** `negative_eval` in the weaker of the two
strengths — the assertions keep material out of a projection (symbols must not
render into `anatomy.md`, sensitive files must not reach it) rather than out of
a read path. Withheld with reasons: scope is filesystem location rather than a
key the read path filters; the audit records file actions rather than memory
mutations and is destructively consolidated; the dashboard displays cerebrum and
cannot edit it, so the review surface is a viewer.

## piodide — `daugasauron/piodide` at [`ad47ef59`](https://github.com/daugasauron/piodide/commit/ad47ef59a500ba26b494dbb05fc5d0ed4e4b6aa2)

A coding agent, Python runtime, shell, editor and local model host in one
browser tab. MIT. Screened: 0 auto-run, 2 build-time Makefiles, and one
dependency that is not a registry package — `ghostty-web` from a commit-pinned
GitHub archive tarball.

**Excluded: nothing survives the session, so the correctability question never
arises.** The README says a refresh clears the workspace and the code agrees,
which is worth checking rather than accepting, because that is the claim this
corpus most often finds contradicted:

- `src/browser-sessions.ts` is the session store and it is a `Map`. `save()`
  writes to the map; `exportCurrent()` returns an object, not a file. Its own
  comment says the branches *"intentionally disappear on refresh along with
  Pyodide MEMFS."*
- The workspace is one Pyodide MEMFS at `/home/web` shared by the agent's file
  tools, Python, Neovim, git and the WASI programs, and it dies with the tab.
- `src/` contains no OPFS write site at all. The OPFS handles live inside
  `@mlc-ai/web-llm`'s cache manager, which piodide calls to stream known GGUFs.
  Model weights and two `sessionStorage` flags sequencing a service-worker
  reload are the entire durable surface, and neither is a claim that can be
  false.

**A second clean instance for [the vocabulary probe](2026-08-19-the-vocabulary-probe-lies.md).**
Every `memory` hit in the tree is `MemoryFs` — the WASI in-memory filesystem —
or `WebAssembly.Memory`. A grep-based screen returns dozens of hits and is wrong
in every one, which is the systems-sense poison the note names from SAM. The
tell is that all the hits sit in `src/wasi/` and its tests.

**Three mechanisms kept anyway.** The durability contract is stated *to the
model* — `src/main.ts:107`: *"The runtime and filesystem persist for this page
only. A refresh destroys them."* Most systems in this corpus never tell the
agent what its memory guarantees are, and an agent that does not know its store
is ephemeral will promise a user that it will remember. `docs/workspace.md`
carries a Lifetime table enumerating every state class against where it lives,
which is the enumerated-copies discipline applied to volatility rather than to
deletion. And the `html` tool's description names the storage APIs that will
silently fail in an opaque-origin `srcdoc` — localStorage, sessionStorage,
IndexedDB — so the model does not write code that appears to save and does not.

## sift-kg — `juanceresa/sift-kg` at [`d786991c`](https://github.com/juanceresa/sift-kg/commit/d786991c024f5401f113fc0cb70aee96dd1bd3bf)

A CLI that turns document collections into a browsable knowledge graph:
ingest → LLM extraction → build → resolve → interactive review → apply. MIT,
56 Python files, 13,547 lines, no commit since 2026-05-11. Screened: 0 auto-run,
a `tests/conftest.py` that executes on pytest collection, no lockfile beside
`pyproject.toml`.

**In scope**, and the bundled skill is why: `.agents/skills/sift-kg/SKILL.md`
tells an agent to treat the graph as *"your persistent, structured memory of the
user's world"*, to orient from `sift topology` at session start and to query it
before answering. The model's surface is read-only — `info`, `topology`,
`query`, `search` — but an extracted entity or relation can be false, carries an
id, and there is a human surface for adjudicating it.

**The finding: the corrections live downstream of the artifact that regenerates
them.** Three layers, and the rebuild input is the one without the decisions in
it.

| Layer | Written by | Read by `sift build` |
| --- | --- | --- |
| `extractions/*.json` | `sift extract` (LLM, per document) | yes — the whole input |
| `graph_data.json` | `sift build`; merges applied and rejected relations removed here | no, it is overwritten |
| `merge_proposals.yaml`, `relation_review.yaml` | `sift resolve`, then the human in `sift review` | no |

`build` calls `load_extractions(output_dir)` and `build_graph(extractions, …)`
and saves over `graph_data.json`. It does not load the existing graph and
consults neither decision file. So every applied merge and every rejected
relation is undone by the next build — and the bundled skill instructs the agent
to run exactly that whenever the user adds documents.

**The sharper half is that both semantics are in one function, twenty lines
apart.** In `src/sift_kg/cli.py` the `resolve` command writes merge proposals
with `write_proposals(merge_file, proposals_path)` and no prior read, so every
`CONFIRMED` and `REJECTED` status is truncated back to fresh `DRAFT`s —
`write_proposals` opens with `"w"`. The relation-review branch immediately
below reads the existing file, builds `existing` from
`(source_id, target_id, relation_type)` and extends only with triples not
already present, so a relation already adjudicated is never re-asked. One review
system remembers decisions keyed on the value; its sibling overwrites them.

And the surviving guard cuts the wrong way. Because the relation dedupe is keyed
on the triple regardless of status, a relation the user rejected — removed from
the graph at apply time by `resolve/engine.py:152-179`, symmetrically — comes
back into `graph_data.json` on the next build from the extraction that produced
it, and is then *not* re-flagged for review, because the triple is already in
the file. The correction is reverted and the surface that would have caught it
is suppressed by its own memory of having asked once.

**The status field is the near-miss worth naming.**
`StatusType = Literal["DRAFT", "CONFIRMED", "REJECTED"]` is a discrete state
rather than a float, and the confidence float lives separately on each merge
member — the split the atlas asks for. It does not earn `trust_state`, because
the state is a property of a *proposal* and withholds nothing: no entity is kept
out of a read because of it.

**Provisional marks: 1 of 7.** `human_review` — `sift review` is an interactive
approve/reject surface over proposed merges and flagged relations, and it is the
product's centre rather than a viewer. Everything else no, on the reading above.
Entities and relations do carry `context` and `evidence` quotes from the source
text, so the raw layer is retained and the derived layer is genuinely
rebuildable; that property is what makes this a good example rather than a
careless one.

---

## What this leaves open

Two reports are not written. OpenWolf and sift-kg both clear the bar and both
have a finding sharper than the average report in the corpus. Against that,
[the widening note](2026-08-09-widening-and-its-falling-marginal-value.md) asks
whether a *pattern* would move rather than whether a report could be written,
and both would move one:

- OpenWolf against **memory as an editing surface** and against whatever page
  ends up holding *a model's stdout is not a merge*.
- sift-kg against **evidence before belief**, which currently argues that a
  rebuildable projection is the safe design. It is — for the evidence. This is
  the case where the rebuild is also what reverts every correction, because the
  corrections were applied to the projection and the rebuild input never learned
  about them. *Rebuildable* is not one property, and
  [the log and the projection](2026-08-03-the-log-and-the-projection.md) already
  says the word means two things; this adds a third reading, where the
  projection holds state the log cannot reconstruct.

## For next time

**A rebuildable projection is only safe if every correction is an input to the
rebuild.** Ask, of any system that regenerates a derived store: where does a
human decision live, and is that file on the read path of the regeneration? If
the answer is that decisions are applied to the output, the design has a
scheduled undo.

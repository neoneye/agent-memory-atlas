# Three re-reads, and a trust state with four writers and no reader

**Status:** three systems re-read at commits newer than what the atlas pins.
**No pin advanced, no mark changed, no report rewritten** — a re-pin is a claim
about the whole report, and none of these got a whole re-reading. What follows
is what the next re-pin has to fold in.
**Origin:** three URLs submitted together for re-analysis. Each new checkout was
screened again before anything was read; nothing was installed and nothing was
run.

---

## llm-wiki-memory — a dormant repository woke up

Pinned at [`b7cc76a4`](https://github.com/ctxr-dev/llm-wiki-memory/commit/b7cc76a493573baac133969b324a874990556146),
last read 2026-08-06, when the History entry recorded that no commit had landed
since 18 July. Since then: **29 commits, 510 files, +55,114 / −7,087.** A webapp
(F0–F7), EmbeddingGemma on Transformers.js v4 with worker-thread inference and
bounded cold embeds, a migration registry and runner, judge-gated distillation.
Screened again: 1 auto-run surface (`AGENTS.md`, read as data), 50 floating
ranges behind a lockfile.

**The finding is an epistemic state that is written correctly and read nowhere.**
`mcp-server/mcp-judge-gate.mjs` adds a fail-closed quality judge to the MCP write
path: the judge runs once, a fail returns the verdict and recommendation without
writing, a provider outage blocks the write rather than dropping it silently, and
`write.acceptQuality:true` stores the best attempt stamped
`memory.quality:"unverified"`.

That flag is durable and carefully plumbed:

| Role | Sites |
| --- | --- |
| Writers | `mcp-write-dispatch.mjs:145`, `compile-actions.mjs:98`, `consolidate-llm-merge.mjs:136`, `consolidate-llm-refresh.mjs:238` |
| Preservers | `wiki-identity.mjs:143`, `recall.mjs:275` |
| Clearers (a passing rewrite) | `consolidate-llm-merge.mjs:137`, `consolidate-llm-refresh.mjs:239` |
| **Readers that filter, rank or branch** | **none** |

Every non-test reference is a write, a pass-through or a delete. The single hit
inside `recall.mjs` is on the *write* side, rebuilding metadata during a save,
and its comment gives the reason to keep it: pass the flag through *"else the
flag is dropped and consolidate/recall can't treat the leaf cautiously."* The
repository's own rule template is franker — *"a reserved affordance for the read
side; the flag is always preserved on the leaf."*

So `trust_state` stays withheld, and this is the informative kind of absence
rather than a gap: the state exists, is discrete, survives consolidation, has a
clearing path and a committed test, and nothing consults it. It is the
[declared-and-unwired](2026-08-18-the-producer-check-and-a-corpus-audit.md)
family with the halves reversed — the producer is real four times over and the
consumer was never written.

**Marks unchanged at 2 of 7**, with `human_review` now much stronger than the pin
records: the webapp edits through the engine rather than displaying.
`negative_eval` still not earned — the closest committed cases
(`cron-healing.test.mjs:82`, `consolidate-llm-passes.test.mjs:240`) assert
internal invariants and stored bodies, not that material must not come back from
a read.

**And the incident.** `test/real-brain-guard.test.mjs` is a regression guard whose
header describes what it is guarding: a test that failed to isolate
`MEMORY_DATA_DIR` — a static engine import froze it to the default before
`setupWorkspace` ran — read *and wrote* the developer's real
`~/.llm-wiki-memory` and hard-deleted about **590 real leaves**. `env.mjs` now
refuses the real brain under `LWM_FORBID_REAL_BRAIN`, and `test/setup-guard.mjs`
arms that marker from a preload and redirects an unset or real data dir. The
largest deletion event in this memory system's history was its own test suite,
and the fix is a guard that fails closed on the path rather than a convention
about fixtures.

## PLUR1BUS — maintenance work that starved the write path

Pinned at [`3479373f`](https://github.com/Cyb3rb1ade/openclaw-plur1bus-memory/commit/3479373f87dc8f70d460d09ddeb20ffb83355231),
release 7.4.0. Three commits since: one substantive fix, a changelog and a
lockfile bump to 7.4.1. Screened again: the same `postinstall` host patch, two
manifests inside the cooldown. No published claim goes stale; marks unchanged at
seven of seven.

`drainEmbeddingQueueFile` was bounded only by item count — default 250 — and ran
**before** capture inside the same sixty-second budget. With a full backlog the
drain spent the entire budget and capture was aborted every time. The commit
message carries the production evidence from 2026-08-20:
`found 276 texts to capture` followed by `capture worker timed out after 60000ms`
roughly 30 ms later, the timer already nearly sixty seconds old when capture
began.

The fix moves the drain after capture into whatever budget remains, honours
`options.signal` and a new `options.deadlineMs`, and reports `stoppedEarly` —
previously the loop did not break at all, so the `AbortError` surfaced deep in
the embedder instead of at the loop boundary. A second defect is fixed in the
same change: a missing `await` before `pool.withDb`, without which the `finally`
ran while capture was still going, which is the concurrency the rework exists to
remove. Committed as `tests/neo-embedding-drain-budget.test.js`.

**This is a failure mode
[recoverable background work](../content/patterns/recoverable-background-work.md)
does not have.** The pattern covers a job that fails and loses its inputs. Here
the job succeeded, kept its inputs, and starved the write path it exists to
serve — and the only observable was a log line announcing the 276 texts it was
about to drop. The generalizable form: **a maintenance pass and the write path it
serves must not share one deadline, and if they must, the write path goes
first.** Worth adding to that page's failure section with this instance behind
it.

Worth crediting separately: the commit message explicitly separates this from a
same-day outage with a different cause — a host-side timeout with failover to a
262k model. Distinguishing two correlated failures in a commit log is rare.

## har — the exclusion holds, and the mechanism it was kept for hardened

Not a report. [The 2026-08-07 note](2026-08-07-a-harness-that-reinvented-the-tombstone.md)
excluded `os-factory/har` and kept three mechanisms; its addendum re-read at
0.55.0. Now at [`f6ec0fb8`](https://github.com/os-factory/har/commit/f6ec0fb87c0db8226bbce8db5481c7c6f2ba2987),
release 0.62.1: **32 commits, seven minor releases, +11,697 / −1,153 across 184
files**, and the tree grew from 16,065 to **40,925** TypeScript lines.

**The exclusion is firmer than when it was written.** The memory-vocabulary probe
now returns three hits in 40,925 lines, and all three are unrelated: *"Remember a
repo so Mission Control can sync it"*, a *"fire-and-forget"* comment, and a
shell-output test. The project more than doubled in size and added no memory
surface at all.

The mechanism the note kept it for is now explicit and larger.
`src/core/control-unregister.ts` is a dedicated module: unregistering prompts
with a default of No and *proposes* worktree deletions rather than performing
them. `control-sync.ts:62` documents `force` as *"Re-register even if the path
was previously unregistered"*; `control-sync.ts:597` drops a previously
unregistered path from the local registry *"so auto-sync stops retrying"*; and
`cli/commands/control.ts:352` names the thing outright — an **unregister
blocklist**, cleared only by an explicit `control reset` that reports how many
entries it removed. A refusal keyed on the value, consulted by the loop that
would otherwise re-assert it, overridable only on purpose, and countable when
cleared.

Still not memory, and for the same reason as before: the refusal is about
whether a path is synced, not about a claim that could be false. The boundary
test the exclusion rests on is unchanged, which is the point of re-running it.

---

## What this leaves for the next re-pin

- **llm-wiki-memory** needs a full re-read, not a History entry. Five hundred
  files moved and the report describes a version of the system that predates the
  webapp, the judge gate and the embedding stack. The `quality` finding above is
  the thing to verify first at whatever commit that reading pins, because it is
  the one that decides a mark.
- **PLUR1BUS** does not. Three commits do not justify re-asserting 10,867 lines
  of `index.js`, and the drain finding can be carried without moving the pin.
- **har** needs nothing but the addendum.

## For next time

The three re-reads produced three different kinds of result — a mark-deciding
finding, a pattern-page gap, and a confirmed absence — and only the first is what
"re-analyze" usually means. The confirmed absence is worth as much: an exclusion
whose reasoning was checked against a tree that doubled in size is a much
stronger exclusion than one written once. Re-running a *boundary* decision is
cheap and nothing in the workflow currently asks for it.

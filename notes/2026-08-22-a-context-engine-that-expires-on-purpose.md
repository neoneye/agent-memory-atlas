# A context engine that expires on purpose

**Status:** triage. One repository read on 2026-08-22 and again on 2026-08-27
at [`ca09efa022eb64fcfe283ed98791728b304c1068`](https://github.com/Perseus-Computing-LLC/perseus/commit/ca09efa022eb64fcfe283ed98791728b304c1068),
no report. Screened before each reading; nothing installed or run.
**Origin:** submitted as a re-analysis of Perseus Vault. It is a different
repository.

---

## The two Perseuses

The atlas has a report on
[Perseus-Computing-LLC/perseus-vault](https://github.com/Perseus-Computing-LLC/perseus-vault).
[Perseus-Computing-LLC/perseus](https://github.com/Perseus-Computing-LLC/perseus)
is a **separate repository from the same organisation** — 882 commits since
18 May 2026, MIT, published to PyPI as `perseus-ctx`. The pinned sha of the
Vault report does not exist in it. Anyone reconciling this org by project name
rather than by URL will merge them, the same hazard already recorded for
`agentmemory` and for the two Engrams.

## Why it gets no report

The project draws the atlas's own scope boundary, in its own README, before
anyone else has to:

> Perseus resolves and shapes the active working context; Perseus Vault owns
> durable-memory persistence and recall.

and defines the terms it is separating — *active working context* is "the
current, task-relevant workspace state — files, services, tasks, and other facts
that can change," resolved **at render time**; *durable memory* is "information
intended to survive session boundaries," and belongs to the Vault. The product
is a renderer: `perseus render .perseus/context.md -o AGENTS.md` writes the file
the assistant loads at session start, kept live by `perseus watch`. Nothing it
resolves is a belief that could later turn out to have been false. A stale
render is repaired by rendering again, which is the definition of not being
memory.

The one thing that does survive a session is the checkpoint store, and reading
it settles the case rather than complicating it. `cmd_checkpoint` writes
`{version, written, task, status, next, notes, workspace, stale_after}` as a
timestamped YAML file, under `max_keep: 30` and a `ttl_s` defaulting to 86,400.
**The record ships with an expiry**, because a run record's value is that it
stops being relevant — which is the cleanest illustration yet of the boundary
the compare page draws: *a store of the agent's work is not a store of the
agent's beliefs*. Third worked case, after the beads and the run-record note
above.

`@memory` is a directive that pulls Vault-backed recall into the render, so
Perseus is a **consumer** of a memory system rather than one. That is an
integration surface, and the report it belongs in is the Vault's.

## Not in scope, and not nothing to learn

Two things worth carrying, on the standing rule that those are different
verdicts.

**The checkpoint lock is built for the case most single-user tools ignore.**
`O_CREAT | O_EXCL` for atomicity across NFS, a PID-liveness probe that uses
`OpenProcess` on Windows because `os.kill(pid, 0)` there calls
`TerminateProcess`, and — the good one — `PermissionError` treated as *alive*:

> EPERM — the process EXISTS but belongs to another user. Cross-user is the
> NORMAL case for agents sharing a checkpoint store over NFS/SMB; treating it as
> dead let a second writer unlink a live lock and clobber. Only ESRCH means dead.

A stale-lock reclaim that reads EPERM as death is a bug that only appears when
two people's agents share a directory, which is exactly when it costs the most.

**Natural-sort the filenames or prune the wrong file.** Checkpoints are
`<ts>.yaml` or `<ts>_<n>.yaml` with an unpadded collision counter, so a plain
string sort puts `_10` before `_2` and "delete the oldest" deletes a newer one.
Any store that names files by timestamp with an unpadded disambiguator has this,
and it surfaces as data loss during retention rather than as an error.

## The re-pin that was actually available

Perseus Vault itself had moved two commits, and those two are not cosmetic:
a rejected-value tombstone that now follows derived provenance, and a strict
workspace-binding path. Folded into
[the Vault report](../content/systems/perseus-vault.md) and into
[rejected value tombstone](../content/patterns/rejected-value-tombstone.md).

---

## The second reading, and why the verdict is the same

Seventeen commits later the checkpoint store is unchanged — `ttl_s` still
defaults to 86,400, `max_keep` to 30, and every record still carries the
`stale_after` it was written with. Nothing new here survives a session as a
belief. The exclusion stands.

Two things arrived that are worth recording anyway, and one of them completes a
mechanism this atlas had only half of.

**`--offline` stopped being a label.** The flag's own help text read
*"(Hidden) Enable air-gapped deployment mode. No-op."* — a declared-and-unwired
switch of exactly the kind the atlas's producer check exists to find, sitting in
the CLI of a tool sold on governed context. It is now `src/perseus/offline.py`,
415 lines whose docstring opens *"`--offline` is an enforcement mode, not a
label"*: connects, sends and name-service lookups fail closed unless they target
a numeric loopback address or a local Unix socket, with a seccomp syscall filter
installed where the platform supports one and an explicit statement that
container policy is still required for subprocesses. A no-op flag that later
becomes enforcement is the rarer direction of that finding, and worth naming as
such.

**The selection inspector is the consumer half of a pair whose producer is in
the Vault.** `src/perseus/context_inspector.py` is a read-only projection over a
run artifact: per candidate, a disposition drawn from a closed set —
`selected`, `dropped_budget`, `dropped_type_cap`, `dropped_caller_limit`,
`filtered_lifecycle`, `filtered_scope`, `filtered_policy`, `superseded`,
`abstained`, `not_in_candidate_pool` — with hash commitments over policy,
configuration, code and the projection itself, and a stated resolution of
*"commitments, bounded identifiers, source references, and digests only; raw
bodies require a separate authorized local path."* It is reachable as a CLI verb
and as the MCP tool `perseus_context_inspect`.

It also has no producer in this repository: grepping the tree for the
disposition vocabulary finds `context_inspector.py`, its tests, and the
generated single-file `perseus.py` bundle, and nothing else. The artifact it
projects comes from `perseus-vault`, where
[`9ecda85`](https://github.com/Perseus-Computing-LLC/perseus-vault/commit/9ecda85729a5eda2e80f1780d2e662a983c5076a)
(25 August 2026) added `src/selection_decisions.rs` and a
`docs/specs/selection-decisions-v1.md` under an opt-in
`include_selection_decisions` request flag. So the answer to *why was this
memory not retrieved* is produced by the memory system and rendered by the
context engine, across two repositories — which is the reason a reader
reconciling this organisation by project name will find half a mechanism and
conclude it is unwired. Folded into
[the Vault report](../content/systems/perseus-vault.md).

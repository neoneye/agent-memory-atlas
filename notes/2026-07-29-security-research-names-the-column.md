# Security research names the column, and finds nobody has built it

**Status:** done; overview.md correction and scope sections updated
**Origin:** *A Survey on Long-Term Memory Security in LLM Agents: Attacks,
Defenses, and Governance Across the Memory Lifecycle*,
[arXiv:2604.16548](https://arxiv.org/abs/2604.16548) (v2, 11 June 2026; v1 17
April 2026). Eight authors, MemTensor and Shanghai Jiao Tong University. Read on
2026-07-29 as the fourth of the recent surveys checked against the atlas.

Of the four, this is the one that matters most, and it is the only one that
links a repository.

## Why it is the important one

The other three surveys are memory research looking at memory. This is security
research looking at memory, and it arrives at the atlas's capability columns from
threat models rather than from repositories — which is the strongest kind of
corroboration available, because the two methods share no inputs.

Its frame is a **Memory Lifecycle Framework**: six phases (WRITE, STORE,
RETRIEVE, EXECUTE, SHARE & PROPAGATE, FORGET & ROLLBACK) crossed with four
objectives (Integrity, Confidentiality, Availability, Governance). Attacks are
traced as cross-phase chains — poisoned content persists, propagates, and
resists cleanup — which is a better description of the atlas's re-assertion
failure than the memory literature has produced.

Note the authorship: MemTensor is the MemOS group, and the atlas has a
[MemOS report](../content/systems/memos.md). The survey cites MemOS as partial
support for one of its own primitives. That is worth stating plainly rather than
treating the survey as a neutral observer.

## VMG against the seven columns

§5 proposes **Verifiable Memory Governance** — five primitives a long-term-memory
system must provide. The mapping is in
[overview.md](../content/overview.md); the short form:

| VMG | Atlas |
| --- | --- |
| Write Authorization | the governed write gateway pattern |
| Provenance Visibility | `audit_log` + evidence-before-belief |
| Principal-Scoped Retrieval | `scope_enforced`, nearly verbatim |
| Rollbackability | no column — append-only memory audit is nearest |
| **Verified Forgetting** | the question the atlas asks of every system |

Verified Forgetting gets a formal definition the atlas does not have and should
probably steal:

```text
VF_ε(M_t) := ∀X, Pr[ Expose_X(q, F_X(M_t)) = 1 ] ≤ ε,  q ~ Q_X
```

— a bound on the probability that any adversarial probing query re-exposes
content X after the deletion operator F_X has run, where the store must be clean
"from any substrate — including raw logs, compressed summaries, vector indices,
and propagated copies". That is the atlas's deletion test with the adversary
made explicit and the substrates enumerated, and the enumeration is better than
the atlas's own: *propagated copies* is a phase the
[benchmarks page](../content/benchmarks.md) deletion test does not currently cover.

**The paper's own status line for it is "no existing literature."** Its Figure 3
renders the five as a dependency tower with deployment maturity per layer: Write
Authorization partial, Provenance Visibility partial (MemOS, VerificAgent),
Principal-Scoped Retrieval early-stage, Rollbackability largely absent, Verified
Forgetting *no existing literature* — the only one so marked.

Three repositories in this atlas carry a value-level tombstone. None has a
paper. The literature has the definition and reports the mechanism missing; the
code has the mechanism and no definition. Each half is invisible to the other,
and that is now demonstrated rather than asserted.

### The vocabulary gap survives the survey that closes it

| Term | This survey | 107-page survey |
| --- | --- | --- |
| `provenance` | 25 | 3 |
| `rollback` | 24 | — |
| `forget*` | 25 | 52 |
| `audit*` | 13 | 5 |
| `deletion` | 12 | 2 |
| `unlearn` | 9 | 0 |
| `poison` | 48 | — |
| `tombstone` | **0** | **0** |
| `rejected` | **0** | **0** |
| `negative` | **0** | **0** |
| `tenant` | **0** | **0** |

So the *property* now has a name, a formal definition and a research programme.
The *mechanism* — a durable record of a rejected value, keyed on the value —
still has none. A reader who implemented VF from this paper would most likely
build versioned snapshots plus a membership test, and would rediscover the
tombstone by accident.

## The repository: OWASP Agent Memory Guard

The survey's single hyperlink is to
[OWASP/www-project-agent-memory-guard](https://github.com/OWASP/www-project-agent-memory-guard)
(Apache 2.0, `78b9227f5d832cfe83b1d3f01dbcb6f51235dc39`, 28 July 2026). Read in
full: ~2,500 lines of `src/`, nine test modules, semgrep rules, an MCP server,
LangChain and AutoGen integrations.

It is the closest public code to VMG, and it earns **no report**, for the reason
set out in the scope section: the only shipped `MemoryStore` is a dict, the
snapshot store is a 50-entry ring buffer in RAM, the event log is a list, and
both servers construct the guard with no store. It is a layer that expects you
to bring the durable half. The rule that excluded MemEngine applies for a
different reason — workbench versus layer — and the scope section now carries
both shapes.

What it does carry, and what the atlas would have marked if anything persisted:

- **A trust state machine, enforced.** `MemoryClass` transitions run through a
  promotion graph; `ephemeral → user_preference_candidate → verified_preference`
  sets `requires_verification=True`, and `promote()` raises without an explicit
  `verified=True`. `retrieved_fact` and `tool_observation` can never reach
  `verified_preference` at all. Writing with a conflicting class raises rather
  than silently reclassifying. This is the shape
  [trust-state-machine](../content/patterns/trust-state-machine.md) describes,
  with the human opt-in on the promoting edge.
- **Rollbackability**, the primitive the survey calls largely absent: snapshot
  before every blocked write, snapshot before every `retire_if` sweep, and
  `rollback()` restoring a labelled snapshot.
- **A self-reinforcement detector** — the only code in this atlas's reading
  aimed directly at an agent laundering its own claims into fact.

### Two findings from reading the callers

Both are the atlas's usual method and both matter more than the feature list.

**The self-reinforcement detector guards the wrong timescale for this atlas's
failure.** It fires only on `AGENT_AUTHORED` writes, over a 60-second cooldown,
against a deque of eight prior values on the same key, using a `difflib`
similarity ratio capped at 1,024 characters. That catches a tight
write-read-elaborate loop inside one session — a real attack, and the one the
module documents. It cannot catch the failure this atlas keeps finding, where a
scheduled extraction pass re-asserts a corrected value hours or days later:
the window has closed, the deque is gone with the process, and any intervening
user write resets the counter by design.

**The quarantine is the clearest near-miss on a tombstone in the atlas.** A
blocked write's value goes to `self._quarantine[key] = value`, is exposed as a
read-only property, and is counted by `metrics.py`. `rg -n "_quarantine"` over
`src/` returns exactly those three sites. Nothing consults it on a later write.
Re-submit the same rejected value and, if no detector independently matches it a
second time, it commits — and the detectors are content-pattern matchers
(injection strings, PII shapes), not a memory of what was refused. The value was
captured, held, and never used to refuse anything.

So the OWASP project built to secure agent memory implements four of the
survey's five primitives, and the one it misses is Verified Forgetting — the one
the survey says has no existing literature. Two independent artifacts, the same
hole.

## Changes made

1. **[overview.md](../content/overview.md), §Correction.** A new subsection on
   VMG with the five-to-seven mapping, the "no existing literature" status, and
   the term counts. This replaces nothing; it sits after the 107-page survey's
   paragraph as the stronger external statement.
2. **[overview.md](../content/overview.md), §Not in scope.** A fourth exclusion
   shape — *a guard is not a store* — with the OWASP project pinned, the three
   mechanisms it carries, and the two caller findings.

No capability mark moved, and no report was added. A pinned commit was read and
produced no row, which is the correct outcome when the thing read has nothing
that survives a restart.

## Worth doing next

- **Steal the VF definition** for [benchmarks.md](../content/benchmarks.md) §6.
  The current deletion test enumerates substrates informally; VF's list — raw
  logs, compressed summaries, vector indices, **propagated copies** — is better,
  and the last item is a gap in the atlas's own specification. Cross-agent
  propagation is a deletion surface nothing here tests.
- **The three tombstone holders have no paper**, and this survey is the venue
  that would want them. Recorded as an observation, not a plan.

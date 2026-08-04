# Three repositories, one report, and a harness that is not memory

**Status:** done — one report added ([Nova AI](../content/systems/nova-ai.md)),
two refusals recorded, one pre-existing count error found and fixed.
**Origin:** three URLs submitted together on 2026-08-04 —
`Whooptie/NOVA_AI`, `showjihyun/bvcounterchat`, `showjihyun/bvwebchat`.

## The one that qualified

**Nova AI** is 25,000 lines of Python built by one author for one user, running
24/7 as a local background process, and it calls **no model at all**. Its
knowledge memory is a hand-built concept graph — a word has senses, a sense has
`is_a`/`part_of`/`causes` edges, each edge carries its own `source`, `confidence`
and `created_at` — with 242 concepts committed and real provenance in the data
(`wikipedia` on auto-derived edges, `user` on supplied ones).

Two mechanisms are better than most of the corpus manages, and both exist
*because* there was no model to delegate to:

- **The write gate is a spoken question.** A parsed relation sits in a single
  `pending_relation` and is not stored until the user answers "ja" to *"Mag ik
  onthouden dat 'X' is een soort van 'Y'?"*, with sense disambiguation asked
  first. An unparseable answer re-asks rather than defaulting.
- **Corrections are quarantined from curated ground truth.** Confirmed
  classifier corrections go to their own file, are merged with `training_data.json`
  only in a local copy for the duration of a retrain, and are restored under
  `try/finally`. The docstring names the hazard — extending the instance
  attribute would have persisted corrections into the human-owned file — beside
  the line that avoids it.

And the gap is structural: `find_contradictions` works and **nothing calls it**,
while nothing anywhere removes a relation, a sense or a concept. The full
argument is in the report; what belongs here is the shape, because it is the
atlas's own thesis arriving from an unexpected direction. Correction is usually
hard because a model makes it hard. Here there is no model, the author reasoned
carefully about every epistemic transition on the way *in*, and the way *out* was
still never built. That is weak evidence that the asymmetry is not about LLMs at
all.

Licence is *"Viewable, Not Reusable"* — all rights reserved — reviewed under the
same exception already applied to OptMem, and stated in section 1 so a reader
knows the ideas are to be re-implemented rather than lifted.

## The two that did not, and why the second one was close

Neither `bvwebchat` nor `bvcounterchat` is a memory system, and neither is what
its name suggests. `bvwebchat/src` is a multi-room web chat server;
`bvcounterchat/src` is a browser 3D FPS game whose only persistence is a
kill/death/playtime stats table. **Every `memory` match in the latter is
SQLite's `:memory:` DSN** — checked rather than counted, because a file list
saying "four files mention memory" is exactly what
[hazard 3](2026-07-28-methodology-hazards.md) is about.

What is substantial in both is the **Claude Code development harness** beside the
app, and the two differ sharply there.

`bvcounterchat` has a markdown ledger and six `gate_*.py` hooks that block tool
calls. No state store. Straightforward refusal.

`bvwebchat` is the interesting one. It carries `.harness/state/` with:

| File | Holds |
| --- | --- |
| `session.json` | goal, done, next, open questions |
| `decisions.jsonl` | decisions with rationale, append-only, single writer |
| `phase.jsonl` | phase transitions with per-guard verdicts |

plus HMAC-signed state that demotes to a fail-closed `IDLE` when tampered,
atomic writes via `os.replace`, stdlib-only hooks (because "a dead hook is
fail-open"), and a `SessionStart` hook that injects a ≤15-line digest built from
it. The digest's docstring states its own selection rule: content focuses on
*"what git does not know"* — the why, the next, the open questions — and a
comment beside the transition log reads **"the transition log is the evidence,
not a person's memory."**

That passes the letter of this atlas's qualification test. Something survives the
session; it has an identity; it can be corrected.

**It was still refused, and the reason is worth writing down because it will
recur.** What survives is *workflow control state*. A phase is not a claim that
can be true or false. `decisions.jsonl` is the closest thing to a belief store
and it is a log of choices made, not of facts asserted — there is nothing for a
tombstone to key on, nothing a contradiction could exist between, and no
question the correction machinery this atlas measures would even be asked. The
qualification test's phrase is "an identity that can later be **corrected**", and
correction presupposes something that can be wrong about the world.

The distinction to carry forward: **a harness that persists is not a memory that
believes.** Both outlive the session; only one of them can be mistaken.

Recorded rather than dropped because this is the cleanest instance of the
boundary the atlas has, and because the refusal is not on grounds of size,
quality or novelty — bvwebchat's state contract is better engineered than several
systems that *do* have reports.

## The count error the sweep found

Adding a report means bumping the corpus denominator, and the sweep turned up an
error that predates this batch:

> "The atlas holds **140 reports across 135 repositories**… Counts of *systems*
> are 133 and counts of *repositories* are 132."

Three vintages in two sentences. The true figure, derivable in one command from
report frontmatter, is **141 reports across 140 repositories** —
`NousResearch/hermes-agent` is the only repository reviewed twice, so the gap is
exactly one:

```sh
rg --no-filename -N '^source_url:' content/systems/*.md | sort | uniq -d
```

The homepage separately claimed "over 139 repositories", which was right, so the
site made two disagreeing claims about the same number.

**Why it drifted is the same shape as
[the superlative audit](2026-08-04-the-superlative-audit-first-pass.md).**
`check_homepage.py` guards the *report* count because it is a file count.
Nothing derives the *repository* count, so every addition bumped the reports
figure and left the repositories figure to a hand edit that stopped happening.
The one-liner above is the check that would close it; it is not written yet, and
the same argument that produced `check_inspected_pins.py` applies here.

Worth separating from the capability numerators, which behaved correctly: Nova
carries `audit_log` and `human_review`, and the build regenerated 24→25 and
28→29 by itself, because those tables are generated from frontmatter. The counts
that go stale are exactly the ones a human types.

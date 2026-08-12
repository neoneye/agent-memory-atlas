# Which marks could be execution-grounded — what a fortnight of reading actually ran

**Status:** proposed. The disclosure already exists in the rubric's known limits;
the tiering below does not.
**Origin:** an outside review (Qwen, 2026-08-12) called the LLM reviewer a
*"bombshell"* and demanded the atlas *"spin up a Docker container, insert a
memory, update it, delete it, and query it"* — transitioning from code-grounded
to execution-grounded. The demand is right in principle, wrong about the cost,
and answerable with evidence this project already generated without noticing.

## Two corrections to the framing

**It is not buried.** The reviewer describes the LLM-reviewer disclosure as *"the
most damaging revelation … buried in the Known limits section"*. It is under a
heading called Known limits, which is where a project puts a limitation it wants
found.

**"A 71% failure rate on re-audits" is not a rate.** The rubric records *five of
seven `audit_log` marks failing a re-audit* — one re-audit, of one capability, on
2026-07-28, disclosed as an anecdote in the methodology hazards note. The rubric
itself asks for an agreement study *"instead of a list of anecdotes"* precisely
because that number is not a measurement. Generalising it to the corpus is the
inference the page declines to make.

What survives both corrections: **static reading cannot verify stateful
behaviour**, and this atlas's marks are claims about stateful behaviour.

## The evidence nobody collected

Between 2026-08-11 and 2026-08-12 this project executed code from five reviewed
repositories, without a container and without installing anything:

| System | What ran | Cost |
| --- | --- | --- |
| [PLUR1BUS](../content/systems/plur1bus.md) | `node --test` on three regression files; 27 passed | no install — the suite needs no framework |
| PLUR1BUS | negative control: restored `lib/neo-arch.js` from the prior pin on a scratch copy; 5 of 7 failed | one `git checkout` |
| [Hillock](../content/systems/hillock.md) | the reservoir recurrence and the gate geometry, reproduced in separate code | pure Python, no import of the target |
| [Memory Compiler](../content/systems/memory-compiler.md) | its own seven `scripts/` validators as shipped; `Validated 36 fixture(s)` | stdlib only |
| [MythologIQ Agent Memory](../content/systems/agent-memory-doctrine.md) | the residue partition, through a driver written for the review over copies of two stdlib-only modules | no install; the package `__init__` pulls in `jsonschema` |

Five of the last nine systems read. None needed Docker. Three needed nothing but
an interpreter already present. The binding constraint was not tooling — it was
the seven-day dependency cooldown in
[`screen-repository`](../.agents/skills/screen-repository/SKILL.md), which
refused installs for [NeuraKeep](../content/systems/neurakeep.md) and Hillock and
would have refused them for most freshly-published repositories.

So "run the code" is not blocked by ambition. It is blocked, correctly, by a
supply-chain rule this project is not going to relax, and enabled far more often
than the current method admits.

## Proposal: three tiers, recorded per mark

Add an `evidence:` value to the existing `capability_evidence:` block, from a
closed vocabulary:

- **`read`** — the mark was established by reading code at the pin. Today's
  default and, for most marks, the honest answer.
- **`reproduced`** — the mechanism's arithmetic or logic was re-derived in
  separate code that does not import the target. Hillock's reservoir and gate,
  MythologIQ's residue partition. Cheap, safe under the cooldown, and it catches
  exactly the failure the reviewer names: a plausible reading of a recurrence
  that does not do what it appears to.
- **`executed`** — the target's own tests or tools were run, with what was run
  and what passed stated in the report's History. PLUR1BUS, Memory Compiler.

**The rule worth adopting with it:** where a mark rests on a claim that can be
falsified by twenty lines of arithmetic — a decay curve, a similarity threshold,
a recurrence, a score that decides admission — reproduce it rather than reading
it. Three of the four most surprising findings of the last fortnight came from
doing exactly that, and none of them would have survived a careful read.

## What this deliberately does not promise

Not a container per system, not a standing CI matrix, and not execution as a
precondition for a mark. Most of the corpus is unbuildable on one laptop under a
cooldown, and a tier that most reports cannot reach would push the project toward
reviewing only what is easy to run — which is a worse bias than the one it fixes.

The point of the tier is that a reader can see **which** marks were run and which
were read, instead of being told once, on the rubric page, that none of them were.

# Enforce where the writer cannot reach — a pattern page the corpus can already fill

**Status:** proposed, with a sweep that needs verifying before the page is written.
**Origin:** an outside review (Qwen, 2026-08-13) asked for the *"Actuator-as-Logger
Pattern"* to be extracted from [arc-code](../content/systems/arc-code.md) into the
[pattern library](../content/patterns/index.md). The request is right and the
name is too narrow: the corpus holds at least five instances and only one of them
is about logging.

## The principle

**An invariant enforced by the party it constrains is a policy. An invariant
enforced somewhere that party cannot reach is a mechanism.**

arc-code is the sharpest case because it has the before and after. `act.py` used
to run inside the agent's sandbox, which put the ARC key on a disk the agent is
root on, and the instruction to log every action was the whole guarantee. One run
disposed of it: *"handed a session that might have died, an agent read
`scorecard.json`, built its own HTTP client with `ARC_API_KEY` and played a RESET
that never reached `logs.txt`."*

The fix was not a stronger instruction. `rig/broker.py` moved the actuator into a
separate process holding the key and every game session; the agent gets a
forwarding client and no key, and ARC answers 401 to a request without one. The
guarantee is then stated as a property of the topology rather than of the agent's
cooperation: *"anything reaching the game is written down by the thing that
forwards it."*

Note what is **not** claimed — the agent may still call the broker directly, and
must be able to, because that is how it plays. The design does not try to control
the agent's behaviour. It removes the capability that made bypassing possible.

## Candidate instances already in the corpus

A first-pass sweep of the 264 reports. Each needs re-reading at its pin before it
appears on a pattern page; this list is where to look, not what to publish.

| System | The reach that was removed | Form |
| --- | --- | --- |
| [arc-code](../content/systems/arc-code.md) | the agent has no API key, so no request reaches the game off-log | capability removal |
| [Octopoda OS](../content/systems/octopoda-os.md) | the wrong write *"is rejected — by the database, under a role that cannot bypass it"* | privilege separation |
| [Aukora Kernel](../content/systems/aukora-kernel.md) | *"the model cannot promote a tier, cannot bypass the gate"* | the decision is not exposed to the model |
| [OmniIntelligence](../content/systems/omniintelligence.md) | a migration names one writer and the SQL guard *"holds even if that stops being true"* | the invariant restated as a predicate |
| [MemoryOps AI](../content/systems/memoryops-ai.md) | *"a policy the application cannot bypass"* | enforcement below the caller |
| [Verel](../content/systems/verel.md) | *"a review path that cannot bypass it"* | the gate is on the only path |

[PRO-LONG](../content/systems/pro-long.md) is the counter-case and belongs on the
page for it. Its log is written by the harness, which is the right side of the
line — and the copy the agent reads is mounted read-write in a workspace the
prompt invites the agent to save notes into, and the harness computes its next
sync offset from the size of that copy. The recorder is out of reach; the
*record* is not. The failure that follows is silent history loss, reproduced in
that report.

## Why it is not one of the existing pages

- **[Governed write gateway](../content/patterns/governed-write-gateway.md)**
  makes one backend operation responsible for the invariants of durable memory
  *regardless of where a write originates*. It assumes writers arrive at the
  gateway. This pattern is what you do when a writer can decide not to.
- **[Append-only memory audit](../content/patterns/append-only-memory-audit.md)**
  is about not overwriting the evidence. This is about the evidence being
  complete in the first place — an append-only log with an off-path effect is
  append-only and wrong.

The relationship worth stating on the page is that this pattern is a
*precondition* for both. A gateway nobody can go around and an audit that records
every mutation are the same claim, and the claim rests on a capability boundary
neither page currently names.

## What the page would need

Beyond the atlas's standard sections, three things this pattern specifically
demands:

1. **The invariant, stated as what cannot happen** — "no effect without a
   record", "no promotion without the gate" — rather than as what the component
   does.
2. **Where the boundary is drawn, and what is deliberately left uncontrolled.**
   arc-code's is the model: the agent may call the broker however it likes. A
   pattern page that reads as "constrain the agent" would teach the wrong thing.
3. **The test that matters, which is adversarial.** Not "does the gate work" but
   "what happens when the constrained party tries to go around it" — the question
   arc-code answered by accident and everyone else on that list answers by
   assertion. This is the same shape as the
   [negative retrieval assertion](../content/patterns/rejected-value-tombstone.md)
   the rubric already counts, applied to a write path.

## Stance

`reporting`, not `advocacy`. Six instances arrived at independently is evidence
the shape recurs; it is not evidence that removing a capability is the right
trade in every design, and the cost — a separate process, a privilege boundary,
an operational surface — is real. The
[pattern index](../content/patterns/index.md) tracks stance per page and the
build checks it, so this needs deciding before the page is written rather than
after.

## Not proposed

The review's other three suggested primitives are already placed or too thin.
*Budget-matched ablation* is documented on the
[benchmarks page](../content/benchmarks.md) with PRO-LONG as its worked example
and belongs there, beside the other benchmarking rules, rather than in a library
about memory mechanisms. *Lexical-over-semantic recall for grid state* is one
system's correct choice for one data shape, and the general form — exact recall
beats approximate recall when the memory is machine-generated and checkable — is
a sentence in two reports, not a pattern with instances. *Reversible optimistic
self-edit* from Prime Agent is the most promising of the three and needs a second
instance before it is a pattern rather than a system's good idea.

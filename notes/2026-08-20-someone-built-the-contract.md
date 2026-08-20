# Someone built the contract

**Status:** finding about cluster G, the atlas's unbuilt program. One system in
the corpus has shipped a portable capability contract with the two properties
this project specified and never implemented.
**Origin:** re-reading `Perseus-Computing-LLC/perseus-vault` at
[`1bf7041e428a7302281c67f5d597a06f33d38cce`](https://github.com/Perseus-Computing-LLC/perseus-vault/commit/1bf7041e428a7302281c67f5d597a06f33d38cce)
on 2026-08-20, nine commits past the previous pin.

---

## What is there

`benchmark/scoped_memory/` — 728 lines of contract, a runner, a fixture, two
test files and a README, versioned `perseus-vault-scoped-memory-contract/v1`
and described as *"a capability boundary, not a second memory API"*. It covers
bounded search/recall, context projection, inspect, authorized store, correction
with explicit successor lineage, and supersession with observable
`active`/`superseded` states.

Two of its properties are the ones
[the harness note](2026-08-12-the-harness-this-page-does-not-ship.md) and
[the conformance note](2026-08-09-the-conformance-run-the-atlas-does-not-run.md)
argued for, and neither is incidental.

**It runs the same contract against two surfaces.** `InProcessSurface` is a
deterministic reference; `McpSurface` is an adapter over the shipped
`VaultClient` and the canonical MCP tools. The harness note's central claim was
that *a harness shipped with only a passing fixture proves nothing about whether
its assertions discriminate* — the answer there was a deliberately leaky store
that fails exactly the steps it was built to fail. This is the other half of the
same idea: a reference surface establishes what a pass looks like, and the real
system is measured against it through its own tool surface.

**An absence is never a pass.** `OUTCOMES` is `allow`, `deny`, `scope_mismatch`,
`stale_conflict`, `abstain`, `unavailable`, and the README states the rule:
*"A missing semantic provider or surface is represented as `unavailable`; it is
never converted to a fabricated zero or pass."*
`test_publication.py::test_failed_surface_is_explicitly_partial_not_zero` pins
it. This is the property
[the build-page review](2026-08-20-the-build-page-judged-as-a-recommendation.md)
found missing from nineteen of the atlas's own twenty acceptance tests, fixed
here at the level of the outcome vocabulary rather than per assertion — which is
the better place for it, because a vocabulary with no "silently nothing" value
cannot express the failure.

Two more worth naming. Scope is bound out of band —
`user_id`, `workspace_hash`, `agent_id`, `session_id` — with the README stating
that *"model-authored arguments cannot supply or override any of those fields"*
and `contract.py:190` returning `_result("deny", "caller_scope_injection")` when
they try; and *"scope and policy filtering happens before a ranker receives
candidate IDs"*, with a `RecordingRanker` so a test can assert what the ranker
was handed rather than what the API returned. Set that beside
[Outworked](../content/systems/outworked.md), read the same day, where the scope
is the model's own tool argument and the session already knows better: the two
are the same question answered at opposite ends.

And the published artifact is hash-only, with a stable repeated signature
(`test_report_is_hash_only_and_repeated_signature_is_stable`) — a result you can
cite without republishing the corpus it ran over.

## What this means for cluster G

The [notes survey](2026-08-20-ninety-four-notes-clustered.md) named nine notes
specifying harnesses, eval suites and conformance runs, one shipped artifact
between them, and a standing question of whether to build the cluster or close
it. This is a third answer, and the honest one: **part of it got built
somewhere else, by a system in the corpus, without this project's involvement.**

That is not a reason to celebrate and not a reason to stop. Three things follow.

**The atlas's twenty acceptance tests are now behind a published example.** The
`positive_control` field added to `.agents/protocol/tests.yaml` on 2026-08-20 is
a per-test patch on a catalogue whose *vocabulary* has no way to say
"unavailable". Perseus's outcome set is the structural version of the same fix.
Worth considering whether the catalogue should carry an outcome vocabulary
rather than a boolean plus a control.

**A contract that runs against a reference and a real surface is the shape the
conformance note kept circling.** That note closed step 2 — running the deletion
sequence against 238 checkouts contradicts the screening tool — and inverted the
burden onto the systems themselves. What it could not specify was what makes a
self-run readable. This is one answer: publish the contract, publish a reference
surface, publish a hash-only report, and let the adapter be the thing a reader
inspects.

**And the atlas still has not run anything.** Perseus built a contract for its
own system. That is not a cross-system benchmark and does not become one by
being good; the deletion sequence remains unrun against any system here, and
this note does not change that. What it changes is the cost of the next step —
there is now a worked example to read before writing one, rather than only the
specification this project wrote for itself.

## For next time

**When a note proposes an artifact, check the corpus before assuming nobody
built it.** Nine notes accumulated over three weeks arguing about a harness, and
the first system to ship the interesting half of one is a system already in the
atlas with a report and a pin. A monthly grep for the vocabulary of the unbuilt
program — contract, conformance, surface, outcome, adapter — across the corpus
costs nothing and would have surfaced this the week it landed.

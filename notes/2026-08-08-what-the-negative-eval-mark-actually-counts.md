# What the `negative_eval` mark actually counts — 27 of 37, and three kinds

**Status:** done. This is the re-score the
[rubric's open work](../content/methodology/atlas-rubric.md) named after an
outside review argued the mark had drifted from its definition.
**Method:** all 37 reports carrying the flag, re-read at their pinned commits
against the rubric's wording, *"committed evaluation cases assert that particular
material must **not** be retrieved"*. Derived from the committed reports rather
than from a fresh code read — the same method as the
[tombstone strong-form audit](2026-08-07-the-strong-form-tombstone-subset.md).
Where a report does not state what earned the mark, this note says so instead of
inferring it.

## The question

The reviewer sampled three marks and argued none of them is a negative
*retrieval* assertion: [Aeris](../content/systems/aeris.md) excluding engine
identifiers from a serialized projection, [Prime
Agent](../content/systems/prime-agent.md) keeping an earlier summary out of the
next summarization, [DeepCode](../content/systems/deepcode.md) keeping a
parent-directory instruction file out of an assembled preamble. The conclusion
drawn was that "the count of 37 is inflated by semantic drift".

Three out of 37 is a sample, not a measurement, and the magnitude claim was not
earned. The direction was. Here is the measurement.

## The answer

**27 of 37 assert that particular material is not returned by a read path.** The
definition holds for those, and it holds in two distinguishable ways. The other
**10 assert something else** — real, committed, useful tests, keeping material
out of something that is not a retrieval result.

| Kind | Count | What the assertion is about |
| --- | ---: | --- |
| **Content** | 20 | A specific value, fact or row must not come back from a query |
| **Boundary** | 7 | One scope or tenant must not reach another's material through recall |
| **Not retrieval** | 10 | Material kept out of a projection, a preamble, a summary, a file, or a write |

### Content (20)

[agent-afk](../content/systems/agent-afk.md) · [Agno](../content/systems/agno.md)
· [brain-md](../content/systems/brain-md.md) ·
[Core Memory](../content/systems/core-memory.md) ·
[Daimon](../content/systems/daimon.md) ·
[Engram Alpha](../content/systems/engram-alpha.md) ·
[Graphify](../content/systems/graphify.md) · [Helm](../content/systems/helm.md) ·
[KiroCrew](../content/systems/kirocrew.md) ·
[Lethe](../content/systems/lethe.md) · [memsem](../content/systems/memsem.md) ·
[Mimir](../content/systems/mimir.md) ·
[mnemopi](../content/systems/mnemopi.md) ·
[Mnemosyne](../content/systems/mnemosyne.md) ·
[Project N.E.K.O.](../content/systems/neko.md) · [Omi](../content/systems/omi.md)
· [open-cowork](../content/systems/open-cowork.md) ·
[Perseus Vault](../content/systems/perseus-vault.md) ·
[Universal Memory Engine](../content/systems/universal-memory-engine.md) ·
[Verel](../content/systems/verel.md)

The strongest are unambiguous and there is no argument to have about them.
Verel's `tests/test_memory_negative_eval.py` asserts a rejected fact is
*"invisible to EVERY recall path, un-resurrectable by re-assertion,
un-launderable"*. Lethe's ForgetEval runs 385 adversarial cases whose entire
premise is that released, superseded and purged content is not returned.
Universal Memory Engine's `eval/fixtures/retrieval_golden.json` carries
`forbid_nodes` beside `expect_nodes` on all 32 queries. Omi asserts the memory a
user reviewed away is absent from the result *while the other three are present*
— the positive control that separates a real negative case from a broken query.

### Boundary (7)

[Aukora Kernel](../content/systems/aukora-kernel.md) ·
[CrewAI](../content/systems/crewai.md) ·
[EverOS](../content/systems/everos.md) · [MIRIX](../content/systems/mirix.md) ·
[MuninnDB](../content/systems/muninndb.md) ·
[NOOA Memory](../content/systems/nooa-memory.md) ·
[Provem](../content/systems/provem.md)

These satisfy the definition — material must not be retrieved — but the material
is *everything on the other side of a boundary* rather than a particular value.
The atlas has always separated these in the
[benchmarks page](../content/benchmarks.md) and the separation matters: a system
can assert perfect tenant isolation and have no way to test that a *corrected*
value stopped coming back. All seven arrived from access-control discipline
rather than from memory research, which is why they cluster.

### Not retrieval (10)

| System | What the committed case actually asserts |
| --- | --- |
| [Aeris](../content/systems/aeris.md) | Engine identifiers absent from a **serialized projection** handed to a model |
| [DeepCode](../content/systems/deepcode.md) | A parent-directory instruction file absent from an **assembled preamble** |
| [Prime Agent](../content/systems/prime-agent.md) | An earlier summary not fed into the **next summarization** |
| [Helix AGI](../content/systems/helix-agi.md) | A removed note's id absent **from the file on disk** — deletion durability |
| [memoryops-ai](../content/systems/memoryops-ai.md) | An eval harness asserting a **write decision** of `drop` or `block` — material never saved |
| [Cognis](../content/systems/cognis.md) | A caller-supplied header cannot override the JWT subject — **identity binding** |
| [CSM](../content/systems/csm.md) | A reviewer bound to one session cannot **act on** another session's candidate |
| [iai-pme](../content/systems/iai-pme.md) | Architectural absences — no spawn path, no window compaction — beside forgetting and redaction cases |
| [Argo](../content/systems/argo.md) | Retrieval **refuses to answer** when its index is unqualified; nothing comes back, but no particular material is named |
| [Pydantic AI Harness](../content/systems/pydantic-ai-harness.md) | Nothing. The report says the mark is earned and names no case |

The reviewer's three examples are all in this table, so the objection was
correct about them. It was correct about roughly a quarter of the corpus, not
about the count as a whole.

## The one that should not be there

**Pydantic AI Harness is the finding.** Every other report in this note names a
file, a test, or an assertion; that one asserts the mark and cites nothing. This
is the failure mode the
[methodology hazards note](2026-07-28-methodology-hazards.md) already records —
a mark surviving because nobody re-read the sentence under it — and it survived
this long for exactly the reason the review identified: `capabilities:` is a
list of flags, so a mark with no evidence looks identical to a mark with a test
behind it. It should be re-read at its pin and dropped if nothing turns up.

## What changes, and what does not

**The flags do not change.** Dropping ten marks would delete the information
that ten systems ship committed must-not tests, which is worth knowing and rare.
Renaming the mark would quietly move the goalposts under a published count.

**The prose changes.** Wherever the atlas quotes 37, it now says what the 37 are:
committed cases asserting material must not appear somewhere, of which 27 are
about a read path. The rubric carries the split. A reader who wants the strict
reading of "negative retrieval assertion" should use **27**.

**The evidence block carries the kind.** `capability_evidence:`'s `subsystem`
field already does this work for the four migrated reports — Aeris's record
reads *"model-facing projection, not the memory store"*, Prime Agent's reads
*"conversation compaction, not memory retrieval"*. As the remaining reports
migrate, the split stops being a note and becomes a query.

## Follow-up

- Re-read Pydantic AI Harness at its pin; drop the mark if no case exists.
- Migrate the ten "not retrieval" reports' evidence blocks first, since their
  `subsystem` field is what stops the next reader repeating this audit.
- The [benchmarks page](../content/benchmarks.md)'s negative-precision row names
  five content holders and three boundary holders. It is a subset of this note's
  20 and 7 and should be regenerated from the split rather than hand-listed.

# Hermes and Holographic: one repository, two report scopes

**Status:** pins aligned; report structure remains an editorial decision.
**Recommendation:** keep two reports for now, with explicit scopes and a shared
re-read workflow. A merge is reasonable if the atlas chooses the configured
product as its unit of comparison, but sharing a repository does not settle that
choice.
**Origin:** `scripts/drift_report.py`'s first full run put `hermes-agent` and
`holographic` in the same register and made a defect visible that neither report
could show on its own.

## What would a merge mean?

There are three separate decisions: how many pages a reader opens, how many
memory implementations the comparison tables distinguish, and how many upstream
checkouts a maintainer reviews. They need not have the same answer.

The current reports describe different scopes at the same commit:

| Question | [Hermes Agent](../content/systems/hermes-agent.md) | [Holographic](../content/systems/holographic.md) |
| --- | --- | --- |
| What is being assessed? | Built-in curated memory, session history, skills, and the host's provider contract | The optional first-party provider in `plugins/memory/holographic/` |
| What holds durable facts? | Delimited entries in `MEMORY.md` / `USER.md` | SQLite fact rows, linked entities, and derived HRR vectors and category banks |
| How does content reach the prompt? | Curated memory is bounded and frozen at session start; session history is searched separately | Provider prefetch and tool queries retrieve ranked facts |
| What changes memory? | The built-in `memory` tool, with a configurable approval gate and budget enforcement | `fact_store`, mirrored host additions, and optional session-end extraction |
| What evidence earns the current marks? | `human_review` for the built-in write gate; `negative_eval` for exclusions from the frozen prompt snapshot | Neither mark is awarded in this report; the host's evidence does not establish coverage of the plugin's own paths |

These are distinctions in stored data, read paths, and mutation policy, not just
two descriptions of the same backend. The table summarizes the existing pinned
reports; it is not a fresh upstream code review.

But they are also **coupled parts of one product**. Holographic implements
Hermes's provider contract, receives host lifecycle events, and can mirror
built-in additions. The reports describe a concrete seam: removing the Markdown
entry does not remove the mirrored SQLite fact. Saying they merely "happen to
live in one tree" understates the integration that makes them worth reading
together.

## The strongest case for merging

A person evaluating Hermes needs to know what happens with Holographic enabled.
One report could explain the built-in layer, the optional provider, and their
interaction in one place. It would give shared lifecycle and interface claims
one editorial home, and one report pin would avoid this particular split in
revisions.

Different mechanisms alone do not justify separate reports. The Hermes report
already contains curated files, session search, skills, and a provider
interface. Treating every distinct mechanism as a new system would fragment the
atlas and make its totals depend on how finely an author subdivides a product.
The boundary needs to be defensible beyond this one plugin.

Nor would merging have to erase Holographic's analysis. A substantial section
could retain its schema, diagram, caveats, and pattern links. Existing inbound
links are a migration cost, not a reason to preserve a report indefinitely. The
plugin's unusual vector algebra is a reason to cover it, not by itself a reason
to give it a separate row.

## Why I would keep the reports separate for now

The strongest reason is **the scope of a capability claim**. Hermes's approval
gate governs built-in memory writes; it does not establish that the plugin's
direct tool and extraction paths require approval. The host's negative tests
cover its frozen prompt snapshot; they do not establish that a downvoted fact
is excluded correctly from Holographic retrieval.

Under the current [generator](../scripts/generate_matrix.py), each report
supplies one matrix row and one set of capability flags. A merged row could
award the union of the marks and explain their limits in prose, but the row
alone would conceal which component has the mechanism. Taking the intersection
would instead hide mechanisms that were found. This scope problem already
exists in broad host reports; merging would need to address it, not silently
choose one interpretation.

Holographic has its own store, tools, retrieval rules, and update/delete
behaviour, and it is optional within the host. That makes it a useful unit of
comparison with other memory providers even though it is not a separate product
or repository. My proposed boundary is to keep a separate report when a
selectable memory implementation has a distinct persistence and retrieval
lifecycle that would otherwise be obscured in the host's row. A helper module,
index, or additional storage format is not enough. This is a proposed editorial
rule, not a claim that the whole corpus has already been classified by it.

| Choice | Benefit | Cost or condition |
| --- | --- | --- |
| One report, one comparison row | One account of the configured product and its interactions | Requires an explicit rule for marks that apply to only one component |
| Two reports, coordinated re-reads | Preserves distinct comparison rows and existing URLs; reviews the shared seam together | Requires clear scope labels and deliberate coordination |
| One page, two component rows | Brings the account together while preserving comparison detail | Requires generator and navigation changes; page count stops being report count |

I favour the second choice with the current format. The third is worth
considering if this becomes a recurring corpus shape. The first becomes more
compelling if readers primarily need product configurations, if the plugin loses
its separate lifecycle, or if repeated editorial duplication outweighs the
value of its comparison row. Those are reasons to revisit the decision; a
shared Git URL is not sufficient on its own.

## What went wrong with the pins

The two reports had drifted **7,068 commits apart**: `hermes-agent` was pinned at
`1bbb6e5b` (25 August 2026) and `holographic` at `0fa5e41c` (27 July 2026), the
commit `hermes-agent` had been read at two pins earlier.

Different pins do not make either report false: each describes its own inspected
commit. They do mean the pair cannot automatically be read as one account of a
host and plugin deployed together. The pins were visible individually, but the
consequence for cross-report claims was not explained.

The existing [inspected-pin checker](../scripts/check_inspected_pins.py)
explicitly permits multiple overview entries for one repository and lets each
report match any of them. Its comment names Hermes and Holographic as reports
that can be re-read independently. The gap was therefore partly a policy choice,
not simply that nobody had written a cross-report check. Requiring matching
pins would tighten that policy.

Both are now pinned at `9e6c4100cbf5222fb473ecc2b51fd17874f6ee75`, and the
repositories-inspected list in `content/overview.md` carries one entry rather
than two.

## Coordinate the reading without conflating the reports

For this coupled pair, I would use one upstream checkout and one target commit
per re-read, with separate evidence review for each report and a shared check of
the host/plugin seam. In particular, follow an addition, a replacement, and a
removal across the two stores, and inspect the contract and its implementation
together. A shared pin identifies the tree; it does not prove that these paths
compose correctly.

A local check can group reports by normalized `source_url` and flag differing
revisions. I would make divergence an error for this explicitly coupled pair,
with a diagnostic naming both reports and pins. A blanket rule for every shared
repository is too broad: historical comparisons or independently assessed
packages may intentionally use different revisions. Exceptions should state
why the pins differ and what cross-report comparison remains valid.

The check must not be satisfied by merely copying a SHA into the second report.
If its subsystem is unchanged, a diff can reduce the re-read, but the shared
wiring, evidence anchors, and absence claims still need checking, as described
in [the note on subsystem drift](2026-09-01-the-memory-subsystem-is-the-stillest-part.md).
When that work is incomplete, retain the honest old pin and identify the pair as
not yet jointly reviewed.

This workflow and stricter check are proposals; this edit implements neither.
The count also needs the right noun: two reports here are two assessed memory
implementations, not two independent repositories or independent observations
about the field. Use the generated [capability index](../content/capabilities.md)
for corpus totals rather than maintaining another total in this note.

## Verification record from the pin alignment

The remaining sections preserve the earlier reading's audit trail. They are
useful regardless of the report-layout decision. I have checked the local report
frontmatter, scope statements, generator, and pin checker for this editorial
revision; I have not fetched or re-read the upstream tree or re-run these probes.

Get the tree the reports describe. A blobless or shallow fetch of the exact
commit is enough; a full clone of this repository is ~900 MB.

```sh
mkdir hermes-agent && cd hermes-agent
git init -q
git remote add origin https://github.com/NousResearch/hermes-agent.git
git fetch --depth 1 origin 9e6c4100cbf5222fb473ecc2b51fd17874f6ee75
git checkout -q FETCH_HEAD
```

**Screen before reading.** This is a live tree with an auto-run surface
(`.envrc`), twenty-one build-time execution surfaces including `postinstall`
hooks and `setup.py`, and twenty manifests changed within seven days. Nothing
below installs anything or runs a suite, and nothing should.

### The one wrong claim

The Holographic report credited `rebuild_all_vectors()` twice — as a
"deterministic recovery path" in section 9 and as a Steal bullet — for
recomputing every vector and bank from stored text. No such function exists at
this commit.

```sh
rg -n 'rebuild_all_vectors' .        # expect: no output
rg -n 'def _rebuild_bank' plugins/memory/holographic/store.py   # expect: line 247
```

The property that survives is narrower, and the report now says so: content is
canonical, `update_fact` recomputes a fact's vector when content changes, and
`_rebuild_bank` rebuilds one category from the vectors its facts already carry.
The earlier reading reported no bulk backfill path for facts without vectors.
`plugins/memory/holographic/retrieval.py:57-58` carries a comment about "stores
whose `hrr_vector` was never backfilled". That comment supports the existence of
vectorless stores; it does not by itself prove the absence of a backfill path.

**What a verifier cannot settle from this tree alone:** whether
`rebuild_all_vectors()` existed at `0fa5e41c` and was removed, or was never
there and the first reading was wrong about it. Both are consistent with the
correction as written. Deciding it needs `git fetch --depth 1 origin 0fa5e41c…`
and a second grep. The answer changes the attribution of the correction in
History, not the current mechanism description.

### The claim that contradicted itself

Section 1 said a downvoted fact "becomes permanently invisible". Section 4 of the
same report already said the row survives and `list` returns it. Section 4 was
right, and sections 1 and 9 now agree with it.

| Where | Expect |
| --- | --- |
| `plugins/memory/holographic/store.py:73` | `_HELPFUL_DELTA, _UNHELPFUL_DELTA = 0.05, -0.10` |
| `plugins/memory/holographic/store.py:191` | `list_facts(…, min_trust: float = 0.0, …)` |
| `plugins/memory/holographic/retrieval.py:52` | `search(…, min_trust: float = 0.3, …)` |
| `plugins/memory/holographic/__init__.py:105` | `min_trust_threshold` defaulting to `0.3` |
| `plugins/memory/holographic/__init__.py:48` | tool schema `min_trust` documented as default 0.3 |

At the documented defaults, three unhelpful ratings take a fact from 0.5 to
approximately 0.2, below the 0.3 search threshold but above `list_facts`' 0.0
threshold. This describes default suppression, not permanent invisibility or
erasure. A runtime boundary test should check the actual stored float and
comparison after each rating; decimal arithmetic alone is not a test of either
retrieval path.

### Claims that were re-anchored, not corrected

The plugin was compacted from roughly 2,000 lines to 912, and the Hermes memory
layer was split into more files. Every size and path in both reports was
re-derived; the mechanisms are unchanged.

```sh
wc -l plugins/memory/holographic/{holographic,store,retrieval,__init__}.py
#   125  308  215  264   → 912

wc -l tools/memory_tool.py tools/memory_tool_store.py \
      agent/memory_manager.py agent/memory_provider.py hermes_state.py
#   397  417  826  165  1386

ls hermes_state_*.py | wc -l         # 21
```

Spot-checks that the mechanism did not move with the files:

| Claim | Where | Expect |
| --- | --- | --- |
| trust multiplies relevance as well as supplying a retrieval floor | `retrieval.py:69` | `fact["score"] = relevance * fact["trust_score"]` |
| fusion weights | `retrieval.py:40` | `0.4 / 0.3 / 0.3` |
| weights without NumPy | `retrieval.py:42-43` | `0.6 / 0.4 / 0.0` |
| `contradict` comparison cap | `retrieval.py:127` | `if len(rows) > 500:` |
| budget refusal cap | `tools/memory_tool_store.py:75` | `_MAX_CONSOLIDATION_FAILURES_PER_TURN = 3` |
| load-time scan is idempotent | `tools/memory_tool_store.py:120` | `… if entry and not entry.startswith("[BLOCKED:")` |
| checkpoint API the host wants | `agent/memory_provider.py:20` | `PRE_COMPRESS_CHECKPOINT_API_VERSION = 2` |
| what the base class declares | `agent/memory_provider.py:63` | `pre_compress_checkpoint_api_version = 1` |
| the `negative_eval` suite | `tests/tools/test_memory_tool.py:609` | `class TestLoadTimeSnapshotSanitization:` |

### The absence claims

These probes were recorded in the reports' appendices for the next re-read.
Expected results below come from the earlier reading. A scoped grep checks the
named implementation or suite; it cannot establish a repository-wide absence.
Before retaining a broader claim, widen the search to the whole tree and inspect
alternative names and call paths. All probes below should return nothing unless
noted.

```sh
rg -n 'checkpoint_api_version|supports_checkpoint' plugins/memory/
#   0 — the earlier reading found no shipped adapter opting into v2; inspect
#   inherited behaviour and host dispatch before extending that conclusion.

rg -n 'tombstone|deleted_at|is_deleted|suppress' plugins/memory/holographic/
rg -n 'user_id|project_id|session_id|scope' plugins/memory/holographic/store.py
rg -n 'audit' plugins/memory/holographic/ tools/memory_tool_store.py tools/memory_tool.py

rg -n 'record_feedback|min_trust|unhelpful' tests/plugins/memory/test_holographic_*.py
#   0 — no literal matches for these names in the named test files

rg -n 'record_feedback|min_trust|unhelpful|trust_score' tests/plugins/memory/test_holographic_*.py
#   1 hit, at test_holographic_retrieval.py:192 — and it is a re-implementation
#   of the scoring formula inside a determinism test, not a test of the trust
#   model. The broader grep finds adjacent coverage, but does not prove the
#   narrower search is exhaustive. Inspect callers and indirectly parameterized
#   tests before concluding that no case exercises the trust floor.

rg -n 'contradict' tests/plugins/memory/
#   0 — no literal match in the plugin tests. Widening to
#   `rg -n 'contradict' tests/` returns hits in unrelated suites. That is
#   a vocabulary check, not proof that equivalent behaviour is untested.
```

## Limits of this note

The reading behind it used a shallow clone at HEAD plus a fetch of the pinned
commit, so commit *counts* here (7,068 apart; 14,909 and 7,841 behind at the time
of the register run) come from the GitHub compare API and not from a local
history walk. Each is reproducible as
`GET /repos/NousResearch/hermes-agent/compare/<base>...<head>` and reading
`ahead_by`. The line anchors, file sizes and grep results above all come from
the tree at `9e6c4100` and are the part worth re-running.

The upstream reading recorded no test-suite execution. This editorial revision
does not add an upstream test run or settle the historical `rebuild_all_vectors`
question.

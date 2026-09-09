# Two reports, one repository, two pins — and what an independent reader should be able to check

**Status:** finding, applied. Written to be verified by someone who has not read
the session that produced it.
**Origin:** `scripts/drift_report.py`'s first full run put `hermes-agent` and
`holographic` in the same register and made a defect visible that neither report
could show on its own.

## The finding

`NousResearch/hermes-agent` is the only repository in the corpus carrying two
reports. That is deliberate and documented — the agent's built-in Markdown
memory and the first-party HRR plugin shipped in `plugins/memory/holographic/`
are different systems that happen to live in one tree. What was not deliberate
is that they had drifted **7,068 commits apart**: `hermes-agent` was pinned at
`1bbb6e5b` (25 August 2026) and `holographic` at `0fa5e41c` (27 July 2026), the
commit `hermes-agent` had been read at two pins earlier.

So the atlas simultaneously described one repository in two states, and a reader
comparing the two reports was comparing across a gap nothing on either page
named. Every per-report check passed the whole time: each report was internally
consistent, each pin was reachable, each History section was well-formed. The
invariant that failed — *two reports on one repository should describe one
state* — had no owner, because no existing check looks at two reports at once.

Both are now pinned at `9e6c4100cbf5222fb473ecc2b51fd17874f6ee75`, and the
repositories-inspected list in `content/overview.md` carries one entry rather
than two.

## Why this is the interesting failure

The register was built to find stale pins. It found something a staleness number
cannot express: not that a pin was old, but that two pins **disagreed with each
other**. Drift is a fact about a report and its upstream; this is a fact about
two reports and each other, and it only became visible when both rows sat in one
file keyed on `repo`.

That suggests a cheap check with no network in it: group reports by `source_url`
and fail when a group holds more than one distinct `revision`. It would have
caught this on the day the second re-read landed instead of six weeks later. It
is not built, and it is worth building.

## What was corrected, and what an independent verifier can settle

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
Nothing recomputes vectors for facts that have none — `plugins/memory/holographic/retrieval.py:57-58`
carries a comment about "stores whose `hrr_vector` was never backfilled", which
is the acknowledgement that no backfill ships.

**What a verifier cannot settle from this tree alone:** whether
`rebuild_all_vectors()` existed at `0fa5e41c` and was removed, or was never
there and the first reading was wrong about it. Both are consistent with the
correction as written. Deciding it needs `git fetch --depth 1 origin 0fa5e41c…`
and a second grep, and the answer changes only the History wording, not the
report body.

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

Three unhelpful ratings take a fact from 0.5 to 0.2, under every floor except
`list_facts`'. The arithmetic is the whole claim: `0.5 − 0.10 − 0.10 − 0.10`,
against `trust_score >= min_trust`, so two ratings leave it exactly at the floor
and retrievable, and the third does not.

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
| trust multiplies relevance, never gates it | `retrieval.py:69` | `fact["score"] = relevance * fact["trust_score"]` |
| fusion weights | `retrieval.py:40` | `0.4 / 0.3 / 0.3` |
| weights without NumPy | `retrieval.py:42-43` | `0.6 / 0.4 / 0.0` |
| `contradict` comparison cap | `retrieval.py:127` | `if len(rows) > 500:` |
| budget refusal cap | `tools/memory_tool_store.py:75` | `_MAX_CONSOLIDATION_FAILURES_PER_TURN = 3` |
| load-time scan is idempotent | `tools/memory_tool_store.py:120` | `… if entry and not entry.startswith("[BLOCKED:")` |
| checkpoint API the host wants | `agent/memory_provider.py:20` | `PRE_COMPRESS_CHECKPOINT_API_VERSION = 2` |
| what the base class declares | `agent/memory_provider.py:63` | `pre_compress_checkpoint_api_version = 1` |
| the `negative_eval` suite | `tests/tools/test_memory_tool.py:609` | `class TestLoadTimeSnapshotSanitization:` |

### The absence claims

Each of these is a criticism in one of the two reports, and each is now recorded
in that report's appendix so it can be re-run at the next pin. All should return
nothing unless noted.

```sh
rg -n 'checkpoint_api_version|supports_checkpoint' plugins/memory/
#   0 — no shipped adapter opts into v2, so every mountable provider is on
#   best-effort semantics and a failed pre-compress checkpoint is a debug line

rg -n 'tombstone|deleted_at|is_deleted|suppress' plugins/memory/holographic/
rg -n 'user_id|project_id|session_id|scope' plugins/memory/holographic/store.py
rg -n 'audit' plugins/memory/holographic/ tools/memory_tool_store.py tools/memory_tool.py

rg -n 'record_feedback|min_trust|unhelpful' tests/plugins/memory/test_holographic_*.py
#   0 — nothing calls the feedback API or sets a floor

rg -n 'record_feedback|min_trust|unhelpful|trust_score' tests/plugins/memory/test_holographic_*.py
#   1 hit, at test_holographic_retrieval.py:192 — and it is a re-implementation
#   of the scoring formula inside a determinism test, not a test of the trust
#   model. Both greps are here because the second is what makes the first
#   trustworthy: a pattern that returns nothing has to be shown to be capable of
#   returning something. No case exercises the trust floor in either direction,
#   which is the finding — the hazard the report is built around is untested.

rg -n 'contradict' tests/plugins/memory/
#   0 — the plugin's headline action has no committed case either. Widening to
#   `rg -n 'contradict' tests/` returns hits in unrelated suites, which is the
#   same capability control: the term is findable, just not here.
```

## The judgement call, recorded because it was nearly made the other way

The first response to "two reports, one repository" was to merge them, and that
was begun before being reversed. The case against merging, which is the reason
they stayed separate:

- The atlas's comparative apparatus is per report — one `matrix`, one capability
  row, one verdict, one diagram. Holographic is the corpus's only vector-symbolic
  architecture, cited as a comparator by twelve other system reports and nine
  pattern pages; folding it into a Hermes section removes that row from the
  comparison tables and turns every one of those cross-references into an anchor.
- The two are genuinely different systems. They share a repository, not a design.

The case for merging, which is real and was not baseless: 392 of 393 reports are
one-per-repository, and a re-read of this repository has to update two pages or
create exactly the drift described above. The check proposed in "Why this is the
interesting failure" is the cheaper answer to that than a merge.

## Limits of this note

The reading behind it used a shallow clone at HEAD plus a fetch of the pinned
commit, so commit *counts* here (7,068 apart; 14,909 and 7,841 behind at the time
of the register run) come from the GitHub compare API and not from a local
history walk. Each is reproducible as
`GET /repos/NousResearch/hermes-agent/compare/<base>...<head>` and reading
`ahead_by`. The line anchors, file sizes and grep results above all come from
the tree at `9e6c4100` and are the part worth re-running.

No test suite was executed, on this tree or any other.

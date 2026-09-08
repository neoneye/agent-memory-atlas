# Benchmark hygiene and a register that separates evidence from inference

**Written 2026-09-09.** Prompted by reading
[harbor-framework/terminal-bench][pin] at
`83c7a6172d629c6575b785ab12c8db787bb2e323`. It measures terminal tasks within a
session, so the atlas discusses it on the benchmarks page rather than giving it
a memory-system report. Two practices are worth recording systematically:
contamination markers and versioned task maintenance. Neither, by itself, proves
that a benchmark is uncontaminated or remains discriminating.

## 1. A canary is a marker, not proof of training exposure

All sixty-six live `task.toml` files carry **the same GUID**, not a distinct
identifier for each task. The [canary check][canary] requires that literal marker
in task instructions, task metadata, environment Dockerfiles, and supported text
files under solutions and tests. It checks presence and comment placement; it
does not test a model for memorisation. The [review documentation][review] states
the check's intended anti-contamination role.

This gives corpus builders a string to search for when excluding benchmark
material. Finding it in a candidate training corpus establishes that marked text
is present there; it does not establish that a model was trained on it. Finding
it in model output is also insufficient on its own: the string might have come
from the evaluation prompt, retrieved files, tools, or another public document
using the same marker. Its shared use prevents attribution to one task.

The benchmarks page's [probe advice][probe-advice] asks for fictional,
high-entropy facts **and a no-memory baseline**. That baseline is an empirical
control, not merely prevention. A contamination marker complements it by making
source material recognisable; it does not replace the comparison or explain why
a baseline answered correctly.

**For a memory benchmark, keep two uses separate.** A marker in conversation
records the system is asked to ingest can help audit copying or retrieval. Its
appearance afterwards is compatible with successful memory. Testing for prior
exposure needs a separate condition that withholds those records and the target
marker, disables retrieval and external tools, and clears prior session state.
Record the elicitation prompt, model and decoding settings, and compare against
unexposed control markers. Even then, a hit supports prior exposure rather than
identifying its training source, and a miss does not establish a clean model.
That is a proposed experiment, not something Terminal-Bench's static check runs.

**The limits matter.** A marker can be stripped while the questions survive;
it cannot measure how much contamination helped a score. A later release can
add markers, but they say nothing retroactively about previously distributed
unmarked copies. Adding markers early helps preserve coverage; publishing once
without them does not make all future marking useless.

## 2. An archive establishes retention of old tasks, not why they left

At the pin, Terminal-Bench has sixty-six live task directories and ninety
directories in [the archive][archive]. Its [README][readme] describes a continuous
benchmark with tagged releases published on Harbor Hub. Those are checkable
observations about its structure and stated release process.

The archive count is not a count of tasks retired for being too easy. The
history includes an [import of Terminal-Bench 2.1 archive tasks][archive-import],
as well as individual moves such as [archiving gpt2-codegolf][archive-move]. An
archive can contain earlier editions, broken tasks, or tasks removed for other
reasons. These entries do not establish a saturation threshold or a policy for
retiring tasks when models solve them reliably.

The benchmarks page's [saturation argument][saturation] gives a reason to
consider refreshing a task set. Versioned replacement is one possible response;
so are harder extensions and keeping a fixed set for longitudinal comparisons.
A dataset released with a paper can acquire later versions. Whether any given
memory benchmark does so needs its own source check, not an inference from its
publication format.

**Comparability needs more than a version label.** Report the immutable dataset
revision or digest, task set, grader and harness version, alongside the model
configuration. A moving `latest` reference is insufficient. Different releases
produce scores on different tasks; versioning makes that difference visible but
does not make the scores comparable. To measure progress, rerun configurations
on the same release or report a shared-task comparison separately. Record why
tasks were added or removed so a harder successor does not silently change the
capability being measured.

## 3. What the page can and cannot establish

The page discusses contamination controls, including withheld material and
no-memory baselines, and records Terminal-Bench's marker and archive. It does
not tabulate those properties consistently across benchmarks. That is a gap in
the atlas's records, not evidence that every other benchmark lacks them.

A file search can establish marker presence. Establishing a detection procedure
requires reading the harness; establishing a retirement policy requires release
records and reasons. A directory count answers neither. The register should
preserve those distinctions instead of compressing them into yes/no columns
labelled *contamination guard* and *maintained*.

## 4. Separate the register from the argument

### The navigation problem

At atlas commit `aae48f51f962cd80e543f0a07d44ac83046ee3ae`,
`content/benchmarks.md` has 3,342 lines and nine numbered sections. Section 2
contains five third-level headings, including its boundary discussion. Section 6
contains twenty-two third-level headings, but those are **not twenty-two
benchmarks**: they also include the proposed procedure, substrate discussion,
harness and gaps in measurement.

Many benchmark discussions have argumentative headings that omit their names.
The names remain searchable in the body, but the table of contents is a poor
name index. Identity and evidence are spread between sections 2 and 6, making
comparison harder than it needs to be.

### The proposal

Put a compact register in section 2, with stable name anchors and links to the
existing analyses. Keep the essays and their titles. A row should identify a
**benchmark and evaluated release**; different releases must not silently
overwrite one another. The visible index can stay narrow, with linked evidence
notes carrying the details below rather than forcing every field into one wide
table.

| Field | Evidence and boundary |
| --- | --- |
| Name, artifact, licence | Link the released artifact and its licence; distinguish code from dataset terms. |
| Evidence basis | Paper, artifact read at a full pin or digest, or locally reproduced result; link the source. |
| Unit, size and split | State what an item is and which release the count describes. |
| Measures | Recall, deletion, forgetting or capability; link the scoring definition. |
| Contamination marker | Location and granularity: shared marker, per-item marker, or not assessed. |
| Exposure check or control | Corpus filtering, model probing, withheld data or no-memory baseline; distinguish a proposal from an implemented check. |
| Release and retirement evidence | Version identifier, archive or release history, and documented removal reasons; do not infer ongoing maintenance from an archive. |
| Uncertainty and cost reporting | Name the evaluated run, interval method and cost boundary; these belong to a result, not every use of a dataset. |
| Reproduction status | Separate available artifacts, inspected scoring code, recomputed published aggregates and a locally executed benchmark. |

**Unknown is not absent.** Use *not assessed* when this reading did not check a
field; *not found at the pin* only after recording search scope; and
*not applicable* with a reason. A source that reports a result supports
*reported*, not *reproduced*. Each factual cell needs a pinned path, paper
section or result artifact. A validator can check missing sources and broken
references; it cannot establish the truth of a judgement.

### A bounded first step

Start with Terminal-Bench, LoCoMo and LongMemEval, which the page already
discusses. Reuse those readings for identity and scoring, and leave hygiene
fields *not assessed* until their artifacts have been checked for that question.
Do not fill an absence from silence in an existing report. The Terminal-Bench
row's hygiene evidence can already be stated:

| Property | Finding at the Terminal-Bench pin |
| --- | --- |
| Marker | One shared GUID in all 66 live task metadata files; the static check also covers other task text. [Source][canary] |
| Model exposure detection | Not established by the static marker check; the external Harbor harness was not inspected for this. |
| Releases | Tagged releases on Harbor Hub, as described by the pinned README. [Source][readme] |
| Archive | 90 directories; history includes a prior-edition import and individual task moves. [Import][archive-import], [example move][archive-move]. |
| Saturation-driven retirement | Not established by the directory count or the cited archive history. |

Before expanding the pilot, check that a reader can find all three names, follow
each row to its analysis and evidence, and distinguish an unknown from a
negative finding. Preserve existing essay anchors and run the site checks after
moving content. No new model runs are required to build this index; claims of
successful contamination detection or reproduced scores would require their own
experiments. This note proposes the register; it does not implement it.

## Provenance and correction

I checked Terminal-Bench at `83c7a6172d629c6575b785ab12c8db787bb2e323` after
running `scripts/screen_repo.py`: zero auto-run surfaces, thirteen build-time
execution surfaces and eight unpinned dependency surfaces. I installed no
dependencies and ran no upstream code or benchmark. My read-only count found
66 live `task.toml` files, all marked, one distinct GUID and 90 archive
directories. I read the marker check, its documentation, the README and archive
history. The harness is external and was not part of this check.

The initial note treated canary output as proof of training exposure, described
the archive as retirement without checking its origins, and inferred missing
mechanisms from missing descriptions. Those claims are replaced above. The
same marker and retirement overclaims on the benchmarks page are corrected
alongside this note. I also checked the page's headings: its probe advice
includes a no-memory baseline, and section 6's twenty-two headings are not a
count of benchmarks.

[pin]: https://github.com/harbor-framework/terminal-bench/tree/83c7a6172d629c6575b785ab12c8db787bb2e323
[canary]: https://github.com/harbor-framework/terminal-bench/blob/83c7a6172d629c6575b785ab12c8db787bb2e323/scripts/checks/check-canary.sh
[review]: https://github.com/harbor-framework/terminal-bench/blob/83c7a6172d629c6575b785ab12c8db787bb2e323/docs/TASK_REVIEW_AUTOMATION.md#check-canary
[archive]: https://github.com/harbor-framework/terminal-bench/tree/83c7a6172d629c6575b785ab12c8db787bb2e323/archive
[readme]: https://github.com/harbor-framework/terminal-bench/blob/83c7a6172d629c6575b785ab12c8db787bb2e323/README.md
[archive-import]: https://github.com/harbor-framework/terminal-bench/commit/f38349fc9c32aeaf77e30b5bd0464f3a2af8b791
[archive-move]: https://github.com/harbor-framework/terminal-bench/commit/5ad8c0bcf2c2741cf8fc45df52685b95c4462347
[probe-advice]: ../content/benchmarks.md#the-model-may-already-know-the-answer
[saturation]: ../content/benchmarks.md#the-benchmark-may-not-be-hard-enough-to-separate-systems

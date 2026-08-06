# VISTA: a harness whose traces are published and whose code is not

**Status:** done — examined 2026-08-06, no report, recorded in the overview's
scope section
**Origin:** `https://vista-research.github.io/` submitted 2026-08-06
**Pin examined:** `vista-research/vista-research.github.io` at
`61b71c52991441a13754d6b7675ec844cbe4e33f`, dated 6 August 2026 — the project
page and its replay data. There is no other repository in the organisation.

## What it is

VISTA — *A Visual Harness for Reasoning in an Interactive World* — from five
authors at MIT (Qiushi Han, Keya Hu, Linlu Qiu, Cathy Wu, Kaiming He), posted
5 August 2026. It gives a general-purpose multimodal model raw 512×512 PNG
frames of an ARC-AGI-3 game, free-form language to reason in, and what the page
calls a *"lossless visual memory"*. Using Claude Opus 5 as the base model it
reports completing all 25 public games with a 100% win rate and a perfect 100
Relative Human Action Efficiency score, using 56.0% fewer actions than
first-time human players.

There is no paper and no harness source. The page links three *other* people's
ARC-AGI-3 agents and one other harness; it links nothing of its own.

## The call

No report, on two independent grounds, either of which is sufficient.

**There is no inspectable implementation at a pinned commit.** The only
repository under `vista-research` is the project page itself. The atlas's third
genuine exclusion applies directly.

**And the memory does not outlive the session.** The unit here is one game run:
*"One agent plays each game from its first observation to completion."* Within a
run the agent keeps two markdown notes and a frame store, and those survive
context compaction — *"When the model approaches its context limit, it writes a
concise continuation state, then resumes from the current visual state in a
fresh context. Its notes, visual memory, and action history remain available."*
They do not survive the run. Checked against the traces rather than assumed:
across all 25 games, **zero** first-`GUIDE.md` writes reference any other game's
id, and each game's notes begin from that game's own first observations.

The atlas's boundary says compaction counts *"only when something survives the
session with an identity that could later be corrected."* Surviving compaction
is the easier half and VISTA clears it; the surviving unit still dies with the
run.

## Why it is recorded rather than dropped

### 1. The traces are published, and they are enough to audit the mechanism

This is the part worth generalising. The repository ships, for each of the 25
games, a `replays/claude-opus-5/data/<game>.json` and a `packs/<game>.pack` —
320 MB in total. The JSON is a complete run trace: every agent message, every
`inspect` call with its stated question and the exact regions requested, every
`read_pixels` call with its palette and sampled rows, and **every memory write
with its full content**.

From those files alone, with no harness source, the entire memory surface can be
reconstructed:

| Reconstructed from traces | Value |
| --- | --- |
| Memory targets | Two files: `GUIDE.md`, `WORKING.md` |
| `WORKING.md` writes | 204, across 23 of 25 games |
| `GUIDE.md` writes | 56, across 22 of 25 games |
| Write semantics | **Full-document replacement — 215 rewrites, 0 strict appends** |
| Note size | median 1,320 characters, maximum 3,121 |
| `inspect` calls | 208 |
| `read_pixels` calls | 901 |
| Total game actions | 7,542 |

And the headline claim is checkable from the same files. Recomputed here:
**25 of 25 runs carry `status: "WIN"`, every scorecard reports `score: 100`, and
`levelsCompleted == levelCount` in every run.** The claim survives its own
artifacts.

That is the finding: **a harness that publishes its run traces is inspectable
even when its code is not.** Everything above is a property of the memory
mechanism, established at a pinned commit, by an outsider, without the
implementation. The atlas's inclusion test asks for inspectable code, and it
asks for that because code is normally the only thing that settles what a system
does. Traces at this fidelity settle a large part of it. They do not settle
everything — what the prompt says, what happens on an error, what the compaction
boundary actually preserves, whether the frame store is bounded — and none of
those is visible here, which is why this stays a note.

### 2. The comparison table on that page is a taxonomy worth borrowing

The page sets four memory mechanisms against each other on *what is kept, what
is lost, how it comes back*:

- **Context window** — recent turns as tokens and KV-cache activations; loses
  whatever falls outside the window, with older visual detail compressed away;
  comes back through implicit attention over what still fits.
- **Program world model** — observations distilled into code: state,
  transitions, goal conditions; loses anything the reconstruction does not
  model, and the frames themselves; comes back by executing the reconstruction.
- **Written text notes** — the model's own description of what happened; loses
  everything not written down, *"the model chooses what to drop"*; comes back by
  re-reading its own text.
- **Lossless visual memory** — every returned frame at full resolution, indexed
  by turn and frame; loses **nothing**; comes back through `inspect` and
  `read_pixels`, on the model's own decision.

The third column is the useful one, and it is the column this atlas usually has
to reconstruct for itself. The framing of `inspect` as an *"explicit attention
mechanism"* at frame, region and pixel level is a good name for a thing several
systems here implement without naming: retrieval as the model deciding what to
bring back, rather than a ranker deciding for it.

The honest caveat on "loses nothing": it is lossless with respect to *what the
environment returned*, over one run. It is not a claim about anything surviving
the run, and the page does not make one.

### 3. The note rewrite is full-replacement, and the obvious criticism does not land

215 of the memory writes replace the whole document; none appends. So there is
no record of what a rewrite removed — the structural property the atlas
criticises wherever a model rewrites its own notes.

89 of those rewrites shrank the note. The largest cut 987 characters, from 1,443
to 456, in game `sk48` at turn 151. **Inspecting it, that is correct
behaviour**: the agent had just completed Level 4 and discarded the finished
level's confirmed mechanics and its 18-step plan, replacing them with Level 5's
geometry and a fresh hypothesis. Discarding a completed level's plan is what the
note is *for*.

Worth writing down because the cheap version of this check — count the
shrinking rewrites, report the biggest — would have produced a finding, and the
finding would have been wrong. The structural criticism stands (nothing records
what was dropped, so a bad drop and a good one look identical from outside);
the instance does not support it.

## The pairing worth keeping

[Cognitive Weave](2026-08-06-a-paper-and-its-official-implementation.md) was
examined the same day. It claims 34% and 42% over MemGPT, A-MEM and Mem0, and
ships 568 lines with no dataset, metric, result or test, and with its title
mechanism on a To-Do list. VISTA claims 25 of 25 and ships the run traces that
let a stranger recompute it in one pass.

Neither earns a report. They are at opposite ends of the axis the atlas's
[benchmarks page](../content/benchmarks.md) exists to measure, and the
difference between them is not rigour of prose or seniority of authorship — it
is whether the artifacts were published. One published the claim; the other
published the evidence.

## Open questions a reader should not assume away

- **Is the frame store bounded?** Every returned frame at full resolution, for a
  270-action run, is a lot of frames. Whether anything evicts, and what happens
  when it cannot, is not visible.
- **What does compaction actually preserve?** The page says notes, visual memory
  and action history remain available. The traces do not mark the compaction
  boundary, so how often it fired and what the continuation state contained
  cannot be checked from them.
- **What is in the prompt?** *"A short prompt"*, same for every game, is all the
  page says. For a harness whose thesis is minimalism, the prompt is the claim.
- **Does anything carry across games?** The traces say no. Whether that is a
  design decision or a limitation is not stated, and it is the question that
  decides whether VISTA is a memory system on this atlas's terms or a very good
  within-episode one.

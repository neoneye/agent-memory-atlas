# Two hygiene mechanisms from a benchmark that is not about memory, and what they imply for the shape of the page

**Written 2026-09-09.** Prompted by reading
[harbor-framework/terminal-bench](https://github.com/harbor-framework/terminal-bench)
at `83c7a6172d629c6575b785ab12c8db787bb2e323`. It is not a memory system — one
task, one fresh container, one session, graded at the end — so it earned a
known-limitations bullet and an entry on the benchmarks page rather than a
report. While reading it I found two practices that are cheap, checkable, and
absent from every benchmark this page describes. Both answer a problem the page
already states and leaves without a remedy.

---

## 1. The canary, and the half of contamination nobody here measures

Every one of Terminal-Bench's sixty-six `task.toml` files opens with a line of
the form `# harbor-canary GUID <uuid>`. Sixty-six of sixty-six carry one. It is
one line, written once, and it does something no probe design can do: if that
GUID ever appears in a model's output, the task is in the training data, and you
know it as a fact rather than as a suspicion.

The page's section **"The model may already know the answer"** states the trap
correctly and prescribes only the preventive half — fictional, high-entropy,
multi-hop probes so that pre-training cannot supply the answer and a plausibility
prior cannot hit it. That is good advice and it is not the same thing. Prevention
tries to make leakage *not matter*. A canary tells you leakage *happened*. A
benchmark can do everything the three properties ask and still be sitting in a
crawl, and nothing in the current advice would reveal it.

The distinction matters most for exactly the benchmarks this page depends on.
LoCoMo and LongMemEval have been public, downloadable and widely mirrored for a
long time. The page's whole argument about whether a bad score matters rests on
scores from those datasets, and it has no instrument that would tell it if the
questions had been memorised. A canary would not fix that retroactively — you
cannot add one to a dataset already released — but it is the reason a *new*
memory benchmark should carry one from its first commit.

**What the mechanism would look like for a memory benchmark.** Terminal-Bench's
unit is a task directory, so the canary lives in the task file. A memory
benchmark's unit is a conversation and a set of probes, so the canary belongs in
the source records — one high-entropy token planted in the haystack, never in a
question, never in an answer key, and checked against model outputs during
scoring. That is close to the shape the page's own probe advice already
describes, which is why it costs almost nothing to add: a benchmark generating
fictional high-entropy facts is one line away from generating a canary too.

**Honest limits.** A canary only fires if someone inspects outputs for it, which
means the harness has to look. It detects a leak and does not measure how much
the leak helped. And a benchmark published without one can never acquire one,
because the artifact a canary would have marked is already out.

## 2. Retirement, and the saturation the page names without a remedy

Terminal-Bench holds sixty-six live task directories and ninety retired ones in
an `archive/`. More tasks have been taken out than are currently in. It is a
*continuous* benchmark: the dataset is versioned and published on a hub with
tagged releases rather than frozen at a paper.

The page's section **"The benchmark may not be hard enough to separate systems"**
describes the failure this addresses: when a benchmark stops separating good
memory from a big context window, a score on it says little. The page has also
observed the memory benchmarks in use here saturating at the top. What it does
not name is that saturation is a maintenance problem with a known answer, and
that no memory benchmark it describes performs that maintenance — because a
dataset frozen at a publication cannot. Nobody removes a LoCoMo conversation
that every system now answers.

**The cost is real and Terminal-Bench pays it deliberately.** Retiring tasks
breaks comparability across versions: a 57.9% this month and a 44.6% three
months ago may be measuring different task sets. The mechanism that makes this
survivable is versioned releases with a resolvable dataset identifier, so a score
can name the version it was measured against. A memory benchmark that wanted
retirement would have to adopt the versioning first; retirement without it just
makes the numbers incomparable and nobody notices.

## 3. What both have in common, and what the page currently records instead

Neither is a scoring decision. Both are properties of a benchmark *as an
artifact*: does it carry a contamination guard, and does anything ever leave it.
Both are checkable in one command against a checkout. And neither appears in any
benchmark description on this page — not for the ones read directly at a pinned
commit, and not for the ones described from their papers.

What the page does record about a benchmark is: what it scores, how many items,
what licence, whether an artifact exists, and whether the numbers recompute. That
is the right set for answering *is this measurement trustworthy*. It is missing
the set that answers *will this measurement still be trustworthy next year*.

## 4. A restructuring proposal

### The problem, in numbers

`content/benchmarks.md` is 3,342 lines, nine top-level sections and about
forty-five subsections. Two of those sections have ended up doing the same job
in different registers:

- **Section 2, "What Benchmarks Exist"** (lines 72–596, four subsections) is
  where a benchmark's identity goes — found in a reviewed repository, read at a
  pin, or named from outside.
- **Section 6, "Does Anything Benchmark Forgetting?"** (lines 1370–2994, twenty-two
  subsections, 1,624 lines — half the page) has become the de-facto catalogue.
  Most of its subsections are individual benchmarks under argumentative titles:
  *"A benchmark whose baseline wins, and the category that cannot fail"*,
  *"A self-reported leaderboard whose artifacts are checkable anyway"*,
  *"The follow-up that argues the cheap baseline was the answer all along"*.

Those titles are the best writing on the page and they are useless for finding a
benchmark by name. The consequence is structural rather than stylistic: a new
benchmark has no single home, its identity gets split between section 2 and
section 6, and there is no place where the same facts are stated about every
benchmark in the same order. Adding the twelfth or twentieth benchmark makes this
worse in proportion.

### The proposal: separate the register from the argument

**A register.** One table, one row per benchmark, the same fields in the same
order, each cell short enough to scan:

| Field | Why it is in the register rather than the prose |
| --- | --- |
| Name, artifact URL, licence | Identity, and whether it can be obtained |
| Read at a pin? | The atlas's own standard of evidence |
| Unit | Conversation, task, document set — decides what "one item" means |
| Size | Items, and the split |
| Scores what | Recall, deletion, forgetting, capability |
| Contamination guard | The canary column, new |
| Maintained | Frozen at a paper, or versioned with retirement — new |
| Reports an interval | Whether a score comes with a confidence bound |
| Reports cost | Dollars or tokens per run |
| Reproducible from the artifact | The page's existing bar, stated per benchmark |

The last four are the columns this page's own critique sections keep asking for
and never tabulate. Two of them come from a benchmark that has nothing to do with
memory, which is the point of writing this down.

**The argument keeps its titles.** Sections 3 through 7 stay narrative and stay
argumentative. What changes is that each essay stops restating identity and
instead links to the register row. The register is where a reader goes to
compare; the essays are where they go to understand.

**Where the register lives.** Inside section 2, replacing the current four
subsections' role as the identity store, with those subsections becoming
provenance notes on the register rather than parallel catalogues.

### What not to do

- **Do not split into per-benchmark pages.** The systems corpus works that way
  because each system needs a full mechanism reading. A benchmark needs a row and
  a paragraph; 393 report pages plus forty benchmark pages would bury the
  argument that makes this page worth reading.
- **Do not let the register become an uncited list.** Every cell should be
  traceable to something read. The atlas already binds counts to frontmatter and
  fails the build when they drift; a register with no such binding will rot, and
  a rotted register is worse than prose because it looks authoritative.
- **Do not add another specification this page does not run.** Section 9 already
  admits the page holds others to a standard it does not meet, having specified a
  thirteen-step deletion sequence and a contradiction test and shipped neither.
  Every field above is readable from an artifact already in hand. None of them
  needs a harness. That constraint is deliberate.

### The smallest useful first step

Add the two new columns — contamination guard, and maintained — to the
benchmarks already described, filling them only where the artifact was read at a
pin and writing *unknown* everywhere else. That is a few hours of checking, it
produces an honest table with visible gaps, and the gaps are themselves the
finding: if the column is empty for every memory benchmark and full for the one
capability benchmark that wandered into scope, that is worth saying plainly.

---

## Provenance

Terminal-Bench facts are from a full clone read at
`83c7a6172d629c6575b785ab12c8db787bb2e323`: sixty-six task directories each with
a `task.toml`, sixty-six carrying a canary GUID, ninety directories under
`archive/`, thirteen leaderboard submissions each recording an accuracy with a
95% confidence half-width, an average trial duration, token counts and a cost.
Nothing was installed or run. The claim that no benchmark described on this page
carries a contamination guard is a claim about the atlas's own records and about
the artifacts read at a pin, not about every dataset in the world.

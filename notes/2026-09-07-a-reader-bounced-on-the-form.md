# A reader bounced on the form

**Status:** proposal, with two changes already landed and one pilot to run
**Origin:** feedback from the author of `no_human`, received 2026-09-07, on
[their own report](../content/systems/no-human.md). Quoted in full because the
complaint is precise:

> At first glance this assessment report looked like something I'd want to
> create but after reading some of it, it exemplifies a lot of what I hate
> about AI code agent explanations. It's so unnecessarily difficult to read
> and process. AI struggles to judge what to define and set up context for. It
> jumps around in degree of specificity and it does not distill the
> important/significant parts well. I still have to sort what's what and
> figure out what's the big deal. Not to mention the wall of text with barely
> any spacing between the lines.

This is the first reader from a reviewed repository to say the report was
right and unreadable. The atlas is written for exactly that reader. Nothing in
the complaint is about a fact, and the facts in that report were checked
against the code at the pin; the complaint is that the reader could not get to
them.

## What is already done

Two of the sentences had mechanical causes, fixed in `9a9ca1de` and
`6c175368`.

- **"Barely any spacing."** Running text sat in an 820px column at 16px,
  which measured 113 characters per line on the live page. Nobody sets prose
  that wide, and at that measure the leading reads as cramped whatever its
  value. `.prose` now sets a 34em measure (about 75 characters), 17px, 1.72
  leading and a 1.5em paragraph gap. Tables, code, diagrams and the h2 rules
  keep the column.
- **The diagram.** It rendered 2.28:1 and was scaled to a third of its height
  to fit. A `;` in one transition label had spawned eight phantom states, and
  the rank between the two Active states and their three exits carried eight
  labelled edges side by side. Regrouping under a composite state brought it
  to 1.24:1. Five other state diagrams carried the same `;` fault, and
  `check_mermaid.py` now refuses it — and its older colon rule turned out to
  have been dormant for every captioned diagram, which is also fixed.

Those were the easy half. The other three sentences are about the prose.

## What the other three sentences point at

Read against the no_human report specifically, each maps to something
countable.

**"Wall of text", the part spacing cannot fix.** The report's paragraphs are
110 words at the median and 228 at the longest; 18 of its 45 paragraphs exceed
120 words and 11 exceed 150. The corpus median is 44 words. This report is an
outlier by two and a half times, so the complaint is not about the house style
— it is about this report, and the reports like it. At the new measure a
200-word paragraph is 17 lines, which is a block whatever the leading.

**"Jumps around in degree of specificity."** The first paragraph of the
executive summary is one sentence of identity — a ticket-to-pull-request agent
with a learning store inside it — followed in the same paragraph by the
licence, the commit count and date range, the author count, the line count of
the package and of the orchestrator file, the test-function count, and the
outcome of the security screen including how many manifests were inside a
cooldown. That is four altitudes in 130 words. A reader who wants the identity
is made to climb through the census to reach paragraph two, where the finding
is.

**"Does not distill the important parts."** The report's significant finding
is in the second paragraph of the summary and in section 2: a store whose
founding contract — *a human confirms every learning* — was reversed on 31
August 2026 into bounded auto-management, after a flood of 487 pending
proposals against 53 active, most of them a templated *"a task finished"*
with no evidence. That is the big deal. It is present, and it is correct, and
it is the second thing said. Only section 2 opens with its own finding; the
other thirteen open with mechanism and arrive at the finding somewhere in the
middle. The
table of contents lists fourteen section titles that name topics
(*Retrieval Mechanics*), not conclusions, so it does not help either.

**"Struggles to judge what to define and set up context for."** Section 2
defines the `source` / `origin` split in full — nine enumerated values with
their producers — before saying why the split exists (three producers once
wrote provenance into `source` and were never queued). The reason is the
sentence worth reading; the enumeration is reference material. The same
pattern recurs with file:line citations placed mid-sentence, so that a clause
about a behaviour is interrupted by where it lives before it says what it
does.

None of this is a density problem. The audience is senior engineers, the
reviewed repository's own developers, and coding agents, and the density is
the point of the atlas. It is an ordering and a chunking problem, and those
have rules.

## What can be done

In order of leverage. Each item is small on its own; the first three change
what a new report looks like, the last two keep old reports from staying as
they are.

### 1. Rewrite the no_human report as the pilot

The reader who complained is the one who will read it again. Rules for the
rewrite, and for the format after it:

- **Lead every section with its finding, in one sentence, before any
  mechanism.** Section 2 opens: *A memory here is a lesson with a lifecycle,
  never an observation.* That is a lead sentence, and it is the only section
  that has one. Section 7 should open the same way: nothing is deleted, every
  exit is a flag with an audit row.
- **One point per paragraph, and a ceiling of 120 words.** A paragraph that
  needs 200 words is two paragraphs with a joint the writer did not find. The
  corpus median of 44 shows the atlas can already do this.
- **Move the census out of the summary paragraph.** Licence, commit count,
  author count, line counts, test counts and the screen's outcome go in one
  place: the existing metadata band at the top of the page carries the pin and
  the date and could carry these, or they become the first block of the file
  index appendix. They stay in the report; they stop being the second sentence.
- **Say why a distinction exists before enumerating it.** The `source` /
  `origin` paragraph becomes: the reason, then the two columns, then the
  values as a compact list. The reader who needs the nine values can read the
  list; the reader who needs the design decision has it in one sentence.
- **Citations end the sentence.** `queue.py:1162-1197` belongs after the claim
  it supports, in parentheses, once. A sentence with a citation in the middle
  is read twice.
- **The summary's first paragraph is: what it is, what is notable, what
  fails.** Three sentences that a reader can stop after. The 31 August
  reversal and the flood that caused it are sentence two.

Then send the author the link, and ask the same question.

### 2. Put those rules in the format document and the skill

`content/methodology/per-repo-report-format.md` and
`.agents/skills/add-memory-system/SKILL.md` say what a section contains, and
say nothing about how a section opens or how long a paragraph runs. Add the
six rules above to both, in the same register as the existing *"Write about
the system, not about the writing of the report."* The skill already has a
pre-integration checklist; *"every section opens with its finding"* and *"no
paragraph over 120 words"* are two lines on it.

### 3. Add a paragraph ceiling to the build

The atlas already runs a ceiling on corpus-scoped superlatives — a count that
may fall and may not rise — and it has worked because the number is in the
test output every run. The same shape fits here:

- `check_paragraph_length.py` counts paragraphs over 150 words in
  `content/systems/*.md`, excluding fenced code, tables and list items.
- Today the count is 301, in 100 of 378 reports. That is the ceiling.
- The check fails when the count rises. It prints the count every run, and the
  ten longest with their report and section, so the next re-analysis pass
  knows where to spend an hour.

150 rather than 120 for the ceiling, because the ceiling is a floor on
regression, not the target; the target lives in the format document. With the
ceiling at 150 and the 83 paragraphs over 200 listed first, the worst
offenders are a bounded job.

### 4. Titles in the table of contents that carry a conclusion

The sticky table of contents lists section titles. For a report page it could
list the section's lead sentence, or the first eight words of it, under the
title — which is free once rule 1 holds, because the lead sentence is then a
predictable line the build can lift. A reader scanning the rail would see
*"Nothing is deleted; every exit is a flag with an audit row"* under
*Write Mechanics* and know whether to stop there. This is a build-script
change and a CSS change, and it is worth nothing until the sections have lead
sentences, so it comes after 1 and 2.

### 5. Fold the rules into re-analysis

`.agents/skills/reanalyze-memory-system/` re-pins a report against a newer
commit. Every report it touches is a report being rewritten anyway; adding the
six rules to that skill's checklist means the 100 reports over the ceiling get
fixed at the rate the corpus is already being re-read, with no separate
campaign.

## What not to do

- **Do not add glosses.** *"A tombstone is…"* for a senior engineer is the
  other way to be unreadable. The audience memo stands.
- **Do not trade density for summary.** The fix for a 200-word paragraph is
  two paragraphs, not a 60-word paragraph with the evidence removed. Every
  file:line anchor stays; it moves to the end of its sentence.
- **Do not rewrite 378 reports in a campaign.** The ceiling stops regression
  today; re-analysis fixes the rest as it goes. A campaign would be a hundred
  reports edited by an agent under a word budget, which is how a report gets
  shorter without getting clearer.
- **Do not narrate the change in the report.** A rewritten no_human report
  says what no_human is. It does not say it was rewritten.

## Order

1 today, because the reader is waiting and it is one report. 2 and 3 in the
same commit, because a rule with no check decays from the newest end. 5 is a
checklist line. 4 after the pilot shows what a lead sentence looks like across
fourteen sections.

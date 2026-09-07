# A reader bounced on the form

**Status:** proposal, with two changes already landed and one pilot to run
before any rule becomes mandatory
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

This is the first reader from a reviewed repository to say a report about
their own code was hard to read. The atlas is written for exactly that reader.
The complaint concerns presentation; it does not assess factual accuracy either
way, and nothing below should be read as the author having vouched for the
report's claims.

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
countable. What follows is a hypothesis about the cause — ordering and
chunking — that the counts support and the pilot below is meant to test. It
is not a complete account of the reader's difficulty, and the pilot may show
that other things matter as much.

**"Wall of text", the part spacing cannot fix.** The report's paragraphs are
110 words at the median and 228 at the longest; 18 of its 45 paragraphs exceed
120 words and 11 exceed 150. The corpus median is 44 words. This report is an
outlier by two and a half times, which suggests the length is specific to this
report and the ones like it rather than to the house style — though a short
paragraph can bury its point just as well, so length is the countable symptom
and not the whole diagnosis. At the new measure a 200-word paragraph is 17
lines, which is a block whatever the leading.

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
it is the second thing said. Three sections open with a statement of
behaviour rather than mechanism — section 2 (*a lesson with a lifecycle, never
an observation*), section 6 (*there is no query at injection time*) and
section 7 (*writes are deferred and evidence-driven*) — and even those stop
at the behaviour: none says what it costs or buys the reader, which is the
part they are asking for. The distinction worth pursuing is not whether a
section opens with a finding but whether the opening states the behaviour's
consequence. Section 4 opens with a function call, section 9 with a bolded
label, and section 3 with *"everything is one Python process and one SQLite
file"* — true, and silent on what follows from it. The
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

The working hypothesis, then, is that this is mostly an ordering and a
chunking problem, and those have rules. The audience is senior engineers, the
reviewed repository's own developers, and coding agents, and the density of
evidence is the point of the atlas — but density is not the same as
completeness of every detail, and a senior reader can still need a distinction
explained when its meaning here is local to the system. Two things the rewrite
may remove are repetition and detail that changes nothing for the reader; the
evidence behind a claim is not on that list.

## What can be done

In order of leverage. Each item is small on its own; the first three change
what a new report looks like, the last two keep old reports from staying as
they are.

### 1. Rewrite the no_human report as the pilot

The reader who complained is the one who will read it again. Candidate rules
for the rewrite — candidate because the pilot is what decides whether they
enter the format:

- **Open an analytical section with its main point, and say why it matters
  before expanding the mechanism.** One sentence, or two when a qualification
  needs room; a verdict forced into one sentence everywhere manufactures
  significance or drops the exception. Section 2's opening — *a lesson with a
  lifecycle, never an observation* — is the shape, and it still needs its
  second half: what that buys the operator. The file index, History and Open
  Questions sections are reference and are exempt.
- **Check every lead against its section and against the pinned code.** The
  first draft of this note proposed *"nothing is deleted"* as section 7's lead.
  The report contradicted it in one place and agreed with it in two others:
  the mental model said a reject on the outcome or review path deletes, the
  reliability section said an outcome-origin reject is the only product path
  that removes a row, and the description said nothing is ever deleted.
  Reconciled against the pin before the rewrite: `reject()` deletes an
  unconfirmed proposal from any origin outside its six-member archive set,
  which is the outcome path, review and reply; and four further paths —
  `nh rules remove`, `nh skills remove` and the matching API routes — call
  `delete_memory` directly on any row a prefix resolves, with no origin check
  and no audit row. None of the three formulations was right, and the
  appendix's own absence search shows why: it counted the one `DELETE`
  statement and not its five callers. A lead sentence written under a brevity
  rule is where this error is easiest to make and hardest to see, and the
  correction is logged in the overview's known-limitations list, not narrated
  in the report.
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

Then send the author the link with a test of comprehension, not of agreement.
Three questions, asked without the expected answers: from the opening alone,
what is the report's central claim about the store and what qualification
does it carry; for any section, where is the evidence for its lead sentence;
and where did reading remain difficult. A fourth question is separate and
scored separately: do they agree with what the report puts first. An accurate
paraphrase plus a disagreement passes the readability test — a reader can
understand the report perfectly and weigh a different limitation. The
rewrite's own ordering, for the record: the 31 August reversal first, because
the report connects four mechanisms to the flood that forced it — the
success-proposal gate off by default, the 45-day archive of unconfirmed
proposals, the two-occurrence threshold for corrections, and the ten-a-day
cap; and among limitations, the read-side term screen that fails open,
whose supported consequence is that a matcher error lets otherwise eligible
memories into the prompt without that screening step, with only the
write-time quarantine — which fails closed and is a separate guard — standing
in front of a term the operator wanted kept out. Whether that is the
limitation a reader weighs first is their call.

If the three answers are accurate and every retained conclusion still carries
the evidence and the qualifications it had before, the format is adopted
provisionally: one rewrite is evidence that the shape helps, not proof that
each rule — least of all the exact 120-word ceiling — caused the improvement.
If the answers are not accurate, the hypothesis was wrong or incomplete, and
this note gets a follow-up rather than the skill getting six new rules.

### 2. Put the rules that survive the pilot in the format document and the skill

`content/methodology/per-repo-report-format.md` and
`.agents/skills/add-memory-system/SKILL.md` say what a section contains, and
say nothing about how a section opens or how long a paragraph runs. After the
pilot, add whichever of the rules above held up to both, in the same register
as the existing *"Write about the system, not about the writing of the
report."* The skill already has a pre-integration checklist; *"every
analytical section opens with its main point and why it matters, checked
against the section and the pin"* and *"no paragraph over 120 words"* are two
lines on it. A rule for definitions
belongs there too, and it is not *"never define"*: define a term at first use
when its meaning in this system differs from the usual one or when the report
turns on it, and otherwise trust the reader.

### 3. Add a paragraph guardrail to the build

The atlas already runs a ceiling on corpus-scoped superlatives — a count that
may fall and may not rise — and it has worked because the number is in the
test output every run. A single corpus-wide count is the wrong shape here,
though: it would let a new 300-word paragraph in tomorrow's report pass
because someone split two old ones elsewhere. Two checks, described for what
they are:

- **Each report's violation count may not rise.** `check_paragraph_length.py`
  keeps a baseline file listing, per report, the number of paragraphs over
  150 words at the time the check was introduced. A report with no baseline
  entry — every new report — has a baseline of zero, so a new oversized
  paragraph fails on its own there. Lowering an entry is the only edit the
  file accepts. What this does not catch, said plainly: within a report that
  has a baseline, one oversized paragraph can be replaced by another at the
  same count. That is the limit of a count, and the reason the readability
  pass in item 5 is separate work.
- **The aggregate is reported, not enforced.** The total and the ten longest
  paragraphs, with report and section, print every run so a re-analysis pass
  knows where an hour goes. That number limits accumulated debt and is not a
  readability score; passing the check says nothing about whether a section
  leads with its finding.

Counting method, so the baseline is reproducible: a paragraph is a run of
non-blank lines in the Markdown body after the frontmatter, with fenced code
blocks removed; headings and table rows are excluded; **list items count**,
each item as its own paragraph, because a bullet can carry the same wall as a
paragraph and the no_human report has items of 67 words. Words are
whitespace-separated tokens. The figures in this note — 301 paragraphs over
150 words in 100 of 378 reports, 83 over 200 — were measured with the old
method, list items excluded, and are a lower bound. The baseline is written
from a run of the new method, not from these numbers.

150 rather than 120 for the guardrail, because it is a floor on regression,
not the target; the target lives in the format document.

### 4. Deferred: lead sentences in the table of contents

The sticky table of contents lists section titles. Once sections have lead
sentences the build could lift them into the rail. Deferred, for two reasons
that outweigh the appeal: fourteen extra sentences may make the rail harder to
scan than the titles alone, and a truncated lead — the first eight words —
can drop the qualification that makes the finding true, as the *"nothing is
deleted"* example above shows. If it is ever done, it shows the full sentence
or nothing, and only after the pilot has produced sentences worth showing.

### 5. Add a readability pass to re-analysis

`.agents/skills/reanalyze-memory-system/` re-pins a report against a newer
commit. When the mechanism is unchanged the body can be left untouched, so
re-analysis does not rewrite prose by itself; a readability pass is added
work, and the skill has to say so — one step, run on the report being
re-pinned, applying the surviving rules to the sections it already has open.
The cost is bounded by the report. A pass limited to the sections a re-pin
has open cannot promise to lower every report's count on every visit; what it
promises is that reports with oversized paragraphs get shorter in the sections
that were touched, at the rate the corpus is already being re-read, with no
separate campaign.

## What not to do

- **Do not define everything, and do not define nothing.** *"A tombstone
  is…"* for a senior engineer is the other way to be unreadable; the `source`
  / `origin` split, whose meaning is local to no_human, is exactly what needs
  a sentence. The rule is in item 2.
- **Do not trade evidence for summary.** The fix for a 200-word paragraph is
  two paragraphs, or one with the repetition and the inert detail cut, not a
  60-word paragraph with the evidence removed. Every file:line anchor that
  supports a claim stays; it moves to the end of its sentence.
- **Do not rewrite 378 reports in a campaign.** The guardrail, once built,
  would stop regression; re-analysis would fix the rest as it goes. A campaign would be a hundred
  reports edited by an agent under a word budget, which is how a report gets
  shorter without getting clearer.
- **Do not narrate the change in the report.** A rewritten no_human report
  says what no_human is. It does not say it was rewritten.

## Order

1 first, because the reader is waiting and it is one report, and because it
is the test of everything else. 2, 3 and 5 only after the pilot passes the
test in item 1, and then in one commit, because a rule with no check decays
from the newest end. 4 stays deferred.

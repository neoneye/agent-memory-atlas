---
name: remove-meta-narrative
description: Detect and remove narration of the project's own history from published pages, so a reader gets the current state instead of a draft's changelog. Use before publishing or committing any edit to content/ or site/, when correcting a claim that turned out wrong, when folding a new finding into an existing page, and whenever an edit adds a paragraph rather than replacing one.
---

# Remove Meta-Narrative

A published page states **what is true**. A `## History` entry states **what
changed**. When the second leaks into the first, the reader has to reconstruct
the project's sequence of positions before they can find out what it currently
thinks — and they were only ever asking the second question.

This has been corrected in this repository at least six times, including one
sweep across 273 files, and it recurs because the rule is easy to agree with and
the failure does not look like a violation while you are committing it.

## The shape of the failure

**Almost always: appending instead of replacing.** A new fact arrives. The
natural edit is to write a paragraph stating it and leave the paragraph it
supersedes in place. Both are now on the page, the newer one hedged into a
transition — *"the argument has started to fail"*, *"this is no longer none"* —
and the page argues with itself. Nothing was deleted, so nothing felt wrong.

Four forms, in increasing order of how well they hide:

| Form | Looks like | Caught by |
| --- | --- | --- |
| **Explicit** | "This report previously said", "re-read on <date>", "the atlas had missed" | grep 1 |
| **Self-report** | "this page **said** '164 open-source systems'", "the count **was** N **until** 7 August", "the sentence **was false** in the way that matters" | grep 4 |
| **Adverbial** | "there are **now** two paths", "**still** inverts", "**no longer** none", "**has since** been read" | grep 2 |
| **Structural** | a paragraph superseded by the next one, both retained; a bullet holding two positions | **nothing automatic — you have to read it** |

The structural form is the one that matters most and the one the greps cannot
see, because every individual sentence is fine.

**The self-report form is the one that slipped past this skill in practice.** A
licence section opened *"This page said '164 open-source memory systems' until
7 August 2026. The sentence was false in the way that matters…"* — three
sentences of the page grading its own past claim, in the body, when the
correction was already logged and dated in the known-limitations list. It evaded
grep 1 (which had "this page **first/named/called**", not "this page **said**")
and grep 3 (whose trajectory verbs did not include reporting verbs or a bare
"was false"). The tell is a **reporting or self-judgement verb whose subject is
the project** — the page, the report, the atlas, the count, the headline, the
sentence — rather than the system under review. When the page says what the page
used to say, cut it; the correction lives in the known-limitations list.

## Where this narration is correct — do not strip it

Removing it from these places is a worse error than leaving it in the body.

- **`## History` in a system report.** One dated entry per reading, newest first,
  with the full sha. This is the log; its tense is correct there, and
  `check_history.py` fails the build without it.
- **`## History` in `content/overview.md`.** What a reading taught the *method*.
- **The known-limitations list.** A published claim that was wrong is corrected
  *there*, dated, saying what was wrong and in which direction. That record is
  the project's honesty and deleting it to make a page read cleanly is the
  opposite of the point.
- **`notes/`.** Working documents. A changelog is the genre.
- **Facts about the subject's own history.** "Until 31 July 2026 neither variable
  was assigned anywhere in the repository" describes the code. Keep it.
- **Facts about an external work.** A survey's publication date, a paper's
  figures, a commit that fixed something upstream.

## Detect

Run all four, over the **body only**. Stop at `## History` — and, in
`content/overview.md`, stop earlier still, at `### Known Limitations`: everything
from there to `## History` is the dated correction log, which legitimately
narrates past claims ("previously said", "was wrong", "until <date>"), so
scanning into it buries the real body hits under dozens of correct ones. The
sed guards below stop at whichever comes first.

All four need triage. On this repository's rubric page, grep 1 returns five hits
and all five are legitimate — "re-reading a system is the expensive part" is a
statement about method, not a narration of a past position.

```sh
# 1 — explicit narration
sed '/^### Known Limitations$/q; /^## History$/q' <file> \
  | rg -n -i 're-read|re-review|re-pin|previously (said|reported|found|named)|this (report|page) (first|named|called)|the atlas (found|missed|had)'

# 2 — adverbial leakage, high false-positive rate by design
sed '/^### Known Limitations$/q; /^## History$/q' <file> \
  | rg -n -i '\b(now|still|no longer|used to|already|newer|earlier|these days|has since|has started|as of this reading|at the time of writing)\b'

# 3 — the project narrating its own trajectory. High yield.
sed '/^### Known Limitations$/q; /^## History$/q' <file> \
  | rg -n -i '(atlas|report|corpus|rubric|census)[^.]{0,50}(has now|now documents|has since|has not previously|had not|used to be|previously)|the reason this (report|page)|this atlas.{0,3}s (tooling|screener|scripts|build)|the atlas (can|could|should) (say|said|call|claim)|in a single round'

# 4 — the page reporting or grading its own past claim (the self-report form).
# A reporting/judgement verb whose subject is the project, or a state the page
# says it held "until" a past date. Highest yield of the four on correction edits.
sed '/^### Known Limitations$/q; /^## History$/q' <file> \
  | rg -n -i '(this|the) (page|report|atlas|headline|tagline|sentence|count|matrix|census|table) [^.]{0,60}\b(said|read|claimed|stated|listed|counted|called it)\b|\bwas (false|wrong|misleading|inaccurate|overstated|stale)\b|\buntil [0-9]{1,2} (january|february|march|april|may|june|july|august|september|october|november|december) [0-9]{4}'
```

Grep 4 has two triage traps, both already illustrated in the tables below. A
reporting verb whose subject is the *subject system* is fine — "the README said
it forgets" describes the code. And "**until** <date>" bounding a *subject* fact
is fine — "until 31 July 2026 neither variable was assigned" describes the
repository, not the page. Cut only when the thing that said, was wrong, or held
until a date is *this project*.

Grep 3 is narrow **on purpose**. Do not widen it to `this atlas|in this corpus`:
comparative claims — "the only system in this atlas that…", "most systems in this
corpus collapse these" — are current state and correct, they outnumber the real
hits by roughly fifty to one, and in a 260-file sweep two genuine hits sat
unnoticed inside that noise until the pattern was narrowed to trajectory verbs.

Then the part no command does: **read every paragraph you added or touched, and
the one immediately before and after it.** You are looking for two paragraphs
that hold different positions on the same question.

## Triage each hit: is the word about the subject, or about this project?

| Keep — about the subject | Cut — about this project |
| --- | --- |
| "values this key has **previously** lost" | "there are **now** two write destinations" |
| "evaluated against **now** or against an `asOf`" | "**still** archived at the third re-assertion" |
| "the pattern must **still** rank in the top five" | "the audit gap is **no longer** open" |
| "holds what is **no longer** true" (a tombstone file's contents) | "**already** covered in the previous pin" |
| "the only system in this atlas that routes them separately" | "the defect this atlas has **now** found five times in a fortnight" |
| "drops the summary when a message **no longer** exists" | "MemoryAgentBench **has since** been read above" |
| "the README **said** it forgets on restart" (about the code) | "this page **said** '164 open-source systems' **until** August" |
| "**until** 31 July 2026 neither variable was assigned" (the repo) | "the count **was wrong** in the way that matters" |

**The test:** if the sentence would have to change when *this project* changes
rather than when the *subject* changes, it is the wrong kind, whatever word
carries it.

## Correct

Do not edit the transition. Rewrite the passage as the answer to *"what is the
case?"*, and let the replaced text go.

The corrected passage has this shape, in this order:

1. **The current position, stated flat.** No transition, no contrast with a
   position the reader cannot see. "Two systems here carry it" — not "this is no
   longer none".
2. **The evidence for it**, named and checkable.
3. **The live consequence** — what follows *now*, not what stopped following.
4. **One origin, not two arguments.** If the old paragraph gave a reason that no
   longer holds, delete the reason. Do not leave it standing with a rebuttal
   underneath.

Then put what changed in the History entry or the known-limitations list, where
a reader who wants the sequence can find it.

**Worked shape:**

> **Before** — two paragraphs, the second arguing with the first:
> *"…the omission is not obviously costing this corpus many marks."* …
> *"**The rarity argument has started to fail.** … Two is not many, but it is
> **no longer** none, and the counter-argument **that survives** is narrower…"*
>
> **After** — one paragraph, current state:
> *"Two systems here carry it: [A], whose … ; and [B], which … So rarity is not
> what keeps it off the list. What keeps it off is that two readings are not
> enough to say what separates a rollback from an undo button over a log nobody
> keeps."*

## Red flags — stop and rewrite the passage

- You are adding a paragraph and keeping the one above it.
- You wrote a bolded sentence announcing that a previous position has changed.
- You quoted what the page, the count, or the headline used to say — or called a
  past claim false, wrong or misleading — anywhere but the known-limitations log.
- The passage contains a contrast whose other half is not on the page.
- You are hedging a new fact to avoid contradicting an old sentence — the old
  sentence is the thing to delete.
- A reader would have to know what the page said last week.

## Common mistakes when correcting

- **Stripping the History entry too.** The log is required and correct. Move the
  narration into it rather than deleting the fact.
- **Deleting a correction record.** A wrong published claim belongs in the
  known-limitations list, dated. Cutting it hides the error.
- **Over-triaging the adverb grep.** It has a high false-positive rate on
  purpose; "are **used to** prime the renderer" and "a grant is **still**
  current" are both correct. Read each hit before touching it.
- **Fixing the words and leaving the structure.** Removing "has started to fail"
  from a bullet that still holds two positions makes the contradiction quieter,
  not absent.
- **Leaving a running tally in place.** "The atlas has now found this five
  times", "the fourth instance in the corpus" — a count of the project's own
  findings is stale on the next reading and sizes a defect by the reader's
  knowledge of the project. Point at the pattern page or the census section that
  collects the instances, and let it hold the count.
- **Editing only the file you were pointed at.** The same passage is usually
  paraphrased in the homepage card, the verdict entry and the overview family
  prose. Sweep the same vocabulary through every file the change touched.

## After correcting

`npm run build && npm test`. Rewriting a paragraph often moves a count or an
external citation out of the block that exempted it — `check_claim_counts.py`
scopes its external-corpus exemption per paragraph, so a survey's figures
separated from their `arXiv:` link start failing. That is the checker working;
re-anchor the citation at the claim.

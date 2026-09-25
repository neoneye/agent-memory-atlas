# Written to be checked, not yet to be read

**Status:** proposal. Nothing below has landed. Measurements are from the tree at
`879c679e6`, 2026-09-25, using the method in the [appendix](#method).
**Builds on:** [2026-09-07-a-reader-bounced-on-the-form.md](2026-09-07-a-reader-bounced-on-the-form.md),
which diagnosed one report. This note covers the whole site: reports, pattern
pages, the overview and the verdicts.

The atlas is built so that any claim can be checked. That part works, and
nothing here trades it away. Every anchor, pin and quoted line stays. What the
atlas is not yet built for is a reader who goes from top to bottom. The point is
usually present and correct, but it arrives second, after a census, a caveat or
a list of absences. On the site's largest pages it arrives after several hundred
thousand words.

The audience stays the one in
[`per-repo-report-format.md`](../content/methodology/per-repo-report-format.md#who-these-are-written-for):
senior engineers, the reviewed projects' own developers, and coding agents.
Nothing here proposes glosses, plain-language leads or softening. It proposes
three things: the finding goes first, each fact is said once, and every
cross-reference is a link.

## What already works

The fixes below extend four things the atlas already does well.

- **The overview's *In Short*.** Five numbered findings, each in bold as a claim
  with the count it rests on, followed by the mechanism. This is the house voice
  at its best, and it is the model for everything below.
- **Eyebrows.** *"A draft is written but not injected"* (PLUR). *"The guard
  against a second copy is spelled one way"* ([kiwi-mem](../content/systems/kiwi-mem.md)). One line each, a finding rather
  than a topic, and they read well.
- **Mental Model openers.** *"A memory is a sentence the model wrote and a set
  of judgements about it."* The unit is defined in a single sentence, and the
  reader has a frame before any file path appears.
- **no_human's summary, as it now reads.** What it is, what is
  notable (the 31 August reversal), what is weak, all in one paragraph a reader
  can stop after.

## What the measurements show

**Long paragraphs are coming back, mostly through History.** On 2026-09-17,
commit `77a926e68` recorded zero prose paragraphs over 200 words. That count
used a method the repository does not keep. With the method in the appendix,
comparing the tree at `77a926e68` with today:

| | 2026-09-17 | 2026-09-25 |
|---|---|---|
| Paragraphs over 200 words, outside `## History` | 30 | 43 |
| `## History` paragraphs over 120 words | 475 | 864 |
| `## History` paragraphs over 200 words | 143 | 237 |

Every re-pin adds a History entry, and History entries are written as a single
paragraph. The median History paragraph is 98 words, twice the corpus median of
48. Vestige's 2026-09-11 entry runs to about 400 words and re-describes the new
benchmark suite in full. That description belongs in section 10, which the entry
says was rewritten. The guardrail that the 2026-09-07 note proposed (item 3)
was never built, so the gains from the split campaign are being lost at the rate
re-pins happen.

**Sentences run long.** The median sentence is 21 words, but the p90 is 44, and
1,759 sentences exceed 60 words. Most of the long ones are an enumeration joined
by semicolons, or a claim broken up by an em-dash aside and a mid-sentence
`file:line`.

**The summary opens with a census.** In 507 of 627 reports, the first summary
paragraph carries at least one of these: a licence (427), a line count (413), a
commit count (211) or the screen's result. PLUR is typical. Its first sentence
says what it is in eight words, then spends forty on commits, authors, line
counts and test counts. Its second sentence is the screen. The third says where
the store lives. The finding (*"Six of seven marks, and the one that decides the
character of the system is `trust_state`"*) opens paragraph two. The
2026-09-07 note proposed moving this census into the metadata band; that has
not happened.

**Descriptions are paragraphs.** The frontmatter `description` feeds cards and
link previews. It has a median of 38 words, 266 are over 40, and the longest is
153. PLUR's is one 75-word sentence that lists five mechanisms. The eyebrow
already does the one-line job well; the description should be the second line,
not the whole report in miniature.

**Pattern pages are mostly catalogue.** `## Seen in the atlas` makes up 86% of
[rejected-value-tombstone](../content/patterns/rejected-value-tombstone.md)
(9,778 of 11,342 words), 89% of
[scope-as-a-first-class-key](../content/patterns/scope-as-a-first-class-key.md)
and 87% of the trust-state machine. `AGENTS.md` sends a builder to that section
to find *"the systems worth reading"*. At 9,778 words it is no longer a pointer
to those systems.

**The overview is the corpus restated.** It is 428,000 words long. §1 Taxonomy
is 91,000, §2 Comparative Matrix is 221,000 and §11 Appendix is 75,000. §8 *What
I Would Build* (822 words) and §10 *Practical Checklist* (453) are the two
sections `AGENTS.md` sends a builder to, and they come after roughly 340,000
words. Eight separate lines of the overview link to PLUR. The verdicts page is a further
218,000 words in one section.

**Verbal tics that stand in for a point:**

| Phrase | Count in reports |
|---|---|
| *worth naming* | 271 |
| *worth reading* | 221 |
| *worth noting* | 90 |
| *worth knowing* | 64 |
| *genuinely* (+ adjective) | 338 |
| em-dash | 13.9 per 1,000 words, about one every 72 |
| *nothing* | 3.7 per 1,000 words |
| *elsewhere* | 281 uses; 1 has a link within 60 characters |

The last row is the one that costs the reader most. Vestige's History, for
example, says *"the same ruling this atlas applied to a declared approve tool
elsewhere"*. That is a precise reference with the name taken out, and a reader
cannot follow it.

## Voice: seven rules

These are written in the register of the format document so that they can move
there unchanged if they hold up.

1. **Claim, consequence, anchor, in that order.** The 2026-09-07 note asked for
   sections to open with the claim. Its sharper observation was that even the
   good openers stop at behaviour and never say what the behaviour costs or buys.
   PLUR's *"A draft is still retrievable and still searchable; it just never
   reaches the model's context"* is behaviour. The missing clause says what an
   operator or agent can now do that they could not before. Write it only when
   the code supports it, and leave it out when it does not. The anchor goes last, in parentheses, once.

2. **One altitude per paragraph.** Census, finding, mechanism and evidence are
   four altitudes. A paragraph can hold one of them, or a finding together with
   its evidence. The "jumps around in specificity" complaint was about mixing
   them.

3. **Prefer a scoped positive to a bare absence.** *"The status filter
   runs on the search path and not on the session-start context builder"*, with
   both anchors, is easier to read than *"nothing filters
   status on the context path"*, and it is also harder to get wrong. Negative
   existence claims are the atlas's dominant error class. At 3.7 uses of
   *nothing* per 1,000 words, reports read as lists of what is missing. The
   scoped form says what is there and where it stops. The absence claim still
   belongs in Recorded Searches.

4. **Delete the throat-clearing.** In *"It is worth naming that X"*, X is the
   sentence. The same goes for *worth noting*, *genuinely*, and *the part worth
   reading is*. If a statement needs an intensifier to feel significant, state
   its consequence instead (rule 1).

5. **One aside per sentence, and split at 40 words.** An em-dash aside that
   carries the point should be the sentence. An enumeration joined by semicolons
   becomes a list. A sentence that needs 60 words is two sentences with a joint
   the writer did not look for. This is the same method as the paragraph splits:
   split at a boundary that is already there.

6. **A cross-reference is a link or it is cut.** *Elsewhere*, *another system
   here* and *the line this atlas drew* each name a specific page. Link it with
   its slug, or remove the comparison. An agent reader cannot resolve a pronoun
   that points at the corpus, and a human reader will not try.

7. **History states the delta, not the mechanism.** A History entry is the pin,
   what moved, which marks changed and why, and a link to the section that now
   carries the evidence. Three or four sentences at most. `remove-meta-narrative`
   already stops History from leaking into the page. This is the reverse case:
   the page leaking into History, so that the same evidence is stated twice and
   the longer copy is the one nobody reads.

The 2026-09-07 note's rule on definitions still stands and is not repeated here:
define a term when its meaning is local to the system, and trust the reader
otherwise.

## Structure: five changes

In order of reach per unit of work.

### 1. The census moves to the metadata band

Licence, line count, commit range, author count, test count and the screen's
outcome become frontmatter fields, and the build renders them in the band that
already shows the pin and date. The first summary paragraph then has one job:
what the system is, what is notable, and what is weak. no_human shows that
shape. The licence stays on the page, just not in the prose. This means
changing the `add-memory-system` skill, which asks for the licence to be stated in
section 1. Existing reports convert when
they are next re-pinned. The frontmatter is filled from the existing sentence,
and the sentence is removed.

### 2. `description` gets a ceiling

Twenty-five words, one sentence, saying what the system is and the one thing
that distinguishes it. The mechanism list already exists in the capability
marks, which render beside it.

### 3. Pattern pages get *Read these first*

At the top of `## Seen in the atlas`: three to five systems, each with one line
on why it is the exemplar. Candidates are a clean implementation, the instructive
failure, and the smallest version that works. The full catalogue stays below as
reference. This is what `AGENTS.md` already assumes the section provides.
`check_protocol.py` or a sibling check can require that the block exists and has
five entries or fewer.

### 4. History entries get a shape

Rule 7, enforced as a word ceiling per entry (150) on new entries only. Entries
already written stay as they are. They record what was true when they were
written, and rewriting them is exactly the campaign the 2026-09-07 note warned
against.

### 5. The overview is split, not trimmed

The overview needs its own decision note before anything moves. This is the
proposal for that note. The overview becomes *In Short*, *Reading This Report*,
§3–§10 and History, roughly 40,000 words, all of it synthesis. §1 Taxonomy, §2
Comparative Matrix and §11 Appendix become their own pages, linked from the
places they are linked now. Anchors into those sections need redirects or
stubs, because reports and pattern pages cite them. §9 is already a pointer to
the verdicts page, which shows the pattern works. This is the largest change
and the one with the most inbound anchors. It goes last.

## What the build can hold

The atlas keeps a rule when a check holds it, and loses it when no check does.
The superlatives ceiling is the precedent: a count that can fall and cannot rise.

- **Paragraph ratchet per report, History included.** This is the 2026-09-07
  proposal with one change: History counts. A baseline file records, per
  report, the number of paragraphs over 150 words. A new report has a baseline
  of zero. The only edit the file accepts is lowering a number.
- **Sentence ratchet**, built the same way, for sentences over 60 words.
- **Tic ceiling**, built the same way as the superlatives ceiling, over
  `worth (naming|noting|reading|knowing)`, `genuinely`, and *elsewhere* with no
  link in the same sentence.
- **Census guard.** Once the band exists, the first summary paragraph may not
  contain a line count or a commit count.
- **Description ceiling**, 25 words, for new and re-pinned reports.

What no check can do is judge whether the lead is the right finding. The
comprehension test in the 2026-09-07 note (three questions, with agreement
scored separately) is the only instrument proposed for that. This note does not
know whether it was sent. If it was, its answers decide which of the seven rules
become mandatory. If it was not, it is the cheapest evidence available.

## What not to do

- **Do not rewrite the corpus in a campaign.** Ratchets stop regression, and
  the `reanalyze-memory-system` readability pass fixes the sections a re-pin
  already has open. A hundred reports shortened by an agent under a word budget
  get shorter without getting clearer, and the qualifications are the first
  thing to go. The 2026-09-07 note's *"nothing is deleted"* example shows how a
  brief lead can be wrong three ways.
- **Do not cut evidence to make room.** A split paragraph keeps every anchor.
  A moved census keeps every number.
- **Do not narrate the rewrite.** A report with a better lead says what the
  system is. It does not say it was improved.
- **Do not measure readability with a score.** Flesch and its relatives punish
  identifiers, and identifiers are the point. The counts above are proxies for
  specific complaints, and each is tied to one.

## Order

1. **Ratchets first**, all five in one commit, because they are the only item
   that stops the numbers above from getting worse while everything else is
   decided.
2. **The seven voice rules and the History shape**, added to
   `per-repo-report-format.md` and to the checklists in `add-memory-system` and
   `reanalyze-memory-system`, in the same commit as a worked rewrite of one
   report's summary and History. Vestige is a good candidate: both of its
   problems are on this page.
3. **Metadata band and description ceiling.** A build change, then conversion
   on re-pin.
4. ***Read these first*** on the three largest pattern pages.
5. **The overview split**, preceded by its own note.

## Method

Paragraphs: the body after the frontmatter, with fenced code removed, split on
blank lines. Blocks that start with `#`, `|`, `- `, `* `, `>`, `<` or a numbered
list marker are excluded. Words are whitespace tokens. Sentences are split on
`[.!?]` followed by whitespace and an uppercase letter, a backtick or `*`. This
over-splits on some abbreviations, so the sentence figures are a floor. The
section is the most recent `## ` heading. Section word counts on the overview,
verdicts and pattern pages are whitespace tokens between `## ` headings.
Phrase counts are case-insensitive `grep -o` over `content/systems/*.md`.
The 2026-09-17 column was measured by running the same script on
`git archive 77a926e68 content/systems`, so the two columns compare like with
like. Neither can be compared to the zero recorded in that commit's message.

```python
import re, glob
def paras(path):
    t = open(path).read()
    t = re.sub(r'^---\n.*?\n---\n', '', t, flags=re.S)
    t = re.sub(r'```.*?```', '', t, flags=re.S)
    sec = ''
    for blk in re.split(r'\n\s*\n', t):
        s = blk.strip()
        if s.startswith('## '):
            sec = s.split('\n')[0]; continue
        if not s or s.startswith(('#', '|', '- ', '* ', '>', '<')) or re.match(r'\d+\.', s):
            continue
        yield sec, len(s.split()), s
```

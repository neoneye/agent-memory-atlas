# Written to be checked, not yet to be read

**Status:** implemented on 2026-09-25 as the [plan](#implementation-plan) at
the end describes, in `76cd3ae62` (prose ratchet), `292651c83` (tic ceiling),
`daeab93d1` (header band and PLUR), `c589e320b` (report shape),
`ce3fd5417` (reading order in the format and skills) and `65994d5a3` (Read
these first). The overview split waits on its decision note. The voice rules
are provisional, because the comprehension test's outcome is not recorded. Measurements are from the tree at
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

**Descriptions are paragraphs.** The frontmatter `description` renders as the
deck under every report's title (`document-deck` in `templates/document.html`)
and goes into the page's JSON-LD. It has a median of 38 words, 266 are over 40, and the longest is
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
A new check can require the block on any catalogue over 3,000 words, which on
2026-09-25 meant four pages.

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

## Implementation plan

> **For agentic workers:** use `superpowers:subagent-driven-development` or
> `superpowers:executing-plans` to carry this out task by task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** stop the counts above from rising, then convert the corpus to
finding-first at the rate it is already re-read.

**Architecture:** four new check scripts with the same shape as
`list_superlatives.py`: a docstring that carries the reason, `--self-test`
fixtures, and a `--check` gate wired into `scripts/test_site.sh`. Two are
ratchets over everything already written. Two hold only prose written after a
cutover date, which a re-pin crosses by bumping `analyzed_at`. There is one
template change for the header band. There are text changes to the format
document and three skills. The overview split gets its own note and no code.

**Tech stack:** Python 3 standard library, Pandoc templates, Bash.
`npm run build` and `npm test`.

### Global constraints

- **One git actor, gated chains.** Run the build and test in the background as
  `npm run build && bash scripts/test_site.sh; echo "chain exit=$?"`. Read
  `chain exit=`, not the wrapper's status. Never pipe the test step.
- **Negative controls run on a scratch copy** (`mktemp -d`), never in the
  working tree.
- **Commit and push to main from HEAD:** `git push origin HEAD:main`. No
  `reset --hard`, no `checkout --` over uncommitted work.
- **Run `remove-meta-narrative`** over every edit under `content/` before
  committing it.
- **Corpus counts in `content/` prose are placeholders.** A ceiling constant
  in a script is a number, as `CORPUS_CLAIM_CEILING` already is.
- **Measure ceilings and baselines on the day they ship.** The figures in this
  note are from 2026-09-25 and will have moved.
- **A self-test is written first and proven able to fail.** Here the repo's
  existing form stands in for red-green TDD. The fixtures are the tests, and a
  deliberately broken constant on a scratch copy is what shows the check can go
  red.

### Before starting

Ask the maintainer one question: was the comprehension test from the 2026-09-07 note
sent to the no_human author, and did an answer come back? If it did, the
answer decides whether Task 5's rules go in as *mandatory* or *provisional*.
Nothing else depends on it.

### Dependencies

Tasks 1, 2 and 6 are independent. Task 3 must come before Task 4, because
the shape check requires the fields the band renders. Task 5 comes after
Task 3, because its text names those fields. Task 7 comes last.

### File map

| File | Task | Responsibility |
|---|---|---|
| `scripts/list_long_prose.py` (new) | 1 | per-report ratchet on paragraphs over 150 words and sentences over 60 |
| `scripts/prose_baseline.json` (new, generated) | 1 | per-report baseline; only `--lower` edits it |
| `scripts/list_voice_tics.py` (new) | 2 | ceiling on throat-clearing phrases and unlinked *elsewhere* |
| `templates/document.html` | 3 | header band: licence, size, activity, tests |
| `.agents/skills/add-memory-system/scripts/scaffold_report.py` | 3 | new reports get the four fields |
| `scripts/licence_drift.py` | 3 | reads `licence:` before falling back to prose |
| `content/systems/plur.md`, `content/overview.md` | 3 | worked example, and one known-limitations entry |
| `scripts/check_report_shape.py` (new) | 4 | description, band fields, census-free summary and History entry length, from a cutover |
| `scripts/test_site.sh` | 1, 2, 4, 6 | wiring |
| `content/methodology/per-repo-report-format.md` | 5 | the voice rules and the summary and History shapes |
| `.agents/skills/add-memory-system/SKILL.md`, `.agents/skills/reanalyze-memory-system/SKILL.md` | 5, 6 | checklists and the readability pass |
| `scripts/check_pattern_exemplars.py` (new) | 6 | *Read these first* above any catalogue over 3,000 words |
| four pattern pages, `AGENTS.md`, `.agents/skills/use-the-atlas/SKILL.md` | 6 | the exemplar lists, and pointers to them |
| `notes/<date>-splitting-the-overview.md` (new) | 7 | decision note with an inbound-anchor inventory |

All four scripts below were run against the tree at `879c679e6` on 2026-09-25
while this plan was being written. Every self-test passed, and each negative
control failed the way its step says it should.

---

### Task 1: Per-report prose ratchet

**Files:** create `scripts/list_long_prose.py` and
`scripts/prose_baseline.json`, and modify `scripts/test_site.sh`.

**Interfaces:** produces `units(text) -> Iterator[str]` and
`counts(text) -> (long_paragraphs, long_sentences)`. Nothing later imports
them. The docstring defines the counting method, which replaces the one in
this note's [Method](#method) (list items now count).

- [x] **Step 1: Create the script.**

```python
#!/usr/bin/env python3
"""Hold each report's long paragraphs and long sentences to a ratchet.

The 2026-09-07 reader feedback was that a report read as a wall of text. The
2026-09-17 split campaign cleared the worst paragraphs by hand, and with nothing
watching they came back: on 2026-09-25 the History sections alone held 864
paragraphs over 120 words, against 475 eight days earlier, because every re-pin
appends one and writes it as a single block.

**Per report, not a corpus total.** A total lets a new 300-word paragraph in
one report pass because someone split two old ones in another. Each report has
its own baseline in `prose_baseline.json`; a report with no entry — every new
report — has a baseline of zero. `--lower` is the only way the file changes,
and it can only lower.

**History counts.** It is where the paragraphs came back.

What a unit is: the Markdown body after the frontmatter, fenced code removed,
split on blank lines. Blocks opening with `#`, `|`, `>` or `<` are skipped. A
block of list items is split into one unit per item, because a bullet can carry
the same wall as a paragraph. Words are whitespace tokens. Sentences split on
`[.!?]` followed by whitespace and a capital, a backtick or `*`, which
over-splits on abbreviations, so the sentence count is a floor.

**The hole this does not close:** within a report that has a baseline, one long
paragraph can replace another at the same count. Nothing here says whether a
paragraph leads with its finding.

Usage: list_long_prose.py <project-dir>            report: totals and the ten longest
       list_long_prose.py --check <project-dir>    gate
       list_long_prose.py --lower <project-dir>    rewrite baseline, never upward
       list_long_prose.py --init <project-dir>     write baseline when none exists
       list_long_prose.py --self-test
"""
import json
import re
import sys
from pathlib import Path

PARAGRAPH_LIMIT = 150
SENTENCE_LIMIT = 60
BASELINE = Path(__file__).resolve().parent / "prose_baseline.json"

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
FENCE = re.compile(r"^```.*?^```[ \t]*$", re.S | re.M)
LIST_ITEM = re.compile(r"^(?:[-*+]|\d+\.)\s+")
SKIP = ("#", "|", ">", "<")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z*`])")


def units(text: str):
    """Every prose paragraph and list item in a report body, one string each."""
    body = FENCE.sub("", FRONTMATTER.sub("", text))
    for block in re.split(r"\n[ \t]*\n", body):
        lines = block.strip().split("\n")
        if not lines[0] or lines[0].lstrip().startswith(SKIP):
            continue
        item: list[str] = []
        for line in lines:
            stripped = line.strip()
            if LIST_ITEM.match(stripped):
                if item:
                    yield " ".join(item)
                item = [LIST_ITEM.sub("", stripped, count=1)]
            else:
                item.append(stripped)
        if item:
            yield " ".join(item)


def counts(text: str) -> tuple[int, int]:
    paragraphs = sentences = 0
    for unit in units(text):
        if len(unit.split()) > PARAGRAPH_LIMIT:
            paragraphs += 1
        sentences += sum(
            1 for s in SENTENCE_END.split(unit) if len(s.split()) > SENTENCE_LIMIT
        )
    return paragraphs, sentences


def measure(root: str) -> dict[str, tuple[int, int]]:
    systems = Path(root) / "content" / "systems"
    return {p.stem: counts(p.read_text(encoding="utf-8"))
            for p in sorted(systems.glob("*.md"))}


def load_baseline() -> dict[str, tuple[int, int]]:
    if not BASELINE.exists():
        return {}
    return {k: (v[0], v[1]) for k, v in json.loads(BASELINE.read_text()).items()}


def write_baseline(rows: dict[str, tuple[int, int]]) -> None:
    # One report per line, so a --lower shows up in a diff as the lines it moved.
    lines = [f"  {json.dumps(k)}: [{v[0]}, {v[1]}]"
             for k, v in sorted(rows.items()) if v != (0, 0)]
    BASELINE.write_text("{\n" + ",\n".join(lines) + "\n}\n")


def regressions(now, base) -> list[str]:
    out = []
    for slug, (p, s) in sorted(now.items()):
        bp, bs = base.get(slug, (0, 0))
        if p > bp:
            out.append(f"{slug}: {p} paragraphs over {PARAGRAPH_LIMIT} words, baseline {bp}")
        if s > bs:
            out.append(f"{slug}: {s} sentences over {SENTENCE_LIMIT} words, baseline {bs}")
    return out


def lowered(now, base) -> dict[str, tuple[int, int]]:
    return {slug: (min(now[slug][0], b[0]), min(now[slug][1], b[1]))
            for slug, b in base.items() if slug in now}


def self_test() -> int:
    words = lambda n: " ".join(["word"] * n)
    cases = [
        ("a 151-word paragraph counts", f"{words(151)}.\n", (1, 1)),
        ("a 151-word code block does not", f"```\n{words(151)}\n```\n", (0, 0)),
        ("a table row does not", f"| {words(151)} |\n", (0, 0)),
        ("two 80-word bullets are two units",
         f"- {words(80)}.\n- {words(80)}.\n", (0, 2)),
        ("a paragraph under History counts",
         f"## History\n\n**2026-09-25** {words(151)}.\n", (1, 1)),
        ("three 55-word sentences are short",
         f"{words(55)}. A {words(54)}. A {words(54)}.\n", (1, 0)),
    ]
    for name, text, expected in cases:
        got = counts(text)
        if got != expected:
            print(f"self-test failed: {name}: got {got}, expected {expected}", file=sys.stderr)
            return 1
    if not regressions({"new": (1, 0)}, {}):
        print("self-test failed: a new report with a long paragraph passed", file=sys.stderr)
        return 1
    if regressions({"old": (3, 5)}, {"old": (3, 5)}):
        print("self-test failed: an unchanged report was flagged", file=sys.stderr)
        return 1
    if lowered({"old": (4, 1)}, {"old": (3, 5)}) != {"old": (3, 1)}:
        print("self-test failed: --lower raised an entry", file=sys.stderr)
        return 1
    print("self-test: 9 controls passed")
    return 0


def report(root: str) -> int:
    rows = []
    for path in sorted((Path(root) / "content" / "systems").glob("*.md")):
        for unit in units(path.read_text(encoding="utf-8")):
            rows.append((len(unit.split()), path.stem, unit[:70]))
    now = measure(root)
    print(f"{sum(p for p, _ in now.values())} paragraphs over {PARAGRAPH_LIMIT} words, "
          f"{sum(s for _, s in now.values())} sentences over {SENTENCE_LIMIT}, "
          f"in {sum(1 for v in now.values() if v != (0, 0))} reports\n")
    for n, slug, head in sorted(rows, reverse=True)[:10]:
        print(f"  {n:4}  {slug:32} {head}")
    return 0


def main(args: list[str]) -> int:
    root = next((a for a in args if not a.startswith("--")), ".")
    if "--self-test" in args:
        return self_test()
    now = measure(root)
    if "--init" in args:
        if BASELINE.exists():
            print(f"{BASELINE.name} exists; use --lower", file=sys.stderr)
            return 1
        write_baseline(now)
        return 0
    if "--lower" in args:
        write_baseline(lowered(now, load_baseline()))
        return 0
    if "--check" in args:
        problems = regressions(now, load_baseline())
        if problems:
            print("Long prose rose above its baseline. Split at a boundary the text "
                  "already has; do not edit the baseline upward.", file=sys.stderr)
            for p in problems:
                print(f"  {p}", file=sys.stderr)
            return 1
        print(f"long prose at or under baseline in {len(now)} reports")
        return 0
    return report(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [x] **Step 2: Run the self-test.**
  `python3 scripts/list_long_prose.py --self-test` should print
  `self-test: 9 controls passed`.

- [x] **Step 3: Prove the self-test can fail.**

```bash
T=$(mktemp -d) && sed 's/^PARAGRAPH_LIMIT = 150/PARAGRAPH_LIMIT = 1500/' scripts/list_long_prose.py > $T/p.py && python3 $T/p.py --self-test; echo "exit=$?"; rm -rf $T
```

  Expected: `self-test failed: a 151-word paragraph counts: got (0, 1),
  expected (1, 1)` and `exit=1`.

- [x] **Step 4: Measure, then write the baseline.**
  `python3 scripts/list_long_prose.py .` prints the totals and the ten longest
  units. On 2026-09-25 that was `920 paragraphs over 150 words, 1799 sentences
  over 60, in 550 reports`, and the longest was a 626-word History entry in
  memsem. Then run `python3 scripts/list_long_prose.py --init .` and
  `python3 scripts/list_long_prose.py --check .`. Expected: `long prose at or
  under baseline in <N> reports`.

- [x] **Step 5: Negative control on a scratch copy of the corpus.**

```bash
T=$(mktemp -d) && mkdir -p $T/content && cp -R content/systems $T/content/ && python3 -c "print('\n\n' + ' '.join(['word'] * 200) + '.')" >> $T/content/systems/plur.md && python3 scripts/list_long_prose.py --check $T; echo "exit=$?"; rm -rf $T
```

  Expected: `plur: <n+1> paragraphs over 150 words, baseline <n>` and
  `exit=1`. The leading blank lines matter. Without them the words join the
  last paragraph, and only the sentence count moves.

- [x] **Step 6: Wire it in.** In `scripts/test_site.sh`, directly after the
  `list_inert_recorded_commands.py --check` block:

```bash
# The 2026-09-07 reader feedback was a wall of text. A hand-split campaign
# cleared the worst of it on 2026-09-17 and nothing held it: eight days later
# the History sections alone had gone from 475 paragraphs over 120 words to 864.
# Per-report ratchet, History included; a new report's baseline is zero.
if ! python3 "$project_dir/scripts/list_long_prose.py" --self-test; then
  echo "list_long_prose.py cannot demonstrate that its counter still works." >&2
  exit 1
fi
if ! python3 "$project_dir/scripts/list_long_prose.py" --check "$project_dir"; then
  exit 1
fi
```

- [x] **Step 7: Build and test** with the gated chain. Expected:
  `chain exit=0`.

- [x] **Step 8: Commit and push.**

```bash
git add scripts/list_long_prose.py scripts/prose_baseline.json scripts/test_site.sh && git commit -m "Hold each report's long paragraphs and sentences to a ratchet, History included" && git push origin HEAD:main
```

---

### Task 2: Throat-clearing and unlinked-reference ceiling

**Files:** create `scripts/list_voice_tics.py` and modify
`scripts/test_site.sh`.

**Interfaces:** consumes `_quoted_spans(text) -> list[tuple[int, int]]` from
`scripts/list_superlatives.py`, which is importable because Python puts the
script's own directory first on `sys.path`. None of its imports reach
`scripts/queue.py`, the file that shadows the stdlib module in
`licence_drift.py`.

- [x] **Step 1: Create the script.**

```python
#!/usr/bin/env python3
"""Count phrases that stand in for a point, and unlinked references to the corpus.

Two kinds, one ratchet.

**Throat-clearing.** In "it is worth naming that X", X is the sentence. *worth
naming*, *worth noting*, *worth reading*, *worth knowing* and *genuinely* carried
roughly 980 uses across the reports on 2026-09-25. Each announces significance
instead of stating the consequence that would carry it.

**A reference the reader cannot follow.** "The same ruling this atlas applied to
a declared approve tool elsewhere" names a specific page and then takes the name
out. On 2026-09-25, 280 of 281 uses of *elsewhere* in the reports had no link
within 60 characters. Counted here only when the sentence holding it has no
Markdown link.

A quotation is the subject's words and is not counted, for the reason
`list_superlatives.py` gives: the edit a ratchet invites for a false positive is
to alter the quotation, which is worse than the miscount.

Same shape as the superlatives ceiling: the total may fall and may not rise.
The hole it does not close: one phrase can be removed and another added.

Usage: list_voice_tics.py <project-dir>
       list_voice_tics.py --check <project-dir>
       list_voice_tics.py --self-test
"""
import re
import sys
from pathlib import Path

from list_superlatives import _quoted_spans

TIC = re.compile(r"\bworth (?:naming|noting|reading|knowing)\b|\bgenuinely\b", re.I)
ELSEWHERE = re.compile(r"\belsewhere\b", re.I)
LINK = re.compile(r"\]\(")
SENTENCE = re.compile(r"[^.!?\n]*(?:[.!?]|$)")

#: Set to 1484 on 2026-09-25, across all of content/, and lowered as phrases
#: are cut. Never raise it to admit a new one.
TIC_CEILING = 1481


def hits(text: str) -> list[tuple[int, str]]:
    spans = _quoted_spans(text)
    quoted = lambda i: any(lo <= i < hi for lo, hi in spans)
    out = [(m.start(), m.group(0)) for m in TIC.finditer(text) if not quoted(m.start())]
    flat = text.replace("\n", " ")
    for s in SENTENCE.finditer(flat):
        if LINK.search(s.group(0)):
            continue
        for m in ELSEWHERE.finditer(s.group(0)):
            at = s.start() + m.start()
            if not quoted(at):
                out.append((at, "elsewhere (unlinked)"))
    return out


def collect(root: str) -> list[tuple[str, str]]:
    content = Path(root) / "content"
    rows = []
    for path in sorted(content.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for at, phrase in hits(text):
            rows.append((f"{path.relative_to(content)}:{text.count(chr(10), 0, at) + 1}", phrase))
    return rows


def self_test() -> int:
    cases = [
        ("a tic counts", "It is worth noting that the log is sealed.", 1),
        ("genuinely counts", "The split is genuinely useful.", 1),
        ("a quoted tic does not", 'The README says "worth reading twice".', 0),
        ("unlinked elsewhere counts", "The same ruling applied elsewhere.", 1),
        ("linked elsewhere does not",
         "The same ruling applied elsewhere, in [Vestige](../vestige/).", 0),
        ("a link in the next sentence does not excuse",
         "It was ruled elsewhere. See [Vestige](../vestige/).", 1),
    ]
    for name, text, expected in cases:
        if len(hits(text)) != expected:
            print(f"self-test failed: {name}: got {len(hits(text))}", file=sys.stderr)
            return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main(args: list[str]) -> int:
    root = next((a for a in args if not a.startswith("--")), ".")
    if "--self-test" in args:
        return self_test()
    rows = collect(root)
    if "--check" in args:
        if len(rows) > TIC_CEILING:
            print(f"voice tics rose to {len(rows)} > {TIC_CEILING}. State the "
                  "consequence instead of the intensifier, and link or cut "
                  "'elsewhere'; do not raise the ceiling.", file=sys.stderr)
            return 1
        print(f"{len(rows)} voice tics (ceiling {TIC_CEILING}).")
        return 0
    print(f"{len(rows)} voice tics\n")
    for location, phrase in rows:
        print(f"  {location:<44} {phrase}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [x] **Step 2: Run the self-test.** Expected: `self-test: 6 controls
  passed`.

- [x] **Step 3: Prove it can fail.** Put a copy in a scratch directory with
  `list_superlatives.py` beside it, delete `if LINK.search(s.group(0)):
  continue`, and run `--self-test`. Expected: `self-test failed: linked
  elsewhere does not: got 1`.

- [x] **Step 4: Set the ceiling from today's count.**

```bash
N=$(python3 scripts/list_voice_tics.py . | head -1 | cut -d' ' -f1) && sed -i '' "s/^TIC_CEILING = .*/TIC_CEILING = $N/" scripts/list_voice_tics.py && python3 scripts/list_voice_tics.py --check .
```

  On 2026-09-25 the count across all of `content/` was 1,484: 414
  *genuinely*, 334 unlinked *elsewhere*, 310 *worth naming*, 244 *worth
  reading*, 98 *worth noting*, 84 *worth knowing*. Expected: `<N> voice tics
  (ceiling <N>).`

- [x] **Step 5: Wire it in** after Task 1's block:

```bash
# Phrases that announce significance instead of stating the consequence, and
# "elsewhere" with no link: on 2026-09-25, 280 of 281 in the reports had none.
# Same ratchet as the superlatives: the total may fall and may not rise.
if ! python3 "$project_dir/scripts/list_voice_tics.py" --self-test; then
  echo "list_voice_tics.py cannot demonstrate that its matcher still works." >&2
  exit 1
fi
if ! python3 "$project_dir/scripts/list_voice_tics.py" --check "$project_dir"; then
  exit 1
fi
```

- [x] **Step 6: Build and test, then commit and push.** The message is
  "Ceiling on throat-clearing phrases and unlinked references to the corpus".

---

### Task 3: The header band, with PLUR as the worked example

**Files:** modify `templates/document.html`,
`.agents/skills/add-memory-system/scripts/scaffold_report.py`,
`scripts/licence_drift.py`, `content/systems/plur.md` and
`content/overview.md`.

**Interfaces:** produces four optional frontmatter keys, each a quoted
string: `licence` (an SPDX identifier from `licence_drift.SPDX`, or an
expression such as `"MIT OR Apache-2.0"`), `size`, `activity` and `tests`.
Task 4 requires the first three on any report read after the cutover.

- [x] **Step 1: Template.** In `templates/document.html`, insert this between
  the `$endif$` that closes the source/revision `document-meta` and
  `$if(stance)$`. The existing `.document-meta` rules in `assets/main.css`
  already style a second row; the stance pill uses one.

```html
          $if(licence)$
          <div class="document-meta">
            <div class="meta-pill"><span>Licence</span><strong>$licence$</strong></div>
            $if(size)$<div class="meta-pill"><span>Size</span><strong>$size$</strong></div>$endif$
            $if(activity)$<div class="meta-pill"><span>Activity</span><strong>$activity$</strong></div>$endif$
            $if(tests)$<div class="meta-pill"><span>Tests</span><strong>$tests$</strong></div>$endif$
          </div>
          $endif$
```

- [x] **Step 2: Scaffold.** In `render_report`, after the `analyzed_at` line:

```python
        # Rendered in the header band, so the summary can open with the finding.
        # check_report_shape.py requires the first three on any report read
        # after its cutover.
        'licence: ""\n'
        'size: ""\n'
        'activity: ""\n'
        'tests: ""\n'
```

- [x] **Step 3: `licence_drift.py` reads the field first.** Add beside
  `SPDX`:

```python
#: The header-band field. Preferred over the prose when it holds one SPDX id; a
#: compound expression falls back to the sentence in section 1, which is where
#: a restrictive or dual licence is still stated.
FRONTMATTER_LICENCE = re.compile(r'^licence:\s*"?([^"\n]+?)"?\s*$', re.M)
```

  In `reports()`, replace `claim = stated(body)` with:

```python
        field = FRONTMATTER_LICENCE.search(text)
        if field and SPDX.fullmatch(field.group(1)):
            claim = ALIASES.get(field.group(1), field.group(1))
        else:
            claim = stated(body)
```

- [x] **Step 4: Convert PLUR.** In `content/systems/plur.md`:
  - Add to the frontmatter, after `analyzed_at`:

```yaml
licence: "Apache-2.0"
size: "66,632 lines of TypeScript in ten packages"
activity: "927 commits by thirteen authors, 19 March – 8 September 2026"
tests: "4,893 cases in 82,289 lines"
```

  - Replace `description` with the following (22 words): `"A local-first
    shared memory for coding agents: plain-text engrams in one YAML file,
    where a draft stays retrievable but is never injected."`
  - Replace the first summary paragraph, which runs from *"PLUR is a
    local-first shared memory"* to *"a cache rather than truth."*, with:

```markdown
PLUR is a local-first shared memory for coding agents: the agent writes
plain-text engrams into `~/.plur/engrams.yaml`, which is the source of truth,
and SQLite, PGLite or Postgres attach only as an index the code describes as a
cache rather than truth. What sets it apart is a commitment level on every
engram, where `draft` keeps a lesson retrievable and searchable but out of the
model's context. Its weak points come after that: nothing in this tree can
approve a draft, the direct correction path overwrites without a record, and a
retired engram is deliberately invisible to the dedup that would stop it coming
back.
```

  - The removed screen sentence is already in the 2026-09-08 History entry.
    If *"nothing was installed or run"* is not in that entry, put it as the
    first sentence of section 10, where a statement about test runs belongs.
    Do not edit the old entry.
  - **Fix a stale count found while drafting this plan.** The summary says
    *"Six of seven marks"* and then *"The other five."*, but `capabilities:`
    has held five since `human_review` was withdrawn on 2026-09-19. Change
    them to *"Five of seven marks"* and *"The other four."*. Then add a bullet
    at the top of `### Known Limitations` in `content/overview.md`, in that
    list's form: a re-pin withdrew a mark in the frontmatter and in section 9,
    and left the summary's count, which no check compares with
    `capabilities:`.

- [x] **Step 5: Verify.**

```bash
python3 scripts/licence_drift.py --slug plur
```

  Expected on stderr: `1 stated licences: 1 agree, 0 differ, 0 with no licence
  file found.` This makes one network fetch. Then run the gated chain and
  `grep -c 'meta-pill"><span>Licence' docs/systems/plur/index.html`, which
  should print `1`. Open `docs/systems/plur/index.html` through
  `npm run serve` in the browser pane at desktop width and at 375px. The band
  must wrap without horizontal scroll.

- [x] **Step 6: `remove-meta-narrative` over both content files, then commit
  and push.** The message is "Header band for licence, size, activity and
  tests; PLUR converted and its summary's mark count corrected".

---

### Task 4: Hold new and re-pinned reports to the shape

**Files:** create `scripts/check_report_shape.py` and modify
`scripts/test_site.sh`.

**Interfaces:** consumes the band fields from Task 3. `CUTOVER` is the date
this task lands, written as a literal.

- [x] **Step 1: Create the script.** Set `CUTOVER` to the commit date.

```python
#!/usr/bin/env python3
"""Hold new and re-pinned reports to the reading order, from the cutover on.

Four rules, from notes/2026-09-25-written-to-be-checked-not-yet-to-be-read.md.
Each applies only where the prose is being written anyway: to a report whose
`analyzed_at` is on or after CUTOVER, and to History entries dated on or after
it. A re-pin bumps `analyzed_at`, so the corpus converts at the rate it is
re-read, and nothing is rewritten in a campaign.

1. **`description` is one line.** It renders as the deck under the title, on
   the page and in link previews. At most DESCRIPTION_LIMIT words.
2. **The census lives in the header band.** `licence`, `size` and `activity`
   are non-empty in the frontmatter; `tests` is optional.
3. **The summary opens with the finding, not the census.** The first
   paragraph under `## 1. Executive Summary` may not carry a line, commit or
   author count; those live in the `size` and `activity` frontmatter fields,
   which render in the header band.
4. **A History entry states the delta.** At most HISTORY_LIMIT words from its
   `**YYYY-MM-DD**` to the next entry. The evidence goes in the section it
   changed, and the entry links there.

What this cannot check: whether the first paragraph is the right finding.

Usage: check_report_shape.py <project-dir>
       check_report_shape.py --self-test
"""
import re
import sys
from pathlib import Path

#: The day this check shipped. Reports and History entries dated before it are
#: not held; they convert when a reading next opens them.
CUTOVER = "2026-09-25"
DESCRIPTION_LIMIT = 25
HISTORY_LIMIT = 150
REQUIRED_FACTS = ("licence", "size", "activity")

ANALYZED_AT = re.compile(r"^analyzed_at:\s*\"?(\d{4}-\d{2}-\d{2})", re.M)
DESCRIPTION = re.compile(r"^description:\s*(.+)$", re.M)
SUMMARY = re.compile(r"^## 1\. Executive Summary\s*\n+(.+?)(?:\n\s*\n|\Z)", re.M | re.S)
NUMBER_WORD = r"(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|twenty)"
CENSUS = re.compile(
    rf"\b(?:\d[\d,.]*\s*k?|{NUMBER_WORD})\s+(?:lines|commits|authors|contributors)\b", re.I)
HISTORY = re.compile(r"^## History\s*$", re.M)
ENTRY = re.compile(r"^\*\*(\d{4}-\d{2}-\d{2})\*\*", re.M)


def history_entries(text: str) -> list[tuple[str, str]]:
    heading = HISTORY.search(text)
    if not heading:
        return []
    tail = text[heading.end():]
    tail = tail[:m.start()] if (m := re.search(r"^## ", tail, re.M)) else tail
    starts = list(ENTRY.finditer(tail))
    return [(m.group(1), tail[m.start():(starts[i + 1].start() if i + 1 < len(starts) else len(tail))])
            for i, m in enumerate(starts)]


def problems(name: str, text: str) -> list[str]:
    out = []
    for date, entry in history_entries(text):
        if date >= CUTOVER and len(entry.split()) > HISTORY_LIMIT:
            out.append(f"{name}: History entry {date} is {len(entry.split())} words "
                       f"(limit {HISTORY_LIMIT}); move the evidence into the section it changed")
    analyzed = ANALYZED_AT.search(text)
    if not analyzed or analyzed.group(1) < CUTOVER:
        return out
    for key in REQUIRED_FACTS:
        if not re.search(rf'^{key}:\s*"?[^"\s]', text, re.M):
            out.append(f"{name}: `{key}:` is empty or missing; the header band renders it")
    if (d := DESCRIPTION.search(text)):
        words = len(d.group(1).strip().strip('"').split())
        if words > DESCRIPTION_LIMIT:
            out.append(f"{name}: description is {words} words (limit {DESCRIPTION_LIMIT})")
    if (s := SUMMARY.search(text)) and (c := CENSUS.search(s.group(1))):
        out.append(f"{name}: summary opens with a census ('{c.group(0)}'); "
                   "move it to the size/activity frontmatter fields")
    return out


def self_test() -> int:
    long_desc = " ".join(["word"] * 26)
    facts = 'licence: "MIT"\nsize: "900 lines of Go"\nactivity: "12 commits by one author"\n'
    head = lambda date, desc="A store.": f"---\ndescription: \"{desc}\"\nanalyzed_at: {date}\n{facts}---\n"
    cases = [
        ("a new long description fails", head(CUTOVER, long_desc), 1),
        ("a new report with an empty fact fails",
         head(CUTOVER).replace('size: "900 lines of Go"', 'size: ""'), 1),
        ("an old long description passes", head("2026-01-01", long_desc), 0),
        ("a census in a new summary fails",
         head(CUTOVER) + "## 1. Executive Summary\n\nX is a store — 927 commits by thirteen authors.\n", 1),
        ("a census in the second paragraph passes",
         head(CUTOVER) + "## 1. Executive Summary\n\nX is a store.\n\nIt has 66,632 lines.\n", 0),
        ("a long new History entry fails",
         head("2026-01-01") + f"## History\n\n**{CUTOVER}** — " + " ".join(["w"] * 151) + "\n", 1),
        ("a long old History entry passes",
         head("2026-01-01") + "## History\n\n**2026-09-11** — " + " ".join(["w"] * 400) + "\n", 0),
        ("an entry ends at the next entry",
         head("2026-01-01") + f"## History\n\n**{CUTOVER}** — short.\n\n**2026-09-11** — "
         + " ".join(["w"] * 400) + "\n", 0),
    ]
    for name, text, expected in cases:
        got = len(problems("fixture", text))
        if got != expected:
            print(f"self-test failed: {name}: got {got} problems, expected {expected}", file=sys.stderr)
            return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main(root: str) -> int:
    found = []
    for path in sorted((Path(root) / "content" / "systems").glob("*.md")):
        found += problems(path.name, path.read_text(encoding="utf-8"))
    if found:
        print("Reports read or re-read since the cutover are out of reading order:", file=sys.stderr)
        for p in found:
            print(f"  {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--self-test" in args:
        sys.exit(self_test())
    sys.exit(main(next((a for a in args if not a.startswith("--")), ".")))
```

- [x] **Step 2: Self-test.** Expected: `self-test: 8 controls passed`. Prove
  it can fail by setting `HISTORY_LIMIT = 1500` on a scratch copy. Expected:
  `self-test failed: a long new History entry fails: got 0 problems,
  expected 1`.

- [x] **Step 3: Positive and negative control on a scratch copy.** Bump two
  reports' `analyzed_at` to `CUTOVER`. PLUR has been converted; vestige has
  not.

```bash
T=$(mktemp -d) && mkdir -p $T/content && cp -R content/systems $T/content/ && C=$(sed -n 's/^CUTOVER = "\(.*\)".*/\1/p' scripts/check_report_shape.py) && for s in plur vestige; do sed -i '' "s/^analyzed_at: .*/analyzed_at: $C/" $T/content/systems/$s.md; done && python3 scripts/check_report_shape.py $T; echo "exit=$?"; rm -rf $T
```

  Expected: no line for `plur.md`. The lines for `vestige.md` should name the
  missing `licence`, `size` and `activity`, the description's length, and the
  census if its summary opens with one. `exit=1`. If PLUR appears, Task 3
  left something unconverted. With the cutover set in the past, the whole
  corpus shows the pool re-pins will convert. On 2026-09-25 that was 564
  descriptions, 424 summaries and 748 History entries.

- [x] **Step 4: Wire it in** after Task 2's block:

```bash
# Reports read or re-read from the cutover on open with the finding: the census
# is in the header band, the description is one line, and a History entry states
# the delta. Older prose is not held, so the corpus converts as it is re-read.
if ! python3 "$project_dir/scripts/check_report_shape.py" --self-test; then
  echo "check_report_shape.py cannot demonstrate that it still fails." >&2
  exit 1
fi
if ! python3 "$project_dir/scripts/check_report_shape.py" "$project_dir"; then
  exit 1
fi
```

- [x] **Step 5: Build and test, then commit and push.** The message is
  "From the cutover on, a report opens with the finding and its History entry
  states the delta".

---

### Task 5: The rules, in the format document and the skills

**Files:** modify `content/methodology/per-repo-report-format.md`,
`.agents/skills/add-memory-system/SKILL.md` and
`.agents/skills/reanalyze-memory-system/SKILL.md`.

- [x] **Step 1: Format document, new section** after *Dates are absolute,
  never relative*. Write it as *provisional* unless the question in *Before
  starting* came back answered.

```markdown
## Reading order

The evidence rules above make a claim checkable. These make it findable. The
reader is the same expert; nothing here is a gloss.

- **Claim, consequence, anchor.** Open an analytical section with what the
  system does, then what that costs or buys the operator, then the file and
  line, in parentheses, once, at the end of the sentence. A consequence is
  written only where the code supports it.
- **One altitude per paragraph.** Census, finding, mechanism and evidence are
  different altitudes; a paragraph holds one, or a finding with its evidence.
- **A scoped positive over a bare absence.** "The filter runs on the search
  path and not on the context builder", with both anchors, reads better and
  is harder to get wrong than "nothing filters the context path". The search
  behind the absence still goes in Recorded Searches.
- **No intensifiers.** *Worth naming*, *worth noting*, *genuinely*: the
  sentence after the phrase is the point. If it needs help, state its
  consequence. `list_voice_tics.py` holds the count.
- **One aside per sentence; split at 40 words.** An aside that carries the
  point is the sentence. An enumeration joined by semicolons is a list.
- **A cross-reference is a link or it is cut.** *Elsewhere*, *another system
  here* and *the line this atlas drew* each name a page. Name it and link it.
- **Define a term when its meaning is local to the system**, and trust the
  reader otherwise.
```

- [x] **Step 2: Format document, Executive Summary.** Replace *"What is
  genuinely interesting technically."* with *"What is notable technically,
  and what it buys."* Add below the bullet list:

```markdown
The first paragraph is three things a reader can stop after: what the system
is, what is notable, and what is weak. Licence, size, commit activity and test
counts go in the `licence`, `size`, `activity` and `tests` frontmatter fields,
which render in the header band; a licence that restricts use, or a dual one,
is also stated in this section, because it changes what a reader may do.
`description` is one sentence of at most 25 words.
```

- [x] **Step 3: Format document, History.** After the example entry, add:

```markdown
An entry is the pin, what moved, which marks changed and why, and a link to
the section that now carries the evidence — at most 150 words. The evidence is
stated once, in the body; an entry that re-describes the mechanism is the body
leaking into the log. `check_report_shape.py` holds entries dated on or after
its cutover.
```

- [x] **Step 4: `add-memory-system`.** In the paragraph that says a licence is
  *"stated in section 1"*, change it to *"stated in the `licence` field, and
  in section 1 when it restricts use"*. Add to the *Before integration,
  verify* list:

```markdown
- The first summary paragraph says what the system is, what is notable and
  what is weak, with no line, commit or author count; those are in `size` and
  `activity`.
- `description` is one sentence of at most 25 words.
- Every *elsewhere*, *another system* or comparison to a named report carries
  a link.
```

- [x] **Step 5: `reanalyze-memory-system`.** After the four outcomes in
  *Decide the shape, then write*, add:

```markdown
**Readability pass on what you opened.** A re-pin bumps `analyzed_at`, which
puts the report under `check_report_shape.py`: fill `licence`, `size` and
`activity` from the summary's census and delete the census, shorten
`description` to one sentence, and write the new History entry as the delta.
In the sections you edited, apply *Reading order* from the format document.
Leave untouched sections and older History entries alone: they are converted
when a reading opens them, not by a campaign.
```

- [x] **Step 6: `remove-meta-narrative`, then the gated chain, then commit and
  push.** The message is "Reading order: the voice rules, and the summary and
  History shapes, in the format and the skills".

---

### Task 6: *Read these first* on long pattern catalogues

**Files:** create `scripts/check_pattern_exemplars.py`, and modify
`scripts/test_site.sh`, `content/patterns/rejected-value-tombstone.md`,
`content/patterns/scope-as-a-first-class-key.md`,
`content/patterns/trust-state-machine.md`,
`content/patterns/append-only-memory-audit.md`, `AGENTS.md` (line 33),
`.agents/skills/use-the-atlas/SKILL.md` (line 50) and
`.agents/skills/add-memory-system/SKILL.md` (line 312).

- [x] **Step 1: Create the script.**

```python
#!/usr/bin/env python3
"""Require a short *Read these first* list above a long pattern catalogue.

`AGENTS.md` sends a builder to a pattern page's `## Seen in the atlas` to find
the systems worth reading. On the largest pages that section is most of the
page — 9,778 of 11,342 words on the rejected-value tombstone on 2026-09-25 —
and a catalogue that long is no longer a pointer to anything.

Rule: a catalogue over CATALOGUE_LIMIT words opens with `### Read these first`,
holding 1 to MAX_EXEMPLARS bullets, each linking a system report, and nothing
else: a heading closes it, or the catalogue below renders as part of the short
list and the entry point is gone again. The block is
validated wherever it appears, whatever the catalogue's length. Choosing the
exemplars is a judgement this cannot check; it checks that the list exists,
sits first, stays short and points at reports.

Usage: check_pattern_exemplars.py <project-dir>
       check_pattern_exemplars.py --self-test
"""
import re
import sys
from pathlib import Path

CATALOGUE_LIMIT = 3000
MAX_EXEMPLARS = 5

CATALOGUE = re.compile(r"^## (?:Seen in the atlas|In the analyzed systems)\s*$", re.M)
BLOCK = re.compile(r"\A\s*### Read these first\s*\n(.*?)(?=^#{2,3} |\Z)", re.M | re.S)
BULLET = re.compile(r"^- ", re.M)
SYSTEM_LINK = re.compile(r"\]\((?:\.\./)+systems/[a-z0-9-]+/?(?:#[^)]*)?\)")


def problems(name: str, text: str) -> list[str]:
    heading = CATALOGUE.search(text)
    if not heading:
        return []
    section = text[heading.end():]
    section = section[:m.start()] if (m := re.search(r"^## ", section, re.M)) else section
    block = BLOCK.match(section)
    if not block:
        if "### Read these first" in section:
            return [f"{name}: 'Read these first' is not the first thing in the catalogue"]
        if len(section.split()) > CATALOGUE_LIMIT:
            return [f"{name}: catalogue is {len(section.split())} words with no "
                    f"'### Read these first' (limit {CATALOGUE_LIMIT})"]
        return []
    items = [i for i in BULLET.split(block.group(1))[1:] if i.strip()]
    out = []
    loose = [l for l in block.group(1).split("\n")
             if l.strip() and not l.startswith(("- ", "  "))]
    if loose:
        out.append(f"{name}: 'Read these first' holds more than its list; close it "
                   "with a heading before the catalogue")
    if not 1 <= len(items) <= MAX_EXEMPLARS:
        out.append(f"{name}: 'Read these first' has {len(items)} entries (1 to {MAX_EXEMPLARS})")
    out += [f"{name}: exemplar {n} links no system report"
            for n, item in enumerate(items, 1) if not SYSTEM_LINK.search(item)]
    return out


def self_test() -> int:
    big = " ".join(["w"] * (CATALOGUE_LIMIT + 1))
    item = "- [A](../../systems/a/) seals its log.\n"
    cases = [
        ("a long catalogue without the block fails", f"## Seen in the atlas\n\n{big}\n", 1),
        ("a short catalogue without it passes", "## Seen in the atlas\n\nA few systems.\n", 0),
        ("a block of three passes",
         f"## Seen in the atlas\n\n### Read these first\n\n{item * 3}\n### Every instance\n\n{big}\n", 0),
        ("a block the catalogue runs on into fails",
         f"## Seen in the atlas\n\n### Read these first\n\n{item * 3}\nThe catalogue.\n", 1),
        ("a block of six fails", f"## Seen in the atlas\n\n### Read these first\n\n{item * 6}\n", 1),
        ("an unlinked exemplar fails", "## Seen in the atlas\n\n### Read these first\n\n- A seals its log.\n", 1),
        ("a block placed below the catalogue fails",
         f"## Seen in the atlas\n\nText.\n\n### Read these first\n\n{item}", 1),
    ]
    for name, text, expected in cases:
        got = len(problems("fixture", text))
        if got != expected:
            print(f"self-test failed: {name}: got {got}, expected {expected}", file=sys.stderr)
            return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main(root: str) -> int:
    found = []
    for path in sorted((Path(root) / "content" / "patterns").glob("*.md")):
        found += problems(path.name, path.read_text(encoding="utf-8"))
    if found:
        print("Pattern catalogues without a short entry point:", file=sys.stderr)
        for p in found:
            print(f"  {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--self-test" in args:
        sys.exit(self_test())
    sys.exit(main(next((a for a in args if not a.startswith("--")), ".")))
```

- [x] **Step 2: Self-test** (expect `self-test: 7 controls passed`). Then run
  the check against the tree. It should fail on exactly four pages: at
  2026-09-25 those were `append-only-memory-audit.md` (4,258 words),
  `rejected-value-tombstone.md` (9,774), `scope-as-a-first-class-key.md`
  (8,550) and `trust-state-machine.md` (3,597). That failure is the red step.

- [x] **Step 3: Write the four lists.** For each page, list the systems its
  catalogue links, with the first sentence of each paragraph:

```bash
python3 - content/patterns/trust-state-machine.md <<'PY'
import re, sys
t = open(sys.argv[1]).read()
sec = re.split(r"^## ", t.split("## Seen in the atlas", 1)[1], flags=re.M)[0]
for para in re.split(r"\n\s*\n", sec):
    links = re.findall(r"\[([^\]]+)\]\((?:\.\./)+systems/([a-z0-9-]+)/", para)
    if links:
        first = re.split(r"(?<=[.!?])\s", " ".join(para.split()), 1)[0]
        print(f"{links[0][1]:28} {first[:160]}")
PY
```

  Choose three to five. Aim for the cleanest complete implementation, the
  most instructive failure, and the smallest version that works. Where a
  catalogue already calls a system the sharpest or the richest, that is a
  candidate. Each bullet is one line: a link to the report, then a clause
  taken from the catalogue's own claim about it. **No claim that is not
  already in the catalogue.** Close the list with a heading, or the whole
  catalogue renders under it. Form:

```markdown
### Read these first

- [Magic Context](../../systems/magic-context/) — two independent axes rather than one status column.

### Every instance
```

- [x] **Step 4: Pointers.** `AGENTS.md` line 33: *"The last one names the
  systems worth reading"* becomes *"The last one opens with* Read these first*,
  three to five systems to start from"*. Make the same change in
  `use-the-atlas` step 3. In `add-memory-system` line 312, add: *"Add the
  system to* Read these first *only if it displaces one there on the
  criteria that list states; the list stays at five or fewer."*

- [x] **Step 5: Wire it in** after Task 4's block, with a comment in the same
  style that names the 9,774-word catalogue. Then `remove-meta-narrative`
  over the four pages, the gated chain, and commit and push. The message is
  "Read these first above every pattern catalogue over 3,000 words".

---

### Task 7: A decision note for the overview split

**Files:** create `notes/<date>-splitting-the-overview.md`. No code, and
nothing moves until the maintainer approves the note.

- [x] **Step 1: Inventory the anchors that would move** out of §1, §2
  and §11, and every link into them from outside those sections:

```bash
python3 - <<'PY'
import re, glob, collections
t = open("content/overview.md").read()
secs = re.split(r"^(?=## )", t, flags=re.M)
is_moving = lambda s: re.match(r"## (1\.|2\.|11\.) ", s)
slug = lambda h: re.sub(r"[^\w\- ]", "", h.lower()).strip().replace(" ", "-")
def ids(s):
    return {slug(h) for h in re.findall(r"^#{2,6} (.+)$", s, re.M)} | set(re.findall(r'id="([^"]+)"', s))
moving = set().union(*(ids(s) for s in secs if is_moving(s)))
inbound = collections.Counter()
for s in secs:
    if not is_moving(s):
        for a in re.findall(r"\]\(#([\w\-]+)\)", s):
            if a in moving:
                inbound[("overview.md, kept section", a)] += 1
for f in glob.glob("content/**/*.md", recursive=True) + glob.glob("site/**/*", recursive=True) + ["AGENTS.md"]:
    if f.endswith("overview.md") or not f.endswith((".md", ".html")):
        continue
    for a in re.findall(r"compare/?#([\w\-]+)", open(f).read()):
        if a in moving:
            inbound[(f, a)] += 1
print(len(moving), "anchors in the moving sections;", sum(inbound.values()), "links into them from outside those sections")
for (f, a), n in sorted(inbound.items(), key=lambda x: -x[1]):
    print(f"{n:3}  {f}  #{a}")
PY
```

  The overview renders to `/compare/`, so every link from another page is
  `compare/#<id>`. Search for that form, not `overview/#`. At 2026-09-25 the
  first version of this step searched `overview/#`, found nothing outside the
  page, and printed `6 links`. The note written from the corrected search found
  55 external links and 31 internal cross-section links. Before trusting any
  count, build once and compare one computed slug with its `id=` in
  `docs/compare/index.html`.

- [x] **Step 2: Write the note.** Cover what stays (*In Short*, *Reading This
  Report*, §3–§10, History — about 41,000 words at 2026-09-25), the three new
  pages and their URLs, how every link from Step 1 that changes page gets
  rewritten (which `check_anchors.py` then checks), which `AGENTS.md` and
  `use-the-atlas` sentences change, and what it would take to reverse.
  Written as [2026-09-25-splitting-the-overview.md](2026-09-25-splitting-the-overview.md).

- [x] **Step 3: Commit and push the note**, and stop.

### What the plan leaves open

- **Whether a lead is the right finding.** No task checks it. The
  comprehension test does, and it covers one report.
- **Older prose.** Ratchets stop it growing. It shrinks only where a reading
  opens it.
- **The verdicts page** (218,000 words in one section). It is out of scope
  here, and the natural follow-up once Task 7 has settled how the overview
  splits.

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

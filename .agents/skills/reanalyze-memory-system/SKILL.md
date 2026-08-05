---
name: reanalyze-memory-system
description: Re-read a repository Agent Memory Atlas already has a report for, at a newer commit, and fold what changed into the existing report. Use when asked to re-analyze, re-read, re-pin, refresh, or check for updates on a system already in the atlas, when an upstream project reports a fix, or when a freshness check flags a stale pin.
---

# Re-analyze Memory System

The atlas pins every report to a commit. Upstream moves; the pin does not. This
skill covers the second-most-common workflow in the repository: reading a system
again at a newer commit and folding the result into the report that exists.

**Screen the new checkout first, every time.** Run the `screen-repository` skill
before reading the diff:

```sh
python3 scripts/screen_repo.py /absolute/path/to/source-repository
```

A re-read clones a *newer* commit than the one that was screened, and the newest
commit is exactly where a compromise would arrive — a `postinstall` added last
week, a hook that was not there at the pin, a dependency range that resolved to
something new. Screening once at first reading is worth nothing here. Compare the
screen against the previous one where it matters: a new `RUNS` finding since the
pin is itself a reason to slow down, and a `FRESH` finding is close to guaranteed
— a project that just moved has just changed its dependency surface, which is
exactly the seven-day window the cooldown exists for. Re-reads are the common
case for that finding, not the exception.

It is not `add-memory-system`. There is no scaffolding, no new slug, no new
homepage card. Read that skill for the report format, the capability
definitions, the matrix rules and the build/validate loop — all of that still
applies. This one covers what is different.

## The rule that gets broken

**Write the result, not the re-review.** The report describes the system at the
pinned commit. It is not a changelog of the atlas's own understanding.

Grep the repository's history for `Fold the .* re-review into the report instead
of narrating it` and you will find the same correction applied more than once.
The forms that keep appearing and must not:

- "Re-read on <date>, N commits past the previous pin…"
- "At the commit this report first covered…"
- "This report previously said…" / "the atlas had missed…"
- "The report was updated to reflect…"

Check the finished report with:

```sh
rg -n -i 're-read|re-review|re-pin|previously (said|reported)|this report (first|named|called)|the atlas (found|missed|had)' content/systems/<slug>.md
```

Every hit is either a fact about the *subject system's* own history — which is
allowed and often the point, e.g. "until 31 July 2026 neither variable was
assigned anywhere in the repository" — or process narration, which is not. If a
sentence would have to change when the atlas changes rather than when the system
changes, it is the second kind.

### The forms that grep misses, which are the common ones

The list above is what the failure looks like when it is *explicit*. It almost
never is. The re-review leaks in as ordinary adverbs, and a report can pass the
grep above while every section quietly narrates the diff:

- "There are **now** two ways to reject a value" — there are two.
- "Where it **still** inverts" — where it inverts.
- "Trust is **now** a state, not only a score" — trust is a state.
- "Committed negative cases **now** run to five" — they run to five.
- "The review queue is the **newer** half" — newer than what the reader cannot see.
- "The mark is earned and the finding is **narrower than it was**" — grades the
  atlas's position, not the code.

Every one of those is invisible to the first grep and says the same forbidden
thing. So run the second check too, over the body only:

```sh
sed '/^## History$/q' content/systems/<slug>.md \
  | rg -n -i '\b(now|still|no longer|used to|already|newer|earlier|these days|has since|as of this reading)\b'
```

**Stop at `## History`.** That section is the log and its tense is correct there;
including it buries the real hits under the entry you just wrote, and a check
whose output is mostly noise is a check that gets skipped.

This one has a **high false-positive rate by design** — it is a prompt to apply
the test, not a list of defects. Triage each hit by asking what the word is about:

| Keep — the word is about the subject | Delete — the word is about the report |
| --- | --- |
| "values this key has **previously** lost" | "there are **now** two write destinations" |
| "evaluated against **now** or against an `asOf`" | "**still** archived at the third re-assertion" |
| "the pattern must **still** rank in the top five" after consolidation | "the audit gap is **no longer** open" |
| "what the store believed then against what is **now** claimed about then" | "**already** covered in the previous pin" |

The rule is unchanged and the adverbs are just where it hides: a sentence that
has to change when the atlas changes is the wrong kind, whatever word carries it.

Sweep the same vocabulary through every file the re-read touched, not only the
report. The homepage card is the one that gets missed — it is three sentences
written last, and "a rejected candidate **now** writes a suppression" shipped to
the published homepage exactly that way.

The one place a re-review *is* recorded is the **`## History` section at the
bottom of the report** — one dated entry per reading, newest first, carrying the
full 40-character sha. That is the log. The report body is the state, and
`scripts/check_history.py` fails the build if the newest entry's date is not the
report's `analyzed_at`, so a re-pin cannot ship without one.

What a reading taught the *method* rather than the system — that criticisms are
the claims most likely to go stale, that an orphaned pin is not a stale one, that
a hand-maintained list drifts where the process touches it — goes in the
`## History` section at the bottom of `content/overview.md`. Nothing dated goes
in the verdicts in section 9 or in the known-limitations list; those hold the
system's verdict and the atlas's standing limits, neither of which is an event.

## Establish what moved

Read the existing report's frontmatter for `revision` and `analyzed_at`. Clone
the upstream at `HEAD` — a full clone, not `--depth`, or the pinned commit may
be unreachable and commit counts will be clone artifacts rather than facts about
the project.

```sh
git log --oneline <pinned-sha>..HEAD
git diff --stat <pinned-sha>..HEAD
git diff --stat <pinned-sha>..HEAD -- <the memory paths the report's appendix names>
```

The appendix file index of the existing report is the map: it already names the
files that carry the mechanism. Diff those first, then read the commit subjects
for anything the appendix would not have listed — a new binary, a new entry
point, a new package.

If the upstream repository 404s, check for a rename before concluding it is
gone: GitHub redirects renamed repositories, and the new name is in the redirect.
See "A project that renamed itself" below.

## Decide the shape, then write

Three outcomes. Name which one you are in before editing, because they call for
different work.

**Nothing moved.** The mechanism is unchanged and no published claim is stale.
Re-pin `revision`, `revision_url` and `analyzed_at`, update the commit in
`content/overview.md`'s repositories-inspected list, and say so plainly in a new
History entry. This is a real result and worth recording — it is the common case,
and it is the one a commit-id comparison cannot distinguish from the others.
"Nothing moved" is still a reading, so it still gets an entry; the check requires
one whatever the outcome was.

**A published claim went stale.** The report asserts something that is no longer
true at the new commit. Correct the body — do not append a correction beside the
old text. Then check the *criticisms* specifically: the most common stale claim
is a gap the project has since closed, which is the failure direction least
likely to be reported by a reader. Re-check every capability mark, in both
directions.

**The mechanism is unchanged and the context is not.** The report's findings
hold and something else has appeared — a second entry point, a new mode, a
subsystem that bypasses the mechanism. Extend the report where the new material
belongs and leave the rest alone.

## What must be updated together

- `revision`, `revision_url`, `analyzed_at` in the report frontmatter.
- Any `matrix:` value the change touches, and `capabilities:` if a mark moved.
- A new entry at the top of the report's `## History`, dated to `analyzed_at`,
  with the full 40-char sha and what changed — including, when a published claim
  was wrong, what was wrong and in which direction.
- The system's verdict in `content/overview.md` section 9, if the verdict itself
  changed. It carries no dated line.
- The commit link in the repositories-inspected list in the appendix. This is a
  separate hand edit from the frontmatter and it is the one that gets forgotten —
  three entries had drifted before `scripts/check_inspected_pins.py` existed, all
  three on re-reviewed systems.
- An entry in `content/overview.md`'s `## History` **only** when the re-read
  taught something about the method rather than about the system.
- The homepage card in `site/index.html` when the headline finding changed, and
  its `data-search` terms when new mechanism names appeared.
- Pattern pages citing this system as evidence, when the evidence changed.
- Counts, if a mark moved — see the count discipline in `add-memory-system`.

Line numbers in the existing report are pinned to the old commit and are the
thing most likely to be silently wrong after a re-pin. Re-verify every one you
keep:

```sh
for spec in path/to/file.rs:123 path/to/other.py:456; do
  f=${spec%:*}; n=${spec#*:}; printf "%-44s %s\n" "$spec" "$(sed -n "${n}p" "$f")"
done
```

## When an upstream fixes something the atlas reported

State it as the system's history, not as the atlas's. "`<sha>` wired it" is a
fact about the project; "the atlas was right" is not. If the upstream's own
commit message or test file cites this atlas, that citation is a fact about
their repository and can be reported as one.

Then look for what the fix reveals rather than stopping at the fix:

- Did it leave the original defect reachable by another path? A fix in the
  callers leaves the library default intact for the next caller.
- Did it trade the defect for a weaker property? A boundary that now exists may
  be weaker than the one the design claimed.
- Did the same commit fix something the atlas did not find? Say so, and say what
  kind of reading would have caught it.
- Is there now a test? Run it if the toolchain is present and the run is cheap,
  and report what you ran and what passed. A report that says "nothing tests
  this" is a claim with a date on it.

## When a third party reports a finding

Verify it yourself at the **atlas's pinned commit**, not only at the reporter's
`main` — a report that answers a question at a different commit than it
publishes creates the drift it was meant to remove. If the code differs between
the two, say which one the answer applies to.

Then add what the report cannot get from the claim alone: whether a committed
test covers the property, whether the reporter's paraphrase matches the code
they quoted, and what the adjacent unasserted case is. Credit the reporter in
place, with a link to the issue. Remove the open question the finding answers.

## A project that renamed itself

The report's slug is the atlas's, not the project's, and changing it breaks a
published URL. The repository has a convention for this:

1. `git mv content/systems/<old>.md content/systems/<new>.md`.
2. Update `title`, `source_name`, `source_url`, `revision_url`.
3. State the rename in section 1, including whether it is complete in code —
   package manifests, licence headers and changelogs usually lag the README.
4. Add `site/redirects/<old-slug>.html`, copying an existing one. It is a
   meta-refresh page carrying `data-redirect-stub` on its `<body>`.
   `scripts/build_site.sh` copies every file in that directory to
   `docs/systems/<slug>/index.html`, and `scripts/test_site.sh` excludes
   stubs from its one-report-per-content-file count by looking for that
   attribute.
5. Sweep the old slug out of `content/overview.md`, `site/index.html` and any
   pattern page. Generated files (the matrix, the capability grid, the A–Z
   index, `content/systems-index.md`) rebuild themselves — do not hand-edit
   them.

Check whether the rename predates the atlas's own analysis. If the README at
the pinned commit already carried the new name, the report was wrong when
published rather than overtaken, and the known-limitations bullet should say so.

## Build and validate

Same as `add-memory-system`:

```sh
npm run build
npm test
```

`npm test` will catch a matrix out of sync, a stale count, an abbreviated commit
link, a missing Mermaid diagram, a missing or misdated History entry, and an
inspected-list pin that disagrees with the report. It will not catch a line number
that moved or a claim that is no longer true.

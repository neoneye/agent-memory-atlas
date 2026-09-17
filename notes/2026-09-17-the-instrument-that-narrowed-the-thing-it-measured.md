# The instrument that narrowed the thing it measured

**Written 2026-09-17.** Four re-reads in one pass, and three of them had already
published a number or an absence that the repository did not support. The
mistakes were not careless. Each one came from measuring through a filter nobody
knew was between the question and the answer — and in two cases the project being
read had found its own instance first and written the diagnosis down.

The shape: **a count or an absence is taken from a surface that silently excludes
part of the thing being counted.** The reading is honest, the command is real,
the number is wrong, and nothing in the output says a filter was applied.

## 1. A deny-by-default rule hid a third of the evidence

[Ori Mnemos][ori] published a test count of 35. The repository has 57 test
files. The gap is not drift: `.gitignore` carried `tests/*` plus a
hand-maintained allowlist of 36 `!` lines, so a newly written test was invisible
to git unless someone remembered to exempt it, and `tests/fixtures/` was ignored
as well — meaning even the allowlisted tests could not run from a clean clone.

The project found this itself and stated the mechanism better than a summary can:

> "Deny-by-default on a test directory fails silently and in the worst
> direction: the suite still passes locally, so nothing tells you the evidence
> never shipped."

The part worth keeping for a reader of repositories is the second half. The
atlas counted what `git ls-files` showed, which is the correct command, run
correctly, against a surface that had been narrowed upstream. **A reading that
enumerates through version control inherits whatever version control was told to
hide.** The 21 hidden files were not incidental — they were the tests proving the
correctness fixes in the release.

## 2. A count nobody recomputed

[Claudest][cla] carried "two test files" in four places, including the matrix
`risks` field and the verdict entry, against a repository holding twenty test
files and 470 test functions — seventeen files and 414 functions under
`tests/claude-memory/` alone.

No filter caused this one; it was simply never recomputed, and it propagated
because a matrix field and a verdict entry are copies rather than views.

What makes it worth recording beside the first case is that **the criticism the
number was supporting was correct, and survived the correction in a stronger
form.** The point was never that the suite is small. It is that
`grep -rli consolidat tests/` returns exactly one file, and what that file tests
is config writing — so the one mechanism that edits the user's `CLAUDE.md` and
`MEMORY.md` on every session is the one nothing exercises. Counting tests against
the repository hid a fact that counting them against the mechanism makes obvious.

## 3. An absence search that covered two of three directories

[AgenticTrading][agt] withheld `negative_eval` on a grep across the committed
tests. The grep was real and its result was true. It covered
`memory_testing/` and `orchestration/tests/`, and the repository also has
`orchestration/FinAgents/memory/tests/` — five files and 1,796 lines *inside* the
memory package, driving all three servers, which the appendix never named.

The mark does not move: that directory carries zero `assert` statements and
decides an outcome by searching the reply for `success`, `stored`, `created`,
`saved` or `memory_id`, so a store that echoed the word `stored` would pass. But
the published sentence rested on a search that never looked where the tests were.

**An absence claim is only as wide as the paths it enumerated**, and the appendix
is where that width becomes checkable by someone else.

## 4. Line numbers are a measurement too

[SillyTavern][sil] moved 86 commits with its memory mechanism unchanged — two of
three anchored files byte-identical by blob sha, the third taking +147/-28 from
a sorting optimisation whose own message says *"Sort order is unchanged"*. A
re-pin on that basis is correct and nearly free.

Five of the report's twenty-one line anchors had still moved. `:4024` at the old
pin is `delayUntilRecursion: { default: 0 }`; at the new pin it is a comment.
Re-pinning without re-verifying would have left the report citing real lines that
name unrelated code — the most durable kind of wrong, because the link resolves.

The file's own length was stale in two places as well.

## What this suggests for a reviewer

Every case above is a *true statement about a narrowed surface*. The defence is
not more care; it is naming the surface in the claim.

- **State the enumeration, not just the result.** "57 test files" is a fact about
  a checkout; "`git ls-files` showed 36" is a fact about a checkout *and* its
  `.gitignore`. When they disagree, the second is the finding.
- **Count against the mechanism, not the repository.** A large suite that never
  drives the dangerous path is more misleading than a small one, because the
  total is reassuring.
- **Re-run an absence search as a path list.** The question is not "did the grep
  return nothing" but "which directories did it enter". Put the paths in the
  appendix so the next reader can widen them.
- **Re-verify every line number a re-pin carries forward,** and check the two
  places the file's length is quoted.
- **Prove the instrument before trusting a null.** Two of this pass's own steps
  produced false negatives: a positive control that never fired because the test
  text landed after `## History` and was stripped, and a blob comparison that
  reported three files IDENTICAL because a `for path in …` loop had emptied
  `$PATH` under zsh and both sides captured the empty string. Two failed commands
  always compare equal. Test for emptiness before testing for equality, and make
  the control fire before believing the absence.

The two projects here that found their own instance both did it the same way — by
hitting the symptom in use, then writing the mechanism into a commit message or a
test docstring rather than leaving it in the diff. Neither would be recoverable
from the code alone.

[ori]: ../content/systems/ori-mnemos.md
[cla]: ../content/systems/claudest.md
[agt]: ../content/systems/agentictrading.md
[sil]: ../content/systems/sillytavern.md

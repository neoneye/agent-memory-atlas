# The atlas is being read by the systems it reviews

**Status:** finding about the project's position, with four instances in a week.
**Origin:** noticing that four separate re-reads this week turned on something an
upstream did *because of* a report.

## The instances

**memoir-cli closed the finding.** The report's central criticism was that the
absolute tombstone the project's own spec makes normative had no writer any user
could reach — the only assignment lived in a dated one-off script whose header
said it was not wired into any command. Release 3.12.0 ships `memoir forget
[--purge]`. The mark follows. A separate commit in the same run reads:
*"server.json: 3.2.2 -> 3.12.0 (MCP registry manifest was 9 minors stale —
caught by the agent-memory-atlas review)"*, with an npm hook added so it cannot
drift again.

**Hippo audited the report back, and was right twice.** Its roadmap carries a
section headed *agent-memory-atlas comparative gap analysis (source-verified)*,
which checked every claim about hippo's code against hippo's code and found the
atlas wrong or overstated on three. Two held on re-verification here: the
bi-temporal paragraph was wrong twice in one sentence, and `negative_eval` had
been withheld on a fact about one fixture schema rather than about the evidence.
The third had already been corrected in an earlier reading. Its own discipline
note is the part worth quoting: *"the atlas is an LLM-authored report and
inherits LLM-report failure modes. Any future item sourced from an external
audit of hippo's code gets a source-verification pass before it lands."*

**PLUR1BUS's author filed an issue and a PR** rewriting the atlas's report on
his own system — covered in
[when the system's author sends a patch](2026-08-19-when-the-systems-author-sends-a-patch.md).

**MeMex-Zero-RAG's headline risk is gone** — `L1/credentials.md`, committed
despite `.gitignore` and its own warning, is now three `.example` files.

## What changes

The atlas was written as a reader's artifact: read code, pin a commit, publish
what is there. Four events in one week say it is also an actor in the systems it
describes, and three consequences follow.

**A finding has a half-life now.** "No writer any user can reach" was true when
published and false eleven days later. A criticism that names a specific missing
mechanism is the most likely kind to be closed, and the report that carries it
is the least likely to be re-read, because nothing about it looks stale. That
argues for re-reading the reports with the sharpest criticisms first, rather
than the oldest.

**Being right is not the same as being current.** The Hippo case is the useful
one: the report was corrected by its subject, and the subject was correct. That
is the system working — but only because the correction was checked against the
tree here before it landed, which is the rule that keeps a report from becoming
whatever its subject last said about it. Verify, then restate in the atlas's
own voice, citing what was read here.

**The reports are read as scorecards whether or not they are written as ones.**
Hippo's roadmap turned four withheld marks into four numbered work items with
effort estimates and success criteria. That is a better use than the atlas
intends and a heavier one than a judgement call can carry: a mark withheld for a
narrow reason gets read as a gap to close. It is an argument for the evidence
records — a mark that says *why*, in four fields, is harder to misread than a
tick.

## The thing not to do

None of this is a reason to soften a finding, to route corrections through the
subject, or to let a maintainer's description stand in for a reading. The value
of the atlas to the people building these systems is exactly that it is not
their description of themselves. The right response to being read by your
subjects is to be more careful, not more agreeable.

# The same bug twice in one session, and why writing it down did not stop it

**Status:** finding about my own process, with a checker gap named.
**Origin:** a blanket `t.replace(OLD_SHA, NEW_SHA)` in the re-pin scripts,
which is the obvious way to re-pin a report and is wrong.

## The bug

A report's frontmatter carries the pin, and its `## History` carries one entry
per reading, each quoting the commit *that reading was made against*. Replacing
every occurrence of the old sha updates the frontmatter — and rewrites the
commit id inside every older History entry, so each past reading silently claims
the commit it was not made at.

The History section is the atlas's record of what was read when. Corrupting it
is worse than a stale pin, because a stale pin is visible and this is not.

## It happened twice

**First**, on memoryops-ai and tokenmizer. Caught before commit, fixed, and
written into the commit message as a lesson — including the observation that
`check_history.py` validates the newest entry against the pin and cannot see an
older one being rewritten.

**Then again**, on the batch of eight: agent-memory-doctrine, breadcrumbs,
nexusmem, memex-zero-rag, memoir-cli, hippo-memory, perseus-vault, mnemosyne.
Three of those were already pushed by the time it was found.

The detection was cheap once looked for — no sha should appear twice across one
report's History entries:

```sh
sed -n '/^## History$/,$p' content/systems/<slug>.md \
  | grep -oE '\[`[a-f0-9]{40}`\]' | grep -oE '[a-f0-9]{40}' | sort | uniq -d
```

The repair was cheap too: take the pre-edit file from git, keep the new entry,
splice the old tail back. Verified two ways — no duplicate sha in any History,
and every file's newest entry matching its pin.

## The lesson, which is not "be careful"

**I had already written this lesson down, in a commit message, and it did not
prevent the recurrence.** That is the finding. Prose in a commit message is not
a control; it is a record. The same hand reached for the same
`replace(OLD, NEW)` a few hours later because it is the shortest correct-looking
way to express "re-pin this report".

Two things would have worked where the note did not:

1. **A checker.** The duplicate-sha grep above is three lines and would have
   failed the build both times. `check_history.py` exists and validates the
   newest entry only, which is exactly the shape of gap this atlas reports in
   other people's code — a validator that checks the thing that was created and
   not the thing that was quietly changed.
2. **A narrower tool.** Re-pinning should edit the three frontmatter lines and
   prepend one History entry, and should not be able to touch the rest of the
   file. The blunt instrument is the bug.

Neither exists yet. Until one does, the grep belongs in the re-pin routine.

## The related near-miss

In the same batch I wrote a History entry quoting a sha whose first twelve
characters matched HEAD and whose remaining twenty-eight I had invented, because
I typed a plausible-looking id instead of reading one. `check_inspected_pins.py`
caught it — the list and the report disagreed — and the message was confusing
precisely because both ids *displayed* as `2c1fe382b9c2`. A truncated display of
a full-length identifier hides exactly the class of error that matters.

# Evidence records rot, and only a re-read finds it

**Status:** finding about the `capability_evidence` schema, with two instances.
**Origin:** re-pinning Perseus Vault and NexusMem on the same day, and checking
each record's anchors against the tree rather than carrying them forward.

## The shape

A `capability_evidence` record is four fields — subsystem, file, symbol, test —
and its whole value is that a reader can go and look. That makes it the most
citation-like thing in the corpus, and citations rot in a specific way: the
claim stays true while the coordinates stop pointing at it.

Both instances were found the same way and neither was visible from the report.

**Perseus Vault — the symbol was deleted.** The `human_review` record named
`mimir_action_approve` in `src/mcp.rs`. It existed at the previous pin; it does
not exist at this one. The approval surface is `admission_decide` in
`src/tools.rs`, refusing any decision that is not `approve` or `reject`. The
mark is still earned; the evidence for it pointed at nothing.

**NexusMem — the symbol moved.** The `scope_enforced` record named
`src/store/store.ts`. A refactor split that file, and `search` now lives at
`src/store/search.ts:51`. The predicate is unchanged, the test that pins it is
unchanged, and the file named in the record is no longer the file.

## Why nothing catches this

`check_capability_evidence.py` validates *shape*: that every mark has a record,
that all four fields are filled, that the flag is one of the seven, and that
coverage does not fall. It cannot open the subject repository — that repository
is not in this one — so it cannot know whether `src/mcp.rs` still contains
`mimir_action_approve`.

Nothing else can either. The pin makes the claim checkable *by a person with the
clone*; it does not make it self-checking. So an evidence record is true at the
commit it was written against and unverified at every commit after, and the only
event that re-verifies it is a re-read of that system.

That is a property of the design rather than a defect in it — the alternative is
vendoring 301 repositories — but it has a consequence worth stating: **the
evidence block is not a durable citation, it is a dated one.** A reader
following a record against a newer checkout can find nothing there and conclude
the atlas was wrong, when the atlas was right on a date.

## What to do about it

1. **Re-verify every anchor on a re-pin, not just the marks.** The mark surviving
   says nothing about whether its coordinates did. Both of these had surviving
   marks.
2. **Prefer the symbol to the line number, and the test to both.** Line numbers
   moved on every report re-read this week — Mnemosyne's `degrade_episodic` went
   from `beam.py:8163` to `:8705`, Hippo's sections 4 and 9 moved by seven to
   nine lines each. A symbol name survives a refactor that a line number cannot;
   a test id survives a rename that a symbol cannot.
3. **Write `none` when there is no test.** Perseus's re-anchored record says
   `none — no committed test names the approval path`, which is more useful than
   a plausible file, and is the field's documented honest answer.
4. **Consider stamping the record.** A record is only claimed true at the report's
   `analyzed_at`, and the frontmatter already carries that. Saying so once, on
   the rubric page, would stop a reader reading a dated citation as a standing
   one.

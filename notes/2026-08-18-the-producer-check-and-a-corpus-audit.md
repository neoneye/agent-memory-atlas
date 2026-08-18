# The producer check, and auditing 301 reports for marks that launder it

**Status:** finding, plus a method that is cheap to re-run.
**Origin:** an outside review asked for a "wiring check"; the step was genuinely
missing from `add-memory-system`, and adding it raised the question of whether
the corpus had been doing it informally all along.

## The gap

Declared-and-unwired is the most common defect the atlas reports. Fifty-one
reports carry a version of it, and the sharpest verdict entries are instances:
an audit log where nine of twenty actions have no producer, a tombstone whose
only writer is a script its own header says is *"NOT wired into any CLI
command"*, a reviewer quorum that always passes because the policy it reads is
hardcoded `{}` at both write paths.

Grepping `.agents/skills/add-memory-system/SKILL.md` for `producer`, `wired`,
`call site` or `caller` returned **nothing**. Those fifty-one findings existed
because whoever wrote the report thought to look. The rate across 301 reports
was therefore not knowable.

## The step, and why the obvious version of it fails

The naive form — *grep for call sites; if only tests call it, flag UNWIRED* —
would miss most of the real cases in this corpus. All three examples above have
callers, and a call-graph grep reports them live. The question is whether any
path a user or an agent can reach **produces** the state the mechanism acts on,
which is data flow rather than the call graph.

The shapes it keeps taking, now written into the skill: a parameter every caller
omits, a config key with no setter, a branch on a flag nothing sets, a default no
caller overrides, and a writer that exists only in tests or in a file the package
manifest excludes.

## The audit, and its result

All fifty reports whose body contains an unwired claim, read against the marks
they carry. **No report credits a capability mark to a mechanism its own prose
says has no producer.** Zero exceptions.

The confirming direction is stronger evidence than the clean cases:
`alma-memory`'s caller-less `needs_review()` sits on a report with no
`human_review`; `csm`'s writer-less review queue likewise; `memoir-cli`'s
unreachable tombstone earns no `tombstone`; `palazzo`'s unfilled `valid_from`
earns no `bitemporal`; `memory-lancedb-pro`'s writer-less `pending` state earns
neither `trust_state` nor `human_review`.

Five reports state the withholding in as many words, and they are the models to
copy: `kage` (*"Audit log — withheld, and the reason is a second unwired
mechanism"*), `memoir`, `nooa-memory`, `powermem` (*"withheld twice over"*),
`yantrikdb`.

So the step codifies the bar rather than raising it — which is worth saying in
the skill, because a writer told only *"do not credit an unwired mechanism"*
cannot tell whether that is established practice or a new rule aimed at work
already published.

## The distinction the audit surfaced

**A missing producer means the mechanism was never built. A stale consumer means
it was built and does not take effect.** These fail differently and the producer
test does not separate them on its own.

OmniIntelligence is the corpus's example of the second, and was the only
borderline call in fifty: its manual kill switch appends to
`pattern_disable_events` with `reason` and `actor` both `NOT NULL`, so the
producer is real — and the gate reads a materialized view nothing refreshes
outside tests. The mark stands; the report is required to say the override never
reaches the read path.

MindCache, re-pinned the same day, is a third shape worth naming: a scope repair
that **fails into a `try` block**. `filter_by(user_id)` passes a positional
argument to a keyword-only method, so the lookup raises before it queries, and
the caller catches `Exception` and logs at `INFO`. The leak is closed and the
feature is closed with it, silently. A scope repair belongs where a wrong one is
loud.

## The method, for re-running it

Cheap, and worth repeating whenever the corpus grows. Regex the report bodies for
`no producer|never called|no call site|not wired|never wired|unwired|no writer|
cannot be reached|no caller`, pair each hit with the report's `capabilities:`,
and judge by hand whether the unwired mechanism is the one a carried mark names.

Three false-positive classes cost the most time and are worth filtering up front:

1. **Appendix and history noise.** A file index naming an unwired file is not a
   claim. Cutting at `## Appendix` / `## History` dropped the output from 1,019
   lines to 425 and two reports out of the set entirely.
2. **Matches that span a newline.** `grep -n` is line-based and misses
   `no\ncaller`; the sentence-level pass over `re.sub(r'\s+',' ',text)` finds
   hits that a line grep swears are absent. Three reports looked like ghosts
   until this was noticed.
3. **Absence-shaped statements of strength.** memanto's *"no caller can select
   `manual` and supply nothing"* and windie-sandbox's *"no caller can forget
   it"* are enforcement guarantees, not findings. Same words, opposite polarity.

The count moved 52 → 51 → 50 as the query sharpened, which is worth stating
whenever the number is quoted.

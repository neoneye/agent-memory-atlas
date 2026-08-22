# Notes

Working documents that are **not part of the published site** — proposals,
backlog, and decisions with their reasoning. `scripts/build_site.sh` only reads
`content/`, `site/`, `assets/` and `templates/`, so nothing here is rendered or
clobbered by a build.

Convention: `YYYY-MM-DD-{name}.md`, dated when the note was written rather than
when the work happens.

- [2026-08-23-a-tested-contract-for-losing-the-write.md](2026-08-23-a-tested-contract-for-losing-the-write.md) —
  llmaker triaged and excluded: a self-hosting platform whose only memory is a
  20-turn Redis transcript with a 7-day TTL. The keeper is underneath the scope
  call — every Redis call swallows its exception, and a committed test asserts
  that `load`, `append` and `clear` all return normally against a raising
  client, so the silent loss is a contract and anyone who later wants the write
  to report failure has to delete an assertion first. GENOME has the same
  surface one report over. Also: an eval harness that marks which of its four
  metrics a judge produced and which one arithmetic did.
- [2026-08-22-a-context-engine-that-expires-on-purpose.md](2026-08-22-a-context-engine-that-expires-on-purpose.md) —
  `Perseus-Computing-LLC/perseus` triaged and excluded: it is a separate
  repository from the Vault the atlas reports on, and it is a live-context
  renderer whose README draws this atlas's own boundary before anyone else has
  to. The one thing that survives a session is a checkpoint carrying a
  `stale_after` and a `max_keep: 30` — a run record that ships with an expiry,
  which is the cleanest case yet of *a store of the agent's work is not a store
  of the agent's beliefs*. Two things worth stealing anyway: a stale-lock
  reclaim that reads `EPERM` as alive because cross-user is the normal case for
  agents sharing a store over NFS, and a natural-sort key for `<ts>_<n>.yaml`
  filenames, without which retention deletes the newest file first.
- [2026-08-22-the-benchmark-everyone-cites-and-the-hint-with-no-verb.md](2026-08-22-the-benchmark-everyone-cites-and-the-hint-with-no-verb.md) —
  LongMemEval read at a commit for the first time and deliberately given no
  report: it is a dataset and a harness, so the findings went to the benchmarks
  page instead, which now reads five benchmarks directly rather than four. Three
  different accuracies come out of one run, abstention is a substring test on the
  question id rather than a category, the retrieval metrics drop every abstention
  item, and the dataset is not in the repository — which matters because the
  September 2025 "cleaned" release changed the haystacks and no result artifact
  records which one it read. Heimdall re-pinned: the shell-command parser is gone,
  replaced by a level-triggered reconciler whose queue rows carry no verb, and the
  new finding is that two subsystems now delete from one store while the audit
  compares the journal only to the filesystem.
- [2026-08-21-a-search-that-keeps-what-worked-and-nothing-it-refused.md](2026-08-21-a-search-that-keeps-what-worked-and-nothing-it-refused.md) —
  AVO (arXiv:2603.24517) triaged: an evolutionary-search paper, not agent memory
  and with no repository to pin, carrying one observation this atlas keeps
  finding in genres it was not looking at — the lineage store keeps what worked
  and nothing about what it refused.
- [2026-08-20-the-build-page-judged-as-a-recommendation.md](2026-08-20-the-build-page-judged-as-a-recommendation.md) —
  the paved path read end to end as a builder would, and six defects, almost all
  in packaging rather than argument. The sharpest: of the twenty acceptance
  tests, only two have a `then` clause requiring a memory to be *present*, so a
  system whose recall always returns the empty set satisfies sixteen outright and
  two more with an audit row — the anti-vacuity guard the catalogue applies
  correctly to `evidence.rebuild_from_retained` did not propagate to the other
  nineteen. Also: the profile chosen in §1 is never consumed by §3 or §4 though
  the join already exists in two committed artifacts; deferrability cuts across
  the stages rather than along them, so the most deferrable stage is scheduled
  before the two that close silent failures; "an afternoon" is an invented number
  on a page that refuses to invent numbers; and Stage 1's row promises a scope
  *boundary* where the atlas reserves that word for something stronger.
- [2026-08-20-a-curriculum-a-position-paper-and-a-stale-record.md](2026-08-20-a-curriculum-a-position-paper-and-a-stale-record.md) —
  three non-systems triaged beside the Heimdall report. Marble's curriculum
  taxonomy is not memory and is the worked example the promotion-between-tiers
  page has been asking for: evidence criteria required on every node, a
  prerequisite DAG whose edges are typed hard or soft and carry a one-line reason
  each. The scientific-teams position paper is the thinnest adjacency here and is
  recorded so nobody checks it twice. And a Cipher Brief essay about export
  controls carries the best compression of the staleness argument in this
  directory — *"a larger model querying the same stale record returns the same
  coordinates faster and with more confidence"* — which lands on the same side as
  Heimdall: staleness is not something a bigger model detects, it is something
  that has to be checked. Two rules: *not in scope* and *nothing to learn* are
  different verdicts, and where a claim comes from predicts its relevance badly.
- [2026-08-20-two-platforms-and-the-window-that-persists.md](2026-08-20-two-platforms-and-the-window-that-persists.md) —
  Hybro and Future AGI triaged, both excluded. Hybro is the closest call in a
  while: a `backend/context_memory/` package the five-word operation probe cannot
  see by name, holding durable conversation turns with a body stored by reference
  plus hash and expiry, a token estimate per representation, `was_successful` on
  the turn, and a room summary carrying key decisions — and it stays out because
  the only caller of `search_memory` is the orchestrator assembling a supervisor
  context, and nothing is scoped above a room. Future AGI observes agents rather
  than remembering for them; its prompt optimiser promotes an instruction, which
  cannot be false, over no store at all. Sixth vocabulary poison and the most
  on-the-nose: every `tombstone` in that tree is a ClickHouse CDC deletion
  marker. Two rules follow — probe directory names as well as operations, and
  settle the compaction boundary by asking who issues the query *and* what the
  widest scope is.
- [2026-08-20-someone-built-the-contract.md](2026-08-20-someone-built-the-contract.md) —
  Perseus Vault shipped `benchmark/scoped_memory/`, a versioned portable
  capability contract with the two properties nine of this project's notes
  specified and never built: the same contract run against a deterministic
  reference surface *and* an MCP adapter over the real system, and an outcome
  vocabulary — allow, deny, scope_mismatch, stale_conflict, abstain,
  unavailable — where *"a missing semantic provider or surface is represented as
  `unavailable`; it is never converted to a fabricated zero or pass"*, pinned by
  a committed test. Scope is bound out of band with a named refusal for caller
  injection, filtering runs before the ranker sees candidate IDs, and the
  published report is hash-only with a stable signature. Cluster G's honest
  third answer: part of it got built somewhere else, by a system already in the
  corpus. What follows — the atlas's twenty tests are a boolean plus a control
  where an outcome vocabulary would be structural, and the atlas still has not
  run anything.
- [2026-08-20-what-it-cannot-recheck-it-does-not-carry.md](2026-08-20-what-it-cannot-recheck-it-does-not-carry.md) —
  commaai/openpilot triaged and excluded on a boundary this corpus had not drawn
  before: its persisted state *is* falsifiable — learned steering ratio, camera
  extrinsics, torque response — but there is no agent for whom it is memory, no
  model with tools and no registry to grep. Read anyway for four mechanisms the
  memory corpus mostly lacks. It names the one learned value whose producing
  condition it cannot re-observe — stiffness, lowered by wet roads — and resets
  it every drive with the reason in a comment. It keys a cached belief on the
  car, the tuning scheme, the constants and the learner's own `VERSION`, so a
  changed algorithm makes every belief it produced unrestorable without a
  migration. Its forgiving loader is safe because it `remove()`s what it could
  not parse, and on a validity failure it refuses the fitted parameters while
  restoring the raw points. Retention is a flag per key in one header, executed
  by the lifecycle owner. Plus hysteresis applied to a trust state rather than to
  retrieval, and a fifth vocabulary-probe poison: `tombstone` here is a crash
  dump.
- [2026-08-20-four-more-and-the-memory-under-the-product.md](2026-08-20-four-more-and-the-memory-under-the-product.md) —
  outworked, Corbell, mission-control and the Proteus paper triaged. Two of the
  three repositories read like memory systems and are not; the third is a
  pixel-art Electron office with the most complete memory of the four —
  `memorySet`/`memorySearch`/`memoryDelete` over a scoped key-value table,
  exposed as MCP tools, so the model is their caller. Corbell learns `Decision`
  records from design docs and loses the human's confirmations on the next
  `docs:scan`, which is the sift-kg finding in an unrelated repository, beside a
  `load()` that answers every parse failure with an empty list. mission-control
  stores questions awaiting answers, not claims that could be false, and gives
  the vocabulary probe a new poison: every `memory` hit is credential RAM.
  Proteus is parametric memory inside a sequence model and is kept only as a
  boundary marker. Outworked and Corbell became reports the same day. The rule: when a repository's memory is not what the
  repository is for, the tool registry finds it and the README does not.
- [2026-08-20-three-candidates-and-the-half-that-can-be-false.md](2026-08-20-three-candidates-and-the-half-that-can-be-false.md) —
  OpenWolf, piodide and sift-kg triaged; two in scope with no report yet, one
  excluded. The same shape in all three: the durable state splits into a half
  that cannot be wrong and a half that can, and the second is the unprotected
  one. OpenWolf's only belief-writer is a weekly cron that overwrites cerebrum.md
  with a model's stdout, routed by a substring check, while every mechanical
  store has a hook — and the repo ships a `cerebrum_stale` detector advising you
  to check the hooks that do not exist. piodide keeps nothing falsifiable at all
  and states that contract to the model in its own system prompt. sift-kg
  rebuilds its graph from retained extractions and the rebuild is what reverts
  every human rejection: `sift resolve` truncates the merge decisions while the
  relation-review branch twenty lines below reads, dedupes on the value triple
  and extends. Carries the rule that follows — a rebuildable projection is only
  safe if every correction is an input to the rebuild.
- [2026-08-20-three-re-reads-and-a-trust-state-with-no-reader.md](2026-08-20-three-re-reads-and-a-trust-state-with-no-reader.md) —
  llm-wiki-memory, PLUR1BUS and har re-read at newer commits; no pin advanced and
  no mark changed, because none of them got a whole re-reading. llm-wiki-memory
  woke from dormancy (29 commits, 510 files) with a fail-closed quality judge
  whose `memory.quality:"unverified"` flag has four writers, two preservers, two
  clearers and no reader — declared-and-unwired with the halves reversed — plus a
  test-isolation guard written after its own suite hard-deleted ~590 real leaves
  from the developer's store. PLUR1BUS fixed an embedding drain that ran before
  capture inside the same 60-second budget and starved it, which is a failure
  mode the recoverable-background-work page does not have. har doubled in size
  and added no memory surface, and the refusal mechanism it was kept for now
  prints its own name: an unregister blocklist.
- [2026-08-20-ninety-four-notes-clustered.md](2026-08-20-ninety-four-notes-clustered.md) —
  the other ninety-four notes sorted into ten kinds, with the most significant
  document and the most significant insight named per cluster. Three findings
  from the distribution: the scope boundary got more writing (12 notes) than the
  acquisition it bounds (8); the largest and fastest-growing cluster is the
  project auditing its own method (12), whose best items are engineering findings
  with no dependence on agent memory; and the nine notes specifying harnesses,
  eval suites and conformance runs have shipped one artifact between them and no
  harness at all, which makes cluster G a decision rather than a backlog. Also the
  chronological turn at 2026-08-09, where the corpus stopped being the thing
  under construction and became the thing under audit.
- [2026-08-20-the-corpus-held-the-answer-the-rubric-had-no-column.md](2026-08-20-the-corpus-held-the-answer-the-rubric-had-no-column.md) —
  An outside survey named an axis — who currently holds the right to write —
  that three reports written in the previous two days each answered differently.
  Reading more systems does not produce a new axis; a different decomposition
  does, and the evidence had been accumulating in prose with nowhere to go.
- [2026-08-20-a-failure-that-reads-as-empty.md](2026-08-20-a-failure-that-reads-as-empty.md) —
  A loader that returns the empty value on every read failure, and a save that
  appends to whatever the loader returned, compose into silent data loss. The
  corrupted store and the empty store are indistinguishable to every test that
  does not deliberately corrupt one.
- [2026-08-20-the-good-pattern-is-one-subsystem-away.md](2026-08-20-the-good-pattern-is-one-subsystem-away.md) —
  fx, memoir and KAISEN each solve a problem correctly in one subsystem and not
  in another that has it too. Rigor attaches to the subsystem that visibly
  needed it, not to the property. One grep turns a complaint into an
  observation.
- [2026-08-20-the-evidence-record-is-a-review-instrument.md](2026-08-20-the-evidence-record-is-a-review-instrument.md) —
  Verifying a mark asks whether a claim is true; writing its evidence record
  asks where exactly it happens, which is one level deeper than the rubric ever
  requires. Three weeks of a correct mark, one hour of writing four fields to
  find its boundary.
- [2026-08-19-a-re-pin-is-a-claim-about-the-whole-report.md](2026-08-19-a-re-pin-is-a-claim-about-the-whole-report.md) —
  Verifying the one criticism an upstream said it had closed, then advancing the
  pin, left the report pinning 3.12.0 and describing 3.11 in two other places.
  An upstream note about one gap is a reason to widen the re-read, not to narrow
  it — and the verdict file went stale in the same pass.
- [2026-08-19-a-test-that-restates-a-constant.md](2026-08-19-a-test-that-restates-a-constant.md) —
  A retention cap was inverted so a paying account kept less than a free one,
  and the unit test covering it pinned the literal numbers, so it moved with the
  bug and asserted the inversion. Assert the property the constant exists to
  satisfy, with the general form for caps, limits, timeouts and TTLs.
- [2026-08-19-two-ways-to-be-wrong-about-your-own-benchmark.md](2026-08-19-two-ways-to-be-wrong-about-your-own-benchmark.md) —
  repowise and Gortex are mirror images: a sealed external split whose evidence
  lives in another repository, against a committed ground truth of ten queries
  the project wrote about its own codebase. "Committed" and "independent" are
  two axes, and the benchmarks page currently sorts on one.
- [2026-08-19-nothing-moved-is-when-to-audit-the-report.md](2026-08-19-nothing-moved-is-when-to-audit-the-report.md) —
  When HEAD is already the pinned commit there is no diff, the code becomes a
  frozen reference, and every disagreement with the report is yours. One such
  pass found a missing mark, two line numbers wrong when written, frontmatter
  contradicting itself, and a verdict claim with nothing in the report behind it.
- [2026-08-19-one-field-asked-two-questions.md](2026-08-19-one-field-asked-two-questions.md) —
  Gortex weights its provenance ladder twice, discounting its *most* trusted tier
  for centrality because abundant evidence inflates authority. repowise's gate
  stamps `unverified` on both "checked and failed" and "could not check". Same
  error from opposite ends: enumerate a judgment field's writers and readers
  separately.
- [2026-08-19-the-same-bug-twice-in-one-session.md](2026-08-19-the-same-bug-twice-in-one-session.md) —
  A blanket sha replace is the obvious way to re-pin a report and it rewrites the
  commit id inside every *older* History entry, so each past reading silently
  claims a commit it was not made at. Caught on two reports, written up as a
  lesson in the commit message, and then repeated hours later across eight —
  three already pushed. The finding is that the note did not prevent the
  recurrence: prose in a commit message is a record, not a control. Carries the
  three-line duplicate-sha grep that would have failed the build both times, the
  check_history.py gap it exposes (newest entry only), and a near-miss where a
  fabricated sha tail hid behind a truncated display.
- [2026-08-19-evidence-records-rot-and-only-a-re-read-finds-it.md](2026-08-19-evidence-records-rot-and-only-a-re-read-finds-it.md) —
  Two capability_evidence records went stale the same day: Perseus Vault's
  human_review named a symbol that had been deleted, NexusMem's scope_enforced
  named a file a refactor had emptied. Both marks still held; only the
  coordinates rotted. check_capability_evidence.py validates shape and cannot
  open the subject repository, so an evidence record is true at the commit it was
  written against and unverified at every commit after — a dated citation, not a
  durable one. Four rules follow, including prefer the symbol to the line number
  and the test id to both.
- [2026-08-19-the-atlas-is-being-read-by-the-systems-it-reviews.md](2026-08-19-the-atlas-is-being-read-by-the-systems-it-reviews.md) —
  Four events in one week where an upstream acted on a report: memoir-cli shipped
  the retraction verb whose absence was the report's central criticism and
  credited the review in its commit message, Hippo published a source-verified
  audit of the atlas that was right twice, PLUR1BUS's author filed a PR rewriting
  his own report, and MeMex-Zero-RAG removed the committed credentials file.
  Three consequences: a sharp finding now has a half-life and should be re-read
  before an old one, being right is not being current, and the reports are read
  as scorecards whether or not they are written as ones — which is an argument
  for evidence records over ticks. And the thing not to do: none of it is a
  reason to soften a finding or let a maintainer's description stand in for a
  reading.
- [2026-08-19-the-vocabulary-probe-lies.md](2026-08-19-the-vocabulary-probe-lies.md) —
  Grepping a tree for `remember`/`tombstone`/`supersede` settled four repositories
  in minutes and was wrong in every one until the hits were read. Five recurring
  poisons: a committed BERT tokenizer vocabulary and a vendored licence (Warp),
  the IR sense of `recall@k` (qmd), the systems sense of `memory` as RAM (SAM),
  and a framework whose chat buffer is called memory (ai-tutor-app). The worse
  failure is the clean probe: a `crates/`-scoped search made Warp's wired memory
  client look declared-and-unwired until the producer check ran over the whole
  tree. Five rules, including exclude `models/` and `LICENSE*` before counting.
- [2026-08-19-when-the-systems-author-sends-a-patch.md](2026-08-19-when-the-systems-author-sends-a-patch.md) —
  PLUR1BUS's maintainer filed a re-pin request and a PR rewriting the atlas's
  report on his own system, carefully and accurately. Precedent recorded: check
  what is already published first (most of it was, in more detail), fold in only
  what survives independent reading at the pin and restate it in the atlas's
  voice, and close rather than merge — the patch was against a superseded
  baseline, indented two `matrix:` keys three spaces so they would not parse,
  and, decisively, a reader cannot tell afterwards whose words a report carries.
  Both threads answered publicly; outward-facing acts were confirmed first.
- [2026-08-19-there-is-no-ideal-memory-only-a-frontier.md](2026-08-19-there-is-no-ideal-memory-only-a-frontier.md) —
  Why the request for a page describing "the ideal memory — continuous learning,
  never forgets, max on all KPIs" produced the tensions page instead. Each third
  is refuted by the corpus: never-forgetting is the most-documented failure here,
  Engram Alpha fits an abstention line per graph because abstention is not free,
  and two systems found and deliberately cut the loop where retrieval certifies
  its own outputs. Also the second argument — an ideal-memory page would fight
  `/build/`'s "the correctable stack is not the default" — and the two decisions
  inside the page that keep it from reading as an argument for building nothing.
- [2026-08-19-measure-the-chrome-before-restyling-it.md](2026-08-19-measure-the-chrome-before-restyling-it.md) —
  "The nav bar is crowded" was a horizontal-scroll bug: eleven items plus the
  GitHub pill need 1,051px against a 1,240px header with the brand's 189px, so
  zero slack at the widest layout and the whole document scrolling sideways from
  ~1,300px down to the 760px breakpoint. The fix was sized from that arithmetic
  rather than guessed. Carries the accessibility trap — `.brand-mark` is
  aria-hidden, so `display: none` on the wordmark would have left the home link
  with no accessible name — and the observation that the real pressure is eleven
  top-level items, where the next fix is grouping rather than more shaving.
- [2026-08-18-the-gaps-were-placement-not-content.md](2026-08-18-the-gaps-were-placement-not-content.md) —
  Four outside reviews in one session (Qwen twice, Grok, Kimi) produced four
  accepted changes, and only one was missing content: the producer check. The
  other three were material the atlas already had, in a place the complaining
  reader had not reached — the rubric's "one language model's reading of code it
  did not run" was three weeks old and two clicks from the capability strip that
  needed it. Adds a second triage class beside the rendering one: when a review
  proposes something the atlas already does, ask where it is relative to what the
  reader was looking at. Also records why a page-wide "may be unwired" banner was
  refused — it would have been false, checked against all fifty reports the same
  day — and why maintenance verdicts, line-number evidence keys and a reference
  implementation stay declined.
- [2026-08-18-the-producer-check-and-a-corpus-audit.md](2026-08-18-the-producer-check-and-a-corpus-audit.md) —
  Declared-and-unwired is the atlas's most common finding and nothing in
  `add-memory-system` asked for the check; fifty-one reports carried one because
  someone thought to look. The step is now required, phrased as "find the
  producer" rather than "grep the callers", because the sharpest cases all have
  callers and fail on data flow. Auditing all fifty reports with an unwired claim
  against their marks: zero credit a mark to a mechanism they say has no
  producer, five state the withholding explicitly. Surfaces the
  missing-producer / stale-consumer distinction (OmniIntelligence) and a third
  shape from MindCache — a scope repair that fails into a `try` block. Carries
  the re-runnable method and its three false-positive classes.
- [2026-08-18-two-rules-for-one-field-and-then-none.md](2026-08-18-two-rules-for-one-field-and-then-none.md) —
  The A–Z index printed each system's identity three times on 279 of 301 rows.
  Two rules were written for when to print the slug; the first was wrong in both
  directions at once, the second was right, and then the field was deleted
  anyway. The lesson: a field needing a rule to decide whether to show it is
  usually a field that should not be shown, and the signal was in the first
  measurement. Also records the sort change it forced (by title, not by an
  invisible key) and three layout constraints worth not rediscovering — why not a
  `<table>`, why fixed column units, and why `layout: wide` exists.
- [2026-08-16-a-fork-a-successor-and-an-editor.md](2026-08-16-a-fork-a-successor-and-an-editor.md) —
  Three coding agents read and excluded. One of them, Cline, had been excluded on
  7 August with a re-entry condition attached, and the condition is checkable —
  which is the point of attaching one.
- [2026-08-14-two-long-context-papers-and-the-boundary-of-what-memory-is-for.md](2026-08-14-two-long-context-papers-and-the-boundary-of-what-memory-is-for.md) —
  Chroma's Context Rot report and the Oolong benchmark (arXiv:2511.02817), read
  and triaged — neither a memory system, both measurements that bound what a
  memory layer is for. Context Rot's LongMemEval result (every model family
  scores higher on a focused ~300-token prompt than the full ~113K conversation)
  is the empirical case for retrieval, stated as a measurement and made by a
  vector-DB vendor; Oolong is the aggregation half retrieval cannot help, where
  frontier models fail at 128K. Both say a bigger window is not the fix, and both
  are now cited on the benchmarks page. Also closes a loop: MemCP's hardcoded
  `test_context_rot.py` baseline traces to this real, measured phenomenon it
  asserts a constant for instead of running.
- [2026-08-14-a-coding-agent-whose-search-is-the-users-not-the-models.md](2026-08-14-a-coding-agent-whose-search-is-the-users-not-the-models.md) —
  Kimi Code CLI has cross-session full-text search over its session corpus,
  which is the DeepSeek Harness shape exactly — and it is out of scope where DSH
  is in, on one fact: DSH registers the search as model-facing tools, while Kimi
  Code's search is an app-server service for the UI and the agent's thirteen-tool
  registry has no recall tool at all. The human can search past sessions; the
  model cannot. The line between a searchable session corpus that is agent memory
  and searchable session history that is a product feature is whether the model
  can query it, and grepping the tool registry answers it faster than reading the
  storage engine. `contextMemory` is window management, `minidb` indexes sessions
  not beliefs, and `AGENTS.md` is generated once by `/init`.
- [2026-08-14-the-framework-that-explains-the-deepseek-correction.md](2026-08-14-the-framework-that-explains-the-deepseek-correction.md) —
  Cordis, the plugin runtime under DeepSeek Harness, has zero hits for recall,
  persist, storage, durable, embedding, vector, sqlite, database, forget or
  retrieve, and its loader's `write()` is a comment saying the tree is in-memory.
  The exclusion is trivial; the reason for reading it is that its design is why
  the DSH report was wrong. When capabilities are separately-mounted plugins with
  isolated service symbols, "implemented" and "present" become independent facts
  and nothing at the implementation site signals which. Proposes a three-step
  reading rule — find the shipped composition rather than the example one, grep
  it for the package, and check the config it passes rather than the component's
  schema default — and an explicit prompt for it in the report format.
- [2026-08-14-a-handoff-protocol-and-the-durable-thing-that-is-not-a-belief.md](2026-08-14-a-handoff-protocol-and-the-durable-thing-that-is-not-a-belief.md) —
  DeepJudge's Agent Handoff Protocol requires durable state as a normative MUST
  — a thread mapping, an idempotency result and materialised resources,
  committed atomically and retained at least 24 hours — and is still not memory,
  because a correlation identifier and a replay guard are not claims that can be
  wrong. The same call `showjihyun/bvwebchat` got, reached from the protocol side
  instead of the harness side, and the distinguishing question in both is not
  whether something survives but whether the surviving thing could be false.
  Keeps three mechanisms: the sharpest untrusted-input rule in the corpus, an
  idempotency-key-plus-request-fingerprint write guard that would give a memory
  store a conflict signal where it currently overwrites, and a normative
  deletion-completeness MUST. Also pairs its unrunnable fifteen-scenario
  conformance list against LangGraph's runnable one, which covers the wrong half.
- [2026-08-14-a-teaching-corpus-and-the-prior-art-it-was-citing.md](2026-08-14-a-teaching-corpus-and-the-prior-art-it-was-citing.md) —
  a thirty-notebook cookbook's reading list named 21 systems, 15 already
  reported, and the six that were left had been cited in 5 to 16 `content/`
  files each *before* anybody read them. The gap a `source_url` join cannot see
  is not an uncovered repository but a covered report leaning on an unread one,
  and a probe for it is proposed. Also reverses the 2026-08-09 disposition of
  `getzep/zep` — the row was correct that the engine is Graphiti and wrong to
  stop there, because the client repository is where the vendor keeps fifty
  committed LoCoMo runs. Records two arithmetic bugs of the same shape found in
  one sitting, both in metrics rather than stores, and the `--only` argument
  `screen_corpus.py` needs before a batch's own checkouts can reach the ledger.
- [2026-08-13-the-fourth-review-and-the-second-broken-diagram.md](2026-08-13-the-fourth-review-and-the-second-broken-diagram.md) —
  a fourth outside review opened with "the Mental Model table has completely lost
  its markdown rendering", quoting three edge labels from the PRO-LONG report's
  Mermaid diagram. Two further items asked for a rubric page and a pattern
  library that exist and sit in the nav of every rendered page. Two reviews now
  resolve the same way, which makes the delivery surface the finding: check the
  rendered artifact before answering a criticism of presentation, and the corpus
  before answering one of coverage. Also corrects the claim that PRO-LONG's
  missing test suite is buried in section 10 — it is in section 1, though as the
  closing line, which is the version of the criticism worth keeping.
- [2026-08-13-the-rubric-definitions-are-in-a-tooltip.md](2026-08-13-the-rubric-definitions-are-in-a-tooltip.md) —
  every report page already carries the seven mechanisms as marked chips with a
  legend distinguishing *assessed and carries none* from *nobody looked*. What
  does not arrive is the definitions: they live in `title` attributes, so they
  are invisible to a text extractor, a printed copy, Reader mode, a keyboard and
  a touch screen — which is why a reviewer could name all seven and still call
  the criteria a black box. Proposes linking each chip to a stable per-mark
  rubric anchor. Also records the correction: the first version of this note
  claimed the marks were absent, from a grep for the frontmatter keys on a page
  that renders the display names.
- [2026-08-13-enforce-where-the-writer-cannot-reach.md](2026-08-13-enforce-where-the-writer-cannot-reach.md) —
  a pattern page proposal with six candidate instances already in the corpus:
  an invariant enforced by the party it constrains is a policy, and one enforced
  where that party cannot reach is a mechanism. arc-code is the case with a
  before and after, PRO-LONG is the counter-case where the recorder is out of
  reach but the record is not, and the page's distinguishing test is adversarial
  — not "does the gate work" but "what happens when the constrained party goes
  around it".
- [2026-08-13-a-memory-type-axis-and-why-machinery-is-the-wrong-one.md](2026-08-13-a-memory-type-axis-and-why-machinery-is-the-wrong-one.md) —
  accepts that the atlas has no axis for *what kind of memory this is* and
  declines the reason offered for it. The eight families sort by how you would
  adopt a system, not by what it holds, so a seeded `memory_type` key is worth
  adding; but sorting by machinery would file daimon — the most complete deletion
  test in the corpus, achievable because it has no embeddings to compact — below
  the systems it beats on the axis the atlas cares most about.
- [2026-08-13-what-a-friction-column-could-actually-say.md](2026-08-13-what-a-friction-column-could-actually-say.md) —
  measures the four proposed reality-check columns against what 264 reports can
  already fill. The report format has required "does the agent block" and "what
  is the lag" since it was written, and 124 of 264 reports state the first: the
  gap is enforcement, not policy. Proposes fixing that before adding a column,
  then seeding `write_mode` and `setup` through the same labelled mechanism that
  back-filled `stack_*`, and keeping token overhead out of the matrix because no
  reading produces it.
- [2026-08-12-deletion-harness-level-1-and-level-2.md](2026-08-12-deletion-harness-level-1-and-level-2.md) —
  the implementation plan for the thirteen-step sequence. **Level 1** is the
  harness running against itself: an adapter Protocol, steps 1–10, and two
  reference stores where the validation criterion is that the leaky one fails
  *exactly* the four steps it was built to fail. **Level 2a** points it at Memory
  Compiler, chosen because it installs nothing and carries a falsifiable
  prediction — a 10-character canary should fail step 6 where a 12-character one
  passes, because its collision scan ignores values below twelve characters, and
  the spec's own default token sits exactly on that boundary. **Level 2b** adds
  steps 11–13 and replaces step 9's boolean with MythologIQ's four-way residue
  partition, which turns a step almost everything fails into one that
  discriminates. The fleet is explicitly not proposed, with reasons. Also records
  three defects in the published spec that only building surfaces.

- [2026-08-12-what-would-make-rollback-a-mark.md](2026-08-12-what-would-make-rollback-a-mark.md) —
  the rubric declined to score recoverability partly because almost nothing
  implements it. NeuraKeep ships a working undo and MythologIQ specifies rollback
  traceability, so the rarity argument expired and the limits section now says
  so. What never existed is a definition that discriminates: proposes one in
  three clauses — restored from a durable record of the prior state, reversible
  by a caller rather than by the database under it, and the reversal itself
  recorded — and refuses to adopt it before a corpus sweep, because a mark
  awarded on a loose reading is the `audit_log` failure repeated. Authority left
  alone, with the condition that would reopen it.

- [2026-08-12-the-harness-this-page-does-not-ship.md](2026-08-12-the-harness-this-page-does-not-ship.md) —
  the benchmarks page faults FiFA for releasing no code and AOEP-v0 for
  describing an unshipped harness, then specifies a thirteen-step deletion
  sequence and ships neither. The asymmetry is real, the acknowledgement has
  landed in §9, and this is the build: one file, standard library, an adapter
  Protocol, and — the part that matters — a deliberately leaky example store that
  *fails* steps 5–8, because a harness shipped with only a passing fixture proves
  nothing about whether its assertions discriminate. No certificate, no
  scoreboard, no pass list.

- [2026-08-12-which-marks-could-be-execution-grounded.md](2026-08-12-which-marks-could-be-execution-grounded.md) —
  answers "run the code, don't just read it" with evidence the project generated
  without noticing: five of the last nine systems had code executed during
  review, none needing a container and three needing nothing but an interpreter.
  The binding constraint is the seven-day cooldown, not tooling. Proposes three
  tiers recorded per mark — `read`, `reproduced`, `executed` — and one rule: where
  a mark rests on arithmetic that twenty lines can falsify, reproduce it. Also
  corrects two framings, including that "a 71% failure rate on re-audits" is one
  incident on one capability rather than a rate.

- [2026-08-12-the-cheapest-of-the-ten-metrics.md](2026-08-12-the-cheapest-of-the-ten-metrics.md) —
  of the ten axes in the scorecard, write-to-readable lag needs a clock and two
  calls. About forty lines against the deletion sequence's existing adapter, with
  the four design points that are the whole value: a unique token per trial so
  the probe cannot measure a cache, polling `prompt_prefix` rather than the
  store's read API because the question is when the memory reaches the *model*,
  p50/p95/max and never a mean because the distributions are bimodal by
  construction, and a timeout treated as a result rather than an error.

- [2026-08-12-the-atlas-read-without-javascript.md](2026-08-12-the-atlas-read-without-javascript.md) —
  **the delivery fix shipped 2026-08-13**; pre-rendering stays declined because
  it would add puppeteer to a build with no Node dependencies at all.
  An outside review reported floating `no`/`yes`/`a test fails` text and missing
  linked documents on the build page. Both were artifacts of reading it without
  JavaScript and with anchors stripped: the text is a Mermaid flowchart's edge
  labels, and the three "missing" documents are hyperlinks in the sentences that
  name them. Worth a note anyway, because `check_mermaid.py` requires a diagram
  in every system report, so all 260 report pages degrade to raw `flowchart TD`
  source for readers who execute no JavaScript — a growing share. Proposes
  build-time SVG rendering, a one-line text alternative per diagram, and a guard
  that pins the current behaviour.

- [2026-08-10-the-loop-this-atlas-keeps-naming-has-a-number-now.md](2026-08-10-the-loop-this-atlas-keeps-naming-has-a-number-now.md) —
  arXiv:2608.00017 measures the self-grading feedback loop this atlas keeps
  asserting from code: wrong episodes get inflated scores, the inflation couples
  to reuse, and agent error rises with retrieved-set corruption at a measured
  slope. Its Error-Independence Assumption says a stronger judge from the same
  family cannot fix it, which is the argument behind Engram Alpha's *"exposure
  doesn't validate"* arrived at independently. No report: the repository the
  paper twice says holds its code, traces and result files returns 404, while
  the author's account is active with 48 other public repositories. Worth
  re-checking — if it appears, this is a report.

- [2026-08-09-a-tokenomics-list-triaged.md](2026-08-09-a-tokenomics-list-triaged.md) —
  73 open-source projects from a token-cost list, read against the memory bar in
  fifteen batches. The starting hypothesis was that a cost corpus would be a poor
  place to find memory systems and a plausible place to find the cache measurement
  [cache-preserving injection](../content/patterns/cache-preserving-injection.md)
  says nobody publishes. It was wrong in the more useful direction: **eight**
  memory systems, none of them filed under *Memory* — Serena is for code
  navigation, Ollama for local inference, gh-aw for CI, vLLM Semantic Router for
  routing, and every one has memory underneath. The measurement turned up too, in
  llmtrim, from a project that found the problem by watching its own compression
  savings leak. Plus a new scope boundary (the semantic response cache, argued
  from GPTCache's hit check refusing to serve a session its own answer), six
  pattern pages changed, and the method finding that matters: an awesome-list entry
  describes what a project is *for*, and a memory system is usually not what its
  host is for — so nothing but a grep of the source would have found any of these.
- [2026-08-09-a-phased-program-and-where-to-abandon-it.md](2026-08-09-a-phased-program-and-where-to-abandon-it.md) —
  sequences the four notes below, and three results came out of it that none of
  them could see alone. The cheapest item is a prerequisite for the other three,
  because every later artifact cites the state of the atlas and without a tag they
  all cite a moving target. Local execution is safe in exactly one phase —
  against this project's own kernel and its paired broken arm — which is also the
  phase that decides whether the conformance line is real, and it is allowed to
  fail: a test that cannot be made to fail on the broken arm is removed rather
  than shipped with a caveat. And phase 3's gate is not a submission but a
  finding: if reading the adapter added nothing to reading the log, the burden
  inversion bought nothing and phase 4 must not happen. Written before any gate
  became inconvenient, because a program where each stage is justified by the next
  one is how phase 4 gets approved before phase 2 returned.
- [2026-08-09-the-conformance-run-the-atlas-does-not-run.md](2026-08-09-the-conformance-run-the-atlas-does-not-run.md) —
  step 2 of the eval-suite note is closed rather than deferred: running the
  deletion sequence means executing 238 checkouts, which contradicts the
  screening tool this project built to avoid executing checkouts. The rejection
  it reopens instead — "a `pip install` that nobody runs" — predicted a
  population's behaviour, and Verel, Perseus and Daimon each built an executable
  self-evaluation unprompted. So the burden inverts, and the design problem
  becomes what makes a self-run readable statically at a pin: the project's own
  public CI with an addressable log, a pinned commit, **the adapter committed
  upstream** because the dominant failure will be an adapter that passes by not
  testing, and a negative control per test in the same job — Daimon's placebo arm
  as a submission rule. The atlas reads the adapter, not the result. Plus the
  asymmetry that keeps it off a scoreboard: a submission is only ever evidence
  *for* a mechanism, because not running is not failing.
- [2026-08-09-seventy-one-repositories-from-an-outside-corpus.md](2026-08-09-seventy-one-repositories-from-an-outside-corpus.md) —
  Seventy reports written and pushed across seventeen batches from an outside
  candidate list. Every candidate in the tabulated list is now read and either
  written up or dispositioned in the note; nothing in the join remains
  unexamined.
- [2026-08-09-the-corpus-has-a-half-life.md](2026-08-09-the-corpus-has-a-half-life.md) —
  113 of 238 reports were read in the project's first six days and have not been
  touched since; the age distribution is bimodal, so the average report a reader
  lands on is much older than the project. Measured from `analyzed_at` with no
  network call, which is the point — upstream polling is the expensive path and is
  not needed to rank the queue. Two cheap proposals: a dated tag so a citation
  can name what it read, and the age delta surfaced at the point of reading — a
  number, not a freshness badge, because a badge needs a vocabulary that would
  assert fourteen days means the same thing for a project with four commits a
  month and one with four a day. Neither makes a report more true; they stop
  staleness being invisible, and the failure mode is a reader trusting an old
  report, not distrusting one.
- [2026-08-09-the-receipts-the-atlas-cannot-produce.md](2026-08-09-the-receipts-the-atlas-cannot-produce.md) —
  the case for a downstream-changes page is not influence, it is that on 4 August
  a review claimed five maintainers merged against the rubric and the atlas could
  not check a factual claim about itself. The data is already in the `## History`
  sections but unevenly: Perseus, memsem and Verel are explicitly attributable
  and Daimon is not, which is the row that matters because an enthusiastic page
  would assert causation the report never claimed. Generated from a frontmatter
  field rather than hand-kept, attribution labelled explicit/inferred/unknown,
  atlas retractions carried as rows too — and a firewall enforced in `scripts/`,
  because responsiveness is adoption evidence wearing a lab coat.
- [2026-08-09-widening-and-its-falling-marginal-value.md](2026-08-09-widening-and-its-falling-marginal-value.md) —
  the incumbent option held to the same scrutiny as the three proposals written
  beside it. Seventy reports in one day is the project's best throughput and also
  seventy new pins in a queue nobody re-reads; recent batches keep converging on
  conclusions the corpus already held, which is a real result and the signature of
  a covered space. The bar worth applying to a candidate: worth the pin if a
  *pattern* might move, not if a report can be written — which two candidates
  currently clear, the symbolic lineage and MemState on Kuzu.
- [2026-08-09-the-constant-was-fixed-for-thirty-arms.md](2026-08-09-the-constant-was-fixed-for-thirty-arms.md) —
  60 is the only RRF constant anywhere in this corpus, and it was fixed in a
  pilot over thirty configurations of one search engine, on a curve flat from 30
  to 100, with the paper itself saying the choice "was not critical" — 80 scored
  higher in the same table. Bruch et al. (TOIS 2023) is the source that settles
  it: one constant *per arm*, swept 1–100 over nine datasets, where a convex
  combination of normalized scores beats RRF (60,60) on all nine, a symmetric
  (5,5) transfers, and in-domain per-arm tuning collapses out of domain — so
  "sweep it" is not sufficient advice. At k=60 one arm's whole top-60 rank signal
  spans 1.967×, but the value of cross-arm agreement is 1 + (k+a)/(k+b), not a
  flat 2×, and candidate depth and arm correlation sit outside the arithmetic
  entirely. Latent Terms supplies the premise's missing citation — BM25 0.9490
  against Contriever 0.0265 on LIMIT — narrowly: its recovery to 0.5100 takes a
  new autoencoder over token activations and a second inverted index, not a
  rescoring of the embedding.
- [2026-08-09-the-papers-the-reports-did-not-read.md](2026-08-09-the-papers-the-reports-did-not-read.md) —
  audit prompted by the SESA report saying "no ablation is present" when the
  README cited a paper whose Table 3 ablates the mechanism at 2.7 points. Eleven
  paper-backed systems checked against their own READMEs; none of the eleven
  reports cites the paper. Only one carried an unscoped absence claim —
  MemoryOS — and reading its paper strengthened the claim rather than breaking
  it. Both agent skills now require a citation grep before section 10, and the
  distinction the audit turns on: "no ablation" is a claim about the work, "no
  result is committed to this repository" is a claim about the artifact.
- [2026-08-09-the-database-people-arrived-at-the-same-four.md](2026-08-09-the-database-people-arrived-at-the-same-four.md) —
  a data-management vision paper (arXiv:2605.26252) derives this atlas's argument
  from the other side: four failure modes that match the four reported here, and
  six correctness conditions of which C2 is the rejected-value tombstone stated
  as a property and C4 is provenance-preserving forgetting. It proves append-only
  storage cannot satisfy C2. The tombstone page's "no shared vocabulary" clause
  was wrong and has been narrowed. Its prototype, MemState on Kuzu, is a
  screening candidate.
- [2026-08-09-a-mirror-that-agrees-to-forget.md](2026-08-09-a-mirror-that-agrees-to-forget.md) —
  `Untrivial-ai/agent-orchestrator` triaged and excluded on the
  harness-is-not-a-store boundary: sixty-five migrations, none of them holding a
  claim that could be false, and no memory claim anywhere in its own docs. Kept
  because it is a *derived copy* of a provider's chat history that treats
  upstream forgetting as an obligation — a rollback propagates through five
  statements in one transaction, reaching a queue, rows written by an older
  build, a recomputed summary column and a blocked approval, with the read side
  filtering discarded prose and refusing to renumber the sequence. The
  enumerated-derived-copies discipline the atlas asks for, from something that
  never claimed to remember. Two smaller mechanisms: `applied_title` as a
  compare-and-set witness for auto-update-versus-human-edit, and compaction split
  into a timeline row plus a state column.
- [2026-08-07-three-coding-agents-and-where-their-memory-isnt.md](2026-08-07-three-coding-agents-and-where-their-memory-isnt.md) —
  `cline/cline`, `MoonshotAI/kimi-code` and `MoonshotAI/kimi-cli` triaged
  together and all excluded. Cline's Memory Bank, the most-cited memory in
  coding agents, appears in exactly two files and both are in `docs/` — it is a
  prompt plus the agent's ordinary file tools. Of the two Moonshot repos the
  interesting one is the one being wound down: `kimi-cli` ships `SendDMail`,
  agent-chosen time travel back to a context checkpoint with a note to its past
  self, which the TypeScript successor did not carry over. What `kimi-code`
  built instead is a compaction prompt that asks the model to carry unverified
  claims through the summary *as* unverified. Second pass on `kimi-code`'s cron
  subsystem — durable, agent-authored, workspace-scoped, and still not memory,
  because a schedule is an intent that cannot be false — for two moves that
  transfer: re-enumerate from the store after a compaction instead of trusting
  the summary, and deliver expiry as a renewal offer rather than firing it
  silently. No runtime skill authoring in any of the three.
- [2026-08-07-a-harness-that-reinvented-the-tombstone.md](2026-08-07-a-harness-that-reinvented-the-tombstone.md) —
  `os-factory/har` triaged and excluded — every one of its twelve tables is about
  runs, and `recall`/`remember`/`forget`/`embedding`/`vector` appear twice in
  16,065 lines. Recorded anyway for three mechanisms: a rejected-value tombstone
  in its repository registry whose refusal propagates back to the sync loop that
  would re-assert it, a validation record keyed by the tree hash it is about so
  it invalidates itself, and a propose-review-apply gateway over `AGENTS.md` with
  a floor on how much of the file a refresh may delete.
- [2026-08-07-the-goedel-machine-lineage.md](2026-08-07-the-goedel-machine-lineage.md) —
  Schmidhuber's 2003 Gödel machine, the Huxley-Gödel Machine that approximates it,
  and its implementation triaged: what persists there is a tree of git commit ids
  and their utility measures, read by the search loop and by nothing at task time,
  so it is an optimizer's state rather than a memory. Two things worth taking
  anyway — judging a node by what its descendants achieve, and getting undo for
  free by versioning every self-modification as a commit.
- [2026-08-07-the-atlas-as-an-agent-protocol.md](2026-08-07-the-atlas-as-an-agent-protocol.md) —
  a seven-step proposal to turn the atlas into an agent workflow, triaged: the
  premise is right and five of its "missing" pieces are already written down, so
  the gap is packaging rather than knowledge. A root `AGENTS.md` is built; the
  build brief, test ids and a `use-the-atlas` skill were then built the same day;
  a manifest field carrying judgements nobody made, and the phrase
  "conformance", are declined on precedent.
- [2026-08-08-the-guidance-was-already-in-context.md](2026-08-08-the-guidance-was-already-in-context.md) —
  four process failures in one session, all of the same class: the instruction
  existed, was correct, and was already loaded. A standing commit authorization
  asked around three times, the repository's own skills not invoked, a negative
  control run with `git checkout` in the working tree that destroyed four
  uncommitted fixes, and a claim published backwards from a rendering when the
  paper shipped its source. Companion to the methodology hazards note, which
  covers failures of evidence rather than of following guidance — and the point
  is that the build stayed green through all four.
- [2026-08-08-an-audit-layer-that-shows-one-trajectory-twice.md](2026-08-08-an-audit-layer-that-shows-one-trajectory-twice.md) —
  a task-synthesis paper's project site publishes an "Audit layer" inviting the
  reader not to trust its metrics; read in a browser, the failed baseline and the
  successful run are byte-identical at every turn that renders, every turn past
  the baseline's length is blank on the successful side, and the rubric scores
  94.5/100 with every criterion at the same confidence citing the same three
  turns. They are fixtures behaving as fixtures — the gap is the sentence they
  are published under. A third variant of a failure the atlas already names
  twice, and the most persuasive, because it looks like finished work. Revised
  the same day against the paper's LaTeX source, which corrected one claim this
  atlas had backwards and found the paper's flagship RL score stated as 49.44 in
  its table and abstract and 46.07 in its conclusion.
- [2026-08-08-what-the-negative-eval-mark-actually-counts.md](2026-08-08-what-the-negative-eval-mark-actually-counts.md) —
  all 37 mark-holders re-read against the rubric's own wording after a review
  argued the mark had drifted: 27 assert about a read path, 20 about a value and
  7 about a boundary, while 10 keep material out of a projection, a preamble, a
  summarization, a file or a write. One report asserts the mark and cites no case
  at all. The flags stay at 37 and the split is published instead.
- [2026-08-07-the-strong-form-tombstone-subset.md](2026-08-07-the-strong-form-tombstone-subset.md) —
  the nine mark-holders re-read against the pattern page's own definition: five
  refuse the write, two are durable only because nothing reads the rejection and
  the key happens to be the value, one suppresses at read, one is all three at
  once. Also found the pattern page contradicting the Daimon report on
  normalization for six days, and wrote the ninth holder's missing entry.
- [2026-08-06-rare-mechanisms-and-useful-inversions.md](2026-08-06-rare-mechanisms-and-useful-inversions.md) —
  the mechanisms this corpus holds once, each labelled with what kind of claim it
  actually supports and what the nearest prior art is. Written first as a novelty
  inventory, which verified rarity in an opportunistic corpus and then upgraded it
  into field-level originality; an outside review took that apart and the
  retractions are tabled at the bottom — including the framing the atlas thought
  it coined, which the literature had already named *false success*.
- [2026-08-06-the-count-claim-checker.md](2026-08-06-the-count-claim-checker.md) —
  thirteen stale numerators in one day, the checker that now guards them, the one
  it missed that a reader found the same evening, and the branch added to catch
  that which then shipped with no control of its own. Every stale number sat
  beside generated ones that were correct, which is what makes the class
  dangerous.
- [2026-08-06-four-arc-agi-3-harnesses-converge-on-the-same-memory.md](2026-08-06-four-arc-agi-3-harnesses-converge-on-the-same-memory.md) —
  Tycho, Retrodict, Schema and VISTA independently put an append-only record in
  charge and the model's own notes on probation — and why a third-party
  scorecard makes a whole family of claims checkable.
- [2026-08-06-a-harness-whose-traces-are-published-and-whose-code-is-not.md](2026-08-06-a-harness-whose-traces-are-published-and-whose-code-is-not.md) —
  VISTA: no source, 320 MB of run traces, and the whole memory surface
  reconstructed from them — plus the shrinking-note finding that inspection
  refuted.
- [2026-08-06-a-paper-and-its-official-implementation.md](2026-08-06-a-paper-and-its-official-implementation.md) —
  Cognitive Weave: a paper claiming 34% and 42% over MemGPT, A-MEM and Mem0,
  and an official implementation whose title mechanism is an unchecked To-Do
  item — plus why the To-Do list is the first thing to read.
- [2026-07-28-atlas-kernel-proposal.md](2026-07-28-atlas-kernel-proposal.md) —
  a reference implementation of the four-pattern minimum stack, plus the paired
  broken configuration that proves each failure mode.
- [2026-07-28-executable-eval-suite.md](2026-07-28-executable-eval-suite.md) —
  turning the deletion and contradiction tests into runnable code, and why the
  subset framing matters more than the harness.
- [2026-07-28-pattern-cookbook.md](2026-07-28-pattern-cookbook.md) —
  a copy-pasteable artifact per pattern, in priority order, with the trap.
- [2026-07-28-editorial-backlog.md](2026-07-28-editorial-backlog.md) —
  prose de-duplication, the measured/claimed axis, and re-analysis priority from
  the first freshness run.
- [2026-07-28-refusal-as-a-lens.md](2026-07-28-refusal-as-a-lens.md) —
  systems converge on architecture and diverge on what they refuse to do; ten
  grounded cases and what to do with the observation.
- [2026-07-28-research-questions.md](2026-07-28-research-questions.md) —
  six questions the committed corpus can answer with no new reviews.
- [2026-07-28-methodology-hazards.md](2026-07-28-methodology-hazards.md) —
  how this review process fails, including the two that already published wrong
  claims, and the best-evidenced one: a grep scoped to the wrong files returns
  exactly what a real absence returns, caught three times in one assessment and
  twice pointing at a criticism; and the 294 corpus-scoped superlatives nothing
  in the build has ever checked.
- [2026-07-28-symbolic-prior-art.md](2026-07-28-symbolic-prior-art.md) —
  belief revision, truth maintenance and BDI belief bases are absent from the
  atlas's lineage, and whether that is an omission or a real discontinuity is
  unresolved.
- [2026-07-28-pattern-gap-analysis.md](2026-07-28-pattern-gap-analysis.md) —
  an external 20-pattern list checked against the library; the real gap is that
  the comparative report names 29 recurring patterns and only 17 became pages.
- [2026-07-29-memory-survey-forms-functions-dynamics.md](2026-07-29-memory-survey-forms-functions-dynamics.md) —
  the field's 107-page survey of itself read against the atlas; the corpora
  overlapped by ten systems of sixty-three, the survey's vocabulary does not
  contain the atlas's central mechanism, and all eleven of its unreviewed
  framework candidates were then triaged — nine became reports and four corrected
  claims the atlas had published.
- [2026-07-29-what-survives-encryption.md](2026-07-29-what-survives-encryption.md) —
  a design note rather than a review: a model needs plaintext, so the client is
  the boundary; similarity search is the only operation that breaks; and
  crypto-shredding plus a blinded-fingerprint tombstone is the only answer this
  corpus offers to propagated copies.
- [2026-07-29-memorypapers-against-the-atlas.md](2026-07-29-memorypapers-against-the-atlas.md) —
  200 papers with a security category the surveys lack; A-MemGuard writes a
  rejected-value lesson it never persists, MemMachine is an unreviewed system in
  scope, and a site claiming weekly updates carries a title retired in June.
- [2026-07-29-a-coherence-coordinator-not-a-memory-system.md](2026-07-29-a-coherence-coordinator-not-a-memory-system.md) —
  Cohexa-ai/agent-coherence read at a pinned commit and excluded as a system:
  a coherence coordinator rather than a memory store, recorded in overview.md,
  with one claim that does not hold named in the note.
- [2026-07-29-a-reading-list-triaged.md](2026-07-29-a-reading-list-triaged.md) —
  a nine-item recent-papers list worked end to end; four surveys link one
  repository between them, no report was added, and three published atlas claims
  changed anyway.
- [2026-07-29-security-research-names-the-column.md](2026-07-29-security-research-names-the-column.md) —
  a security survey derives four of the atlas's capability columns from threat
  models, gives deletion durability a formal definition, and marks it "no
  existing literature"; the OWASP guard it links implements four of its five
  primitives and quarantines rejected values it never consults again.
- [2026-07-29-the-forgetting-benchmark-in-a-bibliography.md](2026-07-29-the-forgetting-benchmark-in-a-bibliography.md) —
  a third consolidated benchmark list with the same vocabulary gap, and the one
  paper that does score deletion compliance — found in its citations, listed in
  no benchmark table, releasing no code, with an abstract that contradicts its
  own results table.
- [2026-07-29-selective-forgetting-that-is-not.md](2026-07-29-selective-forgetting-that-is-not.md) —
  two surveys call MemoryAgentBench's fourth competency *selective forgetting*;
  the repository calls it conflict resolution, and its dataset keeps both values
  and hands the recency rule to the model in the prompt.
- [2026-07-29-the-other-agent-memory-atlas.md](2026-07-29-the-other-agent-memory-atlas.md) —
  a different public project with the same name; a link check of its 122 sources
  and what a confidence score determined entirely by one other column is worth.
- [2026-07-30-a-review-that-found-the-undisclosed-method.md](2026-07-30-a-review-that-found-the-undisclosed-method.md) —
  a reader reconstructed how the reports are written from reading them, stated it
  in passing, and was right about a thing the atlas had never disclosed; plus
  three suggestions declined and one claim pushed back on.
- [2026-07-30-two-ai-reviews.md](2026-07-30-two-ai-reviews.md) —
  every checkable claim in two favourable reviews held except the one given the
  authority of a direct quotation, which is not in the atlas; plus the field's
  most-cited survey, closed out, whose companion repository links no code and
  whose first author's own memory library has no persistence layer.
- [2026-07-30-twenty-suggestions-triaged.md](2026-07-30-twenty-suggestions-triaged.md) —
  a 20-item list of "missing" systems checked against the corpus; five already
  reviewed, five closed and unreachable for the third time, six new, and the two
  entries the list hedged hardest on were the two with the most to point at.
- [2026-07-30-a-reddit-thread-triaged.md](2026-07-30-a-reddit-thread-triaged.md) —
  the first external input that had not read the atlas, converging on the write
  path anyway; one under-covered idea (authority as precedence, one
  implementation), one gap with no occupant (failure-driven step repair), and a
  star-velocity argument that is the best external case yet for the rule against
  citing adoption as evidence.
- [2026-08-03-the-layer-below-delete.md](2026-08-03-the-layer-below-delete.md) —
  a review whose four headline proposals were all already decided, one of them by
  shipping the page it asked for; its buried critique sent this project into four
  vector engines, where the leak it alleged does not happen and two failures it
  did not allege do — deleted embeddings persisted verbatim to the index file,
  and a documented seven-day floor on erasure — which is a layer below where
  every `update_delete` claim in the corpus stops.
- [2026-08-03-a-null-control-and-a-drifted-list.md](2026-08-03-a-null-control-and-a-drifted-list.md) —
  two findings from a re-read that changed no mark: the published
  repositories-inspected list had drifted on three systems and every one of them
  was a system this project had re-reviewed, with the nine-line check that would
  have caught it still unwritten; and Daimon now ships the placebo arm the
  benchmarks page argues nobody has, having used it to refute one of its own
  shipped features and to say which way its conservatism cut.
- [2026-08-03-the-log-and-the-projection.md](2026-08-03-the-log-and-the-projection.md) —
  a claim published the same morning, checked and half retracted: CQRS is absent
  from the corpus but event sourcing is not, and the atlas writes the name down
  only when a README hands it over — twenty reports describe a canonical store
  with a rebuildable projection without once calling it that; the distinction
  worth taking from the literature is that "rebuildable" means two different
  things depending on whether a model is in the replay path.
- [2026-08-03-two-lists-of-candidates-triaged.md](2026-08-03-two-lists-of-candidates-triaged.md) —
  a curated recommendation and a raw GitHub search dump submitted together; six
  of thirty were already reviewed, all thirty were reachable for once, and the
  three systems named as worth trying scored bottom of the batch on correction,
  scope and tests while the two strongest sat in the list that was waved past —
  the sharpest instance yet of the rule against citing stars, since the starred
  recommendation is the weakest candidate on mechanism in the same message.
- [2026-08-04-the-superlative-audit-first-pass.md](2026-08-04-the-superlative-audit-first-pass.md) —
  the 294 corpus-scoped superlatives split into ten mechanically checkable count
  claims and 284 judgements; four of the seven real counts were stale, and one
  was caused an hour earlier by the regex sweep that bumps denominators to
  satisfy the build while leaving numerators nobody checked — a stale figure
  wearing a current denominator reads fresher than it did before the fix.
- [2026-08-04-the-compare-page-as-a-tool.md](2026-08-04-the-compare-page-as-a-tool.md) —
  the first external review that measured anything rather than arguing about
  content; all seven measurements verified, the rows made attributable again by
  pinning the first column, the consent banner's thumb taken off the scale, and
  the normalized-badge redesign declined for a stated reason — badges need a
  vocabulary the atlas refuses to invent, and the seven columns that have one are
  already filterable on a page two reviewers failed to find.
- [2026-08-04-nine-repositories-triaged.md](2026-08-04-nine-repositories-triaged.md) —
  nine URLs checked: four candidates, five refused, and two of the refusals on
  grounds already written down — a graph database is a backend the corpus reads
  as a shared dependency rather than reviews, and 310,000 lines of client around
  a hosted service is not inspectable code. Five of eight clones carry no licence
  file at all, which is a caveat to state in section 1 rather than a reason to
  skip.
- [2026-08-04-automating-re-analysis.md](2026-08-04-automating-re-analysis.md) —
  a proposal for scheduling re-reads at 147 systems, arguing that the gap is
  prioritisation rather than detection since `check_freshness.py` already exists.
  The strongest signal is a maintainer who has turned up in the Discord or
  answered a report before — engagement observed rather than proxied, so it is a
  tier rather than a term, with the privacy and stale-list constraints that come
  with a hand-kept map of people. Stars belong in the scheduler and nowhere near
  a report, behind an enforced firewall; they are a weak proxy for the same thing
  and should damp a tier-2 score built on drift and appendix-touch rather than
  drive it. The
  queue should rank on expected value **per unit cost**, because re-verifying a
  project that ships an assertion gate costs one command. And the thing to build
  first is not automation at all: commit the demonstration behind every mechanism
  claim to `demos/<slug>/`, because an upstream's accurate commit message is not
  a claim about what remains.
- [2026-08-04-three-repositories-and-a-harness-that-is-not-memory.md](2026-08-04-three-repositories-and-a-harness-that-is-not-memory.md) —
  three URLs, one report: Nova AI calls no model at all, gates every knowledge
  write on a spoken question, quarantines corrections from its curated training
  set — and still never built a delete, which is weak evidence that the
  correction asymmetry is not about LLMs. The two refusals are chat apps whose
  substance is a Claude Code harness beside them, and the closer one keeps
  HMAC-signed cross-session state it can correct; refused anyway, because a phase
  is not a claim that can be wrong. A harness that persists is not a memory that
  believes. The sweep also found the repository count wrong by four, in a
  sentence that carried three vintages at once.
- [2026-08-04-a-third-review-and-the-second-invented-quotation.md](2026-08-04-a-third-review-and-the-second-invented-quotation.md) —
  a favourable Gang-of-Four comparison checked line by line: the intersection and
  stack arguments are read correctly and seven pattern names are quoted right,
  but the closer claims five maintainers merged code against the rubric and no
  report, verdict or note records a single one — the only adoption the atlas can
  evidence is RainBox, its own repository. Two of three reviews now invent their
  final sentence at the point of maximum claimed evidence, which makes the error
  location predictable rather than anecdotal.
- [2026-07-28-declined-proposals.md](2026-07-28-declined-proposals.md) —
  suggestions considered and rejected, with the reasoning and what would change
  the decision.

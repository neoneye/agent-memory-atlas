# Notes

Working documents that are **not part of the published site** — proposals,
backlog, and decisions with their reasoning. `scripts/build_site.sh` only reads
`content/`, `site/`, `assets/` and `templates/`, so nothing here is rendered or
clobbered by a build.

Convention: `YYYY-MM-DD-{name}.md`, dated when the note was written rather than
when the work happens.

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

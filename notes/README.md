# Notes

Working documents that are **not part of the published site** — proposals,
backlog, and decisions with their reasoning. `scripts/build_site.sh` only reads
`content/`, `site/`, `assets/` and `templates/`, so nothing here is rendered or
clobbered by a build.

Convention: `YYYY-MM-DD-{name}.md`, dated when the note was written rather than
when the work happens.

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
- [2026-07-28-declined-proposals.md](2026-07-28-declined-proposals.md) —
  suggestions considered and rejected, with the reasoning and what would change
  the decision.

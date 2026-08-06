# Rare mechanisms and useful inversions — and what a novelty claim would take

**Status:** second version, rescoped after review. The first was titled *What is
actually new here*, and it did what its title promised: it verified **rarity
inside an opportunistic corpus** and then upgraded that into **field-level
originality**, which is a different claim resting on evidence nobody gathered.
An outside review (Codex, 2026-08-06) took it apart claim by claim. Most of the
hits landed, four were checkable and all four checked out, and the corrections
are recorded in Part 4 rather than quietly absorbed.
**Origin:** a plain question — *what are the most novel ideas in the atlas?* —
which the corpus can partly answer and no page assembles.

## What this note can and cannot claim

The first version stated three tiers of novelty claim and then tagged no entry
with which one it was making, so "unique in these 155 repositories", "the atlas
named it" and "the field does not have this" blurred into one voice. Every entry
below now carries a label:

| Label | Means |
| --- | --- |
| **Corpus-unique** | No other implementation found in the 155 pinned reports. A statement about this corpus, at these commits. |
| **Rare in corpus** | A handful of instances, counted. |
| **Atlas coinage** | The atlas named a thing that already happens. The name is the contribution; the phenomenon is not new. |
| **Adaptation** | An established mechanism from another field, applied to agent memory. The adaptation may be new; the mechanism is not. |
| **Prior art unsearched** | Nobody has looked outside this corpus. Most entries are partly this. |

**The limit that governs all of them.** This corpus is opportunistic — systems
encountered, suggested, or found while looking for the others — and it holds only
inspectable code. "No other implementation found here" is therefore compatible
with the mechanism being ordinary practice in closed systems, in the literature,
or in repositories nobody sent. **A real novelty claim needs a literature search
per mechanism, and this note does not contain one.** Where an adjacent prior art
is named below it is named from ordinary knowledge, not from a survey — which is
enough to *deflate* a novelty claim and not enough to establish priority either
way.

The atlas has a standing hazard for exactly this shape:
[none found is a claim about a search](2026-07-28-methodology-hazards.md). The
first version applied it to repositories and then broke it on the literature.

## Part 1 — Two contributions that survive the scoping

### The rejected-value tombstone — *atlas coinage, plus a working hypothesis*

**What it is.** A refusal keyed on the **value**, normalized, consulted on the
*write* path, so a later extraction proposing the same value is refused before it
can become active — as opposed to hiding a row, which stops a reader seeing it
and does nothing to stop a writer recreating it.

**What the atlas can support.** That this is a mechanism worth naming and asking
every system about, and that asking it separates systems that otherwise look
alike. The rubric mark is carried by **9 of 155**.

**What it cannot support, and the first version did.** The definition above is
the *strong* form. The nine are the **broader capability mark**, and the
[pattern page](../content/patterns/rejected-value-tombstone.md) itself records
that the population includes read-path suppression, at least one holder where the
behaviour appears to be a side effect, and one keyed on exact text rather than a
normalized value. Defining the strict mechanism and then attaching the broad
count to "it" is a definition/count mismatch. **How many of the nine implement
the normalized write-path form has not been re-derived** — that is a re-reading,
and until someone does it, the honest sentence is "nine earn the mark; a smaller
subset implements the form described here."

**On the field-level claim.** The first version rested it on three tokens absent
from one survey ([arXiv:2512.13564](https://arxiv.org/abs/2512.13564): *tombstone*,
*rejected*, *negative*, with "verifiable forgetting and auditable updates" listed
as future work on p. 75). Three missing tokens in one document do not establish
absence from a field — that is the atlas's own hazard, committed against the
literature instead of a repository.

What genuinely strengthens it is a *second, independent* document, and the atlas
already has one: the OWASP-linked security survey read in
[security research names the column](2026-07-29-security-research-names-the-column.md)
derives the capability from threat models, defines deletion durability formally,
and marks it **"no existing literature"** — its own judgement, not the atlas's.
Two documents converging is a working hypothesis worth publishing under that
name. It is not a proof, and the difference is the whole subject of this note.

### The layer below delete — *method extension; prior art unsearched*

**What it is.** The one finding that leaves the repository under review, to ask
what the storage engine does with a vector after the memory system's `delete`
returns. Four engines read at pinned commits: pgvector, Chroma with its hnswlib
fork, Qdrant, LanceDB.

**What it found.** The vector is not returned by search in any of the four — the
failure most often assumed does not happen. The index *degrades*: a soft-deleted
node keeps being traversed and never returned, so recall drops for the surviving
memories, a cost paid specifically by the systems that correct most. And the
embedding survives — hnswlib's own comment says `markDelete` "does NOT really
change the current graph", `saveIndex` writes the deleted vector to the index
file verbatim, `unmarkDelete` restores it; LanceDB documents a seven-day floor as
a feature. pgvector's `VACUUM` zeroes the element, which is what makes the other
three a choice rather than a law.

**The case that makes it land.** `memory-project` documents `purge()` for
"something that should never have been recorded in the first place (e.g.
accidentally jotted sensitive content)". It is `col.delete(ids=[doc_id])` on
Chroma. The function written for secrets has the least complete erasure, and the
memory system is faultless — it issued exactly the right call to its store.

**Not a novelty claim.** Reading a dependency's source is ordinary engineering,
and vacuum/compaction semantics are documented by the engines themselves. The
contribution is that a *comparative atlas* followed its own claim down one layer
instead of stopping at the API boundary, and that the four reports needed to do it
are now written down. **Dependency reach, stated reproducibly:** counting the
engine named in a report's `matrix.storage`, pgvector backs 15 systems, Chroma
12, Qdrant 11, LanceDB 5. (The first version quoted 16/11/11/6 with no definition
attached, and no current query reproduces those.)

### Three things the first version claimed and should not have

- **"The lying operation"** — a call that returns, increments a counter, appends
  an audit row, and does nothing. The phenomenon is real and the three fixes
  cited are real (agentmemory `#1132`, Hindsight `#3161`, Mastra `#17910`, all
  within four weeks). The *naming* is not the atlas's: the established terms are
  **false success** and **silent failure**, and
  [arXiv:2606.09863](https://arxiv.org/abs/2606.09863) — *From Confident Closing
  to Silent Failure: Characterizing False Success in LLM Agents*, June 2026 —
  studies exactly this, before the note was written. Verified by reading the
  abstract. What survives is the atlas-specific consequence: this failure
  undercuts every other question here, because "does a deleted value stay
  deleted" presupposes the delete happened, and an audit row for a mutation that
  did not occur is worse than no row. The test that catches it reads the store
  back and compares.
  Also corrected: "three finds in a month suggests the base rate is not low" is
  not a statistic. There is no sampling frame, no denominator and no independent
  selection. **The recurrence makes the class worth checking systematically** —
  that is all three cases support.
- **"None found is a claim about a search"** — sound research hygiene, not a new
  framing. It stays in the atlas as a *local rule* with two scars attached
  (waku-agent, Core Memory), which is what makes it operative here. It is not a
  contribution to anything.
- **Labelling a pattern library by evidential maturity** — old pattern-language
  practice. A candidate lacking enough instances is a **proto-pattern**, and the
  classical pattern form requires a **Known Uses** section for exactly this
  reason. The atlas's reporting/advocacy split is a rediscovery, and presenting
  it as an invention makes the project look unaware of the field it borrowed the
  word "pattern" from.

## Part 2 — Rare implementations and useful adaptations

Not a novelty ranking. Ordered by how consequential the mechanism is for memory
that can be corrected, with the corpus claim and the nearest prior art named for
each.

### 1. A durable record of a decision *not* to act, that is consulted — `agentic-context-engine`
**Corpus-unique.** The deduplicator pairs skills by cosine similarity and asks a
model to merge, update or keep them; a KEEP verdict is stored — the pair, the
reasoning, the similarity at the time — and checked in the detector's inner loop
(`detector.py:234`) before the pair is offered again. Without it, two skills that
look alike and are not look alike forever: every pass re-asks, and a
nondeterministic judge may answer differently each time.
**Prior art:** a domain-specific **cannot-link constraint**, mature in
constrained clustering; negative caching is the same instinct in another
setting. The adaptation is persisting a *model's* judgement as the constraint,
with its reasoning, inside a skill library.
**Limit:** a KEEP recorded on bad reasoning is now permanent, and nothing
re-opens it.

### 2. Authority withdrawn by measured evidence — `agentrecall-x`
**Corpus-unique.** `isNoiseCandidate` excludes a p0 human correction from its own
veto once it has been surfaced at least three times and honoured under 30% of the
time. Standing is granted, exercised, measured, and taken away.
**Prior art:** reputation systems and risk-adaptive access control revoke
standing on measured behaviour; the adaptation is applying it to a *human
correction* inside a memory store.
**Limit:** the precision driving the withdrawal is judged by the same loop
watching the agent, so the measurement is not independent of what it measures.

### 3. The policy version stamped on every decision it made — `memledger`
**Corpus-unique.** `memory.policy.yaml` canonicalised (RFC 8785), hashed, and the
hash recorded in every event the policy influenced, so editing the rules never
rewrites history.
**Prior art:** policy engines already do this — OPA decision logs carry the policy
bundle revision. This is good engineering imported into memory, not a new idea.
**Limit, and it is the report's own:** the dedup lookup filters
`status != 'deleted'`, so a fact the user deleted is re-created on the next
extraction. The most rigorous provenance model here, and the one query that could
act on it is written to skip it.

### 4. Two different fixes to the same audit hole — `palazzo`, `aura`
**Rare in corpus** (39 of 155 carry an append-only mutation audit; these two are
what the rest are missing). They are **not one mechanism**, and the first version
hid the difference behind one heading:
- **Palazzo** makes the audit entry a *precondition*: `log_strict` fails the
  delete when the write-ahead entry cannot be durably appended, and the entry
  carries a text preview so it says what was removed. **Prior art:** this is the
  write-ahead logging rule itself — log before you act — applied to a memory
  deletion rather than a transaction.
- **Aura** makes the log *tamper-evident*: a SHA-256 chain (`seq`,
  `content_hash`, `prev_hash`, `entry_hash`), so deletion shows as a sequence gap
  and insertion as a broken link. I ran `tests/test_audit_chain.py` — 16 passed,
  including modified-body, broken-link and deleted-entry. **Prior art:**
  hash-chained logs are a decades-old tamper-evident construction. Not the same
  construction as Certificate Transparency, which the first version implied: CT
  uses an append-only **Merkle tree** with signed tree heads and
  inclusion/consistency proofs ([RFC 9162](https://www.rfc-editor.org/rfc/rfc9162.html)),
  where Aura has a linear `prev_hash` chain. Same family, different guarantees —
  and it is *Lethe*, with its Merkle root, that sits closer to the CT shape.
**Limit:** Aura's chain is verified by Aura. Tamper-evidence without an external
witness detects a careless rewrite, not a determined one.

### 5. A signed acknowledgment that survives erasure — `aukora-kernel`, `lethe`
**Corpus-unique** in this shape. Aukora appends and fsyncs the receipt *before*
the row and chains the **content hash** rather than the plaintext. Lethe's
`purge_with_receipt` issues an Ed25519-signed statement that *"at time T, this
system acknowledged the deletion of records with these text hashes, when the
event log's Merkle root was R"*, and its purge reaches the lexical index by
construction (FTS5 deliberately not contentless).
**What it proves, precisely** — the first version overclaimed this worse than
anything else in the note. The receipt proves who signed, what log state they
committed to, and whether that log was later altered. It **does not** prove the
bytes are gone from the row store, backups, replicas, caches or exports; a system
can sign a false acknowledgment. Lethe's own report says *acknowledged*, and
lists as a risk that a purged text can be inscribed again because no write path
consults the receipt's hash.
**And "hashing the hash dissolves the tension" was glib.** A retained digest of
low-entropy content is confirmation-testable and may remain identifying, which is
the standing pseudonymization-versus-anonymization problem — see
[what survives encryption](2026-07-29-what-survives-encryption.md), where the
atlas already worked through the crypto-shredding version.
**Prior art:** tamper-evident logs, crypto-shredding, transparency receipts.

### 6. Verifying the agent's claim about its own authorship — `csm`
**Corpus-unique.** Each file change stored as a before hash, an after hash and a
lineage manifest of per-line SHA-256 counts; the file is re-read and the change
classified `active | partially_superseded | superseded | reverted` by comparing
surviving line multiplicities. No model, no diff library — line hashes and set
arithmetic.
**Why it matters:** [verify memory against its subject](../content/overview.md)
has four instances and three check claims *about* an artifact. This checks a
claim about the agent's own authorship of one — "I fixed the retry logic" in
session three, when session five rewrote the file. Every system here that stores
a session summary carries that risk.
**Prior art:** content-based change detection and line-provenance tracking
(`git blame`, MSR line-genealogy work).
**Limit, stated in the report:** survival in the file is a weaker claim than
correctness.

### 7. Stochastic recall — `loongflow`
**Corpus-unique** (the only non-deterministic retrieval here). Samples from a
Boltzmann distribution over scores, temperature driven by the store's *measured*
diversity and bounded on both sides, so a collapsed store loosens selection until
variety returns. It names a failure nobody else here does: deterministic top-*k*
with a slightly wrong ranker surfaces the same wrong memories forever.
**Prior art:** softmax/Boltzmann exploration and simulated annealing are
textbook; the adaptation is driving the temperature from a *diversity
measurement of the store*.
**Limit:** right only where recall informs what to try next, not what is true;
and it gives up reproducibility, with no seed or replay path.

### 8. Trust that gates capability — `omi`
**Rare in corpus** (28 of 155 record a discrete trust state; nearly all spend it
on ranking). `ACTION_POLICY` maps each epistemic status to permitted *uses*, and
`can_use_for_action` requires an `accepted` fact before an irreversible action —
so an unreviewed memory may answer a question with a disclaimer and may not send,
buy or delete.
**Prior art:** assurance-level and risk-based access control.
**Limit:** the grading is only as good as the status assignment feeding it.

### 8b. Labelling by consequence rather than by belief — `openhuman`
Separated from the entry above, because the first version merged them and the
merge was wrong. OpenHuman's report says plainly that it has no `Candidate`,
`Verified` or `Rejected`, that provenance is assigned at ingest and permanent,
and that it **does not model belief at all — it models blast radius.** So the
28-system trust-state denominator does not apply to it.
**Prior art:** this is an information-flow taint lattice, a well-established
model; the adaptation is applying it to memory content, with sanitization
deliberately unable to launder provenance.

### 9. Diffusion instead of traversal, and non-destructive entity resolution — `hipporag`
**Adaptation, corpus-unique here.** Personalized PageRank over the whole graph
replaces hop planning — seed weights divided by the entity's chunk count so hubs
do not dominate, damping 0.5 to keep relevance near the query's entities — and
similar entities are linked with weighted edges instead of merged. Graphiti's own
stated biggest risk is that entity-resolution mistakes reshape a large part of the
graph; a synonymy edge makes a wrong decision a weak spurious path.
**Prior art:** PPR is Haveliwala's, and the report credits the HippoRAG paper;
soft/probabilistic entity resolution is an established alternative to merging.
**Limit:** cost (PPR per query over the whole graph), attribution (no single
signal explains a ranking), and blur once the graph is dense.

### 10. Memory of what has not happened yet — `minecontext`
**Rare in corpus.** Event time separate from record time and **allowed to be in
the future**, which is what makes a commitment you have not kept yet expressible
at all. A schema forbidding future timestamps cannot represent it.
**Prior art:** prospective memory is a term from cognitive psychology, and
bi-temporal databases have permitted future valid-time since Snodgrass.

### 10b. Content embargoed until a date — `memento`
Also separated, for the same reason as 8b: Memento's own report says it is *not*
remembering to do something later, it is **content deliberately unreachable until
later**. `status = 'sealed'` with a `deliver_on` column keeps an entry outside
transcription, indexing and the timeline until a worker flips it.
**The transferable part is the enforcement**, not the feature: a state the whole
read path already respects, rather than a predicate every query must remember.

### 11. Four smaller ones, each cheap to copy
- **`echo-agent`'s `provenance_guard`** — the trust label belongs to the *write
  path* (`user_stated` 3, `consolidated` 2, `model_inferred` 1), so the model
  cannot nominate its own output as user-stated. Most trust models label the
  payload, which the labelled party can forge.
- **`empryo`'s git co-change affinity** — a memory attached to files that
  historically change together with what you are editing surfaces without
  matching a query token, entered at RRF rank 5 so it stays behind a direct hit.
  *Prior art:* change coupling, a standard mining-software-repositories signal.
- **`cosmonapse`'s failure vocabulary** — the only memory contract here that lets
  a backend decline, shed load, miss a deadline and roll back. Elsewhere the
  interface can only succeed or throw, so "I am overloaded" and "I have nothing"
  are the same answer. *Prior art:* RPC status taxonomies and backpressure.
- **`cambium`'s refusal to return an unearned pass** — its freshness tool prints
  `overdue=0 fresh=0` and concludes "NOTHING CHECKED… this is not evidence of
  freshness".

## Part 3 — Where they sit, counted

The first version asserted that *every* idea above sits after a memory has been
believed, which its own entries falsify — 7 and 9 are retrieval. The second
version counted, but counted **entries**, and four of those entries hold more
than one mechanism — so "seven of eleven" and "six of fourteen" had different
denominators built from different units. Third attempt, one **atomic mechanism**
per row:

| # | Mechanism | System | Phase | Refusal? |
| --- | --- | --- | --- | --- |
| 1 | KEEP-decision record, consulted | `agentic-context-engine` | Consolidation | yes |
| 2 | Veto withdrawn by measured precision | `agentrecall-x` | Use / act | yes |
| 3 | Policy hash stamped on every event | `memledger` | Audit / provenance | no |
| 4 | Audit entry as precondition for delete | `palazzo` | Delete | yes |
| 5 | Hash-chained receipt store | `aura` | Audit / provenance | no |
| 6 | Receipt fsynced before the row, chained on content hash | `aukora-kernel` | Delete | no |
| 7 | Signed purge acknowledgment | `lethe` | Delete | no |
| 8 | Line-multiplicity authorship check | `csm` | Verification | no |
| 9 | Boltzmann-sampled recall | `loongflow` | **Retrieval** | no |
| 10 | Status gates permitted uses | `omi` | Use / act | yes |
| 11 | Taint lattice by consequence | `openhuman` | Provenance | no |
| 12 | PPR diffusion instead of traversal | `hipporag` | **Retrieval** | no |
| 13 | Non-destructive entity resolution | `hipporag` | Consolidation | no |
| 14 | Event time allowed in the future | `minecontext` | Admission / schema | no |
| 15 | Sealed until `deliver_on` | `memento` | Admission | no |
| 16 | Write refused below provenance rank | `echo-agent` | Capture / write | yes |
| 17 | Git co-change affinity as a recall signal | `empryo` | **Retrieval** | no |
| 18 | Failure vocabulary in the contract | `cosmonapse` | Contract | yes |
| 19 | Check refuses an unearned pass | `cambium` | Tooling | yes |

Nineteen mechanisms. Grouping consolidation, delete, audit/provenance,
verification and use/act as *after a memory exists and is believed*: **11 of 19.**
Retrieval: **3.** The remaining five are admission (2), write, contract and
tooling.

The phase assignment is a judgement and the bucket boundary is arguable — a
reader who thinks consolidation belongs with capture gets 9 of 19 instead. The
arithmetic is not: it is derivable from the table above, which is the difference
between this version and the last two.

**What cannot be concluded.** The first version wrote that nobody benchmarks the
correction phase and that the sparse mechanisms and the sparse benchmarks "are
the same fact". Both are wrong. The atlas itself records **30 of 155** systems
committing negative-retrieval assertions, and Lethe ships ForgetEval, which
benchmarks exactly this. And an opportunistic, non-representative sample cannot
support a causal claim about why anyone built anything. What the corpus supports
is the observation, not the explanation.

**On refusal.** The first version said "seven of eleven entries are about
refusal" and gave five examples; the second counted six of fourteen against a
denominator that did not exist. From the table: rows 1, 2, 4, 10, 16, 18 and 19 —
**7 of 19**, where the test is that the mechanism's *action* is to deny, withhold
or decline. Row 13 is the closest call and is marked no: linking instead of
merging avoids a destructive act rather than refusing a request. The observation
from [refusal as a lens](2026-07-28-refusal-as-a-lens.md) survives at that size,
and survives being counted three different ways, which is more than it had
before.

## Part 4 — What the reviews changed

Recorded because a note that was wrong about its central claim should say so at
the top of the file and in detail at the bottom, not be quietly edited. Two
passes, the second reviewing the first version's own corrections.

| Claim in v1 | Status |
| --- | --- |
| Three tokens absent from one survey show the field lacks the tombstone | **Retracted.** Overturned by the atlas's own hazard; replaced with a two-document working hypothesis |
| "The lying operation" is a framing the atlas produced | **Retracted.** Prior names *false success* / *silent failure*; [arXiv:2606.09863](https://arxiv.org/abs/2606.09863) predates it — verified |
| "Three finds suggests the base rate is not low" | **Retracted.** No sampling frame; reworded to recurrence |
| Pattern-maturity labelling is an atlas contribution | **Retracted.** Proto-pattern and Known Uses are prior art |
| "None found is a claim about a search" is a contribution | **Downgraded** to a local rule with two scars |
| Nine systems carry the mechanism *as defined here* | **Corrected.** Nine earn the broad mark; the strong-form subset is unre-derived |
| Lethe's receipt proves erasure | **Corrected.** It is a signed acknowledgment bound to the log |
| Omi + OpenHuman are one trust entry | **Split.** OpenHuman's report says it does not model belief |
| MineContext + Memento are one prospective entry | **Split.** Memento's report says it is not prospective |
| Every entry sits after belief | **Corrected twice.** v2 counted entries, four of which held several mechanisms each, so its two conclusions had incompatible denominators. v3 counts 19 atomic mechanisms: 11 after belief, 3 retrieval, 7 refusals |
| Nobody benchmarks the phase | **Retracted.** 30 negative-eval suites, plus ForgetEval |
| pgvector 16, Chroma 11, Qdrant 11, LanceDB 6 | **Corrected** to 15/12/11/5 by `matrix.storage`, with the definition stated. `content/overview.md` carried the same stale figures and is fixed |
| "the 284-judgement subset" | **Corrected.** That split was taken at 136 reports; `list_superlatives.py` now reports **320** corpus-scoped superlatives, and it scans `content/`, not `notes/`, so the disclosure was inapplicable as written |
| Aura's chain is "what certificate transparency is built on" | **Corrected in v3.** CT is a Merkle tree with signed tree heads and inclusion proofs ([RFC 9162](https://www.rfc-editor.org/rfc/rfc9162.html)); Aura is a linear `prev_hash` chain. Same family, different construction — and Lethe's Merkle root is the closer analogue |
| The mechanism-noun matcher added in v2 | **Fixed in v3.** It bypassed the local-scope guard and had no fixture of its own, so "two tombstones" in one system's prose could have failed the build. It now requires a corpus marker in the sentence, and three controls cover the branch — one of them mutation-tested by deleting the guard and confirming the control fails |

**And the drift the review found that the new checker missed.**
[`overview.md:104`](../content/overview.md) still read *"the atlas's headline
counts — three tombstones, six negative-eval suites"* against live counts of nine
and thirty — stale by six and twenty-four, in the paragraph explaining what the
atlas's headline counts mean. `check_claim_counts.py` walked past it because it
required an atlas noun (*systems*, *reports*, *repositories*) or the corpus
denominator, and "three tombstones" is neither. The checker now binds a number
that names its mechanism directly, the sentence is fixed, and the sequence is
worth keeping: a checker shipped in the morning, a reader finding what it missed
in the evening. The
[count-checker note](2026-08-06-the-count-claim-checker.md) has the rest.

## Follow-ups

- **Re-derive the strong-form tombstone subset.** Which of the nine key on a
  normalized value, consult it on the write path, and refuse activation? Until
  that exists, the pattern page and this note both hedge in prose where a count
  belongs. It would also settle the invention-chain numerators on
  [the pattern page](../content/patterns/rejected-value-tombstone.md) that two
  passes have now declined to touch.
- **One literature search, on one mechanism.** Entry 1 or entry 2, done properly,
  would show what upgrading "corpus-unique" to "novel" actually costs — and
  whether the atlas can afford to make the claim at all.
- **Decide whether Part 1 belongs on the site.** It is the answer to *why read
  this rather than the survey*, and no page gives it. It is publishable only in
  the scoped form above.

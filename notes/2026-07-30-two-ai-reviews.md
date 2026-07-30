# Two AI reviews, checked

**Status:** done — one atlas change, one declined proposal recorded, one survey closed out
**Origin:** unsolicited reviews of the atlas from Gemini and Grok, submitted
2026-07-30. Both are broadly favourable; this note records what was checked,
what was wrong, and what came of it.

## The claims that held

Every specific, checkable claim in both reviews was accurate against the repo:

- The qualification test is quoted correctly — *"something it stores survives the
  session with an identity that can later be corrected"*.
- Skales' deletion modal is verbatim from
  [its report](../content/systems/skales.md): *"Deletion not yet supported in UI."*
- MemPalace does carry exactly one of the seven marks.
- The tombstone count and its provenance — three systems, Verel under red-team
  pressure, RainBox adopting it, Daimon an independent weaker arrival — is right.
- ADK and AutoGen do lack a removal method, and AutoGen's cannot express one.
- There are exactly five divergences.

Both reviews describe a corpus of "~76–91" systems. It was 91 that morning and
96 by evening. That is drift, not error, and it is the expected cost of a
project whose unit is a pinned commit.

## The claim that did not

Grok's review closes by quoting the atlas's "central thesis" as a blockquote:

> Retrieval is only half the memory problem. Almost every system builds the
> ascent; almost none completes the descent — which is why correction, not
> retrieval, is where memory fails.

**That sentence is not in the atlas.** `grep -rni "ascent\|descent" content/`
returns one hit, in [metaclaw](../content/systems/metaclaw.md), about gradient
descent. The framing is a fair paraphrase of what the atlas argues, and the
quotation marks are an invention.

Recorded because it is the atlas's own recurring finding, arriving from the
outside and pointed inward. This project's method is: take the strongest claim
that could be checked against an artifact, and check it. Here the strongest
claim in a review *of* the atlas — the one sentence given the authority of a
direct quotation — is the one with no artifact behind it, and it appears at
exactly the point where the reviewer reached for maximum confidence. That is the
same shape as Memvid's untraceable figures, SimpleMem's six numbers with no
committed results, and the other atlas's confidence score that was a restatement
of one other column.

The practical consequence is small and worth stating anyway: a reader who
encounters the atlas through a summary of it may be quoting a sentence nobody
wrote.

## The pioneering survey, closed out

Grok's reading list named one item the atlas had not processed: **Zhang, Bo, Ma,
Li, Chen, Dai, Zhu, Dong and Wen, *A Survey on the Memory Mechanism of Large
Language Model based Agents***, [arXiv:2404.13501](https://arxiv.org/abs/2404.13501)
(21 April 2024, 39 pages), the field's earliest comprehensive survey and its
most cited. Absent from `content/` and `notes/` until now. It was accepted into
**ACM Transactions on Information Systems**, not ACM Computing Surveys as the
review states.

Checked the way the [reading-list note](2026-07-29-a-reading-list-triaged.md)
says to: go to what the paper points at. Its companion repository is
[nuster1128/LLM_Agent_Memory_Survey](https://github.com/nuster1128/LLM_Agent_Memory_Survey),
last updated 2 July 2025 to record the journal acceptance. It holds the survey's
categorisation, its figures and its citation block. **No implementation, no
benchmark harness, no dataset, and no links to framework repositories** — a
reading list, like the four before it.

So the finding is the same one, now confirmed across five surveys including the
earliest: *the field's survey literature and the field's inspectable code have
almost no intersection.* The [survey pass](2026-07-29-memory-survey-forms-functions-dynamics.md)
that produced nine reports got them from a framework **table**, not from a
bibliography.

One connection is worth keeping. The survey's first author maintains
`nuster1128/MemEngine`, which this atlas examined in an earlier round and left
without a report because **it has no persistence layer at all**, and no licence
file. The person who wrote the field's most-cited account of agent memory also
shipped an agent-memory library that does not outlive the process. That is not a
criticism of either artifact — a research framework and a durable store are
different things — but it is the vocabulary-versus-code gap in a single author,
and it is the sharpest illustration this atlas has of why it reads repositories
instead of surveys.

## What changed

- **[The prospective-memory section](../content/overview.md) is extended.** Both
  reviewers independently picked it out as the most interesting part of the
  atlas, and Gemini's expansion of it contained one framing the atlas did not
  have: the category is nearly empty because of a **boundary dispute**, not an
  oversight. Schedulers and job queues already own future commitments, and that
  division survives everything except the semantic trigger — "the next time we
  discuss project scope" cannot live in cron, because matching it needs the
  incoming turn, the stored commitment, and a judgement that the two are about
  the same thing, which is a retrieval operation. Added, together with three
  requirements no system here holds at once and the observation that
  ai-memory's handoff is the near-miss from the other side.
- **[An "API-contract only" tier was declined](2026-07-28-declined-proposals.md)**,
  with its own entry, because it is the fourth arrival of the closed-source
  proposal and the first version narrow enough to need a separate answer.
- Nothing else. The run-versus-read critique is already conceded at length in
  the known-limitations section, in more detail than the critique asks for.

## The reason to record a favourable review at all

Not for the praise. Two independent reviewers with no shared inputs converged on
the same three things — correction as the field's blind spot, the companion and
roleplay systems competing on authorial control, and prospective memory as the
empty category. That is weak evidence that those three are the load-bearing
claims, and it is the only external corroboration the atlas has that is not
another reading list.

It is weak evidence for a specific reason worth stating: both reviewers read the
atlas, so their agreement may be the atlas's own emphasis reflected back. The
convergence is on *which* of the atlas's claims are most interesting, not on
whether they are true, and nothing here tests them.

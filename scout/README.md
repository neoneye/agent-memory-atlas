# Daily candidate shortlists

One pair of files per day, written by [`scripts/triage`](../scripts/triage):

- `YYYY-MM-DD.jsonl` — the machine-readable record. The first line is a `meta`
  object: the source snapshot's hash and size, how many repositories were newly
  imported as against how many were already in the backlog, how many were
  actually inspected, what stopped the run, the day's capacity, and disk use.
  Every line after it is one selected candidate with the evidence that selected
  it — pinned commit, score breakdown with the anchor behind each award, test
  evidence paths and content hashes, metrics with their uncertainty, and the
  selection id the analysis claims against.
- `YYYY-MM-DD.md` — the same content as a digest to read.

The `kind` discriminator matches Scout's own record shape, so
`Daily-Nerd/scout`'s `data/candidates.jsonl` and these files read the same way.

They are committed because that is what makes the scout-to-triage path checkable
after the fact. A run of these over several weeks answers whether discovery is
feeding triage anything worth reading, and whether the rubric's threshold is in
the right place, without anyone having to open a database.

Two things they are not. A shortlist is the best among the candidates **actually
inspected and found eligible** that day, not a claim to have assessed the whole
feed — the `meta` record carries the coverage that says so. And the daily file
does not replace either Scout's cumulative index or triage's own state; it is a
statement about one day.

Scout owns `candidates.jsonl` and triage never writes to it. A candidate that
fails triage, or that the atlas analyses and rejects, stays in Scout's discovery
history.

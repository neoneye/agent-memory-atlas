# Candidate triage

Scout discovers repositories and writes them to `data/candidates.jsonl` in
[`Daily-Nerd/scout`](https://github.com/Daily-Nerd/scout). The atlas can read
about twenty repositories a day, properly, at a pinned commit. This program
stands between the two: it imports Scout's index without ever writing to it,
collects cheap evidence, remembers every decision, and produces one bounded,
explained shortlist a day.

It never clones anything, never runs anything it fetched, and never files an
issue. The expensive analysis is a separate program; the contract with it is
`claim` and `result`.

The specification this implements is
[`notes/2026-09-11-candidate-triage.md`](../../notes/2026-09-11-candidate-triage.md),
adapted to Scout's 11 September feed by
[`notes/2026-09-11-candidate-triage-v2.md`](../../notes/2026-09-11-candidate-triage-v2.md).

---

## Install

Nothing to install. Python 3.11 or newer, standard library only — no
dependencies, no virtualenv, no service.

```bash
python3 scripts/triage --help
```

The directory is executable because it holds a `__main__.py`, so `scripts/triage`
is both the package and the command.

## Configure

Defaults, then a JSON config file, then environment variables, then flags — in
that order, each overriding the one before.

| What | Default | Override |
| --- | --- | --- |
| Triage state | `$XDG_DATA_HOME/agent-memory-atlas-triage`, i.e. `~/.local/share/…` | `--state-dir`, `AMA_TRIAGE_STATE_DIR` |
| Daily output | `scout/` in this repository | `--output-dir`, `AMA_TRIAGE_OUTPUT_DIR` |
| Atlas checkout | this repository | `--atlas-repo`, `AMA_TRIAGE_ATLAS_REPO` |
| Feed | `Daily-Nerd/scout@main:data/candidates.jsonl` | `--source-repo`, `--source-ref`, `--source-path` |
| Local feed | none | `--source-file`, or `ingest --input` |
| Day boundary | `Europe/Copenhagen` | `--timezone` |
| Config file | `<state-dir>/config.json` | `AMA_TRIAGE_CONFIG` |

Every field of `Config` and `Limits` in [`config.py`](config.py) can also be set
from the config file, or from `AMA_TRIAGE_<FIELD>` and `AMA_TRIAGE_LIMIT_<FIELD>`.

**The maintainer's fork is a contingency, not a fallback.** If upstream
disappears, this program preserves state and reports the failure. Switching
source is an explicit configuration change, never something it does on its own.

### Token

Read-only. Unauthenticated works and gives you sixty API requests an hour, which
is roughly six repositories; a token gives five thousand.

```bash
export GITHUB_TOKEN="$(gh auth token)"     # or a fine-grained token with public read
```

The token is read from the environment, sent only to `api.github.com`, and never
written to a log, a database field, a classifier prompt, or an export.

### Classifier (optional)

The structural rules in [`evidence.py`](evidence.py) match paths and vocabulary.
That is **not** an answer to the atlas's question — does this persist
agent-relevant claims across sessions, under an identity that could later be
corrected — and the program does not pretend otherwise: without a judge, every
scope decision is labelled `heuristic` in the database, the digest and the JSONL.

```bash
export AMA_TRIAGE_CLASSIFIER_PROVIDER=anthropic
export AMA_TRIAGE_CLASSIFIER_MODEL=claude-opus-5
export AMA_TRIAGE_CLASSIFIER_TOKEN=...
```

The classifier gets no tools, sees only evidence already fetched under the byte
ceilings, and must cite a path and an exact quote for every claim. Citations are
checked against the bytes that were fetched; an uncheckable one discards the
whole verdict. Repository text — READMEs, comments, `AGENTS.md` — is quoted as
untrusted data and cannot change the policy or redirect a request.

A hand-written assessment works the same way and needs no provider:

```bash
python3 scripts/triage assess --manual labels.json
```

```json
[{"repo": "owner/name", "assessor": "simon", "in_scope": true, "substance": true,
  "test_evidence_level": "substantive", "confidence": 0.9,
  "reasoning": "…", "citations": [{"path": "tests/test_recall.py", "quote": "assert …"}]}]
```

---

## Operate

### First time

```bash
python3 scripts/triage init
```

Explicit, and the only command that creates state. Everything else **fails** if
the database is missing or unreadable. That is deliberate: an empty ledger would
reselect repositories the atlas analysed months ago and spend a day of budget
proving it.

### Every day

```bash
GITHUB_TOKEN="$(gh auth token)" python3 scripts/triage run
```

Ingest, assess, select, write `scout/YYYY-MM-DD.json` and `scout/YYYY-MM-DD.md`.
Bounded by a hundred inspections and three thousand API requests a day; safe to
run twice.

Or the stages separately:

```bash
python3 scripts/triage ingest                      # fetch and import
python3 scripts/triage assess --limit 20           # evidence, under budget, resumable
python3 scripts/triage select --dry-run            # what would be admitted
python3 scripts/triage select                      # finalize and freeze the day
python3 scripts/triage status                      # counts, capacity, budgets, disk
python3 scripts/triage explain owner/repo          # evidence, history, next action
```

A day is **frozen** once selected. Rerunning regenerates the identical files
from the committed transaction rather than selecting again, so a crash between
the database commit and the file write costs nothing. Showing an older day
(`select --day 2026-09-01`) never admits anything.

### The day's output

`scout/YYYY-MM-DD.json` is the machine-readable record: one object describing the
run — source hash, newly imported against backlog, what was inspected, what
stopped the run, capacity, disk — with a `shortlist` array holding one object per
selected candidate and the evidence that selected it. Pretty-printed with sorted
keys, so a diff between two days shows what changed.

It is deliberately not JSON Lines. A day's report is read whole and is usually a
handful of records; a stream format would mean two different record shapes in a
two-line file, and `json.load` should be the whole of reading it.

`scout/YYYY-MM-DD.md` is the same content as a digest to read.

These files are committed to this repository on purpose: six weeks of them answer
"is the scout-to-triage path working" without anyone having to reason about a
database.

### What Scout sends, and what triage does with it

Scout's feed carries two shapes of repository record. **Modern** records carry a
`latest` payload — description, stars, push date, licence, the terms that
matched, sometimes topics and a cached README size — beside `sources`,
`source_urls` and Scout's first and last sighting. **Legacy** records are the
initial issue batch Scout retracted as a discovery misfire
([issue 1256](https://github.com/Daily-Nerd/scout/issues/1256)): `title_only:
true`, an issue number, nothing else. A third shape, a bare name with a status,
is ordinary older input and is treated as such.

Since Scout's [PR 1257](https://github.com/Daily-Nerd/scout/pull/1257), merged
11 September 2026, a row also carries Scout's own states and its own rubric.
`discovery` says what Scout did — `seen`, `filed`, `retracted`, `title_only` —
and `assessment` what its scoring said — `none`, `tier-a`, `tier-b`, `tier-c`,
`atlas-known`. `score`, `tier`, `components`, `absent_components` and
`scored_at` are that rubric's output, recomputed on every Scout run. Inside
`latest`, `fetched_at` is when Scout last read the repository from GitHub, and
`tree_tests`, `tree_source_files` and `tree_fetched_at` are what one git-tree
listing showed it. Scout's own README states that a retracted or title-only
discovery never means the atlas analysed or rejected the project, and this
program agrees: a legacy row without a payload is held, whether it says
`title_only: true` or `discovery: retracted`.

Everything in `latest` is stored as a **hint**, validated and capped, and shown
by `explain` under *upstream hints*. A hint is another program's observation of
unknown age. It decides which repository has its metadata fetched first. It is
never copied into the measured facts, never read by a gate, and never part of
the atlas score. A missing hint is neutral; only a measured zero — a README
size of 0 — counts against. Scout's tree signals order the queue the same way:
a seen tests directory reads earlier, an unfetched tree is neutral. Scout's
states and rubric are kept under `upstream_*` names — `upstream_discovery`,
`upstream_assessment`, `upstream_tier`, `upstream_score`,
`upstream_components` — read by nothing that decides and by nothing that
orders: Scout's tier weighs the same signals this program collects for itself,
and reading it would count them twice. The day's report counts the snapshot's
`discovery` and `assessment` states under *Scout's own view*, so its
vocabulary and this program's can be compared without being confused.

An observation is recorded when what Scout said changed: a new tier or a new
discovery state is one, a rescored decimal with a new `scored_at` is not.

**The legacy batch is held.** A title-only record with no payload is imported
and kept, and held out of the daily metadata and inspection budgets. The hold
is about the source, not the project: it is not a rejection, it is separate
from `analysis_status`, and a new policy version does not lift it. Two things
do: a later snapshot that carries a payload for that identity, which clears the
hold even if the `title_only` flag was left stale or the discovery still says
`retracted`; or the maintainer.

```bash
python3 scripts/triage legacy list                    # what is held, and why
python3 scripts/triage legacy release owner/repo      # revisit one, deliberately
python3 scripts/triage legacy release --batch 20      # or a bounded batch (at most 50)
```

A released identity is not held again by a later import. There is no daily
sweep of the held set.

Work that already exists outranks the hold. An identity that is selected,
running, accepted or rejected by an analysis, or that a person assessed by
hand, is never held; its disposition says `analysis_precedence` or
`manually_assessed`. An identity triage had already assessed keeps its evidence
and its status and is held with the disposition `assessed_before_hold` — which
means it is not offered for admission until released.

**Measurements go stale.** A metadata row older than `metadata_max_age_days`
(14) is due for a refresh under the same daily budget, and so is one whose
feed hint reports a newer push — after a day, so a reimport cannot turn every
hinted change into same-day work. A refresh reads GitHub, not the seven-day
response cache, and every measurement is dated by the oldest response it was
built from, so a cache hit never makes old numbers look new. Refreshing a
measurement does not reopen an analysis rejection or anything running.

The fetch reads the Contents API's JSON form for the file's size and git blob
sha. Up to 1 MiB that response also carries the file as Base64, and those bytes
are used. The feed passed 1 MiB on 11 September 2026, above which a second
request fetches the raw bytes. Either way a body that does not match both size
and sha is refused — so a truncated download is a failure, not a feed that
happens to be shorter. The upstream commit that last touched the file
is recorded with every ingestion; pin a snapshot with `--source-ref <sha>`.

### Handing work to the analysis

```bash
python3 scripts/triage claim <selection-id> --worker my-laptop
python3 scripts/triage result <attempt-id> --input result.json
```

A claim is a lease with a fencing token. An expired lease can be reclaimed, which
supersedes the previous attempt explicitly; the superseded worker can still
submit and its submission is recorded as stale rather than allowed to overwrite
the newer one. A retry continues the same selection and does **not** consume
another day's admission.

```json
{"status": "accepted", "analysed_commit": "…", "report": "content/systems/foo.md"}
{"status": "rejected", "analysed_commit": "…", "reason": "a context buffer, not a memory"}
{"status": "error", "retryable": true, "category": "network"}
```

An `error` is a technical failure and returns the candidate to the pool. It is
never recorded as a judgement about the project — that would mean the atlas had
rejected something it never read.

The analyser owns any checkout it makes: it deletes its own temporary directory
on completion, including after an error, and recovers its own abandoned
workspaces on its next start. This program does not clone and does not clean
another program's directories.

### Resuming interrupted work

Everything is resumable and nothing has to be undone. Budgets are per civil day
and survive restart, so a second run continues where the first stopped rather
than re-spending an exhausted allowance. An interrupted assessment leaves the
candidate unassessed and it comes back round. An interrupted selection either
committed or did not; if it committed, the files regenerate. An interrupted
analysis leaves a lease that expires and can be reclaimed with a higher fence.

```bash
python3 scripts/triage status        # what is outstanding, and what a lease is holding
```

---

## Disk

The candidate index is small. The risk is everything else, and the default path
writes no repository source to disk at all — blobs are read into bounded
buffers, assessed, and dropped. What survives is paths, hashes, capped excerpts
and decisions.

| Resource | Default ceiling |
| --- | ---: |
| Candidate feed, decoded | 16 MiB |
| One source blob, decoded | 256 KiB |
| Blobs per inspected repository | 12 |
| Source text per inspected repository | 2 MiB |
| Responses per inspected repository | 16 MiB |
| Requests per repository | 30 |
| GitHub requests per day | 3,000 |
| Inspection deadline per repository | 90 s |
| Response cache | 64 MiB, metadata only, 7-day TTL, LRU |
| Scratch | 32 MiB |
| Run log | 16 MiB, rotated at half, one predecessor kept, redacted |
| Whole state directory | 256 MiB soft stop |

A daily ceiling stops the run; it is not recorded against the repository that
happened to be in hand. When the request ceiling or a rate limit cuts a
measurement or an inspection short, nothing is written for that repository, no
slot is spent on it, its status is untouched, and it is due again next run. A
rerun on a day whose allowance is spent offers nothing. The rotating exploration
cursor moves past a candidate only once it has actually been measured or
inspected, so a run that stops early skips no one.

`Content-Length` is never trusted: the reader counts the bytes that actually
arrive and, separately, the bytes that come out of the decompressor, so a
chunked response, a misdeclared length and a compression bomb all land on the
same ceiling.

```bash
python3 scripts/triage cleanup       # scratch, cache eviction, WAL checkpoint
tail -3 ~/.local/share/agent-memory-atlas-triage/triage.log
```

The run log is one JSON line per invocation — command, duration, exit, error —
so it grows with invocations rather than with the feed. Everything written
through it is redacted first.

Cleanup also runs at the start of every `ingest`, `assess` and `run` — the
maintainer does not reboot daily, so anything that only happens at startup
happens never. If a deletion fails, repository processing stops and the exact
path is reported; it is retried on the next invocation rather than accumulating
silently.

**Decisions, assessments, selections and results are never deleted to reclaim
space.** If the state directory must shrink, export and archive it deliberately.

### What the cleanup guarantee actually is

No process can run a `finally` block after `SIGKILL` or power loss. The promise
is narrower and true:

* Normal completion, exceptions, timeouts and Ctrl-C leave **zero** per-assessment
  scratch.
* Abnormal termination leaves **bounded, marked** directories under one owned
  root, and the next locked startup removes them before doing anything else.
* The default in-memory path leaves no repository bodies on disk even then.
* Unowned neighbours and symlinks are reported and never deleted or traversed.

A single OS-backed `flock` guards all of this, so a crashed process releases it
without anyone interpreting a stale PID file.

## Back up

```bash
python3 scripts/triage export --output backup.jsonl
python3 scripts/triage restore --input backup.jsonl        # into an empty state dir
```

The backup carries decisions, aliases, assessments, selections, attempts, budget
use and the schema and policy versions needed to continue safely. It carries no
credentials and no cached response bodies. A restore **replaces** a ledger; it
never merges into one. It builds the database at the backup's own schema
version, loads the rows, migrates forward in the same transaction, and reopens
the result before moving it into place — so a backup from an older build comes
back at the current schema, and a restore that fails leaves the existing ledger
untouched. An attempt restored as `running` holds a lease from before
the backup and needs reconciling with whoever held it before it is reclaimed —
`restore` lists those.

---

## How a decision is made

Four mandatory gates, then a rank. A high score does not buy a way past a gate,
which is why adoption is worth ten points out of a hundred and sits behind a
logarithm.

1. **In scope** — persists agent-relevant claims across sessions under an
   identity that could support correction. A working correction mechanism is not
   required; its absence is a finding for the full analysis.
2. **Readable implementation** beyond a placeholder, a promotional README or an
   unmodified template.
3. **Substantive committed tests.** A README promise, a testing badge, a
   directory named `tests` and a runner dependency are all not enough.
4. **Not a duplicate** of an existing report or an open selection.

Test evidence is one of `unknown`, `absent`, `mention_only`, `files_only`,
`substantive`, `memory_specific`. The distinction that matters is between the
first two: a truncated tree, an unfamiliar layout, a failed request or an
exhausted per-repository budget produces `unknown`, which **defers**. Only an
adequately covered tree with nothing in it produces `absent`, which rejects.
Collapsing those two is how a project gets rejected for the reviewer's timeout.
A stop that belongs to the day — the request ceiling, a rate limit — produces
neither: the reading is discarded, and the run ends.

The rubric is in [`policy.json`](policy.json) with a version, and every awarded
point carries the anchor that awarded it, visible in `explain` and in the day's
JSONL.

| Component | Max |
| --- | ---: |
| Test evidence | 30 |
| Implementation substance | 25 |
| Contribution and maintenance | 20 |
| Potential value to the atlas | 15 |
| Adoption and public track record | 10 |

Known bot accounts are counted separately, and what remains is called
*apparently non-bot* rather than *human*, because GitHub's account type does not
prove a person. An account under thirty days old caps the track-record score and
records a caution; it is never a spam label, and strong code with real tests
outweighs a sparse public profile. Private history is *unavailable*, not absent.

---

## Tests

```bash
python3 scripts/triage selftest
```

195 tests, about four seconds, hermetic — a fake GitHub, temporary state
directories, no network. They run as part of `npm test` for this repository.

They cover the acceptance list in the specification: rewritten and reordered
feeds, renames and name reuse, the source file never changing, byte ceilings and
compression bombs, README prompt injection, the daily and outstanding limits
under reruns and timezone changes, fencing tokens and stale submissions,
scratch after every termination path including `SIGKILL`, and a 1,400-candidate
fixture run.

---

## The first live runs

On 11 September 2026, against the live feed, with a token:

| | |
| --- | --- |
| Feed | 275,543 bytes, 1,384 lines |
| Records | 1,331 repositories, 53 `post`/`meta`, 0 malformed |
| Metadata collected | 40 repositories |
| Inspected | 37 repositories: 52 inspections, 40 of them under policy `2026-09-11.2` |
| Current outcomes | 6 eligible, 27 rejected, 4 deferred |
| Selected | 1 — the day froze on the first, smaller batch |
| State directory | 2.3 MiB after the first batch, 74 bytes of scratch |

1,331 repositories in an accumulated index is a **backlog**, not a daily arrival
rate, and the report separates newly imported from backlog for that reason.

The first batch of twelve ran under `2026-09-11.1` and exposed five defects,
each now pinned by a test in [`tests/test_regressions.py`](tests/test_regressions.py):
a Rust store written with `std::fs` was invisible, so a crate with a
`core/persistence.rs` was rejected as out of scope; scope was rejected from a
*sample* in which no store write appeared, which is an absence claim from
partial coverage; correction vocabulary such as `deleted_at` and a plain `scope`
column went unmatched, so the fifteen atlas-value points were unreachable and
every candidate was ranked out of eighty-five; blob reads were spent on issue
templates, config files and a translated README instead of source; and an empty
repository was deferred as "the tree could not be listed". Under `.2`, two of the
first batch's rejections — ContextMeld and memora — are eligible.

The version names the evidence rules and the weights together. A rejection is a
statement under one version, and a new version makes it due for reassessment,
which is how the first batch was re-read without anyone clearing a decision by
hand.

More than half the rejections under `.2` are about score, not gates: fifteen of
the twenty-seven cleared all four gates and scored between 46 and 59. The minimum of
60 sits on that cluster, and it is the clearest thing these batches say: the
number is a guess until it is calibrated.

---

## What this does not do, and what is not yet known

* **The rubric is uncalibrated.** Every weight and anchor in `policy.json` is a
  starting assumption. One live batch of twelve is not a calibration; the step
  that would make these numbers evidence is the labelled-sample review in §10
  Phase 5 of the specification, and it has not been done.
* **Scope is heuristic unless you configure a judge.** Without a classifier or a
  manual assessment, in-scope means "a store is written to in code that also uses
  the memory vocabulary". That is a keyword and structure match. It is labelled
  as one everywhere it appears and should not be read as a semantic judgement.
* **Only `anthropic` is implemented** as a classifier provider. Everything else
  reports clearly that it is not, and the manual import always works.
* **The atlas's prose exclusions are hand-kept.** Reports under `content/systems/`
  import automatically from frontmatter. Repositories examined and deliberately
  set aside live in `content/overview.md` as sentences, and the machine-readable
  half of that is [`exclusions.txt`](exclusions.txt), maintained by hand.
* **Nothing observes a CI run.** A workflow shows tests are configured to run.
  Whether they passed is a claim about a run, and this program has not watched
  one.
* **A truncated tree concludes nothing.** GitHub truncates large trees; when it
  does, absence of a path is not evidence and the candidate defers.
* **One process at a time**, guarded by a local `flock`. A state directory shared
  across machines over a network filesystem is not supported.
* **A hundred inspections a day is a cost ceiling**, not a promise that a hundred
  inspections yield twenty eligible projects. Fewer than twenty selections is an
  ordinary result.
* **Nothing here is scheduled, published or pushed.** No cron, no issues, no
  commits. That was not asked for, and it is a separate decision.

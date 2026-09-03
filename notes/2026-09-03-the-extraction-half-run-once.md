# The extraction half, run once

**Status:** a reading, 3 September 2026, of `robert-mcdermott/ai-knowledge-graph`
at [`40b701978e41c64ee4e787a5b1c5b833b5e0e8e8`](https://github.com/robert-mcdermott/ai-knowledge-graph/commit/40b701978e41c64ee4e787a5b1c5b833b5e0e8e8).
Filed in the overview's examined-without-report list. No report. Screened before
reading: no auto-run surface, no build-time execution, no unpinned manifest,
`uv.lock` unchanged for 478 days. Nothing installed or run.

---

## What it is

A CLI: one text file in, one JSON file and one HTML page out. Apache-2.0, 2,040
lines of Python, 64 commits between 22 March and 27 December 2025, three
authors. Chunk the text by words, ask an OpenAI-compatible endpoint for
lower-cased subject–predicate–object triples with predicates capped at three
words, standardise entity names, infer more edges, render with PyVis and
Louvain communities. The three tags all carry the same `version = "0.6.1"`.

## Why no report

The inclusion test asks for something stored, retrieved later, and open to
being scoped, corrected or forgotten. Here the JSON is written once and read by
nothing except a re-renderer; there is no query path, no merge of a second
document into the graph of a first, no scope, no correction and no deletion.
The word *memory* does not occur in the code. It is the extraction stage that
graph memories such as Graphiti and cognee build on, without the store or the
reader that would make it one of them. Kind one in the boundary taxonomy, and
it will not reverse on a release: adding a store and a reader would make it a
different program.

## What is worth carrying

**The stated-versus-inferred flag, and the number behind it.** Every edge the
inference phase adds is marked `inferred: True`, drawn dashed, and filterable
on the page. The README's own run shows why the flag matters more than it looks:
209 stated edges and 355 inferred, so 63% of the delivered graph is the
inference phase's. A graph memory that borrows this stage and stores the result
has stored a majority of guesses under one flag.

**Where the guesses come from.** Transitive composition mints a predicate from
the path — `A → B → C` becomes `<pred> via B` — which is why the run's second
and third most common relations are *"advances via Artificial Intelligence"*
and *"pioneered via computing"*. Lexical similarity mints `relates to` or
`is type of` between any two entities that share a four-letter word or contain
one another, which is where the most common relation, *"related to"* at 65
occurrences, comes from. Standardisation merges two entities whose four-letter
stems overlap by more than half. Each is defensible for a picture and each
would be a false belief in a store an agent recalls from.

## Small things

- *"Added -22 inferred relationships"* in the README's console output is
  `len(filtered) - len(triples)` printed after deduplication and self-reference
  removal, not a bug in the count of inferences.
- The README's configuration block says `chunk_size = 200` and
  `temperature = 0.2`; the committed `config.toml` says 100 and 0.8.
- `json_to_html.py`'s usage string names `docs/industrialRev.json`, which is not
  in the tree; `docs/` holds one 864 KB rendered page.

## What this changes for the method

Nothing new. The boundary taxonomy's first kind covers it, and the reading was
worth the hour for one sentence the graph-memory reports can now cite: a
majority-inferred graph is what an unconstrained inference phase produces on a
966-word document, and the systems that store such graphs rarely say what
fraction of their edges a model guessed.

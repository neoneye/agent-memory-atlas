---
title: "Hillock"
eyebrow: "A gate that is control flow"
description: "A small local prototype that refuses by never calling the model, publishes every version's scores including the ones that fell, and raised its gate until the benchmark's own answerable questions stopped clearing it."
root: ../..
page_kind: system
source_name: "roandejager/Hillock"
source_url: https://github.com/roandejager/Hillock
revision: 5fdaeffe7dadee52a15cf1772b46013cc1af256a
revision_url: https://github.com/roandejager/Hillock/commit/5fdaeffe7dadee52a15cf1772b46013cc1af256a
analyzed_at: 2026-08-30
capabilities: "negative_eval"
capability_evidence:
  negative_eval: "the benchmark fixture and the gate metric | evaluate_hillock_PROTO_ish.py `generate_test_assets` (lines 77-86), `run_evaluation` | ten of the thirty generated questions carry `\"answerable\": False` and no expected triple, so the only correct behaviour is a refusal — a question about a person the corpus never mentions (`Where was Thomas Edison born?`), a predicate the subject does not carry (`What did Albert Einstein discover?`), a relation asked in the wrong direction (`Who cracked Enigma?`), and a bare identity probe (`Who is Turing?`). They are asserted against a real read path: `run_evaluation` ingests, queries each one, and counts a `HALLUCINATION_LEAK` whenever the gate admits a fact for a question that has no answer. Since v0.5 the run is unseeded — all three tables are dropped and the in-process HDC state, codebook and vocabulary book cleared — so a negative cannot be satisfied by a store that was never populated, and `verify_hillock.py`'s seventh check pins the seed-overlap arithmetic at four | the harness is the mechanism; no run output is committed, and `verify_hillock.py` check 8 computes how many negatives leak and asserts nothing with the number"
stack_storage: "sqlite"
stack_retrieval: "lexical, vector"
stack_source: "reviewed"
matrix:
  memory_unit: "A subject-predicate-object triple, plus a decaying co-activation weight between two entities"
  storage: "One SQLite file with four tables — entities, relations, hebbian_weights and an `hdc_reservoirs` blob store for multi-hop path vectors; the 10,000-dimensional codebook is in-process only"
  retrieval: "String entity linking, a one-hop SQL fetch, then cosine over bundled ±1 hypervectors against a fixed threshold, `0.55` at this pin; every vector is derived from the string's character n-grams rather than drawn at random"
  write: "An LLM extracts triples from ingested text or from a conversational assertion; there is no admission gate"
  update_delete: "Nothing is corrected. The functional-predicate `DELETE` is commented out under *\"Keep all extracted candidates in DB rather than destructively deleting earlier valid facts\"*, so every relation is now append-only with no supersession in its place; `clear_and_reinitialize` drops all four tables"
  scoping: "None — one database, one user, no scope key anywhere in the schema"
  integration: "A local console loop against Ollama; no API, no MCP, no library surface"
  background: "None; Hebbian decay runs inline on every turn"
  trust: "No status, no confidence, no provenance and no timestamp on a stored fact"
  strengths: "The refusal is a return statement — the model is never asked a question the symbolic layer could not answer"
  risks: "The gate's threshold is fixed while its similarity falls with query length, and none of the four benchmark questions the report scores clears it at `0.72` or at the `0.55` that replaced it — a distribution the verification suite computes and does not assert"
---

## 1. Executive Summary

Hillock is a local, single-user memory prototype: 1,827 lines of Python across eight files, licensed AGPL-3.0 with a contributor licence agreement its README says exists to preserve the option of commercial dual-licensing later. It stores facts as triples in SQLite, tracks Hebbian co-activation weights between entities, and holds a 10,000-dimensional hypervector space for matching.

Two things make it interesting to this atlas, and neither is the hyperdimensional computing.

**The refusal is control flow rather than instruction.** In `main.py`, the local model is only invoked *after* the symbolic layer has matched at least one stored fact above a similarity threshold, and it is handed those facts to render. When nothing matches, the function returns a fixed string — *"I do not have verified information about that"* — and no model is called at all. Almost every system in this corpus that promises not to hallucinate does it by asking a model to say "I don't know"; this one makes the question unaskable. That is a structurally different guarantee, and it is twelve lines of `if`.

**It publishes a seven-row version table including the rows where its own numbers fell.** Extraction precision 15.5%, extraction recall 50.0%, retrieval accuracy 45.0%, gate accuracy 43.3% — on the README, above the install instructions, beside every previous version's figures and a paragraph warning that the benchmark is one 32-sentence text and *"not enough to claim statistical robustness yet"*. Publishing the regressions is the creditable part and almost nothing in this corpus does it: gate accuracy peaked at 60.0% two versions earlier and retrieval accuracy at 55.0% one version earlier, and both rows are still there. The prose beneath the table is where the candour stops — it names only the two figures that rose, and the 🎉 marking "Retrieval Accuracy 45.0%" sits on a number ten points below the row above it. The harness that computes them is committed, and so is the whole benchmark: twenty answerable questions with expected subject-predicate-object and ten hard negatives each annotated with the reason it is unanswerable. What is not committed is any run output.

**The fading-context reservoir leaves its zero state because the token is added to it directly.** `step` computes `state = decay*state + token_hv + roll(state)*token_hv`, and the middle term is what makes the recurrence go anywhere: without it every term is proportional to the state, and a zero-initialised vector maps to zero forever. Reproducing both forms in separate code, the old rule holds a norm of `0.0` across five steps and the current one climbs `8.0 → 34.4`. The added term also does more than revive the state: `get_context_fingerprint` scores the state against *unbound* codebook entity vectors, so a purely permutation-bound state would have had no component to align with them.

Against that, two findings that reading the code produces and the README does not.

The **gate's operating point is a function of how long the question is, and the threshold has been raised past the benchmark.** Facts are bundled from exactly three components — a deliberate normalization the README explains — while the query is bundled from all its tokens, and both are compared against a fixed `HDC_THRESHOLD` of `0.72`, commented *"Recalibrated gating threshold to eliminate hallucination leaks"*. Reimplementing the encoder and the bundling in separate code, all four of the benchmark's own answerable sample questions score between `0.367` and `0.450` against the exact triple they ask about, and none of them clears the gate. The README's architecture diagram prints `Passed Threshold >= 0.42`.

And the **published gate accuracy does not measure gating.** `gate_acc = (correct_blocks + correct_answers) / len(questions)` pools blocking on the ten negatives with answering on the twenty positives. Read against the other published number, the pooled figure implies the gate blocked four of ten hard negatives.

## 2. Mental Model

A memory here is a **triple** — `Marie_Curie → born_in → Poland` — and nothing else is durable except the strength of association between two entities.

A fact becomes a memory when a local model extracts it, either from an ingested document or from a sentence the user typed that parses as a declaration. There is no admission gate, no confidence, and no review: `update_relation` is called and the triple is in the store. A fact stops being a memory when a later assertion overwrites it — which happens only for five named functional predicates, `born_in`, `died_in`, `capital_of`, `place_of_birth` and `place_of_death` — or when `/reset` drops all three tables. Every other relation accumulates. There is no per-fact deletion, no status, no timestamp, and no record that anything was ever removed.

So the epistemic vocabulary is thin by construction: **everything stored is treated as true**, and the entire trust decision has been moved from the store to the read path. That is a coherent position for a prototype and it puts unusual weight on the gate.

The second durable structure is associative rather than propositional. `HebbianPlasticityEngine.update_associations` takes the set of entities active on a turn and, for each pair, moves their weight toward 1.0:

```python
new_w = current_w + self.eta * (1.0 - current_w)      # eta = 0.15
```

then multiplies every pair *not* co-active this turn by `1 - decay` (0.01). Reinforcement is asymptotic and cannot exceed one; decay is per-turn rather than per-unit-time, so an association fades by conversational distance rather than by the calendar — which is consistent, since no row in this schema carries a time at all. These weights survive the session in SQLite. They are used to prime the renderer with related concepts, never to select which facts answer a question.

The third structure does not survive anything. The codebook is an in-process dictionary, allocated lazily on first sight of a token, and the reservoir state is a NumPy array in memory. Both are rebuilt from scratch on every launch, and rebuilding them is free: `get_or_allocate_hypervector` routes every string through `resolve_predicate_hypervector`, which sums the character 3-, 4- and 5-grams of the padded string, each hashed with MD5 into a seeded ±1 draw. A given entity therefore resolves to the *same* hypervector in every run, and two strings sharing character n-grams resolve to correlated ones. Measuring the encoder in separate code, ten unrelated entity names average a pairwise cosine of `+0.003`, while `born` against `born_in` is `+0.32` and `discover` against `discovered` is `+0.55`. That morphological signal does real work — it is how a query token reaches a fact predicate without a synonym table. The vector layer holds no memory in the sense this atlas uses the word: nothing is stored, and every vector is a pure function of its string.

```mermaid
%% caption: below the cosine threshold the model is never called and a fixed refusal is returned, so the gate is a hard admission test rather than a ranking
flowchart TD
  Q["user turn"] --> L["link_entities:<br/>string match to entity ids"]
  L --> F["SQL: every triple where the entity<br/>is subject or object"]
  F --> M["bundle query tokens · bundle each fact<br/>as exactly 3 components · cosine"]
  M --> G{"cosine ≥ 0.72?"}
  G -->|no| R["return 'I do not have verified<br/>information about that' —<br/>the model is never called"]
  G -->|yes| H["Hebbian: strengthen every<br/>co-active pair, decay the rest"]
  H --> P["render prompt = matched facts<br/>+ primed associations"]
  P --> O["Ollama renders the answer"]
  S["reservoir state"] -. "decay·state + token + roll(state)·token" .-> S
  S -.->|"top-1 codebook match"| PR["pronoun resolution<br/>when no entity linked"]
```

## 3. Architecture

A console program. `python main.py` opens a REPL against a local Ollama endpoint; there is no server, no API and no importable library boundary.

- **`main.py`** (20 KB) — the loop, entity linking, the HDC matcher, the gate, extraction prompts, and the three verbosity modes.
- **`database.py`** — three-table SQLite schema and all SQL.
- **`plasticity.py`** — the Hebbian engine, also over the same SQLite file.
- **`reservoir.py`** (236 lines) — the subword encoder, a sign-random-projection SimHash for GloVe vectors, and the fading-context reservoir.
- **`ingestor.py`** — threaded chunking of `.txt` and `.pdf` into blocks of five sentences with two overlapping.
- **`talon_engine.py`** (20 KB) — the CUDA relation extractor, which the README presents as stages one to three of its architecture and lists in its file overview.
- **`evaluate_hillock_PROTO_ish.py`** (16 KB) — the benchmark.
- **`config.py`** — every tunable constant in one place, which at this size is the right call.

### Deployment and ergonomics

The dependency list is `numpy`, `psutil`, `pypdf` — three lines, unpinned — and the README's setup does not agree with it: it instructs a CUDA PyTorch install from an external index before `pip install -r requirements.txt`, and lists *"NVIDIA GPU with CUDA support (8GB VRAM recommended)"* as a prerequisite. `torch` is what that command installs; `transformers`, `glirel`, `spacy`, `fastcoref` and `sentence-transformers` — the five packages `talon_engine.py` imports — are in neither the command nor the file. So the documented install produces a machine with CUDA PyTorch on it and the extraction pipeline the architecture diagram is drawn around inert.

**A first run downloads 822 MB from a third-party host without asking.** `IntegratedHillock.__init__` calls `load_lightweight_glove()`, which checks for `glove.6B.50d.txt`, does not find it — the file is not in the repository and nothing in the README mentions it — and calls `urllib.request.urlretrieve("https://nlp.stanford.edu/data/glove.6B.zip", "glove.6B.zip")` before extracting the 50-dimensional table. That is the whole of the `GLOVE_PATH` story: a bare filename in the working directory, a silent fetch on the first launch, and a `~10MB RAM` footprint claimed in the docstring for the trimmed dictionary rather than the archive it arrives in.

The store is one SQLite file of three small tables, so it is inspectable and repairable with any SQL client, and `/reset` re-seeds ten entities and seven relations so a fresh database is never empty. Nothing runs in the background; every write, decay step and query happens inline on the turn.

**`talon_engine.py` is where the install cost changes, and it carries a hazard worth stating plainly.** It loads `jackboyla/glirel-large-v0` through HuggingFace, and to do so it disables a safety check:

```python
transformers.utils.import_utils.check_torch_load_is_safe = lambda: None
transformers.modeling_utils.check_torch_load_is_safe = lambda: None
```

That check is what refuses to deserialize a `torch.load`-format checkpoint, which is a pickle and therefore an arbitrary-code-execution surface; the comment above it calls it a "security block". Two further patches sit beside it and neither disables a guard — one supplies missing tied-weight attributes on an older `fastcoref` model class, the other defaults two keyword arguments on `GLiREL._from_pretrained` for Hub compatibility. The bypass is one patch applied to two module paths.

One thing bounds the risk: `transformers` and `glirel` are absent from `requirements.txt`, so a reader following the documented install gets `TalonEngine = None` and an inert path — the import is wrapped in `try/except ImportError` and the initializer in a second `try`, so it fails closed twice — and the engine is hardcoded to `cuda:0`. What that bound does not cover is intent. The README's architecture diagram opens with the TALON engine, its prerequisites list a CUDA GPU, and its setup instructs a PyTorch install; a reader who does what the README says is aiming for the configuration in which the guard is off. Nothing in the README tells them so.

**The v0.4 schema work is all on that path.** `DEFAULT_PREDICATE_TAXONOMY` (about fifty Wikidata relations), `ORIGIN_PREDICATES` with its person-to-location directionality rule, `SYMMETRIC_PREDICATES`, `get_canonical_triple_key` — which maps `(A, collaborated_with, B)` and `(B, collaborated_with, A)` onto one key — `is_inverted_asymmetric_pair` and `clean_entity_text` are defined in `talon_engine.py` and referenced in no other file. The canonical key is the exact machinery a store would need to correct a symmetric relation, and `database.py` never calls it.

## 4. Essential Implementation Paths

### The gate — `main.py`, `select_answering_facts`

The query is bundled into one hypervector by summing the vector of every surviving token. Each candidate fact is bundled from **exactly three components**: resolved subject, resolved object, and the predicate's hypervector from `resolve_predicate_hypervector`. Cosine is taken between the two bundles and compared against `HDC_THRESHOLD`, which is `0.55` at this pin.

The three-component rule is deliberate and the README explains it: holding every fact to the same number of components keeps a short fact from scoring higher than a long one for structural rather than semantic reasons. That reasoning is right, and it is more care than most threshold-based retrieval in this corpus receives.

The unhandled half is that the *query* side has no such rule. Tokens are deduplicated by resolved identity and anything of two characters or fewer is dropped unless it is a known entity, but what survives is an unbounded bundle compared against a bundle of three. Because the encoder is near-orthogonal on unrelated strings — measured at `+0.003` mean pairwise cosine — the bundle of n components has a norm proportional to `sqrt(n)`, so the score falls as the question gets longer while the threshold stays fixed. Reimplementing the encoder and the bundling in separate code, with the subject and object shared between query and fact:

| Surviving query components | Cosine | Against the `0.55` in `config.py` | Against the `0.42` the README prints |
| --- | --- | --- | --- |
| 2 | 0.822 | pass | pass |
| 3 | 0.663 | pass | pass |
| 4 | 0.495 | **block** | pass |
| 5 | 0.385 | **block** | **block** |
| 8 | 0.217 | **block** | **block** |

Same fact, same overlap, opposite outcomes — and the window in which a shared-subject-and-object match survives is three tokens wide at `0.55`, two at the `0.72` that preceded it. Sharing all three components buys four either way: `1.000`, `0.868`, `0.691`, `0.553` at n = 3, 4, 5, 6, the last of which clears `0.55` by three thousandths.

**Run the benchmark's own questions through it and none of them clears the gate.** Each scored against the exact triple it asks about:

| Benchmark question | Cosine | `config.py` 0.55 | the 0.72 before it | README 0.42 |
| --- | --- | --- | --- | --- |
| *"Where was Marie Curie born?"* | 0.423 | **block** | **block** | pass |
| *"Where was Alan Turing born?"* | 0.429 | **block** | **block** | pass |
| *"What did Alan Turing crack?"* | 0.450 | **block** | **block** | pass |
| *"Who did Turing work with?"* | 0.367 | **block** | **block** | **block** |

**The threshold moved 0.17 and not one of them crossed.** All four sit between
`0.367` and `0.450`, below both settings, so a recalibration described as
eliminating hallucination leaks changed the verdict on none of the sampled
answerable questions. The number the change was made for is the one the
verification suite computes and does not assert.

The two threshold columns are both the project's own: `0.72` is what `config.py` sets and `0.42` is what the README's architecture diagram advertises, so the documentation describes a gate that admits three of these four questions and the code ships one that admits none. For a system whose central claim is refusing to answer when it should, the threshold is the most important number in the repository, and raising it *"to eliminate hallucination leaks"* is the move that trades answers for refusals without changing what the gate measures. The README's own table records the trade in the two columns that depend on it: retrieval accuracy fell from 55.0% to 45.0% and gate accuracy from 56.7% to 43.3% while precision rose. Normalising the query side the way the fact side is normalised — a fixed component budget, or dividing by the component count — is the change the fixed threshold is waiting for, and it is the change that would let the threshold be raised without paying for it in answerable questions.

*These figures are the subword-only regime, which is what runs when the GloVe fetch fails and what applies to any token outside GloVe's trimmed 50,000-word vocabulary. With the table loaded, a predicate or entity found in it is bundled with a SimHash projection as well, which moves the absolute numbers; the norm argument that produces the length dependence does not depend on which regime is active.*

### The refusal — `main.py`

Three `return` statements produce `DETERMINISTIC_GATED_FALLBACK`, and what matters is where they sit. The Ollama call is inside the branch that has already matched facts; every path that fails to match returns the fixed string first. The model is never given a question without evidence, so it has no opportunity to answer one from parametric knowledge.

That is the strongest idea here and it generalizes past the prototype. A system prompt saying "only answer from the provided context" is a request; a control-flow structure in which the un-evidenced case never reaches the model is a property. The cost is equally structural: everything the model could legitimately have contributed — paraphrase, arithmetic, combining two facts — is also unreachable, and the system's ceiling is whatever its triple extractor managed to store.

### Correction — `database.py`, `update_relation`

```python
# Keep all extracted candidates in DB rather than destructively deleting earlier valid facts
                #if predicate in SINGLE_VALUED_PREDICATES:
                #    cursor.execute("DELETE FROM relations WHERE source_id = ? AND predicate = ?", (src_key, predicate))
cursor.execute("INSERT OR REPLACE INTO relations VALUES (?, ?, ?)", (src_key, predicate, tgt_key))
```

**Correction does not happen at all.** The functional-predicate `DELETE` is
commented out, under a comment that gives the right reason — destroying an
earlier valid fact to make room for a later one loses data — and puts nothing in
its place. So a newer `born_in` no longer removes the older one, both rows
persist, and there is no supersession pointer, no tombstone, no timestamp and no
ordering to say which the system now believes. Both are candidates at the next
retrieval, and the gate scores them on cosine alone.

That is a real improvement on the destructive version and it is half a change.
The comment identifies the problem with `DELETE`; the fix for it is a
supersession row or a `valid_to`, not the absence of both.

**The allowlist is the whole correction policy, and it reaches one of the predicates this system produces.** `predicate_map` in `main.py` normalises everything the extractor emits into four canonical forms — `born_in`, `collaborated_with`, `discovered`, `cracked` — of which only `born_in` appears in the set. `capital_of` exists only in the seed data; `died_in`, `place_of_birth` and `place_of_death` appear nowhere but this set, the fifty-relation taxonomy in `talon_engine.py`, and that file's `ORIGIN_PREDICATES`. Anything the model extracts under an un-normalised predicate — the README's own example of extraction noise is `[Grace_Hopper] -[became_a_pioneer]-> […]` — is append-only by construction. `talon_engine.py` does define `get_canonical_triple_key`, which folds a symmetric relation and its inverse onto one key and is precisely what would let `collaborated_with` be corrected; no code outside that file calls it.

So a user who corrects "Marie Curie discovered Radioactivity" leaves both triples in the store, and both are candidates at the next retrieval. The arrangement protects multi-valued relations from data loss and makes single-valued correctness depend on a hand-maintained set of five strings meeting a predicate vocabulary that a language model invents at ingest time. A `functional` column on the predicate, or a supersession row instead of a `DELETE`, would not have that coupling.

### Writes — `main.py`, conversational learning

A user sentence that is not a question goes to a two-pass extraction prompt, and if it parses, `update_relation` is called immediately: *"I have recorded a new factual declaration."* There is no confirmation, no provenance, and no distinction in the store between a fact extracted from an ingested PDF and one the user asserted in passing. Everything the gate later protects rests on this being right.

### Ingestion — `ingestor.py`

Documents are split into blocks of five sentences with two overlapping, dispatched to worker threads (`MAX_WORKERS = 1` by default, with a comment noting the GTX 1070 it was tuned on), and each block is sent to the model for triple extraction. The overlap is a sensible cheap defence against a fact straddling a chunk boundary; the deduplication that would otherwise imply is handled by the triple primary key.

## 5. Memory Data Model

Three tables. `entities(id, name, type)`, `relations(source_id, predicate, target_id)` with the triple as primary key and cascading foreign keys, and `hebbian_weights(entity_a, entity_b, weight)` with the pair as primary key.

What is absent is easier to list than what is present: no timestamp, no provenance, no confidence, no status, no source document, no scope key, no version, no soft-delete column. A stored fact carries exactly its three strings.

Two smaller observations. `PRAGMA foreign_keys = ON` is set on the connections in `_initialize_db` and `update_relation`, but SQLite applies that pragma per connection, and `plasticity.py` opens its own connections without it — so the cascade the schema declares does not apply on the writer that touches entity pairs most often. It happens not to matter, because nothing deletes an entity row outside the full reset. And `hebbian_weights` rows are decayed but never pruned, so the table grows monotonically with the number of entity pairs ever co-active.

## 6. Retrieval Mechanics

Three stages, all on the turn. `link_entities` matches query tokens against entity ids by string; a single SQL statement fetches every triple where a linked entity is the subject *or* the object, which is a one-hop neighbourhood rather than a traversal; the HDC matcher scores and thresholds them.

`query_relation` carries a small fallback worth naming: if the exact predicate misses, it stems both sides — stripping `ed`, `ing`, `s` and collapsing separators — and accepts a substring match in either direction. It is crude and it is honest about being crude, and for a triple store whose predicates come out of a language model with no controlled vocabulary, some such tolerance is unavoidable.

The failure mode is the one the benchmark measures. Extraction produces predicates like `became_a_pioneer` where the query expects `developed`, and no amount of matcher tolerance recovers a relation the extractor never formed. Retrieval quality here is bounded above by extraction quality, and extraction recall is the lowest of the four published numbers.

## 7. Write Mechanics

Every write is synchronous and inline. The user waits for extraction on a conversational assertion; ingestion of a document blocks the console. There is no queue, no background pass and no re-indexing, which for a store of a few thousand triples is a reasonable trade and one the README implicitly makes by targeting a single local user.

Deletion is `/reset` and nothing else. Conflict handling does not exist as a concept: a contradicting assertion is an overwrite, and two facts that disagree can only coexist if their predicates differ.

### Operational cost

- **The write path is synchronous** and dominated by a local model call per block or per assertion.
- **The lag before a memory is retrievable is zero** — the fact is in SQLite before the turn returns.
- **No background pass rewrites the store**, so nothing can silently undo a correction. In a corpus where most deletion claims expire at the next scheduled job, "there are no scheduled jobs" is a real property rather than a missing feature.
- **The read path injects only matched triples plus primed associations**, so the prompt grows with the number of matching facts and nothing bounds it explicitly.

## 8. Agent Integration

There is none, and the report should be plain about it. Hillock is a console application with a hardcoded Ollama URL; there is no MCP server, no HTTP API, no plugin contract and no packaging beyond `requirements.txt`. `/ingest`, `/mode` and `/reset` are the whole surface. Adapting it for another agent means importing `main.py`'s class and calling `execute_chat_turn`, which is possible — the return tuple carries the mode string — but nothing in the repository is arranged for that.

## 9. Reliability, Safety, and Trust

Strengths:

- **The un-evidenced case never reaches the model**, which is a property rather than an instruction.
- **The benchmark's hard negatives are committed with their reasoning**, ten of them, each annotated with why the text does not support an answer.
- **Facts are normalized to a fixed component count before comparison**, so fact length does not distort ranking.
- **Every hyperparameter is in one file**, named, with the calibrated threshold marked as calibrated.
- **The optional GPU path fails closed twice** — on import and on initialization.
- **No background job can undo a correction**, because there are none.
- **The published numbers are unflattering and prominent**, with a written account of why they are low.

Gaps:

- **The reservoir has no test.** The recurrence that revived it is one term in one line, and nothing asserts the state changes when a token is fed to it.
- **The gate's threshold is length-sensitive**, so admission depends on phrasing in a way nothing in the repository states.
- **The published gate accuracy pools blocking with answering**, and the pooled number is dominated by the twenty answerable questions.
- **Correction reaches one predicate the system actually produces**, and is destructive and unrecorded where it does.
- **Nothing stored carries provenance, time or trust**, so a user assertion and a PDF extraction are indistinguishable afterwards.
- **No scope of any kind**, which is consistent with one local user and worth stating anyway.
- **`talon_engine.py` disables a checkpoint-deserialization guard** on the path the README's architecture diagram and prerequisites point at.
- **A stated capability rests on a component that does not run**, which is the general form of the first gap and the one a reader should check for themselves before adopting anything here.

## 10. Tests, Evals, and Benchmarks

**`verify_hillock.py` is a 20-point CPU verification suite** — the repository's
first assertions outside the benchmark. It covers eight areas without a GPU or
the TALON models: SQLite seed counts and single-valued predicate overwrite, the
Hebbian strengthen and decay constants *"vs README math"*, VSA determinism,
bipolar output and binding orthogonality, the v0.4 span cleaners and
inverted-pair purge, coreference span replacement with character offsets, the
ingestion path's loud halt when the TALON stack is absent, a benchmark
seed-contamination arithmetic check, and a gate score distribution. It exits
non-zero on any failure. Checking a decay constant against the number the README
publishes is the right instinct, and so is asserting that the ingestion path
halts loudly rather than degrading when its extractor is missing.

**Check 8 computes the number this report is about and asserts nothing with
it.** It builds a seed-only database, runs every benchmark question through
`select_answering_facts` with `threshold=-1.0` — the gate disabled, so the raw
score distribution comes back — and then:

```python
passes = sum(1 for a, m, _ in rows if a and m is not None and m >= HDC_THRESHOLD)
leaks  = sum(1 for a, m, _ in rows if not a and m is not None and m >= HDC_THRESHOLD)
check("gate-distribution-ran", len(rows) == 32, f"verified gate distribution on {len(rows)} queries")
```

The `32` is the whole of what the file has changed since the benchmark grew:
the fixture went from thirty questions to thirty-two, and the assertion's
constant was updated to match. `passes` and `leaks` are each assigned once, on
the two lines above, and appear nowhere else in the repository — the line was
edited without the question being asked.

`passes` is how many answerable questions clear 0.72. `leaks` is how many baited
ones do. Neither identifier appears again in the file. The only assertion is that
thirty rows were produced — that the distribution *ran*, not what it said. So the
suite reaches the exact measurement the gate's calibration turns on, computes
both halves of it, and checks the row count instead. Two live numbers and a
tautology, and the check's own name says so.

The repair is one line each and needs no new machinery: `check("gate-admits-answerable", passes > 0, ...)` would fail today and is the assertion the threshold has never had.

**I ran nothing from this repository.** The screen found no auto-executing surfaces and no dependency inside the cooldown, but the benchmark requires a local Ollama with a pulled model and its numbers are model-dependent by construction — and a first launch would fetch 822 MB from `nlp.stanford.edu`. The reservoir, encoder and gate findings above are all reproductions: the subword encoder and the bundling arithmetic were reimplemented from `reservoir.py` and `main.py` in a separate file and run against a throwaway virtualenv holding nothing but NumPy.

`evaluate_hillock_PROTO_ish.py` is better than its filename, and it runs
unseeded. Rather than calling `clear_and_reinitialize()`, it deletes
`relations`, `hebbian_weights` and `entities` outright and then clears the
in-process HDC state, codebook and vocabulary book — *"to ensure 100% pure,
unseeded benchmark evaluation"*. Clearing the in-memory codebook as well as the
tables is the half that is easy to miss: a reservoir that kept its vocabulary
would carry the seeds' encodings into a run whose database no longer held them.
Beside it, the verification suite's seventh check asserts the contamination
arithmetic directly — four initial seeds overlap the evaluation targets — so the
quantity is pinned rather than argued.

It writes its own fixtures, ingests, queries, and scores four metrics. Twenty questions carry an expected subject, predicate and object; ten are negatives, each with an inline comment giving the reason: *Newton is 1600s, Tesla is 1800s*; *Curie discovered radioactivity, Einstein didn't*; *Enigma is target object, testing link-routing direction*. Those ten are committed cases asserting that particular material must not be returned on a read path, which is the [negative retrieval assertion](../../patterns/rejected-value-tombstone/) this atlas counts, and annotating each with its rationale is rarer than the assertion itself.

Two things are wrong with the scoring, and they are worth separating from the low scores themselves.

**`gate_acc` is not a gate metric.** The formula is `(correct_blocks + correct_answers) / len(questions)` — thirty questions, of which twenty are answerable — so a system that answered every answerable question and blocked nothing would score 66.7% on a metric the script labels *"Hallucination defense rate"*. A system that blocked everything would score 33.3%, which is lower than the 43.3% reported and higher than four of the seven rows in the README's version table. Pooling a positive obligation with a negative invariant into one scalar is exactly the failure the [AOEP-v0 protocol](../../benchmarks/#aoep) separates its scorecard to avoid, and this is the clearest live instance of it in the corpus.

**The two published numbers together imply the gate's actual performance.** With `retrieval_acc = correct_answers / 20 = 45.0%`, `correct_answers` is 9; with `gate_acc = (correct_blocks + 9) / 30 = 43.3%`, `correct_blocks` is 4. So the hard-negative block rate behind the headline "Gate Accuracy 43.3%" is **four of ten**, and six of the ten baited queries produced what the script itself names a `HALLUCINATION_LEAK` — after a threshold recalibration whose stated purpose was to eliminate them. The reported figure is not wrong arithmetic; it is a label that does not describe its formula, and the label is what makes the recalibration look like it worked.

**No run output is committed** — no JSON, no log, no results file — so all twenty-eight numbers in the README's version table rest on the author's report of local runs. The harness and the full fixture set being committed puts this well ahead of the published-numbers-without-artifacts antipattern this atlas names elsewhere, and one committed output file would close the gap entirely.

**No paper, arXiv reference or citation file exists in this repository.**

## 11. For Your Own Build

### Steal

- **Make the refusal control flow.** If the retrieval step returns nothing, return a fixed string and do not call the model. A prompt asking a model to decline is a request; a branch that never reaches the model is a guarantee, and it costs less code than the prompt does.
- **Normalize what you compare before you threshold it.** Holding every candidate to the same component count so length cannot inflate similarity is the right instinct — and then apply it to *both* sides, or the fixed threshold you calibrated moves under you.
- **Commit the negatives with their reasons.** Ten unanswerable questions, each with a comment saying why the source text does not support an answer, are worth more than a hundred recall cases, and the comments are what let a later reader check the test rather than trust it.
- **Publish the number that embarrasses you**, with the diagnosis beside it — and keep the row after it stops being your best. A seven-row version table that still shows the release where gate accuracy peaked at 60.0%, two releases before the current one, is worth more than any single figure in it. The discipline to finish is writing the prose under the table about the columns that *fell*, not only the ones that rose.
- **Put every constant in one file and mark the ones you calibrated.** At this size it turns "what would I tune" into a five-minute question.
- **Decay by turn when you have no clock.** If nothing in the schema carries a timestamp, decaying associations per interaction is coherent; adding a half-life in days would not be.

### Avoid

- **A recurrence with no additive term.** `state = decay*state + f(state, token)` is zero-preserving, and a zero-initialised state stays zero forever however long you run it. The assertion that catches it is one line — feed a token, check the norm moved — and it belongs beside any state you carry across turns.
- **A hand-maintained list of which predicates are functional.** If the vocabulary is invented by a language model at ingest time and the list is five strings in a source file, the two will not meet. Put the property on the predicate, or supersede instead of deleting.
- **A threshold calibrated against one input shape.** If the score depends on a property of the query the threshold does not know about — length, token count, language — the gate is measuring phrasing as much as relevance.
- **Raising the threshold as the fix for a leak.** It is the one knob that always appears to work, because it moves both error rates in the direction the metric you are watching happens to reward. Without an assertion pinning what the gate must still admit, the version that stops the leaks is also the version that stops the answers, and only a metric that separates the two obligations will show it.
- **A single scalar over positive and negative obligations.** Blocking what must be blocked and answering what must be answered are different jobs with opposite degenerate solutions; a pooled score hides which one you failed.
- **Keying a correction on `(subject, predicate)` for every relation.** It silently makes them all functional, and the first multi-valued predicate you meet loses data with no error — but narrowing it to an allowlist trades that for relations nobody can correct at all. Both failures are quiet.
- **Disabling a deserialization guard to load a model**, especially in a module the README does not list. If the optional path needs it, say so where the person installing it will read it.

### Fit

This is a prototype and says so, so the question is not whether to deploy it but what to take from it. The gate is the answer: it is the cleanest demonstration in this atlas that "the system will not answer without evidence" can be a structural property, and it fits in a file you can read in one sitting. Take that.

Do not take the storage layer. Three strings per fact with no time, no source and no status is below the floor for anything that has to be corrected later, and the destructive update makes the first multi-valued predicate a data-loss event. Anyone who wanted to build on this would be adding those columns before adding anything else — which is a compliment to how little else is in the way.

The hyperdimensional layer is the part to be most careful about, and not because the idea is wrong. Gradient-free symbolic vector matching over a codebook is a real technique with a real literature, and the matcher here is a working instance of it — the subword encoder in particular earns its place, giving `born` a `+0.32` cosine against `born_in` for the cost of an MD5 per n-gram. What a reader should check is which half of any given release runs: the architecture diagram is drawn around an extraction engine whose five imports are not in `requirements.txt`, the schema and directionality work is defined in that same unreachable file, and the semantic half of the encoder depends on a table the first launch downloads without asking.

## 12. Open Questions

- Does the revived reservoir resolve pronouns correctly in practice, or does the bundle term dominate the permutation-bound term enough that word order stops mattering?
- Is the five-predicate allowlist meant to grow with the extractor's vocabulary, and what maintains it?
- `HDC_THRESHOLD` has been `0.42`, `0.78`, `0.68`, `0.72` and `0.55` across five releases, under a comment that has read *"Recalibrated gating threshold to eliminate hallucination leaks"* for the last two of them. What is any of them calibrated against, and could anything committed say? `leaks` is computed once per verification run and discarded, and the four questions scored in section 4 block at `0.72` and at `0.55` alike.
- What is the intended behaviour for a genuinely multi-valued predicate — is `collaborated_with` meant to hold one target, or is the `DELETE` an oversight?
- The README presents `talon_engine.py` as the architecture and instructs a CUDA PyTorch install, while `requirements.txt` names none of the five packages that file imports. Is the omission deliberate, and does the author know the patch disables a `torch.load` guard on the path the README points at?
- Is the GloVe fetch — 822 MB from `nlp.stanford.edu` on first launch, unmentioned in the setup instructions — intended, or a development convenience that shipped?
- Do the version table's rows come from one run each, and would committing those runs' outputs be acceptable given they depend on a local model?
- What does `passes` read on a real run? The verification suite computes it and
  discards it; the number would settle the calibration question above in one
  line of output, and asserting it is the difference between a suite that
  measures the gate and one that checks it.
- The GloVe fetch survives a corrupt or truncated zip by re-downloading and
  verifies nothing about what arrives. `hashlib` is already imported in
  that file — for n-gram seeding — so a digest check is available where it is
  needed.

## Appendix: File Index

- Gate, matcher, entity linking, console loop: `main.py` (`select_answering_facts`, `execute_chat_turn`, `link_entities`, `resolve_entity_identity`).
- Schema and all SQL, including the destructive correction: `database.py` (`update_relation`, `query_relation`, `get_all_facts_for_entities`).
- Hebbian reinforcement and decay: `plasticity.py` (`update_associations`, `get_associated_priming_context`).
- VSA context math: `reservoir.py` (`step`, `get_context_fingerprint`).
- Document chunking and the optional GPU extractor: `ingestor.py`, `talon_engine.py`.
- Benchmark, fixtures and metrics: `evaluate_hillock_PROTO_ish.py` (`generate_test_assets`, `run_evaluation`).
- Hyperparameters: `config.py`.
- Verification suite: `verify_hillock.py` (eight areas, twenty checks; check 8 holds the unasserted gate distribution).
- Launchers: `run.sh`, `run.bat`.

## History


**2026-08-30** — [`5fdaeffe7dadee52a15cf1772b46013cc1af256a`](https://github.com/roandejager/Hillock/commit/5fdaeffe7dadee52a15cf1772b46013cc1af256a) — re-pinned four commits on, at v0.6.0 with HYDRA late interaction and an `hdc_reservoirs` blob table for multi-hop path vectors. The mark is unchanged at one: the benchmark fixture grew from thirty questions to thirty-two and still carries ten unanswerable ones, so `negative_eval` holds on the same basis.

**`HDC_THRESHOLD` took its fifth value and nothing the report scores changed hands.** `0.42 → 0.78 → 0.68 → 0.72 → 0.55`, under a comment that has read *"Recalibrated gating threshold to eliminate hallucination leaks"* for the last two settings. The section 4 tables carry the new column: the four benchmark questions sit at `0.367`–`0.450` and block at `0.72` and at `0.55` alike, so a 0.17 move changed the verdict on none of them. The component-window table shifts by one — a three-component query now passes where it did not — and the README's advertised `0.42` still admits three of the four.

**The verification suite's one edit in this window was the constant.** `verify_hillock.py` changed exactly one line, `len(rows) == 30` to `len(rows) == 32`, keeping the check named `gate-distribution-ran`. `passes` and `leaks` are still assigned on the two lines above it and appear nowhere else in the repository, so the quantity the recalibration is named for is computed once per run and discarded — and this time the line was edited without the question being asked. The open question about what the threshold is calibrated against is narrowed accordingly: nothing committed can answer it.

**Correction stopped happening.** `database.py`'s functional-predicate `DELETE` is commented out under *"Keep all extracted candidates in DB rather than destructively deleting earlier valid facts"*. The reason is right — destroying an earlier valid fact to make room for a later one loses data — and nothing replaces it, so a newer `born_in` leaves the older row in place with no supersession pointer, no timestamp and no ordering, and both are candidates at the next retrieval. The matrix's `update_delete` and `storage` fields are corrected for that and for the fourth table.

Screened again first: no auto-run surface, no build-time execution surface, one unpinned surface and one manifest inside the seven-day cooldown; nothing was installed and nothing was run.
**2026-08-27** — [`a30ce1a25f0d5763f10a6e591feb2a8122175180`](https://github.com/roandejager/Hillock/commit/a30ce1a25f0d5763f10a6e591feb2a8122175180) — re-pinned six commits on, at v0.6. Screened again: no auto-run surface, no build-time execution, one unpinned surface; nothing was installed and nothing was run. The mark is unchanged at `negative_eval`.

The release is a hypergraph pass — a MaxSim sub-dimensional cascade in `reservoir.py`, positional permutation and sequential path binding for multi-hop paths, token-level late interaction replacing query bundling, and SQLite blob storage for hyperdimensional vectors. Two checks were added to `verify_hillock.py` with it, and both are real properties that can fail: permutation orthogonality asserts `abs(cos(orig, perm)) < 0.12` on a rolled vector, and the sequential-path check asserts the bound path stays bipolar with `set(np.unique(path_hv)) <= {-1, 1}`.

**The gate-distribution check beside them still tests that the instrument ran rather than what it measured.** `verify_hillock.py` scores thirty questions against `HDC_THRESHOLD`, computes `passes` — answerable questions whose top score cleared the gate — and `leaks` — *unanswerable* questions whose top score cleared it — and then asserts neither:

```python
passes = sum(1 for a, m, _ in rows if a and m is not None and m >= HDC_THRESHOLD)
leaks  = sum(1 for a, m, _ in rows if not a and m is not None and m >= HDC_THRESHOLD)
check("gate-distribution-ran", len(rows) == 30, f"verified gate distribution on {len(rows)} queries")
```

Neither local is referenced again. The check name is accurate — the assertion is that thirty rows were produced — and `leaks` is the number that decides whether the gate admits material for questions it should refuse, which is the property the gate exists for. The harness is otherwise a genuine gate: `check` collects results and `main` ends `sys.exit(1 if fails else 0)`, so a failing property does fail the run. This one cannot fail.

**2026-08-23** — [`803e7a23835194b3b1d63037af4b2be8fe034c78`](https://github.com/roandejager/Hillock/commit/a30ce1a25f0d5763f10a6e591feb2a8122175180) — second reading, fourteen commits on, at v0.5. Screened again first: no auto-executing surface, no build-time execution, nothing inside the seven-day cooldown, and one unpinned surface — nine `>=` requirements. Nothing was installed and nothing was run. The gate is unchanged: `HDC_THRESHOLD` is still `0.72`, `select_answering_facts` and the reservoir's similarity math are untouched apart from logging moving behind a debug verbosity level, so every finding about the gate stands at this pin. Two things changed that bear on the report. The benchmark harness became genuinely unseeded — it now deletes all three tables and clears the in-process HDC state, codebook and vocabulary book rather than calling `clear_and_reinitialize()` — which removes the seed contamination the previous reading had to reason around. And `verify_hillock.py` arrived, the repository's first assertions outside the benchmark: twenty checks over eight areas, exiting non-zero on failure, including a Hebbian constant checked against the README's published math. Its eighth check computes how many answerable questions clear the threshold and how many baited ones leak, and asserts neither — the only assertion is that thirty rows were produced. The rest of the release is the console: a Rich dashboard, `/inspect` and `/status`, model switching over local Ollama models, token streaming, configurable debug verbosity, and `run.sh` / `run.bat`. The GloVe fetch gained corrupt-zip recovery and still has no checksum.

**2026-08-13** — [`976780453be026a32acbd5ee92cf4fe2adaf6c3f`](https://github.com/roandejager/Hillock/commit/976780453be026a32acbd5ee92cf4fe2adaf6c3f) — twenty commits on, v0.2.3 to v0.4.1, with every one of the eight source files changed. Screened again before reading: 0 auto-run surfaces, 0 build-time exec, nothing inside the cooldown, one unpinned manifest — identical to the previous two screens. Nothing from the repository was executed; the encoder and bundling arithmetic were reimplemented in a separate file and run in a throwaway virtualenv holding only NumPy.

**Three published claims went stale, all in the same direction.** `HDC_THRESHOLD` moved `0.42 → 0.78 → 0.68 → 0.72`, so the cosine table in section 4 was recomputed. The codebook is no longer random: `get_or_allocate_hypervector` routes every string through `resolve_predicate_hypervector`, so a hypervector is now a deterministic function of its characters rather than a fresh random draw per launch — which retires the hand-written predicate synonym table and gives `born` a `+0.32` cosine against `born_in`. And the four README scores became a seven-row version table whose current row reads 15.5% / 50.0% / 45.0% / 43.3%, so the implied hard-negative block rate moved from three of ten to four of ten.

**One claim was imprecise when written rather than overtaken.** The report described a third monkey-patch as overriding `GLiREL._from_pretrained` *"similarly"* to the `check_torch_load_is_safe` bypass. At that pin and at this one it defaults two keyword arguments for Hub compatibility, and the patch beside it supplies missing tied-weight attributes to an older `fastcoref` class. There is one security bypass, applied to two module paths.

**What the recalibration bought and what it cost.** The comment on the new threshold reads *"Recalibrated gating threshold to eliminate hallucination leaks"*. Reproducing the arithmetic, all four of the benchmark's own answerable sample questions now score between `0.367` and `0.450` against the exact triple they ask about — every one below `0.72`, where three of the four cleared `0.42`. The README's own table records the trade: retrieval accuracy `55.0% → 45.0%` and gate accuracy `56.7% → 43.3%` while extraction precision rose `11.5% → 15.5%`. Six of ten hard negatives still leak.

**The optional path became the documented one and stayed uninstallable.** The README's architecture diagram now opens with the TALON engine, the prerequisites list a CUDA GPU, and the setup instructs a PyTorch install from an external index — while `requirements.txt` remains `numpy`, `psutil`, `pypdf` and names none of the five packages `talon_engine.py` imports. All of the v0.4 schema work — the fifty-relation taxonomy, `SYMMETRIC_PREDICATES`, `get_canonical_triple_key`, the directionality guard, the span sanitizer — is defined in that file and called from no other, so the canonical key that would let a symmetric relation be corrected sits beside a `database.py` that never asks for it. `SINGLE_VALUED_PREDICATES` and `predicate_map` are both unchanged, so correction still reaches `born_in` alone.

**One new user-facing behaviour.** `IntegratedHillock.__init__` calls `load_lightweight_glove()`, which on a machine without `glove.6B.50d.txt` — absent from the repository, unmentioned in the README — fetches 822 MB from `nlp.stanford.edu` and extracts it. The README's architecture diagram also still prints `Passed Threshold >= 0.42`, and its self-deprecating opening is gone.

**2026-08-12** — [`a0499a55d0e44787dc0df03f4661dd9b0e7c9480`](https://github.com/roandejager/Hillock/commit/a0499a55d0e44787dc0df03f4661dd9b0e7c9480) — re-read one day past the first pin, at v0.2.3, two commits later. Screened again before reading: 0 auto-run surfaces, 0 build-time exec, nothing inside the cooldown, one unpinned manifest; nothing was installed and nothing from the repository was executed.

[`348f08341e7b9dfd42a10d5a23b855e4bd46d0a1`](https://github.com/roandejager/Hillock/commit/348f08341e7b9dfd42a10d5a23b855e4bd46d0a1) changes three things in twenty-five added lines. `reservoir.step` gains `+ token_hv`, so the recurrence has an additive term and a zero-initialised state leaves zero — reproducing both forms in separate code, the previous rule holds a norm of `0.0` across five steps where the current one climbs to `34.4`. `update_relation` narrows its `DELETE` to a set of five named functional predicates, so a second `collaborated_with` no longer removes the first. And `select_answering_facts` deduplicates query tokens by resolved identity and drops tokens of two characters or fewer.

**What the second fix trades.** Removing the data loss for multi-valued relations leaves correction reaching only `born_in`: `predicate_map` normalises the extractor's output into `born_in`, `collaborated_with`, `discovered` and `cracked`, and only the first is in the allowlist, while `died_in`, `place_of_birth` and `place_of_death` appear nowhere else in the tree but the optional GLiREL label list. A corrected `discovered` fact now leaves both triples in the store. The report's previous statement — that the delete keyed on `(subject, predicate)` made every relation functional — was accurate at that pin and describes a defect the project has replaced with a narrower one.

**What the third fix does not change.** The report's claim that the gate's operating point moves with question length holds at this commit: the fact side is still exactly three components, the query side is still unbounded, and `HDC_THRESHOLD` is still `0.42`. The two-character filter removes nothing from three of the benchmark's own four sample phrasings and one token from the fourth, so the crossover between passing and blocking still sits between six and eight surviving components.

The README, its four published metrics and `config.py` are untouched by the commit, so the numbers on the front page describe the extraction, matching and gating behaviour of the previous version.

**2026-08-11** — [`62f75e0c2b70a92991b47c14b320742b026ad3ce`](https://github.com/roandejager/Hillock/commit/62f75e0c2b70a92991b47c14b320742b026ad3ce) — first reading, on the `master` default branch, at the fifty-sixth commit of a repository created 11 June 2026. Screened before reading: 0 auto-run surfaces, 0 build-time exec surfaces, 0 dependency surfaces inside the cooldown, 1 unpinned manifest (`numpy`, `psutil`, `pypdf`, none pinned); nothing was installed and nothing from the repository was executed. The reservoir and gate-geometry findings were checked by reproducing the arithmetic in separate code rather than by importing the modules.

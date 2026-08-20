# The vocabulary probe lies, in both directions

**Status:** method, with eight instances — five from one day, three added a
day later from SkillEvaluator, fx and TrueForge.
**Origin:** screening qmd, kitaru, SAM, Warp and ai-tutor-app in sequence and
watching the same cheap check mislead each time differently.

## The check

Grepping a tree for `remember`, `recall`, `belief`, `supersede`, `tombstone`,
`forget`, `provenance` is the fastest way to decide whether a repository is
worth a deep read. It is worth keeping — it settled four of five of these in
minutes. It also produced a wrong answer in every one of them until the hits
were read, and the wrongness has a small number of recurring shapes.

## Poisoned by a committed artifact

**Warp** returns dozens of hits for `tombstone`, `supersede` and `forget`. The
sources are a committed **BERT tokenizer vocabulary**
(`crates/input_classifier/models/onnx/bert_tiny_tokenizer.json`) — an English
wordlist, so it matches almost any probe — and the **vendored Alacritty
licence**. Excluding files under `models/` and any `LICENSE*` before counting is
the fix, and it should be the default.

## Poisoned by the measurement vocabulary

**qmd** returns 52 hits for `recall`. Every one is `recall@1`, `recall@3`,
`avg_recall_at_k` in its benchmark harness — information retrieval's word, not
memory's. Any repository that scores itself will do this.

## Poisoned by the systems vocabulary

**SAM** returns seventeen `memory` hits, all of them RAM: in-memory libp2p hosts
in tests. Its one `remember` is a comment about caching a failed dial so a node
does not retry into a fifteen-second timeout. **Kitaru**'s three `supersede`
hits are a worker's task-claim lease being taken by a newer attempt.

## Poisoned by the framework

**ai-tutor-app** returns 319 `memory` hits, and the word is LangChain's:
compaction middlewares, checkpointers, `InMemoryStore`. A RAG application built
on a framework whose conversation buffer is called memory will always look like
a memory system to a grep.

## Poisoned by the substring, which is the cheapest one to miss

**SkillEvaluator** returns ten hits for `recall`. Every one is the substring
inside **`IgnoreCallback`**. Not a poisoned corpus, not a borrowed vocabulary —
just a short probe word living inside a longer ordinary identifier, in a
codebase that has nothing to do with memory. `recall` is the dangerous one here
because it is five letters and appears inside `Callback`, `recallable` and
`precall`; `forget` and `tombstone` are long enough to be safe.

**fx** is the same shape three times over and is the reason to check the
discriminating words rather than the common one. Its counts look promising —
`memory` 229, `remember` 26, `recall` 15, `forget` 11 — and every one is
something else: `memory` is Zig's allocators, `remember` is `rememberFailure`
in the UI error path, `forget` is `forgetShimmer` in the transcript animation,
and `recall` is shell-style **prompt history**, the up-arrow. The repository does
have a real memory tool. Not one of those 281 hits is it; it was found by reading
the tool directory listing.

**TrueForge** rounds it out from the other side: 13 `memory` hits, all RAM —
`InMemorySessionStore`, "in-memory state", "Redis/in-memory key" — with `recall`
and `forget` at zero. Here the probe's *shape* was right (the low counts on the
discriminating words were the true signal) and the `memory` count was noise, in a
language where every third file allocates.

The rule these three add: **a manual-memory language guarantees a high `memory`
count and tells you nothing.** In Zig, Rust, C and C++, drop `memory` from the
probe entirely and weight `recall`/`forget`/`supersede`/`tombstone` — then read
them, because `recall` is short enough to hide inside a callback.

## The opposite failure, which is worse

A probe that comes back **clean** feels like a settled answer and is the case to
check hardest, because a scoped search proves nothing about the paths it did not
cover.

**Warp is the instance.** Searching `crates/` for the memory-store command
symbols found argument structs and no implementation — the exact signature of
declared-and-unwired, and I nearly wrote it up as one. The implementation is in
`app/`, which `crates/` does not contain. What caught it was running the
producer check **across the whole tree** rather than the subtree the first
search happened to pick. The finding reversed completely: from "a command
surface with nothing behind it" to "a REST client against a server-side store".

## What to keep

1. **Exclude `models/`, `LICENSE*`, `vendor/` and lockfiles before counting.**
   A committed wordlist matches everything.
2. **Read three hits per term before believing a count.** One line of context
   separates `recall@k` from recall.
3. **A clean probe is a hypothesis.** Confirm it by naming what the durable
   store actually holds — SAM's twelve tables, qmd's four — rather than by the
   absence of a word.
4. **Scope a producer check to the repository, not to the directory you were
   already reading.** The one time this went wrong, the search was correct and
   the subtree was not.
5. **State the trap in the entry.** Every one of these is written into the
   published entry for that repository, so the next reader does not re-derive
   it from the same grep.
6. **Drop `memory` from the probe in a manual-memory language.** Zig, Rust, C
   and C++ guarantee a high count from allocators alone. The discriminating
   words are `recall`, `forget`, `supersede` and `tombstone` — and `recall` is
   short enough to hide inside `IgnoreCallback`, so it needs reading even when
   it is the only hit.
7. **A tool directory listing beats a grep.** fx's real memory system was found
   by running `ls src/tools/`, after 281 vocabulary hits had pointed at
   allocators and UI animation state. Where a codebase names its capabilities as
   directories, read the names.

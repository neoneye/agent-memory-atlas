---
name: use-the-atlas
description: Design, review, or build a memory system for some other product, using the Agent Memory Atlas as the reference. Use when asked to add memory, persistence, or recall to a repository, to review an existing memory implementation against the atlas, or to decide which memory patterns a product actually needs. Runs in one of four modes — decide, design, review, build — and only the last one writes code, after its own approval.
---

# Use the Atlas

The other three skills in this repository grow the corpus. This one spends it.

**The failure this skill exists to prevent:** an agent pointed at 155 reports
reads widely, finds the most rigorous mechanism, and builds it. The result is a
tombstone and a governed write gateway on a single-user notes app that needed
scoped SQLite and an explicit write path. The atlas's own pattern index says the
correctable stack is *"one stack among several, not a bar the others fail to
clear"* — and a warning addressed to a human reader does not constrain an agent
unless something makes it.

So the discipline here is subtractive. **Adopt the smallest set that closes a
failure this product can actually suffer, and write down what you deferred.**

## Pick a mode first, and do not drift out of it

The four jobs people ask for are different, and three of them do not touch the
target repository. State which one you are in before you start, and **treat
approval of an artifact as approval of that artifact only** — a person who
approved a build brief has approved a design, not a commit.

| Mode | You produce | You may modify the target repo |
| --- | --- | --- |
| `decide` | which patterns this product needs, and why | no |
| `design` | the build brief | no |
| `review` | a closure report over the memory that already exists, with the open rows named | no |
| `build` | brief → **separate approval to implement** → code and tests | yes, after that second approval |

Default to the narrowest mode the request supports. "What does my memory design
need?" is `decide`. "Review my memory implementation" is `review` and ends with a
report — the gaps it finds are findings, not a work order. Moving from `design`
to `build` needs the developer to say so after reading the brief; the brief being
approved is not that sentence.

## What you read, and what you do not

Do not read the system reports. Read these, in order:

1. `content/patterns/index.md` § *How to use the library* — failure → pattern.
2. The same page's § *Stacks, by what you are building* — five profile rows, each
   naming the failure that hurts for that shape, each with a *what you can defer*
   paragraph.
3. The pattern pages you selected — `Cost to adopt`, `Tradeoffs`,
   `Implementation checklist`, `Tests to require`, `Seen in the atlas`.
4. `content/overview.md` § 8 *What I Would Build* (ship-first order) and § 10
   *Practical Checklist*.
5. `content/benchmarks.md` § 6 and § 7 when you need the deletion and
   contradiction tests in detail.

Open a system report only when a pattern page cites it for the exact mechanism
you are borrowing. Then pin it: the report describes one commit, and so does
anything you copy from it.

## The steps

### 1. Read the target repository before reading the atlas

Determine, from the code where possible: single-user or multi-tenant; passive
assistant or an agent that acts; what becomes memory; what breaks when a memory
is wrong; the correction and deletion obligations; the privacy boundary; the
latency and cost budget; the database already in the stack.

Ask the developer only where two readings produce materially different designs.
"Do you have users other than yourself?" is worth asking. "Do you want good
memory?" is not.

### 2. Propose a profile, then argue with it

Pick the row from the stacks table. Say which row and why in one sentence. If no
row fits, say `none` and name the failure you are designing against instead —
the table is a starting point, and five rows do not cover every product.

### 3. Write the build brief and stop

Follow `.agents/protocol/build-brief.md`. Every `adopt`, `defer` and `reject`
line carries a reason. **A brief with an empty `defer` list means the failure
analysis did not happen** — go back to step 1.

Then stop. In `decide` and `design` this is where the work ends. In `build`,
implementation needs a second, explicit go-ahead after the brief has been read —
approval of a design is not authorization to write to someone's repository. Do
not write code first and present the brief as documentation of what you already
built.

### 4. Implement in an order where each stage stands alone

Ship-first order from § 8, which is deliberately not the order a demo suggests:

1. Scope and primary storage.
2. Raw evidence capture, durable and model-independent.
3. Minimal lexical retrieval — FTS is enough to be useful.
4. Derived memory with provenance back to the evidence.
5. Correction and deletion, reaching every projection.
6. Background enrichment and vector retrieval.
7. Audit, telemetry, and the repair paths.

**Nothing above stage 4 may be a prerequisite for remembering anything.** A
memory system whose capture path depends on an embedding service or a model call
loses data when either is down — the atlas's zero-LLM-capture pattern is the
argument, and several reports are the evidence.

### 5. Run the tests by id

The ids are in `.agents/protocol/tests.yaml`, each with a portable given/when/then
and a statement of what a pass does not prove. Implement them in the target
project's own test framework. `scripts/check_protocol.py` validates that
catalogue against the pages it cites, so a test whose source argument has moved
fails this repository's build rather than misleading yours.

In `review` mode you run the same ids against the implementation that already
exists, and the output is the closure report in step 6 — including the rows that
come back open.

Two rules. **Assert absence, not ranking** — a scope test that checks the wrong
memory ranks low has tested nothing. And **score the assembled prompt, not the
retriever** — truncation, dedupe and ordering sit between recall and the model,
and any of them can drop a memory that retrieval correctly found.

### 6. Produce the closure report and the lock file

The table from `.agents/protocol/build-brief.md`: pattern, where it lives, test,
result. **Do not call it a conformance report.** The atlas certifies nothing and
has run its own deletion sequence against no system. Report which failure modes
are closed and which are open; an open row is an honest result, and a report with
no open rows in a system with a vector index is the one to disbelieve.

Write `memory-atlas.lock` into the target repository so the next review can be
small.

## Rules that apply to everything you write

- **Absence is scoped to a commit.** "Not found" means not found in the inspected
  code at that pin. Never upgrade it into a claim about a project or the field.
- **Never cite stars, downloads or adoption** as evidence that a mechanism is
  sound. This project has a standing rule and a note about what it cost to learn.
- **Never hand-copy a count.** "9 of 155" is generated from frontmatter and goes
  stale. Link to the capability index instead.
- **Patterns compose at the intersections, and that is where they fail.** A
  tombstone is decorative if three ungoverned write paths bypass it; hybrid
  retrieval without scope means better recall and a wider blast radius.

## When the answer is "you do not need this"

A prototype with one user, manual writes and no extraction needs scoped storage,
an explicit write path and addressable memories with real `update` and `delete`.
That is a complete and correct answer, and saying so is worth more than a design
document. Write the brief anyway — three `adopt` lines and a `defer` list with
reasons is exactly the artifact that makes the next decision cheap.

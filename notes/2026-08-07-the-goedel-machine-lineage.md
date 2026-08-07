# The Gödel machine lineage — an optimizer's state is not a memory

**Status:** triaged. One repository read and excluded with the reasoning
recorded; the theory and the paper read as prior art rather than as candidates.
**Origin:** three links submitted together —
[arXiv:2510.21614](https://arxiv.org/abs/2510.21614) (Huxley-Gödel Machine),
[metauto-ai/HGM](https://github.com/metauto-ai/HGM), and Schmidhuber's
[Gödel machine page](https://people.idsia.ch/~juergen/goedelmachine.html). They
are one lineage, and reading them together is what makes the scope decision
interesting rather than routine.

## The lineage

**Gödel machine (2003, revised 2006).** A self-referential problem solver that
*"rewrites any part of its own code as soon as it has found a proof that the
rewrite is useful."* Optimality is global rather than local because the machine
must first prove that continuing to search for alternative rewrites is not
worthwhile. What it stores is an initial proof searcher plus axioms describing
the utility function, the hardware, and its own entire initial code.

**Huxley-Gödel Machine (October 2025; ICLR 2026 oral).** Wang, Piękos, Li,
Laakom, Chen, Ostaszewski, Zhuge and Schmidhuber. The practical approximation:
coding agents that iteratively rewrite themselves, with the search guided by
**CMP** — an aggregate of the benchmark performance of an agent's *descendants*,
used as the indicator of its self-improvement potential. The paper names the
failure it addresses as a **Metaproductivity-Performance Mismatch**: the agent
that scores best now is not the agent whose lineage improves most.

**The implementation** is 12,540 lines of Python at
[`013872d9`](https://github.com/metauto-ai/HGM/commit/013872d95da978483f5b540e531db063d23890da),
screened before reading: 0 auto-run surfaces, 2 build-time execution paths, 21
unpinned requirements, nothing inside the seven-day cooldown. Nothing was
installed, built or run.

## Why HGM is out of scope

The atlas admits a system when **something it stores survives the session with an
identity that can later be corrected.** HGM stores a great deal and none of it is
that.

`tree.py` holds the durable state: a `Node` is a **git commit id** of a
self-modified agent, plus `utility_measures`, a parent pointer and children,
pickled to disk. The tree is what the search consults to decide which
self-modification to expand next. So the thing that persists is a *population of
program versions and their measured scores* — an optimizer's state.

Two details settle it rather than one:

- **Nothing retrieves from it at task time.** The evolved agent solves a
  SWE-bench instance with its tools and its prompts; the tree is read by the
  outer search loop, not by the agent doing the work.
- **The self-improvement step is stateless.** `self_improve_step.py` calls the
  model with `msg_history=None`, and `best_agent/self_evo.md` — the file whose
  name most suggests a durable self-record — is a transcript of the improvement
  *instruction*, not a store the next generation reads. There is no accumulating
  record of what the lineage has already learned about itself.

That is the shape this project has recorded before as *a harness that persists is
not a memory that believes*, and HGM is its strongest instance: the persistent
state is richer than a workflow phase and still not a claim. A utility estimate
sharpens as evidence arrives; it is never *wrong* in the way a belief is wrong,
and there is nothing a correction would attach to.

**Where it would enter the atlas.** Give a generation a durable record of what
its ancestors tried and why it failed — read by the next self-improvement step —
and it becomes procedural memory with a verified-execution gate, which is
[skills as procedural memory](../content/patterns/skills-as-procedural-memory.md)
at the granularity of a whole agent. The current design deliberately puts that
knowledge in the *code* instead, which is a defensible answer and a different
one.

## What the atlas can take from it anyway

**CMP is a credit-assignment rule, and credit assignment is what this atlas keeps
finding unbuilt.** Judging a node by its descendants rather than by its own score
is the same move as refusing to let retrieval frequency stand for truth: both say
*the signal you can measure most easily is not the signal you want*. The atlas's
[decay and reinforcement](../content/patterns/decay-and-reinforcement.md) page
argues this for memories and has no instance that measures a memory by what it
later made possible. HGM measures a *program* that way, and names the mismatch it
corrects.

**Git is the undo.** Every node is a commit, so a self-modification is reversible
by construction — the property [Prime Agent](../content/systems/prime-agent.md)
builds explicitly with before/after snapshots and `rollbackProposal`. A
self-modifying system that versions itself in git gets that for free, and it is
worth naming as the cheap option beside the built one.

**And the Gödel machine belongs in the prior-art conversation.**
[Symbolic prior art](2026-07-28-symbolic-prior-art.md) records that belief
revision, truth maintenance and BDI belief bases are absent from this atlas's
lineage. Self-referential provable self-improvement is a fourth absence of the
same kind — a 2003 formalism for *when a system may rewrite what it is*, where
this corpus's systems rewrite what they believe with no proof obligation at all.
The distance is instructive rather than embarrassing: the Gödel machine demands a
proof of improvement before a rewrite, and the atlas's central finding is that
most memory systems cannot even record that a value was rejected.

## Recorded

`metauto-ai/HGM` goes in the excluded list in `content/overview.md` with the
reasoning above, so a reader who meets it in a list of self-improving-agent
projects finds out here why it is not a memory system rather than re-deriving it.
The two documents are cited from this note only — neither is a repository the
atlas can pin.

# The arrow points one way

**Status:** a decidable test, extracted from two exclusions that looked like
judgement calls and are not. Written after `anthropics/claude-code` was examined
and declined on the same ground `Tencent/UI-Mate` was, and the ground turned out
to be one grep.

---

## The question a skills directory raises

[Skills as procedural memory](../content/patterns/skills-as-procedural-memory.md)
argues that a committed instruction file is memory in the sense this atlas
cares about: durable, retrievable, and consulted before acting. That is right,
and it creates a problem the pattern page does not settle. Every coding agent
now ships a directory of skills, commands, agents and prompt assets. If all of
them are procedural memory, the corpus swallows the entire tooling ecosystem and
the word stops discriminating.

The test that separates them is not the file format, the retrieval mechanism or
the size of the directory. It is the direction of the arrow.

## The test

**Does anything in the tree write one of these files?**

Not *could a person edit it* — a person can edit anything. Whether the running
system, having finished a task, produces or amends an asset the next run reads.
If nothing does, the directory is authored guidance that happens to live beside
an agent, and correction means a human editing a file, which is the same
relationship a README has to the program it documents.

It runs as one command per candidate:

```sh
rg -n --glob '*.{py,ts,js,rs,go,sh}' \
  "write.*(SKILL|CLAUDE\.md|\.claude/)|open\(.*(SKILL|CLAUDE)"
```

Then read every loader it does find, because the interesting failure is a loader
opening in read mode and nothing else touching the path.

## What it decides

**`anthropics/claude-code`** ships 149 files of plugins — skills, commands,
agents, output styles, a rules engine — and 38 of examples. Every loader opens
them to read (`load_rules`, `load_rule_file`, `open(file_path, 'r')`), and the
grep for a writer returns nothing. A finished session teaches the next one
nothing that lives in that tree. Declined.

**`Tencent/UI-Mate`** was declined earlier on the same fact, stated in its own
source comment: *"the workflow writes them, the agent only reads them."* Every
reference to a demonstration file is a load, a glob, or a raise-if-missing.

Against those, the systems the pattern page is actually about:

- **[Voyager](../content/systems/voyager.md)** adds a skill only through a gate.
- **[Verel](../content/systems/verel.md)** clusters *failures* into induced
  candidate rules and requires promotion before one is live.
- **[SESA](../content/systems/sesa.md)** writes a card only from a failure, then
  scores every card it hands out and **deletes** one whose net score has gone
  negative after at least three retrievals.

Three writers, three different write policies, and all three are arguable in a
way a read-only directory is not. That is the tell: where the arrow points both
ways there is a policy to disagree with, and where it points one way there is
only a filing convention.

## Why this belongs beside the boundary taxonomy

[The boundary is doing most of the work](2026-08-30-the-boundary-is-doing-most-of-the-work.md)
sorts exclusions into four kinds and asks that the entries say which kind they
are. This is a refinement of its first kind rather than a fifth: a read-only
skills tree *does* hold something that could be false — a skill can be wrong, and
often is — but nothing in the system can find that out, because the system never
writes one. The falsifiability is real and unreachable, which is a different
sentence from "nothing here is a claim" and should be written differently.

**It also reverses cleanly, which the first kind usually does not.** One release
that distils a completed session back into a skill file makes either repository a
candidate. That is worth stating in the exclusion entry, because it is the only
kind of decline that is a roadmap item rather than a category error.

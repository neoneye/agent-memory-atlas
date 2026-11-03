# Recorded searches that could not match

**Status:** every affected command was re-run at its pin and rewritten on 2026-11-03; each of the 40 reports gained a History entry, and the four appendix entries were corrected in place. `list_inert_recorded_commands.py --check` fails on a new one.

## What happened

Under `-E`, git uses the platform's POSIX regex library unless it was built with PCRE. On macOS that library's extended mode treats `\b`, `\s`, `\w`, `\d`, `\<` and `\>` as escapes it cannot match, and treats `\|` as a literal pipe. Both installed gits behave this way: Apple Git 2.39.5 and git 2.23.0 in `/usr/local`, neither with PCRE. Measured with both:

| Form | `git grep -E` | `git grep` (basic) | BSD `grep -E` |
| --- | --- | --- | --- |
| `\b`, `\s`, `\w`, `\d`, `\<`, `\>` | matches nothing | matches | matches |
| `\|` | literal pipe | alternation | literal pipe |

So `git grep -nE '\.disputed\b' -- src` returns nothing on the machine these reports are written on, whatever the tree holds. A pattern with other alternatives still matches through them, which is why many of the affected commands returned something and the defect went unnoticed. The same commands work on glibc, so a reader on Linux would have seen the hits. The Cindy re-read on 2026-11-03 found two empty searches of this kind at both pins.

A table cell's `\|` is the Markdown escape for `|` and renders as one, so it is not this defect.

## The sweep

66 commands in 41 pages: 61 in 40 reports and five in four appendix entries for examined repositories. Each pin was fetched at depth one (yacmemo's from the archive copy, because upstream returns 404), and each command was run three ways:

- as written;
- with every escape translated to a POSIX form;
- through BSD `grep -E` over `git ls-files` for the same pathspec, which accepts `\b` natively.

The second and third forms agreed on every command that returns nothing. The rewritten commands use `-w` where `\b…\b` wraps the whole pattern, `(^|[^[:alnum:]_])` and `([^[:alnum:]_]|$)` for a single boundary, and `[[:space:]]` for `\s`. Each rewritten command returns what the verified translation returned.

`llm-memory-api`'s `slug_pattern \|\| '%'` wants the literal SQL operator and is exempt by name.

## What the working searches found

Most annotations held: the hits a working search returns are the ones the annotation names, so a working form had been run once and only the recorded form was wrong. Where the claim did not hold:

| Page | Recorded | At the pin |
| --- | --- | --- |
| [kannaka-memory](../content/systems/kannaka-memory.md) | `disputed` has no writer anywhere in `src/` | two writers, `collective/merge.rs:255` and `paradox.rs:665`, both reached only from tests; no reader |
| [kannaka-memory](../content/systems/kannaka-memory.md) | `\bmcp\b`: no match | comments recording the MCP server's removal |
| [hive-mind](../content/systems/hive-mind.md) | no match on a scope predicate | the telemetry dashboard's session filter (`08_read_api.py:392`); no memory read |
| [auraos](../content/systems/auraos.md) | no delete path in code | the browser client drops parsed profile fields from its in-page object; nothing removes stored memory |
| [mnemosyne-nabzx](../content/systems/mnemosyne-nabzx.md) | no match | one doc comment saying there is no garbage collection |
| [otis](../content/systems/otis.md) | no trust-state term | one comment on serving limits |
| [hyperconsciousness](../content/systems/hyperconsciousness.md) | no `material` reader outside `capture.rs` | holds; the hits are recovery-kit key material |
| appendix: overgraph | `remember`/MCP search matches one helper | also the helper's call site and a roadmap sentence on an MCP server |
| appendix: overgraph | tenancy search returns nothing | example properties in two GQL parser tests |
| appendix: open-ontologies | every `memory` hit is RAM, mode or WASM | also a design comment and a credit to synaptic-memory |

Six more annotations gained a hit they had omitted (chump, ciris-agent, gambletan-cortex, memex, muninn and one in sonder-runtime that is unrelated to the escapes: the basic-mode `facade\.record\b` search can match, and returns a test call). No mark moved: every corrected claim narrows to one still true of production code.

## What the gate does not close

It reads `grep` and `git grep` commands, in inline code and fenced lines. A search written with `sed`, `awk` or `find -regex` is not read. It cannot see a recorded "no match" that was never run, and it checks the form, never the result.

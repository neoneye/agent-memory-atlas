---
title: "OKF Agent Memory"
eyebrow: "Three frontmatter fields look like trust state; the one search reads promotes rather than withholds"
description: "A Go implementation of the Open Knowledge Format that keeps agent memory as markdown in the repository, with a change log the MCP write path cannot switch off and a write path that treats agent-supplied strings as hostile."
root: ../..
page_kind: system
source_name: "okf-memory/okf-agent-memory"
source_url: https://github.com/okf-memory/okf-agent-memory
archive_name: "okf-memory--okf-agent-memory"
revision: 2649a28213d487fbc764c5d6670ff6216d5f7bfe
revision_url: https://github.com/okf-memory/okf-agent-memory/commit/2649a28213d487fbc764c5d6670ff6216d5f7bfe
analyzed_at: 2026-09-16
capabilities: "audit_log"
capability_evidence:
  audit_log: "a dated change log in the bundle, written by the library on every concept write, which the agent-facing path cannot turn off | pkg/okf/mutate.go:51-52, :355-365, :433, cmd/okf/mcp.go:615, :646, cmd/okf/main.go:715, :798 | the mark is not the git history the README leads with, which this atlas does not count, but `knowledge/log.md`: `SaveConcept` appends a dated `Creation` or `Update` entry naming the concept path and title, and `RelateConcepts` appends its own `Update` when it links two concepts. The record lives in the bundle beside the memory it describes, so it travels with a clone and is readable without the tool. What makes it more than a convention is where the switch sits: the CLI exposes `--no-log` and defaults it on, while both MCP write handlers pass `autoLog` as a hardcoded `true`, so an agent writing through the protocol cannot suppress its own entry. `AppendLogEntry` is also one of the paths the security suite covers, sanitising newlines so a description cannot forge a second entry | pkg/okf/mutate_security_test.go:266 `TestAppendLogEntrySanitizesNewlines`, with :353 covering the same injection on the relation path"
stack_storage: "files"
stack_retrieval: "lexical"
stack_source: "reviewed"
matrix:
  memory_unit: "A concept: one markdown file with YAML frontmatter carrying type, title, description, tags, a `generated` provenance stamp, `verified` entries, `status`, `governance`, `code_refs`, `stale_after`, sources and an optional attestation"
  storage: "Plain markdown under `knowledge/` in the repository, parsed by a zero-dependency Go library; no database and no vector store"
  retrieval: "In-memory BM25 over the bundle, plus a code-path leg matching `code_refs`, ranked with a governance multiplier"
  write: "`okf create` and `okf update` from the CLI, or `okf_create` and `okf_update` over MCP; both round-trip the frontmatter through the parser rather than editing text"
  update_delete: "An update rewrites the file and appends a log entry; there is no delete in the library, so erasure is a file removal outside the tool"
  scoping: "The bundle directory is the boundary; there is no scope key on a concept and no scope predicate on a search"
  integration: "A single Go binary serving a CLI and an MCP server with six tools, plus `okf agents link`, which symlinks `CLAUDE.md` and other tool instruction files at a single source of truth"
  background: "None; validation, linting and search are invoked, and CI runs the validator over the repository's own bundle"
  trust: "`generated` records which agent wrote a concept and when, `verified` and `attestation` record checking, and a validator gates the bundle's structure in CI"
  strengths: "The write path is built as though the thing writing it is not trustworthy, which for agent-written memory is the correct assumption. `mutate_security_test.go` covers path traversal on save and on parent-index update, reserved root and subdirectory filenames, symlinks pointing at reserved or non-markdown targets, external symlinks on load, YAML quoting, and newline sanitisation on both log entries and relations — and `TestSaveConceptRejectsFrontmatterInjection` is the one that matters most here, because a concept body reaches other agents as instructions: `okf agents link` symlinks `CLAUDE.md` and its equivalents at the bundle, so a frontmatter key smuggled through a description would be read as configuration by every tool in the repository. The second thing worth taking is the log: a dated, in-band change record that the MCP path cannot disable, which is a stronger claim than the `git log` the README offers, since a commit records what a human chose to stage and this records what the tool actually wrote"
  risks: "Three frontmatter fields read like epistemic state and only one of them reaches retrieval. `status` is parsed, validated against `draft|stable|deprecated`, and serialized back, and no read path consults it: `okf search` ranks a deprecated concept exactly as it ranks a stable one. `stale_after` is the same shape — the validator emits a warning once the date has passed, and search is unaffected, so a concept the tool itself calls stale is still handed to an agent at full weight. `governance` is the one search does read, and it multiplies the score, so the effect of the trust vocabulary on retrieval is to promote rather than to withhold. The `hold` level compounds this: `EffectiveGovernance` documents it as \"execution freeze / manual signoff required\", but the freeze exists only as a line of bootstrap prompt text — `IF governance == \"hold\" => STOP(\"Subsystem frozen by governance. Request explicit human confirmation.\")` — so the code ranks the concept higher and asks the model to stop, which is an instruction rather than a gate. Smaller: `okf update --help` offers `'active'` as an example status, and the validator rejects it, while `stable`, the value that is valid, goes unmentioned"
---

## 1. Executive Summary

OKF Agent Memory is "[a] Domain-Neutral, Git-Native Persistent Project Memory
for AI Agents based on the Open Knowledge Format (OKF) v0.2" — MIT, Go with no
third-party dependencies, 10,217 lines across 27 files, and a memory that is
markdown files under `knowledge/` in the repository being worked on.

The positioning is a middle ground, and it is stated plainly: the format "bridges
the gap between unstructured ad-hoc markdown files (`CLAUDE.md`, `AGENTS.md`)
and complex, black-box vector databases." One binary provides a CLI and an MCP
server with six tools, search is in-memory BM25 over the parsed bundle, and a
validator checks the bundle's structure in CI.

**The frontmatter is where the interest is, and where the gap is.** A concept
carries `status` (`draft | stable | deprecated`), `stale_after` (a date), and
`governance` (`context | constraint | hold`). Two of the three are parsed,
validated, serialized back, and consulted by nothing on the read path.
`okf search` ranks a deprecated concept exactly as it ranks a stable one, and a
concept whose `stale_after` has passed — which `okf validate` will warn about —
is retrieved at full weight.

The third is read, and it moves the score the other way:

```go
func governanceRank(gov string) int {
	switch strings.ToLower(gov) {
	case GovernanceHold:
		return 3
```

`score := float64(governanceRank(gov) * 10)`. So the only trust field that
reaches retrieval is one that **promotes**, and the two that could withhold do
not. `hold` is documented as "execution freeze / manual signoff required", and
the freeze is a sentence in a bootstrap prompt — `IF governance == "hold" =>
STOP(...)` — addressed to the model rather than enforced by the tool. The code
ranks the frozen subsystem first and asks the agent to stop when it gets there.

**What the project does earn is a mutation record that is not git.** The README
leads with `git diff` and `git log`, which is not an audit of what the tool
wrote — a commit records what somebody chose to stage. `knowledge/log.md` is the
real one: `SaveConcept` appends a dated `Creation` or `Update` entry naming the
concept, the CLI can suppress it with `--no-log`, and both MCP handlers pass
`autoLog` as a hardcoded `true`. The agent-facing path cannot write without
leaving the entry.

## 2. Mental Model

A **concept** is one markdown file with frontmatter, in your repository.

A **status** is a value the validator checks and the search ignores.

A **governance level** is a ranking multiplier that reads like a gate.

A **log entry** is written by the tool, not by the committer.

```mermaid
%% caption: three frontmatter fields carry epistemic meaning, only governance reaches the ranker and it multiplies the score, while status and stale_after are validated and never consulted on the read path
flowchart TB
    W["okf create / okf update (CLI)<br/>okf_create / okf_update (MCP)"] --> SAVE["SaveConcept(bundleDir, c, isNew,<br/>autoLog, autoIndex, actor)"]
    SAVE --> FILE[("knowledge/**.md —<br/>YAML frontmatter + markdown body")]
    SAVE --> LOG[("knowledge/log.md — dated<br/>Creation / Update entries")]
    W -.->|"CLI: --no-log can suppress it<br/>MCP: autoLog is hardcoded true"| LOG
    SEC["mutate_security_test.go: traversal,<br/>reserved names, external symlinks,<br/>YAML quoting, newline sanitisation,<br/>frontmatter injection"] --> SAVE
    FILE --> P["parser: status · stale_after ·<br/>governance · code_refs · generated ·<br/>verified · attestation"]
    P --> V{"okf validate"}
    V -->|"status outside the three valid values"| GATE["a gate finding"]
    V -->|"stale_after <= today"| WARN["a warning — and nothing else happens"]
    P --> S["okf search: in-memory BM25<br/>+ a code_refs leg"]
    STATUS["status"] -.->|"parsed, validated, serialized back —<br/>NO read path consults it"| NOTHING["a deprecated concept ranks<br/>exactly like a stable one"]
    STALE["stale_after"] -.->|"a validator warning only"| NOTHING
    GOV["governance"] --> RANK["score = governanceRank(gov) * 10<br/>hold=3 · constraint=2 · context=1"]
    RANK --> S
    RANK -.->|"the one trust field that reaches retrieval<br/>PROMOTES rather than withholds"| UP["the frozen subsystem ranks first"]
    HOLD["governance: hold —<br/>'execution freeze / manual signoff required'"] -.->|"enforced only by bootstrap prompt text:<br/>IF governance == 'hold' => STOP(...)<br/>an instruction to the model, not a gate"| NOHR["no review mark"]
    S --> AGENT["what the agent is handed"]
    LINK["okf agents link — symlinks CLAUDE.md,<br/>AGENTS.md and friends at one source"] -.->|"which is why frontmatter injection<br/>on the write path is the real threat"| SEC
```

## 3. Architecture

| Area | Role |
| --- | --- |
| `pkg/okf/types.go` | The concept, its frontmatter, and `EffectiveGovernance` |
| `pkg/okf/parser.go` | A hand-written frontmatter parser and serializer, round-tripping unknown keys |
| `pkg/okf/search.go` | BM25, the `code_refs` leg, and `governanceRank` |
| `pkg/okf/validator.go` | Status, staleness, graph and structure checks |
| `pkg/okf/mutate.go` | Writes, the parent index, and the change log |
| `pkg/okf/aag/` | A linter for RFC 2119 modal prefixes in agent instructions |
| `cmd/okf/` | One binary: CLI, MCP server, and the tool symlink manager |

## 4. Essential Implementation Paths

`pkg/okf/types.go:29-32` — `status`, `governance` and `stale_after` declared
side by side, which is what makes the divergence in how they are used worth
checking.

`pkg/okf/search.go:248-257` and `:315` — the only trust field that reaches the
ranker, and the direction it moves the score.

`pkg/okf/validator.go:220-228` — where `status` and `stale_after` are checked,
and the fact that a stale concept produces a warning rather than a filter.

`pkg/okf/bootstrap.go:32` — the `hold` freeze, as prompt text.

`pkg/okf/mutate.go:355-365` — the log entry, and the flag that can turn it off.

`pkg/okf/mutate_security_test.go:191` — frontmatter injection, refused.

## 5. Memory Data Model

One markdown file per concept, addressed by its bundle-relative path without the
extension. Frontmatter carries a required `type`, a title and description, tags,
a `generated` stamp recording which agent produced it and when, a list of
`verified` entries, `status`, `governance`, `code_refs` binding the concept to
source paths or globs, `stale_after`, `sources`, and an optional attestation.
Unknown keys are preserved through the round trip rather than dropped, which is
the right call for a format meant to outlive one tool.

## 6. Retrieval Mechanics

In-memory BM25 over titles, descriptions, tags and bodies, with a second leg
matching a file path against `code_refs` so a concept can be found by the code
it constrains rather than by its words. Results carry the governance level, and
the governance multiplier dominates the ranking at ten points per rank against
BM25's single-digit scores.

## 7. Write Mechanics

Writes go through the parser and serializer rather than through text editing, so
a concept cannot acquire malformed frontmatter by way of an edit. `SaveConcept`
optionally updates the parent index and appends the log entry. There is no
delete in the library: removing a concept means removing a file, which is
consistent with the git-native premise and means erasure leaves no entry in the
log that records every creation.

## 8. Agent Integration

One binary, six MCP tools — `okf_create`, `okf_update`, `okf_relate`,
`okf_search`, `okf_show`, `okf_validate` — and `okf agents link`, which
symlinks `CLAUDE.md`, `.github/copilot-instructions.md` and the other per-tool
instruction files at a single source of truth so they cannot drift apart.

## 9. Reliability, Safety, and Trust

The security posture is the strong part and is unusually complete for a project
this size: traversal refused on save and on index update, reserved filenames
refused at root and in subdirectories, symlinks refused when they point outside
the bundle or at non-markdown, YAML values quoted, newlines sanitised in log
entries and relations, and frontmatter injection refused. The weak part is that
none of the epistemic fields withhold anything at read time.

## 10. Tests, Evals, and Benchmarks

A Go test suite covering the parser, the validator, governance, scenarios, the
security surface and the AAG linter, plus a dogfood test that runs the library
against this repository's own `knowledge/` bundle and a search benchmark. There
are no committed cases asserting that particular material must not be retrieved,
which follows from there being no read path that withholds.

## 11. For Your Own Build

If you add a status field, write down which read path filters on it before you
add the third value. A vocabulary that only the validator consults is
documentation with a schema.

Check the direction of your trust signal. A multiplier that promotes constrained
material is a reasonable design, but it is not the same mechanism as one that
withholds superseded material, and a frontmatter block can make them look alike.

Take the injection tests. Memory written by an agent and symlinked at
`CLAUDE.md` is an instruction channel, and treating the writer as hostile is the
only safe posture.

## 12. Open Questions

Whether `deprecated` is meant to filter. The CLI's own example — `okf update
decisions/adr-001 --status deprecated --desc "Superseded by adr-008."` — reads
like a supersession that should take the old decision out of an agent's way, and
nothing downstream acts on it.

Whether `hold` should be enforceable by the tool at all. The bootstrap text is
the only enforcement, and a model that does not read it, or reads it and
continues, is unconstrained by a field named for a freeze.

## Appendix: File Index

| Path | What to read it for |
| --- | --- |
| `pkg/okf/search.go:248-257` | The only trust field that reaches the ranker, and its direction |
| `pkg/okf/validator.go:220-228` | Two fields checked at validation and nowhere else |
| `pkg/okf/bootstrap.go:32` | A freeze that exists as prompt text |
| `pkg/okf/mutate.go:355-365` | A change log the MCP path cannot switch off |
| `pkg/okf/mutate_security_test.go:191`, `:266` | Injection into frontmatter, and into the log |

## History

**2026-09-16** — [`2649a28213d487fbc764c5d6670ff6216d5f7bfe`](https://github.com/okf-memory/okf-agent-memory/commit/2649a28213d487fbc764c5d6670ff6216d5f7bfe) — first reading, at a commit dated 16 September 2026. Screened before opening, from a shallow clone: eight files scanned, two auto-run surfaces, two build-time execution points, no unpinned surfaces and one dependency file inside the seven-day cooldown. `AGENTS.md` and `CLAUDE.md` are addressed to a reading agent and were recorded as data. Nothing was installed, built or run.

---
title: "TigrimOSR"
eyebrow: "Proposed skills, staged on disk"
description: "A Rust agent platform whose synthesizer proposes skills beside the live ones and waits for approval, forgets every rejection when the process exits — and ships a new folder-local CLI in which the synthesizer never runs."
root: ../..
page_kind: system
source_name: "Sompote/TigrimOSR"
source_url: https://github.com/Sompote/TigrimOSR
revision: 0813f2eb9f28a07e9adb6231f3de4f09803b66b4
revision_url: https://github.com/Sompote/TigrimOSR/commit/0813f2eb9f28a07e9adb6231f3de4f09803b66b4
analyzed_at: 2026-07-31
capabilities: "trust_state, scope_enforced, human_review"
matrix:
  memory_unit: "A skill — a SKILL.md with a registry row carrying review status, rationale and the sessions it came from — plus one memory.md per project"
  storage: "JSON files on disk (skills.json, projects.json, chat history) and SKILL.md directories, resolved through a project-first overlay in CLI mode"
  retrieval: "No search; the project's assigned skills and its memory.md are assembled into the system prompt"
  write: "A synthesizer reads finished sessions, user feedback and subagent traces, then proposes create or update"
  update_delete: "Proposals stage as SKILL.md.proposed and become live by rename on approval; rejection deletes the proposal and records nothing"
  scoping: "Project id selects the memory.md and filters the installed-skills block; the CLI scopes instead by launch directory, with skills, persona, settings and history in a local .tigrimos"
  integration: "Native Rust desktop app, embedded web UI, a folder-local `tigrim` CLI, MCP servers, plugins, Telegram and LINE bots"
  background: "A scheduler runs the skill synthesizer in the desktop and headless binaries only; compaction hooks track file reads and invoked skills"
  trust: "review_status pending or approved, persisted, with pending coupled to enabled=false"
  strengths: "A staged proposal a person can diff before it takes effect, carrying its rationale and source sessions"
  risks: "Proposal state is in-memory only, so a rejected skill can be re-proposed after a restart, and the CLI never starts the synthesizer that produces skills in the first place"
---

## 1. Executive Summary

TigrimOSR is a single-binary Rust agent platform — desktop app, embedded web
server, swarm orchestration, MCP, plugins, Telegram and LINE bots — of which the
memory-relevant part is a **skill synthesizer**: a background pass that reads
finished chat sessions, the user's thumbs-up/down feedback and subagent traces,
and proposes new or updated skills.

It belongs in this atlas for one mechanism. When the synthesizer wants to change
an existing skill, it does not change it. It writes `SKILL.md.proposed` beside the
live `SKILL.md`, sets the registry row to `review_status: "pending"` with the
model's `rationale` and a `based_on` list of the sessions it drew from, and stops.
The live skill is untouched and still in use. A person opens the proposal, sees a
real before/after diff (`get_proposed_diff` returns both files), and approves —
at which point promotion is a `tokio::fs::rename`. That is the
[promotion between tiers](../../patterns/promotion-between-tiers/) pattern with an
atomic commit and a human gate, and it is better staged than most of this atlas.

One rule inside it is worth pulling out on its own: `require_approval` defaults to
true, and the code forces it true regardless of settings when the target skill's
`source == "custom"`, with the comment *"User-authored (custom) skills are never
overwritten silently"*. Automation may rewrite what automation wrote; it may never
rewrite what a person wrote without asking. Nothing else in this atlas escalates
its approval requirement based on who authored the memory.

**The weakness is exactly symmetric to the strength, and it is the atlas's
recurring finding in an unusually clean form.** Approval is durable — a file
rename, a registry row, a `SKILL.md` on disk. *Rejection is not.* The proposal
list lives in a process-lifetime `OnceLock<Mutex<SynthesizerStatus>>` with no load
or save; rejecting a create deletes the skill folder and drops the registry row;
rejecting an update deletes the `.proposed` file and resets the status. Restart the
binary and there is no record that anything was ever proposed or refused, and
nothing in the synthesis path consults past rejections. The same sessions produce
the same proposal again.

**There are two ways to run TigrimOSR and the mechanism above is in only one of
them.** `src/bin/tigrim.rs` is a Claude-Code-style CLI that treats the directory
it launches in as the workspace: `.tigrimos/` holds that folder's skills,
persona, settings and chat history, and `src/server/data.rs` carries an overlay —
`skills_root()`, `resolve_config_file`, `overlay_dirs`, and a
`PROJECT_LOCAL_FILES` list — that routes reads project-first. It is a cleaner
scope boundary than the project-id filter, and it is four days old at this
commit.

The synthesizer does not run there. `skill_synthesizer::start_cron` is called
twice, both times in `src/main.rs`, and `src/bin/tigrim.rs` calls neither. A CLI
folder gets the thirteen bundled skills seeded at first run and nothing after
that: no proposals, no `SKILL.md.proposed`, no approve or reject, no
`review_status` transitions. The skill library in a `.tigrimos` folder is a
fixture. So the new mode isolates memory well and generates none, and the mode
that generates it keeps its decisions in a process that forgets them.

## 2. Mental Model

Two kinds of memory, with very different levels of care.

| Kind | What it is |
| --- | --- |
| `project.memory` | One `memory.md` per project — a blob, injected whole |
| skill | `SKILL.md` plus a registry row: `enabled`, `review_status`, `auto_meta` — and `auto_meta` carries `kind`, `based_on`, `generated_at`, `model`, `rationale` |
| chat sessions | Persisted history, and the synthesizer's raw material |

The skill lifecycle is the interesting one. It belongs to the desktop and
headless binaries; in the CLI a folder's skills are seeded once and no state in
this diagram is ever entered.

```mermaid
flowchart TB
    SRC["finished sessions<br/>+ user feedback<br/>+ subagent traces"]
    SRC -->|"scheduler runs run_synthesis"| PR["Proposal<br/>kind: create or update<br/>name, content, rationale, based_on"]
    PR --> GATE{"require_approval?"}
    GATE -->|"false"| THRU["write straight through<br/>review_status = approved"]
    GATE -->|"true — the default,<br/>and forced when source is custom"| STAGE
    STAGE["create: SKILL.md written,<br/>enabled = false, review_status = pending<br/>update: SKILL.md.proposed beside the live file"]
    STAGE --> AP["approve"]
    STAGE --> RJ["reject"]
    AP --> LIVE["rename to SKILL.md<br/>enabled = true"]
    RJ --> DEL["delete .proposed;<br/>a create is removed outright<br/>and its row dropped"]
    DEL --> NOTHING["nothing recorded,<br/>nothing remembered"]

    style THRU fill:#f4e2bd,stroke:#b8860b
    style NOTHING fill:#f4e2bd,stroke:#b8860b
```

Two highlighted boxes, two different gaps. Turning off `require_approval` writes a
model-authored skill straight to `approved`, and a rejection leaves **no trace at
all** — so the same proposal can be regenerated from the same sessions on the next
synthesis run, and nothing knows it was already refused.

`review_status` is a persisted discrete state, and `pending` is coupled to
`enabled: false`, so a pending skill exists on disk and is withheld from every
run. That earns the trust-state mark under this atlas's definition — a discrete
status field, not a score, with a state that withholds the memory from use — and
two caveats belong with it. It is *approval* status rather than truth: nothing
here can say a skill is wrong, only that nobody has said yes to it. And `rejected`
is set on the in-memory proposal and never persists on a skill; the durable
vocabulary is `pending` and `approved`.

`project.memory` gets none of this. It is a string, written whole by
`PUT /:id/memory`, mirrored to `memory.md` in the working folder and to
`projects.json`, and prepended to the system prompt as `Project memory/context:`.
No entries, no identity below the project, no review.

## 3. Architecture

```mermaid
flowchart TD
    UI["native Rust UI /<br/>embedded web UI /<br/>Telegram, LINE"] --> SRV["axum server<br/>src/server/routes"]
    SRV --> AL["agent_loop<br/>+ toolbox, mcp, graph"]
    SRV --> D[("JSON on disk<br/>projects.json, skills.json,<br/>chat history, settings")]
    SCH["scheduler"] --> SY["skill_synthesizer"]
    SY --> D
    SY --> SK[("skills/&lt;slug&gt;/<br/>SKILL.md<br/>SKILL.md.proposed")]
    AL --> SK
    AL --> CMP["compact<br/>track_file_read, track_invoked_skill"]
```

- **One crate, now two binaries**, roughly 67,700 lines across 77 source files.
  A `refactor:` commit split the crate into a lib plus `tigrimos` (desktop and
  headless) and `tigrim` (CLI). `server/` holds the axum routes and services,
  `ui/` the native desktop views, plus `vm/`, `cli/`, and `security/` with a
  sandbox and file-access control.
- **Persistence is JSON files**, not a database — `read_json` / `write` through
  `src/server/data.rs`, with a remote-backend mode that proxies the same calls to
  another instance over HTTP with a bearer token.
- **No embeddings and no vector store.** There is no memory search anywhere; recall
  is prompt assembly from the project's assigned skills and its `memory.md`.

### The project overlay

The CLI's storage model is worth its own description, because it is a different
scoping mechanism from the one the rest of this report describes rather than a
variant of it. `init_project` creates `<cwd>/.tigrimos` and calls
`data::set_project_dir`; from then on three resolvers in `src/server/data.rs`
decide where a read lands:

| Resolver | Behaviour when a project dir is set |
| --- | --- |
| `resolve_data_file` | Routes the four names in `PROJECT_LOCAL_FILES` — `chat_history.json`, `cli_state.json`, `settings.json`, `skills.json` — to the project dir. Everything else stays global. |
| `skills_root` | Returns `<proj>/skills` with **no global fallback**, so a folder sees only its own skill packages. |
| `resolve_config_file` / `overlay_dirs` | Project-first with global fallback, for YAML profiles under `agents/`, `agent_loops/`, `graph/`. |

The asymmetry is deliberate and the doc comments say so: config falls back,
skills do not — *"desktop-only skills no longer leak into CLI system prompts"*.
Persona follows the same rule in `src/server/routes/chat.rs`, where the
`SOUL.md` / `IDENTITY.md` read now resolves `project_dir().unwrap_or(data_dir)`
so a folder answers with its own persona or with none.

`GLOBAL_DATA_DIR_OVERRIDE` is the detail that shows the author had already been
bitten: `data_dir()` used to pick `./data` when that directory existed, which in
a CLI launched inside an arbitrary repository would have hijacked any project
that happens to contain a `data/` folder. The CLI pins the global dir explicitly
to disable that heuristic.

One thing the overlay does not cover is `projects.json`, and the CLI does not
use it — `src/cli/run.rs:162` sets `project_id: None`. A CLI folder therefore
has no project, and so no `memory.md`, no custom instructions and no
project-assigned skill filter. The durable memory of a `tigrim` folder is its
chat history, its persona files, and a skill library nothing writes to.

### Deployment and ergonomics

The lightest deployment of anything in this atlas that does this much: download a
DMG or MSI, or run one binary. No database, no Python, no Node. The README's
measured figures at this commit are about 4 MB resident for the CLI, 7 MB
headless, and 190 MB for the desktop app with its embedded browser.

An LLM key is needed to *synthesize* skills but not to store anything — the memory
paths are plain file writes, so the store works with the model offline. Providers
are pluggable down to Claude Code, Gemini CLI and Codex with no API key.

The store is as repairable as it gets: `skills.json`, `projects.json` and a tree
of `SKILL.md` files. A wrong skill is fixed in an editor. This is the same
property the file-canonical family has, arrived at by a different route.

## 4. Essential Implementation Paths

**Synthesis input** — `src/server/services/skill_synthesizer.rs`.
`SessionSummary` gathers `user_queries`, `final_assistant`, a `feedback` list of
`FeedbackEntry {role, rating, comment, excerpt}`, and a `subagent_workflow` of
`SubagentTrace {label, task, tools_used, skills_loaded, completed, error}`. Note
`completed` and `error`: failed subagent runs are input, not filtered out.

**Proposal construction** — `Proposal {kind, name, description, content,
based_on, rationale}`, surfaced through `add_proposal_to_status` as a
`SkillProposal` with `review_status: "pending"` and an `existing_content` field so
the reviewer sees what would be replaced.

**Create path** — `write_new_auto_skill` (line 977). Writes `SKILL.md` live, then
registers the row with `enabled: !require_approval` and
`review_status: pending | approved`. With the default, the file exists and the
skill is disabled.

**Update path** — around line 1020. Looks up an existing `auto` or `custom` skill;
if the target is missing it falls back to create. `require_approval` is read from
settings, then **forced true when `source == "custom"`**. Approved-through writes
the live file; otherwise `write_skill_file(&slug, &p.content, true)` writes the
`.proposed` sibling and the row goes `pending` with
`auto_meta.proposed_path = Some("SKILL.md.proposed")`.

**Approve** — `approve_proposal` (line 1100). Sets the in-memory status, then
`tokio::fs::rename(SKILL.md.proposed → SKILL.md)` when the proposal exists, or
writes the content directly, then flips `enabled = true` and clears
`proposed_path`.

**Reject** — `reject_proposal` (line 1146). Deletes the `.proposed` file; for an
update, resets the skill's `review_status` to `"approved"`; for a create,
`remove_dir_all(skill_dir)` and `skills.retain(|s| s.name != proposal_name)`.

**Review affordance** — `get_proposed_diff` returns `(current, proposed)` for a
skill, reading both files, with an empty `current` for creates.

**Project memory** — `src/server/routes/projects.rs`: `put_memory` writes
`memory.md` into the working folder and mirrors it into `projects.json`;
`load_project_run_context` (line 113) assembles name, description, working folder,
`memory`, custom instructions and the project's `skills` list into the system
block. `POST /:id/memory/generate` is a stub.

**Compaction** — `src/server/services/compact.rs`: `track_file_read`,
`track_invoked_skill`, `set_active_plan`, `on_pre_compact` / `on_post_compact`
hooks and `validate_message_structure`.

**Project overlay** — `src/server/data.rs`: `set_project_dir`, `skills_root`,
`resolve_data_file`, `resolve_config_file`, `overlay_dirs`, `data_file_path`,
`GLOBAL_DATA_DIR_OVERRIDE`. `src/cli/project.rs` holds `init_project`,
`seed_examples`, `seed_settings_file` and the `CliState` struct;
`src/bin/tigrim.rs` calls them at startup and calls `install_bundled_skills`
against the project dir.

**History filter** — `src/server/routes/chat.rs`, in `start_agent_run`: the
message list sent to the model drops assistant turns whose content begins with
`"Error: "` or `"⚠️"`.

## 5. Memory Data Model

Everything is a serde struct in a JSON file. The skill row is the one with real
metadata:

```rust
struct Skill { id, name, description, source, script, enabled,
               installed_at, review_status: Option<String>,
               auto_meta: Option<SkillAutoMeta> }
struct SkillAutoMeta { kind, based_on: Vec<String>, generated_at,
                       model, proposed_path: Option<String>,
                       rationale: Option<String> }
```

`based_on`, `model`, `generated_at` and `rationale` together are better provenance
than most of this atlas manages: a reviewer can see which sessions produced the
proposal, which model wrote it, when, and why. `source` distinguishes `auto`,
`custom` and installed skills, and it is load-bearing rather than decorative —
it is what triggers the forced approval in section 4.

Scoping is the project. `load_project_run_context` looks up one project by id and
assembles only that project's `memory` and only the skills named in its `skills`
list; nothing else reaches the prompt. That is a scope key applied on the read
path, which is what the rubric asks for, and it is enough for the mark. It is also
the atlas's thinnest instance of it: the boundary is a filter during prompt
assembly rather than a property of storage, and the skill files themselves live in
one global directory that any project may name.

What is absent: no per-entry identity inside `memory.md`, no validity interval, no
supersession pointer, no confidence, and — the finding in section 1 — no durable
record of a rejection.

## 6. Retrieval Mechanics

There is no retrieval. No embeddings, no index, no search over memory, no ranking.
What reaches the model is whatever `load_project_run_context` assembles: the
project's `memory.md` in full, plus the installed-skills block filtered to that
project's assignment.

For a project-scoped desktop tool that is a defensible choice and it has the
property [gate the expensive path](../../patterns/gate-the-expensive-path/) wants
— nothing irrelevant is retrieved because nothing is retrieved. The cost is the
one that shape always carries: `memory.md` is injected whole on every turn, so its
size is a fixed tax and there is no mechanism that would notice it growing past
usefulness. `POST /:id/memory/generate` — the endpoint that would presumably
summarize or compact it — is a stub at this commit.

In CLI mode there is no `memory.md` to inject at all, since there is no project.
What the read path assembles there is the folder's `SOUL.md` and `IDENTITY.md`,
the enabled-skills block built from `.tigrimos/skills.json`, and the folder's own
chat history.

That history acquired a filter in this round, and it is the one genuinely new
selection rule in the codebase. `start_agent_run` now drops assistant turns whose
content starts with `"Error: "` or `"⚠️"` before building the message list,
with a comment naming the failure it fixes: those strings are UI placeholders
rather than model output, and models were few-shot imitating them — *a dead
provider's quota message kept "answering" in a session even after switching
providers.* This is the transcript-as-memory hazard in its sharpest form. Nothing
wrote a memory; the interface wrote a turn into the history, and the history is
the prompt, so the artifact became an example.

The fix is right and the implementation is a prefix match on two display strings.
A legitimate answer beginning "Error: " — an entirely ordinary way for a coding
agent to open an explanation of a compiler message — is dropped from history
silently, and the placeholders stay in the persisted session and stay on screen,
so what the user sees and what the model sees have quietly diverged. A marker on
the message struct would have cost one field.

## 7. Write Mechanics

Two write paths with opposite characters.

`memory.md` is a **blind overwrite**. `put_memory` takes the request body, writes
the file, mirrors the string into `projects.json`, and stamps `updated_at`. There
is no merge, no diff, no previous version, and no guard on what was lost. It is
the human's file, edited by the human, so the risk is bounded — but the same
endpoint is reachable by anything holding the API token.

Skills are the **staged** path, described in section 4, and the staging is the
good part. Three properties are worth naming because they are separable and each
is copyable on its own:

1. The proposal is a **file on disk**, not a row in a queue. It survives a crash,
   it can be read with `cat`, and promotion is an atomic rename.
2. The live memory is **untouched** while the proposal waits. A pending update
   costs nothing and risks nothing.
3. The approval requirement **escalates on provenance**. `source == "custom"`
   forces review even when the operator has turned auto-update on globally.

And then the fourth property, which is absent and which the other three make
conspicuous: the decision is not remembered. `synth_status()` is a
`OnceLock<Arc<Mutex<SynthesizerStatus>>>` initialized to `default()`; nothing
reads it from disk at startup and nothing writes it. `last_run_at` lives in that
same struct, so after a restart the synthesizer does not know when it last ran
either. A user who rejects a proposed skill on Monday can be offered it again on
Tuesday, and the only thing standing between them is that nobody restarted the
binary.

### Operational cost

- **Synchronous?** No. Memory writes are file writes; synthesis is scheduled.
- **Lag?** Skills appear at the next synthesis run *and* after a human approves,
  so the write-to-recall path includes a person. That is slow by design and is the
  right trade for content that becomes instructions.
- **Whole-store passes?** Synthesis reads finished sessions and reasons across
  them; `consumed_session_ids` dedupes within a run, not across restarts.
- **Read path?** `memory.md` in full plus the filtered skills block, every turn,
  unbounded and at the front of the prompt.
- **In CLI mode?** No synthesis at all. `start_cron` is called only from
  `src/main.rs`, so a `tigrim` folder's skill set is whatever `init_project`
  seeded and never changes on its own.

## 8. Agent Integration

The widest surface of any single binary here: MCP servers (client side), a plugin
system taking zip bundles of skills/MCP/agents/connectors, ClawHub skills, six
swarm modes with a shared blackboard, a graph mode with a judge panel, custom
tools defined in YAML, Telegram and LINE bots, a terminal CLI with a REPL, and a
remote mode where a desktop app drives another instance over HTTP — including
forwarding proposal approve/reject actions to the remote synthesizer.

The CLI is the newest surface and the one that changes the memory story. It runs
the same engine in-process — `src/cli/run.rs` builds an `AgentRunRequest` and
calls `chat::start_agent_run` directly, with no server — which is why it inherits
the prompt assembly and the history filter while inheriting none of the scheduled
background work.

The model has no memory tools. It cannot save, forget or correct; it produces
sessions, and a separate pass decides what those sessions taught. Combined with
the human gate, that is a deliberate and coherent allocation: the model does the
work, the synthesizer proposes the lesson, the person decides.

The judge panel is adjacent to memory rather than part of it — an
evaluator-optimizer gate on *answers*, not on what is remembered — but it is the
same instinct applied one layer up, and a reader interested in verified-write
gates will find both in one codebase.

## 9. Reliability, Safety, and Trust

Provenance on skills is good: `based_on`, `model`, `generated_at`, `rationale`.
Provenance on `memory.md` is nil.

The security module is more developed than the memory model — `security/sandbox.rs`
and `security/file_access.rs`, per-tool approval, timeouts, output caps, and a
working folder resolved as a sandbox root. For a desktop agent with shell and
browser access that is the right emphasis.

Prompt injection has a specific route into durable memory here, and the human gate
is what closes it: injected text in a session can shape a proposal, but with
`require_approval` on it cannot become an enabled skill without someone clicking
approve. Turning that setting off removes the only barrier between a poisoned
session and a live instruction file — which is worth stating plainly, because the
setting exists and defaults the safe way.

The concurrency model for JSON persistence is read-modify-write on whole files
(`get_skills` → mutate → `save_skills`), so two writers can lose an update. With a
single desktop user that is theoretical; with the remote mode and bots driving the
same instance it is less so.

Data-loss risk is concentrated in the reject path — `remove_dir_all` on a skill
folder — and in the in-memory proposal list, which discards pending work on
restart as well as rejections.

The overlay came with the right secret hygiene, which is worth naming because
per-folder config is where keys usually leak. `init_project` writes
`.tigrimos/.gitignore` covering `settings.json`, `.env`, `chat_history.json`,
`cli_state.json` and `repl_history`, and rewrites it on every run so older
folders are upgraded in place rather than left with the earlier, narrower list.
The seeded `settings.json` blanks its credential fields on purpose;
`apply_env_overrides` reads `TIGRIMOS_API_KEY`, `TIGRIMOS_MODEL` and
`TIGRIMOS_API_URL` last, on top of the file, and `save_settings` never writes
them back. A folder that is a git repository — which is the normal case for this
mode — does not acquire a committable key by being initialized.

## 10. Tests, Evals, and Benchmarks

62 inline Rust tests (`#[test]` / `#[tokio::test]`) across the source tree, which
is real coverage for a project of this age but is concentrated on the agent loop,
tool config resolution and message validation rather than on memory. No test in
the tree exercises the propose/approve/reject cycle, and none asserts anything
about `memory.md`.

There is no eval harness, no benchmark, and no committed results, which is
consistent — this is an agent platform, not a memory system making retrieval
claims, and inventing a number would be worse than the absence.

The count is unchanged across this round's fifteen commits, and none of the new
code carries a test: `src/cli/`, `src/bin/tigrim.rs` and the overlay resolvers in
`src/server/data.rs` have no `#[test]` between them. Path resolution with a
fallback rule that differs per file class is exactly the kind of logic a table
test covers in ten lines.

The test I would want is short and would have caught the finding in section 1:
propose a skill, reject it, restart the synthesizer state, run synthesis over the
same sessions, and assert the proposal does not return. As written it does.

## 11. For Your Own Build

### Steal

- **Stage the proposal as a file beside the live one.** `SKILL.md.proposed` next
  to `SKILL.md`, promoted by rename, is the cheapest correct implementation of a
  staged write: crash-safe, greppable, atomic on commit, and diffable by a person
  with no tooling.
- **Escalate the approval requirement on provenance.** "Automation may overwrite
  what automation wrote, never what a person wrote" is one comparison in one `if`,
  and it removes the worst outcome of an auto-update feature.
- **Carry the rationale and the sources on the proposal.** `based_on`,
  `rationale`, `model` and `generated_at` turn a review from a judgement about
  text into a judgement about an argument.
- **Feed failures into synthesis.** `SubagentTrace` keeps `completed` and `error`,
  so what went wrong is available to learn from rather than filtered out.
- **Name the files that must be per-folder, then route reads through one
  resolver.** `PROJECT_LOCAL_FILES` is a four-element constant and
  `resolve_data_file` is nine lines, and together they converted a global store
  into a per-directory one without touching a single caller. The variant worth
  copying is the asymmetry: config falls back to global, the skill library does
  not, because a stale config is an inconvenience and a leaked instruction file
  is a behaviour change you did not ask for.
- **Keep error placeholders out of the model's view of history.** A UI artifact
  written into a transcript becomes a few-shot example on the next turn. Filter
  it — and prefer a flag on the message over a prefix match on its text.

### Avoid

- **Do not make approval durable and rejection ephemeral.** This is the
  transferable lesson and it generalizes past this codebase: if a person's "yes"
  writes a file and their "no" writes nothing, the system is asymmetrically
  biased toward accumulating whatever the generator produces, and the user
  experiences it as being asked the same question forever. A rejection is a
  memory — see the [rejected-value tombstone](../../patterns/rejected-value-tombstone/).
- **Do not keep review state in process memory.** Pending proposals are work in
  progress; losing them on restart is a bug even before the rejection problem.
- **Do not inject an unbounded blob every turn with no path that compacts it.**
  `memory.md` grows and the endpoint that would summarize it is a stub.
- **Do not let read-modify-write on whole JSON files be the persistence model**
  once more than one client can write.
- **Do not identify a class of message by how its text starts.** The history
  filter drops any assistant turn beginning `"Error: "`, which a real answer
  about an error message does. Classification belongs on the struct that wrote
  the message, not on a prefix a user can produce by accident.
- **Do not ship a second entry point that silently omits the background work.**
  A CLI folder looks like a full installation — same skills directory, same
  registry format, same prompt block — and its skill set can never change,
  because the only thing that would change it is started in the other binary.

### Fit

TigrimOSR suits an individual or small team who want a self-contained agent
platform they can install in a minute, run offline against local models, and
extend in YAML — and who value that the thing which learns from their sessions
asks before changing anything. As a *host*, the breadth is unusual for one binary.

As a *memory system* it is thin by design and should be read that way: one blob
per project, plus a skill library. Its contribution to this atlas is the
propose-stage-approve mechanism rather than the memory model, and that mechanism
is worth copying into systems whose memory model is much richer.

Do not adopt it where memory has to be correctable in the sense this atlas means.
A user who says "no, don't remember that" is answered, and then forgotten.

Pick the binary deliberately, because they are different products on this axis.
The desktop app is the one this report is about: it learns from your sessions and
asks before acting on what it learned. The `tigrim` CLI is a well-isolated agent
runner whose per-folder skill library is a fixture — the right choice if you want
directory-scoped configuration and no surprises, and the wrong one if you came
for the mechanism.

## 12. Open Questions

- **Was `synth_status` intended to persist?** It holds `last_run_at`, which only
  makes sense across runs, so the in-memory-only lifetime reads as an oversight
  rather than a decision. Issue history was not read.
- **Does the remote mode persist proposals on the server side?**
  `forward_proposal_action` and `/api/skills/auto/full-status` push the state to
  the remote instance, which has the same in-memory structure; whether a
  server-mode deployment behaves differently was not established.
- **What triggers `run_synthesis` in practice?** `scheduler.rs` exists and
  `run_synthesis_forced` is exposed; the default cadence was not traced.
- **What does `POST /:id/memory/generate` become?** It is a stub, and it is the
  hook where `memory.md` would acquire a lifecycle.
- **How do the swarm modes share memory?** A shared blackboard is described; what
  of it survives a run was not traced.
- **Is the CLI's missing synthesizer a decision or an omission?** The CLI is four
  days old at this pin and the commits describing it are about isolation and
  footprint, not about what to leave out. A scheduled LLM pass in a short-lived
  terminal process is a genuinely awkward fit, so either reading is plausible;
  nothing in the tree says which.
- **Where would a CLI folder's proposals live if they existed?** `skills.json` is
  already project-local, so the registry side is solved; the proposal list is the
  part with no home in either mode.
- **Why do seven skill packages ship without being installed?**
  `assets/skills/` holds twenty directories and `BUNDLED_SKILLS` lists thirteen.
  `brand-discovery`, `educational-grade-analysis`, `language-ranking-chart`,
  `marketing-research-report`, `product-research-pipeline`,
  `python-bar-chart-generator` and `tigrimos-market-research` are referenced
  nowhere else in the repository, so they reach no installation by any path.

## Appendix: File Index

**Skill memory** — `src/server/services/skill_synthesizer.rs`
(`SkillProposal`, `write_new_auto_skill`, `approve_proposal`, `reject_proposal`,
`get_proposed_diff`, `synth_status`), `src/server/routes/skills.rs`

**Project memory** — `src/server/routes/projects.rs` (`put_memory`, `get_memory`,
`load_project_run_context`), `src/ui/projects_view.rs`

**Persistence** — `src/server/data.rs` (`Skill`, `SkillAutoMeta`, `Project`,
`ChatSession`, `get_skills`, `save_skills`, `read_json`, and the overlay
resolvers `skills_root`, `resolve_data_file`, `resolve_config_file`,
`overlay_dirs`)

**CLI and project overlay** — `src/bin/tigrim.rs`, `src/cli/project.rs`,
`src/cli/run.rs`, `src/cli/commands.rs`, `src/cli/repl.rs`

**Agent loop and context** — `src/server/services/agent_loop.rs`,
`src/server/services/toolbox.rs`, `src/server/services/compact.rs`,
`src/server/services/graph.rs`

**Scheduling** — `src/server/services/scheduler.rs`

**Security** — `src/security/sandbox.rs`, `src/security/file_access.rs`

**UI review surface** — `src/ui/skills_view.rs`, `src/ui/settings.rs`

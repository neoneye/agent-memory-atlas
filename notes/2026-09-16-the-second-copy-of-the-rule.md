# The second copy of the rule is the one that decides

**Written 2026-09-16.** Prompted by re-reading twenty-four reports against their
upstream repositories in one pass. The same underlying problem accounted for
changes in seven of them, and it is not a bug class any of the atlas's capability
marks can see: a rule that governs a memory — what may be read, what a row's
status is, whether the store opens — was written down in more than one place, and
the copies diverged.

Three of the seven are the failure. Caura's own comment records an earlier leak
that moved from one copy of a predicate to the next; SuperLocalMemory had a tier
value reverted by the mirror of its own column; MentisDB had one of four load
sites with the wrong policy, and three copies of one vocabulary that had drifted
apart. In each case the copy that drifted was the one no test covered, and in two
of the three it was the copy that decided the outcome.

The other four are answers, which is why they are worth reading together:
centralise and enforce the centralisation (Caura), move the invariant to where
the data changes (Utopia), name the duplication and test the pair against each
other (Lorekit), or add a dimension and write down which read paths it does not
reach (teamai-cli).

The systems are unrelated — Python over Postgres, Rust over SQLite, TypeScript
over Postgres and over Cloudflare D1, Rust over Postgres. The shape is the same.

## 1. The predicate that leaked when it was copied

[Caura][caura] carries the clearest statement of the problem, in the docstring
of the function that fixes it. `_fleet_scope_clause` is the single builder every
fleet-scoped read calls, and its comment explains why it is single:

> A54 established what happens otherwise — the identical predicate lived in
> several queries, one was fixed, and the leak simply moved to the next copy.
> Every fleet-scoped read builds its clause here so "strict" cannot mean
> different things in different queries.

What makes it worth copying is that the project did not stop at centralising.
`tests/test_c27_strict_fleet_scoping.py:95-107` reads the storage module's own
source with `inspect.getsource` and asserts that `fleet_id.in_(fleet_ids)`
appears exactly once — inside the helper — and that `_fleet_scope_clause(`
appears exactly five times, the definition plus four fleet-scoped reads. The
failure message names the consequence rather than the count: an inline copy sits
outside the strict switch and is silently permissive.

A centralisation is a convention until something fails when it is broken.

[Lorekit][lorekit] shows the other honest answer, for when the copy cannot be
removed. Its tenant-visibility predicate exists twice — once for the Node MCP
core and once for the Deno edge functions, which cannot import across the
runtime boundary — and the module says so rather than pretending otherwise. The
copy is constrained in two ways: it is a filter-shaper that never re-derives
membership, taking an already-resolved org-id list so the predicate cannot drift
from the SQL function that is the sole source of truth, and a parity spec guards
the pair. A duplication that is named, narrowed, and tested against its twin is
a different thing from one that merely exists.

## 2. The mirror that reverted the authority

[SuperLocalMemory][slm] stores a memory's tier twice, in an authoritative column
and a mirror that a reconcile step syncs one way. Release 4.1.15 corrected how
the tier is decided; the maintenance pass then wrote the corrected value to the
mirror, and reconcile — later in the same cycle — put the old value back. On a
real store the corrected tiers appeared and were gone within one pass.

The test that was supposed to cover this passed throughout.
`test_lifecycle_has_one_authority.py` asserted that reconcile syncs in the right
*direction*. It never asserted that a value the maintenance pass had just written
was still there afterwards. The replacement is named for the property rather than
the mechanism — `test_a_recomputed_lifecycle_survives_the_tick.py` — and the fix
routes all four write sites through one `_persist_lifecycle` that writes both
columns, with a check that fails the build if a new site writes only the mirror.

## 3. The load site that had the wrong policy

[MentisDB][mentisdb] holds a canonical append-only thought log and a vector
sidecar derived from it. Failing closed is right for the log and wrong for the
sidecar, which is always rebuildable — and three of the four sidecar load sites
did exactly that. The fourth, `manage_vector_sidecar`, put the load error in its
match scrutinee with `?`, so a stale sidecar WAL aborted chain open for every
daemon request. The canonical store was intact and unreachable because something
computed from it would not load.

The same repository carried its `ThoughtType` vocabulary in three hand-maintained
string tables, in `server.rs`, `llm.rs` and `lib.rs`. They had drifted far enough
that the server's copy silently rejected two valid variants, `Goal` and
`LLMExtracted` — a stored genre an agent could not name at the boundary that
writes it. All three now delegate to one `FromStr`.

## 4. Where the invariant belongs

[Utopia][utopia] assembles every temporal read predicate in exactly two modules,
and the module head says why in terms that generalise past temporality: a defence
scattered across every read point fails silently when one is missed, because SQL
does not complain and neither does the compiler. In the same window it moved a
second invariant for the same reason. Conflict withdrawal used to happen inside a
read path; migration `0051` moves it onto a trigger on the `facts` table, with
the arithmetic stated — twelve sites set `invalidated_at` and four undo it,
patching each is a matter of time before one is missed, and the invariant belongs
where the data changes.

[Lobu][lobu] states the composition requirement as a warning rather than leaving
it to be inferred. Its resource-visibility compiler does not fence soft-deleted
connections, because the sibling connection-visibility compiler does; the header
ends *"never use this compiler standalone."* Two predicates that are only correct
together are one rule in two files, and saying so in the source is the cheapest
guard available.

## 5. The useful inverse

[teamai-cli][teamai] added a second scoping dimension in the same period —
roles, alongside projects — and deliberately kept it out of the memory read path.
`resolveProjectResourceNamespaces` states that it is *"the ONLY source of
learnings namespaces. Roles never contribute them"*, and the caller unions the
two dimensions on the knowledge and skills axes only. Same-named resources across
a role and a project namespace are treated as an admin-side duplicate rather than
a runtime precedence rule, which is the decision that keeps the learnings
predicate single-authority.

Adding a dimension to a system and writing down which read paths it does *not*
reach is the same discipline as centralising one, arrived at from the other end.

## What this suggests for a reviewer

The atlas's capability marks ask whether a mechanism exists and whether a
reachable path uses it. None of them asks how many implementations of it there
are, and on this evidence that is the question that decides whether the mechanism
holds a year later. Three checks are cheap:

- **Count the call sites of the rule, and count the inline copies separately.**
  A scope predicate, a status filter or a decay threshold that appears more than
  once is a rule with a second copy, whether or not both copies are correct today.
- **Ask which copy the failure path reads.** MentisDB's odd site out was the one
  that decided whether the store opened at all; SuperLocalMemory's was the one
  written last in the cycle. The dangerous copy is rarely the most-used one.
- **Read the test for what it asserts, not what it is named.** A test that pins
  the mechanism — this function syncs in this direction — can pass indefinitely
  while the outcome it exists to protect does not hold.

[caura]: ../systems/caura/
[slm]: ../systems/superlocalmemory/
[mentisdb]: ../systems/mentisdb/
[utopia]: ../systems/utopia/
[lobu]: ../systems/lobu/
[teamai]: ../systems/teamai-cli/
[lorekit]: ../systems/lorekit/

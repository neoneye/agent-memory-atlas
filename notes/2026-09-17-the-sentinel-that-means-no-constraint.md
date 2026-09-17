# The sentinel that means "no constraint"

**Written 2026-09-17.** Prompted by reading sixteen systems in one pass. Five of
them shared a defect I had been treating as five unrelated bugs, and the shape
only became visible because two of the five had already found it themselves and
written the diagnosis into their own tests.

The shape: a parameter has a value that means *no constraint* — zero days, an
empty list, a null timestamp, an unset variable — and the code that applies a
default cannot distinguish that value from the parameter being absent. The
language's own defaulting operator then resolves the ambiguity, and it resolves
it the same way every time.

**The failure direction is not random.** `||`, `or`, and `or None` all treat the
sentinel as missing, so the caller's explicit request is replaced by the
system's default. When the sentinel meant *narrow to nothing*, the result is a
widening. When it meant *do not act*, the result is an action.

## 1. Zero meant "off" and the default deleted

[ai-maestro][aim] carries two instances in one file. `pruneShortTermMemory`
opens with `const retentionDays = options.retentionDays || DEFAULT_MEMORY_SETTINGS.retention.shortTermDays`,
and the very next statement is `if (retentionDays === 0) { … return { pruned: 0 } }`.
The default is 30, so `0 || 30` is 30 and the disable branch can never fire from
a caller. The PATCH route passes the body's value straight through, which makes
`{"action":"prune","retentionDays":0}` — the documented way to ask for no
pruning — a request that hard-deletes every message older than thirty days in
consolidated conversations. The off switch is the delete switch.

Its sibling is quieter. `searchMemoriesByEmbedding` sets
`const minConfidence = options.minConfidence || 0.5`, and the long-term memory
endpoint documents a default of 0 and passes exactly that. So the documented "no
threshold" request applies a 0.5 floor, and every memory the extracting model
scored below 0.5 is unreachable through the query path — while still visible in
the unfiltered list view, which is what makes it hard to notice.

## 2. An empty list meant "nothing matched" and the search widened to everything

[memory-vault][mv] had the same collapse on a scope filter, which is the
dangerous place for it. `resolve_space_names` returned `[]` for names that
resolved to nothing, and the caller collapsed that to `None` with `or None` —
and `None`, in that search builder, means *no space filter*. So
`spaces=["unknown"]` searched every space.

The fix and the test are both worth copying. `_build_where_clause` now documents
three cases where most code has two:

> `None` → no space filter (search every space)
> `[]` → caller asked for specific spaces but none resolved; return zero rows
> (a hard `false` predicate) rather than silently widening to every space

and the end-to-end test ingests a uniquely-tokened document, searches for it
under a nonexistent space name, and asserts zero results — with the next test
asserting that a search with *no* filter still finds its own token, so the fix
cannot pass by breaking the unfiltered path.

Asking for nothing and asking for anything are different requests. Two branches
cannot express three states.

## 3. A timestamp tested for presence, not against the clock

The same ambiguity appears without any defaulting operator when a nullable
timestamp is used as a boolean.

[Beever Atlas][ba] retires a fact by setting `invalid_at`, and its reads skip a
fact whose `invalid_at is not None`. That makes the column a flag that happens to
carry a date: a fact invalidated with a *future* timestamp is withheld from the
moment the stamp is written rather than from the moment it names, so scheduling
an expiry is impossible and attempting it silently deletes early.

[Deus][deus] shows the other form. Its read predicate is
`(e.expired_at IS NULL OR e.expired_at > date('now'))`, compared against the
clock across eight query sites, so an atom known to be true until the end of the
quarter can be stamped now and stays retrievable until then. The same column, the
same nullability, and a different question asked of it.

Interestingly Deus is not consistent with itself: its *relationship* reads use
the stricter `expired_at IS NULL`, so an edge expires immediately. Nothing in the
code says whether that asymmetry was chosen.

## 4. The guard that compared against NULL and matched nothing

[Pensyve][pen] is not a falsy collapse, but it belongs here because the outcome
is identical: a constraint that was present, correct, and doing nothing.

Its row-level security scoped queries through a Postgres session variable, set
with `set_config('pensyve.namespace_id', $1, true)`. The `true` means
transaction-local; a standalone statement is its own implicit transaction; so
the setting was discarded before the query it was meant to scope ever ran. In the
module's own words, *"every policy compared against NULL and matched nothing."*

A second instance sits beside it. Postgres exempts a table's owner from its own
policies, and the application connected as the schema owner, so `ENABLE ROW LEVEL
SECURITY` left them inert until `FORCE` was moved into the schema applied at
every startup.

Two independent ways for a security control to be configured, reviewed, merged,
and completely ineffective — with no error, no warning, and nothing in a test run
that would look different.

## What this suggests for a reviewer

The unifying question is not "is there a default?" but **"can this parameter
express three states?"** Absent, present-and-empty, and present-and-populated are
three different requests, and a two-state representation forces two of them to
share an answer.

Four checks, all cheap:

- **Find every `||`, `or` and `or None` applied to an option whose zero, empty
  list or empty string means something.** `??` and an explicit `is None` cost one
  character and one line respectively. This is the whole of §1 and §2.
- **Ask what the empty case does, separately from the absent case.** If they
  produce the same SQL, one of them is wrong — and it is nearly always the empty
  one, resolving in the widening direction.
- **For any nullable timestamp used as a state, check whether it is compared to
  the clock or tested for presence.** A date that only ever means "set" should
  have been a boolean; a date that is compared should be compared everywhere.
- **Prove the guard fires.** Pensyve's technique generalises past Postgres: its
  test takes the production statement, *deletes the scope predicate*, runs it
  across tenants and asserts nothing moved. A guard that has never been observed
  refusing anything is a guard nobody has tested.

The two projects here that found their own instance both did it the same way —
by hitting the symptom in use, then writing the mechanism into a test docstring
rather than a commit message. memory-vault's test says the filter *"used to
silently widen to every space"*; pensyve's module header says the GUC was
discarded before the query ran. Neither would be recoverable from the diff.

[aim]: ../content/systems/ai-maestro.md
[mv]: ../content/systems/memory-vault.md
[ba]: ../content/systems/beever-atlas.md
[deus]: ../content/systems/deus.md
[pen]: ../content/systems/pensyve.md

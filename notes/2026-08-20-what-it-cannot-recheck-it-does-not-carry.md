# What it cannot re-check, it does not carry

**Status:** triaged and excluded, with four mechanisms recorded. A new exclusion
class: not *the durable thing cannot be false*, but *there is no agent for whom
it is memory*.
**Origin:** `commaai/openpilot` submitted for analysis on 2026-08-20. Read at
[`555f48c5d28709f039b79f3f6105e51305edd4b5`](https://github.com/commaai/openpilot/commit/555f48c5d28709f039b79f3f6105e51305edd4b5)
(2026-08-19), MIT, ~500 Python files in a 3.5 GB checkout. Screened first: three
auto-run surfaces, two build-time execution points, two dependency manifests
inside the seven-day cooldown, and an uninstalled `scripts/post-commit` hook —
so nothing was installed, nothing was built and no device was involved.

---

## The scope call, and why it is a different one

openpilot is driver assistance for 300+ cars. It has no language model with
tools, no retrieval surface, and nothing a model queries. Every previous
exclusion in this directory turned on the *durability* half of the test — a
harness that persists is not a memory that believes, an idempotency key cannot
be wrong, a schedule is an intent. This one inverts that.

**Its persisted state is genuinely falsifiable.** `LiveParametersV2` holds a
learned steering ratio, stiffness factor and angle offset; `LiveTorqueParameters`
holds a learned lateral-acceleration factor, offset and friction coefficient;
`CalibrationParams` holds learned camera extrinsics; `LiveDelay` holds a learned
actuator delay. Each is a claim about a specific vehicle, inferred from
observation, wrong often enough that the code is mostly about noticing, and
carried across ignition cycles. That is a belief store by every part of this
atlas's test except the one that names who is doing the believing.

So the exclusion is: **there is no agent here to hold a memory.** The values are
consumed by a Kalman filter and a controller, not recalled into a context. The
[tool-registry test](2026-08-14-a-coding-agent-whose-search-is-the-users-not-the-models.md)
does not merely fail — there is no registry to grep, because there is no model
with tools. Recording the class explicitly, because "falsifiable but not agent
memory" is a boundary this corpus had not previously had to draw, and the next
robotics or control repository submitted will land on it too.

What follows is why it was worth the reading anyway.

## 1. It names the one thing it cannot re-validate, and refuses to persist it

`selfdrive/locationd/paramsd.py:234-237`, in the middle of a load path that
restores three learned values:

> ```python
> if not replay:
>   # When driving in wet conditions the stiffness can go down, and then be too low on the next drive
>   # Without a way to detect this we have to reset the stiffness every drive
>   stiffness_factor = 1.0
> ```

Four learned parameters, and the code separates them by whether the condition
that produced the value is detectable later. Steering ratio and angle offset are
properties of the vehicle and survive; stiffness is a property of the vehicle
*and the road surface*, the road surface is not observable at startup, and
therefore the value is thrown away every drive — deliberately, with the reason
written where the decision is made.

This atlas spends a great deal of prose on systems that carry beliefs they
cannot check. Almost nothing in the corpus does the opposite: identifies which
of its own learned values depends on a condition it cannot re-observe, and
declines to carry that one. **The generalizable rule: persistence is not a
property of the store, it is a property of each fact — decided by whether the
conditions that made it true can be re-observed when it is read back.**

The nearest thing the corpus has is bi-temporal validity, which records *when* a
fact was true and leaves the reader to decide. This is stronger and cheaper: if
the answer would always be "cannot tell", do not write the row.

## 2. The learned value is keyed to the thing it is about, and to the method

`selfdrive/locationd/torqued.py:36` — `VERSION = 1  # bump this to invalidate old
parameter caches` — and `:129`:

```python
def get_restore_key(CP, version):
  ...
  return (CP.carFingerprint, CP.lateralTuning.which(), a, b, version)
```

A cached belief is restored only when the car fingerprint, the tuning scheme, the
two static tuning constants the learner refines, **and the learner's own version**
all match. Change the algorithm and every belief it ever produced stops being
restorable, without a migration, a sweep or a scheduled expiry — the key simply
stops matching.

`paramsd.py:215` does the coarser version of the same thing and raises
`Exception("Car model mismatch")` when `last_CP.carFingerprint != CP.carFingerprint`.

This is the self-invalidating key the har note admired in a different domain — a
validation record filed under the hash of the tree it certifies — arrived at
independently by people learning physical constants. **A memory whose key
includes what it is about and how it was derived cannot be stale; it can only be
absent.** Memory systems key on subject alone and then need decay, TTLs and
re-verification sweeps to approximate what a composite key gives for free.

## 3. On an invalid load it deletes the record rather than ignoring it

`paramsd.py:230-232`: any failure in the restore path — mismatch, insane value,
a parse error — is caught and followed by `params.remove("LiveParametersV2")`,
then a log line, then defaults. The bad memory is not kept-and-skipped, not
marked and left, not silently overwritten later; it is removed on the spot.

Set that beside
[the empty-read defect class](2026-08-20-a-failure-that-reads-as-empty.md) found
three times this month, where a forgiving loader returns an empty value and the
next save persists the emptiness. openpilot's loader is also forgiving — it
catches everything — but it *acts* on the failure by deleting the source of it,
so the next boot reads a genuinely absent record rather than a corrupt one that
reports as empty. **A forgiving loader is safe exactly when it removes what it
could not parse.**

The sanity check beside it is worth quoting for its shape:
`min_sr, max_sr = 0.5 * CP.steerRatio, 2.0 * CP.steerRatio`, and a stored value
outside that band raises. The bound is relative to a static value the vehicle
already declares, not an absolute constant — so the check travels to 300 cars
without a table.

Also at `torqued.py:108-116`: when the restore key matches but `cache_ltp.valid`
is false, the fitted parameters are refused **and the raw sample points are
restored anyway**. Evidence before belief, in a system that has never heard the
phrase: the conclusion is discarded, the observations that produced it are kept,
and the learner restarts from data rather than from zero.

## 4. Retention is declared per key in one file and executed by the lifecycle owner

`common/params_keys.h` gives every key a flag beside its type:

```
{"CalibrationParams",     {PERSISTENT, BYTES}},
{"CarParams",             {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, BYTES}},
{"LiveTorqueParameters",  {PERSISTENT | DONT_LOG, BYTES}},
{"AccessToken",           {CLEAR_ON_MANAGER_START | DONT_LOG, STRING}},
```

and `system/manager/manager.py:31-34` and `:131-137` execute them —
`params.clear_all(ParamKeyFlag.CLEAR_ON_MANAGER_START)`, the same for
`CLEAR_ON_ONROAD_TRANSITION` and `CLEAR_ON_IGNITION_ON` — at the three lifecycle
points that own those transitions.

Two properties the corpus's retention machinery usually lacks. The lifetime is a
property of the **key**, enumerated in one readable file rather than implied by
whichever writer happens to delete things; and the clearing is done by the
**lifecycle owner**, not by each subsystem remembering to clean up after itself.
`DONT_LOG` sits in the same flag word, so "how long does this live" and "may this
leave the device" are answered in the same declaration.

Compare Redis Agent Memory Server's `select_ids_for_forgetting`, which the
comparative report praises for combining age and inactivity: that is a good
*policy*, evaluated at runtime over rows. This is a good *schema*, evaluated by
grep.

## 5. Validity flips with hysteresis

`paramsd.py:155-157` runs each learned offset through
`check_valid_with_hysteresis(previous_state, value, MAX, LOWERED_MAX)`: a value
becomes invalid when it crosses `MAX` and becomes valid again only when it falls
back under a lower threshold. The published message then carries
`angleOffsetValid`, `angleOffsetAverageValid`, `roll_valid` and `sensorValid` as
separate booleans beside the numbers.

The atlas has [retrieval hysteresis](../content/patterns/retrieval-hysteresis.md)
for units that would otherwise flap in and out of context, and a
[trust-state machine](../content/patterns/trust-state-machine.md) for discrete
epistemic status. This composes them: **hysteresis applied to the trust state
rather than to retrieval**, so a memory sitting near its plausibility boundary
does not alternate between believed and doubted on consecutive reads. Nothing in
the corpus does that, and the systems most likely to need it are the ones whose
confidence scores hover near a threshold.

## What it is not, and one clean vocabulary result

No provenance beyond the restore key, no audit of mutations, no human review
surface, no notion of a rejected value — and none of those is a gap, because the
consumer is a filter that will re-derive the value in a few minutes of driving
anyway. The whole design is only coherent because **the beliefs are cheap to
re-learn**, which is the property most agent memory lacks and the reason its
correction machinery has to be heavier. That contrast is the honest summary of
what transfers: mechanisms 1–4 transfer; the confidence to delete on doubt does
not, unless your store can re-derive what it dropped.

**A fifth instance for [the vocabulary probe](2026-08-19-the-vocabulary-probe-lies.md),
and the funniest one.** A grep for `tombstone` — this atlas's rarest and
most-cited mechanism — returns `system/tombstoned.py`, a crash-dump reporter:
*"reporting new tombstone"* means a Linux process died and left a dump. `forget`
returns the WiFi settings screen; `remember` returns a path-memoisation helper in
a plotting tool. Every hit for the corpus's three sharpest words, and not one of
them about memory.

## For next time

Two things to carry back into the reviewing method.

**Ask, of any persisted value: could the condition that made this true be
re-observed on read?** If not, the honest options are to drop it on write (what
openpilot does with stiffness) or to store the condition beside it. A store that
carries such a value silently is making a claim it cannot support, and the review
format has no prompt for this today.

**A composite restore key is an alternative to decay, not a detail.** When a
report describes TTLs, half-lives or re-verification sweeps, it is worth asking
what the system would need to key on for staleness to become impossible instead
of scheduled. Usually the answer is the subject plus the version of whatever
derived it, and usually both are already at hand.

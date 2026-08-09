# The strong-form tombstone subset — five of nine, and a taxonomy instead of a count

**Status:** done. This is the follow-up
[the rare-mechanisms note](2026-08-06-rare-mechanisms-and-useful-inversions.md)
left open, and that two earlier passes declined to touch.
**Method:** the nine reports carrying the `tombstone` mark, re-read at their
pinned commits, against the four properties the pattern page's strong form
names. Derived from the committed reports rather than from a fresh code read;
where a report does not state a property, this note says so rather than
inferring it.

## The question

The atlas says nine systems of 164 carry a rejected-value tombstone. The
[pattern page](../content/patterns/rejected-value-tombstone.md) defines the
mechanism more narrowly than the mark does: a record **keyed on the value**,
**normalized**, **consulted on the write path**, **refusing activation**. Both
sentences are true and they are not about the same set, which is a
definition/count mismatch an outside review caught. So: how many of the nine
implement the form the page argues for?

## The answer

**Five of the nine, when this was written; six of eleven now.** And the four
that do not fail in three distinguishable ways, which turns out to be more
useful than the number.

| System | Value-keyed | Normalized | Read before the write? | Write refused? | Kind |
| --- | --- | --- | --- | --- | --- |
| [memsem](../content/systems/memsem.md) | yes | yes — normalised subject, predicate, object | yes, `memory_add` checks first | yes — `{rejected: true}`, no row | **Consulted** |
| [perseus-vault](../content/systems/perseus-vault.md) | yes — digest, not value | yes — `normalize_rejected_value` | yes, every remember-path write | yes, with a named test | **Consulted** |
| [universal-memory-engine](../content/systems/universal-memory-engine.md) | yes — canonical label | yes — `canonicalKey` | yes, four points in the write gate | yes — `suppressed_blocked` | **Consulted** |
| [rainbox](../content/systems/rainbox.md) | yes — `value_key` | yes — `belief_keys`/`_SHAPE_RULES`, no LLM | yes — dedupe → **tombstone** → conflict → create, under lock | yes, refusals counted in `hit_count` | **Consulted** |
| [verel](../content/systems/verel.md) | yes — ledger on `make_key(subject, predicate, scope)` | asserted, function not named in the report | yes — the gate sees the ledger; `approve()` refuses a rejected record | yes — a re-write stays rejected | **Consulted** |
| [noosphere](../content/systems/noosphere.md) | yes — HMAC `subjectHash` over the capture | yes — `digestWithAllKeys` across the retained keyring | yes — inside the serializable transaction, after `lockLineages` | yes — a 409, *"Capture was previously revoked"* | **Consulted** |
| [daimon](../content/systems/daimon.md) | yes — content-derived id | yes — `canonical_text`: NFKC, invisibles, casefold, **confusables** | partly — the supersede-candidate emitter consults it; the capture path does not | no — the value re-enters the checkpoint and is suppressed on every read | **Hybrid** |
| [provem](../content/systems/provem.md) | yes | yes — token set with a subset test | no | no — read-side suppression, stated as the known limit | **Suppressed** |
| [mnemosyne](../content/systems/mnemosyne.md) | yes — SHA-256 of the triple | yes — NFC, length-prefixed | no — nothing reads the rejection | no — the write lands **on** the tombstoned row and bumps its counts; `superseded_by` stays set | **Collided** |
| [nova-ai](../content/systems/nova-ai.md) | yes — the definition text | no evidence of normalization; matched by definition text | no | no — same collision; only `source == "user"` can promote | **Collided** |

## The taxonomy is the finding

Counting stops being interesting once you notice the four rows below the line
are not one failure mode but three, separated by a single question: **does
anything read the rejection before the write completes?**

- **Consulted (5, now 6).** Something looks the value up and the write does not
  happen. This is the pattern as argued.
- **Collided (2).** Nothing looks anything up. The rejection survives because the
  primary key *is* the value, so a re-extraction lands on the rejected row
  instead of minting a live one. Durable, free, and **held in place by the
  absence of a filter** — both reports say the same thing, that adding
  `AND superseded_by IS NULL` or `AND status != 'rejected'` during a tidy-up
  would remove the guarantee silently, and neither project has a test.
- **Suppressed (1).** The write lands, the read path hides it. Real protection
  for the agent, no protection for the store — which for Provem, whose stated
  purpose is GDPR Article 17, is the distinction that matters most.
- **Hybrid (1).** Daimon is all three at once: collided by content-addressed id,
  suppressed on every read path, and consulted by exactly one write path.

**The two collisions are the same accident, independently.** Two systems, two
languages, two data models, no shared lineage, both arriving because dedup is
written against content and rejection against the same record. That is a
stronger observation than either instance: the property is *reachable by
accident*, which says something about how cheap it would be to reach on purpose,
and something else about how easily it is lost.

## What this changes on the published pages

Three things, all now fixed.

**The pattern page contradicted a report.** It said of Daimon *"the key is not
normalized — it is a hash of the exact text"*. The Daimon report's own history
records the correction on **2026-07-30**: *"the tombstone key is canonical rather
than literal text"*, one of three published claims that stopped being true at
that re-read. The report was updated; the pattern page, which repeats the claim
as an argument, was not. Six days of two atlas pages disagreeing about the same
mechanism, and the stale one is the page a reader is sent to.

**The ninth holder had no entry.** The page characterises the first through the
eighth and its own blockquote says *"one carries the mark without yet being
characterised here"* — that is
[universal-memory-engine](../content/systems/universal-memory-engine.md), and it
belongs in the consulted group: `addSuppression` keyed on the candidate's
`canonical_key`, checked at four points in the write gate, a hit rejected as
`suppressed_blocked`, and the cleanup pass writing suppressions too so a deletion
binds the future.

**A superlative in the verdicts was falsified by the page next to it.** Mnemosyne's
verdict called it *"the only one that appears to be a side effect"* while the
pattern page already described Nova AI as the same accident. Corrected to two.

## What this does not settle

- **Verel's normalization is asserted, not shown.** The report says a
  normalization mistake at the boundary is where the mechanism would leak, and
  the page's round-9 lesson is about look-alikes evading its key, but no report
  names the function. That is the one cell in the table above that a code read
  would firm up.
- **Nova AI is marked "no evidence of normalization"**, which is a statement
  about the report, not about the code. Per the atlas's own rule, that is not the
  same as "it does not normalize".
- **Five is not a recommendation.** Four of the five arrived through this atlas's
  own orbit — one invented under adversarial pressure, one adopted from it, two
  built after a report named the absence — so the count still measures the
  atlas's reach as much as the field's practice. The
  [rare-mechanisms note](2026-08-06-rare-mechanisms-and-useful-inversions.md)
  states why that matters for any novelty claim built on it.

## Follow-up

The honest next step is the one the pattern page has been deferring under a
different name: **a test that distinguishes consulted from collided.** Write the
value, reject it, re-assert it through the extractor, then assert both that no
new live row exists *and* that the store contains no second copy. The consulted
five pass both halves; the collided two pass the first and fail the second; the
suppressed one fails the first. Nobody has to be told which group they are in —
the test says it.


---

## 2026-08-09 — a sixth consulted instance, and the property none of the others has

[Noosphere](../content/systems/noosphere.md) was added from
[the outside corpus](2026-08-09-seventy-one-repositories-from-an-outside-corpus.md)
and lands in the **Consulted** row on all four properties. It is added to the
table above rather than kept separate, because it fails none of them.

What it adds to the taxonomy is a fifth question the other five never had to
answer: **what happens to a value-keyed tombstone when the key rotates?**

Noosphere's `subjectHash` is an HMAC, not a plain digest. Rotate the secret and
every stored `subjectHash` becomes uncomputable from new input — so a naive
implementation silently readmits every value it had ever refused, with no error
and no signal. The fix is in the comment beside the check:

> A tombstone from any retained key version blocks recreation. Historical keys
> remain in the bounded keyring until their tombstones and source TTLs have
> expired.

`digestWithAllKeys` computes the candidate's digest under every retained key
version and matches the tombstone against the whole set; `MemoryTombstone`
stores `hmacKeyVersion` so the retention policy is auditable.

**The five earlier instances do not have this problem and could acquire it.**
memsem, Perseus Vault, Universal Memory Engine, RainBox and Verel all key on a
plain normalised value or a digest with no secret. Any of them adding a keyed
hash — for privacy, for multi-tenancy, for anything — would need this exact
mechanism, and the failure would be invisible: the tombstone table would still
be full, the checks would still run, and nothing would ever match.

The cost is the reason it is bounded. Retaining historical keys is what makes
the check possible, so the keyring size is bounded by the tombstone TTL — ninety
days here. **This is the first tombstone in the atlas with a deliberate
expiry**, and the pattern page's strong form should probably grow a fifth
question of its own: *for how long?*

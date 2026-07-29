# What survives encryption

**Status:** design note; nothing here was read in code
**Origin:** the open questions on [Buzz](../content/systems/buzz.md), which is
the atlas's only system whose storage provider can read neither the content of a
memory nor which memory it is. Its report ends by saying that embeddings over
ciphertext the relay cannot read is a research problem rather than a backlog
item, and stops there. This note is the argument that stopping there concedes
too much.

**Read this differently from a system report.** Every other document in this
repository describes code at a pinned commit. This one reasons about a design
that no system here implements. Where it refers to Buzz, MemMachine, Daimon,
Verel or RainBox it refers to code that *was* read; everything else is argument,
and should be treated as the weaker kind of claim this atlas usually avoids
publishing.

## The boundary that decides everything

**A model must see plaintext to use a memory.** That is not a limitation of any
cipher; it is what *use* means. So encryption can protect memory at rest and in
transit, and the trust boundary sits wherever plaintext has to materialise —
the client.

Everything below follows from that single constraint. "Encrypted memory" is
really **client-side encryption over a storage provider that can read nothing**,
and the design question is narrower and more tractable than it first appears:
which memory operations still work when the server holds only ciphertext?

## What survives, and the one thing that does not

| Operation | Under encryption |
| --- | --- |
| Write | Unchanged. Encrypt client-side, store the blob |
| Fetch by key | Unchanged, if the key is blinded. Buzz's `d = HMAC(K_c, slug)` is exactly this and costs one hash |
| Delete by key | Unchanged, and strictly better than plaintext — see crypto-shredding below |
| Graph edges | Fine, provided node identifiers are already blinded |
| Scope enforcement | **Improved.** A different principal derives different blinded keys, so namespaces are not merely un-joined but unaddressable. Buzz earns `scope_enforced` this way rather than with a `WHERE` clause |
| **Similarity search** | **Breaks.** You cannot rank ciphertext by meaning |

Buzz gets every row but the last, which is why it is a real system with a relay
that knows nothing — and why its ceiling is a few hundred hand-curated entries
reachable by `[[slug]]` reference from a `core` engram.

## Four ways out of the retrieval problem

In descending order of how much weight I would put on them:

1. **Keep the index client-side and the content server-side.** The size
   asymmetry favours this more than people assume. A 384-dimension vector
   quantised to int8 is ~384 bytes, so 100k memories is roughly 38 MB of index —
   comfortable on a phone, trivial on a laptop. The server becomes an encrypted
   blob store; the client holds vectors and searches locally. **This needs no
   exotic cryptography and is buildable today.**
2. **Secure enclaves.** Practical now, and honest about what it is: not
   "the server learns nothing" but "trust relocated to a hardware vendor and an
   attestation chain". Sometimes the right trade; not the same claim.
3. **Searchable symmetric encryption.** A real literature with real systems.
   Leaks access patterns and search patterns, which over a long-lived personal
   corpus is far more than it sounds — query frequency alone profiles a user.
4. **Homomorphic vector search, or PIR.** Real and improving, still far too slow
   for interactive retrieval at personal-corpus scale.

**(1) is the answer for anything shippable.** It also explains Buzz's shape: it
took the strictest possible version — no index at all — and paid for it in
recall.

## What encryption uniquely fixes

This is the part worth the note, because it is not a cost but a capability the
atlas has been looking for.

### Crypto-shredding is the only answer to propagated copies

Encrypt each memory under its own key and deletion becomes key destruction. The
ciphertext survives; it is permanently unreadable. That reaches backups,
replicas, snapshots, and copies sitting on infrastructure you do not control —
because you were never going to chase those copies, and you do not have to.

That matters here specifically. The
[security survey](2026-07-29-security-research-names-the-column.md) defines
Verified Forgetting as content being unrecoverable "from any substrate —
including raw logs, compressed summaries, vector indices, and **propagated
copies**", and that note recorded propagated copies as the gap in this atlas's
own [deletion test](../content/benchmarks.md). Crypto-shredding is the only
mechanism encountered in this whole corpus that addresses it. Every plaintext
system's deletion is a statement about the stores it knows about.

### A tombstone that is better under encryption than without it

Buzz's tombstone is a `value: null` head keyed on the **slug**, so re-writing
the same rejected value succeeds. The atlas's three tombstone holders — Verel,
RainBox, Daimon — key on the value, and therefore must **retain the wrong value**
in order to block it. That is an uncomfortable property when the thing being
forgotten is the sensitive thing.

Encryption admits a construction that avoids it:

```text
on reject:  store  HMAC(k_tomb, normalize(value))     # blinded fingerprint
on write:   compute the same HMAC, refuse on match
```

The storage provider sees a keyed hash and learns nothing. The client refuses
re-assertion **without ever retaining the rejected plaintext**. For a "forget
that I said X" request, that is the behaviour a user actually means, and no
plaintext tombstone in this atlas can offer it.

Two honest limits:

- It catches exact re-assertion after normalisation, not semantic re-assertion.
  *"I live in Berlin"* and *"my home's in Berlin"* have different fingerprints.
  The client holds plaintext, so a semantic check can run there too — but that
  is a model call on the write path, with the cost that implies.
- The tombstone set grows without bound and is itself sensitive in aggregate: a
  fingerprint set is a set of things this person asked to forget. It wants the
  same lifecycle discipline as the memory it guards.

### It forces the architecture this atlas keeps recommending

If the server can read nothing, then extraction, deduplication, conflict
detection and tombstone checks have nowhere to run except the client. The
[governed write gateway](../content/patterns/governed-write-gateway.md) stops
being a discipline a team maintains and becomes structural. Encrypted memory is,
almost incidentally, better-governed memory — which is the opposite of how the
trade is usually described.

## What it actually costs

- **All server-side background work disappears.** No nightly consolidation, no
  server-side dedup, no server-side re-embedding. Changing embedding model means
  the client downloads everything, re-embeds, and re-uploads — a cost that scales
  with corpus rather than with the day's activity, and the exact inverse of the
  property [MemMachine](../content/systems/memmachine.md) gets from its
  `is_ingested` watermark.
- **Metadata leaks and padding is not free.** Item count, sizes, write timing,
  access patterns, and — if edges are stored — the shape of the graph. Buzz
  blinds the index and the relay still sees that this agent wrote three things at
  14:02. Padding and batching buy some of it back at a latency and bandwidth
  cost that has to be budgeted, not waved at.
- **Crypto-shredding and provenance are in tension.** MemMachine's best property
  is that its citations *resolve*, because the episodes are retained. Shred the
  key for an episode and every citation to it dangles — you have kept the audit
  trail and destroyed the evidence it points at. A system wanting both needs to
  decide, per class of memory, which one wins.
  [Daimon](../content/systems/daimon.md) is the most encryption-compatible
  design in the atlas for exactly this reason: it stores a hash of the source and
  a quote with a message id rather than the transcript, so there is less to
  shred and the link was checked at write time.
- **Sharing and forgetting fight each other.** Re-encrypt a memory to another
  agent's key and your deletion can no longer reach it. Key hierarchies with
  revocation are the answer and are the genuinely hard part of the design — the
  security survey gives SHARE & PROPAGATE its own lifecycle phase, and it is the
  phase this note is least confident about.

## The sketch

A client-side memory engine over a dumb encrypted blob store:

- per-item content keys under a revocable hierarchy;
- blinded slugs (`HMAC(k, slug)`) so the store cannot correlate topics;
- the vector index local and quantised, synced as an encrypted blob;
- extraction, conflict detection and tombstone checks client-side, because they
  have nowhere else to run;
- deletion implemented as key destruction, with a blinded-fingerprint tombstone
  retained afterwards;
- an explicit, budgeted acceptance that volume and timing leak.

That is roughly **Buzz plus a local index plus per-item keys**, and the distance
from what Buzz already is to that is smaller than the distance from Buzz to any
conventional memory service.

## What would have to be checked before believing any of this

- Whether the int8-index-on-device figure survives contact with a real corpus,
  including metadata, deleted-but-not-compacted rows, and multiple embedding
  versions in flight.
- Whether a blinded-fingerprint tombstone survives an adversary who can *guess*
  values: an HMAC over a low-entropy space (a city, a name) is a dictionary
  attack for anyone who obtains `k_tomb`. It protects against the storage
  provider, not against a client compromise.
- What key rotation does to the tombstone set, which must remain comparable
  across rotations or every rotation forgets what was forgotten.
- Whether any existing system does the local-index-plus-encrypted-blob split
  already. None of the 77 reviewed here does, but the atlas's selection rule is
  opportunistic and this is a shape a privacy-focused product would plausibly
  have built without publishing about it.

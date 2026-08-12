# The marks are invisible on the page that earns them

**Status:** proposed. The gap is verified; the fix is not adopted.
**Origin:** an outside review (Qwen, 2026-08-13) asked the atlas to *"define the
rubric — stop using a black box"*, claiming each report page lists seven
mechanisms with no definition of what earns one. That description is wrong in a
way worth following: the page lists **none** of them.

## What is actually there

`content/systems/<slug>.md` carries the marks in frontmatter:

```yaml
capabilities: "trust_state, scope_enforced"
```

That key feeds `scripts/extract_stack.py`, the generated
[capability index](../content/capabilities.md), the capability grid and the
comparative matrix, and `npm test` fails when a report omits it. It does not
reach the rendered report. Checked directly:

```sh
rg -n 'trust_state|scope_enforced' docs/systems/mindcache/index.html
# no output
```

MindCache earns two marks and a reader on its page cannot see either. The
rubric is one nav click away on every page — `templates/document.html:62` — and
nothing on the page says which of its definitions this system met.

So the reviewer's complaint is right and their explanation is inverted. The
rubric is not a black box; it is a page most readers have no reason to open,
because the page they are on never raises the question.

## Why this matters more than it sounds

The marks are the atlas's only structured verdict. Everything else on a report
page is prose, and prose is where the near-misses live — *"`trust_state` is
withheld even though the codebase is full of statuses"* is a sentence a reader
finds only by reading section 2 of
[Acontext](../content/systems/acontext.md). The mark is the part a reader can
scan, compare and act on, and it is the part the page omits.

There is a second cost, specific to how this atlas argues. The rubric is strict
on purpose, and the value of a withheld mark comes from the reader knowing it was
*considered*. `capabilities: ""` means "assessed, carries none" — a real answer,
and the common one. On the rendered page that is indistinguishable from "nobody
looked", which is exactly the distinction
[the rubric](../content/methodology/atlas-rubric.md) exists to protect.

## Proposal

**Render the seven marks in the report header, each linking to its definition,
showing earned and withheld distinctly.** Something like:

```text
tombstone · trust_state · bitemporal · scope_enforced · audit_log · human_review · negative_eval
              ^earned                    ^earned
```

with the earned ones filled, the rest struck or greyed, and every one of them an
anchor into `methodology/atlas-rubric/#<mark>`. Three properties are worth
building in deliberately:

1. **Show all seven, not only the earned ones.** A row of two pills says what
   this system has; a row of seven with two filled says what it was measured
   against, which is the more honest artifact and the one that makes an empty row
   meaningful.
2. **Link each mark to its own definition, not to the rubric page.** The rubric
   is long. A reader who wants to know what `bitemporal` required should land on
   the paragraph, which means the rubric needs stable per-mark anchors — a small
   content change that also lets reports link a mark from prose.
3. **Generate it from the same frontmatter the index reads.** No second source of
   truth, and `check_claim_counts.py` keeps working unchanged.

Cost: one template block, one build-script pass, and anchors in the rubric.
No new dependency, and it degrades correctly for a reader without JavaScript —
which, per
[the fourth review](2026-08-13-the-fourth-review-and-the-second-broken-diagram.md),
is not a hypothetical reader.

## What this does not fix

It does not make the near-miss visible. "Almost has a tombstone" is the most
useful sentence in several reports and it will still be prose. A pill row that
said *withheld — see §7* would be better and is a bigger change: it needs a
per-mark reason in frontmatter, which is a schema change and a writing burden on
every future report. Worth considering separately, and worth not bundling into a
one-template fix.

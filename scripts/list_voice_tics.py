#!/usr/bin/env python3
"""Count phrases that stand in for a point, and unlinked references to the corpus.

Two kinds, one ratchet.

**Throat-clearing.** In "it is worth naming that X", X is the sentence. *worth
naming*, *worth noting*, *worth reading*, *worth knowing* and *genuinely* carried
roughly 980 uses across the reports on 2026-09-25. Each announces significance
instead of stating the consequence that would carry it.

**A reference the reader cannot follow.** "The same ruling this atlas applied to
a declared approve tool elsewhere" names a specific page and then takes the name
out. On 2026-09-25, 280 of 281 uses of *elsewhere* in the reports had no link
within 60 characters. Counted here only when the sentence holding it has no
Markdown link.

A quotation is the subject's words and is not counted, for the reason
`list_superlatives.py` gives: the edit a ratchet invites for a false positive is
to alter the quotation, which is worse than the miscount.

Same shape as the superlatives ceiling: the total may fall and may not rise.
The hole it does not close: one phrase can be removed and another added.

Usage: list_voice_tics.py <project-dir>
       list_voice_tics.py --check <project-dir>
       list_voice_tics.py --self-test
"""
import re
import sys
from pathlib import Path

from list_superlatives import _quoted_spans

TIC = re.compile(r"\bworth (?:naming|noting|reading|knowing)\b|\bgenuinely\b", re.I)
ELSEWHERE = re.compile(r"\belsewhere\b", re.I)
LINK = re.compile(r"\]\(")
SENTENCE = re.compile(r"[^.!?\n]*(?:[.!?]|$)")

#: Set to 1484 on 2026-09-25, across all of content/. Lower it as phrases are
#: cut; never raise it to admit a new one.
TIC_CEILING = 1484


def hits(text: str) -> list[tuple[int, str]]:
    spans = _quoted_spans(text)
    quoted = lambda i: any(lo <= i < hi for lo, hi in spans)
    out = [(m.start(), m.group(0)) for m in TIC.finditer(text) if not quoted(m.start())]
    flat = text.replace("\n", " ")
    for s in SENTENCE.finditer(flat):
        if LINK.search(s.group(0)):
            continue
        for m in ELSEWHERE.finditer(s.group(0)):
            at = s.start() + m.start()
            if not quoted(at):
                out.append((at, "elsewhere (unlinked)"))
    return out


def collect(root: str) -> list[tuple[str, str]]:
    content = Path(root) / "content"
    rows = []
    for path in sorted(content.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for at, phrase in hits(text):
            rows.append((f"{path.relative_to(content)}:{text.count(chr(10), 0, at) + 1}", phrase))
    return rows


def self_test() -> int:
    cases = [
        ("a tic counts", "It is worth noting that the log is sealed.", 1),
        ("genuinely counts", "The split is genuinely useful.", 1),
        ("a quoted tic does not", 'The README says "worth reading twice".', 0),
        ("unlinked elsewhere counts", "The same ruling applied elsewhere.", 1),
        ("linked elsewhere does not",
         "The same ruling applied elsewhere, in [Vestige](../vestige/).", 0),
        ("a link in the next sentence does not excuse",
         "It was ruled elsewhere. See [Vestige](../vestige/).", 1),
    ]
    for name, text, expected in cases:
        if len(hits(text)) != expected:
            print(f"self-test failed: {name}: got {len(hits(text))}", file=sys.stderr)
            return 1
    print(f"self-test: {len(cases)} controls passed")
    return 0


def main(args: list[str]) -> int:
    root = next((a for a in args if not a.startswith("--")), ".")
    if "--self-test" in args:
        return self_test()
    rows = collect(root)
    if "--check" in args:
        if len(rows) > TIC_CEILING:
            print(f"voice tics rose to {len(rows)} > {TIC_CEILING}. State the "
                  "consequence instead of the intensifier, and link or cut "
                  "'elsewhere'; do not raise the ceiling.", file=sys.stderr)
            return 1
        print(f"{len(rows)} voice tics (ceiling {TIC_CEILING}).")
        return 0
    print(f"{len(rows)} voice tics\n")
    for location, phrase in rows:
        print(f"  {location:<44} {phrase}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

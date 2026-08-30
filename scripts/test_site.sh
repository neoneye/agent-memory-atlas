#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
site_dir="$project_dir/docs"

required=(
  "$site_dir/index.html"
  "$site_dir/compare/index.html"
  "$site_dir/benchmarks/index.html"
  "$site_dir/build/index.html"
  "$site_dir/tensions/index.html"
  "$site_dir/capabilities/index.html"
  "$site_dir/patterns/index.html"
  "$site_dir/patterns/rejected-value-tombstone/index.html"
  "$site_dir/patterns/bi-temporal-fact-validity/index.html"
  "$site_dir/patterns/decay-and-reinforcement/index.html"
  "$site_dir/patterns/zero-llm-capture/index.html"
  "$site_dir/assets/main.css"
  "$site_dir/assets/main.js"
  "$site_dir/discord.html"
)

for path in "${required[@]}"; do
  if [[ ! -s "$path" ]]; then
    echo "Missing required site file: $path" >&2
    exit 1
  fi
done

# This suite validates the *rendered* site in docs/, which is a committed build
# rather than a fresh one — so an edit to content/ that has not been rebuilt is
# checked against the previous build's HTML. That is not a theoretical gap: on
# 2026-08-08 a fragment link to an id that does not exist passed a full run and
# failed the next one, because the run that should have caught it read HTML
# written before the link was added. A green suite over stale output is the
# lying-operation failure this atlas names in other people's code.
stale="$(find "$project_dir/content" "$project_dir/templates" -type f \
  -newer "$site_dir/index.html" -print -quit 2>/dev/null || true)"
if [[ -n "$stale" ]]; then
  echo "docs/ is older than $stale — run 'npm run build' before 'npm test'." >&2
  exit 1
fi

expected_systems="$(find "$project_dir/content/systems" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"
expected_patterns="$(find "$project_dir/content/patterns" -maxdepth 1 -name '*.md' ! -name 'index.md' | wc -l | tr -d ' ')"

if [[ "$expected_systems" == "0" || "$expected_patterns" == "0" ]]; then
  echo "Could not derive expected counts from content/ (systems=$expected_systems, patterns=$expected_patterns)." >&2
  exit 1
fi

# Redirect stubs left behind by a renamed project (site/redirects/*.html) also
# land under systems/<slug>/index.html and are not reports. They carry
# data-redirect-stub so this count stays "one rendered report per content file".
system_count="$(find "$site_dir/systems" -mindepth 2 -maxdepth 2 -name index.html -exec grep -L 'data-redirect-stub' {} + | wc -l | tr -d ' ')"
if [[ "$system_count" != "$expected_systems" ]]; then
  echo "Expected $expected_systems rendered system reports, found $system_count" >&2
  exit 1
fi

revision_count="$(grep -Rho 'Analyzed revision' "$site_dir/systems" | wc -l | tr -d ' ')"
if [[ "$revision_count" != "$expected_systems" ]]; then
  echo "Expected revision metadata on all $expected_systems reports, found $revision_count" >&2
  exit 1
fi

# The check above proves a report carries a pin; it does not prove the pin
# agrees with the repositories-inspected list overview.md publishes. A
# re-review updates frontmatter in one file and that list is a hand edit in
# another, so the two drift apart silently — three entries had, all of them on
# re-reviewed systems, and every existing check stayed green.
if ! python3 "$project_dir/scripts/check_inspected_pins.py" "$project_dir"; then
  exit 1
fi

# Re-review narration used to be written into whatever paragraph it contradicted
# and into two unrelated lists in overview.md. It now goes in one place per
# report. This asserts the newest History entry is the reading the report is
# pinned to, so a re-pin cannot ship without recording one.
if ! python3 "$project_dir/scripts/check_history.py" "$project_dir"; then
  exit 1
fi

# Section 9's 140 per-system anchors moved to /verdicts/ on 4 August 2026 and a
# fragment never reaches the server, so external /compare/#<slug> links are
# caught client-side. That only works while the slug exists on the new page.
if ! python3 "$project_dir/scripts/check_verdict_anchors.py" "$project_dir"; then
  exit 1
fi

# check_verdict_anchors.py proves the slug resolves; nothing proved the entry
# under it still describes the report. A re-analysis updates the report, the
# overview, the homepage card and the bound counts, and the verdicts entry was
# on none of those checklists — four were stale on 2026-08-30, one of them
# arguing against a mark the report awards.
if ! python3 "$project_dir/scripts/check_verdict_marks.py" --self-test; then
  echo "check_verdict_marks.py cannot demonstrate that it still fails." >&2
  exit 1
fi
if ! python3 "$project_dir/scripts/check_verdict_marks.py" "$project_dir"; then
  exit 1
fi

# check_anchors.py follows fragments and stops there, so a relative href that
# points at nothing has never been checked. Thirty were broken when this was
# written — mostly sibling reports written `./verel/` from inside
# `systems/memary/`, which resolves one level too deep — plus a pattern page
# linking `../../overview/` at a page that renders to `/compare/`. Every one of
# them was a reader clicking through to inspect a claim and landing on a 404.
if ! python3 - "$site_dir" <<'PY'
import re, sys
from pathlib import Path

site = Path(sys.argv[1])
broken = []
for page in sorted(site.rglob("*.html")):
    html = page.read_text(encoding="utf-8")
    for href in sorted(set(re.findall(r'href="([^"#:]+)(?:#[^"]*)?"', html))):
        # Absolute and off-site links are somebody else's problem; `href="/"`
        # has its own check below.
        if not href or href.startswith(("http", "//", "mailto", "/")):
            continue
        target = (page.parent / href).resolve()
        if not (target.is_file() or (target / "index.html").is_file()):
            broken.append(f"{page.relative_to(site)} -> {href}")

if broken:
    print("\n".join(broken), file=sys.stderr)
    print(f"{len(broken)} relative links point at nothing.", file=sys.stderr)
    raise SystemExit(1)
print("every relative link in the site resolves.")
PY
then
  exit 1
fi

# Every verdict heading links to that system's report, so a reader weighing an
# entry can open the evidence behind it. Two ways for that to rot silently: a
# heading added without the link, and a link whose target moved. The check above
# proves a heading's target exists; this proves the heading has one at all.
if ! python3 - "$site_dir" <<'PY'
import re, sys
from pathlib import Path

page = Path(sys.argv[1]) / "verdicts" / "index.html"
html = page.read_text(encoding="utf-8")
headings = re.findall(r'<h3 id="([^"]+)">(.*?)</h3>', html, re.S)
problems = []
for slug, inner in headings:
    match = re.match(r'\s*<a\s+href="([^"]+)"', inner, re.S)
    if not match:
        problems.append(f"verdict heading '{slug}' is not a link to its report")
        continue
    target = (page.parent / match.group(1) / "index.html").resolve()
    if not target.is_file():
        problems.append(f"verdict heading '{slug}' links to {match.group(1)}, which does not exist")

if problems:
    print("\n".join(problems), file=sys.stderr)
    raise SystemExit(1)
print(f"{len(headings)} verdict headings link to a report that exists.")
PY
then
  exit 1
fi

# --check does more than compare the generated tables: it also validates matrix
# values, capability flags, and revision pins. Discarding its stderr and printing
# one hardcoded message reported every one of those as a stale matrix and told
# the reader to run a build that would not fix it. Show what the script actually
# said, and only then suggest the regenerate.
if ! check_output="$(python3 "$project_dir/scripts/generate_matrix.py" --check 2>&1)"; then
  echo "$check_output" >&2
  echo "If the above is a drift between the generated tables and the frontmatter," >&2
  echo "run 'npm run build' to regenerate them." >&2
  exit 1
fi

matrix_rows="$(grep -c '^| `' "$project_dir/content/overview.md" | tr -d ' ')"
if [[ "$matrix_rows" != "$expected_systems" ]]; then
  echo "Expected $expected_systems matrix rows, found $matrix_rows" >&2
  exit 1
fi

# The homepage is hand-written while the reports are not, so its cards and
# statistics drift silently as systems are added.
if ! python3 "$project_dir/scripts/check_homepage.py" "$project_dir"; then
  echo "Homepage is out of step with content/systems." >&2
  exit 1
fi

# check_homepage.py guards the denominator, which a file count derives. The
# numerators are the atlas's headline findings and nothing guarded them: four
# were found stale in one page on 2026-08-06, each sitting beside generated
# numbers that were correct. --self-test runs a positive and a negative control
# first, because a checker that can no longer fail is worse than no checker.
if ! python3 "$project_dir/scripts/check_claim_counts.py" --self-test; then
  echo "check_claim_counts.py cannot demonstrate that it still fails." >&2
  exit 1
fi
if ! python3 "$project_dir/scripts/check_claim_counts.py" "$project_dir"; then
  echo "A mechanism count in content/ disagrees with the report frontmatter." >&2
  exit 1
fi

# Both checks above guard the *count* of marks. Neither says what a mark points
# at, and a mark that names no subsystem is how three correct marks add up to a
# profile no memory path in the system has. The evidence block is the fix and it
# is being filled report by report, so this ratchets rather than gates.
if ! python3 "$project_dir/scripts/check_capability_evidence.py" --self-test; then
  echo "check_capability_evidence.py cannot demonstrate that it still fails." >&2
  exit 1
fi
if ! python3 "$project_dir/scripts/check_capability_evidence.py" "$project_dir"; then
  echo "Capability evidence is malformed, or coverage fell below the floor." >&2
  exit 1
fi

# YAML keeps the last of a duplicate key and drops the first without failing, so
# a second `capability_evidence:` or `matrix:` block loses the one above it with
# nothing in the rendered page to say so. Pandoc downgrades that to a warning.
if ! python3 "$project_dir/scripts/check_frontmatter_keys.py" --self-test; then
  echo "check_frontmatter_keys.py cannot demonstrate that it still fails." >&2
  exit 1
fi
if ! python3 "$project_dir/scripts/check_frontmatter_keys.py" "$project_dir"; then
  echo "A frontmatter block declares the same key twice." >&2
  exit 1
fi

# A screening record certifies one revision. Nothing compared the recorded
# revision to the report's pin, so a re-pinned report kept the record from its
# previous commit and the summary counted it as screened. Absent records are a
# backlog and never fail; records claiming to be screened at a revision the
# report has moved off are the defect, and they ratchet down.
if ! python3 "$project_dir/scripts/check_screening_ledger.py" "$project_dir"; then
  echo "Screening records certify revisions the reports no longer pin." >&2
  exit 1
fi

# The storage census is only worth publishing if a seeded guess cannot quietly
# become indistinguishable from a reviewed judgement. --check enforces the
# vocabulary, that every report declares the keys, that the seeded count never
# rises, and that the rendered table matches the frontmatter it claims to sum.
if ! python3 "$project_dir/scripts/extract_stack.py" --self-test; then
  echo "extract_stack.py cannot demonstrate that its seeding rules still hold." >&2
  exit 1
fi
if ! python3 "$project_dir/scripts/extract_stack.py" "$project_dir" --check; then
  echo "The stack census is stale, malformed, or lost reviewed coverage." >&2
  exit 1
fi

# The protocol catalogue claims each test "carries the page it came from, so a
# test whose source argument changes goes stale visibly rather than quietly".
# Nothing made that true until this check existed, and an outside review said so.
if ! python3 "$project_dir/scripts/check_protocol.py" --self-test; then
  echo "check_protocol.py cannot demonstrate that it still fails." >&2
  exit 1
fi
if ! python3 "$project_dir/scripts/check_protocol.py" "$project_dir"; then
  echo "The agent protocol disagrees with the pages it cites." >&2
  exit 1
fi

# Every pattern page states its epistemic status in its header, and the patterns
# index states the same classification in prose. Two copies of one claim drift,
# and drifting *this* claim relabels an argument as a consensus.
if ! python3 "$project_dir/scripts/check_pattern_stance.py" --self-test; then
  echo "check_pattern_stance.py cannot demonstrate that it still fails." >&2
  exit 1
fi
if ! python3 "$project_dir/scripts/check_pattern_stance.py" "$project_dir"; then
  echo "A pattern's stance pill contradicts the patterns index." >&2
  exit 1
fi

# build_site.sh wraps every <table> in .table-wrap. A hand-authored wrapper in
# content/ nests them, and each wrapper grows its own "expand to full width"
# toggle — which is how the capability grid ended up with two.
nested_wraps="$(python3 - "$site_dir" <<'PYWRAP'
import glob, os, sys

site = sys.argv[1]
bad = []
for page in glob.glob(os.path.join(site, "**", "index.html"), recursive=True):
    html = open(page, encoding="utf-8").read()
    wraps = html.count('class="table-wrap')
    tables = html.count("<table")
    if wraps > tables:
        bad.append(f"{os.path.relpath(page, site)}: {wraps} table-wrap for {tables} tables")
print("\n".join(bad))
PYWRAP
)"
if [[ -n "$nested_wraps" ]]; then
  echo "Nested .table-wrap (each one adds another expand toggle):" >&2
  echo "$nested_wraps" >&2
  exit 1
fi

# The homepage and the generated pages carry separate hand-maintained <head>
# blocks whose comments say they must be kept in step. Consent Mode lives in
# there, so drift means some pages honour the reader's cookie choice and others
# do not — invisible on every page either way.
if ! python3 "$project_dir/scripts/check_heads.py" "$project_dir"; then
  exit 1
fi

# A mermaid diagram that fails to parse renders as "Syntax error in text" on the
# published page and is invisible to every other check here — the markdown is
# valid, the HTML is valid, and only the browser knows. Reported from the live
# site once already.
if ! python3 "$project_dir/scripts/check_mermaid.py" "$project_dir/content"; then
  exit 1
fi

# The diagrams render client-side, so an unrendered page delivers their source.
# Two outside reviews read that source as broken page layout and opened with it,
# which makes the wrapper a delivery guarantee rather than a nicety: every
# diagram ships inside a captioned figure, and the written-caption count only
# rises.
if ! python3 "$project_dir/scripts/check_diagram_captions.py"; then
  exit 1
fi

# A cited paper the reader has to retype an identifier to find is a dead end, and
# the atlas cites papers constantly. Every arXiv mention in content/ and notes/
# must be a link.
if ! python3 "$project_dir/scripts/check_arxiv_links.py" "$project_dir"; then
  exit 1
fi

# Heading ids are generated from heading text, so a numbered section changes its
# anchor whenever sections are renumbered. Catch fragment links that no longer land.
broken_anchors="$(python3 "$project_dir/scripts/check_anchors.py" "$site_dir")"
if [[ -n "$broken_anchors" ]]; then
  echo "Fragment links pointing at ids that do not exist:" >&2
  echo "$broken_anchors" >&2
  exit 1
fi

# Pandoc decides loose-vs-tight per LIST, not per item: one bullet containing
# blank-line-separated paragraphs wraps EVERY sibling `<li>` in `<p>`, and
# `.prose p` then adds a 19px bottom margin to all of them. On 2026-08-08 a
# single expanded bullet did that to all 93 Known Limitations items — a
# site-wide spacing change and most of a 6,000-line HTML diff, invisible to
# every other check here because the markdown and the HTML are both valid.
# Long prose belongs in a subsection, not inside a list item.
#
# Ratcheted rather than absolute, because four lists were already loose when this
# check was written — 45 items on the comparative report, 15 on Verel, 13 and 12
# on Core Memory. Those are recorded rather than exempted; the floor is the
# number that may not grow, and lowering it is a deliberate edit with a diff.
if ! python3 - "$site_dir" <<'PY'
import re, sys
from pathlib import Path

BASELINE = 0  # loose lists of 10+ items. This may only go down.

found = []
for page in sorted(Path(sys.argv[1]).rglob("index.html")):
    html = page.read_text(encoding="utf-8")
    for match in re.finditer(r"<ul>.*?</ul>", html, re.S):
        block = match.group(0)
        items = block.count("<li>")
        loose = len(re.findall(r"<li>\s*<p>", block))
        if items >= 10 and loose:
            found.append(f"{page}: a {items}-item list is loose ({loose} items wrapped in <p>)")

if len(found) > BASELINE:
    print("\n".join(found), file=sys.stderr)
    print(
        f"{len(found)} loose lists of 10+ items; the baseline is {BASELINE}. "
        "A list item holding blank-line-separated paragraphs makes every sibling "
        "item loose — move the prose into a subsection.",
        file=sys.stderr,
    )
    raise SystemExit(1)
print(f"{len(found)} loose lists of 10+ items (baseline {BASELINE}).")
if len(found) < BASELINE:
    print(f"BASELINE can be lowered to {len(found)}.")
PY
then
  exit 1
fi

# A markdown link missing its closing paren does not become a broken link — it
# stops being a link at all, and pandoc renders the whole run as literal text.
# check_anchors.py validates the links that exist and structurally cannot see
# this one, which is how `[`qwen-mm-plugins`](../systems/qwen-mm-plugins/, [...`
# sat on the comparative report until a reader reported it.
#
# The rendered page is the right place to look: after a successful parse, `](`
# survives only inside code, so anywhere else it is an unparsed link.
if ! python3 - "$site_dir" <<'PYLINK'
import html as h
import re
import sys
from pathlib import Path

found = []
for page in sorted(Path(sys.argv[1]).rglob("*.html")):
    text = page.read_text(encoding="utf-8")
    # A markdown example inside code or pre is legitimate and stays.
    text = re.sub(r"<(pre|code)\b.*?</\1>", "", text, flags=re.S)
    for match in re.finditer(r"\]\(", text):
        context = h.unescape(text[max(0, match.start() - 70):match.start() + 70])
        found.append(f"{page}: unparsed link -- {' '.join(context.split())}")

if found:
    print("\n".join(found), file=sys.stderr)
    print(
        f"{len(found)} markdown link(s) rendered as literal text. A missing "
        "closing paren stops a link being a link, so the anchor check never "
        "sees it.",
        file=sys.stderr,
    )
    raise SystemExit(1)
print("no markdown link rendered as literal text.")
PYLINK
then
  exit 1
fi

# The JSON-LD block interpolates the page's own title and description, and a
# description containing a double quote produced a block that did not parse —
# invisible on the page, because a browser ignores an unparseable ld+json and
# renders exactly the same. The values are escaped in build_site.sh; this checks
# the result rather than trusting the escaping.
if ! python3 - "$site_dir" <<'PYLD'
import json
import re
import sys
from pathlib import Path

bad = []
checked = 0
for page in sorted(Path(sys.argv[1]).rglob("index.html")):
    text = page.read_text(encoding="utf-8")
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
        checked += 1
        try:
            json.loads(block)
        except ValueError as error:
            bad.append(f"{page}: {error}")

if bad:
    print("\n".join(bad), file=sys.stderr)
    print(
        f"{len(bad)} JSON-LD block(s) do not parse. A browser ignores these "
        "silently, so nothing on the page looks wrong.",
        file=sys.stderr,
    )
    raise SystemExit(1)
print(f"{checked} JSON-LD blocks parse.")
PYLD
then
  exit 1
fi

missing_dates="$(grep -RLs '^analyzed_at:' "$project_dir/content/systems" --include='*.md' || true)"
if [[ -n "$missing_dates" ]]; then
  echo "System reports missing analyzed_at frontmatter:" >&2
  echo "$missing_dates" >&2
  exit 1
fi

analyzed_count="$(grep -Rho 'Analyzed on' "$site_dir/systems" | wc -l | tr -d ' ')"
if [[ "$analyzed_count" != "$expected_systems" ]]; then
  echo "Expected analyzed-on dates on all $expected_systems reports, found $analyzed_count" >&2
  exit 1
fi

pattern_count="$(find "$site_dir/patterns" -mindepth 2 -maxdepth 2 -name index.html | wc -l | tr -d ' ')"
if [[ "$pattern_count" != "$expected_patterns" ]]; then
  echo "Expected $expected_patterns rendered design patterns, found $pattern_count" >&2
  exit 1
fi

# The Discord redirect repeats the invite URL four times — canonical, robots-free
# meta refresh, script, and the visible fallback link. Rotating the invite by
# editing three of the four leaves a page that sends most readers to a dead
# invite and looks correct in the browser that honours the one that was updated.
discord_urls="$(grep -o 'https://discord\.gg/[A-Za-z0-9]*' "$site_dir/discord.html" | sort -u)"
if [[ "$(printf '%s\n' "$discord_urls" | wc -l | tr -d ' ')" != "1" ]]; then
  echo "site/discord.html points at more than one invite:" >&2
  echo "$discord_urls" >&2
  exit 1
fi
if [[ "$(grep -c 'https://discord\.gg/' "$site_dir/discord.html" | tr -d ' ')" != "4" ]]; then
  echo "site/discord.html should carry the invite in all four places (canonical," >&2
  echo "meta refresh, script, fallback link); one of them is missing." >&2
  exit 1
fi

if ! grep -q 'href="./patterns/"' "$site_dir/index.html"; then
  echo "Homepage does not link to the pattern library." >&2
  exit 1
fi

if ! grep -q 'sticky-table-head' "$site_dir/assets/main.js" ||
   ! grep -q 'sticky-table-head' "$site_dir/assets/main.css"; then
  echo "Sticky table-header behavior is missing from the generated assets." >&2
  exit 1
fi

if grep -Rqs 'href="<a' "$site_dir/systems" --include='*.html'; then
  echo "Malformed nested source links found in rendered system reports." >&2
  exit 1
fi

if grep -Rqs 'href="/' "$site_dir" --include='*.html'; then
  echo "Root-relative links found; these break under the GitHub Pages project path." >&2
  exit 1
fi

# Generated files that are one `git add -A` away from being committed: Python
# bytecode from the scripts importing each other, and scratch pages written into
# the built site so a local server can reach them. A .pyc reached main twice
# before .gitignore covered it, so the ignore rule alone is not the guard.
if git -C "$project_dir" rev-parse --git-dir >/dev/null 2>&1; then
  tracked_junk="$(git -C "$project_dir" ls-files | grep -E '(^|/)__pycache__/|\.pyc$|^docs/_' || true)"
  if [[ -n "$tracked_junk" ]]; then
    echo "Build artifacts are tracked in git:" >&2
    echo "$tracked_junk" >&2
    echo "Run 'git rm --cached <path>' — .gitignore does not untrack what is already committed." >&2
    exit 1
  fi
fi

# Reports are pinned and stamped with analyzed_at, so a duration measured from
# "now" is both redundant and perishable — "dormant for two and a half years" is
# wrong a few months after it is written. See the report format's date rule.
# The methodology page and the OpenWorker report quote these phrasings on
# purpose, so they are exempt.
# Deliberately narrow: only durations attached to a project's *activity* state,
# plus two fixed phrasings. A check that fires on illustrative prose — "a claim
# verified two years ago from one verified today" — gets switched off, so it is
# scoped to the sentences that actually rot. Lines quoting the rule are exempt.
stale_dates="$(
  grep -rniE "(dormant|stale|inactive|unmaintained|abandoned|untouched|quiet|no commits?|last commits?|not been (updated|touched)) [^.]{0,40}(for|in) (the )?(past |last )?(a |an )?(one|two|three|four|five|six|seven|eight|nine|ten|half|[0-9]+)[ a-z-]*(year|month|week)s?|the day of review|\byesterday\b" \
    "$project_dir/content/systems" "$project_dir/content/overview.md" 2>/dev/null \
    | grep -v "absolute dates" || true
)"
if [[ -n "$stale_dates" ]]; then
  echo "Relative date references found — use an absolute date or 'at this commit':" >&2
  echo "$stale_dates" >&2
  exit 1
fi

# The homepage card numbers are a reading order, and cards have historically been
# prepended as well as appended — which left 46 through 63 running backwards in
# the DOM without anything noticing. Assert the labels ascend contiguously from 1.
card_order="$(python3 - "$project_dir/site/index.html" <<'PY'
import re, sys
html = open(sys.argv[1]).read()
nums = [int(n) for n in re.findall(r'<div class="system-card-top"><span>[^<]*</span><code>(\d+)</code>', html)]
if nums != list(range(1, len(nums) + 1)):
    bad = [f"{a}->{b}" for a, b in zip(nums, nums[1:]) if b != a + 1]
    print(f"homepage card numbers are not 1..{len(nums)} in DOM order; breaks at: {', '.join(bad[:8])}")
PY
)"
if [[ -n "$card_order" ]]; then
  echo "$card_order" >&2
  echo "Reorder the <article class=\"system-card\"> blocks so their numbers ascend." >&2
  exit 1
fi

echo "Validated $system_count reports, $pattern_count design patterns, card ordering, revision metadata, inspected-list pins, history sections, verdict anchors, analyzed-on dates, and project-relative navigation."

#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
site_dir="$project_dir/docs"

required=(
  "$site_dir/index.html"
  "$site_dir/compare/index.html"
  "$site_dir/benchmarks/index.html"
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

# Heading ids are generated from heading text, so a numbered section changes its
# anchor whenever sections are renumbered. Catch fragment links that no longer land.
broken_anchors="$(python3 "$project_dir/scripts/check_anchors.py" "$site_dir")"
if [[ -n "$broken_anchors" ]]; then
  echo "Fragment links pointing at ids that do not exist:" >&2
  echo "$broken_anchors" >&2
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

echo "Validated $system_count reports, $pattern_count design patterns, card ordering, revision metadata, analyzed-on dates, and project-relative navigation."

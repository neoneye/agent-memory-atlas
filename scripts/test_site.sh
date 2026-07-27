#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
site_dir="$project_dir/docs"

required=(
  "$site_dir/index.html"
  "$site_dir/compare/index.html"
  "$site_dir/patterns/index.html"
  "$site_dir/patterns/rejected-value-tombstone/index.html"
  "$site_dir/patterns/bi-temporal-fact-validity/index.html"
  "$site_dir/patterns/decay-and-reinforcement/index.html"
  "$site_dir/patterns/zero-llm-capture/index.html"
  "$site_dir/assets/main.css"
  "$site_dir/assets/main.js"
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

system_count="$(find "$site_dir/systems" -mindepth 2 -maxdepth 2 -name index.html | wc -l | tr -d ' ')"
if [[ "$system_count" != "$expected_systems" ]]; then
  echo "Expected $expected_systems rendered system reports, found $system_count" >&2
  exit 1
fi

revision_count="$(grep -Rho 'Analyzed revision' "$site_dir/systems" | wc -l | tr -d ' ')"
if [[ "$revision_count" != "$expected_systems" ]]; then
  echo "Expected revision metadata on all $expected_systems reports, found $revision_count" >&2
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

echo "Validated $system_count reports, $pattern_count design patterns, revision metadata, analyzed-on dates, and project-relative navigation."

#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
site_dir="$project_dir/docs"

required=(
  "$site_dir/index.html"
  "$site_dir/compare/index.html"
  "$site_dir/patterns/index.html"
  "$site_dir/patterns/rejected-value-tombstone/index.html"
  "$site_dir/assets/main.css"
  "$site_dir/assets/main.js"
)

for path in "${required[@]}"; do
  if [[ ! -s "$path" ]]; then
    echo "Missing required site file: $path" >&2
    exit 1
  fi
done

system_count="$(find "$site_dir/systems" -mindepth 2 -maxdepth 2 -name index.html | wc -l | tr -d ' ')"
if [[ "$system_count" != "11" ]]; then
  echo "Expected 11 rendered system reports, found $system_count" >&2
  exit 1
fi

revision_count="$(grep -Rho 'Analyzed revision' "$site_dir/systems" | wc -l | tr -d ' ')"
if [[ "$revision_count" != "11" ]]; then
  echo "Expected revision metadata on all 11 reports, found $revision_count" >&2
  exit 1
fi

pattern_count="$(find "$site_dir/patterns" -mindepth 2 -maxdepth 2 -name index.html | wc -l | tr -d ' ')"
if [[ "$pattern_count" != "10" ]]; then
  echo "Expected 10 rendered design patterns, found $pattern_count" >&2
  exit 1
fi

if ! grep -q 'href="./patterns/"' "$site_dir/index.html"; then
  echo "Homepage does not link to the pattern library." >&2
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

echo "Validated 11 reports, 10 design patterns, revision metadata, and project-relative navigation."

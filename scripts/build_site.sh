#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="$project_dir/docs"
template="$project_dir/templates/document.html"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "Pandoc is required to build the atlas." >&2
  exit 1
fi

# The comparative matrix is derived from each report's frontmatter, so adding a
# system never means editing a forty-row table by hand.
python3 "$project_dir/scripts/generate_matrix.py"

rm -rf "$output_dir"
mkdir -p "$output_dir/assets" "$output_dir/compare" "$output_dir/benchmarks" "$output_dir/systems" "$output_dir/patterns" "$output_dir/methodology"

cp "$project_dir/site/index.html" "$output_dir/index.html"
cp -R "$project_dir/assets/." "$output_dir/assets/"
touch "$output_dir/.nojekyll"

render_document() {
  local input="$1"
  local destination="$2"
  local source_href
  local revision_href
  local analyzed_at

  source_href="$(sed -n 's/^source_url:[[:space:]]*//p' "$input" | head -n 1)"
  revision_href="$(sed -n 's/^revision_url:[[:space:]]*//p' "$input" | head -n 1)"
  analyzed_at="$(sed -n 's/^analyzed_at:[[:space:]]*//p' "$input" | head -n 1)"
  source_href="${source_href#\"}"
  source_href="${source_href%\"}"
  revision_href="${revision_href#\"}"
  revision_href="${revision_href%\"}"
  analyzed_at="${analyzed_at#\"}"
  analyzed_at="${analyzed_at%\"}"

  local capability_strip=""
  if [[ "$input" == *"/content/systems/"* ]]; then
    capability_strip="$(python3 "$project_dir/scripts/capability_strip.py" "$input")"
  fi

  mkdir -p "$(dirname "$destination")"
  pandoc "$input" \
    --from=gfm \
    --to=html5 \
    --standalone \
    --syntax-highlighting=none \
    --template="$template" \
    --variable="source_href:$source_href" \
    --variable="revision_href:$revision_href" \
    --variable="analyzed_at_text:$analyzed_at" \
    --variable="capability_strip:$capability_strip" \
    --output="$destination"
}

render_document "$project_dir/content/overview.md" "$output_dir/compare/index.html"
render_document "$project_dir/content/patterns/index.md" "$output_dir/patterns/index.html"
render_document "$project_dir/content/benchmarks.md" "$output_dir/benchmarks/index.html"

for input in "$project_dir"/content/systems/*.md; do
  slug="$(basename "$input" .md)"
  render_document "$input" "$output_dir/systems/$slug/index.html"
done

for input in "$project_dir"/content/patterns/*.md; do
  slug="$(basename "$input" .md)"
  if [[ "$slug" == "index" ]]; then
    continue
  fi
  render_document "$input" "$output_dir/patterns/$slug/index.html"
done

for input in "$project_dir"/content/methodology/*.md; do
  slug="$(basename "$input" .md)"
  render_document "$input" "$output_dir/methodology/$slug/index.html"
done

# Tables are intentionally wide. Wrap them so small screens scroll within the
# table instead of forcing the entire page wider than the viewport.
while IFS= read -r -d '' page; do
  perl -0pi -e 's{(<table\b.*?</table>)}{<div class="table-wrap">$1</div>}gs' "$page"
done < <(find "$output_dir" -name "index.html" -print0)

echo "Built Agent Memory Atlas into $output_dir"

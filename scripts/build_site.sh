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

# The A–Z index is generated from the same frontmatter, so a report cannot exist
# without appearing in it. See scripts/generate_index.py for why the page exists.
python3 "$project_dir/scripts/generate_index.py"

rm -rf "$output_dir"
mkdir -p "$output_dir/assets" "$output_dir/a-z" "$output_dir/compare" "$output_dir/benchmarks" "$output_dir/capabilities" "$output_dir/systems" "$output_dir/patterns" "$output_dir/methodology"

cp "$project_dir/site/index.html" "$output_dir/index.html"
# /discord.html is a redirect in front of the Discord invite, so the invite code
# lives in one file rather than in every place it has been shared.
cp "$project_dir/site/discord.html" "$output_dir/discord.html"
cp -R "$project_dir/assets/." "$output_dir/assets/"
touch "$output_dir/.nojekyll"

render_document() {
  local input="$1"
  local destination="$2"
  local source_href
  local revision_href
  local revision_short
  local analyzed_at

  source_href="$(sed -n 's/^source_url:[[:space:]]*//p' "$input" | head -n 1)"
  revision_href="$(sed -n 's/^revision_url:[[:space:]]*//p' "$input" | head -n 1)"
  analyzed_at="$(sed -n 's/^analyzed_at:[[:space:]]*//p' "$input" | head -n 1)"
  # Reports pin a full 40-character commit id, because a short one is only
  # unique until the repository grows into the collision. Forty characters of
  # hex in a header pill is noise, so the pill shows the first eight and the
  # full id stays in the link and the tooltip.
  revision_short="$(sed -n 's/^revision:[[:space:]]*//p' "$input" | head -n 1)"
  revision_short="${revision_short//\"/}"
  if [[ ${#revision_short} -gt 8 ]]; then
    revision_short="${revision_short:0:8}…"
  fi
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
    --variable="revision_short:$revision_short" \
    --variable="analyzed_at_text:$analyzed_at" \
    --variable="capability_strip:$capability_strip" \
    --output="$destination"
}

render_document "$project_dir/content/overview.md" "$output_dir/compare/index.html"
render_document "$project_dir/content/systems-index.md" "$output_dir/a-z/index.html"
render_document "$project_dir/content/patterns/index.md" "$output_dir/patterns/index.html"
render_document "$project_dir/content/benchmarks.md" "$output_dir/benchmarks/index.html"
render_document "$project_dir/content/capabilities.md" "$output_dir/capabilities/index.html"

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
#
# Commit ids are written out in full in the markdown, because a pin is only
# unambiguous at forty characters. Forty characters of hex is unreadable on a
# page, and the provenance list on the overview stacks fifty of them, so the
# rendered text is cut to eight with the full id kept in the link and a tooltip.
# Done here rather than by hand in the markdown: the source stays honest, and a
# report added later cannot reintroduce the noise.
while IFS= read -r -d '' page; do
  perl -0pi -e 's{(<table\b.*?</table>)}{<div class="table-wrap">$1</div>}gs' "$page"
  perl -0pi -e 's{<code>([0-9a-f]{40})</code>}
                 {"<code class=\"commit-id\" title=\"$1\">".substr($1,0,8)."\xe2\x80\xa6</code>"}gex' "$page"
done < <(find "$output_dir" -name "index.html" -print0)

echo "Built Agent Memory Atlas into $output_dir"

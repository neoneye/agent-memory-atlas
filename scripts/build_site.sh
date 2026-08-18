#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="$project_dir/docs"
template="$project_dir/templates/document.html"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "Pandoc is required to build the atlas." >&2
  exit 1
fi

# Every generator below reads this frontmatter, and YAML resolves a duplicate key
# by silently keeping the last one — so a second `capability_evidence:` block
# would be dropped here and the page would render as if it never existed. Pandoc
# reports that as a warning and builds anyway; this refuses to.
python3 "$project_dir/scripts/check_frontmatter_keys.py" "$project_dir"

# The comparative matrix is derived from each report's frontmatter, so adding a
# system never means editing a forty-row table by hand.
python3 "$project_dir/scripts/generate_matrix.py"

# The A–Z index is generated from the same frontmatter, so a report cannot exist
# without appearing in it. See scripts/generate_index.py for why the page exists.
python3 "$project_dir/scripts/generate_index.py"

# The storage/retrieval census on the capability index, from the stack_* keys
# each report declares. Regenerating is idempotent; --check enforces it in tests.
python3 "$project_dir/scripts/extract_stack.py" --render >/dev/null

rm -rf "$output_dir"
mkdir -p "$output_dir/assets" "$output_dir/a-z" "$output_dir/compare" "$output_dir/benchmarks" "$output_dir/capabilities" "$output_dir/verdicts" "$output_dir/build" "$output_dir/systems" "$output_dir/patterns" "$output_dir/methodology"

cp "$project_dir/site/index.html" "$output_dir/index.html"
# /discord.html is a redirect in front of the Discord invite, so the invite code
# lives in one file rather than in every place it has been shared.
cp "$project_dir/site/discord.html" "$output_dir/discord.html"
# A report whose upstream project renames itself gets a new slug and a stub at
# the old URL, so links already published against the old name keep working.
# site/redirects/<old-slug>.html becomes /systems/<old-slug>/index.html.
for redirect in "$project_dir"/site/redirects/*.html; do
  [[ -e "$redirect" ]] || continue
  redirect_slug="$(basename "$redirect" .html)"
  mkdir -p "$output_dir/systems/$redirect_slug"
  cp "$redirect" "$output_dir/systems/$redirect_slug/index.html"
done
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

  # A pattern page declares one `stance:` slug and the label is derived here, so
  # the prose on the page and the pill above it cannot drift into disagreeing
  # about what the page is. `check_pattern_stance.py` binds the slug to the
  # bucket the patterns index lists the page under; this only spells it.
  local stance
  local stance_label=""
  stance="$(sed -n 's/^stance:[[:space:]]*//p' "$input" | head -n 1)"
  stance="${stance//\"/}"
  case "$stance" in
    reporting) stance_label="Reporting an established practice" ;;
    advocacy) stance_label="Advocacy — one or two instances" ;;
    category-bound) stance_label="Mature in one category, unknown outside it" ;;
    mixed) stance_label="Reporting, with one advocacy claim" ;;
    "") ;;
    *) echo "unknown stance '$stance' in $input" >&2; exit 1 ;;
  esac

  local capability_strip=""
  if [[ "$input" == *"/content/systems/"* ]]; then
    capability_strip="$(python3 "$project_dir/scripts/capability_strip.py" "$input")"
  fi

  # 820px is a reading measure, chosen for paragraphs. A page that is a
  # directory rather than an argument — the A–Z index, four columns of it —
  # cannot honour that measure and stay in columns, and shrinking the columns to
  # fit is what produced a wrapped, ragged list in the first place. `layout:
  # wide` lets such a page opt out; everything else keeps the measure.
  local layout
  local shell_class=""
  layout="$(sed -n 's/^layout:[[:space:]]*//p' "$input" | head -n 1)"
  layout="${layout//\"/}"
  case "$layout" in
    wide) shell_class=" is-wide" ;;
    "") ;;
    *) echo "unknown layout '$layout' in $input" >&2; exit 1 ;;
  esac

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
    --variable="stance_label:$stance_label" \
    --variable="shell_class:$shell_class" \
    --output="$destination"

  # The diagrams render client-side, so an unrendered page hands a reader the
  # Mermaid source. Wrapping it in a captioned <figure> means that source
  # arrives labelled instead of as loose edge labels — twice now, an outside
  # review has read it as broken page layout.
  python3 "$project_dir/scripts/wrap_diagrams.py" "$destination"
}

render_document "$project_dir/content/overview.md" "$output_dir/compare/index.html"
render_document "$project_dir/content/systems-index.md" "$output_dir/a-z/index.html"
render_document "$project_dir/content/patterns/index.md" "$output_dir/patterns/index.html"
render_document "$project_dir/content/benchmarks.md" "$output_dir/benchmarks/index.html"
render_document "$project_dir/content/build.md" "$output_dir/build/index.html"
render_document "$project_dir/content/tensions.md" "$output_dir/tensions/index.html"
render_document "$project_dir/content/capabilities.md" "$output_dir/capabilities/index.html"
render_document "$project_dir/content/verdicts.md" "$output_dir/verdicts/index.html"
render_document "$project_dir/content/contributing.md" "$output_dir/contributing/index.html"

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

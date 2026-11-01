#!/usr/bin/env bash
# Rebuilds assets/memory-map/memory-map.json, the data behind the memory map page (content/map.md).
# The layout is seeded, so the same reports give the same file. Needs Node and, once, the pinned umap-js:
#   (cd scripts/memory_map && npm ci --ignore-scripts)
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
atlas="$(cd "$here/../.." && pwd)"
features="$(mktemp)"
trap 'rm -f "$features"' EXIT
python3 "$here/extract.py" "$atlas" "$features"
node "$here/layout.js" "$features" "$atlas/assets/memory-map/memory-map.json"

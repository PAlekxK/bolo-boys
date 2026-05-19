#!/usr/bin/env bash
# Run after editing data/events.json or data/venues.json.
#
# Regenerates derived artifacts from canonical JSON:
#   - MusicEvent JSON-LD block in index.html
#   - sitemap.xml <lastmod>
#   - bandsintown-upload.csv
#
# Idempotent: safe to run repeatedly.

set -euo pipefail

cd "$(dirname "$0")/.."

echo "→ events-to-jsonld.py"
python3 tools/events-to-jsonld.py

echo "→ bump-sitemap.py"
python3 tools/bump-sitemap.py

echo "→ events-to-bandsintown-csv.py"
python3 tools/events-to-bandsintown-csv.py > bandsintown-upload.csv
echo "wrote bandsintown-upload.csv ($(wc -l < bandsintown-upload.csv | tr -d ' ') lines)"

echo "→ check-stale-events.py"
# Non-blocking: surfaces past-dated events.json entries that need Phase 5 cleanup.
python3 tools/check-stale-events.py || true

echo "✓ done"

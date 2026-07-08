#!/usr/bin/env bash
# Run after editing data/events.json or data/venues.json.
#
# Regenerates derived artifacts from canonical JSON:
#   - per-event .ics files in assets/ics/ (+ populates ics_url in events.json)
#   - MusicEvent JSON-LD block in index.html
#   - sitemap.xml <lastmod>
#   - bandsintown-upload.csv
#
# Idempotent: safe to run repeatedly.

set -euo pipefail

cd "$(dirname "$0")/.."

# ics runs first: it populates events.json's ics_url field, which the site reads.
echo "→ events-to-ics.py"
python3 tools/events-to-ics.py

echo "→ events-to-jsonld.py"
python3 tools/events-to-jsonld.py

echo "→ bump-sitemap.py"
python3 tools/bump-sitemap.py

echo "→ events-to-bandsintown-csv.py"
python3 tools/events-to-bandsintown-csv.py > bandsintown-upload.csv
_total=$(wc -l < bandsintown-upload.csv | tr -d ' ')
echo "wrote bandsintown-upload.csv ($((_total - 1)) events + 1 header row)"

echo "→ check-stale-events.py"
# Non-blocking: surfaces past-dated events.json entries that need Phase 5 cleanup.
python3 tools/check-stale-events.py || true

# BIT upload reminder: compare md5 of current CSV against md5 stored in sentinel.
# Content-based check (not mtime) so idempotent reruns don't trigger false alarms.
SENTINEL="tools/.last-bit-upload"
CURRENT_MD5="$(md5 -q bandsintown-upload.csv 2>/dev/null || md5sum bandsintown-upload.csv 2>/dev/null | awk '{print $1}')"
STORED_MD5="$(cat "$SENTINEL" 2>/dev/null || echo '')"
if [[ -z "$STORED_MD5" ]] || [[ "$CURRENT_MD5" != "$STORED_MD5" ]]; then
  echo ""
  if [[ -z "$STORED_MD5" ]]; then
    echo "⚠ Bandsintown upload status unknown — no sentinel found."
  else
    echo "⚠ Bandsintown CSV content has changed since last upload."
  fi
  echo "  BIT APPENDS — does NOT dedupe by event ID. Re-uploading the full CSV"
  echo "  creates duplicates. Upload only NEW rows since last upload, OR be"
  echo "  ready to manually delete duplicates in the BIT UI afterward."
  echo "  After uploading, run: bash tools/mark-bit-upload.sh"
fi

echo "✓ done"

#!/usr/bin/env bash
# Mark that the current bandsintown-upload.csv has been uploaded to Bandsintown.
# Run this immediately after a successful BIT upload so /bolo-status can tell
# whether the local CSV is in sync with what BIT is actually showing.
#
# Usage: bash tools/mark-bit-upload.sh

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SENTINEL="${SCRIPT_DIR}/.last-bit-upload"
CSV="${SCRIPT_DIR}/../bandsintown-upload.csv"

if [[ ! -f "$CSV" ]]; then
  echo "✗ bandsintown-upload.csv not found at $CSV"
  echo "  Run tools/run-propagators.sh first."
  exit 1
fi

# Surface the duplicate-on-append risk if BIT already had these events.
# Documented in CLAUDE.md Phase 2 step 9 (discovered 2026-05-23).
echo "⚠ Reminder: BIT appends on upload. If you uploaded events that were"
echo "  already on BIT, duplicates exist now and need manual deletion."
echo ""

# Sentinel stores the md5 of the CSV at upload time. That way an idempotent
# propagator re-run (which bumps mtime but not content) won't trigger a false
# "upload needed" warning — we compare content, not mtime.
CSV_MD5="$(md5 -q "$CSV")"
echo "$CSV_MD5" > "$SENTINEL"

echo "✓ Marked Bandsintown upload at $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "  CSV: $CSV"
echo "  CSV md5: $CSV_MD5"
echo "  Sentinel: $SENTINEL"
echo ""
echo "  Next /bolo-status will treat the BIT profile as in sync with the"
echo "  current CSV. Re-run this script after any future BIT upload."

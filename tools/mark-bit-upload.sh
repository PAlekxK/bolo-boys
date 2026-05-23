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

touch "$SENTINEL"
echo "✓ Marked Bandsintown upload at $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "  CSV: $CSV"
echo "  Sentinel: $SENTINEL"
echo ""
echo "  Next /bolo-status will treat the BIT profile as in sync with the"
echo "  current CSV. Re-run this script after any future BIT upload."

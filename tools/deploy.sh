#!/usr/bin/env bash
# Deploy boloboys.band and PROVE it landed.
#
# The site is a Cloudflare Worker (bolo-boys-band) serving static assets.
# Pushing main does NOT deploy — there is no git integration. This script is
# the deploy. It exists because that gap silently froze the live site at the
# 6/30 commit for 17 days.
#
# Usage: bash tools/deploy.sh
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Deploying $(git rev-parse --short HEAD) — $(git log -1 --format=%s)"
npx --yes wrangler@latest deploy

echo
echo "==> Verifying against production (not inferring)"
# Cloudflare needs a beat to propagate; index.html has gone live ahead of its
# assets before (2026-07-16), so don't check too eagerly.
sleep 15

fail=0
check() { # path, expected_code
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://www.boloboys.band/$1?cb=$RANDOM$$")
  if [ "$code" = "$2" ]; then
    printf '  ok    %-42s %s\n' "/$1" "$code"
  else
    printf '  FAIL  %-42s %s (expected %s)\n' "/$1" "$code" "$2"; fail=1
  fi
}

# Fan-facing surfaces must be up.
check "" 200
check "data/events.json" 200
check "data/band.json" 200
check "sitemap.xml" 200
check "robots.txt" 200

# Internal files must NOT be served (see .assetsignore).
check "CLAUDE.md" 404
check "tools/deploy.sh" 404

# The live files must byte-match what's being deployed. This is the check that
# would have caught the 17-day freeze on day one. The site renders from the
# JSON at runtime, so a stale data file is just as broken as a stale page —
# check those too, not only index.html.
match() { # local_path, url_path
  curl -sL "https://www.boloboys.band/$2?cb=$RANDOM$$" -o "/tmp/bolo-prod-check.$$"
  if [ "$(md5 -q /tmp/bolo-prod-check.$$)" = "$(md5 -q "$1")" ]; then
    printf '  ok    live %-28s matches local HEAD\n' "$2"
  else
    printf '  FAIL  live %-28s does NOT match local HEAD\n' "$2"; fail=1
  fi
  rm -f "/tmp/bolo-prod-check.$$"
}
match index.html ""
match data/band.json data/band.json
match data/events.json data/events.json
match data/past-shows.json data/past-shows.json

# Stamp an observation in the ops-layer ledger — win or lose.
#
# The ops-layer's site tile does not report "when did we last deploy" (a deploy
# date can be old and completely fine, so it fails in the flattering direction).
# It reports live-vs-local equality plus a BOUNDED interval — "live content
# changed between X and Y" — derived from a ledger of every time we actually
# looked. That interval is only as tight as the looking is frequent, and until
# 2026-08-09 the only looks on record were from the day it was built.
#
# A deploy is the one moment we KNOW production changed, so it is the highest-
# value observation there is. Stamped before the pass/fail exit on purpose: an
# observation of a FAILED deploy is exactly what the ledger wants to hold.
#
# Never fails the deploy. The probe is a courtesy, not a gate — and the private
# repo may simply not be checked out beside this one.
facts=../bolo-private/tools/opslayer-facts.py
if [ -f "$facts" ]; then
  if python3 "$facts" --deep >/dev/null 2>&1; then
    echo "  ok    ops-layer site observation stamped"
  else
    echo "  note  ops-layer observation not stamped (probe failed) — deploy unaffected"
  fi
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "✅ Deployed and verified."
else
  echo "❌ Deployed but verification FAILED — the live site is not what you think."
  echo "   Re-run in ~30s (propagation), then check the Cloudflare dashboard."
  exit 1
fi

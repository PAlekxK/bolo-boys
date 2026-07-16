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
sleep 5

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

# The live homepage must byte-match the commit being deployed. This is the
# check that would have caught the 17-day freeze on day one.
curl -sL "https://www.boloboys.band/?cb=$RANDOM$$" -o /tmp/bolo-prod-index.$$
if [ "$(md5 -q /tmp/bolo-prod-index.$$)" = "$(md5 -q index.html)" ]; then
  echo "  ok    live index.html matches local HEAD"
else
  echo "  FAIL  live index.html does NOT match local HEAD — deploy did not land"
  fail=1
fi
rm -f /tmp/bolo-prod-index.$$

echo
if [ "$fail" -eq 0 ]; then
  echo "✅ Deployed and verified."
else
  echo "❌ Deployed but verification FAILED — the live site is not what you think."
  echo "   Re-run in ~30s (propagation), then check the Cloudflare dashboard."
  exit 1
fi

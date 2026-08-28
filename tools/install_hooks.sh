#!/usr/bin/env bash
# install_hooks.sh — install this repo's git hooks.
#
# .git/hooks is NOT versioned, so a hook that only lives there is one clone or one
# recovery away from being gone. This script is the tracked copy; run it after any
# clone or restore.
#
#   bash tools/install_hooks.sh          # install
#   bash tools/install_hooks.sh --status # what is installed right now
#
# The pre-commit hook refuses a commit whose generated views no longer match their
# source (tools/generated_views.py). It is the ONLY one of the three callers that
# catches the failure actually measured on 2026-08-28: edit data/appointments.json,
# commit, never run --render.
#
# It is not a cage. `git commit --no-verify` bypasses it, and deleting
# .git/hooks/pre-commit removes it entirely.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$REPO/.git/hooks/pre-commit"

if [[ "${1:-}" == "--status" ]]; then
  if [[ -x "$HOOK" ]]; then echo "installed: $HOOK"; else echo "NOT installed: $HOOK"; fi
  exit 0
fi

mkdir -p "$(dirname "$HOOK")"
cat > "$HOOK" <<'HOOKBODY'
#!/usr/bin/env bash
# Installed by tools/install_hooks.sh. Blocks a commit that would leave a generated
# view lagging its source. Bypass with --no-verify if you genuinely mean to.
REPO="$(git rev-parse --show-toplevel)"
if ! python3 "$REPO/tools/generated_views.py"; then
  echo ""
  echo "🔴 pre-commit: a generated view does not match its source."
  echo "   fix:    python3 tools/generated_views.py --render && git add -u"
  echo "   bypass: git commit --no-verify"
  exit 1
fi
HOOKBODY
chmod +x "$HOOK"
echo "installed $HOOK"

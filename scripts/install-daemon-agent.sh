#!/bin/bash
# Render and install the bellows daemon LaunchAgent for THIS machine.
# Idempotent: safe to re-run. bootstrap.sh will call this after migration.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TPL="$ROOT/scripts/com.eluvian.bellows-daemon.plist.template"
DEST="$HOME/Library/LaunchAgents/com.eluvian.bellows-daemon.plist"
LABEL="com.eluvian.bellows-daemon"

[ -x "$ROOT/.venv/bin/python" ] || { echo "no venv at $ROOT/.venv — run bootstrap first"; exit 1; }
[ -f "$ROOT/config.json" ]      || { echo "config.json missing at $ROOT — see MACHINE_SETUP.md"; exit 1; }

# Ensure claude is reachable on the PATH the plist will carry; without it the
# daemon's auth preflight fails at every KeepAlive retry.
PATH="$HOME/.local/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin" \
    command -v claude > /dev/null 2>&1 || {
    echo "claude not found on the plist PATH — install Claude Code first (see MACHINE_SETUP.md)"
    exit 1
}

mkdir -p "$HOME/Library/LaunchAgents"

sed -e "s|__BELLOWS_ROOT__|$ROOT|g" -e "s|__HOME__|$HOME|g" "$TPL" > "$DEST"
echo "rendered $DEST (root=$ROOT)"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$DEST"
echo "loaded $LABEL"

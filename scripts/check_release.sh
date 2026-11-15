#!/usr/bin/env bash
# Usage: check_release.sh VERSION NOTES_FILE
# Fails unless every file that carries the version agrees with VERSION and
# CHANGELOG.md has a section for it; writes that section's body to NOTES_FILE.
set -euo pipefail

v=$1
notes=$2
fail=0

expect() { # label actual
  if [ "$2" != "$3" ]; then
    echo "::error::$1 is '$2', expected '$3'"
    fail=1
  fi
}

expect package.json "$(jq -r .version package.json)" "$v"
expect plugin/claude/.claude-plugin/plugin.json "$(jq -r .version plugin/claude/.claude-plugin/plugin.json)" "$v"
expect plugin/.mars-plugin.json "$(jq -r .version plugin/.mars-plugin.json)" "$v"
expect "marketplace.json ref" "$(jq -r '.plugins[0].source.ref' .claude-plugin/marketplace.json)" "v$v"

awk -v h="## [$v]" '
  index($0, h) == 1 { on = 1; next }
  on && /^## / { exit }
  on
' CHANGELOG.md > "$notes"
if ! grep -q '[^[:space:]]' "$notes"; then
  echo "::error::CHANGELOG.md has no '## [$v]' section with content"
  fail=1
fi

exit $fail

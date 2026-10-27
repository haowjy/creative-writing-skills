#!/bin/bash
# Sync meridian context repos (work docs, KB) when a Claude session ends.
#
# Why: meridian's builtin git-autosync fires on meridian lifecycle events
# (spawn.start/finalized, work.started/done). Commits created AFTER the last
# such event — e.g. knowledge capture by an Agent-tool subagent as the final
# act of a session — are stranded locally until the next meridian event.
# This hook closes that gap at session end.
#
# Conditional by design: it does nothing unless the project has git-autosync
# configured in meridian.toml. `meridian hooks list` is the single authority
# on that config — no parallel parsing here.

command -v meridian >/dev/null 2>&1 || exit 0

names=$(meridian hooks list 2>/dev/null \
  | awk '$1 ~ /^git-autosync:/ && $NF == "enabled" {print $1}' \
  | sort -u)

[ -z "$names" ] && exit 0

for n in $names; do
  meridian hooks run "$n" >/dev/null 2>&1 || true
done

exit 0

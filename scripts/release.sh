#!/usr/bin/env bash

# Release script: bump the version in mars.toml, rebuild the committed plugin
# output, commit, tag, and optionally push.
#
# Usage:
#   ./scripts/release.sh              # patch bump (0.5.19 -> 0.5.20)
#   ./scripts/release.sh minor        # minor bump (0.5.19 -> 0.6.0)
#   ./scripts/release.sh major        # major bump (0.5.19 -> 1.0.0)
#   ./scripts/release.sh --push       # patch bump + push
#   ./scripts/release.sh minor --push # minor bump + push
#
# `mars version` would do this in one step, but it refuses this package today:
# the hand-authored hook directories under `.claude/hooks/` and
# `.codex/hooks/` are unmanaged target directories to Mars, so its publish
# check fails. Once those hooks live in a Mars-managed source location, this
# script can delegate.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

bump="patch"
push=false

for arg in "$@"; do
  case "$arg" in
    patch|minor|major) bump="$arg" ;;
    --push) push=true ;;
    -h|--help)
      echo "Usage: $0 [patch|minor|major] [--push]"
      echo "  patch (default): 0.5.19 -> 0.5.20"
      echo "  minor:           0.5.19 -> 0.6.0"
      echo "  major:           0.5.19 -> 1.0.0"
      echo "  --push:          push commit and tag to origin"
      exit 0
      ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

current=$(grep '^version' mars.toml | head -1 | sed 's/.*= *"\(.*\)"/\1/')
if [ -z "$current" ]; then
  echo "release.sh: could not read version from mars.toml" >&2
  exit 1
fi

IFS='.' read -r maj min pat <<< "$current"
case "$bump" in
  patch) pat=$((pat + 1)) ;;
  minor) min=$((min + 1)); pat=0 ;;
  major) maj=$((maj + 1)); min=0; pat=0 ;;
esac

next="${maj}.${min}.${pat}"
tag="v${next}"

errors=()

if git rev-parse "$tag" >/dev/null 2>&1; then
  errors+=("Tag $tag already exists")
fi

branch=$(git branch --show-current)
if [ "$branch" != "main" ]; then
  errors+=("Not on main branch (currently on '$branch')")
fi

if ! git diff --quiet --exit-code -- ':!mars.toml'; then
  errors+=("Working tree has uncommitted changes")
fi

if ! git diff --cached --quiet --exit-code; then
  errors+=("Staged changes exist")
fi

if ! command -v mars >/dev/null 2>&1; then
  errors+=("'mars' is not on PATH (install mars-agents==0.20.2); it rebuilds plugin/")
fi

if [ ${#errors[@]} -gt 0 ]; then
  echo "Release blocked: fix these before retrying:"
  for err in "${errors[@]}"; do
    echo "  - $err"
  done
  exit 1
fi

echo "Bumping: $current -> $next ($bump)"

# Portable in-place edit: `sed -i ''` is macOS-only, `sed -i` is GNU-only.
sed "s/^version = \"${current}\"/version = \"${next}\"/" mars.toml > mars.toml.new
mv mars.toml.new mars.toml

verify=$(grep '^version' mars.toml | head -1 | sed 's/.*= *"\(.*\)"/\1/')
if [ "$verify" != "$next" ]; then
  echo "release.sh: version replacement failed (got '$verify', expected '$next')" >&2
  git checkout -- mars.toml
  exit 1
fi

echo "Rebuilding the plugin at $next..."
if ! mars build plugin; then
  echo "release.sh: plugin build failed; restoring mars.toml" >&2
  git checkout -- mars.toml
  exit 1
fi

git add mars.toml plugin .claude-plugin .cursor-plugin package.json
git commit -m "v${next}"
git tag "$tag"

echo "Created commit and tag: $tag"

if $push; then
  git push origin main --tags
  echo "Pushed to origin (CI release workflow will run)"
else
  echo "Run 'git push origin main --tags' to publish, or rerun with --push"
fi

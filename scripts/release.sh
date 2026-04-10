#!/usr/bin/env bash

# Release script: bump version in mars.toml, commit, tag, optionally push.
# Usage:
#   ./scripts/release.sh              # patch bump (0.0.6 -> 0.0.7)
#   ./scripts/release.sh minor        # minor bump (0.0.6 -> 0.1.0)
#   ./scripts/release.sh major        # major bump (0.0.6 -> 1.0.0)
#   ./scripts/release.sh --push       # patch bump + push
#   ./scripts/release.sh minor --push # minor bump + push

cd "$(git rev-parse --show-toplevel)" || exit 1

bump="patch"
push=false

for arg in "$@"; do
  case "$arg" in
    patch|minor|major) bump="$arg" ;;
    --push) push=true ;;
    -h|--help)
      echo "Usage: $0 [patch|minor|major] [--push]"
      echo "  patch (default): 0.0.6 -> 0.0.7"
      echo "  minor:           0.0.6 -> 0.1.0"
      echo "  major:           0.0.6 -> 1.0.0"
      echo "  --push:          push commit and tag to origin"
      exit 0
      ;;
    *) echo "Unknown argument: $arg"; exit 1 ;;
  esac
done

# --- Collect all preflight errors before failing ---

errors=()

# Read current version from mars.toml
current=$(grep '^version' mars.toml | head -1 | sed 's/.*= *"\(.*\)"/\1/')
if [ -z "$current" ]; then
  errors+=("Could not read version from mars.toml")
fi

if [ ${#errors[@]} -eq 0 ]; then
  IFS='.' read -r maj min pat <<< "$current"

  case "$bump" in
    patch) pat=$((pat + 1)) ;;
    minor) min=$((min + 1)); pat=0 ;;
    major) maj=$((maj + 1)); min=0; pat=0 ;;
  esac

  next="${maj}.${min}.${pat}"
  tag="v${next}"

  # Check tag doesn't already exist
  if git rev-parse "$tag" >/dev/null 2>&1; then
    errors+=("Tag $tag already exists")
  fi
fi

# Check for uncommitted changes (except mars.toml which we're about to edit)
if ! git diff --quiet --exit-code -- ':!mars.toml'; then
  errors+=("Working tree has uncommitted changes")
  echo "  Dirty files:"
  git diff --name-only -- ':!mars.toml' | sed 's/^/    /'
fi

# Check for staged changes
if ! git diff --cached --quiet --exit-code; then
  errors+=("Staged changes exist")
  echo "  Staged files:"
  git diff --cached --name-only | sed 's/^/    /'
fi

# Check we're on main
branch=$(git branch --show-current)
if [ "$branch" != "main" ]; then
  errors+=("Not on main branch (currently on '$branch')")
fi

# Report all errors at once
if [ ${#errors[@]} -gt 0 ]; then
  echo "Release blocked — fix these before retrying:"
  for err in "${errors[@]}"; do
    echo "  - $err"
  done
  exit 1
fi

echo "Bumping: $current -> $next ($bump)"

# Bump version in mars.toml
sed -i '' "s/^version = \"${current}\"/version = \"${next}\"/" mars.toml

# Verify the change took
verify=$(grep '^version' mars.toml | head -1 | sed 's/.*= *"\(.*\)"/\1/')
if [ "$verify" != "$next" ]; then
  echo "Error: version replacement failed (got '$verify', expected '$next')"
  git checkout mars.toml
  exit 1
fi

git add mars.toml
git commit -m "Release $tag"
git tag "$tag"

echo "Created commit and tag: $tag"

if $push; then
  git push origin main --tags
  echo "Pushed to origin (CI release workflow will run)"
else
  echo "Run 'git push origin main --tags' to publish, or rerun with --push"
fi

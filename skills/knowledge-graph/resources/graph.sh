#!/usr/bin/env bash
#
# graph.sh — Build a document relationship map from markdown files.
#
# Usage: bash graph.sh [root_directory]
#   Defaults to current working directory if no argument given.
#
# Outputs:
#   - File connectivity (outbound links per file)
#   - Orphaned files (no inbound links)
#   - Broken links (targets that don't exist)
#   - Missing back-links (A -> B but B !-> A)
#   - Entity mention map (wikilinks across files)
#
# Dependencies: grep, awk, sed, find, sort, comm — standard unix tools only.

set -euo pipefail

ROOT="${1:-.}"
ROOT="$(cd "$ROOT" && pwd)"

TMPDIR_GRAPH="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_GRAPH"' EXIT

LINKS_FILE="$TMPDIR_GRAPH/links.tsv"        # source_file \t target_path
WIKILINKS_FILE="$TMPDIR_GRAPH/wikilinks.tsv" # source_file \t entity_name
MERMAID_FILE="$TMPDIR_GRAPH/mermaid.tsv"     # source_file \t relationship_line
YAML_REFS_FILE="$TMPDIR_GRAPH/yaml_refs.tsv" # source_file \t ref_type \t ref_value
ALL_FILES="$TMPDIR_GRAPH/all_files.txt"
LINKED_TARGETS="$TMPDIR_GRAPH/linked_targets.txt"
LINK_SOURCES="$TMPDIR_GRAPH/link_sources.tsv" # target_file \t source_file (reverse index)

# --- Collect all markdown files ---
find "$ROOT" -name '*.md' -not -path '*/.git/*' -not -path '*/node_modules/*' | sort > "$ALL_FILES"

FILE_COUNT=$(wc -l < "$ALL_FILES" | tr -d ' ')
if [ "$FILE_COUNT" -eq 0 ]; then
    echo "No .md files found under $ROOT"
    exit 0
fi

# --- Extract markdown links [text](path) ---
while IFS= read -r file; do
    # Skip YAML front matter, then extract markdown links
    # Only match links to local paths (not http/https/mailto)
    awk 'NR==1 && /^---$/ { skip=1; next } skip && /^---$/ { skip=0; next } !skip { print }' "$file" \
    | grep -oE '\[[^]]*\]\([^)]+\)' 2>/dev/null \
    | sed 's/.*](\([^)]*\))/\1/' \
    | grep -v '^https\?://' \
    | grep -v '^mailto:' \
    | sed 's/#.*//' \
    | while IFS= read -r link; do
        [ -z "$link" ] && continue
        # Resolve relative to file's directory
        filedir="$(dirname "$file")"
        resolved="$(cd "$filedir" 2>/dev/null && realpath -q "$link" 2>/dev/null || echo "$filedir/$link")"
        printf '%s\t%s\n' "$file" "$resolved"
    done
done < "$ALL_FILES" > "$LINKS_FILE" 2>/dev/null || true

# --- Extract wikilinks [[entity]] ---
while IFS= read -r file; do
    grep -oE '\[\[[^]]+\]\]' "$file" 2>/dev/null \
    | sed 's/\[\[\(.*\)\]\]/\1/' \
    | while IFS= read -r entity; do
        printf '%s\t%s\n' "$file" "$entity"
    done
done < "$ALL_FILES" > "$WIKILINKS_FILE" 2>/dev/null || true

# --- Extract mermaid relationship lines ---
while IFS= read -r file; do
    awk '
    /^```mermaid/ { in_mermaid=1; next }
    /^```/ { in_mermaid=0; next }
    in_mermaid && /-->|---|-\.->|==>|--[^-]/ {
        print FILENAME "\t" $0
    }
    ' FILENAME="$file" "$file" 2>/dev/null
done < "$ALL_FILES" > "$MERMAID_FILE" 2>/dev/null || true

# --- Extract YAML front matter references ---
while IFS= read -r file; do
    # Read YAML front matter (between first --- and second ---)
    awk '
    NR==1 && /^---$/ { in_yaml=1; next }
    in_yaml && /^---$/ { exit }
    in_yaml && /^(arc|chapter|characters|location|locations|requires|see|related|pov|arc_id|chapters):/ {
        print FILENAME "\t" $0
    }
    ' FILENAME="$file" "$file" 2>/dev/null
done < "$ALL_FILES" > "$YAML_REFS_FILE" 2>/dev/null || true

# === OUTPUT REPORT ===

echo "=========================================="
echo "  Document Relationship Graph"
echo "  Root: $ROOT"
echo "  Files: $FILE_COUNT markdown files"
echo "=========================================="
echo ""

# --- Section 1: File Connectivity ---
echo "## Outbound Links"
echo ""
if [ -s "$LINKS_FILE" ]; then
    awk -F'\t' -v root="$ROOT" '{
        # Strip root prefix for readability
        src = $1; sub(root "/", "", src)
        tgt = $2; sub(root "/", "", tgt)
        print src " -> " tgt
    }' "$LINKS_FILE" | sort
else
    echo "(no markdown links found)"
fi
echo ""

# --- Section 2: Wikilinks / Entity Mentions ---
echo "## Wikilink Entity Mentions"
echo ""
if [ -s "$WIKILINKS_FILE" ]; then
    awk -F'\t' -v root="$ROOT" '{
        src = $1; sub(root "/", "", src)
        print $2 "\t" src
    }' "$WIKILINKS_FILE" | sort | awk -F'\t' '
    $1 != prev {
        if (prev != "") print ""
        printf "[[%s]]:\n", $1
        prev = $1
    }
    { printf "  - %s\n", $2 }
    END { if (prev != "") print "" }
    '
else
    echo "(no wikilinks found)"
fi
echo ""

# --- Section 3: Mermaid Relationships ---
echo "## Mermaid Relationships"
echo ""
if [ -s "$MERMAID_FILE" ]; then
    awk -F'\t' -v root="$ROOT" '{
        src = $1; sub(root "/", "", src)
        # Trim whitespace from relationship line
        line = $2; gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)
        print src ": " line
    }' "$MERMAID_FILE" | sort
else
    echo "(no mermaid relationships found)"
fi
echo ""

# --- Section 4: YAML Front Matter References ---
echo "## YAML Front Matter References"
echo ""
if [ -s "$YAML_REFS_FILE" ]; then
    awk -F'\t' -v root="$ROOT" '{
        src = $1; sub(root "/", "", src)
        # Trim whitespace
        ref = $2; gsub(/^[[:space:]]+|[[:space:]]+$/, "", ref)
        print src ": " ref
    }' "$YAML_REFS_FILE" | sort
else
    echo "(no YAML references found)"
fi
echo ""

# --- Section 5: Broken Links ---
echo "## Broken Links"
echo ""
broken_count=0
if [ -s "$LINKS_FILE" ]; then
    while IFS=$'\t' read -r src tgt; do
        if [ ! -e "$tgt" ]; then
            src_short="${src#$ROOT/}"
            tgt_short="${tgt#$ROOT/}"
            echo "  $src_short -> $tgt_short (not found)"
            broken_count=$((broken_count + 1))
        fi
    done < "$LINKS_FILE"
fi
if [ "$broken_count" -eq 0 ]; then
    echo "(no broken links)"
fi
echo ""

# --- Section 6: Orphaned Files ---
# Build set of files that are targets of at least one link
echo "## Orphaned Files (no inbound links)"
echo ""
if [ -s "$LINKS_FILE" ]; then
    awk -F'\t' '{ print $2 }' "$LINKS_FILE" | sort -u > "$LINKED_TARGETS"
else
    touch "$LINKED_TARGETS"
fi

orphan_count=0
while IFS= read -r file; do
    if ! grep -qF "$file" "$LINKED_TARGETS" 2>/dev/null; then
        file_short="${file#$ROOT/}"
        echo "  $file_short"
        orphan_count=$((orphan_count + 1))
    fi
done < "$ALL_FILES"
if [ "$orphan_count" -eq 0 ]; then
    echo "(no orphaned files)"
fi
echo ""

# --- Section 7: Missing Back-links ---
echo "## Missing Back-links (A -> B but B does not -> A)"
echo ""

# Build reverse index
if [ -s "$LINKS_FILE" ]; then
    awk -F'\t' '{ print $2 "\t" $1 }' "$LINKS_FILE" > "$LINK_SOURCES"
fi

missing_count=0
if [ -s "$LINKS_FILE" ]; then
    while IFS=$'\t' read -r src tgt; do
        [ ! -e "$tgt" ] && continue  # skip broken links
        # Check if target links back to source
        if ! grep -q "^${tgt}	${src}$" "$LINKS_FILE" 2>/dev/null; then
            src_short="${src#$ROOT/}"
            tgt_short="${tgt#$ROOT/}"
            echo "  $src_short -> $tgt_short (no back-link)"
            missing_count=$((missing_count + 1))
        fi
    done < "$LINKS_FILE"
fi
if [ "$missing_count" -eq 0 ]; then
    echo "(no missing back-links)"
fi
echo ""

# --- Summary ---
link_count=0
[ -s "$LINKS_FILE" ] && link_count=$(wc -l < "$LINKS_FILE" | tr -d ' ')
wikilink_count=0
[ -s "$WIKILINKS_FILE" ] && wikilink_count=$(wc -l < "$WIKILINKS_FILE" | tr -d ' ')
mermaid_count=0
[ -s "$MERMAID_FILE" ] && mermaid_count=$(wc -l < "$MERMAID_FILE" | tr -d ' ')

echo "## Summary"
echo "  Files scanned:       $FILE_COUNT"
echo "  Markdown links:      $link_count"
echo "  Wikilinks:           $wikilink_count"
echo "  Mermaid relations:   $mermaid_count"
echo "  Broken links:        $broken_count"
echo "  Orphaned files:      $orphan_count"
echo "  Missing back-links:  $missing_count"

#!/usr/bin/env bash
#
# analyze.sh — Mechanical prose metrics for a markdown file.
#
# Usage: bash analyze.sh <file.md> [window_size]
#   file.md      — markdown file to analyze
#   window_size  — paragraphs for repetition detection window (default: 5)
#
# Measures:
#   - Sentence length distribution (mean, median, min, max, stdev)
#   - Sentence opener variety (pronoun, article, conjunction, name, other)
#   - Dialogue-to-narration ratio
#   - Repetition detection (echoed words within N paragraphs)
#   - Pronoun distribution (POV consistency)
#
# Dependencies: awk, sed, grep, wc, sort, tr — standard unix tools only.

set -euo pipefail

FILE="${1:-}"
WINDOW="${2:-5}"

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
    echo "Usage: bash analyze.sh <file.md> [window_size]"
    exit 1
fi

TMPDIR_ANALYSIS="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_ANALYSIS"' EXIT

# --- Preprocess: strip YAML front matter, code blocks, and mermaid blocks ---
CLEAN="$TMPDIR_ANALYSIS/clean.txt"
awk '
BEGIN { skip=0; first=1 }
first && /^---$/ { skip=1; first=0; next }
skip && /^---$/ { skip=0; first=0; next }
/^```/ { skip=!skip; next }
!skip { first=0; print }
' "$FILE" > "$CLEAN"

# Strip markdown formatting but preserve text content
# PROSE keeps blank lines (needed for paragraph splitting)
# PROSE_DENSE strips blank lines (needed for sentence/word analysis)
PROSE="$TMPDIR_ANALYSIS/prose.txt"
PROSE_DENSE="$TMPDIR_ANALYSIS/prose_dense.txt"
sed -e 's/^#\+ //' \
    -e 's/\*\*\([^*]*\)\*\*/\1/g' \
    -e 's/\*\([^*]*\)\*/\1/g' \
    -e 's/_\([^_]*\)_/\1/g' \
    -e 's/\[[^]]*\]([^)]*)//g' \
    "$CLEAN" > "$PROSE"
sed '/^[[:space:]]*$/d' "$PROSE" > "$PROSE_DENSE"

echo "=========================================="
echo "  Prose Analysis: $(basename "$FILE")"
echo "=========================================="
echo ""

# === SENTENCE LENGTH DISTRIBUTION ===
echo "## Sentence Length Distribution"
echo ""

# Split into sentences (approximate — split on . ! ? followed by space or EOL)
SENTENCES="$TMPDIR_ANALYSIS/sentences.txt"
cat "$PROSE_DENSE" | tr '\n' ' ' | sed 's/\([.!?]\)[[:space:]]/\1\n/g' | sed '/^[[:space:]]*$/d' > "$SENTENCES"

SENT_LENGTHS="$TMPDIR_ANALYSIS/sent_lengths.txt"
while IFS= read -r sentence; do
    # Count words in sentence
    echo "$sentence" | wc -w | tr -d ' '
done < "$SENTENCES" > "$SENT_LENGTHS"

awk '
{
    lengths[NR] = $1
    sum += $1
    if ($1 > max) max = $1
    if (min == 0 || $1 < min) min = $1
    n++
}
END {
    if (n == 0) { print "  (no sentences found)"; exit }
    mean = sum / n

    # Standard deviation
    for (i = 1; i <= n; i++) {
        diff = lengths[i] - mean
        sumsq += diff * diff
    }
    stdev = sqrt(sumsq / n)

    # Median (simple: sort and pick middle)
    # Copy to sortable array
    for (i = 1; i <= n; i++) sorted[i] = lengths[i]
    # Bubble sort (fine for typical chapter sizes)
    for (i = 1; i <= n; i++)
        for (j = i+1; j <= n; j++)
            if (sorted[i] > sorted[j]) {
                tmp = sorted[i]; sorted[i] = sorted[j]; sorted[j] = tmp
            }
    if (n % 2 == 1) median = sorted[int(n/2)+1]
    else median = (sorted[n/2] + sorted[n/2+1]) / 2

    printf "  Sentences:  %d\n", n
    printf "  Mean:       %.1f words\n", mean
    printf "  Median:     %.1f words\n", median
    printf "  Min:        %d words\n", min
    printf "  Max:        %d words\n", max
    printf "  Std Dev:    %.1f\n", stdev
}
' "$SENT_LENGTHS"
echo ""

# === SENTENCE OPENER VARIETY ===
echo "## Sentence Opener Variety"
echo ""

OPENERS="$TMPDIR_ANALYSIS/openers.txt"
# Extract first word of each sentence, lowercase
sed 's/^[[:space:]]*//' "$SENTENCES" \
    | awk '{ print tolower($1) }' \
    | sed 's/[^a-z]//g' \
    | grep -v '^$' > "$OPENERS"

OPENER_COUNT=$(wc -l < "$OPENERS" | tr -d ' ')

# Categorize openers
awk '
{
    w = $1
    if (w ~ /^(i|me|my|we|our|you|your|he|his|him|she|her|they|their|them|it|its)$/)
        pronouns++
    else if (w ~ /^(the|a|an|this|that|these|those)$/)
        articles++
    else if (w ~ /^(and|but|or|so|yet|for|nor|because|although|though|while|when|if|after|before|since|until|as|once)$/)
        conjunctions++
    else
        other++
    total++
}
END {
    if (total == 0) { print "  (no openers found)"; exit }
    printf "  Pronoun starts:      %d (%.0f%%)\n", pronouns, (pronouns/total)*100
    printf "  Article starts:      %d (%.0f%%)\n", articles, (articles/total)*100
    printf "  Conjunction starts:  %d (%.0f%%)\n", conjunctions, (conjunctions/total)*100
    printf "  Other starts:        %d (%.0f%%)\n", other, (other/total)*100
    printf "  Total sentences:     %d\n", total
}
' "$OPENERS"
echo ""

# === DIALOGUE-TO-NARRATION RATIO ===
echo "## Dialogue-to-Narration Ratio"
echo ""

# Count lines containing dialogue (lines with quoted speech)
DIALOGUE_LINES=$(grep -cE '".+"' "$PROSE_DENSE" 2>/dev/null || echo "0")
TOTAL_LINES=$(wc -l < "$PROSE_DENSE" | tr -d ' ')
NARRATION_LINES=$((TOTAL_LINES - DIALOGUE_LINES))

if [ "$TOTAL_LINES" -gt 0 ]; then
    DIALOGUE_PCT=$(awk "BEGIN { printf \"%.0f\", ($DIALOGUE_LINES / $TOTAL_LINES) * 100 }")
    NARRATION_PCT=$(awk "BEGIN { printf \"%.0f\", ($NARRATION_LINES / $TOTAL_LINES) * 100 }")
    echo "  Dialogue lines:   $DIALOGUE_LINES ($DIALOGUE_PCT%)"
    echo "  Narration lines:  $NARRATION_LINES ($NARRATION_PCT%)"
    echo "  Total lines:      $TOTAL_LINES"
else
    echo "  (no content found)"
fi
echo ""

# === REPETITION DETECTION ===
echo "## Repetition Detection (window: $WINDOW paragraphs)"
echo ""

# Split into paragraphs (blank-line separated), then find repeated content words
# within sliding window
PARAGRAPHS="$TMPDIR_ANALYSIS/paragraphs"
mkdir -p "$PARAGRAPHS"

# Split file into paragraph files
awk -v dir="$PARAGRAPHS" '
BEGIN { pnum=1; outfile=dir "/p_" sprintf("%04d", pnum) ".txt" }
/^[[:space:]]*$/ {
    if (has_content) {
        pnum++
        outfile = dir "/p_" sprintf("%04d", pnum) ".txt"
        has_content = 0
    }
    next
}
{
    print tolower($0) >> outfile
    has_content = 1
}
' "$PROSE"

PARA_COUNT=$(ls "$PARAGRAPHS"/p_*.txt 2>/dev/null | wc -l | tr -d ' ')

if [ "$PARA_COUNT" -ge 2 ]; then
    # For each sliding window, find words appearing 3+ times that are 5+ chars
    # (skip short common words)
    REPEATS="$TMPDIR_ANALYSIS/repeats.txt"
    para_files=($(ls "$PARAGRAPHS"/p_*.txt 2>/dev/null | sort))

    for ((i=0; i <= ${#para_files[@]} - WINDOW && i >= 0; i++)); do
        end=$((i + WINDOW))
        [ "$end" -gt "${#para_files[@]}" ] && end="${#para_files[@]}"
        window_files=("${para_files[@]:i:WINDOW}")

        cat "${window_files[@]}" \
            | tr -cs 'a-z' '\n' \
            | grep -E '^.{5,}$' \
            | sort | uniq -c | sort -rn \
            | awk '$1 >= 3 { printf "  %dx \"%s\" (paragraphs %d-%d)\n", $1, $2, start+1, end }' \
                start="$i" end="$((i + WINDOW))"
    done | sort -u > "$REPEATS"

    if [ -s "$REPEATS" ]; then
        # Show top 20 most repeated
        head -20 "$REPEATS"
        repeat_count=$(wc -l < "$REPEATS" | tr -d ' ')
        if [ "$repeat_count" -gt 20 ]; then
            echo "  ... and $((repeat_count - 20)) more"
        fi
    else
        echo "  (no notable repetitions detected)"
    fi
else
    echo "  (not enough paragraphs for window analysis)"
fi
echo ""

# === PRONOUN DISTRIBUTION ===
echo "## Pronoun Distribution (POV Consistency)"
echo ""

# Count pronouns by category
ALL_WORDS="$TMPDIR_ANALYSIS/all_words.txt"
cat "$PROSE_DENSE" | tr -cs 'A-Za-z' '\n' | tr 'A-Z' 'a-z' | grep -v '^$' > "$ALL_WORDS"
TOTAL_WORDS=$(wc -l < "$ALL_WORDS" | tr -d ' ')

awk '
{
    w = $1
    if (w ~ /^(i|me|my|mine|myself)$/) first_person++
    else if (w ~ /^(we|us|our|ours|ourselves)$/) first_plural++
    else if (w ~ /^(you|your|yours|yourself|yourselves)$/) second_person++
    else if (w ~ /^(he|him|his|himself)$/) third_masc++
    else if (w ~ /^(she|her|hers|herself)$/) third_fem++
    else if (w ~ /^(they|them|their|theirs|themselves)$/) third_plural++
    else if (w ~ /^(it|its|itself)$/) third_neuter++
    total++
}
END {
    if (total == 0) { print "  (no words found)"; exit }
    printf "  1st person singular (I/me/my):     %d (%.1f%%)\n", first_person, (first_person/total)*100
    printf "  1st person plural (we/us/our):     %d (%.1f%%)\n", first_plural, (first_plural/total)*100
    printf "  2nd person (you/your):             %d (%.1f%%)\n", second_person, (second_person/total)*100
    printf "  3rd person masc (he/him/his):      %d (%.1f%%)\n", third_masc, (third_masc/total)*100
    printf "  3rd person fem (she/her/hers):     %d (%.1f%%)\n", third_fem, (third_fem/total)*100
    printf "  3rd person plural (they/them):     %d (%.1f%%)\n", third_plural, (third_plural/total)*100
    printf "  3rd person neuter (it/its):        %d (%.1f%%)\n", third_neuter, (third_neuter/total)*100
    printf "  Total words:                       %d\n", total
}
' "$ALL_WORDS"
echo ""

echo "=========================================="
echo "  Analysis complete."
echo "=========================================="

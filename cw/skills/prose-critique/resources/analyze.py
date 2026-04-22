#!/usr/bin/env python3
"""
Mechanical prose metrics for a markdown file.

Usage:
    uv run resources/analyze.py <file.md> [window_size]
"""

from __future__ import annotations

import argparse
import re
import statistics
import sys
from collections import Counter
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
QUOTE_RE = re.compile(r'".+?"')

PRONOUN_STARTS = {
    "i",
    "me",
    "my",
    "we",
    "our",
    "you",
    "your",
    "he",
    "his",
    "him",
    "she",
    "her",
    "they",
    "their",
    "them",
    "it",
    "its",
}
ARTICLE_STARTS = {"the", "a", "an", "this", "that", "these", "those"}
CONJUNCTION_STARTS = {
    "and",
    "but",
    "or",
    "so",
    "yet",
    "for",
    "nor",
    "because",
    "although",
    "though",
    "while",
    "when",
    "if",
    "after",
    "before",
    "since",
    "until",
    "as",
    "once",
}
PRONOUN_GROUPS = {
    "1st person singular (I/me/my)": {"i", "me", "my", "mine", "myself"},
    "1st person plural (we/us/our)": {"we", "us", "our", "ours", "ourselves"},
    "2nd person (you/your)": {"you", "your", "yours", "yourself", "yourselves"},
    "3rd person masc (he/him/his)": {"he", "him", "his", "himself"},
    "3rd person fem (she/her/hers)": {"she", "her", "hers", "herself"},
    "3rd person plural (they/them)": {
        "they",
        "them",
        "their",
        "theirs",
        "themselves",
    },
    "3rd person neuter (it/its)": {"it", "its", "itself"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze prose mechanics in markdown.")
    parser.add_argument("file", help="Markdown file to analyze")
    parser.add_argument(
        "window_size",
        nargs="?",
        type=int,
        default=5,
        help="Paragraph window for repetition detection",
    )
    return parser.parse_args()


def strip_frontmatter_and_fences(text: str) -> str:
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                start = idx + 1
                break

    cleaned: list[str] = []
    in_fence = False
    for line in lines[start:]:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            cleaned.append(line)
    return "\n".join(cleaned)


def strip_markdown(text: str) -> str:
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    return text


def get_sentences(dense_text: str) -> list[str]:
    flattened = " ".join(line.strip() for line in dense_text.splitlines() if line.strip())
    return [part.strip() for part in SENTENCE_SPLIT_RE.split(flattened) if part.strip()]


def words(text: str) -> list[str]:
    return [match.group(0).lower() for match in WORD_RE.finditer(text)]


def paragraphs(prose_text: str) -> list[str]:
    return [chunk.strip() for chunk in re.split(r"\n\s*\n", prose_text) if chunk.strip()]


def print_sentence_lengths(sentences: list[str]) -> None:
    print("## Sentence Length Distribution")
    print()
    lengths = [len(words(sentence)) for sentence in sentences if words(sentence)]
    if not lengths:
        print("  (no sentences found)")
        print()
        return

    mean_value = statistics.fmean(lengths)
    median_value = statistics.median(lengths)
    stdev_value = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0

    print(f"  Sentences:  {len(lengths)}")
    print(f"  Mean:       {mean_value:.1f} words")
    print(f"  Median:     {median_value:.1f} words")
    print(f"  Min:        {min(lengths)} words")
    print(f"  Max:        {max(lengths)} words")
    print(f"  Std Dev:    {stdev_value:.1f}")
    print()


def print_sentence_openers(sentences: list[str]) -> None:
    print("## Sentence Opener Variety")
    print()
    opener_words = []
    for sentence in sentences:
        match = WORD_RE.search(sentence)
        if match:
            opener_words.append(match.group(0).lower())

    if not opener_words:
        print("  (no openers found)")
        print()
        return

    categories = Counter()
    for opener in opener_words:
        if opener in PRONOUN_STARTS:
            categories["pronouns"] += 1
        elif opener in ARTICLE_STARTS:
            categories["articles"] += 1
        elif opener in CONJUNCTION_STARTS:
            categories["conjunctions"] += 1
        else:
            categories["other"] += 1

    total = len(opener_words)
    print(
        f"  Pronoun starts:      {categories['pronouns']} ({(categories['pronouns'] / total) * 100:.0f}%)"
    )
    print(
        f"  Article starts:      {categories['articles']} ({(categories['articles'] / total) * 100:.0f}%)"
    )
    print(
        f"  Conjunction starts:  {categories['conjunctions']} ({(categories['conjunctions'] / total) * 100:.0f}%)"
    )
    print(
        f"  Other starts:        {categories['other']} ({(categories['other'] / total) * 100:.0f}%)"
    )
    print(f"  Total sentences:     {total}")
    print()


def print_dialogue_ratio(dense_lines: list[str]) -> None:
    print("## Dialogue-to-Narration Ratio")
    print()
    total_lines = len(dense_lines)
    if not total_lines:
        print("  (no content found)")
        print()
        return

    dialogue_lines = sum(1 for line in dense_lines if QUOTE_RE.search(line))
    narration_lines = total_lines - dialogue_lines
    print(
        f"  Dialogue lines:   {dialogue_lines} ({(dialogue_lines / total_lines) * 100:.0f}%)"
    )
    print(
        f"  Narration lines:  {narration_lines} ({(narration_lines / total_lines) * 100:.0f}%)"
    )
    print(f"  Total lines:      {total_lines}")
    print()


def print_repetition(paragraph_list: list[str], window_size: int) -> None:
    print(f"## Repetition Detection (window: {window_size} paragraphs)")
    print()
    if len(paragraph_list) < 2:
        print("  (not enough paragraphs for window analysis)")
        print()
        return

    findings: dict[tuple[str, int, int], int] = {}
    for start in range(0, max(len(paragraph_list) - window_size + 1, 1)):
        window = paragraph_list[start : start + window_size]
        counts = Counter(
            word
            for paragraph in window
            for word in words(paragraph)
            if len(word) >= 5
        )
        for word, count in counts.items():
            if count >= 3:
                findings[(word, start + 1, start + len(window))] = count

    if not findings:
        print("  (no notable repetitions detected)")
        print()
        return

    ordered = sorted(findings.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
    for (word, start, end), count in ordered[:20]:
        print(f'  {count}x "{word}" (paragraphs {start}-{end})')
    if len(ordered) > 20:
        print(f"  ... and {len(ordered) - 20} more")
    print()


def print_pronouns(dense_text: str) -> None:
    print("## Pronoun Distribution (POV Consistency)")
    print()
    all_words = words(dense_text)
    if not all_words:
        print("  (no words found)")
        print()
        return

    total = len(all_words)
    counts = Counter(all_words)
    for label, variants in PRONOUN_GROUPS.items():
        count = sum(counts[variant] for variant in variants)
        print(f"  {label:<35} {count:>5} ({(count / total) * 100:.1f}%)")
    print(f"  Total words:                       {total}")
    print()


def main() -> int:
    args = parse_args()
    path = Path(args.file)
    if not path.is_file():
        print("Usage: uv run resources/analyze.py <file.md> [window_size]", file=sys.stderr)
        return 1
    if args.window_size <= 0:
        print("window_size must be a positive integer", file=sys.stderr)
        return 1

    raw_text = path.read_text(encoding="utf-8", errors="ignore")
    prose_text = strip_markdown(strip_frontmatter_and_fences(raw_text))
    dense_lines = [line for line in prose_text.splitlines() if line.strip()]
    dense_text = "\n".join(dense_lines)
    sentence_list = get_sentences(dense_text)
    paragraph_list = paragraphs(prose_text)

    print("==========================================")
    print(f"  Prose Analysis: {path.name}")
    print("==========================================")
    print()

    print_sentence_lengths(sentence_list)
    print_sentence_openers(sentence_list)
    print_dialogue_ratio(dense_lines)
    print_repetition(paragraph_list, args.window_size)
    print_pronouns(dense_text)

    print("==========================================")
    print("  Analysis complete.")
    print("==========================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

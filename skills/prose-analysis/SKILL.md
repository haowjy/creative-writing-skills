---
name: prose-analysis
description: Mechanical prose metrics — sentence length, opener variety, dialogue ratio, repetition, pronoun distribution. Use when you need quantitative signals about prose before making subjective judgments, or when comparing a draft against the project's baseline.
---

# Prose Analysis — Quantitative Signals

Scripts that measure mechanical properties of prose. These produce numbers, not quality verdicts. The numbers become useful only when compared against the project's own baseline — research shows no reliable universal thresholds for "good" prose exist.

## What the Scripts Measure

The bundled `resources/analyze.sh` script produces:

- **Sentence length distribution** — mean, median, min, max, standard deviation. Compare across chapters for consistency. High variance often indicates varied rhythm (usually good); low variance may indicate monotone pacing.
- **Sentence opener variety** — categorizes first words of sentences (pronoun, article, conjunction, name, other). Heavy pronoun-leading ("I did... I saw... I felt...") is a common POV drift signal.
- **Dialogue-to-narration ratio** — proportion of lines that are dialogue vs narration. Useful for scene-type comparison (action scenes should skew narration, conversation scenes should skew dialogue).
- **Repetition detection** — words and short phrases that appear multiple times within a sliding window of N paragraphs. Catches echoed words the author didn't intend.
- **Pronoun distribution** — counts of I/me/my vs he/she/they/etc. Useful as a POV consistency check (a first-person chapter with sudden third-person pronouns needs investigation).

## Running the Script

```bash
bash resources/analyze.sh <file.md> [window_size]
```

- `file.md` — the markdown file to analyze
- `window_size` — optional, number of paragraphs for the repetition detection window (default: 5)

Output is plain text with labeled sections. Standard unix tools only (awk, sed, grep, wc, sort).

## What the Scripts Don't Measure

Some metrics from the research literature are excluded because they're either unreliable, require Python NLP libraries, or don't produce actionable signals for creative writing:

- **Readability scores** (Flesch-Kincaid, etc.) — not a quality predictor for fiction
- **Vocabulary richness** (raw TTR) — methodologically weak at varying text lengths. MATTR is better but requires windowed computation that's impractical in pure bash.
- **Perplexity** — requires a language model to compute, and very low perplexity just means "predictable," not "bad"
- **Adverb/filter word density** — modest effect sizes, heavily genre-confounded

## Resources

- **`resources/analyze.sh`** — the analysis script
- **`resources/antipatterns.md`** — AI writing antipatterns, honestly categorized as research-backed vs community folklore. Read this when reviewing AI-generated drafts and you want to know which signals are worth investigating vs which are unreliable.
- **`resources/baseline.md`** — how to establish a project baseline from existing chapters and compare new drafts against it. Read this before interpreting analysis output for the first time on a project.

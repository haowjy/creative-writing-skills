# Establishing a Project Baseline

Prose metrics are meaningless in isolation. "Average sentence length: 14.2 words" tells you nothing without knowing what's normal for this project, this author, this genre. The baseline is the project's own published chapters — the prose the author has already approved as representative of their voice.

## Building the Baseline

Run `analyze.sh` against each published chapter and record the results:

```bash
for chapter in story/chapter*/[0-9]*chapter.md; do
    echo "=== $(basename "$chapter") ==="
    bash resources/analyze.sh "$chapter"
    echo ""
done > baseline_report.txt
```

From the collected results, note:

- **Sentence length range** — what's the typical mean and standard deviation across chapters? A chapter with mean sentence length 2 standard deviations from the project average is worth investigating.
- **Opener distribution** — what's the normal pronoun-start percentage? First-person chapters will naturally be higher than third-person chapters, so compare within POV type.
- **Dialogue ratio** — what range do conversation-heavy chapters fall in vs action chapters? This gives you genre-appropriate expectations for new scenes.
- **Repetition baseline** — every author has words they lean on. The baseline tells you which repetitions are voice and which are unintentional echoes.

## Comparing a Draft

Run the same script against the draft, then compare section by section against the baseline. Look for:

- **Metrics that fall outside the project's established range** — these are investigation triggers, not automatic problems. A chapter that breaks pattern might be doing so intentionally (a tense scene with shorter sentences, a reflective passage with longer ones).
- **Sudden shifts within a single document** — if the first half of a chapter has dramatically different metrics than the second half, that's worth examining. It may indicate a voice drift, especially in AI-assisted drafts where the model's tendencies gradually override the project style.
- **POV consistency** — pronoun distribution should match the declared POV. A first-person chapter where third-person pronouns spike in certain sections may have slipped POV.

## What the Baseline Can't Tell You

The baseline captures mechanical patterns, not quality. A draft that matches every metric perfectly can still be lifeless prose. A draft that deviates dramatically might be the best chapter in the project. The baseline helps you ask "is this consistent with the project's voice?" — the answer to "is this good?" requires human judgment.

## Updating the Baseline

When new chapters are published and approved, add them to the baseline. The baseline should represent the project as it currently stands, not a frozen snapshot from chapter 1. Author voice evolves — the baseline should track that evolution.

If the project has distinct voices (different POV characters, different narrative modes), maintain separate baselines per voice/mode. Comparing a third-person Fuji chapter against first-person Amber chapters will produce misleading deviations.

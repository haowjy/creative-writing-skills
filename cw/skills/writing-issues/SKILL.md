---
name: writing-issues
description: >
  Logging and referencing writing issues — craft problems, tics, inconsistencies,
  and structural concerns found during analysis, critique, or review. Use when
  an agent identifies something worth tracking beyond a single critique report:
  repeated tics across chapters, inconsistencies that affect multiple scenes,
  structural problems that need the author's attention, or patterns that should
  be fixed in revision.
---

# Writing Issues

Issues are writing problems worth tracking beyond a single critique report. A critic finding a pacing problem in one draft produces a critique finding. A critic noticing the same pacing problem across three chapters produces an issue — it's a pattern that won't be fixed by revising one scene.

## When to Log an Issue

Log when the problem is:

- **Recurring** — the same tic, habit, or weakness appears across multiple chapters or scenes. A single instance is a critique finding; a pattern is an issue.
- **Structural** — affects the project's architecture, not just one passage. Scene-type technique that doesn't scale, emotional register that's inconsistent across the arc, a narrative device approaching its shelf life.
- **Worth tracking separately from the content it appears in** — the author might want to address it in a dedicated revision pass rather than fixing it inline during the next draft.

Don't log every critique finding as an issue. A scene that runs long is a critique note. A pattern of scenes running long in the middle third of every chapter is an issue.

## Where Issues Live

`$MERIDIAN_FS_DIR/issues/` — one file per issue. Issues persist across work items because they're project-level concerns, not scoped to a single draft or revision cycle.

## What to Include

Each issue file should contain enough for someone encountering it later to understand the problem without re-reading every chapter:

- **What the issue is** — specific and concrete, not "pacing could be better"
- **Evidence** — quotes, counts, chapter references. The evidence is what makes it an issue rather than an opinion.
- **Scope** — what's affected. Specific chapters, a scene type across all chapters, a character's dialogue in certain situations.
- **Severity or priority** — how much it damages the reader's experience. A tic that appears 5 times is less urgent than a structural inconsistency that undermines a character arc.

## Checking for Duplicates

Before creating a new issue, check what already exists in `$MERIDIAN_FS_DIR/issues/`. The same problem discovered independently by different agents (a critic and a style-creator, say) should be one issue with combined evidence, not two separate files saying the same thing.

If an existing issue covers the same ground, update it with new evidence rather than creating a duplicate.

## Referencing Issues

When a critique report or style analysis identifies something that's already a tracked issue, reference it rather than re-describing it: "this is another instance of the emotional inconsistency issue (see `$MERIDIAN_FS_DIR/issues/emotional-inconsistency.md`)." This connects individual findings to the larger pattern.

## Closing Issues

When an issue has been addressed — the tics edited out, the inconsistency resolved, the structural problem fixed — the file stays but gets marked as resolved with a note on what changed. Keeping resolved issues provides a record of what was caught and fixed, which helps calibrate future analysis.

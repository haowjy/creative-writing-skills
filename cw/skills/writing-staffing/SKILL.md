---
name: writing-staffing
description: >
  Dispatch reference for composing writing teams. Teaches which skills to
  load for each subagent, which resources to reference, and when to fan out.
  Load when staffing a workflow.
---

# Writing Staffing

Each subagent has its own skill set. This skill teaches what *extra* skills
to load and reference when dispatching work.

## Dispatch Reference

### `@writer`

Extra skills: `/character-sim` for voice fidelity, `/shared-dao` for
project vocabulary.

Reference: name the production mode from `/creative-writing-modes` →
`resources/prose-modes.md` (fresh draft, revision, bridge, alternate take,
line polish). Point to `/creative-writing-craft` →
`resources/prose-writing.md` or `resources/scene-construction.md` when
relevant. Include style files, character state, and continuity anchors.

One writer per scene — voice consistency degrades when multiple writers
handle adjacent content.

### `@critic`

Extra skills: `/creative-writing-craft` for prose/voice focus, `/shared-dao`
for vocabulary checks.

Assign a focus area: structure, character, voice, prose, or continuity.
Include style files for voice critique.

Fan out with different focus areas simultaneously. Scale to stakes:
1–2 for low-stakes, 3 for standard chapters, 4–5 for pivotal scenes with
duplicated coverage on the critical dimension.

### `@editor`

Name the edit level: editorial review, developmental, line edit, copyedit,
proofreading. Point to `/story-review` → `resources/editorial-review.md` for
holistic pass, or the specific edit-level resource.

Use when the draft needs a priority order across concerns. For depth on
one dimension, use `@critic`.

### `@continuity-checker`

Include the draft plus canon, timeline, character state, and vocab files.
More expensive than a critic with continuity focus — reads broadly. Use the
critic for routine checks, the continuity-checker for deep validation.

### `@brainstormer`

Extra skills: `/character-sim` for character arcs, `/creative-research` for
real-world grounding.

Fan out on different *angles*, not the same angle. Three perspectives
beats five instances of one.

### `@outliner`

Outlining starts after direction is chosen — use `@brainstormer` first.
The outliner's output feeds the writer.

### `@style-creator`

Include sample chapters or existing style files. Point to
`/creative-writing-craft` → `resources/style-analysis.md`.

### `@reader-sim`

Extra skills: `/character-sim` when the reader persona is a specific
character type.

Specify the reader persona and knowledge boundary (what has this reader
already read). Include the draft.

Run after the write/critique loop converges, before presenting to the
author. A scene can be technically clean and leave a reader cold.

### `@character-sim`

Include character state and voice/style files. Specify the scenario or
relationship to explore. Fan out for multi-character scenes.

### `@web-researcher`

Specify the question, story context, and what the story currently assumes
so the researcher can flag contradictions.

## Effort Scaling

Scale critic coverage to stakes. Knowledge maintenance waits until direction
or chapters settle. Reader-sim runs after the write/critique loop converges.

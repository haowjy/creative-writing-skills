---
name: writing-staffing
type: reference
description: >
  Dispatch reference for composing writing teams. Teaches which extra skills
  to attach via --skills, which resources to reference in spawn prompts, and
  when to fan out. Load when staffing a workflow.
model-invocable: false
---

# Writing Staffing

Each agent loads its core skills from its YAML. This skill teaches what
*extra* to attach and reference when spawning.

## Dispatch Reference

### `@writer`

Extra `--skills`: `character-sim` for voice fidelity, `shared-dao` for
project vocabulary.

Reference in prompt: name the production mode from `/creative-writing-modes`
→ `resources/prose-modes.md` (fresh draft, revision, bridge, alternate take,
line polish). Point to `/creative-writing-craft` → `resources/prose-writing.md`
or `resources/scene-construction.md` when relevant. Attach style files,
character state, and continuity anchors via `-f`.

One writer per scene — voice consistency degrades when multiple writers
handle adjacent content.

### `@critic`

Extra `--skills`: `creative-writing-craft` for prose/voice focus,
`shared-dao` for vocabulary checks.

Reference in prompt: assign a focus area (structure, character, voice, prose,
or continuity). Attach style files via `-f` for voice critique.

Fan out with different focus areas simultaneously. Scale to stakes:
1–2 for low-stakes, 3 for standard chapters, 4–5 for pivotal scenes with
duplicated coverage on the critical dimension.

### `@editor`

Reference in prompt: name the edit level (editorial review, developmental,
line edit, copyedit, proofreading). Point to `/story-review` →
`resources/editorial-review.md` for holistic pass, or the specific
edit-level resource.

Use when the draft needs a priority order across concerns. For depth on
one dimension, use `@critic`.

### `@continuity-checker`

Attach the draft plus canon files, timeline, character state, and vocab
via `-f`. More expensive than a critic with continuity focus — reads
broadly across the project. Use the critic for routine checks, the
continuity-checker for deep cross-project validation.

### `@brainstormer`

Extra `--skills`: `character-sim` for character arcs, `creative-research`
for real-world grounding.

Fan out on different *angles*, not the same angle. Three perspectives
beats five instances of one.

### `@outliner`

Outlining starts after direction is chosen — use `@brainstormer` first.
The outliner's output feeds the writer.

### `@style-creator`

Attach sample chapters or existing style files via `-f`. Point to
`/creative-writing-craft` → `resources/style-analysis.md`.

### `@reader-sim`

Extra `--skills`: `character-sim` when the reader persona is a specific
character type.

Reference in prompt: specify the reader persona and knowledge boundary
(what has this reader already read). Attach the draft via `-f`.

Run after the write/critique loop converges, before presenting to the
author. A scene can be technically clean and leave a reader cold.

### `@character-sim`

Attach character state and voice/style files via `-f`. Specify the scenario
or relationship to explore. Fan out for multi-character scenes.

### `@web-researcher`

Reference in prompt: the specific question, story context, and what the
story currently assumes (so the researcher can flag contradictions).

### `@kb-lead`

Extra `--skills`: `story-memory` for fiction-specific fact categories and
artifact layout.

Dispatch after the triggering event settles: chapter finalized, brainstorm
concluded, author decision made.

## Effort Scaling

Scale critic coverage to stakes. Knowledge maintenance waits until direction
or chapters settle. Reader-sim runs after the write/critique loop converges.

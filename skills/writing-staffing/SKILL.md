---
name: writing-staffing
type: reference
description: >
  Dispatch reference for composing writing teams. Teaches which extra skills
  to attach, which resources and files to name in specialist briefs, and when
  to fan out versus run parallel lanes. Load when staffing a workflow.
model-invocable: false
---

# Writing Staffing

Each agent loads its core skills from its definition. This skill teaches what
*extra* to attach and reference when delegating.

## Model Selection

Agent defaults are usually correct. When overriding or selecting models for
additional lanes, match the model to the work: creative taste and high-stakes
critique need judgment; outlining and cross-document checks need structured
synthesis; bulk gathering and mechanical checks can use a cheaper model when
later synthesis will catch misses.

For model-diverse fan-out, choose two available model families with different
blind spots. Check the live model catalog and model-specific prompting guidance
at dispatch time rather than assuming which models or routes are available.

**Fan-out** gives the same question and files to different model families for
independent judgment. Reserve it for high-stakes calls where model diversity
can reveal different blind spots. **Parallel lanes** use different prompts or
focus areas; use each agent's default model unless a lane needs a capability it
lacks.

## Dispatch Reference

### `@writer`

Attach `/character-sim` for voice fidelity and `/shared-dao` for project
vocabulary.

Name the production mode from `/creative-writing-modes` →
`resources/prose-modes.md` (fresh draft, revision, bridge, alternate take,
line polish). Point to `/creative-writing-craft` →
`resources/prose-writing.md` or `resources/scene-construction.md` when relevant.
Name the style and character-state files for everyone who appears, plus the
continuity anchors.

One writer per scene — voice consistency degrades when multiple writers handle
adjacent content.

### `@critic`

Attach `/creative-writing-craft` for prose or voice focus and `/shared-dao` for
vocabulary checks.

Assign a focus area: structure, character, voice, prose, or continuity. Name the
style file for voice critique and character-state files for character or
continuity focus.

Run different focus areas as parallel lanes. Scale to stakes: 1–2 for
low-stakes, 3 for standard chapters, 4–5 for pivotal scenes with duplicated
coverage on the critical dimension.

For a pivotal scene or disputed judgment, fan out the same critical dimension
across two strong model families, then synthesize the disagreement.

### `@editor`

Name the edit level: editorial review, developmental, line edit, copyedit, or
proofreading. Point to `/story-review` → `resources/editorial-review.md` for a
holistic pass, or the specific edit-level resource.

Use when the draft needs a priority order across concerns. For depth on one
dimension, use `@critic`.

### `@continuity-checker`

Name the draft plus canon, timeline, character-state, and vocabulary files.
This agent is more expensive than a critic with continuity focus because it
reads broadly across the project. Use the critic for routine checks and the
continuity checker for deep cross-project validation.

### `@brainstormer`

Attach `/character-sim` for character arcs and `/creative-research` for
real-world grounding.

Run parallel lanes on different *angles*, not the same angle. Three perspectives
beat five instances of one.

### `@outliner`

Outlining starts after direction is chosen — use `@brainstormer` first. The
outliner's output feeds the writer.

### `@style-creator`

Name sample chapters or existing style files. Point to
`/creative-writing-craft` → `resources/style-analysis.md`.

### `@reader-sim`

Attach `/character-sim` when the reader persona is a specific character type.
Specify the reader persona and knowledge boundary: what this reader has already
read. Name the draft.

Run after the write/critique loop converges, before presenting to the author. A
scene can be technically clean and leave a reader cold.

### `@character-sim`

Name character-state and style files. Specify the scenario or relationship to
explore. Use one parallel lane per character or perspective for independent
exploration; use one shared simulation when testing their interaction.

### `@web-researcher`

Specify the question, story context, and what the story currently assumes so
the researcher can flag contradictions.

### `@kb-lead`

Attach `/story-memory` for fiction-specific fact categories and artifact
layout. Delegate after the triggering event settles: a chapter is finalized, a
brainstorm concludes, or the author makes a decision.

## Effort Scaling

Scale critic coverage to stakes. Knowledge maintenance waits until direction or
chapters settle. Reader simulation runs after the write/critique loop converges.

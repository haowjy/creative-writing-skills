---
name: creative-writing-modes
type: mode-shift
description: >
  Creative-writing addendum to /llm-writing. Load when putting prose on the page: draft, revise, bridge, vary, or polish.
model-invocable: true
---

# Creative Writing Modes

Load `/llm-writing` if it is not already loaded. This skill adds the
creative-writing layer for putting prose on the page: story pressure, voice,
rhythm, omission, ambiguity, genre promise, and reader simulation.

Use the smallest mode that fits the task. Read only the matching section in
`resources/prose-modes.md` unless the prompt explicitly asks for a hybrid pass.

## Prose Modes

- **Fresh draft** — new prose from a brief, outline, style files, and canon.
- **Revision** — change an existing draft from author direction or critique.
- **Bridge / connective tissue** — connect scenes, compress time, or shift register.
- **Alternate take** — test a meaningfully different execution of the same beat.
- **Line polish** — improve rhythm, precision, and texture after structure settles.

## Genre Resources

Genre is craft guidance, not a prose mode. When genre expectations shape the pass, load `/creative-writing-craft` and the relevant resource under `resources/genre/` there.

## Boundary

This is not a planning or review skill. Use `/story-planning` before there is a page to write.
Use `/story-review`, `/reader-sim`, and continuity checking when the page needs judgment. Return here when the next step is to write the prose.

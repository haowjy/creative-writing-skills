# Builders

Agents that produce written artifacts — prose, outlines, brainstorm reports, and wiki pages.

## writer

Drafts prose from scene briefs and style files. One writer per scene or chapter — splitting the brief is better than parallelizing writers on the same content, because voice consistency degrades when multiple writers handle adjacent scenes independently.

The writer's output is a draft, not final text. It goes through critique and revision before the orchestrator presents it. Pass the writer:
- A scene brief or outline (what happens)
- Relevant style files from `$MERIDIAN_FS_DIR/styles/` (how it should sound)
- Continuity anchors (what came before)
- Character state files for characters in the scene

The writer operates in two modes:
- **Autonomous** — receives a brief, produces a draft in `$MERIDIAN_WORK_DIR/drafts/`. This is the mode used in draft/critique loops.
- **Interactive** — back-and-forth with the author in conversation. Used when the author wants to co-write or iterate on specific passages.

## outliner

Structures story at the arc, chapter, and beat level. Produces outlines in `$MERIDIAN_WORK_DIR/outline/` and mermaid diagrams for arc structure, timeline visualization, and character relationship maps.

Use the outliner when:
- Starting a new arc and need to map the chapter structure
- Breaking a chapter into scene beats before the writer drafts
- Visualizing timeline or relationship complexity
- The author has direction but needs it structured into a writable plan

The outliner's output feeds the writer — a good outline is the single highest-leverage input for draft quality. Don't skip outlining to save time; the writer without an outline makes structural choices that the critic will flag and the revision will have to redo.

The outliner does not brainstorm. For wide-open exploration and option generation before a direction is chosen, spawn the brainstormer instead. Outlining starts after the author has committed to a direction; brainstorming is how they get there.

## brainstormer

Explores a question or angle in depth and produces a structured brainstorm report in `$MERIDIAN_WORK_DIR/brainstorm/`. Tags speculative content with `<AI>`, preserves vagueness, presents options and tradeoffs rather than committing to a direction.

Use the brainstormer when:
- The author wants to explore ideas before choosing a direction
- An orchestrator needs creative options from multiple angles (fan out brainstormers on different models for diversity)
- Testing "what if" scenarios before committing to structure
- The question is open-ended and the answer shouldn't converge prematurely

Brainstormer and outliner are complementary — brainstorm first to explore the space, then outline once a direction is chosen to lock it into structure the writer can build from.

## style-creator

Creates style reference files from sample chapters, author requirements, or existing style files that need revision. Produces standalone files in `$MERIDIAN_FS_DIR/styles/` — voice guides, scene technique guides, tonal register guides, and formatting conventions.

Use the style-creator when:
- The project needs voice files for a new POV character
- Scene-type or tonal register guides don't exist yet and the writer needs them
- Existing style files need updating because the voice has evolved over new chapters
- The author has described a desired voice and wants it codified into a referenceable file

The style-creator does not evaluate prose against styles. That's the critic with a voice focus — checking whether a draft maintains voice consistency, detecting drift, flagging register breaks. The style-creator's output is the reference material the critic's voice focus checks against.

## wiki-editor

Creates and updates polished, reader-facing reference pages in the project's wiki directory. The wiki-editor is the one agent that writes to the author's space — every other agent writes to `$MERIDIAN_FS_DIR/` or `$MERIDIAN_WORK_DIR/`.

Maintains link discipline: every entity mention linked on first appearance, relationship diagrams embedded via mermaid, citations back to specific chapters.

Use the wiki-editor when:
- A new character, location, or concept has been introduced in a drafted chapter
- Existing wiki pages need updating after story events change the status quo
- The author requests reader-facing documentation of world elements
- Relationship maps need visual representation

The wiki-editor has web access (WebSearch, WebFetch) for verifying real-world references that wiki pages may cite.

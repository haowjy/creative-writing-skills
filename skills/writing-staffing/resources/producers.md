# Producers

Agents that write or gather: prose, options, outlines, style files, research,
simulated conversation, and kb updates.

## `@writer`

Spawn it for the prose passes `/creative-writing-muse` hands off. Name the mode from `/creative-writing-craft`
`resources/prose-modes.md` (fresh draft, revision, bridge, alternate take, line
polish) and the path to write to. Tell it to load `/character-sim` for voice
fidelity and `/shared-dao` when the scene uses project vocabulary.

One writer per scene: voice consistency degrades when several writers handle
adjacent content.

## `@brainstormer`

Run parallel lanes on different angles, not the same angle: three perspectives
beat five instances of one. Tell it to load `/character-sim` for character
arcs and `/creative-research` for real-world grounding.

## `@outliner`

Outlining starts after the author confirms direction; brainstorm first. The
outline feeds the writer.

## `@style-creator`

Pass sample chapters or existing style files, or the author's stated voice
goals when there are no samples.

## `@character-sim`

Name the scenario or relationship to explore. Run one lane per character or
perspective for independent exploration, or one shared simulation to test how
they interact.

## `@web-researcher`

Name the question, the story context, and what the story currently assumes, so
it can flag contradictions.

## `@kb-lead`

Tell it to load `/story-memory` for the fiction-specific fact categories and
kb layout. When to spawn it and what its brief carries are in
`/story-workflow` § After Work Settles.

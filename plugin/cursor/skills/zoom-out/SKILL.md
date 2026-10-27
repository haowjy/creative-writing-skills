---
name: zoom-out
description: 'Use when orienting in an unfamiliar area: fans out parallel explorers across structure, knowledge, and history, then synthesizes one orientation map.'
metadata:
  type: mode-shift
alwaysApply: false
---

# Zoom Out

Load `/creative-writing-skills:qi-layer` if it isn't already loaded.

Orient in an unfamiliar area by fanning out parallel explorers, each covering a different angle, then synthesizing their reports into one orientation map. A single explorer sees one slice; zoom-out covers structure *and* knowledge *and* history at once, so the picture isn't skewed by one lens.

Use when starting in an unfamiliar subsystem, picking up someone else's work, or when the user says "orient me" / "what's the lay of the land here."

## Fan Out

Spawn in parallel the angles the area has material for, each scoped to one angle and one question.

- **Structure** (`@explorer`): how the area's parts connect and where behavior lives; in code, callers, dependencies, module boundaries, entry points.
- **Documented knowledge** (`@explorer` over the knowledge base): what's been written about this area, including architecture, guides, synthesized research.
- **Decision history** (`@session-miner`): why it's shaped this way. Prior choices, rejected alternatives, constraints discovered.
- **Domain concepts** (`@explorer`): the vocabulary in use (KB vocab pages, `.context/CONTEXT.md`, AGENTS.md).

Give each explorer one angle, scoped with concrete path or topic targets: the value is independent coverage.

## Synthesize

Read the reports and produce one orientation map, not stitched-together dumps:

- **What this is**: the area's purpose and boundaries, in two or three sentences.
- **Structure**: the parts and interfaces that matter and how they connect (a mermaid diagram if the shape is spatial).
- **Why it's like this**: the decisions and constraints that explain the current shape.
- **Vocabulary**: the terms needed to speak about it precisely.
- **Open threads**: gaps, debt, or unresolved questions the explorers surfaced.

When reports contradict each other, resolve it rather than listing both, by what each source governs: the thing itself (the code, the data, the manuscript) shows its current state, and a settled decision shows intent. A doc that misdescribes current state is stale (note it); a gap between current state and settled intent is a divergence to report. Keep the map tight: the goal is a reader who can now navigate the area, not an exhaustive transcript.

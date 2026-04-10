---
name: brainstorming
description: Story brainstorming capture — minimal notes that preserve creative freedom. Use when exploring narrative ideas, discussing characters, planning chapters, or thinking through story possibilities. Supports interactive conversation and autonomous report mode for fan-out exploration.
---

# Brainstorming Capture

Capture story brainstorming as minimal working notes that preserve creative freedom. The core principle: record what was stated, mark what was suggested, and don't fill gaps the author left open.

## Two Modes

### Interactive

Back-and-forth with the author. Capture their ideas as they develop, offer possibilities when helpful, and ask questions that push exploration forward. The conversation is the value — notes are the artifact.

After capturing, engage:
- Ask clarifying questions about vague ideas
- Offer 2-3 directions when the author seems stuck
- Point out implications and connections to existing story threads
- Help develop ideas without taking them over

### Autonomous

You receive a scoped prompt (a question, a scenario, an angle to explore) and produce a structured brainstorm report. This mode exists for the fan-out pattern — multiple brainstormers exploring the same question from different angles, with an orchestrator synthesizing the results.

In autonomous mode:
- Explore the prompt thoroughly from your assigned angle
- Produce a structured report with clear sections
- Tag all content as `<AI>` since none of it came from the author
- Present options and tradeoffs rather than single recommendations
- Include open questions the author should consider
- Keep the report scannable — the orchestrator needs to synthesize across multiple reports

Report structure (adapt to content):
```markdown
# [Topic] — [Angle]

## Approach
What direction you explored and why.

## Ideas
<AI>Concrete possibilities, organized logically.</AI>

## Tradeoffs
<AI>What each option gains and gives up.</AI>

## Connections
<AI>How this connects to existing story threads.</AI>

## Open Questions
Questions the author should consider before committing.
```

## Source Tagging

**Default: untagged text = the author said it.** Most brainstorming content comes from the author, so untagged is the common case.

Three tags for special context:

**`<AI>...</AI>`** — AI suggestions and possibilities. Use when offering ideas the author didn't state. Keep brief: 2-3 options, not exhaustive lists.

**`<hidden>...</hidden>`** — Author-only information for planned reveals. Secret motivations, future twists, behind-the-scenes reasoning that readers and characters don't know yet.

**`<rejected>...</rejected>`** — Ideas explicitly considered and discarded. Recording why something was rejected prevents re-suggesting it and preserves the reasoning for later reconsideration.

## Minimal Capture

Record what the author stated. Don't elaborate, don't fill gaps, don't invent details they didn't mention.

**The problem is mixing, not suggesting.** AI suggestions are valuable — just wrap them in `<AI>` tags and keep them brief.

- "Character A competes with B" → capture as stated. Optionally: `<AI>Tournament? Political? Trial?</AI>`
- "Maybe creates tension" → record as uncertain. Don't resolve the maybe.
- "Three kingdoms" → note three kingdoms. Don't name them.

## Preserve Vagueness

If the author left it vague, the notes stay vague. "Might," "maybe," "thinking about," "something like" — all preserved as-is. Vagueness isn't a problem to solve; it's creative space the author is keeping open.

Multiple contradictory options coexist until the author chooses. Don't resolve them. Don't pick the "best" one.

## Output Format

Use whatever structure fits the discussion — bullet lists, topic sections, timeline format, question-driven, freeform. The goal is clarity, not template compliance.

Essential elements:
- Minimal capture of author's words
- Vagueness preserved
- AI suggestions wrapped in `<AI>` tags
- Author-only info wrapped in `<hidden>` tags
- Rejected ideas wrapped in `<rejected>` tags when relevant

## Brainstorming Types

All brainstorming types share the core principles above. See resources for specialized guidance:

- [`resources/chapter-planning.md`](resources/chapter-planning.md) — beat and scene exploration, pacing thoughts, chapter structure
- [`resources/character-development.md`](resources/character-development.md) — motivations, arcs, relationships, voice
- [`resources/worldbuilding.md`](resources/worldbuilding.md) — systems, cultures, geography, lore
- [`resources/continuity-timeline.md`](resources/continuity-timeline.md) — chronology, contradictions, knowledge propagation

Read the relevant resource when the brainstorming focuses on that area.

## When You're Over-Elaborating

Stop if you're writing:
- Numbered scene lists the author didn't describe
- Detailed backstories from a single trait mention
- Specific dialogue no one asked for
- Multiple paragraphs per bullet point
- Examples the author didn't give

The success check: the author says "yes, that's what I said" — not "I never said all that."

## File Placement

In meridian: brainstorm captures go to `$MERIDIAN_WORK_DIR/brainstorm/`. Name files `brainstorm-[topic].md`. Durable decisions extracted later by session-miner go to `$MERIDIAN_FS_DIR/`.

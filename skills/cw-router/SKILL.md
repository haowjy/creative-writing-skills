---
name: cw-router
description: Quick guide to choosing the right creative writing skill or migrated Codex agent-role skill for a specific task — brainstorming vs documentation, critique vs writing, analysis vs architecture, etc.
---

# Creative Writing — Quick Reference

Quick guide to choosing the right skill or agent for your task.

Codex note: Claude/Mars agents have been migrated as Codex skills named
`cw-agent-<agent-name>`. When older docs say "spawn writer" or "writer
agent", use `cw-agent-writer`; when it says `story-orchestrator`, use
`cw-agent-story-orchestrator`. These are role modes in Codex, not native
Claude agent processes.

Claude slash commands have also been migrated as command-entry skills:
`/bs` -> `cw-command-bs`, `/write` -> `cw-command-write`, `/wiki` ->
`cw-command-wiki`, and `/critique` -> `cw-command-critique`.

---

## Skills (knowledge loaded into context)

### command-entry skills
**Use for:** Explicit Claude-style command equivalents in Codex.
**Commands:** `cw-command-bs`, `cw-command-write`, `cw-command-wiki`, `cw-command-critique`
**Key trait:** Lightweight entrypoints that route to the matching writing skill and migrated agent-role skill.

### brainstorming
**Use for:** Exploring ideas, figuring things out, thinking through options
**Creates:** Skeletal working notes with [TBD] markers and source tags
**Handles:** Story/plot brainstorming, chapter planning, worldbuilding exploration, character development, timeline and continuity work
**Key trait:** Multiple options coexist, preserves vagueness, exploratory

### prose-writing
**Use for:** Actually writing story prose in your style
**Writes:** Scenes, chapters, dialogue, narrative prose
**Key trait:** Creates actual story text, matches your voice

### prose-critique
**Use for:** Getting feedback on written chapters/scenes
**Analyzes:** Plot and pacing, character development, prose quality, story structure
**Key trait:** Feedback on existing writing, not creating content

### wiki-docs
**Use for:** Documenting finalized decisions, creating canonical reference (wiki pages)
**Creates:** Polished, reader-ready wiki/documentation pages with citations
**Key trait:** Single version, no [TBD], encyclopedic/wiki tone

### story-architecture
**Use for:** Structural analysis — arc shape, tension curves, pacing across chapters
**Key trait:** Zoomed-out view of story structure, not line-level feedback

### story-context
**Use for:** Loading relevant story context (characters, locations, prior events) before a task
**Key trait:** Context-gathering, not content-creating

### story-decisions
**Use for:** Recording and retrieving authorial decisions about the story
**Key trait:** Decision log, not brainstorming

### writing-principles
**Use for:** Understanding what makes fiction work — four reward channels, documented AI failure modes, craft tradition
**Key trait:** Foundational theory, not task-specific guidance

### writing-artifacts
**Use for:** Understanding the artifact types the system produces and where they go
**Key trait:** File conventions and output formats

### writing-staffing
**Use for:** Understanding which agent handles what, and when to fan out across multiple agents
**Key trait:** Agent roster and coordination patterns

---

## Agents (Codex role skills)

**story-orchestrator** — Primary entry point. Coordinates brainstorming, drafting, critique, and knowledge maintenance across all agents.

**draft-orchestrator** — Runs the draft/critique loop: spawns writers, critics, and reader-sims in parallel.

**knowledge-orchestrator** — Coordinates knowledge maintenance: wiki updates, graph maintenance, continuity checks.

**writer** — Writes prose in the project's style.

**critic** — Provides structured critique across the four reward channels.

**reader-sim** — Simulates a reader's experience and reports per-channel engagement.

**character-sim** — Simulates a character's behavior for dialogue testing and scene exploration.

**brainstormer** — Wide-open option generation on a scoped question.

**outliner** — Structural decomposition into beat sheets and arc maps.

**explorer** — Fast codebase/project exploration — finds files, searches content, answers structural questions.

**researcher** — Web research for worldbuilding, fact-checking, and reference gathering.

**continuity-checker** — Checks draft against established canon for consistency errors.

**wiki-editor** — Creates and maintains wiki documentation pages.

**graph-maintainer** — Updates the project knowledge graph from new content.

**chronicler** — Records session decisions and discoveries into persistent notes.

**session-miner** — Mines past session transcripts for unreported decisions and context.

**style-creator** — Analyzes existing prose to create a style guide.

---

## Key Distinction: Brainstorm vs Documentation

**Still figuring it out?** → **brainstorming** skill (or use **cw-agent-brainstormer**)
- "Maybe X, or Y, or Z?"
- [TBD] markers everywhere
- Multiple versions coexist

**You've decided and it's ready to document?** → **wiki-docs** skill (or use **cw-agent-wiki-editor**)
- Single authoritative version
- Polished and reader-ready
- No [TBD] markers

---

## Common Scenarios

| Request | Skill or Agent |
|---|---|
| "Exploring worldbuilding ideas for my magic system" | brainstorming |
| "Finalized my magic system, want to document it" | wiki-docs |
| "Thinking through how this chapter should flow" | brainstorming |
| "Write this chapter" | prose-writing (or cw-agent-writer) |
| "Wrote this chapter, want feedback" | prose-critique (or cw-agent-critic) |
| "Character profile for my protagonist" | wiki-docs if finalized, brainstorming if exploring |
| "Analyze the pacing across my chapters" | story-architecture |
| "Check this draft for continuity errors" | cw-agent-continuity-checker |
| "Run a full draft/critique loop" | cw-agent-story-orchestrator |

---

## Decision Tree

```
Are you writing story prose?
  └─ Yes → prose-writing / cw-agent-writer
  └─ No ↓

Do you want feedback on something written?
  └─ Yes → prose-critique / cw-agent-critic
  └─ No ↓

Are you figuring things out or have you decided?
  └─ Figuring out → brainstorming / cw-agent-brainstormer
  └─ Decided → wiki-docs / cw-agent-wiki-editor

Need structural/pacing analysis?
  └─ Yes → story-architecture

Need a custom writing style?
  └─ Yes → cw-agent-style-creator
```

---

## Still Unsure?

1. **Exploring/uncertain?** → brainstorming
2. **Finalized/polished?** → wiki-docs
3. **Need feedback?** → prose-critique
4. **Actually writing?** → prose-writing
5. **Need the full pipeline?** → cw-agent-story-orchestrator

When in doubt, start with brainstorming. You can always move to docs later when things are decided.

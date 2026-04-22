---
name: cw-router
description: Quick guide to choosing the right creative writing skill or agent. Use when you need help deciding which skill to load or which agent to spawn for a specific task — brainstorming vs documentation, critique vs writing, analysis vs architecture, etc.
---

# Creative Writing — Quick Reference

Quick guide to choosing the right skill or agent for your task.

---

## Skills (knowledge loaded into context)

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

### prose-analysis
**Use for:** Quantitative analysis of prose patterns — sentence rhythm, word frequency, voice consistency
**Key trait:** Diagnostic data, not subjective critique

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

### knowledge-graph
**Use for:** Maintaining the project knowledge graph (characters, locations, relationships, events)
**Key trait:** Structured data maintenance

### writing-principles
**Use for:** Understanding what makes fiction work — four reward channels, documented AI failure modes, craft tradition
**Key trait:** Foundational theory, not task-specific guidance

### writing-artifacts
**Use for:** Understanding the artifact types the system produces and where they go
**Key trait:** File conventions and output formats

### writing-staffing
**Use for:** Understanding which agent handles what, and when to fan out across multiple agents
**Key trait:** Agent roster and coordination patterns

### python-tool-runner
**Use for:** Running bundled Python helper scripts
**Key trait:** Prefers `uv run`, checks for `uv`, confirms before installation

---

## Agents (spawned for independent work)

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

**Still figuring it out?** → **brainstorming** skill (or spawn a **brainstormer** agent)
- "Maybe X, or Y, or Z?"
- [TBD] markers everywhere
- Multiple versions coexist

**You've decided and it's ready to document?** → **wiki-docs** skill (or spawn a **wiki-editor** agent)
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
| "Write this chapter" | prose-writing (or spawn writer) |
| "Wrote this chapter, want feedback" | prose-critique (or spawn critic) |
| "Character profile for my protagonist" | wiki-docs if finalized, brainstorming if exploring |
| "Analyze the pacing across my chapters" | story-architecture |
| "Check this draft for continuity errors" | spawn continuity-checker |
| "Run a full draft/critique loop" | spawn story-orchestrator |

---

## Decision Tree

```
Are you writing story prose?
  └─ Yes → prose-writing / writer agent
  └─ No ↓

Do you want feedback on something written?
  └─ Yes → prose-critique / critic agent
  └─ No ↓

Are you figuring things out or have you decided?
  └─ Figuring out → brainstorming / brainstormer agent
  └─ Decided → wiki-docs / wiki-editor agent

Need structural/pacing analysis?
  └─ Yes → story-architecture

Need a custom writing style?
  └─ Yes → spawn style-creator agent
```

---

## Still Unsure?

1. **Exploring/uncertain?** → brainstorming
2. **Finalized/polished?** → wiki-docs
3. **Need feedback?** → prose-critique
4. **Actually writing?** → prose-writing
5. **Need the full pipeline?** → spawn story-orchestrator

When in doubt, start with brainstorming. You can always move to docs later when things are decided.

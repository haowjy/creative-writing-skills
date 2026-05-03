---
description: >
  Maintaining the story knowledge base — creating, updating, and organizing
  wiki-style reference pages in kb/. Use when capturing finalized story
  knowledge, updating character profiles, documenting world mechanics, or
  restructuring the kb.
---

# KB Management

The knowledge base (`kb/`) is the project's durable memory. Every agent reads
from it for context. This skill covers how to maintain it well.

## Layers

**Canon** — established facts the story has committed to. Once a chapter is
published/finalized, the facts it establishes are canon. Contradicting canon
breaks reader trust.

**Wiki** — synthesized reference pages. How the magic system works, character
relationships, faction politics. Living documents that evolve as the story
develops.

**Styles** — voice reference files derived from prose samples. The writer
and critic agents depend on these for voice consistency.

**Issues** — tracked writing problems that span multiple chapters (recurring
tics, pacing patterns, continuity errors). See the writing-issues skill.

## Page Conventions

### One Concept Per Document

Each doc covers one coherent topic — one character, one location, one system.
When a doc covers two unrelated topics, split it. When two docs explain the
same thing from different angles, merge or cross-reference.

Name files by what they describe (`fire-magic.md`, `protagonist.md`), not
when they were written (`session-3-notes.md`).

### Organization

```text
kb/
  characters/
    <name>.md              # one file per character
  world/
    <topic>.md             # locations, factions, systems
    <domain>/
      <topic>.md           # nest when a domain has many pages
  timeline/
    <arc-or-period>.md     # chronological entries
  canon/
    <chapter-or-arc>.md    # hard facts per chapter/arc
  styles/
    <style-name>.md        # voice reference files
  issues/
    <issue-name>.md        # tracked writing problems
```

The project's `CLAUDE.md` may customize this. Read it first.

### Linking

Link to related pages with relative paths. Cross-reference instead of
duplicating — one source of truth per concept. A character page links to
the location page for their home, the timeline entry for their arc, etc.

### Readability

Write pages that work in isolation:

- **Self-contained** — enough context that a reader doesn't need three
  other pages first
- **Scannable** — headers, bullets, tables. Bold key terms on first use.
- **Concrete** — specific quotes, chapter references, scene citations
- **Current** — update when the story invalidates or extends what's here

## When to Create vs Update

**Create** a new page when a concept is finalized enough to be referenced
by other agents. Don't create pages for things still in brainstorming.

**Update** an existing page when new chapters establish facts about it,
when the author makes decisions that change it, or when a page has become
stale.

**Split** when a page grows past ~200 lines or covers multiple unrelated
concepts.

## What Belongs in KB vs Work

- Finalized knowledge → `kb/`
- Draft iterations, brainstorm captures, critique reports → `work/`
- Promoted facts after a draft completes → `kb/canon/` or relevant wiki page

The chronicler agent handles routine extraction from completed chapters.
Direct kb edits are for the author or muse when capturing decisions
interactively.

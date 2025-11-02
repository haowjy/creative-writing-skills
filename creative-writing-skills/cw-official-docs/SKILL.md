---
name: cw-official-docs
description: Creative writing skill for creating canonical reference documentation (wikis) for fictional worlds, characters, and story events. Use when creating or updating wiki pages, official documentation, character profiles, location documentation, or lore pages. Creates polished, sourced, encyclopedic reference material.
---

# Official Documentation

Create canonical, sourced wiki pages for your story's characters, locations, events, and lore.

## Purpose

Build authoritative documentation (wiki-style pages) that serves as "single source of truth" for your fictional world. These are polished, cited, encyclopedic reference pages suitable for readers - NOT working notes or brainstorming.

**Can be created before or during writing** for worldbuilding, lore, and reference material that won't all appear in the story itself.

## Documentation vs Brainstorm Notes

**The key distinction:** Documentation = you've decided and it's polished enough to show someone. Brainstorm = you're still figuring it out.

| Documentation | Brainstorm |
|------|------------|
| Single version | Multiple options coexist |
| Polished | Skeletal |
| No [TBD] markers | Source tags throughout |
| Reader-ready | Author's working notes |
| Finalized decisions | Exploratory |

## Core Principles

### 1. Canonical Only

Wiki pages contain ONLY confirmed information:
- Facts from written chapters OR finalized worldbuilding
- Details the author has decided
- Single authoritative version

### 2. Citations Required

Every claim needs a source:
- Chapter references for story facts
- "Worldbuilding document: [filename]" for lore created before writing
- Scene-specific citations when possible

### 3. Encyclopedic Tone

Write like a reference work:
- Third person
- Past tense for completed events, present for current state
- Neutral, factual tone

## Flexible Structure

**Documentation pages aren't templates to fill in** - structure should fit the content.

Some character pages need detailed backstory, others don't. Some locations are just "a tavern in the capital" - that's one paragraph, not 12 sections. Some magic systems need elaborate rules, others are intentionally mysterious.

**Include what matters, skip what doesn't.** Trust your judgment.

See references/page-patterns.md for common patterns and examples - not mandatory structures.

## Creating Documentation Pages

1. **Decide what needs documenting** - Character? Location? System? Event?
2. **Choose relevant structure** - See references/page-patterns.md for common patterns
3. **Write what matters** - Skip irrelevant sections, adapt structure to content
4. **Add citations** - See references/citation-guide.md for formats
5. **Cross-reference** - Link related pages for discoverability

Structure adapts to content - not every page needs every section.

## Using Web Search

Search when helpful for:
- Verifying real-world facts your story references
- Research for worldbuilding elements
- Finding similar fictional documentation/wikis for inspiration
- Checking naming conventions or terminology

## Timing

**You can write documentation pages BEFORE writing story chapters** - just ensure content is finalized and presentation-ready, not exploratory.

**For worldbuilding/lore:** Finalize concept → Create documentation page → Use while writing

**For story events:** Write chapters → Document what happened → Create documentation page

## Teaching Example: Simple vs Complex

**Not every page needs elaborate structure:**

**Simple location (totally valid):**
```markdown
---
title: The Broken Wheel Tavern
type: location
---

# The Broken Wheel Tavern

A run-down tavern in the merchant quarter of Kingsport. Known for cheap ale and cheaper rooms.

The protagonist meets their contact here in Chapter 3.

**References:**
- Chapter 3: First meeting scene
```

**Complex character (when needed):**
```markdown
---
title: Marcus Webb
type: character
status: alive
---

# Marcus Webb

Former military intelligence officer turned information broker in Kingsport.

## Background
Served 15 years in the Royal Intelligence Service before a scandal forced his resignation. Now operates independently, selling information to whoever can pay.

## Appearance
Mid-40s, graying hair, military bearing despite civilian clothes. Distinctive scar across left eyebrow from field injury.

## Role in Story
Acts as information source for the protagonist. Provides critical intelligence about the conspiracy in Chapter 3, then becomes recurring ally throughout Arc 1.

## Key Relationships
- **Sarah Chen**: Former colleague, maintains uneasy trust
- **The protagonist**: Professional relationship, provides information for payment

**References:**
- Chapter 3: First introduction, provides intel
- Chapter 7: Warns protagonist about surveillance  
- Chapter 12: Reveals his own involvement in the conspiracy
```

**Both are valid** - structure fits what needs documenting.

## Skills are Composable

Feel free to combine with other skills when helpful (e.g., using cw-brainstorming while exploring worldbuilding before finalizing into documentation pages).

## File Placement (Claude Code)

1. Check project documentation for organization
2. Common locations: `docs/`, `wiki/`, `docs/reference/`, `reference/`
3. Match existing naming conventions
4. Ask if unclear

## Resources

See:
- `references/page-patterns.md` - Common patterns and examples (not templates)
- `references/citation-guide.md` - How to cite sources
- `references/example-pages.md` - Complete example pages at different complexity levels

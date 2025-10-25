---
name: creative-writing-assistant
description: Comprehensive creative writing assistant for fiction and narrative projects. Helps with writing prose in your style, creating reference documentation (character profiles, world-building, lore), analyzing your writing style, and critiquing story content. Use for any fiction/narrative writing task including drafting, editing, documenting, style analysis, or story critique.
---
# Creative Writing Assistant

## Overview

This skill provides comprehensive support for creative writing projects. It helps you:
- **Write prose** that follows your project's style and conventions
- **Create reference materials** (character profiles, locations, lore documentation)
- **Analyze your writing style** to document patterns and preferences
- **Critique your story** for plot, character, pacing, dialogue, and prose issues

All focused on **fiction and narrative writing**.

## Quick Navigation

Choose what you need help with:

**Writing prose?** → See [Writing Workflow](#writing-workflow)
**Creating reference docs?** → See [Documentation Workflow](#documentation-workflow)
**Want style analysis?** → See [Style Analysis Workflow](#style-analysis-workflow)
**Need story critique?** → See [Story Critique Workflow](#story-critique-workflow)

---

## Writing Workflow

### When to Use
- Drafting new chapters, scenes, or prose
- Editing existing content
- Checking consistency with established content
- Need to follow project-specific guidelines

### How It Works

#### Before Writing: Discover Project Guidelines

1. **Look for convention documentation**:
   - Check root directory for `CLAUDE.md`, `CONVENTIONS.md`, `WRITING.md`, `STYLE.md`
   - These often explain the entire project structure

2. **Find style guide directories**:
   - Common locations: `.cursor/rules/`, `.ai/`, `docs/style/`
   - Identify what guides exist

3. **Identify relevant guides**:
   - Master prose guide
   - Scene-type guides (dialogue, battles, discovery, etc.)
   - Character voice guides
   - Read relevant guides BEFORE writing

4. **Check reference materials**:
   - Character profiles (for voice consistency)
   - World-building docs (for canon facts)
   - Timeline files (for chronology)

5. **Examine existing files for patterns**:
   - File naming conventions
   - YAML frontmatter structure
   - Formatting preferences (em dashes, ellipsis, quotes)
   - Directory organization

#### While Writing

- Maintain POV consistency
- Use project-specific conventions
- Preserve character voices
- Respect established canon
- Format appropriately

#### When Editing

- Identify edit type (line edits, content edits, consistency edits)
- Find relevant project guidance
- Preserve project patterns
- Verify against canon

### Optional Fallback References

If a project has NO style guides, see:
- `references/writing-techniques.md` - General prose techniques
- `references/dialogue-patterns.md` - Dialogue basics
- `references/scene-transitions.md` - Transition techniques

**But always prioritize project-specific guides over these generic references.**

---

## Documentation Workflow

### When to Use
- Creating character profiles
- Documenting locations or world-building
- Writing lore or concept pages
- Building reference materials for your fictional world
- Creating timelines or event documentation

### How It Works

#### Determine Page Type

Different reference types need different structures:
- **Character pages**: Biography, personality, abilities, relationships
- **Location pages**: Description, geography, history, notable features
- **Lore/concept pages**: Definition, mechanics, history, examples
- **Event pages**: Timeline, participants, causes, consequences
- **Item pages**: Description, properties, history, significance
- **Timeline pages**: Chronological event documentation

#### Use Templates

Read `references/page-templates.md` for complete templates showing:
- Required sections for each page type
- YAML frontmatter structure
- Citation formats
- Example structures

#### Write with Consistency

- Use third-person perspective
- Past tense for completed events
- Neutral, encyclopedic tone
- Cite sources (chapter references)
- Link to related pages

#### Citation Management

Read `references/citation-guide.md` for:
- Citation format styles
- How to cite chapters, scenes, pages
- Handling contradictions
- Best practices

#### Examples

See `references/example-pages.md` for complete examples of well-structured wiki pages.

---

## Style Analysis Workflow

### When to Use

**ONLY when explicitly requested** with phrases like:
- "Analyze my writing style"
- "Create a style guide from these samples"
- "Document my writing patterns"
- "Extract my style from this"

**Do NOT trigger** for general writing, editing, or feedback requests.

### How It Works

#### 1. Gather Samples

Request if not provided:
- Minimum: 1,000-2,000 words
- Better: 3,000-5,000 words
- Best: Multiple samples showing different scene types

#### 2. Analyze Systematically

Read `references/analysis-techniques.md` for detailed analysis methods covering:
- Sentence structure (length, variation, fragments)
- Punctuation patterns (em dash, ellipsis, quotes)
- Narrative voice (POV, tense, distance, filters)
- Dialogue style (tags, beats, subtext)
- Descriptive approach (sensory details, metaphors)
- Pacing techniques (scene breaks, paragraph length)
- Word choice (vocabulary, adverbs, repeated phrases)
- Formatting preferences (thoughts, emphasis, breaks)

#### 3. Generate Style Guide

Use `references/style-guide-template.md` to create comprehensive documentation with:
- Overview and distinctive features
- Specific patterns with numbers/frequencies
- Examples from the samples
- Quick reference checklist
- Things to avoid (absent patterns)

#### 4. Deliver Based on Context

**In Claude Code**: Create file in appropriate location or package as skill
**In Claude Chat**: Output document with copy-paste instructions

---

## Story Critique Workflow

### When to Use

**ONLY when explicitly requested** with phrases like:
- "Analyze my story/chapter/plot"
- "Critique this chapter"
- "Review my story structure"
- "What are the problems with this?"
- "Give me feedback on this"

**Do NOT trigger** for general writing help or editing.

### How It Works

#### 1. Clarify the Request

Ask about:
- **Analysis type**: Specific focus or comprehensive?
- **Context**: Genre, audience, draft stage
- **Scope**: Scene, chapter, multiple chapters
- **Specific concerns**: Problem areas to examine

#### 2. Choose Analysis Type(s)

Based on the request, read relevant reference(s):

**Plot & Structure** (`references/plot-structure.md`):
- Story structure frameworks
- Cause and effect chains
- Plot holes and logic gaps
- Setup and payoff
- Arc development
- Common issues: saggy middle, rushed ending

**Character Development** (`references/character-development.md`):
- Character arcs and growth
- Motivation consistency
- Voice distinctiveness
- Character agency
- Complexity and believability
- Common issues: reactive protagonist, flat arc

**Pacing & Flow** (`references/pacing-flow.md`):
- Scene momentum
- Transition smoothness
- Summary vs. scene balance
- Chapter hooks
- Dead space identification
- Common issues: slow opening, flat pacing

**Dialogue Quality** (`references/dialogue-craft.md`):
- Naturalism and authenticity
- Subtext and depth
- Info-dumping issues
- Character voice distinction
- Purpose and efficiency
- Common issues: on-the-nose dialogue, exposition

**Prose & Technical** (`references/prose-technique.md`):
- Sentence clarity and variety
- Show vs. tell balance
- Filter words and passive voice
- Word choice precision
- Purple prose
- Common issues: telling not showing, monotonous rhythm

#### 3. Conduct Analysis

- Be specific with examples
- Be balanced (strengths AND weaknesses)
- Be constructive (suggest solutions)
- Use quotes from the text
- Prioritize major issues
- Consider genre and audience

#### 4. Structure Feedback

```markdown
# Analysis of [Title]

## Overview
[Overall impression, strengths, concerns]

## What's Working Well
[Specific positives with examples]

## Areas for Improvement
### [Category]
**Issue**: [Description]
**Example**: [Quote]
**Suggestion**: [Fix]

## Priority Recommendations
1. [Most important]
2. [Second priority]
3. [Third priority]

## Questions to Consider
[Thought-provoking questions]
```

---

## Decision Tree

Use this to determine which workflow to follow:

```
User request type:
├─ Writing/editing prose → Writing Workflow
├─ Creating character profile/location page/lore → Documentation Workflow
├─ "Analyze my style" / "Document my patterns" → Style Analysis Workflow
└─ "Critique this" / "What's wrong with..." → Story Critique Workflow
```

Multiple workflows can be used in sequence:
- Analyze style, THEN write prose using that style
- Create character profile, THEN write scene with that character
- Critique chapter, THEN edit based on feedback

---

## Best Practices

### For Writing
- Always read project style guides before drafting
- Respect established conventions
- Check canon before adding facts
- Ask when conventions are unclear

### For Documentation
- Use consistent templates within page types
- Cite all sources
- Maintain neutral tone
- Cross-reference related pages

### For Style Analysis
- Need adequate samples (2,000+ words)
- Analyze systematically, not impressionistically
- Quantify patterns where possible
- Show examples for each pattern

### For Story Critique
- Be specific, not vague
- Balance positive and negative
- Consider genre expectations
- Adjust to draft stage
- Provide actionable suggestions

---

## Reference Files

This skill includes comprehensive references organized by workflow:

### Writing References (Optional Fallbacks)
- `writing-techniques.md` - General prose techniques
- `dialogue-patterns.md` - Dialogue basics
- `scene-transitions.md` - Transition techniques

### Documentation References
- `page-templates.md` - Complete templates for all page types
- `example-pages.md` - Well-structured example pages
- `citation-guide.md` - Citation formats and best practices

### Style Analysis References
- `style-guide-template.md` - Template for creating style guides
- `analysis-techniques.md` - Systematic analysis methods

### Story Critique References
- `plot-structure.md` - Structure, causation, arcs
- `character-development.md` - Arcs, motivation, voice, agency
- `pacing-flow.md` - Momentum, transitions, hooks
- `dialogue-craft.md` - Naturalism, subtext, voice
- `prose-technique.md` - Clarity, show vs tell, word choice

All references load on-demand based on what you need.

---

## Integration Philosophy

This skill is designed to be **convention-agnostic**. It:
- Discovers YOUR project structure
- Follows YOUR style guides
- Respects YOUR conventions
- Adapts to YOUR patterns

It does NOT impose a writing style or structure. Every project is different, and this skill helps Claude work with your unique approach.

---

## Remember

- **Writing**: Read project guides first, follow established patterns
- **Documentation**: Use templates, cite sources, maintain consistency
- **Style analysis**: Only when explicitly requested, be systematic
- **Story critique**: Only when explicitly requested, be constructive

Good writing assistance respects the author's vision and amplifies their voice rather than imposing generic "best practices."

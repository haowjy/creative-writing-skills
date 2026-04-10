# Citation Guide

How to cite sources in wiki documentation. Citations make the wiki verifiable — every claim should trace back to where it was established.

## Why Cite

- **Verification:** readers can check the source
- **Contradiction resolution:** when sources disagree, citations show which takes precedence
- **Update tracking:** when a chapter is revised, citations show which wiki pages need updating

## Basic Formats

### Inline Citations

For specific facts within the body text:

```markdown
Sarah discovers her powers at age 15 (Chapter 2). She trains with 
Master Chen for three years (Chapters 4-7) before facing her first 
real challenge (Chapter 8).
```

### Reference Section

Collected at the bottom of the page:

```markdown
**References:**
- Chapter 2: Power awakening
- Chapter 5: First mention of the prophecy
- Chapter 8: Full confrontation scene
```

### Reference-Style (Numbered)

For pages with many specific citations:

```markdown
Sarah discovers her powers at age 15 [1]. She trains for three 
years [2] before her first real challenge [3].

**References:**
[1] Chapter 2: Power awakening
[2] Chapters 4-7: Training arc
[3] Chapter 8: First mission
```

## Organizing References

### By Topic

When a page covers multiple aspects:

```markdown
**References:**

*Physical Description*
- Chapter 2: Initial description
- Chapter 9: Post-transformation appearance

*Abilities*
- Chapter 5: Power discovery
- Chapter 11: Full power reveal
```

### By Chronology

For biographies and event pages:

```markdown
**References:**
- Chapter 1: Childhood flashback
- Chapter 6: College years mentioned
- Chapter 12: Complete backstory revealed
```

### By Relevance

Most important first:

```markdown
**References:**
- Chapter 8: Major character-defining moment
- Chapter 3: First appearance
- Chapter 15: Arc resolution
```

## Special Cases

### Contradictions

Note both sources explicitly:

```markdown
Sarah's age is stated as 23 in Chapter 2, but referred to as 25 in 
Chapter 8. [Contradiction — clarification needed]

**References:**
- Chapter 2: Age given as 23
- Chapter 8: Referred to as 25
```

### Implied Information

When something is suggested but not stated:

```markdown
Marcus likely has military training (implied by combat skills and 
terminology, not explicitly stated).

**References:**
- Chapter 4: Combat proficiency demonstrated
- Chapter 7: Uses military jargon
```

### Worldbuilding Sources

For lore created before chapters are written:

```markdown
The danger rating system uses five tiers.

**References:**
- Worldbuilding doc: `danger-ratings.md`
- Chapter 3: Tier system referenced in dialogue
```

### Work-in-Progress

For incomplete information:

```markdown
The antagonist's true name has not yet been revealed.

**References:**
- Chapters 1-10: Referred to only as "The Shadow"
- [To be updated when revealed]
```

## Spoiler Citations

When a citation itself is a spoiler:

```markdown
**References:**
- Chapter 3: First appearance

<details>
<summary>Spoiler references (Chapter 15+)</summary>

- Chapter 15: True identity revealed
- Chapter 18: Final confrontation
</details>
```

## Updating Citations

When chapters are revised, add update notes:

```markdown
**References:**
- Chapter 5: Sarah's backstory [updated 2025-03-15]
- Chapter 8: Relationship dynamic changed in revision [rev. 2025-03-15]
```

## Cross-References

Link to related wiki pages:

```markdown
Sarah's relationship with [[Marcus Webb]] is complicated by the 
revelation about [[the prophecy]] in Chapter 8.

**See also:** [[Marcus Webb]], [[The Prophecy]], [[Chapter 8 Events]]
```

## Best Practices

- Be specific enough to find the source (chapter + scene description)
- Organize logically for the page's content
- Note contradictions rather than silently picking one version
- Update when chapters change
- Use inline citations for specific facts, reference sections for general sourcing
- Cross-reference related wiki pages

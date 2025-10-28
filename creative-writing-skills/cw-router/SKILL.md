---
name: cw-router
description: Quick guide to choosing the right creative writing skill. Use when you need help deciding which creative writing skill to use for a specific task - brainstorming vs documentation, critique vs writing, etc.
---

# Creative Writing Skills - Quick Reference

Quick guide to choosing the right skill for your task.

## The Skills

### cw-brainstorm-capture
**Use for:** Exploring ideas, figuring things out, thinking through options

**Creates:** Skeletal working notes with [TBD] markers and source tags

**Handles:**
- Story/plot brainstorming
- Chapter planning (beats, scenes)
- Worldbuilding exploration (magic, cultures, geography)
- Character development (motivations, arcs, relationships)
- Timeline and continuity work

**Key trait:** Multiple options coexist, preserves vagueness, exploratory

---

### cw-official-wiki
**Use for:** Documenting finalized decisions, creating canonical reference

**Creates:** Polished, reader-ready wiki pages with citations

**Handles:**
- Character profiles
- Location documentation  
- Lore/system pages
- Event documentation
- Any finalized worldbuilding

**Key trait:** Single version, no [TBD], encyclopedic tone

---

### cw-story-critique
**Use for:** Getting feedback on written chapters/scenes

**Analyzes:**
- Plot and pacing
- Character development
- Prose quality
- Story structure
- Whatever needs feedback

**Key trait:** Feedback on existing writing, not creating content

---

### cw-prose-writing
**Use for:** Actually writing story prose in your style

**Writes:**
- Scenes and chapters
- Dialogue
- Narrative prose
- Story content

**Key trait:** Creates actual story text, matches your voice

---

### cw-style-skill-creator
**Use for:** Creating custom style skills for prose writing

**Creates:** Skills that teach Claude your specific writing style

**Key trait:** Meta-skill for building other skills

---

## Key Distinction: Brainstorm vs Wiki

This is the most common confusion:

**Still figuring it out?** → **cw-brainstorm-capture**
- "Maybe X, or Y, or Z?"
- [TBD] markers everywhere
- Multiple versions coexist
- Skeletal notes

**You've decided and it's ready to show someone?** → **cw-official-wiki**  
- Single authoritative version
- Polished and reader-ready
- No [TBD] markers
- Canonical documentation

---

## Common Scenarios

### "I'm exploring worldbuilding ideas for my magic system"
→ **cw-brainstorm-capture** (exploring, not finalized yet)

### "I've finalized my magic system and want to document it"
→ **cw-official-wiki** (decided and ready to document)

### "I'm thinking through how this chapter should flow"
→ **cw-brainstorm-capture** (planning/exploring)

### "I need to write this chapter"
→ **cw-prose-writing** (actually writing)

### "I wrote this chapter and want feedback"
→ **cw-story-critique** (getting feedback)

### "I need a character profile for my protagonist"
→ **cw-official-wiki** if finalized, **cw-brainstorm-capture** if still exploring

### "I'm figuring out character motivations and relationships"
→ **cw-brainstorm-capture** (exploring)

### "I want to document this character's canon profile"
→ **cw-official-wiki** (documenting finalized)

### "Help me work out the timeline of events"
→ **cw-brainstorm-capture** (working through chronology)

### "I want Claude to write in my specific style"
→ **cw-style-skill-creator** first (create style skill), then **cw-prose-writing**

---

## Decision Tree

```
Are you writing story prose?
  └─ Yes → cw-prose-writing
  └─ No ↓

Do you want feedback on something written?
  └─ Yes → cw-story-critique
  └─ No ↓

Are you figuring things out or have you decided?
  └─ Figuring out → cw-brainstorm-capture
  └─ Decided → cw-official-wiki

Need a custom writing style?
  └─ Yes → cw-style-skill-creator
```

---

## Skills Work Together

You can use multiple skills in combination:

- **Brainstorm** → finalize → **Wiki** (explore then document)
- **Brainstorm** → **Prose** (plan then write)
- **Prose** → **Critique** (write then get feedback)
- **Brainstorm** + **Wiki** (check existing wiki while brainstorming)
- **Critique** + **Brainstorm** (get feedback and brainstorm fixes)

Skills are composable - use whatever combination helps.

---

## Still Unsure?

**Default rules:**

1. **Exploring/uncertain?** → brainstorm-capture
2. **Finalized/polished?** → official-wiki  
3. **Need feedback?** → story-critique
4. **Actually writing?** → prose-writing

When in doubt, start with brainstorm-capture. You can always move to wiki later when things are decided.

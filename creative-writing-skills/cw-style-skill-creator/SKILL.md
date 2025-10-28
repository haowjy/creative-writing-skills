---
name: cw-style-skill-creator
description: Creative writing skill for creating style skills that teach Claude to write in specific styles. Use when you want to create style guides that the cw-prose-writing skill can follow. Creates either simple markdown files or full .skill packages. Audience is AI (Claude), format is directive and example-based.
---

# Style Skill Creator

Create style skills that teach Claude your writing style.

## Critical: Audience is AI

This creates **AI instructions** (for Claude to read), NOT **human documentation** (for authors to read).

| AI Instructions | Human Documentation |
|-----------------|---------------------|
| "When writing X, do Y" | "The story uses X because Y" |
| Directive commands | Explanatory descriptions |
| Pattern + examples | Analysis + reasoning |

## Step 1: Ask About Format

**Always ask first:**

```
Would you like me to create:

1. Simple markdown file (.md)
   - Quick, lightweight
   - Single file with style instructions
   
2. Full skill package (.skill)
   - Properly structured and validated
   - Can include reference files with examples
   - Better for complex styles

Which format would you prefer?
```

## Simple Markdown Format

```markdown
---
description: [What this style covers]
alwaysApply: false
---

# [Style Name]

[Brief intro]

## [Category]

[Directive instructions with examples]
```

**Location:** `.cursor/rules/styles/[name].md` or user-specified

## Full Skill Package Format

### Initialize

```bash
python /mnt/skills/examples/skill-creator/scripts/init_skill.py [skill-name] --path [output-dir]
```

Creates directory structure with SKILL.md, references/, scripts/, assets/

### Customize

**SKILL.md structure:**
```markdown
---
name: [skill-name]
description: Style skill for [specific writing type]
---

# [Style Name]

## Purpose
Teaches Claude to write [X] in the author's style.

## [Style Instructions]
[Directive instructions organized by category]
```

**Add reference files if helpful:**
- `references/examples.md` - Good/bad examples
- `references/patterns.md` - Detailed pattern library

**Delete unused directories** (scripts/, assets/ if not needed)

### Package

```bash
python /mnt/skills/examples/skill-creator/scripts/package_skill.py [path-to-skill] [output-dir]
```

Creates validated `.skill` file ready to distribute.

## Writing Style: Directive and Technical

**Use imperative/command form:**

✅ "Use short sentences during action"  
✅ "Avoid dialogue tags"  
✅ "Show emotion through action"  
❌ "The author tends to use short sentences" (that's analysis, not instruction)

**Always include examples:**

```markdown
**Emotional beats:**
- Use action instead of emotional labels
- Example: "Her hands trembled" not "She felt nervous"
```

**Pattern + Example format:**
```markdown
**[Pattern name]:**
- [Instruction about the pattern]
- Example: [Concrete example]
- Avoid: [What NOT to do]
```

## Common Style Skill Types

**Master Prose:** Overall writing voice, sentence structure, tone  
**Dialogue:** Tag usage, action beats, subtext, character voice  
**Action:** Sentence length, detail level, pacing  
**Description:** Sensory detail, metaphors, level of detail  
**Character Voice:** Per-character speech patterns and vocabulary  
**Formatting:** Em dashes, ellipsis, scene breaks, thought formatting

## Creation Process

### 1. Gather Input

From user description:
- "Describe your style to me"
- "What patterns should this cover?"

From existing prose:
- "Can I read some chapters to identify patterns?"
- Read 2-3 chapters if provided

### 2. Ask About Format

Simple .md or full .skill package?

### 3A. Simple Path

- Create markdown with sections
- Add directive instructions + examples
- Save to `.cursor/rules/styles/` or specified location

### 3B. Full Skill Path

1. Run `init_skill.py`
2. Edit SKILL.md with style instructions
3. Add reference files if helpful
4. Delete unused directories
5. Run `package_skill.py`
6. Provide download link

## Examples

### Dialogue Style (Simple .md)

```markdown
---
description: Dialogue writing conventions
alwaysApply: false
---

# Dialogue Style

## Dialogue Tags

**Minimize "said":**
- Use action beats instead
- Example: She crossed her arms. "Fine."
- When using tags, prefer "said" to fancy verbs

## Interruptions

**Use em dashes:**
- For interrupted speech: "I thought we could—"
- Example: "Wait, I—" He grabbed her arm.

## Subtext

**Characters avoid directness:**
- Show tension through what's NOT said
- Example: "That's nice." (flat, clearly upset)
- Avoid: "I'm angry!" (too direct)
```

### Character Voice

```markdown
---
name: character-amber-voice
description: Amber's voice and speech patterns
---

# Character Voice: Amber

## Speech Patterns

**Careful word choice:**
- Adult consciousness = measured speech
- Avoids contractions when stressed
- Example: "I do not want to go" not "I don't wanna go"

**Politeness as defense:**
- Overly formal when uncomfortable
- Uses "please" and "thank you" excessively

## Internal Monologue

**Analytical:**
- Observes and categorizes
- Example: "Dr. Fuji's hands trembled—stress response, possibly guilt."
```

## Integration

**The workflow:**
1. User writes chapters naturally
2. This skill converts patterns into style skills
3. cw-prose-writing loads and follows those skills
4. Result: Consistent AI-written prose in user's style

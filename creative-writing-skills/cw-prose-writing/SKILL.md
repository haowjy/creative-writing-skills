---
name: cw-prose-writing
description: Creative writing skill for drafting and editing narrative fiction prose. Use when writing new scenes, chapters, or dialogue, or when editing existing prose. Discovers and follows project-specific style guides, character voice conventions, and formatting preferences.
---

# Prose Writing

Write narrative fiction following your project's established style and conventions.

## Before Writing: Discover Style Guidance

**ALWAYS check for style guidance before writing:**

### Step 1: Check Project Documentation

Look for:
- `CLAUDE.md` - Often explains project structure
- `WRITING.md`, `CONVENTIONS.md`, `STYLE.md`
- `README.md` - May contain writing instructions

### Step 2: Find Style Guide Locations

Common locations:
- `.cursor/rules/styles/` - Style files (`.md` or `.skill` packages)
- `.cursor/rules/` - May contain style files
- `.ai/styles/`, `.ai/rules/`
- `docs/style/`, `style/`, `writing/`
- Installed Claude skills

**Style guides can be:**
- Simple markdown files (`.md`)
- Full skill packages (`.skill`) created by cw-style-skill-creator
- Both work - read and follow their instructions

### Step 3: Identify Relevant Guides

Different types:
- Master prose guide (overall writing style)
- Scene-type guides (dialogue, action, description)
- Character voice guides (how specific characters speak/think)
- POV guides (perspective and tense)
- Formatting guides (em dashes, ellipsis, scene breaks)

**Read relevant guides BEFORE writing.** If writing dialogue-heavy scene, read both master and dialogue guides.

### Step 4: Check Reference Materials

Also look for:
- Character profiles (voice consistency, canon facts)
- Location wikis (setting details)
- Timeline docs (chronology)
- Lore pages (worldbuilding accuracy)

## If No Style Guides Exist

**When NO style guides found:**

Inform user:
```
I don't see any style guides in your project yet. I can write in 
competent default prose, but you'll get better results by creating 
style guides first using the cw-style-skill-creator skill.

Would you like me to:
1. Write in default style for now
2. Help you create style guides first
3. Search your project for existing style documentation
```

**If user wants you to proceed anyway:**
- Write in clean, competent prose
- Look for patterns in existing chapters if available
- Use neutral narrative voice
- Follow basic conventions

## Using Web Search

Search when helpful for:
- Research for scenes (locations, historical details, technical accuracy)
- Verifying facts mentioned in prose
- Finding inspiration or reference examples
- Genre convention research
- Cultural accuracy verification

## Writing Workflow

**While Writing:**
- Apply discovered style conventions
- Match character voices to profiles
- Respect established canon
- Use project formatting conventions
- Maintain consistent POV and tense

**Self-Check After:**
- Does this match the project's voice?
- Is POV/tense consistent?
- Do characters sound like themselves?
- Are canon facts accurate?

## Output Format

### Claude.ai Chat
Markdown artifact with proper formatting

### Claude Code
1. Check project structure for chapter organization
2. Match existing naming conventions
3. Use appropriate directory
4. Include proper frontmatter if project uses it

## Integration with Style Skills

**The workflow:**
1. User writes chapters naturally
2. User uses cw-style-skill-creator to create style skills
3. This skill loads and follows those style skills
4. Result: AI writes in user's established style

**Without style guides:** Generic competent prose  
**With style guides:** YOUR specific voice

## Skills are Composable

Feel free to combine with other skills - e.g., using cw-official-docs to check character details while writing.

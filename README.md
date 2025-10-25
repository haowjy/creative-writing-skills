# Creative Writing Skills

A comprehensive creative writing assistant plugin for Claude Code and Claude.ai. This skill helps with writing prose in your style, creating reference documentation (character profiles, world-building, lore), analyzing your writing style, and critiquing story content.

## Features

- Write prose in your personal style
- Create character profiles and world-building documentation
- Analyze and critique story content
- Get guidance on dialogue, pacing, plot structure, and more
- Generate reference documentation for your creative projects

## Installation

### For Claude Code

**Option 1: Install from Marketplace (Recommended)**

1. Add this marketplace to Claude Code:
   ```
   /plugin marketplace add yourusername/creative-writing-skills
   ```

2. Install the plugin:
   ```
   /plugin install creative-writing-assistant@creative-writing-skills
   ```

3. Verify installation:
   ```
   /plugin
   ```

**Option 2: Install from Local Path**

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/creative-writing-skills.git
   ```

2. Add as a local marketplace:
   ```
   /plugin marketplace add ./creative-writing-skills
   ```

3. Install the plugin:
   ```
   /plugin install creative-writing-assistant
   ```

### For Claude.ai

**Step 1: Create Your Writing Project**

1. Go to [Claude.ai](https://claude.ai) and create a new Project
2. Name it after your writing project (e.g., "My Fantasy Novel")

**Step 2: Add the Creative Writing Skill**

1. Download this repository as a ZIP file from GitHub
2. Extract the ZIP file
3. In your Project, click "Add Content" → "Upload Files"
4. Upload the key reference files from `creative-writing-skills/creative-writing-assistant/references/`:
   - `writing-techniques.md`
   - `character-development.md`
   - `dialogue-craft.md`
   - `plot-structure.md`
   - `style-guide-template.md`
   - And any other reference files you want to use

**Step 3: Build Your Writing Wiki**

For best results, use this skill to create a comprehensive knowledge base for your project. Upload these documents to your Project's knowledge base (200,000 token capacity ≈ 500 pages):

1. **Style Guide**
   - Upload sample chapters of your writing
   - Ask: "Analyze my writing style and create a comprehensive style guide"
   - Save the generated style guide as a document and upload it

2. **Character Profiles**
   - Ask: "Create a detailed character profile for [character name]"
   - Build a wiki-style database with one document per major character
   - Include: personality, backstory, motivations, relationships, character arc

3. **World-Building Documentation**
   - Create documents for: setting, magic systems, technology, politics, history, cultures
   - Organize by topic with clear section identifiers
   - Ask Claude to help expand and detail each aspect

4. **Plot & Story Structure**
   - Upload your outline or synopsis
   - Create act breakdowns, scene lists, plot threads
   - Track character arcs and story progression

5. **Lore & Reference Material**
   - Terminology glossaries
   - Timeline of events
   - Maps and geography notes
   - Cultural details and worldbuilding specifics

**Step 4: Organize Your Knowledge Base**

Best practices for your writing project knowledge base:

- **Use descriptive filenames**: `character-protagonist-name.md`, `world-magic-system.md`
- **Add section identifiers**: Use clear headings so Claude can reference specific sections
- **Keep documents focused**: One document per character/location/concept
- **Update regularly**: Add new documents as your story develops
- **Curate quality content**: Focus on relevant, high-quality information
- **Combine document types**: Mix character profiles, plot outlines, style guides for rich context

**Step 5: Set Custom Instructions**

In your Project settings, add custom instructions like:
```
You are helping me write [genre] fiction. Always:
- Write in my established style (see style-guide.md)
- Maintain character consistency (see character profiles)
- Follow the world rules (see world-building docs)
- Match the tone and voice of my existing chapters
```

**Working with Your Project**

Once set up, you can:
- "Write the next scene where [character] discovers [plot point]"
- "How would [character A] react to [character B] doing [action]?"
- "Expand the lore about [world element]"
- "Create a new character profile for [role] that fits my world"
- "Analyze this chapter for consistency with my established style"

Claude will draw from your entire knowledge base (style guide, characters, world-building) to provide contextually accurate, style-consistent responses.

## Usage

### Quick Start

Once installed in Claude Code, simply ask for help with creative writing tasks:

- "Help me write a compelling opening scene for my fantasy novel"
- "Create a character profile for my protagonist"
- "Analyze the pacing of this chapter"
- "Suggest improvements to this dialogue"
- "Help me develop the world-building for my sci-fi setting"

### Setting Up a Writing Project

For best results, create a dedicated writing project with a custom style guide:

1. **Create a project directory** for your writing:
   ```bash
   mkdir my-novel
   cd my-novel
   ```

2. **Generate a style guide** based on your writing:
   - Place sample chapters or writing in your project directory
   - Ask Claude: "Analyze my writing style and create a style guide"
   - Claude will use this skill to create a comprehensive style guide

3. **Save your style guide** to project memory:
   - Create a `.claude/CLAUDE.md` file in your project
   - Add your style guide, character profiles, and world-building notes
   - Use the `#` shortcut to quickly add memories
   - Import modular files: `@./style-guide.md` or `@./characters/protagonist.md`

4. **Organize your project**:
   ```
   my-novel/
   ├── .claude/
   │   └── CLAUDE.md           # Main project instructions
   ├── style-guide.md          # Your personal writing style
   ├── characters/             # Character profiles
   ├── world-building/         # Setting and lore
   └── chapters/               # Your manuscript
   ```

5. **Work with context**: When you work in this directory, Claude will automatically use your style guide, character profiles, and world-building notes to:
   - Write new scenes in your style
   - Maintain character consistency
   - Follow your established lore and world rules
   - Apply your preferred narrative techniques

### Example Workflow

```bash
# Navigate to your writing project
cd my-novel

# Analyze your existing work
# "Analyze these three chapters and create a style guide"

# Use the skill to create character documentation
# "Create a detailed character profile for my protagonist based on chapter 1"

# Write new content with your style
# "Write the next scene where the protagonist confronts the antagonist"
```

## What's Included

- Comprehensive writing technique guides
- Character development frameworks
- Plot structure templates
- Dialogue crafting guidance
- Pacing and flow techniques
- Style analysis tools
- Scene transition guides
- Reference templates for characters, world-building, and lore

## License

MIT

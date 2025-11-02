# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains a Claude Code plugin with six composable creative writing skills designed to assist with the complete writing process: brainstorming, prose writing, critique, documentation, and style guide creation.

**Key insight:** These skills are designed to work together. The skills are composable—users can invoke multiple skills in sequence or combination to handle complex writing workflows.

## Plugin Architecture

### Structure
- `creative-writing-skills/` - Contains six skill directories (cw-*)
- Each skill directory contains:
  - `SKILL.md` - The main skill prompt/instructions
  - `references/` - Optional reference documentation used by the skill
- `.claude-plugin/marketplace.json` - Plugin manifest defining all skills
- `zips/` - Packaged `.skill` files for Claude.ai users
- `scripts/` - Build utilities

### The Six Skills

1. **cw-router** - Helps users choose the right skill for their task
2. **cw-prose-writing** - Writes story prose following project style guides
3. **cw-brainstorming** - Captures exploratory story ideas in minimal working notes
4. **cw-story-critique** - Analyzes written chapters and provides constructive feedback
5. **cw-official-docs** - Creates polished, canonical documentation (character profiles, world lore, etc.)
6. **cw-style-skill-creator** - Creates custom style guides from sample writing

**Core distinction:** brainstorming (exploratory, multiple options, [TBD] markers) vs. official-docs (finalized, single version, polished).

### Composability

Skills are designed to reference each other and work together:
- Brainstorm → finalize → Docs
- Write prose → Critique → Brainstorm fixes
- Style creator → Prose writing (using created styles)

## Custom Slash Commands

This repository includes custom slash commands in `.claude/commands/` that explicitly invoke the creative writing skills. These commands make it easier to switch between different writing modes.

### Available Commands

- **`/bs`** - Brainstorm and explore story ideas (uses cw-brainstorming skill)
- **`/write [style]`** - Enter prose writing mode (uses cw-prose-writing skill)
  - Optionally specify a style: `/write action-heavy`, `/write literary`, etc.
  - If a style guide exists in the project, it will be used
  - If no style guide exists, Claude will write in that general style using its knowledge
  - References the style-skill-creator skill when users need to create style guides
- **`/wiki`** - Create canonical documentation/wiki pages (uses cw-official-docs skill)
- **`/critique`** - Get feedback on your writing (uses cw-story-critique skill)

### Why Slash Commands?

While skills can be invoked automatically, slash commands provide:
1. **Explicit mode switching** - Clear signal to Claude about what mode you want
2. **Context shift** - The command prompt completely shifts Claude's context to the skill
3. **Easier invocation** - Shorter than saying "use the cw-brainstorming skill"
4. **Arguments support** - Pass additional context directly (e.g., `/write thriller-style`)

## Development Commands

### Building Skill Packages
```bash
python scripts/create_skill_zips.py
```
Creates individual `.skill` files (ZIP format) in `zips/` directory for uploading to Claude.ai.

### Testing the Plugin Locally
```bash
# Add as local marketplace
claude plugin marketplace add .

# Install the plugin
claude plugin install creative-writing-skills

# List installed plugins
claude plugin
```

### Making Changes to Skills

When modifying a skill:
1. Edit the `SKILL.md` in the appropriate skill directory
2. Update `references/` files if adding/changing reference documentation
3. Rebuild packages: `python scripts/create_skill_zips.py`
4. Test locally in a writing project directory

## Skill Design Patterns

### Source Tagging (Brainstorming)
The brainstorming skill uses a 3-tag system:
- **Untagged** = user stated this
- **`<AI>...</AI>`** = AI suggestions/possibilities
- **`<hidden>...</hidden>`** = Author-only information (twists, secrets)

This preserves the distinction between user's ideas and AI contributions.

### Citation System (Official Docs)
Documentation pages require citations:
- Chapter references: `Chapter 3: Scene where X discovers Y`
- Worldbuilding: `Worldbuilding document: magic-system.md`

### Style Guide Format (Style Creator)
Style guides are **AI instructions** (directive), not human documentation (explanatory):
- Use imperative form: "Use short sentences during action"
- Always include examples
- Pattern + Example format

### Flexible Structure Philosophy
Documentation and critique skills avoid rigid templates—structure should fit the content. A simple tavern needs one paragraph, not 12 sections. Trust judgment over formulas.

## Distribution

This plugin supports two distribution models:

1. **Claude.ai** - Users download `.skill` files from releases and upload to Claude.ai
   - **Note:** Slash commands in `.claude/commands/` are NOT included in `.skill` files
   - Claude.ai users can manually copy slash commands to their projects if desired
2. **Claude Code** - Users install via marketplace:
   ```bash
   claude plugin marketplace add haowjy/creative-writing-skills
   claude plugin install creative-writing-skills@creative-writing-skills
   ```
   - Slash commands in `.claude/commands/` are automatically included in the plugin

## Important Conventions

- Skill names always start with `cw-` prefix
- Each skill's `SKILL.md` uses frontmatter with `name` and `description`
- Skills should be self-contained but can reference other skills
- Skills should mention they are "composable" and can work with other skills
- The router skill helps users navigate between skills when uncertain

## Version Management

Version is defined in `.claude-plugin/marketplace.json` under `metadata.version`.

When releasing:
1. Update version in `marketplace.json`
2. Run `python scripts/create_skill_zips.py` to rebuild packages
3. Create GitHub release with updated `.skill` files from `zips/`
4. Update README.md if functionality changes

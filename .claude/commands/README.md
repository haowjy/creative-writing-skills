# Creative Writing Slash Commands

These custom slash commands provide explicit mode switching for the creative writing skills.

## Available Commands

### Brainstorming
- **`/bs`** - Brainstorm and explore story ideas

**Usage:**
```
/bs I'm thinking about a magic system where...
/bs What if the antagonist actually...
```

### Writing Prose
- **`/write [style]`** - Enter prose writing mode

**Usage:**
```
/write                          (uses project style guides if found)
/write action-heavy             (writes in action-heavy style)
/write literary                 (writes in literary style)
/write the next scene where...  (context for what to write)
```

If a style name is provided and no matching style guide exists, Claude will use general conventions for that style.

### Documentation/Wiki
- **`/wiki`** - Create canonical documentation pages

**Usage:**
```
/wiki Create a character profile for my protagonist
/wiki Document the magic system
```

### Critique
- **`/critique`** - Get feedback on your writing

**Usage:**
```
/critique [file or paste text]
/critique Analyze the pacing in chapter 3
```

### Creating Style Guides

To create style guides, use natural language within `/write` mode or just ask directly:
- "Analyze my writing style and create a style guide"
- "Create a dialogue style guide from these chapters"

The `/write` command will direct you to the style-skill-creator skill when needed.

## Why Use Slash Commands?

1. **Explicit invocation** - Clear signal about which skill you want
2. **Context shifting** - The command completely shifts Claude's focus to the skill
3. **Shorter syntax** - Easier than "use the cw-brainstorming skill"
4. **Arguments** - Pass additional context directly

## Natural Language Still Works

You can still use natural language to invoke skills:
- "Help me brainstorm ideas for my antagonist"
- "Write this scene in my style"
- "Create a wiki page for this location"

The slash commands just provide an explicit alternative when you want guaranteed skill activation.

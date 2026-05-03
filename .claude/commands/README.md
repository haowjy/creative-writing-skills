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
/write                          (uses project style files if found)
/write action-heavy             (writes in action-heavy style)
/write literary                 (writes in literary style)
/write the next scene where...  (context for what to write)
```

If a style name is provided and no matching style file exists in `kb/styles/`, Claude will use general conventions for that style.

### Knowledge Base
- **`/kb`** - Create or update kb reference pages

**Usage:**
```
/kb Create a character profile for my protagonist
/kb Update the magic system page with the new constraints
/kb Document the timeline for act 2
```

### Critique
- **`/critique`** - Get adversarial feedback on your writing

**Usage:**
```
/critique [file or paste text]
/critique Analyze the pacing in chapter 3
```

## Why Use Slash Commands?

1. **Explicit invocation** - Clear signal about which skill you want
2. **Context shifting** - The command shifts Claude's focus to the skill
3. **Shorter syntax** - Easier than "use the prose-critique skill"
4. **Arguments** - Pass additional context directly

## Natural Language Still Works

You can still use natural language to invoke skills:
- "Help me brainstorm ideas for my antagonist"
- "Write this scene in my style"
- "Critique the pacing in chapter 3"

The slash commands just provide an explicit alternative when you want guaranteed skill activation.

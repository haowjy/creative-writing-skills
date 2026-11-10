# KB Bootstrap

Starter layout for a new project KB. The KB tree follows `/creative-writing-skills:qi-layer`:
intent in `AGENTS.md`, governance depth in `.context/`.

## Directory Layout

```
kb/
  AGENTS.md          # intent: what belongs here, key rules
  .context/
    CONTEXT.md       # governance depth: writing conventions, structure, validation
  index.md           # catalog of pages with one-line summaries
  vocab.md           # project-wide terminology
```

Add directories as the KB grows: a topic earns a directory when it has
multiple related pages.

## Content Types

**Wiki pages**: what the project does and why, by topic: concepts,
architecture, patterns, the reasons behind choices, facts about the outside
world. Agents create pages, update them, and maintain cross-references.

**Sources**: raw material: articles, research, transcripts, data. Immutable.
Agents read from sources but never modify them.

## Starter AGENTS.md

```markdown
# KB Guide

Why the project is the way it is, where no one directory owns the
reason: domain concepts, architecture, patterns, facts about the outside
world. Pages record the system's current direction, what it should be,
independent of any checkout. Only what the human chose or finished work
established belongs here; options still open stay in work directories.

Raw research dumps and conversation transcripts don't belong here;
synthesize them first. Active task plans live in work directories.
Knowledge that depends on one subsystem stays colocated with it.

When content is superseded, delete it. Pages
read as current truth, never narrate their own evolution. A changed
choice rewrites its page; git keeps the old version.

- `index.md`: catalog. Update when you create or modify a page.
- `.context/CONTEXT.md`: writing conventions, structure, validation.
```

## Starter .context/CONTEXT.md

```markdown
# KB Working Conventions

## Writing

- One concept per page. Split when a page covers two unrelated topics.
- Each concept has one source of truth; other pages link to it.
- Name files by what they describe (`token-validation.md`), not when
  (`auth-redesign-notes.md`).
- Calibrate depth to importance. Reference material is terse and scannable.
  Architecture pages walk through reasoning.
- Each page says what the project does and why. A rule with no reason gets
  deleted; a rejected option stays only with the fact that sank it.
- No decision IDs and no decision register: write by topic.

## Structure

- Directories emerge organically as topics accumulate related pages.

## Validation

Use `/md-validation` for link checking and diagram validation before
committing.
```

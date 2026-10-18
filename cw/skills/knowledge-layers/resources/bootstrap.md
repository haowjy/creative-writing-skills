# KB Bootstrap

Starter layout for a new project KB. The KB tree follows `/qi-layer`:
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

A KB holds four kinds of content.

**Wiki pages**: synthesized knowledge. How things work, concepts,
architecture, patterns. Agents create pages, update them, and maintain
cross-references.

**Decision records**: what was chosen, what was rejected, and why. Wiki
pages link to decisions for rationale; decisions link to wiki pages for
context. Separate from wiki pages because the reasoning behind a choice
outlives the description of the current system: when the system changes,
the old decision record still explains why it was built that way.

**Sources**: raw material: articles, research, transcripts, data. Immutable.
Agents read from sources but never modify them.

## Starter AGENTS.md

```markdown
# KB Guide

Big-picture knowledge that spans components and outlives sessions:
decisions, domain concepts, architectural rationale, patterns. Pages
record the system's current settled intent — what it should be —
independent of any checkout.

Raw research dumps and conversation transcripts don't belong here;
synthesize them first. Active task plans live in work directories.
Knowledge that depends on one subsystem stays colocated with it.

When content is superseded, delete it or move it to `archive/`. Pages
read as current truth, never narrate their own evolution.

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
- Decision records capture what was chosen, what was rejected, and why.
  Wiki pages link to them for rationale.

## Structure

- Directories emerge organically as topics accumulate related pages.

## Validation

Use `/md-validation` for link checking and diagram validation before
committing.
```

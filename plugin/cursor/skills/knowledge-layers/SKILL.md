---
name: knowledge-layers
description: 'Use when deciding where knowledge goes or reading/writing durable docs: AGENTS.md and .context/ beside the code, the KB, and work directories.'
metadata:
  type: reference
alwaysApply: false
---

# Knowledge Layers

Knowledge lives next to what it describes. Load `/creative-writing-skills:qi-layer` before writing
`AGENTS.md` or `.context/`.

## Three Places

| Place | What goes there | Reader |
|---|---|---|
| Beside the code (`AGENTS.md`, `.context/`) | Knowledge about this directory, and its deferred work in `.context/TODO` (must-do) and `FUTURE` (nice-to-have); `/creative-writing-skills:qi-layer` says which file | An agent about to work in the directory |
| KB | Why the project is the way it is, where no one directory owns the reason; domain concepts; facts about the outside world | A future agent or the owner, without this work's context |
| Work directory | Anything not settled yet: plans, options, open questions, scratch | Agents on this work item |

Colocate first. Knowledge about one subsystem goes in its `AGENTS.md` or
`.context/`, even when it reads like a concept: a doc far from what it
describes isn't updated when that thing changes. The KB holds what would
survive a rewrite of any one implementation. Deferred work that spans
directories or needs outside visibility goes to the issue tracker.

## The KB Records Why

A KB page says what the project does, or what the human chose it should
do, and why: the reason, the fact or
constraint behind it, and what would change it. The reason is the content.
An agent that knows it can tell when it stops holding; an agent given only
the verdict can only obey it. A rule whose reason nobody can state gets
deleted. State the behavior and its reason without names, quotes or session
IDs: a line lifted from a conversation reads as a ruling.

Organize by topic, not as a register of decisions: no decision IDs, no
`decisions/` tree, no lists of rejected options. Keep a rejected option only
with the fact that sank it ("a fixed request deadline killed healthy long
generations"). Without its reason it reads as a ban nobody can re-examine.

Two things reach the KB: what the human chose, and what finished work
established. An option they floated, a question they asked, or a list they
gave without picking stays in the work directory until they choose. Read how
they said it: "maybe X?" is not a choice, and a choice made with a hedge is
written "for now" or "trying".

Before writing about some work, read the docs, `AGENTS.md`, `.context/` and
comments it updated. Link to them and write only what they don't say. When
they say all of it, the KB gets a link or nothing.

## Invariants and Current Choices

An **invariant** is a rule that holds however the work is done, until the
human changes it. Invariants can change: when one stops serving the users,
propose the change to the human as its own visible step, never to get a
task passing. Each is kept because the project's users rely on what it
protects; a user can be a program, such as an agent calling a CLI. A rule
whose breaking would hurt no one you can name is a contract of the area that
holds it, not an invariant.

The human names each invariant. They are rare and cut across the project,
so they sit in the root `AGENTS.md` beside who the users are, each a short
rule and its reason. A `.context/` page the root links says how the code
keeps each one, what checks it, and where it falls short.

Everything else is a **current choice**: how things stand now, with its
reason, open to change when the reason stops holding or the human asks for
something else (`/creative-writing-skills:intent-modeling`). Write it beside the work it describes,
as current state rather than as a rule.

## Current Truth

Every durable layer states the best current understanding and never
narrates its own history. Delete superseded content, and content whose
subject is gone, on sight, even with nothing to put in its place: agents
reason from what they load, and stale knowledge is worse than a gap.
Delete rather than move aside: version control is the archive, and a tree
without it gets a copy before you delete. Commit untracked files before
deleting them, and say in the commit message what
went and why. The agent that owns a tree's content deletes from it; a
structural role flags instead.

`AGENTS.md` and `.context/` describe the tree that contains them: update
them in the same change as what they describe. In a code project,
`resources/code.md` maps this onto branches and merges.

## KB Operations

A KB carries its own `AGENTS.md`, written per `/creative-writing-skills:qi-layer`. Read it before
writing; for that KB it wins over this skill. `resources/bootstrap.md` is a
starting layout for a new KB.

- **Ingest:** to capture a settled change, follow `resources/capture.md`.
- **Maintain:** when moving or renaming a page, fix every reference to it.
- **Lint:** look for contradictions, stale claims, orphan pages, and rules
  with no reason. `/creative-writing-skills:md-validation` checks links and diagrams.

Flag what needs the human inline, with the date and both sides:

```markdown
> [!FLAG] **Needs human review**: this page says X; `other-page.md` says Y.
> Both may be partly right. Flagged 2026-04-28.
```

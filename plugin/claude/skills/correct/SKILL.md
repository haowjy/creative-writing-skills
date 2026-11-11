---
name: correct
description: 'Use when the human wants a mistake agents keep making fixed. Starts from their correction or the mistake they name, finds what led the agent there, and fixes it where the cause is: the project''s docs, the code, or the prompt''s source; a cause in an installed prompt becomes a note for its owner.'
disable-model-invocation: true
metadata:
  type: mode-shift
argument-hint: The correction or mistake to start from
---

# Correct

The human corrected an agent and doesn't want to do it again. Find what led
the agent to the mistake, and change that.

## Find the Cause

Start from the correction the human gave or the mistake they name. Read the
session where it happened: what the agent read, what it was told, what it
did (`@session-miner` finds the passages; read them yourself). When the
human asks for a sweep, look for the same mistake in recent sessions,
reverts and review comments.

A single occurrence can be a bad run, with nothing in the setup to blame.
When that's what the evidence shows, say so and change nothing.

The usual causes:

- a line the agent read that misled it: stale, contradicted by the code, or
  buried under lines that matter less
- code that invites the mistake: two ways to do one task, a misleading
  name, a dead example that copies wrong
- a prompt (an agent or a skill) that steers wrong, or says nothing at the
  moment of choice

The same cause usually sits in more than one place: a stale rule copied
into other `AGENTS.md` files or KB pages, the same pattern in sibling code,
the same wording in another prompt. Search for it; the cause is found when
every copy is.

## Fix It Where the Cause Is

- **A misleading line** in `AGENTS.md`, `.context/` or the KB: correct or
  delete it. Thinning is often the fix: a rule lost among ten others gets
  followed once they go. Add a line only when nothing the agent read covers
  the choice, and put it where the agent reads it as it makes that choice.
- **Code that invites the mistake:** make the wrong way stop working,
  strongest first. One owner per piece of state and one supported way per
  task, with the old way and its dead examples deleted; then types, so the
  bad state can't be written; then a lint whose error names what to use
  instead, proven to fail on a real past mistake. This is a code change: it
  goes through the project's normal flow, not in with the correction.
- **A prompt:** fix it at its source. When the source is the repository
  you're working in, edit it there for the owner to review. When it's an
  installed package, leave the installed copy alone, since the next sync
  overwrites it: leave a note where the package's owners will see it
  (wherever its `AGENTS.md` says, an issue on its repository, or a message
  to whoever maintains it) saying what the human corrected, in which
  session, and the line you suspect.

A permission or hook that blocks an agent's action is for a destructive
mistake that has repeated, with the human's approval: it blocks legitimate
work too.

## Report

Each mistake with its evidence and cause, and what you changed or where you
left the note; and each one you judged a bad run, with why.

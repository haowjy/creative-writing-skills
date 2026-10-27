---
name: handoff
description: 'Use when the next phase belongs to a different interactive lead: writes a transition brief, runs applicable pre-phase checks, and hands off to a new primary session.'
metadata:
  type: mode-shift
---

# Handoff

Write a transition brief for a different interactive lead. Treat an argument as
the requested next lead or focus; otherwise infer both from the work.

## Write the Transition Brief

Start with `/creative-writing-skills:intent-modeling`: separate what the human said from what they want
to be true when the work is done. Then compact the conversation into a file the
next lead can use as its opening brief:

- Human intent: the end goal in the human's terms, not implementation steps
- Current state: what was accomplished and where things stand
- Key decisions and why
- Open questions or blockers
- Artifact paths: exact file paths to read first
- What the next lead needs: its immediate objective, constraints, and relevant
  skills

Keep artifact content in its files and give their paths in the brief. Write the
brief to the work directory when one is available; otherwise use a temporary
file.

## Run Pre-* Checks

Check for `pre-*` checkpoint skills that apply to the next phase, such as
`pre-dev` before implementation. Load and run each applicable checkpoint so the
next lead starts with its prerequisites ready.

## Hand Off

Hand off to a new primary session. Give the user the chosen lead, the exact path
to the brief, and any work or source references the next session needs. The user
starts the new session; do not start it for them.

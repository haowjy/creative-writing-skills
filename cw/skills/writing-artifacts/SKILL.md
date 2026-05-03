---
description: Where writing artifacts live — kb/ for durable knowledge, work/ for scratch. Use when deciding where to read from or write to.
---

# Writing Artifacts

- Durable project knowledge lives in `kb/` at the project root.
- Work scratch lives in `work/`, for the current drafting effort.
- Project-specific structure (kb subdirectories, author's conventions) is
  documented in the project's `CLAUDE.md`. Read it for this project's layout.

## Work Layout

```text
work/
  outline/               # current outline being worked
  drafts/                # draft iterations (v1, v2, etc.)
  critique-reports/      # critic output for each round
  brainstorm/            # brainstorm captures and synthesis
```

## KB Layout

```text
kb/
  styles/                # style reference files for writer/critic agents
  characters/            # character state and profiles
  world/                 # world details, locations, factions
  timeline/              # chronological event entries
  canon/                 # hard facts the story has established
  issues/                # tracked writing issues (tics, inconsistencies)
```

A project can customize this layout in its `CLAUDE.md`. Read that first.

## Shared Workspace

The working tree is shared between the author and all agents. Any file may
have been edited by someone else since you last saw it.

Read the current state before acting on it — a draft may have author edits
between critique rounds, a kb entry may have been updated by another agent,
an outline may have been restructured. Treat what's on disk as the authority,
not your memory of what was there.

When your edits would conflict with changes someone else made, surface the
conflict rather than silently overwriting. The author's direct edits are
always authoritative.

## Promotion

When a drafting effort completes, promote *knowledge* from work/ to kb/ — not
raw artifacts. Brainstorm captures and draft iterations stay in work/.

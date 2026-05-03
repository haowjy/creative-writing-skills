---
name: writing-artifacts
description: Where writing artifacts live — kb for durable knowledge, work directory for scratch. Use when deciding where to read from or write to.
---

# Writing Artifacts

- Durable project knowledge lives in `$MERIDIAN_CONTEXT_KB_DIR`. See `kb-conventions` for the kb model.
- Work scratch lives in `$MERIDIAN_CONTEXT_WORK_DIR`, scoped to the current work item and archived on completion.
- Project-specific structure (kb subdirectories, author's space, conventions) is documented in the project's `AGENTS.md`. Read it for this project's layout.

## Work Layout

```text
$MERIDIAN_CONTEXT_WORK_DIR/
  outline/               # current outline being worked
  drafts/                # draft iterations (v1, v2, etc.)
  critique-reports/      # critic output for each round
  brainstorm/            # brainstorm captures and synthesis
```

## Shared Workspace

The working tree is shared between the author, the orchestrators, and worker
agents. Any file may have been edited by someone else since you last saw it.

Read the current state before acting on it — a draft may have author edits
between critique rounds, a KB entry may have been updated by another agent,
an outline may have been restructured. Treat what's on disk as the authority,
not your memory of what was there.

When your edits would conflict with changes someone else made, surface the
conflict rather than silently overwriting. The author's direct edits are
always authoritative.

## Promotion

When a work item completes, promote *knowledge* from work to kb — not raw artifacts. Brainstorm captures and draft iterations stay archived in the work item.

## Convention Is Swappable

This skill defines convention. A project can replace it without touching agent bodies.

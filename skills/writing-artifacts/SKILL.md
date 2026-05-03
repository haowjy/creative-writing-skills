---
name: writing-artifacts
description: Where writing artifacts live — kb for durable knowledge, work directory for scratch. Use when deciding where to read from or write to.
invocation: implicit
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

## Promotion

When a work item completes, promote *knowledge* from work to kb — not raw artifacts. Brainstorm captures and draft iterations stay archived in the work item.

## Convention Is Swappable

This skill defines convention. A project can replace it without touching agent bodies.

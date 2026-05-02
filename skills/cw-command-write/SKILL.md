---
name: cw-command-write
description: Use when the user types or refers to /write, asks for the creative writing write command, wants prose-writing mode, or provides /write with an optional style name or scene request.
---

# CW Command: /write

Codex adaptation of the Claude Code `/write [style]` creative writing command.

Use this as an explicit command entrypoint, then apply `prose-writing` and, when a role mode is useful, `cw-agent-writer`.

## Behavior

- Write narrative fiction prose, not outline notes or critique.
- Before writing, look for relevant style guides in the current project when files are available.
- Read applicable style guides, character profiles, lore docs, prior chapters, and scene briefs before drafting.
- Match discovered project voice and conventions.
- If a style name is provided and no matching project style guide exists, use general conventions for that style and say that no project-specific guide was found.
- If the user asks to create a style guide instead of draft prose, use `cw-agent-style-creator`.

## Input

Treat text after `/write` as either:

- a style name, such as `action-heavy` or `literary`;
- a scene/chapter request;
- both, if the wording clearly includes style plus task.

If the user only says `/write`, ask for the scene, chapter, or revision target.

For the original Claude command text, see `references/command.md`.

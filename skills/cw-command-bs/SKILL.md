---
name: cw-command-bs
description: Use when the user types or refers to /bs, asks for the creative writing brainstorm command, or wants explicit brainstorming mode for story, plot, character, worldbuilding, chapter, or scene ideas.
---

# CW Command: /bs

Codex adaptation of the Claude Code `/bs` creative writing command.

Use this as an explicit command entrypoint, then apply `brainstorming` and, when a role mode is useful, `cw-agent-brainstormer`.

## Behavior

- Explore story ideas without committing them as canon.
- Capture only what the user states as fact.
- Mark assistant suggestions with `<AI>...</AI>`.
- Mark author-only secrets, twists, or spoiler material with `<hidden>...</hidden>`.
- Preserve vagueness with `[TBD]` instead of filling gaps.
- Keep notes skeletal enough that the user still has creative room.
- After capturing notes, continue the conversation to develop options.

## Input

Treat text after `/bs` as the brainstorming prompt. If the user only says `/bs`, ask what topic, scene, character, or story problem they want to explore.

For the original Claude command text, see `references/command.md`.

---
name: cw-command-wiki
description: Use when the user types or refers to /wiki, asks for the creative writing wiki command, or wants finalized story canon documented as character pages, lore pages, worldbuilding docs, or reader-facing reference pages.
---

# CW Command: /wiki

Codex adaptation of the Claude Code `/wiki` creative writing command.

Use this as an explicit command entrypoint, then apply `wiki-docs` and, when a role mode is useful, `cw-agent-wiki-editor`.

## Behavior

- Create or update canonical, reader-facing story documentation.
- Include only finalized, confirmed information.
- Use citations for claims when source material is available: chapter references, scene references, worldbuilding notes, or existing docs.
- Write in polished encyclopedic tone: third person, factual, neutral.
- Use flexible structure that fits the topic; do not force a rigid template.
- Add cross-references to related pages when useful.
- If the user is still exploring possibilities, route to `cw-command-bs` or `brainstorming` instead of presenting the material as canon.

## Input

Treat text after `/wiki` as the documentation target. If the user only says `/wiki`, ask what topic should be documented and whether the facts are finalized.

For the original Claude command text, see `references/command.md`.

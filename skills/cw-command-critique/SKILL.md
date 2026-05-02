---
name: cw-command-critique
description: Use when the user types or refers to /critique, asks for the creative writing critique command, wants structured feedback on fiction, or provides text/file context for prose, pacing, character, dialogue, plot, or genre critique.
---

# CW Command: /critique

Codex adaptation of the Claude Code `/critique` creative writing command.

Use this as an explicit command entrypoint, then apply `prose-critique` and, when a role mode is useful, `cw-agent-critic`.

## Behavior

- Critique existing story content; do not rewrite unless the user asks.
- Ask for target audience, goals, desired feedback type, or draft stage only when missing information would materially change the critique.
- Calibrate feedback to the draft stage: early drafts need structural and intent feedback; late drafts can tolerate line-level precision.
- Consider plot, character, pacing, dialogue, prose quality, continuity, and genre fit.
- Use structured findings with severity and concrete evidence.
- Use web research only when current genre conventions or external craft references would materially improve the answer.

## Input

Treat text after `/critique` as pasted prose, a file target, or the requested critique focus. If the user only says `/critique`, ask for the text or file and desired focus.

For the original Claude command text, see `references/command.md`.

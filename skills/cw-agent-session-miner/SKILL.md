---
name: cw-agent-session-miner
description: Use when the user asks for the creative writing session-miner agent or wants durable story decisions recovered from brainstorms, planning conversations, or session notes.
---

# CW Agent: session-miner

This is a Codex adaptation of the Claude Code `session-miner` agent profile from `creative-writing-skills`.

## Role

Mine conversations for decisions, rejected alternatives, rationale, and unresolved questions. Write or report decision records with provenance.

## Codex Adaptation

- Treat this skill as a role mode in the current Codex assistant; it does not register a Claude/Mars agent or slash command.
- Load or apply supporting creative-writing skills when relevant: `story-decisions`, `writing-artifacts`.
- Do not assume `meridian spawn`, Mars work directories, Claude plugin commands, or Claude-only tools exist.
- If the original profile says to spawn another agent, translate that into Codex workflow: either perform the bounded role locally, or use Codex subagents only when the user has explicitly asked for agent delegation.
- Preserve the original profile's safety boundary: read-only roles should report findings only; writing roles may edit/create files only when the user asked for file changes.
- For exact role details, read `references/agent-profile.md`.

## Operating Pattern

1. Identify the user's story task and confirm the role actually fits.
2. Gather the minimum story context needed: brief, draft, canon, style files, wiki, kb, or decision notes.
3. Follow the role boundary from the original profile.
4. Produce the role's expected artifact or report in plain Markdown.
5. State assumptions, unresolved questions, and what should happen next in the writing workflow.

---
name: character-sim
description: "In-character conversation for voice discovery and relationship testing. Pass the character, the scenario or relationship to explore, and their style and character-state files; the conversation itself is the output."
model: opus
model-policies:
  - match: {alias: opus}
    override: {}
  - match: {alias: fable}
    no-fallback: true
    override: {}
  - match: {alias: sonnet}
    override: {}
  - match: {alias: sol}
    override: {}
  - match: {alias: deepseek}
    override: {effort: low}
skills:
  load: [character-sim, writing-principles, llm-writing]
  available: [story-memory]
tools:
  'bash(meridian session *)': allow
  'bash(cat *)': allow
  edit: deny
  write: deny
  notebook: deny
  ask_user: deny
sandbox: read-only
---

# Character Simulation

Use `/character-sim`.


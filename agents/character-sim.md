---
name: character-sim
description: In-character conversation for voice discovery and relationship testing.
model: deepseek
model-policies:
  - match:
      alias: deepseek
    override: {}
  - match:
      alias: sonnet
    override: {}
  - match:
      alias: gpt55
    override:
      effort: low
  - match:
      alias: gpt
    override: {}
skills:
  load: [character-sim, writing-principles, llm-writing]
  available: [story-memory]
tools:
  'bash(meridian spawn show *)': allow
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


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
  load: [character-voice, writing-principles, llm-writing]
  available: [story-context]
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

Use `/character-voice`.

Doesn't write files: the conversation itself is the output, mined later by
the chronicler or muse.


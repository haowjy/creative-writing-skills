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
  bash: allow
  read: allow
  notebook: deny
  ask_user: deny
  'bash(git revert:*)': deny
  'bash(git checkout --:*)': deny
  'bash(git restore:*)': deny
  'bash(git reset --hard:*)': deny
  'bash(git clean:*)': deny
sandbox: danger-full-access
approval: never
---

# Character Simulation

Use `/character-sim`.


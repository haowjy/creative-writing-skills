---
name: reader-sim
description: Experiential reader response from a caller-specified reader persona; pass the persona, draft, and knowledge boundary.
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
  load: [reader-sim, writing-principles, llm-writing]
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

# Reader Simulation

Use `/reader-sim`.

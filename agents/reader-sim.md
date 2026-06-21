---
name: reader-sim
description: Experiential reader response to a draft, moment by moment.
model: deepseek
model-policies:
  - match:
      alias: deepseek
    override:
      effort: low
  - match:
      alias: opus
    override: {}
  - match:
      alias: gpt
    override: {}
  - match:
      alias: sonnet
    override: {}
skills:
  load: [reader-experience, writing-principles, llm-writing]
tools:
  read: allow
  grep: allow
  glob: allow
  edit: deny
  write: deny
  notebook: deny
  ask_user: deny
sandbox: read-only
---

# Reader Simulation

Use `/reader-experience`. Read-only: report the experience, don't edit.

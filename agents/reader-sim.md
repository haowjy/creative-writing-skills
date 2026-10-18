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

Use `/reader-sim`.

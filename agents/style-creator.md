---
name: style-creator
description: Analyzes prose samples to produce style reference files for the project's voice.
model: opus
effort: high
model-policies:
  - match: {alias: opus}
    override: {effort: high}
  - match: {alias: fable}
    no-fallback: true
    override: {effort: high}
  - match: {alias: sonnet}
    override: {}
  - match: {alias: sol}
    override: {}
  - match: {alias: deepseek}
    override: {effort: low}
skills:
  load: [creative-writing-craft, writing-principles, llm-writing]
  available: [story-memory]
tools:
  bash: allow
  write: allow
  edit: allow
  read: allow
  glob: allow
  grep: allow
  notebook: deny
  ask_user: deny
  'bash(git revert:*)': deny
  'bash(git checkout --:*)': deny
  'bash(git restore:*)': deny
  'bash(git reset --hard:*)': deny
  'bash(git clean:*)': deny
sandbox: workspace-write
---

# Style Creator

Use `/creative-writing-craft` → `resources/style-analysis.md`.

When working without sample chapters, distinguish what's specified from
what's inferred.

Write to the kb styles directory.

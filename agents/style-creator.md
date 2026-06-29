---
name: style-creator
description: Analyzes prose samples to produce style reference files for the project's voice.
model: deepseek
effort: high
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

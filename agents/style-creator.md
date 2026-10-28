---
name: style-creator
description: "Analyzes prose samples into style reference files for the project's voice. Pass sample chapters or existing style files, or the author's voice goals when there are no samples; writes to the kb styles directory and returns the files written and what each rests on."
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

Analyze the prose samples you are given into style reference files, following
`/creative-writing-craft` `resources/style-analysis.md`. Write them to the kb
styles directory, and report the files you wrote and which samples or stated
goals each rests on.

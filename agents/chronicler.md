---
name: chronicler
description: Extracts factual state changes from written chapters into the kb.
model: deepseekflash
model-policies:
  - match:
      alias: deepseekflash
    override: {}
  - match:
      alias: deepseek
    override: {}
  - match:
      alias: sonnet
    override: {}
skills:
  load: [fact-extraction, knowledge-layers, writing-artifacts, llm-writing]
  available: [md-validation, shared-dao]
tools:
  bash: allow
  write: allow
  edit: allow
  notebook: deny
  ask_user: deny
  'bash(git revert:*)': deny
  'bash(git checkout --:*)': deny
  'bash(git restore:*)': deny
  'bash(git reset --hard:*)': deny
  'bash(git clean:*)': deny
sandbox: workspace-write
---

# Chronicler

Use `/fact-extraction`. Use `/knowledge-layers` for KB conventions,
`/md-validation` for link topology, `/writing-artifacts` for project structure.

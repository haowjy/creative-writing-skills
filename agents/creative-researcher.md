---
name: creative-researcher
description: "Web research for fiction: primary sources, reference works, cultural detail, domain expertise, and community discussion. Pass the question, the story context, and what the story currently assumes; returns sourced findings with conflicts and gaps, flagging where the story's assumptions are wrong."
mode: subagent
model: luna
effort: medium
model-policies:
  - match: {alias: luna}
    override: {effort: medium}
  - match: {alias: sonnet}
    override: {}
  - match: {alias: deepseek}
    override: {effort: low}
skills:
  load: [creative-research]
tools:
  bash: allow
  write: allow
  edit: allow
  web: allow
  notebook: deny
  ask_user: deny
sandbox: danger-full-access
approval: never
---

# Creative Researcher

Research the question you are given with `/creative-research`.

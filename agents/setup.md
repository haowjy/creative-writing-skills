---
name: setup
description: "Sets up a writing project once: interviews the author about the project, samples and voice, then writes the AGENTS.md, kb/ layout and style files every writing agent reads. Start it when a project has no AGENTS.md yet."
mode: primary
model: sonnet
effort: low
model-policies:
  - match: {alias: sonnet}
    override: {}
  - match: {alias: deepseek}
    override: {}
  - match: {alias: opus}
    override: {}
skills:
  load: [project-setup]
  available: [creative-writing-craft, story-memory]
subagents: []
tools:
  bash: allow
  write: allow
  edit: allow
  notebook: deny
sandbox: danger-full-access
approval: never
---

# Setup

Run `/project-setup` with the author, from the interview to the files it
creates. Ask focused questions and offer choices where you can. The author
approves each file before you write it.

---
name: reflect
description: 'Use when the user invokes it before you report: checks you delivered what they needed, not only what they literally asked, and routes knowledge capture.'
disable-model-invocation: true
metadata:
  type: guardrail
argument-hint: Optional focus for the check
---

# Reflect

Load `/creative-writing-skills:intent-modeling` if it isn't already loaded.

Did you deliver what they actually needed? Given what you changed, is there anything adjacent worth improving now while context is fresh, without opening a new project?

If something should survive this session, put it in the right layer: `/creative-writing-skills:knowledge-layers` for placement (AGENTS.md, `.context/`, KB, docs), `/creative-writing-skills:qi-layer` for writing AGENTS.md and `.context/CONTEXT.md`.

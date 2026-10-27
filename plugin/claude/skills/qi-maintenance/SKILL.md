---
name: qi-maintenance
description: Load on agents that make durable changes to a project's files, so the colocated AGENTS.md and .context/ docs stay true for the next cold agent.
disable-model-invocation: true
metadata:
  type: guardrail
---

# Qi Maintenance

Treat the nearest `AGENTS.md` and current-truth `.context/` documents like
comments attached to what they cover: read them before changing it.

As you make a coherent change, keep those documents accurate in the same
change. If a cold agent could still work correctly from them, leave them
alone. If they would mislead the next agent, update them before finishing.

Write what a cold agent needs and can't read from the files themselves. When the
implementation diverged from the settled plan, record the divergence and leave
the intent as settled.

Load `/creative-writing-skills:qi-layer` when creating, moving, restructuring, or substantially
rewriting colocated knowledge.

Track deferred work separately: directory-local must-do work goes in the
nearest `.context/TODO`, directory-local nice-to-have work in
`.context/FUTURE`, and cross-cutting or externally visible work in the project
issue tracker. Load `/creative-writing-skills:knowledge-layers` when placement is unclear.
Cross-cutting KB synthesis belongs to `@kb-lead`, after the change settles.

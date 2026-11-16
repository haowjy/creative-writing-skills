---
name: shared-workspace
description: 'Use when a workspace has changes from other agents: safe orientation, preserving unfamiliar files.'
metadata:
  type: guardrail
alwaysApply: false
---

# Shared Workspace

Other humans and agents may be working in this directory. Treat unfamiliar
files and edits as live work, not clutter, and keep them, including files a
compaction or handoff leaves you unsure are yours. When your task needs a
clean environment, make an isolated one instead of cleaning this one. When
your work overlaps changes you don't understand, stop and report the
conflict.

Report the files you changed, what you left behind (generated files, logs),
and what you didn't touch because its owner was unclear.

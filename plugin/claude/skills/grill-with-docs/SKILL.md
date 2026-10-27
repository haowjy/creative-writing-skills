---
name: grill-with-docs
description: |
  Use when grilling should be grounded primarily in project artifacts. Loads `/grill`, checks project vocabulary and prior decisions first, and spawns bounded explorers when the answer should come from docs.
metadata:
  type: reference
---

# Grill With Docs

Load `/creative-writing-skills:grill` if it isn't already loaded.
Load `/creative-writing-skills:knowledge-layers` if it isn't already loaded.

Use this when the challenge should be grounded primarily in project
artifacts.

Check repo docs, existing prompts, prior decisions, active work artifacts,
and project vocabulary before reaching for external sources.

When the answer should come from project materials beyond what is already in
context, spawn a bounded `@explorer` instead of bulk-reading the tree yourself.
Use `@session-miner` only when the missing context lives in transcripts rather
than artifacts.

If the conversation produces durable terminology or decisions, update the
right documentation surface.

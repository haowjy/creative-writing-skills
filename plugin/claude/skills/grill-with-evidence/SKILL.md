---
name: grill-with-evidence
description: |
  Use when grilling should be grounded in evidence. Loads `/grill`, then checks the plan, terms, and assumptions against project artifacts first and primary sources when needed.
disable-model-invocation: true
metadata:
  type: reference
---

# Grill With Evidence

Load `/creative-writing-skills:grill` if it isn't already loaded.

Ground the grilling in evidence before you push the human on a disputed point.

Check the strongest source that answers the question:

- current artifacts already in context
- relevant repo docs, existing prompts, prior decisions, and project vocabulary
- source code and real implementations in the wild
- official docs, specs, and standards
- research, papers, and formal studies
- articles and secondary analysis
- first-hand accounts such as issue threads, forums, Reddit, and social media

Prefer primary and first-hand sources over summaries when possible. Treat
user-generated content cautiously: it is increasingly polluted by bots,
astroturfing, and other motivated actors, so corroborate before relying on it.

Read focused source material first. Prefer concrete artifacts and primary
sources over summaries and hearsay.

When the answer should come from project artifacts beyond what is already in
context, spawn a `@explorer`.

When the answer should come from primary sources beyond what is already in
context, search the web directly rather than hand-waving from memory.

When the missing context lives in prior conversation rather than artifacts,
spawn a `@session-miner`.

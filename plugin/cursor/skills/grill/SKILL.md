---
name: grill
description: |
  Use in conversation to stress-test a plan or direction. Interviews the human in rounds, asking every question that is ready with a recommended answer, until no decision is left open.
metadata:
  type: mode-shift
alwaysApply: false
---

# Grill

Load `/creative-writing-skills:intent-modeling` if it isn't already loaded.

Interview the human relentlessly about the plan or direction until you reach
a shared understanding. Map it as a decision tree: each decision branches
into the decisions that hang off it.

Work in rounds. Each round, ask every question whose prerequisites are
already settled, numbered, each with your recommended answer, worded so
"yes" accepts the recommendation. A question that depends on another one
still open waits for a later round. After the answers, recompute what is
now askable and run the next round. Finish when no question is left open.

Facts are yours to find: read artifacts and source material instead of
asking. Decisions are the human's.

---
name: llm-writing
description: Use when producing written artifacts for humans — catches default LLM writing patterns.
---

# LLM Writing

Load `/intent-modeling` if it isn't already loaded.

Recognizing default LLM writing behaviors is most of the battle — once you
notice the pull, you can judge whether to resist it for this particular piece.

## Behavioral Pulls

Filling structure without anchoring to purpose. Summarizing with labels
instead of explaining how things work. Stating conclusions without evidence.
Smoothing over uncertainty. Encoding corrections as prohibitions. Defining
by negation. Restating what was just said as a transition.

Not always wrong — the failure is when they happen by default.

## Conversational Bleed

Writing as if responding to a user when producing a document for a reader
who wasn't in the conversation. "It's not X — it's Y" corrects a
misconception nobody has. "Let's break this down" addresses a question
nobody asked.

Write for the reader. They have no context from the conversation that
prompted the document.

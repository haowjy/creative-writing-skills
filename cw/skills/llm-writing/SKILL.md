---
name: llm-writing
type: guardrail
description: Load when producing any written artifact for humans.
---

# LLM Writing

LLM training creates default writing behaviors that show up regardless of
domain. Recognizing them is most of the battle — once you notice the pull,
you can judge whether to resist it or let it through for this particular
piece.

## Behavioral Pulls

Generating fluent text that fills structural expectations without anchoring
to purpose. Summarizing with labels instead of explaining how things work.
Stating conclusions without showing evidence. Applying the same structure to
every document. Smoothing over genuine uncertainty. Encoding corrections as
absolute prohibitions. Defining things by what they aren't. Filling space
with transitions that restate what was just said.

These aren't always wrong. The failure is when they happen by default rather
than by choice.

## Conversational Mode Leaking into Documents

The most common structural tells come from writing as if responding to a user
when producing a document for a reader who wasn't in the conversation.
"It's not X — it's Y" corrects a misconception nobody has. "Let's break this
down" addresses a question nobody asked. "Here's the thing" builds suspense
for a reader who just wants the information. Fractal summaries recap a
conversation that didn't happen.

When writing a document, write for the reader. They have no context from the
conversation that prompted the document.

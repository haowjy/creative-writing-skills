---
name: grill-with-docs
description: Use when challenging a plan — grills the author against documented decisions and sharpens terminology.
---

# Grill With Docs

Load `/intent-modeling` if it isn't already loaded.

Interview the author relentlessly about every aspect of their plan until you
reach a shared understanding. Walk down each branch of the decision tree,
resolving dependencies between decisions one by one.

Keep each turn to the next unresolved branch or a small cluster of related
questions the author can answer in one reply, then wait. Provide your
recommended answer for each question.

## Starting the Session

Read the plan or proposed direction the author provides. Identify:

- **Decision branches** — choices that gate other choices
- **Dependency order** — which decisions must resolve first
- **Terms needing precision** — vague, overloaded, or undefined vocabulary
- **Assumptions** — things treated as given that may not be

Start with the highest-leverage unresolved dependency — the earliest branch
point that unblocks the most downstream decisions.

## Challenging Terminology

Check every significant term against the project's existing vocabulary where
it exists:

1. Vocabulary pages in the kb — `kb/vocab.md` for project-wide terms,
   `kb/<domain>/vocab.md` for domain-specific ones.
2. Project conventions in `CLAUDE.md` — established names and labels.
3. Active work notes in `work/` — terms already defined for the current effort.
4. Prior decisions — terms established by earlier choices.

When the author's language conflicts with documented terms, call it out
immediately. Name the conflict: "You said X, but the kb defines Y for this
concept — which should we use?"

Sharpen vague or overloaded terms into canonical terms. Use concrete
scenarios and edge cases to force precise boundaries — "Does 'sync' here mean
the timeline beat, the character's realization, or something new?" See
`/shared-dao` for the vocabulary discipline.

## Gathering Evidence

When answering requires cross-referencing project materials beyond what is
already in context, read the specific files directly, or spawn a focused
subagent to gather evidence so your own context stays on the grilling
conversation. Scope each lookup to one question and target specific files or
directories — chapters, kb entries, outlines, prior decisions.

Frame the lookup as an evidence-seeking question with file/path targets. Act
on findings to sharpen your next question or to challenge the author's
assumptions with evidence.

## Updating Documentation

Update artifacts inline as decisions crystallize. Reasoning flattens the
longer you wait — capture it in the moment.

### Active work notes

Record decisions in `work/` as they stabilize — the decision, the reasoning,
and any constraints that emerged. Keep open questions visible.

### KB vocabulary

When the session produces a new canonical term or refines an existing one,
update the appropriate vocabulary page: `kb/vocab.md` for cross-cutting
terms, `kb/<domain>/vocab.md` for domain-specific ones. Follow `/kb-management`
for page structure.

### Durable decisions

Create durable decision records sparingly — only when the choice is hard to
reverse, surprising without context, and involves a real tradeoff. Record it
in the relevant kb page. Keep provisional decisions in `work/` until they
prove durable.

## Session Rhythm

Each cycle through a decision branch:

1. State the branch and why it matters now (dependency context).
2. Ask focused questions with your recommended answer for each.
3. Wait for the author's response.
4. If the answer raises a sub-question, drill into it before moving on.
5. If the answer can be verified against project materials, check the relevant
   files and use what you find to confirm or challenge.
6. When the branch resolves, update the relevant documentation surface
   immediately.
7. Advance to the next branch.

The session ends when all branches of the decision tree are resolved and the
documentation reflects the shared understanding.

---
name: story-decisions
description: Story decision capture and mining — recording what was decided, what was rejected, and why, inline with the artifacts they relate to. Use whenever story direction is being chosen, brainstorm options are being narrowed, character or world choices are being made, or past decisions need to be recovered from session history.
---

# Story Decisions

Story decisions evaporate faster than code decisions. The reasoning behind a character's age, a meeting scene's tone, a timeline ordering, a rejected plot thread — it lives in brainstorm sessions that get compacted, in conversations that end, in the author's head between writing sessions. A month later, the question resurfaces: "why did we make Amber 8 instead of 10?" and the reasoning is gone. Worse, a writer agent drafts a scene that contradicts a decision nobody recorded.

Record decisions while the reasoning is fresh — in the moment the choice is made, not retroactively. A decision captured from memory after a long brainstorm flattens the nuance: alternatives blur together, constraints lose specificity, reasoning becomes post-hoc justification.

## What to Record

Every decision entry answers three questions: **what** was decided, **why** it was chosen, and **what else** was considered.

- **The choice itself.** State it concretely — name the characters, scenes, mechanics, or world elements affected. "We decided on a lighter tone" is vague. "The Route 1 meeting uses comedic misunderstanding, not a shared-threat scenario" is a decision.
- **The reasoning.** What constraints, goals, or creative instincts drove the choice? Was it narrative pacing? Character voice? Thematic consistency? Reasoning without specifics is opinion — "felt right" doesn't help the writer who needs to execute the decision six sessions later.
- **Alternatives rejected.** Name them and say why they were rejected. "We considered a combat-first meeting but rejected it because Amber doesn't have battle experience yet and it would require explaining her competence" is the most valuable sentence in any story decision record — it prevents the next brainstormer from re-proposing the rejected approach.
- **Constraints discovered.** Often the decision itself is less interesting than the constraint that forced it. "The timeline doesn't allow more than two days on Route 1" explains more than "we compressed the Route 1 arc."
- **What changed.** If this decision revises a prior one, reference what it replaces and why circumstances shifted. Story direction evolves — that's fine, but the evolution should be traceable.

## Where Decisions Live — Inline, Not Separate

Decisions are written inline with the artifacts they relate to in `$MERIDIAN_FS_DIR/`. Not in a separate decisions file. Not in a master log.

A character age decision lives in `$MERIDIAN_FS_DIR/characters/amber.md`, annotated where the age is stated. A timeline ordering decision lives in `$MERIDIAN_FS_DIR/timeline/`, annotated at the event sequence. A world mechanics decision lives in `$MERIDIAN_FS_DIR/world/`, annotated at the relevant system description.

This keeps decisions co-located with the facts they govern. When the writer loads a character file, they see not just the current state but *why* it's that way. When the continuity-checker flags a timeline issue, the reasoning for the ordering is right there.

### Annotation Format

```markdown
Amber is 8 years old at story start.
<!-- decision: Age set to 8. Considered 6 (too young for agency in early arcs)
     and 10 (too old for the vulnerability dynamic with Fuji). 8 balances
     competence with dependence. Session: p142, 2025-03-15 -->
```

Use HTML comments for decision annotations — they're invisible in rendered markdown but preserved in source. Include a session reference so the full discussion can be recovered via `meridian session` if needed.

## When to Record — and When to Skip

Record a decision when someone could reasonably make a different choice and the reasoning isn't obvious from the story itself. The test: would a writer agent need this context to draft a scene correctly?

Especially important when:
- Narrowing brainstorm options (the rejected alternatives are as valuable as the chosen one)
- Establishing character traits that constrain future scenes
- Ordering timeline events where the sequence affects plot logic
- Choosing tone or approach for a pivotal scene
- Overriding a critic's finding (record why the orchestrator disagreed)
- Revising a prior decision (what changed and why)

Skip decisions that follow directly from established canon or project conventions. If the story has already established that Amber can't battle yet, a scene brief that avoids combat isn't a decision worth recording — it's a constraint.

## Proactive Capture vs Retroactive Mining

### Proactive — Record as You Go

The story-orchestrator and knowledge-orchestrator record decisions in real time as brainstorming narrows options and direction crystallizes. This is the high-quality path — decisions captured in the moment retain their full context.

After a brainstorm session where options were explored and the author chose a direction: immediately dispatch the session-miner to extract decisions and write them inline to `$MERIDIAN_FS_DIR/`. Don't wait — the session context is richest right after the conversation.

### Retroactive — Mine Past Sessions

When decisions weren't captured in the moment (they often aren't), the session-miner can extract them from past session transcripts using `meridian session`. This recovers what would otherwise be lost, but the quality is lower — compacted sessions may have lost nuance, and the miner is reconstructing reasoning rather than recording it.

Use retroactive mining when:
- A writer or critic encounters a fact with no recorded reasoning
- Starting work on a new arc and needing to gather all prior decisions that constrain it
- Onboarding to a project with existing history but no decision annotations

The session-miner reads transcripts and writes decision annotations inline to the relevant `$MERIDIAN_FS_DIR/` entries, tagged with the source session for traceability.

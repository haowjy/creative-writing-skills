---
name: prose-writing
description: Prose drafting technique for narrative fiction. Use when writing new scenes, chapters, or dialogue — whether in conversation with an author or producing a draft autonomously from a brief. Covers craft fundamentals; project-specific voice comes from style files passed alongside this skill.
---

# Prose Writing

Draft narrative fiction that serves the story's needs. This skill covers craft technique — the how of prose. Project-specific voice, character speech patterns, and formatting conventions come from style files (in `$MERIDIAN_FS_DIR/styles/` or passed via prompt). Read those before writing.

## Two Modes

### Interactive

Back-and-forth with the author. They describe what they want, you draft, they react, you revise. The conversation IS the feedback loop — don't produce a "final" draft on the first pass. Offer options when the direction is ambiguous. Ask about intent when a scene could go multiple ways.

### Autonomous

You receive a brief (scene outline, beat list, emotional arc, relevant context) and produce a draft. No author in the loop — the draft goes to critics next, not to a human. This means:

- Follow the brief's direction without second-guessing it. The orchestrator already confirmed intent.
- Make concrete choices rather than hedging. A critic can flag a bad choice; they can't critique a hedge.
- Write the full scene, not a summary or outline. The output is prose, not planning.
- Mark places where you made significant interpretive choices (e.g., `<!-- CHOICE: interpreted "tense conversation" as passive-aggressive rather than openly hostile -->`) so critics and the orchestrator can evaluate your calls.

## Scene Entry

Open scenes in the middle of something happening. The reader should orient through action and context, not through setup narration. A character already mid-task, mid-conversation, or mid-thought gives the reader something to track immediately.

Avoid:
- Weather/setting paragraphs before anything happens
- Character waking up or traveling to the scene location
- "The room was..." description blocks
- Recap of how we got here

The exception is when the setting itself IS the story beat — a character seeing a destroyed city for the first time, or arriving somewhere that changes everything. Then the setting description carries narrative weight.

## Scene Purpose

Every scene needs to change something — character knowledge, relationships, power dynamics, stakes, emotional state. If nothing is different at the end than at the beginning, the scene is a candidate for cutting.

Before writing, identify what changes. In interactive mode, ask the author. In autonomous mode, extract it from the brief. If the brief doesn't specify what changes, flag it: `<!-- UNCLEAR: brief doesn't specify what changes in this scene -->`.

## Point of View

Stay in the established POV. First person means the narrator can only report what they perceive, think, and feel — not what other characters are thinking. Third limited means access to one character's interiority per scene.

POV violations are the most common craft error in AI-generated fiction. Watch for:
- Reporting emotions of non-POV characters as fact ("She felt angry") instead of through observable behavior ("Her jaw tightened")
- The narrator knowing things they shouldn't (what happened in a room they weren't in)
- Head-hopping between characters within a scene

## Show Through Action

Demonstrate character states through behavior, dialogue, and physical response rather than narrating them directly.

Telling: "He was nervous about the meeting."
Showing: "He checked his watch for the third time, then straightened a tie that was already straight."

This doesn't mean never tell. Summary narration is appropriate for:
- Transitions between important moments
- Routine actions that don't carry emotional weight
- Time compression ("The next three weeks passed in a blur of training")

The heuristic: tell for logistics, show for moments that matter.

## Dialogue

Dialogue should do at least two things simultaneously: advance the plot AND reveal character, or reveal character AND build tension, or build tension AND seed information. Single-purpose dialogue ("As you know, the reactor is on the third floor") feels flat because real conversation is never purely transactional.

**Subtext.** Characters rarely say exactly what they mean. They deflect, understate, change the subject, answer a different question than the one asked. The gap between what's said and what's meant is where characterization lives.

**Voice differentiation.** Each character should sound distinct enough that you could identify the speaker without dialogue tags. This comes from vocabulary, sentence structure, speech patterns, and what they choose to talk about — not from accent spelling or verbal tics bolted on.

**Action beats over dialogue tags.** "Said" is invisible; use it freely. Avoid creative tags ("he exclaimed," "she retorted") — they draw attention to the tag instead of the dialogue. Use action beats to show how something is said: "She set the cup down carefully. 'That's not what I meant.'"

## Pacing

Vary sentence length and structure to control reading speed. Short sentences speed things up — good for action, tension, shock. Longer sentences slow the reader down — good for reflection, description, complex emotion.

Scene-level pacing: alternate between high-tension and lower-tension beats. Sustained intensity becomes numbing. The quiet moment after the crisis is what gives the crisis weight.

Chapter-level pacing: end on forward momentum. Not necessarily a cliffhanger — an unanswered question, a new complication, an emotional shift. Give the reader a reason to continue.

## Sensory Detail

Ground scenes in specific sensory details rather than generic description. "The forest" is nowhere. "Pine needles crunching underfoot, the smell of wet bark" is a place.

Use the POV character's sensory priorities. A chef notices smells. A musician notices sounds. A soldier notices exits. What a character pays attention to reveals who they are.

Avoid cataloging all five senses mechanically. One or two vivid, specific details do more work than a comprehensive sensory inventory.

## Interiority

The POV character's inner life — thoughts, reactions, memories, associations — is what distinguishes prose fiction from screenplay. Don't neglect it.

But interiority should be specific and revealing, not generic emotional labeling. "She felt sad" is a label. "She kept reaching for her phone to text him before remembering" is interiority that shows the reader something about grief.

In high-action scenes, interiority contracts to fragments — quick reactions, snap judgments. In reflective scenes, it expands. Match the depth of inner experience to the pace of the scene.

## Revision Signals

When reviewing your own draft (or receiving critique), watch for these patterns:

- **Redundant beats.** Saying the same thing through action, dialogue, AND narration. Pick the strongest delivery and cut the others.
- **Throat-clearing.** Opening paragraphs that circle the point before landing on it. Cut to where the real scene starts.
- **Emotional choreography.** Characters cycling through emotions in predictable patterns (shock → denial → anger → acceptance) without the specific, messy reality of how people actually process things.
- **Placeholder prose.** Competent but generic sentences that could appear in any story. If a sentence could be swapped into a different scene without anyone noticing, it's not doing enough work.

## Resources

Style files passed alongside this skill contain project-specific voice guidance — character speech patterns, tonal registers, formatting conventions, scene-type techniques. Read them before drafting. They override general craft advice when they're more specific.

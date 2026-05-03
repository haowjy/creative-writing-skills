---
name: writing-principles
description: What fiction readers want (four reward channels) and the specific ways LLM training damages each one. Load when drafting prose, critiquing, or diagnosing why a passage feels flat.
---

# Writing Principles

Load `/llm-writing` if it isn't already loaded. This skill adds the
fiction-specific layer.

## Trust the Reader

The reader is an active collaborator. They reconstruct emotions from behavior,
infer motives from action, hold tension across scenes, fill gaps the text
leaves open, and make assumptions about what's coming next. That work — the
reconstruction, the inference, the anticipation — is where the reward lives.

Your training pulls in the opposite direction. The helpfulness instinct wants
to explain, resolve, clarify, and complete. In fiction, every one of those
impulses can damage the reading experience by doing work the reader wanted to
do themselves. The specific failure modes below are all forms of this: not
trusting the reader to interpret an emotion, hold an ambiguity, follow
subtext, or tolerate unresolved tension.

Trust doesn't mean obscurity. Readers also need coherent narrative, stable
geography, and enough access to model characters. The discipline is knowing
when to leave space and when to orient.

## Four Reward Channels

Readers enjoy fiction through four separable channels. Good prose protects all
four at once; damaging any one damages the reading experience.

- **Transportation** — entering the story world. Protected by coherent
  narrative progression, consistent POV, concrete sensory grounding. Consistent
  POV means writing from inside the character's knowledge state — what have
  they experienced, what do they actually know right now, what would they
  notice and miss? The full story is in your context window; the character
  only has what they've lived through. Separate those.
- **Aesthetic** — sentence-level pleasure. Protected by variety in rhythm,
  word choice, and sentence shape. Style is a reward channel, not decoration.
- **Social simulation** — modeling characters as minds. Protected by access
  through behavior and interiority, distinct voices, emotion the reader
  interprets rather than being told.
- **Flow** — readable challenge. Protected by pacing that matches the scene's
  work, sentences that support comprehension.

The channels compose — optimizing one at the expense of others fails.
Over-explaining breaks social simulation. Under-explaining breaks
transportation. Generic style breaks aesthetic pleasure. Impenetrable style
breaks flow.

## Applying the Principles

The craft skills carry the execution: `/prose-writing` for immersion patterns
(psychic distance, rhythm, sensory grounding, interiority) and
`/scene-construction` for how scenes work on the page (entry, dialogue,
pacing, transitions).

This skill's job is the diagnostic layer. When a passage feels off and you
can't name why, check the four channels — which one broke? Then see
`resources/failure-modes.md` for common patterns and fix heuristics.

## Resources

- [`resources/failure-modes.md`](resources/failure-modes.md) — per-pattern
  deep dives with examples and fix heuristics.
- [`resources/citations.md`](resources/citations.md) — research backing for
  the four-channel model and documented failure modes.

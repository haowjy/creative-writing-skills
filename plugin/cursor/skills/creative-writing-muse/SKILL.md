---
name: creative-writing-muse
alwaysApply: false
metadata:
  type: mode-shift
---

# Creative Writing Muse

Use this when there are no subagents. Act as the muse in one conversation by
loading the relevant writing skills and switching stances deliberately. Keep the
author-facing thread coherent while you move between direction, drafting,
critique, revision, and memory.

Start by understanding author intent: desired reader simulation, emotional
target, constraints, taste signals, open uncertainty, and what should remain
unsaid. Keep that intent visible as you change stance. The author has the final
say.

Before writing character prose, find the style and character state.

## Choose the Stance

Load the skills needed for the next stance:

- **Direction:** `/creative-writing-skills:story-planning`
- **Drafting:** `/creative-writing-skills:creative-writing-modes`, `/creative-writing-skills:creative-writing-craft`, `/creative-writing-skills:llm-writing`
- **Critique:** `/creative-writing-skills:story-review`, `/creative-writing-skills:reader-sim`, `/creative-writing-skills:writing-principles`
- **Research:** `/creative-writing-skills:creative-research`
- **Voice and terms:** `/creative-writing-skills:creative-writing-craft`, `/creative-writing-skills:character-sim`, `/creative-writing-skills:shared-dao`
- **Memory:** `/creative-writing-skills:story-memory`; also `/kb-management` and `/project-setup` if available

## Self-Prompt Before Each Stance

Before doing the next pass, name the prompt you are giving yourself:

- What is the author's intent for this pass?
- What reader effect should the output create or protect?
- Which constraints, style, character state, canon, and vocabulary matter now?
- What should remain ambiguous, unresolved, rough, or strange?
- What output should this pass produce?
- What would be the wrong kind of success?

Ask the author only when the answer would change the work. Otherwise state your
read and continue.

## Keep Stances Separate

Explore without committing too early. Draft before judging. Critique from the
reader's experience. Revise the highest-impact issue. Update memory only for
settled facts and decisions.

Before switching stance, synthesize what changed and whether the next move still
serves the author's intent. For pivotal passages, create two meaningfully
different takes and explain what each take proves.

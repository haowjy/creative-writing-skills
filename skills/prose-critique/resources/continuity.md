# Continuity Review

Evaluate factual consistency — timeline, geography, character state, and established rules.

## What to Cross-Reference

Continuity errors are factual contradictions between what the draft says and what the story has established. They're distinct from character or plot issues — a character acting inconsistently is a character problem; a character being in two places at once is a continuity problem.

### Character State

- **Physical state:** Injuries, abilities, possessions. A character who broke their arm in chapter 3 shouldn't be climbing a wall in chapter 4 without addressing it.
- **Knowledge state:** What does each character know at this point? Characters acting on information they haven't received yet is a continuity break.
- **Location:** Where is each character? Can they plausibly be where the scene needs them?
- **Relationships:** Have the right encounters happened? Is character A reacting to something character B said, and did that conversation actually happen?

### Timeline

- **Event ordering:** Do events happen in the established order? Are flashbacks placed correctly relative to the story's timeline?
- **Duration:** Does the time that passes match what's stated? If "two days later" is stated but the events described would take a week, that's a break.
- **Parallel threads:** Do simultaneous storylines stay synchronized? If character A's storyline covers a week and character B's covers three days, and they converge, the timeline needs to account for the gap.
- **Ages and dates:** Do character ages track correctly? Do seasonal or calendar references stay consistent?

### Geography

- **Travel time:** Can characters get from A to B in the time allotted? Are distance descriptions consistent?
- **Spatial relationships:** Do directions stay consistent? If the river is east of the city in chapter 2, it should still be east in chapter 10.
- **Scene blocking:** Within a scene, do character positions make sense? Can character A see what the narration says they see from where they're standing?

### Established Rules

- **World rules:** Do magic systems, technology, social structures operate consistently? If magic costs energy in chapter 5, it shouldn't be free in chapter 12 without explanation.
- **Character rules:** Do character abilities stay consistent? Skills and limitations established earlier should persist unless the narrative addresses the change.
- **Narrative rules:** If the story established that POV character can't know certain things, does that constraint hold?

## How to Report Continuity Findings

For each finding, provide:

1. **The contradiction** — what the draft says vs what was established
2. **Where it was established** — specific chapter/scene reference
3. **Where it contradicts** — specific location in the draft
4. **Severity** — does this break the reader's trust, or is it a minor inconsistency most readers wouldn't notice?

Some continuity breaks are more damaging than others. A character's eye color changing is minor. A character knowing about a conversation they weren't present for is serious — it undermines the reader's trust in the narrative.

## Continuity vs Intentional Change

Not every inconsistency is an error. The story might have:
- Unreliable narrators who contradict established facts intentionally
- Characters who lie or misremember
- Retcons the author made deliberately
- Evolving world rules (the magic system changes because of story events)

When flagging a potential break, note whether it could be intentional. "Character X states the attack was on Tuesday, but Chapter 3 established it was Thursday. If this is intentional (unreliable narrator, faulty memory), it should be signaled to the reader."

## Working with Project Knowledge

When available, cross-reference against:
- Timeline documents in `$MERIDIAN_FS_DIR/timeline/`
- Character state files in `$MERIDIAN_FS_DIR/characters/`
- Canon facts in `$MERIDIAN_FS_DIR/canon/`
- Wiki pages for established world facts

These are the project's knowledge base — use them as the source of truth for what's been established.

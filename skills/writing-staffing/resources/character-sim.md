# Character Simulation

Character exploration through performance. The `character-sim` agent becomes a character for freeform conversation — the author (or another agent) interacts with the character to discover voice, test dynamics, and explore reactions in unplotted situations.

## character-sim

Stays in character. Doesn't break to explain, doesn't over-narrate, doesn't meta-comment on the interaction. Responds as the character would — with their knowledge, their biases, their emotional state.

Works with whatever character context it's given:

- **Full context mode** — loads relevant style files from `$MERIDIAN_FS_DIR/styles/` and character state from `$MERIDIAN_FS_DIR/characters/`. The combination gives voice patterns AND factual grounding (what the character knows, where they are in the story, their relationships). Use when the character is established and the goal is to hear how they'd react to specific situations.

- **Ad hoc mode** — character description comes entirely from the prompt. "You're a 14-year-old from a fighting dojo who just lost his first real battle. You're proud, stubborn, and your dad is watching. React." No files needed. Use when:
  - The character doesn't exist yet
  - Sketching a one-off NPC
  - Exploring "what if" scenarios with modified traits
  - Testing a character concept before committing to a profile

## Use cases

**Voice discovery** — hear how a character sounds in different emotional states. Spawn a character-sim, give it a scenario, and observe the voice that emerges. Especially valuable for characters whose voice isn't established yet.

**Relationship testing** — play out unscripted encounters between characters. See how they interact without the author scripting the outcome. Reveals dynamics that planned scenes might miss.

**Stress testing** — confront a character with unexpected situations and see authentic reactions. "What would the protagonist do if she discovered the secret early?" The answer reveals character, even if the scenario never appears in the story.

**Ad hoc sketching** — describe a character on the fly, interact with them to discover who they are before writing anything down. Useful early in character development when the author has a vague sense and needs to find the specifics.

## Multi-character fan-out

The orchestrator spawns multiple character-sim agents as different characters in the same scene. Each loads a different voice and character state. They interact autonomously while the author observes.

```bash
# Two characters meeting for the first time
meridian spawn -a character-sim \
  -p "You are [character]. You've just arrived at the inn after a rough day on the road. Someone your age approaches you." \
  -f $MERIDIAN_FS_DIR/styles/[relevant style files] \
  -f $MERIDIAN_FS_DIR/characters/[character].md

meridian spawn -a character-sim \
  -p "You are [other character]. You've been waiting at the inn for a potential travel companion. Someone about your age walks in looking exhausted." \
  -f $MERIDIAN_FS_DIR/styles/voice-kyle.md \
  -f $MERIDIAN_FS_DIR/characters/kyle.md
```

The session-miner can later extract voice patterns, relationship dynamics, and character insights from the character-sim transcripts. The value is the conversation itself — character-sim is a read-only agent that doesn't write files.

## Staffing considerations

Character simulation is inherently cheap (read-only, no file writes, no tool use beyond conversation). Use it liberally for exploration. The cost of spawning a character-sim is much less than the cost of discovering a character's voice doesn't work after drafting an entire chapter.

## Relationship to reader-sim

Character-sim and `reader-sim` are symmetric simulation agents on different sides of the text: character-sim *produces* in-character behavior so the author can observe it, while reader-sim *consumes* a finished draft and reports the reading experience. Both are read-only, both report experience rather than craft findings, and both are cheap enough to spawn liberally.

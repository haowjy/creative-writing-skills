---
description: Context scoping for writing subagents — use when deciding what context a subagent should receive. Poor context handoffs cause writers to invent contradictions and critics to miss relevant history.
---

# Story Context

Every subagent spawn starts with a context decision. Get it wrong and the
writer invents facts that contradict established canon, the critic misses a
continuity issue because it never saw the relevant chapter, or the brainstormer
explores territory the author already rejected.

## What Each Agent Needs

### Writers

Writers need enough to stay in voice and on-canon, not everything ever written:

- **Scene brief or outline** — what happens in this scene, the beats to hit
- **Relevant style files** — check `kb/styles/` and pick the files that match.
  Character files for whoever appears, scene-type files for the kind of scene.
  Each style file is self-describing — read the top to know when it applies.
- **Continuity anchors** — the immediately preceding chapter or scene (for
  flow), plus any chapters that establish facts this scene references. Two to
  four files, not the entire manuscript.
- **Character state** — character files from `kb/characters/` for characters
  who appear, especially if their emotional state or knowledge has changed
  recently

Tell the writer where to find more if it needs to explore — "the full arc
outline is in `work/outline/`" — rather than passing everything preemptively.

### Critics

Critics need the draft plus enough context to judge it against:

- **The draft being reviewed**
- **The scene brief or outline** — so the critic can check whether the draft
  achieved what it was supposed to
- **Relevant style files** — so voice critics can compare against the target
- **Prior chapters for continuity** — so continuity critics can cross-reference
- **Known issues** — tracked issues in `kb/issues/` if the critic should watch
  for specific recurring problems

### Brainstormers

Brainstormers need constraints, not answers:

- **The question being explored** — scoped tightly in the prompt
- **Established context that constrains the answer** — character profiles,
  timeline, prior decisions
- **What's been rejected** — so they don't re-propose dead ends

Don't pass too much — brainstormers that receive the full project history tend
to produce conservative ideas instead of exploring fresh territory.

### Knowledge Maintenance

- **Chronicler**: the chapter(s) to extract facts from, plus existing kb
  entries for deduplication

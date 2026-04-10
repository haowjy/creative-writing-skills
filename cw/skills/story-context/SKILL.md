---
name: story-context
description: Context scoping for writing agent spawns — use when deciding what context a spawned agent should receive, whether ephemeral story decisions should be materialized before handoff, and how much to pass. Poor context handoffs cause writers to invent contradictions and critics to miss relevant history.
---

# Story Context

Every spawn starts with a context decision. Get it wrong and the writer invents facts that contradict established canon, the critic misses a continuity issue because it never saw the relevant chapter, or the brainstormer explores territory the author already rejected.

This skill teaches the judgment — what story context to pass, when to materialize decisions before spawning, and how much is enough.

## Choose the Right Mechanism

**File references — concrete artifacts.** Use when the context already exists as files: chapters, outlines, wiki pages, style files from `.meridian/fs/styles/`, character state from `.meridian/fs/characters/`. The agent reads exactly what you point it at. This is the default choice because files are stable, inspectable, and survive compaction.

```
# Good: writer gets the scene brief, relevant style files, and prior chapter for continuity
Spawn the writer agent using the Agent tool with these files:
  .meridian/work/<work-item>/outline/route1-brief.md
  .meridian/fs/styles/voice-amber-1p.md
  .meridian/fs/styles/scene-battle.md
  story/chapter4/4chapter.md

# Bad: dumping every chapter and style file "just in case"
```

**Conversation history.** Use when the agent needs to understand decisions, reasoning, or brainstorm context that hasn't been written down yet. Session history captures the *why* behind choices — why the author picked this meeting angle, what tone they want, what they explicitly rejected.

```
# Good: critic needs to understand the author's intent for this scene
Spawn the critic agent using the Agent tool, including relevant conversation context
and the draft file: .meridian/work/<work-item>/drafts/route1-v1.md

# Bad: passing conversation history when the direction is already captured in an outline
```

**Materialize first — when context is too important to be ephemeral.** If critical story decisions only live in conversation, write them to `.meridian/fs/` or `.meridian/work/<work-item>/` *before* spawning. Story direction decisions are especially important to materialize — if the author chose "comedic misunderstanding" over "shared threat" for a meeting scene, that reasoning needs to survive compaction. The writer who drafts the scene weeks later needs to know not just what was chosen, but what was rejected.

**Rule of thumb**: if a writer could accidentally contradict this context, materialize it. If it's supplementary background that enriches but isn't load-bearing, conversation history is fine.

## What Each Agent Needs

### Writers

Writers need enough to stay in voice and on-canon, not everything ever written. The essential context:

- **Scene brief or outline** — what happens in this scene, the beats to hit
- **Relevant style files** — POV voice (`voice-amber-1p.md`), scene-type technique (`scene-battle.md`), tonal register (`tone-grief.md`). Pick the ones that match the scene.
- **Continuity anchors** — the immediately preceding chapter or scene (for flow), plus any chapters that establish facts this scene references. Two to four files, not the entire manuscript.
- **Character state** — from `.meridian/fs/characters/` for characters who appear in the scene, especially if their emotional state or knowledge has changed recently

Tell the writer where to find more if it needs to explore — "the full arc outline is in the work directory, focus on the Route 1 section" — rather than attaching everything preemptively.

### Critics

Critics need the draft plus enough context to judge it against:

- **The draft being reviewed** — always as a file reference
- **The scene brief or outline** — so the critic can check whether the draft achieved what it was supposed to
- **Relevant style files** — so voice critics can compare against the target voice
- **Prior chapters for continuity** — so continuity critics can cross-reference facts
- **Author intent** — via conversation context if the orchestrator discussed direction with the author, or via materialized decision notes

### Brainstormers

Brainstormers need constraints, not answers:

- **The question being explored** — scoped tightly in the prompt
- **Established context that constrains the answer** — character profiles, timeline, prior decisions that limit the design space
- **What's been rejected** — so they don't re-propose dead ends

Don't pass too much — brainstormers that receive the full project history tend to produce conservative ideas that fit neatly into existing patterns instead of exploring fresh territory.

### Knowledge Maintenance Agents

- **Session-miner**: conversation context pointing at the conversation to mine, plus `.meridian/fs/` paths for where to write findings
- **Chronicler**: the chapter(s) to extract facts from as file references, plus existing `.meridian/fs/canon/` and `.meridian/fs/timeline/` for deduplication
- **Graph-maintainer**: the `.meridian/fs/` directory structure — it needs to see everything to rebuild connections

## Cross-Phase Context

Carry forward what a previous phase learned by including its outputs as context. The revision writer benefits from seeing what the first-draft writer discovered — where the outline was ambiguous, what choices were made to fill gaps. The critic benefits from seeing prior critique rounds — what was already flagged and addressed.

Combine mechanisms when phases produce artifacts: pass the prior spawn's reasoning context alongside the files it created for concrete outputs.

```
# Revision writer gets the critique synthesis AND the original draft
Spawn the writer agent using the Agent tool with:
  .meridian/work/<work-item>/drafts/route1-v1.md
  .meridian/work/<work-item>/critique-reports/round1-synthesis.md
Prompt: "Revise the Route 1 scene, addressing the pacing and voice findings"
```

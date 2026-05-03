---
description: Team composition for writing workflows — which subagents to use, how many, what focus areas to assign, and how to scale effort. Use when composing critic panels, staffing draft/revise loops, or setting up brainstorm fan-outs.
---

# Writing Staffing

Compose the right team for each writing task. The goal is coverage across
perspectives — critics with different focus areas, brainstormers exploring
different angles — not redundant passes from the same angle.

## General Principles

**Delegation keeps context clean.** Each mode of work benefits from a fresh
context window — drafting needs voice fidelity, critique needs adversarial
distance, research needs breadth. Use subagents to mode-switch rather than
doing everything in the main conversation.

**Review convergence.** Critic loops run until convergence (no new substantive
findings), not a fixed number of passes.

**Brainstorm diversity over brainstorm volume.** Three brainstormers exploring
different angles beats five exploring the same angle.

**Style creation and style evaluation are separate modes.** Creating style
reference files from sample prose is an analytical task (use @style-creator).
Evaluating whether a draft maintains voice is a critique task with voice
focus (use @critic).

## Effort Scaling

Effort scaling applies mainly to critics — the role that fans out within a
draft/revise cycle.

- Low-stakes drafts (brainstorm captures, wiki stubs): 1-2 critics
- Standard chapters: 3 critics with split focus areas
- Pivotal scenes (character deaths, reveals, arc climaxes): 4-5 critics

## Subagent Catalog

### Writers

- **@writer** — generative prose from briefs. One writer per scene/chapter.
  Use opus for voice fidelity.
- **@revision-writer** — surgical revision from critique findings. Preserves
  voice while fixing specific issues.
- **@bridge-writer** — transitions, time compression, connective passages
  between pivotal scenes.

### Critics and Reviewers

- **@critic** — adversarial prose critique. Fan out with different focus areas:
  voice, pacing, character, continuity. Sonnet default; use opus for
  final-pass on pivotal scenes.
- **@continuity-checker** — specialist: checks draft against canon files.
  Use when a scene references established facts.
- **@reader-sim** — experiential reading. Reports what it felt like to read
  the draft. Use for pivotal scenes or when something feels off but you can't
  name it. Opus for nuance.

### Exploration

- **@brainstormer** — wide-open idea exploration. Fan out for diversity.
- **@character-sim** — character voice performance. Spawn when you need to
  hear how a character talks or test relationship dynamics.
- **@outliner** — story structure at arc/chapter/beat levels.
- **@style-creator** — analyzes prose and produces style reference files.

### Knowledge

- **@chronicler** — extracts facts from chapters into the kb. Cheap (haiku)
  and focused.

## Parallelism

Think about what depends on what:

- Critics need a finished draft — they wait for the writer
- Critics examine different dimensions — fan them all out simultaneously
- Brainstormers are independent — fan them out
- Character simulations in a multi-character scene are independent — fan out
- Chronicler runs after a chapter is finalized, not during drafting

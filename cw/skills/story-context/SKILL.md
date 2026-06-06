---
name: story-context
description: >
  Context scoping for writing subagents: use when deciding what context a subagent should receive, whether ephemeral story decisions should be written down before handoff, and how much to pass. Poor context handoffs cause writers to invent contradictions and critics to miss relevant history.
---

# Story Context

Every subagent handoff starts with a context decision. Get it wrong and the
writer invents facts that contradict established canon, the critic misses a
continuity issue because it never saw the relevant chapter, or the brainstormer
explores territory the author already rejected.

A subagent only knows what you give it. This skill is the judgment: what story
context to pass, when to write decisions down before handing off, and how much
is enough.

## Choose the Right Mechanism

Three ways to get context to a subagent, each for a different situation.

**Point at files**: when context already exists as files — chapters, outlines,
wiki pages, style files, character state. Default choice, because files are
stable, inspectable, and survive compaction. Name the specific files in the
subagent's prompt and scope tightly: pass the files that matter, not everything.

**Put it in the prompt**: when the subagent needs decisions, reasoning, or
brainstorm context that hasn't been written down yet. Capture the *why* behind
choices directly in the prompt — why the author picked this angle, what they
rejected.

**Materialize first**: when context is too important to be ephemeral. If
critical story decisions only live in the conversation, write them to `kb/` or
`work/` *before* handing off. If a writer could accidentally contradict this
context, materialize it. If it's supplementary background, putting it in the
prompt is fine.

## What Each Agent Needs

### Writers

Writers need enough to stay in voice and on-canon, not everything ever written:

- **Scene brief or outline**: what happens in this scene, the beats to hit
- **Relevant style files**: check `kb/styles/` and pick the files that match.
  Character files for whoever appears, scene-type files for the kind of scene.
  Each style file is self-describing: read the top to know when it applies.
- **Continuity anchors**: the immediately preceding chapter or scene (for
  flow), plus any chapters that establish facts this scene references. Two to
  four files, not the entire manuscript.
- **Character state**: character files from `kb/characters/` for characters
  who appear, especially if their emotional state or knowledge has changed
  recently
- **Vocab**: relevant `vocab.md` files when the scene uses invented terms,
  magic/faction names, titles, relationship labels, or genre terms with
  project-specific meanings

Tell the writer where to find more if it needs to explore, for example: "the
full arc outline is in `work/outline/`; focus on the Route 1 section." Avoid
passing everything preemptively.

### Critics

Critics need the draft plus enough context to judge it against:

- **The draft being reviewed**
- **The scene brief or outline**: so the critic can check whether the draft
  achieved what it was supposed to
- **Relevant style files**: so voice critics can compare against the target
- **Prior chapters for continuity**: so continuity critics can cross-reference
- **Author intent**: the direction the author discussed, via materialized
  decision notes or directly in the prompt
- **Known issues**: tracked issues in `kb/issues/` if the critic should watch
  for specific recurring problems
- **Vocab**: relevant `vocab.md` files when consistency of naming, aliases,
  deprecated terms, or invented language matters

### Brainstormers

Brainstormers need constraints, not answers:

- **The question being explored**: scoped tightly in the prompt
- **Established context that constrains the answer**: character profiles,
  timeline, prior decisions that limit the design space
- **What's been rejected**: so they don't re-propose dead ends
- **Existing vocabulary**: enough vocab context to avoid minting new names for
  concepts the project has already named

Don't pass too much: brainstormers that receive the full project history tend
to produce conservative ideas that fit neatly into existing patterns instead of
exploring fresh territory.

### Knowledge Maintenance

- **Chronicler**: the chapter(s) to extract facts from, plus existing canon
  files, timeline entries, and vocab files for deduplication
- **Continuity-checker**: the draft plus canon, timeline, character state, and
  vocab files for any domains the draft touches

## Cross-Phase Context

Carry forward what a previous phase learned. The revision writer benefits from
seeing what the first-draft writer discovered; the critic benefits from seeing
prior critique rounds. When you run a multi-step loop, include the earlier
phase's notes and the files it produced in the next subagent's prompt — reasoning
context for the *why*, files for the *what*.

## Vocab Handoffs

Treat vocabulary as operational story context. If a writer, critic, or
brainstormer could choose the wrong name for a concept, pass the relevant
`vocab.md` file or write the decision down before handing off. This matters most
for magic systems, factions, recurring in-world phrases, titles, relationship
labels, and terms the author corrected during conversation.

When a session settles terminology, record it before handoff: canonical name,
meaning, aliases still in circulation, and boundaries that prevent likely
confusion.

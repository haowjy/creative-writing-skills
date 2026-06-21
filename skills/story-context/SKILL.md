---
name: story-context
type: reference
description: >
  Context scoping for writing handoffs. Use when deciding what story context to pass, whether to materialize decisions before handoff, and how much is enough.
---

# Story Context

Every spawn starts with a context decision. Get it wrong and the writer invents facts that contradict established canon, the critic misses a continuity issue because it never saw the relevant chapter, or the brainstormer explores territory the author already rejected.

The spawn mechanics (`-f`, `--from`, spawn commands) are documented in `meridian spawn -h`. This skill teaches the judgment: what story context to pass, when to materialize decisions before spawning, and how much is enough.

## Choose the Right Mechanism

Three options, each for a different situation. `meridian spawn -h` has the
command syntax; this section covers when to use which.

**Files (`-f`)**: when context already exists as files: chapters, outlines,
wiki pages, style files, character state. Default choice because files are
stable, inspectable, and survive compaction. Scope tightly: pass the files
that matter, not everything.

**Session history (`--from`)**: when the agent needs decisions, reasoning, or
brainstorm context that hasn't been written down yet. Session history captures
the *why* behind choices: why the author picked this angle, what they rejected.

**Materialize first**: when context is too important to be ephemeral. If
critical story decisions only live in conversation, write them to the kb or
work directory *before* spawning. If a writer could accidentally contradict
this context, materialize it. If it's supplementary background, `--from` is
fine.

## What Each Agent Needs

### Writers

Writers need enough to stay in voice and on-canon, not everything ever written. The essential context:

- **Scene brief or outline**: what happens in this scene, the beats to hit
- **Relevant style files**: look at what exists in the styles directory and pick the files that match the scene. Character files for whoever appears, scene-type files for the kind of scene being written. Each style file is self-describing: read the top to know when it applies.
- **Continuity anchors**: the immediately preceding chapter or scene (for flow), plus any chapters that establish facts this scene references. Two to four files, not the entire manuscript.
- **Character state**: character files for characters who appear in the scene, especially if their emotional state or knowledge has changed recently
- **Vocab**: relevant `vocab.md` files when the scene uses invented terms, magic/faction names, titles, relationship labels, or genre terms with project-specific meanings

Tell the writer where to find more if it needs to explore, for example: "the full arc outline is in the work directory; focus on the Route 1 section." Avoid attaching everything preemptively.

### Critics

Critics need the draft plus enough context to judge it against:

- **The draft being reviewed**: always via `-f`
- **The scene brief or outline**: so the critic can check whether the draft achieved what it was supposed to
- **Relevant style files**: so voice critics can compare against the target voice
- **Prior chapters for continuity**: so continuity critics can cross-reference facts
- **Author intent**: via `--from` if the orchestrator discussed direction with the author, or via materialized decision notes
- **Known issues**: tracked issues if the critic should watch for specific recurring problems
- **Vocab**: relevant `vocab.md` files when consistency of naming, aliases, deprecated terms, or invented language matters

### Brainstormers

Brainstormers need constraints, not answers:

- **The question being explored**: scoped tightly in the prompt
- **Established context that constrains the answer**: character profiles, timeline, prior decisions that limit the design space
- **What's been rejected**: so they don't re-propose dead ends
- **Existing vocabulary**: enough vocab context to avoid minting new names for concepts the project has already named

Don't pass too much: brainstormers that receive the full project history tend to produce conservative ideas that fit neatly into existing patterns instead of exploring fresh territory.

### Knowledge Maintenance

- **Chronicler**: the chapter(s) to extract facts from via `-f`, plus existing canon files, timeline entries, and vocab files for deduplication
- **Continuity-checker**: the draft plus canon, timeline, character state, and vocab files for any domains the draft touches
- **Base @kb-maintainer**: the kb directory structure: it needs to see everything to rebuild connections
- **Base @kb-writer**: `--from` pointing at the conversation to mine, plus kb paths for where to write findings

## Cross-Phase Context

Carry forward what a previous phase learned using `--from <prior-spawn-id>`.
The revision writer benefits from seeing what the first-draft writer
discovered. The critic benefits from seeing prior critique rounds.

Combine mechanisms when phases produce artifacts: `--from` for reasoning
context, `-f` for the files the prior phase created.

## Vocab Handoffs

Treat vocabulary as operational story context. If a writer, critic, or
brainstormer could choose the wrong name for a concept, pass the relevant
`vocab.md` file or materialize the decision before spawning. This matters most
for magic systems, factions, recurring in-world phrases, titles, relationship
labels, and terms the author corrected during conversation.

When a session settles terminology, record it before handoff: canonical name,
meaning, aliases still in circulation, and boundaries that prevent likely
confusion.

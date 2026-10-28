# Story Context

Every specialist handoff starts with a context decision. Get it wrong and the
writer invents facts that contradict established canon, the critic misses a
continuity issue because it never saw the relevant chapter, or the brainstormer
explores territory the author already rejected.

This resource covers the judgment: what story context to pass, when to materialize decisions before handoff, and how much is enough.

## Choose the Right Mechanism

Three options, each for a different situation:

**Pass files**: when context already exists as files — chapters, outlines,
wiki pages, style, character state. Default choice because files are
stable, inspectable, and survive compaction. Scope tightly: pass the files
that matter, not everything.

**Carry this conversation or a prior run**: when the agent needs decisions,
reasoning, or brainstorm context that has not been written down yet. The
carried context captures the *why* behind choices: why the author picked this
angle and what they rejected.

**Materialize first**: when context is too important to be ephemeral. If
critical story decisions only live in conversation, write them to the kb or
work directory *before* handoff. If a worker could accidentally contradict
this context, materialize it. If it is supplementary background, carry the
current conversation or a prior run.

## What Each Agent Needs

### Writers

Writers need enough to stay in voice and on-canon, not everything ever written. The essential context:

- **Scene brief or outline**: what happens in this scene, the beats to hit
- **Style**: how they sound. Look in the styles directory if this project has one; each reference says when it applies.
- **Character state**: history, circumstances, and current knowledge for whoever appears. Pass whatever this project uses. If you cannot pass it, tell the writer where it lives.
- **Continuity anchors**: the immediately preceding chapter or scene (for flow), plus any chapters that establish facts this scene references. Two to four files, not the entire manuscript.
- **Vocab**: relevant `vocab.md` files when the scene uses invented terms, magic/faction names, titles, relationship labels, or genre terms with project-specific meanings

Tell the writer where to find more if it needs to explore, for example: "the full arc outline is in the work directory; focus on the Route 1 section." Avoid passing everything preemptively.

### Critics

Critics need the draft plus enough context to judge it against:

- **The draft being reviewed**: always pass the draft files
- **The scene brief or outline**: so the critic can check whether the draft achieved what it was supposed to
- **Style**: so voice critics can compare against the target voice
- **Character state**: so character and continuity critics can check it
- **Prior chapters for continuity**: so continuity critics can cross-reference facts
- **Author intent**: carry this conversation or a prior run when the orchestrator discussed direction with the author, or pass materialized decision notes
- **Known issues**: tracked issues if the critic should watch for specific recurring problems
- **Vocab**: relevant `vocab.md` files when consistency of naming, aliases, deprecated terms, or invented language matters

### Brainstormers

Brainstormers need constraints, not answers:

- **The question being explored**: scoped tightly in the prompt
- **Established context that constrains the answer**: character state, timeline, prior decisions that limit the design space
- **What's been rejected**: so they don't re-propose dead ends
- **Existing vocabulary**: enough vocab context to avoid minting new names for concepts the project has already named

Don't pass too much: brainstormers that receive the full project history tend to produce conservative ideas that fit neatly into existing patterns instead of exploring fresh territory.

### Outliners

- **The confirmed direction**: what the author approved, with provisional parts marked
- **What came before**: existing outlines, character state, timeline, and the prior chapters the outline builds on

### Simulations

- **Reader simulation**: the draft, the reader persona, and the knowledge boundary: what this reader has already read
- **Character simulation**: the character's style and character-state files, plus the scenario or relationship to explore

### Style Analysis

- **Samples**: sample chapters or existing style files; without samples, the author's stated voice goals

### Research

- **The question**: scoped to what the story needs
- **Story context**: setting, period, and what the story currently assumes, so the researcher can flag contradictions

### Knowledge Maintenance

- **Fact extraction**: pass the chapter files to extract from, plus existing canon files, timeline entries, and vocab files for deduplication
- **Continuity-checker**: the draft plus canon, timeline, character state, and vocab files for any domains the draft touches
- **Character-state contradiction**: do not patch character state from a draft. Update only after the author confirms.
- **KB restructuring**: the full kb directory structure — needs to see everything to rebuild connections
- **Read past sessions**: carry the prior run to mine, and pass the kb paths where findings belong

## Cross-Phase Context

Carry forward what a previous phase learned. The writer benefits from seeing
what the prior draft pass discovered when revising. The critic benefits from
seeing prior critique rounds.

Combine mechanisms when phases produce artifacts: carry the prior run for
reasoning context, and pass files for the artifacts the prior phase created.

## Vocab Handoffs

Treat vocabulary as operational story context. If a writer, critic, or
brainstormer could choose the wrong name for a concept, pass the relevant
`vocab.md` file or materialize the decision before handing off. This matters most
for magic systems, factions, recurring in-world phrases, titles, relationship
labels, and terms the author corrected during conversation.

When a session settles terminology, record it before handoff: canonical name,
meaning, aliases still in circulation, and boundaries that prevent likely
confusion.

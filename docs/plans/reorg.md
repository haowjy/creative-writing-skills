# Creative-writing reorg: candidates

Proposals for the planned rewrite and reorg of this package, not yet decided. Each says
what it would change and why; Jimmy decides which to take.

## One review taxonomy in `/story-review`

`/story-review` divides a review two ways: five edit levels (editorial, developmental,
line, copyedit, proofreading) and six critique focuses (structure, character, voice,
prose, continuity, baseline), about 7,000 words across 13 resources. They overlap: a
developmental edit covers what the structure and character focuses cover, and a line
edit covers voice and prose. Muse has to choose a lens before it chooses a level or a
focus, and a check kept in two files drifts.

Proposal: keep the edit levels as the one axis, since editors and authors already work
in them; fold each focus file's checks into its level; keep continuity as its own lane,
since it reads across the project rather than the draft. Read the files before
deciding: some focus checks may not fit any level.

## Fold `continuity-checker` into `critic`

The continuity checker runs the critic's own `prose-critique/continuity.md`. Its reason
for being a separate agent was cost, which no longer holds: it defaults to Sonnet, and
a critic lane can be given Sonnet the same way. Folding it in removes one agent; the
line telling it to read across the project would move into `continuity.md`. This
interacts with the taxonomy above.

## `/story-memory` maps `/knowledge-layers` onto a story

kb-lead stays: it brings `/knowledge-layers` (colocate first, the kb records what spans
the project, pages say how things stand now, stale pages are deleted), and muse tells it
to load `/story-memory` for the story's specifics. `/story-memory` doesn't yet say how
the three places fall in a story, so kb-lead has to work it out. Open `/story-memory`
(or `kb-layout.md`) with the mapping:

| Place | In a story project |
|---|---|
| Beside the work (`AGENTS.md`, `.context/`) | A book or arc folder's `AGENTS.md`: rules for agents writing there, such as a POV rule. Its `.context/`: chapter notes and comments as files |
| KB (the project's `kb/`) | Canon, wiki, vocab, styles and writing issues: what spans the story |
| Work directory | Brainstorms, drafts, critique rounds |

Say that the story's kb is the project's `kb/`, not a runtime's context KB.

The notes-and-comments convention belongs here too: Meridian Flow's design
(meridian-flow-docs `work/notes-and-comments/decisions.md`) has the owner's decisions that
notes and comments are plain files in `.context/`, one file per comment, and that the
manuscript links to them with the linked words as the highlight
(`[the gate had been open all night](.context/notes/scene1.md/comments/pacing.md)`), and
that the convention is written into these skills. Its folder layout and front-matter
properties were proposed and not confirmed: settle them with Jimmy before writing them in.

## `/shared-dao` in the fiction lanes

writer, critic and continuity-checker load `/shared-dao`, whose first line loads
`/qi-layer` (how to write `AGENTS.md` and `.context/`), about 780 words per run. Once
story projects use a folder's `AGENTS.md` and `.context/` (the mapping above), lanes that
write notes or comments may need `/qi-layer`, and the one-name-per-concept discipline is
already in `kb-layout.md` (Vocab Pages) and `continuity.md` (Terminology). Decide with
that mapping whether each lane keeps it.

## `project-setup` as one file

After the 2026-11 cleanup each environment walkthrough in `project-setup/resources/` is a
few lines. Merge them into `SKILL.md`, then update the package `AGENTS.md` rule that says
one walkthrough per resource, and the meridian-cli bootstrap that names one.

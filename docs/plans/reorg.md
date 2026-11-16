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

## Fold `@continuity-checker` into `@critic`

The continuity checker runs the critic's own `prose-critique/continuity.md`. Its reason
for being a separate agent was cost, which no longer holds: it defaults to Sonnet, and
a critic lane can be given Sonnet the same way. Folding it in removes one agent; the
line telling it to read across the project would move into `continuity.md`. This
interacts with the taxonomy above.

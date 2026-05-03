# Creative Writing Project Setup

Guided creation of the project's `AGENTS.md` — the single source of truth that all agents read for project-specific conventions.

## Learn About the Project

- What kind of project — novel, short story collection, serial, screenplay?
- How far along — starting fresh, or existing chapters/worldbuilding?
- Single POV or multiple? Linear or non-linear timeline? How much worldbuilding?
- Where do they keep their writing (chapters, story files)? What's the layout?

## Writing Samples and Style

Ask about writing samples — these are the foundation for style analysis:

- Do they have sample chapters or scenes already written for this project?
- Do they have writing from other projects that captures the voice they want?
- Are there published works they want to draw style inspiration from?
- Any specific voice goals — close third, omniscient, first person? Formal, colloquial?

Collect whatever they have. Save samples to `$MERIDIAN_CONTEXT_KB_DIR/samples/` so they're available for future style analysis runs. Then offer to run style analysis on them immediately (`meridian spawn -a style-creator -f <samples>`). Style files are the most impactful thing to get right early — every writing agent depends on them.

If they're starting fresh with no samples, capture their voice goals in the AGENTS.md so style files can be created from early drafts once they exist.

## Propose and Iterate

Based on what you learn, draft an `AGENTS.md` and show it to the author. This should cover:

- **Project overview** — what the project is, one paragraph
- **Author's space** — where the author keeps their writing and how it's organized. Agents read from here, don't write to it.
- **KB structure** — what subdirectories exist under `$MERIDIAN_CONTEXT_KB_DIR` and what they're for. Suggest based on project complexity:
  - Simple (short story, single POV): maybe `characters/`, `canon/`, `styles/`
  - Medium (novel, few POVs): add `timeline/`
  - Complex (series, large world): add `world/`, `issues/`, `graphs/`
- **Voice and style** — what style files exist, what samples they're derived from, voice goals not yet captured in style files
- **Conventions** — anything project-specific: naming patterns, chapter numbering, POV tagging, spoiler handling

Present the draft and let the author adjust. Iterate until they're satisfied.

## Create the Files

Once approved:

1. Write `AGENTS.md` with the agreed content
2. Write `CLAUDE.md` containing `@AGENTS.md`
3. Create any kb directories referenced in the AGENTS.md
4. Save writing samples to `$MERIDIAN_CONTEXT_KB_DIR/samples/`
5. Create the standard work directories
6. If samples were provided, offer to spawn style-creator

## Existing Projects

If `AGENTS.md` already exists, read it first and suggest updates rather than overwriting.

---
name: project-setup
alwaysApply: false
metadata:
  type: checkpoint
---

# Project Setup

Set up a project once so every later session starts with the conventions it
needs: an `AGENTS.md`, a `kb/` layout, and style files when the author has
samples.

## First, Load One Environment Walkthrough

Ask the author where they work, or infer it from the session, then read exactly
one of these and follow its setup and walkthrough:

- `resources/meridian.md` — Meridian, with the package installed by `mars add`.
- `resources/claude-code.md` — Claude Code with this plugin.
- `resources/claude-desktop.md` — claude.ai, Claude Desktop, or Cowork.
- `resources/other-harnesses.md` — Codex, Cursor, OpenCode, or Grok.

Do not load the others.

## Learn About the Project

Ask about:

- What kind of project: novel, short story collection, serial?
- How far along: starting fresh, or existing chapters and worldbuilding?
- Single POV or multiple? Linear or non-linear timeline? How much worldbuilding?
- Where they keep their writing? What is the existing layout?

## Writing Samples and Style

Writing samples are the foundation for style analysis:

- Do they have sample chapters or scenes already written?
- Do they have writing from other projects that captures the voice they want?
- Are there published works they want to draw style inspiration from?
- Voice goals: close third, omniscient, first person? Formal, colloquial?

Collect whatever they have and save it to `kb/samples/`. If there is enough
material, offer to analyze it with `/creative-writing-skills:creative-writing-craft`: read the samples,
identify the voice dimensions, and write initial style files to `kb/styles/`.
Style files are the most impactful thing to get right early; every writing
agent depends on them.

If they are starting fresh, capture their voice goals in `AGENTS.md` so style
files can be created from the first drafts.

## Propose and Iterate

Draft `AGENTS.md` and show it to the author. Cover:

- **Project overview**: what the project is, one paragraph.
- **Author's space**: where the author keeps their writing and how it is
  organized. Agents read from here; they do not write to it.
- **KB structure**: which subdirectories exist under `kb/` and what each is
  for. Load `/creative-writing-skills:story-memory`; its `resources/kb-layout.md` has the layers,
  page conventions, and the default layout. Pick the subset this project
  needs: simple (short story, single POV), medium (novel, a few POVs), or
  complex (series, large world).
- **Voice and style**: which style files exist, which samples they came from,
  and which voice goals are not captured yet.
- **Conventions**: naming patterns, chapter numbering, POV tagging, spoiler
  handling, anything else project-specific.
- **Shared vocabulary**: early canonical terms, aliases, invented words, genre
  terms with project-specific meanings, and terms agents should avoid or
  distinguish.

Present the draft and let the author adjust until they are satisfied.

## Create the Files

Once approved:

1. Write or update `AGENTS.md` with the agreed content.
2. Create the `kb/` directories it names.
3. Create `kb/vocab.md` when the project has named concepts agents must use
   consistently; add domain vocab files when a domain already has enough
   distinct terms.
4. Create `work/` with `outline/`, `drafts/`, `critique-reports/`, and
   `brainstorm/`.
5. Save the writing samples to `kb/samples/`.
6. If samples were provided and the author wants it, produce initial style
   files in `kb/styles/`.

## Existing Projects

If `AGENTS.md` already has creative writing conventions, read it first and
propose updates. Do not overwrite the author's decisions.

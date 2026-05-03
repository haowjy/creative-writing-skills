---
description: One-time project setup for creative writing. Interviews you about your project, collects writing samples, proposes kb structure, and creates CLAUDE.md with project conventions.
model-invocable: false
---

# Project Setup

Guide the author through setting up their creative writing project. The goal
is a working `CLAUDE.md` and directory structure that all agents read for
project-specific conventions, plus initial style files if writing samples are
available.

## Learn About the Project

Ask about:

- What kind of project — novel, short story collection, serial?
- How far along — starting fresh, or existing chapters and worldbuilding?
- Single POV or multiple? Linear or non-linear timeline? How much worldbuilding?
- Where do they keep their writing? What's the existing layout?

## Writing Samples and Style

Ask about writing samples — these are the foundation for style analysis:

- Do they have sample chapters or scenes already written?
- Do they have writing from other projects that captures the voice they want?
- Are there published works they want to draw style inspiration from?
- Voice goals — close third, omniscient, first person? Formal, colloquial?

Collect whatever they have. Save samples to `kb/samples/` so they're available
for future style analysis. If they have enough material, offer to analyze
their style using the `/style-analysis` methodology — read the samples,
identify the voice dimensions, and produce initial style files in `kb/styles/`.

If they're starting fresh with no samples, capture their voice goals in
CLAUDE.md so style files can be created from early drafts.

## Propose and Iterate

Based on what you learn, draft a `CLAUDE.md` section and show it to the
author. Cover:

- **Project overview** — what the project is, one paragraph
- **Author's space** — where the author keeps their writing and how it's
  organized
- **KB structure** — what subdirectories exist under `kb/` and what they're
  for. Suggest based on project complexity:
  - Simple (short story, single POV): `characters/`, `canon/`, `styles/`
  - Medium (novel, few POVs): add `timeline/`
  - Complex (series, large world): add `world/`, `issues/`
- **Voice and style** — what style files exist, what samples they're derived
  from, voice goals not yet captured
- **Conventions** — anything project-specific: naming patterns, chapter
  numbering, POV tagging, spoiler handling

Present the draft and let the author adjust. Iterate until they're satisfied.

## Create the Files

Once approved:

1. Write or update `CLAUDE.md` with the agreed content
2. Create the `kb/` directories referenced in CLAUDE.md
3. Create `work/` with standard subdirectories (outline/, drafts/,
   critique-reports/, brainstorm/)
4. Save any writing samples to `kb/samples/`
5. If samples were provided and the author wants style analysis, produce
   initial style files in `kb/styles/`

## Existing Projects

If `CLAUDE.md` already has creative writing conventions, read it first and
suggest updates rather than overwriting.

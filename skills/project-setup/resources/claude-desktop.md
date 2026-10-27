# claude.ai, Claude Desktop, and Cowork

These all install skills from the plugin marketplace. Cowork also runs the
agents; claude.ai chat runs skills only.

## Setup

Add the marketplace from the repository: **Customize** → **Personal plugins**
→ **+** → **Create plugins** → **Add marketplace** → **Add from repository**,
enter `haowjy/creative-writing-skills`, then sync and install the
**creative-writing-skills** plugin.

To load skills one at a time instead, download the `.skill` files from the
[latest release](https://github.com/haowjy/creative-writing-skills/releases/latest)
and use **Customize** → **Skills** → **+** → **Upload skill**.

## First Session

1. Run `project-setup` from the plugin (on claude.ai, select the
   **project-setup** skill). It runs the same interview and produces
   `AGENTS.md`, the `kb/` layout, and style files when samples exist.
2. On claude.ai there is no project filesystem: the setup comes back as text
   for you to save, and later sessions need the relevant parts pasted in. In
   Cowork the files are written to the project.
3. Turn on **creative-writing-muse** and describe the project. On claude.ai it
   is the whole session agent; in Cowork the muse agent coordinates and can
   dispatch the writer and critic.

## A Chapter

1. Ask for a plan: beats, POV, what the chapter must accomplish.
2. Ask for the draft, with the style and character state for everyone who
   appears.
3. Ask for a critique on one focus area (structure, character, voice, prose,
   continuity), then for the revision that addresses it.
4. Ask to update the kb with what the chapter establishes.

With agents (Cowork), each step can go to the specialist agent; on claude.ai,
`creative-writing-muse` does them in one conversation using the craft skills.

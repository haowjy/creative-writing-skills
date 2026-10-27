# Meridian

Meridian runs `muse` as the session agent and can spawn the other agents as
separate sessions, each with its own context.

## Setup

Add the package to the project, then sync it. This needs Meridian with Mars
0.20 or newer.

```bash
meridian mars add haowjy/creative-writing-skills
meridian mars sync
```

Run `meridian` in the project directory. The session runs as `muse`; a new
project runs the setup bootstrap on first launch.

## First Session

1. Run this setup skill if the project has no `AGENTS.md` yet. Answer the
   interview; it writes `AGENTS.md`, the `kb/` layout, and style files when
   samples exist.
2. Start `muse` and describe what you are working on. It reads `AGENTS.md`
   and the kb before proposing a next step.

## A Chapter

1. Ask `muse` for a chapter plan, or spawn the outliner directly:
   `meridian spawn -a outliner -f work/outline/current.md`.
2. `muse` spawns `writer` with the brief, style file, and character state.
3. `muse` spawns `critic` on the draft, one focus area at a time, and
   synthesizes what to change.
4. When the chapter settles, `muse` runs `story-memory` to update the kb.

Spawn any agent by name when you want it to own a session:
`meridian spawn -a critic -f story/ch04.md`.

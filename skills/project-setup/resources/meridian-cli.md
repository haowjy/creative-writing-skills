# meridian-cli

meridian-cli is the command-line tool. It runs `muse` as the session agent and
can spawn the other agents as separate sessions, each with its own context.

## Setup

Add the package to the project, then sync it. This needs meridian-cli with Mars
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
2. `muse` drafts the chapter with you from the plan, the style file, and the
   character state. It spawns `writer` for an alternate take on another model,
   a polish pass you ask for, or a draft too long to hold in one session.
3. `muse` spawns `critic` on the draft, one lane at a time (a focus area or
   an edit level), and synthesizes what to change, for up to two rounds.
4. When the chapter settles, `muse` spawns `kb-lead` to update the kb.

Spawn any agent by name when you want it to own a session:
`meridian spawn -a critic -f story/ch04.md`.

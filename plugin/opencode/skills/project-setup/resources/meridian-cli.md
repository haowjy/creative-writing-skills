# meridian-cli

meridian-cli is the command-line tool. It runs `muse` as the session agent and
can spawn the other agents as separate sessions, each with its own context.

## Setup

Add the package to the project, then sync it.

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

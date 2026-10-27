# Claude Code

The plugin installs every agent and skill under the `creative-writing-skills`
namespace.

## Setup

```text
/plugin marketplace add haowjy/creative-writing-skills
/plugin install creative-writing-skills@creative-writing-skills
```

Then start a session with `muse` as the agent:

```bash
claude --agent creative-writing-skills:muse
```

`muse` dispatches the other agents (`outliner`, `writer`, `critic`,
`continuity-checker`, `reader-sim`, and the rest). Any of them can own a
session when you want to work on one thing: `claude --agent
creative-writing-skills:outliner`. Skills are invoked as
`/creative-writing-skills:<skill>`.

## First Session

1. In a normal Claude Code session in the project, run
   `/creative-writing-skills:project-setup`. This skill is user-invoked only:
   agents do not call it. It creates `AGENTS.md`, the `kb/` layout, and style
   files when you have samples.
2. Start `claude --agent creative-writing-skills:muse` and describe the
   project. It reads `AGENTS.md` and the kb before proposing a next step.

## A Chapter

1. Ask `muse` for a chapter plan; it dispatches `outliner` with the confirmed
   direction.
2. `muse` dispatches `writer` with the brief, style file, and character state
   for everyone who appears.
3. `muse` dispatches `critic` on the draft, one focus area at a time, and
   turns the reports into what to change. It adds `continuity-checker` or
   `reader-sim` when the chapter is pivotal.
4. When the chapter settles, `muse` uses `story-memory` to update the kb.

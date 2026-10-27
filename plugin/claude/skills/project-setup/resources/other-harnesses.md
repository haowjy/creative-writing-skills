# Other Harnesses

The plugin also builds for Codex, Cursor, OpenCode, and Grok. Codex and
OpenCode load skills but not agents, so use the `creative-writing-muse` skill
there; Cursor and Grok load the agents too.

## Codex

```bash
codex plugin marketplace add haowjy/creative-writing-skills
codex plugin add creative-writing-skills@creative-writing-skills
```

Skills load; agents do not. For setup, run the `project-setup` skill. For
writing, load `creative-writing-muse` and work in one session: plan, draft,
critique, revise.

## Cursor

```bash
agent plugin marketplace add https://github.com/haowjy/creative-writing-skills
```

Then install the plugin from Cursor's Customize UI. For local development,
point the agent at the built tree: `agent --plugin-dir <checkout>/plugin/cursor`.
Agents and skills load.

## OpenCode

```bash
opencode plugin add git+https://github.com/haowjy/creative-writing-skills.git
```

Skills load; agents do not. Use `creative-writing-muse` as above.

## Grok

```bash
grok plugin marketplace add https://github.com/haowjy/creative-writing-skills
grok plugin install creative-writing-skills --trust
```

Agents and skills load from the same tree Claude Code uses.

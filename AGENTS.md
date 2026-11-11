# creative-writing-skills

Agents and skills for writing fiction: `muse` is the author's creative partner, and
specialist agents draft, critique, simulate readers and keep the story's KB. The same
source ships to meridian-cli and Claude Code projects through `mars add`, as a plugin for
Claude Code, Codex, Cursor and OpenCode, and as Claude.ai skill zips on each GitHub
Release. Codex, OpenCode and Claude.ai users get the skills but no agents.

## Rules

- **Write muse's method into the skills.** `creative-writing-muse` and `story-workflow`
  are the only copy of how muse works; the `muse` agent body holds only its job, the
  verdict it owns, the `@kb-lead` hand-off and its report. Behavior written into the
  agent body never reaches the users who get skills but no agents. The split mirrors
  meridian-dev-workflow's `/solo-dev` and `/dev-workflow`, so a lesson from one package
  has an obvious home in the other.
- **`plugin/` and the root catalogs are Mars output.** `meridian mars build plugin`
  writes `plugin/`, `.claude-plugin/`, `.cursor-plugin/` and `package.json` from the
  source and the published dependency graph; commit them with the source change that
  caused them. CI rebuilds with the `mars-agents` version pinned in
  `.github/workflows/ci.yml` and fails on any diff, so a hand edit, a stale tree, or a
  tree built by a different Mars version fails it.
- **Widen the dependency filters deliberately.** The `agents` and `skills` lists on
  `[dependencies.meridian-base]` in `mars.toml` hold every meridian-base item the shipped
  prose names, and each item they add is surface plugin users see. Keep include mode:
  it is what keeps meridian-base's `context-autosync` hook out of the plugin.
- **Destination sync comes from the `writing-sync` dependency.** Don't vendor its
  skills here.
- **Project setup has one interview.** `skills/project-setup` is
  `model-invocable: false` (users start it, agents never do); its resources hold one
  walkthrough per environment and `SKILL.md` loads exactly one.
  `bootstrap/project-setup`, meridian-cli's first-run document, only names the skill
  and the walkthrough to follow.

## Commands

```bash
meridian mars build plugin                         # rebuild plugin/ and the catalogs
meridian mars check                                # package, frontmatter, stale plugin output
python3 scripts/check_refs.py                      # every @agent and /skill in plugin/claude resolves
claude plugins validate plugin/claude              # plugin manifest and components
claude plugins validate .claude-plugin/marketplace.json
python3 scripts/create_skill_zips.py               # Claude.ai zips/*.skill (CI does this on release)
git config core.hooksPath .githooks                # once per clone: run these checks at commit
```

Rebuild, then run `check_refs.py`, after any edit that names an agent or a skill: it
fails when the dependency filters drop something a shipped file names. The pre-commit
hook skips its Mars checks when bare `mars` isn't on PATH.

## Watching

- **Muse runs the lifecycle from `/story-workflow`.** On the next muse
  sessions, and the next claude.ai or Codex sessions with
  `creative-writing-muse` on: it states its read in a line instead of a
  question list; it drafts in its own context and spawns `@writer` only for
  an alternate take, an author-asked polish pass, or a very long draft; every
  plan marks confirmed versus provisional parts; after two critique rounds on
  a chapter it presents the open concerns and lets the author decide.
- **`@kb-lead` briefs name what settled.** When a chapter or ruling
  settles, muse spawns `@kb-lead` with what settled and the files that show
  it, and a trial direction lands in the kb as a trial, not canon (#10). If
  trials still harden, story-memory needs the three kinds of story knowledge
  #10.1 proposes.
- **`@critic` covers editorial review.** Asked for an editorial review, a
  critic reads the whole draft before writing,
  leads with the overall diagnosis, orders notes by reader cost, and writes
  no replacement prose. Callers name a focus area or an edit level; a critic
  with neither says which lane it chose.
- **Writer and critic without `/llm-writing`.** Writer drafts and line
  polish avoid the negation pairs and summary endings `antipatterns.md`
  lists, and the writer's report stays readable. If drafts show more
  explanatory smoothing than before, compare a run with `/llm-writing` back
  on the same brief before restoring it.
- **Staffing says "tell it to load", not "attach" (#11).** Meridian muse runs
  still get the named skills onto the spawn, and Claude Code subagents load
  them when the brief names them.

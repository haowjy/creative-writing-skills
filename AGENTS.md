# AGENTS.md

This file provides guidance to AI Agents when working with this repository.

## Repository Overview

A Mars source package providing composable creative writing agents and skills for meridian-cli and Claude Code. Also distributes Claude.ai skill uploads via GitHub Releases.

## Key Distinctions

**`skills/` vs `plugin/`:** `skills/` and `agents/` are the Mars source: consumed by Claude Code and meridian-cli projects via `mars add`. `plugin/` is Mars-owned output: `mars build plugin` lowers the source plus the dependency graph into Claude/Codex/Grok, Cursor, and OpenCode trees and writes the marketplace catalogs. Never edit `plugin/` or those catalogs by hand; edit the source and rebuild (see [Building the plugin](#building-the-plugin)). CI fails on a stale or hand-edited tree.

**Agents vs skills:** Agents are spawned as independent processes (orchestrators, writers, critics). Skills are reference material loaded into agent context (craft knowledge, patterns, conventions). See `agents/` and `skills/` directories.

**Destination sync:** Comes from the `writing-sync` Mars dependency (`haowjy/writing-sync`), not this repo. Do not vendor those skills here.

## Package Management

This repo is both a Mars source package (publishes agents/skills) and a Mars consumer (depends on `meridian-base`).

```bash
mars check                   # Validate package, schema, and plugin output state
./scripts/release.sh patch   # Bump version, rebuild plugin/, commit, tag
```

Version lives in `mars.toml` under `[package]`. Tags trigger CI releases. Release with `scripts/release.sh` rather than `mars version` until [mars-agents#239](https://github.com/haowjy/mars-agents/issues/239) ships: a single build leaves `plugin/.mars-plugin.json` different from a rebuild, which fails CI's rebuild-and-diff check, so the script builds twice.

**Version sync:** `scripts/release.sh` bumps `mars.toml`, rebuilds `plugin/` and the root catalogs at the new version, and commits them together, so the plugin version never lags `mars.toml`.

**meridian-cli session roots:** meridian-cli spawns resolve `MERIDIAN_TASK_DIR` for the
checkout where source work happens, but `MERIDIAN_PROJECT_DIR` stays anchored to
the session control root for state, profiles, and context. Nested
`meridian ...` commands use project-root resolution, so CWD alone may not target
this package. `scripts/release.sh` anchors itself to the repository root; when
running Mars by hand from an inherited meridian-cli environment, pass the root
explicitly:

```bash
mars build plugin --root "$PWD"
```

Use explicit `-C <package-root>` whenever running meridian-cli commands for this
package from an inherited meridian-cli environment. For task checkouts, prefer
`meridian -C "$MERIDIAN_TASK_DIR" ...`.

Release with `mars` directly, not `meridian mars`: the Mars bundled in current
meridian-cli releases predates schema 1 and `[plugin]`, so it cannot build the
plugin tree or read this package.

## Building the plugin

`mars build plugin` writes `plugin/` and the files Mars owns at the package root (`.claude-plugin/marketplace.json`, `.cursor-plugin/marketplace.json`, `package.json`) from `agents/`, `skills/`, `bootstrap/`, the `mars.toml` dependency filters, and the resolved dependency graph. Commit the generated tree with the source change that caused it.

```bash
mars build plugin        # needs Mars 0.20.2 or newer
mars check               # reports stale, hand-edited, or missing plugin output
```

The build reads published state only (`mars.toml` plus the dependency graph), never `mars.local.toml`, `mars.lock`, or `.mars/`. The plugin ships this package's agents plus the skills and delegates they name: the `agents` and `skills` filters on `[dependencies.meridian-base]` keep meridian-base's operational surface and its `context-autosync` hook out, `writing-sync` contributes its one skill, and no hand-adapted copy exists any more. Both lists hold the closure of the prose references in the shipped tree — what Mars cannot infer from frontmatter — and `scripts/check_refs.py` fails the build when the closure grows; widen them deliberately, because a dependency skill or agent that comes back in is user-visible surface. Prefer widening over switching to `exclude`: include mode is what keeps the hook out.

`skills/project-setup` is `model-invocable: false`, so Mars lowers it to a user-invoked `/creative-writing-skills:project-setup`; its resources hold one setup walkthrough per environment, and `SKILL.md` loads exactly one. `bootstrap/project-setup` is its meridian-cli automatic-setup counterpart: bootstrap documents have no plugin surface, so it is not in the plugin, and the meridian-cli first-run document only names the skill and the walkthrough to follow, so the interview has one source.

**`creative-writing-muse`:** source lives in `skills/creative-writing-muse` and reaches the plugin through the same build. It is a user-activated, single-agent muse mode for skills-only environments; the `muse` agents do not load it. The agents follow the Product Lead pattern directly: capture author intent, craft specialist prompts, route work, synthesize results, and speak back to the author.

**Plugin manifest:** `plugin/claude/.claude-plugin/plugin.json` is generated from `[package]` (name, version, description, first author, homepage, license). Claude Code auto-discovers components without it, but the marketplace **add-from-GitHub** path (Cowork / claude.ai) validates the plugin and *rejects it* if the manifest is missing. `claude plugins validate .claude-plugin/marketplace.json` only checks the marketplace schema, not the plugin — so CI also runs `claude plugins validate plugin/claude`, which validates the manifest plus every agent/skill component file.

## Design Patterns

**Source tagging (brainstorming):** Untagged = user stated. `<AI>...</AI>` = AI suggestion. `<hidden>...</hidden>` = author-only (twists, secrets).

**Citations (kb pages):** Chapter references (`Chapter 3: Scene where X discovers Y`) and document references (`magic-system.md`).

**Style guides:** Directive AI instructions, not human documentation. Imperative form + examples.

## Development

**Build Claude.ai zips:** `python3 scripts/create_skill_zips.py` → `zips/*.skill` (packages `plugin/claude/skills`)

**Validate package and plugin:** `mars check`

**Check references:** `python3 scripts/check_refs.py` lists every `@agent` and `/skill` in the built `plugin/claude` tree that does not resolve to a shipped item. CI and the pre-commit hook run it after the rebuild, so a filter that drops an item another file names fails there instead of shipping. Run it after any source edit that mentions an agent or a skill.

**Rebuild the plugin:** `mars build plugin`, then commit `plugin/`

**Validate plugin manifest:** `claude plugins validate .claude-plugin/marketplace.json` (marketplace schema) and `claude plugins validate plugin/claude` (plugin manifest + components)

**Release flow:** `./scripts/release.sh [patch|minor|major] [--push]` bumps `mars.toml`, rebuilds `plugin/`, commits `vX.Y.Z`, and tags it. Push the tag (the script's `--push` does it) and CI creates the GitHub Release with `.skill` artifacts.

**Pre-commit hook:** `.githooks/pre-commit` front-loads the distribution-breaking checks (`mars build plugin` + `mars check`, then a dirty-tree check on the generated paths, then the reference check, then `claude plugins validate` for the Claude tree and marketplace) so they fire at commit time instead of only in CI. It's committed but not auto-installed — enable it once per clone:

```bash
git config core.hooksPath .githooks
```

It blocks the commit on failure; bypass a single commit with `git commit --no-verify`. (Skips a check when its CLI, `mars` or `claude`, isn't on PATH.)

**CI:** PRs run `mars check` + a rebuild-and-diff check on `plugin/` and the root catalogs + the reference check (`scripts/check_refs.py`) + Claude plugin/marketplace validation (`claude plugins validate`) + frontmatter validation + zip build. `mars check` only warns about stale output, so the rebuild-and-diff step is what fails the build. CI pins `mars-agents==0.20.2` because the committed tree is compared against the Mars that built it. Tag pushes create releases.

## Conventions

- Each skill's `SKILL.md` uses YAML frontmatter with `name` and `description`
- Skills may reference another skill by name; the dependency filter ships the closure of those references and `scripts/check_refs.py` proves it resolves
- Agent profiles declare their skills in the `skills:` frontmatter block
- Generated directories (`.agents/`, `.claude/`, `.codex/`, `.cursor/` and `.opencode/` agent and skill output, `.mars/`, `.meridian/`) are gitignored; `mars sync` writes them

## Watching

Behavior a released change expects but no real run has shown yet. Check it on
the next runs that exercise it, then delete the entry, fixing the prompt first
if the runs show otherwise.

- **writer on `argon` (0.5.15).** No spawn has run on Gemini 4 Argon yet, and
  its tool calling is reported unreliable. On the first writer runs routed to
  it: it reads the brief, style and character-state files, writes the draft
  where the brief says, and follows the style. If the tool loop fails, make
  the writer's work text in, text out, or move the default back to Opus.

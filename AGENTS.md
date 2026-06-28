# AGENTS.md

This file provides guidance to AI Agents when working with this repository.

## Repository Overview

A Mars source package providing composable creative writing agents and skills for Meridian and Claude Code. Also distributes Claude.ai skill uploads via GitHub Releases.

## Key Distinctions

**`skills/` vs `cw/skills/`:** `skills/` is the Mars source: consumed by Claude Code projects via `mars add`. `cw/skills/` holds the Claude.ai / plugin distribution — genericized copies with Meridian-specific references removed. Edit `skills/` first, then resync `cw/` (see [Syncing the `cw/` distribution](#syncing-the-cw-distribution)). CI fails on drift, so this is not optional.

**Agents vs skills:** Agents are spawned as independent processes (orchestrators, writers, critics). Skills are reference material loaded into agent context (craft knowledge, patterns, conventions). See `agents/` and `skills/` directories.

## Package Management

This repo is both a Mars source package (publishes agents/skills) and a Mars consumer (depends on `meridian-base`).

```bash
meridian mars check     # Validate package structure and frontmatter
meridian mars sync      # Install dependencies into .agents/
meridian mars version patch  # Bump version, commit, tag
```

Version lives in `mars.toml` under `[package]`. Tags trigger CI releases.

**Marketplace catalog version:** `mars version patch` bumps `mars.toml` but does **not** touch `.claude-plugin/marketplace.json`. When you bump the package, also bump `metadata.version` there by hand to match — it's a cosmetic catalog version with no CI gate, so it drifts silently if you forget (it sat at `0.2.0` while the package was `0.3.10`). The cw **plugin** manifest (`cw/.claude-plugin/plugin.json`) deliberately omits `version` and tracks the git SHA, so it needs no bump.

**Meridian session roots:** Meridian spawns resolve `MERIDIAN_TASK_DIR` for the
checkout where source work happens, but `MERIDIAN_PROJECT_DIR` stays anchored to
the session control root for state, profiles, and context. Nested
`meridian ...` commands use project-root resolution, so CWD alone may not target
this package. For package releases, pass the package root explicitly:

```bash
meridian -C "$PWD" mars version patch --push
```

Use explicit `-C <package-root>` whenever running Meridian commands for this
package from an inherited Meridian environment. For task checkouts, prefer
`meridian -C "$MERIDIAN_TASK_DIR" ...`.

## Syncing the `cw/` distribution

`cw/skills/` adapts `skills/` for harnesses without Meridian (Claude.ai uploads, the Claude Code plugin). Skills split two ways:

- **GENERATED** — selected skills copied from a temporary Mars consumer project's `.claude/skills/`. Mars performs Claude frontmatter/native lowering; the script filters the skills that belong in the cw distribution.
- **MANUAL** — skills carrying cw-specific adaptations, cw-only behavior, or dependency changes not yet available through a released Mars dependency. Hand-maintained; the tool lints but never overwrites them.

```bash
python3 scripts/sync_cw_skills.py            # check for drift (CI gate); exit 1 on problems
python3 scripts/sync_cw_skills.py --apply    # build temp Mars consumer and refresh GENERATED skills
python3 scripts/sync_cw_skills.py --list     # print the GENERATED/MANUAL classification
```

After editing a generated `skills/<name>/SKILL.md`, run `--apply` so Mars lowers it into the cw distribution. Adapt MANUAL skills by hand, then run the check. The sync script builds a temporary Mars consumer and may need network access to resolve git dependency tags. CI fails on generated drift, leaked Meridian vocab in `cw/`, or dangling skill/agent references. cw frontmatter is Claude vocab (`name` + `description`, plus Claude-native flags such as `disable-model-invocation` when Mars lowers `model-invocable: false`) — never Mars `type`/`model-invocable`/`effort`.

**`creative-writing-muse`:** source lives in `skills/creative-writing-muse` and is generated into `cw/skills/creative-writing-muse`. It is a user-activated, single-agent muse mode for skills-only environments; the `muse` agents do not load it. The agents follow the Product Lead pattern directly: capture author intent, craft specialist prompts, route work, synthesize results, and speak back to the author.

**Plugin manifest:** `cw/.claude-plugin/plugin.json` is required. Claude Code auto-discovers components without it, but the marketplace **add-from-GitHub** path (Cowork / claude.ai) validates the plugin and *rejects it* if the manifest is missing. `claude plugins validate .claude-plugin/marketplace.json` only checks the marketplace schema, not the plugin — so CI also runs `claude plugins validate cw`, which validates the manifest plus every agent/skill component file. `version` is intentionally omitted from the manifest so the plugin tracks the git commit SHA (always-latest, no extra bump surface).

## Slash Commands

| Command | Skill |
|---|---|
| `/bs` | story-planning |
| `/write [style]` | creative-writing-modes |
| `/wiki` | kb-management |
| `/critique` | story-review |

## Design Patterns

**Source tagging (brainstorming):** Untagged = user stated. `<AI>...</AI>` = AI suggestion. `<hidden>...</hidden>` = author-only (twists, secrets).

**Citations (kb-management):** Chapter references (`Chapter 3: Scene where X discovers Y`) and document references (`magic-system.md`).

**Style guides:** Directive AI instructions, not human documentation. Imperative form + examples.

## Development

**Build Claude.ai zips:** `python3 scripts/create_skill_zips.py` → `zips/*.skill`

**Validate package:** `meridian mars check`

**Validate plugin manifest:** `claude plugins validate .claude-plugin/marketplace.json` (marketplace schema) and `claude plugins validate cw` (cw plugin manifest + components)

**Release flow:** Bump version in `mars.toml` → commit → tag `vX.Y.Z` → push tag → CI creates GitHub Release with `.skill` artifacts.

**Pre-commit hook:** `.githooks/pre-commit` front-loads the distribution-breaking checks (cw skill sync + `claude plugins validate cw`) so they fire at commit time instead of only in CI. It's committed but not auto-installed — enable it once per clone:

```bash
git config core.hooksPath .githooks
```

It blocks the commit on failure; bypass a single commit with `git commit --no-verify`. (Skips plugin validation if the `claude` CLI isn't on PATH.)

**CI:** PRs run `mars check` + marketplace/plugin validation (`claude plugins validate`) + frontmatter validation + `sync_cw_skills.py` drift check + zip build. Tag pushes create releases.

## Conventions

- Each skill's `SKILL.md` uses YAML frontmatter with `name` and `description`
- Skills are self-contained: no cross-skill dependencies
- Agent profiles declare their skills in the `skills:` frontmatter array
- Generated directories (`.agents/`, `.mars/`, `.meridian/`) are gitignored

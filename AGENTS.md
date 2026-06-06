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

- **MIRROR** — pure-craft skills with no harness-specific content. Auto-synced verbatim from `skills/<name>/` (body + `resources/`), frontmatter rewritten to Claude vocab.
- **MANUAL** — skills carrying Meridian→generic adaptations (spawn mechanics, env paths), skills adapted from the `meridian-base` dependency, and cw-only skills. Hand-maintained; the tool lints but never overwrites them.

```bash
python3 scripts/sync_cw_skills.py            # check for drift (CI gate); exit 1 on problems
python3 scripts/sync_cw_skills.py --apply    # sync MIRROR skills from skills/
python3 scripts/sync_cw_skills.py --list     # print the MIRROR/MANUAL classification
```

After editing a `skills/<name>/SKILL.md`, run `--apply` (MIRROR skills sync automatically; MANUAL skills you adapt by hand, then `--check`). CI runs the check on every PR and fails on mirror drift, leaked Meridian vocab in `cw/`, or dangling skill/agent references. cw frontmatter is Claude vocab only (`name` + `description`) — never Mars `type`/`model-invocable`/`effort`.

**`cw-muse`:** Claude.ai has no agents, so `cw/skills/cw-muse` is the entry-point skill standing in for the muse agent — activate it to drive a single-agent brainstorm/draft/critique/revise session. The plugin (Claude Code/Cowork) uses the muse **agent** instead, with cw agents flattened (no `bard`/`lore-keeper`).

**Plugin manifest:** `cw/.claude-plugin/plugin.json` is required. Claude Code auto-discovers components without it, but the marketplace **add-from-GitHub** path (Cowork / claude.ai) validates the plugin and *rejects it* if the manifest is missing. `claude plugins validate .claude-plugin/marketplace.json` only checks the marketplace schema, not the plugin — so CI also runs `claude plugins validate cw`, which validates the manifest plus every agent/skill component file. `version` is intentionally omitted from the manifest so the plugin tracks the git commit SHA (always-latest, no extra bump surface).

## Slash Commands

| Command | Skill |
|---|---|
| `/bs` | brainstorming |
| `/write [style]` | prose-writing |
| `/wiki` | kb-management |
| `/critique` | prose-critique |

## Design Patterns

**Source tagging (brainstorming):** Untagged = user stated. `<AI>...</AI>` = AI suggestion. `<hidden>...</hidden>` = author-only (twists, secrets).

**Citations (kb-management):** Chapter references (`Chapter 3: Scene where X discovers Y`) and document references (`magic-system.md`).

**Style guides:** Directive AI instructions, not human documentation. Imperative form + examples.

## Development

**Build Claude.ai zips:** `python3 scripts/create_skill_zips.py` → `zips/*.skill`

**Validate package:** `meridian mars check`

**Validate plugin manifest:** `claude plugins validate .claude-plugin/marketplace.json` (marketplace schema) and `claude plugins validate cw` (cw plugin manifest + components)

**Release flow:** Bump version in `mars.toml` → commit → tag `vX.Y.Z` → push tag → CI creates GitHub Release with `.skill` artifacts.

**CI:** PRs run `mars check` + marketplace/plugin validation (`claude plugins validate`) + frontmatter validation + `sync_cw_skills.py` drift check + zip build. Tag pushes create releases.

## Conventions

- Each skill's `SKILL.md` uses YAML frontmatter with `name` and `description`
- Skills are self-contained: no cross-skill dependencies
- Agent profiles declare their skills in the `skills:` frontmatter array
- Generated directories (`.agents/`, `.mars/`, `.meridian/`) are gitignored

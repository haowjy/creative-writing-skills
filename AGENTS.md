# AGENTS.md

This file provides guidance to AI Agents when working with this repository.

## Repository Overview

A Mars source package providing 17 composable creative writing agents and 12 skills for Claude Code. Also distributes Claude.ai skill uploads via GitHub Releases.

## Key Distinctions

**`skills/` vs `cw/skills/`:** `skills/` is the Mars source — consumed by Claude Code projects via `mars add`. `cw/skills/` holds adapted copies for Claude.ai uploads (meridian-specific references replaced with generic equivalents). When updating a skill, edit `skills/` first, then sync changes to `cw/skills/`.

**Agents vs skills:** Agents are spawned as independent processes (orchestrators, writers, critics). Skills are reference material loaded into agent context (craft knowledge, patterns, conventions). See `agents/` and `skills/` directories.

## Package Management

This repo is both a Mars source package (publishes agents/skills) and a Mars consumer (depends on `meridian-base`).

```bash
meridian mars check     # Validate package structure and frontmatter
meridian mars sync      # Install dependencies into .agents/
meridian mars version patch  # Bump version, commit, tag
```

Version lives in `mars.toml` under `[package]`. Tags trigger CI releases.

## Slash Commands

| Command | Skill |
|---|---|
| `/bs` | brainstorming |
| `/write [style]` | prose-writing |
| `/wiki` | wiki-docs |
| `/critique` | prose-critique |

## Design Patterns

**Source tagging (brainstorming):** Untagged = user stated. `<AI>...</AI>` = AI suggestion. `<hidden>...</hidden>` = author-only (twists, secrets).

**Citations (wiki-docs):** Chapter references (`Chapter 3: Scene where X discovers Y`) and document references (`magic-system.md`).

**Style guides:** Directive AI instructions, not human documentation. Imperative form + examples.

## Development

**Build Claude.ai zips:** `python3 scripts/create_skill_zips.py` → `zips/*.skill`

**Validate package:** `meridian mars check`

**Validate plugin manifest:** `claude plugins validate .claude-plugin/marketplace.json`

**Release flow:** Bump version in `mars.toml` → commit → tag `vX.Y.Z` → push tag → CI creates GitHub Release with `.skill` artifacts.

**CI:** PRs run `mars check` + frontmatter validation + zip build. Tag pushes create releases.

## Conventions

- Each skill's `SKILL.md` uses YAML frontmatter with `name` and `description`
- Skills are self-contained — no cross-skill dependencies
- Agent profiles declare their skills in the `skills:` frontmatter array
- Generated directories (`.agents/`, `.mars/`, `.meridian/`) are gitignored

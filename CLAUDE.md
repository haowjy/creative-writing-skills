# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Repository Overview

A Mars source package providing 17 composable creative writing agents and 12 skills for Claude Code. Also distributes Claude.ai skill uploads via GitHub Releases.

## Repository Structure

```
creative-writing-skills/
├── agents/              # 17 agent profiles (Mars source)
├── skills/              # 12 skill directories (Mars source, Claude Code)
│   └── <name>/
│       ├── SKILL.md
│       └── resources/   # optional
├── cw/                  # Claude.ai distribution (adapted copies, no meridian refs)
│   ├── agents/          # Claude.ai agent copies (not currently distributed)
│   ├── skills/          # Claude.ai skill copies
│   └── cw-router/       # Router skill for Claude.ai web UI
├── .claude/
│   ├── commands/        # Slash commands (/bs, /write, /wiki, /critique)
│   └── settings.json
├── .claude-plugin/
│   └── marketplace.json # Legacy plugin manifest
├── scripts/
│   └── create_skill_zips.py  # Builds .skill zips from cw/
├── .github/workflows/
│   ├── ci.yml           # PR validation (mars check, frontmatter, zip build)
│   └── release.yml      # Tag-triggered release with .skill artifacts
├── mars.toml            # Package definition + dependencies
└── mars.lock
```

## Key Distinctions

**`skills/` vs `cw/skills/`:** `skills/` is the Mars source — consumed by Claude Code projects via `mars add`. `cw/skills/` holds adapted copies for Claude.ai uploads (meridian-specific references replaced with generic equivalents). When updating a skill, edit `skills/` first, then sync changes to `cw/skills/`.

**Agents vs skills:** Agents are spawned as independent processes (orchestrators, writers, critics). Skills are reference material loaded into agent context (craft knowledge, patterns, conventions). See `agents/` and `skills/` directories.

## Package Management

This repo is both a Mars source package (publishes agents/skills) and a Mars consumer (depends on `meridian-base` and `meridian-dev-workflow`).

```bash
meridian mars check     # Validate package structure and frontmatter
meridian mars sync      # Install dependencies into .agents/
meridian mars version patch  # Bump version, commit, tag
```

Version lives in `mars.toml` under `[package]`. Tags trigger CI releases.

## Agents (17)

| Agent | Role |
|---|---|
| **story-orchestrator** | Primary entry point — coordinates all workflows |
| **draft-orchestrator** | Draft/critique loop with writers, critics, reader-sims |
| **knowledge-orchestrator** | Wiki updates, graph maintenance, continuity |
| **writer** | Prose in the project's established style |
| **critic** | Structured critique across four reward channels |
| **reader-sim** | Simulated reader experience |
| **character-sim** | Character behavior simulation for dialogue testing |
| **brainstormer** | Wide-open option generation |
| **outliner** | Beat sheets and arc maps |
| **explorer** | Fast project exploration |
| **researcher** | Web research for worldbuilding |
| **continuity-checker** | Drafts vs established canon |
| **wiki-editor** | Wiki documentation |
| **graph-maintainer** | Project knowledge graph |
| **chronicler** | Session decision recording |
| **session-miner** | Mine transcripts for unreported decisions |
| **style-creator** | Analyze prose to create style guides |

## Skills (12)

| Skill | Purpose |
|---|---|
| **brainstorming** | Exploratory idea generation with [TBD] markers |
| **prose-writing** | Voice matching, scene construction |
| **prose-critique** | Multi-dimensional feedback |
| **prose-analysis** | Quantitative prose pattern analysis |
| **wiki-docs** | Encyclopedic documentation with citations |
| **story-architecture** | Arc shape, tension curves |
| **story-context** | Loading relevant story context before tasks |
| **story-decisions** | Decision logging and retrieval |
| **knowledge-graph** | Project knowledge graph maintenance |
| **writing-principles** | Four reward channels, AI failure modes |
| **writing-artifacts** | Artifact types and file conventions |
| **writing-staffing** | Agent roster and coordination patterns |

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

**Release flow:** Bump version in `mars.toml` → commit → tag `vX.Y.Z` → push tag → CI creates GitHub Release with `.skill` artifacts.

**CI:** PRs run `mars check` + frontmatter validation + zip build. Tag pushes create releases.

## Conventions

- Each skill's `SKILL.md` uses YAML frontmatter with `name` and `description`
- Skills are self-contained — no cross-skill dependencies
- Agent profiles declare their skills in the `skills:` frontmatter array
- Generated directories (`.agents/`, `.mars/`, `.meridian/`) are gitignored

# Creative Writing Skills

A multi-agent creative writing assistant for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Provides 17 specialized agents and 12 composable skills for prose writing, brainstorming, critique, story architecture, knowledge management, and style analysis. Also available as standalone Claude.ai skill uploads.

The `story-orchestrator` agent is the main entry point — it understands your intent, fans out brainstormers and researchers to explore options, kicks off draft/critique loops when you're ready to write, and coordinates knowledge maintenance so your wiki, decision logs, and continuity stay current as your story evolves.

## What's Included

### Agents (17)

| Agent | Role |
|---|---|
| **story-orchestrator** | Primary entry point — coordinates all creative writing workflows |
| **draft-orchestrator** | Runs the draft/critique loop with writers, critics, reader-sims |
| **knowledge-orchestrator** | Coordinates wiki updates, graph maintenance, continuity checks |
| **writer** | Writes prose in the project's established style |
| **critic** | Structured critique across four reader reward channels |
| **reader-sim** | Simulates a reader's experience, reports per-channel engagement |
| **character-sim** | Simulates character behavior for dialogue testing and scene exploration |
| **brainstormer** | Wide-open option generation on a scoped question |
| **outliner** | Structural decomposition into beat sheets and arc maps |
| **explorer** | Fast project exploration — finds files, searches content |
| **researcher** | Web research for worldbuilding and fact-checking |
| **continuity-checker** | Checks drafts against established canon |
| **wiki-editor** | Creates and maintains wiki documentation |
| **graph-maintainer** | Updates the project knowledge graph |
| **chronicler** | Records session decisions into persistent notes |
| **session-miner** | Mines past session transcripts for unreported decisions |
| **style-creator** | Analyzes existing prose to create style guides |

### Skills (12)

| Skill | Purpose |
|---|---|
| **brainstorming** | Exploratory idea generation with [TBD] markers |
| **prose-writing** | Voice matching, scene construction, prose craft |
| **prose-critique** | Multi-dimensional feedback (character, voice, structure, prose, continuity) |
| **prose-analysis** | Quantitative prose pattern analysis |
| **wiki-docs** | Encyclopedic documentation with citations |
| **story-architecture** | Arc shape, tension curves, structural analysis |
| **story-context** | Loading relevant story context before tasks |
| **story-decisions** | Decision logging and retrieval |
| **knowledge-graph** | Project knowledge graph maintenance |
| **writing-principles** | Four reward channels, AI failure modes, craft tradition |
| **writing-artifacts** | Artifact types and file conventions |
| **writing-staffing** | Agent roster and coordination patterns |

## Installation

### Mars (recommended)

[Mars](https://github.com/haowjy/meridian-channel) is a package manager for Claude Code agents and skills.

```bash
meridian mars add haowjy/creative-writing-skills
meridian mars sync
```

If you have the standalone `mars` CLI installed, `mars add` / `mars sync` also works.

### Claude Code plugin (legacy)

```bash
claude plugin marketplace add haowjy/creative-writing-skills
claude plugin install creative-writing-skills@creative-writing-skills
```

### Claude.ai

Download `.skill` files from [GitHub Releases](https://github.com/haowjy/creative-writing-skills/releases) and upload them in Claude.ai under **Settings > Capabilities > Skills**.

Recommended starting set: `cw-router.skill`, `prose-writing.skill`, `brainstorming.skill`, `prose-critique.skill`.

For Claude.ai, use `cw-router` to route to the right skill for your task. The full agent system is Claude Code only.

## Usage

Use `story-orchestrator` as the default entry point. It coordinates brainstorming, drafting, critique, and knowledge maintenance across all the specialized agents.

### Slash Commands (Claude Code)

These slash commands are provided via `.claude/commands/` and work in Claude Code only.

| Command | What it does |
|---|---|
| `/bs` | Brainstorm and explore story ideas |
| `/write [style]` | Enter prose-writing mode (optionally with a style) |
| `/wiki` | Create canonical wiki/documentation pages |
| `/critique` | Critique prose with structured feedback |

### Examples

- "Help me brainstorm ideas for my magic system"
- "Write the next scene where my protagonist discovers the truth"
- "Critique this chapter for pacing and character consistency"
- "Create a wiki page for this location"
- "Analyze my writing style and create a style guide from these chapters"

## Project Setup

A recommended layout for a Mars-based writing project:

```text
my-story/
├── mars.toml              # Package config + dependencies
├── .claude/
│   └── CLAUDE.md          # Project instructions
├── .agents/               # Managed by mars sync (agents + skills)
├── story/                 # Chapters, drafts
├── wiki/                  # Character profiles, lore, locations
├── style/
│   └── style-guide.md     # Your writing style reference
└── notes/                 # Planning, brainstorms, decision logs
```

Typical flow:
1. Brainstorm and explore options with `story-orchestrator`.
2. Capture decisions and canon pages as they stabilize.
3. Draft with style context, then run critique and continuity checks.
4. Keep wiki and decision logs in sync with each accepted change.

## Development

### Build Claude.ai skill zips

```bash
python3 scripts/create_skill_zips.py
```

Outputs to `zips/*.skill`.

### Validate package

```bash
meridian mars check
```

### Release

```bash
./scripts/release.sh              # patch bump, commit, tag
./scripts/release.sh minor        # minor bump
./scripts/release.sh major        # major bump
./scripts/release.sh --push       # patch bump + push (triggers CI release)
```

### CI/CD

- Push / PR to `main`: runs `mars check`, frontmatter validation, lock freshness check, zip build.
- Tag push (`v*`): validates, then creates a GitHub Release with `.skill` artifacts.

## License

Apache License 2.0. See [LICENSE](LICENSE).

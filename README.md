# Creative Writing Skills

Composable agents and skills for creative writing with Claude Code. Also available as Claude.ai skill uploads.

## What's Included

### Agents (17)

| Agent | Role |
|---|---|
| **story-orchestrator** | Primary entry point - coordinates all creative writing workflows |
| **draft-orchestrator** | Runs the draft/critique loop with writers, critics, reader-sims |
| **knowledge-orchestrator** | Coordinates wiki updates, graph maintenance, continuity checks |
| **writer** | Writes prose in the project's established style |
| **critic** | Structured critique across four reader reward channels |
| **reader-sim** | Simulates a reader's experience, reports per-channel engagement |
| **character-sim** | Simulates character behavior for dialogue testing and scene exploration |
| **brainstormer** | Wide-open option generation on a scoped question |
| **outliner** | Structural decomposition into beat sheets and arc maps |
| **explorer** | Fast project exploration - finds files, searches content |
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

Claude Code setup/prerequisites are documented in the official [Claude Code docs](https://docs.claude.com/en/docs/claude-code/quickstart).

### Mars (recommended)

```bash
mars add haowjy/creative-writing-skills
mars sync
```

`mars.toml` in this repo currently declares version `0.0.5`.

### Claude Code plugin (legacy alternative)

```bash
claude plugin marketplace add haowjy/creative-writing-skills
claude plugin install creative-writing-skills@creative-writing-skills
claude plugin
```

### Claude.ai

1. Download `.skill` files from [GitHub Releases](https://github.com/haowjy/creative-writing-skills/releases).
2. In Claude.ai, go to `Settings > Capabilities > Skills`.
3. Upload the skills you want to use (start with `cw-router.skill`, `prose-writing.skill`, and `prose-critique.skill`).

## Usage

Use `story-orchestrator` as the default entry point in Claude Code. It routes work to specialized agents and skills.

### Slash Commands

| Command | What it does |
|---|---|
| `/bs` | Brainstorm and explore story ideas |
| `/write [style]` | Enter prose-writing mode (optionally with a style) |
| `/wiki` | Create canonical wiki/documentation pages |
| `/critique` | Critique prose with structured feedback |

### Example prompts

- "Help me outline a 12-chapter arc for this premise."
- "Write the next scene in my existing style guide."
- "Critique this chapter for pacing and continuity."
- "Create a canon wiki page for the magic system."

For Claude.ai, use `cw-router` to route to the right skill when needed.

## Project Setup

A simple project layout for long-form writing:

```text
my-story/
├── .claude/
│   └── CLAUDE.md
├── drafts/
├── wiki/
├── style/
│   └── style-guide.md
└── notes/
```

Recommended flow:
1. Start with brainstorming and architecture.
2. Capture decisions and canon pages as soon as they stabilize.
3. Draft with style context, then run critique and continuity checks.
4. Keep wiki and decision logs in sync with each accepted change.

## Development

### Build Claude.ai skill zips

```bash
python3 scripts/create_skill_zips.py
```

Artifacts are written to `zips/*.skill`.

### Validate package wiring

```bash
meridian mars check
```

### CI/CD

- Pull requests run `mars check` and frontmatter validation.
- Tag pushes create GitHub releases, including generated `.skill` artifacts.

## License

Apache License 2.0. See [LICENSE](LICENSE).

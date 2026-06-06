# Creative Writing Skills

[![CI](https://github.com/haowjy/creative-writing-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/haowjy/creative-writing-skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Write novels, short stories, and serial fiction with AI that maintains your voice, tracks your continuity, and gets better the more you use it. From first brainstorm to polished draft: specialized agents handle each mode of work (writing, critiquing, revising, exploring) while shared skills carry the craft methodology.

**What you get:**
- **Brainstorm without committing**: explore plot options, character arcs, and world mechanics with multiple AI perspectives before deciding anything
- **Write in your voice**: create style files from your existing prose, then draft new scenes that match
- **Catch your own mistakes**: structured critique, continuity checks, and simulated reader reactions
- **Keep everything in sync**: knowledge base updates as your story evolves

## Quick Start

```bash
meridian mars add haowjy/creative-writing-skills
meridian mars sync
meridian bootstrap
```

## Installation

### Mars (Meridian)

```bash
meridian mars add haowjy/creative-writing-skills
meridian mars sync
```

Then run `meridian` to start a session with muse. First-time setup runs the bootstrap automatically.

### Claude Code / Cowork

Claude Code and Cowork use the same plugin format.

**Claude Code**: add the marketplace and install:

```bash
/plugin marketplace add haowjy/creative-writing-skills
/plugin install creative-writing-skills@cw
```

**Cowork**: open the Claude desktop app → **Customize** → **Plugins** → **+** (Personal plugins) → **Add marketplace**, enter `haowjy/creative-writing-skills`, then install the **creative-writing-skills** plugin. Cowork runs the full plugin, agents included.

Once installed, start a session with muse as your agent:

```bash
claude --agent creative-writing-skills:muse
```

Run the one-time project setup to create your `CLAUDE.md` and `kb/` structure:

```
/creative-writing-skills:project-setup
```

### Claude.ai

Use it the way you'd use the muse agent, but inside a single chat: activate the **`cw-muse`** skill, tell it what you're writing, and it takes the lead — brainstorming, drafting, critiquing, and revising across the same conversation, switching stance as the work needs and leaning on the craft skills for discipline. claude.ai chat runs **skills only**, so `cw-muse` stands in for the muse agent: there are no subagents to spawn, and the other agents appear grayed out (they run only in Cowork).

First, get the skills into claude.ai — pick one:

- **Add the marketplace (recommended):** **Customize** → **Plugins** → **+** → **Add marketplace** → `haowjy/creative-writing-skills`, then install the plugin. Skills load; agents stay grayed out in chat.
- **Upload the zips (fallback):** download the `.skill` files from the [latest release](https://github.com/haowjy/creative-writing-skills/releases/latest), then **Customize** → **Skills** → **"+"** → **Upload skill** for each one.

Then open a chat, activate **`cw-muse`**, and start talking about your story. Recommended starting set: **cw-muse**, **writing-principles**, **prose-writing**, **scene-construction**, **prose-critique**.

> Prefer to build the zips yourself? Clone the repo and run `python scripts/create_skill_zips.py` to regenerate the `.skill` files in `zips/`.

## How It Works

```mermaid
flowchart TB
    You([You]) --> M[muse]

    M --> Explore
    M --> Draft
    M --> Maintain

    subgraph Explore ["Explore & Plan"]
        direction LR
        B[brainstormer] ~~~ CS[character-sim]
        CS ~~~ O[outliner]
    end

    subgraph Draft ["Draft & Revise"]
        direction TB
        W[writer] --> CR[critic]
        CR -->|synthesis| RW[revision-writer]
        RW -.->|iterate| CR
        M -.->|pivotal scenes| RS[reader-sim]
        M -.->|voice check| CC[continuity-checker]
    end

    subgraph Maintain ["Knowledge"]
        direction LR
        CH[chronicler]
        SC[style-creator]
    end

    Explore -->|direction confirmed| Draft
    Draft -->|decisions & facts| Maintain
    Maintain -.->|context for next session| Explore
```

**Explore:** Fan out brainstormers for creative variety. Spawn character-sims to discover voices. Use outliners to shape structure once a direction is chosen.

**Draft & Revise:** Muse runs the write/critique/revise loop: writer produces prose, critics evaluate across the four reward channels (transportation, aesthetic, social simulation, flow), revision-writer fixes specific issues. Reader-sim gives experiential signal on pivotal scenes.

**Knowledge:** Chronicler extracts facts from completed chapters into the kb. Style-creator captures voice patterns from prose samples. The kb grows as the project evolves, giving every future agent accurate context.

## Agents

| Agent | Role |
|---|---|
| **muse** | Author's creative partner: intent capture, brainstorming, drafting loops, knowledge maintenance |
| **writer** | Generative prose from scene briefs in the project's voice |
| **revision-writer** | Surgical revision from critique: preserves voice, fixes specific issues |
| **bridge-writer** | Transitions, time compression, connective passages between pivotal scenes |
| **critic** | Adversarial critique across the four reader reward channels |
| **reader-sim** | Simulates a reader's experience, reports moment-by-moment |
| **character-sim** | In-character voice performance for discovery and relationship testing |
| **continuity-checker** | Checks drafts against established canon |
| **brainstormer** | Wide-open option generation on a scoped question |
| **outliner** | Structural decomposition into beat sheets and arc maps |
| **style-creator** | Analyzes existing prose to create style reference files |
| **chronicler** | Extracts story facts from chapters into the kb |

## Skills

| Skill | Purpose |
|---|---|
| **writing-principles** | Four reward channels, AI failure modes, reader psychology |
| **prose-writing** | Immersion patterns: psychic distance, rhythm, sensory grounding, interiority |
| **scene-construction** | Beat-level craft: scene entry, dialogue, pacing, transitions |
| **prose-critique** | Adversarial reading methodology with focus areas |
| **style-analysis** | How to analyze prose and produce style reference files |
| **story-architecture** | Arc shape, tension curves, structural analysis |
| **story-context** | Context scoping: what to pass to each agent type |
| **shared-dao** | Shared vocabulary: canonical story terms, aliases, and ambiguity resolution |
| **brainstorming** | Exploratory capture with source tagging |
| **kb-management** | Maintaining the story knowledge base: page conventions, organization, when to create vs update |
| **writing-artifacts** | File conventions: kb/ for durable knowledge, work/ for scratch |
| **writing-issues** | Issue tracking across revision cycles |
| **writing-staffing** | Team composition: which agents, how many, what focus areas |
| **project-setup** | One-time guided setup: interviews about the project, creates CLAUDE.md and kb structure |
| **llm-writing** | General LLM writing discipline: behavioral pulls and document-writing guardrails |

## Project Layout

```text
my-story/
├── CLAUDE.md              # Project conventions (created by project-setup)
├── story/                 # Chapters and manuscript
├── work/                  # Current drafting effort
│   ├── outline/
│   ├── drafts/
│   ├── critique-reports/
│   └── brainstorm/
└── kb/                    # Durable knowledge base
    ├── styles/            # Voice reference files
    ├── characters/        # Character state and profiles
    ├── world/             # Locations, lore, systems
    ├── timeline/          # Chronology
    ├── canon/             # Established facts
    └── issues/            # Tracked writing problems
```

## Compatibility

| Feature | Claude Code | Cowork | Mars (Meridian) | Claude.ai |
|---|:---:|:---:|:---:|:---:|
| All agents | Yes (flat) | Yes (flat) | Yes (hierarchical) | No (grayed out in chat) |
| All skills | Yes | Yes | Yes | Marketplace add or zip |
| Multi-agent orchestration | Via muse | Via muse | Via muse → bard → workers | No |
| Project setup | Yes | Yes | Yes | No |

Claude Code and Cowork use the same plugin format with all agents as flat subagents under muse. The Meridian version adds intermediate orchestrators (bard for drafting, lore-keeper for knowledge maintenance) for deeper context isolation. You can add the marketplace to the Claude desktop app from GitHub; Cowork runs the agents, but plain claude.ai chat runs skills only (agents grayed out) — there the `cw-muse` skill provides the session-lead orchestration in a single conversation, backed by the craft skills.

## Current Experiments

**Rhetorical questions in skill prompts.** The economy section in `writing-principles` uses rhetorical questions ("what can you leave out and still have the scene work?") rather than declarative statements. LLMs can distinguish rhetorical from information-seeking questions internally ([arxiv 2604.14128](https://arxiv.org/abs/2604.14128)), and Self-Ask prompting shows questions improve reasoning, but no research directly tests whether rhetorical questions in system prompts improve task performance vs. equivalent declaratives. Keeping the rhetorical form to see if it activates a self-check loop that declaratives don't.

## Development

### Validate package

```bash
meridian mars check
```

### Release

```bash
mars version patch              # bump, commit, tag
mars version patch --push       # bump, commit, tag, push
```

## License

Apache License 2.0. See [LICENSE](LICENSE).

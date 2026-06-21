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

**Cowork**: in the sidebar, **Customize** → **Personal plugins** → **+** → **Create plugins** → **Add marketplace** → **Add from repository**, enter `haowjy/creative-writing-skills`, then install the **creative-writing-skills** plugin. (Same flow as [Claude.ai](#claudeai) below — Cowork just also runs the agents.)

Once installed, start a session with muse as your agent:

```bash
claude --agent creative-writing-skills:muse
```

Run the one-time project setup to create your `CLAUDE.md` and `kb/` structure:

```
/creative-writing-skills:project-setup
```

### Claude.ai

`cw-muse` turns an ordinary Claude chat into a creative-writing partner. Turn it on, tell it what you're working on, and it carries you from first idea to finished draft in one conversation — talking through ideas, drafting scenes in your voice, flagging what isn't working, and revising. The other skills (prose, scene craft, critique, structure) are the craft knowledge it draws on; you don't have to invoke them yourself.

First, add the skills to claude.ai — pick one:

- **Add the marketplace (easiest):** in the sidebar, **Customize** → **Personal plugins** → **+** → **Create plugins** → **Add marketplace** → **Add from repository**, enter `haowjy/creative-writing-skills`, and click **Sync**.

  ![Adding the marketplace in claude.ai: the plugins icon and + in the sidebar, with the repository entered in the Add marketplace dialog](docs/images/claudeai-add-marketplace.png)
- **Upload the files:** download the `.skill` files from the [latest release](https://github.com/haowjy/creative-writing-skills/releases/latest), then **Customize** → **Skills** → **"+"** → **Upload skill** for each one.

Then start a chat, turn on **`cw-muse`**, and describe what you want to write — it leads from there. Adding skills one at a time instead? Start with **cw-muse**, **writing-principles**, **prose-writing**, **scene-construction**, and **prose-critique**.

> Want to build the files yourself? Clone the repo and run `python scripts/create_skill_zips.py` to regenerate them in `zips/`.

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
| **muse** | Author-facing creative partner for all story work, from brainstorming through production handoff |
| **bard** | Drives confirmed creative direction to finished drafts through write, critique, and revision cycles |
| **writer** | Fresh prose drafts from scene briefs and style references |
| **revision-writer** | Surgical revision from critique findings, preserving voice and what works |
| **bridge-writer** | Transitions, time compression, and connective passages between scenes |
| **critic** | Deep adversarial critique of a draft, one focus area at a time |
| **reader-sim** | Experiential reader response to a draft, moment by moment |
| **character-sim** | In-character conversation for voice discovery and relationship testing |
| **continuity-checker** | Cross-references content against established canon for contradictions |
| **brainstormer** | Creative option generation for a scoped question or angle |
| **outliner** | Sequences confirmed direction into arc, chapter, and beat-level outlines |
| **style-creator** | Analyzes prose samples to produce style reference files for the project's voice |
| **chronicler** | Extracts factual state changes from written chapters into the kb |
| **lore-keeper** | Story knowledge maintenance after brainstorms, drafts, and decisions |

## Skills

| Skill | Purpose |
|---|---|
| **creative-direction** | Shape what the story wants to be before producing pages |
| **production-drafting** | Turning confirmed creative direction into finished drafts |
| **writing-principles** | Four reward channels, AI failure modes, reader psychology |
| **prose-writing** | Prose-level immersion patterns: psychic distance, rhythm, sensory grounding |
| **scene-construction** | Beat-level craft: scene entry, dialogue, pacing, transitions |
| **prose-critique** | Adversarial reading methodology with focus areas |
| **character-voice** | Speaking as a character for voice discovery and dialogue exploration |
| **reader-experience** | Experiential reading through the four reward channels |
| **fact-extraction** | Extracting factual state changes from chapters into the kb |
| **style-analysis** | How to analyze prose and produce style reference files |
| **story-architecture** | Arc shape, tension curves, structural analysis |
| **story-context** | Context scoping for writing handoffs |
| **shared-dao** | Shared vocabulary: canonical story terms, aliases, and ambiguity resolution |
| **brainstorming** | Exploratory capture with source tagging |
| **writing-artifacts** | File conventions: kb/ for durable knowledge, work/ for scratch |
| **writing-issues** | Tracking writing issues that persist beyond a single critique |
| **writing-staffing** | Team composition for writing workflows |
| **project-setup** | One-time guided setup: creates CLAUDE.md and kb structure |
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

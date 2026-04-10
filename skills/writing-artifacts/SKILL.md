---
name: writing-artifacts
description: Shared artifact convention between orchestrators — what goes where in `$MERIDIAN_FS_DIR/` and `$MERIDIAN_WORK_DIR/`, how artifacts flow between phases, and what each directory means. Use whenever work artifacts, style files, knowledge entries, drafts, or critique reports are being created, referenced, or discussed.
---

# Writing Artifacts

Artifacts live in two places: durable project knowledge in `$MERIDIAN_FS_DIR/` and temporary work scratch in `$MERIDIAN_WORK_DIR/`. This convention defines what each directory means, who writes it, and how artifacts flow between orchestrators. Every orchestrator shares this understanding — it's how story direction survives the handoff from brainstorming to drafting to revision.

## `$MERIDIAN_FS_DIR/` — Durable Project Knowledge

The agent-maintained knowledge layer. Both humans and agents read it. Quality bar: readable prose with clear structure, not agent shorthand. Decisions baked inline with reasoning — a character entry includes *why* that age was chosen, a timeline entry includes *why* events are ordered that way.

```
$MERIDIAN_FS_DIR/
├── styles/              # voice, scene-type, tone guides (style-creator output)
│   ├── voice-*.md       #   character voices / POV styles
│   ├── scene-*.md       #   scene-type techniques (battle, discovery, etc.)
│   ├── tone-*.md        #   tonal registers (grief, humor, tension)
│   └── formatting.md    #   mechanical conventions (em dashes, ellipsis, etc.)
├── characters/          # character state + decision annotations
├── world/               # locations, lore, systems, factions
├── timeline/            # chronology, event ordering
├── canon/               # established facts from written chapters
└── graphs/              # relationship maps, knowledge graph output
```

### What Goes Where

**`styles/`** — How to write, not what to write. Voice files capture a character's speech patterns, narration style, and tonal range. Scene-type files capture technique for specific scene categories. Tone files capture emotional registers. The style-creator produces these from sample chapters or author requirements; the writer loads them when drafting.

**`characters/`** — Current character state: where they are in the story, what they know, their emotional trajectory, key relationships. Updated by the chronicler after chapters are written. Includes decision annotations — "Amber is 8 at story start [decided in session X, alternatives considered: 6, 10, rejected because...]".

**`world/`** — Locations, systems, lore, factions — anything about the world that multiple chapters reference. The chronicler and session-miner both contribute here.

**`timeline/`** — Event chronology. When things happened, in what order, with citations back to chapters. The continuity-checker's primary reference.

**`canon/`** — Facts established by written chapters. Not a copy of the chapter — a synthesis of what the chapter established as true. "Chapter 4 established that Amber can sense ghost-type energy" with a citation.

**`graphs/`** — Mermaid relationship diagrams, knowledge graph output, connection maps. The graph-maintainer keeps these current.

## `$MERIDIAN_WORK_DIR/` — Work Scratch

Temporary, scoped to the current work item. Archived when work completes. Durable knowledge gets promoted to `$MERIDIAN_FS_DIR/` before closing out.

```
$MERIDIAN_WORK_DIR/
├── outline/             # current outline being worked
├── drafts/              # draft iterations (v1, v2, etc.)
├── critique-reports/    # critic output for each round
└── brainstorm/          # brainstorm captures and synthesis
```

### What Goes Where

**`outline/`** — Scene briefs, beat breakdowns, chapter structure. The outliner writes here; the writer reads from here.

**`drafts/`** — Draft iterations. Each revision gets a new version (`route1-v1.md`, `route1-v2.md`). The draft-orchestrator tracks which version is current.

**`critique-reports/`** — Individual critic reports and orchestrator synthesis. Named by round and focus (`round1-structure.md`, `round1-synthesis.md`). The draft-orchestrator writes the synthesis; the writer reads it for revision.

**`brainstorm/`** — Brainstorm outputs from fan-out sessions. Named by angle or model (`meeting-combat.md`, `meeting-comedy.md`). The story-orchestrator synthesizes these before presenting options to the author.

## Who Writes What

| Artifact | Written by | Read by |
|---|---|---|
| `$MERIDIAN_FS_DIR/styles/` | style-creator | writer, critic (voice focus) |
| `$MERIDIAN_FS_DIR/characters/` | chronicler, session-miner | writer, critic, continuity-checker |
| `$MERIDIAN_FS_DIR/world/` | chronicler, session-miner | writer, researcher, wiki-editor |
| `$MERIDIAN_FS_DIR/timeline/` | chronicler | continuity-checker, outliner |
| `$MERIDIAN_FS_DIR/canon/` | chronicler | critic, continuity-checker, writer |
| `$MERIDIAN_FS_DIR/graphs/` | graph-maintainer | explorer, wiki-editor, orchestrators |
| `$MERIDIAN_WORK_DIR/outline/` | outliner | writer, draft-orchestrator |
| `$MERIDIAN_WORK_DIR/drafts/` | writer | critic, draft-orchestrator |
| `$MERIDIAN_WORK_DIR/critique-reports/` | critic, draft-orchestrator | writer, story-orchestrator |
| `$MERIDIAN_WORK_DIR/brainstorm/` | brainstormer | story-orchestrator |

## Promotion

When a work item completes, the orchestrator promotes durable knowledge from `$MERIDIAN_WORK_DIR/` to `$MERIDIAN_FS_DIR/`:

- Story decisions discovered during brainstorming → baked inline into relevant `$MERIDIAN_FS_DIR/` entries
- New character state from a drafted chapter → `$MERIDIAN_FS_DIR/characters/`
- New canon facts → `$MERIDIAN_FS_DIR/canon/`
- Timeline updates → `$MERIDIAN_FS_DIR/timeline/`

The knowledge-orchestrator handles promotion by dispatching chronicler, session-miner, and graph-maintainer. Don't promote raw brainstorm captures or draft iterations — those stay archived in the work item. Promote the *knowledge* extracted from them.

## Author's Space vs Agent Space

Agents maintain `$MERIDIAN_FS_DIR/`. The author maintains `story/`, `wiki/`, and `future/`. The wiki-editor is the one agent that writes to the author's space (`wiki/`), producing polished, reader-facing reference pages. All other agent output goes to `$MERIDIAN_FS_DIR/` or `$MERIDIAN_WORK_DIR/`.

Agents don't reorganize the author's manuscript structure or planning files. They read from the author's space and write to their own.

## This Convention Is Swappable

A project can replace this skill with its own artifact conventions — different directory names, different flow, different files — without touching orchestrator or agent bodies. The convention is a skill, not hardcoded structure.

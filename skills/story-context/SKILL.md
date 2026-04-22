---
name: story-context
description: Context scoping for writing agent spawns — use when deciding what context a spawned agent should receive, whether ephemeral story decisions should be materialized before handoff, and how much to pass. Poor context handoffs cause writers to invent contradictions and critics to miss relevant history.
---

# Story Context

Every spawn starts with a context decision. Get it wrong and the writer invents facts that contradict established canon, the critic misses a continuity issue because it never saw the relevant chapter, or the brainstormer explores territory the author already rejected.

The `/meridian-spawn` skill teaches the mechanics of `-f`, `--from`, and spawn commands. This skill teaches the judgment — what story context to pass, when to materialize decisions before spawning, and how much is enough.

## Choose the Right Mechanism

**`-f` — concrete artifacts.** Use when the context already exists as files: chapters, outlines, wiki pages, style files, character state files. The agent reads exactly what you point it at. This is the default choice because files are stable, inspectable, and survive compaction.

```bash
KB=$(meridian context kb)
WORK=$(meridian context work)

# Good: writer gets the scene brief, relevant style files, and prior chapter for continuity
meridian spawn -a writer -p "Draft the Route 1 encounter scene" \
  -f $WORK/outline/route1-brief.md \
  -f $KB/styles/[relevant style files] \
  -f $KB/styles/[relevant scene-type files] \
  -f story/chapter4/4chapter.md

# Bad: dumping every chapter and style file "just in case"
meridian spawn -a writer -p "Draft the Route 1 encounter" \
  -f story/**/*.md -f $KB/styles/*.md
```

**`--from` — conversation history.** Use when the agent needs to understand decisions, reasoning, or brainstorm context that hasn't been written down yet. Session history captures the *why* behind choices — why the author picked this meeting angle, what tone they want, what they explicitly rejected.

```bash
# Good: critic needs to understand the author's intent for this scene
meridian spawn -a critic --from p203 -p "Review for voice consistency" \
  -f $WORK/drafts/route1-v1.md

# Bad: passing --from when the direction is already captured in an outline
```

**Materialize first — when context is too important to be ephemeral.** If critical story decisions only live in conversation, write them to the kb or work directory *before* spawning. Story direction decisions are especially important to materialize — if the author chose "comedic misunderstanding" over "shared threat" for a meeting scene, that reasoning needs to survive compaction. The writer who drafts the scene weeks later needs to know not just what was chosen, but what was rejected.

**Rule of thumb**: if a writer could accidentally contradict this context, materialize it. If it's supplementary background that enriches but isn't load-bearing, `--from` is fine.

## What Each Agent Needs

### Writers

Writers need enough to stay in voice and on-canon, not everything ever written. The essential context:

- **Scene brief or outline** — what happens in this scene, the beats to hit
- **Relevant style files** — look at what exists in the styles directory and pick the files that match the scene. Character files for whoever appears, scene-type files for the kind of scene being written. Each style file is self-describing — read the top to know when it applies.
- **Continuity anchors** — the immediately preceding chapter or scene (for flow), plus any chapters that establish facts this scene references. Two to four files, not the entire manuscript.
- **Character state** — character files for characters who appear in the scene, especially if their emotional state or knowledge has changed recently

Tell the writer where to find more if it needs to explore — "the full arc outline is in the work directory, focus on the Route 1 section" — rather than attaching everything preemptively.

### Critics

Critics need the draft plus enough context to judge it against:

- **The draft being reviewed** — always via `-f`
- **The scene brief or outline** — so the critic can check whether the draft achieved what it was supposed to
- **Relevant style files** — so voice critics can compare against the target voice
- **Prior chapters for continuity** — so continuity critics can cross-reference facts
- **Author intent** — via `--from` if the orchestrator discussed direction with the author, or via materialized decision notes
- **Known issues** — tracked issues if the critic should watch for specific recurring problems

### Brainstormers

Brainstormers need constraints, not answers:

- **The question being explored** — scoped tightly in the prompt
- **Established context that constrains the answer** — character profiles, timeline, prior decisions that limit the design space
- **What's been rejected** — so they don't re-propose dead ends

Don't pass too much — brainstormers that receive the full project history tend to produce conservative ideas that fit neatly into existing patterns instead of exploring fresh territory.

### Knowledge Maintenance Agents

- **Session-miner**: `--from` pointing at the conversation to mine, plus kb paths for where to write findings
- **Chronicler**: the chapter(s) to extract facts from via `-f`, plus existing canon files and timeline entries for deduplication
- **Graph-maintainer**: the kb directory structure — it needs to see everything to rebuild connections

## Cross-Phase Context

Use `--from <prior-spawn-id>` to carry forward what a previous phase learned. The revision writer benefits from seeing what the first-draft writer discovered — where the outline was ambiguous, what choices were made to fill gaps. The critic benefits from seeing prior critique rounds — what was already flagged and addressed.

Combine mechanisms when phases produce artifacts: pass the prior spawn's report via `--from` for reasoning context, and the files it created via `-f` for concrete outputs.

```bash
WORK=$(meridian context work)

# Revision writer gets the critique synthesis AND the original draft
meridian spawn -a writer \
  --from p301 \
  -f $WORK/drafts/route1-v1.md \
  -f $WORK/critique-reports/round1-synthesis.md \
  -p "Revise the Route 1 scene, addressing the pacing and voice findings"
```

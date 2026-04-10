---
name: writing-staffing
description: Team composition for writing workflows — which agents to spawn, how many, what focus areas to assign, and how to scale effort. Use when composing critic panels, dispatching researchers, staffing draft/revise loops, or setting up brainstorm fan-outs.
---

# Writing Staffing

Compose the right team for each writing task. The goal is coverage across perspectives — critics with different focus areas, researchers with different scopes, brainstormers on different models — not redundant passes from the same angle.

## Model Selection

Profile defaults are correct for most roles — don't override with `-m` unless you have a specific reason. The primary uses of `-m` are:

- **Brainstorm fan-out**: spawning brainstormers across different model families for creative diversity. Different models bring genuinely different sensibilities — one leans literary, another pragmatic, another wild. That's the point.
- **Critic fan-out**: spawning critics across different models so their blind spots don't overlap. A prose quality issue that one model habitually misses, another catches.

Run `meridian models list` to see available families and strengths.

## General Principles

**Delegation is mandatory for orchestrators.** An orchestrator's value is coordination and judgment, not solo execution. Orchestrators never write prose, draft outlines, or edit wiki pages directly — not even for small fixes. Writing your own drafts bypasses the critique and revision lanes that catch what the writer can't see in their own work. If no team composition was provided by your caller, compose one yourself before starting — use the catalogs in the resources below.

**Review convergence.** Critic loops run until convergence (no new substantive findings), not a fixed number of passes. The orchestrator can stop early, but must log the reasoning in the decision log so future agents understand what was decided and why.

**Brainstorm diversity over brainstorm volume.** Three brainstormers on different models exploring different angles beats five on the same model. Creative diversity comes from different perspectives, not more of the same perspective.

**Style creation vs style evaluation are separate roles.** The style-creator produces style reference files from sample chapters or author requirements. It does not evaluate prose against those styles. Style evaluation — checking whether a draft maintains the project's voice, detecting voice drift, flagging register breaks — is the critic agent with a voice focus. If you need new style files, spawn the style-creator. If you need to check whether a draft matches the style, spawn a critic with voice focus.

## Effort Scaling

Effort scaling applies mainly to critics — the role that fans out within a draft/revise cycle. Writers don't scale within a phase (one writer per scene/chapter; split the brief if it's too big).

For critics, scale to the stakes and complexity of the content:
- Low-stakes drafts (brainstorm captures, wiki stubs): 1-2 critics on default model
- Standard chapters: 3 critics with split focus areas, consider a specialist model for voice or continuity
- Pivotal scenes (character deaths, reveals, arc climaxes): 4-5 critics; for critical focus areas like voice consistency and continuity, duplicate coverage across models

## Parallelism

Think about what depends on what:

- Critics need a finished draft — they wait for the writer
- Critics examine different dimensions — fan them all out simultaneously
- Within a brainstorm fan-out, all brainstormers are independent — fan them out
- Knowledge maintenance agents (chronicler, session-miner, graph-maintainer) are mostly independent — fan them out after the triggering event
- Character-sim agents in a multi-character scene are independent — fan them out, then synthesize

## Agent Catalogs

See resources for detailed catalogs of available agents and when to use each:

- Read `resources/critics.md` when composing critique panels — covers critic focus areas and the continuity-checker specialist.
- Read `resources/researchers.md` when dispatching research — covers research focus areas and when web search is warranted.
- Read `resources/builders.md` when staffing writing, outlining, or wiki work — covers writer, outliner, and wiki-editor.
- Read `resources/knowledge.md` when triggering knowledge maintenance — covers session-miner, chronicler, and graph-maintainer.
- Read `resources/character-sim.md` when setting up character exploration — covers character-sim dispatch and multi-character fan-out patterns. Read it alongside `resources/reader-sim.md` when a workflow also needs experiential reader-response data on a draft.

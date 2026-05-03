---
name: writing-staffing
description: Team composition for writing workflows — which agents to spawn, how many, what focus areas to assign, and how to scale effort. Use when composing critic panels, dispatching researchers, staffing draft/revise loops, or setting up brainstorm fan-outs.
model-invocable: false
---

# Writing Staffing

Compose the right team for each writing task. The goal is coverage across perspectives — critics with different focus areas, researchers with different scopes, brainstormers exploring different angles — not redundant passes from the same angle.

## General Principles

**Delegation keeps context clean.** Each mode of work benefits from a fresh context window and different model strengths — drafting needs voice fidelity, critique needs adversarial distance, research needs breadth. Orchestrators coordinate mode-switches through agents. If no team composition was provided by your caller, compose one yourself before starting — use the catalogs in the resources below.

**Review convergence.** Critic loops run until convergence (no new substantive findings), not a fixed number of passes. The orchestrator can stop early, but must log the reasoning in the decision log so future agents understand what was decided and why.

**Brainstorm diversity over brainstorm volume.** Three brainstormers exploring different angles beats five exploring the same angle. Creative diversity comes from different perspectives, not more of the same perspective.

**Style creation and style evaluation are separate modes.** Creating style reference files from sample prose is an analytical task. Evaluating whether a draft maintains the project's voice is a critique task with voice focus. Use the right mode for each — see the agent catalogs in resources.

## Effort Scaling

Effort scaling applies mainly to critics — the role that fans out within a draft/revise cycle. Writers don't scale within a phase (one writer per scene/chapter; split the brief if it's too big).

For critics, scale to the stakes and complexity of the content:
- Low-stakes drafts (brainstorm captures, wiki stubs): 1-2 critics
- Standard chapters: 3 critics with split focus areas
- Pivotal scenes (character deaths, reveals, arc climaxes): 4-5 critics; for critical focus areas like voice consistency and continuity, duplicate coverage

## Parallelism

Think about what depends on what:

- Critics need a finished draft — they wait for the writer
- Critics examine different dimensions — fan them all out simultaneously
- Within a brainstorm fan-out, all brainstormers are independent — fan them out
- Knowledge maintenance has ordering constraints — see `resources/knowledge.md`
- Character simulations in a multi-character scene are independent — fan them out, then synthesize

## Agent Catalogs

See resources for detailed catalogs of available agents and when to use each:

- Read `resources/critique-synthesis.md` when synthesizing findings from multiple critics — covers reward-channel triage.
- Read `resources/critics.md` when composing critique panels — covers critic focus areas and the continuity-checker specialist.
- Read `resources/researchers.md` when dispatching research — covers research focus areas and base agent usage.
- Read `resources/builders.md` when staffing writing, outlining, or style work — covers writer, outliner, style-creator, and base agents for wiki/reference pages.
- Read `resources/knowledge.md` when triggering knowledge maintenance — covers chronicler and base agent dispatch order.
- Read `resources/character-sim.md` when setting up character exploration — covers character-sim dispatch and multi-character fan-out patterns. Read it alongside `resources/reader-sim.md` when a workflow also needs experiential reader-response data on a draft.

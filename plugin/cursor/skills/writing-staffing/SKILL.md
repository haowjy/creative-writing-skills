---
name: writing-staffing
description: |
  Load before you hand story work to another agent: which agent takes which lane, which skills to tell it to load, which files to pass, how many lanes to run, and which model to run them on.
metadata:
  type: reference
alwaysApply: false
---

# Writing Staffing

Each agent loads its core skills itself. Your brief adds the rest: the lane,
the extra skills to tell it to load ("load `/creative-writing-skills:character-sim`"), the files to
pass, the reader effect to create, and what to leave ambiguous or unresolved.
The files each kind of work needs are in `/creative-writing-skills:story-memory`
`resources/story-context.md` § What Each Agent Needs.

## Model Selection

Agent defaults are usually correct. When overriding or selecting models for
additional lanes, match the model to the work: creative taste and high-stakes
critique need judgment; outlining and cross-document checks need structured
synthesis; bulk gathering and mechanical checks can use a cheaper model when
later synthesis will catch misses.

For model-diverse fan-out, choose two available model families with different
blind spots. Check the live model catalog and model-specific prompting guidance
at dispatch time rather than assuming which models or routes are available.

**Fan-out** passes the same question and files to different model families for
independent judgment. Reserve it for high-stakes calls where model diversity
can reveal different blind spots. **Parallel lanes** use different prompts or
focus areas; use each agent's default model unless a lane needs a capability it
lacks.

## Agent Catalogs

- `resources/producers.md`: `@writer`, `@brainstormer`, `@outliner`,
  `@style-creator`, `@character-sim`, `@web-researcher`, and `@kb-lead`. Open
  it before you spawn an agent that writes or gathers.
- `resources/reviewers.md`: `@critic` lanes (a focus area or an edit level),
  `@continuity-checker`, `@reader-sim`, and how many lanes a chapter needs.
  Open it before staffing any critique.

---
name: writing-staffing
description: |
  Load before you hand story work to another agent: which agent takes which lane, which skills to tell it to load, which files to pass, how many lanes to run, and which model to run them on.
metadata:
  type: reference
---

# Writing Staffing

Each agent loads its core skills itself. Your brief adds the rest: the lane,
the extra skills to tell it to load ("load `/creative-writing-skills:character-sim`"), the files to
pass, the reader effect to create, and what to leave ambiguous or unresolved.
The files each kind of work needs are in `/creative-writing-skills:story-memory`
`resources/story-context.md` § What Each Agent Needs.

## Model Selection

Run every lane on its agent's default model. Lanes that look at different
angles, focus areas or characters are **parallel lanes**, and the different
prompts are what make them independent. Change a lane's model only when it
needs a capability its default lacks.

**Fan-out** is the exception: the same question and files sent to two model
families, for a high-stakes or disputed call where their different blind spots
are the point. A family is a provider: Opus, Sonnet and Fable are one family, so
two Anthropic models add no diversity. Your harness's own agent tool usually
reaches only its own provider, so fan out with `meridian spawn -m <model>`, and
check the live catalog (`meridian mars models list`) and its prompting guidance
(`meridian mars models prompting`) at dispatch time.

## Agent Catalogs

- `resources/producers.md`: `@writer`, `@brainstormer`, `@outliner`,
  `@style-creator`, `@character-sim`, `@creative-researcher`, and `@kb-lead`. Open
  it before you spawn an agent that writes or gathers.
- `resources/reviewers.md`: `@critic` lanes (a focus area or an edit level),
  `@continuity-checker`, `@reader-sim`, and how many lanes a chapter needs.
  Open it before staffing any critique.

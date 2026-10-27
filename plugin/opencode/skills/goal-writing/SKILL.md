---
name: goal-writing
description: |
  Load when turning intent into an executable goal for an agent, delegated run, work item, experiment, or handoff. Use to define outcome, evidence, constraints, anti-goals, stop conditions, and reporting shape before work begins.
metadata:
  type: reference
---

# Goal Writing

Use this skill when a task needs a goal that another agent or future session can
execute without reinterpreting intent.

A goal is the control surface for agent work. It says what should become true,
what evidence proves it, and what the agent must not do while pursuing it. A loop
is one way to execute a goal; the goal is the primitive.

## What a Good Goal Needs

Write goals with the parts that change behavior:

1. **Outcome.** What should be observably true when the work succeeds?
2. **Why.** What decision, user need, or research question does this unblock?
3. **Ground truth.** What files, artifacts, prior decisions, baselines, or current
   state should the agent treat as authoritative?
4. **Scope.** What is in scope, out of scope, and not to be changed?
5. **Priority.** If goals conflict, which outcome wins and which tradeoff is
   acceptable?
6. **Constraints.** Cost, time, risk, compatibility, safety, compute, style, or
   process limits.
7. **Evidence.** What command, metric, artifact, review, citation, run, or
   observation proves the outcome?
8. **Anti-goals.** What would be a bad way to achieve the metric or an invalid
   shortcut?
9. **Stop / ask conditions.** When should the agent stop, ask, defer, or declare
   the goal blocked?
10. **Report shape.** What should come back: changes, findings, decision,
   validation evidence, open risks, or next step?

Fill only the slots whose information would change what the agent does.

## Optimization Goals

Optimization goals need extra guardrails because agents can satisfy a narrow
metric while damaging the real objective.

For any goal shaped like "improve X," specify:

- the metric or observable target,
- the baseline being compared against,
- the allowed search space,
- the invariants that must not regress,
- the data, benchmark, evaluator, or review gate that cannot be changed,
- what counts as cheating, leakage, overfitting, cherry-picking, or metric gaming,
- how many attempts, how much budget, or what escalation threshold applies,
- what evidence must be reported for all meaningful attempts, not only the best
  attempt.

If the strategy is unknown, write a learning goal first: identify mechanisms,
baselines, constraints, or promising directions. Set a performance goal once
the agent has a credible path to improve it.

## Quality Checks

Before handing off a goal, check:

- **Specific:** Could two agents read it and aim at the same outcome?
- **Observable:** Can success be verified without trusting the agent's opinion?
- **Bounded:** Does it prevent adjacent work from expanding silently?
- **Grounded:** Does it name the artifacts, baseline, or state needed to begin?
- **Honest:** Does it define invalid shortcuts and ways the result could be fake?
- **Calibrated:** Is this a performance goal when the path is known, or a
  learning goal when the path is uncertain?
- **Actionable:** Does the agent have a plausible next action?
- **Reportable:** Will the final answer include enough evidence to decide what
  to do next?

If a goal fails these checks, rewrite it before handing off or starting the work.

## When the Goal Drives a Loop

Some goals require repeated attempts. Add loop mechanics only when feedback from
one attempt should change the next attempt.

For loop-driven goals, specify:

- what changes between attempts,
- what signal is observed after each attempt,
- how the signal is compared to the target or baseline,
- what memory or log is updated,
- when to continue, branch, stop, or ask,
- who reviews the loop when cheating or metric gaming is possible.

A loop without a clear goal is drift. A goal without feedback is wishful
thinking. Keep the goal primary and the loop accountable to it.

## Reviewer Gates

Use an independent reviewer when the goal creates incentives to cheat, hide
failures, overfit, or reinterpret success after the fact.

Ask the reviewer to check:

- whether the metric matches the real objective,
- whether the baseline and data were preserved,
- whether failures and non-best attempts were reported,
- whether constraints were violated,
- whether the claimed success follows from the evidence,
- what would change their mind.

For research and benchmark work, prefer reviewer gates before promotion, not
after the result has already been written as a win.

## Handoff Template

```markdown
Goal: <observable outcome>

Why: <decision, user need, or research question this unblocks>

Ground truth:
- <files, artifacts, baselines, prior decisions, current state>

Scope:
- In: <owned work>
- Out: <explicit exclusions>

Priority / tradeoffs:
- <what wins when objectives conflict>

Constraints:
- <limits, invariants, cost/risk boundaries>

Anti-goals / invalid shortcuts:
- <ways not to win>

Evidence of success:
- <commands, metrics, artifacts, citations, review gates, or observations>

Stop / ask if:
- <ambiguity, risk, budget, blocker, or cheating concern>

Report back with:
- <summary shape and evidence>
```

Keep the template terse. Delete sections that do not change the agent's behavior.
